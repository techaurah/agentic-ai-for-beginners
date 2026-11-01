"""Lesson 11 exercise solution: ReAct when a tool cannot answer.

The question asks the price of a root canal, which is not in the price
list. A careless agent invents a number. This one reads the observation,
says what it does not know, still answers the half of the question it can
(the Saturday calendar), and hands the missing price to a human to
confirm. Not hallucinating is a behaviour you design, not a hope.

Run:  python3 solution.py
"""

PRICES = {"teeth whitening": 299, "emergency repair": 150, "routine checkup": 80}
CALENDAR = {"friday": ["09:00", "14:00"], "saturday": ["10:00"]}


def price_lookup(service: str) -> str:
    price = PRICES.get(service.lower())
    return f"{service}: GBP {price}" if price else f"{service}: not in the price list"


def calendar_lookup(day: str) -> str:
    slots = CALENDAR.get(day.lower(), [])
    return f"{day}: free slots {slots}" if slots else f"{day}: fully booked"


TOOLS = {"price_lookup": price_lookup, "calendar_lookup": calendar_lookup}


def react(question: str) -> None:
    print(f"question: {question}")
    steps = [
        (
            "The question has two parts: a root canal price and Saturday hours. Price first.",
            "price_lookup",
            {"service": "root canal"},
        ),
        (
            "The price list has no root canal entry. I will NOT guess a number. "
            "I can still answer the calendar half, then flag the price for a human.",
            "calendar_lookup",
            {"day": "saturday"},
        ),
    ]
    observations = []
    for thought, tool, args in steps:
        print(f"  Thought:     {thought}")
        print(f"  Action:      {tool}({args})")
        observation = TOOLS[tool](**args)
        observations.append(observation)
        print(f"  Observation: {observation}")
    print("  Final answer: I cannot quote a root canal price from our list,")
    print("                so I will not invent one: a member of the team will")
    print("                confirm it. Saturday does have a free slot at 10:00")
    print("                if you would like us to hold it meanwhile.")
    print("  Handoff note:  root canal pricing requested, not in price list.")


if __name__ == "__main__":
    react("What does a root canal cost, and are you open Saturday?")
