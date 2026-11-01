# FreshMatch — Real-data project report

**Current source: real Instacart purchase records**, downloaded from the user's Git LFS commit `2fed8b5`. All five required files passed schema checks and SHA-256 verification against their LFS object IDs. The catalogue contains 49,688 products; the experiment samples 3,000 eligible households and selects 320 products across 51 aisles using historical frequency only. There are 49,760 historical and 3,000 held-out final available prior orders.

## Models and supervised protocol

Apriori/FP-Growth mine complements from identical history. Ten pair features describe category/aisle/department, name-token brand proxies, names, shopping contexts, lift, estimated price ratio, popularity ratio and reorder similarity. Weak labels are a heuristic, not expert substitute annotation. Eligible alternatives share category and have lift below 1.5; query/outage exclusions are enforced.

The original category-local round-robin fold assignment left a real-data validation fold without positive labels. The replacement uses deterministic category-balanced product assignments, accepting only splits with at least five labels of each class in each retained outer/CV partition. It uses label counts only, before fitting any model. All cross-boundary pairs are purged and both endpoints are disjoint. Exact fold indices enter model-cache identity. The audit is preserved in the manifest.

The outer split retains 2036 training and 266 test pairs; 1532 boundary pairs are purged. The test has **261 negative and only five positive** weak labels: classification estimates are fragile. CV is not nested and historical feature construction is transductive.

| Model | Role | Deployed | ROC-AUC | PR-AUC | F1 | Precision@5 | Recall@5 | NDCG@5 | MAP@5 | Training time (s) | CV PR-AUC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Random Forest | Proposed | False | 0.9762 | 0.6736 | 0.8000 | 0.0301 | 0.0880 | 0.0658 | 0.0476 | 2.8973 | 0.8457 |
| Gradient Boosting | Proposed | False | 0.9900 | 0.8188 | 0.6667 | 0.0300 | 0.0856 | 0.0657 | 0.0481 | 2.2424 | 0.7991 |
| Logistic Regression | Comparison | False | 0.9854 | 0.6514 | 0.5455 | 0.0343 | 0.0987 | 0.0756 | 0.0561 | 0.0941 | 0.7443 |
| XGBoost | Comparison | True | 0.9908 | 0.8225 | 0.6667 | 0.0299 | 0.0865 | 0.0668 | 0.0493 | 0.2274 | 0.9083 |
| MLPClassifier | Comparison | False | 0.4912 | 0.0307 | 0.0000 | 0.0351 | 0.0983 | 0.0721 | 0.0520 | 0.7169 | 0.3214 |
| Soft Voting (RF + GB + XGB) | Comparison | False | 0.9801 | 0.7933 | 0.6667 | 0.0299 | 0.0876 | 0.0658 | 0.0478 | 3.7317 | 0.9054 |

**Deployed suitability model: XGBoost**, selected by training CV PR-AUC. These classification scores are not acceptance probabilities. All six share product-disjoint folds, with scaling and sigmoid calibration contained in fitting. Main-card explanations use non-additive feature-occlusion sensitivity; gain/permutation importance is not causal.

## Behavioral learning-to-rank

LambdaMART learns historical adjacent-order switches from 2,100 training households: 28,383 observed historical switch events yield 8,840 informative candidate groups and 147,340 rows. Groups without an eligible positive or without a preference ordering cannot train the ranker. Validation uses 384 final-order events from a separate 450-household allocation. Four configurations compete on validation NDCG@5; depth 2 / 160 trees is fixed before test reporting.

The test contains 365 final-order switch events from 163 of 450 reserved households. Historical catalogue features remain shared across households, so this is not a fully inductive test. Real relevance is observed next-order same-aisle purchasing, broader than the old synthetic hidden-need label.

| model | ndcg_at_k | recall_at_k | hit_rate | target_coverage | ndcg_ci_low | ndcg_ci_high |
| --- | --- | --- | --- | --- | --- | --- |
| Behavioral LambdaMART | 0.1294 | 0.1580 | 0.2438 | 0.3671 | 0.1030 | 0.1547 |
| Weak-label classifier | 0.0647 | 0.0867 | 0.1397 | 0.3671 | 0.0463 | 0.0854 |
| Content similarity | 0.0883 | 0.1118 | 0.1918 | 0.3671 | 0.0677 | 0.1104 |
| Shopping context | 0.1019 | 0.1351 | 0.2219 | 0.3671 | 0.0808 | 0.1255 |
| Popularity | 0.1409 | 0.1636 | 0.2740 | 0.3671 | 0.1135 | 0.1682 |

The paired NDCG difference versus the weak-label model is +0.0647, 95% household-bootstrap interval [+0.0437, +0.0859]. **Popularity outperforms the behavioral model on this test.** No model was changed after inspecting that result. Only 36.7% of events have a relevant target surviving eligibility; test metrics retain excluded targets in denominators. These events differ from the full 2,540-event weak-label benchmark.

## Product and evidence

All seven app pages use the regenerated real-data artifacts. ML Lab presents candidate comparisons, category counts, validation-only ablations, gain importance and weak-label reliability diagrams (Brier/log loss/ECE). Full notebook execution passed using retained ingestion/mining caches; the exact pinned Python 3.12 environment passed 23 tests. See VALIDATION.md. New real-data browser viewport inspection and remote real-data CI are not claimed.

Instacart has no observed prices, verified brands, stockout labels, ingredient equivalence or confirmed substitution outcomes. Prices remain deterministic estimates and brand names are token proxies. Revenue remains a labelled scenario, not causal recovered sales. Better candidate coverage, expert labels, fully inductive features and prospective shopper evaluation remain future work. Previous synthetic results are historical demonstrations, not current measurements.
