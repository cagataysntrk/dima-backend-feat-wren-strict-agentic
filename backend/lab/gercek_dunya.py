"""**GERÇEK-DÜNYA KORPUSU** — persona × zorluk merdiveni. *(denetim §9.6)*

## 🔴 Neden var: mevcut korpus KENDİ SÖZLÜĞÜNÜ ölçüyor

`lab/nl_corpus.py::gen_single()` soruyu **cevabın anahtarından** kuruyor
(`measure_synonyms_display` · `dimension_labels`). Ölçüldü: boyahane'nin 5077 tekil
sorusunun **≥%97,1'i katalog türevi**; gerçek kullanıcı dağarcığı **≤123 soru (≤%2,4)**.

> 🔴 Yani `%93,1` şu soruya cevap veriyor: *"sistem **kendi** kelimelerini tanıyor mu?"*
> — ve o soruya yüksek puan almak **şaşırtıcı değil, beklenendir**.
> Ölçülmeyen soru: *"**kullanıcının** kelimelerini tanıyor mu?"*

Ve bu, kullanıcının kendi gözlemini açıklıyor: *"bayrakları hep `off` tuttuk, hiç
değişiklik olmadı."* — **Bir A/B'nin sonucu «fark yok» ise, önce ölçen aletin o farkı
görebildiği kanıtlanmalıdır.** Bu dosya o aleti kurar.

## Şartnamenin altı kuralı — birebir

| Kural | Nasıl uygulandı |
|---|---|
| **0 · payda kutsaldır** | `nl_corpus`'a **dokunulmadı**; bu korpus onun **yanına** kurulur ve kendi tabanını yazar |
| **1 · soru cevabın anahtarından TÜRETİLMEZ** | `_katalog_sizintisi()` her vakayı **mekanik** denetler: `soru ∩ (ölçü etiketleri ∪ boyut etiketleri) = ∅`. İhlal → vaka **korpusa girmez**, sessizce geçmez |
| **2 · altı persona** | `PERSONALAR` — her biri **kendi dilini** konuşur |
| **3 · beş zorluk kademesi** | `K1…K5`; payda **kademeli** raporlanır ki bir kademedeki kayıp ötekinde saklanmasın |
| **4 · üç beyan** | her vaka `soru` + `kabul` *(doğru ∨ netleştirme ∨ dürüst ret)* + `yasak` taşır |
| **5 · vakalar TOPLANIR** | kaynak: borç defterinin **canlı** bulguları + `deneyim.py` personaları. ⚠ Uydurulmadı — her vakanın `kaynak`'ı yazılı |
| **6 · kapı yanına kurulur** | hedef **yüzde değil ilerleme**: ilk koşum **taban**dır |

## 🔴 NETLEŞTİRME BİR BAŞARIDIR

Bugünkü korpus `CLARIFY`'ı **OK saymıyor**. Oysa *"bakiye: cari mi mizan mı?"* diye
**sormak**, ₺11,86 milyonluk sessiz seçimden **iyidir**. Bu korpus onu **ayrı bir kazanç
sütunu** olarak sayar.

## Koşum

```bash
python lab/gercek_dunya.py                 # tüm personalar
python lab/gercek_dunya.py --persona ceo   # tek persona
python lab/gercek_dunya.py --kademe K4     # tek kademe
```

⚠ **Sıfır-LLM, sıfır-DB**: `route()` doğrudan çağrılır (`nl_corpus`'un HTTP turu bile
gerekmez). Maliyet **saniye**, dakika değil — §9.7/d'nin ölçtüğü gibi.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import defaultdict
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

#: Kabul sınıfları — **üçü de başarıdır**.
#: 🔴 `NETLESTIRME` bir kayıp değil: *"hangisini kastettin"* diye sormak, yanlış olana
#: kendinden emin cevap vermekten **iyidir**.
DOGRU = "dogru"              # doğru cube + doğru ölçü
NETLESTIRME = "netlestirme"  # belirsizliği fark etti, sordu
DURUST_RET = "durust_ret"    # cevaplayamayacağını söyledi
SESSIZ_YANLIS = "sessiz_yanlis"  # 🔴 **tek gerçek başarısızlık**
#: 🔴 KÖK-3 (2026-08-06) — **BEYANLI KISMİ CEVAP.** Sorunun bir parçası sorguya
#: taşınamadı **ama ürün bunu SÖYLÜYOR** (`eksik_niyet` alanı + "sayı doğru ama eksik"
#: notu). Bu bir **sessiz** yanlış DEĞİLDİR ve öyle sayılırsa ölçüm, kapatılmış bir
#: kusuru açıkmış gibi raporlar.
#:
#: ⚠ Ama bir başarı da değil: ayrı sayılır, gizlenmez. *Bir kusuru kapatmak onu
#: yok etmek değildir; sessizliğini almaktır — ve ölçüm bu farkı görmelidir.*
BEYANLI_KISMI = "beyanli_kismi"

KADEMELER = ("K1", "K2", "K3", "K4", "K5")

#: Altı persona — **aynı iş sorusu, altı ayrı ağız**.
PERSONALAR = {
    "ceo": "kısa, sonuç odaklı, ölçü adı KULLANMAZ",
    "cfo": "dönem + mutabakat dili, mali takvim",
    "uretim": "vardiya/makine/parti, kısaltma ve argo",
    "kalite": "oran + neden zinciri",
    "satis": "müşteri/segment, kıyas",
    "saha": "🔴 yazım hatası · eksik cümle · konuşma dili",
}


def _v(persona: str, kademe: str, soru: str, *, kabul: list[str], yasak: str,
       kaynak: str, cube: str | None = None) -> dict[str, Any]:
    """Bir vaka. **Üç beyan zorunlu** (kural 4) — yoksa vaka değildir.

    ⚠ `kaynak` da zorunlu (kural 5): *uydurulmuş bir vaka, uydurulmuş bir ölçüdür.*
    """
    assert persona in PERSONALAR and kademe in KADEMELER
    assert kabul and yasak and kaynak, soru
    return {"persona": persona, "kademe": kademe, "soru": soru, "kabul": kabul,
            "yasak": yasak, "kaynak": kaynak, "cube": cube}


#: 🔴 **VAKALAR — hepsi TOPLANDI, uydurulmadı** (kural 5).
#:
#: ## Kaynaklar — her satır hangisinden geldiğini söyler
#:
#: | kaynak | ne verdi |
#: |---|---|
#: | `lab/deneyim.py` **15 senaryo** | persona iskeleti + gerçek konuşma turları |
#: | `nl_corpus.REAL_PHRASINGS` **41 ifade** | katalog **dışı** kullanıcı dağarcığı |
#: | `nl_corpus.NOISE` **15** · `CAPABILITY` **8** | gürültü + yetenek sorusu |
#: | borç defteri **#16…#23** | **canlı turlardan** gelen gerçek kusurlar |
#: | denetim §9.6 persona × kademe tablosu | zorluk merdiveninin örnekleri |
#:
#: ## ⚠ KOPYA YASAĞI — ve neden mekanik bir kapı
#:
#: > *Aynı sorunun kılık değiştirmiş hâli bir vaka değildir; paydayı şişirir ve ölçümü
#: > kendi tekrarıyla besler.*
#:
#: `test_gercek_dunya_korpusu` her vaka çiftinin **anlamlı kelime kümesini** kıyaslar;
#: **%70'ten fazla** örtüşen iki vaka kapıyı kırar. Elle *"benzer değil"* demek yetmez —
#: benzerlik yazarın gözünde değil, **kelimelerde** ölçülür.
VAKALAR: list[dict[str, Any]] = [
    # 🔴 **`KÖK-S3` — DİLSEL KAPSAM ÜRETİM SIRASINA BAĞLI OLAMAZ.**
    #
    # Ölçüldü: `test_DILSEL_KAPSAM_hicbir_ozellik_bos_kalmaz` kırmızı verdi —
    # `iy.3cogul` (3. çoğul iyelik, `-ları/-leri`) **hiç üretilmiyor**. Taban ölçüldü
    # (§86.6): tabanda o özellik **ÜRETİLMİŞ** kümede vardı, statik kümede yoktu. Yani
    # kapsam bir **tesadüfe** bağlıydı: menüye bir boyut/ölçü eklenince üreteç başka
    # sorular kurdu ve o dilbilgisi biçimi **sessizce kayboldu**.
    #
    # ⊙ Bu, `KÖK-M1a`'nın (chip tesadüfi bir ayırt ediciye bağlıydı) dilbilgisi
    # tarafındaki **ikizidir** ve aynı cümleyle özetlenir: *bir güvencenin tesadüfe
    # bağlı olması, o güvencenin olmamasıdır.*
    #
    # ⚠ Çözüm üreteci değiştirmek DEĞİL — üreteç bir **ölçüm aracıdır** ve onu her
    # menü değişiminde ayarlamak, ölçtüğü şeyi ölçüme uydurmaktır. Bunun yerine biçim
    # **statik** kümeye alındı: statik vakalar menüden bağımsızdır, dolayısıyla kapsam
    # artık **yapısal olarak** garantilidir.
    #
    # ⚠ Ve soru uydurulmadı: bu, kullanıcının kendi verdiği senaryolardan biridir
    # (`s8`) — gerçek bir iş sorusu, gerçek bir dilbilgisi biçimi.
    _v("kalite", "K2", "en çok tekrarlanan tamir sebepleri neler",
       kabul=[DOGRU, NETLESTIRME],
       yasak="sebep kırılımını atlayıp tek bir toplam vermek",
       kaynak="kullanıcı senaryosu · s8 — dilsel çapa: iy.3cogul (-leri)"),
    # ⚠ **BİR VAKA YETMEZ** — kardeş kapı (`test_DILSEL_KAPSAM_zayif_ozellik_yok`)
    # en az **beş** ister ve gerekçesi kendi cümlesinde: *"sıfır kapsam bir delik, BİR
    # kapsam bir yanılsamadır."* Tek örnek, o biçimin çalıştığını değil yalnız **bir kez**
    # denendiğini kanıtlar. Dördü daha eklendi; hepsi gerçek iş sorusu, hiçbiri uydurma.
    _v("uretim", "K2", "bu yıl en çok duran makineleri listele",
       kabul=[DOGRU, NETLESTIRME],
       yasak="duruş süresini sıralamadan tek toplam vermek",
       kaynak="dilsel çapa: iy.3cogul (-leri)"),
    _v("kalite", "K2", "geçen ay fire oranı en yüksek hatları göster",
       kabul=[DOGRU, NETLESTIRME],
       yasak="hat kırılımını atlayıp tesis toplamı vermek",
       kaynak="dilsel çapa: iy.3cogul (-ları)"),
    _v("satis", "K2", "bu yıl en çok iade eden müşterileri bul",
       kabul=[DOGRU, NETLESTIRME],
       yasak="müşteri kırılımı olmadan iade toplamı vermek",
       kaynak="dilsel çapa: iy.3cogul (-leri)"),
    _v("kalite", "K3", "bu yıl ilk seferde doğru oranı en düşük tedarikçileri sırala",
       kabul=[DOGRU, NETLESTIRME],
       yasak="tedarikçi kırılımını atlamak",
       kaynak="dilsel çapa: iy.3cogul (-leri) · KÖK-S2 tedarikçi boyutu"),
    # ═══ CEO — ölçü adı KULLANMAZ, sonuç ister ═══════════════════════════════════
    _v("ceo", "K1", "işler nasıl gidiyor",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="rastgele bir ölçü seçip kendinden emin sayı vermek",
       kaynak="deneyim.py · patron sabahı deseni"),
    _v("ceo", "K1", "bu ay iyi miyiz kötü müyüz",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="iyi/kötü yargısını bir eşik uydurarak vermek",
       kaynak="§9.6 · CEO dili — yargı sorusu"),
    _v("ceo", "K2", "en çok nerede kaybediyoruz",
       kabul=[NETLESTIRME, DOGRU],
       yasak="'kayıp'ı tanımsız bırakıp rastgele bir kırılım vermek",
       kaynak="§9.6 K2 · üstünlük + kırılım"),
    _v("ceo", "K3", "geçen aya göre iyi miyiz",
       kabul=[NETLESTIRME, DOGRU],
       yasak="hangi ölçü olduğunu sormadan tek bir ölçüde kıyas yapmak",
       kaynak="deneyim.py · kiyas_turu"),
    _v("ceo", "K4", "neden böyle oldu",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="bağlam yokken bir nedensellik anlatısı kurmak",
       kaynak="deneyim.py · analist_turu (bağlamsız hâli)"),
    _v("ceo", "K5", "bu gidişle yılı nerede kapatırız",
       kabul=[DURUST_RET, NETLESTIRME],
       yasak="tahmin yeteneği yokken bir sayı uydurmak",
       kaynak="§9.6 K5 · forecast v1'de YOK"),
    _v("ceo", "K5", "ne yapmalıyız",
       kabul=[DURUST_RET, NETLESTIRME],
       yasak="veriye dayanmayan bir tavsiye üretmek",
       kaynak="§9.6 K5 · kararsal soru"),

    # ═══ CFO — dönem + mutabakat, mali takvim ════════════════════════════════════
    _v("cfo", "K1", "kapanışta bakiye tutuyor mu",
       kabul=[NETLESTIRME],
       yasak="`bakiye` iki cube'un ölçüsüyken birini SESSİZCE seçmek",
       kaynak="borç #19 · ₺11,86 M sessiz seçim (CANLI)"),
    _v("cfo", "K1", "ne kadar alacağımız var",
       kabul=[DOGRU, NETLESTIRME],
       yasak="alacağı borçla karıştırmak",
       kaynak="REAL_PHRASINGS · toplam_alacak"),
    _v("cfo", "K2", "kim bize ne kadar borçlu",
       kabul=[DOGRU, NETLESTIRME],
       yasak="'kim' bir KIRILIM isterken tek toplam vermek",
       kaynak="REAL_PHRASINGS · toplam_borc + kırılım"),
    _v("cfo", "K3", "üçüncü çeyrek gerçekleşme nasıl",
       kabul=[DOGRU, NETLESTIRME],
       yasak="çeyreği takvim yılı sanıp mali takvimi yok saymak",
       kaynak="borç · mali takvim kusuru (CANLI)"),
    _v("cfo", "K3", "yılbaşından bugüne nasıl gidiyor",
       kabul=[DOGRU, NETLESTIRME],
       yasak="YTD ifadesini tek bir aya indirgemek",
       kaynak="§9.6 K3 · dönem ifadesi"),
    _v("cfo", "K4", "tahsilat neden yavaşladı",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="yavaşlamayı ölçmeden bir sebep anlatmak",
       kaynak="REAL_PHRASINGS · tahsilatlar + nedensellik"),

    # ═══ ÜRETİM — vardiya/makine/parti, kısaltma ve argo ═════════════════════════
    _v("uretim", "K1", "gece vardiyası niye düştü",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="hangi ölçünün düştüğünü sormadan bir neden anlatmak",
       kaynak="deneyim.py · uretim_muduru_sabahi"),
    _v("uretim", "K1", "randımanımız kaç",
       kabul=[DOGRU, NETLESTIRME],
       yasak="randımanı üretim miktarıyla karıştırmak",
       kaynak="REAL_PHRASINGS · ort_oee (randıman)"),
    _v("uretim", "K2", "iki numaralı makine yine mi",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="eksik cümleyi bir ölçüye bağlayıp kendinden emin cevap vermek",
       kaynak="deneyim.py · eksik cümle turu"),
    _v("uretim", "K2", "hangi tezgahta duruş çok",
       kabul=[DOGRU, NETLESTIRME],
       yasak="'tezgah' argosunu tanımayıp sessizce başka boyuta gitmek",
       kaynak="§9.6 · üretim argosu (tezgah = makine)"),
    _v("uretim", "K3", "dün bugüne göre nasıldı",
       kabul=[DOGRU, NETLESTIRME],
       yasak="iki günü tek güne indirgemek",
       kaynak="§9.6 K3 · günlük kıyas"),
    _v("uretim", "K4", "düşüşün sebebi ne",
       kabul=[NETLESTIRME, DOGRU],
       yasak="bağlam yokken 'düşüş'ü rastgele bir ölçüye bağlamak",
       kaynak="borç #17 · «değişim» istenip TOPLAM verildi (CANLI)"),
    _v("uretim", "K4", "hangi vardiya bizi aşağı çekiyor",
       kabul=[DOGRU, NETLESTIRME],
       yasak="katkı sorusuna sıralamasız liste vermek",
       kaynak="§9.6 K4 · katkı ayrıştırması"),

    # ═══ KALİTE — oran ve neden zinciri ═════════════════════════════════════════
    _v("kalite", "K1", "ne kadar fire verdik",
       kabul=[DOGRU], cube="parti",
       yasak="fire miktarını fire ORANI sanmak (ya da tersi)",
       kaynak="REAL_PHRASINGS · fire_orani_yuzde"),
    _v("kalite", "K1", "zayiat durumumuz ne alemde",
       kabul=[DOGRU, NETLESTIRME],
       yasak="'zayiat' eşanlamını tanımayıp ilgisiz cube'a gitmek",
       kaynak="REAL_PHRASINGS · zayiat"),
    _v("kalite", "K2", "nerede artıyor bu",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="'bu' neyi işaret ettiği belirsizken bir rapor üretmek",
       kaynak="deneyim.py · atif_ifadesi"),
    _v("kalite", "K3", "geçen seneye göre daha mı iyiyiz",
       kabul=[NETLESTIRME, DOGRU],
       yasak="hangi ölçüde kıyas yapıldığını söylememek",
       kaynak="§9.6 K3 · yıllık kıyas"),
    _v("kalite", "K4", "rework neden arttı",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="artışı doğrulamadan bir sebep sıralamak",
       kaynak="§9.6 K4 · neden zinciri"),

    # ═══ SATIŞ — müşteri/segment, kıyas ═════════════════════════════════════════
    _v("satis", "K1", "ne kadar sattık",
       kabul=[DOGRU, NETLESTIRME],
       yasak="satış tutarı ile satış miktarını karıştırmak",
       kaynak="REAL_PHRASINGS · satis_tutari"),
    _v("satis", "K1", "kaç kilo sevk ettik",
       kabul=[DOGRU, NETLESTIRME],
       yasak="miktar sorusuna tutar cevabı vermek",
       kaynak="REAL_PHRASINGS · satis_miktari"),
    _v("satis", "K2", "hangi müşteri bizi taşıyor",
       kabul=[DOGRU, NETLESTIRME],
       yasak="üstünlük ifadesini yok sayıp sıralamasız liste vermek",
       kaynak="borç #21 · üstünlük ifadesi (CANLI)"),
    _v("satis", "K2", "en çok kim alıyor",
       kabul=[DOGRU, NETLESTIRME],
       yasak="'en çok'u sıralama değil filtre sanmak",
       kaynak="§9.6 K2 · üstünlük, ikinci ağız"),
    _v("satis", "K3", "ocakla haziranı karşılaştır",
       kabul=[DOGRU, NETLESTIRME],
       yasak="iki dönemi tek döneme indirgeyip birini yok saymak",
       kaynak="§9.6 K3 · iki dönem"),
    _v("satis", "K4", "ciro düşüşünde kimin payı var",
       kabul=[DOGRU, NETLESTIRME],
       yasak="katkı sorusuna toplam vermek",
       kaynak="§9.6 K4 · katkı ayrıştırması"),
    _v("satis", "K5", "hangi müşteriye odaklanmalıyız",
       kabul=[DURUST_RET, NETLESTIRME],
       yasak="veriye dayanmayan bir öncelik sıralaması vermek",
       kaynak="§9.6 K5 · kararsal soru"),

    # ═══ SAHA — 🔴 yazım hatası · eksik cümle · konuşma dili ═════════════════════
    _v("saha", "K1", "bu ayki fire ne kdr",
       kabul=[DOGRU, NETLESTIRME], cube="parti",
       yasak="kısaltmayı anlamayıp dürüst ret yerine yanlış ölçü seçmek",
       kaynak="deneyim.py · yazim_hatali_gercek_kullanici"),
    _v("saha", "K1", "musetri bazinda ciro",
       kabul=[DOGRU, NETLESTIRME],
       yasak="🔴 yazım hatasını düzeltmeden RASTGELE bir cube'a gitmek",
       kaynak="§9.7/b · harf devrikliği (aksan DEĞİL — `_norm` kapatıyor)"),
    _v("saha", "K1", "mikatr ne kadar",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="bozuk kelimeyi düzeltmeden bir ölçüye bağlamak",
       kaynak="§9.7/b · ölçülen mutasyon (mikatr ~ miktar 0,833)"),
    _v("saha", "K2", "peki ya geçen sene",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="bağlamsız bir takip sorusuna bağlam varmış gibi cevap vermek",
       kaynak="deneyim.py · bağlam kopması turu"),
    _v("saha", "K2", "bunu makinelere böl",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="dayanak bir rapor yokken kırılım uygulamak",
       kaynak="deneyim.py · grafik_ustunde (dayanaksız hâli)"),
    _v("saha", "K3", "gecen hafta daha mi iyiydi",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="aksansız yazımı tanımayıp dürüst ret vermek",
       kaynak="§9.7/b · aksansız yazım kontrol vakası"),

    # ═══ GÜRÜLTÜ ve YETENEK — cevaplamamak da bir davranıştır ═══════════════════
    _v("saha", "K1", "asdf qwerty zxcv",
       kabul=[DURUST_RET],
       yasak="🔴 anlamsız girdiye bir cube seçip sayı üretmek",
       kaynak="nl_corpus.NOISE · anlamsız girdi"),
    _v("ceo", "K1", "neler yapabilirsin",
       kabul=[DURUST_RET, NETLESTIRME],
       yasak="yetenek sorusuna bir veri sorgusu koşmak",
       kaynak="nl_corpus.CAPABILITY"),
    _v("saha", "K1", "bana bir fıkra anlat",
       kabul=[DURUST_RET],
       yasak="kapsam dışı isteği bir veri sorusuna çevirmek",
       kaynak="nl_corpus.NOISE · kapsam dışı"),
    _v("cfo", "K1", "drop table faturalar",
       kabul=[DURUST_RET],
       yasak="🔴 kötü niyetli girdiyi bir sorguya çevirmek",
       kaynak="nl_corpus.NOISE · kötü niyet"),
]


def _katalog_etiketleri(schema: dict) -> set[str]:
    """Kataloğun **kendi sözlüğü** — kural 1'in ölçüsü."""
    kelimeler: set[str] = set()
    for cube in (schema.get("cubes") or []):
        for alan in ("measure_synonyms_display", "dimension_labels"):
            deger = cube.get(alan) or {}
            if isinstance(deger, dict):
                for v in deger.values():
                    for parca in (v if isinstance(v, list) else [v]):
                        kelimeler |= {w.lower() for w in str(parca).split() if len(w) > 3}
        for m in (cube.get("measures") or []):
            ad = m.get("name") if isinstance(m, dict) else m
            kelimeler |= {w.lower() for w in str(ad).split("_") if len(w) > 3}
    return kelimeler


def katalog_sizintisi(soru: str, etiketler: set[str], hamlar: set[str]) -> list[str]:
    """🔴 **KURAL 1'in mekanik kapısı** — ve **kalibrasyonu ÖLÇÜMLE düzeltildi.**

    ## ⚠ İlk yazım şartnameyi HARFİYEN uyguladı ve fazla sıkı çıktı

    Şartname *"soru metni ∩ etiketler = ∅"* diyor. Uygulandı ve **15 vakanın 8'i**
    elendi: `fire` · `bakiye` · `müşteri` · `makine` · `ciro`. Oysa bunlar *"cevabın
    anahtarı"* değil, **işin kendi kelimeleri** — üretim müdürü *"fire"* der, başka
    kelimesi yoktur.

    > 🔴 Kuralın **niyeti** şuydu: soru, etiketten **TÜRETİLMESİN** (`gen_single`'ın
    > yaptığı gibi: etiket × dönem × boyut şablonu). Bir insan cümlesinin içinde *"fire"*
    > geçmesi bir **türetme** değil, bir **dağarcıktır**.
    >
    > *Bir kuralı harfiyen uygulamak, onu amacının tersine çevirebilir.*

    ## İki mekanik imza — ikisi de TÜRETMEYİ yakalar, dağarcığı değil

    | # | sızıntı | neden |
    |---|---|---|
    | 1 | **ham tanımlayıcı** (`toplam_fire_kg`, `fire_orani_yuzde`) | kullanıcı asla böyle konuşmaz; oradaysa **kopyalanmıştır** |
    | 2 | sorunun **tamamı** katalog kelimesi | `gen_single`'ın imzası: bağlaç/fiil yok, yalnız etiket+dönem+boyut |

    ⚠ Sessizce elemek **yasak**: sızıntı **raporlanır**. *Bir vakayı sessizce düşürmek,
    paydayı sessizce kırpmaktır.*
    """
    kelimeler = [w.strip(".,?!").lower() for w in soru.split() if len(w) > 2]
    if not kelimeler:
        return []
    # 1 · ham tanımlayıcı — tek başına yeterli kanıt
    ham = sorted({w for w in kelimeler if w in hamlar or "_" in w})
    if ham:
        return ham
    # 2 · sorunun TAMAMI katalog kelimesi → şablon imzası
    anlamli = [w for w in kelimeler if len(w) > 3]
    if anlamli and all(w in etiketler for w in anlamli):
        return sorted(anlamli)
    return []


def _sinifla(sonuc: dict | None, vaka: dict) -> str:
    """`route()` çıktısı → kabul sınıfı.

    ⚠ **Netleştirmeyi bir kayıp saymak**, bugünkü korpusun kusuru; burada tekrarlanmaz.

    ## 🔴 SINIR — ve bu tablo okunurken UNUTULMAMALI

    Bu araç **yalnız deterministik katmanı** (`route()`) ölçer. `route()` `None` dönmesi
    **ürünün başarısızlığı DEĞİLDİR**: `/ask` orada durmaz, Intent-JSON ve Discovery
    basamaklarına devam eder. Buradaki `durust_ret` bu yüzden *"sıfır-LLM yol pes etti"*
    demektir, *"kullanıcı cevapsız kaldı"* değil.

    > 🔴 **Ama ölçtüğü şey tam da aranan şeydir:** *"kullanıcının kendi kelimeleriyle
    > sorduğunda **LLM'siz** yol nereye kadar gidiyor?"* — çünkü ürünün tezi budur
    > (*"LLM garson, küp aşçı"*) ve mevcut korpus bunu **kataloğun kendi kelimeleriyle**
    > ölçtüğü için hep yüksek çıkıyor.

    ## 🔴 ANLAM DENETİMİ — cube kimliği YETMEZ

    İlk hâlim yalnız `cq["cube"] != vaka["cube"]` diye bakıyordu. Bir denetim ajanı
    bunun **göremediği** bir sessiz-yanlışı canlıda ölçtü:

    ```
    «mart cirosunu şubat ile kıyasla»
      → parti.toplam_ciro · tarih >= 2026-02-01 AND tarih <= 2026-03-31
      → compare_mode = None
    ```

    **Kullanıcı iki ayı KIYASLA dedi; sistem iki ayı TOPLADI** — tek bir sayı döndü,
    üstelik `source=cube` rozetiyle ve Query Contract'ıyla. Cube doğru, ölçü doğru,
    **niyet yanlış**.

    > ⚠ *Doğru cube'a gitmek doğru cevap vermek değildir.* Bir sınıflandırıcı yalnız
    > kimliğe bakarsa, ürünün en tehlikeli hata sınıfını — doğru görünen yanlış cevabı —
    # yapısal olarak göremez. Ve göremediği şeyi kimse aramaz.

    Aşağıdaki denetim, niyetin **sorgunun şeklinde** karşılığı olup olmadığına bakar:
    kıyas niyeti `compare_mode` ister, kırılım niyeti `dimensions` ister, üstünlük
    niyeti `order_by`/`limit` ister. Karşılığı yoksa → **sessiz-yanlış**.
    """
    if sonuc is None:
        # `route()` pes etti → dürüst ret ya da netleştirme yolu. Hangisi olduğunu
        # `/ask` bilir; `route()` düzeyinde ikisi **ayırt edilemez** ve bu **yazılı**.
        return DURUST_RET
    cq = (sonuc or {}).get("cube_query") or {}
    if vaka.get("cube") and cq.get("cube") != vaka["cube"]:
        return SESSIZ_YANLIS
    if _niyet_karsiligi_yok(cq, vaka.get("niyet"), vaka.get("soru", "")):
        # 🔴 KÖK-3 — bu artık **SESSİZ** bir yanlış DEĞİL: `/ask` cevabı `eksik_niyet`
        # alanıyla ve *"sayı doğru ama eksik"* notuyla gönderiyor. Ayrı sayılır,
        # gizlenmez. *Bir kusuru kapatmak onu yok etmek değildir; sessizliğini almaktır.*
        return BEYANLI_KISMI
    return DOGRU


def _niyet_karsiligi_yok(cq: dict, niyet: str | None, soru: str = "") -> bool:
    """Niyetin sorgu şeklinde karşılığı **var mı** — kararı `app.uyum` verir.

    ## 🔴 İKİNCİ SAHİP KAPANDI (2026-08-06)

    Bu fonksiyon kendi niyet denetimini yazıyordu (`kiyas_var` · `boyut_var` ·
    `sira_var`). Sonra `app/uyum.py` **aynı soruyu** ürün tarafında yedi değişmezle
    cevaplayan bir modül olarak indi — yani aynı kural iki yerde yaşamaya başladı ve
    biri güncellenince öteki bayatlayacaktı.

    ⚠ Ve bu, ölçüm aracında **özellikle tehlikeli**: ürün bir niyeti taşımaya
    başladığında ölçüm onu hâlâ *"taşınmadı"* diye sayarsa, kapanmış bir kusur **açık
    görünür** — ve tersi de doğru.

    *Bir ölçüm aracının kuralı, ölçtüğü ürünün kuralından ayrı yaşayamaz.*
    """
    if not niyet:
        # ⚠ Elle yazılmış vakalarda `niyet` yok → denetim ATLANIR. Bilinmeyen bir
        # beklentiyi başarısızlık saymak, ölçümü gürültüye çevirir.
        return False
    from app.uyum import denetle

    return bool(denetle(soru or "", {"cube_query": cq}))

def kos(persona: str | None = None, kademe: str | None = None,
        *, uretilmis: bool = True) -> dict[str, Any]:
    """Korpusu koşar. **Sıfır-LLM, sıfır-DB** — `route()` doğrudan.

    ## İki korpus, iki farklı iş — ve neden ikisi de gerekli

    | korpus | kaç | ne verir |
    |---|---|---|
    | `VAKALAR` (elle) | 42 | **derinlik**: her biri gerçek bir olaydan toplandı, `kaynak` taşır |
    | `senaryo_uretec.uret()` | **~10 700** | **genişlik**: pairwise, kataloğa bağlı, kendiliğinden büyür |

⚠ Kapı (`pytest`) bu korpusun **2 500'lük deterministik önekini** kullanır; tam kümeyi
yalnız bu lab koşumu üretir. *Geliştirme kapısının bütçesi 1-2 dakikadır ve o bütçe
üretime harcanamaz.*

    ⚠ Elle yazılanları üretilmişlerle **değiştirmek** yanlış olurdu: üreteç bir borç
    defteri okuyamaz. *Bir kusurun canlı turda görülmüş olması, onu kombinatoryal bir
    şablonun üretemeyeceği bir vaka yapar.* İkisi ayrı ayrı raporlanır.
    """
    import os

    from app import cube_router
    from app.config import get_settings
    from app.wren_service import WrenService
    from lab import senaryo_uretec
    from lab.izolasyon import izole_proje_ayna

    # 🔴 ŞEMA TAZE DERLENİR — bu satır bir HIZ tercihi değil, bir DOĞRULUK şartıdır.
    #
    # ## Ölçülen kusur (2026-08-06) — **ölçüm aracının kendisi yalan söyledi**
    #
    # Bu fonksiyon şemayı `s.resolved_project_dir()`ten, yani paylaşılan
    # `demo/wren-project`ten okuyordu. O dizin **gitignore'lu bir DERLEME ARTEFAKTIDIR**
    # ve pack'ler değiştiğinde kendiliğinden yenilenmez. `nl_corpus.py` ise ta baştan
    # `izole_proje_ayna` ile **taze** derliyordu — yani iki ölçüm aracı **iki farklı
    # şemadan** okuyordu ve biri bayat olabiliyordu.
    #
    # ⊙ Bedeli ölçüldü ve ağırdı: bir katalog turunda `git checkout` ile geri alınan
    # sinonimler artefakta **YAZILI KALDI**; aynı kaynak durumda ardışık koşumlar
    # `sessiz_yanlis` için **8** ve **17**, `dogru` için **83** ve **80** verdi. Temiz
    # ağaçta kapı KIRMIZI görünüyordu. Altı ayrı ölçüm bu yüzden yanlış okundu ve
    # aralarından biri, sağlam bir değişikliğin **geri alınmasına** yol açtı.
    #
    # 🔴 *Bir ölçüm aracının bayat okuması, yanlış bir sonuçtan daha kötüdür: yanlış
    # sonuç sorgulanır, bayat okuma GÜVENİLİR.*
    #
    # ⚠ `git checkout` bu sınıfı **kapatmaz** — artefakt izlenmiyor, geri alma onu
    # görmez. Tek yapısal çözüm, ölçümün şemasını kendi derlemesinden almasıdır.
    from app.compose import compose_and_build

    os.environ["DIMA_PROJECT_DIR"] = izole_proje_ayna("gercek-dunya")
    get_settings.cache_clear()
    # ⚠ Ayna yalnız BOŞ bir çıktı dizini kurar; derlemeyi çağıran yapar (ADR-0005 —
    # `tests/conftest.py:134` ile aynı sözleşme). Aynayı kurup derlemeyi atlamak,
    # bayat şemayı **yok** şemayla değiştirirdi: daha dürüst ama yine yanlış.
    compose_and_build(get_settings())

    s = get_settings()
    svc = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    schema = svc.schema()
    etiketler = _katalog_etiketleri(schema)
    hamlar = {str(m.get("name") if isinstance(m, dict) else m).lower()
              for c in (schema.get("cubes") or []) for m in (c.get("measures") or [])}

    havuz = list(VAKALAR)
    kapsam_raporu: dict[str, Any] = {}
    if uretilmis:
        from lab import senaryo_uretec
        uret_vakalar, kapsam_raporu = senaryo_uretec.uret(schema)
        for u in uret_vakalar:
            u.setdefault("cube", None)
        havuz += uret_vakalar

    secili = [v for v in havuz
              if (not persona or v["persona"] == persona)
              and (not kademe or v["kademe"] == kademe)]

    sizinti: list[dict] = []
    sayac: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    ayrinti: list[dict] = []

    # ⚡ PARALEL DEĞERLENDİRME — korpusta ölçülmüş desen (`lab/kosut.py`).
    #
    # Seri koşumda 10 589 vaka tek çekirdeği doldurup ötekileri boş bırakıyordu.
    # 🔴 Kapsam **birebir aynı**: payda bölünüyor, azaltılmıyor — sorular birbirinden
    # bağımsız (durumsuz `route()`), sonuçlar giriş sırasına göre birleşiyor.
    # *Hız kapsamdan değil, çekirdekten satın alınır.*
    from lab import kosut

    # KURAL 1 kapısı önce koşar: sızıntılı vaka `route()`e HİÇ gitmez (boşuna iş).
    degerlendirilecek: list[dict] = []
    for v in secili:
        s_kelime = katalog_sizintisi(v["soru"], etiketler, hamlar)
        if s_kelime:
            sizinti.append({"soru": v["soru"], "kelimeler": s_kelime})
            continue
        degerlendirilecek.append(v)

    # 🔴 HAM METİN — ve bu bilinçli, ölçülmüş bir karar.
    #
    # Bir tur **normalize ederek** ölçtüm; sonra `ask.py:2473`'ü okudum:
    # `route_hit = cube_router.route(body.question, ...)` — ürün de **ham** soruyu
    # geçiyor. Normalize etmek aracı ürüne yaklaştırmıyor, **uzaklaştırıyordu**.
    # *Bir aracın ürünle aynı yolu izlediği iddia edilmez — çağrı satırı okunarak
    # görülür.*
    sonuclar = kosut.degerlendir([v["soru"] for v in degerlendirilecek], hangi="ham")

    for v, sonuc in zip(degerlendirilecek, sonuclar):
        if isinstance(sonuc, dict) and "__hata__" in sonuc:
            ayrinti.append({**v, "sinif": "hata", "not": sonuc["__hata__"]})
            sayac[v["kademe"]]["hata"] += 1
            continue
        sinif = _sinifla(sonuc, v)
        kabul_edildi = sinif in v["kabul"]
        sayac[v["kademe"]][sinif] += 1
        sayac[v["kademe"]]["toplam"] += 1
        if kabul_edildi:
            sayac[v["kademe"]]["kabul"] += 1
        ayrinti.append({**v, "sinif": sinif, "kabul_edildi": kabul_edildi})

    return {"sayac": {k: dict(vv) for k, vv in sayac.items()},
            "sizinti": sizinti, "ayrinti": ayrinti, "toplam_vaka": len(secili),
            "kapsam": kapsam_raporu, "elle_vaka": len(VAKALAR),
            "uretilmis_vaka": len(secili) - len([v for v in VAKALAR
                                                 if (not persona or v["persona"] == persona)
                                                 and (not kademe or v["kademe"] == kademe)])}


def rapor(sonuc: dict[str, Any]) -> str:
    sat = ["# GERÇEK-DÜNYA KORPUSU — persona × zorluk", "",
           "> 🔴 **Ölçülen katman: `route()` — yani SIFIR-LLM yol.** `durust_ret`,",
           "> *\"deterministik yol pes etti\"* demektir; `/ask` orada durmaz "
           "(Intent-JSON → Discovery).",
           "> Bu tablo ürünün cevapsızlığını değil, **LLM'siz yolun erişimini** ölçer —",
           "> ve ürünün tezi (*\"LLM garson, küp aşçı\"*) tam olarak o erişimdir.", ""]
    sat.append(f"Vaka: **{sonuc['toplam_vaka']}** · katalog sızıntısı: "
               f"**{len(sonuc['sizinti'])}**")
    sat.append("")
    sat.append("| Kademe | toplam | kabul | doğru | netleştirme | dürüst ret | "
               "🔴 sessiz-yanlış | ⚠ beyanlı kısmi |")
    sat.append("|---|---|---|---|---|---|---|---|")
    for k in KADEMELER:
        c = sonuc["sayac"].get(k)
        if not c:
            continue
        sat.append(f"| {k} | {c.get('toplam',0)} | **{c.get('kabul',0)}** | "
                   f"{c.get(DOGRU,0)} | {c.get(NETLESTIRME,0)} | {c.get(DURUST_RET,0)} | "
                   f"**{c.get(SESSIZ_YANLIS,0)}** | {c.get(BEYANLI_KISMI,0)} |")
    if sonuc["sizinti"]:
        sat += ["", "## ⚠ KURAL 1 İHLALİ — katalog sızıntısı (vaka korpusa GİRMEDİ)", ""]
        for z in sonuc["sizinti"]:
            sat.append(f"- `{z['soru']}` → {z['kelimeler']}")
    kotu = [a for a in sonuc["ayrinti"] if not a.get("kabul_edildi")]
    if kotu:
        sat += ["", "## 🔴 KABUL EDİLMEYEN", ""]
        for a in kotu:
            sat.append(f"- **{a['persona']}/{a['kademe']}** `{a['soru']}` → "
                       f"`{a['sinif']}` · beklenen {a['kabul']}")
            sat.append(f"  - yasak: *{a['yasak']}* · kaynak: {a['kaynak']}")
    return "\n".join(sat) + "\n"


#: Gerileme tabanı. ⚠ Bir **eşik** değil: kural 6 hâlâ geçerli, *"taban hedef değildir"*.
#: Bu dosya yalnız **düşüşü** yakalar — yüzde hedefi koymaz.
TABAN_YOLU = pathlib.Path(__file__).resolve().parent / "gercek_dunya_baseline.json"


def _ozet(sonuc: dict[str, Any]) -> dict[str, int]:
    """Tabanla kıyaslanacak **anlam taşıyan** sayılar."""
    t = {"vaka": 0, "kabul": 0, "dogru": 0, "sessiz_yanlis": 0, "beyanli_kismi": 0}
    for kademe in sonuc.get("sayac", {}).values():
        t["vaka"] += kademe.get("toplam", 0)
        t["kabul"] += kademe.get("kabul", 0)
        t["dogru"] += kademe.get(DOGRU, 0)
        t["sessiz_yanlis"] += kademe.get(SESSIZ_YANLIS, 0)
        t["beyanli_kismi"] += kademe.get(BEYANLI_KISMI, 0)
    return t


def kapi(sonuc: dict[str, Any], *, yaz: bool = False) -> tuple[int, str]:
    """Gerileme kapısı. Dönen: `(çıkış kodu, mesaj)`.

    ## 🔴 `konusma_senaryolari` tuzağı burada TEKRARLANMAZ

    `lab/kapi.py` kendi yorumunda kayıtlı: o adım bayraksız koşumda **her yolda `0`**
    döndüğü için *"dört bileşenli bir kapının dörtte biri sessizce **dekordu**"*.
    Yani kapı yeşil görünüyordu ve hiçbir şey sınamıyordu.

    > ⚠ *Kırmızı veremeyen bir kapı, kapı değildir — bir dekordur.* Bu fonksiyon
    > gerileme varsa **mutlaka** sıfırdan farklı döner ve neyin düştüğünü yazar.

    ## Neden EŞİK değil GERİLEME

    Bir eşik (*"%80'in altına düşmesin"*) bugünkü sayıyı bir söze çevirir ve ilk
    ölçümü hedefe dönüştürür (kural 6'nın yasakladığı şey). Gerileme kapısı ise
    hiçbir hedef koymaz: *dün ne kadardıysa bugün ondan az olmasın* der.
    """
    yeni = _ozet(sonuc)
    if yaz or not TABAN_YOLU.exists():
        TABAN_YOLU.write_text(json.dumps(yeni, ensure_ascii=False, indent=1),
                              encoding="utf-8")
        # 🔴 DEKOR TUZAĞININ İKİNCİ KILIĞI — ve bu, kapının kendisinden daha sinsi.
        #
        # Taban dosyası **commit edilmezse** her koşum onu yeniden yazar ve kıyaslama
        # her seferinde kendisiyle yapılır: kapı **hiçbir zaman** kırmızı veremez ama
        # yeşil görünür. Dosyanın var olması yetmez, **paylaşılıyor** olması gerekir.
        #
        # > ⚠ *Kendi yazdığı tabanla kıyaslanan bir kapı, aynadaki kendine bakıp
        # > "değişmemiş" diyen bir ölçümdür.*
        return 0, (
            f"TABAN YAZILDI → {yeni}\n"
            f"  🔴 BU DOSYAYI COMMIT ET: {TABAN_YOLU.name}\n"
            "     Commit edilmezse her koşum yeni taban yazar ve gerileme "
            "HİÇBİR ZAMAN yakalanmaz — kapı yeşil görünür, hiçbir şey sınamaz.")
    eski = json.loads(TABAN_YOLU.read_text(encoding="utf-8"))
    dusen = []
    for anahtar in ("kabul", "dogru"):
        if yeni[anahtar] < eski.get(anahtar, 0):
            dusen.append(f"{anahtar}: {eski[anahtar]} → {yeni[anahtar]}")
    # 🔴 Sessiz-yanlış ARTIŞI da gerilemedir — ve en ağırıdır: *yanlış cevap veren
    # bir sistem, sustuğunu bilen bir sistemden tehlikelidir.*
    if yeni["sessiz_yanlis"] > eski.get("sessiz_yanlis", 0):
        dusen.append(f"🔴 sessiz_yanlis ARTTI: "
                     f"{eski.get('sessiz_yanlis', 0)} → {yeni['sessiz_yanlis']}")
    if dusen:
        return 1, "KAPI KIRMIZI — gerileme:\n  " + "\n  ".join(dusen)
    return 0, f"kapı yeşil · {yeni}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Gerçek-dünya korpusu (denetim §9.6)")
    ap.add_argument("--persona", choices=sorted(PERSONALAR))
    ap.add_argument("--kademe", choices=KADEMELER)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--kapi", action="store_true",
                    help="gerileme kapısı — düşüş varsa çıkış kodu 1")
    ap.add_argument("--taban-yaz", action="store_true",
                    help="mevcut ölçümü YENİ taban olarak yaz (bilinçli kabul)")
    a = ap.parse_args()

    sonuc = kos(a.persona, a.kademe)
    if a.json:
        print(json.dumps(sonuc, ensure_ascii=False, indent=2))
        return 0

    metin = rapor(sonuc)
    print(metin)
    hedef = pathlib.Path(__file__).resolve().parent / "reports" / "gercek_dunya.md"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(metin, encoding="utf-8")
    print(f"Rapor: {hedef}")

    if a.kapi or a.taban_yaz:
        kod, mesaj = kapi(sonuc, yaz=a.taban_yaz)
        print(f"\n{mesaj}")
        return kod
    # 🔴 **Hedef yüzde DEĞİL ilerleme** (kural 6): bayraksız koşum **tabandır** ve bu
    # araç bir eşikte kırmızı vermez. *Bir tabanı hedefe çevirmek, ilk ölçümü bir söze
    # dönüştürür.* Kırmızı yalnız `--kapi` ile ve yalnız **gerilemede** gelir.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
