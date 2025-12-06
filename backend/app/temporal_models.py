from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from enum import Enum

class OrderStatus(str, Enum):
    INITIALIZING = "initializing"
    CREATED = "created"
    INVENTORY_RESERVED = "inventory_reserved"
    PAYMENT_PROCESSING = "payment_processing"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PACKAGING = "packaging"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class TemporalOrderItem:
    product_id: int
    quantity: int
    price: float

@dataclass
class OrderFulfillmentInput:
    user_id: int
    items: List[TemporalOrderItem]
    shipping_address: Optional[dict] = None
    payment_method_id: Optional[str] = None
    total_amount: Optional[float] = None

@dataclass
class OrderFulfillmentResult:
    order_id: str
    final_status: OrderStatus
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[str] = None
    failure_reason: Optional[str] = None
    created_at: Optional[datetime] = None

