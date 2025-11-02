import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta, datetime
from jose import jwt, JWTError
from temporalio.client import Client, WorkflowFailureError
from typing import Optional

from fastapi.middleware.cors import CORSMiddleware
import crud, models, schemas, security, config
import stripe

from workflow import OrderProcessingWorkflow
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)
temporal_client: Optional[Client] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global temporal_client
    from temporalio.contrib.pydantic import pydantic_data_converter

    temporal_client = await Client.connect(
        "temporal:7233",
        data_converter=pydantic_data_converter
    )
    print("Connected to Temporal server")

    yield

app = FastAPI(
    title="Dream Demo API",
    description="API for the online flower shop.",
    version="0.1.0",
    lifespan=lifespan
)

# --- CORS Middleware ---
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In main.py, add to your middleware or responses
@app.middleware("http")
async def add_no_index_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    return response

# --- Authentication Dependencies ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


# --- Authentication Endpoints ---

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- User Endpoints ---

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user


# --- Payment Endpoints ---

stripe.api_key = config.STRIPE_SECRET_KEY

@app.post("/create-payment-intent")
def create_payment(request: schemas.PaymentIntentCreateRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    order = crud.get_order(db, order_id=request.order_id)
    if not order or order.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")

    # Calculate total amount in cents
    total_amount = sum(item.price_at_purchase * item.quantity for item in order.items)
    total_amount_in_cents = int(total_amount * 100)

    try:
        intent = stripe.PaymentIntent.create(
            amount=total_amount_in_cents,
            currency='usd',
            automatic_payment_methods={"enabled": True},
            metadata={"order_id": str(request.order_id)}  # Add this line
        )
        return {"client_secret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Order Endpoints ---


@app.post("/orders/", response_model=schemas.WorkflowStartResponse)
async def create_order_endpoint(
        order: schemas.OrderCreate,
        current_user: models.User = Depends(get_current_user)
):

    order_dict = order.dict()

    workflow_id = f"create-order-{current_user.id}-{int(datetime.now().timestamp())}"
    handle = await temporal_client.start_workflow(
        OrderProcessingWorkflow.create_order_workflow,
        args=[order_dict, current_user.id],
        id=workflow_id,
        task_queue="create-order-tasks",
    )

    return {
        "message": "Order creation started",
        "workflow_id": handle.id
    }

@app.post("/orders/{order_id}/update-status", response_model=schemas.Order)
def update_order_status(order_id: int, status_update: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # In a real app, you'd have more robust checks here
    order = crud.get_order(db, order_id)
    if not order or order.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.update_order_status(db=db, order_id=order_id, status=status_update.get('status'))

@app.get("/orders/", response_model=List[schemas.Order])
def read_orders(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_orders_by_user(db=db, user_id=current_user.id)


# --- Product Endpoints ---

@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)


@app.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products


@app.get("/")
def read_root():
    """A welcome message for the API root."""
    return {"message": "Welcome to the Dream Demo Flower Shop API!"}

@app.post("/orders/{order_id}/process-payment")
def process_order_payment(order_id: int, db: Session = Depends(get_db),
                          current_user: models.User = Depends(get_current_user)):
    """
    Process payment and complete order workflow.
    Called after successful Stripe payment.
    """
    order = crud.get_order(db, order_id)
    if not order or order.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")

    result = process_payment(db, order_id)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhook events for payment processing.
    This is called by Stripe when payment events occur.
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        # In production, verify the webhook signature
        # event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)

        # For demo purposes, just parse the JSON
        import json
        event = json.loads(payload)

        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            # Extract order_id from metadata (we'd need to add this when creating payment intent)
            order_id = payment_intent.get('metadata', {}).get('order_id')

            if order_id:
                # Process the successful payment
                result = process_payment(db, int(order_id))
                return {"status": "success", "result": result}

        return {"status": "ignored"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Cancel a pending order and return inventory to stock.
    """
    order = crud.get_order(db, order_id)
    if not order or order.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != 'pending':
        raise HTTPException(status_code=400, detail="Only pending orders can be cancelled")

    # Return inventory to stock
    crud.release_inventory(db, order_id)

    # Update order status
    order = crud.update_order_status(db, order_id, "cancelled")

    return order


def process_payment(db: Session, order_id: int) -> dict:
    """
    Complete payment processing workflow:
    1. Update order status to 'paid'
    2. Check inventory availability
    3. Allocate inventory
    4. Notify fulfillment
    5. Send confirmation email

    NOTE: This function simulates realistic delays between order states
    that would occur in a production environment.
    """
    import time

    order = crud.get_order(db, order_id)
    if not order:
        return {"status": "error", "message": "Order not found"}

    # Update order status to paid (payment confirmed)
    order = crud.update_order_status(db, order_id, "paid")
    print(f"[PAYMENT] Order #{order_id} payment confirmed - awaiting fulfillment")

    # Simulate payment settlement delay (realistic: 1-2 seconds)
    time.sleep(2)

    # Check inventory
    if not crud.check_inventory(db, order_id):
        crud.update_order_status(db, order_id, "payment_failed")
        return {
            "status": "error",
            "message": "Insufficient inventory",
            "order_id": order_id
        }

    # Allocate inventory
    if not crud.allocate_inventory(db, order_id):
        crud.update_order_status(db, order_id, "payment_failed")
        return {
            "status": "error",
            "message": "Failed to allocate inventory",
            "order_id": order_id
        }

    # Update status to processing (order being prepared/packed)
    crud.update_order_status(db, order_id, "processing")
    print(f"[WAREHOUSE] Order #{order_id} picked and being packed")

    # Simulate warehouse processing time (realistic: 5-10 seconds for demo, hours in reality)
    time.sleep(5)

    # Notify fulfillment team
    fulfillment_result = crud.notify_fulfillment(order_id)
    print(f"[SHIPPING] Order #{order_id} shipped")

    # Simulate shipping/delivery time (realistic: 3 seconds for demo, days in reality)
    time.sleep(3)

    # Send confirmation email
    confirmation_result = crud.send_confirmation(order_id, order.owner.email)

    # Mark as complete (delivered)
    crud.update_order_status(db, order_id, "completed")
    print(f"[DELIVERY] Order #{order_id} delivered successfully")

    return {
        "status": "success",
        "order_id": order_id,
        "fulfillment": fulfillment_result,
        "confirmation": confirmation_result
    }