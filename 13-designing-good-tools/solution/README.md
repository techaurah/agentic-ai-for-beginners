# Solution: idempotency the caller cannot get wrong

Run it:

```bash
cd 13-designing-good-tools/solution
python3 solution.py
```

Output:

```text
First send:       {"ok": true, "data": {"message_id": "MSG-B34C46", "channel": "sms", "to": "+1-555-0100", "appointment_id": "BK-7144CE"}}
Retry (timeout):  {"ok": true, "data": {"message_id": "MSG-B34C46", ..., "note": "Idempotent replay: reminder already sent."}}
Retry (loop):     {"ok": true, "data": {"message_id": "MSG-B34C46", ..., "note": "Idempotent replay: reminder already sent."}}
Messages actually sent: 1
Bad channel:      {"ok": false, "error": {"code": "invalid_value", "message": "'channel' must be one of ['sms', 'email'], got 'pigeon'.", "retryable": true}}
```

## The one design decision that matters

In the lesson, the caller supplied the idempotency key. Here the tool derives it: `"reminder:" + appointment_id`. The reasoning is the heart of the exercise. An idempotency key only works if every retry of the same operation carries the same key. A model caller might generate a fresh key per attempt, especially across separate conversations, silently defeating the mechanism. Deriving the key from the identity of the operation itself (one appointment gets one reminder) removes that failure mode entirely, at the cost of flexibility: if you ever legitimately need two reminders for one appointment, the key must grow a distinguishing part, such as the reminder stage (`reminder:BK-7144CE:24h`).

Rule of thumb: when the operation has a natural identity, derive the key from it. Accept a caller-supplied key when the operation is genuinely anonymous, and document that retries must reuse it.
