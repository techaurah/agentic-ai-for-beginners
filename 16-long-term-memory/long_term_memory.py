"""
Lesson 16: Long-term memory: stores, summaries, and what to never store.

Long-term memory is what an agent keeps between sessions. Three skills
matter more than the storage technology:

  1. Store facts, not transcripts. A fact has a key, a value, a source,
     and a confidence, so it can be checked, corrected, and deleted.
  2. Summarise sessions into facts with rules you can inspect. (A model
     can write summaries too, but the storage contract stays the same.)
  3. Refuse to store some things at all. Secrets and payment data do not
     become safe because an agent wrote them into a JSON file.

Run it:  python3 long_term_memory.py
"""

import json
import re
import tempfile
from pathlib import Path

# Patterns that must never reach the store. Order matters: the first
# matching rule is the reason reported to the caller.
NEVER_STORE = [
    (re.compile(r"\b\d{4}[ -]\d{4}[ -]\d{4}[ -]\d{4}\b"), "payment card number"),
    (re.compile(r"\b(?:sk|ghp|AKIA)[A-Za-z0-9_\-]{10,}\b"), "API key or token"),
    (re.compile(r"(?i)\bpassword\b\s*(?:is|:|=)\s*\S+"), "password"),
    (re.compile(r"(?i)\b(?:ssn|social security)\b"), "government ID"),
]


class MemoryStore:
    """A JSON-file fact store with provenance and a never-store filter."""

    def __init__(self, path: Path):
        self.path = path
        self.facts: dict[str, dict] = {}
        if path.exists():
            self.facts = json.loads(path.read_text())

    def remember(self, key: str, value: str, source: str, day: int) -> dict:
        for pattern, label in NEVER_STORE:
            if pattern.search(value):
                return {"stored": False, "reason": f"Refused: value looks like a {label}."}
        self.facts[key] = {"value": value, "source": source, "day": day}
        self._save()
        return {"stored": True, "key": key}

    def recall(self, key: str) -> dict | None:
        return self.facts.get(key)

    def forget(self, key: str) -> bool:
        if key in self.facts:
            del self.facts[key]
            self._save()
            return True
        return False

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.facts, indent=2))


def summarise_session(turns: list[str]) -> list[tuple[str, str]]:
    """Compress one session into storable facts with inspectable rules.

    Returns (key, value) pairs. Anything the rules do not recognise is
    left out on purpose: a long-term store should hold less, not more.
    """
    facts = []
    joined = " ".join(turns).lower()
    for slot in ("morning", "afternoon", "evening"):
        if f"prefers {slot}" in joined or f"{slot} appointments" in joined:
            facts.append(("preferred_time", slot))
    if "text me" in joined or "by text" in joined:
        facts.append(("preferred_channel", "text message"))
    if "email me" in joined:
        facts.append(("preferred_channel", "email"))
    for service in ("cleaning", "checkup", "consultation"):
        if service in joined:
            facts.append(("last_service_discussed", service))
    return facts


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        store = MemoryStore(Path(tmp) / "memory.json")

        session = [
            "Hi, I usually book morning appointments if I can.",
            "Please text me the reminders, I never check email.",
            "Last time the cleaning took longer than expected.",
        ]
        print("Session summary -> facts proposed:")
        for key, value in summarise_session(session):
            result = store.remember(key, value, source="session-2026-11-01", day=1)
            print(f"  {key} = {value!r} -> {result}")

        print("\nTrying to store things that must never be stored:")
        print(" ", store.remember("card", "My card is 4242 4242 4242 4242",
                                  source="chat", day=1))
        print(" ", store.remember("note", "the password is hunter2",
                                  source="chat", day=1))

        print("\nA week later (day 8), a new session recalls:")
        print("  preferred_time ->", store.recall("preferred_time"))
        print("  preferred_channel ->", store.recall("preferred_channel"))

        print("\nThe customer asks to be forgotten:")
        print("  forget preferred_time ->", store.forget("preferred_time"))
        print("  recall after forget ->", store.recall("preferred_time"))
