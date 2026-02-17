# -*- coding: utf-8 -*-
import sys
import io

# Fix encoding for Windows
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except:
    pass

"""
Sample data seeder for Medical Shop
Run this to populate your database with sample medicines
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from datetime import datetime, timedelta

def create_sample_medicines(db: Session):
    """Create sample medicines with Hindi names"""
    
    sample_medicines = [
        # Common medicines
        {
            "name": "Paracetamol 500mg",
            "name_hindi": "पैरासिटामोल",
            "generic_name": "Acetaminophen",
            "company": "Cipla",
            "composition": "Paracetamol 500mg",
            "price_per_unit": 2.0,
            "mrp": 2.5,
            "stock_quantity": 500,
            "reorder_level": 50,
            "default_packaging": "strip",
            "units_per_package": 10,
            "category": "Pain Relief",
            "prescription_required": False,
            "batch_number": "PCM2024001",
            "expiry_date": datetime.now() + timedelta(days=730),
            "rack_location": "A1"
        },
        {
            "name": "Crocin 650mg",
            "name_hindi": "क्रोसिन",
            "generic_name": "Paracetamol",
            "company": "GSK",
            "composition": "Paracetamol 650mg",
            "price_per_unit": 3.0,
            "mrp": 3.5,
            "stock_quantity": 300,
            "reorder_level": 30,
            "default_packaging": "strip",
            "units_per_package": 15,
            "category": "Pain Relief",
            "prescription_required": False,
            "batch_number": "CRC2024001",
            "expiry_date": datetime.now() + timedelta(days=720),
            "rack_location": "A2"
        },
        {
            "name": "Dolo 650",
            "name_hindi": "डोलो",
            "generic_name": "Paracetamol",
            "company": "Micro Labs",
            "composition": "Paracetamol 650mg",
            "price_per_unit": 2.5,
            "mrp": 3.0,
            "stock_quantity": 400,
            "reorder_level": 40,
            "default_packaging": "strip",
            "units_per_package": 15,
            "category": "Pain Relief",
            "prescription_required": False,
            "batch_number": "DOL2024001",
            "expiry_date": datetime.now() + timedelta(days=700),
            "rack_location": "A3"
        },
        {
            "name": "Azithromycin 500mg",
            "name_hindi": "एज़िथ्रोमाइसिन",
            "generic_name": "Azithromycin",
            "company": "Cipla",
            "composition": "Azithromycin 500mg",
            "price_per_unit": 35.0,
            "mrp": 40.0,
            "stock_quantity": 100,
            "reorder_level": 20,
            "default_packaging": "strip",
            "units_per_package": 5,
            "category": "Antibiotic",
            "prescription_required": True,
            "batch_number": "AZI2024001",
            "expiry_date": datetime.now() + timedelta(days=600),
            "rack_location": "B1"
        },
        {
            "name": "Amoxicillin 500mg",
            "name_hindi": "एमोक्सिसिलिन",
            "generic_name": "Amoxicillin",
            "company": "Sun Pharma",
            "composition": "Amoxicillin 500mg",
            "price_per_unit": 12.0,
            "mrp": 15.0,
            "stock_quantity": 200,
            "reorder_level": 30,
            "default_packaging": "strip",
            "units_per_package": 10,
            "category": "Antibiotic",
            "prescription_required": True,
            "batch_number": "AMO2024001",
            "expiry_date": datetime.now() + timedelta(days=650),
            "rack_location": "B2"
        },
        {
            "name": "Cetirizine 10mg",
            "name_hindi": "सेटीरिज़ीन",
            "generic_name": "Cetirizine",
            "company": "Dr. Reddy's",
            "composition": "Cetirizine Hydrochloride 10mg",
            "price_per_unit": 1.5,
            "mrp": 2.0,
            "stock_quantity": 350,
            "reorder_level": 40,
            "default_packaging": "strip",
            "units_per_package": 10,
            "category": "Antihistamine",
            "prescription_required": False,
            "batch_number": "CET2024001",
            "expiry_date": datetime.now() + timedelta(days=680),
            "rack_location": "C1"
        },
        {
            "name": "Omeprazole 20mg",
            "name_hindi": "ओमेप्राज़ोल",
            "generic_name": "Omeprazole",
            "company": "Lupin",
            "composition": "Omeprazole 20mg",
            "price_per_unit": 4.0,
            "mrp": 5.0,
            "stock_quantity": 250,
            "reorder_level": 30,
            "default_packaging": "strip",
            "units_per_package": 10,
            "category": "Antacid",
            "prescription_required": False,
            "batch_number": "OME2024001",
            "expiry_date": datetime.now() + timedelta(days=710),
            "rack_location": "D1"
        },
        {
            "name": "Pantoprazole 40mg",
            "name_hindi": "पैंटोप्राज़ोल",
            "generic_name": "Pantoprazole",
            "company": "Alkem",
            "composition": "Pantoprazole 40mg",
            "price_per_unit": 5.5,
            "mrp": 6.5,
            "stock_quantity": 180,
            "reorder_level": 25,
            "default_packaging": "strip",
            "units_per_package": 10,
            "category": "Antacid",
            "prescription_required": False,
            "batch_number": "PAN2024001",
            "expiry_date": datetime.now() + timedelta(days=690),
            "rack_location": "D2"
        },
        {
            "name": "Ibuprofen 400mg",
            "name_hindi": "इबुप्रोफेन",
            "generic_name": "Ibuprofen",
            "company": "Abbott",
            "composition": "Ibuprofen 400mg",
            "price_per_unit": 3.5,
            "mrp": 4.5,
            "stock_quantity": 280,
            "reorder_level": 35,
            "default_packaging": "strip",
            "units_per_package": 10,
            "category": "Pain Relief",
            "prescription_required": False,
            "batch_number": "IBU2024001",
            "expiry_date": datetime.now() + timedelta(days=670),
            "rack_location": "A4"
        },
        {
            "name": "Metformin 500mg",
            "name_hindi": "मेटफॉर्मिन",
            "generic_name": "Metformin",
            "company": "USV",
            "composition": "Metformin Hydrochloride 500mg",
            "price_per_unit": 1.8,
            "mrp": 2.5,
            "stock_quantity": 450,
            "reorder_level": 50,
            "default_packaging": "strip",
            "units_per_package": 15,
            "category": "Diabetes",
            "prescription_required": True,
            "batch_number": "MET2024001",
            "expiry_date": datetime.now() + timedelta(days=750),
            "rack_location": "E1"
        },
        {
            "name": "Atorvastatin 10mg",
            "name_hindi": "एटोर्वास्टेटिन",
            "generic_name": "Atorvastatin",
            "company": "Torrent",
            "composition": "Atorvastatin 10mg",
            "price_per_unit": 6.0,
            "mrp": 7.5,
            "stock_quantity": 150,
            "reorder_level": 25,
            "default_packaging": "strip",
            "units_per_package": 10,
            "category": "Cholesterol",
            "prescription_required": True,
            "batch_number": "ATO2024001",
            "expiry_date": datetime.now() + timedelta(days=640),
            "rack_location": "F1"
        },
        {
            "name": "Vitamin D3 60000 IU",
            "name_hindi": "विटामिन डी3",
            "generic_name": "Cholecalciferol",
            "company": "Mankind",
            "composition": "Cholecalciferol 60000 IU",
            "price_per_unit": 25.0,
            "mrp": 30.0,
            "stock_quantity": 120,
            "reorder_level": 20,
            "default_packaging": "strip",
            "units_per_package": 4,
            "category": "Vitamin",
            "prescription_required": False,
            "batch_number": "VIT2024001",
            "expiry_date": datetime.now() + timedelta(days=800),
            "rack_location": "G1"
        },
        {
            "name": "Multivitamin Tablets",
            "name_hindi": "मल्टीविटामिन",
            "generic_name": "Multivitamin",
            "company": "HealthKart",
            "composition": "Multivitamin & Minerals",
            "price_per_unit": 8.0,
            "mrp": 10.0,
            "stock_quantity": 200,
            "reorder_level": 30,
            "default_packaging": "strip",
            "units_per_package": 15,
            "category": "Vitamin",
            "prescription_required": False,
            "batch_number": "MUL2024001",
            "expiry_date": datetime.now() + timedelta(days=850),
            "rack_location": "G2"
        },
        {
            "name": "Diclofenac Gel 30g",
            "name_hindi": "डाइक्लोफेनाक जेल",
            "generic_name": "Diclofenac",
            "company": "Novartis",
            "composition": "Diclofenac Diethylamine 1.16% w/w",
            "price_per_unit": 120.0,
            "mrp": 150.0,
            "stock_quantity": 50,
            "reorder_level": 10,
            "default_packaging": "tube",
            "units_per_package": 1,
            "category": "Topical Pain Relief",
            "prescription_required": False,
            "batch_number": "DIC2024001",
            "expiry_date": datetime.now() + timedelta(days=600),
            "rack_location": "H1"
        },
        {
            "name": "Cough Syrup 100ml",
            "name_hindi": "खांसी की दवाई",
            "generic_name": "Dextromethorphan",
            "company": "Dabur",
            "composition": "Dextromethorphan HBr 10mg/5ml",
            "price_per_unit": 85.0,
            "mrp": 100.0,
            "stock_quantity": 80,
            "reorder_level": 15,
            "default_packaging": "bottle",
            "units_per_package": 1,
            "category": "Cough & Cold",
            "prescription_required": False,
            "batch_number": "COU2024001",
            "expiry_date": datetime.now() + timedelta(days=550),
            "rack_location": "I1"
        },
    ]
    
    # Create medicines
    for med_data in sample_medicines:
        medicine = models.Medicine(**med_data)
        db.add(medicine)
    
    db.commit()
    print("Created {} sample medicines".format(len(sample_medicines)))

def create_sample_customer(db: Session):
    """Create a sample customer"""
    customer = models.Customer(
        name="Ramesh Kumar",
        phone="+919876543210",
        address="123, Main Street, Delhi",
        is_regular=True,
        customer_id="CUST001"
    )
    db.add(customer)
    db.commit()
    print("Created sample customer")

def main():
    """Run the seeder"""
    print("Seeding database with sample data...")
    
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    print("Tables created")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_medicines = db.query(models.Medicine).count()
        if existing_medicines > 0:
            print("Database already has {} medicines. Skipping seeding.".format(existing_medicines))
            print("If you want to reseed, please clear the database first.")
            return
        
        # Seed data
        create_sample_medicines(db)
        create_sample_customer(db)
        
        print("\nDatabase seeding completed successfully!")
        print("\nSummary:")
        print("   Medicines: {}".format(db.query(models.Medicine).count()))
        print("   Customers: {}".format(db.query(models.Customer).count()))
        
    except Exception as e:
        print("Error seeding database: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()