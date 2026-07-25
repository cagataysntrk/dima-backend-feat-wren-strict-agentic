"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { AskResponse, CubeQuery } from "@/lib/types";
import { createSchedule, getFeatures, getMe, verifyReport } from "@/lib/api-client";
import { BrandMark } from "@/components/BrandMark";
import { InterpretationBar } from "@/components/InterpretationBar";
import { ResultView } from "@/components/ResultView";
import { KpiCardView } from "@/components/KpiCard";
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
  // 🔔 zamanla (ADR-0011, beta bayrağı): raporun CubeQuery'si göreli dönemle zamanlanır.
  const schedStage = useFeature("scheduled_reports");
  const canSchedule = usePermission("schedule:create");
  const canVerify = usePermission("vqr:write");
  const [schedOpen, setSchedOpen] = useState(false);
  const [scheduled, setScheduled] = useState<string | null>(null);
  const schedule = (preset: { every: "hour" | "day" | "week"; at?: string; weekday?: number; period: string; name: string }) => {
    if (!data?.cube_query) return;
    const cq = { ...data.cube_query,
      filters: ((data.cube_query.filters as { dimension: string }[] | undefined) ?? [])
        .filter((f) => f.dimension !== "tarih") };
    if (!(cq.filters as unknown[]).length) delete (cq as Record<string, unknown>).filters;
    createSchedule({ label: vLabel ?? data.question, cube_query: cq,
      period: preset.period, every: preset.every, at: preset.at, weekday: preset.weekday })
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
          <div className="flex shrink-0 items-center gap-1.5 pt-0.5">
            {schedStage && canSchedule && data.cube_query && data.source && (
              <span className="relative">
                <button
                  onClick={() => setSchedOpen((o) => !o)}
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
                  <span className="absolute right-0 top-full z-30 mt-1 flex w-56 flex-col border border-hairline bg-background shadow-lg">
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
                  </span>
                )}
              </span>
            )}
            {verifyStage && canVerify && data.cube_query && data.source && (
              // tek kutu: ✓/✗ geri bildirim (aşama rozeti gösterilmez — bayrak iç bilgi)
              <div className="inline-flex h-[20px] items-stretch border border-hairline font-mono text-[11px]">
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
                  onClick={() => {
                    if (!data.cube_query || !vLabel || !verifyKey || flagged) return;
                    verifyReport(data.cube_query, vLabel, { verdict: "wrong", session_id: sessionId })
                      .then(() => setFb((m) => ({ ...m, [verifyKey]: "bad" })))
                      .catch(() => {});
                  }}
                  title="Bu rapor yanlış — kayda geçer; bu soruya öğrenilmiş yakın bir çift varsa silinir"
                  className={`border-l border-hairline px-1.5 transition-colors ${
                    flagged ? "text-red-500" : "text-neutral-400 hover:text-foreground"
                  }`}
                >
                  {flagged ? "✗ kaydedildi" : "✗ yanlış"}
                </button>
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
          />
        </div>
      )}

      <div className="mt-5 flex items-center justify-between">
        <button
          onClick={() => setShowSql((s) => !s)}
          className="font-mono text-[11px] uppercase tracking-wider text-neutral-400 transition-colors hover:text-foreground"
        >
          {showSql ? "— sql gizle" : "+ sql göster"}
        </button>
        {data.contract_id && (
          <span
            className="font-mono text-[10px] tracking-wider text-neutral-300 dark:text-neutral-600"
            title="Query Contract — bu raporun kanıt kaydı: soru + sorgu + sonuç özeti mühürlendi; sonradan yeniden oynatılıp doğrulanabilir"
          >
            {data.contract_id}
          </span>
        )}
        {showSql && (
          <pre className="mt-2 overflow-auto border border-hairline bg-neutral-950 p-4 font-mono text-xs leading-relaxed text-neutral-100">
            {data.sql}
          </pre>
        )}
      </div>
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
