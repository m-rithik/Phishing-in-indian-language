import { analyzeContent } from "./analyzer.mjs";
import { requestSelectedPageText } from "./selection.mjs";

const MAX_INPUT_CODE_POINTS = 20_000;
const SUPPORTED_MODES = new Set(["message", "url"]);

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

function boundedCodePointCount(value) {
  let count = 0;
  for (const _character of value) {
    count += 1;
    if (count > MAX_INPUT_CODE_POINTS) return { count, overLimit: true };
  }
  return { count, overLimit: false };
}

function safeArray(value) {
  return Array.isArray(value) ? value : [];
}

export function createPopupController({
  documentApi,
  chromeApi,
  analyze = analyzeContent,
  readSelection = requestSelectedPageText,
}) {
  const message = documentApi.querySelector("#message");
  const messageLabel = documentApi.querySelector("#message-label");
  const inputHint = documentApi.querySelector("#input-hint");
  const counter = documentApi.querySelector("#counter");
  const analyzeButton = documentApi.querySelector("#analyze");
  const selectionButton = documentApi.querySelector("#selection");
  const clearButton = documentApi.querySelector("#clear");
  const messageModeButton = documentApi.querySelector("#mode-message");
  const linkModeButton = documentApi.querySelector("#mode-link");
  const examples = documentApi.querySelector("#examples");
  const urgentExample = documentApi.querySelector("#example-urgent");
  const accountExample = documentApi.querySelector("#example-account");
  const status = documentApi.querySelector("#status");
  const emptyState = documentApi.querySelector("#empty-state");
  const result = documentApi.querySelector("#result");
  const risk = documentApi.querySelector("#risk");
  const summary = documentApi.querySelector("#summary");
  const reasons = documentApi.querySelector("#reasons");
  const checks = documentApi.querySelector("#checks");
  const checksGroup = documentApi.querySelector("#checks-group");
  const nextSteps = documentApi.querySelector("#next-steps");
  const nextStepsGroup = documentApi.querySelector("#next-steps-group");
  const linkSummary = documentApi.querySelector("#link-summary");
  let generation = 0;
  let currentMode = "message";
  let selectionBusy = false;

  function setSelectionBusy(busy) {
    selectionBusy = busy;
    const unavailableInMode = currentMode !== "message";
    selectionButton.disabled = busy || unavailableInMode;
    selectionButton.hidden = unavailableInMode;
    selectionButton.setAttribute("aria-busy", busy ? "true" : "false");
  }

  function setEmptyState(visible) {
    emptyState.hidden = !visible;
  }

  function hideResult() {
    result.hidden = true;
    result.className = "result";
    risk.textContent = "";
    summary.textContent = "";
    reasons.replaceChildren();
    checks.replaceChildren();
    nextSteps.replaceChildren();
    linkSummary.textContent = "";
    linkSummary.hidden = true;
    setEmptyState(true);
  }

  function addTextItems(container, values) {
    for (const value of values) {
      if (typeof value !== "string" || value === "") continue;
      const item = documentApi.createElement("li");
      item.textContent = value;
      container.append(item);
    }
  }

  function render(analysis) {
    const normalizedRisk = Object.hasOwn(PRESENTATION, analysis?.risk)
      ? analysis.risk
      : "cannot_analyze";
    const presentation = PRESENTATION[normalizedRisk];
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

    nextSteps.replaceChildren();
    addTextItems(nextSteps, safeArray(analysis?.nextSteps));
    nextStepsGroup.hidden = nextSteps.children.length === 0;

    const inspected = analysis?.linkSummary?.inspected;
    const flagged = analysis?.linkSummary?.flagged;
    const limited = analysis?.linkSummary?.limited;
    if (
      Number.isSafeInteger(inspected) &&
      Number.isSafeInteger(flagged) &&
      typeof limited === "boolean" &&
      (analysis?.mode === "url" || inspected > 0 || flagged > 0 || limited)
    ) {
      linkSummary.textContent = `${inspected} recognized link${inspected === 1 ? "" : "s"} inspected · ${flagged} flagged · ${limited ? "candidate scan limited" : "candidate scan complete"}`;
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
    setSelectionBusy(false);
    return generation;
  }

  function renderAnalysisFailure(sourceLabel) {
    render({
      risk: "cannot_analyze",
      reasons: ["The local checker encountered an unexpected problem. No content was stored."],
      nextSteps: ["Try again, or use a shorter excerpt."],
    });
    status.textContent = `${sourceLabel} could not be analyzed locally.`;
  }

  function analyzePastedText() {
    supersede();
    try {
      const analysis = analyze(message.value, { mode: currentMode });
      render(analysis);
      status.textContent =
        analysis?.risk === "cannot_analyze"
          ? "Input did not produce a result. Nothing was sent or stored."
          : `${currentMode === "url" ? "Link" : "Message"} analyzed locally. Nothing was sent or stored.`;
      return analysis;
    } catch {
      renderAnalysisFailure("Input");
      return undefined;
    }
  }

  async function analyzeSelection() {
    if (currentMode !== "message") {
      supersede();
      render({
        risk: "cannot_analyze",
        reasons: ["Page selection is available only in Message mode."],
        nextSteps: ["Switch to Message mode, or paste a link above."],
      });
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
        render(analysis);
        status.textContent =
          analysis?.risk === "cannot_analyze"
            ? "Selected text did not produce a result. Nothing was stored."
            : "Selected text analyzed locally. Nothing was stored.";
      } catch {
        renderAnalysisFailure("Selected text");
      }
      return;
    }

    const reason =
      SELECTION_FAILURE_REASONS[selected?.status] ??
      SELECTION_FAILURE_REASONS.unavailable;
    render({ risk: "cannot_analyze", reasons: [reason] });
    status.textContent = "Selected page text was not analyzed.";
  }

  function updateCounter() {
    const { count, overLimit } = boundedCodePointCount(message.value);
    counter.textContent = overLimit
      ? "Over 20,000"
      : `${count.toLocaleString("en-US")} / 20,000`;
    counter.className = overLimit ? "counter over-limit" : "counter";
    counter.setAttribute(
      "aria-label",
      overLimit
        ? "Input is over the 20,000 character limit"
        : `${count.toLocaleString("en-US")} of 20,000 characters`,
    );
  }

  function handleInput() {
    supersede();
    hideResult();
    status.textContent = "";
    updateCounter();
  }

  function setMode(mode) {
    if (!SUPPORTED_MODES.has(mode)) return false;
    if (currentMode === mode) return true;
    currentMode = mode;
    supersede();
    hideResult();
    status.textContent = "";
    const messageMode = mode === "message";
    messageModeButton.className = `mode-button${messageMode ? " active" : ""}`;
    linkModeButton.className = `mode-button${messageMode ? "" : " active"}`;
    messageModeButton.setAttribute("aria-pressed", messageMode ? "true" : "false");
    linkModeButton.setAttribute("aria-pressed", messageMode ? "false" : "true");
    messageLabel.textContent = messageMode ? "Paste a message" : "Paste a link";
    message.setAttribute(
      "placeholder",
      messageMode
        ? "Paste a suspicious text, email, or chat message…"
        : "Paste a complete web address…",
    );
    inputHint.textContent = messageMode
      ? "Nothing is sent or saved. Press Ctrl/⌘ + Enter to analyze."
      : "The link is inspected as text only—it is never opened. Press Ctrl/⌘ + Enter to analyze.";
    urgentExample.textContent = EXAMPLE_LABELS[mode].urgent;
    accountExample.textContent = EXAMPLE_LABELS[mode].account;
    setSelectionBusy(selectionBusy);
    updateCounter();
    return true;
  }

  function useExample(exampleName) {
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
    hideResult();
    updateCounter();
    status.textContent = "Cleared.";
    message.focus();
  }

  analyzeButton.addEventListener("click", analyzePastedText);
  selectionButton.addEventListener("click", () => {
    void analyzeSelection();
  });
  clearButton.addEventListener("click", clearResult);
  messageModeButton.addEventListener("click", () => setMode("message"));
  linkModeButton.addEventListener("click", () => setMode("url"));
  message.addEventListener("input", handleInput);
  message.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      analyzePastedText();
    }
  });
  examples.addEventListener("click", (event) => {
    const exampleName = event.target?.getAttribute?.("data-example");
    if (exampleName !== null && exampleName !== undefined) useExample(exampleName);
  });

  updateCounter();
  setSelectionBusy(false);
  hideResult();

  return {
    analyzePastedText,
    analyzeSelection,
    clearResult,
    handleInput,
    setMode,
    useExample,
  };
}

if (typeof document !== "undefined") {
  createPopupController({ documentApi: document, chromeApi: globalThis.chrome });
}
