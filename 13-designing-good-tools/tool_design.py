"""
Lesson 13: Designing tools agents can actually use.

Three design rules, each demonstrated in code:
  1. Schemas are contracts. Validate every argument before the tool runs,
     and say exactly what was wrong when validation fails.
  2. Errors are data. A tool returns a structured error the model can act
     on ("slot_taken, try another slot") instead of raising and killing
     the conversation.
  3. Writes need idempotency. If the model retries a booking with the same
     idempotency key, the tool returns the original result instead of
     booking twice.

Run it:  python3 tool_design.py
"""

import hashlib
import json

# ---------------------------------------------------------------------------
# A small tool framework: schema, validation, structured results.
# ---------------------------------------------------------------------------

def ok(data: dict) -> dict:
    return {"ok": True, "data": data}


def err(code: str, message: str, retryable: bool) -> dict:
    """A structured error a model can reason about and recover from."""
    return {"ok": False, "error": {"code": code, "message": message,
                                    "retryable": retryable}}


def validate(schema: dict, args: dict) -> dict | None:
    """Return an error dict if args break the schema, else None.

    Schema format: {field: (type_name, required, enum_or_None)}
    """
    for field, (type_name, required, enum) in schema.items():
        if field not in args:
            if required:
                return err("missing_argument",
                           f"'{field}' is required. Provide it and retry.", True)
            continue
        value = args[field]
        type_ok = {"string": str, "integer": int, "boolean": bool}[type_name]
        if not isinstance(value, type_ok) or (type_name == "integer" and isinstance(value, bool)):
            return err("wrong_type",
                       f"'{field}' must be a {type_name}, got {type(value).__name__}.", True)
        if enum and value not in enum:
            return err("invalid_value",
                       f"'{field}' must be one of {enum}, got '{value}'.", True)
    extra = set(args) - set(schema)
    if extra:
        return err("unknown_argument",
                   f"Unknown argument(s): {sorted(extra)}. Remove them and retry.", True)
    return None


# ---------------------------------------------------------------------------
# The tool: book_appointment, designed properly.
# ---------------------------------------------------------------------------

BOOKINGS: dict[str, dict] = {}          # booking_id -> booking
IDEMPOTENCY_KEYS: dict[str, str] = {}   # idempotency_key -> booking_id
TAKEN_SLOTS = {("2026-11-06", "09:00")}  # already booked by someone else

BOOK_APPOINTMENT_SCHEMA = {
    "date": ("string", True, None),
    "time": ("string", True, None),
    "service": ("string", True, ["cleaning", "checkup", "consultation"]),
    "customer": ("string", True, None),
    "idempotency_key": ("string", True, None),
}


def book_appointment(args: dict) -> dict:
    # Rule 1: the schema is a contract. Nothing runs until arguments conform.
    problem = validate(BOOK_APPOINTMENT_SCHEMA, args)
    if problem:
        return problem

    # Rule 3: a retry with the same key returns the original booking.
    key = args["idempotency_key"]
    if key in IDEMPOTENCY_KEYS:
        original = BOOKINGS[IDEMPOTENCY_KEYS[key]]
        return ok({**original, "note": "Idempotent replay: this booking already existed."})

    # Rule 2: a business-rule failure is data, not an exception.
    if (args["date"], args["time"]) in TAKEN_SLOTS:
        return err("slot_taken",
                   f"{args['date']} at {args['time']} is already booked. "
                   "Check availability and offer a different slot.", True)

    booking_id = "BK-" + hashlib.sha256(key.encode()).hexdigest()[:6].upper()
    booking = {"booking_id": booking_id, "date": args["date"], "time": args["time"],
               "service": args["service"], "customer": args["customer"],
               "status": "confirmed"}
    BOOKINGS[booking_id] = booking
    IDEMPOTENCY_KEYS[key] = booking_id
    TAKEN_SLOTS.add((args["date"], args["time"]))
    return ok(booking)


if __name__ == "__main__":
    good = {"date": "2026-11-06", "time": "10:30", "service": "checkup",
            "customer": "Amara", "idempotency_key": "req-001"}

    print("1. Missing argument (no date):")
    bad = {k: v for k, v in good.items() if k != "date"}
    print("  ", json.dumps(book_appointment(bad)))

    print("2. Invalid value (service not in the enum):")
    print("  ", json.dumps(book_appointment({**good, "service": "surgery"})))

    print("3. Valid booking:")
    first = book_appointment(good)
    print("  ", json.dumps(first))

    print("4. The model retries the exact same request (network hiccup, retry loop):")
    print("  ", json.dumps(book_appointment(good)))
    print(f"   Bookings stored: {len(BOOKINGS)} (still 1: no double booking)")

    print("5. A different customer tries the same slot with a new key:")
    other = {**good, "customer": "Ben", "idempotency_key": "req-002"}
    print("  ", json.dumps(book_appointment(other)))
