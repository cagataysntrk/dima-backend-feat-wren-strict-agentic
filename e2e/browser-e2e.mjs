#!/usr/bin/env node
// Bağımlılıksız uçtan-uca (E2E) test: dima-frontend + dima-backend + dima (Wren).
//
// Ne yapar:
//   1. API katmanı — backend /health, /schema (ilişkiler dahil mi?), /ask (çapraz
//      tablo sorgusu JOIN üretip satır döndürüyor mu?).
//   2. Tarayıcı katmanı — sistem Chrome'unu headless başlatır, CDP (Chrome DevTools
//      Protocol) ile bağlanır, frontend'i açar, HYDRATION'ı doğrular (React fiber),
//      bir örnek butona tıklar ve gerçek fetch → üretilen SQL + sonuç tablosunu bekler.
//
// Bağımlılık YOK: Node 22 native fetch + WebSocket kullanır, headless Chrome sürücüsü elde.
//
// Kullanım:
//   node e2e/browser-e2e.mjs
//   FRONTEND_URL=http://localhost:3000 BACKEND_URL=http://localhost:8000 node e2e/browser-e2e.mjs
//   npm run e2e
//
// Ortam değişkenleri:
//   FRONTEND_URL  (varsayılan http://frontend.dima.localtld.sh)
//   BACKEND_URL   (varsayılan http://backend.dima.localtld.sh)
//   CHROME_BIN    (otomatik bulunamazsa Chrome ikili yolu)
//   CDP_PORT      (varsayılan 9222)
//   HEADFUL=1     (tarayıcıyı görünür başlat — hata ayıklama)

import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const FRONTEND_URL = process.env.FRONTEND_URL ?? "http://frontend.dima.localtld.sh";
const BACKEND_URL = process.env.BACKEND_URL ?? "http://backend.dima.localtld.sh";
const CDP_PORT = Number(process.env.CDP_PORT ?? 9222);
const CROSS_QUESTION = "Makine bazında verim ve fire oranı";

// --- küçük test koşucusu ----------------------------------------------------
let passed = 0;
let failed = 0;
function ok(name) {
  passed++;
  console.log(`  \x1b[32m✓\x1b[0m ${name}`);
}
function fail(name, detail) {
  failed++;
  console.log(`  \x1b[31m✗\x1b[0m ${name}`);
  if (detail) console.log(`      ${String(detail).split("\n").join("\n      ")}`);
}
function section(title) {
  console.log(`\n\x1b[1m${title}\x1b[0m`);
}
async function check(name, fn) {
  try {
    const detail = await fn();
    ok(detail ? `${name} — ${detail}` : name);
  } catch (err) {
    fail(name, err?.message ?? err);
  }
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// --- Faz 1: API katmanı -----------------------------------------------------
async function testApi() {
  section(`API — ${BACKEND_URL}`);

  await check("GET /health 200", async () => {
    const r = await fetch(`${BACKEND_URL}/health`);
    if (!r.ok) throw new Error(`status ${r.status}`);
  });

  await check("GET /schema ilişkileri içeriyor", async () => {
    const r = await fetch(`${BACKEND_URL}/schema`);
    if (!r.ok) throw new Error(`status ${r.status}`);
    const s = await r.json();
    const rels = s.relationships ?? [];
    if (rels.length < 2) throw new Error(`ilişki sayısı ${rels.length}`);
    if (!rels.some((x) => x.condition?.includes("makineler.makine")))
      throw new Error("makineler hub ilişkisi yok");
    return `${s.models.length} model, ${rels.length} ilişki`;
  });

  await check("POST /ask geçerli SQL üretir ve satır döndürür", async () => {
    const r = await fetch(`${BACKEND_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: CROSS_QUESTION }),
    });
    if (!r.ok) throw new Error(`status ${r.status}`);
    const d = await r.json();
    // Sağlayıcıya göre (kural/LLM) SQL şekli değişir → kesin şekil değil, SONUÇ doğrula.
    if (!/^\s*(with|select)\b/i.test(d.sql || "")) throw new Error(`SELECT değil: ${d.sql}`);
    const rows = d.result?.row_count ?? 0;
    if (rows < 1) throw new Error("0 satır döndü");
    return `${rows} satır, SQL üretildi ve çalıştı`;
  });
}

// --- Chrome bulma + başlatma ------------------------------------------------
function findChrome() {
  if (process.env.CHROME_BIN && existsSync(process.env.CHROME_BIN)) return process.env.CHROME_BIN;
  const candidates = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
  ];
  for (const c of candidates) if (existsSync(c)) return c;
  throw new Error("Chrome bulunamadı. CHROME_BIN ile yol verin.");
}

function launchChrome(url) {
  const bin = findChrome();
  const profileDir = mkdtempSync(join(tmpdir(), "dima-e2e-chrome-"));
  const headless = process.env.HEADFUL ? [] : ["--headless=new"];
  const args = [
    ...headless,
    `--remote-debugging-port=${CDP_PORT}`,
    `--user-data-dir=${profileDir}`,
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
    "--disable-gpu",
    "--window-size=1280,900",
    url, // Chrome'u doğrudan URL'de aç — Page.navigate context yarışını önler
  ];
  const proc = spawn(bin, args, { stdio: "ignore" });
  return { proc, profileDir };
}

// --- minimal CDP istemcisi (native WebSocket) -------------------------------
async function getPageTarget(url) {
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${CDP_PORT}/json`);
      const targets = await r.json();
      const page = targets.find(
        (t) => t.type === "page" && t.webSocketDebuggerUrl && !t.url.startsWith("devtools://"),
      );
      if (page) return page;
    } catch {
      /* Chrome henüz dinlemiyor */
    }
    await sleep(250);
  }
  throw new Error("CDP page target bulunamadı (Chrome başlamadı mı?)");
}

class Cdp {
  constructor(ws) {
    this.ws = ws;
    this.id = 0;
    this.pending = new Map();
    ws.addEventListener("message", (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
      }
    });
  }
  static async connect(wsUrl) {
    const ws = new WebSocket(wsUrl);
    await new Promise((resolve, reject) => {
      ws.addEventListener("open", resolve, { once: true });
      ws.addEventListener("error", () => reject(new Error("WS bağlanamadı")), { once: true });
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
  // Sayfada JS çalıştır; değeri döndür (JSON serileştirilebilir olmalı).
  async evaluate(expression) {
    const res = await this.send("Runtime.evaluate", {
      expression,
      returnByValue: true,
      awaitPromise: true,
    });
    if (res.exceptionDetails)
      throw new Error(res.exceptionDetails.exception?.description ?? "eval hatası");
    return res.result.value;
  }
  close() {
    try {
      this.ws.close();
    } catch {
      /* yut */
    }
  }
}

async function waitFor(cdp, expression, { timeout = 15000, interval = 300, label = "" } = {}) {
  const start = Date.now();
  let last;
  while (Date.now() - start < timeout) {
    last = await cdp.evaluate(expression);
    if (last) return last;
    await sleep(interval);
  }
  throw new Error(`zaman aşımı${label ? ` (${label})` : ""}; son değer: ${JSON.stringify(last)}`);
}

// --- Faz 2: Tarayıcı katmanı ------------------------------------------------
async function testBrowser() {
  section(`Tarayıcı — ${FRONTEND_URL}`);
  let chrome;
  let cdp;
  try {
    chrome = launchChrome(FRONTEND_URL);
    const target = await getPageTarget(FRONTEND_URL);
    cdp = await Cdp.connect(target.webSocketDebuggerUrl);
    await cdp.send("Runtime.enable");

    await check("Sayfa yüklendi (başlık render edildi)", async () => {
      const title = await waitFor(
        cdp,
        `document.querySelector('h1')?.textContent || ''`,
        { label: "h1" },
      );
      return title;
    });

    // KRİTİK: localtld/Caddy origin'inde allowedDevOrigins yoksa React hydrate olmaz.
    await check("Client HYDRATE oldu (React fiber mevcut)", async () => {
      const has = await waitFor(
        cdp,
        `(() => {
          const btns = [...document.querySelectorAll('button')];
          const b = btns.find(x => Object.keys(x).some(k => k.startsWith('__reactFiber')));
          return !!b;
        })()`,
        { label: "reactFiber" },
      );
      if (!has) throw new Error("hiçbir butonda React fiber yok — hydrate olmadı");
    });

    await check(`Örnek butona tıkla → input dolar ("${CROSS_QUESTION}")`, async () => {
      const clicked = await cdp.evaluate(`(() => {
        const btns = [...document.querySelectorAll('button')];
        const b = btns.find(x => (x.textContent || '').trim() === ${JSON.stringify(CROSS_QUESTION)});
        if (!b) return false;
        b.click();
        return true;
      })()`);
      if (!clicked) throw new Error("örnek buton bulunamadı");
      // setState asenkron: input değeri bir sonraki render'da güncellenir → bekle.
      await waitFor(
        cdp,
        `(document.querySelector('input')?.value || '').includes('verim')`,
        { label: "input value" },
      );
    });

    await check("Sonuç geldi: SQL + grafik render edildi", async () => {
      // Sonuç varsayılan olarak GRAFİK (ECharts canvas) olarak gelir.
      const res = await waitFor(
        cdp,
        `(() => {
          const pre = document.querySelector('pre');
          const canvas = document.querySelector('canvas');
          const rows = document.querySelectorAll('table tbody tr').length;
          if (!pre || (!canvas && rows === 0)) return null;
          return { sql: pre.textContent, chart: !!canvas, rows };
        })()`,
        { timeout: 20000, label: "sonuç grafiği" },
      );
      if (!/\b(select|with)\b/i.test(res.sql)) throw new Error(`SQL yok/geçersiz: ${res.sql}`);
      return res.chart ? "ECharts grafik + SQL üretildi" : `${res.rows} satır (tablo)`;
    });

    await check("Tablo görünümüne geçilebiliyor", async () => {
      await cdp.evaluate(`(() => {
        const b = [...document.querySelectorAll('button')].find(x => (x.textContent||'').trim() === 'Tablo');
        if (b) b.click();
      })()`);
      await waitFor(cdp, `document.querySelectorAll('table tbody tr').length > 0`, {
        label: "tablo satırları",
      });
    });
  } finally {
    cdp?.close();
    if (chrome) {
      try {
        chrome.proc.kill("SIGTERM");
      } catch {
        /* yut */
      }
      try {
        rmSync(chrome.profileDir, { recursive: true, force: true });
      } catch {
        /* yut */
      }
    }
  }
}

// --- ana --------------------------------------------------------------------
(async () => {
  console.log("dima uçtan-uca test (frontend + backend + Wren engine)");
  await testApi();
  try {
    await testBrowser();
  } catch (err) {
    fail("Tarayıcı testi başlatılamadı", err?.message ?? err);
  }

  console.log(`\n\x1b[1mÖzet:\x1b[0m ${passed} geçti, ${failed} kaldı`);
  process.exit(failed === 0 ? 0 : 1);
})();
