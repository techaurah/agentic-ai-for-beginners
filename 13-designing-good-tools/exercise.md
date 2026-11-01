# Exercise: a reminder tool that cannot spam

The booking tool from the lesson is safe against double booking. Now build the tool that usually causes the real-world complaint: `send_reminder`. An agent sends an appointment reminder, the call times out, the agent retries, and the customer receives the same text three times.

Write `send_reminder` from scratch using the lesson's three rules:

1. **Schema:** it takes `channel` (only `sms` or `email`), `to`, `message`, and `appointment_id`, all required. Invalid input returns the lesson's structured error envelope.
2. **Errors as data:** an invalid channel returns an `invalid_value` error the model can fix, not an exception.
3. **Idempotency:** derive the idempotency key from the appointment (`"reminder:" + appointment_id`) instead of asking the caller to supply one. Ask yourself why: who is more reliable at keeping the key stable across retries, the model or your code?

Keep "sent" messages in a list that stands in for the real inbox, and print it at the end.

**Done when:** your demo sends one reminder, retries it twice (simulating a timeout and a retry loop), and the sent list still contains exactly one message, with each retry returning the original `message_id` and a note that it is an idempotent replay. A call with `channel: "pigeon"` should return a structured error.

The worked solution is in `solution/`.
