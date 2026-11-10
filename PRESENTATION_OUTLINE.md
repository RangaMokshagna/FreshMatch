# FreshMatch — Improved model presentation

1. **Problem:** suggest plausible grocery alternatives when a preferred item is unavailable. Explain suitability separately from ranking preference and purchase probability.
2. **Real data:** 320 selected products / 51 aisles from 3,000 development households; 49,760 historical baskets and 3,000 last-prior baskets. Prices and brand labels remain estimated/proxied.
3. **Reference models:** six classifiers; XGBoost supplies a separate suitability score. The small classifier test has only five positive labels, so do not overstate it.
4. **Improved learner:** directional LambdaMART uses candidate popularity, repeat purchases, switching preferences, names/context, relative price and suitability. Training transition encodings exclude the household being fitted.
5. **Hybrid selection:** four tree configurations and ten predefined blends compete on original validation NDCG only. Selected: depth 4 / 120 trees, 75% learned ranking + 25% popularity. Freeze before new-household evaluation.
6. **New holdout:** 5,000 previously unused households, disjoint from all development users; 4,594 qualifying examples from 1,888 households. Same fixed candidate pool for every method.
7. **Results:** hybrid NDCG@5 0.1344; popularity 0.1326; original ranker 0.1173. Hybrid has the highest measured primary score among compared methods and improves 14.6% over the old ranker. The small edge over popularity is not statistically conclusive: paired interval [-0.00042,+0.00421]. It does not win every metric.
8. **App and limits:** hybrid controls suggestion order; suitability remains separate. All 29 local tests pass and seven pages render. Candidate coverage remains 36.2%; expert substitute labels, actual prices/ingredients and prospective shopper acceptance remain future work.

The old 365-example test is retrospective reference evidence and had popularity ahead. Do not mix that population with the new 4,594-example holdout. Current slides and detailed evidence are in presentations/ and IMPROVEMENT_RESULTS.md.
