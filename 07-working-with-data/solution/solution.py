"""Lesson 07 exercise solution: guarded stage moves and a hot-leads export.

Two upgrades to state_demo.py:

  1. Stage moves are guarded by a transition map. A lead may move forward
     one stage at a time, or to 'lost' from anywhere. Skipping stages or
     moving backwards raises an error instead of corrupting the pipeline.
  2. Leads scoring 80 or more are exported to output/hot_leads.csv, the
     list a human (or a follow-up agent) should work first.

Run:  python3 solution.py
"""

import csv
import json
from pathlib import Path

BASE = Path(__file__).parent
SEED = BASE.parent / "data" / "pipeline_seed.json"
OUT_DIR = BASE.parent / "output"

STAGES = ["new", "contacted", "qualified", "booked", "lost"]


def allowed_moves(stage: str) -> set:
    if stage == "lost":
        return set()
    index = STAGES.index(stage)
    moves = {"lost"}
    if index + 1 < len(STAGES) - 1:
        moves.add(STAGES[index + 1])
    elif stage != "booked":
        moves.add("booked")
    return moves


def move_stage(state: dict, lead_id: str, new_stage: str) -> None:
    for lead in state["leads"]:
        if lead["id"] == lead_id:
            current = lead["stage"]
            if new_stage not in allowed_moves(current):
                raise ValueError(
                    f"illegal move {current} -> {new_stage} for {lead_id}; "
                    f"allowed: {sorted(allowed_moves(current))}"
                )
            lead["stage"] = new_stage
            print(f"moved {lead_id}: {current} -> {new_stage}")
            return
    raise KeyError(f"no lead with id {lead_id}")


def export_hot_leads(state: dict, minimum: int = 80) -> Path:
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / "hot_leads.csv"
    hot = [lead for lead in state["leads"] if lead["score"] >= minimum]
    hot.sort(key=lambda lead: lead["score"], reverse=True)
    with open(path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "score", "stage", "service"])
        for lead in hot:
            writer.writerow(
                [lead["id"], lead["name"], lead["score"], lead["stage"], lead["service"]]
            )
    return path, hot


def main() -> None:
    with open(SEED) as file:
        state = json.load(file)
    print(f"loaded {len(state['leads'])} leads")

    move_stage(state, "LP-2026-00031", "booked")  # qualified -> booked: legal
    try:
        move_stage(state, "LP-2026-00035", "booked")  # contacted -> booked: skips a stage
    except ValueError as error:
        print(f"rejected: {error}")

    path, hot = export_hot_leads(state)
    print(f"exported {len(hot)} hot lead(s) (score >= 80) to output/hot_leads.csv:")
    for lead in hot:
        print(f"  {lead['id']}  score {lead['score']}  {lead['name']} ({lead['stage']})")


if __name__ == "__main__":
    main()
