# Word salad and the Power of Noise — notes

Author: maria, 2026-10-16. The RAG area's open question 2 called this "the cheapest decisive
test in the literature": if literal word salad improves a RAG reader, no information-theoretic
account of the noise effect can be right. I had a local GPU and an afternoon of pauses, so I ran
it, with the plan written down before I looked.

Nothing happened, which is itself a result. Word salad left accuracy where it was (−0.2 points;
the interval excludes the paper's +3). Real unrelated passages pulled it down slightly. One small
model, one setting: this does not refute the Power of Noise, but its most diagnostic form did not
appear where it should have been easiest to see.

What I was tempted to do and didn't: peek at 100 questions, see a trend, and stop. The plan file
is the only reason I can say the result was not chosen.
