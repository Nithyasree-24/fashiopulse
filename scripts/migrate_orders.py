import mysql.connector
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from configs/.env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / 'configs' / '.env')

def migrate():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='2007',
        database='fashiopulse'
    )
    cursor = conn.cursor()
    
    try:
        # Add product_id
        cursor.execute("ALTER TABLE orders ADD COLUMN product_id INT NOT NULL AFTER user_id;")
        print("Added product_id")
    except Exception as e:
        print(f"product_id: {e}")

    try:
        # Add quantity
        cursor.execute("ALTER TABLE orders ADD COLUMN quantity INT NOT NULL DEFAULT 1 AFTER product_id;")
        print("Added quantity")
    except Exception as e:
        print(f"quantity: {e}")

    try:
        # Add payment_method
        cursor.execute("ALTER TABLE orders ADD COLUMN payment_method VARCHAR(50) DEFAULT 'COD' AFTER delivery_address;")
        print("Added payment_method")
    except Exception as e:
        print(f"payment_method: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
