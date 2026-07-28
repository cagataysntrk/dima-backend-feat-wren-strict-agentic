"use client";

import { useMemo, useState } from "react";
import { Renderer } from "@openuidev/react-lang";

import { CatalogProvider, catalogSummary } from "@/lib/catalog";
import { fixtures } from "@/lib/fixtures";
import { library } from "@/lib/library";

/**
 * VOKABÜLER TEZGÂHI.
 *
 * Amacı modelin panoyu güzel kurup kurmadığına bakmak DEĞİL — önce dilin
 * kompozisyonu ifade edebildiğini ve renderer'ın gerçek `AskResponse`'larla
 * doğru çizdiğini görmek. Bu yüzden sayfa ANAHTAR OLMADAN da tam çalışır:
 * soldaki metni elle düzenler, sağda sonucu görürsün.
 *
 * "Model ile üret" düğmesi anahtar varsa çalışır; yoksa 503 döner ve tezgâhın
 * geri kalanı etkilenmez.
 */

const SAMPLE = `root = Dashboard("Üretim Panosu", [ust, egilim, detay])
ust = Grid([k1, k2, k3], "3")
k1 = KpiTile("q1")
k2 = KpiTile("q2")
k3 = KpiTile("q6")
egilim = Section("Eğilim", [c1, yorum])
c1 = ChartTile("q3")
yorum = InsightNote("q3")
detay = Section("Detay", [alt])
alt = Grid([c2, t1], "2")
c2 = ChartTile("q4", "bar-h")
t1 = TableTile("q5", 6)`;

export default function Bench() {
  const [source, setSource] = useState(SAMPLE);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const catalog = useMemo(() => catalogSummary(fixtures), []);

  async function generate() {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          catalog,
          messages: [{ role: "user", content: "Üretim performansı panosu hazırla." }],
        }),
      });
      if (!res.ok) {
        const body = (await res.json().catch(() => null)) as { error?: string } | null;
        setError(body?.error ?? `İstek başarısız (${res.status}).`);
        return;
      }
      setSource(await res.text());
    } catch {
      setError("Ağ hatası.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="bench">
      <section className="bench-pane">
        <header>
          <h2>Katalog</h2>
          <p className="muted">Modele giden bilgi — yalnız şekil, satır yok.</p>
        </header>
        <pre className="bench-catalog">{catalog}</pre>

        <header>
          <h2>OpenUI Lang</h2>
          <p className="muted">Modelin üreteceği çıktı. Elle düzenleyebilirsin.</p>
        </header>
        <textarea
          value={source}
          onChange={(e) => setSource(e.target.value)}
          spellCheck={false}
          className="bench-source"
        />
        <button onClick={generate} disabled={busy}>
          {busy ? "Üretiliyor…" : "Model ile üret"}
        </button>
        {error ? <p className="bench-error">{error}</p> : null}
      </section>

      <section className="bench-pane bench-output">
        <header>
          <h2>Sonuç</h2>
          <p className="muted">Gerçek AskResponse verisiyle çizildi.</p>
        </header>
        <CatalogProvider entries={fixtures}>
          <Renderer
            response={source}
            library={library}
            // onError HER çözümlemede çağrılır ve her şey yolundaysa [] gelir —
            // koşulsuz loglamak "hata var" sanılan bir gürültü üretiyordu.
            // Boş dizi = temiz. Dolu dizi, modele geri beslenecek düzeltme
            // sinyalidir (bilinmeyen bileşen, eksik prop, çözülmemiş referans).
            onError={(errors) => {
              if (errors.length) console.warn("[genui] düzeltilebilir hatalar:", errors);
            }}
          />
        </CatalogProvider>
      </section>
    </main>
  );
}
