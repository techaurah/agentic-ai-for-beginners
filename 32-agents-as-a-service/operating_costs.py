"""Operating-cost worksheet for running a business agent for one client.

Lesson 32, Agentic AI for Beginners (TechAura Academy).

Every number in this file is ILLUSTRATIVE. Prices for models, hosting and
tools change constantly, and labour rates depend on your market. The point
of the worksheet is the structure: which cost lines exist, how they scale,
and what a client is actually paying for when an agent is run for them as
a service. Replace the inputs with your own quotes before using any total.

Run:  python3 operating_costs.py
"""

from __future__ import annotations

# --- Illustrative inputs (edit these) --------------------------------------

ILLUSTRATIVE = {
    # Volume
    "enquiries_per_month": 400,          # enquiries the agent handles
    "avg_turns_per_enquiry": 6,          # messages per enquiry, both ways
    # Model usage (per enquiry, blended across the pipeline's steps)
    "input_tokens_per_enquiry": 9000,
    "output_tokens_per_enquiry": 1800,
    "input_price_per_million": 0.80,     # USD, illustrative mid-tier model
    "output_price_per_million": 4.00,    # USD, illustrative mid-tier model
    # Fixed monthly lines
    "hosting_usd": 25,                   # small VPS / serverless baseline
    "tools_usd": 40,                     # calendar, sheets/CRM tier, monitoring
    "phone_and_messaging_usd": 30,       # number rental + per-message fees
    # Human operations (the part vendors hide)
    "ops_hours_per_month": 4,            # review queues, tune prompts, check traces
    "improvement_hours_per_month": 2,    # monthly improvement work on the agent
    "labour_rate_usd_per_hour": 40,      # blended operator rate, illustrative
    # Safety margin for incidents and overruns
    "contingency_pct": 10,
}


def monthly_costs(inp: dict) -> dict:
    enquiries = inp["enquiries_per_month"]
    model = enquiries * (
        inp["input_tokens_per_enquiry"] / 1_000_000 * inp["input_price_per_million"]
        + inp["output_tokens_per_enquiry"] / 1_000_000 * inp["output_price_per_million"]
    )
    lines = {
        "Model usage": model,
        "Hosting": inp["hosting_usd"],
        "Tools and data": inp["tools_usd"],
        "Phone and messaging": inp["phone_and_messaging_usd"],
        "Human operations (review, tuning)":
            inp["ops_hours_per_month"] * inp["labour_rate_usd_per_hour"],
        "Monthly improvement work":
            inp["improvement_hours_per_month"] * inp["labour_rate_usd_per_hour"],
    }
    subtotal = sum(lines.values())
    lines["Contingency"] = subtotal * inp["contingency_pct"] / 100
    lines["TOTAL per month"] = subtotal + lines["Contingency"]
    lines["Cost per enquiry"] = lines["TOTAL per month"] / enquiries
    return lines


def main() -> None:
    print("ILLUSTRATIVE worksheet. Replace every input with your own quotes.\n")
    for name, value in monthly_costs(ILLUSTRATIVE).items():
        print(f"{name:<38} ${value:>8.2f}")
    print("\nThe lesson: model tokens are the smallest line on this page.")
    print("The service a client pays for is the human operations around the agent.")


if __name__ == "__main__":
    main()
