# Lesson 01: Exercise

## Teach the agent to reschedule

Real customers change their minds. Extend `agent_vs_chatbot.py` with a third turn and the machinery to survive it:

1. Add a third conversation turn: "Actually, could we move it to 12:30 instead?"
2. Give the agent a new tool, `cancel_booking(ref)`, that marks an existing booking as cancelled. Bookings need a status now: a record that can be active or cancelled, not a list that only grows.
3. Add a rule that fires before the plain booking rule: if there is an active booking and the message asks to move or change it and names a new time, cancel the old booking first, then book the new time, and confirm with the new reference.
4. Keep the trace honest: the cancel and the rebook each get their own `act:` line.

Run all three turns through both systems. The chatbot's turn 3 reply is part of the exercise: write one sentence in your notes on what it just promised and what actually happened to the booking.

You are done when the final summary shows one active booking at 12:30 under a new reference, and the 10:00 booking listed as cancelled.

## Solution

See `solution/agent_with_reschedule.py`, with notes in `solution/SOLUTION.md`.
