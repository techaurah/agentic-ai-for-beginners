"""Lesson 09 demo: the agent loop, perceive, decide, act, observe.

A scripted fake model (clearly labelled, deterministic) drives a real loop
against real tool functions. Swap the fake model for a real LLM and the
loop, the tools, and the safety limits stay exactly the same. That is the
point of the lesson: the loop is the product, the model is a component.

Task: "Book a viewing for lead LP-2026-00042 on Friday afternoon."

Fully offline, standard library only.

Run:  python3 agent_loop.py
"""

MAX_STEPS = 6  # hard stop: an agent that cannot finish in 6 steps stops

# ---------------------------------------------------------------- tools
# Tools are ordinary functions. The agent can only touch the world
# through these, which is what makes the system auditable and safe.

CALENDAR = {
    "friday": ["09:00", "14:00", "16:30"],
    "saturday": ["10:00"],
}
BOOKINGS = []


def check_availability(day: str) -> dict:
    free = [slot for slot in CALENDAR.get(day.lower(), []) if slot not in BOOKINGS]
    return {"day": day, "free_slots": free}


def book_appointment(day: str, time: str, lead_id: str) -> dict:
    slot = f"{day} {time}"
    if slot in BOOKINGS:
        return {"ok": False, "error": f"{slot} is already booked"}
    BOOKINGS.append(slot)
    return {"ok": True, "confirmation": f"BK-1042", "slot": slot, "lead_id": lead_id}


TOOLS = {"check_availability": check_availability, "book_appointment": book_appointment}


# ---------------------------------------------------------------- model
class ScriptedModel:
    """A fake model with a fixed script, standing in for an LLM.

    A real model would choose the same actions from the task text and the
    observations. The script keeps the lesson deterministic: same run,
    same trace, every time. It is a test double, not a shortcut in the
    architecture.
    """

    def __init__(self, task: str):
        self.task = task
        self.step = 0

    def decide(self, observation: dict | None) -> dict:
        self.step += 1
        if self.step == 1:
            return {
                "thought": "I need a free Friday afternoon slot before I can book.",
                "tool": "check_availability",
                "args": {"day": "friday"},
            }
        if self.step == 2:
            free = observation["free_slots"]
            afternoon = [s for s in free if s >= "12:00"]
            slot = afternoon[0]
            return {
                "thought": f"Friday has free slots {free}. {slot} is the first afternoon slot.",
                "tool": "book_appointment",
                "args": {"day": "friday", "time": slot, "lead_id": "LP-2026-00042"},
            }
        return {
            "thought": "The booking is confirmed. Nothing else is needed.",
            "final": (
                f"Booked LP-2026-00042 into {observation['slot']} "
                f"(confirmation {observation['confirmation']})."
            ),
        }


# ---------------------------------------------------------------- loop
def run_agent(task: str) -> str:
    print(f"task: {task}")
    model = ScriptedModel(task)
    observation = None

    for step in range(1, MAX_STEPS + 1):
        print(f"\n[step {step}] PERCEIVE: observation = {observation}")
        decision = model.decide(observation)
        print(f"[step {step}] DECIDE:   {decision['thought']}")

        if "final" in decision:
            print(f"[step {step}] FINISH:   {decision['final']}")
            return decision["final"]

        tool_name = decision["tool"]
        print(f"[step {step}] ACT:      {tool_name}({decision['args']})")
        observation = TOOLS[tool_name](**decision["args"])
        print(f"[step {step}] OBSERVE:  {observation}")

    raise RuntimeError(f"agent did not finish within {MAX_STEPS} steps; stopped")


if __name__ == "__main__":
    run_agent("Book a viewing for lead LP-2026-00042 on Friday afternoon.")
