import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

from api.models import Clothing

names_to_check = [
    "Ribbed Halter Mini Dress",
    "Space-Dye Knit Mini Dress",
    "Floral Tiered Maxi Dress",
    "Cold-Shoulder Boho Ruffle Dress"
]

for name in names_to_check:
    p = Clothing.objects.filter(product_name=name).first()
    if p:
        print(f"{p.product_id} | {p.product_name} | URL: {p.product_image}")
