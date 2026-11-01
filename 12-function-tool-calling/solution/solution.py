"""
Lesson 12 exercise solution: add a fourth tool to the loop.

Adds convert_currency (with fake, fixed exchange rates) and teaches the
fake model to use it when the request mentions a currency conversion.
The loop itself does not change at all: that is the point of the design.
Adding a tool means adding one function, one schema entry, and one
decision rule in the model.

Run it:  python3 solution.py
"""

import ast
import json
import operator

FAKE_RATES = {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "AED": 3.67}


def calculator(expression: str) -> dict:
    allowed = {ast.Add: operator.add, ast.Sub: operator.sub,
               ast.Mult: operator.mul, ast.Div: operator.truediv,
               ast.USub: operator.neg}

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


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert an amount using fixed teaching rates (not live FX data)."""
    if from_currency not in FAKE_RATES or to_currency not in FAKE_RATES:
        return {"error": f"Unknown currency. Known: {sorted(FAKE_RATES)}"}
    usd = amount / FAKE_RATES[from_currency]
    converted = round(usd * FAKE_RATES[to_currency], 2)
    return {"amount": amount, "from": from_currency, "to": to_currency,
            "converted": converted}


TOOLS = {
    "calculator": {
        "fn": calculator, "description": "Evaluate an arithmetic expression.",
        "parameters": {"expression": "string"},
    },
    "convert_currency": {
        "fn": convert_currency,
        "description": "Convert an amount between currencies (teaching rates).",
        "parameters": {"amount": "number", "from_currency": "string",
                       "to_currency": "string"},
    },
}


class FakeModel:
    def respond(self, messages: list[dict]) -> dict:
        user_text = next(m["content"] for m in messages if m["role"] == "user")
        done = {m["tool"] for m in messages if m["role"] == "tool"}
        plan = []
        if "total" in user_text or "cost" in user_text:
            plan.append(("calculator", {"expression": "1250 * 3 + 99"}))
        if "euro" in user_text.lower() or "eur" in user_text.lower():
            plan.append(("convert_currency", {"amount": 3849,
                                              "from_currency": "USD",
                                              "to_currency": "EUR"}))
        for name, args in plan:
            if name not in done:
                return {"type": "tool_call", "name": name, "arguments": args}
        results = {m["tool"]: m["content"] for m in messages if m["role"] == "tool"}
        parts = []
        if "calculator" in results:
            parts.append(f"the package total is ${results['calculator']['result']}")
        if "convert_currency" in results:
            r = results["convert_currency"]
            parts.append(f"that is EUR {r['converted']} at the teaching rate")
        return {"type": "final", "text": "Summary: " + "; ".join(parts) + "."}


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
        result = TOOLS[name]["fn"](**args)
        print(f"TOOL (step {step}): {name}({json.dumps(args)}) -> {json.dumps(result)}")
        messages.append({"role": "tool", "tool": name, "content": result})
    raise RuntimeError("Step limit reached.")


if __name__ == "__main__":
    run_agent("What is the total cost of 3 seats, in euros?")
