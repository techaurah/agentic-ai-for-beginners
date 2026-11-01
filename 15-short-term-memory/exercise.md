# Exercise: pinned facts that trimming cannot kill

The lesson's window protects the budget, but it has a blind spot. Run the lesson demo and look at the first user turn: if Amara had said "I am allergic to fluoride" in that first message, the fact would be trimmed away by turn nine, while later small talk survives. For a booking agent, that is the worst possible trade.

Add a third memory tier to `conversation_state.py`: **pinned facts**.

1. Add a `pins` list to `ConversationState`. When a user message contains a standing fact about the user (your triggers can be simple phrases such as `allergic to`, `i use a wheelchair`, `do not call`, `no fluoride`), store the message in `pins`. A fact is pinned once, not once per mention.
2. Pins are never trimmed, and they are counted in the token budget (they are not free; they are protected).
3. `build_context()` injects each pin near the end of the context as its own system message, prefixed `PINNED FACT:`, after the slots line.
4. Change the demo: make the first user message "Hi, my name is Amara. One important thing: I am allergic to fluoride." Keep the rest of the conversation the same length, and run it.

**Done when:** the printed context shows the early turns trimmed as before, and the allergy fact still present as a pinned fact at the end. Print a line proving it, for example a check that "fluoride" appears in the final context.

Think about the boundary as you work: what belongs in slots, what belongs in pins, and what belongs in neither? The solution in `solution/` states one defensible answer.
