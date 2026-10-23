# Fisher Phase 1 Pilot Readiness Scorecard

## Status: BLOCKED

All gates below must be marked **✅ PASS** before recruitment can begin.

---

## GOVERNANCE GATES

### ✅ / ❌ Ethics Board Approval
- [ ] Formal IRB/REC submission completed
- [ ] Approval letter received (include IRB number)
- [ ] Protocol version matches deployed consent form
- **Owner**: Researcher + Institution
- **Timeline**: 4–6 weeks after submission
- **Current Status**: **BLOCKED** (not yet submitted)

### ✅ / ❌ Consent Form Finalized
- [ ] Consent document drafted and reviewed by ethics board
- [ ] Consent covers all data uses (training, evaluation, publication)
- [ ] Withdrawal process clearly specified
- [ ] Withdrawal deadline = start of model training (not ambiguous)
- [ ] Consent available in English and target languages (optional)
- **Owner**: Researcher + Ethics board
- **Timeline**: Part of ethics approval
- **Current Status**: **BLOCKED** (RECRUITMENT_PROTOCOL.md drafted; needs ethics review)

### ✅ / ❌ Data Processing Agreement
- [ ] Defined who has access to what data
- [ ] Researcher is custodian; donor/IRB have oversight
- [ ] External vault (if cloud-based) has signed DPA
- [ ] Encryption standards specified (AES-256 minimum)
- [ ] Breach notification plan documented
- **Owner**: Researcher + Legal/Compliance
- **Timeline**: 1–2 weeks
- **Current Status**: **BLOCKED** (template exists; not yet signed)

### ✅ / ❌ Security Audit
- [ ] Code review: defang script checked for leakage
- [ ] Encryption audit: vault setup verified
- [ ] Access control: only researcher can read/write defanged data
- [ ] Threat model reviewed: THREAT_MODEL.md confirmed up-to-date
- [ ] Incident response plan drafted
- **Owner**: Security officer or external auditor
- **Timeline**: 1 week
- **Current Status**: **BLOCKED** (no security audit assigned)

---

## TECHNICAL GATES

### ✅ / ❌ Pilot Validator Ready
- [ ] `fisher_pilot validate --mode draft` runs on example JSONL
- [ ] `fisher_pilot validate --mode ready` enforces 240-item allocation
- [ ] Schema validates consent_reference, privacy_review, artifact_review
- [ ] Deterministic three-fold split working
- [ ] All unit tests pass (180+ tests)
- **Owner**: Researcher
- **Timeline**: Complete
- **Current Status**: **✅ PASS** (all tests passing)

### ✅ / ❌ Defang Script Audited
- [ ] Script correctly identifies URLs, emails, IPs, UPI, phones, payment handles
- [ ] All patterns covered (regex + manual verification)
- [ ] Defanging is lossy (cannot reverse-engineer original)
- [ ] Script handles edge cases (spaced URLs, defanged-in-input, etc.)
- [ ] Test coverage ≥95%
- **Owner**: Researcher
- **Timeline**: 1 week (final pass)
- **Current Status**: **🟡 PARTIAL** (fisher_baselines/data.py has defang, but not standalone tested)

### ✅ / ❌ Annotation Interface Deployed
- [ ] Web form created and tested
- [ ] Blind randomization working (items in random order, no metadata)
- [ ] Annotator IDs obfuscated (ANN-001, not names)
- [ ] Session logging in place (for quality audit)
- [ ] Interface tested with 3 annotators (usability check)
- **Owner**: Researcher / Web developer
- **Timeline**: 2 weeks
- **Current Status**: **BLOCKED** (ANNOTATION_INTERFACE_GUIDE.md drafted; no code yet)

---

## RECRUITMENT GATES

### ✅ / ❌ Recruitment Materials Approved
- [ ] Recruitment email templates approved by ethics board
- [ ] Social media posts (Twitter, LinkedIn) approved
- [ ] GitHub issue approved (if recruiting publicly)
- [ ] All materials mention ethics board contact info
- **Owner**: Ethics board
- **Timeline**: 1 week (part of approval)
- **Current Status**: **BLOCKED** (materials drafted; awaiting ethics review)

### ✅ / ❌ Recruitment Channels Identified
- [ ] Primary contacts (direct outreach) listed: ≥20 candidate donors
- [ ] Community channels selected (Reddit, GitHub, Twitter, LinkedIn)
- [ ] No cold calls; all recruitment is opt-in or through known contacts
- [ ] Recruiter training: how to present the study (neutral, no coercion)
- **Owner**: Researcher + community liaisons
- **Timeline**: 1 week
- **Current Status**: **🟡 PARTIAL** (RECRUITMENT_PROTOCOL.md defines channels; contacts not yet identified)

### ✅ / ❌ Consent Tracking System Ready
- [ ] Consent ledger template created (CSV or database)
- [ ] Ledger stores: submission_id, consent_date, language_stratum, label
- [ ] Withdrawal ledger template: withdrawal_id, item_date, withdrawal_reason
- [ ] Access control: only researcher can read
- [ ] Ledgers stored in secure vault (not Git, not shared)
- **Owner**: Researcher
- **Timeline**: 1 week
- **Current Status**: **BLOCKED** (templates drafted; not yet deployed)

---

## DATA QUALITY GATES

### ✅ / ❌ Duplicate Detection Plan
- [ ] Strategy: template-hashing (ignore numbers, routes, format)
- [ ] Baseline duplicates from public datasets identified (Dravidian spam, etc.)
- [ ] Decision rule: ≤3 duplicates per donor acceptable; >3 = flag batch
- [ ] Mechanism: script implemented and tested
- **Owner**: Researcher
- **Timeline**: 1 week
- **Current Status**: **🟡 PARTIAL** (fisher_baselines/data.py has template grouping; not yet tuned for duplicates)

### ✅ / ❌ Language Stratum Balance
- [ ] Target: 4 strata × 2 labels × 30 items = 240 total
- [ ] Allocation rule: equal distribution (60 items per stratum, 30 phishing + 30 benign)
- [ ] Monitoring: weekly check on recruitment progress
- [ ] Contingency: if one stratum lags, extend recruitment or accept minor imbalance
- **Owner**: Researcher
- **Timeline**: Ongoing during recruitment
- **Current Status**: **PENDING** (not yet recruiting)

### ✅ / ❌ Annotation Agreement Target
- [ ] Required: ≥80% pairwise agreement (≥192/240 items with agreement)
- [ ] If <80%: halt, flag data quality issue
- [ ] Adjudication plan: 2–1 splits resolved by expert; 3-way excluded
- [ ] Quality audit: check for annotator bias (e.g., ANN-001 always says PHISHING)
- **Owner**: Expert reviewer
- **Timeline**: After annotation
- **Current Status**: **PENDING** (templates ready; process not yet executed)

---

## PUBLICATION GATES

### ✅ / ❌ Publication Boundaries Clear
- [ ] Pilot is data-readiness validation; NOT a phishing evaluation
- [ ] Results paper: "Feasibility and annotation of phishing signals in Indic messages"
- [ ] No claims: accuracy, low false positive rate, deployment readiness
- [ ] Acknowledgment: authentic donor contributions (with consent)
- **Owner**: Researcher + Ethics board
- **Timeline**: Finalize before releasing any results
- **Current Status**: **BLOCKED** (PAPER_1_PREREGISTRATION.md drafted; not yet finalized)

### ✅ / ❌ Donor Privacy in Publication
- [ ] No donor names, identities, or geographic info published
- [ ] Sample quotes from defanged messages allowed (no PII visible)
- [ ] Anonymization verified by independent reviewer (not researcher)
- [ ] Donor consent to include in appendix (optional)
- **Owner**: Researcher + Anonymization reviewer
- **Timeline**: Before publication
- **Current Status**: **PENDING** (guidelines drafted)

---

## SCORING SUMMARY

| Category | Gates | Passing | Status |
|----------|-------|---------|--------|
| **Governance** | 4 | 0 | 🔴 BLOCKED |
| **Technical** | 4 | 1 | 🟡 PARTIAL |
| **Recruitment** | 3 | 0 | 🔴 BLOCKED |
| **Data Quality** | 3 | 0 | 🔴 BLOCKED |
| **Publication** | 2 | 0 | 🔴 BLOCKED |
| **TOTAL** | 16 | 1 | 🔴 BLOCKED |

---

## Action Items (Priority Order)

### Phase 0: Prepare for Approval
1. **Finalize consent form** (1 week)
   - Incorporate ethics board feedback
   - Prepare translations (Hindi, Tamil, Telugu)
   
2. **Submit to ethics board** (1 week)
   - Full submission package (protocol, consent, recruitment materials, data security plan)
   - Expect 4–6 weeks for approval

3. **Set up recruitment channels** (2 weeks, in parallel)
   - Identify 20+ primary contacts
   - Draft recruitment emails/social posts (awaiting ethics approval to send)

4. **Deploy annotation interface** (2 weeks, in parallel)
   - Code web form
   - Test with 3 pilot annotators
   - Document usability feedback

### Phase 1: Post-Approval
5. **Finalize defang & quality scripts** (1 week)
   - Complete code review
   - Run defang on synthetic test cases
   
6. **Recruit donors** (Weeks 1–4 after approval)
   - Send outreach
   - Collect consents
   - Receive submissions

7. **Defang & validate** (Week 5)
   - Process all submissions
   - Remove duplicates, failures
   - Finalize pilot JSONL

8. **Annotate** (Week 6)
   - 3 annotators label all 240 items
   - Resolve disagreements
   - Validate agreement ≥80%

### Phase 2: Publication
9. **Analyze results** (Week 7)
   - Compute agreement statistics
   - Measure Romanized-Indic coverage
   - Identify lessons learned

10. **Draft feasibility paper** (Weeks 8–10)
    - Describe pilot design, outcomes, limitations
    - Include methodological insights for phishing research in Indic languages

---

## Sign-Off

**Researcher**: ___________________ Date: __________

**Ethics Board Chair**: ___________________ Date: __________

**Donor Privacy Advocate** (if applicable): ___________________ Date: __________

---

## Notes

- This scorecard is a **living document**; update weekly during recruitment
- Each gate's **owner** is responsible for tracking and reporting progress
- **BLOCKED status** prevents advancement to next phase
- **PARTIAL status** requires mitigation plan before proceeding
- **✅ PASS** means gate is satisfied; proceed with confidence
