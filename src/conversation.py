"""
Multi-turn conversation context manager.

Maintains thread history so the classifier sees prior turns in a conversation,
not just the isolated latest tweet. This addresses Failure Mode 3 (truncated
multi-turn threads) described in the report.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Turn:
    """A single turn in a support conversation."""
    role: str           # 'customer' or 'agent'
    text: str
    intent: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class ConversationThread:
    """A multi-turn conversation thread."""
    thread_id: str
    turns: List[Turn] = field(default_factory=list)
    resolved: bool = False

    def add_turn(self, role: str, text: str, intent: str = None, confidence: float = None):
        self.turns.append(Turn(role=role, text=text, intent=intent, confidence=confidence))

    def get_context_window(self, max_turns: int = 4) -> List[Turn]:
        """Returns the last N turns for context injection."""
        return self.turns[-max_turns:] if len(self.turns) > max_turns else self.turns[:]

    def format_context_for_prompt(self, max_turns: int = 4) -> str:
        """Formats prior turns as a readable context string for the LLM prompt."""
        window = self.get_context_window(max_turns)
        if not window:
            return ""
        lines = ["Prior conversation context:"]
        for i, turn in enumerate(window):
            prefix = "Customer" if turn.role == "customer" else "Agent"
            lines.append(f"  [{i+1}] {prefix}: {turn.text}")
        return "\n".join(lines)

    @property
    def turn_count(self) -> int:
        return len(self.turns)

    @property
    def last_customer_intent(self) -> Optional[str]:
        """Returns the intent of the most recent customer turn with a known intent."""
        for turn in reversed(self.turns):
            if turn.role == "customer" and turn.intent:
                return turn.intent
        return None


class ConversationStore:
    """
    In-memory store for active conversation threads.
    In production this would be backed by Redis or a DB.
    """
    def __init__(self):
        self._threads: Dict[str, ConversationThread] = {}

    def get_or_create(self, thread_id: str) -> ConversationThread:
        if thread_id not in self._threads:
            self._threads[thread_id] = ConversationThread(thread_id=thread_id)
        return self._threads[thread_id]

    def get(self, thread_id: str) -> Optional[ConversationThread]:
        return self._threads.get(thread_id)

    def close(self, thread_id: str):
        if thread_id in self._threads:
            self._threads[thread_id].resolved = True

    def list_active(self) -> List[str]:
        return [tid for tid, t in self._threads.items() if not t.resolved]

    def clear(self, thread_id: str):
        self._threads.pop(thread_id, None)


# Module-level singleton store
conversation_store = ConversationStore()
