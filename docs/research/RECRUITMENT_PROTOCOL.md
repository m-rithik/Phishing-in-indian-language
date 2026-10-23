# Fisher Phase 1 Recruitment Protocol

## Status

**STAGE**: Phase 1 feasibility pilot (240 messages)
**AUTHORIZATION**: BLOCKED — Requires ethics board approval and governance sign-off
**EFFECTIVE DATE**: Pending

---

## 1. Recruitment Strategy

### Target Population
- **Primary**: Hindi, Tamil, Telugu users (India-based or diaspora with active messaging patterns)
- **Age**: 18+ years
- **Language proficiency**: Comfortable with Indic scripts or Latin-character Romanization
- **Messaging frequency**: ≥1 message per day in target language

### Recruitment Channels
1. **Direct messaging** (email, WhatsApp, Slack)
   - To known contacts from university, workplace, language communities
   - Personal introduction by researcher
   
2. **Community networks** (opt-in, no cold calls)
   - GitHub issues in Fisher repository (public)
   - Twitter/X (language-community hashtags)
   - LinkedIn posts (research interest groups)
   - Reddit (r/IndianLanguages, r/hindi, etc.)

3. **Incentives** (optional, approved separately)
   - No payment (preserve consent authenticity)
   - Acknowledgment in paper appendix (opt-in)
   - Access to phishing-detection tool after study

### Exclusion Criteria
- **Cannot participate**:
  - Users with prior relationship to researchers (conflict of interest)
  - Minors (<18 years)
  - Users unable to provide informed consent
  - Professional message senders (e.g., customer service, marketing)

---

## 2. Informed Consent Process

### Consent Document Requirements
The consent form must clearly state:

1. **Purpose**
   - Study: Phishing detection in Indic-language messages
   - Use: Train and evaluate machine learning models
   - Scope: Fisher feasibility pilot, 240 messages, 2–3 weeks

2. **Data Collection**
   - **What**: Up to 30 messages (any length) you submit via defanged form
   - **Defanging**: Researcher removes phone numbers, URLs, account IDs, payment info before processing
   - **Defanged output**: Stored in JSONL file with SHA-256 hash of text (no original bytes)

3. **Data Retention**
   - **Original message**: Destroyed immediately after defanging (zero durable retention)
   - **Defanged text**: Retained for 6 months for model training; destroyed after publication
   - **No backups**: No automatic cloud backups; manual encrypted external-drive storage only
   - **No sharing**: Data stays in researcher's external vault (not in Git, not in lab server)

4. **Risks**
   - **Privacy risk**: Although messages are defanged, skilled adversaries could potentially reverse content from linguistic patterns
   - **Re-identification risk**: If defanging is incomplete, personal information could be visible
   - **No guarantee of anonymity**: Defanging is a best-effort process; perfect privacy cannot be assured

5. **Benefits**
   - Direct: None. Participation does not improve your personal security.
   - Societal: Advance phishing-detection research for Indic-language users.

6. **Withdrawal**
   - **Right to withdraw**: You can withdraw consent at any time until data is anonymized (start of model training)
   - **Withdrawal process**: Email researcher with withdrawal request; all your defanged messages are deleted within 48 hours
   - **No penalty**: Withdrawal incurs no penalty; you may continue using Fisher public tool

7. **Contact Information**
   - **Researcher**: [name, email, phone]
   - **Ethics board**: [institution, email, phone]
   - **Concerns**: Contact ethics board directly (researcher is not the sole gate)

### Consent Form Template

```
FISHER PHISHING-DETECTION PILOT — INFORMED CONSENT

Study Title: Phishing Detection in Hindi, Tamil, and Telugu Messages (Fisher v0.1)
Researcher: [Name] ([Email])
Institution: [University/Organization]
Ethics ID: [IRB Approval Number]

You are being invited to participate in a research study. Please read this
carefully. Your participation is entirely voluntary.

STUDY PURPOSE
This research evaluates machine-learning methods for detecting phishing and
scam messages in Hindi, Tamil, and Telugu. Findings will inform both academic
research and public tools.

WHAT YOU WILL DO
1. You will submit up to 30 personal messages (SMS, WhatsApp, email, etc.)
2. Messages can be in Hindi, Tamil, Telugu, or English-mixed
3. Submission takes ~10–15 minutes via a web form
4. You will receive no further contact unless you withdraw

DATA HANDLING
- Your messages will be automatically processed to remove sensitive data
  (phone numbers, URLs, account numbers, payment info)
- Defanged messages are stored only on an encrypted external drive
- Original messages are permanently deleted after defanging
- Defanged data will be retained for 6 months, then deleted after publication

YOUR RIGHTS
- You can withdraw at any time before data anonymization (start of training)
- Withdrawal is free; no explanation needed
- Your withdrawn messages will be deleted within 48 hours
- You can request to see what your defanged messages look like

RISKS & BENEFITS
Risks: Defanging is best-effort; skilled adversaries could potentially infer
content from linguistic patterns. We cannot guarantee perfect anonymity.

Benefits: No direct benefit to you. Societal benefit: advance phishing detection
for Indic-language users.

CONSENT
I have read and understood this information. I agree to participate:
  [  ] I agree (printed name) _________________ Date __________
  [  ] I do NOT agree

Contact Information:
- Researcher: [Email] [Phone]
- Ethics Board: [Email] [Phone]
```

### Consent Tracking
- **Consent vault**: Separate from message vault (external, access-restricted)
- **Tracking**: Mapping of consent IDs to donor identifiers (names, emails) stored in secure vault
- **Withdrawal ledger**: Append-only log of withdrawal requests with timestamp and action taken

---

## 3. Submission Process

### Pre-Submission (Researcher Responsibility)
1. Email consent form to prospective donor
2. Donor reads, signs, and returns via secure email or DocuSign
3. Researcher confirms signature authenticity
4. Researcher issues unique submission ID (random, no PII embedded)

### Submission Interface
A simple web form (no authentication required; single-use submission link):

```
FISHER MESSAGE SUBMISSION

Submission ID: [auto-generated unique code]
Language: [dropdown: Hindi / Tamil / Telugu / English-Indic code-mixed]

Message Input:
[Text area, up to 30 messages, one per line]

Batch ID: [auto-filled from submission ID]
Source ID: [auto-filled from consent mapping]

[Submit Button]

Privacy Notice:
- This form does NOT store your submission
- Submission is processed locally and defanged immediately
- You will NOT receive a confirmation email (no server logs of your action)
- If you do not receive the defanged report within 10 minutes, resubmit
```

### Post-Submission (Researcher Action)
1. **Batch processing**:
   - Receive submission on secure email or local file drop
   - Run defang script: extract URLs, emails, IPs, UPI, phone, payment handles
   - Replace with placeholders: `[URL]`, `[EMAIL]`, `[PHONE]`, etc.
   - Compute SHA-256 hash of defanged text (final artifact)
   - Destroy original message bytes

2. **Artifact generation**:
   - Write defanged text + metadata to `items.jsonl` (source_id, batch_id, language, hash)
   - Confirm no PII leakage before import

3. **Notification** (optional):
   - Respond to donor with defanged version of their own messages (for transparency)
   - Donor can optionally request further defanging if they spot sensitive data

---

## 4. Quality Checks

### For Each Donor Batch
- [ ] Consent form signed and dated
- [ ] Consent mapping entry created (consent_id → donor contact info)
- [ ] Submission date recorded
- [ ] Language stratum matches consent request
- [ ] Messages successfully defanged (no URLs, emails, IPs, phone numbers visible)
- [ ] Defanged messages imported to `items.jsonl`
- [ ] Original message bytes deleted from submission folder
- [ ] Submission folder purged and securely wiped
- [ ] Donor contacted (if consent includes notification preference)

### Fraud Checks
- **Duplicate detection**: Are messages copied from public datasets or previous donors?
  - Use template-grouping algorithm (ignore numbers, routes, format)
  - Flag if >3 exact template matches to public datasets
- **Bot/automated submission**: Are messages obviously machine-generated?
  - Run basic language ID (not phishing-heavy, but unnatural syntax patterns)
  - Flag if probability of human author < 0.7
- **Tainted consent**: Did donor understand they were giving consent?
  - Verify consent form was read (timestamps on form, not instant signing)
  - Monitor for pattern of submissions from single person (prevent proxy donation)

---

## 5. Incentive Policy (if approved)

**Financial incentive NOT recommended** (may bias toward false/fabricated consent)

**Acceptable alternatives**:
- [ ] None (purely voluntary)
- [ ] Acknowledge in appendix ("Thanks to N donors...")
- [ ] Early access to Fisher v1.0 tool
- [ ] Certificate of participation (for educational institutions)

---

## 6. Timeline

| Phase | Timeline | Owner |
|-------|----------|-------|
| Ethics board submission | Week 1–2 | Researcher |
| Consent template finalized | Week 3 | Ethics board + Researcher |
| Recruitment begins | Week 4 | Researcher + Community leads |
| Submission window | Weeks 5–8 | Donors + Researcher |
| Defanging + validation | Week 9 | Researcher |
| Pilot data ready | Week 10 | Validator + Researcher |

---

## 7. Governance Gates

Before recruitment can begin:

- [ ] **Ethics board approval** (IRB/REI clearance)
- [ ] **Data processing agreement** (if external vault is on cloud)
- [ ] **Security audit** (defang script, encryption, access control)
- [ ] **Recruitment materials approved** (consent form, web form, emails)
- [ ] **Donor consent ledger template** (approved format, access control)

**CURRENT STATUS**: All gates BLOCKED (no approvals yet)

---

## References

- PILOT_V01.md: Pilot schema and readiness validator
- CONSENT_ETHICS_PRIVACY.md: Broader consent/privacy framework
- CHANGE_DECISION_LOG.md: Governance decisions (Luna-ID system)
