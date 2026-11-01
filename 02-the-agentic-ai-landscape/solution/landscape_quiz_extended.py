"""
Lesson 02 - Exercise solution: a fourth scenario and an approval rule.

Adds the scenario the exercise asks for (clinic reminders where a
human approves every message) and a new rule: when a job needs human
approval before anything is sent, the helper says so on every
recommendation, and the no-code base gains points because approval
steps are a built-in feature of workflow tools.

Run it with:

    python3 landscape_quiz_extended.py
"""

CATEGORIES = [
    "Model API calls only",
    "No-code automation (n8n-style)",
    "Agent framework (code)",
    "Multi-agent system",
]


def score_scenario(scenario):
    scores = {name: 0 for name in CATEGORIES}
    reasons = {name: [] for name in CATEGORIES}

    if scenario["steps_fixed"]:
        scores["No-code automation (n8n-style)"] += 3
        reasons["No-code automation (n8n-style)"].append(
            "The steps are the same on every run, so a drawn workflow is "
            "easier to inspect and maintain than agent reasoning."
        )
        scores["Model API calls only"] += 1

    if scenario["team"] == "operations":
        scores["No-code automation (n8n-style)"] += 3
        reasons["No-code automation (n8n-style)"].append(
            "The team runs operations rather than a codebase, so a visual "
            "workflow is the thing they can actually own."
        )

    if scenario["team"] == "engineering":
        scores["Agent framework (code)"] += 2
        reasons["Agent framework (code)"].append(
            "Engineers can own code, tests, and deployment."
        )
        scores["Multi-agent system"] += 1

    if scenario["judgement_varies"]:
        scores["Agent framework (code)"] += 3
        reasons["Agent framework (code)"].append(
            "The right next step changes from case to case, which is "
            "exactly what the agent loop is for."
        )
        scores["Multi-agent system"] += 2
        scores["No-code automation (n8n-style)"] += 1

    if scenario["multiple_specialists"]:
        scores["Multi-agent system"] += 4
        reasons["Multi-agent system"].append(
            "Distinct specialists handing work to each other is the one "
            "shape multi-agent is genuinely built for."
        )
        scores["Agent framework (code)"] += 1

    if scenario["simple_qa"]:
        scores["Model API calls only"] += 3
        reasons["Model API calls only"].append(
            "One question in, one answer out: anything more is ceremony."
        )
        scores["No-code automation (n8n-style)"] += 1

    # NEW RULE: approval-gated work.
    if scenario.get("needs_human_approval"):
        scores["No-code automation (n8n-style)"] += 2
        reasons["No-code automation (n8n-style)"].append(
            "Workflow tools ship approval steps as a built-in feature, so "
            "the human gate is configuration, not new code."
        )
        for name in CATEGORIES:
            reasons[name].append(
                "Whichever base wins, add a human approval step before "
                "anything is sent to a real person."
            )

    winner = CATEGORIES[0]
    for name in CATEGORIES:
        if scores[name] > scores[winner]:
            winner = name
    return scores, reasons, winner


def report(scenario):
    scores, reasons, winner = score_scenario(scenario)
    print(f"SCENARIO: {scenario['name']}")
    print(f"  The job: {scenario['job']}")
    score_line = " | ".join(f"{name} {scores[name]}" for name in CATEGORIES)
    print(f"  Scores: {score_line}")
    print(f"  Recommendation: {winner}")
    for reason in reasons[winner]:
        print(f"    - {reason}")
    if scenario.get("shared_tools"):
        print(
            "    - Note: whichever base wins, expose the shared tools "
            "through MCP so every agent uses the same tool set."
        )
    print()


SCENARIOS = [
    {
        "name": "Invoice inbox for a small wholesaler",
        "job": "Read invoice emails, extract the totals, and type them "
               "into a spreadsheet. Same steps, every day.",
        "steps_fixed": True, "team": "operations", "judgement_varies": False,
        "multiple_specialists": False, "simple_qa": False,
        "shared_tools": False, "needs_human_approval": False,
    },
    {
        "name": "Research assistant for a consulting team",
        "job": "Given a client question, plan the research, search internal "
               "documents, follow up on gaps, and draft a report. The path "
               "is different every time.",
        "steps_fixed": False, "team": "engineering", "judgement_varies": True,
        "multiple_specialists": False, "simple_qa": False,
        "shared_tools": False, "needs_human_approval": False,
    },
    {
        "name": "Support desk with three specialisms",
        "job": "Billing, technical, and account specialists hand customer "
               "cases to each other until the case is resolved. All three "
               "use the same CRM and calendar tools.",
        "steps_fixed": False, "team": "engineering", "judgement_varies": True,
        "multiple_specialists": True, "simple_qa": False,
        "shared_tools": True, "needs_human_approval": False,
    },
    {
        # NEW SCENARIO added by the exercise.
        "name": "Appointment reminders for a dental clinic",
        "job": "Every morning, find tomorrow's appointments, draft a "
               "reminder for each patient, and send them once a staff "
               "member has approved the batch. Same flow every day, "
               "nothing goes out unapproved.",
        "steps_fixed": True, "team": "operations", "judgement_varies": False,
        "multiple_specialists": False, "simple_qa": False,
        "shared_tools": False, "needs_human_approval": True,
    },
]


def main():
    print("Lesson 02 - Exercise solution: approval-aware recommendations")
    print("=============================================================")
    print()
    for scenario in SCENARIOS:
        report(scenario)


if __name__ == "__main__":
    main()
