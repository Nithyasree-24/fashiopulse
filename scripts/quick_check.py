import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

from api.models import Clothing

media_path = os.path.join(os.getcwd(), 'media', 'uploads')

# Get first 10 products (what shows on frontend by default)
products = Clothing.objects.all()[:10]

print("Checking first 10 products visible in frontend:\n")
print("=" * 100)
print(f"{'ID':<5} {'Name':<45} {'DB Path':<35} {'File Exists'}")
print("=" * 100)

for p in products:
    name = p.product_name[:40]
    path_display = (p.product_image[:30] + '...') if p.product_image and len(p.product_image) > 30 else (p.product_image or 'NULL')
    
    file_exists = "❌"
    if p.product_image:
        filename = p.product_image.replace('/media/uploads/', '')
        full_path = os.path.join(media_path, filename)
        if os.path.exists(full_path):
            file_exists = "✅"
    
    print(f"{p.product_id:<5} {name:<45} {path_display:<35} {file_exists}")

print("\n" + "=" * 100)
print("\nTo test in browser, try these URLs:")
print("  http://localhost:8000/media/uploads/product_1.jpg")
print("  http://localhost:8000/media/uploads/product_2.jpg")
print("\nFrontend should request:")
print("  http://localhost:8000/media/uploads/product_X.jpg")
