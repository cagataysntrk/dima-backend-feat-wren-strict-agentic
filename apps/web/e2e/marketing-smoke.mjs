#!/usr/bin/env node

import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { spawn } from "node:child_process";
import { join } from "node:path";
import { tmpdir } from "node:os";

const BASE = process.env.MARKETING_FRONTEND_URL ?? process.env.FRONTEND_URL ?? "http://localhost:3000";
const CDP_PORT = Number(process.env.MARKETING_CDP_PORT ?? 9233);
const routes = [
  "/",
  "/product",
  "/how-it-works",
  "/solutions",
  "/solutions/textile-dyehouse",
  "/security",
  "/integrations",
  "/about",
  "/contact",
  "/privacy",
  "/terms",
];

let passed = 0;
let failed = 0;
function check(name, condition, detail = "") {
  if (condition) {
    passed += 1;
    console.log(`  ✓ ${name}${detail ? ` — ${detail}` : ""}`);
  } else {
    failed += 1;
    console.error(`  ✗ ${name}${detail ? ` — ${detail}` : ""}`);
  }
}

async function request(path, options = {}) {
  return fetch(new URL(path, BASE), { redirect: "manual", ...options });
}

async function testRoutes() {
  console.log(`Marketing routes — ${BASE}`);
  for (const route of routes) {
    const response = await request(route);
    check(`${route} returns 200`, response.status === 200, String(response.status));
  }
  const missing = await request(`/marketing-route-does-not-exist-${Date.now()}`);
  check("unknown public route returns 404", missing.status === 404, String(missing.status));
  const protectedResponse = await request("/app");
  const location = protectedResponse.headers.get("location") ?? "";
  check("logged-out /app redirects to login", [301, 302, 307, 308].includes(protectedResponse.status) && location.includes("/login?next=%2Fapp"), `${protectedResponse.status} ${location}`);
  const robots = await request("/robots.txt");
  const robotsText = await robots.text();
  check("robots excludes application and API surfaces", robotsText.includes("Disallow: /") || (robotsText.includes("/app") && robotsText.includes("/api/")));
  const sitemap = await request("/sitemap.xml");
  const sitemapText = await sitemap.text();
  check("sitemap includes textile route", sitemapText.includes("/solutions/textile-dyehouse"));
  check("unapproved legal pages are visibly gated", (await request("/privacy").then((r) => r.text())).includes("LEGAL REVIEW REQUIRED"));
}

function findChrome() {
  const candidates = [
    process.env.CHROME_BIN,
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
  ].filter(Boolean);
  return candidates.find((candidate) => existsSync(candidate));
}

async function waitForTarget() {
  for (let attempt = 0; attempt < 50; attempt += 1) {
    try {
      const response = await fetch(`http://127.0.0.1:${CDP_PORT}/json`);
      const targets = await response.json();
      const page = targets.find((target) => target.type === "page" && target.webSocketDebuggerUrl);
      if (page) return page;
    } catch {
      // Chrome is still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  throw new Error("Chrome CDP target was not available");
}

class Cdp {
  constructor(webSocket) {
    this.webSocket = webSocket;
    this.id = 0;
    this.pending = new Map();
    webSocket.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      const pending = this.pending.get(message.id);
      if (!pending) return;
      this.pending.delete(message.id);
      if (message.error) pending.reject(new Error(message.error.message));
      else pending.resolve(message.result);
    });
  }

  static async connect(url) {
    const socket = new WebSocket(url);
    await new Promise((resolve, reject) => {
      socket.addEventListener("open", resolve, { once: true });
      socket.addEventListener("error", () => reject(new Error("CDP WebSocket connection failed")), { once: true });
    });
    return new Cdp(socket);
  }

  send(method, params = {}) {
    const id = ++this.id;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.webSocket.send(JSON.stringify({ id, method, params }));
    });
  }

  async evaluate(expression) {
    const result = await this.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description ?? "Runtime evaluation failed");
    return result.result.value;
  }

  close() {
    this.webSocket.close();
  }
}

async function testBrowser() {
  const chromePath = findChrome();
  if (!chromePath) {
    check("browser smoke", false, "Chrome binary not found");
    return;
  }
  const profile = mkdtempSync(join(tmpdir(), "dima-marketing-smoke-"));
  const chrome = spawn(chromePath, ["--headless=new", `--remote-debugging-port=${CDP_PORT}`, `--user-data-dir=${profile}`, "--no-first-run", "--no-default-browser-check", "--disable-gpu", `--window-size=1280,900`, BASE], { stdio: "ignore" });
  let cdp;
  try {
    const target = await waitForTarget();
    cdp = await Cdp.connect(target.webSocketDebuggerUrl);
    await cdp.send("Runtime.enable");
    await cdp.send("Page.enable");
    await cdp.send("Page.navigate", { url: new URL("/solutions/textile-dyehouse", BASE).toString() });
    await new Promise((resolve) => setTimeout(resolve, 1500));
    const pageFacts = await cdp.evaluate(`({ url: location.pathname, h1: document.querySelectorAll('h1').length, main: !!document.querySelector('main'), header: !!document.querySelector('header'), footer: !!document.querySelector('footer'), overflow: document.documentElement.scrollWidth > window.innerWidth + 1 })`);
    check("textile page has one H1 and landmarks", pageFacts.url === "/solutions/textile-dyehouse" && pageFacts.h1 === 1 && pageFacts.main && pageFacts.header && pageFacts.footer, JSON.stringify(pageFacts));
    check("textile page has no horizontal overflow", !pageFacts.overflow);

    await cdp.send("Emulation.setDeviceMetricsOverride", { width: 375, height: 812, deviceScaleFactor: 1, mobile: true });
    await cdp.send("Page.navigate", { url: new URL("/", BASE).toString() });
    await new Promise((resolve) => setTimeout(resolve, 1000));
    const mobileFacts = await cdp.evaluate(`(() => { const button = [...document.querySelectorAll('button[aria-label]')].find((item) => /menu|menü/i.test(item.getAttribute('aria-label') || '')); return { trigger: !!button, overflow: document.documentElement.scrollWidth > window.innerWidth + 1, menuText: button?.getAttribute('aria-label') || '' }; })()`);
    check("mobile header exposes a labelled menu control", mobileFacts.trigger && mobileFacts.menuText.length > 0, mobileFacts.menuText);
    check("mobile homepage has no horizontal overflow", !mobileFacts.overflow);
    await cdp.evaluate(`(() => { const button = [...document.querySelectorAll('button[aria-label]')].find((item) => /menu|menü/i.test(item.getAttribute('aria-label') || '')); button?.click(); return !!button; })()`);
    await new Promise((resolve) => setTimeout(resolve, 250));
    const menuOpen = await cdp.evaluate(`document.querySelector('[data-slot="sheet-content"]')?.getAttribute('data-state') === 'open'`);
    check("mobile menu opens", menuOpen === true);
    await cdp.send("Input.dispatchKeyEvent", { type: "keyDown", key: "Escape", code: "Escape", windowsVirtualKeyCode: 27 });
    await cdp.send("Input.dispatchKeyEvent", { type: "keyUp", key: "Escape", code: "Escape", windowsVirtualKeyCode: 27 });
    await new Promise((resolve) => setTimeout(resolve, 250));
    const menuClosed = await cdp.evaluate(`document.querySelector('[data-slot="sheet-content"]')?.getAttribute('data-state') !== 'open'`);
    check("Escape closes mobile menu", menuClosed === true);
  } catch (error) {
    check("browser smoke", false, error.message);
  } finally {
    cdp?.close();
    chrome.kill("SIGKILL");
    await new Promise((resolve) => setTimeout(resolve, 150));
    rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
  }
}

try {
  await testRoutes();
  await testBrowser();
} catch (error) {
  check("marketing smoke runner", false, error.message);
}

console.log(`\nMarketing smoke summary: ${passed} passed, ${failed} failed`);
process.exit(failed === 0 ? 0 : 1);
