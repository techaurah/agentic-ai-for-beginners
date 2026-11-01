"""A miniature outcome-assertion test harness for agents.

Run it:

    python3 harness.py

It plays every scenario in scenarios.py against two variants of the agent
in agent.py: the careful one, which must pass everything, and a buggy one
with three realistic defects, which must not. The point of the lesson:
an agent test suite earns its keep by failing loudly on bad behaviour,
not by passing politely on good behaviour.

The harness checks outcomes only (stage, fields, tool calls, bookings,
score, hard content rules). It never scores how a reply "reads". Wording
quality is a job for the judge-and-review methods in Lesson 25.
"""

from agent import FrontDeskAgent
from scenarios import SCENARIOS


def check(assertion, transcript):
    """Return (passed, message). Message explains any failure plainly."""
    kind = assertion[0]

    if kind == "stage_is":
        ok = transcript["stage"] == assertion[1]
        return ok, f"stage is {transcript['stage']!r}, expected {assertion[1]!r}"
    if kind == "field_present":
        ok = assertion[1] in transcript["fields"]
        return ok, f"field {assertion[1]!r} was not captured"
    if kind == "tool_called":
        ok = assertion[1] in transcript["tool_calls"]
        return ok, f"tool {assertion[1]!r} was never called"
    if kind == "tool_calls_at_most":
        count = transcript["tool_calls"].count(assertion[1])
        ok = count <= assertion[2]
        return (
            ok,
            f"tool {assertion[1]!r} was called {count} times, "
            f"budget is {assertion[2]}",
        )
    if kind == "booked_hour_is":
        ok = transcript["booked_hour"] == assertion[1]
        return ok, f"booked hour is {transcript['booked_hour']}, expected {assertion[1]}"
    if kind == "booked_hour_is_not":
        ok = transcript["booked_hour"] != assertion[1]
        return ok, f"booked hour {assertion[1]} must never be booked"
    if kind == "no_booking":
        ok = transcript["booked_hour"] is None
        return ok, f"expected no booking, but hour {transcript['booked_hour']} was booked"
    if kind == "score_is":
        ok = transcript["score"] == assertion[1]
        return ok, f"score is {transcript['score']}, expected {assertion[1]}"
    if kind == "reply_contains":
        ok = assertion[1].lower() in transcript["reply_text"]
        return ok, f"no reply contains {assertion[1]!r}"
    if kind == "reply_excludes":
        ok = assertion[1].lower() not in transcript["reply_text"]
        return ok, f"a reply contains forbidden text {assertion[1]!r}"
    raise ValueError(f"unknown assertion kind: {kind}")


def run_scenario(agent, scenario):
    """Play the scripted turns and evaluate every assertion."""
    for turn in scenario["turns"]:
        agent.handle(turn)
    transcript = agent.transcript()
    failures = []
    for assertion in scenario["assertions"]:
        passed, message = check(assertion, transcript)
        if not passed:
            failures.append(f"{assertion[0]}: {message}")
    return failures


def run_suite(label, agent_factory):
    print(f"Suite: {label}")
    scenarios_passed = 0
    assertions_failed = 0
    for scenario in SCENARIOS:
        agent = agent_factory()
        failures = run_scenario(agent, scenario)
        total = len(scenario["assertions"])
        if failures:
            assertions_failed += len(failures)
            print(f"  [FAIL] {scenario['name']}: {scenario['title']}")
            for failure in failures:
                print(f"         - {failure}")
            print(f"         ({total - len(failures)}/{total} assertions passed)")
        else:
            scenarios_passed += 1
            print(f"  [PASS] {scenario['name']}: {scenario['title']} ({total} assertions)")
    print(
        f"  Result: {scenarios_passed}/{len(SCENARIOS)} scenarios passed, "
        f"{assertions_failed} assertions failed"
    )
    print()
    return scenarios_passed, assertions_failed


def main():
    good_passed, good_failed = run_suite(
        "careful agent (must pass everything)",
        lambda: FrontDeskAgent(buggy=False),
    )
    buggy_passed, buggy_failed = run_suite(
        "buggy agent (must not pass)",
        lambda: FrontDeskAgent(buggy=True),
    )

    suite_works = good_failed == 0 and buggy_failed > 0
    print(
        "Demo verdict: "
        + (
            "the careful agent passes the whole suite, and the suite "
            f"catches the buggy agent red-handed ({buggy_failed} failed "
            "assertions). That is what an outcome test is for."
            if suite_works
            else "something is wrong with the suite itself."
        )
    )
    return 0 if suite_works else 1


if __name__ == "__main__":
    raise SystemExit(main())
