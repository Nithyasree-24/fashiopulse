import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

from api.models import Clothing

media_path = os.path.join(os.getcwd(), 'media', 'uploads')
files = set(os.listdir(media_path))

products = Clothing.objects.all()

missing_or_mismatch = 0
total_checked = 0

print("Checking ALL products for file extension mismatches...")
print("-" * 100)

for p in products:
    if p.product_image:
        total_checked += 1
        db_filename = p.product_image.replace('/media/uploads/', '')
        
        if db_filename not in files:
            # Check if it exists with different extension
            base_name = os.path.splitext(db_filename)[0]
            
            found_alt = False
            for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG']:
                alt_name = base_name + ext
                if alt_name in files:
                    print(f"⚠️ MISMATCH: ID {p.product_id} expects {db_filename} BUT found {alt_name}")
                    found_alt = True
                    break
            
            if not found_alt:
                 print(f"❌ MISSING: ID {p.product_id} expects {db_filename} (No file found)")
            
            missing_or_mismatch += 1

print("-" * 100)
print(f"Total Checked: {total_checked}")
print(f"Issues Found: {missing_or_mismatch}")
