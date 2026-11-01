"""
Lesson 18: RAG from scratch.

A complete retrieval-augmented generation pipeline in pure Python:
chunk -> embed (hand-rolled TF-IDF) -> retrieve (cosine) -> answer
(template composer standing in for the LLM call).

No third-party packages, no network, no API keys. Run it:

    python3 rag.py

The corpus is a small knowledge base for a fictional company,
Northbeam Plumbing and Heating. Swap the corpus and you have the
skeleton of every RAG system you will ever build.
"""

import math
import re
from collections import Counter

# ---------------------------------------------------------------------------
# 1. The corpus: raw documents, as they would arrive from a website,
#    a help centre, or a folder of policy files.
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# 2. Chunking: split documents into small, retrievable pieces.
#    Strategy here: group sentences into chunks of at most ~35 words.
# ---------------------------------------------------------------------------


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def chunk_document(doc, max_words=35):
    chunks = []
    current = []
    current_words = 0
    for sentence in split_sentences(doc["text"]):
        words = len(sentence.split())
        if current and current_words + words > max_words:
            chunks.append(" ".join(current))
            current, current_words = [], 0
        current.append(sentence)
        current_words += words
    if current:
        chunks.append(" ".join(current))
    return [
        {"doc_id": doc["id"], "title": doc["title"], "text": text}
        for text in chunks
    ]


# ---------------------------------------------------------------------------
# 3. Embedding, hand-rolled: TF-IDF vectors.
#    A word is weighted by how often it appears in a chunk (TF) and how
#    rare it is across all chunks (IDF). Vectors are plain dicts.
# ---------------------------------------------------------------------------

STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "does", "you", "your", "we", "our",
    "and", "or", "of", "to", "in", "on", "for", "with", "what", "how",
    "much", "many", "can", "i", "it", "if", "at", "by", "from", "this",
}


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def content_tokens(text):
    return [t for t in tokenize(text) if t not in STOPWORDS]


class TfidfIndex:
    def __init__(self, chunks):
        self.chunks = chunks
        self.idf = {}
        self.vectors = []
        n = len(chunks)
        doc_freq = Counter()
        tokenized = []
        for chunk in chunks:
            tokens = content_tokens(chunk["text"])
            tokenized.append(tokens)
            for token in set(tokens):
                doc_freq[token] += 1
        for token, df in doc_freq.items():
            self.idf[token] = math.log((1 + n) / (1 + df)) + 1.0
        for tokens in tokenized:
            self.vectors.append(self._vectorize(tokens))

    def _vectorize(self, tokens):
        counts = Counter(tokens)
        total = max(len(tokens), 1)
        return {
            token: (count / total) * self.idf.get(token, 1.0)
            for token, count in counts.items()
        }

    def embed_query(self, query):
        return self._vectorize(content_tokens(query))

    @staticmethod
    def cosine(a, b):
        dot = sum(weight * b.get(token, 0.0) for token, weight in a.items())
        norm_a = math.sqrt(sum(w * w for w in a.values()))
        norm_b = math.sqrt(sum(w * w for w in b.values()))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    def search(self, query, k=3):
        query_vector = self.embed_query(query)
        scored = [
            (self.cosine(query_vector, vector), i)
            for i, vector in enumerate(self.vectors)
        ]
        scored.sort(reverse=True)
        return [
            (score, self.chunks[i]) for score, i in scored[:k] if score > 0.0
        ]


# ---------------------------------------------------------------------------
# 4. Answering: retrieve, then compose.
#    In production an LLM writes this answer from the retrieved chunks.
#    Here a small template composer picks the sentences that share words
#    with the question, so the whole pipeline runs offline and you can
#    see exactly what the model would be given.
# ---------------------------------------------------------------------------


def compose_answer(query, results):
    if not results:
        return "I could not find anything about that in the knowledge base."
    query_words = set(content_tokens(query))
    picked = []
    for _score, chunk in results:
        for sentence in split_sentences(chunk["text"]):
            overlap = query_words & set(content_tokens(sentence))
            if overlap and sentence not in picked:
                picked.append(sentence)
    if not picked:
        picked = [split_sentences(results[0][1]["text"])[0]]
    sources = []
    for _score, chunk in results:
        if chunk["doc_id"] not in sources:
            sources.append(chunk["doc_id"])
    body = " ".join(picked[:3])
    return f"{body} (Sources: {', '.join(sources)})"


def ask(index, query):
    results = index.search(query, k=3)
    print(f"\nQ: {query}")
    for score, chunk in results:
        preview = chunk["text"][:70].replace("\n", " ")
        print(f"   [{score:.3f}] {chunk['doc_id']}: {preview}...")
    print(f"A: {compose_answer(query, results)}")


def main():
    chunks = []
    for doc in DOCS:
        chunks.extend(chunk_document(doc))
    index = TfidfIndex(chunks)
    print(f"Indexed {len(DOCS)} documents as {len(chunks)} chunks.")

    ask(index, "How much does a boiler repair callout cost?")
    ask(index, "Do you offer a warranty on boiler repairs?")
    ask(index, "Can I pay for a new boiler in monthly instalments?")
    ask(index, "Do you cover Manchester?")
    ask(index, "Do you sell garden furniture?")


if __name__ == "__main__":
    main()
