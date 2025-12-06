from pydantic import BaseModel, ConfigDict, EmailStr
from decimal import Decimal
import datetime
from typing import Optional, List

# --- Product Schemas ---

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    inventory_count: int
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


class PaymentIntentCreateRequest(BaseModel):
    order_id: int

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    price_at_purchase: Decimal
    product: Product # Include product details

    model_config = ConfigDict(from_attributes=True)

class OrderBase(BaseModel):
    items: List[OrderItemCreate]

class OrderCreate(OrderBase):
    pass

class Order(BaseModel):
    id: int
    owner_id: int
    created_at: datetime.datetime
    status: str
    items: List[OrderItem] = []

    model_config = ConfigDict(from_attributes=True)

class WorkflowStartResponse(BaseModel):
    message: str
    workflow_id: str
    