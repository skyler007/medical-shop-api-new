from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

from app.database import engine, get_db
from app import models, schemas
from app.services.order_service import OrderService

# Create tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="Medical Shop Management API",
    description="AI-powered medical shop order and invoice management system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for invoices
os.makedirs("invoices", exist_ok=True)
app.mount("/invoices", StaticFiles(directory="invoices"), name="invoices")

# ===== HEALTH CHECK =====
@app.get("/")
def root():
    return {
        "message": "Medical Shop API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ===== MEDICINE ROUTES =====
@app.post("/api/medicines", response_model=schemas.MedicineResponse, status_code=status.HTTP_201_CREATED)
def create_medicine(medicine: schemas.MedicineCreate, db: Session = Depends(get_db)):
    """Create a new medicine in inventory"""
    db_medicine = models.Medicine(**medicine.dict())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

@app.get("/api/medicines", response_model=List[schemas.MedicineResponse])
def get_medicines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all medicines"""
    medicines = db.query(models.Medicine).offset(skip).limit(limit).all()
    return medicines

@app.get("/api/medicines/{medicine_id}", response_model=schemas.MedicineResponse)
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    """Get medicine by ID"""
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine

@app.put("/api/medicines/{medicine_id}", response_model=schemas.MedicineResponse)
def update_medicine(medicine_id: int, medicine_update: schemas.MedicineUpdate, db: Session = Depends(get_db)):
    """Update medicine details"""
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    update_data = medicine_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(medicine, key, value)
    
    db.commit()
    db.refresh(medicine)
    return medicine

@app.delete("/api/medicines/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
    """Delete medicine"""
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    db.delete(medicine)
    db.commit()
    return None

@app.post("/api/medicines/search", response_model=schemas.MedicineSearchResponse)
def search_medicines(search_request: schemas.MedicineSearchRequest, db: Session = Depends(get_db)):
    """Search medicines by name (Hindi/English) or generic name"""
    medicines = OrderService.search_medicine(db, search_request.query, search_request.limit)
    return {
        "medicines": medicines,
        "total": len(medicines)
    }

# ===== CUSTOMER ROUTES =====
@app.post("/api/customers", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer"""
    # Check if phone already exists
    existing = db.query(models.Customer).filter(models.Customer.phone == customer.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this phone already exists")
    
    db_customer = models.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.get("/api/customers", response_model=List[schemas.CustomerResponse])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all customers"""
    customers = db.query(models.Customer).offset(skip).limit(limit).all()
    return customers

@app.get("/api/customers/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get customer by ID"""
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.get("/api/customers/phone/{phone}", response_model=schemas.CustomerResponse)
def get_customer_by_phone(phone: str, db: Session = Depends(get_db)):
    """Get customer by phone number"""
    customer = db.query(models.Customer).filter(models.Customer.phone == phone).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# ===== ORDER ROUTES =====
@app.post("/api/orders", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Create a new order manually"""
    try:
        db_order = OrderService.create_order(db, order)
        return db_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")

@app.get("/api/orders", response_model=List[schemas.OrderResponse])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all orders"""
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    return orders

@app.get("/api/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/orders/number/{order_number}", response_model=schemas.OrderResponse)
def get_order_by_number(order_number: str, db: Session = Depends(get_db)):
    """Get order by order number"""
    order = db.query(models.Order).filter(models.Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# ===== AI AGENT ROUTES (Main integration point for voice AI) =====
@app.post("/api/ai-agent/order", response_model=schemas.AIAgentOrderResponse)
def create_order_from_ai_agent(order_request: schemas.AIAgentOrderRequest, db: Session = Depends(get_db)):
    """
    Main endpoint for AI Voice Agent to create orders
    This is what your voice AI service (Vapi/Bland/Twilio) will call
    """
    result = OrderService.create_order_from_ai_agent(db, order_request)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Failed to create order")
        )
    
    return result

# ===== INVOICE ROUTES =====
@app.get("/api/invoices/{invoice_id}", response_model=schemas.InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Get invoice by ID"""
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@app.get("/api/invoices/number/{invoice_number}", response_model=schemas.InvoiceResponse)
def get_invoice_by_number(invoice_number: str, db: Session = Depends(get_db)):
    """Get invoice by invoice number"""
    invoice = db.query(models.Invoice).filter(models.Invoice.invoice_number == invoice_number).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@app.get("/api/invoices/{invoice_id}/download")
def download_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Download invoice PDF"""
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if not invoice.pdf_path or not os.path.exists(invoice.pdf_path):
        raise HTTPException(status_code=404, detail="Invoice PDF not found")
    
    return FileResponse(
        invoice.pdf_path,
        media_type="application/pdf",
        filename=f"{invoice.invoice_number}.pdf"
    )

# ===== DASHBOARD/STATS ROUTES =====
@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    total_orders = db.query(models.Order).count()
    total_customers = db.query(models.Customer).count()
    total_medicines = db.query(models.Medicine).count()
    
    # Low stock medicines
    low_stock = db.query(models.Medicine).filter(
        models.Medicine.stock_quantity <= models.Medicine.reorder_level
    ).count()
    
    # Today's orders
    from datetime import datetime, timedelta
    today = datetime.now().date()
    today_orders = db.query(models.Order).filter(
        models.Order.order_date >= today
    ).count()
    
    # Total revenue
    total_revenue = db.query(models.Invoice).with_entities(
        models.Invoice.total_amount
    ).all()
    revenue_sum = sum([inv[0] for inv in total_revenue if inv[0]])
    
    return {
        "total_orders": total_orders,
        "total_customers": total_customers,
        "total_medicines": total_medicines,
        "low_stock_medicines": low_stock,
        "today_orders": today_orders,
        "total_revenue": revenue_sum
    }

@app.get("/api/dashboard/low-stock")
def get_low_stock_medicines(db: Session = Depends(get_db)):
    """Get medicines with low stock"""
    medicines = db.query(models.Medicine).filter(
        models.Medicine.stock_quantity <= models.Medicine.reorder_level
    ).all()
    return medicines

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
