import json
import sqlite3
import unittest
from datetime import datetime, timezone, timedelta
from ingestion import setup, ingest, collector_state, collection_session

class IngestionTest(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE snapshots(category TEXT, listing_id TEXT, observed_at TEXT, payload TEXT, PRIMARY KEY(category,listing_id,observed_at))')
        setup(self.db)
        self.sample = {'listing_id':'test-only','category':'role','name':'测试非行情','server':'测试服',
                       'price':100,'observed_at':(datetime.now(timezone.utc)-timedelta(hours=1)).isoformat(),
                       'features':{'level':175,'school':'女儿村','realm':'渡劫'},'source_url':'https://example.com/test',
                       'empty_verified':True,'status':'listed'}
    def tearDown(self): self.db.close()

    def test_idempotent_duplicates_and_same_time_changes_overwrite(self):
        self.assertEqual(ingest(self.db,[self.sample])['inserted'],1)
        self.assertEqual(ingest(self.db,[self.sample])['duplicates'],1)
        self.assertEqual(ingest(self.db,[{**self.sample,'price':1}])['overwritten'],1)
        payload=json.loads(self.db.execute('SELECT payload FROM snapshots').fetchone()[0])
        self.assertEqual(payload['price'],1)

    def test_mixed_batch_reports_rejections_with_row_numbers(self):
        result=ingest(self.db,[self.sample,{**self.sample,'listing_id':'bad','price':-1}])
        self.assertEqual((result['inserted'],result['rejected'],result['status']),(1,1,'partial'))
        self.assertEqual(result['errors'][0]['row'],2)

    def test_equivalent_timezones_deduplicated(self):
        ingest(self.db,[self.sample])
        changed={**self.sample,'observed_at':datetime.fromisoformat(self.sample['observed_at']).astimezone(timezone(timedelta(hours=8))).isoformat()}
        self.assertEqual(ingest(self.db,[changed])['duplicates'],1)

    def test_newer_snapshot_overwrites_previous_snapshot(self):
        ingest(self.db,[self.sample])
        newer={**self.sample,'status':'removed','observed_at':datetime.now(timezone.utc).isoformat()}
        self.assertEqual(ingest(self.db,[newer])['overwritten'],1)
        c=next(r for r in collector_state(self.db)['coverage'] if r['category']=='role')
        self.assertEqual((c['products'],c['snapshots'],c['fresh_listed']),(1,1,0))

    def test_older_snapshot_does_not_replace_newer_snapshot(self):
        ingest(self.db,[self.sample])
        older={**self.sample,'price':1,'observed_at':(datetime.now(timezone.utc)-timedelta(days=1)).isoformat()}
        self.assertEqual(ingest(self.db,[older])['duplicates'],1)
        payload=json.loads(self.db.execute('SELECT payload FROM snapshots').fetchone()[0])
        self.assertEqual(payload['price'],100)

    def test_categories_and_source_validation(self):
        rows=[]
        for cat in ('equipment','pet','item','appearance'):
            rows.append({**self.sample,'category':cat,'features':{'name':'测试物品'}})
        result=ingest(self.db,rows)
        self.assertEqual(result['inserted'],4)
        for change in ({'source_url':'javascript:alert(1)'},{'status':'fake'},{'empty_verified':'true'}):
            self.assertEqual(ingest(self.db,[{**self.sample,**change}])['rejected'],1)

    def test_no_network_activity_or_fake_coverage(self):
        s=collector_state(self.db)
        self.assertEqual(s['network_requests'],0)
        self.assertEqual(s['network_status'],'not_configured')
        self.assertTrue(all(c['products']==0 and c['latest_at'] is None for c in s['coverage']))

    def test_extension_runs_are_reported_separately(self):
        ingest(self.db,[self.sample],source_type='chrome_extension')
        state=collector_state(self.db)
        self.assertEqual(state['network_status'],'chrome_extension')
        self.assertEqual(state['network_requests'],1)
        self.assertEqual(state['runs'][0]['source_type'],'chrome_extension')

    def test_collection_session_tracks_running_and_completion(self):
        started=collection_session(self.db,{'action':'start','total':3,'source_url':'https://xyq.cbg.163.com/equip'})
        self.assertEqual(collector_state(self.db)['current_session']['status'],'running')
        done=collection_session(self.db,{'action':'update','id':started['id'],'status':'completed','completed':2,'failed':1,
                                         'inserted':1,'overwritten':1,'duplicates':0,'errors':['一个失败原因']})
        self.assertEqual((done['status'],done['completed'],done['failed']),('completed',2,1))
        state=collector_state(self.db)
        self.assertEqual((state['sessions'][0]['inserted'],state['sessions'][0]['overwritten']),(1,1))
        self.assertEqual(state['sessions'][0]['errors'],['一个失败原因'])

    def test_collection_session_accepts_large_paged_collection(self):
        started=collection_session(self.db,{'action':'start','total':300,'source_url':'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py'})
        self.assertEqual(started['total'],300)
        with self.assertRaisesRegex(ValueError,'1至1000'):
            collection_session(self.db,{'action':'start','total':1001,'source_url':'https://xyq.cbg.163.com/cgi-bin/xyq_overall_search.py'})

if __name__=='__main__': unittest.main()
