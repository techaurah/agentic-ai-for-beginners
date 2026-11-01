"""
Lesson 15: Short-term memory and conversation state.

Short-term memory is two different things that beginners often merge:

  1. The transcript: the messages you send back to the model each turn.
     It cannot grow forever, so you keep a window: system prompt first,
     recent turns last, and a compact note for what was trimmed away.
  2. Task state: structured facts the conversation has established
     (slots). State survives trimming because it lives outside the
     transcript, and it is what your tools and code actually read.

Run it:  python3 conversation_state.py
"""

import json
import re


def estimate_tokens(text: str) -> int:
    """Rough estimate: about 4 characters per token for English text."""
    return max(1, len(text) // 4)


class ConversationState:
    """A windowed transcript plus a slot store, with a trim log."""

    def __init__(self, system_prompt: str, token_budget: int = 120):
        self.system_prompt = system_prompt
        self.token_budget = token_budget
        self.turns: list[dict] = []        # {"role": ..., "content": ...}
        self.slots: dict = {}              # structured facts, never trimmed
        self.trimmed_note = ""             # compact note about dropped turns
        self._trimmed_total = 0
        self._trimmed_topics: list[str] = []

    # -- writing -----------------------------------------------------------
    def add(self, role: str, content: str) -> None:
        self.turns.append({"role": role, "content": content})
        self._extract_slots(content)
        self._trim()

    def _extract_slots(self, content: str) -> None:
        """Pull structured facts out of a message with simple rules.

        A real system uses the model or a form to fill slots; the point
        here is where the facts live, not how clever the extraction is.
        """
        lower = content.lower()
        for service in ("cleaning", "checkup", "consultation"):
            if service in lower:
                self.slots["service"] = service
        for day in ("friday", "saturday", "monday"):
            if day in lower:
                self.slots["day"] = day
        name_match = re.search(r"my name is ([A-Za-z]+)", lower)
        if name_match:
            self.slots["customer"] = name_match.group(1).capitalize()

    # -- the window --------------------------------------------------------
    def _transcript_tokens(self) -> int:
        total = estimate_tokens(self.system_prompt) + estimate_tokens(self.trimmed_note)
        return total + sum(estimate_tokens(t["content"]) for t in self.turns)

    def _trim(self) -> None:
        dropped = []
        while self._transcript_tokens() > self.token_budget and len(self.turns) > 2:
            dropped.append(self.turns.pop(0))
        if dropped:
            self._trimmed_total += len(dropped)
            self._trimmed_topics.extend(t["content"][:24] for t in dropped)
            topics = ", ".join(sorted(set(self._trimmed_topics)))
            self.trimmed_note = (f"[{self._trimmed_total} earlier turn(s) trimmed. "
                                 f"They covered: {topics}...]")

    def build_context(self) -> list[dict]:
        """What you would actually send to the model this turn."""
        messages = [{"role": "system", "content": self.system_prompt}]
        if self.trimmed_note:
            messages.append({"role": "system", "content": self.trimmed_note})
        messages.extend(self.turns)
        if self.slots:
            messages.append({"role": "system",
                             "content": f"Known facts (slots): {json.dumps(self.slots)}"})
        return messages


if __name__ == "__main__":
    state = ConversationState(
        system_prompt="You are a booking assistant for BrightSmile Dental.",
        token_budget=120,
    )

    script = [
        ("user", "Hi, my name is Amara and I need a cleaning."),
        ("assistant", "Hello Amara, I can book a cleaning. Which day suits you?"),
        ("user", "Friday would be perfect, in the morning if possible."),
        ("assistant", "Friday has 09:00, 10:30, and 14:00 free. Shall I take 09:00?"),
        ("user", "Actually, before we lock it in, what does a cleaning include?"),
        ("assistant", "A cleaning includes a scale and polish, a fluoride treatment, "
                    "and a brief check of your gums by the hygienist."),
        ("user", "That sounds fine. And how long does it take, roughly?"),
        ("assistant", "About 45 minutes, including a few minutes to settle in."),
        ("user", "Great. Yes, let us go with Friday at 09:00 for the cleaning."),
    ]
    for role, content in script:
        state.add(role, content)

    context = state.build_context()
    print(f"Turns kept in window: {len(state.turns)} of {len(script)}")
    print(f"Slots (never trimmed): {json.dumps(state.slots)}")
    print("\nContext sent to the model on the next turn:")
    for message in context:
        print(f"  [{message['role']}] {message['content']}")
