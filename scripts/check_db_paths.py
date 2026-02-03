import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

from api.models import Clothing

# Check the first 20 products to see their exact database paths
products = Clothing.objects.all()[:20]

print("First 20 products - Database paths:\n")
print("=" * 100)

for p in products:
    path_status = "❌ NULL" if not p.product_image else ("✅" if p.product_image.startswith('/media/uploads/') else "⚠️ WRONG")
    print(f"{path_status} | ID {p.product_id:3} | {p.product_name[:35]:35} | {p.product_image or 'NULL'}")

print("\n" + "=" * 100)

# Count how many have NULL or wrong paths
null_count = Clothing.objects.filter(product_image__isnull=True).count()
empty_count = Clothing.objects.filter(product_image='').count()
total = Clothing.objects.count()

print(f"\nStatistics:")
print(f"  Total products: {total}")
print(f"  NULL paths: {null_count}")
print(f"  Empty paths: {empty_count}")
print(f"  Should have paths: {total - null_count - empty_count}")
