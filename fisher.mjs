#!/usr/bin/env node
import { analyzeContent } from "./browser_extension/analyzer.mjs";

const USAGE = `Fisher — local message and link checks

Usage:
  node fisher.mjs analyze [--mode message|url] [--format text|json]
  node fisher.mjs batch   [--mode message|url] [--format text|json]

Read input from standard input. Analyze checks one complete message or link.
Batch checks up to 500 physical lines and returns aggregate counts only.
Input stays local; links are never opened. No reputation or safety guarantee.
`;
const MAX_BYTES = 1_048_576;
const MAX_BATCH_LINES = 500;

function options(args) {
  if (args.length === 1 && ["--help", "-h"].includes(args[0])) return { help: true };
  const [command, ...rest] = args;
  if (!["analyze", "batch"].includes(command) || rest.length % 2) return null;
  const result = { command, mode: "message", format: "text" };
  const seen = new Set();
  for (let index = 0; index < rest.length; index += 2) {
    const key = rest[index];
    const value = rest[index + 1];
    if (seen.has(key)) return null;
    seen.add(key);
    if (key === "--mode" && ["message", "url"].includes(value)) result.mode = value;
    else if (key === "--format" && ["text", "json"].includes(value)) result.format = value;
    else return null;
  }
  return result;
}

async function readInput() {
  const decoder = new TextDecoder("utf-8", { fatal: true });
  const parts = [];
  let size = 0;
  for await (const chunk of process.stdin) {
    size += chunk.byteLength;
    if (size > MAX_BYTES) throw new Error("input");
    parts.push(decoder.decode(chunk, { stream: true }));
  }
  parts.push(decoder.decode());
  return parts.join("");
}

function batchReport(input, mode) {
  const lines = input.split("\n");
  if (lines.at(-1) === "") lines.pop();
  if (!lines.length || lines.length > MAX_BATCH_LINES) throw new Error("input");
  const counts = { high: 0, review: 0, no_match: 0, cannot_analyze: 0 };
  for (const line of lines) {
    const report = analyzeContent(line.endsWith("\r") ? line.slice(0, -1) : line, { mode });
    counts[report.risk] += 1;
  }
  return {
    engineVersion: "0.4.0",
    mode,
    total: lines.length,
    counts,
    note: "Aggregate rule results only. No labels, accuracy measurement, or safety guarantee.",
  };
}

function textReport(report, batch) {
  if (batch) {
    return [
      `Fisher ${report.engineVersion} · ${report.total} ${report.mode} inputs`,
      ...Object.entries(report.counts).map(([key, value]) => `${key}: ${value}`),
      report.note,
    ].join("\n");
  }
  return [
    `Fisher ${report.engineVersion} · ${report.risk}`,
    ...report.reasons.map((reason) => `- ${reason}`),
    ...report.nextSteps.map((step) => `Next: ${step}`),
    "Local pattern checks only; no reputation or safety guarantee.",
  ].join("\n");
}

async function main() {
  const config = options(process.argv.slice(2));
  if (!config) {
    process.stderr.write("Invalid usage. Run node fisher.mjs --help.\n");
    return 2;
  }
  if (config.help) {
    process.stdout.write(USAGE);
    return 0;
  }
  try {
    const input = await readInput();
    const batch = config.command === "batch";
    const report = batch ? batchReport(input, config.mode) : analyzeContent(input, { mode: config.mode });
    process.stdout.write((config.format === "json" ? JSON.stringify(report) : textReport(report, batch)) + "\n");
    return (batch ? report.counts.cannot_analyze > 0 : report.risk === "cannot_analyze") ? 1 : 0;
  } catch {
    process.stderr.write("Cannot process input. Use valid UTF-8, at most 1 MiB, and at most 500 batch lines.\n");
    return 1;
  }
}

process.exitCode = await main();
