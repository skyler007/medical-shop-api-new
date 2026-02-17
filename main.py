from fastapi import FastAPI, Depends, HTTPException, status, Request
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

app = FastAPI(
    title="Medical Shop Management API",
    description="AI-powered medical shop order and invoice management system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("invoices", exist_ok=True)
app.mount("/invoices", StaticFiles(directory="invoices"), name="invoices")

@app.get("/")
def root():
    return {"message": "Medical Shop API is running", "status": "healthy", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ===== VAPI WEBHOOK =====
# ===================================================
# REPLACE your existing vapi_webhook function in main.py
# This handles messy data from Vapi gracefully
# ===================================================

@app.post("/api/vapi/webhook")
async def vapi_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        print("Vapi webhook received:", body)
        message = body.get("message", {})
        msg_type = message.get("type", "")

        if msg_type == "tool-calls":
            tool_calls = message.get("toolCalls", [])
            if not tool_calls:
                return {"results": [{"toolCallId": "none", "result": "No order data"}]}

            tool_call = tool_calls[0]
            function_args = tool_call.get("function", {}).get("arguments", {})

            # ── Clean medicines list ──────────────────────────────
            raw_medicines = function_args.get("medicines", [])
            cleaned_medicines = []
            for m in raw_medicines:
                # Extract just the number from quantity like "5 packs", "2 strips", "1"
                raw_qty = str(m.get("quantity", "1"))
                import re
                qty_match = re.search(r'\d+', raw_qty)
                qty = int(qty_match.group()) if qty_match else 1

                # Normalize packaging
                raw_pack = str(m.get("packaging", "strip")).lower()
                valid_packagings = ["strip", "bottle", "box", "loose", "tube", "vial"]
                packaging = "strip"  # default
                for vp in valid_packagings:
                    if vp in raw_pack:
                        packaging = vp
                        break

                cleaned_medicines.append({
                    "name": m.get("name", ""),
                    "quantity": qty,
                    "packaging": packaging
                })

            # ── Clean phone number ────────────────────────────────
            raw_phone = str(function_args.get("customer_phone", "0000000000"))
            digits_only = re.sub(r'\D', '', raw_phone)
            # Add +91 if Indian number without country code
            if len(digits_only) == 10:
                phone = "+91" + digits_only
            elif len(digits_only) > 10:
                phone = "+" + digits_only
            else:
                phone = "+91" + digits_only.zfill(10)

            # ── Clean name ────────────────────────────────────────
            customer_name = function_args.get("customer_name", "").strip()
            if not customer_name:
                customer_name = "Customer"

            print(f"Cleaned order -> name={customer_name}, phone={phone}, medicines={cleaned_medicines}")

            order_request = schemas.AIAgentOrderRequest(
                customer_name=customer_name,
                customer_phone=phone,
                customer_address=function_args.get("customer_address", None) or None,
                medicines=cleaned_medicines,
                language=function_args.get("language", "hindi") or "hindi"
            )

            result = OrderService.create_order_from_ai_agent(db, order_request)
            print("Order result:", result)

            if result.get("success"):
                msg = "Order placed! Order number {}. Total {} rupees. Thank you! Shukriya!".format(
                    result.get("order_number"), result.get("total_amount"))
            else:
                msg = "Sorry could not place order. {}".format(result.get("message"))

            return {"results": [{"toolCallId": tool_call.get("id", "tool-1"), "result": msg}]}

        return {"status": "received"}

    except Exception as e:
        print("Vapi webhook error:", str(e))
        import traceback
        traceback.print_exc()
        return {"results": [{"toolCallId": "error", "result": "Error processing order. Please call again."}]}


# ===================================================
# ADD THIS SECTION TO YOUR main.py
# Place it right after the existing VAPI WEBHOOK section
# ===================================================

# ===== VAPI STOCK CHECK TOOL =====
@app.post("/api/vapi/check-stock")
async def vapi_check_stock(request: Request, db: Session = Depends(get_db)):
    """
    Vapi calls this endpoint mid-call as a Tool Call.
    It checks if a medicine is in stock and returns
    a spoken response in Hindi + English.
    """
    try:
        body = await request.json()
        print("Vapi check-stock received:", body)

        message = body.get("message", {})
        msg_type = message.get("type", "")

        if msg_type != "tool-calls":
            return {"status": "received"}

        tool_calls = message.get("toolCalls", [])
        if not tool_calls:
            return {"results": [{"toolCallId": "none", "result": "No medicine name provided."}]}

        tool_call = tool_calls[0]
        tool_call_id = tool_call.get("id", "tool-1")
        args = tool_call.get("function", {}).get("arguments", {})

        medicine_name = args.get("medicine_name", "").strip()

        if not medicine_name:
            return {
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Nahi hai."
                }]
            }

        # Search for the medicine (handles Hindi + English names)
        from sqlalchemy import or_
        medicines = db.query(models.Medicine).filter(
            or_(
                models.Medicine.name.ilike(f"%{medicine_name}%"),
                models.Medicine.name_hindi.ilike(f"%{medicine_name}%"),
                models.Medicine.generic_name.ilike(f"%{medicine_name}%")
            )
        ).all()

        if not medicines:
            return {
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Nahi hai."
                }]
            }

        # Found the medicine - check stock
        medicine = medicines[0]  # Best match
        stock = medicine.stock_quantity
        name_display = medicine.name

        if stock <= 0:
            result_msg = "Nahi hai."
        else:
            result_msg = "Haa."

        print(f"Stock check: {name_display} -> qty={stock} -> {result_msg}")

        return {
            "results": [{
                "toolCallId": tool_call_id,
                "result": result_msg
            }]
        }

    except Exception as e:
        print("Stock check error:", str(e))
        import traceback
        traceback.print_exc()
        return {
            "results": [{
                "toolCallId": "error",
                "result": "Nahi hai."
            }]
        }


# ===== VAPI BULK STOCK CHECK (check multiple medicines at once) =====
@app.post("/api/vapi/check-stock-bulk")
async def vapi_check_stock_bulk(request: Request, db: Session = Depends(get_db)):
    """
    Check stock for multiple medicines at once.
    Vapi can call this after collecting the full order
    to validate all items before confirming.
    """
    try:
        body = await request.json()
        message = body.get("message", {})
        msg_type = message.get("type", "")

        if msg_type != "tool-calls":
            return {"status": "received"}

        tool_calls = message.get("toolCalls", [])
        if not tool_calls:
            return {"results": [{"toolCallId": "none", "result": "No medicines provided."}]}

        tool_call = tool_calls[0]
        tool_call_id = tool_call.get("id", "tool-1")
        args = tool_call.get("function", {}).get("arguments", {})

        medicines_list = args.get("medicines", [])

        if not medicines_list:
            return {
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "No medicines in the order. Koi medicine nahi bataya."
                }]
            }

        from sqlalchemy import or_
        available = []
        unavailable = []

        for item in medicines_list:
            med_name = item.get("name", "").strip()
            qty_requested = item.get("quantity", 1)

            results = db.query(models.Medicine).filter(
                or_(
                    models.Medicine.name.ilike(f"%{med_name}%"),
                    models.Medicine.name_hindi.ilike(f"%{med_name}%"),
                    models.Medicine.generic_name.ilike(f"%{med_name}%")
                )
            ).all()

            if not results:
                unavailable.append(f"{med_name} (not found)")
            else:
                med = results[0]
                if med.stock_quantity <= 0:
                    unavailable.append(f"{med.name} (out of stock)")
                elif med.stock_quantity < qty_requested:
                    available.append(f"{med.name} (only {med.stock_quantity} available, you asked for {qty_requested})")
                else:
                    available.append(f"{med.name} x{qty_requested} ✓")

        if not unavailable:
            result_msg = "Sab haa."
        else:
            unavail_str = ', '.join(unavailable)
            result_msg = f"{unavail_str} nahi hai."

        return {
            "results": [{
                "toolCallId": tool_call_id,
                "result": result_msg
            }]
        }

    except Exception as e:
        print("Bulk stock check error:", str(e))
        return {
            "results": [{
                "toolCallId": "error",
                "result": "Stock check mein error hua. Please try again."
            }]
        }


# ===== AI AGENT ROUTES =====
@app.post("/api/ai-agent/order", response_model=schemas.AIAgentOrderResponse)
def create_order_from_ai_agent(order_request: schemas.AIAgentOrderRequest, db: Session = Depends(get_db)):
    result = OrderService.create_order_from_ai_agent(db, order_request)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to create order"))
    return result

# ===== MEDICINE ROUTES =====
@app.post("/api/medicines", response_model=schemas.MedicineResponse, status_code=status.HTTP_201_CREATED)
def create_medicine(medicine: schemas.MedicineCreate, db: Session = Depends(get_db)):
    db_medicine = models.Medicine(**medicine.dict())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

@app.get("/api/medicines", response_model=List[schemas.MedicineResponse])
def get_medicines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Medicine).offset(skip).limit(limit).all()

@app.get("/api/medicines/{medicine_id}", response_model=schemas.MedicineResponse)
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine

@app.put("/api/medicines/{medicine_id}", response_model=schemas.MedicineResponse)
def update_medicine(medicine_id: int, medicine_update: schemas.MedicineUpdate, db: Session = Depends(get_db)):
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    for key, value in medicine_update.dict(exclude_unset=True).items():
        setattr(medicine, key, value)
    db.commit()
    db.refresh(medicine)
    return medicine

@app.delete("/api/medicines/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(medicine)
    db.commit()

@app.post("/api/medicines/search", response_model=schemas.MedicineSearchResponse)
def search_medicines(search_request: schemas.MedicineSearchRequest, db: Session = Depends(get_db)):
    medicines = OrderService.search_medicine(db, search_request.query, search_request.limit)
    return {"medicines": medicines, "total": len(medicines)}

# ===== CUSTOMER ROUTES =====
@app.post("/api/customers", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
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
    return db.query(models.Customer).offset(skip).limit(limit).all()

@app.get("/api/customers/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.get("/api/customers/phone/{phone}", response_model=schemas.CustomerResponse)
def get_customer_by_phone(phone: str, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.phone == phone).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# ===== ORDER ROUTES =====
@app.post("/api/orders", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    try:
        return OrderService.create_order(db, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error creating order: {}".format(str(e)))

@app.get("/api/orders", response_model=List[schemas.OrderResponse])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Order).offset(skip).limit(limit).all()

@app.get("/api/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/orders/number/{order_number}", response_model=schemas.OrderResponse)
def get_order_by_number(order_number: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# ===== INVOICE ROUTES =====
@app.get("/api/invoices/{invoice_id}", response_model=schemas.InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@app.get("/api/invoices/{invoice_id}/download")
def download_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if not invoice.pdf_path or not os.path.exists(invoice.pdf_path):
        raise HTTPException(status_code=404, detail="Invoice PDF not found")
    return FileResponse(invoice.pdf_path, media_type="application/pdf",
                        filename="{}.pdf".format(invoice.invoice_number))

# ===== DASHBOARD =====
@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    from datetime import datetime
    total_orders = db.query(models.Order).count()
    total_customers = db.query(models.Customer).count()
    total_medicines = db.query(models.Medicine).count()
    low_stock = db.query(models.Medicine).filter(
        models.Medicine.stock_quantity <= models.Medicine.reorder_level).count()
    today_orders = db.query(models.Order).filter(
        models.Order.order_date >= datetime.now().date()).count()
    revenue_sum = sum([inv[0] for inv in db.query(models.Invoice).with_entities(
        models.Invoice.total_amount).all() if inv[0]])
    return {"total_orders": total_orders, "total_customers": total_customers,
            "total_medicines": total_medicines, "low_stock_medicines": low_stock,
            "today_orders": today_orders, "total_revenue": revenue_sum}

@app.get("/api/dashboard/low-stock")
def get_low_stock_medicines(db: Session = Depends(get_db)):
    return db.query(models.Medicine).filter(
        models.Medicine.stock_quantity <= models.Medicine.reorder_level).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)