"""
Lesson 22 exercise solution: add a FactCheck node.

The reviewer checks that findings were used; it does not check that the
brief's claims are supported by the findings. The FactCheck node sits
between writer and reviewer, extracts the brief's bullet claims, and
verifies each one shares its key words with the finding it cites. If a
claim fails, the graph routes back to the writer with the unsupported
claim named in the review notes.

To prove the node works, the demo poisons the findings with one
hand-written "finding" whose text the writer quotes correctly, and one
brief claim is tampered with after writing: FactCheck must catch it.

Run:  python3 solution.py
"""

import re

STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "does", "you", "your", "we", "our",
    "and", "or", "of", "to", "in", "on", "for", "with", "what", "how",
    "why", "can", "i", "it", "if", "at", "by", "from", "this", "that",
}


def content_words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS}


def fact_check(state):
    """Every bullet must be supported by the finding it cites."""
    findings_by_title = {f["title"]: f for f in state["findings"]}
    unsupported = []
    for line in state["brief"].splitlines():
        if not line.startswith("- "):
            continue
        claim, _, cited = line[2:].rpartition("(")
        title = cited.rstrip(")").strip()
        finding = findings_by_title.get(title)
        if finding is None:
            unsupported.append(f"unknown source cited: {title}")
            continue
        claim_words = content_words(claim)
        finding_words = content_words(finding["text"])
        support = len(claim_words & finding_words) / max(len(claim_words), 1)
        if support < 0.5:
            unsupported.append(f"claim cites {title} but is not supported by it")
    if unsupported:
        return {"fact_check": "fail", "review_notes": "; ".join(unsupported)}
    return {"fact_check": "pass", "review_notes": ""}


class Graph:
    def __init__(self):
        self.nodes, self.edges, self.conditional = {}, {}, {}
        self.entry = None

    def add_node(self, name, fn):
        self.nodes[name] = fn

    def set_entry(self, name):
        self.entry = name

    def add_edge(self, a, b):
        self.edges[a] = b

    def add_conditional_edge(self, a, router):
        self.conditional[a] = router

    def run(self, initial_state, max_steps=12):
        state = dict(initial_state)
        current = self.entry
        steps = 0
        while current is not None:
            steps += 1
            if steps > max_steps:
                raise RuntimeError("graph exceeded max steps")
            update = self.nodes[current](state)
            state.update(update)
            print(f"  NODE {current}")
            if "fact_check" in update:
                print(f"    -> fact_check: {update['fact_check']}"
                      + (f" ({update['review_notes']})" if update["review_notes"] else ""))
            if current in self.conditional:
                current = self.conditional[current](state)
            else:
                current = self.edges.get(current)
        return state


def writer(state):
    lines = [f"Brief: {state['topic']}", ""]
    for finding in state["findings"]:
        first = finding["text"].split(". ")[0].rstrip(".") + "."
        lines.append(f"- {first} ({finding['title']})")
    if state.get("tamper") and state.get("retries", 0) == 0:
        # Simulate the classic writer failure: a plausible invented claim
        # bolted onto a real citation.
        lines.append(
            "- Installers who answer within 5 minutes win 90 percent of "
            "bookings, according to national data. (UK boiler market note)"
        )
    return {"brief": "\n".join(lines)}


def route_after_check(state):
    if state["fact_check"] == "fail" and state.get("retries", 0) < 1:
        return "writer"
    return None


def main():
    findings = [
        {"source": "market-note", "title": "UK boiler market note",
         "text": "Most boiler replacements are distress purchases: the old boiler fails and the homeowner needs heat restored within days, not weeks. Speed of response is the main reason customers choose one installer over another."},
        {"source": "missed-calls", "title": "Missed call study, home services",
         "text": "Small home-services firms miss a large share of inbound calls during working hours because engineers are on jobs. Calls that reach voicemail are rarely returned the same day."},
    ]

    print("Pass 1: honest brief")
    graph = Graph()
    graph.add_node("writer", writer)
    graph.add_node("fact_check", fact_check)
    graph.set_entry("writer")
    graph.add_edge("writer", "fact_check")
    graph.add_conditional_edge("fact_check", route_after_check)
    final = graph.run({"topic": "why firms lose bookings", "findings": findings})
    print(f"  fact_check: {final['fact_check']}")

    print("\nPass 2: writer invents a statistic (tamper on)")
    graph2 = Graph()
    graph2.add_node("writer", writer)
    graph2.add_node("fact_check", fact_check)
    graph2.set_entry("writer")
    graph2.add_edge("writer", "fact_check")

    def route2(state):
        if state["fact_check"] == "fail" and state.get("retries", 0) < 1:
            state["retries"] = state.get("retries", 0) + 1
            state["tamper"] = False  # rewrite drops the invented claim
            return "writer"
        return None

    graph2.add_conditional_edge("fact_check", route2)
    final2 = graph2.run({"topic": "why firms lose bookings",
                         "findings": findings, "tamper": True})
    print(f"  fact_check after rewrite: {final2['fact_check']}")
    print("\nFinal brief (pass 2):\n")
    print(final2["brief"])


if __name__ == "__main__":
    main()
