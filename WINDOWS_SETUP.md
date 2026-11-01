# Run FreshMatch on Windows with real data

## 1. Download the project

On GitHub, open https://github.com/RangaMokshagna/FreshMatch and choose
**Code → Download ZIP**. Extract `FreshMatch-main.zip` into a folder you can find,
such as `C:\Users\cheth\Downloads\FreshMatch-main`.

Open that folder and confirm you can see `requirements.txt`, `scripts`, and
`streamlit_app.py`. If another `FreshMatch-main` folder is inside, open that inner
folder; the commands below must run beside `requirements.txt`.

GitHub ZIP archives may include small Git LFS pointer files instead of CSV contents.
If you clone using Git instead, install Git LFS and run `git lfs install` followed
by `git lfs pull`. Otherwise copy your previously downloaded CSVs as described below.

## 2. Add the downloaded data

Open `C:\Users\cheth\Downloads\archive`. Copy these extracted files into the
project's `instacart` folder:

```text
FreshMatch-main\
  requirements.txt
  streamlit_app.py
  scripts\
  instacart\
    README.md
    orders.csv
    order_products__prior.csv
    products.csv
    aisles.csv
    departments.csv
```

If Windows hides filename extensions, turn on **View → Show → File name
extensions** in File Explorer. Each required file must be a CSV, not a ZIP.
Extract nested `*.csv.zip` archives if present. Keep the original download as a
backup. Source CSVs already in the repository are stored with Git LFS.

## 3. Install Python and dependencies

Install **64-bit Python 3.12** from https://www.python.org/downloads/windows/
if it is not already installed. Include the Python launcher during installation.

In the project folder, right-click empty space and choose **Open in Terminal**.
Run each command in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

These commands use the virtual environment directly; PowerShell script activation
is not required. Keep this terminal open for the next steps.

## 4. Validate and train with real records

```powershell
.\.venv\Scripts\python.exe scripts\train.py --data-source instacart --data-dir .\instacart --check-data
.\.venv\Scripts\python.exe scripts\train.py --data-source instacart --data-dir .\instacart
```

The first command checks files and sample schemas. The second trains all six
classifiers and the behavioral ranker, writes inference artifacts, and updates
`RESULTS.md`. Wait for `PASS: notebook training, artifact generation and integrity
assertions`. Training time depends on your laptop. Data loading streams the large
purchase CSV; the experiment samples up to 3,000 households and 320 products.

Missing or invalid real data produces an error; it never silently switches to
synthetic data. If a model/data check fails, keep the terminal error for diagnosis.

## 5. Open the application

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Open the local address Streamlit prints. The sidebar should identify the data as
**Instacart** after a successful training run. Review the **Model Performance** and
**ML Lab** pages for the new real-data metrics.

Instacart supplies real product names, baskets and reorder records. Prices remain
estimates, brand labels are unverified name-token proxies, and observed switching
is not confirmed stockout substitution. The previous synthetic results are not
real-data evidence.

Optional validation:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
