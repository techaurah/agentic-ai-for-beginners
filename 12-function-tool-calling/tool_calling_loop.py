"""
Lesson 12: Function/tool calling end to end.

A complete tool-calling loop with a deterministic fake model, so the whole
thing runs offline with the Python standard library only.

The moving parts, in the same shape every real framework uses:
  1. Tools are described to the model as data (name, description, parameters).
  2. The model answers with either a tool call or a final message.
  3. Your code validates and runs the tool call, then feeds the result back.
  4. Repeat until the model answers in plain text (or you hit a step limit).

Run it:  python3 tool_calling_loop.py
"""

import ast
import json
import operator

# ---------------------------------------------------------------------------
# 1. Tools. Each tool is a plain Python function plus a schema describing it.
# ---------------------------------------------------------------------------

FAKE_CALENDAR = {
    "2026-11-06": ["09:00", "10:30", "14:00"],   # Friday
    "2026-11-07": ["11:00"],                      # Saturday
    "2026-11-08": [],                             # Sunday: fully booked
}


def calculator(expression: str) -> dict:
    """Evaluate a basic arithmetic expression safely (no eval())."""
    allowed = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.USub: operator.neg,
    }

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in allowed:
            return allowed[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed:
            return allowed[type(node.op)](walk(node.operand))
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")

    return {"result": walk(ast.parse(expression, mode="eval"))}


def check_calendar(date: str) -> dict:
    """Return the free slots on a date from a fake calendar."""
    if date not in FAKE_CALENDAR:
        return {"date": date, "free_slots": [], "note": "No calendar data for this date."}
    slots = FAKE_CALENDAR[date]
    return {"date": date, "free_slots": slots, "note": f"{len(slots)} slot(s) free."}


def score_lead(budget_usd: int, timeline_days: int, is_decision_maker: bool) -> dict:
    """Score a sales lead from 0-100 with simple, inspectable rules."""
    score = 0
    score += 40 if budget_usd >= 1000 else 20 if budget_usd >= 500 else 5
    score += 35 if timeline_days <= 14 else 20 if timeline_days <= 30 else 5
    score += 25 if is_decision_maker else 5
    band = "hot" if score >= 80 else "warm" if score >= 55 else "cold"
    return {"score": score, "band": band}


TOOLS = {
    "calculator": {
        "fn": calculator,
        "description": "Evaluate an arithmetic expression, e.g. '1250 * 3 + 99'.",
        "parameters": {"expression": "string"},
    },
    "check_calendar": {
        "fn": check_calendar,
        "description": "Look up free appointment slots for a date (YYYY-MM-DD).",
        "parameters": {"date": "string"},
    },
    "score_lead": {
        "fn": score_lead,
        "description": "Score a lead 0-100 from budget, timeline, and decision authority.",
        "parameters": {"budget_usd": "integer", "timeline_days": "integer",
                       "is_decision_maker": "boolean"},
    },
}


# ---------------------------------------------------------------------------
# 2. The fake model. A real model reads the conversation and decides; this
#    one follows fixed rules so every run is identical and easy to follow.
# ---------------------------------------------------------------------------

class FakeModel:
    """A stand-in for an LLM that 'decides' with keyword rules.

    It looks at the original user request, works out which tools are needed,
    and requests them one at a time. When every needed result is in the
    conversation, it writes the final answer from those results.
    """

    def respond(self, messages: list[dict]) -> dict:
        user_text = next(m["content"] for m in messages if m["role"] == "user")
        done = {m["tool"] for m in messages if m["role"] == "tool"}

        plan = []
        if "total" in user_text or "cost" in user_text:
            plan.append(("calculator", {"expression": "1250 * 3 + 99"}))
        if "free" in user_text or "slot" in user_text:
            plan.append(("check_calendar", {"date": "2026-11-06"}))
        if "score" in user_text or "lead" in user_text:
            plan.append(("score_lead", {"budget_usd": 1500, "timeline_days": 10,
                                        "is_decision_maker": True}))

        for name, args in plan:
            if name not in done:
                return {"type": "tool_call", "name": name, "arguments": args}

        # Everything requested is done: compose the final answer from results.
        results = {m["tool"]: m["content"] for m in messages if m["role"] == "tool"}
        parts = []
        if "calculator" in results:
            parts.append(f"the package total is ${results['calculator']['result']}")
        if "check_calendar" in results:
            slots = ", ".join(results["check_calendar"]["free_slots"])
            parts.append(f"Friday 2026-11-06 has free slots at {slots}")
        if "score_lead" in results:
            r = results["score_lead"]
            parts.append(f"the lead scores {r['score']}/100 ({r['band']})")
        return {"type": "final", "text": "Summary: " + "; ".join(parts) + "."}


# ---------------------------------------------------------------------------
# 3. The loop. This is your code in every real agent: validate, run, feed
#    back, and guard against a model that never stops asking for tools.
# ---------------------------------------------------------------------------

def run_agent(user_request: str, max_steps: int = 6) -> str:
    model = FakeModel()
    messages = [{"role": "user", "content": user_request}]
    print(f"USER: {user_request}")

    for step in range(1, max_steps + 1):
        reply = model.respond(messages)

        if reply["type"] == "final":
            print(f"AGENT (step {step}): {reply['text']}")
            return reply["text"]

        name, args = reply["name"], reply["arguments"]
        if name not in TOOLS:
            raise ValueError(f"Model asked for unknown tool: {name}")
        expected = TOOLS[name]["parameters"]
        if set(args) != set(expected):
            raise ValueError(f"Bad arguments for {name}: expected {sorted(expected)}, "
                             f"got {sorted(args)}")
        result = TOOLS[name]["fn"](**args)
        print(f"TOOL (step {step}): {name}({json.dumps(args)}) -> {json.dumps(result)}")
        messages.append({"role": "tool", "tool": name, "content": result})

    raise RuntimeError(f"Step limit of {max_steps} reached without a final answer.")


if __name__ == "__main__":
    print("--- Scenario 1: one tool ---")
    run_agent("What is the total cost of 3 seats?")
    print("\n--- Scenario 2: two tools in one request ---")
    run_agent("Score this lead for me, and check which slots are free on Friday.")
    print("\n--- Scenario 3: all three tools ---")
    run_agent("Give me the total cost, score the lead, and find a free slot.")
