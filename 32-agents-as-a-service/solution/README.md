# Solution 32: Price the operation, not the demo

**The 10x test (illustrative inputs, volume raised to 4,000 enquiries).** `operating_costs_10x.py` produces:

```text
Model usage                            $   57.60
TOTAL per month                        $  431.86
Cost per enquiry                       $    0.11
```

Model usage grows exactly 10x ($5.76 to $57.60) and is still only about 13% of the total. Hosting, tools, and messaging stay flat at these volumes. Human operations were kept flat in the script, which is optimistic at 10x volume (review queues grow), but even doubling them leaves the conclusion intact. Total cost rises just 15% while volume rises 900%, and cost per enquiry falls from $0.94 to $0.11.

What that means for pricing: an operator whose fee scales linearly with enquiry count is charging for the one input that barely costs anything. Fair AaaS pricing is mostly a flat operations fee for the human work, with volume tiers that step gently, because the operator's real costs step gently. If you are buying, a quote that multiplies by volume is a quote built on the token fallacy from the lesson.

**The honesty test.** The easiest line to quietly drop is the monthly improvement work ($80 here), or its cousin, the daily review inside operations hours. The quote looks cheaper and nothing breaks in month one. What breaks is month four: the business has changed a price, a service, or a booking rule, the agent still quotes the old world, a prospect records the wrong promise, and the client discovers their agent has been confidently out of date for weeks. Dropped operations lines do not remove the work. They convert it into incidents.

**Your numbers will differ** from the illustrative ones, sometimes a lot (voice agents, for example, move the messaging line from footnote to headline). The shape is what transfers: tokens small, humans dominant, honesty about both.
