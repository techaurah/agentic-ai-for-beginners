# Lesson 16: Long-term memory: stores, summaries, and what to never store

**Time:** 60-75 minutes · **Difficulty:** Intermediate · **Prerequisites:** Lesson 15 (short-term memory and state)

Short-term memory ends when the session ends. Long-term memory is what an agent is allowed to carry into next week: that a customer prefers morning appointments, that reminders should go by text, that the last cleaning ran long. Done well, it is the difference between an agent that feels like a stranger every visit and one that feels like a good receptionist. Done carelessly, it is a privacy incident stored in a JSON file.

This lesson builds a small long-term store and focuses on the three decisions that matter more than any database choice: store facts rather than transcripts, summarise sessions into those facts with inspectable rules, and refuse to store some categories of information at all.

## What should a stored fact look like?

A fact in this lesson's store is a record with four fields:

- **key**: what the fact is about (`preferred_time`, `preferred_channel`).
- **value**: the fact itself, small and specific (`morning`).
- **source**: where it came from (which session, which tool, which user statement).
- **day**: when it was learned, so it can age, expire, and be audited.

Source and date feel like bureaucracy until the first time a stored fact is wrong. Then they are the only way to answer "why does the agent believe this, and when did it learn it?" A transcript dump answers neither question, which is why transcripts are the wrong thing to store: they are bulky, unsearchable, full of things that were never facts, and impossible to correct one item at a time.

## How does a session become facts?

At the end of a session, something has to compress it. In `long_term_memory.py` that is `summarise_session()`: a short list of explicit rules that recognise a few patterns ("prefers morning", "text me", a service mentioned) and propose facts. Anything the rules do not recognise is left out on purpose. A long-term store should hold less than the session contained, not more.

In production, a model often writes the summary instead of rules. That is fine, and it scales to messier conversations, but the contract stays the same: the summary becomes discrete facts with sources, a human or a test can inspect them, and the raw transcript is not the memory.

## What must never be stored?

Some information does not become safe because an agent wrote it down politely. Payment card numbers, passwords, API keys, and government IDs have no business in an agent's memory store, where they would sit in plain text, inside backups, inside logs, one bug away from exposure. The store in this lesson enforces that with a refusal filter: `remember()` checks every value against patterns for those categories and returns a refusal with a reason instead of storing it.

Two honest caveats. First, a regex filter is a seatbelt, not a vault: it catches the obvious cases and teaches the principle, and a production system adds real secret scanning and encryption at rest. Second, the deeper rule is architectural: an agent that never needs a card number should never be in a position to receive one. Route payments to a payment provider and keep the data out of the conversation entirely.

The same lesson includes `forget()`: if a customer asks for a fact to be deleted, deletion must actually work, key by key. The exercise extends this to expiry and delete-everything, because both are requests real products receive.

### How to run it

```bash
cd 16-long-term-memory
python3 long_term_memory.py
```

The demo summarises a short session into facts, tries to store two forbidden values, recalls facts a week later, then forgets one. Expected output:

```text
Session summary -> facts proposed:
  preferred_time = 'morning' -> {'stored': True, 'key': 'preferred_time'}
  preferred_channel = 'text message' -> {'stored': True, 'key': 'preferred_channel'}
  last_service_discussed = 'cleaning' -> {'stored': True, 'key': 'last_service_discussed'}

Trying to store things that must never be stored:
  {'stored': False, 'reason': 'Refused: value looks like a payment card number.'}
  {'stored': False, 'reason': 'Refused: value looks like a password.'}

A week later (day 8), a new session recalls:
  preferred_time -> {'value': 'morning', 'source': 'session-2026-11-01', 'day': 1}
  preferred_channel -> {'value': 'text message', 'source': 'session-2026-11-01', 'day': 1}

The customer asks to be forgotten:
  forget preferred_time -> True
  recall after forget -> None
```

## Why this matters in production

Long-term memory is a trust feature wearing a technical costume. Customers experience it as being recognised; regulators experience it as stored personal data with obligations attached, including consent, correction, and deletion rights (the GDPR's right to erasure is the famous example, and it is not the only one). The habits in this lesson scale directly: facts with provenance, summarisation you can audit, a never-store list enforced in code, working deletion, and, from the exercise, expiry so stale facts die on their own. Teams that skip these end up with an unsearchable transcript swamp that is simultaneously less useful and more dangerous.

## Common failures

- **Storing raw transcripts as "memory".** Bulky, uncorrectable, and full of non-facts and other people's data.
- **Facts without source or date.** Un-auditable beliefs that cannot age out or be traced when wrong.
- **Summaries that keep everything.** A summary that loses nothing is not a summary; the discipline is choosing what earns storage.
- **Secrets in the store.** If it would hurt on the front page, it does not go in a JSON file. Filter in code, and design so the agent rarely sees secrets at all.
- **Deletion that does not delete.** A `forget` that hides a fact in the UI but keeps it in storage is a broken promise with legal exposure.

## Recap

- [ ] Store discrete facts with key, value, source, and date, not transcripts.
- [ ] Summarise sessions into facts with rules (or a model) whose output can be inspected.
- [ ] Enforce a never-store list in code: payment data, passwords, keys, government IDs.
- [ ] Deletion must work per fact, and stale facts should expire (the exercise).
- [ ] Long-term memory is personal data; treat its obligations as part of the design.

## Resources

- Anthropic, Effective context engineering for AI agents: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- OWASP, Top 10 for LLM Applications (sensitive information disclosure): https://owasp.org/www-project-top-10-for-large-language-model-applications/
- GDPR, Article 17, Right to erasure: https://gdpr-info.eu/art-17-gdpr/
- Mem0 documentation (a production memory layer, for comparison): https://docs.mem0.ai
