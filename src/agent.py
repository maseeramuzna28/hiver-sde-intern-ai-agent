"""
Main Support Agent module orchestrating classification, reply generation, and escalation.
"""
from typing import Dict, Any, Optional
from .classifier import ClaudeClassifier
from .reply_generator import ReplyGenerator
from .escalation import EscalationManager

class SupportAgent:
    """End-to-End AI Support Agent for Customer Support Automation."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.classifier = ClaudeClassifier(api_key=api_key, model=model or "claude-3-5-sonnet-20241022")
        self.reply_generator = ReplyGenerator()
        self.escalation_manager = EscalationManager()

    def process_message(self, text: str) -> Dict[str, Any]:
        """
        Processes an incoming customer message.
        
        Args:
            text: Customer tweet or message content.
            
        Returns:
            Dict containing:
                - text: Original message
                - intent: Classified intent category
                - confidence: Classification confidence
                - needs_escalation: Boolean
                - escalation_reason: Reasoning string
                - priority: AUTOMATED, LOW, MEDIUM, or URGENT
                - suggested_reply: Drafted response
        """
        # Step 1: Classify intent via Claude API / Fallback
        classification = self.classifier.classify(text)

        # Step 2: Evaluate Escalation Triggers
        escalation_result = self.escalation_manager.evaluate_escalation(text, classification)

        # Step 3: Generate or Refine Response
        suggested_reply = self.reply_generator.generate_reply(text, classification)

        return {
            "text": text,
            "intent": classification["intent"],
            "confidence": round(classification["confidence"], 3),
            "needs_escalation": escalation_result["needs_escalation"],
            "escalation_reason": escalation_result["escalation_reason"],
            "priority": escalation_result["priority"],
            "suggested_reply": suggested_reply
        }
