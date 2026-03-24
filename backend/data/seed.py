import sqlite3
import pandas as pd
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "retail_graph.db")

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Customers
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT,
        region TEXT
    )""")
    
    # Products
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        product_id TEXT PRIMARY KEY,
        name TEXT,
        category TEXT,
        price REAL
    )""")
    
    # Orders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT,
        product_id TEXT,
        quantity INTEGER,
        order_date TEXT,
        status TEXT,
        FOREIGN KEY(customer_id) REFERENCES Customers(customer_id),
        FOREIGN KEY(product_id) REFERENCES Products(product_id)
    )""")
    
    # Deliveries
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Deliveries (
        delivery_id TEXT PRIMARY KEY,
        order_id TEXT,
        delivery_date TEXT,
        status TEXT,
        FOREIGN KEY(order_id) REFERENCES Orders(order_id)
    )""")
    
    # Invoices
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Invoices (
        invoice_id TEXT PRIMARY KEY,
        delivery_id TEXT,
        amount REAL,
        invoice_date TEXT,
        FOREIGN KEY(delivery_id) REFERENCES Deliveries(delivery_id)
    )""")
    
    # Payments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Payments (
        payment_id TEXT PRIMARY KEY,
        invoice_id TEXT,
        amount REAL,
        payment_date TEXT,
        status TEXT,
        FOREIGN KEY(invoice_id) REFERENCES Invoices(invoice_id)
    )""")
    
    conn.commit()
    conn.close()

def seed_synthetic_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Customers
    customers = [("C001", "Acme Corp", "North"), ("C002", "Globex", "South"), ("C003", "Stark Ind", "East")]
    cursor.executemany("INSERT OR IGNORE INTO Customers VALUES (?,?,?)", customers)
    
    # Products
    products = [("P001", "Widget", "Hardware", 100), ("P002", "Gadget", "Hardware", 150), ("P003", "Software Lic", "Software", 500)]
    cursor.executemany("INSERT OR IGNORE INTO Products VALUES (?,?,?,?)", products)
    
    # Flow
    orders_data = []
    deliveries_data = []
    invoices_data = []
    payments_data = []
    
    for i in range(1, 51):
        order_id = f"O100{i}"
        cust_id = random.choice(customers)[0]
        prod_id = random.choice(products)[0]
        qty = random.randint(1, 10)
        dt = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 30))
        orders_data.append((order_id, cust_id, prod_id, qty, dt.strftime('%Y-%m-%d'), "Completed"))
        
        # 90% chance to have a delivery
        if random.random() < 0.9:
            del_id = f"D200{i}"
            del_dt = dt + timedelta(days=random.randint(1, 5))
            deliveries_data.append((del_id, order_id, del_dt.strftime('%Y-%m-%d'), "Delivered"))
            
            # 85% chance to have an invoice
            if random.random() < 0.85:
                inv_id = f"I300{i}"
                inv_dt = del_dt + timedelta(days=random.randint(1, 3))
                amount = qty * [p for p in products if p[0] == prod_id][0][3]
                invoices_data.append((inv_id, del_id, amount, inv_dt.strftime('%Y-%m-%d')))
                
                # 80% chance for payment
                if random.random() < 0.8:
                    pay_id = f"PAY400{i}"
                    pay_dt = inv_dt + timedelta(days=random.randint(1, 14))
                    payments_data.append((pay_id, inv_id, amount, pay_dt.strftime('%Y-%m-%d'), "Cleared"))

    cursor.executemany("INSERT OR IGNORE INTO Orders VALUES (?,?,?,?,?,?)", orders_data)
    cursor.executemany("INSERT OR IGNORE INTO Deliveries VALUES (?,?,?,?)", deliveries_data)
    cursor.executemany("INSERT OR IGNORE INTO Invoices VALUES (?,?,?,?)", invoices_data)
    cursor.executemany("INSERT OR IGNORE INTO Payments VALUES (?,?,?,?,?)", payments_data)
    
    conn.commit()
    conn.close()
    print("Database seeded successfully.")

if __name__ == "__main__":
    create_tables()
    seed_synthetic_data()
