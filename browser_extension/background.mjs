// Background script - listens for page loads and auto-analyzes

const cachedResults = new Map();

// Listen for direct messages from content script (faster path)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'pageContentExtracted' && sender?.tab?.id) {
    const tabId = sender.tab.id;
    const text = request.text;

    // Cache the result
    cachedResults.set(tabId, {
      text,
      url: sender.tab.url,
      title: sender.tab.title,
      timestamp: Date.now(),
    });

    // Analyze immediately and show notification
    analyzeAndNotify(tabId, text);
  }

  // Handle getCachedPageContent requests
  if (request.action === 'getCachedPageContent') {
    const tabId = sender.tab?.id;
    if (tabId && cachedResults.has(tabId)) {
      sendResponse({ found: true, data: cachedResults.get(tabId) });
    } else {
      sendResponse({ found: false });
    }
  }
});

// Also listen for tab updates as fallback
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && !tab.url.startsWith('chrome://')) {
    // Only try if we haven't already got content from the script
    if (!cachedResults.has(tabId)) {
      // Page fully loaded - trigger auto-analysis as fallback
      chrome.tabs.sendMessage(
        tabId,
        { action: 'extractPageText', maxCodePoints: 20000 },
        (response) => {
          if (response?.success && response?.text && !cachedResults.has(tabId)) {
            // Cache the result
            cachedResults.set(tabId, {
              text: response.text,
              url: tab.url,
              title: tab.title,
              timestamp: Date.now(),
            });

            // Analyze immediately and show notification
            analyzeAndNotify(tabId, response.text);
          }
        }
      );
    }
  }
});

// Analyze text and show notification
async function analyzeAndNotify(tabId, text) {
  try {
    if (!text || text.length === 0) {
      // No text to analyze - set neutral badge
      chrome.action.setBadgeText({ text: '○', tabId });
      chrome.action.setBadgeBackgroundColor({ color: '#888888', tabId });
      return;
    }

    // Import and use the analyzer
    const { analyzeText } = await import('./detector.mjs');
    const analysis = analyzeText(text);

    if (analysis && analysis.risk) {
      // Update badge
      updateBadge(tabId, analysis.risk);

      // Show notification for high-risk and review pages
      if (analysis.risk === 'high' || analysis.risk === 'review') {
        showNotification(analysis, analysis.risk);
      }

      // Cache the analysis
      const cached = cachedResults.get(tabId);
      if (cached) {
        cached.analysis = analysis;
      }
    } else {
      // Failed to analyze - set neutral badge
      chrome.action.setBadgeText({ text: '○', tabId });
      chrome.action.setBadgeBackgroundColor({ color: '#888888', tabId });
    }
  } catch (error) {
    // Silently fail if analysis doesn't work in background
    chrome.action.setBadgeText({ text: '', tabId });
  }
}

// Update badge with risk level
function updateBadge(tabId, risk) {
  const badgeConfig = {
    high: { text: '⚠', color: '#d32f2f', title: 'High-risk page detected' },
    review: { text: '!', color: '#f57c00', title: 'Review recommended' },
    no_match: { text: '✓', color: '#388e3c', title: 'No clear match' },
  };

  const config = badgeConfig[risk] || badgeConfig.no_match;

  chrome.action.setBadgeText({ text: config.text, tabId });
  chrome.action.setBadgeBackgroundColor({ color: config.color, tabId });
  chrome.action.setTitle({ title: config.title, tabId });
}

// Show notification popup
function showNotification(analysis, risk) {
  const riskLevels = {
    high: { emoji: '🚨', title: 'High-Risk Page Detected', color: '#d32f2f' },
    review: { emoji: '⚠️', title: 'Page Needs Review', color: '#f57c00' },
    no_match: { emoji: '✓', title: 'Page Safe', color: '#388e3c' },
  };

  const riskConfig = riskLevels[risk] || riskLevels.no_match;
  const reason = analysis?.reasons?.[0] || 'Suspicious patterns detected';

  // Show Chrome notification
  try {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon-128.png',
      title: `${riskConfig.emoji} ${riskConfig.title}`,
      message: `${reason}\n\nClick the Fisher icon for full details.`,
      priority: risk === 'high' ? 2 : 1,
      silent: false,
    });
  } catch (error) {
    // Notification API might not be available on all sites
  }
}

// Clean up cache and badge when tab is closed
chrome.tabs.onRemoved.addListener((tabId) => {
  cachedResults.delete(tabId);
});
