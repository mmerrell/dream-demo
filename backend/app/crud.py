from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException
import models, schemas, security

# --- Product CRUD ---

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_product_by_name(db: Session, name: str):
    return db.query(models.Product).filter(models.Product.name == name).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# --- User CRUD ---

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Order CRUD ---

class InsufficientInventoryError(Exception):
    def __init__(self, product_name: str, available: int, requested: int):
        self.product_name = product_name
        self.available = available
        self.requested = requested
        super().__init__(f"Not enough inventory for {product_name}: need {requested}, have {available}")

class InventoryAllocationFailedError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class ProductNotFoundError(Exception):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Product with id {product_id} not found")

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def create_order_db(db: Session, order: schemas.OrderCreate, user_id: int) -> models.Order:
    db_order = models.Order(owner_id=user_id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in order.items:
        product = get_product(db, item.product_id)
        if not product:
            raise ProductNotFoundError(item.product_id)
        if product.inventory_count < item.quantity:
            raise InsufficientInventoryError(str(product.name), int(product.inventory_count), int(item.quantity))

        db_order_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=product.price
        )
        db.add(db_order_item)
        
        # Decrement inventory
        product.inventory_count -= item.quantity

    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders_by_user(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.owner_id == user_id).all()

def update_order_status(db: Session, order_id: int, status: str):
    db_order = get_order(db, order_id)
    if db_order:
        db_order.status = status
        db.commit()
        db.refresh(db_order)
    return db_order

# Inventory Management Functions
def check_inventory(db: Session, order_id: int) -> bool:
    """
    Check if there's sufficient inventory for all items in an order.
    Returns True if all items are available, False otherwise.
    """
    order = get_order(db, order_id)
    if not order:
        return False

    for item in order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product or product.inventory_count < item.quantity:
            return False

    return True

def allocate_inventory(db: Session, order_id: int) -> bool:
    """
    Reduce inventory counts for all items in an order.
    Returns True if successful, False if inventory insufficient.
    """
    order = get_order(db, order_id)
    if not order:
        return False

    # Check inventory first
    if not check_inventory(db, order_id):
        return False

    # Allocate (reduce) inventory
    for item in order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.inventory_count -= item.quantity

    db.commit()
    return True


def release_inventory(db: Session, order_id: int) -> bool:
    """
    Return inventory to stock if order is cancelled.
    """
    order = get_order(db, order_id)
    if not order:
        return False

    for item in order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.inventory_count += item.quantity

    db.commit()
    return True


# Mock notification functions (would integrate with email service in production)

def notify_fulfillment(order_id: int) -> dict:
    """
    Mock function to notify fulfillment team.
    In production, this would integrate with a fulfillment system or send emails.
    """
    print(f"[FULFILLMENT] Order #{order_id} ready for fulfillment")
    return {
        "status": "notified",
        "order_id": order_id,
        "timestamp": datetime.now().isoformat()
    }
