# FreshMatch — speaker notes

## 1. FreshMatch

Introduce FreshMatch as an explainable grocery substitution workbench. The current demonstration uses real Instacart product and purchase records. Our experiment selects 320 products and 3,000 households; this is a bounded research sample, not the full retail universe. Prices are estimates and brand strings are name-token proxies. The screenshots in this presentation were freshly captured from the real-data app.

## 2. A missing item should not end the basket

Example: a shopper wants organic milk and their preferred item is unavailable. We suggest same-aisle candidates, show an estimated price difference, and explain suitability. Products bought together are often complements, not replacements, so co-purchase alone is not our substitute rule. We do not promise nutritional equivalence, dietary safety or actual sales recovery.

## 3. Real Instacart records, with a clear study sample

The source has 49,688 products across 134 aisles. We sample whole households, then select 320 products by historical purchase frequency. Each household’s last available prior order is held out; earlier prior orders form history. The experiment uses 49,760 historical baskets and 3,000 final baskets from 3,000 households. Source hashes are recorded. These are not Kaggle’s hidden competition test labels. Instacart does not contain observed prices or verified brands.

## 4. From basket history to an explained recommendation

Data validation checks schemas, identifiers, references and LFS content. Historical baskets feed Apriori and FP-Growth complement mining and pair-feature construction. Weak heuristic labels train suitability models; an independent behavioral ranking experiment learns historical switching. Eligibility, price and availability filters are applied when serving candidates. The notebook writes portable inference artifacts consumed by Streamlit. Historical features remain shared across households, so evaluation is transductive.

## 5. Two learning tasks: suitability and behavior

The six classifiers are Random Forest, Gradient Boosting, Logistic Regression, XGBoost, MLPClassifier and RF/GB/XGB soft voting. Training-CV average precision chooses XGBoost for the main app; sigmoid calibration maps outputs to weak-label frequencies, not acceptance probabilities. LambdaMART uses XGBRanker with rank:ndcg on historical switches. Four configurations compete on validation NDCG@5; depth 2 and 160 trees are selected. No test scores choose either deployed classifier or ranker configuration.

## 6. Train, choose and test on separate groups

Classifier partitions are product-disjoint at both endpoints and purge crossing pairs. Seeded category-balanced assignments use label counts only to guarantee at least five examples of each class per retained partition. The outer test has 266 pairs but only five positive weak labels, so classification scores are fragile. Behavioral households split 70/15/15: 2,100 train, 450 validation, 450 reserved test. There are 384 validation and 365 test switching events; only 163 reserved test households generate qualifying events. Historical features use all households: transductive rather than fully inductive evaluation.

## 7. Find a swap, then test a stockout scenario

The screenshots are actual captures of the current real-data app. Find Substitutes searches Organic Milk, ranks eligible alternatives and shows model sensitivities, estimated price differences and exports. Out-of-Stock Simulator excludes multiple products and uses an explicitly chosen acceptance assumption to estimate units/revenue; it is not observed recovery. Product Explorer, shown on the data slide, adds category and purchase-frequency views. Main-card scores are suitability, not purchase probabilities.

## 8. Show the relationship—and the evidence behind it

Relationship Explorer separates complements (frequently purchased together) from predicted eligible alternatives. Main-card occlusion sensitivities compare one feature with its training median; they are not additive or causal explanations. Model Performance compares six models, ROC/PR, confusion matrices, permutation importance and future ranking baselines. These screenshots are genuine real-data app captures. ML Lab is shown on the next slide. About records the method, team and limitations.

## 9. The ranker improves on suitability; popularity still leads

All five methods below use the same 365 held-out switching events and eligible candidate pools. NDCG@5 rewards placing observed relevant products nearer the top; higher is better. Behavioral LambdaMART is 0.1294 and the weak-label classifier is 0.0647. Their paired household-bootstrap difference is +0.0647 with 95% interval [+0.0437,+0.0859]. Popularity is higher at 0.1409, so we do not claim the learned ranker is best. Only 36.7% of events have any relevant target inside eligibility; excluded targets remain in metric denominators. These are proxy switches, not confirmed substitutions or causal recovered sales.

## 10. A working research project, with clear next steps

Conclude with evidence rather than an inflated success claim. All 23 local tests pass, covering all seven app pages plus splits, input data, scores and uncertainty. The project is reproducible and uses real purchase records. The next experiment should address candidate eligibility/coverage; additional expert substitute labels, observed price/pack-size/ingredient information and prospective acceptance testing are needed. Brand tokens and estimated prices are not verified retail data. The About page makes those boundaries visible. Invite questions.

