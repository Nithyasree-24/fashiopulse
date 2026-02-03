import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

from api.models import Clothing

# Check specific products from the screenshot
# Products: Charcoal Motivational, Black Racing, Long Sleeve, Smocked, Scoop Neck, Sleeveless
product_names = [
    "Charcoal Motivational",
    "Black Racing",
    "Long Sleeve",
    "Smocked",
    "Scoop Neck",
    "Sleeveless"
]

print("Checking products from screenshot:\n")

for name_part in product_names:
    products = Clothing.objects.filter(product_name__icontains=name_part)[:1]
    if products:
        p = products[0]
        print(f"\n{p.product_name[:50]}")
        print(f"  ID: {p.product_id}")
        print(f"  DB Path: {p.product_image}")
        
        if p.product_image:
            filename = p.product_image.replace('/media/uploads/', '')
            full_path = os.path.join(os.getcwd(), 'media', 'uploads', filename)
            exists = os.path.exists(full_path)
            print(f"  File exists: {exists}")
            if not exists:
                print(f"  Expected: {filename}")
