"""
Lesson 19: Agentic RAG: retrieval as a tool.

In Lesson 18 the pipeline always retrieved, once, with the raw question.
Here the index sits behind a tool interface and a small agent decides:
  - does this message need the knowledge base at all?
  - is it really two questions in one sentence?
  - did the first search land? If not, reformulate and search again.
  - is there actually evidence? If not, say so instead of bluffing.

The agent's "brain" is a small rule-based planner so the lesson runs
offline and deterministically. In production an LLM makes these calls;
the tool contract and the loop are identical.

Run:  python3 agentic_rag.py
"""

import math
import re
from collections import Counter

# --- Corpus and index (the Lesson 18 pipeline, condensed) -------------------

DOCS = [
    {"id": "services", "title": "Services", "text": "Northbeam Plumbing and Heating provides boiler repairs, boiler installation, emergency plumbing, bathroom fitting, and annual boiler servicing. Every engineer is Gas Safe registered and DBS checked."},
    {"id": "hours", "title": "Opening hours", "text": "Our opening hours are Monday to Friday from 8:00 to 18:00 and Saturday from 9:00 to 13:00. We are closed on Sundays and bank holidays. The emergency line is answered 24 hours a day, 7 days a week, including holidays."},
    {"id": "pricing", "title": "Pricing", "text": "A boiler repair callout costs 85 pounds, which is deducted from the final bill if you go ahead with the repair. An annual boiler service costs 95 pounds. New boiler installation starts from 1950 pounds including the boiler, fitting, and disposal of the old unit."},
    {"id": "warranty", "title": "Warranty", "text": "All boiler repairs carry a 12-month warranty covering parts and labour. If the same fault returns within 12 months, we fix it free of charge. New boiler installations carry a 5-year warranty on parts and labour when the boiler is serviced annually by us."},
    {"id": "booking", "title": "Booking and cancellations", "text": "You can book a visit by phone or through the booking form on our website. We confirm every appointment by text message the day before. You can cancel or move an appointment free of charge up to 4 hours before the visit. Later cancellations are charged at 40 pounds."},
    {"id": "area", "title": "Service area", "text": "We cover Leeds, Harrogate, and York, plus surrounding villages within a 25-mile radius of Leeds city centre. Emergency callouts outside this area are sometimes possible for an extra travel charge. We do not currently cover Sheffield or Manchester."},
    {"id": "emergency", "title": "Emergencies", "text": "For burst pipes, leaks, or a boiler that has stopped in cold weather, call the emergency line at any time. Inside our service area we aim to arrive within 2 hours. Turn off your stopcock and boiler before the engineer arrives if water is leaking."},
    {"id": "payment", "title": "Payment", "text": "We accept card payments and bank transfer. We do not accept cash. For installations over 1000 pounds we offer a monthly payment plan over 12 or 24 months, subject to a quick credit check."},
]

STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "does", "you", "your", "we", "our",
    "and", "or", "of", "to", "in", "on", "for", "with", "what", "how",
    "much", "many", "can", "i", "it", "if", "at", "by", "from", "this",
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
    def __init__(self, chunks):
        self.chunks = chunks
        self.idf = {}
        self.vectors = []
        n = len(chunks)
        doc_freq = Counter()
        tokenized = []
        for chunk in chunks:
            tokens = content_tokens(chunk["text"]) + content_tokens(chunk["title"])
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
            scored.append((score, self.chunks[i]))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [(s, c) for s, c in scored[:k] if s > 0.0]


# --- The tool interface ------------------------------------------------------
# This dict is the contract an LLM would see: name, description, parameters.
# The function is what actually runs. Keep this shape in mind; it is the
# same contract LangChain, LlamaIndex, and MCP all use, with different
# packaging (see the lesson README).

SEARCH_TOOL = {
    "name": "search_knowledge_base",
    "description": (
        "Search the Northbeam knowledge base for facts about services, "
        "prices, hours, warranty, booking, service area, emergencies, "
        "and payment. Returns the best-matching passages with scores."
    ),
    "parameters": {
        "query": "string, a focused search phrase",
        "k": "integer, how many passages to return (default 3)",
    },
}

CHUNKS = []
for _doc in DOCS:
    CHUNKS.extend(chunk_document(_doc))
INDEX = TfidfIndex(CHUNKS)


def search_knowledge_base(query, k=3):
    """The tool itself. Returns passages, not an answer."""
    return [
        {"score": round(score, 3), "doc_id": chunk["doc_id"], "text": chunk["text"]}
        for score, chunk in INDEX.search(query, k=k)
    ]


# --- The agent ---------------------------------------------------------------
# A deterministic planner standing in for the LLM. It demonstrates the
# decision points; an LLM-driven agent makes the same points with prompts.

MIN_SCORE = 0.15  # below this, a search counts as "no useful evidence"

SMALLTALK = ("hello", "hi there", "how are you", "thank", "good morning",
             "good afternoon", "bye")

# Words users use that the corpus phrases differently.
SYNONYMS = {"open": "opening hours", "cost": "price", "pay": "payment"}
# Extra words allowed when matching answer sentences to a sub-question.
EXPANSIONS = {"opening": {"open"}, "cost": {"costs"}, "pay": {"payment"}}


class Agent:
    def log(self, message):
        print(f"   {message}")

    def needs_retrieval(self, question):
        q = question.lower()
        return not any(phrase in q for phrase in SMALLTALK)

    def split_question(self, question):
        """Split a compound question into sub-questions on ' and ' joins."""
        parts = re.split(r"\s+and\s+", question.strip().rstrip("?"), flags=re.I)
        parts = [p.strip() for p in parts if len(p.split()) >= 3]
        return parts if len(parts) > 1 else [question]

    def reformulate(self, query):
        words = content_tokens(query)
        return " ".join(SYNONYMS.get(w, w) for w in words)

    def search_with_retry(self, sub_question):
        results = search_knowledge_base(sub_question)
        best = results[0]["score"] if results else 0.0
        self.log(
            f'TOOL search_knowledge_base("{sub_question}") '
            f"-> {len(results)} passages, best score {best}"
        )
        if best < MIN_SCORE:
            retry_query = self.reformulate(sub_question)
            if retry_query != sub_question:
                results = search_knowledge_base(retry_query)
                best = results[0]["score"] if results else 0.0
                self.log(f'TOOL retry as "{retry_query}" -> best score {best}')
        return results if best >= MIN_SCORE else []

    @staticmethod
    def pick_sentence(sub_question, passages):
        """Best-supported sentence for one sub-question, or None."""
        words = set(content_tokens(sub_question))
        for word in list(words):
            words |= EXPANSIONS.get(word, set())
        best_sentence, best_overlap, best_doc = None, 0, None
        for passage in passages:
            for sentence in split_sentences(passage["text"]):
                overlap = len(words & set(content_tokens(sentence)))
                if overlap > best_overlap:
                    best_sentence, best_overlap, best_doc = (
                        sentence, overlap, passage["doc_id"])
        return (best_sentence, best_doc) if best_sentence else (None, None)

    def answer(self, question):
        print(f"\nQ: {question}")
        if not self.needs_retrieval(question):
            self.log("PLAN small talk; no knowledge-base search needed")
            print("A: Happy to help. For anything about Northbeam services, "
                  "prices, or bookings, just ask.")
            return
        sub_questions = self.split_question(question)
        if len(sub_questions) > 1:
            self.log(f"PLAN split into {len(sub_questions)} sub-questions")
        picked, sources = [], []
        for sub in sub_questions:
            passages = self.search_with_retry(sub)
            sentence, doc_id = self.pick_sentence(sub, passages)
            if sentence and sentence not in picked:
                picked.append(sentence)
                if doc_id not in sources:
                    sources.append(doc_id)
        if not picked:
            print("A: I checked the knowledge base and could not find that. "
                  "It may not be something Northbeam offers.")
            return
        print(f"A: {' '.join(picked)} (Sources: {', '.join(sources)})")


def main():
    agent = Agent()
    agent.answer("Hello, how are you today?")
    agent.answer("What are your opening hours and do you offer a warranty on boiler repairs?")
    agent.answer("How much does a callout cost?")
    agent.answer("Do you rent out scaffolding towers?")


if __name__ == "__main__":
    main()
