# AGENTS.md

Conventions for AI assistants working in this repository. Human contributors should read CONTRIBUTING.md; this file states the same rules in machine-checkable form.

## Repository shape

- Lessons live in root folders named `NN-kebab-lesson-name`, numbered 00 to 36, matching the lessons table in README.md exactly. Never rename a lesson folder without updating README.md, llms.txt, and PROGRESS.md in the same change.
- Each lesson folder contains: `README.md` (the lesson), runnable code files, `exercise.md`, and `solution/` with the worked solution.
- Root files: README.md (landing page), llms.txt (course index for AI assistants), PROGRESS.md (learner checklist), resources/, showcase/, translations/, assets/.

## Writing rules

- Plain language, short sentences. Define every technical term on first use or ensure it exists in resources/glossary.md.
- No em dashes anywhere, in prose or code comments. Use commas, colons, or full stops instead.
- Question-shaped headings are welcome in lessons where natural.
- No invented statistics, learner counts, or results. Claims need a linked source.
- Do not promise certificates. The course's completion artifact is the public capstone showcase.

## Code rules

- Python 3.11 or newer, standard library first. The course core runs on the stdlib; optional extras are comments in requirements.txt, not requirements.
- Every lesson must have a zero-credential demo path: fake keys, recorded data, or a free tier. Paid requirements are stated at the top of the lesson.
- Code must run top to bottom in the Lesson 00 setup. A lesson may ship a `smoke_test.py`; CI runs every file with that name, so keep smoke tests fast, offline, and credential-free.
- Deterministic where possible: seeded data and recorded fixtures, so learner output matches the lesson text.

## Change rules

- Small fixes may go straight to a pull request. New lessons, rewritten lessons, and new translation languages start with an issue (the two-tier rule in CONTRIBUTING.md).
- If lesson titles change, update README.md, llms.txt, and PROGRESS.md together; the three must never disagree.
- Showcase rows are added by learners via PR, one row per learner, format in showcase/README.md.
