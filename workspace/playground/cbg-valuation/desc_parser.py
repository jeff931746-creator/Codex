"""Bounded, non-executing decoder/parser for uploaded CBG description files."""
import base64
import binascii
import json
import re

class LPCParser:
    def __init__(self, text):
        if not isinstance(text, str) or len(text) > 1_000_000:
            raise ValueError('详情文本为空或超过解析上限')
        self.text, self.pos, self.nodes = text, 0, 0

    def skip(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def consume(self, token):
        self.skip()
        if not self.text.startswith(token, self.pos):
            raise ValueError(f'详情语法错误：位置 {self.pos} 应为 {token}')
        self.pos += len(token)

    def value(self, depth=0):
        self.skip()
        self.nodes += 1
        if depth > 64 or self.nodes > 50000:
            raise ValueError('详情嵌套或节点数量超限')
        if self.text.startswith('([', self.pos):
            self.pos += 2
            result = {}
            while True:
                self.skip()
                if self.text.startswith('])', self.pos):
                    self.pos += 2
                    return result
                key = self.value(depth+1)
                if not isinstance(key, (str, int)):
                    raise ValueError('映射键必须为文本或整数')
                key = str(key)
                self.consume(':')
                if key in result:
                    raise ValueError('详情存在重复键：'+key)
                result[key] = self.value(depth+1)
                self.skip()
                if self.text.startswith('])', self.pos):
                    continue
                self.consume(',')
        if self.text.startswith('({', self.pos):
            self.pos += 2
            result = []
            while True:
                self.skip()
                if self.text.startswith('})', self.pos):
                    self.pos += 2
                    return result
                result.append(self.value(depth+1))
                self.skip()
                if not self.text.startswith('})', self.pos):
                    self.consume(',')
        try:
            value, size = json.JSONDecoder().raw_decode(self.text[self.pos:])
        except (ValueError, json.JSONDecodeError) as exc:
            raise ValueError(f'不支持的详情语法，位置 {self.pos}') from exc
        if value is not None and not isinstance(value, (str, int, float, bool)):
            raise ValueError('不支持的详情值类型')
        self.pos += size
        return value

    def parse(self):
        value = self.value()
        self.skip()
        if self.pos != len(self.text) or not isinstance(value, dict):
            raise ValueError('详情必须是完整的属性映射')
        return value

def decode_description(payload):
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict) or not isinstance(payload.get('equip_desc'), str):
        raise ValueError('详情响应缺少 equip_desc')
    encoded = payload['equip_desc']
    if len(encoded) > 1_500_000:
        raise ValueError('详情文件过大')
    if encoded.startswith('@'):
        parts = encoded.split('@', 2)
        if len(parts) != 3 or not re.fullmatch(r'[A-Za-z0-9]{1,64}', parts[1]):
            raise ValueError('不支持的详情版本格式')
        version, data = parts[1:]
        data = data.removesuffix('@')
        if payload.get('version') and payload['version'] != version:
            raise ValueError('详情响应版本与编码前缀不一致')
        try:
            decoded = json.loads(base64.b64decode(data, validate=True).decode('utf-8'))
        except (binascii.Error, ValueError, UnicodeError) as exc:
            raise ValueError('详情编码不完整或不支持') from exc
        # Mobile responses encode a JSON string; desktop pages wrap it as {"d": "..."}.
        text = decoded.get('d') if isinstance(decoded, dict) else decoded
        if not isinstance(text, str):
            raise ValueError('解码内容不是文本')
        text = ''.join(chr(ord(c)^ord(version[i%len(version)])) for i,c in enumerate(text))
    else:
        text = encoded
        version = payload.get('version')
        # Overall-search pages expose an already decoded role object.  The
        # extension serializes that object as strict JSON so it can share the
        # same bounded, non-executing parser path as desktop detail pages.
        if text.lstrip().startswith('{'):
            def pairs_to_dict(pairs):
                result={}
                for key,value in pairs:
                    if key in result:
                        raise ValueError('详情 JSON 存在重复键：'+str(key))
                    result[key]=value
                return result
            try:
                value=json.loads(text,object_pairs_hook=pairs_to_dict,
                                 parse_constant=lambda value: (_ for _ in ()).throw(ValueError('详情 JSON 包含非有限数值')))
            except (TypeError,json.JSONDecodeError) as exc:
                raise ValueError('详情 JSON 格式错误') from exc
            if not isinstance(value,dict):
                raise ValueError('详情 JSON 必须是属性对象')
            return version,value
    return version, LPCParser(text).parse()

def records(value):
    if isinstance(value, dict):
        return [(str(k), v) for k,v in value.items() if isinstance(v, dict)]
    if isinstance(value, list):
        return [(str(i), v) for i,v in enumerate(value) if isinstance(v, dict)]
    return []

def _enum_name(catalog, field, ident):
    source=catalog.get(field) if isinstance(catalog,dict) else None
    if not isinstance(source,dict) or len(source)>5000:
        return None
    value=source.get(str(ident),source.get(ident))
    if isinstance(value,str) and 0<len(value)<=80:
        return value
    if isinstance(value,dict):
        name=value.get('name')
        if isinstance(name,str) and 0<len(name)<=80:
            return name
    return None

def _asset_skills(item, catalog, field):
    raw=item.get('all_skills')
    if not isinstance(raw,dict):
        return []
    result=[]
    for ident,level in raw.items():
        name=_enum_name(catalog,field,ident)
        result.append({'id':str(ident),'name':name or '未公开名称','level':level,'mapped':bool(name)})
    return result

def _pet_extras(item, catalog):
    equipment=[]
    for slot in range(1,4):
        value=item.get(f'summon_equip{slot}')
        if not isinstance(value,dict):
            continue
        ident=value.get('iType')
        equipment.append({'slot':slot,'type_id':ident,
                          'name':_enum_name(catalog,'equip_info',ident) or f'召唤兽装备 {slot}',
                          'description':value.get('cDesc') or ''})
    accessory=None
    accessory_type=item.get('summon_equip4_type')
    if accessory_type:
        accessory={'type_id':accessory_type,
                   'name':_enum_name(catalog,'pet_shipin_info',accessory_type) or '召唤兽饰品',
                   'description':item.get('summon_equip4_desc') or ''}
    neidans=[]
    cores=item.get('summon_core')
    if isinstance(cores,dict):
        for ident,value in cores.items():
            level=value[0] if isinstance(value,list) and value else None
            neidans.append({'id':str(ident),'name':_enum_name(catalog,'pet_neidans',ident) or '未公开名称',
                            'level':level})
    return equipment,neidans,accessory

def parse_description(payload, official_catalog=None):
    version, raw = decode_description(payload)
    groups = [('equipment','AllEquip','equip_info'),('pet','AllSummon','pet_info'),
              ('mount','AllRider','rider_info'),('clothes','ExAvt','clothes_info'),
              ('xiangrui','HugeHorse','xiangrui_info')]
    assets = []
    for category, field, enum_field in groups:
        for key, item in records(raw.get(field)):
            name = item.get('cName') or _enum_name(official_catalog,enum_field,item.get('iType'))
            skill_field=('pet_skill_desc' if category=='pet' else 'zuoqi_skill_desc' if category=='mount'
                         else 'xiangrui_skill' if category=='xiangrui' else None)
            pet_equipment,neidans,pet_accessory=_pet_extras(item,official_catalog) if category=='pet' else ([],[],None)
            assets.append({'category':category, 'record_id':key,
                           'name':name if isinstance(name,str) and name else f'未映射名称（{item.get("iType",key)}）',
                           'type_id':item.get('iType'), 'level':item.get('iGrade',item.get('obj_level')),
                           'position':item.get('wear_pos'),
                           'skills':_asset_skills(item,official_catalog,skill_field) if skill_field else [],
                           'pet_equipment':pet_equipment, 'neidans':neidans, 'pet_accessory':pet_accessory,
                           'raw':item})
    return {'version':version,'raw':raw,'assets':assets,
            'counts':{category:sum(a['category']==category for a in assets) for category,_,_ in groups},
            'present_groups':[field for _,field,_ in groups if field in raw],
            'warnings':['仅解析用户提供的文件，不访问外网。',
                        '锦衣列表包含部件、挂件及足迹，条目数不等于套装数。',
                        '保留原始编号和属性，未映射名称不猜测。乾元丹字段尚未确认。']}

def parse_bundle(payload):
    from role_parser import parse_role_response
    if not isinstance(payload,dict):
        raise ValueError('请提供两份响应')
    basic=payload.get('detail_response')
    description=payload.get('desc_response')
    profile=parse_role_response(basic)
    desc=parse_description(description)
    equip=basic['equip']
    expected=equip.get('equip_desc_version')
    if not expected or not desc['version'] or expected!=desc['version']:
        raise ValueError('两份响应的详情版本不一致或缺失，请使用同一商品的两份响应')
    basic_id=(equip.get('other_info') or {}).get('usernum')
    raw_id=desc['raw'].get('usernum')
    if basic_id is None or raw_id is None or str(basic_id)!=str(raw_id):
        raise ValueError('两份响应的角色编号不一致或缺失')
    if desc['raw'].get('iGrade')!=profile['features']['level']:
        raise ValueError('两份响应的角色等级不一致')
    profile['description']=desc
    profile['unknown_fields']=[k for k in profile['unknown_fields'] if k not in ('clothes','xiangrui')]
    for source,dest in [('iNutsNum','potential')]:
        v=desc['raw'].get(source)
        if isinstance(v,(int,float)) and not isinstance(v,bool):
            profile['features'][dest]=v
    profile['warnings']=[w for w in profile['warnings'] if not w.startswith('乾元丹、')]+desc['warnings']
    return profile

SCHOOL_NAMES = {
    1:'大唐官府', 2:'化生寺', 3:'女儿村', 4:'方寸山', 5:'天宫',
    6:'普陀山', 7:'龙宫', 8:'五庄观', 9:'狮驼岭', 10:'魔王寨',
    11:'阴曹地府', 12:'盘丝洞', 13:'神木林', 14:'凌波城',
    15:'无底洞', 16:'女魃墓', 17:'天机城', 18:'花果山',
    19:'东海渊', 20:'九黎城', 21:'弥勒山'
}

def parse_desktop_bundle(payload):
    """Build a profile from the desktop detail page's hidden encoded field."""
    from role_parser import parse_role_response
    if not isinstance(payload, dict) or not isinstance(payload.get('equip_desc'), str):
        raise ValueError('桌面版详情缺少 equip_desc')
    metadata = payload.get('metadata') or {}
    if not isinstance(metadata, dict):
        raise ValueError('桌面版商品信息格式错误')
    catalog=payload.get('official_catalog') or payload.get('skill_catalog') or {}
    desc = parse_description({'equip_desc':payload['equip_desc']}, catalog)
    raw = desc['raw']
    school = SCHOOL_NAMES.get(raw.get('iSchool'))
    level = raw.get('iGrade')
    server = metadata.get('server_name')
    missing=[]
    if not isinstance(level, int):
        missing.append('等级')
    if not school:
        missing.append('门派')
    if not isinstance(server, str) or not server.strip():
        missing.append('区服')
    if missing:
        raise ValueError('桌面版详情缺少：'+'、'.join(missing))
    summary = ''
    holy = raw.get('i3FlyLv')
    transfer = raw.get('iZhuanZhi')
    chinese = '零一二三四五六七八九'
    if isinstance(holy, int) and 0 < holy < len(chinese):
        summary = '化圣' + chinese[holy] + '重'
    elif transfer == 2:
        summary = '渡劫'
    elif transfer == 1:
        summary = '飞升'
    elif transfer == 0:
        summary = '未飞升'
    role_raw = dict(raw)
    if summary:
        role_raw['summary'] = summary
    equip = {
        'other_info':role_raw, 'equip_level':level, 'card_style':{'school':school},
        'server_name':server.strip(), 'area_name':metadata.get('area_name'),
        'eid':metadata.get('listing_id'), 'serverid':metadata.get('server_id'),
        'equip_detail_url':metadata.get('source_url'), 'price':metadata.get('price'),
        'status_desc':metadata.get('status_desc'), 'desc_sumup_short':summary,
    }
    profile = parse_role_response({'equip':equip, 'server_now_time':metadata.get('response_time')}, catalog)
    profile['description'] = desc
    profile['source_type'] = 'user_provided_desktop_har'
    profile['unknown_fields'] = [k for k in profile['unknown_fields'] if k not in ('clothes','xiangrui')]
    value=raw.get('iNutsNum')
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        profile['features']['potential']=value
    profile['warnings'] = [
        '来自用户导出的桌面版 HAR，仅在本机解析响应正文。',
        '未读取 Cookie、Token 或请求头，也不执行页面脚本。',
        '挂牌价格单位未验证，不自动写入行情库。',
    ] + desc['warnings'][1:]
    return profile
