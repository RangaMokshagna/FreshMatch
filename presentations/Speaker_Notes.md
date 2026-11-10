# FreshMatch — speaker notes

## 1. FreshMatch

Introduce FreshMatch as an explainable grocery substitution workbench. The current demonstration uses real Instacart product and purchase records. Our experiment selects 320 products and 3,000 households; this is a bounded research sample, not the full retail universe. Prices are estimates and brand strings are name-token proxies. The screenshots in this presentation were freshly captured from the real-data app.

## 2. A missing item should not end the basket

Example: a shopper wants organic milk and their preferred item is unavailable. We suggest same-aisle candidates, show an estimated price difference, and explain suitability. Products bought together are often complements, not replacements, so co-purchase alone is not our substitute rule. We do not promise nutritional equivalence, dietary safety or actual sales recovery.

## 3. Real Instacart records, with a clear study sample

The source has 49,688 products across 134 aisles. We sample whole households, then select 320 products by historical purchase frequency. Each household’s last available prior order is held out; earlier prior orders form history. The experiment uses 49,760 historical baskets and 3,000 final baskets from 3,000 households. Source hashes are recorded. These are not Kaggle’s hidden competition test labels. Instacart does not contain observed prices or verified brands.

## 4. From basket history to an explained recommendation

Data validation checks schemas, identifiers, references and LFS content. Historical baskets feed Apriori and FP-Growth complement mining and pair-feature construction. Weak heuristic labels train suitability models; an independent behavioral ranking experiment learns historical switching. Eligibility, price and availability filters are applied when serving candidates. The notebook writes portable inference artifacts consumed by Streamlit. Historical features remain shared across households, so evaluation is transductive.

## 5. FreshMatch combines learned ranking with popularity

The new directional LambdaMART adds absolute candidate popularity, reorder rates, historical switching preferences, relative prices and original XGBoost suitability. Three household-cross-fitted encodings exclude each fitted household from its own transition-evidence features. Four configurations compete on the original validation events; depth 4 with 120 trees wins. Ten predefined rank blends are selected on validation NDCG only. The winner is 75% learned ranking and 25% popularity; direct transition blend weight is zero, but transition preferences remain a model input. Reference suitability classifiers are Random Forest, Gradient Boosting, Logistic Regression, XGBoost, MLP and soft voting. XGBoost supplies the separate displayed suitability score. The original classifier test has only five positive labels, so its scores remain a limited supplementary signal.

## 6. Freeze the model before checking new households

Model fitting uses the original training households and validation tuning uses 384 events. The old 365-event test had already been inspected, so it is now labelled retrospective development evidence. After selection, the protocol froze the score-file hashes, weights, primary NDCG@5 metric, unchanged candidate rule, random seed and 5,000 new households before reading their outcomes. Those households do not overlap any of the 3,000 development households. Their last two available prior orders yield 4,594 switching examples from 1,888 households. None of these new customers histories fit features, transitions, models or weights. This is a new-household holdout within the same public dataset, not a prospective external retail study.

## 7. Find a swap, then test a stockout scenario

The screenshots are actual captures of the current real-data hybrid app. Find Substitutes searches Organic Milk, ranks eligible alternatives and shows model sensitivities, estimated price differences and exports. Out-of-Stock Simulator excludes multiple products and uses an explicitly chosen acceptance assumption to estimate units/revenue; it is not observed recovery. Product Explorer, shown on the data slide, adds category and purchase-frequency views. Main cards are ordered by FreshMatch Hybrid. Their displayed suitability scores remain a separate XGBoost signal, not purchase probabilities.

## 8. Show the relationship—and the evidence behind it

Relationship Explorer separates complements (frequently purchased together) from predicted eligible alternatives. Main-card occlusion sensitivities compare one feature with its training median; they are not additive or causal explanations. Model Performance compares six models, ROC/PR, confusion matrices, permutation importance and future ranking baselines. These screenshots are genuine real-data app captures. ML Lab is shown on the next slide. About records the method, team and limitations.

## 9. Highest measured ranking quality, with a small edge

The validation-selected FreshMatch Hybrid scores NDCG@5 0.134397 on 4,594 new-household events; popularity scores 0.132627 and the original LambdaMART 0.117266. This is 14.6% relative improvement over the old ranker on the same examples. The paired hybrid-minus-original interval is [+0.01285,+0.02157]. The hybrid-minus-popularity difference is +0.00177 with 95% household-bootstrap interval [-0.00042,+0.00421], which includes zero: do not claim statistically established superiority over popularity. Hybrid has the highest observed primary NDCG score among the compared methods, but does not win every metric. Candidate coverage remains 36.2%, with ineligible targets retained in denominators. No model or weight was changed after the fresh holdout was inspected.

## 10. A stronger model, with honest evidence

Conclude with evidence rather than an inflated success claim. All 29 local tests pass, covering all seven app pages plus splits, input data, scores and uncertainty. The project now serves the validation-approved hybrid and separately displays original suitability scores. It leads on observed NDCG in a fixed new-household test, with uncertainty vs popularity explicitly reported. The next experiment should address candidate eligibility/coverage; additional expert substitute labels, observed price/pack-size/ingredient information and prospective acceptance testing are needed. Brand tokens and estimated prices are not verified retail data. The About page makes those boundaries visible. Invite questions.
