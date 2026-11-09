import unittest
from server import is_extension_request, mapped_icon_path, full_role_sample, mark_asset_scope

class ServerSecurityTest(unittest.TestCase):
    def test_icon_enum_mapping(self):
        self.assertEqual(mapped_icon_path('pet','102128'),'pets/small/102128.gif')
        self.assertEqual(mapped_icon_path('pet_skill','416'),'pet_child_skill/0416.gif')
        self.assertEqual(mapped_icon_path('role_skill','9'),'role_skills/0009.gif')
        self.assertEqual(mapped_icon_path('role_skill','201'),'role_skills/0201.gif')
        self.assertEqual(mapped_icon_path('clothes','123'),'clothes/1230000.gif')
        self.assertIsNone(mapped_icon_path('unknown','1'))
        self.assertIsNone(mapped_icon_path('pet','../1'))

    def test_extension_is_limited_to_sync_endpoint_and_marker(self):
        origin='chrome-extension://abcdefghijklmnop'
        self.assertTrue(is_extension_request(origin,'/api/parse-desktop-bundle','sync-v1'))
        self.assertTrue(is_extension_request(origin,'/api/collect-desktop-bundle','sync-v1'))
        self.assertTrue(is_extension_request(origin,'/api/collection-session','sync-v1'))
        self.assertFalse(is_extension_request(origin,'/api/import','sync-v1'))
        self.assertFalse(is_extension_request(origin,'/api/parse-desktop-bundle','wrong'))
        self.assertFalse(is_extension_request('https://evil.example','/api/parse-desktop-bundle','sync-v1'))

    def test_full_role_sample_keeps_scope_and_asset_counts(self):
        profile={'listing_id':'x','name':'角色','server':'测试服','raw_price':'123.45',
                 'response_time':'2026-01-01T00:00:00+00:00','source_url':'https://example.com/x',
                 'features':{'level':175,'school':'方寸山','realm':'化圣九重'},
                 'description':{'assets':[{'category':'equipment'},{'category':'pet','skills':[1,2]}],
                                'present_groups':['AllEquip','AllSummon','AllRider','ExAvt','HugeHorse']}}
        sample=full_role_sample(profile)
        self.assertEqual(sample['price'],123.45)
        self.assertEqual(sample['features']['sample_scope'],'full_role')
        self.assertTrue(sample['features']['asset_detail_complete'])
        self.assertEqual((sample['features']['equipment_count'],sample['features']['pet_count'],sample['features']['pet_skill_total']),(1,1,2))

    def test_missing_asset_group_is_unknown_not_zero(self):
        profile={'listing_id':'x','name':'角色','server':'测试服','raw_price':100,
                 'source_url':'https://xyq.cbg.163.com/equip','features':{'level':175},
                 'description':{'assets':[],'present_groups':['AllEquip']}}
        sample=full_role_sample(profile)
        self.assertEqual(sample['features']['equipment_count'],0)
        self.assertNotIn('pet_count',sample['features'])
        self.assertEqual(sample['features']['sample_scope'],'role_core')
        self.assertFalse(sample['features']['asset_detail_complete'])

    def test_asset_scope_is_shared_by_target_and_market_profiles(self):
        complete=mark_asset_scope({'features':{},'description':{'present_groups':[
            'AllEquip','AllSummon','AllRider','ExAvt','HugeHorse']}})
        partial=mark_asset_scope({'features':{},'description':{'present_groups':['AllEquip']}})
        self.assertEqual(complete['features']['sample_scope'],'full_role')
        self.assertEqual(partial['features']['sample_scope'],'role_core')

if __name__=='__main__': unittest.main()
