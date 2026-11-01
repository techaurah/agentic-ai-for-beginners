"""Qualify stage: score an enquiry and assign its band.

The extraction of signals from a raw message is the one place an LLM
belongs in this pipeline (Lesson 05 output contracts apply). The scoring
arithmetic below is deterministic code, never the model's opinion.
"""

from __future__ import annotations

from .models import WEIGHTS, Enquiry, band_for


def score_signals(signals: dict) -> int:
    """Total the eight signals, each clamped to its weight. Range 0-100."""
    # TODO(capstone): implement clamping and totalling.
    raise NotImplementedError("capstone: implement score_signals()")


def qualify(enquiry: Enquiry) -> Enquiry:
    """Set enquiry.score and enquiry.band in place and return the enquiry."""
    # TODO(capstone): use score_signals() and band_for().
    raise NotImplementedError("capstone: implement qualify()")


def extract_signals(message: str) -> dict:
    """Extract the eight signals from a raw message.

    Capstone requirement: implement this with a strict output contract.
    The offline path may use the keyword heuristics sketched in the
    lesson; the production path calls a model and validates the result
    against WEIGHTS before scoring. Either way, the return value must be
    a dict whose keys are a subset of WEIGHTS.
    """
    # TODO(capstone): implement signal extraction.
    raise NotImplementedError("capstone: implement extract_signals()")
