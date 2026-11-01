# Exercise: a supervisor that adapts to the work

The lesson's supervisor runs the full path for every enquiry: classify, check the calendar, draft with the model. But Lesson 08 already taught us that categories deserve different handling. A `research` enquiry does not need a calendar check, and its reply does not need a model: a good human-written template is faster, cheaper, and more consistent.

Build a supervisor, in a new file, that adapts:

1. Handle **two** enquiries: Ayesha Khan's emergency booking request and Maria Gomez's "just researching, no rush" message (both appear in earlier lessons).
2. The supervisor plans, then classifies each enquiry.
3. For `booking`: check the calendar, then draft with the model, quoting a real free slot.
4. For `research`: **skip the calendar entirely** and reply from a fixed template function that makes **no** model call.
5. Count model calls per enquiry and print the count at the end of each run.

Expected shape:

```text
enquiry from Ayesha Khan: ...
  supervisor reads classification: booking
  booking path: calendar checked, 3 free slots
  model calls used: 3

enquiry from Maria Gomez: ...
  supervisor reads classification: research
  research path: calendar SKIPPED, template reply, no draft call
  model calls used: 2
```

When it runs, read `solution/` on why "spend calls only where they change the outcome" is the supervisor pattern's entire economic argument.
