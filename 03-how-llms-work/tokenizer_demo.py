"""
Lesson 03 - A tiny tokenizer, and why tokens run your budget.

Run it with:

    python3 tokenizer_demo.py

Models do not read words or letters. They read tokens: chunks of text
turned into numbers. This demo builds a deliberately simple word-level
tokenizer so you can watch the mechanics. Real tokenizers split text
into subwords, which the lesson explains, but the counting lesson is
the same: tokens are what context windows hold and what APIs charge
for.
"""

import re

TOKEN_PATTERN = re.compile(r"[A-Za-z]+|[0-9]+|[^\sA-Za-z0-9]")


def tokenize(text):
    """Split text into words, numbers, and single punctuation marks."""
    return TOKEN_PATTERN.findall(text)


def build_vocab(texts):
    """Assign each new token the next free ID, in order of appearance."""
    vocab = {}
    for text in texts:
        for token in tokenize(text):
            if token not in vocab:
                vocab[token] = len(vocab)
    return vocab


def encode(text, vocab):
    return [vocab[token] for token in tokenize(text)]


def decode(ids, vocab):
    inverse = {token_id: token for token, token_id in vocab.items()}
    text = " ".join(inverse[token_id] for token_id in ids)
    return text.replace(" .", ".").replace(" ,", ",")


def main():
    print("Lesson 03 - Tokens: what the model actually reads")
    print("==================================================")

    short = "Book a meeting with Sara on Tuesday."
    padded = (
        "Please could you kindly book a meeting with Sara on Tuesday, "
        "if that is possible."
    )
    print("\n1. Same job, different token cost")
    for label, text in [("Direct ", short), ("Padded ", padded)]:
        tokens = tokenize(text)
        print(f"   {label}: {len(tokens)} tokens - {tokens}")

    sentences = [short, padded]
    vocab = build_vocab(sentences)
    ids = encode(short, vocab)
    print("\n2. Text becomes numbers, and back")
    print(f"   Vocabulary size: {len(vocab)} tokens")
    print(f"   Encoded: {ids}")
    print(f"   Decoded: {decode(ids, vocab)}")

    paragraph = (
        "Your agent reads the inbox every morning. It sorts each message "
        "by topic and urgency. Urgent messages go to a human. The rest "
        "are drafted, checked, and sent."
    )
    window = 20
    tokens = tokenize(paragraph)
    kept = tokens[:window]
    kept_text = " ".join(kept).replace(" .", ".").replace(" ,", ",")
    print(f"\n3. A context window is a hard budget (window = {window} tokens)")
    print(f"   Paragraph length: {len(tokens)} tokens")
    print(f"   What fits:        \"{kept_text}\"")
    print(f"   What is cut:      {len(tokens) - window} tokens never reach the model")

    print(
        "\nNote: real tokenizers are subword tokenizers. Ours treats "
        "'rebooked' as one\ntoken; a production tokenizer splits rare "
        "words into pieces such as 're' +\n'book' + 'ed'. The counts "
        "differ, the lesson does not: tokens are the unit."
    )


if __name__ == "__main__":
    main()
