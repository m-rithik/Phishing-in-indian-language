// Background script with automatic page scanning and notifications

console.log('Fisher: Background script loaded');

// Trigger Point 1: Page load detection
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (!tab.url || isRestrictedUrl(tab.url)) return;

  // TRIGGER POINT 1: Page starts loading
  if (changeInfo.status === 'loading') {
    console.log('Fisher: Page loading -', tab.url);
    chrome.action.setBadgeText({ text: '⏳', tabId });
    chrome.action.setBadgeBackgroundColor({ color: '#2196F3', tabId });
  }

  // TRIGGER POINT 2: Page finished loading
  if (changeInfo.status === 'complete') {
    console.log('Fisher: Page complete -', tab.url);
    extractAndAnalyzePageContent(tabId);
  }
});

// Check if URL is restricted
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
    console.log('Fisher: Extracted', pageText?.length || 0, 'characters');

    if (pageText && pageText.length > 10) {
      analyzePageAndNotify(tabId, pageText);
    } else {
      chrome.action.setBadgeText({ text: '', tabId });
    }
  } catch (error) {
    console.log('Fisher: Extraction failed -', error.message);
    chrome.action.setBadgeText({ text: '', tabId });
  }
}

// TRIGGER POINT 4: Analyze page content
async function analyzePageAndNotify(tabId, text) {
  try {
    const analysis = performQuickAnalysis(text);
    console.log('Fisher: Analysis result -', analysis.risk);
    console.log('Fisher: Analysis details -', analysis);

    if (analysis) {
      updateBadgeAndNotify(tabId, analysis);
    } else {
      console.log('Fisher: No analysis result');
    }
  } catch (error) {
    console.error('Fisher: Analysis error -', error);
  }
}

// Quick analysis with better pattern matching
function performQuickAnalysis(text) {
  if (!text) return { risk: 'no_match', reasons: [] };

  let risk = 'no_match';
  const reasons = [];
  const textLower = text.toLowerCase();

  // Expanded urgency patterns
  const urgencyPatterns = [
    'urgent', 'immediately', 'act now', 'today only', 'suspend', 'suspended',
    'block', 'blocked', 'verify', 'confirm', 'update', 'click here', 'click link',
    'verify account', 'confirm identity', 'verify identity', '24 hour', '24 hours',
    'frozen', 'locked', 'restricted', 'limited', 'confirm now', 'verify now'
  ];

  // Expanded credential patterns
  const credentialPatterns = [
    'otp', 'password', 'pin', 'cvv', 'kyc', 'account number',
    'credit card', 'debit card', 'card number', 'routing number',
    'ssn', 'social security', 'passport', 'drivers license', 'aadhaar'
  ];

  // Phone request patterns
  const phonePatterns = [
    'call now', 'call immediately', 'contact number', 'phone number',
    'reach out', 'call us', 'dial', 'contact us immediately'
  ];

  // Count matches
  let urgencyCount = 0;
  let credentialCount = 0;
  let phoneCount = 0;

  urgencyPatterns.forEach(pattern => {
    const regex = new RegExp('\\b' + pattern + '\\b', 'gi');
    const matches = textLower.match(regex);
    if (matches) urgencyCount += matches.length;
  });

  credentialPatterns.forEach(pattern => {
    const regex = new RegExp('\\b' + pattern + '\\b', 'gi');
    const matches = textLower.match(regex);
    if (matches) credentialCount += matches.length;
  });

  phonePatterns.forEach(pattern => {
    const regex = new RegExp('\\b' + pattern + '\\b', 'gi');
    const matches = textLower.match(regex);
    if (matches) phoneCount += matches.length;
  });

  // Determine risk level
  if (credentialCount > 0 && urgencyCount > 0) {
    risk = 'high';
    reasons.push('Requests credentials with urgency');
  } else if (credentialCount > 2) {
    risk = 'high';
    reasons.push('Multiple credential requests detected');
  } else if (credentialCount > 0 && (urgencyCount > 0 || phoneCount > 0)) {
    risk = 'review';
    reasons.push('Contains credential requests and pressure tactics');
  } else if ((urgencyCount > 2 && text.length < 500) || (credentialCount > 0)) {
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
      title: 'HIGH-RISK PAGE DETECTED',
      priority: 2
    },
    review: {
      emoji: '⚠️',
      text: '!',
      color: '#f57c00',
      title: 'PAGE NEEDS REVIEW',
      priority: 1
    },
    no_match: {
      emoji: '✓',
      text: '✓',
      color: '#388e3c',
      title: 'PAGE APPEARS SAFE',
      priority: 0
    }
  };

  const config = riskConfig[risk] || riskConfig.no_match;

  // Update badge
  chrome.action.setBadgeText({ text: config.text, tabId });
  chrome.action.setBadgeBackgroundColor({ color: config.color, tabId });
  chrome.action.setTitle({
    title: `${config.emoji} ${config.title}`,
    tabId
  });

  // TRIGGER POINT 6: Show notification
  if (risk === 'high' || risk === 'review') {
    showNotificationPopup(tabId, config, analysis);
  }
}

// TRIGGER POINT 6: Display notification popup
function showNotificationPopup(tabId, config, analysis) {
  try {
    const reason = analysis.reasons?.[0] || 'Click the icon for details';

    console.log('Fisher: Injecting banner -', config.title);

    // Inject visible banner into page
    chrome.scripting.executeScript({
      target: { tabId },
      world: 'MAIN',
      func: (title, message, color) => {
        // Create banner element
        const banner = document.createElement('div');
        banner.id = 'fisher-alert-banner';
        banner.style.cssText = `
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          z-index: 999999;
          background: ${color};
          color: white;
          padding: 20px;
          font-size: 18px;
          font-weight: bold;
          text-align: center;
          box-shadow: 0 4px 12px rgba(0,0,0,0.3);
          font-family: Arial, sans-serif;
          line-height: 1.6;
        `;

        banner.innerHTML = `
          <div>🚨 ${title}</div>
          <div style="font-size: 14px; margin-top: 8px; font-weight: normal;">${message}</div>
          <div style="font-size: 12px; margin-top: 8px; opacity: 0.9;">Click the Fisher icon for full analysis</div>
        `;

        document.body.insertBefore(banner, document.body.firstChild);

        // Auto-remove after 8 seconds
        setTimeout(() => {
          if (banner && banner.parentNode) {
            banner.remove();
          }
        }, 8000);
      },
      args: [config.title, reason, config.color || '#d32f2f']
    }).then(() => {
      console.log('Fisher: Banner injected successfully');
    }).catch(err => {
      console.error('Fisher: Banner injection failed -', err.message);
    });
  } catch (error) {
    console.error('Fisher: Notification error -', error);
  }
}

// Clean up
chrome.tabs.onRemoved.addListener((tabId) => {
  console.log('Fisher: Tab closed -', tabId);
});
