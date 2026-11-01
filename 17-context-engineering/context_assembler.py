"""
Lesson 17: Context engineering: fitting the right information into the window.

Every agent call assembles a context from parts that compete for the same
budget: the system prompt, tool schemas, retrieved documents, memory, the
recent conversation, and the new user message. Context engineering is
deciding, on purpose:

  * what gets in (relevance beats volume),
  * in what order (instructions first, the question last),
  * and what happens when it does not all fit (a policy, not an accident).

This assembler packs parts by priority under a token budget and reports
exactly what it included, truncated, or dropped, so the policy is visible
instead of buried in a prompt string.

Run it:  python3 context_assembler.py
"""


def estimate_tokens(text: str) -> int:
    """Rough estimate: about 4 characters per token for English text."""
    return max(1, len(text) // 4)


class Part:
    def __init__(self, name: str, text: str, priority: int, required: bool = False):
        self.name = name
        self.text = text
        self.priority = priority      # lower number = packed earlier
        self.required = required      # required parts are never dropped

    @property
    def tokens(self) -> int:
        return estimate_tokens(self.text)


def assemble(parts: list[Part], budget: int) -> tuple[str, list[dict]]:
    """Pack parts into one context string under a token budget.

    Returns (context, report). Required parts (the instructions and the
    user's actual question) are reserved first: an assembler that drops
    the question to keep a retrieved document has its priorities upside
    down. Optional parts are then packed in priority order. A part that
    does not fit is truncated with a marker if there is room for a useful
    chunk, or dropped; the report records which happened. Included parts
    are emitted in priority order regardless of packing order.
    """
    by_priority = sorted(parts, key=lambda p: p.priority)
    packing_order = ([p for p in by_priority if p.required]
                     + [p for p in by_priority if not p.required])
    included_text: dict[str, str] = {}
    report_by_name: dict[str, dict] = {}
    used = 0

    for part in packing_order:
        remaining = budget - used
        if part.tokens <= remaining:
            included_text[part.name] = part.text
            used += part.tokens
            report_by_name[part.name] = {"part": part.name, "tokens": part.tokens,
                                         "action": "included"}
        elif remaining >= 40 and not part.required:  # room for a useful chunk
            keep_chars = (remaining - 10) * 4
            included_text[part.name] = part.text[:keep_chars] + " [...truncated...]"
            used = budget
            report_by_name[part.name] = {"part": part.name, "tokens": remaining,
                                         "action": "truncated"}
        else:
            action = "ERROR: required part dropped" if part.required else "dropped"
            report_by_name[part.name] = {"part": part.name, "tokens": 0, "action": action}

    context = "\n\n".join(included_text[p.name] for p in by_priority
                          if p.name in included_text)
    report = [report_by_name[p.name] for p in by_priority]
    return context, report


def demo_parts() -> list[Part]:
    return [
        Part("system_prompt",
             "You are a booking assistant for BrightSmile Dental. Be brief. "
             "Never invent prices or policies.", priority=0, required=True),
        Part("tool_schemas",
             "Tools: check_calendar(date), book_appointment(date, time, service, "
             "customer, idempotency_key), score_lead(budget, timeline, authority).",
             priority=1),
        Part("memory_summary",
             "Customer: Amara. Prefers morning appointments and text reminders. "
             "Last visit: cleaning, ran long.", priority=2),
        Part("retrieved_policy",
             "Policy: a cleaning takes 45 minutes. Cancellations under 24 hours "
             "before the appointment incur a fee equal to half the service price. "
             "New patients should arrive 10 minutes early to complete forms. "
             "The clinic is closed on Sundays and public holidays.", priority=3),
        Part("recent_turns",
             "User: Friday would be perfect, in the morning if possible. "
             "Assistant: Friday has 09:00, 10:30, and 14:00 free.",
             priority=4),
        Part("user_message",
             "What happens if I need to cancel the Friday cleaning?",
             priority=5, required=True),
    ]


if __name__ == "__main__":
    for budget in (400, 150):
        context, report = assemble(demo_parts(), budget)
        print(f"=== Budget: {budget} tokens ===")
        for row in report:
            print(f"  {row['part']:<18} {row['tokens']:>4} tokens  {row['action']}")
        print(f"  {'TOTAL':<18} {sum(r['tokens'] for r in report):>4} tokens")
        if budget == 150:
            print("\nAssembled context at the tight budget:")
            print(context)
        print()
