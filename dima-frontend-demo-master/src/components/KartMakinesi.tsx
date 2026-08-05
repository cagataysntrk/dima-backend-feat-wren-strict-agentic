"use client";

/** **KART MAKİNESİ** — grafiğin *etrafındaki* her şey. (FAZ 4)
 *
 * ## 🔴 Neden bu bileşen var
 *
 * Kullanıcının ölçülmüş şikâyeti: *"sağ panelde grafikler aşırı fazla ve boğucu, asıl
 * unsur gibi duruyor."* Envanter onu doğruladı: bir rapor kartında **~59 katman/işlem**
 * var — başlıkta 20 düğme, `InterpretationBar`'da 15 kontrol, üstüne katkı ve reçete
 * katmanları.
 *
 * > Grafiği *"olduğu gibi"* sohbete koymak, grafiği değil **bütün makinesini** sohbete
 * > koymaktır. Ama çözüm grafiği küçültmek de değil — *okunamayan bir thumbnail, sıfır
 * > bilgi taşıyan ekstra bir etkileşim maliyetidir.*
 *
 * **Doğru ayrım: grafiği makinesinden ayır.**
 *
 * | | sohbet | panel |
 * |---|---|---|
 * | ne var | cevap cümlesi + sayı + **temiz grafik** | aynı grafik + **bu bileşen** |
 * | kontrol | 🔴 sıfır — bir tek *"panelde aç"* | yorum çubuğu · katkı · reçete · drill |
 * | rolü | **okunur** | **çalışılır** |
 *
 * ## ⚠ Aynı bileşen, iki yer — ve neden kopya DEĞİL
 *
 * Panel kapalıyken makine kartın **altında** kalır (bugünkü davranış korunur, hiçbir
 * işlev kaybolmaz); panel açıkken **oraya taşınır** ve karttan gizlenir. Tek bileşen,
 * iki konum — *aynı makineyi iki kez yazmak, birini güncelleyip ötekini unutmanın
 * garantisidir.*
 */

import { useState } from "react";

import { ContributionLayer } from "@/components/ContributionLayer";
import { KokNedenHaritasi } from "@/components/KokNedenHaritasi";
import { InterpretationBar } from "@/components/InterpretationBar";
import { PrescriptionLayer } from "@/components/PrescriptionLayer";
import type { AskResponse } from "@/lib/types";

export function KartMakinesi({
  item,
  onCubeEdit,
  sessionId,
  onNot,
}: {
  item: AskResponse & { question?: string };
  onCubeEdit?: (a: { cq: Record<string, unknown>; label: string }) => void;
  sessionId?: string;
  /** 🔴 Vaka kaydı → sohbet. Not **yoluyla birlikte** gider: *bir not, kökeni olmadan
   *  bir kanaattir.* Verilmezse harita not almayı hiç TEKLİF ETMEZ — çalışmayan bir
   *  düğme göstermek, olmayan bir yeteneği vaat etmektir. */
  onNot?: (metin: string) => void;
}) {
  const [haritaAcik, setHaritaAcik] = useState(false);
  const olcuVar =
    ((item.cube_query as { measures?: unknown[] } | null)?.measures?.length ?? 0) > 0;

  return (
    <>
      {/* YORUM ÇUBUĞU — 15 ayrı düzenleme, hepsi LLM'siz `/cube` üzerinden.
          ⚠ Bu, panelin *"çalışılır"* olmasının kalbi: kullanıcı ölçüyü, kırılımı,
          dönemi ve filtreyi burada değiştirir ve her değişiklik **yeni bir soru
          sormadan** yeni bir sonuç üretir. */}
      {item.cube_query && onCubeEdit && olcuVar && (
        <InterpretationBar cq={item.cube_query} onEdit={onCubeEdit} />
      )}

      {/* REÇETE — 🔴 SIRA BAĞLAYICI: reçete ÖNCE, katkı SONRA.
          Reçete *"ne yapmalı"* sorusunun cevabıdır; altındaki katkı katmanı o cevabın
          DAYANAĞIDIR. Sıra ters olsaydı kullanıcı önce ham ayrışmayı, sonra cevabı
          görürdü — yani gerekçeyi hükümden önce okurdu. */}
      {item.prescription && (
        <PrescriptionLayer
          recete={item.prescription}
          onCubeEdit={onCubeEdit}
          soru={item.question}
          sessionId={sessionId}
          // Kanıt bağı: karar, dayandığı makbuza bağlanınca YENİDEN ÇALIŞTIRILABİLİR
          // bir iddiaya dönüşür. Kanıtsız kayıt da meşrudur ama farklıdır.
          contractIds={item.contract_id ? [item.contract_id] : []}
          // ŞABLON: `contract_ids` o günün sayısını DONDURUR, `cube_query` aynı analizi
          // BUGÜN koşulabilir kılar. İkisi farklı sorular cevaplar.
          cubeQuery={item.cube_query ?? null}
        />
      )}

      {/* 🌳 KÖK-NEDEN HARİTASI (FAZ 4B) — *"hangi yola bakmaya değer?"*
          ⚠ Katkı katmanının ALTERNATİFİ değil, ÖNÜ: katkı *"değişimi kim sürükledi"*yi
          ayrıştırır; harita **hangi boyutta dallanmanın değdiğini** ve 🔴 **neye
          BAKILMADIĞINI** söyler. Kullanıcının şikâyeti (*"çok karışık, çözemiyor"*)
          eksik veriden değil, eksik **öncelikten** doğuyordu.
          ⚠ VARSAYILAN KAPALI: panel zaten yoğun; harita bir **araç**tır, bir katman değil.
          Açık gelseydi, tam da düzeltmeye çalıştığı boğulmayı üretirdi. */}
      {item.cube_query && olcuVar && (
        <div className="mt-3 border-t border-[var(--surface-kenar)] pt-3">
          <button
            type="button"
            onClick={() => setHaritaAcik((a) => !a)}
            aria-expanded={haritaAcik}
            className="rounded-[var(--radius-btn)] px-2 py-1 font-mono text-[var(--text-etiket)] text-neutral-500 transition-colors hover:text-accent"
          >
            🌳 kök neden haritası {haritaAcik ? "▾" : "▸"}
          </button>
          {haritaAcik && (
            <div className="mt-2">
              <KokNedenHaritasi
                cubeQuery={item.cube_query}
                sessionId={sessionId}
                onNot={
                  onNot
                    ? ({ yol, not: metin }) =>
                        // 🔴 YOL GÖRSELLEŞTİRİLİR: `fire ↑ ── makine: RAM-2 ── ✎ "…"`.
                        // Yol olmadan not yeniden üretilemez, doğrulanamaz, tartışılamaz.
                        onNot(`${yol.join(" ── ")} ── ✎ ${metin}`)
                    : undefined
                }
              />
            </div>
          )}
        </div>
      )}

      {/* KATKI AYRIŞTIRMASI — şelale + PVM. *"Neden değişti"* sorusunun ham dayanağı. */}
      {item.cube_query && (item.result || item.contribution) && (
        <ContributionLayer
          cubeQuery={item.cube_query}
          sessionId={sessionId}
          onCubeEdit={onCubeEdit}
          hazir={item.contribution ?? null}
        />
      )}
    </>
  );
}
