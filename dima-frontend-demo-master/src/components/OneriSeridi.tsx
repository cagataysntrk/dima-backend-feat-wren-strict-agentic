"use client";

// 🔴 FAZ 6.2/6.3/6.4/6.5 — YAZARKEN-ARA ŞERİDİ.
//
// Backend motoru `backend/app/oneri.py`, ucu `GET /oneri`. Bu bileşen o ucun
// **gerçek tüketicisidir**: `test_uc_yetim_degil` bir sarmalayıcının UI'da
// çağrılmasını şart koşar (`SARMALAYICI_MUAF` bugüne dek **boş** — muafiyet
// verilmemiş, verilmeyecek).
//
// ⊘ Sorgu KOŞMAZ: tıklanan aday yalnız **metni** tamamlar. Sayıyı küp koyar.
// ⚠ Yetki süzmesi **motorda** ve **sıralamadan önce** yapılır — bu bileşen süzmez,
//   süzülmüş listeyi alır (bir öneri listesi envanterdir).
//
// ══════════════════════════════════════════════════════════════════════════════
// 🔴🔴 `§5.1` — **BİLEŞEN ARTIK BESTECİYİ SARMALIYOR** (2026-08-13)
// ══════════════════════════════════════════════════════════════════════════════
//
// Önce yalnız girdinin **altına** bir pill satırı çiziyordu. `§5.1`'in çizimi ise üç
// katmanlıdır ve ortadaki katman girdinin **kendisidir**:
//
//     ┌─ 📌 RAM-3 · toplam_fire_kg · bu ay        [✕ bağlamı bırak] ─┐   ← çapa
//       ┌────────────────────────────────────────────────────────┐
//       │ fire ki▌                                               │     ← children
//       └────────────────────────────────────────────────────────┘
//        ↳ BU RAPOR ÜZERİNDE …  ↳ YENİ KONU …                          ← şerit
//
// Bu yüzden bileşen `children` alır. İki kazanç, ikisi de ölçülmüş bir kusuru kapatır:
//
// ① **ÇAPA GÖRÜNÜR OLUR.** Kayıtlı ilke: *bir thread/UI gruplaması semantik bağlam
//    sınırı taşımaz; yeni bağlam yalnız **açık kullanıcı eylemiyle** doğar.* `✕` o
//    açık eylemdir ve artık kullanıcının **yazdığı yerin üstünde** durur — panelin
//    tepesinde değil. *Gizli bir durumu görünür kılmak, onu yazının yanına koymaktır.*
//
// ② **KLAVYE ARTIK KÜRESEL DEĞİL.** Eski hâl `window.addEventListener("keydown", …,
//    true)` kullanıyordu: ekranda iki girdi olduğu anda ↓↑/Enter **ikisinde birden**
//    ateşlenirdi. Sarmalayıcı, `onKeyDownCapture` ile tuşları **kendi** bestecisine
//    hapseder — odak nerede ise şerit oradadır.
//
// ⚠ Bu yüzden bileşen artık **`return null` DEMEZ**: içinde besteci var. Bayrak/tercih
// kapalıyken çizilmeyen şey **şerittir**, girdi değil. (Ölçüldü: eski `if (kapaliBayrak)
// return null` bu sarmalamayla birlikte **soru kutusunu yok ederdi**.)

import {
  useEffect, useRef, useState, useSyncExternalStore,
  type KeyboardEvent, type ReactNode,
} from "react";
import { getOneri, oneriTik } from "@/lib/api-client";
import type { CubeQuery } from "@/lib/types";
import { useFeature } from "@/lib/useFeature";

/** `6.4` — debounce 200 ms. Her tuşta uç çağırmak, ucu bir DDoS'a çevirir. */
const DEBOUNCE_MS = 200;
/** `6.4` — **≤7** öneri, kaydırma yok. Görünmeyen bir öneri, olmayan bir öneridir. */
const AZAMI = 7;

/** 🔴 **TUŞ ≠ BAYRAK.** `oneri_katmani` sunucu tarafıdır ve bir **yetkidir**; bu anahtar
 *  yalnız bir **kullanıcı tercihidir** ve onu **EZEMEZ**: bayrak kapalıyken anahtar hiç
 *  çizilmez (`useFeature` null/`off` → toggle da yok). Tercih `localStorage`'da durur
 *  çünkü bir kullanıcı ayarı, sekme yenilenince unutuluyorsa bir ayar değil bir kazadır.
 *
 *  ⚠ `test_serit_BAYRAGA_bagli`'nin uyardığı *«planın localStorage çaresi»* BU DEĞİLDİR:
 *  o, **bayrağı** localStorage'a taşımayı (ve A/B ölçümünü kaybetmeyi) öneriyordu.
 *  Bayrak hâlâ `useFeature`'dan, yani normal kanaldan akıyor. */
const TERCIH_ANAHTARI = "dima-oneri-serit";

/** ⚠ Tercih bir **dış depodur**, bir React durumu değil — bu yüzden `useState`+`useEffect`
 *  ile değil `useSyncExternalStore` ile okunur. İki somut kazancı var:
 *  ① **Hydration**: sunucu anlık görüntüsü `true`; `useState(() => localStorage…)` ilk
 *     render'ı istemciden ayrıştırırdı (`KayitBildirimi.tsx`'in kendi şerhi).
 *  ② Aynı anda birden çok besteci çizilirse (bugün bir tane) hepsi **tek** kaynaktan
 *     okur — iki kutuda iki farklı «açık/kapalı» hâli doğamaz. */
// ⚠ `try/catch` süs değil: `getSnapshot` **her render'da** çağrılır ve `localStorage`
// erişimi bazı gizli-mod/üçüncü-taraf-çerez ayarlarında **fırlatır**. Orada fırlayan bir
// okuma, bütün soru kutusunu düşürürdü. *Bir tercihi okuyamamak, bir arıza değildir;
// arıza, okuyamayınca çökmektir.*
// ⚠ `_bellek`: depo erişilemiyorsa **oturumluk** yedek. Onsuz, depo fırlatan bir
// tarayıcıda tuş görünür ama HİÇBİR ŞEY YAPMAZDI — kalıcılığı kaybetmek bir eksiklik,
// tuşun ölmesi bir kusurdur.
let _bellek = true;
const _aboneler = new Set<() => void>();
const tercihAbone = (f: () => void) => { _aboneler.add(f); return () => { _aboneler.delete(f); }; };
const tercihOku = () => {
  try { return window.localStorage.getItem(TERCIH_ANAHTARI) !== "0"; } catch { return _bellek; }
};
function tercihYaz(acikMi: boolean) {
  _bellek = acikMi;
  try { window.localStorage.setItem(TERCIH_ANAHTARI, acikMi ? "1" : "0"); } catch { /* yut */ }
  _aboneler.forEach((f) => f());
}

/** `§5.1` — ÇAPA. İki iş görür ve ikisi de **verilir, üretilmez**:
 *  * `etiket` — insan-okur hâl (tek sahibi `temellendirme`: *«anladığım şu»*, 0 LLM);
 *  * `cq` — uca gönderilecek **ham sorgu**; `BU RAPOR ÜZERİNDE` bandı bunsuz boş kalır. */
export interface OneriCapasi {
  etiket: string;
  cq?: CubeQuery | null;
  ipucu?: string;
}

type Grup = "rapor_ustunde" | "yeni_konu";

/** `§5.1`'in iki başlığı — **sıra bağlayıcıdır**: bağlam üstündeki iş önce gelir,
 *  çünkü kullanıcı oraya bakarken yazıyor. */
const GRUP_SIRASI: Grup[] = ["rapor_ustunde", "yeni_konu"];
const GRUP_BASLIK: Record<Grup, string> = {
  rapor_ustunde: "↳ BU RAPOR ÜZERİNDE",
  yeni_konu: "↳ YENİ KONU",
};

/** Şeritte görünen **bir satır** — `oneriler` (cümle) ve `adaylar` (eski, çıplak etiket)
 *  bu tek biçimde buluşur. ⚠ İki ayrı render dalı yazmak, aynı listeyi iki kez çizmek ve
 *  bir gün yalnız birini düzeltmek olurdu. */
interface Satir {
  kimlik: string;
  metin: string;
  grup: Grup;
  ipucu: string;
  /** 🔴 `§7 ②` — sunucunun `tur`u. Bir satırın **koşulacak mı yoksa tamamlanacak mı**
   *  olduğunu tek başına bu alan söyler; `cube_query`nin yokluğu söylemez (bir cümle onu
   *  şema eksikliğinden de taşımayabilir). Eski `adaylar` dalında `tur` yoktur → `""`,
   *  yani o dal **her zaman** tamamlama olarak kalır (`KURAL B`). */
  tur: string;
  /** 🔴 `§45` — öngörünün **hazır sorgusu**. Ölçülen kusur: tıklamada **atılıyordu**;
   *  cümle `/ask`'a **metin** olarak gidiyor, route şüpheli sayılıp **garsona** düşüyordu.
   *  Oysa bu `cube_query` katalogdan deterministik üretildi — yeniden *anlaşılmasına*
   *  gerek yok. Plan `§6 Thread 1`: *«Enter → `cube_query` koşar · 34 ms · **0 token**»*.
   *  ⚠ `null` olabilir (makro satırları taşımaz) — dal sırası bunu **şart** koşar 🆤. */
  cq: CubeQuery | null;
}

/** 🔴 **MAKRO ADLARI — `backend/app/makro.py::MAKROLAR` ile birebir.** Şerit bugün yalnız
 *  `neden`i üretiyor (`oneri_cumle.TUR_NEDEN`), ötekiler `makrolar_icin` üzerinden gelir.
 *  ⚠ Küme **kapalı** ve bilerek: `tur`u körlemesine makro adı saymak, bir gün eklenecek
 *  sıradan bir `tur`u (ör. `donem_kaydir`) sessizce `/oneri/makro`'ya yollar ve kullanıcı
 *  bir 400 görürdü. *Bir adı bir komut sanmak, ancak adların listesi varsa güvenlidir.* */
const MAKRO_ADLARI = new Set(["neden", "gecen_yil", "en_kotu"]);

export function OneriSeridi({
  metin,
  onSec,
  onSorgu,
  sonBakilanlar = [],
  capa = null,
  onCapaBirak,
  onMakro,
  children,
}: {
  metin: string;
  onSec: (etiket: string) => void;
  /** `§45` — hazır `cube_query` taşıyan öngörü **koşulur** (`/cube`, 0 LLM). Verilmezse
   *  eski davranış birebir sürer (`KURAL B`). */
  onSorgu?: (cq: CubeQuery, metin: string) => void;
  /** `5.9` — boş girdide gösterilecek **son bakılanlar**. Yeni bir depo AÇMAZ:
   *  sohbetin kendi kartlarından türetilir (kalıcı durum yok, izin yok, senkron yok). */
  sonBakilanlar?: string[];
  /** `§5.1` — aktif `cube_query`'nin görünür hâli. `null` → çapa çubuğu hiç çizilmez. */
  capa?: OneriCapasi | null;
  /** 🔴 `✕ bağlamı bırak` — **açık kullanıcı eylemi.** Verilmezse düğme çizilmez. */
  onCapaBirak?: () => void;
  /** 🔴 `§7 ②` — bir **makro** satırı tıklandı (`tur ∈ MAKRO_ADLARI`). Verilmezse makro
   *  satırı bugünkü gibi yalnız metni tamamlar — yani `KURAL B` ile birebir eski davranış. */
  onMakro?: (ad: string, soru: string) => void;
  /** Bestecinin kendisi (`CaretInput`). ⚠ Çapa **üstünde**, şerit **altında** durur. */
  children: ReactNode;
}) {
  // 🔴 `6.6` — TUŞ. Kapalıyken şerit çizilmez **ve `/oneri` hiç çağrılmaz** 🆀.
  // ⚠ Planın `localStorage` çaresi UYGULANMADI: `useFeature` zaten var, bayrak normal
  // kanaldan akar ve planın kendi uyardığı **A/B kaybı** (`§40.3`) doğmaz 🆝.
  const acik = useFeature("oneri_katmani");
  const kapaliBayrak = acik === null || acik === "off";
  // Kullanıcı tercihi — bayrağın **altında** bir katman (yukarıdaki `TERCIH_ANAHTARI`).
  // ⚠ Sunucu anlık görüntüsü `true`: bir tercih okunamıyorsa varsayılan **açıktır**;
  // okuyamadığı için bir yeteneği kapatan arayüz, onu sessizce geri alır.
  const tercih = useSyncExternalStore(tercihAbone, tercihOku, () => true);
  const [adaylar, setAdaylar] = useState<Satir[]>([]);
  // 🔴 **BAŞLANGIÇ `-1`: HİÇBİRİ SEÇİLİ DEĞİL — ve bu `§3.3`'ün ta kendisidir.**
  // Eskiden `0` idi: şerit görünürken `Enter` **her zaman** ilk adayı alırdı, yani
  // kullanıcı kendi cümlesini gönderemezdi. O bir tamamlama değil bir **menüdür**
  // (*«listede yoksa yok»*). Artık `Enter` kullanıcının yazdığını gönderir; şeride
  // girmek için önce `↓`. *Serbest metni kapatan bir öneri, öneri değil bir kapıdır.*
  const [secili, setSecili] = useState(-1);
  const [kapali, setKapali] = useState(false);
  const sonIstek = useRef(0);

  useEffect(() => {
    const q = metin.trim();
    // 🔴 Bayrak kapalıysa **ağa hiç çıkma** — «çizmemek» yetmez, `E-1`'in ölçümü
    // istekten başlar. ⚠ Kullanıcı tercihi de **aynı kapıdan** geçer: susturulmuş bir
    // şerit için istek atmak, tuşu bir süse çevirirdi.
    if (kapaliBayrak || !tercih || q.length < 2 || kapali) {
      setAdaylar([]);
      return;
    }
    const kimlik = ++sonIstek.current;
    const t = setTimeout(() => {
      // 🔴 Çapa uca **gider**: `BU RAPOR ÜZERİNDE` bandını sunucu ancak bağlamı
      // bilirse kurabilir (`oneri_cumle._rapor_ustunde` çapasızken boş döner).
      getOneri(q, capa?.cq ?? null)
        .then((y) => {
          // ⚠ Yarış koruması: geç dönen ESKİ bir cevap yeni listeyi EZMEMELİ —
          // typeahead'de en sık görülen görsel hata budur.
          if (kimlik !== sonIstek.current) return;
          // 🔴🔴 `§42` — **ÇIPLAK ETİKET DÜŞÜŞÜ KAPATILDI** (kullanıcı kararı 2026-08-13).
          //
          // Bu dal `oneriler` boşken `adaylar`a düşüyor ve şeride **alan adları**
          // basıyordu: *«duruş sayısı · arıza sayısı · kırılım»*. Kullanıcı bunu ekranda
          // görüp reddetti: *«öneri değil ÖNGÖRÜ… cümle bile değil»* — ve haklıydı:
          // bir alan adı listesi bir **tamamlama öngörüsü değildir**, katalogdur.
          //
          // ⚠ Eski gerekçe *(«hiç göstermemek alternatif değil — `KURAL B`»)* **bayrak
          // kapalı** hâl için yazılmıştı; ama ölçülen ekran bayrak **açıkken** çekildi
          // (*«öneri: açık»*). Yani o gerekçe bu düşüşü savunmuyordu.
          //
          // ⊙ Yeni kural: şerit ya **cümle** gösterir ya **hiçbir şey**. Boş bir şerit
          // sessizdir; yanlış bir şerit ise ürünü *«işe yaramaz»* gösterir 🆡.
          const satirlar: Satir[] = (y.oneriler ?? []).map((o) => ({
            kimlik: o.kimlik, metin: o.metin,
            grup: o.grup === "rapor_ustunde" ? "rapor_ustunde" : "yeni_konu",
            ipucu: o.cube_query ? `${o.cube ?? ""} · ${o.tur}` : `makro · ${o.tur}`,
            tur: o.tur,
            cq: o.cube_query ?? null,
          }));
          // ⚠ Sıralama **burada** yapılır, render'da değil: `secili` bir **konumdur** ve
          // o konum ekrandaki sırayla birebir aynı olmak zorunda — `↓↑` ile
          // `oneriTik(konum)` aksi hâlde iki farklı listeyi sayardı 🆆.
          satirlar.sort((a, b) => GRUP_SIRASI.indexOf(a.grup) - GRUP_SIRASI.indexOf(b.grup));
          setAdaylar(satirlar.slice(0, AZAMI));
          setSecili(-1);
        })
        .catch(() => setAdaylar([]));   // öneri katmanı cevabı BOZMAZ (§101.1)
    }, DEBOUNCE_MS);
    return () => clearTimeout(t);
  }, [metin, kapali, kapaliBayrak, tercih, capa]);

  useEffect(() => { setKapali(false); }, [metin]);

  // 🔴 `FAZ 8.1` — SEÇİMİN TEK KAPISI. Fare ve klavye **aynı** yoldan geçer; iki ayrı
  // yol olsaydı biri kaydeder öteki kaydetmezdi ve sayı sessizce eksik kalırdı ㊲.
  function sec(i: number) {
    const a = adaylar[i];
    if (!a) return;
    oneriTik(metin.trim(), adaylar.map((x) => x.kimlik), i);
    // 🔴🔴 `§7 ②` — **MAKRO SATIRI TEK İSTİSNADIR VE İSTİSNA OLMAK ZORUNDADIR.**
    //
    // Bu şeridin kuralı *«tıklama yalnız metni tamamlar»*dır ve o kural yerinde duruyor:
    // bir `cube_query` taşıyan satır bile koşmaz. Ama makro satırının tamamlayacağı bir
    // metin **yoktur** — *«fire neden bu seviyede?»* bir sorgu adı değil bir **reçete
    // adıdır** (`cube_query = null`, `tur = "neden"`). Onu besteciye yazmak, kullanıcıya
    // hiçbir yolun cevaplamadığı bir cümle bırakmak olurdu: `Enter`'a bastığında istek
    // `/ask`e gider ve garson aynı planı **LLM ile** yeniden kurmaya çalışır — yani
    // `§7`'nin `②` kademesi sessizce `③`e düşer, ve o tablonun başlığı *«karışmamalılar»*.
    //
    // ⚠ `onMakro` yoksa eski davranış **birebir** sürer (`KURAL B`).
    if (MAKRO_ADLARI.has(a.tur) && onMakro) {
      onMakro(a.tur, a.metin);
      setKapali(true);
      return;
    }
    // 🔴🔴 `§45` — HAZIR SORGU VARSA **KOŞ**; cümleyi yeniden anlattırma.
    //
    // ⟳ Buradaki eski not *«sorgu KOŞMAZ: `cube_query` taşısa bile tıklama yalnız metni
    // tamamlar»* diyordu. Ölçüldü ve **bu bir kusurdu**: cümle besteciye yazılıp `/ask`'a
    // gidiyor, `route()` onu *yarım isabet* sayıp **garsona** devrediyordu (`§51`). Yani
    // katalogdan **deterministik** üretilmiş, `cube_query`'si elimizde olan bir cevabı
    // sistem **LLM'e yeniden tahmin ettiriyordu** 🆤 — planın `§6 Thread 1`'i tam tersini
    // yazıyor: *«Enter → `cube_query` koşar · 34 ms · **0 token**»*.
    //
    // ⚠ Dal sırası **şart**: makro (sorgusuz) → hazır sorgu → metin. Ve `onSorgu` yoksa
    // eski davranış **birebir** sürer (`KURAL B`).
    if (a.cq && onSorgu) {
      onSorgu(a.cq, a.metin);
      setKapali(true);
      return;
    }
    onSec(a.metin);
    setKapali(true);
  }

  // `6.5` — Klavye: ↓↑ Enter Esc. **Poliş değil, iddianın kanıtı**: bir öneri şeridi
  // fareye mecbur bırakıyorsa yazarken-ara değildir.
  //
  // 🔴 **YAKALAMA (capture) fazında ve YALNIZ bu bestecide.** `CaretInput`'un kendi
  // `onKeyDown`'u `Enter`'ı **gönderime** çevirir; kabarma fazında dinleseydik önce o
  // çalışır, kullanıcı bir aday seçerken sorusunu **göndermiş** olurdu. `capture` +
  // `stopPropagation` sırayı tersine çevirir: şerit önce bakar, ilgilenmiyorsa
  // dokunmaz. *Bir tuşu iki sahip dinliyorsa, hangisinin kazandığı yazılı olmalıdır.*
  function tuslar(e: KeyboardEvent) {
    if (!adaylar.length) return;
    const durdur = () => { e.preventDefault(); e.stopPropagation(); };
    if (e.key === "ArrowDown") { durdur(); setSecili((s) => (s + 1) % adaylar.length); }
    else if (e.key === "ArrowUp") { durdur(); setSecili((s) => (s <= 0 ? adaylar.length : s) - 1); }
    else if (e.key === "Enter" && secili >= 0) { durdur(); sec(secili); }
    else if (e.key === "Escape") {
      // 🔴 `8.4` — «yazdı, hiçbirini tıklamadı» **NEGATİF** sinyaldir: gösterilenler
      // yanlıştı. Sessizce kapatmak, o bilgiyi çöpe atmak olurdu 🆆.
      durdur();
      oneriTik(metin.trim(), adaylar.map((a) => a.kimlik), -1);
      setKapali(true);
    }
  }

  // 🔴 `§44` — ÖNGÖRÜ SATIRI **ÇİP DEĞİL, LİSTE SATIRIDIR** (`§40` sözleşmesi).
  //
  // Ölçülen kusur (kullanıcı ekranı): cümleler yan yana çip olarak diziliyordu; bir
  // tamamlama listesi böyle okunmaz — göz **soldan aşağı** tarar. Üstelik aynı ekranda
  // pill satırı da çip olduğu için **iki katman ayırt edilemiyordu** (plan `1242`:
  // *«adımlar dikey, yuvalar yatay; ikisi aynı şeritte olmaz»*).
  //
  // ⚠ Erişilebilirlik plan `§40`'ın açık şartıdır: `listbox`/`option` + `aria-selected`.
  // Klavye (`↓↑ Enter Esc`) **zaten** kuruluydu; eksik olan **rolün ilanıydı** — ekran
  // okuyucu için bir çip yığını ile bir seçenek listesi aynı şey değildir.
  const pill = (a: Satir, i: number) => (
    <button
      key={a.kimlik}
      type="button"
      role="option"
      aria-selected={i === secili}
      id={`oneri-${i}`}
      onMouseDown={(e) => { e.preventDefault(); sec(i); }}
      className={
        "block w-full truncate rounded px-2 py-1 text-left transition-colors " +
        (i === secili
          ? "bg-accent/10 text-accent"
          : "text-neutral-500 hover:bg-hairline/40 hover:text-foreground")
      }
      title={a.ipucu}
    >
      {a.metin}
    </button>
  );

  // `5.9` — **BOŞ GİRDİ**: uç çağrılmaz, sohbetin kendi geçmişinden son bakılanlar
  // gösterilir. ⚠ *«En çok sorulanlar»* ve *«dikeyin çekirdek 5'i»* **uygulanmadı**:
  // ikisi de ölçüye dayanır ve o ölçü kodda **yok** (bkz. `5.5`'in gerekçeli ⊘'si) —
  // uydurulmuş bir sıralama, sıralama değildir ㊱.
  const bos = !metin.trim();
  // ⚠ Başlıklar yalnız **bağlam üstünde** en az bir cümle varken çizilir. Çapa yokken
  // her satır zaten *«yeni konu»*dur ve tek başına duran bir `↳ YENİ KONU` başlığı bilgi
  // değil gürültüdür. *Bir başlık, yalnız ayırdığı şey varsa ayırır.*
  const grupluCiz = adaylar.some((a) => a.grup === "rapor_ustunde");

  const serit = (() => {
    if (kapaliBayrak || !tercih || kapali) return null;
    if (bos) {
      return sonBakilanlar.length ? (
        <div className="flex flex-wrap items-center gap-1">
          <span className="select-none text-neutral-500">son bakılanlar:</span>
          {sonBakilanlar.slice(0, AZAMI).map((e) => (
            <button
              key={e}
              type="button"
              onMouseDown={(ev) => { ev.preventDefault(); onSec(e); }}
              className="rounded border border-hairline px-2 py-0.5 text-neutral-500 transition-colors hover:text-foreground"
            >
              {e}
            </button>
          ))}
        </div>
      ) : null;
    }
    if (!adaylar.length) return null;
    if (!grupluCiz) return <div className="flex flex-wrap gap-1">{adaylar.map(pill)}</div>;
    return (
      <div className="flex flex-col gap-1">
        {GRUP_SIRASI.map((g) => {
          const uyeler = adaylar.map((a, i) => [a, i] as const).filter(([a]) => a.grup === g);
          if (!uyeler.length) return null;
          return (
            <div key={g} className="flex flex-col gap-0.5">
              <span className="select-none text-[10px] uppercase tracking-wider text-neutral-500">
                {GRUP_BASLIK[g]}
              </span>
              <div className="flex flex-wrap gap-1">{uyeler.map(([a, i]) => pill(a, i))}</div>
            </div>
          );
        })}
      </div>
    );
  })();

  return (
    <div onKeyDownCapture={tuslar}>
      {/* 🔴 `§5.1` ÇAPA ÇUBUĞU — bayraktan **bağımsızdır**. `oneri_katmani` kapalıyken
          de çizilir, çünkü gösterdiği şey bir öneri değil **bağlamın kendisidir**: bu
          çubuk `ReportPanel`'in tepesindeki eski *«bağlam: X ×»* göstergesinin YERİNE
          geçti (tek sahip). Bayrağa bağlasaydık, bayrağı kapatmak var olan bir
          yeteneği **geri alırdı** — `KURAL B`'nin tam tersi. */}
      {capa && (
        <div className="mb-1.5 flex items-center gap-1.5 border border-hairline px-2 py-1 font-mono text-[10px] text-neutral-500">
          <span aria-hidden>📌</span>
          <span className="truncate" title={capa.ipucu ?? capa.etiket}>{capa.etiket}</span>
          {onCapaBirak && (
            <button
              type="button"
              onClick={onCapaBirak}
              title="Bu bağlamı bırak — panel temizlenir, sonraki soru YENİ bir konu açar. Bağlam yalnız bu açık eylemle değişir."
              className="ml-auto shrink-0 border border-hairline px-1 leading-tight transition-colors hover:border-accent/50 hover:text-foreground"
            >
              ✕ bağlamı bırak
            </button>
          )}
        </div>
      )}
      {children}
      {(serit || !kapaliBayrak) && (
        <div className="mt-1 flex items-start gap-2 font-mono text-xs">
          <div className="min-w-0 flex-1">{serit}</div>
          {/* 🔴 TUŞ — yalnız bayrak AÇIKKEN görünür (tercih, yetkiyi ezemez). */}
          {!kapaliBayrak && (
            <button
              type="button"
              onClick={() => tercihYaz(!tercih)}
              aria-pressed={tercih}
              title={tercih
                ? "Yazarken-ara önerilerini sustur — bu tarayıcıda hatırlanır (sorularınız etkilenmez)"
                : "Yazarken-ara önerilerini yeniden aç"}
              className={`shrink-0 select-none border px-1.5 py-0.5 text-[10px] transition-colors ${
                tercih
                  ? "border-hairline text-neutral-500 hover:text-foreground"
                  : "border-hairline text-neutral-500 opacity-[var(--opacity-soluk)] hover:opacity-100"
              }`}
            >
              öneri: {tercih ? "açık" : "kapalı"}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
