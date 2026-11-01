# Resources

Curated resources for Agentic AI for Beginners, grouped by theme. Lessons link to the items they use; this page is the full shelf. Official documentation first, because it ages best. If a link here breaks, that is a lesson problem: please open an issue so it gets fixed for everyone.

New to a word? The [glossary](glossary.md) defines every term this course uses, in plain language.

## Official documentation

- [OpenAI API documentation](https://platform.openai.com/docs): model APIs, tool calling, and structured outputs, used from Lesson 04 on.
- [Anthropic documentation](https://docs.anthropic.com): Claude API, tool use, and Anthropic's published guidance on building effective agents and context engineering.
- [Model Context Protocol documentation](https://modelcontextprotocol.io): the MCP specification, concepts, and SDK references behind Lesson 14.
- [LangChain documentation](https://python.langchain.com/docs): the framework pieces used for comparison in Modules 6 and 7.
- [LangGraph documentation](https://langchain-ai.github.io/langgraph/): stateful agent graphs, persistence, and human-in-the-loop, used in Lesson 22.
- [n8n documentation](https://docs.n8n.io): the workflow platform behind Lesson 08 and the no-code track.
- [Hugging Face documentation](https://huggingface.co/docs): models, datasets, and embeddings references used in Module 6.
- [Python documentation](https://docs.python.org/3/): the standard library the whole course is built on.

## Papers worth reading

Short list, high signal. Each one is named in the lesson that uses it.

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) (Vaswani et al., 2017): the transformer paper, background for Lesson 03.
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) (Lewis et al., 2020): the RAG paper, background for Lesson 18.
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) (Yao et al., 2022): the reasoning-and-acting pattern from Lesson 11.
- [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761) (Schick et al., 2023): early tool-use research, background for Module 4.
- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) (Shinn et al., 2023): the reflection pattern from Lesson 11.
- [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442) (Park et al., 2023): memory and reflection in agents, background for Module 5.

## Communities

- [This course's Discussions](https://github.com/techaurah/agentic-ai-for-beginners/discussions): questions, capstone help, and showcase announcements. Ask here first.
- [Hugging Face forums](https://discuss.huggingface.co): model and dataset questions from the open-source community.
- [n8n community forum](https://community.n8n.io): workflow help, templates, and node questions for the no-code track.
- [Model Context Protocol on GitHub](https://github.com/modelcontextprotocol): the specification, SDKs, and the reference servers repository, useful once you reach Lesson 14.

## Tools

- [Python](https://www.python.org): the language of the course. Version 3.11 or newer.
- [uv](https://docs.astral.sh/uv/) or plain `pip`: environment and package management, set up in Lesson 00.
- [Ollama](https://ollama.com): run open models locally for the zero-cost paths in early lessons.
- [Docker](https://www.docker.com): used by the deployment lessons in Module 9 and by n8n self-hosting.
- [LeadPipe MCP](https://github.com/techaurah/leadpipe-mcp): the MCP server studied as a case study in Lesson 14.
- [QualBench](https://github.com/techaurah/qualbench): the agent testing tool taught in Lesson 24.
- [n8n-audit](https://github.com/techaurah/n8n-audit): the workflow linter referenced by the automation lessons.

## Going further

- [resources/glossary.md](glossary.md) in this folder: every course term, defined plainly.
- The other TechAurah Academy courses, linked from the main [README](../README.md): MCP servers, testing AI agents, context engineering, and multi-agent systems go deeper on their slice of this course.
