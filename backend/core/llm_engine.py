import os
import sqlite3
import json
import re
from dotenv import load_dotenv
from groq import Groq

# Load environment variables specific to this execution frame
load_dotenv()

# Initialize dynamically to ensure it picks up the true API key after dotenv runs
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "retail_graph.db")

SCHEMA_INFO = """
Table: Customers (customer_id, name, region)
Table: Products (product_id, name, category, price)
Table: Orders (order_id, customer_id, product_id, quantity, order_date, status)
Table: Deliveries (delivery_id, order_id, delivery_date, status)
Table: Invoices (invoice_id, delivery_id, amount, invoice_date)
Table: Payments (payment_id, invoice_id, amount, payment_date, status)

Note on relationships: 
- An order contains a product_id.
- A delivery links to an order_id. 
- An invoice links to a delivery_id.
To find products connected to invoices, you MUST join Products -> Orders -> Deliveries -> Invoices sequentially.
"""

def is_domain_relevant(question: str) -> bool:
    domain_keywords = ['order', 'delivery', 'invoice', 'payment', 'customer', 'product', 'cash', 'billing', 'flow', 'trace']
    q_lower = question.lower()
    return any(keyword in q_lower for keyword in domain_keywords)

def execute_sql(query: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description] if cursor.description else []
        conn.close()
        return {"columns": columns, "rows": rows}
    except Exception as e:
        return {"error": str(e)}

def extract_node_ids(db_results: dict):
    # Extract IDs to highlight on the frontend
    ids = []
    if "rows" in db_results and "columns" in db_results:
        id_cols = [i for i, col in enumerate(db_results["columns"]) if col.endswith("_id")]
        for row in db_results["rows"]:
            for col_idx in id_cols:
                if row[col_idx]:
                    ids.append(str(row[col_idx]))
    return list(set(ids))

def generate_natural_language_response(question: str):
    if not is_domain_relevant(question):
        return {
            "answer": "This system is designed to answer questions related to the provided Order-to-Cash dataset only.",
            "data": []
        }
    
    # 1: Text to SQL
    client = Groq(api_key=os.environ.get("GROQ_API_KEY", "placeholder"))
    
    sql_prompt = f"""
    You are an expert SQL generator. Convert the user's question into a SQLite query.
    Schema:
    {SCHEMA_INFO}
    
    Output ONLY valid SQL, no markdown formatting or explanation. 
    Question: {question}
    """
    
    try:
        sql_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": sql_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0
        )
        sql_query = sql_completion.choices[0].message.content.strip()
        sql_query = re.sub(r'```sql', '', sql_query).replace('```', '').strip()
        
        print(f"DEBUG SQL GENERATED: {sql_query}")

        # 2: Execute SQL
        db_results = execute_sql(sql_query)
        
        if "error" in db_results:
            return {"answer": f"Could not compute data: {db_results['error']}", "data": []}
            
        highlight_nodes = extract_node_ids(db_results)
        
        # 3: Data to Text
        answer_prompt = f"""
        You are a data assistant for an Order-to-Cash graph system.
        User Question: {question}
        SQL Used: {sql_query}
        DB Results: {json.dumps(db_results)}
        
        Generate a concise, natural language answer summarizing the DB Results. 
        """
        answer_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": answer_prompt}],
            model="llama-3.1-8b-instant",
        )
        final_answer = answer_completion.choices[0].message.content
        
        return {
            "answer": final_answer,
            "data": highlight_nodes
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "answer": f"Error connecting to LLM or executing query. Details: {str(e)}",
            "data": []
        }
