"""Versioned feature materialization and honest time-based model diagnostics."""
import json
import math
import re
from datetime import datetime, timezone

MODEL_VERSION = '175-listing-v5'
PARSER_VERSION = 'role-features-v2'

ROLE_CORE_FIELDS = ('level', 'school', 'realm')
ROLE_TRAINING_FIELDS = tuple(f'iExptSki{i}' for i in range(1, 5))
ROLE_TRAINING_CAP_FIELDS = tuple(f'iMaxExpt{i}' for i in range(1, 5))
PET_TRAINING_FIELDS = tuple(f'iBeastSki{i}' for i in range(1, 5))
ROLE_AUX_FIELDS = ('strong', 'speed')
ROLE_PROGRESS_FIELDS = ('achievement', 'qianyuan', 'potential', 'experience')
ROLE_ASSET_FIELDS = ('equipment_count', 'pet_count', 'mount_count',
                     'clothes_count', 'xiangrui_count', 'pet_skill_total',
                     'equipment_level_sum', 'equipment_high_level_count',
                     'equipment_gem_sum', 'equipment_gem_max',
                     'equipment_special_count', 'pet_high_skill_total',
                     'pet_growth_average', 'pet_growth_max',
                     'pet_neidan_total', 'pet_equipment_total')


def asset_summary(assets):
    """Materialize comparable asset structure without pretending it is price.

    These fields let market samples learn whether two whole roles actually
    carry similar equipment and summons.  They deliberately avoid fixed yuan
    values; rare named assets will need their own item-level market tables.
    """
    result = {key: 0 for key in ROLE_ASSET_FIELDS}
    if not isinstance(assets, list):
        return result
    equipment = [item for item in assets if item.get('category') == 'equipment']
    pets = [item for item in assets if item.get('category') == 'pet']
    result.update({
        'equipment_count': len(equipment),
        'pet_count': len(pets),
        'mount_count': sum(item.get('category') == 'mount' for item in assets),
        'clothes_count': sum(item.get('category') == 'clothes' for item in assets),
        'xiangrui_count': sum(item.get('category') == 'xiangrui' for item in assets),
        'equipment_level_sum': sum(_number(item.get('level')) or 0 for item in equipment),
        'equipment_high_level_count': sum((_number(item.get('level')) or 0) >= 150 for item in equipment),
        'pet_skill_total': sum(len(item.get('skills') or []) for item in pets),
        'pet_high_skill_total': sum(
            sum(str(skill.get('name') or '').startswith('高级')
                for skill in (item.get('skills') or []) if isinstance(skill, dict))
            for item in pets),
        'pet_neidan_total': sum(len(item.get('neidans') or []) for item in pets),
        'pet_equipment_total': sum(len(item.get('pet_equipment') or []) for item in pets),
    })
    gem_levels = []
    special_count = 0
    for item in equipment:
        desc = str((item.get('raw') or {}).get('cDesc') or '')
        match = re.search(r'锻炼等级\s*(\d+)', desc)
        if match:
            gem_levels.append(int(match.group(1)))
        special_count += sum(token in desc for token in ('特技：', '特效：', '套装效果：'))
    result['equipment_gem_sum'] = sum(gem_levels)
    result['equipment_gem_max'] = max(gem_levels, default=0)
    result['equipment_special_count'] = special_count
    growth = [(_number((item.get('raw') or {}).get('grow')) or 0) / 1000 for item in pets]
    result['pet_growth_average'] = round(sum(growth) / len(growth), 4) if growth else 0
    result['pet_growth_max'] = max(growth, default=0)
    return result


def setup_modeling(db):
    db.execute('''CREATE TABLE IF NOT EXISTS model_features (
        category TEXT NOT NULL, listing_id TEXT NOT NULL, observed_at TEXT NOT NULL,
        model_version TEXT NOT NULL, parser_version TEXT NOT NULL,
        completeness REAL NOT NULL, payload TEXT NOT NULL,
        PRIMARY KEY(category, listing_id, observed_at, model_version))''')
    db.execute('''CREATE TABLE IF NOT EXISTS model_backtests (
        id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, model_version TEXT NOT NULL,
        payload TEXT NOT NULL)''')


def _number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) else None


def role_feature_document(row):
    features = row.get('features') or {}
    skill_levels = []
    for key, value in features.items():
        if not key.startswith('skill_'):
            continue
        try:
            ident = int(key[6:])
        except ValueError:
            continue
        number = _number(value)
        if ident < 150 and number is not None:
            skill_levels.append(number)
    expected = (ROLE_CORE_FIELDS + ROLE_TRAINING_FIELDS + ROLE_TRAINING_CAP_FIELDS +
                PET_TRAINING_FIELDS + ROLE_AUX_FIELDS + ROLE_PROGRESS_FIELDS + ROLE_ASSET_FIELDS)
    present = sum(features.get(key) not in (None, '') for key in expected)
    # School skills form a variable-length group and therefore count once.
    completeness = (present + bool(skill_levels)) / (len(expected) + 1)
    return {
        'model_version': MODEL_VERSION,
        'parser_version': PARSER_VERSION,
        'sample_scope': features.get('sample_scope', 'empty_role'),
        'level': _number(features.get('level')),
        'school': features.get('school'),
        'realm': features.get('realm'),
        'training': {key: _number(features.get(key)) for key in ROLE_TRAINING_FIELDS},
        'training_caps': {key: _number(features.get(key)) for key in ROLE_TRAINING_CAP_FIELDS},
        'pet_training': {key: _number(features.get(key)) for key in PET_TRAINING_FIELDS},
        'school_skills': sorted(skill_levels, reverse=True),
        'auxiliary': {key: _number(features.get(key)) for key in ROLE_AUX_FIELDS},
        'progress': {key: _number(features.get(key)) for key in ROLE_PROGRESS_FIELDS},
        'assets': {key: _number(features.get(key)) for key in ROLE_ASSET_FIELDS},
        'completeness': round(completeness, 4),
    }


def feature_document(row):
    if row.get('category') == 'role':
        return role_feature_document(row)
    features = row.get('features') or {}
    return {'model_version': MODEL_VERSION, 'parser_version': PARSER_VERSION,
            'name': features.get('name'), 'completeness': 1.0 if features.get('name') else 0.0}


def materialize_snapshot(db, row):
    document = feature_document(row)
    db.execute('''INSERT OR REPLACE INTO model_features
        (category,listing_id,observed_at,model_version,parser_version,completeness,payload)
        VALUES (?,?,?,?,?,?,?)''',
        (row['category'], row['listing_id'], row['observed_at'], MODEL_VERSION,
         PARSER_VERSION, document['completeness'],
         json.dumps(document, ensure_ascii=False, sort_keys=True, allow_nan=False)))
    return document


def rebuild_features(db):
    count = 0
    for (payload,) in db.execute('SELECT payload FROM snapshots'):
        materialize_snapshot(db, json.loads(payload))
        count += 1
    return count


def model_state(db):
    row = db.execute('''SELECT COUNT(*), AVG(completeness), MIN(completeness), MAX(completeness)
        FROM model_features WHERE model_version=?''', (MODEL_VERSION,)).fetchone()
    level_rows = db.execute('''SELECT json_extract(payload,'$.level'), COUNT(*)
        FROM model_features WHERE model_version=? AND category='role'
        GROUP BY json_extract(payload,'$.level') ORDER BY COUNT(*) DESC''', (MODEL_VERSION,)).fetchall()
    latest = db.execute('SELECT payload FROM model_backtests WHERE model_version=? ORDER BY id DESC LIMIT 1',
                        (MODEL_VERSION,)).fetchone()
    return {'version': MODEL_VERSION, 'parser_version': PARSER_VERSION,
            'materialized_snapshots': row[0] or 0,
            'average_completeness': round(row[1] or 0, 3),
            'minimum_completeness': round(row[2] or 0, 3),
            'maximum_completeness': round(row[3] or 0, 3),
            'level_coverage': [{'level': r[0], 'snapshots': r[1]} for r in level_rows],
            'latest_backtest': json.loads(latest[0]) if latest else None,
            'target': 'listing_price', 'sale_price_enabled': False,
            'server_coefficient_enabled': False}


def save_backtest(db, result):
    created_at = datetime.now(timezone.utc).isoformat()
    result = {**result, 'created_at': created_at, 'model_version': MODEL_VERSION}
    db.execute('INSERT INTO model_backtests(created_at,model_version,payload) VALUES (?,?,?)',
               (created_at, MODEL_VERSION, json.dumps(result, ensure_ascii=False, allow_nan=False)))
    return result
