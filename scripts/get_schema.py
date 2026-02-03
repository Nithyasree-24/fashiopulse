import os
import django
from django.core.management import call_command
import io

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

with open('full_schema.txt', 'w') as f:
    call_command('inspectdb', 'users', 'clothing', stdout=f)
