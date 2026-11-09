import unittest
from role_parser import parse_role_response

class RoleParserTest(unittest.TestCase):
    def test_holy_realm_is_preserved(self):
        payload=self.response()
        payload['equip']['other_info']['summary']='已化圣九重'
        self.assertEqual(parse_role_response(payload)['features']['realm'],'化圣九重')

    def test_official_catalog_does_not_promote_description_only_skills(self):
        payload=self.response()
        payload['equip']['card_style']['school']='化生寺'
        payload['equip']['other_info']['all_skills']={'16':180,'17':180,'162':1,'99999':1}
        catalog={'school_skill':{'16':{'name':'金刚伏魔'},'17':{'name':'小乘佛法'}},
                 'ju_qing_skill':{'170':'翰墨之道'},
                 'ju_qing_skill_desc':{'162':{'name':'牌弈之术'}}}
        groups=parse_role_response(payload,catalog)['skills']['groups']
        self.assertEqual([row['name'] for row in groups['school']],['金刚伏魔','小乘佛法'])
        self.assertEqual(groups['plot'],[])
        self.assertEqual([row['id'] for row in groups['unknown']],[162,99999])

    def test_handwriting_and_painting_display_levels_follow_cbg(self):
        payload=self.response()
        payload['equip']['other_info']['all_skills']={'170':4,'197':2}
        groups=parse_role_response(payload)['skills']['groups']
        self.assertEqual([(row['id'],row['level']) for row in groups['plot']],[(170,3),(197,1)])

    def response(self):
        return {'equip':{'equip_level':175,'card_style':{'school':'龙宫'},'server_name':'龙马精神',
                'price':999999,'status_desc':'买家取走','eid':'test-only',
                'other_info':{'cName':'测试角色','iGrade':175,'summary':'已渡劫 总修:76 总宠修:77',
                'xiulian':76,'pet_xiulian':77,'iExptSki1':7,'iMaxExpt1':20,
                'all_skills':{'230':40}}}}
    def test_direct_fields_and_skill_ids_preserved(self):
        parsed=parse_role_response(self.response())
        self.assertEqual(parsed['features']['realm'],'渡劫')
        self.assertEqual(parsed['features']['cultivation'],76)
        self.assertEqual(parsed['features']['pet_cultivation'],77)
        self.assertEqual(parsed['features']['iMaxExpt1'],20)
        self.assertEqual(parsed['features']['skill_230'],40)
    def test_unknown_fields_not_inferred(self):
        parsed=parse_role_response(self.response())
        self.assertNotIn('qianyuan',parsed['features'])
        self.assertEqual(parsed['features']['strong'],40)
        self.assertNotIn('speed',parsed['features'])
        self.assertNotIn('price',parsed)
        self.assertEqual(parsed['price_unit'],'unverified')
        self.assertEqual(parsed['status_desc'],'买家取走')
    def test_skill_groups_keep_unmapped_entries(self):
        payload=self.response()
        payload['equip']['other_info']['all_skills']={'25':180,'33':131,'201':140,'237':30,'153':2,'99999':7}
        parsed=parse_role_response(payload)
        groups=parsed['skills']['groups']
        self.assertEqual(groups['school'][0]['name'],'破浪诀')
        self.assertEqual(groups['life'][0]['name'],'强身术')
        self.assertEqual(groups['plot'][0]['name'],'丹元济会')
        self.assertEqual(groups['unknown'][0]['id'],99999)
        self.assertEqual(parsed['skills']['count'],6)
        self.assertEqual(parsed['features']['speed'],30)
    def test_school_names_not_applied_to_other_school(self):
        payload=self.response()
        payload['equip']['card_style']['school']='其他门派'
        payload['equip']['other_info']['all_skills']={'25':100}
        parsed=parse_role_response(payload)
        self.assertEqual(parsed['skills']['groups']['school'],[])
        self.assertEqual(parsed['skills']['groups']['unknown'][0]['level'],100)
    def test_unknown_realm_is_not_defaulted(self):
        response=self.response()
        response['equip']['other_info']['summary']='化圣'
        self.assertNotIn('realm',parse_role_response(response)['features'])
    def test_nonrole_or_wrong_response_rejected(self):
        for p in ({'version':'x','equip_desc':'encoded'},{'equip':{}},[]):
            with self.assertRaises(ValueError): parse_role_response(p)

if __name__=='__main__': unittest.main()
