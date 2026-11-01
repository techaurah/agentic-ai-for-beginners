# Solution 26: Classify the action nobody planned for

**The new tier (`guardrails.py`).** `export_customer_data` sits in a tier of its own, `data_export`, added to `HUMAN_TIERS`. It could have shared the `external` tier; a separate tier earns its place the first time the clinic wants different rules for exports (say, manager-only approval, or business hours only) without touching message sending. Tiers are policy, and policy gets more specific over time, never less.

**The ID pattern.** One regex, `\b\d{3}-\d{2}-\d{4}\b`, added to both directions, with different behaviour per direction: blocked at input with instructions for the caller, redacted at output because a draft that quotes an intake form should be cleaned, not killed. Same secret, different layer, different response. That asymmetry is normal in production guardrails.

**The pause count (`demo.py`).** The summary now counts every action whose outcome was not a free run: 5 of 10 in the extended shift (send, refund, delete, export, and the still-unknown mailing list). Expect this number to start arguments, which is its job. If 5 pauses per 10 actions makes the shift unusable, the answer is not to remove the gate; it is to look at which paused actions have a clean approval history and graduate those, one tier decision at a time, with the audit log as the evidence.

Note the unknown action still pauses and still gets denied by the scripted human. Adding a new named action changed nothing about the default. Defaults are the whole design: new capabilities arrive guilty until classified innocent.
