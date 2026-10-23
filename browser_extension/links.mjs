export const MAX_URL_CODE_POINTS = 2_048;
export const MAX_MESSAGE_URL_CANDIDATES = 32;
const MAX_QUERY_PAIRS = 32;
const MAX_EMBEDDED_DESTINATIONS = 4;

const NAVIGATION_QUERY_KEYS = new Set([
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
]);

const DEFANGED_SCHEME = /\bhxxps?:\/\//giu;
const SPACED_DEFANGED_DOT =
  /\s{1,8}(?:\[\s{0,8}\.\s{0,8}\]|\(\s{0,8}dot\s{0,8}\))\s{0,8}(?=(?:com|dev|in|org|net|xyz|top|site|online|link|info|click|example)(?=$|[^\p{L}\p{M}\p{N}-]))/giu;
const TIGHT_DEFANGED_DOT =
  /(?:\[\s{0,8}\.\s{0,8}\]|\(\s{0,8}dot\s{0,8}\))(?=\p{L}[\p{L}\p{M}\p{N}-]{1,62}(?=$|[^\p{L}\p{M}\p{N}-]))/giu;
const HAS_DEFANGED_DOT =
  /\[\s{0,8}\.\s{0,8}\]|\(\s{0,8}dot\s{0,8}\)/iu;
const EXPLICIT_SCHEME = /^[a-z][a-z0-9+.-]{0,31}:\/\//iu;
const SUPPORTED_SCHEME = /^https?:\/\//iu;
const INCOMPLETE_WEB_PREFIX =
  /^(?:https?|hxxps?)(?:::\/\/|;:\/\/|;|:(?!\/\/)[\\/]{0,2}|\/\/)/iu;
const EMBEDDED_LOCATOR_START =
  /(?:\u0000)?(?:[a-z][a-z0-9+.-]{0,31}:\/\/|www\.)|(?:https?|hxxps?)(?:::\/\/|;:\/\/|;|:(?!\/\/)[\\/]{0,2}|\/\/)/giu;
const WEB_SCHEME_START =
  /(?:\u0000)?(?:https?|hxxps?)(?:\/\/|:\/\/|::\/\/|;:\/\/|;|:(?!\/\/)[\\/]{0,2})/giu;
const EXPLICIT_SCHEME_AT_INDEX = /[a-z][a-z0-9+.-]{0,31}:\/\//iuy;
const INCOMPLETE_WEB_PREFIX_AT_INDEX =
  /(?:https?|hxxps?)(?:::\/\/|;:\/\/|;|:(?!\/\/)[\\/]{0,2}|\/\/)/iuy;
const MESSAGE_HOST =
  String.raw`[\p{L}\p{N}](?:[\p{L}\p{M}\p{N}-]{0,61}[\p{L}\p{M}\p{N}])?(?:[.\u3002\uff0e\uff61][\p{L}\p{N}](?:[\p{L}\p{M}\p{N}-]{0,61}[\p{L}\p{M}\p{N}])?)+`;
const MESSAGE_HOST_FINDER = new RegExp(MESSAGE_HOST, "gu");
const MESSAGE_HOST_AT_INDEX = new RegExp(MESSAGE_HOST, "uy");
const IPV6_FINDER = /\[[0-9a-f:.]+\](?::\d{1,5})?/giu;
const UNICODE_WHITESPACE = /\p{White_Space}/u;
const UNSUPPORTED_CONTROL = /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f]/u;
const DEFAULT_IGNORABLES =
  /[\p{Cf}\u034f\u115f\u1160\u17b4\u17b5\u180b-\u180f\u3164\ufe00-\ufe0f\uffa0\ufff0-\ufff8\u{1bca0}-\u{1bca3}\u{1d173}-\u{1d17a}\u{e0000}-\u{e0fff}]/gu;
const NUMERIC_IPV4_PART = /^(?:0x[0-9a-f]+|0[0-7]*|[0-9]+)$/iu;
const DEFANGED_MARKER = "\u0000";
const WRAPPER_PAIRS = new Map([
  ["(", ")"],
  ["[", "]"],
  ["{", "}"],
  ["<", ">"],
  ['"', '"'],
  ["'", "'"],
  ["“", "”"],
  ["‘", "’"],
  ["«", "»"],
  ["‹", "›"],
  ["〈", "〉"],
  ["《", "》"],
  ["「", "」"],
  ["『", "』"],
  ["【", "】"],
  ["〔", "〕"],
  ["〖", "〗"],
  ["〘", "〙"],
  ["〚", "〛"],
]);
const CLOSER_TO_OPENER = new Map(
  [...WRAPPER_PAIRS].map(([opener, closer]) => [closer, opener]),
);
const TRAILING_SENTENCE_PUNCTUATION = new Set([
  ".",
  ",",
  ";",
  ":",
  "!",
  "?",
  "…",
  "।",
  "॥",
  "、",
  "。",
  "，",
  "；",
  "：",
  "！",
  "？",
  "｡",
  "､",
]);
const BOUNDARY_DECORATION =
  /^(?:\p{Extended_Pictographic}|\p{So}|\p{Sk}|[\u2022\u2023\u2043\u2190-\u21ff\u2219\u22c5\u25e6])$/u;
const MAX_BOUNDARY_DECORATIONS = 16;
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
  nested_destination: {
    id: "link_nested_destination",
    label: "Embedded destination: Navigation field",
    detail:
      "A navigation-related query field contains another web address; this does not show that navigation occurred.",
  },
  nested_userinfo: {
    id: "link_nested_userinfo",
    label: "Embedded destination: User-information syntax",
    detail: "An embedded web address includes user-information syntax before its host.",
  },
  nested_insecure_http: {
    id: "link_nested_insecure_http",
    label: "Embedded destination: Unencrypted protocol",
    detail: "An embedded web address uses HTTP rather than HTTPS.",
  },
  nested_ip_literal: {
    id: "link_nested_ip_literal",
    label: "Embedded destination: IP-literal host",
    detail: "An embedded web address uses an IP address instead of a named host.",
  },
  nested_internationalized_host: {
    id: "link_nested_internationalized_host",
    label: "Embedded destination: Internationalized host",
    detail:
      "An embedded web address uses Unicode or encoded internationalized host labels.",
  },
  nested_nondefault_port: {
    id: "link_nested_nondefault_port",
    label: "Embedded destination: Non-default port",
    detail: "An embedded web address explicitly uses a non-default network port.",
  },
  nested_shortener: {
    id: "link_nested_shortener",
    label: "Embedded destination: Opaque shortened destination",
    detail:
      "An embedded web address uses a known shortening service whose final destination is not available locally.",
  },
  nested_many_labels: {
    id: "link_nested_many_labels",
    label: "Embedded destination: Many host labels",
    detail:
      "An embedded web address contains an unusually large number of dot-separated host labels.",
  },
  nested_inspection_limited: {
    id: "link_nested_inspection_limited",
    label: "Embedded destination: Incomplete inspection",
    detail:
      "An embedded destination format or local query-inspection limit prevented complete analysis.",
  },
};

const NESTED_OBSERVATION_NAMES = Object.freeze({
  userinfo: "nested_userinfo",
  insecure_http: "nested_insecure_http",
  ip_literal: "nested_ip_literal",
  internationalized_host: "nested_internationalized_host",
  nondefault_port: "nested_nondefault_port",
  shortener: "nested_shortener",
  many_labels: "nested_many_labels",
});

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
  const withoutOriginalIgnorables = text.replace(DEFAULT_IGNORABLES, "");
  const normalized = withoutOriginalIgnorables
    .normalize("NFKC")
    .replace(DEFAULT_IGNORABLES, "");
  const withSchemes = normalized.replace(DEFANGED_SCHEME, (scheme) =>
    `${DEFANGED_MARKER}${scheme.replace(/^hxxp/iu, "http")}`,
  );
  return withSchemes
    .replace(SPACED_DEFANGED_DOT, `${DEFANGED_MARKER}.${DEFANGED_MARKER}`)
    .replace(TIGHT_DEFANGED_DOT, `${DEFANGED_MARKER}.${DEFANGED_MARKER}`);
}

function startsWithBareIpv6Locator(token) {
  if (!token.startsWith("[")) return false;
  const bracketEnd = token.indexOf("]");
  if (bracketEnd === -1) return false;
  return isBracketedIpv6Authority(token.slice(0, bracketEnd + 1));
}

function trimCandidateToken(rawToken) {
  let start = 0;
  let end = rawToken.length;
  const expectedClosers = [];

  while (start < end && WRAPPER_PAIRS.has(rawToken[start])) {
    if (
      rawToken[start] === "[" &&
      startsWithBareIpv6Locator(rawToken.slice(start, end))
    ) {
      break;
    }
    expectedClosers.push(WRAPPER_PAIRS.get(rawToken[start]));
    start += 1;
  }

  const closerBalances = new Map();
  for (const [opener, closer] of WRAPPER_PAIRS) {
    if (opener !== closer) closerBalances.set(closer, 0);
  }
  for (const character of rawToken.slice(start, end)) {
    const openerCloser = WRAPPER_PAIRS.get(character);
    if (openerCloser !== undefined && openerCloser !== character) {
      closerBalances.set(openerCloser, closerBalances.get(openerCloser) + 1);
    }
    const opener = CLOSER_TO_OPENER.get(character);
    if (opener !== undefined && opener !== character) {
      closerBalances.set(character, closerBalances.get(character) - 1);
    }
  }

  let changed = true;
  while (changed && start < end) {
    changed = false;
    const trailingCharacter = rawToken[end - 1];
    if (expectedClosers.at(-1) === trailingCharacter) {
      end -= 1;
      expectedClosers.pop();
      if (closerBalances.has(trailingCharacter)) {
        closerBalances.set(
          trailingCharacter,
          closerBalances.get(trailingCharacter) + 1,
        );
      }
      changed = true;
      continue;
    }
    if (TRAILING_SENTENCE_PUNCTUATION.has(trailingCharacter)) {
      end -= 1;
      changed = true;
      continue;
    }
    const opener = CLOSER_TO_OPENER.get(trailingCharacter);
    if (
      opener !== undefined &&
      (opener === trailingCharacter || closerBalances.get(trailingCharacter) < 0)
    ) {
      end -= 1;
      if (opener !== trailingCharacter) {
        closerBalances.set(
          trailingCharacter,
          closerBalances.get(trailingCharacter) + 1,
        );
      }
      changed = true;
    }
  }
  return { text: rawToken.slice(start, end), start, end };
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
  if (candidate === "" || UNICODE_WHITESPACE.test(candidate) || candidate.includes("@")) {
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

function looksLikeEmailShapedToken(candidate) {
  const parts = candidate.split("@");
  if (parts.length < 2) return false;
  return parts.slice(1).some((part) => looksLikeMessageBareLocator(part));
}

function looksLikeIncompleteMessageLocator(candidate) {
  const prefixMatch = INCOMPLETE_WEB_PREFIX.exec(candidate);
  if (prefixMatch === null) return false;
  return looksLikeMessageBareLocator(
    candidate.slice(prefixMatch[0].length).replaceAll("\\", "/"),
  );
}

function authorityHost(candidate, bare) {
  let authority = authorityFromCandidate(candidate, bare);
  const atIndex = authority.lastIndexOf("@");
  if (atIndex !== -1) authority = authority.slice(atIndex + 1);

  if (authority.startsWith("[")) {
    const bracketEnd = authority.indexOf("]");
    if (bracketEnd === -1) return null;
    const suffix = authority.slice(bracketEnd + 1);
    if (suffix !== "" && !/^:\d{1,5}$/u.test(suffix)) return null;
    return isBracketedIpv6Authority(authority) ? authority.slice(0, bracketEnd + 1) : null;
  }

  const colonIndex = authority.lastIndexOf(":");
  if (colonIndex !== -1) {
    const port = authority.slice(colonIndex + 1);
    if (!/^\d{1,5}$/u.test(port)) return null;
    authority = authority.slice(0, colonIndex);
  }
  return authority;
}

function hasValidNamedOrIpv4Host(candidate, bare) {
  const rawHost = authorityHost(candidate, bare);
  if (rawHost === null || rawHost === "" || rawHost.startsWith("[")) {
    return rawHost !== null && rawHost.startsWith("[");
  }

  const host = rawHost.endsWith(".") ? rawHost.slice(0, -1) : rawHost;
  if (host === "") return false;
  if (isNumericIpv4Candidate(host)) return true;

  const labels = host.replace(/[\u3002\uff0e\uff61]/gu, ".").split(".");
  return labels.every((label) =>
    /^[\p{L}\p{N}](?:[\p{L}\p{M}\p{N}-]{0,61}[\p{L}\p{M}\p{N}])?$/u.test(
      label,
    ),
  );
}

function messageCandidateFlags(candidate) {
  const explicitScheme = EXPLICIT_SCHEME.exec(candidate)?.[0] ?? "";
  const looksLikeJoinedHttpText =
    explicitScheme !== "" &&
    !/^https?:\/\//iu.test(explicitScheme) &&
    /https?:\/\//iu.test(explicitScheme);
  const locator =
    (explicitScheme !== "" && !looksLikeJoinedHttpText) ||
    /^www\./iu.test(candidate) ||
    looksLikeMessageBareLocator(candidate);
  return {
    locator,
    incomplete: looksLikeIncompleteMessageLocator(candidate),
    email: looksLikeEmailShapedToken(candidate),
  };
}

function isUsableMessageCandidate(candidate) {
  const flags = messageCandidateFlags(candidate);
  if (flags.incomplete || flags.email) return true;
  if (!flags.locator) return false;
  const status = inspectCandidate(candidate).status;
  return status === "ok" || status === "unsupported";
}

function isLocatorStartBoundary(token, start) {
  if (start === 0) return true;
  const previousCharacter = previousCodePoint(token, start)?.character;
  return (
    previousCharacter !== undefined &&
    !/[\p{L}\p{M}\p{N}_]/u.test(previousCharacter)
  );
}

function previousCodePoint(text, end) {
  if (end <= 0) return null;
  let start = end - 1;
  const finalCodeUnit = text.charCodeAt(start);
  if (finalCodeUnit >= 0xdc00 && finalCodeUnit <= 0xdfff && start > 0) {
    const leadingCodeUnit = text.charCodeAt(start - 1);
    if (leadingCodeUnit >= 0xd800 && leadingCodeUnit <= 0xdbff) start -= 1;
  }
  return { character: text.slice(start, end), start };
}

function authorityEndsWithDomainSeparator(candidate) {
  const bare = !EXPLICIT_SCHEME.test(candidate);
  const authority = authorityFromCandidate(candidate, bare);
  return /[.\u3002\uff0e\uff61]$/u.test(authority);
}

function trimTrailingDecorations(markedCandidate) {
  let end = markedCandidate.length;
  let count = 0;
  while (count < MAX_BOUNDARY_DECORATIONS) {
    const previous = previousCodePoint(markedCandidate, end);
    if (previous === null || !BOUNDARY_DECORATION.test(previous.character)) break;
    end = previous.start;
    count += 1;
  }
  if (end === markedCandidate.length) return markedCandidate;

  const trimmed = markedCandidate.slice(0, end);
  const candidate = trimmed.replaceAll(DEFANGED_MARKER, "");
  if (
    candidate === "" ||
    authorityEndsWithDomainSeparator(candidate) ||
    !isUsableMessageCandidate(candidate)
  ) {
    return markedCandidate;
  }
  return trimmed;
}

function canonicalizeMarkedCandidate(markedCandidate) {
  const withoutMarkers = markedCandidate.replaceAll(DEFANGED_MARKER, "");
  const hasDefangedScheme = /^hxxps?:\/\//iu.test(withoutMarkers);
  return {
    candidate: hasDefangedScheme
      ? withoutMarkers.replace(/^hxxp/iu, "http")
      : withoutMarkers,
    defanged: markedCandidate.includes(DEFANGED_MARKER) || hasDefangedScheme,
  };
}

function findDecoratedCandidateStart(token) {
  let start = 0;
  let count = 0;
  while (count < MAX_BOUNDARY_DECORATIONS) {
    const character = token.codePointAt(start);
    if (character === undefined) break;
    const text = String.fromCodePoint(character);
    if (!BOUNDARY_DECORATION.test(text)) break;
    start += text.length;
    count += 1;

    const trimmed = trimCandidateToken(token.slice(start));
    const markedCandidate = trimTrailingDecorations(trimmed.text);
    if (isUsableMessageCandidate(markedCandidate.replaceAll(DEFANGED_MARKER, ""))) {
      return start;
    }
  }
  return -1;
}

function isCandidateDelimiter(character) {
  return (
    character === ":" ||
    character === "," ||
    character === ";" ||
    WRAPPER_PAIRS.has(character) ||
    CLOSER_TO_OPENER.has(character) ||
    BOUNDARY_DECORATION.test(character)
  );
}

function collectEmailCandidates(token) {
  const candidates = [];
  let atIndex = token.indexOf("@");
  while (atIndex !== -1) {
    MESSAGE_HOST_AT_INDEX.lastIndex = atIndex + 1;
    const domainMatch = MESSAGE_HOST_AT_INDEX.exec(token);
    if (
      domainMatch !== null &&
      looksLikeMessageBareLocator(domainMatch[0])
    ) {
      let start = atIndex;
      while (start > 0) {
        const previous = previousCodePoint(token, start);
        if (previous === null || isCandidateDelimiter(previous.character)) break;
        start = previous.start;
      }
      if (start < atIndex) {
        candidates.push({
          kind: "email",
          start,
          end: atIndex + 1 + domainMatch[0].length,
          priority: 1,
        });
      }
    }
    atIndex = token.indexOf("@", atIndex + 1);
  }
  return candidates;
}

function collectBareCandidates(token) {
  const candidates = [];
  MESSAGE_HOST_FINDER.lastIndex = 0;
  let match = MESSAGE_HOST_FINDER.exec(token);
  while (match !== null) {
    if (!looksLikeMessageBareLocator(match[0])) {
      match = MESSAGE_HOST_FINDER.exec(token);
      continue;
    }
    const previous = previousCodePoint(token, match.index)?.character;
    if (
      token.slice(Math.max(0, match.index - 3), match.index) === "://" ||
      (previous !== undefined && /[\p{L}\p{M}\p{N}_@.-]/u.test(previous))
    ) {
      match = MESSAGE_HOST_FINDER.exec(token);
      continue;
    }
    candidates.push({ kind: "locator", start: match.index, priority: 2 });
    match = MESSAGE_HOST_FINDER.exec(token);
  }

  IPV6_FINDER.lastIndex = 0;
  match = IPV6_FINDER.exec(token);
  while (match !== null) {
    if (!isLocatorStartBoundary(token, match.index)) {
      match = IPV6_FINDER.exec(token);
      continue;
    }
    if (looksLikeMessageBareLocator(match[0])) {
      candidates.push({ kind: "locator", start: match.index, priority: 2 });
    }
    match = IPV6_FINDER.exec(token);
  }
  return candidates;
}

function collectEmbeddedCandidates(token) {
  const candidates = [];
  EMBEDDED_LOCATOR_START.lastIndex = 0;
  let match = EMBEDDED_LOCATOR_START.exec(token);
  while (match !== null) {
    const joinedHttpMatch =
      /^(?!https?:\/\/)[a-z0-9+.-]*(https?:\/\/)/iu.exec(match[0]);
    if (joinedHttpMatch !== null) {
      const innerStart = match.index + joinedHttpMatch[0].lastIndexOf(joinedHttpMatch[1]);
      if (isLocatorStartBoundary(token, innerStart)) {
        candidates.push({ kind: "locator", start: innerStart, priority: 0 });
      }
    } else if (isLocatorStartBoundary(token, match.index)) {
      candidates.push({ kind: "locator", start: match.index, priority: 0 });
    }
    match = EMBEDDED_LOCATOR_START.exec(token);
  }
  return candidates;
}

function isUsableCollectedLocator(token, candidate, boundaryIndexes) {
  if (candidate.kind !== "locator") return false;
  const span = locatorCandidateSpan(
    token,
    candidate.start,
    boundaryIndexes,
    new Set(),
  );
  const flags = messageCandidateFlags(span.candidate);
  if (flags.incomplete) return true;
  if (!flags.locator || codePointLengthExceeds(span.candidate, MAX_URL_CODE_POINTS)) {
    return false;
  }
  const status = inspectCandidate(span.candidate).status;
  return status === "ok" || status === "unsupported";
}

function collectMessageCandidates(token, boundaryIndexes) {
  const candidates = [
    ...collectEmbeddedCandidates(token),
    ...collectEmailCandidates(token),
    ...collectBareCandidates(token),
  ].sort((first, second) =>
    first.start === second.start
      ? first.priority - second.priority
      : first.start - second.start,
  );

  const firstUsableLocator = candidates.find(
    (candidate) =>
      candidate.kind === "locator" &&
      (candidate.priority === 0 ||
        isUsableCollectedLocator(token, candidate, boundaryIndexes)),
  );
  if (firstUsableLocator === undefined) return candidates;

  const byStart = new Map(candidates.map((candidate) => [candidate.start, candidate]));
  WEB_SCHEME_START.lastIndex = firstUsableLocator.start + 1;
  let match = WEB_SCHEME_START.exec(token);
  while (match !== null) {
    if (match.index > firstUsableLocator.start) {
      const existing = byStart.get(match.index);
      if (existing === undefined) {
        const recovered = {
          kind: "locator",
          start: match.index,
          priority: 0,
          forceSplit: true,
        };
        candidates.push(recovered);
        byStart.set(match.index, recovered);
      } else if (existing.kind === "locator") {
        existing.forceSplit = true;
      }
    }
    match = WEB_SCHEME_START.exec(token);
  }
  return candidates.sort((first, second) =>
    first.start === second.start
      ? first.priority - second.priority
      : first.start - second.start,
  );
}

function candidatePrefix(token, start) {
  const prefixStart = token[start] === DEFANGED_MARKER ? start + 1 : start;
  EXPLICIT_SCHEME_AT_INDEX.lastIndex = prefixStart;
  const explicit = EXPLICIT_SCHEME_AT_INDEX.exec(token);
  if (explicit !== null) {
    return {
      length: prefixStart - start + explicit[0].length,
      incomplete: false,
    };
  }

  INCOMPLETE_WEB_PREFIX_AT_INDEX.lastIndex = prefixStart;
  const incomplete = INCOMPLETE_WEB_PREFIX_AT_INDEX.exec(token);
  return {
    length: incomplete === null ? 0 : prefixStart - start + incomplete[0].length,
    incomplete: incomplete !== null,
  };
}

function buildBoundaryIndexes(token) {
  const nextAt = new Int32Array(token.length + 1);
  const nextStop = new Int32Array(token.length + 1);
  nextAt.fill(-1);
  nextStop.fill(-1);
  let atIndex = -1;
  let stopIndex = -1;

  for (let index = token.length - 1; index >= 0; index -= 1) {
    const character = String.fromCodePoint(token.codePointAt(index));
    if (character === "@") atIndex = index;
    if (
      character === "/" ||
      character === "?" ||
      character === "#" ||
      character === "|" ||
      BOUNDARY_DECORATION.test(character)
    ) {
      stopIndex = index;
    }
    nextAt[index] = atIndex;
    nextStop[index] = stopIndex;
  }
  return { nextAt, nextStop };
}

function hasFollowingUserinfo(index, boundaryIndexes) {
  const atIndex = boundaryIndexes.nextAt[index + 1];
  const stopIndex = boundaryIndexes.nextStop[index + 1];
  return atIndex !== -1 && (stopIndex === -1 || atIndex < stopIndex);
}

function hasValidPortStart(token, colonIndex) {
  let index = colonIndex + 1;
  const digitStart = index;
  while (index < token.length && /\d/u.test(token[index])) index += 1;
  const digitCount = index - digitStart;
  if (digitCount < 1 || digitCount > 5) return false;
  if (index === token.length) return true;
  const character = String.fromCodePoint(token.codePointAt(index));
  return (
    character === "/" ||
    character === "?" ||
    character === "#" ||
    character === "|" ||
    TRAILING_SENTENCE_PUNCTUATION.has(character) ||
    WRAPPER_PAIRS.has(character) ||
    CLOSER_TO_OPENER.has(character) ||
    BOUNDARY_DECORATION.test(character)
  );
}

function locatorBoundaryEnd(token, start, boundaryIndexes, candidateStarts) {
  const prefix = candidatePrefix(token, start);
  const authorityStart = start + prefix.length;
  let inPath = false;
  let inIpv6 = token[authorityStart] === "[";
  let authorityHasSeparator = false;
  let lastValidAuthorityEnd = authorityStart;
  const pathCloserDepth = new Map();

  for (let index = authorityStart; index < token.length; ) {
    if (index > authorityStart && candidateStarts.has(index)) {
      return inPath || lastValidAuthorityEnd === authorityStart
        ? index
        : lastValidAuthorityEnd;
    }
    const codePoint = token.codePointAt(index);
    const character = String.fromCodePoint(codePoint);
    const width = codePoint > 0xffff ? 2 : 1;
    if (character === DEFANGED_MARKER) {
      index += width;
      continue;
    }

    if (!inPath) {
      if (
        character === "/" ||
        character === "?" ||
        character === "#" ||
        (prefix.incomplete && character === "\\")
      ) {
        inPath = true;
        index += width;
        continue;
      }
      if (inIpv6) {
        if (character === "]") {
          inIpv6 = false;
          lastValidAuthorityEnd = index + width;
        }
        index += width;
        continue;
      }
      if (
        character === "[" &&
        (index === authorityStart || token[index - 1] === "@")
      ) {
        inIpv6 = true;
        index += width;
        continue;
      }
      if (character === "@") {
        authorityHasSeparator = false;
        lastValidAuthorityEnd = index + width;
        index += width;
        continue;
      }
      if (hasFollowingUserinfo(index, boundaryIndexes)) {
        index += width;
        continue;
      }
      if (character === "." || character === "\uff0e" || character === "\uff61") {
        authorityHasSeparator = true;
        index += width;
        continue;
      }
      if (character === "\u3002") {
        if (authorityHasSeparator) return index;
        authorityHasSeparator = true;
        index += width;
        continue;
      }
      if (character === ":") {
        if (hasValidPortStart(token, index)) {
          index += width;
          continue;
        }
        return index;
      }
      if (/^[\p{L}\p{M}\p{N}-]$/u.test(character)) {
        if (character !== "-") lastValidAuthorityEnd = index + width;
        index += width;
        continue;
      }
      return index;
    }

    const expectedCloser = WRAPPER_PAIRS.get(character);
    if (expectedCloser !== undefined && expectedCloser !== character) {
      pathCloserDepth.set(
        expectedCloser,
        (pathCloserDepth.get(expectedCloser) ?? 0) + 1,
      );
      index += width;
      continue;
    }
    if (CLOSER_TO_OPENER.has(character)) {
      const depth = pathCloserDepth.get(character) ?? 0;
      if (depth === 0) return index;
      pathCloserDepth.set(character, depth - 1);
      index += width;
      continue;
    }
    if (character === "|") return index;
    if (
      ((character === "," || character === ";") ||
        BOUNDARY_DECORATION.test(character)) &&
      candidateStarts.has(index + width)
    ) {
      return index;
    }
    index += width;
  }
  return token.length;
}

function locatorCandidateSpan(
  token,
  start,
  boundaryIndexes,
  candidateStarts,
) {
  const end = locatorBoundaryEnd(
    token,
    start,
    boundaryIndexes,
    candidateStarts,
  );
  const trimmed = trimCandidateToken(token.slice(start, end));
  const markedCandidate = trimTrailingDecorations(trimmed.text);
  const candidateStart = start + trimmed.start;
  return {
    start: candidateStart,
    end: candidateStart + markedCandidate.length,
    ...canonicalizeMarkedCandidate(markedCandidate),
  };
}

function scanMessageToken(token) {
  const spans = [];
  const boundaryIndexes = buildBoundaryIndexes(token);
  const candidates = collectMessageCandidates(token, boundaryIndexes);
  const candidateStarts = new Set(
    candidates
      .filter((candidate) => candidate.forceSplit === true)
      .map((candidate) => candidate.start),
  );
  let cursor = 0;

  for (const next of candidates) {
    if (next.start < cursor) continue;
    const span =
      next.kind === "email"
        ? {
            start: next.start,
            end: next.end,
            candidate: token.slice(next.start, next.end).replaceAll(DEFANGED_MARKER, ""),
            defanged: false,
          }
        : locatorCandidateSpan(
            token,
            next.start,
            boundaryIndexes,
            candidateStarts,
          );
    const flags = messageCandidateFlags(span.candidate);
    if (
      span.end > span.start &&
      (flags.locator || flags.incomplete || flags.email)
    ) {
      spans.push({ ...span, flags });
      cursor = span.end;
    }
  }

  if (spans.length === 0) {
    let start = findDecoratedCandidateStart(token);
    if (start === -1) start = 0;
    const trimmed = trimCandidateToken(token.slice(start));
    const markedCandidate = trimTrailingDecorations(trimmed.text);
    const fallback = {
      start: start + trimmed.start,
      end: start + trimmed.start + markedCandidate.length,
      ...canonicalizeMarkedCandidate(markedCandidate),
    };
    const flags = messageCandidateFlags(fallback.candidate);
    if (flags.locator || flags.incomplete || flags.email) {
      spans.push({ ...fallback, flags });
    }
  }
  return spans;
}

function semanticOutsideSpan(text, followsMaskedSpan) {
  if (!followsMaskedSpan || !text.startsWith("_")) return text;
  const underscoreEnd = /^_+/u.exec(text)?.[0].length ?? 0;
  return `${text.slice(0, underscoreEnd)} ${text.slice(underscoreEnd)}`;
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

function inspectEmbeddedDestinations(parsed) {
  const observations = [];
  let qualifyingDestinations = 0;
  let queryPairs = 0;
  let limited = false;

  for (const [rawKey, value] of parsed.searchParams) {
    queryPairs += 1;
    if (queryPairs > MAX_QUERY_PAIRS) {
      limited = true;
      break;
    }
    if (!NAVIGATION_QUERY_KEYS.has(rawKey.toLocaleLowerCase("en"))) continue;

    const absoluteDestination = /^https?:\/\//iu.test(value);
    const protocolRelativeDestination = value.startsWith("//");
    if (!absoluteDestination && !protocolRelativeDestination) {
      if (/^[a-z][a-z0-9+.-]{0,31}:/iu.test(value)) limited = true;
      continue;
    }

    observations.push("nested_destination");
    qualifyingDestinations += 1;
    if (qualifyingDestinations > MAX_EMBEDDED_DESTINATIONS) {
      limited = true;
      continue;
    }

    const candidate = protocolRelativeDestination ? `https:${value}` : value;
    if (
      codePointLengthExceeds(candidate, MAX_URL_CODE_POINTS) ||
      UNSUPPORTED_CONTROL.test(candidate) ||
      UNICODE_WHITESPACE.test(candidate) ||
      hasUnpairedSurrogate(candidate) ||
      candidate.includes("\ufffd") ||
      /%(?![0-9a-f]{2})/iu.test(candidate)
    ) {
      limited = true;
      continue;
    }
    const result = inspectCandidate(candidate, { inspectNested: false });
    if (result.status !== "ok") {
      limited = true;
      continue;
    }
    for (const observation of result.observations) {
      const nestedObservation = NESTED_OBSERVATION_NAMES[observation];
      if (nestedObservation !== undefined) observations.push(nestedObservation);
    }
  }

  if (limited) observations.push("nested_inspection_limited");
  return { observations, limited };
}

function inspectCandidate(
  candidate,
  { defanged = false, inspectNested = true } = {},
) {
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
  if (!hasValidNamedOrIpv4Host(candidate, bare)) {
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
  let limited = false;
  if (inspectNested) {
    const nestedResult = inspectEmbeddedDestinations(parsed);
    observations.push(...nestedResult.observations);
    limited = nestedResult.limited;
  }
  return { status: "ok", observations, limited };
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

export function inspectMessageContext(input) {
  const view = makeDefangedView(input);
  const observations = [];
  const semanticParts = [];
  let semanticCursor = 0;
  let inspected = 0;
  let flagged = 0;
  let candidatesSeen = 0;
  let found = false;
  let limited = false;

  for (const tokenMatch of view.matchAll(/\S+/gu)) {
    const token = tokenMatch[0];
    semanticParts.push(view.slice(semanticCursor, tokenMatch.index));
    const spans = scanMessageToken(token);
    let tokenCursor = 0;
    for (const span of spans) {
      semanticParts.push(
        semanticOutsideSpan(token.slice(tokenCursor, span.start), tokenCursor > 0),
        " ",
      );
      tokenCursor = span.end;
    }
    semanticParts.push(
      semanticOutsideSpan(token.slice(tokenCursor), tokenCursor > 0),
    );
    semanticCursor = tokenMatch.index + token.length;

    for (const span of spans) {
      if (!span.flags.locator && !span.flags.incomplete) continue;
      found = true;
      candidatesSeen += 1;
      if (candidatesSeen > MAX_MESSAGE_URL_CANDIDATES) {
        limited = true;
        continue;
      }
      if (codePointLengthExceeds(span.candidate, MAX_URL_CODE_POINTS)) {
        limited = true;
        continue;
      }
      if (span.flags.incomplete) {
        limited = true;
        continue;
      }

      const result = inspectCandidate(span.candidate, { defanged: span.defanged });
      if (result.status !== "ok") {
        limited = true;
        continue;
      }
      inspected += 1;
      if (result.limited) limited = true;
      if (result.observations.length > 0) flagged += 1;
      observations.push(...result.observations);
    }
  }

  semanticParts.push(view.slice(semanticCursor));

  const linkResult = {
    found,
    limited,
    summary: { inspected, flagged, limited },
    checks: uniqueChecks(observations),
  };
  return {
    linkResult,
    semanticText: semanticParts.join("").replaceAll(DEFANGED_MARKER, ""),
  };
}

export function inspectMessageLinks(input) {
  return inspectMessageContext(input).linkResult;
}

export function inspectUrlInput(input) {
  const emptySummary = { inspected: 0, flagged: 0, limited: false };
  if (typeof input !== "string") {
    return { status: "invalid_type", summary: emptySummary, checks: [] };
  }
  if (codePointLengthExceeds(input, MAX_URL_CODE_POINTS)) {
    return {
      status: "too_long",
      summary: { inspected: 0, flagged: 0, limited: true },
      checks: [],
    };
  }
  if (UNSUPPORTED_CONTROL.test(input) || hasUnpairedSurrogate(input)) {
    return { status: "malformed", summary: emptySummary, checks: [] };
  }

  const candidate = input.trim();
  if (candidate === "") {
    return { status: "empty", summary: emptySummary, checks: [] };
  }
  if (UNICODE_WHITESPACE.test(candidate)) {
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
      limited: result.limited,
    },
    checks: uniqueChecks(result.observations),
  };
}
