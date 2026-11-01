"""
Lesson 21: Roles and handoffs.

Multi-agent systems fail at the seams: one agent finishes, the next one
starts with half the context, a guessed format, or data it should never
have seen. This lesson treats the seam as a contract:

  - a RoleSpec says what a role is responsible for, what it may receive,
    what it must produce, and which tools it may use;
  - a Handoff is validated against the receiving role's contract before
    the receiving agent ever runs.

Pure Python, no framework. Frameworks give you the plumbing; the
contract discipline is yours to design.

Run:  python3 handoffs.py
"""

from dataclasses import dataclass, field


class HandoffError(Exception):
    """Raised when a handoff payload breaks the receiving role's contract."""


@dataclass
class RoleSpec:
    name: str
    mission: str
    accepts: dict          # field name -> type description, all required
    produces: list         # field names this role guarantees in its output
    tools: list            # tools this role is allowed to call
    never_receive: list = field(default_factory=list)  # least-privilege list


# --- Two roles in a small service-business pipeline ---------------------------

INTAKE = RoleSpec(
    name="IntakeAgent",
    mission="Talk to the customer, understand the job, capture the facts.",
    accepts={"customer_message": "string"},
    produces=["customer_name", "job_type", "urgency", "summary"],
    tools=["classify_message", "lookup_customer"],
)

SCHEDULER = RoleSpec(
    name="SchedulingAgent",
    mission="Turn a qualified enquiry into a booked visit.",
    accepts={
        "customer_name": "string",
        "job_type": "string",
        "urgency": "string: low | normal | high",
        "summary": "string",
    },
    produces=["proposed_slot", "booking_reference"],
    tools=["check_calendar", "book_appointment"],
    never_receive=["card_number", "password", "payment_details"],
)

ROLES = {role.name: role for role in (INTAKE, SCHEDULER)}


# --- Handoff validation -------------------------------------------------------

def validate_handoff(target_role, payload):
    """Check a payload against the target role's contract.

    Returns a list of problems. Empty list means the handoff may proceed.
    """
    problems = []
    for field_name in target_role.accepts:
        if field_name not in payload:
            problems.append(f"missing required field: {field_name}")
        elif not str(payload[field_name]).strip():
            problems.append(f"empty required field: {field_name}")
    for field_name in target_role.never_receive:
        if field_name in payload:
            problems.append(
                f"forbidden field for {target_role.name}: {field_name} "
                f"(least privilege: this role never needs it)"
            )
    return problems


def handoff(from_role, to_role_name, payload):
    target = ROLES[to_role_name]
    print(f"\nHANDOFF {from_role.name} -> {to_role_name}")
    print(f"  payload fields: {sorted(payload)}")
    problems = validate_handoff(target, payload)
    if problems:
        for problem in problems:
            print(f"  x REJECTED: {problem}")
        raise HandoffError(f"{to_role_name} refused the handoff")
    print("  ok contract satisfied, receiving agent may start")
    return payload


# --- The agents (deterministic stand-ins for LLM-driven roles) ----------------

def intake_agent(message):
    print(f'INTAKE received: "{message}"')
    lowered = message.lower()
    urgent_words = ("leak", "burst", "freezing", "no heating", "no hot water")
    urgency = "high" if any(w in lowered for w in urgent_words) else "normal"
    job_type = "boiler repair" if "boiler" in lowered else "general enquiry"
    return {
        "customer_name": "Mrs Carter",
        "job_type": job_type,
        "urgency": urgency,
        "summary": message,
    }


def scheduling_agent(enquiry):
    slot = "tomorrow 09:00" if enquiry["urgency"] == "high" else "Thursday 13:00"
    return {"proposed_slot": slot, "booking_reference": "NB-1042"}


def main():
    print("Role contracts:")
    for role in ROLES.values():
        print(f"  {role.name}: {role.mission}")
        print(f"    accepts={list(role.accepts)} produces={role.produces} tools={role.tools}")

    # A clean run: intake produces exactly what the scheduler accepts.
    enquiry = intake_agent("My boiler has stopped and the house is freezing")
    enquiry = handoff(INTAKE, "SchedulingAgent", enquiry)
    booking = scheduling_agent(enquiry)
    print(f"SCHEDULER produced: {booking}")

    # A sloppy run: a rushed integration passes raw form data, including
    # a payment field the scheduler must never see, and drops urgency.
    sloppy = {
        "customer_name": "Mr Osei",
        "job_type": "boiler repair",
        "summary": "Boiler stopped",
        "card_number": "4242 4242 4242 4242",
    }
    try:
        handoff(INTAKE, "SchedulingAgent", sloppy)
    except HandoffError as error:
        print(f"\nPipeline stopped safely: {error}")
        print("Nothing downstream ran on bad or forbidden data.")


if __name__ == "__main__":
    main()
