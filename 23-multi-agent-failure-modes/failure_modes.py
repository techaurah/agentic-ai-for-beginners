"""
Lesson 23: Multi-agent failure modes, and the guards that stop them.

Three ways multi-agent systems hurt you in production, each simulated
deterministically, each run twice: guards off, then guards on.

  1. THE LOOP: two agents hand the same work back and forth forever.
     Guard: a loop detector that recognises repeated state and a hard
     turn budget, escalating to a human with a summary.

  2. THE COST BLOWOUT: a planner keeps decomposing work into more
     subtasks, each one a paid model call.
     Guard: a budget cap that stops the run at a spend limit and
     returns partial results instead of a surprise bill.

  3. THE CONFLICT: two agents answer the same question differently.
     Guard: an arbiter that checks both answers against the source of
     truth and escalates when neither matches.

Costs are simulated token counts, so the lesson runs offline. The
counters, thresholds, and escalation shapes are the production ones.

Run:  python3 failure_modes.py
"""

import hashlib

COST_PER_CALL = 1_200  # simulated tokens per agent call


# ---------------------------------------------------------------------------
# Failure 1: the loop
# ---------------------------------------------------------------------------

class LoopGuard:
    """Watches handoffs. Trips when the same state signature repeats."""

    def __init__(self, max_repeats=3, max_turns=10):
        self.max_repeats = max_repeats
        self.max_turns = max_turns
        self.seen = {}
        self.turns = 0

    @staticmethod
    def signature(artifact, last_action):
        raw = f"{last_action}|{artifact}".encode()
        return hashlib.sha256(raw).hexdigest()[:10]

    def observe(self, artifact, last_action):
        """Returns a trip reason, or None if the run may continue."""
        self.turns += 1
        sig = self.signature(artifact, last_action)
        self.seen[sig] = self.seen.get(sig, 0) + 1
        if self.seen[sig] >= self.max_repeats:
            return f"same state seen {self.seen[sig]} times (signature {sig})"
        if self.turns >= self.max_turns:
            return f"turn budget exhausted ({self.max_turns})"
        return None


def planner(artifact):
    # The planner never actually changes the artifact: it re-emits it
    # with fresh confidence. This is the polite face of a stuck agent.
    return artifact, "submit_for_review"


def reviewer(artifact):
    # The reviewer applies a rule the artifact can never satisfy:
    # it demands a sign-off line the planner was never told to add.
    if "Signed off by: Head of Operations" in artifact:
        return artifact, "approve"
    return artifact, "request_revision"


def run_loop(guard_on):
    print(f"\n--- Failure 1: the loop (guards {'ON' if guard_on else 'OFF'}) ---")
    artifact = "Draft email to customers about the price change."
    guard = LoopGuard() if guard_on else None
    action = "submit_for_review"
    hard_stop = 50  # the platform kills the run here, eventually
    for turn in range(1, hard_stop + 1):
        if action == "submit_for_review":
            artifact, action = reviewer(artifact)
            actor = "reviewer"
        elif action == "request_revision":
            artifact, action = planner(artifact)
            actor = "planner"
        else:
            print(f"  turn {turn}: approved, loop ends happily")
            return turn
        if guard:
            reason = guard.observe(artifact, action)
            if reason:
                print(f"  turn {turn}: LOOP GUARD TRIPPED: {reason}")
                print(f"  ESCALATION to human: planner and reviewer disagree on a "
                      f"requirement neither can see. Artifact unchanged for "
                      f"{turn} turns.")
                return turn
        if turn in (1, 2, 3, hard_stop):
            print(f"  turn {turn}: {actor} -> {action}")
    print(f"  killed by the platform at turn {hard_stop}. "
          f"Simulated cost so far: {hard_stop * COST_PER_CALL:,} tokens.")
    return hard_stop


# ---------------------------------------------------------------------------
# Failure 2: the cost blowout
# ---------------------------------------------------------------------------

class BudgetCap:
    def __init__(self, limit_tokens):
        self.limit = limit_tokens
        self.spent = 0

    def charge(self, tokens):
        """Returns False when the next call would breach the cap."""
        if self.spent + tokens > self.limit:
            return False
        self.spent += tokens
        return True


def decompose(task, depth):
    """A planner that splits every task into two subtasks, eagerly."""
    if depth == 0:
        return [task]
    left = decompose(f"{task}.a", depth - 1)
    right = decompose(f"{task}.b", depth - 1)
    return left + right


def run_cost(guard_on, budget=10_000):
    print(f"\n--- Failure 2: the cost blowout (guards {'ON' if guard_on else 'OFF'}) ---")
    plan = decompose("quarterly-report", depth=4)
    print(f"  planner decomposed the job into {len(plan)} subtasks")
    cap = BudgetCap(budget) if guard_on else None
    done = 0
    spent = 0
    for subtask in plan:
        if cap and not cap.charge(COST_PER_CALL):
            print(f"  BUDGET CAP: stopped at {cap.spent:,} of {budget:,} tokens "
                  f"after {done} subtasks")
            print(f"  returning partial result: {done} of {len(plan)} sections, "
                  f"with the remainder listed as not attempted")
            return done, cap.spent
        spent += COST_PER_CALL
        done += 1
    print(f"  all {done} subtasks ran. Total simulated cost: {spent:,} tokens")
    print("  nobody decided to spend that; the decomposition did.")
    return done, spent


# ---------------------------------------------------------------------------
# Failure 3: conflicting outputs
# ---------------------------------------------------------------------------

SOURCE_OF_TRUTH = {
    "question": "How long is the free cancellation window?",
    "answer": "Free cancellation up to 4 hours before the visit.",
}

AGENT_ANSWERS = [
    {"agent": "SupportAgent", "answer": "You can cancel free of charge up to 24 hours before the visit."},
    {"agent": "BookingAgent", "answer": "Free cancellation up to 4 hours before the visit."},
]


def arbiter(answers, truth):
    """Compare each answer against the source of truth."""
    verdicts = []
    for item in answers:
        matches = item["answer"].strip().lower() == truth["answer"].strip().lower()
        verdicts.append((item["agent"], matches))
    winners = [agent for agent, ok in verdicts if ok]
    return verdicts, winners


def run_conflict(guard_on):
    print(f"\n--- Failure 3: conflicting outputs (guards {'ON' if guard_on else 'OFF'}) ---")
    if not guard_on:
        chosen = AGENT_ANSWERS[-1]  # last writer wins: a common default
        print(f"  two agents answered differently; the system shipped the "
              f"last one ({chosen['agent']})")
        print(f"  shipped: \"{chosen['answer']}\"")
        print("  it happened to be right this time. Nothing in the system "
              "knew that, or would have caught it if the order flipped.")
        return
    verdicts, winners = arbiter(AGENT_ANSWERS, SOURCE_OF_TRUTH)
    for agent, ok in verdicts:
        print(f"  arbiter: {agent} {'MATCHES' if ok else 'CONFLICTS WITH'} "
              f"the source of truth")
    if len(winners) == 1:
        print(f"  shipped the {winners[0]} answer, flagged the other for review")
    else:
        print("  ESCALATION to human: no answer matches the source of truth")


# ---------------------------------------------------------------------------

def main():
    loop_off = run_loop(guard_on=False)
    loop_on = run_loop(guard_on=True)
    done_off, spent_off = run_cost(guard_on=False)
    done_on, spent_on = run_cost(guard_on=True)
    run_conflict(guard_on=False)
    run_conflict(guard_on=True)
    print("\n--- Scoreboard ---")
    print(f"Loop:      unguarded ran {loop_off} turns, guarded stopped at {loop_on}")
    print(f"Cost:      unguarded spent {spent_off:,} tokens for {done_off} subtasks, "
          f"guarded spent {spent_on:,} for {done_on} plus an honest partial result")
    print("Conflict:  unguarded shipped by accident, guarded shipped by evidence")


if __name__ == "__main__":
    main()
