import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "/Users/mt/Downloads/1.13-1.15关卡进度.xlsx";
const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);

const summary = await workbook.inspect({
  kind: "workbook,sheet,table",
  maxChars: 12000,
  tableMaxRows: 8,
  tableMaxCols: 12,
  tableMaxCellChars: 120,
});

console.log(summary.ndjson);
