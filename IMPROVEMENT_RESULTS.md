# FreshMatch hybrid improvement — reproducible evidence

The improvement adds directional candidate popularity, candidate/query reorder signals, relative price and empirical-Bayes historical switching preferences. Transition evidence is calculated from **training households only**. Training uses three household-cross-fitted encodings so a household never contributes the target outcomes that encode its own training rows. Existing catalogue features remain transductive within the original development sample.

## Pre-test selection

Four directional LambdaMART configurations were compared on the original 384 validation events. Depth 4 / 120 trees won. Ten predefined blends used within-query percentile ranks with ties preserved. The selected weights were 0.75 learned ranking / 0.25 popularity / 0 direct transition blend; transition evidence remains an input to the learned model. This configuration scored 0.13565 validation NDCG@5 versus popularity's 0.12913 and passed the validation-only deployment gate.

No test metric chooses a configuration. `hybrid_selection.json` is written before old test evaluation; its hash is recorded in `hybrid_report.json`. The retrospective 365-example test scored 0.14039 for the hybrid versus popularity 0.14089 and original LambdaMART 0.12936. Those outcomes had been inspected previously, so they are not presented as fresh evidence.

## Frozen new-household evaluation

Before reading new evaluation households, `fresh_holdout_protocol.json` froze all inference file hashes, seed 20261110, 5,000 sampled households, the excluded development household IDs, a primary NDCG@5 metric and the unchanged candidate policy. These 5,000 households do not overlap any of the 3,000 used previously. Only their last two available prior orders construct evaluation events; none of their histories fit catalogue features, transition evidence, models or blend weights.

The new evaluation contains 4,594 events from 1,888 qualifying households. This is an unused-household holdout within the same public Instacart dataset, not a prospective retail experiment or a different external dataset.

| Method | NDCG@5 | Recall@5 | Hit rate | Coverage |
| --- | ---: | ---: | ---: | ---: |
| FreshMatch Hybrid | 0.134397 | 0.162724 | 0.253374 | 0.361994 |
| Popularity | 0.132627 | 0.161936 | 0.252939 | 0.361994 |
| Content similarity | 0.078441 | 0.104800 | 0.167175 | 0.361994 |
| Shopping context | 0.099683 | 0.132987 | 0.215716 | 0.361994 |
| Weak-label classifier | 0.067070 | 0.086982 | 0.139747 | 0.361994 |
| Original LambdaMART | 0.117266 | 0.145298 | 0.230518 | 0.361994 |
| Directional LambdaMART | 0.134328 | 0.163341 | 0.253809 | 0.361994 |

## Interpretation

Hybrid NDCG@5 is 14.6% higher than the original ranker on the same examples. The paired difference vs the original ranker is +0.01713, 95% household-bootstrap interval [+0.01285, +0.02157]. The difference vs popularity is +0.00177 with interval [-0.00042, +0.00421]. The point estimate leads the compared methods on the declared primary metric, but the interval does **not** establish superiority over popularity. Popularity has slightly higher precision and the directional-only component has slightly higher recall/hit rate. Do not describe this as best on all metrics or guaranteed best in production.

Candidate eligibility remains exactly the original same-aisle/low-lift rule for every method; ineligible targets remain in recall/NDCG denominators. Coverage is only 36.2%, a material limitation. No candidate rules were adjusted after looking at fresh results. Prices remain estimates, brands are proxies, and switching is not substitution ground truth.

## Reproduce and serve

- `python scripts/train.py --data-source instacart`: base training plus original and improved ranking experiments.
- `python scripts/improve.py`: refit the improved experiment from matching existing real-data base artifacts. CSV hashes and catalogue IDs must match.
- `python scripts/verify_fresh_holdout.py`: verify the published frozen checkpoint against its fixed new-household sample. Changed checkpoint hashes are rejected; this is deliberate protection against test reuse.
- `python -m unittest discover -s tests -v`: checks including encodings, frozen splits, independent metrics/interval recomputation and app order.

The app activates only a validation-approved hybrid whose product/matrix fingerprints match the loaded base data. Main-card suitability remains the separate XGBoost weak-label score; ranking order and exported ranking score come from the hybrid. Model Performance and ML Lab show current new-household results first, retain labelled legacy experiments, and state uncertainty. Simulator acceptance remains a user assumption; its initial reference rate is explicitly labelled as the legacy classifier benchmark.

Portable scores and audit tables are tracked. Fitted model binaries stay local. Old presentations were generated before this change; their results must be updated rather than mixing old and new evaluation populations.
