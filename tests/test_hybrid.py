import hashlib
import json
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
from hybrid_ranker import transition_counts, transition_probability, query_percentiles
from advanced_ml import cluster_interval
ROOT=Path(__file__).resolve().parents[1]

class HybridTests(unittest.TestCase):
    def test_disallowed_households_cannot_change_transition_evidence(self):
        events=[dict(user=1,query=0,targets=[1,2]),dict(user=9,query=0,targets=[2])]
        counts=transition_counts(events,3,{1})
        np.testing.assert_array_equal(counts[0],[0,.5,.5])
        events.append(dict(user=9,query=1,targets=[0]))
        np.testing.assert_array_equal(counts,transition_counts(events,3,{1}))
        self.assertEqual(counts.sum(),1.)

    def test_smoothing_backs_off_and_never_crosses_aisles(self):
        p,prior=transition_probability(np.zeros((3,3)),['a','a','b'])
        self.assertEqual(p[0,1],1.)
        self.assertEqual(p[0,2],0.)
        self.assertTrue(np.isfinite(p).all())
        np.testing.assert_array_equal(np.diag(p),np.zeros(3))
        with self.assertRaises(ValueError):transition_probability(np.zeros((2,2)),['a','a'],alpha=0)

    def test_rank_blends_preserve_ties_and_ignore_ineligible_values(self):
        values=np.array([[999,2,2],[3,0,4],[1,2,0]],float)
        mask=~np.eye(3,dtype=bool)
        ranks=query_percentiles(values,mask)
        self.assertEqual(ranks[0,1],ranks[0,2])
        self.assertEqual(ranks[0,0],0.)
        self.assertGreater(ranks[1,2],ranks[1,0])

    def test_report_selection_and_paired_comparisons(self):
        path=ROOT/'artifacts/hybrid_report.json'
        if not path.exists():self.skipTest('Improvement artifacts have not been trained yet')
        report=json.loads(path.read_text());selection=report['selection']
        self.assertEqual(hashlib.sha256((ROOT/'artifacts/hybrid_selection.json').read_bytes()).hexdigest(),report['selection_sha256'])
        self.assertEqual(selection['selected_weights'],max(selection['hybrid_trials'],key=lambda x:x['validation_ndcg_at_5']))
        best=max(selection['model_trials'],key=lambda x:x['validation_ndcg_at_5'])
        self.assertEqual(selection['selected_parameters'],{k:best[k] for k in ['max_depth','n_estimators']})
        for fold in selection['encoding_audit']:
            self.assertFalse(set(fold['training_users'])&set(fold['encoding_users']))
            self.assertTrue(set(fold['encoding_users'])<=set(report['split']['train']))
        self.assertFalse(set(report['split']['train'])&set(report['split']['test']))
        records=pd.read_csv(ROOT/'artifacts/hybrid_test_events.csv')
        hybrid=records[records.model=='FreshMatch Hybrid'].reset_index(drop=True)
        for row in report['test_metrics']:
            frame=records[records.model==row['model']].reset_index(drop=True)
            pd.testing.assert_frame_equal(hybrid[['user','query']],frame[['user','query']])
            self.assertAlmostEqual(frame.ndcg_at_k.mean(),row['ndcg_at_k'])
            self.assertTrue(set(frame.user)<=set(report['split']['test']))
        for pair in report['paired_comparisons']:
            base=records[records.model==pair['baseline']].reset_index(drop=True)
            delta=hybrid[['user']].copy();delta['value']=hybrid.ndcg_at_k-base.ndcg_at_k
            np.testing.assert_allclose(cluster_interval(delta,'value'),[pair['ci_low'],pair['ci_high']])
            self.assertAlmostEqual(delta.value.mean(),pair['ndcg_difference'])

class FreshHoldoutTests(unittest.TestCase):
    def test_fresh_households_and_frozen_checkpoint(self):
        if not (ROOT/'artifacts/fresh_holdout_report.json').exists():self.skipTest('Fresh holdout has not been evaluated')
        if json.loads((ROOT/'artifacts/manifest.json').read_text())['source']!='Instacart':
            self.skipTest('Real-data holdout belongs to the real checkpoint, not demo training')
        report=json.loads((ROOT/'artifacts/fresh_holdout_report.json').read_text())
        protocol=json.loads((ROOT/'artifacts/fresh_holdout_protocol.json').read_text())
        self.assertFalse(set(report['sampled_households'])&set(protocol['excluded_development_users']))
        self.assertEqual(len(report['sampled_households']),5000)
        self.assertEqual(hashlib.sha256((ROOT/'artifacts/fresh_holdout_protocol.json').read_bytes()).hexdigest(),report['protocol_sha256'])
        for name,digest in protocol['frozen_files_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/'artifacts'/name).read_bytes()).hexdigest(),digest)
        records=pd.read_csv(ROOT/'artifacts/fresh_holdout_events.csv')
        hybrid=records[records.model=='FreshMatch Hybrid'].reset_index(drop=True)
        for metric in report['test_metrics']:
            frame=records[records.model==metric['model']].reset_index(drop=True)
            pd.testing.assert_frame_equal(hybrid[['user','query']],frame[['user','query']])
            self.assertTrue(set(frame.user)<=set(report['sampled_households']))
            self.assertEqual(len(frame),metric['events'])
            self.assertAlmostEqual(frame.ndcg_at_k.mean(),metric['ndcg_at_k'])
            self.assertAlmostEqual(frame.hit_rate.mean(),metric['hit_rate'])
        for pair in report['paired_comparisons']:
            base=records[records.model==pair['baseline']].reset_index(drop=True)
            delta=hybrid[['user']].copy();delta['value']=hybrid.ndcg_at_k-base.ndcg_at_k
            np.testing.assert_allclose(cluster_interval(delta,'value'),[pair['ci_low'],pair['ci_high']])

if __name__=='__main__':unittest.main()
