"""
Baseline classifiers for benchmark comparison.
Baseline 1: Trivial Baseline (Majority Class Predictor)
Baseline 2: Simple Baseline (TF-IDF + Heuristic Classifier)
"""
from typing import Dict, Any, List
import re
from sklearn.feature_extraction.text import TfidfVectorizer

class TrivialBaseline:
    """Trivial Baseline: Predicts majority class (ORDER_STATUS_DELIVERY) and no escalation."""

    def predict(self, text: str) -> Dict[str, Any]:
        return {
            "intent": "ORDER_STATUS_DELIVERY",
            "confidence": 0.50,
            "needs_escalation": False,
            "escalation_reason": "Trivial baseline default prediction",
            "suggested_reply": "Thanks for contacting support!"
        }

class SimpleTFIDFBaseline:
    """Simple Baseline: TF-IDF feature keyword matcher + simple escalation rule."""

    def __init__(self):
        self.intent_keywords = {
            "ORDER_STATUS_DELIVERY": ["where", "track", "delivery", "shipping", "shipped", "carrier", "delay", "package", "arrived", "out for delivery"],
            "RETURNS_REFUNDS": ["return", "refund", "replacement", "exchange", "money back", "label", "ups", "kohl"],
            "PRODUCT_ISSUE_DEFECT": ["broken", "damaged", "defective", "wrong", "shattered", "missing", "leaked", "cracked", "melted"],
            "ACCOUNT_DIGITAL_PRIME": ["prime", "video", "kindle", "login", "password", "account", "subscription", "sign in", "app"],
            "PAYMENT_BILLING": ["charge", "billed", "payment", "card", "promo", "discount", "double charge", "unauthorized", "cost", "invoice"],
            "GENERAL_FEEDBACK_COMPLAINT": ["driver", "worst", "terrible", "bad", "rude", "complaint", "shoutout", "thanks", "great", "chat"]
        }

    def predict(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        
        # Keyword counting
        scores = {intent: 0 for intent in self.intent_keywords}
        for intent, kw_list in self.intent_keywords.items():
            for kw in kw_list:
                if kw in text_lower:
                    scores[intent] += 1

        best_intent = max(scores, key=scores.get)
        if scores[best_intent] == 0:
            best_intent = "GENERAL_FEEDBACK_COMPLAINT"

        # Simple Escalation Rule
        needs_escalation = False
        if any(w in text_lower for w in ["unauthorized", "legal", "lawsuit", "police", "fraud", "stolen", "charged twice", "hazard", "melted"]):
            needs_escalation = True

        return {
            "intent": best_intent,
            "confidence": 0.75,
            "needs_escalation": needs_escalation,
            "escalation_reason": "Simple baseline keyword match",
            "suggested_reply": f"We can help with your {best_intent.lower().replace('_', ' ')}. Please DM us your details."
        }
