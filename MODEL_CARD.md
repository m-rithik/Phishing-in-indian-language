# Fisher Model Card v0.6

## Model Details

### Model Description
**Fisher** is a **local, rule-based phishing-signal detector** for Hindi, Tamil, Telugu, and English messages. It is **not** a trained machine learning model.

- **Version**: 0.6.0
- **Type**: Transparent rule-based system (no ML)
- **Languages**: Hindi (Devanagari, Romanized), Tamil, Telugu, English-Indic code-mixed
- **Input**: Text messages (20K character max) or URLs (2K character max)
- **Output**: Risk classification (high, review, no_match, cannot_analyze)

### Model Architecture

**Engine Components** (browser_extension/):
1. **detector.mjs**: Message pattern rules (6 categories: credential, urgency, action, impersonation, money, defang)
2. **links.mjs**: URL parsing and structural inspection (credentials, HTTP, IP addresses, punycode, shorteners)
3. **analyzer.mjs**: Public API combining detector + link results

**Analysis Pipeline**:
```
Input Text
  ↓
Normalize (NFKC, remove format controls, lowercase, collapse whitespace)
  ↓
Detect Signal Patterns (6 categories, weighted)
  ↓
Negation Suppression (e.g., "never share OTP" → no high risk)
  ↓
Extract URLs (greedy longest-match, defang recognition)
  ↓
Inspect URLs (embedded credentials, IP hosts, shorteners, etc.)
  ↓
Composite Risk (message signals + link signals)
  ↓
Output Report (risk, reasons, checks, next steps)
```

### Model Rules (Sample)

**Credential Signals** (weight=3):
- Exact matches: "otp", "one-time password", "pin", "password", "cvv", "kyc", "verify account"
- Indic script: ओटीपी, पासवर्ड, கடவுச்சொல், ఓటీపీ
- Confusable lookalikes: α→a, а→a, с→c (e.g., "раѕѕωοrd" → detected)

**Urgency Signals** (weight=2):
- Exact: "urgent", "immediately", "act now", "expire", "suspend", "jaldi", "तुरंत"

**Impersonation Signals** (weight=2):
- Bank, government, police, customs, courier, delivery, support team

**Money Signals** (weight=2):
- Payment, prize, refund, fine, loan, winnings, rupees, ₹

**Action Signals** (weight=2):
- Click, open, visit, call, send, share, download, tap, भेजें

**Defang Recognition**:
- hxxps, [.], (dot), spaced domain (example [.] com)

**Protective Advisory** (suppresses high):
- "never share OTP", "don't click", "bank will not ask"

---

## Model Performance

### Training Data
**None.** Fisher v0.6 uses curated rules, not trained ML models.

### Auxiliary Baseline Results
(Development-only spam/ham evaluation on public Dravidian dataset; **not phishing**; **not Fisher validation**):

| Model | Spam F1 | Spam Precision | Spam Recall |
|-------|---------|----------------|------------|
| Character TF-IDF + Logistic Regression | 0.9078 | 0.9209 | 0.8950 |
| Word + Character TF-IDF + Linear SVM | 0.9181 | 0.9568 | 0.8824 |

**Important Caveats**:
- These are **spam/ham measurements**, not **phishing detection**
- Evaluated on **public corpus** (Dravidian dataset), not authentic Fisher phishing messages
- No authentic phishing data has been collected yet
- Models use **default decision thresholds**; no threshold tuning, calibration, or cost-weighting
- Results do not support **accuracy, false positive rate, campaign-disjoint, per-language**, or **deployment claims**

### Known Limitations

1. **No authentic evaluation**: Fisher has never been evaluated on real phishing messages in Hindi/Tamil/Telugu
2. **Rule-based only**: Transparent pattern matching; cannot learn from data
3. **Romanization ambiguity**: Cannot resolve "otp" → Hindi ओटीपी vs. English OTP
4. **No reputation data**: Cannot check domain legitimacy (links are never opened)
5. **Defang blindspots**: Malformed defang, unusual abbreviations, creative misspellings
6. **URL structural only**: No semantic understanding of destination content
7. **Single-interpretation**: Always uses top-1 transliteration candidate (multi-candidate aggregation deferred)
8. **Context-free**: Rules ignore preceding/following tokens
9. **False positives possible**: Legitimate bank warnings ("verify account") may trigger high risk
10. **No voice/conversation support**: Text messages only

### Known Misses

- Customs-fee messages ("package held at customs, pay a fee") and friend-in-need messages ("I am stuck, send money") are not detected.
- Promotional spam on UCI almost never reaches high (recall 0.005).
- Real bank notices and OTP warnings get review.

---

## Model Behavior

### Intended Use
- **Primary**: Help users pause and inspect suspicious messages before acting
- **Secondary**: Generate signals for downstream human review or classifier
- **NOT for**: Automated blocking, security appliance integration, deployment, SLA claims

### Out-of-Scope Use
- Real-time filtering (no API, no rate limits)
- Accuracy-dependent decision-making (rules are transparent heuristics, not trained)
- Non-Indic languages (not trained on Arabic, Russian, Mandarin, etc.)
- Audio, images, documents (text messages only)
- Spam detection as proxy for phishing (different signal distribution)

### Input/Output Examples

**Example 1: High Risk**
```
Input: "आपके बैंक खाता को verify करने के लिए तुरंत [URL] पर क्लिक करें। OTP भेजें।"

Output:
{
  "risk": "high",
  "reasons": [
    "Mentions account verification or sensitive credentials.",
    "Uses urgency, expiry, suspension, or immediate-pressure language.",
    "A web address was found and should be verified independently."
  ],
  "checks": [
    {"label": "Message rules", "detail": "credential + urgency → high"},
    {"label": "Web address present", "detail": "1 URL detected"},
    {"label": "Embedded destination", "detail": "URL structural findings"}
  ],
  "nextSteps": [
    "Do not use the link or provide credentials.",
    "Verify the request through an independently obtained official channel."
  ]
}
```

**Example 2: No Match**
```
Input: "मीटिंग कल 2 बजे ऑफिस में। ये रिंक भेजता हूं: [URL]"

Output:
{
  "risk": "no_match",
  "reasons": [
    "No configured finding was detected; this is not a safety result."
  ],
  "nextSteps": [
    "No configured finding was detected; this is not a safety result.",
    "Continue to verify unexpected requests through an independent channel."
  ]
}
```

---

## Data

### Training Data
No training data (rules are hand-coded).

### Evaluation Data
Planned: 240-message Fisher pilot (deidentified, defanged Hindi/Tamil/Telugu messages).
- Status: BLOCKED (awaiting ethics approval and donor recruitment)
- Expected: Q4 2026 (pending)

### Data Collection Process
See RECRUITMENT_PROTOCOL.md and PILOT_READINESS_SCORECARD.md

### Annotation
Blind annotation by 3 independent reviewers; phishing vs. benign labels.
- Status: PENDING (awaiting interface deployment and recruitment)

---

## Ethical Considerations

### Fairness & Bias
- **Romanization coverage**: Rules cover common Indic Romanization patterns (Hindi, Tamil, Telugu)
- **Language coverage**: Only 3 Indic languages + English; no Marathi, Gujarati, Bengali, etc.
- **Cultural context**: Rules are derived from observable phishing tactics, not linguistic analysis
- **Bias risk**: Rules may over-flag legitimate authority messages (banks, government), under-flag code-switched text

### Privacy
- **Permissions**: The only extension permission is contextMenus; right-click text is held in service-worker memory for about 30 seconds until the popup reads it, and selections can include text inside iframes
- **No network calls**: All analysis is local (extension runs offline)
- **No data retention**: Messages exist transiently in browser/popup memory
- **No telemetry**: No usage tracking, message logging, or analytics
- **Defanging**: Input URLs/emails are not stored in output reports

### Limitations on Use
- **Not for blocking**: Do not use as sole basis for automated message filtering
- **Not for deployment**: Do not integrate into messaging app without human review layer
- **Not for claims**: Do not claim "0.95 accuracy" or "1% false positive rate" without authentic evaluation

---

## Model Card History

| Version | Date | Changes |
|---------|------|---------|
| 0.5.0 | October 2026 | Initial model card (rule-based, no trained model) |
| 0.6.0 | October 2026 | Multi-candidate transliteration support, expanded detector rules, held-out evaluation (Fisher v0.6) |
| 1.0.0 | Planned | Trained phishing classifier (Fisher v1.0, post-pilot) |

---

## Contact & Citation

**Researcher**: [Name] ([Email])
**Repository**: https://github.com/m-rithik/Phishing-in-indian-language
**License**: No reuse license selected

**Suggested Citation**:
```bibtex
@software{fisher2026,
  title={Fisher: Local Phishing-Signal Detection for Indic Languages},
  author={[Name]},
  url={https://github.com/m-rithik/Phishing-in-indian-language},
  year={2026},
  note={v0.6.0, rule-based prototype}
}
```

---

## Disclaimer

**Fisher v0.6 is an unvalidated research prototype.**

- No phishing performance has been measured
- Rules are transparent heuristics, not trained on authentic data
- "No clear pattern match" is explicitly NOT a safety result
- Use at your own risk; verify unexpected requests independently

**This is not a guarantee of message safety or security.**
