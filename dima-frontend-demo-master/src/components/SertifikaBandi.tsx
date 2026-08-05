"use client";

/** FAZ 7.3(k) · **SARI DRIFT UYARI BANDI** — B8'in tek kullanıcı-görünür yüzeyi.
 * [bayrak: `metrik_sertifikasi`]
 *
 * ## 🔴 Ölçüm yol haritasını düzeltti
 *
 * Yol haritası *"arkası kurulu, önü yoktu"* diyordu. Ölçüldü: **arkası da kurulu
 * değildi.** Beş halka vardı ve **hiçbiri diğerine dokunmuyordu**:
 *
 * | halka | vardı | bağlıydı |
 * |---|---|---|
 * | `metrik_sertifikasi` tablosu | ✅ | 🔴 okuyucu yok |
 * | `app/certification.py` (12 test) | ✅ | 🔴 çağıran yok |
 * | `Explain.sertifika` (backend) | ✅ | 🔴 dolduran yok |
 * | `Explain.sertifika` (TypeScript) | 🔴 **tipte bile yoktu** | — |
 * | `sertifikaRozeti()` | ✅ | 🔴 çağıran yok |
 *
 * > 🔴 *Bir zincirin her halkasını ayrı ayrı test etmek, zinciri test etmek değildir.*
 * > (Aynı denetimde bu sınıfın **on iki** modülde tekrarladığı ölçüldü.)
 *
 * ## Neden bir BANT, bir rozet değil
 *
 * Rozet *"bu ne"* der ve küçüktür; drift *"bu sayıya dayanarak verdiğin karar artık
 * dayanmadığı bir tanıma ait olabilir"* der. İkisi aynı ağırlıkta olamaz:
 * **rozet bir etikettir, drift bir uyarıdır.**
 *
 * ⚠ Ama bant **yalnız `uyari` kademesinde** çıkar. Sağlam bir sertifika için bant
 * açmak, uyarıyı **sıradanlaştırırdı** — ve sıradanlaşan bir uyarı okunmaz. Sağlam
 * kademe rozet olarak (`sertifikaRozeti`) kalır.
 *
 * ## ⚠ "Yeniden doğrula" neden bir DÜĞME DEĞİL
 *
 * Yol haritası *"«yeniden doğrula» eski/yeni tanımla sonucu kıyaslar"* diyor. O kıyas
 * bir **yetki kararıdır**: sertifikayı tazelemek, tanımı **yeniden onaylamak** demektir
 * ve onay sahibi bir metrik sahibidir, cevabı okuyan kişi değil.
 *
 * 🔴 Buraya bir düğme koymak, **onaysız bir onay** üretirdi. Bant bunun yerine
 * **nedeni** söylüyor ve kullanıcıyı metrik sahipliği yüzeyine (`SchemaPanel`)
 * yönlendiriyor — *bir uyarı, çözemeyeceği bir eylemi vaat etmemeli.*
 */

import type { AskResponse } from "@/lib/types";

/** Backend'in `otomatik_iptal_nedeni` kodları → düz Türkçe.
 *
 * ⚠ Bilinmeyen bir kod **gizlenmez, olduğu gibi gösterilir**: bir uyarının anlaşılmaz
 * yarısını atmak, uyarının tamamını eksik yapar. */
const NEDEN_METNI: Record<string, string> = {
  tanim: "ölçünün tanımı onaydan sonra değişti",
  koken: "ölçünün beslendiği kolon kümesi değişti",
  sure: "onayın 90 günlük geçerliliği doldu",
};

function nedenCumlesi(nedenler: string[] | null | undefined): string {
  const liste = (nedenler ?? []).map((n) => NEDEN_METNI[n] ?? n);
  if (!liste.length) return "onaydan beri bir değişiklik saptandı";
  return liste.join(" · ");
}

export function SertifikaBandi({ item }: { item: AskResponse }) {
  const s = item.explain?.sertifika;
  // 🔴 Bant YALNIZ uyarı kademesinde. Sağlam sertifika için bant açmak, uyarıyı
  // sıradanlaştırır — ve sıradanlaşan bir uyarı okunmaz.
  if (!s?.yeniden_dogrulama_gerekli) return null;

  return (
    <div
      role="note"
      aria-label="Metrik tanımı uyarısı"
      className="mt-3 border-l-2 border-amber-500/70 bg-amber-500/[0.06] py-2 pl-3 pr-2"
    >
      <p className="font-mono text-[var(--text-etiket)] uppercase tracking-wider text-amber-600">
        ⚠ metrik tanımı değişmiş — sertifika yeniden doğrulanmalı
      </p>
      <p className="mt-1 font-mono text-[11px] leading-snug text-neutral-500">
        Bu ölçünün tanımını bir sahip <span className="text-foreground">onaylamıştı</span>
        {s.seviye ? ` (${s.seviye})` : ""}, ama {nedenCumlesi(s.otomatik_iptal_nedeni)}.{" "}
        {/* 🔴 Onay SİLİNMEDİ ve bu SÖYLENİYOR: "hiç onaylanmamış" ile "onaylanmış ama
            tanım değişmiş" farklı şeylerdir, ve ikincisi daha bilgilendiricidir. */}
        <span className="text-foreground">Onay silinmedi</span> — sayı hâlâ hesaplanıyor,
        ama dayandığı tanım artık onaylanan tanım olmayabilir.
      </p>
      {/* ⚠ Eylem bir DÜĞME değil, bir YÖN: yeniden doğrulama bir yetki kararıdır ve
          sahibi metrik sahibidir. *Bir uyarı, çözemeyeceği bir eylemi vaat etmemeli.* */}
      <p className="mt-1 font-mono text-[var(--text-etiket)] leading-snug text-neutral-400">
        Yeniden doğrulama metrik sahibinin kararıdır — ayarlar → veri modeli → ölçü
        sahipliği.
      </p>
      {s.kisit && (
        // ⚠ Backend'in bilinen sınırı **taşınıyor**, gizlenmiyor: çok ölçülü cevapta
        // sertifika ilk ölçüden okunur. Kullanıcı hangi ölçü hakkında uyarıldığını
        // bilmeden bir karar veremez.
        <p className="mt-1 font-mono text-[var(--text-etiket)] leading-snug text-neutral-400">
          ⚠ {s.kisit}
        </p>
      )}
    </div>
  );
}
