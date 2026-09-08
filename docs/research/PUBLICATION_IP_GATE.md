# Fisher Publication and IP Gate

> Status: internal, embargoed planning control. This document is not legal advice, a patentability opinion, a freedom-to-operate analysis, or a substitute for qualified counsel.

## Purpose

This gate prevents research publication pressure from causing premature disclosure or inflated novelty claims. It applies before any public preprint, GitHub publication, dataset/model release, abstract, poster, talk, competition submission, public demo, thesis upload, or venue submission describing the proposed Fisher mechanism.

**OBSERVED:** Fisher is presently an uncommitted, pre-data research design with no measured result. **DERIVED:** there is no evidence yet that the proposed mechanism works or that it is protectable. **UNKNOWN:** inventorship, ownership, name clearance, filing jurisdiction, statutory deadlines, patentability, freedom to operate, and the effect of any prior/private disclosure.

## Research novelty and patentability are different gates

A publishable empirical contribution can be incremental yet useful. A technically interesting idea can still be unpatentable, owned by another party, disclosed too early, or blocked by prior claims. Conversely, a filing decision does not validate the science.

The research gate asks whether Fisher provides measured evidence beyond strong baselines. The IP gate asks a qualified professional whether a specific claim set is new, non-obvious, sufficiently described, owned by the correct inventors/assignees, and worth filing. Passing one does not pass the other.

## What Fisher must not claim

The following directions are established, generic, crowded, or insufficiently searched and cannot be represented as Fisher inventions:

- N-best or lattice transliteration;
- context-aware Romanized Indic transliteration;
- Aksharantar, IndicXlit, MuRIL, XLM-R, IndicBERT v2, or IndicLID;
- typed graphs or actor/action/destination extraction;
- generic brand, source, owner, or domain consistency checking;
- generic `transliterate → graph → compare destination → score → alert` orchestration;
- multitask classification, temperature scaling, selective classification, confidence display, or explanations;
- conversation-level scam progression or conversation memory; and
- a first Indic, multilingual, scam, deployable, on-device, or production phishing detector.

Public products include [Google Messages scam protection described for India](https://blog.google/intl/en-in/company-news/googles-safety-charter-for-indias-ai-led-transformation/) and [Microsoft Defender user/domain impersonation protection](https://learn.microsoft.com/en-us/defender-office-365/anti-phishing-policies-about). **UNKNOWN:** their internal model architecture and exact Indic behavior. Their existence is sufficient to prohibit an unsupported “first deployable system” claim.

## Narrow invention candidate for professional review

**DERIVED candidate, not a legal claim:** preserve calibrated probabilities over ambiguous Romanized interpretations; apply shared path encoding and path-specific semantic relation/risk inference; marginalize relation posteriors and risk using those probabilities; quantify instability between path-level semantic/risk results; and use that instability jointly with predictive entropy in a selective decision.

The potentially reviewable unit is the probability-preserving relation-posterior/instability/selective coupling, not its individual components. It remains subject to these disqualifying checks:

1. the mechanism is already disclosed in scientific, patent, product, thesis, code, or standards literature;
2. the implementation merely applies known marginalization and selective prediction in an obvious way;
3. experiments show no mechanism-specific benefit;
4. the description lacks a concrete, reproducible implementation;
5. earlier public/private work changes ownership or novelty; or
6. filing cost and enforcement value outweigh realistic benefit.

**UNKNOWN:** whether this candidate has weak, moderate, or strong patent potential. Only a professional search and claim analysis can assign that conclusion.

## Patent-pressure register

These documents are pressure indicators requiring element-by-element professional review; their inclusion is not a conclusion that Fisher infringes, is anticipated, or is patentable.

| Document | Pressure area to inspect | Current conclusion |
| --- | --- | --- |
| [US8438642B2](https://patents.google.com/patent/US8438642B2/en) | phishing/identity-related detection pipelines | Scope overlap **UNKNOWN**; claim chart required |
| [US12531898B2](https://patents.google.com/patent/US12531898B2/en) | claimed source/domain-owner or related consistency comparison | Highest stated pressure for generic entity–destination checks; exact overlap **UNKNOWN** |
| [US11750648B1](https://patents.google.com/patent/US11750648B1/en) | phishing detection and message/security analysis | Scope overlap **UNKNOWN** |
| [US20250133111A1](https://patents.google.com/patent/US20250133111A1/en) | recent phishing/scam analysis claims | Pending/legal status and overlap require counsel |
| [WO2026075707A1](https://patents.google.com/patent/WO2026075707A1/en) | conversation-aware scam/phishing reasoning | Supports deferring conversation-memory novelty from Paper 1 |

Search must also include patent families, prosecution history, citations, continuations, non-US equivalents, abandoned applications where technically relevant, non-patent literature, products, repositories, dissertations, and public demonstrations. A keyword search alone is inadequate.

## Scientific prior-art boundary

At minimum, compare the proposed mechanism element by element against:

- [transliteration lattice precedent](https://aclanthology.org/W12-4410/);
- [neural lattice language modeling](https://arxiv.org/abs/1803.05071);
- [context-aware Romanized South Asian transliteration](https://direct.mit.edu/coli/article/50/2/475/119145/);
- [Aksharantar](https://aclanthology.org/2023.findings-emnlp.4/);
- [MuRIL](https://arxiv.org/abs/2103.10730), [IndicBERT v2](https://aclanthology.org/2023.acl-long.693/), [IndicLID](https://arxiv.org/abs/2305.15814), and [XLM-R](https://arxiv.org/abs/1911.02116);
- [PhishSigma++](https://arxiv.org/abs/2605.11619), [semantic scam primitives](https://aclanthology.org/2026.findings-acl.1025/), [ScriptMind](https://aclanthology.org/2026.eacl-industry.2/), and [SmishTank](https://arxiv.org/abs/2402.18430);
- [neural-network calibration](https://proceedings.mlr.press/v70/guo17a.html); and
- [selective classification](https://arxiv.org/abs/1705.08500).

This list is non-exhaustive. Search coverage, query strings, databases, dates, and exclusions must be preserved in an internal evidence log.

## Required disclosure sequence

No step may be skipped merely to meet a paper deadline:

1. **Internal invention disclosure:** freeze the exact mechanism, contributors, dated conception evidence, implementation status, alternatives, and known prior art.
2. **Professional review:** qualified counsel or the responsible institutional technology-transfer office performs inventor/ownership review, search strategy review, and element-by-element claim charting.
3. **Empirical gate:** `development`-only evidence establishes that the claimed coupling exists in code and has a measurable mechanism signal; `primary_test` results remain governed by the preregistration.
4. **Decision:** authorized owner records `FILE`, `DO NOT FILE`, or `DEFER`, including jurisdiction/timing constraints and who approved it.
5. **If filing:** obtain written confirmation of the filing event and the exact scope authorized for disclosure. Do not assume that drafting, payment, or counsel discussion equals filing.
6. **If no filing:** obtain written authorization to disclose and retain the reasons; narrow scholarly novelty language to the evidence.
7. **Public release:** only then choose preprint/code/data/demo/venue timing, apply dataset consent/license restrictions, and run publication QA.

[WIPO's patent FAQ](https://www.wipo.int/en/web/patents/faq_patents) explains why public disclosure can affect novelty. The consequences depend on jurisdiction and facts, so professional advice is mandatory.

## Gate checklist

### A. Identity, ownership, and disclosure audit

- [ ] Every contributor and claimed inventive contribution is recorded.
- [ ] Employment, university, sponsor, competition, grant, and collaborator IP terms are reviewed.
- [ ] Prior talks, messages, repositories, attachments, demos, classes, proposals, and submissions are catalogued with audience and date.
- [ ] The current repository visibility and access list are verified.
- [ ] Fisher project/product/publication name clearance is professionally reviewed.

### B. Search and claim-boundary audit

- [ ] A professional search covers patents, families, prosecution, papers, code, products, theses, and standards.
- [ ] Each candidate claim element is charted against the closest references.
- [ ] Generic components are expressly disclaimed.
- [ ] Alternatives and design-around value are assessed.
- [ ] Freedom-to-operate questions are separated from patentability questions.

### C. Technical enablement audit

- [ ] The exact algorithm, data flow, candidate calibration, marginalization, disagreement measure, and selective policy are reproducibly described.
- [ ] A working internal implementation exists.
- [ ] `development`-only mechanism evidence is preserved without claiming `primary_test` success.
- [ ] Inventive steps are distinguishable from MuRIL/encoder choice and ordinary engineering.
- [ ] Failed alternatives and null ablations are retained.
- [ ] Capacity- and supervision-matched controls show whether any gain comes from semantic consistency rather than extra parameters or labels.
- [ ] The [transliteration-resource](TRANSLITERATION_RESOURCE_PROTOCOL.md), [offline-registry](REGISTRY_PROTOCOL.md), and [factorial-condition](FACTORIAL_CONDITION_SPEC.md) manifests are frozen and hash-linked.

### D. Research publication audit

- [ ] Both co-primary results and all preregistered gates are reported honestly.
- [ ] Claims match the method-plus-benchmark, dataset/resource, or null-result route selected by evidence.
- [ ] No metric, SOTA, real-world, on-device, user-safety, or production claim exceeds the study.
- [ ] `primary_test` contains only tester-originated records, every label×stratum cell meets the authentic-donation gate for a field-like claim, and donation/simulation results are disaggregated.
- [ ] Gold labels rely only on model-visible text/artifacts; source intent and provenance are not presented as model evidence.
- [ ] Dataset release permission is evaluated row by row; public accessibility is not treated as a license.
- [ ] Anonymization, dual-submission, artifact, and preprint policies for the target venue are checked at decision time.

### E. Security, privacy, and release audit

- [ ] Released examples contain no active links, credentials, direct identifiers, or unsafe artifacts.
- [ ] Consent, withdrawal, provenance, license, and redistribution rules permit the exact release.
- [ ] Model/data artifacts are checked for memorization and sensitive leakage.
- [ ] The demo is offline/safe and labeled as a research prototype.
- [ ] Publication artifacts disclose limitations and abstention behavior.

## Decision outcomes

| Outcome | Required evidence | Permitted next action |
| --- | --- | --- |
| `BLOCKED` | any ownership, disclosure, safety, data-rights, or claim-boundary item unresolved | continue internal work only |
| `FILE` | written professional/owner decision plus confirmed filing and authorized disclosure scope | disclose only the authorized material |
| `DO NOT FILE` | written owner decision and scholarly claim boundary | publish after research/data/security gates pass |
| `DEFER` | documented missing evidence and next review date/owner | remain embargoed; gather specified evidence |

The current outcome is **BLOCKED** because professional search, ownership/name review, technical implementation, empirical evidence, and a filing/no-filing decision are all **UNKNOWN** or incomplete.

## Paper-claim language after the gate

If the empirical and publication gates pass, use bounded language such as “we evaluate” and “in our preregistered corpus.” Use “we propose” for the coupled method unless exhaustive evidence supports a stronger phrase. Report null or mixed co-primary results directly. Do not use “proves,” “solves phishing,” “first,” “patented,” “patent pending,” “production-ready,” or “protects users” without exact supporting authority and evidence.

## Recordkeeping

Keep the invention disclosure, counsel communications, claim charts, access lists, and sensitive prior-art work outside public artifacts with appropriate access controls. The repository's Luna register records verified checkpoint decisions, not privileged legal content. A public release decision must name the authorizing person/office, authorized material, date, and the research/data/security gates that passed.
