#!/usr/bin/env node
/**
 * Build TE analysisQuery JSON for activity dapan review (3 reports).
 *
 * NOTE: default projectId / channels below are placeholder examples.
 * Always pass --config session.json (or --project-id / channels via config)
 * with YOUR project's real values before running against a real TE project.
 *
 * Usage:
 *   node build_activity_dapan_qp.js --config session.json
 *   node build_activity_dapan_qp.js --start 2026-06-27 --end 2026-07-03 --participation-scene 示例场景 --project-id 999999
 *
 * Writes: qp-dapan.json, qp-tier.json, qp-content.json to --out dir (default stdout summary paths)
 */
const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const opts = {
    projectId: 999999, // placeholder: replace with your TE projectId
    start: '2026-06-27',
    end: '2026-07-03',
    participationScenes: null,
    payContentSplitProp: 'scene_id@scene_id_cn2', // placeholder: your scene split property
    tierIntervals: [1, 7, 101, 1001, 10001, 50001],
    channels: [
      // placeholder channels: replace platform/areaMin/areaMax with your project's real values
      { platform: 'channel_a', areaMin: 1, areaMax: 9999 },
      { platform: 'channel_b', areaMin: 1, areaMax: 2999 },
      { platform: 'channel_c', areaMin: 1, areaMax: 599 },
    ],
    out: null,
    config: null,
  };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--config') opts.config = argv[++i];
    else if (a === '--start') opts.start = argv[++i];
    else if (a === '--end') opts.end = argv[++i];
    else if (a === '--participation-scene') {
      if (!opts.participationScenes) opts.participationScenes = [];
      opts.participationScenes.push(argv[++i]);
    }
    else if (a === '--project-id') opts.projectId = Number(argv[++i]);
    else if (a === '--out') opts.out = argv[++i];
  }
  if (opts.config) Object.assign(opts, JSON.parse(fs.readFileSync(opts.config, 'utf8')));
  // Pitfall: config using startDate/endDate aliases would silently keep the
  // default start/end window under the old logic. Normalize aliases here.
  if (opts.startDate) opts.start = opts.startDate;
  if (opts.endDate) opts.end = opts.endDate;
  if (opts.activityStart) opts.start = opts.activityStart;
  if (opts.activityEnd) opts.end = opts.activityEnd;
  if (!opts.participationScenes || opts.participationScenes.length === 0) {
    opts.participationScenes = ['示例场景'];
  }
  return opts;
}

function dateToMs(dateStr, endOfDay) {
  const [y, m, d] = dateStr.split('-').map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  if (endOfDay) dt.setUTCHours(23, 59, 59, 0);
  return dt.getTime() - 8 * 3600 * 1000; // UTC+8 naive offset; adjust to your project's timezone if different
}

function buildOrFilts(channels) {
  return channels.map((ch) => ({
    filts: [
      { columnName: 'area_id', columnDesc: '区服id', selectType: 'number', tableType: '0', calcuSymbol: 'C06', ftv: [String(ch.areaMin), String(ch.areaMax)], filterType: 'SIMPLE' },
      { columnName: 'platform', columnDesc: '平台(注册时)', selectType: 'string', tableType: '0', calcuSymbol: 'C00', ftv: [ch.platform], filterType: 'SIMPLE' },
    ],
    relation: '1',
    filterType: 'COMPOUND',
  }));
}

const PAY2 = { columnName: 'pay_type_id', columnDesc: '', selectType: 'number', tableType: '0', calcuSymbol: 'C00', ftv: ['2'], filterType: 'SIMPLE' };
const PAY7 = { columnName: 'pay_type_id', columnDesc: '', selectType: 'number', tableType: '0', calcuSymbol: 'C00', ftv: ['7'], filterType: 'SIMPLE' };
const LOGIN_WAY2 = { columnName: 'login_way', columnDesc: '', selectType: 'number', tableType: '0', calcuSymbol: 'C00', ftv: ['2'], filterType: 'SIMPLE' };

function sceneFilter(keywords) {
  return {
    columnName: 'scene_id@scene_id_cn1',
    columnDesc: '场景id(中文)',
    selectType: 'string',
    tableType: '0',
    subTableType: 'vprop_dict',
    calcuSymbol: 'C07',
    ftv: keywords,
    filterType: 'SIMPLE',
  };
}

const USER_ENTITY = {
  index: 1,
  taIdMeasure: {
    columnName: '#user_id', columnDesc: 'User ID', selectType: 'number', tableType: '0',
    entityId: 888888, entityName: 'user', entityType: 'PRIMARY', primaryBigintType: true, // placeholder: replace entityId via list_entities for your project
  },
};

function dep(event, quota = 'A101', prop = null) {
  const d = {
    event: { eventName: event, eventDesc: event, eventType: 'event' },
    quota: { quotaName: quota, quotaDesc: quota },
    property: null,
  };
  if (prop) {
    d.property = { columnName: prop, columnDesc: prop === '#vp@cost_yuan' ? '付费金额(元)' : prop, tableType: '0', subTableType: 'vprop_sql' };
  }
  return d;
}

function formula(name, customEvent, deps, uuid, customFilters, format = 'FORMAT_FLOAT') {
  return {
    eventName: name,
    eventDesc: customEvent,
    type: 1,
    relation: '1',
    filts: [],
    customEvent,
    customFilters,
    formulation: { formulationDeps: deps },
    format,
    eventUuid: uuid,
    quotaEntities: [USER_ENTITY],
  };
}

function uuid(prefix) {
  return `${prefix}-${Math.random().toString(36).slice(2, 8)}`;
}

function buildDapan(opts) {
  const OR_FILTS = buildOrFilts(opts.channels);
  const SCENE = sceneFilter(opts.participationScenes);
  const startMs = dateToMs(opts.start, false);
  const endMs = dateToMs(opts.end, true);
  const u = {
    login: uuid('dapan-login'),
    payu: uuid('dapan-payu'),
    payr: uuid('dapan-payr'),
    prate: uuid('dapan-prate'),
    arpu: uuid('dapan-arpu'),
    arppu: uuid('dapan-arppu'),
    part: uuid('dapan-part'),
    prt: uuid('dapan-prt'),
    voua: uuid('dapan-voua'),
    vouu: uuid('dapan-vouu'),
  };
  const cfPayLogin = [{ index: 0, relation: '1', filts: [PAY2] }, { index: 1, relation: '1', filts: [LOGIN_WAY2] }];
  const cfPartLogin = [{ index: 0, relation: '1', filts: [SCENE] }, { index: 1, relation: '1', filts: [LOGIN_WAY2] }];
  const cfArppu = [{ index: 0, relation: '1', filts: [PAY2] }, { index: 1, relation: '1', filts: [PAY2] }];

  const events = [
    { type: 0, eventName: 't_login', eventDesc: '登录表', eventNameDisplay: '活动期间活跃人数', analysis: 'A101', analysisDesc: 'User count', tableType: '0', relation: '1', filts: [LOGIN_WAY2], eventUuid: u.login },
    { type: 0, eventName: 't_pay_flow', eventDesc: '支付表', eventNameDisplay: '活动期间付费人数', analysis: 'A101', analysisDesc: 'User count', tableType: '0', relation: '1', filts: [PAY2], eventUuid: u.payu },
    { type: 0, eventName: 't_pay_flow', eventDesc: '支付表', eventNameDisplay: '活动期间总收入', analysis: 'A103', analysisDesc: 'Sum', tableType: '0', subTableType: 'vprop_sql', relation: '1', filts: [PAY2], quota: '#vp@cost_yuan', quotaDesc: '付费金额(元)', eventUuid: u.payr },
    formula('活动期间付费率', 't_pay_flow.A101/t_login.A101', [dep('t_pay_flow', 'A101'), dep('t_login', 'A101')], u.prate, cfPayLogin, 'FORMAT_PERCENT'),
    formula('活动期间ARPU', 't_pay_flow.#vp@cost_yuan.A103/t_login.A101', [dep('t_pay_flow', 'A103', '#vp@cost_yuan'), dep('t_login', 'A101')], u.arpu, cfPayLogin),
    formula('活动期间ARPPU', 't_pay_flow.#vp@cost_yuan.A103/t_pay_flow.A101', [dep('t_pay_flow', 'A103', '#vp@cost_yuan'), dep('t_pay_flow', 'A101')], u.arppu, cfArppu),
    { type: 0, eventName: 't_goods_flow', eventDesc: '非货币道具表', eventNameDisplay: '活动参与人数', analysis: 'A101', analysisDesc: 'User count', tableType: '0', relation: '1', filts: [SCENE], eventUuid: u.part },
    formula('活动参与率', 't_goods_flow.A101/t_login.A101', [dep('t_goods_flow', 'A101'), dep('t_login', 'A101')], u.prt, cfPartLogin, 'FORMAT_PERCENT'),
    { type: 0, eventName: 't_pay_flow', eventDesc: '支付表', eventNameDisplay: '代金券总付费金额（元）', analysis: 'A103', analysisDesc: 'Sum', tableType: '0', subTableType: 'vprop_sql', relation: '1', filts: [PAY7], quota: '#vp@cost_yuan', quotaDesc: '付费金额(元)', eventUuid: u.voua },
    { type: 0, eventName: 't_pay_flow', eventDesc: '支付表', eventNameDisplay: '代金券总付费人数', analysis: 'A101', analysisDesc: 'User count', tableType: '0', relation: '1', filts: [PAY7], eventUuid: u.vouu },
  ];

  const stageInfo = Object.values(u).map((eventUuid) => ({ eventUuid, stage: 'anv' }));
  const displayQuotas = events.map((e) => {
    if (e.type === 0) {
      const dq = { checked: '1', type: 0, eventName: e.eventName, eventNameDisplay: e.eventNameDisplay, analysis: e.analysis, customEvent: '' };
      if (e.quota) { dq.quota = e.quota; dq.quotaDesc = e.quotaDesc; }
      return dq;
    }
    return { checked: '1', type: 1, eventName: e.eventName, eventNameDisplay: '', analysis: '', customEvent: e.customEvent };
  });

  return {
    events,
    eventView: {
      projectId: opts.projectId,
      startTime: startMs,
      endTime: endMs,
      timeParticleSize: 'T5',
      groupBy: [],
      graphShape: 'L0',
      total: true,
      rowSpanType: 'fold',
      filts: OR_FILTS,
      relation: '0',
      displayQuotas,
      displayGroups: [{ checked: '1', groups: ['总体'] }],
      comparedByTime: false,
      uiCommonConfig: JSON.stringify({ stageInfo, stageFlag: false, byType: 'event', columnSortType: -2 }),
    },
  };
}

function buildTier(opts) {
  const OR_FILTS = buildOrFilts(opts.channels);
  const startMs = dateToMs(opts.start, false);
  const endMs = dateToMs(opts.end, true);
  const payBase = {
    type: 0,
    eventName: 't_pay_flow',
    eventDesc: '支付表',
    analysis: 'A103',
    analysisDesc: 'Sum',
    tableType: '0',
    subTableType: 'vprop_sql',
    relation: '1',
    filts: [PAY2],
    quota: '#vp@cost_yuan',
    quotaDesc: '付费金额(元)',
  };
  return {
    events: [
      { ...payBase, eventNameDisplay: '付费结构', quotaIntervalArr: opts.tierIntervals, intervalType: 'user_defined' },
      { ...payBase, eventNameDisplay: '', intervalType: 'def' },
    ],
    eventView: {
      projectId: opts.projectId,
      startTime: startMs,
      endTime: endMs,
      timeParticleSize: 'T5',
      groupBy: [],
      graphShape: 'L4',
      total: true,
      simStatDisplay: true,
      taIdMeasureVo: { columnName: '#user_id', columnDesc: 'User ID', selectType: 'number', tableType: '0', entityId: 888888, entityName: 'user' },
      filts: OR_FILTS,
      relation: '0',
      displayQuotas: [
        { checked: '1', type: 0, eventName: 't_pay_flow', analysis: 'A103', quota: '#vp@cost_yuan', quotaDesc: '付费金额(元)' },
        { checked: '1', type: 0, eventName: 't_pay_flow', analysis: 'A103', quota: '#vp@cost_yuan', quotaDesc: '付费金额(元)' },
      ],
      displayGroups: [{ checked: '1', groups: ['总体'] }],
    },
  };
}

function buildContent(opts) {
  const OR_FILTS = buildOrFilts(opts.channels);
  const startMs = dateToMs(opts.start, false);
  const endMs = dateToMs(opts.end, true);
  const splitProp = opts.payContentSplitProp;
  const u1 = uuid('content-payu');
  const u2 = uuid('content-payu-pct');
  const u3 = uuid('content-payr');
  const u4 = uuid('content-payr-pct');

  const cfEmpty = [{ index: 0, relation: '1', filts: [] }, { index: 1, relation: null, filts: [] }];

  const events = [
    {
      type: 0, eventName: 't_pay_flow', eventDesc: '支付表', eventNameDisplay: '付费人数',
      analysis: 'A101', analysisDesc: 'User count', tableType: '0', relation: '1', filts: [PAY2],
      eventSplitIndexes: [0], eventUuid: u1,
      quotaEntities: [{ index: 0, taIdMeasure: USER_ENTITY.taIdMeasure }],
    },
    {
      eventName: '付费人数占比', type: 1, relation: '1', filts: [PAY2],
      customEvent: 't_pay_flow.A101/t_pay_flow.A101',
      customFilters: cfEmpty,
      formulation: { formulationDeps: [dep('t_pay_flow', 'A101'), dep('t_pay_flow', 'A101')] },
      format: 'FORMAT_PERCENT', eventSplitIndexes: [0], eventUuid: u2,
      quotaEntities: [{ index: 0, taIdMeasure: USER_ENTITY.taIdMeasure }, USER_ENTITY],
    },
    {
      type: 0, eventName: 't_pay_flow', eventDesc: '支付表', eventNameDisplay: '付费金额',
      analysis: 'A103', analysisDesc: 'Sum', tableType: '0', subTableType: 'vprop_sql', relation: '1', filts: [PAY2],
      quota: '#vp@cost_yuan', quotaDesc: '付费金额(元)', eventSplitIndexes: [0], eventUuid: u3,
    },
    {
      eventName: '付费金额占比', type: 1, relation: '1', filts: [PAY2],
      customEvent: 't_pay_flow.#vp@cost_yuan.A103/t_pay_flow.#vp@cost_yuan.A103',
      customFilters: cfEmpty,
      formulation: { formulationDeps: [dep('t_pay_flow', 'A103', '#vp@cost_yuan'), dep('t_pay_flow', 'A103', '#vp@cost_yuan')] },
      format: 'FORMAT_PERCENT', eventSplitIndexes: [0], eventUuid: u4,
      quotaEntities: [],
    },
  ];

  const stageInfo = [u1, u2, u3, u4].map((eventUuid, i) => ({ eventUuid, stage: i % 2 === 1 ? 'anv' : (i === 2 ? 'sum' : 'anv') }));
  // normalize stages to match a TE-UI-saved final state: pay users anv, pct anv, amount sum->anv
  stageInfo[2].stage = 'sum';
  stageInfo[3].stage = 'anv';

  return {
    events,
    eventView: {
      projectId: opts.projectId,
      startTime: startMs,
      endTime: endMs,
      timeParticleSize: 'T5',
      groupBy: [],
      graphShape: 'L1',
      total: true,
      rowSpanType: 'unfold',
      filts: OR_FILTS,
      relation: '0',
      displayQuotas: [
        { checked: '1', type: 0, eventName: 't_pay_flow', analysis: 'A101', eventNameDisplay: '付费人数', customEvent: '' },
        { checked: '1', type: 1, eventName: '付费人数占比', customEvent: 't_pay_flow.A101/t_pay_flow.A101', eventNameDisplay: '' },
        { checked: '1', type: 0, eventName: 't_pay_flow', analysis: 'A103', quota: '#vp@cost_yuan', eventNameDisplay: '付费金额', customEvent: '' },
        { checked: '1', type: 1, eventName: '付费金额占比', customEvent: 't_pay_flow.#vp@cost_yuan.A103/t_pay_flow.#vp@cost_yuan.A103', eventNameDisplay: '' },
      ],
      displayGroups: [],
      comparedByTime: false,
      eventSplit: {
        event: null,
        groupByProp: null,
        splitPropsLast: false,
        eventList: [{ eventName: 't_pay_flow', eventDesc: '支付表', eventType: 'event', realAvailable: false }],
        groupByPropList: [{
          columnName: splitProp,
          columnDesc: 'scene_type_scene_id',
          selectType: 'string',
          tableType: '0',
          subTableType: 'vprop_dict',
        }],
      },
      uiCommonConfig: JSON.stringify({
        stageInfo,
        stageFlag: true,
        byType: 'event',
        columnSortType: -2,
        showChartPercent: true,
      }),
    },
  };
}

function main() {
  const opts = parseArgs(process.argv);
  const out = {
    dapan: buildDapan(opts),
    tier: buildTier(opts),
    content: buildContent(opts),
  };
  if (opts.out) {
    fs.mkdirSync(opts.out, { recursive: true });
    fs.writeFileSync(path.join(opts.out, 'qp-dapan.json'), JSON.stringify(out.dapan));
    fs.writeFileSync(path.join(opts.out, 'qp-tier.json'), JSON.stringify(out.tier));
    fs.writeFileSync(path.join(opts.out, 'qp-content.json'), JSON.stringify(out.content));
    console.log(JSON.stringify({
      out: opts.out,
      files: ['qp-dapan.json', 'qp-tier.json', 'qp-content.json'],
      window: { start: opts.start, end: opts.end },
      participationScenes: opts.participationScenes,
      projectId: opts.projectId,
    }));
  } else {
    console.log(JSON.stringify(out, null, 2));
  }
}

main();
