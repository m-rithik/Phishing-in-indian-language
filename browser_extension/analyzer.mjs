import { analyzeTextWithLinks } from "./detector.mjs";
import { inspectUrlInput } from "./links.mjs";

export const ENGINE_VERSION = "0.5.0";
const EMPTY_LINK_SUMMARY = Object.freeze({ inspected: 0, flagged: 0, limited: false });

const NEXT_STEPS = {
  high: [
    "Do not use the link or provide credentials, money, or software.",
    "Verify the request through an independently obtained official channel.",
  ],
  review: [
    "Pause before acting on the message or web address.",
    "Verify the sender and destination through an independent official channel.",
  ],
  no_match: [
    "No configured finding was detected; this is not a safety result.",
    "Continue to verify unexpected requests through an independent official channel.",
  ],
  cannot_analyze: [
    "No result was produced from this input.",
    "Check the input format and limits, then try again with permitted content.",
  ],
};

function report(mode, risk, reasons, linkSummary, checks) {
  return {
    engineVersion: ENGINE_VERSION,
    mode,
    risk,
    reasons: [...reasons],
    nextSteps: [...NEXT_STEPS[risk]],
    linkSummary: { ...linkSummary },
    checks: checks.map((check) => ({ ...check })),
  };
}

function cannotAnalyze(mode, reason, linkSummary = EMPTY_LINK_SUMMARY) {
  return report(mode, "cannot_analyze", [reason], linkSummary, []);
}

function resolveMode(options) {
  if (options === undefined) return { valid: true, mode: "message" };
  if (options === null || typeof options !== "object" || Array.isArray(options)) {
    return { valid: false, mode: "message" };
  }
  let mode;
  try {
    mode = options.mode === undefined ? "message" : options.mode;
  } catch {
    return { valid: false, mode: "message" };
  }
  if (mode !== "message" && mode !== "url") {
    return { valid: false, mode: "message" };
  }
  return { valid: true, mode };
}

function analyzeMessage(input) {
  const { textResult, linkResult } = analyzeTextWithLinks(input);
  if (textResult.risk === "cannot_analyze") {
    return report(
      "message",
      "cannot_analyze",
      textResult.reasons,
      EMPTY_LINK_SUMMARY,
      [],
    );
  }

  let risk = textResult.risk;
  if ((linkResult.summary.inspected > 0 || linkResult.limited) && risk === "no_match") {
    risk = "review";
  }

  const reasons = [...textResult.reasons];
  const checks = [
    {
      id: "message_rules",
      label: "Message rules",
      detail:
        textResult.risk === "no_match"
          ? "The configured message rules found no clear combination; this is not a safety result."
          : "The configured message rules produced the reported message finding.",
    },
  ];
  if (linkResult.summary.inspected > 0) {
    reasons.push("A web address was found and should be verified independently.");
    checks.push({
      id: "link_present",
      label: "Web address present",
      detail: "At least one web address was found in the submitted message.",
    });
  }
  if (linkResult.checks.length > 0) {
    reasons.push("One or more web addresses have structural characteristics that need review.");
    checks.push(...linkResult.checks);
  }
  if (linkResult.limited) {
    reasons.push("Web-address inspection was incomplete because of its format or a local limit.");
    checks.push({
      id: "link_inspection_limited",
      label: "Incomplete web-address inspection",
      detail: "A web-address format or local limit prevented complete analysis.",
    });
  }
  return report("message", risk, [...new Set(reasons)], linkResult.summary, checks);
}

function analyzeUrl(input) {
  const linkResult = inspectUrlInput(input);
  if (linkResult.status !== "ok") {
    const reasonByStatus = {
      invalid_type: "No analyzable web address was provided.",
      empty: "No analyzable web address was provided.",
      too_long: "The web address exceeds the 2,048-character limit; nothing was analyzed.",
      unsupported: "Only one HTTP or HTTPS web address or bare domain can be analyzed.",
      multiple_or_malformed: "Provide exactly one complete web address or bare domain.",
      invalid: "The submitted web address could not be parsed locally.",
      malformed: "The submitted web address contains unsupported characters.",
    };
    return cannotAnalyze(
      "url",
      reasonByStatus[linkResult.status] ??
        "The submitted web address could not be analyzed locally.",
      linkResult.summary,
    );
  }

  const risk = linkResult.checks.length > 0 ? "review" : "no_match";
  const reasons =
    risk === "review"
      ? ["One or more structural URL characteristics require review."]
      : ["No configured structural URL finding was detected; this is not a safety result."];
  return report("url", risk, reasons, linkResult.summary, linkResult.checks);
}

export function analyzeContent(input, options = undefined) {
  const resolved = resolveMode(options);
  if (!resolved.valid) {
    return cannotAnalyze("message", "The requested analysis mode is not supported.");
  }
  return resolved.mode === "url" ? analyzeUrl(input) : analyzeMessage(input);
}
