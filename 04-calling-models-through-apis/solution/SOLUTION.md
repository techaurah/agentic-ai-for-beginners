# Lesson 04: Solution notes

Run it:

```bash
python3 extract_appointment.py
```

Expected output: the request, the raw JSON reply, the parsed appointment `{'service': 'cleaning', 'customer': 'Mr. Patel', 'day': 'Friday', 'time': '9:30', 'phone': '555-0142'}`, and "Validation: OK (keys present, day, time, and phone formats valid)".

**What changed and why.** The client and prompt follow Lesson 04 exactly; the new weight sits in `validate`, which returns a list of problems instead of failing on the first one, so a bad reply reports everything wrong with it in one pass. The three format checks use two small regular expressions and one membership test against the weekday list. Each guards a real downstream failure: a calendar write with day "Fri", a reminder job parsing "9.30" as a decimal, an SMS gateway rejecting a phone number with no separator.

**What to notice.** Validation is ordered cheapest first: presence, then shape, then (in later lessons) meaning. And if you ran the sabotage test from the exercise, you watched a reply with every key present still get refused. Presence is not validity. That sentence will save you money one day.
