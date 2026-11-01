# Lesson 28: Observability: Tracing Agent Runs and Tracking Cost

**Time:** 50-65 minutes · **Difficulty:** Intermediate · **Prerequisites:** Lessons 24 (testing agents), 27 (deployment)

## The hook

A user writes in: "Your agent told me the manager would call, and nobody called. Also it took forever." You open your logs and find one line: a request came in, a 200 went out. Somewhere between those two facts, the agent made two model calls, looked up the wrong customer record, failed, retried, and escalated, and you can see none of it. An agent you cannot reconstruct after the fact is an agent you are not operating. You are merely hosting it.

## What is a trace?

A **trace** is the structured record of one agent run: a run id, the job, and a sequence of timed events, each model call with its token counts, each tool call with its success or failure, from `run_started` to `run_finished`. Where a log line says "something happened", a trace says "this happened, then this, it took this long, it cost this much, and this step failed".

The format in this lesson is **JSON Lines**: one JSON object per line in a file, appended as events happen. It is the least glamorous format available and the right one to learn on. It survives crashes (the lines already written are intact), it streams, and every tool on earth can read it. Production systems graduate to tracing platforms built on standards like OpenTelemetry, where each event becomes a **span** inside a trace and a backend draws the timelines for you. The discipline transfers unchanged: decide what an event is, record it at the moment it happens, and never reconstruct from memory later.

Two fields do more work than the rest. The **run id** ties a user complaint to one exact run. The **token counts on every model call** turn cost from a monthly invoice surprise into a per-run number you can act on while it is still small.

## Worked example

Generate a day of traces, then read them back:

```bash
python3 traced_agent.py
python3 trace_reader.py
```

The writer simulates three runs on a logical clock, so every learner's trace file is identical: a lead qualification, a booking, and a complaint that goes wrong in an interesting way. `traced_agent.py` writes 16 events to `traces/day.jsonl`. The reader rebuilds each run as a timeline:

```text
RUN run-003 (handle_complaint) finished escalated in 2105ms
   t+    0ms  run_started
   t+    0ms  llm_call frontier-1 (1250 in / 380 out) [1310ms]
   t+ 1310ms  tool_call lookup_customer  <-- FAILED [30ms]
   t+ 1340ms  tool_call lookup_customer [45ms]
   t+ 1385ms  llm_call frontier-1 (640 in / 190 out) [720ms]
   t+ 2105ms  run_finished
```

Everything the support complaint described is visible in six lines: the big slow first model call, the customer lookup failing, the retry succeeding, and the run still ending escalated after 2.1 seconds. Then the reader prices the day, using a small table of fake prices (clearly labelled, because inventing plausible numbers and presenting them as real rates is how bad engineering decisions happen):

```text
Cost by model (fake prices, for teaching only):
  frontier-1  3 calls  in 2,780 tok  out 830 tok  $0.0208
  small-1     2 calls  in 530 tok  out 75 tok  $0.0001
Total estimated cost: $0.0209 across 3 runs (1 escalated, 2 ok)
Slowest single step: llm_call frontier-1 (1250 in / 380 out) in run-003 at 1310ms
```

Read the two outputs together and the operational story writes itself: run-003 was the slowest run, the most expensive run, and the only failure, and one flaky tool call sits in the middle of all three facts. That is the run that gets this week's engineering time. Without the trace, the same week would have been spent guessing.

Notice what the reader is: a separate program that only reads. Instrumentation (writing events) and analysis (reading them) are different jobs with different change rates. You will rewrite readers constantly, per question. You get exactly one chance to write the events, at the moment they happen.

## Why this matters in production

Three production questions are unanswerable without traces. "What did the agent actually do in this conversation?" is the support question, and it arrives with a screenshot attached. "Which runs are eating the budget?" is the finance question, and per-run cost answers it before the invoice does. "Did the new prompt make things slower, or is that the tool?" is the engineering question, and step timings settle it in minutes instead of arguments. Teams that skip tracing do not avoid these questions. They answer them by guessing, in public, during incidents.

## Common failures

- **Logging replies instead of events.** A transcript of final answers hides the tool failures and retries that explain them. Trace steps, not just outcomes.
- **No run id.** The moment a user says "your agent", you need one identifier that finds the whole run across every file and service.
- **Cost tracked monthly, in aggregate.** A single looping run can spend a week's budget in an afternoon. Per-run cost, checked daily, is the smallest unit that allows intervention.
- **Tracing everything except failures.** Failed tool calls and escalations are the highest-value events in the file. If your format makes them optional, they will be missing exactly when needed.

## Recap

- [ ] A trace is the timed, structured record of one run, keyed by a run id
- [ ] Record every model call (with tokens) and every tool call (with success or failure)
- [ ] JSON Lines is enough to learn on; platforms and OpenTelemetry come later
- [ ] Writing events and reading them are separate programs, changed at separate rates
- [ ] Per-run cost turns the monthly invoice into a daily, actionable number

## Resources

- [What are OpenTelemetry traces? (Checkly Learn)](https://www.checklyhq.com/docs/learn/opentelemetry/traces/): the key concepts behind the standard your traces will graduate to
- [OpenTelemetry distributed tracing (Uptrace)](https://uptrace.dev/opentelemetry/distributed-tracing): spans, context propagation, and sampling, explained with examples
- [OpenAI: Working with evals](https://developers.openai.com/api/docs/guides/evals): traces are the raw material evals from Lesson 25 are built from
