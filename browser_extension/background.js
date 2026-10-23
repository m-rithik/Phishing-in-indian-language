// Minimal background script - just handle extension requests
// All analysis happens in the popup

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractPageText') {
    // Just acknowledge
    sendResponse({ status: 'processing' });
  }
});
