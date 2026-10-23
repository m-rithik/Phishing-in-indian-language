// Background script - listens for page loads and auto-analyzes

const cachedResults = new Map();

// Import the analyzer (simplified version for background)
async function importAnalyzer() {
  // We'll communicate with popup for analysis, but can also do basic analysis here
  return null;
}

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

          // Analyze immediately and show notification
          analyzeAndNotify(tabId, response.text);
        }
      }
    );
  }
});

// Analyze text and show notification
async function analyzeAndNotify(tabId, text) {
  try {
    // Import and use the analyzer
    const { analyzeText } = await import('./detector.mjs');
    const analysis = analyzeText(text);

    if (analysis && analysis.risk) {
      // Update badge
      updateBadge(tabId, analysis.risk);

      // Show notification for high-risk pages
      if (analysis.risk === 'high') {
        showNotification(analysis);
      }

      // Cache the analysis
      const cached = cachedResults.get(tabId);
      if (cached) {
        cached.analysis = analysis;
      }
    }
  } catch (error) {
    // Silently fail if analysis doesn't work in background
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
function showNotification(analysis) {
  const riskLevels = {
    high: { emoji: '🚨', title: 'High-Risk Page', color: '#d32f2f' },
    review: { emoji: '⚠️', title: 'Review Needed', color: '#f57c00' },
    no_match: { emoji: '✓', title: 'Safe', color: '#388e3c' },
  };

  const riskConfig = riskLevels[analysis.risk] || riskLevels.no_match;

  // Show Chrome notification
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icon-128.png',
    title: `${riskConfig.emoji} ${riskConfig.title}`,
    message: `This page has ${analysis.risk === 'high' ? 'suspicious patterns' : 'patterns worth reviewing'}. ${analysis.reasons?.[0] || 'Click the Fisher icon to see details.'}`,
    priority: analysis.risk === 'high' ? 2 : 1,
  });
}

// Clean up cache and badge when tab is closed
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
