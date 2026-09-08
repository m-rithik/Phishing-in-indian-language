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
      this.hidden = false;
      this.listeners = {};
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
  }

  const ids = [
    "message",
    "message-label",
    "input-hint",
    "counter",
    "analyze",
    "selection",
    "clear",
    "mode-message",
    "mode-link",
    "examples",
    "example-urgent",
    "example-account",
    "status",
    "empty-state",
    "result",
    "risk",
    "summary",
    "reasons",
    "checks",
    "checks-group",
    "next-steps",
    "next-steps-group",
    "link-summary",
  ];
  const elements = Object.fromEntries(ids.map((id) => [id, new FakeElement()]));
  elements.result.hidden = true;
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
    engineVersion: "0.4.0",
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

function withSelection(text, callback) {
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
  globalThis.getSelection = () => ({
    rangeCount: 1,
    getRangeAt: () => range,
  });
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
  globalThis.getSelection = () => ({
    rangeCount: 1,
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
  globalThis.getSelection = () => ({
    rangeCount: 1,
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
    assert.equal(calls.length, 1);
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
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    readSelection: async () => ({ status: "ok", text: secret }),
  });
  await controller.analyzeSelection();

  const rendered = [
    elements.message.value,
    elements.status.textContent,
    elements.risk.textContent,
    elements.summary.textContent,
    ...elements.reasons.children.map((item) => item.textContent),
  ].join("\n");
  assert.equal(rendered.includes(secret), false);
  assert.equal(elements.message.value, "");
  assert.equal(elements.result.hidden, false);
  assert.equal(elements.result.focusCount, 1);
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
});

test("structured analysis renders generic checks, next steps, and link counts", () => {
  const { elements, documentApi } = popupFixture();
  const controller = createPopupController({
    documentApi,
    chromeApi: {},
    analyze: () =>
      analysisResult({
        mode: "url",
        linkSummary: { inspected: 1, flagged: 1, limited: false },
      }),
  });
  controller.setMode("url");
  elements.message.value = "https://destination.example";
  controller.analyzePastedText();

  assert.equal(elements.checks.children.length, 1);
  assert.equal(elements["next-steps"].children.length, 1);
  assert.equal(
    elements["link-summary"].textContent,
    "1 recognized link inspected · 1 flagged · candidate scan complete",
  );
  assert.equal(elements["link-summary"].hidden, false);
  assert.equal(elements.result.className, "result risk-review");
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
  }
});
