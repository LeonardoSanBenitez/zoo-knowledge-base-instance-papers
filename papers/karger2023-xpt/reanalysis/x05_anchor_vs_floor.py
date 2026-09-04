"""x05 -- Anchoring or a floor? Partially decidable from the published numbers.

MY OWN OPEN QUESTION, from the record: the 1-in-X format was preceded by ten
reference classes. If those anchors dragged the answers down, the format gap is
an anchoring effect and not the floor effect I claimed. The two make different
predictions and some of them are checkable without any new data.

THE ANCHOR SET (report footnote 69, the three it names):
    1 in 2            a fair coin lands tails
    1 in 300,000      lifetime probability of dying from lightning
    1 in 10,000,000   a random newborn becomes US president

THE ANSWERS given in that format:
    1 in 2,000        total catastrophe by 2100
    1 in 50,000       AI catastrophe by 2100
    1 in 20,000,000   total extinction by 2100
    1 in 40,000,000   AI extinction by 2100

PREDICTIONS THAT DIFFER
  anchoring (classic): answers cluster ON or BETWEEN the presented values, and
      do not go beyond the extremes of the anchor range.
  floor removal: answers go wherever the belief is, including OUTSIDE the anchor
      range; the anchors only supply a scale on which small numbers are sayable.

PREDICTION THEY SHARE
  Both predict the gap grows with rarity, so that test -- which I already ran in
  x04 -- cannot separate them. It only rules out "two noisy measurements".

Run: python x05_anchor_vs_floor.py
"""
import csv
import math

ANCHORS = [("fair coin tails", 2), ("death by lightning", 300_000),
           ("random newborn becomes US president", 10_000_000)]
ANSWERS = [("total catastrophe by 2100", 2_000),
           ("AI catastrophe by 2100", 50_000),
           ("total extinction by 2100", 20_000_000),
           ("AI extinction by 2100", 40_000_000)]


def main():
    rows = []
    amin = min(a[1] for a in ANCHORS)
    amax = max(a[1] for a in ANCHORS)
    print("=" * 88)
    print("1. DO THE ANSWERS STAY INSIDE THE ANCHOR RANGE?")
    print("=" * 88)
    print(f"  anchor range shown: 1 in {amin:,} to 1 in {amax:,}")
    print()
    print(f"  {'answer':<30} {'1 in X':>14} {'outside the range?':>20}")
    outside = 0
    for label, x in ANSWERS:
        out = x > amax or x < amin
        outside += out
        print(f"  {label:<30} {x:14,} {('YES, beyond' if out else 'no'):>20}")
        rows.append(dict(check="range", answer=label, one_in_x=x,
                         outside_anchor_range=bool(out)))
    print()
    print(f"  {outside} of {len(ANSWERS)} answers fall OUTSIDE the anchor range,")
    print("  both of them beyond its rare end (1 in 20 million and 1 in 40")
    print("  million against a smallest anchor of 1 in 10 million).")
    print()
    print("  Classic anchoring does not predict systematic extrapolation past")
    print("  the extreme anchor. This is evidence AGAINST anchoring as the sole")
    print("  mechanism -- though not against it as a contributor.")

    print()
    print("=" * 88)
    print("2. DO THE ANSWERS CLUSTER NEAR THE ANCHORS?")
    print("   Distance in log10 units from each answer to its nearest anchor.")
    print("=" * 88)
    print(f"  {'answer':<30} {'nearest anchor':<38} {'log10 distance':>15}")
    ds = []
    for label, x in ANSWERS:
        best = min(ANCHORS, key=lambda a: abs(math.log10(a[1]) - math.log10(x)))
        d = abs(math.log10(best[1]) - math.log10(x))
        ds.append(d)
        print(f"  {label:<30} {best[0]:<38} {d:15.2f}")
        rows.append(dict(check="distance", answer=label, nearest_anchor=best[0],
                         log10_distance=d))
    print()
    print(f"  mean log10 distance to the nearest anchor: {sum(ds)/len(ds):.2f}")
    print("  i.e. the typical answer sits about a factor of ten away from any")
    print("  number the respondents were shown. They are not echoing the")
    print("  anchors; they are using the scale the anchors established.")

    print()
    print("=" * 88)
    print("3. WHAT THE TEXTBOX FORMAT COULD NOT HAVE SAID")
    print("=" * 88)
    print("  The 1-in-X extinction answer is 1 in 20,000,000 = 0.000005%.")
    print("  Entered as a percentage that is 5e-6, which requires typing five")
    print("  significant places after the decimal point. The observed textbox")
    print("  answer is 4%, the 40th percentile of a 0-100 box.")
    print()
    for label, x in ANSWERS:
        pct = 100.0 / x
        dps = max(0, int(math.ceil(-math.log10(pct))) + 1)
        print(f"  {label:<30} = {pct:.8f}%  -> needs ~{dps} decimal places")
        rows.append(dict(check="typing", answer=label, pct=pct,
                         decimal_places_needed=dps))
    print()
    print("  A response format is not neutral about which answers are easy to")
    print("  give. That is the whole claim, and it does not require anchoring")
    print("  to be false -- the two mechanisms are close to the same thing")
    print("  described from different ends: the anchors work BY making small")
    print("  numbers sayable.")

    print()
    print("=" * 88)
    print("VERDICT, and what would settle it")
    print("=" * 88)
    print("  Partially resolved. Anchoring in its classic form (cluster on the")
    print("  presented values, do not exceed them) is contradicted: 2 of 4")
    print("  answers are beyond the rarest anchor and the mean distance to any")
    print("  anchor is a factor of ten.")
    print("  NOT resolved: whether a DIFFERENT anchor set would move the")
    print("  answers again. That needs an experiment nobody has run -- the same")
    print("  question in 1-in-X format under two different anchor ladders. It")
    print("  is cheap, and until someone runs it the size of the format effect")
    print("  is known and its cause is not.")

    keys = sorted({k for r in rows for k in r})
    with open("out_anchor_vs_floor.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("\nwrote out_anchor_vs_floor.csv")


if __name__ == "__main__":
    main()
