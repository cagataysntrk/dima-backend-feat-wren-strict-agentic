#!/usr/bin/env node

import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const FRONTEND_URL = process.env.FRONTEND_URL ?? "http://127.0.0.1:3000/fast-poc";
const CDP_PORT = Number(process.env.CDP_PORT ?? 9232);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

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
  const profileDir = mkdtempSync(join(tmpdir(), "dima-fast-poc-"));
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
    FRONTEND_URL,
  ], { stdio: "ignore" });
  return { proc, profileDir };
}

async function target() {
  for (let i = 0; i < 60; i++) {
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

async function waitFor(cdp, expression, label) {
  for (let i = 0; i < 60; i++) {
    const value = await cdp.eval(expression);
    if (value) return value;
    await sleep(250);
  }
  throw new Error(`timeout: ${label}`);
}

const chrome = launchChrome();
let cdp;
try {
  const pageTarget = await target();
  cdp = await Cdp.connect(pageTarget.webSocketDebuggerUrl);
  await cdp.send("Runtime.enable");

  await waitFor(
    cdp,
    `document.querySelector('[data-fast-poc="true"] h1')?.textContent?.includes('Analyst rendering POC')`,
    "POC heading",
  );

  await waitFor(cdp, `!!document.querySelector('[data-fast-chart] canvas')`, "chart canvas");

  const chartMeta = await cdp.eval(`(() => ({
    chart: !!document.querySelector('[data-fast-chart] canvas'),
    workspaceText: document.body.innerText.includes('Collections') || document.body.innerText.includes('Query Builder'),
    fast: !!document.querySelector('[data-fast-poc="true"]')
  }))()`);

  if (!chartMeta.chart || !chartMeta.fast) throw new Error("chart/shell missing");
  if (chartMeta.workspaceText) throw new Error("generic Metabase workspace copy leaked into POC");

  const switched = await cdp.eval(`(() => {
    const button = [...document.querySelectorAll('button')].find((item) => item.textContent?.trim() === 'Tablo');
    if (!button) return false;
    button.click();
    return true;
  })()`);
  if (!switched) throw new Error("table toggle missing");

  const rows = await waitFor(
    cdp,
    `document.querySelectorAll('[data-fast-table] table tbody tr').length`,
    "table rows",
  );
  if (rows !== 12) throw new Error(`expected 12 table rows, got ${rows}`);

  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: 390,
    height: 844,
    deviceScaleFactor: 1,
    mobile: true,
  });
  await sleep(300);

  const narrow = await cdp.eval(`(() => {
    const shell = document.querySelector('[data-fast-shell]');
    if (!shell) return null;
    return {
      width: shell.getBoundingClientRect().width,
      viewport: window.innerWidth,
      scrollWidth: document.documentElement.scrollWidth,
    };
  })()`);

  if (!narrow) throw new Error("narrow shell missing");
  if (narrow.width > narrow.viewport + 1) throw new Error(`shell overflow: ${JSON.stringify(narrow)}`);
  if (narrow.scrollWidth > narrow.viewport + 4) throw new Error(`document overflow: ${JSON.stringify(narrow)}`);

  console.log(JSON.stringify({
    status: "GREEN",
    chart: true,
    table_rows: rows,
    narrow,
    route: "/fast-poc",
  }, null, 2));
} finally {
  try { cdp?.ws?.close(); } catch {}
  try { chrome.proc.kill("SIGTERM"); } catch {}
  try { rmSync(chrome.profileDir, { recursive: true, force: true }); } catch {}
}
