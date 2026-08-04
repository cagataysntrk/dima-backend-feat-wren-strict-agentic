"use client";

/** FAZ 5.2 — **paylaşılan rapor sayfası**.
 *
 * 🔴 **Bu sayfa yetim-uç kapısı sayesinde doğdu.** İlk yazımda paylaşım linki doğrudan
 * API yoluna (`/share/{token}`) işaret ediyordu — yani müdür linki açtığında **ham JSON**
 * görecekti. `test_uc_yetim_degil` bunu commit'ten önce yakaladı.
 * *Bir uç, tüketicisi olmadan "bitti" değildir.*
 *
 * ## Ne GÖSTERİLİR, ne GÖSTERİLMEZ
 *
 * Gösterilen şey bir **rapor görüntüsüdür**: soru · anlatı · tablo. Gösterilmeyen şey
 * **sorgunun kendisidir** — yük `cube_query`/`sql` taşımaz, dolayısıyla bu sayfadan
 * yeni bir sorgu **çalıştırılamaz**. *Bir paylaşım linki bir oturum değildir.*
 *
 * ⚠ Sayfa **giriş ister** (kurum içi paylaşım) ve backend token'daki tenant'ın okuyanın
 * tenant'ıyla eşleşmesini **zorunlu** kılar. Eşleşmezse 404 — 403 değil, çünkü bir
 * token'ın var olduğunu sızdırmak tahmini kolaylaştırır.
 */

import { useQuery } from "@tanstack/react-query";
import { use } from "react";
import { apiClient, apiErrorMessage } from "@/lib/api-client";

type PaylasilanRapor = {
  question: string;
  note?: string | null;
  narration?: string | null;
  columns: string[];
  rows: Record<string, unknown>[];
  source?: string | null;
  view_hint?: string | null;
};

export default function PaylasilanRaporSayfasi(
  { params }: { params: Promise<{ token: string }> },
) {
  const { token } = use(params);
  const q = useQuery({
    queryKey: ["paylasim", token],
    queryFn: async () => {
      const { data } = await apiClient.get<PaylasilanRapor>(`/share/${token}`);
      return data;
    },
    retry: false,
  });

  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <p className="mb-4 font-mono text-[10px] uppercase tracking-widest text-neutral-400">
        paylaşılan rapor
      </p>

      {q.isPending && (
        <p className="font-mono text-[12px] text-neutral-400">yükleniyor…</p>
      )}

      {q.isError && (
        <div className="border border-hairline p-4">
          <p className="font-mono text-[12px] text-red-500">
            {apiErrorMessage(q.error)}
          </p>
          {/* ⚠ Süre dolmuş · imza bozuk · başka şirket — üçü de AYNI cevabı verir. Hangisi
              olduğunu söylemek, bir token'ın var olup olmadığını sızdırırdı. */}
          <p className="mt-2 font-mono text-[11px] leading-snug text-neutral-400">
            Bu link geçersiz, süresi dolmuş ya da başka bir şirkete ait olabilir.
            Paylaşan kişiden yeni bir link isteyin.
          </p>
        </div>
      )}

      {q.data && (
        <article className="space-y-4">
          <h1 className="font-mono text-[15px] text-foreground">{q.data.question}</h1>

          {q.data.narration && (
            <p className="text-[14px] leading-relaxed text-foreground">
              {q.data.narration}
            </p>
          )}
          {q.data.note && (
            <p className="font-mono text-[12px] text-neutral-400">{q.data.note}</p>
          )}

          {q.data.rows.length > 0 && (
            <div className="overflow-x-auto border border-hairline">
              <table className="w-full font-mono text-[12px]">
                <thead>
                  <tr className="border-b border-hairline text-neutral-400">
                    {q.data.columns.map((c) => (
                      <th key={c} className="px-2 py-1 text-left font-normal">{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {q.data.rows.map((r, i) => (
                    <tr key={i} className="border-b border-hairline/50">
                      {q.data!.columns.map((c) => (
                        <td key={c} className="px-2 py-1">{String(r[c] ?? "")}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* 🔴 Okuyucu neye baktığını BİLMELİ: maskeli, süreli, ve sorgusuz. */}
          <p className="border-t border-hairline pt-3 font-mono text-[10px] leading-snug text-neutral-400">
            Bu bir <span className="text-foreground">rapor görüntüsüdür</span>: içerik
            maskelenmiştir, link sürelidir ve buradan yeni bir sorgu çalıştırılamaz.
            {q.data.source ? ` Kaynak: ${q.data.source}.` : ""}
          </p>
        </article>
      )}
    </main>
  );
}
