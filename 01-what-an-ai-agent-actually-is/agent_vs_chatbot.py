"""
Lesson 01 - Chatbot vs agent: the same conversation, two systems.

Run it with:

    python3 agent_vs_chatbot.py

A visitor asks a salon about a Saturday haircut, then asks to book.
The chatbot pattern-matches replies and sounds helpful, but it has no
memory and cannot change anything in the world. The agent remembers
facts, calls tools (a calendar and a booking function), and finishes
the job. Watch the trace lines: perceive, decide, act, observe.
"""

import re

# ---------------------------------------------------------------- chatbot

CHATBOT_RULES = [
    ("saturday", "We are open on Saturdays from 9:00 to 17:00."),
    ("book", "Great, I have noted that down for you."),
    ("price", "A haircut costs 25."),
    ("hello", "Hello! How can I help you today?"),
]


def chatbot_reply(message):
    """A classic keyword chatbot: stateless, tool-less, confident."""
    text = message.lower()
    for keyword, reply in CHATBOT_RULES:
        if keyword in text:
            return reply
    return "Thanks for your message. A team member will get back to you."


# ------------------------------------------------------------------- tools

CALENDAR = {
    "Saturday": ["10:00", "12:30", "15:00"],
    "Sunday": [],
    "Monday": ["09:00", "11:00"],
}
SERVICES = {"haircut": ["haircut"], "colouring": ["colouring", "coloring"]}
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ------------------------------------------------------------------- agent

class SalonAgent:
    """A tiny rule-based agent: memory, a goal, and tools it can call."""

    def __init__(self):
        self.facts = {}          # what the agent has perceived and kept
        self.bookings = []       # what the agent has actually changed
        self.trace = []          # how it got there, for us to inspect

    # tools -------------------------------------------------------------
    def check_calendar(self, day):
        return CALENDAR.get(day, [])

    def book(self, service, day, time):
        ref = f"BK-{1001 + len(self.bookings)}"
        self.bookings.append(
            {"ref": ref, "service": service, "day": day, "time": time}
        )
        return ref

    # the loop -----------------------------------------------------------
    def handle(self, message):
        self.trace = []
        text = message.lower()

        # perceive: pull facts out of the message and keep them
        for service, words in SERVICES.items():
            if any(word in text for word in words):
                self.facts["service"] = service
        for day in DAYS:
            if day.lower() in text:
                self.facts["day"] = day
        time_match = re.search(r"\b\d{1,2}:\d{2}\b", message)
        time = time_match.group(0) if time_match else None
        perceived = ", ".join(f"{k}='{v}'" for k, v in sorted(self.facts.items()))
        self.trace.append(f"perceive: {perceived}")

        # decide + act
        if "book" in text and time and "day" in self.facts:
            service = self.facts.get("service", "appointment")
            day = self.facts["day"]
            ref = self.book(service, day, time)
            self.trace.append(
                f"act: book(service='{service}', day='{day}', time='{time}') -> {ref}"
            )
            self.trace.append("decide: goal reached, confirm the booking")
            return (
                f"Booked: {service} on {day} at {time}. "
                f"Your reference is {ref}."
            )

        if "day" in self.facts and "service" in self.facts:
            day = self.facts["day"]
            service = self.facts["service"]
            slots = self.check_calendar(day)
            self.trace.append(f"act: check_calendar(day='{day}') -> {slots}")
            if slots:
                self.trace.append("decide: offer the free slots and ask for a choice")
                return (
                    f"Yes, we have {service} appointments on {day}. Free slots: "
                    f"{', '.join(slots)}. Which one would you like?"
                )
            self.trace.append("decide: no slots that day, say so honestly")
            return f"We are fully booked for {service} on {day}."

        self.trace.append("decide: not enough facts yet, ask a clarifying question")
        return "Happy to help. Which service and which day are you thinking of?"


# -------------------------------------------------------------------- demo

CONVERSATION = [
    "Hi, do you offer haircuts on Saturday morning?",
    "The 10:00 slot works. Please book it for me.",
]


def main():
    agent = SalonAgent()
    print("Lesson 01 - Chatbot vs agent")
    print("============================")
    for turn, message in enumerate(CONVERSATION, start=1):
        print(f"\nTURN {turn}")
        print(f"You:     {message}")
        print(f"Chatbot: {chatbot_reply(message)}")
        reply = agent.handle(message)
        print(f"Agent:   {reply}")
        for line in agent.trace:
            print(f"  trace: {line}")
    print("\nResult")
    print("------")
    print("Bookings the chatbot actually made: 0")
    print(f"Bookings the agent actually made:   {len(agent.bookings)}")
    for booking in agent.bookings:
        print(
            f"  {booking['ref']}: {booking['service']} on "
            f"{booking['day']} at {booking['time']}"
        )


if __name__ == "__main__":
    main()
