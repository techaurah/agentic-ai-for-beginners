# Decision worksheet: buy, build, or hybrid

Score each factor 1-5 for your company. Be honest; a flattering score produces an expensive answer. Then total the two columns (the script `score_decision.py` does the arithmetic and applies the thresholds).

## Factors that favour BUYING (an operated service, Lesson 32)

| # | Factor | Score 1-5 | How to judge it |
|---|---|---|---|
| B1 | Speed needed | | 5 = revenue is leaking now and every month of delay costs real money. 1 = no deadline pressure. |
| B2 | No internal builder | | 5 = nobody on the team can build and maintain this. 1 = a strong engineer is idle. |
| B3 | Process stability | | 5 = the process has run the same way for a year. 1 = it changes monthly. |
| B4 | Standard shape | | 5 = capture, qualify, book, follow up; the classic pattern of Lesson 31. 1 = deeply unusual workflow. |
| B5 | Cost of failure is operational | | 5 = a failed agent means missed leads, recoverable. 1 = a failed agent means regulatory or safety exposure. |

## Factors that favour BUILDING (in-house or your own contractor)

| # | Factor | Score 1-5 | How to judge it |
|---|---|---|---|
| D1 | Strategic capability | | 5 = agent skill is a core asset you intend to compound. 1 = a means to an end. |
| D2 | Internal expertise | | 5 = engineers on staff who have shipped LLM systems. 1 = none. |
| D3 | Data sensitivity | | 5 = data cannot leave your walls, by law or by policy. 1 = ordinary business data. |
| D4 | Unusual integration depth | | 5 = the agent must live inside proprietary internal systems. 1 = standard calendar, CRM, email. |
| D5 | Volume economics | | 5 = volume so high that operating it yourself is clearly cheaper at scale. 1 = modest volume. |

## Reading the result

- **Buy leads by 6 or more:** buy the operated service. Spend your energy on the ownership and exit terms (Lesson 32), not on a build.
- **Build leads by 6 or more:** build. Budget for the run, not just the build: monitoring, tuning, and improvement hours from Lesson 32's worksheet are yours now.
- **Within 5 either way: hybrid.** The common shape: an operator builds and runs the first version while your team shadows, learns, and takes over the pieces it wants, with handover defined in the contract from day one.

## The three questions that override the arithmetic

1. If this agent stopped working tonight, who notices first, and when? If the honest answer is "a customer, next week", whoever runs it needs monitoring you currently do not have.
2. Is the process written down anywhere? An agent encodes a process. An undocumented process gets encoded as someone's guess, bought or built.
3. In twelve months, do you want to own an agent, or own agent-building skill? They are different purchases. Price them differently.
