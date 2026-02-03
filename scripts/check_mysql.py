try:
    import mysql.connector
    print("mysql.connector imported")
except ImportError as e:
    print(f"Error: {e}")
