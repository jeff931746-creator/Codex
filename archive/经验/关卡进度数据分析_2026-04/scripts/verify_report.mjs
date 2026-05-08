import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const reportPath = "/Users/mt/Documents/Codex/tmp/level_progress_analysis/reports/1.13-1.15关卡进度分析报告.xlsx";
const input = await FileBlob.load(reportPath);
const workbook = await SpreadsheetFile.importXlsx(input);

const summary = await workbook.inspect({
  kind: "workbook,sheet,table",
  maxChars: 8000,
  tableMaxRows: 8,
  tableMaxCols: 8,
  tableMaxCellChars: 120,
});
console.log(summary.ndjson);

const dashboard = await workbook.inspect({
  kind: "table",
  range: "分析摘要!A1:I24",
  include: "values,formulas",
  tableMaxRows: 24,
  tableMaxCols: 9,
});
console.log(dashboard.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

for (const sheetName of ["分析摘要", "每日进度", "付费分层", "流失与卡点", "图表", "玩家明细"]) {
  await workbook.render({ sheetName, scale: 1 });
  console.log(`rendered ${sheetName}`);
}
