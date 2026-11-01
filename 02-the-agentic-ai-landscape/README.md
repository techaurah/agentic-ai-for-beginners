# Lesson 02: The Agentic AI landscape

**Time:** about 35 minutes · **Difficulty:** Beginner · **Prerequisites:** Lessons 00 and 01

Every week a new framework trends, and every week a team somewhere pauses a working project to ask whether they picked the wrong one. The expensive mistake is not choosing the second-best tool. It is choosing a shape of system that does not match the job: a multi-agent platform for a fixed daily workflow, or a drag-and-drop workflow for a problem whose steps change with every case. This lesson maps the landscape by shape first and names second, so your choices stay good even as the names churn.

## What are the four bases?

Almost everything in Agentic AI is one of four bases, or a blend. **Model API calls only**: ordinary code that calls a model where judgement is needed and does everything else itself. No agent loop at all, and for one-question-in, one-answer-out jobs, nothing more is honest engineering. **No-code automation**: a visual workflow tool, n8n being the one this course uses, where steps are drawn, data flows between them, and an AI step sits inside a deterministic process. **Agent frameworks in code**: libraries like LangGraph, CrewAI, AutoGen, the OpenAI Agents SDK, and Semantic Kernel, which give you the perceive, decide, act loop from Lesson 01 with state, tools, and control flow under version control. **Multi-agent systems**: several agents with distinct roles handing work to each other, powerful for genuine specialisation and genuinely hard to debug.

## Where do protocols fit?

Protocols are not a fifth base. They are the plumbing that lets any base use tools and other agents without custom wiring each time. The one that matters most right now is MCP, the Model Context Protocol: a standard way for tools to describe themselves so any compatible agent can discover and call them. Think of it as USB for agent tools. Instead of hand-writing a calendar integration for every agent you build, the calendar exposes an MCP server once and every agent uses it. Lesson 14 goes deep on MCP, and this course's companion tool, LeadPipe MCP, is a working example. The practical takeaway for landscape decisions: whatever base you choose, prefer tools exposed through the protocol, because they survive your next framework change.

## Who maintains it? The question that decides more than features do

Framework demos are all impressive. The differences that hurt arrive in month three: who on your team can read the system, change it safely, and explain it to a client? An operations team can own a drawn n8n workflow in a way they will never own a Python graph. An engineering team will eventually fight a no-code tool's limits and want code, tests, and deployment they control. Neither answer is smarter. They are answers about people, and the worked example scores exactly that.

## The worked example: a decision helper, not a horoscope

The file `landscape_quiz.py` turns the landscape into five questions: Are the steps the same on every run? Who maintains it? Does the right next step change case by case? Do several specialists hand work to each other? Is it basically one question in, one answer out? Each answer moves points between the four bases, with reasons attached, and the script scores three prepared scenarios: an invoice inbox, a research assistant, and a three-specialism support desk.

Run it:

```bash
cd 02-the-agentic-ai-landscape
python3 landscape_quiz.py
```

Expected output (trimmed here to the verdicts; the script prints its reasoning in full):

```text
SCENARIO: Invoice inbox for a small wholesaler
  Scores: Model API calls only 1 | No-code automation (n8n-style) 6 | Agent framework (code) 0 | Multi-agent system 0
  Recommendation: No-code automation (n8n-style)

SCENARIO: Research assistant for a consulting team
  Scores: Model API calls only 0 | No-code automation (n8n-style) 1 | Agent framework (code) 5 | Multi-agent system 3
  Recommendation: Agent framework (code)

SCENARIO: Support desk with three specialisms
  Scores: Model API calls only 0 | No-code automation (n8n-style) 1 | Agent framework (code) 6 | Multi-agent system 7
  Recommendation: Multi-agent system
```

Notice the support desk: framework scores 6 and multi-agent 7. Close scores are the helper telling the truth, that both are defensible and the deciding factor is appetite for complexity. Then run `python3 landscape_quiz.py --interactive` and score a project of your own. Argue with the result. The argument is the learning.

## Why this matters in production

Choosing the wrong base is a rewrite, and rewrites are where agent budgets go to die. The pattern we see in client work is consistent: a fixed, high-volume process gets an agent because agents are fashionable, and the team spends months adding guardrails to make it behave like the workflow it should have been. Or a genuinely open-ended research task gets a rigid workflow, and the team spends months adding branches for cases the workflow cannot foresee. The five questions in this lesson, asked before anything is built, prevent both. They return in Lesson 33 as the buying-versus-building framework companies use, because the same shape logic decides whether to buy a tool, hire a service, or build.

## Common failures

- **Choosing by demo.** Demos are staged on the happiest path. Score your ugliest real case instead.
- **Starting multi-agent.** It multiplies cost, latency, and failure modes. Earn it with a single agent that demonstrably cannot cope.
- **Ignoring the maintainer.** A system nobody on the team can change is a dependency, not an asset.
- **Hand-wiring every tool per agent.** Without a protocol layer, every framework change means rebuilding every integration.
- **Treating the map as permanent.** Frameworks converge and swap places yearly. Shapes and questions outlast rankings.

## Recap checklist

- [ ] I can describe the four bases and give an example job for each
- [ ] I can explain what MCP is and why it is plumbing, not a base
- [ ] I ran the helper and can defend or dispute each of its three verdicts
- [ ] I know the five questions to ask before choosing a base

## Resources

- [Model Context Protocol](https://modelcontextprotocol.io/introduction): the protocol's own introduction, the primary source
- [Building effective agents, Anthropic](https://www.anthropic.com/engineering/building-effective-agents): the workflows-versus-agents distinction this lesson's shapes rest on
- [n8n documentation](https://docs.n8n.io/): the no-code base used in this course, including its AI capabilities
- [LangGraph documentation](https://langchain-ai.github.io/langgraph/): the code framework we build with in Module 7
- [CrewAI documentation](https://docs.crewai.com/): a role-based framework, worth comparing against LangGraph's graph model

**Next:** Module 1 begins. Lesson 03, how LLMs work, enough to build on.
