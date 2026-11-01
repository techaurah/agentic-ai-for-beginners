"""
Lesson 18 exercise solution: title boosting.

Problem: plain TF-IDF over chunk text under-ranks chunks whose document
title matches the question. "Opening hours" questions, for example, rank
the emergency chunk (which mentions the 24-hour line) about as high as
the hours chunk itself.

Fix: index each chunk's text together with its document title repeated
(title terms get extra weight), exactly how many production systems add
title and heading text to the indexed content.

Run:  python3 solution.py
"""

import math
import re
from collections import Counter

DOCS = [
    {
        "id": "services",
        "title": "Services",
        "text": (
            "Northbeam Plumbing and Heating provides boiler repairs, boiler "
            "installation, emergency plumbing, bathroom fitting, and annual "
            "boiler servicing. Every engineer is Gas Safe registered and DBS "
            "checked. We work on all major boiler brands including Worcester "
            "Bosch, Vaillant, and Ideal."
        ),
    },
    {
        "id": "hours",
        "title": "Opening hours",
        "text": (
            "Our office is open Monday to Friday from 8:00 to 18:00 and on "
            "Saturday from 9:00 to 13:00. We are closed on Sundays and bank "
            "holidays. The emergency line is answered 24 hours a day, 7 days "
            "a week, including holidays."
        ),
    },
    {
        "id": "pricing",
        "title": "Pricing",
        "text": (
            "A boiler repair callout costs 85 pounds, which is deducted from "
            "the final bill if you go ahead with the repair. An annual boiler "
            "service costs 95 pounds. New boiler installation starts from "
            "1950 pounds including the boiler, fitting, and disposal of the "
            "old unit."
        ),
    },
    {
        "id": "warranty",
        "title": "Warranty",
        "text": (
            "All boiler repairs carry a 12-month warranty covering parts and "
            "labour. If the same fault returns within 12 months, we fix it "
            "free of charge. New boiler installations carry a 5-year warranty "
            "on parts and labour when the boiler is serviced annually by us."
        ),
    },
    {
        "id": "booking",
        "title": "Booking and cancellations",
        "text": (
            "You can book a visit by phone or through the booking form on our "
            "website. We confirm every appointment by text message the day "
            "before. You can cancel or move an appointment free of charge up "
            "to 4 hours before the visit. Later cancellations are charged at "
            "40 pounds."
        ),
    },
    {
        "id": "area",
        "title": "Service area",
        "text": (
            "We cover Leeds, Harrogate, and York, plus surrounding villages "
            "within a 25-mile radius of Leeds city centre. Emergency callouts "
            "outside this area are sometimes possible for an extra travel "
            "charge. We do not currently cover Sheffield or Manchester."
        ),
    },
    {
        "id": "emergency",
        "title": "Emergencies",
        "text": (
            "For burst pipes, leaks, or a boiler that has stopped in cold "
            "weather, call the emergency line at any time. Inside our service "
            "area we aim to arrive within 2 hours. Turn off your stopcock and "
            "boiler before the engineer arrives if water is leaking."
        ),
    },
    {
        "id": "payment",
        "title": "Payment",
        "text": (
            "We accept card payments and bank transfer. We do not accept "
            "cash. For installations over 1000 pounds we offer a monthly "
            "payment plan over 12 or 24 months, subject to a quick credit "
            "check."
        ),
    },
]

STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "does", "you", "your", "we", "our",
    "and", "or", "of", "to", "in", "on", "for", "with", "what", "how",
    "much", "many", "can", "i", "it", "if", "at", "by", "from", "this",
    "when", "open",
}


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def content_tokens(text):
    return [t for t in tokenize(text) if t not in STOPWORDS]


def split_sentences(text):
    return [p for p in re.split(r"(?<=[.!?])\s+", text.strip()) if p]


def chunk_document(doc, max_words=35):
    chunks, current, words = [], [], 0
    for sentence in split_sentences(doc["text"]):
        w = len(sentence.split())
        if current and words + w > max_words:
            chunks.append(" ".join(current))
            current, words = [], 0
        current.append(sentence)
        words += w
    if current:
        chunks.append(" ".join(current))
    return [{"doc_id": doc["id"], "title": doc["title"], "text": t} for t in chunks]


class TfidfIndex:
    """With title_boost, the document title is indexed alongside the text."""

    def __init__(self, chunks, title_boost=0):
        self.chunks = chunks
        self.idf = {}
        self.vectors = []
        n = len(chunks)
        doc_freq = Counter()
        tokenized = []
        for chunk in chunks:
            tokens = content_tokens(chunk["text"])
            # The change: repeat the title terms so they weigh more.
            tokens += content_tokens(chunk["title"]) * title_boost
            tokenized.append(tokens)
            for token in set(tokens):
                doc_freq[token] += 1
        for token, df in doc_freq.items():
            self.idf[token] = math.log((1 + n) / (1 + df)) + 1.0
        for tokens in tokenized:
            counts = Counter(tokens)
            total = max(len(tokens), 1)
            self.vectors.append(
                {t: (c / total) * self.idf.get(t, 1.0) for t, c in counts.items()}
            )

    def search(self, query, k=3):
        q_counts = Counter(content_tokens(query))
        q_total = max(sum(q_counts.values()), 1)
        q_vec = {t: (c / q_total) * self.idf.get(t, 1.0) for t, c in q_counts.items()}
        scored = []
        for i, vec in enumerate(self.vectors):
            dot = sum(w * vec.get(t, 0.0) for t, w in q_vec.items())
            na = math.sqrt(sum(w * w for w in q_vec.values()))
            nb = math.sqrt(sum(w * w for w in vec.values()))
            score = dot / (na * nb) if na and nb else 0.0
            scored.append((score, self.chunks[i]["doc_id"]))
        scored.sort(reverse=True)
        return [(s, d) for s, d in scored[:k] if s > 0.0]


def main():
    chunks = []
    for doc in DOCS:
        chunks.extend(chunk_document(doc))
    query = "What are your opening hours?"
    plain = TfidfIndex(chunks, title_boost=0)
    boosted = TfidfIndex(chunks, title_boost=2)
    print(f"Q: {query}")
    print("Without title boost:", [(d, round(s, 3)) for s, d in plain.search(query)])
    print("With title boost:   ", [(d, round(s, 3)) for s, d in boosted.search(query)])
    print(
        "\nWithout the boost the right chunk wins by a whisker (0.242 vs "
        "0.202),\nbecause 'hours' does almost no work as body text. With "
        "the title counted,\nthe margin is decisive (0.678) and the "
        "misleading chunks fall away.\nMetadata is part of the document."
    )


if __name__ == "__main__":
    main()
