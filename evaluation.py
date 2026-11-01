"""Label-stratified product-disjoint splits, selected without fitting any model."""
from __future__ import annotations

import numpy as np


def product_disjoint_splits(a, b, labels, categories, *, seed=42, folds=3,
                            min_class_count=5, outer_attempts=128, fold_attempts=512):
    """Purge every cross-boundary pair and require class support in each partition.

    Retry deterministic, category-balanced product assignments using class counts
    only. No estimator, probability or performance metric influences assignment.
    Products from tiny categories may supply no retained within-partition pairs.
    """
    a, b, labels, categories = map(np.asarray, (a, b, labels, categories))
    if a.shape != b.shape or a.shape != labels.shape or a.ndim != 1:
        raise ValueError('Pair endpoints and labels must be equally sized vectors.')
    if not np.isin(labels, [0, 1]).all() or min_class_count < 1 or folds < 2:
        raise ValueError('Binary labels, positive class support and at least two folds are required.')
    if not len(a) or np.any(a < 0) or np.any(b < 0) or max(a.max(), b.max()) >= len(categories):
        raise ValueError('Pair endpoints must index the catalogue.')
    counts = lambda ids: np.bincount(labels[ids].astype(int), minlength=2)
    rng = np.random.default_rng(seed)
    n = len(categories)
    groups = [np.flatnonzero(categories == c) for c in np.unique(categories)]
    for outer in range(outer_attempts):
        held = np.zeros(n, dtype=bool)
        for group in groups:
            ids = rng.permutation(group)
            held[ids[:min(len(ids), max(2, round(len(ids) * .25)))]] = True
        train = np.flatnonzero(~held[a] & ~held[b])
        test = np.flatnonzero(held[a] & held[b])
        if np.min(counts(test)) < min_class_count or np.min(counts(train)) < min_class_count * folds:
            continue
        for attempt in range(fold_attempts):
            assignment = np.full(n, -1, dtype=int)
            for group in groups:
                ids = rng.permutation(group[~held[group]])
                # Random phase avoids concentrating every rare category in fold zero.
                assignment[ids] = (np.arange(len(ids)) + rng.integers(folds)) % folds
            fa, fb = assignment[a[train]], assignment[b[train]]
            cv = [(np.flatnonzero((fa != f) & (fb != f)),
                   np.flatnonzero((fa == f) & (fb == f))) for f in range(folds)]
            if any(np.min(counts(train[tr])) < min_class_count or
                   np.min(counts(train[va])) < min_class_count for tr, va in cv):
                continue
            audit = dict(method='Seeded category-balanced product assignments; label-count support only',
                min_examples_per_class=min_class_count, seed=seed,
                outer_assignment_attempt=outer + 1, fold_assignment_attempt=attempt + 1,
                train_class_counts=counts(train).tolist(), test_class_counts=counts(test).tolist(),
                purged_pairs=int(len(a)-len(train)-len(test)),
                folds=[dict(train_class_counts=counts(train[tr]).tolist(),
                            validation_class_counts=counts(train[va]).tolist()) for tr, va in cv])
            return train, test, cv, audit
    raise ValueError('Cannot form supported product-disjoint partitions. Increase catalogue/data coverage; '
                     f'each retained train/test/CV partition needs {min_class_count} examples per class.')
