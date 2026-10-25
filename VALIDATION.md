# FreshMatch — Submission validation

The current notebook executed end to end locally in Python 3.11 with requirements pinned to the installed tested versions. The launch cell was intentionally skipped via `FRESHMATCH_SKIP_LAUNCH=1` for automated execution; the generated app was inspected on the already running localhost Streamlit server. A Google Colab live session and public tunnel were not independently tested in this pass.

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
