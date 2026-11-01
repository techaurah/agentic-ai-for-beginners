"""Lesson 10 demo: agent architectures compared on the same task.

One task, three architectures, one scripted fake model underneath all of
them (deterministic, clearly labelled). What changes is the STRUCTURE:
who decides, in what order, and how many model calls it costs.

Task: handle a new enquiry end to end: classify it, check the calendar,
draft a reply.

  1. single agent   one loop does everything
  2. pipeline       fixed stages, no loop, no choices
  3. supervisor     a coordinator delegates to two worker agents

Fully offline, standard library only.

Run:  python3 architectures.py
"""

ENQUIRY = {
    "name": "Ayesha Khan",
    "message": "I have tooth pain and need an emergency appointment this week.",
}
FREE_SLOTS = ["Fri 09:00", "Fri 14:00", "Fri 16:30"]

model_calls = 0  # the shared fake model counts every call, whoever makes it


def fake_model(job: str, payload: str) -> str:
    """One deterministic stand-in for every LLM call in this lesson."""
    global model_calls
    model_calls += 1
    if job == "classify":
        return "booking"
    if job == "draft":
        return (
            "Hi Ayesha, sorry to hear that. We have emergency slots "
            "this week (Fri 14:00 is free). Reply to confirm."
        )
    raise ValueError(job)


def check_calendar() -> list:
    return FREE_SLOTS  # a tool, not a model call


# ------------------------------------------------------- 1. single agent
def single_agent(enquiry: dict) -> dict:
    """One loop perceives, decides, acts. Flexible, but every step is a
    model call and the model can wander off the path."""
    global model_calls
    model_calls = 0
    steps = []
    category = fake_model("classify", enquiry["message"])
    steps.append(f"classify -> {category}")
    slots = check_calendar()
    steps.append(f"check_calendar -> {len(slots)} free slots")
    reply = fake_model("draft", category)
    steps.append("draft reply")
    return report("single agent", steps, reply)


# ---------------------------------------------------------- 2. pipeline
def pipeline(enquiry: dict) -> dict:
    """Fixed stages in a fixed order. No loop, no judgement calls, the
    cheapest and most predictable shape. Also the least flexible."""
    global model_calls
    model_calls = 0
    steps = []
    category = fake_model("classify", enquiry["message"])
    steps.append(f"stage 1 classify -> {category}")
    slots = check_calendar()
    steps.append(f"stage 2 check_calendar -> {len(slots)} free slots")
    reply = fake_model("draft", category)
    steps.append("stage 3 draft reply")
    return report("pipeline", steps, reply)


# -------------------------------------------------------- 3. supervisor
def worker_agent(role: str, enquiry: dict) -> str:
    """Workers are small agents with one job each."""
    if role == "classifier":
        return fake_model("classify", enquiry["message"])
    if role == "drafter":
        return fake_model("draft", "booking")
    raise ValueError(role)


def supervisor(enquiry: dict) -> dict:
    """The supervisor model plans and delegates; workers execute.
    Coordination costs extra model calls, and buys specialisation."""
    global model_calls
    model_calls = 0
    steps = []
    model_calls += 1  # the supervisor's own planning call
    steps.append("supervisor plans: classify, check calendar, draft")
    category = worker_agent("classifier", enquiry)
    steps.append(f"delegate to classifier worker -> {category}")
    slots = check_calendar()
    steps.append(f"check_calendar tool -> {len(slots)} free slots")
    reply = worker_agent("drafter", enquiry)
    steps.append("delegate to drafter worker -> reply ready")
    return report("supervisor", steps, reply)


def report(name: str, steps: list, reply: str) -> dict:
    print(f"\n=== {name} ===")
    for step in steps:
        print(f"  {step}")
    print(f"  model calls: {model_calls}")
    print(f"  result: {reply}")
    return {"architecture": name, "model_calls": model_calls}


if __name__ == "__main__":
    results = [single_agent(ENQUIRY), pipeline(ENQUIRY), supervisor(ENQUIRY)]
    print("\n=== summary ===")
    for result in results:
        print(f"  {result['architecture']:<14} model calls: {result['model_calls']}")
