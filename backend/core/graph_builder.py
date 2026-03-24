import networkx as nx
import pandas as pd
import json

class GraphBuilder:
    def __init__(self):
        self.G = nx.DiGraph()
    
    def load_data(self):
        # We will load the dataset here. For the prototype, we create sample order-to-cash data nodes.
        # In a real environment, you'd parse business domain CSV or SQL tables into these edges.
        
        # Sample entities
        self.G.add_node("C1", type="Customer", name="Alice")
        self.G.add_node("O1", type="Order", total=500, status="completed")
        self.G.add_node("D1", type="Delivery", date="2025-01-01")
        self.G.add_node("I1", type="Invoice", amount=500, date="2025-01-02")
        self.G.add_node("P1", type="Payment", amount=500, date="2025-01-03")
        
        # Adding edges (relationships)
        self.G.add_edge("C1", "O1", relationship="PLACED_ORDER")
        self.G.add_edge("O1", "D1", relationship="HAS_DELIVERY")
        self.G.add_edge("D1", "I1", relationship="GENERATED_INVOICE")
        self.G.add_edge("I1", "P1", relationship="HAS_PAYMENT")

    def get_graph_data(self):
        nodes = []
        for n, data in self.G.nodes(data=True):
            nodes.append({"id": n, "label": data.get('type', 'Unknown'), **data})
            
        edges = []
        for u, v, data in self.G.edges(data=True):
            edges.append({"source": u, "target": v, "label": data.get('relationship', 'RELATES_TO')})
            
        return {"nodes": nodes, "links": edges}

graph_builder = GraphBuilder()
graph_builder.load_data()
