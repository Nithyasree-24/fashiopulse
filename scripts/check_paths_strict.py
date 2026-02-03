import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

from api.models import Clothing

media_path = os.path.join(os.getcwd(), 'media', 'uploads')
files = set(os.listdir(media_path))

products = Clothing.objects.all()

print("Checking first 10 products DB paths vs filesystem...")
print(f"{'ID':<5} {'DB Path':<40} {'Correct Path':<40} {'Status'}")
print("-" * 100)

for p in products[:10]:
    original_path = p.product_image or ""
    expected_filename = f"product_{p.product_id}.jpg"
    
    # We expect path in DB to be: /media/uploads/product_X.jpg
    expected_db_path = f"/media/uploads/{expected_filename}"
    
    exists_on_disk = expected_filename in files
    
    status = "✅ OK"
    if original_path != expected_db_path:
        status = "❌ Path Mismatch"
    elif not exists_on_disk:
        status = "❌ File Missing"
        
    print(f"{p.product_id:<5} {original_path:<40} {expected_db_path:<40} {status}")
