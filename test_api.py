"""
Test script to demonstrate API usage
Make sure the server is running before executing this
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_medicine_search():
    """Test medicine search"""
    print("\n🔍 Testing Medicine Search...")
    
    # Search in Hindi
    response = requests.post(
        f"{BASE_URL}/api/medicines/search",
        json={"query": "पैरासिटामोल", "limit": 3}
    )
    print(f"Search 'पैरासिटामोल': Found {len(response.json()['medicines'])} medicines")
    
    # Search in English
    response = requests.post(
        f"{BASE_URL}/api/medicines/search",
        json={"query": "crocin", "limit": 3}
    )
    print(f"Search 'crocin': Found {len(response.json()['medicines'])} medicines")

def test_create_order_from_ai():
    """Test creating order from AI agent"""
    print("\n🔍 Testing AI Agent Order Creation...")
    
    order_data = {
        "customer_name": "राजेश कुमार",
        "customer_phone": "+919876543210",
        "customer_address": "123, दिल्ली",
        "medicines": [
            {
                "name": "paracetamol",
                "quantity": 2,
                "packaging": "strip"
            },
            {
                "name": "crocin",
                "quantity": 1,
                "packaging": "strip"
            }
        ],
        "language": "hindi"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ai-agent/order",
        json=order_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Order Created Successfully!")
        print(f"   Order Number: {result['order_number']}")
        print(f"   Invoice Number: {result['invoice_number']}")
        print(f"   Total Amount: ₹{result['total_amount']}")
        print(f"   Invoice PDF: {result['invoice_pdf_url']}")
        return result
    else:
        print(f"❌ Error: {response.json()}")
        return None

def test_get_order_details(order_id):
    """Test getting order details"""
    print(f"\n🔍 Testing Get Order Details (ID: {order_id})...")
    
    response = requests.get(f"{BASE_URL}/api/orders/{order_id}")
    
    if response.status_code == 200:
        order = response.json()
        print(f"✅ Order Details Retrieved!")
        print(f"   Customer: {order['customer']['name']}")
        print(f"   Phone: {order['customer']['phone']}")
        print(f"   Items: {len(order['order_items'])}")
        print(f"   Total: ₹{order['final_amount']}")
        return order
    else:
        print(f"❌ Error: {response.json()}")
        return None

def test_dashboard_stats():
    """Test dashboard statistics"""
    print("\n🔍 Testing Dashboard Stats...")
    
    response = requests.get(f"{BASE_URL}/api/dashboard/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Dashboard Stats:")
        print(f"   Total Orders: {stats['total_orders']}")
        print(f"   Total Customers: {stats['total_customers']}")
        print(f"   Total Medicines: {stats['total_medicines']}")
        print(f"   Low Stock Items: {stats['low_stock_medicines']}")
        print(f"   Today's Orders: {stats['today_orders']}")
        print(f"   Total Revenue: ₹{stats['total_revenue']:.2f}")
    else:
        print(f"❌ Error: {response.json()}")

def test_all():
    """Run all tests"""
    print("=" * 50)
    print("Medical Shop API - Test Suite")
    print("=" * 50)
    
    try:
        test_health()
        test_medicine_search()
        result = test_create_order_from_ai()
        
        if result:
            test_get_order_details(result['order_id'])
        
        test_dashboard_stats()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server!")
        print("   Make sure the server is running at http://localhost:8000")
        print("   Run: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_all()
