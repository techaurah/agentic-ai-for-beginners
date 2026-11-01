"""
Lesson 21 exercise solution: add a third role, FollowUpAgent.

The follow-up role receives the booking output plus the minimum customer
context it needs, and produces a follow-up plan. Its contract shows the
two contract moves that matter in practice: it accepts the scheduler's
produced fields (contracts chain), and it refuses raw contact details
beyond what follow-up messaging actually needs.

Run:  python3 solution.py
"""

from dataclasses import dataclass, field


class HandoffError(Exception):
    pass


@dataclass
class RoleSpec:
    name: str
    mission: str
    accepts: dict
    produces: list
    tools: list
    never_receive: list = field(default_factory=list)


SCHEDULER = RoleSpec(
    name="SchedulingAgent",
    mission="Turn a qualified enquiry into a booked visit.",
    accepts={"customer_name": "string", "job_type": "string",
             "urgency": "string", "summary": "string"},
    produces=["proposed_slot", "booking_reference"],
    tools=["check_calendar", "book_appointment"],
    never_receive=["card_number", "password", "payment_details"],
)

FOLLOW_UP = RoleSpec(
    name="FollowUpAgent",
    mission="Confirm the booking with the customer and schedule a "
            "post-visit satisfaction check.",
    accepts={
        "customer_name": "string",
        "proposed_slot": "string",
        "booking_reference": "string",
    },
    produces=["confirmation_message", "follow_up_time"],
    tools=["send_message", "schedule_reminder"],
    never_receive=["card_number", "payment_details", "internal_notes"],
)

ROLES = {r.name: r for r in (SCHEDULER, FOLLOW_UP)}


def validate_handoff(target_role, payload):
    problems = []
    for field_name in target_role.accepts:
        if field_name not in payload:
            problems.append(f"missing required field: {field_name}")
        elif not str(payload[field_name]).strip():
            problems.append(f"empty required field: {field_name}")
    for field_name in target_role.never_receive:
        if field_name in payload:
            problems.append(f"forbidden field for {target_role.name}: {field_name}")
    return problems


def handoff(from_name, to_role_name, payload):
    target = ROLES[to_role_name]
    print(f"\nHANDOFF {from_name} -> {to_role_name}: fields {sorted(payload)}")
    problems = validate_handoff(target, payload)
    if problems:
        for problem in problems:
            print(f"  x REJECTED: {problem}")
        raise HandoffError(f"{to_role_name} refused the handoff")
    print("  ok contract satisfied")
    return payload


def follow_up_agent(booking):
    message = (
        f"Hello {booking['customer_name']}, your visit is confirmed for "
        f"{booking['proposed_slot']} (ref {booking['booking_reference']}). "
        f"Reply to this message if you need to move it."
    )
    return {"confirmation_message": message, "follow_up_time": "visit + 24h"}


def main():
    booking = {
        "customer_name": "Mrs Carter",
        "proposed_slot": "tomorrow 09:00",
        "booking_reference": "NB-1042",
    }
    accepted = handoff("SchedulingAgent", "FollowUpAgent", dict(booking))
    print(f"FOLLOW-UP produced: {follow_up_agent(accepted)}")

    # The scheduler's working payload includes internal notes. Forwarding
    # the whole dict is the lazy integration, and the contract stops it.
    leaky = dict(booking)
    leaky["internal_notes"] = "Customer sounded stressed; price sensitive."
    try:
        handoff("SchedulingAgent", "FollowUpAgent", leaky)
    except HandoffError as error:
        print(f"\nPipeline stopped safely: {error}")
        print("Fix: forward only the fields the contract accepts.")


if __name__ == "__main__":
    main()
