# Solution: a second tool, with routing

Run it:

```bash
python3 solution.py
```

Output:

```
Q: Are you open on Saturday?
   PLAN tool=get_opening_hours args={'day': 'saturday'}
   TOOL get_opening_hours -> 9:00 to 13:00
A: On Saturday we are open 9:00 to 13:00.

Q: What warranty do I get on a boiler repair?
   PLAN tool=search_knowledge_base args={'query': 'What warranty do I get on a boiler repair?'}
   ...
A: All boiler repairs carry a 12-month warranty covering parts and labour.
```

## What changed

Two tools now exist behind the same contract shape. The router checks one narrow pattern first: a weekday name plus an opening-hours intent routes to `get_opening_hours`. Everything else falls through to search. The lookup answer is exact because it comes from structured data, not from the closest-matching paragraph.

## Where this rule breaks

Ask "Are you open on the Saturday before Christmas?" and the router cheerfully answers with regular Saturday hours, ignoring the holiday exception buried in the prose. Narrow rules route the common case well and the edge case confidently wrong. That is the honest trade at the heart of agentic RAG: models route flexibly but unpredictably, rules route predictably but narrowly. Production systems layer them: rules for the exact lookups, a model for everything else, and retrieval as the fallback that can say "not found".

The broader pattern matters beyond this lesson: as your agents gain tools (Lesson 14), "which tool, with what arguments" becomes the main quality problem, ahead of the tools themselves.
