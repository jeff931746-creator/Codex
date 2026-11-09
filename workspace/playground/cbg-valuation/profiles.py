"""Persist parsed user-provided profiles separately from market samples."""
import json
from datetime import datetime, timezone

def setup_profiles(db):
    db.execute('CREATE TABLE IF NOT EXISTS offline_profiles (listing_id TEXT PRIMARY KEY, saved_at TEXT NOT NULL, payload TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS market_profiles (listing_id TEXT PRIMARY KEY, saved_at TEXT NOT NULL, payload TEXT NOT NULL)')

def save_profile(db, profile):
    ident=profile.get('listing_id')
    if not isinstance(ident,str) or not ident:
        return profile
    existing=db.execute('SELECT payload FROM offline_profiles WHERE listing_id=?',(ident,)).fetchone()
    if existing:
        old=json.loads(existing[0])
        if (old.get('description') and not profile.get('description') and
            old.get('description_version')==profile.get('description_version') and
            old.get('description_version')):
            profile={**profile,'description':old['description']}
    profile={**profile,'saved_at':datetime.now(timezone.utc).isoformat()}
    db.execute('INSERT OR REPLACE INTO offline_profiles VALUES (?,?,?)',
               (ident,profile['saved_at'],json.dumps(profile,ensure_ascii=False,allow_nan=False)))
    return profile

def save_market_profile(db, profile):
    """Persist collector detail without exposing it in the user's role history."""
    ident=profile.get('listing_id')
    if not isinstance(ident,str) or not ident:
        return profile
    profile={**profile,'saved_at':datetime.now(timezone.utc).isoformat()}
    db.execute('INSERT OR REPLACE INTO market_profiles VALUES (?,?,?)',
               (ident,profile['saved_at'],json.dumps(profile,ensure_ascii=False,allow_nan=False)))
    return profile

def get_profile(db, ident=None):
    if ident:
        row=db.execute('SELECT payload FROM offline_profiles WHERE listing_id=?',(ident,)).fetchone()
    else:
        row=db.execute('SELECT payload FROM offline_profiles ORDER BY saved_at DESC LIMIT 1').fetchone()
    return json.loads(row[0]) if row else None

def list_profiles(db, limit=60):
    rows=db.execute(
        'SELECT listing_id,saved_at,payload FROM offline_profiles ORDER BY saved_at DESC LIMIT ?',
        (limit,)
    ).fetchall()
    result=[]
    for ident,saved_at,payload in rows:
        profile=json.loads(payload)
        features=profile.get('features') or {}
        result.append({
            'listing_id':ident,
            'saved_at':saved_at,
            'name':profile.get('name') or f"{features.get('level','?')}级{features.get('school','角色')}",
            'server':profile.get('server') or '未知服务器',
            'level':features.get('level'),
            'school':features.get('school'),
            'status_desc':profile.get('status_desc'),
            'source_url':profile.get('source_url'),
        })
    return result
