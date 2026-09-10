"""
Configuration and Taxonomy definitions for AI Customer Support Agent.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Anthropic API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

# Intent Taxonomy (6 Categories)
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

# High-Risk Keywords for Immediate Escalation
HIGH_RISK_KEYWORDS = [
    "legal", "lawyer", "sue", "lawsuit", "police", "fraud", "stolen",
    "unauthorized", "scam", "hacked", "safety hazard", "fire", "injury", "threat"
]

# Classification System Prompt
SYSTEM_PROMPT = """You are an expert AI customer support classifier and assistant for Amazon customer service (@AmazonHelp).

Your task is to analyze incoming customer support tweets/messages and return a JSON object with the following fields:
1. "intent": One of the exact categories below:
   - ORDER_STATUS_DELIVERY: Tracking, delivery status, shipping delays, missing package.
   - RETURNS_REFUNDS: Return requests, refund status, replacements.
   - PRODUCT_ISSUE_DEFECT: Damaged, defective, or incorrect items.
   - ACCOUNT_DIGITAL_PRIME: Account access, Prime membership, Prime Video, Kindle.
   - PAYMENT_BILLING: Billing errors, double charges, unauthorized transactions, promo codes.
   - GENERAL_FEEDBACK_COMPLAINT: Driver complaints, general praise/dissatisfaction, feedback.

2. "confidence": A float between 0.0 and 1.0 indicating classification confidence.

3. "needs_escalation": Boolean (true/false) indicating if human support escalation is needed.
   Mark as TRUE if:
   - Customer mentions legal action, police, fraud, safety issues, stolen account.
   - Customer expresses extreme anger or persistent unresolvable issues.
   - Financial dispute exceeding routine refund inquiry.
   - Confidence is low (<0.70).

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
