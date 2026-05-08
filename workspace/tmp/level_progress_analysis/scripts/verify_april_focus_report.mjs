import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const reportPath = "/Users/mt/Documents/Codex/tmp/level_progress_analysis/reports/4月为主关卡流失对比分析报告.xlsx";
const input = await FileBlob.load(reportPath);
const workbook = await SpreadsheetFile.importXlsx(input);

const summary = await workbook.inspect({
  kind: "workbook,sheet,table",
  maxChars: 10000,
  tableMaxRows: 8,
  tableMaxCols: 10,
  tableMaxCellChars: 120,
});
console.log(summary.ndjson);

const dashboard = await workbook.inspect({
  kind: "table",
  range: "结论摘要!A1:G28",
  include: "values,formulas",
  tableMaxRows: 28,
  tableMaxCols: 7,
});
console.log(dashboard.ndjson);

const priority = await workbook.inspect({
  kind: "table",
  range: "卡点优先级!A1:Q12",
  include: "values,formulas",
  tableMaxRows: 12,
  tableMaxCols: 17,
});
console.log(priority.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

for (const sheetName of ["结论摘要", "4月主分析", "三期对比", "付费分层", "卡点优先级", "口径说明", "玩家明细", "图表"]) {
  await workbook.render({ sheetName, scale: 1 });
  console.log(`rendered ${sheetName}`);
}
