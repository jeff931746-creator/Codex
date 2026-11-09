"""Versioned, auditable adjustments for role training and skills.

The values are market reference increments, not recovery of historical spend.
Initial anchors come from the two valuation references reviewed on 2026-10-28;
they must later be calibrated against collected listings and real outcomes.
"""

from bisect import bisect_left


RULE_VERSION = '2026-10-public-model-v2'

# The September reference table gives one combined quote for the relevant
# offensive cultivation plus the two defensive cultivations at each level.
PERSON_TRAINING_ANCHORS = {
    129: ((15, 10, 900), (20, 15, 1400), (21, 15, 1750),
          (20, 20, 1850), (21, 21, 2100)),
    159: ((20, 15, 2300), (20, 20, 2650), (21, 20, 3700),
          (25, 25, 4600)),
    175: ((20, 20, 3650), (25, 20, 4550), (25, 25, 5400)),
}

# Public valuation guidance gives 15/20/25-level per-item anchors.  Piecewise
# interpolation preserves every recorded level instead of collapsing to a sum.
PET_TRAINING_ANCHORS = ((0, 0), (15, 100), (20, 400), (25, 800))

# 175 school-skill increments visible in the September reference.  Five or
# more skills were not assigned a stable numeric quote there, so the verified
# four-skill value is conservatively capped rather than invented.
SCHOOL_SKILL_175 = (0, 700, 1300, 1800, 2200)

# Strong/Speed values that were legible in the reference table.  Values outside
# this observed range use endpoint slopes and are flagged by the caller only as
# provisional market adjustments.
AUXILIARY_LEVEL_VALUES = {
    10: 50, 20: 100, 21: 110, 22: 120, 23: 130, 24: 150,
    25: 160, 26: 180, 27: 190, 28: 210, 29: 230, 30: 250,
    31: 270, 32: 290, 33: 310, 34: 330, 35: 360, 36: 380,
    37: 410, 38: 440, 39: 470, 40: 500, 41: 550,
    42: 600, 43: 650, 44: 700, 45: 750, 46: 800, 47: 880,
    48: 1000, 49: 1150, 50: 1300, 51: 1500, 52: 1700,
    53: 1900, 54: 2100, 55: 2300, 56: 2500, 57: 2700, 58: 2900,
}


def _number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _linear(points, value):
    if value <= points[0][0]:
        return points[0][1]
    if value >= points[-1][0]:
        left, right = points[-2], points[-1]
    else:
        index = bisect_left([point[0] for point in points], value)
        left, right = points[index - 1], points[index]
    span = right[0] - left[0]
    return left[1] + (value - left[0]) * (right[1] - left[1]) / span


def person_training_value(features):
    values = [_number(features.get(f'iExptSki{i}')) for i in range(1, 5)]
    level = _number(features.get('level'))
    if level not in PERSON_TRAINING_ANCHORS or any(value is None for value in values):
        return None
    # A role normally prices its relevant attack or spell cultivation, while
    # both defensive cultivations must be present.  Keep all four raw fields;
    # only this market adjustment uses the stronger offensive cultivation.
    offense = max(values[0], values[2])
    defense = min(values[1], values[3])
    anchors = PERSON_TRAINING_ANCHORS[level]
    # Use the highest fully reached published tier.  This is monotonic and does
    # not invent prices between configurations that the source did not quote.
    reached = [quote for off, resist, quote in anchors
               if offense >= off and defense >= resist]
    floor = float(max(reached) if reached else min(quote for _, _, quote in anchors))
    # Smooth the old hard tiers by interpolating toward the nearest better
    # published configuration.  Published quotes remain the boundaries.
    better = [(abs(off-offense)+abs(resist-defense), off, resist, quote)
              for off, resist, quote in anchors if off >= offense and resist >= defense]
    if better:
        _, next_off, next_def, next_quote = min(better)
        span = max((next_off-offense) + (next_def-defense), 1)
        progress = max(0.0, 1.0 - span / 10.0)
        floor += (next_quote - floor) * progress
    return floor


def training_cap_value(features):
    values = [_number(features.get(f'iExptSki{i}')) for i in range(1, 5)]
    caps = [_number(features.get(f'iMaxExpt{i}')) for i in range(1, 5)]
    if any(value is None for value in values + caps):
        return None
    # Upper limits have real replacement cost.  Keep the premium conservative
    # until the market backtest can learn a stable coefficient.
    return min(sum(max(cap-current, 0) for cap,current in zip(caps,values)), 20) * 25.0


def pet_training_value(features):
    values = [_number(features.get(f'iBeastSki{i}')) for i in range(1, 5)]
    if any(value is None for value in values):
        return None
    # Attack/spell control are more liquid than the two defensive controls.
    weights = (1.15, .85, 1.15, .85)
    return sum(_linear(PET_TRAINING_ANCHORS, value) * weight
               for value, weight in zip(values, weights))


def school_skill_value(features):
    level = _number(features.get('level'))
    if level != 175:
        return 0.0
    # Current official skill IDs for school skills are below the plot/life
    # ranges.  Both target and sample already share the same school.
    levels = []
    for key, value in features.items():
        if not key.startswith('skill_'):
            continue
        try:
            ident = int(key[6:])
        except ValueError:
            continue
        value = _number(value)
        if ident < 150 and value is not None:
            levels.append(value)
    if not levels:
        return None
    # Preserve the verified four-skill/2200 anchor while valuing every recorded
    # level continuously.  Cubic scaling is an explicit cost proxy, not a
    # claim that historical spend is recovered one-for-one.
    equivalents = sum((min(max(value, 0), 180) / 180) ** 3 for value in levels)
    return float(min(equivalents, 4) * (SCHOOL_SKILL_175[4] / 4))


def auxiliary_value(features, key):
    value = _number(features.get(key))
    if value is None:
        return None
    points = tuple(sorted(AUXILIARY_LEVEL_VALUES.items()))
    return _linear(points, value)


def valuation_components(features):
    """Return comparable market components; missing data stays unknown."""
    return {
        '人物修炼': person_training_value(features),
        '修炼上限': training_cap_value(features),
        '召唤兽修炼': pet_training_value(features),
        '师门技能': school_skill_value(features),
        '强壮': auxiliary_value(features, 'strong'),
        '神速': auxiliary_value(features, 'speed'),
    }


def adjustment_between(target, sample):
    target_values = valuation_components(target)
    sample_values = valuation_components(sample)
    details = {}
    missing = []
    for name, target_value in target_values.items():
        if target_value is None:
            continue
        sample_value = sample_values.get(name)
        if sample_value is None:
            missing.append(name)
            continue
        details[name] = round(target_value - sample_value, 2)
    return details, missing


def is_pricing_feature(key):
    if key in ('cultivation', 'pet_cultivation', 'strong', 'speed'):
        return True
    if key.startswith(('iExptSki', 'iMaxExpt', 'iBeastSki')):
        return True
    if key.startswith('skill_'):
        try:
            ident = int(key[6:])
        except ValueError:
            return False
        return ident < 150
    return False
