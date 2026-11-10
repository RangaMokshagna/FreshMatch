"""Directional, household-cross-fitted behavioral ranking and validation-only blending."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from xgboost import XGBRanker
from advanced_ml import household_split, switching_events, ranking_records, cluster_interval, _training_arrays


def transition_counts(events, n, allowed_users):
    """Only permitted households contribute; multi-target events have unit total mass."""
    allowed_users=set(allowed_users)
    counts=np.zeros((n,n),dtype=np.float64)
    for e in events:
        if e['user'] not in allowed_users:
            continue
        targets=sorted(set(e['targets'])-{e['query']})
        if targets:
            counts[e['query'],targets]+=1/len(targets)
    return counts


def transition_probability(counts, categories, alpha=25.):
    """Empirical-Bayes switching preference with an aisle-specific candidate prior."""
    counts=np.asarray(counts,dtype=float);categories=np.asarray(categories)
    if alpha<=0 or counts.shape!=(len(categories),len(categories)) or not np.isfinite(counts).all() or (counts<0).any():
        raise ValueError('Nonnegative finite square counts and positive smoothing are required.')
    same=categories[:,None]==categories[None,:]
    weights=(counts.sum(axis=0)+1)[None,:]*same
    np.fill_diagonal(weights,0)
    prior=np.divide(weights,weights.sum(1,keepdims=True),out=np.zeros_like(weights),where=weights.sum(1,keepdims=True)>0)
    values=(counts+alpha*prior)/(counts.sum(1,keepdims=True)+alpha)
    return np.where(same,values,0),prior


def query_percentiles(scores, eligible):
    """Normalize within each query without breaking equal-score ties."""
    scores=np.asarray(scores);eligible=np.asarray(eligible,dtype=bool)
    if scores.shape!=eligible.shape or not np.isfinite(scores[eligible]).all():
        raise ValueError('Score shape and finite eligible values are required.')
    out=np.zeros(scores.shape,dtype=np.float32)
    for q in range(len(scores)):
        ids=np.flatnonzero(eligible[q]);ids=ids[ids!=q]
        if len(ids):out[q,ids]=rankdata(scores[q,ids],method='average')/len(ids)
    return out


def directed_features(products, matrices, counts):
    n=len(products);cat=products.category.to_numpy();brand=products.brand.to_numpy()
    pop=products.popularity.to_numpy(float);prices=products.price.to_numpy(float);reorder=products.reorder_rate.to_numpy(float)
    p,prior=transition_probability(counts,cat)
    aa,bb=np.indices((n,n))
    columns={
        'same_brand':(brand[aa]==brand[bb]),'name_similarity':matrices['text'],
        'shopping_context':matrices['context'],'log_lift':np.log1p(np.minimum(matrices['lift'],20)),
        'price_ratio':np.minimum(prices[aa],prices[bb])/np.maximum(prices[aa],prices[bb]),
        'candidate_popularity':np.log1p(pop[bb]),'query_popularity':np.log1p(pop[aa]),
        'candidate_reorder':reorder[bb],'query_reorder':reorder[aa],
        'candidate_relative_price':np.minimum(prices[bb]/prices[aa],10),
        'switch_preference':p,'reverse_switch_preference':p.T,
        'switch_evidence':np.log1p(counts),'candidate_switch_prior':prior,
        'weak_suitability':np.maximum(matrices['scores'],0)}
    return np.stack(list(columns.values()),axis=-1).astype(np.float32),list(columns)


def cross_fitted_training(events, products, matrices, train_users, folds=3):
    """A training household never supplies its own transition-encoding targets."""
    users=np.asarray(sorted(train_users),dtype=int)
    blocks=[set(block.tolist()) for block in np.array_split(np.random.default_rng(42).permutation(users),folds)]
    xs=[];ys=[];groups=[];audit=[]
    for block in blocks:
        evidence_users=set(train_users)-block
        counts=transition_counts(events,len(products),evidence_users)
        cube,_=directed_features(products,matrices,counts)
        own=[e for e in events if e['user'] in block]
        x,y,g=_training_arrays(own,matrices['eligible'],cube)
        xs.append(x);ys.append(y);groups.append(g)
        audit.append(dict(training_users=sorted(block),encoding_users=sorted(evidence_users),groups=len(g)))
    return np.concatenate(xs),np.concatenate(ys),np.concatenate(groups),audit


def fit_and_select(products, matrices, historical, valid, splits, output):
    """This function deliberately receives no test events."""
    x,y,groups,encoding_audit=cross_fitted_training(historical,products,matrices,splits['train'])
    counts=transition_counts(historical,len(products),splits['train'])
    cube,names=directed_features(products,matrices,counts)
    eligible=matrices['eligible'];categories=products.category.to_numpy()
    pop=np.broadcast_to(products.popularity.to_numpy(),eligible.shape)
    prior,_=transition_probability(counts,categories)
    pop_rank=query_percentiles(pop,eligible);prior_rank=query_percentiles(prior,eligible)
    parameters=[dict(max_depth=d,n_estimators=t) for d in [2,4] for t in [120,240]]
    model_trials=[];models=[];score_matrices=[]
    for params in parameters:
        model=XGBRanker(objective='rank:ndcg',eval_metric='ndcg@5',learning_rate=.05,tree_method='hist',
                        n_jobs=2,random_state=42,**params)
        model.fit(x,y,group=groups)
        scores=model.predict(cube.reshape(-1,cube.shape[-1])).reshape(eligible.shape)
        score=float(ranking_records(scores,eligible,valid,categories).ndcg_at_k.mean())
        print('Validation directional ranker:',params,score,flush=True)
        model_trials.append(dict(**params,validation_ndcg_at_5=score));models.append(model);score_matrices.append(scores)
    best=max(range(len(parameters)),key=lambda i:model_trials[i]['validation_ndcg_at_5'])
    learned=query_percentiles(score_matrices[best],eligible)
    trials=[];blends=[]
    for learned_weight in [.25,.5,.75,1.]:
        for transition_fraction in ([0.,.5,1.] if learned_weight<1 else [0.]):
            transition_weight=(1-learned_weight)*transition_fraction
            popularity_weight=1-learned_weight-transition_weight
            values=learned_weight*learned+transition_weight*prior_rank+popularity_weight*pop_rank
            score=float(ranking_records(values,eligible,valid,categories).ndcg_at_k.mean())
            trials.append(dict(learned_weight=learned_weight,transition_weight=transition_weight,
                               popularity_weight=popularity_weight,validation_ndcg_at_5=score))
            blends.append(values)
    selected=max(range(len(trials)),key=lambda i:trials[i]['validation_ndcg_at_5'])
    popularity_validation=float(ranking_records(pop,eligible,valid,categories).ndcg_at_k.mean())
    # Deploy a changed ranking only if it passes this validation gate, never a test-score gate.
    deploy=trials[selected]['validation_ndcg_at_5']>popularity_validation
    selected_scores=blends[selected]
    base_hashes={name:hashlib.sha256((output/name).read_bytes()).hexdigest() for name in ['products.csv','matrices.npz'] if (output/name).exists()}
    selection=dict(base_files_sha256=base_hashes,protocol_version='directional-hybrid-v1',seed=42,primary_metric='NDCG@5',
        selected_parameters=parameters[best],model_trials=model_trials,hybrid_trials=trials,
        selected_weights=trials[selected],popularity_validation_ndcg=popularity_validation,
        deploy_hybrid=deploy,feature_names=names,encoding_audit=encoding_audit,
        train_groups=len(groups),train_rows=len(y),
        evidence_households=sorted(splits['train']),validation_households=sorted(splits['validation']),
        comparison_policy='Unchanged same-aisle/low-lift candidate pool for every method',
        test_disclosure='Retrospective development benchmark: earlier outcomes on this dataset were inspected. No new independent-test claim.',
        selection_rule='Best validation NDCG@5; hybrid deployment requires validation NDCG above popularity. No test metric selects weights or parameters.')
    output.mkdir(parents=True,exist_ok=True)
    # Persist all selection decisions before test evaluation starts.
    (output/'hybrid_selection.json').write_text(json.dumps(selection,indent=2))
    models[best].save_model(output/'hybrid_ranker.ubj')
    return selection,selected_scores,score_matrices[best],prior,pop


def run_improvement(products, history, history_orders, final_events, matrices, output, synthetic=False):
    output=Path(output)
    splits=household_split(history_orders.user_id.unique())
    historical=switching_events(history,history_orders,products,synthetic)
    train=[e for e in historical if e['user'] in splits['train']]
    valid=[e for e in final_events if e['user'] in splits['validation']]
    if not valid:raise ValueError('No validation events.')
    selection,hybrid,directional,prior,pop=fit_and_select(products,matrices,train,valid,splits,output)
    frozen=(output/'hybrid_selection.json').read_bytes()
    selection_hash=hashlib.sha256(frozen).hexdigest()
    test=[e for e in final_events if e['user'] in splits['test']]
    if not test:raise ValueError('No test events.')
    methods={'FreshMatch Hybrid':hybrid,'Directional LambdaMART':directional,
             'Smoothed purchase switches':prior,'Popularity':pop,
             'Weak-label classifier':matrices['scores'],'Content similarity':matrices['text'],
             'Shopping context':matrices['context']}
    old_path=output/'advanced_scores.npz'
    if old_path.exists():
        with np.load(old_path,allow_pickle=False) as data:methods['Original LambdaMART']=data['scores']
    records={};rows=[];paired=[]
    categories=products.category.to_numpy()
    for name,values in methods.items():
        frame=ranking_records(values,matrices['eligible'],test,categories)
        records[name]=frame
        low,high=cluster_interval(frame,'ndcg_at_k')
        rows.append(dict(model=name,**frame[['precision_at_k','recall_at_k','ndcg_at_k','map_at_k','hit_rate','target_coverage']].mean().to_dict(),
                         ndcg_ci_low=low,ndcg_ci_high=high,events=len(frame),households=int(frame.user.nunique())))
    for name,frame in records.items():
        if name=='FreshMatch Hybrid':continue
        delta=records['FreshMatch Hybrid'][['user','query']].copy()
        pd.testing.assert_frame_equal(delta.reset_index(drop=True),frame[['user','query']].reset_index(drop=True))
        delta['difference']=records['FreshMatch Hybrid'].ndcg_at_k-frame.ndcg_at_k
        low,high=cluster_interval(delta,'difference')
        paired.append(dict(baseline=name,ndcg_difference=float(delta.difference.mean()),ci_low=low,ci_high=high))
    np.savez_compressed(output/'hybrid_scores.npz',scores=hybrid.astype(np.float32),eligible=matrices['eligible'],
                        learned=query_percentiles(directional,matrices['eligible']),
                        transitions=query_percentiles(prior,matrices['eligible']),popularity=query_percentiles(pop,matrices['eligible']))
    events=pd.concat([f.assign(model=name) for name,f in records.items()],ignore_index=True)
    events.to_csv(output/'hybrid_test_events.csv',index=False)
    report=dict(version='1.0',source='Synthetic grocery simulation' if synthetic else 'Instacart',
        selection_sha256=selection_hash,selection=selection,test_metrics=rows,paired_comparisons=paired,
        split={k:sorted(v) for k,v in splits.items()},validation_events=len(valid),test_events=len(test),
        limitations=[selection['test_disclosure'],'Historical catalogue features remain transductive.',
            'Observed same-aisle purchase switches are proxy relevance, not confirmed substitutes.',
            'Transition features are encoded out of household for fitting and use only training households for predictions.',
            'Candidate eligibility is unchanged; coverage remains a limitation.',
            'No guarantee of real stockout recovery, dietary equivalence or purchase acceptance.'])
    assert frozen==(output/'hybrid_selection.json').read_bytes()
    (output/'hybrid_report.json').write_text(json.dumps(report,indent=2))
    print(pd.DataFrame(rows).to_string(index=False),flush=True)
    print('Paired comparisons:',paired,flush=True)
    return report
