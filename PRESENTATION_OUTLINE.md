# FreshMatch — Six-slide presentation

1. **Problem and live demo:** unavailable essential → same-category alternatives, prices and explanation.
2. **Data and integrity:** synthetic 288 products / 27,000 baskets; history/final-order separation; explicit simulated prices and brands.
3. **Method:** complements from Apriori/FP-Growth; substitutes from shared context, names, low lift and price/popularity. Show README architecture.
4. **Fair comparison:** RF/GB proposed; four comparators; identical product-disjoint test/CV folds; purged boundary pairs; fold-local scaling and sigmoid calibration. Historical context remains transductive.
5. **Results and tradeoffs:** use assets/model-comparison.csv. RF wins CV selection; LR ranks future switches better. RF hit rate 52.7%, content 51.8%, popularity 32.2%. High classification scores learn heuristic labels; content still wins RF NDCG/MAP.
6. **Product and next steps:** six-page responsive app, local feature sensitivities, scenario recovery KPIs, reproducible notebook. Next: expert labels, ingredient/size constraints, inventory capacity and prospective acceptance testing. Do not claim causal recovered revenue.
