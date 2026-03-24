import os
import sqlite3
import pandas as pd
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "retail_graph.db")
DATASET_DIR = "D:/Dodge AI/frontend/sap-order-to-cash-dataset/sap-o2c-data"

def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Removed old database.")

def ingest_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                row = json.loads(line.strip())
                for key, val in row.items():
                    if isinstance(val, (dict, list)):
                        row[key] = json.dumps(val)
                data.append(row)
    return pd.DataFrame(data)

def run_ingestion():
    reset_db()
    conn = sqlite3.connect(DB_PATH)
    
    if not os.path.exists(DATASET_DIR):
        print(f"Error: Dataset directory {DATASET_DIR} not found.")
        return

    folders = [f for f in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, f))]
    
    for folder in folders:
        folder_path = os.path.join(DATASET_DIR, folder)
        table_name = folder # use folder name as table name
        
        all_dfs = []
        for file in os.listdir(folder_path):
            if file.endswith(".jsonl"):
                df = ingest_jsonl(os.path.join(folder_path, file))
                all_dfs.append(df)
        
        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            combined_df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"Ingested table: {table_name} with {len(combined_df)} records.")
            
    conn.close()
    print("Database built successfully from SAP Order-to-Cash dataset.")

if __name__ == "__main__":
    run_ingestion()
