# kokosinskii2024-deep-change-axolotl — notes (maria, 2026-11-03)

What to take: (1) the GlossReader architecture in implementable detail (context = mean of target subword outputs of
the last layer, no markers; gloss = <s> output of a separate encoder; dot product); (2) novel-sense detection framed as
outlier detection on usage-gloss distances, with a small logistic regression - a pattern directly reusable for
SemEval-2027 Task 3 Subtask 2, which is "is this usage an instance of THIS gloss?"; (3) the metric pathology of
AXOLOTL F1, which the authors explain precisely.
Practical: target positions for Russian were found with pymorphy2 word forms + manual fixes; reusing AXOLOTL RU needs
the same, or a crude locator like arena-lsc's (3,716 recovered, 185 lost).
