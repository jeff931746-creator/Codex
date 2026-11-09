import json
import mimetypes
import re
import ssl
import sqlite3
import certifi
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from urllib.request import urlopen
from engine import compare, backtest
from ingestion import setup, ingest, collector_state, collection_session
from role_parser import parse_role_response
from desc_parser import parse_bundle, parse_desktop_bundle
from profiles import setup_profiles, save_profile, save_market_profile, get_profile, list_profiles
from modeling import setup_modeling, rebuild_features, model_state, save_backtest, asset_summary

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'data' / 'market.sqlite3'
EXTENSION_HEADER = 'X-CBG-Extension'
EXTENSION_ROUTES = {'/api/parse-desktop-bundle', '/api/collect-desktop-bundle', '/api/collection-session'}
ICON_ROOT = 'https://cbg-xyq.res.netease.com/images/'
ICON_ENUM = {
    'equipment':('big/','.gif'),'pet':('pets/small/','.gif'),'mount':('riders/','.gif'),
    'clothes':('clothes/','0000.gif'),'xiangrui':('xiangrui/','.gif'),
    'role_skill':('role_skills/','.gif'),'pet_skill':('pet_child_skill/','.gif'),'pet_equipment':('equip/small/','.gif'),
    'pet_accessory':('pet_shipin/small/','.png'),'neidan':('neidan/','.jpg')
}
ICON_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
REQUIRED_ASSET_GROUPS = {'AllEquip', 'AllSummon', 'AllRider', 'ExAvt', 'HugeHorse'}

def mapped_icon_path(kind, ident):
    if kind not in ICON_ENUM or not isinstance(ident,str) or not re.fullmatch(r'\d{1,12}',ident):
        return None
    prefix,suffix=ICON_ENUM[kind]
    if kind in ('role_skill','pet_skill'):
        ident=ident.zfill(4)
    return prefix+ident+suffix
def is_extension_request(origin, route, marker):
    return (isinstance(origin, str) and origin.startswith('chrome-extension://') and
            route in EXTENSION_ROUTES and marker == 'sync-v1')

def mark_asset_scope(profile):
    """Mark whether a parsed role contains every value-bearing asset group."""
    description = profile.get('description') or {}
    present = set(description.get('present_groups') or [])
    complete = REQUIRED_ASSET_GROUPS.issubset(present)
    profile.setdefault('features', {})['sample_scope'] = 'full_role' if complete else 'role_core'
    profile['features']['asset_detail_complete'] = complete
    return profile

def full_role_sample(profile):
    """Convert one parsed detail page into a traceable whole-role listing snapshot."""
    try:
        price = float(profile.get('raw_price'))
    except (TypeError, ValueError):
        raise ValueError('列表中没有识别到有效挂牌价')
    if price <= 0:
        raise ValueError('列表中没有识别到有效挂牌价')
    profile = mark_asset_scope(profile)
    features = dict(profile.get('features') or {})
    description = profile.get('description') or {}
    assets = description.get('assets')
    present = set(description.get('present_groups') or [])
    # Missing groups are unknown, not empty.  A confirmed zero is only written
    # when the corresponding official detail group was present in the page.
    groups = [('equipment','equipment_count','AllEquip'), ('pet','pet_count','AllSummon'),
              ('mount','mount_count','AllRider'), ('clothes','clothes_count','ExAvt'),
              ('xiangrui','xiangrui_count','HugeHorse')]
    if isinstance(assets, list):
        summary = asset_summary(assets)
        for category, key, source_group in groups:
            if source_group in present:
                features[key] = summary[key]
        if 'AllEquip' in present:
            for key in ('equipment_level_sum', 'equipment_high_level_count',
                        'equipment_gem_sum', 'equipment_gem_max', 'equipment_special_count'):
                features[key] = summary[key]
        if 'AllSummon' in present:
            for key in ('pet_skill_total', 'pet_high_skill_total', 'pet_growth_average',
                        'pet_growth_max', 'pet_neidan_total', 'pet_equipment_total'):
                features[key] = summary[key]
    return {'listing_id': profile.get('listing_id'), 'category': 'role',
            'name': profile.get('name'), 'server': profile.get('server'), 'price': price,
            'observed_at': profile.get('response_time') or datetime.now(timezone.utc).isoformat(),
            'source_url': profile.get('source_url'), 'status': 'listed', 'features': features}

def refresh_market_asset_features(db):
    """Upgrade stored market snapshots from their retained detail payloads."""
    updated = 0
    for (payload,) in db.execute('SELECT payload FROM market_profiles'):
        profile = json.loads(payload)
        try:
            sample = full_role_sample(profile)
        except (TypeError, ValueError):
            continue
        row = db.execute('SELECT observed_at,payload FROM snapshots WHERE category=? AND listing_id=?',
                         ('role', sample['listing_id'])).fetchone()
        if not row:
            continue
        current = json.loads(row[1])
        sample['observed_at'] = current.get('observed_at') or row[0]
        sample['status'] = current.get('status', 'listed')
        db.execute('UPDATE snapshots SET payload=? WHERE category=? AND listing_id=?',
                   (json.dumps(sample, ensure_ascii=False, allow_nan=False), 'role', sample['listing_id']))
        updated += 1
    return updated

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def initialize():
    DB.parent.mkdir(exist_ok=True)
    with connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS snapshots (category TEXT, listing_id TEXT, observed_at TEXT, payload TEXT, PRIMARY KEY(category, listing_id, observed_at))')
        db.execute('CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, created_at TEXT, payload TEXT)')
        setup(db)
        setup_profiles(db)
        setup_modeling(db)
        refresh_market_asset_features(db)
        rebuild_features(db)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'public'), **kwargs)

    def send_json(self, value, status=200):
        body = json.dumps(value, ensure_ascii=False, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        origin = self.headers.get('Origin')
        route = urlsplit(self.path).path
        if is_extension_request(origin, route, self.headers.get(EXTENSION_HEADER)):
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Vary', 'Origin')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        origin = self.headers.get('Origin')
        route = urlsplit(self.path).path
        requested = {item.strip().lower() for item in self.headers.get('Access-Control-Request-Headers','').split(',')}
        if not is_extension_request(origin, route, 'sync-v1') or EXTENSION_HEADER.lower() not in requested:
            return self.send_json({'error':'不接受该跨域预检'}, 403)
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, ' + EXTENSION_HEADER)
        self.send_header('Access-Control-Max-Age', '600')
        self.send_header('Vary', 'Origin')
        self.end_headers()

    def do_GET(self):
        route = urlsplit(self.path).path
        if route == '/api/icon':
            query=parse_qs(urlsplit(self.path).query)
            icon_path=mapped_icon_path(query.get('kind',[None])[0],query.get('id',[None])[0])
            if not icon_path:
                return self.send_json({'error':'无效图标枚举'},400)
            try:
                with urlopen(ICON_ROOT+icon_path,timeout=8,context=ICON_SSL_CONTEXT) as response:
                    body=response.read(1_000_001)
                if not body or len(body)>1_000_000:
                    raise ValueError('图标响应异常')
                self.send_response(200)
                self.send_header('Content-Type',mimetypes.guess_type(icon_path)[0] or 'application/octet-stream')
                self.send_header('Cache-Control','no-store')
                self.send_header('Content-Length',str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception:
                self.send_json({'error':'官方图标暂不可用'},502)
            return
        if route == '/api/profile':
            ident=parse_qs(urlsplit(self.path).query).get('listing_id',[None])[0]
            with connect() as db:
                profile=get_profile(db,ident)
            return self.send_json({'profile':profile})
        if route == '/api/profiles':
            with connect() as db:
                profiles=list_profiles(db)
            return self.send_json({'profiles':profiles})
        if route == '/api/state':
            with connect() as db:
                samples = [json.loads(r[0]) for r in db.execute('SELECT payload FROM snapshots ORDER BY observed_at DESC')]
                reports = [{'id': r['id'], 'created_at': r['created_at'], **json.loads(r['payload'])}
                           for r in db.execute('SELECT * FROM reports ORDER BY id DESC LIMIT 40')]
                collector = collector_state(db)
                model = model_state(db)
            self.send_json({'samples': samples, 'reports': reports, 'collector': collector, 'model': model})
        elif route.startswith('/api/'):
            self.send_json({'error': '接口不存在'}, 404)
        else:
            super().do_GET()

    def do_POST(self):
        route = urlsplit(self.path).path
        origin = self.headers.get('Origin')
        local_request = origin in (None, 'http://' + self.headers.get('Host', ''))
        extension_request = is_extension_request(origin, route, self.headers.get(EXTENSION_HEADER))
        # Only the local UI and the narrowly scoped Chrome extension endpoint may mutate data.
        if not local_request and not extension_request:
            return self.send_json({'error': '不接受跨站请求'}, 403)
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self.send_json({'error': '仅接受 JSON'}, 415)
        try:
            length = int(self.headers.get('Content-Length', 0))
            if not 0 < length <= 2_000_000:
                raise ValueError('请求大小超限或为空')
            data = json.loads(self.rfile.read(length))
            if route == '/api/parse-role-response':
                profile=parse_role_response(data)
                with connect() as db:
                    profile=save_profile(db,profile)
                return self.send_json(profile)
            if route == '/api/parse-offline-bundle':
                profile=parse_bundle(data)
                with connect() as db:
                    profile=save_profile(db,profile)
                return self.send_json(profile)
            if route == '/api/parse-desktop-bundle':
                profile=mark_asset_scope(parse_desktop_bundle(data))
                with connect() as db:
                    profile=save_profile(db,profile)
                return self.send_json(profile)
            if route == '/api/collect-desktop-bundle':
                profile=mark_asset_scope(parse_desktop_bundle(data))
                sample=full_role_sample(profile)
                with connect() as db:
                    profile=save_market_profile(db,profile)
                    result=ingest(db,[sample],source_type='chrome_extension')
                return self.send_json({'profile':profile,'ingestion':result})
            if route == '/api/collection-session':
                with connect() as db:
                    result=collection_session(db,data)
                return self.send_json(result)
            if route == '/api/import':
                rows = data if isinstance(data, list) else data.get('samples')
                with connect() as db:
                    result = ingest(db, rows)
                return self.send_json(result)
            if route == '/api/evaluate':
                targets = data.get('targets')
                if not isinstance(targets, list) or not 1 <= len(targets) <= 100:
                    raise ValueError('请提供1至100个估价分项')
                mode = data.get('mode', 'normal')
                days = int(data.get('days', 7))
                if days not in (1, 3, 7, 30):
                    raise ValueError('无效样本时效')
                with connect() as db:
                    samples = [json.loads(r[0]) for r in db.execute('SELECT payload FROM snapshots')]
                    components = [{'target': target, **compare(target, samples, mode, days)} for target in targets]
                    ready = all(c['status'] == 'ready' for c in components)
                    result = {'mode': mode, 'name': data.get('name', '未命名角色'), 'days': days,
                              'components': components, 'total': sum(c['price'] for c in components) if ready else None,
                              'status': 'ready' if ready else 'incomplete',
                              'coverage': '当前数据库全服有效样本；暂未应用区服热度系数'}
                    db.execute('INSERT INTO reports(created_at,payload) VALUES (?,?)',
                               (datetime.now(timezone.utc).isoformat(), json.dumps(result, ensure_ascii=False, allow_nan=False)))
                return self.send_json(result)
            if route == '/api/backtest':
                with connect() as db:
                    samples = [json.loads(r[0]) for r in db.execute('SELECT payload FROM snapshots')]
                    result = save_backtest(db, backtest(samples))
                return self.send_json(result)
            self.send_json({'error': '接口不存在'}, 404)
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            self.send_json({'error': str(exc)}, 400)

if __name__ == '__main__':
    initialize()
    print('估价工作台：http://127.0.0.1:8765', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8765), Handler).serve_forever()
