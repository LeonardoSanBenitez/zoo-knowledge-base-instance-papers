"""Recover the denominators Obels et al. do not print, from the percentages they do.

THE PROBLEM. The paper reports inter-rater agreement as four rounded
percentages -- 60% and 55% for SPSS scripts, 75% and 56% for R -- and states
elsewhere that 17 articles used SPSS and 13 used R. Writing those percentages
into a record with n = 17 and n = 13 fails the `value == count/denominator`
checksum, which is how I found out that **neither 55% nor 60% is attainable as
k/17, and neither 75% nor 56% as k/13.** The stated article counts are not the
denominators of the agreement figures.

My own CONTRIBUTING rule says: fill `count` and `denominator` ONLY from the
source, because multiplying a rounded value by a guessed n fabricates a count,
and a fabricated count that passes the checksum is worse than an absent one. I
had done exactly that. The checksum caught it.

THE RECOVERY. Both percentages in a language group must share one denominator.
Enumerate every n and ask which admits both.

  SPSS:  60% needs n in {10, 15, 20, 25, ...};  55% needs n in {11, 20, 22, ...}
         -> unique intersection at n <= 25:  n = 20   (12/20 and 11/20)
  R:     75% needs n in {8, 12, 16, 20, 24};   56% needs n in {9, 16, 18, 25}
         -> unique intersection at n <= 25:  n = 16   (12/16 and 9/16)

And the third, independent confirmation, from the paper's own prose: "R was used
as a coding language in 13 ... 17 papers used SPSS ... and 3 papers used both".
So the SPSS-involving group is 17 + 3 = **20** and the R-involving group is
13 + 3 = **16**, and 20 + 16 = 36, the number of articles that shared both data
and code. The coders evidently scored each article once per language it used.

Three routes to the same pair of numbers, none of which is "assume the n I had
lying around".

Usage:  python recover_denominators.py
"""

REPORTED = {
    "SPSS": {"executability": 60, "reproducibility": 55},
    "R": {"executability": 75, "reproducibility": 56},
}
STATED_ARTICLE_COUNTS = {"SPSS": 17, "R": 13, "both languages": 3}
NMAX = 40


def admits(pct, n):
    return [k for k in range(n + 1) if round(100 * k / n) == pct]


print("REPORTED percentages and whether the STATED article counts can produce them")
print("-" * 74)
for lang, d in REPORTED.items():
    n = STATED_ARTICLE_COUNTS[lang]
    for what, pct in d.items():
        ks = admits(pct, n)
        print("  %-5s %-16s %2d%%  with n=%d -> %s"
              % (lang, what, pct, n, ("k=%s" % ks) if ks else "IMPOSSIBLE"))
print()
print("RECOVERY: which single n admits BOTH percentages of a language group?")
print("-" * 74)
recovered = {}
for lang, d in REPORTED.items():
    cands = [n for n in range(4, NMAX + 1)
             if all(admits(pct, n) for pct in d.values())]
    print("  %-5s candidates up to n=%d : %s" % (lang, NMAX, cands))
    small = [n for n in cands if n <= 25]
    if len(small) == 1:
        n = small[0]
        recovered[lang] = n
        detail = ", ".join("%s %d/%d" % (w, admits(p, n)[0], n) for w, p in d.items())
        print("        unique at n<=25 -> n = %d   (%s)" % (n, detail))
    else:
        print("        NOT unique; do not fill count/denominator")
print()
print("THIRD CONFIRMATION, from the paper's own prose")
print("-" * 74)
s, r, b = (STATED_ARTICLE_COUNTS[k] for k in ("SPSS", "R", "both languages"))
print("  '17 papers used SPSS ... R was used in 13 ... 3 papers used both'")
print("  SPSS-involving = %d + %d = %d      R-involving = %d + %d = %d"
      % (s, b, s + b, r, b, r + b))
print("  and %d + %d = %d, the number of articles that shared both data and code."
      % (s + b, r + b, s + b + r + b))
ok = recovered.get("SPSS") == s + b and recovered.get("R") == r + b
print()
print("RECOVERY CONFIRMED BY THREE INDEPENDENT ROUTES" if ok else
      "ROUTES DISAGREE -- leave count/denominator absent")
