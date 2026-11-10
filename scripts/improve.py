"""Reproduce the directional hybrid experiment using current real-data artifacts."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from real_data import load_instacart, provenance
from advanced_ml import switching_events
from hybrid_ranker import run_improvement

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=ROOT/'instacart')
    args=parser.parse_args()
    products=pd.read_csv(ROOT/'artifacts/products.csv')
    manifest=json.loads((ROOT/'artifacts/manifest.json').read_text())
    audit=provenance(args.data_dir)
    if manifest.get('data_provenance',{}).get('files')!=audit['files']:
        raise SystemExit('Source CSV hashes differ from the existing inference artifacts. Run scripts/train.py first.')
    original,orders,lines=load_instacart(args.data_dir)
    if original.product_id.tolist()!=products.product_id.tolist():
        raise SystemExit('Catalogue IDs differ. Regenerate base artifacts before improvement.')
    last=orders.groupby('user_id').order_number.transform('max')
    historical_orders=orders[orders.order_number<last].copy()
    history=lines[lines.order_id.isin(historical_orders.order_id)].copy()
    final_ids=set(orders.loc[orders.order_number==last,'order_id'])
    final_events=[e for e in switching_events(lines,orders,products) if e['target_order'] in final_ids]
    with np.load(ROOT/'artifacts/matrices.npz',allow_pickle=False) as z:matrices={k:z[k] for k in z.files}
    run_improvement(products,history,historical_orders,final_events,matrices,ROOT/'artifacts')
    for name in ['hybrid_selection.json','hybrid_report.json','hybrid_scores.npz','hybrid_test_events.csv']:
        manifest['sha256'][name]=hashlib.sha256((ROOT/'artifacts'/name).read_bytes()).hexdigest()
    manifest['hybrid_experiment']={'report':'hybrid_report.json','scores':'hybrid_scores.npz'}
    selection=json.loads((ROOT/'artifacts/hybrid_selection.json').read_text())
    manifest['main_ranking_model']='FreshMatch Hybrid' if selection['deploy_hybrid'] else 'Weak-label suitability'
    (ROOT/'artifacts/manifest.json').write_text(json.dumps(manifest,indent=2))
