# FreshMatch — Project report

**Problem.** Help a shopper retain a basket when an essential is unavailable by ranking plausible same-category alternatives.

**Data.** This verified run uses synthetic 288-product, 12-category data, 24,000 historical baskets and 3,000 final baskets. Instacart ingestion is supported. Prices and brands are simulated or estimated, never claimed as original retail truth.

**Method.** Apriori and FP-Growth mine complements. Substitutes use name/context similarity, low direct lift, category, price and popularity signals. Weak labels encode a heuristic. Both endpoints are product-disjoint across the supervised test split and each of three purged CV folds. Historical context remains transductive.

**Models.** RF and GB are proposed. LR, XGBoost, MLP and RF+GB+XGBoost soft voting are comparisons. Shared fold lists, brief tuning, sigmoid calibration and fold-local scaling support fair comparison. Training-CV PR-AUC selects Random Forest; reporting outcomes never select deployment. Numerically tied CV scores retain model order.

| Model | ROC-AUC | PR-AUC | F1 | Precision@5 | Recall@5 | NDCG@5 | MAP@5 | Training time (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Random Forest | 1.0000 | 1.0000 | 0.9928 | 0.1054 | 0.5269 | 0.3238 | 0.2577 | 3.4402 |
| Gradient Boosting | 0.9985 | 0.9949 | 0.9855 | 0.0989 | 0.4944 | 0.2920 | 0.2267 | 2.9571 |
| Logistic Regression | 1.0000 | 1.0000 | 1.0000 | 0.1212 | 0.6058 | 0.3778 | 0.3034 | 0.0981 |
| XGBoost | 0.9978 | 0.9935 | 0.9855 | 0.1093 | 0.5466 | 0.3280 | 0.2572 | 0.2734 |
| MLPClassifier | 1.0000 | 1.0000 | 1.0000 | 0.1090 | 0.5451 | 0.3436 | 0.2776 | 1.3460 |
| Soft Voting (RF + GB + XGB) | 1.0000 | 1.0000 | 0.9855 | 0.1066 | 0.5332 | 0.3260 | 0.2586 | 3.7266 |

**Behavioral evidence.** RF's future-switch hit rate is 52.7%, with household-bootstrap interval 51.0%–54.4%. Content hits 51.8% and popularity 32.2%. LR has better future ranking than deployed RF, and content beats RF on NDCG/MAP. High weak-label classification is not expert validation or causal sales evidence.

**Product.** The notebook writes and launches seven Streamlit pages. Ranked cards combine price differences, animated score rings, reasons and local feature-occlusion sensitivities. The simulator displays labelled demand/revenue scenarios, not observed recovery. Global permutation importance and local sensitivities describe model behavior without claiming causality.

**Validation and limitations.** All six pages render at desktop/375px. Automated checks verify product separation, metrics, score provenance and eligibility. Remaining gaps include real expert labels, ingredient/pack-size constraints, inventory capacity, fully inductive evaluation and prospective acceptance testing. See README and VALIDATION.

## Behavioral learning-to-rank extension

LambdaMART (`XGBRanker`, pairwise LambdaRank gradients for NDCG) learns observed switches from 15,545 historical query groups (357,535 candidate rows) belonging to 2,100 training households. The other households are assigned to validation (450) and testing (450); 477 validation and 474 test final-order switch events are available. Four depth/tree configurations are selected on validation NDCG@5, resulting in depth 2 and 80 trees. Final-order labels never train the ranker. Historical feature construction remains transductive.

On the held-out 474-event subset, LambdaMART records NDCG@5 0.4067 and hit rate 64.1%, versus weak-label suitability 0.3580 / 56.5%, content 0.3604 / 54.0%, shopping context 0.3596 / 60.3% and popularity 0.1819 / 30.4%. The paired NDCG difference versus weak labels is +0.0488, with 95% household-bootstrap interval [+0.0102, +0.0865]. This subset is separate from the original full final-order benchmark.

ML Lab presents the evaluation, interactive filtered ranking, category samples, validation-only feature removal and classifier reliability diagrams with ECE, Brier and log loss. Removing price/popularity features increases validation NDCG from 0.4078 to 0.4133; this descriptive result does not change the preselected full-feature model after test inspection. Relative rank scores are not probabilities. The main recommendation cards retain calibrated suitability scores.

Reproduce with `python scripts/train.py`; validate with `python -m unittest discover -s tests -v`. The notebook embeds the Python implementations; `scripts/sync_notebook.py` keeps them synchronized. A GitHub Actions workflow runs training and tests. Real-world effectiveness still requires real data and prospective evaluation.
