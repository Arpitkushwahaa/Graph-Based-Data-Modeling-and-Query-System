import networkx as nx
import pandas as pd
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "retail_graph.db")

class GraphBuilder:
    def __init__(self):
        self.G = nx.DiGraph()
    
    def load_data(self):
        self.G.clear()
        if not os.path.exists(DB_PATH):
            return

        conn = sqlite3.connect(DB_PATH)
        
        # Load tables
        try:
            customers = pd.read_sql("SELECT * FROM Customers", conn)
            products = pd.read_sql("SELECT * FROM Products", conn)
            orders = pd.read_sql("SELECT * FROM Orders", conn)
            deliveries = pd.read_sql("SELECT * FROM Deliveries", conn)
            invoices = pd.read_sql("SELECT * FROM Invoices", conn)
            payments = pd.read_sql("SELECT * FROM Payments", conn)
        except Exception as e:
            conn.close()
            return
            
        conn.close()

        # Add Nodes
        for _, row in customers.iterrows():
            self.G.add_node(row['customer_id'], type="Customer", Entity="Customer", Name=row['name'], Region=row['region'])
            
        for _, row in products.iterrows():
            self.G.add_node(row['product_id'], type="Product", Entity="Product", Name=row['name'], Category=row['category'], Price=row['price'])
            
        for _, row in orders.iterrows():
            self.G.add_node(row['order_id'], type="Order", Entity="Order", Quantity=row['quantity'], Date=row['order_date'], Status=row['status'])
            self.G.add_edge(row['customer_id'], row['order_id'], relationship="PLACED_ORDER")
            self.G.add_edge(row['order_id'], row['product_id'], relationship="ORDERED_PRODUCT")
            
        for _, row in deliveries.iterrows():
            self.G.add_node(row['delivery_id'], type="Delivery", Entity="Delivery", Date=row['delivery_date'], Status=row['status'])
            self.G.add_edge(row['order_id'], row['delivery_id'], relationship="HAS_DELIVERY")
            
        for _, row in invoices.iterrows():
            self.G.add_node(row['invoice_id'], type="Invoice", Entity="Invoice", Amount=row['amount'], Date=row['invoice_date'])
            self.G.add_edge(row['delivery_id'], row['invoice_id'], relationship="GENERATED_INVOICE")
            
        for _, row in payments.iterrows():
            self.G.add_node(row['payment_id'], type="Payment", Entity="Payment", Amount=row['amount'], Date=row['payment_date'], Status=row['status'])
            self.G.add_edge(row['invoice_id'], row['payment_id'], relationship="HAS_PAYMENT")

    def get_graph_data(self):
        self.load_data()
        nodes = []
        for n, data in self.G.nodes(data=True):
            # Calculate connections count
            connections = len(list(self.G.successors(n))) + len(list(self.G.predecessors(n)))
            nodes.append({"id": n, "label": data.get('type', 'Unknown'), "Connections": connections, **data})
            
        edges = []
        for u, v, data in self.G.edges(data=True):
            edges.append({"source": u, "target": v, "label": data.get('relationship', 'RELATES_TO')})
            
        return {"nodes": nodes, "links": edges}

graph_builder = GraphBuilder()

