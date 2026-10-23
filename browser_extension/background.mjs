// Background script - listens for page loads and auto-analyzes

const cachedResults = new Map();

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && !tab.url.startsWith('chrome://')) {
    // Page fully loaded - trigger auto-analysis
    chrome.tabs.sendMessage(
      tabId,
      { action: 'extractPageText', maxCodePoints: 20000 },
      (response) => {
        if (response?.success && response?.text) {
          // Cache the result
          cachedResults.set(tabId, {
            text: response.text,
            url: tab.url,
            title: tab.title,
            timestamp: Date.now(),
          });
        }
      }
    );
  }
});

// Clean up cache when tab is closed
chrome.tabs.onRemoved.addListener((tabId) => {
  cachedResults.delete(tabId);
});

// Provide API for popup to get cached analysis
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getCachedPageContent') {
    const tabId = sender.tab?.id;
    if (tabId && cachedResults.has(tabId)) {
      sendResponse({ found: true, data: cachedResults.get(tabId) });
    } else {
      sendResponse({ found: false });
    }
  }
});
