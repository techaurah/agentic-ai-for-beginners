"""
Lesson 20 exercise solution: contradiction detection.

The base checker catches missing citations and unsupported claims, but
not a claim that quotes a real span while asserting the opposite of it
("We cover Manchester" citing the span that says we do not). This
extension adds rule R4: if a cited span contains a negation ("do not",
"never", "no", "not") around a claim's key entity, and the claim itself
is not negated, flag a possible contradiction for human review.

It is a heuristic, deliberately: it flags for review instead of
auto-failing, because negation handling is where simple checkers lie.

Run:  python3 solution.py
"""

import re

SPANS = {
    "S10": {
        "doc": "area",
        "text": "We do not currently cover Sheffield or Manchester.",
    },
    "S11": {
        "doc": "area",
        "text": "We cover Leeds, Harrogate, and York, plus surrounding "
                "villages within a 25-mile radius of Leeds city centre.",
    },
}

STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "you", "your", "we", "our", "and",
    "or", "of", "to", "in", "on", "for", "with", "if", "up", "by", "from",
    "this", "that", "it", "its", "can", "will", "all", "any",
}

NEGATIONS = ("do not", "does not", "never", "not cover", "no longer", "n't")


def content_words(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if w not in STOPWORDS}


def is_negated(text):
    lowered = text.lower()
    return any(neg in lowered for neg in NEGATIONS)


def check_contradictions(answer, spans):
    flags = []
    for i, claim in enumerate(answer, start=1):
        if is_negated(claim["text"]):
            continue  # the claim itself is negative; nothing to flip
        claim_words = content_words(claim["text"])
        for span_id in claim["citations"]:
            span = spans.get(span_id)
            if not span:
                continue
            shared = claim_words & content_words(span["text"])
            if is_negated(span["text"]) and len(shared) >= 2:
                flags.append(
                    f"claim {i}: cited span {span_id} is NEGATED but the "
                    f"claim is positive (shared words: "
                    f"{', '.join(sorted(shared))}) -> review (rule R4)"
                )
    return flags


ANSWER = [
    {"text": "We cover Leeds and Harrogate.", "citations": ["S11"]},
    {"text": "We cover Manchester for emergency callouts.", "citations": ["S10"]},
    {"text": "We do not cover Sheffield.", "citations": ["S10"]},
]


def main():
    flags = check_contradictions(ANSWER, SPANS)
    for claim in ANSWER:
        print(f"- {claim['text']} {claim['citations']}")
    print()
    if flags:
        print(f"R4 FLAGS ({len(flags)}):")
        for flag in flags:
            print(f"  ! {flag}")
    else:
        print("R4: no contradictions flagged")
    print(
        "\nClaims 1 and 3 pass: claim 3 is safe because it repeats the "
        "span's negation\ninstead of dropping it. Claim 2 is the classic "
        "failure: right entity,\nright span, opposite meaning."
    )


if __name__ == "__main__":
    main()
