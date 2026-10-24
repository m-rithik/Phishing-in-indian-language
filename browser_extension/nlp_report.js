// Renders the cached auto-scan result for the tab that opened this report.
// Page title, URL, and analysis fields are inserted as text, never as HTML.

const RISK_BADGES = {
  high: { label: "🚨 HIGH-RISK", className: "high" },
  review: { label: "⚠️ REVIEW", className: "review" },
  no_match: { label: "NO CLEAR MATCH — not a safety result", className: "no-match" },
};
const LANGUAGES = { hindi: "Hindi 🇮🇳", tamil: "Tamil 🇱🇰", telugu: "Telugu", english: "English 🇬🇧" };

function element(tag, { text, className, style } = {}, children = []) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = String(text);
  if (className) node.className = className;
  if (style) node.style.cssText = style;
  node.append(...children);
  return node;
}

function statCard(count, label) {
  return element("div", { className: "stat-card" }, [
    element("div", { className: "number", text: Number(count) || 0 }),
    element("div", { className: "label", text: label }),
  ]);
}

function renderAnalysis(container, tab, analysis) {
  const badge = RISK_BADGES[analysis.risk] || RISK_BADGES.no_match;
  const children = [
    element("h4", { text: tab.title || "Untitled page" }),
    element("p", { style: "font-size: 12px; color: #666; margin: 5px 0 15px 0;" }, [
      "URL: ",
      element("code", { text: tab.url || "" }),
    ]),
    element("div", { style: "margin: 10px 0;" }, [
      "Risk Level: ",
      element("span", { className: `badge ${badge.className}`, text: badge.label }),
    ]),
  ];

  if (analysis.language) {
    const known = Object.hasOwn(LANGUAGES, analysis.language);
    children.push(
      element("div", {}, [
        "Language: ",
        element("span", {
          className: known ? `language-tag ${analysis.language}` : "language-tag",
          text: known ? LANGUAGES[analysis.language] : analysis.language,
        }),
      ]),
    );
  }

  if (Array.isArray(analysis.triggered) && analysis.triggered.length > 0) {
    children.push(
      element("div", { style: "margin-top: 15px;" }, [
        element("strong", { text: "Detected Patterns:" }),
        element("ul", { className: "detected-list" }, analysis.triggered.map((item) => element("li", { text: item }))),
      ]),
    );
  }

  if (analysis.stats) {
    children.push(
      element("div", { className: "stats-box", style: "margin-top: 15px;" }, [
        statCard(analysis.stats.urgencyCount, "Urgency Keywords"),
        statCard(analysis.stats.credentialCount, "Credential Keywords"),
        statCard(analysis.stats.phoneCount, "Phone Keywords"),
      ]),
    );
  }

  container.replaceChildren(element("div", {}, children));
}

function renderMessage(container, message) {
  container.replaceChildren(element("p", { text: message, style: "color: #999;" }));
}

document.getElementById("back-button").addEventListener("click", () => window.close());

const container = document.getElementById("currentAnalysis");
const tabParameter = new URLSearchParams(location.search).get("tabId") ?? "";
const tabId = /^\d{1,15}$/.test(tabParameter) ? Number(tabParameter) : null;

if (tabId === null) {
  renderMessage(container, "Open this report from the Fisher popup on the page you want to review.");
} else {
  chrome.tabs.get(tabId, (tab) => {
    if (chrome.runtime.lastError || !tab) {
      renderMessage(container, "The page this report was opened for is no longer available.");
      return;
    }
    chrome.runtime.sendMessage({ action: "getCurrentAnalysis", tabId }, (response) => {
      if (chrome.runtime.lastError || !response?.analysis) {
        renderMessage(container, "No analysis data available for this page. Reload the page and open the report again.");
        return;
      }
      renderAnalysis(container, tab, response.analysis);
    });
  });
}
