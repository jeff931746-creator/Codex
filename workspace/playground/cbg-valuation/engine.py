"""Snapshot-based listing comparisons, independent of source adapters."""
import math
from datetime import datetime, timezone
from valuation_rules import RULE_VERSION, adjustment_between, is_pricing_feature
from modeling import MODEL_VERSION, feature_document

CATEGORIES = {'role', 'equipment', 'pet', 'item', 'appearance'}

def parse_time(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('采集时间必须带时区')
    return dt.astimezone(timezone.utc)

def validate_sample(row):
    for key in ('listing_id', 'category', 'name', 'server', 'price', 'observed_at', 'features', 'source_url'):
        if key not in row:
            raise ValueError('缺少字段：' + key)
    if row['category'] not in CATEGORIES or not isinstance(row['features'], dict) or not row['features']:
        raise ValueError('类别或属性不合法')
    if isinstance(row['price'], bool) or not isinstance(row['price'], (int, float)) or not math.isfinite(row['price']) or row['price'] <= 0:
        raise ValueError('挂牌价必须是大于零的有限数值')
    for key in ('listing_id', 'name', 'server', 'source_url'):
        if not isinstance(row[key], str) or not row[key].strip():
            raise ValueError(key + ' 必须为非空文本')
    if parse_time(row['observed_at']) > datetime.now(timezone.utc):
        raise ValueError('采集时间不能在未来')
    return row

def weighted_median(rows, price_key='price'):
    ordered = sorted(rows, key=lambda x: x[price_key])
    total = sum(x['weight'] for x in ordered)
    acc = 0
    for row in ordered:
        acc += row['weight']
        if acc >= total / 2:
            return row[price_key]

def weighted_quantile(rows, quantile, price_key='price'):
    if not 0 <= quantile <= 1:
        raise ValueError('分位数必须在0至1之间')
    ordered = sorted(rows, key=lambda x: x[price_key])
    total = sum(x['weight'] for x in ordered)
    threshold = total * quantile
    acc = 0
    for row in ordered:
        acc += row['weight']
        if acc >= threshold:
            return row[price_key]
    return ordered[-1][price_key]

def confidence_summary(rows, target):
    if not rows:
        return {'grade':'不足','score':0,'effective_samples':0,'target_completeness':0}
    effective = sum(row['weight'] for row in rows) / max(row['weight'] for row in rows)
    target_completeness = feature_document(target)['completeness']
    sample_completeness = sum(feature_document(row)['completeness'] * row['weight'] for row in rows) / sum(row['weight'] for row in rows)
    similarity = sum(row['similarity'] * row['weight'] for row in rows) / sum(row['weight'] for row in rows) / 100
    density = min(effective / 12, 1)
    score = round(100 * (.35 * density + .3 * target_completeness + .2 * sample_completeness + .15 * similarity))
    # A visually complete record must not create false confidence when the
    # comparable market is sparse.  High confidence needs at least twelve
    # effective observations; medium needs five.
    grade = ('高' if score >= 80 and effective >= 12 else
             '中' if score >= 60 and effective >= 5 else '低')
    return {'grade':grade,'score':score,'effective_samples':round(effective,1),
            'target_completeness':round(target_completeness,3),
            'sample_completeness':round(sample_completeness,3)}

def compare(target, samples, mode='normal', max_age_days=7, now=None):
    if mode not in ('normal', 'exact'):
        raise ValueError('未知估价模式')
    if target.get('category') not in CATEGORIES or not target.get('features') or not target.get('server'):
        raise ValueError('请填写类别、区服和属性')
    features = target['features']
    # Level and advancement define the hard market segment.  School remains a
    # strong similarity feature: normal mode may expand across schools when a
    # school-specific pool is sparse; exact mode keeps the same school.
    required = ('level', 'realm') if target['category'] == 'role' else ('name',)
    if any(k not in features or features[k] == '' for k in required):
        raise ValueError('目标缺少必要属性：' + '、'.join(required))
    now = now or datetime.now(timezone.utc)
    latest = {}
    for s in samples:
        key = (s['category'], s['listing_id'])
        if key not in latest or parse_time(s['observed_at']) > parse_time(latest[key]['observed_at']):
            latest[key] = s
    matches = []
    excluded = {'时效或在售状态不符': 0, '类别不同': 0,
                '资料完整度不同': 0, '未核验为空号': 0, '必要属性不同': 0,
                '修炼或技能不同': 0, '补充属性缺失或不符': 0}
    for s in latest.values():
        age = (now - parse_time(s['observed_at'])).total_seconds() / 86400
        if age < 0 or age > max_age_days or s.get('status', 'listed') != 'listed':
            excluded['时效或在售状态不符'] += 1
            continue
        # Server is deliberately not a matching condition.  The base estimate
        # uses comparable listings across all servers; a separate popularity
        # coefficient can be applied later when verified server data exists.
        if s['category'] != target['category']:
            excluded['类别不同'] += 1
            continue
        sf = s['features']
        if s['category'] == 'role':
            target_scope = features.get('sample_scope', 'empty_role')
            sample_scope = sf.get('sample_scope', 'empty_role')
            if target_scope != sample_scope:
                excluded['资料完整度不同'] += 1
                continue
            if target_scope == 'empty_role' and s.get('empty_verified') is not True:
                excluded['未核验为空号'] += 1
                continue
        if any(sf.get(k) != features[k] for k in required):
            excluded['必要属性不同'] += 1
            continue
        if s['category'] == 'role' and mode == 'exact' and sf.get('school') != features.get('school'):
            excluded['必要属性不同'] += 1
            continue
        price_adjustments, missing_pricing = ({}, [])
        if s['category'] == 'role':
            price_adjustments, missing_pricing = adjustment_between(features, sf)
            # Precise means every available cultivation/skill field is valued;
            # it does not mean an identical whole role must exist.  A sample
            # missing an entire priced component is not safe to adjust.
            if missing_pricing:
                excluded['修炼或技能不同'] += 1
                continue
        distance, compared_weight, differences, missing = 0., 0., [], False
        for key, val in features.items():
            if key in required or key == 'sample_scope' or is_pricing_feature(key) or val is None or val == '':
                continue
            if key == 'school':
                feature_weight = 4.0
            elif key.startswith(('equipment_', 'pet_')):
                feature_weight = 2.2
            elif key in ('clothes_count', 'xiangrui_count', 'mount_count'):
                feature_weight = 1.4
            else:
                feature_weight = .18 if key.startswith('skill_') else .55 if key.startswith(('iExpt','iMaxExpt','iBeast')) else 1.
            if key not in sf or sf[key] is None:
                # Unknown is not zero.  Keep the comparable sample with a
                # modest confidence penalty and expose the missing field.
                distance += feature_weight * .35
                compared_weight += feature_weight
                differences.append(f'{key}: 样本未记录')
                continue
            other = sf[key]
            if other == val:
                compared_weight += feature_weight
                continue
            if isinstance(val, (int, float)) and not isinstance(val, bool) and isinstance(other, (int, float)) and not isinstance(other, bool):
                delta = min(abs(other - val) / max(abs(val), 10), 2.)
                distance += feature_weight * delta
                compared_weight += feature_weight
            else:
                distance += feature_weight
                compared_weight += feature_weight
            differences.append(f'{key}: 目标 {val} / 样本 {other}')
        if missing:
            excluded['补充属性缺失或不符'] += 1
            continue
        distance = distance / max(compared_weight, 1.)
        adjustment = round(sum(price_adjustments.values()), 2)
        adjusted_price = max(round(s['price'] + adjustment, 2), 1)
        adjustment_text = [f'{name}校正 {amount:+.0f}元' for name, amount in price_adjustments.items() if amount]
        matches.append({**s, 'weight': 1 / (1 + distance * 5) / (1 + age / 7),
                        'adjusted_price': adjusted_price, 'price_adjustment': adjustment,
                        'adjustment_breakdown': price_adjustments,
                        'differences': adjustment_text + differences,
                        'similarity': round(100 / (1 + distance))})
    matches.sort(key=lambda x: (-x['weight'], x['price']))
    match_scope = '同条件'
    if target['category'] == 'role':
        same_school = [row for row in matches
                       if row.get('features', {}).get('school') == features.get('school')]
        if mode == 'exact' or len(same_school) >= 3:
            matches = same_school
            match_scope = '同等级、境界、门派'
        else:
            match_scope = '同等级、境界（门派样本不足，已扩展）'
    # With the current cross-server market, distant comparables add more
    # listing-price noise than evidence.  Leave-one-out calibration on the
    # deduplicated sample set selects the ten closest adjusted listings.
    selected = matches if mode == 'exact' else matches[:10]
    confidence = confidence_summary(selected, target)
    if len(selected) < 3:
        scope_note = ('完整角色同等级、境界' if
                      target.get('category') == 'role' and features.get('sample_scope') == 'full_role'
                      else '同条件')
        return {'status': 'insufficient', 'count': len(selected), 'price': None,
                'low': None, 'high': None, 'samples': selected, 'excluded': excluded,
                'confidence': confidence, 'model_version': MODEL_VERSION,
                'match_scope': match_scope,
                'reason': f'{scope_note}至少需要3个有效样本，当前还缺{3-len(selected)}个'}
    # Listing data is right-skewed and contains aspirational asks.  The
    # standard baseline therefore uses a weighted lower-middle quantile rather
    # than the raw median.  It remains a listing reference, not a sale price.
    prices = sorted(s['adjusted_price'] for s in selected)
    point_quantile = .20 if mode == 'exact' else .40
    return {'status': 'ready', 'count': len(selected),
            'price': weighted_quantile(selected, point_quantile, 'adjusted_price'),
            'low': weighted_quantile(selected, .15, 'adjusted_price'),
            'high': weighted_quantile(selected, .75, 'adjusted_price'),
            'samples': selected, 'excluded': excluded, 'rule_version': RULE_VERSION,
            'model_version': MODEL_VERSION, 'confidence': confidence,
            'match_scope': match_scope,
            'price_target': 'listing_price',
            'reason': ('修炼技能校正后的加权20%低位挂牌' if mode == 'exact' else
                       '修炼技能分项校正后的加权40%稳健挂牌基准')}

def backtest(samples, max_age_days=30):
    """Cross-sectional leave-one-product-out evaluation.

    Marketplace result pages are commonly collected in price order, so their
    observation timestamps are not an independent time series.  Treating the
    collection order as walk-forward history would train on cheap rows and
    test on expensive rows.  Each prediction therefore uses every other
    current product and never its own listing id.
    """
    ordered = sorted((s for s in samples if s.get('category') == 'role' and
                      s.get('features', {}).get('level') == 175 and s.get('status', 'listed') == 'listed'),
                     key=lambda row: parse_time(row['observed_at']))
    predictions = []
    evaluation_now = max((parse_time(row['observed_at']) for row in ordered), default=datetime.now(timezone.utc))
    for actual in ordered:
        history = [row for row in ordered if row['listing_id'] != actual['listing_id']]
        if len(history) < 3:
            continue
        target = {'category':'role','name':actual['name'],'server':actual['server'],
                  'features':actual['features']}
        result = compare(target, history, 'normal', max_age_days, evaluation_now)
        if result['status'] != 'ready':
            continue
        error = result['price'] - actual['price']
        baseline_rows = [{**row, 'weight':1.0} for row in history
                         if row.get('features', {}).get('level') == actual['features'].get('level') and
                         row.get('features', {}).get('school') == actual['features'].get('school') and
                         row.get('features', {}).get('realm') == actual['features'].get('realm')]
        baseline = weighted_median(baseline_rows) if baseline_rows else None
        predictions.append({'listing_id':actual['listing_id'],'observed_at':actual['observed_at'],
                            'actual':actual['price'],'predicted':result['price'],'error':round(error,2),
                            'absolute_error':round(abs(error),2),
                            'absolute_percentage_error':round(abs(error)/actual['price']*100,2),
                            'baseline':baseline,
                            'baseline_absolute_percentage_error':(
                                round(abs(baseline-actual['price'])/actual['price']*100,2)
                                if baseline is not None else None),
                            'confidence':result['confidence']})
    if not predictions:
        return {'status':'insufficient','evaluated':0,'predictions':[],
                'reason':'时间留出后没有至少3个更早的同类样本'}
    abs_errors = sorted(row['absolute_error'] for row in predictions)
    pct_errors = sorted(row['absolute_percentage_error'] for row in predictions)
    signed = sorted(row['error'] for row in predictions)
    middle = lambda values: values[len(values)//2]
    baseline_pct = sorted(row['baseline_absolute_percentage_error'] for row in predictions
                          if row['baseline_absolute_percentage_error'] is not None)
    return {'status':'ready','evaluated':len(predictions),
            'median_absolute_error':middle(abs_errors),
            'median_absolute_percentage_error':middle(pct_errors),
            'baseline_median_absolute_percentage_error':middle(baseline_pct) if baseline_pct else None,
            'improves_on_baseline':bool(baseline_pct and middle(pct_errors) < middle(baseline_pct)),
            'median_signed_error':middle(signed),
            'high_bias_rate':round(sum(row['error'] > 0 for row in predictions)/len(predictions),3),
            'predictions':predictions[-100:]}
