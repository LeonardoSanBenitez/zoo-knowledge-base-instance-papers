# schlechtweg2021-dwug — notes (maria, 2026-11-03)

Read as the source of most public "sense" gold in LSC. The key fact for evaluation: DWUG senses are correlation-
clustering clusters of a sparse human proximity graph, not dictionary senses. Three consequences seen today in
arena-lsc: (1) random labels with the gold k score very high 1b on DWUG (0.62-0.89), because each word has one period
pair and k varies a lot across words; (2) DWUG k and dictionary sense counts are different quantities - a model tuned on
DWUG granularity need not match a dictionary-sense benchmark such as SemEval-2027 Task 3; (3) the WUG pipeline is
itself the clustering a model is compared to, which favours systems that imitate it.
The Swedish OCR noise noted here reappears in the SemEval-2027 SV dev data (1880-1915 Kubhist-like text).
