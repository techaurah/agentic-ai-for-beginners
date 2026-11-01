# Exercise 32: Price the operation, not the demo

Use `operating_costs.py` and `operating-cost-worksheet.csv`.

1. **Your market, your numbers.** Fill the `your_value` column of the CSV for a business you know (yours, a client's, or a fictional one you can describe in one sentence). Use a real current model price from the provider's pricing page and a labour rate you would actually charge or pay. Write down where each number came from.

2. **The 10x test.** In the script, copy `ILLUSTRATIVE` to a second dict and raise `enquiries_per_month` from 400 to 4,000, keeping everything else the same. Run it. Which lines grow, which stay flat, and what happens to the cost per enquiry? Write three sentences on what that tells you about how an operator's pricing should change as a client grows.

3. **The honesty test.** List one line in the worksheet that a less honest operator could quietly drop to make their quote look cheaper, and write two sentences on what breaks, and when, if that line is not actually done.

Acceptance checks:
- Your CSV has no empty `your_value` cells in the volume, fixed, and human sections.
- Your 10x run shows model usage still a small share of the total, and cost per enquiry falling.
- The solution in `solution/` matches your reasoning on points 2 and 3 (your numbers will differ; the shape should not).
