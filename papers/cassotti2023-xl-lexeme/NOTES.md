# cassotti2023-xl-lexeme — notes (maria, 2026-11-03)

Short paper, long shadow: by 2026 this is the default usage encoder of the whole LSC community, including the
SemEval-2027 Task 3 organisers (Cassotti is one of them). Practical facts a user needs and the paper does not give:
- Target marking is done at the TOKEN level by the WordTransformer library (tokenise left / "<t>" / target / "</t>" /
  right separately, then center-truncate to 128 tokens around the target). Passing a string with "<t>" inserted is
  not guaranteed to tokenise the same way.
- Pooling: paper says sum, released config says mean; same cosine.
- It does NOT separate subtle connotational senses well: on the SemEval-2027 SV dev set, no clustering threshold splits
  kvinna (individual vs generic woman) or forort (suburb vs immigrant-dense suburb) better than one cluster
  (arena-lsc Baseline error analysis). Those are exactly the senses Task 3 annotates.
