import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const WORK_DIR = "/Users/mt/Documents/Codex/tmp/level_progress_analysis/data/period_comparison";
const OUTPUT_DIR = "/Users/mt/Documents/Codex/tmp/level_progress_analysis/reports";
const OUTPUT_PATH = path.join(OUTPUT_DIR, "1.13-1.15关卡进度分析报告.xlsx");

const summary = JSON.parse(await fs.readFile(path.join(WORK_DIR, "analysis_summary.json"), "utf8"));

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
      return Number.isFinite(n) && String(n) === v ? n : v;
    });
  });
}

function pct(value) {
  return `${(value * 100).toFixed(1)}%`;
}

function round(value, digits = 1) {
  return Number(value.toFixed(digits));
}

function sheetSummaryRows() {
  return [
    ["批次", "人数", "首日平均进度", "最终平均进度", "最终中位进度", "平均记录天数", "记录天数中位数", "流失人数", "流失率"],
    ...summary.map((s) => [
      s.sheet,
      s.players,
      round(s.first_day_mean),
      round(s.final_progress_mean),
      s.final_progress_median,
      round(s.record_days_mean),
      s.record_days_median,
      s.churn_players,
      pct(s.churn_rate),
    ]),
  ];
}

function targetKpis() {
  const target = summary.find((s) => s.sheet === "1.13-1.15");
  const prev = summary.find((s) => s.sheet === "1.09-1.11");
  return [
    ["指标", "1.13-1.15", "对比 1.09-1.11", "解读"],
    ["样本人数", target.players, prev.players, "两批样本量接近，可做粗略横向对比"],
    ["首日平均进度", round(target.first_day_mean), round(prev.first_day_mean), "首日进入深度基本一致"],
    ["最终平均进度", round(target.final_progress_mean), round(prev.final_progress_mean), "1.13-1.15 略高，但中位数相同"],
    ["最终中位进度", target.final_progress_median, prev.final_progress_median, "主体玩家仍停在第 15 关附近"],
    ["平均记录天数", round(target.record_days_mean), round(prev.record_days_mean), "记录深度略高"],
    ["流失率", pct(target.churn_rate), pct(prev.churn_rate), "1.13-1.15 流失率高约 5.6pct"],
  ];
}

function writeRows(sheet, startCell, rows) {
  const startCol = startCell.match(/[A-Z]+/)[0];
  const startRow = Number(startCell.match(/\d+/)[0]);
  const startIdx = startCol.charCodeAt(0) - 65;
  const endIdx = startIdx + rows[0].length - 1;
  const endCol = String.fromCharCode(65 + endIdx);
  const endRow = startRow + rows.length - 1;
  sheet.getRange(`${startCell}:${endCol}${endRow}`).values = rows;
  return `${startCell}:${endCol}${endRow}`;
}

const workbook = Workbook.create();
const dashboard = workbook.worksheets.add("分析摘要");
const daySheet = workbook.worksheets.add("每日进度");
const paySheet = workbook.worksheets.add("付费分层");
const churnSheet = workbook.worksheets.add("流失与卡点");
const chartsSheet = workbook.worksheets.add("图表");
const detailSheet = workbook.worksheets.add("玩家明细");

writeRows(dashboard, "A1", [["1.13-1.15 关卡进度分析报告"]]);
writeRows(dashboard, "A3", targetKpis());
writeRows(dashboard, "A13", sheetSummaryRows());

writeRows(
  dashboard,
  "A19",
  [
    ["核心结论"],
    ["1. 1.13-1.15 批次首日平均进度 9.1、最终平均进度 26.4、最终中位进度 15，说明少数深度玩家拉高均值，主体仍集中在前两章。"],
    ["2. 流失率 61.8%，高于 1.09-1.11 的 56.2%；主要流失/停留关卡集中在 1-06、1-10、1-12、1-13、2-04。"],
    ["3. 50~100 和 100~300 档推进明显更深、流失更低；1~7 和 7~50 是主要流失来源。"],
    ["4. 原表中间累计进度列在第 10 章后存在映射异常，本报告用原始关卡号重新计算累计进度。"],
  ],
);

const dayRows = await readCsv("day_summary_1.13-1.15.csv");
const deltaRows = await readCsv("delta_summary_1.13-1.15.csv");
const churnRows = await readCsv("churn_levels_1.13-1.15.csv");
const stayRows = await readCsv("stay_levels_1.13-1.15.csv");
const finalStageRows = await readCsv("final_stage_dist_1.13-1.15.csv");

writeRows(daySheet, "A1", dayRows);
writeRows(daySheet, "J1", deltaRows);
writeRows(paySheet, "A1", await readCsv("by_pay_1.13-1.15.csv"));
writeRows(churnSheet, "A1", churnRows);
writeRows(churnSheet, "G1", stayRows);
writeRows(churnSheet, "N1", finalStageRows);
writeRows(detailSheet, "A1", await readCsv("row_metrics_1.13-1.15.csv"));

writeRows(chartsSheet, "A1", [["天数", "有记录率", "平均累计进度"], ...dayRows.slice(1).map((r) => [r[0], r[3], r[4]])]);
writeRows(chartsSheet, "E1", [["流失关卡", "流失人数"], ...churnRows.slice(1, 11).map((r) => [r[1], r[2]])]);
writeRows(chartsSheet, "H1", [["卡点关卡", "最长停留人数", "平均连续停留天数"], ...stayRows.slice(1, 11).map((r) => [r[4], r[1], r[2]])]);

chartsSheet.charts.add("line", {
  title: "1.13-1.15 每日留存记录率与进度",
  categories: dayRows.slice(1).map((r) => r[0]),
  series: [
    { name: "有记录率", values: dayRows.slice(1).map((r) => Number(r[3])) },
    { name: "平均累计进度 / 100", values: dayRows.slice(1).map((r) => Number(r[4]) / 100) },
  ],
  hasLegend: true,
  legend: { position: "bottom" },
  from: { row: 1, col: 10 },
  extent: { widthPx: 560, heightPx: 300 },
});

chartsSheet.charts.add("bar", {
  title: "主要流失关卡",
  categories: churnRows.slice(1, 11).map((r) => r[1]),
  series: [{ name: "流失人数", values: churnRows.slice(1, 11).map((r) => Number(r[2])) }],
  hasLegend: false,
  barOptions: { direction: "column", grouping: "clustered", gapWidth: 80 },
  dataLabels: { showValue: true },
  from: { row: 18, col: 0 },
  extent: { widthPx: 520, heightPx: 300 },
});

chartsSheet.charts.add("bar", {
  title: "最长停留关卡",
  categories: stayRows.slice(1, 11).map((r) => r[4]),
  series: [{ name: "出现为最长停留人数", values: stayRows.slice(1, 11).map((r) => Number(r[1])) }],
  hasLegend: false,
  barOptions: { direction: "column", grouping: "clustered", gapWidth: 80 },
  dataLabels: { showValue: true },
  from: { row: 18, col: 8 },
  extent: { widthPx: 520, heightPx: 300 },
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
