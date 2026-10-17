"""k1 -- Is 'no improvement whatever beyond ~$75,000' what Kahneman & Deaton's own Table 2 shows?
Inputs transcribed from Table 2 (PMC2944762, read 2026-10-17): difference in mean between adjacent income groups
and its t value. SE = diff / t; 95% CI = diff +/- 1.96 SE; ratio of the top step to the step below it.
Author: maria 2026-10-17."""
rows = {  # measure: (top-vs-second diff, t), (second-vs-third diff, t)
    'positive affect': ((0.0035, 1.9), (0.0082, 4.4)),
    'blue affect (lower is better; sign as printed)': ((0.0013, 0.6), (-0.0131, 5.7)),
    'stress (sign as printed)': ((0.0055, 1.5), (0.0016, 0.4)),
    'ladder (0-10)': ((0.2264, 19.4), (0.2268, 19.7)),
}
for k, ((d1, t1), (d2, t2)) in rows.items():
    se = d1 / t1; lo, hi = d1 - 1.96 * se, d1 + 1.96 * se
    print(f"{k:<46} top step {d1:+.4f} (t {t1}) 95% CI [{lo:+.4f}, {hi:+.4f}] | step below {d2:+.4f} (t {t2}) | "
          f"top/below {d1/d2:+.2f}, CI upper/below {hi/abs(d2):.2f}")
print("Top group n = 72,744-73,109, second 40,136-40,301 (Table 2).")
