import { analyzeContent } from "./analyzer.mjs";
import { MAX_INPUT_CHARS } from "./detector.mjs";
import { MAX_URL_CODE_POINTS } from "./links.mjs";
import { requestSelectedPageText } from "./selection.mjs";

const SUPPORTED_MODES = new Set(["message", "url", "batch"]);
const SUPPORTED_BATCH_KINDS = new Set(["message", "url"]);
const BATCH_FILTERS = new Set([
  "all",
  "high",
  "review",
  "no_match",
  "cannot_analyze",
]);
const MAX_BATCH_CODE_POINTS = 100_000;
const MAX_BATCH_LINES = 100;
const MAX_BATCH_FILE_BYTES = 1_048_576;

const MODE_INPUT = {
  message: {
    limit: MAX_INPUT_CHARS,
    noun: "message",
    hint: `Nothing leaves your device. Draft stays in this window. Up to ${MAX_INPUT_CHARS.toLocaleString("en-US")} characters. Press Ctrl/⌘ + Enter to analyze.`,
  },
  url: {
    limit: MAX_URL_CODE_POINTS,
    noun: "link",
    hint: `The link is inspected as text only—it is never opened. Nothing leaves your device. Up to ${MAX_URL_CODE_POINTS.toLocaleString("en-US")} characters. Press Ctrl/⌘ + Enter to analyze.`,
  },
  batch: {
    limit: MAX_BATCH_CODE_POINTS,
    noun: "batch",
    hint: `Add one item per line. Up to ${MAX_BATCH_LINES} lines and ${MAX_BATCH_CODE_POINTS.toLocaleString("en-US")} characters total. Blank lines are kept as items that cannot be analyzed.`,
  },
};

const PRESENTATION = {
  high: {
    heading: "High-risk patterns found",
    summary:
      "Pause. Do not pay, open links, install software, or share sensitive information before verifying the request independently.",
  },
  review: {
    heading: "Worth a closer look",
    summary:
      "Some patterns deserve caution. Verify the sender, destination, and request using a trusted route.",
  },
  no_match: {
    heading: "No clear pattern match",
    summary:
      "The configured checks found no clear combination. This is not a guarantee that the content is safe.",
  },
  cannot_analyze: {
    heading: "Could not analyze",
    summary:
      "No risk result was produced. Check the input or try a shorter, permitted excerpt.",
  },
};

const SELECTION_FAILURE_REASONS = {
  empty: "No selected page text was found. Select text or paste it instead.",
  too_long:
    "Selected page text exceeds the 20,000-character limit; nothing was analyzed. Select a shorter excerpt instead.",
  too_complex:
    "The selection is too complex to read safely; nothing was analyzed. Paste a shorter excerpt instead.",
  unavailable:
    "Selected page text could not be accessed. Paste the text to analyze it instead.",
};

const EXAMPLES = {
  message: {
    urgent:
      "Urgent: your delivery is on hold. Pay the small redelivery fee now at parcel-update.example.",
    account:
      "Your bank account will be suspended today. Share your OTP to complete verification.",
    hindi:
      "तुरंत कार्रवाई करें: आपका खाता बंद हो जाएगा। सत्यापन के लिए अपना OTP साझा करें।",
    tamil:
      "அவசரம்: உங்கள் கணக்கு இன்று முடக்கப்படும். சரிபார்க்க OTP-ஐ பகிரவும்.",
    telugu:
      "అత్యవసరం: మీ ఖాతా ఈరోజు నిలిపివేయబడుతుంది. ధృవీకరణ కోసం OTP పంచుకోండి.",
    benign:
      "Hi, the team lunch moved to 1:00 PM. Please reply if you have any dietary preferences.",
  },
  url: {
    urgent: "http://192.0.2.1:8080/example",
    account: "https://example.com",
  },
};

const EXAMPLE_LABELS = {
  message: { urgent: "Urgent delivery", account: "Account alert" },
  url: { urgent: "IP address", account: "HTTPS address" },
};

const RESULT_CONTEXT = {
  message: "Message check",
  url: "Link check",
  selection: "Selected text check",
  batch: "Batch check",
};

const REPORT_LIMITATION =
  "This deterministic pattern report is not a safety guarantee, reputation check, live blocklist, or machine-learning result.";
const REPORT_PRIVACY =
  "Input stays in this window. Only a report you explicitly save is downloaded.";
const REPORT_FILENAME = "fisher-analysis-report.json";
const BATCH_REPORT_FILENAME = "fisher-batch-report.json";

const BATCH_EXAMPLES = {
  message: [
    "Urgent: your account will close today. Share your OTP now.",
    "Hi, the team lunch moved to 1:00 PM.",
    "",
    "Read the notes at https://example.com/reference.",
  ].join("\n"),
  url: [
    "https://example.com",
    "http://192.0.2.1:8080/example",
    "",
    "https://subdomain.example.org/path",
  ].join("\n"),
};

function boundedCodePointCount(value, limit) {
  let count = 0;
  for (const _character of value) {
    count += 1;
    if (count > limit) return { count, overLimit: true };
  }
  return { count, overLimit: false };
}

function safeArray(value) {
  return Array.isArray(value) ? value : [];
}

function safeStrings(value) {
  return safeArray(value).filter((item) => typeof item === "string");
}

function buildDownloadReport(analysis, context, lineNumber, contextLabel) {
  const inspected = analysis?.linkSummary?.inspected;
  const flagged = analysis?.linkSummary?.flagged;
  const limited = analysis?.linkSummary?.limited;
  const downloadReport = {
    report: {
      engineVersion:
        typeof analysis?.engineVersion === "string" ? analysis.engineVersion : "unknown",
      mode: analysis?.mode === "url" ? "url" : "message",
      risk: Object.hasOwn(PRESENTATION, analysis?.risk)
        ? analysis.risk
        : "cannot_analyze",
      reasons: safeStrings(analysis?.reasons),
      nextSteps: safeStrings(analysis?.nextSteps),
      linkSummary: {
        inspected:
          Number.isSafeInteger(inspected) && inspected >= 0 ? inspected : null,
        flagged: Number.isSafeInteger(flagged) && flagged >= 0 ? flagged : null,
        limited: typeof limited === "boolean" ? limited : null,
      },
      checks: safeArray(analysis?.checks)
        .filter(
          (check) =>
            typeof check?.id === "string" &&
            typeof check?.label === "string" &&
            typeof check?.detail === "string",
        )
        .map(({ id, label, detail }) => ({ id, label, detail })),
    },
    context: contextLabel ?? RESULT_CONTEXT[context] ?? RESULT_CONTEXT.message,
    limitation: REPORT_LIMITATION,
    privacy: REPORT_PRIVACY,
  };
  if (Number.isSafeInteger(lineNumber) && lineNumber > 0) {
    downloadReport.lineNumber = lineNumber;
  }
  return downloadReport;
}

function downloadJsonReport(report, documentApi, filename = REPORT_FILENAME) {
  const BlobConstructor = globalThis.Blob;
  const urlApi = globalThis.URL;
  if (
    typeof BlobConstructor !== "function" ||
    typeof urlApi?.createObjectURL !== "function" ||
    typeof urlApi?.revokeObjectURL !== "function"
  ) {
    throw new Error("Download unavailable");
  }
  const anchor = documentApi.createElement("a");
  if (typeof anchor?.click !== "function") throw new Error("Download unavailable");
  const blob = new BlobConstructor([`${JSON.stringify(report, null, 2)}\n`], {
    type: "application/json",
  });
  const objectUrl = urlApi.createObjectURL(blob);
  try {
    anchor.href = objectUrl;
    anchor.download = filename;
    anchor.click();
  } finally {
    urlApi.revokeObjectURL(objectUrl);
  }
}

function splitBatchLines(value) {
  const lines = value.split("\n");
  if (lines.at(-1) === "") lines.pop();
  return lines.map((line) =>
    line.endsWith("\r") ? line.slice(0, -1) : line,
  );
}

function isValidBatchContent(value) {
  if (value === "") return false;
  if (boundedCodePointCount(value, MAX_BATCH_CODE_POINTS).overLimit) return false;
  return splitBatchLines(value).length <= MAX_BATCH_LINES;
}

function genericCannotAnalyze(mode) {
  return {
    engineVersion: "unknown",
    mode,
    risk: "cannot_analyze",
    reasons: ["The local checker encountered an unexpected problem for this item."],
    nextSteps: ["Review this item separately, or try a shorter permitted value."],
    linkSummary: { inspected: 0, flagged: 0, limited: false },
    checks: [],
  };
}

export function createPopupController({
  documentApi,
  chromeApi,
  analyze = analyzeContent,
  readSelection = requestSelectedPageText,
  saveReport,
  expandedWorkspace = false,
  yieldTask = () => new Promise((resolve) => setTimeout(resolve, 0)),
}) {
  const message = documentApi.querySelector("#message");
  const messageLabel = documentApi.querySelector("#message-label");
  const inputHint = documentApi.querySelector("#input-hint");
  const inputError = documentApi.querySelector("#input-error");
  const counter = documentApi.querySelector("#counter");
  const analyzeButton = documentApi.querySelector("#analyze");
  const analyzeLabel = documentApi.querySelector("#analyze-label");
  const selectionButton = documentApi.querySelector("#selection");
  const clearButton = documentApi.querySelector("#clear");
  const messageModeButton = documentApi.querySelector("#mode-message");
  const linkModeButton = documentApi.querySelector("#mode-link");
  const batchModeButton = documentApi.querySelector("#mode-batch");
  const batchOptions = documentApi.querySelector("#batch-options");
  const batchKind = documentApi.querySelector("#batch-kind");
  const batchFile = documentApi.querySelector("#batch-file");
  const batchDemoButton = documentApi.querySelector("#batch-demo");
  const cancelBatchButton = documentApi.querySelector("#cancel-batch");
  const batchProgress = documentApi.querySelector("#batch-progress");
  const examples = documentApi.querySelector("#examples");
  const moreExamples = documentApi.querySelector("#more-examples");
  const urgentExample = documentApi.querySelector("#example-urgent");
  const accountExample = documentApi.querySelector("#example-account");
  const status = documentApi.querySelector("#status");
  const emptyState = documentApi.querySelector("#empty-state");
  const result = documentApi.querySelector("#result");
  const resultContext = documentApi.querySelector("#result-context");
  const risk = documentApi.querySelector("#risk");
  const summary = documentApi.querySelector("#summary");
  const reasons = documentApi.querySelector("#reasons");
  const checks = documentApi.querySelector("#checks");
  const checksGroup = documentApi.querySelector("#checks-group");
  const checksDetails = documentApi.querySelector("#checks-details");
  const resultCheckCount = documentApi.querySelector("#result-check-count");
  const resultLinkCount = documentApi.querySelector("#result-link-count");
  const nextSteps = documentApi.querySelector("#next-steps");
  const nextStepsGroup = documentApi.querySelector("#next-steps-group");
  const linkSummary = documentApi.querySelector("#link-summary");
  const editInputButton = documentApi.querySelector("#edit-input");
  const locateBatchLineButton = documentApi.querySelector("#locate-batch-line");
  const downloadReportButton = documentApi.querySelector("#download-report");
  const batchResults = documentApi.querySelector("#batch-results");
  const batchTotal = documentApi.querySelector("#batch-total");
  const batchHigh = documentApi.querySelector("#batch-high");
  const batchReview = documentApi.querySelector("#batch-review");
  const batchNoMatch = documentApi.querySelector("#batch-no-match");
  const batchCannotAnalyze = documentApi.querySelector("#batch-cannot-analyze");
  const batchFilter = documentApi.querySelector("#batch-filter");
  const batchList = documentApi.querySelector("#batch-list");
  const batchEmptyFilter = documentApi.querySelector("#batch-empty-filter");
  const downloadBatchButton = documentApi.querySelector("#download-batch");
  let generation = 0;
  let currentMode = "message";
  let currentBatchKind = "message";
  let activeResultContext = currentMode;
  let selectionBusy = false;
  let batchBusy = false;
  let activeReport;
  let activeBatchLineNumber;
  let completedBatchRows = [];
  let activeBatchReport;
  const drafts = { message: message.value, url: "", batch: "" };
  const reportSaver =
    saveReport ??
    ((reportToSave, filename) =>
      downloadJsonReport(reportToSave, documentApi, filename));

  function invalidateActiveReport() {
    activeReport = undefined;
    downloadReportButton.disabled = true;
  }

  function setBatchBusy(busy) {
    batchBusy = busy;
    analyzeButton.disabled = busy;
    cancelBatchButton.hidden = !busy;
    cancelBatchButton.disabled = !busy;
    batchKind.disabled = busy;
    batchFile.disabled = busy;
    batchDemoButton.disabled = busy;
    batchProgress.setAttribute("aria-busy", busy ? "true" : "false");
  }

  function clearBatchPresentation() {
    activeBatchLineNumber = undefined;
    completedBatchRows = [];
    activeBatchReport = undefined;
    downloadBatchButton.disabled = true;
    batchResults.hidden = true;
    batchList.replaceChildren();
    batchEmptyFilter.hidden = true;
    batchTotal.textContent = "0";
    batchHigh.textContent = "0";
    batchReview.textContent = "0";
    batchNoMatch.textContent = "0";
    batchCannotAnalyze.textContent = "0";
  }

  function setSelectionBusy(busy) {
    selectionBusy = busy;
    const unavailableInMode = currentMode !== "message" || expandedWorkspace;
    selectionButton.disabled = busy || unavailableInMode;
    selectionButton.hidden = unavailableInMode;
    selectionButton.setAttribute("aria-busy", busy ? "true" : "false");
  }

  function setEmptyState(visible) {
    emptyState.hidden = !visible;
  }

  function hideResult() {
    invalidateActiveReport();
    result.hidden = true;
    result.className = "result";
    activeResultContext = currentMode;
    resultContext.textContent = RESULT_CONTEXT[currentMode];
    editInputButton.textContent = "Edit input";
    locateBatchLineButton.hidden = true;
    risk.textContent = "";
    summary.textContent = "";
    reasons.replaceChildren();
    checks.replaceChildren();
    checksDetails.hidden = true;
    resultCheckCount.textContent = "—";
    resultLinkCount.textContent = "—";
    nextSteps.replaceChildren();
    linkSummary.textContent = "";
    linkSummary.hidden = true;
    setEmptyState(currentMode !== "batch" || batchResults.hidden);
  }

  function addTextItems(container, values) {
    for (const value of values) {
      if (typeof value !== "string" || value === "") continue;
      const item = documentApi.createElement("li");
      item.textContent = value;
      container.append(item);
    }
  }

  function render(analysis, context = currentMode, contextLabel) {
    const normalizedRisk = Object.hasOwn(PRESENTATION, analysis?.risk)
      ? analysis.risk
      : "cannot_analyze";
    const presentation = PRESENTATION[normalizedRisk];
    activeResultContext = Object.hasOwn(RESULT_CONTEXT, context) ? context : "message";
    resultContext.textContent =
      contextLabel ?? RESULT_CONTEXT[activeResultContext];
    editInputButton.textContent =
      activeResultContext === "selection"
        ? "Back to input"
        : activeResultContext === "batch"
          ? "Back to batch"
          : "Edit input";
    locateBatchLineButton.hidden = activeResultContext !== "batch";
    risk.textContent = presentation.heading;
    summary.textContent = presentation.summary;
    result.className = `result risk-${normalizedRisk.replace("_", "-")}`;

    reasons.replaceChildren();
    const evidence = safeArray(analysis?.reasons);
    addTextItems(
      reasons,
      evidence.length > 0
        ? evidence
        : ["No additional evidence detail was available for this result."],
    );

    checks.replaceChildren();
    for (const check of safeArray(analysis?.checks)) {
      if (typeof check?.label !== "string" || typeof check?.detail !== "string") continue;
      const item = documentApi.createElement("li");
      const content = documentApi.createElement("span");
      const label = documentApi.createElement("strong");
      label.textContent = check.label;
      content.append(label);
      content.append(documentApi.createTextNode(check.detail));
      item.append(content);
      checks.append(item);
    }
    checksGroup.hidden = checks.children.length === 0;
    checksDetails.hidden = checks.children.length === 0;

    const inspectedCount = analysis?.linkSummary?.inspected;
    if (normalizedRisk === "cannot_analyze") {
      resultCheckCount.textContent = "—";
      resultLinkCount.textContent = "—";
    } else {
      resultCheckCount.textContent = String(checks.children.length);
      resultLinkCount.textContent =
        Number.isSafeInteger(inspectedCount) && inspectedCount >= 0
          ? String(inspectedCount)
          : "—";
    }

    nextSteps.replaceChildren();
    addTextItems(nextSteps, safeArray(analysis?.nextSteps));
    nextStepsGroup.hidden = nextSteps.children.length === 0;

    const inspected = analysis?.linkSummary?.inspected;
    const flagged = analysis?.linkSummary?.flagged;
    const limited = analysis?.linkSummary?.limited;
    if (
      Number.isSafeInteger(inspected) &&
      Number.isSafeInteger(flagged) &&
      inspected >= 0 &&
      flagged >= 0 &&
      flagged <= inspected &&
      typeof limited === "boolean" &&
      (analysis?.mode === "url" || inspected > 0 || flagged > 0 || limited)
    ) {
      const messages = [
        inspected === 0
          ? "No web addresses were checked."
          : `${inspected} web address${inspected === 1 ? "" : "es"} checked.`,
      ];
      if (flagged > 0) {
        messages.push(
          `${flagged} checked address${flagged === 1 ? "" : "es"} had structural warning cues.`,
        );
      } else if (inspected > 0) {
        const addressNoun = inspected === 1 ? "address" : "addresses";
        const safetyVerb = inspected === 1 ? "is" : "are";
        messages.push(
          `No structural warning cues were found in the checked ${addressNoun}. This does not establish that the checked ${addressNoun} ${safetyVerb} safe.`,
        );
      }
      if (limited) messages.push("Some address candidates could not be checked.");
      linkSummary.textContent = messages.join(" ");
      linkSummary.hidden = false;
    } else {
      linkSummary.textContent = "";
      linkSummary.hidden = true;
    }

    setEmptyState(false);
    result.hidden = false;
    result.focus();
  }

  function supersede() {
    generation += 1;
    invalidateActiveReport();
    setSelectionBusy(false);
    setBatchBusy(false);
    return generation;
  }

  function renderAnalysisFailure(sourceLabel, context) {
    render(
      {
        risk: "cannot_analyze",
        reasons: [
          "The local checker encountered an unexpected problem. Nothing leaves your device. No input history is saved.",
        ],
        nextSteps: ["Try again, or use a shorter excerpt."],
      },
      context,
    );
    status.textContent = `${sourceLabel} could not be analyzed locally.`;
  }

  function updateInputValidation() {
    const modeInput = MODE_INPUT[currentMode];
    const countResult = boundedCodePointCount(message.value, modeInput.limit);
    const formattedLimit = modeInput.limit.toLocaleString("en-US");
    const lineCount =
      currentMode === "batch" && message.value !== "" && !countResult.overLimit
        ? splitBatchLines(message.value).length
        : 0;
    const tooManyLines = currentMode === "batch" && lineCount > MAX_BATCH_LINES;
    counter.textContent = countResult.overLimit
      ? `Over ${formattedLimit}`
      : currentMode === "batch"
        ? `${lineCount} / ${MAX_BATCH_LINES} lines · ${countResult.count.toLocaleString("en-US")} / ${formattedLimit}`
        : `${countResult.count.toLocaleString("en-US")} / ${formattedLimit}`;
    counter.className =
      countResult.overLimit || tooManyLines ? "counter over-limit" : "counter";
    counter.setAttribute(
      "aria-label",
      countResult.overLimit
        ? `Input is over the ${formattedLimit} character limit`
        : tooManyLines
          ? `Input is over the ${MAX_BATCH_LINES} line limit`
          : currentMode === "batch"
            ? `${lineCount} of ${MAX_BATCH_LINES} lines and ${countResult.count.toLocaleString("en-US")} of ${formattedLimit} characters`
            : `${countResult.count.toLocaleString("en-US")} of ${formattedLimit} characters`,
    );
    message.setAttribute(
      "aria-invalid",
      countResult.overLimit || tooManyLines ? "true" : "false",
    );
    inputError.textContent = countResult.overLimit
      ? `Shorten this ${modeInput.noun} to ${formattedLimit} characters or fewer before analyzing.`
      : tooManyLines
        ? `Use ${MAX_BATCH_LINES} lines or fewer before analyzing.`
        : "";
    inputError.hidden = !countResult.overLimit && !tooManyLines;
    return !countResult.overLimit && !tooManyLines;
  }

  function renderBatchList() {
    const requestedFilter = BATCH_FILTERS.has(batchFilter.value)
      ? batchFilter.value
      : "all";
    if (requestedFilter !== batchFilter.value) batchFilter.value = requestedFilter;
    const visibleRows = completedBatchRows.filter(
      ({ risk }) => requestedFilter === "all" || risk === requestedFilter,
    );
    if (
      activeBatchLineNumber !== undefined &&
      !visibleRows.some(({ lineNumber }) => lineNumber === activeBatchLineNumber)
    ) {
      activeBatchLineNumber = undefined;
      hideResult();
    }
    batchList.replaceChildren();
    for (const row of visibleRows) {
      const item = documentApi.createElement("li");
      const button = documentApi.createElement("button");
      button.type = "button";
      button.textContent = `Line ${row.lineNumber} · ${PRESENTATION[row.risk].heading}`;
      button.setAttribute("data-line-number", String(row.lineNumber));
      button.setAttribute(
        "aria-pressed",
        row.lineNumber === activeBatchLineNumber ? "true" : "false",
      );
      button.addEventListener("click", () => selectBatchItem(row.lineNumber));
      item.append(button);
      batchList.append(item);
    }
    batchEmptyFilter.hidden = visibleRows.length > 0;
  }

  function selectBatchItem(lineNumber) {
    if (!Number.isSafeInteger(lineNumber) || lineNumber < 1) return false;
    const row = completedBatchRows.find((item) => item.lineNumber === lineNumber);
    if (row === undefined) return false;
    activeBatchLineNumber = lineNumber;
    const sourceContext = `Batch ${row.mode === "url" ? "link" : "message"} · line ${lineNumber}`;
    render(row.analysis, "batch", sourceContext);
    activeReport = buildDownloadReport(
      row.analysis,
      "batch",
      lineNumber,
      sourceContext,
    );
    downloadReportButton.disabled = false;
    renderBatchList();
    status.textContent = `Showing findings for batch line ${lineNumber}.`;
    return true;
  }

  function locateBatchLine() {
    if (
      currentMode !== "batch" ||
      activeBatchLineNumber === undefined ||
      typeof message.setSelectionRange !== "function"
    ) {
      return false;
    }
    let start = 0;
    for (let lineNumber = 1; lineNumber < activeBatchLineNumber; lineNumber += 1) {
      const separator = message.value.indexOf("\n", start);
      if (separator === -1) return false;
      start = separator + 1;
    }
    const separator = message.value.indexOf("\n", start);
    let end = separator === -1 ? message.value.length : separator;
    if (end > start && message.value[end - 1] === "\r") end -= 1;
    message.focus();
    message.setSelectionRange(start, end);
    status.textContent = `Located batch line ${activeBatchLineNumber} in the input.`;
    return true;
  }

  function buildBatchReport(rows, mode, counts) {
    return {
      mode,
      total: rows.length,
      counts: { ...counts },
      reports: rows.map(({ lineNumber, analysis }) => ({
        lineNumber,
        report: buildDownloadReport(analysis, "batch").report,
      })),
      limitation: REPORT_LIMITATION,
      privacy: REPORT_PRIVACY,
    };
  }

  async function analyzeBatch() {
    if (currentMode !== "batch") return undefined;
    drafts.batch = message.value;
    const runGeneration = supersede();
    clearBatchPresentation();
    hideResult();
    if (!updateInputValidation()) {
      batchProgress.textContent = "Batch was not analyzed. Check the limits above.";
      batchProgress.hidden = false;
      status.textContent = "Batch was not analyzed. Nothing leaves your device.";
      message.focus();
      return undefined;
    }
    if (message.value === "") {
      batchProgress.textContent = "Add at least one line before analyzing.";
      batchProgress.hidden = false;
      status.textContent = "Empty batch was not analyzed.";
      message.focus();
      return undefined;
    }

    const lines = splitBatchLines(message.value);
    const mode = currentBatchKind;
    const rows = [];
    const counts = { high: 0, review: 0, no_match: 0, cannot_analyze: 0 };
    setBatchBusy(true);
    batchProgress.hidden = false;
    batchProgress.textContent = `Analyzing 0 of ${lines.length}…`;
    status.textContent = "Analyzing the batch locally…";

    try {
      for (let index = 0; index < lines.length; index += 1) {
        await yieldTask();
        if (runGeneration !== generation) return undefined;
        let analysis;
        try {
          analysis = analyze(lines[index], { mode });
        } catch {
          analysis = genericCannotAnalyze(mode);
        }
        const normalizedRisk = Object.hasOwn(PRESENTATION, analysis?.risk)
          ? analysis.risk
          : "cannot_analyze";
        counts[normalizedRisk] += 1;
        rows.push({
          lineNumber: index + 1,
          mode,
          risk: normalizedRisk,
          analysis,
        });
        batchProgress.textContent = `Analyzing ${index + 1} of ${lines.length}…`;
      }
    } catch {
      if (runGeneration !== generation) return undefined;
      setBatchBusy(false);
      clearBatchPresentation();
      hideResult();
      batchProgress.textContent = "Batch analysis stopped before completion.";
      status.textContent = "No partial batch report was kept.";
      return undefined;
    }

    if (runGeneration !== generation) return undefined;
    setBatchBusy(false);
    completedBatchRows = rows;
    activeBatchReport = buildBatchReport(rows, mode, counts);
    batchTotal.textContent = String(rows.length);
    batchHigh.textContent = String(counts.high);
    batchReview.textContent = String(counts.review);
    batchNoMatch.textContent = String(counts.no_match);
    batchCannotAnalyze.textContent = String(counts.cannot_analyze);
    batchResults.hidden = false;
    downloadBatchButton.disabled = false;
    setEmptyState(false);
    renderBatchList();
    batchProgress.textContent = `Analyzed ${rows.length} lines locally.`;
    status.textContent = "Batch analysis complete. No input history is saved.";
    batchResults.focus();
    return activeBatchReport;
  }

  function cancelBatch() {
    if (!batchBusy) return false;
    supersede();
    clearBatchPresentation();
    hideResult();
    batchProgress.hidden = false;
    batchProgress.textContent = "Batch analysis canceled.";
    status.textContent = "No partial batch report was kept.";
    message.focus();
    return true;
  }

  function setBatchKind(kind) {
    if (!SUPPORTED_BATCH_KINDS.has(kind)) return false;
    if (currentBatchKind === kind) return true;
    currentBatchKind = kind;
    batchKind.value = kind;
    supersede();
    clearBatchPresentation();
    hideResult();
    batchProgress.textContent = "";
    batchProgress.hidden = true;
    status.textContent = "";
    return true;
  }

  function useBatchDemo() {
    if (currentMode !== "batch") return false;
    message.value = BATCH_EXAMPLES[currentBatchKind];
    handleInput();
    message.focus();
    return true;
  }

  async function importBatchFile(file = batchFile.files?.[0]) {
    if (currentMode !== "batch") return false;
    batchFile.value = "";
    const importGeneration = supersede();
    clearBatchPresentation();
    hideResult();
    batchProgress.hidden = false;
    status.textContent = "";
    const validName = typeof file?.name === "string" && /\.txt$/iu.test(file.name);
    const mediaType =
      typeof file?.type === "string" ? file.type.split(";", 1)[0].trim() : undefined;
    const validType =
      file?.type === "" || mediaType?.toLowerCase() === "text/plain";
    const validSize =
      Number.isSafeInteger(file?.size) &&
      file.size >= 0 &&
      file.size <= MAX_BATCH_FILE_BYTES;
    if (!validName || !validType || !validSize || typeof file?.arrayBuffer !== "function") {
      batchProgress.textContent = validSize
        ? "Choose a plain-text .txt file. The current draft was kept."
        : "Choose a .txt file no larger than 1 MiB. The current draft was kept.";
      return false;
    }

    batchProgress.textContent = "Reading the text file locally…";
    try {
      const buffer = await file.arrayBuffer();
      if (importGeneration !== generation) return false;
      const importedText = new TextDecoder("utf-8", { fatal: true }).decode(buffer);
      if (importGeneration !== generation) return false;
      if (!isValidBatchContent(importedText)) {
        batchProgress.textContent =
          "The file was empty or exceeded the batch limits. The current draft was kept.";
        return false;
      }
      message.value = importedText;
      drafts.batch = importedText;
      updateInputValidation();
      batchProgress.textContent = "Text imported. Review it, then analyze locally.";
      status.textContent = "The imported text has not been analyzed.";
      message.focus();
      return true;
    } catch {
      if (importGeneration !== generation) return false;
      batchProgress.textContent =
        "The file was not valid UTF-8 text. The current draft was kept.";
      return false;
    }
  }

  function setBatchFilter(filter) {
    if (!BATCH_FILTERS.has(filter)) return false;
    batchFilter.value = filter;
    renderBatchList();
    return true;
  }

  function downloadBatchReport() {
    if (activeBatchReport === undefined) {
      status.textContent = "No completed batch report is available to download.";
      return false;
    }
    try {
      reportSaver(activeBatchReport, BATCH_REPORT_FILENAME);
      status.textContent = "Batch report downloaded.";
      return true;
    } catch {
      status.textContent = "Batch report could not be downloaded.";
      return false;
    }
  }

  function analyzePastedText() {
    if (currentMode === "batch") return analyzeBatch();
    drafts[currentMode] = message.value;
    supersede();
    if (!updateInputValidation()) {
      hideResult();
      status.textContent = "Input was not analyzed. Nothing leaves your device.";
      message.focus();
      return undefined;
    }
    try {
      const analysis = analyze(message.value, { mode: currentMode });
      render(analysis, currentMode);
      activeReport = buildDownloadReport(analysis, currentMode);
      downloadReportButton.disabled = false;
      status.textContent =
        analysis?.risk === "cannot_analyze"
          ? "Input did not produce a result. Nothing leaves your device."
          : `${currentMode === "url" ? "Link" : "Message"} analyzed locally. Nothing leaves your device. No input history is saved.`;
      if (analysis?.risk === "cannot_analyze") message.focus();
      return analysis;
    } catch {
      invalidateActiveReport();
      renderAnalysisFailure(currentMode === "url" ? "Link" : "Message", currentMode);
      return undefined;
    }
  }

  async function analyzeSelection() {
    if (expandedWorkspace) {
      supersede();
      hideResult();
      status.textContent = "Page selection is unavailable in the expanded workspace.";
      return;
    }
    if (currentMode !== "message") {
      supersede();
      render({
        risk: "cannot_analyze",
        reasons: ["Page selection is available only in Message mode."],
        nextSteps: ["Switch to Message mode, or paste a link above."],
      }, "selection");
      status.textContent = "Selected page text was not read in Link mode.";
      return;
    }

    const requestGeneration = supersede();
    hideResult();
    setSelectionBusy(true);
    status.textContent = "Reading only the selected text from this page…";
    let selected;
    try {
      selected = await readSelection(chromeApi);
    } catch {
      selected = { status: "unavailable" };
    }
    if (requestGeneration !== generation) return;
    setSelectionBusy(false);

    if (selected?.status === "ok") {
      try {
        const analysis = analyze(selected.text, { mode: "message" });
        render(analysis, "selection");
        activeReport = buildDownloadReport(analysis, "selection");
        downloadReportButton.disabled = false;
        status.textContent =
          analysis?.risk === "cannot_analyze"
            ? "Selected text did not produce a result. It was not copied into the draft."
            : "Selected text analyzed locally. It was not copied into the draft. No input history is saved.";
      } catch {
        invalidateActiveReport();
        renderAnalysisFailure("Selected text", "selection");
      }
      return;
    }

    const reason =
      SELECTION_FAILURE_REASONS[selected?.status] ??
      SELECTION_FAILURE_REASONS.unavailable;
    render({ risk: "cannot_analyze", reasons: [reason] }, "selection");
    status.textContent = "Selected page text was not analyzed.";
  }

  function handleInput() {
    drafts[currentMode] = message.value;
    supersede();
    clearBatchPresentation();
    hideResult();
    batchProgress.textContent = "";
    batchProgress.hidden = true;
    status.textContent = "";
    updateInputValidation();
  }

  function setMode(mode) {
    if (!SUPPORTED_MODES.has(mode)) return false;
    if (currentMode === mode) return true;
    drafts[currentMode] = message.value;
    currentMode = mode;
    message.value = drafts[mode];
    supersede();
    clearBatchPresentation();
    hideResult();
    batchProgress.textContent = "";
    batchProgress.hidden = true;
    status.textContent = "";
    const messageMode = mode === "message";
    const linkMode = mode === "url";
    const batchMode = mode === "batch";
    messageModeButton.className = `mode-button${messageMode ? " active" : ""}`;
    linkModeButton.className = `mode-button${linkMode ? " active" : ""}`;
    batchModeButton.className = `mode-button${batchMode ? " active" : ""}`;
    messageModeButton.setAttribute("aria-pressed", messageMode ? "true" : "false");
    linkModeButton.setAttribute("aria-pressed", linkMode ? "true" : "false");
    batchModeButton.setAttribute("aria-pressed", batchMode ? "true" : "false");
    messageLabel.textContent = messageMode
      ? "Paste a message"
      : linkMode
        ? "Paste a link"
        : "Paste one item per line";
    message.setAttribute(
      "placeholder",
      messageMode
        ? "Paste a suspicious text, email, or chat message…"
        : linkMode
          ? "Paste a complete web address…"
          : "One message or link per line…",
    );
    inputHint.textContent = MODE_INPUT[mode].hint;
    if (!batchMode) {
      urgentExample.textContent = EXAMPLE_LABELS[mode].urgent;
      accountExample.textContent = EXAMPLE_LABELS[mode].account;
    }
    examples.hidden = batchMode;
    moreExamples.hidden = !messageMode;
    batchOptions.hidden = !batchMode;
    analyzeLabel.textContent = batchMode ? "Analyze batch" : "Analyze locally";
    setSelectionBusy(selectionBusy);
    updateInputValidation();
    return true;
  }

  function useExample(exampleName) {
    if (currentMode === "batch") return false;
    const example = EXAMPLES[currentMode][exampleName];
    if (example === undefined) return false;
    message.value = example;
    handleInput();
    message.focus();
    return true;
  }

  function clearResult() {
    supersede();
    message.value = "";
    drafts[currentMode] = "";
    clearBatchPresentation();
    hideResult();
    batchProgress.textContent = "";
    batchProgress.hidden = true;
    updateInputValidation();
    status.textContent = "Cleared.";
    message.focus();
  }

  function editInput() {
    const returningFromSelection = activeResultContext === "selection";
    const returningFromBatch = activeResultContext === "batch";
    supersede();
    drafts[currentMode] = message.value;
    hideResult();
    updateInputValidation();
    status.textContent = returningFromSelection
      ? "Message input ready. Selected page text was not copied."
      : returningFromBatch
        ? "Batch results ready."
        : "Ready to edit.";
    if (returningFromBatch) batchResults.focus();
    else message.focus();
  }

  function downloadReport() {
    if (activeReport === undefined) {
      status.textContent = "No current report is available to download.";
      return false;
    }
    try {
      reportSaver(activeReport, REPORT_FILENAME);
      status.textContent = "Report downloaded.";
      return true;
    } catch {
      status.textContent = "Report could not be downloaded.";
      return false;
    }
  }

  analyzeButton.addEventListener("click", analyzePastedText);
  selectionButton.addEventListener("click", () => {
    void analyzeSelection();
  });
  clearButton.addEventListener("click", clearResult);
  editInputButton.addEventListener("click", editInput);
  locateBatchLineButton.addEventListener("click", locateBatchLine);
  downloadReportButton.addEventListener("click", downloadReport);
  messageModeButton.addEventListener("click", () => setMode("message"));
  linkModeButton.addEventListener("click", () => setMode("url"));
  batchModeButton.addEventListener("click", () => setMode("batch"));
  batchKind.addEventListener("change", () => setBatchKind(batchKind.value));
  batchFile.addEventListener("change", () => {
    void importBatchFile();
  });
  batchDemoButton.addEventListener("click", useBatchDemo);
  cancelBatchButton.addEventListener("click", cancelBatch);
  batchFilter.addEventListener("change", () => setBatchFilter(batchFilter.value));
  downloadBatchButton.addEventListener("click", downloadBatchReport);
  message.addEventListener("input", handleInput);
  message.addEventListener("keydown", (event) => {
    if (
      event.key === "Enter" &&
      (event.ctrlKey || event.metaKey) &&
      !event.isComposing
    ) {
      event.preventDefault();
      analyzePastedText();
    }
  });
  examples.addEventListener("click", (event) => {
    const exampleName = event.target?.getAttribute?.("data-example");
    if (exampleName !== null && exampleName !== undefined) useExample(exampleName);
  });

  inputHint.textContent = MODE_INPUT[currentMode].hint;
  moreExamples.hidden = false;
  batchOptions.hidden = true;
  batchResults.hidden = true;
  batchProgress.hidden = true;
  batchEmptyFilter.hidden = true;
  analyzeLabel.textContent = "Analyze locally";
  currentBatchKind = SUPPORTED_BATCH_KINDS.has(batchKind.value)
    ? batchKind.value
    : "message";
  batchKind.value = currentBatchKind;
  updateInputValidation();
  setSelectionBusy(false);
  setBatchBusy(false);
  clearBatchPresentation();
  hideResult();
  let pendingProcessed = false;
  function processPendingSelection(reply) {
    if (pendingProcessed || !reply) return;
    if (reply.status === "ok" && typeof reply.text === "string") {
      pendingProcessed = true;
      try {
        const analysis = analyze(reply.text, { mode: "message" });
        render(analysis, "selection");
        activeReport = buildDownloadReport(analysis, "selection");
        downloadReportButton.disabled = false;
        status.textContent =
          analysis?.risk === "cannot_analyze"
            ? "Selected text did not produce a result. It was not copied into the draft."
            : "Selected text analyzed locally. It was not copied into the draft. No input history is saved.";
      } catch {
        invalidateActiveReport();
        renderAnalysisFailure("Selected text", "selection");
      }
    } else if (reply.status === "too_long") {
      pendingProcessed = true;
      render(
        { risk: "cannot_analyze", reasons: [SELECTION_FAILURE_REASONS.too_long] },
        "selection",
      );
      status.textContent = "Selected page text was not analyzed.";
    }
  }

  let pendingSelectionOperation;
  if (chromeApi?.runtime?.sendMessage) {
    try {
      const response = chromeApi.runtime.sendMessage(
        { type: "fisher-pending-selection" },
        (reply) => {
          if (chromeApi.runtime?.lastError) return;
          processPendingSelection(reply);
        },
      );
      if (response && typeof response.then === "function") {
        pendingSelectionOperation = response
          .then((reply) => {
            processPendingSelection(reply);
          })
          .catch(() => {});
      }
    } catch {
      // Ignore error silently
    }
  }

  return {
    analyzePastedText,
    analyzeSelection,
    editInput,
    clearResult,
    handleInput,
    setMode,
    useExample,
    useBatchDemo,
    analyzeBatch,
    cancelBatch,
    setBatchKind,
    importBatchFile,
    setBatchFilter,
    selectBatchItem,
    locateBatchLine,
    downloadReport,
    downloadBatchReport,
    pendingSelectionOperation,
  };
}

if (typeof document !== "undefined") {
  let expandedWorkspace = false;
  try {
    expandedWorkspace =
      new URLSearchParams(globalThis.location?.search ?? "").get("view") ===
      "workspace";
  } catch {
    expandedWorkspace = false;
  }
  if (expandedWorkspace) document.documentElement.dataset.view = "workspace";
  // A toolbar popup sizes itself from its content, so it keeps the fixed width.
  // The same page opened in a tab may shrink with a narrow window instead.
  else if (!globalThis.chrome?.extension?.getViews?.({ type: "popup" })?.includes(globalThis)) {
    document.documentElement.dataset.host = "tab";
  }
  createPopupController({
    documentApi: document,
    chromeApi: globalThis.chrome,
    expandedWorkspace,
  });
}
