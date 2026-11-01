"""
Lesson 19 exercise solution: a second tool, and choosing between tools.

The agent gains a structured lookup tool, get_opening_hours(day), which
reads a small table instead of searching prose. The planner now routes:
hours questions for a specific day go to the lookup tool, everything
else factual goes to search. This is the core agentic-RAG skill: the
right source for the question, not search for everything.

Run:  python3 solution.py
"""

import re

HOURS_TABLE = {
    "monday": "8:00 to 18:00",
    "tuesday": "8:00 to 18:00",
    "wednesday": "8:00 to 18:00",
    "thursday": "8:00 to 18:00",
    "friday": "8:00 to 18:00",
    "saturday": "9:00 to 13:00",
    "sunday": "closed (emergency line only)",
}

GET_HOURS_TOOL = {
    "name": "get_opening_hours",
    "description": "Look up office opening hours for one weekday.",
    "parameters": {"day": "string, weekday name, e.g. 'saturday'"},
}

SEARCH_TOOL = {
    "name": "search_knowledge_base",
    "description": "Search company facts: prices, warranty, booking, area, payment.",
    "parameters": {"query": "string, focused search phrase"},
}

KB = {
    "warranty": "All boiler repairs carry a 12-month warranty covering parts and labour.",
    "pricing": "A boiler repair callout costs 85 pounds, deducted from the final bill if you go ahead.",
    "booking": "Book by phone or the website form; we confirm by text the day before.",
}


def get_opening_hours(day):
    return HOURS_TABLE.get(day.lower(), "unknown day")


def search_knowledge_base(query):
    words = set(re.findall(r"[a-z]+", query.lower()))
    for topic, text in KB.items():
        if topic in words or (topic == "pricing" and "cost" in words):
            return text
    return ""


class RouterAgent:
    def route(self, question):
        q = question.lower()
        day = next((d for d in HOURS_TABLE if d in q), None)
        if day and ("open" in q or "hours" in q or "close" in q):
            return ("get_opening_hours", {"day": day})
        return ("search_knowledge_base", {"query": question})

    def answer(self, question):
        print(f"\nQ: {question}")
        tool, args = self.route(question)
        print(f"   PLAN tool={tool} args={args}")
        if tool == "get_opening_hours":
            result = get_opening_hours(**args)
            print(f"   TOOL get_opening_hours -> {result}")
            print(f"A: On {args['day'].capitalize()} we are open {result}.")
        else:
            result = search_knowledge_base(**args)
            print(f"   TOOL search_knowledge_base -> {result[:50]}...")
            print(f"A: {result}" if result else "A: Nothing found on that.")


def main():
    agent = RouterAgent()
    agent.answer("Are you open on Saturday?")
    agent.answer("What warranty do I get on a boiler repair?")
    agent.answer("How much does a callout cost?")


if __name__ == "__main__":
    main()
