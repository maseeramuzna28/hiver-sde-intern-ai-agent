"""
Main Support Agent module orchestrating classification, reply generation, and escalation.
Supports both single-turn and multi-turn conversation context.
"""
from typing import Dict, Any, Optional
from .classifier import ClaudeClassifier
from .reply_generator import ReplyGenerator
from .escalation import EscalationManager
from .conversation import ConversationThread, conversation_store
from .config import DEFAULT_MODEL


class SupportAgent:
    """End-to-End AI Support Agent for Customer Support Automation."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.classifier = ClaudeClassifier(api_key=api_key, model=model or DEFAULT_MODEL)
        self.reply_generator = ReplyGenerator()
        self.escalation_manager = EscalationManager()

    def process_message(self, text: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes an incoming customer message, optionally within a conversation thread.

        Args:
            text: Customer tweet or message content.
            thread_id: Optional thread/conversation ID. If provided, prior turns from
                       that thread are injected as context into the classifier prompt,
                       directly addressing Failure Mode 3 (truncated multi-turn threads).

        Returns:
            Dict containing:
                - text, intent, confidence, needs_escalation,
                  escalation_reason, priority, suggested_reply,
                  thread_id (if multi-turn), turn_number (if multi-turn)
        """
        # ── Multi-turn context ──────────────────────────────────────────────────
        conversation_context = ""
        thread = None
        if thread_id:
            thread = conversation_store.get_or_create(thread_id)
            conversation_context = thread.format_context_for_prompt(max_turns=4)

        # Step 1: Classify intent via Claude API / Fallback (with thread context if available)
        classification = self.classifier.classify(text, conversation_context=conversation_context)

        # Step 2: Evaluate Escalation Triggers
        escalation_result = self.escalation_manager.evaluate_escalation(text, classification)

        # Step 3: Generate or Refine Response
        suggested_reply = self.reply_generator.generate_reply(text, classification)

        # Step 4: Record this turn into the thread
        if thread is not None:
            thread.add_turn(
                role="customer",
                text=text,
                intent=classification["intent"],
                confidence=classification["confidence"]
            )
            thread.add_turn(role="agent", text=suggested_reply)

        result = {
            "text": text,
            "intent": classification["intent"],
            "confidence": round(classification["confidence"], 3),
            "needs_escalation": escalation_result["needs_escalation"],
            "escalation_reason": escalation_result["escalation_reason"],
            "priority": escalation_result["priority"],
            "suggested_reply": suggested_reply,
        }

        # Attach thread metadata if multi-turn
        if thread is not None:
            result["thread_id"] = thread_id
            result["turn_number"] = thread.turn_count // 2  # customer turns only
            result["prior_intent"] = thread.last_customer_intent

        return result

    def reset_thread(self, thread_id: str):
        """Clears a conversation thread (e.g. when issue is resolved)."""
        conversation_store.clear(thread_id)
