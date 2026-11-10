"""One frozen evaluation on 5,000 previously unused households; never fits a model."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from advanced_ml import switching_events,ranking_records,cluster_interval

if __name__=='__main__':
    art=ROOT/'artifacts'
    source_manifest=json.loads((art/'manifest.json').read_text())['data_provenance']['files']
    source_hashes={}
    for name in ['orders.csv','order_products__prior.csv']:
        digest=hashlib.sha256()
        with (ROOT/'instacart'/name).open('rb') as handle:
            for block in iter(lambda:handle.read(1024*1024),b''):digest.update(block)
        if digest.hexdigest()!=source_manifest[name]['sha256']:
            raise SystemExit('Source CSV hash differs from the original dataset: '+name)
        source_hashes[name]=digest.hexdigest()
    development=json.loads((art/'hybrid_report.json').read_text())
    old_users=set().union(*(set(ids) for ids in development['split'].values()))
    model_files=['hybrid_selection.json','hybrid_scores.npz','matrices.npz','advanced_scores.npz','products.csv']
    hashes={name:hashlib.sha256((art/name).read_bytes()).hexdigest() for name in model_files}
    protocol=dict(version='fresh-households-v1',seed=20261110,households=5000,
        excluded_development_users=sorted(old_users),frozen_files_sha256=hashes,
        primary_model='FreshMatch Hybrid',primary_metric='NDCG@5',
        candidate_policy='Unchanged same-aisle, lift below 1.5; same pool for all methods',
        selection='Model parameters and weights were fixed on original validation households before these evaluation households were read.',
        disclosure='Fresh, disjoint household holdout from the same public dataset; not a new external or prospective retail dataset.')
    protocol_path=art/'fresh_holdout_protocol.json'
    if protocol_path.exists():
        if json.loads(protocol_path.read_text())!=protocol:
            raise SystemExit('Frozen holdout protocol differs. Do not reuse this holdout for model tuning.')
    else:
        protocol_path.write_text(json.dumps(protocol,indent=2))
    frozen=protocol_path.read_bytes()
    orders=pd.read_csv(ROOT/'instacart/orders.csv',usecols=['order_id','user_id','order_number','eval_set'])
    prior=orders[orders.eval_set=='prior'].copy()
    sizes=prior.groupby('user_id').size()
    available=np.asarray(sorted(set(sizes[sizes>=4].index)-old_users))
    users=set(np.random.default_rng(protocol['seed']).choice(available,protocol['households'],replace=False).tolist())
    assert not users&old_users
    window=prior[prior.user_id.isin(users)].sort_values(['user_id','order_number']).groupby('user_id').tail(2)
    wanted=set(window.order_id)
    final_ids=set(window.loc[window.groupby('user_id').order_number.idxmax(),'order_id'])
    products=pd.read_csv(art/'products.csv');ids=set(products.product_id)
    chunks=[]
    with pd.read_csv(ROOT/'instacart/order_products__prior.csv',usecols=['order_id','product_id','reordered'],chunksize=1_000_000) as reader:
        for chunk in reader:
            part=chunk[chunk.order_id.isin(wanted)&chunk.product_id.isin(ids)]
            if not part.empty:chunks.append(part)
    lines=pd.concat(chunks,ignore_index=True)
    events=[e for e in switching_events(lines,window,products) if e['target_order'] in final_ids]
    if not events:raise SystemExit('No holdout switching events.')
    with np.load(art/'matrices.npz',allow_pickle=False) as data:base={k:data[k] for k in data.files}
    with np.load(art/'hybrid_scores.npz',allow_pickle=False) as data:hybrid={k:data[k] for k in data.files}
    with np.load(art/'advanced_scores.npz',allow_pickle=False) as data:original=data['scores']
    methods={'FreshMatch Hybrid':hybrid['scores'],
             'Popularity':np.broadcast_to(products.popularity.to_numpy(),base['eligible'].shape),
             'Content similarity':base['text'],'Shopping context':base['context'],
             'Weak-label classifier':base['scores'],'Original LambdaMART':original,
             'Directional LambdaMART':hybrid['learned']}
    frames={};rows=[];paired=[]
    for name,values in methods.items():
        frame=ranking_records(values,base['eligible'],events,products.category.to_numpy())
        frames[name]=frame
        low,high=cluster_interval(frame,'ndcg_at_k')
        rows.append(dict(model=name,**frame[['ndcg_at_k','precision_at_k','recall_at_k','map_at_k','hit_rate','target_coverage']].mean().to_dict(),
                         ndcg_ci_low=low,ndcg_ci_high=high,events=len(frame),households=int(frame.user.nunique())))
    for name,frame in frames.items():
        if name=='FreshMatch Hybrid':continue
        pd.testing.assert_frame_equal(frames['FreshMatch Hybrid'][['user','query']],frame[['user','query']])
        delta=frame[['user']].copy();delta['difference']=frames['FreshMatch Hybrid'].ndcg_at_k-frame.ndcg_at_k
        low,high=cluster_interval(delta,'difference')
        paired.append(dict(baseline=name,ndcg_difference=float(delta.difference.mean()),ci_low=low,ci_high=high))
    report=dict(source='Instacart',source_csv_sha256=source_hashes,protocol_sha256=hashlib.sha256(frozen).hexdigest(),sampled_households=sorted(users),
        test_events=len(events),test_metrics=rows,paired_comparisons=paired,disclosure=protocol['disclosure'],
        limitations=['Eligibility and catalogue remain fixed to the original study; results concern observed same-aisle switches, not expert substitution labels.',
                     'The method was developed after earlier benchmark results; this evaluation uses different households whose final labels did not select parameters.',
                     'A positive point estimate alone does not establish superiority when the paired interval includes zero.'])
    pd.concat([f.assign(model=name) for name,f in frames.items()],ignore_index=True).to_csv(art/'fresh_holdout_events.csv',index=False)
    (art/'fresh_holdout_report.json').write_text(json.dumps(report,indent=2))
    assert frozen==protocol_path.read_bytes()
    for name,expected in hashes.items():assert hashlib.sha256((art/name).read_bytes()).hexdigest()==expected
    manifest=json.loads((art/'manifest.json').read_text())
    for name in ['fresh_holdout_protocol.json','fresh_holdout_report.json','fresh_holdout_events.csv']:
        manifest['sha256'][name]=hashlib.sha256((art/name).read_bytes()).hexdigest()
    (art/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(pd.DataFrame(rows).to_string(index=False))
    print('Paired comparisons:',paired)
