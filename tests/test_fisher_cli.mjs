import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import test from "node:test";

const cli = fileURLToPath(new URL("../fisher.mjs", import.meta.url));
const run = (args, input = "") => spawnSync(process.execPath, [cli, ...args], { input, encoding: "utf8", timeout: 10_000 });

function runWithClosedStdout(args) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [cli, ...args], {
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stderr = "";
    child.stderr.setEncoding("utf8");
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });
    child.on("error", reject);
    child.on("close", (status, signal) => resolve({ status, signal, stderr }));
    child.stdout.destroy();
  });
}

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

test("an early-closing output consumer terminates quietly", async () => {
  const result = await runWithClosedStdout(["--help"]);
  assert.deepEqual(result, { status: 0, signal: null, stderr: "" });
  assert.doesNotMatch(result.stderr, /EPIPE|Error|fisher\.mjs/);
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

test("single and batch reports use the shared engine version", async () => {
  const { ENGINE_VERSION } = await import("../browser_extension/analyzer.mjs");
  const single = run(["analyze", "--format", "json"], "Lunch at noon");
  const batch = run(["batch", "--format", "json"], "Lunch at noon\n");

  assert.equal(single.status, 0);
  assert.equal(batch.status, 0);
  assert.equal(JSON.parse(single.stdout).engineVersion, ENGINE_VERSION);
  assert.equal(JSON.parse(batch.stdout).engineVersion, ENGINE_VERSION);
});

test("URL text output explains structural checks without echoing submitted data", () => {
  const input = "http://user:private@127.0.0.1:8080/private?query=QUERY_CANARY";
  const result = run(["analyze", "--mode", "url"], input);
  assert.equal(result.status, 0);
  assert.match(result.stdout, /review/);
  assert.deepEqual(
    result.stdout.split("\n").filter((line) => line.startsWith("Check: ")),
    [
      "Check: User-information syntax — A web address includes user-information syntax before its host.",
      "Check: Unencrypted protocol — A web address uses HTTP rather than HTTPS.",
      "Check: IP-literal host — A web address uses an IP address instead of a named host.",
      "Check: Non-default port — A web address explicitly uses a non-default network port.",
    ],
  );
  assert.doesNotMatch(
    result.stdout,
    /user:private|private|127\.0\.0\.1|8080|query=|QUERY_CANARY/,
  );
  assert.equal(result.stdout, run(["analyze", "--mode", "url"], input).stdout);
});

test("URL and message modes enforce their own code-point limits", () => {
  const exactUrl = `https://example.com/${"😀".repeat(2_048 - 20)}`;
  assert.equal([...exactUrl].length, 2_048);

  const acceptedUrl = run(["analyze", "--mode", "url", "--format", "json"], exactUrl);
  assert.equal(acceptedUrl.status, 0);
  assert.notEqual(JSON.parse(acceptedUrl.stdout).risk, "cannot_analyze");

  for (const input of [`${exactUrl}x`, ` ${exactUrl}`, "a".repeat(20_001)]) {
    const rejectedUrl = run(["analyze", "--mode", "url", "--format", "json"], input);
    assert.equal(rejectedUrl.status, 1);
    const report = JSON.parse(rejectedUrl.stdout);
    assert.equal(report.mode, "url");
    assert.equal(report.risk, "cannot_analyze");
    assert.deepEqual(report.reasons, [
      "The web address exceeds the 2,048-character limit; nothing was analyzed.",
    ]);
    assert.deepEqual(report.linkSummary, { inspected: 0, flagged: 0, limited: true });
  }

  const acceptedMessage = run(["analyze", "--format", "json"], "a".repeat(20_000));
  assert.equal(acceptedMessage.status, 0);
  assert.notEqual(JSON.parse(acceptedMessage.stdout).risk, "cannot_analyze");

  const rejectedMessage = run(["analyze", "--format", "json"], "a".repeat(20_001));
  assert.equal(rejectedMessage.status, 1);
  assert.deepEqual(JSON.parse(rejectedMessage.stdout).reasons, [
    "Input exceeds the 20,000-character analysis limit; nothing was analyzed.",
  ]);
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

test("embedded destinations appear in CLI findings while batch reports stay aggregate-only", () => {
  const input = "https://relay.example/?next=http%3A%2F%2Fuser%3ASECRET_TOKEN%40127.0.0.1%3A8080%2FPRIVATE_PATH";
  const single = run(["analyze", "--mode", "url", "--format", "json"], input);
  assert.equal(single.status, 0);
  const report = JSON.parse(single.stdout);
  assert.equal(report.risk, "review");
  assert.ok(report.checks.some(check => check.id === "link_nested_ip_literal"));
  assert.deepEqual(report.linkSummary, { inspected: 1, flagged: 1, limited: false });
  assert.doesNotMatch(single.stdout, /SECRET_TOKEN|PRIVATE_PATH|127\.0\.0\.1|relay\.example/);
  const batch = run(["batch", "--mode", "url", "--format", "json"], `${input}\nhttps://example.com\n`);
  assert.equal(batch.status, 0);
  const aggregate = JSON.parse(batch.stdout);
  assert.equal(aggregate.total, 2);
  assert.deepEqual(aggregate.counts, { high: 0, review: 1, no_match: 1, cannot_analyze: 0 });
  assert.equal(Object.hasOwn(aggregate, "items"), false);
  assert.doesNotMatch(batch.stdout, /SECRET_TOKEN|PRIVATE_PATH|relay\.example|example\.com/);
});

test("batch-detail prints one ordered JSON result per line without echoing input", () => {
  const input = "Lunch at noon\nSECRET_CANARY send OTP immediately at bank.example\nUnga account blocked, udane OTP anuppunga\n";
  const result = run(["batch-detail"], input);
  assert.equal(result.status, 0);
  assert.equal(result.stderr, "");
  const rows = result.stdout.trimEnd().split("\n").map((row) => JSON.parse(row));
  assert.deepEqual(rows.map((row) => row.line), [1, 2, 3]);
  assert.deepEqual(rows.map((row) => row.risk), ["no_match", "high", "high"]);
  assert.ok(rows.every((row) => Array.isArray(row.reasons) && row.reasons.length > 0));
  assert.doesNotMatch(result.stdout, /SECRET_CANARY|bank\.example|Lunch/);
  const blank = run(["batch-detail"], "Lunch at noon\n\n");
  assert.equal(blank.status, 1);
  assert.equal(JSON.parse(blank.stdout.trimEnd().split("\n")[1]).risk, "cannot_analyze");
});

test("batch-detail enforces the 500-line limit and rejects invalid options", () => {
  assert.equal(run(["batch-detail"], "hello\n".repeat(500)).status, 0);
  const tooMany = run(["batch-detail"], "hello\n".repeat(501));
  assert.equal(tooMany.status, 1);
  assert.equal(tooMany.stdout, "");
  assert.equal(run(["batch-detail", "--mode"], "hello\n").status, 2);
});