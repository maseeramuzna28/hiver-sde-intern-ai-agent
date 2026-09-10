"""
Main Support Agent backend wrapper.
"""
from typing import Dict, Any, Optional
from .classifier import ClaudeClassifier
from .reply_generator import ReplyGenerator, EscalationManager

class SupportAgent:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.classifier = ClaudeClassifier(api_key=api_key, model=model or "claude-3-5-sonnet-20241022")
        self.reply_generator = ReplyGenerator()
        self.escalation_manager = EscalationManager()

    def process_message(self, text: str) -> Dict[str, Any]:
        classification = self.classifier.classify(text)
        escalation_result = self.escalation_manager.evaluate_escalation(text, classification)
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
