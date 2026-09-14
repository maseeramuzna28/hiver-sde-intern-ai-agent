"""
Configuration and Taxonomy definitions for AI Customer Support Agent Backend.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY      = os.getenv("GROQ_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
API_PROVIDER      = "groq" if GROQ_API_KEY else ("anthropic" if ANTHROPIC_API_KEY else "heuristic")
GROQ_MODEL        = os.getenv("GROQ_MODEL", os.getenv("CLAUDE_MODEL", "llama-3.3-70b-versatile"))
ANTHROPIC_MODEL   = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
DEFAULT_MODEL     = GROQ_MODEL if API_PROVIDER == "groq" else ANTHROPIC_MODEL

INTENT_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "ORDER_STATUS_DELIVERY": {
        "description": "Questions about order status, tracking numbers, shipping delays, estimated delivery, or missing packages.",
        "examples": ["Where is my package?", "Track order #12345", "Delivery was supposed to arrive yesterday"],
        "requires_escalation_default": False
    },
    "RETURNS_REFUNDS": {
        "description": "Requests for returning an item, refund status, replacement items, or return policy details.",
        "examples": ["I want to return this dress", "When will my refund process?", "Can I get a replacement?"],
        "requires_escalation_default": False
    },
    "PRODUCT_ISSUE_DEFECT": {
        "description": "Reports of damaged goods, defective hardware, incorrect items delivered, or broken packaging.",
        "examples": ["My order arrived broken", "You sent the wrong size", "The item does not work at all"],
        "requires_escalation_default": False
    },
    "ACCOUNT_DIGITAL_PRIME": {
        "description": "Issues related to Amazon Prime membership, account login, passwords, Kindle, Prime Video, or digital services.",
        "examples": ["Unable to log in", "Cancel my Prime membership", "Prime Video isn't loading"],
        "requires_escalation_default": False
    },
    "PAYMENT_BILLING": {
        "description": "Questions or disputes regarding charges, unauthorized billing, promo codes, gift card issues, or double charges.",
        "examples": ["I was charged twice", "My promo code isn't working", "Unauthorized charge on my credit card"],
        "requires_escalation_default": True
    },
    "GENERAL_FEEDBACK_COMPLAINT": {
        "description": "General dissatisfaction, complaints about service quality, driver behavior, praise, or general queries.",
        "examples": ["Driver threw my package", "Great customer service", "Terrible experience today"],
        "requires_escalation_default": False
    }
}

HIGH_RISK_KEYWORDS = [
    "legal", "lawyer", "sue", "lawsuit", "police", "fraud", "stolen",
    "unauthorized", "scam", "hacked", "safety hazard", "fire", "injury", "threat"
]

SYSTEM_PROMPT = """You are an expert AI customer support classifier and assistant for Amazon customer service (@AmazonHelp).

Your task is to analyze incoming customer support tweets/messages and return a JSON object with the following fields:
1. "intent": One of the exact categories: ORDER_STATUS_DELIVERY, RETURNS_REFUNDS, PRODUCT_ISSUE_DEFECT, ACCOUNT_DIGITAL_PRIME, PAYMENT_BILLING, GENERAL_FEEDBACK_COMPLAINT.
2. "confidence": A float between 0.0 and 1.0.
3. "needs_escalation": Boolean (true/false).
4. "escalation_reason": String explaining why escalation is or is not needed.
5. "suggested_reply": A professional, empathetic response following Amazon Support guidelines (max 280 chars, friendly tone, asks for DM with order details if needed).

Output ONLY valid JSON matching this schema:
{
  "intent": "<INTENT_CATEGORY>",
  "confidence": <FLOAT>,
  "needs_escalation": <BOOLEAN>,
  "escalation_reason": "<STRING>",
  "suggested_reply": "<STRING>"
}
"""
