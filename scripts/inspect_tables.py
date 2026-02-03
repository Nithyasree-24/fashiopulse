import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashiopulse_backend.settings')
django.setup()

with open('db_info.txt', 'w', encoding='utf-8') as f:
    with connection.cursor() as cursor:
        cursor.execute("DESCRIBE orders")
        columns = cursor.fetchall()
        f.write("Orders columns:\n")
        for col in columns:
            f.write(str(col) + "\n")

        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        f.write("\nUsers columns:\n")
        for col in columns:
            f.write(str(col) + "\n")
