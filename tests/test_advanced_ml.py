import json
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from advanced_ml import (calibration_diagnostics, cluster_interval, household_split,
                         ranking_records, switching_events, _training_arrays)

ROOT = Path(__file__).resolve().parents[1]


class EvaluationTests(unittest.TestCase):
    def test_households_are_disjoint_complete_and_reproducible(self):
        first = household_split(np.repeat(np.arange(100), 2))
        self.assertEqual(first, household_split(np.arange(100)))
        self.assertEqual(set.union(*first.values()), set(range(100)))
        self.assertFalse(first['train'] & first['validation'])
        self.assertFalse(first['train'] & first['test'])
        self.assertFalse(first['validation'] & first['test'])
        with self.assertRaises(ValueError):
            household_split([1, 2])

    def test_ranking_preserves_ineligible_targets_in_denominator(self):
        eligible = np.ones((4, 4), dtype=bool)
        np.fill_diagonal(eligible, False)
        eligible[0, 3] = False
        scores = np.zeros((4, 4)); scores[0] = [100, .2, .8, 10]
        rows = ranking_records(scores, eligible, [dict(user=1, query=0, targets=[2, 3])], ['a']*4, k=2)
        self.assertEqual(rows.iloc[0].recall_at_k, .5)
        self.assertEqual(rows.iloc[0].precision_at_k, .5)
        self.assertAlmostEqual(rows.iloc[0].ndcg_at_k, 1/(1+1/np.log2(3)))
        self.assertEqual(rows.iloc[0].map_at_k, .5)
        self.assertEqual(rows.iloc[0].target_coverage, 1)

    def test_no_candidates_and_stable_ties(self):
        scores = np.ones((3, 3))
        events = [dict(user=1, query=0, targets=[1])]
        none = ranking_records(scores, np.zeros((3, 3), dtype=bool), events, ['a']*3)
        self.assertEqual(none.iloc[0].ndcg_at_k, 0)
        tied = ranking_records(scores, np.ones((3, 3), dtype=bool), events, ['a']*3, k=1)
        self.assertEqual(tied.iloc[0].hit_rate, 1)  # query excluded even if eligibility says true
        with self.assertRaises(ValueError):
            ranking_records(np.full((3, 3), np.nan), np.ones((3, 3)), events, ['a']*3)

    def test_household_bootstrap_preserves_cluster_sizes(self):
        frame = pd.DataFrame({'user': [1, 1, 1, 2], 'metric': [0., 0., 0., 1.]})
        self.assertEqual(cluster_interval(frame, 'metric'), [0., 1.])
        frame['metric'] = .4
        np.testing.assert_allclose(cluster_interval(frame, 'metric'), [.4, .4])

    def test_calibration_boundary_bins_and_validation(self):
        perfect = calibration_diagnostics([0, 1], [0., 1.])
        self.assertEqual(perfect['ece'], 0)
        self.assertEqual(perfect['brier'], 0)
        self.assertEqual([r['bin'] for r in perfect['reliability']], [0, 9])
        poor = calibration_diagnostics([0, 1], [1., 0.])
        self.assertEqual(poor['ece'], 1)
        with self.assertRaises(ValueError):
            calibration_diagnostics([0, 1], [0., np.nan])

    def test_historical_events_are_adjacent_and_exclude_repeats(self):
        products = pd.DataFrame({'product_id': [10, 11, 12], 'aisle': ['a']*3, 'need_id': [1, 1, 2]})
        orders = pd.DataFrame({'order_id': [3, 1, 2], 'user_id': [7]*3, 'order_number': [3, 1, 2]})
        lines = pd.DataFrame({'order_id': [1, 2, 3], 'product_id': [10, 11, 12]})
        events = switching_events(lines, orders, products, synthetic=True)
        self.assertEqual(events, [dict(user=7, query=0, targets=[1], previous_order=1, target_order=2)])
        real = switching_events(lines, orders, products, synthetic=False)
        self.assertEqual(len(real), 2)

    def test_ranker_groups_preserve_labels_and_candidates(self):
        features = np.arange(18).reshape(3, 3, 2)
        eligible = ~np.eye(3, dtype=bool)
        x, y, groups = _training_arrays([dict(query=0, targets=[2])], eligible, features)
        np.testing.assert_array_equal(x, features[0, [1, 2]])
        np.testing.assert_array_equal(y, [0, 1])
        self.assertEqual(groups.tolist(), [2])
        with self.assertRaises(ValueError):
            _training_arrays([dict(query=0, targets=[0])], eligible, features)


class ArtifactTests(unittest.TestCase):
    def test_notebook_and_python_sources_match(self):
        n = json.loads((ROOT/'product_substitution.ipynb').read_text())
        for name in ['app.py', 'advanced_ml.py', 'real_data.py', 'evaluation.py']:
            cells = [''.join(c['source']) for c in n['cells'] if c['cell_type']=='code']
            embedded = next(s.split('\n', 1)[1] for s in cells if s.startswith(f'%%writefile {name}\n'))
            self.assertEqual(embedded, (ROOT/name).read_text())

    def test_public_artifact_checksums(self):
        import hashlib
        manifest = json.loads((ROOT/'artifacts/manifest.json').read_text())
        for name in ['advanced_report.json', 'advanced_scores.npz', 'advanced_test_events.csv', 'products.csv', 'matrices.npz']:
            self.assertEqual(hashlib.sha256((ROOT/'artifacts'/name).read_bytes()).hexdigest(), manifest['sha256'][name])

    def test_paired_interval_matches_saved_event_records(self):
        report = json.loads((ROOT/'artifacts/advanced_report.json').read_text())
        records = pd.read_csv(ROOT/'artifacts/advanced_test_events.csv')
        ranker = records[records.model=='Behavioral LambdaMART'].reset_index(drop=True)
        baseline = records[records.model=='Weak-label classifier'].reset_index(drop=True)
        pd.testing.assert_frame_equal(ranker[['user','query']], baseline[['user','query']])
        ranker['delta'] = ranker.ndcg_at_k-baseline.ndcg_at_k
        interval = cluster_interval(ranker, 'delta', seed=report['seed'])
        np.testing.assert_allclose(interval, [report['paired_comparison']['ci_low'],report['paired_comparison']['ci_high']])
        self.assertAlmostEqual(ranker.delta.mean(), report['paired_comparison']['mean_delta'])

    def test_saved_protocol_and_metrics(self):
        report = json.loads((ROOT/'artifacts/advanced_report.json').read_text())
        splits = {k: set(v) for k, v in report['split']['households'].items()}
        self.assertFalse(splits['train'] & splits['test'])
        self.assertFalse(splits['validation'] & splits['test'])
        selected = max(report['trials'], key=lambda r:r['validation_ndcg_at_5'])
        self.assertEqual(report['selected_parameters'], {k:selected[k] for k in ['max_depth','n_estimators']})
        records = pd.read_csv(ROOT/'artifacts/advanced_test_events.csv')
        for row in report['test_metrics']:
            frame = records[records.model == row['model']]
            self.assertEqual(len(frame), row['events'])
            self.assertTrue(set(frame.user) <= splits['test'])
            for metric in ['ndcg_at_k','recall_at_k','precision_at_k','map_at_k','hit_rate']:
                self.assertAlmostEqual(frame[metric].mean(), row[metric])
        with np.load(ROOT/'artifacts/advanced_scores.npz',allow_pickle=False) as z:
            n = len(pd.read_csv(ROOT/'artifacts/products.csv'))
            self.assertEqual(z['scores'].shape, (n, n))
            self.assertTrue(np.isfinite(z['scores']).all())

if __name__ == '__main__':
    unittest.main()
