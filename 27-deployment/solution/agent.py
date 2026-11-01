"""The agent being deployed: a small clinic front-desk responder.

Deliberately simple and deterministic. Deployment is the lesson here,
not agent cleverness, so the "model" is a set of intent rules over the
same clinic facts used across this module (hours, services, prices).
In a real deployment this function is where the LLM call lives; the
service wrapper in server.py would not change at all.
"""

PRICES = {"check-up": 60, "cleaning": 90, "whitening": 120, "filling": 110}


def respond(message):
    """Return {"reply": str, "intent": str} for one user message."""
    text = message.lower()

    if "hour" in text or "open" in text or "when" in text:
        return {
            "intent": "hours",
            "reply": (
                "We are open Monday to Saturday, 9am to 5pm. "
                "The last appointment starts at 4pm."
            ),
        }

    price_words = ("cost", "price", "much", "$")
    for service, price in PRICES.items():
        if service in text and any(word in text for word in price_words):
            return {
                "intent": "price",
                "reply": (
                    f"A {service} costs ${price}. Prices can change, so "
                    "we confirm the exact fee when you book."
                ),
            }

    if "book" in text:
        return {
            "intent": "booking",
            "reply": (
                "I can help you book. Tell me the service, the day, and "
                "a time between 9am and 4pm, plus your name and phone "
                "number, and I will check the calendar."
            ),
        }

    if "hello" in text or "hi" in text:
        return {
            "intent": "greeting",
            "reply": (
                "Hello, this is the Brightpath Dental front desk. "
                "Ask me about hours, prices, or booking a visit."
            ),
        }

    return {
        "intent": "fallback",
        "reply": (
            "I look after appointments, hours, and prices for the clinic. "
            "Ask me about any of those, or say 'book' to start a booking."
        ),
    }
