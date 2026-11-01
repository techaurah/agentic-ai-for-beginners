# Lesson 18: RAG from scratch

**Time:** about 50 minutes | **Difficulty:** Intermediate | **Prerequisites:** Lesson 07 (working with data), Lesson 09 (the agent loop)

Your agent is only as good as what it can look up. Ask a language model about your company's warranty policy and it will answer confidently from general training, which is a polite way of saying it will guess. Retrieval-augmented generation, RAG, fixes this: before the model answers, the system searches your own documents, retrieves the relevant passages, and hands them to the model as evidence. In this lesson you build the whole pipeline yourself, with no framework and no vector database, so every moving part is visible.

## What is RAG, in plain language?

RAG has four steps, and this lesson implements each one:

1. **Chunk.** Split your documents into small pieces. A model cannot use a 40-page PDF as evidence; it can use three relevant paragraphs.
2. **Embed.** Turn each chunk into a list of numbers (a vector) that captures what the chunk is about, so similar texts get similar vectors.
3. **Retrieve.** Turn the user's question into a vector the same way, then find the chunks whose vectors are closest.
4. **Answer.** Give the question plus the retrieved chunks to the model, with instructions to answer from the evidence.

Production systems swap each step for something stronger: smarter chunkers, learned embedding models, vector databases. The shape never changes. If you understand this lesson's 200 lines, you understand the skeleton inside every RAG product you will ever evaluate or buy.

## How does the embedding work here?

Real embedding models are neural networks. Ours is TF-IDF, the classic hand-rolled alternative, and it is enough to learn the mechanics. Each word gets a weight based on two things: how often it appears in the chunk (term frequency) and how rare it is across the whole corpus (inverse document frequency). "Boiler" appears everywhere in a plumbing knowledge base, so it carries little signal. "Stopcock" appears once, so it carries a lot. The result is a sparse vector per chunk, stored as a plain Python dictionary.

Retrieval then uses cosine similarity: the angle between the question vector and each chunk vector. Small angle, high score, relevant chunk. The `TfidfIndex` class in `rag.py` is the entire search engine.

## Walking through the code

`rag.py` is organised in the same four steps:

- `DOCS` holds eight short documents for a fictional company, Northbeam Plumbing and Heating: services, hours, pricing, warranty, booking, area, emergencies, payment. This is the raw material a real business would export from its website and help centre.
- `chunk_document` splits each document into chunks of roughly 35 words, breaking on sentence boundaries so chunks stay readable.
- `TfidfIndex` builds the vectors once at startup, the same way a production system indexes documents once and answers many questions against the index.
- `compose_answer` stands in for the LLM call. It picks the retrieved sentences that share words with the question and assembles them into an answer with sources listed. Using a template composer here is deliberate: you can see exactly what evidence the model would receive, and the lesson runs fully offline.

## Run it

```bash
python3 rag.py
```

Expected output (trimmed):

```
Indexed 8 documents as 15 chunks.

Q: How much does a boiler repair callout cost?
   [0.494] pricing: A boiler repair callout costs 85 pounds, which is deducted from the fi...
   ...
A: A boiler repair callout costs 85 pounds, which is deducted from the final bill if you go ahead with the repair. ...

Q: Do you cover Manchester?
   [0.624] area: We do not currently cover Sheffield or Manchester....
A: We do not currently cover Sheffield or Manchester. We cover Leeds, Harrogate, and York, ...

Q: Do you sell garden furniture?
A: I could not find anything about that in the knowledge base.
```

Read the scores, not just the answers. The Manchester question scores 0.624 against the area chunk because "Manchester" is rare in the corpus, so it weighs heavily. The garden furniture question retrieves nothing above zero, and the system says so. That refusal is a feature: a RAG system that knows when the evidence is missing is worth ten that bluff.

## Why this matters in production

Almost every business agent you will build sits on a RAG core: the support agent answering from policies, the sales agent quoting real prices, the internal assistant searching procedures. The failures clients actually hit are rarely model failures. They are retrieval failures: the right document was never chunked well, never indexed, or ranked below a plausible-looking wrong one. When you have built the pipeline by hand once, you debug those failures in minutes instead of blaming the model.

It also sets your expectations correctly when buying tools. A vendor's "AI knowledge base" is this pipeline plus a real embedding model, a vector store, and a dashboard. Worth paying for, sometimes. Never magic.

## Common failures

- **Chunks too big.** A 2,000-word chunk that mentions the answer once will rank below a short chunk about something else, and even when retrieved, it buries the model in noise. Keep chunks focused on one idea.
- **Chunks too small.** Splitting mid-sentence or mid-table produces fragments that score well and read as nonsense. Break on structure: sentences, headings, paragraphs.
- **No refusal path.** If retrieval returns nothing useful and the system answers anyway, you have rebuilt the guessing problem you were trying to remove. Always check scores before answering.
- **Stale index.** The documents changed, the index did not. In production, re-indexing is part of the publishing workflow, not an afterthought.
- **Ignoring metadata.** Titles, headings, and product names are strong relevance signals. The exercise below shows how much they matter.

## Recap checklist

- [ ] I can name the four RAG steps and what each one is for
- [ ] I can explain TF-IDF weighting in one sentence
- [ ] I ran the pipeline and read retrieval scores, not just answers
- [ ] I know why a "no evidence" refusal is correct behaviour
- [ ] I can list two chunking mistakes and their symptoms

## Resources

- Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (the original RAG paper): https://arxiv.org/abs/2005.11401
- OpenAI documentation, retrieval and embeddings concepts: https://platform.openai.com/docs
- Anthropic documentation, context and retrieval guidance: https://docs.anthropic.com
- scikit-learn TF-IDF vectorizer docs (how the production version of this lesson's embedding works): https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
- Pinecone learning centre, chunking strategies: https://www.pinecone.io/learn/chunking-strategies/

Next: Lesson 19 puts this index behind a tool interface and lets an agent decide when and how to search.
