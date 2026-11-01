"""Small fabricated CSV fixtures test ingestion, never serve as real training data."""
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

import pandas as pd

from real_data import (DatasetError, SCHEMAS, cache_fingerprint, extract_instacart_archive,
                       load_instacart, provenance, validate_instacart)

ROOT = Path(__file__).resolve().parents[1]


def fixture(root):
    pd.DataFrame({'product_id':[1,2,3], 'product_name':['Brand Alpha','Brand Beta','Future only'],
                  'aisle_id':[1]*3,'department_id':[1]*3}).to_csv(root/'products.csv',index=False)
    pd.DataFrame({'aisle_id':[1],'aisle':['milk']}).to_csv(root/'aisles.csv',index=False)
    pd.DataFrame({'department_id':[1],'department':['dairy']}).to_csv(root/'departments.csv',index=False)
    orders, lines = [], []
    for user in range(1,21):
        for number in range(1,5):
            order = user*10+number
            orders.append(dict(order_id=order,user_id=user,order_number=number,eval_set='prior'))
            # Product 3 occurs exclusively in held-out orders and must not select the catalogue.
            product = 3 if number==4 else (number%2+1)
            lines.append(dict(order_id=order,product_id=product,reordered=int(number>1)))
    pd.DataFrame(orders).to_csv(root/'orders.csv',index=False)
    pd.DataFrame(lines).to_csv(root/'order_products__prior.csv',index=False)


class RealDataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        fixture(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_missing_data_fails_without_fallback_or_artifact_changes(self):
        manifest = (ROOT/'artifacts/manifest.json').read_bytes()
        result = subprocess.run([sys.executable,str(ROOT/'scripts/train.py'), '--data-dir', str(self.root/'missing')],
                                capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('Real Instacart data is required',result.stderr)
        self.assertEqual((ROOT/'artifacts/manifest.json').read_bytes(),manifest)

    def test_schema_checks_and_check_only_command(self):
        self.assertEqual(validate_instacart(self.root),self.root)
        result = subprocess.run([sys.executable,str(ROOT/'scripts/train.py'),'--check-data','--data-dir',str(self.root)],
                                capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        (self.root/'aisles.csv').write_text('wrong\n1\n')
        with self.assertRaisesRegex(DatasetError,'missing columns'):
            validate_instacart(self.root)

    def test_lfs_pointer_is_not_accepted_as_csv(self):
        (self.root/'aisles.csv').write_text('version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 100\n')
        with self.assertRaisesRegex(DatasetError,'Git LFS pointer'):
            validate_instacart(self.root)

    def test_invalid_reorder_flag_rejected(self):
        lines = pd.read_csv(self.root/'order_products__prior.csv')
        lines.loc[0,'reordered']=2
        lines.to_csv(self.root/'order_products__prior.csv',index=False)
        with self.assertRaisesRegex(DatasetError,'0 or 1'):
            validate_instacart(self.root)

    def test_holdout_does_not_select_catalogue(self):
        products, orders, lines = load_instacart(self.root,max_products=2,max_households=20,chunksize=7)
        self.assertEqual(set(products.product_id),{1,2})
        self.assertEqual(orders.user_id.nunique(),20)
        self.assertEqual(set(lines.product_id),{1,2})
        self.assertNotIn('need_id',products)
        self.assertEqual(set(orders.groupby('user_id').size()),{4})

    def test_cache_invalidation_includes_all_source_files(self):
        before = provenance(self.root)
        self.assertEqual(before['source'],'Instacart')
        self.assertEqual(set(before['files']),set(SCHEMAS))
        frame = pd.read_csv(self.root/'products.csv')
        frame.loc[0,'product_name']='Changed product'
        frame.to_csv(self.root/'products.csv',index=False)
        self.assertNotEqual(cache_fingerprint(before),cache_fingerprint(provenance(self.root)))
        self.assertNotEqual(cache_fingerprint(before),cache_fingerprint(provenance(self.root,seed=7)))

    def test_unknown_product_reference_rejected(self):
        lines = pd.read_csv(self.root/'order_products__prior.csv');lines.loc[0,'product_id']=999
        lines.to_csv(self.root/'order_products__prior.csv',index=False)
        with self.assertRaisesRegex(DatasetError,'missing from products'):
            load_instacart(self.root,max_households=20)

    def test_partial_prior_file_rejected(self):
        lines = pd.read_csv(self.root/'order_products__prior.csv').iloc[1:]
        lines.to_csv(self.root/'order_products__prior.csv',index=False)
        with self.assertRaisesRegex(DatasetError,'no purchase rows'):
            load_instacart(self.root,max_households=20)

    def test_nested_archives_only_extract_whitelisted_basenames(self):
        archive = self.root/'download.zip'
        with zipfile.ZipFile(archive,'w') as outer:
            outer.writestr('../../unwanted.txt','ignored')
            for name in SCHEMAS:
                payload = io.BytesIO()
                with zipfile.ZipFile(payload,'w') as inner:
                    inner.writestr('nested/'+name,(self.root/name).read_bytes())
                outer.writestr(name+'.zip',payload.getvalue())
        destination = self.root/'extracted'
        extract_instacart_archive(archive,destination)
        self.assertEqual(set(p.name for p in destination.iterdir()),set(SCHEMAS))
        with self.assertRaisesRegex(DatasetError,'already exist'):
            extract_instacart_archive(archive,destination)


if __name__=='__main__':
    unittest.main()
