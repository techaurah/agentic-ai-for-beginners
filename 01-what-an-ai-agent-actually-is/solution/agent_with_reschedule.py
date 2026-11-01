"""
Lesson 01 - Exercise solution: the agent learns to reschedule.

Adds a third turn to the demo conversation. The visitor changes their
mind, so the agent needs a new tool (cancel_booking) and a new rule:
when someone asks to move a booking, cancel the old one first, then
book the new time. The chatbot, as ever, books nothing and cancels
nothing, but sounds perfectly pleasant about it.

Run it with:

    python3 agent_with_reschedule.py
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
    def __init__(self):
        self.facts = {}
        self.bookings = []   # every record keeps a status: active/cancelled
        self.trace = []

    # tools -------------------------------------------------------------
    def check_calendar(self, day):
        return CALENDAR.get(day, [])

    def book(self, service, day, time):
        ref = f"BK-{1001 + len(self.bookings)}"
        self.bookings.append(
            {"ref": ref, "service": service, "day": day,
             "time": time, "status": "active"}
        )
        return ref

    def cancel_booking(self, ref):
        for booking in self.bookings:
            if booking["ref"] == ref and booking["status"] == "active":
                booking["status"] = "cancelled"
                return True
        return False

    def active_booking(self):
        for booking in self.bookings:
            if booking["status"] == "active":
                return booking
        return None

    # the loop -----------------------------------------------------------
    def handle(self, message):
        self.trace = []
        text = message.lower()

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

        # NEW RULE: a reschedule request. Cancel first, then rebook.
        current = self.active_booking()
        if current and time and ("move" in text or "change" in text or "instead" in text):
            old_ref = current["ref"]
            self.cancel_booking(old_ref)
            self.trace.append(f"act: cancel_booking(ref='{old_ref}') -> cancelled")
            new_ref = self.book(current["service"], current["day"], time)
            self.trace.append(
                f"act: book(service='{current['service']}', day='{current['day']}', "
                f"time='{time}') -> {new_ref}"
            )
            self.trace.append("decide: goal reached, confirm the new booking")
            return (
                f"Moved: your {current['service']} is now on {current['day']} "
                f"at {time}. New reference is {new_ref}."
            )

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
    "Actually, could we move it to 12:30 instead?",
]


def main():
    agent = SalonAgent()
    print("Lesson 01 - Exercise solution: rescheduling")
    print("===========================================")
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
    active = [b for b in agent.bookings if b["status"] == "active"]
    cancelled = [b for b in agent.bookings if b["status"] == "cancelled"]
    print("Bookings the chatbot actually made: 0")
    print(f"Bookings the agent holds now:       {len(active)}")
    for booking in active:
        print(
            f"  {booking['ref']}: {booking['service']} on "
            f"{booking['day']} at {booking['time']} (active)"
        )
    for booking in cancelled:
        print(
            f"  {booking['ref']}: {booking['service']} on "
            f"{booking['day']} at {booking['time']} (cancelled)"
        )


if __name__ == "__main__":
    main()
