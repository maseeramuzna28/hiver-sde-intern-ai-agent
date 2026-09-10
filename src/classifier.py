"""
Classifier module using Claude API with structured JSON output and robust fallback.
"""
import json
import logging
import re
from typing import Dict, Any, Optional
import anthropic

from .config import (
    ANTHROPIC_API_KEY,
    DEFAULT_MODEL,
    SYSTEM_PROMPT,
    INTENT_TAXONOMY,
    HIGH_RISK_KEYWORDS
)

logger = logging.getLogger(__name__)

class ClaudeClassifier:
    """Classifies customer support messages using Claude API or heuristic fallback."""

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None

    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classifies a customer message.
        
        Returns:
            Dict containing: intent, confidence, needs_escalation, escalation_reason, suggested_reply
        """
        if not text or not text.strip():
            return {
                "intent": "GENERAL_FEEDBACK_COMPLAINT",
                "confidence": 0.5,
                "needs_escalation": False,
                "escalation_reason": "Empty or whitespace message",
                "suggested_reply": "Hello! How can we assist you with your Amazon order today?"
            }

        # Try Claude API first if client is initialized
        if self.client:
            try:
                return self._classify_with_claude(text)
            except anthropic.APIConnectionError as e:
                logger.warning(f"Claude API Connection Error: {e}. Falling back to heuristic classifier.")
            except anthropic.RateLimitError as e:
                logger.warning(f"Claude API Rate Limit Error: {e}. Falling back to heuristic classifier.")
            except anthropic.APIError as e:
                logger.warning(f"Claude API Error: {e}. Falling back to heuristic classifier.")
            except Exception as e:
                logger.warning(f"Unexpected error in Claude API call: {e}. Falling back to heuristic classifier.")

        # Fallback to heuristic classification if API is unavailable
        return self._heuristic_classify(text)

    def _classify_with_claude(self, text: str) -> Dict[str, Any]:
        """Calls Claude API for structured classification."""
        prompt = f"Customer Tweet: \"{text}\"\n\nClassify this message and generate a structured JSON response."
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text.strip()
        
        # Extract JSON from code block if wrapped
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        parsed = json.loads(content)

        # Validate required fields
        intent = parsed.get("intent", "GENERAL_FEEDBACK_COMPLAINT")
        if intent not in INTENT_TAXONOMY:
            intent = "GENERAL_FEEDBACK_COMPLAINT"

        return {
            "intent": intent,
            "confidence": float(parsed.get("confidence", 0.90)),
            "needs_escalation": bool(parsed.get("needs_escalation", False)),
            "escalation_reason": str(parsed.get("escalation_reason", "")),
            "suggested_reply": str(parsed.get("suggested_reply", ""))
        }

    def _heuristic_classify(self, text: str) -> Dict[str, Any]:
        """Rule-based heuristic classifier for offline / fallback usage."""
        text_lower = text.lower()

        # Check high risk escalation
        high_risk_found = [kw for kw in HIGH_RISK_KEYWORDS if kw in text_lower]
        needs_escalation = len(high_risk_found) > 0
        escalation_reason = f"Contains high risk keywords: {', '.join(high_risk_found)}" if high_risk_found else ""

        # Keyword matching rules
        scores = {intent: 0 for intent in INTENT_TAXONOMY}

        # ORDER_STATUS_DELIVERY
        if any(w in text_lower for w in ["where is", "track", "delivery", "delivered", "shipping", "shipped", "carrier", "delay", "arriving", "package", "where's my"]):
            scores["ORDER_STATUS_DELIVERY"] += 3

        # RETURNS_REFUNDS
        if any(w in text_lower for w in ["return", "refund", "replace", "exchange", "money back", "send back"]):
            scores["RETURNS_REFUNDS"] += 3

        # PRODUCT_ISSUE_DEFECT
        if any(w in text_lower for w in ["broken", "damaged", "defective", "wrong item", "faulty", "not working", "destroyed", "missing item"]):
            scores["PRODUCT_ISSUE_DEFECT"] += 3

        # ACCOUNT_DIGITAL_PRIME
        if any(w in text_lower for w in ["prime", "video", "kindle", "login", "password", "account", "sign in", "subscription"]):
            scores["ACCOUNT_DIGITAL_PRIME"] += 3

        # PAYMENT_BILLING
        if any(w in text_lower for w in ["charge", "billed", "payment", "card", "promo", "discount", "double charge", "unauthorized", "cost"]):
            scores["PAYMENT_BILLING"] += 3

        # GENERAL_FEEDBACK_COMPLAINT
        if any(w in text_lower for w in ["driver", "worst", "terrible", "bad service", "thanks", "great", "complaint", "rude"]):
            scores["GENERAL_FEEDBACK_COMPLAINT"] += 2

        # Best matching intent
        best_intent = max(scores, key=scores.get)
        max_score = scores[best_intent]

        if max_score == 0:
            best_intent = "GENERAL_FEEDBACK_COMPLAINT"
            confidence = 0.65
        else:
            confidence = min(0.70 + (max_score * 0.08), 0.95)

        # Escalation based on intent defaults & confidence
        if INTENT_TAXONOMY[best_intent]["requires_escalation_default"] or confidence < 0.70:
            needs_escalation = True
            if not escalation_reason:
                escalation_reason = f"Low confidence score ({confidence:.2f}) or billing category requiring supervisor review."

        # Default fallback reply generator
        reply = self._generate_fallback_reply(best_intent)

        return {
            "intent": best_intent,
            "confidence": confidence,
            "needs_escalation": needs_escalation,
            "escalation_reason": escalation_reason,
            "suggested_reply": reply
        }

    def _generate_fallback_reply(self, intent: str) -> str:
        """Generates template response for fallback classification."""
        templates = {
            "ORDER_STATUS_DELIVERY": "We'd love to look into your delivery status! Please send us a DM with your order ID so we can assist you right away. - Alex",
            "RETURNS_REFUNDS": "Sorry to hear you need a return/refund! Please DM us your order number and email address so we can get this sorted for you. - Sam",
            "PRODUCT_ISSUE_DEFECT": "We apologize for the inconvenience with your item! Please send us a direct message with your order details so we can arrange a replacement. - Taylor",
            "ACCOUNT_DIGITAL_PRIME": "We're here to help with your Amazon account/Prime service! Please DM us your account email so our technical team can assist. - Morgan",
            "PAYMENT_BILLING": "We take payment concerns very seriously. Please send us a secure Direct Message with your order details so we can investigate. - Jordan",
            "GENERAL_FEEDBACK_COMPLAINT": "Thank you for bringing this to our attention. Please DM us your details so we can share your feedback with our team. - Chris"
        }
        return templates.get(intent, "Thanks for reaching out to Amazon Support! Please send us a DM with your details so we can help. - Team Amazon")
