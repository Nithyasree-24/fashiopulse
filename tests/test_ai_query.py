import requests
import json

url = "http://localhost:8000/api/ai-query/"

def test_query(prompt, user_id=1):
    data = {"prompt": prompt, "user_id": user_id}
    try:
        response = requests.post(url, json=data)
        print(f"\n--- Testing: '{prompt}' ---")
        if response.status_code == 200:
            res_data = response.json()
            print(f"Message: {res_data.get('message')}")
            products = res_data.get('products', [])
            print(f"Count: {len(products)}")
            for p in products[:3]:
                print(f"- {p['product_name']} | Cat: {p['product_category']} | Color: {p['color']} | Price: {p['price']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

# Test 1: Category Strictness (Red Dresses) - should NOT show red tops
test_query("red dresses")

# Test 2: Specific Name (Jeans) - should only show items containing 'jeans' in name
test_query("jeans")

# Test 3: Budget Constraint (Dresses under 2000)
test_query("dresses under 2000")
