"""
Lesson 02 - The landscape, as a decision helper.

Run it with:

    python3 landscape_quiz.py                # three worked scenarios
    python3 landscape_quiz.py --interactive  # answer for your own project

Most "which framework should I use?" arguments go wrong because the
honest answer depends on the shape of the job, not on the tools. This
script scores four bases (plain model calls, a no-code workflow, an
agent framework in code, a multi-agent system) against five questions
about the job, and explains its recommendation.
"""

import sys

CATEGORIES = [
    "Model API calls only",
    "No-code automation (n8n-style)",
    "Agent framework (code)",
    "Multi-agent system",
]


def score_scenario(scenario):
    """Score each base against the shape of the job. Returns everything."""
    scores = {name: 0 for name in CATEGORIES}
    reasons = {name: [] for name in CATEGORIES}

    if scenario["steps_fixed"]:
        scores["No-code automation (n8n-style)"] += 3
        reasons["No-code automation (n8n-style)"].append(
            "The steps are the same on every run, so a drawn workflow is "
            "easier to inspect and maintain than agent reasoning."
        )
        scores["Model API calls only"] += 1
        reasons["Model API calls only"].append(
            "Fixed steps can also live in ordinary code with a model call inside."
        )

    if scenario["team"] == "operations":
        scores["No-code automation (n8n-style)"] += 3
        reasons["No-code automation (n8n-style)"].append(
            "The team runs operations rather than a codebase, so a visual "
            "workflow is the thing they can actually own."
        )

    if scenario["team"] == "engineering":
        scores["Agent framework (code)"] += 2
        reasons["Agent framework (code)"].append(
            "Engineers can own code, tests, and deployment, so a framework "
            "gives control without fighting the tool."
        )
        scores["Multi-agent system"] += 1
        reasons["Multi-agent system"].append(
            "An engineering team can absorb the extra moving parts."
        )

    if scenario["judgement_varies"]:
        scores["Agent framework (code)"] += 3
        reasons["Agent framework (code)"].append(
            "The right next step changes from case to case, which is "
            "exactly what the agent loop is for."
        )
        scores["Multi-agent system"] += 2
        reasons["Multi-agent system"].append(
            "Varying judgement is a prerequisite for multi-agent to pay off."
        )
        scores["No-code automation (n8n-style)"] += 1
        reasons["No-code automation (n8n-style)"].append(
            "A workflow can still host an AI step for the judgement calls."
        )

    if scenario["multiple_specialists"]:
        scores["Multi-agent system"] += 4
        reasons["Multi-agent system"].append(
            "Distinct specialists handing work to each other is the one "
            "shape multi-agent is genuinely built for."
        )
        scores["Agent framework (code)"] += 1
        reasons["Agent framework (code)"].append(
            "A single agent with good tools covers some of this, more simply."
        )

    if scenario["simple_qa"]:
        scores["Model API calls only"] += 3
        reasons["Model API calls only"].append(
            "One question in, one answer out: anything more is ceremony."
        )
        scores["No-code automation (n8n-style)"] += 1
        reasons["No-code automation (n8n-style)"].append(
            "A workflow adds scheduling and integrations if you need them."
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
        "steps_fixed": True,
        "team": "operations",
        "judgement_varies": False,
        "multiple_specialists": False,
        "simple_qa": False,
        "shared_tools": False,
    },
    {
        "name": "Research assistant for a consulting team",
        "job": "Given a client question, plan the research, search internal "
               "documents, follow up on gaps, and draft a report. The path "
               "is different every time.",
        "steps_fixed": False,
        "team": "engineering",
        "judgement_varies": True,
        "multiple_specialists": False,
        "simple_qa": False,
        "shared_tools": False,
    },
    {
        "name": "Support desk with three specialisms",
        "job": "Billing, technical, and account specialists hand customer "
               "cases to each other until the case is resolved. All three "
               "use the same CRM and calendar tools.",
        "steps_fixed": False,
        "team": "engineering",
        "judgement_varies": True,
        "multiple_specialists": True,
        "simple_qa": False,
        "shared_tools": True,
    },
]


def ask(prompt, choices):
    while True:
        answer = input(prompt).strip().lower()
        if answer in choices:
            return answer
        print(f"  Please answer one of: {', '.join(choices)}")


def interactive():
    print("Answer five questions about your project.\n")
    steps_fixed = ask("1. Are the steps the same on every run? (y/n) ", ["y", "n"]) == "y"
    team = ask("2. Who maintains it? (ops/eng) ", ["ops", "eng"])
    judgement = ask("3. Does the right next step change case by case? (y/n) ", ["y", "n"]) == "y"
    specialists = ask("4. Do several specialists hand work to each other? (y/n) ", ["y", "n"]) == "y"
    simple = ask("5. Is it basically one question in, one answer out? (y/n) ", ["y", "n"]) == "y"
    scenario = {
        "name": "Your project",
        "job": "Scored from your answers above.",
        "steps_fixed": steps_fixed,
        "team": "operations" if team == "ops" else "engineering",
        "judgement_varies": judgement,
        "multiple_specialists": specialists,
        "simple_qa": simple,
        "shared_tools": False,
    }
    print()
    report(scenario)


def main():
    if "--interactive" in sys.argv:
        interactive()
        return
    print("Lesson 02 - Which base does this job need?")
    print("==========================================")
    print()
    for scenario in SCENARIOS:
        report(scenario)
    print("Run with --interactive to score your own project.")


if __name__ == "__main__":
    main()
