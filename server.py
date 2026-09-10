"""
FastAPI REST Backend for AI Customer Support Agent.
Provides endpoints for classification, evaluation, and system metadata.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from src.agent import SupportAgent
from src.config import INTENT_TAXONOMY
from evaluate import run_comprehensive_evaluation

app = FastAPI(
    title="AI Customer Support Agent API",
    description="FastAPI Backend for Twitter Customer Support Classification & Escalation (@AmazonHelp)",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agent
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
        "service": "AI Customer Support Agent API",
        "target_brand": "@AmazonHelp",
        "version": "1.0.0",
        "endpoints": ["/classify", "/evaluate", "/intents"]
    }

@app.post("/classify", response_model=ClassifyResponse)
def classify_message(request: ClassifyRequest):
    """Classifies an incoming customer support message."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty.")
    
    result = agent.process_message(request.text)
    return result

@app.get("/evaluate")
def get_evaluation():
    """Runs and returns comprehensive benchmark evaluation metrics."""
    return run_comprehensive_evaluation()

@app.get("/intents")
def get_intents():
    """Returns the 6-class intent taxonomy metadata."""
    return INTENT_TAXONOMY

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
