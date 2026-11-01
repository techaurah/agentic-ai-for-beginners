"""
Lesson 15 exercise solution: pinned facts.

Problem with the lesson version: trimming protects the budget, but a
fact stated early ("I am allergic to fluoride") can be trimmed away
while small talk survives. The fix is a third memory tier: pinned facts.
A pin is extracted once, stored outside the transcript, and re-injected
into every context, like slots, but for safety and preference facts the
user states explicitly rather than task data being collected.

Run it:  python3 solution.py
"""

import json
import re


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


class ConversationState:
    def __init__(self, system_prompt: str, token_budget: int = 120):
        self.system_prompt = system_prompt
        self.token_budget = token_budget
        self.turns: list[dict] = []
        self.slots: dict = {}
        self.pins: list[str] = []          # pinned facts, never trimmed
        self.trimmed_note = ""
        self._trimmed_total = 0
        self._trimmed_topics: list[str] = []

    def add(self, role: str, content: str) -> None:
        self.turns.append({"role": role, "content": content})
        if role == "user":
            self._extract(content)
        self._trim()

    def _extract(self, content: str) -> None:
        lower = content.lower()
        name_match = re.search(r"my name is ([A-Za-z]+)", lower)
        if name_match:
            self.slots["customer"] = name_match.group(1).capitalize()
        for service in ("cleaning", "checkup", "consultation"):
            if service in lower:
                self.slots["service"] = service
        # Pins: anything the user flags as a standing fact about themselves.
        for trigger in ("allergic to", "i use a wheelchair", "do not call",
                        "i am deaf", "no fluoride"):
            if trigger in lower and content not in self.pins:
                self.pins.append(content)

    def _transcript_tokens(self) -> int:
        total = estimate_tokens(self.system_prompt) + estimate_tokens(self.trimmed_note)
        total += sum(estimate_tokens(p) for p in self.pins)
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
        messages = [{"role": "system", "content": self.system_prompt}]
        if self.trimmed_note:
            messages.append({"role": "system", "content": self.trimmed_note})
        messages.extend(self.turns)
        if self.slots:
            messages.append({"role": "system",
                             "content": f"Known facts (slots): {json.dumps(self.slots)}"})
        for pin in self.pins:
            messages.append({"role": "system", "content": f"PINNED FACT: {pin}"})
        return messages


if __name__ == "__main__":
    state = ConversationState("You are a booking assistant for BrightSmile Dental.",
                              token_budget=120)
    script = [
        ("user", "Hi, my name is Amara. One important thing: I am allergic to fluoride."),
        ("assistant", "Noted, Amara, no fluoride for you. What can I book today?"),
        ("user", "A cleaning on Friday morning if possible."),
        ("assistant", "Friday has 09:00, 10:30, and 14:00 free."),
        ("user", "Before we lock it in, what does a cleaning include?"),
        ("assistant", "A scale and polish, plus a brief gum check by the hygienist."),
        ("user", "And how long does it take, roughly?"),
        ("assistant", "About 45 minutes, including a few minutes to settle in."),
        ("user", "Great. Yes, Friday at 09:00 for the cleaning please."),
    ]
    for role, content in script:
        state.add(role, content)

    context = state.build_context()
    print(f"Turns kept: {len(state.turns)} of {len(script)}")
    print(f"Pins: {state.pins}")
    print("\nContext on the next turn:")
    for message in context:
        print(f"  [{message['role']}] {message['content']}")
    fluoride_mentions = sum(1 for m in context if "fluoride" in m["content"].lower())
    print(f"\nThe allergy fact survives in context: {fluoride_mentions > 0}")
