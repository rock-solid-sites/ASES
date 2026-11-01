#!/usr/bin/env node
import { readFile } from 'node:fs/promises';
import { proposePlans } from './dist/planner.js';

if (process.argv.length !== 3) {
  process.stderr.write('Usage: node cli.mjs <local-planning-input.json>\n');
  process.exitCode = 2;
} else {
  try {
    const raw = await readFile(process.argv[2], 'utf8');
    const input = JSON.parse(raw);
    const result = proposePlans(input);
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
    if (result.status !== 'ok') process.exitCode = 1;
  } catch (err) {
    process.stderr.write(`${err instanceof Error ? err.message : String(err)}\n`);
    process.exitCode = 1;
  }
}