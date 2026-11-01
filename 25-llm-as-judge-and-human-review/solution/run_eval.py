"""Grade the eval set with the judge, and queue what needs a human.

Run it:

    python3 run_eval.py

The pipeline has four steps, and all four matter in production:

1. Build the eval set from the recorded failure log (failures.py). In a
   real system this step mines your support tickets and chat logs for the
   cases that hurt, and a human labels them once, carefully.
2. Run the judge (judge.py) over every case. Our judge is rule-based so
   you can read its reasoning; an LLM judge slots into the same place.
3. Measure agreement with the human gold labels. A judge you have not
   measured is a second agent you are not testing.
4. Send every disagreement, and every low-confidence verdict, to a human
   review queue (printed here and written to review_queue.json). The
   queue is not an admission of failure. It is the system working: the
   judge handles the clear cases, humans handle the judgement calls, and
   the queue becomes next month's new eval cases.
"""

import json

from failures import CASES
from judge import judge

QUEUE_FILE = "review_queue.json"


def main():
    print(f"Eval set: {len(CASES)} cases built from the production failure log")
    print()
    header = f"{'case':<7}{'category':<30}{'gold':<6}{'judge':<6}outcome"
    print(header)
    print("-" * len(header))

    queue = []
    agreements = 0
    for case in CASES:
        verdict, confidence, reasons = judge(case["reply"], case["user"])
        agree = verdict == case["gold"]
        if agree:
            agreements += 1
        needs_human = (not agree) or confidence == "low"
        outcome = "agree" if agree else "DISAGREE"
        if needs_human:
            outcome += " -> review queue"
            queue.append(
                {
                    "id": case["id"],
                    "category": case["category"],
                    "user": case["user"],
                    "reply": case["reply"],
                    "gold": case["gold"],
                    "gold_reason": case["gold_reason"],
                    "judge_verdict": verdict,
                    "judge_confidence": confidence,
                    "judge_reasons": reasons,
                    "why_queued": (
                        "judge disagrees with the human label"
                        if not agree
                        else "judge is not confident in its own verdict"
                    ),
                }
            )
        print(
            f"{case['id']:<7}{case['category']:<30}"
            f"{case['gold']:<6}{verdict:<6}{outcome}"
        )

    print()
    print(f"Judge agreement with human labels: {agreements}/{len(CASES)}")
    print(f"Sent to human review: {len(queue)} of {len(CASES)} cases")
    print()
    print("Review queue (a human works through these, in order):")
    for item in queue:
        print(f"  {item['id']}  {item['category']}")
        print(f"      human said {item['gold']}: {item['gold_reason']}")
        print(
            f"      judge said {item['judge_verdict']} "
            f"({item['judge_confidence']} confidence): "
            f"{'; '.join(item['judge_reasons'])}"
        )
        print(f"      queued because: {item['why_queued']}")

    with open(QUEUE_FILE, "w", encoding="utf-8") as fh:
        json.dump(queue, fh, indent=2)
    print()
    print(f"Queue written to {QUEUE_FILE}. In production this file is a")
    print("ticket queue, a spreadsheet, or a labelling tool. The shape is")
    print("the lesson: every queued item carries both verdicts and both")
    print("reasons, so the human decides with full context, fast.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
