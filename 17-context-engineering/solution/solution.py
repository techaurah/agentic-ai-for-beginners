"""
Lesson 17 exercise solution: relevance-ranked retrieval.

The lesson version packs retrieved documents in a fixed priority order,
which means a long, irrelevant policy can eat the budget before the one
paragraph that answers the question. The fix: score each retrieved chunk
against the user's message (here, simple keyword overlap; in production
this is what embeddings and rerankers do properly) and pack the most
relevant chunks first under their own sub-budget.

Run it:  python3 solution.py
"""

import re


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def keywords(text: str) -> set[str]:
    stop = {"the", "a", "an", "if", "i", "to", "of", "is", "it", "and",
            "what", "do", "does", "me", "my", "need"}
    return {w for w in re.findall(r"[a-z]+", text.lower()) if w not in stop}


def _matches(a: str, b: str) -> bool:
    """Loose word match: equal, or one is a prefix of the other.

    Exact matching alone misses 'cancel' vs 'cancellations', which is
    why real systems use stemming, embeddings, or a reranker. This tiny
    prefix rule is the teaching stand-in for all three.
    """
    return a == b or (min(len(a), len(b)) >= 4
                      and (a.startswith(b) or b.startswith(a)))


def relevance(chunk: str, question: str) -> int:
    chunk_words = keywords(chunk)
    return sum(1 for q in keywords(question)
               if any(_matches(q, c) for c in chunk_words))


CHUNKS = [
    ("fee_policy",
     "Cancellations under 24 hours before the appointment incur a fee "
     "equal to half the service price. The fee is added to the next bill."),
    ("cleaning_duration",
     "A cleaning takes 45 minutes including a scale, polish, and fluoride "
     "treatment, plus a brief gum check by the hygienist."),
    ("opening_hours",
     "The clinic opens 08:00 to 18:00 Monday to Saturday and is closed on "
     "Sundays and public holidays."),
    ("new_patients",
     "New patients should arrive 10 minutes early to complete forms and "
     "confirm insurance details at reception."),
    ("parking",
     "Free parking is available behind the clinic, with two accessible "
     "bays near the side entrance."),
]


def pack_retrieval(chunks: list[tuple[str, str]], question: str,
                   sub_budget: int) -> tuple[list[str], list[dict]]:
    scored = sorted(chunks, key=lambda c: relevance(c[1], question), reverse=True)
    included, report, used = [], [], 0
    for name, text in scored:
        tokens = estimate_tokens(text)
        if relevance(text, question) > 0 and used + tokens <= sub_budget:
            included.append(text)
            used += tokens
            report.append({"chunk": name, "score": relevance(text, question),
                           "tokens": tokens, "action": "included"})
        else:
            reason = "no keyword overlap" if relevance(text, question) == 0 else "over sub-budget"
            report.append({"chunk": name, "score": relevance(text, question),
                           "tokens": 0, "action": f"dropped ({reason})"})
    return included, report


if __name__ == "__main__":
    question = "What happens if I need to cancel the Friday cleaning?"
    included, report = pack_retrieval(CHUNKS, question, sub_budget=60)
    print(f"Question: {question}")
    print(f"Retrieval sub-budget: 60 tokens\n")
    for row in report:
        print(f"  {row['chunk']:<18} relevance {row['score']}  {row['action']}")
    print("\nPacked into the context, most relevant first:")
    for text in included:
        print(f"  - {text}")
