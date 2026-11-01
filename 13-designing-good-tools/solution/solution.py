"""
Lesson 13 exercise solution: a send_reminder tool with the same three
design rules (schema contract, errors as data, idempotency).

The failure this prevents: an agent retries a reminder after a timeout
and the customer gets the same text three times. With an idempotency
key derived from the appointment, every retry returns the first send.

Run it:  python3 solution.py
"""

import hashlib
import json

SENT: list[dict] = []            # the "sent messages" log (a stand-in inbox)
KEYS: dict[str, dict] = {}       # idempotency_key -> original result


def ok(data: dict) -> dict:
    return {"ok": True, "data": data}


def err(code: str, message: str, retryable: bool) -> dict:
    return {"ok": False, "error": {"code": code, "message": message,
                                    "retryable": retryable}}


SCHEMA = {
    "channel": ("string", True, ["sms", "email"]),
    "to": ("string", True, None),
    "message": ("string", True, None),
    "appointment_id": ("string", True, None),
}


def validate(schema: dict, args: dict) -> dict | None:
    for field, (type_name, required, enum) in schema.items():
        if field not in args:
            if required:
                return err("missing_argument", f"'{field}' is required.", True)
            continue
        if enum and args[field] not in enum:
            return err("invalid_value",
                       f"'{field}' must be one of {enum}, got '{args[field]}'.", True)
    return None


def send_reminder(args: dict) -> dict:
    problem = validate(SCHEMA, args)
    if problem:
        return problem

    # The key comes from the appointment, not from the caller: the same
    # appointment can never produce two reminders, whoever asks.
    key = "reminder:" + args["appointment_id"]
    if key in KEYS:
        return ok({**KEYS[key], "note": "Idempotent replay: reminder already sent."})

    message_id = "MSG-" + hashlib.sha256(key.encode()).hexdigest()[:6].upper()
    record = {"message_id": message_id, "channel": args["channel"],
              "to": args["to"], "appointment_id": args["appointment_id"]}
    SENT.append(record)
    KEYS[key] = record
    return ok(record)


if __name__ == "__main__":
    reminder = {"channel": "sms", "to": "+1-555-0100",
                "message": "Reminder: cleaning on Friday at 09:00.",
                "appointment_id": "BK-7144CE"}

    print("First send:      ", json.dumps(send_reminder(reminder)))
    print("Retry (timeout): ", json.dumps(send_reminder(reminder)))
    print("Retry (loop):    ", json.dumps(send_reminder(reminder)))
    print(f"Messages actually sent: {len(SENT)}")
    print("Bad channel:     ",
          json.dumps(send_reminder({**reminder, "channel": "pigeon",
                                    "appointment_id": "BK-999"})))
