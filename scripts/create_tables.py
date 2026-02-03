import mysql.connector
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / 'configs' / '.env')

# Database connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2007',  # From settings.py
    'database': 'fashiopulse'
}

# SQL statements
sql_statements = [
    "DROP TABLE IF EXISTS cart;",
    "DROP TABLE IF EXISTS wishlist;",
    """
    CREATE TABLE cart (
        cart_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT DEFAULT 1,
        size VARCHAR(10),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES clothing(product_id) ON DELETE CASCADE,
        UNIQUE KEY unique_user_product_size (user_id, product_id, size)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    """
    CREATE TABLE wishlist (
        wishlist_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        product_id INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES clothing(product_id) ON DELETE CASCADE,
        UNIQUE KEY unique_user_product (user_id, product_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
]

try:
    # Connect to database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    print("Connected to database successfully!")
    
    # Execute each SQL statement
    for sql in sql_statements:
        cursor.execute(sql)
        print(f"Executed: {sql[:50]}...")
    
    conn.commit()
    print("\n✅ Cart and Wishlist tables created successfully!")
    
    # Verify tables
    cursor.execute("SHOW TABLES LIKE 'cart'")
    if cursor.fetchone():
        print("✅ Cart table exists")
        cursor.execute("DESCRIBE cart")
        print("\nCart table structure:")
        for row in cursor.fetchall():
            print(f"  {row}")
    
    cursor.execute("SHOW TABLES LIKE 'wishlist'")
    if cursor.fetchone():
        print("\n✅ Wishlist table exists")
        cursor.execute("DESCRIBE wishlist")
        print("\nWishlist table structure:")
        for row in cursor.fetchall():
            print(f"  {row}")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"❌ Error: {err}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
