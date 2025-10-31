from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from jose import jwt, JWTError

from fastapi.middleware.cors import CORSMiddleware

import crud, models, schemas, security, config
import stripe
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dream Demo API",
    description="API for the online flower shop.",
    version="0.1.0"
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
        )
        return {"client_secret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Order Endpoints ---

@app.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_order(db=db, order=order, user_id=current_user.id)

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
