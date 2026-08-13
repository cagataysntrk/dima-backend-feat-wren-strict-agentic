"use client";

// 🔴🔴 `§63` — **KOŞMADAN GÖRÜNEN PLAN.** `§28.3`'ün karar tablosu tek satırla:
// *«çok adım (N ≥ 2) → 🔴 **her zaman** önizleme»*. Ve belgenin **başlığı** işin kendisi:
// *«route ve garson, KARAR VERİCİ olmaktan çıkıp TAHMİNCİ oluyor … **kullanıcı KARARI
// VERİR (bir tık)**»* (`§3.1`). Bu dosya o tıkın oturduğu yerdir.
//
// ⊙ Ölçülmüş gerekçe (plan): *«bugün plan yazılıp KOŞUYOR; 7. adımda çökerse kullanıcı
// SONDA öğreniyor — onarım tutma **%25**, payda 16.»* Bir planı koşmadan görünür yapmak,
// onu onarmaktan ucuzdur.
//
// ══ ÜÇ YERLEŞİM KARARI ══
//
// ① 🔴 **ADIMLAR DİKEY** (plan satır `1242`: *«adımlar dikey, yuvalar yatay; ikisi aynı
//    şeritte olmaz»*). Bir plan bir **sıra**dır; yatay dizilen sıra, kaydırma çubuğunun
//    arkasında biten bir sıradır. Pill satırı yatay kalır çünkü o bir **küme**dir.
//
// ② 🔴 **`gecerli === false` DE ÇİZİLİR.** `§7`'nin dürüst-ret şartı: kullanıcı neyin
//    tutmadığını **görmeden** düzeltemez. Geçersiz plan gizlenmez; `[koş]` söner, gerekçe
//    (`note`) düz metin olarak kalır. *Bir reddi sessizleştirmek, onu çözülemez yapar.*
//
// ③ ⊘ **`[düzenle]` PLANI DEĞİL CÜMLEYİ DÜZENLER.** Adım listesini elle kurcalatacak bir
//    sözleşme sunucuda **yok** ve uydurmak `§18.8`'in morfoloji tuzağıdır. Yapabildiğimiz
//    dürüst iş: kullanıcının **kendi cümlesini** besteciye geri yazmak ve önizlemeyi
//    kapatmak. Adım düzenleme açık bir borçtur (🅖) — eksiği yayına yazmak, olmayan bir
//    yeteneği varmış gibi çizmekten yeğdir.

// ⚠ Tek sahip: nesnenin şekli `lib/onizleme.ts`'te tanımlı, burada **yeniden yazılmaz**.
import type { PlanOnizlemesi } from "@/lib/onizleme";

export function PlanOnizleme({
  onizleme,
  busy = false,
  onKos,
  onIptal,
  onDuzenle,
}: {
  onizleme: PlanOnizlemesi;
  busy?: boolean;
  /** 🔴 Onay. Aynı gövde `kos: true` ile yeniden gönderilir — ikinci bir uç yok. */
  onKos: () => void;
  onIptal: () => void;
  onDuzenle: () => void;
}) {
  const { adimlar, gecerli, note } = onizleme;
  return (
    <div
      className="mt-2 rounded border border-hairline bg-neutral-50/60 px-3 py-2"
      // ⚠ Ekran okuyucu için bu bir **duyuru**dur: kullanıcı yazarken altında beliren
      // bir plan, sessizce belirirse hiç belirmemiş sayılır.
      role="group"
      aria-label="plan önizlemesi"
    >
      <div className="mb-1.5 flex items-baseline gap-2 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
        <span>{gecerli ? "PLAN — koşmadan önce" : "PLAN — koşulamaz"}</span>
        <span className="text-neutral-300">·</span>
        <span>{adimlar.length} adım</span>
      </div>

      {/* ① adımlar DİKEY — `ol` çünkü sıra anlam taşır, süs değil. */}
      <ol className="space-y-0.5">
        {adimlar.map((a) => (
          <li key={a.sira} className="flex gap-2 text-xs leading-5">
            <span className="w-4 shrink-0 text-right font-mono text-neutral-400">
              {a.sira}
            </span>
            <span className="shrink-0 font-mono text-[10px] uppercase tracking-wide text-accent">
              {a.fiil}
            </span>
            <span className="text-neutral-700">{a.metin}</span>
          </li>
        ))}
      </ol>

      {/* ② gerekçe — geçersizken **asıl** bilgi budur. */}
      {note && <p className="mt-1.5 text-[11px] leading-4 text-neutral-500">{note}</p>}

      <div className="mt-2 flex gap-1.5">
        <button
          type="button"
          onClick={onKos}
          disabled={!gecerli || busy}
          className="rounded border border-accent px-2 py-0.5 font-mono text-[11px] text-accent disabled:opacity-40"
        >
          koş
        </button>
        <button
          type="button"
          onClick={onDuzenle}
          disabled={busy}
          className="rounded border border-hairline px-2 py-0.5 font-mono text-[11px] text-neutral-600 disabled:opacity-40"
        >
          düzenle
        </button>
        <button
          type="button"
          onClick={onIptal}
          disabled={busy}
          className="rounded border border-hairline px-2 py-0.5 font-mono text-[11px] text-neutral-500 disabled:opacity-40"
        >
          iptal
        </button>
      </div>
    </div>
  );
}
