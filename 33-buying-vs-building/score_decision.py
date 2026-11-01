"""Apply the Lesson 33 decision framework to two sample companies.

Scores come from decision-framework.md (each factor 1-5). The samples are
fictional and deliberately contrasting: a small clinic that should buy,
and a large operator that should build. Run it, then score your own
company with the same function.

Run:  python3 score_decision.py
"""

from __future__ import annotations

BUY_FACTORS = ["speed_needed", "no_internal_builder", "process_stability",
               "standard_shape", "failure_is_operational"]
BUILD_FACTORS = ["strategic_capability", "internal_expertise",
                 "data_sensitivity", "integration_depth", "volume_economics"]

# Fictional samples. Brightpath Dental Group: 14 staff, three clinics,
# no engineers, losing after-hours bookings today (the Lesson 31 pattern).
BRIGHTPATH_DENTAL = {
    "speed_needed": 5, "no_internal_builder": 5, "process_stability": 4,
    "standard_shape": 5, "failure_is_operational": 5,
    "strategic_capability": 1, "internal_expertise": 1,
    "data_sensitivity": 3, "integration_depth": 1, "volume_economics": 1,
}

# Fictional samples. Northgate Logistics: 240 staff, an internal platform
# team, proprietary dispatch systems, very high enquiry volume.
NORTHGATE_LOGISTICS = {
    "speed_needed": 2, "no_internal_builder": 1, "process_stability": 3,
    "standard_shape": 2, "failure_is_operational": 2,
    "strategic_capability": 5, "internal_expertise": 5,
    "data_sensitivity": 4, "integration_depth": 5, "volume_economics": 5,
}


def recommend(scores: dict) -> tuple[int, int, str]:
    for factor in BUY_FACTORS + BUILD_FACTORS:
        value = scores.get(factor)
        if not isinstance(value, int) or not 1 <= value <= 5:
            raise ValueError(f"{factor} must be an integer 1-5, got {value!r}")
    buy = sum(scores[f] for f in BUY_FACTORS)
    build = sum(scores[f] for f in BUILD_FACTORS)
    lead = buy - build
    if lead >= 6:
        verdict = "BUY: use an operated service. Negotiate ownership and exit terms."
    elif lead <= -6:
        verdict = "BUILD: develop in-house. Budget for the run, not just the build."
    else:
        verdict = "HYBRID: operator builds and runs v1 while your team shadows and takes over piece by piece."
    return buy, build, verdict


def main() -> None:
    for name, scores in [("Brightpath Dental Group (fictional)", BRIGHTPATH_DENTAL),
                         ("Northgate Logistics (fictional)", NORTHGATE_LOGISTICS)]:
        buy, build, verdict = recommend(scores)
        print(f"{name}\n  buy {buy}/25   build {build}/25   -> {verdict}\n")


if __name__ == "__main__":
    main()
