"""Business assistant pipeline: capture, qualify, book, follow up.

A small, deterministic reference implementation of the pattern taught in
Lesson 31 of Agentic AI for Beginners (TechAura Academy).

Pipeline stages:
  1. capture   - take raw enquiries from any channel, normalise, dedupe
  2. qualify   - score each enquiry 0-100 on eight signals, assign a band
  3. book      - HOT and WARM enquiries get a slot on a fake calendar
  4. follow up - NURTURE enquiries enter a follow-up queue with a ladder

Standard library only. No network, no API keys, no randomness: the same
seed data always produces the same output, so you can diff your changes
against the lesson text.

Run:  python3 business_assistant.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Scoring model (the same model used across TechAura's open-source tools)
#
# Eight signals, each scored up to its weight. Total 100.
#   problem  20  how painful and specific is the problem?
#   fit      20  how well does the business match what we sell?
#   value    15  likely deal value
#   size     10  company size / capacity to use the offer
#   pay      10  signals they can and do pay for solutions
#   access   10  can we reach a decision maker?
#   urgency  10  how soon do they need it?
#   activity  5  recent engagement signals
# ---------------------------------------------------------------------------

WEIGHTS = {
    "problem": 20,
    "fit": 20,
    "value": 15,
    "size": 10,
    "pay": 10,
    "access": 10,
    "urgency": 10,
    "activity": 5,
}

BANDS = ((80, "HOT"), (65, "WARM"), (50, "NURTURE"), (0, "COLD"))


def band_for(score: int) -> str:
    for threshold, name in BANDS:
        if score >= threshold:
            return name
    return "COLD"


# ---------------------------------------------------------------------------
# Seeded enquiries. In production these arrive from web forms, Instagram
# DMs, WhatsApp, email. Here they are fixed dicts so the run is repeatable.
# The "signals" dict is what an LLM extraction step (Lesson 04/12) or a
# human would produce from the raw message. Everything after extraction
# is deterministic code, on purpose: money decisions should not be vibes.
# ---------------------------------------------------------------------------

SEED_ENQUIRIES = [
    {
        "id": "ENQ-001",
        "channel": "website",
        "name": "Brightpath Dental",
        "contact": "ops@brightpathdental.example",
        "message": "We miss calls after 6pm and lose bookings. Need cover this month.",
        "signals": {"problem": 19, "fit": 20, "value": 13, "size": 8,
                    "pay": 9, "access": 9, "urgency": 10, "activity": 4},
    },
    {
        "id": "ENQ-002",
        "channel": "instagram",
        "name": "Glowhaus Med Spa",
        "contact": "@glowhausmedspa",
        "message": "DMs pile up on weekends. Interested in automated replies.",
        "signals": {"problem": 15, "fit": 18, "value": 11, "size": 6,
                    "pay": 7, "access": 6, "urgency": 6, "activity": 5},
    },
    {
        "id": "ENQ-003",
        "channel": "whatsapp",
        "name": "Summit Roofing",
        "contact": "+1-555-013-4471",
        "message": "Quotes go out late and nobody follows up. Losing jobs.",
        "signals": {"problem": 17, "fit": 16, "value": 14, "size": 7,
                    "pay": 8, "access": 5, "urgency": 8, "activity": 3},
    },
    {
        "id": "ENQ-004",
        "channel": "website",
        "name": "Brightpath Dental",
        "contact": "ops@brightpathdental.example",
        "message": "Following up on my earlier message about after-hours calls.",
        "signals": {"problem": 19, "fit": 20, "value": 13, "size": 8,
                    "pay": 9, "access": 9, "urgency": 10, "activity": 4},
    },
    {
        "id": "ENQ-005",
        "channel": "email",
        "name": "City Pets Clinic",
        "contact": "hello@citypets.example",
        "message": "Maybe looking at reminders next quarter, just researching.",
        "signals": {"problem": 11, "fit": 14, "value": 8, "size": 6,
                    "pay": 6, "access": 5, "urgency": 3, "activity": 3},
    },
    {
        "id": "ENQ-006",
        "channel": "instagram",
        "name": "Random Giveaway Page",
        "contact": "@freestuffdaily",
        "message": "Collab? We promote pages for exposure.",
        "signals": {"problem": 1, "fit": 0, "value": 0, "size": 1,
                    "pay": 0, "access": 1, "urgency": 0, "activity": 1},
    },
]


# ---------------------------------------------------------------------------
# Stage 1: capture
# ---------------------------------------------------------------------------

@dataclass
class Enquiry:
    id: str
    channel: str
    name: str
    contact: str
    message: str
    signals: dict
    score: int = 0
    band: str = ""


def capture(raw_enquiries: list[dict]) -> list[Enquiry]:
    """Normalise raw channel payloads and drop exact duplicates.

    Dedupe key: the contact handle. A second message from the same
    contact is a follow-up to the conversation, not a new lead, and
    counting it twice inflates every report downstream.
    """
    by_contact: dict[str, Enquiry] = {}
    enquiries = []
    for raw in raw_enquiries:
        contact = raw["contact"].strip().lower()
        if contact in by_contact:
            existing = by_contact[contact]
            existing.signals["activity"] = min(
                WEIGHTS["activity"], existing.signals.get("activity", 0) + 2)
            existing.message = raw["message"]
            print(f"capture: repeat contact {raw['contact']} ({raw['id']}) "
                  f"merged into {existing.id}, activity boosted")
            continue
        entry = Enquiry(
            id=raw["id"], channel=raw["channel"], name=raw["name"],
            contact=raw["contact"], message=raw["message"],
            signals=dict(raw["signals"]),
        )
        enquiries.append(entry)
        by_contact[contact] = entry
    return enquiries


# ---------------------------------------------------------------------------
# Stage 2: qualify
# ---------------------------------------------------------------------------

def qualify(enquiry: Enquiry) -> Enquiry:
    """Score 0-100 from the eight signals and assign a band.

    Signal values are clamped to their weights: a buggy extractor (or an
    over-enthusiastic LLM) must not be able to push a score past 100.
    """
    total = 0
    for signal, weight in WEIGHTS.items():
        total += max(0, min(weight, int(enquiry.signals.get(signal, 0))))
    enquiry.score = total
    enquiry.band = band_for(total)
    return enquiry


# ---------------------------------------------------------------------------
# Stage 3: book (fake calendar)
# ---------------------------------------------------------------------------

@dataclass
class FakeCalendar:
    """A stand-in for Google Calendar etc. Slots are fixed strings.

    The assistant only ever sees this interface (is_free / book), so
    swapping in a real calendar later changes one class, not the pipeline.
    """
    slots: list[str] = field(default_factory=lambda: [
        "Tue 10:00", "Tue 14:00", "Wed 09:30", "Wed 13:00", "Thu 11:00",
    ])
    booked: dict = field(default_factory=dict)  # slot -> enquiry id

    def book_first_free(self, enquiry_id: str) -> str | None:
        for slot in self.slots:
            if slot not in self.booked:
                self.booked[slot] = enquiry_id
                return slot
        return None


# ---------------------------------------------------------------------------
# Stage 4: follow up
# ---------------------------------------------------------------------------

FOLLOW_UP_LADDER = [
    {"day": 1, "action": "Send a helpful recap and one useful resource. No pitch."},
    {"day": 3, "action": "Ask one diagnostic question about their current process."},
    {"day": 7, "action": "Share a relevant result pattern and offer a short call."},
    {"day": 14, "action": "Final check-in. If no reply, move to monthly nurture."},
]


@dataclass
class FollowUp:
    enquiry_id: str
    name: str
    band: str
    ladder: list = field(default_factory=lambda: FOLLOW_UP_LADDER)


# ---------------------------------------------------------------------------
# The pipeline
# ---------------------------------------------------------------------------

def run_pipeline(raw_enquiries: list[dict]) -> dict:
    calendar = FakeCalendar()
    follow_ups: list[FollowUp] = []
    escalations: list[dict] = []
    results = []

    for enquiry in qualify_all(capture(raw_enquiries)):
        if enquiry.band in ("HOT", "WARM"):
            slot = calendar.book_first_free(enquiry.id)
            if slot:
                action = f"booked {slot}"
            else:
                action = "no slot free: escalate to human"
                escalations.append({"id": enquiry.id, "name": enquiry.name,
                                    "score": enquiry.score, "band": enquiry.band})
        elif enquiry.band == "NURTURE":
            follow_ups.append(FollowUp(enquiry.id, enquiry.name, enquiry.band))
            action = "added to follow-up queue"
        else:  # COLD
            action = "archived (below nurture threshold)"
        results.append({
            "id": enquiry.id, "name": enquiry.name, "channel": enquiry.channel,
            "score": enquiry.score, "band": enquiry.band, "action": action,
        })

    return {"results": results, "calendar": calendar.booked,
            "follow_up_queue": follow_ups, "escalations": escalations}


def qualify_all(enquiries: list[Enquiry]) -> list[Enquiry]:
    return [qualify(e) for e in enquiries]


def main() -> None:
    outcome = run_pipeline(SEED_ENQUIRIES)
    print("\n=== Business assistant run ===")
    for r in outcome["results"]:
        print(f"{r['id']}  {r['name']:<22} {r['channel']:<9} "
              f"score {r['score']:>3}  {r['band']:<7} -> {r['action']}")
    print("\nCalendar:", json.dumps(outcome["calendar"], indent=2))
    print(f"Follow-up queue: {[f.enquiry_id for f in outcome['follow_up_queue']]}")
    print(f"Ladder for each queued lead: "
          f"{[step['day'] for step in FOLLOW_UP_LADDER]} days")
    print(f"Escalations for a human: {outcome['escalations']}")


if __name__ == "__main__":
    main()
