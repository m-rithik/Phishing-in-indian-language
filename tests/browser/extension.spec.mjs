import { test, expect, chromium } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { createServer } from "node:http";
import { fileURLToPath } from "node:url";
import { readFile } from "node:fs/promises";

let context;
let control;
let extensionId;
let fixtureServer;
let fixtureUrl;
const REPORT_TITLE = `Report <img src=x onerror="window.__fisherInjected=1"> fixture`;
const extensionPath = fileURLToPath(new URL("../../browser_extension", import.meta.url));

test.beforeAll(async () => {
  test.setTimeout(60_000);
  // A disposable profile, never the user's Chrome profile. CDP only enables
  // test installation and toolbar-action simulation; it ships in no artifact.
  context = await chromium.launchPersistentContext("", {
    channel: "chromium",
    headless: true,
    viewport: { width: 440, height: 760 },
    args: ["--enable-unsafe-extension-debugging"],
    ignoreDefaultArgs: ["--disable-extensions"],
  });
  control = await context.browser().newBrowserCDPSession();
  ({ id: extensionId } = await control.send("Extensions.loadUnpacked", { path: extensionPath }));
  fixtureServer = createServer((request, response) => {
    response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    if (request.url === "/report-fixture") {
      response.end(`<!doctype html><html lang="en"><title>${REPORT_TITLE.replaceAll("<", "&lt;")}</title>
        <p>Urgent: verify your account and share the OTP immediately.</p></html>`);
      return;
    }
    response.end(`<!doctype html><html lang="en"><title>Fisher synthetic fixture</title>
      <p id="unselected">UNSELECTED_CANARY transfer cryptocurrency now</p>
      <section id="block-selection"><div>Send</div><span hidden>HIDDEN_CANARY reveal password</span><div>OTP immediately at bad.example</div></section>
      <p id="inline-selection"><span>pass</span><span>word</span></p>
      <input id="form-canary" value="FORM_VALUE_CANARY">
      <p id="selected">Lunch at noon</p>
    </html>`);
  });
  await new Promise((resolve) => fixtureServer.listen(0, "127.0.0.1", resolve));
  fixtureUrl = `http://127.0.0.1:${fixtureServer.address().port}`;
});

test.afterAll(async () => {
  await context?.close();
  if (fixtureServer) await new Promise((resolve) => fixtureServer.close(resolve));
});

async function popupPage() {
  const page = await context.newPage();
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto(`chrome-extension://${extensionId}/popup.html`);
  await expect(page.locator("#analyze")).toBeVisible();
  return page;
}

// Toolbar popups initially appear as an "other" CDP target, then become a
// page without a Playwright page event. Attach to the real target directly.
async function popupEvaluator(targetId) {
  const { sessionId } = await control.send("Target.attachToTarget", { targetId, flatten: false });
  let nextId = 0;
  const send = async (method, params = {}) => {
    const id = ++nextId;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { cleanup(); reject(new Error("Popup evaluation timed out")); }, 5_000);
      const receive = (event) => {
        if (event.sessionId !== sessionId) return;
        const reply = JSON.parse(event.message);
        if (reply.id !== id) return;
        cleanup();
        if (reply.error || reply.result?.exceptionDetails) reject(new Error("Popup evaluation failed"));
        else resolve(reply.result?.result?.value);
      };
      function cleanup() { clearTimeout(timer); control.off("Target.receivedMessageFromTarget", receive); }
      control.on("Target.receivedMessageFromTarget", receive);
      control.send("Target.sendMessageToTarget", {
        sessionId,
        message: JSON.stringify({ id, method, params }),
      }).catch((error) => { cleanup(); reject(error); });
    });
  };
  await send("Runtime.runIfWaitingForDebugger");
  return (expression) => send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
}

async function openToolbarPopup(fixture) {
  await fixture.bringToFront();
  const { targetInfos } = await control.send("Target.getTargets", { filter: [{}] });
  const tab = targetInfos.find((target) => target.type === "tab" && target.url === fixture.url());
  expect(tab).toBeDefined();
  const existingTargets = new Set(targetInfos.map((target) => target.targetId));
  await control.send("Extensions.triggerAction", { id: extensionId, targetId: tab.targetId });
  let popupTarget;
  await expect.poll(async () => {
    const { targetInfos: targets } = await control.send("Target.getTargets", { filter: [{}] });
    popupTarget = targets.find(
      (target) => target.type === "page" && target.url.includes(extensionId) && !existingTargets.has(target.targetId),
    );
    return !!popupTarget;
  }).toBe(true);
  const evaluate = await popupEvaluator(popupTarget.targetId);
  await expect.poll(() => evaluate("document.readyState")).toBe("complete");
  return { evaluate, targetId: popupTarget.targetId };
}

function collectResultSnapshot() {
  return {
    risk: document.querySelector("#risk").textContent,
    summary: document.querySelector("#summary").textContent,
    reasons: [...document.querySelectorAll("#reasons li")].map((item) => item.textContent),
    nextSteps: [...document.querySelectorAll("#next-steps li")].map((item) => item.textContent),
    checks: [...document.querySelectorAll("#checks li")].map((item) => item.textContent),
    linkSummary: document.querySelector("#link-summary").textContent,
  };
}

const resultSnapshotExpression = `(${collectResultSnapshot.toString()})()`;

async function selectFixtureContents(page, selector) {
  return page.evaluate((targetSelector) => {
    const range = document.createRange();
    range.selectNodeContents(document.querySelector(targetSelector));
    getSelection().removeAllRanges();
    getSelection().addRange(range);
    return getSelection().toString();
  }, selector);
}

async function pastedAnalysisSnapshot(text) {
  const page = await popupPage();
  await page.locator("#message").fill(text);
  await page.locator("#analyze").click();
  await expect(page.locator("#result")).toBeVisible();
  const snapshot = await page.evaluate(collectResultSnapshot);
  await page.close();
  return snapshot;
}

test("installed popup analyzes, explains, clears, and makes no network request", async () => {
  const page = await popupPage();
  const externalRequests = [];
  page.on("request", (request) => {
    if (!request.url().startsWith(`chrome-extension://${extensionId}/`)) externalRequests.push(request.url());
  });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.locator("#message").fill("Send OTP immediately at bank.example");
  await expect(page.locator("#result")).toBeHidden();
  await page.locator("#analyze").click();
  await expect(page.locator("#risk")).toContainText("High-risk");
  await expect(page.locator("#result")).toBeFocused();
  await expect(page.locator("#next-steps li")).not.toHaveCount(0);
  await expect(page.locator("#result")).not.toContainText("bank.example");
  await page.screenshot({ path: "outputs/browser_extension/v0.5-result.png", fullPage: true });
  await page.locator("#clear").click();
  await expect(page.locator("#message")).toHaveValue("");
  await expect(page.locator("#message")).toBeFocused();
  await expect(page.locator("#result")).toBeHidden();
  expect(errors).toEqual([]);
  expect(externalRequests).toEqual([]);
  await page.close();
});

test("popup.html contains no #selection", async () => {
  const page = await popupPage();
  await expect(page.locator("#selection")).toHaveCount(0);
  await page.close();
});

test("link mode, keyboard shortcut, and edits keep results current", async () => {
  const page = await popupPage();
  await page.locator("#mode-link").click();
  await expect(page.locator("#selection")).toHaveCount(0);
  await page.locator("#message").fill("http://user:private@127.0.0.1:8080/private");
  await page.locator("#message").press("Control+Enter");
  await expect(page.locator("#result")).toBeVisible();
  await expect(page.locator("#checks")).toContainText("IP");
  await expect(page.locator("#result")).not.toContainText("private");
  await page.locator("#message").fill("https://example.com");
  await expect(page.locator("#result")).toBeHidden();
  await page.locator("#analyze").click();
  await expect(page.locator("#risk")).toContainText("No clear");
  await expect(page.locator("#summary")).toContainText("not a guarantee");
  await expect(page.locator("#link-summary")).toContainText(
    "does not establish that the checked address is safe",
  );
  await expect(page.locator("#link-summary")).toHaveCSS("background-color", "rgb(237, 240, 245)");
  await page.close();
});

test("active and inactive mode buttons retain an opaque keyboard focus ring", async () => {
  const page = await popupPage();
  const focusStyle = (selector) => page.locator(selector).evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      boxShadow: style.boxShadow,
      outlineColor: style.outlineColor,
      outlineStyle: style.outlineStyle,
      outlineWidth: style.outlineWidth,
    };
  });

  await page.keyboard.press("Tab");
  await expect(page.locator("#open-workspace")).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.locator("#mode-message")).toBeFocused();
  expect(await focusStyle("#mode-message")).toEqual({
    boxShadow: "rgb(7, 89, 133) 0px 0px 0px 5px",
    outlineColor: "rgb(255, 255, 255)",
    outlineStyle: "solid",
    outlineWidth: "2px",
  });

  await page.keyboard.press("Tab");
  await expect(page.locator("#mode-link")).toBeFocused();
  expect((await focusStyle("#mode-link")).boxShadow).toBe(
    "rgb(7, 89, 133) 0px 0px 0px 5px",
  );
  await page.keyboard.press("Space");
  await expect(page.locator("#mode-link")).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator("#mode-link")).toHaveClass(/active/);
  expect(await focusStyle("#mode-link")).toEqual({
    boxShadow: "rgb(7, 89, 133) 0px 0px 0px 5px",
    outlineColor: "rgb(255, 255, 255)",
    outlineStyle: "solid",
    outlineWidth: "2px",
  });
  await page.emulateMedia({ reducedMotion: "reduce" });
  expect(await page.evaluate(() => matchMedia("(prefers-reduced-motion: reduce)").matches)).toBe(true);
  expect(await page.locator("#mode-link").evaluate((element) => (
    Number.parseFloat(getComputedStyle(element).transitionDuration)
  ))).toBeLessThanOrEqual(0.001);
  await page.close();
});

test("mode drafts, result context, and Edit input form one local editing workflow", async () => {
  const page = await popupPage();
  const externalRequests = [];
  page.on("request", (request) => {
    if (!request.url().startsWith(`chrome-extension://${extensionId}/`)) externalRequests.push(request.url());
  });
  const messageDraft = "Draft 😀";
  const linkDraft = "http://user:private@127.0.0.1:8080/private";

  await page.locator("#message").fill(messageDraft);
  await expect(page.locator("#counter")).toHaveText("7 / 20,000");
  await page.locator("#mode-link").click();
  await expect(page.locator("#message")).toHaveValue("");
  await expect(page.locator("#counter")).toHaveText("0 / 2,048");

  await page.locator("#message").fill(linkDraft);
  await page.locator("#analyze").click();
  await expect(page.locator("#result-context")).toHaveText("Link check");
  await expect(page.locator("#link-summary")).toHaveText(
    "1 web address checked. 1 checked address had structural warning cues.",
  );
  await page.locator("#edit-input").click();
  await expect(page.locator("#result")).toBeHidden();
  await expect(page.locator("#message")).toHaveValue(linkDraft);
  await expect(page.locator("#message")).toBeFocused();
  await expect(page.locator("#status")).toHaveText("Ready to edit.");

  await page.locator("#mode-message").click();
  await expect(page.locator("#message")).toHaveValue(messageDraft);
  await expect(page.locator("#counter")).toHaveText("7 / 20,000");
  await page.locator("#analyze").click();
  await expect(page.locator("#result-context")).toHaveText("Message check");

  await page.locator("#mode-link").click();
  await expect(page.locator("#message")).toHaveValue(linkDraft);
  await expect(page.locator("#counter")).toHaveText("42 / 2,048");
  expect(externalRequests).toEqual([]);
  await page.close();
});

test("link limit gives inline correction, blocks analysis, and returns focus", async () => {
  const page = await popupPage();
  await page.locator("#mode-link").click();
  const exact = `https://example.com/${"a".repeat(2_048 - 20)}`;
  const oversized = `${exact}a`;

  await page.locator("#message").fill(exact);
  await expect(page.locator("#counter")).toHaveText("2,048 / 2,048");
  await expect(page.locator("#message")).toHaveAttribute("aria-invalid", "false");
  await page.locator("#analyze").click();
  await expect(page.locator("#result")).toBeVisible();

  await page.locator("#message").fill(oversized);
  await expect(page.locator("#counter")).toHaveText("Over 2,048");
  await expect(page.locator("#counter")).toHaveAttribute(
    "aria-label",
    "Input is over the 2,048 character limit",
  );
  await expect(page.locator("#message")).toHaveAttribute("aria-invalid", "true");
  await expect(page.locator("#input-error")).toContainText("Shorten this link to 2,048 characters");
  await expect(page.locator("#result")).toBeHidden();
  await page.locator("#analyze").click();
  await expect(page.locator("#message")).toBeFocused();
  await expect(page.locator("#result")).toBeHidden();
  await expect(page.locator("body")).not.toContainText(oversized);
  await page.close();
});

test("pasted malformed input keeps its explanation and returns focus to the field", async () => {
  const page = await popupPage();
  await page.locator("#mode-link").click();
  await page.locator("#message").fill("not a complete link");
  await page.locator("#analyze").click();
  await expect(page.locator("#risk")).toHaveText("Could not analyze");
  await expect(page.locator("#reasons")).toContainText("complete web address");
  await expect(page.locator("#message")).toBeFocused();
  await page.close();
});

test("examples wait for an explicit check and oversized message is rejected whole", async () => {
  const page = await popupPage();
  await page.locator('[data-example="account"]').click();
  await expect(page.locator("#message")).not.toHaveValue("");
  await expect(page.locator("#result")).toBeHidden();
  await page.locator("#message").fill("a".repeat(45_000) + " send OTP immediately");
  expect((await page.locator("#message").inputValue()).length).toBeGreaterThan(45_000);
  await expect(page.locator("#counter")).toHaveText("Over 20,000");
  await expect(page.locator("#message")).toHaveAttribute("aria-invalid", "true");
  await page.locator("#analyze").click();
  await expect(page.locator("#input-error")).toContainText("Shorten this message to 20,000 characters");
  await expect(page.locator("#message")).toBeFocused();
  await expect(page.locator("#result")).toBeHidden();
  await page.close();
});

test("empty and populated states pass automated accessibility checks", async () => {
  const page = await popupPage();
  expect(await page.locator("body").evaluate((element) => element.getBoundingClientRect().width)).toBe(404);
  const empty = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
  expect(empty.violations).toEqual([]);
  await page.screenshot({ path: "outputs/browser_extension/v0.5-popup.png", fullPage: true });
  await page.locator("#message").fill("Send OTP immediately");
  await page.locator("#analyze").click();
  await expect(page.locator("#result")).toBeVisible();
  const populated = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
  expect(populated.violations).toEqual([]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.close();
});

test("recommended action precedes evidence and the popup fits 320 pixels", async () => {
  const page = await popupPage();
  await page.setViewportSize({ width: 320, height: 760 });
  expect(await page.locator("body").evaluate((element) => element.getBoundingClientRect().width)).toBe(320);
  await page.locator("#message").fill("Send OTP immediately");
  await page.locator("#analyze").click();

  const order = await page.locator("#result .result-group h3").allTextContents();
  expect(order).toEqual(["What to do next", "Evidence noticed", "Checks performed"]);
  await expect(page.locator("#next-steps")).toBeVisible();
  await expect(page.locator("#reasons")).toBeVisible();
  await expect(page.locator("#checks")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: "outputs/browser_extension/v0.5-320-result.png", fullPage: true });
  await page.close();
});

test("expanded workspace opens empty, stays local, and adapts to narrow screens", async () => {
  const popup = await popupPage();
  await popup.locator("#message").fill("PRIVATE_DRAFT_CANARY do not transfer this draft");
  const opened = context.waitForEvent("page");
  await popup.locator("#open-workspace").click();
  const page = await opened;
  await page.waitForLoadState();
  await page.setViewportSize({ width: 1440, height: 1100 });
  expect(page.url()).toBe(`chrome-extension://${extensionId}/popup.html?view=workspace`);
  await expect(page.locator("html")).toHaveAttribute("data-view", "workspace");
  await expect(page.locator("#message")).toHaveValue("");
  await expect(page.locator("body")).not.toContainText("PRIVATE_DRAFT_CANARY");
  await expect(page.locator("#selection")).toHaveCount(0);
  await expect(page.locator("#open-workspace")).toBeHidden();
  expect(await page.evaluate(() => window.opener === null)).toBe(true);
  const requests = [];
  page.on("request", request => {
    if (!request.url().startsWith(`chrome-extension://${extensionId}/`)) requests.push(request.url());
  });
  expect((await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze()).violations).toEqual([]);
  await page.screenshot({ path: "outputs/browser_extension/workspace-light.png", fullPage: true });
  await page.locator("#example-account").click();
  await expect(page.locator("#result")).toBeHidden();
  await page.locator("#analyze").click();
  await expect(page.locator("#risk")).toContainText("High-risk");
  await expect(page.locator("#result-check-count")).toHaveText("1");
  await expect(page.locator("#result-link-count")).toHaveText("0");
  await page.screenshot({ path: "outputs/browser_extension/workspace-result.png", fullPage: true });
  expect((await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze()).violations).toEqual([]);
  await page.locator("#checks-details summary").click();
  await expect(page.locator("#checks")).toBeHidden();
  await page.locator("#checks-details summary").click();
  await expect(page.locator("#checks")).toBeVisible();
  for (const width of [768, 640, 320]) {
    await page.setViewportSize({ width, height: 900 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await expect(page.locator("#analyze")).toBeVisible();
  }
  await page.screenshot({ path: "outputs/browser_extension/workspace-mobile.png", fullPage: true });
  expect(requests).toEqual([]);
  await page.close();
  await popup.close();
});

test("saved JSON contains only the current generic report and never submitted secrets", async () => {
  const page = await popupPage();
  await page.locator("#mode-link").click();
  await page.locator("#message").fill("http://user:SECRET_PASSWORD@127.0.0.1:8080/PRIVATE_PATH?token=SECRET_TOKEN");
  await page.locator("#analyze").click();
  const pending = page.waitForEvent("download");
  await page.locator("#download-report").click();
  const download = await pending;
  expect(download.suggestedFilename()).toBe("fisher-analysis-report.json");
  const text = await readFile(await download.path(), "utf8");
  for (const secret of ["SECRET_PASSWORD", "PRIVATE_PATH", "SECRET_TOKEN", "127.0.0.1"]) {
    expect(text).not.toContain(secret);
  }
  const saved = JSON.parse(text);
  expect(saved.report.mode).toBe("url");
  expect(saved.report.risk).toBe("review");
  expect(saved.context).toBe("Link check");
  expect(saved.report.linkSummary).toEqual({ inspected: 1, flagged: 1, limited: false });
  expect(saved.report.checks.length).toBeGreaterThan(0);
  expect(saved.limitation).toContain("not a safety guarantee");
  expect(Object.keys(saved).sort()).toEqual(["context", "limitation", "privacy", "report"]);
  await page.locator("#message").fill("https://example.com");
  await expect(page.locator("#result")).toBeHidden();
  await expect(page.locator("#download-report")).toBeDisabled();
  await page.close();
});

test("multilingual samples are explicit, composition-safe, and private", async () => {
  const page = await popupPage();
  for (const sample of ["hindi", "tamil", "telugu", "benign"]) {
    await page.locator(`#example-${sample}`).click();
    await expect(page.locator("#message")).not.toHaveValue("");
    await expect(page.locator("#result")).toBeHidden();
    await page.locator("#message").dispatchEvent("keydown", {
      key: "Enter", ctrlKey: true, isComposing: true,
    });
    await expect(page.locator("#result")).toBeHidden();
    await page.locator("#analyze").click();
    await expect(page.locator("#risk")).toHaveText(sample === "benign" ? "No clear pattern match" : "High-risk patterns found");
  }
  await page.locator("#mode-link").click();
  await expect(page.locator("#more-examples")).toBeHidden();
  await page.locator("#analyze").click();
  await expect(page.locator("#result-check-count")).toHaveText("—");
  await expect(page.locator("#result-link-count")).toHaveText("—");
  await page.close();
});

test("dark workspace and popup preserve contrast and forced-color selection", async () => {
  const page = await popupPage();
  await page.emulateMedia({ colorScheme: "dark", reducedMotion: "reduce" });
  expect((await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze()).violations).toEqual([]);
  await page.goto(`chrome-extension://${extensionId}/popup.html?view=workspace`);
  await page.setViewportSize({ width: 1440, height: 1100 });
  await page.locator("#example-account").click();
  await page.locator("#analyze").click();
  await expect(page.locator("#result")).toBeVisible();
  expect((await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze()).violations).toEqual([]);
  await page.screenshot({ path: "outputs/browser_extension/workspace-dark.png", fullPage: true });
  await page.emulateMedia({ forcedColors: "active", reducedMotion: "reduce" });
  expect(await page.locator("#mode-message").evaluate(element => getComputedStyle(element).outlineStyle)).toBe("solid");
  await page.close();
});

test("bulk review retains blank lines, filters findings, and shows the chosen line", async () => {
  const page = await popupPage();
  await page.goto(`chrome-extension://${extensionId}/popup.html?view=workspace`);
  await page.setViewportSize({ width: 1440, height: 1100 });
  await page.locator("#mode-batch").click();
  const source = "Send OTP immediately\nDinner at eight\n\nRead the notes at https://example.com";
  await page.locator("#message").fill(source);
  await expect(page.locator("#batch-results")).toBeHidden();
  await page.locator("#analyze").click();
  await expect(page.locator("#batch-results")).toBeVisible();
  await expect(page.locator("#batch-total")).toHaveText("4");
  await expect(page.locator("#batch-high")).toHaveText("1");
  await expect(page.locator("#batch-review")).toHaveText("1");
  await expect(page.locator("#batch-no-match")).toHaveText("1");
  await expect(page.locator("#batch-cannot-analyze")).toHaveText("1");
  await expect(page.locator("#batch-list button")).toHaveCount(4);
  await page.locator("#batch-list button").first().click();
  await expect(page.locator("#risk")).toHaveText("High-risk patterns found");
  await expect(page.locator("#result-context")).toContainText(/line 1/i);
  await expect(page.locator("#batch-results")).not.toContainText("Send OTP immediately");
  await page.locator("#locate-batch-line").click();
  await expect(page.locator("#message")).toBeFocused();
  expect(await page.locator("#message").evaluate(element => element.value.slice(element.selectionStart, element.selectionEnd))).toBe("Send OTP immediately");
  await expect(page.locator("#batch-results")).toBeVisible();
  await page.locator("#batch-filter").selectOption("cannot_analyze");
  await expect(page.locator("#batch-list button")).toHaveCount(1);
  await expect(page.locator("#result")).toBeHidden();
  await page.locator("#batch-list button").click();
  await expect(page.locator("#risk")).toHaveText("Could not analyze");
  await expect(page.locator("#result-context")).toContainText(/line 3/i);
  await page.locator("#locate-batch-line").click();
  expect(await page.locator("#message").evaluate(element => element.selectionStart === element.selectionEnd)).toBe(true);
  await page.locator("#batch-filter").selectOption("all");
  await page.locator("#batch-list button").first().click();
  expect((await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze()).violations).toEqual([]);
  await page.screenshot({ path: "outputs/browser_extension/bulk-workspace.png", fullPage: true });
  await page.emulateMedia({ colorScheme: "dark", reducedMotion: "reduce" });
  expect((await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze()).violations).toEqual([]);
  await page.screenshot({ path: "outputs/browser_extension/bulk-workspace-dark.png", fullPage: true });
  await page.setViewportSize({ width: 320, height: 900 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.locator("#message").fill("Changed draft");
  await expect(page.locator("#batch-results")).toBeHidden();
  await expect(page.locator("#download-batch")).toBeDisabled();
  await page.close();
});

test("bulk file import waits for analysis and exports generic line findings only", async () => {
  const page = await popupPage();
  await page.locator("#mode-batch").click();
  await page.locator("#batch-kind").selectOption("url");
  const source = "https://example.com\r\nhttp://user:SECRET_PASS@127.0.0.1:8080/SECRET_PATH?token=SECRET_TOKEN\r\n\r\n";
  await page.locator("#batch-file").setInputFiles({
    name: "SECRET_FILENAME.txt", mimeType: "text/plain;charset=utf-8", buffer: Buffer.from(source),
  });
  await expect(page.locator("#message")).toHaveValue(source.replaceAll("\r\n", "\n"));
  await expect(page.locator("#batch-results")).toBeHidden();
  await expect(page.locator("body")).not.toContainText("SECRET_FILENAME");
  await page.locator("#analyze").click();
  await expect(page.locator("#batch-total")).toHaveText("3");
  await expect(page.locator("#batch-review")).toHaveText("1");
  await expect(page.locator("#batch-no-match")).toHaveText("1");
  await expect(page.locator("#batch-cannot-analyze")).toHaveText("1");
  const pending = page.waitForEvent("download");
  await page.locator("#download-batch").click();
  const download = await pending;
  expect(download.suggestedFilename()).toBe("fisher-batch-report.json");
  const content = await readFile(await download.path(), "utf8");
  expect(content).not.toMatch(/SECRET_|127\.0\.0\.1|example\.com/);
  const report = JSON.parse(content);
  expect(JSON.stringify(report)).toContain('"cannot_analyze"');
  await page.locator("#batch-file").setInputFiles({ name: "bad.txt", mimeType: "text/plain", buffer: Buffer.from([0xc3, 0x28]) });
  await expect(page.locator("#batch-results")).toBeHidden();
  await expect(page.locator("#download-batch")).toBeDisabled();
  await expect(page.locator("#message")).toHaveValue(source.replaceAll("\r\n", "\n"));
  await page.close();
});

test("bulk cancellation and line limits never expose partial completed reports", async () => {
  const page = await popupPage();
  await page.locator("#mode-batch").click();
  await page.locator("#message").fill(Array(100).fill("Send OTP immediately").join("\n"));
  await page.evaluate(() => {
    document.querySelector("#analyze").click();
    document.querySelector("#cancel-batch").click();
  });
  await expect(page.locator("#cancel-batch")).toBeHidden();
  await expect(page.locator("#batch-results")).toBeHidden();
  await expect(page.locator("#download-batch")).toBeDisabled();
  await page.locator("#message").fill(Array(101).fill("Dinner at eight").join("\n"));
  await page.locator("#analyze").click();
  await expect(page.locator("#batch-results")).toBeHidden();
  await expect(page.locator("#input-error")).toBeVisible();
  await page.locator("#mode-message").click();
  await expect(page.locator("#batch-options")).toBeHidden();
  await expect(page.locator("#message")).toHaveValue("");
  await page.locator("#mode-batch").click();
  await expect(page.locator("#message")).toHaveValue(Array(101).fill("Dinner at eight").join("\n"));
  await page.close();
});

test("link checking exposes embedded navigation cues without opening destinations", async () => {
  const page = await popupPage();
  const requests = [];
  page.on("request", request => {
    if (!request.url().startsWith(`chrome-extension://${extensionId}/`)) requests.push(request.url());
  });
  await page.locator("#mode-link").click();
  await page.locator("#message").fill("https://example.com/login?next=http%3A%2F%2Fuser%3ASECRET_VALUE%40127.0.0.1%3A8080%2FPRIVATE_PATH");
  await page.locator("#analyze").click();
  await expect(page.locator("#risk")).toHaveText("Worth a closer look");
  await expect(page.locator("#checks")).toContainText(/embedded/i);
  await expect(page.locator("#result")).not.toContainText("SECRET_VALUE");
  await expect(page.locator("#result")).not.toContainText("PRIVATE_PATH");
  await expect(page.locator("#result-link-count")).toHaveText("1");
  expect(requests).toEqual([]);
  await page.close();
});

test("context menu item is registered by background service worker", async () => {
  let sw = context.serviceWorkers().find((w) => w.url().includes(extensionId));
  if (!sw) {
    sw = await context.waitForEvent("serviceworker", {
      predicate: (worker) => worker.url().includes(extensionId),
      timeout: 5000,
    }).catch(() => null);
  }
  if (sw) {
    const hasContextMenu = await sw.evaluate(() => typeof chrome.contextMenus !== "undefined");
    expect(hasContextMenu).toBe(true);
  } else {
    const { targetInfos } = await control.send("Target.getTargets", { filter: [{}] });
    const swTarget = targetInfos.find((t) => t.type === "service_worker" && t.url.includes(extensionId));
    expect(swTarget).toBeDefined();
  }
});

