"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { runDecisionTemplate, saveDecision, verifyDecision } from "@/lib/api-client";
import { fmtValue } from "@/lib/format";
import type { CubeQuery, DecisionRecord, Prescription } from "@/lib/types";

// FAZ G3/H — REÇETE cevabın İÇİNDE bir katman, ayrı bir panel DEĞİL.
//
// Backend'de üç şey hesaplanıyor ve düz metne çevrilseydi ÜÇÜ DE kaybolurdu:
//   · segment başına YÖN (kötüleşti/iyileşti) — `lower_is_better` BEYANINDAN
//   · YOĞUNLAŞMA oranı — "tek segmente odaklanmak anlamlı mı" sorusunun cevabı
//   · etki ve pay sayıları — chip yalnız etiket taşır
//
// Yön bir RENK kararıdır ve metinden okunmaz: "fire arttı" cümlesi kötü bir haberdir,
// "ciro arttı" iyi. Ayrımı ad tahmininden değil metadata beyanından biliyoruz; UI'ın
// bunu göstermemesi, ölçülmüş bir bilgiyi çöpe atmak olurdu.

function Yon({ yon }: { yon: string }) {
  const kotu = yon === "kotulesti";
  return (
    <span
      className={`shrink-0 font-mono text-[10px] uppercase ${kotu ? "text-red-500" : "text-emerald-600"}`}
      title={
        kotu
          ? "İSTENMEYEN yönde hareket etti (cube metadata'sındaki lower_is_better beyanına göre)"
          : "İSTENEN yönde hareket etti (lower_is_better beyanına göre)"
      }
    >
      {kotu ? "▲ kötüleşti" : "▼ iyileşti"}
    </span>
  );
}

export function PrescriptionLayer({
  recete,
  onCubeEdit,
  soru,
  sessionId,
  contractIds,
  cubeQuery,
}: {
  recete: Prescription;
  onCubeEdit?: (e: { cq: CubeQuery; label: string }) => void;
  soru?: string;
  sessionId?: string;
  contractIds?: string[];
  // FAZ 5.8 — kararın dayandığı analiz. ⚠ Opsiyonel: taşımayan bir çağrı şablonsuz
  // kaydeder ve backend bunu **409 ile dürüstçe söyler** (yeniden koşulamaz). Uydurma
  // bir şablon yazmak, o kararın bugün de aynı analizle alınacağını **varsaymak** olurdu.
  cubeQuery?: CubeQuery | null;
}) {
  const olcu = recete.measure ?? "";
  const yogun = recete.concentration;
  // KARAR KAYDI (Faz E-4): kullanıcı bir seçeneği SEÇTİĞİNDE karar kaydedilir. Seçilenle
  // birlikte DEĞERLENDİRİLENLERİN TAMAMI da gider — "neden bu?" ancak "hangilerine
  // karşı?" bilinirse cevaplanabilir.
  const [kayit, setKayit] = useState<DecisionRecord | null>(null);

  const kaydet = useMutation({
    mutationFn: (secilen: (typeof recete.options)[number]) =>
      saveDecision({
        question: soru ?? null,
        chosen: secilen,
        options: recete.options,
        rationale: recete.rationale,
        contract_ids: contractIds ?? [],
        session_id: sessionId ?? null,
        // ⚠️ FAZ 0.11 — REVİZYON ZİNCİRİ. Karar **silinmez** (`decision.py:35`):
        // fikir değiştiğinde YENİ bir kayıt yazılır ve eskisi `supersedes` ile
        // işaret edilir. Bu alan bağlanmadan revizyon, birbirinden kopuk iki kayıt
        // olurdu ve *"bu karar neyin yerine geçti?"* sorusu cevapsız kalırdı.
        // (II-E.7 bu zincire dayanıyor — alan silinemez, BAĞLANIR.)
        supersedes: kayit?.id ?? null,
        // 🔴 FAZ 5.8 — ŞABLON. Kararın dayandığı analiz **yeniden koşulabilir** olarak
        // saklanır: `contract_ids` o günün sayısını dondurur, şablon *"aynı analizi
        // bugün koşsak ne çıkar"* sorusunu açar. `period` ezilebilir çünkü bir kararın
        // en sık tekrarı **başka bir dönemde** olur.
        sablon: cubeQuery ? { cube_query: cubeQuery, parametreler: ["period"] } : null,
      }),
    onSuccess: setKayit,
  });

  // DOĞRULA: makbuzun değeri onu KONTROL EDEBİLMEKTE. Sunucu hash'i yeniden hesaplar;
  // kayıt sonradan değiştirilmişse `verified=false` döner.
  const dogrula = useMutation({
    mutationFn: (id: string) => verifyDecision(id),
    onSuccess: setKayit,
  });

  // 🔴 FAZ 5.8 — **ŞABLONU YENİDEN KOŞ.** *"Aynı analizi bugün koşsak ne çıkar?"*
  //
  // Makbuz o günün sayısını **dondurur**; şablon onu **tekrarlanabilir** kılar. İkisi
  // farklı sorular cevaplar ve bu yüzden iki ayrı düğme: `doğrula` geçmişe bakar,
  // `bugün koş` bugüne. ⚠ 0 LLM — dönen `cube_query` `/cube` yolundan geçer.
  const sablonuKos = useMutation({
    mutationFn: (id: string) => runDecisionTemplate(id),
    onSuccess: (r) => onCubeEdit?.({ cq: r.cube_query, label: "karar şablonu · bugün" }),
  });

  return (
    <div className="mt-2 border border-hairline">
      <div className="flex items-baseline justify-between border-b border-hairline px-2 py-1">
        <span className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
          reçete
        </span>
        {yogun != null && (
          <span
            className="font-mono text-[10px] text-neutral-500"
            title="En büyük segmentin brüt harekete oranı. Düşükse değişim dağınıktır ve tek bir segmente odaklanmak toplamı kayda değer biçimde değiştirmez."
          >
            yoğunlaşma %{(yogun * 100).toFixed(0)}
          </span>
        )}
      </div>

      {/* DAĞINIK DEĞİŞİMDE ÖNERİ ÜRETİLMEZ — ve bu bir eksiklik değil bir KARARDIR.
          Boş bir liste göstermek yerine NEDEN boş olduğu söylenir; `contribution`ın
          "AVG'de katkı payı TANIMSIZDIR" kapısıyla aynı disiplin. */}
      {recete.diffuse ? (
        <p className="px-2 py-2 font-mono text-[11px] leading-relaxed text-amber-600">
          {recete.rationale}
        </p>
      ) : (
        <>
          <div>
            {recete.options.map((o, i) => (
              <button
                key={`${o.segment}-${i}`}
                type="button"
                disabled={!onCubeEdit || !o.cube_query}
                onClick={() =>
                  o.cube_query && onCubeEdit?.({ cq: o.cube_query, label: o.segment })
                }
                title={
                  onCubeEdit
                    ? "Bu segmenti tek başına aç — LLM'siz koşar, kendi makbuzunu üretir"
                    : undefined
                }
                className={`flex w-full items-baseline justify-between gap-3 border-b border-hairline/40 px-2 py-1 text-left font-mono text-[11px] last:border-0 ${
                  onCubeEdit && o.cube_query
                    ? "transition-colors hover:bg-foreground/[0.04]"
                    : "cursor-default"
                }`}
              >
                <span className="w-4 shrink-0 text-neutral-500">{i + 1}.</span>
                <span className="min-w-0 flex-1 truncate text-neutral-300">
                  {onCubeEdit && o.cube_query && <span className="mr-1 text-neutral-500">↗</span>}
                  {o.segment}
                </span>
                <Yon yon={o.direction} />
                <span className="shrink-0 tabular-nums">
                  <span className={o.impact >= 0 ? "text-emerald-600" : "text-red-500"}>
                    {o.impact >= 0 ? "+" : ""}
                    {fmtValue(o.impact, olcu)}
                  </span>
                  {/* `share === null` = "net değişim ~0, pay TANIMSIZ". Backend bunu
                      bilerek uydurmuyor; UI de uydurmamalı — "%0" yazmak "katkısı yok"
                      demektir ve bu YANLIŞ olur. */}
                  <span className="ml-1 text-neutral-500">
                    ({o.share == null ? "—" : `${(o.share * 100).toFixed(0)}%`})
                  </span>
                </span>
              </button>
            ))}
          </div>
          <p className="border-t border-hairline px-2 py-1 font-mono text-[10px] leading-relaxed text-neutral-500">
            {recete.rationale}
          </p>

          {/* 🔴🔴 FAZ 4.1 — Katman 7'nin guarded-LLM muhakemesi. `rationale`'IN
              ÜSTÜNE binmez, YANINA eklenir (`answer.py::_tavsiye_ekle`/`_kok_
              tavsiye_ekle` ikisini de AYRI alanlarda taşır — biri deterministik
              "→ Öneri:", öteki LLM'in ÜSLUP kattığı yorum). Görsel dil `Makbuz.
              tsx`'in `kanit_sinifi==="probabilistik"` işaretiyle AYNI (amber `⚠`)
              — *"bu bir yorum/öneridir, bir ölçüm değil"* ayrımı burada da
              görünsün, iki yerde iki farklı ikonla değil. */}
          {recete.muhakeme_metni && (
            <p
              className="border-t border-hairline px-2 py-1 font-mono text-[10px] leading-relaxed text-amber-700 dark:text-amber-400"
              title="Bu metin LLM tarafından yazıldı (ÜSLUP) — sayılar yukarıdaki deterministik seçeneklerden, LLM hiçbir sayı üretmedi. Rakamlar ölçüldü, yorum olasılıksaldır."
            >
              <span className="mr-1">⚠ yorum:</span>
              {recete.muhakeme_metni}
            </p>
          )}

          {/* KARAR KAYDI — rapor kalır, kararın kendisi kaybolur. Altı ay sonra "bunu
              neden yapmıştık" sorusunun cevabı burada durur. Şerit yalnız öneri VARSA
              görünür: dağınık değişimde kaydedilecek bir karar yoktur. */}
          <div className="flex flex-wrap items-center gap-1.5 border-t border-hairline px-2 py-1">
            {kayit ? (
              <>
                <span
                  className={`font-mono text-[10px] ${
                    kayit.verified === false
                      ? "text-red-500"
                      : kayit.verified === true
                        ? "text-emerald-600"
                        : "text-neutral-500"
                  }`}
                  title={
                    kayit.verified === false
                      ? "KURCALANMIŞ: kayıt sonradan değiştirilmiş, hash tutmuyor"
                      : kayit.verified === true
                        ? "Hash doğrulandı — kayıt değişmemiş"
                        : "Doğrulanamadı (kayıtta hash yok)"
                  }
                >
                  {kayit.verified === false ? "⚠ kurcalanmış" : "✓ karar kaydedildi"} ·{" "}
                  {kayit.id}
                </span>
                <button
                  onClick={() => dogrula.mutate(kayit.id)}
                  disabled={dogrula.isPending}
                  title="Sunucu hash'i yeniden hesaplar — kayıt değişmiş mi?"
                  className="border border-hairline px-2 py-[2px] font-mono text-[10px] text-neutral-500 transition-colors hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
                >
                  {dogrula.isPending ? "doğrulanıyor…" : "doğrula"}
                </button>
                {/* ⚠ Yalnız şablonlu kayıtta: şablonsuz bir kararı "koş" diye teklif
                    etmek, backend'in 409'unu bir hata gibi göstermek olurdu. */}
                {kayit.sablon?.cube_query && onCubeEdit && (
                  <button
                    onClick={() => sablonuKos.mutate(kayit.id)}
                    disabled={sablonuKos.isPending}
                    title="Kararın dayandığı analizi BUGÜNKÜ veriyle yeniden koş (0 LLM)"
                    className="border border-hairline px-2 py-[2px] font-mono text-[10px] text-neutral-500 transition-colors hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
                  >
                    {sablonuKos.isPending ? "koşuluyor…" : "↻ bugün koş"}
                  </button>
                )}
                <span className="font-mono text-[10px] text-neutral-500">
                  {kayit.evidence_count} makbuz kanıt
                </span>
              </>
            ) : (
              <>
                <span className="font-mono text-[10px] text-neutral-400">
                  kararı kaydet:
                </span>
                {recete.options.map((o, i) => (
                  <button
                    key={`kaydet-${o.segment}-${i}`}
                    onClick={() => kaydet.mutate(o)}
                    disabled={kaydet.isPending}
                    title={`"${o.segment}" seçeneğini seçtiğini, DEĞERLENDİRİLEN TÜM seçeneklerle ve gerekçesiyle birlikte kalıcı kaydet`}
                    className="border border-hairline px-2 py-[2px] font-mono text-[10px] text-neutral-500 transition-colors hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
                  >
                    {kaydet.isPending ? "…" : o.segment}
                  </button>
                ))}
              </>
            )}
            {kaydet.isError && (
              <span className="font-mono text-[10px] text-red-500">
                kaydedilemedi — karar KAYBOLDU, tekrar dene
              </span>
            )}
          </div>
        </>
      )}
    </div>
  );
}
