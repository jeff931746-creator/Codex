import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";
import { homedir } from 'node:os';
import { join } from 'node:path';

const inputPath = process.env.LEVEL_PROGRESS_INPUT || join(homedir(), 'Downloads', '1.13-1.15关卡进度.xlsx');
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
