"""
Lesson 22: A two-agent workflow as an explicit state graph.

A Researcher gathers findings from a source corpus; a Writer turns the
findings into a short brief; a Review step checks the brief against the
findings and can send it back once for a rewrite.

The graph engine here is a small teaching model written in pure Python:
shared state, named nodes, edges, and one conditional edge. It mirrors
LangGraph's model closely, and the lesson README maps every piece to
the real framework. Using a teaching model first means the graph is
something you can read in one sitting, not something you import.

Run:  python3 researcher_writer_graph.py
"""

import re

# --- Source corpus the Researcher can search ---------------------------------
# In production these would be documents, web results, or database rows.

SOURCES = [
    {"id": "market-note", "title": "UK boiler market note",
     "text": "Most boiler replacements are distress purchases: the old boiler fails and the homeowner needs heat restored within days, not weeks. Speed of response is the main reason customers choose one installer over another."},
    {"id": "missed-calls", "title": "Missed call study, home services",
     "text": "Small home-services firms miss a large share of inbound calls during working hours because engineers are on jobs. Calls that reach voicemail are rarely returned the same day, and the customer usually books the next firm that answers."},
    {"id": "reviews", "title": "Review platform analysis",
     "text": "Firms that reply to every review within a day rate noticeably higher than firms that reply sporadically. Customers mention response speed in reviews almost as often as they mention the quality of the work itself."},
    {"id": "pricing-page", "title": "Pricing transparency note",
     "text": "Publishing clear callout and servicing prices reduces tyre-kicker enquiries and increases completed bookings, because customers can self-qualify before they pick up the phone."},
    {"id": "out-of-scope", "title": "History of the barometer",
     "text": "The barometer was developed in the seventeenth century to measure atmospheric pressure and predict changes in the weather."},
]

STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "does", "you", "your", "we", "our",
    "and", "or", "of", "to", "in", "on", "for", "with", "what", "how",
    "why", "can", "i", "it", "if", "at", "by", "from", "this", "that",
}


def content_words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS}


# --- Nodes -------------------------------------------------------------------
# Each node receives the shared state and returns a partial update.
# Nodes never call each other directly; the graph decides what runs next.

def researcher(state):
    topic_words = content_words(state["topic"])
    scored = []
    for source in SOURCES:
        overlap = len(topic_words & content_words(source["text"] + " " + source["title"]))
        if overlap > 0:
            scored.append((overlap, source))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    findings = [
        {"source": source["id"], "title": source["title"], "text": source["text"]}
        for _score, source in scored[:3]
    ]
    return {"findings": findings}


def writer(state):
    findings = state["findings"]
    # Default style: keep briefs to the two strongest findings. When the
    # reviewer sends notes back, completeness beats brevity.
    chosen = findings if state.get("review_notes") else findings[:2]
    lines = [f"Brief: {state['topic']}", ""]
    for finding in chosen:
        first_sentence = finding["text"].split(". ")[0].rstrip(".") + "."
        lines.append(f"- {first_sentence} ({finding['title']})")
    if state.get("review_notes"):
        lines.append("")
        lines.append(f"Editor note addressed: {state['review_notes']}")
    return {"brief": "\n".join(lines)}


def reviewer(state):
    """Check the brief actually uses the findings. Returns a verdict."""
    brief = state.get("brief", "")
    missing = [
        f["title"] for f in state["findings"]
        if f["title"] not in brief
    ]
    retries = state.get("retries", 0)
    if missing and retries < 1:
        return {
            "verdict": "rewrite",
            "review_notes": f"include findings from: {', '.join(missing)}",
            "retries": retries + 1,
        }
    return {"verdict": "accept", "review_notes": ""}


# --- The graph engine (teaching model) ---------------------------------------

class Graph:
    """A minimal state graph: nodes, fixed edges, conditional edges."""

    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.conditional = {}
        self.entry = None

    def add_node(self, name, fn):
        self.nodes[name] = fn

    def set_entry(self, name):
        self.entry = name

    def add_edge(self, from_node, to_node):
        self.edges[from_node] = to_node

    def add_conditional_edge(self, from_node, router):
        """router(state) returns the next node name, or None to finish."""
        self.conditional[from_node] = router

    def run(self, initial_state, max_steps=12):
        state = dict(initial_state)
        current = self.entry
        steps = 0
        while current is not None:
            steps += 1
            if steps > max_steps:
                raise RuntimeError(f"graph exceeded {max_steps} steps; "
                                   f"a loop guard every graph needs")
            update = self.nodes[current](state)
            state.update(update)
            summary = {}
            for k, v in update.items():
                if isinstance(v, list):
                    summary[k] = f"<{len(v)} items>"
                elif isinstance(v, str) and len(v) > 45:
                    summary[k] = v[:45].replace("\n", " ") + "..."
                else:
                    summary[k] = v
            print(f"  NODE {current}: {summary}")
            if current in self.conditional:
                current = self.conditional[current](state)
            else:
                current = self.edges.get(current)
        return state


def route_after_review(state):
    return "writer" if state.get("verdict") == "rewrite" else None


def build_graph():
    graph = Graph()
    graph.add_node("researcher", researcher)
    graph.add_node("writer", writer)
    graph.add_node("reviewer", reviewer)
    graph.set_entry("researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_conditional_edge("reviewer", route_after_review)
    return graph


# --- Demo ---------------------------------------------------------------------

def main():
    print("Topic: why do small plumbing firms lose bookings they should win?")
    print("Running graph: researcher -> writer -> reviewer (- rewrite once -> writer)")
    graph = build_graph()
    final = graph.run({
        "topic": "why small plumbing firms lose bookings: missed calls, "
                 "slow response, pricing and reviews",
    })
    print("\nFinal brief:\n")
    print(final["brief"])
    print(f"\nVerdict: {final['verdict']} after {final.get('retries', 0)} rewrite(s)")


if __name__ == "__main__":
    main()
