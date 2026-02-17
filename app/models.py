from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class PackagingType(str, enum.Enum):
    STRIP = "strip"  # पट्टी
    BOTTLE = "bottle"  # बोतल
    BOX = "box"  # डिब्बा
    LOOSE = "loose"  # खुली
    TUBE = "tube"  # ट्यूब
    VIAL = "vial"  # शीशी

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Medicine(Base):
    __tablename__ = "medicines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    name_hindi = Column(String(200), nullable=True)  # हिंदी नाम
    generic_name = Column(String(200), nullable=True)
    company = Column(String(200), nullable=True)
    composition = Column(Text, nullable=True)
    
    # Pricing
    price_per_unit = Column(Float, nullable=False)
    mrp = Column(Float, nullable=False)
    
    # Stock
    stock_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    
    # Packaging
    default_packaging = Column(String(50), default="strip")
    units_per_package = Column(Integer, default=10)  # e.g., 10 tablets per strip
    
    # Categories
    category = Column(String(100), nullable=True)  # e.g., Antibiotic, Painkiller
    prescription_required = Column(Boolean, default=False)
    
    # Metadata
    batch_number = Column(String(100), nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    rack_location = Column(String(50), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="medicine")

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    # Customer type
    is_regular = Column(Boolean, default=False)
    customer_id = Column(String(50), nullable=True, unique=True)  # For regular customers
    
    # Metadata
    total_orders = Column(Integer, default=0)
    total_amount_spent = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Customer
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Order details
    status = Column(String(20), default="pending")
    total_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    final_amount = Column(Float, default=0.0)
    
    # Source
    order_source = Column(String(50), default="phone")  # phone, walk-in, online, ai-agent
    language_used = Column(String(20), nullable=True)  # hindi, english, hinglish
    
    # Notes
    notes = Column(Text, nullable=True)
    prescription_image = Column(String(500), nullable=True)
    
    # Timestamps
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    invoice = relationship("Invoice", back_populates="order", uselist=False)

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    
    # Item details
    quantity = Column(Integer, nullable=False)
    packaging_type = Column(String(50), default="strip")
    price_per_unit = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    medicine = relationship("Medicine", back_populates="order_items")

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    
    # Invoice details
    subtotal = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.0)  # GST percentage
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # Payment
    payment_method = Column(String(50), nullable=True)  # cash, card, upi, online
    payment_status = Column(String(20), default="unpaid")  # paid, unpaid, partial
    
    # PDF
    pdf_path = Column(String(500), nullable=True)
    
    # Delivery
    sent_via_whatsapp = Column(Boolean, default=False)
    sent_via_email = Column(Boolean, default=False)
    sent_via_sms = Column(Boolean, default=False)
    
    # Timestamps
    invoice_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="invoice")
