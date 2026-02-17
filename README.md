# 🏥 Medical Shop Management System

AI-powered medical shop order and invoice management system with **Hindi + English** voice support.

## 🌟 Features

- ✅ **Bilingual Support** - Hindi & English (and Hinglish mix)
- ✅ **AI Voice Agent Integration** - Ready for Vapi.ai, Bland.ai, Twilio
- ✅ **Automatic Invoice Generation** - Professional PDF invoices
- ✅ **Medicine Inventory Management** - Stock tracking with Hindi names
- ✅ **Order Management** - Phone orders, walk-ins, AI agent orders
- ✅ **Customer Management** - Regular customer tracking
- ✅ **Low Stock Alerts** - Reorder level tracking
- ✅ **REST API** - Complete API for integrations

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- PostgreSQL
- pip

### 2. Installation

```bash
# Clone or download the project
cd medical-shop-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Install PostgreSQL (if not installed)
# Windows: Download from postgresql.org
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql

# Create database
psql -U postgres
CREATE DATABASE medical_shop_db;
\q
```

### 4. Configuration

```bash
# Copy example env file
copy .env .env  # Windows
# OR
cp .env .env    # Mac/Linux

# Edit .env file with your details:
# - Update DATABASE_URL with your PostgreSQL credentials
# - Add your shop details (name, address, phone, GST)
# - Add API keys if using AI services
```

### 5. Seed Sample Data

```bash
# Populate database with sample medicines
python seed_data.py
```

### 6. Run the Application

```bash
# Start the server
python main.py

# OR use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access the API

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs (Interactive Swagger UI)
- Health Check: http://localhost:8000/health

## 📡 AI Voice Agent Integration

### How It Works

```
Customer Calls → AI Voice Agent (Vapi/Bland/Twilio) 
    → Captures Order Details (Hindi/English)
    → Sends to API: POST /api/ai-agent/order
    → System Processes Order
    → Generates Invoice PDF
    → Returns Invoice Details
    → AI Agent Confirms to Customer
```

### API Endpoint for AI Agent

**POST** `/api/ai-agent/order`

**Request Body:**
```json
{
  "customer_name": "राजेश कुमार",
  "customer_phone": "+919876543210",
  "customer_address": "123, दिल्ली",
  "medicines": [
    {
      "name": "पैरासिटामोल",
      "quantity": 2,
      "packaging": "strip"
    },
    {
      "name": "Crocin",
      "quantity": 1,
      "packaging": "strip"
    }
  ],
  "language": "hindi"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Order created successfully! आर्डर सफलतापूर्वक बन गया!",
  "order_id": 1,
  "order_number": "ORD-20240217123456",
  "invoice_number": "INV-20240217123456",
  "total_amount": 125.50,
  "invoice_pdf_url": "invoices/INV-20240217123456.pdf"
}
```

### Setting Up Voice AI Services

#### Option 1: Vapi.ai (Recommended)

1. Sign up at https://vapi.ai
2. Create a new assistant
3. Configure:
   - **Language**: Hindi + English
   - **Voice**: Select Hindi voice or multilingual
   - **Webhook**: `https://your-domain.com/api/ai-agent/order`
4. Set up conversation flow to collect:
   - Customer name
   - Phone number
   - Medicine names (with quantities and packaging)
   - Delivery address (optional)

#### Option 2: Bland.ai

1. Sign up at https://bland.ai
2. Create phone agent
3. Set webhook to your API endpoint
4. Configure for Hindi/English support

#### Option 3: Twilio + Claude API

```python
# Example integration (you'll need to build this)
from twilio.rest import Client
import anthropic

# On incoming call:
# 1. Convert speech to text (Twilio)
# 2. Send to Claude for understanding
# 3. Extract order details
# 4. Call your API
# 5. Convert response to speech
# 6. Play to customer
```

## 📚 API Documentation

### Medicine APIs

- `POST /api/medicines` - Add new medicine
- `GET /api/medicines` - List all medicines
- `GET /api/medicines/{id}` - Get medicine by ID
- `PUT /api/medicines/{id}` - Update medicine
- `DELETE /api/medicines/{id}` - Delete medicine
- `POST /api/medicines/search` - Search medicines (Hindi/English)

### Customer APIs

- `POST /api/customers` - Create customer
- `GET /api/customers` - List customers
- `GET /api/customers/{id}` - Get customer
- `GET /api/customers/phone/{phone}` - Get by phone

### Order APIs

- `POST /api/orders` - Create order manually
- `GET /api/orders` - List orders
- `GET /api/orders/{id}` - Get order details
- `GET /api/orders/number/{order_number}` - Get by order number

### Invoice APIs

- `GET /api/invoices/{id}` - Get invoice
- `GET /api/invoices/number/{invoice_number}` - Get by invoice number
- `GET /api/invoices/{id}/download` - Download PDF

### Dashboard APIs

- `GET /api/dashboard/stats` - Get statistics
- `GET /api/dashboard/low-stock` - Low stock medicines

## 🗄️ Database Schema

### Tables

1. **medicines** - Medicine inventory
2. **customers** - Customer details
3. **orders** - Order records
4. **order_items** - Order line items
5. **invoices** - Invoice records

## 📦 Sample Data

The system comes with 15 pre-loaded medicines including:
- Paracetamol (पैरासिटामोल)
- Crocin (क्रोसिन)
- Dolo 650 (डोलो)
- Azithromycin (एज़िथ्रोमाइसिन)
- Amoxicillin (एमोक्सिसिलिन)
- And more...

## 🧪 Testing the API

### Using Postman or curl

```bash
# Create an order from AI agent
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

# Search for medicine
curl -X POST http://localhost:8000/api/medicines/search \
  -H "Content-Type: application/json" \
  -d '{"query": "पैरासिटामोल", "limit": 5}'

# Get dashboard stats
curl http://localhost:8000/api/dashboard/stats
```

### Using API Docs

Visit http://localhost:8000/docs for interactive API testing with Swagger UI.

## 📱 Next Steps

### For Production Deployment

1. **Set up domain and SSL**
   - Get a domain name
   - Set up SSL certificate (Let's Encrypt)

2. **Deploy backend**
   - Use Heroku, AWS, DigitalOcean, or Railway
   - Set environment variables
   - Set up PostgreSQL database

3. **Configure Voice AI**
   - Point webhook to your domain
   - Test end-to-end flow

4. **Add WhatsApp/SMS Integration** (Optional)
   - Use Twilio for SMS
   - Use WhatsApp Business API for invoice delivery

5. **Build Frontend** (Optional)
   - React/Vue/Angular dashboard
   - Medicine management
   - Order tracking
   - Reports and analytics

## 🛠️ Customization

### Adding GST Calculation

Edit `app/services/order_service.py`:

```python
# In create_order_from_ai_agent method
tax_rate = 12.0  # Set your GST rate
tax_amount = total_amount * (tax_rate / 100)
```

### Customizing Invoice Design

Edit `app/services/invoice_service.py` to modify PDF layout, colors, logo, etc.

### Adding More Packaging Types

Edit `app/models.py`:

```python
class PackagingType(str, enum.Enum):
    STRIP = "strip"
    BOTTLE = "bottle"
    BOX = "box"
    LOOSE = "loose"
    TUBE = "tube"
    VIAL = "vial"
    INJECTION = "injection"  # Add new type
```

## 🐛 Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
# Windows: Check Services
# Mac/Linux: sudo service postgresql status

# Verify DATABASE_URL in .env file
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use
```bash
# Change port in main.py or run:
uvicorn main:app --port 8001
```

## 📞 Support

For issues or questions:
1. Check `/docs` endpoint for API documentation
2. Review error messages in console
3. Check PostgreSQL logs

## 📝 License

This project is provided as-is for educational and commercial use.

## 🙏 Credits

Built with:
- FastAPI
- PostgreSQL
- SQLAlchemy
- ReportLab
- Pydantic

---

**Happy Automating! 🚀**

**शुभकामनाएं! 🎉**
