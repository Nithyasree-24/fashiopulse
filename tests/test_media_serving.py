import requests
import os

# Test if Django is serving media files
base_url = "http://localhost:8000"

# Test 1: Check if server is running
try:
    response = requests.get(f"{base_url}/api/", timeout=5)
    print(f"✅ Django server is running (Status: {response.status_code})")
except Exception as e:
    print(f"❌ Django server not responding: {e}")
    exit(1)

# Test 2: Check if media files are accessible
test_images = [
    "/media/uploads/product_1.jpg",
    "/media/uploads/product_10.jpg",
    "/media/uploads/product_201.jpg",
    "/media/uploads/product_202.jpg"
]

print("\nTesting media file serving:")
for img_path in test_images:
    url = f"{base_url}{img_path}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {img_path} - OK (Size: {len(response.content)} bytes)")
        else:
            print(f"❌ {img_path} - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ {img_path} - Error: {e}")

print("\n" + "="*80)
print("If you see ✅ above, Django media serving is working correctly!")
print("If you see ❌, there's a configuration issue.")
