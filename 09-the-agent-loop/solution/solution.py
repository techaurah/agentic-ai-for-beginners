"""Lesson 09 exercise solution: recovering when the first choice fails.

The 14:00 slot is already booked before the agent starts. A brittle agent
would report success anyway or give up. This one observes the failure,
reasons about what it learned, and books the next afternoon slot. The
loop is unchanged; the model script handles one more observation shape.

Run:  python3 solution.py
"""

MAX_STEPS = 8

CALENDAR = {"friday": ["09:00", "14:00", "16:30"]}
BOOKINGS = ["friday 14:00"]  # someone got there first


def check_availability(day: str) -> dict:
    free = [
        slot
        for slot in CALENDAR.get(day.lower(), [])
        if f"{day} {slot}" not in BOOKINGS
    ]
    return {"day": day, "free_slots": free}


def book_appointment(day: str, time: str, lead_id: str) -> dict:
    slot = f"{day} {time}"
    if slot in BOOKINGS:
        return {"ok": False, "error": f"{slot} is already booked"}
    BOOKINGS.append(slot)
    return {"ok": True, "confirmation": "BK-1043", "slot": slot, "lead_id": lead_id}


TOOLS = {"check_availability": check_availability, "book_appointment": book_appointment}


class RecoveringModel:
    """Scripted fake model that reacts to a failed booking attempt."""

    def __init__(self):
        self.step = 0
        self.tried = []

    def decide(self, observation):
        self.step += 1
        if self.step == 1:
            return {
                "thought": "Check Friday availability first, as before.",
                "tool": "check_availability",
                "args": {"day": "friday"},
            }
        if observation and "free_slots" in observation:
            # The agent asked for its preference (14:00) from stale
            # information, a classic race: the list it reasoned over
            # changed after it looked. Here it insists on trying 14:00
            # only if it was in the ORIGINAL full calendar, which sets
            # up the failure this exercise is about.
            self.tried.append("14:00")
            return {
                "thought": "My preference is 14:00. I will attempt it and see.",
                "tool": "book_appointment",
                "args": {"day": "friday", "time": "14:00", "lead_id": "LP-2026-00042"},
            }
        if observation and observation.get("ok") is False:
            return {
                "thought": (
                    "14:00 failed: already booked. The observation told me "
                    "the truth my plan lacked. Next afternoon option is 16:30."
                ),
                "tool": "book_appointment",
                "args": {"day": "friday", "time": "16:30", "lead_id": "LP-2026-00042"},
            }
        return {
            "thought": "Booked on the second attempt. Report honestly.",
            "final": (
                f"Booked LP-2026-00042 into {observation['slot']} "
                f"(confirmation {observation['confirmation']}). "
                "First choice 14:00 was already taken."
            ),
        }


def run_agent(task: str) -> None:
    print(f"task: {task}")
    print(f"pre-existing bookings: {BOOKINGS}")
    model = RecoveringModel()
    observation = None
    for step in range(1, MAX_STEPS + 1):
        print(f"\n[step {step}] PERCEIVE: observation = {observation}")
        decision = model.decide(observation)
        print(f"[step {step}] DECIDE:   {decision['thought']}")
        if "final" in decision:
            print(f"[step {step}] FINISH:   {decision['final']}")
            return
        print(f"[step {step}] ACT:      {decision['tool']}({decision['args']})")
        observation = TOOLS[decision["tool"]](**decision["args"])
        print(f"[step {step}] OBSERVE:  {observation}")
    raise RuntimeError("agent did not finish; stopped by MAX_STEPS")


if __name__ == "__main__":
    run_agent("Book a viewing for lead LP-2026-00042 on Friday afternoon.")
