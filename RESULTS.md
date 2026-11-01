# FreshMatch · Measured results
Data: **Synthetic grocery simulation**. 288 products; 24,000 history baskets; 3,000 future baskets.
Selected model: **Random Forest**, chosen by training cross-validation.

## Six-model comparison · identical pair split, CV folds and next-order events
Proposed methods: **Random Forest and Gradient Boosting**. Comparison methods: Logistic Regression, XGBoost, MLPClassifier and soft voting (RF + GB + XGBoost).

| Model | Role | Deployed | ROC-AUC | PR-AUC | F1 | Precision@5 | Recall@5 | NDCG@5 | MAP@5 | Training time (s) | CV PR-AUC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Random Forest | Proposed | True | 1.0 | 1.0 | 0.9928 | 0.1054 | 0.5269 | 0.3238 | 0.2577 | 3.4402 | 1.0 |
| Gradient Boosting | Proposed | False | 0.9985 | 0.9949 | 0.9855 | 0.0989 | 0.4944 | 0.292 | 0.2267 | 2.9571 | 0.9998 |
| Logistic Regression | Comparison | False | 1.0 | 1.0 | 1.0 | 0.1212 | 0.6058 | 0.3778 | 0.3034 | 0.0981 | 1.0 |
| XGBoost | Comparison | False | 0.9978 | 0.9935 | 0.9855 | 0.1093 | 0.5466 | 0.328 | 0.2572 | 0.2734 | 1.0 |
| MLPClassifier | Comparison | False | 1.0 | 1.0 | 1.0 | 0.109 | 0.5451 | 0.3436 | 0.2776 | 1.346 | 0.9997 |
| Soft Voting (RF + GB + XGB) | Comparison | False | 1.0 | 1.0 | 0.9855 | 0.1066 | 0.5332 | 0.326 | 0.2586 | 3.7266 | 1.0 |

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
Runtime before app launch: 7.3 seconds (excludes package installation; fitted-model cache hit: True). The training-time column retains original search/refit/calibration measurements when models are cached.

Novelty: complementary-item rules are separated from substitution signals; context similarity measures shared shopping roles;
low direct lift suppresses co-purchased products; six calibrated model families share one split/CV protocol and are compared with content and popularity;
the benchmark uses future behavior independent of weak labels; multi-item stockouts remove unavailable candidates.

Limitations: synthetic/estimated prices, heuristic labels, product-disjoint supervised split with transductive historical context, and a conditional observational
switch benchmark. Results are not causal sales recovery evidence. A simpler baseline can outperform the ensemble;
the tables report measured outcomes without hiding that possibility.


## Behavioral LambdaMART · held-out households
| model | precision_at_k | recall_at_k | ndcg_at_k | map_at_k | hit_rate | target_coverage | ndcg_ci_low | ndcg_ci_high | events | households |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Behavioral LambdaMART | 0.1283 | 0.6414 | 0.4067 | 0.3297 | 0.6414 | 1.0 | 0.3749 | 0.4394 | 474 | 278 |
| Weak-label classifier | 0.1131 | 0.5654 | 0.358 | 0.2908 | 0.5654 | 1.0 | 0.3282 | 0.3893 | 474 | 278 |
| Content similarity | 0.108 | 0.5401 | 0.3604 | 0.3015 | 0.5401 | 1.0 | 0.3288 | 0.3947 | 474 | 278 |
| Shopping context | 0.1207 | 0.6034 | 0.3596 | 0.2802 | 0.6034 | 1.0 | 0.3293 | 0.392 | 474 | 278 |
| Popularity | 0.0608 | 0.3038 | 0.1819 | 0.1421 | 0.3038 | 1.0 | 0.1561 | 0.2085 | 474 | 278 |

Selection: validation-household final-order NDCG@5. Historical features remain transductive.
Paired NDCG@5 difference vs weak-label classifier: +0.0488; 95% household-bootstrap interval [+0.0102, +0.0865].
