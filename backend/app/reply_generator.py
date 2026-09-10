"""
Reply Generator and Escalation Manager for Backend.
"""
from typing import Dict, Any
from .config import HIGH_RISK_KEYWORDS, INTENT_TAXONOMY

class ReplyGenerator:
    def generate_reply(self, message: str, classification_result: Dict[str, Any]) -> str:
        suggested = classification_result.get("suggested_reply", "").strip()
        if suggested and len(suggested) > 20 and not suggested.startswith("Hello! How can we assist"):
            return suggested
        intent = classification_result.get("intent", "GENERAL_FEEDBACK_COMPLAINT")
        return self._build_intent_reply(intent)

    def _build_intent_reply(self, intent: str) -> str:
        templates = {
            "ORDER_STATUS_DELIVERY": "We'd be glad to track this down for you! Please send us a Direct Message with your 17-digit order number so we can check the status immediately.",
            "RETURNS_REFUNDS": "We're sorry for the trouble! Please send us a DM with your order details and we will guide you through the instant return/refund process.",
            "PRODUCT_ISSUE_DEFECT": "Apologies that your order arrived in less than perfect condition! Please DM us your order ID and a quick details description so we can send a replacement.",
            "ACCOUNT_DIGITAL_PRIME": "We're here to help get your Prime access/account sorted! Please DM us your registered account email so we can investigate.",
            "PAYMENT_BILLING": "We understand billing issues are urgent. Please send us a private Direct Message with your order details so our billing team can review this right away.",
            "GENERAL_FEEDBACK_COMPLAINT": "Thank you for reaching out to @AmazonHelp. Please send us a Direct Message with details about your experience so we can best assist you!"
        }
        return templates.get(intent, "Thank you for contacting @AmazonHelp. Please send us a DM with your order ID so we can assist!")

class EscalationManager:
    CONFIDENCE_THRESHOLD = 0.70

    def evaluate_escalation(self, message: str, classification: Dict[str, Any]) -> Dict[str, Any]:
        reasons = []
        priority = "LOW"
        message_lower = message.lower()

        found_keywords = [kw for kw in HIGH_RISK_KEYWORDS if kw in message_lower]
        if found_keywords:
            reasons.append(f"High risk terms detected: {', '.join(found_keywords)}")
            priority = "URGENT"

        confidence = classification.get("confidence", 1.0)
        if confidence < self.CONFIDENCE_THRESHOLD:
            reasons.append(f"Low AI confidence score ({confidence:.2f} < {self.CONFIDENCE_THRESHOLD})")
            if priority != "URGENT":
                priority = "MEDIUM"

        intent = classification.get("intent", "")
        intent_meta = INTENT_TAXONOMY.get(intent, {})
        if intent_meta.get("requires_escalation_default", False):
            reasons.append(f"Intent category '{intent}' requires mandatory agent review.")
            if priority == "LOW":
                priority = "MEDIUM"

        if classification.get("needs_escalation", False):
            llm_reason = classification.get("escalation_reason", "")
            if llm_reason and llm_reason not in reasons:
                reasons.append(f"LLM Escalation Flag: {llm_reason}")
            if priority == "LOW":
                priority = "MEDIUM"

        needs_escalation = len(reasons) > 0
        final_reason = "; ".join(reasons) if reasons else "Routine inquiry; standard automated workflow."

        return {
            "needs_escalation": needs_escalation,
            "escalation_reason": final_reason,
            "priority": priority if needs_escalation else "AUTOMATED"
        }
