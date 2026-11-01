# Lesson 03: Solution notes

Run it:

```bash
python3 conversation_cost.py
```

Expected output: per-message counts of 23 (system), 11, 25, 13, 19 (tool), and 11, for a total of **102 tokens**. Against a 120-token window it fits with 18 tokens of headroom. Against a 90-token window it is over budget by 12, and the script prints the warning: the oldest messages will be dropped or must be summarised.

**What changed and why.** This is the lesson's tokenizer pointed at a conversation instead of single sentences, plus the budget comparison the demo did with one paragraph. Two numbers deserve a stare. The system message (23) and the tool result (19) together cost more than both user messages combined: in real systems the "overhead" text you write once and the data your tools return routinely outweigh what the customer actually typed. And the whole six-message exchange, which feels tiny, eats most of a small window. Scale that to a 40-turn support chat with file attachments and you have the reason Module 5 (memory) and Lesson 17 (context engineering) exist.
