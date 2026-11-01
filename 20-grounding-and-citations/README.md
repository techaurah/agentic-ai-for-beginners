# Lesson 20: Grounding and citations

**Time:** about 50 minutes | **Difficulty:** Intermediate | **Prerequisites:** Lesson 19 (agentic RAG), Lesson 17 (context engineering)

A citation is not proof. Any model can sprinkle bracketed references over an answer it invented, and the brackets make the invention more dangerous, not less, because they ask the reader to stop checking. Grounding is the stronger discipline: every claim in an answer must be traceable to a specific source passage, and a piece of code, not a vibe, verifies the trace before the answer ships. This lesson builds the format and the verifier.

## What is a source span?

A span is the smallest citable unit of your knowledge base: one sentence or one short passage, with a stable ID. In `grounded_answers.py` the Northbeam documents are split into spans S1 to S11, each stored with its document name and text. Citations point at spans, not documents, because "see our pricing page" is not checkable and "[S1]" is: a human or a program can open S1 and compare.

Three design rules follow from this:

- **Spans must be small enough to verify at a glance.** One fact, maybe two.
- **Span IDs must be stable.** If re-indexing renumbers every span, every stored answer and audit log becomes meaningless.
- **The composer and the checker share the span store.** The model cites from the same list the checker verifies against, or the IDs are fiction.

## The answer format: claims, not prose

The lesson represents an answer as a list of claims, each with its own citations:

```python
{"text": "Repairs carry a 12-month warranty covering parts and labour.",
 "citations": ["S4"]}
```

This feels bureaucratic compared to flowing prose, and that is the point. Prose hides where one claim ends and the next begins; a claim list makes every assertion individually verifiable. In production you can render the claim list into natural prose with the markers inline, exactly as the lesson's `render` function does. The structure underneath is what gets checked.

## What does the checker actually check?

Three rules, in `check_answer`:

- **R1, presence.** Every claim carries at least one citation. An uncited claim fails, full stop. This rule alone catches the most common real-world failure: the model answered one part from evidence and quietly improvised the rest.
- **R2, existence.** Every cited span ID exists in the store. Models happily cite S99 in a store that ends at S11.
- **R3, support.** The cited text must actually back the claim. The lesson approximates this two ways: at least half of the claim's key words must appear in the cited spans, and every number in the claim must appear in the cited text. The number rule is deliberately strict, because numbers are where quiet fabrications live: prices, hours, warranty periods, deadlines.

None of this proves a claim true. It proves the claim is anchored to a span that plausibly says it, which is the difference between "trust me" and "check S9".

## Run it

```bash
python3 grounded_answers.py
```

Two answers get checked. Answer A passes: three claims, all cited, all supported. Answer B reads just as smoothly and fails:

```
CHECKER: FAIL (2 violations)
  x claim 2 ...: NO CITATION (rule R1)
  x claim 3 ...: number 24 does not appear in the cited span (rule R3)
```

Claim 3 is the instructive one. The real policy is free cancellation up to 4 hours before the visit; the answer says 24 hours and cites the correct span, S9. A human skimming the citation would likely nod it through. The number check does not skim.

## The blind spot, stated honestly

Answer B contains a third flaw the checker does not catch: "We cover Manchester for emergency callouts", citing S11, the span that says Northbeam does not cover Manchester. The words match, the number check finds nothing to bite on, and the meaning is inverted. Keyword support cannot see negation. Every automated grounding check has a version of this hole, including commercial ones; serious systems narrow it with entailment models and human review on high-stakes answers, and they say so. This lesson's exercise adds a negation heuristic that flags exactly this pattern for review. You will feel its limits, which is the correct lesson: verification is layered, and the last layer is a person who knows the business.

## Why this matters in production

Citations convert agent answers from content into evidence. Support teams can audit a complaint in seconds ("the bot cited S9, the policy changed last week, the span is stale"). Regulated and high-trust work, finance, health, legal, anything where a wrong number costs money, increasingly demands this trace as a condition of deploying an agent at all. And the checker pattern generalises: anything you can state as a rule about an answer (cited, in-policy, in-tone, in-language) you can verify in code before a customer ever sees the answer.

## Common failures

- **Citation theatre.** Markers everywhere, spans that do not support the claims. Worse than no citations, because it manufactures confidence.
- **Document-level citations.** Citing a 40-page policy PDF is citing nothing. Span-level or it did not happen.
- **Checking prose instead of claims.** If the checker cannot isolate claims, it cannot fail them precisely. Structure first, rendering second.
- **Treating a pass as truth.** A passed answer is an anchored answer. The span itself can be stale or wrong; grounding moves the trust question to your documents, where it belongs and where you can manage it.
- **One threshold for everything.** A wrong opening time and a wrong medical disclaimer are not the same risk. High-stakes claim types deserve stricter rules and human review.

## Recap checklist

- [ ] I can explain why a citation alone is not grounding
- [ ] I can state the three checker rules and what each catches
- [ ] I saw the number check catch a fabrication the citation hid
- [ ] I can name the checker's blind spot and why it exists
- [ ] I know why claims, not prose, are the unit of verification

## Resources

- Anthropic documentation, citations feature: https://docs.anthropic.com
- OpenAI documentation, structured outputs (for claim-shaped answers): https://platform.openai.com/docs
- Gao et al., "Enabling Large Language Models to Generate Text with Citations" (the ALCE benchmark for citation quality): https://arxiv.org/abs/2305.14627
- NLI and entailment background (the model-based next step after keyword checks): https://arxiv.org/abs/2212.08073

Module 6 closes here. Next, Module 7: what happens when one agent is not enough and several have to work together.
