"use client";

// Dallı kök-neden analizi (Faz 4.10, 1 Ağustos 2026 — dış yol haritası 2.5+2.15).
//
// Kullanıcı senaryosu: bir metrik (ör. OEE) düşük/yüksek çıktığında NEDENİNİ bulmak için
// tıklaya tıklaya dallanıp GERÇEK verilerle (gerekirse ilişkili bir cube'a geçerek) en
// alttaki ham satırlara kadar inebilmek. Backend (POST /ask/drill) HER adımda GERÇEK bir
// sorgu çalıştırır (mock yok) — bu panel yalnız o adımların SONUÇLARINI (formül açıklaması,
// dallanma çipleri, ilişkili-cube çipleri, aykırı-kategori vurgusu, ham satırlar) gösterir
// ve breadcrumb ile geriye dönüşü yönetir. İleride bir agent'ın da AYNI /ask/drill
// sözleşmesini çağırması hedeflenir — bu yüzden burada YENİ bir iş mantığı YOK, yalnız
// backend'in zaten döndürdüğü yapıyı render eder.

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { drillAsk } from "@/lib/api-client";
import { ContractDetailPanel } from "@/components/ContractDetailPanel";
import type { CubeQuery, DrillResponse, QueryResult } from "@/lib/types";
import { useOdakTuzagi } from "@/lib/odakTuzagi";

interface Step {
  label: string;
  data: DrillResponse;
}

export function DrillDownPanel({
  cubeQuery,
  result,
  sessionId,
  onClose,
  initialFilter,
}: {
  cubeQuery: CubeQuery;
  result: QueryResult | null;
  sessionId?: string;
  onClose: () => void;
  // Doğrulama turu düzeltmesi (1 Ağustos 2026, P1-2) — grafikte TEK bir çubuğa/dilime
  // tıklanınca panel BOŞTAN (action:"explain") değil, DOĞRUDAN o kategoriye filtrelenmiş
  // (action:"select") açılsın diye. Ekstra bir effect/ikinci-adım GEREKMEZ — ilk sorgunun
  // KENDİSİ koşullu seçilir (aşağıdaki queryFn).
  initialFilter?: { dimension: string; value: string } | null;
}) {
  // İlk adım — useQuery ile getirilir (mevcut SchemaPanel/HelpPanel deseniyle TUTARLI).
  // `initialFilter` verilmişse İLK adımın KENDİSİ zaten "select" olur (explain+ayrı bir
  // select adımı ZİNCİRLEMEK yerine) — bu yüzden ek bir effect/ikinci-adım GEREKMEZ.
  // Sonraki adımlar (extraSteps) yalnız KULLANICI bir çipe TIKLADIĞINDA eklenir — hiçbir
  // setState bir effect İÇİNDEN çağrılmaz (React'ın "effect'te senkron setState" uyarısını
  // doğuran ara-state kopyalama YOK: `steps` dizisi render SIRASINDA initialQuery.data +
  // extraSteps'ten TÜRETİLİR, saklanmaz).
  const initialQuery = useQuery({
    queryKey: ["drill-explain", cubeQuery, result, initialFilter],
    queryFn: () =>
      initialFilter
        ? drillAsk({ cube_query: cubeQuery, session_id: sessionId, action: "select",
                    dimension: initialFilter.dimension, filter_value: initialFilter.value })
        : drillAsk({ cube_query: cubeQuery, result, session_id: sessionId, action: "explain" }),
  });

  const [extraSteps, setExtraSteps] = useState<Step[]>([]);
  const [cursor, setCursor] = useState<number | null>(null); // null = HER ZAMAN son adım
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rawRows, setRawRows] = useState<DrillResponse["raw_rows"] | null>(null);
  // UC-2.18/2.19 "kanıt paneli": bu adımı üreten GERÇEK SQL — kopyalanıp DB'de çalıştırılınca
  // ekrandaki AYNI sonucu vermeli (bkz. backend test_drill_steps_expose_running_sql_and_duration…).
  const [showSql, setShowSql] = useState(false);
  const [copied, setCopied] = useState(false);
  const [contractOpen, setContractOpen] = useState(false);

  // 🔴 FAZ 7.5 · A11Y-3/A11Y-6: Esc **ve** odak tuzağı artık `useOdakTuzagi`'nin —
  // burada elle yazılmış Esc dinleyicisi, aynı kuralın üç ayrı sahibinden biriydi ve
  // üçü de odağı hiç tutmuyordu.
  const kutuRef = useOdakTuzagi<HTMLDivElement>(true, onClose);

  const steps: Step[] = initialQuery.data
    ? [{
        label: initialFilter ? `${initialFilter.dimension}=${initialFilter.value}` : "Başlangıç",
        data: initialQuery.data,
      }, ...extraSteps]
    : [];
  const effectiveCursor = cursor === null ? steps.length - 1 : cursor;
  const current = effectiveCursor >= 0 ? steps[effectiveCursor] : null;

  const run = async (label: string, patch: Partial<Parameters<typeof drillAsk>[0]>) => {
    // Çifte-tıklama/yarış koruması: bir adım zaten çalışırken YENİ bir dal tetiklenirse,
    // ikisi de AYNI effectiveCursor'ı yakalayıp extraSteps'i TUTARSIZ güncelleyebilir
    // (ikisi de aynı slice noktasına yazar). Buton `disabled={loading}` ile zaten engellenir,
    // bu erken çıkış İKİNCİ bir güvenlik katmanı (ör. hızlı klavye/dokunmatik çifte-tetik).
    if (loading) return;
    setLoading(true);
    setError(null);
    setRawRows(null);
    try {
      const base = current?.data.cube_query ?? cubeQuery;
      const data = await drillAsk({
        cube_query: base,
        result: current ? current.data.result : result,
        session_id: sessionId,
        action: "explain",
        ...patch,
      });
      // effectiveCursor'a KADAR olan extraSteps korunur (breadcrumb'ta geriye dönüp YENİ
      // bir dal denerse eski dal atılır) — index -1 (Başlangıç) extraSteps'te hiç yok.
      setExtraSteps((prev) => [...prev.slice(0, effectiveCursor), { label, data }]);
      setCursor(effectiveCursor + 1);
    } catch {
      setError("Bu adım çalıştırılamadı. Lütfen tekrar dener misin?");
    } finally {
      setLoading(false);
    }
  };

  const copySql = async () => {
    if (!current?.data.sql) return;
    try {
      await navigator.clipboard.writeText(current.data.sql);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* pano erişimi olmayan bağlamda (http/eski tarayıcı) best-effort — buton yine de SQL'i gösterir */
    }
  };

  const showRaw = async () => {
    if (!current || loading) return;
    setLoading(true);
    setError(null);
    try {
      const data = await drillAsk({
        cube_query: current.data.cube_query, action: "raw", limit: 50, session_id: sessionId,
      });
      setRawRows(data.raw_rows);
    } catch {
      setError("Ham satırlar getirilemedi.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[1px]"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Kök nedeni incele"
    >
      <div
        ref={kutuRef}
        className="max-h-[85vh] w-[min(720px,92vw)] overflow-auto border border-hairline bg-background p-5 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-3 flex items-center justify-between">
          <h2 className="font-mono text-[13px] uppercase tracking-wide text-muted">
            Kök nedeni incele
          </h2>
          <button onClick={onClose} aria-label="Kapat" className="text-muted hover:text-foreground">
            ✕
          </button>
        </div>

        {/* Breadcrumb — istediği adıma geri dönebilir. */}
        {steps.length > 0 && (
          <div className="mb-3 flex flex-wrap items-center gap-1 font-mono text-[11px] text-muted">
            {steps.map((s, i) => (
              <span key={i} className="flex items-center gap-1">
                {i > 0 && <span>→</span>}
                <button
                  onClick={() => setCursor(i)}
                  className={i === effectiveCursor ? "text-accent" : "hover:text-foreground hover:underline"}
                >
                  {s.label}
                </button>
              </span>
            ))}
          </div>
        )}

        {initialQuery.isError && (
          <p className="mb-3 text-xs text-red-500">Bu rapor incelenemedi (bağlantı sorunu olabilir).</p>
        )}
        {error && <p className="mb-3 text-xs text-red-500">{error}</p>}
        {(loading || initialQuery.isLoading) && <p className="mb-3 text-xs text-muted">…</p>}

        {current && (
          <div className="space-y-4 text-sm">
            {current.data.note && (
              <p className="border-l-2 border-accent pl-2 text-xs text-accent">{current.data.note}</p>
            )}
            <p className="text-[13px] text-foreground">{current.data.formula_explanation}</p>

            {/* Kanıt: bu adımı üreten GERÇEK SQL — kopyalanıp DB'de çalıştırılınca ekrandaki
                AYNI sonucu verir (UC-2.18/2.19). `explain` sorgu ÇALIŞTIRMADIĞI için süre yok. */}
            {current.data.sql && (
              <div className="border-t border-hairline pt-2">
                <div className="flex items-center justify-between gap-2">
                  <button
                    onClick={() => setShowSql((s) => !s)}
                    className="font-mono text-[10px] uppercase tracking-wider text-neutral-400 transition-colors hover:text-foreground"
                  >
                    {showSql ? "— sql gizle" : "+ sql göster (kanıt)"}
                  </button>
                  {current.data.duration_ms != null && (
                    <span className="font-mono text-[10px] text-neutral-400">
                      {current.data.duration_ms} ms
                    </span>
                  )}
                </div>
                {showSql && (
                  <div className="mt-1.5">
                    <pre className="overflow-auto border border-hairline bg-neutral-950 p-3 font-mono text-[11px] leading-relaxed text-neutral-100">
                      {current.data.sql}
                    </pre>
                    <div className="mt-1 flex items-center gap-3">
                      <button
                        onClick={copySql}
                        className="font-mono text-[10px] text-muted underline hover:text-foreground"
                      >
                        {copied ? "✓ kopyalandı" : "sql'i kopyala"}
                      </button>
                      {/* Doğrulama turu düzeltmesi (P1-10): drill'in HER adımı kendi Query
                          Contract kaydını üretiyordu ama kimliği ekranda hiç gösterilmiyordu
                          (ReportPanel'de gösteriliyor, drill'de unutulmuştu). */}
                      {current.data.contract_id && (
                        <button
                          onClick={() => setContractOpen(true)}
                          className="font-mono text-[10px] text-neutral-400 underline-offset-2 hover:text-foreground hover:underline"
                          title="Query Contract — bu adımın kanıt kaydı (tıkla → incele)"
                        >
                          {current.data.contract_id}
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
            {contractOpen && current?.data.contract_id && (
              <ContractDetailPanel
                contractId={current.data.contract_id}
                onClose={() => setContractOpen(false)}
              />
            )}

            {current.data.result && current.data.result.rows.length > 0 && (
              <BreakdownTable
                result={current.data.result}
                anomalies={current.data.anomalies}
                dimension={(current.data.cube_query?.dimensions as string[] | undefined)?.slice(-1)[0]}
                disabled={loading}
                onPick={(dim, value) => run(`${dim}=${value}`, { action: "select", dimension: dim, filter_value: value })}
              />
            )}

            {current.data.available_dimensions.length > 0 && (
              <div>
                <p className="mb-1 font-mono text-[10px] uppercase tracking-wide text-muted">
                  buna göre kır
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {current.data.available_dimensions.map((d) => (
                    <button
                      key={d.name}
                      onClick={() => run(d.label, { action: "expand", dimension: d.name })}
                      disabled={loading}
                      className="border border-hairline px-2 py-1 text-xs transition-colors hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
                    >
                      {d.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {current.data.related_cubes.length > 0 && (
              <div>
                <p className="mb-1 font-mono text-[10px] uppercase tracking-wide text-muted">
                  ilişkili veri (kök neden adayı)
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {current.data.related_cubes.map((r) => (
                    <button
                      key={r.cube}
                      onClick={() => run(`↳ ${r.label}`, { action: "related", target_cube: r.cube })}
                      disabled={loading}
                      className="border border-dashed border-hairline px-2 py-1 text-xs transition-colors hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
                    >
                      {r.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="border-t border-hairline pt-3">
              <button
                onClick={showRaw}
                disabled={loading}
                className="text-xs text-muted underline transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
              >
                Ham satırları göster (bu dilimin gerçek kayıtları)
              </button>
              {rawRows && (
                <div className="mt-2 max-h-56 overflow-auto border border-hairline">
                  <table className="w-full text-left text-[11px]">
                    <thead>
                      <tr>
                        {rawRows.columns.map((c) => (
                          <th key={c} className="border-b border-hairline px-2 py-1 font-mono text-muted">
                            {c}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rawRows.rows.map((r, i) => (
                        <tr key={i} className="odd:bg-neutral-500/5">
                          {rawRows.columns.map((c) => (
                            <td key={c} className="px-2 py-1 font-mono">
                              {String(r[c] ?? "")}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <p className="px-2 py-1 text-[10px] text-muted">{rawRows.row_count} satır</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function BreakdownTable({
  result,
  anomalies,
  dimension,
  disabled,
  onPick,
}: {
  result: QueryResult;
  anomalies: DrillResponse["anomalies"];
  dimension?: string;
  disabled?: boolean;
  onPick: (dimension: string, value: string) => void;
}) {
  const anomalyByValue = new Map(anomalies.map((a) => [a.value, a]));
  const clickable = Boolean(dimension) && !disabled;
  return (
    <div className={`overflow-auto border border-hairline ${disabled ? "opacity-50" : ""}`}>
      <table className="w-full text-left text-[12px]">
        <thead>
          <tr>
            {result.columns.map((c) => (
              <th key={c} className="border-b border-hairline px-2 py-1 font-mono text-muted">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {result.rows.map((r, i) => {
            const dimValue = dimension ? String(r[dimension] ?? "") : null;
            const anomaly = dimValue ? anomalyByValue.get(dimValue) : undefined;
            const pick = () => clickable && dimValue && onPick(dimension!, dimValue);
            return (
              <tr
                key={i}
                onClick={pick}
                onKeyDown={(e) => {
                  if (clickable && (e.key === "Enter" || e.key === " ")) {
                    e.preventDefault();
                    pick();
                  }
                }}
                tabIndex={clickable ? 0 : undefined}
                role={clickable ? "button" : undefined}
                aria-label={clickable && dimValue ? `${dimension}: ${dimValue} — bu değere göre kır` : undefined}
                className={`${clickable ? "cursor-pointer hover:bg-accent/10 focus-visible:bg-accent/10 focus-visible:outline-none" : ""} ${
                  anomaly ? (anomaly.direction === "below" ? "bg-red-500/10" : "bg-green-500/10") : ""
                }`}
                title={anomaly ? `Ortalamadan ${anomaly.direction === "below" ? "düşük" : "yüksek"} (z=${anomaly.z_score})` : undefined}
              >
                {result.columns.map((c) => (
                  <td key={c} className="px-2 py-1 font-mono">
                    {String(r[c] ?? "")}
                    {c === dimension && anomaly && (
                      <span className="ml-1" aria-hidden>
                        {anomaly.direction === "below" ? "▼" : "▲"}
                      </span>
                    )}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
