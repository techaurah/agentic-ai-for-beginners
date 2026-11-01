# Exercise: give the agent a second tool, and make it choose

**Time:** about 30 minutes | **Difficulty:** Intermediate

The lesson agent has one tool: search. Search is a blunt instrument for questions that have an exact answer. "Are you open on Saturday?" should not be a similarity search across prose; it should be a lookup in a table.

## Your task

Add a second tool and teach the agent to route between tools:

1. Add a structured data source: a dictionary of opening hours by weekday (Monday 8:00 to 18:00, Saturday 9:00 to 13:00, Sunday closed, and so on).
2. Wrap it as a tool named `get_opening_hours` with the same contract shape as `SEARCH_TOOL`: name, description, parameters (a single `day`).
3. Extend the planner so a question that names a weekday and asks about opening goes to the lookup tool, while other factual questions still go to search.
4. Print the routing decision in the trace, like the lesson code does, so you can see which tool was chosen and why.

Test with at least: "Are you open on Saturday?", "What warranty do I get on a boiler repair?", "How much does a callout cost?"

## What "done" looks like

- The Saturday question is answered from the table, not from search, and the hours are exact.
- The warranty and price questions still route to search and answer correctly.
- You can state the rule you used for routing, and one question type where your rule would choose wrong.

The worked solution is in `solution/`. It uses a deliberately small knowledge base for the search side so the routing logic stays in focus.
