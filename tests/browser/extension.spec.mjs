import { test, expect, chromium } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { createServer } from "node:http";
import { fileURLToPath } from "node:url";

let context;
let control;
let extensionId;
let fixtureServer;
let fixtureUrl;
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
  fixtureServer = createServer((_request, response) => {
    response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    response.end('<!doctype html><html lang="en"><title>Fisher synthetic fixture</title><p id="unselected">UNSELECTED_CANARY send OTP immediately</p><p id="selected">Lunch at noon</p></html>');
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
  await control.send("Extensions.triggerAction", { id: extensionId, targetId: tab.targetId });
  let popupTarget;
  await expect.poll(async () => {
    const { targetInfos: targets } = await control.send("Target.getTargets", { filter: [{}] });
    popupTarget = targets.find((target) => target.type === "page" && target.url.includes(extensionId));
    return !!popupTarget;
  }).toBe(true);
  const evaluate = await popupEvaluator(popupTarget.targetId);
  await expect.poll(() => evaluate("document.readyState")).toBe("complete");
  return { evaluate, targetId: popupTarget.targetId };
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
  await page.screenshot({ path: "outputs/browser_extension/v0.4-result.png", fullPage: true });
  await page.locator("#clear").click();
  await expect(page.locator("#message")).toHaveValue("");
  await expect(page.locator("#message")).toBeFocused();
  await expect(page.locator("#result")).toBeHidden();
  expect(errors).toEqual([]);
  expect(externalRequests).toEqual([]);
  await page.close();
});

test("link mode, keyboard shortcut, and edits keep results current", async () => {
  const page = await popupPage();
  await page.locator("#mode-link").click();
  await expect(page.locator("#selection")).toBeHidden();
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
  await page.close();
});

test("examples wait for an explicit check and oversized paste is rejected whole", async () => {
  const page = await popupPage();
  await page.locator('[data-example="account"]').click();
  await expect(page.locator("#message")).not.toHaveValue("");
  await expect(page.locator("#result")).toBeHidden();
  await page.locator("#message").fill("a".repeat(45_000) + " send OTP immediately");
  expect((await page.locator("#message").inputValue()).length).toBeGreaterThan(45_000);
  await page.locator("#analyze").click();
  await expect(page.locator("#risk")).toContainText(/Could not|Cannot/);
  await expect(page.locator("#reasons")).toContainText("20,000");
  await page.close();
});

test("real toolbar action grants only explicit selected-text access", async () => {
  const fixture = await context.newPage();
  await fixture.goto(fixtureUrl);
  await fixture.evaluate(() => {
    const range = document.createRange();
    range.selectNodeContents(document.querySelector("#selected"));
    getSelection().removeAllRanges();
    getSelection().addRange(range);
  });
  const { evaluate, targetId } = await openToolbarPopup(fixture);
  await expect.poll(() => evaluate("Boolean(document.querySelector('#selection'))")).toBe(true);
  expect(await evaluate("document.querySelector('#result').hidden")).toBe(true);
  await evaluate("document.querySelector('#selection').click()");
  await expect.poll(() => evaluate("document.querySelector('#risk').textContent")).toContain("No clear");
  expect(await evaluate("document.querySelector('#message').value")).toBe("");
  expect(await evaluate("document.body.textContent.includes('UNSELECTED_CANARY')")).toBe(false);
  await control.send("Target.closeTarget", { targetId });
  await fixture.close();
});

for (const restricted of [false, true]) {
  test(restricted ? "restricted browser page fails with a generic result" : "empty page selection produces no safety result", async () => {
    const fixture = await context.newPage();
    await fixture.goto(restricted ? "chrome://version/" : fixtureUrl);
    const { evaluate, targetId } = await openToolbarPopup(fixture);
    await evaluate("document.querySelector('#selection').click()");
    await expect.poll(() => evaluate("document.querySelector('#risk').textContent")).toBe("Could not analyze");
    const reasons = await evaluate("document.querySelector('#reasons').textContent");
    expect(reasons).toContain(restricted ? "could not be accessed" : "No selected page text");
    expect(await evaluate("document.querySelector('#message').value")).toBe("");
    await control.send("Target.closeTarget", { targetId });
    await fixture.close();
  });
}

test("empty and populated states pass automated accessibility checks", async () => {
  const page = await popupPage();
  const empty = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
  expect(empty.violations).toEqual([]);
  await page.screenshot({ path: "outputs/browser_extension/v0.4-popup.png", fullPage: true });
  await page.locator("#message").fill("Send OTP immediately");
  await page.locator("#analyze").click();
  const populated = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
  expect(populated.violations).toEqual([]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.close();
});
