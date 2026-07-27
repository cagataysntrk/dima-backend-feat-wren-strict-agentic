"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import type { AskResponse, CubeQuery } from "@/lib/types";
import { Composer } from "@/components/shell/Composer";
import { ResultView } from "@/components/ResultView";
import { InterpretationBar } from "@/components/InterpretationBar";
import { SourceBadge } from "@/components/report/SourceBadge";
import { MessageActions } from "@/components/report/MessageActions";
import { SqlBlock } from "@/components/report/SqlBlock";
import { KpiCardView } from "@/components/KpiCard";
import { OutputInsight } from "@/components/OutputInsight";
import { Bubble, DimaAvatar, Message, MessageScroller, UserAvatar } from "@/components/ai/chat";
import { ChainOfThought, Reasoning } from "@/components/ai/thinking";
import { thinkingMs } from "@/lib/thinking";
import { attachmentsOf } from "@/lib/attachments";
import { Attachment } from "@/components/ai/attachment";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
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
  onSelect,
  onSubmit,
  onCubeEdit,
  verifyLabel,
  sessionId,
}: {
  items: AskResponse[];
  active: AskResponse | null;
  pending: boolean;
  pendingQuestion?: string;
  pendingFiles?: File[];
  onSelect: (item: AskResponse) => void;
  onSubmit: (q: string, files?: File[]) => void;
  onCubeEdit?: (edit: { cq: CubeQuery; label: string }) => void;
  verifyLabel?: string | null;
  sessionId?: string;
}) {
  const t = useTranslations();
  const [value, setValue] = useState("");
  const thread = [...items].reverse(); // eski üstte, yeni altta
  // SQL gösterimi (sql_display bayrağı, ADR-0009) — ham şeffaflık özelliği; bayrak
  // kapalıysa SQL bloğu hiç render edilmez (backend /features'tan çözülür).
  const sqlStage = useFeature("sql_display");

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
        scrollKey={`${items.length}:${pendingQuestion ?? ""}`}
      >
        {/* Tek ritim: hem turlar arasında hem tur içinde space-y-9 (36px).
            Eşit boşluk, konuşmayı "soru+cevap blokları" yerine tek bir akış gibi
            okutur — ChatGPT/Claude deseni. Gruplamayı boşluk değil, avatar ve
            hizalama taşıyor. */}
        <div className="mx-auto w-full max-w-3xl space-y-9 px-4 pt-16 pb-36">
          {thread.map((item, i) => (
            <div key={`${item.question}-${i}`} className="space-y-9">
              <Message from="user" className="items-start gap-3 pl-10">
                <div className="flex min-w-0 flex-col items-end gap-1.5">
                  <Bubble from="user">{item.question}</Bubble>
                  <MessageAttachments files={attachmentsOf(item)} />
                </div>
                <UserAvatar className="mt-0.5 shrink-0" />
              </Message>

              <Message from="assistant" className="items-start gap-3 pr-10">
                <DimaAvatar className="mt-0.5 shrink-0" />
                <Bubble from="assistant" className="space-y-2">
                  {/* düşünce zinciri cevabın yanında kalır — varsayılan kapalı */}
                  {thinkingMs(item) !== undefined && <Reasoning durationMs={thinkingMs(item)} />}
                  {/* KPI yanıtı NOT taşısa da bir RAPORDUR (kart) — salt-not gibi
                      davranıp gömmüyoruz (canlı 2026-07-25). */}
                  {/* Cross-cube KPI kartı (CCC / likidite) — cube tablosu değil bileşke. */}
                  {item.kpi && <KpiCardView card={item.kpi} />}
                  {item.note && !item.kpi ? (
                    <div className="rounded-lg border-l-2 border-brand/50 bg-brand/[0.04] py-2 pr-2 pl-3">
                      <p className="text-sm leading-snug text-muted-foreground">{item.note}</p>
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
                      <Card className={cn("gap-3 p-3", active === item && "ring-1 ring-brand/30")}>
                        {/* Tek başlık satırı: rozet + satır sayısı solda, grafik/tablo sağda.
                            ("Panelde aç" kaldırıldı — rapor artık sohbetin içinde yaşıyor.) */}
                        <ResultView
                          result={item.result}
                          viewHint={item.view_hint ?? undefined}
                          meta={
                            <>
                              <SourceBadge source={item.source} />
                              <span className="text-xs text-muted-foreground">
                                {t("chat.rows", { count: item.result.row_count })}
                              </span>
                            </>
                          }
                        />
                        {/* sorgunun kendisi — grafiğin/tablonun altında, kapalı başlar
                            (sql_display bayrağı açıksa) */}
                        {sqlStage && item.sql && <SqlBlock sql={item.sql} />}
                      </Card>
                      <MessageActions
                        data={item}
                        verifyLabel={verifyLabel}
                        sessionId={sessionId}
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
                  {/* Evrensel çıktı yorumu — KPI/tablo/grafik/rapor hepsinin altında (flag'li). */}
                  <OutputInsight interpretation={item.interpretation} />
                </Bubble>
              </Message>
            </div>
          ))}

          {pendingQuestion && (
            <div className="space-y-9">
              <Message from="user" className="items-start gap-3 pl-10">
                <div className="flex min-w-0 flex-col items-end gap-1.5">
                  <Bubble from="user">{pendingQuestion}</Bubble>
                  <MessageAttachments files={pendingFiles} />
                </div>
                <UserAvatar className="mt-0.5 shrink-0" />
              </Message>
              <Message from="assistant" className="items-start gap-3 pr-10">
                <DimaAvatar className="mt-0.5 shrink-0" />
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
