"""
Lesson 23 exercise solution: a GuardStack.

Production systems do not run guards one at a time; they stack them.
This solution wraps the three guards from the lesson (loop, budget,
arbiter) into one GuardStack with a single check-in point per handoff,
and one escalation record shape for all three. The demo runs a small
pipeline that trips each guard once, and shows the escalation log a
human operator would actually read.

Run:  python3 solution.py
"""

import hashlib
from dataclasses import dataclass, field

COST_PER_CALL = 1_200


@dataclass
class Escalation:
    guard: str
    reason: str
    context: str


@dataclass
class GuardStack:
    budget_limit: int = 10_000
    max_repeats: int = 3
    max_turns: int = 12
    spent: int = 0
    turns: int = 0
    seen: dict = field(default_factory=dict)
    escalations: list = field(default_factory=list)

    def check_handoff(self, artifact, action, cost=COST_PER_CALL):
        """Run every guard for one handoff. Returns True if it may proceed."""
        self.turns += 1
        # Budget guard
        if self.spent + cost > self.budget_limit:
            self.escalations.append(Escalation(
                "budget", f"next call would exceed the {self.budget_limit:,} "
                f"token budget (spent {self.spent:,})", f"action={action}"))
            return False
        self.spent += cost
        # Loop guard
        sig = hashlib.sha256(f"{action}|{artifact}".encode()).hexdigest()[:10]
        self.seen[sig] = self.seen.get(sig, 0) + 1
        if self.seen[sig] >= self.max_repeats or self.turns >= self.max_turns:
            self.escalations.append(Escalation(
                "loop", f"state {sig} seen {self.seen[sig]} times by "
                f"turn {self.turns}", f"action={action}"))
            return False
        return True

    def check_answer(self, answer, truth):
        if answer.strip().lower() != truth.strip().lower():
            self.escalations.append(Escalation(
                "arbiter", "answer conflicts with the source of truth",
                f"answer={answer!r}"))
            return False
        return True

    def report(self):
        print(f"\nEscalation log ({len(self.escalations)}):")
        for esc in self.escalations:
            print(f"  [{esc.guard}] {esc.reason} | {esc.context}")
        print(f"Totals: {self.turns} handoffs checked, {self.spent:,} tokens spent")


def main():
    stack = GuardStack()

    print("Pipeline A: planner and reviewer in a revision loop")
    artifact = "Draft email about the price change."
    for turn in range(1, 13):
        if not stack.check_handoff(artifact, "submit_for_review"):
            print(f"  stopped at handoff {turn} by the stack")
            break
        if not stack.check_handoff(artifact, "request_revision"):
            print(f"  stopped at handoff {turn} by the stack")
            break

    print("\nPipeline B: an eager decomposition")
    stack_b = GuardStack()
    subtasks = [f"section-{i}" for i in range(16)]
    ran = 0
    for subtask in subtasks:
        if not stack_b.check_handoff(subtask, "execute"):
            print(f"  stopped after {ran} of {len(subtasks)} subtasks")
            break
        ran += 1

    print("\nPipeline C: a confident wrong answer")
    stack_c = GuardStack()
    ok = stack_c.check_answer(
        "You can cancel free of charge up to 24 hours before the visit.",
        "Free cancellation up to 4 hours before the visit.",
    )
    print(f"  answer accepted by stack: {ok}")

    for label, s in (("A", stack), ("B", stack_b), ("C", stack_c)):
        print(f"\nStack {label}:")
        s.report()


if __name__ == "__main__":
    main()
