"""Local data ingestion only. No network or authentication bypass adapter."""
import hashlib
import json
from datetime import datetime, timezone
from urllib.parse import urlsplit

from engine import CATEGORIES, parse_time, validate_sample
from modeling import materialize_snapshot, setup_modeling

def setup(db):
    setup_modeling(db)
    compact_snapshots(db)
    db.execute('CREATE UNIQUE INDEX IF NOT EXISTS snapshots_one_per_product ON snapshots(category, listing_id)')
    db.execute('''CREATE TABLE IF NOT EXISTS ingestion_runs (
        id INTEGER PRIMARY KEY, created_at TEXT NOT NULL,
        status TEXT NOT NULL, summary TEXT NOT NULL)''')
    db.execute('''CREATE TABLE IF NOT EXISTS collection_sessions (
        id INTEGER PRIMARY KEY, started_at TEXT NOT NULL, updated_at TEXT NOT NULL,
        status TEXT NOT NULL, total INTEGER NOT NULL, completed INTEGER NOT NULL DEFAULT 0,
        failed INTEGER NOT NULL DEFAULT 0, source_url TEXT,
        inserted INTEGER NOT NULL DEFAULT 0, overwritten INTEGER NOT NULL DEFAULT 0,
        duplicates INTEGER NOT NULL DEFAULT 0, error_summary TEXT NOT NULL DEFAULT '[]')''')
    columns={row[1] for row in db.execute('PRAGMA table_info(collection_sessions)')}
    for name,definition in (
        ('inserted','INTEGER NOT NULL DEFAULT 0'),
        ('overwritten','INTEGER NOT NULL DEFAULT 0'),
        ('duplicates','INTEGER NOT NULL DEFAULT 0'),
        ('error_summary',"TEXT NOT NULL DEFAULT '[]'"),
    ):
        if name not in columns:
            db.execute(f'ALTER TABLE collection_sessions ADD COLUMN {name} {definition}')
    # Older sessions predate per-task outcome counters. Rebuild them from the
    # extension ingestion runs that occurred inside each session time window.
    for ident,started,updated,completed,inserted,overwritten,duplicates in db.execute(
        '''SELECT id,started_at,updated_at,completed,inserted,overwritten,duplicates
           FROM collection_sessions WHERE completed>0''').fetchall():
        if inserted or overwritten or duplicates:
            continue
        summaries=[json.loads(row[0]) for row in db.execute(
            '''SELECT summary FROM ingestion_runs WHERE created_at>=? AND created_at<=? ORDER BY id''',
            (started,updated)).fetchall()]
        summaries=[item for item in summaries if item.get('source_type')=='chrome_extension']
        if not summaries:
            continue
        db.execute('''UPDATE collection_sessions SET inserted=?,overwritten=?,duplicates=? WHERE id=?''',(
            sum(item.get('inserted',0) for item in summaries),
            sum(item.get('overwritten',0) for item in summaries),
            sum(item.get('duplicates',0) for item in summaries),ident))

def compact_snapshots(db):
    """Keep only the newest observation for each product and its matching features."""
    before = db.execute('SELECT COUNT(*) FROM snapshots').fetchone()[0]
    db.execute('''DELETE FROM snapshots WHERE rowid NOT IN (
        SELECT rowid FROM (
            SELECT rowid, ROW_NUMBER() OVER (
                PARTITION BY category, listing_id
                ORDER BY observed_at DESC, rowid DESC
            ) AS position
            FROM snapshots
        ) WHERE position=1
    )''')
    db.execute('''DELETE FROM model_features WHERE NOT EXISTS (
        SELECT 1 FROM snapshots
        WHERE snapshots.category=model_features.category
          AND snapshots.listing_id=model_features.listing_id
          AND snapshots.observed_at=model_features.observed_at
    )''')
    after = db.execute('SELECT COUNT(*) FROM snapshots').fetchone()[0]
    return before-after

def collection_session(db, data):
    now = datetime.now(timezone.utc).isoformat()
    action = data.get('action')
    if action == 'start':
        total = data.get('total')
        source_url = data.get('source_url')
        if isinstance(total, bool) or not isinstance(total, int) or not 1 <= total <= 1000:
            raise ValueError('采集数量必须为1至1000')
        parsed = urlsplit(source_url or '')
        if parsed.scheme != 'https' or parsed.hostname != 'xyq.cbg.163.com':
            raise ValueError('采集来源必须是藏宝阁页面')
        cursor = db.execute('INSERT INTO collection_sessions(started_at,updated_at,status,total,source_url) VALUES (?,?,?,?,?)',
                            (now, now, 'running', total, source_url))
        return {'id': cursor.lastrowid, 'status': 'running', 'total': total,
                'completed': 0, 'failed': 0, 'updated_at': now}
    if action == 'update':
        ident, status = data.get('id'), data.get('status')
        completed, failed = data.get('completed'), data.get('failed')
        inserted, overwritten = data.get('inserted',0), data.get('overwritten',0)
        duplicates, errors = data.get('duplicates',0), data.get('errors',[])
        if status not in ('running','completed','stopped','failed'):
            raise ValueError('无效采集状态')
        if any(isinstance(v, bool) or not isinstance(v, int) or v < 0
               for v in (ident, completed, failed, inserted, overwritten, duplicates)):
            raise ValueError('采集进度格式错误')
        if not isinstance(errors,list) or any(not isinstance(item,str) for item in errors):
            raise ValueError('采集错误摘要格式错误')
        row = db.execute('SELECT total FROM collection_sessions WHERE id=?',(ident,)).fetchone()
        if not row or completed + failed > row[0]:
            raise ValueError('采集任务不存在或进度超限')
        db.execute('''UPDATE collection_sessions SET updated_at=?,status=?,completed=?,failed=?,
                      inserted=?,overwritten=?,duplicates=?,error_summary=? WHERE id=?''',
                   (now,status,completed,failed,inserted,overwritten,duplicates,
                    json.dumps(errors[:10],ensure_ascii=False),ident))
        return {'id':ident,'status':status,'total':row[0],'completed':completed,
                'failed':failed,'inserted':inserted,'overwritten':overwritten,
                'duplicates':duplicates,'errors':errors[:10],'updated_at':now}
    raise ValueError('无效采集任务操作')

def normalize(row):
    if not isinstance(row, dict):
        raise ValueError('每条样本必须是对象')
    row = dict(row)
    validate_sample(row)
    if row.get('status', 'listed') not in ('listed', 'removed', 'sold', 'unknown'):
        raise ValueError('状态仅支持 listed/removed/sold/unknown')
    parsed = urlsplit(row['source_url'])
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        raise ValueError('来源必须是完整 HTTP(S) 链接')
    if parsed.username or parsed.password:
        raise ValueError('来源链接不能包含账号密码')
    if row['category'] == 'role' and not all(k in row['features'] for k in ('level', 'school', 'realm')):
        raise ValueError('角色样本缺少等级、门派或境界')
    if row['category'] != 'role' and not row['features'].get('name'):
        raise ValueError('资产属性中必须有 name，用于同类匹配')
    if 'empty_verified' in row and not isinstance(row['empty_verified'], bool):
        raise ValueError('empty_verified 必须是布尔值')
    row['observed_at'] = parse_time(row['observed_at']).isoformat()
    row['status'] = row.get('status', 'listed')
    # Test metadata and arbitrary top-level fields do not enter the pricing data.
    allowed = ('listing_id', 'category', 'name', 'server', 'price', 'observed_at',
               'source_url', 'status', 'empty_verified', 'features')
    row = {k: row[k] for k in allowed if k in row}
    json.dumps(row, allow_nan=False)
    return row

def encode(row):
    return json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)

def ingest(db, rows, source_type='local_import'):
    if not isinstance(rows, list) or not 1 <= len(rows) <= 3000:
        raise ValueError('请导入1至3000条样本')
    result = {'received': len(rows), 'inserted': 0, 'overwritten': 0, 'duplicates': 0,
              'conflicts': 0, 'rejected': 0, 'errors': [], 'categories': {},
              'source_type': source_type, 'network_requests': 0}
    for index, raw in enumerate(rows, 1):
        try:
            row = normalize(raw)
            product_key = (row['category'], row['listing_id'])
            key = (*product_key, row['observed_at'])
            payload = encode(row)
            existing = db.execute('''SELECT observed_at,payload FROM snapshots
                WHERE category=? AND listing_id=? ORDER BY observed_at DESC LIMIT 1''', product_key).fetchone()
            if existing:
                if existing[0] == row['observed_at'] and encode(json.loads(existing[1])) == payload:
                    result['duplicates'] += 1
                    continue
                if parse_time(row['observed_at']) < parse_time(existing[0]):
                    result['duplicates'] += 1
                    continue
                db.execute('DELETE FROM snapshots WHERE category=? AND listing_id=?', product_key)
                db.execute('DELETE FROM model_features WHERE category=? AND listing_id=?', product_key)
                result['overwritten'] += 1
            db.execute('INSERT INTO snapshots VALUES (?,?,?,?)', (*key, payload))
            materialize_snapshot(db, row)
            if not existing:
                result['inserted'] += 1
            c = row['category']
            result['categories'][c] = result['categories'].get(c, 0) + 1
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
            result['rejected'] += 1
            result['errors'].append({'row': index, 'reason': str(exc)})
    result['status'] = ('completed' if not result['rejected'] and not result['conflicts']
                        else 'partial' if result['inserted'] or result['overwritten'] or result['duplicates'] else 'rejected')
    result['batch_hash'] = hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    result['created_at'] = datetime.now(timezone.utc).isoformat()
    # Cap diagnostics returned to the UI; counts still describe the entire batch.
    result['errors'] = result['errors'][:100]
    cursor = db.execute('INSERT INTO ingestion_runs(created_at,status,summary) VALUES (?,?,?)',
                        (result['created_at'], result['status'], encode(result)))
    result['id'] = cursor.lastrowid
    return result

def collector_state(db):
    coverage = []
    for category in sorted(CATEGORIES):
        records = db.execute('SELECT listing_id,observed_at,payload FROM snapshots WHERE category=?', (category,)).fetchall()
        latest = {}
        for listing_id, observed_at, payload in records:
            if listing_id not in latest or parse_time(observed_at) > parse_time(latest[listing_id]['observed_at']):
                latest[listing_id] = json.loads(payload)
        now = datetime.now(timezone.utc)
        coverage.append({'category': category, 'snapshots': len(records), 'products': len(latest),
                         'servers': len({r['server'] for r in latest.values()}),
                         'fresh_listed': sum(r.get('status', 'listed') == 'listed' and
                                             0 <= (now-parse_time(r['observed_at'])).total_seconds() <= 7*86400
                                             for r in latest.values()),
                         'latest_at': max((r['observed_at'] for r in latest.values()), default=None)})
    runs = [{'id': r[0], **json.loads(r[1])} for r in db.execute('SELECT id,summary FROM ingestion_runs ORDER BY id DESC LIMIT 30')]
    extension_runs = [r for r in runs if r.get('source_type') == 'chrome_extension']
    session_rows=db.execute('''SELECT id,started_at,updated_at,status,total,completed,failed,source_url,
                               inserted,overwritten,duplicates,error_summary
                               FROM collection_sessions ORDER BY id DESC LIMIT 20''').fetchall()
    keys=('id','started_at','updated_at','status','total','completed','failed','source_url',
          'inserted','overwritten','duplicates','error_summary')
    sessions=[]
    for row in session_rows:
        session=dict(zip(keys,row))
        try: session['errors']=json.loads(session.pop('error_summary') or '[]')
        except json.JSONDecodeError: session['errors']=[]
        if session['status']=='running' and (datetime.now(timezone.utc)-parse_time(session['updated_at'])).total_seconds()>120:
            session['status']='interrupted'
        sessions.append(session)
    session=sessions[0] if sessions else None
    return {'network_status': 'chrome_extension' if extension_runs else 'not_configured',
            'network_requests': sum(r.get('received', 0) for r in extension_runs),
            'reason': ('Chrome 扩展已接入；详情请求使用当前浏览器登录状态，完整资料和价格快照保存在本机。'
                       if extension_runs else
                       '尚未收到扩展采集数据。可在藏宝阁列表页点击扩展中的“采集当前列表”。'),
            'current_session':session, 'sessions':sessions, 'coverage': coverage, 'runs': runs}
