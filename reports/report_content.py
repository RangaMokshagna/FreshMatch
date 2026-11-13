"""Report content built from the project's recorded real-data evidence."""
from pathlib import Path
import json,csv
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts'
FRESH=json.loads((ART/'fresh_holdout_report.json').read_text())
HYBRID=json.loads((ART/'hybrid_selection.json').read_text())
OLD=json.loads((ART/'advanced_report.json').read_text())
META=json.loads((ART/'manifest.json').read_text())
with (ART/'comparison.csv').open() as f:CLASSIFIERS=list(csv.DictReader(f))
AUTHORS=[('K. Darshan Sai','RA2311027010002'),('J. Ranga Mokshagna','RA2311027010003'),('P. Bharat Sai','RA2311027010007')]
TITLE='FRESHMATCH: AI-POWERED PRODUCT SUBSTITUTION DISCOVERY AND INTELLIGENT ALTERNATIVE RECOMMENDATION USING MACHINE LEARNING'
PAGES=[]
def page(title='',chapter=None,blocks=None):
 d={'title':title,'chapter':chapter,'blocks':blocks or []};PAGES.append(d);return d

def p(t):return {'type':'p','text':t}
def h(t):return {'type':'h','text':t}
def bullets(items):return {'type':'bullets','items':items}
def table(id,title,headers,rows,widths=None):return {'type':'table','id':id,'title':title,'headers':headers,'rows':rows,'widths':widths}
def figure(id,title,path,height):return {'type':'figure','id':id,'title':title,'path':path,'height':height}
def code(t):return {'type':'code','text':t}
def eq(t):return {'type':'equation','text':t}

# Front matter mirrors the reference order. Faculty names are profile-driven.
for kind,title in [('cover','TITLE PAGE'),('declaration','OWN WORK DECLARATION FORM'),('certificate','BONAFIDE CERTIFICATE'),('acknowledgements','ACKNOWLEDGEMENTS')]:
 page(title,blocks=[{'type':kind}])
page('ABSTRACT',blocks=[
p('FreshMatch is a grocery substitution workbench that helps a user explore possible replacements when a preferred product is unavailable. It combines real Instacart purchase records, product information and historical shopping patterns in a Streamlit application. The development study uses 320 products across 51 aisles and 3,000 anonymous customer accounts, with 49,760 historical baskets and 3,000 final available prior orders kept aside for evaluation.'),
p('Apriori and FP-Growth identify frequent co-purchases, while six classifiers learn rule-based suitability labels. XGBoost is selected for the separate suitability signal. An improved directional LambdaMART model adds candidate popularity, repeat-purchase rates and historical switching preferences. Transition features are encoded using other training households so that a household does not supply the outcomes used to encode its own training rows. Validation selects a blend of 75% learned ranking and 25% popularity after both components are converted to comparable within-query ranks.'),
p('The selected configuration is frozen before checking 5,000 previously unused households. Their last two available prior orders produce 4,594 switching examples from 1,888 qualifying accounts. FreshMatch Hybrid records NDCG@5 of 0.1344, compared with 0.1326 for popularity and 0.1173 for the original ranker. The relative gain over the original ranker is 14.6%. Its small lead over popularity is not statistically conclusive: the paired 95% household-bootstrap interval for the difference includes zero.'),
p('The project provides seven application pages, reproducible training scripts, source-file fingerprints and 29 passing software tests. Prices remain estimates, brand labels are name-token proxies, and later same-aisle purchases are only evidence of possible substitution. The report therefore presents FreshMatch as an auditable research system rather than proof of dietary equivalence or actual recovered sales.'),
p('<b>Keywords:</b> Grocery substitution, Instacart, hybrid recommendation, LambdaMART, XGBoost, association mining, NDCG@5, Streamlit.')])
for kind,title in [('contents','TABLE OF CONTENTS'),('figures','LIST OF FIGURES'),('tables','LIST OF TABLES'),('abbreviations','ABBREVIATIONS')]:page(title,blocks=[{'type':kind}])

page('INTRODUCTION',1,[
h('1.1 Introduction to the Project'),
p('A shopper who cannot find a preferred grocery product still needs to complete the basket. Searching manually through similar names can be slow, and a frequently purchased item may not serve the same purpose as the missing product. FreshMatch brings product information and purchase history together so that the user can inspect possible alternatives in one place.'),
p('For example, a shopper looking for Organic Milk may want to compare other milk products by estimated price, purchase patterns and availability. The application provides a ranked list, a separate suitability score and a plain-language reason. The user makes the final choice; the system does not decide whether a product is safe for a particular diet.'),
h('1.2 Problem Statement'),
p('The task is to rank plausible replacements from a known catalogue while excluding the original product, declared outages and products above the user\'s price limit. The available dataset records purchases, but it does not say that a particular purchase was a deliberate replacement. The modelling problem therefore requires a clear distinction between heuristic suitability and observed changes in purchasing.'),
p('FreshMatch addresses this problem through two connected learning tasks. Classifiers estimate agreement with rule-based product-pair labels. A behavioral ranker learns how to order candidates using historical purchase changes. Their outputs are checked against simple alternatives, including popularity, rather than assuming that a more complex model must perform better.'),
h('1.3 Motivation'),
p('The project is motivated by a practical need for useful, explainable suggestions. A recommendation becomes easier to assess when a shopper can see why it was listed, apply a budget, and remove unavailable items. The same transparency is valuable for a technical reviewer: source data, model selection and evaluation boundaries should be visible and reproducible.')])

page(blocks=[h('1.4 Objectives'),bullets([
'Prepare real grocery purchase records and retain an auditable record of the input files and sampling settings.',
'Separate products often bought together from products that may serve as alternatives.',
'Compare six suitability classifiers under the same product-disjoint evaluation protocol.',
'Learn directional ranking signals from historical switches without using a household to encode its own training targets.',
'Select a hybrid on validation data, freeze its settings, and assess it on previously unused households.',
'Build an interface for search, stockout scenarios, product exploration, relationships and model evidence.',
'Report strong baselines, uncertainty and remaining limitations alongside the measured improvement.']),
h('1.5 Scope and Deliverables'),
p('The scope is an offline research prototype using a bounded catalogue from the Instacart dataset [1]. The deliverables include an executable notebook, reusable Python modules, inference tables and arrays, an interactive Streamlit website, automated checks, an evaluation report and a presentation. The application reads prepared inference artifacts, so browsing recommendations does not require retraining a model.'),
p('A household in this report means one anonymous customer account identified by user_id. It is not a verified family. The system is also query-based: it gives a product-level ranking rather than a personalized recommendation based on a logged-in shopper\'s private history.'),
h('1.6 Contribution of the Work'),
p('The contribution is the complete and inspectable workflow: consistent data preparation, complementary-item mining, suitability modelling, improved behavioral ranking, a validation-selected blend, and fair comparison on fixed candidate pools. The improved model is called Directional LambdaMART because of its directional features; this name describes the project implementation, not a new standard algorithm.'),
p('The final system keeps the ranking score separate from the displayed XGBoost suitability score. This avoids presenting either number as a customer\'s probability of accepting a replacement. The project repository and exported evidence make these decisions available for review [2].')])

page('BACKGROUND AND RELATED WORK',2,[h('2.1 Recommendation Methods and Popularity'),
p('Recommendation systems use information about users, items or interactions to decide what to show. In this project, a query product is the item needing an alternative, and the candidate is a possible replacement. A simple popularity baseline orders allowed candidates by historical purchase frequency. It is easy to understand and provides a demanding reference when common items account for much of the observed purchasing.'),
p('Name similarity offers another baseline. TF-IDF represents product names as weighted terms, and cosine similarity compares their vectors [12]. This can identify shared descriptions, but similar words do not establish equal pack size, ingredients or intended use. Shopping-context similarity instead compares patterns of co-purchase around products.'),
h('2.2 Apriori and FP-Growth'),
p('Apriori discovers frequent itemsets by generating and checking candidate combinations [3]. FP-Growth compresses transactions into a tree and mines frequent patterns without the same candidate-generation process [4]. Both are used here on identical historical baskets, support and maximum itemset length. Agreement between their itemsets provides a useful implementation check.'),
p('A strong association normally describes products purchased together. Bread and butter are an illustrative complement pair, not necessarily substitutes. FreshMatch therefore uses association information as relationship evidence and applies a low-direct-lift eligibility rule to possible replacements. Co-purchase alone is not treated as proof that two products can replace each other.'),
h('2.3 Suitability Classification and Calibration'),
p('Random Forest, Gradient Boosting, Logistic Regression, XGBoost, an MLP classifier and soft voting are compared using the same retained pair partitions. XGBoost is a tree-boosting implementation with efficient training and regularisation [6]. Sigmoid calibration maps classifier outputs to observed weak-label frequencies. Calibration is evaluated with Brier loss, log loss and expected calibration error; it does not turn weak labels into verified shopper acceptance [8,9].')])

page(blocks=[h('2.4 Learning to Rank and LambdaMART'),
p('Learning to rank addresses the order of several candidates rather than only whether one candidate belongs to a class. LambdaMART combines LambdaRank-style ranking updates with boosted decision trees [5]. In FreshMatch it is implemented using XGBRanker with the rank:ndcg objective. The model learns from groups of candidates associated with the same query and purchase-change event.'),
p('Direction matters. Replacing product A with B need not have the same preference strength as replacing B with A. The improved model therefore includes candidate-specific popularity and reorder rates, a directional price relationship, and historical switching evidence in both directions. These extend the earlier ranker, whose pair-comparison features were largely symmetric.'),
h('2.5 Hybrid Ranking'),
p('Learned scores and raw purchase counts are on different scales. FreshMatch converts each component into a percentile rank within the allowed candidate pool, using average ranks for ties. A weighted sum then combines the learned ordering with popularity. The final 75/25 choice is selected from predefined candidates on validation NDCG@5, rather than chosen after looking at the new holdout.'),
p('The combination preserves a useful signal from common purchases while allowing the model to favour a candidate for a particular query. A popularity method can still be strong, so the report retains it as a separately measured baseline. The selected blend is an empirical choice for this study, not a universal rule for grocery recommendation.'),
h('2.6 Evaluation Principles'),
p('NDCG rewards placing relevant items earlier in a recommendation list [7]. Precision, recall, mean average precision and hit rate describe other parts of ranking quality. A single metric cannot establish correctness for every shopper or product category. FreshMatch reports multiple measures and uses household-level bootstrap sampling to reflect that several examples can come from the same account [11].'),
p('The project follows three evaluation boundaries: product-disjoint partitions for weak-label classification, separate households for ranker fitting and validation, and a frozen new-household holdout for the final improvement. Their populations and purposes differ, so their scores are not combined into one accuracy claim.')])

page('DATASET AND METHODOLOGY',3,[h('3.1 Source Dataset and Required Files'),
p('The project uses Instacart purchase records from the community dataset supplied with the project [1]. The uploaded source contains 49,688 products, 134 aisles and 21 departments. Five CSV files are required. The additional order_products__train.csv is present in Git LFS but is not consumed by this experiment.'),
table('3.1','Required Instacart files and fields used',['File','Fields used / role'],[
['products.csv','product_id, product_name, aisle_id, department_id; catalogue and lookup keys.'],
['orders.csv','order_id, user_id, order_number, eval_set; account membership and sequence.'],
['order_products__prior.csv','order_id, product_id, reordered; contents of prior baskets.'],
['aisles.csv','aisle_id, aisle; category names for eligible alternatives.'],
['departments.csv','department_id, department; broader product grouping.']],[156,328]),
h('3.2 Study Sample and Derived Information'),
p('Whole customer accounts with at least four prior orders are sampled with a fixed seed. Catalogue selection uses historical purchase counts only. Product IDs index records and score matrices; they are not continuous numerical predictors. Popularity and reorder rate are derived from history. Price is a deterministic estimate, while brand is an unverified first-word proxy.'),
table('3.2','Recorded development sample',['Quantity','Recorded value'],[
['Development households','3,000 anonymous accounts'],['Selected catalogue','320 products across 51 aisles'],['Historical baskets','49,760'],['Held-out final prior baskets','3,000'],['Classifier pair sample','2,036 training / 266 test / 1,532 purged'],['New evaluation sample','5,000 additional, disjoint accounts']],[272,212])])

page(blocks=[h('3.3 Temporal and Household Boundaries'),
p('For each development account, the final available prior order is held out. Earlier prior orders form history. This is an order-sequence holdout; it is not Kaggle\'s hidden competition test and it does not establish a global calendar-time split. Observed switches are formed when an item in an earlier basket disappears and a same-aisle product appears in the following basket.'),
table('3.3','Ranking partitions and observed evaluation examples',['Partition','Accounts','Use / qualifying examples'],[
['Ranker training','2,100','Historical transitions fit the ranker.'],['Validation','450','384 final-order examples select configuration.'],['Original test (reference)','450','365 examples; later treated as retrospective.'],['New holdout, sampled','5,000','No overlap with all 3,000 development accounts.'],['New holdout, active','1,888','4,594 qualifying switching examples.']],[170,62,252]),
h('3.4 Features, Eligibility and Evaluation Units'),
p('Historical context, names and purchase counts are shared across the original development catalogue, so the earlier experiment is transductive. Transition encodings use only training households and exclude the fitted household. None of the additional 5,000 accounts supplies feature-fitting or model-selection information. Every compared method uses the same eligible candidates: same aisle/category, direct lift below 1.5, with self-matches excluded.'),
figure('3.1','FreshMatch end-to-end workflow','reports/assets/workflow.png',164),
p('An evaluation event is a qualifying purchase change, not one customer and not a confirmed replacement. Multiple events may belong to a customer. Targets excluded by eligibility remain in recall and NDCG denominators, so limited coverage is visible rather than hidden.')])

page('NOTEBOOK IMPLEMENTATION',4,[h('4.1 Data Loading, Validation and Provenance'),
p('The loader checks required files and columns before training. It also checks catalogue identifiers, aisle/department references, sampled purchase references, reorder flags, duplicate order/product pairs and completeness of sampled orders. The large prior-purchase CSV is streamed in chunks instead of being loaded in one allocation. Git LFS pointers are rejected with an instruction to restore the real objects.'),
p('SHA-256 digests of all five inputs and the sampling settings are stored in the manifest. Changing a source file changes ingestion-cache identity. Real data is the default; missing data stops the run instead of silently generating synthetic records. An explicit synthetic option remains available for software testing, and its outputs are labelled separately.'),
code('source = validate_instacart(data_dir)\naudit = provenance(source, seed=42, max_products=320)\nproducts, orders, lines = load_instacart(source)\n# Separate the last prior order before fitting history features.'),
h('4.2 Historical Baskets and Association Mining'),
p('A sparse basket-product matrix represents the historical orders. Apriori and FP-Growth use support 0.0015, maximum itemset length two, and a directed-rule confidence cutoff of 0.025. The recorded itemsets must agree. Their measured runtimes are retained on cache hits rather than reported as new computation times.'),
table('4.1','Association-mining results from the recorded real-data run',['Algorithm','Seconds','Itemsets','Directed rules'],[['Apriori','6.1265','1,266','1,671'],['FP-Growth','76.4105','1,266','1,671']],[166,92,105,121]),
p('Apriori was faster in this bounded run. FP-Growth\'s general efficiency on other transaction structures does not guarantee a lower runtime here. Agreement in itemsets and rule counts is the key cross-check; association strength is still not a substitute label.')])

page(blocks=[h('4.3 Weak Labels and Six Classifiers'),
p('Positive pair labels require the same category, high category-relative context similarity and direct lift below 0.55. Negative examples include cross-category pairs, strong complements and difficult within-category examples; ambiguous pairs are excluded. These labels encode a modelling rule rather than an expert judgment.'),
p('The retained outer test contains 261 negative and only five positive labels. Product assignments are seeded and category-balanced, accepting only partitions with at least five examples of each class. Pairs crossing boundaries are purged, and both endpoints are disjoint between retained training and evaluation sets. The exact CV indices enter fitted-model cache identity.'),
table('4.2','Six-model suitability comparison (weak-label task)',['Model','CV AP','Test AP','Test F1'],[[r['Model'].replace('Soft Voting (RF + GB + XGB)','Soft voting (RF + GB + XGB)'),f"{float(r['CV PR-AUC']):.4f}",f"{float(r['PR-AUC']):.4f}",f"{float(r['F1']):.4f}"] for r in CLASSIFIERS],[235,83,83,83]),
p('All models share the three product-disjoint folds. Scaling for Logistic Regression and MLP stays inside their pipelines, and sigmoid calibration is fitted within the training protocol. XGBoost has the highest recorded training-CV average precision, 0.9083, and supplies the separate suitability signal. Test scores do not choose the classifier.'),
p('Average precision is reported as PR-AUC in the application. Because the positive test class is very small, the figures are fragile and should not be read as evidence of universal substitute quality. The main-card order now comes from the hybrid ranker, not from sorting these suitability probabilities alone.')])

feature_desc=[
['same_brand','Equality of unverified brand-name tokens.'],['name_similarity','TF-IDF cosine similarity of product names.'],['shopping_context','Similarity between historical co-purchase contexts.'],['log_lift','Log-transformed direct co-purchase lift.'],['price_ratio','Smaller estimated price divided by the larger.'],['candidate_popularity','Log historical purchase count of the candidate.'],['query_popularity','Log historical purchase count of the query.'],['candidate_reorder','Historical repeat-purchase rate of the candidate.'],['query_reorder','Historical repeat-purchase rate of the query.'],['candidate_relative_price','Candidate/query estimated price ratio, capped at 10.'],['switch_preference','Smoothed preference for moving from query to candidate.'],['reverse_switch_preference','Smoothed preference in the reverse direction.'],['switch_evidence','Log count of observed query-to-candidate switches.'],['candidate_switch_prior','Aisle-specific prior from training switching evidence.'],['weak_suitability','Nonnegative original weak-label suitability score.']]
page(blocks=[h('4.4 Directional LambdaMART and Its Inputs'),
p('The improved ranker adds information about the candidate itself rather than relying mainly on symmetric pair similarities. It is fitted using 8,840 informative candidate groups and 147,340 candidate rows. Groups with no eligible positive, no negative ordering or fewer than two candidates cannot provide the ranking signal used here.'),
table('4.3','Fifteen inputs to the improved directional ranker',['Input','Interpretation'],feature_desc,[174,310]),
h('4.5 Household-Cross-Fitted Transition Features'),
p('Training accounts are divided into three blocks. For each block, historical switching counts are built from the other two blocks and used to encode that block\'s rows. A household therefore cannot supply the outcomes that encode its own training features. Prediction-time transition evidence uses all 2,100 training accounts, never validation or evaluation accounts.'),
p('Multi-target events contribute one unit of total count mass, shared across their targets. Smoothing uses an aisle-specific candidate prior with strength 25. This supports rare query-product pairs while keeping historical evidence separate from the labels being fitted.')])

page(blocks=[h('4.6 Model Settings and Hybrid Score'),
table('4.4','Selected directional and hybrid settings',['Setting','Recorded value'],[['Implementation','XGBRanker / LambdaMART'],['Objective','rank:ndcg; validation metric NDCG@5'],['Maximum tree depth','4'],['Number of trees','120'],['Learning rate','0.05'],['Transition smoothing / encoding','Strength 25 / three household blocks'],['Seed / CPU threads','42 / 2'],['Blend weights','0.75 learned rank + 0.25 popularity rank']],[220,264]),
p('Each component is converted to a within-query percentile rank over the base eligible pool. Average ranks preserve ties. Larger values indicate a higher relative position; they are not buying probabilities. Validation selects the final weighted sum:'),
eq('Hybrid(q, c) = 0.75 × ML_percentile(q, c) + 0.25 × Popularity_percentile(q, c).'),
p('For illustration, a candidate with ML rank 0.90 and popularity rank 0.80 scores 0.875. Another with 0.70 and 1.00 scores 0.775. The first would appear earlier. These are hypothetical normalized ranks from a larger pool, not measured product predictions.'),
h('4.7 Serving and Reproducible Exports'),
p('The app applies price, same-aisle and outage restrictions and orders the remaining candidates by the fixed hybrid matrix. Its displayed XGBoost suitability and associated feature sensitivity remain separate signals. Product and matrix fingerprints must match before the hybrid is activated. Tables, JSON and numeric arrays support inference without loading an untrusted model pickle.'),
code('fit_directional_ranker(training_groups)\nselect_parameters_and_weights(validation_events)\nfreeze_selection_and_score_hashes()\nranked = allowed_candidates.sorted_by(hybrid_score, descending=True)'),
p('The notebook embeds the Python source modules. Synchronization checks protect edits; scripts/train.py and scripts/improve.py reproduce fitting, while the frozen holdout script refuses changed checkpoint hashes.')])

page('EXTENDED EXPERIMENTS',5,[h('5.1 Validation-Only Model and Blend Selection'),
p('The original 384 validation examples select both tree configuration and blend weights. Four directional candidates are fitted with learning rate 0.05. No new-household outcome is available to this stage.'),
table('5.1','Directional ranker configurations on validation data',['Depth','Trees','Validation NDCG@5'],[[str(r['max_depth']),str(r['n_estimators']),f"{r['validation_ndcg_at_5']:.6f}"] for r in HYBRID['model_trials']],[110,110,264]),
p('The best directional candidate has depth four and 120 trees. Ten predefined blends then combine learned, transition and popularity ranks. The selected 0.75/0/0.25 blend scores 0.135653, above popularity\'s validation score of 0.129128, and passes the deployment gate. Transition information still enters the learned model even when its direct blend weight is zero.'),
table('5.2','Predefined blends evaluated on validation data',['Learned','Transition','Popularity','NDCG@5'],[[f"{r['learned_weight']:.3f}",f"{r['transition_weight']:.3f}",f"{r['popularity_weight']:.3f}",f"{r['validation_ndcg_at_5']:.6f}"] for r in HYBRID['hybrid_trials']],[100,100,100,184]),
p('The old 365-example test was already inspected during development. Its hybrid result, 0.14039 versus popularity 0.14089, is retained as retrospective evidence rather than presented as a fresh test.')])

page(blocks=[h('5.2 Frozen New-Household Verification'),
p('After validation selection, a protocol fixes the primary NDCG@5 metric, seed 20261110, candidate rule, excluded development-account IDs and inference-file hashes. The next sample contains 5,000 accounts that do not overlap any of the 3,000 development accounts. Their last two available prior orders construct evaluation events; none of their histories fits features, switching evidence, models or blend weights.'),
figure('5.1','Development, freezing and new-household verification','reports/assets/evaluation.png',188),
p('The new sample yields 4,594 qualifying events from 1,888 accounts. Accounts without a qualifying purchase change do not create an event. This explains why 5,000 sampled households and 1,888 evaluated households are both correct. All methods score the same events and candidate pools, and excluded relevant targets remain in metric denominators.'),
h('5.3 Confidence and Test-Reuse Controls'),
p('The primary model and weights are not changed after reading the new results. Frozen file digests are checked again after evaluation. Replacing a checkpoint causes the verification script to refuse that protocol, helping prevent accidental reuse of a test for tuning. Source CSV digests are also compared with the recorded dataset manifest.'),
p('Confidence intervals resample whole households rather than individual rows. This retains dependence between several examples from the same account. The implementation uses 1,000 bootstrap draws and the 2.5th and 97.5th percentiles. Paired comparisons subtract method scores on matched events before the household bootstrap [11].')])

cal_rows=[[name.replace('Soft Voting (RF + GB + XGB)','Soft voting'),f"{r['brier']:.4f}",f"{r['log_loss']:.4f}",f"{r['ece']:.4f}"] for name,r in OLD['calibration'].items()]
page(blocks=[h('5.4 Ranking Measures and Feature-Removal Reference'),
p('At K = 5, precision is relevant hits divided by five, recall is hits divided by all observed targets, and hit rate records whether any target was found. MAP rewards relevant items appearing earlier. NDCG compares the achieved discounted gain with the ideal ordering [7]:'),
eq('DCG@5 = Σ (relᵣ / log₂(r + 1)), r = 1…5;   NDCG@5 = DCG@5 / IDCG@5.'),
p('NDCG is a ranking score from zero to one, not an accuracy percentage. The following feature-removal study belongs to the original LambdaMART experiment and is included as a labelled reference, not as an ablation of the new hybrid.'),
table('5.3','Original-ranker feature-removal study (validation reference)',['Experiment','Validation NDCG@5'],[[r['experiment'],f"{r['validation_ndcg_at_5']:.6f}"] for r in OLD['ablations']],[328,156]),
h('5.5 Calibration of the Separate Suitability Signal'),
table('5.4','Weak-label classifier calibration on 266 retained test pairs',['Classifier','Brier loss','Log loss','ECE'],cal_rows,[235,83,83,83]),
p('Lower values are preferred for these calibration/error measures. ECE uses ten equal-width bins and a sample-weighted probability/frequency gap. Only five test pairs have positive weak labels, so these diagnostics are noisy. They concern heuristic suitability, not actual replacement acceptance or the hybrid rank score.')])

# One complete, readable screenshot page per interface module.
app_pages=[
('6.1 Find Substitutes','01-find-substitutes.png','Find Substitutes with real-data alternatives and separate suitability scores.',[
'FreshMatch is implemented as a seven-page Streamlit application [10]. Find Substitutes is the main shopper-facing page. A user searches the catalogue, selects an item and reviews alternatives. The current order is set by the validation-approved hybrid, while price limits and declared outages remove candidates that cannot be shown.',
'The cards show product names, estimated prices, reasons and a separate XGBoost suitability score. A higher suitability score does not necessarily mean an earlier card, because suitability and hybrid rank serve different purposes. The page states this distinction rather than presenting either signal as a purchase probability.',
'Expandable sensitivity text describes how the suitability model responds when a feature is replaced by its training median. It is not an additive explanation of the whole hybrid and is not causal. CSV export retains ranking and suitability fields. Ingredients, dietary suitability and pack size must still be checked by the shopper.']),
('6.2 Out-of-Stock Simulator','02-stockout.png','Multiple-outage scenario with user-controlled demand and acceptance assumptions.',[
'The simulator lets the user mark several products unavailable at the same time. Every selected outage is removed from the candidate pools. Demand, budget and an assumed acceptance rate can be adjusted to explore a scenario; inventory quantities are not modelled.',
'Estimated recovered units equal covered demand multiplied by the chosen acceptance assumption. The revenue scenario additionally uses the estimated price of each first-ranked alternative. These values are neither recorded sales nor a validated forecast of business recovery.',
'The initial reference rate is explicitly labelled as a legacy classifier benchmark. That offline overlap rate is not a calibrated acceptance probability for the new hybrid. The user can change the assumption and export the scenario. This page is useful for discussing operational possibilities while keeping assumptions visible.']),
('6.3 Product Explorer','03-products.png','Catalogue search, category views and historical purchase-frequency exploration.',[
'Product Explorer makes the selected real catalogue easy to inspect. A user can search names and filter by category, then view the number of products, a typical estimated price and the average historical reorder rate.',
'The purchase-frequency chart highlights frequently bought products, while the scatter plot compares estimated prices with historical purchases. The table exposes category, brand-token proxy, popularity and repeat-purchase rate so that the information supporting recommendations can be reviewed.',
'These summaries describe the selected development sample, not the full Instacart population. A product\'s reorder rate measures the share of its historical purchase rows marked as repeats; it is not a forecast for a particular person. The displayed brand field may be a word such as Organic, so it must not be mistaken for a verified manufacturer.']),
('6.4 Relationship Explorer','04-relationships.png','Graph view separating candidate substitutes from frequently co-purchased complements.',[
'Relationship Explorer helps the user distinguish two different product relationships. Complements are items often bought together. Possible substitutes are eligible alternatives ranked for the selected query. A graph uses separate edge colours so that the two meanings are not mixed.',
'The page also shows mined association rules, support, confidence, lift and the recorded Apriori/FP-Growth comparison. Support describes joint occurrence in historical baskets; confidence describes the conditional rule frequency; lift compares co-purchase with an independence baseline.',
'The relationships are descriptive evidence, not verified consumer intent. A strong complement association is not automatically a suitable replacement. The same-category and low-lift restriction still applies to candidates. Its restricted coverage is reported in evaluation rather than avoided by inserting a known later purchase into the recommendation list.']),
('6.5 Model Performance','05-models.png','Current hybrid holdout results above the labelled original classifier experiment.',[
'Model Performance shows current hybrid evaluation first. The chart compares methods on the same 4,594 examples, and uncertainty bars accompany NDCG@5. The table includes precision, recall, MAP, hit rate, coverage and the number of events and households.',
'The original six-classifier study remains available below as a labelled reference. It includes a shared comparison table, ROC and precision-recall curves, a confusion matrix, permutation importance and weak-label calibration measures. XGBoost remains the suitability signal; it is no longer the rule that orders the main cards.',
'A viewer should distinguish the current new-household ranking study from the original classifier and 2,540-event legacy benchmark. They use different populations and targets. The page reports that the hybrid has the highest measured primary ranking score while explaining that its small edge over popularity is not statistically conclusive.']),
('6.6 ML Lab','06-ml-lab.png','New-household evidence and controls for exploring the ranking model.',[
'ML Lab provides a closer view of recommendation experiments. Current evidence shows the frozen new-household holdout, selected parameters and blend weights. It also records the paired comparison against popularity and explains the uncertainty around that difference.',
'The interactive ranker view allows a product query, price limit and unavailable alternatives. The user can compare the active hybrid ordering with the separate suitability signal. Original LambdaMART trials, category slices and feature-removal experiments are retained as labelled reference material.',
'The probability-calibration view belongs to the six weak-label classifiers. Its reliability diagram compares mean probabilities with observed weak-label frequencies. It does not calibrate shopper acceptance or the hybrid ordering score. Small category samples and the five-positive classifier test are explicitly limited evidence, not proof of a generally best-performing system.']),
('6.7 About, Execution and Transparency','07-about.png','Project methodology, team information, tools and dataset limitations.',[
'The About page explains the project purpose, workflow, team and data source. It describes the validated hybrid and the separate suitability signal, while making the estimated-price and unverified-brand fields visible. This helps a non-technical reviewer understand what information the system actually has.',
'The project separates installation, reproducible fitting and lightweight serving. Prepared tables and numeric arrays allow the website to start without retraining. Tests cover input handling, splits, encodings, rankings and interface behavior; 29 passing checks are software evidence, not a claim that every recommendation is correct.'])]
for i,(heading,file,caption,paras) in enumerate(app_pages,1):
 blocks=[h(heading)]+[p(t) for t in paras[:2]]
 blocks.append(figure(f'6.{i}',caption,'presentations/screenshots/'+file,286 if i==1 else 308))
 blocks += [p(t) for t in paras[2:]]
 if i==7:blocks.append(code('python scripts/train.py --data-source instacart\npython -m unittest discover -s tests -v\npython -m streamlit run streamlit_app.py'))
 page('FRESHMATCH APPLICATION' if i==1 else '',6 if i==1 else None,blocks)

fresh_rows=[[r['model'].replace('Content similarity','Name similarity'),f"{r['ndcg_at_k']:.4f}",f"{r['precision_at_k']:.4f}",f"{r['recall_at_k']:.4f}",f"{r['map_at_k']:.4f}",f"{r['hit_rate']:.4f}"] for r in FRESH['test_metrics']]
page('RESULTS AND DISCUSSION',7,[h('7.1 New-Household Ranking Results'),
p('The frozen hybrid is evaluated on 4,594 qualifying events from 1,888 previously unused accounts. All seven methods use the same candidate eligibility and event definitions. The primary measure is NDCG@5; other measures show whether the ordering improvement also changes retrieval and hit rates.'),
table('7.1','Ranking results on the fixed new-household holdout',['Method','NDCG@5','Precision@5','Recall@5','MAP@5','Hit rate'],fresh_rows,[149,67,67,67,67,67]),
p('FreshMatch Hybrid has the highest observed NDCG@5, 0.134397. The directional-only component is very close at 0.134328, while popularity scores 0.132627. The original ranker scores 0.117266 on the same examples, giving a relative hybrid improvement of approximately 14.6%.'),
h('7.2 What the Improvement Means'),
p('The improvement is strongest relative to the earlier learned models and similarity baselines. The hybrid does not win every metric: popularity has slightly higher precision, and the directional-only component has slightly higher recall and hit rate. These differences are visible in the table rather than replaced by a single best-model label.'),
p('Target coverage is 0.361994 for every method. In other words, only 36.2% of events have any observed relevant product inside the eligible pool. This constrains attainable performance and points to candidate generation as an important next research step. The candidate policy was not relaxed after seeing the holdout results.'),
p('This study does not establish a universally best recommender. Ranking scores are not dietary-equivalence judgments, buying probabilities or actual recovered revenue.')])

paired=[[r['baseline'],f"{r['ndcg_difference']:+.5f}",f"{r['ci_low']:+.5f}",f"{r['ci_high']:+.5f}"] for r in FRESH['paired_comparisons']]
page(blocks=[h('7.3 Paired Uncertainty and Interpretation'),
table('7.2','Hybrid-minus-baseline NDCG differences and 95% bootstrap intervals',['Comparison baseline','Mean difference','Lower bound','Upper bound'],paired,[184,100,100,100]),
p('The paired difference against the original ranker is +0.01713, with a positive interval from +0.01285 to +0.02157. Against popularity the difference is +0.00177, with interval -0.00042 to +0.00421. Because this latter interval includes zero, superiority over popularity is not statistically established. Separate methods\' error bars are not a substitute for this paired calculation.'),
figure('7.1','NDCG@5 with household-bootstrap intervals on the same 4,594 events.','reports/assets/ranking-results.png',216),
p('The result supports further work on the improved ranker while preserving a realistic account of uncertainty. It does not support adjusting weights after inspecting the holdout and then calling the same data unseen. The score-file digests, fixed protocol and per-event audit table make that boundary inspectable.')])

page('LIMITATIONS AND FUTURE WORK',8,[h('8.1 Labels and Statistical Limits'),
p('Observed same-aisle purchase changes are useful proxies, but they do not confirm a stockout, a deliberate replacement or equal product use. Weak suitability labels are rule-based, and their test contains only five positive pairs. The new-household study is within the same public dataset, not a prospective retailer trial. Its small difference from popularity needs more independent evidence.'),
h('8.2 Coverage and Product Information'),
p('The restricted 320-product catalogue and low-lift rule exclude many later purchases. Coverage is 36.2% on the new holdout. Widening eligibility may help retrieval but can also introduce complements or poor matches; such changes should be selected using training/validation data and a fresh evaluation. The current dataset does not provide verified prices, brands, ingredients, package sizes, nutrition or inventory capacity.'),
h('8.3 Personalisation and Operational Scope'),
p('FreshMatch gives a product-level ranking, not a logged-in customer-specific preference model. Historical features share information within the development population, although the additional 5,000 accounts are excluded from fitting. The stockout simulator applies explicit assumptions rather than estimating causal recovered sales. Tests and browser checks establish implemented behavior, not commercial readiness.'),
h('8.4 Planned Improvements'),
bullets(['Collect expert-checked substitute pairs and ingredient, pack-size and dietary constraints.',
'Improve candidate generation and test category-specific rules with predeclared validation criteria.',
'Add observed retail prices and inventory quantities before making operational recovery estimates.',
'Use a new independent holdout for later model changes; preserve the existing frozen study as historical evidence.',
'Run prospective acceptance and usability studies, including accessibility and production monitoring.'])])

page('CONCLUSION',9,[h('9.1 Summary of the Work'),
p('FreshMatch brings real grocery purchase data, recommendation modelling and an explainable interface into one reproducible project. The workflow prepares Instacart records, mines co-purchases, compares six suitability classifiers and learns how to order possible alternatives. It separates products commonly bought together from candidates that may serve a similar shopping need.'),
p('The improved directional ranker adds candidate popularity, repeat purchases and cross-fitted switching evidence. Validation selects a 75% learned-rank and 25% popularity blend. On 4,594 new-household examples, that fixed hybrid has the highest measured NDCG@5 among the compared methods and improves by 14.6% relative to the original ranker on the same events.'),
p('The remaining uncertainty matters. The lead over popularity is small and not statistically conclusive; coverage is limited and the outcomes are purchase proxies. Presenting those facts makes the work more useful than claiming that machine learning always defeats a simple baseline.'),
h('9.2 Project Outcomes'),
bullets(['A real-data pipeline with strict input checks, Git LFS support and recorded source fingerprints.',
'Comparable suitability and ranking experiments with explicit evaluation boundaries.',
'A validation-selected hybrid connected to the main recommendation order.',
'Seven application pages, exportable evidence, screenshots, reports and a presentation.',
'Twenty-nine passing software checks and a fixed new-household verification protocol.']),
p('The next stage is to strengthen the evidence with better product information, expert labels and genuinely new outcome data. Within its current scope, FreshMatch demonstrates how an ML recommendation project can be improved, tested and explained without confusing a high point estimate with guaranteed real-world success.')])

REFERENCES=[
('[1]','Instacart Market Basket Analysis, community dataset supplied by psparks, Kaggle. https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis.'),
('[2]','FreshMatch project team, FreshMatch source code and recorded experiment artifacts, commit c767a0c. https://github.com/RangaMokshagna/FreshMatch.'),
('[3]','R. Agrawal and R. Srikant, “Fast Algorithms for Mining Association Rules,” Proceedings of the 20th International Conference on Very Large Data Bases, pp. 487–499, 1994.'),
('[4]','J. Han, J. Pei and Y. Yin, “Mining Frequent Patterns without Candidate Generation,” Proceedings of ACM SIGMOD, pp. 1–12, 2000. doi:10.1145/342009.335372.'),
('[5]','C. J. C. Burges, “From RankNet to LambdaRank to LambdaMART: An Overview,” Microsoft Research Technical Report MSR-TR-2010-82, 2010.'),
('[6]','T. Chen and C. Guestrin, “XGBoost: A Scalable Tree Boosting System,” Proceedings of ACM SIGKDD, pp. 785–794, 2016. doi:10.1145/2939672.2939785.'),
('[7]','K. Järvelin and J. Kekäläinen, “Cumulated Gain-Based Evaluation of IR Techniques,” ACM Transactions on Information Systems, vol. 20, no. 4, pp. 422–446, 2002. doi:10.1145/582415.582418.'),
('[8]','F. Pedregosa et al., “Scikit-learn: Machine Learning in Python,” Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.'),
('[9]','Scikit-learn Developers, Probability Calibration user guide and CalibratedClassifierCV documentation. https://scikit-learn.org/stable/modules/calibration.html.'),
('[10]','Streamlit, Streamlit documentation: application development, data display and testing. https://docs.streamlit.io/.'),
('[11]','B. Efron and R. J. Tibshirani, An Introduction to the Bootstrap. Chapman & Hall, 1993.'),
('[12]','G. Salton and C. Buckley, “Term-Weighting Approaches in Automatic Text Retrieval,” Information Processing & Management, vol. 24, no. 5, pp. 513–523, 1988. doi:10.1016/0306-4573(88)90021-0.')]
page('REFERENCES',blocks=[{'type':'reference','text':label+' '+text} for label,text in REFERENCES])
assert len(PAGES)==34,len(PAGES)
