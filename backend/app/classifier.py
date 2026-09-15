"""
Classifier module using Groq (Llama 3.3 70B) or Anthropic Claude with structured JSON output and robust fallback.
"""
import json
import logging
import re
from typing import Dict, Any, Optional

from .config import (
    GROQ_API_KEY,
    ANTHROPIC_API_KEY,
    DEFAULT_MODEL,
    API_PROVIDER,
    SYSTEM_PROMPT,
    INTENT_TAXONOMY,
    HIGH_RISK_KEYWORDS
)

logger = logging.getLogger(__name__)


class ClaudeClassifier:
    """Classifies customer support messages using Groq/Claude API or heuristic fallback."""

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        self.model    = model
        self.provider = API_PROVIDER
        self.client   = None

        if self.provider == "groq":
            try:
                from groq import Groq
                self.client = Groq(api_key=api_key or GROQ_API_KEY)
                logger.info(f"Using Groq API — model: {self.model}")
            except Exception as e:
                logger.warning(f"Groq init failed: {e}. Using heuristic fallback.")
        elif self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=api_key or ANTHROPIC_API_KEY)
                logger.info(f"Using Anthropic API — model: {self.model}")
            except Exception as e:
                logger.warning(f"Anthropic init failed: {e}. Using heuristic fallback.")

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
                return self._classify_with_llm(text)
            except Exception as e:
                logger.warning(f"API call failed: {e}. Falling back to heuristic.")

        return self._heuristic_classify(text)

    def _classify_with_llm(self, text: str) -> Dict[str, Any]:
        prompt = f"Current Customer Tweet: \"{text}\"\n\nClassify this message and generate a structured JSON response."

        if self.provider == "groq":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=500,
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content.strip()
        else:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text.strip()

        parsed = self._parse_json_response(content)
        intent = parsed.get("intent", "GENERAL_FEEDBACK_COMPLAINT")
        if intent not in INTENT_TAXONOMY:
            intent = "GENERAL_FEEDBACK_COMPLAINT"

        try:
            confidence = max(0.0, min(1.0, float(parsed.get("confidence", 0.90))))
        except (TypeError, ValueError):
            confidence = 0.90

        suggested_reply = str(parsed.get("suggested_reply", "")).strip()
        if len(suggested_reply) > 280:
            suggested_reply = suggested_reply[:277].rstrip() + "..."

        return {
            "intent":            intent,
            "confidence":        confidence,
            "needs_escalation":  parsed.get("needs_escalation", False) is True,
            "escalation_reason": str(parsed.get("escalation_reason", "")),
            "suggested_reply":   suggested_reply,
        }

    @staticmethod
    def _parse_json_response(content: str) -> Dict[str, Any]:
        """Accept plain JSON or JSON wrapped in a markdown response."""
        cleaned = content.strip()
        fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.IGNORECASE | re.DOTALL)
        if fenced:
            cleaned = fenced.group(1).strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            start, end = cleaned.find("{"), cleaned.rfind("}")
            if start < 0 or end <= start:
                raise
            parsed = json.loads(cleaned[start:end + 1])

        if not isinstance(parsed, dict):
            raise ValueError("LLM response must be a JSON object")
        return parsed

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
        max_score   = scores[best_intent]
        confidence  = 0.65 if max_score == 0 else min(0.70 + (max_score * 0.08), 0.95)

        if INTENT_TAXONOMY[best_intent]["requires_escalation_default"] or confidence < 0.70:
            needs_escalation = True
            if not escalation_reason:
                escalation_reason = f"Low confidence ({confidence:.2f}) or billing category requiring supervisor review."

        return {
            "intent":            best_intent,
            "confidence":        confidence,
            "needs_escalation":  needs_escalation,
            "escalation_reason": escalation_reason,
            "suggested_reply":   self._fallback_reply(best_intent),
        }

    def _fallback_reply(self, intent: str) -> str:
        templates = {
            "ORDER_STATUS_DELIVERY":     "We'd love to look into your delivery status! Please send us a DM with your order ID so we can assist right away. - Alex",
            "RETURNS_REFUNDS":           "Sorry to hear you need a return/refund! Please DM us your order number and email so we can get this sorted. - Sam",
            "PRODUCT_ISSUE_DEFECT":      "We apologize for the inconvenience! Please send us a DM with your order details so we can arrange a replacement. - Taylor",
            "ACCOUNT_DIGITAL_PRIME":     "We're here to help with your account! Please DM us your registered email so our technical team can assist. - Morgan",
            "PAYMENT_BILLING":           "We take payment concerns very seriously. Please DM us your order details so we can investigate immediately. - Jordan",
            "GENERAL_FEEDBACK_COMPLAINT":"Thank you for reaching out. Please DM us your details so we can escalate your feedback to the right team. - Chris",
        }
        return templates.get(intent, "Thanks for reaching out! Please send us a DM with your details so we can help. - Team Amazon")
