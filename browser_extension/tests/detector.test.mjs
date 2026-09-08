import assert from "node:assert/strict";
import { performance } from "node:perf_hooks";
import test from "node:test";

import {
  analyzeText,
  CONFUSABLE_PROFILE_VERSION,
  MAX_INPUT_CHARS,
} from "../detector.mjs";

const CONFUSABLE_REASON = "Contains character lookalikes resembling a configured sensitive term.";

test("ordinary text is no-match while protective messages require review", () => {
  assert.equal(analyzeText("Dinner is ready at eight.").risk, "no_match");
  assert.equal(
    analyzeText("Bank safety notice: never share OTP or password. Do not click suspicious links.")
      .risk,
    "review",
  );
  assert.equal(analyzeText("ओटीपी साझा न करें और अनजान लिंक न खोलें।").risk, "review");
  assert.equal(
    analyzeText("வங்கி பாதுகாப்பு அறிவிப்பு: ஓடிபி பகிர வேண்டாம். இணைப்பை திறக்க வேண்டாம்.")
      .risk,
    "review",
  );
  assert.equal(
    analyzeText("బ్యాంక్ భద్రతా హెచ్చరిక: ఓటీపీ పంచుకోవద్దు. లింక్ తెరవద్దు.").risk,
    "review",
  );
});

test("urgent or routed protective advisories conservatively require review", () => {
  assert.equal(analyzeText("Urgent security reminder: never share OTP.").risk, "review");
  assert.equal(analyzeText("Do not click bank-help.example.").risk, "review");
  assert.equal(
    analyzeText("तुरंत सुरक्षा चेतावनी: ओटीपी साझा न करें।").risk,
    "review",
  );
  assert.equal(
    analyzeText("அவசரம் பாதுகாப்பு அறிவிப்பு: ஓடிபி பகிர வேண்டாம்.").risk,
    "review",
  );
  assert.equal(
    analyzeText("అత్యవసరం భద్రతా హెచ్చరిక: ఓటీపీ పంచుకోవద్దు.").risk,
    "review",
  );
});

test("a protective clause cannot suppress a separate payment demand", () => {
  assert.equal(
    analyzeText("Never share OTP. Pay ₹500 immediately at bad.example").risk,
    "review",
  );
  assert.equal(
    analyzeText("Do not click suspicious links. Pay ₹500 to scam.example immediately.").risk,
    "review",
  );
});

test("an undelimited protective phrase cannot suppress a risky-action pivot", () => {
  assert.equal(
    analyzeText("Never share OTP Pay ₹500 immediately at bad.example").risk,
    "review",
  );
  assert.equal(
    analyzeText("Do not click bad.example Pay ₹500 immediately at scam.example").risk,
    "review",
  );
  assert.equal(
    analyzeText("Do not share OTP call customer care immediately at bad.example").risk,
    "review",
  );
  assert.equal(
    analyzeText("Never share OTP send ₹500 immediately at bad.example").risk,
    "review",
  );
  assert.equal(
    analyzeText("OTP share mat karo paise send karo bad.example").risk,
    "review",
  );
});

test("protective prefixes never suppress unenumerated pivots", () => {
  assert.equal(
    analyzeText("Never share OTP ₹500 immediately at bad.example").risk,
    "review",
  );
  assert.equal(
    analyzeText("Never share OTP update KYC immediately at bad.example").risk,
    "review",
  );
  assert.equal(
    analyzeText("Never share OTP confirm KYC immediately at bad.example").risk,
    "review",
  );
  assert.equal(
    analyzeText("Never share OTP tap bad.example immediately").risk,
    "review",
  );
  assert.equal(
    analyzeText("OTP share mat karo KYC update karo bad.example").risk,
    "review",
  );
});

test("English and Romanized Indic scam combinations are high risk", () => {
  assert.equal(
    analyzeText("SBI KYC expires today. Verify your account immediately at sbi-help.example").risk,
    "high",
  );
  assert.equal(
    analyzeText("Bank ka OTP abhi bhejo, account block hoga. Link open karo bank-help.example").risk,
    "high",
  );
});

test("Devanagari, Tamil, and Telugu scam combinations are detected", () => {
  assert.equal(
    analyzeText("बैंक खाता आज ही बंद होगा। तुरंत ओटीपी भेजें और bank-help.example खोलें।").risk,
    "high",
  );
  assert.equal(
    analyzeText("வங்கி கணக்கு இன்றே முடக்கப்படும். உடனே ஓடிபி அனுப்ப bank-help.example திறக்கவும்.").risk,
    "high",
  );
  assert.equal(
    analyzeText("బ్యాంక్ ఖాతా ఈరోజే నిలిపివేయబడుతుంది. వెంటనే ఓటీపీ పంపి bank-help.example తెరవండి.").risk,
    "high",
  );
});

test("Unicode obfuscation is normalized and explained", () => {
  const result = analyzeText("Bank alert: send c\u200bvv immediately at secure-help.example");
  assert.equal(result.risk, "high");
  assert.ok(result.reasons.some((reason) => reason.includes("invisible")));

  const dotVariant = analyzeText("Bank says send OTP immediately at bank-help。xyz.");
  assert.equal(dotVariant.risk, "high");
  assert.ok(dotVariant.reasons.some((reason) => reason.includes("web address")));

  const compatibilityOnly = analyzeText("Ｂａｎｋ customer service is open today.");
  assert.equal(
    compatibilityOnly.reasons.some((reason) => reason.includes("invisible")),
    false,
  );
});

test("frozen confusable profile is review-only for every configured skeleton", () => {
  assert.equal(CONFUSABLE_PROFILE_VERSION, "FISHER_GC_SENSITIVE_V1");
  for (const input of [
    "οtρ",
    "оtр",
    "ριn",
    "pіn",
    "ραѕѕword",
    "pаsswоrd",
    "ραѕѕcode",
    "passcodе",
    "сνν",
    "kγc",
    "kуc",
  ]) {
    const result = analyzeText(input);
    assert.equal(result.risk, "review", input);
    assert.ok(result.reasons.includes(CONFUSABLE_REASON), input);
  }
});

test("confusable detection never promotes contextual requests to high", () => {
  for (const input of [
    "Send οtρ immediately at risk.example",
    "Enter your ρіn at risk.example",
    "Provide сνν immediately",
    "Update kуc immediately at risk.example",
    "Never share οtρ immediately at risk.example",
    "οtρ तुरंत भेजें risk.example",
  ]) {
    const result = analyzeText(input);
    assert.equal(result.risk, "review", input);
    assert.ok(result.reasons.includes(CONFUSABLE_REASON), input);
  }
  assert.equal(analyzeText("Send OTP immediately at risk.example").risk, "high");
});

test("uppercase and default-ignorable lookalikes use the same review floor", () => {
  const result = analyzeText("Send Ο\u200bTΡ immediately at risk.example");
  assert.equal(result.risk, "review");
  assert.ok(result.reasons.includes(CONFUSABLE_REASON));
  assert.ok(result.reasons.some((reason) => reason.includes("invisible")));
});

test("sensitive lookalike tokens inside dotted strings still require review", () => {
  for (const input of [
    "Please send οtp.test",
    "Please share рin.test",
    "Please send pαssword.test",
    "Please send passcodе.test",
    "Please enter сvv.test",
    "Please update kуc.test",
  ]) {
    const result = analyzeText(input);
    assert.equal(result.risk, "review", input);
    assert.ok(result.reasons.includes(CONFUSABLE_REASON), input);
  }
});

test("partial, spaced, ordinary, digit, and non-sensitive tokens are outside the profile", () => {
  for (const input of [
    "пример оплаты",
    "αεροπλάνο",
    "कृपया OTP साझा न करें",
    "0TP",
    "xοtρx",
    "ο t ρ",
    "όtρ",
    "bаnk.example",
    "verіfy accοunt",
  ]) {
    assert.equal(analyzeText(input).reasons.includes(CONFUSABLE_REASON), false, input);
  }
});

test("repeated mapped letters remain bounded and deterministic", () => {
  const input = "ο".repeat(MAX_INPUT_CHARS);
  const started = performance.now();
  const first = analyzeText(input);
  const elapsedMilliseconds = performance.now() - started;
  assert.deepEqual(first, analyzeText(input));
  assert.equal(first.reasons.includes(CONFUSABLE_REASON), false);
  assert.ok(elapsedMilliseconds < 500, `confusable scan took ${elapsedMilliseconds} ms`);
});

test("confusable results never echo raw, mapped, or code-point values", () => {
  const input = "Send οtρ immediately at risk.example";
  const serialized = JSON.stringify(analyzeText(input)).toLocaleLowerCase("en");
  assert.equal(serialized.includes(input.toLocaleLowerCase("en")), false);
  assert.equal(serialized.includes("otp"), false);
  assert.equal(serialized.includes("03bf"), false);
  assert.equal(serialized.includes("u+03"), false);
  assert.equal(serialized.includes("greek"), false);
  assert.equal(serialized.includes("cyrillic"), false);
});

test("empty, invisible-only, malformed, and over-limit inputs cannot be analyzed", () => {
  assert.deepEqual(analyzeText(""), {
    risk: "cannot_analyze",
    reasons: ["No analyzable text was provided."],
  });
  assert.equal(analyzeText(" \n\t ").risk, "cannot_analyze");
  assert.equal(analyzeText("\u200b\u034f").risk, "cannot_analyze");
  assert.equal(analyzeText({ toString: () => "secret" }).risk, "cannot_analyze");

  const maliciousTail = `${"a".repeat(MAX_INPUT_CHARS)} bank OTP send immediately bank-help.example`;
  const result = analyzeText(maliciousTail);
  assert.deepEqual(result, {
    risk: "cannot_analyze",
    reasons: ["Input exceeds the 20,000-character analysis limit; nothing was analyzed."],
  });
});

test("a malicious instruction cannot hide behind protective wording", () => {
  const result = analyzeText(
    "Never share OTP with strangers. Now send OTP immediately to bank-help.example",
  );
  assert.equal(result.risk, "high");
  assert.equal(
    result.reasons.includes("Protective wording was detected; context may be a warning."),
    true,
  );
});

test("an advisory cannot suppress a later credential-disclosure request", () => {
  assert.equal(
    analyzeText("Never share OTP with anyone. Send me your password.").risk,
    "review",
  );
  assert.equal(analyzeText("OTP share mat karo. Password bhejo.").risk, "review");
  assert.equal(
    analyzeText("Never share OTP with anyone send me your password").risk,
    "review",
  );
  assert.equal(analyzeText("OTP share mat karo password bhejo").risk, "review");
  assert.equal(
    analyzeText("Never share OTP with anyone; verify your account").risk,
    "review",
  );
});

test("benign authority, refund, domain, and action signals require review, not high", () => {
  const result = analyzeText(
    "Bank delivery notice: your refund payment is available at bank.example. Click to review.",
  );
  assert.equal(result.risk, "review");
  assert.equal(
    analyzeText("Urgent KYC update: visit bank.example for the official policy.").risk,
    "review",
  );
});

test("malformed Unicode and disallowed controls cannot be analyzed", () => {
  assert.equal(analyzeText("bank\u0000otp send immediately").risk, "cannot_analyze");
  assert.equal(analyzeText("bank\ud800otp send immediately").risk, "cannot_analyze");
  assert.equal(analyzeText("bank\udc00otp send immediately").risk, "cannot_analyze");
  assert.equal(analyzeText("bank\u0085otp send immediately").risk, "cannot_analyze");
  assert.equal(analyzeText("bank\u009cotp send immediately").risk, "cannot_analyze");
  assert.notEqual(analyzeText("ordinary\tline\ntext").risk, "cannot_analyze");
});

test("input limit counts Unicode code points and rejects without truncation", () => {
  assert.notEqual(analyzeText("😀".repeat(MAX_INPUT_CHARS)).risk, "cannot_analyze");
  assert.equal(analyzeText("😀".repeat(MAX_INPUT_CHARS + 1)).risk, "cannot_analyze");
});

test("adversarial repeated domain labels remain bounded", () => {
  const started = performance.now();
  const result = analyzeText("a.".repeat(MAX_INPUT_CHARS / 2));
  const elapsedMilliseconds = performance.now() - started;
  assert.ok(["no_match", "review"].includes(result.risk));
  assert.ok(elapsedMilliseconds < 500, `domain scan took ${elapsedMilliseconds} ms`);
});

test("runtime format controls are removed in the matching view and explained", () => {
  const result = analyzeText("Bank says send o\u{13430}tp immediately at bank-help.example");
  assert.equal(result.risk, "high");
  assert.ok(result.reasons.some((reason) => reason.includes("invisible")));
});

test("results are deterministic and never echo analyzed secrets", () => {
  const secret = "SECRET-OTP-849201";
  const input = `Bank says send ${secret} immediately at bank-help.example`;
  const first = analyzeText(input);
  const second = analyzeText(input);
  assert.deepEqual(first, second);
  assert.equal("score" in first, false);
  assert.equal(JSON.stringify(first).includes(secret), false);
});
