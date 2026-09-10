"""
Classifier module using Claude API with structured JSON output and robust fallback.
"""
import json
import logging
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
        if not text or not text.strip():
            return {
                "intent": "GENERAL_FEEDBACK_COMPLAINT",
                "confidence": 0.5,
                "needs_escalation": False,
                "escalation_reason": "Empty or whitespace message",
                "suggested_reply": "Hello! How can we assist you with your Amazon order today?"
            }

        if self.client:
            try:
                return self._classify_with_claude(text)
            except Exception as e:
                logger.warning(f"Claude API Error: {e}. Falling back to heuristic classifier.")

        return self._heuristic_classify(text)

    def _classify_with_claude(self, text: str) -> Dict[str, Any]:
        prompt = f"Customer Tweet: \"{text}\"\n\nClassify this message and generate a structured JSON response."
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.content[0].text.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        parsed = json.loads(content)
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
        text_lower = text.lower()
        high_risk_found = [kw for kw in HIGH_RISK_KEYWORDS if kw in text_lower]
        needs_escalation = len(high_risk_found) > 0
        escalation_reason = f"Contains high risk keywords: {', '.join(high_risk_found)}" if high_risk_found else ""

        scores = {intent: 0 for intent in INTENT_TAXONOMY}
        if any(w in text_lower for w in ["where is", "track", "delivery", "delivered", "shipping", "shipped", "carrier", "delay", "arriving", "package"]):
            scores["ORDER_STATUS_DELIVERY"] += 3
        if any(w in text_lower for w in ["return", "refund", "replace", "exchange", "money back", "send back"]):
            scores["RETURNS_REFUNDS"] += 3
        if any(w in text_lower for w in ["broken", "damaged", "defective", "wrong item", "faulty", "not working", "destroyed", "missing item"]):
            scores["PRODUCT_ISSUE_DEFECT"] += 3
        if any(w in text_lower for w in ["prime", "video", "kindle", "login", "password", "account", "sign in", "subscription"]):
            scores["ACCOUNT_DIGITAL_PRIME"] += 3
        if any(w in text_lower for w in ["charge", "billed", "payment", "card", "promo", "discount", "double charge", "unauthorized"]):
            scores["PAYMENT_BILLING"] += 3
        if any(w in text_lower for w in ["driver", "worst", "terrible", "bad service", "thanks", "great", "complaint", "rude"]):
            scores["GENERAL_FEEDBACK_COMPLAINT"] += 2

        best_intent = max(scores, key=scores.get)
        max_score = scores[best_intent]
        confidence = 0.65 if max_score == 0 else min(0.70 + (max_score * 0.08), 0.95)

        if INTENT_TAXONOMY[best_intent]["requires_escalation_default"] or confidence < 0.70:
            needs_escalation = True
            if not escalation_reason:
                escalation_reason = f"Low confidence score ({confidence:.2f}) or billing category requiring supervisor review."

        reply = self._generate_fallback_reply(best_intent)
        return {
            "intent": best_intent,
            "confidence": confidence,
            "needs_escalation": needs_escalation,
            "escalation_reason": escalation_reason,
            "suggested_reply": reply
        }

    def _generate_fallback_reply(self, intent: str) -> str:
        templates = {
            "ORDER_STATUS_DELIVERY": "We'd love to look into your delivery status! Please send us a DM with your order ID so we can assist you right away. - Alex",
            "RETURNS_REFUNDS": "Sorry to hear you need a return/refund! Please DM us your order number and email address so we can get this sorted for you. - Sam",
            "PRODUCT_ISSUE_DEFECT": "We apologize for the inconvenience with your item! Please send us a direct message with your order details so we can arrange a replacement. - Taylor",
            "ACCOUNT_DIGITAL_PRIME": "We're here to help with your Amazon account/Prime service! Please DM us your registered account email so our technical team can assist. - Morgan",
            "PAYMENT_BILLING": "We take payment concerns very seriously. Please send us a secure Direct Message with your order details so we can investigate. - Jordan",
            "GENERAL_FEEDBACK_COMPLAINT": "Thank you for bringing this to our attention. Please DM us your details so we can share your feedback with our team. - Chris"
        }
        return templates.get(intent, "Thanks for reaching out to Amazon Support! Please send us a DM with your details so we can help. - Team Amazon")
