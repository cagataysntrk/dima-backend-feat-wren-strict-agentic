"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  BrainCircuit,
  ClipboardPenLine,
  LoaderCircle,
  RefreshCw,
  SlidersHorizontal,
} from "lucide-react";
import type { Analysis, AskResponse, CubeQuery, Preference, Report } from "@dima/contracts";
import {
  createPreference,
  deletePreference,
  generateReport,
  listPreferences,
  runAnalysis,
  type AnalysisKind,
  type ReportTemplate,
} from "@dima/api-client";

import { ResultView } from "@/components/ResultView";
import { Badge } from "@dima/ui/primitives/badge";
import { Button } from "@dima/ui/primitives/button";
import { Card } from "@dima/ui/primitives/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@dima/ui/primitives/dialog";
import { Input } from "@dima/ui/primitives/input";
import { Label } from "@dima/ui/primitives/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@dima/ui/primitives/select";
import { Separator } from "@dima/ui/primitives/separator";
import { useFeature } from "@/lib/access";
import { apiErrorMessage } from "@dima/api-client";

/**
 * CEO demo yetenek kapıları.
 *
 * Bunlar ŞİMDİLİK backend'de yok; her biri `useFeature` ile kapalıdır. Bu
 * bileşenleri şimdiden yazmak "sahte analiz" üretmez: bayrak yoksa DOM'a hiç
 * girmezler, endpoint de çağrılmaz. Backend contract geldiğinde yüzey kendiliğinden
 * açılır ve aynı typed istemciyi kullanır.
 */
function enabled(stage: string | null): boolean {
  return stage !== null && stage !== "off";
}

function cubeQueries(items: AskResponse[]): CubeQuery[] {
  return items.flatMap((item) => (item.cube_query ? [item.cube_query] : []));
}

export function DecisionTools({
  items,
  sessionId,
  onEvidence,
}: {
  items: AskResponse[];
  sessionId?: string;
  /** Analist iddiasındaki kanıta inmek için mevcut deterministik `/cube` yolu. */
  onEvidence?: (edit: { cq: CubeQuery; label: string }) => void;
}) {
  const reportStage = useFeature("rapor_uretimi");
  const analystStage = useFeature("analist");
  const memoryStage = useFeature("hafiza");

  if (!enabled(reportStage) && !enabled(analystStage) && !enabled(memoryStage)) return null;

  return (
    <section className="space-y-2" aria-label="Karar araçları">
      <Separator />
      <div className="flex flex-wrap gap-2">
        {enabled(reportStage) && <ReportBuilder items={items} sessionId={sessionId} />}
        {enabled(analystStage) && (
          <AnalystStudio items={items} sessionId={sessionId} onEvidence={onEvidence} />
        )}
        {enabled(memoryStage) && <PreferenceManager />}
      </div>
    </section>
  );
}

function ReportBuilder({ items, sessionId }: { items: AskResponse[]; sessionId?: string }) {
  const [open, setOpen] = useState(false);
  const [template, setTemplate] = useState<ReportTemplate>("uretim_ozeti");
  const [period, setPeriod] = useState("geçen hafta");
  const [report, setReport] = useState<Report | null>(null);
  const request = useMutation({
    mutationFn: () =>
      generateReport({
        template,
        period: period.trim() || null,
        session_id: sessionId,
        cube_queries: cubeQueries(items),
      }),
    onSuccess: setReport,
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-1.5">
          <ClipboardPenLine className="size-3.5" />
          rapor oluştur
          <BetaBadge />
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[88svh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>{report ? report.title : "Rapor oluştur"}</DialogTitle>
          <DialogDescription>
            Sayılar kayıtlı sorgulardan gelir. Dil katmanı varsa, yorum ayrıca etiketlenir.
          </DialogDescription>
        </DialogHeader>

        {report ? (
          <ReportPreview report={report} />
        ) : (
          <form
            className="space-y-4"
            onSubmit={(event) => {
              event.preventDefault();
              request.mutate();
            }}
          >
            <div className="space-y-2">
              <Label htmlFor="report-template">Rapor türü</Label>
              <Select value={template} onValueChange={(value) => setTemplate(value as ReportTemplate)}>
                <SelectTrigger id="report-template" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="uretim_ozeti">Üretim özeti</SelectItem>
                  <SelectItem value="surdurulebilirlik">Sürdürülebilirlik özeti</SelectItem>
                  <SelectItem value="yonetim">Yönetim raporu</SelectItem>
                  <SelectItem value="gunluk">CEO günlüğü</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="report-period">Dönem</Label>
              <Input
                id="report-period"
                name="period"
                value={period}
                onChange={(event) => setPeriod(event.target.value)}
                placeholder="geçen hafta"
              />
            </div>
            {request.isError && <InlineError error={request.error} />}
            <DialogFooter>
              <Button type="submit" disabled={request.isPending} className="gap-1.5">
                {request.isPending && <LoaderCircle className="size-3.5 animate-spin" />}
                {request.isPending ? "Rapor hazırlanıyor" : "Raporu hazırla"}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}

function ReportPreview({ report }: { report: Report }) {
  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        {report.period_resolved && <span>{report.period_resolved}</span>}
        {report.contract_id && <Badge variant="outline" className="font-mono text-[10px]">{report.contract_id}</Badge>}
      </div>
      {report.sections.map((section, index) => (
        <section key={`${section.title}-${index}`} className="space-y-2">
          <h3 className="text-sm font-medium text-foreground">{section.title}</h3>
          {section.body && <p className="text-sm leading-relaxed text-foreground">{section.body}</p>}
          {section.commentary && (
            <div className="rounded-md border border-brand/20 bg-brand/5 px-3 py-2">
              <Badge variant="brand-subtle" className="mb-1 text-[10px]">yorumdur</Badge>
              <p className="text-sm leading-relaxed text-foreground">{section.commentary}</p>
            </div>
          )}
          {section.result && <ResultView result={section.result} viewHint={section.view_hint ?? undefined} />}
        </section>
      ))}
    </div>
  );
}

function AnalystStudio({
  items,
  sessionId,
  onEvidence,
}: {
  items: AskResponse[];
  sessionId?: string;
  onEvidence?: (edit: { cq: CubeQuery; label: string }) => void;
}) {
  const [open, setOpen] = useState(false);
  const [kind, setKind] = useState<AnalysisKind>("swot");
  const [period, setPeriod] = useState("son çeyrek");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const request = useMutation({
    mutationFn: () =>
      runAnalysis({
        kind,
        period: period.trim() || null,
        session_id: sessionId,
        cube_queries: cubeQueries(items),
      }),
    onSuccess: setAnalysis,
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-1.5">
          <BrainCircuit className="size-3.5" />
          analist
          <BetaBadge />
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[88svh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>{analysis ? analysis.title : "Analist"}</DialogTitle>
          <DialogDescription>
            Her iddia bir kanıta bağlanır. Tahmin varsa varsayımlar görünmeden sunulmaz.
          </DialogDescription>
        </DialogHeader>
        {analysis ? (
          <AnalysisPreview analysis={analysis} onEvidence={onEvidence} />
        ) : (
          <form
            className="space-y-4"
            onSubmit={(event) => {
              event.preventDefault();
              request.mutate();
            }}
          >
            <div className="space-y-2">
              <Label htmlFor="analysis-kind">Çalışma</Label>
              <Select value={kind} onValueChange={(value) => setKind(value as AnalysisKind)}>
                <SelectTrigger id="analysis-kind" className="w-full"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="swot">Veriye dayalı SWOT</SelectItem>
                  <SelectItem value="scorecard">Çeyrek karnesi</SelectItem>
                  <SelectItem value="plan">Öncelikli aksiyon planı</SelectItem>
                  <SelectItem value="risk">Risk değerlendirmesi</SelectItem>
                  <SelectItem value="breakeven">Karbon başabaş OEE</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="analysis-period">Dönem</Label>
              <Input id="analysis-period" name="period" value={period} onChange={(event) => setPeriod(event.target.value)} />
            </div>
            {request.isError && <InlineError error={request.error} />}
            <DialogFooter>
              <Button type="submit" disabled={request.isPending} className="gap-1.5">
                {request.isPending && <LoaderCircle className="size-3.5 animate-spin" />}
                {request.isPending ? "Analiz yapılıyor" : "Analizi başlat"}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}

function AnalysisPreview({
  analysis,
  onEvidence,
}: {
  analysis: Analysis;
  onEvidence?: (edit: { cq: CubeQuery; label: string }) => void;
}) {
  return (
    <div className="space-y-4">
      <p className="text-sm leading-relaxed text-foreground">{analysis.summary}</p>
      {analysis.assumptions && analysis.assumptions.length > 0 && (
        <div className="rounded-md border border-border bg-muted/40 p-3">
          <h3 className="text-xs font-medium text-muted-foreground">Varsayımlar</h3>
          <ul className="mt-1.5 space-y-1 text-xs leading-relaxed text-foreground">
            {analysis.assumptions.map((assumption) => <li key={assumption}>• {assumption}</li>)}
          </ul>
        </div>
      )}
      <div className="space-y-2">
        {analysis.claims.map((claim, index) => {
          const evidence = claim.evidence;
          return (
            <Card key={`${claim.text}-${index}`} className="gap-2 p-3">
              <div className="flex flex-wrap items-center gap-1.5">
                <Badge variant="outline" className="text-[10px]">{claim.kind}</Badge>
                <ConfidenceBadge confidence={claim.confidence} />
                {claim.metric && <span className="font-mono text-[10px] text-muted-foreground">{claim.metric}</span>}
              </div>
              <p className="text-sm leading-relaxed text-foreground">{claim.text}</p>
              {claim.value != null && (
                <p className="font-mono text-xs tabular-nums text-muted-foreground">
                  {new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 2 }).format(claim.value)} {claim.unit ?? ""}
                </p>
              )}
              {onEvidence && evidence && (
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 w-fit gap-1.5 text-xs"
                  onClick={() => onEvidence({ cq: evidence, label: `kanıt: ${claim.text}` })}
                >
                  <RefreshCw className="size-3.5" />
                  kanıta git
                </Button>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}

function PreferenceManager() {
  const [open, setOpen] = useState(false);
  const [scope, setScope] = useState<Preference["scope"]>("default_period");
  const [value, setValue] = useState("son 30 gün");
  const list = useQuery({ queryKey: ["preferences"], queryFn: listPreferences, enabled: open });
  const create = useMutation({
    mutationFn: () => createPreference({ scope, value: value.trim(), source_question: "Kullanıcı tercihi" }),
    onSuccess: () => void list.refetch(),
  });
  const remove = useMutation({
    mutationFn: deletePreference,
    onSuccess: () => void list.refetch(),
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-1.5">
          <SlidersHorizontal className="size-3.5" />
          çalışma bağlamı
          <BetaBadge />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Çalışma bağlamı</DialogTitle>
          <DialogDescription>Bu tercih sonraki sorularına açıkça uygulanır.</DialogDescription>
        </DialogHeader>
        <form
          className="space-y-3"
          onSubmit={(event) => {
            event.preventDefault();
            if (value.trim()) create.mutate();
          }}
        >
          <div className="space-y-2">
            <Label htmlFor="preference-scope">Tercih türü</Label>
            <Select value={scope} onValueChange={(next) => setScope(next as Preference["scope"])}>
              <SelectTrigger id="preference-scope" className="w-full"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="default_period">Varsayılan dönem</SelectItem>
                <SelectItem value="currency">Para birimi</SelectItem>
                <SelectItem value="granularity">Zaman granülerliği</SelectItem>
                <SelectItem value="summary_style">Özet tarzı</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="preference-value">Değer</Label>
            <Input id="preference-value" name="value" value={value} onChange={(event) => setValue(event.target.value)} />
          </div>
          {create.isError && <InlineError error={create.error} />}
          <DialogFooter>
            <Button type="submit" disabled={create.isPending || !value.trim()}>
              {create.isPending ? "Kaydediliyor" : "Tercihi kaydet"}
            </Button>
          </DialogFooter>
        </form>
        <Separator />
        <div className="space-y-2" aria-live="polite">
          {list.isLoading ? (
            <p className="text-sm text-muted-foreground">Tercihler yükleniyor…</p>
          ) : list.isError ? (
            <InlineError error={list.error} />
          ) : list.data?.length ? (
            list.data.map((preference) => (
              <div key={preference.id} className="flex items-center justify-between gap-3 rounded-md border border-border px-3 py-2">
                <div className="min-w-0">
                  <p className="text-sm text-foreground">{preference.value}</p>
                  <p className="font-mono text-[10px] text-muted-foreground">{preference.scope}</p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={remove.isPending}
                  onClick={() => remove.mutate(preference.id)}
                  className="text-muted-foreground hover:text-destructive"
                >
                  kaldır
                </Button>
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">Henüz kaydedilmiş tercih yok.</p>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

function ConfidenceBadge({ confidence }: { confidence: string }) {
  const label = confidence === "deterministic" ? "hesaplandı" : confidence === "estimated" ? "parametreli" : "model";
  const variant = confidence === "deterministic" ? "brand" : confidence === "estimated" ? "brand-subtle" : "secondary";
  return <Badge variant={variant} className="text-[10px]">{label}</Badge>;
}

function BetaBadge() {
  return <Badge variant="brand-subtle" className="px-1.5 text-[9px]">beta</Badge>;
}

function InlineError({ error }: { error: unknown }) {
  return (
    <p role="alert" className="rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
      {apiErrorMessage(error)}
    </p>
  );
}
