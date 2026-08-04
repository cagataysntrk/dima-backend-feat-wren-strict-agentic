"use client";

import { useRef, useState } from "react";
import { useClickOutside } from "@/lib/useClickOutside";
import { useFeature } from "@/lib/useFeature";
import { usePermission } from "@/lib/usePermission";
import { NextStepChips } from "@/components/NextStepChips";
import type { AskResponse, CubeQuery, DashboardListItem } from "@/lib/types";
import {
  addDashboardWidget,
  askVerify,
  createDashboard,
  createSchedule,
  onaylaEylem,
  listDashboards,
  verifyReport,
  createShareLink,
} from "@/lib/api-client";
import { ContractDetailPanel } from "@/components/ContractDetailPanel";
import { ContributionLayer } from "@/components/ContributionLayer";
import { PrescriptionLayer } from "@/components/PrescriptionLayer";
import { DrillDownPanel } from "@/components/DrillDownPanel";
import { InterpretationBar } from "@/components/InterpretationBar";
import { ResultView } from "@/components/ResultView";
import { KpiCardView } from "@/components/KpiCard";
import { OutputInsight } from "@/components/OutputInsight";
import { AdhocBadge, SourceBadge } from "@/components/ChatPanel";

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
  // FAZ H — onay kartı. Öneri hangi izne bağlıysa O kontrol edilir; ama hook sırası
  // sabit kalmalı (React kuralı), bu yüzden KAYITTAKİ izinlerin hepsi baştan çözülür
  // (`app/eylem.py::EYLEM_KAYIT` → query:run · schedule:create). Kayda üçüncü bir izin
  // eklenirse buraya da eklenmeli — backend testi (`test_eylem_onayi.py`) bunu kilitler.
  const canQuery = usePermission("query:run");
  const izinliMi = (izin: string) =>
    izin === "schedule:create" ? canSchedule : izin === "query:run" ? canQuery : false;
  const [eylemBekliyor, setEylemBekliyor] = useState(false);
  // FAZ 5.2 — paylaşılabilir link. `null` = henüz istenmedi; string = link ya da hata.
  const [paylasimLink, setPaylasimLink] = useState<string | null>(null);
  const [paylasimHata, setPaylasimHata] = useState<string | null>(null);
  const paylasimAcik = useFeature("tur_paylas");
  const [eylemSonuc, setEylemSonuc] = useState<string | null>(null);
  const onaylaEylemi = async () => {
    const oneri = item.eylem_onerisi;
    if (!oneri || eylemBekliyor) return;
    setEylemBekliyor(true);
    setActionError(null);
    try {
      // Kullanıcının o anki CANLI görünümü yalnız burada bilinir (backend uydurmaz).
      const lv = liveViewRef.current;
      const liveHint = lv && lv.sql === (item.sql ?? "") ? lv.hint : null;
      const args = { ...oneri.argumanlar,
                     ...(liveHint && oneri.eylem === "pano.ekle" ? { view_hint: liveHint } : {}) };
      const out = await onaylaEylem(oneri.eylem, args);
      setEylemSonuc(out.note);
    } catch {
      setActionError("İşlem tamamlanamadı. Lütfen tekrar dener misin?");
    } finally {
      setEylemBekliyor(false);
    }
  };
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
            {/* FAZ S · STEERING — kullanıcı bu cevap hazırlanırken yeni bir soru sordu.
                Cevap KAYBOLMADI (sessiz iptal yok) ama aktif bağlamı ele geçirmedi.
                Bunu söylememek "neden eski rapor geri geldi?" sorusunu doğururdu. */}
            {item.steering_golgede && (
              <span className="mb-1 block font-mono text-[10px] text-amber-500">
                ↺ bu cevap siz yeni bir soru sorarken hazırlanıyordu — bağlam yeni
                sorunuzda kaldı
              </span>
            )}
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
            {/* FAZ 2.6 — MALİ YIL. Yalnız takvim yılından FARKLIYSA görünür.
                🔴 "Bu yıl" dediğinde Nisan–Mart penceresi gelen bir kullanıcı, hangi
                pencereyi gördüğünü BİLMELİ: doğru sayı, yanlış soruya cevap olabilir. */}
            {/* FAZ 2.5 — HEDEF. Yalnız BEYAN varsa görünür; hedef UYDURULMAZ. */}
            {item.hedef && (
              <span
                title={`Hedef ${item.hedef.hedef} · gerçekleşen ${item.hedef.gerceklesen}` +
                  (item.hedef.sapma_yuzde !== null ? ` · sapma %${item.hedef.sapma_yuzde}` : "")}
                className={`inline-flex h-[20px] items-center gap-1 border px-1.5 font-mono text-[10px] tracking-wide ${
                  item.hedef.ulasildi
                    ? "border-accent/40 text-accent"
                    : "border-amber-500/40 text-amber-600"
                }`}
              >
                {item.hedef.ulasildi ? "◉" : "◎"} hedef {item.hedef.hedef}
              </span>
            )}
            {item.mali_donem && (
              <span
                title={`Bu şirketin mali yılı takvim yılından farklı. Gösterilen pencere: ${item.mali_donem}`}
                className="inline-flex h-[20px] items-center gap-1 border border-hairline px-1.5 font-mono text-[10px] tracking-wide text-neutral-500"
              >
                <span aria-hidden>◷</span> {item.mali_donem}
              </span>
            )}
            {/* FAZ 1 (K1): yapı ham SQL'den TÜRETİLDİYSE rozet bunu söyler — yapı ≠ güven. */}
            <AdhocBadge cubeQuery={item.cube_query} />
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
        {item.note && !item.kpi && !item.eylem_onerisi && (
          <div className="mt-3 border-l-2 border-amber-500/50 bg-amber-500/[0.04] py-1.5 pl-3 font-mono text-[12px] leading-snug text-neutral-500">
            {item.note}
          </div>
        )}
        {/* FAZ H — ONAY KARTI. Ajan yazma işini ÇALIŞTIRMAZ, önerir; yazma yalnız bu
            düğmeye basılınca ve KULLANICININ KENDİ kimliğiyle olur.
            · Düğme yetkiye bağlı: `oneri.izin` /auth/me `permissions` listesinde YOKSA
              düğme HİÇ çıkmaz (rol matrisi UI'a KOPYALANMAZ — CLAUDE.md).
            · Geri alınamaz eylemde (zamanlama) dil AĞIRLAŞIR ve bu AÇIKÇA yazılır;
              kullanıcı neyi onayladığını okumadan basmasın.
            · `view_hint` burada eklenir: kullanıcının o anki CANLI görünümünü yalnız
              frontend bilir, backend onu UYDURMAZ. */}
        {item.eylem_onerisi && (
          <div className="mt-3 border border-accent/40 bg-accent/[0.04] p-3">
            <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-accent">
              onay gerekiyor
            </div>
            <p className="font-mono text-[12px] leading-snug text-foreground">
              {item.eylem_onerisi.ozet}
            </p>
            {!item.eylem_onerisi.geri_alinabilir && (
              <p className="mt-1 font-mono text-[11px] text-amber-500">
                Bu işlem geri alınamaz: kurulduktan sonra gönderilmiş bildirimler geri çekilemez.
              </p>
            )}
            {eylemSonuc ? (
              <p className="mt-2 font-mono text-[11px] text-accent">✓ {eylemSonuc}</p>
            ) : izinliMi(item.eylem_onerisi.izin) ? (
              <div className="mt-2 flex items-center gap-2">
                <button
                  onClick={onaylaEylemi}
                  disabled={eylemBekliyor}
                  className="border border-accent/50 px-2 py-0.5 font-mono text-[11px] text-accent transition-colors hover:bg-accent/10 disabled:opacity-50"
                >
                  {eylemBekliyor ? "…" : "Onayla"}
                </button>
                <button
                  onClick={() => setEylemSonuc("Vazgeçildi — hiçbir şey kaydedilmedi.")}
                  className="border border-hairline px-2 py-0.5 font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground"
                >
                  Vazgeç
                </button>
              </div>
            ) : (
              <p className="mt-2 font-mono text-[11px] text-neutral-400">
                Bu işlem için yetkiniz yok — bir yöneticiden isteyebilirsiniz.
              </p>
            )}
          </div>
        )}
        {/* FAZ 5.2 — PAYLAŞILABİLİR LİNK. Yeni panel DEĞİL: kartın kendi şeridinde bir
            satır (K5 tavanı 13/13). Dört değişmez sunucuda uygulanır ve kullanıcıya
            **söylenir**: link süreli ve maskeli, ve bir OTURUM DEĞİLDİR — çalıştırılabilir
            bir sorgu taşımaz. *Kullanıcı neyi paylaştığını bilmeden paylaşamaz.* */}
        {paylasimAcik && item.result && (
          <div className="mt-3 border-t border-hairline pt-2">
            <button
              type="button"
              onClick={async () => {
                setPaylasimHata(null);
                try {
                  const r = await createShareLink(item);
                  // 🔴 Link **frontend** yoluna gider, API yoluna değil: `r.share_url`
                  // (`/share/{token}`) bir API ucudur ve açan kişi ham JSON görürdü.
                  // Yetim-uç kapısı bunu commit'ten ÖNCE yakaladı.
                  const tok = r.share_url.split("/").pop() ?? "";
                  setPaylasimLink(`${window.location.origin}/paylasim/${tok}`);
                } catch {
                  setPaylasimHata("Paylaşım linki oluşturulamadı.");
                }
              }}
              className="font-mono text-[11px] text-neutral-400 transition-colors hover:text-accent"
            >
              ⇗ paylaşılabilir link
            </button>
            {paylasimHata && (
              <p className="mt-1 font-mono text-[11px] text-red-500">{paylasimHata}</p>
            )}
            {paylasimLink && (
              <div className="mt-1.5 space-y-1">
                <input
                  readOnly
                  value={paylasimLink}
                  onFocus={(e) => e.currentTarget.select()}
                  className="w-full border border-hairline bg-transparent px-2 py-1 font-mono text-[11px] text-foreground"
                />
                <p className="font-mono text-[10px] leading-snug text-neutral-400">
                  Link <span className="text-foreground">7 gün</span> geçerli, içerik{" "}
                  <span className="text-foreground">maskelenmiş</span> ve yalnız{" "}
                  <span className="text-foreground">aynı şirketten</span> giriş yapmış
                  biri açabilir. Sorgu taşımaz — bir rapor görüntüsüdür, bir oturum değil.
                </p>
              </div>
            )}
          </div>
        )}
        {showTrace && item.trace && (
          <div className="mt-3 border border-hairline bg-neutral-500/[0.03] p-3">
            <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
              nasıl çözüldü
            </div>
            {/* ⚠️ FAZ 0.9 — `explain.path` YETİMDİ: tip `types.ts`'te vardı, hiçbir yerde
                RENDER EDİLMİYORDU ([KANIT §0.1-7]). Backend her cevapta hangi YOLDAN
                geçildiğini yazıyor (cube · cube+llm · llm:*) ve bu, rozetin taşıdığı
                garantiyi TAMAMLAYAN bilgidir: rozet "ne" der, yol "nereden" der.
                Trace bloğunun ÜSTÜNE konur çünkü adımların bağlamıdır — MIMARI §5'in
                "source gizlenemez" kuralının ayrıntı katmanı. */}
            {item.explain?.path && (
              <div className="mb-2 font-mono text-[11px] text-neutral-500">
                <span className="mr-1 text-neutral-400">yol:</span>
                <span className="text-foreground">{item.explain.path}</span>
              </div>
            )}
            {/* FAZ 1.12 — KANIT SINIFI. ⚠ Skaler bir "güven yüzdesi" DEĞİL: MIMARI §5'in
                kararı gereği kalibre edilmemiş bir sayı "güven değil SÜStür". Bu bir
                KATEGORİ ve ayrıntı katmanında durur (D3: makbuz katmanlı) — üst satırda
                gösterilseydi rozetin söylediğini ikinci kez, başka kelimelerle söylerdi.
                `cube+llm`'de sayı küpten gelse bile ALAN SEÇİMİ olasılıksaldır: seçim
                yanlışsa doğru sayı YANLIŞ SORUYA cevap olur. */}
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
            {/* FAZ 4 — AJAN KOŞUM MAKBUZU. `trace` insan-okur bir anlatı; bu ise
                DENETLENEBİLİR bir kayıt: hangi araç, ne kadar sürdü, hangi adım
                REDDEDİLDİ. Reddedilen adımlar GİZLENMEZ — bütçe tüketildi ve kullanıcı
                neyin DENENDİĞİNİ görebilmeli (sessizce kaybolan bir adım, yapılmamış bir
                adım gibi okunur ve koşumun maliyeti anlaşılmaz olur). */}
            {item.agent_run && item.agent_run.steps.length > 0 && (
              <div className="mt-2 border-t border-hairline pt-2">
                <div className="mb-1 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
                  <span>ajan adımları</span>
                  <span className="text-neutral-500">
                    {item.agent_run.step_count} adım · {item.agent_run.query_count} sorgu
                  </span>
                  {item.agent_run.truncated && (
                    <span
                      className="text-amber-600"
                      title={item.agent_run.truncation_reason ?? "bütçe tavanı aşıldı"}
                    >
                      ⚠ kısıldı
                    </span>
                  )}
                </div>
                <ul className="space-y-0.5">
                  {item.agent_run.steps.map((s, i) => (
                    <li
                      key={`${s.tool}-${i}`}
                      className={`font-mono text-[11px] ${s.error ? "text-amber-600" : "text-neutral-500"}`}
                      title={s.error ?? undefined}
                    >
                      <span className="mr-1 text-neutral-400">
                        {s.determinism === "llm" ? "▚" : "◆"}
                      </span>
                      {s.tool}
                      <span className="ml-1 text-neutral-400">{s.ms}ms</span>
                      {s.error && <span className="ml-1">— reddedildi</span>}
                      {s.gated === false && (
                        <span className="ml-1 text-amber-600" title={s.note}>
                          — kapısız
                        </span>
                      )}
                      {/* ⚠️ FAZ 0.8 — `agent_run.steps[].receipt` YETİMDİ: yalnız
                          `types.ts:74`'te geçiyordu, hiçbir yerde render edilmiyordu
                          ([KANIT §0.1-7]). Makbuz kimliği, bir adımın ürettiği KANITIN
                          kimliğidir: tıklanınca o kanıtın kendisine (`/contracts/{id}`)
                          gider. Bu, "her sayının kaynağını kanıtlayabilen" vaadinin
                          ADIM SEVİYESİNDEKİ karşılığıdır — makbuz görünmezse vaat bir
                          beyandan ibarettir. */}
                      {s.receipt && (
                        <a
                          href={`/contracts/${s.receipt}`}
                          title="Bu adımın ürettiği kanıt (Query Contract)"
                          className="ml-1 text-accent underline-offset-2 hover:underline"
                        >
                          ⛓ makbuz
                        </a>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}

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

      {/* ⚠️ FAZ 1.7 — TAZELİK MERDİVENİ, ÜÇ GÖRSEL HÂL.
          🔴 `hata` VE `bilinmiyor` kademelerinde SAYI GÖSTERİLMEZ; yerine AÇIKLAMA gelir.
          B4: **bilinmeyen tazelik TAZE DEĞİLDİR** — ölçemediğimiz bir şeyi iyi varsaymak,
          `⊘ ÖLÇÜLEMEDİ` üçüncü hâlinin tam tersi olurdu. Kaynak planlar bunun TERSİNİ
          yazıyordu; yol haritası "bugünkü davranıştan KASITLI BİR SERTLEŞME" diye düzeltti.
          Sekiz gün eski bir sayıyı normal gibi göstermek, kullanıcıyı YANLIŞ BİR KARARA
          götürür — ve o karar geri alınamaz. Sayının yerine NEDEN gösterilmediği gelir. */}
      {item.result && (item.freshness === "hata" || item.freshness === "bilinmiyor") && (
        <div className="border border-amber-600/60 bg-amber-950/20 p-4">
          <p className="mb-1 font-mono text-[10px] uppercase tracking-wider text-amber-500">
            {item.freshness === "hata" ? "veri bayat — sayı gösterilmiyor"
                                       : "tazelik bilinmiyor — sayı gösterilmiyor"}
          </p>
          <p className="text-[13px] leading-relaxed text-amber-200/90">
            {item.tazelik_aciklama}
          </p>
          {item.son_veri_ts && (
            <p className="mt-1.5 font-mono text-[10px] text-neutral-400">
              son senkron: {new Date(item.son_veri_ts).toLocaleString("tr-TR")}
            </p>
          )}
        </div>
      )}

      {item.result && item.freshness !== "hata" && item.freshness !== "bilinmiyor" && (
        <div className="border border-hairline bg-background p-4">
          {/* `uyari` → rakamın ALTINA ince turuncu dalgalı çizgi. Rozetten FARKLI bir
              görsel kanal (renk+alt çizgi vs. emoji) — ikisi yarışmaz, üst üste binmez. */}
          {item.freshness === "uyari" && (
            <p
              className="mb-2 font-mono text-[10px] text-amber-500 decoration-amber-500 decoration-wavy underline underline-offset-4"
              title={item.tazelik_aciklama ?? undefined}
            >
              veri eskimiş olabilir
            </p>
          )}
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

      {/* FAZ 1.12 · AI ACT Md.50 — **AI İÇERİK İŞARETLEME.**

          🔴 İşaretlenen şey SAYI DEĞİL, ÜSLUP'tur. Sayıyı bu üründe her zaman küp koyar ve
          `narration_guard` eşleşmeyen sayı taşıyan cümleyi DÜŞÜRÜR — yani sayı zaten makine
          üretimi bir metnin insafına bırakılmaz. Md.50'nin istediği, METNİN makine tarafından
          yazıldığının okuyucuya söylenmesidir.

          ⚠ İşaret ANLATININ YANINDA durur, kartın tepesinde değil: tepede duran bir rozet
          "bu cevabın TAMAMI yapay zekâ ürünü" diye okunurdu ve bu YANLIŞ olurdu — tablo,
          sayı ve kırılım deterministik küpten gelir.

          Karar backend'de (`answer.seal`); burada ikinci bir çıkarım yapılmaz. */}
      {item.ai_generated_prose && (
        <p
          className="mx-auto mt-1 flex max-w-4xl items-center gap-1.5 px-8 font-mono text-[10px] tracking-wide text-neutral-400"
          title="Yukarıdaki AÇIKLAMA METNİ yapay zekâ tarafından yazıldı (AB Yapay Zekâ Yasası Md.50). Sayılar ve tablo bu metinden DEĞİL, doğrudan semantik küpten gelir; metindeki eşleşmeyen sayılar yayımlanmadan önce düşürülür."
        >
          <span aria-hidden>✎</span>
          açıklama metni yapay zekâ ürünü — sayılar küpten gelir
        </p>
      )}

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
        <PrescriptionLayer
          recete={item.prescription}
          onCubeEdit={onCubeEdit}
          soru={item.question}
          sessionId={sessionId}
          // Kanıt bağı: karar, dayandığı makbuza bağlanınca YENİDEN ÇALIŞTIRILABİLİR
          // bir iddiaya dönüşür. Kanıtsız kayıt da meşrudur ama farklıdır.
          contractIds={item.contract_id ? [item.contract_id] : []}
          // FAZ 5.8 — ŞABLON: `contract_ids` o günün sayısını DONDURUR, `cube_query`
          // aynı analizi BUGÜN koşulabilir kılar. İkisi farklı sorular cevaplar.
          cubeQuery={item.cube_query ?? null}
        />
      )}

      {item.cube_query && (item.result || item.contribution) && (
        <ContributionLayer
          cubeQuery={item.cube_query}
          sessionId={sessionId}
          onCubeEdit={onCubeEdit}
          hazir={item.contribution ?? null}
        />
      )}

      {/* DEVAM SORUSU chip'leri (`suggestions`) — FAZ D2.
          ⚠️ ÖLÇÜLEN YETİM ALAN: `suggestions` yalnız `ReportPanel`'in NOT dalında
          render ediliyordu. Bir RAPOR kartı geldiğinde (source=cube + sonuç) bu alan
          hiç okunmuyordu — yani "bunu analiz et" cevabının ürettiği "Neden böyle?" /
          "Normal mi?" / "Ne yapmalıyız?" chip'leri EKRANDA GÖRÜNMÜYORDU.
          `test_cevap_alani_yetim_degil` bunu göremedi çünkü alan adı frontend'de BİR
          yerde geçiyordu; kapının kör noktası "hangi RENDER YOLUNDA" sorusuydu.
          `next_steps`ten AYRI durur: o sorguyu DÜZENLER (`cube_query` taşır), bu ise
          bir SORU sorar — ikisi farklı eylemdir ve aynı kutuya konursa kullanıcı
          hangisinin yeni sayı getireceğini bilemez. */}
      {onReply && (item.suggestions?.length ?? 0) > 0 && (
        <div className="mt-3">
          <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
            devam sorusu
          </div>
          <div className="flex flex-wrap gap-1.5">
            {item.suggestions!.map((s, i) => (
              <button
                key={`sug-${i}`}
                onClick={() => onReply(threadId, index, s.query)}
                title="Bu cevabın üstünde konuşur — yeni sorgu yazılmaz"
                className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-600 transition-colors hover:border-accent/50 hover:text-foreground dark:text-neutral-300"
              >
                <span className="mr-1 text-neutral-400">↳</span>
                {s.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* K2 sonraki adım chip'leri (backend 'next_steps' flag'iyle gelir) — kırılım/ölçek/
          zaman. Tıklama mevcut deterministik /cube yolunu kullanır (LLM yok). */}
      {/* Konuşma cevabında (`contribution` dolu) bu blok GİZLENİR: bulgular cevabın
          GÖVDESİDİR ve yukarıda zengin haliyle duruyor. Burada da göstermek aynı listeyi
          İKİ KEZ, üstelik ikincisini YANLIŞ BAŞLIKLA ("sonraki adım") sunardı. */}
      {!item.contribution && onCubeEdit && (
        <NextStepChips steps={item.next_steps} onCubeEdit={onCubeEdit} />
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
