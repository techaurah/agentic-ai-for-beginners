"""
Lesson 20: Grounding and citations.

An answer is grounded when every claim in it can be traced to a source
span: a specific sentence in a specific document. This lesson builds:
  1. a span store (documents split into citable units, S1, S2, ...),
  2. an answer format where every claim carries its citations,
  3. a checker that FAILS an answer when a claim has no citation, cites
     a span that does not exist, or cites a span that does not actually
     support the claim.

The composer here is template-based so the lesson runs offline. With a
real LLM the composer changes; the checker does not. That is the point:
verification is code, not hope.

Run:  python3 grounded_answers.py
"""

import re

# --- 1. The span store -------------------------------------------------------
# Same Northbeam facts as Lessons 18-19, split into citable sentences.

DOCUMENTS = {
    "pricing": (
        "A boiler repair callout costs 85 pounds, which is deducted from "
        "the final bill if you go ahead with the repair. An annual boiler "
        "service costs 95 pounds. New boiler installation starts from 1950 "
        "pounds including the boiler, fitting, and disposal of the old unit."
    ),
    "warranty": (
        "All boiler repairs carry a 12-month warranty covering parts and "
        "labour. If the same fault returns within 12 months, we fix it free "
        "of charge. New boiler installations carry a 5-year warranty on "
        "parts and labour when the boiler is serviced annually by us."
    ),
    "booking": (
        "You can book a visit by phone or through the booking form on our "
        "website. We confirm every appointment by text message the day "
        "before. You can cancel or move an appointment free of charge up to "
        "4 hours before the visit."
    ),
    "area": (
        "We cover Leeds, Harrogate, and York, plus surrounding villages "
        "within a 25-mile radius of Leeds city centre. We do not currently "
        "cover Sheffield or Manchester."
    ),
}


def build_spans(documents):
    spans = {}
    counter = 0
    for doc_id, text in documents.items():
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s]
        for sentence in sentences:
            counter += 1
            spans[f"S{counter}"] = {"doc": doc_id, "text": sentence}
    return spans


SPANS = build_spans(DOCUMENTS)

STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "does", "you", "your", "we", "our",
    "and", "or", "of", "to", "in", "on", "for", "with", "if", "up", "by",
    "from", "this", "that", "it", "its", "can", "will", "all", "any",
}


def content_words(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if w not in STOPWORDS}


# --- 2. The answer format ----------------------------------------------------
# An answer is a list of claims. Each claim: text + the span ids that are
# supposed to support it. Rendering adds the familiar [S1] markers.

GOOD_ANSWER = [
    {
        "text": "A boiler repair callout costs 85 pounds, deducted from the "
                "final bill if you go ahead with the repair.",
        "citations": ["S1"],
    },
    {
        "text": "Repairs carry a 12-month warranty covering parts and labour.",
        "citations": ["S4"],
    },
    {
        "text": "You can cancel an appointment free of charge up to 4 hours "
                "before the visit.",
        "citations": ["S9"],
    },
]

# The same answer, the way an unguarded model actually writes it: one
# claim lost its citation, one cites a real span that says something
# else, and one number was quietly "improved".
BAD_ANSWER = [
    {
        "text": "A boiler repair callout costs 85 pounds, deducted from the "
                "final bill if you go ahead with the repair.",
        "citations": ["S1"],
    },
    {
        "text": "Repairs carry a 12-month warranty covering parts and labour.",
        "citations": [],  # uncited claim
    },
    {
        "text": "You can cancel an appointment free of charge up to 24 hours "
                "before the visit.",
        "citations": ["S9"],  # span says 4 hours, not 24
    },
    {
        "text": "We cover Manchester for emergency callouts.",
        "citations": ["S11"],  # real span, but it says the opposite
    },
]


def render(answer):
    lines = []
    for claim in answer:
        marks = "".join(f"[{c}]" for c in claim["citations"])
        lines.append(f"- {claim['text']} {marks}".rstrip())
    return "\n".join(lines)


# --- 3. The checker ----------------------------------------------------------
# Rules:
#   R1 every claim must carry at least one citation.
#   R2 every cited span must exist.
#   R3 the cited spans must support the claim: at least SUPPORT_THRESHOLD
#      of the claim's content words must appear in the cited text, and
#      every number in the claim must appear in the cited text (numbers
#      are where quiet fabrications live).

SUPPORT_THRESHOLD = 0.5


def numbers_in(text):
    return re.findall(r"\d+(?:\.\d+)?", text)


def check_answer(answer, spans):
    violations = []
    for i, claim in enumerate(answer, start=1):
        label = f"claim {i} ({claim['text'][:45]}...)"
        if not claim["citations"]:
            violations.append(f"{label}: NO CITATION (rule R1)")
            continue
        cited_text = ""
        for span_id in claim["citations"]:
            if span_id not in spans:
                violations.append(f"{label}: cites unknown span {span_id} (rule R2)")
            else:
                cited_text += " " + spans[span_id]["text"]
        if not cited_text:
            continue
        claim_words = content_words(claim["text"])
        cited_words = content_words(cited_text)
        if claim_words:
            support = len(claim_words & cited_words) / len(claim_words)
            if support < SUPPORT_THRESHOLD:
                violations.append(
                    f"{label}: cited span supports only {support:.0%} of the "
                    f"claim's key words (rule R3)"
                )
        for number in numbers_in(claim["text"]):
            if number not in numbers_in(cited_text):
                violations.append(
                    f"{label}: number {number} does not appear in the cited "
                    f"span (rule R3)"
                )
    return violations


def report(name, answer):
    print(f"\n--- {name} ---")
    print(render(answer))
    violations = check_answer(answer, SPANS)
    if violations:
        print(f"CHECKER: FAIL ({len(violations)} violations)")
        for violation in violations:
            print(f"  x {violation}")
    else:
        print(f"CHECKER: PASS ({len(answer)} claims, all cited and supported)")
    return violations


def main():
    print("Span store:")
    for span_id, span in SPANS.items():
        print(f"  {span_id} [{span['doc']}] {span['text'][:60]}...")
    report("Answer A: written with citations", GOOD_ANSWER)
    report("Answer B: written the way unguarded models write", BAD_ANSWER)
    print(
        "\nAnswer B reads just as smoothly as Answer A, and the checker "
        "catches two of\nits three flaws. The third, a dropped negation in "
        "claim 4, slips through:\nthe cited span really does mention "
        "Manchester, it just says the opposite.\nClosing that hole is this "
        "lesson's exercise."
    )


if __name__ == "__main__":
    main()
