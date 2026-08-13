"use client";

// ══════════════════════════════════════════════════════════════════════════════
// 🔴🔴 `§5.2` + `§5.3` — PILL SATIRI: `Niyet` NESNESİNİN GÖRÜNÜR HÂLİ
// ══════════════════════════════════════════════════════════════════════════════
//
//    olcu_adaylari      donemler        kirilimlar       turler
//         │                │                │               │
//    [toplam_fire_kg] [bu ay]    [makineye göre]    [+ ölçü ▾]
//
// Motor `backend/app/pill.py`, ucu `GET /oneri/pill`. Bu bileşen o ucun **tek**
// tüketicisidir: uç ölçüldü, yazıldı, testlendi ve **hiçbir yerden çağrılmıyordu** —
// bu deponun beş kez ölçülmüş *«yazılmış ama bağlanmamış»* kusuru 🆘.
//
// 🔴 **YENİ MODEL KURULMUYOR, MEVCUT MODEL ÇİZİLİYOR.** Pill'ler sunucuda `Niyet`
// alanlarından türetilir; bu dosya **hiçbir** pill üretmez, sıralamaz, adlandırmaz ya da
// doğrulamaz. İkinci bir temsil doğsaydı bir gün biri ötekinden ayrılır ve kullanıcı
// *«anladığım şu»* diye **yanlış** bir şey okurdu (`KAT-1`).
//
// ══ ÜÇ TASARIM KARARI, ÜÇÜ DE PLANIN BİR CÜMLESİNDEN ══
//
// ① 🔴 **`+` TİPLİDİR** (`§5.2`). Tek bir `+` üç ayrı anlama gelir (aynı sorguya ölçü
//    ekle · adım ekle · ayrı rapor) ve plan bunu **bir numaralı tuzak** ilan ediyor:
//    *«göre/bazında»* de üç anlamlıydı ve bu depoyu **üç kez** ısırdı. Bu yüzden her `+`
//    kendi **sonucunu yazıyla** taşır — `sonuc === "plan"` olan `+ adım` bir **adım**
//    ekleyeceğini söyler, ötekiler aynı fişi büyüteceğini. Rengi de ayrı (accent ↔ nötr),
//    ama renk **tek** ayırt edici değil: renk körlüğü bir kusur sebebi olamaz.
//
// ② 🔴 **KIRMIZI PILL'İN NEDENİ TOOLTIP DEĞİL** (`§5.3`). *«İmkânsız soru sorulamaz hâle
//    gelir»* ancak kullanıcı **neden** imkânsız olduğunu okuyabiliyorsa doğrudur. Bir
//    `title` özniteliği fare gerektirir, dokunmatikte hiç açılmaz ve ekran okuyucuda
//    sıranın sonuna düşer. Nedenler pill satırının **altında**, düz metin olarak yazılır.
//    ⚠ Ve **sahipsiz neden de yazılır**: `hatalar[].alan` için bir pill çizilmemiş olsa
//    bile (sunucu bir alanı pill'lemeden reddedebilir) cümle kaybolmaz. *Bir gerekçeyi
//    yalnız sahibi varken göstermek, gerekçeyi bazen susturmaktır.*
//
// ③ ⊘ **`+` BESTECİYE YAZMAZ** — ve bu bir eksiklik değil, çizilmiş bir sınır. `secenekler`
//    bir **envanterdir** (*«buraya ne eklenebilir»*), bir cümle kurma grameri değil: hangi
//    seçeneğin kullanıcının cümlesine **hangi Türkçe ekle** iliştirileceğini söyleyen bir
//    sözleşme sunucuda **yok**. Uydurmak, bu deponun `§18.8`'de yazılı morfoloji tuzağına
//    (*«şehrde»*) elle girmek olurdu. `+` bu yüzden seçeneklerini **açar**; kullanıcı ne
//    ekleyebileceğini görür ve kendi cümlesiyle yazar. *Bir arayüzün bilmediği bir dili
//    konuşmaya çalışması, susmasından pahalıdır.*
//
// ⚠ Seçeneği olmayan bir `+` **düğme değil, etikettir**: tıklanınca hiçbir şey yapmayan
//   bir düğme, hiçbir yerde iz bırakmayan bir vaattir.

import { useEffect, useRef, useState } from "react";
import { getPill } from "@/lib/api-client";
import type { PillYaniti } from "@/lib/types";
import { useFeature } from "@/lib/useFeature";

/** `OneriSeridi` ile **aynı ritim** (o dosyanın `6.4` şerhi): her tuşta uç çağırmak, ucu
 *  bir DDoS'a çevirir. İki katmanın farklı beklemesi, ekranda iki farklı anda beliren iki
 *  satır demekti — aynı kutunun altında iki ayrı tempo bir kusurdur. */
const DEBOUNCE_MS = 200;

const BOS: PillYaniti = { piller: [], artilar: [], hatalar: [] };

/** `sonuc` → kullanıcının okuduğu **sonuç beyanı**. ⚠ Kapalı küme sunucunun
 *  (`pill.SONUC_TEK_SORGU` / `SONUC_PLAN`); burada yalnız **Türkçesi** yaşıyor. */
const SONUC_METNI: Record<string, string> = {
  tek_sorgu: "aynı sorguya",
  plan: "yeni adım",
};

/** 🔴 `§53` — YUVA ADLARI. Sunucu pill'i `alan` koduyla yollar (`olcu` · `varlik` ·
 *  `donem` · `kirilim` · `tur`); insan-okur ad bir **sunum** kararıdır ve burada
 *  yaşar. ⚠ Bilinmeyen bir alan gelirse **kodu** yazılır: yeni bir yuva sessizce
 *  kaybolmaz, adsız görünür ve fark edilir 🆓. */
const ALAN_ADI: Record<string, string> = {
  olcu: "ölçü", varlik: "varlık", donem: "dönem", kirilim: "kırılım", tur: "tür",
};

export function PillSatiri({ metin }: { metin: string }) {
  // 🔴 Bayrak `oneri_katmani` ve bu bir kapsam kararıdır: pill satırı öneri şeridiyle
  // **aynı** öngörü katmanının parçası (`§5.1`–`§5.3`) ve aynı kutunun altında duruyor.
  // İkinci bir bayrak açmak, tek bir yüzeyi iki anahtarla yönetmek olurdu.
  // ⚠ `KURAL B`: bayrak kapalıyken bu bileşen `null` döner ve **ağa hiç çıkmaz** —
  // «çizmemek» yetmez, maliyetin ölçümü istekten başlar.
  const acik = useFeature("oneri_katmani");
  const kapaliBayrak = acik === null || acik === "off";
  const [yanit, setYanit] = useState<PillYaniti>(BOS);
  const sonIstek = useRef(0);

  const q = metin.trim();

  useEffect(() => {
    // 🔴 `q` boşken uç **hiç çağrılmaz**. Sunucu boş soruda zaten boş satır döndürüyor
    // (`routers/oneri.py`: *«uydurma bir niyet çizmek …»*) — ama o kararı ağ üzerinden
    // sormak, cevabı bilinen bir soruyu her tuşta yeniden sormaktır.
    if (kapaliBayrak || !q) return;
    const kimlik = ++sonIstek.current;
    const t = setTimeout(() => {
      getPill(q)
        .then((y) => {
          // ⚠ Yarış koruması `OneriSeridi` ile birebir aynı: geç dönen ESKİ bir cevap
          // yeni satırı EZMEMELİ. Burada kusur daha da sinsi olurdu — kullanıcı
          // yazmayı sürdürürken **eski** cümlenin kırmızısını görürdü.
          if (kimlik === sonIstek.current) setYanit(y);
        })
        // Öneri katmanı cevabı **bozmaz** (`§101.1`): pill ucu düşerse satır kaybolur,
        // soru kutusu çalışmaya devam eder.
        .catch(() => { if (kimlik === sonIstek.current) setYanit(BOS); });
    }, DEBOUNCE_MS);
    return () => clearTimeout(t);
  }, [q, kapaliBayrak]);

  // 🔴 **BOŞALTMA BİR ETKİ DEĞİL BİR TÜRETMEDİR.** İlk sürüm boş girdide `setYanit(BOS)`
  // çağırıyordu ve `react-hooks/set-state-in-effect` onu haklı olarak reddetti: bir etkinin
  // gövdesinde eşzamanlı `setState`, ardışık render doğurur. Ve kural burada yalnız bir
  // biçim uyarısı değil — *«girdi boşsa satır yok»* zaten **mevcut durumdan hesaplanabilen**
  // bir şeydi; onu ikinci bir yere yazmak, aynı gerçeğin iki sahibi olurdu.
  //
  // ⊙ Bedava gelen davranış: yazarken satır **kaybolup geri gelmiyor**. Eski cevap yenisi
  // gelene kadar duruyor (bayatlığı debounce penceresiyle sınırlı, `OneriSeridi` ile aynı
  // ritim). *Bir göstergeyi her tuşta silmek, onu okunamaz yapmanın en hızlı yoludur.*
  const { piller, artilar, hatalar } = kapaliBayrak || !q ? BOS : yanit;
  if (!piller.length && !artilar.length && !hatalar.length) return null;

  // `§5.3` — hangi **alan** kırmızı. ⚠ Eşleşme `alan` üzerinden, `deger` üzerinden değil:
  // bir pill'in `deger`i bir dizi olabilir (`donemler`) ve hatanın `deger`i o dizinin
  // kendisi ya da bir üyesi olabilir. Alanı eşleştirmek, sunucunun *«şu alan yüzünden»*
  // cümlesiyle birebir aynı granülerliktir.
  const hataliAlanlar = new Set(hatalar.map((h) => h.alan));

  return (
    <div className="mt-1 flex flex-col gap-1 font-mono text-[11px]">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
        {piller.map((p, i) => {
          const kirmizi = hataliAlanlar.has(p.alan);
          // 🔴 `§53` — YUVANIN ADI GÖRÜNÜR. Ölçülen kusur: öneri çipi ile pill çipi
          // **aynı** görünüyordu; kullanıcı ekranda alt sırayı öneri sandı. Şerit artık
          // dikey **liste**, pill satırı yatay ve her yuva **adıyla** duruyor — plan
          // `§5.2`nin sütunları ve `1242`nin *«ikisi aynı şeritte olmaz»* kuralı.
          // ⚠ Ad **yalnız grubun ilkinde**: her çipe ad yapıştırmak satırı ikiye katlar.
          const ilk = i === 0 || piller[i - 1].alan !== p.alan;
          return (
            <span key={`${p.alan}:${p.metin}`} className="inline-flex items-center gap-1">
              {ilk && (
                <span className="select-none uppercase tracking-wider text-neutral-600">
                  {ALAN_ADI[p.alan] ?? p.alan}
                </span>
              )}
              <span
                // ⚠ `aria-invalid`: kırmızı **yalnız bir renk değil bir durumdur**; ekran
                // okuyucu onu görmezse `§5.3` yalnız gören kullanıcılar için doğrudur.
                aria-invalid={kirmizi || undefined}
                className={
                  "max-w-full truncate border px-1.5 py-0.5 " +
                  (kirmizi
                    ? "border-red-500/60 bg-red-500/[0.06] text-red-600 dark:text-red-400"
                    : "border-hairline text-neutral-500")
                }
              >
                {p.metin}
              </span>
            </span>
          );
        })}
        {artilar.map((a) => (
          <ArtiDugmesi key={a.tip} arti={a} />
        ))}
      </div>
      {/* `§5.3` — NEDEN, OKUNUR HÂLDE. Tooltip değil: bkz. bu dosyanın ② şerhi. */}
      {hatalar.map((h, i) => (
        <div
          key={`${h.alan}-${i}`}
          role="status"
          className="leading-snug text-red-600 dark:text-red-400"
        >
          ⊘ {h.neden}
        </div>
      ))}
    </div>
  );
}

/** 🔴 **TİPLİ `+`** — kendi sonucunu yazıyla taşır ve seçeneklerini açar (bkz. ① ve ③). */
function ArtiDugmesi({ arti }: { arti: PillYaniti["artilar"][number] }) {
  const [acik, setAcik] = useState(false);
  const plan = arti.sonuc === "plan";
  const sonuc = SONUC_METNI[arti.sonuc] ?? arti.sonuc;
  // ⚠ Seçeneksiz `+` bir **etikettir**: tıklanacak bir şeyi olmayan bir düğme çizmemek,
  // bir yeteneği gizlemek değil, olmayan bir yeteneği vaat etmemektir.
  const tiklanir = arti.secenekler.length > 0;
  const govde = (
    <>
      {arti.metin}
      {/* 🔴 Tip **yazıyla** görünür, yalnız renkle değil: renk tek başına bir ayrım
          taşıyamaz (renk körlüğü) ve zaten `title` da bir fare varsayardı. */}
      <span className="ml-1 opacity-[var(--opacity-soluk)]">· {sonuc}</span>
    </>
  );
  const renk = plan
    ? "border-accent/50 text-accent"
    : "border-hairline text-neutral-500";

  return (
    <span className="relative inline-flex flex-col">
      {tiklanir ? (
        <button
          type="button"
          onClick={() => setAcik((v) => !v)}
          aria-expanded={acik}
          title={plan
            ? "Bir ADIM ekler — sonuç sıralı bir plandır (birden çok kart değil)."
            : "Aynı sorguyu büyütür — sonuç tek bir cube_query'dir."}
          className={`border px-1.5 py-0.5 transition-colors hover:text-foreground ${renk}`}
        >
          {govde} {acik ? "▴" : "▾"}
        </button>
      ) : (
        <span className={`border px-1.5 py-0.5 ${renk}`}>{govde}</span>
      )}
      {acik && (
        // ⊘ Seçenekler **okunur**, tıklanmaz — bkz. ③. Kullanıcı ne ekleyebileceğini
        // görür ve kendi cümlesiyle yazar; arayüz onun adına Türkçe kurmaz.
        <span className="mt-0.5 flex flex-wrap gap-1 border border-hairline px-1.5 py-1 text-neutral-500">
          {arti.secenekler.map((s) => (
            <span key={s.deger} className="whitespace-nowrap">
              {s.metin}
            </span>
          ))}
        </span>
      )}
    </span>
  );
}
