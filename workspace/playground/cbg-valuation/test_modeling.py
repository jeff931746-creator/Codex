import json
import sqlite3
import unittest
from modeling import setup_modeling, materialize_snapshot, model_state, MODEL_VERSION, asset_summary


class ModelingTest(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        setup_modeling(self.db)

    def tearDown(self): self.db.close()

    def test_materialized_features_are_versioned_and_unknown_is_not_zero(self):
        row={'category':'role','listing_id':'a','observed_at':'2026-10-28T00:00:00+00:00',
             'features':{'level':175,'school':'女儿村','realm':'渡劫','iExptSki1':25}}
        doc=materialize_snapshot(self.db,row)
        self.assertEqual(doc['model_version'],MODEL_VERSION)
        self.assertIsNone(doc['training']['iExptSki2'])
        saved=json.loads(self.db.execute('SELECT payload FROM model_features').fetchone()[0])
        self.assertEqual(saved['level'],175)
        self.assertLess(saved['completeness'],1)

    def test_model_state_exposes_disabled_unverified_layers(self):
        state=model_state(self.db)
        self.assertFalse(state['sale_price_enabled'])
        self.assertFalse(state['server_coefficient_enabled'])

    def test_asset_summary_extracts_market_comparison_structure(self):
        assets=[
            {'category':'equipment','level':160,'raw':{'cDesc':'锻炼等级 11 特技：晶清诀 特效：永不磨损'}},
            {'category':'pet','skills':[{'name':'高级必杀'},{'name':'吸血'}],
             'neidans':[{'id':'1'}],'pet_equipment':[{'id':'2'}],'raw':{'grow':1266}},
            {'category':'clothes'}, {'category':'xiangrui'}]
        summary=asset_summary(assets)
        self.assertEqual(summary['equipment_gem_max'],11)
        self.assertEqual(summary['equipment_special_count'],2)
        self.assertEqual(summary['pet_high_skill_total'],1)
        self.assertEqual(summary['pet_growth_average'],1.266)


if __name__=='__main__': unittest.main()
