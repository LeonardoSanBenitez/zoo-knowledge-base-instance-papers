# periti2024-systematic-comparison-cwe-lsc — notes (maria, 2026-11-03)

The paper a SemEval-2027 Task 3 participant should read first, for one reason: it shows that HOW you cluster matters
more than whether you cluster. With the same XL-LEXEME embeddings, graded change from affinity-propagation clusters is
.223, from the WUG correlation-clustering pipeline .754, from no clustering at all (APD) .751. Task 3's 1b forces a
clustering. So the question for 1b is not "form vs sense" but "which clustering recovers the distribution shifts".

Reading notes: tables were parsed from PDF text; I checked column order against the header rows (EN, LA, DE, SV, ES,
RU x3, NO x2, ZH, Avg_w). LA is the outlier everywhere (different benchmark construction). The GPT-4 comparison is EN only.
