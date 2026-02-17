from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime
from app.services.invoice_service import InvoiceGenerator
import os

class OrderService:
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ORD-{timestamp}"
    
    @staticmethod
    def generate_invoice_number():
        """Generate unique invoice number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"INV-{timestamp}"
    
    @staticmethod
    def search_medicine(db: Session, query: str, limit: int = 10):
        """Search medicine by name (Hindi or English) or generic name"""
        medicines = db.query(models.Medicine).filter(
            (models.Medicine.name.ilike(f"%{query}%")) |
            (models.Medicine.name_hindi.ilike(f"%{query}%")) |
            (models.Medicine.generic_name.ilike(f"%{query}%"))
        ).limit(limit).all()
        
        return medicines
    
    @staticmethod
    def get_or_create_customer(db: Session, name: str, phone: str, address: str = None):
        """Get existing customer or create new one"""
        # Check if customer exists
        customer = db.query(models.Customer).filter(
            models.Customer.phone == phone
        ).first()
        
        if customer:
            # Update name and address if provided
            if name and name != customer.name:
                customer.name = name
            if address:
                customer.address = address
            db.commit()
            db.refresh(customer)
            return customer
        
        # Create new customer
        new_customer = models.Customer(
            name=name,
            phone=phone,
            address=address
        )
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        return new_customer
    
    @staticmethod
    def create_order_from_ai_agent(db: Session, order_data: schemas.AIAgentOrderRequest):
        """
        Process order from AI voice agent
        1. Find/create customer
        2. Search and match medicines
        3. Create order with items
        4. Generate invoice
        5. Return order details
        """
        try:
            # Get or create customer
            customer = OrderService.get_or_create_customer(
                db,
                name=order_data.customer_name,
                phone=order_data.customer_phone,
                address=order_data.customer_address
            )
            
            # Create order
            order = models.Order(
                order_number=OrderService.generate_order_number(),
                customer_id=customer.id,
                order_source="ai-agent",
                language_used=order_data.language,
                status="pending"
            )
            db.add(order)
            db.flush()  # Get order ID
            
            # Process medicines and create order items
            total_amount = 0.0
            order_items = []
            missing_medicines = []
            
            for med_request in order_data.medicines:
                med_name = med_request.get("name")
                quantity = med_request.get("quantity", 1)
                packaging = med_request.get("packaging", "strip")
                
                # Search for medicine
                medicines = OrderService.search_medicine(db, med_name, limit=1)
                
                if not medicines:
                    missing_medicines.append(med_name)
                    continue
                
                medicine = medicines[0]
                
                # Check stock
                if medicine.stock_quantity < quantity:
                    missing_medicines.append(f"{med_name} (insufficient stock)")
                    continue
                
                # Calculate price
                item_total = medicine.price_per_unit * quantity
                
                # Create order item
                order_item = models.OrderItem(
                    order_id=order.id,
                    medicine_id=medicine.id,
                    quantity=quantity,
                    packaging_type=packaging,
                    price_per_unit=medicine.price_per_unit,
                    total_price=item_total
                )
                db.add(order_item)
                order_items.append(order_item)
                
                # Update stock
                medicine.stock_quantity -= quantity
                
                total_amount += item_total
            
            # Check if we have any items
            if not order_items:
                db.rollback()
                return {
                    "success": False,
                    "message": f"Could not find medicines: {', '.join(missing_medicines)}",
                    "missing_medicines": missing_medicines
                }
            
            # Calculate totals
            discount = 0.0
            tax_rate = 0.0  # You can add GST calculation here
            tax_amount = total_amount * (tax_rate / 100)
            final_amount = total_amount - discount + tax_amount
            
            order.total_amount = total_amount
            order.discount_amount = discount
            order.tax_amount = tax_amount
            order.final_amount = final_amount
            order.status = "confirmed"
            
            # Create invoice
            invoice = models.Invoice(
                invoice_number=OrderService.generate_invoice_number(),
                order_id=order.id,
                subtotal=total_amount,
                discount=discount,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                total_amount=final_amount,
                payment_status="unpaid"
            )
            db.add(invoice)
            
            # Update customer stats
            customer.total_orders += 1
            customer.total_amount_spent += final_amount
            
            db.commit()
            db.refresh(order)
            db.refresh(invoice)
            
            # Generate PDF
            pdf_dir = "invoices"
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_filename = f"{invoice.invoice_number}.pdf"
            pdf_path = os.path.join(pdf_dir, pdf_filename)
            
            invoice_generator = InvoiceGenerator()
            invoice_generator.generate_invoice_pdf(order, invoice, pdf_path)
            
            # Update invoice with PDF path
            invoice.pdf_path = pdf_path
            db.commit()
            
            response = {
                "success": True,
                "message": "Order created successfully! आर्डर सफलतापूर्वक बन गया!",
                "order_id": order.id,
                "order_number": order.order_number,
                "invoice_number": invoice.invoice_number,
                "total_amount": final_amount,
                "invoice_pdf_url": pdf_path
            }
            
            if missing_medicines:
                response["warning"] = f"Some medicines not found: {', '.join(missing_medicines)}"
            
            return response
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Error creating order: {str(e)}"
            }
    
    @staticmethod
    def create_order(db: Session, order_data: schemas.OrderCreate):
        """Create order from manual entry or web interface"""
        try:
            # Get or create customer
            customer = OrderService.get_or_create_customer(
                db,
                name=order_data.customer_name,
                phone=order_data.customer_phone,
                address=order_data.customer_address
            )
            
            # Create order
            order = models.Order(
                order_number=OrderService.generate_order_number(),
                customer_id=customer.id,
                order_source=order_data.order_source,
                language_used=order_data.language_used,
                notes=order_data.notes,
                status="pending"
            )
            db.add(order)
            db.flush()
            
            # Process items
            total_amount = 0.0
            
            for item_data in order_data.items:
                medicine = db.query(models.Medicine).filter(
                    models.Medicine.id == item_data.medicine_id
                ).first()
                
                if not medicine:
                    db.rollback()
                    raise ValueError(f"Medicine ID {item_data.medicine_id} not found")
                
                if medicine.stock_quantity < item_data.quantity:
                    db.rollback()
                    raise ValueError(f"Insufficient stock for {medicine.name}")
                
                item_total = medicine.price_per_unit * item_data.quantity
                
                order_item = models.OrderItem(
                    order_id=order.id,
                    medicine_id=medicine.id,
                    quantity=item_data.quantity,
                    packaging_type=item_data.packaging_type,
                    price_per_unit=medicine.price_per_unit,
                    total_price=item_total
                )
                db.add(order_item)
                
                medicine.stock_quantity -= item_data.quantity
                total_amount += item_total
            
            # Calculate totals
            discount = 0.0
            tax_rate = 0.0
            tax_amount = total_amount * (tax_rate / 100)
            final_amount = total_amount - discount + tax_amount
            
            order.total_amount = total_amount
            order.discount_amount = discount
            order.tax_amount = tax_amount
            order.final_amount = final_amount
            order.status = "confirmed"
            
            # Create invoice
            invoice = models.Invoice(
                invoice_number=OrderService.generate_invoice_number(),
                order_id=order.id,
                subtotal=total_amount,
                discount=discount,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                total_amount=final_amount,
                payment_status="unpaid"
            )
            db.add(invoice)
            
            # Update customer stats
            customer.total_orders += 1
            customer.total_amount_spent += final_amount
            
            db.commit()
            db.refresh(order)
            db.refresh(invoice)
            
            # Generate PDF
            pdf_dir = "invoices"
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_filename = f"{invoice.invoice_number}.pdf"
            pdf_path = os.path.join(pdf_dir, pdf_filename)
            
            invoice_generator = InvoiceGenerator()
            invoice_generator.generate_invoice_pdf(order, invoice, pdf_path)
            
            invoice.pdf_path = pdf_path
            db.commit()
            
            return order
            
        except Exception as e:
            db.rollback()
            raise e
