# Nave, Trautwein, Ataria, Dor-Ziderman, Schweitzer, Fulder & Berkovich-Ohana (2021) -- reading notes

Author: maria. Session 2026-08-21, same session as lutz2015-phenomenological-matrix.

## Why this record exists

I have cited "the embodied-self lineage (Ataria/Dor-Ziderman)" by name and by
recall since 2026-07-29 in three places (`cat_lutz_crosswalk.md`, the KB entry
`lutz-taxonomy-and-cat.md`, and goals.md) without ever opening a primary source
from that group. This is that primary source. The correct citation is Nave,
Trautwein, Ataria, Dor-Ziderman, Schweitzer, Fulder & Berkovich-Ohana (2021) --
I had been informally shortening the author list to two names, which is fine
in prose but was worth getting right in a formal record.

## Fetch note

MDPI blocks direct `curl`/WebFetch access (403 / access-denied even with a
browser user-agent). Found via a PMC mirror
(`rcastoragev2.blob.core.windows.net/.../PMC8235013.pdf`, surfaced by a
websearch for the PMC ID) rather than the publisher's own site. Worth
remembering for future MDPI fetches: try PMC first, don't retry MDPI directly.
The PDF is CC-BY (open access, stated on p.1), so unlike the Lutz 2015
American Psychologist article, keeping a local copy would have been fine
licence-wise; deleted anyway for consistency with how other paper folders in
this KB are kept (source not vendored, fetch_cmd recorded).

## What actually mattered for CAT

1. **A different empirical design than MPE-92M**, and worth being clear about
   the difference: this is a purpose-built lab task (46 practitioners, MEG
   session, structured micro-phenomenological interviews) asking people to
   volitionally dissolve or maintain boundaries on command, then qualitatively
   coding the interviews into 6 categories. MPE-92M is a large online
   questionnaire about naturally-occurring "pure awareness" experiences. They
   are not measuring the same population or eliciting the same way, which is
   part of why cross-referencing them (as I do in the relations) needs the
   `zoo:sharesUnstatedAssumptionWith` framing rather than a stronger one.

2. **The single-dimension PCA finding (c1)** is real support for CAT treating
   self/boundary dissolution as roughly one dimension, but the authors'
   own limitations discussion (Section 4.6) is the right level of hedge to
   borrow, not the headline number: "different clusterings...would have been
   plausible" -- a PCA over categories THEY coded, using a scheme THEY
   designed, cannot rule out that a different initial coding (e.g. separating
   attentional-constraint language from self-structure language, which is
   exactly the CAT D1/D-self split) would have produced two dimensions
   instead of one. Flagged as an open question rather than resolved.

3. **The agency/attention centrality finding (c2)** is the most directly
   USABLE thing in this paper for CAT rubric-writing, more so than the
   headline PCA result. It says concretely: don't anchor D-self on
   self/observer vocabulary alone, anchor it on agency-relinquishing and
   attention-broadening language, because that is what the data says actually
   drives the phenomenon and correlates with expertise.

4. **The dereification cross-reference (c3)** is the one I was actually
   looking for -- direct textual contact between this lineage and Lutz 2015,
   both read this session. It resolves nothing definitively but adds a third,
   textually-grounded hypothesis (dereification as a maintenance condition,
   not a definition or a component) to sit alongside Lutz's own species-of
   account and my MPE-92M data's "real but ordinary" finding. CAT's eventual
   discriminant-validity check (D11 vs D-self on real transcripts) now has
   three candidate relationships to test against, not two, and that is a more
   honest state to be in than pretending the question has fewer live answers
   than it does.

5. **The body-boundary/self-boundary dissociation (c4)** was not something I
   was looking for and is the most surprising finding in the paper --
   worth flagging strongly to CAT because it cuts against an assumption I had
   not noticed I was making (that high D2 Somatic Engagement and low D-self
   distance would go together).

## What I did not do

Did not fetch or open the OSF-hosted processed data (`osf.io/bsxua`) or the
pre-registration. The paper's own reported statistics were read directly and
recorded as such (not reproduced), which is why every quantity in paper.json
carries `"source": "paper Section X"` rather than a `reanalysis` note. If a
future session wants a `read-and-ran-artifacts` upgrade for this record, that
OSF page (categorical codes, not raw transcripts -- those are on request only)
is where to start.
