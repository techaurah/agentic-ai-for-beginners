# Lesson 03: Exercise

## Price a whole conversation

Single prompts are not what agents send. They send conversations that grow every turn. Write a script, `conversation_cost.py`, that:

1. Holds this six-message conversation (system instructions, two user messages, one agent reply, one tool result, one follow-up) from the Bright Smiles Dental booking story. Reconstruct it from Lesson 01's demo and Lesson 03's paragraph if you want the exact wording, or write an equivalent six messages of similar length.
2. Counts the tokens in each message with the lesson's tokenizer, prints one line per message (role, count, and the first characters of the text), then prints the total.
3. Reports the total against a context window budget twice: once at 120 tokens and once at 90. When it fits, print the headroom left. When it does not, print a warning naming how many tokens are over, and what a real system would have to do about it.

Predict the total before you run it: most people underestimate by a third, because system prompts and tool results are longer than they feel.

## Solution

See `solution/conversation_cost.py`, with notes in `solution/SOLUTION.md`.
