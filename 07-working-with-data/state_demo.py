"""Lesson 07 demo: JSON, files, and spreadsheets as agent state.

An agent is only as reliable as the state it keeps. This demo treats a JSON
file as the agent's memory of a sales pipeline and a CSV as a price list,
then performs the three operations every agent eventually needs:

  1. read state        (load the pipeline from disk)
  2. update state      (add a scored lead, move a lead to a new stage)
  3. write state back  (save JSON, export a CSV summary a human can open)

Fully offline, standard library only, deterministic output.

Run:  python3 state_demo.py
Output files land in ./output/ so the seed data is never mutated.
"""

import csv
import json
from pathlib import Path

BASE = Path(__file__).parent
SEED = BASE / "data" / "pipeline_seed.json"
PRICES = BASE / "data" / "services.csv"
OUT_DIR = BASE / "output"

VALID_STAGES = ["new", "contacted", "qualified", "booked", "lost"]


def load_state() -> dict:
    with open(SEED) as file:
        return json.load(file)


def load_prices() -> dict:
    with open(PRICES, newline="") as file:
        return {row["service"]: row for row in csv.DictReader(file)}


def next_lead_id(leads: list) -> str:
    highest = max(int(lead["id"].split("-")[-1]) for lead in leads)
    return f"LP-2026-{highest + 1:05d}"


def score_lead(message: str) -> int:
    """A tiny deterministic stand-in for an LLM scorer.

    Same input, same score, every run. Lesson 04 shows the real model call;
    the state handling around it is identical either way.
    """
    score = 40
    text = message.lower()
    if "emergency" in text or "pain" in text:
        score += 35
    if "price" in text or "cost" in text:
        score += 10
    if "book" in text or "appointment" in text:
        score += 15
    return min(score, 100)


def move_stage(state: dict, lead_id: str, new_stage: str) -> None:
    if new_stage not in VALID_STAGES:
        raise ValueError(f"unknown stage: {new_stage}")
    for lead in state["leads"]:
        if lead["id"] == lead_id:
            lead["stage"] = new_stage
            return
    raise KeyError(f"no lead with id {lead_id}")


def export_summary(state: dict) -> Path:
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / "summary.csv"
    with open(path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["stage", "leads"])
        for stage in VALID_STAGES:
            count = sum(1 for lead in state["leads"] if lead["stage"] == stage)
            writer.writerow([stage, count])
    return path


def main() -> None:
    state = load_state()
    prices = load_prices()
    print(f"loaded pipeline '{state['pipeline']}' with {len(state['leads'])} leads")
    print(f"loaded {len(prices)} services from the CSV price list")

    message = "I have tooth pain, it feels like an emergency. Can I book an appointment?"
    new_lead = {
        "id": next_lead_id(state["leads"]),
        "name": "Ayesha Khan",
        "channel": "website form",
        "service": "emergency repair",
        "score": score_lead(message),
        "stage": "new",
    }
    state["leads"].append(new_lead)
    price = prices[new_lead["service"]]["price_gbp"]
    print(
        f"added {new_lead['id']} ({new_lead['name']}): "
        f"score {new_lead['score']}, service '{new_lead['service']}' at GBP {price}"
    )

    move_stage(state, new_lead["id"], "qualified")
    print(f"moved {new_lead['id']} from 'new' to 'qualified'")

    OUT_DIR.mkdir(exist_ok=True)
    state_path = OUT_DIR / "pipeline.json"
    with open(state_path, "w") as file:
        json.dump(state, file, indent=2)
    summary_path = export_summary(state)
    print(f"saved updated state to output/pipeline.json ({len(state['leads'])} leads)")
    print("summary by stage:")
    for stage in VALID_STAGES:
        count = sum(1 for lead in state["leads"] if lead["stage"] == stage)
        print(f"  {stage:<10} {count}")
    print(f"wrote {summary_path.relative_to(BASE)}")


if __name__ == "__main__":
    main()
