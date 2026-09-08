import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import test from "node:test";

const cli = fileURLToPath(new URL("../fisher.mjs", import.meta.url));
const run = (args, input = "") => spawnSync(process.execPath, [cli, ...args], { input, encoding: "utf8", timeout: 10_000 });

test("help and usage are sanitized and use conventional exits", () => {
  const help = run(["--help"]);
  assert.equal(help.status, 0);
  assert.match(help.stdout, /standard input/);
  for (const args of [[], ["SECRET"], ["analyze", "--mode", "SECRET"], ["analyze", "--format", "json", "--format", "json"]]) {
    const result = run(args);
    assert.equal(result.status, 2);
    assert.equal(result.stdout, "");
    assert.doesNotMatch(result.stderr, /SECRET/);
  }
});

test("single analysis agrees with the shared core and never echoes input", async () => {
  const { analyzeContent } = await import("../browser_extension/analyzer.mjs");
  const input = "SECRET_CANARY send OTP immediately at bank.example";
  const result = run(["analyze", "--format", "json"], input);
  assert.equal(result.status, 0);
  assert.deepEqual(JSON.parse(result.stdout), analyzeContent(input));
  assert.equal(result.stderr, "");
  assert.doesNotMatch(result.stdout, /SECRET_CANARY|bank\.example/);
  assert.equal(run(["analyze", "--format", "json"], input).stdout, result.stdout);
});

test("URL mode and text output are usable", () => {
  const result = run(["analyze", "--mode", "url"], "http://127.0.0.1/login");
  assert.equal(result.status, 0);
  assert.match(result.stdout, /review/);
  assert.doesNotMatch(result.stdout, /127\.0\.0\.1|login/);
});

test("batch retains blank and invalid lines in aggregate accounting", () => {
  const input = "Lunch at noon\r\n\r\nsend OTP immediately\r\n";
  const result = run(["batch", "--format", "json"], input);
  assert.equal(result.status, 1);
  const report = JSON.parse(result.stdout);
  assert.equal(report.total, 3);
  assert.deepEqual(report.counts, { high: 1, review: 0, no_match: 1, cannot_analyze: 1 });
  assert.equal(Object.values(report.counts).reduce((a, b) => a + b), report.total);
  assert.doesNotMatch(result.stdout, /Lunch|OTP|records|predictions/);
});

test("batch accepts 500 lines, rejects 501 without partial output", () => {
  assert.equal(run(["batch"], "hello\n".repeat(500)).status, 0);
  const result = run(["batch"], "hello\n".repeat(501));
  assert.equal(result.status, 1);
  assert.equal(result.stdout, "");
});

test("invalid UTF-8, byte overflow, and oversize message fail safely", () => {
  for (const input of [Buffer.from([0xc3, 0x28]), Buffer.alloc(1_048_577, 97)]) {
    const result = run(["analyze"], input);
    assert.equal(result.status, 1);
    assert.equal(result.stdout, "");
    assert.match(result.stderr, /Cannot process input/);
  }
  const result = run(["analyze", "--format", "json"], "a".repeat(20_001));
  assert.equal(result.status, 1);
  assert.equal(JSON.parse(result.stdout).risk, "cannot_analyze");
});
