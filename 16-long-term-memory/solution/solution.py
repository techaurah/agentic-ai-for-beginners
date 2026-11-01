"""
Lesson 16 exercise solution: expiry and total deletion.

Two additions a real long-term store needs:

  1. Expiry. Facts go stale: a preferred time from two years ago may be
     wrong now. Each fact gets a time-to-live; recall() treats expired
     facts as gone, and a weekly-style sweep removes them from disk.
  2. Forget-everything. "Delete everything you remember about me" is a
     request real products must honour, so forget_all() wipes the store
     and reports how many facts were removed.

Run it:  python3 solution.py
"""

import json
import re
import tempfile
from pathlib import Path

NEVER_STORE = [
    (re.compile(r"\b\d{4}[ -]\d{4}[ -]\d{4}[ -]\d{4}\b"), "payment card number"),
    (re.compile(r"\b(?:sk|ghp|AKIA)[A-Za-z0-9_\-]{10,}\b"), "API key or token"),
    (re.compile(r"(?i)\bpassword\b\s*(?:is|:|=)\s*\S+"), "password"),
    (re.compile(r"(?i)\b(?:ssn|social security)\b"), "government ID"),
]

DEFAULT_TTL_DAYS = 180


class MemoryStore:
    def __init__(self, path: Path):
        self.path = path
        self.facts: dict[str, dict] = {}
        if path.exists():
            self.facts = json.loads(path.read_text())

    def remember(self, key: str, value: str, source: str, day: int,
                 ttl_days: int = DEFAULT_TTL_DAYS) -> dict:
        for pattern, label in NEVER_STORE:
            if pattern.search(value):
                return {"stored": False, "reason": f"Refused: value looks like a {label}."}
        self.facts[key] = {"value": value, "source": source, "day": day,
                           "ttl_days": ttl_days}
        self._save()
        return {"stored": True, "key": key}

    def _expired(self, fact: dict, today: int) -> bool:
        return today - fact["day"] > fact["ttl_days"]

    def recall(self, key: str, today: int) -> dict | None:
        fact = self.facts.get(key)
        if fact is None or self._expired(fact, today):
            return None
        return fact

    def sweep_expired(self, today: int) -> list[str]:
        gone = [k for k, f in self.facts.items() if self._expired(f, today)]
        for key in gone:
            del self.facts[key]
        if gone:
            self._save()
        return gone

    def forget_all(self) -> int:
        count = len(self.facts)
        self.facts = {}
        self._save()
        return count

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.facts, indent=2))


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        store = MemoryStore(Path(tmp) / "memory.json")
        store.remember("preferred_time", "morning", source="session-1", day=1)
        store.remember("gate_code_note", "prefers a text before visits",
                       source="session-1", day=1, ttl_days=7)

        print("Day 5:  preferred_time ->", store.recall("preferred_time", today=5))
        print("Day 5:  short-lived fact ->", store.recall("gate_code_note", today=5))
        print("Day 30: short-lived fact ->", store.recall("gate_code_note", today=30),
              "(expired: treated as gone)")
        print("Day 30 sweep removes:", store.sweep_expired(today=30))
        print("Day 30: preferred_time ->", store.recall("preferred_time", today=30))

        print("\nCustomer: 'Delete everything you remember about me.'")
        print("forget_all removed", store.forget_all(), "fact(s)")
        print("Recall after wipe:", store.recall("preferred_time", today=30))
