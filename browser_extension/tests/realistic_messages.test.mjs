import assert from "node:assert/strict";
import test from "node:test";

import { analyzeContent } from "../analyzer.mjs";

const analyze = (text) => analyzeContent(text, { mode: "message" });

test("benign casual use of 'fine' is no_match", () => {
  assert.equal(analyze("Call me when you reach, I'm fine").risk, "no_match");
});

test("emoji greeting is no_match and not reported as invisible characters", () => {
  const result = analyze("Happy birthday \u2764\uFE0F");
  assert.equal(result.risk, "no_match");
  assert.ok(
    !result.reasons.some((reason) => /invisible/i.test(reason)),
    `unexpected reasons: ${result.reasons.join(" | ")}`,
  );
});

test("a courier asking for a pin code is not high risk", () => {
  const result = analyze(
    "Your Amazon delivery is out today. Please share your pin code with the courier: amzn.in/d/abc",
  );
  assert.notEqual(result.risk, "high");
});

test("bank impersonation with KYC and a lookalike link is high", () => {
  assert.equal(
    analyze("Dear SBI customer, your KYC expired. Update now: sbi-kyc-update.xyz").risk,
    "high",
  );
});

test("Telugu password request containing ZWNJ is review or high", () => {
  const result = analyze("\u0C2E\u0C40 \u0C2A\u0C3E\u0C38\u0C4D\u200C\u0C35\u0C30\u0C4D\u0C21\u0C4D \u0C07\u0C35\u0C4D\u0C35\u0C02\u0C21\u0C3F");
  assert.ok(["review", "high"].includes(result.risk), `got ${result.risk}`);
});

test("romanized Tamil OTP demand is high", () => {
  assert.equal(analyze("Unga account blocked, udane OTP anuppunga").risk, "high");
});

test("romanized Telugu OTP demand is high", () => {
  assert.equal(analyze("Mee account blocked, ventane OTP pampandi").risk, "high");
});

test("romanized Hindi OTP demand is high", () => {
  assert.equal(analyze("Aapka khata band ho jayega, turant OTP bhejo").risk, "high");
});

test("electricity disconnection threat is review or high", () => {
  const result = analyze(
    "Your electricity connection will be disconnected tonight. Call the officer now",
  );
  assert.ok(["review", "high"].includes(result.risk), `got ${result.risk}`);
});

test("native Hindi request with Latin OTP is high", () => {
  assert.equal(
    analyze("तुरंत अपना OTP भेजें वरना खाता बंद हो जाएगा").risk,
    "high",
  );
});

test("native Telugu request with Latin OTP is high", () => {
  assert.equal(
    analyze("మీ బ్యాంక్ ఖాతా బ్లాక్ చేయబడింది. వెంటనే OTP పంపండి").risk,
    "high",
  );
});

test("Hindi electricity disconnection scam is review or high", () => {
  const result = analyze(
    "आपका बिजली कनेक्शन आज रात काट दिया जाएगा। तुरंत इस नंबर पर कॉल करें",
  );
  assert.ok(["review", "high"].includes(result.risk), `got ${result.risk}`);
});

test("Hindi advisory not to share OTP is not high", () => {
  assert.notEqual(
    analyze("सावधान: अपना OTP किसी को मत भेजें, तुरंत 1930 पर शिकायत करें").risk,
    "high",
  );
});

test("benign team lunch message is no_match", () => {
  assert.equal(analyze("Hi, team lunch moved to 1 PM").risk, "no_match");
});
