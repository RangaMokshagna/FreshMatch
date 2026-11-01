import unittest
import numpy as np
from evaluation import product_disjoint_splits

class SplitTests(unittest.TestCase):
    def test_disjoint_support_and_reproducibility(self):
        categories=np.repeat(['a','b','c'],24)
        a,b=np.triu_indices(len(categories),1)
        y=((categories[a]==categories[b]) & ((a+b)%3==0)).astype(int)
        train,test,cv,audit=product_disjoint_splits(a,b,y,categories)
        endpoints=lambda ids:set(a[ids])|set(b[ids])
        self.assertFalse(endpoints(train)&endpoints(test))
        for tr,va in cv:
            self.assertFalse(endpoints(train[tr])&endpoints(train[va]))
            for subset in [train[tr],train[va],test]:
                self.assertGreaterEqual(np.bincount(y[subset],minlength=2).min(),5)
        again=product_disjoint_splits(a,b,y,categories)
        np.testing.assert_array_equal(train,again[0]);np.testing.assert_array_equal(test,again[1])
        self.assertEqual(audit,again[3])

    def test_impossible_support_raises(self):
        with self.assertRaisesRegex(ValueError,'Cannot form supported'):
            product_disjoint_splits([0,1],[1,2],[0,1],['a']*3,outer_attempts=2,fold_attempts=2)

if __name__=='__main__':
    unittest.main()
