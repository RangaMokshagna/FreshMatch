# FreshMatch — Validation

## Real-data transition · pending official inputs

Real-data training now defaults to Instacart and fails before notebook execution when the five required CSVs are missing. The current local suite passes 20 tests, including eight ingestion/archive/CLI tests and the seven-page app test. Test fixtures are small fabricated CSVs, not real-data performance evidence. Input/schema checks, streaming ingestion, history-only catalogue selection, all-file content fingerprints and nested ZIP extraction are covered by fabricated **test fixtures**, not presented as real training records. No official Instacart files have been supplied here, so end-to-end real-data training and real model performance remain unverified. Previous results below are synthetic and have not been relabelled as real.

## Advanced extension · previous synthetic validation

Validated in an isolated Python 3.12.14 virtual environment with the exact pinned dependencies. `python scripts/train.py` completed all notebook cells, generated behavioral ranking artifacts and passed the original notebook integrity assertions. `python -m pip check` reported no broken requirements.

`python -m unittest discover -s tests -v`: **12 tests passed**. These cover deterministic disjoint household assignment, adjacent-order relevance, ranker candidate/label grouping, ineligible-target metric denominators, stable ranking ties and empty pools, clustered bootstrapping, calibration boundary bins, embedded-source synchronization, artifact checksums, independently recomputed test metrics and paired confidence intervals. The app test renders all **seven pages**, changes the ranker query and calibration model, excludes every same-category alternative through availability controls, and checks the original recommendation CSV control.

The behavioral experiment trains on 15,545 groups / 357,535 candidate rows from 2,100 households. Validation uses 477 events; reporting uses 474 events from 278 of the 450 reserved test households. Four configurations are selected using validation NDCG@5 only; three feature-removal models are evaluated on validation only. Test targets never train the ranker. Historical feature construction remains shared across households, so this is transductive.

NDCG@5 is 0.4067 versus 0.3580 for the weak-label baseline on identical test events; the paired 95% household-bootstrap difference interval is [+0.0102, +0.0865]. Results are synthetic and conditional on observed switches. The new ML Lab was checked through Streamlit AppTest; new desktop/mobile browser inspection and a remote GitHub Actions run were **not** performed. Earlier browser screenshots below describe the original six pages, not the added page.

Reproduce the historical synthetic workflow explicitly:

```bash
python scripts/train.py --data-source synthetic
python -m unittest discover -s tests -v
```

The lightweight advanced report, numeric score matrix and per-event audit table are included with the project. Fitted models and the fully executed notebook remain ignored local outputs. The source notebook has cleared outputs to avoid shipping stale results; tests ensure its embedded Python matches the editable files.

## Original submission evidence

The following records describe the earlier project version and are retained as historical evidence.

The original notebook executed end to end locally in Python 3.11 with requirements pinned to the installed tested versions. The launch cell was intentionally skipped via `FRESHMATCH_SKIP_LAUNCH=1` for automated execution; the generated app was inspected on the already running localhost Streamlit server. A Google Colab live session and public tunnel were not independently tested in this pass.

## Automated checks

26 assertions passed: outer product endpoint separation; all three purged CV endpoint separations; full six-model metric columns; same-category eligibility; complement exclusion; finite local explanation tensors; bounded probabilities; six independently recomputed ROC-AUC/PR-AUC/F1 results; final matrix equality to the selected calibrated model; deployment flag consistency; six AppTest pages; example-product selection and score explanation; self-exclusion; app comparison-table equality.

The artifact files preserve labelled pairs and exact outer/CV indices for audit. Pair classification labels remain heuristic, historical features are transductive, and tuning is not nested. Final-order ranking does not select the deployment winner.

## Browser checks

All six pages inspected at desktop 1280px and mobile 375px: no app exceptions, document overflow or main-container overflow. No captured browser console errors. Wide tables retain internal scrolling. Product selection, local explanation expansion, custom navigation, score rings, stock badge, filters and CSV controls render. Screenshots in assets are captured from the actual app, not mockups. Mobile and desktop viewport overrides were reset after inspection. Reduced-motion rules disable ring and skeleton animation.

See `assets/validation-checks.json` and `assets/responsive-checks.json` for measured evidence. CSS uses explicit dark secondary text, white controls, focus rings and contrast-aware tokens; this is not a comprehensive screen-reader or third-party accessibility certification.

## Environment note

The pre-existing local environment also contains unrelated `dowhy`, whose SciPy upper bound conflicts with the installed SciPy. FreshMatch does not import or require dowhy; its own notebook and app ran successfully. Use a fresh virtual environment for the pinned project requirements.

## Remaining empirical work

Synthetic data and simulated prices do not demonstrate real shopper acceptance, nutritional equivalence or causal recovery. Future ranking is conditional on observed switches; real stockouts may differ. Simulator assumptions are visible and editable. Real deployment needs expert labels, ingredient/pack-size checks, stock constraints and a prospective evaluation.
