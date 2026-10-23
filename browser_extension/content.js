// Content script to extract page text and communicate with popup

function extractPageText(maxCodePoints = 20000) {
  try {
    // Get all visible text from the page
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      null,
      false
    );

    let text = '';
    let nodeCount = 0;
    const maxNodes = 5000;

    let node;
    while ((node = walker.nextNode()) && nodeCount < maxNodes) {
      const nodeText = node.textContent?.trim();
      if (nodeText && nodeText.length > 0) {
        if (text.length + nodeText.length > maxCodePoints) {
          text += nodeText.substring(0, maxCodePoints - text.length);
          break;
        }
        text += (text.length > 0 ? ' ' : '') + nodeText;
      }
      nodeCount++;
    }

    return text.trim();
  } catch (error) {
    return null;
  }
}

// Auto-send page content to background on load
function autoSendContent() {
  try {
    const text = extractPageText(20000);
    if (text && text.length > 0) {
      chrome.runtime.sendMessage(
        { action: 'pageContentExtracted', text, url: window.location.href },
        () => {
          // Ignore errors from background script
          void chrome.runtime.lastError;
        }
      );
    }
  } catch (error) {
    // Silently fail
  }
}

// Send on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', autoSendContent);
} else {
  autoSendContent();
}

// Also send on window load to catch dynamic content
window.addEventListener('load', autoSendContent);

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractPageText') {
    const text = extractPageText(request.maxCodePoints || 20000);
    sendResponse({ text, success: text !== null });
  }
});
