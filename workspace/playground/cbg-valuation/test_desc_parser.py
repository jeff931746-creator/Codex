import base64
import json
import unittest
from desc_parser import LPCParser, decode_description, parse_description, parse_bundle, parse_desktop_bundle

class DescParserTest(unittest.TestCase):
    def desktop_encoded(self, plain, key='AbCd1234EfGh5678'):
        encrypted=''.join(chr(ord(c)^ord(key[i%len(key)])) for i,c in enumerate(plain))
        data=base64.b64encode(json.dumps({'d':encrypted}).encode()).decode()
        return f'@{key}@{data}@'

    def test_desktop_encoded_description_and_profile(self):
        plain='(["usernum":"42","iGrade":175,"iSchool":2,"iZhuanZhi":2,"cName":"测试角色","all_skills":(["230":40,"237":44]),"AllEquip":({}),"AllSummon":({})])'
        encoded=self.desktop_encoded(plain)
        version,raw=decode_description({'equip_desc':encoded})
        self.assertEqual(version,'AbCd1234EfGh5678')
        self.assertEqual(raw['iSchool'],2)
        profile=parse_desktop_bundle({'equip_desc':encoded,'metadata':{'server_name':'测试服','server_id':'1','listing_id':'x'}})
        self.assertEqual(profile['features']['school'],'化生寺')
        self.assertEqual(profile['features']['realm'],'渡劫')
        self.assertEqual(profile['features']['strong'],40)
        self.assertEqual(profile['source_type'],'user_provided_desktop_har')

    def test_overall_search_decoded_json_profile(self):
        raw={'usernum':'42','iGrade':175,'iSchool':7,'iZhuanZhi':2,'cName':'全服角色',
             'all_skills':{'29':180},'AllEquip':{},'AllSummon':{}}
        profile=parse_desktop_bundle({'equip_desc':json.dumps(raw,ensure_ascii=False),
                                      'metadata':{'server_name':'测试服','server_id':'1','listing_id':'overall-x'}})
        self.assertEqual(profile['features']['level'],175)
        self.assertEqual(profile['features']['school'],'龙宫')
        self.assertEqual(profile['name'],'全服角色')

    def test_nested_collections_and_punctuation_inside_strings(self):
        value=LPCParser('(["name":"名字([不替换])","items":({([1:"甲",]),}),])').parse()
        self.assertEqual(value,{'name':'名字([不替换])','items':[{'1':'甲'}]})
    def test_roundtrip_encoded_payload(self):
        text='(["ExAvt":([1:(["cName":"秋水芙蓉","wear_pos":1,]),]),])'
        version='0123456789abcdef0123456789abcdef'
        encoded=''.join(chr(ord(c)^ord(version[i%32])) for i,c in enumerate(text))
        payload={'version':version,'equip_desc':'@'+version+'@'+base64.b64encode(json.dumps(encoded).encode()).decode()}
        result=parse_description(payload)
        self.assertEqual(result['assets'][0]['name'],'秋水芙蓉')
        self.assertEqual(result['counts']['clothes'],1)
        self.assertEqual(result['assets'][0]['position'],1)
    def test_no_eval_and_no_trailing_content(self):
        for text in ('__import__("os")','([]) malicious','(["x":1,"x":2,])'):
            with self.assertRaises(ValueError): LPCParser(text).parse()
    def test_version_mismatch_and_bad_base64(self):
        for payload in ({'version':'bad','equip_desc':'@'+'a'*32+'@eA=='},
                        {'equip_desc':'@'+'a'*32+'@%%%'}):
            with self.assertRaises(ValueError): decode_description(payload)
    def test_present_empty_group_distinct_from_missing(self):
        result=parse_description({'equip_desc':'(["AllSummon":([]),])'})
        self.assertIn('AllSummon',result['present_groups'])
        self.assertNotIn('AllEquip',result['present_groups'])
        self.assertEqual(result['counts']['pet'],0)

    def test_official_asset_and_pet_skill_enums(self):
        text='(["AllEquip":([1:(["iType":2754,]),]),"AllSummon":([1:(["iType":102246,"iGrade":180,"all_skills":(["416":1,]),"summon_core":(["901":({5,0,([]),}),]),"summon_equip1":(["iType":9311,"cDesc":"装备属性",]),"summon_equip4_type":3550,"summon_equip4_desc":"玄天灵力 9",]),]),])'
        catalog={'equip_info':{'2754':{'name':'乾坤天罡履'}},'pet_info':{'102246':'毗舍童子'},
                 'pet_skill_desc':{'416':{'name':'高级神佑复生'}},'pet_neidans':{'901':'迅敏'},
                 'pet_shipin_info':{'3550':'赤炎战笛'},
                 'equip_info':{'2754':{'name':'乾坤天罡履'},'9311':{'name':'召唤兽铠甲'}}}
        result=parse_description({'equip_desc':text},catalog)
        self.assertEqual(result['assets'][0]['name'],'乾坤天罡履')
        self.assertEqual(result['assets'][1]['name'],'毗舍童子')
        self.assertEqual(result['assets'][1]['skills'][0]['name'],'高级神佑复生')
        self.assertEqual(result['assets'][1]['neidans'][0]['name'],'迅敏')
        self.assertEqual(result['assets'][1]['pet_equipment'][0]['name'],'召唤兽铠甲')
        self.assertEqual(result['assets'][1]['pet_accessory']['name'],'赤炎战笛')

    def test_bundle_requires_same_version_and_role(self):
        detail={'equip':{'other_info':{'usernum':123,'iGrade':175,'summary':'已渡劫'},
                        'equip_desc_version':'v1','server_name':'测试服','card_style':{'school':'龙宫'}}}
        desc={'version':'v1','equip_desc':'(["usernum":123,"iGrade":175,"iNutsNum":200,])'}
        result=parse_bundle({'detail_response':detail,'desc_response':desc})
        self.assertEqual(result['features']['potential'],200)
        detail['equip']['other_info']['usernum']=456
        with self.assertRaises(ValueError): parse_bundle({'detail_response':detail,'desc_response':desc})
        detail['equip']['other_info']['usernum']=123
        detail['equip']['equip_desc_version']='v2'
        with self.assertRaises(ValueError): parse_bundle({'detail_response':detail,'desc_response':desc})

if __name__=='__main__': unittest.main()
