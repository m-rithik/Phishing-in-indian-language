# Fisher Phase 1 Annotation Interface Guide

## Overview

Blind annotation of defanged messages (phishing vs. benign) by 3 independent human reviewers.
This document describes the interface, labeling instructions, disagreement resolution, and quality gates.

---

## 1. Annotation Interface Design

### Interface Specification (Web-based)

```
╔════════════════════════════════════════════════════════════╗
║ FISHER ANNOTATION INTERFACE v0.1                           ║
║ Annotator: [Blind ID: ANN-001] | Batch: [001] | 30/240   ║
╚════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────┐
│ ITEM ID: ITM-00123                                          │
│ LANGUAGE: Hindi (Devanagari + Romanized)                   │
│ DEFANGED: ✓ (no URLs, emails, phone visible)              │
│ ROMANIZED_INDIC: ✓ Contains Roman spelling of Indic text  │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ MESSAGE TEXT (defanged)                                       │
│                                                               │
│ "आपके बैंक खाता को verify करने के लिए तुरंत [URL] पर       │
│  क्लिक करें। OTP भेजें। आपका खाता suspend हो सकता है।"    │
│                                                               │
└──────────────────────────────────────────────────────────────┘

ANNOTATION TASK:
═══════════════════════════════════════════════════════════════

Is this message PHISHING, BENIGN, or UNCLEAR?

[Radio buttons]
  (○) PHISHING
      └─ Attempts to steal credentials, money, or access
      └─ Uses urgency, impersonation, threats
      └─ Asks for OTP, password, personal data
  
  (○) BENIGN
      └─ Legitimate message (social, informational, promotional)
      └─ No credential request or unusual urgency
  
  (○) UNCLEAR
      └─ Cannot decide without additional context
      └─ Message is ambiguous, fragmented, or mixed-language

CONFIDENCE (if not UNCLEAR):
─────────────────────────────────────────────────────────────
  [Slider] 0% ━━━━●━━━━ 100%
           Uncertain     Very certain

NOTES (optional):
─────────────────────────────────────────────────────────────
  [Text field, max 200 chars]
  (e.g., "Looks like a bank impersonation" or "Message is from friend")

═══════════════════════════════════════════════════════════════
[Previous] [Submit] [Skip]

Progress: 12/30 items labeled | 18 remaining
Est. time: ~15 mins | Elapsed: 8:42
═══════════════════════════════════════════════════════════════
```

### Key Design Features

1. **Blind randomization**
   - No sequence number, batch identity, or source leakage
   - Random item ordering within batch
   - Annotator ID is obfuscated (ANN-001, not researcher name)

2. **Defang verification**
   - Visual checkmark confirms no URLs, emails, phone numbers
   - If defang failed, flag it → remove from pilot (do not label)

3. **Language/script indicator**
   - Shows language and whether Romanized-Indic patterns are present
   - Helps reviewer contextualize the message

4. **Confidence slider**
   - 0–100% scale; helps measure annotator certainty
   - Not required for UNCLEAR responses

5. **Notes field**
   - Optional; helps explain disagreements during adjudication
   - Not used for automatic majority voting (human review only)

---

## 2. Labeling Instructions

### PHISHING Label
A message is PHISHING if it:

**Criterion 1: Requests sensitive information**
- OTP, password, CVV, KYC, account details
- Even if phrased as "verification" or "confirmation"

**OR Criterion 2: Requests action with threat/urgency AND impersonation**
- Action: click, open link, call, send, update
- Threat/urgency: "immediately", "suspend", "block", "expire", "जल्दी", "तुरंत"
- Impersonation: claims to be bank, government, police, delivery, support

**OR Criterion 3: Financial request with deception**
- Asks for payment, transfer, gift card, loan
- Falsely claims you won money, have refund due, owe fine
- Uses urgency (time-limited offer, exclusive deal)

**Examples (all PHISHING)**:
```
[Hindi] "आपका बैंक खाता suspend होगा। तुरंत सत्यापित करें।
https://[defanged] पर क्लिक करें।"
→ PHISHING: credential request + urgency + impersonation

[Tamil] "பரிசு வென்றீர்! ரூ 50,000 பெற உங்கள் அட்டை விவரங்களை கொடுங்கள்"
→ PHISHING: false prize claim + financial request

[Romanized] "send ur otp on whatsapp 9999999999 to confirm ur amazon account"
→ PHISHING: direct OTP request + impersonation
```

### BENIGN Label
A message is BENIGN if it:

**Is legitimate communication**: social, informational, promotional, work-related
**Does NOT request**: credentials, money, or private personal information
**Does NOT use**: deceptive impersonation or false threats

**Examples (all BENIGN)**:
```
[Hindi] "मेरा नया वीडियो देखो। यहाँ रिंक है: https://[defanged]"
→ BENIGN: friend sharing content, no request

[Tamil] "நாளை சந்திப்பு 2 மணிக்கு அலுவலகத்தில்"
→ BENIGN: meeting reminder, no request

[English] "Your Amazon order has shipped. Track it at https://[defanged]"
→ BENIGN: order confirmation (if actually from legit channel)
```

### UNCLEAR Label
Use when:
- **Fragment**: Only 1–2 words, context missing ("verify account" alone)
- **Ambiguous language**: Could be joke, code, or corrupted text
- **Mixed signals**: Legitimate-looking but with subtle red flags you can't explain
- **Truly uncertain**: You can't decide even after 30 seconds

---

## 3. Annotation Workflow

### Session Setup
1. Annotator logs in with blind ID (ANN-001, ANN-002, ANN-003)
2. System assigns 30 random items from pilot (stratified by language)
3. Items are in random order; no metadata visible
4. Annotator is given 45 min. session time (soft limit; can extend)

### Per-Item Workflow
1. Read message (defanged text)
2. Choose label: PHISHING / BENIGN / UNCLEAR
3. If not UNCLEAR: provide confidence (0–100%)
4. Optionally add notes
5. Click [Submit]
6. Next item appears or session ends

### Flagging Issues
If annotator encounters:
- **Incomplete defanging** (visible phone/email): Click [Flag] → item removed from pilot
- **Duplicate** (seen before): Note in [Notes]; label normally; flagged in analysis
- **Multiple languages** (code-switched): Label the apparent intent; note language mix
- **Unreadable** (corrupted text): Mark UNCLEAR; note in system log

---

## 4. Disagreement Resolution (Adjudication)

### Agreement Calculation
For each item, count label votes (3 annotators):
- **Perfect agreement**: 3–0 for one label → Accept
- **2–1 split**: Two annotators agree → Adjudicate (tie-break by expert)
- **3-way disagreement**: Each label has 1 vote → Expert review

### Tie-Breaking Process

1. **2–1 Split (e.g., 2 PHISHING, 1 BENIGN)**
   - Expert (senior researcher, blinded to identities) reviews notes
   - If notes explain disagreement: accept expert decision
   - If no clear signal: mark as "AMBIGUOUS" and exclude from final model training

2. **3-Way Split (e.g., 1 PHISHING, 1 BENIGN, 1 UNCLEAR)**
   - Treat UNCLEAR as "no signal"; expert breaks tie between PHISHING/BENIGN
   - If expert still uncertain: exclude from training (use for calibration only)

### Quality Gates
- **Required agreement rate**: ≥80% (240 items must have agreement on ≥192 items)
- **If <80%**: Stop; flag data quality issue; do not proceed to model training

### Example Adjudication Log

```
ITM-00042
─────────
Annotators: ANN-001 → PHISHING (conf=85%)
            ANN-002 → PHISHING (conf=90%)
            ANN-003 → BENIGN   (conf=60%)

Decision: 2-1 split (PHISHING wins)
Expert review: Notes mention "OTP request" + "urgency language"
  → Expert confirms PHISHING label
Final label: PHISHING (with confidence=low due to disagreement)

```

---

## 5. Annotator Training

### Pre-Annotation Training Session (30 min)
- Watch video walkthrough of interface
- Label 5 practice items (not from actual pilot)
- Discuss ambiguous cases (e.g., UNCLEAR vs. BENIGN boundary)
- Q&A and clarification

### Training Examples (5 practice items)

| Item | Text | Expected | Explanation |
|------|------|----------|-------------|
| Ex-1 | "OTP भेजें" | PHISHING | Direct OTP request |
| Ex-2 | "मीटिंग कल 2 बजे" | BENIGN | Meeting reminder, no request |
| Ex-3 | "आपका खाता verify करें" | UNCLEAR (→ PHISHING) | Alone, ambiguous; but "verify account" is phishing signal |
| Ex-4 | "नया कार्यक्रम लॉन्च हुआ" | BENIGN | Announcement, no request |
| Ex-5 | "एक्सक्लूसिव ऑफर: अभी खरीदें" | BENIGN (→ PHISHING?) | Depends on whether it asks for payment or personal info; if just ad link, BENIGN |

---

## 6. Data Collection & Storage

### Per-Annotator File
```
annotations_ANN-001.jsonl
─────────────────────────
{"item_id": "ITM-00042", "label": "phishing", "confidence": 85, "notes": "OTP + urgency"}
{"item_id": "ITM-00001", "label": "benign", "confidence": 92, "notes": "Greeting from friend"}
...
```

### Metadata
- Annotator ID (blind, e.g., ANN-001)
- Batch ID (e.g., BATCH-001)
- Timestamp (for auditing session length)
- Confidence score (0–100, omit if UNCLEAR)

### Privacy & Safety
- No annotator personal info in files
- Files stored on encrypted external drive (not cloud)
- Session logs destroyed after annotation agreement validation
- Annotators do not have access to each other's labels until after submission

---

## 7. Timeline & Logistics

| Task | Duration | Participant |
|------|----------|-------------|
| Train annotators | 30 min | 3 annotators + expert |
| Annotate items | 2 hrs | 3 annotators (in parallel) |
| Adjudicate disagreements | 1 hr | 1 expert reviewer |
| Validate & finalize labels | 30 min | Researcher |

**Total**: ~4–5 hours over 1–2 days

---

## 8. Quality Assurance Checklist

Before finalizing annotation data:

- [ ] Agreement rate ≥80% (at least 192/240 items)
- [ ] No item left with 3-way disagreement (all tie-broken)
- [ ] Defang validation: no leakage found
- [ ] Duplicate check: <5% of items are duplicate templates
- [ ] Language distribution: 4 strata × 2 labels × 30 items ≈ balanced
- [ ] No bias detected: phishing rate is 30–70% (not heavily skewed)
- [ ] Annotator feedback: no reports of confusing interface or instructions

---

## References

- PILOT_V01.md: Pilot schema (label definitions, allocation)
- ANNOTATION_GUIDE.md: Domain-specific guidance (phishing patterns)
- RECRUITMENT_PROTOCOL.md: Consent and donor management
