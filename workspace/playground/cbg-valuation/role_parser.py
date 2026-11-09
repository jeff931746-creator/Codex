"""Parse a user-provided get_equip_detail response offline."""
import json
import re
from skill_catalog import describe_skills

def parse_role_response(payload, official_catalog=None):
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict) or not isinstance(payload.get('equip'), dict):
        raise ValueError('请提供 get_equip_detail 的完整响应，顶层应有 equip 对象')
    equip = payload['equip']
    other = equip.get('other_info')
    if not isinstance(other, dict):
        raise ValueError('响应中没有角色 other_info，不能作为角色资料解析')
    card = equip.get('card_style') or {}
    school = card.get('school') or equip.get('format_equip_name')
    server = equip.get('server_name')
    level = other.get('iGrade', equip.get('equip_level'))
    if not school or not server or not isinstance(level, int):
        raise ValueError('角色等级、门派或区服缺失')
    summary = other.get('summary') or equip.get('desc_sumup_short') or ''
    realm = None
    holy = re.search(r'化圣([一二三四五六七八九])重?', summary)
    if holy:
        realm = '化圣' + holy.group(1) + '重'
    else:
        if '渡劫' in summary:
            realm = '渡劫'
        elif '未飞升' in summary:
            realm = '未飞升'
        elif '飞升' in summary:
            realm = '飞升'
    features = {'level': level, 'school': school}
    if realm is not None:
        features['realm'] = realm
    for source, dest in [('xiulian','cultivation'),('pet_xiulian','pet_cultivation'),('AchPointTotal','achievement')]:
        value = other.get(source)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            features[dest] = value
    # Preserve original keys: no unverified skill-ID/name mapping.
    for key in [f'iExptSki{i}' for i in range(1,6)]+[f'iMaxExpt{i}' for i in range(1,6)]+[f'iBeastSki{i}' for i in range(1,5)]:
        value = other.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            features[key] = value
    skills = other.get('all_skills') or {}
    if not isinstance(skills, dict):
        raise ValueError('all_skills 应为对象')
    for key,value in skills.items():
        if str(key).isdigit() and isinstance(value,int) and not isinstance(value,bool):
            features['skill_'+str(key)] = value
    for ident,name in [('230','strong'),('237','speed')]:
        value=skills.get(ident)
        if isinstance(value,int) and not isinstance(value,bool):
            features[name]=value
    return {'name':other.get('cName') or f'{level}级{school}', 'server':server,
            'area':equip.get('area_name'), 'category':'role', 'features':features,
            'listing_id':equip.get('eid'), 'server_id':equip.get('serverid'),
            'description_version':equip.get('equip_desc_version'),
            'source_url':equip.get('equip_detail_url'),
            'status_desc':equip.get('status_desc') or (equip.get('selling_info_data') or {}).get('status'),
            'raw_price':equip.get('price'), 'price_unit':'unverified',
            'response_time':payload.get('server_now_time'), 'source_type':'user_provided_response',
            'skills':describe_skills(skills,school,official_catalog),
            'unknown_fields':[k for k in ['qianyuan','strong','speed','clothes','xiangrui'] if k not in features],
            'warnings':['来自手动提供的响应，未进行联网读取。',
                        '挂牌价格单位未验证，不换算成人民币，不自动写入行情库。',
                        '乾元丹与未映射字段保留未知；技能名称映射尚未覆盖全部门派。',
                        '此响应不能证明角色是已核验空号。']}
