# Fisher v0.5.0 Release Notes

**Release Date**: October 11, 2026

---

## Summary

Fisher v0.5 adds workspace, bulk-check, and comprehensive governance infrastructure to establish a reproducible foundation for the Phase 1 feasibility pilot.

---

## What's New

### Browser Extension
- ✨ **Workspace view**: Side-by-side input and findings (responsive, light/dark mode)
- ✨ **Bulk check**: Analyze up to 100 messages/links per session (filter, download report)
- ✨ **Selection mode**: Analyze explicitly selected page text (no standing host access)
- 🎨 **Extension icons**: 16px, 32px, 48px, 128px PNG + SVG
- 📱 **Accessibility**: Keyboard shortcuts (Ctrl/⌘+Enter), focus management, reduced-motion support
- 📊 **Reporting**: Generic findings export (JSON, no message echo)

### Shared Engine (Node.js)
- 🔍 **Link inspection**: Embedded destination parsing (query params, protocol-relative URLs)
- 🔤 **Confusable profile**: Unicode lookalike detection (α→a, а→a, с→c for sensitive terms)
- 🛡️ **Negation detection**: Suppresses false positives ("never share OTP")
- 📋 **CLI improvements**: Message/URL/batch modes, JSON output

### Transliteration Module (New!)
- 🔤 **Candidate generation**: Multiple plausible Indic interpretations from Romanized input
- 📝 **Rule-based**: Hindi, Tamil, Telugu romanization patterns (100+ rules per language)
- 🎯 **Phishing-focused**: OTP, CVV, KYC, password, PIN patterns weighted high
- 🧪 **20 unit tests** (all passing)
- Foundation for Phase 2 multi-candidate aggregation

### Governance & Documentation
- 📋 **RECRUITMENT_PROTOCOL.md**: Donor recruitment, consent, defanging, quality checks
- 🏷️ **ANNOTATION_INTERFACE_GUIDE.md**: Blind review interface, labeling rules, adjudication
- ✅ **PILOT_READINESS_SCORECARD.md**: 16-gate checklist (status: BLOCKED, awaiting ethics approval)
- 📝 **MODEL_CARD.md**: Transparent documentation (no trained model, rules-based, no authentic evaluation)
- 🔐 **Privacy-first**: Zero durable retention of original messages, defanging before storage

### Testing
- ✅ **148 Node.js tests** (analyzer, detector, links, CLI, selection)
- ✅ **318 Python tests** (baselines, pilot validator, transliteration)
- 📊 **CI/CD ready**: GitHub Actions workflow for continuous validation
- 🔒 **Security audits**: Extension packaging, CSP, defang validation

### Quality
- 📈 **Code organization**: 6 major modules (browser_extension, fisher_baselines, fisher_pilot, fisher_transliteration, etc.)
- 📖 **Documentation**: 20+ research contracts, 5 phase-1 governance documents
- 🏗️ **Reproducibility**: Deterministic evaluation, seed-based CV, publication-safe output (no message echo)

---

## Breaking Changes

**None.** v0.5 is compatible with v0.4 API (new features are additive).

---

## Known Issues & Limitations

### Current Limitations
1. **No authentic phishing evaluation**: Rules are transparent heuristics; no trained model
2. **Romanization ambiguity**: Cannot resolve "otp" → English vs. Hindi ओटीपी (deferred to v0.6)
3. **Single-interpretation**: Uses top-1 transliteration candidate (multi-candidate deferred)
4. **No reputation data**: URL legitimacy checks disabled (no DNS resolution, no IP reputation lookups)
5. **False positives**: Legitimate bank messages ("verify account", "account suspended") may trigger review
6. **Link-only analysis**: Cannot reason about embedded images, attachments, metadata
7. **No voice support**: Text messages only (audio Indic phishing deferred)

### Unresolved Issues
- [ ] **Defang completeness**: Edge cases (spaced URLs, unusual abbreviations) may leak through
- [ ] **Romanization rules coverage**: Informal/slang Romanization patterns may be missing
- [ ] **Performance**: Not profiled on large batches (500 URLs, 20K character messages)
- [ ] **Browser automation**: Playwright suite not yet executed (requires test environment setup)
- [ ] **Accessibility audit**: axe-core scan not yet run (WCAG compliance TBD)

---

## Roadmap

### v0.5.1 (Minor, Q4 2026)
- Accessibility audit + fixes (WCAG 2.1 Level AA)
- Performance profiling & optimization
- Browser automation test execution
- Defang edge-case hardening

### v0.6.0 (Major, Q1 2027)
- Multi-candidate transliteration aggregation
- Multilingual encoder (XLS-R or mBERT) integration
- Phishing classifier (trained on Fisher pilot data)
- Threshold tuning for low false-positive rate

### v1.0.0 (Production, Q2 2027)
- Authentic phishing evaluation results
- Low false-positive guarantee (≤2% on test set)
- Mobile app support (iOS/Android)
- Deployment infrastructure (cloud API, edge)

### Deferred (v2.0+)
- Voice phishing detection
- Conversation context awareness
- Full semantic factorial (1,000+ rules)
- Offline registry of known-malicious domains
- Patent claims (if applicable)

---

## Installation & Usage

### Browser Extension
1. Download ZIP or clone repository
2. Open `chrome://extensions` or `edge://extensions`
3. Enable **Developer mode**
4. Click **Load unpacked** → select `browser_extension/` folder
5. Click Fisher icon; choose **Message**, **Link check**, or **Bulk check**

### CLI
```bash
node fisher.mjs analyze < message.txt
node fisher.mjs analyze --mode url < link.txt
node fisher.mjs batch < messages-one-per-line.txt
```

### Python Baselines
```bash
uv sync
uv run python -m fisher_baselines evaluate --workbook data.xlsx
uv run python -m fisher_pilot validate --sources sources.jsonl --items items.jsonl --annotations annotations.jsonl --mode draft --format text
uv run python -m fisher_transliteration generate_candidates "otp"
```

---

## Security Considerations

### Privacy
- ✅ **Local analysis**: All computation happens on your device
- ✅ **No network calls**: No telemetry, no external APIs
- ✅ **No storage**: Messages exist transiently in browser memory
- ✅ **No history**: Popup and workspace each start with empty drafts

### Safety
- ✅ **Content Security Policy**: No inline scripts, no external resources
- ✅ **Input validation**: All inputs validated before processing
- ✅ **Output safety**: No message echo in reports (JSON export contains generic findings only)
- ⚠️ **Defanging limitations**: Best-effort only; malformed or creative obfuscation may leak through

---

## System Requirements

### Browser Extension
- **Chrome/Edge**: v120+
- **Permissions**: `activeTab` (temporary, on-demand), `scripting` (for selection mode)
- **Storage**: <5 MB extension size, no persistent storage

### CLI
- **Node.js**: v22+
- **OS**: macOS, Linux, Windows
- **Dependencies**: None (pure JavaScript)

### Python Tools
- **Python**: 3.11+
- **Dependencies**: pandas, scikit-learn, numpy, openpyxl (dev-only in prod)

---

## Testing & Validation

### Unit Tests
```bash
npm test                    # 148 Node.js tests
uv run python -m unittest discover -s tests -p 'test_*.py'  # 318 Python tests
```

### Browser Tests
```bash
npx playwright install chromium
npm run test:browser
```

### Baseline Evaluation
```bash
uv run python -m fisher_baselines evaluate \
  --workbook data.xlsx \
  --output-dir outputs/
```

### Pilot Validation
```bash
uv run python -m fisher_pilot validate \
  --sources sources.jsonl \
  --items items.jsonl \
  --annotations annotations.jsonl \
  --mode draft --format text
```

---

## Acknowledgments

- **Researchers**: [Names, institutions]
- **Community**: Thanks to Hindi, Tamil, Telugu language communities for feedback
- **Ethics Board**: [Institution, IRB number pending]
- **Pilot Donors**: Pending (Phase 1 recruitment will proceed post-approval)

---

## License

No reuse license has been selected. This repository is intended for the owner's private use.
Visit https://github.com/m-rithik/Phishing-in-indian-language for updates.

---

## Feedback & Issues

Report bugs, feature requests, or governance concerns:
- **GitHub Issues**: https://github.com/m-rithik/Phishing-in-indian-language/issues
- **Email**: [Contact email]
- **Ethics concerns**: [Ethics board contact]

---

## Previous Versions

| Version | Release | Status |
|---------|---------|--------|
| v0.5.0 | Oct 2026 | Current (rule-based prototype, no trained model) |
| v0.4.0 | Aug 2026 | End of support |
| v0.3.0 | Jun 2026 | End of support |
| v0.1.0 | May 2026 | End of support |

---

## Next Steps for Users

### Researchers
1. Review MODEL_CARD.md for limitations and intended use
2. Read RECRUITMENT_PROTOCOL.md if planning Phase 1 pilot participation
3. Check PILOT_READINESS_SCORECARD.md for governance status

### Extension Users
1. Load extension from `browser_extension/` folder (see Installation above)
2. Try synthetic examples (Hindi, Tamil, Telugu, benign)
3. Use **Workspace** view for larger analysis sessions
4. **Save report** (JSON) for your records

### Developers
1. Fork repository and create a branch
2. Run full test suite (`npm test && uv run python -m unittest discover`)
3. Submit PR with tests and documentation updates
4. Review CODE OF CONDUCT and research governance requirements

---

**Happy analyzing! 🔍**
