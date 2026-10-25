# FreshMatch · Measured results
Data: **Synthetic grocery simulation**. 288 products; 24,000 history baskets; 3,000 future baskets.
Selected model: **Random Forest**, chosen by training cross-validation.

## Six-model comparison · identical pair split, CV folds and next-order events
Proposed methods: **Random Forest and Gradient Boosting**. Comparison methods: Logistic Regression, XGBoost, MLPClassifier and soft voting (RF + GB + XGBoost).

| Model | Role | Deployed | ROC-AUC | PR-AUC | F1 | Precision@5 | Recall@5 | NDCG@5 | MAP@5 | Training time (s) | CV PR-AUC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Random Forest | Proposed | True | 1.0 | 1.0 | 0.9928 | 0.1054 | 0.5269 | 0.3238 | 0.2577 | 8.6515 | 1.0 |
| Gradient Boosting | Proposed | False | 0.9985 | 0.9949 | 0.9855 | 0.0989 | 0.4944 | 0.292 | 0.2267 | 6.3029 | 0.9998 |
| Logistic Regression | Comparison | False | 1.0 | 1.0 | 1.0 | 0.1212 | 0.6058 | 0.3778 | 0.3034 | 0.1559 | 1.0 |
| XGBoost | Comparison | False | 0.9977 | 0.9933 | 0.9855 | 0.1059 | 0.5297 | 0.3242 | 0.2576 | 2.2667 | 1.0 |
| MLPClassifier | Comparison | False | 1.0 | 1.0 | 1.0 | 0.109 | 0.5451 | 0.3436 | 0.2776 | 4.044 | 0.9997 |
| Soft Voting (RF + GB + XGB) | Comparison | False | 1.0 | 1.0 | 0.9855 | 0.1066 | 0.5332 | 0.3249 | 0.257 | 7.9429 | 1.0 |

The deployed row is selected by **training CV PR-AUC**, not by these held-out outcomes. The notebook and Model Performance page share this exact table and a single bar chart with a metric dropdown (including training seconds on their own scale).
Training time includes grid search, refit and calibration; voting time includes component fits. LR/MLP scaling is fitted within each training fold. Exact CV ties retain the declared model order.


## Held-out next-order ranking (K=5)
| model | precision_at_k | recall_at_k | ndcg_at_k | map_at_k | hit_rate | hit_ci_low | hit_ci_high | target_coverage | events | revenue_saved |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FreshMatch | 0.1054 | 0.5269 | 0.3238 | 0.2577 | 0.5269 | 0.5102 | 0.5442 | 1.0 | 3194 | 6859.76 |
| Popular in category | 0.0643 | 0.3215 | 0.1957 | 0.1547 | 0.3215 | 0.3055 | 0.3356 | 1.0 | 3194 | 3522.38 |
| Content similarity | 0.1035 | 0.5175 | 0.3418 | 0.2841 | 0.5175 | 0.5012 | 0.5358 | 1.0 | 3194 | 6825.53 |

Classification PR-AUC is average precision. MAP is truncated at 5 and divided by all relevant targets.
Top-5 hit rate has a household-bootstrap 95% interval of 51.0%–54.4%.
Runtime before app launch: 21.0 seconds (excludes package installation; fitted-model cache hit: True). The training-time column retains original search/refit/calibration measurements when models are cached.

Novelty: complementary-item rules are separated from substitution signals; context similarity measures shared shopping roles;
low direct lift suppresses co-purchased products; six calibrated model families share one split/CV protocol and are compared with content and popularity;
the benchmark uses future behavior independent of weak labels; multi-item stockouts remove unavailable candidates.

Limitations: synthetic/estimated prices, heuristic labels, product-disjoint supervised split with transductive historical context, and a conditional observational
switch benchmark. Results are not causal sales recovery evidence. A simpler baseline can outperform the ensemble;
the tables report measured outcomes without hiding that possibility.
