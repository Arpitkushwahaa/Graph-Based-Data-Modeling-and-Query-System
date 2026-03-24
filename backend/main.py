from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Graph Data Modeling System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Graph Query API running"}

@app.get("/graph")
def get_graph(node_id: str = None):
    # Stub for returning the graph nodes & edges
    return {"nodes": [], "edges": []}

@app.post("/query")
def submit_query(request: QueryRequest):
    # Stub for natural language query engine
    return {
        "answer": "This is a placeholder answer.",
        "data": []
    }
