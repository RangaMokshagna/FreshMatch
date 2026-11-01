# FreshMatch — Real-data ML presentation

1. **Problem and live demo:** unavailable groceries → filtered alternatives. Distinguish heuristic suitability, relative ranking scores and acceptance probabilities.
2. **Real dataset:** Git-LFS-backed Instacart CSVs; 49,688 products in source, 320 selected products / 51 aisles, 3,000 sampled households, 49,760 history baskets and 3,000 held-out last prior orders. Prices/brands remain estimated/proxied.
3. **Method:** complements from Apriori and FP-Growth; pair suitability from names, contexts, lift, category and estimated price/popularity/reorder signals. No stockout or expert substitution labels are claimed.
4. **Classifier protocol:** six tuned/calibrated models, product-disjoint outer/CV partitions, purged boundary pairs and minimum class support. XGBoost wins training-CV selection. Test has only five positive weak labels; explain the uncertainty.
5. **Behavioral ranker:** LambdaMART trained on 8,840 historical candidate groups / 147,340 rows from 2,100 households. Four configurations selected on 384 validation events; 365 test events from disjoint households. Historical features remain transductive.
6. **Real results:** NDCG@5: behavioral 0.1294, weak-label 0.0647, content 0.0883, context 0.1019, popularity 0.1409. Behavioral improvement vs weak labels has paired 95% interval [+0.0437,+0.0859], but popularity is stronger. Only 36.7% target coverage.
7. **Diagnostics and engineering:** ML Lab, category slices, validation ablations, calibration and explanations. Source-synchronized notebook, provenance hashes, exact CV cache identity and 23 local passing tests covering all seven app pages.
8. **Limitations and next work:** improve candidate coverage, acquire expert labels/real price and ingredient data, fit fully inductive features and run prospective acceptance evaluation. Do not compare old synthetic scores directly with the real-data experiment or claim causal recovered revenue.
