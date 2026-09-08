export const MAX_INPUT_CHARS = 20_000;
export const CONFUSABLE_PROFILE_VERSION = "FISHER_GC_SENSITIVE_V1";

const DEFAULT_IGNORABLES =
  /[\p{Cf}\u034f\u115f\u1160\u17b4\u17b5\u180b-\u180f\u3164\ufe00-\ufe0f\uffa0\ufff0-\ufff8\u{1bca0}-\u{1bca3}\u{1d173}-\u{1d17a}\u{e0000}-\u{e0fff}]/gu;
const HAS_DEFAULT_IGNORABLE =
  /[\p{Cf}\u034f\u115f\u1160\u17b4\u17b5\u180b-\u180f\u3164\ufe00-\ufe0f\uffa0\ufff0-\ufff8\u{1bca0}-\u{1bca3}\u{1d173}-\u{1d17a}\u{e0000}-\u{e0fff}]/u;
const DOT_VARIANTS = /[\u3002\uff0e\uff61]/gu;
const OBFUSCATED_DOTS = /\[\s*\.\s*\]|\(\s*dot\s*\)/giu;
const SPACED_DOTS = /\s*\.\s*/gu;
const WORD_DOTS = /\s+dot\s+/giu;
const DISALLOWED_CONTROLS = /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f]/u;
const CONFUSABLE_REASON =
  "Contains character lookalikes resembling a configured sensitive term.";
const CONFUSABLE_TOKEN = /[\p{L}\p{M}\p{N}]+/gu;
const CONFUSABLE_SUBSTITUTIONS = new Map([
  ["α", "a"],
  ["а", "a"],
  ["с", "c"],
  ["е", "e"],
  ["ι", "i"],
  ["і", "i"],
  ["ο", "o"],
  ["о", "o"],
  ["ρ", "p"],
  ["р", "p"],
  ["ѕ", "s"],
  ["ν", "v"],
  ["γ", "y"],
  ["у", "y"],
]);
const CONFUSABLE_SENSITIVE_TERMS = new Set([
  "otp",
  "pin",
  "password",
  "passcode",
  "cvv",
  "kyc",
]);

const SIGNALS = [
  {
    category: "credential",
    weight: 3,
    reason: "Mentions account verification or sensitive credentials.",
    pattern:
      /\b(?:otp|one[ -]?time password|pin|password|passcode|cvv|kyc|verify (?:your )?account)\b|ओटीपी|पासवर्ड|केवाईसी|ஓடிபி|கடவுச்சொல்|ஓடிபி|పాస్‌వర్డ్|కేవైసీ|ఓటీపీ/iu,
  },
  {
    category: "urgency",
    weight: 2,
    reason: "Uses urgency, expiry, suspension, or immediate-pressure language.",
    pattern:
      /\b(?:urgent|immediately|act now|today only|expires? today|suspend(?:ed|ion)?|block(?:ed|ing)?|jaldi|turant|abhi)\b|तुरंत|जल्दी|अभी|आज ही|बंद हो|உடனே|அவசரம்|இன்றே|முடக்க|వెంటనే|అత్యవసరం|ఈరోజే|నిలిపివేయ/iu,
  },
  {
    category: "action",
    weight: 2,
    reason: "Pushes the reader to click, open, call, send, share, or update.",
    pattern:
      /\b(?:click|open|visit|verify|update|confirm|call|send|share|download|tap|bhejo|karo)\b|क्लिक|खोलें|भेजें|साझा|अपडेट|அழுத்த|திறக்க|அனுப்ப|பகிர|புதுப்பிக்க|క్లిక్|తెరవ|పంప|పంచ|అప్‌డేట్/iu,
  },
  {
    category: "impersonation",
    weight: 2,
    reason: "Claims or implies authority from a bank, government, police, or delivery service.",
    pattern:
      /\b(?:bank|sbi|rbi|government|govt|police|income tax|customs?|courier|delivery|support team|customer care)\b|बैंक|सरकार|पुलिस|आयकर|कूरियर|வங்கி|அரசு|காவல்|வருமான வரி|கூரியர்|బ్యాంక్|ప్రభుత్వం|పోలీస్|ఆదాయపు పన్ను|కొరియర్/iu,
  },
  {
    category: "money",
    weight: 2,
    reason: "Mentions payment, winnings, refunds, fines, loans, or financial rewards.",
    pattern:
      /₹|\b(?:payment|pay now|prize|lottery|reward|refund|cashback|fine|loan|rupees?|lakh)\b|रुपये|इनाम|जुर्माना|ऋण|பணம்|பரிசு|அபராதம்|கடன்|రూపాయలు|బహుమతి|జరిమానా|రుణం/iu,
  },
  {
    category: "link",
    weight: 3,
    reason: "Contains a web address or an obfuscated domain.",
    pattern:
      /\b(?:https?:\/\/|hxxps?:\/\/|www\.)[^\s]{1,2048}|\b(?:[a-z0-9][a-z0-9-]{0,62}\.){1,5}(?:com|in|org|net|xyz|top|site|online|link|info|click|example)\b/iu,
  },
];

const PROTECTIVE_ADVISORY =
  /\b(?:do not|don't|never)\s+(?:click|open|share|send|reveal|provide|tell|submit|enter|verify)|\b(?:bank|we)\s+will never ask|\botp\s+(?:share|send)\s+(?:mat|na)\b|ओटीपी.{0,24}(?:साझा न करें|मत भेजें)|(?:लिंक|कड़ी).{0,16}(?:न खोलें|क्लिक न करें)|ஓடிபி.{0,24}(?:பகிர வேண்டாம்|அனுப்ப வேண்டாம்)|இணைப்பை.{0,16}(?:திறக்க வேண்டாம்|அழுத்த வேண்டாம்)|ఓటీపీ.{0,24}(?:పంచుకోవద్దు|పంపవద్దు)|లింక్.{0,16}(?:తెరవద్దు|క్లిక్ చేయవద్దు)/iu;
const DIRECT_DISCLOSURE_REQUEST =
  /\b(?:send|share|reveal|provide|tell|submit|enter)\b(?:\s+(?:me|us|them|your|the)){0,2}\s+\b(?:otp|one[ -]?time password|pin|password|passcode|cvv)\b|\b(?:otp|one[ -]?time password|pin|password|passcode|cvv)\b(?:\s+(?:now|abhi|please)){0,2}\s+\b(?:send|share|reveal|provide|submit|enter|bhejo|batao)\b|(?:ओटीपी|पासवर्ड|पिन|सीवीवी)[^.!?;।！？]{0,16}(?:भेजें|भेजो|साझा|बताएं|बताओ|दर्ज करें)|(?:ஓடிபி|கடவுச்சொல்|பின்|சிவிவி)[^.!?;।！？]{0,16}(?:அனுப்ப|பகிர|சொல்ல|உள்ளிட)|(?:ఓటీపీ|పాస్‌వర్డ్|పిన్|సీవీవీ)[^.!?;।！？]{0,16}(?:పంప(?!వద్దు)|పంచ(?!ుకోవద్దు)|చెప్ప(?!వద్దు)|నమోదు)/giu;
const ACCOUNT_VERIFICATION_REQUEST =
  /\bverify (?:your )?account\b|(?:खाता|अकाउंट)[^.!?;।！？]{0,16}(?:सत्यापित करें|वेरीफाई करें)|கணக்கை[^.!?;।！？]{0,16}சரிபார்க்க|ఖాతాను[^.!?;।！？]{0,16}ధృవీకరించ/giu;
const NEGATION_BEFORE_REQUEST =
  /(?:\b(?:never|do not|don't|not|mat|na)\s*|(?:मत|न)\s*)$/iu;
const NEGATION_AFTER_REQUEST =
  /^\s*(?:mat|na|nahi|न करें|मत|வேண்டாம்|கூடாது|వద్దు|ద్దు|ుకోవద్దు|కూడదు|చేయవద్దు)/iu;

function normalizeInput(raw) {
  const removedFormat = HAS_DEFAULT_IGNORABLE.test(raw);
  const withoutOriginalIgnorables = raw.replace(DEFAULT_IGNORABLES, "");
  const compatibilityNormalized = withoutOriginalIgnorables.normalize("NFKC");
  const withoutIgnorables = compatibilityNormalized.replace(DEFAULT_IGNORABLES, "");
  return {
    text: withoutIgnorables
      .replace(DOT_VARIANTS, ".")
      .toLocaleLowerCase("en")
      .replace(/\s+/gu, " ")
      .trim(),
    removedFormat,
  };
}

function domainMatchingView(text) {
  return text
    .replace(OBFUSCATED_DOTS, ".")
    .replace(WORD_DOTS, ".")
    .replace(SPACED_DOTS, ".");
}

function hasUnpairedSurrogate(text) {
  for (let index = 0; index < text.length; index += 1) {
    const codeUnit = text.charCodeAt(index);
    if (codeUnit >= 0xd800 && codeUnit <= 0xdbff) {
      const next = text.charCodeAt(index + 1);
      if (!(next >= 0xdc00 && next <= 0xdfff)) {
        return true;
      }
      index += 1;
    } else if (codeUnit >= 0xdc00 && codeUnit <= 0xdfff) {
      return true;
    }
  }
  return false;
}

function exceedsCodePointLimit(text) {
  let count = 0;
  for (const _character of text) {
    count += 1;
    if (count > MAX_INPUT_CHARS) {
      return true;
    }
  }
  return false;
}

function requestIsLocallyNegated(text, start, end) {
  const before = text.slice(Math.max(0, start - 32), start);
  const after = text.slice(end, Math.min(text.length, end + 24));
  return NEGATION_BEFORE_REQUEST.test(before) || NEGATION_AFTER_REQUEST.test(after);
}

function hasNonNegatedMatch(text, pattern) {
  for (const match of text.matchAll(pattern)) {
    const start = match.index;
    if (!requestIsLocallyNegated(text, start, start + match[0].length)) {
      return true;
    }
  }
  return false;
}

function hasNonNegatedSensitiveRequest(text) {
  return (
    hasNonNegatedMatch(text, DIRECT_DISCLOSURE_REQUEST) ||
    hasNonNegatedMatch(text, ACCOUNT_VERIFICATION_REQUEST)
  );
}

function mapsToConfiguredSensitiveTerm(token) {
  let codePointCount = 0;
  let usedSubstitution = false;
  let skeleton = "";
  for (const character of token) {
    codePointCount += 1;
    if (codePointCount > 8) {
      return false;
    }
    const substitution = CONFUSABLE_SUBSTITUTIONS.get(character);
    if (substitution === undefined) {
      skeleton += character;
    } else {
      skeleton += substitution;
      usedSubstitution = true;
    }
  }
  return usedSubstitution && CONFUSABLE_SENSITIVE_TERMS.has(skeleton);
}

function hasConfiguredConfusableSensitiveTerm(text) {
  for (const match of text.matchAll(CONFUSABLE_TOKEN)) {
    if (mapsToConfiguredSensitiveTerm(match[0])) {
      return true;
    }
  }
  return false;
}

export function analyzeText(input) {
  if (typeof input !== "string") {
    return {
      risk: "cannot_analyze",
      reasons: ["No analyzable text was provided."],
    };
  }
  if (exceedsCodePointLimit(input)) {
    return {
      risk: "cannot_analyze",
      reasons: ["Input exceeds the 20,000-character analysis limit; nothing was analyzed."],
    };
  }
  if (DISALLOWED_CONTROLS.test(input) || hasUnpairedSurrogate(input)) {
    return {
      risk: "cannot_analyze",
      reasons: ["Input contains unsupported control or malformed Unicode characters."],
    };
  }

  const normalized = normalizeInput(input);
  if (normalized.text === "") {
    return {
      risk: "cannot_analyze",
      reasons: ["No analyzable text was provided."],
    };
  }

  const reasons = [];
  const categories = new Set();
  let score = 0;

  const matchingText = domainMatchingView(normalized.text);
  for (const signal of SIGNALS) {
    if (signal.pattern.test(matchingText)) {
      score += signal.weight;
      categories.add(signal.category);
      reasons.push(signal.reason);
    }
  }

  if (normalized.removedFormat) {
    score += 1;
    reasons.push("Contains invisible or formatting characters that can hide words.");
  }

  const hasConfusableSensitiveTerm = hasConfiguredConfusableSensitiveTerm(normalized.text);
  if (hasConfusableSensitiveTerm) {
    reasons.push(CONFUSABLE_REASON);
  }

  const hasSensitiveRequest = hasNonNegatedSensitiveRequest(normalized.text);
  if (PROTECTIVE_ADVISORY.test(normalized.text)) {
    reasons.push("Protective wording was detected; context may be a warning.");
  }

  if (reasons.length === 0) {
    reasons.push("No configured scam-signal combination was detected.");
  }

  const highRiskCombination =
    hasSensitiveRequest && (categories.has("link") || categories.has("urgency"));
  const risk = highRiskCombination
    ? "high"
    : hasConfusableSensitiveTerm || score >= 3
      ? "review"
      : "no_match";
  return { risk, reasons };
}
