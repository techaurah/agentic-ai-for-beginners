# Lesson 19: RAG with a framework, and agentic RAG

**Time:** about 55 minutes | **Difficulty:** Intermediate | **Prerequisites:** Lesson 18 (RAG from scratch), Lesson 12 (function and tool calling)

Lesson 18's pipeline had a fixed shape: every question triggered exactly one search, using the question word for word. Real users do not cooperate with that shape. They ask two questions in one sentence, use words your documents never use, and ask about things your business does not do. Agentic RAG is the fix: retrieval stops being a fixed pipeline step and becomes a tool the agent can call, skip, repeat, and reformulate. This lesson rebuilds the Northbeam assistant that way, then shows how the same design looks in LangChain and LlamaIndex.

## What changes when retrieval becomes a tool?

Four decisions move from your code into the agent's loop:

1. **Whether to search at all.** "Hello, how are you?" needs no evidence. A fixed pipeline searches anyway and pays for it.
2. **How to split the question.** "What are your opening hours and do you offer a warranty?" is two lookups. One search with the whole sentence retrieves a muddle of both.
3. **What to search for.** Users say "cost"; documents say "price". If the first search scores badly, the agent reformulates and tries again.
4. **When to stop and refuse.** If two searches find nothing above a score threshold, the honest answer is "I could not find that", not a generated guess.

In the lesson code these decisions are made by a small rule-based planner, so everything runs offline and you can read the decision logic. In production an LLM makes the same decisions from a prompt. The tool contract, the trace, and the failure modes are identical either way.

## The tool contract

`agentic_rag.py` defines the search exactly the way an LLM would see it:

```python
SEARCH_TOOL = {
    "name": "search_knowledge_base",
    "description": "Search the Northbeam knowledge base for facts about services, prices, ...",
    "parameters": {"query": "string, a focused search phrase", "k": "integer, ..."},
}
```

The description matters more than the code behind it. It tells the agent what the tool knows and when to call it. A vague description ("search stuff") produces vague tool use in every framework. Write descriptions like documentation, because to the agent, they are.

## How would this look in LangChain or LlamaIndex?

The packaging changes; the design does not. In LangChain, you wrap the retriever as a tool and hand it to an agent:

```python
# Illustrative: requires langchain and a model API key. Not run in this lesson.
from langchain.tools.retriever import create_retriever_tool

search_tool = create_retriever_tool(
    retriever,  # any LangChain retriever over your index
    "search_knowledge_base",
    "Search the Northbeam knowledge base for facts about services, prices, hours, ...",
)
agent = create_agent(model, tools=[search_tool], prompt="Answer from retrieved evidence...")
```

In LlamaIndex, a query engine becomes a tool the same way:

```python
# Illustrative: requires llama-index and a model API key. Not run in this lesson.
from llama_index.core.tools import QueryEngineTool

search_tool = QueryEngineTool.from_defaults(
    query_engine=index.as_query_engine(),
    name="search_knowledge_base",
    description="Search the Northbeam knowledge base for facts about services, prices, ...",
)
```

Notice what survived the translation: the tool name, the description, and the idea that the agent chooses when to call it. Frameworks also give you retrievers with better embeddings, rerankers, and tracing. Reach for a framework when you need those, which is usually once the corpus outgrows a folder of text files. Build the first version the Lesson 18 way so you know what the framework is doing for you.

## Walking through the run

```bash
python3 agentic_rag.py
```

The trace is the lesson. Watch the compound question:

```
Q: What are your opening hours and do you offer a warranty on boiler repairs?
   PLAN split into 2 sub-questions
   TOOL search_knowledge_base("What are your opening hours") -> 3 passages, best score 0.468
   TOOL search_knowledge_base("do you offer a warranty on boiler repairs") -> 3 passages, best score 0.349
A: Our opening hours are Monday to Friday from 8:00 to 18:00 and Saturday from 9:00 to 13:00. All boiler repairs carry a 12-month warranty covering parts and labour. (Sources: hours, warranty)
```

Two searches, one sentence of evidence per sub-question, sources that match the claims. Then the question the business cannot answer:

```
Q: Do you rent out scaffolding towers?
   TOOL search_knowledge_base("Do you rent out scaffolding towers?") -> 0 passages, best score 0.0
   TOOL retry as "rent out scaffolding towers" -> best score 0.0
A: I checked the knowledge base and could not find that. It may not be something Northbeam offers.
```

The agent searched, reformulated once, found nothing above the threshold (`MIN_SCORE = 0.15`), and refused. The greeting at the top of the run skips retrieval entirely.

## Why this matters in production

Fixed pipelines break quietly: a compound question gets a half answer that sounds complete, and nobody notices until a customer acts on it. Agentic retrieval costs more (extra model calls, extra searches, more latency) and buys correctness on exactly the messy questions real users ask. The score threshold is your quality gate: tune it on real questions from your own logs, and log every refusal. A rising refusal rate usually means your documents have a gap, which is a content problem you can fix, not a model problem you cannot.

## Common failures

- **Searching for everything.** If the agent searches on greetings and chit chat, latency and cost grow and answers get stranger, not better. Gate retrieval behind a real decision.
- **No score threshold.** Without a minimum score, the top result is always used, even when it is irrelevant. There is always a top result. That is the trap.
- **Reformulating forever.** Retry once, maybe twice, with a genuinely different phrasing. Five searches for the same missing fact is a cost leak wearing a trench coat.
- **Splitting on every "and".** "Fish and chips" is one topic. Production splitters are models, not string splits; the lesson's simple splitter is a teaching stand-in, and its limits are the point.
- **Tool description drift.** The corpus grows to cover vans and hiring, but the tool description still says "prices and hours", so the agent never searches for the new topics. Descriptions are part of the index.

## Recap checklist

- [ ] I can name the four decisions agentic RAG moves into the agent loop
- [ ] I can explain why a tool description is a retrieval-quality feature
- [ ] I saw the split, retry, and refusal behaviours in the trace
- [ ] I know what a score threshold protects against
- [ ] I can sketch the same design in LangChain or LlamaIndex terms

## Resources

- LangChain documentation, retrieval and tools: https://docs.langchain.com
- LlamaIndex documentation, query engines as tools: https://developers.llamaindex.ai
- Anthropic, "Building effective agents" (tool use and agent loop design): https://www.anthropic.com/research/building-effective-agents
- OpenAI documentation, function calling: https://platform.openai.com/docs/guides/function-calling
- Model Context Protocol documentation (the standard tool contract from Lesson 14): https://modelcontextprotocol.io

Next: Lesson 20 tackles the trust problem: making every answer carry citations a checker can verify.
