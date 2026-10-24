import assert from "node:assert/strict";
import test from "node:test";

import { analyzeContent, ENGINE_VERSION } from "../analyzer.mjs";
import { analyzeText } from "../detector.mjs";
import {
  inspectMessageContext,
  inspectMessageLinks,
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
  assert.equal(ENGINE_VERSION, "0.6.0");
  assert.equal(result.engineVersion, ENGINE_VERSION);
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

test("message link authority accepts alphabetic suffixes without an allowlist", () => {
  for (const input of [
    "Visit portal.com",
    "Visit portal.dev",
    "Visit portal.fisher",
    "Review invoice.pdf",
  ]) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "review", input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 1, flagged: 0, limited: false },
      input,
    );
    assert.ok(result.checks.some((check) => check.id === "link_present"), input);
  }

  for (const locator of ["portal.com", "portal.dev", "portal.fisher"]) {
    assert.equal(analyzeContent(`Send OTP through ${locator}`).risk, "high", locator);
  }
});

test("email-like tokens are masked without becoming web-link evidence", () => {
  for (const input of [
    "Contact otp@example.com",
    "Contact password@portal.dev",
    "Contact urgent-send@portal.fisher",
  ]) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "no_match", input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 0, flagged: 0, limited: false },
      input,
    );
    assert.equal(result.checks.some((check) => check.id === "link_present"), false);
    assert.equal(
      result.reasons.some((reason) => reason.includes("credentials")),
      false,
      input,
    );
  }
  const sensitiveRequest = analyzeContent("Send OTP to otp@portal.dev");
  assert.equal(sensitiveRequest.risk, "review");
  assert.equal(sensitiveRequest.checks.some((check) => check.id === "link_present"), false);
});

test("message locators survive common ASCII, Indic, and CJK trailing punctuation", () => {
  for (const punctuation of [
    ":",
    ")",
    "]",
    "}",
    ">",
    "।",
    "॥",
    "。",
    "」",
    "】",
    "？",
  ]) {
    const input = `Reference example.com${punctuation}`;
    const result = analyzeContent(input);
    assert.equal(result.risk, "review", input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 1, flagged: 0, limited: false },
      input,
    );
    assert.ok(result.checks.some((check) => check.id === "link_present"), input);
  }
});

test("email masking survives common ASCII, Indic, and CJK trailing punctuation", () => {
  for (const punctuation of [
    ":",
    ")",
    "]",
    "}",
    ">",
    "।",
    "॥",
    "。",
    "」",
    "】",
    "？",
  ]) {
    const input = `Contact otp@example.com${punctuation}`;
    const result = analyzeContent(input);
    assert.equal(result.risk, "no_match", input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 0, flagged: 0, limited: false },
      input,
    );
    assert.equal(result.checks.some((check) => check.id === "link_present"), false);
    assert.equal(
      result.reasons.some((reason) => reason.includes("credentials")),
      false,
      input,
    );
  }
});

test("message locators and emails survive common paired wrappers", () => {
  for (const input of [
    "[example.com]",
    "(example.com)",
    "“example.com”",
    "«example.com»",
    "「example.com」",
    "【example.com】",
    "《example.com》",
    "【(example.com)】",
  ]) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "review", input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 1, flagged: 0, limited: false },
      input,
    );
  }

  for (const input of [
    "Contact [otp@example.com]",
    "Contact “otp@example.com”",
    "Contact 「otp@example.com」",
    "Contact 【otp@example.com】",
    "Contact 【(otp@example.com)】",
  ]) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "no_match", input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 0, flagged: 0, limited: false },
      input,
    );
    assert.equal(
      result.reasons.some((reason) => reason.includes("credentials")),
      false,
      input,
    );
  }
});

test("boundary trimming preserves balanced URL path punctuation and IPv6 brackets", () => {
  for (const input of [
    "https://example.com/path(foo)",
    "https://example.com/path[foo]",
    "https://example.com/path(foo)).",
  ]) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "review", input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 1, flagged: 0, limited: false },
      input,
    );
  }

  for (const input of [
    "[::1]",
    "[::1]।",
    "https://[2001:db8::1]/path",
    "「https://[2001:db8::1]/path」",
  ]) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "review", input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 1, flagged: 1, limited: false },
      input,
    );
    assert.ok(result.checks.some((check) => check.id === "link_ip_literal"), input);
  }
});

test("unusual email-shaped tokens mask semantics without becoming links", () => {
  const inputs = [
    `${"otp-".repeat(20)}@portal.dev`,
    "otp/secret@portal.dev",
    "otp?secret@portal.dev",
    "otp#secret@portal.dev",
    "otp@@portal.dev",
    "otp@example.dev@thing",
  ];
  for (const input of inputs) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "no_match", input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 0, flagged: 0, limited: false },
      input,
    );
    assert.equal(result.checks.some((check) => check.id === "link_present"), false);
    assert.equal(
      result.reasons.some((reason) => reason.includes("credentials")),
      false,
      input,
    );
  }

  const userinfo = analyzeContent("https://otp:password@portal.dev/private");
  assert.equal(userinfo.risk, "review");
  assert.deepEqual(userinfo.linkSummary, {
    inspected: 1,
    flagged: 1,
    limited: false,
  });
  assert.ok(userinfo.checks.some((check) => check.id === "link_present"));
  assert.ok(userinfo.checks.some((check) => check.id === "link_userinfo"));
  assert.equal(
    userinfo.reasons.some((reason) => reason.includes("credentials")),
    false,
  );
});

test("default-ignorable locator characters are normalized before canonical scanning", () => {
  const recognized = analyzeContent("Send OTP through exa\u200bmple.com");
  assert.equal(recognized.risk, "high");
  assert.deepEqual(recognized.linkSummary, {
    inspected: 1,
    flagged: 0,
    limited: false,
  });
  assert.ok(recognized.checks.some((check) => check.id === "link_present"));
  assert.ok(recognized.reasons.some((reason) => reason.includes("invisible")));

  const maskedSuffix = analyzeContent("exa\u200bmple.otp");
  assert.equal(maskedSuffix.risk, "review");
  assert.equal(maskedSuffix.linkSummary.inspected, 1);
  assert.equal(
    maskedSuffix.reasons.some((reason) => reason.includes("credentials")),
    false,
  );
  assert.ok(maskedSuffix.reasons.some((reason) => reason.includes("invisible")));

  for (const input of [
    "Send OTP through exa\u200bmple[.]dev",
    "Send OTP through hxx\u200bps://example[.]dev",
  ]) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "high", input);
    assert.equal(result.linkSummary.inspected, 1, input);
    assert.ok(result.checks.some((check) => check.id === "link_defanged"), input);
    assert.ok(result.reasons.some((reason) => reason.includes("invisible")), input);
  }
});

test("URL hosts, paths, and user information cannot supply semantic cues", () => {
  for (const input of [
    "https://otp-bank.example/urgent/send/password",
    "http://otp:password@bank.dev/verify/account/immediately",
  ]) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "review", input);
    assert.equal(result.linkSummary.inspected, 1, input);
    assert.equal(
      result.reasons.some((reason) => reason.includes("credentials")),
      false,
      input,
    );
    assert.equal(
      result.reasons.some((reason) => reason.includes("urgency")),
      false,
      input,
    );
    assert.equal(
      result.reasons.some((reason) => reason.includes("reader to click")),
      false,
      input,
    );
  }
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

test("link_present is a message-only composition check", () => {
  const messageResult = analyzeContent("https://example.com");
  assert.ok(messageResult.checks.some((check) => check.id === "link_present"));

  const urlResult = analyzeContent("https://example.com", { mode: "url" });
  assertExactReportShape(urlResult);
  assert.equal(urlResult.checks.some((check) => check.id === "link_present"), false);
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
    "Version 12.34.56 is ready.",
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
  for (const input of [
    "See hxxps://example[.]com",
    "See example (dot) com",
    "See example[.]dev",
    "See example (dot) dev",
    "See example[.]fisher",
  ]) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "review", input);
    assert.ok(result.checks.some((check) => check.id === "link_defanged"), input);
    assert.equal(result.linkSummary.inspected, 1, input);
  }

  assert.equal(analyzeContent("Send OTP through example[.]dev").risk, "high");

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

test("URL mode enforces its code-point limit before trimming raw input", () => {
  const locator = "https://example.com";
  const atLimit = `${" ".repeat(MAX_URL_CODE_POINTS - locator.length)}${locator}`;
  assert.equal([...atLimit].length, MAX_URL_CODE_POINTS);
  assert.equal(analyzeContent(atLimit, { mode: "url" }).risk, "no_match");

  for (const input of [
    ` ${atLimit}`,
    `${" ".repeat(20_001 - locator.length)}${locator}`,
  ]) {
    const result = analyzeContent(input, { mode: "url" });
    assert.equal([...input].length > MAX_URL_CODE_POINTS, true);
    assert.equal(result.risk, "cannot_analyze");
    assert.deepEqual(
      result.linkSummary,
      { inspected: 0, flagged: 0, limited: true },
      [...input].length,
    );
  }
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

test("candidates beyond the inspection bound stay masked from semantic rules", () => {
  const candidates = Array.from(
    { length: MAX_MESSAGE_URL_CANDIDATES + 1 },
    (_, index) =>
      index === MAX_MESSAGE_URL_CANDIDATES
        ? "https://otp-bank.example/urgent/send/password"
        : `https://host${index}.example/path`,
  );
  const result = analyzeContent(candidates.join(" "));
  assert.equal(result.risk, "review");
  assert.deepEqual(result.linkSummary, {
    inspected: MAX_MESSAGE_URL_CANDIDATES,
    flagged: 0,
    limited: true,
  });
  assert.equal(
    result.reasons.some((reason) => reason.includes("credentials")),
    false,
  );
  assert.equal(
    result.reasons.some((reason) => reason.includes("urgency")),
    false,
  );
});

test("unsupported message schemes are limited, review-only, and not link-present", () => {
  const result = analyzeContent("Send OTP through ftp://otp-bank.dev/send/password");
  assert.equal(result.risk, "review");
  assert.deepEqual(result.linkSummary, { inspected: 0, flagged: 0, limited: true });
  assert.ok(result.checks.some((check) => check.id === "link_inspection_limited"));
  assert.equal(result.checks.some((check) => check.id === "link_present"), false);
  assert.equal(
    result.reasons.includes("A web address was found and should be verified independently."),
    false,
  );
  assert.deepEqual(
    result,
    analyzeContent("Send OTP through ftp://neutral.dev/file"),
  );
});

test("obvious malformed message locators are masked and reported as incomplete", () => {
  for (const malformedLocator of [
    "https:/otp-bank.example/urgent/send/password",
    "https:otp-bank.example/urgent/send/password",
    "https:://otp-bank.example/urgent/send/password",
    "https;otp-bank.example/urgent/send/password",
    "https;://otp-bank.example/urgent/send/password",
    "https:\\otp-bank.example\\urgent\\send\\password",
    "http//otp-bank.example/urgent/send/password",
    "hxxp:otp-bank.example/urgent/send/password",
    "hxxps:/otp-bank.example/urgent/send/password",
    "URL:https:/otp-bank.example/urgent/send/password।",
  ]) {
    const input = `Reference ${malformedLocator}`;
    const result = analyzeContent(input);
    const linkResult = inspectMessageLinks(input);
    assert.equal(result.risk, "review", input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 0, flagged: 0, limited: true },
      input,
    );
    assert.equal(linkResult.found, true, input);
    assert.equal(linkResult.limited, true, input);
    assert.ok(result.checks.some((check) => check.id === "link_inspection_limited"), input);
    assert.equal(result.checks.some((check) => check.id === "link_present"), false);
    assert.equal(
      result.reasons.some((reason) => reason.includes("credentials")),
      false,
      input,
    );
    assert.equal(
      result.reasons.some((reason) => reason.includes("urgency")),
      false,
      input,
    );
    assert.equal(
      result.reasons.some((reason) => reason.includes("reader to click")),
      false,
      input,
    );
  }
});

test("embedded and decorated message locators use one bounded candidate span", () => {
  for (const input of [
    "⚠️https://example.com",
    "🔗https://example.com",
    "•https://example.com",
    "→https://example.com",
    "Link:https://example.com",
    "लिंक:https://example.com",
    "[Official](https://example.com)",
    "Visit(https://example.com)",
    "See:https://example.com",
    "https://example.com✅",
    "https://example.com/✅",
    "https://example.com/path?status=✅",
  ]) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "review", input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 1, flagged: 0, limited: false },
      input,
    );
    assert.ok(result.checks.some((check) => check.id === "link_present"), input);
    assert.equal(
      result.checks.some((check) => check.id === "link_internationalized_host"),
      false,
      input,
    );
  }

  const unicodeHost = analyzeContent("https://bücher.example");
  assert.ok(
    unicodeHost.checks.some((check) => check.id === "link_internationalized_host"),
  );

  const visibleRequest = analyzeContent(
    "[Send OTP](https://example.com) immediately",
  );
  assert.equal(visibleRequest.risk, "high");

  const maskedUrlText = analyzeContent(
    "[Official](https://otp-bank.example/urgent/send/password)",
  );
  assert.equal(maskedUrlText.risk, "review");
  assert.equal(
    maskedUrlText.reasons.some((reason) => reason.includes("credentials")),
    false,
  );
  assert.equal(
    maskedUrlText.reasons.some((reason) => reason.includes("urgency")),
    false,
  );
});

test("email masking survives adjacent emoji without hiding ordinary symbol prose", () => {
  for (const decoration of ["⚠️", "🔗", "🙂", "•", "→"]) {
    const result = analyzeContent(`Contact otp@example.com${decoration}`);
    assert.equal(result.risk, "no_match", decoration);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 0, flagged: 0, limited: false },
      decoration,
    );
    assert.equal(
      result.reasons.some((reason) => reason.includes("credentials")),
      false,
      decoration,
    );
  }

  for (const input of [
    "⚠️ Important notice",
    "Price is $5",
    "Use C++ syntax",
    "prefixhttps://example.com",
  ]) {
    const result = analyzeContent(input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 0, flagged: 0, limited: false },
      input,
    );
  }
});

test("punctuation-attached locator spans preserve visible message semantics", () => {
  const emailInput = "Send:otp@example.com";
  const emailContext = inspectMessageContext(emailInput);
  assert.equal(emailContext.semanticText, "Send: ");
  const emailResult = analyzeContent(emailInput);
  assert.ok(
    emailResult.reasons.some((reason) => reason.includes("reader to click")),
  );
  assert.equal(
    emailResult.reasons.some((reason) => reason.includes("credentials")),
    false,
  );

  const urlInput = "https://example.com,send OTP immediately";
  const urlContext = inspectMessageContext(urlInput);
  assert.equal(urlContext.semanticText, " ,send OTP immediately");
  const urlResult = analyzeContent(urlInput);
  assert.equal(urlResult.risk, "high");
  assert.ok(urlResult.reasons.some((reason) => reason.includes("credentials")));
  assert.ok(urlResult.reasons.some((reason) => reason.includes("urgency")));
  assert.ok(urlResult.reasons.some((reason) => reason.includes("reader to click")));

  const indicInput = "https://example.com。ओटीपी तुरंत भेजें";
  const indicContext = inspectMessageContext(indicInput);
  assert.equal(indicContext.semanticText, " 。ओटीपी तुरंत भेजें");
  const indicResult = analyzeContent(indicInput);
  assert.equal(indicResult.risk, "high");
  assert.ok(indicResult.reasons.some((reason) => reason.includes("credentials")));

  const unicodeSeparatorHost = analyzeContent("https://example。com");
  assert.deepEqual(unicodeSeparatorHost.linkSummary, {
    inspected: 1,
    flagged: 1,
    limited: false,
  });

  for (const [input, visibleSuffix] of [
    ["https://example.com:send OTP immediately", ":send OTP immediately"],
    ["https://example.com)send OTP immediately", ")send OTP immediately"],
    ["https://example.com✅send OTP immediately", "✅send OTP immediately"],
    [
      "[Official](https://example.com)send OTP immediately",
      "[Official]( )send OTP immediately",
    ],
  ]) {
    const context = inspectMessageContext(input);
    assert.equal(context.semanticText.trim(), visibleSuffix, input);
    assert.equal(analyzeContent(input).risk, "high", input);
  }

  for (const punctuation of ["$", "%", "&", "*", "+", "=", "_", "~"]) {
    const input = `https://example.com${punctuation}send OTP immediately`;
    const context = inspectMessageContext(input);
    assert.ok(context.semanticText.includes(punctuation), input);
    assert.ok(context.semanticText.includes("send OTP immediately"), input);
    assert.equal(analyzeContent(input).risk, "high", input);
  }
});

test("punctuation-separated locators are inspected and masked independently", () => {
  for (const input of [
    "https://one.example,https://two.example",
    "one.example,two.example",
    "https://one.example;https://two.example",
    "https://one.example)https://two.example",
    "https://one.example]https://two.example",
    "https://one.example|https://two.example",
    "https://one.example✅https://two.example",
    "https://one.example$https://two.example",
    "https://one.example%https://two.example",
    "https://one.example&https://two.example",
    "https://one.example*https://two.example",
    "https://one.example+https://two.example",
    "https://one.example=https://two.example",
    "https://one.example~https://two.example",
  ]) {
    const context = inspectMessageContext(input);
    assert.deepEqual(
      context.linkResult.summary,
      { inspected: 2, flagged: 0, limited: false },
      input,
    );
    assert.equal(context.semanticText.includes("example"), false, input);
  }

  const boundedInput = Array.from(
    { length: MAX_MESSAGE_URL_CANDIDATES + 1 },
    (_, index) =>
      index === MAX_MESSAGE_URL_CANDIDATES
        ? "https://otp-bank.example/urgent/send/password"
        : `https://host${index}.example`,
  ).join(",");
  const bounded = analyzeContent(boundedInput);
  assert.deepEqual(bounded.linkSummary, {
    inspected: MAX_MESSAGE_URL_CANDIDATES,
    flagged: 0,
    limited: true,
  });
  assert.equal(
    bounded.reasons.some((reason) => reason.includes("credentials")),
    false,
  );
  assert.equal(
    bounded.reasons.some((reason) => reason.includes("urgency")),
    false,
  );
});

test("connector runs separate later schemes only after an earlier locator", () => {
  for (const connector of ["__", "___", "_foo_", "--", ".."]) {
    const input = `https://one.example${connector}https://two.example`;
    const context = inspectMessageContext(input);
    assert.deepEqual(
      context.linkResult.summary,
      { inspected: 2, flagged: 0, limited: false },
      input,
    );
    assert.equal(context.semanticText.includes("example"), false, input);
  }

  for (const connector of ["__", "_foo_"]) {
    const boundedInput = Array.from(
      { length: MAX_MESSAGE_URL_CANDIDATES + 1 },
      (_, index) =>
        index === MAX_MESSAGE_URL_CANDIDATES
          ? "https://otp-bank.example/urgent/send/password"
          : `https://host${index}.example`,
    ).join(connector);
    const context = inspectMessageContext(boundedInput);
    assert.deepEqual(
      context.linkResult.summary,
      {
        inspected: MAX_MESSAGE_URL_CANDIDATES,
        flagged: 0,
        limited: true,
      },
      connector,
    );
    assert.equal(context.semanticText.includes("otp-bank"), false, connector);
    assert.equal(context.semanticText.includes("password"), false, connector);

    const result = analyzeContent(boundedInput);
    assert.equal(result.risk, "review", connector);
    assert.equal(
      result.reasons.some((reason) => reason.includes("credentials")),
      false,
      connector,
    );
    assert.equal(
      result.reasons.some((reason) => reason.includes("urgency")),
      false,
      connector,
    );
    assert.equal(
      result.reasons.some((reason) => reason.includes("reader to click")),
      false,
      connector,
    );
  }

  for (const input of ["prefix_https://example.com", "foo_bar.com"]) {
    assert.deepEqual(
      analyzeContent(input).linkSummary,
      { inspected: 0, flagged: 0, limited: false },
      input,
    );
  }
});

test("defanged markers remain transparent across standalone and chained spans", () => {
  const standalone = inspectMessageContext("hxxps://two[.]example/urgent/path");
  assert.deepEqual(standalone.linkResult.summary, {
    inspected: 1,
    flagged: 1,
    limited: false,
  });
  assert.equal(standalone.semanticText.includes("example"), false);
  assert.equal(standalone.semanticText.includes("urgent"), false);
  assert.ok(standalone.linkResult.checks.some((check) => check.id === "link_defanged"));

  for (const secondLocator of [
    "hxxps://two[.]example/path",
    "hxxps://two.example/path",
  ]) {
    const input = `https://one.example__${secondLocator}`;
    const context = inspectMessageContext(input);
    assert.deepEqual(
      context.linkResult.summary,
      { inspected: 2, flagged: 1, limited: false },
      input,
    );
    assert.equal(context.semanticText.includes("two"), false, input);
    assert.equal(context.semanticText.includes("path"), false, input);
    assert.ok(
      context.linkResult.checks.some((check) => check.id === "link_defanged"),
      input,
    );
  }

  const boundedInput = Array.from(
    { length: MAX_MESSAGE_URL_CANDIDATES + 1 },
    (_, index) =>
      index === MAX_MESSAGE_URL_CANDIDATES
        ? "hxxps://otp-bank[.]example/urgent/send/password"
        : `hxxps://host${index}[.]example`,
  ).join("__");
  const context = inspectMessageContext(boundedInput);
  assert.deepEqual(context.linkResult.summary, {
    inspected: MAX_MESSAGE_URL_CANDIDATES,
    flagged: MAX_MESSAGE_URL_CANDIDATES,
    limited: true,
  });
  for (const hiddenText of ["example", "otp-bank", "urgent", "send", "password"]) {
    assert.equal(context.semanticText.includes(hiddenText), false, hiddenText);
  }
  const result = analyzeContent(boundedInput);
  assert.equal(result.risk, "review");
  assert.equal(
    result.reasons.some((reason) => reason.includes("credentials")),
    false,
  );
  assert.equal(
    result.reasons.some((reason) => reason.includes("urgency")),
    false,
  );
  assert.equal(
    result.reasons.some((reason) => reason.includes("reader to click")),
    false,
  );
});

test("valid raw user-information punctuation stays inside the locator span", () => {
  for (const input of [
    "https://user!name@example.com/path",
    "https://user'name@example.com/path",
    "https://user(name@example.com/path",
    "https://user)name@example.com/path",
    "https://user%20name@example.com/path",
  ]) {
    const result = analyzeContent(input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 1, flagged: 1, limited: false },
      input,
    );
    assert.ok(result.checks.some((check) => check.id === "link_userinfo"), input);
    assert.equal(inspectMessageContext(input).semanticText.trim(), "", input);
  }
});

test("authority punctuation does not create link evidence in ordinary prose", () => {
  for (const input of [
    "Use foo_bar.com as an identifier.",
    "A+B=C",
    "Cost is $5",
    "prefixhttps://example.com",
  ]) {
    assert.deepEqual(
      analyzeContent(input).linkSummary,
      { inspected: 0, flagged: 0, limited: false },
      input,
    );
  }
});

test("message span scanning stays bounded for repeated adjacent patterns", () => {
  for (const [label, input, expectedInspected] of [
    ["bare domains", "a.com)".repeat(3_000), MAX_MESSAGE_URL_CANDIDATES],
    ["email-shaped spans", "a@b.com,".repeat(2_400), 0],
    ["scheme URLs", "https://a.co)".repeat(1_400), MAX_MESSAGE_URL_CANDIDATES],
    ["raw authority punctuation", "a.com$".repeat(3_000), MAX_MESSAGE_URL_CANDIDATES],
    [
      "contextual underscore URLs",
      "https://a.co_foo_".repeat(1_100),
      MAX_MESSAGE_URL_CANDIDATES,
    ],
    [
      "defanged connector URLs",
      "hxxps://a[.]co__".repeat(1_100),
      MAX_MESSAGE_URL_CANDIDATES,
    ],
  ]) {
    assert.ok([...input].length <= 20_000, label);
    const started = performance.now();
    const context = inspectMessageContext(input);
    const elapsed = performance.now() - started;
    assert.equal(context.linkResult.summary.inspected, expectedInspected, label);
    assert.ok(elapsed < 500, `${label} span scan took ${elapsed}ms`);
  }
});

test("URL mode rejects invalid named-host authority labels before normalization", () => {
  for (const input of [
    "https://exa,mple.com",
    "https://foo_bar.com",
    "https://-foo.com",
    "https://foo-.com",
    "https://foo..com",
    "https://.foo.com",
  ]) {
    const result = analyzeContent(input, { mode: "url" });
    assert.equal(result.risk, "cannot_analyze", input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 0, flagged: 0, limited: false },
      input,
    );
  }

  for (const input of [
    "https://bücher.example",
    "https://例え.テスト",
    "https://xn--bcher-kva.example",
    "https://127.1",
    "https://0x7f000001",
    "https://0177.0.0.1",
    "https://[2001:db8::1]:8080",
    "https://user:password@example.com:8080/path",
  ]) {
    assert.notEqual(analyzeContent(input, { mode: "url" }).risk, "cannot_analyze", input);
  }
});

test("surplus closing punctuation remains linear near the message limit", () => {
  const input = `https://example.com/${")".repeat(19_000)}`;
  const started = performance.now();
  const result = analyzeContent(input);
  const elapsed = performance.now() - started;

  assert.equal(result.risk, "review");
  assert.deepEqual(result.linkSummary, {
    inspected: 1,
    flagged: 0,
    limited: false,
  });
  assert.ok(elapsed < 500, `near-limit punctuation scan took ${elapsed}ms`);
});

test("incomplete-locator recognition does not reinterpret normal prose", () => {
  for (const input of [
    "HTTP // uses a separated protocol label.",
    "The text https:/ has no destination.",
    "Use http// notation in documentation.",
    "URL: is a field label.",
  ]) {
    const result = analyzeContent(input);
    assert.equal(result.risk, "no_match", input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 0, flagged: 0, limited: false },
      input,
    );
  }
});

test("URL mode rejects every literal Unicode whitespace separator", () => {
  for (const separator of ["\u00a0", "\u2000", "\u2028", "\u2029", "\u3000"]) {
    const input = `https://one.example/path${separator}https://two.example`;
    const result = analyzeContent(input, { mode: "url" });
    assert.equal(result.risk, "cannot_analyze", separator.codePointAt(0));
    assert.deepEqual(
      result.linkSummary,
      { inspected: 0, flagged: 0, limited: false },
      separator.codePointAt(0),
    );
  }

  const encodedSpace = analyzeContent("https://one.example/path%20segment", {
    mode: "url",
  });
  assert.equal(encodedSpace.risk, "no_match");
});

test("message detector and public report use the same canonical link scan", () => {
  for (const input of [
    "Dinner is ready.",
    "portal.dev",
    "ftp://portal.dev/file",
    "Send OTP at portal.fisher",
    "Contact otp@portal.dev",
  ]) {
    const detectorResult = analyzeText(input);
    const reportResult = analyzeContent(input);
    const linkResult = inspectMessageLinks(input);
    assert.deepEqual(
      Object.keys(linkResult),
      ["found", "limited", "summary", "checks"],
      input,
    );
    assert.equal(reportResult.risk, detectorResult.risk, input);
    assert.deepEqual(reportResult.linkSummary, linkResult.summary, input);
    assert.equal(
      reportResult.checks.some((check) => check.id === "link_present"),
      linkResult.summary.inspected > 0,
      input,
    );
  }
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

  const messageResult = analyzeContent(`Send OTP at ${input}`);
  const serializedMessage = JSON.stringify(messageResult);
  assert.equal(serializedMessage.includes(input), false);
  for (const secret of secrets) {
    assert.equal(serializedMessage.includes(secret), false, secret);
  }
});

test("URL mode inspects raw, encoded, and protocol-relative embedded destinations", () => {
  for (const input of [
    "https://relay.example/?next=https://127.0.0.1/private",
    "https://relay.example/?NEXT=https%3A%2F%2F127.0.0.1%2Fprivate",
    "https://relay.example/?return_to=%2F%2F127.0.0.1%2Fprivate",
  ]) {
    const result = analyzeContent(input, { mode: "url" });
    assertExactReportShape(result);
    assert.equal(result.risk, "review", input);
    assert.deepEqual(result.linkSummary, {
      inspected: 1,
      flagged: 1,
      limited: false,
    });
    assert.ok(
      result.checks.some((check) => check.id === "link_nested_destination"),
      input,
    );
    assert.ok(
      result.checks.some((check) => check.id === "link_nested_ip_literal"),
      input,
    );
    assert.ok(
      result.checks
        .filter((check) => check.id.startsWith("link_nested_"))
        .every((check) => check.label.startsWith("Embedded destination: ")),
      input,
    );
  }
});

test("documented navigation keys are finite and case-insensitive", () => {
  const keys = [
    "url",
    "redirect",
    "redirect_url",
    "redirect_uri",
    "next",
    "continue",
    "return",
    "return_to",
    "destination",
    "target",
  ];
  for (const key of keys) {
    const input = `https://relay.example/?${key.toUpperCase()}=https%3A%2F%2Ftarget.example`;
    const result = analyzeContent(input, { mode: "url" });
    assert.equal(result.risk, "review", key);
    assert.ok(
      result.checks.some((check) => check.id === "link_nested_destination"),
      key,
    );
  }

  for (const key of ["to", "dest", "callback", "redirected"]) {
    const result = analyzeContent(
      `https://relay.example/?${key}=https%3A%2F%2Ftarget.example`,
      { mode: "url" },
    );
    assert.equal(result.risk, "no_match", key);
    assert.equal(
      result.checks.some((check) => check.id.startsWith("link_nested_")),
      false,
      key,
    );
  }
});

test("relative and double-encoded navigation values are not destinations", () => {
  for (const value of [
    "/dashboard",
    "dashboard",
    "https%253A%252F%252Ftarget.example%252Fprivate",
  ]) {
    const result = analyzeContent(`https://relay.example/?next=${value}`, {
      mode: "url",
    });
    assert.equal(result.risk, "no_match", value);
    assert.deepEqual(result.linkSummary, {
      inspected: 1,
      flagged: 0,
      limited: false,
    });
    assert.equal(
      result.checks.some((check) => check.id.startsWith("link_nested_")),
      false,
      value,
    );
  }
});

test("unsupported absolute schemes yield limitation evidence without destination claims", () => {
  for (const value of [
    "ftp%3A%2F%2Ftarget.example%2Ffile",
    "javascript%3Aalert(1)",
    "data%3Atext%2Fplain%2Cvalue",
  ]) {
    const result = analyzeContent(`https://relay.example/?next=${value}`, {
      mode: "url",
    });
    assert.equal(result.risk, "review", value);
    assert.deepEqual(result.linkSummary, {
      inspected: 1,
      flagged: 1,
      limited: true,
    });
    assert.deepEqual(
      result.checks.map((check) => check.id),
      ["link_nested_inspection_limited"],
      value,
    );
  }
});

test("embedded destinations reuse structural checks without recursive inspection", () => {
  const structural = analyzeContent(
    "https://relay.example/?next=http%3A%2F%2Fuser%3Apass%40127.0.0.1%3A8080%2Fprivate",
    { mode: "url" },
  );
  assert.deepEqual(
    structural.checks.map((check) => check.id),
    [
      "link_nested_destination",
      "link_nested_userinfo",
      "link_nested_insecure_http",
      "link_nested_ip_literal",
      "link_nested_nondefault_port",
    ],
  );

  const recursiveValue = encodeURIComponent(
    "https://nested.example/?next=https%3A%2F%2F127.0.0.1",
  );
  const nonrecursive = analyzeContent(
    `https://relay.example/?next=${recursiveValue}`,
    { mode: "url" },
  );
  assert.deepEqual(
    nonrecursive.checks.map((check) => check.id),
    ["link_nested_destination"],
  );
});

test("embedded destination checks cover Unicode hosts, shorteners, and many labels", () => {
  for (const [destination, expectedId] of [
    ["https://bücher.example/private", "link_nested_internationalized_host"],
    ["https://bit.ly/private", "link_nested_shortener"],
    [
      "https://one.two.three.service.example.com/private",
      "link_nested_many_labels",
    ],
  ]) {
    const result = analyzeContent(
      `https://relay.example/?next=${encodeURIComponent(destination)}`,
      { mode: "url" },
    );
    assert.equal(result.risk, "review", destination);
    assert.ok(
      result.checks.some((check) => check.id === "link_nested_destination"),
      destination,
    );
    assert.ok(
      result.checks.some((check) => check.id === expectedId),
      destination,
    );
  }
});

test("malformed embedded destinations yield generic bounded limitation evidence", () => {
  for (const input of [
    "https://relay.example/?next=https%3A%2F%2F%25",
    "https://relay.example/?next=https%3A%2F%2Ftarget.example%2F%FF",
  ]) {
    const result = analyzeContent(input, { mode: "url" });
    assert.equal(result.risk, "review", input);
    assert.deepEqual(
      result.linkSummary,
      { inspected: 1, flagged: 1, limited: true },
      input,
    );
    assert.deepEqual(
      result.checks.map((check) => check.id),
      ["link_nested_destination", "link_nested_inspection_limited"],
      input,
    );
  }
});

test("decoded controls and whitespace cannot be normalized into valid embedded destinations", () => {
  const separators = ["\u0000", "\n", "\t", " ", "\u000b", "\u007f"];
  for (const separator of separators) {
    for (const destination of [
      `https://target${separator}.example/private`,
      `https://target.example/private${separator}path`,
    ]) {
      const input = `https://relay.example/?next=${encodeURIComponent(destination)}`;
      const result = analyzeContent(input, { mode: "url" });
      assert.equal(result.risk, "review", separator.codePointAt(0));
      assert.deepEqual(
        result.linkSummary,
        { inspected: 1, flagged: 1, limited: true },
        separator.codePointAt(0),
      );
      assert.deepEqual(
        result.checks.map((check) => check.id),
        ["link_nested_destination", "link_nested_inspection_limited"],
        separator.codePointAt(0),
      );
    }
  }
});

test("every decoded Unicode whitespace separator limits embedded inspection", () => {
  const whitespaceCodePoints = [
    0x0009,
    0x000a,
    0x000b,
    0x000c,
    0x000d,
    0x0020,
    0x0085,
    0x00a0,
    0x1680,
    0x2000,
    0x2001,
    0x2002,
    0x2003,
    0x2004,
    0x2005,
    0x2006,
    0x2007,
    0x2008,
    0x2009,
    0x200a,
    0x2028,
    0x2029,
    0x202f,
    0x205f,
    0x3000,
  ];
  for (const codePoint of whitespaceCodePoints) {
    const separator = String.fromCodePoint(codePoint);
    const destination = `https://target.example/a${separator}b`;
    const input = `https://relay.example/?next=${encodeURIComponent(destination)}`;
    const result = analyzeContent(input, { mode: "url" });
    assert.deepEqual(
      result.checks.map((check) => check.id),
      ["link_nested_destination", "link_nested_inspection_limited"],
      codePoint,
    );
  }
});

test("embedded destination inspection is capped at 32 query pairs and four values", () => {
  const firstThirtyTwoPairs = Array.from(
    { length: 32 },
    (_, index) => `field${index}=value${index}`,
  ).join("&");
  const pairLimited = analyzeContent(
    `https://relay.example/?${firstThirtyTwoPairs}&next=https%3A%2F%2F127.0.0.1`,
    { mode: "url" },
  );
  assert.deepEqual(pairLimited.linkSummary, {
    inspected: 1,
    flagged: 1,
    limited: true,
  });
  assert.deepEqual(
    pairLimited.checks.map((check) => check.id),
    ["link_nested_inspection_limited"],
  );

  const destinations = [0, 1, 2, 3]
    .map((index) => `next=https%3A%2F%2Ftarget${index}.example`)
    .concat("next=https%3A%2F%2F127.0.0.1")
    .join("&");
  const valueLimited = analyzeContent(`https://relay.example/?${destinations}`, {
    mode: "url",
  });
  assert.deepEqual(valueLimited.linkSummary, {
    inspected: 1,
    flagged: 1,
    limited: true,
  });
  assert.ok(
    valueLimited.checks.some(
      (check) => check.id === "link_nested_inspection_limited",
    ),
  );
  assert.equal(
    valueLimited.checks.some((check) => check.id === "link_nested_ip_literal"),
    false,
  );
});

test("encoded message destinations get nested checks while literal splitting stays stable", () => {
  const encoded = analyzeContent(
    "Open https://relay.example/?next=https%3A%2F%2F127.0.0.1%2Fprivate",
  );
  assert.deepEqual(encoded.linkSummary, {
    inspected: 1,
    flagged: 1,
    limited: false,
  });
  assert.ok(encoded.checks.some((check) => check.id === "link_nested_destination"));
  assert.ok(encoded.checks.some((check) => check.id === "link_nested_ip_literal"));

  const literal = inspectMessageLinks(
    "https://relay.example/?next=https://127.0.0.1/private",
  );
  assert.deepEqual(literal.summary, {
    inspected: 2,
    flagged: 1,
    limited: false,
  });
  assert.equal(
    literal.checks.some((check) => check.id === "link_nested_destination"),
    false,
  );
  assert.ok(literal.checks.some((check) => check.id === "link_ip_literal"));
});

test("embedded destination reports are deterministic and do not echo submitted values", () => {
  const secrets = [
    "nested-user-314",
    "nested-pass-159",
    "nested-private-265.example",
    "nested-path-358",
    "nested-query-979",
  ];
  const destination = `http://${secrets[0]}:${secrets[1]}@${secrets[2]}:8080/${secrets[3]}?token=${secrets[4]}`;
  const input = `https://relay.example/?next=${encodeURIComponent(destination)}`;
  const first = analyzeContent(input, { mode: "url" });
  const second = analyzeContent(input, { mode: "url" });
  assert.deepEqual(first, second);
  const serialized = JSON.stringify(first);
  assert.equal(serialized.includes(input), false);
  assert.equal(serialized.includes(destination), false);
  for (const secret of secrets) assert.equal(serialized.includes(secret), false, secret);
});
