import test from 'node:test';
import assert from 'node:assert/strict';
import { parseEnv, launch } from '../run.mjs';

test('dotenv preserves Chinese, Windows paths, quoted spaces and JSON', () => {
  assert.deepEqual(parseEnv('\uFEFF# comment\r\nROOT="C:\\工作 目录\\bridge"\r\nexport TOKEN=literal\r\nMAP={"chat:id":"团队群"}\r\n'), {
    ROOT: 'C:\\工作 目录\\bridge', TOKEN: 'literal', MAP: '{"chat:id":"团队群"}'
  });
});

test('dotenv treats shell syntax as literal data and skips invalid keys', () => {
  assert.deepEqual(parseEnv('KEY=$(echo should-not-run)\nINVALID-KEY=bad\nEMPTY=\nOTHER=value # comment'), {
    KEY: '$(echo should-not-run)', EMPTY: '', OTHER: 'value'
  });
});

test('invalid launch mode fails before spawning a process', () => {
  assert.throws(() => launch('unknown-mode'), /Unknown mode/);
});
