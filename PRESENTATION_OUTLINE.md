# FreshMatch — Advanced ML presentation

1. **Problem and demo:** find alternatives for unavailable groceries; distinguish suitability, rank preference and acceptance probability.
2. **Data:** synthetic 288-product catalogue, 24,000 historical and 3,000 final baskets. Prices and brands are simulated; Instacart ingestion remains supported.
3. **Original ML:** Apriori/FP-Growth complements, context/name/price features, six tuned classifiers, product-disjoint folds and sigmoid calibration. Explain why heuristic labels can produce near-perfect classification.
4. **Behavioral LambdaMART:** learn observed historical switches with `rank:ndcg`. Show 15,545 query groups and 357,535 candidate rows; need IDs define synthetic relevance but never enter features.
5. **Experimental design:** 70/15/15 household split; historical transitions train; validation final orders select one of four configurations; test final orders report results. Historical features remain transductive.
6. **Measured ranking:** on 474 test events, NDCG@5 0.4067 versus weak-label 0.3580; hit rate 64.1% versus 56.5%. Compare content, context and popularity on identical candidate pools. Show paired household-bootstrap interval [+0.0102, +0.0865] for NDCG improvement.
7. **Diagnostics:** ML Lab category slices, validation-only ablations, gain importance and classifier reliability diagrams with Brier/log loss/ECE. Price/popularity removal slightly improves validation; do not change model selection after inspecting test results.
8. **Engineering and limitations:** synchronized notebook/Python sources, reproducible runner, 12 passing tests covering all seven pages, and a CI workflow. Synthetic proxy switching is not confirmed stockout acceptance; real data, ingredient/size constraints, fully inductive evaluation and prospective trials remain future work.
