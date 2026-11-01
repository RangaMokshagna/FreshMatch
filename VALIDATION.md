# FreshMatch — Current real-data validation

## Data and provenance

Fetched Git LFS commit `2fed8b5` from the user's repository. Downloaded and checked out the five required CSV objects; their SHA-256 hashes match the Git LFS pointer OIDs. The prior-purchases file is 577,550,706 bytes and orders.csv is 108,968,645 bytes. The ingestion manifest records all required file hashes, byte sizes and sampling settings. The optional order_products__train.csv is not consumed.

Real CSV schema/sample checks passed. Full ingestion verified catalogue references, unique product/order IDs, sampled purchase references, reorder flags, completeness of sampled orders and absence of duplicate sampled order/product pairs. Each household's final available prior order is separated from history; catalogue frequency selection uses history only.

The run uses 320 real products, 51 aisles, 3,000 households, 49,760 historical baskets and 3,000 final baskets. Prices are estimates and brands are name-token proxies. No synthetic records were used in this run.

## Training and regression checks

`python scripts/train.py --data-source instacart --data-dir ./instacart` completed all notebook cells and integrity assertions. Valid ingestion and mining outputs were reused after diagnosing the initial split failure. The initial category-local folds had a validation partition with no positive weak labels; this failed assertion was not disabled. A tested deterministic label-support split now requires five examples of each class in each retained partition, preserves endpoint separation, and is selected without model performance scores. Exact CV indices enter fitted-model caching.

`python -m unittest discover -s tests -v`: **23 tests passed**. Coverage includes product-disjoint class support and repeatability, infeasible split rejection, deterministic household partitions, real CSV/reference/holdout checks using fabricated fixtures, LFS pointer rejection, archive extraction, no silent synthetic fallback, ranking denominators, bootstrap calculations, probability calibration, source synchronization, inference checksums, and independently recomputed event metrics/paired intervals. The AppTest renders all seven pages, exercises query/calibration choices and complete category outages, and checks the main recommendation CSV control.

The classifier test contains 266 pairs, only five of them positive. This is a material statistical limitation. The behavioral test contains 365 events from 163 households; target coverage is 36.7%. Popularity's NDCG@5 is 0.1409 versus behavioral 0.1294 and weak-label 0.0647. The paired behavioral-minus-weak-label interval is [+0.0437, +0.0859]. No model was selected using these reporting outcomes.

## Scope limits

Historical features remain transductive; labels are weak or observational purchase proxies. This is not confirmed stockout substitution, nutritional equivalence, real-price forecasting or causal sales recovery. The seven-page check uses Streamlit AppTest; new real-data browser/viewport checks were not performed. Existing screenshots and earlier JSON evidence describe the previous synthetic version. The explicit synthetic training path also completed in an isolated temporary copy after the split fix, while the project retained its real artifacts. The GitHub Actions workflow checks explicit synthetic mode; this local real-data execution does not establish a remote real-data CI result.

The source notebook has cleared outputs. The executed notebook is retained locally in .cache_freshmatch/executed.ipynb; portable real inference/audit outputs are tracked in artifacts. Large source CSVs remain in Git LFS; fitted model binaries remain local. Reproduce with the commands in README.md or WINDOWS_SETUP.md.
