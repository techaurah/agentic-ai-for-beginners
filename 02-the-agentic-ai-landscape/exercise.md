# Lesson 02: Exercise

## Add a scenario, and a rule the helper is missing

The decision helper in `landscape_quiz.py` knows nothing about regulated or sensitive work. Fix that, in two parts:

1. **A fourth scenario:** "Appointment reminders for a dental clinic." Every morning the system finds tomorrow's appointments, drafts a reminder per patient, and sends them only after a staff member approves the batch. Same flow every day; nothing goes out unapproved. Set the scenario's five answers honestly from that description, and add a sixth field, `needs_human_approval`, set to true (false for the other three scenarios).
2. **A new rule:** when `needs_human_approval` is true, the no-code base gains 2 points, with a reason about approval steps being a built-in feature of workflow tools. Every category also gains a closing reason: whichever base wins, a human approval step goes in before anything is sent to a real person.

Before you run it, predict the clinic scenario's winner and the no-code score on paper. Then run it and check your prediction. (For calibration: the first three scenarios' scores must not change.)

## Solution

See `solution/landscape_quiz_extended.py`, with notes in `solution/SOLUTION.md`.
