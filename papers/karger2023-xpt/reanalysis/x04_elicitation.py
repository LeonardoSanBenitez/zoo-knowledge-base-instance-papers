"""x04 -- The same people, the same question, two response formats, and answers
six orders of magnitude apart.

THE DATUM. XPT footnote 70. A public sample of college graduates answered the
existential-risk questions twice, in two formats:

  (A) "simple textbox": type a probability as a percentage.
  (B) "1-in-X": they were first shown ten calibrating reference classes --
      1 in 2 for a coin, 1 in 300,000 for death by lightning, 1 in 10,000,000
      for a random newborn becoming US president -- and then asked to fill in X.

Restricting to the N=405 respondents who answered BOTH (the report gives this
subsample explicitly, because the survey was staged and not everyone saw both):

      Total extinction by 2100    4%     vs   1 in 20,000,000
      AI extinction by 2100       1.5%   vs   1 in 40,000,000
      Total catastrophe by 2100   10%    vs   1 in 2,000
      AI catastrophe by 2100      5%     vs   1 in 50,000

This script does the arithmetic the report does not: the size of the gap, how it
scales with the rarity of the event, and what each format implies about a
conditional probability that has a plain meaning -- given a catastrophe that
kills a tenth of humanity, how likely is it to go all the way?

No simulation is needed. This is eight numbers and a calculator, and that is
exactly why it is worth writing down: the finding is sitting in a footnote.

Run: python x04_elicitation.py
"""
import csv
import math

# (label, textbox percentage, "1 in X" denominator)
ROWS = [
    ("total extinction by 2100", 4.0, 20_000_000),
    ("AI extinction by 2100", 1.5, 40_000_000),
    ("total catastrophe by 2100", 10.0, 2_000),
    ("AI catastrophe by 2100", 5.0, 50_000),
]

# The XPT forecaster groups, for comparison. (catastrophe %, extinction %)
GROUPS = [
    ("superforecasters", 9.05, 1.0),
    ("domain experts", 20.0, 6.0),
    ("general x-risk experts", 28.95, 6.6),
    ("public, textbox", 10.0, 4.0),
    ("public, 1-in-X", 100.0 / 2_000, 100.0 / 20_000_000),
]


def main():
    out = []
    print("=" * 92)
    print("1. THE GAP, per question (N = 405 matched respondents)")
    print("=" * 92)
    print(f"  {'question':<28} {'textbox':>10} {'1-in-X':>16} {'ratio':>14}")
    for label, pct, denom in ROWS:
        p_box = pct / 100.0
        p_inx = 1.0 / denom
        ratio = p_box / p_inx
        print(f"  {label:<28} {pct:9.2f}% {p_inx:16.3e} {ratio:14,.0f}x")
        out.append(dict(check="gap", question=label, textbox_p=p_box,
                        one_in_x_p=p_inx, ratio=ratio))
    print()
    print("  The textbox format returns numbers between two thousand and eight")
    print("  hundred thousand times larger than the 1-in-X format, FROM THE SAME")
    print("  PEOPLE ON THE SAME QUESTION IN THE SAME SURVEY.")

    print()
    print("=" * 92)
    print("2. THE GAP GROWS WITH THE RARITY OF THE EVENT")
    print("=" * 92)
    print(f"  {'question':<28} {'1-in-X probability':>20} {'ratio':>14}")
    for r in sorted(out, key=lambda x: -x["one_in_x_p"]):
        print(f"  {r['question']:<28} {r['one_in_x_p']:20.3e} "
              f"{r['ratio']:14,.0f}x")
    print()
    print("  This is the signature of a FLOOR, not of two noisy measurements of")
    print("  one thing. Nobody types 0.000005 into a percentage box. The 1-in-X")
    print("  format removes the floor by changing the units the answer is")
    print("  expressed in, and the gap opens exactly where the floor binds.")

    print()
    print("=" * 92)
    print("3. THE CONDITIONAL THAT HAS A PLAIN MEANING")
    print("   P(extinction | catastrophe): given an event that kills a tenth of")
    print("   humanity within five years, how likely is it to finish the job?")
    print("=" * 92)
    print(f"  {'group / format':<26} {'P(cat)':>10} {'P(ext)':>12} "
          f"{'P(ext|cat)':>13}")
    for name, cat, ext in GROUPS:
        cond = ext / cat
        print(f"  {name:<26} {cat:9.3f}% {ext:11.5f}% {cond:12.2%}")
        out.append(dict(check="conditional", group=name, p_cat=cat / 100,
                        p_ext=ext / 100, p_ext_given_cat=cond))
    print()
    print("  Every forecaster group lands between 11% and 40%. The public's")
    print("  textbox answers land in the same place (40%). Their 1-IN-X answers")
    print("  land at 0.01% -- three to four orders of magnitude away, from the")
    print("  same respondents.")
    print()
    print("  Note which way this cuts. The 1-in-X numbers are NOT obviously the")
    print("  better ones. A conditional of 0.01% says a catastrophe killing 800")
    print("  million people almost never escalates, which is its own strong and")
    print("  unargued claim. The finding is not that one format is right. It is")
    print("  that THE FORMAT, not the belief, is setting the number.")

    print()
    print("=" * 92)
    print("4. WHAT SURVIVES THE FORMAT CHANGE: the ordering, and only that")
    print("=" * 92)
    box = {r["question"]: r["textbox_p"] for r in out if r.get("check") == "gap"}
    inx = {r["question"]: r["one_in_x_p"] for r in out if r.get("check") == "gap"}
    qs = list(box)
    print(f"  {'pair':<52} {'textbox ratio':>14} {'1-in-X ratio':>14}")
    for i in range(len(qs)):
        for j in range(i + 1, len(qs)):
            a, b = qs[i], qs[j]
            rb = box[a] / box[b]
            ri = inx[a] / inx[b]
            print(f"  {a + '  /  ' + b:<52} {rb:14.3f} {ri:14.3f}")
            out.append(dict(check="ratio-preservation", pair=f"{a}/{b}",
                            textbox_ratio=rb, one_in_x_ratio=ri))
    # CORRECTED IN PLACE 2026-09-04. The first version of this section said
    # "the ordering survives, the levels do not", implying the RATIOS survive
    # too. My own table refutes that: only 1 of the 6 pairwise ratios is within
    # a factor of 2 across formats. What survives is the RANKING, not the
    # ratios. Leaving the wrong sentence in a script that prints the refuting
    # table would be the exact failure this corpus exists to prevent.
    pres = [r for r in out if r.get("check") == "ratio-preservation"]
    within2 = [r for r in pres
               if r["one_in_x_ratio"] > 0
               and 0.5 <= (r["textbox_ratio"] / r["one_in_x_ratio"]) <= 2.0]
    box_rank = sorted(box, key=lambda q: -box[q])
    inx_rank = sorted(inx, key=lambda q: -inx[q])
    def short(q):
        w = q.split()
        return w[0][:5] + "-" + w[1][:3]
    print()
    print("  RANKS: textbox  " + " > ".join(short(q) for q in box_rank))
    print("         1-in-X   " + " > ".join(short(q) for q in inx_rank))
    print(f"         identical: {box_rank == inx_rank}   (4 of 4 ranks)")
    print(f"  RATIOS: {len(within2)} of {len(pres)} pairwise ratios agree within "
          f"a factor of 2 across formats.")
    print()
    print("  So the ORDERING is fully preserved and the RATIOS are not. Only")
    print("  total-extinction / AI-extinction survives (2.67 vs 2.00); the")
    print("  extinction-versus-catastrophe ratios move by four orders of")
    print("  magnitude, and even total-catastrophe / AI-catastrophe moves from")
    print("  2 to 25.")
    print()
    print("  These answers therefore carry ORDINAL information about which risk")
    print("  is bigger and essentially none about how much bigger, or how big.")
    print("  Which is the problem, because every policy use of them is cardinal:")
    print("  an expected-value calculation, a cost-benefit ratio, a threshold.")

    keys = sorted({k for r in out for k in r})
    with open("out_elicitation.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(out)
    print("\nwrote out_elicitation.csv")


if __name__ == "__main__":
    main()
