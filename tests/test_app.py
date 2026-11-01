from pathlib import Path
import unittest
import json
import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]

class AppTests(unittest.TestCase):
    def test_all_pages_and_advanced_interactions(self):
        at = AppTest.from_file(str(ROOT/'streamlit_app.py'), default_timeout=60)
        for page in ['Find Substitutes','Out-of-Stock Simulator','Product Explorer',
                     'Relationship Explorer','Model Performance','ML Lab','About']:
            with self.subTest(page=page):
                at.session_state['freshmatch_page'] = page
                at.run()
                self.assertFalse(at.exception, [e.message for e in at.exception])
                self.assertFalse(at.error, [e.value for e in at.error])
                if json.loads((ROOT/'artifacts/manifest.json').read_text())['source']!='Instacart':
                    self.assertTrue(any('Synthetic demo' in warning.value for warning in at.warning))
        at.session_state['freshmatch_page'] = 'ML Lab'
        at.run()
        products = pd.read_csv(ROOT/'artifacts/products.csv')
        query = min(24, len(products)-1)
        at.selectbox(key='lab_query').select(query).run()
        unavailable = products.index[products.category==products.iloc[query].category].tolist()
        at.multiselect(key='lab_outages').set_value(unavailable).run()
        self.assertFalse(at.exception)
        self.assertTrue(any('No alternatives' in i.value for i in at.info))
        at.multiselect(key='lab_outages').set_value([]).run()
        at.selectbox(key='calibration_model').select('Logistic Regression').run()
        self.assertFalse(at.exception)
        self.assertGreaterEqual(len(at.dataframe), 7)
        at.session_state['freshmatch_page'] = 'Find Substitutes'
        at.run()
        at.selectbox(key='chosen_product').select(0).run()
        self.assertFalse(at.exception)
        self.assertTrue(at.get('download_button'))

if __name__ == '__main__':
    unittest.main()
