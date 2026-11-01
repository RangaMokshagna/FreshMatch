# FreshMatch · Measured results
Data: **Instacart**. 320 products; 49,760 history baskets; 3,000 future baskets.
Selected model: **XGBoost**, chosen by training cross-validation.

## Six-model comparison · identical pair split, CV folds and next-order events
Proposed methods: **Random Forest and Gradient Boosting**. Comparison methods: Logistic Regression, XGBoost, MLPClassifier and soft voting (RF + GB + XGBoost).

| Model | Role | Deployed | ROC-AUC | PR-AUC | F1 | Precision@5 | Recall@5 | NDCG@5 | MAP@5 | Training time (s) | CV PR-AUC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Random Forest | Proposed | False | 0.9762 | 0.6736 | 0.8 | 0.0301 | 0.088 | 0.0658 | 0.0476 | 2.8973 | 0.8457 |
| Gradient Boosting | Proposed | False | 0.99 | 0.8188 | 0.6667 | 0.03 | 0.0856 | 0.0657 | 0.0481 | 2.2424 | 0.7991 |
| Logistic Regression | Comparison | False | 0.9854 | 0.6514 | 0.5455 | 0.0343 | 0.0987 | 0.0756 | 0.0561 | 0.0941 | 0.7443 |
| XGBoost | Comparison | True | 0.9908 | 0.8225 | 0.6667 | 0.0299 | 0.0865 | 0.0668 | 0.0493 | 0.2274 | 0.9083 |
| MLPClassifier | Comparison | False | 0.4912 | 0.0307 | 0.0 | 0.0351 | 0.0983 | 0.0721 | 0.052 | 0.7169 | 0.3214 |
| Soft Voting (RF + GB + XGB) | Comparison | False | 0.9801 | 0.7933 | 0.6667 | 0.0299 | 0.0876 | 0.0658 | 0.0478 | 3.7317 | 0.9054 |

The deployed row is selected by **training CV PR-AUC**, not by these held-out outcomes. The notebook and Model Performance page share this exact table and a single bar chart with a metric dropdown (including training seconds on their own scale).
Training time includes grid search, refit and calibration; voting time includes component fits. LR/MLP scaling is fitted within each training fold. Exact CV ties retain the declared model order.


## Held-out next-order ranking (K=5)
| model | precision_at_k | recall_at_k | ndcg_at_k | map_at_k | hit_rate | hit_ci_low | hit_ci_high | target_coverage | events | revenue_saved |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FreshMatch | 0.0299 | 0.0865 | 0.0668 | 0.0493 | 0.1441 | 0.1299 | 0.1583 | 0.3559 | 2540 | 1474.03 |
| Popular in category | 0.0584 | 0.1566 | 0.1316 | 0.1023 | 0.2508 | 0.2334 | 0.268 | 0.3559 | 2540 | 2323.8 |
| Content similarity | 0.0379 | 0.106 | 0.0796 | 0.0581 | 0.1732 | 0.1587 | 0.1864 | 0.3559 | 2540 | 1786.65 |

Classification PR-AUC is average precision. MAP is truncated at 5 and divided by all relevant targets.
Top-5 hit rate has a household-bootstrap 95% interval of 13.0%–15.8%.
Runtime before app launch: 17.1 seconds (excludes package installation; fitted-model cache hit: False). The training-time column retains original search/refit/calibration measurements when models are cached.

Novelty: complementary-item rules are separated from substitution signals; context similarity measures shared shopping roles;
low direct lift suppresses co-purchased products; six calibrated model families share one split/CV protocol and are compared with content and popularity;
the benchmark uses future behavior independent of weak labels; multi-item stockouts remove unavailable candidates.

Limitations: synthetic/estimated prices, heuristic labels, product-disjoint supervised split with transductive historical context, and a conditional observational
switch benchmark. Results are not causal sales recovery evidence. A simpler baseline can outperform the ensemble;
the tables report measured outcomes without hiding that possibility.


## Behavioral LambdaMART · held-out households
| model | precision_at_k | recall_at_k | ndcg_at_k | map_at_k | hit_rate | target_coverage | ndcg_ci_low | ndcg_ci_high | events | households |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Behavioral LambdaMART | 0.0564 | 0.158 | 0.1294 | 0.1008 | 0.2438 | 0.3671 | 0.103 | 0.1547 | 365 | 163 |
| Weak-label classifier | 0.029 | 0.0867 | 0.0647 | 0.0482 | 0.1397 | 0.3671 | 0.0463 | 0.0854 | 365 | 163 |
| Content similarity | 0.0416 | 0.1118 | 0.0883 | 0.0651 | 0.1918 | 0.3671 | 0.0677 | 0.1104 | 365 | 163 |
| Shopping context | 0.0482 | 0.1351 | 0.1019 | 0.0748 | 0.2219 | 0.3671 | 0.0808 | 0.1255 | 365 | 163 |
| Popularity | 0.063 | 0.1636 | 0.1409 | 0.1103 | 0.274 | 0.3671 | 0.1135 | 0.1682 | 365 | 163 |

Selection: validation-household final-order NDCG@5. Historical features remain transductive.
Paired NDCG@5 difference vs weak-label classifier: +0.0647; 95% household-bootstrap interval [+0.0437, +0.0859].
