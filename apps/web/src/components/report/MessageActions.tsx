"use client";

import { useState } from "react";
import { Bell, Check, Download, X } from "lucide-react";
import type { AskResponse } from "@dima/contracts";
import {
  createSchedule,
  verifyReport,
  type AnomalyAlarm,
  type ThresholdAlarm,
} from "@dima/api-client";
import { useFeature, usePermission } from "@/lib/access";
import { Button } from "@dima/ui/primitives/button";
import { Input } from "@dima/ui/primitives/input";
import { Label } from "@dima/ui/primitives/label";
import { Popover, PopoverContent, PopoverTrigger } from "@dima/ui/primitives/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@dima/ui/primitives/select";
import { Separator } from "@dima/ui/primitives/separator";
import { Textarea } from "@dima/ui/primitives/textarea";
import { ToggleGroup, ToggleGroupItem } from "@dima/ui/primitives/toggle-group";
import { Tooltip, TooltipContent, TooltipTrigger } from "@dima/ui/primitives/tooltip";
import { CopyIcon } from "@dima/ui/ai/copy-icon";
import { AddToDashboard } from "@/components/report/AddToDashboard";
import { fileNameFor, resultToCsv } from "@/lib/export";
import { downloadDocument, useDocuments } from "@/stores/documents";
import { cn } from "@dima/ui/utils";

const SCHEDULE_PRESETS = [
  { name: "her sabah 08:00 · dünün verisi", every: "day" as const, at: "08:00", period: "dün" },
  { name: "her saat · bugünün verisi", every: "hour" as const, period: "bugün" },
  {
    name: "her pazartesi 08:00 · geçen hafta",
    every: "week" as const,
    at: "08:00",
    weekday: 1,
    period: "geçen hafta",
  },
];

type AlarmType = "none" | "threshold" | "anomaly";

/**
 * Cevabın ALTINDAKİ aksiyon şeridi (ChatGPT/Claude tarzı): doğru · yanlış ·
 * zamanla · kopyala. Görünürlük backend'den gelir — özellik bayrağı (`useFeature`)
 * ⊕ izin (`usePermission`); rol matrisi UI'a kopyalanmaz. Eskiden sağ paneldeydi.
 */
export function MessageActions({
  data,
  verifyLabel,
  sessionId,
  conversationId,
  className,
}: {
  data: AskResponse;
  verifyLabel?: string | null;
  sessionId?: string;
  /** Üretilen belge hangi sohbete ait — sohbet kapsamlı Belgeler bunu süzer. */
  conversationId?: string;
  className?: string;
}) {
  const [scheduled, setScheduled] = useState(false);
  const [fb, setFb] = useState<"ok" | "bad" | null>(null);
  const [copied, setCopied] = useState(false);
  const [exported, setExported] = useState(false);
  const addDocument = useDocuments((st) => st.add);

  const schedStage = useFeature("scheduled_reports");
  const verifyStage = useFeature("verify_button");
  const dashStage = useFeature("dashboards");
  const canSchedule = usePermission("schedule:create");
  const canVerify = usePermission("vqr:write");

  // Raporu üreten son GERÇEK soru (chip etiketi değil) — verify bu metinle öğrenir.
  const vLabel = data.question.startsWith("chip:") ? (verifyLabel ?? data.question) : data.question;
  const verified = fb === "ok";
  const flagged = fb === "bad";

  const showSchedule = schedStage && canSchedule && data.cube_query && data.source;
  const showVerify = verifyStage && canVerify && data.cube_query && data.source;

  // Alarmın bakacağı ölçüler raporun KENDİ cube_query'sinden gelir — kullanıcı
  // burada serbest metin yazmasın, var olmayan ölçüye alarm kurulmasın.
  const measures = (data.cube_query?.measures as string[] | undefined) ?? [];

  const [wrongOpen, setWrongOpen] = useState(false);
  const [comment, setComment] = useState("");
  const [schedOpen, setSchedOpen] = useState(false);
  const [alarmType, setAlarmType] = useState<AlarmType>("none");
  const [alarmMeasure, setAlarmMeasure] = useState("");
  const [alarmOp, setAlarmOp] = useState<"gt" | "lt">("gt");
  const [alarmValue, setAlarmValue] = useState("");
  const [emails, setEmails] = useState("");

  const schedule = (preset: (typeof SCHEDULE_PRESETS)[number]) => {
    if (!data.cube_query) return;
    // Zamanlanmış rapor GÖRELİ dönemle koşar ("dün"), bu yüzden raporu üreten
    // mutlak tarih filtresi düşürülür — yoksa her koşumda aynı geçmiş pencere gelirdi.
    const cq = {
      ...data.cube_query,
      filters: ((data.cube_query.filters as { dimension: string }[] | undefined) ?? []).filter(
        (f) => f.dimension !== "tarih",
      ),
    };
    if (!(cq.filters as unknown[]).length) delete (cq as Record<string, unknown>).filters;

    const measure = alarmMeasure || measures[0] || "";
    let threshold: ThresholdAlarm | AnomalyAlarm | null = null;
    if (alarmType === "threshold" && measure && alarmValue.trim() !== "") {
      const value = Number(alarmValue);
      if (!Number.isNaN(value)) threshold = { measure, op: alarmOp, value };
    } else if (alarmType === "anomaly" && measure) {
      threshold = { measure, method: "zscore" };
    }

    const to = emails
      .split(",")
      .map((e) => e.trim())
      .filter((e) => e.includes("@"));

    createSchedule({
      label: vLabel,
      cube_query: cq,
      period: preset.period,
      every: preset.every,
      at: preset.at,
      weekday: preset.weekday,
      threshold,
      delivery: to.length ? { email: { to } } : null,
    })
      .then(() => {
        setScheduled(true);
        setSchedOpen(false);
      })
      .catch(() => {});
  };

  const doVerify = () => {
    if (!data.cube_query) return;
    verifyReport(data.cube_query, vLabel, { undo: verified || undefined, session_id: sessionId })
      .then(() => setFb(verified ? null : "ok"))
      .catch(() => {});
  };

  const submitWrong = () => {
    if (!data.cube_query || flagged) return;
    verifyReport(data.cube_query, vLabel, {
      verdict: "wrong",
      session_id: sessionId,
      comment: comment.trim() || undefined,
    })
      .then(() => {
        setFb("bad");
        setWrongOpen(false);
        setComment("");
      })
      .catch(() => {});
  };

  // Dosyayı TARAYICI üretir: satırlar zaten burada ve backend'de dışa aktarma
  // ucu yok (dima-backend HEAD'de doğrulandı). Uç eklendiğinde değişen tek şey
  // blob'un kaynağı olur — belge modeli ve bu düğme aynı kalır.
  const exportCsv = () => {
    if (!data.result) return;
    const blob = resultToCsv(data.result);
    const name = fileNameFor(vLabel, "csv");
    const id = addDocument({
      name,
      origin: "generated",
      kind: "csv",
      size: blob.size,
      conversationId,
      question: vLabel,
      contractId: data.contract_id ?? null,
      blob,
    });
    downloadDocument({
      id,
      name,
      origin: "generated",
      kind: "csv",
      size: blob.size,
      createdAt: Date.now(),
      blob,
    });
    setExported(true);
  };

  const copy = () => {
    const text = data.sql ?? data.note ?? data.question;
    void navigator.clipboard?.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };

  if (!showSchedule && !showVerify && !dashStage && !data.result && !data.sql) return null;

  const alarmMeasureValue = alarmMeasure || measures[0] || "";

  return (
    <div className={cn("flex flex-wrap items-center gap-0.5 pt-0.5", className)}>
      {showVerify && (
        <>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                onClick={doVerify}
                aria-label="doğru"
                className={cn(
                  "h-7 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground",
                  verified && "text-emerald-600 dark:text-emerald-400",
                )}
              >
                <Check className="size-3.5" />
                {verified ? "öğrenildi" : "doğru"}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              {verified
                ? "Doğrulamayı geri al"
                : "Doğru olarak işaretle — aynı soru bundan sonra LLM'siz cevaplanır"}
            </TooltipContent>
          </Tooltip>

          {/* "✗ yanlış" doğrudan göndermez: önce OPSİYONEL gerekçe sorulur.
              Yorumsuz gönderim tek tık uzakta kalır — zorunlu form geri bildirimi
              öldürür, ama "neden yanlış" olmadan negatif sinyal yalnız "bir şey
              bozuk" demektir. */}
          <Popover
            open={wrongOpen}
            onOpenChange={(o) => {
              if (flagged) return;
              setWrongOpen(o);
              if (!o) setComment("");
            }}
          >
            <Tooltip>
              <TooltipTrigger asChild>
                <PopoverTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    aria-label="yanlış"
                    className={cn(
                      "h-7 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground",
                      flagged && "text-destructive",
                    )}
                  >
                    <X className="size-3.5" />
                    {flagged ? "kaydedildi" : "yanlış"}
                  </Button>
                </PopoverTrigger>
              </TooltipTrigger>
              <TooltipContent side="bottom">
                Yanlış — kayda geçer; öğrenilmiş yakın çift varsa silinir
              </TooltipContent>
            </Tooltip>
            <PopoverContent align="start" className="w-72 space-y-2 p-3">
              <Label
                htmlFor="verify-comment"
                className="font-mono text-[10px] tracking-wider text-muted-foreground uppercase"
              >
                neden yanlış? (opsiyonel)
              </Label>
              <Textarea
                id="verify-comment"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows={3}
                placeholder="ör. yanlış ölçü / eksik kırılım / dönem hatalı…"
                className="resize-none text-xs"
              />
              <div className="flex gap-1.5">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={submitWrong}
                  className="h-7 flex-1 border-destructive/40 text-xs text-destructive hover:bg-destructive/5 hover:text-destructive"
                >
                  {comment.trim() ? "yorumla gönder" : "yorumsuz gönder"}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setWrongOpen(false);
                    setComment("");
                  }}
                  className="h-7 px-2 text-xs text-muted-foreground"
                >
                  vazgeç
                </Button>
              </div>
            </PopoverContent>
          </Popover>
        </>
      )}

      {showSchedule && (
        <Popover open={schedOpen} onOpenChange={setSchedOpen}>
          <Tooltip>
            <TooltipTrigger asChild>
              <PopoverTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  aria-label="zamanla"
                  className={cn(
                    "h-7 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground",
                    scheduled && "text-brand",
                  )}
                >
                  <Bell className="size-3.5" />
                  {scheduled ? "zamanlandı" : "zamanla"}
                </Button>
              </PopoverTrigger>
            </TooltipTrigger>
            <TooltipContent side="bottom">Bu raporu düzenli olarak çalıştır</TooltipContent>
          </Tooltip>
          <PopoverContent align="start" className="w-80 space-y-3 p-3">
            {/* Alarm (opsiyonel) — rapor her koşumda gelir; alarm yalnız KOŞUL
                sağlanınca uyarı üretir. Sabit sınırın olmadığı ölçülerde (fire,
                duruş) anomali kipi z-skoruyla "olağandışı"yı yakalar. */}
            {measures.length > 0 && (
              <div className="space-y-2">
                <Label className="font-mono text-[10px] tracking-wider text-muted-foreground uppercase">
                  alarm (opsiyonel)
                </Label>
                <ToggleGroup
                  type="single"
                  size="sm"
                  variant="outline"
                  value={alarmType}
                  onValueChange={(v) => v && setAlarmType(v as AlarmType)}
                  className="w-full"
                >
                  <ToggleGroupItem value="none" className="flex-1 px-2 text-xs">
                    yok
                  </ToggleGroupItem>
                  <ToggleGroupItem value="threshold" className="flex-1 px-2 text-xs">
                    eşik
                  </ToggleGroupItem>
                  <ToggleGroupItem value="anomaly" className="flex-1 px-2 text-xs">
                    anomali
                  </ToggleGroupItem>
                </ToggleGroup>

                {alarmType !== "none" && (
                  <div className="flex items-center gap-1.5">
                    <Select
                      value={alarmMeasureValue}
                      onValueChange={setAlarmMeasure}
                    >
                      <SelectTrigger size="sm" className="h-7 min-w-0 flex-1 text-xs" aria-label="Alarm ölçüsü">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {measures.map((m) => (
                          <SelectItem key={m} value={m} className="text-xs">
                            {m}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>

                    {alarmType === "threshold" ? (
                      <>
                        <Select value={alarmOp} onValueChange={(v) => setAlarmOp(v as "gt" | "lt")}>
                          <SelectTrigger size="sm" className="h-7 w-14 text-xs" aria-label="Karşılaştırma">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="gt" className="text-xs">
                              &gt;
                            </SelectItem>
                            <SelectItem value="lt" className="text-xs">
                              &lt;
                            </SelectItem>
                          </SelectContent>
                        </Select>
                        <Input
                          value={alarmValue}
                          onChange={(e) => setAlarmValue(e.target.value)}
                          inputMode="decimal"
                          placeholder="değer"
                          aria-label="Eşik değeri"
                          className="h-7 w-20 text-xs"
                        />
                      </>
                    ) : (
                      <span className="shrink-0 text-xs text-muted-foreground">
                        z-skoru (olağandışı)
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* E-posta teslim (opsiyonel) — uygulama içi zil HER ZAMAN düşer. */}
            <div className="space-y-1.5">
              <Label
                htmlFor="schedule-emails"
                className="font-mono text-[10px] tracking-wider text-muted-foreground uppercase"
              >
                e-posta (opsiyonel)
              </Label>
              <Input
                id="schedule-emails"
                value={emails}
                onChange={(e) => setEmails(e.target.value)}
                placeholder="ali@firma.com, ayse@firma.com"
                className="h-7 text-xs"
              />
            </div>

            <Separator />

            {/* Periyot seçimi zamanlamayı KURAR — yukarıdaki alarm/e-posta ayarları
                seçilen preset'le birlikte gönderilir. */}
            <div className="space-y-0.5">
              <Label className="font-mono text-[10px] tracking-wider text-muted-foreground uppercase">
                ne sıklıkla
              </Label>
              {SCHEDULE_PRESETS.map((pr) => (
                <Button
                  key={pr.name}
                  variant="ghost"
                  size="sm"
                  onClick={() => schedule(pr)}
                  className="h-7 w-full justify-start px-2 text-xs font-normal text-muted-foreground hover:text-foreground"
                >
                  {pr.name}
                </Button>
              ))}
            </div>
          </PopoverContent>
        </Popover>
      )}

      {/* Panoya sabitle — bayrak `dashboards`; sonuç değil SORGU kaydedilir. */}
      {dashStage && <AddToDashboard data={data} label={vLabel} />}

      {/* Dışa aktar — dosya İSTEMCİDE üretilir (backend'de dışa aktarma ucu yok),
          Belgeler'e ÜRETİLEN rozetiyle düşer. */}
      {data.result && data.result.row_count > 0 && (
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              onClick={exportCsv}
              aria-label="dışa aktar"
              className={cn(
                "h-7 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground",
                exported && "text-brand",
              )}
            >
              <Download className="size-3.5" />
              {exported ? "belgelerde" : "dışa aktar"}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="bottom">
            Sonucu CSV olarak üret — Belgeler&apos;e eklenir ve indirilir
          </TooltipContent>
        </Tooltip>
      )}

      {data.sql && (
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              onClick={copy}
              aria-label="SQL'i kopyala"
              className="h-7 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground"
            >
              <CopyIcon copied={copied} />
              {copied ? "kopyalandı" : "kopyala"}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="bottom">SQL&apos;i panoya kopyala</TooltipContent>
        </Tooltip>
      )}
    </div>
  );
}
