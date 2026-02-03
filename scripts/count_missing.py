import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

from api.models import Clothing

media_path = os.path.join(os.getcwd(), 'media', 'uploads')

# Get all image files
image_files = set(os.listdir(media_path))
products = Clothing.objects.all()

missing = []
has_image = []

for p in products:
    expected_jpg = f"product_{p.product_id}.jpg"
    expected_jpeg = f"product_{p.product_id}.jpeg"
    
    if expected_jpg in image_files or expected_jpeg in image_files:
        has_image.append(p.product_id)
    else:
        missing.append(p.product_id)

print(f"✅ Products WITH images: {len(has_image)}")
print(f"❌ Products WITHOUT images: {len(missing)}")
print(f"\nMissing product IDs: {missing[:20]}...")  # Show first 20
print(f"\nTotal products in database: {products.count()}")
print(f"Total image files: {len(image_files)}")
