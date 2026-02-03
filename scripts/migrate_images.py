import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

from api.models import Clothing

media_path = os.path.join(os.getcwd(), 'media', 'uploads')

products = Clothing.objects.all()
updated_count = 0
already_correct = 0
not_found = 0

for p in products:
    base_name = f"product_{p.product_id}"
    filename = None
    
    # Check for .jpg or .jpeg
    if os.path.exists(os.path.join(media_path, f"{base_name}.jpg")):
        filename = f"{base_name}.jpg"
    elif os.path.exists(os.path.join(media_path, f"{base_name}.jpeg")):
        filename = f"{base_name}.jpeg"
    
    correct_path = f"/media/uploads/{filename}" if filename else None
    
    if filename:
        if p.product_image != correct_path:
            p.product_image = correct_path
            p.save()
            updated_count += 1
        else:
            already_correct += 1
    else:
        not_found += 1
        print(f"⚠️ No image file found for product {p.product_id}")

print(f"\n✅ Already correct: {already_correct}")
print(f"🔄 Updated: {updated_count}")
print(f"❌ No file found: {not_found}")
print(f"\nTotal products processed: {products.count()}")
