"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import type { AskResponse, CubeQuery, Report } from "@/lib/types";
import type { Thread } from "@/lib/threads";
import { Besteci } from "@/components/Besteci";
import { BrandMark } from "@/components/BrandMark";
import { DurdurDugmesi } from "@/components/DurdurDugmesi";
import { NextStepChips } from "@/components/NextStepChips";
import { ReportCard } from "@/components/ReportCard";
import { ReportView } from "@/components/ReportView";

// ⚠️ FAZ 0.23 — RAPORLANABİLİRLİK TEK SAHİPTE.
//
// Bu kapı eskiden `it.result || it.kpi` idi ve **İKİ YERDE ayrı ayrı** yazılıydı
// (`lastReportableIdx` hesabı + render dalı). Ama `ask.py`'nin *"cevap üstünde konuş"*
// dalı **`result` DÖNDÜRMEZ**: gövdeyi `contribution` (+ `prescription`) taşır — kodun
// kendi yorumu: *"Bulgular CEVABIN GÖVDESİDİR — `next_steps` DEĞİL … UI'da farklı
// görünmelidir."* Render edici (`ReportCard`) **zaten yazılmış ve doğruydu**
// (`item.cube_query && (item.result || item.contribution)`); **sırası hiç gelmiyordu.**
// Sonuç: Faz D2/G1/G3'te ödenmiş üç özellik (katkı ayrıştırması · reçete · chip'ler)
// ekranda YOKTU; geriye sarı bir not kalıyordu.
//
// Tek fonksiyon: *"aynı kuralın iki sahibi"* bu deponun 1 numaralı kusur sınıfı.
// **Yeni yetenek SIFIR** — çalışan, testli, makbuzlu bir motor görünmezden görünüre geçer.
//
// 🔴 **SAYMA — KAPAT (KAT-5).** İlk sürüm gövde alanlarını SAYIYORDU
// (`result|kpi|contribution|prescription`) ve denetim bunun bedelini ölçtü: listede
// olmayan **beşinci** gövde alanı `eylem_onerisi` — yani FAZ H'nin *"Onayla"* kartı,
// ürünün manşet vaadi — kapının dışında kalıyordu. `ReportCard`'ın TEK tüketicisi bu
// kapının arkasında olduğu için kullanıcı *"bundan sonra hep aylık göster"* dediğinde
// sarı bir not görüyor, **Onayla düğmesi hiç çıkmıyordu**. Yani 0.23'ün düzelttiği
// hatanın birebir aynısı, düzeltmenin KENDİ İÇİNE kodlanmıştı.
//
// Doğru biçim: **gövdeyi sayma, gövdesizliği kapat.** *"Saf not"* = yalnız açıklama/
// yönlendirme taşıyan cevap. Bunun dışında değeri olan HER alan bir gövdedir → yeni bir
// gövde alanı eklendiğinde bu liste güncellenmek zorunda DEĞİLDİR.
//
// Listenin yönü de bilinçli: buraya bir **taşıma/meta** alanı eklemeyi unutmak, saf-not
// cevabının kart olarak render edilmesine yol açar — **görünür** bir gerileme. Tersi
// (gövde alanını saymayı unutmak) **sessiz** bir kayıptı; bu tam da yaşandı.
// ⚠️ 🔴 **KÜME `AskResponse`'a göre değil, EKRANDAKİ NESNEYE göre kurulur.**
// İlk sürüm yalnız backend'in `app/schemas.py::AskResponse` alanlarını düşünüyordu; ama
// istemci cevaba **kendi alanını ekliyor**: `steering_golgede` (`types.ts`, `page.tsx`'te
// set edilir, backend bu alanı GÖNDERMEZ). O alan kümede olmadığı için, yönlendirme
// gölgesindeki **her saf-not cevabı** kart olarak render ediliyordu — hem gövdesiz bir
// kart, hem de `lastReportableIdx` olduğu için `viewHint`'i üstüne çekiyordu.
// Denetimde bulundu; kapı `test_SAF_NOT_ISTEMCI_ALANLARINI_da_KAPSIYOR` ile kilitli:
// **backend şemasında OLMAYAN her istemci alanı bu kümede OLMAK ZORUNDA.**
const SAF_NOT_ALANLARI = new Set<keyof AskResponse | string>([
  "question", "note", "suggestions", "next_steps", "trace", "source", "sql",
  "planned_sql", "cube_query", "view_hint", "is_new_topic", "thread_id",
  "reply_to_label", "explain", "job_id", "contract_id", "agent_run",
  "calculation_explanation",
  // — istemci-tarafı alanlar (backend göndermez, `page.tsx` ekler) —
  "steering_golgede",
  // 🔴🔴 `§7 ②` — **MAKRO'NUN İKİ META ALANI, VE BU KÜMENİN KENDİ UYARISININ AYNEN
  // TEKRARI.** `POST /oneri/makro` cevabına iki alan ekliyor: `makro` (koşan reçetenin
  // **adı**) ve `adim_sayisi` (kaç adım koştu). İkisi de bir **gövde** değil bir
  // künyedir — ne bir sonuç, ne bir grafik, ne bir öneri.
  //
  // ⊙ Ve kümeye yazılmasaydı kusur **dürüst reddin tam üstüne** düşerdi: makro
  // koşamadığında cevap `{source: null, makro: "neden", note: "<gerekçe>"}` olur, yani
  // gövdesi **yoktur** — ama `makro` dolu bir dize olduğu için `raporlanabilir()` `true`
  // döner ve cevap **gövdesiz bir rapor kartı** olarak çizilirdi. Saf-not dalı (ve onun
  // okunur gerekçesi) hiç çalışmazdı. Bu, `kanit_sinifi` ve `soz` vakalarının
  // **üçüncüsüdür**; bu dosyanın kendi cümlesi: *«buraya bir taşıma/meta alanı eklemeyi
  // unutmak, saf-not cevabının kart olarak render edilmesine yol açar.»*
  //
  // ⚠ `AskResponse`'a **tip olarak eklenmediler**: küme `keyof AskResponse | string`
  // kabul ediyor ve `types.ts` tavanında (`616/616`) bir satır boşluk yok. Bir alanı
  // tipe yazmak burada bir kazanç da vermezdi — ikisi de yalnız bu kümede okunuyor.
  "makro", "adim_sayisi",
  // 🔴 **GARSON FAZI — DİPNOTLAR, GÖVDE DEĞİL.** `G1`'in `temellendirme`si ve `G2`'nin
  // `diyalog_durumu`su bir cevabın **yanında** konuşur (rozet · bekleyen yuva); ikisi de
  // `ReportCard` içinde render edilir ama hiçbiri bir **rapor gövdesi** değildir.
  // Kümeye girmezlerse bir netleştirme cevabı ("hangi dönem?") yalnız bu dipnotlar
  // yüzünden **gövdesiz bir kart** olarak çizilir — bu dosyanın kendi uyarısıyla
  // *"görünür bir gerileme"*.
  //
  // ⚠ Ölçüldü ve bir sınır bulundu: `kanit_sinifi` de kümenin DIŞINDA ve netleştirme
  // cevaplarında **dolu geliyor** — yani o cevaplar bu fazdan ÖNCE de raporlanabilir
  // sayılıyordu. Bu satırlar o durumu **düzeltmez**, çünkü düzeltmek ölçülmemiş bir
  // davranış değişikliğidir; borç `OPERASYON-DURUM.md`'ye yazıldı.
  // *Kendi alanını sınıflandırmak bir sorumluluk; başkasınınkini ölçmeden değiştirmek
  // bir risktir.*
  "temellendirme", "diyalog_durumu",
  // 🔴 `DA-3` — **KAPI BİR TOTOLOJİYDİ.** `kanit_sinifi` `schemas.py:396`'da
  // `"olculmus"` VARSAYILANIYLA gelir ve `test_ai_act_uyumu` onu *"her yanıtta"* diye
  // kilitler → kümede olmadığı için `raporlanabilir()` **daima true** dönüyordu.
  //
  // İki sonucu vardı ve ikisi de görünürdü: (1) bir netleştirme cevabı (*"hangi dönem?"*)
  // **gövdesiz bir rapor kartı** olarak çiziliyordu — üstelik *kanıt sınıfı: ölçülmüş*
  // damgasıyla, yani bir SORUYA "ölçülmüş" deniyordu; (2) alttaki saf-not dalı ve onun
  // doğru başlığı (`"şunlardan biri mi?"`) **hiç çalışmıyordu**, kart varsayılan
  // `"sonraki adım"` başlığını basıyordu — deponun kendi yasakladığı **yanlış başlık**.
  //
  // ⚠ Gövdeler bu kümeye giremez ve bunu bir kapı kilitler
  // (`test_RAPORLANABILIRLIK_SAYMIYOR_KAPATIYOR`): `result` · `kpi` · `contribution` ·
  // `prescription` · `eylem_onerisi` · `interpretation` · `recommendations` · `viz`.
  // Yani gerçek bir gövde taşıyan cevap **yine** kart olur; değişen yalnız gövdesizler.
  //
  // *Her cevapta dolu olan bir alan, bir ayrım ölçütü olamaz — yalnız ayrımın olmadığını
  // gizler.*
  "kanit_sinifi",
  // 🔴 `soz` — `note`'un KARDEŞİ (`ReportCard` ikisini `item.soz || item.note` diye tek
  // blokta basar). `FAZ 5.17`'de eklenirken bu kümeye **yazılmamış**; kusur o gün
  // görünmedi çünkü `kanit_sinifi` zaten kapıyı totolojiye çevirmişti — bir kusur bir
  // başkasını gizliyordu. `kanit_sinifi` kapanınca `soz` ortaya çıktı.
  // *İki kusur üst üste bindiğinde, birini kapatmak ötekini bulur.*
  "soz",
]);

export function raporlanabilir(it: AskResponse): boolean {
  return Object.entries(it).some(([alan, deger]) => {
    if (SAF_NOT_ALANLARI.has(alan)) return false;
    if (deger === null || deger === undefined || deger === false) return false;
    if (Array.isArray(deger)) return deger.length > 0;
    if (typeof deger === "object") return Object.keys(deger).length > 0;
    return deger !== "";
  });
}

// §B Adım 2 (1 Ağustos 2026) — sağ panel artık İNCE bir YIĞIN kapsayıcısı: bir thread'in
// (aynı konudaki tüm cevaplar) item dizisini alır, her raporlanabilir item için bir
// <ReportCard> render eder (eski tek-rapor gövdesi ARTIK ReportCard'ta) — yeni cevap
// ÖNCEKİLERİ SİLMEZ, altına eklenir (kullanıcının "altta biriken akış" tarifi). `fb` (verify
// geri bildirim map'i) burada TEK, PAYLAŞILAN state olarak tutulur (içerik-anahtarlı olduğu
// için yığındaki TÜM kartlarda güvenle paylaşılabilir) — `pending`/`error` artık TÜM render'ı
// DEĞİŞTİRMEZ, yığının ALTINA eklenen bir kuyruk göstergesi/hata kutusu olur.
export function ReportPanel({
  thread,
  pending,
  aktifJobId,
  viewHint,
  onCubeEdit,
  onMakro,
  error,
  sessionId,
  contextLabel,
  onClearContext,
  onContinue,
  onReply,
  onReplyMulti,
  sonBakilanlar = [],
  tuval = null,
}: {
  thread: Thread | null;
  pending: boolean;
  // FAZ 1.12 · AI Act Md.14 — arka-plan işinin kimliği (yalnız uzun Discovery'de dolar);
  // durdurma düğmesi ancak bu doluyken görünür.
  aktifJobId?: string | null;
  // YALNIZ thread'in EN SON raporlanabilir item'ına geçirilir (bkz. aşağıdaki lastReportableIdx).
  viewHint?: { kind: string; nonce: number } | null;
  onCubeEdit?: (edit: { cq: CubeQuery; label: string }) => void;
  // 🔴 `§7 ②` — ADLANDIRILMIŞ MAKRO: `POST /oneri/makro`, **sıfır LLM**, N deterministik
  // adım. ⚠ Çapayı (`capa.cq`) ve kırılım boyutunu bu panel **verir**, çünkü ikisinin de
  // tek sahibi burasıdır (`capaCq` aşağıda `temellendirme` ile aynı kalemden okunuyor).
  // `page.tsx`'in bilmesi gereken tek şey cevabın nereye düşeceğidir.
  onMakro?: (ad: string, soru: string, cq: CubeQuery, boyut: string) => void;
  error: string | null;
  sessionId?: string;
  // §B DÜZELTMESİ (1 Ağustos 2026, 2. tur) — "bağlam: X" göstergesi ARTIK burada: eski sol
  // chat'in bu göstergesi kaldırıldı (kullanıcı: "bağlam olarak da mesela oee eklenebiliyor
  // küp bağlamı olarak vs o da sağda panelde olacak artık") — akış SAĞDA olduğu için bağlam
  // bilgisi de SAĞDA olmalı.
  contextLabel?: string | null;
  onClearContext?: () => void;
  // §B düzeltmesi (1 Ağustos 2026) — bu panelin KENDİ komposer'ı: aktif thread'in GÜNCEL
  // bağlamıyla devam eder (eski TEK komposer'ın bağlamsal davranışı, artık burada).
  onContinue?: (text: string) => void;
  // Bir karta "yanıtla": bağlam O ÇAPA karttan gelir, sonuç thread'in SONUNA eklenir.
  // `hucre` (Faz G2): grafikte işaret edilen koordinat — ReportCard'dan page.tsx'e
  // geçirilir, orada `AskRequest.anchor` olur.
  onReply?: (threadId: string, anchorIndex: number, text: string,
             hucre?: { dimension: string; value: string }) => void;
  // Birden fazla kart seçip birleşik bağlamla sor: çapa = seçilenlerin EN SONuncusu.
  onReplyMulti?: (threadId: string, anchorIndex: number, extraIndices: number[], text: string) => void;
  // 🔴 `5.9` — boş girdide gösterilen **son bakılanlar**. ⚠ Burada TÜRETİLMEZ, alınır:
  // kaynağı sohbetin TÜM thread'leridir (`page.tsx::sonBakilanEtiketler(threads)`) ve bu
  // panel yalnız AKTİF thread'i görür. Kendi listesini kursaydı, iki yerde iki farklı
  // *«son bakılanlar»* doğardı. *Bir listeyi göremediği veriden kurmak, onu daraltmaktır.*
  sonBakilanlar?: string[];
  // 🔴🔴 **`🗂 TUVAL` — BESTECİYİ KOPYALAMAK YERİNE GÖVDEYİ DEĞİŞTİRMEK (2026-08-13).**
  //
  // ⊙ Ölçülmüş gerileme: `page.tsx` tuval modunda `AnalysisCanvas`'ı bu panelin
  // **YERİNE** çiziyordu → o modda ekranda **hiçbir girdi kutusu kalmıyordu** (sol
  // besteci kaldırıldığı için ikinci bir kutu da yoktu). Kullanıcı yazamıyordu.
  //
  // 🔴 İki çare vardı ve ikisi çok farklı: ① tuvalin altına **ikinci bir besteci**
  // koymak — aynı özelliği üçüncü kez bakmak (`OneriSeridi` sarmalaması, çapa, tuşlar,
  // temizlik…); ② bu panelin **gövdesini** değiştirmek. ②'de kopya SIFIRDIR: besteci ·
  // çapa · bekleme/hata göstergesi · `pending` ayrımı tek sahipte kalır ve tuval yalnız
  // kaydırılan alanın içeriği olur. *Bir görünümü değiştirmek için sahibini
  // çoğaltmak gerekmiyorsa, çoğaltmamak gerekir.*
  //
  // ⚠ Verildiğinde kart yığını çizilmez ve **seçim çubuğu da çizilmez**: görünmeyen
  // kartları *«seç»* diye teklif etmek, yapılamayacak bir şeyi teklif etmektir.
  // ⊘ `null` (varsayılan) → bu dosya bayt bayt eski davranışını sürdürür.
  tuval?: ReactNode;
}) {
  // Verify geri bildirimi ("✓ doğru"/"✗ yanlış") İÇERİK-ANAHTARLI (verifyKey = label::sql) —
  // bu yüzden TÜM kartlar (hatta thread'ler) arasında GÜVENLE paylaşılabilir tek bir map.
  const [fb, setFb] = useState<Record<string, "ok" | "bad">>({});
  // 🔴 `§RP` — agentic rapor tam sayfa açılır. `AnalysisCanvas`/`DashboardView`'in
  // **aynı** deseni (`postReport → ReportView`); burada kaynak `/report` değil
  // orkestratörün cevabı. *Aynı belgeyi iki farklı görüntüleyiciyle çizmek, iki farklı
  // ürün yapmaktır.*
  const [acikRapor, setAcikRapor] = useState<Report | null>(null);
  // 🔴 `§RV-canvas` — açık belge **en sonuncuysa** düzenlenebilir ve yeni cevabı
  // **izler**. İkisi de aynı gerekçeden doğar: bir düzenleme isteği her zaman
  // `previous_rapor` ile gider, o da bağlamdaki (yani en son) belgedir. Eski bir belge
  // açıkken composer gösterseydik, istek ekrandakinden **başka** bir belgeye yazılırdı.
  // ⚠ `takip` olmadan kullanıcı düzenler ve ekranda **hiçbir şey değişmezdi** — canvas'ın
  // en can alıcı yerinde sessiz bir hiçlik. *Bir belgeyi düzenlemek, düzenlenmiş hâlini
  // görmekle tamamlanır.*
  const [takip, setTakip] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  // §B düzeltmesi (1 Ağustos 2026) — çoklu-seçim bağlam: hangi kartların seçili olduğu
  // (index'e göre, thread'in KENDİ item dizisindeki konum) + iki alt-komposer'ın metni.
  const [selectionMode, setSelectionMode] = useState(false);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [continueValue, setContinueValue] = useState("");
  const [multiValue, setMultiValue] = useState("");
  // Thread değişince seçim sıfırlanır — React'ın "render sırasında state ayarlama" deseni
  // (bkz. react.dev "Adjusting state when a prop changes"), `useEffect` içinde setState'in
  // gereksiz bir ekstra render turuna yol açmasını ÖNLER (eslint react-hooks kuralı).
  const [selectionResetKey, setSelectionResetKey] = useState(thread?.id);
  if (thread?.id !== selectionResetKey) {
    setSelectionResetKey(thread?.id);
    setSelectionMode(false);
    setSelected(new Set());
  }

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [thread?.id, thread?.items.length, pending]);

  // 🔴🔴 **TEK CHAT (2026-08-13) — BU PANEL ARTIK ERKEN DÖNMÜYOR.**
  //
  // Burada üç erken dönüş vardı (`error && !thread` · `pending && !thread` · `!thread`)
  // ve üçü de **besteciyi birlikte götürüyordu**. Sol besteci dururken bu zararsızdı:
  // soru sorulacak başka bir kutu vardı. Sol besteci kaldırılınca (kullanıcı kararı:
  // *«çift chat'e her özelliği girmek elim bir hata ve risk»*) aynı erken dönüş ürünün
  // **tek** girdi kutusunu yok ederdi — thread yokken soru sorulamaz hâle gelirdi.
  //
  // ⚠ Davranış kaybı YOK: üç durumun metni **aynen** duruyor, yalnız gövdeye taşındı;
  // besteci artık her hâlde alt kenarda kalıyor. *Bir boş durum, çıkış yolunu da
  // göstermek zorundadır.*
  const bosGovde = (
    <Center>
      {error ? (
        <div className="max-w-sm border border-red-300 bg-red-50 px-4 py-3 font-mono text-[13px] text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
          {error}
        </div>
      ) : pending ? (
        <div className="flex items-center gap-2 font-mono text-[13px] text-neutral-400">
          <span className="dima-caret" style={{ height: "0.9em" }} />
          yürütülüyor…
        </div>
      ) : (
        <div className="max-w-xs text-center font-mono text-[13px] text-neutral-400">
          <span className="dima-caret" style={{ height: "0.9em" }} /> aşağıdan sor — rapor burada belirir
        </div>
      )}
    </Center>
  );

  // "chip:" ile başlayan sentetik chip-düzenleme etiketleri gerçek bir soru DEĞİLDİR (bkz.
  // vqr.py::store — "chip etiketleri soru değildir") — verify bunlarla değil, GERİYE doğru en
  // yakın GERÇEK soruyla öğrenir. Sayfa-seviyeli tek `verifyLabel` state'i YERİNE her kart
  // KENDİ thread'indeki konumundan bunu türetir (thread değiştirmede/geçmişte gezinmede asla
  // bayatlamaz).
  const nearestRealQuestion = (items: AskResponse[], index: number): string | null => {
    for (let i = index; i >= 0; i--) {
      if (!items[i].question.startsWith("chip:")) return items[i].question;
    }
    return null;
  };
  let lastReportableIdx = -1;
  // FAZ 0.23 — aynı kapı (aşağıdaki render dalıyla TEK sahip). Eskiden `it.result || it.kpi`
  // burada TEKRAR yazılıydı → `lastReportableIdx`/`viewHint` de aynı körlüğü MİRAS ALIYORDU.
  thread?.items.forEach((it, i) => { if (raporlanabilir(it)) lastReportableIdx = i; });
  // `§RV-canvas` — bağlamdaki belge: `previous_rapor` her zaman **bunu** taşır.
  const sonBelge: Report | null =
    (lastReportableIdx >= 0 ? thread?.items[lastReportableIdx]?.rapor : null) ?? null;

  // 🔴 `§5.1` — **GÖRÜNÜR ÇAPA.** `📌 RAM-3 · toplam_fire_kg · bu ay`
  //
  // ⚠ Etiket burada **üretilmez, okunur**: tek sahibi `temellendirme`dir (*«anladığım
  // şu»* — kaynağı yalnız `cube_query`, 0 LLM). İkinci bir okuma yazmak, aynı cümlenin
  // iki yerde ayrışması demekti (`Temellendirme.tsx`'in kendi şerhi: *bir yeteneği iki
  // yere koymak, onu iki kez kazanmak değil iki kez bakmaktır*). Alan sırası da onunla
  // birebir aynı: kapsam (`cube`) **önce** — `DA-7`'nin ölçtüğü `WRONG_SCOPE` %14,4.
  //
  // 🔴 Kapı `contextLabel`dir, `temellendirme` DEĞİL: bir sonraki isteğin bağlam taşıyıp
  // taşımadığını yalnız `page.tsx`'in `contextCq`'su bilir. Temellendirmesi olan ama
  // bağlamı düşmüş bir karttan çapa çizmek, **tutulmayacak bir söz** olurdu.
  // ⚠ Son item bilerek: `contextCq` da son cevaptan kurulur; daha eski bir karta bakmak
  // ekrandaki çapayı gönderilenden ayırırdı.
  //
  // ⚠ `cq` de **aynı** kalemden okunur ve uca gider (`getOneri` onu parçalı query
  // paramına çevirir): sunucunun `BU RAPOR ÜZERİNDE` bandı çapasız **boş** döner. Etiketi
  // bir kalemden, sorguyu başka bir kalemden almak, ekranda yazan bağlam ile üretilen
  // önerilerin ayrışması demekti.
  //
  // ⚠ `useMemo` bir performans süsü değil bir **kimlik** kararıdır: `OneriSeridi`'nin
  // getirme etkisi `capa`ya bağlıdır; her render'da yeni bir nesne üretmek, alakasız her
  // render'da typeahead isteğini yeniden zamanlardı (sıcak yol, `p95` bütçeli).
  const capaTemeli = thread?.items.at(-1)?.temellendirme;
  const capaCq = thread?.items.at(-1)?.cube_query ?? null;
  const capaEtiketi = contextLabel
    ? [capaTemeli?.cube, capaTemeli?.olcu, capaTemeli?.donem,
       ...(capaTemeli?.kirilim ?? []), ...(capaTemeli?.filtreler ?? [])]
        .filter(Boolean).join(" · ") || contextLabel
    : null;
  const capa = useMemo(
    () => (capaEtiketi ? { etiket: capaEtiketi, cq: capaCq } : null),
    [capaEtiketi, capaCq],
  );

  // §B düzeltmesi (1 Ağustos 2026) — çoklu-seçim: en-son (en büyük index) seçilen kart
  // yapısal ÇAPA olur (kendi cube_query/sql'i normal follow-up gibi kullanılır), geri
  // kalanı `extra_context` olarak (yalnız Discovery grounding'i, backend'de bilinçli
  // kapsam sınırı — bkz. ask.py::_with_extra_context) eklenir.
  // ⚠ Metin artık **parametreyle** gelir: kırpma ve boş koruması `Besteci`'nin tek
  // kapısında yapılır (bkz. o dosyanın `onGonder` şerhi). Geri kalan her şey aynı.
  const submitReplyMulti = (t: string) => {
    if (!thread || !onReplyMulti || selected.size === 0) return;
    const idxs = Array.from(selected).sort((a, b) => a - b);
    const anchorIndex = idxs[idxs.length - 1];
    const extraIndices = idxs.slice(0, -1);
    onReplyMulti(thread.id, anchorIndex, extraIndices, t);
    setMultiValue("");
    setSelected(new Set());
    setSelectionMode(false);
  };

  return (
    <>
    {acikRapor && (
      <div className="fixed inset-0 z-50 bg-background">
        <ReportView
          report={takip ? (sonBelge ?? acikRapor) : acikRapor}
          onClose={() => { setAcikRapor(null); setTakip(false); }}
          onSor={takip ? onContinue : undefined}
        />
      </div>
    )}
    <div className="flex h-full min-h-0 flex-col">
      {/* §B DÜZELTMESİ (1 Ağustos 2026, 2. tur) — üst çubuk: SOLDA aktif bağlam göstergesi
          (eski sol chat'ten taşındı), SAĞDA seçim modu toggle'ı + sayaç. Thread değişince
          seçim otomatik sıfırlanır (bkz. yukarıdaki render-sırasında-ayarlama).

          🔴 **BAĞLAM GÖSTERGESİ BURADAN TAŞINDI (`§5.1`, 2026-08-13)** — silinmedi,
          **yerini değiştirdi**: artık bestecinin hemen üstündeki 📌 çapa çubuğu
          (`OneriSeridi`). İki gerekçe:
          ① `§5.1`'in çizimi onu yazının yanına koyuyor — panelin tepesinde duran bir
             bağlam, kullanıcının BAKMADIĞI yerde durur.
          ② İkisini birden çizmek *«bağlamı bırak»* ediminin **iki sahibi** demekti; bu
             deponun bir numaralı kusur sınıfı. `onClearContext` hâlâ TEK fonksiyon —
             yalnız düğmesi taşındı. */}
      {/* ⚠ Thread yokken çubuk hiç çizilmez: seçilecek kart yokken *«kartları seç»*
          teklif etmek, yapılamayacak bir şeyi teklif etmektir. ⊙ `!tuval` aynı
          cümlenin ikinci hâli: tuval kipinde kart yığını ekranda **yok**. */}
      {thread && !tuval && (
      <div className="flex shrink-0 items-center gap-2 border-b border-hairline px-4 py-1.5">
        <button
          onClick={() => { setSelectionMode((m) => !m); setSelected(new Set()); }}
          className={`border px-2 py-0.5 font-mono text-[11px] transition-colors ${
            selectionMode
              ? "border-accent/40 text-accent"
              : "border-hairline text-neutral-400 hover:text-foreground"
          }`}
        >
          {selectionMode ? "✕ seçimi bitir" : "☐ kartları seç"}
        </button>
        {selectionMode && (
          <>
            <span className="font-mono text-[11px] text-neutral-400">{selected.size} seçili</span>
            {selected.size > 0 && (
              <button
                onClick={() => setSelected(new Set())}
                className="font-mono text-[11px] text-neutral-400 underline-offset-2 transition-colors hover:text-foreground hover:underline"
              >
                temizle
              </button>
            )}
          </>
        )}
      </div>
      )}
      <div ref={scrollRef} className="min-h-0 flex-1 overflow-auto">
        {/* 🔴 GÖVDE = tuval **ya da** kart yığını **ya da** boş durum. Üçü de aynı
            kaydırılan alanın içeriğidir; besteci hepsinin altında AYNI yerde kalır. */}
        {tuval ? tuval : !thread ? bosGovde : thread.items.map((it, i) => {
          if (raporlanabilir(it)) {
            return (
              <ReportCard
                key={`${thread.id}-${i}`}
                item={it}
                onRaporAc={(r) => { setAcikRapor(r); setTakip(r === sonBelge); }}
                index={i}
                threadId={thread.id}
                viewHint={i === lastReportableIdx ? viewHint : null}
                onCubeEdit={onCubeEdit}
                precedingLabel={nearestRealQuestion(thread.items, i)}
                sessionId={sessionId}
                fb={fb}
                setFb={setFb}
                onReply={onReply}
                selectable={selectionMode}
                selected={selected.has(i)}
                onToggleSelect={() =>
                  setSelected((s) => {
                    const n = new Set(s);
                    if (n.has(i)) n.delete(i);
                    else n.add(i);
                    return n;
                  })
                }
              />
            );
          }
          // §B DÜZELTMESİ (1 Ağustos 2026, 2. tur) — not-yalnız (result/kpi'siz, ör.
          // netleştirme/upload bildirimi) item'lar ARTIK burada, hafif bir blok olarak
          // render edilir — bu akış eskiden SADECE sol chat'te vardı, kullanıcı: "follow
          // up önerileri artık sağda gelmeli çünkü artık thread sağda akacak". Öneri-chip'i
          // tıklaması bu SPESİFİK item'a anchor'lı bir "yanıtla" (aynı mekanizma, `onReply`).
          if (it.note) {
            return (
              <div key={`${thread.id}-${i}-note`} className="mx-auto max-w-4xl px-8 py-4">
                <h3 className="mb-1.5 font-mono text-[13px] leading-snug text-foreground">
                  {it.question}
                </h3>
                <div className="border-l-2 border-amber-500/50 bg-amber-500/[0.04] py-1.5 pl-3 font-mono text-[12px] leading-snug text-neutral-500">
                  {it.note}
                </div>
                {/* 🔴 `§38 D4` — **KIND SÜZGECİ BU DALDA YOKTU** (⟳ 2026-08-12).
                    `ReportCard` üç edimi ayırıyor (`!s.kind` devam · `"tanim"` başka
                    tanım · `"turetme"` bunu mu demek istedin) ama bu saf-not dalı
                    HEPSİNİ tek tip butona basıyordu. Backend sözleşmesi
                    (`app/belirsizlik_chipi.py:51`) *«Frontend bunu AYRI bir grupta ve
                    KENDİ açıklamasıyla basar»* diyor ve **bileşen ayrımı yapmıyor** —
                    yani bu dal da o cümlenin kapsamındaydı.
                    ⚠ *«Bu sayı BAŞKA BİR HESAP»* chip'i ile *«tedarikçi kırılımı»*
                    chip'i aynı görünüyorsa, kullanıcı hangisinin YENİ BİR SAYI
                    getireceğini bilemez — ve bir chip'in yanındaki açıklama, chip'in
                    kendisi kadar bir vaattir. */}
                {it.suggestions && it.suggestions.filter((s) => !s.kind).length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {it.suggestions
                      .filter((s) => !s.kind)
                      .map((s) => (
                        <button
                          key={s.label}
                          onClick={() => onReply?.(thread.id, i, s.query)}
                          className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-600 transition-colors hover:border-accent/50 hover:text-foreground dark:text-neutral-300"
                        >
                          {s.label}
                        </button>
                      ))}
                  </div>
                )}
                {it.suggestions && it.suggestions.some((s) => s.kind === "tanim") && (
                  <div className="mt-2 border-l-2 border-amber-400/60 pl-3 dark:border-amber-500/50">
                    <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-amber-600 dark:text-amber-400">
                      başka tanım
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {it.suggestions
                        .filter((s) => s.kind === "tanim")
                        .map((s, k) => (
                          <button
                            key={`tanim-${k}`}
                            onClick={() => onReply?.(thread.id, i, s.query)}
                            title="Aynı soruyu bu tanımla yeniden sorar — yeni bir sayı gelir"
                            className="border border-amber-400/50 px-2 py-1 font-mono text-[11px] text-amber-700 transition-colors hover:border-amber-500 hover:bg-amber-50 dark:text-amber-300 dark:hover:bg-amber-950/30"
                          >
                            <span className="mr-1 opacity-60">⇄</span>
                            {s.label}
                          </button>
                        ))}
                    </div>
                  </div>
                )}
                {/* ⚠️ FAZ 0.23 — SAF-NOT dalında `next_steps` YOKTU (ölçüldü:
                    `grep -n "next_steps" ReportPanel.tsx` → 0 isabet). Sonuç:
                    `_intent_uyusmazlik_chipi` (`ask.py`) *"Hangi ölçüyü istiyorsun?"*
                    diye soruyordu ve **altında tıklanacak hiçbir şey yoktu.**
                    Desen `ReportCard.tsx`'in K2 bloğunun AYNISI — `onCubeEdit` →
                    `/cube`, **0 LLM**. `suggestions`'tan AYRI durur: o yeni bir SORU
                    sorar (`onReply`), bu ise mevcut sorguyu DÜZENLER (`cube_query` taşır). */}
                {onCubeEdit && (
                  <NextStepChips
                    steps={it.next_steps}
                    onCubeEdit={onCubeEdit}
                    // ⚠ Bu dal bir NETLEŞTİRME cevabıdır ("Hangi ölçüyü istiyorsun?").
                    // Buradaki liste bir SORUNUN ŞIKLARIDIR; "sonraki adım" başlığı
                    // `ReportCard`'ın kendi gerekçesiyle YANLIŞ BAŞLIK olurdu.
                    baslik="şunlardan biri mi?"
                  />
                )}
              </div>
            );
          }
          return null;
        })}
        {/* ⚠ `thread &&`: thread yokken bu iki blok `bosGovde` içinde ZATEN çiziliyor —
            koşulsuz bırakmak aynı beklemeyi/hatayı **iki kez** göstermek olurdu.
            🔴 `|| tuval`: tuval kipinde `bosGovde` çizilmez, yani thread henüz yokken
            bekleme/hata **hiçbir yerde** görünmezdi — bestecisi olan bir yüzeyin
            geri bildirimi de olmak zorundadır. *Yazdıran, cevabın nerede olduğunu da
            söylemelidir.* */}
        {(thread || tuval) && pending && (
          <div className="mx-auto flex max-w-4xl items-center gap-2 px-8 py-4 font-mono text-[13px] text-neutral-400">
            <span className="dima-caret" style={{ height: "0.9em" }} />
            yürütülüyor…
            {/* FAZ 1.12 · AI Act Md.14 — durdurma BEKLEMENİN yanında durur. Yalnız
                arka-plana kuyruklanan (uzun Discovery) işte görünür; senkron yolda
                `aktifJobId` hiç dolmaz ve düğme hiç çizilmez. */}
            <span className="ml-auto">
              <DurdurDugmesi jobId={aktifJobId ?? null} />
            </span>
          </div>
        )}
        {(thread || tuval) && error && (
          <div className="mx-auto max-w-4xl px-8 py-4">
            <div className="max-w-sm border border-red-300 bg-red-50 px-4 py-3 font-mono text-[13px] text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
              {error}
            </div>
          </div>
        )}
      </div>
      {/* §B düzeltmesi (1 Ağustos 2026) — alt komposer(lar): seçim modunda ve ≥1 kart
          seçiliyken "birleşik bağlam" çubuğu; aksi halde normal "devam et" çubuğu — ikisi
          karşılıklı dışlayıcı.

          🔴🔴 **TEK CHAT (2026-08-13).** Bu artık *"sağdaki"* besteci değil, ürünün
          **TEK** girdi kutusudur: sol panelin komposer'ı kaldırıldı ve yerine yalnız
          `+ yeni sohbet` düğmesi geçti (`ChatPanel.tsx`). Kullanıcının kendi gerekçesi:
          *«çift chat'e her özelliği girmek elim bir hata ve risk»* — bir yeteneği iki
          kutuya bağlamak, onu iki kez gözden geçirmek demekti.

          ⚠ Thread yokken de çizilir ve o hâlde `onContinue` bağlamsız gider (`contextCq`
          · `prevSql` · `thread_id` hepsi `null`) — yani `page.tsx`'in `"continue"` dalı
          o durumda **taze** bir istek üretir ve `onSuccess` yeni bir thread kimliği
          basar. Eski sol komposer'ın işi böylece kaybolmadan taşındı.

          🔴 `OneriSeridi` **besteciyi sarmalar**: 📌 çapa üstte, öneri şeridi altta,
          `↓↑ Enter Esc` yalnız odaktaki kutuda (bkz. o dosyanın başlığı).

          🔴🔴 **GÖVDE ARTIK `Besteci.tsx`'te (2026-08-13).** Burada aynı sarmalama
          **iki kez** yazılıydı; `🗂 tuval` kipinde bir üçüncüsü gerekince kopya bir
          borç olmaktan çıkıp bir **kusura** dönüşürdü. Çıkarıldı: aşağıdaki iki
          çağıran (çoklu-seçim · devam et) artık **tek** uygulamayı koşuyor.
          ⊙ Ve tuval kipi bir **üçüncü çağıran bile açmadı**: tuval bu panelin gövdesi
          olarak geçtiği için besteci zaten olduğu yerde kalıyor — *bir görünümü
          değiştirmek için sahibini çoğaltmak gerekmiyorsa, çoğaltmamak gerekir.*
          ⚠ Kaybolan davranış YOK: çapa · şerit · tuşlar · `busy` · `ipucu` hepsi
          prop olarak geçiyor, `secili = -1` kararı `OneriSeridi`'nin içinde duruyor. */}
      {/* ⚠ `!tuval`: seçim çubuğu tuval kipinde çizilmediği için oradan seçimden
          **çıkılamaz**; birleşik kutuyu orada göstermek kullanıcıyı çıkışı olmayan bir
          kipte bırakırdı. Seçim SİLİNMEZ, yalnız kutusu beklemeye alınır — kart
          yığınına dönünce çubuk da seçim de olduğu gibi yerinde. */}
      {selectionMode && !tuval && selected.size > 0 && onReplyMulti ? (
        <Besteci
          deger={multiValue}
          onDeger={setMultiValue}
          onGonder={submitReplyMulti}
          busy={pending}
          sonBakilanlar={sonBakilanlar}
          ustBilgi={`${selected.size} kart birleştirilerek soruluyor`}
          vurgulu
        />
      ) : (
        onContinue && (
          <Besteci
            deger={continueValue}
            onDeger={setContinueValue}
            onGonder={(t) => { onContinue(t); setContinueValue(""); }}
            busy={pending}
            sonBakilanlar={sonBakilanlar}
            capa={capa}
            onCapaBirak={onClearContext}
            // 🔴 `§7 ②` — makro **yalnız bir çapa varken** koşabilir: *«neden bu
            // seviyede?»* sorusunun öznesi ekrandaki sayıdır ve sunucu da bunu yazıyor
            // (*«çapasız bir makronun öznesi yoktur ve tıklandığında düşer»*). `capaCq`
            // yokken prop hiç verilmez → şerit o satırı bugünkü gibi metne tamamlar.
            // ⚠ `boyut`: reçeteler (`neden` · `en_kotu`) bir **kırılım** ister ve tek
            // meşru kaynağı çapanın kendi `dimensions`'ıdır. Burada bir boyut **seçmek**
            // (*«ilk boyutu alıveririm»* diye şemadan devşirmek) kullanıcının sormadığı
            // bir kırılımı ona kendi sorusu gibi göstermek olurdu. Boş kalırsa sunucu
            // 400 + Türkçe gerekçe döner ve o gerekçe kullanıcıya **ulaşır**.
            onMakro={capaCq && onMakro
              ? (ad, soru) => onMakro(ad, soru, capaCq,
                  String(((capaCq.dimensions as unknown[]) ?? [])[0] ?? ""))
              : undefined}
            ipucu={thread ? "bu rapor üzerinde devam et…" : "sor…"}
          />
        )
      )}
    </div>
    </>
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
