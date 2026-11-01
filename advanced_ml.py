"""Behavioral learning-to-rank and auditable offline evaluation for FreshMatch.

Catalogue features are transductive (all historical baskets); future orders never
enter feature fitting or ranker selection. Observed switches are proxy relevance,
not confirmed stockouts, expert suitability or shopper acceptance.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss
from xgboost import XGBRanker


def household_split(users, seed=42):
    ids = np.unique(np.asarray(users, dtype=int))
    if len(ids) < 20:
        raise ValueError('At least 20 households are required for train/validation/test splits.')
    ids = np.random.default_rng(seed).permutation(ids)
    a, b = int(.7 * len(ids)), int(.85 * len(ids))
    return {name: set(part.tolist()) for name, part in zip(
        ['train', 'validation', 'test'], [ids[:a], ids[a:b], ids[b:]])}


def switching_events(lines, orders, products, synthetic=False):
    """Adjacent observed orders, retaining all relevant targets before eligibility."""
    pid = dict(zip(products.product_id, range(len(products))))
    baskets = {int(oid): set(g.product_id.map(pid).dropna().astype(int))
               for oid, g in lines.groupby('order_id', sort=False)}
    aisle = products.aisle.to_numpy()
    need = products.need_id.to_numpy() if synthetic else None
    events = []
    for user, group in orders.sort_values(['user_id', 'order_number']).groupby('user_id', sort=False):
        sequence = group.order_id.astype(int).tolist()
        for previous, current in zip(sequence, sequence[1:]):
            old, new = baskets.get(previous, set()), baskets.get(current, set())
            for query in sorted(old - new):
                targets = sorted(t for t in new if aisle[t] == aisle[query]
                                 and (need is None or need[t] == need[query]))
                if targets:
                    events.append(dict(user=int(user), query=query, targets=targets,
                                       previous_order=previous, target_order=current))
    return events


def ranking_records(values, eligible, events, categories, k=5):
    values, eligible = np.asarray(values), np.asarray(eligible, dtype=bool)
    if values.shape != eligible.shape or values.ndim != 2 or values.shape[0] != values.shape[1]:
        raise ValueError('Scores and eligibility must be equal square matrices.')
    if k < 1 or not np.isfinite(values[eligible]).all():
        raise ValueError('Positive K and finite eligible scores are required.')
    top = {}
    for query in {e['query'] for e in events}:
        ids = np.flatnonzero(eligible[query]).copy()
        ids = ids[ids != query]
        top[query] = ids[np.argsort(-values[query, ids], kind='stable')][:k]
    rows = []
    for e in events:
        query, targets = e['query'], set(e['targets'])
        if not targets:
            raise ValueError('Switch events must contain at least one relevant target.')
        candidates = top[query]
        rel = np.isin(candidates, list(targets)).astype(float)
        positions = np.arange(len(rel)) + 1
        hits = rel.sum()
        ideal = np.sum(1 / np.log2(np.arange(min(k, len(targets))) + 2))
        rows.append(dict(user=e['user'], query=query, category=str(categories[query]),
            precision_at_k=float(hits / k), recall_at_k=float(hits / len(targets)),
            ndcg_at_k=float(np.sum(rel / np.log2(positions + 1)) / ideal),
            map_at_k=float(np.sum(np.cumsum(rel) / positions * rel) / len(targets)),
            hit_rate=float(hits > 0), target_coverage=float(any(eligible[query, t] and t != query for t in targets))))
    return pd.DataFrame(rows)


def cluster_interval(frame, metric, seed=42, draws=1000):
    """Event-weighted mean; resample whole households, preserving their event counts."""
    if frame.empty:
        raise ValueError('Cannot bootstrap an empty evaluation.')
    agg = frame.groupby('user')[metric].agg(['sum', 'size'])
    samples = np.random.default_rng(seed).integers(0, len(agg), size=(draws, len(agg)))
    means = agg['sum'].to_numpy()[samples].sum(1) / agg['size'].to_numpy()[samples].sum(1)
    return [float(v) for v in np.quantile(means, [.025, .975])]


def calibration_diagnostics(y, probabilities, bins=10):
    y, p = np.asarray(y), np.asarray(probabilities, dtype=float)
    if y.shape != p.shape or y.ndim != 1 or not len(y) or not np.isin(y, [0, 1]).all():
        raise ValueError('Expected equally sized nonempty binary labels and probabilities.')
    if bins < 1 or not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError('Probabilities must be finite and in [0, 1]; bins must be positive.')
    assignments = np.minimum((p * bins).astype(int), bins - 1)
    rows = []
    for i in range(bins):
        mask = assignments == i
        if mask.any():
            rows.append(dict(bin=i, count=int(mask.sum()), mean_probability=float(p[mask].mean()),
                             observed_frequency=float(y[mask].mean())))
    ece = sum(r['count'] * abs(r['mean_probability'] - r['observed_frequency']) for r in rows) / len(y)
    return dict(brier=float(brier_score_loss(y, p)), log_loss=float(log_loss(y, p, labels=[0, 1])),
                ece=float(ece), samples=len(y), reliability=rows)


def _training_arrays(events, eligible, feature_cube):
    xs, ys, groups = [], [], []
    for e in events:
        q = e['query']
        ids = np.flatnonzero(eligible[q])
        ids = ids[ids != q]
        labels = np.isin(ids, e['targets']).astype(np.int32)
        # Constant-label groups have no preference ordering to learn.
        if len(ids) < 2 or not labels.any() or labels.all():
            continue
        xs.append(feature_cube[q, ids]); ys.append(labels); groups.append(len(ids))
    if not groups:
        raise ValueError('No informative historical switch groups are available for ranker fitting.')
    return np.concatenate(xs), np.concatenate(ys), np.asarray(groups, dtype=np.uint32)


def run_experiment(*, products, history, history_orders, final_events, feature_cube,
                   feature_names, eligible, weak_scores, text_scores, context_scores,
                   models, pair_x, pair_y, artifact_dir, synthetic, seed=42):
    """Fit on historical transitions; choose configs on validation final orders only."""
    started = perf_counter()
    output = Path(artifact_dir)
    splits = household_split(history_orders.user_id.unique(), seed)
    historical = switching_events(history, history_orders, products, synthetic)
    train = [e for e in historical if e['user'] in splits['train']]
    valid = [e for e in final_events if e['user'] in splits['validation']]
    test = [e for e in final_events if e['user'] in splits['test']]
    if not valid or not test:
        raise ValueError('Validation and test need final-order switch events.')
    categories = products.category.to_numpy()
    train_x, train_y, group = _training_arrays(train, eligible, feature_cube)
    candidates = [dict(max_depth=depth, n_estimators=trees) for depth in [2, 4] for trees in [80, 160]]
    trials, fitted = [], []
    for parameters in candidates:
        estimator = XGBRanker(objective='rank:ndcg', eval_metric='ndcg@5', learning_rate=.06,
                              tree_method='hist', n_jobs=2, random_state=seed, **parameters)
        estimator.fit(train_x, train_y, group=group)
        scores = estimator.predict(feature_cube.reshape(-1, feature_cube.shape[-1])).reshape(eligible.shape)
        validation = ranking_records(scores, eligible, valid, categories)
        trials.append(dict(**parameters, validation_ndcg_at_5=float(validation.ndcg_at_k.mean())))
        fitted.append((estimator, scores))
    best = max(range(len(trials)), key=lambda i: trials[i]['validation_ndcg_at_5'])
    ranker, scores = fitted[best]
    ranker.save_model(output / 'behavioral_ranker.ubj')
    np.savez_compressed(output / 'advanced_scores.npz', scores=scores.astype(np.float32))
    baselines = {'Behavioral LambdaMART': scores, 'Weak-label classifier': weak_scores,
                 'Content similarity': text_scores, 'Shopping context': context_scores,
                 'Popularity': np.broadcast_to(products.popularity.to_numpy(), eligible.shape)}
    # Feature removal diagnostics use validation only; no selection on test metrics.
    ablations = []
    for label, removed in [('Without name similarity', ['text_similarity']),
                           ('Without shopping context', ['context_similarity', 'log_lift']),
                           ('Without price and popularity', ['price_ratio', 'popularity_ratio', 'reorder_similarity'])]:
        keep = [i for i, name in enumerate(feature_names) if name not in removed]
        ablated = XGBRanker(objective='rank:ndcg', learning_rate=.06, tree_method='hist',
                            n_jobs=2, random_state=seed, **candidates[best])
        ablated.fit(train_x[:, keep], train_y, group=group)
        vals = ablated.predict(feature_cube[:, :, keep].reshape(-1, len(keep))).reshape(eligible.shape)
        frame = ranking_records(vals, eligible, valid, categories)
        ablations.append(dict(experiment=label, validation_ndcg_at_5=float(frame.ndcg_at_k.mean())))
    ablations.insert(0, dict(experiment='All features', validation_ndcg_at_5=trials[best]['validation_ndcg_at_5']))
    records, summaries = {}, []
    for name, values in baselines.items():
        frame = ranking_records(values, eligible, test, categories)
        records[name] = frame
        low, high = cluster_interval(frame, 'ndcg_at_k', seed)
        summaries.append(dict(model=name, **frame[['precision_at_k', 'recall_at_k', 'ndcg_at_k',
            'map_at_k', 'hit_rate', 'target_coverage']].mean().to_dict(), ndcg_ci_low=low,
            ndcg_ci_high=high, events=len(frame), households=int(frame.user.nunique())))
    paired = records['Behavioral LambdaMART'][['user', 'query']].copy()
    paired['ndcg_delta'] = (records['Behavioral LambdaMART'].ndcg_at_k - records['Weak-label classifier'].ndcg_at_k)
    delta_ci = cluster_interval(paired, 'ndcg_delta', seed)
    slices = records['Behavioral LambdaMART'].groupby('category').agg(
        events=('query', 'size'), households=('user', 'nunique'), ndcg_at_5=('ndcg_at_k', 'mean'),
        recall_at_5=('recall_at_k', 'mean'), hit_rate=('hit_rate', 'mean')).reset_index().to_dict('records')
    reliability = {name: calibration_diagnostics(pair_y, estimator.predict_proba(pair_x)[:, 1])
                   for name, estimator in models.items()}
    combined = pd.concat([frame.assign(model=name) for name, frame in records.items()], ignore_index=True)
    combined.to_csv(output / 'advanced_test_events.csv', index=False)
    fingerprint = hashlib.sha256(np.ascontiguousarray(feature_cube).tobytes()).hexdigest()
    report = dict(version='1.0', seed=seed, source='Synthetic grocery simulation' if synthetic else 'Instacart',
        objective='Behavioral LambdaMART / rank:ndcg', selection='Validation-household final-order NDCG@5',
        selected_parameters=candidates[best], trials=trials, ablations=ablations, test_metrics=summaries,
        paired_comparison=dict(baseline='Weak-label classifier', metric='NDCG@5',
            mean_delta=float(paired.ndcg_delta.mean()), ci_low=delta_ci[0], ci_high=delta_ci[1]),
        category_slices=slices, calibration=reliability, feature_names=list(feature_names),
        gain_importance=dict(zip(feature_names, [float(v) for v in ranker.feature_importances_])),
        split=dict(households={name: sorted(ids) for name, ids in splits.items()},
                   train_groups=int(len(group)), train_rows=len(train_y),
                   historical_switch_events=len(train), validation_events=len(valid), test_events=len(test)),
        feature_sha256=fingerprint, runtime_seconds=round(perf_counter() - started, 2),
        limitations=[
            'Historical features use all households: this is transductive, not a fully inductive evaluation.',
            'Ranker training households, validation households and test households are disjoint.',
            'Training labels use historical adjacent orders; validation/test labels use final orders.',
            'Switches are observed purchase proxies, not confirmed substitutions or real stockouts.',
            'Synthetic need groups define relevance only; need_id is never an input feature.',
            'Rank scores are relative preferences, not calibrated acceptance probabilities.',
            'Validation is reused for tuning and ablations. Reported test metrics do not select the ranker.',
            'Bootstrap intervals resample households; category slices can have small sample sizes.'])
    (output / 'advanced_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    assert not splits['train'] & splits['validation'] and not splits['train'] & splits['test'] and not splits['validation'] & splits['test']
    assert np.isfinite(scores).all()
    print(f'Behavioral ranker: {len(group):,} historical training groups; {len(valid):,} validation / {len(test):,} test events.')
    print(pd.DataFrame(summaries).to_string(index=False))
    print('Paired test NDCG@5 difference vs weak labels:', report['paired_comparison'])
    return report
