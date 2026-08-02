"use client";

import { useRef, useState } from "react";
import { useClickOutside } from "@/lib/useClickOutside";
import { useFeature } from "@/lib/useFeature";
import { usePermission } from "@/lib/usePermission";
import type { AskResponse, CubeQuery, DashboardListItem } from "@/lib/types";
import {
  addDashboardWidget,
  askVerify,
  createDashboard,
  createSchedule,
  listDashboards,
  verifyReport,
} from "@/lib/api-client";
import { ContractDetailPanel } from "@/components/ContractDetailPanel";
import { ContributionLayer } from "@/components/ContributionLayer";
import { PrescriptionLayer } from "@/components/PrescriptionLayer";
import { DrillDownPanel } from "@/components/DrillDownPanel";
import { InterpretationBar } from "@/components/InterpretationBar";
import { ResultView } from "@/components/ResultView";
import { KpiCardView } from "@/components/KpiCard";
import { OutputInsight } from "@/components/OutputInsight";
import { SourceBadge } from "@/components/ChatPanel";

// §B Adım 2 (1 Ağustos 2026) — tek-rapor kartı: bugünkü ReportPanel'in TÜM gövdesi + tüm
// rapor-başına local state'i (SQL/trace toggle, schedule/dashboard-ekle popover'ları, verify
// ✓/✗, drill-down, contract paneli) BİREBİR buraya taşındı — ReportPanel artık bunu bir
// thread'in item dizisi üstünde `.map()`ler (bkz. ReportPanel.tsx). `fb` (verify geri bildirim
// map'i) İÇERİK-ANAHTARLI olduğu için (verifyKey = label::sql) PAYLAŞILAN bir prop olarak
// yukarıdan alınır — yığındaki/thread'lerdeki TÜM kartlarda güvenle paylaşılabilir.
export function ReportCard({
  item,
  index,
  threadId,
  viewHint,
  onCubeEdit,
  precedingLabel,
  sessionId,
  fb,
  setFb,
  onReply,
  selectable,
  selected,
  onToggleSelect,
}: {
  item: AskResponse;
  // §B düzeltmesi (1 Ağustos 2026) — bu kartın thread.items içindeki konumu — "yanıtla"nın
  // çapa olarak hangi karta bağlandığını belirlemesi için (ReportPanel'e geri gönderilir).
  index: number;
  threadId: string;
  // "grafik ver" tarzı görünüm isteği — YALNIZ en son (aktif) karta anlamlıdır, ResultView'i
  // remount edip başlangıç görünümü zorlar. Önceki kartlar HER ZAMAN kendi kalıcı
  // item.view_hint'ini kullanır (bkz. ReportPanel'in yalnız son karta geçirme mantığı).
  viewHint?: { kind: string; nonce: number } | null;
  onCubeEdit?: (edit: { cq: CubeQuery; label: string }) => void;
  // §B Adım 2: sayfa-seviyeli tek `verifyLabel` state'i KALDIRILDI — her kart KENDİ
  // thread'inde, kendi indeksinden GERİYE doğru "chip:" ile başlamayan en yakın soruyu
  // ReportPanel'den (nearestRealQuestion) alır.
  precedingLabel: string | null;
  sessionId?: string;
  fb: Record<string, "ok" | "bad">;
  setFb: React.Dispatch<React.SetStateAction<Record<string, "ok" | "bad">>>;
  // §B düzeltmesi (1 Ağustos 2026) — "bu karta yanıt ver": bağlam BU kartın kendi
  // cube_query/sql'inden gelir, thread'in GÜNCEL durumundan DEĞİL. Sonuç thread'in
  // SONUNA eklenir (araya sokulmaz) — kullanıcının kendi netleştirdiği davranış.
  onReply?: (threadId: string, anchorIndex: number, text: string,
             hucre?: { dimension: string; value: string }) => void;
  // Çoklu-seçim (birleşik bağlam) — yalnız seçim modu açıkken görünür bir checkbox.
  selectable?: boolean;
  selected?: boolean;
  onToggleSelect?: () => void;
}) {
  const [showSql, setShowSql] = useState(false);
  const [showTrace, setShowTrace] = useState(false);
  // Faz 4.10 — dallı kök-neden analizi paneli (tıkla-dallan, ilişkili cube'lara geçiş,
  // yaprak seviyesinde ham satırlar).
  const [drillOpen, setDrillOpen] = useState(false);
  // Doğrulama turu düzeltmesi (1 Ağustos 2026, P1-2) — grafikte tıklanan tek kategori;
  // doluysa drill panelini "Başlangıç"tan değil DOĞRUDAN o kategoriye seçili açar.
  const [drillFilter, setDrillFilter] = useState<{ dimension: string; value: string } | null>(null);
  // Faz G2 — grafikte işaret edilen hücre. Panel AÇMAZ; kullanıcıya ne yapmak istediğini
  // sorar (konuş / kırılıma in). Tek tıklamaya tek yorum dayatmamak için.
  const [sohbetCapasi, setSohbetCapasi] =
    useState<{ dimension: string; value: string } | null>(null);
  const closeDrill = () => { setDrillOpen(false); setDrillFilter(null); };
  // Query Contract keşif/replay paneli (doğrulama turu düzeltmesi, 1 Ağustos 2026, P1-9).
  const [contractOpen, setContractOpen] = useState(false);
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
    liveViewRef.current = { sql: item.sql ?? "", hint };
  };
  const openDashMenu = () => {
    if (!dashOpen) listDashboards().then((r) => setDashList(r.dashboards)).catch(() => {});
    setSchedOpen(false); setWrongOpen(false);  // tek-açık
    setDashOpen((o) => !o);
  };
  const addToDash = async (dashId: string) => {
    if (!item.cube_query) return;
    try {
      const lv = liveViewRef.current;
      const liveHint = lv && lv.sql === (item.sql ?? "") ? lv.hint : null;
      await addDashboardWidget(dashId, {
        title: item.question,
        cube_query: item.cube_query, // compare (YoY) dahil — backend add_widget korur
        // Kullanıcının seçtiği canlı görünüm (tip/ölçü) öncelikli; yoksa /ask'ın ipucu.
        view_hint: liveHint ?? item.view_hint ?? null,
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
  const measures = ((item.cube_query?.measures as string[] | undefined) ?? []);
  const [alarmType, setAlarmType] = useState<"none" | "threshold" | "anomaly">("none");
  const [alarmMeasure, setAlarmMeasure] = useState<string>("");
  const [alarmOp, setAlarmOp] = useState<"gt" | "lt">("gt");
  const [alarmValue, setAlarmValue] = useState<string>("");
  const [emails, setEmails] = useState<string>("");
  const schedule = (preset: { every: "hour" | "day" | "week"; at?: string; weekday?: number; period: string; name: string }) => {
    if (!item.cube_query) return;
    const cq = { ...item.cube_query,
      filters: ((item.cube_query.filters as { dimension: string }[] | undefined) ?? [])
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
    setActionError(null);
    createSchedule({ label: vLabel ?? item.question, cube_query: cq,
      period: preset.period, every: preset.every, at: preset.at, weekday: preset.weekday,
      threshold, delivery: to.length ? { email: { to } } : null })
      .then(() => { setScheduled(verifyKey); setSchedOpen(false); })
      .catch(() => setActionError("Zamanlama kaydedilemedi. Lütfen tekrar dener misin?"));
  };

  // "✓ doğru" / "✗ yanlış" (beta bayrağı): geri bildirim — doğrulama geri ALINABİLİR.
  // `fb` artık PAYLAŞILAN bir prop (bkz. ReportPanel) — içerik-anahtarlı olduğu için
  // (verifyKey = label::sql) yığındaki/thread'lerdeki TÜM kartlarda güvenle paylaşılır.
  const verifyStage = useFeature("verify_button");
  const vLabel = item.question.startsWith("chip:") ? (precedingLabel ?? item.question) : item.question;
  // Doğrulanabilir iki şekilden biri: deterministik cube_query (eski /verify) YA DA
  // strict-agentic wren_sql cevabı (yeni /ask/verify) — ikisi de "gerçek bir SQL üretti ve
  // çalıştırdı" anlamına gelir, yalnız hangi API çağrılacağı farklıdır (bkz. doVerify).
  const verifiable = Boolean(item.cube_query) || Boolean(item.sql);
  const verifyKey = verifiable && vLabel ? `${vLabel}::${item.sql ?? ""}` : null;
  const verified = verifyKey != null && fb[verifyKey] === "ok";
  const flagged = verifyKey != null && fb[verifyKey] === "bad";
  // ✗ yanlış → yorum popup'ı: kullanıcı isterse "neden yanlış"ı yazar, isterse yazmadan
  // yollar. Yorum backend'de note'a düşer → log madencisini (#57) besler.
  const [wrongOpen, setWrongOpen] = useState(false);
  const [wrongComment, setWrongComment] = useState("");
  // §B düzeltmesi (1 Ağustos 2026) — "↳ yanıtla": mevcut dashOpen/schedOpen/wrongOpen
  // dörtlüsüyle (closeMenus/actionsRef) AYNI tek-açık/dışarı-tıklamada-kapan deseni.
  const [replyOpen, setReplyOpen] = useState(false);
  const [replyText, setReplyText] = useState("");
  // Doğrulama turu düzeltmesi (1 Ağustos 2026, P1-12): zamanla/doğrula/yanlış-işaretle
  // aksiyonları başarısız olursa kullanıcı HİÇBİR geri bildirim almıyordu (popup sessizce
  // açık kalıyor ya da buton durumu güncellenmiyordu) — tek, paylaşılan bir hata metni.
  const [actionError, setActionError] = useState<string | null>(null);
  // Rapor aksiyon menüleri (zamanla / panoya ekle / yanlış / yanıtla) TEK-AÇIK + dışarı-
  // tıklamada kapanır.
  const closeMenus = () => { setDashOpen(false); setSchedOpen(false); setWrongOpen(false); setReplyOpen(false); };
  const actionsRef = useClickOutside<HTMLDivElement>(
    dashOpen || schedOpen || wrongOpen || replyOpen, closeMenus,
  );
  const submitReply = () => {
    const t = replyText.trim();
    if (!t || !onReply) return;
    onReply(threadId, index, t);
    setReplyOpen(false);
    setReplyText("");
  };
  // cube_query varsa deterministik /verify; yoksa (strict-agentic /ask) wren_sql /ask/verify.
  const doVerify = (opts: { undo?: boolean; verdict?: "wrong"; comment?: string }) => {
    if (!vLabel) return Promise.reject(new Error("no label"));
    if (item.cube_query) {
      return verifyReport(item.cube_query, vLabel, { session_id: sessionId, ...opts });
    }
    if (item.sql) {
      return askVerify({ question: vLabel, sql: item.sql, session_id: sessionId, ...opts });
    }
    return Promise.reject(new Error("no verifiable payload"));
  };
  const submitWrong = () => {
    if (!verifyKey) return;
    setActionError(null);
    doVerify({ verdict: "wrong", comment: wrongComment.trim() || undefined })
      .then(() => { setFb((m) => ({ ...m, [verifyKey]: "bad" })); setWrongOpen(false); setWrongComment(""); })
      .catch(() => setActionError("Geri bildirim gönderilemedi. Lütfen tekrar dener misin?"));
  };

  return (
    <div className="mx-auto max-w-4xl px-8 py-7">
      <div className="mb-5 border-b border-hairline pb-4">
        <div className="flex items-start justify-between gap-3">
          {selectable && (
            <input
              type="checkbox"
              checked={!!selected}
              onChange={onToggleSelect}
              title="Bu kartı birleşik bağlama ekle"
              className="mt-1.5 h-3.5 w-3.5 shrink-0 accent-accent"
            />
          )}
          <div className="min-w-0 flex-1">
            {/* §B (Madde 4, 1 Ağustos 2026): sol paneldeki vurgu kaydırınca görünür alan
                dışına çıkabiliyordu — burada HER ZAMAN görünen, "şu an gösterilen bu mu,
                yeni bir konu mu yoksa devam mı" sorusunu doğrudan cevaplayan bir etiket.
                §B DÜZELTMESİ (1 Ağustos 2026): `reply_to_label` VARSA (bu karta özel bir
                yanıtsa) ÖNCELİKLİ gösterilir — hangi karta bağlandığı en somut bilgi. */}
            <span className="mb-0.5 block font-mono text-[10px] uppercase tracking-wider text-neutral-400">
              {item.reply_to_label
                ? `↳ yanıt: "${item.reply_to_label}"`
                : item.is_new_topic ? "◆ yeni konu" : "↳ önceki raporun devamı"}
            </span>
            <h2 className="font-mono text-[15px] leading-snug text-foreground">{item.question}</h2>
          </div>
          <div ref={actionsRef} className="flex shrink-0 items-center gap-1.5 pt-0.5">
            {schedStage && canSchedule && item.cube_query && item.source && (
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
            {dashStage && item.cube_query && item.source && (
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
            {verifyStage && canVerify && verifiable && item.source && (
              // tek kutu: ✓/✗ geri bildirim (aşama rozeti gösterilmez — bayrak iç bilgi)
              <div className="relative inline-flex h-[20px] items-stretch border border-hairline font-mono text-[11px]">
                <button
                  onClick={() => {
                    if (!verifyKey) return;
                    setActionError(null);
                    // ikinci tık = GERİ AL (yanlışlıkla doğrulamayı düzeltme yolu)
                    doVerify({ undo: verified || undefined })
                      .then(() =>
                        setFb((m) => {
                          const n = { ...m };
                          if (verified) delete n[verifyKey];
                          else n[verifyKey] = "ok";
                          return n;
                        }),
                      )
                      .catch(() => setActionError("İşlem gerçekleştirilemedi. Lütfen tekrar dener misin?"));
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
            <SourceBadge source={item.source} confidence={item.explain?.confidence} />
            {item.cube_query && item.result && (
              <button
                onClick={() => setDrillOpen(true)}
                title="Bu sayı hangi kırılımlardan oluşuyor? Tıklaya tıklaya en alt satıra kadar in. (SEVİYE analizi — değişim için «𝚫 neden değişti?»)"
                className="border border-hairline px-2 py-[3px] font-mono text-[11px] text-neutral-400 transition-colors hover:border-accent hover:text-accent"
              >
                ⤵ kırılıma in
              </button>
            )}
            {item.trace && item.trace.length > 0 && (
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
            {/* §B düzeltmesi (1 Ağustos 2026) — "buna cevap ver": mevcut dashOpen/schedOpen/
                wrongOpen popover'larıyla AYNI görsel desen (küçük textarea + gönder/vazgeç),
                AYNI actionsRef alt-ağacının İÇİNDE (dışında olsaydı textarea'ya tıklamak
                kendini kapatırdı). */}
            {onReply && (
              <span className="relative">
                <button
                  onClick={() => { setDashOpen(false); setSchedOpen(false); setWrongOpen(false); setReplyOpen((o) => !o); }}
                  title="Bu karta yanıt ver — thread'in SONUNA eklenir, bu kartın bağlamıyla"
                  className={`flex h-[20px] items-center border px-1.5 font-mono text-[11px] transition-colors ${
                    replyOpen ? "border-accent/40 text-accent" : "border-hairline text-neutral-400 hover:text-foreground"
                  }`}
                >
                  ↳ yanıtla
                </button>
                {replyOpen && (
                  <span className="absolute right-0 top-full z-30 mt-1 flex w-64 flex-col gap-2 border border-hairline bg-background p-2 text-left shadow-lg">
                    <span className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
                      bu karta yanıt ver
                    </span>
                    <textarea
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      rows={3}
                      placeholder="ör. bu ölçüyü haftalık kır…"
                      className="resize-none border border-hairline bg-background px-1.5 py-1 font-mono text-[11px]"
                    />
                    <div className="flex gap-1">
                      <button
                        onClick={submitReply}
                        className="flex-1 border border-accent/40 px-2 py-1 font-mono text-[11px] text-accent transition-colors hover:bg-accent/[0.06]"
                      >
                        gönder
                      </button>
                      <button
                        onClick={() => { setReplyOpen(false); setReplyText(""); }}
                        className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground"
                      >
                        vazgeç
                      </button>
                    </div>
                  </span>
                )}
              </span>
            )}
          </div>
        </div>
        {actionError && (
          <p className="mt-2 font-mono text-[11px] text-red-500">{actionError}</p>
        )}
        {/* Faz 1.5: konu-değişimi gibi bilgilendirici notlar (ör. "Konu değişti: OEE → parti")
            artık gerçek bir raporla BİRLİKTE gelebilir (ChatPanel'deki AYNI desen) — rapor
            açıldığında kullanıcı NEDEN konunun değiştiğini burada da görsün, yalnız sohbet
            akışına gömülü kalmasın. */}
        {item.note && !item.kpi && (
          <div className="mt-3 border-l-2 border-amber-500/50 bg-amber-500/[0.04] py-1.5 pl-3 font-mono text-[12px] leading-snug text-neutral-500">
            {item.note}
          </div>
        )}
        {showTrace && item.trace && (
          <div className="mt-3 border border-hairline bg-neutral-500/[0.03] p-3">
            <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
              nasıl çözüldü
            </div>
            <ol className="space-y-0.5">
              {item.trace.map((t, i) => (
                <li key={i} className="font-mono text-[11px] text-neutral-500">
                  <span className="mr-1 text-accent">{String(i + 1).padStart(2, "0")}</span>
                  {t}
                </li>
              ))}
            </ol>
            {/* Faz 3: `explain` trace'in ÜSTÜNE biner (onu değiştirmez) — yalnız sessizce
                yapılan gerçek bir varsayım varsa (ör. dönem belirtilmedi) gösterilir. */}
            {item.explain && item.explain.assumptions.length > 0 && (
              <div className="mt-2 border-t border-hairline pt-2">
                <div className="mb-1 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
                  varsayımlar
                </div>
                <ul className="space-y-0.5">
                  {item.explain.assumptions.map((a, i) => (
                    <li key={i} className="font-mono text-[11px] text-amber-600">
                      {a}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {item.cube_query && onCubeEdit &&
        ((item.cube_query as { measures?: unknown[] }).measures?.length ?? 0) > 0 && (
        <InterpretationBar cq={item.cube_query} onEdit={onCubeEdit} />
      )}

      {/* Cross-cube KPI kartı (CCC / likidite) — cube tablosu değil bileşke skaler. */}
      {item.kpi && <KpiCardView card={item.kpi} />}

      {item.result && (
        <div className="border border-hairline bg-background p-4">
          <ResultView
            key={`${item.question}·${item.sql}·${viewHint?.nonce ?? 0}`}
            result={item.result}
            viewHint={viewHint?.kind}
            viz={item.viz}
            onViewChange={onLiveView}
            onDataPointClick={
              item.cube_query
                ? (dimension, value) => {
                    // FAZ G2 — grafikte bir hücreye tıklamak ARTIK doğrudan panel açmaz.
                    // Önce bir SOHBET ÇAPASI kurulur: kullanıcı o hücre hakkında
                    // konuşabilir ("neden böyle?") ya da kırılıma inebilir. Panelin
                    // hemen açılması tek bir yorumu (gezinme) dayatıyordu; oysa aynı
                    // tıklama "bunu konuşalım" da demek olabilir.
                    setSohbetCapasi({ dimension, value });
                  }
                : undefined
            }
          />
        </div>
      )}

      {/* Evrensel çıktı yorumu (feature flag'li) — KPI/tablo/grafik altında. */}
      <OutputInsight interpretation={item.interpretation} />

      {/* Madde 12 (1 Ağustos 2026): düz-dil "nasıl hesaplandı?" — KpiCard'ın card.explain'iyle
          AYNI amaç, sıradan (KPI-olmayan) cube raporları için. SQL okumayan kullanıcı için
          SQL toggle'ından ÖNCELİKLİ: her zaman görünür, "+ sql göster" açılmasa bile. KPI
          kartı zaten kendi açıklamasını gösterdiği için burada TEKRAR EDİLMEZ. */}
      {!item.kpi && item.calculation_explanation && (
        <p className="mt-3 max-w-prose whitespace-pre-line text-xs leading-relaxed text-neutral-500">
          {item.calculation_explanation}
        </p>
      )}

      {/* K4 öneriler — K3 sinyalinden 'neye bakmalısın' + opsiyonel tıklanır drill. */}
      {onCubeEdit && (item.recommendations?.length ?? 0) > 0 && (
        <div className="mt-3 space-y-1.5">
          {item.recommendations!.map((rec, i) => (
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

      {/* FAZ H2 — "neden değişti?" cevabın İÇİNDE bir katman (yeni panel DEĞİL, H3 kuralı).
          Backend'de Faz 5.1/5.2'de yazılmış `POST /ask/contribution` bu turda ilk kez bir
          tüketici kazandı; `tests/test_uc_yetim_degil.py` onu artık CI'da tutuyor. Yalnız
          gerçek bir sonucu olan cube cevaplarında görünür — dönemsel değişim yoksa uç zaten
          dürüst bir `note` döndürür. */}
      {/* FAZ G2 — GRAFİĞE ÇAPALI DİYALOG. Kullanıcı bir hücreye tıkladığında tek bir
          yorum DAYATILMAZ; ne yapmak istediği sorulur. Aynı tıklama "buraya inelim" de
          olabilir "bunu konuşalım" da — panelin doğrudan açılması ikincisini imkânsız
          kılıyordu. Şerit yalnız tıklamadan SONRA belirir: boşken hiçbir yer kaplamaz
          (kademeli açılım, MIMARI §14.2). */}
      {sohbetCapasi && (
        <div className="mt-2 flex flex-wrap items-center gap-1.5 border border-accent/30 bg-accent/[0.04] p-2">
          <span className="font-mono text-[11px] text-neutral-400">
            ◎ <span className="text-foreground">{sohbetCapasi.value}</span> seçildi —
          </span>
          {onReply && (["bu neden böyle?", "normal mi?"] as const).map((soru) => (
            <button
              key={soru}
              onClick={() => {
                onReply(threadId, index, soru, sohbetCapasi);
                setSohbetCapasi(null);
              }}
              title="Konuşma YALNIZ bu hücrenin üstünde yürür — koordinat gerçek bir alt-sorguya çevrilir"
              className="border border-hairline px-2 py-[3px] font-mono text-[11px] text-neutral-400 transition-colors hover:border-accent hover:text-accent"
            >
              {soru}
            </button>
          ))}
          <button
            onClick={() => {
              setDrillFilter(sohbetCapasi);
              setDrillOpen(true);
              setSohbetCapasi(null);
            }}
            title="Bu hücrenin altındaki kırılımlara in"
            className="border border-hairline px-2 py-[3px] font-mono text-[11px] text-neutral-400 transition-colors hover:border-accent hover:text-accent"
          >
            ⤵ kırılıma in
          </button>
          <button
            onClick={() => setSohbetCapasi(null)}
            aria-label="Seçimi kaldır"
            className="ml-auto font-mono text-[11px] text-neutral-500 hover:text-foreground"
          >
            ×
          </button>
        </div>
      )}

      {/* REÇETE önce gelir: kullanıcı "ne yapmalıyız?" diye sordu — CEVAP budur.
          Altındaki katkı katmanı o cevabın DAYANAĞIDIR (hangi segment ne kadar
          hareket etti). Sıra ters olsaydı kullanıcı önce ham ayrışmayı, sonra
          cevabı görürdü. */}
      {item.prescription && (
        <PrescriptionLayer recete={item.prescription} onCubeEdit={onCubeEdit} />
      )}

      {item.cube_query && (item.result || item.contribution) && (
        <ContributionLayer
          cubeQuery={item.cube_query}
          sessionId={sessionId}
          onCubeEdit={onCubeEdit}
          hazir={item.contribution ?? null}
        />
      )}

      {/* K2 sonraki adım chip'leri (backend 'next_steps' flag'iyle gelir) — kırılım/ölçek/
          zaman. Tıklama mevcut deterministik /cube yolunu kullanır (LLM yok). */}
      {/* Konuşma cevabında (`contribution` dolu) bu blok GİZLENİR: bulgular cevabın
          GÖVDESİDİR ve yukarıda zengin haliyle duruyor. Burada da göstermek aynı listeyi
          İKİ KEZ, üstelik ikincisini YANLIŞ BAŞLIKLA ("sonraki adım") sunardı. */}
      {!item.contribution && onCubeEdit && (item.next_steps?.length ?? 0) > 0 && (
        <div className="mt-3">
          <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
            sonraki adım
          </div>
          <div className="flex flex-wrap gap-1.5">
            {item.next_steps!.map((step, i) => (
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
        {item.contract_id && (
          <button
            onClick={() => setContractOpen(true)}
            className="font-mono text-[10px] tracking-wider text-neutral-300 underline-offset-2 transition-colors hover:text-foreground hover:underline dark:text-neutral-600"
            title="Query Contract — bu raporun kanıt kaydı: soru + sorgu + sonuç özeti mühürlendi; sonradan yeniden oynatılıp doğrulanabilir (tıkla → incele)"
          >
            {item.contract_id}
          </button>
        )}
      </div>
      {sqlStage && showSql && (
        <pre className="mt-2 overflow-auto border border-hairline bg-neutral-950 p-4 font-mono text-xs leading-relaxed text-neutral-100">
          {item.sql}
        </pre>
      )}
      {/* Doğrulama turu düzeltmesi (1 Ağustos 2026, P2-22): `planned_sql` (dry-plan çıktısı —
          backend'de zaten dolduruluyordu, bkz. app/routers/ask.py) hiç GÖSTERİLMİYORDU.
          Yalnız GERÇEK çalışan SQL'den FARKLIYSA gösterilir (self-healing/repair sonrası
          "plan neydi, gerçekte ne çalıştı" farkını görünür kılar) — aynıysa gürültü olmasın
          diye tekrar edilmez. */}
      {sqlStage && showSql && item.planned_sql && item.planned_sql !== item.sql && (
        <div className="mt-2">
          <p className="mb-1 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
            plan (öz iyileştirme öncesi derlenen SQL)
          </p>
          <pre className="overflow-auto border border-hairline bg-neutral-950 p-4 font-mono text-xs leading-relaxed text-neutral-400">
            {item.planned_sql}
          </pre>
        </div>
      )}
      {contractOpen && item.contract_id && (
        <ContractDetailPanel contractId={item.contract_id} onClose={() => setContractOpen(false)} />
      )}
      {drillOpen && item.cube_query && item.result && (
        <DrillDownPanel
          cubeQuery={item.cube_query}
          result={item.result}
          sessionId={sessionId}
          initialFilter={drillFilter}
          onClose={closeDrill}
        />
      )}
    </div>
  );
}
