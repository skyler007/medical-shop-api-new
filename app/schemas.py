from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class PackagingTypeEnum(str, Enum):
    STRIP = "strip"
    BOTTLE = "bottle"
    BOX = "box"
    LOOSE = "loose"
    TUBE = "tube"
    VIAL = "vial"


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentMethodEnum(str, Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    ONLINE = "online"


# ================= MEDICINE =================

class MedicineBase(BaseModel):
    name: str
    name_hindi: Optional[str] = None
    generic_name: Optional[str] = None
    company: Optional[str] = None
    composition: Optional[str] = None
    price_per_unit: float
    mrp: float
    stock_quantity: int = 0
    reorder_level: int = 10
    default_packaging: str = "strip"
    units_per_package: Optional[int] = None
    category: Optional[str] = None
    prescription_required: bool = False
    batch_number: Optional[str] = None
    rack_location: Optional[str] = None


class MedicineCreate(MedicineBase):
    pass


class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    name_hindi: Optional[str] = None
    price_per_unit: Optional[float] = None
    mrp: Optional[float] = None
    stock_quantity: Optional[int] = None
    reorder_level: Optional[int] = None
    default_packaging: Optional[str] = None
    units_per_package: Optional[int] = None
    batch_number: Optional[str] = None
    rack_location: Optional[str] = None
    category: Optional[str] = None
    expiry_date: Optional[datetime] = None


class MedicineResponse(MedicineBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ================= CUSTOMER =================

class CustomerBase(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    is_regular: bool = False
    customer_id: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int
    total_orders: int = 0
    total_amount_spent: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True


# ================= ORDER ITEMS =================

class OrderItemBase(BaseModel):
    medicine_id: int
    quantity: int
    packaging_type: str = "strip"


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: int
    price_per_unit: float
    total_price: float
    medicine: Optional[MedicineResponse] = None

    class Config:
        from_attributes = True


# ================= INVOICE =================

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    order_id: int
    subtotal: float
    discount: float
    tax_rate: float
    tax_amount: float
    total_amount: float
    payment_method: Optional[str]
    payment_status: str
    pdf_path: Optional[str]
    sent_via_whatsapp: bool
    sent_via_email: bool
    sent_via_sms: bool
    invoice_date: datetime

    class Config:
        from_attributes = True


# ================= ORDER =================

class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_address: Optional[str] = None
    items: List[OrderItemCreate]
    notes: Optional[str] = None
    order_source: str = "phone"
    language_used: Optional[str] = "hindi"

    @validator('items')
    def validate_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Order must have at least one item')
        return v


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer: CustomerResponse
    status: str
    total_amount: float
    discount_amount: float
    tax_amount: float
    final_amount: float
    order_source: str
    language_used: Optional[str]
    notes: Optional[str]
    order_date: datetime
    order_items: List[OrderItemResponse]
    invoice: Optional[InvoiceResponse] = None   # ✅ ADDED (only change)

    class Config:
        from_attributes = True


# ================= AI AGENT =================

class AIAgentOrderRequest(BaseModel):
    customer_name: str
    customer_phone: str
    customer_address: Optional[str] = None
    medicines: List[dict]
    language: str = "hindi"
    conversation_transcript: Optional[str] = None


class AIAgentOrderResponse(BaseModel):
    success: bool
    message: str
    order_id: Optional[int] = None
    order_number: Optional[str] = None
    invoice_number: Optional[str] = None
    total_amount: Optional[float] = None
    invoice_pdf_url: Optional[str] = None


# ================= SEARCH =================

class MedicineSearchRequest(BaseModel):
    query: str
    limit: int = 10


class MedicineSearchResponse(BaseModel):
    medicines: List[MedicineResponse]
    total: int


# ================= AUTH =================

class UserRegister(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    password: str
    role: Optional[str] = "customer"


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    is_active: bool
    role: str = "customer"
    created_at: datetime

    class Config:
        from_attributes = True


class UserAdminResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    is_active: bool
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserStatusUpdate(BaseModel):
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class ChangePassword(BaseModel):
    current_password: str
    new_password: str


# ================= DRAFT =================

class DraftOrderItem(BaseModel):
    medicine_id: int
    medicine_name: str
    packaging_type: str = "strip"
    quantity: int
    price_per_unit: float
    total_price: float


class DraftOrder(BaseModel):
    items: List[DraftOrderItem]
    estimate_total: float
    notes: Optional[str] = None
