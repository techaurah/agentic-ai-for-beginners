# Lesson 03: How LLMs work, enough to build on

**Time:** about 40 minutes · **Difficulty:** Beginner · **Prerequisites:** Lesson 00 (Lessons 01 and 02 recommended)

Your agent "forgot" the customer's name halfway through a long conversation, and a stakeholder asks why the AI is being careless. It was not careless. The name fell out of a fixed-size window the model reads from, the way the end of a long queue falls out of a small waiting room. Almost every confusing behaviour you will meet in this course (sudden forgetfulness, rising bills, answers that drift off-topic) becomes obvious once you know three mechanical facts about how these models work. This lesson teaches those three, with code, and deliberately skips the rest.

## What is a token?

A model does not read letters or words. It reads tokens: chunks of text, each mapped to a number. Your text is sliced into tokens, converted to a list of IDs, and the model works on the numbers. Common words are usually one token. Rare words are split into subword pieces: a production tokenizer might cut "rebooked" into "re" + "book" + "ed". Punctuation counts. Spaces count. The practical consequence lands immediately: two prompts that ask for the same thing can cost very different amounts, because cost and capacity are counted in tokens, not in meaning.

## What is a context window?

The context window is the maximum number of tokens the model can consider in one call: your system instructions, the conversation so far, any documents or tool results you include, and the reply it is generating, all share one budget. Windows are large now, but they are never infinite, and the failure mode is silent. When the input outgrows the window, the oldest material is cut or the call fails, and the model does not announce what it can no longer see. Every technique later in this course for managing memory (Module 5) and context (Lesson 17) exists because this budget is real.

## What do models actually do with the tokens?

Strip away the mystique and a language model does one thing: given the tokens so far, it predicts a probability for each possible next token, picks one, appends it, and repeats. Two builder-level consequences follow. First, the model is always continuing text, not consulting a database of facts, which is why grounding (Module 6) and verification (Module 8) are your job. Second, you control how it picks. The **temperature** setting reshapes those probabilities: low temperature makes the model take the most likely token almost every time, which is what you want for extraction and classification; higher temperature flattens the odds and adds variety, which is what you want for drafting. There is no universally good value. There is a right value per step, a point Lesson 30 prices out properly.

## The worked example: count tokens yourself

The file `tokenizer_demo.py` builds the simplest honest tokenizer (words, numbers, and punctuation marks) and runs three experiments: the token cost of a direct instruction versus a padded one, an encode and decode round-trip through a tiny vocabulary, and a 34-token paragraph forced through a 20-token window.

Run it:

```bash
cd 03-how-llms-work
python3 tokenizer_demo.py
```

Expected output:

```text
1. Same job, different token cost
   Direct : 8 tokens - ['Book', 'a', 'meeting', 'with', 'Sara', 'on', 'Tuesday', '.']
   Padded : 17 tokens - ['Please', 'could', 'you', 'kindly', 'book', 'a', 'meeting', 'with', 'Sara', 'on', 'Tuesday', ',', 'if', 'that', 'is', 'possible', '.']

2. Text becomes numbers, and back
   Vocabulary size: 18 tokens
   Encoded: [0, 1, 2, 3, 4, 5, 6, 7]
   Decoded: Book a meeting with Sara on Tuesday.

3. A context window is a hard budget (window = 20 tokens)
   Paragraph length: 34 tokens
   What fits:        "Your agent reads the inbox every morning. It sorts each message by topic and urgency. Urgent messages go"
   What is cut:      14 tokens never reach the model
```

Read the third experiment until it stings a little. The sentence about humans getting the urgent messages is exactly the part that got cut. In a real agent, the cut material is your earliest instructions or the customer's first message, and nobody gets an error. They get a subtly wrong agent.

## Why this matters in production

Three production realities trace straight back to this lesson. Cost: you are billed per token in and out, so padded prompts, bloated histories, and verbose tool results are a recurring bill, not a rounding error. Reliability: long conversations degrade quietly as early context falls out, so serious systems summarise and select context deliberately instead of concatenating everything. Behaviour: when a model produces something odd, "what exactly was in its window, and at what temperature" diagnoses more incidents than any prompt tweak. Keep those questions; Lesson 28's tracing exists to answer them.

## Common failures

- **Pasting everything in, just in case.** Whole documents, full histories, every tool result. You pay for all of it, and the important parts compete with the filler.
- **Blaming the model for window cuts.** If the name is not in the window, the model cannot use it. That is arithmetic, not attitude.
- **One temperature for everything.** Extraction at creative settings invents variety you then have to validate away.
- **Assuming tokens equal words.** Code, URLs, other languages, and punctuation-heavy text all tokenise differently. Estimate with a real tokenizer before a big run, not after the invoice.

## Recap checklist

- [ ] I can define a token and explain subwords in one sentence each
- [ ] I can list what shares the context window budget in a single call
- [ ] I ran the demo and can explain why 14 tokens of the paragraph vanished
- [ ] I know which temperature direction suits extraction, and which suits drafting

## Resources

- [OpenAI Tokenizer](https://platform.openai.com/tokenizer): paste text and watch a production tokenizer count it
- [tiktoken, OpenAI on GitHub](https://github.com/openai/tiktoken): the open-source tokenizer library, for real counts in your own code
- [Context windows, Anthropic documentation](https://docs.anthropic.com/en/docs/build-with-claude/context-windows): how a major provider describes and handles the budget
- [Tokenizers, Hugging Face course](https://huggingface.co/learn/nlp-course/chapter6/1): the deeper, still friendly, treatment of how tokenizers are built

**Next:** Lesson 04, calling models through APIs: your first working call, and structured outputs.
