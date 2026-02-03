import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

from api.models import Clothing

# Fix any paths with /media/upload/ (singular) to /media/uploads/ (plural)
products = Clothing.objects.all()
fixed = 0

for p in products:
    if p.product_image and '/media/upload/' in p.product_image and '/media/uploads/' not in p.product_image:
        # Fix the typo
        p.product_image = p.product_image.replace('/media/upload/', '/media/uploads/')
        p.save()
        fixed += 1
        print(f"Fixed product {p.product_id}: {p.product_image}")

print(f"\n✅ Fixed {fixed} products with typo in path")
