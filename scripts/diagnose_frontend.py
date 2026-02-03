import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

from api.models import Clothing

media_path = os.path.join(os.getcwd(), 'media', 'uploads')

# Get first 10 products to match what's shown in the frontend
products = Clothing.objects.all()[:10]

print("Checking first 10 products (what you see in the frontend):\n")
print("=" * 80)

for p in products:
    status = "❌"
    issue = ""
    
    if not p.product_image:
        issue = "No path in database"
    elif not p.product_image.startswith('/media/uploads/'):
        issue = f"Wrong format: {p.product_image}"
    else:
        filename = p.product_image.replace('/media/uploads/', '')
        full_path = os.path.join(media_path, filename)
        
        if os.path.exists(full_path):
            status = "✅"
            issue = "OK"
        else:
            issue = f"File not found: {filename}"
    
    print(f"{status} ID {p.product_id} | {p.product_name[:40]:40} | {issue}")

print("\n" + "=" * 80)
print("\nAvailable image files in media/uploads (first 20):")
files = sorted(os.listdir(media_path))[:20]
for f in files:
    print(f"  - {f}")
