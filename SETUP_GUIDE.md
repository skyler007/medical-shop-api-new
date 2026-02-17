# 🚀 Quick Setup Guide - Medical Shop Management System

## ✅ What You Have

A complete **Python FastAPI** backend system for your medical shop that:
- Handles phone orders in **Hindi + English**
- Automatically generates **PDF invoices**
- Ready to integrate with **AI voice agents** (Vapi, Bland, Twilio)
- Manages medicine inventory with Hindi names
- Tracks customers and orders

---

## 📋 Setup Steps (Step-by-Step)

### Step 1: Install Python
Download and install Python 3.8+ from https://www.python.org/downloads/

**Check installation:**
```bash
python --version
```

### Step 2: Install PostgreSQL
Download from https://www.postgresql.org/download/

**After installation:**
1. Open pgAdmin (comes with PostgreSQL)
2. Create a new database called `medical_shop_db`
3. Note your username (usually `postgres`) and password

### Step 3: Extract and Navigate to Project
```bash
cd medical-shop-api
```

### Step 4: Create Virtual Environment
```bash
python -m venv venv
```

### Step 5: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### Step 6: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 7: Configure Environment

1. Copy `.env.example` to `.env`
2. Edit `.env` file:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/medical_shop_db

SHOP_NAME=Your Medical Store Name
SHOP_ADDRESS=Your Address Here
SHOP_PHONE=+91-9876543210
SHOP_EMAIL=yourmail@example.com
SHOP_GST=22AAAAA0000A1Z5
```

### Step 8: Seed Sample Data
```bash
python seed_data.py
```
This adds 15 sample medicines to your database.

### Step 9: Start the Server

**Windows:**
```bash
start.bat
```

**Mac/Linux:**
```bash
./start.sh
```

**OR manually:**
```bash
python main.py
```

### Step 10: Test the API

Open browser: http://localhost:8000/docs

**OR run test script:**
```bash
python test_api.py
```

---

## 🎯 Quick Test

### Test 1: Search Medicine (Hindi)
```bash
curl -X POST http://localhost:8000/api/medicines/search \
  -H "Content-Type: application/json" \
  -d '{"query": "पैरासिटामोल", "limit": 5}'
```

### Test 2: Create Order from AI Agent
```bash
curl -X POST http://localhost:8000/api/ai-agent/order \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "राजेश कुमार",
    "customer_phone": "+919876543210",
    "medicines": [
      {"name": "paracetamol", "quantity": 2, "packaging": "strip"}
    ],
    "language": "hindi"
  }'
```

The invoice PDF will be created in the `invoices/` folder!

---

## 🤖 Connecting AI Voice Agent

### For Vapi.ai (Recommended)

1. **Sign up**: https://vapi.ai
2. **Create Assistant**
3. **Configure**:
   - Language: Hindi + English
   - Voice: Select Hindi voice
   - Webhook URL: `http://your-domain.com/api/ai-agent/order`
   
4. **Set Conversation Flow**:
   ```
   - Greet customer (नमस्ते / Hello)
   - Ask for name
   - Ask for medicines needed
   - Ask for quantities
   - Confirm order
   - Send to webhook
   ```

5. **Test**: Call the number Vapi provides

### For Bland.ai

Similar setup as Vapi.ai - point webhook to your API endpoint.

---

## 📊 API Endpoints

**Full documentation**: http://localhost:8000/docs

### Main Endpoints:

- `POST /api/ai-agent/order` - **Main endpoint for voice AI**
- `POST /api/medicines/search` - Search medicines
- `GET /api/orders` - List all orders
- `GET /api/dashboard/stats` - Get statistics
- `GET /api/invoices/{id}/download` - Download invoice PDF

---

## 🔧 Common Issues

### "Cannot connect to database"
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Check username/password

### "Module not found"
```bash
pip install -r requirements.txt --force-reinstall
```

### "Port 8000 already in use"
```bash
# Change port in main.py:
uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## 📱 Next Steps

### For Production:

1. **Deploy Backend**
   - Heroku (easiest): https://heroku.com
   - Railway: https://railway.app
   - DigitalOcean: https://digitalocean.com

2. **Get Domain & SSL**
   - Use Cloudflare for free SSL
   - Point domain to your server

3. **Configure Voice AI**
   - Update webhook URL to your domain
   - Test end-to-end flow

4. **Optional: Add WhatsApp/SMS**
   - Twilio for SMS: https://twilio.com
   - WhatsApp Business API for invoice delivery

---

## 🆘 Need Help?

1. Check `/docs` for API documentation
2. Review README.md for detailed info
3. Check error messages in console
4. Verify PostgreSQL logs

---

## 📝 Files Overview

```
medical-shop-api/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── seed_data.py        # Sample data loader
├── test_api.py         # Test script
├── .env.example        # Environment template
├── README.md           # Detailed documentation
├── start.bat           # Windows startup
├── start.sh            # Mac/Linux startup
└── app/
    ├── database.py     # Database config
    ├── models.py       # Database models
    ├── schemas.py      # API schemas
    └── services/
        ├── order_service.py    # Order logic
        └── invoice_service.py  # PDF generation
```

---

**You're all set! 🎉**

**Run `python main.py` and start building!**

**शुभकामनाएं! 🚀**
