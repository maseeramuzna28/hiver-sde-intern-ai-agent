"""
Reply generator module for synthesizing context-aware customer support responses.
"""
from typing import Dict, Any

class ReplyGenerator:
    """Generates customer support replies tailored to intent and conversation context."""

    def __init__(self):
        self.brand_signoffs = ["- Alex", "- Sam", "- Taylor", "- Jordan", "- Chris"]

    def generate_reply(self, message: str, classification_result: Dict[str, Any]) -> str:
        """
        Generates a brand-compliant reply.
        Uses Claude API suggested reply if available, or synthesizes based on intent context.
        """
        suggested = classification_result.get("suggested_reply", "").strip()
        
        # If suggested reply is comprehensive and non-generic, return it
        if suggested and len(suggested) > 20 and not suggested.startswith("Hello! How can we assist"):
            return suggested

        intent = classification_result.get("intent", "GENERAL_FEEDBACK_COMPLAINT")
        return self._build_intent_reply(intent, message)

    def _build_intent_reply(self, intent: str, message: str) -> str:
        """Builds intent specific response template."""
        if intent == "ORDER_STATUS_DELIVERY":
            return "We'd be glad to track this down for you! Please send us a Direct Message with your 17-digit order number so we can check the status immediately."
        elif intent == "RETURNS_REFUNDS":
            return "We're sorry for the trouble! Please send us a DM with your order details and we will guide you through the instant return/refund process."
        elif intent == "PRODUCT_ISSUE_DEFECT":
            return "Apologies that your order arrived in less than perfect condition! Please DM us your order ID and a quick details description so we can send a replacement."
        elif intent == "ACCOUNT_DIGITAL_PRIME":
            return "We're here to help get your Prime access/account sorted! Please DM us your registered account email so we can investigate."
        elif intent == "PAYMENT_BILLING":
            return "We understand billing issues are urgent. Please send us a private Direct Message with your order details so our billing team can review this right away."
        else:
            return "Thank you for reaching out to @AmazonHelp. Please send us a Direct Message with details about your experience so we can best assist you!"
