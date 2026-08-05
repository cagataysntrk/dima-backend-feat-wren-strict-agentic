"use client";

/** FAZ 7.8 · **K1 — KATMANLI MAKBUZ.** [bayrak: `ui_kanit_gorunurlugu`]
 *
 * ## 🔴 D3 "zaten yapılmış" diye YANLIŞ KAPATILMIŞTI — ve ölçüm bunu doğruladı
 *
 * `grep -rn "<details\|<summary" src/` → **2** (ikisi de `ConnectionReviewPanel`'de,
 * makbuzla ilgisiz). Cevap kartında **sıfır**. Bugünkü hâl:
 *
 * | yüzey | yer | sorun |
 * |---|---|---|
 * | `?` toggle | `ReportCard` | **üç düz listeyi aynı görsel seviyede** açıyor |
 * | `+ sql göster` | ayrı toggle | aynı sorunun başka bir yarısı, başka bir yerde |
 * | `contract_id` | ayrı **modal** | üçüncü yer |
 * | `agent_run.steps[].receipt` | — | vardı, **okunuyordu ama kademesizdi** |
 *
 * → **Üç kopuk yüzey, sıfır kademe.** Kullanıcı *"bu sayı nereden geldi"* sorusunu
 * sormak için üç ayrı yere tıklamayı **öğrenmek** zorundaydı.
 *
 * ## Neden kademe — ve bu bir tercih değil, bir ölçüm
 *
 * > *"Daha uzun açıklamalar, **doğruluğu artırmadan** kullanıcı güvenini artırıyor."*
 * > — Steyvers ve ark., *Nature Machine Intelligence* 7:221-231 (2025)
 *
 * Yani **varsayılan olarak uzun ayrıntı göstermek, güveni yanlış yönde kalibre eder**.
 * Varsayılan **kısa**, ayrıntı **talep üzerine**.
 *
 * ## Üç katman
 *
 * | # | Ne | Kaynağı |
 * |---|---|---|
 * | 1 | **Tek satır**: *"deterministik küp · 2 adım · 34 ms"* + yol rozeti | `source` · `agent_run` |
 * | 2 | **Düz Türkçe "ne yaptım"**: hangi cube · hangi ölçü · hangi filtre · hangi dönem | `cube_query`'den **deterministik** |
 * | 3 | Tam iz + ajan adımları + **tıklanabilir makbuz** + SQL + `contract_id` | mevcut alanlar |
 *
 * 🔴 **Ayrıntı SİLİNMEZ, yalnız KATLANIR.** Bugün görünen hiçbir şey kaybolmuyor —
 * denetlenebilirlik bir kademelendirmeye feda edilemez.
 *
 * ⚠ **Katman 2 neden `cube_query`'den türetiliyor, backend'den istenmiyor:** o alan
 * cevabın **kendisiyle birlikte** geliyor ve tam olarak çalıştırılan sorgudur. Backend'e
 * ikinci bir *"bunu anlat"* ucu eklemek, aynı gerçeğin **iki sahibini** yaratırdı — ve
 * ikisi bir gün ayrışırdı. (Databricks Genie'nin *"Inspect"*i de join koşullarını ve
 * filtre değerlerini cevabın **içinde** gösteriyor, bir "SQL göster" toggle'ının altına
 * **gömmüyor**.)
 */

import type { AskResponse } from "@/lib/types";

/** Yol → düz Türkçe. ⚠ Bir **etikettir**, bir skor değil: `explain.confidence`
 *  kalibre edilmemiş bir yol etiketidir ve bu yüzden **sayı olarak gösterilmez**
 *  (MIMARI §9: *"kalibre edilmediği sürece o sayı bir güven değil bir SÜStür"*). */
const YOL_ADI: Record<string, string> = {
  cube: "deterministik küp",
  kpi: "deterministik KPI",
  "cube+llm": "küp + LLM alan seçimi",
  vqr: "doğrulanmış sorgu tekrarı",
  statement: "yapısal mali tablo",
  meta: "meta soru",
  catalog: "katalog sorusu",
  rule: "kural tabanlı yedek",
};

function yolAdi(source: string | null | undefined): string {
  if (!source) return "bilinmiyor";
  if (source.startsWith("llm:")) return `keşif (${source.slice(4)})`;
  return YOL_ADI[source] ?? source;
}

type Sozluk = Record<string, unknown>;

function dizi(v: unknown): string[] {
  return Array.isArray(v) ? v.filter((x): x is string => typeof x === "string") : [];
}

/** 🔴 **Katman 2 — deterministik anlatı.** `cube_query`'nin şekli
 *  (`cube` · `measures` · `dimensions` · `timeDimensions` · `filters`) doğrudan
 *  okunur; **hiçbir şey uydurulmaz**: bir alan yoksa o satır **hiç yazılmaz**.
 *
 *  ⚠ *"Filtre yok"* yazmak ile filtre satırını hiç yazmamak **aynı şey değildir**:
 *  ilki bir **iddiadır** ve `cube_query` şekli değişirse sessizce yanlış olur.
 */
export function neYaptim(cq: unknown): { etiket: string; deger: string }[] {
  if (!cq || typeof cq !== "object") return [];
  const q = cq as Sozluk;
  const satirlar: { etiket: string; deger: string }[] = [];

  if (typeof q.cube === "string") satirlar.push({ etiket: "veri kümesi", deger: q.cube });

  const olculer = dizi(q.measures);
  const harman = Array.isArray(q.blend)
    ? (q.blend as Sozluk[]).flatMap((b) => dizi(b?.measures))
    : [];
  const tumOlculer = [...olculer, ...harman];
  if (tumOlculer.length) {
    satirlar.push({ etiket: "ölçü", deger: tumOlculer.join(" · ") });
  }

  const boyutlar = dizi(q.dimensions);
  if (boyutlar.length) satirlar.push({ etiket: "kırılım", deger: boyutlar.join(" · ") });

  const td = Array.isArray(q.timeDimensions) ? (q.timeDimensions[0] as Sozluk) : null;
  if (td && typeof td.dimension === "string") {
    const gran = typeof td.granularity === "string" ? td.granularity : null;
    satirlar.push({
      etiket: "dönem",
      deger: gran ? `${td.dimension} · ${gran}` : String(td.dimension),
    });
  }

  const filtreler = Array.isArray(q.filters) ? (q.filters as Sozluk[]) : [];
  if (filtreler.length) {
    satirlar.push({
      etiket: "filtre",
      // Değerler **gösterilir**, gizlenmez: bir filtrenin varlığını bilip değerini
      // bilmemek, sayıyı açıklamaz. (Maskeleme sunucuda `pii.py`'nin işidir.)
      deger: filtreler
        .map((f) => {
          const alan = typeof f?.member === "string" ? f.member
            : typeof f?.dimension === "string" ? f.dimension : "?";
          const op = typeof f?.operator === "string" ? f.operator : "=";
          const deg = dizi(f?.values).join(", ");
          return deg ? `${alan} ${op} ${deg}` : `${alan} ${op}`;
        })
        .join(" · "),
    });
  }

  if (typeof q.limit === "number") satirlar.push({ etiket: "satır sınırı", deger: String(q.limit) });

  return satirlar;
}

export function Makbuz({
  item,
  sqlAcik,
  onContract,
}: {
  item: AskResponse;
  /** SQL yalnız `sql_gorunurlugu` kademesi açıkken katman 3'e girer — bir bayrağın
   *  kararı burada **tekrar** verilmez, çağırandan gelir. */
  sqlAcik: boolean;
  onContract?: () => void;
}) {
  const adimlar = item.agent_run?.step_count ?? item.trace?.length ?? 0;
  const ms = item.agent_run?.steps.reduce((t, s) => t + (s.ms ?? 0), 0) ?? 0;
  const anlati = neYaptim(item.cube_query);

  // Hiçbir kanıt yoksa makbuz da yoktur — boş bir kabuk, güven vaat edip bilgi vermez.
  if (!anlati.length && !item.trace?.length && !item.agent_run) return null;

  return (
    <details className="mt-3 border border-hairline bg-neutral-500/[0.03]" data-makbuz>
      {/* 🔴 KATMAN 1 — TEK SATIR. Varsayılan görünüm budur ve **kısa olması bir
          karardır** (Steyvers 2025): uzun açıklama, doğruluğu artırmadan güveni artırır. */}
      <summary className="cursor-pointer px-3 py-1.5 font-mono text-[11px] text-neutral-500 marker:text-neutral-400">
        <span className="text-foreground">{yolAdi(item.source)}</span>
        {adimlar > 0 && <span> · {adimlar} adım</span>}
        {ms > 0 && <span> · {ms} ms</span>}
        {/* 🔴 **Kanıt sınıfı İKİ YÖNDE de yazılır** — ve bu bir kapının düzeltmesi:
            katmanlı makbuza geçerken yalnız *"olasılıksal"* uyarısı korunmuş, *"ölçülmüş"*
            hâli düşürülmüştü. `test_ai_act_uyumu` yakaladı.

            ⚠ Yokluğu bir bilgi **değildir**: kullanıcı *"ölçülmüş"* ile *"bu alan hiç
            gelmemiş"* arasındaki farkı **göremezdi** — ve AI Act'in istediği tam olarak
            o ayrımdır. ⚠ İki hâl aynı vurguyu taşımaz: uyarı amber, ölçülmüş soluk —
            *bir güvenceyi bir uyarı kadar bağırtmak, uyarıyı sıradanlaştırır.* */}
        {item.kanit_sinifi === "probabilistik" ? (
          <span
            className="ml-1.5 text-amber-600"
            title="Bu cevabın üretiminde olasılıksal bir adım var (SQL yazımı ya da alan/ölçü SEÇİMİ). Sayı doğru hesaplanmış olsa bile SORUNUN karşılığı olmayabilir."
          >
            ⚠ olasılıksal
          </span>
        ) : item.kanit_sinifi === "olculmus" ? (
          <span
            className="ml-1.5 opacity-[var(--opacity-soluk)]"
            title="Cevap uçtan uca deterministik yoldan üretildi — aynı soru aynı sonucu verir."
          >
            ölçülmüş
          </span>
        ) : null}
      </summary>

      <div className="border-t border-hairline px-3 py-2">
        {/* KATMAN 2 — DÜZ TÜRKÇE "NE YAPTIM". */}
        {anlati.length > 0 && (
          <dl className="space-y-0.5">
            {anlati.map((s) => (
              <div key={s.etiket} className="flex gap-2 font-mono text-[11px]">
                <dt className="w-[5.5rem] shrink-0 text-neutral-400">{s.etiket}</dt>
                <dd className="min-w-0 break-words text-foreground">{s.deger}</dd>
              </div>
            ))}
          </dl>
        )}
        {item.calculation_explanation && (
          <p className="mt-1.5 font-mono text-[11px] leading-snug text-neutral-500">
            {item.calculation_explanation}
          </p>
        )}

        {/* 🔴 KATMAN 3 — TAM İZ. **Hiçbir şey silinmedi**, yalnız bir kademe altına
            katlandı: denetlenebilirlik bir kademelendirmeye feda edilemez. */}
        <details className="mt-2 border-t border-hairline pt-2" data-makbuz-tam>
          <summary className="cursor-pointer font-mono text-[10px] uppercase tracking-wider text-neutral-400">
            tam iz
          </summary>
          <div className="mt-1.5 space-y-2">
            {item.explain?.path && (
              <div className="font-mono text-[11px] text-neutral-500">
                <span className="mr-1 text-neutral-400">yol:</span>
                <span className="text-foreground">{item.explain.path}</span>
              </div>
            )}
            {item.trace && item.trace.length > 0 && (
              <ol className="space-y-0.5">
                {item.trace.map((t, i) => (
                  <li key={i} className="font-mono text-[11px] text-neutral-500">
                    <span className="mr-1 text-accent">{String(i + 1).padStart(2, "0")}</span>
                    {t}
                  </li>
                ))}
              </ol>
            )}
            {/* Ajan adımları — **reddedilenler dâhil**. Sessizce kaybolan bir adım,
                yapılmamış bir adım gibi okunur ve koşumun maliyeti anlaşılmaz olur. */}
            {item.agent_run && item.agent_run.steps.length > 0 && (
              <div className="border-t border-hairline pt-1.5">
                <div className="mb-1 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
                  ajan adımları · {item.agent_run.step_count} adım ·{" "}
                  {item.agent_run.query_count} sorgu
                  {item.agent_run.truncated && (
                    <span className="ml-1 text-amber-600" title={item.agent_run.truncation_reason ?? "bütçe tavanı aşıldı"}>
                      ⚠ kısıldı
                    </span>
                  )}
                </div>
                <ul className="space-y-0.5">
                  {item.agent_run.steps.map((s, i) => (
                    <li key={i} className="font-mono text-[11px] text-neutral-500">
                      <span className="mr-1 text-neutral-400">{s.tool}</span>
                      <span className="text-neutral-400">· {s.determinism} · {s.ms} ms</span>
                      {s.error && <span className="ml-1 text-amber-600">· {s.error}</span>}
                      {s.gated === false && (
                        <span className="ml-1 text-neutral-400" title="Bileşik adım — ayrı bir yetki kaydı yok">
                          · kayıtsız
                        </span>
                      )}
                      {/* ⚠ FAZ 0.8'in yetim alanı: `receipt` **tıklanabilir** olmalı,
                          yoksa bir kimlik dizgisi olarak kalır ve kimse açamaz. */}
                      {s.receipt && (
                        <a
                          href={`/contracts/${s.receipt}`}
                          className="ml-1 text-neutral-400 underline-offset-2 hover:text-accent hover:underline"
                          title="Bu adımın kanıt kaydı"
                        >
                          · makbuz
                        </a>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {sqlAcik && item.sql && (
              <pre className="overflow-auto border border-hairline bg-neutral-950 p-3 font-mono text-[11px] leading-relaxed text-neutral-100">
                {item.sql}
              </pre>
            )}
            {sqlAcik && item.planned_sql && item.planned_sql !== item.sql && (
              <div>
                <p className="mb-1 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
                  plan (öz iyileştirme öncesi derlenen SQL)
                </p>
                <pre className="overflow-auto border border-hairline bg-neutral-950 p-3 font-mono text-[11px] leading-relaxed text-neutral-400">
                  {item.planned_sql}
                </pre>
              </div>
            )}
            {item.contract_id && onContract && (
              <button
                onClick={onContract}
                className="font-mono text-[10px] tracking-wider text-neutral-400 underline-offset-2 transition-colors hover:text-foreground hover:underline"
                title="Query Contract — bu raporun kanıt kaydı: soru + sorgu + sonuç özeti mühürlendi; sonradan yeniden oynatılıp doğrulanabilir"
              >
                {item.contract_id}
              </button>
            )}
          </div>
        </details>
      </div>
    </details>
  );
}

/** 🔴 **KURAL B — bayrak KAPALIYKEN eski davranış.** `ui_kanit_gorunurlugu=off` iken
 *  `ReportCard` bunu render eder: yol · kanıt sınıfı · trace · ajan adımları **aynı
 *  görsel seviyede**, `?` toggle'ıyla açılan **düz** bir blok — yani 7.8 öncesi hâl.
 *
 *  ⚠ Bu kod **bilerek** iyileştirilmedi. *Bir geri-alma yolunun değeri, geri
 *  aldığı şeyin birebir aynısını vermesindedir*; "biraz daha iyi" bir eski hâl, geri
 *  almayı bir **üçüncü** davranışa çevirir ve kıyas ölçülemez olur.
 */
export function MakbuzDuz({ item }: { item: AskResponse }) {
  if (!item.trace) return null;
  return (
    <div className="mt-3 border border-hairline bg-neutral-500/[0.03] p-3">
      <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
        nasıl çözüldü
      </div>
      {item.explain?.path && (
        <div className="mb-2 font-mono text-[11px] text-neutral-500">
          <span className="mr-1 text-neutral-400">yol:</span>
          <span className="text-foreground">{item.explain.path}</span>
        </div>
      )}
      {item.kanit_sinifi && (
        <div className="mb-2 font-mono text-[11px] text-neutral-500">
          <span className="mr-1 text-neutral-400">kanıt sınıfı:</span>
          <span
            className={item.kanit_sinifi === "probabilistik" ? "text-amber-600" : "text-foreground"}
            title={
              item.kanit_sinifi === "probabilistik"
                ? "Bu cevabın üretiminde olasılıksal bir adım var (SQL yazımı ya da alan/ölçü SEÇİMİ). Sayı doğru hesaplanmış olsa bile SORUNUN karşılığı olmayabilir."
                : "Cevap uçtan uca deterministik yoldan üretildi — aynı soru aynı sonucu verir."
            }
          >
            {item.kanit_sinifi === "probabilistik" ? "olasılıksal" : "ölçülmüş"}
          </span>
        </div>
      )}
      <ol className="space-y-0.5">
        {item.trace.map((t, i) => (
          <li key={i} className="font-mono text-[11px] text-neutral-500">
            <span className="mr-1 text-accent">{String(i + 1).padStart(2, "0")}</span>
            {t}
          </li>
        ))}
      </ol>
      {item.agent_run && item.agent_run.steps.length > 0 && (
        <div className="mt-2 border-t border-hairline pt-2">
          <div className="mb-1 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
            ajan adımları · {item.agent_run.step_count} adım · {item.agent_run.query_count} sorgu
          </div>
          <ul className="space-y-0.5">
            {item.agent_run.steps.map((s, i) => (
              <li key={i} className="font-mono text-[11px] text-neutral-500">
                <span className="mr-1 text-neutral-400">{s.tool}</span>
                <span className="text-neutral-400">· {s.determinism} · {s.ms} ms</span>
                {s.error && <span className="ml-1 text-amber-600">· {s.error}</span>}
                {s.receipt && (
                  <a
                    href={`/contracts/${s.receipt}`}
                    className="ml-1 text-neutral-400 underline-offset-2 hover:text-accent hover:underline"
                  >
                    · makbuz
                  </a>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
