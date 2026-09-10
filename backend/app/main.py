"""
FastAPI Server for Decoupled Backend Architecture.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import os
import sys

# Add parent directory to sys.path so imports work cleanly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import SupportAgent
from app.config import INTENT_TAXONOMY

app = FastAPI(
    title="Hiver AI Support Agent API",
    description="FastAPI Backend for Twitter Customer Support Classification & Escalation (@AmazonHelp)",
    version="2.0.0"
)

# Enable CORS for React frontend (Vite defaults to http://localhost:5173 or port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = SupportAgent()

class ClassifyRequest(BaseModel):
    text: str = Field(..., example="@AmazonHelp Where is my package #112-9988-7711? It was due yesterday!")

class ClassifyResponse(BaseModel):
    text: str
    intent: str
    confidence: float
    needs_escalation: bool
    escalation_reason: str
    priority: str
    suggested_reply: str

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Hiver AI Support Agent FastAPI Backend",
        "target_brand": "@AmazonHelp",
        "version": "2.0.0"
    }

@app.post("/api/classify", response_model=ClassifyResponse)
def classify_message(request: ClassifyRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty.")
    result = agent.process_message(request.text)
    return result

@app.get("/api/intents")
def get_intents():
    return INTENT_TAXONOMY

@app.get("/api/benchmark")
def get_benchmark():
    # Return pre-computed benchmark results
    return {
        "dataset_size": 200,
        "models": [
            {"name": "Baseline 1: Trivial (Majority Class)", "accuracy": 16.5, "macro_f1": 4.72, "esc_f1": 0.0, "reply_score": 4.0},
            {"name": "Baseline 2: Simple (TF-IDF + Rules)", "accuracy": 64.0, "macro_f1": 64.25, "esc_f1": 21.05, "reply_score": 4.75},
            {"name": "Main Model: Claude AI Support Agent", "accuracy": 94.5, "macro_f1": 94.1, "esc_f1": 88.5, "reply_score": 4.86}
        ],
        "judge_alignment": {
            "sample_size": 30,
            "exact_agreement_pct": 86.67,
            "adjacent_agreement_pct": 100.0,
            "cohens_kappa": 0.791
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
