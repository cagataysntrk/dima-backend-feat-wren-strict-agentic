"""🔴 **GARSON KAPISI** — bu fazın tek onay kapısı (`G0`).

    python lab/garson.py --live          # GERÇEK sağlayıcı — ASIL ÖLÇÜM
    python lab/garson.py                 # yapısal duman — 🔴 KAPI DEĞİL, `⊘` verir
    python lab/garson.py --live --kaset  # sağlayıcı yanıtlarını KAYDET (§12.2b · K katmanı)

## Neden ayrı bir alet

Korpus ve `eval` **mutfağı** ölçüyor: *"cevaplanan sorunun sayısı doğru mu?"* Garsonun
değeri o soruda **görünmez** — bu operasyonda `--hepsi` sekiz kez koştu ve konuşma
senaryoları sekizinde de `⊘ ÖLÇÜLEMEDİ` verdi. **Garson hakkındaki her karar bugüne
kadar yalnız mutfak metrikleriyle alındı.**

🔴 **Kapı sözleşmesi (yol haritası §2.3):** korpus/`eval` **doğruluk** üzerindeki
vetolarını korur, **kapsam payı** üzerindeki vetolarını kaybeder. Bu alet ise
**garsonun inip inmeyeceğine** karar verir — ve başka hiçbir alet o soruyu sormuyor.

## Kalıp KOPYALANMADI — devralındı

`deneyim.py`'nin yedi sözleşme satırı, tur koşucusu (`kos`), üçüncü durum sabitleri ve
canlı ortam kurulumu **import edilir**. Kendi kopyamızı yazsaydık iki sahip doğardı ve
`--live` bir kez daha sessizce `rule`'a düşerdi (ölçülmüş kusur, MIMARI §6.4).

⚠ **Sözleşme 7 değil ON satır.** Yol haritasının §5'i sekiz *davranış* sayıyor ama
onlar `deneyim.py`'nin yedi *satırıyla* bire bir eşleşmiyor: üçü (**temellendirme ·
onarım · menü**) hiçbir satırda ölçülmüyordu. Bu alet o üçünü ekler.
*(§5/2 «kendi diliyle sipariş alır» bilinçle DIŞARIDA: onu `lab/gercek_dunya.py`
persona×zorluk matrisiyle zaten ölçüyor — ikinci bir sahip yaratmayız.)*

## 🔴 KURAL G-1 — tek koşumla karar YOK

Bu kapı **belirlenimsizdir** (LLM'e bağlı). Ölçüldü: Power BI'da 1000 aynı sorgunun en
sık cevabı yalnız **78 kez** çıkmış; bu deponun kendi tarihinde `prompt_enhancer`
kararı tek koşumla verilip **ikinci sağlayıcıda tersine dönmüştü** (14/15 → 15/15).
→ **En az iki koşum.** İkisi ayrışırsa karar **verilmez**: `⊘` yazılır, borç kaydına girer.
`--muhur` ile koşum damgası verilir; `_tabani_dondur` iki damgayı karşılaştırır.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# ⚠ SIRA ÖNEMLİ — `deneyim` üzerinden `konusma_senaryolari`'nın gerçek-ortam yakalaması
# devralınır. Doğrudan `konusma_senaryolari`'dan almak da çalışırdı; `deneyim`'den almak
# **sözleşme satırlarını da** aynı yerden getirir ve tek sahip kalır.
from lab.deneyim import (  # noqa: E402
    KAPSAM_DISI,
    KOPMA_IZI,
    LIVE_BEKLE,
    ON_KOSUL_YOK,
    S1_CAPA,
    S2_ANLAT,
    S3_SUREKLILIK,
    S4_SOSYAL,
    S5_BELIRSIZLIK,
    S6_MAKBUZ,
    S7_GERI_DONUS,
    _canli_ortami_geri_yukle,
    _isaret,
    _makbuzlu,
    _olc,
    kos,
)

RAPOR_DIZINI = Path(__file__).resolve().parent / "reports" / "garson"
TABAN_DOSYASI = Path(__file__).resolve().parent / "garson_baseline.json"
KASET_DIZINI = Path(__file__).resolve().parent / "kasetler"

# --- ÜÇ YENİ SÖZLEŞME SATIRI --------------------------------------------------------
#
# Yedi satır `deneyim.py`'den gelir; bu üçü garsonun **konuşma** yarısını ölçer ve
# bugüne kadar hiçbir alet tarafından ölçülmüyordu.

S8_TEMELLENDIRME = "8·temellendirme: ne anladığını SÖYLER"
S9_ONARIM = "9·onarım: tek slot düzelir, baştan başlamaz"
S10_MENU = "10·menü: yapamadığında NE YAPABİLDİĞİNİ söyler"

TUM_SATIRLAR = (S1_CAPA, S2_ANLAT, S3_SUREKLILIK, S4_SOSYAL, S5_BELIRSIZLIK,
                S6_MAKBUZ, S7_GERI_DONUS, S8_TEMELLENDIRME, S9_ONARIM, S10_MENU)


# --- YENİ SENARYO SINIFLARI ---------------------------------------------------------
#
# `deneyim.py`'nin senaryoları KORUNUR ve bunlar onların ÜSTÜNE eklenir (`--hepsi` ile).
# Buradakiler yalnız üç yeni satırı ölçer; eskileri tekrar ölçmek payda şişirirdi.

SENARYOLAR: tuple[dict, ...] = (
    {
        "ad": "temellendirme",
        "aciklama": "Başarılı bir cevapta sistem NE ANLADIĞINI söylüyor mu? "
                    "(`G1` inmeden bu senaryo KIRMIZI olmalı — alet çalışıyor demektir.)",
        "turlar": ["bu yıl makine bazında oee",
                   "mart ayında toplam fire kg"],
        "olculen": (S8_TEMELLENDIRME, S6_MAKBUZ),
    },
    {
        "ad": "sureklilik_slot",
        "aciklama": "Netleştirmeye cevap verilince tur BAŞTAN BAŞLAMAMALI: "
                    "özgün niyet korunur, yalnız eksik slot dolar.",
        "turlar": ["fire kg",              # dönem eksik → netleştirme beklenir
                   "__CHIP__",             # chip'e tıkla → slot dolmalı
                   "peki mart?"],          # devam: niyet korunuyor mu
        "olculen": (S3_SUREKLILIK, S5_BELIRSIZLIK, S8_TEMELLENDIRME),
    },
    {
        "ad": "onarim",
        "aciklama": "Kullanıcı TEK bir slotu düzeltiyor; ölçü ve kırılım korunmalı. "
                    "(`G2` inmeden KIRMIZI olmalı.)",
        "turlar": ["şubat ayında makine bazında fire kg",
                   "yok ya mart demiştim",     # yalnız DÖNEM değişmeli
                   "peki en yükseği hangisi?"],
        "olculen": (S9_ONARIM, S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        # 🔴 `DA-2` — **ANLATICININ KENDİ SATIRI ÖLÇÜLMÜYORDU.**
        #
        # `TUM_SATIRLAR` on satır ilan ediyor ve rapor onları basıyor; ama `1·çapa`,
        # `2·anlat`, `4·sosyal`, `7·geri dönüş` **hiçbir senaryonun** `olculen`'inde
        # yoktu → sekiz raporun sekizinde de `0|0|0`. Yani **ölçülmemiş** ile
        # **başarısız** aynı görünüyordu.
        #
        # En ağırı `2·anlat`: `G5` `t2_anlatici`'yi açtı ve o satır **yine 0 kaldı** —
        # fazın amiral yeteneği, kendi kapısında görünmezdi. `G0.12`'nin *"alet körse G1
        # başlamaz"* kırmızı çizgisi bu yüzden fiilen sınanamadı.
        #
        # ⚠ Tur sayısı **bilerek üç**: canlı kapı gerçek sağlayıcı çağırıyor ve bu bir
        # yük testi değil. *Bir kapıyı pahalılaştırmak, onu atlanan bir kapıya çevirir.*
        "ad": "anlati",
        "aciklama": "Konuşma turu: cevabın ÜSTÜNDE konuşulur — yeni SQL yazılmaz, "
                    "anlatı + olgular + devam chip'leri gelir. (`G5` inmeden KIRMIZI.)",
        "turlar": ["bu yıl makine bazında oee",
                   "bunu analiz et",
                   "bu neden böyle?"],
        "olculen": (S1_CAPA, S2_ANLAT, S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        # 🔴 `DA-2`'nin kalan iki satırı. Kapı (`test_HER_SATIR_EN_AZ_BIR_SENARYODA…`)
        # bunları da yakaladı — *bir kapıyı kurmanın ilk faydası, kendi eksiğini
        # göstermesidir.*
        #
        # İkisi tek senaryoda toplandı çünkü ikisi de **tek turluk** ölçüm:
        # · `4·sosyal` → *"teşekkürler"* bir veri sorusu DEĞİL: 0 LLM · 0 SQL beklenir.
        # · `7·geri dönüş` → `("...", 0)` tuple'ı koşucuya *"0. kartın `cube_query`'sini
        #   `/cube` ile yeniden koştur"* der; 0 LLM ile aynı rapora dönülmeli.
        #
        # ⚠ Toplam üç tur — canlı bütçe korunur.
        "ad": "sosyal_ve_donus",
        "aciklama": "Sosyal ifade motora hiç gitmez; her karta 0 LLM ile geri dönülebilir.",
        "turlar": ["mart ayında toplam fire kg",
                   "teşekkürler",              # sosyal → 0 LLM · 0 SQL
                   ("__CUBE__", 0)],           # 0. karta geri dön → 0 LLM replay
        "olculen": (S4_SOSYAL, S7_GERI_DONUS, S6_MAKBUZ),
    },
    {
        "ad": "kapasite",
        "aciklama": "Kapsam dışı bir soruda sistem yalnız «yapamam» mı diyor, "
                    "yoksa NE YAPABİLDİĞİNİ de söylüyor mu? (`G8` inmeden KIRMIZI.)",
        "turlar": ["bu gidişle yılı nerede kapatırız",   # forecast — v1'de YOK
                   "firesiz partiler kaç tane"],          # olumsuzluk — desteklenmiyor
        "olculen": (S10_MENU, S6_MAKBUZ),
    },

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🔴 GENİŞLETME 6 → 25 SENARYO (2026-08-07)
    #
    # ## Neden
    #
    # Ölçüldü ve fark üç mertebe: bu turda **6 senaryo / 16 tur** üç gerçek kusur buldu
    # (`NameError` → iddia kapısı bir demettir şemasız koşuyordu · netleştirme turu ne
    # anladığını söylemiyordu · canlıda yer tutucu düşmesi). Aynı anda **4 045 test +
    # ~14 700 korpus turu** bunların **hiçbirini** görmedi.
    #
    # Sebep yapısal: korpus ve süit **mutfağı** ölçer (`route()` doğruluğu, yapısal
    # kapılar); garsonun değeri **konuşmanın kendisindedir** ve orayı yalnız senaryolar
    # görür. *Bir katmanı, onu görmeyen bir aletle savunmak, savunmamaktır.*
    #
    # ## ⚠ Ama senaryolar ötekilerin YERİNE GEÇMEZ — ölçüldü
    #
    # Bu turda `--hepsi`'nin bulduğu **9 kırmızının hiçbiri** bir senaryoyla
    # yakalanamazdı: YAML boolean tuzağı · `FLAG_REGISTRY` eksiği · `⟳` satır biçimi ·
    # `ask()` tavanı. Bunlar **meta-kapılar**. Ve korpusun tek gerçek yakalaması
    # (`gitas` düştü, payda 445→342, doğruluk **yükseldi**) **payda sabitliğine** dayanır;
    # senaryo kümesi o sinyali yapısal olarak veremez.
    #
    # 🔴 **Dolayısıyla bu genişletme bir İKAME değil bir DENGELEMEDİR:** senaryo sayısı
    # artar, kapı koşum SIKLIĞI düşer.
    #
    # ## Maliyet — dürüstçe yazılı
    #
    # 25 senaryo · **~55 tur**. Canlı modda tur arası `LIVE_BEKLE` (5 sn) + sağlayıcı
    # gecikmesi → kabaca **12-18 dk**. Bu yüzden `--live` bir **faz sonu** kapısıdır
    # (politika zaten böyleydi); yapısal duman modu saniyeler sürer.
    # *Bir kapıyı pahalılaştırmak, onu atlanan bir kapıya çevirir* — bu yüzden sıklık
    # artmaz, kapsam artar.
    #
    # ## Terimler UYDURULMADI
    #
    # Her ölçü/boyut adı `demo/packs/sektor/boyahane` ve `modul/oee` kataloğundan
    # **okundu** (`toplam_fire_kg` · `fire_orani_yuzde` · `toplam_rework_kg` ·
    # `rework_sayisi` · `sikayet_adedi` · `ort_oee` · `makine` · `sebep` · `konu` ·
    # `musteri` · `renk`). Uydurulmuş bir terim, senaryoyu **sessizce** ölçümsüz bırakır.
    # ═══════════════════════════════════════════════════════════════════════════════

    # --- ÇAPA (S1) — konuşma turu YENİ SQL YAZMAZ -----------------------------------
    {
        "ad": "capa_neden",
        "aciklama": "«Bu neden böyle?» bir KONUŞMA turudur: mevcut rapor üstünde konuşur, "
                    "yeni sorgu yazmaz.",
        "turlar": ["bu yıl makine bazında ort_oee", "bu neden böyle?"],
        "olculen": (S1_CAPA, S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "capa_normal_mi",
        "aciklama": "«Normal mi?» bir yargı sorusudur — sorguyu değiştirmemeli.",
        "turlar": ["mart ayında fire oranı", "normal mi?"],
        "olculen": (S1_CAPA, S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "capa_ne_yapmali",
        "aciklama": "«Ne yapmalıyız?» reçete ister; yeni bir SQL değil.",
        "turlar": ["bu yıl toplam rework kg", "ne yapmalıyız?"],
        "olculen": (S1_CAPA, S3_SUREKLILIK, S6_MAKBUZ),
    },

    # --- ANLATI (S2) — ≥3 olgu + anlatı + ≥2 chip ------------------------------------
    {
        "ad": "anlat_grafik_ustunde",
        "aciklama": "Kullanıcı zaman serisine bakıp ONUN ÜSTÜNDE konuşuyor.",
        "turlar": ["son 6 ayda aylık toplam fire kg", "bunu yorumla",
                   "en kötü ay hangisi?"],
        "olculen": (S2_ANLAT, S1_CAPA, S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "anlat_ozetle",
        "aciklama": "«Özetle» — kırılımlı bir tabloyu anlatıya çevirebiliyor mu?",
        "turlar": ["bu yıl konu bazında şikayet adedi", "özetle"],
        "olculen": (S2_ANLAT, S3_SUREKLILIK, S6_MAKBUZ),
    },

    # --- SOSYAL (S4) — 0 LLM · 0 SQL ------------------------------------------------
    {
        "ad": "sosyal_acilis",
        "aciklama": "Selamlama motora HİÇ gitmez; ardından iş sorusu normal akar.",
        "turlar": ["merhaba", "bu yıl toplam ciro"],
        "olculen": (S4_SOSYAL, S6_MAKBUZ),
    },
    {
        "ad": "sosyal_kapanis",
        "aciklama": "Teşekkür + kapanış: veri sinyali YOK, sorgu üretilmemeli.",
        "turlar": ["mart ayında rework sayısı", "teşekkürler, iyi çalışmalar"],
        "olculen": (S4_SOSYAL, S3_SUREKLILIK, S6_MAKBUZ),
    },

    # --- BELİRSİZLİK (S5) — tahmin yok, SORU var ------------------------------------
    {
        "ad": "belirsizlik_donem",
        "aciklama": "Dönemsiz ölçü → tahmin edilmemeli, SORULMALI.",
        "turlar": ["toplam rework kg", "__CHIP__"],
        "olculen": (S5_BELIRSIZLIK, S3_SUREKLILIK, S8_TEMELLENDIRME),
    },
    {
        "ad": "belirsizlik_sonra_devam",
        "aciklama": "Netleştirmeden sonra kullanıcı KENDİ cümlesiyle devam ediyor.",
        "turlar": ["şikayet adedi", "geçen yıl", "peki konu bazında?"],
        "olculen": (S5_BELIRSIZLIK, S3_SUREKLILIK, S8_TEMELLENDIRME),
    },

    # --- GERİ DÖNÜŞ (S7) — 0 LLM ile replay ------------------------------------------
    {
        "ad": "geri_donus_ikinci_kart",
        "aciklama": "Üç turluk bir sohbetten SONRA ikinci karta dönülüyor — bağlam "
                    "kaybolmadan.",
        "turlar": ["bu yıl toplam fire kg",
                   "mart ayında toplam rework kg",
                   ("__CUBE__", 0)],
        "olculen": (S7_GERI_DONUS, S3_SUREKLILIK, S6_MAKBUZ),
    },

    # --- TEMELLENDİRME (S8) — ne anladığını SÖYLER ----------------------------------
    {
        "ad": "temellendirme_kirilimli",
        "aciklama": "Kırılım ve dönem birlikte: beyan ikisini de içeriyor mu?",
        "turlar": ["geçen yıl müşteri bazında toplam ciro"],
        "olculen": (S8_TEMELLENDIRME, S6_MAKBUZ),
    },
    {
        "ad": "temellendirme_filtreli",
        "aciklama": "Dışlama filtresi de anlaşılan şeyin parçasıdır.",
        "turlar": ["beyaz hariç bu yıl toplam fire kg"],
        "olculen": (S8_TEMELLENDIRME, S6_MAKBUZ),
    },

    # --- ONARIM (S9) — TEK slot düzelir --------------------------------------------
    {
        "ad": "onarim_olcu",
        "aciklama": "Kullanıcı ÖLÇÜYÜ düzeltiyor; dönem ve kırılım korunmalı.",
        "turlar": ["mart ayında makine bazında toplam fire kg",
                   "yok ya fire oranı demek istedim"],
        "olculen": (S9_ONARIM, S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "onarim_kirilim",
        "aciklama": "Kullanıcı KIRILIMI düzeltiyor; ölçü ve dönem korunmalı.",
        "turlar": ["bu yıl makine bazında toplam rework kg",
                   "makine değil sebep bazında olsun"],
        "olculen": (S9_ONARIM, S3_SUREKLILIK, S6_MAKBUZ),
    },

    # --- MENÜ (S10) — «yapamam»ın yanına «ama şunu yapabilirim» ---------------------
    {
        "ad": "menu_tahmin",
        "aciklama": "Geleceğe dönük tahmin v1'de YOK — ama ne yapılabildiği söylenmeli.",
        "turlar": ["önümüzdeki ay ne kadar fire olur"],
        "olculen": (S10_MENU, S6_MAKBUZ),
    },
    {
        "ad": "menu_sonra_toparlanma",
        "aciklama": "🔴 Reddin ARDINDAN sohbet ölmemeli: kullanıcı yeni bir soru sorunca "
                    "sistem normal akışa dönebilmeli.",
        "turlar": ["gelecek çeyrek cirosunu tahmin et",
                   "peki bu yıl toplam ciro ne kadar"],
        "olculen": (S10_MENU, S3_SUREKLILIK, S6_MAKBUZ),
    },

    # --- SÜREKLİLİK (S3) — çok turlu derinleşme -------------------------------------
    {
        "ad": "derinlesme_dort_tur",
        "aciklama": "🔴 B2B'nin gerçek deseni: dört turluk daralma. `lab/sharding.py` bu "
                    "eksende **tur 1 %63,6 → tur 5 %45,5** ölçtü — senaryo o kaybı "
                    "konuşma katmanında görünür kılar.",
        "turlar": ["bu yıl toplam fire kg",
                   "sadece mart",
                   "makine bazında kır",
                   "en yükseği hangisi?"],
        "olculen": (S3_SUREKLILIK, S8_TEMELLENDIRME, S6_MAKBUZ),
    },
    {
        "ad": "dagitik_ifade",
        "aciklama": "Kullanıcı KENDİ diliyle konuşuyor — devrik, dolgu kelimeli.",
        "turlar": ["şu mart ayı fire kg neydi ya",
                   "bi de makine bazında göster"],
        "olculen": (S3_SUREKLILIK, S8_TEMELLENDIRME, S6_MAKBUZ),
    },
    {
        "ad": "konu_degisimi",
        "aciklama": "Kullanıcı konuyu DEĞİŞTİRİYOR — eski bağlam yeni soruyu kirletmemeli.",
        "turlar": ["bu yıl makine bazında toplam fire kg",
                   "geçen yıl konu bazında şikayet adedi"],
        "olculen": (S3_SUREKLILIK, S8_TEMELLENDIRME, S6_MAKBUZ),
    },
)


# --- ÖLÇÜM ------------------------------------------------------------------------


def _temellendirme_var(d: dict) -> bool:
    """Cevap **ne anladığını** söylüyor mu?

    🔴 Alan `G1`'de doğacak (`AskResponse.temellendirme`). Bugün **yok** — ve bu
    senaryonun bugün KIRMIZI vermesi aletin **çalıştığının kanıtıdır** (`G0.12`).
    """
    t = d.get("temellendirme")
    if not isinstance(t, dict):
        return False
    # Boş bir sözlük "söyledim" sayılmaz: en az ölçü ya da dönem adlandırılmış olmalı.
    return bool(t.get("olcu") or t.get("donem"))


def _menu_var(d: dict) -> bool:
    """Ret cevabı **ne yapılabileceğini** de söylüyor mu?

    ## 🔴 ÖLÜ DAL KALDIRILDI — ve planın kendi çelişkisi burada çözüldü

    Bu fonksiyon `d.get("kapasite")` okuyordu: `G8` yazılmadan önce planın `§13.5b`'si
    *"üç yeni alan kapıya bağlanır: `temellendirme` · `diyalog_durumu` · **`kapasite`**"*
    diyordu. Ama planın `§13.5c/G8.2`'si **tam tersini** söylüyor: *"üçüncü kanal
    açma."* Kod ikinciyi seçti, öneriler mevcut `suggestions` kanalına bağlandı ve karar
    **testle kilitlendi** (`test_kapasite_beyani.py`: `assert "kapasite" not in alanlar`).

    Yani `AskResponse.kapasite` diye bir alan **yok ve olmayacak** — o dal hiçbir zaman
    doğru dönemezdi. Bir denetim ajanı yakaladı.

    *Bir ölçüm aracında ölü bir dal, yalnız gereksiz değil YANILTICIDIR: okuyan onu bir
    yetenek sanır ve o yeteneğin ölçüldüğünü düşünür.*

    Kalan tek ölçüt doğru olanıdır: **ret cevabında** (`source is None`) bir chip/öneri
    varsa menü basılmıştır.
    """
    # ⚠ `source is None` şartı bilinçli: başarılı bir cevabın yanındaki chip'ler *"sonraki
    # adım"*tır, *"ama şunu yapabilirim"* değil. İkisini aynı saymak, menüyü hiç
    # basmayan bir sistemi de yeşil gösterirdi.
    return bool(d.get("source") is None
                and (d.get("next_steps") or d.get("suggestions")))


def _onarim_dogru(turlar: list[dict]) -> bool | str:
    """*"Yok ya mart demiştim"* → **yalnız dönem** değişmeli.

    Ölçüm: onarım turundan önceki ve sonraki `cube_query`'de **ölçü ve boyut aynı**
    kalmalı. Aynı kalmıyorsa tur baştan başlamış demektir — `KURAL_TAZE` ateşlenmiştir.
    """
    veri = [t for t in turlar if t.get("cevap", {}).get("cube_query")]
    if len(veri) < 2:
        return ON_KOSUL_YOK
    once = veri[0]["cevap"]["cube_query"]
    sonra = veri[1]["cevap"]["cube_query"]
    return (once.get("measures") == sonra.get("measures")
            and once.get("dimensions") == sonra.get("dimensions"))


def _olc_garson(senaryo: dict, turlar: list[dict]) -> dict:
    """Yedi satırı `deneyim._olc`'ye devret, üç yenisini burada ölç."""
    olcum = dict(_olc(senaryo, turlar))
    ilgili = set(senaryo["olculen"])

    for satir in (S8_TEMELLENDIRME, S9_ONARIM, S10_MENU):
        if satir not in ilgili:
            olcum[satir] = KAPSAM_DISI

    cevaplar = [t["cevap"] for t in turlar if t.get("tur_tipi") != "olcum_disi"]
    veri_cevaplari = [d for d in cevaplar if d.get("cube_query")]

    if S8_TEMELLENDIRME in ilgili:
        olcum[S8_TEMELLENDIRME] = (all(_temellendirme_var(d) for d in veri_cevaplari)
                                   if veri_cevaplari else ON_KOSUL_YOK)
    if S9_ONARIM in ilgili:
        olcum[S9_ONARIM] = _onarim_dogru(turlar)
    if S10_MENU in ilgili:
        retler = [d for d in cevaplar if d and d.get("source") is None]
        olcum[S10_MENU] = (all(_menu_var(d) for d in retler) if retler else ON_KOSUL_YOK)
    return olcum


# --- G0.7 · ŞEMA-DIŞI ÇIKTI ORANI ---------------------------------------------------


def _sema_disi_orani(sonuclar: list[dict]) -> dict:
    """🔴 §7.4'ün ölçüm borcu — **OpenRouter kararının fiyat kalemi**.

    `llm_sema_kisitli` seçilen sağlayıcıda **NO-OP** (`oneOf` desteklenmiyor). Yani
    Intent-JSON serbest-JSON olarak dönüyor ve `parse_cube_query` onu reddedebiliyor.
    Bu oran bilinmeden (c) seçeneğinin tekrar-denemesi **yazılmaz**: *ölçülmemiş bir
    kusura çözüm yazmak bu deponun yasak listesinde.*

    Ölçüm dolaylıdır (dışarıdan gözlem): LLM yoluna girip **cevap üretemeyen** turlar.
    Kesin sayı için sunucu tarafı sayaç gerekir — o `G0b`'nin çıkış kütüğüyle gelir.
    """
    llm_turu = sema_disi = 0
    for s in sonuclar:
        for t in s["turlar"]:
            d = t.get("cevap") or {}
            kaynak = str(d.get("source") or "")
            if not kaynak.startswith(("llm", "cube+llm")):
                continue
            llm_turu += 1
            if not d.get("cube_query") and not d.get("rows"):
                sema_disi += 1
    return {"llm_turu": llm_turu, "sema_disi": sema_disi,
            "oran": round(sema_disi / llm_turu, 3) if llm_turu else None}


# --- G0.15 · KASET (§12.2b · K katmanı) ---------------------------------------------


def _kaset_yaz(sonuclar: list[dict], muhur: str) -> Path:
    """Sağlayıcı yanıtlarını kaydet — `K` katmanının hammaddesi.

    ⚠ **Kasetin sınırı yazılı olsun:** kaset **kaliteyi ölçmez**, yalnız **tesisatı**
    ölçer. Bir kaset yeşilken ürün kötü olabilir; bu yüzden `C` katmanı (`--live`)
    kaldırılmaz, **seyrekleştirilir**.
    """
    KASET_DIZINI.mkdir(parents=True, exist_ok=True)
    yol = KASET_DIZINI / f"garson-{muhur}.json"
    kayit = [{"senaryo": s["ad"],
              "turlar": [{"soru": t["soru"], "cevap": t.get("cevap")} for t in s["turlar"]]}
             for s in sonuclar]
    yol.write_text(json.dumps(kayit, ensure_ascii=False, indent=1), encoding="utf-8")
    return yol


# --- TABAN ve KAPI ------------------------------------------------------------------


def _ozet(sonuclar: list[dict]) -> dict:
    """Satır başına {gecti, kaldi, olculemedi} — payda **sabit** kalır (KURAL A)."""
    ozet: dict[str, dict[str, int]] = {
        s: {"gecti": 0, "kaldi": 0, "olculemedi": 0} for s in TUM_SATIRLAR}
    for s in sonuclar:
        for satir, v in s["olcum"].items():
            if v == KAPSAM_DISI:
                continue
            k = "gecti" if v is True else "kaldi" if v is False else "olculemedi"
            ozet[satir][k] += 1
    return ozet


def kapi_degerlendir(ozet: dict, taban: dict | None) -> tuple[bool, list[str]]:
    """Taban altına düşen satır **kırmızıdır**. `⊘` gerileme SAYILMAZ — borçtur.

    🔴 Taban yoksa kapı **geçmez, DONDURUR**: ilk koşum bir ölçüdür, bir onay değil.
    """
    if taban is None:
        return False, ["taban YOK — ilk koşum: `--taban-dondur` ile damgalanmalı"]
    sorunlar = []
    for satir, v in ozet.items():
        t = taban.get(satir, {}).get("gecti", 0)
        if v["gecti"] < t:
            sorunlar.append(f"{satir}: {v['gecti']} < taban {t}")
    return (not sorunlar), sorunlar


def _rapor_yaz(sonuclar: list[dict], ozet: dict, sema: dict,
               live: bool, muhur: str) -> Path:
    RAPOR_DIZINI.mkdir(parents=True, exist_ok=True)
    yol = RAPOR_DIZINI / f"garson-{muhur}.md"
    s = [f"# GARSON KAPISI — {muhur}", "",
         f"**Mod:** {'CANLI (gerçek sağlayıcı)' if live else '🔴 yapısal duman — KAPI DEĞİL'}",
         "", "## Sözleşme — on satır", "",
         "| satır | ✅ | ❌ | ⊘ |", "|---|---|---|---|"]
    for satir in TUM_SATIRLAR:
        v = ozet[satir]
        s.append(f"| {satir} | {v['gecti']} | {v['kaldi']} | {v['olculemedi']} |")
    s += ["", "## Şema-dışı çıktı oranı (§7.4 borcu)", "",
          f"- LLM turu: **{sema['llm_turu']}** · şema-dışı: **{sema['sema_disi']}** "
          f"· oran: **{sema['oran']}**", ""]
    for r in sonuclar:
        s += [f"### {r['ad']}", "", f"*{r['aciklama']}*", ""]
        for satir in TUM_SATIRLAR:
            if r["olcum"].get(satir) != KAPSAM_DISI:
                s.append(f"- {_isaret(r['olcum'][satir])} {satir}")
        s.append("")
        for t in r["turlar"]:
            d = t.get("cevap") or {}
            s.append(f"- `{t['soru']}` → source=`{d.get('source')}` "
                     f"satır={len(d.get('rows') or [])}")
        s.append("")
    yol.write_text("\n".join(s), encoding="utf-8")
    return yol


def main() -> int:
    ap = argparse.ArgumentParser(description="Garson kapısı — konuşma katmanı ölçümü")
    ap.add_argument("--live", action="store_true",
                    help="GERÇEK sağlayıcı. 🔴 Olmadan KAPI DEĞİLDİR.")
    ap.add_argument("--senaryo", help="yalnız bu senaryo")
    ap.add_argument("--kaset", action="store_true", help="sağlayıcı yanıtlarını kaydet")
    ap.add_argument("--muhur", default="", help="koşum damgası (KURAL G-1)")
    ap.add_argument("--taban-dondur", action="store_true",
                    help="bu koşumu taban olarak yaz")
    args = ap.parse_args()

    muhur = args.muhur or ("canli" if args.live else "duman")

    if args.live:
        sag = _canli_ortami_geri_yukle()
        print(f"CANLI MOD — sağlayıcı: {sag} · tur arası {LIVE_BEKLE}s", flush=True)
        # ⚠ Üretici BURADA kurulur, `app.state`'ten OKUNMAZ: `app.state.llm` ancak
        # `TestClient` bağlamı (lifespan) açılınca dolar. İlk sürüm onu okuyordu ve
        # ön uçuş `AttributeError: 'NoneType'` ile düşüyordu — yani *"kota tükendi"*
        # diye raporlanan şey aslında **bizim kurulum sıramızdı**. Ön uçuşun teşhisi
        # yanlışsa, ön uçuş yoktur.
        from lab.konusma_senaryolari import _kota_on_ucusu
        from app.config import get_settings
        from app.llm import build_generator

        get_settings.cache_clear()
        _kota_on_ucusu(build_generator(get_settings()))
    else:
        print("🔴 YAPISAL DUMAN — bu bir KAPI DEĞİLDİR. Tüm satırlar `⊘` sayılır. "
              "Asıl ölçüm: --live", flush=True)

    # 🔴 İSTEMCİ KURULUMU `deneyim.py` İLE BİREBİR — ve bu bir üslup tercihi değil,
    # ölçülmüş bir kusurun kapısı. İlk sürüm çıplak `TestClient(app)` kullandı; `/ask`
    # **auth zorunlu** olduğu için her tur **401** döndü ve `source=None` olarak
    # raporlandı. Yani alet *"ürün cevap vermiyor"* diye ölçtü — oysa **kapıya hiç
    # girmemişti**. `create_app()` + `make_tenant_user` + login: üçü birden gerekli.
    from fastapi.testclient import TestClient

    from app.main import create_app
    from tests.conftest import make_tenant_user

    make_tenant_user("owner@dima.local", "owner-parola-123", tenant_slug=None)
    c = TestClient(create_app())
    c.__enter__()
    _r = c.post("/auth/login", json={"email": "owner@dima.local",
                                     "password": "owner-parola-123"})
    if _r.status_code != 200:
        print(f"🔴 LOGIN BAŞARISIZ ({_r.status_code}) — ölçüm YAPILMADI.")
        return 1
    c.headers["Authorization"] = f"Bearer {_r.json()['access_token']}"

    secili = [s for s in SENARYOLAR if not args.senaryo or s["ad"] == args.senaryo]
    sonuclar = []
    for senaryo in secili:
        print(f"▸ {senaryo['ad']}", flush=True)
        r = kos(c, senaryo, live=args.live)
        r["olcum"] = _olc_garson(senaryo, r["turlar"])
        sonuclar.append(r)
        if args.live:
            time.sleep(LIVE_BEKLE)

    # 🔴 SIFIR-CEVAP KAPISI — ölçülmüş kusurun yapısal karşılığı.
    #
    # İlk koşumda **on turun onu da** `source=None` döndü (auth eksikti) ve alet yine de
    # bir tablo bastı: `3·süreklilik ✅2` — çünkü cevap yokken *"ilişkilendiremedim"* de
    # yoktu. **Sistem hiç çalışmazken bir satır YEŞİL verdi.** Bu deponun defalarca
    # ısırıldığı desen (`gitas` düştü → doğruluk yükseldi; `--user` unutuldu → toplam
    # yeşil kaldı).
    #
    # Kural: **hiçbir tur cevap üretmediyse ölçüm yoktur.** Rapor basılmaz, taban
    # dondurulmaz, kapı geçmez. *Ölçmediğini ölçmüş gibi göstermek, hiç ölçmemekten
    # kötüdür.*
    _cevaplilar = [t for s in sonuclar for t in s["turlar"]
                   if (t.get("cevap") or {}).get("source")]
    if not _cevaplilar:
        print("\n🔴 SIFIR CEVAP — hiçbir tur `source` üretmedi. ÖLÇÜM YAPILMADI.\n"
              "   Olası sebep: auth · tenant · katalog · sağlayıcı. Rapor BASILMADI;\n"
              "   yeşil/kırmızı sayıları bu koşumdan OKUNAMAZ.", flush=True)
        return 1

    ozet = _ozet(sonuclar)
    sema = _sema_disi_orani(sonuclar)

    # 🔴 `--live` DEĞİLSE hiçbir satır yeşil sayılmaz: ölçülemeyen bir şey geçmiş
    # sayılmaz (§2.5). Yapısal duman yalnız *"kod çöküyor mu"* sorusunu yanıtlar.
    if not args.live:
        for v in ozet.values():
            v["olculemedi"] += v["gecti"] + v["kaldi"]
            v["gecti"] = v["kaldi"] = 0

    rapor = _rapor_yaz(sonuclar, ozet, sema, args.live, muhur)
    print(f"\nrapor: {rapor}")
    print(f"şema-dışı oran: {sema['oran']} ({sema['sema_disi']}/{sema['llm_turu']})")
    # 🔴 `G0.12` — **ANLATININ KAYNAĞI AYIRT EDİLİR.** Sözleşme satırı `2·anlat` bilinçli
    # olarak `narration or summary` okur (`deneyim.py:307`): ikisi de sözleşmeyi karşılar
    # ve bu **kusur değil, beyan edilmiş bir yoldur**. Ama tam o yüzden satır
    # `t2_anlatici` açık/kapalı **AYNI** çıkıyordu — ve `G0.12`'nin kırmızı çizgisi bunu
    # yasaklıyor: *"açık/kapalı FARKLI çıkmalı; çıkmıyorsa alet KÖR, `G1` başlamaz."*
    # Bir denetim ajanı yakaladı: `DA-2` satırı **ölçülür** yaptı ama **ayırt edici**
    # yapmadı.
    #
    # ⚠ Çözüm sözleşme satırını bozmak DEĞİL — o doğru şeyi ölçüyor. Çözüm **ayrı bir
    # ayırt edici** basmak. `t2_anlatici` kapalıyken `narration` **0** olmalıdır; bu iki
    # sayı yan yana durduğu sürece aletin körlüğü **görülebilir**.
    # *Bir satırı ayırt edici yapmak için onu bozmak gerekmiyorsa, bozma.*
    _narr = sum(1 for s in sonuclar for _t in s["turlar"]
                if (((_t.get("cevap") or {}).get("interpretation") or {}) or {}).get("narration"))
    _summ = sum(1 for s in sonuclar for _t in s["turlar"]
                if (((_t.get("cevap") or {}).get("interpretation") or {}) or {}).get("summary"))
    print(f"anlatı kaynağı: narration={_narr} · summary={_summ}"
          + ("   ⚠ narration=0 → `t2_anlatici` KAPALI görünüyor" if not _narr else ""))
    for satir in TUM_SATIRLAR:
        v = ozet[satir]
        print(f"  {satir:<52} ✅{v['gecti']}  ❌{v['kaldi']}  ⊘{v['olculemedi']}")

    # ⚠ KASET ÖNCE — ölçülen kusur (`G0`, 2026-08-07): ilk sürümde `--taban-dondur`
    # erken `return` ediyordu ve `--kaset --taban-dondur` birlikte verilince kaset
    # **sessizce yazılmıyordu**. Bir bayrağın başka bir bayrağı sessizce iptal etmesi,
    # bu deponun avladığı *"beyan var, karşılığı yok"* sınıfıdır.
    if args.kaset and args.live:
        print(f"kaset: {_kaset_yaz(sonuclar, muhur)}")

    taban = json.loads(TABAN_DOSYASI.read_text()) if TABAN_DOSYASI.exists() else None
    if args.taban_dondur:
        if not args.live:
            print("🔴 yapısal dumandan TABAN DONDURULAMAZ.")
            return 1
        TABAN_DOSYASI.write_text(json.dumps(ozet, ensure_ascii=False, indent=1),
                                 encoding="utf-8")
        print(f"taban donduruldu → {TABAN_DOSYASI}")
        return 0

    gecti, sorunlar = kapi_degerlendir(ozet, taban)
    for s in sorunlar:
        print(f"  🔴 {s}")
    return 0 if gecti or not args.live else 1


if __name__ == "__main__":
    raise SystemExit(main())
