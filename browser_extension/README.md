# Fisher v0.4 — message and link checks

Fisher helps you pause and inspect a suspicious message or link. The Chrome/Edge popup and local command-line tool share the same deterministic engine. Choose Message to check a pasted message, or Link check to inspect an address without opening it. Explicitly selected top-frame page text can also be checked in Message mode.

This is an **unvalidated research prototype**, not a phishing classifier and not a guarantee that a message is safe or malicious. `No clear pattern match` is explicitly not a safety result. Its rule-based explanations are intended to support, not replace, independent verification.

## Load unpacked

1. Open `chrome://extensions` in Chrome or `edge://extensions` in Edge.
2. Enable developer mode.
3. Choose **Load unpacked** and select this `browser_extension` directory.
4. Pin Fisher. Choose **Message** or **Link check**, paste an input, and press **Analyze locally**. In Message mode you can also select page text, open Fisher, and press **Analyze selected text on this page**.

Use **Ctrl+Enter** / **Cmd+Enter** to analyze. Example buttons fill a synthetic input for you to inspect before running. Clear removes the current input and result; edits and mode changes invalidate older results. Nothing runs as you type.

## What the checks mean

- **High-risk patterns found** (`high`): an existing non-negated sensitive request occurs with a link or urgency cue. Verify the request through an independently obtained official channel before acting.
- **Worth a closer look** (`review`): one or more configured signals deserve attention. Legitimate warnings, normal links, and benign internationalized domains can also trigger review.
- **No clear pattern match** (`no_match`): no configured combination matched; this is not a safety verdict.
- **Could not analyze** (`cannot_analyze`): the input is empty, unsupported, malformed, or exceeds a bound. No partial input is presented as a complete check.

Link checks use local URL parsing. Findings can include embedded credentials before the host, plain HTTP, IP hosts, internationalized/punycode hostnames, non-default ports, deep hostnames, and known shortening services. Message mode also recognizes bounded defanged spelling; Link check requires a complete HTTP(S) address or bare domain. These describe structure, not reputation, domain ownership, or brand legitimacy. HTTPS does not establish legitimacy. The tool never resolves DNS, follows redirects, downloads a link, or exposes hostnames and query values in its report.

Message input is limited to 20,000 Unicode code points. URL inspection also has a 2,048-character candidate limit and a 32-candidate budget. A budget-limited scan is explicitly incomplete and cannot yield a no-match result.

## Local command-line companion

Node.js 22+ is sufficient; there are no runtime packages to install. Run from the repository root:

```console
node fisher.mjs --help
node fisher.mjs analyze --format json < /path/to/message.txt
node fisher.mjs analyze --mode url < /path/to/link.txt
node fisher.mjs batch --format json < /path/to/messages-one-per-line.txt
```

Analyze reads one complete input, including multiline messages. Batch reads one input per LF-delimited physical line (CRLF supported), up to 500 lines and 1 MiB of valid UTF-8. Blank or unsupported lines count as `cannot_analyze`; they are not dropped. Batch output contains only aggregate risk counts. Reports never contain source text, per-row identifiers, link addresses, or learned probabilities. All input comes from stdin to avoid putting message contents in command arguments.

Exit `0` means a report was produced for every input, regardless of the risk level. Exit `1` means at least one input could not be analyzed or input processing failed. Exit `2` means invalid command usage. No CLI command writes files; redirection is controlled by the caller.

## Permissions and data handling

The manifest requests exactly `activeTab` and `scripting`. `activeTab` is temporary permission associated with the user invoking the extension; it is not a standing host permission. The code queries the active tab and injects the selection reader only after the user presses **Analyze selected page text**. Injection is limited to frame `0` (the top frame), so selections inside embedded frames are not read. The bounded traversal reads text data only after a text node is confirmed to intersect the browser selection. It does not read the page URL, title, HTML, form values, or unselected page text.

There are no host permissions, content scripts, background worker, network calls, remote code, telemetry, messaging, or storage APIs. Text can exist transiently in page memory, the browser's script-result transfer, and popup memory while analysis runs; the extension makes no secure-erasure claim. At most 20,000 Unicode code points of selected text can cross into the popup. Longer input is rejected in full rather than returned as a partial string, and traversal is also bounded by a text-node limit. Selected text is not copied into the textarea or rendered in results. Results contain generic evidence categories, never the matched text. Displayed web addresses remain plain text and are never converted into clickable links.

## Architecture

- `popup.html`, `popup.js`, and `styles.css`: accessible user-triggered interface, cancellation of stale selection work, and safe text-only rendering.
- `analyzer.mjs`: versioned report shared with the CLI; combines unchanged text rules with structural link observations and next steps.
- `links.mjs`: bounded local URL extraction and structure checks; no network or reputation data.
- `selection.mjs`: validates the active tab and injected result, then performs a bounded top-frame selection read in an isolated world after the explicit button action.
- `detector.mjs`: fail-closed input bounding, Unicode compatibility normalization, removal of invisible formatting characters, transparent multilingual/romanized signal rules, protective-context labeling, the frozen review-only profile described below, and deterministic category-combination decisions.
- `tests/*.test.mjs`: dependency-free Node tests for the analyzer, detector, permission bridge, UI controller, Unicode bounds, privacy, and stale-result cancellation.
- `../fisher.mjs`: stdin-only local companion, excluded from the browser ZIP.

The rules cover a deliberately small set of English, Hindi/Devanagari, Tamil, Telugu, and Romanized Indic signals. They do not establish language coverage, accuracy, robustness, or research performance.

## Frozen sensitive-token lookalike profile

`FISHER_GC_SENSITIVE_V1` is a tiny, purpose-specific v0.2 modification. After the existing local normalization, it examines whole letter/mark/number tokens of at most eight Unicode code points. A frozen substitution table is considered only when it produces exactly one of `otp`, `pin`, `password`, `passcode`, `cvv`, or `kyc`, and at least one configured substitution was required. The finding adds a generic **review** reason only. It never supplies credential evidence or promotes a result to high risk.

This profile does not rewrite, display, hash, persist, or report the examined token or its internal comparison form. Exact configured tokens also receive the review floor when they appear inside a dotted string; that is token evidence, not a domain assessment. It is a frozen partial subset, not general Unicode lookalike handling, Unicode Technical Standard #39 conformance, language or script detection, domain safety checking, or brand-impersonation detection.

## Test

Run from the repository root:

```text
npm test
uv run --python 3.11 python -m unittest -q tests.test_extension_package
```

For real Chromium interaction and automated accessibility checks:

```console
npm ci
npx playwright install chromium
npm run test:browser
```

Browser tests install the real unpacked extension into a temporary Chromium profile and use synthetic fixtures. They exercise paste/link interactions, the actual toolbar action, selected text, empty/restricted pages, and automated accessibility. Test-only DevTools extension debugging never touches your existing browser profile. Playwright and axe are development-only dependencies; neither is bundled into the extension. The tests follow [Playwright's Chromium extension workflow](https://playwright.dev/docs/chrome-extensions), the experimental [DevTools extension commands](https://chromedevtools.github.io/devtools-protocol/tot/Extensions/), and [Chrome's temporary activeTab permission model](https://developer.chrome.com/docs/extensions/develop/concepts/activeTab). Automated checks do not replace human language review or testing with assistive technology. Microsoft Edge and non-Chromium browsers are not covered by this suite.

The repository's `Fisher checks` workflow runs unit tests, Chromium checks, Python tests, and ZIP construction on GitHub once this source is pushed. It has read-only repository permissions and does not publish artifacts or deploy a release.

Heuristic limits remain: spaced `word [.] com` can be explanatory prose or a defanged domain, so it can trigger review. Bare-domain extraction is a candidate scan, not exhaustive recognition. Existing top-frame selection joins DOM text nodes without layout separators; iframe, form-control, shadow-DOM, and multi-range selections are limited. Language coverage, accuracy, and false-positive rate are unmeasured.

## Build the deterministic local package

From the repository root, run:

```text
uv run --python 3.11 python -m fisher_extension_package
```

The command takes no arguments and refuses to replace an existing destination. It creates one file only:

```text
outputs/browser_extension/fisher-scam-signal-prototype-v0.4.0.zip
```

The ZIP contains eight runtime files: `analyzer.mjs`, `links.mjs`, `detector.mjs`, `manifest.json`, `popup.html`, `popup.js`, `selection.mjs`, and `styles.css`. Tests, CLI, development dependencies, and this README are excluded. On success, the command prints the project-relative archive path, member count, byte count, and SHA-256 digest. Verify the digest independently with:

```text
LC_ALL=C shasum -a 256 outputs/browser_extension/fisher-scam-signal-prototype-v0.4.0.zip
```

Creating this local deterministic archive does not sign, publish, release, or establish store readiness for the extension. Publication requires a separate review and explicit authorization.

If the command reports an error after the atomic archive link becomes visible, it deliberately does not delete the public archive path. Inspect the path and archive contents manually, then remove the file only after confirming it is the intended target. A later build will continue to refuse that existing path.
