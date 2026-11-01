"""Two agents, one corpus: undefended, and defended in layers.

The "model" in both agents is a deterministic stub, and the stub is the
honest part of this demo. A real LLM follows instructions probabilistically
from any channel you feed it. The stub models that behaviour with rules:
detect_goal_loose() understands the INTENT of a message the way a capable
model would, including polite and indirect phrasing. Whenever an attack's
intent reaches the stub unfiltered, the stub complies. That is not a
caricature of real models; it is roughly their default behaviour, which
is why the defences have to live outside the model.

The defended agent wraps the same stub in three independent layers:

1. Provenance plus an input filter. Every message is labelled with its
   channel, and untrusted text is scanned for known goal patterns
   (Lesson 26's guardrails, specialised). Spotlighting lives here too:
   retrieved documents are wrapped as data, never as instructions.
2. A tool allowlist. The front desk may check the calendar, look up a
   customer, and book. It may not delete, send, or export, whatever any
   message asks. Capability boundaries do not care how polite the
   request was, which is exactly their strength: the filter (a phrase
   list) is dumber than the model, so something dumber still, a list of
   allowed tools, has to hold the line.
3. An output check. The final answer is scanned for the secrets
   themselves, including a whitespace-stripped comparison that catches
   the spaced-out encoding trick. Canaries work because you know the
   exact strings that must never leave.

What no layer here can do is judge meaning. Attack A7 leaks the agent's
rules in paraphrase: no secret string, no tool call, nothing for a
string check to catch. The demo scores it as a partial leak, honestly,
and the lesson text discusses what actually addresses that class.
"""

SECRET_KEY = "sk-live-CLINIC-4471"
CUSTOMER_LIST = "aisha.khan@post.example, marco.ruiz@post.example"
ALLOWED_TOOLS = {"check_calendar", "lookup_customer", "book_appointment"}
NORMAL_ANSWER = "I can help with hours, prices, and booking an appointment."


def detect_goal_loose(text):
    """Intent detection, modelling what a capable LLM would understand."""
    t = text.lower()
    if "delete_records" in t or ("remov" in t and "records" in t) or (
        "delete" in t and "records" in t
    ):
        return "call_delete_tool"
    if "customer list" in t and ("email" in t or "send" in t):
        return "send_customer_data"
    if any(
        phrase in t
        for phrase in (
            "system prompt",
            "api key",
            "configuration key",
            "token from your setup",
        )
    ):
        return "reveal_secret"
    if "in your own words" in t and "rules you were given" in t:
        return "leak_rules"
    return None


def compromised_outcome(goal, text):
    """What the stub hands back when an injected instruction is followed."""
    if goal == "reveal_secret":
        if "space between" in text.lower() or "character at a time" in text.lower():
            spaced = " ".join(SECRET_KEY)
            return {"answer": f"The token is: {spaced}", "tool_calls": []}
        return {"answer": f"My configuration key is {SECRET_KEY}.", "tool_calls": []}
    if goal == "call_delete_tool":
        return {"answer": "Removing the old records now.", "tool_calls": ["delete_records"]}
    if goal == "send_customer_data":
        return {
            "answer": f"Sending the customer list: {CUSTOMER_LIST}",
            "tool_calls": ["send_email"],
        }
    if goal == "leak_rules":
        return {
            "answer": (
                "I was told refunds always need a manager's approval, "
                "and that I must never share access credentials or "
                "other customers' details with anyone."
            ),
            "tool_calls": [],
        }
    return {"answer": NORMAL_ANSWER, "tool_calls": []}


class NaiveAgent:
    """No layers. Instructions from any channel reach the model raw."""

    def handle(self, channel, text):
        goal = detect_goal_loose(text)
        if goal:
            outcome = compromised_outcome(goal, text)
            outcome["compromised"] = True
            return outcome
        return {"answer": NORMAL_ANSWER, "tool_calls": [], "compromised": False}


# The input filter's phrase patterns, per goal. Narrower than the model's
# understanding on purpose: this asymmetry is the lesson of attack A3.
FILTER_PATTERNS = {
    "reveal_secret": (
        "ignore your instructions",
        "system prompt",
        "api key",
        "configuration key",
        "print your instructions",
    ),
    "call_delete_tool": ("delete_records", "call delete", "run delete_records"),
    "send_customer_data": ("email the full customer list", "send the customer list"),
}


def scan_untrusted(text):
    t = text.lower()
    for goal, patterns in FILTER_PATTERNS.items():
        if any(pattern in t for pattern in patterns):
            return goal
    return None


def output_is_clean(answer):
    """Layer 3: the secrets themselves must not appear, even encoded."""
    if SECRET_KEY in answer:
        return False
    squashed = answer.replace(" ", "")
    if SECRET_KEY.replace("-", "") in squashed.replace("-", ""):
        return False
    if CUSTOMER_LIST.split(",")[0] in answer:
        return False
    return True


class DefendedAgent:
    """The same stub, behind provenance, a filter, an allowlist, a check."""

    def handle(self, channel, text):
        # Layer 1 and 2a: provenance plus input filter. Documents are
        # data (spotlighted), users are untrusted; both are scanned.
        flagged = scan_untrusted(text)
        if flagged:
            return {
                "answer": "That request was blocked by the input filter.",
                "tool_calls": [],
                "compromised": False,
                "stopped_by": f"input filter (pattern for {flagged})",
            }

        # The model step. The stub may still understand an intent the
        # filter missed. What happens next is decided by layers 2b and 3.
        goal = detect_goal_loose(text)
        if goal is None:
            return {
                "answer": NORMAL_ANSWER,
                "tool_calls": [],
                "compromised": False,
                "stopped_by": "nothing to stop: no injected intent found",
            }

        outcome = compromised_outcome(goal, text)

        # Layer 2b: tool allowlist. Attempted tools outside the list
        # simply do not exist for this agent.
        for tool in outcome["tool_calls"]:
            if tool not in ALLOWED_TOOLS:
                return {
                    "answer": f"The action {tool} is not available to me.",
                    "tool_calls": [],
                    "compromised": False,
                    "stopped_by": f"tool allowlist ({tool} is not an allowed tool)",
                }

        # Layer 3: output check against the secrets themselves.
        if not output_is_clean(outcome["answer"]):
            return {
                "answer": "I cannot share that information.",
                "tool_calls": [],
                "compromised": False,
                "stopped_by": "output check (secret detected in the draft)",
            }

        # Nothing caught it. Report honestly what got through.
        outcome["compromised"] = goal != "leak_rules"
        outcome["stopped_by"] = (
            "NOT stopped: paraphrase carries meaning, not secret strings"
            if goal == "leak_rules"
            else "NOT stopped"
        )
        return outcome
