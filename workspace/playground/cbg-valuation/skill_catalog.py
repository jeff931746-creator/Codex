"""Known skill IDs; unmapped entries must remain visible.

Reference: liushuang/myguhao, static/skill_info.json (inspected 2026-10-27).
This is a partial lookup, not a complete current official catalog.
"""
SOURCE = 'https://github.com/liushuang/myguhao/blob/master/server-api/src/main/resources/static/skill_info.json'
LIFE = {201:'强身术',202:'冥想',203:'暗器技巧',204:'打造技巧',205:'裁缝技巧',
        206:'中药医理',207:'炼金术',208:'烹饪技巧',209:'追捕技巧',210:'逃离技巧',
        211:'养生之道',212:'健身术',216:'巧匠之术',217:'熔炼技巧',218:'灵石技巧',
        230:'强壮',231:'淬灵之术',237:'神速'}
DRAGON = {25:'破浪诀',29:'九龙诀',30:'呼风唤雨',31:'龙腾',32:'逆鳞',33:'游龙术',34:'龙附'}
PLOT = {151:'古董评估',152:'建筑之术',153:'丹元济会',154:'变化之术',155:'火眼金睛',
        156:'调息',157:'打坐',158:'奇门遁甲',159:'妙手空空',160:'仙灵店铺',
        161:'宝石工艺',170:'翰墨之道',197:'丹青之道'}

def _official_maps(catalog):
    if not isinstance(catalog, dict):
        return {}, {}, {}
    def names(field, nested=False):
        source=catalog.get(field)
        if not isinstance(source,dict) or len(source)>500:
            return {}
        result={}
        for key,value in source.items():
            if not str(key).isdigit():
                continue
            name=value.get('name') if nested and isinstance(value,dict) else value
            if isinstance(name,str) and 0<len(name)<=40:
                result[int(key)]=name
        return result
    school=names('school_skill',True)
    life=names('life_skill')
    plot=names('ju_qing_skill')
    return school,life,plot

def describe_skills(raw, school, official_catalog=None):
    official_school,official_life,official_plot=_official_maps(official_catalog)
    result = {'school':[], 'life':[], 'plot':[], 'unknown':[]}
    for key,value in raw.items():
        if not str(key).isdigit() or not isinstance(value,int) or isinstance(value,bool):
            continue
        key = int(key)
        if key in official_school:
            group,name='school',official_school[key]
        elif key in official_life:
            group,name='life',official_life[key]
        elif key in official_plot:
            group,name='plot',official_plot[key]
        elif school=='龙宫' and key in DRAGON:
            group,name='school',DRAGON[key]
        elif key in LIFE:
            group,name='life',LIFE[key]
        elif key in PLOT:
            group,name='plot',PLOT[key]
        else:
            group,name='unknown','技能编号 '+str(key)
        display_level=value-1 if group=='plot' and key in (170,197) and value>0 else value
        result[group].append({'id':key,'name':name,'level':display_level,'mapped':group!='unknown'})
    for rows in result.values():
        rows.sort(key=lambda row:row['id'])
    live=bool(official_school or official_life or official_plot)
    return {'groups':result,'count':sum(map(len,result.values())),
            'source':'https://cbg-xyq.res.netease.com/js/game_auto_config.js' if live else SOURCE,
            'catalog_type':'official_page' if live else 'fallback_partial',
            'note':('名称来自当前藏宝阁页面的完整官方技能枚举；官方未公开名称的内部编号单独保留。' if live else
                    '当前仅使用部分备用映射；重新通过 Chrome 扩展同步可载入官方完整枚举。')}
