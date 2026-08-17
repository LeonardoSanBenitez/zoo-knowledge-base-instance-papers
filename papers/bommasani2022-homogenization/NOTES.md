# Notes — Bommasani, Creel, Kumar, Jurafsky & Liang (2022), Picking on the Same Person

Author: maria. Skimmed 2026-08-07; **read properly the same session** after the record
itself flagged that one of my own claims depended on a paper I had not opened.
Structured record: `paper.json`.

## Why I went back

`maria2026-marginal-competence#c4` asserted a `zoo:sharesUnstatedAssumptionWith` edge to
this paper — that both this literature and the correlated-errors literature assume
similarity of *outputs* is the way to measure loss of independence. I wrote that from an
abstract, flagged it as unsupportable, and `kb.py query --depth skimmed` kept it visible.
Good. **The claim was wrong**, and reading the paper produced a better one.

The summariser could not parse the PDF at all — returned an honest refusal. The PDF was
on disk from the same call. Read it directly. Second time this session that rule paid.

## What it actually does — and it is ahead of the 2025 work

Equation 3:

> H^individual(h¹,…,hᵏ) = SYSTEMIC FAILURE(h¹,…,hᵏ) / ∏ᵢ FAIL(hⁱ)
> = E_j[∏ᵢ Fⁱ(x_j)] / ∏ᵢ E_j[Fⁱ(x_j)]

The denominator **is the independence baseline** — the rate of everyone-fails-this-person
you would see if the decision-makers failed independently at their observed marginal
rates. H = 1 matches independence; H > 1 is homogenization beyond it.

And they say exactly why, in §3.1:

> SYSTEMIC FAILURE "will in general be higher for less accurate systems independent of a
> *specific* tendency to pick (i.e. fail) on the same person."

That is the accuracy confound I spent a session rediscovering in the 2025 multiple-choice
literature. It was anticipated and handled here in 2022. Kim et al. (2025) *regressed*
methodologically relative to this paper — they went from an independence-normalised ratio
back to a uniform-over-wrong-answers baseline.

§3.4 is unusual and worth borrowing from: they explicitly discuss the **convergent and
divergent validity** of their own metric (Campbell & Fiske 1959, Messick 1987, Jacobs &
Wallach 2021) — is it correlated with what it should be, uncorrelated with what it
shouldn't. Almost nobody does this for a newly minted metric. It should be cross-linked
with `instance-general/philosophy-of-science/construct-validity-and-formalization.md`,
which is about precisely this and does not cite it.

## The corrected version of my claim — sharper, and I think unsaid

Their null models heterogeneity across **decision-makers** (each model's marginal failure
rate) but not across **the people being judged**. If some applicants are genuinely weak,
every screener rejects them, and H > 1 with zero component sharing.

**The individual plays exactly the role that item difficulty plays in the MCQ setting.**
So Jo, Garg & Raghavan's (2026) critique of capability-only nulls applies directly to
Equation 3 — the null sits at the same rung of their ladder as the one they show is
insufficient. I have not seen anyone say this.

They half-see it, in footnote 4: *"some individuals can be justifiably rejected from all
opportunities (e.g. those attempting to become lawyers without passing the bar exam)"*.
The acknowledgement stays in prose and never enters the metric. That is the gap.

## The half that gets dropped in citation

§5, and they flag it as a surprise themselves: **sharing a foundation model does not
reliably homogenize outcomes. The adaptation method does** — linear probing consistently
produces more homogeneous outcomes than finetuning, in *both* vision (CLIP) and language
(RoBERTa). So shared components are not destiny.

Downstream work leans on the simple "shared components → shared failure" story that this
paper's own experiments partially contradict. And it fits the 2026 finding that residual
model clusters track fine-tuning provenance rather than shared base: what homogenizes is
the *pipeline*, not the *substrate*.

Data-sharing results (§4, German Credit n=1000 and ACS PUMS n=3.6M) do go the expected
way: sharing training data reliably increases homogenization, individual-level effects
generally exceeding group-level.

## Standing

`read_depth: read-full-text`. Claims c2 and c3 remain `unverified` — I read the setup and
the stated results, opened no artifacts and ran nothing. That is the honest line.
