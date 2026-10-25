# FreshMatch — Project report

**Problem.** Help a shopper retain a basket when an essential is unavailable by ranking plausible same-category alternatives.

**Data.** This verified run uses synthetic 288-product, 12-category data, 24,000 historical baskets and 3,000 final baskets. Instacart ingestion is supported. Prices and brands are simulated or estimated, never claimed as original retail truth.

**Method.** Apriori and FP-Growth mine complements. Substitutes use name/context similarity, low direct lift, category, price and popularity signals. Weak labels encode a heuristic. Both endpoints are product-disjoint across the supervised test split and each of three purged CV folds. Historical context remains transductive.

**Models.** RF and GB are proposed. LR, XGBoost, MLP and RF+GB+XGBoost soft voting are comparisons. Shared fold lists, brief tuning, sigmoid calibration and fold-local scaling support fair comparison. Training-CV PR-AUC selects Random Forest; reporting outcomes never select deployment. Numerically tied CV scores retain model order.

| Model | ROC-AUC | PR-AUC | F1 | Precision@5 | Recall@5 | NDCG@5 | MAP@5 | Training time (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Random Forest | 1.0000 | 1.0000 | 0.9928 | 0.1054 | 0.5269 | 0.3238 | 0.2577 | 8.6515 |
| Gradient Boosting | 0.9985 | 0.9949 | 0.9855 | 0.0989 | 0.4944 | 0.2920 | 0.2267 | 6.3029 |
| Logistic Regression | 1.0000 | 1.0000 | 1.0000 | 0.1212 | 0.6058 | 0.3778 | 0.3034 | 0.1559 |
| XGBoost | 0.9977 | 0.9933 | 0.9855 | 0.1059 | 0.5297 | 0.3242 | 0.2576 | 2.2667 |
| MLPClassifier | 1.0000 | 1.0000 | 1.0000 | 0.1090 | 0.5451 | 0.3436 | 0.2776 | 4.0440 |
| Soft Voting (RF + GB + XGB) | 1.0000 | 1.0000 | 0.9855 | 0.1066 | 0.5332 | 0.3249 | 0.2570 | 7.9429 |

**Behavioral evidence.** RF's future-switch hit rate is 52.7%, with household-bootstrap interval 51.0%–54.4%. Content hits 51.8% and popularity 32.2%. LR has better future ranking than deployed RF, and content beats RF on NDCG/MAP. High weak-label classification is not expert validation or causal sales evidence.

**Product.** The notebook writes and launches six Streamlit pages. Ranked cards combine price differences, animated score rings, reasons and local feature-occlusion sensitivities. The simulator displays labelled demand/revenue scenarios, not observed recovery. Global permutation importance and local sensitivities describe model behavior without claiming causality.

**Validation and limitations.** All six pages render at desktop/375px. Automated checks verify product separation, metrics, score provenance and eligibility. Remaining gaps include real expert labels, ingredient/pack-size constraints, inventory capacity, fully inductive evaluation and prospective acceptance testing. See README and VALIDATION.
