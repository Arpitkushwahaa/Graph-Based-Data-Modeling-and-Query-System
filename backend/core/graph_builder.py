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
            customers = pd.read_sql("SELECT businessPartner as customer_id, businessPartnerName as name FROM business_partners", conn)
            products = pd.read_sql("SELECT product as product_id, productType as category FROM products", conn)
            orders = pd.read_sql("SELECT salesOrder as order_id, soldToParty as customer_id, totalNetAmount as amount, creationDate as order_date FROM sales_order_headers LIMIT 500", conn)
            order_items = pd.read_sql("SELECT salesOrder as order_id, material as product_id, netAmount FROM sales_order_items LIMIT 1000", conn)
            deliveries = pd.read_sql("SELECT deliveryDocument as delivery_id, creationDate as delivery_date FROM outbound_delivery_headers LIMIT 500", conn)
            delivery_items = pd.read_sql("SELECT deliveryDocument as delivery_id, referenceSdDocument as order_id FROM outbound_delivery_items LIMIT 1000", conn)
            invoices = pd.read_sql("SELECT billingDocument as invoice_id, totalNetAmount as amount, creationDate as invoice_date FROM billing_document_headers LIMIT 500", conn)
            invoice_items = pd.read_sql("SELECT billingDocument as invoice_id, referenceSdDocument as order_id FROM billing_document_items LIMIT 1000", conn)
        except Exception as e:
            conn.close()
            print("Error loading data:", e)
            return

        conn.close()

        # Add Nodes
        for _, row in customers.iterrows():
            if pd.notna(row['customer_id']):
                self.G.add_node(str(row['customer_id']), type="Customer", Entity="Customer", Name=row['name'])
                
        for _, row in products.iterrows():
            if pd.notna(row['product_id']):
                self.G.add_node(str(row['product_id']), type="Product", Entity="Product", Category=row['category'])

        for _, row in orders.iterrows():
            if pd.notna(row['order_id']):
                self.G.add_node(str(row['order_id']), type="Order", Entity="Order", Amount=row.get('amount'), Date=row.get('order_date'))
                if pd.notna(row['customer_id']):
                    self.G.add_edge(str(row['customer_id']), str(row['order_id']), relationship="PLACED_ORDER")

        for _, row in order_items.iterrows():
            if pd.notna(row['order_id']) and pd.notna(row['product_id']):
                self.G.add_edge(str(row['order_id']), str(row['product_id']), relationship="ORDERED_PRODUCT")

        for _, row in deliveries.iterrows():
            if pd.notna(row['delivery_id']):
                self.G.add_node(str(row['delivery_id']), type="Delivery", Entity="Delivery", Date=row.get('delivery_date'))
        
        for _, row in delivery_items.iterrows():
            if pd.notna(row['delivery_id']) and pd.notna(row['order_id']):
                self.G.add_edge(str(row['order_id']), str(row['delivery_id']), relationship="HAS_DELIVERY")

        for _, row in invoices.iterrows():
            if pd.notna(row['invoice_id']):
                self.G.add_node(str(row['invoice_id']), type="Invoice", Entity="Invoice", Amount=row.get('amount'), Date=row.get('invoice_date'))
                
        for _, row in invoice_items.iterrows():
            if pd.notna(row['invoice_id']) and pd.notna(row['order_id']):
                self.G.add_edge(str(row['order_id']), str(row['invoice_id']), relationship="GENERATED_INVOICE")

    def get_graph_data(self):
        self.load_data()
        nodes = []
        for n, data in self.G.nodes(data=True):
            connections = len(list(self.G.successors(n))) + len(list(self.G.predecessors(n)))
            nodes.append({"id": n, "label": data.get('type', 'Unknown'), "Connections": connections, **data})

        edges = []
        for u, v, data in self.G.edges(data=True):
            edges.append({"source": u, "target": v, "label": data.get('relationship', 'RELATES_TO')})

        return {"nodes": nodes, "links": edges}

graph_builder = GraphBuilder()
