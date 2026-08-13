"""**FRONTEND MODÜL BÜYÜME KAPISI** — `0.21`'in arayüz yarısı. *(denetim F5)*

## 🔴 Ölçülen risk

`ask.py` **2.498 satıra** çıktı ve ancak bir kapı kurulunca durdu. Frontend'de o kapı
**hiç yoktu**:

```
ls backend/tests/test_modul_buyume.py                    # var — yalnız backend
grep -rn "ReportCard" backend/tests/test_modul_buyume.py # → 0
```

`ReportCard.tsx` bugün **948 kod satırı · 25 buton**: cevap-sonrası **tüm** etkileşim
orada (zamanla · panoya ekle · doğrula · yanlış bildir · drill · makbuz · karta yanıt ·
onay kartı · SQL · sözleşme · çapa · hücre kırılımı).

> ⚠ Denetimin kendi ifadesiyle bu *"bir kusur değil bir **risktir**"* — ve `ask.py`
> **tam bu şekilde** büyüdü. *Bir tavan, aşıldıktan sonra konursa bir tavan değil bir
> onaydır.*

## 🔴 TAVAN = BUGÜNKÜ ÖLÇÜM, hedef değil

Küçültmek serbesttir ve ayrı bir maddedir; bu kapı **büyümeyi** durdurur. Sayılar
`kapi_ortak.yorumsuz()` ile **yorumsuz** ölçülür — bu depoda yorumlar gerekçe taşır ve
onları saymak, **belgelemeyi cezalandırırdı**.

⚠ Tavan aşıldığında yapılacak şey **tavanı yükseltmek değil**, davranışı bir modüle
çıkarmaktır (`Makbuz.tsx` · `SertifikaBandi.tsx` · `HataSeridi.tsx` · `GeriAlSeridi.tsx`
bu turda tam olarak böyle doğdu). Gerçekten muaf bir iş ise `MUAFIYET`'e **gerekçesiyle**
yazılır — *gerekçesiz bir muafiyet, muafiyet değil sessiz bir tavan artışıdır.*
"""

from __future__ import annotations

import pytest

from tests.kapi_ortak import fe_dosyalari, yorumsuz

#: `dosya → tavan` (kod satırı, yorumsuz). **Ölçülen değerler** — 2026-08-05.
#: ⚠ Yalnız *"ağırlık merkezi"* dosyalar: her dosyaya tavan koymak, kapıyı bir
#: bürokrasiye çevirir ve **hiçbirine bakılmaz** hâle getirir.
TAVANLAR = {
    # 🔴 **948 → 1009 (2026-08-06) ve bu ARTIŞIN İKİ AYRI SAHİBİ VAR — ikisi de yazılı.**
    #
    # ⊙ +37 · `7595250` (KÖK-2/KÖK-3): `eksik_niyet` uyarı şeridi. Backend cevabı artık
    #   *"sayı doğru ama sorunun bir parçası taşınmadı"* diyor ve bunun bir TÜKETİCİSİ
    #   olmadan özellik "bitti" değildir (deponun *arka-ön bütünlüğü* kuralı).
    #   🔴 Ve bu artış kapıyı KIRMIZIYA ÇEVİRDİ, kimse görmedi: yerel kapı 2026-08-04'te
    #   **yalnız korpusa** indirildi ve süit gecelik CI'ya taşındı. Üç commit boyunca
    #   kırmızı kaldı. *Bir kapıyı ucuzlaştırmak, onu görünmez yapmanın da yoludur.*
    #
    # ⊙ +24 · KÖK-9 belirsizlik chip'i: `suggestions[].kind === "tanim"` bloğu.
    #   TAŞINAMAZ ve sebebi ÜÇÜNCÜ BİR EDİM olması: "devam sorusu" bu cevabın ÜSTÜNDE
    #   konuşur, "sonraki adım" bu SORGUYU düzenler, bu ise AYNI SORUYU BAŞKA BİR TANIMLA
    #   yeniden sorar. Var olan kutuya koymak, o kutunun kullanıcıya verdiği sözü
    #   ("yeni sorgu yazılmaz") YALAN yapardı. *Bir chip'in yanındaki açıklama, chip'in
    #   kendisi kadar bir vaattir.*
    #
    # ⚠ Tavan MUAFIYET listesine değil buraya yazıldı: `test_KAPI_SAHTE_DEGIL` bu dosyada
    # `n == TAVANLAR[dosya]` arıyor (boşluksuz tavan), muafiyet toplamına değil.
    # ⊙ +24 · KÖK-7d TÜRETME chip'i (`kind === "turetme"`). ÜÇÜNCÜ değil DÖRDÜNCÜ bir
    # edim ve kendi kutusunu hak ediyor: "devam sorusu" bir CEVABIN üstünde konuşur,
    # "sonraki adım" bir SORGUYU düzenler, "başka tanım" aynı soruyu başka tanımla sorar
    # — bu ise bir REDDİN yanında durur ve sorunun KENDİSİNİ düzeltir ("ne kadar sattık"
    # → "ciro"). Var olan bir kutuya konsa kullanıcı bir cevabın devamı sanardı; oysa
    # ortada cevap yok, red var. *Bir chip'in bulunduğu kutu, ne vaat ettiğini söyler.*
    # ⊙ 1033 → 1032 (2026-08-07, `G1`): temellendirme rozet dizisi bu dosyaya yazıldı,
    # kapı yakaladı, **bileşene çıkarıldı** (`Temellendirme.tsx`) ve dosya bir satır
    # KÜÇÜLDÜ. Tavan ölçülen değere ÇEKİLDİ — `test_KAPI_GERCEKTEN_KIRMIZI_VERIYOR`
    # boşluk bırakmayı yasaklıyor: *kırmızı veremeyen bir kapı, olmayan bir kapıdır.*
    # ⊙ 1032 → 1035 (`G2`): `<DiyalogDurumu item={item} />` + import + yorum. Render
    # ZATEN bileşene çıkarılmış hâlde geldi (G1'in dersi) — burada kalan yalnız ÇAĞRI.
        # ⊙ +2 · `G6` FRAGMENT SARMALAYICISI (`<>` + `</>`) — **derleme için zorunlu**.
    #   `G2` `<DiyalogDurumu>`'yu `<NextStepChips>`'in yanına sarmalayıcısız koydu ve dosya
    #   **TS1005 ile derlenmiyordu**; kusur bir demet boyunca görünmedi çünkü yerel kapı
    #   yalnız `pytest` koşuyor — `tsc` bu operasyonda **hiç çağrılmamıştı**.
    #   🔴 TAŞINAMAZ: iki satır bir davranış değil bir **sözdizimi zorunluluğudur**. Tavanın
    #   amacı davranış birikimini durdurmaktır, derleyicinin dilbilgisini değil. Bir
    #   bileşene çıkarmak, iki satırdan kaçmak için bir dosya açmak olurdu.
    #   Kapısı: `tests/test_frontend_derlenir.py`.
    #   *Bir dilin derleyicisi koşulmuyorsa, o dilde yazılan her şey denetimsizdir.*
    # ⊙ +1 · `DA-8` — `vurgula` içe aktarımı. Backend `**kalın**` yazıyor, ekranda
    #   yorumlayıcı yoktu → kullanıcı **yıldızları okuyordu**. Yorumlayıcı bir bileşene
    #   değil `src/lib/vurgu.tsx`'e çıkarıldı (tavanın kendi talimatı); burada kalan
    #   yalnız **bir içe aktarım satırı**. *Bir vurgu işareti, yorumlanmadığında
    #   vurgunun tersini yapar.*
    # ⊙ +2 · `DA-7`/`flex-wrap` — rozet çubuğu `shrink-0` idi ve SARMIYORDU: `Temellendirme`
    #   rozetleri (kırılım+filtre sayısı sınırsız) çubuğu taşırıp kardeş sütundaki soru
    #   başlığını (`min-w-0 flex-1`) sıfıra eziyordu. **Taşınamaz:** bu bir bileşen değil
    #   kardeş sütunlar arası bir **düzen kuralı**; bir bileşene çıkarmak kuralı ait
    #   olduğu yerden koparırdı. *Sarmak, sınırsız bir listeyi sınırlı bir alana
    #   sığdırmanın doğru yoludur; kırpmak bilgiyi siler.*
    # 🔴 **1040 → 1048 (`FAZ 6`, 2026-08-09).** ⚠ Tavan `MUAFIYET` listesine DEĞİL
    # buraya yazıldı ve bu bir tercih değil bir **zorunluluk**: `test_KAPI_GERCEKTEN_
    # KIRMIZI_VERIYOR` bu dosyayı **doğrudan tablodan** okur (`n == TAVANLAR[dosya]`),
    # çünkü kapının kırmızı verebildiğini kanıtlamak için tavanda **boşluk olmamalı**.
    # Muafiyetle yükseltmek tavanı 1048 yapar ama tabloyu 1040'ta bırakır — meta-kapı
    # o boşluğu görür ve haklı olarak *"kapı büyümeyi durdurmuyor"* der.
    #
    # ⊙ Sekiz satırın hesabı: davranışın kendisi zaten bir bileşene **çıkarıldı**
    # (`PlanAdimlari.tsx`, 123 satır); burada kalan yalnız **kablo** — import (1) ·
    # bileşen çağrısı (1) · adım kanıtı için iki durum satırı (2) · panelin kimlik
    # seçimi (4). Bunları da çıkarmak, kartın hangi paneli açtığını karttan **ayırmak**
    # olurdu; `InterpretationBar` çapasının muafiyetiyle birebir aynı gerekçe.
    #
    # 🔴 Ve dördü bir kusuru **gidermek** için: ölü `/contracts/{id}` bağlantısı (404)
    # kapatıldı. *Bir kusuru gidermenin bedeli de tavandan ödenir — ama ödenmiş olması
    # yazılmalıdır.*
    # ⟳ **1048 → 1064 (`§RP`, 2026-08-10).** Bu dosyada tavan **ölçülen değere çekilir**
    # (`test_KAPI_GERCEKTEN_KIRMIZI_VERIYOR` sıfır boşluk şart koşar) — yani artış burada
    # görünür olmak **zorundadır**, muafiyet listesine saklanamaz.
    # 🔴 Δ=16: agentic raporu **tam sayfa açan kapı**. ⚠ **YENİ RENDER KODU YOK** — belgeyi
    # `ReportView` çizer (`AnalysisCanvas`/`DashboardView` ile AYNI desen). Onaltı satırın
    # çoğu, düğmenin **neden kartın içine gömülmediğini** yazan şerh: bir sohbet kartı bir
    # rapor sayfası değildir ve beş bloğu oraya sığdırmak ikisini de bozardı.
    # 🔴 Koşul `item.rapor` üzerinde: alan boşken blok **hiç render edilmez** (`KURAL B`).
    "components/ReportCard.tsx": 1064,
    # ⊙ +22 · `FAZ 6.1/8.1` ÖNERİ UCU SARMALAYICILARI (`getOneri` · `oneriTik` ·
    # `OneriAdayi`/`OneriYaniti` tipleri).
    #
    # ⚠ **Bileşene çıkarılamadı ve nedeni ölçüldü** 🅗: `test_uc_yetim_degil.py`
    # sarmalayıcıları **`api-client.ts` içinde** arıyor (*«api-client.ts'te uç
    # sarmalayıcısı bulunamadı — çapa kaymış»*). Ayrı bir `oneri-api.ts` açmak bu
    # dosyayı küçültürdü ama **öteki kapıyı kör ederdi** — bir borcu başka bir borca
    # taşımak olurdu 🆝.
    #
    # ⚠ Δ tam ölçülen fazladır (**814 − 792 = 22**), yuvarlanmadı 🅜; boşluk bırakmak
    # `test_KAPI_SAHTE_DEGIL`'i kırmızı verir.
    "lib/api-client.ts": 814,
    "lib/chart.ts": 688,
    # ⊙ 579 → 581: +1 `eksik_niyet?: string[]` (KÖK-3) · +1 `Suggestion.kind?` (KÖK-9).
    # ⚠ İkisi de bir ALAN BEYANIDIR, mantık değil — tip dosyasının büyümesi burada
    # backend sözleşmesinin büyümesidir ve onu cezalandırmak, sözleşmeyi belgesiz
    # bırakmayı ödüllendirirdi.
    #
    # ⊙ 581 → 585 (2026-08-07, garson ara fazı) — **aynı gerekçe, iki yeni sözleşme alanı:**
    #   +1 `hava_boslugu?: {yer_tutucu, bozulan}` (`G0b`) — gerçek değer/sayı yer tutucuya
    #      çevrildi; kullanıcı verisinin ÇIKMADIĞINI görebilmeli.
    #   +4 `temellendirme?: {cube, olcu, donem, granulerlik, kirilim[], filtreler[]}` (`G1`)
    #      — *"anladığım şu"*; 0 LLM, 0 token.
    #   🔴 İkisi de `test_cevap_alani_yetim_degil.py` tarafından ZORUNLU kılınıyor: backend
    #   alanı tüketicisiz kalamaz. Yani bu artış bir tercih değil, **başka bir kapının
    #   emri**. Tipi yazmamak, alanı yetim bırakmak olurdu.
    #
    # ⊙ 585 → 588 (`G2`): +3 `diyalog_durumu?: {acik_slotlar, sorulan, dolu, tur_no}`.
    #   Aynı gerekçe: bir ALAN BEYANI. Ve `test_cevap_alani_yetim_degil` onu ZORUNLU
    #   kılıyor — tipi yazmamak, alanı yetim bırakmak olurdu.
    # ⊙ +6 · 🔴 `G2` — `DiyalogDurumu` **paylaşılan** tipe çıktı ve `AskRequest`'e girdi.
    #   Alan bir demet boyunca yalnız `AskResponse`'ta vardı; istek tarafı yoktu ve
    #   `KURAL_DEVAM` üretimde hiç ateşlenmedi. `kismi_cq` de eklendi — o olmadan
    #   `devam_edilebilir` (hem `sorulan` hem `kismi_cq` ister) yine `None` döner, yani
    #   yankıyı tipli nesneden kuran biri **kapattığını sanır**.
    #   ⚠ Bir tipi bölmek onu küçültmez; iki yönde AYNI şekli garanti eder.
    # ⊙ +4 · `DA-4` — anlatı guard'ının makbuzu (`anlati_dogrulandi` · `anlati_dusen` ·
    #   `guard_muaf`). `narration_guard.Rapor.makbuza()` yazılmıştı ve **hiçbir yerden
    #   çağrılmıyordu**: `G5.4`'ün *"muafiyetler GÖRÜNÜR olur"* kazancı yalnız log'a
    #   gidiyordu ve kullanıcı *"her sayı doğrulanır"* sanmaya devam ediyordu.
    #   ⚠ Yeni panel/alan **açılmadı**: mevcut `hava_boslugu` bloğuna girdi — iddia
    #   kapısının izi neredeyse oraya. *İki kapıyı iki ayrı yere yazmak, onları iki ayrı
    #   şeymiş gibi gösterir.*
    "lib/types.ts": 598,
    "components/ReviewPanel.tsx": 555,
    # ⊙ +9 · 🔴 `G2` DİYALOG DURUMU YANKISI — **taşınamaz, çünkü bir davranış değil bir
    #   TELDİR.** Backend'in bellek zinciri (`AskRequest.diyalog_durumu` → `context.py::
    #   KURAL_DEVAM`) tamamen yazılmış ve testliydi; istemci onu **göndermiyordu**, yani
    #   `KURAL_DEVAM` üretimde **hiç ateşlenmedi**. Üç denetim ajanının ikisi bağımsız
    #   buldu. İnen: 1 durum kancası + 5 yaşam-döngüsü noktası + 3 gönderim.
    #   ⚠ Bir kancaya (`useDialogState`) çıkarmak `contextCq` ile arasındaki **kardeşlik**
    #   ilişkisini gizlerdi — ikisi aynı anda kurulup aynı anda sıfırlanmak ZORUNDA ve o
    #   eşleşme yan yana durduğu için görünür. *Bir tavanın amacı davranış birikimini
    #   durdurmaktır; bir yetimi kapatan teli değil.*
    #   Kapısı: `tests/test_cevap_alani_yetim_degil.py::test_K2c_ISTEK_ALANI_GONDERILIYOR_mu`.
    "app/page.tsx": 543,
    "components/ResultView.tsx": 476,
    # ⊙ +3 · `DA-9` — kıyas chip'i **kipe duyarlı** oldu. Eskiden `=== "yoy"` sabit
    #   kodluydu; `G6`'nın `kiyas_cebiri`'si `mom` de üretiyor. Kusur iki katlıydı:
    #   `mom` aktifken chip **"kapalı"** gösteriyordu ve tıklayınca kullanıcının kıyasını
    #   **sessizce `yoy`'a çeviriyordu** — bir gösterge, kapatmaya çalıştığı şeyi
    #   DEĞİŞTİRİYORDU. **Taşınamaz:** üç satırın ikisi bir `const`, biri bir etiket;
    #   bir bileşene çıkarmak tek bir chip için dosya açmak olurdu.
    #   *Bir anahtarın yalnız bir değeri tanıması, öteki değeri yok saymak değil BOZMAKTIR.*
    "components/InterpretationBar.tsx": 475,
}

#: `(dosya, Δ, gerekçe)` — her satır **bir maddeye** aittir ve nedeni yazılıdır.
MUAFIYET: list[tuple[str, int, str]] = [
    ("app/page.tsx", 1,
     "🔴 `§45` — **ÖNGÖRÜ TIKLAMASI HAZIR SORGUYU KOŞAR** (`onSorguKos`). Tek bir "
     "kod satırı: `cubeMutation.mutate({ cq, label })`. ⊙ Ölçülen kusur: şeritteki "
     "cümlenin `cube_query`'si tıklamada **atılıyor**, metin `/ask`'a gidiyor ve "
     "`route()` onu yarım isabet sayıp **garsona** devrediyordu — yani katalogdan "
     "deterministik ürettiğimiz cevabı **LLM'e yeniden tahmin ettiriyorduk**; plan "
     "`§6 Thread 1` ise *«Enter → `cube_query` koşar · 34 ms · 0 token»* diyor. "
     "⚠ Bileşene çıkarma **denendi ve reddedildi**: koşum yolu `cubeMutation` ve o "
     "sayfanın durumuna bağlı; ikinci bir koşum sahibi `KAT-1`'i bozardı ㊲. "
     "Kazanç bir satırdan büyük: her öngörü tıklaması bir LLM turu tasarruf eder."),
    ("app/page.tsx", 9,
     "🔴🔴 `§RY` — **BELGE BAĞLAMI KIRPILARAK GÖNDERİLİR.** ⊙ Ölçüldü: `previous_rapor` "
     "**tam** gidiyordu (`pages[][].result.rows` dâhil) ve ölçüm aracı `Argüman listesi "
     "çok uzun` ile düştü — kusuru o gösterdi. Sunucu yalnız **kimlikleri** okuyor "
     "(`_belge_bolumleri`); yani sunucunun **az önce ürettiği** satırlar bir sonraki "
     "turda **geri** taşınıyordu. ⚠ Kırpma **istemcide**: veriyi göndermemek, gönderip "
     "sunucuda atmaktan farklıdır — ikincisi bant genişliğini zaten harcamıştır. "
     "🔴 Dokuz satırın **sekizi** bu gerekçenin kendisi; kod bir `map` çağrısı. "
     "*Bir aracın sınırına çarpmak, bazen ölçtüğü şeyin kusurunu gösterir.*"),
    ("app/page.tsx", 8,
     "🔴🔴 `§RD` — **BELGE BAĞLAMI (`contextRapor`), `contextCq`'nun KARDEŞİ.** ⚠ "
     "**TAŞINAMAZ:** bu dosya thread/bağlam yaşam döngüsünün **tek** sahibidir; bağlamı "
     "ikinci bir yere koymak, aynı yaşam döngüsünü iki yerden yönetmek olurdu — ve "
     "`diyalog_durumu` tam olarak bu sebeple burada duruyor (kendi şerhi: *«bir demet "
     "boyunca EKSİKTİ → KURAL_DEVAM üretimde hiç ateşlenmedi»*). 🔴 Sekiz satırın "
     "**beşi** yaşam döngüsü noktası (`setContextRapor`) ve biri istek alanı: alanın "
     "kendisi tek satır, gerisi *«kardeş alan her yerde kardeş kalsın»* disiplini. "
     "⊙ Ve bu alan bir demet boyunca **yetim**di — backend okuyor, istemci "
     "doldurmuyordu; kapı yakaladı (`test_K2c`): *tanım GÖNDERİM DEĞİLDİR.*"),
    # ═══ `§RP` — AGENTIC RAPOR/PANO (2026-08-10) ═══
    ("lib/types.ts", 13,
     "🔴🔴 `§RP` — `AskResponse.rapor` alanı: orkestratörün ürettiği **çok bölümlü "
     "belge** (`Report`). ⚠ **TAŞINAMAZ** ve gerekçesi bu dosyanın kendi muafiyet "
     "geleneğinde yazılı: bu dosya sunucu sözleşmesinin **tek** aynasıdır. 🔴 Onüç "
     "satırın **oniki**si yorum ve hepsi bir ayrımı korumak için: `plan.bolumler` "
     "(ham) ≠ `rapor` (belge) ≠ `viz_paketi` (tek sonucun çok grafiği). Bu üçü "
     "karıştırıldığında üç kavram birden kaybolur — ve bu depoda tam olarak o desen "
     "ölçüldü. *Adı bir şeyi söyleyen bir alana başka bir şey koymak, iki kavramı "
     "birden kaybetmektir.* Alan `null` varsayılan: belge fiili yoksa hiç dolmaz."),
    ("lib/types.ts", 4,
     "🔴 `FAZ 6` — `AskResponse.plan` alanı (çok adımlı cevabın taşıyıcısı). "
     "⚠ **TAŞINAMAZ** ve gerekçesi bu dosyanın kendi muafiyetinde zaten yazılı: bu "
     "dosya sunucu sözleşmesinin **tek** aynasıdır; bir alanı ikinci bir tip dosyasına "
     "koymak sözleşmeyi iki yerden okumak olurdu. 🔴 Dört satır, tek alan ve `null` "
     "varsayılan: tek adımlı cevapta hiç dolmaz, yani bugünkü kart bayt bayt aynı."),
    ("lib/types.ts", 1,
     "🔴 `G6.3` — `temellendirme.kiyas` alanı. ⚠ **TAŞINAMAZ:** bu dosya sunucu "
     "sözleşmesinin **tek** aynasıdır; bir alanı ikinci bir tip dosyasına koymak, "
     "sözleşmeyi iki yerden okumak olurdu. 🔴 Tek satır, tek alan, ve **bayrağa bağlı** "
     "(`referans_dili` kapalıyken sunucu alanı hiç göndermez)."),
    ("components/InterpretationBar.tsx", 2,
     "🔴 `G6.3` — kıyas anahtarına `data-capa=\"kiyas\"` + `tabIndex` çapası. Makbuzun "
     "yeni kıyas rozetinin **iniş noktası**; öteki dört çapanın (`olcu`·`granulerlik`·"
     "`kirilim`·`donem`/`filtre`) birebir aynı deseni. ⚠ **TAŞINAMAZ:** çapa, düzenleyen "
     "öğenin **üstünde** durmak zorundadır — ayrı bir bileşene çıkarmak, rozetin gideceği "
     "yeri düzenleyenden **ayırmak** olurdu ve ikisi zamanla ayrışırdı. "
     "🔴 Yeni davranış YOK: anahtar zaten vardı, yalnız **bulunabilir** oldu."),
    ("lib/api-client.ts", 14,
     "denetim F2 — pano ve widget GERİ ALMA sarmalayıcıları (`restoreDashboard`, "
     "`restoreDashboardWidget`). 🔴 Bu iki fonksiyon TAŞINAMAZ: `dima-frontend/CLAUDE.md` "
     "birebir «Tüm HTTP `src/lib/api-client.ts`'ten geçer — dağınık `fetch` yok» diyor. "
     "İkinci bir HTTP dosyası açmak, bir tavan borcunu bir MİMARİ İHLALİNE çevirirdi. "
     "⚠ Ve kapı bunu ilk gününde yakaladı — yazarını dahil: bir tavan, kendi koyanını "
     "da bağlamıyorsa bir tavan değildir."),
    # ═══ `§63`/`§64` — ÖNİZLEME YÜZÜ (2026-08-13) ═══
    ("lib/types.ts", 2,
     "🔴 `§63` — `AskResponse.adimlar` + `gecerli`: çok adımlı planın **koşmadan** dönen "
     "tel biçimi (`source=onizleme`). ⚠ **TAŞINAMAZ** ve gerekçesi bu dosyanın kendi "
     "muafiyet geleneğinde yazılı: bu dosya sunucu sözleşmesinin **tek** aynasıdır; bir "
     "alanı ikinci bir tip dosyasına koymak sözleşmeyi iki yerden okumak olurdu. "
     "🔴 İki satır, iki alan, ikisi de **düz** — çünkü sunucu onları düz gönderiyor ve "
     "bir ayna güzelleştirmez. Ekranın istediği birleşik nesneyi `lib/onizleme.ts` kurar; "
     "yani bu turda büyüyen tek yer sözleşme, mantık **tavansız bir modüle** çıktı."),
    ("app/page.tsx", 4,
     "🔴 `§63` — önizlemenin **bağlanması**: kanca importu · `useOnizleme()` · "
     "*«önizleme bir cevap değildir»* muhafızı (`yakala` → `return`) · bestecinin "
     "kumandası. ⚠ **TAŞINAMAZ:** bu dosya thread/bağlam yaşam döngüsünün **tek** "
     "sahibidir ve buradaki tek karar odur — *bir cevap geçmişe/tuvale yazılır mı*. "
     "Onaysız bir plan yazılsaydı bir sonraki takip sorusu **hayalî** bir bağlam "
     "üzerinden sorulurdu. 🔴 Durum makinesi (üç hâl: yok · bekliyor · onaylandı) ve "
     "birleştirme burada DEĞİL: kapının kendi öğüdüne uyularak `lib/onizleme.ts`'e "
     "çıkarıldı — dört satırın hiçbiri mantık taşımıyor, hepsi **bağ**."),
]


def _kod_satiri(metin: str) -> int:
    """Yorum ve boş satır **hariç**. ⚠ Bu depoda yorumlar gerekçe taşır; onları saymak
    **belgelemeyi cezalandırırdı** ve kapı, iyi bir alışkanlığı bir borç gibi gösterirdi."""
    return len([s for s in yorumsuz(metin).split("\n") if s.strip()])


@pytest.mark.parametrize("dosya", sorted(TAVANLAR))
def test_TAVAN_ASILMADI(dosya):
    """🔴 **ASIL KAPI.** *Bir tavan, aşıldıktan sonra konursa bir tavan değil bir
    onaydır.*"""
    kaynak = fe_dosyalari().get(dosya)
    assert kaynak is not None, f"⊘ {dosya} yok — tavan bir şey korumuyor"
    n = _kod_satiri(kaynak)
    tavan = TAVANLAR[dosya] + sum(d for f, d, _ in MUAFIYET if f == dosya)
    assert n <= tavan, (
        f"🔴 {dosya}: {n} kod satırı — tavan {tavan}.\n"
        f"YAPILACAK: yeni davranışı bir **bileşene çıkar**, tavanı yükseltme. Bu turda "
        f"`Makbuz` · `SertifikaBandi` · `HataSeridi` · `GeriAlSeridi` tam böyle doğdu.\n"
        f"Gerçekten muaf bir iş ise `MUAFIYET`'e **dosya + Δ + GEREKÇE** ile yazılır; "
        f"gerekçesiz bir muafiyet, muafiyet değil sessiz bir tavan artışıdır.")


def test_KAPI_GERCEKTEN_KIRMIZI_VERIYOR():
    """⚠ *Kırmızı veremeyen bir kapı, olmayan bir kapıdır.* En büyük dosyaya bir **kod**
    satırı enjekte edilince tavan aşılmalı — yani tavanda **boşluk olmamalı**."""
    dosya = "components/ReportCard.tsx"
    kaynak = fe_dosyalari()[dosya]
    n = _kod_satiri(kaynak)
    assert n == TAVANLAR[dosya], (
        f"🔴 {dosya} tavanında {TAVANLAR[dosya] - n} satır BOŞLUK var — kapı büyümeyi "
        f"durdurmuyor. Tavan **ölçülen değere** çekilmeli.")
    assert _kod_satiri(kaynak + "\nconst _MUTASYON = 1;\n") > TAVANLAR[dosya]


def test_YORUM_SATIRI_TAVANI_YEMIYOR():
    """🔴 Birim kararının davranıştaki karşılığı: bir **yorum** eklemek kapıyı kırmazsa,
    *"yorumsuz sayım"* bir niyet beyanı değil bir ölçüdür."""
    kaynak = fe_dosyalari()["components/ReportCard.tsx"]
    assert _kod_satiri(kaynak + "\n// yalnız bir yorum\n") == _kod_satiri(kaynak)


def test_MUAFIYETLER_GEREKCELI():
    """*Gerekçesiz bir muafiyet, muafiyet değil sessiz bir tavan artışıdır.*"""
    for dosya, delta, gerekce in MUAFIYET:
        assert dosya in TAVANLAR and delta > 0 and len(gerekce) > 25, (dosya, delta)


def test_KAPSAM_agirlik_merkeziyle_SINIRLI():
    """⚠ Her dosyaya tavan koymak, kapıyı bir **bürokrasiye** çevirir ve hiçbirine
    bakılmaz hâle getirir. Kapsam: en büyük sekiz dosya."""
    hepsi = fe_dosyalari()
    en_buyuk = sorted(hepsi, key=lambda k: -_kod_satiri(hepsi[k]))[:8]
    eksik = sorted(set(en_buyuk) - set(TAVANLAR))
    assert not eksik, (
        f"🔴 Ağırlık merkezine yeni dosya girmiş ama tavanı yok: {eksik}. "
        f"Bir dosya en büyük sekize giriyorsa, büyümesi de ölçülmeli.")
