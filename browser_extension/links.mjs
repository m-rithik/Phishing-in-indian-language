export const MAX_URL_CODE_POINTS = 2_048;
export const MAX_MESSAGE_URL_CANDIDATES = 32;

const DEFANGED_SCHEME = /\bhxxps?:\/\//giu;
const DEFANGED_DOT =
  /\s{0,8}(?:\[\s{0,8}\.\s{0,8}\]|\(\s{0,8}dot\s{0,8}\))\s{0,8}(?=(?:com|in|org|net|xyz|top|site|online|link|info|click|example)\b)/giu;
const HAS_DEFANGED_DOT =
  /\[\s{0,8}\.\s{0,8}\]|\(\s{0,8}dot\s{0,8}\)/iu;
const EXPLICIT_SCHEME = /^[a-z][a-z0-9+.-]{0,31}:\/\//iu;
const SUPPORTED_SCHEME = /^https?:\/\//iu;
const ASCII_WHITESPACE = /[\t\n\f\r ]/u;
const UNSUPPORTED_CONTROL = /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f]/u;
const NUMERIC_IPV4_PART = /^(?:0x[0-9a-f]+|0[0-7]*|[0-9]+)$/iu;
const DEFANGED_MARKER = "\u0000";
const SHORTENER_HOSTS = new Set([
  "bit.ly",
  "buff.ly",
  "goo.gl",
  "is.gd",
  "ow.ly",
  "t.co",
  "tinyurl.com",
]);

const OBSERVATION_CHECKS = {
  defanged: {
    id: "link_defanged",
    label: "Defanged web address",
    detail: "A web address uses altered scheme or dot notation.",
  },
  userinfo: {
    id: "link_userinfo",
    label: "User-information syntax",
    detail: "A web address includes user-information syntax before its host.",
  },
  insecure_http: {
    id: "link_insecure_http",
    label: "Unencrypted protocol",
    detail: "A web address uses HTTP rather than HTTPS.",
  },
  ip_literal: {
    id: "link_ip_literal",
    label: "IP-literal host",
    detail: "A web address uses an IP address instead of a named host.",
  },
  internationalized_host: {
    id: "link_internationalized_host",
    label: "Internationalized host",
    detail: "A web address uses Unicode or encoded internationalized host labels.",
  },
  nondefault_port: {
    id: "link_nondefault_port",
    label: "Non-default port",
    detail: "A web address explicitly uses a non-default network port.",
  },
  shortener: {
    id: "link_shortener",
    label: "Opaque shortened destination",
    detail: "A known shortening service does not reveal its final destination locally.",
  },
  many_labels: {
    id: "link_many_labels",
    label: "Many host labels",
    detail: "A host contains an unusually large number of dot-separated labels.",
  },
};

function codePointLengthExceeds(text, limit) {
  let count = 0;
  for (const _character of text) {
    count += 1;
    if (count > limit) return true;
  }
  return false;
}

function hasUnpairedSurrogate(text) {
  for (let index = 0; index < text.length; index += 1) {
    const codeUnit = text.charCodeAt(index);
    if (codeUnit >= 0xd800 && codeUnit <= 0xdbff) {
      const nextCodeUnit = text.charCodeAt(index + 1);
      if (!(nextCodeUnit >= 0xdc00 && nextCodeUnit <= 0xdfff)) return true;
      index += 1;
    } else if (codeUnit >= 0xdc00 && codeUnit <= 0xdfff) {
      return true;
    }
  }
  return false;
}

function makeDefangedView(text) {
  const withSchemes = text.replace(DEFANGED_SCHEME, (scheme) =>
    `${DEFANGED_MARKER}${scheme.replace(/^hxxp/iu, "http")}`,
  );
  return withSchemes.replace(
    DEFANGED_DOT,
    `${DEFANGED_MARKER}.${DEFANGED_MARKER}`,
  );
}

function trimCandidateToken(rawToken) {
  let start = 0;
  let end = rawToken.length;
  const expectedClosers = [];
  const openingPairs = new Map([
    ["(", ")"],
    ["{", "}"],
    ["<", ">"],
    ['"', '"'],
    ["'", "'"],
  ]);

  while (start < end && openingPairs.has(rawToken[start])) {
    expectedClosers.push(openingPairs.get(rawToken[start]));
    start += 1;
  }
  if (
    rawToken[start] === "[" &&
    /^(?:https?|www\.)/iu.test(rawToken.slice(start + 1, start + 10))
  ) {
    expectedClosers.push("]");
    start += 1;
  }

  let changed = true;
  while (changed && start < end) {
    changed = false;
    if (/[.,;!?"'>]/u.test(rawToken[end - 1])) {
      end -= 1;
      changed = true;
      continue;
    }
    const expected = expectedClosers.at(-1);
    if (expected !== undefined && rawToken[end - 1] === expected) {
      end -= 1;
      expectedClosers.pop();
      changed = true;
    }
  }
  return rawToken.slice(start, end);
}

function authorityFromCandidate(candidate, bare) {
  let remainder = candidate;
  if (!bare) {
    const schemeEnd = remainder.indexOf("://");
    remainder = remainder.slice(schemeEnd + 3);
  }
  const authorityEnd = remainder.search(/[/?#]/u);
  return authorityEnd === -1 ? remainder : remainder.slice(0, authorityEnd);
}

function authorityHasNonAsciiHost(candidate, bare) {
  let authority = authorityFromCandidate(candidate, bare);
  const atIndex = authority.lastIndexOf("@");
  if (atIndex !== -1) authority = authority.slice(atIndex + 1);

  let host = authority;
  if (host.startsWith("[")) {
    const bracketEnd = host.indexOf("]");
    if (bracketEnd !== -1) host = host.slice(0, bracketEnd + 1);
  } else {
    const colonIndex = host.lastIndexOf(":");
    if (colonIndex !== -1) host = host.slice(0, colonIndex);
  }
  for (const character of host) {
    if (character.codePointAt(0) > 0x7f) return true;
  }
  return false;
}

function isNumericIpv4Candidate(host) {
  const parts = host.split(".");
  return parts.length <= 4 && parts.every((part) => NUMERIC_IPV4_PART.test(part));
}

function isBracketedIpv6Authority(authority) {
  const bracketEnd = authority.indexOf("]");
  if (bracketEnd === -1 || !authority.slice(1, bracketEnd).includes(":")) return false;
  const suffix = authority.slice(bracketEnd + 1);
  if (suffix !== "" && !/^:\d{1,5}$/u.test(suffix)) return false;
  try {
    const parsed = new URL(`https://${authority}`);
    return parsed.hostname.startsWith("[") && parsed.hostname.endsWith("]");
  } catch {
    return false;
  }
}

function hasDomainSeparator(host) {
  return /[.\u3002\uff0e\uff61]/u.test(host);
}

function looksLikeBareLocator(candidate) {
  if (candidate === "" || ASCII_WHITESPACE.test(candidate) || candidate.includes("@")) {
    return false;
  }
  const authority = authorityFromCandidate(candidate, true);
  if (authority.startsWith("[")) return isBracketedIpv6Authority(authority);

  let host = authority;
  const colonIndex = host.lastIndexOf(":");
  if (colonIndex !== -1) {
    const port = host.slice(colonIndex + 1);
    if (!/^\d{1,5}$/u.test(port)) return false;
    host = host.slice(0, colonIndex);
  }
  return hasDomainSeparator(host) || isNumericIpv4Candidate(host);
}

function looksLikeMessageBareLocator(candidate) {
  if (!looksLikeBareLocator(candidate)) return false;
  const authority = authorityFromCandidate(candidate, true);
  if (authority.startsWith("[")) return true;

  let host = authority;
  const colonIndex = host.lastIndexOf(":");
  if (colonIndex !== -1) host = host.slice(0, colonIndex);
  const labels = host.replace(/[\u3002\uff0e\uff61]/gu, ".").split(".");
  if (
    labels.some(
      (label) =>
        !/^[\p{L}\p{N}](?:[\p{L}\p{M}\p{N}-]{0,61}[\p{L}\p{M}\p{N}])?$/u.test(
          label,
        ),
    )
  ) {
    return false;
  }
  if (
    labels.length === 4 &&
    labels.every((label) => /^\d{1,3}$/u.test(label) && Number(label) <= 255)
  ) {
    return true;
  }
  const finalLabel = labels.at(-1);
  return finalLabel !== undefined && /^\p{L}[\p{L}\p{M}\p{N}-]{1,62}$/u.test(finalLabel);
}

function hasUserinfoSyntax(candidate, bare) {
  return authorityFromCandidate(candidate, bare).includes("@");
}

function isIpv4Hostname(hostname) {
  const parts = hostname.split(".");
  if (parts.length !== 4) return false;
  return parts.every((part) => {
    if (!/^\d{1,3}$/u.test(part)) return false;
    const number = Number(part);
    return number >= 0 && number <= 255;
  });
}

function inspectCandidate(candidate, { defanged = false } = {}) {
  const hasScheme = EXPLICIT_SCHEME.test(candidate);
  if (hasScheme && !SUPPORTED_SCHEME.test(candidate)) {
    return { status: "unsupported", observations: [] };
  }

  const startsWithWww = /^www\./iu.test(candidate);
  const bare = !hasScheme;
  if (bare && !startsWithWww && !looksLikeBareLocator(candidate)) {
    return { status: "invalid", observations: [] };
  }

  let parsed;
  try {
    parsed = new URL(bare ? `https://${candidate}` : candidate);
  } catch {
    return { status: "invalid", observations: [] };
  }
  if (!parsed.hostname || (parsed.protocol !== "http:" && parsed.protocol !== "https:")) {
    return { status: "invalid", observations: [] };
  }

  const hostname = parsed.hostname.toLocaleLowerCase("en");
  const hostWithoutTrailingDot = hostname.endsWith(".")
    ? hostname.slice(0, -1)
    : hostname;
  const ipLiteral =
    (hostname.startsWith("[") && hostname.endsWith("]")) ||
    isIpv4Hostname(hostname);
  const observations = [];
  if (defanged) observations.push("defanged");
  if (hasUserinfoSyntax(candidate, bare)) observations.push("userinfo");
  if (parsed.protocol === "http:") observations.push("insecure_http");
  if (ipLiteral) observations.push("ip_literal");
  if (
    authorityHasNonAsciiHost(candidate, bare) ||
    hostname.split(".").some((label) => label.startsWith("xn--"))
  ) {
    observations.push("internationalized_host");
  }
  if (parsed.port !== "") observations.push("nondefault_port");
  if (SHORTENER_HOSTS.has(hostWithoutTrailingDot)) observations.push("shortener");
  if (!ipLiteral && hostWithoutTrailingDot.split(".").filter(Boolean).length > 4) {
    observations.push("many_labels");
  }
  return { status: "ok", observations };
}

function uniqueChecks(observations) {
  const seen = new Set();
  const checks = [];
  for (const observation of observations) {
    if (seen.has(observation)) continue;
    seen.add(observation);
    checks.push({ ...OBSERVATION_CHECKS[observation] });
  }
  return checks;
}

export function inspectMessageLinks(input) {
  const view = makeDefangedView(input);
  const observations = [];
  let inspected = 0;
  let flagged = 0;
  let candidatesSeen = 0;
  let found = false;
  let limited = false;

  for (const tokenMatch of view.matchAll(/\S+/gu)) {
    const markedCandidate = trimCandidateToken(tokenMatch[0]);
    const candidate = markedCandidate.replaceAll(DEFANGED_MARKER, "");
    const candidateWasDefanged = markedCandidate !== candidate;
    if (
      !EXPLICIT_SCHEME.test(candidate) &&
      !/^www\./iu.test(candidate) &&
      !looksLikeMessageBareLocator(candidate)
    ) {
      continue;
    }
    found = true;
    candidatesSeen += 1;
    if (candidatesSeen > MAX_MESSAGE_URL_CANDIDATES) {
      limited = true;
      break;
    }
    if (codePointLengthExceeds(candidate, MAX_URL_CODE_POINTS)) {
      limited = true;
      continue;
    }

    const result = inspectCandidate(candidate, { defanged: candidateWasDefanged });
    if (result.status !== "ok") {
      limited = true;
      continue;
    }
    inspected += 1;
    if (result.observations.length > 0) flagged += 1;
    observations.push(...result.observations);
  }

  return {
    found,
    limited,
    summary: { inspected, flagged, limited },
    checks: uniqueChecks(observations),
  };
}

export function inspectUrlInput(input) {
  const emptySummary = { inspected: 0, flagged: 0, limited: false };
  if (typeof input !== "string") {
    return { status: "invalid_type", summary: emptySummary, checks: [] };
  }
  if (UNSUPPORTED_CONTROL.test(input) || hasUnpairedSurrogate(input)) {
    return { status: "malformed", summary: emptySummary, checks: [] };
  }

  const candidate = input.trim();
  if (candidate === "") {
    return { status: "empty", summary: emptySummary, checks: [] };
  }
  if (codePointLengthExceeds(candidate, MAX_URL_CODE_POINTS)) {
    return {
      status: "too_long",
      summary: { inspected: 0, flagged: 0, limited: true },
      checks: [],
    };
  }
  if (ASCII_WHITESPACE.test(candidate)) {
    return { status: "multiple_or_malformed", summary: emptySummary, checks: [] };
  }
  if (/^hxxps?:\/\//iu.test(candidate) || HAS_DEFANGED_DOT.test(candidate)) {
    return { status: "unsupported", summary: emptySummary, checks: [] };
  }
  const result = inspectCandidate(candidate);
  if (result.status !== "ok") {
    return { status: result.status, summary: emptySummary, checks: [] };
  }
  return {
    status: "ok",
    summary: {
      inspected: 1,
      flagged: result.observations.length > 0 ? 1 : 0,
      limited: false,
    },
    checks: uniqueChecks(result.observations),
  };
}
