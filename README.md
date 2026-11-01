![FreshMatch banner](assets/banner.svg)

# FreshMatch

**An explainable grocery substitution workbench using real Instacart purchase records.**

[Notebook](product_substitution.ipynb) · [Measured results](RESULTS.md) · [Validation](VALIDATION.md) · [Windows setup](WINDOWS_SETUP.md) · [Project report](PROJECT_REPORT.md)

The current app artifacts were trained on **real Instacart records**, not the previous synthetic demonstration. The uploaded dataset contains 49,688 products, 134 aisles and 21 departments. This reproducible CPU experiment samples **3,000 households**, selects **320 products across 51 aisles** using historical frequency, and separates **49,760 historical baskets** from **3,000 final available prior orders**.

Instacart contains product names, basket contents and reorder flags. **Prices are deterministic estimates; brand strings are unverified name-token proxies.** It does not identify confirmed stockouts, accepted substitutions, ingredients or dietary equivalence. Observed same-aisle switching is a proxy outcome, not substitute ground truth.

## Run locally

Use 64-bit Python 3.12 and Git LFS. On Windows, follow [WINDOWS_SETUP.md](WINDOWS_SETUP.md). On other systems:

```bash
git clone https://github.com/RangaMokshagna/FreshMatch.git
cd FreshMatch
git lfs install
git lfs pull
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/train.py --data-source instacart --data-dir ./instacart --check-data
python scripts/train.py --data-source instacart --data-dir ./instacart
python -m unittest discover -s tests -v
python -m streamlit run streamlit_app.py --server.headless=true --browser.gatherUsageStats=false
```

Training is required only when regenerating the models/artifacts. The checked-in inference artifacts let Streamlit start directly through `streamlit_app.py`. Full model binaries remain local; the app reads portable tables, JSON and numeric arrays rather than unpickling a model.

CSV files in `instacart/` are tracked with Git LFS. A clone without LFS may contain small pointer files; validation tells you to run `git lfs pull`. GitHub's Download ZIP may also contain pointers depending on repository archive settings. You can instead copy your already-downloaded CSVs into `instacart/`.

Required inputs: `orders.csv`, `order_products__prior.csv`, `products.csv`, `aisles.csv`, `departments.csv`. The additional `order_products__train.csv` is not used by this experiment. Alternatively extract a downloaded Kaggle archive into a separate directory:

```bash
python scripts/prepare_instacart.py /path/to/archive.zip --output ./instacart-local
python scripts/train.py --data-dir ./instacart-local
```

The loader validates schemas and references, streams the large purchase table, and records SHA-256 hashes of all five required files plus sampling settings in `artifacts/manifest.json`. Each household's last available **prior** order is held out; this is not Kaggle's hidden competition test set. No API key is needed when CSVs are already downloaded. Source: [psparks/instacart-market-basket-analysis](https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis).

Missing real inputs stop training; there is no automatic synthetic fallback. Explicit demo/CI mode remains available with `python scripts/train.py --data-source synthetic`, which regenerates demo artifacts and labels them accordingly.

## What the app does

- **Find Substitutes:** catalogue search, price/brand filters, eligibility rules, ranked suitability cards, feature sensitivities and CSV export.
- **Out-of-Stock Simulator:** multiple unavailable products and explicitly assumed demand/acceptance scenarios. Estimated revenue uses estimated prices; it is not observed sales recovery.
- **Product Explorer:** real catalogue categories, purchase frequency and estimated prices.
- **Relationship Explorer:** Apriori/FP-Growth complements, context alternatives and relationship graphs.
- **Model Performance:** six classifiers, shared evaluation table, ROC/PR curves, Brier loss, permutation importance and ranking baselines.
- **ML Lab:** behavioral LambdaMART, household-held-out results, bootstrap intervals, category slices, validation ablations, interactive ranking and classifier calibration.
- **About:** method, source and limitations.

The main recommendation cards use calibrated weak-label suitability from **XGBoost**, selected by training CV average precision. Behavioral LambdaMART is a separate experimental ranker in ML Lab; its relative rank scores are not acceptance probabilities.

## Evaluation and real-data results

Apriori and FP-Growth mine the same historical baskets at support 0.0015 and length at most two; their itemsets must agree. Pair features combine category/aisle/department/brand proxies, TF-IDF names, shopping-context cosine, smoothed lift, price/popularity ratios and reorder similarity. Eligible candidates share aisle/category, have lift below 1.5 and exclude the query and declared outages.

**Weak-label classification:** all six models share product-disjoint outer/CV partitions, with boundary pairs purged. Seeded category-balanced assignments use **label counts only** to require at least five examples of each class in every retained train/test/CV partition. No fitted model or performance metric selects these assignments. There are 2,036 training pairs, 266 test pairs and 1,532 purged boundary pairs. The test contains only **five positive weak labels**, so classifier metrics are fragile and do not establish robust substitute quality. Fold-local scaling and sigmoid calibration remain in place. The exact fold indices enter the fitted-model cache key.

**Behavioral ranking:** LambdaMART learns historical adjacent-order switches from 2,100 training households. Four configurations compete on 384 final-order events from separate validation households. The selected depth-2, 160-tree model is fixed before reporting on **365 events from 163 of the 450 reserved test households**. Training includes 8,840 informative candidate groups / 147,340 rows. Groups with no eligible positive or no negative ordering are excluded from training, but evaluation retains ineligible targets in metric denominators.

| Ranker · same 365 test events | NDCG@5 | Hit rate |
| --- | ---: | ---: |
| Behavioral LambdaMART | 0.1294 | 24.4% |
| Weak-label classifier | 0.0647 | 14.0% |
| Content similarity | 0.0883 | 19.2% |
| Shopping context | 0.1019 | 22.2% |
| Popularity | **0.1409** | **27.4%** |

LambdaMART's paired NDCG difference versus the weak-label classifier is **+0.0647**, with a 95% household-bootstrap interval **[+0.0437, +0.0859]**. **Popularity performs better than LambdaMART on this test.** We report this without changing model selection after test inspection. Only **36.7%** of test events have any relevant target in the eligible pool, making candidate coverage a material limitation. Historical features use all households, so the evaluation remains **transductive**, despite disjoint household assignments for ranker fitting/selection/testing.

These figures differ from the separate 2,540-event full-household weak-classifier benchmark shown on Model Performance. Do not compare the two populations as if they were identical. Full classifier/ranking tables are in [RESULTS.md](RESULTS.md); the advanced report and per-event audit rows are in `artifacts/advanced_report.json` and `advanced_test_events.csv`. Previous synthetic numbers are historical demonstrations, not current real-data results.

## Reproducibility

The notebook embeds `app.py`, `advanced_ml.py`, `real_data.py` and `evaluation.py` with writefile cells for self-contained execution. Set `FRESHMATCH_DATA_DIR` before notebook ingestion; real data is the default. Use `FRESHMATCH_SKIP_LAUNCH=1` for automated execution, avoiding a public tunnel. `scripts/train.py` verifies exact pinned package versions, checks source synchronization, executes the notebook, and saves `.cache_freshmatch/executed.ipynb`.

After editing Python sources, run `python scripts/sync_notebook.py` before training. `--check` verifies synchronization without modifying files. Seeds are fixed at 42. Cached ingestion depends on all source hashes; model caching includes exact CV indices. Do not change splits or thresholds after inspecting test performance and then describe the same test as untouched.

The local real-data notebook run and **23 tests** passed, including all seven app pages, ranking filters, split isolation, class support, calibration, source synchronization, checksums and recomputed bootstrap intervals. CI currently exercises explicit synthetic mode to avoid large LFS downloads on every push; a real-data CI run is not claimed. Existing screenshots and earlier validation JSON describe the historical synthetic UI and are not new real-data browser evidence.

## Files and team

| File | Purpose |
| --- | --- |
| `product_substitution.ipynb` | Executable training, evaluation, embedded app and optional launcher |
| `real_data.py` | Strict CSV validation, streaming ingestion, provenance and archive extraction |
| `evaluation.py` | Class-supported product-disjoint outer/CV assignment |
| `advanced_ml.py` | Behavioral ranking, clustered uncertainty and calibration diagnostics |
| `app.py` / `streamlit_app.py` | Generated app and deployment entry point |
| `scripts/` / `tests/` | Reproducible training, synchronization and automated checks |
| `artifacts/` | Current real-data inference outputs and evaluation evidence |
| `instacart/` | Source CSVs stored with Git LFS |

K. Darshan Sai · J. Ranga Mokshagna · P. Bharat Sai. [MIT license](LICENSE).
