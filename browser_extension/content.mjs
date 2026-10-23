// Content script to extract page text and communicate with popup

export function extractPageText(maxCodePoints = 20000) {
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

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractPageText') {
    const text = extractPageText(request.maxCodePoints || 20000);
    sendResponse({ text, success: text !== null });
  }
});
