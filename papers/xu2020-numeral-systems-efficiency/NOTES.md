# Xu, Liu & Regier (2020), numeral systems and efficiency — notes

Author: maria, 2026-10-16. Sixth domain of the day; data on OSF behind a view-only key, and
OSF was down all afternoon, so this is an analytic check, not a reanalysis.

The check takes one line of thought. Most "exact restricted" languages say: one, two, three,
many. With need falling as a power of the number (the paper's own estimate puts 84% of all
need on 1-3), naming 1, 2 and 3 exactly is not merely good; among all 161,700 ways of choosing
three exact numbers it is the single best one. So these systems are efficient because they
count from one, and the model will call any language that counts from one efficient. What it
cannot do is say why a language stops at three rather than six; every stopping point lies on
the frontier.

The need distribution comes from English, a language with words for every number. That makes
the circle visible: we need small numbers often partly because we have words for them. The
authors show the result disappears under uniform need, to their credit.

Through-line, sixth instance: the structure that defines the class (convexity, no synonymy,
monotonicity, IFF, a prefix of the number line) carries the efficiency.

## 2026-11-12 — the deposit, at last

OSF came back, and the view-only key opened the node (curl needed `-g`, because `page[size]` is a glob to it). One file,
1.27 MB, sha256 as published. Inside is the whole analysis, Python 2-era, with the per-language grammars in
`langstrategy.py`.

What the code says is plainer than what I inferred in October. An attested exact-restricted language is scored by
`compute_cost_size_principle(ulim)`, and the hypothetical "efficient" exact curve is the same function at every k. So the
attested point lies on the curve unless its grammar complexity departs from the formula. For 15 of 17 it does not. For the
two that do, Hup and Waskia (both compose numerals), the departure puts them behind the frontier, dominated by plain prefix
systems. The model has a place for compositional numerals, and it charges them.

The candidate defect I nearly reported: 11 of 17 grammars give the "higher" rule the same word as the top numeral. It looked
like the cost treating an ambiguous word as exact. It is not: complexity is 13 with that string and 13 with an invented one,
so to the model the string is a placeholder (n4). Logged in the record as checked and withdrawn. Every documented harm in
the retro-repro project is a false fail; this would have been one more.

Still open: five of the thirty languages have no code in the deposit, and a caption says "six" where the code says five.
