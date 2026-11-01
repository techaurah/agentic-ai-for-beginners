"""An agent runner that traces everything it does.

Run it:

    python3 traced_agent.py

It works three scripted jobs (qualify a lead, book an appointment, handle
a complaint) and writes a structured trace of every run to
traces/day.jsonl: one JSON object per event, in order.

Two teaching choices to notice:

- The clock is logical, not real. Durations are simulated numbers stored
  in the events themselves, so the trace file is identical on every run
  and the reader's output in the lesson is the output you will get. A
  production tracer uses real timestamps; the shape of the data, and
  everything trace_reader.py does with it, is unchanged.
- An event is a fact, not a paragraph. "llm_call, model small-1, 320
  tokens in, 45 out, 210ms" can be summed, filtered, and priced.
  "The agent thought for a bit" cannot. That difference is the whole
  discipline of observability.
"""

import json
import os

TRACE_DIR = "traces"
TRACE_FILE = os.path.join(TRACE_DIR, "day.jsonl")


class Tracer:
    def __init__(self):
        self.clock_ms = 0
        self.events = []

    def emit(self, run_id, event, **details):
        self.events.append(
            {"t_ms": self.clock_ms, "run_id": run_id, "event": event, **details}
        )

    def advance(self, ms):
        self.clock_ms += ms

    def llm_call(self, run_id, model, input_tokens, output_tokens, duration_ms):
        self.emit(
            run_id,
            "llm_call",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
        )
        self.advance(duration_ms)

    def tool_call(self, run_id, tool, duration_ms, ok=True):
        self.emit(
            run_id, "tool_call", tool=tool, duration_ms=duration_ms, ok=ok
        )
        self.advance(duration_ms)

    def run(self, run_id, job, script, status="ok"):
        start = self.clock_ms
        self.emit(run_id, "run_started", job=job)
        script(self, run_id)
        self.emit(
            run_id,
            "run_finished",
            job=job,
            status=status,
            total_ms=self.clock_ms - start,
        )


def job_qualify_lead(t, run_id):
    t.llm_call(run_id, "small-1", 320, 45, 210)        # extract the enquiry
    t.tool_call(run_id, "lookup_customer", 35)         # returning customer?
    t.llm_call(run_id, "frontier-1", 890, 260, 940)    # draft the follow-up


def job_book_appointment(t, run_id):
    t.llm_call(run_id, "small-1", 210, 30, 160)        # parse the request
    t.tool_call(run_id, "check_calendar", 25)
    t.tool_call(run_id, "book_appointment", 40)


def job_handle_complaint(t, run_id):
    t.llm_call(run_id, "frontier-1", 1250, 380, 1310)  # read the complaint
    t.tool_call(run_id, "lookup_customer", 30, ok=False)   # CRM timeout
    t.tool_call(run_id, "lookup_customer", 45)             # retry succeeds
    t.llm_call(run_id, "frontier-1", 640, 190, 720)    # draft the response


def main():
    tracer = Tracer()
    tracer.run("run-001", "qualify_lead", job_qualify_lead)
    tracer.run("run-002", "book_appointment", job_book_appointment)
    tracer.run("run-003", "handle_complaint", job_handle_complaint, status="escalated")

    os.makedirs(TRACE_DIR, exist_ok=True)
    with open(TRACE_FILE, "w", encoding="utf-8") as fh:
        for event in tracer.events:
            fh.write(json.dumps(event) + "\n")

    runs = sum(1 for e in tracer.events if e["event"] == "run_started")
    print(f"Wrote {len(tracer.events)} trace events for {runs} runs to {TRACE_FILE}")
    print("Now read them back with: python3 trace_reader.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
