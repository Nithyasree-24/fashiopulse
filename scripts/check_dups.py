import os
import django
from collections import Counter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

from api.models import Clothing

products = Clothing.objects.all()
images = [p.product_image for p in products]
counts = Counter(images)

for img, count in counts.most_common(5):
    print(f"Count: {count} | URL: {img[:100]}...")
