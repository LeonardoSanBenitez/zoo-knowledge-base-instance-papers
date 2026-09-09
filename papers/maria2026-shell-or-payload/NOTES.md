# When a data link resolves, how often does it return the data?

Measured 2026-09-08. Nobody had. The literature measures whether links *resolve*; the best
measurement of that (`briney2024-data-rot`) states in its own Results that a login wall was
counted as resolving.

## The one idea worth stealing

**Per-host null calibration.** For every link, build a nonsense sibling on the same host —
same shape, identifier replaced by a random token — and fetch both.

> If the host returns the same thing for a real identifier and an invented one, the host is
> not discriminating, and the link's HTTP 200 carries no information about whether anything
> is there.

One extra request. It turns "the link resolved" from an assertion into a measurement, and it
is the generalisation of the one-line control that started all of this: *run your check
against an identifier you invented.*

## What came back

160 PLOS ONE open-access articles, four year strata (2016, 2019, 2022, 2025). 151 have a
parsable data availability statement. **Only 24.4% carry any external link at all** — 58.9%
say the data are within the paper. That leaves 60 unique links, 53 of them fetchable:

| class | n | share of classifiable | 95% CI |
|---|---|---|---|
| **payload** | 31 | 58.5% | [45.1, 70.7] |
| **shell** | 13 | 24.5% | [14.9, 37.6] |
| **homepage** | 7 | 13.2% | [6.5, 24.8] |
| **dead** | 2 | 3.8% | [1.0, 12.8] |

> **37.7% [25.9, 51.2] resolve without delivering the resource.**

The other 7 could not be fetched at all — 403, TLS failure, timeout — and are excluded rather
than guessed at.

**A near-replication I did not plan.** The homepage rate here is **13.2%**. Briney 2024
measures the same category, by a different method, over 1,342 URLs from a different
institution and a different decade: **13.4%**. That is the only quantity both instruments
measure the same way, and they agree.

## The mechanism, confirmed rather than inferred

    doi.org/10.6084/m9.figshare.4307765.v1          -> 202
    doi.org/10.6084/m9.figshare.99999999999.v1      -> 404      the resolver discriminates

    figshare.com/articles/.../11339987              -> 202
    figshare.com/articles/.../9999999999            -> 202      the front end does not

**The same resource is verifiable through its DOI and unverifiable through the publisher's own
URL.** That is a better argument for persistent identifiers than any survival rate, because it
is about whether you can check *today* rather than whether it will be there in a decade.

Consistent with it: DOI links classified `payload` 88% of the time (n=8), plain URLs 53%
(n=45).

## Then I stopped trusting my own instrument

`shell` means *this URL cannot demonstrate the resource exists.* It does **not** mean the data
is gone, and the second instrument exists to keep me honest about that.

`authoritative.py` asks each host's own API the question that decides. Five host families
implemented — OSF, Zenodo, figshare, GitHub, DOI registries — covering 33 of the 60 links.
Every other host returns `unknown-host`, which is the point: *a link checker that reports
`available` for a host it cannot interrogate is reporting that the host answered, and calling
it something else.*

| naive fetch → | exists | never-existed | private |
|---|---|---|---|
| payload | 22 | 0 | 0 |
| shell | 6 | 0 | 2 |
| blocked | 2 | 0 | 0 |
| dead | 0 | 1 | 0 |

> **8 of 33 links (24%, CI [12.8, 41.0]) that the fetch could not verify are reported by the
> host itself as present. The failure was the instrument's, not the deposit's.**

That is the same shape as `maria2026-codecheck-limiting-constraints`, reached by a completely
different route: there, 61% of incomplete human reproductions were limited by the checker
rather than by the deposit. **An instrument that attributes its blind spots to the object it
measures will always find the object at fault.**

## Two things every link checker in this literature scores as "available"

**A private OSF node cited in a published data availability statement.**
`api.osf.io/v2/guids/ysxuz/` → 401. With the `view_only` token that was left in the printed
URL → 200, and `public: false`. So the data is reachable only because an anonymous-peer-review
token survived into the published paper. **That token can be revoked by its owner at any time,
and when it is, nothing about the printed link changes.** A second OSF link in the sample is
401 with no token at all.

**A Dryad DOI that was never registered.** `10.5061/dryad.fttdz08wm`, printed verbatim in
*"Data are available on Dryad (doi.org/10.5061/dryad.fttdz08wm)."*

    doi.org        404
    DataCite       404 both letter cases, and 0 hits on a DOI-field search
    Crossref       404
    datadryad.org  200  {"identifier": "doi:10.5061/dryad.fttdz08wm", "id": 95584,
                         "message": "Identifier cannot be viewed..."}

The submission exists inside Dryad and **was never published**, so the DOI was never minted.
*"Your DOI does not resolve"* is true and useless. *"Your Dryad submission 95584 was never
published"* is actionable, and only the host's own API can say it.

## What this is for

Three consequences, and the first is the one I would act on.

1. **A link check must ask each host the question that decides.** `authoritative.py` is ten
   lines per host and it is the difference between "the server answered" and "the data is
   there". Where no such endpoint exists, say `unknown` — 45% of the sampled links, and not a
   random 45%: national statistics portals, disease databases, institutional repositories, the
   hosts least likely to have an API and most likely to be the only route to the data.
2. **Report `private` and `reserved-never-published` as their own states.** They are neither
   available nor dead, they are common enough to meet in a sample of 33, and each has a
   different, actionable sentence attached.
3. **Never let a checker attribute its own blind spot to the deposit.** A quarter of what mine
   could not verify was there all along.

## Limits, stated plainly

n = 53 classifiable links, one journal, Europe PMC search-index order rather than random. The
direction is robust; the rate is not. `shell` conflates a host that cannot discriminate with a
host serving a soft-404, and separating them takes one more request. Seven links were blocked
outright from this machine — some of that is bot-blocking, which means a checker in a data
centre and a researcher with a browser see different worlds, and nobody has measured *that*
gap either.

## Reproducing

```sh
cd reanalysis
python harvest_das.py          # writes ../artifacts/das_links.json  (~40 MB fetched, not kept)
python shell_or_payload.py --validate    # 6/6 known answers, then
python shell_or_payload.py --corpus
python authoritative.py --validate       # 7/7 known answers, then
python authoritative.py --corpus
```

Both instruments validate against known answers before they are allowed near the corpus. That
ordering is the method, not a courtesy.
