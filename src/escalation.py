"""
Escalation module for evaluating human support routing triggers.
"""
from typing import Dict, Any
from .config import HIGH_RISK_KEYWORDS, INTENT_TAXONOMY

class EscalationManager:
    """Determines whether a message requires human escalation and assigns priority levels."""

    CONFIDENCE_THRESHOLD = 0.70

    def evaluate_escalation(self, message: str, classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates escalation criteria.
        
        Returns:
            Dict with: needs_escalation (bool), escalation_reason (str), priority (str)
        """
        reasons = []
        priority = "LOW"
        message_lower = message.lower()

        # Rule 1: High Risk Keywords
        found_keywords = [kw for kw in HIGH_RISK_KEYWORDS if kw in message_lower]
        if found_keywords:
            reasons.append(f"High risk terms detected: {', '.join(found_keywords)}")
            priority = "URGENT"

        # Rule 2: Low Confidence Score
        confidence = classification.get("confidence", 1.0)
        if confidence < self.CONFIDENCE_THRESHOLD:
            reasons.append(f"Low AI confidence score ({confidence:.2f} < {self.CONFIDENCE_THRESHOLD})")
            if priority != "URGENT":
                priority = "MEDIUM"

        # Rule 3: Intent Specific Escalation Policy
        intent = classification.get("intent", "")
        intent_meta = INTENT_TAXONOMY.get(intent, {})
        if intent_meta.get("requires_escalation_default", False):
            reasons.append(f"Intent category '{intent}' requires mandatory agent review.")
            if priority == "LOW":
                priority = "MEDIUM"

        # Rule 4: LLM explicit escalation flag
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
