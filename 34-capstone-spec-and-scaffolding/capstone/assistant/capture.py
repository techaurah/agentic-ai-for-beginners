"""Capture stage: normalise raw channel payloads into Enquiry objects.

Interface is fixed. Implementation is yours.
"""

from __future__ import annotations

from .models import Enquiry


def capture(raw_enquiries: list[dict]) -> list[Enquiry]:
    """Turn raw enquiry dicts into Enquiry objects, deduplicated.

    Requirements (spec section 2):
    - Dedupe on the normalised contact (strip whitespace, lowercase).
    - A repeat contact stays ONE enquiry: keep the first id, replace the
      message with the newest one, and raise its activity signal by 2,
      capped at the activity weight.
    - Never mutate the caller's dicts.
    - Return enquiries in first-seen order.
    """
    # TODO(capstone): implement capture with dedupe and the repeat boost.
    raise NotImplementedError("capstone: implement capture()")
