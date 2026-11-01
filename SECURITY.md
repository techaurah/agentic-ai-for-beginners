# Security policy

## Reporting a vulnerability

If you find a security problem in this repository, for example a lesson that teaches an unsafe pattern, example code that leaks credentials, or a dependency issue, please do not open a public issue with the details.

Report it privately through the contact form at [techaurah.com](https://techaurah.com), with "Agentic AI course security" in the message. We aim to acknowledge reports within three working days and to fix or annotate confirmed problems in the affected lesson.

## Scope notes

- This is a teaching repository. Example code favours clarity, and lessons say explicitly where production hardening differs from the teaching version (Lesson 29 covers the agent threat model in depth).
- Never commit real API keys to your fork. Lesson 00 shows the environment variable pattern the whole course uses. If you accidentally commit a key, rotate it immediately; deleting the commit is not enough.
