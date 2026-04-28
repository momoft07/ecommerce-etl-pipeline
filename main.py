import sqlite3
import pandas as pd
import logging
from datetime import datetime

# logging steup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===============================================================================================
# 1. DATABASE ERSTELLEN
# ===============================================================================================
logger.info("creating SQLite database...")
conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# ===============================================================================================
# 2. TABELLEN ERSTELLEN
# ===============================================================================================
logger.info("creating tables...")

# Tabelle 1 : customers
cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            country TEXT
        )
''')

# Tabelle 2 : products
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            PRICE REAL
            )
''')

# Tabelle 3 : orders
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY, 
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)  
        )
''')

conn.commit()
logger.info("database with tabelles created successfully.")

# ===============================================================================================
# 3. INSERT sample DATA
# ===============================================================================================
logger.info("inserting sample data")

# Insert customers
customers = [
    (1, 'John Doe', 'john@example.com', 'USA'),
    (2, 'Jane Smith', 'jane@example.com', 'UK'),
    (3, 'Bob Johnson', 'bob@example.com', 'Germany'),
    (4, 'Alice Williams', 'alice@example.com', 'Finnland'),
    (5, 'Charlie Brown', 'charlie@example.com', 'Sweden')
]

cursor.executemany('''
        INSERT INTO customers VALUES (?, ?, ?, ?)
''', customers)

# Insert products
products = [
    (1, 'Laptop', 999.99),
    (2, 'Mouse', 23.99),
    (3, 'Keyboard', 19.99),
    (4, 'Monitor', 199.99),
    (5, 'Headphones', 49.99)
]

cursor.executemany('''
        INSERT INTO products VALUES (?, ?, ?)
''', products)

# Insert orders
orders = [
    (1, 1, 1, 1),
    (2, 1, 2, 2),
    (3, 2, 1, 1),
    (4, 3, 3, 1),
    (5, 4, 4, 2),
    (6, 5, 5, 1),
    (7, 5, 1, 1),
    (8, 2, 2, 1),
    (9, 3, 4, 1),
    (10, 4, 5, 1)
]

cursor.executemany('''
        INSERT INTO orders VALUES (?, ?, ?, ?)
''', orders)

# conn.commit, um die daten in ecommerce.database zu speichern
conn.commit()
logger.info(" Sample data inserted!")

# conn.close, um die verbindung zu schließen
conn.close()

# ===============================================================================================
# 3.1 Extract + JOIN + AGGREGATION
# ===============================================================================================
logger.info("loading data with joins and aggregations")

conn = sqlite3.connect('ecommerce.db')

query = '''
    SELECT 
        c.name,
        SUM(o.quantity * p.price) as total_spent,
        Count(o.order_id) as num_orders
    FROM orders o
        JOIN customers c ON o.Customer_id = c.Customer_id
        JOIN products p ON o.product_id = p.product_id
    GROUP BY c.name
    ORDER BY total_spent DESC
        '''

df = pd.read_sql_query(query, conn)

logger.info(f"Aggregated{len(df)} customers")
logger.info("\nCustomer spending :\n")
logger.info(df.to_string())

conn.close()

# ===============================================================================================
# 3.2 "Welche Produkte werden am meisten gekauft? Und wie viel Geld bringen sie?"
# ===============================================================================================
conn = sqlite3.connect('ecommerce.db')
logger.info("loading data...")

query = '''
    SELECT
        p.product_name,
        SUM(o.quantity) as total_quantity_sold,
        SUM(o.quantity * p.price) as total_revenue,
        COUNT(DISTINCT o.customer_id) as num_customers
    FROM orders o                                           
        JOIN products p ON o.product_id = p.product_id    
        JOIN customers c ON o.customer_id = c.customer_id    
    GROUP BY p.product_name
    ORDER BY total_revenue DESC
'''

df = pd.read_sql_query(query, conn)

logger.info(f"Aggregated {len(df)} products")
logger.info("\nProduct sales :")
logger.info(df.to_string())

conn.close()
