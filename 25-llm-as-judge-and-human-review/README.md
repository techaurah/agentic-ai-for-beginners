# Lesson 25: LLM-as-Judge and Human Review

**Time:** 45-60 minutes · **Difficulty:** Intermediate · **Prerequisites:** Lesson 24 (testing agents)

## The hook

Lesson 24's assertions are exact: a booking exists or it does not. But most agent quality is not exact. Was that reply rude? Did it actually answer the question? Did it promise something the business cannot keep? You cannot write a regex for "rude", and you cannot hire a human to read ten thousand replies a day. So teams reach for a second model to grade the first one. That works, until it quietly doesn't, and this lesson is about building the version that fails loudly instead.

## What is an eval set, really?

An **eval set** is a fixed collection of cases, each with an input, the agent's reply, and a **gold label**: the verdict a knowledgeable human gives, with the reason written down. The word "fixed" does the heavy lifting. Because the cases never change, scores from different weeks are comparable, and a change that helps one case while hurting another shows up immediately.

Where do cases come from? Not from imagination. From your production failure log: the replies that got complaints, the near misses a supervisor caught, the refunds. Real failures have a texture that invented examples lack, and they are, by definition, the failures your system is actually prone to. This lesson's set has ten cases from Brightpath Dental's log, including a correct price quoted for the wrong service, a sarcastic reply to a patient in pain, and a refusal done exactly right.

## What does the judge do with them?

A **judge** grades each reply against the gold labels. In production the judge is usually an LLM given a rubric (a written scoring guide: what counts as a pass, what is an automatic fail, what facts to check). In this lesson the judge is a small rule-based stand-in, deliberately transparent, so you can watch the grading logic instead of trusting a black box. It checks quoted prices against the price list, looks for diagnoses, credentials, other patients' details, and unkeepable promises, and it reports a verdict, a confidence, and its reasons.

The swap is mechanical: replace the rule checks in `judge.py` with a call to a strong model, a rubric prompt, and the same return shape (verdict, confidence, reasons). Everything else in this lesson, the set, the agreement score, the review queue, stays identical. That is the point of building the scaffolding first.

## Worked example

Run the evaluation:

```bash
python3 run_eval.py
```

```text
Eval set: 10 cases built from the production failure log

case   category                      gold  judge outcome
--------------------------------------------------------
F-001  invented price                fail  fail  agree
F-003  medical diagnosis             fail  fail  agree
F-007  missing disclaimer            fail  fail  agree -> review queue
F-008  sarcasm                       fail  pass  DISAGREE -> review queue
F-009  right price, wrong service    fail  fail  agree -> review queue
F-010  short and correct             pass  pass  agree -> review queue

Judge agreement with human labels: 9/10
Sent to human review: 4 of 10 cases
```

Three readings matter here. First, **agreement is 9 of 10**, and the miss is instructive: the judge passed the sarcastic reply (F-008) because sarcasm is a tone judgement and no rule fires on tone. An LLM judge would likely catch it, which is an argument for the swap, not for more rules.

Second, look at F-009. The judge agreed with the human's fail verdict but for the wrong reason: it flagged a missing disclaimer, when the real defect is that $90 is the cleaning price quoted for a check-up. Agreement on the verdict, disagreement on the diagnosis. If you only track the headline score, this case looks solved. It is not, and the exercise makes you fix it properly.

Third, **the review queue is the product**. Four of ten cases route to a human: every disagreement, and every verdict the judge holds with low confidence. The queue file (`review_queue.json`) carries both verdicts and both reasons, so the human decides in seconds with full context. The judge does not replace the human. It reads everything so the human only reads what matters.

## How do you keep the judge honest?

Measure it, the same way you measure the agent. The agreement rate against gold labels is the judge's own score, and it belongs on the same dashboard as the agent's pass rate. When you swap the rule-based judge for an LLM judge, run both against the set and compare before trusting the new one. Judges also drift: a model update can change grading behaviour overnight, which is why the gold set is fixed and versioned alongside the code. And keep adding cases. Every human review decision that overturns a judge verdict is a new case waiting to be labelled, which is how the set, and the judge, improve together.

## Why this matters in production

Sampling is how quality problems hide. A supervisor reading twenty random replies a week will miss the one-in-five-hundred failure that generates the screenshot on social media. A judge reads all of them, imperfectly, and a review queue concentrates human attention where the judge is weak or unsure. That combination, full coverage plus focused humans, is the only quality system that scales with traffic.

## Common failures

- **Building the eval set from imagination.** Polished invented cases miss the failures your system actually produces. Mine the logs.
- **Tracking the score, not the reasons.** A judge can agree for the wrong reason (F-009). Read the disagreements and a sample of the agreements.
- **No review queue.** A judge with no escalation path turns its blind spots into your production incidents.
- **Letting the set rot.** A set that never gains new cases measures last year's failure modes with great precision.

## Recap

- [ ] An eval set is fixed cases with human gold labels and written reasons
- [ ] Cases come from real production failures, not imagination
- [ ] A judge returns a verdict, a confidence, and reasons, whatever powers it
- [ ] Disagreements and low-confidence verdicts go to a human review queue
- [ ] The judge itself is measured against the gold labels, continuously

## Resources

- [OpenAI: Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices): how to design evals and graders that hold up
- [OpenAI: Working with evals](https://developers.openai.com/api/docs/guides/evals): running evals programmatically against your own criteria
- [QualBench](https://github.com/techaurah/qualbench): the outcome-assertion side of the same discipline, from Lesson 24
