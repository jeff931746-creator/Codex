import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const WORK_DIR = "/Users/mt/Documents/Codex/tmp/level_progress_analysis/data/april_focus";
const OUTPUT_DIR = "/Users/mt/Documents/Codex/tmp/level_progress_analysis/reports";
const OUTPUT_PATH = path.join(OUTPUT_DIR, "4月为主关卡流失对比分析报告.xlsx");

const payload = JSON.parse(await fs.readFile(path.join(WORK_DIR, "april_focus_summary.json"), "utf8"));

function colName(index) {
  let n = index + 1;
  let name = "";
  while (n > 0) {
    const rem = (n - 1) % 26;
    name = String.fromCharCode(65 + rem) + name;
    n = Math.floor((n - 1) / 26);
  }
  return name;
}

async function readCsv(file) {
  const text = await fs.readFile(path.join(WORK_DIR, file), "utf8");
  const lines = text.trim().split(/\r?\n/);
  return lines.map((line) => {
    const result = [];
    let cur = "";
    let inQuote = false;
    for (let i = 0; i < line.length; i += 1) {
      const ch = line[i];
      if (ch === '"' && line[i + 1] === '"') {
        cur += '"';
        i += 1;
      } else if (ch === '"') {
        inQuote = !inQuote;
      } else if (ch === "," && !inQuote) {
        result.push(cur);
        cur = "";
      } else {
        cur += ch;
      }
    }
    result.push(cur);
    return result.map((v) => {
      if (v === "") return null;
      const n = Number(v);
      return Number.isFinite(n) && !Number.isNaN(n) ? n : v;
    });
  });
}

function writeRows(sheet, startCell, rows) {
  if (!rows.length || !rows[0].length) return "";
  const match = startCell.match(/^([A-Z]+)(\d+)$/);
  const startColLetters = match[1];
  const startRow = Number(match[2]);
  let startIdx = 0;
  for (const ch of startColLetters) startIdx = startIdx * 26 + (ch.charCodeAt(0) - 64);
  startIdx -= 1;
  const endCol = colName(startIdx + rows[0].length - 1);
  const endRow = startRow + rows.length - 1;
  sheet.getRange(`${startCell}:${endCol}${endRow}`).values = rows;
  return `${startCell}:${endCol}${endRow}`;
}

function pct(value) {
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function round(value, digits = 1) {
  return Number(Number(value).toFixed(digits));
}

function lookupSummary(label) {
  return payload.summary.find((row) => row["批次"] === label);
}

function priorityRowsForSummary() {
  return [
    ["关卡", "问题类型", "4月流失人数", "4月归一化流失率", "1月基线归一化流失率", "4月变化", "优先级分"],
    ...payload.top_priority.slice(0, 8).map((row) => [
      row["关卡标签"],
      row["问题类型"],
      row["4月流失人数"],
      pct(row["4月归一化流失率"]),
      pct(row["1月基线归一化流失率"]),
      pct(row["4月变化"]),
      round(row["优先级分"], 1),
    ]),
  ];
}

const periodSummary = await readCsv("period_summary.csv");
const aprilMain = await readCsv("april_main_analysis.csv");
const comparison = await readCsv("three_period_level_comparison.csv");
const priority = await readCsv("priority_levels.csv");
const payComparison = await readCsv("pay_comparison.csv");
const diagnostics = await readCsv("diagnostics.csv");
const playerDetail = await readCsv("player_detail_all.csv");
const april = lookupSummary("4.4-4.8");
const jan = lookupSummary("1月基线");

const workbook = Workbook.create();
const summarySheet = workbook.worksheets.add("结论摘要");
const aprilSheet = workbook.worksheets.add("4月主分析");
const compareSheet = workbook.worksheets.add("三期对比");
const paySheet = workbook.worksheets.add("付费分层");
const prioritySheet = workbook.worksheets.add("卡点优先级");
const methodSheet = workbook.worksheets.add("口径说明");
const detailSheet = workbook.worksheets.add("玩家明细");
const chartSheet = workbook.worksheets.add("图表");

writeRows(summarySheet, "A1", [["4月为主关卡流失对比分析报告"]]);
writeRows(summarySheet, "A3", [
  ["核心结论"],
  [`1. 4月整体流失率 ${pct(april["流失率"])}，高于 1月基线 ${pct(jan["流失率"])}；最终平均进度 ${round(april["最终平均进度"])}，低于 1月基线 ${round(jan["最终平均进度"])}。`],
  ["2. 前四关三期体验无差别，因此 1-01 到 1-04 只作为流量/样本基准段，不归因为关卡体验变化。"],
  ["3. 4月新增/加重优先看 1-12、1-14、1-11；其中 1-12 和 1-14 同时具备高流失人数和高归一化恶化。"],
  ["4. 2-04、1-09、1-10、1-06、1-13 更像长期卡点，4月仍需关注，但不是单纯的4月新增问题。"],
]);
writeRows(summarySheet, "A10", [
  ["指标", "4.4-4.8", "1月基线", "差异"],
  ["样本人数", april["人数"], jan["人数"], april["人数"] - jan["人数"]],
  ["流失率", pct(april["流失率"]), pct(jan["流失率"]), pct(april["流失率"] - jan["流失率"])],
  ["最终平均进度", round(april["最终平均进度"]), round(jan["最终平均进度"]), round(april["最终平均进度"] - jan["最终平均进度"])],
  ["最终中位进度", april["最终中位进度"], jan["最终中位进度"], april["最终中位进度"] - jan["最终中位进度"]],
  ["1~7占比", pct(april["1~7占比"]), pct(jan["1~7占比"]), pct(april["1~7占比"] - jan["1~7占比"])],
  ["前四关最终停留占比", pct(april["前四关最终停留占比"]), pct(jan["前四关最终停留占比"]), pct(april["前四关最终停留占比"] - jan["前四关最终停留占比"])],
]);
writeRows(summarySheet, "A19", priorityRowsForSummary());

writeRows(aprilSheet, "A1", aprilMain);
writeRows(compareSheet, "A1", comparison);
writeRows(paySheet, "A1", payComparison);
writeRows(prioritySheet, "A1", priority);
writeRows(detailSheet, "A1", playerDetail);
writeRows(methodSheet, "A1", [
  ["项目", "说明"],
  ["主分析对象", "4.4-4.8"],
  ["对比对象", "1.13-1.15、1.09-1.11，并合并为 1月基线"],
  ["累计进度口径", "使用原始关卡号重算：累计进度 = (章节 - 1) * 15 + 小关"],
  ["不用原表累计进度列", "原表第10章后会把 1003/1005 等关卡误映射为个位数"],
  ["原始关卡0", "按无效值处理"],
  ["前四关约束", "1-01 到 1-04 三期体验无差别，只作为流量质量/样本结构基准段"],
  ["4月新增/加重判定", "4月流失人数 >= 5 且 归一化流失率较 1月基线上升 >= 3pct"],
  ["长期卡点判定", "4月和 1月基线均有明显流失信号"],
  ["自然人数堆积判定", "绝对人数高但归一化流失不高"],
]);
writeRows(methodSheet, "A14", diagnostics);

const chartPriority = priority.slice(1, 11);
writeRows(chartSheet, "A1", [
  ["关卡", "4月归一化流失率", "1月基线归一化流失率", "4月流失人数", "优先级分"],
  ...chartPriority.map((row) => [row[1], row[9], row[15], row[5], row[29]]),
]);
writeRows(chartSheet, "G1", [
  ["批次", "流失率", "最终平均进度"],
  ...payload.summary.map((row) => [row["批次"], row["流失率"], row["最终平均进度"]]),
]);

chartSheet.charts.add("bar", {
  title: "重点卡点：4月 vs 1月基线归一化流失率",
  categories: chartPriority.map((row) => row[1]),
  series: [
    { name: "4月归一化流失率", values: chartPriority.map((row) => Number(row[9])) },
    { name: "1月基线归一化流失率", values: chartPriority.map((row) => Number(row[15])) },
  ],
  hasLegend: true,
  legend: { position: "bottom" },
  barOptions: { direction: "column", grouping: "clustered", gapWidth: 90 },
  from: { row: 1, col: 10 },
  extent: { widthPx: 650, heightPx: 320 },
});

chartSheet.charts.add("bar", {
  title: "各批次整体流失率",
  categories: payload.summary.map((row) => row["批次"]),
  series: [{ name: "流失率", values: payload.summary.map((row) => Number(row["流失率"])) }],
  hasLegend: false,
  dataLabels: { showValue: true },
  barOptions: { direction: "column", grouping: "clustered", gapWidth: 100 },
  from: { row: 21, col: 0 },
  extent: { widthPx: 520, heightPx: 280 },
});

chartSheet.charts.add("bar", {
  title: "重点卡点优先级分",
  categories: chartPriority.map((row) => row[1]),
  series: [{ name: "优先级分", values: chartPriority.map((row) => Number(row[29])) }],
  hasLegend: false,
  dataLabels: { showValue: true },
  barOptions: { direction: "column", grouping: "clustered", gapWidth: 80 },
  from: { row: 21, col: 8 },
  extent: { widthPx: 580, heightPx: 280 },
});

await fs.mkdir(OUTPUT_DIR, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(OUTPUT_PATH);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
console.log(errors.ndjson);
console.log(OUTPUT_PATH);
