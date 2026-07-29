"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import type { AskResponse, CubeQuery } from "@dima/contracts";
import { chartDensity } from "@dima/domain";
import { Composer } from "@/components/shell/Composer";
import { InterpretationBar } from "@/components/InterpretationBar";
import { SourceBadge } from "@/components/report/SourceBadge";
import { MessageActions } from "@/components/report/MessageActions";
import { NextSteps, Recommendations } from "@/components/report/NextSteps";
import { ResultCard } from "@/components/report/ResultCard";
import { SqlBlock } from "@/components/report/SqlBlock";
import { KpiCardView } from "@/components/KpiCard";
import { OutputInsight } from "@/components/OutputInsight";
import { Bubble, DimaAvatar, Message, MessageScroller, UserAvatar } from "@/components/ai/chat";
import { ChainOfThought, Reasoning } from "@/components/ai/thinking";
import { thinkingMs } from "@/lib/thinking";
import { attachmentsOf } from "@/lib/attachments";
import { datasetOf } from "@/lib/dataset";
import { DatasetCard } from "@/components/report/DatasetCard";
import { Attachment } from "@/components/ai/attachment";
import { Badge } from "@/components/ui/badge";
import { useFeature } from "@/lib/access";
import { cn } from "@/lib/utils";

/** Mesajla gönderilen ekler — balonun altında, yatay kaydırmalı. */
function MessageAttachments({ files }: { files?: File[] }) {
  if (!files?.length) return null;
  return (
    <div className="flex max-w-full items-center gap-1.5 overflow-x-auto pb-0.5">
      {files.map((f, i) => (
        <Attachment key={`${f.name}-${i}`} file={f} className="shrink-0 scale-95" />
      ))}
    </div>
  );
}

export function ChatPanel({
  items,
  active,
  pending,
  pendingQuestion,
  pendingFiles,
  conversationId,
  onSelect,
  onSubmit,
  onCubeEdit,
  verifyLabel,
  sessionId,
  focus,
}: {
  items: AskResponse[];
  active: AskResponse | null;
  pending: boolean;
  pendingQuestion?: string;
  pendingFiles?: File[];
  /** Aktif sohbetin kimliği — sohbet değişince kaydırma anlık olmalı. */
  conversationId?: string;
  onSelect: (item: AskResponse) => void;
  onSubmit: (q: string, files?: File[]) => void;
  onCubeEdit?: (edit: { cq: CubeQuery; label: string }) => void;
  verifyLabel?: string | null;
  sessionId?: string;
  /** Sağ panelden seçilen sonuç — o karta kaydır ve kısaca vurgula.
   *  `nonce` aynı karta ikinci kez basıldığında da tetiklensin diye. */
  focus?: { item: AskResponse; nonce: number } | null;
}) {
  const t = useTranslations();
  const [value, setValue] = useState("");
  const thread = [...items].reverse(); // eski üstte, yeni altta
  // SQL gösterimi (sql_display bayrağı, ADR-0009) — ham şeffaflık özelliği; bayrak
  // kapalıysa SQL bloğu hiç render edilmez (backend /features'tan çözülür).
  // SQL gösterimi (sql_display, ADR-0009). Bayrak YOKKEN varsayılan AÇIK:
  // deterministik-önce bir üründe sorguyu görebilmek güven yüzeyinin parçası,
  // gizlemek istisna olmalı. Backend "off" döndürürse kapanır — böylece
  // tenant bazlı kapatma imkânı korunuyor, ama sessizce kaybolmuyor.
  // NOT: "off", alpha|beta|prod sözlüğüne EK bir değer; backend registry'sine
  // eklenmeli, yoksa bu dal hiç tetiklenmez.
  const sqlStage = useFeature("sql_display");
  const showSql = sqlStage !== "off";

  const send = (files: File[]) => {
    const q = value.trim();
    if (!q) return;
    onSubmit(q, files);
    setValue("");
  };

  return (
    // Sohbet, üstteki bar ve alttaki komut satırının ALTINDAN akar; ikisi de
    // overlay. Bu yüzden kaydırma alanı tam yükseklik, boşluklar içeride padding.
    <div className="relative flex h-full min-h-0 flex-col">
      {/* Üstte yumuşak erime: içerik bara doğru yaklaşırken saydamlaşır (Claude
          davranışı). Blur'lu opak bir bant yerine maske — böylece "arkasında bir
          panel var" hissi değil, "yazı sönümleniyor" hissi oluşuyor. */}
      <MessageScroller
        className="[mask-image:linear-gradient(to_bottom,transparent_0,#000_4rem)]"
        jumpOffset="bottom-[7rem]"
        // yeni cevap (ya da chip düzenlemesi) gelince en alta zorla kaydır
        // "::" öncesi sohbet kimliği (değişirse anlık atla), sonrası mesaj
        // sayısı/bekleyen soru (aynı sohbette değişirse yumuşak kaydır)
        scrollKey={`${conversationId ?? ""}::${items.length}:${pendingQuestion ?? ""}`}
      >
        {/* Tek ritim: hem turlar arasında hem tur içinde space-y-9 (36px).
            Eşit boşluk, konuşmayı "soru+cevap blokları" yerine tek bir akış gibi
            okutur — ChatGPT/Claude deseni. Gruplamayı boşluk değil, avatar ve
            hizalama taşıyor. */}
        {/* `@container`: genişleyen sonuç kartı, kullanılabilir genişliği `cqw` ile
            ÖLÇEREK büyür. Yüzde ya da negatif kenar boşluğu kullansaydık, sağ panel
            açıkken ya da dar ekranda taşar ve yatay kaydırma doğardı (DESIGN.md
            bunu yasaklıyor). `min()` ile kart hiçbir koşulda kabı aşamaz. */}
        <div className="@container w-full space-y-9 pt-16 pb-36">
          {thread.map((item, i) => (
            <ChatTurn
              key={`${item.question}-${i}`}
              item={item}
              active={active === item}
              showSql={showSql}
              onSubmit={onSubmit}
              onSelect={onSelect}
              onCubeEdit={onCubeEdit}
              verifyLabel={verifyLabel}
              sessionId={sessionId}
              conversationId={conversationId}
              focusNonce={focus?.item === item ? focus.nonce : null}
              t={t}
            />
          ))}

          {pendingQuestion && (
            <div className="mx-auto w-full max-w-3xl space-y-9 px-4">
              <Message from="user" className="items-start gap-3 pl-10">
                <div className="flex min-w-0 max-w-[calc(100%-2.5rem)] flex-col items-end gap-1.5">
                  <MessageAttachments files={pendingFiles} />
                  <Bubble from="user">{pendingQuestion}</Bubble>
                </div>
                <UserAvatar className="mt-0.5 shrink-0" />
              </Message>
              <Message from="assistant" className="items-start gap-3 pr-10">
                <DimaAvatar className="mt-0.5 shrink-0" thinking />
                <ChainOfThought />
              </Message>
            </div>
          )}
        </div>
      </MessageScroller>

      {/* komut satırı — sohbetin ÜSTÜNDE yüzer, arkasından içerik geçer.
          Zemin bandı yok; ayrımı yalnız kartın kendi gölgesi yapıyor. */}
      <div className="pointer-events-none absolute inset-x-0 bottom-0 z-10">
        <div className="pointer-events-auto mx-auto w-full max-w-3xl px-4 pb-3">
          <Composer
            value={value}
            onChange={setValue}
            onSubmit={send}
            busy={pending}
          />
        </div>
      </div>
    </div>
  );
}

/**
 * Tek sohbet turu (soru + cevap). Kendi bileşeni çünkü GENİŞLİK durumu tur
 * başına: kart genişlediğinde büyüyen şey kartın kendisi değil, turu saran
 * kolondur (kaydırma alanı `overflow-auto`; negatif kenar boşluğuyla taşırmak
 * yatay kaydırma doğururdu — DESIGN.md bunu yasaklıyor).
 */
function ChatTurn({
  item,
  active,
  showSql,
  onSubmit,
  onSelect,
  onCubeEdit,
  verifyLabel,
  sessionId,
  conversationId,
  focusNonce,
  t,
}: {
  item: AskResponse;
  active: boolean;
  showSql: boolean;
  onSubmit: (q: string, files?: File[]) => void;
  onSelect: (item: AskResponse) => void;
  onCubeEdit?: (edit: { cq: CubeQuery; label: string }) => void;
  verifyLabel?: string | null;
  sessionId?: string;
  conversationId?: string;
  /** Bu tura odaklanma isteği (değeri değişince kaydır). */
  focusNonce?: number | null;
  t: ReturnType<typeof useTranslations>;
}) {
  // Varsayılan genişliği VERİ belirler: dar sütuna sığmayan sonuç (çok panel,
  // uzun kategori ekseni, çok seri) zaten okunmuyor — kullanıcıyı her seferinde
  // genişlet'e basmaya zorlamak bilinen bir sorunu ona havale etmek olurdu.
  const [wide, setWide] = useState(() =>
    item.result ? chartDensity(item.result) === "dense" : false,
  );
  const dataset = datasetOf(item);

  // Sağ paneldeki Paneller listesinden gelen "buna git" isteği: karta kaydır ve
  // kısa bir halka ile işaretle. Vurgu SÜREKLİ değil — kullanıcıyı nereye
  // baktığına dair bilgilendirir, sonra kendini siler.
  const ref = useRef<HTMLDivElement>(null);
  const [flash, setFlash] = useState(false);
  // Yeni bir odak isteği RENDER SIRASINDA yakalanır (Chart'taki `signature`
  // deseni). Effect içinde senkron setState yapmak zincirleme render tetikler;
  // burada effect yalnız yan etkiyi (kaydırma) ve zamanlayıcıyı üstlenir.
  const [seenNonce, setSeenNonce] = useState<number | null>(null);
  if (focusNonce != null && focusNonce !== seenNonce) {
    setSeenNonce(focusNonce);
    setFlash(true);
  }
  useEffect(() => {
    if (!flash) return;
    ref.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    const id = setTimeout(() => setFlash(false), 1600);
    return () => clearTimeout(id);
  }, [flash]);

  // TUR HİÇ GENİŞLEMEZ. Soru balonu, yorum çubuğu (kırılım chip'leri), not
  // balonu ve aksiyon şeridi hep aynı sütunda kalır — genişleyen TEK şey sonuç
  // kartıdır. Turu büyütmek hepsini birlikte kaydırıyordu.
  //
  // `px-4` KOMUT SATIRIYLA HİZA İÇİN: composer da `max-w-3xl px-4`. Tur bu
  // dolguyu almadığında içerik kutusu 32px daha geniş kalıyor ve avatarlar
  // komut satırının kenarından taşıyordu.
  return (
    <div
      ref={ref}
      className={cn(
        "mx-auto w-full max-w-3xl space-y-9 px-4",
        // scroll-margin: kart üstteki bara girmesin
        "scroll-mt-20",
      )}
    >
            <Message from="user" className="items-start gap-3 pl-10">
              <div className="flex min-w-0 max-w-[calc(100%-2.5rem)] flex-col items-end gap-1.5">
                <MessageAttachments files={attachmentsOf(item)} />
                <Bubble from="user">{item.question}</Bubble>
              </div>
              <UserAvatar className="mt-0.5 shrink-0" />
            </Message>

            <Message from="assistant" className="items-start gap-3 pr-10">
              <DimaAvatar className="mt-0.5 shrink-0" />
              <Bubble from="assistant" className="space-y-2">
                {/* düşünce zinciri cevabın yanında kalır — varsayılan kapalı */}
                {thinkingMs(item) !== undefined && <Reasoning durationMs={thinkingMs(item)} trace={item.trace} />}
                {/* Bağlanan veri kümesi (D1/D2/D36) — yükleme sohbetin bir olayı. */}
                {dataset && <DatasetCard data={dataset} onPick={onSubmit} />}
                {/* KPI yanıtı NOT taşısa da bir RAPORDUR (kart) — salt-not gibi
                    davranıp gömmüyoruz (canlı 2026-07-25). */}
                {/* Cross-cube KPI kartı (CCC / likidite) — cube tablosu değil bileşke. */}
                {item.kpi && <KpiCardView card={item.kpi} />}
                {dataset ? null : item.note && !item.kpi ? (
                  <div className="rounded-lg border-l-2 border-brand/50 bg-brand/[0.04] py-2 pr-2 pl-3">
                    {/* Not, cevabın KENDİSİ — ikincil metadata değil. Bu yüzden
                        `foreground`: muted tonu okunurluğu düşürüyordu. */}
                    <p className="text-sm leading-relaxed text-foreground">{item.note}</p>
                    {item.suggestions && item.suggestions.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {item.suggestions.map((s) => (
                          <button key={s.label} type="button" onClick={() => onSubmit(s.query)}>
                            <Badge
                              variant="outline"
                              className="cursor-pointer font-normal hover:border-brand/40 hover:bg-brand/5"
                            >
                              {s.label}
                            </Badge>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ) : item.result ? (
                  <>
                    {/* Yorum çubuğu artık sohbetin içinde — sağ panelde kopyası yok. */}
                    {item.cube_query && onCubeEdit && (
                      <InterpretationBar cq={item.cube_query} onEdit={onCubeEdit} />
                    )}
                    {/* Tek başlık satırı: rozet + satır sayısı solda, grafik/tablo
                        kontrolleri ve boyut düğmeleri sağda. */}
                    <ResultCard
                      result={item.result}
                      viewHint={item.view_hint ?? undefined}
                      wide={wide}
                      onWideChange={setWide}
                      className={cn((active || flash) && "ring-1 ring-brand/30", flash && "ring-2 ring-brand/60")}
                      meta={
                        <>
                          <SourceBadge source={item.source} />
                          <span className="text-xs text-muted-foreground">
                            {t("chat.rows", { count: item.result.row_count })}
                          </span>
                        </>
                      }
                    >
                      {/* sorgunun kendisi — grafiğin/tablonun altında, kapalı başlar
                          (sql_display bayrağı açıksa) */}
                      {showSql && item.sql && <SqlBlock sql={item.sql} />}
                    </ResultCard>
                    <MessageActions
                      data={item}
                      verifyLabel={verifyLabel}
                      sessionId={sessionId}
                      conversationId={conversationId}
                    />
                  </>
                ) : (
                  <button
                    type="button"
                    onClick={() => onSelect(item)}
                    className="flex w-full items-center gap-2 rounded-lg border border-border px-3 py-2 text-left transition-colors hover:bg-accent"
                  >
                    <span className="font-mono text-[11px] text-muted-foreground">
                      {item.kpi ? "KPI kartı" : "SQL"}
                    </span>
                    <span className="ml-auto">
                      <SourceBadge source={item.source} />
                    </span>
                  </button>
                )}
                {/* Evrensel çıktı yorumu + K3 proaktif sinyaller — KPI/tablo/grafik/
                    rapor hepsinin altında (flag'li). */}
                <OutputInsight interpretation={item.interpretation} />
                {/* K4 önce gelir: sinyal "ne oldu"yu söyledi, öneri "ne yapmalı"yı
                    söyler; K2 chip'leri ise serbest keşif — dar olandan geniş olana. */}
                {onCubeEdit && (
                  <>
                    <Recommendations items={item.recommendations} onDrill={onCubeEdit} />
                    <NextSteps steps={item.next_steps} onDrill={onCubeEdit} />
                  </>
                )}
              </Bubble>
            </Message>
    </div>
  );
}
