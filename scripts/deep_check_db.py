import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

from api.models import Clothing

print("--- SAMPLE DATA (FIRST 50) ---")
products = Clothing.objects.all().order_by('product_id')[:50]
for p in products:
    # Use repr to see exact strings
    print(f"ID: {p.product_id} | Name: {p.product_name[:40]} | Image: {p.product_image}")

print("\n--- SEARCHING FOR UNIQUE IMAGES FOR SCREENSHOT PRODUCTS ---")
names_to_check = [
    "Ribbed Halter Mini Dress",
    "Space-Dye Knit Mini Dress",
    "Floral Tiered Maxi Dress",
    "Cold-Shoulder Boho Ruffle Dress"
]

for name in names_to_check:
    matches = Clothing.objects.filter(product_name__icontains=name)
    print(f"\nChecking: {name} ({matches.count()} matches)")
    for m in matches:
        print(f"  ID: {m.product_id} | Exact Name: {m.product_name} | Image: {m.product_image}")

print("\n--- STATS ---")
total = Clothing.objects.count()
unique_images = Clothing.objects.values('product_image').distinct().count()
print(f"Total Products: {total}")
print(f"Unique Images: {unique_images}")
