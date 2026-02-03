import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

from api.models import Clothing

media_path = os.path.join(os.getcwd(), 'media', 'uploads')

products = Clothing.objects.all()
missing_images = []
has_images = []
wrong_format = []

for p in products:
    if not p.product_image:
        missing_images.append(p.product_id)
    elif not p.product_image.startswith('/media/uploads/'):
        wrong_format.append((p.product_id, p.product_image))
    else:
        # Extract filename from path
        filename = p.product_image.replace('/media/uploads/', '')
        full_path = os.path.join(media_path, filename)
        if os.path.exists(full_path):
            has_images.append(p.product_id)
        else:
            missing_images.append((p.product_id, p.product_image))

print(f"✅ Products with valid images: {len(has_images)}")
print(f"❌ Products with missing image files: {len([m for m in missing_images if isinstance(m, tuple)])}")
print(f"⚠️ Products with no image path: {len([m for m in missing_images if isinstance(m, int)])}")
print(f"🔧 Products with wrong format: {len(wrong_format)}")

if wrong_format:
    print("\nProducts with wrong format (not starting with /media/uploads/):")
    for pid, path in wrong_format[:10]:
        print(f"  ID {pid}: {path}")

if missing_images:
    print(f"\nFirst 10 products with missing images:")
    for item in missing_images[:10]:
        if isinstance(item, tuple):
            print(f"  ID {item[0]}: Expected {item[1]}")
        else:
            print(f"  ID {item}: No path in database")
