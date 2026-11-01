"""Guardrails and an approval gate for agent actions.

Three separate defences live in this file, because they solve three
separate problems:

1. check_input(text): screens what reaches the agent. Blocks card numbers
   pasted into chat and classic instruction-override phrases. Input
   screening is a speed bump, not a wall; Lesson 29 covers attacks in
   depth.
2. check_output(text): screens what leaves the agent. Redacts card
   numbers and API keys, and blocks anything that quotes the system
   prompt. Output checks are the layer that still works when every
   other layer has a bad day.
3. classify_action() plus ApprovalGate: screens what the agent DOES.
   Reads are free. Ordinary writes run but are logged. Anything that
   moves money, deletes data, or speaks to the outside world pauses
   until a human says yes. The human's decision, and their reason, are
   recorded with the action.
"""

import re

CARD_RE = re.compile(r"\b(?:\d{4}[\s-]?){3}\d{4}\b")
ID_NUMBER_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
API_KEY_RE = re.compile(r"\bsk-[A-Za-z0-9-]{8,}\b")
OVERRIDE_PHRASES = (
    "ignore your instructions",
    "ignore previous instructions",
    "disregard your instructions",
    "forget your instructions",
)


def check_input(text):
    """Return (allowed, reason). Reason explains a block to the user."""
    if CARD_RE.search(text):
        return False, (
            "blocked: looks like a card number. Never paste card details "
            "into chat; use the secure payment page instead."
        )
    if ID_NUMBER_RE.search(text):
        return False, (
            "blocked: looks like a national ID number. The clinic never "
            "needs that in chat; bring the card to your appointment "
            "instead."
        )
    lowered = text.lower()
    for phrase in OVERRIDE_PHRASES:
        if phrase in lowered:
            return False, (
                "blocked: the message tries to override the agent's "
                "instructions, so it was not passed on."
            )
    return True, "ok"


def check_output(text):
    """Return (text, notes). Secrets are redacted, leaks are blocked."""
    notes = []
    cleaned = text
    if CARD_RE.search(cleaned):
        cleaned = CARD_RE.sub("[card number removed]", cleaned)
        notes.append("redacted a card number")
    if ID_NUMBER_RE.search(cleaned):
        cleaned = ID_NUMBER_RE.sub("[id number removed]", cleaned)
        notes.append("redacted a national ID number")
    if API_KEY_RE.search(cleaned):
        cleaned = API_KEY_RE.sub("[api key removed]", cleaned)
        notes.append("redacted an API key")
    if "system prompt" in cleaned.lower() and "confidential" in cleaned.lower():
        return None, ["blocked: the draft quoted confidential system text"]
    return cleaned, notes


# Action risk tiers. The tier decides how much freedom the agent gets.
# Anything not listed here is treated as high risk by default: unknown
# actions pause for a human, they do not slip through.
ACTION_TIERS = {
    "lookup_customer": "read",
    "check_calendar": "read",
    "draft_message": "write",
    "update_crm_note": "write",
    "book_appointment": "write",
    "send_message": "external",
    "refund_payment": "money",
    "delete_records": "delete",
    "export_customer_data": "data_export",
}
FREE_TIERS = {"read", "write"}            # run now, still logged
HUMAN_TIERS = {"external", "money", "delete", "data_export"}


def classify_action(action_name):
    return ACTION_TIERS.get(action_name, "unknown")


class ApprovalGate:
    """Mediates every action an agent attempts.

    decide is a callable(action) returning (approved, reason). In the
    demo it is scripted; in production it is a human clicking approve or
    reject in a queue, or a policy engine for the small hours.
    """

    def __init__(self, decide):
        self.decide = decide
        self.audit_log = []

    def attempt(self, action_name, detail=""):
        tier = classify_action(action_name)
        entry = {"action": action_name, "tier": tier, "detail": detail}

        if tier in FREE_TIERS:
            entry["outcome"] = "ran"
            entry["note"] = "free tier: ran immediately, still logged"
        elif tier in HUMAN_TIERS or tier == "unknown":
            approved, reason = self.decide(
                {"action": action_name, "tier": tier, "detail": detail}
            )
            entry["outcome"] = "ran after approval" if approved else "denied"
            entry["note"] = f"human decision: {reason}"
        self.audit_log.append(entry)
        return entry
