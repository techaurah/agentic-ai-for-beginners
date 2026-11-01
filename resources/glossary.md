# Glossary

Every term this course uses, in plain language. If a lesson uses a word that is not defined here or in the lesson itself, that is a lesson problem: please open an issue.

**Agent**: A program that uses a language model to decide what to do next, can call tools to act on the world, and repeats that loop until a goal is met or it is stopped. The step up from a chatbot is the acting, not the talking.

**Agent loop**: The repeating cycle an agent runs: perceive the current state, decide on an action, act through a tool, observe the result, and repeat. Lesson 09 builds one by hand.

**Agentic RAG**: Retrieval used as a tool inside an agent loop, so the agent decides when to search, what to search for, and whether the results are good enough, instead of retrieving once before answering.

**API (Application Programming Interface)**: A defined way for one program to ask another program for something and get a structured answer back. Most agent tools are APIs underneath.

**Chunking**: Splitting documents into smaller pieces so a retrieval system can find and return the relevant piece instead of the whole document.

**Context engineering**: The craft of deciding what information goes into a model's context window, in what order and format. Lesson 17 argues this matters more than clever prompt wording.

**Context window**: The total amount of text a model can consider at once, measured in tokens. Everything the model knows in a given call must fit inside it.

**Embedding**: A list of numbers that represents the meaning of a piece of text, produced by an embedding model. Texts with similar meanings get similar numbers, which is what makes semantic search possible.

**Evaluation (eval)**: A repeatable test that checks whether an agent's behaviour meets a standard. In this course, evals assert outcomes (the right booking was made) rather than grading style.

**Function calling**: See tool calling. The two terms mean the same thing; providers name it differently.

**Grounding**: Tying an answer to retrieved source material so its claims can be checked, instead of letting the model answer from memory alone.

**Guardrails**: Checks placed around an agent that block or escalate actions outside agreed limits, such as spending caps, forbidden topics, or mandatory human approval for certain steps.

**Hallucination**: A fluent, confident output that is wrong. Models produce these because they predict plausible text, not verified facts. Grounding, citations, and evals are the countermeasures taught here.

**Handoff**: Passing a task, and the context needed to continue it, from one agent (or an agent) to another agent or a human, without losing the thread.

**Human-in-the-loop**: A design where a person approves, edits, or rejects an agent's proposed action at defined points, instead of the agent acting fully autonomously.

**Idempotency**: The property that running an operation twice has the same effect as running it once. Booking tools must be idempotent, or a retry creates two bookings.

**LLM (Large Language Model)**: A model trained on large amounts of text that predicts the next token. ChatGPT and Claude are products built around LLMs; the LLM is the engine inside.

**LLM-as-judge**: Using a model to grade another model's outputs against a rubric. Useful at scale, and unreliable in specific ways Lesson 25 covers.

**Long-term memory**: Information an agent stores outside a single conversation and retrieves in later ones, such as a returning customer's preferences.

**MCP (Model Context Protocol)**: An open standard that lets agents connect to tools and data through one protocol instead of a custom integration per tool. Lesson 14 builds on it.

**Multi-agent system**: A system where several agents with different roles cooperate on a task, coordinated by handoffs, a supervisor, or a shared plan.

**Observability**: The ability to see what a system did after the fact: logs, traces, and metrics that let you reconstruct a run and find where it went wrong.

**Orchestration**: The coordination layer that decides which agent or tool runs when, passes state between steps, and handles failures.

**Plan-and-execute**: A pattern where an agent first writes an explicit plan, then carries out the steps, replanning when reality disagrees with the plan.

**Prompt**: The text given to a model for one call, including instructions, context, examples, and the user's input.

**Prompt injection**: An attack where text the agent reads (a web page, an email, a document) contains instructions that try to override the agent's real instructions. Lesson 29 covers the threat model.

**RAG (Retrieval-Augmented Generation)**: A pattern where relevant material is retrieved from a knowledge store and placed in the context window before the model answers, so answers use your data instead of only the model's training.

**ReAct**: A pattern that interleaves reasoning steps with tool actions: think, act, observe, think again. One of the patterns in Lesson 11.

**Reflection**: A pattern where an agent reviews its own output against criteria and revises it before continuing.

**Retrieval**: Finding the chunks of stored information most relevant to a query, usually by embedding similarity, keyword search, or a mix of both (hybrid search).

**Schema**: A formal description of the shape of some data: field names, types, and which are required. Tool inputs and structured outputs are defined by schemas.

**Short-term memory**: The state an agent keeps within one conversation or task: the messages so far, tool results, and working notes.

**Structured output**: Model output constrained to a defined schema, usually JSON, so programs can consume it reliably instead of parsing free text.

**Supervisor pattern**: A multi-agent layout where one agent assigns work to specialist agents and reviews what comes back.

**Swarm**: A multi-agent layout where agents hand work to each other directly based on local rules, with no central coordinator. Flexible, and the hardest to debug.

**Temperature**: A setting that controls how random a model's choices are. Low values make output more predictable; high values make it more varied.

**Token**: The unit models read and write, roughly three quarters of a word in English. Context windows, pricing, and latency are all measured in tokens.

**Tool**: A function an agent can call to do something real: search, read a file, check a calendar, send a message. Tools are what turn a model into an agent.

**Tool calling**: The mechanism where a model outputs a structured request to run a tool with specific arguments, your code runs it, and the result goes back to the model.

**Trace**: A recorded timeline of one agent run: every model call, tool call, input, output, and timing, usually shown as nested spans. Lesson 28 teaches reading them.

**Vector store**: A database that stores embeddings and finds the nearest ones to a query embedding quickly. The storage layer under most RAG systems.

**Webhook**: A way for one service to notify another the moment something happens, by sending an HTTP request to a URL you registered. Lesson 06 builds on them.

**Workflow**: A fixed sequence of steps defined in advance, as in an n8n workflow. Workflows do not decide; agents do. Many production systems combine both.
