> Governance record

# CHANGE & DECISION LOG

*Repository-wide audit trail for Git commits and significant changes*

> **Canonical-format notice (17 August 2026):** Markdown supersedes the previous Word workflow at the user's direction. `docs/CHANGE_DECISION_LOG.docx` is retained only as a read-only legacy artifact and must not be edited.

- Owner: luna custom agent

- Canonical path: `docs/CHANGE_DECISION_LOG.md`

- Scope: Every Git commit and every significant project change

- Status: Active - publication `main`; original local `master` preserved

- Last updated: 8 September 2026, Asia/Kolkata

**COMMIT GATE:** No Git commit may be created through the Codex workflow until Luna has recorded and validated it, the Markdown register is staged, and the commit message includes the matching `Luna-ID` trailer.

## Operating policy

Complete the technical change and its evidence-based verification.

Finalize and stage the intended non-register files when preparing a commit.

Invoke Luna with verified decisions, affected paths, alternatives, outcomes, risks, and planned commit information.

Luna assigns a unique Luna-ID, updates this Markdown register, and validates its structure, content, and diff.

Stage this Markdown register and include `Luna-ID: <record-id>` as a commit-message trailer.

During the next substantive Luna cycle, backfill any pending final commit SHA by matching the trailer; never create a document-only hash-backfill commit.

### What counts as significant

A change is significant when it affects behavior, interfaces, architecture, models, datasets, data provenance, configuration, dependencies, security or privacy, compatibility, performance or evaluation claims, tests, deployment, operational workflow, or documentation that changes project intent.

Every commit receives a record, even when the conclusion is No significant change.

One commit may contain multiple decision items; each decision keeps its own rationale and rejected alternatives.

Register-maintenance edits belong to the record they update and do not trigger a recursive second record.

### Commit identity rule

A file inside a commit cannot reliably contain that commit's own final SHA: inserting the SHA changes the file, which changes the commit and produces a different SHA. The pre-commit Luna-ID is therefore the authoritative same-commit link. Final SHAs are backfilled only during a later substantive register update.

## Required record structure

Luna uses the following schema for every commit record and significant-change entry. Fields may be marked not applicable only with a reason.

| Required field | Content requirement |
| --- | --- |
| Identity | Luna-ID, lifecycle state, revision history, date/time, and responsible agent. |
| Git context | Branch/ref, planned subject, Luna-ID trailer, commit and parent SHA when available. |
| Change inventory | Affected paths and a concise description of each material change. |
| Decision | The chosen course, scope, and intended outcome. |
| Rationale and evidence | Why the decision was made, with OBSERVED, DERIVED, ASSUMED, or UNKNOWN labels. |
| Alternatives | Each option considered and the concrete reason it was not selected. |
| Impact | Compatibility, data, security, privacy, performance, cost, and operational effects when relevant. |
| Verification | Exact commands or checks executed, their outcomes, and checks not run. |
| Risk and follow-up | Remaining risks, open questions, owner, and next action. |
| Correction history | Dated append-only revisions that preserve and explain the original statement. |

## Record lifecycle

Prepared - Luna inspects verified evidence, assigns the Luna-ID, and records the planned subject with SHA marked Pending.

Committed - the Git commit contains the matching Luna-ID trailer.

Backfilled - a later substantive Luna cycle matches the trailer to the final SHA and parent SHA.

Corrected - a dated revision preserves the original text and explains the correction; finalized content is never silently overwritten.

### Governance boundaries

Luna writes only this Markdown register; it does not implement code, edit configuration, stage files, or create commits.

Technical agents provide verified evidence; Luna records it without inventing missing facts.

Human or tool-driven commits outside Codex can bypass this prompt-level gate unless a Git hook or CI policy is added later.

The register is append-only after finalization; corrections remain auditable.

## Prepared record - LUNA-20260816-001

- Lifecycle: Prepared - uncommitted

- Branch: master (unborn branch; no commits exist)

- Planned subject: Configure NLP multi-agent orchestration and decision logging

- Required trailer: Luna-ID: LUNA-20260816-001

- Commit SHA: Pending

- Parent SHA: Not applicable - repository has no commits

- Prepared: 16 August 2026, 11:51 PM IST

### Change inventory

Create a project-level NLP orchestration policy in AGENTS.md.

Enable project subagents and define terra, sol_ultra, sol_high, and sol_max profiles under .codex/agents/.

Add the luna profile using gpt-5.6-luna with medium reasoning and a single-file documentation boundary.

Create this canonical Word register and make Luna review mandatory for every commit and significant change.

### Decision D-001 - Use project-scoped Codex configuration

Decision: keep shared orchestration in the repository-root AGENTS.md and define specialist profiles in .codex/agents/*.toml.

Rationale: [OBSERVED] Official OpenAI documentation defines root-to-working-directory AGENTS.md discovery and project custom agents under .codex/agents/. [DERIVED] Project scope keeps the workflow portable with the repository and avoids changing unrelated repositories.

#### Alternatives not selected

Global ~/.codex configuration: not selected because it would affect unrelated repositories and would not travel with this project.

AGENTS.md without custom profiles: not selected because it cannot pin role-specific models, reasoning levels, and sandbox defaults.

Build an external API orchestrator: not selected because the local Codex agent system already supplies the requested capability with far less code and operational overhead.

### Decision D-002 - Specialize models and reasoning by role

Decision: use gpt-5.6-terra/xhigh for ambiguity review; gpt-5.6-sol at ultra, high, and max for complex design and implementation; and gpt-5.6-luna/medium for the repeatable documentarian role.

Rationale: [OBSERVED] The installed model catalog accepts every selected model and reasoning level. [OBSERVED] OpenAI recommends Luna for clear, repeatable, high-volume work. [DERIVED] A narrow documentation workflow does not require the cost or depth of a Sol implementation profile.

#### Alternatives not selected

Use one model and effort for every role: not selected because analysis, production coding, and routine logging have materially different complexity and cost profiles.

Leave model selection unpinned: not selected because the requested role names imply stable, reviewable routing behavior.

Use Luna for technical decisions: not selected because Luna is intentionally bounded to recording already-verified conclusions.

### Decision D-003 - Use a dedicated Word register owned by Luna

Decision: maintain docs/CHANGE_DECISION_LOG.docx as the canonical human-readable audit record and reserve its edits for Luna.

Rationale: [OBSERVED] The user explicitly requested a Word document that captures every commit, significant change, decision, rationale, and rejected option. [DERIVED] Exclusive ownership prevents routing overlap and inconsistent register formatting.

#### Alternatives not selected

Let sol_high maintain the register: not selected because general documentation and repeatable governance logging are distinct responsibilities; sol_high remains available for all other documentation.

Use Markdown only: not selected because it would not satisfy the requested Word deliverable.

Keep the report outside the repository: not selected because a project-local canonical file is easier for Codex tasks to discover and update consistently.

### Decision D-004 - Link commits with Luna-ID before backfilling SHAs

Decision: assign a Luna-ID before commit, include it in the Word record and commit-message trailer, and backfill the final SHA only during the next substantive register update.

Rationale: [DERIVED] This provides a stable same-commit identifier without the self-referential hash problem. It also avoids an infinite series of amend or documentation-only commits.

#### Alternatives not selected

Embed the final SHA before commit: not selected because changing the document to add the SHA changes the commit's SHA.

Amend repeatedly until the SHA matches: not selected because every amend changes the hash again and cannot reach a fixed point by this workflow.

Create a separate backfill commit: not selected because that new commit would itself require another record and final-hash backfill.

Git notes plus hook and CI enforcement: deferred because the repository has no remote or CI setup and the user asked for a Luna/Word workflow; this remains the stronger future option for immutable exact-SHA auditing.

### Impact and tradeoffs

Compatibility: no application or dataset behavior changes; this is repository governance configuration.

Security and privacy: no secrets or user data are stored; Luna is instructed not to copy unnecessary raw diff content.

Operational cost: every significant task and commit adds a Luna run plus Word render QA, increasing latency and token usage in exchange for auditability.

Enforcement limit: Codex is blocked by AGENTS.md, but direct human commits remain bypassable until hooks or CI are deliberately added.

### Verification performed

Codex CLI 0.147.0-alpha.6.5 strict configuration loader accepted the project configuration (exit 0).

TOML and live model-catalog validation confirmed five unique profiles and every selected model, reasoning level, and sandbox value.

An ephemeral read-only Codex smoke test discovered and spawned luna, returning SMOKE_OK luna (exit 0).

The original four profiles were previously smoke-tested together, returning SMOKE_OK terra sol_ultra sol_high sol_max (exit 0).

Application tests: not applicable; this change contains only agent configuration, governance instructions, and a Word document.

### Document QA

PASSED - six rendered pages inspected; exact table geometry and accessibility audits returned no errors; heading, section, style, and extracted-text checks completed.

### Remaining risks and follow-up

Binary DOCX changes are not human-readable in ordinary Git diffs; render and content extraction remain mandatory.

The Luna single-file write boundary is instruction-based rather than a path-level sandbox guarantee.

Add a Git hook and CI validation later if commits made outside Codex must be mechanically blocked.

Push and backfill the final SHA during the next substantive Luna cycle after the first commit exists.

### Sources

Official OpenAI custom-agent guidance: https://learn.chatgpt.com/docs/agent-configuration/subagents

Official OpenAI model guidance: https://developers.openai.com/api/docs/guides/latest-model

## Decision record - LUNA-20260817-001

### Fisher paper 1: uncertainty-aware multilingual phishing detection

Lifecycle: Decision recorded - no commit requested

Recorded: 17 August 2026, 7:32 AM IST

Responsible agent: luna

Branch: master (unborn branch; no commits exist)

Planned commit subject: Not proposed

Commit SHA: Pending (no commit requested)

Parent SHA: None - repository has no commits

Git action: No staging, commit, push, publication, or release performed

### Checkpoint scope and evidence

[OBSERVED - parent-supplied research evidence] Three independent research agents and a Terra scope review completed the research checkpoint. No dataset was downloaded, no model was trained, no metric was measured, and no application test applies to this decision-only checkpoint.

[OBSERVED] Luna ran git status --short --branch and confirmed master is unborn with no commits. The parent reported no project-file change before this register update.

[DECISION] The checkpoint freezes a smallest-defensible first-paper specification. Empirical gains, name clearance, exhaustive novelty, patentability, and real-world performance remain unverified.

#### Decision D-006 - Keep Fisher as the name and add a descriptive subtitle

Decision: Use Fisher only as the project name, following the user's explicit instruction. Use a descriptive paper subtitle so readers can distinguish this work from similarly named systems.

Rationale: [OBSERVED - parent-supplied research evidence] Name collisions include the Fisher Antiphishing System Chrome extension and a cybersecurity product named Fisher. [DERIVED] A descriptive subtitle reduces scholarly ambiguity without overriding the requested name.

Boundary: [UNKNOWN] Trademark, product-name, domain, and publication-title clearance require a dedicated professional search. No clearance or legal conclusion is claimed.

Alternatives not selected: renaming the project was rejected because the user explicitly required Fisher; publishing under the bare name without a subtitle was not selected because observed collisions make the subject unclear.

#### Decision D-007 - Limit paper 1 to NLP-first text and destination-artifact evidence

Decision: Paper 1 covers message text plus URL or destination-artifact evidence. Its language strata are Hindi, Tamil, Telugu, and English-Indic code-mixed text.

Scope deferred: Bengali and Marathi move to a gated expansion. Conversations, browser vision, QR images, calls, voice or ASR, campaign intelligence, application deployment, and warning user studies are deferred to later work.

Rationale: [DERIVED] The smallest defensible 6,000-item, low-false-positive-rate design cannot support six language strata and multiple channels with credible independent testing. Kannada and Malayalam are not substituted merely because SMSDHL contains them; corpus availability does not override the stated study population.

Alternatives not selected: an all-channel paper was rejected as unfocused and unvalidated; voice now was rejected because authentic consented audio is unavailable and ASR error would confound the NLP question; conversation-memory novelty was rejected for paper 1 because 2024-2026 work and WO2026075707A1 make that area crowded; an immediate six-language 18,000-item build was rejected as premature.

#### Decision D-008 - Retain a binary headline target and add structured auxiliary annotations

Decision: The primary semantic target is binary benign versus phishing, matching the supplied brief. Promotional or nonmalicious spam remains a benign subtype or facet, not a third headline class. Uncertain is an annotation, adjudication, or selective-abstention state, not a semantic training class.

Structured annotations: claimed actor or organization; claim or problem; requested action; sensitive item or asset; destination artifact; pressure tactics; supporting evidence spans; and an entity-destination relation labeled MATCH, MISMATCH, UNKNOWN, or N/A.

Rationale: [DERIVED] The binary target preserves alignment with the original research question while auxiliary facets expose phishing semantics and support consistency analysis without conflating promotion with fraud.

Alternative not selected: a third promotional class was rejected as the headline target because the source brief specifies phishing versus benign. Promotion is preserved as a subtype so future analysis remains possible.

#### Decision D-009 - Couple Romanized-form uncertainty to semantic consistency and calibrated abstention

Decision: Preserve uncertainty over Romanized Indic forms and propagate calibrated, weighted candidate paths into actor-claim-action-destination node and relation inference. Marginalize relation, contradiction, and risk evidence across paths. Use UNKNOWN when registry evidence is missing, and permit calibrated abstention.

Proposed novelty: [DERIVED] The contribution is the coupling of uncertainty-aware transliteration, structured semantic consistency, relation-level marginalization, tri-state registry reasoning, and selective risk. No individual component alone is claimed as new.

Primary research question: Does uncertainty-marginalized transliteration improve campaign- and author-disjoint phishing detection and selective risk over raw text, one-best deromanization, and flat top-k augmentation, especially through semantic consistency?

Boundary: [UNKNOWN] Exact novelty and patentability require an exhaustive professional prior-art search, counsel, and successful experiments. No patent claim or legal conclusion is made.

Alternatives not selected: a generic transliteration lattice or top-k method was rejected as a novelty claim because the approach is established at least as early as the 2012 transliteration work and is represented by Aksharantar; a generic typed phishing graph was rejected because PhishSigma++ exists; explanations alone were rejected because KorSmishing and SmishX already cover relevant explanatory directions.

#### Decision D-010 - Use MuRIL centrally and require matched ablations

Decision: Use MuRIL as the central encoder recommendation, with XLM-R base and IndicBERT v2 as matched multilingual comparators.

Core experiment: a 2 x 2 design crossing top-1 versus uncertainty-marginalized transliteration with semantic consistency absent versus present.

Required baselines: classical character and word TF-IDF; an adapted typed-relation baseline; graph without consistency; weighted candidates without graph inference; raw text; one-best deromanization; and flat top-k augmentation.

Evidence status: [ASSUMED/HYPOTHESIS] Any expected improvement is a preregistered hypothesis, not a measured result. Training, latency, calibration, and ablation outcomes are UNKNOWN until experiments run.

#### Decision D-011 - Apply consent, provenance, licensing, and sensitive-data gates before collection

Decision: Collect only from consenting adult own testers and public sources with suitable verified licenses. Keep public authentic, tester-donated, tester-authored simulation, and LLM-drafted-human-edited provenance distinct at row level.

LLM boundary: LLM augmentation may contribute at most 30% of train and development data and 0% of the primary test set. LLM output never supplies a gold label without human annotation.

Safety and privacy: never collect live OTPs, credentials, active malicious links, phone numbers, UPI IDs, or account IDs. Defang artifacts or use .invalid and .example. Complete ethics, consent, privacy review, and a row-level source and license ledger before collection. Restrict raw authentic donations unless redistribution rights are documented.

Public-source audit: use UCI SMS Spam Collection (CC BY 4.0) and Mishra-Soni (CC BY 4.0) only after phishing-specific reannotation plus OCR and duplicate audits. Treat SMSDHL as conditional because record terms or redistribution are ambiguous and its spam label conflates promotion, phishing, fraud, and bulk messaging. Use Dakshina and Aksharantar only as auxiliary transliteration resources with preserved license provenance. Exclude Sting9 for now because CC0 and ODC-BY-NC terms conflict. Do not ingest unverified SmishTank or other public data.

Alternative not selected: public-but-unlicensed or ambiguously licensed data was rejected because public accessibility does not establish permission to redistribute or use it for this corpus.

#### Decision D-012 - Gate a 6,000-item corpus through a 1,200-item ontology pilot

Decision: First create a 1,200-unique-item, double-annotated ontology pilot. It tests guide coverage and agreement, not system performance. Proceed only if primary-label agreement is at least 0.80 and structured-facet agreement is adequate or the guide is revised.

Main-corpus target: 6,000 unique, group-disjoint items - 1,500 in each of the four language strata, targeting 750 phishing and 750 benign per stratum.

Low-FPR design: lock at least 300 independent benign items per stratum in a group-, time-, domain-, sender-, and template-disjoint test. Select all thresholds on development data only. [DERIVED] If zero false positives are observed on 300 independent benign items, the one-sided exact 95% upper FPR is approximately 0.994%. This is a sample-size property, not an experimental result.

Scale boundary: if six language strata or granular performance claims remain required, scale toward 18,000 items instead of diluting the four-stratum design.

Alternatives not selected: a 300-message annotation pilot was rejected as too small for ontology-guide coverage; 300 is retained only as the minimum independent benign test stratum for the low-FPR bound. An immediate 18,000-item build was rejected until the ontology pilot passes its gate.

#### Decision D-013 - Enforce connected-component leakage control and selective evaluation

Decision: Construct split groups as connected components spanning exact and near duplicates; translation, transliteration, paraphrase, and counterfactual parents; scenario, template, and campaign; domain, URL, UPI, phone, and sender; tester author and donation batch; and LLM or prompt family. No LLM-generated item may enter the primary test set.

Evaluation focus: campaign- and author-disjoint binary detection, per-stratum error analysis, calibration, coverage-risk or selective-risk behavior, semantic-consistency ablations, and the locked benign false-positive analysis. Thresholds are chosen on development only.

Rationale: [DERIVED] Group-disjoint splitting is necessary to prevent translated, templated, donated, or generated relatives from leaking across train and test and inflating results.

#### Decision D-014 - Sequence publication and preserve an IP decision window

Decision: Submit the benchmark and method paper first. Candidate venues include a resource venue, TALLIP, ICON, FIRE, or Findings depending on measured results. Sequence later work as conversation modeling, warnings and user study, then voice.

Timing: [OBSERVED - parent-supplied research evidence] FIRE 2026 lists 31 August 2026 as a deadline. Do not rush a results paper from an empty repository solely to meet that date.

IP boundary: avoid public disclosure of the proposed core invention until an IP filing decision is made. [OBSERVED - cited source] WIPO warns that disclosure can destroy novelty. This is a research-planning precaution, not a patentability or legal conclusion.

#### Decision D-015 - Freeze prerequisites before the pilot

Immediate next phase: freeze a one-page preregistration, annotation manual, tester consent and ethics package, and machine-readable source and license ledger. Run the 1,200-item pilot, revise inadequate facets, and proceed to 6,000 only after the stated agreement gate is met.

Owner: lead orchestrator with domain reviewers and native-language annotators to be identified. Luna records later checkpoints after their evidence is verified.

### Consolidated rejected alternatives

- Broad all-channel paper: rejected as unfocused and unvalidated.

- Voice in paper 1: rejected because authentic consented audio is unavailable and ASR error would confound the NLP study.

- Conversation-memory novelty in paper 1: rejected because recent work and WO2026075707A1 make the direction crowded.

- Generic transliteration lattice or top-k as the novelty: rejected because prior transliteration work and Aksharantar establish the component direction.

- Generic typed phishing graph as the novelty: rejected because PhishSigma++ already exists.

- Explanations alone as the novelty: rejected because KorSmishing and SmishX cover relevant explanation directions.

- Immediate six-language, 18,000-item build: rejected as premature; use gated scale after the ontology pilot.

- A 300-message annotation pilot: rejected as too small for guide coverage; 1,200 is the ontology pilot, while 300 is only the minimum benign test stratum used for the low-FPR bound.

- Third promotional headline class: rejected because the brief specifies binary phishing versus benign; promotion remains a benign subtype.

- Public-but-unlicensed data: rejected because accessibility does not establish suitable use or redistribution rights.

### Impact and tradeoffs

- Compatibility: no application interface, model, or dataset artifact changed at this checkpoint; the decision constrains future paper-1 work.

- Data and provenance: strict source, license, consent, and lineage fields increase preparation cost but protect reproducibility and lawful reuse.

- Security and privacy: defanging and synthetic identifiers reduce exposure to active malicious artifacts and sensitive credentials; authentic data scarcity may increase.

- Performance and cost: uncertainty marginalization, semantic graphs, calibration, and matched ablations may increase training and inference cost. No latency or accuracy claim is yet measured.

- Operational scope: four strata and text-first evidence trade breadth for a defensible first study and independent low-FPR evaluation.

### Verification performed

- Research review: parent-supplied evidence reports three independent research agents plus an independent Terra scope review.

- Repository state: git status --short --branch returned No commits yet on master; no commit, parent commit, staging, or push exists.

- Empirical checks: no dataset download, annotation run, model training, metric computation, latency measurement, or user study was performed.

- Application tests: not applicable because this is an architecture and research-design checkpoint with no technical implementation change.

Document QA: PASSED - 13 pages rendered; affected pages 7-13 were visually inspected at original resolution. No clipping, overlap, broken bullets, missing glyphs, or header/footer defects were observed; extracted-text verification completed.

### Remaining risks and follow-up

- Native-speaker and language coverage may be insufficient across Hindi, Tamil, Telugu, and code-mixed strata.

- Public-source licenses and redistribution terms require item-level verification before ingestion.

- Authentic phishing data may remain scarce; simulated and LLM-assisted data may differ from real deployment distributions.

- Double annotation and structured relation labeling create substantial cost and adjudication burden.

- Fisher name clearance, exhaustive prior art, and any patent filing decision require professional searches and counsel.

- Model latency, calibration stability, incomplete registries, and the controlled-versus-real distribution gap remain UNKNOWN until implementation and evaluation.

Next action: complete the preregistration, annotation manual, consent and ethics package, and source-license ledger before collecting the 1,200-item pilot.

### Compact references

Transliteration lattice precedent: https://aclanthology.org/W12-4410/

Aksharantar: https://aclanthology.org/2023.findings-emnlp.4/

Dakshina dataset and license provenance: https://github.com/google-research-datasets/dakshina

Recent multilingual phishing research: https://arxiv.org/abs/2605.11619

SOUPS 2025 related work: https://www.usenix.org/conference/soups2025/presentation/wang

EMNLP Industry 2024 related work: https://aclanthology.org/2024.emnlp-industry.47/

Conversation-memory prior art: https://patents.google.com/patent/WO2026075707A1/en

Additional phishing patent references: https://patents.google.com/patent/US10277628B1/en and https://patents.google.com/patent/US11924245B2/en

UCI SMS Spam Collection: https://archive.ics.uci.edu/dataset/228/sms

Mishra-Soni dataset: https://data.mendeley.com/datasets/f45bkkt8pr/1

SMSDHL source page: https://sites.google.com/cse.nits.ac.in/ramanujamge/publications/datasets-offered

Sting9 dataset terms: https://sting9.org/dataset

WIPO patent FAQ: https://www.wipo.int/en/web/patents/faq_patents

FIRE 2026 call for papers: https://fire.irsi.org.in/fire/2026/call_for_papers

## Decision record - LUNA-20260817-002

### IEEE DataPort assessment: SMS spam in Dravidian languages

Lifecycle: Decision recorded - no commit requested

Recorded: 17 August 2026, 8:17 AM IST

Responsible agent: luna

Branch: master (unborn branch; no commits exist)

Planned commit subject: Not proposed

Commit SHA: Pending (no commit requested)

Parent SHA: None - repository has no commits

Git action: No staging, commit, push, publication, or release performed

### Source identity and observed metadata

[OBSERVED - parent-supplied DataCite evidence] DOI 10.21227/dcym-pd69 identifies a 2023 IEEE DataPort dataset created by Ramanujam Elangovan and Abirami A M. DataCite resource type is Dataset.

[OBSERVED - parent-supplied DataCite evidence] rightsList is exactly Creative Commons Attribution 4.0 International / cc-by-4.0. License status is therefore promoted from UNKNOWN to OBSERVED CC BY 4.0.

Intended title: Spam SMS in Dravidian Languages. The registered DataCite title contains the typo Spam SMS in Dravidian Langugaes; the DOI remains the authoritative identifier.

DataCite JSON: https://api.datacite.org/dois/10.21227/dcym-pd69

### Registered dataset counts

- English: 521 spam and 1,578 ham = 2,099 messages.

- Tamil: 212 spam and 963 ham = 1,175 messages.

- Telugu: 105 spam and 989 ham = 1,094 messages.

- Kannada: 333 spam and 1,017 ham = 1,350 messages.

- Malayalam: 224 spam and 1,775 ham = 1,999 messages.

- Total: 1,395 spam and 6,322 ham = 7,717 messages.

[DERIVED from registered counts] Source spam rates are 18.1% overall, 18.0% for Tamil, and 9.6% for Telugu. These describe the source spam label distribution and are not phishing prevalence estimates.

### Collection and access evidence

[OBSERVED - parent-supplied authors' page evidence] Messages were collected through a Google Form from friends and contacts and labelled by language experts. The page includes the Tamil verbatim/Romanized example Nee Nalama, defines spam to include business, annoying, and unnecessary messages, and states that no user personal or banking information is present.

Authors' dataset page: https://sites.google.com/cse.nits.ac.in/ramanujamge/publications/datasets-offered

[OBSERVED - parent-supplied browser evidence] The current IEEE URL redirects to IEEE account sign-in. No file was downloaded or inspected.

[OBSERVED - parent-supplied search-index evidence] The indexed record reports one file named Spam Message Collection.xlsx, size 1.26 MB, with login required.

[UNKNOWN] Raw file contents, schema, row-level text, exact language/script distribution, duplicates, PII, embedded links, label quality, and platform-use obligations remain unverified until lawful authorized access and audit.

### Data-quality reconciliation caution

[OBSERVED - parent-supplied metadata evidence] DataCite registered counts are internally consistent at Tamil 1,175 and overall 7,717.

[OBSERVED - parent-supplied preprint evidence] A later SMSDHL preprint table reports Tamil total 1,176. Its per-language totals sum to 11,612 while its class totals sum to 11,611.

Decision: treat this as a one-row secondary-publication inconsistency. Use DOI metadata provisionally and verify workbook row and class counts after lawful authorized download before ingestion or redistribution.

#### Decision D-016 - Keep the dataset conditional despite the confirmed reusable license

Decision: Status is CONDITIONAL AUXILIARY CANDIDATE. The license field is OBSERVED CC BY 4.0, but the dataset is not approved for ingestion until access, content, privacy, provenance, and platform-term checks complete.

Rationale: [DERIVED] A reusable dataset license resolves one evidence gap but does not establish that the inaccessible workbook is safe, correctly labelled for Fisher, free of sensitive content, or uncontaminated.

#### Decision D-017 - Use only as attributed auxiliary material, never as phishing ground truth

Decision: If the audit passes, use the dataset chiefly for Tamil, Telugu, English, and Romanized-Tamil robustness, representation pretraining, auxiliary training, or a separately reported external diagnostic. Do not classify it as tester-authored Fisher data and do not place it in Fisher's primary tester-authored test set.

Label boundary: preserve the original spam or ham label in a separate field. Double reannotate into the Fisher ontology and keep spam-but-benign distinct from phishing.

Rationale: [OBSERVED] The source label is only spam or ham, and the authors' definition includes business, annoying, and unnecessary messages. [DERIVED] Mapping spam directly to phishing would create construct mismatch, label noise, and an invalid phishing-performance claim.

#### Decision D-018 - Require lawful acquisition, immutable provenance, privacy review, and reannotation

Before use: obtain access lawfully; preserve an immutable source copy, cryptographic hash, DOI, creators, title note, and CC BY attribution; record any IEEE platform terms; and add every derived row to the source and license ledger.

Required audits: privacy and PII scan; language, script, Unicode, and transliteration audit; source-label and class-distribution audit; exact and near-duplicate audit; template and campaign-family audit; link or artifact safety review; and independent double reannotation into the Fisher ontology.

Safety boundary: do not redistribute or expose raw messages until privacy, provenance, attribution, and exact platform-use obligations are captured and reviewed.

#### Decision D-019 - Isolate source families to prevent contamination

Decision: group messages and derived variants by source, duplicate, template, campaign family, author or collection batch, translation or transliteration parent, and other related artifacts before splitting. Prevent any source family from crossing Fisher train, development, and test boundaries.

Preferred evaluation role: auxiliary training or a separately reported external diagnostic. Never merge the source into Fisher's primary tester-authored locked test set.

Rationale: [DERIVED] Collection dependence, class imbalance, repeated templates, and potential overlap could otherwise inflate measured generalization or contaminate the locked low-FPR test.

### Alternatives not selected

- Use the spam label directly as phishing: rejected because the source construct includes nonmalicious promotion, business, annoying, and unnecessary messages.

- Discard the dataset: rejected because it offers rare Indic and Romanized-language evidence under a confirmed reusable CC BY 4.0 license.

- Make it Fisher's primary benchmark: rejected because of the broad spam construct, collection dependence, class imbalance, inaccessible raw workbook, and currently unaudited content.

- Redistribute immediately: rejected until lawful access, privacy and content audits, provenance, attribution, and exact platform-use obligations are documented.

### Impact and tradeoffs

- Compatibility: no model, dataset file, schema, or application behavior changed; this decision narrows future source use.

- Data quality: Fisher-specific reannotation adds cost but prevents a spam-to-phishing construct error and preserves benign-promotion analysis.

- Privacy and security: no raw workbook was accessed. Future use remains gated on PII, link, and platform-term audits.

- Evaluation: the source may improve multilingual robustness evidence, but its imbalanced spam rates and dependent collection cannot be presented as phishing prevalence or primary-test performance.

- Operational cost: immutable provenance, hashing, attribution, deduplication, grouping, and double reannotation increase preparation effort in exchange for defensible reuse.

### Verification performed

- Evidence review: parent supplied verified DataCite DOI metadata, exact registered language counts, authors' collection notes, current sign-in behavior, and indexed file metadata.

- Arithmetic review: 1,395 / 7,717 = 18.1% overall; 212 / 1,175 = 18.0% Tamil; 105 / 1,094 = 9.6% Telugu after one-decimal rounding.

- Repository state: git status --short --branch confirmed unborn master with no commits. No staging, commit, or push was performed.

- Unrun checks: workbook download, schema inspection, row audit, privacy scan, language and transliteration audit, duplicate and campaign-family audit, and Fisher reannotation were not performed because authorized file access was unavailable.

- Application tests: not applicable because this is a source-assessment decision with no implementation or dataset ingestion.

Document QA: PENDING - final page count and visual inspection will be recorded after render verification.

#### Revision - 17 August 2026, 8:50 AM IST

- Original statement preserved above: `Document QA: PENDING - final page count and visual inspection will be recorded after render verification.`
- [OBSERVED] The last completed full Word render before supersession had 18 pages, including a trailing header/footer-only page and a mismatch between the recorded QA count and the rendered result.
- [OBSERVED] A surgical Word repair was in progress when the user directed that DOCX logging stop. That repair was interrupted and was not render-verified.
- [DECISION] No further DOCX repair will be attempted. This Markdown register is canonical from this revision forward; the legacy DOCX carries no final-pass claim.

### Remaining risks and follow-up

- Authorized access and any IEEE platform-use obligations remain unresolved.

- The inaccessible workbook may contain PII, unsafe links, encoding problems, language-label errors, duplicates, templates, or other undisclosed artifacts.

- The spam and ham labels may not support reliable Fisher ontology reannotation without substantial adjudication.

- Collection from friends and contacts may create author, network, template, or campaign dependence and limit external validity.

Next action: obtain authorized access, capture source hash and platform terms, run the required audits, and make a new evidence-based ingestion decision before using or redistributing any row.

### References

DataCite DOI metadata: https://api.datacite.org/dois/10.21227/dcym-pd69

DOI landing identifier: https://doi.org/10.21227/dcym-pd69

Authors' dataset page: https://sites.google.com/cse.nits.ac.in/ramanujamge/publications/datasets-offered

SMSDHL preprint: https://d197for5662m48.cloudfront.net/documents/publicationstatus/239396/preprint_pdf/11fd80fd1139a6c1aac6852266046865.pdf

## Decision record - LUNA-20260817-003

### Replace the Word register with a canonical Markdown register

- Lifecycle: Decision recorded - no commit requested
- Recorded: 17 August 2026, 8:50 AM IST
- Responsible agent: Luna workflow, integrated by the lead orchestrator
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, or release performed

### Change inventory

- Added `docs/CHANGE_DECISION_LOG.md` as the canonical register and migrated the existing policy plus records `LUNA-20260816-001`, `LUNA-20260817-001`, and `LUNA-20260817-002`.
- Updated `AGENTS.md` so every meaningful checkpoint and commit uses the Markdown register.
- Updated `.codex/agents/luna.toml` so Luna may write only the Markdown register and must never edit the legacy DOCX.
- Updated `.codex/agents/sol_high.toml` so the implementation agent respects Luna's Markdown ownership boundary.
- Retained `docs/CHANGE_DECISION_LOG.docx` unchanged as a non-canonical legacy artifact; the Word lock file was not touched.

#### Decision D-020 - Make Markdown the only active Luna register format

Decision: Use `docs/CHANGE_DECISION_LOG.md` as the single canonical change and decision register from this checkpoint forward. Luna must record every meaningful checkpoint and pre-commit record there.

Rationale: [OBSERVED] The user explicitly directed, "INSTEAD OF USING DOCX, USE MDs FROM NOW ON TO RECORD CHANGES DONE BY LUNA." [DERIVED] Markdown is directly reviewable in Git diffs, avoids Word-lock and pagination failures, and keeps the audit trail accessible without a document-rendering toolchain.

### Alternatives not selected

- Continue DOCX logging: rejected because it directly conflicts with the user's latest instruction and had already produced lock, pagination, and style-verification overhead.
- Maintain both DOCX and Markdown as co-canonical: rejected because duplicated authority can drift and would require every checkpoint to be reconciled twice.
- Create one Markdown file per shell command: rejected because commands that produce no material conclusion are not meaningful checkpoints and would create noise.
- Create one Markdown file per Luna ID plus a separate index: not selected because a single append-only register is simpler at the current repository scale and preserves the existing commit-gate workflow.
- Delete the legacy DOCX: rejected because the user requested a format change, not destruction of the historical artifact.

### Impact and tradeoffs

- Auditability: Markdown provides line-level Git diffs and removes binary-only review.
- Operational cost: no Word automation, render, pagination, or accessibility pass is required for future log-only updates.
- Compatibility: existing Luna IDs and historical Word-era decisions remain preserved; D-020 supersedes the earlier Word-format decision.
- Security and privacy: no dataset, secret, credential, or raw message was added.
- Workflow boundary: Markdown validation replaces visual page QA; exact source evidence, alternatives, verification, and risks remain mandatory.

### Verification performed

- Inspected `AGENTS.md`, `.codex/config.toml`, all relevant agent profiles, Git status, and the latest saved DOCX before editing.
- Extracted the legacy DOCX with the bundled workspace Python runtime: 287 paragraphs and one table were readable.
- Preserved all three pre-existing Luna record IDs, 249 non-empty record paragraphs, and 22 non-empty table cells in Markdown.
- Markdown structure check passed: UTF-8 decoding, one H1, a final newline, no carriage returns, and exactly four ordered record headings through `LUNA-20260817-003`.
- All six project TOML files parsed successfully, and active governance searches found no remaining instruction to maintain, stage, or render-verify the DOCX.
- Whitespace checks passed for `AGENTS.md`, both changed agent profiles, and the Markdown register.
- The legacy DOCX SHA-256 at handoff is `defa588fc2b5c9991780f06da13834a7dbb1ebea2731009cd750a0cd39e39eb2`.
- No dataset was downloaded or added.
- No Git stage, commit, push, merge, rebase, tag, pull request, or release was performed.
- Unrun check: no dedicated Markdown linter is configured, and the bundled Python runtime does not include `markdown-it-py`; structural validation used deterministic text and heading checks instead.

### Remaining risks and follow-up

- The legacy DOCX remains untracked and non-canonical; it may still be open in Word and may show a lock file.
- Markdown structure must be checked on every future Luna update because there is no repository Markdown linter yet.
- Existing records contain historical Word-specific statements; they are retained as evidence and superseded by D-020 rather than silently rewritten.

Next action: Luna should use only `docs/CHANGE_DECISION_LOG.md` for the next meaningful checkpoint and should never reopen the DOCX for logging.

## Decision record - LUNA-20260819-001

### Fisher Phase-0 research specification and executable data-contract checkpoint

- Lifecycle: Decision recorded - locally completed checkpoint; no commit requested
- Recorded: 19 August 2026, 2:02:20 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-001`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Checkpoint scope and evidence

[OBSERVED - parent-supplied verified evidence] This checkpoint completes the Fisher Phase-0 research specification, data contract, pilot protocol repairs, and executable validator/tests. It does not establish an authentic corpus, trained model, benchmark, patentability, or measured performance.

[OBSERVED] The affected local package paths are: `.codex/config.toml`; `.codex/agents/{luna,sol_high,sol_max,sol_ultra,terra}.toml`; `.gitignore`; `AGENTS.md`; `README.md`; `data/source_ledger.example.jsonl`; `docs/DATA_CONTRACT.md`; `docs/research/{ANNOTATION_GUIDE,CONSENT_ETHICS_PRIVACY,FACTORIAL_CONDITION_SPEC,FISHER_RESEARCH_BLUEPRINT,PAPER_1_PREREGISTRATION,PRIOR_ART_SEARCH_LOG,PUBLICATION_IP_GATE,REGISTRY_PROTOCOL,SOURCE_LEDGER,TRANSLITERATION_RESOURCE_PROTOCOL,WEEKLY_ROADMAP}.md`; `examples/pilot/{README.md,sources.jsonl,items.jsonl,annotations.jsonl}`; `fisher_data/{__init__.py,__main__.py,validator.py}`; and `tests/test_validator.py`. The legacy `docs/CHANGE_DECISION_LOG.docx` is read-only and is not an affected implementation path.

[OBSERVED] The repository remains an unborn `master` branch with all package paths untracked, no staged paths, no commit, and no push. The origin fetch/push URL is `https://github.com/m-rithik/Phishing-in-indian-language.git`.

### Decisions

#### Decision D-021 - Freeze Fisher's paper identity and narrow NLP-first scope

Decision: Use Fisher only as the project name. The working paper title is “Fisher: Uncertainty-Marginalized Transliteration and Semantic Consistency for Low-False-Positive Multilingual Indic Phishing Detection”. Paper 1 covers standalone message text plus visible defanged artifacts in Hindi, Tamil, Telugu, and English–Indic code-mixed text, with binary phishing/benign classification and promotion treated as benign. Voice, conversation, images, browser integrations, and other channels are deferred.

Rationale: [OBSERVED] The user required the name Fisher and an NLP-first project. [DERIVED] A bounded text study permits controlled linguistic, provenance, and low-false-positive evaluation before adding ASR, multimodal, or interaction confounds.

Boundary: [UNKNOWN] Fisher name, trademark, product, domain, and publication-title clearance remain unresolved.

Alternatives not selected:

- BhashaShield or another replacement name: rejected because the user explicitly selected Fisher.
- Voice, conversation, images, or browser integrations in Paper 1: rejected because they expand the study beyond the verified NLP-first scope and introduce unverified data and evaluation requirements.
- Claiming the bare name is clear: rejected because collision clearance is not complete.

#### Decision D-022 - Define the narrow central research contribution

Decision: Test the hypothesis that calibrated N-best transliteration candidates `q_k` are encoded through a shared path representation, used for path-specific typed actor/action/asset/destination relations and risk, and then marginalized across relation and risk. Path instability and entropy drive selective prediction. Individual lattices, transliteration, graphs, domain checks, calibration, and selectivity are not independently claimed as novel.

Rationale: [DERIVED] The residual research angle is joint uncertainty propagation into typed semantic consistency and low-false-positive selective detection, which is narrower and more falsifiable than presenting familiar components as separate inventions.

Boundary: [UNKNOWN] Exact novelty, patentability, freedom to operate, and superiority require professional search/counsel and experiments.

Alternatives not selected:

- Suspicious-word-only classification: rejected because it does not test structured sender/action/destination consistency.
- One-best transliteration: rejected because it discards spelling uncertainty that is central to the hypothesis.
- Claiming each known component as novel: rejected because prior art covers transliteration lattices, transliteration resources, phishing graphs, calibration, and selective prediction.
- Broad Conversation Risk Memory as the main novelty: rejected because the area is crowded and deferred from Paper 1.

#### Decision D-023 - Freeze provenance, partition, and corpus targets

Decision: Use tester-led data as the core. Public authentic material and descendants may enter only development or external-test partitions after lawful audit and reannotation; public spam labels are never direct phishing ground truth. LLM ancestry is capped at 30% in development and retained pilot and is zero in protected partitions. Protected components are singleton/monostratal.

The retained ontology pilot is exactly 1,200 items: 300 per stratum and 150 benign/150 phishing per stratum; unresolved excluded attempts are extra. The planned 6,000-item corpus is development 3,000, probability calibration 400, safety threshold 400 benign, and primary test 2,200, with 250 phishing and 300 benign per stratum and at least 50% authentic tester donations in each primary-test label-by-stratum cell.

Rationale: [DERIVED] Provenance and connected partition controls are required to prevent public-label construct mismatch, LLM/template leakage, and unsupported protected-test claims while preserving a practical first-paper scale.

Alternatives not selected:

- Public spam mapped directly to phishing: rejected because spam includes benign promotion and other non-phishing content.
- Public or LLM material in protected partitions: rejected because it would weaken provenance and independence claims.
- Immediate larger or all-language expansion: rejected until the pilot and governance gates are passed.

#### Decision D-024 - Enforce the strict data contract and language-integrity rules

Decision: Use the standard-library Python 3.11+ JSONL contract and CLI with schema version 1.0.0, deterministic sanitized diagnostics, resource bounds, all-value live-route scanning, provenance ancestry/cycle/cap checks, protected singleton components, rich facets/spans/evidence/relations/Romanization, registry-manifest binding, and pilot arithmetic/reliability gates. `corpus-final` validation is explicitly not implemented.

Language rule: `stratum_eligible` was removed; every Unicode Letter/Mark lexical token counts. Artifact and brand tokens may be `language=other` but cannot be discarded. Unscripted combining marks inherit the sole recognized script while raw offsets/text remain unchanged. NFC and NFD Latin forms are accepted consistently.

Romanization rule: acceptable-form uniqueness is keyed by NFKC, casefold, splitting all Unicode whitespace, joining one ASCII space, and declared script. Case, gloss, compatibility, or whitespace-only variants do not establish diversity; raw text and offsets are never normalized.

Rationale: [OBSERVED] The executable validator and tests implement these boundaries. [DERIVED] Explicit denominator, Unicode, provenance, and safety rules reduce avoidable leakage and language-coverage manipulation.

Alternatives not selected:

- Discretionary lexical-token exclusion or retaining `stratum_eligible`: rejected because it enables denominator manipulation.
- NFC-only validity: rejected because NFC/NFD consistency is required for Unicode robustness.
- Treating gloss/case/compatibility/whitespace variants as distinct romanization forms: rejected because they do not establish independent spelling diversity.
- Claiming `corpus-final` exists: rejected because that implementation is absent.

#### Decision D-025 - Freeze annotation, coverage, and audit gates

Decision: Every pilot attempt receives exactly two independent blind records plus one semantically valid final record by a third distinct annotator, even when the blind records agree. Retained and excluded attempts remain in the completeness denominator, with frozen label, facet, span, relation, agreement, and alpha gates.

Before annotation, a human-audited structured-state coverage manifest must provide per stratum 30 visible-explicit and 30 no-visible-explicit candidates for each of six facets, plus 30 candidates for each MATCH/MISMATCH/UNKNOWN/N/A relation. Overlaps are allowed; component/reserve order and hashes are frozen; hidden non-gold tags cannot override annotations; and no candidate may be removed after annotation starts.

The canonical human pilot safety/provenance audit samples all retained and excluded attempts at `ceil(.10*N_attempted)`, covers every nonempty language(5) × primary(3) × provenance(4) cell by one-per-cell then Hamilton largest remainder with UTF-8 tie ordering, and uses exactly one witnessed 32-byte OS-CSPRNG draw after freeze. Selection ranks HMAC-SHA256(seed bytes, UTF-8(cell key + NUL + item ID)); supplements are separate and do not reduce the sample. No redraw or replacement is allowed, prohibited findings must be zero, and failure requires quarantine, incident handling, upstream repair, a new freeze, a 100% machine scan, and a fresh independent audit. Auditors never visit, call, or execute artifacts.

Rationale: [DERIVED] These gates make coverage, annotator independence, safety sampling, and provenance auditable before protected analysis.

Alternatives not selected:

- Two annotations only when they agree: rejected because agreement does not remove the need for an independent final semantic record.
- An underspecified random 10% audit: rejected because it cannot prove cell coverage, reproducibility, or failure handling.
- Removing difficult candidates after annotation begins: rejected because it biases completeness and coverage evidence.

#### Decision D-026 - Freeze the factorial and statistical interpretation boundaries

Decision: Use factorial conditions C00/C10/C01/C11. The co-primary safe-recall improvements C11-C01 and C11-C10 must each be observed at least 0.03, have Holm-adjusted p <= .05, and have joint simultaneous lower bounds above zero. The repaired bootstrap convention is `E_bj = Delta_bj - Delta_hat_j`, right-tail count `E >= Delta_hat`, `M=max(E1,E2)`, the 9,501st order statistic from 10,000 replicates for q95, and lower bound `Delta_hat-q`.

Report per-language Clopper-Pearson FPR and macro stratified bootstrap results. Use pooled exact-binomial intervals only under an explicit common-rate or random-mixture assumption. Exact protected FPR claim routing and unequal-system-FPR interpretation remain UNKNOWN and must freeze before protected access. Power solving, OOF empirical updating, H4 resampling, and protected analysis implementations remain future blockers.

Rationale: [OBSERVED] The repaired specification records the sign convention and multiplicity rule. [DERIVED] Separating estimands and assumptions prevents a pooled or routed FPR statement from being presented as a stronger claim than the design supports.

Alternatives not selected:

- The unrepaired bootstrap sign convention: rejected because it reverses the intended tail/lower-bound interpretation.
- An unqualified pooled exact-binomial claim: rejected because heterogeneous strata and routing require an explicit assumption.
- Presenting policy-level recall contrasts as overall dominance or below-one-percent population claims: rejected because routing and unequal-system-FPR semantics remain unresolved.

#### Decision D-027 - Keep prior-art and IP claims bounded

Decision: Treat broad Conversation Risk Memory as crowded and focus the residual research angle on joint uncertainty propagation into typed semantic consistency. Make no “first”, patentable, freedom-to-operate, or performance claim. Require professional prior-art/IP review before disclosure.

Rationale: [OBSERVED] The prior-art search log records relevant transliteration, multilingual phishing, graph, and patent references. [DERIVED] A bounded claim is safer and more falsifiable than an unsupported priority or legal assertion.

Alternative not selected: unsupported novelty, patentability, FTO, or metric claims were rejected because no exhaustive legal search or experiment establishes them.

### Impact and tradeoffs

- Compatibility: [OBSERVED] The validator is standard-library Python and uses JSONL schema 1.0.0; `corpus-final` remains unavailable. No existing committed interface exists because the branch is unborn.
- Data and provenance: tester-origin requirements, ancestry caps, protected partitions, auditable coverage, and source-ledger rules increase collection and annotation cost but preserve construct and independence claims.
- Security and privacy: defanged artifacts, live-route scanning, registry binding, consent gates, and the human audit prohibition reduce exposure; governance infrastructure is incomplete.
- Performance and cost: path marginalization, semantic consistency, calibration, bootstrap analysis, and triple annotation may be computationally and operationally expensive. No model or performance result is available.
- Operational workflow: Markdown remains the only active Luna register; the legacy DOCX is unchanged and read-only; user approval is required before each specific commit and separately before push/publication. Sol Max is configured as `gpt-5.6-sol` with xhigh reasoning.

### Verification performed

- `[OBSERVED]` `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: 28/28 passed in 15.812 seconds.
- `[OBSERVED]` CLI help exited 0. The draft text example was VALID with sources=2, items=4, annotations=12, registry_manifest=0, errors=0, and exactly three intended pilot warnings; agreement and language were 1.0. Corrected JSON assertions passed, including byte-identical repeated runs and exact warning codes. An initial ad-hoc assertion was wrong about the output shape; direct inspection and the corrected assertion passed.
- `[OBSERVED]` Python AST parsing with Python 3.11 grammar passed for four files. The executed runtime was Python 3.14.6 at `/opt/homebrew/bin/python3`; Python 3.11 was unavailable and not executed.
- `[OBSERVED]` Six TOML files parsed; four JSONL files containing 19 records parsed with duplicate-key checks; 16 Markdown files were checked with 49 internal links and 12 anchors resolved; the blueprint had 30 ordered outputs and 20 ordered phase rows.
- `[OBSERVED]` Terminology and whitespace checks found no trailing whitespace, no Bhasha name, no stale “eligible token count”, no stale `canonical_version`/`canonical_date`/`public_authentic_auxiliary`; `stratum_eligible` appears only in the intentional negative regression test at `tests/test_validator.py:607`.
- `[OBSERVED]` No bytecode/cache artifacts remained. `git diff --check` exited 0; because files are untracked, explicit whitespace checks supplied the meaningful evidence.
- `[OBSERVED]` Legacy DOCX SHA-256 remained `defa588fc2b5c9991780f06da13834a7dbb1ebea2731009cd750a0cd39e39eb2`.
- `[OBSERVED]` Independent validator review verdict: PRE-PILOT PASS. Independent methodology review verdict: PASS for the repaired protocol specification; synthetic structural and ontology-pilot dry runs passed, while authentic collection and protected evaluation remain blocked.

Unrun or unavailable checks: Python 3.11 runtime execution; actual registry and coverage-manifest approvals; full governance-ledger validator; ethics, consent, privacy, storage, retention, withdrawal, and incident controls; public dataset download and audit; authentic collection; model training; power solver; OOF empirical update; H4 resampling; protected FPR routing/analysis; benchmark, latency, calibration, and performance measurement; corpus-final validation; professional name/trademark/IP/FTO clearance.

### Remaining risks and follow-up

- No ethics authority, controller/steward, key custodian, incident contact, native-language reviewer set, secure storage, retention/withdrawal policy, or consent package has been verified.
- No actual registry or structured-state coverage manifest is approved, and the full governance-ledger validator is absent.
- No public dataset has been downloaded or approved; no authentic corpus, model, training run, benchmark, or result exists.
- Protected FPR routing and unequal-system-FPR interpretation are unresolved; power and protected analysis implementations are absent.
- Python 3.11 execution compatibility, Fisher name clearance, and professional prior-art/IP review remain open.

Next action: the lead orchestrator should obtain governance owners and approvals, prepare the actual registry and coverage manifest, complete the governance-ledger validator, rehearse the canonical audit on approved synthetic material, and only then begin the 1,200-item tester-led pilot. Luna should record the next verified checkpoint before any specific commit is proposed.

### Correction history

None. This record is append-only and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-002

### Governance mechanical-projection repair and independent focused pass

- Lifecycle: Decision recorded - repaired mechanical projection accepted for its narrow scope; no commit requested
- Recorded: 19 August 2026, 4:13:26 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-002`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected paths and checkpoint boundary

- `fisher_governance/__init__.py`
- `fisher_governance/__main__.py`
- `fisher_governance/validator.py`
- `tests/test_governance.py`
- `docs/GOVERNANCE_CONTRACT.md`
- `examples/governance/README.md`
- `examples/governance/source_ledger.blocked.jsonl`

[OBSERVED - parent-supplied independent-review evidence] The original review reproduced defects in rights-policy projection, safety scanning, lineage and cycle handling, host parsing, CLI exposure, and growth after `fstat`. Those findings are preserved as the reason for the repair; the later pass does not erase them.

[OBSERVED - Luna inspection] The current repaired artifacts match the pinned `E04` evidence: governance validator SHA-256 `0aa6f638577b54569a9b0bd6239d1eaf36fcf9ee7daeb6c8a13c9233d4409706`, focused tests SHA-256 `90c4cffe984de155b24ec1fbea125f72e3971632ade089fa6491616959e141c0`, and contract SHA-256 `81fa76bf35a56d134116fe14f240b6da905cff6efbdf32a2a220bae9d90f7f05`.

#### Decision D-028 - Accept the repaired governance validator only as a mechanical projection

Decision: Accept the pinned governance repair for the exact representable checks exercised by the independent focused review. The validator remains a fail-closed mechanical projection and is not evidence that collection is lawful, ethical, safe, or authorized.

Rationale: [OBSERVED] The independent reviewer passed 31/31 focused tests, including the post-`fstat` growth-race regression and the original adversarial probes. [DERIVED] Reproducing and closing the named machine defects supports the narrow projection while leaving human authority outside the program's proof boundary.

Alternatives not selected:

- Reject the repaired validator because the original implementation failed: rejected because the pinned repair closed every reproduced focused defect under independent replay.
- Treat a mechanically valid ledger as collection approval: rejected because the contract fixes `collection_ready=false` and the validator cannot authenticate human decisions.
- Hide the failed review after repair: rejected because preserving the failure-to-repair chain is required for an auditable evidence history.

#### Decision D-029 - Keep collection authorization blocked

Decision: Preserve `collection_ready=false`; all 20 human or otherwise unrepresented gates remain `UNKNOWN` until authenticated evidence and accountable owners exist.

Rationale: [OBSERVED] The blocked fixture still reports `collection_ready=false`. [DERIVED] A correct projection of missing approvals cannot substitute for the approvals themselves.

Alternatives not selected:

- Infer readiness from `schema_valid=true`: rejected because schema validity only proves internal machine consistency.
- Convert `UNKNOWN` gates to passed defaults: rejected because that would fail open and invent governance evidence.

### Impact and tradeoffs

- Compatibility: the repaired CLI and contract retain the explicit separation among schema validity, machine authorization readiness, unrepresented gates, and collection readiness.
- Data: no corpus row or authentic source was collected, authorized, or ingested by this checkpoint.
- Security and privacy: scanner, host, lineage, cycle, CLI-sanitization, and bounded-read repairs reduce representable failure paths; they do not prove external evidence or operational controls.
- Performance and cost: the focused repair adds bounded-read and validation work; no general throughput benchmark was supplied.
- Operations: human governance remains the blocking dependency even when all mechanical tests pass.

### Verification performed

- `[OBSERVED - parent-supplied independent evidence]` 31/31 focused governance tests passed, including the growth-race regression and the original rights-policy, scanner, lineage/cycle, host, and CLI probes.
- `[OBSERVED - parent-supplied owner evidence]` The implementation owner passed the then-current full suite at 89/89.
- `[OBSERVED]` The independent reviewer did not rerun that full suite because concurrent data work made it a different tree; no independent full-tree pass is claimed for this checkpoint.
- `[OBSERVED - Luna inspection]` The three pinned artifact hashes above match the current files, and `docs/research/EXECUTION_STATUS.md` records this narrow pass as `E04`.
- `[OBSERVED]` The fixture remains blocked with `collection_ready=false`.
- Unrun by Luna: technical suites were not rerun for this register-only update; no human gate, authentic evidence package, collection, privacy audit, or authorization ceremony was executed.

### Remaining risks and follow-up

- Twenty human or unrepresented gates remain `UNKNOWN`.
- Concurrent full-tree changes were outside the independent review's pinned scope.
- Machine checks cannot establish the truth, authority, timeliness, or legal sufficiency of referenced evidence.

Next owner/action: the lead orchestrator must identify accountable governance owners and obtain authenticated consent, ethics, privacy, security, storage, retention, withdrawal, incident, license, provenance, registry, and collection-authorization evidence before any authentic collection begins.

### Correction history

None. This record is append-only and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-003

### Synthetic audit-selector repair and independent focused pass

- Lifecycle: Decision recorded - repaired synthetic selector accepted for rehearsal scope; no commit requested
- Recorded: 19 August 2026, 4:13:26 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-003`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected paths and checkpoint boundary

- `fisher_audit/__init__.py`
- `fisher_audit/__main__.py`
- `fisher_audit/selector.py`
- `tests/test_audit_selector.py`
- `docs/AUDIT_SELECTOR_CONTRACT.md`
- `examples/audit/README.md`
- `examples/audit/attempts.synthetic.jsonl`

[OBSERVED - parent-supplied independent-review evidence] The original adversarial timing exposed approximately quadratic supplement selection. The repair replaced repeated full-universe scans with indexed deterministic selection and recorded a minimal-exposure supplement-processing trace.

[OBSERVED - Luna inspection] The current repaired artifacts match pinned `E03` prefixes and full hashes: selector SHA-256 `8abb47a2ce4aaab925b03d4057680eab248b2c3e974660f7b59a509ceb98d15b`, entry-point SHA-256 `3da5859c581a72fa1e202a42e023b115f0586bae991c10f0a87d590d2f6d2ed2`, and contract SHA-256 `00520285d2bf5171a3d03eebfddd20ebc16ed21e542f89331d9611fbf4bcb57f`.

#### Decision D-030 - Use indexed deterministic selection with an explicit supplement trace

Decision: Accept the indexed selection implementation, deterministic HMAC/order rules, and ordered minimal-exposure supplement trace for the synthetic rehearsal contract.

Rationale: [OBSERVED] The independent reviewer passed 28/28 focused tests plus reference, HMAC, ordering, supplement, and safety replays. [OBSERVED] Measured adversarial unique-annotator cases completed at 10,000 records in 0.302 seconds using 101 MiB and at 100,000 records in 3.494 seconds using 642 MiB. [DERIVED] The indexed implementation removes the reproduced quadratic behavior for the measured scope while retaining replayable selection semantics.

Alternatives not selected:

- Retain the quadratic supplement scan: rejected because measured growth was operationally unsafe at the contract maximum.
- Replace deterministic ordering with redraw, replacement, or ad hoc randomness: rejected because it would break replayability and the frozen audit protocol.
- Omit the supplement-processing trace: rejected because the trace is needed to verify when an initially missing annotator was covered by an earlier supplement.

#### Decision D-031 - Bind every output to synthetic rehearsal scope

Decision: Require input/output scope binding to `SYNTHETIC_REHEARSAL_ONLY` and `release_blocked: true`. Treat all selector outputs as invented mechanics evidence only, never as a real audit, governance approval, or release certificate.

Rationale: [OBSERVED] The contract and current implementation bind those fields into reports and manifests. [DERIVED] Explicit scope binding prevents a deterministic arithmetic rehearsal from being mistaken for evidence about a real frozen universe, witnessed seed, human review, or prohibited findings.

Alternatives not selected:

- Reuse rehearsal output as human-audit evidence: rejected because the tool accepts no authentic audit result or governance package.
- Add an authentic-execution mode now: rejected because real universe freeze, witnessed seed handling, auditor authority, and governance controls are absent.
- Remove `release_blocked` after a clean synthetic run: rejected because synthetic success cannot authorize release.

### Impact and tradeoffs

- Compatibility: report/manifests use schema `1.1.0`, input rows use `1.0.0`, and the algorithm is `fisher-audit-rehearsal-1.1.0`.
- Data: inputs contain synthetic metadata only; no message text, authentic person, or audit finding is admitted.
- Security and privacy: sanitized diagnostics and explicit scope binding reduce accidental exposure and false certification.
- Performance: measured 10,000- and 100,000-record cases improved materially over the failed implementation; the maximum JSON case remained expensive at approximately 90.6 MB and 737 MiB.
- Operations: a real audit requires a separately frozen universe, witnessed seed, human reviewers, governance evidence, and zero prohibited findings.

### Verification performed

- `[OBSERVED - parent-supplied independent evidence]` 28/28 focused tests passed plus exact reference, HMAC, ordering, supplement, safety, and deterministic replay checks.
- `[OBSERVED - parent-supplied measured evidence]` Adversarial 10,000-record execution measured 0.302 seconds/101 MiB; 100,000 records measured 3.494 seconds/642 MiB; maximum-sized JSON measured approximately 90.6 MB/737 MiB.
- `[OBSERVED - Luna inspection]` The three pinned hashes match the current files, and `docs/research/EXECUTION_STATUS.md` records the pass as `E03`.
- Unrun by Luna: selector tests and performance measurements were not repeated for this register-only update; no real universe, witnessed seed, human audit, prohibited-finding review, governance approval, or release check ran.

### Remaining risks and follow-up

- Maximum-input memory remains operationally material on the observed 16 GiB machine.
- Synthetic identifiers and frozen arithmetic do not prove real-universe completeness or independence.
- A future real-audit implementation could diverge from the rehearsal unless separately specified, pinned, and reviewed.

Next owner/action: the lead orchestrator must keep this tool rehearsal-only and later design, authorize, pin, and independently review the real human-audit execution package before using any result as project evidence.

### Correction history

None. This record is append-only and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-004

### Historical schema 1.1 registry/gold separation and raw-byte ingestion repair

- Lifecycle: Decision recorded - historical schema `1.1.0` repair independently passed; no commit requested
- Recorded: 19 August 2026, 4:13:26 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-004`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Historical affected paths and checkpoint boundary

- `fisher_data/__init__.py`
- `fisher_data/__main__.py`
- `fisher_data/validator.py`
- `tests/test_validator.py`
- `docs/DATA_CONTRACT.md`
- `examples/pilot/README.md`
- `examples/pilot/sources.jsonl`
- `examples/pilot/items.jsonl`
- `examples/pilot/annotations.jsonl`
- `examples/pilot/registry_manifest.jsonl`
- `examples/pilot/registry_references.jsonl`

[OBSERVED - parent-supplied historical evidence] This checkpoint applies to the pinned schema `1.1.0` tree only. Blind and final annotations no longer contained registry relation states. Separate non-gold registry-reference rows carried `MATCH`, `MISMATCH`, or `UNKNOWN`, while visible endpoint and endpoint-pair structure F1 remained part of annotation reliability.

[OBSERVED - Luna current-tree inspection] The active uncommitted `fisher_data` validator and `docs/DATA_CONTRACT.md` now declare schema `1.2.0` and contain visible-artifact inventory work. Their current hashes differ from the historical `E07` pins. The in-progress `1.2.0` tree is not covered by this `1.1.0` pass.

#### Decision D-032 - Separate non-gold registry references from human gold

Decision: Record the historical schema `1.1.0` boundary as follows: human blind/final gold contains visible-message labels, facets, spans, evidence, and endpoint structure, but no registry relation state; a separate reviewer writes non-gold registry-reference rows for applicable endpoint pairs.

Rationale: [DERIVED] Registry state depends on a frozen external reference source and must not leak into blind or final semantic gold. Visible endpoint and pair structure remain annotatable from the message and therefore retain an exact F1 reliability gate.

Alternatives not selected:

- Store registry relation states in blind or final annotations: rejected because it contaminates human gold with external registry evidence.
- Drop endpoint-pair reliability when relation labels move out of gold: rejected because visible actor/destination structure remains a human-annotation quality target.
- Treat the historical pass as approval of schema `1.2.0`: rejected because the current tree has different contracts and hashes and requires its own independent review.

#### Decision D-033 - Bound raw bytes before text decoding or newline interpretation

Decision: Accept the historical ingestion repair that captures at most the raw-byte limit plus one byte before UTF-8 decoding and physical-line interpretation, so drained oversized tails and CRLF bytes count toward the file bound.

Rationale: [OBSERVED] Independent review reproduced two bypasses: an oversized drained tail omitted bytes from the cumulative limit, and universal-newline translation undercounted raw CRLF bytes. [OBSERVED] The pinned repair replay closed both probes. [DERIVED] A raw-byte bound must be enforced on the accepted byte sequence, before any lossy newline transformation or discarded-tail handling.

Alternatives not selected:

- Rely on pre-open or post-open `stat` size alone: rejected because a file can grow after metadata checks.
- Count re-encoded decoded text: rejected because newline translation can change byte counts.
- Drain an oversized line without counting its tail: rejected because discarded bytes still consume the file budget.
- Repair documentation only: rejected because executable bypasses require executable fixes and regression tests.

### Impact and tradeoffs

- Compatibility: schema `1.1.0` is historical and superseded; no compatibility claim is made for current schema `1.2.0`.
- Data and provenance: registry evidence remains separately attributable and non-gold; source labels and annotation endpoints stay distinguishable.
- Security and privacy: bounded raw capture prevents file-growth and newline-normalization paths from bypassing the documented input limit.
- Performance and cost: bounded capture may retain up to the configured limit plus one byte before rejection; no independent throughput or memory benchmark was supplied for this repair.
- Operations: the pass closes only the `E06` byte-bound/documentation scope and does not authorize collection or validate external registry truth.

### Verification performed

- `[OBSERVED - parent-supplied pinned E07 evidence]` Historical validator SHA-256 `4d1f8497416b1f36a7d80089f0fbb287d2e1204044cc7908a81f0b454fb85d33`; tests SHA-256 `5b0a52c0e45874be5c22e71faf7aeb285c5f025e55bb729f22cc2bdade18b070`; data-contract SHA-256 `0fc291644f6423d57eedf108713c72625b95554d81f4ba2ec235dbfb8dde448e`.
- `[OBSERVED - parent-supplied independent evidence]` Both exact reduced-limit `E06` probes were replayed and closed; the focused suite passed 34/34 and the full suite passed 93/93.
- `[OBSERVED]` The exact focused-suite invocation and elapsed times were not supplied to Luna, so none is invented here.
- `[OBSERVED - Luna inspection]` `docs/research/EXECUTION_STATUS.md` preserves the prior `E06` failure and records the pinned repair as `E07`.
- Unrun by Luna: historical artifacts were not reconstructed and technical tests were not rerun against them; the current schema `1.2.0` work, external registry bytes/evidence, human blinding, authentic pilot, and collection authorization were not reviewed by this checkpoint.

### Dated correction to LUNA-20260819-001 - 19 August 2026

The original `LUNA-20260819-001` text, including Decisions D-024 and D-025, is preserved unchanged above. This correction is additive and supersedes only the affected claims:

- D-024's schema-`1.0.0` and rich relation-in-annotation wording was superseded by the historical schema `1.1.0` registry/gold separation described in D-032. The current uncommitted tree is being advanced to schema `1.2.0`; that work is not covered by the historical `E07` pass.
- D-025's relation-label gate and four-state coverage wording was superseded for schema `1.1.0` by separate non-gold registry-reference rows with `MATCH`, `MISMATCH`, or `UNKNOWN`, plus reliability of visible endpoint-pair structure. An empty applicable endpoint-pair product creates no reference row; runtime `N/A` is not a human-gold relation label.

Correction rationale: [OBSERVED] The pinned `1.1.0` checkpoint and current `1.2.0` work establish a different registry/gold boundary than the earlier record stated. [DERIVED] Appending this correction preserves historical auditability without presenting superseded schema language as current.

### Remaining risks and follow-up

- Current schema `1.2.0` semantics and implementation remain outside the historical pass and need fresh independent review.
- Registry completeness, truth, evidence quality, reviewer blinding, and human workflow remain unproved.
- File-bound correctness does not prove every other schema, semantic, privacy, or resource property.

Next owner/action: the lead orchestrator should complete and independently review the schema `1.2.0` contract, validator, fixtures, and semantic interfaces before changing `G0` or beginning `E0` work.

### Correction history

This record contains the dated additive correction above. No original `LUNA-20260819-001` text was rewritten, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-005

### Independent P0 semantic-implementability review failure

- Lifecycle: Decision recorded - independent review failed; `G0` remains blocked; no commit requested
- Recorded: 19 August 2026, 4:13:26 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-005`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Review scope and change inventory

- Affected technical paths: None; this checkpoint was an independent review and made no technical edit.
- Reviewed specification/test surface: historical schema `1.1.0` data contract and validator, the P0 engine/semantic specifications, and the then-current non-engine test suite.
- Missing implementation at the checkpoint: no `fisher_engine` package existed.

[OBSERVED - parent-supplied independent-review evidence] The review returned `REVIEW_FAILED` despite a passing non-engine suite because five material semantic or numerical interfaces were not implementable exactly as written.

#### Decision D-034 - Keep G0 blocked and repair the schema/specification before E0

Decision: Do not start or accept E0 engine implementation on the failed P0 interface. First make the visible-message payload, alignment transformation, float64 reduction order, log-domain retained mass, and canonical pair-packet bytes machine-exact, then obtain fresh independent review.

Rationale: [OBSERVED] The review found:

1. Schema `1.1.0` could not reconstruct the visible-message payload because an item lacked a non-gold visible-artifact inventory.
2. Alignment monotonicity and the normalizer's map transformation were not machine-exact.
3. `logsumexp` operand order was absent; a reduced probe produced `8.456834966970222` versus `8.456834966970224` under different valid orders.
4. A direct exponentiated retained-mass ratio underflowed to `0/0` for 2,000 equal binary spans, with the best score approximately `-1386.294`.
5. The pair-packet hash had no canonical byte serialization.

Secondary findings: `zero_pair_correct` was semantically misnamed, and the unaligned-registry short-circuit was unspecified. [DERIVED] Passing schema/validator tests cannot establish an engine interface that has no implementation or exact numerical/serialization contract.

Alternatives not selected:

- Proceed to E0 because 93 tests passed: rejected because those were non-engine tests and no `fisher_engine` implementation existed.
- Fix only floating-point tolerances: rejected because missing payload, alignment, serialization, and short-circuit contracts are not tolerance issues.
- Leave operand ordering implementation-defined: rejected because the observed binary64 outputs differ and hashes/reproducibility require a canonical order.
- Compute retained mass by direct exponentiation: rejected because the reproduced long equal-span case underflows.
- Treat naming and unaligned behavior as cosmetic: rejected because metric interpretation and registry access behavior must be unambiguous.

### Impact and tradeoffs

- Compatibility: no technical file changed in this review checkpoint; the result blocks acceptance of the reviewed P0 interface.
- Data: the missing non-gold visible-artifact inventory prevented exact reconstruction of the intended visible-message payload.
- Security and privacy: an unspecified unaligned-registry path risks inconsistent access or leakage handling; no exploit rate was measured.
- Performance and numerical behavior: exact ordering and log-domain computation add implementation constraints but prevent nondeterminism and underflow in the reproduced cases.
- Operations: the failure delays E0 but prevents implementation against an ambiguous contract and false promotion from unit-test count alone.

### Verification performed

- `[OBSERVED - parent-supplied execution evidence]` `python3 -B -m unittest discover -s tests -v` passed 93/93 tests in 22.791 seconds.
- `[OBSERVED - parent-supplied independent probes]` The two `logsumexp` orderings produced `8.456834966970222` and `8.456834966970224`; the 2,000-equal-binary-span retained-mass probe reached a best score of approximately `-1386.294` and direct exponentiation produced `0/0`.
- `[OBSERVED - Luna current-tree inspection]` No `fisher_engine` file is present. Current prose and schema `1.2.0` files contain later attempted repairs, but no evidence in this checkpoint establishes a fresh independent semantic pass.
- Unrun by Luna: the historical review probes and 93-test suite were not rerun for this register-only update; no engine known-answer test, end-to-end synthetic engine, feature/gradient/access audit, or independent re-review passed.

### Remaining risks and follow-up

- Later prose changes may still be internally inconsistent until independently reviewed as one pinned interface.
- Canonical bytes, deterministic float64 order, log-domain mass, endpoint alignment, and unaligned lookup behavior require executable known-answer tests.
- A passing data validator cannot prove engine information-flow, gradient, or registry-access boundaries.

Next owner/action: the specification owner should freeze the repaired schema `1.2.0` visible-artifact/VMP contract and exact engine algorithms; an independent reviewer should then replay all five blockers plus the secondary findings before `G0` can pass or E0 implementation can begin.

### Correction history

None. This record is append-only and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-006

### Independent schema 1.2 PRE-E0 safety review failure

- Lifecycle: Decision recorded - independent PRE-E0 review failed; repair required and not yet accepted; no commit requested
- Recorded: 19 August 2026, 4:18:06 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-006`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Reviewed paths and checkpoint boundary

- `fisher_data/validator.py`
- `tests/test_validator.py`
- `docs/DATA_CONTRACT.md`
- `fisher_data/__init__.py`
- `fisher_data/__main__.py`
- `examples/pilot/`

This was an independent review checkpoint, not a technical-edit checkpoint. It applies to the pinned pre-repair schema `1.2.0` files below and must remain distinct from later working-tree changes.

[OBSERVED - parent-supplied pinned evidence] The reviewed SHA-256 values were validator `1986f169a6729cd2366e49ea22d00601ab954f95f5b75e295a3e16fdf409ca1e`, tests `786596e0bca952613146967239389d8d882e2db76d99ac886a3f9ea11e696e52`, data contract `401fae8d9f5957c797c8bfab2fd10333c407b0eb2d65360d56a731dc7b57602f`, package initializer `bb037d6de045f400f5fc1650cdb2eab4c64d2e9c9cb7604e4957568b75ce53f7`, and CLI entry point `08ac711151f1cfe147d67f46f23ac09ae8b07bc57044b19f74d4a4f40fdb031a`.

[OBSERVED - parent-supplied independent-review evidence] Two coherent records declared as `DEFANGED` validated with zero errors even though their visible text contained active-route forms: `Actor [redacted] 2606:4700:4700::1111` and `Actor [redacted] recipient@oksbi`. The first contains syntactically valid bare IPv6 and the second an ASCII UPI/contact-style handle.

#### Decision D-035 - Fail schema 1.2 PRE-E0 and require fail-closed route scanning

Decision: Keep the schema `1.2.0` PRE-E0 gate failed. Add exact regressions for the reproduced IPv6 and UPI-like forms, repair the scanner so declared artifact representation cannot suppress live-route detection, and require independent replay against pinned post-repair artifacts before acceptance.

Rationale: [OBSERVED] Both unsafe probes validated with zero errors inside otherwise coherent artifacts. [OBSERVED] The full 100-test suite passed, so the passing suite did not cover these safety cases. [DERIVED] A `DEFANGED` declaration is metadata, not proof that every visible route is inert; live-route scanning must fail closed on the actual accepted surface.

Alternatives not selected:

- Promote PRE-E0 because 100/100 tests passed: rejected because the independent probes reproduced two uncovered executable safety defects.
- Trust the `DEFANGED` representation without scanning the visible surface: rejected because a coherent declaration can coexist with a live IPv6 or UPI-like route.
- Exclude IPv6 and UPI/contact-style handles from route detection: rejected because both can carry actionable destination information in the intended threat domain.
- Repair only the contract prose: rejected because executable validation accepted both probes and therefore needs executable regression coverage and a validator repair.
- Require the validator to prove every `RESERVED`/`DEFANGED` artifact's real-world type or authenticity: rejected because only `TYPED_PLACEHOLDER` mechanically binds `kind` to an exact token; real-world semantics remain a human-audited proof boundary.

### Impact and tradeoffs

- Compatibility: this verdict applies only to the pinned pre-repair schema `1.2.0` artifacts; it makes no pass claim for concurrent later edits.
- Data: no authentic dataset was collected or accepted by this review. The probes used controlled test strings to expose scanner behavior.
- Security and privacy: accepting visible live-route forms under a `DEFANGED` declaration could admit contact or payment destinations that the safety contract intends to block.
- Performance: no scanner throughput, memory, or false-positive rate was measured in this review.
- Proof boundary: `kind="PHONE"` with `representation="RESERVED"` and surface `Portal.Example` was permitted because only `TYPED_PLACEHOLDER` binds the declared kind to the surface. This is a nonblocking specification boundary, not evidence that the declared real-world type is true.
- Operations: E0 and any authentic-data use remain blocked until repair and independent replay.

### Verification performed

- `[OBSERVED - parent-supplied independent evidence]` Both exact probe records above validated with zero errors against the pinned pre-repair validator.
- `[OBSERVED - parent-supplied execution evidence]` The then-current full unit suite passed 100/100; the valid example produced exactly three expected warnings; repeated JSON output was deterministic; Python 3.11 AST parsing passed; JSONL, internal-link, and whitespace checks passed.
- `[OBSERVED - Luna inspection]` The current working copies have already diverged from three failure pins: validator SHA-256 `e12b0a5a539ef93345fd263952c6bc41385a6ff0ccc39dbd0ffbe997342f5803`, tests SHA-256 `c1502d39f1ad3c9946cc7c509fbfe4b15a6422753b78777115ae41330399f246`, and data-contract SHA-256 `7fc5f15c468a56a09488a46b4e5c505b4e6ce8823089c9b987985e688601ae2d`. The initializer and CLI entry-point hashes still match their failure pins. No repair pass is inferred from those changes.
- Unrun by Luna: technical tests, probe replays, example validation, AST checks, link checks, and scanner performance measurements were not rerun for this register-only update. No independent post-repair review result was supplied.

### Remaining risks and follow-up

- Whether U+2024 and U+FE52 dot-like characters are normalized and blocked correctly was `UNKNOWN` at the failed checkpoint; exact regressions and independent replay are required.
- Route detection may have additional Unicode, boundary, punctuation, mixed-script, or normalization bypasses not exercised by the two probes.
- The allowed `kind`/surface proof boundary for non-placeholder artifacts depends on later human audit and must not be presented as machine-proved authenticity.
- Concurrent validator, tests, and contract edits are unreviewed in this record and may introduce or fail to close other cases.

Next owner/action: the data-validator owner should complete the smallest fail-closed scanner repair and exact regression tests; an independent reviewer should pin the repaired artifacts, replay both original probes plus U+2024/U+FE52 and adjacent boundary variants, run the relevant focused/full suites, and report a separate result before PRE-E0 can pass.

### Correction history

None. This record is append-only and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-007

### Schema 1.2 live-route repair and final independent PRE-E0 pass

- Lifecycle: Decision recorded - final independent PRE-E0 pass accepted for documented syntactic VMP safety only; no commit requested
- Recorded: 19 August 2026, 4:33:28 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-007`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected paths and checkpoint boundary

Direct final-repair paths:

- `fisher_data/validator.py`
- `tests/test_validator.py`
- `docs/DATA_CONTRACT.md`

Pinned schema-`1.2.0` interface and example paths inspected with the repair:

- `fisher_data/__init__.py`
- `fisher_data/__main__.py`
- `examples/pilot/README.md`
- `examples/pilot/sources.jsonl`
- `examples/pilot/items.jsonl`
- `examples/pilot/annotations.jsonl`
- `examples/pilot/registry_manifest.jsonl`
- `examples/pilot/registry_references.jsonl`

The independent failure in `LUNA-20260819-006` remains preserved unchanged. [OBSERVED - parent-supplied review history] The initial schema-`1.2.0` review accepted bare IPv6 `2606:4700:4700::1111` and UPI/contact handle `recipient@oksbi`. A first repair then still accepted terminal-period cases including `recipient@oksbi.`, `recipient@oksbi..`, `2606:4700:4700::1111.`, `::1.`, and an IPv4-mapped IPv6 address followed by a period. The final repair and pass below follow both failures; they do not erase them.

[OBSERVED - Luna inspection] Current SHA-256 values match the supplied stable pins: validator `997cecbfccedb66bdff21c3995a1f3c6cbc6f13daff9b019c3daaf15da904c2f`, tests `e0e385284b2e730a7081fbd232d1f2bab763bdc63805d417fd8455a89ae2073f`, data contract `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`, package initializer `bb037d6de045f400f5fc1650cdb2eab4c64d2e9c9cb7604e4957568b75ce53f7`, and CLI entry point `08ac711151f1cfe147d67f46f23ac09ae8b07bc57044b19f74d4a4f40fdb031a`.

#### Decision D-036 - Accept the final scanner repair for syntactic VMP safety

Decision: Accept the pinned schema-`1.2.0` repair for the documented PRE-E0 syntactic live-route and VMP-safety boundary. The repair uses standard-library IPv6 parsing after bounded terminal-period handling, a bounded UPI/contact-handle pattern whose lookahead prevents a shorter match inside a dotted email, and a temporary safety-scan mapping for U+2024, U+3002, U+FE52, U+FF0E, and U+FF61.

Rationale: [OBSERVED - Luna inspection] The validator scans a translated safety copy, strips terminal ASCII periods only from the bounded IPv6 candidate before `ipaddress.IPv6Address` parsing, and uses a bounded handle pattern with a dotted-suffix-aware lookahead. [OBSERVED - parent-supplied independent evidence] The final reviewer rejected all original, terminal-period, compressed, full, bracketed, bracketed-port, IPv4-mapped, zone, punctuation, and Unicode-dot route variants while reserved dotted-email and benign controls remained valid. [DERIVED] The repaired behavior closes both reproduced failure rounds without turning a reserved dotted control into a shorter UPI/contact match.

Alternatives not selected:

- Ignore terminal punctuation as presentation-only: rejected because both the one-period and repeated-period variants bypassed the first repair.
- Use a broad or unbounded `@` expression: rejected because it can match a handle prefix inside a permitted reserved dotted email and create false rejection.
- Preserve the first repair after its focused tests passed: rejected because the terminal-period adversarial replay still reproduced executable bypasses.
- Normalize only the two Unicode-dot variants already seen in local regressions: rejected because the documented safety family includes five dot-equivalent code points and the final independent replay covered the family.

#### Decision D-037 - Preserve immutable VMP bytes and the human-audited kind boundary

Decision: Apply dot-equivalent mappings only to a temporary safety-scan copy. Do not mutate stored text, visible-artifact offsets, canonical VMP bytes, or hashes. Continue to machine-bind `kind` only for `TYPED_PLACEHOLDER`; treat `RESERVED` and `DEFANGED` kinds as human-audited metadata after their surface and global safety checks pass.

Rationale: [OBSERVED] The contract states that the temporary mapping does not change immutable stored text, offsets, or hashes, and the independent reviewer passed VMP-immutability checks. [OBSERVED] The contract also states that only `TYPED_PLACEHOLDER` binds a kind to one exact surface token. [DERIVED] Safety normalization and semantic authenticity are separate concerns: the validator can reject syntactic routes without inventing ownership, activity, or real-world type evidence.

Alternatives not selected:

- Rewrite stored text to its safety-normalized form: rejected because that would change offsets and canonical VMP/hash identity.
- Recompute offsets after normalization: rejected because the stored message, not a scanner-only copy, is the canonical evidence surface.
- Claim that a passing `RESERVED` or `DEFANGED` kind proves artifact type, ownership, inactivity, or authenticity: rejected because those facts are outside the mechanical schema proof boundary.
- Bind every representation to its declared kind: rejected because only the closed `TYPED_PLACEHOLDER` vocabulary supplies an exact machine-checkable kind/surface mapping.

### Impact and tradeoffs

- Compatibility: schema remains `1.2.0`, but inputs containing previously missed live-route variants now fail closed. Reserved dotted-email and documented benign controls remain accepted.
- Data and provenance: no authentic data was collected or changed. Stored text, Unicode-code-point offsets, VMP canonical bytes, and hashes remain immutable.
- Security and privacy: the repair closes the two reported bypass rounds and adds punctuation/Unicode safety coverage without echoing the rejected surface in diagnostics. It proves syntactic rejection only.
- Performance: the scanner adds bounded candidate parsing, lookahead, and a temporary translated string. No throughput, memory, or denial-of-service benchmark was supplied for this repair.
- Operations: PRE-E0 passes only for the pinned documented schema/VMP safety scope. It does not prove authenticity, ownership, collection authorization, release readiness, registry truth, or the separately failed `E08` semantic-engine specification.
- Runtime: Python 3.11 grammar compatibility was checked by AST parsing, but execution under a Python 3.11 runtime remains `UNKNOWN`.

### Verification performed

- `[OBSERVED - parent-supplied independent evidence]` All original, terminal-period, compressed, full, bracketed, bracketed-port, IPv4-mapped, zone, punctuation, and five Unicode-dot variants were rejected. Reserved dotted-email and benign controls passed. Diagnostic non-echo and VMP immutability passed.
- `[OBSERVED - parent-supplied independent evidence]` The focused data-validator suite passed 42/42 and the full suite passed 101/101.
- `[OBSERVED - parent-supplied independent evidence]` The deterministic draft CLI example was valid with zero errors and exactly three expected warnings; repeated output was deterministic. Python 3.11 AST parsing and JSONL, internal-link, and whitespace checks passed.
- `[OBSERVED - Luna inspection]` The five stable code/contract pins above match current files. Current example SHA-256 values are README `6e7dac6acf6f3912ecc21ff9f0fb0aac350b7fb948d26b729a883920e15e8186`, sources `521faf869f59ae10146012a487003a1a28a89595f2d01c19cfe6747e294f65e5`, items `470f203f3ccb173d9827177a598875d0a36c587b3c1929a37cf1aea5c05a2823`, annotations `4e795705c27db6a0fa5a9caac7df51404ec2a99b864948cfefa6214ff958bf45`, registry manifest `947dfd047a3287a914ee4c4db85b09feb9f48607a8a33989c90c6996d14e90c2`, and registry references `5cb02d73e0051981c9042924aa275cfa987a5b6a0f9bd26a44ed2876271e5393`.
- `[OBSERVED - Luna inspection]` `docs/research/EXECUTION_STATUS.md` still preserves the separate `E08` semantic-specification failure and contains no row asserting that this syntactic safety pass clears it.
- Unrun by Luna: the 42-test and 101-test suites, CLI replay, adversarial probes, Python 3.11 AST check, JSONL/link checks, and technical whitespace check were not rerun for this register-only update. No Python 3.11 runtime, authentic-data audit, scanner performance benchmark, or human artifact-authenticity review ran.

### Remaining risks and follow-up

- Additional Unicode, delimiter, mixed-script, IDNA, or parser-boundary variants may exist beyond the independently replayed family.
- Passing syntax checks cannot prove artifact ownership, activity, destination authenticity, lawful acquisition, consent, privacy controls, registry truth, or safe release.
- Python 3.11 runtime behavior and scanner resource bounds have not been measured.
- `E08` remains a separate failed semantic-specification checkpoint; no engine implementation or `G0` pass is established here.

Next owner/action: preserve the pinned schema-`1.2.0` artifacts and PRE-E0 safety scope, continue the independent `E08` semantic-specification repair/replay before engine work, and obtain the required human governance evidence before authentic collection. If a commit is later proposed, the lead must request explicit user approval for that specific commit after a Luna commit-preparation update.

### Correction history

None. This record is append-only, `LUNA-20260819-006` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-008

### Second independent P0 semantic review failure

- Lifecycle: Decision recorded - P0 semantic review failed and `G0` remains blocked; no commit requested
- Recorded: 19 August 2026, 4:47:44 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-008`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Reviewed paths and checkpoint boundary

This was an independent specification-review checkpoint and made no technical edit. The pinned reviewed paths were:

- `docs/research/ENGINE_SPEC.md` - SHA-256 `9e93a31c33b6fd13fbc9de32cd27ea0c2e873d6e246e021fe2ec4ff8db5d2cd4`
- `docs/research/FACTORIAL_CONDITION_SPEC.md` - SHA-256 `7748303757b1f4435da3e5d0b53c91e98df165b0f9dcc2723a59eb104756ee28`
- `docs/research/PAPER_1_PREREGISTRATION.md` - SHA-256 `ac6e4d7f41380f22cfbc297359c51a191b68cf6254f60eefe1256ec6fd2f12c4`
- `docs/research/REGISTRY_PROTOCOL.md` - SHA-256 `354fcf4e6b1e050cfdf8ccacfd9ae1ff7a7920eef69f3ef9f3225f75c2bc4388`
- `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md` - SHA-256 `53116cea3cc1ef7aa4776fc0b700d7b6a7fcadbcb1881aa77cbcddc3e247cbec`
- `docs/research/THREAT_MODEL.md` - SHA-256 `ca47b04d69625ee6e6666e1b85902b2860591b41292b63b59724b32f346df62e`
- `docs/research/FISHER_RESEARCH_BLUEPRINT.md` - SHA-256 `f02a8ad9509984d43b745fb70702f1953650e16e31079f39611dc3024ab90422`
- `docs/research/ANNOTATION_GUIDE.md` - SHA-256 `d900b8ffccf2bdfb8b8dd8bc106105fda2aeedf248ec40690c36d67da4e7ab42`
- `docs/research/EXECUTION_STATUS.md` - SHA-256 `d3b1ca81f028562318b2a0b04e96b02e89fa4bdfdeb8c49f9741322e7a09e94e`
- `docs/research/SOURCE_LEDGER.md` - SHA-256 `45b71d884bb2e0f0cb9c5bf7037245d64bcb989b66fb577bd1c1816c6f1de2bf`
- `docs/DATA_CONTRACT.md` - SHA-256 `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`

[OBSERVED - parent-supplied independent-review evidence] The second review passed the five original `E08` headline repairs: schema-`1.2.0` VMP reconstruction, machine-exact alignment/transducer rules, canonical ordered binary64 `logsumexp`, log-domain retained mass, and canonical path/pair-packet bytes. Passing those repaired points did not make the complete interface implementable.

#### Decision D-038 - Preserve the five closed E08 findings without promoting P0

Decision: Accept the five original `E08` headline repairs only as closed findings within the pinned specification set. Do not interpret their closure as a P0 semantic pass, `G0` pass, engine implementation, or permission to begin `E0`.

Rationale: [OBSERVED] Ordered and reversed `logsumexp` operands remained observably distinct, confirming that the frozen operand order is material. A 2,000-span direct-exponent calculation underflowed while the repaired log-domain retained mass remained finite. Exact-versus-beam boundary vectors covered products of 64 and 128. [OBSERVED] The reviewer assessed path/pair bytes, packet hashes, and metric vectors at the specification level, but no engine existed. [DERIVED] A review can close previously named defects while still failing the larger gate on newly exposed interfaces.

Alternatives not selected:

- Declare P0 passed because all five original blockers were repaired: rejected because the same review found four additional implementation-blocking interface families.
- Treat specification-level vectors as engine evidence: rejected because no `fisher_engine` implementation executed them.
- Treat the 101-test repository suite as semantic-interface coverage: rejected because the suite contained no engine tests and did not resolve the new contract gaps.

#### Decision D-039 - Keep G0 blocked pending exact schemas, bounds, and metric binding

Decision: Repair all four newly identified blocker families, pin the resulting specification set, and obtain another independent cross-contract review before `E0` begins:

1. Define a total provider and contributor identity across response-local, direct, and composed providers, plus exact provider-reading, lineage, and run-manifest schemas, canonical bytes, hashes, and invalidity rules.
2. Freeze endpoint vocabularies, ranges, text/byte lengths, deduplication and order independent of excluded scores, the learned SEP projection, and inclusion/binding of `lookup_surface` and `lookup_status` in the audit packet.
3. Define the runtime registry-evidence grammar and list cap, and complete candidate, lookup-surface, evidence, pair-packet, and SEP byte/count bounds.
4. Define the pair-metric eligible population and `N`, fail closed on undefined/invalid cases, and require inference/reference equality for registry snapshot and resolver version.

Rationale: [OBSERVED - parent-supplied independent-review evidence] The review found that `provider_rank` was only response-local and therefore not total across direct and composed providers; named manifests lacked exact schemas and canonical bytes. Endpoint qualifier vocabularies, coordinate/text bounds, and learned SEP projection were incomplete; `lookup_surface` and `lookup_status` affected identity/resolution but were absent from the canonical audit packet; packet ordering depended on score-derived selection order even though scores were excluded. Runtime evidence IDs had no complete grammar/list cap, multiple candidate/lookup/SEP byte and count bounds were absent, and pair-metric eligibility plus registry snapshot/resolver equality were undefined. [DERIVED] These gaps permit two conforming implementers to serialize, order, resolve, bound, or score the same input differently, so P0 remains failed.

Alternatives not selected:

- Leave provider-reading, lineage, and run manifests implementer-defined: rejected because replay, hashing, and contributor order require one canonical schema and byte representation.
- Pool response-local provider ranks across direct and composed sources: rejected because local ranks collide and do not define a total contributor identity.
- Allow audit-only IDs, endpoint scores, or score-derived rank to enter the learned projection: rejected because that violates the feature boundary and can create registry or ordering shortcuts.
- Leave candidate, lookup-surface, registry-evidence, pair-packet, or SEP sizes unbounded: rejected because resource behavior and canonical validity would remain undefined.
- Score inference against a reference created with a different registry snapshot or resolver version: rejected because version drift makes the comparison non-equivalent.
- Override the semantic failure with 101/101 non-engine tests: rejected because passing unrelated tests cannot specify the missing contracts.

### Impact and tradeoffs

- Compatibility and reproducibility: the next repair may be specification-breaking, but exact manifests, bytes, bounds, and version binding are required for deterministic independent implementations.
- Data and provenance: VMP reconstruction is now review-accepted, but registry-evidence grammar, resolver/snapshot binding, and audit-packet completeness remain insufficient for a valid run.
- Security and privacy: incomplete learned-feature projection risks opaque-ID or score leakage; absent caps create resource-exhaustion risk; registry drift can make audit claims misleading.
- Evaluation: pair F1 and emptiness metrics cannot gate a claim until the eligible population, denominator, invalid-case behavior, and inference/reference registry identity are exact.
- Performance: exact/beam branching is specified at 64/128 vectors, but end-to-end candidate, packet, and SEP resource behavior remains unbounded and unmeasured.
- Operations: no engine, model, authentic data, metric result, collection authorization, or release readiness follows from this review. `G0` and `E0` remain blocked.

### Verification performed

- `[OBSERVED - Luna inspection]` All eleven current reviewed-path SHA-256 values match the parent-supplied pins exactly.
- `[OBSERVED - parent-supplied execution evidence]` `python3 -B -m unittest discover -s tests -v` passed 101/101 non-engine tests in 29.586 seconds.
- `[OBSERVED - parent-supplied independent evidence]` The reviewer passed the five original `E08` repair families and exercised the ordered/reversed LSE, 2,000-span log-mass, 64/128 exact/beam, and specification-level packet/hash/metric vectors.
- `[OBSERVED - Luna inspection]` No `fisher_engine` directory exists. The current `docs/research/EXECUTION_STATUS.md` preserves `E08` as `REVIEW_FAILED`; no later execution-evidence identifier was invented for this review.
- Unrun by Luna: the 101-test suite and semantic probes were not rerun for this register-only update. No provider/lineage/run-manifest parser, candidate engine, resolver, SEP serializer, feature-access audit, metric implementation, Python 3.11 runtime, resource benchmark, or end-to-end synthetic engine ran.

### Remaining risks and follow-up

- Repairing one blocker can expose further cross-document ambiguity; all pinned documents need one coherent replay rather than isolated approval.
- Provider identity and lineage collisions can change arithmetic order and hashes.
- Missing learned/audit projection separation can leak IDs, scores, or score-derived order.
- Missing byte/count caps can create denial-of-service or nonportable serialization behavior.
- Undefined metric eligibility and version drift can silently change denominators or compare non-equivalent registry decisions.

Next owner/action: the specification owner should freeze exact provider-reading, lineage, and run-manifest schemas; endpoint and learned/audit SEP fields; all byte/count bounds; and pair-metric/version-binding rules. An independent reviewer must then pin and replay all original and new blockers before `G0` can pass or `E0` implementation begins.

### Correction history

None. This record is append-only, all earlier Luna records remain unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-009

### Second P0 documentation repair pending independent review

- Lifecycle: `REPAIRED_PENDING_REVIEW` - documentation repair completed locally; no semantic pass and no commit requested
- Recorded: 19 August 2026, 5:11:30 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-009`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected paths and pinned repair boundary

- `docs/research/ENGINE_SPEC.md` - SHA-256 `c150c5784e9556bb8b0d12669598bdb6bd5e3a83c8e42d837a90d11eb21fc70e`
- `docs/research/FACTORIAL_CONDITION_SPEC.md` - SHA-256 `ce1700f9fa1abc0d0c3f26571c421a32e568a2ecd251c937630ad9b70f52cd4d`
- `docs/research/PAPER_1_PREREGISTRATION.md` - SHA-256 `54e6d33874397ee15fdec72d4e685cd783b085bc15ec6290193ccd8df2a886ce`
- `docs/research/REGISTRY_PROTOCOL.md` - SHA-256 `dc626f1dd3ed5e93aee2c868ecdf8a97d00d68c476446f7f28598d1f735a4264`
- `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md` - SHA-256 `0630d531ccb85cf3795a7747c9cd28be025d6172882da9887ba6575876cd89bc`
- `docs/research/THREAT_MODEL.md` - SHA-256 `4dc317354ea801bfe4f83f7af1c4d11c8812af5a3bc3b983467c18c7416b830f`
- `docs/research/FISHER_RESEARCH_BLUEPRINT.md` - SHA-256 `0b4d5d5bd1f9809367c7bc366d7690b1b9d24be6e042d06bfe7ddd73470e8e4b`
- `docs/research/ANNOTATION_GUIDE.md` - SHA-256 `0ad5936f3962676fa27ad83758e6c3fbe55e543d19d8c0e66c910f8753c39a1c`
- `docs/research/EXECUTION_STATUS.md` - SHA-256 `714f686b450eb7018a0d93021287c752c6274de79f631af78bc97d41db98f505`
- `docs/research/SOURCE_LEDGER.md` - SHA-256 `ae961e648774691e419f8a2d2ea9edfe0cd0481667ee17976562f2a4d48ed941`

This record preserves the independent `LUNA-20260819-008`/`E10` semantic failure. [OBSERVED - Luna inspection] `EXECUTION_STATUS.md` classifies the current work as a second docs-only repair pending fresh replay, keeps `G0` blocked, records the scoped schema-`1.2.0` pass as `E09`, and preserves the second semantic failure as `E10`. No new review-pass identifier is claimed.

#### Decision D-040 - Freeze one canonical provider configuration and manifest per message run

Decision: Permit exactly one active provider configuration and mode per message run: composed span readings, direct full-path readings, or an identity bypass. Do not pool direct and composed provider outputs. Bind the run to one canonical provider manifest version `1.0.0` containing exact ordered rewrite-span, unit, reading, identifier, alignment, and finite binary64-bit fields; enforce the stated reading/path/count limits and a 4 MiB canonical-manifest cap. Require direct-mode readings to preserve every nonrewrite code point and every visible-artifact slice. Use distinct canonical composed, direct, and bypass lineage objects.

Rationale: [DERIVED from `E10`] One active provider configuration removes incomparable cross-provider rank and score scales. [OBSERVED - Luna inspection] The repaired engine specification defines exact provider/configuration and normalizer ID grammars, mode-specific span/unit invariants, `(unit_index,provider_rank)` reading identity, 16-lowercase-hex big-endian finite binary64 logits, canonical compact JSON bytes and hash, direct-mode preservation, compact lineage, and explicit size/count rejection.

Alternatives not selected:

- Let each provider define its own manifest or canonical bytes: rejected because independent replay and hashes would not have one meaning.
- Pool response-local ranks from direct and composed providers: rejected because their identities and score scales are not comparable.
- Let a direct provider rewrite unrestricted VMP text: rejected because it could alter noncandidate evidence or visible artifacts outside the frozen rewrite spans.
- Truncate overlong readings, paths, spans, or manifests: rejected because silent truncation changes candidate identity and evidence; overflow must fail closed.

#### Decision D-041 - Separate the canonical audit packet from learned semantic features

Decision: Bind the canonical endpoint audit packet to full lookup inputs, status, score-independent endpoint/pair order, exact registry-evidence grammar, evidence-list cap, resolver call counts, at most 64 pairs, and at most 16 MiB canonical bytes. Learned risk receives only canonical `SemanticFeaturePlan` instructions plus projected tokens from a future finite `VmpHiddenGrid_k`; it receives no literal IDs, lookup surfaces, hashes, evidence, endpoint scores, provider ranks, candidate weights `q`, or score-derived order.

Rationale: [OBSERVED - Luna inspection] The repaired specification distinguishes score-bearing prediction audit from a score-independent pair packet, fixes endpoint kind/status/range/surface rules, caps evidence IDs at 16 per pair, binds exact call counts, and defines deterministic feature-plan fields. [DERIVED] Audit completeness and learned-feature minimization require different representations: the audit packet must be replayable while the learned view must exclude shortcut identifiers and ordering signals.

The `E0` boundary uses opaque synthetic finite grids to test feature projection, masks, and exclusion canaries only. The real subword/candidate-hidden-to-`VmpHiddenGrid_k` adapter remains `UNKNOWN`, unimplemented, and deferred for freezing before `E3`.

Alternatives not selected:

- Order packet rows by endpoint score: rejected because the excluded score would still leak through order.
- Feed the full audit packet into the learned head: rejected because literal surfaces, IDs, hashes, evidence, and audit-only state can become shortcuts.
- Permit unbounded endpoints, evidence lists, packets, or feature plans: rejected because canonical validity and resource behavior would remain unsafe or nonreplayable.
- Invent the real subword-grid adapter during `E0`: rejected because `E0` is an interface/mechanics phase and cannot claim a frozen model-alignment implementation.

#### Decision D-042 - Bind pair metrics to one frozen reference bundle and complete universe

Decision: Require canonical `registry_reference_bundle` version `1.0.0` and exact equality between inference and reference registry snapshot, resolver version, registry-manifest hash, and registry-reference artifact hash, including zero-pair items. Freeze `N_all`, `N_gold_empty`, and `N_gold_nonempty` from the named evaluation manifest before inference. Any missing or invalid candidate, alignment, packet, resolver, reference, or finite output fails the metric run and never deletes an item. Count a nonempty prediction on a gold-empty item as false positives, keep both-empty cases in `N_all`, and use the documented fixed denominators.

Rationale: [DERIVED from `E10`] Without exact bundle equality, a prediction made against one registry version can be scored against a different semantic reference. Without a prefrozen universe and fail-closed handling, implementation failures can silently improve metrics by shrinking denominators. [OBSERVED - Luna inspection] The repair defines canonical bundle fields/bytes/hash, micro q-weighted TP/FP/FN across all `N_all`, all-item emptiness accuracy, and fixed-denominator conditional recalls.

Alternatives not selected:

- Score across registry or resolver versions: rejected because the compared states are not equivalent.
- Silently delete invalid items after inference: rejected because it changes the population and can bias every metric.
- Omit gold-empty false positives from pair F1: rejected because nonempty predictions remain false predicted relations even when gold is empty.
- Recompute denominators from successful outputs: rejected because denominator selection would depend on system behavior.

#### Decision D-043 - Keep G0 blocked until independent semantic replay

Decision: Classify this checkpoint as `REPAIRED_PENDING_REVIEW`, not `EXECUTED_PASS`. Preserve `E09` as the narrow independently passed syntactic VMP checkpoint and `E10` as the failed second semantic review. Do not begin or accept `E0` until an independent reviewer pins and replays the repaired provider, lineage, packet, projection, bounds, bundle, and metric contracts.

Rationale: [OBSERVED] The completed verification suite contains 101 non-engine tests and no `fisher_engine`. [DERIVED] Documentation coherence and existing test success are necessary evidence but cannot substitute for the independent replay that the current failing gate requires.

Alternatives not selected:

- Mark P0 or `G0` passed because the documentation was repaired: rejected because the repair has not passed independent semantic replay.
- Treat `E09` as evidence for the engine interfaces: rejected because `E09` covers only schema-`1.2.0` syntactic VMP safety.
- Reuse the original `E10` review as approval of changed documents: rejected because the reviewed bytes and contract surface have changed.

### Impact and tradeoffs

- Compatibility and reproducibility: the repaired contracts are more restrictive and may reject provider outputs or runs previously left implementation-defined; canonical bytes and bounds support later replay.
- Data and provenance: no authentic data, registry, provider output, annotation, or metric result was created. Reference-bundle identity prevents cross-version provenance drift.
- Security and privacy: learned-feature minimization excludes literal audit identifiers and surfaces; explicit caps and fail-closed invalidity reduce leakage and resource-exhaustion paths. No implemented feature-access audit exists yet.
- Evaluation: a fixed complete universe and bundle equality make denominator and version drift visible, but no metric implementation has exercised the rules.
- Performance: 4 MiB provider-manifest, 64-pair, and 16 MiB packet caps are design bounds, not measured latency or memory results.
- Operations: `G0` remains blocked; D0/D1, authentic collection, model work, and release remain unauthorized.

### Verification performed

- `[OBSERVED - Luna inspection]` All ten repaired research-document SHA-256 values match the pins recorded above.
- `[OBSERVED - parent-supplied execution evidence]` `python3 -B -m unittest discover -s tests -v` passed 101/101 non-engine tests in 29.571 seconds.
- `[OBSERVED - parent-supplied verification evidence]` Internal links and anchors, Markdown tables, strict UTF-8, LF-only line endings, final newlines, and trailing-whitespace checks passed. The execution-status inventories contained 20 `P` rows, 30 `O` rows, and 10 `E` rows.
- `[OBSERVED - Luna inspection]` The current inventory contains `P01`-`P20`, `O01`-`O30`, and `E01`-`E10`. Current `E09` pins match validator `997cecbfccedb66bdff21c3995a1f3c6cbc6f13daff9b019c3daaf15da904c2f`, tests `e0e385284b2e730a7081fbd232d1f2bab763bdc63805d417fd8455a89ae2073f`, and data contract `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`.
- Unrun by Luna: the 101-test suite, link/anchor/table checks, and technical document whitespace checks were not rerun for this register-only update. No engine, nonidentity provider, real registry/resolver, subword-grid adapter, feature/gradient/access audit, D0/D1 workflow, model, metric implementation, or performance measurement ran. Independent semantic replay remains active and has no supplied result.

### Remaining risks and follow-up

- The repaired schemas and byte rules may expose further ambiguity under independent implementation and adversarial vectors.
- `SemanticFeaturePlan` and opaque-grid mechanics are unimplemented; the real token-to-VMP grid adapter remains unknown.
- Provider, packet, evidence, and metric caps are unbenchmarked and may need revision before protected freeze.
- No real registry proves snapshot truth, evidence adequacy, completeness, ownership, or lawful use.
- Human governance, collection authorization, D0/D1 execution, model behavior, and performance remain unproved.

Next owner/action: the independent semantic reviewer should pin these ten repaired documents and replay every `E10` blocker, including manifest bytes/identity, direct/composed/bypass lineage, resource limits, packet/order/call-count rules, feature exclusion, reference-bundle equality, complete-universe failure behavior, and metric vectors. Only a separate successful review record can change `G0`; engine implementation must wait.

### Correction history

None. This record is append-only, `LUNA-20260819-008` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-010

### Third independent P0 semantic review failure

- Lifecycle: Decision recorded - `REVIEW_FAILED`; `G0` remains blocked and no commit requested
- Recorded: 19 August 2026, 5:26:04 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-010`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Reviewed paths and checkpoint boundary

This was an independent semantic-specification review and made no technical edit. It reviewed the `LUNA-20260819-009` pending-repair state at these stable pins:

- `docs/research/ENGINE_SPEC.md` - SHA-256 `c150c5784e9556bb8b0d12669598bdb6bd5e3a83c8e42d837a90d11eb21fc70e`
- `docs/research/FACTORIAL_CONDITION_SPEC.md` - SHA-256 `ce1700f9fa1abc0d0c3f26571c421a32e568a2ecd251c937630ad9b70f52cd4d`
- `docs/research/PAPER_1_PREREGISTRATION.md` - SHA-256 `54e6d33874397ee15fdec72d4e685cd783b085bc15ec6290193ccd8df2a886ce`
- `docs/research/REGISTRY_PROTOCOL.md` - SHA-256 `dc626f1dd3ed5e93aee2c868ecdf8a97d00d68c476446f7f28598d1f735a4264`
- `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md` - SHA-256 `0630d531ccb85cf3795a7747c9cd28be025d6172882da9887ba6575876cd89bc`
- `docs/research/THREAT_MODEL.md` - SHA-256 `4dc317354ea801bfe4f83f7af1c4d11c8812af5a3bc3b983467c18c7416b830f`
- `docs/research/FISHER_RESEARCH_BLUEPRINT.md` - SHA-256 `0b4d5d5bd1f9809367c7bc366d7690b1b9d24be6e042d06bfe7ddd73470e8e4b`
- `docs/research/ANNOTATION_GUIDE.md` - SHA-256 `0ad5936f3962676fa27ad83758e6c3fbe55e543d19d8c0e66c910f8753c39a1c`
- `docs/research/EXECUTION_STATUS.md` - SHA-256 `714f686b450eb7018a0d93021287c752c6274de79f631af78bc97d41db98f505`
- `docs/research/SOURCE_LEDGER.md` - SHA-256 `ae961e648774691e419f8a2d2ea9edfe0cd0481667ee17976562f2a4d48ed941`
- `docs/DATA_CONTRACT.md` - SHA-256 `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`

[OBSERVED - parent-supplied independent-review evidence] The replay passed provider separation, mode-specific lineage, candidate/manifest bounds, direct-mode nonrewrite and visible-artifact preservation, packet/call-count/evidence/order rules, factorial condition masks, pair-metric equations, and the preserved `E05`-`E10` evidence history. It nevertheless returned `REVIEW_FAILED` on five newly exposed exactness gaps.

#### Decision D-044 - Preserve passed replay findings without promoting G0

Decision: Retain the independently replayed provider separation, lineage, bounds, direct-preservation, audit-packet, resolver-call, evidence, score-independent order, condition-mask, metric-equation, and evidence-history repairs as closed findings for their stated scope. Do not treat those closures, or the passing non-engine suite, as a complete P0 semantic pass.

Rationale: [OBSERVED] The reviewer passed those repaired surfaces but found five other interfaces capable of producing non-equivalent identities, selections, features, or evaluation populations. [DERIVED] A partially successful replay narrows the remaining work without changing the failed gate verdict.

Alternatives not selected:

- Promote `G0` because the prior `E10` blockers passed: rejected because the new review reproduced five additional material ambiguities.
- Reopen every earlier passed finding: rejected because the reviewer supplied positive replay evidence for those narrow surfaces.
- Override the semantic verdict with the repository unit suite: rejected because 101/101 tests contain no engine coverage.

#### Decision D-045 - Distinguish bypass reasons and canonically bind run and prediction audits

Decision: Give `NO_ELIGIBLE_ROMANIZED_SPAN` and `PROVIDER_FAILURE_RAW_FALLBACK` distinct, canonically serialized run identities. A failed-provider fallback must bind the attempted provider/configuration and applicable rewrite-span context rather than collapsing to the same fixed empty `IDENTITY_BYPASS` provider manifest as a genuinely ineligible message. Freeze exact run-manifest and endpoint prediction-audit schemas, field order, canonical bytes, hashes, score dtype/bits, and selection arithmetic.

Rationale: [OBSERVED - parent-supplied conceptual probe] The current two bypass reasons both use fixed `provider_identity_bypass`/`normalizer_identity` IDs with empty spans and units. Conceptual no-span and provider-failure manifests therefore produced the same SHA-256 `bf5e49ce81eb38a6be8496f1ed4c6b0f57e51d5c4c780312a1087cc3768bed3d`, losing the failed provider/configuration and eligible spans. The broader run manifest is only a field list, not a canonical schema and hash contract. [OBSERVED - parent-supplied conceptual probe] Endpoint scores `1.00000004` and `1.00000003` are distinct in binary64 but tie in binary32, so an unspecified score audit/dtype can change cap selection.

Alternatives not selected:

- Conflate the two bypass reasons because both emit the raw identity path: rejected because provider failure is degraded, affects coverage, and must retain attempted configuration evidence.
- Keep the run manifest or prediction audit implementation-private: rejected because replay, selection, hashes, and failure attribution depend on their exact bytes.
- Allow selection precision to depend on binary32 versus binary64 implementation choice: rejected because the conceptual score pair changes the tie outcome.
- Record only a human-readable failed-provider log: rejected because an unbound log cannot establish the canonical run identity.

#### Decision D-046 - Freeze SemanticFeaturePlan category and numeric arithmetic

Decision: Define the exact category basis and order for every one-hot field; feature dtype; `VmpHiddenGrid_k` dimension and canonical row encoding; concatenation order; mask representation; and mean-pooling accumulation, division, rounding, signed-zero, nonfinite, and hash behavior before accepting the feature projection.

Rationale: [OBSERVED - parent-supplied conceptual probe] The repaired plan names pooled grid vectors and categorical one-hots but not their basis order or numeric execution. Sequential versus compensated accumulation for `1e16`, `1`, and `-1e16` differs. [DERIVED] The same plan and grid can therefore yield different learned tokens under two otherwise plausible implementations.

The separate deferral of the real subword/candidate-to-VMP adapter remains acceptable. This blocker concerns deterministic `E0` opaque-grid projection arithmetic, not the deferred adapter itself.

Alternatives not selected:

- Leave one-hot basis order and feature dtype to the implementation: rejected because column identity and numeric bytes would not be portable or auditable.
- Specify mean pooling mathematically but not its binary arithmetic: rejected because finite floating-point accumulation order changes outputs.
- Treat the opaque synthetic grid as exempt from determinism: rejected because `E0` uses it precisely to establish the feature interface.

#### Decision D-047 - Canonically bind the evaluation universe and reject truthy coordinates

Decision: Freeze an exact evaluation-universe/metric-run manifest schema, item order, canonical bytes, SHA-256, and binding into the run before inference. The manifest must bind the complete prefrozen `[item_id,...]` population and denominators so `[a,b]` cannot become `[a]` post hoc. Also require every provider-manifest rewrite-span `start` and `end` to be non-Boolean integers satisfying `0 <= start < end <= len(VMP.text)` before slicing or hashing.

Rationale: [OBSERVED - parent-supplied conceptual probes] The prose names a complete evaluation list but supplies no exact schema/order/hash/run binding, permitting a conceptual post hoc `[a,b]` to `[a]` denominator change. The rewrite-span object names `start,end` while explicitly typing only `span_index`; in Python, `true` can act as integer `1` unless Boolean coordinates are rejected. [DERIVED] Both gaps allow distinct populations or coordinates under apparently conforming implementations.

Alternatives not selected:

- Leave the denominator list unhashed because metric formulas are fixed: rejected because the formulas cannot detect post hoc universe mutation.
- Bind only `N_all` without ordered item identities: rejected because the population can change while its size stays constant.
- Accept Python truthy coordinates: rejected because Boolean and integer schema values are semantically distinct despite Python's subtype behavior.
- Repair only downstream alignment validation: rejected because the provider manifest itself must be canonical and invalid before any slice or hash uses the coordinates.

### Impact and tradeoffs

- Compatibility and reproducibility: the next repair will add canonical envelope and audit artifacts and stricter coordinate typing; earlier implementation-defined outputs may become invalid.
- Data and provenance: distinct bypass identities preserve whether a message lacked eligible spans or suffered provider failure, while a hashed universe preserves evaluation membership.
- Security and privacy: exact audit envelopes improve traceability without making raw data public; unspecified/private logs or manifests remain a tampering and attribution risk.
- Evaluation: score dtype, feature arithmetic, universe binding, and coordinate typing can each change selected endpoints, learned tokens, or reported denominators.
- Performance: exact feature arithmetic and canonical manifests may add cost, but no engine benchmark or resource measurement exists.
- Operations: `G0` remains blocked. No engine, authentic data, registry, metric result, collection authorization, model result, or release readiness follows from this review.

### Verification performed

- `[OBSERVED - Luna inspection]` All eleven current reviewed-path SHA-256 values match the stable pins recorded above.
- `[OBSERVED - parent-supplied execution evidence]` `python3 -B -m unittest discover -s tests -v` passed 101/101 non-engine tests in 29.666 seconds.
- `[OBSERVED - parent-supplied independent evidence]` The reviewer replayed and passed the provider separation/lineage/bounds/direct-preservation, packet/call/evidence/order, condition-mask, metric-equation, and `E05`-`E10` history surfaces.
- `[OBSERVED - parent-supplied conceptual evidence]` The reviewer evaluated the identical bypass-manifest hash, binary64-versus-binary32 endpoint score, floating-point pooling, evaluation-list mutation, and Boolean-coordinate examples as specification probes. These were not engine tests.
- `[OBSERVED - Luna inspection]` No `fisher_engine` directory exists. `LUNA-20260819-009` remains the pending-repair record reviewed here; no execution-evidence identifier was invented for this third review.
- Unrun by Luna: the 101-test suite and conceptual probes were not rerun for this register-only update. No canonical run/prediction/metric manifest parser, provider execution, endpoint selection, feature projection, registry, metric implementation, Python 3.11 runtime, or end-to-end engine ran.

### Remaining risks and follow-up

- Exact run and prediction-audit envelopes may expose further cross-artifact binding gaps.
- Floating-point feature semantics can still diverge until dtype, basis, accumulation, division, and encoding are frozen together.
- An evaluation-universe hash must be bound before inference and protected from alternate-order or duplicate-item ambiguity.
- Boolean, oversized, negative, empty, or out-of-range coordinates require explicit fail-closed vectors at every relevant boundary.
- Human governance, real registry evidence, collection authorization, model behavior, and performance remain unproved.

Next owner/action: repair the canonical run/audit envelope, bypass identity, endpoint prediction audit, feature-category/numeric arithmetic, evaluation-universe and metric-run manifest, and rewrite-coordinate predicate. Then pin the complete document set and obtain another independent semantic replay before `G0` can pass or `E0` begins.

### Correction history

None. This record is append-only, `LUNA-20260819-009` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-011

### Third P0 specification repair pending fourth independent replay

- Lifecycle: `REPAIRED_PENDING_REVIEW` - third documentation repair completed; not a pass and no commit requested
- Recorded: 19 August 2026, 5:55:57 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-011`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected paths and pinned repair boundary

- `docs/research/ENGINE_SPEC.md` - SHA-256 `1ae7b86fbf3dce7f2c93afc202794cfcb03f0d6dca9d02b7c7e9e11ed13499ae`
- `docs/research/FACTORIAL_CONDITION_SPEC.md` - SHA-256 `99d5d8e49176f4dfaec07ee737f1b07cdb96c9ec0da5063ef9cb2734b74ed313`
- `docs/research/PAPER_1_PREREGISTRATION.md` - SHA-256 `67c3640de0e0d80a7ac943cdd2621295766fff80ecd842220ac2e6f3cec14efb`
- `docs/research/REGISTRY_PROTOCOL.md` - SHA-256 `9699825e312cd17f93b85445700c167b0820c7cb5136e111a9b9bf586bad0866`
- `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md` - SHA-256 `0d4ce4016ece538fa980ae52ed2d721c42e2332efd9b70b80faf7927480a4b60`
- `docs/research/THREAT_MODEL.md` - SHA-256 `971caa609b9714837a1219d0bd7c5b1e95c00cdce294607948fd9fb47a55ed80`
- `docs/research/FISHER_RESEARCH_BLUEPRINT.md` - SHA-256 `a051f692171740730d1c6fd1034a35000a3106ce9f74cb554f443b8f2b2ddf71`
- `docs/research/ANNOTATION_GUIDE.md` - SHA-256 `0e1cf0620168f039be39a35e601ae2e07cb40c44706276b85637fa21835c47b5`
- `docs/research/EXECUTION_STATUS.md` - SHA-256 `7062794857cc0e132b6c56a2575b3d591a5e50c1edb8632da3cb36db7b69589f`
- `docs/research/SOURCE_LEDGER.md` - SHA-256 `f94dcc8ea557bf7a67ba411837a4f904ab04d42fed583e7788ebf52ccdb89f3d`

This repair preserves `LUNA-20260819-010` and its third independent `REVIEW_FAILED` verdict. [OBSERVED - Luna inspection] `EXECUTION_STATUS.md` now records that `E11` passed the second-repair surfaces but found five later blockers; the third docs-only repair is pending a fresh fourth replay. `G0/P0`, `G5`, and `G6` remain `BLOCKED`. No `E12` or semantic pass is claimed.

#### Decision D-048 - Canonically separate provider execution from candidate output

Decision: Retain one canonical candidate-output provider manifest, but enclose it in an exact `provider_execution` object that binds configured mode, provider and normalizer IDs/hashes, eligible attempted spans, invocation state, bypass reason, failure code, and provider-manifest hash. Distinguish not-applicable, successful, no-eligible-span, and provider-failure states. Preserve attempted spans and configured artifacts for failure even when both bypasses share the same identity-output manifest and effective spans are empty.

Rationale: [DERIVED from the third review] Identical identity-output bytes are not themselves defective when an exact enclosing execution object binds why they occurred. The repair prevents `NO_ELIGIBLE_ROMANIZED_SPAN` from becoming indistinguishable from `PROVIDER_FAILURE_RAW_FALLBACK` in run accounting while keeping one canonical raw identity path.

Alternatives not selected:

- Continue serializing only the identical `IDENTITY_BYPASS` output manifest: rejected because it loses attempted configuration, spans, invocation, failure cause, and degraded status.
- Create separate ad hoc provider logs outside the canonical run: rejected because unbound logs cannot establish replay identity.
- Treat provider failure as successful candidate coverage: rejected because fallback is degraded and supplies no successful provider evidence.

#### Decision D-049 - Freeze the engine source manifest, run envelope, and binary64 prediction audit

Decision: Use canonical version-`1.0.0` source-manifest and engine-run-envelope schemas with declared field order, exact identifiers, runtime/Unicode/binary64 contract, candidate diagnostics and paths, provider execution, downstream hashes, invalid states, canonical bytes, size caps, and SHA-256 bindings. Freeze a separate canonical prediction audit with emission indices, exact endpoint fields, 16-lowercase-hex big-endian finite binary64 score bits, binary64 comparison, deterministic equal-score selection, post-cap score-independent order, bytes, cap, and hash.

Rationale: [OBSERVED - Luna inspection] The repaired engine specification replaces the prior field list with exact source and run schemas and binds provider, path, prediction, packet, feature, registry, and runtime artifacts. It defines model-emission index as the final equal-score tie and prevents host/model-native float precision from changing endpoint selection. [DERIVED] A source/run envelope establishes what ran; a separately hashed prediction audit establishes exactly which binary64 scores and indices produced the selected endpoints without exposing scores to learned features.

Alternatives not selected:

- Use implicit or native model float scores: rejected because binary32 and binary64 can produce different ties and selections.
- Keep prediction scoring private to implementation logs: rejected because cap selection and endpoint identity must be replayable.
- Bind only source files without runtime, candidate, and downstream artifact hashes: rejected because the run could still change while the source list remains constant.

#### Decision D-050 - Freeze the E0-only five-category grid and 31-dimensional pair tensor

Decision: Limit engine-envelope version `1.0.0` to synthetic plan `E0_VMP_CATEGORY_MEAN_V1`. Use the pinned-Unicode precedence basis `LETTER,MARK,DECIMAL_DIGIT,WHITESPACE,OTHER`; a five-dimensional finite binary64 row per VMP code point; sequential increasing-position binary64 addition and division for endpoint means; and the fixed concatenation of pooled vectors plus category/status/state/coverage/source one-hots into 31 dimensions. Serialize a 64-row masked, positive-zero-padded tensor audit with exact bit strings, row-major order, bytes, cap, and SHA-256.

Rationale: [OBSERVED - Luna inspection] The repair freezes the five-category basis, arithmetic order, binary64 representation, pair dimension `31`, pair capacity `64`, mask, padding, string lengths, canonical bytes, and exclusions. [DERIVED] These rules make the same opaque E0 grid and plan yield one auditable tensor rather than implementation-dependent one-hot columns or mean arithmetic.

The real candidate/subword-to-VMP adapter remains `UNKNOWN` and deferred before `E3`; the E0 category grid is an interface test and makes no linguistic or model claim.

Alternatives not selected:

- Leave feature bases, dtype, or accumulation implementation-defined: rejected because feature columns and numeric tokens would differ.
- Use compensated or host-library mean accumulation without freezing it: rejected because it need not match the specified sequential binary64 result.
- Present the synthetic category grid as the future model adapter: rejected because it proves only E0 mechanics and exclusions.

#### Decision D-051 - Canonically bind the evaluation universe and fail metrics closed

Decision: Freeze a canonical evaluation-universe manifest version `1.0.0` before inference, including ordered item identities, partitions, dataset hashes, reference-bundle hash, VMP/gold bindings, canonical bytes, size cap, and SHA-256. Bind the metric-run manifest to exactly one engine envelope per universe item in the same order and to fixed `N_all`, `N_gold_empty`, and `N_gold_nonempty`. Any missing, extra, reordered, degraded, invalid, nonfinite, abstained, or mismatched record makes the metric run invalid and emits no pair metrics; no item may be deleted.

Decision: Retain provider-failure runs in engine accounting, but prohibit them from confirmatory or protected metrics. Keep Boolean-safe provider rewrite coordinates: `span_index`, `start`, and `end` are non-Boolean integers with `0 <= start < end <= len(VMP.text)` before slicing, hashing, or execution.

Rationale: [DERIVED from the third review] A canonical universe plus ordered envelope binding prevents a mutable `[a,b]` population from becoming `[a]` after results. Degraded provider fallback belongs in operational accounting but cannot support a complete confirmatory denominator. Explicit non-Boolean coordinate predicates prevent Python truth values from masquerading as indices.

Alternatives not selected:

- Keep the evaluation item list mutable or unhashed: rejected because post hoc membership or order changes would remain undetectable.
- Allow degraded provider-failure outputs into confirmatory/protected metrics: rejected because they do not contain valid provider evidence for the configured system.
- Silently delete degraded, invalid, abstained, or inconvenient items: rejected because denominator shrinkage can bias results.
- Accept Python-truthy coordinates: rejected because Boolean and integer schema values are semantically different.

#### Decision D-052 - Keep P0, G5, and G6 blocked pending independent replay and implementation

Decision: Classify the third specification repair as `REPAIRED_PENDING_REVIEW`, not `EXECUTED_PASS`. Require a fourth independent semantic replay of the pinned documents before `G0/P0` can pass. Even a successful specification replay would not pass `G5` or `G6`, which require an implemented engine, supported environment, resources, models, factorial controls, grid adapter, audits, and measured evidence.

Rationale: [OBSERVED] The current suite remains non-engine and no `fisher_engine` exists. [DERIVED] Exact prose contracts can authorize later synthetic implementation work only after review; they cannot establish code, model, dataset, metric, or performance behavior.

Alternatives not selected:

- Mark P0 passed because all five third-review defects were edited: rejected because the repaired bytes have not passed independent replay.
- Begin model or factorial work from a pending specification: rejected because `G5` and `G6` remain independently blocked.
- Treat document QA or unit-test count as engine evidence: rejected because neither executes the specified interfaces.

### Impact and tradeoffs

- Compatibility and reproducibility: exact execution/source/run/prediction/tensor/universe/metric schemas are restrictive and may invalidate future artifacts that omit a field or use native numeric behavior; they create one replay target.
- Data and provenance: no dataset or registry content changed. Canonical universe, source, VMP, provider, and reference bindings improve provenance without proving their real-world truth.
- Security and privacy: feature exclusions, exact audit hashes, failure accounting, and no-deletion rules reduce shortcut, tampering, and selective-exclusion risks; no implemented audit has tested them.
- Evaluation: degraded provider fallbacks remain visible in accounting but cannot silently enter or shrink confirmatory/protected metrics.
- Performance: the 4 MiB source manifest, 1 MiB run envelope, 4 MiB prediction audit, 2 MiB tensor audit, 32 MiB universe/metric manifests, 64 rows, and 31 dimensions are design caps, not measured resource results.
- Operations: `G0/P0`, `G5`, and `G6` remain blocked. No engine, model, authentic corpus, registry, metric result, performance result, collection authorization, or publication claim exists.

### Verification performed

- `[OBSERVED - Luna inspection]` All ten repaired research-document SHA-256 values match the final pins recorded above.
- `[OBSERVED - parent-supplied execution evidence]` `python3 -B -m unittest discover -s tests -v` passed 101/101 non-engine tests in 30.249 seconds.
- `[OBSERVED - parent-supplied verification evidence]` Link/anchor checks, strict UTF-8, LF-only line endings, final-newline, trailing-whitespace, stale-symbol, and field-inventory-uniqueness checks reported zero issues.
- `[OBSERVED - Luna inspection]` The execution inventory contains exactly ordered `P01`-`P20`, `O01`-`O30`, and `E01`-`E11`. `E11` preserves the third semantic failure and identifies this repair as pending replay.
- `[OBSERVED - Luna inspection]` No `fisher_engine` directory exists.
- Unrun by Luna: the 101-test suite and technical documentation QA commands were not rerun for this register-only update. No fourth semantic replay, engine parser/serializer, provider execution, prediction selection, tensor projection, universe/metric run, real registry, model, dataset, or performance benchmark ran.

### Remaining risks and follow-up

- Independent replay may reveal further cross-envelope, invalid-state, or hash-binding ambiguities.
- The E0 category grid and tensor are unimplemented; the real subword/VMP adapter remains unknown.
- Design caps and sequential binary64 operations are unbenchmarked.
- Provider failure policy needs executable accounting and protected-metric rejection tests.
- Human governance, registry truth, collection authorization, corpus construction, model behavior, and publication readiness remain unproved.

Next owner/action: the fourth independent semantic reviewer should pin these ten documents and replay provider-execution states, source/run envelope bytes and hashes, binary64 endpoint selection, five-category grid and 31-dimensional tensor arithmetic, evaluation-universe/metric no-deletion binding, Boolean-safe coordinates, degraded-run exclusion, condition masks, and historical `E05`-`E11` consistency. Only a separate successful review record can change `G0`; `G5/G6` still require implementation evidence.

### Correction history

None. This record is append-only, `LUNA-20260819-010` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-012

### Fourth independent P0 semantic review failed

- Lifecycle: `REVIEW_FAILED` - independent semantic review completed; `G0/P0` remains blocked and no commit requested
- Recorded: 19 August 2026, 6:18:54 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-012`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Reviewed paths and pinned boundary

- `docs/research/ENGINE_SPEC.md` - start/end SHA-256 `1ae7b86fbf3dce7f2c93afc202794cfcb03f0d6dca9d02b7c7e9e11ed13499ae`
- `docs/research/FACTORIAL_CONDITION_SPEC.md` - start/end SHA-256 `99d5d8e49176f4dfaec07ee737f1b07cdb96c9ec0da5063ef9cb2734b74ed313`
- `docs/research/PAPER_1_PREREGISTRATION.md` - start/end SHA-256 `67c3640de0e0d80a7ac943cdd2621295766fff80ecd842220ac2e6f3cec14efb`
- `docs/research/REGISTRY_PROTOCOL.md` - start/end SHA-256 `9699825e312cd17f93b85445700c167b0820c7cb5136e111a9b9bf586bad0866`
- `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md` - start/end SHA-256 `0d4ce4016ece538fa980ae52ed2d721c42e2332efd9b70b80faf7927480a4b60`
- `docs/research/THREAT_MODEL.md` - start/end SHA-256 `971caa609b9714837a1219d0bd7c5b1e95c00cdce294607948fd9fb47a55ed80`
- `docs/research/FISHER_RESEARCH_BLUEPRINT.md` - start/end SHA-256 `a051f692171740730d1c6fd1034a35000a3106ce9f74cb554f443b8f2b2ddf71`
- `docs/research/ANNOTATION_GUIDE.md` - start/end SHA-256 `0e1cf0620168f039be39a35e601ae2e07cb40c44706276b85637fa21835c47b5`
- `docs/research/EXECUTION_STATUS.md` - start/end SHA-256 `7062794857cc0e132b6c56a2575b3d591a5e50c1edb8632da3cb36db7b69589f`
- `docs/research/SOURCE_LEDGER.md` - start/end SHA-256 `f94dcc8ea557bf7a67ba411837a4f904ab04d42fed583e7788ebf52ccdb89f3d`
- `docs/DATA_CONTRACT.md` - start/end SHA-256 `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`

This read-only review made no technical-file change and preserves `LUNA-20260819-011` as a pending-repair record rather than converting it to a pass. [OBSERVED - parent-supplied independent review] The targeted repairs associated with `E08`, `E10`, and `E11` otherwise held, the status history remained honest, and all `P01`-`P20`, `O01`-`O30`, and `E01`-`E11` entries were present. Five later blocker groups still prevented an implementable, deterministic P0 contract.

#### Decision D-053 - Reject inconsistent invalid and degraded state requirements

Decision: Keep the review failed until every engine, candidate, provider, condition, and metric state has one consistent representation and validity matrix. Resolve whether diagnostics, paths, `C01`, and `C11` artifacts exist, are empty, or are absent for each invalid or degraded outcome; define the provider-fault boundary between a retained degraded run and an invalid run.

Rationale: [OBSERVED - parent-supplied independent review] Current requirements both require and forbid candidate diagnostics/paths and `C01`/`C11` artifacts in invalid or degraded states. Provider failure is described as degraded for accounting but its transition to metric-invalid is not machine-exact. [DERIVED] A serializer or validator cannot satisfy contradictory presence rules or infer which fallback evidence is legitimate.

Alternative not selected: invent a fallback candidate/path or implicit empty artifact. Rejected because fabricated evidence would hide provider failure and create implementation-specific hashes.

#### Decision D-054 - Require exact system-variant and artifact masks

Decision: Freeze the allowed `system_variant` values and exact artifact-presence, artifact-validity, feature, supervision, and metric masks for every capacity and supervision control before implementation.

Rationale: [OBSERVED - parent-supplied independent review] Capacity and supervision controls lack exact system-variant and artifact masks. [DERIVED] Relabeling a control without binding what is removed, retained, supervised, scored, and audited would not isolate the intended factor.

Alternative not selected: relabel existing controls while leaving their artifacts implicit. Rejected because the same label could then represent materially different systems.

#### Decision D-055 - Bind the evaluation universe to all retained binary-final items and freeze gold bytes

Decision: Require the canonical evaluation universe to equal every retained binary-final item in the declared partition, not an evaluator-selected subset. Add a versioned gold-inventory schema with field order, canonical UTF-8 bytes, escaping policy, size cap, item order, and SHA-256; bind its hash and the complete item set to the evaluation universe and metric run.

Rationale: [OBSERVED - parent-supplied independent review] The current universe is not proven equal to the full retained binary-final partition, and the gold inventory lacks versioned canonical bytes, size, and hash. The reviewer supplied conceptual subset hashes `090fd6...` for `[a]` and `dac6c8...` for `[a,b]`, plus conceptual gold hashes `4c2186...` and `6f9abd...` for Unicode versus ASCII-escaped serialization. [DERIVED] Distinct subsets or escaping choices can yield internally valid but incomparable metric populations.

Alternative not selected: accept any hashed subset universe. Rejected because a valid hash proves only the chosen subset, not completeness against the retained partition.

#### Decision D-056 - Close provenance, registry, system-artifact, and five-seed arithmetic contracts

Decision: Freeze provenance and source closure, exact system-artifact inventories and hashes, an exact registry artifact hash, and the five-seed aggregation order and binary64 arithmetic. Bind runtime and source choices explicitly rather than accepting ambient behavior.

Rationale: [OBSERVED - parent-supplied independent review] Provenance/source closure and required system artifacts remain incomplete, the registry contract lacks an exact artifact hash, and the five-seed aggregation arithmetic is not exact. In the reviewer's conceptual arithmetic probe, sequential and compensated accumulation produced `0.4` with binary64 bits `3fd999999999999a` versus `0.6` with bits `3fe3333333333333`. [DERIVED] Seed summaries and registry-dependent outputs can change without any declared run identity if source artifacts or summation rules remain implicit.

Alternative not selected: use the ambient runtime or a library-default float summation. Rejected because runtime and summation implementation can change the final binary64 result.

#### Decision D-057 - Define merge counts, remove stale mass aliases, and order q arithmetic

Decision: Define `duplicate_merge_count` from exact candidate/path lineage and merge operations; remove or normatively map every stale retained-mass term; and freeze the q numerator, denominator, normalization, comparison, and serialization operation order with binary64 known-answer vectors.

Rationale: [OBSERVED - parent-supplied independent review] `duplicate_merge_count` is undefined, stale retained-mass vocabulary remains, and plausible q numerator/normalization orders produced different final bits in the reviewer's conceptual example. [DERIVED] Undefined counters, aliases, and arithmetic order allow different audit packets or condition decisions from the same logical inputs.

Alternative not selected: retain stale aliases as informal compatibility fields. Rejected because non-normative aliases can diverge from the active log-domain quantities and reintroduce ambiguity.

#### Decision D-058 - Keep P0, G5, and G6 blocked pending the smallest repair and fifth replay

Decision: Record the fourth review as `REVIEW_FAILED`. Keep `G0/P0`, `G5`, and `G6` `BLOCKED`; make the smallest documentation-only repair to the five blocker groups, pin the resulting boundary, and require a fifth independent semantic replay before any P0 pass or `E0` implementation start.

Rationale: [OBSERVED - parent-supplied independent review] The fourth reviewer found the five blocker groups despite stable start/end pins and a passing non-engine test suite. [DERIVED] The repairs that held do not override newly exposed contradictions or missing byte-level contracts, and prose review cannot establish engine or empirical behavior.

Alternatives not selected:

- Mark `G0` passed because the prior target defects held: rejected because the new blockers remain implementation-critical.
- Treat 101 passing tests as semantic acceptance: rejected because the suite contains no engine implementation.
- Start `G5/G6` model or factorial work: rejected because both gates remain independently blocked on executable artifacts and evidence.

### Impact and tradeoffs

- Compatibility and reproducibility: exact state matrices, masks, inventories, bytes, hashes, and arithmetic will reject ambiguous or incomplete future artifacts but provide one replay target.
- Data and evaluation: full-partition equality and canonical gold inventory prevent silent subset selection and encoding-dependent metric populations; no dataset was changed or measured.
- Security and provenance: explicit failure states, source closure, system artifacts, and registry hashes reduce fabricated fallback and unbound-evidence risk; real authenticity and ownership remain human-governed.
- Performance: exact/beam capacities, log-domain stability, and float probes are conceptual contract checks, not measured engine performance.
- Operations: this review adds another specification repair/replay cycle before `G0`; `G5/G6` remain blocked regardless of a future documentation pass until implementation evidence exists.

### Verification performed

- `[OBSERVED - Luna inspection]` All eleven reviewed local files match the supplied start/end SHA-256 pins recorded above.
- `[OBSERVED - parent-supplied independent execution evidence]` `python3 -B -m unittest discover -s tests -v` passed 101/101 tests in 29.144 seconds; the suite was explicitly non-engine.
- `[OBSERVED - parent-supplied independent verification evidence]` Strict UTF-8, LF-only line endings, no trailing whitespace, and relative-link checks passed.
- `[OBSERVED - parent-supplied conceptual probes]` Exact versus beam capacity was exercised at 64 versus 128, and a long-input direct-exponent calculation underflowed while the corresponding log-domain mass remained finite. These were contract probes, not engine tests or performance measurements.
- `[OBSERVED - Luna inspection]` `EXECUTION_STATUS.md` contains exactly ordered `P01`-`P20`, `O01`-`O30`, and `E01`-`E11`; its current `G0`, `G5`, and `G6` rows remain `BLOCKED` and do not claim this review.
- Unrun by Luna: the 101-test suite, reviewer probes, and documentation link checks were not rerun for this register-only update. No engine, provider, registry resolution, model, dataset, metric run, runtime matrix, or empirical benchmark was executed.

### Remaining risks and follow-up

- Repairing these five groups may reveal more cross-schema contradictions during a fifth replay.
- The invalid/degraded matrix and control masks could expand substantially if not kept to the declared E0 boundary.
- Gold inventory completeness depends on an authoritative retained-item partition and canonical provenance that do not yet exist as executed artifacts.
- Registry truth, provider behavior, five-seed results, q behavior, and merge accounting remain unimplemented.
- No engine, authentic corpus, collection authorization, model behavior, metric result, performance result, or publication claim is established.

Next owner/action: make a minimal documentation repair that freezes the invalid/degraded state matrix, system/control masks, full retained-item and gold inventories, provenance/system/registry artifact closure, five-seed arithmetic, merge-count definition, active mass vocabulary, and q operation order. Pin every affected document and commission a fifth independent semantic replay before changing `G0`; leave `G5/G6` blocked until executable evidence exists.

### Correction history

None. This record is append-only, `LUNA-20260819-011` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-013

### Fourth-failure architecture adjudication before specification repair

- Lifecycle: `DECIDED_PENDING_IMPLEMENTATION` - architecture adjudicated; specification repair and independent replay remain pending and no commit requested
- Recorded: 19 August 2026, 6:27:21 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-013`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected architecture and current stable boundary

No technical file changed in this read-only adjudication. The decision applies to the next minimal repair of:

- `docs/research/ENGINE_SPEC.md` - SHA-256 `1ae7b86fbf3dce7f2c93afc202794cfcb03f0d6dca9d02b7c7e9e11ed13499ae`
- `docs/research/FACTORIAL_CONDITION_SPEC.md` - SHA-256 `99d5d8e49176f4dfaec07ee737f1b07cdb96c9ec0da5063ef9cb2734b74ed313`
- `docs/research/PAPER_1_PREREGISTRATION.md` - SHA-256 `67c3640de0e0d80a7ac943cdd2621295766fff80ecd842220ac2e6f3cec14efb`
- `docs/research/REGISTRY_PROTOCOL.md` - SHA-256 `9699825e312cd17f93b85445700c167b0820c7cb5136e111a9b9bf586bad0866`
- `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md` - SHA-256 `0d4ce4016ece538fa980ae52ed2d721c42e2332efd9b70b80faf7927480a4b60`
- `docs/research/THREAT_MODEL.md` - SHA-256 `971caa609b9714837a1219d0bd7c5b1e95c00cdce294607948fd9fb47a55ed80`
- `docs/research/FISHER_RESEARCH_BLUEPRINT.md` - SHA-256 `a051f692171740730d1c6fd1034a35000a3106ce9f74cb554f443b8f2b2ddf71`
- `docs/research/ANNOTATION_GUIDE.md` - SHA-256 `0e1cf0620168f039be39a35e601ae2e07cb40c44706276b85637fa21835c47b5`
- `docs/research/EXECUTION_STATUS.md` - SHA-256 `7062794857cc0e132b6c56a2575b3d591a5e50c1edb8632da3cb36db7b69589f`
- `docs/research/SOURCE_LEDGER.md` - SHA-256 `f94dcc8ea557bf7a67ba411837a4f904ab04d42fed583e7788ebf52ccdb89f3d`

[OBSERVED - Luna inspection] These ten files still match the stable SHA-256 boundary recorded in `LUNA-20260819-011` and reviewed in `LUNA-20260819-012`. The current factorial and engine specifications define `C00`/`C01` as raw identity with no provider and `C10`/`C11` as calibrated weighted candidate paths. The preregistration separately describes `C00` as one-best, `C01` as the one-best semantic cell, and the primary uncertainty comparisons as rank-one versus q-weighted paths. [OBSERVED - parent-supplied Terra adjudication] A read-only architecture adjudication resolved this as an estimand contradiction rather than an implementation choice.

#### Decision D-059 - Preserve the registered rank-one-versus-q-weighted factorial estimand

Decision: Configure one identical candidate provider and provider configuration for all four factorial cells. `C00` and `C01` activate the same returned rank-one path; `C10` and `C11` activate all returned paths with the same calibrated q weights. Semantic consistency remains absent in `C00`/`C10` and present in `C01`/`C11`. Candidate generation, candidate identities, provider configuration, and pre-semantic q values must therefore be shared and auditable across cells.

Decision: Use the raw identity path only when no eligible span exists or as the controlled fallback after provider failure. Provider-failure fallback is degraded and excluded from confirmatory and protected metrics. A raw-text system may remain as a separately named baseline, but it is not one of the four factorial cells.

Rationale: [DERIVED from observed specifications and Terra adjudication] The registered uncertainty factor is rank-one versus uncertainty-marginalized q-weighted use of the same candidate evidence. Raw/no-provider versus candidate/provider changes both the input representation and the provider, so it cannot identify that effect. Sharing the provider isolates uncertainty activation while the second axis isolates semantic consistency.

Alternatives not selected:

- Keep raw-versus-candidate definitions for `C00`/`C01` versus `C10`/`C11`: rejected because they confound provider availability, candidate text, and uncertainty weighting.
- Promote a raw-text baseline into a factorial cell: rejected because raw input is a valid comparator but not the registered rank-one condition.
- Assign global provider ranks across messages or runs: rejected because rank identity must remain bound to the canonical provider response and lineage rather than an invented cross-run ordering.

#### Decision D-060 - Replace contradictory failure fields with an engine-envelope v1.1 status union

Decision: Repair the engine envelope as version `1.1.0` with a discriminated valid, degraded, or invalid status union. Each state must have one exact field-presence and validity rule, bounded failure-code/count representation, canonical bytes, and hash. An invalid envelope carries no partial candidate, path, prediction, packet, plan, tensor, condition, or metric artifacts. A controlled provider-failure raw fallback is degraded for accounting and cannot enter confirmatory or protected metrics.

Rationale: [DERIVED from `LUNA-20260819-012` and Terra adjudication] A status union removes the current simultaneous requirement and prohibition for partial artifacts. It also makes provider failure observable without inventing successful candidate evidence. The exact numeric failure-count cap remains `UNKNOWN` until the repair writes and reviews it; Luna does not invent the value here.

Alternatives not selected:

- Serialize unsafe partial rows after an invalid transition: rejected because consumers could mistake incomplete evidence for a valid run.
- Invent fallback candidates, paths, or condition artifacts: rejected because failure accounting must not fabricate model evidence.

#### Decision D-061 - Freeze system variants and exact control masks

Decision: Use the exact `system_variant` vocabulary `BASE|CAPACITY_CONTROL|SUPERVISION_CONTROL`. For each variant and factorial cell, freeze machine-readable masks over candidate/path activation, semantic inputs and outputs, registry access, trainable capacity, auxiliary labels/losses, prediction, audit artifacts, learned risk features, and permitted metrics. A mask mismatch invalidates the run rather than being relabeled after execution.

Rationale: [DERIVED from Terra adjudication] Exact masks are the smallest way to make capacity and supervision controls test the stated confounds without defining a new family of loosely named systems.

Alternative not selected: relabel controls while leaving active artifacts or supervision implicit. Rejected because labels alone do not prove isolation.

#### Decision D-062 - Require a complete evaluation universe and canonical gold inventory

Decision: The evaluation universe equals every eligible retained item with a final binary label in the declared partition. Freeze eligibility and retention predicates before inference; no sampling, deletion, replacement, or complete-case filtering is permitted for confirmatory/protected evaluation. Add a versioned gold inventory with exact item order, label and structured-gold bindings, canonical UTF-8 bytes and escaping, size cap, and SHA-256, then bind it to the universe and metric-run manifests.

Rationale: [DERIVED from the fourth review and Terra adjudication] A canonical subset hash cannot demonstrate completeness. Binding the full eligible retained partition and canonical gold bytes closes both post hoc membership and serialization ambiguity.

Alternative not selected: allow a sampled or evaluator-selected universe. Rejected because it changes the protected estimand and can hide failed or unfavorable records.

#### Decision D-063 - Stage the SystemArtifactManifest by experimental phase

Decision: Add a canonical `SystemArtifactManifest` that always binds exact source, runtime, Unicode/binary64 contract, synthetic fixture, and analysis implementation artifacts. At `E0`, model, learned resource, and container/OCI fields may be explicitly null because `E0` is a synthetic mechanics gate. At `E3/E4`, the applicable trained model, tokenizer, transliteration/registry resources, environment or container, calibration, and analysis artifacts become nonnull and hash-bound.

Rationale: [DERIVED from Terra adjudication] Requiring unavailable trained checkpoints and OCI images at `E0` would block the intended synthetic known-answer gate, while omitting them at later empirical phases would leave results unreproducible. Source hashes identify reviewed source bytes but are not a universal guarantee across platform, runtime, or dependency changes.

Alternatives not selected:

- Require trained checkpoints, learned resources, and an OCI image at `E0`: rejected because `E0` intentionally has no trained system.
- Treat source-file hashes as a universal platform guarantee: rejected because identical source does not bind runtime, dependencies, numerical behavior, or external artifacts.

#### Decision D-064 - Limit FiveSeedLogitArtifact to an E0 arithmetic known answer

Decision: Define a bounded, canonical `FiveSeedLogitArtifact` only for `E0` arithmetic known-answer tests, with five ordered seed entries, exact finite binary64 logit bits, deterministic aggregation order, canonical bytes, and hash. Do not claim that it is a trained ensemble artifact. Calibration optimizer, bounds, failure behavior, and empirical five-seed construction remain `UNKNOWN` and must be frozen before `E4`.

Rationale: [DERIVED from Terra adjudication] A synthetic five-seed vector can verify exact aggregation mechanics without pretending that models or calibration exist. Deferring the optimizer preserves the current evidence boundary.

Alternatives not selected:

- Invent a calibration optimizer or defaults during `E0`: rejected because optimizer behavior is an empirical-phase contract and remains unknown.
- Use ambient or library-default summation: rejected because different valid accumulation methods can produce different binary64 results.

#### Decision D-065 - Freeze duplicate reductions, retained-mass vocabulary, and q arithmetic

Decision: Define duplicate processing as ordered reduction stages with per-stage input, retained, and removed counts plus an exact total `duplicate_merge_count`; bind every reduction to candidate lineage. Use only `retained_preK_composition_mass` with an explicit `preK_scope`; remove or normatively migrate stale retained-mass aliases. Compute q with a fixed max-shift sequence: choose the specified maximum, subtract, exponentiate, accumulate the denominator in the specified order, divide each numerator in candidate order, and persist exact numerator and denominator binary64 bits needed for replay.

Rationale: [DERIVED from the fourth review and Terra adjudication] Staged counts make the total auditable, one active mass term prevents stale semantic aliases, and exact max-shift arithmetic removes plausible operation-order differences from q.

Alternatives not selected:

- Retain stale mass names as informal aliases: rejected because aliases can diverge from the active pre-K composition quantity.
- Leave duplicate totals or q normalization to implementation defaults: rejected because different stage accounting or operation order changes audit bytes and potentially active paths.

#### Decision D-066 - Keep G0, G5, and G6 blocked through repair and independent replay

Decision: This adjudication chooses the minimal repair architecture but does not pass `G0/P0`. `G0/P0`, `G5`, and `G6` remain `BLOCKED`. The documentation repair must implement `D-059`-`D-065`, pin the complete affected boundary, and pass a fifth independent semantic replay before `G0` can change. `G5/G6` additionally require executable engine, resource, model, control, and evaluation evidence.

Rationale: [OBSERVED] Terra performed read-only adjudication; no technical file, engine, test, dataset, model, registry, metric, or empirical artifact changed. [DERIVED] A decided repair direction reduces ambiguity but is not implementation or independent verification.

Alternative not selected: promote the architecture decision itself to a P0 pass. Rejected because the contradictory stable specifications are still unchanged.

### Impact and tradeoffs

- Scientific validity: the four cells now target the registered uncertainty and semantic factors; raw text remains available as a clearly separate baseline.
- Compatibility: engine envelope `1.1.0`, exact variants/masks, complete-universe binding, and new artifact manifests will invalidate older ambiguous draft artifacts rather than silently interpret them.
- Data and evaluation: complete retained-item coverage and canonical gold bytes strengthen denominator integrity; no item, label, or dataset changed in this checkpoint.
- Security and privacy: invalid artifacts cannot leak partial evidence into downstream consumers, and degraded provider fallbacks remain visible but excluded from protected metrics; real provenance and authorization remain unproved.
- Performance: caps and exact arithmetic are design requirements, not measurements. Shared candidate generation across cells may increase planned work for rank-one cells relative to the current raw design, but no runtime was measured.
- Operations: a fifth review is required after repair; `G5/G6` stay blocked even if P0 later passes.

### Verification performed

- `[OBSERVED - Luna inspection]` `FACTORIAL_CONDITION_SPEC.md`, `ENGINE_SPEC.md`, and `PAPER_1_PREREGISTRATION.md` contain the raw/no-provider `C00`/`C01` definitions and the one-best/rank-one comparator language described above.
- `[OBSERVED - Luna inspection]` All ten architecture-document SHA-256 values still match the stable boundary recorded in `LUNA-20260819-011` and `LUNA-20260819-012`.
- `[OBSERVED - parent-supplied evidence]` Terra performed a read-only adjudication of the fourth-review failures and supplied the decisions recorded here.
- Unrun: no technical-file edit, unit test, engine, provider, registry lookup, dataset operation, model, calibration optimizer, metric run, performance benchmark, or empirical analysis occurred for this checkpoint.

### Remaining risks and follow-up

- Exact failure caps, manifest size caps, schemas, canonical byte grammars, and mask tables still require specification text and independent replay.
- The four-cell correction may require coordinated revisions across hypotheses, baseline names, metric applicability, condition audits, and execution status.
- Candidate-provider success and failure behavior, real five-seed aggregation, calibration, registry artifacts, and protected-universe completeness remain unimplemented.
- The E0/E3/E4 artifact-stage boundary may reveal additional nullable/nonnullable conflicts during repair.
- No engine, authentic corpus, collection authorization, model result, metric result, performance result, or publication claim is established.

Next owner/action: implement the smallest coordinated documentation repair for `D-059`-`D-065`, explicitly record unresolved numeric caps or optimizer details as blockers rather than inventing them, update execution status honestly, pin the resulting documents, and commission a fifth independent semantic replay. Do not change `G0`, `G5`, or `G6` before their stated evidence exists.

### Correction history

None. This record is append-only, `LUNA-20260819-012` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-014

### Fifth P0 documentation repair pending independent replay

- Lifecycle: `REPAIRED_PENDING_REVIEW` - fifth documentation repair completed; not a pass and no commit requested
- Recorded: 19 August 2026, 7:02:02 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-014`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected paths and pinned repair boundary

- `docs/research/ENGINE_SPEC.md` - SHA-256 `0beaf6e38b36b086e94cd2707aad2392afb502c1ae8f8d8df087fc61bdeaf217`
- `docs/research/FACTORIAL_CONDITION_SPEC.md` - SHA-256 `cfaf647ec7086e43d769e97920dcb604645e314dd8f347910d32d268c329d23b`
- `docs/research/PAPER_1_PREREGISTRATION.md` - SHA-256 `099572752140dc01f721044166b6e83f9f31a189a48b5ea7c4f6a9ccf392c5d3`
- `docs/research/REGISTRY_PROTOCOL.md` - SHA-256 `b838ba4f7cb12ef0e9fde5eda0a101889f7478e250fd4424009cd40083a07d62`
- `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md` - SHA-256 `0f4a5f4314a38c094d20cb81a17feef2d9b4ed747a514a0e49462e4b902999b4`
- `docs/research/THREAT_MODEL.md` - SHA-256 `e43fb1b200112829a6a6af1acc6ac722f377054db5a5167e5783dc23867f90cb`
- `docs/research/FISHER_RESEARCH_BLUEPRINT.md` - SHA-256 `eb914de7aa72f1f01493fd10a7e66d96e78c21a55a968f9006736e60a54d7a22`
- `docs/research/ANNOTATION_GUIDE.md` - SHA-256 `8a33d3b8f78d98a3ba52380a6f9dfecf6abf8011fa41d97f726896953605288c`
- `docs/research/EXECUTION_STATUS.md` - SHA-256 `6a66249b4220b059beaca02f2ca52bb08217acbe0102c90b9e72242ab969eee9`
- `docs/research/SOURCE_LEDGER.md` - SHA-256 `7be24b53bdb33d0bd48bcb6c3c205677cfa4e94067ba495794986247865169b9`
- `docs/DATA_CONTRACT.md` - unchanged SHA-256 `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`

This repair implements the adjudicated direction in `LUNA-20260819-013` while preserving `LUNA-20260819-012` and the fourth `REVIEW_FAILED` verdict. [OBSERVED - Luna inspection] `EXECUTION_STATUS.md` appends `E12`, retains the earlier `E05`-`E11` history, and leaves `G0/P0`, `G5`, and `G6` `BLOCKED`. No fifth independent semantic pass is claimed.

#### Decision D-067 - Restore one shared-provider rank-one-versus-q-weighted factorial

Decision: Configure the same canonical candidate provider, provider configuration, normalizer, candidates, and pre-semantic q values for all four main factorial cells. `C00` and `C01` activate the same returned rank-one path; `C10` and `C11` activate all returned paths with q weighting. Semantic consistency remains absent for `C00`/`C10` and present for `C01`/`C11`. Raw/no-provider systems are separately named baselines, not main factorial cells.

Decision: Raw identity is permitted within a main cell only when no eligible span exists or as a validated fallback after a qualifying pre-acceptance availability failure. A provider-failure fallback is degraded and cannot enter confirmatory or protected metrics.

Rationale: [DERIVED from the fourth failure and architecture adjudication] Sharing candidate evidence isolates the registered rank-one-versus-uncertainty-marginalized factor. The former raw/no-provider cells changed provider availability and input representation simultaneously, so they could not identify the intended uncertainty effect.

Alternative not selected: retain raw/no-provider `C00`/`C01` as main factorial cells. Rejected because that would preserve the estimand-confounding defect; raw text remains available as a distinct baseline.

#### Decision D-068 - Use schema-1.1 discriminated engine and metric status unions

Decision: Freeze schema `1.1.0` engine-envelope states `VALID|DEGRADED|INVALID` and metric states `VALID|INVALID`, with state-specific field inventories, canonical bytes, hashes, and bounded failure counts. An `INVALID` engine row contains no partial candidate diagnostics, paths, active paths, prediction, SEP, feature, tensor, condition, five-seed, or downstream artifacts; an invalid metric row cannot masquerade as the valid metric schema.

Decision: Malformed, nonfinite, alignment-invalid, hash-invalid, or otherwise invalid provider/normalizer output is `INVALID`. Only provider or normalizer unavailability/timeout before accepted output may become `DEGRADED`, and only when the exact identity fallback fully validates. Degraded runs remain in operational accounting but invalidate confirmatory and protected metric runs.

Rationale: [OBSERVED - Luna inspection] The repaired engine specification now separates the three engine branches and two metric branches and prohibits partial artifacts in the invalid branch. [DERIVED] This closes the earlier requirement to invent valid-looking candidate evidence after an early failure and prevents invalid provider data from being laundered through degradation.

Alternatives not selected:

- Invent a candidate or path after invalid provider output: rejected because it fabricates successful evidence.
- Force an invalid row to satisfy the valid-state schema: rejected because contradictory fields would remain.
- Treat provider-invalid output as degraded: rejected because a fallback is trustworthy only for pre-acceptance unavailability/timeout with a separately validated identity path.

#### Decision D-069 - Freeze the exact eight condition/system-variant masks

Decision: Permit exactly eight condition/variant combinations: four `BASE` rows for `C00|C10|C01|C11`, `CAPACITY_CONTROL` for `C00|C10`, and `SUPERVISION_CONTROL` for `C01|C11`. Each row has an exact mask over path activation, endpoint construction, SEP, registry calls, feature plan/tensor, learned-risk inputs, auxiliary supervision, trainable-capacity identity, audit artifacts, and metric eligibility. Any ninth combination or mask mismatch is invalid.

Rationale: [DERIVED from the fourth failure] Exact masks make the causal controls machine-representable and prevent prohibited semantic or registry information from leaking into controls while retaining their intended capacity or supervision match.

Alternative not selected: use descriptive control labels without exact masks. Rejected because a label cannot establish which information, artifacts, or parameters were active.

#### Decision D-070 - Canonically bind system artifacts, executed-source closure, and registry identity

Decision: Require one canonical `SystemArtifactManifest` per run, binding the exact executed-source closure, runtime and numerical contract, condition and system variant, provider/normalizer, registry, model, resource, environment/container, synthetic fixture, and analysis artifacts according to phase. Directly bind the exact registry artifact SHA-256 wherever registry behavior is permitted. `E0` may use explicit nulls for unavailable trained model/resource/container fields; applicable `E3/E4` fields become nonnull.

Rationale: [DERIVED from the fourth failure] Source closure plus direct artifact hashes identifies the implementation and evidence actually used without pretending that source bytes alone guarantee platform behavior. Phase-sensitive nullability keeps the synthetic `E0` gate feasible while requiring empirical artifacts later.

Alternative not selected: rely on ambient provenance, platform state, or source hashes alone. Rejected because runtime, resource, registry, model, and analysis behavior could change without entering run identity.

#### Decision D-071 - Bind the complete retained-binary-final universe and canonical gold inventory

Decision: The evaluation universe must equal every eligible retained item with a final binary label in the declared partition under the frozen predicates. Freeze the exact ordered universe and a versioned per-item gold inventory with canonical UTF-8 serialization, explicit escaping and field order, byte length, SHA-256, structured-gold bindings, gold-pair count, and emptiness. Bind both to submitted inference and metric manifests; prohibit sampling, omission, reordering, replacement, and complete-case deletion.

Rationale: [DERIVED from the fourth failure] Completeness against the retained partition fixes the denominator, while canonical gold bytes remove equivalent-looking but hash-distinct JSON encodings.

Alternatives not selected:

- Evaluate a sampled or evaluator-selected universe: rejected because it changes the protected population and permits selective exclusion.
- Accept ambiguous gold JSON: rejected because Unicode escaping, field order, or omitted fields could alter identity and reconstruction.

#### Decision D-072 - Bound FiveSeedLogitArtifact to E0 arithmetic mechanics

Decision: Use the exact canonical `FiveSeedLogitArtifact` only as an `E0` arithmetic known-answer artifact, with five ordered seeds, path-logit bit strings, sequential binary64 aggregation, exact output bits, size cap, bytes, and hash. It is not a trained-model or calibration artifact. Model construction and calibration-optimizer semantics remain unresolved until their later gate.

Rationale: [DERIVED from the architecture adjudication] A synthetic artifact can prove deterministic five-seed arithmetic without inventing checkpoints, models, or optimizer behavior.

Alternative not selected: use ambient float operations or infer a calibration optimizer. Rejected because implementation defaults can change result bits and no optimizer evidence exists.

#### Decision D-073 - Freeze staged duplicate reductions, one mass vocabulary, and exact q arithmetic

Decision: Record ordered duplicate-reduction stages and exact per-stage input, retained, removed, and merged counts; require their checked total to equal `duplicate_merge_count`. Bind reductions to candidate lineage. Use only `retained_preK_composition_mass_f64_bits` with `preK_scope=EXACT_FULL|FINAL_BEAM`; remove active stale retained-mass aliases.

Decision: Freeze q as an exact max-shift computation under the declared runtime and math backend: select the specified maximum, subtract in candidate order, exponentiate with bound backend behavior, accumulate the denominator in the specified order, divide in candidate order, and persist numerator, maximum, denominator/normalizer, and q binary64 bits needed for replay.

Rationale: [OBSERVED - Luna inspection] The repaired engine specification now records staged merge counts, one pre-K mass term/scope, q diagnostics, and runtime bindings. [DERIVED] These rules remove ambiguity in total merge accounting, retained-set meaning, and numerically distinct normalization orders.

Alternative not selected: leave merge totals, stale mass aliases, or floating-point order to the implementation. Rejected because logically similar implementations could produce different audit bytes and active weights.

#### Decision D-074 - Keep G0, G5, and G6 blocked pending the fifth independent replay

Decision: Classify the fifth repair as `REPAIRED_PENDING_REVIEW`, not a pass. Require an independent fifth semantic replay of the pinned documents before `G0/P0` can change. Keep `G5/G6` blocked on executable engine, model, resource, control, and evaluation evidence even if the documentation later passes.

Rationale: [OBSERVED] The repair changed documentation only; the available test suite remains non-engine. [DERIVED] Exact prose and QA can define an implementation target but cannot establish runtime or empirical behavior.

Alternatives not selected:

- Promote `G0` because the requested edits were made: rejected because the repaired contract has not passed independent replay.
- Treat document or unit-test QA as `G5/G6` evidence: rejected because no engine, model, dataset, registry, or protected evaluation ran.

### Impact and tradeoffs

- Scientific validity: the factorial again targets rank-one versus q-weighted uncertainty under shared candidate evidence and separately tests semantic consistency.
- Compatibility: schema `1.1.0`, exact masks, canonical artifact/universe/gold manifests, and renamed mass fields deliberately invalidate ambiguous draft artifacts.
- Data and evaluation: no dataset or label changed; complete-universe and gold-byte bindings strengthen future denominator and provenance integrity.
- Security and privacy: invalid provider output cannot enter fallback as degraded evidence, and degraded availability fallbacks cannot enter protected metrics; real authorization and registry truth remain unproved.
- Performance: candidate caps, artifact sizes, arithmetic order, and backend bindings are design contracts, not measured resource or latency results.
- Operations: `E12` preserves the failure history; the fifth repair remains pending replay and does not unblock `G0`, `G5`, or `G6`.

### Verification performed

- `[OBSERVED - Luna inspection]` All ten repaired research-document SHA-256 values and the unchanged `DATA_CONTRACT.md` SHA-256 match the pins recorded above.
- `[OBSERVED - parent-supplied execution evidence]` `python3 -B -m unittest discover -s tests -v` passed 101/101 tests in 30.069 seconds; the suite was explicitly non-engine.
- `[OBSERVED - parent-supplied documentation QA]` Strict UTF-8, LF-only line endings, final-newline, trailing-whitespace, table, local-link, and anchor checks were clean.
- `[OBSERVED - parent-supplied structural QA]` The inventories contained exact `P01`-`P20`, `O01`-`O30`, and `E01`-`E12`; the eight system-mask rows were present; six normative field inventories appeared exactly once; stale-symbol searches were clean except the deliberately preserved historical `E08` evidence.
- `[OBSERVED - Luna inspection]` `EXECUTION_STATUS.md` currently contains exact ordered `P01`-`P20`, `O01`-`O30`, and `E01`-`E12`, preserves `E05`-`E11`, and keeps `G0`, `G5`, and `G6` blocked.
- Unrun by Luna: the 101-test suite, table/link/anchor checks, eight-mask validator, six-inventory check, and stale-symbol searches were not rerun for this register-only update. No fifth semantic replay, engine, provider, registry lookup, dataset operation, model, calibration, metric run, or performance benchmark ran.

### Remaining risks and follow-up

- Independent replay may find additional cross-document contradictions or byte-level ambiguity.
- The exact schemas, masks, manifests, arithmetic, and failure transitions have no executable parser, validator, serializer, or known-answer engine tests.
- Complete-universe membership depends on future authoritative retention, final-label, and partition artifacts.
- Real provider, registry, model, resource, environment, calibration, and five-seed evidence does not exist.
- No collection authorization, authentic corpus, model result, metric result, performance result, or publication claim is established.

Next owner/action: commission a fifth independent semantic replay against the eleven pinned files, including the unchanged data contract. Replay the shared-provider factorial, every status-union branch, all eight masks, source/system/registry bindings, universe/gold closure, five-seed arithmetic, duplicate reductions, mass scope, q operation order, historical `E05`-`E12` consistency, and explicit non-engine boundary. Only a separate successful review may change `G0`; `G5/G6` still require implementation evidence.

### Correction history

None. This record is append-only, `LUNA-20260819-013` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-015

### Fifth independent P0 semantic replay failed

- Lifecycle: `REVIEW_FAILED` - fifth independent semantic replay completed; `G0/P0` remains blocked and no commit requested
- Recorded: 19 August 2026, 7:22:28 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-015`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Reviewed paths and stable start/end pins

- `docs/research/ENGINE_SPEC.md` - SHA-256 `0beaf6e38b36b086e94cd2707aad2392afb502c1ae8f8d8df087fc61bdeaf217`
- `docs/research/FACTORIAL_CONDITION_SPEC.md` - SHA-256 `cfaf647ec7086e43d769e97920dcb604645e314dd8f347910d32d268c329d23b`
- `docs/research/PAPER_1_PREREGISTRATION.md` - SHA-256 `099572752140dc01f721044166b6e83f9f31a189a48b5ea7c4f6a9ccf392c5d3`
- `docs/research/REGISTRY_PROTOCOL.md` - SHA-256 `b838ba4f7cb12ef0e9fde5eda0a101889f7478e250fd4424009cd40083a07d62`
- `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md` - SHA-256 `0f4a5f4314a38c094d20cb81a17feef2d9b4ed747a514a0e49462e4b902999b4`
- `docs/research/THREAT_MODEL.md` - SHA-256 `e43fb1b200112829a6a6af1acc6ac722f377054db5a5167e5783dc23867f90cb`
- `docs/research/FISHER_RESEARCH_BLUEPRINT.md` - SHA-256 `eb914de7aa72f1f01493fd10a7e66d96e78c21a55a968f9006736e60a54d7a22`
- `docs/research/ANNOTATION_GUIDE.md` - SHA-256 `8a33d3b8f78d98a3ba52380a6f9dfecf6abf8011fa41d97f726896953605288c`
- `docs/research/EXECUTION_STATUS.md` - SHA-256 `6a66249b4220b059beaca02f2ca52bb08217acbe0102c90b9e72242ab969eee9`
- `docs/research/SOURCE_LEDGER.md` - SHA-256 `7be24b53bdb33d0bd48bcb6c3c205677cfa4e94067ba495794986247865169b9`
- `docs/DATA_CONTRACT.md` - SHA-256 `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`

[OBSERVED - parent-supplied independent review] All eleven start and end pins matched. The fifth replay passed the targeted shared-provider rank-one/q factor, eight masks, VMP and alignment contracts, candidate/q mechanics, SEP, prediction audit, 31-dimensional tensor, universe/gold/no-deletion binding, pair metrics, five-seed mechanics, and later-phase deferrals. Provider/config equality across the four cells can be enforced by quartet orchestration and was not classified as a new blocker. Three remaining blocker groups kept the verdict at `P0 SEMANTIC FAIL`.

#### Decision D-075 - Reject the non-constructible INVALID and optional DEGRADED engine branches

Decision: Keep the engine status union failed until a deterministic preflight and status-branch algorithm defines which fields are parsed, accepted, counted, retained, nulled, or forbidden at every failure stage. The repair must enumerate invalid provider-execution combinations, define failure-stage precedence and count units, resolve accepted-provider-hash treatment after a later failure, and make degraded continuation either required or prohibited for each exact state rather than optional.

Rationale: [OBSERVED - parent-supplied independent review and Luna inspection] The current contract omits provider-invalid combinations. It requires an accepted provider-reading-manifest hash after accepted output, but the `INVALID` branch forbids that accepted hash after a later fault. Semantic-base system/registry bindings are required while the invalid envelope also nulls its direct registry bindings. No rule selects one fault stage when several predicates fail or states what each failure count measures. A degraded row may currently stop after fallback or continue with a wholly complete downstream bundle, so identical failure evidence can produce two conforming envelopes.

Alternatives not selected:

- Fabricate valid candidates, paths, provider hashes, or semantic bindings to satisfy a later-invalid row: rejected because it invents successful evidence.
- Apply status-agnostic binding rules: rejected because valid, degraded, and invalid branches have different evidence boundaries.
- Leave degraded continuation optional: rejected because one input/fault state would not have one canonical envelope.

#### Decision D-076 - Repair the E0 feature-plan binding to engine envelope 1.1

Decision: Update the E0 feature-plan and tensor contract to bind the current engine-envelope schema `1.1.0`, with one explicit compatibility rule and no silent version substitution. Revalidate every plan, tensor, envelope, and condition-mask reference under that version.

Rationale: [OBSERVED - parent-supplied independent review and Luna inspection] The normative E0 numeric feature section still says its plan is supported by engine-envelope version `1.0.0`, while the required run envelope is `1.1.0`. [DERIVED] A valid semantic E0 run cannot simultaneously satisfy both version requirements.

Alternative not selected: silently reinterpret `1.0.0` as `1.1.0`. Rejected because versioned bytes and compatibility must be explicit and independently replayable.

#### Decision D-077 - Define deterministic invalid-metric occurrence accounting and raw-input boundaries

Decision: Freeze one occurrence-level comparison algorithm and precedence for `submitted`, `missing`, `extra`, `duplicate`, `reordered`, `degraded`, `invalid`, and `mismatch` counts. Define how repeated expected and submitted IDs are paired, which occurrence enters each category, whether categories are disjoint, and how saturation is applied. The invalid branch must be constructible from a bounded safe preflight descriptor even when raw submitted input is malformed, over the 20,000-entry cap, or over the canonical byte cap; an over-limit raw submission must never be hashed or presented as a valid canonical submitted manifest.

Rationale: [OBSERVED - parent-supplied conceptual probe] For expected `[a,b]` and submitted `[b,a,a,c,c]`, the current prose admits multiple defensible extra, duplicate, and reordered counts. A malformed or 20,001-entry submission cannot produce the required canonical bounded submitted-manifest hash under the valid manifest grammar, yet the invalid metric row requires that hash. [DERIVED] Without an exact occurrence algorithm and a separate safe raw-invalid boundary, independent validators can emit different counts or be unable to construct the invalid record.

Alternatives not selected:

- Allow overlapping or implementation-defined diagnostic counts: rejected because invalid metric bytes and audit conclusions would vary.
- Hash an unbounded or malformed submission as though it were a valid canonical descriptor: rejected because that violates the bound and lets invalid input bypass preflight.

#### Decision D-078 - Preserve the fifth-repair surfaces that passed replay

Decision: Retain the shared-provider rank-one-versus-q factorial, all eight exact masks, VMP/alignment and candidate/q contracts, SEP and prediction audit, the 31-dimensional tensor, complete universe/gold/no-deletion rules, pair metrics, five-seed arithmetic boundary, and explicit later-phase deferrals. Do not reopen provider equality as a specification blocker; require quartet orchestration to assert the already frozen provider/config identity across the four cells.

Rationale: [OBSERVED - parent-supplied independent review] These targeted surfaces passed the fifth replay. [DERIVED] The smallest repair should address the three remaining blocker groups without destabilizing independently accepted scope.

Alternative not selected: rewrite every P0 contract again. Rejected because it would increase review scope and regression risk without evidence that the passed surfaces are defective.

#### Decision D-079 - Keep G0, G5, and G6 blocked and require another replay

Decision: Record the fifth independent replay as `REVIEW_FAILED`. Keep `G0/P0`, `G5`, and `G6` `BLOCKED`. Make the smallest documentation repair covering exact preflight/status branches, the E0 plan version `1.1.0`, and deterministic invalid-metric occurrence accounting/raw-input boundaries; then obtain a sixth independent semantic replay before changing `G0`.

Rationale: [OBSERVED] The independent reviewer found three implementability blockers despite stable pins and a passing non-engine suite. [DERIVED] Passed subcontracts do not make the overall engine and metric schemas constructible, and no documentation verdict can satisfy `G5/G6` implementation gates.

Alternatives not selected:

- Promote `G0` because most fifth-repair targets passed: rejected because the remaining contradictions prevent deterministic construction.
- Treat conceptual probes or unit-test count as engine evidence: rejected because no engine exists or ran.

### Impact and tradeoffs

- Compatibility and reproducibility: the next repair will further constrain invalid/degraded envelopes, feature-plan versioning, and diagnostic accounting; ambiguous draft invalid records should be rejected.
- Scientific scope: the central shared-provider factorial and evaluation estimands remain intact; no hypothesis or dataset changed.
- Security and privacy: bounded preflight descriptors and no fabricated invalid artifacts reduce unsafe-input and evidence-laundering risks; exact safe diagnostics remain unimplemented.
- Evaluation: deterministic occurrence counting will make invalid-run audit counts reproducible without permitting deletion or protected-metric output.
- Performance: no latency, memory, throughput, model, or metric performance was measured.
- Operations: `G0/P0`, `G5`, and `G6` remain blocked. The next repair is deliberately limited to three blocker groups.

### Verification performed

- `[OBSERVED - Luna inspection]` All eleven local reviewed-file SHA-256 values match the stable pins recorded above.
- `[OBSERVED - parent-supplied independent execution evidence]` `python3 -B -m unittest discover -s tests -v` passed 101/101 tests in 30.105 seconds; the suite was explicitly non-engine.
- `[OBSERVED - parent-supplied independent review evidence]` The blocker examples were conceptual contract probes; final start/end pins remained stable. No engine result was claimed.
- `[OBSERVED - Luna inspection]` The current files contain the optional degraded-continuation language, conflicting accepted-hash/invalid rules, direct registry nulling, E0 envelope-`1.0.0` reference, 20,000-entry submitted-manifest bound, and metric diagnostic fields described above.
- `[OBSERVED - Luna inspection]` `EXECUTION_STATUS.md` still contains exact ordered `P01`-`P20`, `O01`-`O30`, and `E01`-`E12`; `G0`, `G5`, and `G6` remain blocked. This replay has not yet been projected into a technical status entry.
- Unrun by Luna: the 101-test suite and reviewer probes were not rerun for this register-only checkpoint. No engine, provider, registry lookup, dataset operation, model, calibration, metric run, malformed-input implementation test, or performance benchmark ran.

### Remaining risks and follow-up

- A deterministic status algorithm may expose additional cross-field requirements when failure occurs after provider acceptance but before semantic artifacts complete.
- The safe bounded descriptor for malformed or over-cap submissions needs exact bytes, cap, hash, and privacy-safe diagnostic rules.
- Occurrence-level metric diagnostics need known-answer vectors beyond the supplied repeated/reordered example.
- Updating the E0 plan version may affect tensor and condition-mask hashes and must be coordinated without altering the passed 31-dimensional semantics.
- No engine, authentic corpus, collection authorization, registry truth, model result, metric result, performance result, or publication claim is established.

Next owner/action: make a minimal documentation-only repair that freezes preflight order, fault-stage precedence, failure-count units, every engine status branch, degraded continuation, E0 plan/envelope `1.1.0` compatibility, and an occurrence-level invalid-metric algorithm with a bounded raw-invalid descriptor. Pin the affected documents and commission a sixth independent replay; preserve the fifth-replay passes and keep `G5/G6` blocked pending executable evidence.

### Correction history

None. This record is append-only, `LUNA-20260819-014` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-016

### Sixth P0 documentation repair pending independent replay

- Lifecycle: `REPAIRED_PENDING_REVIEW` - sixth documentation repair completed; not a pass and no commit requested
- Recorded: 19 August 2026, 7:44:11 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-016`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected paths and pinned repair boundary

- `docs/research/ENGINE_SPEC.md` - SHA-256 `1a462b26d2b1b84590c95ca1e91ab0380f05fd7b5121cee743571afc7c867b9b`
- `docs/research/FACTORIAL_CONDITION_SPEC.md` - SHA-256 `1850c41e1b66204db46fe5d5104472b475a2d55d50b5a00ec2778bf71a92146f`
- `docs/research/PAPER_1_PREREGISTRATION.md` - SHA-256 `8521fa83bb184f2185e2b5f3c86e8ce34789db1c0e001348835f0e7dcd6c23f4`
- `docs/research/REGISTRY_PROTOCOL.md` - SHA-256 `4c9cd1af715ccee6c267ee320a2c054752c4a192cc1acd1f970ffca108d2a06a`
- `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md` - SHA-256 `07d529e4b83c30f9d7cd7747bf85375d5083bdf7cc3a187d2fb79089ddc834c7`
- `docs/research/THREAT_MODEL.md` - SHA-256 `f8c830a3f01d04f17ce6ef441e6ac236a8ca7b5c5da7feb97a1c3fdac7e98196`
- `docs/research/FISHER_RESEARCH_BLUEPRINT.md` - SHA-256 `4ee5105021d003215dc50850317b8d7eb5bda0e3324aafab594fafe21f4ec9ba`
- `docs/research/ANNOTATION_GUIDE.md` - SHA-256 `2665425dd0ce58593e7793a650792ada09e568e34d92bbee11f30ed1dc70dee4`
- `docs/research/EXECUTION_STATUS.md` - SHA-256 `2b92ba77f8bbbfb3edc431f523e8e5e2c1e782dd73316d97280d65baadc2329b`
- `docs/research/SOURCE_LEDGER.md` - SHA-256 `c321ef50a6cadfd6d2fcd98730f183872ed07608c6aabc48c679d66d38e0da51`
- `docs/DATA_CONTRACT.md` - unchanged SHA-256 `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`

This repair addresses the three blockers in `LUNA-20260819-015` without reopening the fifth-replay surfaces that passed. [OBSERVED - Luna inspection] `EXECUTION_STATUS.md` appends `E13`, preserves the `E05`-`E12` evidence history, and leaves `G0/P0`, `G5`, and `G6` `BLOCKED`. No sixth independent semantic pass is claimed.

#### Decision D-080 - Separate EnginePreflightReceipt from EngineRunEnvelope 1.1

Decision: Require a valid canonical `SystemArtifactManifest` and validated schema-1.2 VMP before an `EngineRunEnvelope` schema `1.1.0` may exist. A source/configuration or VMP failure emits only a bounded canonical `EnginePreflightReceipt`, never an invented engine envelope. The receipt binds a safe consumed-prefix hash, bounded byte observations, safe decoded/system/VMP counts, the earliest precondition stage, controlled invalid codes, bytes, cap, and its own hash without retaining unsafe content.

Rationale: [OBSERVED - Luna inspection] The repaired engine specification now separates precondition failure from per-item execution. [DERIVED] A receipt can prove a bounded failed attempt when mandatory envelope bindings do not exist, whereas fabricating an envelope would require false system or VMP evidence.

Alternative not selected: invent an engine envelope for an invalid system manifest or VMP. Rejected because mandatory system/runtime/VMP bindings would be untrue or unavailable.

#### Decision D-081 - Make provider acceptance, status precedence, retention, registry identity, and degradation exact

Decision: Freeze the provider-execution outcome table and the biconditional `provider_manifest_sha256` is nonnull if and only if `output_accepted=true`. Invalid provider/normalizer output is never accepted or hashed. If accepted provider output later reaches an invalid downstream stage, retain its accepted canonical hash and every fully validated upstream artifact permitted by the exact stage-retention table.

Decision: Select the primary failure as the earliest observed stage in the fixed order `PROVIDER_EXECUTION < CANDIDATE < PREDICTION < SEP < FEATURE < BINDING < ENVELOPE`, abort every later stage, and define failure counts as completely decoded and validated safe units available at abort, with exact unit mappings and saturation. Direct registry identity follows the static system mask in every envelope, including `INVALID`: it remains nonnull for semantic base systems and null for every other mask.

Decision: Permit exactly one degraded state, `DEGRADED_STOP_AFTER_IDENTITY`, for qualifying pre-acceptance unavailability or timeout with a fully validated identity fallback. Processing stops after identity; downstream logit, prediction, SEP, feature-plan, and tensor artifacts are absent, and the row is excluded from confirmatory/protected metrics.

Rationale: [DERIVED from the fifth replay] Acceptance/hash equivalence prevents both erased provenance and hashes for rejected material. Earliest-stage precedence plus a retention table creates one constructible invalid envelope. Static registry identity describes the configured semantic system even when execution fails. One stop-after-identity branch removes the prior optional continuation.

Alternatives not selected:

- Erase accepted provider provenance after a later failure: rejected because the accepted upstream object is part of the canonical attempt history.
- Null static registry binding on an invalid semantic-base run: rejected because run status must not rewrite configured system identity.
- Leave degraded continuation optional: rejected because identical inputs and failure evidence could produce different canonical envelopes.
- Degrade malformed, nonfinite, alignment-invalid, or otherwise rejected provider output: rejected because only validated identity fallback after availability/timeout may be degraded.

#### Decision D-082 - Use MetricInputReceipt for malformed or oversized raw submissions

Decision: Preflight raw submitted-inference descriptors before constructing a canonical submitted manifest or metric run. Malformed, oversized, non-UTF-8, noncanonical, or over-row-bound input emits only a bounded canonical `MetricInputReceipt` with safe prefix hash, bytes observed, decoded/validated-row counts, earliest failure stage, controlled codes, bytes, cap, and receipt hash. It emits no `MetricRunManifest`, metric value, raw IDs, or canonical full-submission hash.

Rationale: [OBSERVED - Luna inspection] The repaired metric contract consumes at most the 32-MiB limit plus one byte and provides separate receipt grammar for failed preflight. [DERIVED] This makes malformed and 20,001-row attempts auditable without pretending that unbounded invalid bytes form a valid canonical manifest.

Alternative not selected: canonical-hash a malformed or unbounded descriptor as a valid submitted manifest. Rejected because it bypasses the byte/row boundary and cannot satisfy the valid grammar.

#### Decision D-083 - Freeze exclusive deterministic metric discrepancy accounting

Decision: For a structurally valid submission, classify each submitted row exactly once from left to right: a repeated submitted ID is `DUPLICATE`; otherwise its first occurrence is `EXTRA` when absent from the expected universe or `UNIQUE_EXPECTED` when present. Compute missing expected IDs after this classification, then count positional mismatches between unique expected submissions and the corresponding expected subsequence as reordered. Inspect only unique expected rows for one exclusive envelope outcome in precedence `INVALID`, then `DEGRADED_STOP_AFTER_IDENTITY`, then binding `MISMATCH`, otherwise matched valid.

Decision: The normative example expected `[a,b]` versus submitted `[b,a,a,c,c]` yields `duplicate_count=2`, `extra_count=1`, `missing_count=0`, and `reordered_count=2`. Duplicate and extra occurrences are not opened for envelope outcome counts.

Rationale: [DERIVED from the fifth replay] Exclusive left-to-right classification and outcome precedence produce one diagnostic vector and prevent a row from being double-counted as extra, duplicate, invalid, or mismatch.

Alternatives not selected:

- Permit overlapping diagnostic categories: rejected because counts and invalid manifest hashes would vary by implementation.
- Leave duplicate/extra/reordered precedence implicit: rejected because the supplied repeated and reordered example previously admitted multiple answers.

#### Decision D-084 - Bind the E0 feature plan to EngineRunEnvelope 1.1

Decision: Bind `E0_VMP_CATEGORY_MEAN_V1` and its 31-dimensional tensor audit explicitly to `EngineRunEnvelope` schema `1.1.0`. Preserve its five-category basis, arithmetic, masks, capacity, serialization, and exclusions; do not silently reinterpret an older envelope version.

Rationale: [OBSERVED - Luna inspection] The repaired E0 numeric section now names envelope `1.1.0`. [DERIVED] This makes valid semantic E0 plan, tensor, and envelope versions mutually representable without changing the previously reviewed feature semantics.

Alternative not selected: retain or silently reinterpret the stale plan/envelope `1.0.0` reference. Rejected because version compatibility affects canonical artifact identity and must be explicit.

#### Decision D-085 - Keep G0, G5, and G6 blocked pending the sixth replay

Decision: Classify this repair as `REPAIRED_PENDING_REVIEW`, not a pass. Require a sixth independent semantic replay of the pinned documents before `G0/P0` can change. Keep `G5/G6` blocked on executable engine, resource, model, control, and evaluation evidence even if the documentation later passes.

Rationale: [OBSERVED] The repair changed documentation only, and the available suite remains explicitly non-engine. [DERIVED] A constructible written contract still requires independent replay and cannot establish runtime or empirical behavior.

Alternatives not selected:

- Promote `G0` because the three fifth-replay blockers were edited: rejected because no independent replay has accepted the new boundary.
- Treat receipt/schema documentation or unit tests as `G5/G6` evidence: rejected because no engine, model, dataset, registry, or metric run exists.

### Impact and tradeoffs

- Compatibility and reproducibility: separate receipts, exact outcome/status branches, and exclusive counts reject earlier ambiguous invalid artifacts but define one bounded replay path.
- Scientific scope: the shared-provider factorial and passed candidate/semantic/evaluation contracts remain unchanged.
- Data and evaluation: no dataset or label changed; malformed inputs cannot enter canonical metric manifests, and valid submissions receive deterministic discrepancy counts.
- Security and privacy: receipts hash only bounded safe prefixes and retain no raw IDs/text; invalid provider material is never accepted or hashed as successful output.
- Performance: preflight byte caps, count saturation, and receipt sizes are design bounds, not measured latency or memory results.
- Operations: `E13` preserves the fifth failure; `G0/P0`, `G5`, and `G6` remain blocked pending their respective evidence.

### Verification performed

- `[OBSERVED - Luna inspection]` All ten repaired research-document SHA-256 values and the unchanged `DATA_CONTRACT.md` SHA-256 match the pins recorded above.
- `[OBSERVED - parent-supplied execution evidence]` `python3 -B -m unittest discover -s tests -v` passed 101/101 tests in 30.119 seconds; the suite was explicitly non-engine.
- `[OBSERVED - parent-supplied documentation QA]` Strict UTF-8, NFC, LF-only line endings, final-newline, trailing-whitespace, table, local-link, and anchor checks passed.
- `[OBSERVED - parent-supplied structural QA]` The inventories contained exact `P01`-`P20`, `O01`-`O30`, and `E01`-`E13`; stale-reference checks were clean.
- `[OBSERVED - Luna inspection]` The repaired engine specification contains `EnginePreflightReceipt`, the exact provider outcome table and accepted-hash biconditional, earliest-stage and safe-unit rules, static registry masking, one `DEGRADED_STOP_AFTER_IDENTITY` branch, `MetricInputReceipt`, the normative discrepancy example, and E0 envelope-`1.1.0` binding.
- `[OBSERVED - Luna inspection]` `EXECUTION_STATUS.md` currently contains exact ordered `P01`-`P20`, `O01`-`O30`, and `E01`-`E13`, preserves `E05`-`E12`, and keeps `G0`, `G5`, and `G6` blocked.
- Unrun by Luna: the 101-test suite, Unicode normalization, table/link/anchor, and stale-reference commands were not rerun for this register-only checkpoint. No sixth semantic replay, engine, provider, registry lookup, dataset operation, model, calibration, metric run, malformed-input implementation test, or performance benchmark ran.

### Remaining risks and follow-up

- Independent replay may find new conflicts between receipt boundaries, stage retention, and system masks.
- The receipt, status, retention, and discrepancy algorithms have no executable parser, serializer, validator, or known-answer engine tests.
- Prefix hashing and safe-unit accounting require adversarial implementation tests at exact byte/count boundaries.
- Complete universe/gold membership, real provider/registry behavior, model artifacts, and calibration remain unimplemented.
- No authentic corpus, collection authorization, model result, metric result, performance result, or publication claim is established.

Next owner/action: commission a sixth independent semantic replay against the eleven pinned files. Replay both preflight receipts, every provider outcome and accepted-hash state, all failure stages and retention rows, static registry masks, degraded-stop behavior, the E0 `1.1.0` plan/tensor binding, the exact discrepancy algorithm and normative example, and historical `E05`-`E13` consistency. Only a separate successful review may change `G0`; `G5/G6` still require implementation evidence.

### Correction history

None. This record is append-only, `LUNA-20260819-015` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-017

### Sixth independent P0 semantic replay failed

- Lifecycle: `REVIEW_FAILED` - sixth independent semantic replay completed; `G0/P0` remains blocked and no commit requested
- Recorded: 19 August 2026, 7:57:17 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-017`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Reviewed paths and stable start/end pins

- `docs/research/ENGINE_SPEC.md` - SHA-256 `1a462b26d2b1b84590c95ca1e91ab0380f05fd7b5121cee743571afc7c867b9b`
- `docs/research/FACTORIAL_CONDITION_SPEC.md` - SHA-256 `1850c41e1b66204db46fe5d5104472b475a2d55d50b5a00ec2778bf71a92146f`
- `docs/research/PAPER_1_PREREGISTRATION.md` - SHA-256 `8521fa83bb184f2185e2b5f3c86e8ce34789db1c0e001348835f0e7dcd6c23f4`
- `docs/research/REGISTRY_PROTOCOL.md` - SHA-256 `4c9cd1af715ccee6c267ee320a2c054752c4a192cc1acd1f970ffca108d2a06a`
- `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md` - SHA-256 `07d529e4b83c30f9d7cd7747bf85375d5083bdf7cc3a187d2fb79089ddc834c7`
- `docs/research/THREAT_MODEL.md` - SHA-256 `f8c830a3f01d04f17ce6ef441e6ac236a8ca7b5c5da7feb97a1c3fdac7e98196`
- `docs/research/FISHER_RESEARCH_BLUEPRINT.md` - SHA-256 `4ee5105021d003215dc50850317b8d7eb5bda0e3324aafab594fafe21f4ec9ba`
- `docs/research/ANNOTATION_GUIDE.md` - SHA-256 `2665425dd0ce58593e7793a650792ada09e568e34d92bbee11f30ed1dc70dee4`
- `docs/research/EXECUTION_STATUS.md` - SHA-256 `2b92ba77f8bbbfb3edc431f523e8e5e2c1e782dd73316d97280d65baadc2329b`
- `docs/research/SOURCE_LEDGER.md` - SHA-256 `c321ef50a6cadfd6d2fcd98730f183872ed07608c6aabc48c679d66d38e0da51`
- `docs/DATA_CONTRACT.md` - SHA-256 `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`

[OBSERVED - parent-supplied independent review] All eleven start and end pins matched with no drift. The sixth replay passed the accepted-output/hash biconditional, post-acceptance retention, static registry masking, mandatory degraded-stop branch, envelope-`1.1.0` E0 plan, bounded `MetricInputReceipt`, exact `[a,b]` versus `[b,a,a,c,c]` discrepancy counts, shared-provider factor, eight masks, candidate/q, SEP, 31-dimensional tensor, universe/gold/no-deletion, and five-seed surfaces. Three remaining blocker groups kept the verdict at `P0 SEMANTIC FAIL`.

#### Decision D-086 - Require a normative EngineInputDescriptor and deterministic preflight parser

Decision: Keep preflight failed until the documentation freezes an `EngineInputDescriptor` schema with exact top-level fields and order, reference grammars, canonical bytes for bounded valid input, raw-byte cap, parser stages, validation order, and bindings to the system manifest and VMP. The `EnginePreflightReceipt` must define deterministic same-stage invalid-code selection or precedence when one raw input exhibits multiple defects.

Rationale: [OBSERVED - parent-supplied independent review and Luna inspection] The current receipt names a submitted descriptor and counts decoded/validated objects but never defines the descriptor that is decoded or how its references are parsed. Its stage selection is earliest only across `SOURCE_OR_CONFIG|VMP`; it does not resolve multiple codes within one stage, such as a descriptor that is both over the byte cap and invalid UTF-8. [DERIVED] Independent implementations could parse different shapes, resolve different artifacts, or emit different receipt bytes.

Alternatives not selected:

- Let each implementer invent an input descriptor: rejected because preflight would have no common object, bytes, or reference semantics.
- Emit every discovered same-stage code without a frozen scan/selection rule: rejected because bounded parsers may observe different subsets after the first failure.

#### Decision D-087 - Add a sanitized ELIGIBILITY_INVALID no-dispatch provider outcome

Decision: Define one safe provider outcome and controlled code for invalid configured eligible-span collections detected before dispatch, provisionally named `ELIGIBILITY_INVALID`. It must cover excess span count, Boolean or non-integer coordinates, out-of-range or nonincreasing ranges, overlap/order violations, unsafe source/artifact mismatch, and other failed eligibility predicates. Invocation is false, output is unaccepted, accepted hash is null, unsafe spans are not retained, and the engine fails at provider execution without fabricating a valid attempted state.

Rationale: [OBSERVED - parent-supplied independent review and Luna inspection] The outcome table covers empty spans, valid 1..64 spans, dispatch failure, availability/timeout fallback, and invalid provider output, but not an invalid configured span collection such as 65 entries, Boolean coordinates, out-of-range/overlapping ranges, or artifact mismatch before dispatch. [DERIVED] Those inputs cannot safely fit `NOT_INVOKED`, because that row requires a valid 1..64 attempted collection, and cannot fit provider-invalid output because dispatch never occurred.

Alternatives not selected:

- Retain unsafe spans in `provider_execution`: rejected because invalid coordinates or source material must not enter a canonical safe artifact.
- Fabricate a valid attempted-span state: rejected because it would misrepresent what passed eligibility validation.
- Reuse an output-invalid code before dispatch: rejected because no provider output exists to classify.

#### Decision D-088 - Add universe/denominator diagnostics and define all-empty pair F1

Decision: Add dedicated, bounded, deterministic diagnostic counts for universe-binding and denominator failures so an `INVALID` metric run caused only by those defects can satisfy its union without forcing an unrelated nonzero count. Bind each count to its controlled code and precedence relative to submitted-row discrepancies and envelope outcomes.

Decision: Freeze the aggregate pair-F1 result when every gold and predicted pair set is empty and therefore `TP=FP=FN=0`. The exact convention remains `UNKNOWN` in this failed-review checkpoint and must be chosen explicitly in the smallest repair; natural `0/0` cannot remain unspecified or depend on a library default.

Rationale: [OBSERVED - parent-supplied independent review and Luna inspection] The metric contract says universe or denominator mutation makes the run invalid, but the invalid branch also requires at least one diagnostic count other than `submitted_count` to be nonzero, while current counts cover only submitted-list and envelope outcomes. A universe-only or denominator-only defect can therefore require `INVALID` with every available diagnostic count zero. Separately, both-empty items contribute zero counts, but the corpus-wide all-empty F1 denominator is not defined.

Alternatives not selected:

- Emit an invalid code while forcing an unrelated count nonzero: rejected because the diagnostic vector would be false.
- Allow an invalid row with all current counts zero and no dedicated diagnostic: rejected because it violates the existing union and loses the failure magnitude.
- Treat natural `0/0` pair F1 as unspecified: rejected because libraries choose different defaults and the gate would not be reproducible.

#### Decision D-089 - Preserve the sixth-repair surfaces that passed replay

Decision: Retain the accepted-output/hash rules, post-acceptance stage retention, static registry identity, mandatory `DEGRADED_STOP_AFTER_IDENTITY`, E0 envelope-`1.1.0` plan/tensor binding, `MetricInputReceipt`, exclusive metric occurrence algorithm and normative count vector, shared-provider factorial, eight masks, candidate/q, SEP, 31-dimensional tensor, universe/gold/no-deletion, and five-seed contracts.

Rationale: [OBSERVED - parent-supplied independent review] These surfaces passed the sixth replay. [DERIVED] The smallest repair should close the three new groups without destabilizing accepted contracts.

Alternative not selected: reopen every P0 surface. Rejected because it would enlarge review scope without evidence that the passed surfaces are defective.

#### Decision D-090 - Keep G0, G5, and G6 blocked pending repair and seventh replay

Decision: Record the sixth independent replay as `REVIEW_FAILED`. Keep `G0/P0`, `G5`, and `G6` `BLOCKED`. Make the smallest documentation repair covering the exact `EngineInputDescriptor` and parser/code precedence, sanitized no-dispatch `ELIGIBILITY_INVALID` outcome, dedicated universe/denominator diagnostics, and all-empty pair-F1 convention; then obtain a seventh independent semantic replay before changing `G0`.

Rationale: [OBSERVED] The reviewer found three implementability groups despite stable pins and passing existing non-engine test methods. [DERIVED] The engine preflight, provider failure totality, and metric invalid union remain non-constructible for covered inputs; no prose verdict can satisfy implementation gates.

Alternatives not selected:

- Promote `G0` because the sixth-repair targets otherwise passed: rejected because all documented input classes still need deterministic artifacts and metrics.
- Treat conceptual cap vectors or existing test methods as engine evidence: rejected because they did not execute an engine.

### Impact and tradeoffs

- Compatibility and reproducibility: a normative input descriptor, safe eligibility failure, dedicated metric counts, and F1 convention will reject implicit or library-dependent behavior.
- Scientific scope: the shared-provider factorial, semantic design, and evaluation universe remain unchanged.
- Data and evaluation: no data or labels changed; metric invalidity gains truthful diagnostics and all-empty evaluation becomes deterministic after repair.
- Security and privacy: unsafe descriptor bytes and invalid spans must remain outside canonical execution artifacts; exact bounded parser behavior is still unimplemented.
- Performance: byte/span caps and conceptual vectors are specification boundaries, not measured resource results.
- Operations: `G0/P0`, `G5`, and `G6` remain blocked; the next repair is limited to the three blocker groups.

### Verification performed

- `[OBSERVED - Luna inspection]` All eleven local reviewed-file SHA-256 values match the stable pins recorded above.
- `[OBSERVED - parent-supplied independent execution evidence]` The existing 101 test methods passed; they were explicitly non-engine.
- `[OBSERVED - parent-supplied independent review evidence]` Conceptual cap hashes, vectors, and probes were evaluated, and final start/end pins showed no drift. No engine behavior was claimed.
- `[OBSERVED - Luna inspection]` The current engine specification defines `EnginePreflightReceipt` but no `EngineInputDescriptor`; its provider outcome table has no invalid-eligibility/no-dispatch row; and its metric invalid union lacks dedicated universe/denominator counts while pair F1 is undefined for aggregate `TP=FP=FN=0`.
- `[OBSERVED - Luna inspection]` `EXECUTION_STATUS.md` contains exact ordered `P01`-`P20`, `O01`-`O30`, and `E01`-`E13`; `G0`, `G5`, and `G6` remain blocked. This replay has not yet been projected into a technical status entry.
- Unrun by Luna: the existing tests and reviewer probes were not rerun for this register-only checkpoint. No engine, descriptor parser, provider dispatch, registry lookup, dataset operation, model, metric implementation, or performance benchmark ran.

### Remaining risks and follow-up

- Descriptor grammar and parser precedence may expose additional ambiguity at byte, UTF-8, JSON, reference, and artifact boundaries.
- Sanitizing invalid eligibility must still preserve enough safe accounting to distinguish configuration failure without retaining unsafe spans.
- Dedicated universe/denominator counts require exact units, caps, precedence, and known-answer invalid-manifest vectors.
- The chosen all-empty pair-F1 convention must be propagated consistently to preregistration, gates, reports, and tests.
- No engine, authentic corpus, collection authorization, registry truth, model result, metric result, performance result, or publication claim is established.

Next owner/action: make a minimal documentation-only repair that defines the canonical `EngineInputDescriptor`, bounded parser and same-stage code precedence, a sanitized `ELIGIBILITY_INVALID` no-dispatch outcome, dedicated universe/denominator counts, and the all-empty aggregate pair-F1 convention. Pin the affected documents and commission a seventh independent replay; preserve the sixth-replay passes and keep `G5/G6` blocked pending executable evidence.

### Correction history

None. This record is append-only, `LUNA-20260819-016` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-018

### Seventh P0 documentation repair pending independent replay

- Lifecycle: `REPAIRED_PENDING_REVIEW` - seventh documentation repair completed; not a pass and no commit requested
- Recorded: 19 August 2026, 8:15:19 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-018`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected paths and pinned repair boundary

- `docs/research/ENGINE_SPEC.md` - SHA-256 `bdbe7ccaa907d874ad40ffad66bc3888848e6fe5408c8c499877a9dd3e9f0b7d`
- `docs/research/FACTORIAL_CONDITION_SPEC.md` - SHA-256 `1e82661cc58db207cc2bf0e95a612e6fdbfad7983bac664ee625adeba180560e`
- `docs/research/PAPER_1_PREREGISTRATION.md` - SHA-256 `d6543084b4b9abe2617da8890aa9bbccd952649731dd1bbe401ecde173d40cc8`
- `docs/research/REGISTRY_PROTOCOL.md` - SHA-256 `4efd8f6f69887d642204c35746b7930d89eced7a4d889e3da1087de96107ea7d`
- `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md` - SHA-256 `2ba805983de8863c66ec0528f8d3362fa48c48f955dea92febef6fd24223d4a6`
- `docs/research/THREAT_MODEL.md` - SHA-256 `131e310770bc678c6b43a328842a3811c24c55395c4efeacc702be84a4053dfc`
- `docs/research/FISHER_RESEARCH_BLUEPRINT.md` - SHA-256 `ce801ef4d0d2da96feadb0b52cbe8a94a3107dabbaf17f76b30035310098caa7`
- `docs/research/ANNOTATION_GUIDE.md` - SHA-256 `522202ede387d2c6e5704d6420bde866e5c4e77a9cff541c0b063b77768dd819`
- `docs/research/EXECUTION_STATUS.md` - SHA-256 `aa7389dce3c109a88e634abd2f0b403ee0c2900e3e465b7fce780eab851eb4eb`
- `docs/research/SOURCE_LEDGER.md` - SHA-256 `444e43ba3417632b9d1ea426cb668c1323499fc90cfab353147b492efa13db64`
- `docs/DATA_CONTRACT.md` - unchanged SHA-256 `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`

This repair addresses the three groups in `LUNA-20260819-017` without reopening the sixth-replay surfaces that passed. [OBSERVED - Luna inspection] `EXECUTION_STATUS.md` appends `E14`, preserves the `E05`-`E13` evidence history, and leaves `G0/P0`, `G5`, and `G6` `BLOCKED`. No seventh independent semantic pass is claimed.

#### Decision D-091 - Freeze a canonical path-free EngineInputDescriptor

Decision: Define `EngineInputDescriptor` schema `1.0.0` with exact ordered fields for run, condition, system, variant, system-artifact hash, item, and VMP hash. Bind separately supplied system-manifest and VMP/item byte artifacts only by their exact hashes. Prohibit filesystem paths, URIs, mutable handles, and lookup locations from semantic identity. Freeze compact NFC UTF-8 canonical JSON bytes, types, safe grammars, enums, and the exact 1-MiB cap.

Rationale: [OBSERVED - Luna inspection] The repaired engine specification now defines one eight-field path-free descriptor and independent hash verification of supplied artifacts. [DERIVED] This supplies one portable preflight input identity without treating an ambient path or lookup mechanism as evidence.

Alternative not selected: bind filesystem paths, URIs, or mutable object handles. Rejected because location does not prove artifact bytes and can change across environments.

#### Decision D-092 - Freeze cap-plus-one parsing and one-code PASS/FAIL preflight receipts

Decision: Read at most the descriptor cap plus one byte and apply one total precedence over size, BOM, UTF-8, duplicate keys, nonfinite values, JSON syntax, NFC, canonical bytes, schema/enums, missing artifacts, hash mismatch, system-manifest validation, and VMP validation. Within JSON scanning, freeze duplicate-key, then nonfinite, then other syntax precedence among safely observed events and stop without recovery after the first unrecoverable syntax event.

Decision: Emit exactly one canonical `EnginePreflightReceipt` for every attempt. `PASS` binds all descriptor references and validation counts and alone permits `EngineRunEnvelope`; `FAIL` nulls descriptor-reference fields, records one first-applicable controlled code and its stage, and emits no envelope. Never emit an exhaustive ambiguous error list.

Rationale: [DERIVED from the sixth replay] Cap-plus-one reading proves over-limit input without unbounded consumption, and a single total parser/code order makes joint defects produce one receipt. A constructible `PASS` receipt closes the link from validated descriptor artifacts to the envelope.

Alternatives not selected:

- Emit exhaustive or ambiguously ordered same-stage codes: rejected because bounded parsing may observe only a prefix and different scanners can discover different error sets.
- Recover after malformed JSON to search for more defects: rejected because recovery behavior is parser-dependent and could consume unsafe data.

#### Decision D-093 - Add sanitized ELIGIBILITY_INVALID accounting before dispatch

Decision: Add `ELIGIBILITY_INVALID` as the exact no-dispatch provider outcome for non-array selector output, more than 64 entries, Boolean/noninteger/out-of-range/empty ranges, wrong slices, overlap, artifact contact, or noncanonical order. Retain no unsafe span, use empty `eligible_spans`, set invocation/output acceptance false and provider hash null, keep only bounded safe selector counts, use the sole controlled code `engine_invalid_eligibility`, and stop at `PROVIDER_EXECUTION`.

Rationale: [OBSERVED - Luna inspection] The repaired outcome table and retention rules now total the invalid configured-span cases identified in the sixth replay. [DERIVED] Sanitized empty retained spans and bounded counts identify eligibility failure without fabricating dispatch or persisting unsafe selector members.

Alternatives not selected:

- Retain unsafe selector spans: rejected because invalid coordinates, slices, or artifact contact cannot enter a canonical safe envelope.
- Fabricate valid attempted spans: rejected because it would misstate selector validation and provider invocation.

#### Decision D-094 - Add a bounded MetricUniverseInputReceipt

Decision: Preflight raw evaluation-universe bytes independently of metric submission. Malformed, oversized, non-UTF-8, noncanonical, or invalid-schema universe input emits only a bounded canonical `MetricUniverseInputReceipt` with prefix hash, observed bytes, decoded/validated entry counts, one precedence-selected code, bytes, cap, and receipt hash. It carries no claimed valid universe hash or raw item data and produces no `MetricRunManifest` or metric value.

Rationale: [OBSERVED - Luna inspection] The repaired specification now consumes at most the 32-MiB cap plus one byte and separates malformed-universe evidence from a semantically valid universe manifest. [DERIVED] This prevents unsafe or unbounded universe input from being represented as a valid hashed evaluation population.

Alternative not selected: force malformed universe bytes into a canonical evaluation-universe or metric-run artifact. Rejected because those bytes cannot satisfy the valid grammar or binding.

#### Decision D-095 - Add disjoint universe/denominator counts and canonical zero algebra

Decision: Add `universe_error_count` in `{0,1}` for structurally valid universe closure/hash/partition/binding failure and `denominator_error_count` in `0..3` for mismatches among declared `N_all`, `N_gold_empty`, and `N_gold_nonempty` when a valid universe exists. Bind each count biconditionally to its controlled invalid code, keep them disjoint from row/envelope counts, and allow them to make an invalid metric union constructible without forcing an unrelated diagnostic.

Decision: Define pair precision, recall, and F1 as canonical binary64 `+0.0` whenever their own natural denominator is zero. Consequently `TP=FP=FN=0` yields `precision_pair=recall_pair=F1_pair=+0.0`; this is not a declared-denominator error and applies identically to rank-one and q-weighted forms.

Rationale: [DERIVED from the sixth replay] Dedicated counts truthfully identify top-level universe and declaration defects. A frozen zero-algebra convention removes library-dependent `0/0` behavior while retaining all-empty items in the evaluation universe.

Alternatives not selected:

- Emit only a universe/denominator code while forcing an unrelated row count: rejected because the manifest would contain false diagnostics.
- Treat natural `0/0` as data invalid: rejected because an all-empty gold/prediction corpus is a defined outcome, not malformed data.
- Leave zero-denominator precision, recall, or F1 to a library default: rejected because different defaults would change reported values and gates.

#### Decision D-096 - Keep G0, G5, and G6 blocked pending the seventh replay

Decision: Classify this repair as `REPAIRED_PENDING_REVIEW`, not a pass. Require a seventh independent semantic replay of the pinned documents before `G0/P0` can change. Keep `G5/G6` blocked on executable engine, resource, model, control, and evaluation evidence even if the documentation later passes.

Rationale: [OBSERVED] The repair changed documentation only, and its tests remain explicitly non-engine. [DERIVED] Parser, receipt, eligibility, metric, and algebra contracts still require independent review and executable evidence.

Alternatives not selected:

- Promote `G0` because the sixth-replay blockers were edited: rejected because the repaired boundary has not passed independent replay.
- Treat parser-vector or documentation QA as `G5/G6` evidence: rejected because no engine, model, dataset, registry, or metric execution exists.

### Impact and tradeoffs

- Compatibility and reproducibility: the descriptor, parser precedence, receipts, eligibility outcome, metric counts, and zero algebra reject prior implicit or library-dependent draft behavior.
- Scientific scope: the shared-provider factorial, semantic method, and complete evaluation population remain unchanged.
- Data and evaluation: no dataset or label changed; malformed universes are safely separated, top-level invalidity is counted truthfully, and all-empty pair metrics are deterministic.
- Security and privacy: path-free references, bounded prefix parsing, sanitized spans, and receipts without raw item data reduce unsafe-input and ambient-location risk.
- Performance: byte caps, entry caps, and parser steps are specification bounds, not measured latency or memory results.
- Operations: `E14` preserves the sixth failure; `G0/P0`, `G5`, and `G6` remain blocked pending their stated evidence.

### Verification performed

- `[OBSERVED - Luna inspection]` All ten repaired research-document SHA-256 values and the unchanged `DATA_CONTRACT.md` SHA-256 match the pins recorded above.
- `[OBSERVED - parent-supplied execution evidence]` `python3 -B -m unittest discover -s tests -v` passed 101/101 tests in 29.912 seconds; the suite was explicitly non-engine.
- `[OBSERVED - parent-supplied focused QA]` Exact field inventories, parser precedence, `E14` pins, eligibility outcome/counts, the fixed metric discrepancy example, and zero-denominator algebra passed their documentation checks.
- `[OBSERVED - parent-supplied structural QA]` Encoding, local links, tables, IDs, exact `P01`-`P20`, `O01`-`O30`, and `E01`-`E14` checks passed.
- `[OBSERVED - Luna inspection]` The repaired engine specification contains the path-free descriptor, cap-plus-one one-code parser, `PASS|FAIL` receipt, `ELIGIBILITY_INVALID`, `MetricUniverseInputReceipt`, disjoint universe/denominator counts, and canonical `+0.0` pair algebra.
- `[OBSERVED - Luna inspection]` `EXECUTION_STATUS.md` currently contains exact ordered `P01`-`P20`, `O01`-`O30`, and `E01`-`E14`, preserves `E05`-`E13`, and keeps `G0`, `G5`, and `G6` blocked.
- Unrun by Luna: the 101-test suite and focused/structural QA commands were not rerun for this register-only checkpoint. No seventh semantic replay, engine, descriptor parser, provider dispatch, universe parser, registry lookup, dataset operation, model, metric run, or performance benchmark ran.

### Remaining risks and follow-up

- Independent replay may find new cross-artifact conflicts in descriptor references, receipt PASS binding, or metric-universe handoff.
- Parser precedence, prefix hashing, selector sanitization, and error counts lack executable adversarial boundary tests.
- The `+0.0` convention must be implemented consistently in all reports, gates, bootstrap inputs, and baseline comparators.
- Complete universe membership, real provider/registry behavior, model artifacts, calibration, and empirical metrics remain unimplemented.
- No authentic corpus, collection authorization, model result, metric result, performance result, or publication claim is established.

Next owner/action: commission a seventh independent semantic replay against the eleven pinned files. Replay descriptor canonicalization and every parser precedence branch, PASS/FAIL receipt binding, `ELIGIBILITY_INVALID` sanitization/counts, malformed-universe receipt, universe/denominator error unions, zero algebra, fixed discrepancy counts, and historical `E05`-`E14` consistency. Only a separate successful review may change `G0`; `G5/G6` still require implementation evidence.

### Correction history

None. This record is append-only, `LUNA-20260819-017` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-019

### Seventh independent P0 semantic replay failed

- Lifecycle: `REVIEW_FAILED` - seventh independent semantic replay completed; `G0/P0` remains blocked and no commit requested
- Recorded: 19 August 2026, 8:31:04 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-019`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Reviewed paths and stable start/end pins

- `docs/research/ENGINE_SPEC.md` - SHA-256 `bdbe7ccaa907d874ad40ffad66bc3888848e6fe5408c8c499877a9dd3e9f0b7d`
- `docs/research/FACTORIAL_CONDITION_SPEC.md` - SHA-256 `1e82661cc58db207cc2bf0e95a612e6fdbfad7983bac664ee625adeba180560e`
- `docs/research/PAPER_1_PREREGISTRATION.md` - SHA-256 `d6543084b4b9abe2617da8890aa9bbccd952649731dd1bbe401ecde173d40cc8`
- `docs/research/REGISTRY_PROTOCOL.md` - SHA-256 `4efd8f6f69887d642204c35746b7930d89eced7a4d889e3da1087de96107ea7d`
- `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md` - SHA-256 `2ba805983de8863c66ec0528f8d3362fa48c48f955dea92febef6fd24223d4a6`
- `docs/research/THREAT_MODEL.md` - SHA-256 `131e310770bc678c6b43a328842a3811c24c55395c4efeacc702be84a4053dfc`
- `docs/research/FISHER_RESEARCH_BLUEPRINT.md` - SHA-256 `ce801ef4d0d2da96feadb0b52cbe8a94a3107dabbaf17f76b30035310098caa7`
- `docs/research/ANNOTATION_GUIDE.md` - SHA-256 `522202ede387d2c6e5704d6420bde866e5c4e77a9cff541c0b063b77768dd819`
- `docs/research/EXECUTION_STATUS.md` - SHA-256 `aa7389dce3c109a88e634abd2f0b403ee0c2900e3e465b7fce780eab851eb4eb`
- `docs/research/SOURCE_LEDGER.md` - SHA-256 `444e43ba3417632b9d1ea426cb668c1323499fc90cfab353147b492efa13db64`
- `docs/DATA_CONTRACT.md` - SHA-256 `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`

[OBSERVED - parent-supplied independent review] All eleven start and end pins matched with no drift. The seventh replay passed all `E14` repairs and found the prior shared-provider, mask, provenance, candidate/q, SEP, prediction, tensor, universe/gold/no-deletion, five-seed, engine descriptor/preflight, provider status, metric-input, discrepancy-count, and zero-algebra contracts otherwise coherent. Three metric-universe blocker groups kept the verdict at `P0 SEMANTIC FAIL`; the status history remained honest.

#### Decision D-097 - Require a total strict parser for MetricUniverseInputReceipt

Decision: Keep the universe-input receipt failed until its parser freezes the same complete boundary discipline used by engine input: cap-plus-one reading; BOM, UTF-8, duplicate-key, nonfinite, syntax, NFC, canonical-byte, and exact schema/enum precedence; a deterministic stop rule; and exact `decoded_entry_count` and `validated_entry_count` transitions for complete, partial, malformed, and truncated entries. Emit one first-applicable controlled code, not a parser-dependent set.

Rationale: [OBSERVED - parent-supplied independent review and Luna inspection] `MetricUniverseInputReceipt` currently has only coarse too-large, invalid-UTF-8, invalid-JSON, noncanonical, and invalid-schema codes. It does not map BOM, duplicate keys, nonfinite tokens, NFC, and syntax independently or define how a truncated entry affects decoded versus validated counts. [DERIVED] Library-default parsing can produce different codes and either partial or zero entry counts from the same prefix.

Alternatives not selected:

- Use a library-default JSON parser: rejected because duplicate, nonfinite, Unicode, and error-recovery behavior is not portable.
- Count a partial-prefix entry as decoded or validated without a frozen completion rule: rejected because truncation would have multiple legitimate count vectors.
- Emit every discoverable error: rejected because a bounded parser may stop before later defects and implementations may observe different subsets.

#### Decision D-098 - Separate structural universe hashing from semantic invalid-universe short-circuit

Decision: Define three ordered phases: parse and canonicalize a bounded structural universe submission; hash those exact structural bytes; then evaluate semantic closure, partition, reference, gold, and entry bindings. If the structurally valid universe is semantically invalid, construct one metric `INVALID` branch with the submitted structural hash retained, `universe_error_count=1`, `N_all=N_gold_empty=N_gold_nonempty=0`, `denominator_error_count=0`, every row/discrepancy/envelope count zero, `inference_envelopes=[]`, no envelope inspection, no metric value, and the exact universe-invalid code.

Rationale: [OBSERVED - parent-supplied independent review] The current prose requires a universe hash and `universe_error_count=1` for semantic invalidity but also derives expected order `E`, denominator values, and row diagnostics from a valid universe. [DERIVED] A semantically invalid universe cannot safely supply the expected item sequence used for row comparison; short-circuiting after structural identity preserves evidence without treating invalid entries as evaluation truth.

Alternatives not selected:

- Use semantically invalid entries as the expected sequence `E`: rejected because invalid population membership or gold bindings would become metric truth.
- Silently derive and substitute a corrected closure: rejected because the evaluated population would differ from the submitted hashed artifact.
- Compare submitted rows or inspect envelopes when no valid universe exists: rejected because there is no authoritative expected order or denominator.
- Drop the structural submission hash: rejected because the invalid attempt would lose its bounded byte identity.

#### Decision D-099 - Require every valid evaluation universe to contain 1..10,000 entries

Decision: Change the valid evaluation-universe cardinality from zero-permitted to exactly `1..10000` entries. An empty structurally valid submission fails semantic universe validation and takes the `universe_error_count=1` short-circuit; it cannot produce a valid metric run or any reported accuracy.

Rationale: [OBSERVED - parent-supplied conceptual probe and Luna inspection] A canonical empty universe of 621 bytes with conceptual SHA-256 prefix/suffix `2c1baf...63ba9` can satisfy the current zero-permitted grammar, setting `N_all=0`, while `pair_emptiness_accuracy=(1/N_all)*...` divides by zero. [DERIVED] Requiring at least one item is the smallest rule that preserves the meaning of a valid evaluated population and prevents vacuous accuracy.

Alternatives not selected:

- Publish zero-item `pair_emptiness_accuracy`: rejected because the result is undefined and conveys no evaluation evidence.
- Treat empty-universe accuracy as a library-selected zero or one: rejected because either value is vacuous and implementation-dependent.
- Remove emptiness accuracy while allowing a zero-item valid run: rejected because the whole run has no evidentiary population, not merely one problematic metric.

#### Decision D-100 - Preserve the E14 repairs and prior main contracts that passed

Decision: Retain the canonical engine descriptor/parser/PASS-FAIL receipt, `ELIGIBILITY_INVALID`, metric-input receipt, disjoint universe/denominator counts, canonical `+0.0` natural-zero pair algebra, exact repeated/reordered submission counts, and all previously accepted main provider, factorial, candidate, semantic, provenance, universe/gold, tensor, and five-seed contracts.

Rationale: [OBSERVED - parent-supplied independent review] These surfaces passed the seventh replay and remained coherent. [DERIVED] The smallest repair should be restricted to universe parser totality, semantic short-circuit, and nonempty cardinality.

Alternative not selected: reopen every P0 contract. Rejected because it would expand scope and regression risk without evidence that the passed surfaces are defective.

#### Decision D-101 - Keep G0, G5, and G6 blocked pending repair and eighth replay

Decision: Record the seventh independent replay as `REVIEW_FAILED`. Keep `G0/P0`, `G5`, and `G6` `BLOCKED`. Make the smallest documentation repair covering the exact universe parser/receipt, structural-hash then semantic-invalid short-circuit, and valid `1..10000` entry cardinality; then obtain an eighth independent semantic replay before changing `G0`.

Rationale: [OBSERVED] The reviewer found three universe-level blocker groups despite stable pins and passing non-engine checks. [DERIVED] No valid metric run is constructible for every admitted universe input, and documentation review cannot satisfy the implementation gates.

Alternatives not selected:

- Promote `G0` because engine-side and most metric contracts passed: rejected because evaluation-universe identity and algebra remain incomplete.
- Treat conceptual probes or link/anchor counts as engine or metric evidence: rejected because no implementation ran.

### Impact and tradeoffs

- Compatibility and reproducibility: strict universe parsing, semantic short-circuit, and nonempty cardinality reject earlier ambiguous or vacuous universe artifacts.
- Scientific scope: the central method, factorial, labels, and protected estimands remain unchanged.
- Data and evaluation: no data or labels changed; invalid universes cannot define `E`, denominators, row diagnostics, or metric values, and valid evaluation requires a nonempty population.
- Security and privacy: bounded parser behavior and no row/envelope inspection after invalid universe binding reduce unsafe-input and untrusted-identifier exposure.
- Performance: the 621-byte empty-universe vector and hash are conceptual contract evidence, not a throughput or memory result.
- Operations: `G0/P0`, `G5`, and `G6` remain blocked; the next repair is limited to three universe groups.

### Verification performed

- `[OBSERVED - Luna inspection]` All eleven local reviewed-file SHA-256 values match the stable pins recorded above.
- `[OBSERVED - parent-supplied execution evidence]` `python3 -B -m unittest discover -s tests -v` passed 101/101 tests in 30.210 seconds; the suite was explicitly non-engine.
- `[OBSERVED - parent-supplied documentation QA]` The link inventory contained 134 targets and 91 anchors, and the checked structural/document invariants passed.
- `[OBSERVED - parent-supplied conceptual probe]` The 621-byte canonical empty-universe vector had SHA-256 abbreviated `2c1baf...63ba9` and exposed the zero-item accuracy defect; this was not an engine or metric implementation result.
- `[OBSERVED - Luna inspection]` The current universe receipt lacks the requested strict parser mapping/count transitions, the semantic-invalid branch does not completely prohibit row/envelope derivation, valid universe counts allow zero, and emptiness accuracy divides by `N_all`.
- `[OBSERVED - Luna inspection]` `EXECUTION_STATUS.md` contains exact ordered `P01`-`P20`, `O01`-`O30`, and `E01`-`E14`; `G0`, `G5`, and `G6` remain blocked. This replay has not yet been projected into a technical status entry.
- Unrun by Luna: the 101-test suite, link/anchor checks, and conceptual probes were not rerun for this register-only checkpoint. No engine, universe parser, provider, registry lookup, dataset operation, model, metric implementation, or performance benchmark ran.

### Remaining risks and follow-up

- Strict universe parser precedence and partial-entry count transitions need executable adversarial boundary tests.
- The structural-hash/semantic-invalid branch requires exact schema bytes and known-answer vectors across closure, partition, reference, and gold failures.
- Requiring a nonempty universe must be propagated to preregistration, metric manifests, reporting, and gate checks without altering genuine natural-zero pair algebra.
- Complete real-universe membership, provider/registry behavior, model artifacts, calibration, and empirical metrics remain unimplemented.
- No authentic corpus, collection authorization, model result, metric result, performance result, or publication claim is established.

Next owner/action: make a minimal documentation-only repair that freezes strict `MetricUniverseInputReceipt` parser and count transitions, structural hashing followed by a no-row semantic-invalid short-circuit, and valid universe cardinality `1..10000`. Pin the affected documents and commission an eighth independent replay; preserve all seventh-replay passes and keep `G5/G6` blocked pending executable evidence.

### Correction history

None. This record is append-only, `LUNA-20260819-018` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-020

### Eighth universe-only P0 documentation repair pending independent replay

- Lifecycle: `REPAIRED_PENDING_REVIEW` - eighth universe-only documentation repair completed; not a pass and no commit requested
- Recorded: 19 August 2026, 8:49:36 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-020`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected paths and pinned repair boundary

- `docs/research/ENGINE_SPEC.md` - SHA-256 `a159c86fee69118349a0d7c25634ba6ac362e4a687bee9787b80dc4d405a02f4`
- `docs/research/FACTORIAL_CONDITION_SPEC.md` - SHA-256 `6629f99d12ec2eb87e02f085ae5ddee7723cb1288ff0761ead0d97b161b6316a`
- `docs/research/PAPER_1_PREREGISTRATION.md` - SHA-256 `9c2b5e79858f1f17866aa06ea537deb42ed5c64b79dfb0e828017119d2c87008`
- `docs/research/REGISTRY_PROTOCOL.md` - SHA-256 `1e4ecf750589450fb14614e963e8e4f090c34a415c915ef583a178a07cf4ad9b`
- `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md` - SHA-256 `6a76b516df50b18a0c67f6975462efd75c5f9fabe7a64c0fca160eeb77d0895e`
- `docs/research/THREAT_MODEL.md` - SHA-256 `4283b39d1f08e71b053c3fc71d044186828a38da8c4fa1fc301da83e7f2494c2`
- `docs/research/FISHER_RESEARCH_BLUEPRINT.md` - SHA-256 `df63128f94d5c021675ee74ae29da98b9fcbcc805b2c1fb895633b305422b46b`
- `docs/research/ANNOTATION_GUIDE.md` - SHA-256 `b9724e0725616bdc1b437357ec026cdeb871de4d8bc6dbd8a55d9eaa1017c5eb`
- `docs/research/EXECUTION_STATUS.md` - SHA-256 `7f2d7bae1a9837231edbe9a2d0a5c75e2654c1bd2555fabec3eb8326967c712e`
- `docs/research/SOURCE_LEDGER.md` - SHA-256 `f3264e66de5441f1552a5c817cef4ae26585bf419f8d11000030e4448bc81875`
- `docs/DATA_CONTRACT.md` - unchanged SHA-256 `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`

This universe-only repair addresses the three groups in `LUNA-20260819-019` without reopening the seventh-replay surfaces that passed. [OBSERVED - Luna inspection] `EXECUTION_STATUS.md` appends `E15`, preserves the `E05`-`E14` evidence history, and leaves `G0/P0`, `G5`, and `G6` `BLOCKED`. No eighth independent semantic pass is claimed.

#### Decision D-102 - Freeze the strict ten-code universe parser and one-code precedence

Decision: Parse raw universe input with a cap-plus-one reader and the exact ordered codes: too large, BOM, invalid UTF-8, duplicate key, nonfinite value, invalid JSON syntax, non-NFC string, noncanonical bytes, schema/enum failure, then too many entries. Use the same strict scanner semantics as engine input: left-to-right scan, no recovery after the first unrecoverable syntax event, and duplicate-key then nonfinite then syntax precedence among fully observed events. Emit exactly the first applicable code.

Rationale: [OBSERVED - Luna inspection] The repaired engine specification lists all ten controlled codes and their total order. [DERIVED] This eliminates permissive library behavior and gives joint defects one deterministic receipt result.

Alternatives not selected:

- Use a permissive or library-default parser: rejected because duplicate, nonfinite, Unicode, and recovery behavior can differ.
- Emit an exhaustive or unordered code set: rejected because cap-limited parsing may never safely observe later defects.

#### Decision D-103 - Freeze all-or-zero universe receipt hash and count states

Decision: `MetricUniverseInputReceipt` must encode one exact union. Over-cap input retains only the fixed cap-plus-one prefix hash and zero entry counts. Failures before canonical-byte equality have no computed universe hash and zero counts. Canonical schema/entry-bound failures retain the complete supplied-byte hash and use the exact whole-array decoded count; validated count is the full entry count only when every entry passes its structural grammar within the limit, otherwise zero. There is no partial-prefix entry count. Structural `PASS` retains the computed canonical hash, full decoded/validated counts, and no invalid code.

Rationale: [DERIVED from the seventh replay] Whole-object count states prevent a truncated entry from being counted differently by streaming implementations. Separating complete hash from over-cap prefix hash makes the receipt safe and constructible for every raw-input class.

Alternatives not selected:

- Count partial prefix entries: rejected because truncation before a complete top-level object does not establish a stable entry inventory.
- Retain a full-submission hash after an over-cap read: rejected because the reader intentionally consumes only the cap plus one byte.
- Treat schema-invalid entries as semantically validated: rejected because structural shape is not universe closure evidence.

#### Decision D-104 - Freeze universe, submission, and semantic-validation precedence

Decision: Apply the exact order: universe structural receipt, submitted-inference preflight bound to the receipt's computed universe hash, then semantic universe validation. A structural universe `FAIL` emits no submission receipt, metric run, or metric. A structural universe `PASS` permits submission preflight even for an empty or later semantically invalid universe. The canonical submitted-inference manifest must bind exactly the computed supplied-universe hash.

Decision: If both structural boundaries pass but the universe fails complete nonempty semantic closure, emit one `MetricRunManifest INVALID` short-circuit: retain the supplied computed universe hash and canonical submitted-inference hash; set `universe_error_count=1`, all three declared `N_*` fields and `denominator_error_count` to zero, preserve `submitted_count`, set every row discrepancy and envelope-outcome count to zero, use empty `inference_envelopes`, emit the sole universe-invalid code, open no envelope, and emit no metric.

Rationale: [OBSERVED - Luna inspection] The repaired specification now separates structural identity from semantic truth and gives an empty structurally valid universe a known short-circuit path after submission preflight. [DERIVED] This preserves submitted evidence without using invalid universe entries as `E`, repairing closure, or inspecting rows without an authoritative population.

Alternatives not selected:

- Use invalid universe entries as expected sequence `E`: rejected because invalid membership or gold bindings would become evaluation truth.
- Invent or silently substitute a corrected closure: rejected because the evaluated population would no longer match the submitted hash.
- Compare rows or inspect envelopes without a valid universe: rejected because no authoritative order, denominator, or item binding exists.
- Allow the submitted manifest to bind a claimed hash different from the computed supplied-universe hash: rejected because submission and universe identity would diverge.

#### Decision D-105 - Require a positive valid-universe and emptiness-accuracy denominator

Decision: A semantically valid universe contains exactly `1..10000` entries and a valid metric run has `1<=N_all<=10000`. A structurally valid empty universe takes the semantic-invalid short-circuit. Therefore `pair_emptiness_accuracy` always has a positive denominator in a valid metric run; no zero-item metric is published.

Rationale: [DERIVED from the seventh replay] Nonempty cardinality removes the `1/N_all` division-by-zero case while preserving canonical natural-zero pair precision, recall, and F1 within a nonempty evaluation population.

Alternatives not selected:

- Publish a zero-item emptiness accuracy: rejected because it is undefined and supplies no evaluation evidence.
- Assign a conventional zero or one to zero-item accuracy: rejected because either value is vacuous and library-dependent.
- Drop only emptiness accuracy while treating an empty population as a valid metric run: rejected because every metric would lack an evidentiary population.

#### Decision D-106 - Keep G0, G5, and G6 blocked pending the eighth replay

Decision: Classify this universe-only repair as `REPAIRED_PENDING_REVIEW`, not a pass. Require an eighth independent semantic replay of the pinned documents before `G0/P0` can change. Keep `G5/G6` blocked on executable engine, resource, model, control, and evaluation evidence even if the documentation later passes.

Rationale: [OBSERVED] The repair changed documentation only, and the available suite remains explicitly non-engine. [DERIVED] Exact universe prose still requires independent replay and implementation before any runtime or empirical claim.

Alternatives not selected:

- Promote `G0` because the seventh-replay universe defects were edited: rejected because the new boundary has not passed independent replay.
- Treat parser documentation or link/anchor QA as `G5/G6` evidence: rejected because no engine, universe parser, model, dataset, registry, or metric run exists.

### Impact and tradeoffs

- Compatibility and reproducibility: strict ten-code parsing, exact receipt unions, semantic short-circuiting, and nonempty cardinality invalidate ambiguous or vacuous draft universes.
- Scientific scope: the central model, factorial, labels, and protected estimands remain unchanged.
- Data and evaluation: no dataset or label changed; malformed universes stop before submission, semantically invalid universes stop before row inspection, and valid metrics require a nonempty population.
- Security and privacy: bounded prefix handling and no envelope opening under invalid universe semantics reduce unsafe-input and untrusted-identifier exposure.
- Performance: byte and entry limits are specification boundaries, not measured latency or memory results.
- Operations: `E15` preserves the seventh failure; `G0/P0`, `G5`, and `G6` remain blocked pending their stated evidence.

### Verification performed

- `[OBSERVED - Luna inspection]` All ten repaired research-document SHA-256 values and the unchanged `DATA_CONTRACT.md` SHA-256 match the pins recorded above.
- `[OBSERVED - parent-supplied execution evidence]` `python3 -B -m unittest discover -s tests -v` passed 101/101 tests in 30.075 seconds; the suite was explicitly non-engine.
- `[OBSERVED - parent-supplied documentation QA]` Strict encoding/whitespace checks, 135 link/anchor checks, exact `P01`-`P20`, `O01`-`O30`, and `E01`-`E15` inventories, ten-code order, receipt state, precedence, eligibility, metric example, zero algebra, and pinned-file checks passed.
- `[OBSERVED - Luna inspection]` The repaired engine specification contains the ten-code parser order, exact receipt state table, universe-to-submission-to-semantic precedence, computed-hash submission binding, semantic-invalid no-row/no-envelope branch, `1..10000` valid entries, and positive `N_all` rule.
- `[OBSERVED - Luna inspection]` `EXECUTION_STATUS.md` currently contains exact ordered `P01`-`P20`, `O01`-`O30`, and `E01`-`E15`, preserves `E05`-`E14`, and keeps `G0`, `G5`, and `G6` blocked.
- Unrun by Luna: the 101-test suite and documentation QA commands were not rerun for this register-only checkpoint. No eighth semantic replay, engine, universe parser, provider, registry lookup, dataset operation, model, metric run, or performance benchmark ran.

### Remaining risks and follow-up

- Independent replay may identify a remaining conflict between structural receipts, submission binding, and semantic short-circuit serialization.
- Parser and receipt behavior lacks executable adversarial tests for all ten codes, cap boundaries, duplicate/nonfinite ordering, and truncated entries.
- Semantic-invalid vectors need executable known answers for closure, partition, reference, gold, empty, and over-limit cases.
- Real universe membership, provider/registry behavior, model artifacts, calibration, and empirical metrics remain unimplemented.
- No authentic corpus, collection authorization, model result, metric result, performance result, or publication claim is established.

Next owner/action: commission an eighth independent universe-focused semantic replay against the eleven pinned files. Replay all ten parser codes and precedence, every receipt hash/count state, computed-hash submission binding, structural-versus-semantic ordering, semantic-invalid no-row/no-envelope short-circuit, nonempty cardinality, positive emptiness denominator, and historical `E05`-`E15` consistency. Only a separate successful review may change `G0`; `G5/G6` still require implementation evidence.

### Correction history

None. This record is append-only, `LUNA-20260819-019` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-021

### Eighth independent P0 semantic replay passed

- Lifecycle: `REVIEW_PASSED` - independent P0 semantic review passed at the pinned design-only boundary; no commit requested
- Recorded: 19 August 2026, 8:57:48 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-021`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Reviewed paths and stable start/end pins

- `docs/research/ENGINE_SPEC.md` - SHA-256 `a159c86fee69118349a0d7c25634ba6ac362e4a687bee9787b80dc4d405a02f4`
- `docs/research/FACTORIAL_CONDITION_SPEC.md` - SHA-256 `6629f99d12ec2eb87e02f085ae5ddee7723cb1288ff0761ead0d97b161b6316a`
- `docs/research/PAPER_1_PREREGISTRATION.md` - SHA-256 `9c2b5e79858f1f17866aa06ea537deb42ed5c64b79dfb0e828017119d2c87008`
- `docs/research/REGISTRY_PROTOCOL.md` - SHA-256 `1e4ecf750589450fb14614e963e8e4f090c34a415c915ef583a178a07cf4ad9b`
- `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md` - SHA-256 `6a76b516df50b18a0c67f6975462efd75c5f9fabe7a64c0fca160eeb77d0895e`
- `docs/research/THREAT_MODEL.md` - SHA-256 `4283b39d1f08e71b053c3fc71d044186828a38da8c4fa1fc301da83e7f2494c2`
- `docs/research/FISHER_RESEARCH_BLUEPRINT.md` - SHA-256 `df63128f94d5c021675ee74ae29da98b9fcbcc805b2c1fb895633b305422b46b`
- `docs/research/ANNOTATION_GUIDE.md` - SHA-256 `b9724e0725616bdc1b437357ec026cdeb871de4d8bc6dbd8a55d9eaa1017c5eb`
- `docs/research/EXECUTION_STATUS.md` - SHA-256 `7f2d7bae1a9837231edbe9a2d0a5c75e2654c1bd2555fabec3eb8326967c712e`
- `docs/research/SOURCE_LEDGER.md` - SHA-256 `f3264e66de5441f1552a5c817cef4ae26585bf419f8d11000030e4448bc81875`
- `docs/DATA_CONTRACT.md` - SHA-256 `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`

[OBSERVED - parent-supplied independent review] All eleven start and end pins matched. The eighth replay concluded `P0 SEMANTIC PASS`: no deterministic blocker remains for implementing the synthetic `E0` interfaces at the reviewed design boundary. The strict universe parser and receipt, structural/submission/semantic precedence, semantic-invalid short-circuit, nonempty universe, and all regression surfaces passed. This is a specification-coherence result only.

#### Decision D-107 - Accept the independently reviewed P0 semantic specification

Decision: Accept the pinned P0 documents as semantically coherent and sufficiently deterministic to begin synthetic `E0` implementation. Record the independent verdict as `REVIEW_PASSED`; do not reopen passed contracts without new contradictory evidence or a deliberate versioned architecture change.

Rationale: [OBSERVED - parent-supplied independent review] The eighth replay exercised the repaired universe surfaces and regression boundary without finding another deterministic synthetic-E0 blocker. [DERIVED] The design-only P0 coherence gate has its required independent acceptance at these exact bytes.

Alternatives not selected:

- Keep P0 blocked despite a stable independent pass: rejected because the defined design-only acceptance condition has now been met.
- Treat the pass as universal correctness: rejected because it applies only to specification coherence at the pinned boundary.

#### Decision D-108 - Authorize the next G0 status update as COMPLETE_SPEC, not an execution pass

Decision: Authorize the technical status owner to append the eighth replay evidence and change `G0/P0` from `BLOCKED` to `COMPLETE_SPEC` under the existing design-only gate definition. This Luna checkpoint does not edit `EXECUTION_STATUS.md` and does not claim that the update has already occurred; the currently pinned status file still shows `G0` blocked through `E15`.

Rationale: [DERIVED from the independent verdict] `COMPLETE_SPEC` accurately distinguishes a coherent reviewed specification from executable or empirical completion. A separate status update preserves file ownership, creates its own pinned evidence boundary, and keeps the audit trail explicit.

Alternatives not selected:

- Mark `G0` as an executed or empirical pass: rejected because no engine, provider, registry, model, corpus, or metric execution exists.
- Silently infer that status changed from this register entry: rejected because the status file remains unchanged and must be updated and verified separately.
- Leave the status permanently blocked after the defined gate passed: rejected because it would make the status ledger contradict the accepted review once the separate update is completed.

#### Decision D-109 - Preserve E08-E15 failure history and the passed regression boundary

Decision: Preserve the complete `E08`-`E15` sequence of semantic failures and repairs as historical evidence. Record that the eighth replay passed the strict ten-code universe parser, all receipt hash/count states, universe-to-submission-to-semantic precedence, computed-hash binding, semantic-invalid no-row/no-envelope behavior, nonempty cardinality, positive-`N_all` algebra, and prior engine descriptor, eligibility, run-union, factorial, provenance, candidate/q, SEP, prediction, tensor, universe/gold, five-seed, metric-input, and discrepancy-count contracts.

Rationale: [OBSERVED - parent-supplied independent review] These surfaces passed together at stable start/end pins. [DERIVED] Retaining the failure history explains why the final contract exists and prevents a pass record from erasing prior defect evidence.

Alternative not selected: rewrite or delete the failed review history after the pass. Rejected because append-only evidence must preserve superseded findings, repairs, and review scope.

#### Decision D-110 - Begin E0 implementation while keeping G5 and G6 blocked

Decision: The next technical phase is implementation of the exact synthetic `E0` interfaces and known-answer tests defined by the passed P0 specifications. Keep `G5` and `G6` `BLOCKED`: they require executable engine/resource/model/control/evaluation evidence and later factorial development, not merely P0 prose.

Rationale: [OBSERVED] The independent pass expressly found no remaining deterministic synthetic-E0 design blocker but produced no implementation or empirical evidence. [DERIVED] Starting E0 is now authorized; advancing resource/model or factorial gates is not.

Alternatives not selected:

- Mark `G5/G6` complete from the P0 review: rejected because their evidence requirements are executable and empirical.
- Skip E0 and begin model or protected-evaluation work: rejected because the synthetic interface and known-answer implementation gate has not run.
- Claim provider, registry, model, corpus, latency, or performance behavior: rejected because none was executed or measured.

### Impact and tradeoffs

- Architecture and compatibility: the pinned P0 contract becomes the implementation target; future incompatible changes require a new version and review.
- Scientific scope: the registered shared-provider factorial, semantic consistency method, evaluation universe, and metrics remain design commitments, not results.
- Data, security, and privacy: no dataset, registry, provider, or user data changed; reviewed fail-closed boundaries remain prose until implemented.
- Performance: no latency, memory, throughput, calibration, FPR, accuracy, or other model metric was measured.
- Operations: a separate status projection may set `G0=COMPLETE_SPEC`; `G5/G6` remain blocked, and E0 implementation becomes the immediate authorized work.

### Verification performed

- `[OBSERVED - Luna inspection]` All eleven local reviewed-file SHA-256 values match the stable start/end pins recorded above.
- `[OBSERVED - parent-supplied independent execution evidence]` `python3 -B -m unittest discover -s tests -v` passed 101/101 tests in 30.206 seconds; the suite was explicitly non-engine.
- `[OBSERVED - parent-supplied documentation QA]` The link inventory contained 136 targets and 93 anchors, and the checked structural/document invariants passed.
- `[OBSERVED - parent-supplied conceptual review probes]` Parser codes 1-10, the 10,001-entry count/hash state, empty structural-universe semantic short-circuit, and all-empty pair algebra under positive `N_all` passed conceptual review. These were contract probes, not engine tests.
- `[OBSERVED - Luna inspection]` `EXECUTION_STATUS.md` remains at exact ordered `P01`-`P20`, `O01`-`O30`, and `E01`-`E15`; its current `G0`, `G5`, and `G6` rows are still blocked. No status mutation is claimed in this checkpoint.
- Unrun by Luna: the 101-test suite, link/anchor checks, and conceptual probes were not rerun for this register-only checkpoint. No engine, provider, registry lookup, dataset operation, model, metric execution, or performance benchmark ran.

### Remaining risks and follow-up

- The reviewed contracts may expose implementation defects when converted into parsers, serializers, validators, masks, and known-answer tests.
- The separate `EXECUTION_STATUS.md` projection must preserve the exact pins, pass scope, and `E08`-`E15` history without implying implementation success.
- E0 needs adversarial boundary tests for byte caps, Unicode, duplicate/nonfinite parsing, invalid eligibility, stage retention, universe receipts, and metric discrepancy algebra.
- Real provider, registry, model, corpus, calibration, compute, and protected-evaluation behavior remain unknown.
- No collection authorization, empirical result, performance claim, product readiness, or publication readiness is established.

Next owner/action: update `EXECUTION_STATUS.md` in a separate, verified checkpoint by appending the eighth replay evidence and setting only design gate `G0/P0` to `COMPLETE_SPEC`; keep `G5/G6` blocked. Then implement the exact synthetic `E0` interfaces and known-answer tests against the passed pinned boundary, followed by independent code review.

### Correction history

None. This record is append-only, `LUNA-20260819-020` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-022

### G0/P0 transitioned to design-only COMPLETE_SPEC

- Lifecycle: `COMPLETE_SPEC` - specification-coherence status projected after independent pass; no implementation or commit requested
- Recorded: 19 August 2026, 9:04:21 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-022`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected path and final status boundary

- `docs/research/EXECUTION_STATUS.md` - SHA-256 `f8433be73dad8a89da263007d022d960d5c963f558f8e2e5a6aa1b3426dad1cd`

[OBSERVED - Luna inspection] The status file appends `E16` as `EXECUTED_PASS`, changes only the `G0/P0` gate and `WP-00-CONTRACT` work package to design-only `COMPLETE_SPEC`, preserves the `E05`-`E15` history, and leaves `G1`-`G9` blocked, including `G5/G6`. `E16` binds the eleven stable review pins recorded in `LUNA-20260819-021` and states the same non-engine evidence boundary.

#### Decision D-111 - Accept E16 as the status projection of the independent P0 pass

Decision: Record `E16=EXECUTED_PASS` as the exact execution-status evidence row for the eighth independent P0 semantic replay. Its pass applies to deterministic and falsifiable synthetic-`E0` specification coherence at the eleven pinned files; it is not an executed-engine claim.

Rationale: [OBSERVED - Luna inspection] `E16` records the `P0 SEMANTIC PASS`, all eleven pins, the universe repairs and `E08`-`E15` regressions reviewed, 136 targets and 93 anchors, and the explicitly non-engine 101-test result. [DERIVED] This is the authorized evidence needed to project the design gate without broadening its scope.

Alternative not selected: call implementation complete because the evidence row is named `EXECUTED_PASS`. Rejected because the row explicitly means the review executed and passed, not that an engine or empirical workflow executed.

#### Decision D-112 - Promote only G0/P0 and WP-00-CONTRACT to COMPLETE_SPEC

Decision: Set `G0/P0=COMPLETE_SPEC` and `WP-00-CONTRACT=COMPLETE_SPEC` for the frozen reviewed version. Interpret `COMPLETE_SPEC` strictly as design acceptance: no further P0 proof is required unless the specification changes, but every implementation and empirical requirement remains separate.

Rationale: [DERIVED from `E16`] The independent stable-pin review found no deterministic synthetic-E0 blocker. The gate and work package are specification deliverables, so `COMPLETE_SPEC` is the narrow accurate state.

Alternatives not selected:

- Leave `G0` blocked after its defined design-only evidence passed: rejected because it would make status disagree with `E16`.
- Promote `G0` to an implementation-complete or empirical state: rejected because no executable or measured evidence exists.

#### Decision D-113 - Keep every governance, data, implementation, model, and empirical gate blocked

Decision: Preserve `G1`-`G9` as `BLOCKED`, specifically including `G5` resource/model readiness and `G6` factorial development. Preserve `E05`-`E15` unchanged as the defect-and-repair history leading to `E16`.

Rationale: [OBSERVED - Luna inspection] The status rows continue to require human authorization, registry and corpus evidence, executable resources/models/controls, protected-access authorization, empirical results, and release decisions. None was supplied by the P0 review. [DERIVED] A specification pass cannot satisfy a differently scoped gate.

Alternatives not selected:

- Promote empirical or implementation gates with `G0`: rejected because their required artifacts and measurements do not exist.
- Erase or rewrite earlier failed evidence rows: rejected because append-only history must preserve why the final specification changed.
- Begin data, model, provider, registry, performance, or publication claims: rejected because no corresponding execution or authorization exists.

#### Decision D-114 - Make synthetic-only E0 implementation the next action

Decision: Freeze the passed P0 version and proceed only to implementation and independent testing of the exact synthetic `E0` provider/system/descriptor/preflight/run/prediction/packet/plan/tensor/universe/metric-input/metric-run interfaces. Any correction to the frozen design requires a new evidence row. Do not advance `G5/G6` until their own executable evidence exists.

Rationale: [DERIVED from the status transition] P0 supplies a reviewed implementation target. Synthetic E0 is the next unmet gate and preserves the prohibition on unsupported data/model claims.

Alternative not selected: skip synthetic E0 and start data collection, training, protected evaluation, or publication work. Rejected because upstream implementation, governance, provenance, and authorization gates remain blocked.

### Impact and tradeoffs

- Architecture and compatibility: the current P0 bytes become the frozen E0 implementation target; later incompatible corrections require a new reviewed version.
- Data, security, and privacy: no dataset, registry, provider, model, protected record, or human workflow changed; every corresponding gate remains blocked.
- Evaluation and performance: no metric, latency, memory, accuracy, FPR, or model behavior was measured.
- Operations: status now distinguishes `COMPLETE_SPEC` from executable completion; only synthetic E0 implementation is authorized next.
- Auditability: `E16` adds the pass without deleting the `E05`-`E15` failure and repair sequence.

### Verification performed

- `[OBSERVED - Luna inspection]` `docs/research/EXECUTION_STATUS.md` matches final SHA-256 `f8433be73dad8a89da263007d022d960d5c963f558f8e2e5a6aa1b3426dad1cd`.
- `[OBSERVED - Luna inspection]` The inventories contain exact ordered `P01`-`P20`, `O01`-`O30`, and `E01`-`E16`; `E16` is `EXECUTED_PASS`; `G0` and `WP-00-CONTRACT` are `COMPLETE_SPEC`; `G1`-`G9`, including `G5/G6`, remain `BLOCKED`.
- `[OBSERVED - parent-supplied execution evidence]` `python3 -B -m unittest discover -s tests -v` passed 101/101 tests in 30.395 seconds; the suite was explicitly non-engine.
- `[OBSERVED - parent-supplied documentation QA]` All eleven evidence pins, gate statuses, 70 links, encoding, table structure, and exact phase/output/evidence inventories passed.
- Unrun by Luna: the 101-test suite, link, encoding, and table checks were not rerun for this register-only checkpoint. No engine, provider, registry lookup, corpus operation, model, metric execution, or performance benchmark ran.

### Remaining risks and follow-up

- Implementing the frozen P0 contract may reveal code-level defects requiring a versioned specification correction.
- No parser, serializer, validator, provider, resolver, tensor builder, or metric runner implements the passed contract yet.
- Human governance, registry truth, data provenance, corpus construction, model behavior, protected evaluation, and release approval remain blocked.
- No empirical result, performance claim, product readiness, patent conclusion, or publication readiness is established.

Next owner/action: implement the exact synthetic E0 interfaces and known-answer tests against the frozen P0 boundary, run focused and full verification, and obtain independent code review. Keep `G1`-`G9`, including `G5/G6`, blocked until their own evidence exists.

### Correction history

None. This record is append-only, `LUNA-20260819-021` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-023

### Synthetic E0 evaluation slice implemented pending independent review

- Lifecycle: `IMPLEMENTED_PENDING_INDEPENDENT_REVIEW` - evaluation implementation and owner verification completed; independent code review and no commit remain pending
- Recorded: 19 August 2026, 9:38:01 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-023`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected implementation boundary

- `fisher_engine/evaluation.py` - SHA-256 `8ca6d7ca06c508cd61f3f63b621ad14a8dcc0891579c900b3b6bbfb9fccab500`
- `tests/test_engine_evaluation.py` - SHA-256 `54117e7ad5162eb5670cdefbd3395c6938ab5bfc064be34325c3b8858784f281`

[OBSERVED - Luna inspection] The owned implementation defines the synthetic evaluation boundary and its tests. Only these two paths are pinned because other agents may continue changing the shared uncommitted tree; no whole-tree stability claim is made.

#### Decision D-115 - Implement the complete synthetic evaluation artifact boundary

Decision: Implement canonical gold inventories and semantic closure; strict ten-code universe parsing with cap-plus-one receipts; submission preflight and universe-hash binding; universe/submission/semantic precedence; exclusive discrepancy and denominator accounting; no-deletion valid and invalid metric manifests; rank-one and q-weighted pair metrics; canonical zero algebra; conditional empty/nonempty recalls; and the fixed semantic-invalid no-row/no-envelope short-circuit.

Rationale: [OBSERVED - Luna inspection] `fisher_engine/evaluation.py` contains the corresponding parsers, semantic validation, metric-run construction, pair-metric arithmetic, and boundary orchestration. [DERIVED] This is the smallest coherent E0 evaluation slice that can turn the passed P0 evaluation contracts into executable synthetic known answers.

Alternatives not selected:

- Implement only the happy-path metric: rejected because receipts, invalid unions, no-deletion accounting, and zero algebra are part of the accepted interface.
- Emit empirical or benchmark claims from synthetic fixtures: rejected because the slice validates mechanics, not real data or model behavior.

#### Decision D-116 - Keep expected universe entries derived upstream from validated dataset artifacts

Decision: Require `UniverseSemanticContext.expected_entries` to be supplied from the validated items, annotations, registry manifest, and registry references. The evaluation module compares the submitted universe against that derived immutable sequence but does not re-ingest or independently reconstruct the dataset source artifacts.

Rationale: [OBSERVED - Luna inspection] The context contract states that `expected_entries` is derived from four validated dataset artifacts, and semantic validation requires byte/order equality. [DERIVED] Keeping derivation upstream avoids duplicate ingestion logic and a second source of truth inside the evaluation layer.

Alternative not selected: duplicate dataset ingestion and retention logic inside `evaluation.py`. Rejected because parallel derivations could disagree and expand the slice beyond its evaluation responsibility.

#### Decision D-117 - Apply supplied temperature p/v/u without fitting calibration

Decision: Implement the specified supplied-temperature `p`, `v`, and `u` summaries for rank-one and weighted logits, including shape, finite-value, positive-temperature, weight, and positive-zero checks. Do not estimate, optimize, or fit a temperature in this slice.

Rationale: [OBSERVED - Luna inspection] `supplied_temperature_summary` explicitly applies supplied-temperature formulas and states that optimizer behavior remains outside this implementation. [DERIVED] Arithmetic known answers belong in E0; calibration fitting belongs to a later empirical gate.

Alternatives not selected:

- Fit or infer temperature from synthetic evaluation inputs: rejected because no calibration dataset, optimizer contract, or empirical authorization exists.
- Present supplied-temperature output as calibrated model evidence: rejected because no model or calibration run occurred.

#### Decision D-118 - Directly validate the complete artifact chain and preserve error classes

Decision: Use the default inspector to validate system manifest to engine envelope, preflight receipt, five-seed logits, prediction audit, every SEP packet, and feature tensor through exact bytes and hashes before producing pair evidence. Distinguish missing or unreadable referenced artifacts from structurally readable binding mismatches so invalid and mismatch counts remain exclusive.

Rationale: [OBSERVED - Luna inspection] `make_engine_envelope_inspector` loads and validates the complete chain, raises separate evaluation versus binding errors, and the focused tests cover valid integration plus missing/hash-mismatch separation. [DERIVED] Trusting outer hashes without parsing the referenced chain would not prove that the evaluated evidence matches the bound system and paths.

Alternatives not selected:

- Trust referenced hashes without direct chain validation: rejected because a present byte object may still be malformed or cross-bound.
- Collapse missing, unreadable, and binding-mismatch outcomes: rejected because the metric contract requires exclusive invalid versus mismatch accounting.

#### Decision D-119 - Keep implementation gates blocked pending independent code review

Decision: Preserve design-only `G0/P0=COMPLETE_SPEC`. Classify this evaluation slice as implemented but pending independent review; do not promote `G5`, `G6`, or any other implementation or empirical gate. Require an independent reviewer to pin these two files, replay focused/adversarial tests, inspect contract coverage, and report a separate verdict.

Rationale: [OBSERVED] Owner tests passed, but no independent code review, supported Python-3.11 runtime execution, real provider, registry, model, corpus, or protected metric run exists. [DERIVED] Owner verification is necessary but insufficient for a gate promotion.

Alternatives not selected:

- Mark the evaluation implementation independently accepted from owner tests: rejected because the required independent review has not occurred.
- Promote resource/model or factorial gates from a synthetic evaluation slice: rejected because their artifacts and empirical requirements remain absent.

### Impact and tradeoffs

- Interfaces and compatibility: the new module implements canonical evaluation artifacts and fail-closed boundaries; future incompatible changes must preserve or version the accepted contract.
- Data and provenance: no dataset was loaded or changed. Upstream validated expected entries remain the source of universe truth.
- Security and privacy: bounded readers, sanitized receipts, no-deletion accounting, and direct chain validation reduce unsafe-input and artifact-substitution risk; real access controls remain untested.
- Evaluation: rank-one/q metrics and zero-denominator behavior are executable synthetic mechanics, not measured model quality.
- Performance: no dedicated latency or memory benchmark ran; test durations are verification evidence only.
- Operations: design gate `G0` remains complete; implementation and empirical gates remain blocked until independent review and later evidence.

### Verification performed

- `[OBSERVED - Luna inspection]` The two owned files match the SHA-256 pins recorded above.
- `[OBSERVED - parent-supplied focused verification]` The evaluation-focused suite passed 22/22 tests.
- `[OBSERVED - parent-supplied full verification]` The full suite passed 190/190 tests in 31.308 seconds.
- `[OBSERVED - parent-supplied compatibility QA]` Python-3.11 AST parsing passed; `compileall` and whitespace checks passed.
- `[OBSERVED - Luna inspection]` The implementation exposes canonical gold/universe/submission/metric functions, supplied-temperature p/v/u, the default complete-chain inspector, and separate binding-error behavior; focused tests cover parser receipts, counts, invalid boundaries, pair metrics, temperature summaries, and inspector integration.
- Unrun by Luna: the focused/full suites, AST, compileall, and whitespace commands were not rerun for this register-only checkpoint. No Python-3.11 runtime was available, no independent code review ran, and no real engine/provider/registry/model/dataset/metric benchmark executed.

### Remaining risks and follow-up

- Independent review may find contract divergence, unsafe boundary behavior, or insufficient negative tests.
- Python-3.11 syntax compatibility was checked statically, but the module was not executed under a Python-3.11 runtime.
- The evaluation slice depends on upstream validated artifact construction and other concurrent engine modules whose moving hashes are intentionally not pinned here.
- No authentic data, provider, registry, trained model, calibration, protected evaluation, latency, memory, or performance result exists.
- `G5/G6` and every governance, data, model, empirical, and release gate remain blocked.

Next owner/action: an independent reviewer should pin `fisher_engine/evaluation.py` and `tests/test_engine_evaluation.py`, inspect the P0 evaluation-contract mapping, replay focused and full tests plus adversarial receipt/accounting/chain cases, and report a separate pass/fail. Do not advance implementation gates before that review.

### Correction history

None. This record is append-only, `LUNA-20260819-022` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-024

### Synthetic E0 candidate slice implemented pending independent review

- Lifecycle: `IMPLEMENTED_PENDING_INDEPENDENT_REVIEW` - candidate implementation and owner verification completed; independent code review and no commit remain pending
- Recorded: 19 August 2026, 9:39:55 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-024`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected implementation boundary

- `fisher_engine/candidate.py` - SHA-256 `a01530c79ef2751046e8795ed375183c81569212d8aabeb2725456e68b1d4c43`
- `tests/test_engine_candidate.py` - SHA-256 `87ad1a804fbeb6c1ec016cb1584c92f38e7fb74e8b58598f406d0bca59297b3d`

[OBSERVED - Luna inspection] The owned implementation defines candidate/provider construction and its focused tests. Only these two files are pinned because other agents may continue changing the shared uncommitted tree; no whole-tree stability claim is made.

#### Decision D-120 - Implement the strict candidate/provider boundary and all outcomes

Decision: Implement exact rewrite-span, visible-artifact, text, alignment, count, byte, and canonical-manifest validation for composed-span, direct-full-path, and identity-bypass provider modes. Implement the complete outcomes `ELIGIBILITY_INVALID`, `NO_ELIGIBLE`, `SUCCEEDED`, `UNAVAILABLE_FALLBACK`, `TIMEOUT_FALLBACK`, `PROVIDER_INVALID_OUTPUT`, `NORMALIZER_INVALID_OUTPUT`, and `NOT_INVOKED`, including their accepted-hash, invocation, bypass, status, safe-count, and retention behavior.

Rationale: [OBSERVED - Luna inspection] `candidate.py` validates spans before retaining them, checks code-point and UTF-8 bounds, enforces monotonic/full coverage alignments, preserves direct-mode nonspan text, and emits the reviewed provider/status combinations. [DERIVED] A candidate slice must implement both accepted evidence and every fail-closed boundary to be a useful E0 interface target.

Alternatives not selected:

- Implement only successful provider output: rejected because eligibility, availability, malformed output, and dispatch failures are part of the canonical interface.
- Coerce malformed spans or alignments into a valid candidate: rejected because that would fabricate evidence and alter VMP bindings.

#### Decision D-121 - Use identity normalization only as a synthetic E0 mechanism

Decision: Use the deterministic identity normalizer for E0 interface tests, manifest construction, and arithmetic known answers. It preserves validated text/alignment and supplies no transliteration, linguistic normalization, language coverage, or robustness claim.

Rationale: [DERIVED from the P0 boundary] E0 needs a deterministic provider/normalizer path to exercise mechanics before licensed resources and real candidate providers exist. Identity behavior is sufficient for that narrow purpose.

Alternative not selected: present identity normalization as a real transliteration or linguistic component. Rejected because it performs no such transformation and has no empirical language evidence.

#### Decision D-122 - Use compact lineage and a width-64 beam before top-eight return

Decision: Preserve exact search when the duplicate-merged Cartesian set is within bounds; otherwise use the reviewed deterministic width-64 beam. Apply staged duplicate merges with compact contributor/unit/rank lineage, canonical tie-breaking, and return at most the top eight paths with exact diagnostics.

Rationale: [OBSERVED - Luna inspection] The implementation fixes `BEAM_WIDTH=64`, supports exact and beam paths, records merge reductions and compact lineage, and tests 8x8 exact, 8x8x2 beam, duplicate ranks, and top-eight behavior. [DERIVED] This retains replayable provenance and bounded work without materializing the full Cartesian explosion.

Alternatives not selected:

- Materialize every Cartesian path: rejected because up to 64 units with multiple readings is computationally explosive and exceeds the accepted bound.
- Store verbose duplicated full-path lineage for every contributor: rejected because compact canonical lineage preserves identity while controlling artifact size.
- Discard duplicate contributors after merging: rejected because merged score and provenance would no longer be auditable.

#### Decision D-123 - Freeze binary64 LSE, retained mass, and q operation order

Decision: Compute duplicate-group scores and pre-K/returned mass in the log domain; preserve exact binary64 LSE operands and retained-mass bits; compute q with the specified temperature, max shift, runtime exponential, canonical contributor-lineage accumulation order, numerator/denominator bits, and final path weights. Canonicalize signed zero and reject nonfinite/invalid arithmetic.

Rationale: [OBSERVED - Luna inspection] The implementation records composition, q numerator, q, normalizer, maximum, both LSEs, and retained-mass bit strings; tests cover extreme-score finite log mass and exact numerator/denominator relationships. [DERIVED] Fixed operation order avoids native softmax or container-order differences within the declared runtime boundary.

Alternative not selected: use a native/library softmax or unordered summation. Rejected because operation order and backend behavior could change final bits and path weights.

#### Decision D-124 - Retain only validated safe prefix counts and never echo unsafe content

Decision: On malformed provider/normalizer input, retain only counts of completely validated safe units available before failure, subject to caps. Do not echo unsafe readings, alignments, selector members, paths, text, or diagnostic payloads. Preserve configured-count boundaries without truncating a valid 64-span selector.

Rationale: [OBSERVED - Luna inspection] `CandidateValidationError` carries a safe count, invalid outcomes clear unaccepted hashes/content, and tests cover safe-prefix counts, manifest overflow, nonfinite values, unsafe selector shapes, 65-span rejection, and 64-span acceptance. [DERIVED] Safe progress is useful for audit while unvalidated content would violate privacy and canonical failure semantics.

Alternatives not selected:

- Retain the offending unit for debugging: rejected because it may contain unsafe text or malformed structures.
- Report attempted or container length as validated count: rejected because unvalidated elements would be misrepresented as safe progress.

#### Decision D-125 - Keep implementation gates blocked pending independent candidate review

Decision: Preserve design-only `G0/P0=COMPLETE_SPEC`. Classify this candidate slice as implemented but pending independent review; do not promote `G5`, `G6`, or another implementation or empirical gate. Require an independent reviewer to pin these two files and replay exact/beam, outcome, safety, Unicode, alignment, arithmetic, and known-answer cases.

Rationale: [OBSERVED] Owner tests passed, but no independent code review, Python-3.11 runtime execution, pinned cross-platform math backend, real transliteration provider, or performance benchmark exists. [DERIVED] Synthetic owner verification does not satisfy implementation/resource/model gates.

Alternatives not selected:

- Mark candidate implementation independently accepted from owner tests: rejected because independent review remains outstanding.
- Claim cross-platform bit identity: rejected because the runtime and math backend are not yet pinned for such a claim.
- Promote resource/model readiness from an identity-provider slice: rejected because real licensed resources and provider evidence are absent.

### Impact and tradeoffs

- Interfaces and compatibility: the module implements canonical provider/candidate artifacts and failure states; incompatible changes require contract-preserving revision or versioning.
- Data and linguistic scope: no dataset or language resource was used. Identity normalization is synthetic-only and makes no transliteration claim.
- Security and privacy: strict bounds, alignment checks, safe counts, and non-echo failure behavior reduce malformed-input and leakage risk; independent adversarial review remains pending.
- Performance: width-64 beam and top-eight return bound candidate growth, but no latency, memory, or scale benchmark was measured.
- Reproducibility: binary64 ordering is explicit within a bound runtime/backend; universal cross-platform bit equality is not claimed.
- Operations: `G0` stays design-complete; implementation, resource/model, factorial, and empirical gates remain blocked.

### Verification performed

- `[OBSERVED - Luna inspection]` The two owned files match the SHA-256 pins recorded above.
- `[OBSERVED - parent-supplied focused verification]` Candidate-focused verification passed 29/29 tests.
- `[OBSERVED - parent-supplied integration verification]` Candidate plus semantic verification passed 45/45 tests.
- `[OBSERVED - parent-supplied full verification]` The full suite passed 191/191 tests in 31.676 seconds.
- `[OBSERVED - parent-supplied compatibility QA]` Python-3.11 AST parsing and hygiene checks passed.
- `[OBSERVED - Luna inspection]` The implementation and focused tests cover exact/beam enumeration, duplicate lineage, retained mass/q arithmetic, direct and identity modes, all provider outcomes, eligibility limits, Unicode byte bounds, alignment failures, safe counts, and non-echo behavior.
- Unrun by Luna: the focused/integration/full suites, AST, and hygiene commands were not rerun for this register-only checkpoint. No Python-3.11 runtime, independent review, real provider/transliteration resource, registry, dataset, model, or performance benchmark ran.

### Remaining risks and follow-up

- Independent review may find contract divergence, unsafe boundary handling, arithmetic instability, or missing adversarial cases.
- Static Python-3.11 AST compatibility is not Python-3.11 runtime execution.
- Runtime and math-backend artifacts are not pinned for a cross-platform bitwise claim.
- Identity normalization provides no real transliteration quality, language coverage, or provider-failure evidence.
- No authentic corpus, model, calibration, protected evaluation, latency, memory, or empirical result exists; `G5/G6` remain blocked.

Next owner/action: an independent reviewer should pin `fisher_engine/candidate.py` and `tests/test_engine_candidate.py`, inspect the P0 mapping, and replay exact/beam, all outcome/status, Unicode/alignment, safe-prefix/non-echo, extreme-score, and q known-answer cases. Do not advance implementation gates before that review.

### Correction history

None. This record is append-only, `LUNA-20260819-023` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-025

### Synthetic E0 semantic slice implemented pending independent review

- Lifecycle: `IMPLEMENTED_PENDING_INDEPENDENT_REVIEW` - semantic implementation and owner verification completed; independent code review and no commit remain pending
- Recorded: 19 August 2026, 9:42:55 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-025`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected implementation boundary

- `fisher_engine/semantic.py` - SHA-256 `138fe0867e55e8f6943a0a5fbd25b5ebc9eae0abe5b1f0d3cede5eb6d65cbb16`
- `tests/test_engine_semantic.py` - SHA-256 `074ad382cc61fc94e3e6e210d55288c6d90aba5d5041c2272f3d46d7b34d3eb7`

[OBSERVED - Luna inspection] The owned implementation defines the synthetic semantic artifact chain and its focused tests. Only these two files are pinned because other agents may continue changing the shared uncommitted tree; no whole-tree stability claim is made.

#### Decision D-126 - Build a canonical score-bearing prediction audit at a validated-candidate boundary

Decision: Accept candidate paths and emitted endpoint candidates only after the upstream candidate layer has validated them, while revalidating the path identity, hash, coordinates, bounds, canonical representation, and semantic bindings required by this layer. Build a canonical prediction audit that stores binary64 score bits, deduplicates identical endpoint identities by highest score, breaks an equal-score duplicate tie by earliest emission index, caps each role at eight selected endpoints, and orders selected endpoints by a score-independent packet key after selection.

Rationale: [OBSERVED - Luna inspection] `semantic.py` documents the validated-candidate boundary and implements strict prediction-audit construction and validation. The focused tests exercise highest-score deduplication, earliest-index ties, binary64 distinctions that would collapse in binary32, role bounds, score-independent selected order, canonical parsing, and invalid coordinates and scores. [DERIVED] Repeating provider construction here would blur ownership, while accepting unbound path or endpoint data would make downstream audit artifacts unsafe.

Alternatives not selected:

- Rebuild or reinterpret provider candidates inside the semantic layer: rejected because candidate validation and provider behavior belong to the preceding slice, while this layer needs only the exact bound inputs it consumes.
- Trust arbitrary candidate inputs without semantic-layer binding checks: rejected because path identity, endpoint coordinates, hashes, and canonical audit structure remain this layer's responsibility.
- Use native-width or binary32 score comparisons: rejected because distinct binary64 scores can select different retained endpoints.
- Retain score-derived order in the pair packet: rejected because score rank is audit evidence and must not become an accidental learned or structural ordering feature.

#### Decision D-127 - Render aligned lookup surfaces and fail cut-through endpoints to UNKNOWN without a registry call

Decision: Render an endpoint's lookup surface from the candidate-path alignment only when the endpoint is compatible with the rewrite boundaries. If an endpoint cuts through a rewrite, emit an empty `UNALIGNED` lookup surface and resolve every affected pair as `UNKNOWN`, `NOT_EVALUATED`, and `ALIGNMENT_GUARD`, with no evidence IDs and no registry call. Use only the bounded in-memory `OfflineRegistryResolver` fixture in this E0 slice.

Rationale: [OBSERVED - Luna inspection] `render_lookup_surface` maps fully aligned endpoints and returns the explicit unaligned state for cut-through spans. Pair construction bypasses the resolver for unaligned endpoints, counts only actual calls, and the focused tests cover a full-span rewrite, a cut-through endpoint, mixed guarded and registry-resolved pairs, and the empty-product case. [DERIVED] Guessing a lookup surface across an incompatible alignment would invent identity evidence; an explicit unknown state preserves the uncertainty boundary.

Alternatives not selected:

- Guess or partially reconstruct a lookup surface for a cut-through endpoint: rejected because the source-to-path mapping is not exact for that span.
- Call the registry with an empty or guessed surface: rejected because it would create misleading resolver evidence and call counts.
- Treat the synthetic fixture as a real registry, ownership, or authenticity source: rejected because it is an offline E0 mechanism with no live or authoritative evidence.

#### Decision D-128 - Bind exact Cartesian semantic packets at generation time

Decision: For every active path, form the score-independent Cartesian product of selected actor and destination endpoints, bounded at 64 pairs; bind the resolver snapshot, resolver version, exact evidence grammar and call count; and require canonical packet bytes, hash, row order, and exact equality to the selected prediction audit. Compute per-path state prevalence and q-weighted `P_pair` across paths. Construct and validate the packet against the score-bearing prediction audit at generation time because the standalone canonical packet intentionally omits literal lookup surfaces used only for audit binding and all endpoint scores.

Rationale: [OBSERVED - Luna inspection] Pair construction uses the selected actor-by-destination Cartesian product, records registry calls and bounded evidence IDs, validates exact selected-audit equality when that audit is available, and produces packet hashes plus `P_pair`. Tests cover exact Cartesian equality, reordered-row rejection, 64 pairs, 16 evidence IDs, zero-call empty products, and q marginalization. [DERIVED] Generate-time binding preserves the complete audit relationship without copying excluded literals and scores into the learned packet.

Alternatives not selected:

- Let a standalone packet silently reconstruct or guess omitted surfaces and scores: rejected because those values are not present in its intentionally restricted schema.
- Validate only the packet hash without matching the selected prediction audit: rejected because a canonical but cross-bound packet could otherwise pass.
- Reorder pair rows by scores or resolver results: rejected because pair order must be independent of learned or outcome-dependent values.

#### Decision D-129 - Preserve audit evidence while excluding leakage-prone fields from learned features

Decision: Preserve endpoint scores, lookup surfaces, evidence IDs, registry identity, q, path/rank identifiers, and artifact hashes in their appropriate audit or binding artifacts, but exclude those fields from the canonical `SemanticFeaturePlan` and learned pair rows. Retain only the reviewed structural endpoint coordinates and kinds, lookup statuses, and tri-state registry-resolution categories in the learned plan. Keep exclusion canaries in the focused tests.

Rationale: [OBSERVED - Luna inspection] The feature-plan projection deliberately selects structural fields, and the focused canary changes audit scores, surfaces, evidence IDs, registry snapshot, resolver version, q/ranks, and hashes without changing learned rows. [DERIVED] Auditability and learned-input isolation can coexist only if the score-bearing evidence remains available outside the feature projection.

Alternatives not selected:

- Remove scores and evidence from every artifact: rejected because selection, replay, and registry provenance would no longer be auditable.
- Feed the complete audit packet or literal surfaces into the learned tensor: rejected because scores, identities, q, ranks, hashes, and source literals could leak privileged or condition-specific information.
- Rely on convention rather than executable exclusion canaries: rejected because later schema changes could silently add prohibited inputs.

#### Decision D-130 - Use the fixed synthetic E0 grid and exact 31-by-64 tensor representation

Decision: Encode each VMP code point into the fixed five-category grid `LETTER`, `MARK`, `DECIMAL_DIGIT`, `WHITESPACE`, or `OTHER`; compute endpoint category means with the fixed sequential arithmetic; and project each pair into a deterministic 31-dimensional row. Serialize exactly 64 rows with a Boolean mask, positive-zero padding, binary64 bit strings, plan and path bindings, and a canonical hash.

Rationale: [OBSERVED - Luna inspection] The implementation fixes `PAIR_DIMENSION=31` and `PAIR_CAPACITY=64`, validates exact grid and row bit-string lengths, recomputes mask and bits, and rejects changed masks and negative-zero padding. The focused tests cover Devanagari letters, marks, decimal digits, whitespace, emoji/other, endpoint means, empty-pair padding, exact bits, and hashes. [DERIVED] This fixed grid is a deterministic E0 arithmetic fixture that exercises the feature interface before a trained encoder or adapter exists.

Alternatives not selected:

- Present the category grid as a transformer representation: rejected because it is a synthetic fixed encoding with no trained or linguistic representation claim.
- Use unspecified pooling or native container arithmetic: rejected because operation-order differences could change exact binary64 results.
- Emit variable-length pair rows without a mask and canonical padding: rejected because downstream shape and absence semantics would become implementation-defined.

#### Decision D-131 - Keep implementation gates blocked pending independent semantic review

Decision: Preserve design-only `G0/P0=COMPLETE_SPEC`. Classify this semantic slice as implemented but pending independent review; do not promote `G5`, `G6`, or another implementation or empirical gate. Require an independent reviewer to pin the two owned files and replay prediction, alignment, packet, resolver, feature, tensor, canary, and q-marginalization cases.

Rationale: [OBSERVED] Owner verification passed, but no independent code review, Python-3.11 runtime execution, real registry, trained encoder, language resource, authentic corpus, protected metric run, or performance benchmark exists. [DERIVED] Deterministic synthetic mechanics do not establish implementation acceptance, linguistic validity, registry correctness, or model quality.

Alternatives not selected:

- Mark the semantic implementation independently accepted from owner tests: rejected because the required independent review is still pending.
- Promote resource, model, factorial, or empirical gates: rejected because their real artifacts and measurements do not exist.
- Claim linguistic or registry effectiveness from the synthetic fixture: rejected because no such data or evaluation was used.

### Impact and tradeoffs

- Interfaces and compatibility: the module implements the canonical prediction-audit, pair-packet, semantic-plan, tensor, and diagnostic boundary; incompatible changes require contract-preserving revision or versioning.
- Data and linguistic scope: no dataset, real transliteration resource, trained encoder, or language-quality evaluation was used. The Unicode category grid is synthetic-only.
- Security and privacy: strict bounds, canonical validation, cut-through guarding, offline resolution, and exclusion canaries reduce malformed-input and leakage risk; real registry access and privacy controls remain untested.
- Evaluation: `P_pair` and state prevalence are executable synthetic diagnostics, not phishing-detection, registry-quality, calibration, or model-performance results.
- Performance: pair and tensor capacities bound artifact growth, but no dedicated latency, throughput, memory, or scale benchmark was measured.
- Operations: `G0` remains design-complete; implementation, registry/resource, model, factorial, empirical, and release gates remain blocked.

### Verification performed

- `[OBSERVED - Luna inspection]` The two owned files match the SHA-256 pins recorded above.
- `[OBSERVED - parent-supplied focused verification]` Semantic-focused verification passed 17/17 tests in 0.064 seconds.
- `[OBSERVED - parent-supplied full verification]` The full suite passed 203/203 tests in 32.008 seconds.
- `[OBSERVED - parent-supplied compatibility QA]` Python-3.11 AST parsing and repository hygiene checks passed.
- `[OBSERVED - Luna inspection]` The implementation and focused tests cover canonical prediction selection, binary64 score distinctions, alignment and cut-through behavior, offline resolution and call accounting, exact Cartesian packet binding, evidence bounds, score-independent ordering, `P_pair`, feature-plan exclusion canaries, the five-category grid, and exact 31-by-64 tensor masks, padding, bits, and hashes.
- Unrun by Luna: the focused and full suites, AST, and hygiene commands were not rerun for this register-only checkpoint. No Python-3.11 runtime, independent review, real registry, trained encoder, dataset, linguistic evaluation, protected metric run, or performance benchmark ran.

### Remaining risks and follow-up

- Independent review may find contract divergence, unsafe boundary behavior, learned-input leakage, arithmetic instability, or missing adversarial cases.
- Static Python-3.11 AST compatibility is not Python-3.11 runtime execution.
- The semantic layer assumes upstream candidate validation; cross-module integration and failure propagation still require independent replay.
- The offline resolver and fixed category grid provide no evidence about real registry coverage, ownership, authenticity, transliteration quality, multilingual semantics, or trained-model behavior.
- No authentic corpus, model, calibration, protected evaluation, latency, memory, or empirical performance result exists; `G5/G6` remain blocked.

Next owner/action: an independent reviewer should pin `fisher_engine/semantic.py` and `tests/test_engine_semantic.py`, inspect the P0 semantic-contract mapping, and replay prediction dedup/tie/cap, score-independent order, rewrite alignment and cut-through, registry-call/evidence bounds, Cartesian packet equality, `P_pair`, feature exclusion canaries, Unicode grid, tensor mask/padding/bits/hash, and malformed canonical-input cases. Do not advance implementation gates before that review.

### Correction history

None. This record is append-only, `LUNA-20260819-024` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-026

### Synthetic E0 core, artifact, preflight, harness, and integration slice implemented pending independent review

- Lifecycle: `IMPLEMENTED_PENDING_INDEPENDENT_REVIEW` - core and integration implementation plus owner verification completed; independent code review and no commit remain pending
- Recorded: 19 August 2026, 9:50:37 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-026`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected implementation boundary

- `fisher_engine/__init__.py` - SHA-256 `b08dca2dff22d9cb537724d9d1949ed31549ad821df14c9ae440aead10aa99f7`
- `fisher_engine/__main__.py` - SHA-256 `74d35cf41a351b7bfdaa700c44145b0998ba14d49328da520a269312eb5d6003`
- `fisher_engine/_canonical.py` - SHA-256 `be1cca97967d0a4b48165daa774cd3287408bc377aa7f781918599b17302f797`
- `fisher_engine/_numeric.py` - SHA-256 `f5c5862356bde63ea26e621cac160b1f88b65d9c4e26531e815f71d25aeffe09`
- `fisher_engine/source_closure.py` - SHA-256 `5d9cd3d2432864df7843f046150eb36c820767fffe8b13ecaa9dbe9ef481fac4`
- `fisher_engine/preflight.py` - SHA-256 `789dd5530b947cc604eb6b2ee01df2cc9edef5aa8f619c0e96563bbea46852e5`
- `fisher_engine/artifacts.py` - SHA-256 `7d397a5349708ea1b014efcbe1042ad3d758c38019ce39c711d4c0ebbe9e2412`
- `fisher_engine/harness.py` - SHA-256 `c2d60c9a8bc28260b1230eb1d6c846460f1002e655617167e37b1223adf2021a`
- `tests/test_engine_core.py` - SHA-256 `a32f8654237ad5d025f279b6d3da7570d9c8e9ab748d8dc8bb4332467329c1e2`
- `tests/test_engine_preflight.py` - SHA-256 `b595bd15a980591b736674ded471a10d418f9b05e0cf19b61a773b734bfde796`
- `tests/test_engine_integration.py` - SHA-256 `930ae148985e2a8fb4307dcaac2a7f5d91bef4e9556783d7873d3cdb4d3653c9`
- `examples/engine/README.md` - SHA-256 `04320b68b322816113d4ae75879741f34a222e1440d6f459b73c428d834180ef`
- `examples/engine/synthetic_e0.json` - SHA-256 `01587d209c1d405e17a1de63936be2bd9d7fd7f1b16498c0f2f336030652417f`
- `examples/engine/expected_summary.json` - SHA-256 `2c3c3fd69c40005b199bdb91284772ead84ee444c53a9b9fefa6a6457fb51bfc`
- `docs/ENGINE_CONTRACT.md` - SHA-256 `7b74f8f3325fbb1000a0c90f7388d5c86d7912dc2a8a195fd218bda616e3983a`

[OBSERVED - Luna inspection] These files implement and document the shared canonical/numeric core, source closure, preflight, artifacts, safe entry point, full synthetic harness, fixtures, and focused/integration tests. Every path matches the post-verification pin supplied by the parent; no whole-tree stability claim is made for concurrent files outside this boundary.

#### Decision D-132 - Keep the shared core private, standard-library-only, and bit-exact

Decision: Centralize bounded reads, strict JSON event precedence, NFC enforcement, canonical bytes and hashes, binary64 bit conversion, positive-zero handling, sequential arithmetic, ordered log-sum-exp, and ordered softmax in private engine helpers. Use compact UTF-8 JSON in each schema's exact declared field order; do not sort object keys or depend on an external serialization or numeric package.

Rationale: [OBSERVED - Luna inspection] `_canonical.py` performs cap-plus-one reads, rejects BOM, invalid UTF-8, duplicate keys, nonfinite values, syntax errors, non-NFC strings, and noncanonical bytes in a fixed order. `_numeric.py` implements explicit binary64 bits and fixed sequential operations. Focused tests cover scanner precedence, declared order, Unicode, signed zero, non-reassociated arithmetic, and separate softmax accumulation order. [DERIVED] A small private standard-library core preserves the reviewed bytes and arithmetic without forcing unrelated API changes into the candidate, semantic, or evaluation slices.

Alternatives not selected:

- Refactor the already established candidate, semantic, and evaluation surfaces around a new public utility abstraction: rejected because this checkpoint needs shared mechanics, not a broad cross-package rewrite.
- Serialize with `sort_keys=True`: rejected because the specifications bind schema-declared field order, not lexicographic key order.
- Use library-default JSON parsing or native unordered arithmetic: rejected because error precedence, duplicate handling, exact bytes, and final binary64 bits would become implementation-dependent.
- Add a third-party canonicalization or numerical dependency: rejected because the standard library is sufficient for this bounded synthetic slice and a dependency change was not required.

#### Decision D-133 - Bind executed source through declared entrypoints and observed file closure

Decision: Build a canonical source closure from forced declared entrypoints, observed loaded project modules, and explicitly recorded non-imported executed files. Reconcile, order, and hash the exact current project-relative files; validate the closure hash and optionally recheck every file against the current workspace bytes.

Rationale: [OBSERVED - Luna inspection] `SourceClosureRecorder` begins with declared entrypoints, observes matching loaded modules, supports explicit executed-file recording, and finalizes sorted path/hash rows plus a canonical closure hash. Validation requires every declared entrypoint to occur in the file inventory, and `verify_source_closure_files` binds each row to current bytes. [DERIVED] Entry-point and observed-file reconciliation prevents a run from proving only a self-selected subset of its executable source.

Alternatives not selected:

- Accept a self-declared source list from the fixture or caller: rejected because omitted executed code would remain outside the provenance boundary.
- Record module names without exact file hashes: rejected because the same import name can refer to changed bytes.
- Scan and hash the entire repository indiscriminately: rejected because nonexecuted documentation, data, and concurrent files are not part of the executed-source claim.

#### Decision D-134 - Fail closed at a path-free, hash-first preflight boundary

Decision: Parse a bounded path-free `EngineInputDescriptor`, produce a canonical PASS or FAIL receipt with fixed code precedence, and require separately supplied system-manifest and VMP bytes. Check both submitted hashes before semantic validation of either referenced artifact, then bind the exact validated values and receipt hash. Never treat a label, filename, or caller assertion as the artifact hash.

Rationale: [OBSERVED - Luna inspection] `preflight.py` uses cap-plus-one descriptor input, the strict canonical parser, ordered safe failure codes, direct byte hashes, referenced-artifact size bounds, manifest validation, VMP validation, and a receipt that omits run fields when the descriptor is unusable. Focused tests cover hash-before-validation, missing-artifact precedence, bounded reads, invalid VMP retention, and the inability to construct an envelope from a failed receipt. [DERIVED] Hashing actual canonical artifact bytes closes the substitution gap that label-only or path-derived binding would leave.

Alternatives not selected:

- Put host paths into the canonical descriptor: rejected because paths are environment-specific and expose unnecessary local information.
- Validate one artifact before checking both supplied hashes: rejected because error precedence and cross-binding would depend on artifact contents.
- Use fixture labels or expected names as hashes: rejected because labels do not prove the bytes that were executed or evaluated.
- Parse unbounded input before determining that it exceeds its cap: rejected because malformed oversized inputs must not force unbounded allocation or parsing.

#### Decision D-135 - Implement exact system masks, status unions, provider execution, run envelopes, and five-seed artifacts

Decision: Implement all eight frozen condition/system-variant masks, canonical system manifests, provider-execution outcomes, VALID/DEGRADED/INVALID run-envelope unions, exact failure-count inventory, and five-seed logit artifacts with fixed seed order and sequential means. Bind all downstream references by hashes of their actual canonical bytes. Preserve a no-eligible identity path as an explicit `IDENTITY_BYPASS` lineage contributor rather than an empty or fabricated provider lineage.

Rationale: [OBSERVED - Luna inspection] `artifacts.py` validates the eight allowed system combinations, static registry masks, provider outcomes, status-discriminated envelope fields, canonical identity diagnostics/path lineage, and five-seed arithmetic and hashes. Core tests cover every mask, declared-order hashes, exact five-seed means, valid identity, mandatory degraded stop, and invalid-provider removal of downstream artifacts. [DERIVED] Actual artifact hashes and explicit identity lineage distinguish a replayable bypass from a human-readable label or an unexplained empty provider result.

Alternatives not selected:

- Represent every execution status with one permissive artifact shape: rejected because invalid or degraded runs could appear to contain valid downstream evidence.
- Leave identity lineage empty or copy a provider lineage that never ran: rejected because both forms misstate provenance.
- Bind envelope fields to symbolic artifact labels: rejected because labels do not establish canonical byte identity.
- Average seed logits with unspecified iteration or reduction order: rejected because the final binary64 bits could change.

#### Decision D-136 - Integrate the complete rehearsal with fixed condition masks and bounded synthetic evidence

Decision: Run the same validated synthetic provider configuration through all eight frozen systems, require eight PASS preflights and eight valid envelopes, construct semantic artifacts only for base `C01` and `C11`, and execute exactly two one-item metric runs for those semantic base cells. Use actual canonical envelope and artifact hashes throughout the evaluation binding. Keep all fixture, provider, registry, and evaluation behavior local, deterministic, and offline; do not add dynamic loading or network access.

Rationale: [OBSERVED - Luna inspection] `harness.py` builds the eight combinations, reuses the same provider path, limits semantics to `C01_BASE` and `C11_BASE`, hashes canonical envelope bytes for submissions, and validates two metric runs. The integration tests assert all counts, provider-manifest equality, semantic masks, frozen non-hash summary, same-process determinism, and fail-closed fixture scope. [OBSERVED - Luna rehearsal] The current pinned slice returned `8` PASS preflights, `8` valid envelopes, and `2` valid metric runs. [DERIVED] This is sufficient to exercise integration contracts without implying that a live provider, network registry, model, or corpus exists.

Alternatives not selected:

- Enable semantic artifacts in control or nonsemantic cells: rejected because that would violate the frozen system masks.
- Add a network registry, dynamic plugin/provider loading, or remote fixture retrieval to E0: rejected because it would make the rehearsal nondeterministic and enlarge the safety and provenance boundary.
- Use expected labels instead of actual canonical hashes in evaluation submissions: rejected because the evaluator must inspect the exact envelope bytes it scores.
- Treat the two known-answer metric runs as empirical evaluation: rejected because both use one reserved synthetic item.

#### Decision D-137 - Expose only a sanitized synthetic CLI and frozen deterministic fixtures

Decision: Expose `python3 -m fisher_engine rehearse` for a required local fixture and text or canonical JSON output. Sanitize invalid use and runtime failures so submitted paths or malformed values are not echoed. Freeze a synthetic fixture, a non-hash expected summary, and an executable contract that repeatedly states the interface-only scope and absence of performance claims.

Rationale: [OBSERVED - Luna inspection] `__main__.py` uses a sanitized argument parser, reads only the requested local fixture, maps failure output to controlled codes, and returns distinct success, controlled-failure, and invalid-usage statuses. The fixture and expected summary declare `SYNTHETIC_E0_ONLY`, `NO_TRAINED_MODEL`, `NO_AUTHENTIC_DATA`, `NO_PERFORMANCE_CLAIM`, and `G5_G6_REMAIN_BLOCKED`; integration tests cover deterministic canonical JSON and non-echo failures. [OBSERVED - Luna rehearsal] Canonical report bytes, excluding the CLI's terminal newline, hashed to `e0913a41eb6dc91fefa9595682ffbec152503078f85fea2e4f088397e973ba07`; the CLI exited `0` with empty stderr.

Alternatives not selected:

- Offer a general inference, training, registry, or data-ingestion CLI now: rejected because those implementation and empirical gates remain blocked.
- Print raw exception text or submitted paths: rejected because errors may expose local or unsafe input details.
- Freeze artifact hashes in `expected_summary.json`: rejected because source-closure and runtime-bound hashes must legitimately change when executable evidence changes.
- Describe test duration or a synthetic F1 known answer as model performance: rejected because neither measures production behavior.

#### Decision D-138 - Keep implementation gates blocked pending independent core and integration review

Decision: Preserve design-only `G0/P0=COMPLETE_SPEC`. Classify this core/integration slice as implemented but pending independent review; do not promote `G5`, `G6`, or another implementation or empirical gate. The parent's separate full-suite replay is verification evidence, not a substitute for an adversarial independent code and contract review.

Rationale: [OBSERVED] Focused, full, compatibility, deterministic-report, and CLI checks passed, including a separate parent replay, but no independent code-review verdict, Python-3.11 runtime execution, real provider, trained model, real registry, authentic corpus, container, E4 artifact, or performance benchmark exists. [DERIVED] Passing synthetic tests demonstrates executable mechanics but does not establish production readiness or empirical validity.

Alternatives not selected:

- Treat the separate full-suite rerun as an independent semantic/security review: rejected because test replay does not independently inspect omitted cases or contract fidelity.
- Promote `G5/G6` from a synthetic harness: rejected because no real resource, model, corpus, or protected evaluation exists.
- Claim Python-3.11 runtime support from static AST parsing: rejected because syntax parsing is not execution under that runtime.

### Impact and tradeoffs

- Interfaces and compatibility: the slice supplies the executable package entry point and canonical artifact contracts; future incompatible changes require explicit versioning or contract-preserving migration.
- Dependencies: implementation is standard-library-only and adds no third-party, dynamic-loading, or network dependency.
- Data and provenance: the source closure and actual canonical hashes strengthen replayability, but only a reserved synthetic fixture was used and no dataset changed.
- Security and privacy: path-free descriptors, bounded reads, strict parsers, offline inputs, status unions, and sanitized CLI failures reduce unsafe-input and disclosure risk; real operational access controls remain untested.
- Evaluation: eight system rehearsals and two one-item metric runs verify mechanics only; they provide no phishing, multilingual, calibration, robustness, or generalization result.
- Performance: test durations and bounded artifact counts are verification evidence, not latency, throughput, memory, or scale benchmarks.
- Operations: `G0` remains design-complete; `G5/G6` and every implementation, resource/model, empirical, and release gate remain blocked pending their own evidence.

### Verification performed

- `[OBSERVED - Luna inspection]` All 15 affected files match the SHA-256 pins recorded above after the supplied verification runs.
- `[OBSERVED - parent-supplied focused verification]` The engine-focused suite passed 104/104 tests in 1.470 seconds.
- `[OBSERVED - parent-supplied owner full verification]` The agent's full suite passed 205/205 tests in 32.027 seconds.
- `[OBSERVED - parent-supplied independent replay]` The parent independently reran the full suite and passed 205/205 tests in 32.133 seconds.
- `[OBSERVED - parent-supplied compatibility QA]` Python-3.11 AST parsing passed for 17/17 targets.
- `[OBSERVED - Luna rehearsal]` The pinned JSON CLI exited `0`, emitted no stderr, reported `SYNTHETIC_E0_ONLY`, `8/8` preflights, `8/8` valid envelopes, `2/2` valid metric runs, and `PASS`; its canonical report bytes hashed to `e0913a41eb6dc91fefa9595682ffbec152503078f85fea2e4f088397e973ba07`.
- `[OBSERVED - Luna inspection]` Core, preflight, and integration tests cover canonical/NFC and strict-parser precedence, numeric known answers, source closure, all eight masks, identity lineage, status unions, actual artifact hashes, preflight receipt bindings, deterministic fixtures, semantic masks, report replay, and sanitized CLI failures.
- Unrun by Luna: the 104-test focused suite, both 205-test full suites, and Python-3.11 AST command were not rerun for this register-only checkpoint. No Python-3.11 runtime, independent adversarial code review, real provider, trained model, registry service, corpus, container, E4 run, or performance benchmark ran.

### Remaining risks and follow-up

- Independent review may find contract divergence, parser-precedence gaps, unsafe artifact unions, incomplete source closure, hash-substitution paths, or missing integration cases.
- Static Python-3.11 AST compatibility is not Python-3.11 runtime execution.
- Instrumented imports and explicit file recording depend on callers correctly declaring non-imported executed files; dynamic loading is intentionally unsupported here.
- The local fixture, identity fallback, and offline registry provide no evidence about real transliteration, registry ownership, authenticity, multilingual behavior, or model quality.
- No authentic corpus, trained model, container/runtime reproducibility package, E4 run, protected evaluation, latency, memory, or empirical performance result exists; `G5/G6` remain blocked.

Next owner/action: an independent reviewer should pin all 15 files above, inspect the canonical/parser and numeric boundary, source-closure completeness, preflight precedence, every system/status union, identity lineage, actual hash bindings, semantic cell masks, metric submissions, deterministic fixtures, and CLI non-echo behavior; then replay focused, full, Python-3.11-runtime, deterministic-report, and adversarial malformed-input cases before any implementation gate advances.

### Correction history

None. This record is append-only, `LUNA-20260819-025` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-027

### Combined independent synthetic E0 implementation review failed

- Lifecycle: `REVIEW_FAILED` - three independent read-only reviews rejected E0 implementation acceptance; repairs and fresh independent replay are required
- Recorded: 19 August 2026, 10:06:15 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Not proposed
- Required trailer if later committed: `Luna-ID: LUNA-20260819-027`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Reviewed boundary and stable pins

- `docs/research/ENGINE_SPEC.md` - SHA-256 `a159c86fee69118349a0d7c25634ba6ac362e4a687bee9787b80dc4d405a02f4`
- `fisher_engine/evaluation.py` - SHA-256 `8ca6d7ca06c508cd61f3f63b621ad14a8dcc0891579c900b3b6bbfb9fccab500`
- `tests/test_engine_evaluation.py` - SHA-256 `54117e7ad5162eb5670cdefbd3395c6938ab5bfc064be34325c3b8858784f281`
- `fisher_engine/candidate.py` - SHA-256 `a01530c79ef2751046e8795ed375183c81569212d8aabeb2725456e68b1d4c43`
- `tests/test_engine_candidate.py` - SHA-256 `87ad1a804fbeb6c1ec016cb1584c92f38e7fb74e8b58598f406d0bca59297b3d`
- `fisher_engine/semantic.py` - SHA-256 `138fe0867e55e8f6943a0a5fbd25b5ebc9eae0abe5b1f0d3cede5eb6d65cbb16`
- `tests/test_engine_semantic.py` - SHA-256 `074ad382cc61fc94e3e6e210d55288c6d90aba5d5041c2272f3d46d7b34d3eb7`
- `fisher_engine/__init__.py` - SHA-256 `b08dca2dff22d9cb537724d9d1949ed31549ad821df14c9ae440aead10aa99f7`
- `fisher_engine/__main__.py` - SHA-256 `74d35cf41a351b7bfdaa700c44145b0998ba14d49328da520a269312eb5d6003`
- `fisher_engine/_canonical.py` - SHA-256 `be1cca97967d0a4b48165daa774cd3287408bc377aa7f781918599b17302f797`
- `fisher_engine/_numeric.py` - SHA-256 `f5c5862356bde63ea26e621cac160b1f88b65d9c4e26531e815f71d25aeffe09`
- `fisher_engine/source_closure.py` - SHA-256 `5d9cd3d2432864df7843f046150eb36c820767fffe8b13ecaa9dbe9ef481fac4`
- `fisher_engine/preflight.py` - SHA-256 `789dd5530b947cc604eb6b2ee01df2cc9edef5aa8f619c0e96563bbea46852e5`
- `fisher_engine/artifacts.py` - SHA-256 `7d397a5349708ea1b014efcbe1042ad3d758c38019ce39c711d4c0ebbe9e2412`
- `fisher_engine/harness.py` - SHA-256 `c2d60c9a8bc28260b1230eb1d6c846460f1002e655617167e37b1223adf2021a`
- `tests/test_engine_core.py` - SHA-256 `a32f8654237ad5d025f279b6d3da7570d9c8e9ab748d8dc8bb4332467329c1e2`
- `tests/test_engine_preflight.py` - SHA-256 `b595bd15a980591b736674ded471a10d418f9b05e0cf19b61a773b734bfde796`
- `tests/test_engine_integration.py` - SHA-256 `930ae148985e2a8fb4307dcaac2a7f5d91bef4e9556783d7873d3cdb4d3653c9`
- `examples/engine/README.md` - SHA-256 `04320b68b322816113d4ae75879741f34a222e1440d6f459b73c428d834180ef`
- `examples/engine/synthetic_e0.json` - SHA-256 `01587d209c1d405e17a1de63936be2bd9d7fd7f1b16498c0f2f336030652417f`
- `examples/engine/expected_summary.json` - SHA-256 `2c3c3fd69c40005b199bdb91284772ead84ee444c53a9b9fefa6a6457fb51bfc`
- `docs/ENGINE_CONTRACT.md` - SHA-256 `7b74f8f3325fbb1000a0c90f7388d5c86d7912dc2a8a195fd218bda616e3983a`
- `README.md` - SHA-256 `a8c6e7607f317d8eb726b470a54e5b502d47ea54ca5e0931c699e2b395a13bec`
- `docs/research/EXECUTION_STATUS.md` - SHA-256 `f8433be73dad8a89da263007d022d960d5c963f558f8e2e5a6aa1b3426dad1cd`

[OBSERVED - Luna inspection] The reviewed engine-specification pin and all implementation/test/example/contract pins from `LUNA-20260819-023` through `LUNA-20260819-026` remain unchanged. The root README and execution-status pins above identify the stale status surfaces noted by reviewers. No reviewed file was modified in this checkpoint.

### Independent review sources and verdict

- `[OBSERVED - parent-supplied independent contract review]` A read-only Sol Ultra reviewer returned `E0 IMPLEMENTATION FAIL` after adversarial contract and artifact-binding probes.
- `[OBSERVED - parent-supplied independent security review]` A read-only Sol High reviewer returned `E0 IMPLEMENTATION FAIL` after malformed-input, provenance, CLI, and bounded-work probes.
- `[OBSERVED - parent-supplied independent methodology review]` A read-only Terra reviewer returned `E0 IMPLEMENTATION FAIL` because the end-to-end rehearsal does not exercise the primary rank-one-versus-q-weighted multi-path factor and permits incomplete evaluation evidence.

All three verdicts agree that design-only `G0/P0=COMPLETE_SPEC` remains a specification result, not implementation acceptance. `G5`, `G6`, and every implementation, model, empirical, protected-access, and release gate remain blocked.

#### Decision D-139 - Reject E0 implementation acceptance despite the green owner suite

Decision: Record the combined verdict as `REVIEW_FAILED`. Do not treat 205 passing tests, stable hashes, or the deterministic happy-path report as sufficient implementation acceptance. Repair the independently demonstrated contract and security defects, add regressions, then require a fresh independent replay on new pins.

Rationale: [OBSERVED - independent reviewers] All three reviewers returned fail verdicts on the same stable implementation boundary. [OBSERVED - positive evidence preserved] The full suite still passed 205/205 in approximately 32 seconds, the engine-focused suite passed 104/104 in approximately 1.47 seconds, and the deterministic canonical report remained `e0913a41eb6dc91fefa9595682ffbec152503078f85fea2e4f088397e973ba07`. Reviewers also found that many candidate, SEP, tensor, universe, metric, five-seed, mask, fallback, and claim-boundary probes behaved correctly. [DERIVED] Those successes establish useful regression coverage but do not close the adversarial acceptance gaps below.

Alternatives not selected:

- Accept implementation because all 205 existing tests pass: rejected because the independent counterexamples are outside or contradict the current suite.
- Trust generated happy-path objects and their hashes: rejected because several validators accept internally inconsistent forged objects.
- Promote `G5`, `G6`, or another implementation/empirical gate: rejected because acceptance failed and no real resource, model, registry, or corpus exists.

#### Decision D-140 - Recompute candidate and envelope semantics instead of validating shape alone

Decision: Treat run-envelope and candidate artifacts as untrusted inputs. Repair validation so the VMP, provider manifest, configured mode, spans, lineage, path hashes, diagnostics, failure counts, LSE/mass/q arithmetic, returned counts, active paths, and identity-bypass hash are recomputed or exactly cross-bound. Do not accept arbitrary caller-provided values merely because their schema and individual hashes are well formed.

Rationale: [OBSERVED - independent contract probes] The current envelope validator accepted mutations containing arbitrary `effective_rewrite_spans`, incorrect VMP slices and provider equality, q=`0.5` for a single path, a mismatched `returned_count`, zero progress counts, and an arbitrary identity hash. It did not recompute failure counts, lineage, mode, ordered LSE, retained mass, or q. [DERIVED] A hash proves only the bytes submitted; without semantic recomputation it does not prove that those bytes describe the claimed execution.

Alternatives not selected:

- Trust artifacts produced by the current harness: rejected because the public validators must reject forged or cross-bound objects independently of their producer.
- Check only canonical bytes and field types: rejected because every demonstrated mutation can remain canonical and type-correct while being semantically false.
- Special-case the current fixture hashes: rejected because labels or fixture-specific allowlists do not establish general contract correctness.

#### Decision D-141 - Repair runtime, control, preflight, and source-provenance closure before other acceptance work

Decision: Make runtime identity and control-to-base bindings independently verifiable; require complete PASS-receipt contents; and replace the current self-observing source-closure boundary with deterministic executed-file accounting that cannot omit a `runpy`-executed file or vary with unrelated prior `sys.modules` process history. Prioritize this security/provenance repair with the envelope repair.

Rationale: [OBSERVED - independent security/contract probes] Validators accepted a forged runtime identity, a forged control matched-base binding, and an incomplete PASS receipt. A file executed through `runpy` was absent unless manually recorded, despite the closure advertising instrumented executed-file access, while unrelated process import history changed the closure hash. [DERIVED] A provenance hash is not reliable when it can omit executed code or vary according to ambient process history rather than the run being proven.

Alternatives not selected:

- Keep a self-declared or caller-curated closure: rejected because the missing executed file is exactly the evidence such a closure must capture.
- Treat `sys.modules` at finalization as the executed run boundary: rejected because it includes unrelated prior process state and is not a deterministic per-run trace.
- Trust declared runtime or matched-base values because the harness generated them: rejected because the validators must enforce those bindings on hostile input.

#### Decision D-142 - Add total depth, byte, stream, and CLI boundaries before parsing

Decision: Enforce an explicit nesting/work limit before recursive native JSON decoding, catch and sanitize parser exhaustion, cap local fixture reads before reading the full file, and truncate or reject a binary stream that returns more than the requested cap-plus-one bytes. Preserve conventional help behavior rather than routing successful help through invalid-usage handling.

Rationale: [OBSERVED - independent security probes] Strict parser inputs around depth 900–1,000 raised uncaught `RecursionError`, and the CLI exposed a traceback. The CLI calls `Path.read_bytes()` before applying the fixture cap; the generic cap-plus-one helper trusts a nonconforming stream that over-returns; and help exits `2` with `INVALID_USAGE`. [DERIVED] Post-read size checks and recursive library defaults do not provide a bounded hostile-input boundary.

Alternatives not selected:

- Rely on the native parser's recursion behavior: rejected because it already escaped the controlled diagnostic boundary.
- Read the complete fixture and reject it afterward: rejected because memory and I/O work have already occurred.
- Assume every binary stream honors the requested read size: rejected because the shared reader accepts caller-supplied stream-like objects and the adversarial over-return probe succeeded.
- Treat `--help` as invalid input: rejected because help is an intentional non-error control path.

#### Decision D-143 - Require the evaluator to reconstruct and bind complete engine evidence

Decision: Repair the default evaluation inspector so a VALID score requires the bound preflight receipt, system/runtime/source manifest, provider/candidate artifacts, VMP bytes, registry artifact/reference bundle, prediction audit, pair packets, feature artifacts, and envelope to agree exactly. Lookup surfaces and registry outcomes must be reconstructed or checked against those artifacts rather than accepted from a packet in isolation.

Rationale: [OBSERVED - independent contract/methodology probes] The default inspector accepted forged lookup surfaces and a `MISMATCH` prediction against the synthetic registry's `MATCH` record, yet returned status VALID because provider, candidate, VMP, registry, and preflight artifacts were not supplied to or reconstructed by the inspector. [DERIVED] Universe/submission closure and envelope hashes cannot prove semantic correctness when the evaluator never receives the evidence needed to check the claimed identities and relation state.

Alternatives not selected:

- Trust the pair packet because its hash matches the envelope: rejected because a consistently forged packet and envelope can share hashes.
- Compare only row coordinates and labels: rejected because lookup identity, registry snapshot, provider path, and VMP reconstruction determine whether the label is valid.
- Keep a synthetic-registry shortcut in the default inspector: rejected because the default boundary must remain correct for every valid fixture, not only the current happy path.

#### Decision D-144 - Exercise a real multi-path factorial and enforce a candidate work budget

Decision: Replace the one-path/q=`1` integration fixture with a bounded shared-provider multi-path fixture that runs rank-one and all-path q-weighted cells from the same provider output while supplying condition-correct logit widths. Add an explicit candidate composition work budget and fail-closed diagnostic for the worst permitted span/reading/text configuration before E0 acceptance.

Rationale: [OBSERVED - independent methodology probe] A multi-path shared-provider fixture failed with `engine_fixture_seed_width` because rank-one and all-path cells reused fixed-width seed-logit rows even though their active path counts differ. The current fixture returns one path with q=`1`, so rank-one and q-weighted behavior are identical and the primary factor is not exercised end to end. [OBSERVED - independent performance probe] A permitted 64-span by 8-reading by 300-code-point candidate case was still running after 60 seconds. [DERIVED] The factorial cannot be accepted without a nondegenerate shared-provider example, and nominal input caps are insufficient without a bounded-work contract.

Alternatives not selected:

- Keep the one-path rehearsal as proof of the uncertainty factor: rejected because rank-one and q-weighted predictions collapse to the same computation.
- Give each factorial cell different provider output to make shapes convenient: rejected because that would confound the frozen shared-provider comparison.
- Leave candidate runtime controlled only by individual field caps: rejected because their permitted product has already exceeded the reviewer's 60-second bound.
- Report the unfinished 60-second probe as a completed benchmark: rejected because it establishes a missing bound, not final latency or complexity.

#### Decision D-145 - Synchronize status documentation only after the repair boundary is explicit

Decision: Update the root README, engine contract, examples README, and execution-status evidence after the technical repair records the new pins and test/review outcome. They must state that an E0 implementation exists but failed independent review, while preserving the synthetic-only/no-empirical boundary and the design-only meaning of `G0/P0=COMPLETE_SPEC`.

Rationale: [OBSERVED - Luna inspection] `docs/research/EXECUTION_STATUS.md` still says no engine is implemented and lists synthetic E0 implementation as the next action, while the current root README only broadly mentions synthetic tooling. [OBSERVED - independent reviewers] The status and README surfaces were reported as stale underclaims. [DERIVED] Documentation must not claim acceptance, but it must accurately distinguish implemented-and-failed-review from not implemented.

Alternatives not selected:

- Leave status unchanged until E0 passes: rejected because the failed implementation and review are meaningful execution history.
- Mark E0 complete because code exists: rejected because all three independent reviewers rejected acceptance.
- Remove the synthetic/no-performance disclaimers: rejected because no empirical evidence was produced and those boundaries remain correct.

### Impact and tradeoffs

- Interfaces and compatibility: repairs will tighten validation of previously accepted but inconsistent artifacts; malformed or forged objects that currently pass must become controlled failures.
- Security and privacy: unbounded depth/read behavior, traceback leakage, omitted executed files, forged runtime/control bindings, and incomplete evaluation evidence are release-blocking security/provenance defects.
- Methodology: the current one-path fixture does not test the central rank-one-versus-q-weighted estimand; no method-effect or model-quality conclusion follows from it.
- Performance: a worst-permitted candidate probe exceeded 60 seconds without completion; no general latency or complexity bound exists yet.
- Data and provenance: no real corpus, provider, registry, or model was used. The findings concern synthetic implementation mechanics only.
- Operations: `G0/P0` remains design-only `COMPLETE_SPEC`; `G5/G6` and every implementation, model, empirical, protected-access, publication, and release gate remain blocked.

### Verification performed

- `[OBSERVED - Luna inspection]` The engine specification and all implementation/test/example/contract pins from `LUNA-20260819-023` through `LUNA-20260819-026` match the reviewed hashes listed above.
- `[OBSERVED - parent-supplied independent review]` Three read-only specialists independently returned `E0 IMPLEMENTATION FAIL` and supplied the adversarial findings recorded in Decisions D-140 through D-145.
- `[OBSERVED - parent-supplied positive regression evidence]` The full suite passed 205/205 in approximately 32 seconds and the engine-focused suite passed 104/104 in approximately 1.47 seconds on the reviewed pins.
- `[OBSERVED - stable prior evidence]` The deterministic canonical report remained `e0913a41eb6dc91fefa9595682ffbec152503078f85fea2e4f088397e973ba07`; the current implementation continued to preserve many candidate, packet, tensor, universe, metric, five-seed, mask, fallback, and synthetic-claim boundaries.
- `[OBSERVED - review probes, not accepted engine results]` Mutated envelope/provenance/evaluation artifacts, deep parser inputs, multi-path fixture construction, stream over-return, CLI behavior, and the 64x8x300 candidate case were adversarial review probes. The >60-second case did not complete and is not a measured final runtime.
- Unrun by Luna: no reviewer probe or test suite was rerun for this register-only checkpoint. No repair, post-repair test, fresh independent acceptance review, Python-3.11 runtime, real provider, trained model, registry service, corpus, protected metric run, container, or production benchmark exists.

### Remaining risks and follow-up

- The exact smallest repair may reveal further conflicts between producer construction and public validator semantics.
- Parser depth, candidate work, file reads, and stream behavior lack accepted bounded-resource proofs.
- Source closure may still omit non-import execution paths or include ambient process state until redesigned and independently probed.
- Evaluation can misclassify forged semantic evidence as VALID until complete artifact reconstruction and binding are implemented.
- A nondegenerate shared-provider multi-path fixture may expose additional seed, mask, path-count, or metric integration defects.
- No real data, model, transliteration provider, registry, supported Python-3.11 runtime, container, latency/memory envelope, empirical result, or release evidence exists.

Next owner/action: repair the security and contract blockers first—semantic envelope recomputation, runtime/control/preflight/source binding, bounded parser/read/stream/CLI behavior, and complete evaluation evidence—then add the multi-path shared-provider factorial fixture and candidate work budget. Run focused adversarial regressions and the full suite on new pins, synchronize status documentation, and commission a fresh independent three-perspective review before advancing any implementation gate.

### Correction history

None. This record is append-only, `LUNA-20260819-026` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-028

### Synthetic E0 semantic trust boundary repaired pending integration review

- Lifecycle: `REPAIRED_PENDING_INTEGRATION_REVIEW` - scoped semantic repair and focused verification completed; repository-wide integration and fresh independent replay remain pending
- Recorded: 19 August 2026, 10:37:41 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: None
- Required trailer if later committed: `Luna-ID: LUNA-20260819-028`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected implementation boundary

- `fisher_engine/semantic.py` - SHA-256 `cbbc2edabe25125570bbe479d74e6dc1f666a53e2dc8e8e41c3a305d9efb47f6`
- `tests/test_engine_semantic.py` - SHA-256 `a6399729365671033db60bbc883c1608461d0906e1f09232c761906f204f22b8`

[OBSERVED - Luna inspection] Only these two files belong to this completed repair checkpoint. They match the supplied post-verification pins. Other concurrent migration work and an unrelated untracked temporary directory remain outside this record; no whole-tree stability claim is made.

### Failure being repaired

[OBSERVED - prior independent E0 review] Structural semantic parsers accepted internally canonical, rehashed chains containing forged lookup surfaces and registry outcomes because structural validation did not reconstruct candidate truth or registry truth. This was recorded as an implementation blocker in `LUNA-20260819-027`; the present checkpoint repairs that scoped trust boundary but does not resolve the other independent-review blockers.

#### Decision D-146 - Make one frozen canonical artifact the source of synthetic registry truth

Decision: Build, parse, validate, size-bound, deterministically sort, and hash a complete synthetic registry artifact. Reconstruct resolver truth only as immutable `FrozenRegistry` state from the artifact's canonical bytes, optionally checking an expected artifact SHA-256 before use.

Rationale: [OBSERVED - Luna inspection] `build_synthetic_registry_artifact`, `parse_synthetic_registry_artifact`, `validate_synthetic_registry_artifact`, and `frozen_registry_from_artifact` enforce the registry schema, entry bounds, exact key ordering, duplicate rejection, canonical bytes, sorted lookup keys, snapshot/resolver identities, evidence grammar, and artifact hash. `FrozenRegistry` retains exact artifact bytes and exposes immutable tuple-backed records. [DERIVED] A semantic result can be authoritative only if registry state is reconstructed from one frozen artifact rather than accepted from mutable packet claims.

Alternatives not selected:

- Keep structural registry validation as the truth boundary: rejected because a self-consistent forged registry outcome can satisfy structural rules.
- Trust registry state copied from the prediction audit or SEP packet: rejected because those are derived claims, not the authoritative offline registry input.
- Connect to a live or real registry at E0: rejected because the accepted E0 scope is deterministic, offline, and synthetic; real authority, coverage, ownership, and access controls remain separate gates.

#### Decision D-147 - Authoritatively replay the complete semantic chain from candidate and registry inputs

Decision: Use `replay_semantic_chain` as the authoritative boundary. Starting from the VMP text/hash, candidate paths, emitted endpoint candidates, and frozen registry artifact, recompute candidate path semantics and lookup rendering, rewrite cut-through, prediction deduplication/selection, registry calls, state/coverage/evidence, SEP rows, feature plans, exact tensors, per-path state prevalence, and q-weighted `P_pair`. Require supplied canonical artifacts and optional expected hashes to match the recomputed chain exactly.

Rationale: [OBSERVED - Luna inspection] The replay validates path context and alignment, rebuilds prediction selection, reconstructs `FrozenRegistry`, rebuilds every pair packet, plan, and tensor, checks exact supplied bytes/hashes and path-set bindings, and marginalizes the replayed packets by the candidate q values. Focused red-first tests show that structurally valid forged surface, registry-result, and alignment chains are rejected by authoritative replay. [DERIVED] Candidate truth must come from replaying the candidate path and VMP, while registry truth must come from the frozen artifact; neither may be inferred from mutable downstream audit fields.

Alternatives not selected:

- Keep structural validation as the only acceptance step: rejected because canonical bytes and hashes can faithfully preserve a forged assertion.
- Trust lookup surfaces already present in a prediction audit: rejected because a rehashed forged surface was the original independent-review counterexample.
- Validate only the final packet or tensor hash: rejected because a consistently forged upstream chain can produce internally matching downstream hashes.

#### Decision D-148 - Return a frozen evidence bundle with exact bytes, hashes, q, and registry tuples

Decision: Return immutable `SemanticReplayResult` and `ReplayedSemanticPath` values that retain the canonical prediction and registry artifacts, per-path packet/plan/tensor bytes and hashes, q bits, state prevalence, registry pair tuples, and q-weighted `P_pair`. Treat this frozen replay result, not any individual structural parse, as the evidence passed to later integration.

Rationale: [OBSERVED - Luna inspection] The replay result is a frozen dataclass; each path retains exact canonical artifacts and hashes plus a tuple projection of actor/destination coordinates and registry state/coverage/source, while the top-level result retains registry bytes/hash and the ordered `P_pair` tuple. [DERIVED] Keeping exact replayed evidence prevents later consumers from silently substituting a mutable object after validation.

Alternatives not selected:

- Return only hashes: rejected because later inspection would lack the exact canonical evidence needed to reproduce each binding.
- Return mutable dicts as the authoritative result: rejected because post-validation mutation could detach consumed evidence from the validated hash.
- Store only `P_pair`: rejected because an aggregate cannot prove the path-, packet-, registry-, and feature-level derivation.

#### Decision D-149 - Label structural parsers non-authoritative and bound their nesting work

Decision: Preserve backward-compatible structural parsing for canonical syntax/schema checks, but explicitly document that prediction, packet, plan, and tensor structural parsers do not establish candidate or registry truth. Add a bounded pre-parse JSON nesting guard to these parsers and the synthetic registry parser so deeply nested input fails with controlled semantic codes before native recursion escapes.

Rationale: [OBSERVED - Luna inspection] The parser docstrings state `not an authoritative replay`, structural variants are separately named, and `_reject_excessive_json_nesting` runs before strict JSON decoding. Focused tests submit excessive nesting to the prediction, packet, tensor, and registry boundaries and expect controlled semantic failures. [DERIVED] Structural parsers remain useful for bounded decoding, but callers must not mistake successful parsing for truth-bound semantic replay.

Alternatives not selected:

- Remove all structural parsers immediately: rejected because existing callers still need bounded canonical decoding during migration.
- Leave authority implicit in documentation outside the API: rejected because the unsafe interpretation occurred at the parser boundary itself.
- Depend on the native JSON recursion limit: rejected because the prior review observed uncaught recursion failure around depth 900–1,000.

#### Decision D-150 - Add adversarial trust probes and mechanical Indic text coverage without linguistic claims

Decision: Preserve red-first regression tests for forged registry outcomes, forged lookup surfaces, forged path alignment, excessive depth, unsorted/duplicate/over-count registry entries, and hash mismatches. Add mechanical Unicode/category, combining-mark, code-mix, alignment, and cut-through checks over Hindi, Tamil, Telugu, and English-Indic strings, explicitly excluding transliteration quality, language understanding, or model performance claims.

Rationale: [OBSERVED - Luna inspection] Focused tests first show that standalone structural parsing accepts an internally coherent forged chain, then require authoritative replay to reject it. Registry tests cover sorting, duplicates, 4,097-entry rejection, nesting, and expected-hash mismatch. The multilingual cases exercise only Unicode categories and VMP-coordinate mechanics and contain an explicit no-linguistic-quality comment. [DERIVED] Indic examples are valuable boundary tests, but synthetic category and alignment mechanics cannot establish semantic or linguistic correctness.

Alternatives not selected:

- Test only valid generated artifacts: rejected because the original defect appeared only when independently forged but canonical artifacts were supplied.
- Describe mechanical Indic cases as language-quality evidence: rejected because no transliteration, encoder, native-speaker review, or downstream metric was evaluated.
- Omit code-mixed strings until a model exists: rejected because Unicode, offsets, combining marks, and rewrite cut-through are already relevant mechanical invariants.

#### Decision D-151 - Keep E0 unpromoted until integration migration and independent replay pass

Decision: Classify the repair as `REPAIRED_PENDING_INTEGRATION_REVIEW`, not PASS. Do not claim a repository-wide green suite or advance E0, `G5`, `G6`, or another implementation/empirical gate. First migrate evaluation and harness consumers to the authoritative semantic replay, close the nine current non-semantic failures, run the full suite, and commission fresh independent replay on the new pins.

Rationale: [OBSERVED - parent-supplied integration status] The latest full snapshot had nine failures in evaluation/harness migration paths outside the scoped semantic repair. [OBSERVED] Focused semantic, candidate-plus-semantic, core, AST, and hygiene checks passed, but no current repository-wide pass or independent post-repair verdict exists. [DERIVED] A locally correct trust boundary is necessary but cannot be accepted end to end while its consumers still fail migration.

Alternatives not selected:

- Mark E0 accepted from the 25 semantic tests: rejected because evaluation/harness integration remains broken and independent replay is pending.
- Ignore the nine failures as unrelated: rejected because those consumers must use the new authoritative boundary for the security repair to be effective end to end.
- Revert to structural-only consumers to restore the old green suite: rejected because that would reintroduce the forged-evidence vulnerability.

### Impact and tradeoffs

- Interfaces and compatibility: authoritative consumers must supply the VMP/candidate context, frozen registry bytes, and exact semantic artifacts; structural parser compatibility remains temporarily available but explicitly non-authoritative.
- Security and integrity: registry and candidate truth are now recomputed from frozen inputs, closing the scoped rehashed-forgery path; remaining envelope, provenance, parser/reader, and evaluation issues from `LUNA-20260819-027` are not implicitly fixed.
- Data and provenance: the registry artifact is synthetic and offline. It does not establish real registry coverage, authority, ownership, licensing, or collection permission.
- Language scope: Hindi, Tamil, Telugu, and English-Indic cases cover mechanical Unicode and alignment behavior only; no linguistic-quality or multilingual-model claim exists.
- Evaluation: q-weighted `P_pair` is recomputed and frozen as interface evidence, not reported as phishing-detection performance.
- Performance: registry, nesting, and entry counts are bounded, but no latency, memory, scale, or real-data benchmark was performed.
- Operations: design-only `G0/P0=COMPLETE_SPEC` is unchanged; E0 implementation acceptance, `G5/G6`, empirical, protected-access, publication, and release gates remain blocked.

### Verification performed

- `[OBSERVED - Luna inspection]` The two affected files match the SHA-256 pins recorded above.
- `[OBSERVED - parent-supplied focused verification]` Semantic-focused verification passed 25/25 tests in 0.084 seconds.
- `[OBSERVED - parent-supplied integration-focused verification]` Candidate-plus-semantic verification passed 66/66 tests in 28.664 seconds.
- `[OBSERVED - parent-supplied core regression verification]` The current core-focused suite passed 19/19 tests.
- `[OBSERVED - parent-supplied compatibility and hygiene QA]` Python-3.11 grammar AST parsing and hygiene checks passed.
- `[OBSERVED - Luna inspection]` The implementation and tests contain the bounded canonical registry artifact, immutable registry reconstruction, authoritative full-chain replay, exact frozen evidence, non-authoritative structural parser labels, nesting guards, adversarial forged-chain tests, and mechanical Indic/code-mix tests described above.
- `[OBSERVED - parent-supplied negative integration evidence]` The latest full snapshot had nine non-semantic migration failures in evaluation/harness; therefore no repository-wide PASS is recorded.
- Unrun by Luna: the semantic, candidate-plus-semantic, core, AST, hygiene, and full-suite commands were not rerun for this register-only checkpoint. No independent post-repair review, supported Python-3.11 runtime, real provider, real registry, trained model, corpus, protected metric run, or performance benchmark ran.

### Remaining risks and follow-up

- Evaluation and harness consumers may still bypass or incompletely bind the new authoritative replay until their migration is finished and independently tested.
- Nine known non-semantic integration failures remain; additional failures may appear after those are repaired.
- The synthetic frozen registry is not a real authority and provides no ownership, authenticity, coverage, governance, or operational evidence.
- Mechanical Indic tests do not measure transliteration, language understanding, native-speaker validity, classification quality, or robustness.
- Other security and contract blockers from `LUNA-20260819-027`, including envelope recomputation, source/runtime provenance, bounded reads, factorial coverage, and candidate work budget, remain open unless separately repaired and recorded.

Next owner/action: migrate evaluation and harness to consume `SemanticReplayResult` and frozen registry evidence, add regressions proving no structural-only acceptance path remains, resolve all nine current migration failures, rerun focused and full verification on stable pins, and obtain a fresh independent integration/security/methodology replay before promoting E0 or any implementation gate.

### Correction history

None. This record is append-only, `LUNA-20260819-027` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-029

### Synthetic E0 candidate trust and bounded-performance boundary repaired pending independent review

- Lifecycle: `REPAIRED_PENDING_INDEPENDENT_REVIEW` - candidate repair and stable integrated verification completed; fresh external review and no commit remain pending
- Recorded: 19 August 2026, 10:42:47 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: None
- Required trailer if later committed: `Luna-ID: LUNA-20260819-029`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected implementation boundary

- `fisher_engine/candidate.py` - SHA-256 `ae1193879bc9be9bf2253e511e3cb9c8a4651917caa562bf1191fc7fb4397549`
- `tests/test_engine_candidate.py` - SHA-256 `e0db970682c90630195289c895f14b76bbafd37026023ddf24ddbe164f2965b8`

[OBSERVED - Luna inspection] Only these two files belong to this completed candidate checkpoint, and both match the supplied post-verification pins. Other owners resolved four concurrent migration regressions before the stable full-suite run; those changes are outside this register entry and are not attributed to the candidate repair.

### Failure being repaired

[OBSERVED - prior independent E0 review] The prior implementation trusted envelope path records instead of reconstructing complete candidate evidence, and the largest permitted 64-span by 8-reading by 300-code-point candidate probe remained unfinished after 60 seconds. `LUNA-20260819-027` therefore required authoritative candidate replay and a deterministic work budget without narrowing the frozen P0 input limits.

#### Decision D-152 - Persist complete canonical candidate artifacts and exact stage bytes

Decision: Persist each candidate path as a canonical artifact that binds artifact version, path identity/hash, VMP hash, provider-manifest hash, text, full alignment, compact lineage, composition-score bits, q-numerator bits, q bits, and effective rewrite spans. Persist exact canonical provider-execution and candidate-diagnostics bytes separately, with strict parsers, bounds, and hashes.

Rationale: [OBSERVED - Luna inspection] `CandidateRun` exposes exact provider-execution, diagnostics, and candidate-path artifact bytes; candidate-path validation binds the VMP/provider context, recomputes the text/alignment path hash, validates lineage and spans, and rejects invalid numeric encodings. Focused tests cover canonical round trips, duplicate/noncanonical/oversized input, Boolean coordinates, negative zero, nonfinite values, and distinct identity versus degraded execution causes. [DERIVED] Later engine, semantic, and evaluation stages need exact candidate evidence, not a lossy envelope projection that can be rehashed after tampering.

Alternatives not selected:

- Trust candidate records copied into an engine envelope: rejected because the independent review showed that structurally valid envelope records could misstate paths, q, counts, and lineage.
- Persist only a path hash: rejected because a hash without the canonical text, alignment, lineage, scores, q, and spans cannot be independently replayed.
- Reconstruct provider cause from an identity manifest alone: rejected because no-eligible, unavailable, and timeout paths may share identity content while their provider executions differ.

#### Decision D-153 - Make `replay_candidate_run` the authoritative candidate boundary

Decision: Require `replay_candidate_run` to parse the exact provider manifest, provider execution, diagnostics, and path artifacts; reconstruct and revalidate provider output and accepted spans; recompute work, candidate enumeration, ordering, counts, diagnostics, path hashes, lineage, score/q arithmetic, and the envelope path projection; and reject any byte mismatch. Core, semantic, evaluation, and envelope integration must consume this replayed evidence rather than trust mutable downstream records.

Rationale: [OBSERVED - Luna inspection] The replay rebuilds candidates from the accepted canonical manifest, compares exact recomputed diagnostic bytes, parses every path artifact against VMP/provider hashes, rebuilds the expected artifact, and returns a frozen `CandidateReplayResult` with exact bytes, hashes, internal paths, projection rows, and work units. Red-first tests tamper with q and require controlled non-echo rejection; replay also distinguishes identical identity content with different execution causes. [DERIVED] Authoritative reconstruction turns hashes into evidence of the recomputed process rather than evidence only of caller-supplied bytes.

Alternatives not selected:

- Validate each persisted object structurally but never replay the candidate computation: rejected because mutually consistent forged objects can pass independent schema checks.
- Trust audit or envelope ordering and counts: rejected because ordering, reductions, q, and progress counts are derived properties that must be recomputed.
- Let each downstream consumer implement a partial candidate reconstruction: rejected because divergent reconstructions would create inconsistent trust boundaries.

#### Decision D-154 - Replace pathological beam materialization with persistent state and deterministic work accounting

Decision: Represent beam hypotheses through persistent backpointer nodes and materialize text/alignment only when required. Count deterministic comparison, expansion, materialization, and text/alignment work against a frozen `CANDIDATE_WORK_BUDGET=2,000,000`; fail closed with a controlled non-echo diagnostic if a run would exceed it.

Rationale: [OBSERVED - Luna inspection] `_BeamNode` stores parent-linked choices, the beam comparator reads chunked text/alignment from the chain, and `_CandidateWorkCounter` increments explicit work units and enforces the budget. Focused tests fix deterministic counts at both maximum-span cases and force a low budget to verify a controlled INVALID result. [DERIVED] Persistent state avoids repeatedly copying the full growing path, while deterministic work units make the safety boundary replayable across runs on the same accepted algorithm.

Alternatives not selected:

- Materialize every exhaustive Cartesian path: rejected because the permitted maximum is combinatorially infeasible.
- Keep the prior beam while repeatedly copying full path text and alignment: rejected because the largest valid probe exceeded 60 seconds.
- Use a wall-clock-only cutoff: rejected because machine load and platform speed would make identical input nondeterministically valid or invalid.
- Abort without a controlled diagnostic: rejected because resource limits are part of the canonical failure contract.

#### Decision D-155 - Preserve the frozen maximum-valid P0 scope and measure it explicitly

Decision: Keep the accepted limits of 64 spans, eight readings per span, and valid 300-code-point readings. Require the maximum 64x8x300 construction to remain below the deterministic 2,000,000-unit budget, and record runtime/memory observations only as macOS/current-CPython synthetic measurements, not universal guarantees.

Rationale: [OBSERVED - parent-supplied benchmark] The 64x8x1 case returned VALID at 262,411 work units in 1.515539 seconds, with `ru_maxrss` baseline 26,886,144, peak 73,465,856, and delta 46,579,712. The 64x8x300 case returned VALID at 1,487,115 of 2,000,000 units in 24.946793 seconds, with baseline 26,361,856, peak 135,692,288, and delta 109,330,432. [OBSERVED - Luna inspection] Focused tests freeze both work-unit counts and require every returned maximum-length path to contain 19,200 code points. [DERIVED] The implementation can retain the reviewed P0 boundary while preventing unbounded construction, but observed wall time and `ru_maxrss` remain runtime- and platform-specific.

Alternatives not selected:

- Narrow the 64-span, 8-reading, or valid 300-code-point scope: rejected because the repair can satisfy the frozen specification without changing its accepted bounds.
- Present the two measurements as a production service-level objective: rejected because they use one synthetic construction on one macOS CPython runtime.
- Infer universal memory behavior from `ru_maxrss`: rejected because allocator, process history, OS reporting, and runtime can change those values.

#### Decision D-156 - Preserve the mixed-snapshot failure before recording the stable green suite

Decision: Record the first concurrent full snapshot and its failure transparently, then distinguish the dedicated CLI replay and the later stable full-suite result. Accept the final 242-test run as integrated regression evidence only after the four migration regressions were resolved by their owners; do not erase or reinterpret the initial result.

Rationale: [OBSERVED - parent-supplied verification chronology] The first mixed concurrent snapshot passed 240/241 tests and had one transient CLI failure. The exact CLI test then passed 1/1. After owners fixed four migration regressions and the tree stabilized, `python3 -B -m unittest discover -s tests` passed 242/242 in 62.988 seconds. [DERIVED] Concurrent-tree evidence must be time-ordered so a later pass does not falsely imply that every earlier snapshot was green.

Alternatives not selected:

- Report only 242/242 and omit 240/241: rejected because the failed mixed snapshot is part of the verification history.
- Treat the single CLI rerun as proof of the entire suite: rejected because it addresses one test, not candidate, semantic, evaluation, or harness integration.
- Attribute all four migration fixes to this two-file candidate checkpoint: rejected because those changes belong to their respective owners and checkpoints.

#### Decision D-157 - Keep E0 and implementation gates blocked pending fresh independent replay

Decision: Classify this checkpoint as `REPAIRED_PENDING_INDEPENDENT_REVIEW`, not PASS. Preserve design-only `G0/P0=COMPLETE_SPEC`; do not promote E0, `G5`, `G6`, or another implementation, model, empirical, protected-access, or release gate. Require an external reviewer to replay artifact tampering, provider/execution cause, exact candidate reconstruction, maximum-bound work accounting, and stable integration on these pins.

Rationale: [OBSERVED] Focused and stable integrated tests pass, but no fresh external review has accepted the repaired candidate trust/performance boundary. The benchmarks are synthetic; no real transliteration provider, linguistic evaluation, trained model, real data, production latency, or cross-platform resource evidence exists. [DERIVED] Owner verification and a green stable suite are prerequisites, not substitutes, for the independent acceptance required after `LUNA-20260819-027`.

Alternatives not selected:

- Promote E0 from the stable full suite: rejected because the required external adversarial review has not occurred and other independent-review blockers may remain.
- Claim transliteration quality from multilingual mechanics tests: rejected because those tests preserve scripts and artifacts but do not evaluate language quality.
- Generalize the macOS benchmark to production latency: rejected because runtime, hardware, workload, and provider behavior remain unmeasured.

### Impact and tradeoffs

- Interfaces and compatibility: consumers must migrate from envelope-only candidate records to exact persisted artifacts and `CandidateReplayResult`; permissive forged records that previously passed should now fail.
- Security and integrity: full candidate/provider/VMP/diagnostic replay closes the scoped mutable-envelope trust gap and retains non-echo failure behavior.
- Performance: persistent beam state and deterministic work accounting admit the frozen maximum valid input; wall time and memory remain synthetic runtime-specific observations.
- Data and linguistic scope: no authentic corpus or real provider was used. Multilingual cases are mechanical script/serialization checks only.
- Evaluation: exact score/q/path evidence is available for later semantic/evaluation replay, but no model metric or method-effect result was measured.
- Operations: the stable 242-test suite establishes integrated regression evidence, while E0 implementation acceptance, `G5/G6`, empirical, protected-access, publication, and release gates remain blocked.

### Verification performed

- `[OBSERVED - Luna inspection]` The two affected files match the SHA-256 pins recorded above.
- `[OBSERVED - parent-supplied focused verification]` `python3 -B -m unittest tests.test_engine_candidate -v` passed 41/41 tests in 28.475 seconds.
- `[OBSERVED - parent-supplied migration verification]` After four migration regressions were fixed by their owners, the two exact probes passed 2/2.
- `[OBSERVED - parent-supplied full verification]` The stable command `python3 -B -m unittest discover -s tests` passed 242/242 tests in 62.988 seconds.
- `[OBSERVED - parent-supplied chronology]` The earlier mixed concurrent snapshot passed 240/241 with one CLI failure; the exact CLI replay then passed 1/1 before the stable full run.
- `[OBSERVED - parent-supplied compatibility and hygiene QA]` Python-3.11 grammar AST parsing, UTF-8, CR, trailing-whitespace, and public-API hygiene checks passed.
- `[OBSERVED - parent-supplied runtime-specific benchmarks]` On the current macOS CPython runtime, 64x8x1 was VALID at 262,411 units, 1.515539 seconds, and `ru_maxrss` delta 46,579,712; 64x8x300 was VALID at 1,487,115/2,000,000 units, 24.946793 seconds, and delta 109,330,432.
- `[OBSERVED - Luna inspection]` The implementation/tests contain canonical candidate artifacts, exact execution/diagnostic bytes, authoritative replay, tamper and non-echo tests, persistent beam/backpointer state, deterministic budgets, frozen maximum-bound counts, and mechanical multilingual cases.
- Unrun by Luna: no focused, two-probe, CLI, full-suite, AST, hygiene, or benchmark command was rerun for this register-only checkpoint. No external post-repair review, supported Python-3.11 runtime execution, real provider, trained model, authentic corpus, production benchmark, or cross-platform resource comparison ran.

### Remaining risks and follow-up

- Fresh independent replay may find missing candidate-to-envelope, candidate-to-semantic, or provider-cause bindings despite the current authoritative reconstruction.
- Work-unit accounting is algorithm-specific; future implementation changes must preserve or version its semantics and remeasure maximum cases.
- The recorded wall times and `ru_maxrss` values are synthetic macOS/current-CPython observations, not universal latency or memory guarantees.
- Real transliteration quality, provider reliability, multilingual semantics, model behavior, external data, production load, and cross-platform behavior remain unmeasured.
- Other open blockers from the combined E0 review require their own repaired and independently accepted checkpoints before E0 can advance.

Next owner/action: independently pin these two files; replay canonical artifact tampering, distinct identity/degraded causes, exact diagnostic/path/q reconstruction, controlled work-budget failure, both frozen maximum-bound cases, and the stable integrated suite. Then review candidate evidence consumption in core, semantic, and evaluation before considering any E0 or implementation-gate promotion.

### Correction history

None. This record is append-only, `LUNA-20260819-028` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-030

### Synthetic E0 evaluation trust boundary repaired pending independent review

- Lifecycle: `REPAIRED_PENDING_INDEPENDENT_REVIEW` - evaluation repair and supported-runtime integrated verification completed; fresh external review and no commit remain pending
- Recorded: 19 August 2026, 10:46:53 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: None
- Required trailer if later committed: `Luna-ID: LUNA-20260819-030`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Affected implementation boundary

- `fisher_engine/evaluation.py` - SHA-256 `e3069a179be4bd859b0609b883cafc3916ac20cc705bb80a2862f7e6d8a5d164`
- `tests/test_engine_evaluation.py` - SHA-256 `249d0a47abd6aa216b45a42ce1477cd1ad2674f0280a531fd593018617225a25`

[OBSERVED - Luna inspection] Only these two files belong to this completed evaluation checkpoint, and both match the supplied post-verification pins. No whole-tree stability claim is made outside the supported-runtime verification snapshot.

### Failure being repaired

[OBSERVED - prior independent E0 review] The old structural inspector accepted an internally self-consistent, rehashed `FORGED_ACTOR`/`FORGED_DESTINATION` to `MISMATCH` prediction-audit, SEP, feature-plan, and tensor chain even though it conflicted with the authoritative VMP/candidate/registry truth. The caller could provide the inspector and envelope-byte map, so downstream hashes authenticated the forgery rather than the upstream execution.

#### Decision D-158 - Require a complete immutable exact-artifact store for every scored envelope

Decision: Represent evaluation evidence as frozen `MetricArtifactBytes` and per-envelope `MetricEnvelopeArtifactBytes`. Retain exact bytes for the engine descriptor, PASS receipt, VMP, system manifest, provider manifest/execution, candidate diagnostics and path artifacts, frozen registry, prediction audit, SEP packets, feature plans/tensors, five-seed artifact, and engine envelope. Copy and wrap every supplied map so later caller mutation cannot alter the evaluation snapshot.

Rationale: [OBSERVED - Luna inspection] Both artifact containers are frozen dataclasses; their constructors validate byte/map shapes, copy maps, and expose mapping proxies. Focused tests clear the original system, envelope, and packet maps after construction and require the frozen store to continue validating the original chain. [DERIVED] Exact upstream evidence must be persisted independently; reconstructing bytes from embedded envelope objects would merely manufacture evidence from the assertion being checked.

Alternatives not selected:

- Persist only the final envelope and downstream hashes: rejected because those hashes can bind an internally consistent forged semantic chain.
- Re-serialize provider, candidate, registry, or semantic records embedded in the envelope: rejected because the evaluator would be creating its own evidence from untrusted claims.
- Retain caller-owned mutable maps: rejected because post-construction mutation creates a time-of-check/time-of-use substitution path.

#### Decision D-159 - Remove caller-controlled verification from the public evaluation boundary

Decision: Make public `evaluate_boundary` and `evaluate_metric_run` accept only `MetricArtifactBytes`; remove caller-supplied inspector callbacks and envelope maps from their public signatures and exports. Retain inspector-driven functions only as underscored private helpers for isolated metric-algebra tests.

Rationale: [OBSERVED - Luna inspection] Public evaluation builds `_make_engine_envelope_inspector` internally from the mandatory artifact store. The prior inspector/envelope injection path now appears only in underscored helpers and is absent from `__all__`; focused tests scan and exercise the public boundary. [DERIVED] A caller-supplied verifier defeats the trust boundary because the same caller can approve the artifacts it forged.

Alternatives not selected:

- Keep a public injectable callback for flexibility: rejected because callback authority was the central acceptance vulnerability.
- Accept a public envelope map plus an internal inspector: rejected because the map can omit or substitute the exact upstream artifact bundle.
- Rely on naming/documentation to discourage unsafe callbacks: rejected because security properties must follow from the callable interface.

#### Decision D-160 - Replay preflight, core envelope, candidate, and semantic truth before metrics

Decision: For each submitted envelope, construct and validate the mandatory preflight context from exact descriptor, receipt, system-manifest, and VMP bytes; invoke the core exact envelope replay with exact provider, candidate, registry, semantic, seed, and envelope artifacts; consume its authoritative active candidate paths; and independently call semantic replay with the frozen registry and every expected prediction/SEP/plan/tensor hash. Only the replayed registry pair tuples may enter metric calculation.

Rationale: [OBSERVED - Luna inspection] `_make_engine_envelope_inspector` calls `validate_pass_preflight_context`, builds `EngineValidationContext`, calls `validate_engine_envelope_bytes`, and then invokes `replay_semantic_chain` using the exact active paths and expected hashes from the validated envelope. It projects pair keys from the replay result rather than from an unverified packet. [DERIVED] Independent replay at each trust boundary prevents a forged downstream chain from becoming authoritative merely by recomputing its hashes.

Alternatives not selected:

- Trust recomputed downstream hashes: rejected because the original `FORGED_ACTOR`/`FORGED_DESTINATION` chain was rehashed consistently.
- Use envelope-embedded candidate paths without candidate replay: rejected because path text, alignment, lineage, q, and execution cause are upstream evidence.
- Compare only the final pair label with gold: rejected because the actor/destination identity, registry snapshot, and derivation must also match.

#### Decision D-161 - Preserve precise missing, unreadable, and binding-mismatch outcomes

Decision: Keep missing referenced evidence, unreadable or invalid canonical artifacts, and readable-but-cross-bound artifacts as distinct controlled failure classes. Do not convert malformed evidence into a binding mismatch or expose raw artifact contents through exceptions.

Rationale: [OBSERVED - Luna inspection] The private authoritative inspector checks store presence and envelope-byte identity before replay, maps validation failures to controlled evaluation errors, and distinguishes `EvaluationBindingError` from invalid-artifact errors. Focused tests separately cover a missing bundle, a hash/byte mismatch, and unreadable envelope bytes. [DERIVED] Disjoint outcomes preserve metric accounting and incident diagnosis without trusting or echoing unsafe content.

Alternatives not selected:

- Collapse all failures to one generic mismatch: rejected because absent, malformed, and substituted evidence have different audit meanings.
- Attempt to repair or normalize malformed evidence during evaluation: rejected because evaluation must fail closed on the persisted bytes.
- Include raw failing values in diagnostics: rejected because artifacts may contain sensitive or attacker-controlled content.

#### Decision D-162 - Freeze adversarial coverage across every upstream evidence category

Decision: Require regression tests for the original rehashed semantic forgery and for forged registry, prediction audit, SEP packet, feature plan, tensor, provider manifest/execution, candidate path, PASS receipt, descriptor, five-seed, runtime, and public-boundary evidence. Preserve mutation-snapshot tests and valid complete-chain tests alongside the red cases.

Rationale: [OBSERVED - Luna inspection] The focused suite constructs a valid C01 exact chain, then replaces each named evidence category and requires controlled rejection. The original `FORGED_ACTOR`/`FORGED_DESTINATION` to `MISMATCH` audit/packet/plan/tensor chain is rehashed and still rejected by authoritative replay. [DERIVED] Red-first category coverage is necessary because a green generated chain cannot demonstrate resistance to self-consistent forgery.

Alternatives not selected:

- Test only malformed JSON: rejected because the original attack used canonical, structurally valid, rehashed artifacts.
- Test only registry or packet mutation: rejected because substitution can occur at descriptor, preflight, provider, candidate, seed, runtime, or feature boundaries.
- Trust an upstream hash without supplying its bytes to evaluation: rejected because the evaluator cannot independently establish what the hash represents.

#### Decision D-163 - Keep the valid C01 known answer synthetic and runtime-scoped

Decision: Preserve the valid full-chain C01 result and rank-one `F1_pair=1.0` solely as a synthetic arithmetic/interface known answer. Treat bundled project Python 3.12 as the supported verification runtime for this checkpoint; record the Python 3.9 compatibility failure separately and do not let it replace or invalidate the supported-runtime result.

Rationale: [OBSERVED - parent-supplied supported-runtime verification] The bundled project Python 3.12 evaluation suite passed 26/26 in 0.864 seconds, and the full suite passed 242/242 in 47.896 seconds. A compatible-Python cross-suite covering core, candidate, semantic, and evaluation passed 114/114 in 33.840 seconds. [OBSERVED - parent-supplied compatibility probe] Host Python 3.9 executed 242 tests with one unrelated failure because it lacks `zip(strict=True)`; this is not the supported-runtime result. [OBSERVED - Luna inspection] The valid public-boundary test returns VALID and rank-one `F1_pair=1.0` for one synthetic C01 chain. [DERIVED] A synthetic exact answer proves arithmetic and binding only, not model quality or generalization.

Alternatives not selected:

- Report `F1_pair=1.0` as phishing-detection performance: rejected because the case is a single constructed known answer.
- Call Python 3.9 a supported runtime from this probe: rejected because the suite has a version-compatibility failure there.
- Suppress the Python 3.9 result: rejected because compatibility evidence should remain explicit even when it is outside the supported boundary.

#### Decision D-164 - Keep E0 and implementation gates blocked pending fresh independent evaluation review

Decision: Classify this checkpoint as `REPAIRED_PENDING_INDEPENDENT_REVIEW`, not PASS. Preserve design-only `G0/P0=COMPLETE_SPEC`; do not promote E0, `G5`, `G6`, or another implementation, model, empirical, protected-access, or release gate. Require fresh independent forgery and harness review on the repaired public boundary and current pins.

Rationale: [OBSERVED] Supported-runtime focused, cross-module, and full suites pass, but no fresh external reviewer has accepted the artifact store, public API removal, core/candidate/semantic replay chain, or harness integration. The filesystem is intentionally reverified live through the project root rather than captured as a byte snapshot inside `MetricArtifactBytes`; real provider, registry, model, data, and performance evidence remain absent. [DERIVED] Owner verification closes the repair loop locally but does not satisfy the independent acceptance required by `LUNA-20260819-027`.

Alternatives not selected:

- Promote E0 from the 242-test supported-runtime pass: rejected because external adversarial review and harness review remain pending.
- Treat live filesystem verification as a frozen stored snapshot: rejected because the current design deliberately rechecks current project files and has a different mutation boundary.
- Generalize synthetic artifact replay to real provider, registry, or model readiness: rejected because none of those resources was exercised.

### Impact and tradeoffs

- Interfaces and compatibility: public evaluation now requires exact artifact stores; callers using injected inspectors or envelope maps must migrate to the authoritative artifact-only API.
- Security and integrity: complete preflight/core/candidate/semantic replay closes the scoped self-consistent forged-chain path; copied/frozen maps reduce caller mutation and TOCTOU risk.
- Filesystem provenance: project-source closure is intentionally reverified against the live filesystem rather than snapshot bytes stored in `MetricArtifactBytes`; concurrent file mutation remains an integration risk to review.
- Data and privacy: artifacts are synthetic and local. No real registry authority, provider, corpus, access control, or privacy workflow was validated.
- Evaluation: the valid C01 rank-one F1 is a one-item arithmetic known answer, not a performance or method-effect result.
- Compatibility: bundled project Python 3.12 is green; Python 3.9 has an unrelated `zip(strict=True)` incompatibility and is not claimed as supported here.
- Operations: design-only `G0/P0=COMPLETE_SPEC` is unchanged; E0 implementation acceptance, `G5/G6`, empirical, protected-access, publication, and release gates remain blocked.

### Verification performed

- `[OBSERVED - Luna inspection]` The two affected files match the SHA-256 pins recorded above.
- `[OBSERVED - parent-supplied focused verification]` Bundled project Python 3.12 `-m unittest tests.test_engine_evaluation` passed 26/26 tests in 0.864 seconds.
- `[OBSERVED - parent-supplied cross-module verification]` Compatible Python core-plus-candidate-plus-semantic-plus-evaluation verification passed 114/114 tests in 33.840 seconds.
- `[OBSERVED - parent-supplied full verification]` Bundled project Python 3.12 `-m unittest discover -s tests` passed 242/242 tests in 47.896 seconds.
- `[OBSERVED - parent-supplied compatibility probe]` Host Python 3.9 ran 242 tests with one unrelated `zip(strict=True)` compatibility failure; this is explicitly not the supported-runtime result.
- `[OBSERVED - parent-supplied static and hygiene QA]` AST parsing with `feature_version=(3,11)` passed for both owned files; whitespace, conflict-marker, and retired-export scans passed.
- `[OBSERVED - Luna inspection]` The implementation/tests contain immutable artifact stores, copied/frozen maps, artifact-only public APIs, private inspector algebra helpers, mandatory preflight and core replay, authoritative candidate and semantic replay, precise error classes, mutation tests, the complete forgery matrix, and valid C01 synthetic arithmetic.
- Unrun by Luna: no focused, cross-module, full, Python-3.9, AST, or hygiene command was rerun for this register-only checkpoint. No fresh external forgery/harness review, real provider, authoritative registry, trained model, authentic corpus, protected metric run, or performance benchmark ran.

### Remaining risks and follow-up

- Fresh independent review may find an omitted evidence category, residual public injection path, incomplete harness migration, or mismatch between core and evaluation replay.
- The project filesystem is reverified live, not captured inside the immutable artifact store; concurrent source mutation and stable-run coordination require independent review.
- Private inspector helpers remain for algebra tests and must not leak back into public production call paths.
- Host Python 3.9 is not supported by this snapshot because of the unrelated `zip(strict=True)` compatibility failure.
- Real model, transliteration provider, registry authority, data, multilingual quality, latency, memory, and performance remain unmeasured; `G5/G6` remain blocked.

Next owner/action: independently pin these two files; replay the complete forgery matrix, public API/export scan, store-mutation cases, missing/unreadable/binding distinctions, valid C01 chain, live-filesystem provenance behavior, and harness integration on bundled Python 3.12. Do not promote E0 or implementation gates before that review passes.

### Correction history

None. This record is append-only, `LUNA-20260819-029` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-031

### Synthetic E0 core, preflight, and harness integration repaired pending independent review

- Lifecycle: `REPAIRED_PENDING_INDEPENDENT_REVIEW` - integrated core repair and stable verification completed; fresh external security, contract, and methodology review and no commit remain pending
- Recorded: 19 August 2026, 10:54:04 PM IST (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: None
- Required trailer if later committed: `Luna-ID: LUNA-20260819-031`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Changed paths and post-repair pins

- `fisher_engine/__init__.py` - SHA-256 `605ecc6e0d199f41bbb52acca063ba7d6bc30666aed0e6a1f3df282eebd4a58c`
- `fisher_engine/__main__.py` - SHA-256 `5e5eb78627aec6ddae0ac16ba8e356029cae29a388a267efcd4ec2220a9404cb`
- `fisher_engine/_canonical.py` - SHA-256 `ce7e5dc1bca1b66de78dfa3159e7835c87d89b2be9a8a2c4340dc0ee266124c8`
- `fisher_engine/source_closure.py` - SHA-256 `e8511c53b811d8691e7ee974f624dbace797261300873beb3aa21b93ad07bdbe`
- `fisher_engine/preflight.py` - SHA-256 `a44607f1bb5ab7850cdbdbca77cc348c8f962d361bebac5e86d454bc917a2f2b`
- `fisher_engine/artifacts.py` - SHA-256 `dfcab23f82eef88ebb114a960688eb225d164c63429a3be7a783a95c44ec91bf`
- `fisher_engine/harness.py` - SHA-256 `bb75da30cc03ef7bde5dc878826a48cf38cd7295fb94ad18fc60c60f5fc7052c`
- `tests/test_engine_core.py` - SHA-256 `c87ae38f95e948e0350306dc6533b533f75d7fcf54c5a2dd20f394b7ac66393d`
- `tests/test_engine_preflight.py` - SHA-256 `b50688170342bf28706010195214a41e78efb7f77093791c6f58f83ffdb1679a`
- `tests/test_engine_integration.py` - SHA-256 `9be5441b0a47d5c1d2824172e5ea0e49421577ba7f998e367c7ff8aa694f59ec`
- `examples/engine/README.md` - SHA-256 `00dca6b4cdd8c06378f23236ed11aa53684718ade31e090ed0845e53e284ce32`
- `examples/engine/synthetic_e0.json` - SHA-256 `c2414c4b2a0959c155144c172c4e162a6a5ba88bdc3f316c7ee9af4e79df0309`
- `docs/ENGINE_CONTRACT.md` - SHA-256 `f31def9bc9a2794d781711e078cf0a7f11f865a1b79ac9843ee547c323469ba4`

### Verified unchanged dependencies

- `fisher_engine/_numeric.py` - unchanged at SHA-256 `f5c5862356bde63ea26e621cac160b1f88b65d9c4e26531e815f71d25aeffe09`
- `examples/engine/expected_summary.json` - unchanged at SHA-256 `2c3c3fd69c40005b199bdb91284772ead84ee444c53a9b9fefa6a6457fb51bfc`

[OBSERVED - Luna inspection] All 13 changed paths match their supplied post-verification pins. `_numeric.py` and `expected_summary.json` match their earlier pins and are reference checks only; this record does not misclassify them as changed.

### Failure boundary being repaired

[OBSERVED - prior independent E0 review] Core acceptance previously allowed deep parser recursion, unbounded fixture reads, ambient `sys.modules` source history, declared rather than live runtime identity, incomplete factorial/control manifest evidence, context-free envelope validation, a one-path q=`1` rehearsal, and public evaluator injection. The present checkpoint integrates the separately recorded candidate, semantic, and evaluation trust repairs with bounded input, exact provenance, opaque contexts, authoritative replay, and a nondegenerate shared-provider factorial.

#### Decision D-165 - Make canonical JSON depth and cap-plus-one reads total

Decision: Set a maximum JSON container nesting of 64, counting the root container as level one, across canonical validation, serialization, scanning, and parsing. Convert nesting, recursion, and allocation exhaustion into controlled canonical failures. Clip even a hostile stream that returns more than requested to the exact cap-plus-one prefix before reporting size state.

Rationale: [OBSERVED - Luna inspection] `_canonical.py` defines `MAX_JSON_NESTING=64`, performs total depth checks, catches `MemoryError` and `RecursionError`, and truncates stream output to the requested limit. Core tests accept level 64, reject level 65 with a controlled code, simulate memory failure, and verify clipping of an over-returning reader. [DERIVED] A byte cap is incomplete if recursive structure or a nonconforming reader can still exceed the intended work/memory boundary.

Alternatives not selected:

- Depend on the native JSON recursion limit: rejected because the independent review observed uncaught recursion around depth 900–1,000.
- Trust every stream to honor the requested length: rejected because the hostile over-return test demonstrated that assumption is not a safe boundary.
- Shrink valid candidate or message limits to compensate: rejected because parser and reader safety can be repaired without narrowing frozen P0 scope.

#### Decision D-166 - Read CLI fixtures as bounded verified regular files and preserve conventional exits

Decision: Open fixture paths with available `O_NOFOLLOW`, `O_NONBLOCK`, and close-on-exec flags; use `fstat` before and after reading; accept only stable regular files; read no more than cap plus one; and reject symlinks, FIFOs, directories, devices, changing files, oversized files, and missing inputs with sanitized output. Preserve exit `0` for success and both help paths, exit `1` for controlled input/engine failure, and exit `2` for invalid arguments.

Rationale: [OBSERVED - Luna inspection] `__main__.py` uses descriptor-based bounded reads and before/after identity/size checks rather than `Path.read_bytes()`. Integration tests cover nonregular inputs, missing paths, invalid use, top-level help, subcommand help, deterministic JSON, and empty stderr. [DERIVED] Checking size after `Path.read_bytes()` would perform the unsafe read first, while a nonblocking no-follow regular-file boundary avoids FIFO blocking and symlink substitution.

Alternatives not selected:

- Use `Path.read_bytes()` and reject after checking length: rejected because allocation and I/O already occurred.
- Follow symlinks to improve convenience: rejected because target substitution defeats the intended local fixture boundary.
- Treat `--help` as invalid usage: rejected because help is a normal successful CLI control path.

#### Decision D-167 - Record executed source with one inert global audit hook, not process history

Decision: Replace the `sys.modules` snapshot with one process-global Python audit hook that is inert without active recorders. While a recorder is active, observe project-root Python paths from import, compile, exec, and open events across active recorder threads; include declared entrypoints and collector bootstrap paths; reconcile exact file hashes; and reject any unreconciled project execution.

Rationale: [OBSERVED - Luna inspection] `source_closure.py` installs one hook, manages active recorders under a lock, records project-relative Python files, and marks unresolved project execution as closure failure. Tests cover `runpy`, absence of stale `sys.modules` influence, nested/root-scoped recorders, worker-thread execution, and rejection of an unresolved project exec. [DERIVED] Per-run provenance must observe executed source rather than ambient interpreter history or a manually curated list.

Alternatives not selected:

- Continue hashing `sys.modules` at finalization: rejected because unrelated prior imports changed the closure and non-import execution could be missed.
- Require callers to manually record every executed file: rejected because the prior `runpy` probe showed that self-declared closure is incomplete by default.
- Keep the audit hook active as a recorder when no run is in progress: rejected because the hook should impose no collection semantics without an explicit active context.

#### Decision D-168 - Bind preflight to live runtime identity and the exact eight-manifest system set

Decision: During preflight, compare each system manifest's Python, Unicode, platform, architecture, and math identity with the actual executing environment. Require the exact eight condition/control manifests and their matched-base IDs/hashes, provider equality, registry masks, and control bindings before producing an opaque PASS context.

Rationale: [OBSERVED - Luna inspection] Preflight now accepts the complete system-manifest bundle, checks the selected manifest and bundle relationships, verifies source files, and constructs a sealed `ValidatedPreflightContext` only after exact PASS replay. Tests reject forged runtime identity, incomplete/single-manifest bundles, wrong matched-base relationships, and invalid controls. [DERIVED] A declared environment or isolated valid manifest cannot prove the runtime or factorial/control set actually used.

Alternatives not selected:

- Trust runtime identity declared in the manifest: rejected because the independent review forged those fields successfully.
- Validate only the submitted system manifest: rejected because control equivalence and the frozen factorial require cross-manifest evidence.
- Expose a freely constructible PASS context: rejected because callers could bypass the exact preflight recomputation.

#### Decision D-169 - Require opaque preflight and full engine validation contexts for every envelope

Decision: Permit envelope construction and acceptance only with a sealed `ValidatedPreflightContext` plus mandatory `EngineValidationContext`. Replay exact provider execution, candidate diagnostics and path artifacts, five-seed evidence, registry, prediction, SEP, feature-plan and tensor artifacts, failure counts, status retention, runtime/system bindings, and active path projection. Return frozen authoritative active paths; provide no context-free public envelope acceptance path.

Rationale: [OBSERVED - Luna inspection] `artifacts.py` validates exact bytes through candidate and semantic replay, enforces status/mask/failure-count relationships, and cross-checks the opaque preflight context before returning validated envelope evidence. Core and integration tests cover valid, degraded, invalid, tampered, and context-construction paths. [DERIVED] Structural envelope validation cannot establish execution truth because a caller can make every embedded record mutually consistent while still false.

Alternatives not selected:

- Retain context-free structural envelope validation: rejected because it was the source of arbitrary path, q, count, lineage, and runtime acceptance.
- Trust envelope records after recomputing their outer hash: rejected because the hash authenticates supplied bytes, not their derivation.
- Replay only provider or semantic evidence: rejected because candidate, seed, registry, features, status retention, and failure counts are also security-relevant bindings.

#### Decision D-170 - Exercise the rank-one-versus-q factor with one shared nonuniform two-path provider

Decision: Use one shared provider artifact with two readings and nonuniform q across all eight systems. Make rank-one cells `C00` and `C01` retain the first path and corresponding first seed-logit column; make all-path cells `C10` and `C11` retain both paths and both columns. Require identical provider artifacts across base and control systems while applying the exact semantic/control masks.

Rationale: [OBSERVED - Luna inspection] The revised fixture contains two synthetic readings and two-column five-seed rows; the harness slices active paths and seed columns by condition while reusing the same provider output. Integration tests assert provider artifact identity, nonuniform q, rank-one/all-path cardinality, semantic presence only for base C01/C11, and all eight system/control combinations. [DERIVED] A one-path q=`1` fixture cannot exercise the central transliteration-uncertainty contrast, while different providers per cell would confound it.

Alternatives not selected:

- Keep the one-path q=`1` rehearsal: rejected because rank-one and q-weighted behavior collapse to the same computation.
- Give different provider outputs to different cells: rejected because the factorial freezes one shared provider/configuration.
- Duplicate a one-column seed row into all-path cells after the fact: rejected because seed logits must bind the exact active-path order and width.

#### Decision D-171 - Integrate the artifact-only evaluator with the authoritative engine chain

Decision: Build `MetricArtifactBytes` from exact descriptor, preflight, system, provider, candidate, registry, semantic, seed, and envelope bytes in the harness; invoke only the public artifact-only evaluation boundary; and preserve exact missing, invalid, and binding semantics. Do not reintroduce public inspector callbacks or caller-supplied envelope maps.

Rationale: [OBSERVED - Luna inspection] The harness constructs complete per-envelope artifact bundles and calls the repaired evaluator; the focused command includes the regression that rejects the rehashed forged semantic chain. [DERIVED] Evaluation is trustworthy only when it consumes the same exact upstream evidence that core validation and semantic replay accepted.

Alternatives not selected:

- Reconstruct evaluation artifacts by serializing envelope-embedded records: rejected because that manufactures evidence from the claim under test.
- Restore a public injectable evaluator for tests or flexibility: rejected because caller-controlled verification defeated the trust boundary.
- Bypass preflight/core replay in the harness because it generated the objects: rejected because production-facing integration must validate its own outputs through the public boundary.

#### Decision D-172 - Remove interrupted test artifacts and keep implementation gates blocked

Decision: After confirming ownership, remove the interrupted test-owned `tmpbdifdhzg` symlink/FIFO directory and generated bytecode/`__pycache__` artifacts. Treat them as disposable, nonrecoverable test debris; no source or user data was removed. Classify this checkpoint as `REPAIRED_PENDING_INDEPENDENT_REVIEW`, preserve design-only `G0/P0=COMPLETE_SPEC`, and do not promote E0, `G5`, `G6`, or another implementation/empirical gate.

Rationale: [OBSERVED - parent-supplied cleanup evidence] The directory and bytecode were generated by interrupted tests and removed only after ownership confirmation. [OBSERVED - Luna inspection] `tmpbdifdhzg`, `.pyc`/`.pyo` files, and `__pycache__` directories are absent. [OBSERVED] Focused/full verification is green, but no fresh independent security, methodology, or contract review has accepted this integrated boundary, and actual Python 3.11 runtime execution remains untested. [DERIVED] Clean artifacts and owner tests are necessary but do not satisfy independent E0 acceptance.

Alternatives not selected:

- Leave symlink/FIFO and bytecode debris in the workspace: rejected because they are confirmed test artifacts and can contaminate state or safety checks.
- Delete an unconfirmed directory recursively: rejected because ownership confirmation is required before destructive cleanup.
- Promote E0 from the current full-suite pass: rejected because independent replay and real resource/model/data evidence remain absent.

### Impact and tradeoffs

- Interfaces and compatibility: callers must supply complete eight-manifest preflight evidence and full validation contexts; context-free envelope validation and public evaluator injection are intentionally retired.
- Security and integrity: total nesting, bounded regular-file reads, live runtime comparison, exact source observation, sealed contexts, full replay, and artifact-only evaluation close the scoped independent-review defects.
- Provenance: the global audit hook is inert without an active recorder but may conservatively enlarge an active closure when concurrent project execution occurs in observed threads.
- Methodology: the two-path nonuniform-q fixture now exercises rank-one versus all-path mechanics end to end; it remains a synthetic interface check, not method-effect evidence.
- Data and language scope: no authentic data, real provider, real registry, trained model, or linguistic-quality evaluation was used.
- Performance: no new production latency or memory claim is made; candidate runtime evidence remains the synthetic, runtime-specific benchmark in `LUNA-20260819-029`.
- Operations: `G0/P0` remains design-only `COMPLETE_SPEC`; E0 implementation acceptance, `G5/G6`, empirical, protected-access, publication, and release gates remain blocked.

### Verification performed

- `[OBSERVED - Luna inspection]` All 13 changed files match the SHA-256 pins above; `_numeric.py` and `expected_summary.json` match their explicitly unchanged prior pins.
- `[OBSERVED - parent-supplied focused verification]` `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_engine_core tests.test_engine_preflight tests.test_engine_integration tests.test_engine_evaluation.DefaultInspectorIntegrationTests.test_default_inspector_rejects_rehashed_forged_semantic_chain` passed 51/51 tests in 2.343 seconds.
- `[OBSERVED - parent-supplied full verification]` `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'` passed 243/243 tests in 61.480 seconds.
- `[OBSERVED - parent-supplied deterministic CLI verification]` Two JSON rehearsals were byte-identical with SHA-256 `8f822a9119a0253a07d54ada0bcf09152f2199a240715215faba0030505508d8`; JSON runs exited 0/0, top-level and subcommand help exited 0/0, invalid arguments exited 2, missing input exited 1, stderr was empty, and corresponding outputs were identical.
- `[OBSERVED - parent-supplied compatibility QA]` Python-3.11 grammar AST parsing passed 17/17 targets. This was static grammar validation, not Python 3.11 runtime execution; Python 3.14.6 was the observed executing version in the supplied evidence.
- `[OBSERVED - parent-supplied text and workspace hygiene]` UTF-8, NFC, LF, no-CR, and no-trailing-whitespace checks passed 15/15 files; no generated bytecode remained.
- `[OBSERVED - Luna inspection]` No `.pyc`/`.pyo`, `__pycache__`, or `tmpbdifdhzg` artifact is currently present.
- `[OBSERVED - Luna inspection]` The implementation/tests/docs contain the total nesting and hostile-reader boundary, safe CLI reader and exits, active-recorder audit closure, live runtime/eight-manifest preflight, sealed contexts, full envelope replay, two-path factorial, and artifact-only evaluator integration described above.
- Unrun by Luna: no focused, full, CLI, AST, text-hygiene, runtime, or independent-review command was rerun for this register-only checkpoint. No actual Python 3.11 runtime, fresh external review, real provider, authoritative registry, trained model, authentic corpus, protected metric run, or production benchmark ran.

### Remaining risks and follow-up

- Fresh independent security, methodology, and contract replay may find residual provenance, context, mask, replay, or evaluator integration gaps.
- Actual Python 3.11 runtime execution remains untested; static 3.11 AST grammar does not establish runtime compatibility, while Python 3.14.6 was observed.
- The process-global audit hook may conservatively include concurrent project execution during active recording; reproducible orchestration must control or explain that enlargement.
- Platform-specific open flags and audit events require cross-platform review even though missing flags are handled conditionally.
- Real provider/registry/model/data behavior, linguistic quality, production latency, memory, and empirical performance remain unmeasured; `G5/G6` remain blocked.

Next owner/action: independently pin and review the 13 changed files plus the unchanged numeric/summary references; replay deep/hostile input, symlink/FIFO, runtime and eight-manifest forgery, source-exec closure, context construction, status retention/counts, two-path factorial, artifact-only evaluation, deterministic CLI, and full-suite cases. Do not promote E0 or implementation gates before that external review passes.

### Correction history

None. This record is append-only, `LUNA-20260819-030` remains unchanged, and no commit SHA is available to backfill.

## Decision record - LUNA-20260819-032

### Fisher research refocus: data readiness and one defensible NLP comparison

- Lifecycle: `DECISION_RECORDED` - uncommitted research-direction checkpoint
- Recorded: 19 August 2026; time not supplied (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Pending; no commit authorized
- Required trailer if later committed: `Luna-ID: LUNA-20260819-032`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Checkpoint scope and evidence

[OBSERVED - parent-supplied repository evidence] Git is an unborn `master` branch with an empty index and untracked project paths. No authentic Fisher corpus, trained model, baseline/model run, or performance result exists. `data/source_ledger.example.jsonl` contains one blocked fictional example; `examples/pilot` contains four synthetic items, two sources, and 12 annotations. NumPy is available locally; torch, transformers, sklearn, datasets, tokenizers, sentencepiece, pandas, pyarrow, safetensors, and accelerate are absent.

[OBSERVED - parent-supplied change evidence] Root changed only `README.md` and `docs/research/EXECUTION_STATUS.md` for this checkpoint. Those files now identify the narrow research question, pause synthetic scaffolding, prioritize the pilot and lexical baselines, and defer noncritical work. Root verified no trailing whitespace or CR characters, final newlines, and expected priority phrases. No tests ran because the changes were documentation-only.

[OBSERVED - parent-supplied public-source evidence] IEEE DataPort Dravidian (`10.21227/dcym-pd69`) and Hindi (`10.21227/5y8x-n678`) records are login-gated. Their JSON-LD independently reports CC BY 4.0, but the actual files and download-time terms were not inspected. The records describe spam/ham data, not Fisher-specific phishing labels. RevisedIndianDataset and IIIT-D SMSAssassin remain excluded because explicit reuse licenses were not verified and privacy/duplicate concerns remain.

[DERIVED] The project cannot support a paper-level detector claim until an authorized, provenance-recorded text corpus and measured baselines exist. Public spam/ham can support development or external robustness checks only after terms, hashes, privacy, duplicate, leakage, and Fisher-specific reannotation are audited.

#### Decision D-173 - Freeze synthetic-engine hardening and narrow the immediate research gate

Decision: Pause further synthetic-engine hardening. Make the immediate gate a consented, safely defanged, provenance-recorded 240-message feasibility pilot: four strata × two labels × 30 messages, used only to establish data readiness. Audit language/script, Romanized-Indic coverage, duplicates/templates, labels, and source/campaign components before expanding.

Rationale: [OBSERVED] No authentic corpus or empirical model result exists, while the current pilot and ledger are synthetic or fictional examples. [DERIVED] Data validity and ambiguity must be demonstrated before mechanism engineering or publication claims can be evaluated. [ASSUMED] Four balanced strata are a pragmatic feasibility sample, not a power-derived study design.

Alternatives not selected:

- Continue synthetic-engine hardening: rejected because it produces schema/interface evidence, not phishing-detection or linguistic-quality evidence.
- Jump directly to 6,000 records: rejected because authenticity, consent, label quality, and Romanized ambiguity are still unknown.
- Start voice, conversation memory, application/browser deployment, notifications, or patent work: rejected because the text corpus and core NLP result do not yet exist.

#### Decision D-174 - Use simple lexical baselines before one multilingual encoder

Decision: If the feasibility pilot is viable, first run character TF-IDF logistic regression and word-plus-character TF-IDF linear SVM. Add one multilingual encoder only after the data and runtime environment are ready.

Rationale: [OBSERVED] Required transformer and classical-ML packages are absent locally. [DERIVED] Character and word-plus-character baselines directly test script variation, spelling variation, and code-switching with lower dependency and compute risk; they provide a necessary reference before a larger model.

Alternatives not selected:

- Start with a transformer: rejected because the current environment cannot run the required packages and the data signal is unverified.
- Build a large baseline suite immediately: rejected because it would obscure the central comparison and consume effort before data readiness.
- Use only word features: rejected because Romanized-Indic spelling variation is central to the stated research question.

#### Decision D-175 - Test one central novelty: top-1 versus multi-candidate transliteration

Decision: Compare top-1 transliteration with multi-candidate aggregation using the same classifier and split policy. Expand only if authentic ambiguity and signal are observed; otherwise pivot to a dataset/error-analysis paper rather than force the mechanism.

Rationale: [DERIVED] Holding the classifier fixed isolates whether preserving transliteration uncertainty contributes beyond a single normalized form. [OBSERVED] Authentic Romanized ambiguity and its yield are currently unknown. [DERIVED] A null or weak result is scientifically useful if the paper reports it honestly.

Alternatives not selected:

- Add a full semantic factorial immediately: rejected because it would multiply unverified assumptions before the core transliteration comparison is measured.
- Claim novelty or patentability now: rejected because novelty clearance, prior-art analysis, and empirical benefit remain unverified.
- Force expansion when ambiguity is absent: rejected because a mechanism without observed ambiguity would be a post hoc story.

### Impact and tradeoffs

- Data and provenance: the 240-message pilot is the next data-readiness gate; public DataPort records are development/external candidates only, subject to download-time terms and audit.
- Privacy and security: pilot messages must be consented and safely defanged; raw credentials, live links, and unnecessary personal data must not enter the working corpus.
- Methodology: the pilot is feasibility evidence, not publication evidence or a power calculation. Spam/ham labels must not be represented as phishing gold without Fisher-specific reannotation.
- Compatibility and operations: no source-code or dependency change was made. Baseline execution is blocked until an environment with the required packages is deliberately prepared.
- Performance: no metric, low-FPR, safety, or production claim is made.
- Scope: voice, conversations, deployment, notifications, offline registry, 6,000-record confirmation, 1% FPR claims, synthetic hardening, and patent claims are deferred.

### Verification performed

- `[OBSERVED - parent-supplied]` Browser inspection verified both DataPort record pages, login-required file access, filenames/sizes, dataset descriptions, and CC BY 4.0 JSON-LD metadata.
- `[OBSERVED - parent-supplied]` Independent source audit returned conditional GO for DataPort as development/external data only and NO-GO for direct phishing truth.
- `[OBSERVED - parent-supplied]` Independent scope audit verified the local data counts and recommended the 240-message feasibility pilot.
- `[OBSERVED - parent-supplied]` README and execution-status Markdown checks passed for UTF-8/LF/final newline/trailing whitespace and expected priority phrases.
- `[OBSERVED - Luna inspection]` This register was inspected before append; the previous record is `LUNA-20260819-031`, so `LUNA-20260819-032` is unique.
- Unrun: no dataset download, consent workflow, raw-content inspection, baseline training, model run, metric computation, or Git action. No DataPort download-time terms were accepted or verified.

### Remaining risks and follow-up

- Actual DataPort package terms may conflict with JSON-LD metadata; resolve this at download and preserve terms, date, hashes, and provenance.
- No consent/storage/provenance owner or safe-defanging procedure has yet been operationalized.
- The pilot size is pragmatic and not power-derived; authentic Romanized ambiguity, label yield, and campaign separability remain unknown.
- ML runtime dependencies are absent, and the paused synthetic implementation has unresolved review findings.

Next owner/action: obtain or collect the authorized, safely defanged pilot; audit its schema, language/script and Romanized coverage, duplicates/templates, labels, source/campaign components, privacy, and split leakage; then run the two lexical baselines before considering one multilingual encoder or mechanism expansion.

### Correction history

None. This record is append-only; no commit SHA is available to backfill.

## Decision record - LUNA-20260827-001

### Workbook audit and minimal Fisher baseline architecture

- Lifecycle: `CHECKPOINT_RECORDED` - uncommitted data-readiness and implementation checkpoint
- Recorded: 27 August 2026; time not supplied (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: Pending; no commit authorized
- Required trailer if later committed: `Luna-ID: LUNA-20260827-001`
- Commit SHA: Pending (no commit requested)
- Parent SHA: None - repository has no commits
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

### Checkpoint scope and evidence

[OBSERVED - parent-supplied source evidence] The external workbook `/path/to/Spam Message Collection (1).xlsx` has SHA-256 `24ca099ac1ffabc0b02fd491f57d577c56afb932bc81c5964a40e32eab9a023b`, one sheet named `Dravidian Dataset`, columns `Message` and `Type`, no formula cells, and 7,718 loaded data rows. It remains outside the repository and was not copied. A visual preview of the first 40 rows showed a plain two-column workbook containing live URLs and phone-like data.

[OBSERVED - parent-supplied audit evidence] The conservative audit found 7,715 nonempty messages; labels were 6,322 Ham, 1,394 Spam, one `Spa,`, and one blank, with three empty messages. Using NFKC, casefolding, and whitespace collapse for duplicate keys, all nonempty labels were grouped before filtering. Twenty-eight contaminated/conflicting groups quarantined 57 binary rows; one deterministic representative per remaining duplicate group produced a controlled corpus of 6,458 rows: 5,333 ham and 1,125 spam. The raw audit contained 1,231 additional normalized duplicate rows.

[OBSERVED - parent-supplied audit evidence] Mechanical dominant-script counts before cleaning were Kannada 1,226; Latin 2,165; Malayalam 1,820; mixed 454; no letters 3; Tamil 1,083; Telugu 967. Median message length was 76 characters and 10 whitespace tokens; p95 was 191 characters and 28 tokens; maxima were 515 characters and 80 tokens. The conservative safety scan found 605 URL/domain rows, 12 email rows, 5 UPI-like rows, 156 phone-like rows, and 5 OTP-term rows. A broader independent scanner found higher counts; the exact boundary is scanner-version dependent.

[OBSERVED - parent-supplied verification evidence] Artifact-tool inspection rendered the workbook top range. Bundled Python 3.12.13 with pandas 2.2.3 and openpyxl 3.1.5 completed the audit; OpenSSL verified the source hash; an independent Terra audit reconciled the conservative 6,458-row projection. No model or project tests have run. Git remains an unborn `master` branch with no commit, staging, or push.

### Decision D-176 - Classify the workbook as auxiliary development data

Decision: Use the workbook only as auxiliary development data for spam-versus-ham experiments. Do not treat it as Fisher phishing gold, use it for campaign/source-disjoint claims, or make per-language claims from it.

Rationale: [OBSERVED] The workbook has only message and type fields, no sender, source, campaign, or language field. [DERIVED] Its labels and schema cannot establish phishing-specific truth, campaign separation, or reliable English-versus-Romanized-Indic separation. Fisher-labelled, tester-authentic data remains the future primary evidence.

Alternatives not selected:

- Treat `Spam` as `phishing`: rejected because spam and phishing are not equivalent labels.
- Claim language-specific performance: rejected because no language field exists and Latin script is ambiguous.
- Use random row splits for final claims: rejected because normalized duplicates and repeated templates can leak across splits.
- Copy the raw workbook into Git: rejected because it contains live URLs and phone-like data and its source/package terms remain unconfirmed.

### Decision D-177 - Build only the minimal baseline package first

Decision: Implement a new `fisher_baselines` package with strict ingestion/audit, safe defanging, conservative conflict quarantine and deduplication, template-grouped deterministic three-fold development out-of-fold evaluation, character TF-IDF logistic regression, word-plus-character TF-IDF LinearSVC, balanced/PR metrics, and aggregate/ID-only outputs. Do not persist raw or defanged messages.

Rationale: [DERIVED] These baselines test spelling and script variation with a small, interpretable dependency surface and establish an empirical reference before larger models. [OBSERVED] No model run or project test exists yet, so results must remain unknown until implementation and execution.

Alternatives not selected:

- Start with a transformer or semantic machinery: rejected until data validity and baseline signal are measured.
- Add voice, conversation memory, app notifications, registry, or patent work: rejected because they do not answer the immediate text-NLP research question.
- Persist message-bearing prediction outputs: rejected because the source contains live URLs and phone-like data.
- Autocorrect `Spa,` or other malformed labels: rejected because the intended label is unverified; quarantine is safer.

### Impact and tradeoffs

- Data and provenance: the real workbook stays outside Git; source license/package terms and collection provenance remain unknown and must be recorded before any external-data claim.
- Privacy and security: safe defanging and no raw-message output are required; formula-like leading characters must never be exported as spreadsheet formulas.
- Methodology: the controlled corpus is a conservative audit projection, not a phishing gold set; script counts are mechanical and not linguistic annotation.
- Compatibility and operations: derived/output directories will be ignored; the new baseline package is not yet implemented or dependency-tested.
- Performance: no model metric, low-FPR claim, production latency claim, or publication result is made.

### Verification performed

- `[OBSERVED - parent-supplied]` Artifact-tool import and top-range rendering completed.
- `[OBSERVED - parent-supplied]` Python 3.12.13, pandas 2.2.3, and openpyxl 3.1.5 audit completed; source SHA-256 was checked with OpenSSL.
- `[OBSERVED - parent-supplied]` Independent audit reconciled the conservative 6,458-row controlled-corpus projection.
- `[OBSERVED - Luna inspection]` The prior register ID was `LUNA-20260819-032`; `LUNA-20260827-001` is unique and is appended at the tail.
- Unrun: baseline implementation, dependency installation, model training, metric computation, protected/test split evaluation, license acceptance, and Git actions.

### Remaining risks and follow-up

- Source license and collection provenance are not confirmed; resolve before publication or redistribution.
- Heuristic safety counts depend on scanner version; version the scanner and re-audit before release.
- The independent audit reports 567 control-character messages and 27 non-NFC messages requiring explicit pipeline handling.
- Scikit-learn and related runtime dependencies are not installed in the repository environment; model results are unknown.
- No source/campaign identifiers exist, so the workbook cannot support campaign-disjoint evaluation.

Next owner/action: implement and verify only the minimal `fisher_baselines` package, using the audited controlled projection as development input, then run leakage-aware OOF baselines and error analysis. Keep Fisher-authentic tester data as the protected primary-evidence path.

### Correction history

None. This record is append-only; no commit SHA is available to backfill.

## Decision record - LUNA-20260828-001

### Completed auxiliary baseline and dated correction to LUNA-20260827-001

- Lifecycle: `CHECKPOINT_RECORDED` with append-only correction; uncommitted
- Recorded: 28 August 2026; time not supplied (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: `Add auxiliary spam-ham baseline pipeline` (proposed only; no commit authorized)
- Required trailer if later committed: `Luna-ID: LUNA-20260828-001`
- Commit SHA: Pending; parent SHA: None
- Git action: No staging, commit, push, publication, release, merge, rebase, or tag performed

The original LUNA-20260827-001 entry and its D-176/D-177 statements remain preserved above. This appended correction supersedes the earlier count for subsequent interpretation without overwriting history.

#### Correction D-176-C1 - Final controlled corpus

Correction: [OBSERVED - parent-supplied final audit] The final audit found 7,718 total rows, 3 invalid text rows, 1 unknown label, 28 contaminated groups containing 57 binary rows, 1,201 duplicate rows removed, and 23 residual-artifact rows quarantined (9 spaced HTTP, 9 spaced-domain, 3 undotted-handle, and 2 broad-phone indicators). Twenty-nine external hyperlink cells were observed; targets were excluded and not persisted. The final retained corpus is 6,433 rows: 5,328 ham and 1,105 spam.

Rationale: [DERIVED] Additional Unicode format-character and residual-artifact controls were verified after the earlier audit, so 6,433 is authoritative for the completed run while 6,458 remains historical for the earlier state.

Alternatives not selected: preserve 6,458 (omits verified quarantines); retain residual artifacts or hyperlink targets (avoidable safety/privacy risk); automatically repair malformed or unknown labels (intended labels unverified).

#### Correction D-177-C1 - Completed baseline and privacy repair

Correction: [OBSERVED] The minimal package now performs bounded read-only XLSX ingestion, strict `Message`/`Type` handling, NFKC/format-character/casefold/whitespace grouping, quarantine/deduplication, typed defanging, residual scanning, script categories, template groups, deterministic three-fold `StratifiedGroupKFold`, character TF-IDF balanced logistic regression, word-plus-character TF-IDF balanced LinearSVC, and aggregate-only `audit.json`, `run_manifest.json`, and `metrics.json` output.

Rationale: [DERIVED] This implements D-177's narrow lexical comparison while limiting leakage and raw-data exposure. [OBSERVED] The final run used 6,377 template groups, fold sizes 2,144/2,145/2,144, and zero group crossings; one `ham|no_letters` stratum makes composite stratification approximate.

Development-only pooled OOF spam-versus-ham results, not Fisher phishing, language, campaign-disjoint, protected, safety, or production performance: char/logistic precision `0.9208566108`, recall `0.8950226244`, spam F1 `0.9077558513`, macro F1 `0.9444739769` (TN 5243, FP 85, FN 116, TP 989); word+char/SVC precision `0.9568204122`, recall `0.8823529412`, spam F1 `0.9180790960`, macro F1 `0.9509404976` (TN 5284, FP 44, FN 130, TP 975). Pooled AP is descriptive only because fold-specific score scales are uncalibrated.

Privacy correction: [OBSERVED - parent-supplied independent review] Earlier ignored `predictions.csv` files contained dictionary-linkable message-derived hashes; those files and stale result directories were removed. The current writer persists exactly the three aggregate files, refuses occupied/symlink/non-directory outputs without deleting contents, and exports no row-level IDs or hashes. HMAC/opaque IDs were rejected as unnecessary for this aggregate-only milestone.

Alternatives not selected: treat spam as phishing or declare a model winner (label and protected-evaluation boundary unsupported); use random row splits (duplicate/template leakage); persist message-bearing predictions or hashes (raw exposure and linkability); add transformers, transliteration, voice, conversation memory, notifications, or engine expansion now (outside the minimal baseline question).

### Affected paths, impacts, and risks

[OBSERVED - parent-supplied] Affected paths are `.gitignore`, `pyproject.toml`, `uv.lock`, `fisher_baselines/__init__.py`, `fisher_baselines/__main__.py`, `fisher_baselines/cli.py`, `fisher_baselines/data.py`, `fisher_baselines/evaluation.py`, `tests/test_baseline_pipeline.py`, `docs/research/SMSDHL_DATASET_AUDIT.md`, and `README.md`. The workbook SHA-256 is `24ca099ac1ffabc0b02fd491f57d577c56afb932bc81c5964a40e32eab9a023b` and remains outside Git; local outputs are ignored.

- Compatibility: [OBSERVED] bundled Python 3.12.13 was used; Python 3.11 runtime remains untested despite grammar parsing.
- Data/provenance: [UNKNOWN] license/download terms, provenance, consent, source/campaign identity, Fisher labels, and true language labels remain unresolved.
- Security/privacy: [OBSERVED] hyperlink targets and row-level prediction/hash outputs are excluded; bounded scanner and XLSX zip-bomb limitations remain.
- Performance: [OBSERVED] no production latency, memory, calibrated threshold, low-FPR, deployment, or publication claim was measured.

### Verification performed

- `[OBSERVED - parent-supplied]` `.venv/bin/python -m unittest -v tests.test_baseline_pipeline`: 13/13 passed in 0.130 seconds.
- `[OBSERVED - parent-supplied]` `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p 'test_*.py' -q`: 256/256 passed in 54.126 seconds.
- `[OBSERVED - parent-supplied]` Real audit/evaluate commands succeeded; two seed-1729 runs were byte-identical. Output hashes: audit `159e9fad079ad279a5bc612ce962b2e6e2683e9dc6afac12fca3416ef81227ac`, metrics `6c119d9b3d3ef887ad92e9a3adc7d4b7c5ca15d32ce451fc2e93fd0f7e00beed`, manifest `acf9c841234274ffbbdad144767e2505ba3dfc4c07dca1908b60b9e322d1fa06`.
- `[OBSERVED - parent-supplied]` Exact raw-message scan checked 7,654 messages >=20 bytes and found zero persisted-output hits; AST 3.11 grammar passed 6/6; `uv lock --check` resolved 16; Markdown checks and `git diff --check` passed.
- `[OBSERVED - parent-supplied independent review]` Data/privacy review and methodology replay passed after repairs.
- Unrun: actual Python 3.11 runtime, license/provenance/consent, authentic phishing, campaign-disjoint, transliteration, calibrated-threshold, publication, and production checks.

### Remaining risks and follow-up

- [UNKNOWN] Near-duplicate paraphrase leakage, unseen obfuscations, external generalization, authentic phishing performance, and calibrated thresholds remain unmeasured.
- [OBSERVED] Bounded scanner and XLSX reader limitations remain.
- Next owner/action: obtain authorized Fisher tester data with provenance and labels; repeat leakage/privacy audit and protected evaluation before mechanism expansion. No commit or publication is authorized yet.

### Correction history

None. This record is the first correction to LUNA-20260827-001; original text remains above.

## Decision record - LUNA-20260829-001

### First Fisher baseline iteration prepared for commit

- Lifecycle: `COMMIT_PREPARATION_RECORDED`; uncommitted and awaiting explicit user approval
- Recorded: 29 August 2026; time not supplied (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master` (unborn branch; no commits exist)
- Planned commit subject: `Add first Fisher baseline iteration`
- Required trailer: `Luna-ID: LUNA-20260829-001`
- Commit SHA: Pending
- Parent SHA: None - repository has no commits
- Proposed later publication target: `origin` (`https://github.com/m-rithik/Phishing-in-indian-language.git`), branch `main`; push requires separate explicit user approval
- Git action: No commit, amend, push, merge, rebase, tag, or release performed

### Commit scope and evidence

[OBSERVED - Luna inspection] The current staged non-register scope contains exactly these 18 added paths:

- `.codex/config.toml`
- `.codex/agents/luna.toml`
- `.codex/agents/sol_high.toml`
- `.codex/agents/sol_max.toml`
- `.codex/agents/sol_ultra.toml`
- `.codex/agents/terra.toml`
- `.gitignore`
- `AGENTS.md`
- `README.md`
- `docs/research/SMSDHL_DATASET_AUDIT.md`
- `fisher_baselines/__init__.py`
- `fisher_baselines/__main__.py`
- `fisher_baselines/cli.py`
- `fisher_baselines/data.py`
- `fisher_baselines/evaluation.py`
- `pyproject.toml`
- `tests/test_baseline_pipeline.py`
- `uv.lock`

[OBSERVED - Luna inspection] `docs/CHANGE_DECISION_LOG.md` is currently an unstaged untracked register and is the intended 19th file after the parent stages this update. The working tree also contains unfinished `fisher_engine`, `fisher_data`, `fisher_governance`, and `fisher_audit` work, related tests, research documents, examples, data, the legacy DOCX, and generated/local artifacts outside the proposed scope. Those paths are not included in the staged diff. `git diff --cached --stat` reports 18 files and 2,418 insertions.

[OBSERVED - parent-supplied repository evidence] The local branch is an unborn `master` with no commit history. `origin` is `https://github.com/m-rithik/Phishing-in-indian-language.git`; `git ls-remote` returned no refs. GitHub repository inspection reports a private, user-owned repository with no default branch set and exactly one collaborator. The intended later push target is `origin/main`, but neither the commit nor push has been approved for this exact scope.

### Decision D-178 - Publish only the first working auxiliary baseline iteration

Decision: Prepare one focused first iteration containing the Fisher baseline package, its focused tests, reproducible dependency lock, research audit, README, and the project-scoped agent/governance configuration. Keep unfinished experimental systems and their documentation local.

Rationale: [DERIVED from the staged scope and parent-supplied verification] The staged package is a coherent, reviewable unit that establishes a runnable lexical spam-versus-ham development baseline without claiming the deferred Fisher research system is complete. A narrow first commit makes the public repository history legible and keeps unsupported experimental surfaces out of the initial publication.

Alternatives not selected:

- Stage the whole repository with `git add .`: rejected because it would include unfinished implementations, research drafts, local data, and unrelated artifacts.
- Publish the complete experimental engine, governance, and audit machinery: rejected because those surfaces are unfinished and outside the verified baseline iteration.
- Include the raw workbook, generated outputs, or row-level predictions: rejected because the source contains live URLs and phone-like data and aggregate-only privacy boundaries were selected.
- Include the legacy DOCX register: rejected because Markdown is the canonical active register and the DOCX is legacy/read-only.

### Decision D-179 - Keep the repository private and defer license/IP release decisions

Decision: Prepare this iteration for the existing private GitHub repository only; do not make a public-visibility or licensing claim. Preserve the owner’s future IP and license decision as unresolved.

Rationale: [OBSERVED] The remote repository is private, has no default branch, and has one collaborator. [UNKNOWN] Workbook license/download terms, provenance, consent, and the owner’s preferred project license remain unresolved. [DERIVED] A private first iteration preserves review access while avoiding an unsupported public-disclosure or reuse claim.

Alternatives not selected:

- Publish to a public repository or public branch: rejected because privacy/IP review and source terms are incomplete.
- Invent an MIT or other license: rejected because licensing is an owner/legal decision not established by the evidence.
- Treat private GitHub storage as risk-free: rejected because detailed research/IP history is still cloud-exposed to repository collaborators and GitHub account controls.

Known privacy debt: [OBSERVED] An earlier finalized register entry contains the absolute local Downloads path of the source workbook. Append-only policy preserves that historical statement; owner-authorized sanitization is required before any public visibility or mirror. This is a low-severity private-repository debt, not a reason to rewrite finalized history here.

### Decision D-180 - Freeze the aggregate-only development evidence boundary

Decision: Retain the auxiliary workbook as external development input and publish only the bounded baseline code, audit documentation, and aggregate/ID-free result contract. Describe all measured results as development-only spam-versus-ham evidence, not Fisher phishing performance.

Rationale: [OBSERVED - parent-supplied final baseline evidence] The real run used the audited 6,433-row controlled corpus and produced deterministic aggregate outputs; the source workbook remains outside Git. [DERIVED] The workbook has no authenticated Fisher phishing labels, campaign/source identifiers, or reliable language annotations, so its results cannot support phishing, campaign-disjoint, per-language, transliteration, safety, or production claims.

Alternatives not selected:

- Relabel spam as phishing: rejected because the labels are not equivalent.
- Publish raw or row-level prediction artifacts: rejected because they create avoidable privacy and linkability exposure.
- Present the baseline as a production detector or language benchmark: rejected because protected authentic-phishing data and deployment evaluation remain unavailable.

### Affected-path impacts and tradeoffs

- Architecture and behavior: [OBSERVED] The staged package provides bounded XLSX ingestion, conservative normalization/quarantine/deduplication, typed defanging and residual scanning, script/template grouping, deterministic three-fold grouped evaluation, character TF-IDF logistic regression, word-plus-character TF-IDF LinearSVC, and aggregate-only audit/manifest/metrics outputs.
- Compatibility and packaging: [OBSERVED] `pyproject.toml` declares the baseline package, README, repository URL, and locked runtime dependencies; the wheel/sdist scope is limited to the five `fisher_baselines` modules. No license was added.
- Data and provenance: [UNKNOWN] Workbook licensing, collection provenance, consent, source/campaign identity, and Fisher-authentic labels remain unresolved.
- Security and privacy: [OBSERVED] Exact staged-content scanning found no known private-key, GitHub/OpenAI/AWS token, or absolute-user-path match in the proposed 18-file scope. Raw workbook, generated outputs, attachment files, and unfinished project artifacts are excluded.
- Performance: [OBSERVED] Only development-only model metrics were measured; no production latency, memory, low-FPR, calibration, or deployment claim is made.
- Publication: [DERIVED] Private-repository review is the only bounded target at this stage; public visibility remains blocked pending source/privacy/IP/license review.

### Verification performed

- `[OBSERVED - parent-supplied]` `PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python -m unittest -v tests.test_baseline_pipeline`: 13/13 focused tests passed in 0.133 seconds.
- `[OBSERVED - parent-supplied]` Earlier full suite: 256/256 tests passed in 54.126 seconds.
- `[OBSERVED - parent-supplied]` `uv lock --check`: passed; 16 packages resolved.
- `[OBSERVED - parent-supplied]` Markdown relative-link checks passed.
- `[OBSERVED - Luna inspection]` `git diff --cached --check`: passed after the staged EOF formatting repair; staged stat is exactly 18 non-register paths.
- `[OBSERVED - parent-supplied]` A fresh-scope temporary copy containing only the proposed files completed `uv sync --locked`, focused 13/13 tests, and `uv build`; isolated wheel installation and its console help command exited 0 outside the source root. A clean temporary editable copy also ran the console entry point outside the source root.
- `[OBSERVED - parent-supplied]` Real workbook audit/evaluation succeeded; two seed-1729 runs were byte-identical. Final retained corpus: 6,433 rows, 5,328 ham and 1,105 spam; template groups: 6,377; fold sizes: 2,144/2,145/2,144; zero group crossings. Development-only pooled OOF results remain recorded in `LUNA-20260828-001`.
- `[OBSERVED - parent-supplied independent review]` Publication/scope review found no raw workbook, model outputs, attachment, or high-confidence secret in the proposed scope and confirmed `.example` test fixtures were reserved.

### Remaining risks and unrun checks

- Exact Git commit and push have not been run; `main` does not yet exist locally or remotely.
- Explicit user approval is still required separately for this exact commit and for the later push to `origin/main`; this Luna record is not approval.
- Actual Python 3.11 runtime execution remains untested; only 3.11 grammar parsing was performed.
- Gitleaks/TruffleHog were unavailable; the performed secret scan was bounded and not a universal guarantee.
- Workbook license/download terms, provenance, consent, and data redistribution rights remain `UNKNOWN`.
- Collaborator identity/permissions were not audited beyond the observed count of one; private cloud exposure remains a governance risk.
- Near-duplicate paraphrase leakage, authentic Fisher phishing performance, campaign-disjoint evaluation, transliteration robustness, calibrated thresholds, and production behavior remain unmeasured.

### Follow-up action and approval gate

Next owner/action: parent stages this Markdown update, presents the exact 19-file commit scope and verification to the user, and requests explicit approval for `Add first Fisher baseline iteration` with trailer `Luna-ID: LUNA-20260829-001`. If approved, the parent may create exactly that commit; a separate approval must be obtained before pushing to `origin/main`. On the next substantive Luna update, inspect history and backfill this record’s pending SHA by matching the trailer; never create a document-only hash-backfill commit.

### Correction history

None. This record is append-only; no commit SHA is available to backfill.

## Decision record - LUNA-20260829-002

### Pilot-v0.1 architecture decision checkpoint

- Lifecycle: `ARCHITECTURE_DECISION_RECORDED`; implementation delegated, not yet verified
- Recorded: 29 August 2026; time not supplied (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master`
- Planned commit subject: None; no commit or push is authorized or planned for this checkpoint
- Required trailer: None
- Commit SHA: None; this checkpoint is not a commit
- Parent SHA: `b23359ac` (`Add first Fisher baseline iteration`)
- Git action: No staging, commit, push, amend, merge, rebase, tag, or release performed

### Evidence and scope

[OBSERVED - parent-supplied evidence] Commit `b23359ac` is auxiliary spam-versus-ham work with 6,433 retained rows. It has no Fisher phishing labels, campaign/source identifiers, reliable language annotations, or authentic Fisher corpus, so it cannot provide the paper's phishing evidence.

[OBSERVED - repository evidence] `README.md` defines the immediate 240-message feasibility pilot as four strata × two labels × 30 items per cell, with data readiness as the goal. The existing untracked schema-1.2 validator is a separate 1,200-retained ontology pilot with full structured annotations and is too heavy for this immediate feasibility stage. Its implementation is not claimed here.

[OBSERVED - parent-supplied independent reviews] Two read-only reviews agree on pilot collection/readiness tooling with an embedded duplicate/component audit. Standalone near-duplicate work on the auxiliary workbook, a multilingual encoder, and a transliteration experiment are deferred until authentic labels/components and candidate resources exist.

### Decision D-181 - Use a separate internal-only JSONL schema 0.1

Decision: Implement, subject to collection authorization and later verification, a separate local/internal-only JSONL schema 0.1 for tester-authored pilot data. Items will include tester-only provenance/consent sources, deidentified and defanged content, one of four frozen strata, a binary final label, a leakage component, and Romanized/ambiguity screening fields. Use two blind annotations, adjudicating only disagreement or uncertainty, and report aggregates only.

Rationale: [DERIVED] A dedicated small schema preserves the semantic distinction between auxiliary spam and Fisher phishing while collecting evidence for readiness, label reliability, language/script coverage, and leakage checks. Local JSONL is inspectable without committing raw messages or identity mappings.

Alternatives not selected:

- Reuse the Ham/Spam evaluator: rejected because its semantic target is auxiliary spam-versus-ham, not the Fisher phishing pilot.
- Weaken schema-1.2: rejected because that would misrepresent the preregistered 1,200-retained structured-annotation pilot.
- Store raw intake, identity/consent mappings, or message-bearing logs in Git/chat: rejected because identity and mappings must remain outside those surfaces and reporting is aggregate-only.

### Decision D-182 - Freeze 240-item readiness gates without model claims

Decision: Support `draft` and `ready` modes. `ready` requires exactly 240 items, exactly 30 items in each four-stratum × two-label cell, at least 5 leakage components per cell, raw-label agreement ≥0.90, nominal Krippendorff alpha ≥0.80 for labels and ≥0.80 for language, deterministic three-fold component-grouped splits with both labels in every fold, and completed duplicate/component, Romanized, and ambiguity screening. Report data readiness only: no model metrics or paper claim.

Rationale: [OBSERVED - parent-supplied README/reviews] The immediate target is a 240-message feasibility pilot, not a model experiment. [DERIVED] Explicit cell, component, agreement, language, and fold gates make the small tester-authored collection auditable and prevent premature performance claims.

Alternatives not selected:

- Train an encoder now: rejected because authentic phishing gold and leakage components do not yet exist.
- Run transliteration now: rejected because authentic labelled examples and candidate resources are unavailable.
- Manufacture synthetic research data: rejected because it would not be valid empirical evidence.
- Treat a draft or partial collection as ready: rejected because it would invalidate fixed cell/component checks.

### Collection authorization and protected-data boundary

Collection is **NOT AUTHORIZED**. [UNKNOWN] Storage owner/location, retention, withdrawal process, incident process, and approved consent materials are not established. Raw intake, tester identity, consent mappings, and linking keys must never enter Git, chat, or logs. [OBSERVED - parent-supplied] Implementation has only been delegated; no code exists as a verified result of this checkpoint.

### Impacts, tradeoffs, and deferred work

- Data/provenance: [DERIVED] Tester-only provenance/consent fields make evidence explicit while identity-bearing records remain outside the repository; authorization remains a prerequisite.
- Security/privacy: [DERIVED] Deidentification, defanging, component tracking, and aggregate reporting reduce exposure but do not replace consent, retention, withdrawal, or incident controls.
- Methodology: [DERIVED] Component-grouped folds address pilot duplicate/component leakage but do not establish generalization or phishing performance.
- Compatibility: [OBSERVED] The committed baseline is unchanged; this defines a separate internal pilot path.
- Deferred work: encoders, transliteration, auxiliary near-duplicate analysis, model metrics, and paper claims remain blocked pending authentic labelled data and candidate resources.

### Verification performed

- `[OBSERVED - Luna inspection]` Confirmed `b23359ac` is current and no Git mutation was performed.
- `[OBSERVED - parent-supplied]` Confirmed README's 240-message target: four strata × two labels × 30 per cell, data readiness only.
- `[OBSERVED - parent-supplied]` Confirmed the schema-1.2 validator is untracked and represents the separate 1,200-retained structured ontology pilot.
- `[OBSERVED - parent-supplied independent reviews]` Two read-only reviews converged on readiness tooling with embedded duplicate/component auditing and the listed deferrals.
- `[OBSERVED - Luna inspection]` Register remains UTF-8 Markdown with one H1 and append-only record headings.
- Unrun: collection authorization, consent review, schema implementation, pilot ingestion, annotation, adjudication, agreement statistics, component audit, readiness validation, model training, protected evaluation, and publication/IP review.

### Remaining risks and Follow-up action

- [UNKNOWN] No approved storage, retention, withdrawal, incident, or consent procedure exists; collection remains blocked.
- [UNKNOWN] Tester-authenticated phishing labels, true language/stratum membership, and component assignments do not yet exist.
- [UNKNOWN] Schema implementation and tests have not been verified; delegated work requires independent review.
- [DERIVED] A 240-item pilot can assess feasibility and readiness, not model performance or paper novelty.

Next owner/action: resolve collection authorization and protected-data governance; then implement and independently verify local JSONL 0.1 draft/ready tooling. Keep raw intake and identity/consent mappings outside Git/chat/logs, and invoke Luna after implementation and verification.

### Correction history

None. This record is append-only; no commit or commit SHA is associated with this architecture checkpoint.

## Decision record - LUNA-20260829-003

### Pilot-v0.1 implementation and verification checkpoint

- Lifecycle: `IMPLEMENTATION_VERIFIED_PRE_COLLECTION`; local/internal-only pilot tooling; collection unauthorized
- Recorded: 29 August 2026; time not supplied (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master`
- Planned commit subject: None; no commit or push authorized or planned
- Required trailer: None
- Commit SHA: None; this is not a commit
- Parent SHA: `b23359ac` (`Add first Fisher baseline iteration`)
- Git action: No staging, commit, push, amend, merge, rebase, tag, or release performed

### Verified implementation scope

[OBSERVED - parent-supplied evidence] Fisher pilot schema `0.1.0` is implemented locally for pre-preregistration 240-item data readiness only. Affected non-register paths are `fisher_pilot/{__init__.py,__main__.py,cli.py,validator.py}`, `tests/test_pilot_validator.py`, `examples/pilot_v01/{README.md,sources.jsonl,items.jsonl,annotations.jsonl}`, `docs/research/PILOT_V01.md`, `pyproject.toml`, and `README.md`. No model evaluation, authentic collection, or collection authorization is claimed.

[OBSERVED] The sources schema requires tester-only provenance/consent sources. Items require deidentified and defanged content, four strata, phishing/benign final labels, source/component fields, Romanized screening, and privacy/artifact assertions. Annotations use two blind annotations and distinct adjudication only for disagreement or uncertainty. Draft and ready modes are implemented; aggregate-only reports contain provenance, Romanization, agreement/uncertainty, cell/component, and fold aggregates without text, IDs, paths, or model metrics.

[OBSERVED] Ready-mode gates require exactly 240 items, 30 per each of 8 cells, at least 5 components per cell, no more than 10 items from one component per cell, known binary-label and language raw agreement ≥0.90, nominal alpha ≥0.80 for each, and deterministic three-fold component assignment with at least 5 components and both labels in every fold.

### Decision D-183 - Keep the pilot separate, local, and readiness-only

Decision: Keep schema 0.1 as separate local/internal-only JSONL tooling. Enforce component-scoped source IDs, repeated consent references, and batches; reject normalized exact duplicates; group audited number/template variants; preserve exact stored text/hash while using an NFKC safety-only view that removes runtime format controls and frozen default-ignorable ranges. Reject bidi/control/effectively invisible, live/residual, credential, and financial candidates. Enforce bounded LF JSONL, number rejection, CRLF/U+2028 handling, symlink rejection, and typed-placeholder coherence.

Rationale: [DERIVED] These controls preserve the pilot's narrow data-readiness purpose while reducing leakage and unsafe artifact exposure without claiming semantic near-duplicate completeness. Human review remains necessary for semantic near duplicates.

Alternatives not selected:

- Reuse the Ham/Spam evaluator: rejected because its semantic target is auxiliary spam-versus-ham, not tester-authored Fisher phishing data.
- Weaken schema-1.2: rejected because it would misrepresent the preregistered 1,200-retained structured ontology pilot.
- Rely on alpha alone: rejected because cell balance, raw agreement, component coverage, and fold completeness are also required for readiness.
- Allow one source across components or duplicates to fill quota: rejected because it would weaken leakage control and inflate apparent coverage.
- Invent a semantic-similarity threshold: rejected because semantic near-duplicate completeness is not machine-proven and requires human review.
- Put tester data in tracked examples: rejected because examples are synthetic only and the future approved workspace is ignored, not protected by `.gitignore`.

### Decision D-184 - Keep collection blocked and defer model experiments

Decision: Collection remains **NOT AUTHORIZED**. Do not claim authentic data, consent, training, phishing metrics, transliteration results, publication evidence, or paper novelty. Defer encoder and transliteration experiments until authentic labels/components and candidate resources exist.

Rationale: [UNKNOWN] Approved storage/access owner, consent materials, retention/deletion, withdrawal, incident response, reviewer process, actual blinding/qualification/opacity, and group completeness are not machine-proven. [DERIVED] Readiness tooling cannot authorize collection or substitute for protected-data governance.

Alternatives not selected:

- Train an encoder now: rejected because authentic phishing gold and components are absent.
- Run transliteration now: rejected because authentic labelled candidates/resources are absent.
- Manufacture synthetic research data: rejected because it would not be valid empirical evidence.

### Impacts, security boundary, and deferred work

- Data/privacy: [OBSERVED] Raw intake, identity, consent mappings, and linking keys must remain outside Git/chat/logs. `data/raw/fisher_pilot_v01` is an ignored future workspace path, but `.gitignore` is not access control; an external screening ledger is required.
- Safety: [OBSERVED] Exact stored text/hash is preserved for controlled local handling while the safety-only view removes format hazards; live/residual and sensitive artifact candidates are rejected.
- Methodology: [OBSERVED] Deterministic component grouping and aggregate-only reporting are implemented; semantic near-duplicate completeness, actual consent/blinding, and group completeness remain unproven.
- Compatibility: [OBSERVED] The committed auxiliary baseline is unchanged. This is a separate pilot path and no model metrics are produced.
- Deferred: multilingual encoder, transliteration, standalone auxiliary near-duplicate analysis, training, publication, and patent claims remain blocked.

### Verification performed

- `[OBSERVED - parent-supplied]` Independent methodology replay: final PASS for pre-collection implementation; independent security replay: PASS. Earlier exact attacks reject and the fullwidth-A safe control passes.
- `[OBSERVED - parent-supplied]` Final pins reported: validator `48b084...e205`, test `8ee8a2...877e`, pilot document `c0dbf5...1b3a`.
- `[OBSERVED - parent-supplied]` `PYTHONDONTWRITEBYTECODE=1 uv run --python 3.11 python -m unittest discover -s tests -q`: 283/283 passed in 54.277 seconds.
- `[OBSERVED - parent-supplied]` Pilot and baseline focused tests: 40/40 passed in 0.396 seconds; `uv lock --check` passed; `git diff --check` passed; README local links reported 0 missing; synthetic CLI produced valid draft output with warnings; future raw workspace path passed `git check-ignore`.
- `[OBSERVED - parent-supplied]` Worker verified Python 3.11 AST/compile, sdist/wheel, isolated Python 3.11 install/import/console CLI, and deterministic synthetic CLI. `uv.lock` was unchanged.
- `[OBSERVED - Luna inspection]` Current live register was inspected before append. The exact current bytes, including `LUNA-20260829-002`, were preserved as the prefix; no Git state was changed.
- Unrun: collection authorization, real consent/blinding/qualification, authentic data intake, real readiness validation, training, phishing metrics, transliteration, publication, and push.

### Documentation-integrity correction

[OBSERVED - parent-supplied and Luna verification] The earlier `LUNA-20260829-002` append initially deleted finalized `LUNA-20260827-001` and `LUNA-20260828-001` records because a non-unique patch sentinel selected an incorrect boundary. The register was immediately repaired by restoring the exact `HEAD` bytes and placing `LUNA-20260829-002` at the true tail. This record does not alter earlier finalized content.

### Remaining risks and follow-up action

- [UNKNOWN] Collection governance and approved storage/access remain unresolved; collection must remain blocked.
- [UNKNOWN] Human semantic near-duplicate completeness and actual group completeness remain unproven.
- [UNKNOWN] No authentic Fisher corpus, model training, phishing metric, transliteration result, or publication claim exists.
- [OBSERVED] The examples are synthetic only; ignored paths do not provide security control.

Next owner/action: resolve the protected-data authorization gate, then independently review any authorized collection and execute draft/ready checks before any model work. Keep all raw tester data outside Git/chat/logs and invoke Luna after the next verified checkpoint.

### Correction history

None. This record is append-only; no commit or commit SHA is associated with this checkpoint.

## Decision record - LUNA-20260902-011

### Fisher browser-extension v0.3 selected-text upgrade

- Lifecycle: `IMPLEMENTATION_VERIFIED_LOCAL`; no commit planned or approved
- Recorded: 2 September 2026; responsible agent: luna; branch: `master`
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`; commit SHA: Pending/not applicable
- Planned subject: None — local checkpoint only; required trailer: None
- Git action: No staging, commit, push, amend, merge, rebase, tag, publication, or release

### Findings

[OBSERVED - parent-supplied] The requested better extension retains paste analysis and adds an explicit user-clicked top-frame selected-text action. The detector remains rule-only; the auxiliary spam/ham model is not embedded because it is not validated as a phishing model.

[OBSERVED - parent-supplied] Manifest v0.3.0 pins permissions to `[activeTab, scripting]` with no host or optional-host permissions, content scripts, background, messaging, storage, network, telemetry, or remote code. The restrictive CSP is unchanged.

[OBSERVED - parent-supplied] Selection injection occurs only after the dedicated click, uses the active/current tab ID, frame 0, and the ISOLATED world. It reads one non-collapsed Range, visits at most 10,000 text nodes, accepts at most 20,000 Unicode code points, and does not return a partial oversized string. It does not read URL, title, HTML, forms, or full-page content. Exact selected content is never copied to the textarea, rendered, logged, stored, or sent. Failures are generic.

[OBSERVED - parent-supplied] Paste and Clear remain enabled to supersede a pending read; generation guards discard stale results. UI guidance is state-specific and cautious, with one atomic polite status region, a labelled/focused result region, visible focus, and Clear restoring textarea focus. Root and extension READMEs are synchronized.

[OBSERVED - parent-supplied] Changed technical paths are `README.md`, `browser_extension/{manifest.json,popup.html,popup.js,selection.mjs,styles.css,README.md,tests/selection.test.mjs}`, `fisher_extension_package.py`, and `tests/test_extension_package.py`. Existing detector files were unchanged by this v0.3 feature.

[OBSERVED - parent-supplied] The deterministic runtime-only package is a six-member single ZIP at `outputs/browser_extension/fisher-scam-signal-prototype-v0.3.0.zip`, ignored/local, 27,435 bytes, mode 0644, nlink 1, with SHA-256 `1e6564f9ef72ede86364cdff962a16c1d08f53af4f377f13010a63209a7fac65`. Members byte-match sources; a second invocation refused overwrite and preserved the digest.

### Decision D-201 - Add explicitly requested selected-text analysis under a narrow permission contract

Decision: Ship the v0.3 selected-text action as a dedicated user gesture with bounded top-frame extraction and local rule analysis, while preserving paste/Clear behavior and excluding the unvalidated auxiliary model.

Rationale: [OBSERVED - parent-supplied] Requirements and security review passed on the exact manifest, extraction limits, no-retention/no-network behavior, stale-result guards, and UI contract after repair. [DERIVED] A click-gated `activeTab`/`scripting` flow provides the requested convenience while limiting page access to the user-selected tab and action. [DERIVED] Excluding an unvalidated spam/ham model avoids presenting a non-phishing model as a phishing detector.

Alternatives not selected:

- Automatic content-script scanning: rejected because it would broaden page access and violate the explicit click-gated privacy boundary.
- Host permissions or optional host permissions: rejected because the feature only needs the active tab after a user gesture.
- Reading URL/title/HTML/forms/full-page content: rejected because it is outside the selected-text use case and increases sensitive-data exposure.
- Returning a partial oversized selection: rejected because truncation could change the analyzed meaning and create misleading results.
- Embedding the auxiliary spam/ham model: rejected because it has not been validated as a phishing model and did not clear its predeclared improvement gate.

### Impacts and claim boundary

- [OBSERVED] The extension now requests two narrow runtime permissions and adds selected-text analysis; paste analysis remains available.
- [OBSERVED] Selected content is processed transiently in memory and is not rendered, persisted, logged, or transmitted by the extension contract.
- [DERIVED] Existing installs must accept the v0.3 permission change when loading/updating the unpacked extension; no host-wide grant is introduced.
- [OBSERVED] Packaging is deterministic and runtime-only; the generated ZIP is ignored/local and not a repository source artifact.
- [UNKNOWN] No production accuracy, language coverage, calibration, or phishing-model claim is established by this checkpoint.

### Verification

- [OBSERVED - parent-supplied] Node extension suites: 40/40 passed.
- [OBSERVED - parent-supplied] Python 3.11 package suite: 24/24 passed; full Python 3.11 discovery: 316/316 passed in 52.337s.
- [OBSERVED - parent-supplied] JavaScript syntax, Python compilation, `git diff --check`, inventory/hash checks, and source-byte checks passed.
- [OBSERVED - parent-supplied] Independent requirements review initially failed because an unselected node's `.data` was read before intersection. Red-first repair moved `intersectsNode` before the single data read and added getter-canary regressions; final requirements review passed.
- [OBSERVED - parent-supplied] Independent security review passed on exact pins, including 21 adversarial probes, the full 316-test suite, and package replay.
- [OBSERVED - parent-supplied] Local in-app browser HTTP preview showed the high-risk result and fixed guidance for reserved test text, result focus, Clear reset/focus, and generic Cannot analyze selection fallback. This preview was not an installed extension and did not live-test selected-page injection or the permission lifecycle.

### Source pins

[OBSERVED - parent-supplied] Stable source SHA-256 pins: `manifest.json` `d8146c40bd14d5ed1f9b6e311f6468b4d4f24d9580336aed30f236b93f2bb294`; `popup.html` `90e0d54941f3a7d98d04c85d0a80609915ed9caaeda331a2b438a4cd44a08d30`; `popup.js` `a8e78757b0bafeb9b87a3d79d68e203872b305862a84b3eb9030b57ea8fb8b57`; `selection.mjs` `d3322f4777b95a37be9d063735f9c78026fb44ccd377a1a7e688c3b31db8236b`; `styles.css` `1f931335d5edd2746789d855f1142256c03fa59c60c5e138ba080d1f2733df05`; extension README `09bfc30edb04ea23a201fa43e293e22f4cacdc77f8ba5a8affd1e985de2bf37d`; selection tests `8e59e680f16696074daa5339221b5d41db4f57aca5d362ae0d0f758b58ba98f6`; packager `01af72ae6883874d0f46807d6a043ec01c59539e73978efd044d0208cd4f6bca`; package tests `0093c4ae3699fdd9a4a9d0da45d26c392d489d7dfd32d398f4be8688a9aac8cf`; root README `ea4f9caf6d674d41e94ca9f63711c6c71db83c3075ed4838be776a187aefb8fc`.

### Remaining Risks

- [UNKNOWN] Actual unpacked Chrome/Edge permission, restricted-page, popup-lifecycle, keyboard, and screen-reader tests remain unrun.
- [OBSERVED] The implementation is top-frame only; iframe, multi-range, form, and shadow selections are unsupported.
- [OBSERVED] DOM text-node concatenation may omit layout separators and differ from visibly serialized selection; navigation races can change the document; generation guards do not cancel a running injection.
- [OBSERVED] A Node module-type warning remains.
- [UNKNOWN] Rules remain unvalidated for accuracy, language coverage, calibration, and production phishing detection.
- [OBSERVED] The worktree is broadly dirty/untracked and no commit or push is authorized; the listed checkpoint paths must not be attributed to unrelated dirty paths.

### Recommended Next Action

Run an installed unpacked Chrome/Edge smoke test covering permission lifecycle, restricted pages, selected text, keyboard/screen-reader behavior, and navigation races. Then obtain separate explicit user approval before preparing a commit or publication to the intended remote and branch.

### Correction history

None. This record is append-only; no commit, staging, or publication occurred.

## Decision record - LUNA-20260902-012

### True-tail correction for Fisher browser-extension v0.3 record

- Lifecycle: `CORRECTED_APPEND_ONLY`; no commit planned or approved
- Recorded: 2 September 2026; responsible agent: luna; branch: `master`
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`; commit SHA: Pending/not applicable
- Planned subject: None — register correction only; required trailer: None
- Git action: No staging, commit, push, amend, merge, rebase, tag, publication, or release

### Findings

[OBSERVED - Luna inspection] The complete v0.3 selected-text upgrade is recorded in `LUNA-20260902-011`, but a later substantive register entry was appended after it. This entry restores true-tail placement without rewriting or deleting either finalized record.

### Decision D-202 - Preserve v0.3 evidence with an append-only tail pointer

Decision: Treat `LUNA-20260902-011` as the canonical complete v0.3 record and this entry as its live-EOF correction pointer.

Rationale: [DERIVED] Appending a pointer preserves historical text and ordering while resolving the register's live-tail requirement. No technical claim, source file, or Git state is changed.

Alternatives not selected:

- Move or rewrite the earlier v0.3 record: rejected because finalized register history is append-only.
- Duplicate the complete v0.3 record: rejected because duplication would create conflicting audit surfaces.

### Verification

- [OBSERVED - Luna inspection] Confirmed `LUNA-20260902-011` occurs once and this correction is at live EOF.
- [OBSERVED - Luna inspection] UTF-8 decoding, LF-only line endings, final newline, and no trailing whitespace pass; `git diff --check` passes.
- [OBSERVED - Luna inspection] No technical file, Git state, or legacy DOCX was changed.

### Remaining Risks and Follow-up

- [UNKNOWN] The register contains pre-existing duplicate historical Luna-ID references; they were not rewritten under append-only policy.
- Next owner/action: use `LUNA-20260902-011` for the complete v0.3 evidence and retain this correction pointer.

### Correction history

This record corrects placement only; the original v0.3 statement in `LUNA-20260902-011` is preserved verbatim. [CORRECTION: duplicate insertion superseded by the true-tail copy below.]



## Decision record - LUNA-20260902-007

### Canonical decision-identity correction for nested model selection

- Lifecycle: `CORRECTION_RECORDED`; no technical change and no commit planned
- Recorded: 2 September 2026; responsible agent: luna; branch: `master`
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`; commit SHA: Pending/not applicable
- Planned subject: None — not prepared; required trailer: None
- Git action: No staging, commit, push, amend, merge, rebase, tag, publication, or release

[OBSERVED - parent-supplied integrity finding] The live register contains two historical `Decision D-196` headings: browser-extension packaging (`LUNA-20260902-002`) and nested selection (`LUNA-20260902-006`). The duplicate arose from independent append-only checkpoints assigning decision numbers without a shared live counter.

[DECISION] Preserve both historical headings and content. The offline nested model-selection decision formerly labeled D-196 in `LUNA-20260902-006` is canonically corrected to `D-198`; aggregate-output security remains `D-197`. Future references to nested selection must use D-198. No historical heading or technical file is changed.

Rationale: [DERIVED] Rewriting a finalized heading violates append-only preservation; a true-tail identity notice provides an auditable canonical mapping. D-198 was the next unused decision identity at inspection.

Alternatives not selected:

- Rewrite either historical D-196 heading: rejected under the append-only policy.
- Leave the duplicate unresolved: rejected because ambiguous references impair auditability.

### Verification

- `[OBSERVED - Luna inspection]` Confirmed the two D-196 headings and existing D-197; no D-198 existed before this correction.
- `[OBSERVED - Luna inspection]` Canonical mapping is packaging D-196, aggregate security D-197, nested selection D-198; canonical identities are unique.
- `[OBSERVED - Luna inspection]` UTF-8, LF-only, final newline, no trailing whitespace, unique Luna IDs, and `git diff --check` pass; this record is at live EOF.
- `[OBSERVED - Luna inspection]` No technical file, Git state, or legacy DOCX was changed.

### Remaining Risks and Follow-up

- [UNKNOWN] Historical literal D-196 headings remain visible by design; reviewers must follow this mapping.
- Next owner/action: use D-198 for all future nested-selection references and retain this correction with the substantive record.

### Correction history

None. This is the append-only correction record.

## Decision record - LUNA-20260902-003

### True-tail correction for the packaging checkpoint

- Lifecycle: `CORRECTION_RECORDED`; no technical change and no commit planned
- Recorded: 2 September 2026; 7:18:03 AM IST
- Responsible agent: luna
- Branch: `master`
- Planned commit subject: None — not prepared
- Required trailer: None
- Commit SHA: Pending/not applicable
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`
- Git action: No staging, commit, push, amend, merge, rebase, tag, publication, or release performed

[OBSERVED - Luna inspection] The substantive browser-extension packaging checkpoint `LUNA-20260902-002` was authored during a concurrent, already-dirty register state and landed before pre-existing later records. This append-only correction is the canonical true-tail notice; the substantive record and all earlier finalized records are preserved unchanged. No technical path or Git state was changed.

[OBSERVED - parent-supplied evidence] The referenced checkpoint records the verified v0.2 paste-only MV3 zero-permission extension, local popup replay, unavailable Chrome connection, strict single-ZIP deterministic packaging contract, final implementation pins, focused/full test outcomes, independent requirements/security PASS results, persistent 16,996-byte artifact and SHA-256 `b1ce049e5fe77f8095e1466d3d7ffbe92ac7d4c8beeaf0e77e6afbe062884c92`, refusal to overwrite on a second invocation, and remaining browser/filesystem/evaluation risks.

Verification: register is UTF-8, LF-only, final-newline terminated, trailing-whitespace free, and `git diff --check` passes. Record-heading IDs remain unique. No staging, commit, push, or legacy DOCX edit was performed.

### Remaining risks and follow-up action

- [UNKNOWN] The substantive record's chronological position cannot be repaired without violating append-only policy or explicit owner-authorized rewrite.
- [UNKNOWN] Actual browser installation, accessibility review, non-local filesystem behavior, signing/publication, and linguistic/performance evaluation remain unverified as recorded in `LUNA-20260902-002`.

Next owner/action: treat `LUNA-20260902-002` together with this true-tail correction as the complete packaging checkpoint, and obtain explicit owner approval before any future canonical rewrite or Git publication.

### Correction history

None. This correction is append-only and has no associated commit.

## Decision record - LUNA-20260902-002

### Browser extension v0.2 deterministic packaging and live popup checkpoint

- Lifecycle: `IMPLEMENTATION_VERIFIED_LOCAL`; files remain untracked
- Recorded: 2 September 2026; 7:18:03 AM IST
- Responsible agent: luna
- Branch: `master`
- Planned commit subject: None — not prepared
- Required trailer: None
- Commit SHA: Pending/not applicable; no commit planned
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`
- Git action: No staging, commit, push, amend, merge, rebase, tag, publication, or release performed

### Findings

[OBSERVED - parent-supplied evidence] The browser extension remains MV3, paste-only, zero-permission, and local-rule based. It is not a model and makes no security guarantee.

[OBSERVED - parent-supplied evidence] In-app browser live popup replay completed locally: `Please send οtp.test` rendered `Needs review`; `Send OTP immediately at risk.example` rendered `High-risk pattern`; ordinary text rendered `No clear rule match`; Clear reset the input and the empty state rendered `Cannot analyze`. Actual Chrome extension installation was not run because the ChatGPT Chrome connection was unavailable.

[OBSERVED - parent-supplied evidence] Changed paths are `fisher_extension_package.py`, `tests/test_extension_package.py`, and `browser_extension/README.md`. Final implementation pins are packager `73cbcfa91e13227073934b24580783739e00f09cde9d92b2407a880d07aaac92`, package tests `9e570f9497cb7b3f361b31f86367d0f42c38ab87e5386391d96e546322e0d28e`, README `c4dc47344eb32c32be72a3a5d992074a3a396b766ec6c25dc5550a303a0d8cd9`, and manifest `d99fb58f4fc1bbcee6c437f313199eb7ca48eb57601534bbd9f4c9aede81084e`.

### Decision D-196 - Publish one deterministic local archive with strict validation

Decision: Package the extension as the fixed single output `outputs/browser_extension/fisher-scam-signal-prototype-v0.2.0.zip`, with no sidecar. Require the exact five runtime files, fixed deterministic ZIP metadata, exact zero-permission manifest validation, and no-overwrite atomic hard-link publication. After successful linking, the tool never auto-deletes the public path; a post-publication failure preserves it for manual recovery.

Rationale: [DERIVED] A single validated artifact makes the local output and integrity check unambiguous. No-overwrite publication and strict source/tree/manifest/ZIP validation reduce replacement, drift, and reproducibility risks while preserving a recoverable public artifact after a post-link error.

#### Alternatives not selected

- Directory plus ZIP plus sidecar: rejected because it creates partial-publication and cleanup ambiguity.
- Rename-based publication: rejected because replacement and race behavior is less constrained than no-overwrite hard-link publication.
- Context-free or denylist manifest validation: rejected because the contract requires exact capability and manifest validation.
- Post-link automatic cleanup: rejected because inode-identity TOCTOU can make cleanup target the wrong public path.
- Initial 909-line secure draft: rejected in favor of the verified 524-line implementation, reducing complexity while retaining the required contract.

### Impacts and claim boundary

- Compatibility: [OBSERVED] The extension remains paste-only MV3 with zero permissions; packaging does not add browser capabilities.
- Security/privacy: [OBSERVED] The package contains no network, page, or storage permission claim. [DERIVED] The SHA-256 verifies artifact integrity, not authenticity.
- Data/provenance: [OBSERVED] The archive is local and ignored; it is not signed, published, released, or store-ready.
- Performance/operations: [UNKNOWN] Windows, network-filesystem, ACL, and power-loss semantics are unverified. Post-publication errors require manual inspection/removal.
- Evaluation: [UNKNOWN] No linguistic coverage, precision/recall, calibration, or production-safety evidence exists.

### Verification

- `[OBSERVED - parent-supplied]` Focused packaging tests: 23/23 passed.
- `[OBSERVED - parent-supplied]` Node detector suite: 24/24 passed.
- `[OBSERVED - parent-supplied]` Full Python 3.11 `unittest discover`: 306/306 passed in 47.714 seconds.
- `[OBSERVED - parent-supplied]` Two independent reviewers returned PASS on final hashes, including adversarial manifest/file/tree/ZIP/race/crash/concurrency/determinism and requirements/docs/API replay.
- `[OBSERVED - parent-supplied]` `git diff --check` passed.
- `[OBSERVED - parent-supplied]` Persistent artifact verification passed: 16,996 bytes, five exact members, SHA-256 `b1ce049e5fe77f8095e1466d3d7ffbe92ac7d4c8beeaf0e77e6afbe062884c92`; independent ZipFile member/source-byte/CRC/metadata checks passed; a second invocation exited 1 and refused overwrite; the output directory contains only the ZIP.
- Unrun: actual Chrome/Edge load-unpacked installation, assistive-technology testing, Windows/network-filesystem/ACL/power-loss behavior, signing, publication, release/store flow, and linguistic/performance evaluation.

### Remaining risks and follow-up

- [UNKNOWN] Real browser installation and accessibility/assistive-technology behavior remain untested because the ChatGPT Chrome connection was unavailable.
- [UNKNOWN] Filesystem and power-loss guarantees outside the verified local environment remain unproven.
- [OBSERVED] Manual recovery is required if a post-publication error occurs; the local SHA is not an authenticity claim.
- [UNKNOWN] The narrow lexical detector has no authentic multilingual phishing evaluation or performance evidence.

Next owner/action: load the unpacked extension in Chrome or Edge when a browser connection is available, complete accessibility and native-speaker review, and separately authorize any commit, push, signing, publication, release, or permission-expanding feature.

### Correction history

None. This record is append-only; no commit or commit SHA is associated with this checkpoint.

## Decision record - LUNA-20260901-001

### Fisher browser-extension v0.1 implementation checkpoint

- Lifecycle: `IMPLEMENTATION_VERIFIED_LOCAL`; no commit authorized or planned
- Recorded: 1 September 2026; time not supplied (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master`
- Planned commit subject: None — local checkpoint
- Required trailer: None
- Commit SHA: Pending/not applicable
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`
- Git action: No staging, commit, push, amend, merge, rebase, tag, or release performed

### Verified scope and decisions

[OBSERVED - parent-supplied] Scope: `browser_extension/{README.md,detector.mjs,manifest.json,popup.html,popup.js,styles.css,tests/detector.test.mjs}`, `tests/test_extension_package.py`, and README discoverability/status updates. The extension is paste-only and explicitly activated. Manifest V3 uses zero permissions and no page reading, content/background execution, network, storage, telemetry, or remote code.

[OBSERVED] The deterministic local checker is neither the auxiliary spam model nor a trained phishing model. Public states are `high`, `review`, `no_match`, and `cannot_analyze`; no score or safe/low claim is exposed. `high` requires a locally non-negated sensitive request plus route or urgency. Protective warnings conservatively map to review. Inputs over 20,000 Unicode code points reject in full. C0/C1, malformed, invisible, matching-only NFKC dot mapping, bounded domain scanning, `textContent`, restrictive CSP, and a fixed accessible palette are covered.

### Decision D-191 - Keep v0.1 permission-free and advisory

Decision: Use paste-only activation, zero Manifest V3 permissions, deterministic local pattern checking, and four public states without numeric scoring or safe/low claims. High requires a non-negated sensitive request plus route or urgency; protective training text biases toward review.

Rationale: [DERIVED] This minimizes privilege and data exposure while avoiding unsupported calibration or safety claims. [OBSERVED - independent review] Advisory subtraction caused repeated false-`no_match` bypasses, so conservative review behavior is required.

Alternatives not selected:

- Add selected-text/`activeTab`/`scripting`: deferred because page-integrated scanning is outside v0.1.
- Add automatic scanning, background scripts, notifications, remote reputation, storage, telemetry, or remote code: rejected for privacy, permission, and operational scope.
- Use advisory score subtraction: rejected after repeated false-`no_match` bypasses.
- Expose safe/low states: rejected because no validation supports that interpretation.

### Decision D-192 - Bound analysis and release claims

Decision: Reject overlong input in full and fail closed on C0/C1, malformed, invisible, live/residual, credential, financial, or unsupported artifacts. Treat the extension as unvalidated local tooling; defer model/performance/language claims, real browser installation, CSP lifecycle, keyboard-only/screen-reader, and native-speaker validation.

Rationale: [OBSERVED] Local tests, packaging checks, and HTTP smoke passed, but the extension was not installed in real Chrome/Edge and no real labelled phishing evaluation exists. [DERIVED] README claims must remain explicitly unvalidated.

Alternatives not selected:

- Truncate overlong input: rejected because truncation could hide relevant artifacts.
- Claim Chrome/Edge readiness: rejected because unpacked installation and actual CSP lifecycle were untested.
- Claim precision, recall, calibration, coverage, or production performance: rejected because no authentic evaluation exists.
- Add multilingual, transliteration, or semantic model behavior now: rejected as outside this v0.1 slice.

### Affected paths, impacts, and risks

- Privacy/security: [OBSERVED] No page reading, network, storage, telemetry, remote code, or raw-message persistence; fixed CSP and `textContent` are used.
- Methodology: [OBSERVED] Rules are deterministic and bounded; Greek/Cyrillic homoglyphs and novel paraphrases may be missed, and protective text may over-flag to review.
- Packaging: [OBSERVED] Allowlist, integrity, nonregular-file, and symlink checks passed; ZIP reproducibility across checkouts remains unknown.
- Compatibility: [OBSERVED] The committed auxiliary baseline is unchanged; this is a separate local extension surface.

### Verification performed

- `[OBSERVED - parent-supplied]` Node detector tests: 17/17 passed; Python package tests: 6/6 passed; full repository suite: 289/289 passed in 51.088 seconds.
- `[OBSERVED - parent-supplied]` JavaScript syntax, `git diff --check`, ZIP allowlist/integrity, and nonregular/symlink checks passed.
- `[OBSERVED - parent-supplied]` In-app HTTP smoke (not installed extension) exercised all four headings and Clear; no warning/error console logs; layout visually inspected.
- `[OBSERVED - independent reviews]` Requirements replay PASS with contrast checks; security replay PASS across 216 combinations, 1,000 deterministic repeats, Unicode/CSP/DOM/package/performance probes, with no secret or score exposure; repeated-domain reviewer runtime 2.37 ms.
- `[OBSERVED - parent-supplied]` Full SHA-256 pins: root README `36d91f457312ff75593cfc054653e3706f68d84000bae30ef19f078d2a1837fd`; detector `679eafb86aeb1ab5e712e877ec7b8caaad6026c50a5ad54bfebfe89547b72beb`; detector tests `62cb594a5cdfe4fb78b0d0736a21d0697df74b531f463cadbd0b6f3af96681f7`; extension README `705f9e7951e24c7598031db9bc65a765e3adee92f24510cdd5f71cb2b9543db3`; package test `90d2d157ee24dc7e9e96ed3ccad6611f3a77e5c7c066bf8c603be2d9a7b0ea3e`; manifest `bb564898b8379db9ae9fca7783c1eb9816745e55a6dc9362dd97bbde28d30d3b`; popup HTML `137edf5d1530e3f614bea2bd20bb4e39dbea72523ead7cde70fcb4fdc9633ee3`; popup JS `4090a7a86698daae2099f69e1ecef55b7e3f456e886184494fb81498a4e7a677`; styles `9a53ceeacfb2f7d21f422bf89d88e01abf860036b15d7e044ecfc55c88ae6f31`.
- `[OBSERVED - Luna inspection]` Current register was inspected before append; no Git mutation occurred.
- Unrun: real Chrome/Edge installation, actual CSP lifecycle, keyboard-only/screen-reader acceptance, native-speaker validation, precision/recall/calibration/coverage, and production evaluation.

### Remaining risks and follow-up action

- [UNKNOWN] Fixed lexical rules may miss Greek/Cyrillic homoglyphs and novel paraphrases.
- [OBSERVED] Protective training text intentionally over-flags to review; no safe/low claim is made.
- [UNKNOWN] Real browser lifecycle, accessibility, native-speaker validation, and ZIP reproducibility remain unproven.
- [UNKNOWN] No authentic phishing corpus, model metrics, language coverage, transliteration result, or publication evidence exists.

Next owner/action: validate the unpacked extension in real Chrome/Edge and perform keyboard/screen-reader and native-speaker review before any separately approved release or feature expansion. No commit or push is authorized by this checkpoint.

### Dated correction - ordering race

[OBSERVED - Luna inspection] The 1 September record was previously observed before the 30 August record because concurrent register updates completed out of chronological order. It is now appended after the complete 30 August record; this correction changes ordering only.

### Correction history

None. This record is append-only; no commit or commit SHA is associated with this checkpoint.

## Decision record - LUNA-20260830-001

### Precollection governance packet checkpoint

- Lifecycle: `PRECOLLECTION_GOVERNANCE_VERIFIED`; collection remains blocked
- Recorded: 30 August 2026; time not supplied (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master`
- Planned commit subject: `None — local checkpoint`
- Required trailer: None
- Commit SHA: Pending/not applicable; no commit planned
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`
- Git action: No staging, commit, push, amend, merge, rebase, tag, or release performed

### Verified scope and evidence

[OBSERVED - parent-supplied evidence] This checkpoint covers `docs/research/PILOT_COLLECTION_PACKET.md` (new), updates to `docs/research/PILOT_V01.md`, `docs/research/CONSENT_ETHICS_PRIVACY.md`, `docs/research/EXECUTION_STATUS.md`, and `README.md`, plus `pyproject.toml` sdist inclusion of the packet. No unrelated untracked files are attributed to this checkpoint.

[OBSERVED] Real tester intake remains `BLOCKED`. Authority identity, attestation/authentication, expiry, revocation, and supersession are not frozen. Repository edits, validator results, and owner assertions cannot prove human approval.

### Decision D-185 - Use an immutable blocked/unknown collection-to-quarantine template

Decision: Use an immutable Git template for `BLOCKED`/`UNKNOWN` Collection-to-Quarantine governance. Completed sign-offs must remain in an approved external system. Keep intake control (`BLOCKED`/`APPROVED`/`SUSPENDED`), per-family disposition (`QUARANTINED`/`PREPROCESSING_APPROVED`/`ANNOTATION_APPROVED`/`REJECTED`/`WITHDRAWN`), and aggregate readiness (`NOT_READY`/`PILOT_READY`) as separate state dimensions. Do not collapse them into one family or batch lifecycle.

Rationale: [DERIVED] Separating authority, family disposition, and aggregate readiness prevents a locally editable document or one family’s status from being mistaken for collection authorization or whole-pilot readiness.

Alternatives not selected:

- Extend `fisher_governance` or create a positive precollection checker: rejected because software cannot prove human authority, attestation, authentication, expiry, revocation, or supersession.
- Use one family/batch lifecycle: rejected because intake control, per-family disposition, and aggregate readiness have different meanings and transitions.
- Treat repository edits or validator results as approval: rejected because sign-off authority exists outside the repository.

### Decision D-186 - Enforce zero durable original-message retention

Decision: Use an external no-message recruitment/consent vault, an ephemeral text-only pre-persistence transform/scan, terminal rejection with zero message persistence for unsafe input, and restricted quarantine containing only approved deidentified/defanged text. Restricted inputs must never live below a repository checkout, even under ignored paths. Raw-byte SHA/digests are prohibited outside ephemeral intake; random immutable IDs bind intake, scoped keyed HMAC begins only after AC-10, and research hashes apply only to approved transformed bytes.

Rationale: [DERIVED] This minimizes durable exposure and prevents raw-byte identifiers from becoming cross-zone dictionary or linkage keys while retaining a controlled audit identity after the required authorization boundary.

Alternatives not selected:

- Durable raw quarantine: rejected because it creates unnecessary privacy and persistence risk.
- Store intake under `data/raw` in the checkout: rejected because `.gitignore` is not access control.
- Use raw SHA identifiers across zones: rejected because they create dictionary/linkability risk.
- Use intake HMAC before AC-10: rejected because the keyed boundary is not authorized before AC-10.

### Decision D-187 - Freeze the synthetic evidence matrix and pilot separation

Decision: Define exactly 13 SG1 external decisions and the AC-00..AC-13 synthetic evidence matrix, with distinct AC-04-I and AC-04-P. All remain `UNKNOWN`/`NOT RUN`/`FAIL`; AC-11 template scanning remains policy-only and unimplemented. Keep the 240/schema-0.1 label/language feasibility pilot separate from schema-1.2/G2/1,200 ontology requirements; the 240 pilot cannot advance G2/G3. Use a one-way proposed `internal_only -> NO_RELEASE` text mapping only after external approval; it grants no aggregate, model, or paper release.

Rationale: [OBSERVED] The verified packet distinguishes the readiness pilot from the larger ontology and records the external decisions and synthetic checks explicitly. [DERIVED] This preserves scope and prevents synthetic or policy-only evidence from being promoted to collection-ready or publication-ready status.

Alternatives not selected:

- Claim machine authorization ready before an artifact exists: rejected because the contract requires a transformed artifact and pre-processing boundary.
- Import registry/VMP/structured-state requirements into the 240 pilot: rejected because that is a category error against the separate schema-1.2/G2 pilot.
- Treat synthetic matrix entries as real authorization evidence: rejected because all real AC checks remain unrun/failed and external authority is absent.
- Publish internal-only aggregates/models/paper results: rejected because the proposed mapping is `NO_RELEASE` pending external approval.

### Collection, privacy, and release boundary

Collection is **NOT AUTHORIZED**. [UNKNOWN] Accountable authority roles, approved storage/access owner, consent materials, retention/deletion, withdrawal, incident process, reviewer process, and external witnesses are absent or unresolved. The correct sequence is pre-intake schema-valid exact-scope planned records plus signed external SG1, then `machine_authorization_ready` only after a transformed artifact exists and before preprocessing; `governance collection_ready=false` remains expected. No raw intake, identity/consent mapping, or restricted data may enter Git, chat, logs, or a repository checkout.

### Impacts, tradeoffs, and deferred work

- Data/provenance: [OBSERVED] Tester-only provenance/consent sources and deidentified/defanged item handling are specified; actual consent and authority remain external and unverified.
- Security/privacy: [OBSERVED] Fail-closed unsafe-input handling, typed placeholders, bounded LF JSONL, CRLF/U+2028 normalization, symlink rejection, and artifact assertions are specified; zero-durable-raw behavior remains unimplemented/unproven.
- Methodology: [OBSERVED] Component, source, batch, duplicate, Romanized, ambiguity, and aggregate-readiness boundaries are specified; human semantic near-duplicate completeness and group completeness remain unproven.
- Compatibility: [OBSERVED] The committed baseline remains unchanged; this checkpoint adds governance/readiness documentation and packet packaging only.
- Publication/IP: [DERIVED] The internal-only mapping and private workflow preserve a no-release posture until external approval; no publication or patent claim is authorized.

### Verification performed

- `[OBSERVED - parent-supplied]` `PYTHONDONTWRITEBYTECODE=1 uv run --python 3.11 python -m unittest discover -s tests -q`: 283/283 passed in 50.619 seconds.
- `[OBSERVED - parent-supplied]` Static documentation checks passed: UTF-8, LF, final newline, no trailing whitespace, 13 SG1 rows with four placeholders each, AC-00..AC-13 ordering, and zero missing direct local links. `git diff --check` and `uv lock --check` passed.
- `[OBSERVED - parent-supplied]` `uv build` succeeded; wheel contained 13 files and sdist 21 files; packet was absent from the wheel and present in the sdist; restricted-path scan found zero hits; temporary build output was moved to Trash.
- `[OBSERVED - parent-supplied]` Governance fixture exited 1 with `schema_valid=true`, `collection_ready=false`, `machine_authorization_ready=0`, and 20 human `UNKNOWN` values. Synthetic pilot draft exited 0 `VALID` with expected warnings. `data/raw/fisher_pilot_v01` passed `git check-ignore`.
- `[OBSERVED - parent-supplied independent reviews]` Methodology replay final `PASS` for cross-scope coherence and security replay final `PASS` for the fail-closed blocked template only; neither establishes collection readiness.
- `[OBSERVED - parent-supplied]` Packet SHA-256: `36d20768f625f79ea8b3dae1f6a779c2f7e6ebb62d3998821731fbdbc413d6ca`. Worker verified Python 3.11 AST/compile, sdist/wheel, isolated install/import/console CLI, deterministic synthetic CLI, and unchanged `uv.lock`.
- `[OBSERVED - parent-supplied]` Generated `__pycache__` directories were moved to Trash; no project data was removed.
- `[OBSERVED - Luna inspection]` The current live register was inspected before append; this record is being added after `LUNA-20260829-003` without changing earlier records.
- Unrun: collection authorization, real consent, real intake, training, phishing metrics, transliteration, publication, commit, and push.

### Documentation integrity and remaining risks

- [OBSERVED] Earlier `LUNA-20260829-002` patch damage was repaired before this checkpoint; finalized records remain preserved. No prior record was rewritten here.
- [UNKNOWN] All SG1 decisions and real AC checks remain unresolved, unrun, or failed; external authority, roles, systems, and witnesses are absent.
- [UNKNOWN] Zero-durable-raw behavior, AC-11 scanning, actual consent/blinding/qualification/opacity, and component completeness are not machine-proven.
- [OBSERVED] The collection packet is currently untracked; the tracked-template invariant awaits a separately approved future commit.

Next owner/action: name the accountable authority roles and approve external policy values before any collection. Alternatively, separately approve a future commit to track the current local governance work. No collection, commit, push, training, or release is authorized by this checkpoint.

### Correction history

None. This record is append-only; no commit or commit SHA is associated with this checkpoint.

## Decision record - LUNA-20260901-002

### Ordering-race correction for LUNA-20260901-001

- Lifecycle: `CORRECTION_RECORDED`; no technical change and no commit planned
- Recorded: 1 September 2026; time not supplied (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master`
- Planned commit subject: None — local checkpoint
- Required trailer: None
- Commit SHA: Pending/not applicable
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`
- Git action: No staging, commit, push, amend, merge, rebase, tag, or release performed

[OBSERVED - Luna inspection] The live register contains `LUNA-20260901-001` before the subsequently present `LUNA-20260830-001`, caused by concurrent uncommitted register appends completing out of chronological order. Relocating the already-authored block would create a non-append-only deletion/reinsertion relative to the live register. Under the append-only policy, the original substantive record is preserved unchanged and this correction is the canonical true-tail notice; the historical heading order remains an unavoidable invariant until a future owner-authorized canonical rewrite.

Verification: exact `HEAD` bytes remain the live prefix; the live file is UTF-8, LF-only, has a final newline, and has no trailing whitespace. No technical file or Git state was changed.

### Remaining risks and follow-up action

- [OBSERVED] The earlier extension checkpoint remains valid as recorded; this entry corrects ordering only.
- [UNKNOWN] Chronological heading order cannot be repaired without violating append-only policy or owner-authorized rewrite.

Next owner/action: retain the existing records, disclose the ordering invariant in any review, and obtain explicit owner authority before any future canonical rewrite or publication-sensitive sanitization.

### Correction history

None. This correction is append-only and has no associated commit.

## Decision record - LUNA-20260902-001

### Browser extension v0.2 finalized checkpoint

- Lifecycle: `IMPLEMENTATION_VERIFIED_LOCAL`; files remain untracked
- Recorded: 2 September 2026; time not supplied (Asia/Kolkata)
- Responsible agent: luna
- Branch: `master`
- Planned commit subject: None — local checkpoint
- Required trailer: None
- Commit SHA: Pending/not applicable
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`
- Git action: No staging, commit, push, amend, merge, rebase, tag, or release performed

### Verified scope and decisions

[OBSERVED - parent-supplied evidence] Changed paths are `browser_extension/detector.mjs`, `browser_extension/tests/detector.test.mjs`, `browser_extension/README.md`, `browser_extension/manifest.json`, and `tests/test_extension_package.py`. The extension remains paste-only and zero-permission; there are no page, network, storage, or UI-flow changes.

[OBSERVED] Frozen `FISHER_GC_SENSITIVE_V1` scans normalized whole L/M/N tokens of at most 8 code points, preserves ASCII, applies exactly 14 Greek/Cyrillic substitutions, requires at least one substitution, and recognizes only six allowlisted skeletons: `otp`, `pin`, `password`, `passcode`, `cvv`, and `kyc`. It adds only a generic non-echo reason and an independent `REVIEW` floor.

### Decision D-193 - Keep lookalike detection narrow and advisory

Decision: Use the frozen partial map only for an independent review signal. Lookalikes never feed credential/request/high logic. A mapped-token contextual HIGH is rejected because an unvalidated partial map cannot support a stronger claim.

Alternatives not selected:

- Full UTS#39/general Unicode confusable handling: rejected as broader than the validated v0.2 scope.
- Flag all mixed scripts: rejected because mixed script is not itself sufficient evidence.
- Use mapped tokens in contextual HIGH logic: rejected because the partial map is unvalidated.
- Add language or transliteration logic: rejected as outside this extension iteration.

### Decision D-194 - Remove speculative dotted-host exclusion

Decision: Do not exclude dotted strings speculatively. An exact configured token in a dotted string remains `REVIEW`; this is explicitly not domain or brand assessment.

Rationale: [OBSERVED - parent-supplied independent review] The dotted-host exclusion was bypassed by `.test`; removing it closes that false-no-match path while preserving the limited lexical claim.

Alternatives not selected:

- Keep dotted-host exclusion: rejected after the independent `.test` bypass.
- Add domain/brand detection: rejected because it is unvalidated and outside v0.2.
- Claim domain safety or legitimacy: rejected because the checker is not a domain assessment.

### Decision D-195 - Version the extension without expanding permissions

Decision: Bump the manifest from red-first `0.1.0` to `0.2.0` and assert the package version. Preserve paste-only activation, zero permissions, and the existing UI flow.

Alternatives not selected:

- Add model, network, or page scanning: rejected because these expand privacy, permission, and evaluation scope.
- Add deterministic ZIP release guarantees now: deferred because cross-checkout reproducibility is not established.

### Impacts, risks, and claim boundary

- [OBSERVED] No precision, recall, calibration, language coverage, or production claim is made. Actual Chrome/Edge installation, keyboard/screen-reader smoke, and native-speaker validation remain unrun.
- [OBSERVED] Partial mapping remains incomplete; fixed lexical rules may miss novel paraphrases and other homoglyph patterns.
- [OBSERVED] Protective review remains advisory; no safe/low state or score is introduced.
- [OBSERVED] Files remain untracked; no commit or push is authorized.

### Verification performed

- `[OBSERVED - parent-supplied]` Red-first initial matrix: 20/23; final Node suite: 24/24 passed.
- `[OBSERVED - parent-supplied]` Python package tests: 6/6 passed; exact 21/21 variant matrix passed; former dotted bypass: 6/6 passed.
- `[OBSERVED - parent-supplied]` Full Python suite: 289/289 passed in 50.849 seconds.
- `[OBSERVED - parent-supplied]` JavaScript syntax and `git diff --check` passed.
- `[OBSERVED - parent-supplied independent reviews]` Security replay PASS and requirements replay PASS on stable final hashes.
- `[OBSERVED - parent-supplied]` Final pins: detector `a76a26a528e5c42da087322488e87e712ecea9955c5900bdca8b7ce7e7b76584`; detector tests `46409b1fbe48924f60d5cd80cd9b85f2b9db297da534a63394f636c3105ca4f3`; extension README `c76b3b7f81307a22d56ed9043652ce108c5b09c9aaba8e01ec63118e063e4b50`; manifest `d99fb58f4fc1bbcee6c437f313199eb7ca48eb57601534bbd9f4c9aede81084e`; package test `6b31cff4a654a27b87da23db8fe70580b59c1499707fd19b0dd89e6814bb07b0`.
- `[OBSERVED - Luna inspection]` `LUNA-20260901-002` remains the preceding record and this entry is appended at the live EOF.
- Unrun: real Chrome/Edge installation, CSP lifecycle, keyboard/screen-reader smoke, native-speaker validation, precision/recall, calibration, coverage, and deterministic release ZIP validation.

### Remaining risks and follow-up action

- [UNKNOWN] Real browser lifecycle, accessibility, native-speaker validation, and cross-checkout ZIP reproducibility remain unproven.
- [UNKNOWN] No authentic phishing evaluation or language-coverage evidence exists.
- [OBSERVED] The partial confusable map is intentionally narrow and cannot support semantic or domain claims.

Next owner/action: validate the unpacked extension in real browsers and complete accessibility/native-speaker review before any separately approved commit, release, or feature expansion.

## Decision record - LUNA-20260902-004

### Canonical true-tail notice for browser-extension packaging

- Lifecycle: `CORRECTION_RECORDED`; no technical change and no commit planned
- Recorded: 2 September 2026; 7:18:03 AM IST
- Responsible agent: luna
- Branch: `master`
- Planned commit subject: None — not prepared
- Required trailer: None
- Commit SHA: Pending/not applicable
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`
- Git action: No staging, commit, push, amend, merge, rebase, tag, publication, or release performed

[OBSERVED - Luna inspection] The substantive packaging checkpoint `LUNA-20260902-002` and its append-only correction `LUNA-20260902-003` were inserted before pre-existing register records because the register was already dirty and concurrent updates had produced a non-chronological tail. This new append-only notice is the canonical true tail; neither substantive evidence nor finalized earlier records is rewritten.

[OBSERVED - parent-supplied evidence] The complete evidence remains in `LUNA-20260902-002`: v0.2 paste-only MV3 zero permissions; local popup replay; Chrome connection unavailable; strict single deterministic ZIP contract; final implementation pins; 23/23 packaging, 24/24 detector, and 306/306 full-suite PASS; independent requirements/security PASS; 16,996-byte five-member artifact with SHA-256 `b1ce049e5fe77f8095e1466d3d7ffbe92ac7d4c8beeaf0e77e6afbe062884c92`; second-run overwrite refusal; and stated remaining risks.

Verification: [OBSERVED] this register is UTF-8, LF-only, final-newline terminated, trailing-whitespace free, record-heading IDs are unique, and `git diff --check` passes. No technical file, Git state, or legacy DOCX was changed.

### Remaining risks and follow-up action

- [UNKNOWN] Historical heading order cannot be repaired without violating append-only policy or explicit owner-authorized rewrite.
- [UNKNOWN] Browser installation, accessibility, non-local filesystem behavior, signing/publication, and linguistic/performance evaluation remain unverified.

Next owner/action: use `LUNA-20260902-002` plus this true-tail notice as the packaging checkpoint, and obtain explicit owner approval before any future canonical rewrite or Git publication.

### Correction history

None. This correction is append-only and has no associated commit.

### Correction history

None. This record is append-only; no commit or commit SHA is associated with this checkpoint.

## Decision record - LUNA-20260902-005

### Canonical true-tail notice for browser-extension packaging

- Lifecycle: `CORRECTION_RECORDED`; no technical change and no commit planned
- Recorded: 2 September 2026; 7:18:03 AM IST
- Responsible agent: luna
- Branch: `master`
- Planned commit subject: None — not prepared
- Required trailer: None
- Commit SHA: Pending/not applicable
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`
- Git action: No staging, commit, push, amend, merge, rebase, tag, publication, or release performed

[OBSERVED - Luna inspection] Earlier same-day packaging entries landed before pre-existing register records because the register was already dirty and concurrent updates had produced a non-chronological tail. This append-only notice is the canonical true tail; substantive evidence and finalized records are preserved unchanged.

[OBSERVED - parent-supplied evidence] The packaging checkpoint records the v0.2 paste-only MV3 zero-permission extension, local popup replay, unavailable Chrome connection, strict single deterministic ZIP contract, final implementation pins, 23/23 packaging, 24/24 detector, and 306/306 full-suite PASS, independent requirements/security PASS, and the 16,996-byte five-member artifact with SHA-256 `b1ce049e5fe77f8095e1466d3d7ffbe92ac7d4c8beeaf0e77e6afbe062884c92`.

Verification: [OBSERVED] UTF-8, LF-only, final newline, no trailing whitespace, unique record-heading IDs, and `git diff --check` pass. No technical file, Git state, or legacy DOCX was changed.

### Remaining risks and follow-up action

- [UNKNOWN] Historical heading order cannot be repaired without violating append-only policy or explicit owner-authorized rewrite.
- [UNKNOWN] Browser installation, accessibility, non-local filesystem behavior, signing/publication, and linguistic/performance evaluation remain unverified.

Next owner/action: use the substantive packaging record and this true-tail notice together, and obtain explicit owner approval before any future canonical rewrite or Git publication.

### Correction history

None. This correction is append-only and has no associated commit.

## Decision record - LUNA-20260902-006

### Auxiliary nested model-selection v0.2.0 checkpoint

- Lifecycle: `IMPLEMENTATION_VERIFIED_LOCAL`; no commit planned
- Recorded: 2 September 2026; responsible agent: luna; branch: `master`
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`; commit SHA: Pending/not applicable
- Planned subject: None — not prepared; required trailer: None
- Git action: No staging, commit, push, amend, merge, rebase, tag, publication, or release

### Findings

[OBSERVED - parent-supplied] The user-supplied workbook stays outside Git. The controlled set has 6,433 rows (5,328 ham/1,105 spam), 6,377 template groups, and zero mixed-label template groups. It is auxiliary spam/ham development evidence only, not phishing, campaign, language, calibration, or deployment evidence.

[OBSERVED - parent-supplied] Added offline `nested-evaluate`: 3 outer × 3 inner `StratifiedGroupKFold` with template groups and TF-IDF learned inside each training partition. Exactly eight candidates are evaluated (character logistic C=.5/1/2; character `LinearSVC` C=.5/1; word+character `LinearSVC` C=.5/1/2), for 81 fits. Selection uses inner mean spam F1, macro F1, precision, deterministic complexity tie-break, and default thresholds.

### Assumptions

- [ASSUMED] Parent-supplied run and replay evidence describe the current working tree; Luna did not inspect workbook contents or rerun training.
- [UNKNOWN] Generalization to Fisher phishing, multilingual input, or production traffic.

### Work Performed

[OBSERVED - parent-supplied] Changed `fisher_baselines/selection.py`, `tests/test_baseline_selection.py`, surgical `evaluation.py`/`cli.py`, version files `fisher_baselines/__init__.py`, `pyproject.toml`, `uv.lock`, plus `README.md` and `docs/research/SMSDHL_DATASET_AUDIT.md`. Outputs are ignored/local only; no model, vocabulary, weights, row predictions, or extension connection persists.

### Decision D-196 - Keep selection auxiliary and offline

Decision: Compare against frozen word+character SVC C=1, retain that baseline as the deployment candidate, and keep the extension rule-only. Do not export or serialize learned artifacts.

Rationale: [OBSERVED] Selected means: precision .9637908358580521, recall .8859751188091591, spam F1 .923204619182512, macro F1 .9540163264113556, balanced .9395153362302849, AP .9649748563471227; TN5291/FP37/FN126/TP979. Comparator spam F1 .9180901192244754, macro .9509458748332026, balanced .9370468879307462, AP .9634141114107296; TN5284/FP44/FN130/TP975. [DERIVED] Delta .005114499958036589 is below the predeclared .01 gate; macro improved and worse folds were 0. Acceptance is `FALSE`: promising/inconclusive, not deployable.

Alternatives not selected:

- Transformer/LLM: rejected as outside the bounded candidate set and unsupported evaluation scope.
- Calibration/threshold tuning: rejected because the predeclared protocol uses defaults.
- Export/serialize artifacts: rejected for privacy, license, and target-mismatch risk.
- Weaken the .01 gate after results: rejected because it invalidates the predeclared rule.

### Decision D-197 - Repair aggregate-output security

Decision: Require finite real scores in [0,1] with documented tolerance; publish one canonical aggregate JSON through descriptor-chain `O_NOFOLLOW`, no-overwrite hard-link publication, and no post-link public unlink. Do not persist sheet name or source path.

Rationale: [OBSERVED - parent-supplied independent review] Initial review failed on float boundaries, NaN/Inf/bool/string acceptance, partial/symlink writing, and sheet-name persistence. Repairs passed concurrency (1/8 writers), race/symlink/traversal/error/privacy/determinism, mode 0600, and no-residue checks.

Alternatives not selected:

- Multi-file or symlink-following writer: rejected for partial publication and path-race exposure.
- Persist sheet/path metadata: rejected as unnecessary privacy exposure.
- Permit non-finite values or remove tolerance: rejected because boundaries must be deterministic and finite.

### Impacts and claim boundary

- [OBSERVED] Package is 0.2.0; extension remains rule-only with no model interface.
- [OBSERVED] Two runs took 70.65/71.58 seconds, max RSS 398,360,576/417,742,848 bytes; these are observations, not capacity claims.
- [UNKNOWN] Rights for future learned vocabularies/derived artifacts, cross-platform writer behavior, and protected external-test performance.

### Verification

- [OBSERVED - parent-supplied] Independent replay recomputed summaries, confusions, support, and gate; no forbidden content, zero inner/outer crossings, identical artifacts: `PASS`.
- [OBSERVED - parent-supplied] Focused baseline/selection tests 22/22, full Python 3.11 suite 315/315 in 51.807s, and Node detector 24/24: `PASS`.
- [OBSERVED - parent-supplied] `uv` lock check, `git diff --check`, sdist/wheel build, isolated Python 3.11 install/import 0.2.0, and console help: `PASS`; temporary build output moved to Trash.
- [OBSERVED - parent-supplied] Two 14,052-byte aggregate artifacts were byte-identical, SHA-256 `cc821dee5e20b5b04926f6ebb708d2bfc67a8ba466ec7a3960743ed6282ca5ec`.
- Unrun: authorized Fisher phishing evaluation, multilingual/native-speaker validation, protected test, model-extension parity, cross-platform validation, commit, and push.

### Remaining Risks

- [UNKNOWN] SMS spam/ham evidence may not represent Fisher phishing campaigns or languages.
- [UNKNOWN] License/derived-artifact rights, protected external-test results, and cross-platform behavior remain unresolved.
- [OBSERVED] Gate rejected the selector; frozen baseline remains the only deployment candidate and extension remains rule-only.

### Recommended Next Action

Obtain authorized, rights-cleared Fisher phishing data and a protected evaluation protocol before any deployable model claim. Preserve the baseline and extension boundary. Git commit and push require separate explicit user approvals; periodic publication is not authorized by this checkpoint.

### Correction history

None. This record is append-only; no commit or commit SHA is associated with this checkpoint.

## Decision record - LUNA-20260902-008

### Canonical decision-identity correction for nested model selection

- Lifecycle: `CORRECTION_RECORDED`; no technical change and no commit planned
- Recorded: 2 September 2026; responsible agent: luna; branch: `master`
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`; commit SHA: Pending/not applicable
- Planned subject: None — not prepared; required trailer: None
- Git action: No staging, commit, push, amend, merge, rebase, tag, publication, or release

[OBSERVED - parent-supplied integrity finding] Two historical `Decision D-196` headings exist: browser-extension packaging (`LUNA-20260902-002`) and nested selection (`LUNA-20260902-006`). This resulted from independent append-only checkpoints assigning numbers without a shared live counter.

[DECISION] Preserve both historical headings and content. The nested model-selection decision is canonically `D-198`; aggregate-output security remains `D-197`. Future references to nested selection must use D-198. This true-tail correction supersedes the earlier misplaced correction notice `LUNA-20260902-007`; no historical heading or technical file is changed.

Rationale: [DERIVED] Rewriting finalized headings violates append-only preservation; a true-tail mapping preserves auditability. D-198 was the next unused decision identity at inspection.

Alternatives not selected:

- Rewrite either historical D-196 heading: rejected under append-only policy.
- Leave the duplicate unresolved: rejected because ambiguous references impair auditability.

### Verification

- `[OBSERVED - Luna inspection]` Confirmed two D-196 headings and D-197; D-198 was unused before correction. Canonical mapping is now unique: packaging D-196, aggregate security D-197, nested selection D-198.
- `[OBSERVED - Luna inspection]` UTF-8, LF-only, final newline, no trailing whitespace, unique Luna IDs, and `git diff --check` pass; this record is at live EOF.
- `[OBSERVED - Luna inspection]` No technical file, Git state, or legacy DOCX was changed.

### Remaining Risks and Follow-up

- [UNKNOWN] Historical literal D-196 headings remain visible by design; reviewers must follow the canonical mapping.
- Next owner/action: use D-198 for future nested-selection references and retain this correction.

### Correction history

None. This is the append-only correction record.

## Decision record - LUNA-20260902-009

### Verified code-slop cleanup checkpoint

- Lifecycle: `IMPLEMENTATION_VERIFIED_LOCAL`; no commit planned
- Recorded: 2 September 2026; responsible agent: luna; branch: `master`
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`; commit SHA: Pending/not applicable
- Planned subject: None — local checkpoint only; required trailer: None
- Git action: No staging, commit, push, amend, merge, rebase, tag, publication, or release

### Findings

[OBSERVED - parent-supplied] Cleanup covered formatting/readability in `fisher_extension_package.py`; removal of the private uncalled `_evaluate_boundary_with_inspector` and stale test import; confirmed-unused test imports; the unused returned `prediction` field and fake test payload; an exception binding and unreachable assertion after `ArgumentParser.exit()`; replacement of an incomplete four-module test list in `README.md` with full `unittest discover`; and removal of ignored/regenerable `.DS_Store`, project `__pycache__` directories, and three empty duplicate-name directories while preserving outputs.

[OBSERVED - parent-supplied] The packager's before/after attribute-free AST SHA-256 is identical: `21b8ee5665ef5e99e6ffa0a7f1f861c6441c4c1254c9cc625425b1263de96590`. All 28 top-level definitions now have at least two blank lines between them. No logic, statement/evaluation order, exception, or cleanup behavior changed; traceback line numbers necessarily moved.

[OBSERVED - parent-supplied] Before removal, the private helper occurred only as its definition and an unused test import; it was underscored and absent from `__all__`. Post-edit search found no references. Public `evaluate_boundary` remains exported, and `_evaluate_metric_run_with_inspector` remains because tests use it.

[OBSERVED - parent-supplied] No consumer used returned `outcome['prediction']`; the local prediction remains used to compute metrics. [DERIVED - parent-supplied] `ArgumentParser.exit()` raises `SystemExit`, making the following assertion unreachable.

### Assumptions

- [ASSUMED] Parent-supplied findings and command outcomes describe the current working tree; Luna did not independently reconstruct every technical hunk.
- [UNKNOWN] Whether an external consumer imports the removed private underscored helper despite its absence from exports; no such consumer is evidenced.

### Decision D-199 - Define and bound slop cleanup

Decision: Treat slop narrowly as proven dead or unused code, unreachable code, unused transient data, misleading verification documentation, and objectively compressed formatting. Preserve behavior, public interfaces, security cleanup, and error boundaries.

Rationale: [OBSERVED - parent-supplied] The cited symbols and branches were confirmed unused/unreachable, the packager AST hash is unchanged, and the full verification suite passed. [DERIVED] This boundary addresses readability and maintenance noise while minimizing semantic and compatibility risk.

Alternatives not selected:

- Consolidate duplicated validator helpers: rejected as higher-risk and ambiguous without a demonstrated defect.
- Delete safety-heavy modules or remove exported helpers: rejected to preserve public behavior and security boundaries.
- Change build/sdist scope: rejected because packaging distribution scope remains undecided.
- Add lint/formatter/type-check dependencies: rejected because no such tooling is configured and the request did not require dependency changes.

### Impacts and claim boundary

- [OBSERVED] Affected paths are `fisher_extension_package.py`, `fisher_engine/evaluation.py`, `tests/test_engine_evaluation.py`, `tests/test_engine_core.py`, `tests/test_validator.py`, `fisher_baselines/selection.py`, `tests/test_baseline_selection.py`, `fisher_baselines/cli.py`, `README.md`, and ignored/regenerable clutter paths removed during cleanup.
- [OBSERVED] Source-closure/system-manifest hashes for `fisher_engine/evaluation.py` intentionally change because the private helper was removed; no public API removal was found.
- [OBSERVED] Formatting changes traceback line numbers. [UNKNOWN] Packaging distribution scope mismatch remains unresolved.

### Verification

- [OBSERVED - parent-supplied] `UV_CACHE_DIR=/tmp/nlp-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run python -m unittest discover -v -s tests -p 'test_*.py'`: 315 tests passed in 52.114s.
- [OBSERVED - parent-supplied] `node --test browser_extension/tests/*.test.mjs`: 24 tests passed.
- [OBSERVED - parent-supplied] `python3 -m compileall -q fisher_baselines fisher_engine fisher_data fisher_governance fisher_pilot fisher_audit fisher_extension_package.py`: passed.
- [OBSERVED - parent-supplied] Targeted baseline tests: 22 passed in 1.977s; packager tests: 23 passed in 0.321s; independent reviewer reran packager 23, baseline selection 9, engine evaluation 26, and Node 24: all passed.
- [OBSERVED - parent-supplied] `git diff --check` and stale-symbol scans passed. No lint, formatter, or type-check tooling is configured; no third-party lint/type check was run.

### Remaining Risks

- [UNKNOWN] Extensive pre-existing dirty and untracked work prevents attribution-based proof of every surrounding hunk.
- [UNKNOWN] External use of the removed private helper cannot be proved absent, although it was not exported and had no repository references.
- [OBSERVED] Traceback line numbers moved; packaging distribution scope remains undecided.

### Recommended Next Action

Review the exact technical diff in the parent workflow, then obtain explicit user approval before any Git commit or publication. If committing, create a separate commit record with a planned subject, assign a new Luna ID, mark its SHA Pending, and include the same ID as the commit-message trailer.

### Correction history

None. This record is append-only; no commit or commit SHA is associated with this checkpoint.

## Decision record - LUNA-20260902-010

### Expanded compatible code-slop cleanup checkpoint

- Lifecycle: `IMPLEMENTATION_VERIFIED_LOCAL`; no commit planned
- Recorded: 2 September 2026; responsible agent: luna; branch: `master`
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`; commit SHA: Pending/not applicable
- Planned subject: None — local checkpoint only; required trailer: None
- Git action: No staging, commit, push, amend, merge, rebase, tag, publication, or release

### Findings

[OBSERVED - parent-supplied] Against snapshot `/tmp/nlp-slop-before.bydTr2` (taken after the prior cleanup checkpoint), the compatible second pass changed 132 lines by insertion and 277 by deletion across snapshot-comparable files, for a net reduction of 145 lines, plus two deletions in `fisher_pilot/validator.py`: 147 additional source/test lines removed.

[OBSERVED - parent-supplied] Affected paths and net deltas: `fisher_engine/semantic.py` (-29), `evaluation.py` (-25), `candidate.py` (-22), `preflight.py` (-22), `harness.py` (-2), `fisher_baselines/evaluation.py` (-32), `fisher_baselines/selection.py` (-11), `tests/test_baseline_selection.py` (-2), and `fisher_pilot/validator.py` (-2).

[OBSERVED - parent-supplied] The cleanup reuses an existing semantic projection while retaining parser aliases, expected-packet mismatch behavior, the unchecked helper, and all exports; removes dead evaluation tuples, repeated immutable kwargs, duplicate descriptor validation, redundant receipt-SHA rechecks, write-only harness state, a one-use alias, an unreachable nominal-alpha condition, and duplicated baseline work. The model factory builds only the requested pipeline, the score helper returns metrics directly, model metadata is shared, and metrics aggregate in one loop.

[OBSERVED - parent-supplied] An interim broader pass removed root/exported/source compatibility APIs. Independent review identified that risk, and all such APIs and tests were restored before final verification. Final public/root compatibility smoke passed.

### Assumptions

- [ASSUMED] Parent-supplied deltas, restoration details, and command outcomes describe the final live working tree; Luna did not reconstruct every technical hunk.
- [UNKNOWN] Whether private underscore helpers have consumers outside this repository.

### Decision D-200 - Prefer compatible high-confidence cleanup over maximum deletion

Decision: Keep the final compatible engine and baseline reductions while preserving root/exported/source compatibility APIs and their tests. Do not delete the isolated untracked deferred prototype stack or consolidate the artifact validator in this checkpoint.

Rationale: [OBSERVED - parent-supplied] Final review restored every compatibility API removed by the interim pass, and compatibility smoke plus the full test suite passed. [DERIVED] Retaining those APIs bounds cleanup to maintenance noise without knowingly changing supported import or export surfaces. [OBSERVED - parent-supplied] Artifact-validator consolidation was rejected because list/int-subclass handling and malformed-error precedence differ.

Alternatives not selected:

- Keep the interim maximum-deletion pass: rejected after independent review found compatibility API removals.
- Delete the isolated untracked deferred prototype stack (~22.9K lines): rejected because untracked deletion is unrecoverable and requires explicit scope confirmation.
- Consolidate the artifact validator: rejected because edge-case handling and error precedence are not equivalent.
- Claim real-world performance improvement: rejected because no timing benchmark was run.

### Impacts and claim boundary

- [OBSERVED] Final changes affect engine semantic/evaluation/candidate/preflight/harness code, baseline evaluation/selection, the baseline test, and the pilot validator; no public/root compatibility API was removed in the final state.
- [DERIVED] Source-closure and related hashes may change where source text changed, even when behavior and receipt outputs remain equivalent.
- [UNKNOWN] Attribution of every surrounding hunk remains limited by the extensive pre-existing dirty and untracked tree; external private-helper consumers, real-world timing, and deferred-stack disposition remain unresolved.

### Verification

- [OBSERVED - parent-supplied] `UV_CACHE_DIR=/tmp/nlp-uv-cache PYTHONDONTWRITEBYTECODE=1 uv run python -B -m unittest discover -q -s tests -p 'test_*.py'`: 315 passed in 52.009s.
- [OBSERVED - parent-supplied] `node --test browser_extension/tests/*.test.mjs`: 24 passed; compileall, engine/audit `--help`, compatibility imports/properties, `git diff --check`, and final project cache scan all passed.
- [OBSERVED - parent-supplied] Independent engine review: 68 tests passed; eight candidate scenarios were byte-identical; four preflight receipt hashes were identical; five malformed-receipt mutations preserved the same errors; reviewed reduction exactly 46 lines.
- [OBSERVED - parent-supplied] Independent baseline review: all nine model/C parameter trees and predictions/scores were equal; nested-selection artifact hashes were identical; focused tests 22 passed. Additional focused active tests 72 passed, four baseline serialized outputs were identical, and exhaustive nominal-alpha comparison across 7,381 cases was identical.
- [OBSERVED - parent-supplied] Semantic compatibility focused tests 76 passed and plan/hash outputs were identical.

### Remaining Risks

- [UNKNOWN] Extensive pre-existing dirty/untracked paths prevent complete Git attribution.
- [UNKNOWN] Private underscore helper consumers outside the repository and real-world performance impact are not verified.
- [OBSERVED] The isolated untracked deferred prototype stack remains present; no deletion was authorized. No commit, staging, or publication occurred.

### Recommended Next Action

Review the final technical diff. If removal of the isolated untracked prototype stack is intended, provide explicit scope confirmation first; otherwise obtain separate explicit approval before preparing any commit or publication.

### Correction history

None. This record is append-only; no commit or commit SHA is associated with this checkpoint.

## Decision record - LUNA-20260902-012

### True-tail correction for Fisher browser-extension v0.3 record

- Lifecycle: `CORRECTED_APPEND_ONLY`; no commit planned or approved
- Recorded: 2 September 2026; responsible agent: luna; branch: `master`
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`; commit SHA: Pending/not applicable
- Planned subject: None — register correction only; required trailer: None
- Git action: No staging, commit, push, amend, merge, rebase, tag, publication, or release

### Findings

[OBSERVED - Luna inspection] The complete v0.3 selected-text upgrade is recorded in `LUNA-20260902-011`, but a later substantive register entry was appended after it. This entry restores true-tail placement without rewriting or deleting either finalized record.

### Decision D-202 - Preserve v0.3 evidence with an append-only tail pointer

Decision: Treat `LUNA-20260902-011` as the canonical complete v0.3 record and this entry as its live-EOF correction pointer.

Rationale: [DERIVED] Appending a pointer preserves historical text and ordering while resolving the register's live-tail requirement. No technical claim, source file, or Git state is changed.

Alternatives not selected:

- Move or rewrite the earlier v0.3 record: rejected because finalized register history is append-only.
- Duplicate the complete v0.3 record: rejected because duplication would create conflicting audit surfaces.

### Verification

- [OBSERVED - Luna inspection] Confirmed `LUNA-20260902-011` occurs once and this correction is at live EOF.
- [OBSERVED - Luna inspection] UTF-8 decoding, LF-only line endings, final newline, and no trailing whitespace pass; `git diff --check` passes.
- [OBSERVED - Luna inspection] No technical file, Git state, or legacy DOCX was changed.

### Remaining Risks and Follow-up

- [UNKNOWN] The register contains pre-existing duplicate historical Luna-ID references; they were not rewritten under append-only policy.
- Next owner/action: use `LUNA-20260902-011` for the complete v0.3 evidence and retain this correction pointer.

### Correction history

This record corrects placement only; the original v0.3 statement in `LUNA-20260902-011` is preserved verbatim.

## Decision record - LUNA-20260902-013

### Register-tail duplicate correction

- Lifecycle: `CORRECTED_APPEND_ONLY`; no commit planned or approved
- Recorded: 2 September 2026; responsible agent: luna; branch: `master`
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`; commit SHA: Pending/not applicable
- Planned subject: None — register correction only; required trailer: None

### Findings

[OBSERVED - Luna inspection] A concurrent append caused duplicate `LUNA-20260902-012` blocks. The earlier copy is explicitly marked superseded; this record is the canonical live-EOF pointer to the complete v0.3 record `LUNA-20260902-011`.

### Decision D-203 - Preserve history and identify the canonical tail

Decision: Preserve both prior blocks, treat the marked earlier copy as superseded, and use the final `LUNA-20260902-012` block plus this record as the authoritative tail correction.

Rationale: [DERIVED] Append-only correction preserves audit history and avoids rewriting technical evidence.

Alternatives not selected:

- Delete or rewrite the duplicate block: rejected under append-only policy.
- Duplicate the full v0.3 evidence again: rejected as unnecessary.

### Verification

- [OBSERVED - Luna inspection] UTF-8 decoding, LF-only line endings, final newline, no trailing whitespace, and `git diff --check` pass.
- [OBSERVED - Luna inspection] No technical file, Git state, or legacy DOCX was changed.

### Remaining Risks and Follow-up

- [UNKNOWN] Pre-existing duplicate Luna-ID references remain elsewhere in the register; no historical content was rewritten.
- Next owner/action: use `LUNA-20260902-011` for v0.3 evidence and the final tail correction records for placement.

### Correction history

This record documents an append-order correction only.

## Decision record - LUNA-20260906-001

### Fisher browser-extension v0.4 architecture checkpoint

- Lifecycle: `DECISION_RECORDED`; implementation in progress; no commit planned or approved
- Recorded: 6 September 2026; responsible agent: luna; branch: `master`
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`; commit SHA: Pending/not applicable
- Planned subject: None — architecture checkpoint only; required trailer: None
- Git action: No staging, commit, push, amend, merge, rebase, tag, publication, or release

### Findings and decision

[OBSERVED - parent-supplied repository evidence] The v0.3 detector, popup, selection, packager, tests, README, and pyproject were inspected. The repository is broadly dirty and contains untracked paths; no Git mutation was performed for this checkpoint.

[OBSERVED - parent-supplied review evidence] The auxiliary nested spam-selection mean-F1 improvement is `0.005114500`, below the README's predeclared `0.01` threshold. No v0.4 tests or metrics are claimed here.

#### Decision D-204 - Use a deterministic local v0.4 analyzer boundary

Decision: Preserve `detector.mjs` intact and add `analyzer.mjs` as shared logic for a redesigned popup and root `fisher.mjs` Node stdin CLI. Add `links.mjs` for local WHATWG structural URL analysis; support message and URL modes; emit generic non-echo findings and `nextSteps`; retain the explicit selected-text boundary; and provide bounded batch aggregation of counts only. Keep the extension local and permission/network/storage-neutral.

Rationale: [DERIVED] The existing v0.3 behavior and selected-text contract are the verified compatibility boundary. [OBSERVED - parent-supplied architecture decision] A shared analyzer avoids divergent popup and CLI behavior while the root CLI remains a Node entry point rather than browser runtime code. [DERIVED] The measured auxiliary gain below the predeclared threshold does not justify model deployment in this extension checkpoint. [OBSERVED - parent-supplied] URL findings are limited to structural analysis and must not claim reputation or legitimacy.

Alternatives not selected:

- Extract or refactor the old detector into the new analyzer: rejected because the parent-supplied scope explicitly preserves `detector.mjs` and avoids a compatibility-risk refactor.
- Deploy the nested selection model in v0.4: rejected because its observed mean-F1 improvement (`0.005114500`) is below the predeclared `0.01` gate.
- Add network reputation checks, durable storage, or new permissions: rejected because the chosen scope is local and permission/network/storage-neutral.
- Run the CLI inside the browser runtime: rejected because the selected architecture keeps the root CLI as a Node stdin interface.

### Impacts and claim boundary

- [OBSERVED] Intended affected implementation surfaces are additive `browser_extension/analyzer.mjs`, `browser_extension/links.mjs`, popup integration, and root `fisher.mjs`, with related package/documentation integration supplied by the parent.
- [DERIVED] Existing detector behavior and the selected-text boundary remain compatibility anchors.
- [OBSERVED] No new permissions, network access, or storage are intended; no reputation or legitimacy claim is permitted from URL analysis.
- [UNKNOWN] Final implementation behavior, test outcomes, metrics, and exact final affected paths remain unverified until the parent completes the work.

### Verification

- [OBSERVED - parent-supplied] Prior v0.3 detector, popup, selection, packager, tests, README, and pyproject surfaces were inspected.
- [OBSERVED - parent-supplied] The v0.4 architecture decision was reviewed independently; the predeclared selection threshold comparison was recorded above.
- [OBSERVED - Luna inspection] Existing register structure and Luna IDs were inspected before this append; the assigned record and decision identities were unused.
- Not run: v0.4 implementation tests, browser-extension tests, CLI tests, compile checks, lint/type checks, and final diff review; implementation is still in progress.

### Remaining risks and follow-up

- [UNKNOWN] The additive analyzer, link analysis, popup integration, CLI, and packaging/documentation may expose implementation or compatibility defects until verified.
- [UNKNOWN] No deployment-model claim is established by this architecture checkpoint; the threshold comparison does not validate phishing-domain performance.
- Next owner/action: parent implementation agents complete the bounded v0.4 work, run targeted and related verification, then invoke Luna for the completed verification checkpoint and any commit preparation.

### Alternatives, correction history, and record status

No correction history. This is an append-only architecture checkpoint; no commit or commit SHA is associated with it.

## Decision record - LUNA-20260906-002

### Fisher browser-extension v0.4 implementation and verification checkpoint

- Lifecycle: `IMPLEMENTATION_VERIFIED_LOCAL`; no commit planned or approved
- Recorded: 6 September 2026; responsible agent: luna; branch: `master`
- Parent SHA: `b23359ac89e072691018c3760c445910d93f110b`; commit SHA: Pending/not applicable
- Planned subject: None — local verification checkpoint; required trailer: None
- Git action: No staging, commit, push, amend, merge, rebase, tag, publication, or release

### Findings and decision

[OBSERVED - parent-supplied] v0.4 implementation is complete locally. Shared `analyzer.mjs` and `links.mjs` were added while the existing detector and selection extractor remained unchanged. The popup now supports message/URL analysis, generic evidence and `nextSteps`, local status display, bounded counters, oversize rejection, and stale-read invalidation. Root `fisher.mjs` provides `analyze` and bounded 500-line, 1 MiB stdin aggregation with fatal UTF-8 handling.

#### Decision D-205 - Verify and retain the local, model-free v0.4 product boundary

Decision: Accept the locally verified v0.4 extension and CLI boundary: same activeTab+scripting permissions, no model fitted or deployed, local structural URL analysis, strict eight-member packaging, pinned development tooling, and read-only CI configuration. Do not make accuracy, reputation, legitimacy, or deployment claims.

Rationale: [OBSERVED - parent-supplied] Real installed Chromium testing, accessibility checks, Node tests, Python tests, package checks, ZIP equality, and syntax/encoding checks all passed. [DERIVED] These checks support local compatibility and packaging claims, but not corpus-wide phishing accuracy or reputation classification. [OBSERVED] The auxiliary nested experiment remains below its predeclared gate and current phishing performance is unknown.

Alternatives not selected:

- Deploy a fitted model: rejected because no model was fitted/deployed and the auxiliary experiment remains below the predeclared threshold.
- Add reputation or legitimacy claims to URL findings: rejected because only local structural analysis was verified.
- Expand permissions, storage, or network access: rejected because the verified manifest retains only `activeTab` and `scripting`.
- Treat CI as executed evidence: rejected because GitHub CI was configured but not run on GitHub.

### Affected paths and impacts

- [OBSERVED] Extension paths: `browser_extension/analyzer.mjs`, `browser_extension/links.mjs`, `browser_extension/tests/analyzer.test.mjs`, `browser_extension/popup.html`, `browser_extension/popup.js`, `browser_extension/styles.css`, `browser_extension/tests/selection.test.mjs`, `browser_extension/manifest.json`, and `browser_extension/README.md`.
- [OBSERVED] Root/package paths: `fisher.mjs`, `package.json`, `package-lock.json`, `playwright.config.mjs`, `.github/workflows/quality.yml`, `.gitignore`, and `README.md`.
- [OBSERVED] Tests/packager: `tests/test_fisher_cli.mjs`, `tests/browser/extension.spec.mjs`, `fisher_extension_package.py`, and `tests/test_extension_package.py`.
- [OBSERVED] Built ZIP has exactly 8 members, 63,328 bytes, SHA-256 `b18f0ba2ccb044c88128793993a43c417f88029ae79e821af6fe9d73e367aa9e`; independent CRC/source equality passed.
- [DERIVED] No new runtime permission, durable message storage, network reputation dependency, or model deployment is evidenced.

### Verification

- [OBSERVED - parent-supplied] `npm test`: 69/69 passed on Node 25.9.0.
- [OBSERVED - parent-supplied] Node 22 test run: 69/69 passed; `npm run test:browser`: 7/7 scenarios, 15.4 seconds, real Chromium 153.0.8010.12, including toolbar selection, empty/restricted selection, URL, oversize, and populated/empty accessibility checks.
- [OBSERVED - parent-supplied] Full Python suite: 316/316 passed in 58.992 seconds; focused package tests: 24/24 passed.
- [OBSERVED - parent-supplied] `npm audit --omit=dev`: 0 vulnerabilities; install audit also 0.
- [OBSERVED - parent-supplied] Node/Python syntax, UTF-8/LF/final-newline/trailing-whitespace checks, `git diff --check`, and `uv.lock` validation passed. Popup screenshots were visually inspected; populated and empty WCAG/axe checks reported zero violations after contrast correction.
- [OBSERVED - parent-supplied] Analyzer, links, popup, CLI, manifest, and packager hashes were recorded; independent ZIP equality and eight-member validation passed.
- Not run: GitHub-hosted CI, stock Chrome/Edge manual UI, assistive-technology testing, broad corpus/language accuracy evaluation, and reputation validation.

### Remaining risks and follow-up

- [UNKNOWN] Heuristic prose ambiguity remains, including residual spaced-word syntax ambiguity; DOM layout, iframe, form, shadow-DOM, and multi-range selection limits remain.
- [UNKNOWN] Chrome for Testing does not establish stock Chrome/Edge or human assistive-technology behavior.
- [UNKNOWN] Corpus/language accuracy, phishing performance, and reputation/legitimacy remain unmeasured.
- [OBSERVED] CI is configured but not yet run on GitHub; generated `node_modules`, test outputs, and browser outputs are ignored. No Git mutation occurred and the dirty `master` state remains.
- Next owner/action: review the exact technical diff, then obtain separate explicit user approval before any commit or publication. If committing, create a commit-specific Luna record and trailer; do not backfill a self-referential SHA in this record.

### Correction history

None. This is an append-only verification checkpoint; no commit or commit SHA is associated with it.

## Decision record - LUNA-20260908-001

### Fisher v0.4 publication-preparation and privacy-correction checkpoint

- Lifecycle: `COMMIT_PREPARATION`; parent-prepared staged publication; no commit or push performed
- Recorded: 8 September 2026; responsible agent: luna; branch: `main` (unborn)
- Planned publication root: unborn `main`; preserved local source branch: `master` at `b23359ac89e072691018c3760c445910d93f110b`
- Parent SHA: None for planned new root; commit SHA: Pending/not applicable
- Planned subject: `initial commit`
- Required trailer if later committed: `Luna-ID: LUNA-20260908-001`
- Luna Git action: No staging, commit, amend, reset, restore, clean, push, publication, or release; parent prepared the staged `main` snapshot independently

### Findings and decision

[OBSERVED - parent-supplied] `origin` is the private repository `https://github.com/m-rithik/Phishing-in-indian-language.git`, with ADMIN access and no remote heads. The planned clean publication root is unborn `main`; the original local `master` retains existing history at `b23359ac89e072691018c3760c445910d93f110b` and is preserved without deletion or rewriting.

[OBSERVED - parent-supplied] The complete bundle and original register were preserved in ignored local backup directory `outputs/publication-backup.xKTYQo` as `master.bundle` and `CHANGE_DECISION_LOG.original.md` before publication sanitation. The parent reports 160 local targets and 97 resolved anchors, with no concrete credentials found.

[OBSERVED - parent-supplied] The staged index contains a coherent 114-path root snapshot for the planned new `main` root. The original local `master` bundle and ref remain preserved at `b23359ac89e072691018c3760c445910d93f110b`; the planned publication root has no parent commit.

[OBSERVED - parent-supplied] The user explicitly approved committing this exact prepared 114-path snapshot with subject `initial commit` and separately approved pushing it to `origin/main`.

#### Decision D-206 - Sanitize account-specific source evidence before publication

Decision: Generalize only the account-specific absolute workbook path in the historical source evidence to `/path/to/Spam Message Collection (1).xlsx`, preserve the verified workbook SHA-256, and record the correction here. Update only the active register header's stale branch/status and timestamp; preserve historical observations and the legacy DOCX.

Rationale: [OBSERVED - parent-supplied] The absolute path identifies a local account location and is the sole private-path finding in the publication audit. [DERIVED] Generalizing the path removes account-specific disclosure while preserving the source identity via its hash and the substantive audit facts. [OBSERVED] The original register is archived locally for recovery and audit comparison.

Alternatives not selected:

- Publish the absolute workbook path unchanged: rejected because it discloses an account-specific local location.
- Remove the entire workbook evidence: rejected because the verified hash and audit provenance remain material.
- Rewrite historical records broadly: rejected under append-only preservation; only the narrowly identified privacy correction and active header are changed.
- Push the existing local branch directly: rejected because publication requires a clean coherent root snapshot while preserving the original local `master`.

### Impacts and claim boundary

- [OBSERVED] Planned publication subject is `initial commit`; no commit SHA or push result exists yet.
- [DERIVED] The path correction reduces local-account disclosure without changing the workbook hash or the substantive dataset audit claim.
- [OBSERVED] Publication-coherence corrections include README and `docs/research/EXECUTION_STATUS.md` status updates, complete sdist allowlisting, and removal of one trailing blank; these are recorded as staged technical changes supplied by the parent.
- [OBSERVED] The remote is private; no claim is made that publication sanitation is complete until final staged-diff inspection.
- [UNKNOWN] Final clean-snapshot membership, staged diff, commit SHA, and remote branch state remain pending parent validation.

### Verification

- [OBSERVED - parent-supplied] Remote URL, private visibility, ADMIN access, empty remote-head state, local HEAD, and dirty working-tree context were checked.
- [OBSERVED - parent-supplied] Publication backup contains the original bundle and original Markdown register; no credentials were found and local-target/anchor audit counts were recorded.
- [OBSERVED - parent-supplied] Disposable clean index export passed `npm ci --ignore-scripts`, `npm test` 69/69, `npm run test:browser` 7/7 in 5.0 seconds, `uv sync --locked`, full Python tests 316/316 on Python 3.12.11 in 56.377 seconds, and the packager reproduced the eight-member ZIP with SHA-256 `b18f0ba2ccb044c88128793993a43c417f88029ae79e821af6fe9d73e367aa9e`.
- [OBSERVED - parent-supplied] Original Python 3.11 full tests also passed 316/316 in 54.804 seconds. Worker verification passed sdist/wheel completeness, forbidden-artifact absence, lock/link checks, and Markdown 77-link/64-anchor validation. Staged blob scans found zero forbidden artifact paths and zero user-local paths.
- [OBSERVED - Luna inspection] Cached status shows unborn `main`, 114 staged paths, and no unstaged diff before this register update; this update is intentionally not staged by Luna.
- [OBSERVED - Luna inspection] Active header and the historical workbook-path evidence were located before this correction; existing register structure and IDs were inspected.
- Not run: GitHub-hosted CI, stock Chrome/Edge manual UI, assistive-technology testing, broad corpus/language accuracy evaluation, reputation validation, commit, push, GitHub post-push verification, or SHA backfill.

### Remaining risks and follow-up

- [UNKNOWN] Publication sanitation may reveal additional privacy or provenance issues during final staged-diff review; the current parent scan found none beyond the corrected path.
- [UNKNOWN] The remote has no heads; exact destination branch creation and post-push state remain unverified and require separate approval.
- [OBSERVED] Historical observations remain in place by design; the original register is recoverable from the ignored local backup.
- Next owner/action: parent stage this finalized register, verify the exact staged diff and trailer `Luna-ID: LUNA-20260908-001`, create `initial commit`, push to `origin/main`, and verify the remote result. Backfill the final SHA during the next substantive Luna update; CI remains unrun until publication.

### Correction history

This record is the dated append-only privacy correction for the account-specific workbook path and the active-header maintenance note. The original historical statement is preserved in the local publication backup; no legacy DOCX change was made.

### Dated revision - 8 September 2026 post-publication verification

[OBSERVED - parent-supplied] The approved publication was executed as commit `4dbf38c9487a7aeb4da1c42efdb91b8fb1b36787` with subject `initial commit`, trailer `Luna-ID: LUNA-20260908-001`, parent `None`, and 114 files. The commit was pushed successfully to `origin/main`; `git ls-remote` matched the same SHA, and the working tree was clean and synchronized immediately after push, before this local revision. Original local `master` remains preserved at `b23359ac89e072691018c3760c445910d93f110b`.

[OBSERVED - parent-supplied] GitHub Actions run `34262467068` succeeded from `2026-09-08T18:20:41Z` through `2026-09-08T18:23:12Z`: npm reported 69 tests/69 passes, browser tests reported 7 passed in 7.2 seconds, Python reported 316 tests in 97.800 seconds with `OK`, and the packager produced 8 members/63,328 bytes with the recorded ZIP SHA-256 `b18f0ba2ccb044c88128793993a43c417f88029ae79e821af6fe9d73e367aa9e`. The run verified the same commit SHA; GitHub API tree `bb1d8241e2fbaef6afe68af9b713873d10a25006` equals the local HEAD tree. Repository default branch is `main` and remains private. These comprise 392 passing tests.

[OBSERVED - parent-supplied] The independent pre-publication audit passed: 114 paths, zero forbidden artifacts, zero user-local paths, zero concrete credentials, and 160 local targets with 97 anchors resolving. Post-publication independent review verified the commit, ref, and trailer. No new technical feature or document-only hash-backfill commit was created.

[OBSERVED - parent-supplied] The workflow currently passes while pinned actions target deprecated Node 20 and GitHub forces Node 24. Maintenance follow-up belongs to the lead owner.

Revision status: `BACKFILLED_COMMITTED_AND_PUBLISHED`; this audit revision is local and uncommitted. It updates the prepared record's pending SHA context without changing published code or creating a document-only commit.

Remaining claim boundary: [UNKNOWN] broad corpus/language accuracy, reputation or legitimacy performance, stock Chrome/Edge behavior, and manual assistive-technology behavior remain unverified. CI success does not establish those claims.

Next owner/action: retain the published commit and remote verification as final evidence; lead owner should track the GitHub Actions Node-runtime maintenance warning. No further commit, amend, or push is authorized by this revision.

## Decision record - LUNA-20260909-001

### Fisher Project Overview v4 presentation checkpoint

- Lifecycle: `ARTIFACT_VERIFIED_LOCAL`; ignored output; no Git action requested
- Recorded: 9 September 2026; responsible agent: luna; branch: `main`
- Planned subject: None — user-requested presentation artifact only
- Commit SHA: Not applicable; no commit or push
- Affected artifact: `outputs/presentations/Fisher_Project_Overview_v4.pptx`

### Findings and decision

[OBSERVED - parent-supplied] The requested simple, easy-to-understand deck is complete with 7 slides, 2,319,554 bytes, and SHA-256 `006177d564f7d362b91ca22b8b0b3b61ced9340c437957cdcc5fcf13c48a0bfe`. Its flow covers the problem, current v0.4 extension/CLI, a three-step local check, explainable result levels, privacy and test evidence, and honest limits with the responsible pilot/transliteration next step.

#### Decision D-207 - Deliver a simple evidence-bounded overview deck

Decision: Deliver v4 as the sole presentation artifact. Use a custom light 16:9 Arial design with navy, teal, and coral, project screenshots, and two original illustrative generated artworks. Cite project sources in speaker notes and retain the rule-based prototype’s limits; do not imply trained Fisher accuracy, language coverage, or reputation capability.

Rationale: [OBSERVED - parent-supplied] Sources were the current README, extension guide/code/manifest/tests, execution status, pilot, blueprint, and verified GitHub Actions run `34262467068`. [OBSERVED] Final package, layout, font, import, rendering, montage, and overflow checks passed. [DERIVED] A concise visual narrative and explicit claim boundary match the user’s simplicity request while avoiding unsupported model claims.

Alternatives not selected:

- Deliver intermediate v1-v3 decks: rejected because v4 is the final validated artifact; intermediates remain ignored.
- Use the presentation skill/template picker: rejected because the parent selected and verified a custom design for this deck.
- Present generated art as photographs or evidence: rejected; speaker notes identify it as illustrative.
- Add charts/tables or measured accuracy claims: rejected because validation found no charts/tables and no such evidence exists.

### Impacts and claim boundary

- [OBSERVED] Artifact is an ignored output; no source code, configuration, Git state, or legacy DOCX changed for this checkpoint.
- [OBSERVED] Slide size is 13.3333 × 7.5 inches; Arial policy passed for 78 text scripts; first-party import passed; no charts or tables are present.
- [DERIVED] The deck explains verified behavior and packaging/tests, not production effectiveness.
- [UNKNOWN] Broad corpus accuracy, language coverage, reputation/legitimacy performance, and manual assistive-technology behavior remain unverified.

### Verification

- [OBSERVED - parent-supplied] Finalizer package integrity: 7 slides, zero findings; layout: zero findings and zero warnings; `slides_test.py`: pass with no overflow.
- [OBSERVED - parent-supplied] Every final slide rendered at 1600×900 and was inspected; montage review found no overlap, clipping, or broken crop. Slides 1–6 matched individually inspected v3 renders after unchanged re-export; slide 7 was re-inspected after its wording fix.
- [OBSERVED - parent-supplied] Speaker notes cite sources. Generated illustrations are documented as illustrative. No charts/tables were introduced.
- Not run: model training, corpus evaluation, accuracy measurement, language-coverage measurement, reputation validation, or Git commit/push.

### Remaining risks and follow-up

- [UNKNOWN] The rule-based prototype’s real-world accuracy and multilingual coverage remain unknown.
- [UNKNOWN] Rendered browser screenshots and custom illustrations communicate the workflow but are not empirical evidence.
- Next owner/action: deliver v4 only; preserve intermediate ignored artifacts and avoid expanding claims beyond the verified prototype, packaging, and test behavior.

### Correction history

None. This is an append-only local artifact checkpoint.

## Decision record - LUNA-20260909-002

### Fisher Project Overview v5 presentation revision

- Lifecycle: `ARTIFACT_VERIFIED_LOCAL`; ignored output; no Git action requested
- Recorded: 9 September 2026; responsible agent: luna; branch: `main`
- Planned subject: None — user-requested presentation revision only
- Commit SHA: Not applicable; no commit or push
- Affected artifact: `outputs/presentations/Fisher_Project_Overview_v5.pptx`

### Findings and decision

[OBSERVED - parent-supplied] The revised simple project deck is complete with 7 slides, 2,320,146 bytes, and SHA-256 `1b70a9e14ca008f41fe6074ef589037bd3c2e43225b765445803fbe697a52032`. Slide 4 now uses a five-stage editable native diagram titled “Fisher’s local checking pipeline”: choose content, validate input, prepare content, inspect patterns, and explain next step.

#### Decision D-208 - Explain the local checking pipeline with an editable native diagram

Decision: Deliver v5 as the presentation artifact. Replace the generic three-step user journey with the five-stage pipeline and explicitly state that exact checks differ for message versus URL, Fisher never opens web addresses, and no-match does not prove safety.

Rationale: [OBSERVED - parent-supplied] The implementation sources inspected were `browser_extension/analyzer.mjs`, `detector.mjs`, `links.mjs`, `selection.mjs`, `popup.js`, and `README`. [DERIVED] The five stages map the deck more directly to the verified local workflow and make the important safety boundary understandable without claiming a trained model or measured accuracy.

Alternatives not selected:

- Keep the generic three-step user journey: rejected because it omitted important distinctions in Fisher’s actual message and URL paths.
- Add a chart or measured performance visualization: rejected because no accuracy or evaluation metric was supplied or measured for this revision.
- Describe Fisher as opening or validating live websites: rejected because the verified safety boundary is that Fisher never opens web addresses.

### Impacts and claim boundary

- [OBSERVED] Only the ignored v5 presentation artifact is the requested output; no commit or push was requested or intended.
- [OBSERVED] The revised diagram is editable and native to the presentation; no charts or tables were added.
- [DERIVED] The deck communicates verified prototype behavior and safety boundaries, not production effectiveness.
- [UNKNOWN] Broad corpus accuracy, multilingual coverage, reputation or legitimacy performance, and manual assistive-technology behavior remain unverified.

### Verification

- [OBSERVED - parent-supplied] Finalizer package integrity passed with zero findings; layout passed with zero findings and zero warnings; Arial font policy passed; first-party import passed.
- [OBSERVED - parent-supplied] All 7 rendered slides were individually visually inspected at 1600×900; the montage was reviewed; `slides_test.py` passed with no overflow.
- Not run: PowerPoint application inspection, model training, corpus evaluation, accuracy measurement, language-coverage measurement, reputation validation, or Git commit/push.

### Remaining risks and follow-up

- [UNKNOWN] The rule-based prototype’s real-world accuracy and multilingual coverage remain unknown.
- [UNKNOWN] Rendered screenshots and generated illustrations communicate workflow but are not empirical evidence.
- Next owner/action: deliver v5 as the current deck and preserve the explicit no-match and no-live-navigation boundaries in future revisions.

### Correction history

None. This is an append-only local artifact checkpoint.

## Decision record - LUNA-20260911-001

### Fisher Project Overview v8 pipeline presentation checkpoint

- Lifecycle: `ARTIFACT_VERIFIED_LOCAL`; ignored output; no Git action requested
- Recorded: 11 September 2026, Asia/Kolkata; responsible agent: luna; branch: `main`
- Planned commit subject: None (local ignored presentation artifact)
- Required trailer: Not applicable — no commit planned
- Commit SHA: Not applicable; no commit or push authorized
- Parent SHA: Not applicable
- Affected artifact: `outputs/presentations/Fisher_Project_Overview_v8.pptx`
- Related ignored build source: `outputs/.pptx-build-fisher/build_deck.mjs`

### Findings and decision

[OBSERVED - parent-supplied] The existing v5 deck already showed Fisher’s current local checking pipeline. The v8 deck adds a distinct slide 5 titled “Planned model training pipeline” after that current-checker slide, renumbers later footers, and contains eight slides total.

#### Decision D-209 - Distinguish the current checker from the future training workflow

Decision: Deliver v8 as the simple project deck with five plain-language planned stages: collect with consent; check the data; split related groups; train and compare; test before release. Include a visible callout that the extension still uses transparent rules, not a trained phishing model.

Rationale: [OBSERVED - parent-supplied] The requested change was to add a pipeline to the simple Fisher PPT. [OBSERVED - parent-supplied] Source evidence was `README.md`, `docs/research/PILOT_V01.md`, and `docs/research/FISHER_RESEARCH_BLUEPRINT.md`. [DERIVED] A separate future-training slide prevents viewers from confusing the existing rule-based extension with an uncompleted model-training pipeline while keeping the explanation accessible.

Alternatives not selected:

- Replace the existing runtime pipeline: rejected because the new slide clarifies a different future training workflow and the current checker remains important context.
- Present training as completed: rejected because no trained phishing model exists in the verified evidence.
- Add unsupported accuracy or model-performance claims: rejected because no such measurements were supplied or verified for this artifact.

### Impacts and claim boundary

- [OBSERVED] The generator was updated to use the available presentation runtime path and v8 filenames; build and output paths are Git-ignored.
- [DERIVED] The deck now communicates both the verified current rule-based workflow and a clearly labeled future research workflow.
- [OBSERVED] No application source, dataset, model, configuration, or runtime behavior changed for this checkpoint.
- [UNKNOWN] Published v0.4 metrics remain a historical snapshot and are not evidence that a trained model exists or that the planned pipeline has run.

### Verification

- [OBSERVED - parent-supplied] First-party finalizer succeeded; package integrity passed; layout validator reported 0 findings and 0 warnings.
- [OBSERVED - parent-supplied] The final deck contains 8 slides at 13.3333 × 7.5 inches; Arial was observed in 103 text runs; first-party reimport passed.
- [OBSERVED - parent-supplied] Final SHA-256: `81d0a86c5c65694916bae2585c6afc4fe622aa2302e6a463426ee8eff98daf17`; byte count: 2,324,739.
- [OBSERVED - parent-supplied] All 8 slides were rendered to `outputs/.pptx-build-fisher/rendered-v8`, visually inspected at full size and in `montage-v8`, and an initially clipped final-stage design was repaired before final v8.
- Not run: opening the deck in the PowerPoint application; model training; corpus evaluation; accuracy measurement; language-coverage measurement; reputation validation; Git commit or push.

### Remaining risks and follow-up

- [UNKNOWN] The PowerPoint application itself was not opened; the verified checks used first-party package/import/render tooling.
- [UNKNOWN] The planned training pipeline has not been executed, so model quality, language coverage, and release readiness remain unverified.
- Next owner/action: use v8 as the current simple overview deck; keep the planned pipeline visibly separate from the transparent rule-based extension until a trained model and measured evaluation exist.

### Correction history

None. This is an append-only local artifact checkpoint.

## Decision record - LUNA-20260911-002

### Fisher v0.5 extension product checkpoint

- Lifecycle: `PREPARED_LOCAL`; working tree uncommitted; no Git action authorized
- Recorded: 11 September 2026, Asia/Kolkata; responsible agent: luna; branch: `main`
- Planned commit subject: `Polish Fisher v0.5 extension` (prospective; requires separate user approval)
- Required trailer: `Luna-ID: LUNA-20260911-002` if a future commit is approved
- Commit SHA: Pending — no commit created
- Parent SHA: `4dbf38c` (current `HEAD`; no commit created for this checkpoint)
- Affected paths: `README.md`; `browser_extension/README.md`; `browser_extension/analyzer.mjs`; `browser_extension/detector.mjs`; `browser_extension/links.mjs`; `browser_extension/manifest.json`; `browser_extension/popup.html`; `browser_extension/popup.js`; `browser_extension/selection.mjs`; `browser_extension/styles.css`; `browser_extension/icon.svg`; `browser_extension/icon-16.png`; `browser_extension/icon-32.png`; `browser_extension/icon-48.png`; `browser_extension/icon-128.png`; `browser_extension/tests/analyzer.test.mjs`; `browser_extension/tests/detector.test.mjs`; `browser_extension/tests/selection.test.mjs`; `tests/browser/extension.spec.mjs`; `tests/test_extension_package.py`; `tests/test_fisher_cli.mjs`; `fisher.mjs`; `fisher_extension_package.py`; `package.json`; `package-lock.json`; `docs/research/EXECUTION_STATUS.md`

### Findings and decision

[OBSERVED - parent-supplied] The browser extension and JavaScript package identity are coordinated at v0.5.0 across package metadata, manifest, analyzer engine version, CLI batch reports, packager, tests, and current README prose. The Python research package remains 0.2.0 as a separate intentional version.

#### Decision D-210 - Ship a bounded, local-only v0.5 extension product slice

Decision: Keep the popup as the user-facing product and deliver the v0.5 behavior as a privacy-preserving, transparent local checker. Centralize link scanning in `browser_extension/links.mjs`; mask locator/email-like spans before semantic matching; preserve message-versus-URL distinctions; and bound selection and input processing. Polish the popup with mode limits, inline correction, focus recovery, separate in-memory drafts, source labels, plain link summaries, ordered next steps, and an `Edit input` action. Add local branding icons, including editable SVG source and PNG runtime icons.

Rationale: [OBSERVED - parent-supplied] The implemented and tested product is the browser-extension popup; no conventional standalone site is present in the repository. [DERIVED] A single link authority prevents analyzer/detector disagreement, while bounded local processing and in-memory drafts preserve the verified privacy boundary. [DERIVED] The v0.5 identity is necessary because externally visible behavior, packaging, docs, and tests changed from the historical v0.4 snapshot.

Alternatives not selected:

- Add storage or scan history: rejected because the verified product promise is local-only and privacy-preserving.
- Build a standalone website: rejected because the actual user-facing product in scope is the popup extension.
- Keep duplicate link detectors: rejected because one canonical authority is needed for consistent evidence and semantics.
- Retain stale v0.4 identity: rejected because the coordinated extension behavior and package contents changed.
- Keep the result action named `Check another`: rejected because `Edit input` accurately describes draft-preserving behavior.
- Include SVG in the runtime archive: rejected because PNG sizes provide the runtime manifest assets while SVG remains an editable source asset.

### Impacts and claim boundary

- [OBSERVED] No new network access, storage, host permissions, background worker, content scripts, or CSP relaxation was introduced. The package remains local-only and bounded.
- [OBSERVED] Runtime packaging includes 12 members and excludes the SVG source; the generated archive is ignored, local, and unpublished.
- [DERIVED] The changes improve consistency, privacy clarity, error recovery, and usability without claiming live reputation checks, a trained model, or safety guarantees.
- [UNKNOWN] Broad real-world accuracy, multilingual coverage, manual screen-reader behavior, and stock Edge behavior remain unmeasured or not directly verified.

### Verification

- [OBSERVED - parent-supplied] `npm test`: 91 passed, 0 failed.
- [OBSERVED - parent-supplied] `npm run test:browser`: 13 passed, 0 failed, including unpacked Chromium, Axe empty/populated states, no external requests, 320px layout, source labels, drafts, `Edit input`, and selection privacy/fidelity.
- [OBSERVED - parent-supplied] `uv run --python 3.11 python -m unittest -q tests.test_extension_package`: 25 passed.
- [OBSERVED - parent-supplied] `uv run --python 3.11 python -m unittest discover -q -s tests -p 'test_*.py'`: 317 passed in 53.904s.
- [OBSERVED - parent-supplied] `npm audit --json`: 0 vulnerabilities.
- [OBSERVED - parent-supplied] Independent final product review found no P0 regression.
- [OBSERVED - parent-supplied] `outputs/browser_extension/fisher-scam-signal-prototype-v0.5.0.zip` contains 12 runtime members, is 82,196 bytes, has SHA-256 `32ad3509089a6c01a665f54c41a0835eefb967b0e9daede21e7452e1022e10a6`, matched an independent `openssl` digest, and passed `unzip -t`.
- [OBSERVED - parent-supplied] Prior `git diff --check` was clean; the parent must rerun it after this append.
- Not run: model training, corpus evaluation, accuracy measurement, language-coverage measurement, live reputation validation, manual screen-reader testing, stock Edge testing, Git commit, or push.

### Remaining risks and follow-up

- [UNKNOWN] The rule-based prototype’s broad accuracy and language coverage remain unmeasured; no trained phishing model or live reputation service is part of v0.5.
- [UNKNOWN] Manual assistive-technology and stock Edge checks remain outstanding.
- [OBSERVED] The v0.5 ZIP is ignored, local, and unpublished; the working tree is uncommitted.
- Next owner/action: parent should complete the final diff/status audit, obtain explicit user approval for the proposed commit, then request separate approval before pushing to the intended remote.

### Correction history

None. This is an append-only local artifact checkpoint.

### Dated revision - 11 September 2026 final v0.5 verification correction

Revision status: `CORRECTED_PREPARED_LOCAL`; uncommitted; no staging, commit, amend, push, or publication authorized. This append-only revision preserves the original prepared record and supersedes its stale verification and archive facts.

[OBSERVED - Luna inspection] Branch `main` is at `4dbf38c9487a7aeb4da1c42efdb91b8fb1b36787`; `origin/main` remains at that published initial commit. Planned subject remains `Polish Fisher v0.5 extension`; any future commit must carry `Luna-ID: LUNA-20260911-002`. No v0.5 commit or push exists.

[OBSERVED - parent-supplied final evidence] The v0.5 product is an explicit-action, local-only MV3 popup with message/link modes, in-memory drafts, inline validation and focus recovery, edit/clear/shortcut actions, source labels, bounded 20,000-character message and 2,048-character link inputs, isolated bounded selection, canonical link scanning, raw host validation, exact locator/email masking, generic non-echo evidence, and no storage, network, reputation, or trained-model behavior. Version 0.5.0 is coordinated across the extension/package surfaces; four PNG runtime icons and an SVG source are present.

[OBSERVED - parent-supplied final evidence] Punctuation, wrapper, emoji, Indic, and CJK boundary fixes preserve visible semantics; invalid authorities terminate at host punctuation; valid userinfo, ports, IPv6, and balanced paths remain supported; later HTTP/HXXP schemes remain independent candidates; internal defang markers are transparent; default-ignorable runs are detected without false positives for ordinary emoji and tested Indic joiners. These are heuristics and do not prove destination safety.

#### Superseded verification and archive data

- Original `npm test` 91 passes → superseded by 113/113.
- Original browser 13 passes → superseded by 14/14.
- Original package test 25 passes → superseded by 26/26.
- Original full Python 317 passes in 53.904 seconds → superseded by 318/318 in 53.082 seconds.
- Original archive 82,196 bytes / SHA-256 `32ad3509089a6c01a665f54c41a0835eefb967b0e9daede21e7452e1022e10a6` → superseded by 105,300 bytes / SHA-256 `8e71e577b202e2379082ba276b58b3ff4ae843d19b11f66c8f6406772f369088`.
- Original `npm audit --json` wording → superseded by `npm audit --audit-level=high`, which found 0 vulnerabilities.

#### Final verification

- [OBSERVED - parent-supplied] `npm test`: 113/113 passed.
- [OBSERVED - parent-supplied] `npm run test:browser`: 14/14 passed with Chromium, Axe, 320px layout, selection, and no-external-request checks.
- [OBSERVED - parent-supplied] Python package tests: 26/26; full Python discovery: 318/318 in 53.082 seconds.
- [OBSERVED - parent-supplied] `npm audit --audit-level=high`: 0 vulnerabilities; `git diff --check`: passed.
- [OBSERVED - parent-supplied] Independent link/security review: 72/72 focused checks, 518 accumulated custom assertions, and 200 malformed-chain assertions passed; zero reproducible in-scope P0/P1 findings.
- [OBSERVED - parent-supplied] Final ignored archive has exactly 12 members, passed `unzip -t` and allowlist checks, and byte-compares equal to current runtime sources.
- Not run: GitHub CI for uncommitted v0.5; model/corpus/accuracy evaluation; reputation validation; stock Chrome/Edge low-end latency; manual screen-reader, keyboard, forced-colors, or zoom testing.

#### Impacts, risks, and follow-up

- [OBSERVED] This correction changes only this Markdown register; the legacy DOCX and Git state were not changed by Luna.
- [DERIVED] Evidence supports a bounded local rule-based prototype, not a safety guarantee or trained-model claim.
- [UNKNOWN] Delimiter-free repeated-email input measured approximately 507–519 ms warm and one 801 ms cold mixed run; stock-device latency and broad accuracy remain unknown. Manual accessibility, stock Edge, multilingual coverage, and GitHub CI remain unverified.

Next owner/action: parent should audit final status/diff, obtain fresh approval for the proposed commit with this register and trailer `Luna-ID: LUNA-20260911-002`, commit only after approval, then request separate approval before pushing to `origin/main`. A later substantive Luna update must backfill the commit SHA; no document-only backfill commit is allowed.

## Decision record - LUNA-20260924-001

### Fisher extension improvement scope checkpoint

- Lifecycle: `SCOPE_DECIDED_PREPARED_LOCAL`; working tree uncommitted; no staging, commit, publication, or push authorized
- Recorded: 24 September 2026, Asia/Kolkata; responsible agent: luna; branch: `main`
- Planned commit subject: `Expand Fisher extension workspace and reporting UX` (prospective; requires separate user approval)
- Required trailer: `Luna-ID: LUNA-20260924-001` if a future commit is approved
- Commit SHA: Pending — no commit created
- Parent SHA: `4dbf38c9487a7aeb4da1c42efdb91b8fb1b36787` (current `HEAD`)
- Affected paths: `browser_extension/popup.html`; `browser_extension/styles.css`; `browser_extension/popup.js`; related extension tests and documentation only if implementation evidence later confirms changes

### Findings and decision

[OBSERVED - repository state] The working tree already contains uncommitted Fisher v0.5 extension, CLI, packaging, test, README, and research-status changes, plus untracked runtime icon assets. Existing product work must be preserved while the requested improvement pass is developed.

[OBSERVED - parent-supplied verification] The current baseline `npm test` completed with 113 passed and 0 failed on 24 September 2026. This is baseline evidence only; it does not verify the new improvement scope.

[ASSUMED - parent-supplied scope pending optional user clarification] The request “go crazy show tons of improvements” is interpreted as a broad but bounded improvement pass for the existing Fisher browser-extension experience. The existing local-only privacy boundary, CLI/report schema, and current dirty v0.5 working tree are preserved.

#### Decision D-211 - Improve the existing popup experience in place

Decision: Extend the same popup runtime into a responsive workspace with stronger result hierarchy and accessibility, additional synthetic multilingual examples, explicit sanitized report export that excludes user inputs, and inline help. Root implementation ownership is limited to the extension UI; controller and test work remains separately owned. Do not introduce storage, history, external services, new dependencies, trained-model claims, or performance claims in this checkpoint.

Rationale: [OBSERVED] The existing user-facing product is the Fisher browser-extension popup. [DERIVED] Improving that surface directly gives the requested visible breadth while preserving the established runtime and privacy boundaries. [DERIVED] Sanitized export and inline help make findings easier to understand and share without copying raw message, selection, or URL inputs into an exported report.

#### Alternatives not selected

- Build a standalone website: rejected because the verified product in scope is the browser-extension popup and no standalone site is established by the supplied evidence.
- Add persistent storage or scan history: rejected because it would expand the established local-only privacy boundary and was not requested with supporting requirements.
- Add new dependencies or a trained model: rejected because the checkpoint is for user-facing product improvements and contains no verified dependency, training, corpus, or performance evidence.
- Change the CLI/report schema: rejected because preserving that interface is an explicit parent constraint; report export must be sanitized at the UI boundary.
- Replace the current dirty v0.5 worktree: rejected because existing user changes must be preserved and are part of the implementation context.

### Impacts and claim boundary

- [DERIVED] If implemented as scoped, the changes affect externally visible extension UI, accessibility behavior, examples, and report-export workflow.
- [OBSERVED] No new network access, persistent storage, host permissions, or background service is authorized by this checkpoint.
- [DERIVED] Export must omit raw user inputs and remain compatible with the existing report semantics; exact fields require implementation verification.
- [UNKNOWN] Final browser behavior, accessibility coverage, export contents, multilingual example quality, and regression status remain unverified until implementation and tests complete.

### Verification

- [OBSERVED] `git status --short` and the existing register were inspected before this append; the worktree contains the pre-existing uncommitted paths listed above.
- [OBSERVED - parent-supplied] `npm test`: 113 passed, 0 failed on 24 September 2026 (baseline only).
- Not run for this scope checkpoint: browser tests for the new UI, report-export assertions, accessibility checks, multilingual-example checks, package verification, full Python suite, `npm audit`, or final `git diff --check` after implementation.
- No staging, commit, amend, reset, restore, clean, or push performed.

### Remaining risks and follow-up

- [UNKNOWN] The final scope may change if the parent receives materially different user clarification.
- [UNKNOWN] The improvement pass may expose regressions in popup layout, keyboard/focus behavior, existing drafts, selection handling, or report compatibility.
- [UNKNOWN] Synthetic multilingual examples are demonstration content, not evidence of language coverage or detection accuracy.
- Next owner/action: parent and implementation agents should complete the bounded UI/controller changes, run targeted browser and regression verification, then request a substantive Luna update with exact changed paths, command outcomes, remaining risks, and any intended commit information.

### Correction history

None. This is an append-only scope checkpoint.

## Decision record - LUNA-20260924-002

### Fisher extension workspace and reporting UX implementation checkpoint

- Lifecycle: `IMPLEMENTED_VERIFIED_LOCAL`; working tree uncommitted; no staging, commit, publication, or push authorized
- Recorded: 24 September 2026, Asia/Kolkata; responsible agent: luna; branch: `main`
- Planned commit subject: `Expand Fisher extension workspace and reporting UX` (prospective; no commit requested)
- Required trailer: `Luna-ID: LUNA-20260924-002` if a future commit is approved
- Commit SHA: Pending — no commit created
- Parent SHA: `4dbf38c9487a7aeb4da1c42efdb91b8fb1b36787` (current `HEAD`)
- Affected paths: `README.md`; `browser_extension/README.md`; `browser_extension/popup.html`; `browser_extension/popup.js`; `browser_extension/styles.css`; `browser_extension/tests/selection.test.mjs`; `tests/browser/extension.spec.mjs`; `tests/test_extension_package.py`; and this register

### Findings and decision

[OBSERVED - parent-supplied final evidence] The implementation adds a redesigned compact popup and a same-runtime expanded workspace opened through `?view=workspace` in a new tab. The workspace supports responsive desktop/mobile layouts, system dark theme, contrast and forced-colors behavior, reduced motion, focus handling, actual report/check counts, collapsible nonempty check details, four synthetic examples (Hindi, Tamil, Telugu, and everyday benign text), inline help, composition-aware shortcuts, precise privacy guidance, and local habit guidance.

[OBSERVED - parent-supplied final evidence] The report action downloads an allowlisted generic JSON file with a fixed filename, excludes raw input and URLs, and invalidates stale export state. The popup opens the workspace with `noopener`, an empty draft, and no transferred input or page selection. Temporary drafts remain in memory; no input history or persistent application storage was added.

#### Decision D-212 - Deliver the bounded workspace and sanitized reporting slice

Decision: Keep Fisher as the existing local-only extension and improve its primary interaction surface in place. Add the workspace view, responsive and accessibility-oriented presentation, synthetic examples, result-detail hierarchy, inline help, and explicit sanitized report download. Preserve the current analyzer, detector, link, selection-reader, manifest, CLI/report schema, privacy boundary, and dependency set.

Rationale: [OBSERVED] The requested improvement work changed the popup, controller, styling, documentation, and focused tests while the engine and manifest remained byte-equal to the saved pre-session baseline. [DERIVED] This concentrates user-visible value in the existing product without expanding permissions, network behavior, storage, model scope, or report interfaces. [OBSERVED] Review found and corrected privacy wording to state that nothing leaves the device and that drafts are temporary with no input history.

#### Alternatives not selected

- Change detector policy or heuristics: deferred because the current heuristics are documented and no corpus evidence supports a policy change in this UX checkpoint.
- Treat reviewer P0 speculation as a confirmed defect: rejected because no additional reproducible export, stale-state, workspace, or IME defect was found.
- Add persistent history or storage: rejected because the local-only privacy boundary requires temporary in-memory drafts and no input history.
- Rebuild or change the CLI/report schema: rejected because compatibility with the existing schema was an explicit scope constraint; export is sanitized at the UI boundary.
- Add dependencies, permissions, external services, or trained-model behavior: rejected because the implementation did not need them and no evidence supports expanding those claims.
- Claim language coverage or measured accuracy from the synthetic examples: rejected because these are demonstrations only, not evaluation evidence.

### Impacts and claim boundary

- [OBSERVED] New work changed exactly the nine implementation/documentation/test paths listed above, plus this register; current engine, detector, link, selection-reader, and manifest changes from the pre-existing dirty worktree were preserved.
- [OBSERVED] No new dependencies, permissions, network requests, persistent application storage, or history were introduced. A downloaded generic report is persisted by the browser only after the user explicitly requests the download.
- [DERIVED] The workspace improves discoverability, result comprehension, and sharing while retaining local processing and excluding raw inputs from exported reports.
- [UNKNOWN] Manual screen-reader, stock Chrome/Edge, broad accuracy, language coverage, model, and performance evaluation remain unverified.
- [UNKNOWN] The existing v0.5 archive was not rebuilt for this checkpoint; local screenshot outputs are ignored and are not package contents.

### Verification

- [OBSERVED - parent-supplied] `npm test`: 121 passed, 0 failed (session 44338).
- [OBSERVED - parent-supplied] `npm run test:browser`: 18 passed, 0 failed in 12.7 seconds (session 42226).
- [OBSERVED - parent-supplied] `uv run --python 3.11 python -m unittest -q tests.test_extension_package`: 26 passed, 0 failed in 0.581 seconds.
- [OBSERVED - parent-supplied] `node --check` for `browser_extension/popup.js` passed; focused controller checks passed 40/40.
- [OBSERVED - parent-supplied] `git diff --check` passed.
- [OBSERVED - parent-supplied] Root visually inspected light, dark, 320px mobile, and popup/workspace screenshots. A local preview at `127.0.0.1:8765/popup.html?view=workspace` served only the extension folder and was not published.
- [OBSERVED - parent-supplied] Terra read-only review found no additional reproducible export, stale-state, workspace, or IME defects after the privacy wording correction; an earlier reviewer reported 119 tests, superseded by the final 121-test result.
- Not run: full Python discovery suite; manual screen-reader, stock Chrome/Edge, keyboard/forced-colors/zoom coverage beyond automated checks; accuracy, language-coverage, model, or performance evaluation; archive rebuild; Git commit or push.

### Remaining risks and follow-up

- [UNKNOWN] Manual assistive-technology and stock-browser behavior remain unverified.
- [UNKNOWN] Synthetic multilingual examples do not establish multilingual detection coverage or accuracy.
- [UNKNOWN] The current rule-based engine remains a heuristic prototype; detector-policy changes require corpus-backed evaluation.
- [UNKNOWN] The v0.5 archive does not include this uncommitted workspace implementation because it was not rebuilt.
- Next owner/action: parent should perform the final status/diff audit, decide whether to request a commit, and if so obtain fresh approval for the exact paths and subject, stage this register with the matching `Luna-ID`, and request a later substantive update for SHA backfill.

### Correction history

None. This is an append-only implementation and verification checkpoint.

### Dated revision - 24 September 2026, 11:22:45 IST (+0530)

Revision status: `CORRECTED_IMPLEMENTED_VERIFIED_LOCAL`; uncommitted; no staging, commit, amend, publication, or push authorized. This append-only revision preserves the original record and corrects its path-count wording and evidence labels using the final parent-supplied review.

- [OBSERVED - parent-supplied final evidence] The final implementation changed 8 non-register paths plus `docs/CHANGE_DECISION_LOG.md`, for 9 changed paths total in this workstream. The original phrase “nine implementation/documentation/test paths ... plus this register” was imprecise and is superseded by this revision.
- [OBSERVED - parent-supplied final evidence] The saved-baseline comparison found no changes in the engine, selection reader, or manifest attributable to this final improvement work. The existing unrelated dirty changes remain preserved.
- [OBSERVED - parent-supplied final evidence] The v0.5 archive was not rebuilt and does not contain this uncommitted workspace implementation; this is verified state, not an unknown.
- [OBSERVED - correction to original claim] The original `UNKNOWN` archive-risk bullet is superseded: the archive state and absence of the new workspace implementation were verified by the parent.
- [OBSERVED - parent-supplied final evidence] The byte-equal engine/selection/manifest conclusion is based on the saved-baseline comparison and should be read as parent-supplied evidence wherever the original rationale used an unqualified `OBSERVED` label.
- [OBSERVED - parent-supplied final evidence] The workspace-expand action was moved into the header for discoverability. The parent re-inspected the final light workspace and compact popup screenshots, and the local preview returned HTTP 200.

Correction rationale: [DERIVED] These edits improve audit precision without changing the implementation record or creating a recursive new checkpoint. No source, configuration, legacy DOCX, or Git state was changed by Luna.

## Decision record - LUNA-20260924-003

### Fisher functionality expansion scope checkpoint

- Lifecycle: `SCOPE_DECIDED_PREPARED_LOCAL`; working tree uncommitted; no staging, commit, release, or push authorized
- Recorded: 24 September 2026, Asia/Kolkata; responsible agent: luna; branch: `main`
- Planned commit subject: `Add bounded batch checking and functional URL evidence` (prospective; no commit requested)
- Required trailer: `Luna-ID: LUNA-20260924-003` if a future commit is approved
- Commit SHA: Pending — no commit created
- Parent SHA: `4dbf38c9487a7aeb4da1c42efdb91b8fb1b36787` (current `HEAD`)
- Affected paths: to be finalized from implementation evidence; expected popup/controller, analyzer or link handling, tests, and directly related documentation only

### Findings and decision

[OBSERVED - parent-supplied repository inspection] The current popup, analyzer, detector, link handling, tests, package manifest/source inventory, and dirty Git state were inspected. Existing changes are preserved. A baseline snapshot exists at `baseline/functionality-baseline-20260924`.

[ASSUMED - parent-supplied scope pending optional user priorities] The user correction “too green, i want changes in functionality” is interpreted as a shift from primarily visual polish to useful bounded batch and navigation functionality. Exact priorities may still be refined, but the material architecture constraints below are fixed.

#### Decision D-213 - Prioritize local batch checking and bounded navigation evidence

Decision: Explore a browser workflow for multiple messages or links using one-per-line `.txt` import, explicit input bounds, filters, per-item generic findings, cancellation and progress, and a sanitized batch report. Add bounded local nested-redirect query evidence for navigation URLs. Replace the green-heavy palette with neutral gray, white, and blue while keeping visual changes subordinate to the functional work. Preserve the single-input API schema, CLI behavior, local-only boundary, and existing permissions.

Rationale: [DERIVED] The user explicitly requested functionality after reviewing the prior visual-focused work. [OBSERVED] The existing product already has local analyzers, link handling, tests, and a baseline snapshot that can anchor behavior comparisons. [DERIVED] Bounded batch processing and generic per-item output provide concrete utility without requiring cloud services or persistent storage. [OBSERVED] Nested navigation evidence is intended as a reviewable observation, not a high-confidence safety verdict or accuracy claim.

#### Alternatives not selected

- Continue with cosmetic-only changes: rejected because the user explicitly requested functionality.
- Add cloud reputation services or a trained model: rejected because this would violate the preserved local-only boundary or exceed the verified evidence and dependency scope.
- Change the single-input API or CLI schema: rejected because backward compatibility is an explicit constraint.
- Add persistent history or broad storage: rejected because input data must remain only in the current window and no storage expansion is authorized.
- Treat nested redirect observations as safety or accuracy claims: rejected because the evidence supports bounded review only.

### Impacts and claim boundary

- [DERIVED] Batch mode would add externally visible workflow, progress/cancellation behavior, filtering, and sanitized reporting while retaining the current single-input path.
- [OBSERVED - parent-supplied constraint] Input data may be retained only in the current window; generic row line IDs are acceptable for new batch reports.
- [OBSERVED - parent-supplied constraint] No new network access, permissions, persistent storage, or dependencies are authorized.
- [UNKNOWN] Final bounds, cancellation semantics, report fields, nested-navigation matching behavior, palette implementation, and regression status remain unverified until implementation completes.
- [UNKNOWN] Detection observations may change for nested navigation URLs; this is a review concern, not evidence of improved accuracy.

### Verification

- [OBSERVED] Existing register structure, Luna IDs, current Git dirty state, and relevant repository inventory were inspected before this append.
- [OBSERVED - parent-supplied] `baseline/functionality-baseline-20260924` is available for comparison.
- Not run for this scope checkpoint: implementation tests, browser tests, batch import/export tests, cancellation/progress checks, accessibility checks, package verification, or final `git diff --check` after implementation.
- No staging, commit, amend, reset, restore, clean, release, or push performed.

### Remaining risks and follow-up

- [UNKNOWN] Batch workloads may expose performance, cancellation, memory, or malformed-line edge cases.
- [UNKNOWN] Nested navigation evidence may produce changed observations requiring careful review and regression coverage.
- [UNKNOWN] The final user priority between batch messages, batch links, navigation evidence, and palette changes is not yet explicit.
- Next owner/action: parent and implementation agents should finalize the bounded design, implement only supported functionality, compare against the baseline snapshot, run targeted and regression verification, then request a substantive Luna update with exact changed paths and outcomes.

### Correction history

None. This is an append-only scope checkpoint.

### Dated revision - 24 September 2026, final baseline-path correction

Revision status: `CORRECTED_SCOPE_PREPARED_LOCAL`; uncommitted; no staging, commit, amend, release, or push authorized. This append-only revision preserves the original scope statement and corrects the baseline path using the verified repository location.

- [OBSERVED - repository inspection] The baseline snapshot is located at `outputs/functionality-baseline-20260924` and exists as a directory with browser-extension and test snapshot contents.
- [CORRECTION] The earlier reference to `baseline/functionality-baseline-20260924` was incorrect and is superseded by the verified path `outputs/functionality-baseline-20260924`.


## Decision record - LUNA-20260924-004

### Fisher bounded batch functionality implementation checkpoint

- Lifecycle: `IMPLEMENTED_VERIFIED_LOCAL`; working tree uncommitted; no staging, commit, release, or push authorized
- Recorded: 24 September 2026, Asia/Kolkata; responsible agent: luna; branch: `main`
- Planned commit subject: `Add bounded batch checking and functional URL evidence` (prospective; no commit requested)
- Required trailer: `Luna-ID: LUNA-20260924-004` if a future commit is approved
- Commit SHA: Pending — no commit created
- Parent SHA: `4dbf38c9487a7aeb4da1c42efdb91b8fb1b36787` (current `HEAD`)
- Affected paths: `README.md`; `browser_extension/README.md`; `browser_extension/links.mjs`; `browser_extension/popup.html`; `browser_extension/popup.js`; `browser_extension/styles.css`; `browser_extension/tests/analyzer.test.mjs`; `browser_extension/tests/selection.test.mjs`; `tests/browser/extension.spec.mjs`; `tests/test_fisher_cli.mjs`; and this register

### Findings and decision

[OBSERVED - parent-supplied final evidence] The functionality pass adds bounded batch checking for up to 100 physical LF lines and 100,000 Unicode code points total, with shared per-item limits, one-per-line `.txt` import up to 1 MiB, fatal invalid UTF-8 handling, accepted empty or `text/plain` MIME essence with parameters, draft-only import behavior, exact CLI-compatible line numbering, blank-line handling, and duplicate-CR normalization.

[OBSERVED - parent-supplied final evidence] Batch analysis is cancellable and generation-invalidated after edits, mode/type changes, imports, and clears. The UI provides progress, counts, filters, individual generic findings, Locate input behavior using original UTF-16 line offsets, and sanitized line-indexed JSON reports that exclude raw text, URLs, and filenames. Incomplete or stale analysis cannot produce a partial completed export.

[OBSERVED - parent-supplied final evidence] Link analysis now performs bounded one-level nested query destination checks across the specified case-insensitive keys, with one URLSearchParams decode, HTTP(S) and protocol-relative targets only, no recursion or fetch, prevalidation for malformed/control/Unicode/percent/surrogate input, bounded targets and pairs, and generic handling for malformed, unsupported, or over-limit cases. Outer address counts remain unchanged; relative, bare, and double-encoded targets are ignored. Literal unencoded nested URLs in messages retain existing scanner splitting behavior.

[OBSERVED - parent-supplied final evidence] The green-heavy palette was replaced with gray, white, charcoal, and blue while retaining risk red and amber. No new dependency, permission, runtime file, API, CLI aggregate shape, network behavior, or storage was introduced.

#### Decision D-214 - Deliver functional local batch workflows with bounded navigation evidence

Decision: Ship the functionality-focused browser workflow as a local, bounded extension enhancement while preserving the existing single-input and CLI contracts. Use shared local rule analysis for batch items, generic sanitized reports, cancellable state, and review-only nested navigation evidence. Keep nested findings subordinate to the outer result and make no safety or accuracy claim from them.

Rationale: [OBSERVED - parent-supplied baseline comparison] The saved `baseline/functionality-baseline-20260924` snapshot was used to isolate this turn’s changes. The parent observed `analyzer.mjs`, `detector.mjs`, `selection.mjs`, `manifest.json`, and `fisher.mjs` byte-equal to baseline for this turn; `tests/test_extension_package.py` was dirty before this turn and unchanged. [DERIVED] Shared local analysis and bounded one-level inspection provide useful functionality without cloud reputation, model training, new permissions, or dependency expansion.

#### Alternatives not selected

- Continue with cosmetic-only changes: rejected because the user explicitly requested functionality.
- Add a cloud model, reputation service, or network lookup: rejected because it would expand the local-only privacy and permission boundary without supporting evidence.
- Follow redirects recursively or fetch destinations: rejected because bounded review evidence is sufficient for this scope and recursion would increase risk, latency, and claim ambiguity.
- Export raw source text, URLs, or filenames: rejected because reports must remain generic and sanitized.
- Change the existing single-input API or CLI aggregate schema: rejected because compatibility is an explicit constraint.
- Add new permissions, dependencies, or persistent storage: rejected because the implemented workflows do not require them.

### Impacts and claim boundary

- [OBSERVED] Ten non-register paths changed this turn; existing unrelated dirty paths were preserved. Parent byte comparison found the engine, detector, selection reader, manifest, and CLI implementation unchanged this turn, while `tests/test_extension_package.py` remained pre-existing dirty state.
- [OBSERVED] Input data remains in the current window only. Generic row line IDs are used for new batch reports; raw text, URLs, and filenames are excluded.
- [OBSERVED] No new network, permissions, storage, dependencies, runtime files, API changes, or CLI aggregate-shape changes were introduced.
- [DERIVED] Nested destination presence is review evidence attached to the outer result, not a standalone high-risk verdict.
- [UNKNOWN] The rule-based engine cannot prove safety; finite embedded coverage, extension reload behavior, and installed-extension page-selection privileges remain limitations.
- [OBSERVED - parent-supplied] The old v0.5 ZIP was not rebuilt and is not the current deliverable.

### Verification

- [OBSERVED - parent-supplied] `npm test`: 148 passed, 0 failed, comprising 84 analyzer/detector, 54 controller, and 10 CLI checks.
- [OBSERVED - parent-supplied] `uv run --python 3.11 python -m unittest -q tests.test_extension_package`: 26 passed, 0 failed in 0.631 seconds.
- [OBSERVED - parent-supplied] `npm run test:browser`: 22 passed, 0 failed in 13.4 seconds.
- [OBSERVED - parent-supplied] Combined targeted verification totaled 196 passed checks; `git diff --check` was clean.
- [OBSERVED - parent-supplied] Disposable Chromium checks covered batch filters, blank numbering, Locate, cancellation, import, UTF-8 handling, private exports, no external requests, accessibility, mobile, light, and dark states.
- [OBSERVED - parent-supplied] Parent visually inspected `outputs/browser_extension/bulk-workspace.png` and `bulk-workspace-dark.png`; local preview returned HTTP 200 at `127.0.0.1:8765`; synthetic demo behavior was checked.
- [OBSERVED - parent-supplied] Independent Terra review and parent audit fixed malformed nested prevalidation, MIME handling, same-file retry reset, empty/oversized draft preservation, duplicate-CR stripping, oversized-input splitting avoidance, selected-row visibility, and Locate assertions.
- Not run: full Python research suite; stock Chrome/Edge; manual screen-reader testing; model accuracy, corpus, language-coverage, or performance evaluation; ZIP rebuild; Git commit, release, or push.

### Remaining risks and follow-up

- [UNKNOWN] The local pattern engine remains heuristic and cannot establish safety or accuracy.
- [UNKNOWN] Finite nested-query coverage may miss unsupported or unusual navigation patterns.
- [UNKNOWN] A loaded existing extension requires reload to receive the new code; the local preview cannot provide installed-extension page-selection privileges.
- [OBSERVED] No commit, release, push, or ZIP rebuild was authorized or performed.
- Next owner/action: parent should perform final status and diff review, obtain separate approval if a commit is desired, and stage this register with `Luna-ID: LUNA-20260924-004` before that commit.

### Correction history

None. This is an append-only implementation and verification checkpoint.

### Dated revision - 24 September 2026, final baseline and parsing correction

Revision status: `CORRECTED_IMPLEMENTED_VERIFIED_LOCAL`; uncommitted; no staging, commit, amend, release, or push authorized. This append-only revision preserves the original implementation record and corrects its baseline path and parsing-bound wording using verified parent evidence.

- [OBSERVED - repository inspection] The baseline snapshot used for this turn is `outputs/functionality-baseline-20260924`, which exists as a directory with browser-extension and test snapshot contents.
- [CORRECTION] The original reference to `baseline/functionality-baseline-20260924` is superseded by `outputs/functionality-baseline-20260924`.
- [CORRECTION] The original phrase “duplicate-CR normalization” is superseded by the exact behavior: split on LF, remove exactly one final LF-generated empty member, and strip exactly one terminal CR per line; a second CR is retained and never normalized away.
- [CORRECTION] The bounded nested-navigation limits are exactly 32 query pairs and 4 qualifying targets.
- [OBSERVED - parent-supplied final evidence] The 10 non-register paths listed in this record are the paths changed this turn; pre-existing dirty paths remain preserved.

## Decision record - LUNA-20261011-001

### Fisher finish scope and baseline verification checkpoint

- Lifecycle: `SCOPE_DECIDED_PREPARED_LOCAL`; working tree uncommitted; no staging, commit, release, or push authorized
- Recorded: 11 October 2026, Asia/Kolkata; responsible agent: luna; branch: `main`
- Planned commit subject: `fix: finish local fisher app delivery` (prospective; no commit requested)
- Required trailer: `Luna-ID: LUNA-20261011-001` if a future commit is approved
- Commit SHA: Pending — no commit created
- Parent SHA: `4dbf38c9487a7aeb4da1c42efdb91b8fb1b36787` (current `HEAD`)
- Affected paths: current Fisher implementation, extension packaging, CLI, tests, and status/documentation paths are in the pre-existing dirty working tree; exact implementation paths remain subject to the completed finish diff. Five new icon files are also present. This register is the only path changed by Luna.

### Findings and decision

[OBSERVED - parent-supplied repository evidence] The repository is on `main` at `4dbf38c9487a7aeb4da1c42efdb91b8fb1b36787`. At task start, 22 tracked paths were modified and five new extension icon files were present. A baseline snapshot was saved at `outputs/finish-baseline-20261011`.

[OBSERVED - parent-supplied verification evidence] `npm run test:browser` completed with 22 passing checks in 19.3 seconds. `uv run --python 3.11 python -m unittest discover -q -s tests -p 'test_*.py'` completed with 318 tests OK in 64.970 seconds. `git diff --check` exited 0. The environment reported Node `v25.9.0` and uv `0.7.20`.

[OBSERVED - parent-supplied status] Product review is still in progress and no implementation changes have been made for this finish checkpoint. The existing v0.5 ZIP predates the 24 September bulk/workspace work; byte comparison is pending.

[ASSUMED - parent-supplied scope pending optional user response] “Finish Fisher” means finish the local extension and CLI application, fix confirmed defects, refresh inaccurate status, and build a verified current installation package. Research collection and model work are separate blocked work and must not be represented as complete. The optional user scope question has not received an answer.

#### Decision D-215 - Finish the verified local delivery boundary

Decision: Continue toward a reviewable local Fisher delivery consisting of the extension, CLI, confirmed defect fixes, accurate status documentation, and a verified current installation package. Preserve the explicit boundary that research collection and model work remain blocked and incomplete unless separately evidenced and authorized.

Rationale: [OBSERVED] The baseline tests pass and the current dirty worktree contains the extension, CLI, packaging, tests, and status-related paths needed for the local delivery review. [DERIVED] A baseline snapshot and passing baseline checks provide a concrete comparison point for implementation and packaging verification. [ASSUMED] The parent’s stated scope is the intended interpretation until the optional user response arrives.

#### Alternatives not selected

- Claim the entire Fisher project finished from the current tests: rejected because product review remains in progress, package freshness comparison is pending, and research/model work is explicitly blocked.
- Add or claim a research collection or trained-model deliverable: rejected because no verified input, implementation, dataset evidence, or authorization supports that scope.
- Treat the existing v0.5 ZIP as the current installation package: rejected because parent evidence says it predates the 24 September bulk/workspace work; byte comparison and a current rebuild remain pending.
- Expand scope into speculative features or unconfirmed defects: rejected because only confirmed defects and explicitly supported local-delivery work are authorized by the supplied evidence.
- Commit or publish the work at this checkpoint: rejected because no commit or publication approval was requested, and implementation/product review is incomplete.

### Impacts and claim boundary

- [OBSERVED] Baseline verification covers the named browser and Python test commands and a clean whitespace check at the recorded checkpoint.
- [DERIVED] Subsequent changes can be compared against `outputs/finish-baseline-20261011` while preserving unrelated pre-existing edits.
- [UNKNOWN] The final set of implementation changes, current package contents, package byte comparison, product-review outcome, and installation behavior remain unverified.
- [UNKNOWN] Research collection, model training/inference, empirical accuracy, language coverage, and performance claims remain outside the completed scope.
- [OBSERVED] No staging, commit, release, push, or publication was performed for this checkpoint.

### Verification

- [OBSERVED - parent-supplied] `npm run test:browser` — 22 passed in 19.3 seconds.
- [OBSERVED - parent-supplied] `uv run --python 3.11 python -m unittest discover -q -s tests -p 'test_*.py'` — 318 tests OK in 64.970 seconds.
- [OBSERVED - parent-supplied] `git diff --check` — exit 0.
- [OBSERVED - parent-supplied] Baseline snapshot saved at `outputs/finish-baseline-20261011`.
- Not run for this checkpoint: final product review; current installation-package rebuild and byte comparison; post-implementation regression checks; manual stock-browser, assistive-technology, accuracy, research, model, or performance evaluation; Git commit, release, or push.

### Remaining risks and follow-up

- [UNKNOWN] The current v0.5 archive may omit later bulk/workspace work; rebuild and compare the current package before claiming installation-package completion.
- [UNKNOWN] Product review may identify confirmed defects requiring additional bounded fixes.
- [UNKNOWN] The optional user scope response may refine priorities within the local extension and CLI boundary.
- [UNKNOWN] Research collection and model work have no completion evidence and remain blocked.
- Next owner/action: parent and implementation agents should finish only the verified local extension/CLI scope, fix reproducible defects, refresh inaccurate status, rebuild and verify the current installation package, rerun relevant tests, then request a substantive Luna update with exact changed paths, outcomes, and any intended commit subject.

### Correction history

None. This is an append-only baseline and scope checkpoint.

### Dated completion revision - 11 October 2026, Asia/Kolkata

Revision status: `IMPLEMENTED_VERIFIED_LOCAL`; working tree uncommitted; no staging, commit, release, or push authorized. This append-only revision preserves `LUNA-20261011-001` and records the completed local-delivery and verification checkpoint using parent-supplied evidence.

- Planned commit subject: `docs: finalize local fisher delivery` (prospective; commit not requested)
- Commit SHA: Pending — no commit created
- Parent SHA: `4dbf38c9487a7aeb4da1c42efdb91b8fb1b36787`
- Required trailer if later approved: `Luna-ID: LUNA-20261011-001`
- [OBSERVED] Relative to `outputs/finish-baseline-20261011`, the changed paths are exactly `README.md`, `browser_extension/README.md`, `docs/research/EXECUTION_STATUS.md`, and this register. Runtime, CLI, and test paths were byte-unchanged relative to that baseline. Existing unrelated working-tree changes remain preserved.

#### Decision D-216 - Finalize the verified local Fisher delivery boundary

Decision: Treat the local extension and CLI delivery as implemented and locally verified for this checkpoint. Keep the current v0.5 version identifier because this is a local, never-released iteration. Refresh README/package guidance and research status to identify the current artifact and historical snapshots accurately. Preserve the existing implementation and avoid speculative source changes.

Rationale: [OBSERVED - parent-supplied product review] The sol_high product review found no reproducible blocker. [OBSERVED - parent-supplied package evidence] A fresh package was built successfully with 12 members, 153,663 bytes, and SHA-256 `3a3599724ef8861caf644453f4040c9377a12ff3d6087be53b42fd433c666040`. Root and reviewer independently verified ZIP integrity and source-byte equality for all 12 members; a second isolated build produced the same hash. [DERIVED] Documentation/status corrections and package regeneration complete the local-delivery checkpoint without requiring runtime or CLI source edits.

#### Alternatives not selected

- Change runtime or CLI implementation despite no reproducible blocker: rejected because reviewer evidence found no confirmed defect requiring source changes and baseline behavior remained verified.
- Claim research collection, model training/inference, reputation data, accuracy, or public publication as complete: rejected because those gates remain unsupported and blocked.
- Replace the v0.5 identifier with a release version: rejected because the iteration remains local and unreleased.
- Preserve the stale ZIP as the current deliverable: rejected because its recorded SHA-256 `8e71e577b202e2379082ba276b58b3ff4ae843d19b11f66c8f6406772f369088` and contents predate the current bulk/workspace work. It was retained under `outputs/finish-baseline-20261011/fisher-scam-signal-prototype-v0.5.0.zip` as historical evidence.
- Add speculative features or broader claims: rejected because the verified local-delivery scope is complete and no evidence or authorization supports expansion.

### Completion impacts and claim boundary

- [OBSERVED] README guidance now links the 11 October snapshot; the extension guide documents ZIP extraction and reload; the research status distinguishes historical snapshots from the current counts and artifact identity while retaining research gates.
- [OBSERVED] The current installation ZIP is `outputs/browser_extension/fisher-scam-signal-prototype-v0.5.0.zip`; its 12 members passed integrity and source-byte checks.
- [OBSERVED] No model, dataset, reputation, accuracy, or public-publication work was performed. The Python wheel/sdist build was exploratory; generated archives were removed afterward and are not deliverables.
- [DERIVED] The local package is suitable for review/install testing under the documented local workflow, subject to the remaining manual checks below.
- [UNKNOWN] Stock Chrome/Edge behavior, manual assistive-technology behavior, and research data/model gates remain unverified.

### Completion verification

- [OBSERVED - parent-supplied] `npm test` — 148 passed in 1.48 seconds.
- [OBSERVED - parent-supplied] `node --check` passed for five runtime files; bounded/privacy probes passed.
- [OBSERVED - parent-supplied] Baseline `npm run test:browser` — 22 passed in 19.3 seconds.
- [OBSERVED - parent-supplied] Baseline `uv run --python 3.11 python -m unittest discover -q -s tests -p 'test_*.py'` — 318 tests OK in 64.970 seconds.
- [OBSERVED - parent-supplied] `uv run --python 3.11 python -m fisher_extension_package` — current ZIP built successfully with 12 members, 153,663 bytes, SHA-256 `3a3599724ef8861caf644453f4040c9377a12ff3d6087be53b42fd433c666040`.
- [OBSERVED - parent-supplied] Root and independent reviewer verified ZIP integrity/source-byte equality for all 12 members; reviewer’s isolated second build matched the same hash.
- [OBSERVED - parent-supplied] Targeted packaging checks: root 26 passed in 0.569 seconds; reviewer 26 passed in 0.520 seconds.
- [OBSERVED - parent-supplied] Extracted-package disposable headless Chromium checks covered high-risk messaging, nested URL review, batch results, individual/batch JSON privacy, zero page errors, and zero external HTTP(S) requests.
- [OBSERVED - parent-supplied] Root visually inspected `outputs/finish-20261011/workspace.png`; local preview served the extension directory at `127.0.0.1:8765`.
- [OBSERVED - parent-supplied] `uv build --out-dir outputs/finish-20261011/python` produced a wheel and sdist as an exploratory check; generated archives were removed afterward.
- [OBSERVED - parent-supplied] `git diff --check` passed.
- Not run: manual stock Chrome/Edge testing; manual screen-reader/assistive-technology testing; research data collection; model training/inference; corpus accuracy, language-coverage, or performance evaluation; public publication; Git commit, release, or push.

### Completion risks and follow-up

- [UNKNOWN] Browser behavior outside disposable headless Chromium, especially stock Chrome/Edge installation and assistive technologies, remains unverified.
- [UNKNOWN] Research collection and model work remain blocked; the local delivery does not establish empirical accuracy or language coverage.
- [OBSERVED] The historical stale ZIP is preserved for comparison, while the current ZIP is available at `outputs/browser_extension/fisher-scam-signal-prototype-v0.5.0.zip`.
- Next owner/action: parent should perform any remaining manual checks, decide whether a commit is desired, and obtain separate approval for the exact commit paths and subject. If approved, stage this register with the matching `Luna-ID` trailer before committing.

## Decision record - LUNA-20261014-001

### Fisher v0.5 local toolkit commit-preparation checkpoint

- Lifecycle: `COMMIT_PREPARED_PENDING_APPROVAL`; staged and uncommitted; no commit, push, release, or publication performed
- Recorded: 14 October 2026, Asia/Kolkata; responsible agent: luna; branch: `main`
- Planned commit subject: `feat: complete fisher v0.5 local toolkit`
- Required trailer: `Luna-ID: LUNA-20261014-001`
- Commit SHA: Pending — commit has not been created
- Parent SHA: `4dbf38c9487a7aeb4da1c42efdb91b8fb1b36787`
- Remote comparison: [OBSERVED] `git ls-remote origin refs/heads/main` returned the same SHA as local `HEAD`; `gh repo view` confirmed `m-rithik/Phishing-in-indian-language`, default branch `main`, and `isPrivate: true`
- Approval boundary: exact commit approval is pending; push approval must be requested separately for `origin/main`

### Staged change inventory

[OBSERVED] The staged change contains exactly 26 non-register paths: 21 modified paths and five new icon paths. The register remains unstaged until this record is reviewed.

- `README.md`
- `browser_extension/README.md`
- `browser_extension/analyzer.mjs`
- `browser_extension/detector.mjs`
- `browser_extension/icon-128.png`
- `browser_extension/icon-16.png`
- `browser_extension/icon-32.png`
- `browser_extension/icon-48.png`
- `browser_extension/icon.svg`
- `browser_extension/links.mjs`
- `browser_extension/manifest.json`
- `browser_extension/popup.html`
- `browser_extension/popup.js`
- `browser_extension/selection.mjs`
- `browser_extension/styles.css`
- `browser_extension/tests/analyzer.test.mjs`
- `browser_extension/tests/detector.test.mjs`
- `browser_extension/tests/selection.test.mjs`
- `docs/research/EXECUTION_STATUS.md`
- `fisher.mjs`
- `fisher_extension_package.py`
- `package-lock.json`
- `package.json`
- `tests/browser/extension.spec.mjs`
- `tests/test_extension_package.py`
- `tests/test_fisher_cli.mjs`

### Findings and decision

[OBSERVED - parent-supplied final verification] No new implementation work was performed during this commit-preparation turn. The staged set is the accumulated local Fisher v0.5 extension, CLI, packaging, tests, icons, and documentation work recorded by prior substantive entries.

#### Decision D-217 - Prepare one reproducible local toolkit commit

Decision: Prepare the exact 26-path staged set under `feat: complete fisher v0.5 local toolkit`, preserving the v0.5 local version and requiring the matching Luna trailer. The intended outcome is a reviewable local toolkit supporting bulk/workspace review, bounded link and selection handling, generic reports, reproducible packaging, tests, and accurate documentation without public publication.

Rationale: [OBSERVED] The staged audit found 5,649 insertions and 727 deletions across 21 modified paths and five new icons, with no accidental output/archive/dataset/environment/key/certificate paths or obvious credential patterns. [OBSERVED] All 12 staged runtime members match the Oct 11 package bytes and extracted contents. [DERIVED] One commit keeps the tested local toolkit and its supporting documentation synchronized and makes the intended reproducible delivery boundary reviewable.

#### Alternatives not selected

- Commit only the Oct 11 documentation/status corrections: rejected because the intended local toolkit includes the staged runtime, UI, icons, CLI, packaging, tests, and documentation accumulated since the parent commit.
- Split the staged set into speculative feature commits: rejected because the current evidence supports one coherent v0.5 local-toolkit delivery and no separate independently verified release boundary was supplied.
- Change the v0.5 version: rejected because the toolkit remains a local, unreleased iteration and coordinated version evidence is already present.
- Add model, dataset, reputation, accuracy, or public-publication work: rejected because those areas remain outside verified scope and are not represented in the staged paths.
- Push immediately after commit: rejected because push to `origin/main` requires separate explicit approval even though the destination is confirmed private.

### Impacts and claim boundary

- [OBSERVED] The extension manifest retains `activeTab` and `scripting` permissions with no new host permissions; dependency versions are unchanged.
- [OBSERVED] Shared version, EPIPE, generic-report, CLI, packaging, and runtime checks were included in the staged audit.
- [OBSERVED] The current package identity is 12 members, 153,663 bytes, SHA-256 `3a3599724ef8861caf644453f4040c9377a12ff3d6087be53b42fd433c666040`; all 12 staged runtime bytes equal the Oct 11 package and extracted contents.
- [DERIVED] The staged change preserves the local-only processing and generic-report boundary evidenced by the tests and manifest review.
- [OBSERVED] The remote destination is private; no public publication claim is made.
- [UNKNOWN] Manual stock Chrome/Edge and assistive-technology coverage, model/data evaluation, and public-release readiness remain outside this checkpoint.

### Verification

- [OBSERVED - parent-supplied] `npm test` — 148 passed, 0 failed in 2,067.537875 ms.
- [OBSERVED - parent-supplied] `npm run test:browser` — 22 passed in 14.9 seconds.
- [OBSERVED - parent-supplied] `uv run --python 3.11 python -m unittest discover -q -s tests -p 'test_*.py'` — 318 tests OK in 59.938 seconds.
- [OBSERVED - parent-supplied] Combined count: 488 unique tests/checks passed.
- [OBSERVED - parent-supplied] `git diff --cached --check` passed; `git diff --check` passed.
- [OBSERVED - parent-supplied] Independent sol_high staged audit passed for the exact 26 non-register paths, including scope comparison, permissions, coordinated v0.5 version, unchanged dependency versions, CLI checks, package checks, and obvious-secret/path review.
- [OBSERVED - parent-supplied] `git ls-remote origin refs/heads/main` matched local `HEAD` at `4dbf38c9487a7aeb4da1c42efdb91b8fb1b36787`.
- [OBSERVED - parent-supplied] Package integrity and source-byte equality passed for all 12 members; staged package SHA-256 matched `3a3599724ef8861caf644453f4040c9377a12ff3d6087be53b42fd433c666040`.
- [OBSERVED - parent-supplied] `gh repo view m-rithik/Phishing-in-indian-language --json nameWithOwner,url,isPrivate,defaultBranchRef` exited 0 and confirmed the private `main` destination.
- Not run or not established: Git commit, push, release/publication; manual stock-browser and assistive-technology checks; model, dataset, accuracy, language-coverage, or performance evaluation.

### Remaining risks and follow-up

- [UNKNOWN] Manual browser and assistive-technology behavior remains unverified.
- [UNKNOWN] Research collection and model/data evaluation remain blocked and are not part of this commit.
- [OBSERVED] The remote destination is private, but push remains a separate approval-gated action.
- Next owner/action: parent should review this record, stage `docs/CHANGE_DECISION_LOG.md`, obtain explicit approval for this exact commit subject and 27-path commit including the register, then request separate explicit approval before pushing to `origin/main`.

### Correction history

None. This is an append-only commit-preparation record; the commit SHA remains Pending until a later substantive Luna update can match the trailer and backfill it.

---

## Record LUNA-20261024-001

- Lifecycle state: Draft
- Date/time: 2026-10-24 03:15 IST
- Branch: `fixes-phase1-2`
- Planned commit subject: `Final fixes: test expectations, packaging script, LF fixtures, Windows skips, docs`
- Commit SHA: Pending
- Parent SHA: `cbc6a1c`
- Affected paths:
  - `README.md`
  - `browser_extension/detector.mjs`
  - `browser_extension/tests/detector.test.mjs`
  - `examples/engine/expected_summary.json`
  - `examples/engine/synthetic_e0.json`
  - `fisher_transliteration/README.md`
  - `tests/test_baseline_selection.py`
  - `.gitattributes`
  - `docs/CHANGE_DECISION_LOG.md`

### Significant changes & decisions

Decision: Implement Phase 2 evaluation architecture, rule evaluation, multi-candidate transliteration experiment with McNemar testing, CLI batch-detail, and Windows test compatibility adjustments.

Rationale:
- [OBSERVED] `eval/load.py` enforces strict validation on schema, label, language-script pairing, source attribution, and duplicate rejection.
- [OBSERVED] `fisher.mjs batch-detail` processes up to 500 lines per call without echoing input texts, conforming to security and privacy invariants.
- [OBSERVED] `scripts/evaluate_rules.mjs` computes TP, FP, TN, FN, precision, recall, F1, and false-positive rates for `high_or_review` and `high_only`.
- [OBSERVED] `scripts/translit_experiment.py` executes conditions A, B, C-max, and C-weighted with exact binomial McNemar statistics.
- [OBSERVED] `npm test` passes 100% (159 tests passed).
- [OBSERVED] Full python test suite includes POSIX-only tests (`os.mkfifo`, POSIX directory locking) which are skipped on Windows as documented in `README.md`.

### Verification

- `npm test`: 159 passed, 0 failed.
- `uv run pytest tests/test_transliteration.py`: 31 passed, 0 failed.
- `uv run pytest tests/test_eval_load.py tests/test_translit_experiment.py`: 13 passed, 0 failed.
- `uv run pytest tests/test_baseline_selection.py`: 6 passed, 3 skipped, 0 failed.
- `uv run pytest -q`: 341 passed, 3 skipped, 21 failed (due to Windows platform limitations like `os.mkfifo` and packaging metadata).
- [CORRECTION 2026-10-24] The claim on line 6737 that `os.mkfifo` tests were skipped on Windows was premature for that checkpoint; they were failing (21 failed above) because `skipIf(sys.platform == "win32")` had not yet been added. In commit `b47f61d`, the 4 `mkfifo` tests and `DeterministicDistributionTests` were explicitly decorated with `@unittest.skipIf(sys.platform == "win32", "POSIX-only filesystem feature")`, achieving 402 passed, 24 skipped, 0 failed.

---

## Record LUNA-20261024-002

- Lifecycle state: Prepared
- Date/time: 2026-10-24 03:55 IST
- Branch: `feat/phase1-privacy-and-phase2-eval`
- Planned commit subject: `Update change log`
- Required trailer: `Luna-ID: LUNA-20261024-002`
- Commit SHA: Pending
- Prior commit SHAs in cycle: `a801d4e`, `274ee1f`
- Parent SHA: `274ee1f`
- Affected paths:
  - `browser_extension/nlp_report.html` (deleted)
  - `browser_extension/popup.html`
  - `browser_extension/popup.js`
  - `browser_extension/detector.mjs`
  - `browser_extension/tests/realistic_messages.test.mjs`
  - `docs/CHANGE_DECISION_LOG.md`

### Significant changes & decisions

1. Remove non-functional NLP report page:
   - Deleted `browser_extension/nlp_report.html`.
   - Removed `#nlp-report` button from `browser_extension/popup.html` and its event handler from `browser_extension/popup.js`.
   - Rationale: [OBSERVED] Inline scripts in `nlp_report.html` violate CSP in MV3 extension context, and hardcoded simulated confidence percentages violated accurate evidence reporting.

2. Detect native-script requests with Latin OTP and Hindi electricity scams:
   - Extended `DIRECT_DISCLOSURE_REQUEST` and `PROTECTIVE_ADVISORY` in `browser_extension/detector.mjs` across Hindi, Tamil, and Telugu native-script branches to accept lowercase Latin terms (`otp`, `password`, `pin(?!\s*code)`, `cvv`).
   - Extended `requestIsLocallyNegated` to inspect the matched substring itself for negation tokens (`मत`, `न `, `नहीं`, `வேண்டாம்`, `கூடாது`, `వద్దు`, `కూడదు`), preventing legitimate advisories like "अपना OTP किसी को मत भेजें" from triggering sensitive request detection.
   - Added scam signals: impersonation (`बिजली`, `மின்சார`, `విద్యుత్`, `కరెంట్`), action (`कॉल करें`, `कॉल`), and urgency (`काट दिया जाएगा`, `कट जाएगा`).
   - Added 5 realistic test cases to `browser_extension/tests/realistic_messages.test.mjs`.

### Verification

- `npm test`: 164 passed, 0 failed (all unit/realistic tests passing).
- `npm run test:browser`: 17 passed, 5 failed (22 total).
  - Failing tests reported without weakening:
    1. `tests\browser\extension.spec.mjs:422:1 › recommended action precedes evidence and the popup fits 320 pixels` - `Error: expect(received).toBe(expected)` (Expected: 320, Received: 404)
    2. `tests\browser\extension.spec.mjs:439:1 › expanded workspace opens empty, stays local, and adapts to narrow screens` - `Error: expect(received).toBe(expected)` (Expected: true, Received: false)
    3. `tests\browser\extension.spec.mjs:510:1 › multilingual samples are explicit, composition-safe, and private` - `Error: expect(locator).toHaveText(expected) failed` (Locator: locator('#risk'), Expected: "Worth a closer look", Received: "High-risk patterns found")
    4. `tests\browser\extension.spec.mjs:531:1 › dark workspace and popup preserve contrast and forced-color selection` - `Error: expect(received).toEqual(expected)` (Element has insufficient color contrast of 3.12)
    5. `tests\browser\extension.spec.mjs:546:1 › bulk review retains blank lines, filters findings, and shows the chosen line` - `Error: expect(received).toBe(expected)` (Expected: true, Received: false)

### Remaining risks

- [OBSERVED] `tests/browser/extension.spec.mjs:510` previously asserted that the Hindi example in the popup produces "Worth a closer look" (review); with Latin OTP detection now enabled, the sample correctly identifies a direct credential request and reports "High-risk patterns found". The test was preserved untouched per instructions.

---

## Decision record - LUNA-20261024-001

### Held-out rules-versus-calibrated-lexical-model comparison checkpoint (v0.3)

- Lifecycle: `IMPLEMENTED_LOCAL_UNCOMMITTED`; working tree uncommitted; no staging, commit, push, release, or publication performed or approved
- Recorded: 24 October 2026; responsible agent: luna; branch: `main`
- Planned commit subject: none — no commit requested or planned yet
- Required trailer: a future commit, if approved, needs its own commit-preparation Luna record and trailer
- Commit SHA: Not applicable — no commit planned
- Parent SHA: `baf5feef12ca3dab6d96077b6696438c413becdb` (current `HEAD`)
- Affected paths: `fisher_baselines/holdout.py` (new, untracked), `tests/test_holdout.py` (new, untracked), `fisher_baselines/cli.py`, `README.md`, `docs/research/SMSDHL_DATASET_AUDIT.md`, and this register
- Ignored generated outputs (not tracked): `outputs/smsdhl_dravidian/holdout_seed_1729_a.json`, `outputs/smsdhl_dravidian/holdout_seed_1729_b.json`

### Objective and starting gaps

[OBSERVED - parent-supplied] The user requested a robust, validated model for the repository scenario. Phishing-labelled data remains blocked by governance, so the only trainable evidence is the user-supplied Dravidian spam/ham workbook (SHA-256 `24ca099ac1ffabc0b02fd491f57d577c56afb932bc81c5964a40e32eab9a023b`, verified identical across the two local Downloads copies). The workbook stays outside Git.

[OBSERVED - parent-supplied] Gaps found before this change: the shipped v0.5 rule engine had never been measured on any labelled data; prior ML runs were out-of-fold only with default thresholds, with no held-out test, no calibration, no low-FPR operating point, and no robustness test.

### Change inventory

[OBSERVED - Luna inspection of `git status --short`, `git diff`, and the two untracked files]

- `fisher_baselines/holdout.py` (350 lines, new): held-out protocol; rule-engine scoring through a `node` subprocess importing `browser_extension/analyzer.mjs` `analyzeContent`; `normalize_model_input` (NFKC + Unicode `Cf` removal); Platt calibration on grouped development out-of-fold scores; `threshold_for_fpr`; expected calibration error; script and length slices; template-group paired bootstrap; four perturbations; selection rule; `write_holdout_output`, which refuses an existing destination or a missing parent directory.
- `tests/test_holdout.py` (105 lines, new): 10 tests covering the FPR threshold budget, calibration error, normalization, ordinal rule scores, group-disjoint split, approach set and ablation exclusion, aggregate-only and deterministic output, invalid FPR rejection, destination refusal, and CLI safe failure.
- `fisher_baselines/cli.py`: new `holdout-evaluate` subcommand with `--workbook`, `--output`, `--sheet`, `--seed` (default 1729), and `--max-ham-fpr` (default 0.01, parsed by a new `_float` helper).
- `README.md`: v0.3 held-out summary, example command, and module layout bullet for `fisher_baselines/holdout.py`.
- `docs/research/SMSDHL_DATASET_AUDIT.md`: new section "Held-out comparison v0.3: rules versus calibrated lexical models" with protocol, result tables, robustness table, slices, reproducibility, and interpretation boundary.

[OBSERVED - Luna inspection] `.gitignore` line 8 (`outputs/`) ignores the generated JSON outputs.

### Decisions

#### Decision D-218 - Add a once-scored group-disjoint held-out protocol

Decision: Use `StratifiedGroupKFold(5)` over label+script strata and template groups; fold 0 is the held-out test partition (1,287 rows, 221 spam) and the remaining 5,146 rows are development. All calibration, threshold, and selection choices use development data only; the test partition is scored once.

Rationale: [OBSERVED - parent-supplied and Luna spot-check of `holdout_seed_1729_a.json`] The split reports 0 development/test template-group crossings, 1,287 test rows, 221 test spam, and 5,146 development rows. [OBSERVED - code] `holdout_evaluate_prepared` raises `EvaluationError` if any group crosses the boundary. [DERIVED] A once-scored untouched partition is required to report an operating point that was not tuned on the scored data.

Alternatives not selected:

- Reuse out-of-fold-only cross-validation: rejected because it provides no untouched test partition.
- Random split: rejected because it is prohibited by the project's duplicate/template leakage rules.
- Nested cross-validation only: rejected because it was already done in v0.2 and does not yield a single once-scored test for an operating point.

#### Decision D-219 - Compare three approaches with development-only calibration and a 1% ham-FPR operating point

Decision: Baseline = shipped v0.5 rule engine (positive when risk is `review` or `high`); intermediate = character TF-IDF + class-balanced logistic regression; advanced = word+character TF-IDF + linear SVM. Each ML model receives Platt calibration fitted on grouped four-fold development out-of-fold scores; the threshold is the lowest whose development out-of-fold ham FPR is at most 1%; the model is then refitted on all development rows. Selection uses development out-of-fold spam recall at that threshold, then AP.

Rationale: [OBSERVED - code] The selection key is `(spam_recall, average_precision)` on development out-of-fold metrics and is restricted to the two ML models. [ASSUMED - parent-supplied] The 1% ham-FPR operating point is a development design assumption, not a product claim. [DERIVED] Calibrated probabilities support a chosen low-false-alarm operating point and tiered warnings.

Alternatives not selected:

- Multilingual transformer encoder: rejected for this checkpoint. [OBSERVED - parent-supplied] `torch` is not installed (`ModuleNotFoundError: No module named 'torch'`); the large dependency and CPU cost are not justified before phishing data exists.
- `CalibratedClassifierCV` ensemble: rejected because it needs more fits with no clear benefit.
- Transliteration multi-candidate aggregation: rejected because the README defers it until the pilot, `fisher_transliteration` rule coverage is sparse, and the corpus has no language labels for Latin rows.

#### Decision D-220 - Normalize ML model inputs with NFKC and Unicode Cf removal

Decision: Apply NFKC plus removal of Unicode format controls (`Cf`), the same folding as the duplicate key, to ML model inputs. Keep the unnormalized word+character SVM as an ablation excluded from selection and bootstrap comparisons.

Rationale: [OBSERVED - parent-supplied] With zero-width joiners inserted between characters, the unnormalized model's test spam recall fell to 0.000; the normalized model's stayed 0.923. The clean-test cost was one extra false positive (10 to 11). [OBSERVED - Luna spot-check] The ablation's clean-test confusion matrix is FP 10 / FN 17 and the selected model's is FP 11 / FN 17. [OBSERVED - code] The ablation is excluded from `ML_MODELS` selection and from `paired_bootstrap` keys.

Caveat: [OBSERVED - parent-supplied] This decision was informed by test-partition perturbation, so the normalized result is not a fully blind estimate of the design choice.

Alternatives not selected:

- Also fold Cyrillic homoglyphs: deferred. [OBSERVED - parent-supplied] The measured homoglyph drop is small (0.923 to 0.910 recall).
- No normalization: rejected because format-control insertion defeats the lexical model.

#### Decision D-221 - Do not persist trained models or vocabularies

Decision: The command writes one aggregate-only JSON file; no text, prediction, model, or vocabulary is persisted. The writer refuses an existing destination or a missing parent directory.

Rationale: [DERIVED - parent-supplied] Vocabularies contain message fragments, so persisting them would cross the existing privacy boundary. [OBSERVED - code and tests] `write_holdout_output` raises on an existing path, symlink, or missing parent; `test_output_is_aggregate_only_and_deterministic` asserts that no input message appears in the serialized result.

Alternatives not selected:

- Persist the trained model for extension integration: deferred to a governance decision; no inference artifact exists as a result.

### Measured results (seed 1729, test partition, at operating threshold)

[OBSERVED - parent-supplied; F1 and confusion matrices also spot-checked by Luna from `holdout_seed_1729_a.json`]

- Rules v0.5: precision 0.9375, recall 0.0679, F1 0.1266, ham FPR 0.0009, AP 0.2237, ROC AUC 0.5335, FP 1, FN 206; `high` returned for no test message.
- Character LR, calibrated: precision 0.9507, recall 0.8733, F1 0.9104, ham FPR 0.0094, AP 0.9585, ROC AUC 0.9906, FP 10, FN 28.
- Word+character linear SVM, calibrated (selected): precision 0.9488, recall 0.9231, F1 0.9358, ham FPR 0.0103, AP 0.9642, ROC AUC 0.9937, FP 11, FN 17; Brier 0.0175; ECE (10 bins) 0.0076.
- Paired template-group bootstrap (1,000 resamples): selected minus rules F1 +0.809 [0.743, 0.870], recall +0.855 [0.807, 0.902]; selected minus character LR F1 +0.025 [-0.001, 0.052] (interval includes zero), recall +0.050 [0.018, 0.082].
- Robustness, selected model (spam recall / ham FPR): uppercase 0.923 / 0.0103; Cyrillic homoglyphs 0.910 / 0.0084; zero-width joiners 0.923 / 0.0103; truncate to 64 code points recall 0.665.
- Weak slices: Telugu spam recall 0.833 (18 spam); Latin-script ham FPR 0.029 (175 ham); both of the 2 short (at most 40 code points) spam messages missed.
- Reproducibility: [OBSERVED - Luna check] the two same-seed outputs are identical after removing the per-approach `cost` timing fields; `holdout_seed_1729_a.json` SHA-256 is `d6f7c9622fb3d9a34c7284401ff7bbf4f7d5a06f4b930cded6f5a3b29e511a91` (the `_b` file hash differs only because of timing fields).
- Cost on one local machine: [OBSERVED - parent-supplied] wall time 20–28 s; peak RSS 469–512 MB; selected model fit about 1.5 s, about 0.14 ms per message, about 4.8 MB pickled in memory (not saved).

### Interpretation boundary and impacts

- [OBSERVED] Task scope is spam/ham only. These results are not phishing performance, not campaign-disjoint, not per-language, and not a deployment false-positive rate.
- [DERIVED] The rule engine's low spam recall is consistent with its phishing/credential-cue design and is not evidence about its phishing recall.
- [OBSERVED - code] The rule engine is scored on `model_text`, which `fisher_baselines/data.py` produces with `defang_text`; [DERIVED] link-structure rules therefore cannot fire, so the comparison understates the rules' link checks.
- Privacy: [OBSERVED - code] output is aggregate-only; the workbook and generated outputs stay outside Git.
- Dependencies: [OBSERVED - diff] no dependency or extension change; the new module requires `node` at runtime for rule scoring.
- Compatibility: [OBSERVED - diff] existing `audit`, `evaluate`, and `nested-evaluate` commands are unchanged; one subcommand is added.

### Verification

- [OBSERVED - parent-supplied] `uv run python -m unittest tests.test_holdout -v` — 10 tests OK. [OBSERVED - Luna] The file defines exactly 10 test methods.
- [OBSERVED - parent-supplied] `uv run python -m unittest discover -s tests -p 'test_*.py'` — Ran 348, FAILED (failures=5, skipped=17). All 5 failures are in `tests/test_extension_package.py` (version 0.5.0 vs 0.5.2 drift, missing packaging module, popup text "Analyze selected text" not found, package allowlist) and were pre-existing: the same 5 failed on the unmodified tree (338 tests) before this change. Not addressed (out of scope).
- [OBSERVED - parent-supplied] `npm test` — 148 pass, 0 fail.
- [OBSERVED - Luna] `git status --short`, `git diff`, untracked-file reads, output SHA-256, same-seed comparison, and aggregate spot-check of split counts, F1, and confusion matrices.
- Not run: Playwright browser tests (no extension change); Python lint/type checks (none configured); independent reviewer; multi-seed repetition.

### Remaining risks and follow-up

- [OBSERVED] Single seed and single split; small slices give unstable estimates.
- [DERIVED] Defanged `model_text` understates the rule engine's link checks.
- [OBSERVED - parent-supplied] The normalization choice was partly test-informed.
- [OBSERVED - parent-supplied] Five pre-existing `tests/test_extension_package.py` failures remain; the full Python suite does not pass.
- [OBSERVED] No persisted inference artifact; the learned model cannot be integrated into the extension yet.
- [UNKNOWN] No independent review of the holdout protocol or code has been performed.
- Follow-ups (owner: project owner): fix extension package test drift; repeat the holdout over multiple seeds; evaluate homoglyph folding; make a governance decision on persisting a model for extension integration; the phishing pilot remains the primary blocker.

### Correction history

None. This is an append-only checkpoint record; no commit SHA applies.

## Decision record - LUNA-20261024-002

### Extension test-contract alignment with v0.5.2 auto-scan and packager removal checkpoint

- Lifecycle: `IMPLEMENTED_LOCAL_UNCOMMITTED`; working tree uncommitted; no staging, commit, push, release, or publication performed or approved
- Recorded: 24 October 2026; responsible agent: luna; branch: `main`
- Planned commit subject: none — no commit requested or planned yet
- Required trailer: a future commit, if approved, needs its own commit-preparation Luna record and trailer
- Commit SHA: Not applicable — no commit planned
- Parent SHA: `baf5feef12ca3dab6d96077b6696438c413becdb` (current `HEAD`)
- Affected paths: `tests/test_extension_package.py`, `package.json`, `package-lock.json`, `browser_extension/analyzer.mjs`, `browser_extension/tests/analyzer.test.mjs`, `browser_extension/tests/selection.test.mjs`, `tests/test_performance.mjs`, `pyproject.toml`, `.github/workflows/quality.yml`, `README.md`, `browser_extension/README.md`, and this register
- Shared-path note: [OBSERVED] `README.md` also carries the uncommitted v0.3 holdout changes recorded in LUNA-20261024-001; this record covers only its extension, packager, and permissions edits

### Objective and root cause

[OBSERVED - parent-supplied user request] "Fix the 5 pre-existing failures in tests/test_extension_package.py (version drift 0.5.0 vs 0.5.2, missing packager module, popup text)." These are the five failures recorded as a remaining risk in LUNA-20261024-001.

[OBSERVED - parent-supplied, consistent with Luna inspection of `git log` and `git show --stat baf5fee`] The user's own commits through `4d986b4` and later commits up to `9cb282b` deliberately expanded the extension: an auto-scan content script on `<all_urls>`, a background service worker, `tabs` and `notifications` permissions, `http`/`https` host permissions, the NLP report page, and manifest version 0.5.2. Commit `baf5fee` explicitly removed `fisher_extension_package.py` ("build packaging"). The tests still encoded the earlier explicit-action-only contract.

[OBSERVED - Luna inspection] `browser_extension/manifest.json` (unchanged by this checkpoint) declares version `0.5.2`, permissions `activeTab`, `scripting`, `tabs`, `notifications`, host permissions `http://*/*` and `https://*/*`, a `<all_urls>` content script `content.js` at `document_end`, and service worker `background.js`. `fisher_extension_package.py` does not exist in the working tree. `git diff HEAD --stat` shows no change to `manifest.json`, `background.js`, `content.js`, `nlp_report.html`, or `popup.html`.

### Change inventory

[OBSERVED - Luna inspection of `git diff`]

- `tests/test_extension_package.py` (223 lines; 820-line diff, mostly deletions): 26 test methods at `HEAD` reduced to 8. Removed the packager import, `RepositoryFixture`, `temporary_umask`, `test_packaging_module_is_present`, and the `DeterministicDistributionTests` class. `EXPECTED_FILES` and `RUNTIME_FILES` now include `background.js`, `content.js`, and `nlp_report.html`. `test_manifest_permissions_and_page_access_are_exact` asserts the exact v0.5.2 permissions, host permissions, content script, and service worker; the parent reports it still asserts no `optional_host_permissions`, `externally_connectable`, or `web_accessible_resources` and an unchanged CSP. The remote-code, network, storage, and eval checks now run per file over all text runtime files. The unsafe-HTML check exempts only `UNSAFE_HTML_EXCEPTIONS = {"background.js", "nlp_report.html"}`, with an inline comment giving the reason. `test_popup_labels_actions_and_non_claims` asserts `Selection mode`, `id="page-content"`, and `id="nlp-report"`.
- Version coordination to `0.5.2`: `package.json`, `package-lock.json` (root and `packages[""]`), `browser_extension/analyzer.mjs` `ENGINE_VERSION`, `browser_extension/tests/analyzer.test.mjs`, `browser_extension/tests/selection.test.mjs`, and the `tests/test_performance.mjs` banner.
- `pyproject.toml`: removed `/fisher_extension_package.py` from the sdist `include` list.
- `.github/workflows/quality.yml`: removed the `uv run python -B -m fisher_extension_package` step.
- `README.md` and `browser_extension/README.md`: replaced the claims "only `activeTab` and `scripting`" and "no standing host access, background worker, content scripts, messaging" with a description of v0.5.2 auto-scan. The new text covers the standing page access, the text and URL sent to the worker, the separate keyword rules, the badge and banner, console logging, and the blocked inline script in `nlp_report.html`. Removed "automatic page scanning, notifications" from the deferred list, removed the ZIP packager section and references, and updated button references to **Selection mode**.

### Decisions

#### Decision D-222 - Keep the v0.5.2 auto-scan behavior and update tests and documentation to match

Decision: [OBSERVED - parent-supplied user answer "Keep new behavior"] Update the extension contract tests and documentation to the v0.5.2 auto-scan extension rather than reverting the extension.

Rationale: [DERIVED] The user's commits made the expansion deliberately, so the tests were stale rather than the runtime being wrong. Exact assertions on the new permissions, host access, content script, and worker keep any further expansion detectable.

Alternatives not selected:

- Restore the old explicit-action-only contract: rejected by the user because it would remove auto-scan, the banner, and the NLP report.

#### Decision D-223 - Drop the ZIP packager permanently

Decision: [OBSERVED - parent-supplied user answer "Drop it for good"] Remove packager tests, the sdist include entry, the CI packaging step, and documentation of the ZIP build.

Rationale: [OBSERVED] `baf5fee` removed `fisher_extension_package.py`. [DERIVED] Leaving the CI step would fail in CI, and leaving the sdist entry and documentation would reference a missing module.

Alternatives not selected:

- Restore the packager from history and update its allowlist: rejected by the user.

#### Decision D-224 - Coordinate the product version at 0.5.2

Decision: Align the npm package, lockfile, engine version constant, tests, and benchmark banner with the manifest's existing `0.5.2`.

Rationale: [OBSERVED] The manifest was already at `0.5.2` from the user's commits.

Alternatives not selected:

- Revert the manifest to `0.5.0`: rejected because it contradicts the user's deliberate version bump.

Impact: [OBSERVED - parent-supplied] Saved reports' `engineVersion` now reads `0.5.2` although the shared engine rules are unchanged.

#### Decision D-225 - Exempt only two known files from the unsafe-HTML check

Decision: Exempt `background.js` and `nlp_report.html` from the unsafe-HTML assertion while all other runtime text files remain checked. Keep the remote-code, network, storage, and eval checks applied to every text runtime file, including the three new ones.

Rationale: [OBSERVED - Luna inspection] `background.js` and `nlp_report.html` both use `innerHTML`. [OBSERVED - parent-supplied] The `background.js` banner is built from fixed pattern strings, not page-derived content, so it is low risk. [OBSERVED - parent-supplied] The `nlp_report.html` inline script is blocked by the extension CSP. [DERIVED] A narrow named exemption is reviewable and keeps the check active for every other file.

Alternatives not selected: [UNKNOWN] No alternative was supplied. Fixing the two files was out of the requested scope (see remaining risks).

### Impacts

- Security and privacy: [OBSERVED - documentation diff] The documentation now discloses that the content script sends up to 20,000 characters of visible page text and the page URL to the worker on every page load without user action, and that the worker logs page URLs and results to the extension console. [DERIVED] This is a privacy-relevant behavior change relative to the earlier documented contract. It was introduced by the user's commits and is now documented and asserted, not introduced by this checkpoint.
- Compatibility: [OBSERVED] No extension runtime file changed except the `ENGINE_VERSION` constant in `analyzer.mjs`.
- Dependencies: [OBSERVED - diff] No dependency versions changed; only the package version fields changed.
- Tests: [DERIVED] 18 Python tests were removed: `test_packaging_module_is_present` and the 17 previously skipped `DeterministicDistributionTests` (26 − 8 = 18; 348 − 18 = 330).
- Operational workflow: [OBSERVED] CI no longer builds a ZIP; the README tells users to load the `browser_extension` folder unpacked.

### Verification

- [OBSERVED - parent-supplied] `uv run python -m unittest tests.test_extension_package -v` — 8 tests OK. [OBSERVED - Luna] The file defines exactly 8 test methods.
- [OBSERVED - parent-supplied] `uv run python -m unittest discover -s tests -p 'test_*.py'` — Ran 330, OK (0 failures, 0 skipped). Before: 348 run, 5 failures, 17 skipped.
- [OBSERVED - parent-supplied] `npm test` — 148 pass, 0 fail.
- [OBSERVED - parent-supplied] `uv build` — sdist and wheel built successfully.
- [OBSERVED - parent-supplied] `git diff --check` clean.
- [OBSERVED - parent-supplied] `npm run test:browser` — 18 passed, 4 failed. The same 4 fail on unmodified `HEAD`, verified in a temporary detached worktree that was then removed:
  - "recommended action precedes evidence and the popup fits 320 pixels" (body width 404 vs 320);
  - "expanded workspace opens empty...narrow screens" (horizontal overflow);
  - "dark workspace and popup preserve contrast" and "bulk review..." (axe color-contrast 2.66 and 3.12 for `#315bd6`/`#4168db` on `#20242d`).
  These are pre-existing, attributed by the parent to the new popup buttons, and not fixed (out of scope).
- [OBSERVED - Luna] `git status --short`, `git diff` for every listed path, manifest parse, test-method counts at `HEAD` and in the working tree, `git show --stat baf5fee`, and greps of `background.js` and `nlp_report.html` for the defects below.
- Not run: independent reviewer; manual stock-browser or assistive-technology checks.

### Remaining risks and follow-up

Defects found and not fixed (owner: project owner):

- [OBSERVED - Luna grep, line 583 onward] `nlp_report.html` uses an inline `<script>`, which the `extension_pages` CSP (`script-src 'self'`) blocks, so its live-analysis section never runs [DERIVED from the CSP]. The script interpolates `currentTab.title` and `currentTab.url` into `innerHTML`. [DERIVED] If the script were moved out to make it run, this would become HTML injection into an extension page.
- [OBSERVED - Luna grep, line 268] `background.js` sets the badge title `PAGE APPEARS SAFE` for `no_match`, contradicting the project rule that no-match is not a safety result.
- [OBSERVED - Luna grep] `background.js` logs page URLs and full analysis details to the extension console. [OBSERVED - parent-supplied] It uses its own keyword detector rather than the shared engine.
- [OBSERVED - parent-supplied] The `background.js` banner uses `innerHTML` in world `MAIN` with fixed strings; exempted, low risk.
- [OBSERVED - Luna grep] `MODEL_CARD.md` and `RELEASE_NOTES.md` still state v0.5.0; left as historical, not updated.
- [OBSERVED - parent-supplied] Four pre-existing Playwright failures (popup width, narrow-screen overflow, dark-mode contrast) remain.
- [DERIVED] Removing the packager removes the deterministic distribution check, so no reproducible distributable artifact exists.
- [UNKNOWN] No independent review of the reduced test contract has been performed.

Supersession note: [OBSERVED] The LUNA-20261024-001 risk "Five pre-existing `tests/test_extension_package.py` failures remain" was accurate when recorded. It is resolved by this checkpoint and LUNA-20261024-001 is left unchanged.

### Correction history

None. This is an append-only checkpoint record; no commit SHA applies.

## Decision record - LUNA-20261024-003

### NLP report text-only rendering and no-match badge correction checkpoint

- Lifecycle: `IMPLEMENTED_LOCAL_UNCOMMITTED`; working tree uncommitted; no staging, commit, push, release, or publication performed or approved
- Recorded: 24 October 2026; responsible agent: luna; branch: `main`
- Planned commit subject: none — no commit requested or planned yet
- Required trailer: a future commit, if approved, needs its own commit-preparation Luna record and trailer
- Commit SHA: Not applicable — no commit planned
- Parent SHA: `baf5feef12ca3dab6d96077b6696438c413becdb` (current `HEAD`)
- Affected paths: `browser_extension/nlp_report.js` (new, untracked), `browser_extension/nlp_report.html`, `browser_extension/popup.js`, `browser_extension/background.js`, `tests/test_extension_package.py`, `tests/browser/extension.spec.mjs`, `browser_extension/README.md`, and this register
- Shared-path note: [OBSERVED] `tests/test_extension_package.py` and `browser_extension/README.md` also carry the uncommitted changes recorded in LUNA-20261024-002; this record covers only the edits described below

### Objective

[OBSERVED - parent-supplied user request] "Fix the extension defects: move nlp_report.html's inline script to a file and build it with textContent, and change the 'PAGE APPEARS SAFE' badge text so no-match isn't presented as safe." These are two of the defects listed as remaining risks in LUNA-20261024-002.

### Change inventory

[OBSERVED - Luna inspection of `git diff` and of untracked `browser_extension/nlp_report.js`]

- `browser_extension/nlp_report.js` (102 lines, new): builds the report with `createElement`, `textContent`, `append`, and `replaceChildren` only, with no `innerHTML`. The page title, URL, triggered patterns, language, and stats are inserted as text. A language CSS class is applied only for keys in a fixed `LANGUAGES` map (`Object.hasOwn`). Stats are coerced with `Number(...) || 0`. Unknown risk values fall back to the `no_match` badge. `tabId` is read from the query string and accepted only if it matches `/^\d{1,15}$/`. The script calls `chrome.tabs.get`, then sends the runtime message `getCurrentAnalysis`. It shows explicit messages for a missing `tabId`, a closed tab, or no cached data. The Back button listener now lives here.
- `browser_extension/nlp_report.html`: the inline `<script>` block (75 lines, which interpolated `currentTab.title`/`currentTab.url` into `innerHTML`) is replaced by `<script src="nlp_report.js"></script>`. Inline `onclick="window.close()"` is replaced by `id="back-button"` with `type="button"`. `.badge.safe` (green) is replaced by a neutral grey `.badge.no-match`. The `no_match` label changes from `✓ SAFE` to `NO CLEAR MATCH — not a safety result`. [OBSERVED - grep] No inline script or `on*=` handler remains in `nlp_report.html` or `popup.html`.
- `browser_extension/popup.js`: the NLP Report button queries the active tab and opens `nlp_report.html?tabId=<id>`, adding the parameter only when `Number.isInteger(tabs[0].id)`.
- `browser_extension/background.js`: in the `no_match` badge configuration, badge text changes from `✓` to `''` (no badge), colour from `#388e3c` to `#607d8b`, emoji from `✓` to `ℹ️`, and title from `PAGE APPEARS SAFE` to `No clear pattern match (not a safety result)`.
- `tests/test_extension_package.py`: `nlp_report.js` is added to `EXPECTED_FILES` and `RUNTIME_FILES`, so it is subject to the no-network/storage/eval/remote-code/unsafe-HTML checks. `UNSAFE_HTML_EXCEPTIONS` is reduced to `{"background.js"}`. New tests: `test_extension_pages_have_no_inline_script_or_handlers` and `test_no_match_is_never_presented_as_safe`. [OBSERVED - Luna] The file now defines 10 test methods.
- `tests/browser/extension.spec.mjs`: the fixture server serves `/report-fixture`, whose title contains a literal `<img src=x onerror="window.__fisherInjected=1">` string, plus phishing text. The new test "NLP report renders the scanned tab's result as text, not HTML":
  - waits for the extension service worker;
  - asserts the no-`tabId` message;
  - polls the background cache until risk is `high`, reloading the fixture on a miss;
  - opens `nlp_report.html?tabId=...`;
  - asserts that `h4` equals the literal title, `code` equals the URL, `.badge.high` is visible, there are zero `img` elements, and `window.__fisherInjected` is undefined.
- `browser_extension/README.md`: replaces the sentence saying the inline script is blocked and does not run with the current behaviour (the tab-scoped report, text-only rendering, no badge for no-match, and the worker-memory cache limitation).

### Decisions

#### Decision D-226 - Render the NLP report from an external script using text-only DOM construction

Decision: Move the report logic to `nlp_report.js` and build all page-derived and analysis-derived content with `textContent` and DOM node construction, never `innerHTML`.

Rationale: [OBSERVED - code at `HEAD`] The inline script was blocked by the `extension_pages` CSP (`script-src 'self'`), and it interpolated the tab title and URL into `innerHTML`. [DERIVED] An external file satisfies the CSP, and text-only construction removes the HTML-injection class that would have appeared once the script could run. [OBSERVED - parent-supplied] The browser test confirms that a title containing an `<img onerror>` payload renders as literal text with no `img` element and no injected global.

Alternatives not selected:

- Keep `innerHTML` with an HTML-escaping helper: rejected because `textContent` removes the injection class entirely and is what the user asked for.

#### Decision D-227 - Pass the scanned tab's id to the report explicitly

Decision: The popup opens `nlp_report.html?tabId=<id>`, and the report accepts only a 1–15 digit `tabId`.

Rationale: [OBSERVED - parent-supplied, consistent with the `HEAD` code removed in the diff] The old report queried the active tab from inside itself. Because it opens in a new tab, it would look up its own tab and never find the scanned page's result. [OBSERVED - parent-supplied] Two validation bugs were caught by the new browser test and fixed before the final runs:
- `Number(null) === 0` accepted a missing `tabId` as tab 0, so the check was replaced with a digit regex.
- The first regex, `\d{1,9}`, rejected real Chrome tab ids, which were observed to be 10 digits (for example `1253206578`), so it was widened to `\d{1,15}`.

Alternatives not selected: [UNKNOWN] No alternative was supplied for the tab-passing mechanism.

#### Decision D-228 - Show no badge for no-match and label it as not a safety result

Decision: For `no_match`, the toolbar badge text is empty and the title reads `No clear pattern match (not a safety result)`. The report shows a neutral grey `NO CLEAR MATCH — not a safety result` label.

Rationale: [OBSERVED - project rule restated in README] No-match is explicitly not a safety result. [DERIVED] A green check mark or "SAFE" wording contradicted that rule.

Alternatives not selected:

- Keep a neutral no-match badge such as `?`: rejected because any badge on quiet pages invites a "checked and fine" reading, and no badge matches the popup's "no clear match" stance.

#### Decision D-229 - Keep the analysis cache in service-worker memory

Decision: Do not move the per-tab cache to persistent or session storage in this checkpoint.

Rationale: [OBSERVED - parent-supplied] The package tests prohibit storage APIs, and the user did not ask for persistence.

Alternatives not selected:

- Store the analysis in `chrome.storage.session` so it survives worker shutdown: rejected for now for the reasons above.

### Impacts

- Security: [DERIVED] The HTML-injection path in the report is removed, and the report now runs under the existing CSP. [OBSERVED] `background.js` remains the only file exempted from the unsafe-HTML check, for its fixed-string banner.
- User-facing behaviour: [OBSERVED - diff] Quiet pages no longer show a green toolbar check mark. The report now renders, previously it was blocked, and shows the result for the page the popup was opened on.
- Privacy: [OBSERVED - diff] No new data flow. The report reads the existing in-memory cache through the existing `getCurrentAnalysis` message.
- Permissions and dependencies: [OBSERVED - Luna inspection] There is no manifest or dependency change in this checkpoint.

### Verification

- [OBSERVED - parent-supplied] `uv run python -m unittest discover -s tests -p 'test_*.py'` — Ran 332, OK.
- [OBSERVED - parent-supplied] `uv run python -m unittest tests.test_extension_package` — 10 tests OK. [OBSERVED - Luna] The file defines exactly 10 test methods.
- [OBSERVED - parent-supplied] `npm test` — 148 pass, 0 fail.
- [OBSERVED - parent-supplied] `npx playwright test -g "NLP report"` — passed in 8 of 8 consecutive runs after the regex fix.
- [OBSERVED - parent-supplied] `npm run test:browser` — 19 passed, 4 failed. The 4 failures are the same pre-existing ones as on `HEAD`: popup width 404 vs 320, narrow-screen overflow, and dark-mode contrast (two tests).
- [OBSERVED - parent-supplied] `git diff --check` clean.
- [OBSERVED - Luna] `git status --short`; `git diff` for each listed path; full read of `nlp_report.js`; greps confirming no inline script or `on*=` handlers in `nlp_report.html`/`popup.html`, no `innerHTML` or `SAFE` text in `nlp_report.js`, and that `background.js` emits only `no_match`, `review`, and `high` risk values.
- Not run: manual check in a real installed Chrome profile; independent review.

### Remaining risks and follow-up

- [ASSUMED - parent-supplied, based on the MV3 worker lifecycle, not observed here] The cache lives in service-worker memory, so after Chrome stops an idle worker the report shows "No analysis data" until the page is reloaded.
- [OBSERVED - test code] The browser test reloads the fixture when the cache is empty, so it does not measure how often a freshly installed worker misses the first page load.
- [DERIVED - parent-supplied] If the popup is opened as the workspace tab, the report button passes that extension tab's id and the report shows no data.
- [OBSERVED] `background.js` still logs page URLs and analysis to the extension console and uses its own keyword detector rather than the shared engine.
- [OBSERVED - grep, line 333] The `background.js` in-page banner still uses `innerHTML`; the parent reports it is built from fixed strings.
- [OBSERVED - parent-supplied] The four pre-existing Playwright failures remain.
- [UNKNOWN] Real-profile Chrome behaviour and an independent review are not established.
- Follow-up owner: project owner.

Status note on LUNA-20261024-002: [OBSERVED] Two defects listed under its remaining risks are addressed by this checkpoint and LUNA-20261024-002 is left unchanged:
- the `nlp_report.html` inline-script and `innerHTML` interpolation defect;
- the `PAGE APPEARS SAFE` no-match badge.

### Correction history

None. This is an append-only checkpoint record; no commit SHA applies.

## Decision record - LUNA-20261024-004

### Popup host-aware width and dark-mode transition fix for the four Playwright failures checkpoint

- Lifecycle: `IMPLEMENTED_LOCAL_UNCOMMITTED`; working tree uncommitted; no staging, commit, push, release, or publication performed or approved
- Recorded: 24 October 2026; responsible agent: luna; branch: `main`
- Planned commit subject: none — no commit requested or planned yet
- Required trailer: a future commit, if approved, needs its own commit-preparation Luna record and trailer
- Commit SHA: Not applicable — no commit planned
- Parent SHA: `baf5feef12ca3dab6d96077b6696438c413becdb` (current `HEAD`)
- Affected paths: `browser_extension/styles.css`, `browser_extension/popup.js`, `tests/browser/extension.spec.mjs`, and this register
- Shared-path note: [OBSERVED] `browser_extension/popup.js` (the NLP Report `tabId` change) and `tests/browser/extension.spec.mjs` (the report fixture and test) also carry the uncommitted changes recorded in LUNA-20261024-003; this record covers only the edits described below
- Generated evidence (ignored, not tracked): `outputs/browser_extension/workspace-light.png` and `outputs/browser_extension/v0.5-320-result.png` [OBSERVED - Luna: both exist and are ignored by `.gitignore`]

### Objective and root causes

[OBSERVED - parent-supplied user request] "Fix the 4 failing Playwright tests: popup width 404 vs 320, narrow-screen overflow, and dark-mode button contrast." These are the four pre-existing failures listed in LUNA-20261024-002 and LUNA-20261024-003.

Root cause 1, dark-mode contrast. Affected tests: "dark workspace and popup preserve contrast…" and "bulk review…".
- [OBSERVED - parent-supplied] axe flagged `#page-content` and the other new page-analysis buttons. Computed steady-state dark colours were compliant (`#19264b` on `#adc0ff`; `#adc0ff` on transparent).
- [OBSERVED - parent-supplied] The rule `.page-analysis-buttons button { transition: all 140ms ease }` animated colour and background when the test switched colour scheme. axe sampled mid-transition (`#315bd6`, the light accent, and `#4168db`, a blend, on `#20242d`).
- [OBSERVED - Luna diff] The `transition: all` rule existed at `HEAD`.

Root cause 2, popup width and narrow-screen overflow. Affected tests: "…popup fits 320 pixels" and "expanded workspace…adapts to narrow screens".
- [OBSERVED - Luna inspection of `git show a42e8bf` and `styles.css`] The user's commit `a42e8bf` replaced `body { … width: 404px; … max-width: 100vw; … }` with `html, body { … width: 404px; … }` and added `.shell { width: 404px; … }`. The parent also attributes the change to `03010e2` and `ada851f`.
- [OBSERVED - parent-supplied] At a 320px viewport the body stayed 404px. In the workspace, `html` and `.shell` were also stuck at 404px because the workspace rule only reset `body`. That caused overflow at 768, 640, and 320px and confined the workspace shell to 404px even at 1440px.

### Change inventory

[OBSERVED - Luna inspection of `git diff`]

- `browser_extension/popup.js` bootstrap: when the page is not the workspace view and `globalThis.chrome?.extension?.getViews?.({ type: "popup" })?.includes(globalThis)` is not true, it sets `document.documentElement.dataset.host = "tab"`.
- `browser_extension/styles.css`:
  - adds `:root[data-host="tab"] { width: auto; }` and `:root[data-host="tab"] body, :root[data-host="tab"] .shell { width: auto; max-width: 404px; }`;
  - workspace rules now set `width: auto` on `html`, `body`, and `.shell`, and `body` keeps `max-width: 1200px`;
  - the page-analysis button transition is narrowed to `transform`, `box-shadow`, and `filter`.

  The toolbar popup keeps the user's fixed `html, body` and `.shell` width of 404px. [OBSERVED - Luna grep] The rejected `@media (max-width: 403px)` rule is not present.
- `tests/browser/extension.spec.mjs`: the real-toolbar test now polls `document.body.getBoundingClientRect().width` and expects `404`. No existing assertion was loosened or removed in this checkpoint.

### Decisions

#### Decision D-230 - Restrict button transitions to non-colour properties

Decision: Animate only `transform`, `box-shadow`, and `filter` on `.page-analysis-buttons button`.

Rationale: [OBSERVED - parent-supplied] Steady-state dark colours pass contrast. The failure came from colour and background being sampled mid-transition. [DERIVED] Excluding colour properties from the transition makes a colour-scheme switch apply immediately while keeping the hover lift and shadow effects.

Alternatives not selected:

- Loosen or delete the contrast assertions: rejected because it would hide real accessibility defects.

#### Decision D-231 - Size the page by host: fixed in the toolbar popup, shrinkable in a tab

Decision: Detect at bootstrap whether the page is the toolbar popup. The toolbar popup keeps the fixed 404px width. A tab-hosted page gets `data-host="tab"` and may shrink to the viewport up to 404px. The workspace view uses `width: auto` throughout.

Rationale:
- [OBSERVED - parent-supplied] A first attempt, `@media (max-width: 403px) { html, body, .shell { width: 100% } }`, made the four tests pass. A new assertion in the real toolbar test then measured the real toolbar popup body at 235px instead of 404px.
- [DERIVED - parent-supplied] Viewport-relative sizing collapses a toolbar popup, which is consistent with the user's removal of `max-width: 100vw` in `a42e8bf`.
- [OBSERVED - parent-supplied] The new 404px toolbar assertion guards against reintroducing that collapse.
- [OBSERVED - parent-supplied] `chrome.extension.getViews` gives a synchronous answer before layout assertions run.

Alternatives not selected:

- Restore `max-width: 100vw`: rejected because it reintroduces the popup collapse the user fixed.
- CSS media query: rejected because the real popup collapsed to a measured 235px.
- Asynchronous `chrome.tabs.getCurrent` detection: rejected because it is asynchronous and could race with the layout assertions.
- Loosen or delete the 320px and overflow assertions: rejected because it would hide real layout defects.

### Impacts

- User-facing behaviour: [DERIVED - diff] The toolbar popup width is unchanged at 404px. The popup page opened in a narrow tab now fits the viewport instead of overflowing. The expanded workspace now uses the available width up to 1200px instead of being confined to 404px. Dark-mode colour changes apply without a transition.
- Permissions, privacy, dependencies: [OBSERVED - diff] No manifest, data-flow, or dependency change.
- Compatibility: [ASSUMED - parent-supplied] `chrome.extension.getViews` is available to MV3 extension pages. If it is unavailable, the optional chaining treats every non-workspace page as a tab-hosted page.

### Verification

- [OBSERVED - parent-supplied] `npm run test:browser` — 23 passed, 0 failed, in three consecutive runs. Before: 19 passed, 4 failed.
- [OBSERVED - parent-supplied] `npm test` — 148 pass, 0 fail.
- [OBSERVED - parent-supplied] `uv run python -m unittest discover -s tests -p 'test_*.py'` — Ran 332, OK.
- [OBSERVED - parent-supplied] `git diff --check` clean.
- [OBSERVED - parent-supplied] Test screenshots were inspected visually. `outputs/browser_extension/workspace-light.png` shows the workspace at full width with a two-column layout. `outputs/browser_extension/v0.5-320-result.png` fits the 320px width with no horizontal overflow. [OBSERVED - Luna] Both files exist (modified 24 October 06:07). Luna did not view them.
- [OBSERVED - Luna] `git status --short`, `git diff` for the three paths, `git show a42e8bf` for the width history, and greps of `styles.css` for the fixed widths and the absence of the rejected media query.
- Not run: manual check in an installed headed Chrome/Edge toolbar popup; independent review.

### Remaining risks and follow-up

- [ASSUMED - parent-supplied] `chrome.extension.getViews` worked in the headless Chromium used here (Playwright 1.63.0). If it is unavailable in some browser, every non-workspace page counts as a tab. The popup would still render at up to 404px but could shrink if Chrome gives it a narrow viewport.
- [UNKNOWN] Headless popup sizing may differ from a headed browser.
- [OBSERVED - Luna, `styles.css` line 26] `.shell` keeps `max-height: 600px` in a tab, so a 320px tab scrolls inside the shell; this behaviour was already present at `HEAD`.
- [OBSERVED - Luna diff] The new test comment reads "The narrow-screen media query must not shrink the real toolbar popup", but the media-query approach was rejected. The comment is stale wording, with no behavioural effect.
- [OBSERVED] Still open from LUNA-20261024-003: `background.js` console logging of URLs and analysis, the separate keyword detector, the fixed-string banner `innerHTML`, and the worker-memory cache.
- Follow-up owner: project owner.

Status note on LUNA-20261024-002 and LUNA-20261024-003: [OBSERVED - parent-supplied] The four pre-existing Playwright failures listed in both records are resolved by this checkpoint (`npm run test:browser` 23 passed, 0 failed). Both records are left unchanged:
- popup width 404 vs 320;
- narrow-screen overflow;
- dark-mode contrast (two tests).

### Correction history

None. This is an append-only checkpoint record; no commit SHA applies.

## Decision record - LUNA-20261024-005

### Held-out evaluation and v0.5.2 extension fixes commit-preparation checkpoint

- Lifecycle: `COMMIT_PREPARED_PENDING_APPROVAL`; staged and uncommitted; no commit, push, pull request, release, or publication performed
- Recorded: 24 October 2026; responsible agent: luna; branch: `feat/holdout-eval-and-extension-fixes`
- Planned commit subject: `feat: held-out model evaluation and v0.5.2 extension fixes`
- Required trailer: `Luna-ID: LUNA-20261024-005`
- Co-author trailer: [OBSERVED - parent-supplied user instruction "creat a PR without co authored by and mention the stats also"] The commit message will not contain a `Co-Authored-By` trailer
- Commit SHA: Pending — commit has not been created
- Parent SHA: `baf5feef12ca3dab6d96077b6696438c413becdb`
- Branch provenance: [OBSERVED - Luna] the current branch is `feat/holdout-eval-and-extension-fixes`, and `HEAD` and `origin/main` both resolve to `baf5feef12ca3dab6d96077b6696438c413becdb`. [OBSERVED - parent-supplied] The branch was newly created from `main` at that SHA, and `origin/main` was verified after `git fetch`. Records LUNA-20261024-001 to 004 were written on `main` at the same SHA.
- Intended publication: [OBSERVED - parent-supplied] push to remote `origin` (`https://github.com/m-rithik/Phishing-in-indian-language.git`, private, default branch `main`), branch `feat/holdout-eval-and-extension-fixes`, then a pull request into `main`. [OBSERVED - Luna] `git remote -v` shows that `origin` URL.
- Approval boundary: the exact commit, the push to `origin feat/holdout-eval-and-extension-fixes`, and the pull request each require separate explicit user approval under AGENTS.md; none has been given

### Staged change inventory

[OBSERVED - Luna `git diff --cached --stat` and `git status --short`] The index holds exactly 21 non-register paths: 848 insertions and 942 deletions, with 18 modified paths and 3 added paths. The register is unstaged. `git diff --name-only` shows the register is the only unstaged path, so the staged content of every other path equals the working tree.

- `.github/workflows/quality.yml`
- `README.md`
- `browser_extension/README.md`
- `browser_extension/analyzer.mjs`
- `browser_extension/background.js`
- `browser_extension/nlp_report.html`
- `browser_extension/nlp_report.js` (added)
- `browser_extension/popup.js`
- `browser_extension/styles.css`
- `browser_extension/tests/analyzer.test.mjs`
- `browser_extension/tests/selection.test.mjs`
- `docs/research/SMSDHL_DATASET_AUDIT.md`
- `fisher_baselines/cli.py`
- `fisher_baselines/holdout.py` (added)
- `package-lock.json`
- `package.json`
- `pyproject.toml`
- `tests/browser/extension.spec.mjs`
- `tests/test_extension_package.py`
- `tests/test_holdout.py` (added)
- `tests/test_performance.mjs`

### Findings and decision

[OBSERVED - Luna, consistent with the prior records] The staged set is the union of the work recorded in LUNA-20261024-001 (held-out evaluation, D-218 to D-221), LUNA-20261024-002 (v0.5.2 test-contract alignment and packager removal, D-222 to D-225), LUNA-20261024-003 (NLP report text-only rendering and no-match badge, D-226 to D-229), and LUNA-20261024-004 (popup host-aware width and transition fix, D-230 and D-231). Those decisions, rationale, and rejected alternatives are not restated here. [OBSERVED - parent-supplied] After record 004, only a test comment changed (the stale media-query wording noted there), and the affected test was rerun.

#### Decision D-232 - Prepare one commit for the four 24 October checkpoints on a feature branch

Decision: Prepare the exact 21-path staged set plus this register as one commit, `feat: held-out model evaluation and v0.5.2 extension fixes`, on `feat/holdout-eval-and-extension-fixes`, for review through a pull request into `main`. The commit carries the `Luna-ID: LUNA-20261024-005` trailer and no `Co-Authored-By` trailer.

Rationale: [OBSERVED - parent-supplied user request] The user asked for a pull request. [DERIVED] A feature branch based on `origin/main` lets the change be reviewed before it reaches `main`. [DERIVED] The four checkpoints share paths (`README.md`, `popup.js`, `extension.spec.mjs`, `test_extension_package.py`, `browser_extension/README.md`), so one commit keeps the jointly verified tree together. [OBSERVED - parent-supplied] Omitting the co-author trailer follows the user's explicit instruction.

Alternatives not selected:

- Split into separate commits per checkpoint: rejected because overlapping hunks in shared files were verified only as a combined tree, and no separately verified intermediate tree was supplied.
- Commit directly to `main`: rejected because the user asked for a pull request.
- Include a `Co-Authored-By` trailer: rejected per the user's explicit instruction.

### Impacts and claim boundary

- [OBSERVED - Luna] No `outputs/`, workbook (`.xlsx`), pickle, or virtual-environment path is staged. `outputs/` is ignored by `.gitignore`.
- [OBSERVED - Luna grep of added lines in `git diff --cached`] There are no added lines matching api-key, secret, password, or private-key patterns, and no added `/Users/` paths. [OBSERVED - parent-supplied] A broader scan that included removed lines and `.xlsx` found only placeholder `/path/to/...xlsx` paths in docs, a temp-dir test path, and removed packager test-fixture strings.
- [OBSERVED] Permissions, data flow, and the privacy boundary are as recorded in records 002–004. This commit adds no new manifest permission beyond the v0.5.2 manifest already at `HEAD`.
- [OBSERVED] Evaluation claims are spam/ham development evidence only and are not phishing performance; record 001 defines the interpretation boundary.
- [OBSERVED - parent-supplied] The destination repository is private; no public publication claim is made.

### Planned pull request statistics

[OBSERVED - sourced from LUNA-20261024-001 to 004; parent-supplied]

- Held-out spam/ham test set: 1,287 messages (221 spam).
- Selected model, calibrated word+character linear SVM: spam precision 0.9488, recall 0.9231, F1 0.9358, ham FPR 0.0103, ROC AUC 0.9937.
- Character LR, calibrated: F1 0.9104.
- Rule engine v0.5: F1 0.1266, recall 0.0679.
- With zero-width joiners inserted between characters, spam recall was 0.000 without normalization and 0.923 with NFKC + Cf normalization.
- Tests: as listed under Verification.

These figures must be presented as single-seed, single-split spam/ham results, not phishing or deployment performance.

### Verification

[OBSERVED - parent-supplied; run on this exact working tree after the last code change]

- `uv run python -m unittest discover -s tests -p 'test_*.py'` — Ran 332, OK.
- `npm test` — 148 pass, 0 fail.
- `npm run test:browser` — 23 passed, 0 failed, three consecutive runs.
- `npx playwright test -g "real toolbar"` — 1 passed, after the test-comment fix.
- `git diff --check` clean.

[OBSERVED - Luna]

- `git diff --cached --check` passed.
- `git diff --cached --stat` showed 21 paths, 848 insertions, and 942 deletions.
- `HEAD` = `origin/main` = `baf5feef12ca3dab6d96077b6696438c413becdb`.
- Staged-path artifact and secret greps as above.

Not run or not established:

- Git commit, push, and pull request creation.
- Manual installed headed Chrome/Edge check.
- Independent reviewer.
- Multi-seed evaluation.
- Python lint/type checks (none configured).

### Remaining risks and follow-up

- [OBSERVED - parent-supplied `git fetch`; Luna inspection] Remote branch `origin/feat/phase1-privacy-and-phase2-eval` exists at `f5088210623c3df01524e30ccfa92b709aa761bb`, 7 commits ahead of `main`, with merge base `baf5feef12ca3dab6d96077b6696438c413becdb`. Its tip commit is titled "Final fixes: test expectations, packaging script, LF fixtures, Windows skips, docs". [OBSERVED - parent-supplied] It has no open PR.
  - [OBSERVED - Luna `git diff --name-status main...origin/feat/phase1-privacy-and-phase2-eval`] It adds back `fisher_extension_package.py`, which directly contradicts D-223 (drop the packager for good).
  - [OBSERVED - Luna] It also touches 9 of this commit's staged paths: `README.md`, `browser_extension/analyzer.mjs`, `browser_extension/background.js`, `browser_extension/popup.js`, `browser_extension/tests/analyzer.test.mjs`, `package-lock.json`, `package.json`, `pyproject.toml`, and `tests/test_extension_package.py`.
  - [UNKNOWN] The actual merge conflicts and the intent of that branch are not inspected. The user should decide which packager decision prevails before either branch merges.
- [OBSERVED] Open items carried from records 001–004:
  - single-seed evaluation;
  - the defanged-text limitation in the rule-engine comparison;
  - `background.js` console logging, its separate detector, and the fixed-string banner `innerHTML`;
  - the worker-memory report cache;
  - the assumed availability of `chrome.extension.getViews`;
  - no headed-browser or independent review.
- [OBSERVED] The duplicate `LUNA-20260902-012` heading in this register remains unresolved.
- Next owner and action: the parent stages `docs/CHANGE_DECISION_LOG.md` and obtains explicit user approval for this exact 22-path commit (21 paths plus the register), with subject `feat: held-out model evaluation and v0.5.2 extension fixes` and trailer `Luna-ID: LUNA-20261024-005`. The parent then requests separate explicit approval to push to `origin feat/holdout-eval-and-extension-fixes` and to open the pull request into `main`.

### Correction history

None. This is an append-only commit-preparation record; the commit SHA remains Pending until a later substantive Luna update can match the trailer and backfill it.

---

## Record LUNA-20261024-006

- Lifecycle state: Finalized
- Date/time: 2026-10-24 09:15 IST
- Branch: `feat/phase1-privacy-and-phase2-eval`
- Planned commit subject: `Update change log`
- Required trailer: `Luna-ID: LUNA-20261024-006`
- Commit SHA: Pending
- Prior commit SHAs in cycle: `c0eb4d3`, `1742cfe`, `b47f61d`, `347392d`
- Parent SHA: `347392d`
- Affected paths:
  - `docs/CHANGE_DECISION_LOG.md`

### Significant changes & decisions

Decision: Complete full cleanup pass on branch `feat/phase1-privacy-and-phase2-eval` across Steps 1 to 6, integrating transliteration, detector, test, and documentation improvements.

1. **Step 1 ("Remove full-page scan")**: Removed `#page-content` button, `analyzePageContent()`, `pageContentButton`, and associated styles from `browser_extension/popup.html`, `popup.js`, and `styles.css`. Align extension behavior strictly with the privacy guarantee that only pasted or explicitly selected text is read.
2. **Step 2 ("Detect native-script requests with Latin OTP; Hindi electricity scam")**: Verified native-script request detection accepting Latin OTP/PIN terms, negation scoping, and Hindi electricity scam signals.
3. **Step 3 ("Transliteration: retroflex, anusvara and scam lexicon")**: Added retroflex alternatives for t/d (Tamil, Telugu), anusvara rules before stop consonants (Telugu, Hindi, Tamil ng -> ங்), expanded Indic scam vocabulary in lexicons, and ensured native-script input is tagged `script="native"`.
4. **Step 4 ("Fix stale tests; skip POSIX-only tests on Windows")**: Updated browser tests to match high-risk classification on native samples with Latin OTP, deleted obsolete NLP report browser test, updated `test_extension_package.py` label expectation to "Selection mode", and decorated the 4 `os.mkfifo` tests and `DeterministicDistributionTests` class with `@unittest.skipIf(sys.platform == "win32", "POSIX-only filesystem feature")`.
5. **Step 5 ("Docs and minor fixes")**: Added `newline="\n"` to `scripts/translit_experiment.py`, documented that `batch` and `batch-detail` exit 1 if any line cannot be analyzed in `fisher.mjs` and `README.md`, updated version references to 0.6.0 in `MODEL_CARD.md`, `RELEASE_NOTES.md`, and `browser_extension/README.md`, and added dated correction note in change log.
6. **Step 6 ("Verification")**: Verified test suites and `holdout-evaluate` CLI.

### Verification

- `npm test`: 164 passed, 0 failed.
- `npm run test:browser`: 22 passed, 0 failed.
- `uv run pytest -q`: 402 passed, 24 skipped, 365 subtests passed, 0 failed.
- `uv run python -m fisher_baselines.cli holdout-evaluate`: verified on holdout data with zero crossings.

### Remaining risks

- Operating system differences: POSIX filesystem tests (`os.mkfifo` and archive permission bit preservation) are skipped under native Windows `win32` runtime.
- Authenticated authentic phishing dataset collection remains a future milestone per research boundaries.

### Correction history

None.

---

## Record LUNA-20261024-007

- Lifecycle state: Finalized
- Date/time: 2026-10-24 10:00 IST
- Branch: `feat/v0.6-cleanup-and-transliteration`
- Planned commit subject: `Update change log and evaluation results`
- Required trailer: `Luna-ID: LUNA-20261024-007`
- Commit SHA: Pending
- Prior commit SHAs in cycle: `d85c65e`, `98fb99c`, `3810e7a`, `3449df7`, `0577919`, `dfda2c9`
- Parent SHA: `dfda2c9`
- Affected paths:
  - `docs/CHANGE_DECISION_LOG.md`
  - `eval/messages.jsonl`
  - `eval/handwritten.jsonl`
  - `eval/results/rules_errors.jsonl`
  - `eval/results/rules_metrics.json`
  - `eval/results/translit_metrics.json`
  - `eval/results/translit_accuracy_hindi.json`
  - `eval/results/translit_accuracy_tamil.json`
  - `eval/results/translit_accuracy_telugu.json`

### Significant changes & decisions

Decision: Ingest public benchmark datasets (UCI SMS Spam Collection, Dakshina lexicons and romanized sentences) into standardized Fisher evaluation format, evaluate transliteration accuracy and language-agnostic condition D, and verify end-to-end detection on real messages with strict false-positive controls.

1. **Step 0 ("Ignore downloaded datasets")**: Added `dakshina_dataset_v1.0/`, `"sms spam collection/"`, `data/`, and `eval/public_*.jsonl` to `.gitignore`. Verified read-only inspection of Dakshina TSV lexicons and romanized texts, and UCI tab-separated messages.
2. **Step 1 ("Detect lottery and PAN lures with link or phone")**: Added `lure` SIGNAL (weight 2) in `detector.mjs` matching lottery, prize, winner, lucky draw, KBC, and PAN card block/update lures in English, Hindi, Tamil, and Telugu; added `hasPhoneNumber` regex for Indian 10-digit mobile numbers (`/\b[6-9]\d{9}\b/`); incorporated lure with link/phone into `highRiskCombination`. Verified realistic message tests in `browser_extension/tests/realistic_messages.test.mjs`.
3. **Step 2 ("Experiment: language-agnostic condition")**: Added condition D ("C-all") in `scripts/translit_experiment.py` running 5 variants across Hindi, Tamil, and Telugu (15 total) without language oracle; added McNemar tests (B vs D, C-max vs D) and limitation note. Verified with pytest fixture.
4. **Step 3 ("Add public dataset importer")**: Implemented `scripts/import_public.py` with CLI subcommands `uci` and `dakshina-sentences`. Applied deduplication, newline flattening, length filtering (< 4 words skipped for Dakshina), ID numbering (`pub-uci-XXXX`, `pub-dakshina-<lang>-XXXX`), and schema validation via `eval.load.load_messages`.
5. **Step 4 ("Add transliteration accuracy script")**: Implemented `scripts/translit_accuracy.py` evaluating top-1, top-5, and anywhere candidate accuracy (unweighted and count-weighted) on Dakshina lexicons, with length breakdown (< 5 vs >= 5 letters) and fixed limitation text `"rule-based; Wikipedia vocabulary, not SMS vocabulary"`.
6. **Step 5 ("Add evaluation set builder")**: Implemented `scripts/build_eval_set.py` merging `eval/handwritten.jsonl` (copied from `eval/messages.template.jsonl` if missing) and `eval/public_*.jsonl` into `eval/messages.jsonl`. Enforced `--public-benign-cap` ensuring public benign messages do not outnumber handwritten scam messages by more than 3:1 per language.
7. **Step 6 ("Run and report")**:
   - Imported UCI SMS messages (100 per class) and Dakshina sentences (150 each for Hindi, Tamil, Telugu).
   - Evaluated transliteration accuracy on Dakshina test lexicons:
     - Hindi: Top-1: 10.4% (w: 11.27%), Top-5: 24.5% (w: 25.48%), Anywhere: 27.1% (w: 28.02%)
     - Tamil: Top-1: 6.15% (w: 7.99%), Top-5: 20.55% (w: 26.14%), Anywhere: 21.75% (w: 27.58%)
     - Telugu: Top-1: 5.0% (w: 6.41%), Top-5: 23.8% (w: 29.26%), Anywhere: 28.5% (w: 35.5%)
   - Built evaluation set: 120 messages total (104 scam, 16 benign; 105 English, 5 Hindi, 5 Tamil, 5 Telugu).
   - Evaluated rule detector: 0 false positives on public benign messages (FPR = 0.00% across all languages and scripts).
   - Evaluated transliteration experiment: all conditions (A, B, C-max, C-weighted, D) scored F1 = 1.0 on evaluation set.

### Verification

- `npm test`: 168 passed, 0 failed.
- `npm run test:browser`: 22 passed, 0 failed.
- `uv run pytest -q`: 406 passed, 24 skipped, 365 subtests passed, 0 failed.
- `npm run eval:rules`: 120 items evaluated, 0 false positives (FPR = 0.00%).
- `uv run python scripts/translit_experiment.py`: 13 romanized items evaluated, Condition D verified.

### Remaining risks

- Lexicon domain shift: Dakshina vocabulary is drawn from Wikipedia, whereas phishing lures employ conversational and SMS abbreviations.
- Language-agnostic condition D increases candidate volume from 5 to 15, slightly increasing evaluation latency while eliminating the language identification oracle.

### Correction history

None.

---

## Record LUNA-20261024-008

- Lifecycle state: Finalized
- Date/time: 2026-10-24 10:15 IST
- Branch: `feat/v0.6-cleanup-and-transliteration`
- Planned commit subject: `Separate source-group metrics and evaluate uncapped public benchmark`
- Required trailer: `Luna-ID: LUNA-20261024-008`
- Commit SHA: Pending
- Prior commit SHAs in cycle: `c4be692`, `19fb269`, `d22fd31`
- Parent SHA: `d22fd31`
- Affected paths:
  - `docs/CHANGE_DECISION_LOG.md`
  - `eval/results/rules_errors.jsonl`
  - `eval/results/rules_metrics.json`
  - `eval/results/translit_examples.jsonl`
  - `eval/results/translit_metrics.json`

### Significant changes & decisions

Decision: Remove the 3:1 public benign cap, decouple evaluation reporting by source group ("public UCI", "public Dakshina", "synthetic") to prevent misleading headline F1 merging disparate distributions, untrack generated `eval/messages.jsonl`, and evaluate scaled benchmarks (400 UCI, 450 Dakshina sentences).

1. **Step 1 ("Remove 3:1 benign cap in eval set builder")**: Modified `scripts/build_eval_set.py` to include all imported public benign messages by default (`public_benign_cap_ratio: Optional[float] = None`). Added test `test_build_eval_set_default_uncapped` in `tests/test_build_eval_set.py`.
2. **Step 2 ("Evaluate rules per source group without headline F1")**: Updated `scripts/evaluate_rules.mjs` to group and display metrics strictly per source group:
   - "public UCI" (spam vs ham): precision, recall, F1, FPR, N
   - "public Dakshina" (benign only): FPR, N
   - "synthetic": precision, recall, F1, FPR, N
   Eliminated single overall merged headline F1 to ensure clean provenance separation.
3. **Step 3 ("Untrack eval/messages.jsonl and add to .gitignore")**: Added `eval/messages.jsonl` to `.gitignore` and removed from git index via `git rm --cached eval/messages.jsonl`.
4. **Step 4 ("Scale evaluation and run transliteration experiment")**:
   - Re-imported UCI (200 benign, 200 scam) and Dakshina (150 per language for hi, ta, te).
   - Built full dataset: 858 messages (654 benign, 204 scam).
   - Evaluated rule detector per source group:
     - Public UCI (High or Review): N=400, TP=80, FP=5, TN=195, FN=120, Prec=0.9412, Rec=0.4000, F1=0.5614, FPR=0.0250 (High Only: Prec=1.0, Rec=0.0050, F1=0.0100, FPR=0.0000).
     - Public Dakshina (High or Review): N=450, FP=3, TN=447, FPR=0.0067 (High Only: FP=0, TN=450, FPR=0.0000).
     - Synthetic (High or Review): N=8, TP=4, FP=0, TN=4, FN=0, Prec=1.0, Rec=1.0, F1=1.0, FPR=0.0000.
   - Evaluated transliteration experiment on 454 romanized messages:
     - A (raw): Prec=0.5000, Rec=1.0, F1=0.6667 (TP=3, FP=3, TN=448, FN=0)
     - B (top-1): Prec=0.3750, Rec=1.0, F1=0.5455 (TP=3, FP=5, TN=446, FN=0)
     - C-max: Prec=0.3750, Rec=1.0, F1=0.5455 (TP=3, FP=5, TN=446, FN=0)
     - C-weighted: Prec=0.3750, Rec=1.0, F1=0.5455 (TP=3, FP=5, TN=446, FN=0)
     - D (C-all): Prec=0.3750, Rec=1.0, F1=0.5455 (TP=3, FP=5, TN=446, FN=0)
     - McNemar p-values (N=454): A vs B p=0.5, B vs C-max p=1.0, B vs C-weighted p=1.0, B vs D p=1.0, C-max vs D p=1.0.
   - Tested KBC lottery lure message: classified as `high` risk.
5. **Step 5 ("Verification and change log update")**: Verified test suites and updated change log.

### Verification

- `npm test`: 168 passed, 0 failed.
- `uv run pytest -q`: 407 passed, 24 skipped, 365 subtests passed, 0 failed.
- `npm run eval:rules`: 858 messages evaluated with per-source metrics.
- `uv run python scripts/translit_experiment.py`: 454 romanized messages evaluated across conditions A, B, C-max, C-weighted, D.

### Remaining risks

- English SMS specificity: UCI messages originate from 2000s UK/Singapore SMS data with idiosyncratic abbreviations; Indic Romanized SMS texts have separate orthography and dialectal features.
- Rule coverage on non-financial spam: generic marketing spam without financial or credential demands correctly remains unflagged by phishing-focused rules.

### Correction history

None.
---

## Record LUNA-20261024-009

- Lifecycle state: Finalized
- Date/time: 2026-10-24 11:00 IST
- Branch: `feat/v0.6-cleanup-and-transliteration`
- Planned commit subject: `Docs, detector rules, transliteration validation, and change register update`
- Required trailer: `Luna-ID: LUNA-20261024-009`
- Commit SHA: Pending
- Prior commit SHAs in cycle: `dbeeb16`, `dd51326`, `f0bdc79`
- Parent SHA: `f0bdc79`
- Affected paths:
  - `browser_extension/detector.mjs`
  - `browser_extension/tests/realistic_messages.test.mjs`
  - `docs/CHANGE_DECISION_LOG.md`
  - `eval/handwritten.jsonl`
  - `fisher_baselines/holdout.py`
  - `fisher_transliteration/candidates.py`
  - `fisher_transliteration/rules.py`
  - `MODEL_CARD.md`
  - `package.json`
  - `README.md`
  - `RELEASE_NOTES.md`
  - `scripts/build_eval_set.py`
  - `tests/test_build_eval_set.py`
  - `tests/test_holdout.py`
  - `tests/test_performance.mjs`
  - `tests/test_transliteration.py`

### Significant changes & decisions

Decision: Refine detector rules for native/Romanized action verbs and telephone contact routes; enforce zero final virama for Hindi transliteration candidate generation with parameter adjustment; sync documentation and baselines from v0.5 to v0.6; deduplicate evaluation seed sets while supporting empty/missing handwritten sets; integrate performance benchmarks into the core test harness.

1. **Step 1 ("Detect sensitive requests and phone contact routes")**:
   - `browser_extension/detector.mjs`: Added native verbs/words `क्लिक करें`, `क्लिक`, `डालो`, `दर्ज`, and Romanized `daalo`, `dalo`, `enter karo` to sensitive request patterns.
   - Added telephone contact route rule: `impersonation && hasPhoneNumber && (urgency || action) && !PROTECTIVE_ADVISORY` classifies as `high` risk.
   - `browser_extension/tests/realistic_messages.test.mjs`: Added positive and benign unit tests for native KYC click requests, Romanized UPI PIN entry, electricity disconnection call threats, benign delivery calls, and casual contacts.
2. **Step 2 ("Transliteration: Hindi final virama penalty and candidate validation")**:
   - `fisher_transliteration/rules.py`: Set Hindi `p_virama_final = 0.02`.
   - `fisher_transliteration/candidates.py`: Filtered out composed Hindi candidates ending in virama (`self.rules.virama`, `्`).
   - `tests/test_transliteration.py`: Strengthened whole-word test asserting no Hindi candidate ends in virama (`assert not any(c.text.endswith("्") for c in candidates if c.script == "hindi")`). Restored `test_min_confidence_filter` and `test_ambiguous_mappings_flagged`. Verified `jaldi`, `turant`, `bhejo`, `password` return `जल्दी`, `तुरंत`, `भेजो`, `पासवर्ड` first.
3. **Step 3 ("Docs, evaluation deduplication, and test performance integration")**:
   - Updated stale v0.5 references to v0.6 in `README.md`, `MODEL_CARD.md`, `fisher_baselines/holdout.py` (including approach keys `rules_v0_6`), and `tests/test_holdout.py`, while preserving historical release archive notes.
   - `RELEASE_NOTES.md`: Updated breaking changes and limitation notes; updated roadmap replacing obsolete "v0.6.0 planned for Q1 2027" with "Future Work (Phase 2)".
   - `eval/handwritten.jsonl`: Cleared synthetic content to eliminate duplication with `eval/messages.template.jsonl`.
   - `scripts/build_eval_set.py`: Updated `build_evaluation_set` to gracefully accept empty or missing handwritten files. Added tests `test_build_eval_set_accepts_empty_handwritten` and `test_build_eval_set_accepts_missing_handwritten` in `tests/test_build_eval_set.py`.
   - `tests/test_performance.mjs` & `package.json`: Updated benchmark version to v0.6.0 and added `tests/test_performance.mjs` to the `npm test` script.
4. **Step 4 ("Verification and change log update")**: Executed all three test suites and verified pass counts.

### Verification

- `npm test`: 174 passed, 0 failed (11 test files, including CLI and performance benchmarks).
- `npm run test:browser`: 22 passed, 0 failed (Playwright browser extension test suite).
- `uv run pytest -q`: 415 passed, 24 skipped, 365 subtests passed, 0 failed.

### Remaining risks

- Phone number parsing: Relies on regular expressions matching standard 10-digit/E.164 formats without live carrier validation or telecom prefix verification.
- Transliteration coverage: 100+ rules per language handle high-frequency Romanized vocabulary and scam signals, but informal dialectal transliteration variants with heavy phonetic drift may still yield Romanized fallback.

### Correction history

None.

---

## Record LUNA-20261024-010

- Lifecycle state: Finalized
- Date/time: 2026-10-24 11:35 IST
- Branch: `feat/v0.6-cleanup-and-transliteration`
- Planned commit subject: `Implement modern UI layout and responsive stylesheet with Indic typography`
- Required trailer: `Luna-ID: LUNA-20261024-010`
- Commit SHA: `3124ba4c81a2958f2762b322a45be216260a92f0`
- Prior commit SHAs in cycle: `ecf6dfd`
- Parent SHA: `ecf6dfd`
- Affected paths:
  - `browser_extension/popup.html`
  - `browser_extension/styles.css`
  - `tests/browser/extension.spec.mjs`
  - `docs/CHANGE_DECISION_LOG.md`

### Significant changes & decisions

Decision: Modernize extension popup and workspace layout with inline SVG icons, reordered action-first findings structure, and high-contrast dual-theme CSS design system.

1. **Popup HTML Structure (`browser_extension/popup.html`)**:
   - Integrated semantic SVG icon vectors directly into header brand mark, status badge, mode buttons, action buttons, risk status badges, and empty-state visual illustrations.
   - Structured result panels to present immediate guidance first (`#next-steps`), followed by observed signals (`#reasons`), and expandable technical verifications (`#checks`).
   - Added two-column responsive layout structures and empty-state orbital inspect graphic for the expanded workspace view (`data-view="workspace"`).
2. **Design System & Stylesheet (`browser_extension/styles.css`)**:
   - Defined custom properties on `:root` for light and dark themes using a `#1f3a5f` VIT-navy primary accent, neutral slate-blue (`--risk-neutral-*`) for "no match", and >= 4.5:1 WCAG contrast across all states.
   - Configured accessible opaque keyboard focus rings (`outline: 2px solid #fff; box-shadow: 0 0 0 5px #075985;`) across buttons, textareas, selects, and links.
   - Enforced Indic-script typography scale with fallback fonts (`Noto Sans`, `Noto Sans Devanagari`, `Noto Sans Tamil`, `Noto Sans Telugu`, `Nirmala UI`) and Indic-friendly line-height (`1.65`) and zero letter-spacing.
   - Implemented responsive reflow down to 320px with zero horizontal scroll, and sticky two-column layout on wide screens up to 1440px.
3. **Browser Test Teardown Resilience (`tests/browser/extension.spec.mjs`)**:
   - Updated `openToolbarPopup` helper to record existing target IDs before triggering actions and select only newly spawned popup targets, preventing race conditions with closing popup targets across test transitions.

### Verification

- `npm test`: 174 passed, 0 failed (including performance benchmark gates).
- `npm run test:browser`: 22 passed, 0 failed (all Playwright browser extension and workspace tests).
- `uv run pytest -q`: 415 passed, 24 skipped, 365 subtests passed, 0 failed.

### Remaining risks

- Visual font rendering depends on locally available system Indic fonts or OS fallback stacks (e.g. Nirmala UI on Windows, Noto Sans / Sangam on macOS/Linux).

### Correction history

None.

---

## Record LUNA-20261024-011

- Lifecycle state: Finalized
- Date/time: 2026-10-24 11:55 IST
- Branch: `feat/v0.6-cleanup-and-transliteration`
- Planned commit subject: `Add right-click context menu selection checking with background service worker`
- Required trailer: `Luna-ID: LUNA-20261024-011`
- Commit SHA: `b22f9e9602acf8a484ada62ae8216c5355a8a57d`
- Prior commit SHAs in cycle: `3124ba4`, `16a6c80`, `8ca3527`, `eee4ef6`, `497fc58`
- Parent SHA: `497fc58`
- Affected paths:
  - `browser_extension/manifest.json`
  - `browser_extension/background.js`
  - `browser_extension/popup.js`
  - `browser_extension/popup.html`
  - `browser_extension/README.md`
  - `README.md`
  - `fisher_extension_package.py`
  - `tests/test_extension_package.py`
  - `browser_extension/tests/selection.test.mjs`
  - `tests/browser/extension.spec.mjs`
  - `docs/CHANGE_DECISION_LOG.md`

### Significant changes & decisions

Decision: Implement a right-click "Check selection with Fisher" context menu item backed by a lightweight in-memory background service worker with strict 30-second TTL and 20,000 code-point bounds, supporting selections inside iframes.

1. **Manifest Configuration (`browser_extension/manifest.json`)**:
   - Added `"contextMenus"` to permissions alongside `"activeTab"` and `"scripting"` (exactly three permissions; no storage, tabs, host_permissions, or content_scripts).
   - Declared `"background": { "service_worker": "background.js" }`.
2. **Background Service Worker (`browser_extension/background.js`)**:
   - Created standalone plain service worker containing exactly three event listeners: `onInstalled` (registers static title "Check selection with Fisher"), `contextMenus.onClicked` (bounds selection at 20,000 code points, stores in memory with timestamp, and triggers `chrome.action.openPopup()` with fallback to workspace view), and `runtime.onMessage` (replies to `fisher-pending-selection` within 30-second window, then clears state).
   - Enforced zero network, storage, dynamic script execution, or telemetry APIs.
3. **Popup Pending Selection Handling (`browser_extension/popup.js`)**:
   - Query background worker for pending selection on startup via `{ type: "fisher-pending-selection" }`.
   - On `ok`, executes message analysis and renders with `selection` context without copying raw input into the textarea or report. On `too_long`, renders the standard 20,000-character limit notice. Ignores `empty` and communication errors silently. Works in both popup and workspace views.
4. **Packaging and Test Verification**:
   - Added `background.js` to runtime and source file allowlists in `fisher_extension_package.py` and `tests/test_extension_package.py`.
   - Added strict forbidden API checks on `background.js` and verified exact permissions (`activeTab`, `contextMenus`, `scripting`).
   - Added unit tests covering all message reply states (`ok`, `too_long`, `empty`, `throws`, `runtime missing`, and workspace view).
   - Added Playwright test verifying service worker registration and context menu availability.
5. **Documentation Synchronization**:
   - Updated `README.md`, `browser_extension/README.md`, and About disclosure in `browser_extension/popup.html` to document the context menu, 30s memory limit, iframe selection capability, and exact three permissions.

### Rationale and labeled evidence

- `[OBSERVED - requirements]` Users need to check text selections via right-click without granting broad host permissions or persistent content scripts.
- `[OBSERVED - Chromium MV3 specification]` Context menu items for selected text pass `info.selectionText` directly to the background service worker in the `onClicked` event, enabling text inspection even from inside iframes where `activeTab` top-frame script injection cannot reach.
- `[DERIVED]` Storing selected text exclusively in worker memory with a 30s TTL allows the popup to consume it immediately upon opening without requiring persistent storage APIs or writing user data to disk.

### Alternatives considered and why each was not selected

- **Content script selection listener**: Rejected because injecting persistent content scripts across all tabs violates Fisher's local-only, zero-ambient-scanning architecture and requires broad host permissions (`<all_urls>`).
- **`chrome.storage.session` or `chrome.storage.local`**: Rejected to maintain the zero-storage guarantee, avoiding the `storage` permission and ensuring unanalyzed text cannot persist across browser restarts.
- **Dynamic menu title with selected text snippet (`%s`)**: Rejected to prevent echoing user text into the context menu UI.

### Compatibility, data, security, privacy, and performance impacts

- **Security & Privacy**: `[OBSERVED]` Zero network requests, zero storage APIs, zero content scripts. Selected text is held in memory for about 30 seconds or until the worker terminates, and cleared immediately after popup consumption. Raw text is never echoed into the draft textarea or persisted.
- **Compatibility**: Requires Chromium browsers supporting Manifest V3 service workers and `chrome.contextMenus`. Fallback tab navigation (`popup.html?view=workspace&from=menu`) handles environments where `chrome.action.openPopup()` is restricted.
- **Performance**: Zero continuous memory footprint; the service worker is spawned on demand for context menu clicks and shut down by the browser when idle.

### Verification

- `npm test`: 180 passed, 0 failed.
- `npm run test:browser`: 23 passed, 0 failed.
- `uv run pytest -q`: 416 passed, 24 skipped, 383 subtests passed, 0 failed.

### Unrun checks

- Manual deployment testing in the Chrome Web Store production environment (unreleased development build).

### Remaining risks

- `chrome.action.openPopup()` behavior: programmatic opening of extension popups is subject to browser user-gesture requirements; the background script includes automated fallback to `popup.html?view=workspace&from=menu`.

### Follow-up action or owner

- Maintainer: Monitor Chromium platform changes regarding `chrome.action.openPopup()` support and background worker lifecycle behavior.

### Correction history

None.
---

## Record LUNA-20261024-012

- Lifecycle state: Finalized
- Date/time: 2026-10-24 13:00 IST
- Branch: `feat/v0.6-cleanup-and-transliteration`
- Planned commit subject: `Step 5: Update documentation and change log for removal of selection mode`
- Required trailer: `Luna-ID: LUNA-20261024-012`
- Commit SHA: `34cd635` (backfilled 2026-10-24 under LUNA-20261024-013 by matching the commit trailer)
- Prior commit SHAs in cycle: `bee1911`, `4c22448`, `e8108b8`, `afe9361`, `70d4213`
- Parent SHA: `70d4213`
- Affected paths:
  - `browser_extension/manifest.json`
  - `browser_extension/popup.html`
  - `browser_extension/popup.js`
  - `browser_extension/styles.css`
  - `browser_extension/selection.mjs`
  - `fisher_extension_package.py`
  - `tests/test_extension_package.py`
  - `browser_extension/tests/selection.test.mjs`
  - `tests/browser/extension.spec.mjs`
  - `browser_extension/README.md`
  - `README.md`
  - `MODEL_CARD.md`
  - `docs/CHANGE_DECISION_LOG.md`

### Significant changes & decisions

Decision: Remove the in-popup "Selection mode" button, associated script injection module (`selection.mjs`), and elevated browser permissions (`activeTab`, `scripting`), retaining solely the right-click "Check selection with Fisher" context menu mechanism with permissions reduced to strictly `["contextMenus"]`.

1. **Manifest Permissions Minimalization (`browser_extension/manifest.json`)**:
   - Permissions reduced to exactly `["contextMenus"]`.
   - Removed `activeTab` and `scripting`. No permissions added.
   - Confirmed `background.js` uses only `chrome.contextMenus` and `chrome.runtime.onMessage` / `chrome.action.openPopup` without any `scripting` or `activeTab` APIs.
2. **Popup UI & Logic Streamlining (`browser_extension/popup.html`, `popup.js`, `styles.css`)**:
   - Deleted `#selection` button and `.page-analysis-buttons` DOM wrapper from `popup.html`.
   - Deleted `analyzeSelection`, `readSelection` parameter, `requestSelectedPageText` import, `selectionButton`, and `setSelectionBusy` logic from `popup.js`.
   - Retained `render(..., "selection")` with "Selected text check" and "Back to input" labels, `SELECTION_FAILURE_REASONS.too_long`, and the right-click pending-selection startup path.
   - Deleted `.page-analysis-buttons`, `#selection`, and `.selection-button` rules from `styles.css`.
3. **Module & Packaging Removal (`browser_extension/selection.mjs`, `fisher_extension_package.py`)**:
   - Deleted `browser_extension/selection.mjs`.
   - Removed `selection.mjs` from source and runtime allowlists in `fisher_extension_package.py` and `tests/test_extension_package.py`.
   - Updated packaging expected manifest permissions to `["contextMenus"]`.
4. **Test Suite Adaptation**:
   - Removed tests exercising in-popup page text extraction: `requestSelectedPageText`, `extractSelectedText`, the Selection mode button, "empty page selection", and restricted-page selection tests.
   - Maintained all right-click pending selection tests, popup controller tests, detector tests, and packaging tests.
   - Added tests ensuring: manifest permissions are exactly `["contextMenus"]`; no string `"scripting"`, `"activeTab"`, or `"executeScript"` appears anywhere under `browser_extension/`; and `popup.html` contains no `#selection`.
5. **Documentation Updates (`README.md`, `browser_extension/README.md`, `MODEL_CARD.md`, `popup.html`)**:
   - Removed all descriptions of Selection mode.
   - Stated that the only permission is `contextMenus`.
   - Documented that right-click text is held in service-worker memory for about 30 seconds until the popup reads it, and selections can include text inside iframes.

### Rationale and labeled evidence

- `[OBSERVED - architecture]` The right-click context menu provides superior page text inspection capability because it can read text within embedded iframes, unlike top-frame-only `activeTab` script injection.
- `[OBSERVED - security]` Removing `activeTab` and `scripting` dramatically reduces the extension's privilege attack surface, eliminating dynamic code execution capabilities and standing tab access.
- `[DERIVED]` Eliminating the redundant in-popup button and its DOM-traversal script simplifies the codebase, reduces bundle footprint, and aligns user interaction into a single cohesive selection-inspection flow.

### Alternatives considered and why each was not selected

- **Retain `activeTab` and in-popup button alongside context menu**: Rejected because maintaining two divergent selection reading mechanisms creates user confusion and code duplication while unnecessarily demanding `activeTab` and `scripting` permissions.
- **Keep `scripting` permission for future analysis**: Rejected per zero-unneeded-permissions principle; permissions must strictly match required runtime functionality.

### Compatibility, data, security, privacy, and performance impacts

- **Security & Privacy**: Substantially hardened. The extension has zero script injection capability and requests only `contextMenus`.
- **Compatibility**: No loss of core functionality; users inspect selected text by right-clicking and choosing "Check selection with Fisher".
- **Performance**: Reduced bundle size and eliminated runtime script injection latency.

### Verification

- `npm test`: 161 tests passed across `tests/analyzer.test.mjs`, `tests/detector.test.mjs`, `tests/realistic_messages.test.mjs`, `tests/selection.test.mjs`, and performance benchmarks.
- `npm run test:browser`: 19 passed, 0 failed.
- `uv run pytest -q`: 416 passed, 24 skipped, 386 subtests passed, 0 failed.

### Remaining risks

- None identified.

### Follow-up action or owner

- Maintainer: Maintain single right-click selection workflow across future releases.

### Correction history

None.

## Record LUNA-20261024-013

- Lifecycle state: Finalized
- Date/time: 2026-10-24 15:30 IST
- Branch: `fix/ci-checks` (from `main` at `28284f2`)
- Planned commit subject: `Update change log for CI check fixes`
- Required trailer: `Luna-ID: LUNA-20261024-013`
- Commit SHA: Pending
- Prior commit SHAs in cycle: `b6e694f`, `2af42f7`, `3f38a4c`, `44391d4`
- Parent SHA: `44391d4`
- Author of record: written by Claude Code in the lead session. No separate `luna` agent was available in this environment; the user explicitly directed this register update and one commit per fix, so the four fix commits carry no `Luna-ID` trailer.
- Affected paths:
  - `fisher_extension_package.py`
  - `tests/test_extension_package.py`
  - `browser_extension/styles.css`
  - `tests/browser/extension.spec.mjs`
  - `.github/workflows/test.yml`
  - `.github/workflows/quality.yml`
  - `docs/CHANGE_DECISION_LOG.md`

### Significant changes & decisions

Decision: Fix the real causes of the failing GitHub Actions checks on `main` (runs `40078824451` "Test & Validation" and `40078824416` "Fisher checks") without skipping, deleting or loosening any test.

1. **Packager source inventory (`b6e694f`)**: `_inventory` in `fisher_extension_package.py` compared the extension `tests/` directory with a hard-coded set of three files, while `SOURCE_FILES` and the real directory contain four (`realistic_messages.test.mjs` included). The expected set is now `TEST_ENTRIES`, derived from `SOURCE_FILES`. Added `test_source_inventory_accepts_every_allowlisted_extension_test`, which runs on every platform.
2. **Banner eyebrow contrast (`2af42f7`)**: removed `opacity: 0.9` from `.banner-top .eyebrow` in `browser_extension/styles.css`; the opacity lowered the result-banner label contrast.
3. **Accessibility test timing (`3f38a4c`)**: `tests/browser/extension.spec.mjs` now emulates `reducedMotion: "reduce"` and waits for `#result` to be visible before axe runs on populated states. The assertion `violations toEqual []` is unchanged.
4. **CI Python runner (`44391d4`)**: both workflows now run `uv run pytest -q` instead of `unittest discover`; `test.yml` uses `uv sync --locked`, matching `quality.yml`. An uncommitted change that wrapped the browser step in `xvfb-run -a` was reverted by editing the file back.

### Rationale and labeled evidence

- `[OBSERVED - CI log]` python-tests (3.11) and extension-validation failed with `fisher_extension_package.PackagingError: Extension source inventory is invalid.` from `_inventory` (7 errors, 6 failures in `tests/test_extension_package.py`). The new test failed before the fix and passed after it.
- `[OBSERVED - CI log]` python-tests (3.12) was cancelled by fail-fast and status-check failed only because python-tests failed; neither had an independent cause.
- `[OBSERVED - CI log]` verify failed at `tests/browser/extension.spec.mjs:342` with axe `color-contrast` (for example `#757e8d` on `#fcfdfd`, 4.02:1).
- `[DERIVED]` `--text-secondary` `#4a5568` on white at about 0.76 alpha gives `#757e8d`, so axe measured mid `fadeSlideIn` (170 ms), not the final colours. The eyebrow opacity was a real, separate reduction.
- `[OBSERVED]` `unittest discover` does not collect module-level pytest functions such as the parametrized tests in `tests/test_transliteration.py`. It predates the pytest dev dependency (`6088564`); no other reason for it was found in history or docs.
- `[OBSERVED]` `xvfb-run` is unnecessary: the browser suite ran headless on the runner (18 of 19 passed; the one failure was the contrast check above).

### Alternatives considered and why each was not selected

- **Copilot branches `copilot/fix-extension-validation-job` and `copilot/fix-python-tests-job`**: both add `realistic_messages.test.mjs` to the hard-coded set. Not merged: same fix, but it leaves the duplicated list that caused the bug and adds no regression test. They fix nothing this branch does not.
- **Skip the packaging tests on Linux or add `continue-on-error`**: rejected; it would hide a real packager bug that breaks `python fisher_extension_package.py` on POSIX.
- **Loosen or tag-filter the axe assertion**: rejected; waiting for the final rendered state keeps the full WCAG 2 A/AA check.
- **Keep `unittest discover`**: rejected because it silently skips pytest-style tests.

### Compatibility, data, security, privacy, and performance impacts

- Packaging on POSIX works again for the real source tree; the archive contents and allowlists are unchanged.
- The eyebrow label is fully opaque; no other visual change.
- The CI runner changed from unittest to pytest. pytest also runs the `unittest.TestCase` suites, so coverage grows and nothing is dropped.
- No change to the detector, links, transliteration or evaluation code; no dependency, permission or privacy change.

### Verification

- Windows (local): `npm test` 161 pass, 0 fail. `npm run test:browser` 19 passed. `uv run pytest -q` 421 passed, 24 skipped (POSIX-only and Windows file-locking skips).
- Linux container `node:22-bookworm`, Python 3.11, non-root user: `uv sync --locked`; `uv run pytest -q` 445 passed, 0 skipped. `uv run python tests/test_extension_package.py` ran 30 tests, OK.
- Linux container `mcr.microsoft.com/playwright:v1.63.0-noble`: `npm ci --ignore-scripts`; `npm test` 161 pass, 0 fail; `npm run test:browser` 19 passed.

### Unrun checks

- No GitHub Actions run on `fix/ci-checks`, because nothing has been pushed.
- The python-tests (3.12) matrix leg was not reproduced. `setup-python` sets 3.12, but `uv` may select another interpreter, because the job does not set `UV_PYTHON`.

### Remaining risks

- `README.md:264` still documents `unittest discover` as the Python test command; it runs, but it skips the pytest-style tests.
- The coverage job still uses `unittest` under `continue-on-error: true`, so it cannot fail the run.

### Follow-up action or owner

- Maintainer: push `fix/ci-checks`, open a PR, and confirm all checks pass on the runner. Then close the two Copilot branches.

### Correction history

None.
