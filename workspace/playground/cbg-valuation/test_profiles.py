import sqlite3
import unittest
from profiles import setup_profiles, save_profile, save_market_profile, get_profile, list_profiles

class ProfileTest(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:');setup_profiles(self.db)
    def tearDown(self):self.db.close()
    def test_specific_link_lookup_and_missing_not_previous_account(self):
        save_profile(self.db,{'listing_id':'a','features':{'school':'龙宫'}})
        self.assertEqual(get_profile(self.db,'a')['features']['school'],'龙宫')
        self.assertIsNone(get_profile(self.db,'b'))
    def test_latest_profile_and_saved_time(self):
        save_profile(self.db,{'listing_id':'a'})
        save_profile(self.db,{'listing_id':'b'})
        self.assertEqual(get_profile(self.db)['listing_id'],'b')
        self.assertIn('saved_at',get_profile(self.db))

    def test_profile_history_is_compact_and_newest_first(self):
        save_profile(self.db,{'listing_id':'a','name':'甲','server':'测试服','features':{'level':109,'school':'龙宫'}})
        save_profile(self.db,{'listing_id':'b','server':'测试服','features':{'level':175,'school':'女儿村'}})
        rows=list_profiles(self.db)
        self.assertEqual([r['listing_id'] for r in rows],['b','a'])
        self.assertEqual(rows[0]['name'],'175级女儿村')
        self.assertNotIn('features',rows[0])
    def test_basic_reimport_cannot_drop_same_version_detail(self):
        save_profile(self.db,{'listing_id':'a','description_version':'v1','description':{'assets':[]}})
        self.assertIn('description',save_profile(self.db,{'listing_id':'a','description_version':'v1'}))
        self.assertNotIn('description',save_profile(self.db,{'listing_id':'a','description_version':'v2'}))

    def test_market_profiles_never_enter_user_history(self):
        save_profile(self.db,{'listing_id':'mine','name':'我的角色'})
        save_market_profile(self.db,{'listing_id':'market','name':'市场样本'})
        self.assertEqual([row['listing_id'] for row in list_profiles(self.db)],['mine'])
        self.assertIsNone(get_profile(self.db,'market'))
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM market_profiles').fetchone()[0],1)

if __name__=='__main__':unittest.main()
