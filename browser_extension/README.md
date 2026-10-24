# Fisher v0.6 — message and link checks

Fisher helps you pause and inspect a suspicious message or link. The Chrome/Edge popup and local command-line tool share the same deterministic engine. Choose Message to check a pasted message, or Link check to inspect an address without opening it. You can also right-click selected page text and choose "Check selection with Fisher".

This is an **unvalidated research prototype**, not a phishing classifier and not a guarantee that a message is safe or malicious. `No clear pattern match` is explicitly not a safety result. Its rule-based explanations are intended to support, not replace, independent verification.

## Load unpacked

1. Open `chrome://extensions` in Chrome or `edge://extensions` in Edge.
2. Enable developer mode.
3. Choose **Load unpacked** and select this `browser_extension` directory.
4. Pin Fisher. Choose **Message** or **Link check**, paste an input, and press **Analyze locally**. You can also right-click any selected text and choose **Check selection with Fisher**.

If you received the ZIP package, extract it first, then choose the extracted
folder containing `manifest.json` in **Load unpacked**. If Fisher is already
loaded from this repository, press its **Reload** button on the extensions page
to use the current code, then reopen the popup or workspace.

Use **Ctrl+Enter** / **Cmd+Enter** to analyze. Example buttons fill a synthetic input for you to inspect before running. Message and Link check keep separate drafts in popup memory while the popup remains open. Switching modes restores that mode's draft and invalidates an older result. Every result is labeled as a message, link, or selected-text check. **Edit input** hides the result, keeps the active draft, and returns focus to the input; **Clear** removes the active draft and result. Nothing runs as you type.

## A roomier workspace

Choose **Open a roomy workspace** (↗) in the popup header to open an independent tab with
the input and findings side by side. When opened from the header, it starts empty: neither
your draft nor the selected page text is transferred. When a workspace tab is opened from
the menu, it starts with the selected text analyzed but never copied into the draft. Both views adapt to narrow screens
and the system's light or dark appearance, respect reduced motion, and retain visible keyboard
focus and high-contrast selection states.

Try the Hindi, Tamil, Telugu, and everyday-message samples alongside the original
delivery and account examples. These are synthetic demonstrations of the current
rules, not a language-coverage evaluation. Composition input does not trigger the
Ctrl/Command+Enter shortcut until composition ends.

Results show the number of reported check entries and inspected addresses. These
counts are not a confidence score or an exhaustive count of rules attempted;
repeated structural findings may share one reported check. Unanalyzable input
shows a dash instead of an uncomputed count. **Explore the checks** expands or
collapses the available details.

**Save report** downloads `fisher-analysis-report.json` only after an explicit
click. It contains the current generic engine findings, result context, and
limitations, excluding submitted text, link addresses, and arbitrary extra
fields. Editing, clearing, switching modes, or starting a new selection check
invalidates the previous downloadable report. The browser controls where the
file is saved; Fisher retains no report history. Closing a window discards its
drafts. A downloaded report remains on disk until you remove it.

## Bulk checking and text-file import

Choose **Bulk check**, then select whether each line contains a message or a
link. Paste inputs or choose **Import .txt**. Importing fills the editor without
starting analysis. **Load a sample batch** provides synthetic inputs to try the
workflow. Each mode keeps its own draft in window memory.

Browser batches allow at most 100 physical lines and 100,000 Unicode code points
in total. Files must be valid UTF-8 and no larger than 1 MiB. LF and CRLF line
endings are supported; one final newline is treated as a terminator. Internal
blank lines remain numbered inputs and receive `cannot_analyze`. Empty batches
and batches over the overall limits are rejected without a partial report.
Individual inputs still have the existing 20,000-character message or
2,048-character link limit. An oversized individual line gets its own
`cannot_analyze` result while the other lines can be checked.

**Analyze batch** processes each line independently and shows progress. **Cancel**
discards the incomplete run. Editing, clearing, switching modes or input type,
and starting a newer import or analysis invalidate older work. A failed import
keeps your previous draft and removes outdated results.

Completed batches show counts for all four result categories. Filter the list
and select a line to inspect its generic evidence and next steps. Line numbers
match the original physical input, including blanks. **Locate input** selects
that line in the original editor without copying it elsewhere. The result list never
repeats submitted text or link addresses. **Save batch** downloads a JSON report
with generic findings, counts, and line numbers; filenames and source input are
excluded. This file has no automatic expiry and remains wherever the browser
saves it. The browser limits are deliberately smaller than the CLI limits to
keep this interactive workflow bounded.

## What the checks mean

- **High-risk patterns found** (`high`): an existing non-negated sensitive request occurs with a link or urgency cue. Verify the request through an independently obtained official channel before acting.
- **Worth a closer look** (`review`): one or more configured signals deserve attention. Legitimate warnings, normal links, and benign internationalized domains can also trigger review.
- **No clear pattern match** (`no_match`): no configured combination matched; this is not a safety verdict.
- **Could not analyze** (`cannot_analyze`): the input is empty, unsupported, malformed, or exceeds a bound. No partial input is presented as a complete check.

Link checks use local URL parsing. Findings can include embedded credentials before the host, plain HTTP, IP hosts, internationalized/punycode hostnames, non-default ports, deep hostnames, and known shortening services. Message mode also recognizes bounded defanged spelling. It accepts syntactically valid alphabetic suffixes without consulting a live domain registry, so an unlisted suffix can still be checked; filename-like dotted text can conservatively trigger review. Link check requires one complete HTTP(S) address or bare domain. These findings describe structure, not reputation, domain ownership, or brand legitimacy. HTTPS does not establish legitimacy. The tool never resolves DNS, follows redirects, downloads a link, or exposes hostnames and query values in its report.

Message input is limited to 20,000 Unicode code points; Link check input is limited to 2,048. The popup shows the active limit and an inline correction before an oversized draft can be analyzed. Embedded URL inspection also has a 2,048-code-point candidate limit and a 32-candidate budget. A budget-limited scan is explicitly incomplete and cannot yield a no-match result.

Link inspection also checks immediate embedded destinations in these query
fields (matched case-insensitively): `url`, `redirect`, `redirect_url`,
`redirect_uri`, `next`, `continue`, `return`, `return_to`, `destination`, and
`target`. Values are decoded once by the URL query parser. HTTP(S) addresses and
protocol-relative `//` addresses receive separate, generic **Embedded
destination** findings. Protocol-relative values are inspected using HTTPS as
a local parsing convention. Relative paths such as `/dashboard`, bare domains,
and double-encoded addresses are not decoded further or treated as destinations.

At most 32 query pairs and four qualifying embedded destinations are considered
per submitted address. Malformed or unsupported absolute destinations and
exceeded limits produce an incomplete-inspection finding. Inspection does not
recurse into another destination's query fields. Counts in `linkSummary` remain
counts of submitted addresses; an embedded finding flags its containing address
without adding another submitted-address count. Literal unencoded HTTP(S)
schemes inside message text retain the existing scanner behavior and may be
recognized as separate addresses, while encoded destinations receive nested
findings. These observations can trigger review but do not show that a redirect
occurred, predict its final destination, or establish malicious intent.

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

Users can right-click any selected text and choose **Check selection with Fisher**. The right-click path uses the browser's selection string, which can include text inside iframes. The right-click item sends only the text you selected, held in memory by the background service worker for about 30 seconds, or until the browser stops the extension worker, until the popup reads it, with no automatic scanning. If a workspace tab is opened from the menu, it starts with the selected text analyzed but never copied into the draft.

The manifest requests exactly one permission: `contextMenus`. It declares no host permissions, content scripts, `tabs`, or `notifications`, so Fisher never reads a page unless you select text and trigger the context menu. There is no automatic page scan and no page-analysis report.

The sections above describe only the explicit selection path. There are no network calls, remote code, telemetry, or storage APIs. Text can exist transiently in background worker memory and popup memory while analysis runs; the extension makes no secure-erasure claim. At most 20,000 Unicode code points of selected text can cross into the popup. Longer input is rejected in full rather than returned as a partial string. Selected text is not copied into the textarea or rendered in results. Results contain generic evidence categories, never the matched text. Displayed web addresses remain plain text and are never converted into clickable links.

## Architecture

- `popup.html`, `popup.js`, and `styles.css`: accessible user-triggered interface, cancellation of stale selection work, and safe text-only rendering.
- `background.js`: background service worker registering the context menu and temporarily holding selection text in memory for about 30 seconds, or until the browser stops the extension worker.
- `icon.svg` and the derived PNG sizes: the Fisher mark used by the installed extension and toolbar.
- `analyzer.mjs`: versioned report shared with the CLI; combines message-rule results, structural link observations, and next steps.
- `links.mjs`: canonical bounded local URL extraction and structure checks; locator-shaped and email-shaped spans are masked before message semantic matching so their host, path, and address words do not become message cues. It uses no network or reputation data.
- `detector.mjs`: fail-closed input bounding, Unicode compatibility normalization, removal of invisible formatting characters, transparent multilingual/romanized signal rules, protective-context labeling, the frozen review-only profile described below, and deterministic category-combination decisions.
- `tests/*.test.mjs`: dependency-free Node tests for the analyzer, detector, permission bridge, UI controller, Unicode bounds, privacy, and stale-result cancellation.
- `../fisher.mjs`: stdin-only local companion, not part of the extension.

The rules cover a deliberately small set of English, Hindi/Devanagari, Tamil, Telugu, and Romanized Indic signals. They do not establish language coverage, accuracy, robustness, or research performance.

## Frozen sensitive-token lookalike profile

`FISHER_GC_SENSITIVE_V1` is a tiny, purpose-specific v0.2 modification. After the existing local normalization, it examines whole letter/mark/number tokens of at most eight Unicode code points. A frozen substitution table is considered only when it produces exactly one of `otp`, `pin`, `password`, `passcode`, `cvv`, or `kyc`, and at least one configured substitution was required. The finding adds a generic **review** reason only. It never supplies credential evidence or promotes a result to high risk.

This profile does not rewrite, display, hash, persist, or report the examined token or its internal comparison form. Locator-shaped and email-shaped spans are masked before semantic and sensitive-token matching, so words inside their host, path, user-information, or email text do not become message evidence. It is a frozen partial subset, not general Unicode lookalike handling, Unicode Technical Standard #39 conformance, language or script detection, domain safety checking, or brand-impersonation detection.

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

Browser tests install the real unpacked extension into a temporary Chromium profile and use synthetic fixtures. They exercise paste/link interactions, the actual toolbar action, selected text, and automated accessibility. Test-only DevTools extension debugging never touches your existing browser profile. Playwright and axe are development-only dependencies; neither is bundled into the extension. The tests follow [Playwright's Chromium extension workflow](https://playwright.dev/docs/chrome-extensions) and the experimental [DevTools extension commands](https://chromedevtools.github.io/devtools-protocol/tot/Extensions/). Automated checks do not replace human language review or testing with assistive technology. Microsoft Edge and non-Chromium browsers are not covered by this suite.

The repository's `Fisher checks` workflow runs unit tests, Chromium checks, and Python tests on GitHub once this source is pushed. It has read-only repository permissions and does not publish artifacts or deploy a release.

Heuristic limits remain: spaced `word [.] com` can be explanatory prose or a defanged domain, so it can trigger review. Message-mode dotted candidates accept alphabetic suffixes without a live registry, which can conservatively treat filename-like text as an address. Bare-domain extraction is a bounded candidate scan, not exhaustive recognition. A later literal HTTP/HXXP scheme in the same whitespace-free token is conservatively treated as another address after an earlier recognized locator; this keeps chained addresses masked but can split an unusual path containing a literal scheme. Recognized email spans require a domain-shaped suffix, so malformed dotless address-like text remains outside that masking rule. Right-click selection uses the browser's selection string, which can include text inside iframes. Language coverage, accuracy, and false-positive rate are unmeasured.
