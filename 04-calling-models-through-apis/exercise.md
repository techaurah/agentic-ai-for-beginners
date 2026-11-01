# Lesson 04: Exercise

## A new extraction job, with sharper teeth

Lesson 04 extracted a lead and checked that keys exist. Appointments are less forgiving: a booking with a malformed time or phone number is worse than no booking. Build `extract_appointment.py`:

1. The request to handle: "Please book a cleaning for Mr. Patel on Friday at 9:30. His number is 555-0142."
2. Reuse the lesson's pattern: a fake client (labelled simulation) that answers the extraction prompt with JSON, keys `service`, `customer`, `day`, `time`, `phone`.
3. Validate harder than the lesson did. Beyond key presence, check formats: `day` must be a real weekday name, `time` must match the pattern `H:MM` (one or two digits, a colon, two digits), and `phone` must match `NNN-NNNN` (three digits, a hyphen, four digits). Regular expressions from the standard library are the right tool.
4. Print the raw reply, the parsed appointment, and the validation verdict. Any problem should stop the script with a message naming the problem.

To prove the format checks earn their place, temporarily edit the fake reply so the phone reads "5550142" and run it again: the script must refuse the appointment even though every key is present.

## Solution

See `solution/extract_appointment.py`, with notes in `solution/SOLUTION.md`.
