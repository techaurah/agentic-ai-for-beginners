"""A cost and latency simulator for model-per-step strategies.

Run it:

    python3 simulator.py

One seeded workload (a day of clinic-agent traffic: support replies,
lead qualifications, document summaries, complaint replies) is priced
and timed under five strategies:

- all_frontier:   every step on the biggest model. The default most
                  teams ship, and usually the most expensive habit.
- all_small:      every step on the cheapest model. The floor on cost,
                  with a quality question the lesson text discusses.
- routed:         each step type on the cheapest model that does it
                  well: small models classify and extract, a mid model
                  drafts and summarises, the frontier model only reasons.
- routed_cached:  routed, plus an exact-match cache. The workload repeats
                  each unique request 3 times (real traffic does this:
                  the same questions all day), and repeats are served
                  from cache at no model cost.
- routed_cached_batched: plus batch pricing for steps nobody is waiting
                  on (classify, extract, summarise, score run async at
                  half price and a quarter of the latency pressure).

Prices and latencies are FAKE, chosen to be plausible, and printed with
the table. The numbers that matter are the ratios between strategies,
and those are driven by the shape of the workload, which is the skill:
count your steps, price each one, and send each step to the cheapest
model that clears its quality bar (measured with Lessons 24 and 25).
"""

import math
import random

# Fake prices per million tokens, and a latency model:
# latency_ms = base_ms + output_tokens * ms_per_token.
MODELS = {
    "frontier-1": {"input": 3.00, "output": 15.00, "base_ms": 800, "ms_per_token": 12},
    "mid-1": {"input": 0.80, "output": 4.00, "base_ms": 400, "ms_per_token": 8},
    "small-1": {"input": 0.15, "output": 0.60, "base_ms": 150, "ms_per_token": 4},
}

STEP_TOKENS = {  # (input range, output range) per step type
    "classify": ((200, 400), (5, 15)),
    "extract": ((400, 900), (50, 120)),
    "summarize": ((1200, 2500), (120, 250)),
    "draft": ((500, 900), (200, 400)),
    "reason": ((800, 1600), (250, 500)),
    "score": ((300, 600), (20, 60)),
}

PIPELINES = {
    "support_reply": ["classify", "draft"],
    "lead_qualification": ["extract", "reason", "score"],
    "document_summary": ["summarize", "extract"],
    "complaint_reply": ["classify", "reason", "draft"],
}

ROUTING = {
    "classify": "small-1",
    "extract": "small-1",
    "summarize": "mid-1",
    "score": "mid-1",
    "draft": "mid-1",
    "reason": "frontier-1",
}
BATCHABLE = {"classify", "extract", "summarize", "score"}
CACHE_HIT_MS = 5


def build_workload(seed=20261101, unique=40, repeats=3):
    """Deterministic traffic: unique requests, each repeated `repeats` times."""
    rng = random.Random(seed)
    requests = []
    for i in range(unique):
        kind = rng.choice(list(PIPELINES))
        steps = []
        for step_type in PIPELINES[kind]:
            (in_lo, in_hi), (out_lo, out_hi) = STEP_TOKENS[step_type]
            steps.append(
                {
                    "type": step_type,
                    "input_tokens": rng.randint(in_lo, in_hi),
                    "output_tokens": rng.randint(out_lo, out_hi),
                }
            )
        requests.append({"id": f"req-{i + 1:03d}", "kind": kind, "steps": steps})
    day = []
    for _ in range(repeats):
        day.extend(requests)
    return day


def price_step(model, step, batched=False):
    prices = MODELS[model]
    cost = (
        step["input_tokens"] / 1_000_000 * prices["input"]
        + step["output_tokens"] / 1_000_000 * prices["output"]
    )
    latency = prices["base_ms"] + step["output_tokens"] * prices["ms_per_token"]
    if batched:
        cost *= 0.5
        latency //= 4
    return cost, latency


def run_strategy(day, choose_model, cache=False, batch=False):
    seen = set()
    total_cost = 0.0
    latencies = []
    for request in day:
        if cache and request["id"] in seen:
            latencies.append(CACHE_HIT_MS)
            continue
        seen.add(request["id"])
        request_cost = 0.0
        request_latency = 0
        for step in request["steps"]:
            model = choose_model(step["type"])
            batched = batch and step["type"] in BATCHABLE
            cost, latency = price_step(model, step, batched)
            request_cost += cost
            request_latency += latency
        total_cost += request_cost
        latencies.append(request_latency)
    latencies.sort()
    p95 = latencies[math.ceil(0.95 * len(latencies)) - 1]
    avg = sum(latencies) / len(latencies)
    return total_cost, avg, p95


# Ramble thresholds for the cascade (exercise addition). The small
# model's attempt is trusted unless it runs long: a draft or a piece
# of reasoning far past the usual length usually means the request
# was complicated or ambiguous. Length is a crude, cheap quality
# signal. Production systems use better ones (a checker model, format
# validation, tool success), but the design shape is identical:
# try cheap, verify, escalate.
CASCADE_LIMITS = {"draft": 320, "reason": 420}


def run_cascade(day):
    """Routed strategy, but draft and reason steps try small-1 first.

    A step whose small-model output runs past its ramble threshold is
    discarded and rerun on frontier-1. Both runs count toward cost
    and latency: the cascade pays for its escalations, which is
    exactly why it needs measuring instead of assuming.
    """
    total_cost = 0.0
    latencies = []
    escalations = 0
    generative = 0
    for request in day:
        request_cost = 0.0
        request_latency = 0
        for step in request["steps"]:
            if step["type"] in CASCADE_LIMITS:
                generative += 1
                cost, latency = price_step("small-1", step)
                request_cost += cost
                request_latency += latency
                if step["output_tokens"] > CASCADE_LIMITS[step["type"]]:
                    escalations += 1
                    cost, latency = price_step("frontier-1", step)
                    request_cost += cost
                    request_latency += latency
            else:
                cost, latency = price_step(ROUTING[step["type"]], step)
                request_cost += cost
                request_latency += latency
        total_cost += request_cost
        latencies.append(request_latency)
    latencies.sort()
    p95 = latencies[math.ceil(0.95 * len(latencies)) - 1]
    avg = sum(latencies) / len(latencies)
    return total_cost, avg, p95, escalations, generative


def main():
    day = build_workload()
    strategies = [
        ("all_frontier", lambda step: "frontier-1", {}),
        ("all_small", lambda step: "small-1", {}),
        ("routed", lambda step: ROUTING[step], {}),
        ("routed_cached", lambda step: ROUTING[step], {"cache": True}),
        (
            "routed_cached_batched",
            lambda step: ROUTING[step],
            {"cache": True, "batch": True},
        ),
    ]

    print(f"Workload: {len(day)} requests in a day (40 unique, each repeated 3x)")
    print("Fake prices: frontier-1 $3/$15, mid-1 $0.80/$4, small-1 $0.15/$0.60 per 1M tokens")
    print()
    header = f"{'strategy':<24}{'day cost':>10}{'avg latency':>13}{'p95 latency':>13}"
    print(header)
    print("-" * len(header))
    results = {}
    for name, choose, kwargs in strategies:
        cost, avg, p95 = run_strategy(day, choose, **kwargs)
        results[name] = cost
        print(f"{name:<24}${cost:>9.4f}{avg:>11.0f}ms{p95:>11.0f}ms")

    cascade_cost, cascade_avg, cascade_p95, escalations, generative = (
        run_cascade(day)
    )
    results["cascade"] = cascade_cost
    print(
        f"{'cascade':<24}${cascade_cost:>9.4f}"
        f"{cascade_avg:>11.0f}ms{cascade_p95:>11.0f}ms"
    )
    print()
    print(
        f"Cascade detail: {escalations} of {generative} draft and reason "
        "steps escalated to frontier-1 after the small model's attempt "
        "ran long. Both attempts are counted in its cost and latency."
    )

    base = results["all_frontier"]
    best = results["routed_cached_batched"]
    print()
    print(
        f"Routing, caching, and batching take the day from ${base:.4f} to "
        f"${best:.4f}, a {base / best:.1f}x reduction, before any quality"
    )
    print("trade-off is even discussed. Scaled to a month of the same")
    print(f"traffic, that is ${base * 30:.2f} against ${best * 30:.2f}. The")
    print("frontier model still does every reasoning step. It just stops")
    print("being paid to classify messages and extract phone numbers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
