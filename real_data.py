"""Validated, local-only ingestion of the official Instacart CSV dataset.

Resolve repository CSVs with Git LFS before ingestion; never treat LFS pointers as data. Real purchase records do not contain prices or
verified brands; those fields remain explicitly estimated/proxied in FreshMatch.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

SCHEMAS = {
    'orders.csv': ['order_id', 'user_id', 'order_number', 'eval_set'],
    'order_products__prior.csv': ['order_id', 'product_id', 'reordered'],
    'products.csv': ['product_id', 'product_name', 'aisle_id', 'department_id'],
    'aisles.csv': ['aisle_id', 'aisle'],
    'departments.csv': ['department_id', 'department'],
}


class DatasetError(ValueError):
    """A missing or invalid source dataset; never a reason to synthesize records."""


def find_instacart(directory):
    root = Path(directory).expanduser()
    if not root.is_dir():
        return None
    candidates = [root] + sorted(p for p in root.iterdir() if p.is_dir())
    matches = [p for p in candidates if all((p / name).is_file() for name in SCHEMAS)]
    if len(matches) > 1:
        raise DatasetError('Multiple complete datasets found. Point --data-dir to one exact dataset directory.')
    return matches[0] if matches else None


def validate_instacart(directory):
    """Check required files, schemas and sample rows without loading the large prior table."""
    root = find_instacart(directory)
    if root is None:
        missing = [name for name in SCHEMAS if not (Path(directory).expanduser() / name).is_file()]
        raise DatasetError('Real Instacart data is required. Extract the official dataset into '
            f'{Path(directory).expanduser()}. Missing: {", ".join(missing)}. '
            'Download after accepting the Kaggle competition rules, or provide the extracted CSVs. '
            'Synthetic demo data must be selected explicitly with --data-source synthetic.')
    for name, columns in SCHEMAS.items():
        try:
            with (root / name).open('rb') as handle:
                is_pointer = handle.read(128).startswith(b'version https://git-lfs.github.com/spec/v1')
            if is_pointer:
                raise DatasetError(f'{name} is a Git LFS pointer. Run git lfs install and git lfs pull before training.')
            sample = pd.read_csv(root / name, nrows=1000)
        except DatasetError:
            raise
        except (OSError, ValueError, pd.errors.ParserError) as exc:
            raise DatasetError(f'Cannot read {name}: {type(exc).__name__}.') from exc
        missing = set(columns) - set(sample)
        if missing:
            raise DatasetError(f'{name} is missing columns: {", ".join(sorted(missing))}.')
        if sample.empty or sample[columns].isna().any().any():
            raise DatasetError(f'{name} must contain nonempty, non-null required fields.')
        for col in [c for c in columns if c.endswith('_id') or c in ['order_number', 'reordered']]:
            vals = pd.to_numeric(sample[col], errors='coerce')
            if vals.isna().any() or (vals % 1 != 0).any() or (vals < 0).any():
                raise DatasetError(f'{name}.{col} must contain nonnegative integers.')
        if 'reordered' in sample and not sample.reordered.isin([0, 1]).all():
            raise DatasetError(f'{name}.reordered must be 0 or 1.')
        if name == 'orders.csv' and not sample.eval_set.isin(['prior', 'train', 'test']).all():
            raise DatasetError('orders.csv.eval_set must be prior, train or test.')
    return root


def provenance(directory, *, seed=42, max_products=320, max_households=3000):
    root = validate_instacart(directory)
    files = {}
    for name in SCHEMAS:
        digest = hashlib.sha256()
        with (root / name).open('rb') as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b''):
                digest.update(block)
        files[name] = {'sha256': digest.hexdigest(), 'bytes': (root / name).stat().st_size}
    return dict(source='Instacart', ingestion_version='strict-instacart-v1', files=files,
                seed=seed, max_products=max_products, max_households=max_households,
                price_origin='Deterministic estimates; absent from original dataset',
                brand_origin='First-name-token proxy; not verified brand data',
                holdout='Each sampled household\'s last available prior order; all earlier prior orders are history')


def cache_fingerprint(audit):
    return hashlib.sha256(json.dumps(audit, sort_keys=True).encode()).hexdigest()


def _unique(frame, key, name):
    if frame[key].isna().any() or frame[key].duplicated().any():
        raise DatasetError(f'{name}.{key} must be unique and non-null.')


def load_instacart(directory, *, seed=42, max_products=320, max_households=3000, chunksize=1_000_000):
    root = validate_instacart(directory)
    if max_products < 2 or max_households < 20:
        raise DatasetError('Select at least 2 products and 20 households.')
    raw = pd.read_csv(root / 'products.csv', usecols=SCHEMAS['products.csv'])
    aisles = pd.read_csv(root / 'aisles.csv', usecols=SCHEMAS['aisles.csv'])
    departments = pd.read_csv(root / 'departments.csv', usecols=SCHEMAS['departments.csv'])
    for frame, key, name in [(raw, 'product_id', 'products.csv'), (aisles, 'aisle_id', 'aisles.csv'),
                              (departments, 'department_id', 'departments.csv')]:
        _unique(frame, key, name)
    if not raw.aisle_id.isin(aisles.aisle_id).all() or not raw.department_id.isin(departments.department_id).all():
        raise DatasetError('Product aisle/department references do not match their lookup tables.')
    raw = raw.merge(aisles, on='aisle_id', validate='many_to_one').merge(
        departments, on='department_id', validate='many_to_one')
    orders = pd.read_csv(root / 'orders.csv', usecols=SCHEMAS['orders.csv'])
    _unique(orders, 'order_id', 'orders.csv')
    if orders[['user_id', 'order_number']].isna().any().any() or orders.duplicated(['user_id', 'order_number']).any():
        raise DatasetError('Household order numbers must be unique and non-null.')
    orders = orders[orders.eval_set == 'prior'].copy()
    sizes = orders.groupby('user_id').size()
    users = np.sort(sizes[sizes >= 4].index)
    if len(users) < 20:
        raise DatasetError('At least 20 households with four prior orders each are required.')
    chosen = np.random.default_rng(seed).choice(users, min(max_households, len(users)), replace=False)
    orders = orders[orders.user_id.isin(chosen)].copy()
    last = orders.groupby('user_id').order_number.transform('max')
    historic_ids = set(orders.loc[orders.order_number < last, 'order_id'])
    wanted = set(orders.order_id)
    chunks = []
    with pd.read_csv(root / 'order_products__prior.csv', usecols=SCHEMAS['order_products__prior.csv'], chunksize=chunksize) as reader:
        for chunk in reader:
            selected = chunk[chunk.order_id.isin(wanted)].copy()
            if selected.empty:
                continue
            if selected.isna().any().any() or not selected.reordered.isin([0, 1]).all():
                raise DatasetError('Selected purchase rows contain missing fields or invalid reorder flags.')
            if not selected.product_id.isin(raw.product_id).all():
                raise DatasetError('Purchase rows reference products missing from products.csv.')
            chunks.append(selected)
    if not chunks:
        raise DatasetError('No purchase rows match the sampled households.')
    lines = pd.concat(chunks, ignore_index=True)
    if lines.duplicated(['order_id', 'product_id']).any():
        raise DatasetError('Duplicate product/order pairs found in purchase records.')
    if not wanted <= set(lines.order_id):
        raise DatasetError('Some sampled orders have no purchase rows. Check that the full prior file was extracted.')
    # Holdout product frequency must not influence catalogue selection.
    counts = lines[lines.order_id.isin(historic_ids)].product_id.value_counts()
    top = set(counts.head(max_products).index)
    products = raw[raw.product_id.isin(top)].rename(columns={'product_name': 'name', 'aisle': 'category'}).copy()
    products['aisle'] = products.category
    products['brand'] = products.name.str.split().str[0].fillna('Unknown')
    products = products.sort_values('product_id').reset_index(drop=True)
    # Instacart has no prices; these deterministic estimates remain labelled in the app/report.
    products['price'] = np.round(np.random.default_rng(seed).lognormal(1.35, .4, len(products)), 2)
    return products, orders[['order_id', 'user_id', 'order_number']], lines[lines.product_id.isin(top)].copy()


def extract_instacart_archive(archive, output):
    """Extract only recognized CSV payloads, including Kaggle's nested CSV ZIPs.

    Stage and validate all five files before copying; never overwrite existing data
    and never use archive paths as filesystem destinations.
    """
    import shutil
    import tempfile
    import zipfile
    destination = Path(output).expanduser()
    if any((destination / name).exists() for name in SCHEMAS):
        raise DatasetError('Required CSV files already exist in the output directory. Choose a new directory.')
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.extract-', dir=destination) as temporary:
        stage = Path(temporary)
        seen = set()

        def extract_csv(container, member):
            name = Path(member.filename).name
            if name not in SCHEMAS:
                return
            if name in seen:
                raise DatasetError(f'Duplicate archive payload: {name}.')
            seen.add(name)
            with container.open(member) as src, (stage / name).open('xb') as dst:
                shutil.copyfileobj(src, dst)

        try:
            with zipfile.ZipFile(archive) as outer:
                for member in outer.infolist():
                    name = Path(member.filename).name
                    if name in SCHEMAS:
                        extract_csv(outer, member)
                    elif name.endswith('.zip') and name[:-4] in SCHEMAS:
                        with outer.open(member) as stream, zipfile.ZipFile(stream) as inner:
                            for payload in inner.infolist():
                                extract_csv(inner, payload)
            validate_instacart(stage)
            for name in SCHEMAS:
                with (stage / name).open('rb') as src, (destination / name).open('xb') as dst:
                    shutil.copyfileobj(src, dst)
        except zipfile.BadZipFile as exc:
            raise DatasetError('The input is not a valid Instacart ZIP archive.') from exc
    return destination
