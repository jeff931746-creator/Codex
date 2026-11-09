import unittest
from datetime import datetime, timezone, timedelta
from engine import compare, validate_sample, backtest
from valuation_rules import person_training_value

class EngineTest(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)
        self.target = {'category':'role','name':'测试空号','server':'测试服',
                       'features':{'level':175,'school':'女儿村','realm':'渡劫','cultivation':76}}
    def sample(self, ident, price, **kwargs):
        return {'category':'role','listing_id':ident,'name':'测试数据非行情','server':'测试服',
                'features':dict(self.target['features']),'price':price,'empty_verified':True,
                'source_url':'https://example.com/'+ident,'status':'listed',
                'observed_at':(self.now-timedelta(hours=1)).isoformat(),**kwargs}
    def test_duplicate_snapshots_do_not_inflate_evidence(self):
        s=self.sample('a',100)
        result=compare(self.target,[s,{**s,'price':110,'observed_at':self.now.isoformat()},self.sample('b',120)],now=self.now)
        self.assertIsNone(result['price'])
        self.assertEqual(result['count'],2)
    def test_cross_server_matches_while_old_unverified_and_delisted_are_excluded(self):
        rows=[self.sample('a',100),self.sample('b',120),self.sample('c',130,empty_verified=False),
              self.sample('d',90,server='别服'),self.sample('e',90,status='removed'),
              self.sample('f',90,observed_at=(self.now-timedelta(days=8)).isoformat())]
        result=compare(self.target,rows,now=self.now)
        self.assertEqual(result['count'],3)
        self.assertEqual(result['price'],100)
        self.assertEqual(result['excluded']['类别不同'],0)
    def test_exact_and_normal_have_distinct_semantics(self):
        rows=[self.sample(str(i),p) for i,p in enumerate([100,120,140])]
        self.assertEqual(compare(self.target,rows,'exact',now=self.now)['price'],100)
        self.assertEqual(compare(self.target,rows,'normal',now=self.now)['price'],120)
        rows[0]['features']['cultivation']=75
        self.assertEqual(compare(self.target,rows,'exact',now=self.now)['price'],100)
    def test_latest_removed_snapshot_suppresses_old_listing(self):
        rows=[self.sample('a',100),self.sample('b',120),self.sample('c',130),
              self.sample('a',100,status='removed',observed_at=self.now.isoformat())]
        self.assertEqual(compare(self.target,rows,now=self.now)['count'],2)
    def test_unknown_attribute_is_not_zero(self):
        rows=[self.sample(str(i),100+i) for i in range(3)]
        del rows[0]['features']['cultivation']
        result=compare(self.target,rows,now=self.now)
        self.assertEqual(result['count'],3)
        self.assertEqual(result['excluded']['修炼或技能不同'],0)

    def test_training_and_skills_adjust_price_instead_of_filtering_samples(self):
        rows=[self.sample('a',100),self.sample('b',120),self.sample('c',140)]
        for index,row in enumerate(rows):
            row['features'].update({'iExptSki1':20+index,'iExptSki2':20,'iExptSki3':20,
                                    'iExptSki4':20,'iBeastSki1':20,'iBeastSki2':20,
                                    'iBeastSki3':20,'iBeastSki4':20,'skill_1':170+index*5,
                                    'strong':40,'speed':30})
        target={**self.target,'features':{**self.target['features'],'iExptSki1':25,
                'iExptSki2':20,'iExptSki3':25,'iExptSki4':20,
                'iBeastSki1':20,'iBeastSki2':20,'iBeastSki3':20,'iBeastSki4':20,
                'skill_1':180,'strong':40,'speed':30}}
        result=compare(target,rows,now=self.now)
        self.assertEqual(result['count'],3)
        self.assertTrue(all('adjusted_price' in row for row in result['samples']))
        self.assertEqual(result['excluded']['修炼或技能不同'],0)
        self.assertIn('人物修炼',result['samples'][0]['adjustment_breakdown'])

    def test_lower_training_is_not_priced_like_high_training_sample(self):
        base={'iExptSki1':25,'iExptSki2':25,'iExptSki3':25,'iExptSki4':25,
              'iBeastSki1':25,'iBeastSki2':20,'iBeastSki3':25,'iBeastSki4':20,
              'skill_1':180,'strong':40,'speed':40}
        rows=[self.sample(str(i),15000+i*100) for i in range(3)]
        for row in rows: row['features'].update(base)
        target={**self.target,'features':{**self.target['features'],**base,
                'iExptSki2':22,'iExptSki4':22,'iBeastSki1':20,
                'iBeastSki3':20,'iBeastSki4':17,'speed':30}}
        result=compare(target,rows,now=self.now)
        self.assertLess(result['price'],15000)
        self.assertLess(result['samples'][0]['price_adjustment'],0)

    def test_missing_precise_component_is_excluded_not_treated_as_zero(self):
        exact={'iExptSki1':25,'iExptSki2':25,'iExptSki3':25,'iExptSki4':25}
        rows=[self.sample(str(i),100+i) for i in range(3)]
        for row in rows: row['features'].update(exact)
        del rows[0]['features']['iExptSki4']
        target={**self.target,'features':{**self.target['features'],**exact}}
        result=compare(target,rows,now=self.now)
        self.assertEqual(result['count'],2)
        self.assertEqual(result['excluded']['修炼或技能不同'],1)

    def test_person_training_tiers_are_monotonic(self):
        values=[]
        for offense in range(15,26):
            values.append(person_training_value({'level':175,'iExptSki1':offense,
                'iExptSki2':22,'iExptSki3':offense,'iExptSki4':22}))
        self.assertEqual(values,sorted(values))
    def test_exclusion_reasons_cover_latest_goods(self):
        rows=[self.sample('a',100),self.sample('b',120,empty_verified=False),
              self.sample('c',130,status='removed'),self.sample('d',140,server='其他区服')]
        result=compare(self.target,rows,now=self.now)
        self.assertEqual(result['count'],2)
        self.assertEqual(sum(result['excluded'].values()),2)
        self.assertIn('还缺1个',result['reason'])
        self.assertEqual(result['excluded']['未核验为空号'],1)

    def test_whole_role_samples_never_mix_with_empty_roles(self):
        target={**self.target,'features':{**self.target['features'],'sample_scope':'full_role'}}
        rows=[self.sample('a',100),self.sample('b',120),self.sample('c',130)]
        for row in rows:
            row['features']['sample_scope']='full_role'
            row.pop('empty_verified',None)
        result=compare(target,rows,now=self.now)
        self.assertEqual((result['status'],result['count']),('ready',3))

    def test_normal_mode_expands_across_schools_but_exact_does_not(self):
        target={**self.target,'features':{**self.target['features'],'sample_scope':'full_role'}}
        rows=[self.sample('a',100),self.sample('b',120),self.sample('c',130)]
        for index,row in enumerate(rows):
            row['features'].update({'sample_scope':'full_role','school':('女儿村','龙宫','化生寺')[index]})
            row.pop('empty_verified',None)
        self.assertEqual(compare(target,rows,'normal',now=self.now)['count'],3)
        exact=compare(target,rows,'exact',now=self.now)
        self.assertEqual((exact['status'],exact['count']),('insufficient',1))

    def test_invalid_prices_and_future_times_rejected(self):
        for price in [0,-1,float('nan'),True]:
            with self.assertRaises(ValueError): validate_sample(self.sample('a',price))
        with self.assertRaises(ValueError):
            validate_sample(self.sample('a',1,observed_at=(self.now+timedelta(days=1)).isoformat()))

    def test_standard_result_exposes_model_and_confidence(self):
        rows=[self.sample(str(i),p) for i,p in enumerate([100,120,1000,110])]
        result=compare(self.target,rows,now=self.now)
        self.assertEqual(result['price_target'],'listing_price')
        self.assertIn('model_version',result)
        self.assertIn(result['confidence']['grade'],('低','中','高'))
        self.assertLess(result['price'],1000)

    def test_leave_one_product_out_backtest_returns_diagnostics(self):
        rows=[]
        for i,price in enumerate((100,110,120,130,140,150)):
            rows.append(self.sample(str(i),price,observed_at=(self.now-timedelta(hours=6-i)).isoformat()))
        result=backtest(rows)
        self.assertEqual(result['status'],'ready')
        self.assertGreater(result['evaluated'],0)
        self.assertIn('baseline_median_absolute_percentage_error',result)
        self.assertIsInstance(result['improves_on_baseline'],bool)

if __name__=='__main__': unittest.main()
