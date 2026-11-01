"""Memory store: the assistant's durable state, as one JSON file.

Deliberately boring. A single JSON document holding enquiries, bookings,
the follow-up queue, and an append-only event log. Lesson 15 and 16
cover when to graduate to a real database; the interface below is what
must survive that move.
"""

from __future__ import annotations

import json
import os


class MemoryStore:
    def __init__(self, path: str = "assistant_state.json"):
        self.path = path
        self.state = {"enquiries": {}, "bookings": {}, "followups": [],
                      "events": []}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                self.state = json.load(fh)

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(self.state, fh, indent=2)

    def record_event(self, kind: str, detail: str) -> None:
        """Append to the audit log. Events are never edited or removed."""
        # TODO(capstone): append {"kind": kind, "detail": detail} and save.
        raise NotImplementedError("capstone: implement record_event()")

    def upsert_enquiry(self, enquiry_dict: dict) -> None:
        """Insert or replace one enquiry record, keyed by its id."""
        # TODO(capstone): store by id and save.
        raise NotImplementedError("capstone: implement upsert_enquiry()")
