# Lesson 07: Working with data, JSON, files, and spreadsheets as agent state

**Time:** about 40 minutes · **Difficulty:** Beginner · **Prerequisites:** Lesson 06 (APIs and webhooks) · **You need:** Python 3.11 or newer. No API keys, no accounts, no internet.

Ask a room of builders where their agent keeps its memory and you will hear about vector databases and memory frameworks. Ask again six months later, after the system has real users, and the honest answer is usually: a database table, a JSON file, and a spreadsheet somebody in operations refuses to give up. State, meaning the information an agent reads before it acts and writes after it acts, is the least glamorous part of agentic AI and the part that decides whether the system is trustworthy. This lesson teaches state handling with the two formats you will meet everywhere: JSON for structured state, CSV for the spreadsheet world.

## Why does state matter more than the model?

A model call is stateless. The model remembers nothing between calls unless your code hands it the relevant history. Everything the agent "knows" about a lead, a customer, or a half-finished job lives in state that your code loads, updates, and saves. That has a sharp consequence: when an agent does something wrong in production, the bug is in the state handling far more often than in the prompt. A lead scored twice, a stage overwritten by a stale copy, a booking written to the wrong record. The model gets the blame; the file handling did it.

So this lesson treats a small JSON file with the seriousness of a production database: load it, validate moves against it, change exactly what you meant to change, and write the whole thing back in one deliberate save.

## What does the data look like?

Inside `data/` you will find two seeded files. `pipeline_seed.json` is the pipeline for a fictional dental clinic, BrightSmile Dental: three leads, each with an id, name, channel, service, score, and stage, plus the list of valid stages (`new`, `contacted`, `qualified`, `booked`, `lost`). `services.csv` is the price list as a spreadsheet: service, price, duration. Open both before you run anything. Reading your seed data first is a habit worth forming, because every surprise in the output will trace back to something in these two files.

Notice what the JSON gives you that the CSV does not: nesting and types. A lead is one object with named fields, the score is a number you can compare, and the pipeline is one document you can load in a single call. CSV gives you rows of text: simple, universal, openable in any spreadsheet tool your operations team already uses, and with no types at all until your code imposes them. Agents live in both worlds at once, which is why the demo writes both.

## The worked example: read, update, write back

`state_demo.py` performs the three operations every agent eventually needs. First it loads the pipeline JSON and the CSV price list. Then it adds a new lead: the lead's id is computed from the highest existing id (so ids never collide), and its score comes from a small deterministic scoring function that stands in for an LLM scorer. The stand-in is labelled in the code; Lesson 04 showed the real model call, and the state handling around it is identical either way. The new lead's service is priced by looking it up in the CSV, which is the moment the two formats meet. Finally the demo moves the lead from `new` to `qualified`, saves the updated pipeline to `output/pipeline.json`, and exports `output/summary.csv`, a count of leads per stage in a format a human can open in Excel or Google Sheets.

Two design choices are worth copying. The seeds in `data/` are never mutated; all writes go to `output/`, so you can re-run the demo forever and always start from the same state. And stage moves go through a function that checks the target stage is valid, so a typo becomes an error message instead of a lead silently filed under a stage that does not exist.

## Run it

```bash
cd 07-working-with-data
python3 state_demo.py
```

Expected output:

```text
loaded pipeline 'BrightSmile Dental - new patient enquiries' with 3 leads
loaded 4 services from the CSV price list
added LP-2026-00039 (Ayesha Khan): score 90, service 'emergency repair' at GBP 150
moved LP-2026-00039 from 'new' to 'qualified'
saved updated state to output/pipeline.json (4 leads)
summary by stage:
  new        0
  contacted  1
  qualified  2
  booked     1
  lost       0
wrote output/summary.csv
```

Check the score yourself: the message mentions pain, an emergency, and booking an appointment, and the scorer adds points for each. Then open `output/pipeline.json` and find the new lead, and open `output/summary.csv` to see the spreadsheet view of the same state.

## Why this matters in production

Files are where prototypes live, and there is no shame in that: a JSON file is a perfectly good state store for a single-process agent handling modest volume. What matters is knowing the exact moment it stops being good enough. Two agents writing the same file at once will overwrite each other. A crash mid-save can leave a half-written file. Neither problem cares how good your prompts are. The grown-up path is not a different mindset, it is the same three operations (read, update, write) moved onto a store that makes them atomic: a SQLite database, which ships with Python, is the usual next step, and a shared database after that. The interface you practiced here survives every one of those moves.

The second production lesson is the audit trail. This demo overwrites state in place, which is fine for learning. Real lead pipelines also append a record of what changed, when, and why, because "the agent moved my hottest lead to lost" is a question you will eventually have to answer with evidence, not vibes.

## Common failures

- **Mutating your seed or source data.** If the input and the output are the same file, you can never re-run, never diff, and never recover. Read from one place, write to another.
- **Inventing ids instead of deriving them.** Random or timestamp ids collide and duplicate in ways that only appear under load. Derive the next id from the existing state, or use a store that assigns ids for you.
- **Trusting CSV types.** Every value out of a CSV is a string. Compare `"90" > "100"` as text and your hot-lead filter quietly inverts. Convert on load.
- **Saving state in several small writes.** If the process dies between them, the file describes a world that never existed. Build the new state in memory, then write it once.
- **Letting the model write state directly.** The model proposes; your code disposes. Validation, like the stage check in this lesson, belongs in code the model cannot talk its way around.

## Recap checklist

- [ ] I can explain why state bugs, not prompts, cause most production agent failures.
- [ ] I opened both seed files and can describe what each format is good at.
- [ ] I ran the demo and verified the new lead's score by hand.
- [ ] I found the new lead in `output/pipeline.json` and the counts in `output/summary.csv`.
- [ ] I know the signal for when a JSON file stops being enough (concurrent writers, crash safety).

## Resources

- [Python docs: json](https://docs.python.org/3/library/json.html), loading, dumping, and the type mapping between JSON and Python.
- [Python docs: csv](https://docs.python.org/3/library/csv.html), reading and writing spreadsheet-format files, including DictReader.
- [Python docs: sqlite3](https://docs.python.org/3/library/sqlite3.html), the built-in next step when a file stops being enough.
- [JSON.org](https://www.json.org/), the format itself, specified on one page.
