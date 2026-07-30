"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useClickOutside } from "@/lib/useClickOutside";
import type { AskResponse, CubeQuery, DashboardListItem } from "@/lib/types";
import {
  addDashboardWidget,
  createDashboard,
  createSchedule,
  getFeatures,
  getMe,
  listDashboards,
  verifyReport,
} from "@/lib/api-client";
import { BrandMark } from "@/components/BrandMark";
import { InterpretationBar } from "@/components/InterpretationBar";
import { ResultView } from "@/components/ResultView";
import { KpiCardView } from "@/components/KpiCard";
import { OutputInsight } from "@/components/OutputInsight";
import { SourceBadge } from "@/components/ChatPanel";


// Özellik bayrakları (ADR-0009) — açılışta bir kez okunur, modül düzeyinde tutulur.
let _features: Record<string, string> | null = null;
function useFeature(name: string): string | null {
  const [stage, setStage] = useState<string | null>(_features?.[name] ?? null);
  useEffect(() => {
    if (_features) return;
    getFeatures()
      .then((f) => {
        _features = f;
        setStage(f[name] ?? null);
      })
      .catch(() => {});
  }, [name]);
  return stage;
}

// İzinler (/auth/me permissions) — kaynak backend authorize matrisi; rol semantiği
// UI'a KOPYALANMAZ, rol açmak yalnız backend değişikliğidir. Liste yüklenene kadar
// izinli varsayılır (regresyon olmasın); backend her eylemi kendi tarafında da zorlar.
let _perms: string[] | null = null;
function usePermission(action: string): boolean {
  const [ok, setOk] = useState<boolean>(_perms ? _perms.includes(action) : true);
  useEffect(() => {
    if (_perms) return;
    getMe()
      .then((me) => {
        _perms = me.permissions ?? [];
        setOk(_perms.includes(action));
      })
      .catch(() => {});
  }, [action]);
  return ok;
}

// Sağ bölme: seçili raporun canlı görünümü (keskin, mono readout).
export function ReportPanel({
  data,
  pending,
  viewHint,
  onCubeEdit,
  error,
  verifyLabel,
  sessionId,
}: {
  data: AskResponse | null;
  pending: boolean;
  // "grafik ver" tarzı görünüm isteği — ResultView remount edilip başlangıç görünümü olur.
  viewHint?: { kind: string; nonce: number } | null;
  // Yorum çubuğu chip düzenlemeleri (deterministik /cube).
  onCubeEdit?: (edit: { cq: CubeQuery; label: string }) => void;
  error: string | null;
  // Raporu üreten son GERÇEK soru (chip etiketi değil) — verify bu metinle öğrenir.
  verifyLabel?: string | null;
  sessionId?: string;
}) {
  const [showSql, setShowSql] = useState(false);
  const [showTrace, setShowTrace] = useState(false);
  // SQL gösterimi (sql_display bayrağı) — ham şeffaflık özelliği; kapalıysa buton yok.
  const sqlStage = useFeature("sql_display");
  // Panoya ekle (dashboards bayrağı, §9) — bu raporun cube_query'si widget olur.
  const dashStage = useFeature("dashboards");
  const [dashOpen, setDashOpen] = useState(false);
  const [dashList, setDashList] = useState<DashboardListItem[]>([]);
  const [addedTo, setAddedTo] = useState<string | null>(null);
  // Kullanıcının bu raporda seçtiği CANLI görünüm (tip/görünüm/ölçü) — "panoya ekle" bunu gönderir
  // ki pano BİRE BİR aynı grafiği göstersin. Ref (re-render yok): rapora göre anahtarlanır (sql),
  // başka rapordan kalan seçim sızmasın. Tıklama anında okunur.
  const liveViewRef = useRef<{ sql: string; hint: string } | null>(null);
  const onLiveView = (hint: string) => {
    liveViewRef.current = { sql: data?.sql ?? "", hint };
  };
  const openDashMenu = () => {
    if (!dashOpen) listDashboards().then((r) => setDashList(r.dashboards)).catch(() => {});
    setSchedOpen(false); setWrongOpen(false);  // tek-açık
    setDashOpen((o) => !o);
  };
  const addToDash = async (dashId: string) => {
    if (!data?.cube_query) return;
    try {
      const lv = liveViewRef.current;
      const liveHint = lv && lv.sql === (data.sql ?? "") ? lv.hint : null;
      await addDashboardWidget(dashId, {
        title: data.question,
        cube_query: data.cube_query, // compare (YoY) dahil — backend add_widget korur
        // Kullanıcının seçtiği canlı görünüm (tip/ölçü) öncelikli; yoksa /ask'ın ipucu.
        view_hint: liveHint ?? data.view_hint ?? null,
      });
      setAddedTo(dashId);
      setDashOpen(false);
    } catch {
      /* best-effort */
    }
  };
  const createAndAdd = async () => {
    const title = window.prompt("Yeni pano adı:", "Panom");
    if (!title) return;
    try {
      const d = await createDashboard(title);
      await addToDash(d.id);
    } catch {
      /* best-effort */
    }
  };
  // 🔔 zamanla (ADR-0011, beta bayrağı): raporun CubeQuery'si göreli dönemle zamanlanır.
  const schedStage = useFeature("scheduled_reports");
  const canSchedule = usePermission("schedule:create");
  const canVerify = usePermission("vqr:write");
  const [schedOpen, setSchedOpen] = useState(false);
  const [scheduled, setScheduled] = useState<string | null>(null);
  // #56 alarm + e-posta: preset periyodu + opsiyonel eşik/anomali alarmı + alıcı e-postalar.
  const measures = ((data?.cube_query?.measures as string[] | undefined) ?? []);
  const [alarmType, setAlarmType] = useState<"none" | "threshold" | "anomaly">("none");
  const [alarmMeasure, setAlarmMeasure] = useState<string>("");
  const [alarmOp, setAlarmOp] = useState<"gt" | "lt">("gt");
  const [alarmValue, setAlarmValue] = useState<string>("");
  const [emails, setEmails] = useState<string>("");
  const schedule = (preset: { every: "hour" | "day" | "week"; at?: string; weekday?: number; period: string; name: string }) => {
    if (!data?.cube_query) return;
    const cq = { ...data.cube_query,
      filters: ((data.cube_query.filters as { dimension: string }[] | undefined) ?? [])
        .filter((f) => f.dimension !== "tarih") };
    if (!(cq.filters as unknown[]).length) delete (cq as Record<string, unknown>).filters;
    const measure = alarmMeasure || measures[0] || "";
    const threshold =
      alarmType === "threshold" && measure && alarmValue !== ""
        ? { measure, op: alarmOp, value: Number(alarmValue) }
        : alarmType === "anomaly" && measure
          ? { measure, method: "zscore" as const }
          : null;
    const to = emails.split(",").map((e) => e.trim()).filter((e) => e.includes("@"));
    createSchedule({ label: vLabel ?? data.question, cube_query: cq,
      period: preset.period, every: preset.every, at: preset.at, weekday: preset.weekday,
      threshold, delivery: to.length ? { email: { to } } : null })
      .then(() => { setScheduled(verifyKey); setSchedOpen(false); })
      .catch(() => {});
  };

  // "✓ doğru" / "✗ yanlış" (beta bayrağı): geri bildirim — doğrulama geri ALINABİLİR.
  // Durum RAPOR BAŞINA haritada tutulur: oturumda birden çok rapora verilen ✓/✗
  // işaretleri, raporlar arasında gezerken korunur (tek anahtar son işareti eziyordu).
  const verifyStage = useFeature("verify_button");
  const [fb, setFb] = useState<Record<string, "ok" | "bad">>({});
  const vLabel =
    data && data.question.startsWith("chip:") ? (verifyLabel ?? data.question) : data?.question;
  const verifyKey = data?.cube_query && vLabel ? `${vLabel}::${data.sql ?? ""}` : null;
  const verified = verifyKey != null && fb[verifyKey] === "ok";
  const flagged = verifyKey != null && fb[verifyKey] === "bad";
  // ✗ yanlış → yorum popup'ı: kullanıcı isterse "neden yanlış"ı yazar, isterse yazmadan
  // yollar. Yorum backend'de note'a düşer → log madencisini (#57) besler.
  const [wrongOpen, setWrongOpen] = useState(false);
  const [wrongComment, setWrongComment] = useState("");
  // Rapor aksiyon menüleri (zamanla / panoya ekle / yanlış) TEK-AÇIK + dışarı-tıklamada kapanır.
  const closeMenus = () => { setDashOpen(false); setSchedOpen(false); setWrongOpen(false); };
  const actionsRef = useClickOutside<HTMLDivElement>(dashOpen || schedOpen || wrongOpen, closeMenus);
  const submitWrong = () => {
    if (!data?.cube_query || !vLabel || !verifyKey) return;
    verifyReport(data.cube_query, vLabel, {
      verdict: "wrong", session_id: sessionId, comment: wrongComment.trim() || undefined,
    })
      .then(() => { setFb((m) => ({ ...m, [verifyKey]: "bad" })); setWrongOpen(false); setWrongComment(""); })
      .catch(() => {});
  };

  if (error) {
    return (
      <Center>
        <div className="max-w-sm border border-red-300 bg-red-50 px-4 py-3 font-mono text-[13px] text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
          {error}
        </div>
      </Center>
    );
  }

  if (pending && !data) {
    return (
      <Center>
        <div className="flex items-center gap-2 font-mono text-[13px] text-neutral-400">
          <span className="dima-caret" style={{ height: "0.9em" }} />
          yürütülüyor…
        </div>
      </Center>
    );
  }

  if (!data) {
    return (
      <Center>
        <div className="max-w-xs text-center font-mono text-[13px] text-neutral-400">
          <span className="dima-caret" style={{ height: "0.9em" }} /> soldan sor — rapor burada belirir
        </div>
      </Center>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-8 py-7">
      <div className="mb-5 border-b border-hairline pb-4">
        <div className="flex items-start justify-between gap-3">
          <h2 className="font-mono text-[15px] leading-snug text-foreground">{data.question}</h2>
          <div ref={actionsRef} className="flex shrink-0 items-center gap-1.5 pt-0.5">
            {schedStage && canSchedule && data.cube_query && data.source && (
              <span className="relative">
                <button
                  onClick={() => { setDashOpen(false); setWrongOpen(false); setSchedOpen((o) => !o); }}
                  title="Bu raporu zamanla — belirlenen aralıkla otomatik koşar, bildirim üretir"
                  className={`flex h-[20px] items-center border px-1.5 font-mono text-[11px] transition-colors ${
                    scheduled === verifyKey
                      ? "border-accent/40 text-accent"
                      : "border-hairline text-neutral-400 hover:text-foreground"
                  }`}
                >
                  {scheduled === verifyKey ? "🔔 zamanlandı" : "🔔 zamanla"}
                </button>
                {schedOpen && (
                  <span className="absolute right-0 top-full z-30 mt-1 flex w-64 flex-col gap-2 border border-hairline bg-background p-2 shadow-lg">
                    {/* #56 alarm (opsiyonel) — eşik / anomali; ölçü rapor ölçülerinden. */}
                    <div className="flex flex-col gap-1">
                      <span className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
                        alarm (opsiyonel)
                      </span>
                      <div className="flex gap-1 font-mono text-[11px]">
                        {(["none", "threshold", "anomaly"] as const).map((t) => (
                          <button
                            key={t}
                            onClick={() => setAlarmType(t)}
                            className={`border px-1.5 py-0.5 transition-colors ${
                              alarmType === t
                                ? "border-accent/40 text-accent"
                                : "border-hairline text-neutral-400 hover:text-foreground"
                            }`}
                          >
                            {t === "none" ? "yok" : t === "threshold" ? "eşik" : "anomali"}
                          </button>
                        ))}
                      </div>
                      {alarmType !== "none" && (
                        <div className="flex items-center gap-1 font-mono text-[11px]">
                          <select
                            value={alarmMeasure || measures[0] || ""}
                            onChange={(e) => setAlarmMeasure(e.target.value)}
                            className="min-w-0 flex-1 border border-hairline bg-background px-1 py-0.5"
                          >
                            {measures.map((m) => (
                              <option key={m} value={m}>{m}</option>
                            ))}
                          </select>
                          {alarmType === "threshold" ? (
                            <>
                              <select
                                value={alarmOp}
                                onChange={(e) => setAlarmOp(e.target.value as "gt" | "lt")}
                                className="border border-hairline bg-background px-1 py-0.5"
                              >
                                <option value="gt">&gt;</option>
                                <option value="lt">&lt;</option>
                              </select>
                              <input
                                value={alarmValue}
                                onChange={(e) => setAlarmValue(e.target.value)}
                                inputMode="decimal"
                                placeholder="değer"
                                className="w-16 border border-hairline bg-background px-1 py-0.5"
                              />
                            </>
                          ) : (
                            <span className="text-neutral-400">z-skoru (olağandışı)</span>
                          )}
                        </div>
                      )}
                    </div>
                    {/* #56 e-posta teslim (opsiyonel) — in-app bell her zaman düşer. */}
                    <input
                      value={emails}
                      onChange={(e) => setEmails(e.target.value)}
                      placeholder="e-posta (virgülle, opsiyonel)"
                      className="border border-hairline bg-background px-1.5 py-1 font-mono text-[11px]"
                    />
                    {/* Periyot preset'i — tıklama mevcut alarm+e-posta ile zamanlar. */}
                    <div className="flex flex-col border-t border-hairline pt-1">
                      {[
                        { name: "her sabah 08:00 · dünün verisi", every: "day" as const, at: "08:00", period: "dün" },
                        { name: "her saat · bugünün verisi", every: "hour" as const, period: "bugün" },
                        { name: "her pazartesi 08:00 · geçen hafta", every: "week" as const, at: "08:00", weekday: 1, period: "geçen hafta" },
                      ].map((pr) => (
                        <button
                          key={pr.name}
                          onClick={() => schedule(pr)}
                          className="px-2 py-1.5 text-left font-mono text-[11px] text-neutral-500 hover:bg-neutral-500/[0.06] hover:text-foreground"
                        >
                          {pr.name}
                        </button>
                      ))}
                    </div>
                  </span>
                )}
              </span>
            )}
            {dashStage && data.cube_query && data.source && (
              <span className="relative">
                <button
                  onClick={openDashMenu}
                  title="Bu grafiği/tabloyu bir panoya ekle — panoda canlı izlenir"
                  className={`flex h-[20px] items-center border px-1.5 font-mono text-[11px] transition-colors ${
                    addedTo
                      ? "border-accent/40 text-accent"
                      : "border-hairline text-neutral-400 hover:text-foreground"
                  }`}
                >
                  {addedTo ? "✓ panoda" : "+ panoya ekle"}
                </button>
                {dashOpen && (
                  <span className="absolute right-0 top-full z-30 mt-1 flex w-56 flex-col border border-hairline bg-background shadow-lg">
                    {dashList.length === 0 && (
                      <span className="px-2 py-1.5 font-mono text-[11px] text-neutral-400">
                        henüz pano yok
                      </span>
                    )}
                    {dashList.map((d) => (
                      <button
                        key={d.id}
                        onClick={() => addToDash(d.id)}
                        className="px-2 py-1.5 text-left font-mono text-[11px] text-neutral-500 hover:bg-neutral-500/[0.06] hover:text-foreground"
                      >
                        {d.title} · {d.widget_count} widget
                      </button>
                    ))}
                    <button
                      onClick={createAndAdd}
                      className="border-t border-hairline px-2 py-1.5 text-left font-mono text-[11px] text-accent hover:bg-neutral-500/[0.06]"
                    >
                      + yeni pano
                    </button>
                  </span>
                )}
              </span>
            )}
            {verifyStage && canVerify && data.cube_query && data.source && (
              // tek kutu: ✓/✗ geri bildirim (aşama rozeti gösterilmez — bayrak iç bilgi)
              <div className="relative inline-flex h-[20px] items-stretch border border-hairline font-mono text-[11px]">
                <button
                  onClick={() => {
                    if (!data.cube_query || !vLabel || !verifyKey) return;
                    // ikinci tık = GERİ AL (yanlışlıkla doğrulamayı düzeltme yolu)
                    verifyReport(data.cube_query, vLabel, {
                      undo: verified || undefined,
                      session_id: sessionId,
                    })
                      .then(() =>
                        setFb((m) => {
                          const n = { ...m };
                          if (verified) delete n[verifyKey];
                          else n[verifyKey] = "ok";
                          return n;
                        }),
                      )
                      .catch(() => {});
                  }}
                  title={
                    verified
                      ? "Doğrulamayı geri al"
                      : "Bu raporu doğru olarak işaretle — aynı soru bundan sonra LLM'siz cevaplanır"
                  }
                  className={`px-1.5 transition-colors ${
                    verified ? "text-emerald-500" : "text-neutral-400 hover:text-foreground"
                  }`}
                >
                  {verified ? "✓ öğrenildi" : "✓ doğru"}
                </button>
                <button
                  onClick={() => { if (!flagged && verifyKey) { setDashOpen(false); setSchedOpen(false); setWrongOpen((o) => !o); } }}
                  title="Bu rapor yanlış — isteğe bağlı yorum ekleyip kaydet"
                  className={`border-l border-hairline px-1.5 transition-colors ${
                    flagged ? "text-red-500" : "text-neutral-400 hover:text-foreground"
                  }`}
                >
                  {flagged ? "✗ kaydedildi" : "✗ yanlış"}
                </button>
                {/* #62 — ✗ yorum popup'ı: neden yanlış (opsiyonel) → note → #57 madenci. */}
                {wrongOpen && !flagged && (
                  <span className="absolute right-0 top-full z-30 mt-1 flex w-64 flex-col gap-2 border border-hairline bg-background p-2 text-left shadow-lg">
                    <span className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
                      neden yanlış? (opsiyonel)
                    </span>
                    <textarea
                      value={wrongComment}
                      onChange={(e) => setWrongComment(e.target.value)}
                      rows={3}
                      placeholder="ör. yanlış ölçü / eksik kırılım / dönem hatalı…"
                      className="resize-none border border-hairline bg-background px-1.5 py-1 font-mono text-[11px]"
                    />
                    <div className="flex gap-1">
                      <button
                        onClick={submitWrong}
                        className="flex-1 border border-red-500/40 px-2 py-1 font-mono text-[11px] text-red-500 transition-colors hover:bg-red-500/[0.06]"
                      >
                        {wrongComment.trim() ? "yorumla gönder" : "yorumsuz gönder"}
                      </button>
                      <button
                        onClick={() => { setWrongOpen(false); setWrongComment(""); }}
                        className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground"
                      >
                        vazgeç
                      </button>
                    </div>
                  </span>
                )}
              </div>
            )}
            <SourceBadge source={data.source} />
            {data.trace && data.trace.length > 0 && (
              <button
                onClick={() => setShowTrace((s) => !s)}
                title="Bu sorgu nasıl çözüldü?"
                aria-label="Trace"
                className={`flex h-[20px] w-[20px] items-center justify-center border font-mono text-[11px] transition-colors ${
                  showTrace ? "border-accent/40 text-accent" : "border-hairline text-neutral-400 hover:text-foreground"
                }`}
              >
                ?
              </button>
            )}
          </div>
        </div>
        {showTrace && data.trace && (
          <div className="mt-3 border border-hairline bg-neutral-500/[0.03] p-3">
            <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
              nasıl çözüldü
            </div>
            <ol className="space-y-0.5">
              {data.trace.map((t, i) => (
                <li key={i} className="font-mono text-[11px] text-neutral-500">
                  <span className="mr-1 text-accent">{String(i + 1).padStart(2, "0")}</span>
                  {t}
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>

      {data.cube_query && onCubeEdit &&
        ((data.cube_query as { measures?: unknown[] }).measures?.length ?? 0) > 0 && (
        <InterpretationBar cq={data.cube_query} onEdit={onCubeEdit} />
      )}

      {/* Cross-cube KPI kartı (CCC / likidite) — cube tablosu değil bileşke skaler. */}
      {data.kpi && <KpiCardView card={data.kpi} />}



      {data.result && (
        <div className="border border-hairline bg-background p-4">
          <ResultView
            key={`${data.question}·${data.sql}·${viewHint?.nonce ?? 0}`}
            result={data.result}
            viewHint={viewHint?.kind}
            viz={data.viz}
            onViewChange={onLiveView}
          />
        </div>
      )}

      {/* Evrensel çıktı yorumu (feature flag'li) — KPI/tablo/grafik altında. */}
      <OutputInsight interpretation={data.interpretation} />

      {/* K4 öneriler — K3 sinyalinden 'neye bakmalısın' + opsiyonel tıklanır drill. */}
      {onCubeEdit && (data.recommendations?.length ?? 0) > 0 && (
        <div className="mt-3 space-y-1.5">
          {data.recommendations!.map((rec, i) => (
            <div
              key={i}
              className="flex items-center justify-between gap-2 border border-hairline bg-accent/[0.04] px-3 py-2"
            >
              <p className="text-[12px] leading-relaxed text-neutral-600 dark:text-neutral-300">
                <span className="mr-1 text-accent" aria-hidden>
                  →
                </span>
                {rec.text}
              </p>
              {rec.action && (
                <button
                  onClick={() => onCubeEdit({ cq: rec.action!.cube_query, label: rec.action!.label })}
                  title="Deterministik koşar — LLM yok"
                  className="shrink-0 border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-500 transition-colors hover:border-foreground/30 hover:text-foreground"
                >
                  {rec.action.label}
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* K2 sonraki adım chip'leri (backend 'next_steps' flag'iyle gelir) — kırılım/ölçek/
          zaman. Tıklama mevcut deterministik /cube yolunu kullanır (LLM yok). */}
      {onCubeEdit && (data.next_steps?.length ?? 0) > 0 && (
        <div className="mt-3">
          <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
            sonraki adım
          </div>
          <div className="flex flex-wrap gap-1.5">
            {data.next_steps!.map((step, i) => (
              <button
                key={`${step.kind}-${i}`}
                onClick={() => onCubeEdit({ cq: step.cube_query, label: step.label })}
                title="Deterministik koşar — LLM yok"
                className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-500 transition-colors hover:border-foreground/30 hover:text-foreground"
              >
                <span className="mr-1 text-neutral-400">
                  {step.kind === "dimension" ? "⌗" : step.kind === "time" ? "◷" : "∑"}
                </span>
                {step.label}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="mt-5 flex items-center justify-between">
        {sqlStage ? (
          <button
            onClick={() => setShowSql((s) => !s)}
            className="font-mono text-[11px] uppercase tracking-wider text-neutral-400 transition-colors hover:text-foreground"
          >
            {showSql ? "— sql gizle" : "+ sql göster"}
          </button>
        ) : (
          <span />
        )}
        {data.contract_id && (
          <span
            className="font-mono text-[10px] tracking-wider text-neutral-300 dark:text-neutral-600"
            title="Query Contract — bu raporun kanıt kaydı: soru + sorgu + sonuç özeti mühürlendi; sonradan yeniden oynatılıp doğrulanabilir"
          >
            {data.contract_id}
          </span>
        )}
      </div>
      {sqlStage && showSql && (
        <pre className="mt-2 overflow-auto border border-hairline bg-neutral-950 p-4 font-mono text-xs leading-relaxed text-neutral-100">
          {data.sql}
        </pre>
      )}
    </div>
  );
}

// Boş/bekleme durumlarında landing ile aynı imza: alt-orta ink filigran.
function Center({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex h-full items-center justify-center p-6">
      {children}
      <Link
        href="/brand"
        className="absolute inset-x-0 bottom-8 flex justify-center opacity-30 transition-opacity hover:opacity-80"
      >
        <BrandMark size="sm" ink />
      </Link>
    </div>
  );
}
