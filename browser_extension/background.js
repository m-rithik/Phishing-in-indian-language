// Background script with automatic page scanning and notifications

// Trigger Point 1: Page load detection
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  // TRIGGER POINT 1: Page starts loading
  if (changeInfo.status === 'loading' && tab.url && !isRestrictedUrl(tab.url)) {
    chrome.action.setBadgeText({ text: '⏳', tabId });
    chrome.action.setBadgeBackgroundColor({ color: '#2196F3', tabId });
  }

  // TRIGGER POINT 2: Page finished loading
  if (changeInfo.status === 'complete' && tab.url && !isRestrictedUrl(tab.url)) {
    // Extract and analyze the page
    extractAndAnalyzePageContent(tabId);
  }
});

// Check if URL is restricted (chrome://, about://, etc)
function isRestrictedUrl(url) {
  return url.startsWith('chrome://') ||
         url.startsWith('about:') ||
         url.startsWith('file://') ||
         url.startsWith('edge://');
}

// TRIGGER POINT 3: Execute script to extract content
async function extractAndAnalyzePageContent(tabId) {
  try {
    const results = await chrome.scripting.executeScript({
      target: { tabId },
      func: () => {
        // Extract all text from the page
        const walker = document.createTreeWalker(
          document.body,
          NodeFilter.SHOW_TEXT,
          null
        );
        let text = '';
        let node;
        let count = 0;
        while ((node = walker.nextNode()) && count < 5000) {
          const nodeText = node.textContent?.trim();
          if (nodeText && nodeText.length > 0) {
            text += (text.length > 0 ? ' ' : '') + nodeText;
            if (text.length > 20000) {
              text = text.substring(0, 20000);
              break;
            }
          }
          count++;
        }
        return text.trim();
      }
    });

    const pageText = results?.[0]?.result;

    if (pageText && pageText.length > 10) {
      // TRIGGER POINT 4: Analysis starts
      analyzePageAndNotify(tabId, pageText);
    } else {
      chrome.action.setBadgeText({ text: '', tabId });
    }
  } catch (error) {
    // Site is restricted or unreachable
    chrome.action.setBadgeText({ text: '', tabId });
  }
}

// TRIGGER POINT 4: Analyze using Fisher rules (delegated to popup)
async function analyzePageAndNotify(tabId, text) {
  try {
    // For background script, we'll use a simple heuristic analysis
    // Full analysis happens in popup when user clicks icon
    const analysis = performQuickAnalysis(text);

    if (analysis && analysis.risk) {
      // TRIGGER POINT 5: Results ready
      updateBadgeAndNotify(tabId, analysis);
    } else {
      chrome.action.setBadgeText({ text: '', tabId });
    }
  } catch (error) {
    chrome.action.setBadgeText({ text: '○', tabId });
  }
}

// Quick analysis in background (rules-based heuristics)
function performQuickAnalysis(text) {
  if (!text) return null;

  let risk = 'no_match';
  const reasons = [];

  // Check for common phishing signals
  const urgencyPatterns = /urgent|immediately|act now|today only|suspend|block|verify|confirm|update|click here/i;
  const credentialPatterns = /otp|password|pin|cvv|kyc|account number|verify.*account|confirm.*identity/i;
  const phonePatterns = /call.*now|contact.*number|phone.*number|reach.*out/i;

  const hasUrgency = urgencyPatterns.test(text);
  const hasCredentialRequest = credentialPatterns.test(text);
  const hasPhoneRequest = phonePatterns.test(text);

  if (hasCredentialRequest && hasUrgency) {
    risk = 'high';
    reasons.push('Requests credentials with urgency');
  } else if (hasCredentialRequest || (hasUrgency && text.length < 500)) {
    risk = 'review';
    reasons.push('Contains suspicious patterns');
  }

  return {
    risk,
    reasons: reasons.length > 0 ? reasons : ['No clear threats detected']
  };
}

// TRIGGER POINT 5: Update badge and show notification
function updateBadgeAndNotify(tabId, analysis) {
  const risk = analysis.risk;
  const riskConfig = {
    high: {
      emoji: '🚨',
      text: '⚠',
      color: '#d32f2f',
      title: 'HIGH-RISK PAGE',
      message: '⚠️ This page shows signs of phishing',
      priority: 2
    },
    review: {
      emoji: '⚠️',
      text: '!',
      color: '#f57c00',
      title: 'REVIEW NEEDED',
      message: '⚠️ This page has suspicious patterns',
      priority: 1
    },
    no_match: {
      emoji: '✓',
      text: '✓',
      color: '#388e3c',
      title: 'SAFE PAGE',
      message: '✓ No phishing signals detected',
      priority: 0
    }
  };

  const config = riskConfig[risk] || riskConfig.no_match;

  // Update badge
  chrome.action.setBadgeText({ text: config.text, tabId });
  chrome.action.setBadgeBackgroundColor({ color: config.color, tabId });
  chrome.action.setTitle({
    title: `${config.emoji} ${config.title}\n${analysis.reasons?.[0] || 'Click for details'}`,
    tabId
  });

  // TRIGGER POINT 6: Show notification popup
  if (risk === 'high' || risk === 'review') {
    showNotificationPopup(config, analysis);
  }
}

// TRIGGER POINT 6: Display notification popup
function showNotificationPopup(config, analysis) {
  try {
    const reason = analysis.reasons?.[0] || 'Suspicious patterns detected';

    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon-128.png',
      title: config.title,
      message: `${reason}\n\nClick the Fisher icon for details.`,
      priority: config.priority,
      silent: false,
      requireInteraction: config.priority > 0
    });
  } catch (error) {
    // Notification not available on some platforms
  }
}

// Clean up when tab closes
chrome.tabs.onRemoved.addListener((tabId) => {
  // Cleanup if needed
});
