#!/usr/bin/env node

import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const FRONTEND_URL = process.env.FRONTEND_URL ?? "http://127.0.0.1:3000/fast-poc";
const TOKEN = process.env.DIMA_FAST_E2E_TOKEN ?? "";
const CDP_PORT = Number(process.env.CDP_PORT ?? 9232);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

if (!TOKEN) throw new Error("DIMA_FAST_E2E_TOKEN is required");

function findChrome() {
  const candidates = [
    process.env.CHROME_BIN,
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  ].filter(Boolean);
  for (const candidate of candidates) {
    if (existsSync(candidate)) return candidate;
  }
  throw new Error("Chrome/Chromium not found");
}

function launchChrome() {
  const profileDir = mkdtempSync(join(tmpdir(), "dima-fast-ask-"));
  const proc = spawn(findChrome(), [
    "--headless=new",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-background-networking",
    "--no-first-run",
    "--no-default-browser-check",
    `--remote-debugging-port=${CDP_PORT}`,
    `--user-data-dir=${profileDir}`,
    "--window-size=1440,900",
    "about:blank",
  ], { stdio: "ignore" });
  return { proc, profileDir };
}

async function target() {
  for (let i = 0; i < 80; i++) {
    try {
      const response = await fetch(`http://127.0.0.1:${CDP_PORT}/json`);
      const targets = await response.json();
      const pageTarget = targets.find((item) => item.type === "page" && item.webSocketDebuggerUrl);
      if (pageTarget) return pageTarget;
    } catch {}
    await sleep(250);
  }
  throw new Error("CDP target timeout");
}

class Cdp {
  constructor(ws) {
    this.ws = ws;
    this.id = 0;
    this.pending = new Map();
    ws.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      if (!message.id || !this.pending.has(message.id)) return;
      const pending = this.pending.get(message.id);
      this.pending.delete(message.id);
      message.error ? pending.reject(new Error(message.error.message)) : pending.resolve(message.result);
    });
  }

  static async connect(url) {
    const ws = new WebSocket(url);
    await new Promise((resolve, reject) => {
      ws.addEventListener("open", resolve, { once: true });
      ws.addEventListener("error", reject, { once: true });
    });
    return new Cdp(ws);
  }

  send(method, params = {}) {
    const id = ++this.id;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async eval(expression) {
    const response = await this.send("Runtime.evaluate", {
      expression,
      returnByValue: true,
      awaitPromise: true,
    });
    if (response.exceptionDetails) throw new Error("browser evaluation failed");
    return response.result.value;
  }
}

async function waitFor(cdp, expression, label, attempts = 100) {
  for (let i = 0; i < attempts; i++) {
    const value = await cdp.eval(expression);
    if (value) return value;
    await sleep(200);
  }
  throw new Error(`timeout: ${label}`);
}

async function ask(cdp, question, expectedSelector, expectedText = null) {
  const q = JSON.stringify(question);
  const submitted = await cdp.eval(`(() => {
    const input = document.querySelector('[data-fast-question]');
    const form = document.querySelector('[data-fast-ask-form]');
    if (!input || !form) return false;
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    setter.call(input, ${q});
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    form.requestSubmit();
    return true;
  })()`);
  if (!submitted) throw new Error(`could not submit question: ${question}`);

  await waitFor(cdp, `!!document.querySelector('[data-fast-loading]')`, "loading state");
  const expression = expectedText
    ? `document.querySelector('${expectedSelector}')?.textContent?.includes(${JSON.stringify(expectedText)})`
    : `!!document.querySelector('${expectedSelector}')`;
  await waitFor(cdp, expression, `${expectedSelector} for ${question}`);
}

const chrome = launchChrome();
let cdp;
try {
  const pageTarget = await target();
  cdp = await Cdp.connect(pageTarget.webSocketDebuggerUrl);
  await cdp.send("Runtime.enable");
  await cdp.send("Network.enable");
  await cdp.send("Page.enable");
  await cdp.send("Network.setExtraHTTPHeaders", {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });

  const origin = new URL(FRONTEND_URL).origin;
  const cookie = await cdp.send("Network.setCookie", {
    name: "dima_refresh",
    value: "fast-ft003-e2e-route-guard",
    url: origin,
    path: "/",
    httpOnly: true,
    sameSite: "Lax",
  });
  if (cookie.success === false) throw new Error("failed to set route-guard cookie");

  await cdp.send("Page.navigate", { url: FRONTEND_URL });
  await waitFor(
    cdp,
    `document.querySelector('[data-fast-poc="true"] h1')?.textContent?.includes('First real Ask')`,
    "FT-003 heading",
  );

  // Browser-only network latency makes the loading state observable without
  // changing product code or backend behavior.
  await cdp.send("Network.emulateNetworkConditions", {
    offline: false,
    latency: 350,
    downloadThroughput: -1,
    uploadThroughput: -1,
    connectionType: "wifi",
  });

  await ask(cdp, "Son 30 günde kaç sipariş var?", "[data-fast-answer]", "20 kayıt");
  const countRows = await waitFor(
    cdp,
    `document.querySelectorAll('[data-fast-table] table tbody tr').length`,
    "count table",
  );
  if (countRows !== 1) throw new Error(`COUNT table rows expected 1, got ${countRows}`);

  await ask(cdp, "Son 30 gündeki sipariş tutarı ne kadar?", "[data-fast-answer]", "16270");
  const sumRows = await waitFor(
    cdp,
    `document.querySelectorAll('[data-fast-table] table tbody tr').length`,
    "sum table",
  );
  if (sumRows !== 1) throw new Error(`SUM table rows expected 1, got ${sumRows}`);

  await ask(cdp, "Son 30 günde bölgelere göre sipariş tutarı", "[data-fast-answer]", "4 kırılım");
  await waitFor(cdp, `!!document.querySelector('[data-fast-chart] canvas')`, "breakdown chart");
  const breakdownEvidence = await cdp.eval(`(() => ({
    source: document.querySelector('[data-evidence-source]')?.textContent?.trim(),
    period: document.querySelector('[data-evidence-period]')?.textContent?.trim(),
    measure: document.querySelector('[data-evidence-measure]')?.textContent?.trim(),
    breakdown: document.querySelector('[data-evidence-breakdown]')?.textContent?.trim(),
    fingerprint: document.querySelector('[data-evidence-query-fingerprint]')?.textContent?.trim(),
  }))()`);
  if (breakdownEvidence.source !== "metabase://table/1") throw new Error(JSON.stringify(breakdownEvidence));
  if (breakdownEvidence.measure !== "amount") throw new Error(JSON.stringify(breakdownEvidence));
  if (breakdownEvidence.breakdown !== "region") throw new Error(JSON.stringify(breakdownEvidence));
  if (!breakdownEvidence.fingerprint || breakdownEvidence.fingerprint.length !== 12) {
    throw new Error(JSON.stringify(breakdownEvidence));
  }

  await ask(cdp, "Siparişleri say.", "[data-fast-clarification]");
  await ask(cdp, "Siparişlerin ortalama tutarı nedir?", "[data-fast-unsupported]");
  await ask(cdp, "Hatalı alanla sipariş tutarı", "[data-fast-failed]");

  await ask(cdp, "Son 30 günde bölgelere göre sipariş tutarı", "[data-fast-answer]", "4 kırılım");
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: 390,
    height: 844,
    deviceScaleFactor: 1,
    mobile: true,
  });
  await sleep(350);

  const narrow = await cdp.eval(`(() => {
    const shell = document.querySelector('[data-fast-shell]');
    if (!shell) return null;
    return {
      width: shell.getBoundingClientRect().width,
      viewport: window.innerWidth,
      scrollWidth: document.documentElement.scrollWidth,
    };
  })()`);
  if (!narrow) throw new Error("mobile shell missing");
  if (narrow.width > narrow.viewport + 1) throw new Error(`shell overflow: ${JSON.stringify(narrow)}`);
  if (narrow.scrollWidth > narrow.viewport + 4) throw new Error(`document overflow: ${JSON.stringify(narrow)}`);

  const leaked = await cdp.eval(`
    document.body.innerText.includes('Collections') ||
    document.body.innerText.includes('Query Builder') ||
    document.body.innerText.includes('Metabase Search')
  `);
  if (leaked) throw new Error("generic Metabase workspace copy leaked into FT-003 UI");

  console.log(JSON.stringify({
    status: "GREEN",
    backend: "real /fast/ask",
    cognition: "scripted browser harness",
    metabase: "real pinned OSS",
    db: "real synthetic lab",
    count: "PASS",
    sum: "PASS",
    breakdown: "PASS",
    loading: "PASS",
    clarification: "PASS",
    unsupported: "PASS",
    failed: "PASS",
    chart: "PASS",
    table: "PASS",
    desktop: "1440x900 PASS",
    mobile: { width: 390, height: 844, ...narrow },
  }, null, 2));
} finally {
  try { cdp?.ws?.close(); } catch {}
  try { chrome.proc.kill("SIGTERM"); } catch {}
  try { rmSync(chrome.profileDir, { recursive: true, force: true }); } catch {}
}
