# Fisher Prior-Art Search Log

> Status: internal, non-exhaustive evidence log. Last updated: 19 August 2026.
> This is a research-planning record, not a patentability, freedom-to-operate,
> trademark, or legal opinion.

## 1. Search question

The working question is whether prior work already discloses Fisher's complete
proposed coupling: calibrated uncertainty over multiple Romanized Indic
interpretations; shared path encoding; path-specific typed semantic
actor/action/asset/destination relations and risk; probability-weighted
marginalization of both relations and risk; path-disagreement measurement; and
entropy-plus-disagreement selective prediction for low-false-positive phishing
detection.

The search does **not** treat transliteration, lattices, multilingual encoders,
semantic graphs, brand/domain checks, calibration, abstention, explanations, or
conversation memory as individually novel.

## 2. Evidence labels and decision rule

- `OBSERVED`: the linked primary source directly describes the stated element.
- `DERIVED`: the boundary follows from multiple observed elements but still needs
  experimental or professional review.
- `UNKNOWN`: the current search cannot establish the claim.

A missing search hit is not evidence of novelty. Fisher may use “we propose” and
“we evaluate” until an exhaustive scientific review and, if pursued, a
professional patent search support stronger wording. “First,” “patentable,” and
“freedom to operate” remain prohibited.

## 3. Search sessions

### 19 August 2026 — scientific and patent pressure search

Searched ACL Anthology, arXiv, and Google Patents with combinations of:

- `phishing smishing multilingual code-mixed Indic transliteration dataset`;
- `multilingual phishing detection transliteration uncertainty semantic graph`;
- `transliteration lattice uncertainty classification Romanized Indic n-best marginalization`;
- `Indic phishing detection SMS Hindi Tamil Telugu code mixed`;
- `phishing claimed organization destination domain requested action urgency`;
- `phishing conversation risk intent PII request`; and
- `transliteration uncertainty phishing semantic intent graph`.

The search emphasized titles, abstracts, and patent claims. It did not constitute
an element-by-element legal claim chart or a systematic-review database export.

### Earlier project-source checks retained in the register

The project also inspected the IEEE DataPort Dravidian spam-SMS landing record,
its DataCite DOI metadata, the authors' dataset page, and the associated SMSDHL
preprint. No raw dataset was downloaded. Those checks are preserved in
`docs/CHANGE_DECISION_LOG.md`; this log carries their research-use boundary
forward.

## 4. Scientific evidence map

| Element | Primary evidence inspected | Observed boundary for Fisher |
| --- | --- | --- |
| Uncertain lattice inputs with posterior scores | [Sperber et al., EMNLP 2017](https://aclanthology.org/D17-1145/) represent alternative input sequences and posterior probabilities; [Durrani et al.](https://aclanthology.org/W12-4410/) and [Su et al.](https://arxiv.org/abs/1803.05071) provide additional lattice precedent | N-best/lattice uncertainty and posterior-aware neural processing are established |
| Indic transliteration resources and evaluation | [Aksharantar](https://aclanthology.org/2023.findings-emnlp.4/), [large-scale Indic transliteration evaluation](https://aclanthology.org/2021.eacl-main.303/), and [context-aware South Asian transliteration](https://direct.mit.edu/coli/article/50/2/475/119145/) | Candidate generation, Romanized-to-native conversion, context use, and large paired resources are enabling prior work, not Fisher contributions |
| Indic multilingual representation and language identification | [MuRIL](https://arxiv.org/abs/2103.10730), [IndicBERT v2](https://aclanthology.org/2023.acl-long.693/), [IndicLID](https://arxiv.org/abs/2305.15814), [informally Romanized LID](https://aclanthology.org/2025.emnlp-main.117/), and [XLM-R](https://arxiv.org/abs/1911.02116) | Encoders and language routing are comparators or infrastructure |
| Non-English smishing datasets and explanation systems | [MOZ-Smishing](https://aclanthology.org/2025.africanlp-1.23/) and [KorSmishing Explainer](https://aclanthology.org/2024.emnlp-industry.47/) | Fisher is not the first non-English, multilingual, crowdsourced, LLM-assisted, or explainable smishing project |
| Typed phishing relations and semantic analysis | [PhishSigma++](https://arxiv.org/abs/2605.11619), [SmishTank](https://arxiv.org/abs/2402.18430), and [text-based phishing detection](https://arxiv.org/abs/2111.01676) | Typed entities/relations, semantic signals, and text-only phishing classification are crowded components |
| Calibration and selective prediction | [Temperature scaling](https://proceedings.mlr.press/v70/guo17a.html) and [selective classification](https://arxiv.org/abs/1705.08500) | Calibration, uncertainty scores, coverage/risk analysis, and abstention are established |

**DERIVED candidate gap:** this session did not identify a primary source that,
in one standalone-message Indic phishing system, carries a calibrated
Romanization candidate distribution through path-specific typed relation and
risk inference, marginalizes both outputs, and uses semantic path instability
with predictive entropy for selective low-FPR decisions. This is only a search
hypothesis. It remains `UNKNOWN` until broader database, citation-chain, code,
thesis, product, and patent searches and the factorial experiment are complete.

## 5. Patent-pressure map

| Document | Observed pressure | Fisher consequence |
| --- | --- | --- |
| [US10277628B1](https://patents.google.com/patent/US10277628) | purported authoritative entity, requested story/action, and deceptive URL indicators | Generic actor/action/domain reasoning cannot be claimed |
| [US12531898B2](https://patents.google.com/patent/US12531898B2/en) | spoofed-message source/domain-owner consistency and mitigation | Generic entity–destination authorization comparison is high-pressure prior art |
| [US20210344711A1](https://patents.google.com/patent/US20210344711A1/en) | candidate-brand and authorized destination comparison | Brand/destination comparison is not the invention candidate |
| [US11924245B2](https://patents.google.com/patent/US11924245B2/en) | URL plus action, urgency, consequence, or threat-style intent evidence | Intent-feature fusion and urgency are crowded |
| [WO2026075707A1](https://patents.google.com/patent/WO2026075707A1/en) | dialog-turn intent, PII-request classification, accumulated conversation risk, and warning action | Conversation Risk Memory is deferred and cannot anchor Paper 1 novelty |

Other patent families already listed in
[Publication and IP Gate](PUBLICATION_IP_GATE.md) remain in scope for professional
review. Patent status, claim construction, family relationships, prosecution
history, ownership, inventorship, and legal overlap are `UNKNOWN`.

## 6. Public dataset boundary

The [IEEE DataPort Dravidian spam-SMS record](https://ieee-dataport.org/documents/spam-sms-dravidian-languages),
[DataCite DOI metadata](https://api.datacite.org/dois/10.21227/dcym-pd69), and
[authors' dataset page](https://sites.google.com/cse.nits.ac.in/ramanujamge/publications/datasets-offered)
identify a potentially relevant auxiliary source. Its raw rows, exact schema,
rights, label construct, duplicates, privacy state, and active-artifact safety
have not been audited in this repository. Spam/ham is not automatically
phishing/benign.

Any authorized public-authentic row and every descendant are limited to
`development` or `external_test`, require independent visible-input Fisher
annotation, and cannot enter the ontology pilot, calibration, safety-threshold,
or primary-test partitions. No public row has been downloaded or approved.

## 7. Search gaps

The following remain required before a strong novelty statement or public
disclosure decision:

- systematic searches in Scopus, Web of Science, IEEE Xplore, ACM Digital
  Library, Google Scholar citation chains, ProQuest theses, and relevant Indian
  repositories;
- backward and forward citation review for every close scientific source;
- patent-family, classification, citation, non-US, continuation, abandoned-case,
  and prosecution-history searches by a qualified professional;
- code, benchmark, model-card, product, standards, preprint, workshop, and demo
  searches, including non-English queries;
- exact Fisher element-by-element comparison rather than keyword similarity;
- Fisher name/trademark/publication-title clearance; and
- an update immediately before invention disclosure, preprint, submission, or
  public release.

## 8. Current decision

Continue the internal research under the narrow coupled hypothesis. Treat every
component as prior art, run the frozen 2×2 plus capacity/supervision controls,
and route a null or mixed result honestly. Before any public technical
disclosure, follow the sequence: internal invention disclosure, professional
review, explicit file/no-file decision, then publication authorization.
