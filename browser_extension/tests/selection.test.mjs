import assert from "node:assert/strict";
import test from "node:test";

import {
  MAX_SELECTION_CODE_POINTS,
  MAX_VISITED_TEXT_NODES,
  extractSelectedText,
  requestSelectedPageText,
} from "../selection.mjs";
import { createPopupController } from "../popup.js";

function popupFixture() {
  class FakeElement {
    constructor() {
      this.attributes = {};
      this.children = [];
      this.disabled = false;
      this.focusCount = 0;
      this.files = [];
      this.hidden = false;
      this.listeners = {};
      this.selectionEnd = 0;
      this.selectionStart = 0;
      this.textContent = "";
      this.value = "";
      this.className = "";
    }

    addEventListener(type, listener) {
      this.listeners[type] = listener;
    }

    append(child) {
      this.children.push(child);
    }

    getAttribute(name) {
      return this.attributes[name] ?? null;
    }

    focus() {
      this.focusCount += 1;
    }

    replaceChildren() {
      this.children = [];
    }

    setAttribute(name, value) {
      this.attributes[name] = value;
    }

    setSelectionRange(start, end) {
      this.selectionStart = start;
      this.selectionEnd = end;
    }
  }

  const ids = [
    "message",
    "message-label",
    "input-hint",
    "input-error",
    "counter",
    "analyze",
    "analyze-label",
    "selection",
    "clear",
    "mode-message",
    "mode-link",
    "mode-batch",
    "batch-options",
    "batch-kind",
    "batch-file",
    "batch-demo",
    "cancel-batch",
    "batch-progress",
    "examples",
    "more-examples",
    "example-urgent",
    "example-account",
    "example-hindi",
    "example-tamil",
    "example-telugu",
    "example-benign",
    "status",
    "empty-state",
    "result",
    "result-context",
    "risk",
    "summary",
    "reasons",
    "checks",
    "checks-group",
    "checks-details",
    "result-check-count",
    "result-link-count",
    "next-steps",
    "next-steps-group",
    "link-summary",
    "edit-input",
    "locate-batch-line",
    "download-report",
    "batch-results",
    "batch-total",
    "batch-high",
    "batch-review",
    "batch-no-match",
    "batch-cannot-analyze",
    "batch-filter",
    "batch-list",
    "batch-empty-filter",
    "download-batch",
  ];
  const elements = Object.fromEntries(ids.map((id) => [id, new FakeElement()]));
  elements.result.hidden = true;
  elements["batch-results"].hidden = true;
  elements["batch-kind"].value = "message";
  elements["batch-filter"].value = "all";
  return {
    elements,
    documentApi: {
      querySelector(selector) {
        return elements[selector.slice(1)];
      },
      createElement() {
        return new FakeElement();
      },
      createTextNode(text) {
        const node = new FakeElement();
        node.textContent = text;
        return node;
      },
    },
  };
}

function deferred() {
  let resolve;
  const promise = new Promise((resolvePromise) => {
    resolve = resolvePromise;
  });
  return { promise, resolve };
}

function analysisResult(overrides = {}) {
  return {
    engineVersion: "0.5.0",
    mode: "message",
    risk: "review",
    reasons: ["A synthetic test reason."],
    nextSteps: ["Verify through an official channel."],
    linkSummary: { inspected: 0, flagged: 0, limited: false },
    checks: [
      {
        id: "test_check",
        label: "Synthetic check",
        detail: "The injected checker ran.",
      },
    ],
    ...overrides,
  };
}

function withSelection(text, callback, renderedText = text) {
  const previousGetSelection = globalThis.getSelection;
  const textNode = { nodeType: 3, data: text };
  const range = {
    collapsed: false,
    commonAncestorContainer: textNode,
    startContainer: textNode,
    startOffset: 0,
    endContainer: textNode,
    endOffset: text.length,
    intersectsNode: (node) => node === textNode,
  };
  const selection = {
    rangeCount: 1,
    getRangeAt: () => range,
    toString() {
      return renderedText;
    },
  };
  globalThis.getSelection = () => selection;
  try {
    return callback();
  } finally {
    if (previousGetSelection === undefined) {
      delete globalThis.getSelection;
    } else {
      globalThis.getSelection = previousGetSelection;
    }
  }
}

function withTreeSelection(
  {
    nodes,
    selectedNodes = nodes,
    startContainer = selectedNodes[0],
    startOffset = 0,
    endContainer = selectedNodes[selectedNodes.length - 1],
    endOffset,
    renderedText,
    stringify,
  },
  callback,
) {
  const previousDocument = globalThis.document;
  const previousGetSelection = globalThis.getSelection;
  const root = { nodeType: 1 };
  const selected = new Set(selectedNodes);
  let stringificationCalls = 0;
  let stringificationReceiver;
  const selection = {
    rangeCount: 1,
    getRangeAt: () => ({
      collapsed: false,
      commonAncestorContainer: root,
      startContainer,
      startOffset,
      endContainer,
      endOffset,
      intersectsNode: (node) => selected.has(node),
    }),
    toString() {
      stringificationCalls += 1;
      stringificationReceiver = this;
      return stringify === undefined ? renderedText : stringify();
    },
  };
  globalThis.document = {
    createTreeWalker() {
      let index = 0;
      return { nextNode: () => nodes[index++] ?? null };
    },
  };
  globalThis.getSelection = () => selection;
  try {
    return callback({
      selection,
      stringificationCalls: () => stringificationCalls,
      stringificationReceiver: () => stringificationReceiver,
    });
  } finally {
    if (previousDocument === undefined) delete globalThis.document;
    else globalThis.document = previousDocument;
    if (previousGetSelection === undefined) delete globalThis.getSelection;
    else globalThis.getSelection = previousGetSelection;
  }
}

function fakeChrome({ tabs = [{ id: 7 }], injection, queryError, injectionError } = {}) {
  const calls = [];
  const chromeApi = {
    tabs: {
      async query(query) {
        calls.push(["query", query]);
        if (queryError) {
          throw queryError;
        }
        return tabs;
      },
    },
    scripting: {
      async executeScript(details) {
        calls.push(["executeScript", details]);
        if (injectionError) {
          throw injectionError;
        }
        return injection === undefined ? [
          {
            documentId: "document-1",
            frameId: 0,
            result: { status: "ok", text: "selected text" },
          },
        ] : injection;
      },
    },
  };
  return { chromeApi, calls };
}

test("in-page extraction accepts exactly 20,000 BMP or astral code points", () => {
  withSelection("a".repeat(MAX_SELECTION_CODE_POINTS), () => {
    assert.deepEqual(
      extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
      { status: "ok", text: "a".repeat(MAX_SELECTION_CODE_POINTS) },
    );
  });
  withSelection("😀".repeat(MAX_SELECTION_CODE_POINTS), () => {
    assert.deepEqual(
      extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
      { status: "ok", text: "😀".repeat(MAX_SELECTION_CODE_POINTS) },
    );
  });
});

test("in-page extraction rejects 20,001 code points without returning a prefix", () => {
  for (const text of [
    "a".repeat(MAX_SELECTION_CODE_POINTS + 1),
    "😀".repeat(MAX_SELECTION_CODE_POINTS + 1),
  ]) {
    withSelection(text, () => {
      assert.deepEqual(
        extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
        { status: "too_long" },
      );
    });
  }
});

test("raw and rendered selection limits are enforced independently", () => {
  const oversizedRaw = {
    nodeType: 3,
    data: "😀".repeat(MAX_SELECTION_CODE_POINTS + 1),
  };
  withTreeSelection(
    {
      nodes: [oversizedRaw],
      endOffset: oversizedRaw.data.length,
      renderedText: "short rendered text",
    },
    ({ stringificationCalls }) => {
      assert.deepEqual(
        extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
        { status: "too_long" },
      );
      assert.equal(stringificationCalls(), 0);
    },
  );

  const shortRaw = { nodeType: 3, data: "x" };
  for (const [renderedText, expected] of [
    [
      "😀".repeat(MAX_SELECTION_CODE_POINTS),
      { status: "ok", text: "😀".repeat(MAX_SELECTION_CODE_POINTS) },
    ],
    ["😀".repeat(MAX_SELECTION_CODE_POINTS + 1), { status: "too_long" }],
  ]) {
    withTreeSelection(
      { nodes: [shortRaw], endOffset: 1, renderedText },
      ({ stringificationCalls }) => {
        assert.deepEqual(
          extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
          expected,
        );
        assert.equal(stringificationCalls(), 1);
      },
    );
  }
});

test("rendered selection preserves block separators and inline word joins", () => {
  const send = { nodeType: 3, data: "Send" };
  const otp = { nodeType: 3, data: "OTP immediately at bad.example" };
  withTreeSelection(
    {
      nodes: [send, otp],
      endOffset: otp.data.length,
      renderedText: "Send\nOTP immediately at bad.example",
    },
    ({ selection, stringificationCalls, stringificationReceiver }) => {
      assert.deepEqual(
        extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
        { status: "ok", text: "Send\nOTP immediately at bad.example" },
      );
      assert.equal(stringificationCalls(), 1);
      assert.equal(stringificationReceiver(), selection);
    },
  );

  const pass = { nodeType: 3, data: "pass" };
  const word = { nodeType: 3, data: "word" };
  withTreeSelection(
    { nodes: [pass, word], endOffset: word.data.length, renderedText: "password" },
    () => {
      assert.deepEqual(
        extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
        { status: "ok", text: "password" },
      );
    },
  );
});

test("rendered selection preserves explicit whitespace, punctuation, and partial boundaries", () => {
  const first = { nodeType: 3, data: "XX  Pay" };
  const second = { nodeType: 3, data: " now, please!YY" };
  withTreeSelection(
    {
      nodes: [first, second],
      startContainer: first,
      startOffset: 2,
      endContainer: second,
      endOffset: second.data.length - 2,
      renderedText: "  Pay now, please! \n",
    },
    () => {
      assert.deepEqual(
        extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
        { status: "ok", text: "  Pay now, please! \n" },
      );
    },
  );
});

test("missing, throwing, or non-string selection stringifiers fail generically", () => {
  const node = { nodeType: 3, data: "selected" };
  withTreeSelection(
    { nodes: [node], endOffset: node.data.length, renderedText: "selected" },
    ({ selection }) => {
      selection.toString = null;
      assert.deepEqual(
        extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
        { status: "unavailable" },
      );
    },
  );
  for (const stringify of [
    () => {
      throw new Error("SECRET stringifier detail");
    },
    () => 7,
  ]) {
    withTreeSelection(
      { nodes: [node], endOffset: node.data.length, stringify },
      ({ stringificationCalls }) => {
        const serialized = JSON.stringify(
          extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
        );
        assert.equal(serialized, '{"status":"unavailable"}');
        assert.doesNotMatch(serialized, /SECRET/);
        assert.equal(stringificationCalls(), 1);
      },
    );
  }
});

test("zero-DOM-text form selections return empty without reading form values or stringifying", () => {
  const previousDocument = globalThis.document;
  const previousGetSelection = globalThis.getSelection;
  const input = { nodeType: 1 };
  Object.defineProperty(input, "value", {
    get() {
      throw new Error("SECRET form value was read");
    },
  });
  let stringificationCalls = 0;
  globalThis.document = {
    createTreeWalker: () => ({ nextNode: () => null }),
  };
  globalThis.getSelection = () => ({
    rangeCount: 1,
    getRangeAt: () => ({
      collapsed: false,
      commonAncestorContainer: input,
      startContainer: input,
      startOffset: 0,
      endContainer: input,
      endOffset: 1,
      intersectsNode: () => false,
    }),
    toString() {
      stringificationCalls += 1;
      return "SECRET form value";
    },
  });
  try {
    assert.deepEqual(
      extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
      { status: "empty" },
    );
    assert.equal(stringificationCalls, 0);
  } finally {
    if (previousDocument === undefined) delete globalThis.document;
    else globalThis.document = previousDocument;
    if (previousGetSelection === undefined) delete globalThis.getSelection;
    else globalThis.getSelection = previousGetSelection;
  }
});

test("in-page extraction returns generic empty and complexity sentinels", () => {
  withSelection(" \n\t ", () => {
    assert.deepEqual(
      extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
      { status: "empty" },
    );
  });

  const previousDocument = globalThis.document;
  const previousGetSelection = globalThis.getSelection;
  const nodes = [
    { nodeType: 3, data: "one" },
    { nodeType: 3, data: "two" },
  ];
  const root = { nodeType: 1 };
  globalThis.document = {
    createTreeWalker() {
      let index = 0;
      return { nextNode: () => nodes[index++] ?? null };
    },
  };
  let stringificationCalls = 0;
  globalThis.getSelection = () => ({
    rangeCount: 1,
    toString() {
      stringificationCalls += 1;
      return "one\ntwo";
    },
    getRangeAt: () => ({
      collapsed: false,
      commonAncestorContainer: root,
      startContainer: root,
      startOffset: 0,
      endContainer: root,
      endOffset: 2,
      intersectsNode: () => true,
    }),
  });
  try {
    assert.deepEqual(extractSelectedText(MAX_SELECTION_CODE_POINTS, 1), {
      status: "too_complex",
    });
    assert.equal(stringificationCalls, 0);
  } finally {
    if (previousDocument === undefined) delete globalThis.document;
    else globalThis.document = previousDocument;
    if (previousGetSelection === undefined) delete globalThis.getSelection;
    else globalThis.getSelection = previousGetSelection;
  }
});

test("in-page extraction respects Range boundaries across text nodes", () => {
  const previousDocument = globalThis.document;
  const previousGetSelection = globalThis.getSelection;
  const before = { nodeType: 3, data: "UNSELECTED" };
  const first = { nodeType: 3, data: "alpha" };
  const second = { nodeType: 3, data: "beta" };
  const after = { nodeType: 3, data: "ALSO UNSELECTED" };
  const nodes = [before, first, second, after];
  const root = { nodeType: 1 };
  globalThis.document = {
    createTreeWalker() {
      let index = 0;
      return { nextNode: () => nodes[index++] ?? null };
    },
  };
  globalThis.getSelection = () => ({
    rangeCount: 1,
    toString: () => "lphabe",
    getRangeAt: () => ({
      collapsed: false,
      commonAncestorContainer: root,
      startContainer: first,
      startOffset: 1,
      endContainer: second,
      endOffset: 2,
      intersectsNode: (node) => node === first || node === second,
    }),
  });
  try {
    assert.deepEqual(
      extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
      { status: "ok", text: "lphabe" },
    );
  } finally {
    if (previousDocument === undefined) delete globalThis.document;
    else globalThis.document = previousDocument;
    if (previousGetSelection === undefined) delete globalThis.getSelection;
    else globalThis.getSelection = previousGetSelection;
  }
});

test("in-page extraction never reads data from unselected text nodes", () => {
  const previousDocument = globalThis.document;
  const previousGetSelection = globalThis.getSelection;
  const unselected = { nodeType: 3 };
  Object.defineProperty(unselected, "data", {
    get() {
      throw new Error("SECRET unselected text was accessed");
    },
  });
  let selectedDataReads = 0;
  const selected = { nodeType: 3 };
  Object.defineProperty(selected, "data", {
    get() {
      selectedDataReads += 1;
      return "selected text";
    },
  });
  const root = { nodeType: 1 };
  globalThis.document = {
    createTreeWalker() {
      const nodes = [unselected, selected];
      let index = 0;
      return { nextNode: () => nodes[index++] ?? null };
    },
  };
  globalThis.getSelection = () => ({
    rangeCount: 1,
    toString: () => "selected text",
    getRangeAt: () => ({
      collapsed: false,
      commonAncestorContainer: root,
      startContainer: selected,
      startOffset: 0,
      endContainer: selected,
      endOffset: 13,
      intersectsNode: (node) => node === selected,
    }),
  });
  try {
    assert.deepEqual(
      extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
      { status: "ok", text: "selected text" },
    );
    assert.equal(selectedDataReads, 1);
  } finally {
    if (previousDocument === undefined) delete globalThis.document;
    else globalThis.document = previousDocument;
    if (previousGetSelection === undefined) delete globalThis.getSelection;
    else globalThis.getSelection = previousGetSelection;
  }
});

test("an intersecting malicious data getter fails generically without echo", () => {
  const previousGetSelection = globalThis.getSelection;
  const selected = { nodeType: 3 };
  Object.defineProperty(selected, "data", {
    get() {
      throw new Error("SECRET selected getter detail");
    },
  });
  globalThis.getSelection = () => ({
    rangeCount: 1,
    toString: () => "SECRET selected getter detail",
    getRangeAt: () => ({
      collapsed: false,
      commonAncestorContainer: selected,
      startContainer: selected,
      startOffset: 0,
      endContainer: selected,
      endOffset: 1,
      intersectsNode: () => true,
    }),
  });
  try {
    const serialized = JSON.stringify(
      extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
    );
    assert.equal(serialized, '{"status":"unavailable"}');
    assert.doesNotMatch(serialized, /SECRET/);
  } finally {
    if (previousGetSelection === undefined) delete globalThis.getSelection;
    else globalThis.getSelection = previousGetSelection;
  }
});

test("in-page extraction treats collapsed and multiple ranges as non-results", () => {
  const previousGetSelection = globalThis.getSelection;
  const textNode = { nodeType: 3, data: "not returned" };
  let stringificationCalls = 0;
  globalThis.getSelection = () => ({
    rangeCount: 1,
    toString() {
      stringificationCalls += 1;
      return "not returned";
    },
    getRangeAt: () => ({
      collapsed: true,
      commonAncestorContainer: textNode,
      startContainer: textNode,
      startOffset: 0,
      endContainer: textNode,
      endOffset: 0,
      intersectsNode: () => true,
    }),
  });
  try {
    assert.deepEqual(
      extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
      { status: "empty" },
    );
    assert.equal(stringificationCalls, 0);
    globalThis.getSelection = () => ({ rangeCount: 2, getRangeAt: () => null });
    assert.deepEqual(
      extractSelectedText(MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES),
      { status: "too_complex" },
    );
  } finally {
    if (previousGetSelection === undefined) delete globalThis.getSelection;
    else globalThis.getSelection = previousGetSelection;
  }
});

test("bridge performs the exact active-tab top-frame isolated-world injection", async () => {
  const { chromeApi, calls } = fakeChrome();
  assert.deepEqual(await requestSelectedPageText(chromeApi), {
    status: "ok",
    text: "selected text",
  });
  assert.deepEqual(calls[0], [
    "query",
    { active: true, currentWindow: true },
  ]);
  assert.equal(calls.length, 2);
  assert.equal(calls[1][0], "executeScript");
  assert.deepEqual(calls[1][1], {
    target: { tabId: 7, frameIds: [0] },
    world: "ISOLATED",
    func: extractSelectedText,
    args: [MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES],
  });
});

test("bridge uses generic non-echo failures for unavailable APIs and rejections", async () => {
  for (const chromeApi of [
    undefined,
    {},
    fakeChrome({ queryError: new Error("SECRET query detail") }).chromeApi,
    fakeChrome({ injectionError: new Error("SECRET injection detail") }).chromeApi,
  ]) {
    const serialized = JSON.stringify(await requestSelectedPageText(chromeApi));
    assert.match(serialized, /unavailable/i);
    assert.doesNotMatch(serialized, /SECRET/);
  }
});

test("bridge rejects malformed tabs and injection results", async () => {
  const malformedTabs = [
    null,
    [],
    [{ id: -1 }],
    [{ id: 1.5 }],
    [{ id: 1 }, { id: 2 }],
  ];
  for (const tabs of malformedTabs) {
    const { chromeApi, calls } = fakeChrome({ tabs });
    assert.equal((await requestSelectedPageText(chromeApi)).status, "unavailable");
    // Requires exactly 1 valid tab. Arrays without exactly 1 element trigger fallback (2 calls)
    // Single invalid tabs fail on validation without fallback (1 call)
    const isValidSingleTab = Array.isArray(tabs) && tabs.length === 1;
    const expectedCalls = isValidSingleTab ? 1 : 2;
    assert.equal(calls.length, expectedCalls);
  }

  const malformedInjections = [
    null,
    [],
    [{ frameId: 1, result: { status: "ok", text: "secret" } }],
    [{ frameId: 0 }],
    [{ frameId: 0, result: { status: "ok", text: "secret" }, extra: true }],
    [{ frameId: 0, result: { status: "ok", text: "" } }],
    [{ frameId: 0, result: { status: "ok", text: "a".repeat(20_001) } }],
    [{ frameId: 0, result: { status: "too_long", text: "secret" } }],
    [{ frameId: 0, result: { status: "other" } }],
  ];
  for (const injection of malformedInjections) {
    const { chromeApi } = fakeChrome({ injection });
    const serialized = JSON.stringify(await requestSelectedPageText(chromeApi));
    assert.match(serialized, /unavailable/i);
    assert.doesNotMatch(serialized, /secret/i);
  }
});

test("bridge maps empty, too-long, and too-complex sentinels without source text", async () => {
  for (const status of ["empty", "too_long", "too_complex", "unavailable"]) {
    const { chromeApi } = fakeChrome({
      injection: [{ frameId: 0, result: { status } }],
    });
    const result = await requestSelectedPageText(chromeApi);
    assert.equal(result.status, status);
    assert.equal(Object.hasOwn(result, "text"), false);
  }
});

test("popup initialization performs no page API call and only selection is marked busy", async () => {
  const { elements, documentApi } = popupFixture();
  let requests = 0;
  const pending = deferred();
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    readSelection: () => {
      requests += 1;
      return pending.promise;
    },
  });
  assert.equal(requests, 0);

  const operation = controller.analyzeSelection();
  assert.equal(requests, 1);
  assert.equal(elements.selection.disabled, true);
  assert.equal(elements.selection.attributes["aria-busy"], "true");
  assert.equal(elements.analyze.disabled, false);
  assert.equal(elements.clear.disabled, false);
  pending.resolve({ status: "empty" });
  await operation;
  assert.equal(elements.selection.disabled, false);
});

test("Clear cancels an older selection result and restores the empty focused UI", async () => {
  const { elements, documentApi } = popupFixture();
  const pending = deferred();
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    readSelection: () => pending.promise,
  });
  elements.message.value = "old paste";
  const operation = controller.analyzeSelection();
  controller.clearResult();
  pending.resolve({ status: "ok", text: "SECRET stale selected text" });
  await operation;

  assert.equal(elements.message.value, "");
  assert.equal(elements.result.hidden, true);
  assert.equal(elements.risk.textContent, "");
  assert.equal(elements.reasons.children.length, 0);
  assert.equal(elements.message.focusCount, 1);
  assert.equal(JSON.stringify(elements).includes("SECRET"), false);
});

test("newer pasted analysis wins over an older selection request", async () => {
  const { elements, documentApi } = popupFixture();
  const pending = deferred();
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    readSelection: () => pending.promise,
  });
  const operation = controller.analyzeSelection();
  elements.message.value = "ordinary lunch plans";
  controller.analyzePastedText();
  const heading = elements.risk.textContent;
  pending.resolve({
    status: "ok",
    text: "Bank says send OTP immediately at secret.example",
  });
  await operation;

  assert.equal(elements.risk.textContent, heading);
  assert.match(elements.risk.textContent, /No clear pattern match/);
  assert.match(elements.status.textContent, /Message analyzed locally/);
});

test("a newer selection request wins if an older request finishes last", async () => {
  const { elements, documentApi } = popupFixture();
  const first = deferred();
  const second = deferred();
  let calls = 0;
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    readSelection: () => {
      calls += 1;
      return calls === 1 ? first.promise : second.promise;
    },
  });
  const olderOperation = controller.analyzeSelection();
  const newerOperation = controller.analyzeSelection();
  second.resolve({ status: "ok", text: "ordinary lunch plans" });
  await newerOperation;
  const heading = elements.risk.textContent;
  first.resolve({
    status: "ok",
    text: "Bank says send OTP immediately at stale-secret.example",
  });
  await olderOperation;

  assert.equal(elements.risk.textContent, heading);
  assert.match(elements.risk.textContent, /No clear pattern match/);
});

test("selected source text is analyzed but never copied or rendered", async () => {
  const { elements, documentApi } = popupFixture();
  const secret = "Bank says send OTP immediately at secret.example";
  const existingDraft = "Existing message draft";
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    readSelection: async () => ({ status: "ok", text: secret }),
  });
  elements.message.value = existingDraft;
  elements.message.listeners.input();
  await controller.analyzeSelection();

  const rendered = [
    elements.message.value,
    elements.status.textContent,
    elements.risk.textContent,
    elements.summary.textContent,
    ...elements.reasons.children.map((item) => item.textContent),
  ].join("\n");
  assert.equal(rendered.includes(secret), false);
  assert.equal(elements.message.value, existingDraft);
  assert.equal(elements.result.hidden, false);
  assert.equal(elements.result.focusCount, 1);
  assert.equal(elements["edit-input"].textContent, "Back to input");
  assert.equal(
    elements.status.textContent,
    "Selected text analyzed locally. It was not copied into the draft. No input history is saved.",
  );

  elements["edit-input"].listeners.click();

  assert.equal(elements.result.hidden, true);
  assert.equal(elements.message.value, existingDraft);
  assert.equal(elements.message.focusCount, 1);
  assert.equal(
    elements.status.textContent,
    "Message input ready. Selected page text was not copied.",
  );
  assert.equal(elements["edit-input"].textContent, "Edit input");
});

test("editing invalidates a rendered result and a pending selection without analysis", async () => {
  const { elements, documentApi } = popupFixture();
  const pending = deferred();
  let analyses = 0;
  let selectionReads = 0;
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    analyze: () => {
      analyses += 1;
      return analysisResult();
    },
    readSelection: () => {
      selectionReads += 1;
      return pending.promise;
    },
  });

  elements.message.value = "first";
  controller.analyzePastedText();
  assert.equal(elements.result.hidden, false);
  const selectionOperation = controller.analyzeSelection();
  elements.message.value = "😀a";
  elements.message.listeners.input();
  pending.resolve({ status: "ok", text: "SECRET stale selection" });
  await selectionOperation;

  assert.equal(analyses, 1);
  assert.equal(selectionReads, 1);
  assert.equal(elements.result.hidden, true);
  assert.equal(elements.counter.textContent, "2 / 20,000");
  assert.equal(elements["empty-state"].hidden, false);
  assert.equal(JSON.stringify(elements).includes("SECRET"), false);

  elements.message.value = "a".repeat(100_000);
  elements.message.listeners.input();
  assert.equal(elements.counter.textContent, "Over 20,000");
  assert.equal(elements.message.value.length, 100_000);
  assert.equal(analyses, 1);
});

test("message and link modes restore separate in-memory drafts with mode-specific validation", () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({ documentApi, chromeApi: {} });
  const messageDraft = "m".repeat(3_000);
  const linkDraft = "u".repeat(2_049);

  elements.message.value = messageDraft;
  elements.message.listeners.input();
  assert.equal(elements.counter.textContent, "3,000 / 20,000");
  assert.equal(elements.message.attributes["aria-invalid"], "false");

  controller.setMode("url");
  assert.equal(elements.message.value, "");
  assert.equal(elements.counter.textContent, "0 / 2,048");
  elements.message.value = linkDraft;
  elements.message.listeners.input();
  assert.equal(elements.counter.textContent, "Over 2,048");
  assert.equal(elements.message.attributes["aria-invalid"], "true");

  controller.setMode("message");
  assert.equal(elements.message.value, messageDraft);
  assert.equal(elements.counter.textContent, "3,000 / 20,000");
  assert.equal(elements.message.attributes["aria-invalid"], "false");

  controller.setMode("url");
  assert.equal(elements.message.value, linkDraft);
  assert.equal(elements.counter.textContent, "Over 2,048");
  assert.equal(elements.message.attributes["aria-invalid"], "true");
});

test("result context identifies pasted messages, links, and selected page text", async () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    analyze: (_input, options) => analysisResult({ mode: options.mode }),
    readSelection: async () => ({ status: "ok", text: "selected text" }),
  });

  elements.message.value = "message draft";
  controller.analyzePastedText();
  assert.equal(elements["result-context"].textContent, "Message check");
  assert.equal(elements["edit-input"].textContent, "Edit input");

  controller.setMode("url");
  elements.message.value = "https://example.com";
  controller.analyzePastedText();
  assert.equal(elements["result-context"].textContent, "Link check");
  assert.equal(elements["edit-input"].textContent, "Edit input");

  controller.setMode("message");
  await controller.analyzeSelection();
  assert.equal(elements["result-context"].textContent, "Selected text check");
  assert.equal(elements["edit-input"].textContent, "Back to input");
});

test("Edit input preserves the active draft, hides the result, and returns focus", () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({ documentApi, chromeApi: {} });
  const draft = "Review this message again";
  elements.message.value = draft;
  elements.message.listeners.input();
  controller.analyzePastedText();
  assert.equal(elements.result.hidden, false);

  elements["edit-input"].listeners.click();

  assert.equal(elements.message.value, draft);
  assert.equal(elements.result.hidden, true);
  assert.equal(elements["empty-state"].hidden, false);
  assert.equal(elements.status.textContent, "Ready to edit.");
  assert.equal(elements.message.focusCount, 1);
  assert.equal(elements.counter.textContent, "25 / 20,000");
});

test("link mode counts Unicode code points and blocks input above 2,048", () => {
  const { elements, documentApi } = popupFixture();
  const calls = [];
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    analyze: (input, options) => {
      calls.push([input, options]);
      return analysisResult({ mode: "url" });
    },
  });

  controller.setMode("url");
  assert.equal(elements.counter.textContent, "0 / 2,048");
  assert.match(elements["input-hint"].textContent, /2,048 characters/);

  elements.message.value = "😀".repeat(2_048);
  elements.message.listeners.input();
  assert.equal(elements.counter.textContent, "2,048 / 2,048");
  assert.equal(elements.message.attributes["aria-invalid"], "false");
  assert.equal(elements["input-error"].hidden, true);
  controller.analyzePastedText();
  assert.equal(calls.length, 1);

  elements.message.value = "😀".repeat(2_049);
  elements.message.listeners.input();
  assert.equal(elements.counter.textContent, "Over 2,048");
  assert.equal(
    elements.counter.attributes["aria-label"],
    "Input is over the 2,048 character limit",
  );
  assert.equal(elements.message.attributes["aria-invalid"], "true");
  assert.equal(elements["input-error"].hidden, false);
  assert.match(elements["input-error"].textContent, /link.*2,048/i);
  const renderedError = elements["input-error"].textContent;
  controller.analyzePastedText();
  assert.equal(calls.length, 1);
  assert.equal(elements.message.focusCount, 1);
  assert.equal(elements.result.hidden, true);
  assert.doesNotMatch(renderedError, /😀/u);

  elements.message.value = "https://example.com";
  elements.message.listeners.input();
  assert.equal(elements.message.attributes["aria-invalid"], "false");
  assert.equal(elements["input-error"].hidden, true);
});

test("user-correctable pasted cannot-analyze results return focus to the input", () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    analyze: () => analysisResult({
      risk: "cannot_analyze",
      reasons: ["No analyzable input was provided."],
    }),
  });

  elements.message.value = "malformed input";
  controller.analyzePastedText();

  assert.equal(elements.result.hidden, false);
  assert.equal(elements.result.focusCount, 1);
  assert.equal(elements.message.focusCount, 1);
  assert.match(elements.risk.textContent, /Could not analyze/);
  assert.equal(
    elements.status.textContent,
    "Input did not produce a result. Nothing leaves your device.",
  );
});

test("privacy hints and success statuses describe local in-memory behavior precisely", () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    analyze: (_input, options) => analysisResult({ mode: options.mode }),
  });
  assert.equal(
    elements["input-hint"].textContent,
    "Nothing leaves your device. Draft stays in this window. Up to 20,000 characters. Press Ctrl/⌘ + Enter to analyze.",
  );

  elements.message.value = "ordinary draft";
  controller.analyzePastedText();
  assert.equal(
    elements.status.textContent,
    "Message analyzed locally. Nothing leaves your device. No input history is saved.",
  );

  controller.setMode("url");
  assert.equal(
    elements["input-hint"].textContent,
    "The link is inspected as text only—it is never opened. Nothing leaves your device. Up to 2,048 characters. Press Ctrl/⌘ + Enter to analyze.",
  );
  elements.message.value = "https://example.com";
  controller.analyzePastedText();
  assert.equal(
    elements.status.textContent,
    "Link analyzed locally. Nothing leaves your device. No input history is saved.",
  );
});

test("mode changes invalidate pending work and URL mode never requests page selection", async () => {
  const { elements, documentApi } = popupFixture();
  const pending = deferred();
  const calls = [];
  let selectionReads = 0;
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    analyze: (input, options) => {
      calls.push([input, options]);
      return analysisResult({
        mode: options.mode,
        risk: "no_match",
        reasons: ["No synthetic finding."],
      });
    },
    readSelection: () => {
      selectionReads += 1;
      return pending.promise;
    },
  });

  const selectionOperation = controller.analyzeSelection();
  assert.equal(controller.setMode("url"), true);
  pending.resolve({ status: "ok", text: "SECRET stale selection" });
  await selectionOperation;
  assert.equal(elements.result.hidden, true);
  assert.equal(elements.selection.hidden, true);
  assert.equal(elements.selection.disabled, true);

  await controller.analyzeSelection();
  assert.equal(selectionReads, 1);
  assert.match(elements.status.textContent, /not read in Link mode/);
  elements.message.value = "https://destination.example/path";
  controller.analyzePastedText();
  assert.deepEqual(calls, [
    ["https://destination.example/path", { mode: "url" }],
  ]);
  assert.equal(controller.setMode("unsupported"), false);
});

test("Ctrl or Command plus Enter analyzes once using the active mode", () => {
  for (const modifier of ["ctrlKey", "metaKey"]) {
    const { elements, documentApi } = popupFixture();
    const calls = [];
    createPopupController({
      documentApi,
      chromeApi: {},
      analyze: (input, options) => {
        calls.push([input, options]);
        return analysisResult();
      },
    });
    elements.message.value = "synthetic input";
    let prevented = 0;
    elements.message.listeners.keydown({
      key: "Enter",
      ctrlKey: modifier === "ctrlKey",
      metaKey: modifier === "metaKey",
      preventDefault() {
        prevented += 1;
      },
    });
    assert.equal(prevented, 1);
    assert.deepEqual(calls, [[
      "synthetic input",
      { mode: "message" },
    ]]);
  }
});

test("Ctrl or Command plus Enter does not analyze during IME composition", () => {
  const { elements, documentApi } = popupFixture();
  let analyses = 0;
  createPopupController({
    documentApi,
    chromeApi: {},
    analyze: () => {
      analyses += 1;
      return analysisResult();
    },
  });
  let prevented = 0;
  elements.message.listeners.keydown({
    key: "Enter",
    ctrlKey: true,
    metaKey: false,
    isComposing: true,
    preventDefault() {
      prevented += 1;
    },
  });
  assert.equal(analyses, 0);
  assert.equal(prevented, 0);
});

test("example buttons use documentation-safe content and never auto-analyze", () => {
  const { elements, documentApi } = popupFixture();
  let analyses = 0;
  let selectionReads = 0;
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    analyze: () => {
      analyses += 1;
      return analysisResult();
    },
    readSelection: async () => {
      selectionReads += 1;
      return { status: "empty" };
    },
  });
  const target = documentApi.createElement("button");
  target.setAttribute("data-example", "urgent");
  elements.examples.listeners.click({ target });

  assert.match(elements.message.value, /\.example\b/);
  assert.equal(analyses, 0);
  assert.equal(selectionReads, 0);
  assert.equal(elements.result.hidden, true);
  assert.notEqual(elements.counter.textContent, "0 / 20,000");

  controller.setMode("url");
  assert.equal(elements["example-urgent"].textContent, "IP address");
  assert.equal(elements["example-account"].textContent, "HTTPS address");
  assert.equal(controller.useExample("urgent"), true);
  assert.equal(elements.message.value, "http://192.0.2.1:8080/example");
  assert.equal(controller.useExample("account"), true);
  assert.equal(elements.message.value, "https://example.com");
  assert.equal(analyses, 0);
  assert.equal(selectionReads, 0);

  controller.setMode("message");
  assert.equal(elements["example-urgent"].textContent, "Urgent delivery");
  assert.equal(elements["example-account"].textContent, "Account alert");
  assert.equal(elements["more-examples"].hidden, false);

  for (const [name, scriptPattern] of [
    ["hindi", /[\u0900-\u097f]/u],
    ["tamil", /[\u0b80-\u0bff]/u],
    ["telugu", /[\u0c00-\u0c7f]/u],
  ]) {
    assert.equal(controller.useExample(name), true);
    assert.match(elements.message.value, scriptPattern);
  }
  assert.equal(controller.useExample("benign"), true);
  assert.match(elements.message.value, /team lunch/i);
  assert.equal(analyses, 0);
  assert.equal(selectionReads, 0);

  controller.setMode("url");
  assert.equal(elements["more-examples"].hidden, true);
  assert.equal(controller.useExample("hindi"), false);
});

test("structured analysis uses plain, scoped link summaries for counts and incomplete scans", () => {
  const cases = [
    {
      linkSummary: { inspected: 1, flagged: 1, limited: false },
      expected: "1 web address checked. 1 checked address had structural warning cues.",
    },
    {
      linkSummary: { inspected: 2, flagged: 0, limited: false },
      expected: "2 web addresses checked. No structural warning cues were found in the checked addresses. This does not establish that the checked addresses are safe.",
    },
    {
      linkSummary: { inspected: 3, flagged: 2, limited: true },
      expected: "3 web addresses checked. 2 checked addresses had structural warning cues. Some address candidates could not be checked.",
    },
    {
      linkSummary: { inspected: 0, flagged: 0, limited: true },
      expected: "No web addresses were checked. Some address candidates could not be checked.",
    },
  ];

  for (const { linkSummary, expected } of cases) {
    const { elements, documentApi } = popupFixture();
    const controller = createPopupController({
      documentApi,
      chromeApi: {},
      analyze: () => analysisResult({ mode: "url", linkSummary }),
    });
    controller.setMode("url");
    elements.message.value = "https://destination.example";
    controller.analyzePastedText();

    assert.equal(elements.checks.children.length, 1);
    assert.equal(elements["next-steps"].children.length, 1);
    assert.equal(elements["link-summary"].textContent, expected);
    assert.equal(elements["link-summary"].hidden, false);
    assert.equal(elements.result.className, "result risk-review");
    assert.equal(elements["checks-details"].hidden, false);
    assert.equal(elements["result-check-count"].textContent, "1");
    assert.equal(
      elements["result-link-count"].textContent,
      String(linkSummary.inspected),
    );
  }
});

test("cannot-analyze results show uncomputed counts without percentages", () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    analyze: () =>
      analysisResult({
        risk: "cannot_analyze",
        checks: [],
        linkSummary: { inspected: 0, flagged: 0, limited: false },
      }),
  });
  elements.message.value = "malformed input";
  controller.analyzePastedText();
  assert.equal(elements["result-check-count"].textContent, "—");
  assert.equal(elements["result-link-count"].textContent, "—");
  assert.equal(elements["checks-details"].hidden, true);
  assert.doesNotMatch(
    `${elements["result-check-count"].textContent}${elements["result-link-count"].textContent}`,
    /%/,
  );
});

test("URL no-match results hide the empty checks disclosure", () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({ documentApi, chromeApi: {} });
  controller.setMode("url");
  elements.message.value = "https://example.com";
  controller.analyzePastedText();
  assert.match(elements.risk.textContent, /No clear pattern match/);
  assert.equal(elements.checks.children.length, 0);
  assert.equal(elements["checks-details"].hidden, true);
  assert.equal(elements["result-check-count"].textContent, "0");
});

test("explicit report downloads contain only allowlisted report data and static notices", async () => {
  const { elements, documentApi } = popupFixture();
  const saved = [];
  const filenames = [];
  const selectedSecret = "SECRET selected source text";
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    analyze: (_input, options) =>
      analysisResult({
        mode: options.mode,
        arbitraryExtra: "SECRET arbitrary report field",
        timestamp: "SECRET timestamp",
      }),
    readSelection: async () => ({ status: "ok", text: selectedSecret }),
    saveReport: (report, filename) => {
      saved.push(report);
      filenames.push(filename);
    },
  });

  elements.message.value = "SECRET textarea draft";
  elements.message.listeners.input();
  await controller.analyzeSelection();
  assert.equal(saved.length, 0);
  assert.equal(controller.downloadReport(), true);
  assert.equal(saved.length, 1);
  assert.deepEqual(filenames, ["fisher-analysis-report.json"]);
  assert.deepEqual(Object.keys(saved[0]).sort(), [
    "context",
    "limitation",
    "privacy",
    "report",
  ]);
  assert.deepEqual(Object.keys(saved[0].report), [
    "engineVersion",
    "mode",
    "risk",
    "reasons",
    "nextSteps",
    "linkSummary",
    "checks",
  ]);
  assert.equal(saved[0].context, "Selected text check");
  assert.equal(
    saved[0].privacy,
    "Input stays in this window. Only a report you explicitly save is downloaded.",
  );
  assert.match(saved[0].limitation, /not a safety guarantee/i);
  assert.doesNotMatch(JSON.stringify(saved[0]), /SECRET/);
});

test("editing, clearing, mode changes, and pending selection invalidate report downloads", async () => {
  const invalidators = [
    (controller, elements) => elements.message.listeners.input(),
    (controller) => controller.clearResult(),
    (controller) => controller.setMode("url"),
  ];
  for (const invalidate of invalidators) {
    const { elements, documentApi } = popupFixture();
    let saves = 0;
    const controller = createPopupController({
      documentApi,
      chromeApi: {},
      analyze: () => analysisResult(),
      saveReport: () => {
        saves += 1;
      },
    });
    elements.message.value = "initial draft";
    controller.analyzePastedText();
    assert.equal(elements["download-report"].disabled, false);
    invalidate(controller, elements);
    assert.equal(elements["download-report"].disabled, true);
    assert.equal(controller.downloadReport(), false);
    assert.equal(saves, 0);
  }

  const { elements, documentApi } = popupFixture();
  const pending = deferred();
  let saves = 0;
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    analyze: () => analysisResult(),
    readSelection: () => pending.promise,
    saveReport: () => {
      saves += 1;
    },
  });
  elements.message.value = "initial draft";
  controller.analyzePastedText();
  const operation = controller.analyzeSelection();
  assert.equal(elements["download-report"].disabled, true);
  assert.equal(controller.downloadReport(), false);
  assert.equal(saves, 0);
  pending.resolve({ status: "empty" });
  await operation;
});

test("download failures are generic and do not expose saver errors", () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    analyze: () => analysisResult(),
    saveReport: () => {
      throw new Error("SECRET download implementation detail");
    },
  });
  elements.message.value = "input";
  controller.analyzePastedText();
  assert.equal(controller.downloadReport(), false);
  assert.equal(elements.status.textContent, "Report could not be downloaded.");
  assert.doesNotMatch(elements.status.textContent, /SECRET/);
});

test("expanded workspace disables page selection and never reads the originating page", async () => {
  const { elements, documentApi } = popupFixture();
  let selectionReads = 0;
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    expandedWorkspace: true,
    readSelection: async () => {
      selectionReads += 1;
      return { status: "ok", text: "SECRET selected text" };
    },
  });
  assert.equal(elements.selection.hidden, true);
  assert.equal(elements.selection.disabled, true);
  await controller.analyzeSelection();
  assert.equal(selectionReads, 0);
  assert.equal(elements.result.hidden, true);
  assert.equal(
    elements.status.textContent,
    "Page selection is unavailable in the expanded workspace.",
  );
});

test("unexpected checker exceptions produce generic non-echo results", async () => {
  for (const source of ["paste", "selection"]) {
    const { elements, documentApi } = popupFixture();
    const controller = createPopupController({
      documentApi,
      chromeApi: {},
      analyze: () => {
        throw new Error("SECRET checker detail");
      },
      readSelection: async () => ({
        status: "ok",
        text: "SECRET selected input",
      }),
    });
    if (source === "paste") {
      elements.message.value = "SECRET pasted input";
      controller.analyzePastedText();
    } else {
      await controller.analyzeSelection();
    }
    const rendered = JSON.stringify({
      status: elements.status.textContent,
      risk: elements.risk.textContent,
      summary: elements.summary.textContent,
      reasons: elements.reasons.children.map((item) => item.textContent),
    });
    assert.match(rendered, /unexpected problem/);
    assert.doesNotMatch(rendered, /SECRET/);
    assert.equal(elements.result.hidden, false);
    assert.equal(elements["download-report"].disabled, true);
  }
});

test("batch mode keeps its own draft and exposes only batch controls", () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({ documentApi, chromeApi: {} });
  elements.message.value = "message draft";
  elements.message.listeners.input();

  assert.equal(controller.setMode("batch"), true);
  assert.equal(elements.message.value, "");
  assert.equal(elements.examples.hidden, true);
  assert.equal(elements.selection.hidden, true);
  assert.equal(elements["batch-options"].hidden, false);
  assert.equal(elements["analyze-label"].textContent, "Analyze batch");
  assert.match(elements.counter.textContent, /0 \/ 100 lines/);

  assert.equal(controller.useBatchDemo(), true);
  const batchDraft = elements.message.value;
  assert.equal(batchDraft.split("\n").length, 4);
  assert.equal(elements.result.hidden, true);
  assert.equal(elements["batch-results"].hidden, true);

  controller.setMode("message");
  assert.equal(elements.message.value, "message draft");
  controller.setMode("batch");
  assert.equal(elements.message.value, batchDraft);
});

test("message batch demo produces one result for every filter", async () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    yieldTask: async () => {},
  });
  controller.setMode("batch");
  controller.useBatchDemo();
  const report = await controller.analyzeBatch();
  assert.deepEqual(report.counts, {
    high: 1,
    review: 1,
    no_match: 1,
    cannot_analyze: 1,
  });
  assert.equal(elements["batch-list"].children.length, 4);
});

test("batch splitting supports CRLF, removes one final terminator, and counts blank lines", async () => {
  const { elements, documentApi } = popupFixture();
  const seen = [];
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    yieldTask: async () => {},
    analyze: (input, { mode }) => {
      seen.push([input, mode]);
      if (input === "high") return analysisResult({ mode, risk: "high" });
      if (input === "") return analysisResult({ mode, risk: "cannot_analyze" });
      return analysisResult({ mode, risk: "no_match" });
    },
  });
  controller.setMode("batch");
  elements.message.value = "high\r\n\r\nordinary\r\n";

  const report = await controller.analyzeBatch();

  assert.deepEqual(seen, [
    ["high", "message"],
    ["", "message"],
    ["ordinary", "message"],
  ]);
  assert.equal(report.total, 3);
  assert.deepEqual(report.counts, {
    high: 1,
    review: 0,
    no_match: 1,
    cannot_analyze: 1,
  });
  assert.equal(elements["batch-total"].textContent, "3");
  assert.equal(elements["batch-high"].textContent, "1");
  assert.equal(elements["batch-no-match"].textContent, "1");
  assert.equal(elements["batch-cannot-analyze"].textContent, "1");
  assert.equal(elements["batch-list"].children.length, 3);
  assert.match(
    elements["batch-list"].children[1].children[0].textContent,
    /^Line 2 · Could not analyze$/,
  );
  assert.equal(elements.result.hidden, true);
  assert.equal(elements["batch-results"].hidden, false);
});

test("batch rejects empty, over-100-line, and over-100,000-code-point drafts", async () => {
  const { elements, documentApi } = popupFixture();
  let calls = 0;
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    yieldTask: async () => {},
    analyze: () => {
      calls += 1;
      return analysisResult();
    },
  });
  controller.setMode("batch");

  assert.equal(await controller.analyzeBatch(), undefined);
  assert.match(elements["batch-progress"].textContent, /at least one line/i);

  elements.message.value = Array.from({ length: 101 }, () => "x").join("\n");
  elements.message.listeners.input();
  assert.equal(elements.message.attributes["aria-invalid"], "true");
  assert.match(elements["input-error"].textContent, /100 lines or fewer/i);
  assert.equal(await controller.analyzeBatch(), undefined);

  elements.message.value = "😀".repeat(100_001);
  elements.message.listeners.input();
  assert.equal(elements.counter.textContent, "Over 100,000");
  assert.equal(await controller.analyzeBatch(), undefined);
  assert.equal(calls, 0);
  assert.equal(elements["download-batch"].disabled, true);
});

test("batch delegates per-row message and link limits to the existing analyzer", async () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    yieldTask: async () => {},
  });
  controller.setMode("batch");
  elements.message.value = "a".repeat(20_001);
  await controller.analyzeBatch();
  assert.equal(elements["batch-cannot-analyze"].textContent, "1");

  controller.setBatchKind("message");
  elements.message.value = `${"a".repeat(20_000)}\r\r\n`;
  await controller.analyzeBatch();
  assert.equal(elements["batch-cannot-analyze"].textContent, "1");

  controller.setBatchKind("url");
  elements.message.value = "a".repeat(2_049);
  await controller.analyzeBatch();
  assert.equal(elements["batch-cannot-analyze"].textContent, "1");
});

test("canceling a yielded batch discards every partial row and export", async () => {
  const { elements, documentApi } = popupFixture();
  const secondYield = deferred();
  let yields = 0;
  let calls = 0;
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    yieldTask: () => {
      yields += 1;
      return yields === 1 ? Promise.resolve() : secondYield.promise;
    },
    analyze: () => {
      calls += 1;
      return analysisResult();
    },
  });
  controller.setMode("batch");
  elements.message.value = "one\ntwo\nthree";
  const operation = controller.analyzeBatch();
  await Promise.resolve();
  await Promise.resolve();
  assert.equal(calls, 1);
  assert.equal(elements["cancel-batch"].hidden, false);

  assert.equal(controller.cancelBatch(), true);
  secondYield.resolve();
  assert.equal(await operation, undefined);
  assert.equal(elements["batch-results"].hidden, true);
  assert.equal(elements["batch-list"].children.length, 0);
  assert.equal(elements["download-batch"].disabled, true);
  assert.equal(controller.downloadBatchReport(), false);
  assert.match(elements["batch-progress"].textContent, /canceled/i);
});

test("editing and subtype changes supersede pending batch work", async () => {
  for (const invalidate of [
    (controller, elements) => elements.message.listeners.input(),
    (controller) => controller.setBatchKind("url"),
  ]) {
    const { elements, documentApi } = popupFixture();
    const pendingYield = deferred();
    let calls = 0;
    const controller = createPopupController({
      documentApi,
      chromeApi: {},
      yieldTask: () => pendingYield.promise,
      analyze: () => {
        calls += 1;
        return analysisResult();
      },
    });
    controller.setMode("batch");
    elements.message.value = "pending";
    const operation = controller.analyzeBatch();
    invalidate(controller, elements);
    pendingYield.resolve();
    assert.equal(await operation, undefined);
    assert.equal(calls, 0);
    assert.equal(elements["batch-results"].hidden, true);
  }
});

test("batch file import enforces type and size before reading and preserves the draft", async () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({ documentApi, chromeApi: {} });
  controller.setMode("batch");
  elements.message.value = "draft to preserve";
  elements.message.listeners.input();
  let reads = 0;
  const arrayBuffer = async () => {
    reads += 1;
    return new ArrayBuffer(0);
  };

  assert.equal(
    await controller.importBatchFile({
      name: "batch.csv",
      type: "text/plain",
      size: 10,
      arrayBuffer,
    }),
    false,
  );
  assert.equal(
    await controller.importBatchFile({
      name: "batch.txt",
      type: "application/octet-stream",
      size: 10,
      arrayBuffer,
    }),
    false,
  );
  assert.equal(
    await controller.importBatchFile({
      name: "batch.txt",
      type: "text/plain",
      size: 1_048_577,
      arrayBuffer,
    }),
    false,
  );
  assert.equal(reads, 0);
  assert.equal(elements.message.value, "draft to preserve");
  assert.doesNotMatch(elements["batch-progress"].textContent, /batch\.csv/i);
});

test("batch file import uses fatal UTF-8 decoding, fills only, and ignores stale reads", async () => {
  const { elements, documentApi } = popupFixture();
  let analyses = 0;
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    analyze: () => {
      analyses += 1;
      return analysisResult();
    },
  });
  controller.setMode("batch");
  elements.message.value = "original draft";

  assert.equal(
    await controller.importBatchFile({
      name: "invalid.txt",
      type: "text/plain",
      size: 2,
      arrayBuffer: async () => Uint8Array.from([0xc3, 0x28]).buffer,
    }),
    false,
  );
  assert.equal(elements.message.value, "original draft");
  assert.match(elements["batch-progress"].textContent, /valid UTF-8/i);

  assert.equal(
    await controller.importBatchFile({
      name: "valid.txt",
      type: "",
      size: 7,
      arrayBuffer: async () => new TextEncoder().encode("one\ntwo").buffer,
    }),
    true,
  );
  assert.equal(elements.message.value, "one\ntwo");
  assert.equal(analyses, 0);
  assert.match(elements.status.textContent, /has not been analyzed/i);

  assert.equal(
    await controller.importBatchFile({
      name: "parameterized.txt",
      type: "Text/Plain; Charset=UTF-8",
      size: 5,
      arrayBuffer: async () => new TextEncoder().encode("three").buffer,
    }),
    true,
  );
  assert.equal(elements.message.value, "three");
  assert.equal(analyses, 0);

  const pendingRead = deferred();
  elements["batch-file"].value = "C:\\fakepath\\stale.txt";
  const staleImport = controller.importBatchFile({
    name: "stale.txt",
    type: "text/plain",
    size: 12,
    arrayBuffer: () => pendingRead.promise,
  });
  assert.equal(elements["batch-file"].value, "");
  elements.message.value = "newer edit";
  elements.message.listeners.input();
  pendingRead.resolve(new TextEncoder().encode("SECRET stale").buffer);
  assert.equal(await staleImport, false);
  assert.equal(elements.message.value, "newer edit");
});

test("empty or over-limit imported text is rejected before replacing the draft", async () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({ documentApi, chromeApi: {} });
  controller.setMode("batch");
  elements.message.value = "draft to keep";
  const invalidContents = [
    "",
    Array.from({ length: 101 }, () => "line").join("\n"),
    "a".repeat(100_001),
  ];

  for (const content of invalidContents) {
    const bytes = new TextEncoder().encode(content);
    assert.equal(
      await controller.importBatchFile({
        name: "batch.txt",
        type: "text/plain",
        size: bytes.byteLength,
        arrayBuffer: async () => bytes.buffer,
      }),
      false,
    );
    assert.equal(elements.message.value, "draft to keep");
    assert.match(elements["batch-progress"].textContent, /draft was kept/i);
  }
});

test("edit and clear supersede file reads after the native picker value is reset", async () => {
  for (const invalidate of [
    (_controller, elements) => elements.message.listeners.input(),
    (controller) => controller.clearResult(),
  ]) {
    const { elements, documentApi } = popupFixture();
    const controller = createPopupController({ documentApi, chromeApi: {} });
    controller.setMode("batch");
    elements.message.value = "current draft";
    const pendingRead = deferred();
    elements["batch-file"].value = "C:\\fakepath\\pending.txt";
    const operation = controller.importBatchFile({
      name: "pending.txt",
      type: "text/plain",
      size: 8,
      arrayBuffer: () => pendingRead.promise,
    });
    assert.equal(elements["batch-file"].value, "");
    invalidate(controller, elements);
    pendingRead.resolve(new TextEncoder().encode("outdated").buffer);
    assert.equal(await operation, false);
    assert.doesNotMatch(elements.message.value, /outdated/);
    assert.equal(elements["batch-file"].value, "");
  }
});

test("batch filters keep original line numbers and clear excluded item details", async () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    yieldTask: async () => {},
    analyze: (input, { mode }) =>
      analysisResult({ mode, risk: input === "first secret" ? "high" : "review" }),
  });
  controller.setMode("batch");
  elements.message.value = "first secret\nsecond secret";
  await controller.analyzeBatch();
  assert.equal(controller.selectBatchItem(1), true);
  assert.equal(elements["result-context"].textContent, "Batch message · line 1");
  assert.equal(elements.result.hidden, false);

  assert.equal(controller.setBatchFilter("review"), true);
  assert.equal(elements["batch-list"].children.length, 1);
  assert.match(
    elements["batch-list"].children[0].children[0].textContent,
    /^Line 2 ·/,
  );
  assert.doesNotMatch(
    elements["batch-list"].children[0].children[0].textContent,
    /secret/i,
  );
  assert.equal(elements.result.hidden, true);
  assert.equal(elements["download-report"].disabled, true);

  controller.setBatchFilter("no_match");
  assert.equal(elements["batch-list"].children.length, 0);
  assert.equal(elements["batch-empty-filter"].hidden, false);
});

test("Locate input selects the exact original blank or astral CRLF line", async () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    yieldTask: async () => {},
  });
  assert.equal(elements["locate-batch-line"].hidden, true);
  elements.message.value = "ordinary message";
  controller.analyzePastedText();
  assert.equal(elements["locate-batch-line"].hidden, true);

  controller.setMode("batch");
  elements.message.value = "😀 first\r\n\r\nlast 😀\r\n";
  await controller.analyzeBatch();
  assert.equal(controller.selectBatchItem(2), true);
  assert.equal(elements["locate-batch-line"].hidden, false);
  assert.equal(controller.locateBatchLine(), true);
  assert.equal(elements.message.selectionStart, 10);
  assert.equal(elements.message.selectionEnd, 10);

  assert.equal(controller.selectBatchItem(3), true);
  assert.equal(controller.locateBatchLine(), true);
  assert.equal(elements.message.selectionStart, 12);
  assert.equal(elements.message.selectionEnd, 19);
  assert.equal(elements["batch-results"].hidden, false);
  assert.equal(elements.result.hidden, false);
  assert.equal(elements["download-report"].disabled, false);
  assert.match(elements.status.textContent, /batch line 3/i);
});

test("batch and selected-item exports contain allowlisted reports and line numbers only", async () => {
  const { elements, documentApi } = popupFixture();
  const saved = [];
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    yieldTask: async () => {},
    analyze: (_input, { mode }) =>
      analysisResult({
        mode,
        arbitraryExtra: "SECRET raw analyzer field",
        timestamp: "SECRET timestamp",
      }),
    saveReport: (report, filename) => saved.push({ report, filename }),
  });
  controller.setMode("batch");
  elements.message.value = "SECRET first input\nhttps://SECRET.example/path";
  await controller.analyzeBatch();

  assert.equal(controller.downloadBatchReport(), true);
  assert.equal(saved[0].filename, "fisher-batch-report.json");
  assert.deepEqual(Object.keys(saved[0].report).sort(), [
    "counts",
    "limitation",
    "mode",
    "privacy",
    "reports",
    "total",
  ]);
  assert.deepEqual(
    saved[0].report.reports.map(({ lineNumber }) => lineNumber),
    [1, 2],
  );
  assert.doesNotMatch(JSON.stringify(saved[0].report), /SECRET/);

  controller.selectBatchItem(2);
  assert.equal(controller.downloadReport(), true);
  assert.equal(saved[1].filename, "fisher-analysis-report.json");
  assert.equal(saved[1].report.lineNumber, 2);
  assert.equal(saved[1].report.context, "Batch message · line 2");
  assert.doesNotMatch(JSON.stringify(saved[1].report), /SECRET/);
});
