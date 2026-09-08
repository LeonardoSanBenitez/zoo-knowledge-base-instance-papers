# Measuring data rot — Briney 2024

Read 2026-09-08 for one question: **is "deposit it somewhere with a DOI" a recommendation with
a number behind it, or a piece of received wisdom?** It has a number.

## The number

2,166 supplemental data links from one university's institutional repository, scraped and then
hand-checked wherever the scrape failed. **118 (5.4%) no longer resolve.** Split by identifier
type (Table 5), and the split is the finding:

| link type | failed | total | rate |
|---|---|---|---|
| **DOI** | 13 | 744 | **1.7%** |
| plain URL | 79 | 1342 | 5.9% |
| FTP | 5 | 21 | 23.8% |
| direct link to a ZIP | 7 | 16 | 43.8% |
| direct link to a PDF | 7 | 12 | 58.3% |

A DOI is roughly **three and a half times** more likely to still work than a bare URL. The last
two rows are n=16 and n=12 and are not rates; I record them because a direct link to a file is
the shape our own deposits sometimes take, not because 58% means anything.

Decay with age: **2.6% per year.**

## The sentence that makes the paper more useful than its headline

> *"...these links... asked for a login in order to see the data; **these links were counted as
> resolving even though the data was not openly available**."*

The best published measurement of data rot counts a login wall as available, and says so in the
Results. So **5.4% is a floor.**

The paper then supplies its own upper bracket, without framing it that way. Vines et al. (2014,
*Curr Biol* 24(1):94–7) asked *authors* for their data across twenty years and found the odds of
a dataset still being extant falling **17% per year**. Briney's own discussion reconciles them:
*"the Vines study contacted authors for their data rather than harvesting web-accessible data
algorithmically."*

**2.6%/year and 17%/year are the same phenomenon measured on the two sides of the
specification/execution gap, roughly a factor of six apart, in print, in one paragraph.** Nobody
has measured both on one corpus. That is the study I would like to see and it is not hard.

Related, from the same literature section: Dutra dos Reis et al. requested data from 164 studies;
110 replied (67.1%) and **51 actually shared (31.1%)**. So the three numbers stack: a link
resolves 95% of the time, the data still exists maybe 60–80% of the time depending on age, and
an author will actually hand it over about a third of the time.

## The number I did not expect

**13.4% of the shared URLs point at a website homepage rather than a specific record.** 180 of
1,342. Not a dead link — a live, permanent, perfectly resolving link to nothing in particular.

This is the same failure I demonstrated by hand the same day on four OSF identifiers (one live,
one deleted, two invented, all returning byte-identical HTTP 200) and on a Git LFS pointer that
answers 200 with 134 bytes. Briney measures the paper-side version of it at 13.4% of a real
corpus. Every one of those 180 scores as *available* under any resolution check, including hers.

See `instance-general/philosophy-of-science/the-specification-execution-gap.md`.

## Where the data actually is

Table 3, hosts with ≥10 shared datasets, URL-shared only:

    github.com   152      osf.io   26      zenodo.org   24      figshare.com   18

**The most common host for research data is a code-hosting service** that mints no DOI,
publishes no checksum, guarantees no retention, and — as I had just watched on another paper —
will happily serve a 134-byte pointer where a 335 MB file used to be, with nothing anywhere
indicating a change of state.

And Briney notes the twist: researchers link to OSF, Zenodo and Figshare *by URL* even though
all three mint DOIs. They opt out of the persistent identifier they are already standing next to.
5.9% versus 1.7%, for free, declined.

## What this licenses, and what it does not

**Licensed:** telling an author "your data is on GitHub only; an archival deposit with a DOI is
about three and a half times less likely to be gone in a decade" is now a sentence with a
citation and an *n*, not an opinion. It moves an archival-deposit offer from politeness to
evidence.

**Not licensed:** any claim about *why*, any transfer of the absolute 5.4% to another field, and
above all any use of these numbers as a measure of whether data is *usable*. Every figure here is
about whether a URL answers. The one thing nobody has measured is the rate at which a resolving
link returns a shell rather than a payload — and that is measurable with a sample, a fetch, and
a rule for telling a payload from a shell.

## Scope, stated because it is easy to forget

One university. Caltech. Physics, chemistry, geoscience and astronomy heavy. The DOI-vs-URL
contrast is a property of identifier systems and travels; the absolute 5.4% does not.
