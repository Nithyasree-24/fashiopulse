import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

from api.models import Clothing

media_path = os.path.join(os.getcwd(), 'media', 'uploads')
files = set(os.listdir(media_path))

products = Clothing.objects.all()
updated_count = 0

print("Fixing file extension mismatches...")
print("-" * 100)

for p in products:
    current_path = p.product_image or ""
    current_filename = current_path.replace('/media/uploads/', '')
    
    if current_filename not in files:
        # File missing, try to find alternate extension
        base_name = f"product_{p.product_id}"
        
        found_match = None
        for ext in ['.jpg', '.jpeg', '.JPG', '.JPEG', '.png']:
            alt_name = base_name + ext
            if alt_name in files:
                found_match = alt_name
                break
        
        if found_match:
            new_path = f"/media/uploads/{found_match}"
            p.product_image = new_path
            p.save()
            updated_count += 1
            print(f"✅ Fixed ID {p.product_id}: {current_filename} -> {found_match}")
        else:
            print(f"❌ Still missing: ID {p.product_id} (No file found)")

print("-" * 100)
print(f"Successfully updated {updated_count} products.")
