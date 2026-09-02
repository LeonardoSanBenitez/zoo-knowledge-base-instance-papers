# Kahneman & Deaton 2010 — a stub, and why it is a stub

maria, 2026-09-02. `read_depth: abstract-only`. **No assessment in this record
carries any weight and none is offered.** Every number in it is second-hand from
`kkm2023-conflict-resolved` and marked so in its `source` field.

## Why the record exists at all

Three records in this corpus now depend on this paper: the 2021 study exists to
contradict it, the 2023 adversarial collaboration exists to reconcile the two, and
my reanalysis rests on both. A knowledge base that holds those three and silently
omits their anchor is worse than one that holds a stub saying *this is the anchor,
here is what it claims, and here is exactly why nobody here has read it.*

## The retrieval failure, in full

Six routes, none of which produced a PDF:

| # | route | result |
|---|---|---|
| 1 | `ncbi.nlm.nih.gov/pmc/articles/PMC2944762/pdf/` | 1,817 B of HTML |
| 2 | Europe PMC REST `fullTextXML` | **HTTP 200 with a zero-byte body** |
| 3 | `pnas.org/doi/pdf/10.1073/pnas.1011492107` | Cloudflare interstitial |
| 4 | `europepmc.org/articles/pmc2944762?pdf=render` | 403 on `/api/getPdf` |
| 5 | `pmc.ncbi.nlm.nih.gov/.../pnas.201011492.pdf` | 1,817 B of HTML |
| 6 | NCBI OA service `oa.fcgi` | 404 — the endpoint is retired |

And the part that belongs in the "ways HTTP lies" catalogue:

- **Unpaywall** reports `is_oa: true`, `oa_status: green`, with exactly one location
  — route 1, which serves an interstitial.
- **Semantic Scholar** reports an `openAccessPdf` URL — route 4, which 403s.
- **Europe PMC** answers the full-text call with **200 and an empty body**, which
  every downstream tool will treat as "an article with no text" rather than "no
  access".

Three independent open-access indexes assert this article's PDF is available. None
of the URLs they give returns a PDF. The paper is free to a human with a browser and
unavailable to any automated agent, and **no availability metric in existence
distinguishes that state from open**. It is the same shape as
`laurinavichyute2022-share-the-code` — the identifier resolves, and nothing is there
— arriving from a different direction: here the *index* resolves and the *object*
does not.

A fourth failure mode caught the same afternoon, worth recording next to these:
requesting PMC id `PMC10013825` when I wanted `PMC10013834` returned **HTTP 200 and
a complete, valid, well-formed article about magnetic nanoparticles and dendritic
cell tumour vaccines**. A wrong identifier is indistinguishable from a right one
except by reading the title back. `tools/jats2txt.py --meta` now exists partly to
make that one cheap.

## What it claims

"Emotional well-being rises with log income, but there is no further progress beyond
an annual income of ∼$75,000." From more than 450,000 Gallup-Healthways responses,
US, 2008–9, using dichotomous yes/no items about yesterday's feelings.

Two things about the famous number, both from KKM 2023 rather than from the paper:

- **$75,000 is the midpoint of the "60 to 90K" survey category.** It is not an
  estimate of anything. KKM: "A more precise statement would be that there is no
  further progress in average happiness beyond a threshold at or below 90K."
- The evidence for flattening is that the top two income categories are
  statistically indistinguishable. That is an acceptance of a null, and — see
  `maria2026-happiness-income-spread#c4` — the same acceptance, made at a
  self-chosen cut point, is where the 2023 paper's threshold comes from too.

## Owed

Leonardo has offered to fetch papers before. This one is not paywalled; it is
bot-blocked, which is a different problem and probably an easier one. Until it is
read, `kkm2023-conflict-resolved#c2` — the ceiling-effect argument — is accepted on
the argument and not on any evidence I have seen.
