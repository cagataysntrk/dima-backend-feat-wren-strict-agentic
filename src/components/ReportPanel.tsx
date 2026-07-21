"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { AskResponse, CubeQuery } from "@/lib/types";
import { getFeatures, verifyReport } from "@/lib/api-client";
import { BrandMark } from "@/components/BrandMark";
import { InterpretationBar } from "@/components/InterpretationBar";
import { ResultView } from "@/components/ResultView";
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

// Sağ bölme: seçili raporun canlı görünümü (keskin, mono readout).
export function ReportPanel({
  data,
  pending,
  viewHint,
  onCubeEdit,
  error,
}: {
  data: AskResponse | null;
  pending: boolean;
  // "grafik ver" tarzı görünüm isteği — ResultView remount edilip başlangıç görünümü olur.
  viewHint?: { kind: string; nonce: number } | null;
  // Yorum çubuğu chip düzenlemeleri (deterministik /cube).
  onCubeEdit?: (edit: { cq: CubeQuery; label: string }) => void;
  error: string | null;
}) {
  const [showSql, setShowSql] = useState(false);
  const [showTrace, setShowTrace] = useState(false);
  // "✓ doğru" / "✗ yanlış" (beta bayrağı): geri bildirim — doğrulama geri ALINABİLİR.
  const verifyStage = useFeature("verify_button");
  const [verified, setVerified] = useState<string | null>(null);
  const [flagged, setFlagged] = useState<string | null>(null);
  const verifyKey = data?.cube_query ? `${data.question}` : null;

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
            {verifyStage && data.cube_query && data.source && (
              // tek kutu: ✓/✗ geri bildirim (aşama rozeti gösterilmez — bayrak iç bilgi)
              <div className="inline-flex h-[20px] items-stretch border border-hairline font-mono text-[11px]">
                <button
                  onClick={() => {
                    if (!data.cube_query) return;
                    const isOn = verified === verifyKey;
                    // ikinci tık = GERİ AL (yanlışlıkla doğrulamayı düzeltme yolu)
                    verifyReport(data.cube_query, data.question, isOn ? { undo: true } : undefined)
                      .then(() => {
                        setVerified(isOn ? null : verifyKey);
                        setFlagged(null);
                      })
                      .catch(() => {});
                  }}
                  title={
                    verified === verifyKey
                      ? "Doğrulamayı geri al"
                      : "Bu raporu doğru olarak işaretle — aynı soru bundan sonra LLM'siz cevaplanır"
                  }
                  className={`px-1.5 transition-colors ${
                    verified === verifyKey
                      ? "text-emerald-500"
                      : "text-neutral-400 hover:text-foreground"
                  }`}
                >
                  {verified === verifyKey ? "✓ öğrenildi" : "✓ doğru"}
                </button>
                <button
                  onClick={() => {
                    if (!data.cube_query || flagged === verifyKey) return;
                    verifyReport(data.cube_query, data.question, { verdict: "wrong" })
                      .then(() => {
                        setFlagged(verifyKey);
                        setVerified(null);
                      })
                      .catch(() => {});
                  }}
                  title="Bu rapor yanlış — kayda geçer; bu soruya öğrenilmiş yakın bir çift varsa silinir"
                  className={`border-l border-hairline px-1.5 transition-colors ${
                    flagged === verifyKey ? "text-red-500" : "text-neutral-400 hover:text-foreground"
                  }`}
                >
                  {flagged === verifyKey ? "✗ kaydedildi" : "✗ yanlış"}
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

      {data.cube_query && onCubeEdit && (
        <InterpretationBar cq={data.cube_query} onEdit={onCubeEdit} />
      )}

      {data.result && (
        <div className="border border-hairline bg-background p-4">
          <ResultView
            key={`${data.question}·${data.sql}·${viewHint?.nonce ?? 0}`}
            result={data.result}
            viewHint={viewHint?.kind}
          />
        </div>
      )}

      <div className="mt-5">
        <button
          onClick={() => setShowSql((s) => !s)}
          className="font-mono text-[11px] uppercase tracking-wider text-neutral-400 transition-colors hover:text-foreground"
        >
          {showSql ? "— sql gizle" : "+ sql göster"}
        </button>
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
