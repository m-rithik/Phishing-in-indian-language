// Background service worker for Fisher
// Registers the selection context menu and holds pending selection text in memory.

let pending = null;

const MAX_SELECTION_CODE_POINTS = 20000;
const PENDING_TTL_MS = 30000;

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "fisher-check-selection",
    title: "Check selection with Fisher",
    contexts: ["selection"],
  });
});

chrome.contextMenus.onClicked.addListener((info) => {
  if (
    info &&
    info.menuItemId === "fisher-check-selection" &&
    typeof info.selectionText === "string" &&
    info.selectionText.length > 0
  ) {
    let count = 0;
    for (const _ of info.selectionText) {
      count += 1;
      if (count > MAX_SELECTION_CODE_POINTS) break;
    }

    if (count > MAX_SELECTION_CODE_POINTS) {
      pending = { status: "too_long", timestamp: Date.now() };
    } else {
      pending = { status: "ok", text: info.selectionText, timestamp: Date.now() };
    }

    try {
      const openResult = chrome.action.openPopup();
      if (openResult && typeof openResult.catch === "function") {
        openResult.catch(() => {
          chrome.tabs.create({
            url: chrome.runtime.getURL("popup.html?view=workspace&from=menu"),
          });
        });
      }
    } catch {
      chrome.tabs.create({
        url: chrome.runtime.getURL("popup.html?view=workspace&from=menu"),
      });
    }
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (sender && sender.id === chrome.runtime.id && message && message.type === "fisher-pending-selection") {
    const now = Date.now();
    if (pending && (now - pending.timestamp) <= PENDING_TTL_MS) {
      const payload =
        pending.status === "ok"
          ? { status: "ok", text: pending.text }
          : { status: "too_long" };
      pending = null;
      sendResponse(payload);
    } else {
      pending = null;
      sendResponse({ status: "empty" });
    }
    return false;
  }
});
