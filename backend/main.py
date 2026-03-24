from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load env variables FIRST before importing any modules that depend on them
load_dotenv()

from core.graph_builder import graph_builder
from core.llm_engine import generate_natural_language_response

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
    # Retrieve the constructed graph representations
    return graph_builder.get_graph_data()

@app.post("/query")
def submit_query(request: QueryRequest):
    # Process through the LLM engine for natural language text-to-sql output
    result = generate_natural_language_response(request.question)
    return result
