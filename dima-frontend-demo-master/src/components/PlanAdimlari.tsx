"use client";

import { useState } from "react";
import type { AskResponse, CubeQuery } from "@/lib/types";
import { ResultTable } from "./ResultTable";

/** 🔴🔴 FAZ 6 — ÇOK ADIMLI BİR CEVABI GÖSTEREN İLK BİLEŞEN.
 *
 * ## Neden yeni bir bileşen — ve `Makbuz` neden yetmedi
 *
 * Ölçüldü (envanter, 2026-08-09): çok adımlı bir cevabı gösterecek **hiçbir gövde
 * bileşeni yoktu**. Elde olan tek adım listesi `agent_run.steps` idi ve o bir
 * **denetim izidir**:
 *
 * | `agent_run` (makbuz) | `plan` (bu bileşen) |
 * |---|---|
 * | geriye dönük — koşum bitince yazılır | **cevabın kendisi** |
 * | adım başına `tool/ms/hata` | adım başına **SONUÇ** |
 * | iki tık gömülü (kart → makbuz → tam iz) | cevabın **içinde** |
 * | denetçi için | **kullanıcı** için |
 *
 * İkisi de kalır ve karıştırılmaz: biri *"nasıl koştu"*, öteki *"neyi gösteriyor"*.
 *
 * ## Yeniden koşma yeni bir uç istemedi
 *
 * Her bölüm kendi `cube_query`'sini taşıyor ve `onCubeEdit` altyapısı **zaten
 * kurulu** (altı ayrı yerden çağrılıyor, `POST /cube`, sıfır LLM). Bu bileşen ona
 * yedinci bir çağıran ekliyor — yeni bir uç, yeni bir sözleşme yok.
 *
 * ## Katmanlı: varsayılan KAPALI
 *
 * `Makbuz`'un dersi burada da geçerli: ayrıntı **silinmez, katlanır**. Varsayılan
 * hâl tek satır — *"3 adımda üretildi"*; bölüm tabloları istendiğinde açılır.
 * Bir cevabı üç tabloyla açmak, cevabı gizlemenin bir yoludur.
 */
export function PlanAdimlari({
  item,
  onCubeEdit,
}: {
  item: AskResponse;
  onCubeEdit?: (edit: { cq: CubeQuery; label: string }) => void;
}) {
  const [acik, setAcik] = useState(false);
  const plan = item.plan;
  if (!plan || !plan.adimlar?.length) return null;

  const adimlar = plan.adimlar;
  const bolumler = plan.bolumler ?? [];

  return (
    <div className="mt-3 rounded-lg border border-neutral-200 dark:border-neutral-800">
      <button
        type="button"
        onClick={() => setAcik((v) => !v)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm
                   text-neutral-700 hover:bg-neutral-50
                   dark:text-neutral-300 dark:hover:bg-neutral-900"
        aria-expanded={acik}
      >
        <span className="text-neutral-400">{acik ? "▾" : "▸"}</span>
        <span className="font-medium">
          Bu cevap {adimlar.length} adımda üretildi
        </span>
        <span className="text-neutral-400">
          · {adimlar.map((a) => a.fiil).join(" → ")}
        </span>
      </button>

      {acik && (
        <ol className="border-t border-neutral-200 dark:border-neutral-800">
          {adimlar.map((adim, i) => {
            // ⚠ Bölümler yalnız `SORGU` adımları için var; sıra ile eşleşmez.
            // Kaçıncı `SORGU` olduğunu saymak gerekiyor — yoksa üçüncü adımın
            // altına birinci sorgunun tablosu düşerdi.
            const sorguSirasi = adimlar
              .slice(0, i + 1)
              .filter((a) => a.fiil === "SORGU").length - 1;
            const bolum = adim.fiil === "SORGU" ? bolumler[sorguSirasi] : undefined;
            return (
              <li
                key={adim.sira}
                className="border-b border-neutral-100 px-3 py-2 last:border-b-0
                           dark:border-neutral-900"
              >
                <div className="flex items-start gap-2">
                  <span className="mt-0.5 shrink-0 text-xs text-neutral-400">
                    {adim.sira}.
                  </span>
                  <span className="text-sm text-neutral-700 dark:text-neutral-300">
                    {adim.ozet}
                  </span>
                  {bolum?.cube_query && onCubeEdit && (
                    <button
                      type="button"
                      onClick={() =>
                        onCubeEdit({
                          cq: bolum.cube_query as unknown as CubeQuery,
                          label: `adım ${adim.sira}`,
                        })
                      }
                      className="ml-auto shrink-0 rounded border border-neutral-200
                                 px-2 py-0.5 text-xs text-neutral-500
                                 hover:bg-neutral-50 dark:border-neutral-700
                                 dark:hover:bg-neutral-900"
                      title="Bu adımı yeniden koş — LLM çağrılmaz, aynı sorgu tekrar çalışır"
                    >
                      buradan devam et
                    </button>
                  )}
                </div>
                {bolum?.result && (bolum.result.rows?.length ?? 0) > 0 && (
                  <div className="mt-2 overflow-x-auto">
                    <ResultTable result={bolum.result} />
                  </div>
                )}
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}
