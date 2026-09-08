import assert from "node:assert/strict";
import test from "node:test";

import { analyzeContent } from "../analyzer.mjs";
import {
  MAX_MESSAGE_URL_CANDIDATES,
  MAX_URL_CODE_POINTS,
} from "../links.mjs";

const REPORT_KEYS = [
  "engineVersion",
  "mode",
  "risk",
  "reasons",
  "nextSteps",
  "linkSummary",
  "checks",
];

function assertExactReportShape(result) {
  assert.deepEqual(Object.keys(result), REPORT_KEYS);
  assert.equal(result.engineVersion, "0.4.0");
  assert.ok(["message", "url"].includes(result.mode));
  assert.ok(["high", "review", "no_match", "cannot_analyze"].includes(result.risk));
  assert.ok(result.reasons.every((reason) => typeof reason === "string"));
  assert.ok(result.nextSteps.every((step) => typeof step === "string"));
  assert.deepEqual(Object.keys(result.linkSummary), ["inspected", "flagged", "limited"]);
  for (const check of result.checks) {
    assert.deepEqual(Object.keys(check), ["id", "label", "detail"]);
    assert.ok(Object.values(check).every((value) => typeof value === "string"));
  }
}

test("public API has the frozen report shape and deterministic message default", () => {
  const first = analyzeContent("Dinner is ready at eight.");
  const second = analyzeContent("Dinner is ready at eight.", {});
  assertExactReportShape(first);
  assert.deepEqual(first, second);
  assert.equal(first.mode, "message");
  assert.equal(first.risk, "no_match");
  assert.deepEqual(first.linkSummary, { inspected: 0, flagged: 0, limited: false });
});

test("message mode composes detector results without URL-only high promotion", () => {
  const ordinaryLink = analyzeContent("Read the notes at https://example.com/reference.");
  assert.equal(ordinaryLink.risk, "review");
  assert.deepEqual(ordinaryLink.linkSummary, {
    inspected: 1,
    flagged: 0,
    limited: false,
  });

  const advisory = analyzeContent("Do not click https://example.com or share a password.");
  assert.equal(advisory.risk, "review");

  const high = analyzeContent(
    "Send the OTP immediately through https://example.com/verification.",
  );
  assert.equal(high.risk, "high");
});

test("ordinary URL and bare-domain input produce URL-mode no-match, not a safety claim", () => {
  for (const input of [
    "https://example.com/articles?id=3#part",
    "https://example.com.",
    "example.com/reference",
    "\nhttps://example.com/reference\r\n",
  ]) {
    const result = analyzeContent(input, { mode: "url" });
    assertExactReportShape(result);
    assert.equal(result.risk, "no_match", input);
    assert.deepEqual(result.linkSummary, {
      inspected: 1,
      flagged: 0,
      limited: false,
    });
    assert.ok(result.reasons.some((reason) => reason.includes("not a safety result")));
  }
});

test("URL mode reports user-information syntax, HTTP, and non-default ports", () => {
  const result = analyzeContent(
    "http://account:credential@example.com:8080/private?token=value",
    { mode: "url" },
  );
  assert.equal(result.risk, "review");
  assert.deepEqual(
    result.checks.map((check) => check.id),
    ["link_userinfo", "link_insecure_http", "link_nondefault_port"],
  );
  assert.deepEqual(result.linkSummary, { inspected: 1, flagged: 1, limited: false });
});

test("WHATWG-normalized integer, hexadecimal, octal IPv4 and IPv6 are IP literals", () => {
  for (const input of [
    "https://2130706433",
    "https://0x7f000001",
    "https://0177.0.0.1",
    "https://[2001:db8::1]/path",
  ]) {
    const result = analyzeContent(input, { mode: "url" });
    assert.equal(result.risk, "review", input);
    assert.ok(result.checks.some((check) => check.id === "link_ip_literal"), input);
  }
});

test("Unicode and punycode hosts share the internationalized-host observation", () => {
  for (const input of [
    "https://bücher.example",
    "https://xn--bcher-kva.example",
    "example。com",
  ]) {
    const result = analyzeContent(input, { mode: "url" });
    assert.equal(result.risk, "review", input);
    assert.ok(
      result.checks.some((check) => check.id === "link_internationalized_host"),
      input,
    );
  }
});

test("message URL finding avoids version, decimal, and abbreviation tokens", () => {
  for (const input of [
    "Version v0.4.0 is ready.",
    "Meet at 8.30 tomorrow.",
    "This is e.g. a note.",
    "Use .gitignore settings.",
    "A malformed foo..com token.",
  ]) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "no_match", input);
    assert.deepEqual(result.linkSummary, { inspected: 0, flagged: 0, limited: false });
  }
});

test("shorteners and excessive dot-separated labels are observations only", () => {
  const shortener = analyzeContent("https://bit.ly/opaque", { mode: "url" });
  assert.ok(shortener.checks.some((check) => check.id === "link_shortener"));

  const labels = analyzeContent("https://one.two.three.service.example.com/path", {
    mode: "url",
  });
  assert.ok(labels.checks.some((check) => check.id === "link_many_labels"));
  assert.equal(JSON.stringify(labels).includes("registrable"), false);
  assert.equal(JSON.stringify(labels).includes("reputation"), false);
});

test("URL mode rejects unsupported, malformed, empty, multiple, and defanged input", () => {
  for (const input of [
    "",
    "ftp://example.com/file",
    "https://%",
    "https://one.example https://two.example",
    "hxxps://example[.]com",
  ]) {
    const result = analyzeContent(input, { mode: "url" });
    assertExactReportShape(result);
    assert.equal(result.risk, "cannot_analyze", input);
    assert.equal(result.mode, "url", input);
  }
});

test("message mode recognizes defanged routes and keeps them review-only", () => {
  for (const input of ["See hxxps://example[.]com", "See example (dot) com"]) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "review", input);
    assert.ok(result.checks.some((check) => check.id === "link_defanged"), input);
    assert.equal(result.linkSummary.inspected, 1, input);
  }

  const separateFindings = analyzeContent(
    "See http://ordinary.example and hxxps://other[.]example",
  );
  assert.deepEqual(separateFindings.linkSummary, {
    inspected: 2,
    flagged: 2,
    limited: false,
  });
});

test("standalone defanged-dot prose does not attach to unrelated routes", () => {
  assert.equal(analyzeContent("Write [.] literally in prose.").risk, "no_match");

  const result = analyzeContent("A [.] B https://example.com");
  assert.equal(result.risk, "review");
  assert.deepEqual(result.linkSummary, { inspected: 1, flagged: 0, limited: false });
  assert.equal(result.checks.some((check) => check.id === "link_defanged"), false);
});

test("numeric bracket citations are ignored while bare IPv6 remains inspectable", () => {
  for (const input of ["See note [1] for detail.", "See notes [12] and [13]."]) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "no_match", input);
    assert.deepEqual(result.linkSummary, { inspected: 0, flagged: 0, limited: false });
  }

  const ipv6 = analyzeContent("Inspect [::1] locally.");
  assert.equal(ipv6.risk, "review");
  assert.deepEqual(ipv6.linkSummary, { inspected: 1, flagged: 1, limited: false });
  assert.ok(ipv6.checks.some((check) => check.id === "link_ip_literal"));
});

test("invalid input and option types never throw and use the safe report mode", () => {
  for (const [input, options] of [
    [null, undefined],
    [{ toString: () => "https://secret.example" }, { mode: "url" }],
    ["text", null],
    ["text", "url"],
    ["text", []],
    ["text", { mode: null }],
    ["text", { mode: "other" }],
  ]) {
    let result;
    assert.doesNotThrow(() => {
      result = analyzeContent(input, options);
    });
    assertExactReportShape(result);
    assert.equal(result.risk, "cannot_analyze");
    if (options !== undefined && (options === null || options.mode !== "url")) {
      assert.equal(result.mode, "message");
    }
  }
});

test("defanged URL rejection is deterministic across repeated calls", () => {
  const first = analyzeContent("example[.]com", { mode: "url" });
  const second = analyzeContent("example[.]com", { mode: "url" });
  assert.deepEqual(first, second);
  assert.equal(first.risk, "cannot_analyze");
});

test("message and URL limits count Unicode code points and reject without truncation", () => {
  assert.notEqual(analyzeContent("😀".repeat(20_000)).risk, "cannot_analyze");
  assert.equal(analyzeContent("😀".repeat(20_001)).risk, "cannot_analyze");

  const exactUrl = `https://example.com/${"😀".repeat(MAX_URL_CODE_POINTS - 20)}`;
  assert.equal([...exactUrl].length, MAX_URL_CODE_POINTS);
  assert.notEqual(analyzeContent(exactUrl, { mode: "url" }).risk, "cannot_analyze");
  const tooLong = `${exactUrl}x`;
  const rejected = analyzeContent(tooLong, { mode: "url" });
  assert.equal(rejected.risk, "cannot_analyze");
  assert.deepEqual(rejected.linkSummary, { inspected: 0, flagged: 0, limited: true });
});

test("candidate bounds are explicit and incomplete inspection cannot be no-match", () => {
  const input = Array.from(
    { length: MAX_MESSAGE_URL_CANDIDATES + 1 },
    (_, index) => `https://host${index}.example/path`,
  ).join(" ");
  const result = analyzeContent(input);
  assert.equal(result.risk, "review");
  assert.deepEqual(result.linkSummary, {
    inspected: MAX_MESSAGE_URL_CANDIDATES,
    flagged: 0,
    limited: true,
  });
  assert.ok(result.checks.some((check) => check.id === "link_inspection_limited"));
});

test("reports never echo hosts, paths, queries, user information, or submitted text", () => {
  const secrets = [
    "rare-user-731",
    "rare-password-914",
    "private-host-246.example",
    "hidden-path-482",
    "query-secret-593",
  ];
  const input = `http://${secrets[0]}:${secrets[1]}@${secrets[2]}:8080/${secrets[3]}?token=${secrets[4]}`;
  const first = analyzeContent(input, { mode: "url" });
  const second = analyzeContent(input, { mode: "url" });
  assert.deepEqual(first, second);
  const serialized = JSON.stringify(first);
  assert.equal(serialized.includes(input), false);
  for (const secret of secrets) assert.equal(serialized.includes(secret), false, secret);
});
