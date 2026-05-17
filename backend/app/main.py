from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import timedelta
from jose import jwt, JWTError

from fastapi.middleware.cors import CORSMiddleware

from app import crud, models, schemas, security, config
from app.database import engine, get_db
import stripe
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from fastapi import Body
from app.saucelabs_authoring_schemas import GenerateRequest, RunRequest, ScheduleRequest

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dream Demo API",
    description="API for the online flower shop.",
    version="0.1.0"
)

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

@app.middleware("http")
async def log_requests_middleware(request, call_next):
    # Log incoming requests for debug (writes to stdout/backend log)
    try:
        body = await request.body()
        if body:
            print(f"[INCOMING REQUEST] {request.method} {request.url.path} BODY: {body.decode('utf-8', errors='ignore')}")
        else:
            print(f"[INCOMING REQUEST] {request.method} {request.url.path} BODY: <empty>")
    except Exception as e:
        print(f"[INCOMING REQUEST] failed to read body: {e}")
    response = await call_next(request)
    response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    return response

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

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

stripe.api_key = config.STRIPE_SECRET_KEY

@app.post("/create-payment-intent")
def create_payment(request: schemas.PaymentIntentCreateRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    order = crud.get_order(db, order_id=request.order_id)
    if not order or order.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")

    total_amount = sum(item.price_at_purchase * item.quantity for item in order.items)
    total_amount_in_cents = int(total_amount * 100)

    try:
        intent = stripe.PaymentIntent.create(
            amount=total_amount_in_cents,
            currency='usd',
            automatic_payment_methods={"enabled": True},
            metadata={"order_id": str(request.order_id)}
        )
        return {"client_secret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_order(db=db, order=order, user_id=current_user.id)

@app.post("/orders/{order_id}/update-status", response_model=schemas.Order)
def update_order_status(order_id: int, status_update: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    order = crud.get_order(db, order_id)
    if not order or order.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.update_order_status(db=db, order_id=order_id, status=status_update.get('status'))

@app.get("/orders/", response_model=List[schemas.Order])
def read_orders(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_orders_by_user(db=db, user_id=current_user.id)

@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)

@app.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@app.get("/")
def read_root():
    return {"message": "Welcome to the Dream Demo Flower Shop API!"}

_retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429,500,502,503,504], allowed_methods=["GET","POST","PUT","DELETE","HEAD","OPTIONS"])
_session = requests.Session()
_adapter = HTTPAdapter(max_retries=_retries)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)

def _to_payload(req_obj):
    if req_obj is None:
        return {}
    if hasattr(req_obj, "model_dump"):
        return req_obj.model_dump()
    if hasattr(req_obj, "dict"):
        return req_obj.dict()
    return dict(req_obj)

def _sauce_request(method: str, path: str, **kwargs):
    if path.startswith("http"):
        url = path
    else:
        url = f"{config.SAUCE_API_HOST}{path}"
    try:
        resp = _session.request(method, url, auth=(config.SAUCE_USERNAME, config.SAUCE_ACCESS_KEY), timeout=15, **kwargs)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Error contacting Sauce Labs API")
    if resp.status_code >= 400:
        detail = resp.text
        truncated = detail if len(detail) <= 800 else detail[:800]
        raise HTTPException(status_code=resp.status_code, detail=f"Sauce API error: {truncated}")
    try:
        return resp.json()
    except ValueError:
        return {"text": resp.text}

@app.post("/sauce/ai/testcases/generate")
def generate_testcase(req: GenerateRequest = Body(...)):
    payload = _to_payload(req)
    return _sauce_request('post', '/v1/ai-authoring/testcases/generate', json=payload)

@app.get("/sauce/ai/testcases")
def list_testcases(search: Optional[str] = None, skip: int = 0, limit: int = 20):
    params: Dict[str, Any] = {"skip": skip, "limit": limit}
    if search:
        params["search"] = search
    return _sauce_request('get', '/v1/ai-authoring/testcases', params=params)

@app.post("/sauce/ai/testcases/{testcase_id}/run")
def run_testcase(testcase_id: str, req: Optional[RunRequest] = Body(None)):
    payload = _to_payload(req)
    return _sauce_request('post', f'/v1/ai-authoring/testcases/{testcase_id}/run', json=payload)

@app.post("/sauce/ai/testsuites/{suite_id}/run")
def run_testsuite(suite_id: str, buildName: Optional[str] = Body(None)):
    payload = {"buildName": buildName} if buildName else {}
    return _sauce_request('post', f'/v1/ai-authoring/testsuites/{suite_id}/run', json=payload)

@app.post("/sauce/ai/testsuites")
def create_testsuite(req: ScheduleRequest = Body(...)):
    payload = _to_payload(req)
    return _sauce_request('post', '/v1/ai-authoring/testsuites', json=payload)

def process_payment(db: Session, order_id: int) -> dict:
    import time

    order = crud.get_order(db, order_id)
    if not order:
        return {"status": "error", "message": "Order not found"}

    order = crud.update_order_status(db, order_id, "paid")
    print(f"[PAYMENT] Order #{order_id} payment confirmed - awaiting fulfillment")

    time.sleep(2)

    if not crud.check_inventory(db, order_id):
        crud.update_order_status(db, order_id, "payment_failed")
        return {
            "status": "error",
            "message": "Insufficient inventory",
            "order_id": order_id
        }

    if not crud.allocate_inventory(db, order_id):
        crud.update_order_status(db, order_id, "payment_failed")
        return {
            "status": "error",
            "message": "Failed to allocate inventory",
            "order_id": order_id
        }

    crud.update_order_status(db, order_id, "processing")
    print(f"[WAREHOUSE] Order #{order_id} picked and being packed")

    time.sleep(5)

    fulfillment_result = crud.notify_fulfillment(order_id)
    print(f"[SHIPPING] Order #{order_id} shipped")

    time.sleep(3)

    confirmation_result = crud.send_confirmation(order_id, order.owner.email)

    crud.update_order_status(db, order_id, "completed")
    print(f"[DELIVERY] Order #{order_id} delivered successfully")

    return {
        "status": "success",
        "order_id": order_id,
        "fulfillment": fulfillment_result,
        "confirmation": confirmation_result
    }



@app.get("/sauce/ai/testcases")
def list_testcases(search: Optional[str] = None, skip: int = 0, limit: int = 20):
    """Proxy GET to list test cases."""
    url = f"{config.SAUCE_API_HOST}/v1/ai-authoring/testcases"
    params = {"search": search, "skip": skip, "limit": limit}
    resp = requests.get(url, auth=(config.SAUCE_USERNAME, config.SAUCE_ACCESS_KEY), params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


@app.post("/sauce/ai/testcases/{testcase_id}/run")
def run_testcase(testcase_id: str, req: Optional[RunRequest] = Body(None)):
    """Trigger a run of an existing Sauce AI-authored test case."""
    url = f"{config.SAUCE_API_HOST}/v1/ai-authoring/testcases/{testcase_id}/run"
    payload = req.model_dump() if req else {}
    resp = requests.post(url, auth=(config.SAUCE_USERNAME, config.SAUCE_ACCESS_KEY), json=payload)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


@app.post("/sauce/ai/testsuites/{suite_id}/run")
def run_testsuite(suite_id: str, buildName: Optional[str] = Body(None)):
    url = f"{config.SAUCE_API_HOST}/v1/ai-authoring/testsuites/{suite_id}/run"
    payload = {"buildName": buildName} if buildName else {}
    resp = requests.post(url, auth=(config.SAUCE_USERNAME, config.SAUCE_ACCESS_KEY), json=payload)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


@app.post("/sauce/ai/testsuites")
def create_testsuite(req: ScheduleRequest = Body(...)):
    url = f"{config.SAUCE_API_HOST}/v1/ai-authoring/testsuites"
    payload = req.model_dump()
    resp = requests.post(url, auth=(config.SAUCE_USERNAME, config.SAUCE_ACCESS_KEY), json=payload)
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

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