export const MAX_SELECTION_CODE_POINTS = 20_000;
export const MAX_VISITED_TEXT_NODES = 10_000;

const RESULT_STATUSES = new Set([
  "empty",
  "too_long",
  "too_complex",
  "unavailable",
]);

function isRecord(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasExactKeys(value, expected) {
  const keys = Object.keys(value).sort();
  return (
    keys.length === expected.length &&
    keys.every((key, index) => key === expected[index])
  );
}

function exceedsCodePointLimit(text, maximum) {
  let count = 0;
  for (const _character of text) {
    count += 1;
    if (count > maximum) return true;
  }
  return false;
}

/*
 * This function is serialized by chrome.scripting.executeScript. Keep it
 * dependency-free: values from this module's outer scope are unavailable in
 * the isolated page world.
 */
export function extractSelectedText(maxCodePoints, maxVisitedTextNodes) {
  if (
    !Number.isInteger(maxCodePoints) ||
    maxCodePoints < 1 ||
    !Number.isInteger(maxVisitedTextNodes) ||
    maxVisitedTextNodes < 1
  ) {
    return { status: "unavailable" };
  }

  try {
    if (typeof globalThis.getSelection !== "function") {
      return { status: "unavailable" };
    }
    const selection = globalThis.getSelection();
    if (
      selection === null ||
      !Number.isInteger(selection.rangeCount) ||
      selection.rangeCount < 0 ||
      typeof selection.getRangeAt !== "function"
    ) {
      return { status: "unavailable" };
    }
    if (selection.rangeCount === 0) return { status: "empty" };
    if (selection.rangeCount !== 1) return { status: "too_complex" };

    const characters = [];
    let codePointCount = 0;
    let visitedTextNodes = 0;

    function appendText(data, start, end) {
      if (
        typeof data !== "string" ||
        !Number.isInteger(start) ||
        !Number.isInteger(end) ||
        start < 0 ||
        end < start ||
        end > data.length
      ) {
        return "unavailable";
      }
      for (let index = start; index < end; index += 1) {
        const first = data.charCodeAt(index);
        let character = data[index];
        if (first >= 0xd800 && first <= 0xdbff && index + 1 < end) {
          const second = data.charCodeAt(index + 1);
          if (second >= 0xdc00 && second <= 0xdfff) {
            character += data[index + 1];
            index += 1;
          }
        }
        codePointCount += 1;
        if (codePointCount > maxCodePoints) return "too_long";
        characters.push(character);
      }
      return "ok";
    }

    for (let rangeIndex = 0; rangeIndex < selection.rangeCount; rangeIndex += 1) {
      const range = selection.getRangeAt(rangeIndex);
      if (
        range === null ||
        typeof range !== "object" ||
        typeof range.collapsed !== "boolean" ||
        typeof range.intersectsNode !== "function" ||
        range.commonAncestorContainer === null ||
        typeof range.commonAncestorContainer !== "object"
      ) {
        return { status: "unavailable" };
      }
      if (range.collapsed) return { status: "empty" };

      const root = range.commonAncestorContainer;
      let nextTextNode;
      if (root.nodeType === 3) {
        let returned = false;
        nextTextNode = () => {
          if (returned) return null;
          returned = true;
          return root;
        };
      } else {
        if (
          typeof globalThis.document !== "object" ||
          globalThis.document === null ||
          typeof globalThis.document.createTreeWalker !== "function"
        ) {
          return { status: "unavailable" };
        }
        const walker = globalThis.document.createTreeWalker(root, 4);
        if (walker === null || typeof walker.nextNode !== "function") {
          return { status: "unavailable" };
        }
        nextTextNode = () => walker.nextNode();
      }

      while (true) {
        const node = nextTextNode();
        if (node === null) break;
        visitedTextNodes += 1;
        if (visitedTextNodes > maxVisitedTextNodes) {
          return { status: "too_complex" };
        }
        if (
          typeof node !== "object" ||
          node === null ||
          node.nodeType !== 3
        ) {
          continue;
        }
        if (!range.intersectsNode(node)) continue;

        const data = node.data;
        if (typeof data !== "string") return { status: "unavailable" };

        const start = node === range.startContainer ? range.startOffset : 0;
        const end = node === range.endContainer ? range.endOffset : data.length;
        const outcome = appendText(data, start, end);
        if (outcome !== "ok") return { status: outcome };
      }
    }

    const text = characters.join("");
    return text.trim() === "" ? { status: "empty" } : { status: "ok", text };
  } catch {
    return { status: "unavailable" };
  }
}

function validateInjectionResult(injections) {
  if (!Array.isArray(injections) || injections.length !== 1) return null;
  const injection = injections[0];
  if (!isRecord(injection)) return null;
  const keys = Object.keys(injection).sort();
  const validKeys =
    keys.join(",") === "frameId,result" ||
    keys.join(",") === "documentId,frameId,result";
  if (
    !validKeys ||
    injection.frameId !== 0 ||
    (Object.hasOwn(injection, "documentId") &&
      (typeof injection.documentId !== "string" || injection.documentId === ""))
  ) {
    return null;
  }

  const result = injection.result;
  if (!isRecord(result) || typeof result.status !== "string") return null;
  if (result.status === "ok") {
    if (
      !hasExactKeys(result, ["status", "text"]) ||
      typeof result.text !== "string" ||
      result.text.trim() === "" ||
      exceedsCodePointLimit(result.text, MAX_SELECTION_CODE_POINTS)
    ) {
      return null;
    }
    return { status: "ok", text: result.text };
  }
  if (!RESULT_STATUSES.has(result.status) || !hasExactKeys(result, ["status"])) {
    return null;
  }
  return { status: result.status };
}

export async function requestSelectedPageText(chromeApi) {
  if (
    !isRecord(chromeApi) ||
    !isRecord(chromeApi.tabs) ||
    typeof chromeApi.tabs.query !== "function" ||
    !isRecord(chromeApi.scripting) ||
    typeof chromeApi.scripting.executeScript !== "function"
  ) {
    return { status: "unavailable" };
  }

  try {
    const tabs = await chromeApi.tabs.query({ active: true, currentWindow: true });
    if (
      !Array.isArray(tabs) ||
      tabs.length !== 1 ||
      !isRecord(tabs[0]) ||
      !Number.isInteger(tabs[0].id) ||
      tabs[0].id < 0
    ) {
      return { status: "unavailable" };
    }

    const injections = await chromeApi.scripting.executeScript({
      target: { tabId: tabs[0].id, frameIds: [0] },
      world: "ISOLATED",
      func: extractSelectedText,
      args: [MAX_SELECTION_CODE_POINTS, MAX_VISITED_TEXT_NODES],
    });
    return validateInjectionResult(injections) ?? { status: "unavailable" };
  } catch {
    return { status: "unavailable" };
  }
}
