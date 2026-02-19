from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from fastapi.responses import StreamingResponse
import io
from sqlalchemy.orm import joinedload
from app.services.invoice_service import InvoiceGenerator
from typing import List
import os

from app.database import engine, get_db
from app import models, schemas
from app.services.order_service import OrderService
from app.auth import verify_password, get_password_hash, create_access_token, get_current_user, require_roles

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

# ===================================================
# REPLACE your existing vapi_webhook function in main.py
# ===================================================

# ===================================================
# REPLACE your existing vapi_webhook function in main.py
# Handles BOTH Vapi payload formats + stock check
# ===================================================

@app.post("/api/vapi/webhook")
async def vapi_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        import re
        from sqlalchemy import or_

        body = await request.json()
        print("Vapi webhook received:", body)

        # ── Detect payload format ─────────────────────────────
        message = body.get("message", {})
        msg_type = message.get("type", "")

        # FORMAT 1: {"message": {"type": "tool-calls", "toolCalls": [...]}}
        if msg_type == "tool-calls":
            tool_calls = message.get("toolCalls", [])
            if not tool_calls:
                return {"results": [{"toolCallId": "none", "result": "No order data"}]}
            tool_call = tool_calls[0]
            tool_call_id = tool_call.get("id", "tool-1")
            function_args = tool_call.get("function", {}).get("arguments", {})

        # FORMAT 2: {"customer_name": "...", "medicines": [...]} (flat format)
        elif "medicines" in body or "customer_name" in body:
            print("Detected flat payload format from Vapi")
            tool_call_id = "tool-1"
            function_args = body  # the body itself is the args

        else:
            print("Unknown format, ignoring:", msg_type)
            return {"status": "received"}

        # ── Extract raw data ──────────────────────────────────
        raw_medicines = function_args.get("medicines", [])
        cleaned_medicines = []
        out_of_stock = []

        for m in raw_medicines:
            med_name = m.get("name", "").strip()
            if not med_name:
                continue

            # ── STOCK CHECK ───────────────────────────────────
            found = db.query(models.Medicine).filter(
                or_(
                    models.Medicine.name.ilike(f"%{med_name}%"),
                    models.Medicine.name_hindi.ilike(f"%{med_name}%"),
                    models.Medicine.generic_name.ilike(f"%{med_name}%")
                )
            ).first()

            if not found or found.stock_quantity <= 0:
                print(f"Stock check FAILED: {med_name} -> out of stock or not found")
                out_of_stock.append(med_name)
                continue

            print(f"Stock check OK: {med_name} -> qty={found.stock_quantity}")

            # ── Clean quantity ────────────────────────────────
            raw_qty = str(m.get("quantity", "1"))
            qty_match = re.search(r'\d+', raw_qty)
            qty = int(qty_match.group()) if qty_match else 1

            # ── Clean packaging ───────────────────────────────
            raw_pack = str(m.get("packaging", "strip")).lower()
            packaging = "strip"
            for vp in ["strip", "bottle", "box", "loose", "tube", "vial"]:
                if vp in raw_pack:
                    packaging = vp
                    break

            cleaned_medicines.append({
                "name": med_name,
                "quantity": qty,
                "packaging": packaging
            })

        # ── If ALL medicines out of stock ─────────────────────
        if not cleaned_medicines:
            msg = "Sorry, ye medicines stock mein nahi hain: {}. Koi aur medicine chahiye?".format(
                ", ".join(out_of_stock))
            print("All medicines out of stock:", out_of_stock)
            return {"results": [{"toolCallId": tool_call_id, "result": msg}]}

        # ── Clean phone ───────────────────────────────────────
        raw_phone = str(function_args.get("customer_phone", "0000000000"))
        digits_only = re.sub(r'\D', '', raw_phone)
        if len(digits_only) == 10:
            phone = "+91" + digits_only
        elif len(digits_only) > 10:
            phone = "+" + digits_only
        else:
            phone = "+91" + digits_only.zfill(10)

        # ── Clean name ────────────────────────────────────────
        customer_name = function_args.get("customer_name", "").strip() or "Customer"

        print(f"Placing order -> name={customer_name}, phone={phone}, medicines={cleaned_medicines}")

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
            skipped = ""
            if out_of_stock:
                skipped = " Note: {} stock mein nahi tha.".format(", ".join(out_of_stock))
            msg = "Order placed! Order number {}. Total {} rupees. Shukriya!{}".format(
                result.get("order_number"), result.get("total_amount"), skipped)
        else:
            msg = "Sorry order nahi hua. {}".format(result.get("message"))

        return {"results": [{"toolCallId": tool_call_id, "result": msg}]}

    except Exception as e:
        print("Vapi webhook error:", str(e))
        import traceback
        traceback.print_exc()
        return {"results": [{"toolCallId": "error", "result": "Error processing order. Please call again."}]}
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
def create_medicine(medicine: schemas.MedicineCreate, db: Session = Depends(get_db),
                    _=Depends(require_roles("shopkeeper", "admin"))):
    db_medicine = models.Medicine(**medicine.dict())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

@app.get("/api/medicines", response_model=List[schemas.MedicineResponse])
def get_medicines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                  _=Depends(get_current_user)):
    return db.query(models.Medicine).offset(skip).limit(limit).all()

@app.get("/api/medicines/{medicine_id}", response_model=schemas.MedicineResponse)
def get_medicine(medicine_id: int, db: Session = Depends(get_db),
                 _=Depends(get_current_user)):
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine

@app.put("/api/medicines/{medicine_id}", response_model=schemas.MedicineResponse)
def update_medicine(medicine_id: int, medicine_update: schemas.MedicineUpdate, db: Session = Depends(get_db),
                    _=Depends(require_roles("shopkeeper", "admin"))):
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    for key, value in medicine_update.dict(exclude_unset=True).items():
        setattr(medicine, key, value)
    db.commit()
    db.refresh(medicine)
    return medicine

@app.delete("/api/medicines/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medicine(medicine_id: int, db: Session = Depends(get_db),
                    _=Depends(require_roles("admin"))):
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(medicine)
    db.commit()

@app.post("/api/medicines/search", response_model=schemas.MedicineSearchResponse)
def search_medicines(search_request: schemas.MedicineSearchRequest, db: Session = Depends(get_db),
                     _=Depends(get_current_user)):
    medicines = OrderService.search_medicine(db, search_request.query, search_request.limit)
    return {"medicines": medicines, "total": len(medicines)}



# ===== CUSTOMER ROUTES =====
@app.post("/api/customers", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db),
                    _=Depends(require_roles("shopkeeper", "admin"))):
    existing = db.query(models.Customer).filter(models.Customer.phone == customer.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this phone already exists")
    db_customer = models.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.get("/api/customers", response_model=List[schemas.CustomerResponse])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                  _=Depends(require_roles("shopkeeper", "admin"))):
    return db.query(models.Customer).offset(skip).limit(limit).all()

@app.get("/api/customers/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db),
                 _=Depends(require_roles("shopkeeper", "admin"))):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.get("/api/customers/phone/{phone}", response_model=schemas.CustomerResponse)
def get_customer_by_phone(phone: str, db: Session = Depends(get_db),
                          _=Depends(require_roles("shopkeeper", "admin"))):
    customer = db.query(models.Customer).filter(models.Customer.phone == phone).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# ===== ORDER ROUTES =====
@app.post("/api/orders", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db),
                 _=Depends(get_current_user)):
    try:
        return OrderService.create_order(db, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error creating order: {}".format(str(e)))

@app.get("/api/orders", response_model=List[schemas.OrderResponse])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               _=Depends(require_roles("shopkeeper", "admin"))):
    return db.query(models.Order).order_by(models.Order.order_date.desc()).offset(skip).limit(limit).all()

@app.get("/api/orders/my", response_model=List[schemas.OrderResponse])
def get_my_orders(db: Session = Depends(get_db),
                  current_user: models.User = Depends(require_roles("customer"))):
    """Customer's own orders matched by phone."""
    if not current_user.phone:
        return []
    customer = db.query(models.Customer).filter(
        models.Customer.phone.ilike(f"%{current_user.phone.lstrip('+91').lstrip('91')}%")
    ).first()
    if not customer:
        return []
    return db.query(models.Order).filter(
        models.Order.customer_id == customer.id
    ).order_by(models.Order.order_date.desc()).all()

@app.get("/api/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    order = (
        db.query(models.Order)
        .options(
            joinedload(models.Order.invoice),        # 👈 LOAD INVOICE
            joinedload(models.Order.order_items)
            .joinedload(models.OrderItem.medicine), # 👈 LOAD MEDICINE ALSO
            joinedload(models.Order.customer)       # 👈 LOAD CUSTOMER
        )
        .filter(models.Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order

@app.get("/api/orders/number/{order_number}", response_model=schemas.OrderResponse)
def get_order_by_number(order_number: str, db: Session = Depends(get_db),
                        _=Depends(get_current_user)):
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

    invoice = (
        db.query(models.Invoice)
        .options(
            joinedload(models.Invoice.order)
            .joinedload(models.Order.order_items)
            .joinedload(models.OrderItem.medicine),
            joinedload(models.Invoice.order)
            .joinedload(models.Order.customer)
        )
        .filter(models.Invoice.id == invoice_id)
        .first()
    )

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    order = invoice.order

    # Generate PDF in memory
    buffer = io.BytesIO()
    invoice_generator = InvoiceGenerator()
    invoice_generator.generate_invoice_pdf(order, invoice, buffer)

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={invoice.invoice_number}.pdf"
        }
    )

# ===== DASHBOARD =====
@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db),
                        _=Depends(require_roles("shopkeeper", "admin"))):
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

@app.get("/api/dashboard/my-stats")
def get_my_stats(db: Session = Depends(get_db),
                 current_user: models.User = Depends(require_roles("customer"))):
    """Customer's own stats matched by phone."""
    if current_user.phone:
        phone_digits = current_user.phone.lstrip('+91').lstrip('91')
        customer = db.query(models.Customer).filter(
            models.Customer.phone.ilike(f"%{phone_digits}%")
        ).first()
        if customer:
            my_orders = db.query(models.Order).filter(models.Order.customer_id == customer.id).all()
            pending = sum(1 for o in my_orders if o.status == "pending")
            return {"total_orders": len(my_orders), "pending_orders": pending,
                    "total_spent": customer.total_amount_spent}
    return {"total_orders": 0, "pending_orders": 0, "total_spent": 0.0}

@app.get("/api/dashboard/low-stock")
def get_low_stock_medicines(db: Session = Depends(get_db),
                            _=Depends(require_roles("shopkeeper", "admin"))):
    return db.query(models.Medicine).filter(
        models.Medicine.stock_quantity <= models.Medicine.reorder_level).all()

# ===== ADMIN ROUTES =====
@app.get("/api/admin/users", response_model=List[schemas.UserAdminResponse])
def get_all_users(db: Session = Depends(get_db),
                  _=Depends(require_roles("admin"))):
    return db.query(models.User).order_by(models.User.created_at.desc()).all()

@app.put("/api/admin/users/{user_id}/status")
def update_user_status(user_id: int, update: schemas.UserStatusUpdate,
                       db: Session = Depends(get_db),
                       current_user: models.User = Depends(require_roles("admin"))):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own status")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = update.is_active
    db.commit()
    return {"message": "User status updated", "is_active": update.is_active}

# ===== AUTH ROUTES =====
@app.post("/api/auth/register", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    allowed_roles = {"customer", "shopkeeper"}
    role = user_data.role if user_data.role in allowed_roles else "customer"
    user = models.User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}

@app.post("/api/auth/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}

@app.get("/api/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.put("/api/auth/profile", response_model=schemas.UserResponse)
def update_profile(update: schemas.ProfileUpdate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    if update.name:
        current_user.name = update.name
    if update.phone is not None:
        current_user.phone = update.phone
    db.commit()
    db.refresh(current_user)
    return current_user

@app.put("/api/auth/change-password")
def change_password(data: schemas.ChangePassword, db: Session = Depends(get_db),
                    current_user: models.User = Depends(get_current_user)):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)