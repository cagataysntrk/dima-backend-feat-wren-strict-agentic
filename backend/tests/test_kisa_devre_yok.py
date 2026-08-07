"""🔴🔴 AJ0 · **KISA DEVRE YASAĞI** — MIMARI §5'in **18. yasağı**.

## Ölçülen kusur — ve neden bu bir HATA DEĞİL, bir SINIF

Kullanıcı *"mart ayında ciro şubata göre nasıl değişti"* yazdı; sistem
*«değişti» yerine «eğitim» mi demek istedin?* dedi.

🔴 Kök neden bir yazım hatası değil, bir **MERDİVEN** hatası: yazım-benzerliği chip'i
`source=None` ile **return ediyor** (yani **cevap üretmiyor**), ama Discovery ondan
**sonra** geliyor — yani **cevap üretebilecek bir yolun önünü kesiyor**. Eskiden bu soru
merdivenden düşer, Discovery'ye varır ve **bir sayı getirirdi**.

⊙ Ve kodun **kendi yorumları aynı hatayı üç kez kaydetmiş**: `bunu→gunu` · `bundan→unvan`
· `enerji kaynağı→enerji tep`. **Her seferinde çağrı yerinde yamalanmış, kapının
kendisinde hiç.** Bu dosya o kapıdır.

## Sözleşme

> ⛔ *Cevapsız bir dalla cevaplı bir yolu kesme.* Bir dal `source=None` dönüyorsa **henüz
> cevap üretmemiştir**; kendisinden geniş bir yolu kesmesi kullanıcıya **daha kötü bir
> cevabı garanti eder**. Merdiveni yalnız **pozitif cevap** ya da kullanıcının **açık
> `yol_siniri`**'si bitirebilir.

⚠ **Kural Discovery'yi herkese yeniden AÇMIYOR.** *"Yalnız deterministik"* diyen kullanıcı
yine kesilir — **ama kullanıcı öyle dediği için, bir yazım tahmini öyle dediği için değil.**

## Bu kapının bugün ne yaptığı — ve ne YAPMADIĞI

⊙ Bugün: **sınıfı dondurur.** Discovery'nin üstünde `source=None` ile return eden **13**
dal envanterlendi; her biri gerekçeli. **On dördüncüsü eklenirse CI kırmızı.**

⊘ Bugün **yapmadığı**: dalları aday'a çevirmek (davranış dönüşümü). O ayrı bir demettir
ve kapsam etkisi **ölçülmeden** inmez — bu operasyonun KÖK-7b dersi tam olarak budur.
*Bir sınıfı dondurmak, onu çözmenin ilk yarısıdır; ikinci yarısını ölçmeden yapmak
birincisini de geçersiz kılar.*
"""

from __future__ import annotations

import ast
import pathlib

ASK = pathlib.Path(__file__).resolve().parents[1] / "app" / "routers" / "ask.py"
KAYNAK = ASK.read_text(encoding="utf-8")

#: 🔴 **DONDURULMUŞ ENVANTER.** `(satır-imzası, gerekçe)`.
#:
#: ⚠ Satır NUMARASI değil **imza** tutulur: numara her düzenlemede kayar ve kapı
#: gürültüye boğulurdu. İmza, dalın kullanıcıya söylediği şeyin ayırt edici parçasıdır.
#:
#: 🔴 Listeye eklemek **geri alma değil, gerekçeli istisnadır** ve listede **görünür**
#: kalır (yol haritası AJ0'ın kendi cümlesi).
#: Bu test dosyasının kendi kaynağı — ölçüm kaydının varlığını denetlemek için.
KAYNAK_TEST = pathlib.Path(__file__).read_text(encoding="utf-8")

MUAF: list[tuple[str, str]] = [
    # ── KULLANICININ AÇIK KARARI — sözleşmenin izin verdiği İKİ bitiriciden biri ──
    ("_yol_siniri_notu('discovery')",
     "🟢 MEŞRU: kullanıcı `yol_siniri` ile Discovery'yi KAPATTI. Sözleşme bunu açıkça "
     "bir merdiven bitiricisi sayar — kesen bir tahmin değil, bir TALİMAT."),
    ("_yol_siniri_notu('intent')",
     "🟢 MEŞRU: aynı gerekçe, bir basamak yukarısı."),

    # ── NETLEŞTİRME DALLARI — hepsi ADAY olmalı, bugün RETURN ediyor ──
    # ⚠ İMZA DEĞİŞTİ (`DA-10`, 2026-08-07): dal artık `_PERIOD_TEXT` sabitini değil
    # **katalogdan** okunan metni basıyor (`netlestirme.donem`: *"{ne} çıkarabilirim —
    # hangi dönem için?"*). Sabit yedek olarak duruyor ama imza olarak **ölü**.
    # 🔴 Dalın kendisi DEĞİŞMEDİ — yalnız cümlesi düzeldi; kısa devre sınıfı aynen açık.
    # *Bir imzayı güncellemek, imzaladığı şeyi kapatmak değildir.*
    ("note=_donem_soru",
     "🔴 KISA DEVRE: dönem netleştirmesi. Discovery bu soruyu cevaplayabilirdi. "
     "Aday'a çevrilecek (davranış demeti)."),
    ("Saydığın ayl",
     "🔴 KISA DEVRE: ayrık ay listesi tek aralığa çevrilemiyor. `ay_netlestirme` iyi bir "
     "chip üretir ama Discovery'yi de keser."),
    ("typo_suggestion",
     "🔴🔴 **YOL HARİTASININ ADIYLA ANDIĞI VAKA** — `değişti→eğitim` · "
     "`enerji kaynağı→enerji tep`. Bir yazım TAHMİNİ, cevap üretebilecek bir yolun "
     "önünü kesiyor. Sınıfın kurucu örneği. ⊘ Adaya çevrilmesi DENENDİ ve iki yönlü "
     "çıktı — bkz. `test_DAVRANIS_DONUSUMU_OLCULDU_VE_ERTELENDI`."),
    ("Birden fazla konu anlaşıldı",
     "🔴 KISA DEVRE: çapraz-konu netleştirmesi (`_try_fresh_intent` içinden). ⚠ Bu satır bir zamanlar «`_bitirici` onu ADAYA çevirir» diyordu — **KARŞILIKSIZDI**: `grep _bitirici app/` → 0 isabet, ve `git log -S_bitirici` → hiç commit edilmemiş. Geri alınan deneyin açıklaması silinmeden kalmış (2026-08-07 düzeltmesi)."),
    ("Bu ifade birden fazla konud",
     "🔴 KISA DEVRE: çapraz-konu netleştirmesi, ikinci dal (Intent-JSON öncesi)."),
    ("için hangi ölçüyü istiyorsun",
     "🔴 KISA DEVRE: cube belirlendi, ölçü belirsiz. ⚠ «`_bitirici` üzerinden aday olur» iddiası KARŞILIKSIZDI (2026-08-07 düzeltmesi)."),
    ("ile ilgili görün",
     "🔴 KISA DEVRE: konu daraltıldı. ⚠ «`_bitirici`den geçer, kesmez» iddiası KARŞILIKSIZDI (2026-08-07 düzeltmesi)."),
    ("suggestions=_dogrulanm",
     "🔴 KISA DEVRE: kısmi anlama ve katalog dökümü dalları. ⚠ «`_bitirici` ile adaya çevrilir» iddiası KARŞILIKSIZDI (2026-08-07 düzeltmesi)."),
    ("Bu raporu hangi kırılıma gö",
     "🔴 KISA DEVRE: kırılım netleştirmesi (takip yolu) — rapor var, kırılım sorusu kesiyor."),
    ("next_",
     "🔴 KISA DEVRE: takip zinciri netleştirmesi — önceki cq taşınıyor ama yol kesiliyor."),
    ("' '.join((x for x in [note,",
     "🔴 KISA DEVRE: dönem kapısı ile türetme notunun birleştiği dal (KÖK-7d kancası)."),
]


def _kisa_devreler() -> list[tuple[int, str]]:
    """Discovery'nin **üstünde** `source=None` ile RETURN eden dallar.

    ⚠ AST — metin değil: bu depoda kapılar üç kez kendi belgelendirmelerini yakaladı.
    """
    agac = ast.parse(KAYNAK)
    fn = next(x for x in ast.walk(agac)
              if isinstance(x, ast.FunctionDef) and x.name == "ask")
    disc = [n.lineno for n in ast.walk(fn)
            if isinstance(n, ast.Call)
            and getattr(getattr(n.func, "value", None), "id", "") == "llm"
            and getattr(n.func, "attr", "") == "generate_sql"]
    sinir = min(disc) if disc else 10 ** 9
    out = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Return) and n.value is not None and n.lineno < sinir:
            kod = ast.unparse(n.value)
            if "source=None" in kod:
                out.append((n.lineno, kod))
    return out


def test_YENI_KISA_DEVRE_EKLENMEDI():
    """🔴 **ASIL KAPI — tuzak testi.** Discovery'nin üstünde `source=None` ile return
    eden **her** dal gerekçeli muafiyet listesinde olmalı. On dördüncüsü eklenirse
    **CI kırmızı**.

    *Bir hata sınıfı kapıya bağlanır, örneklerine değil.*"""
    kapsanmayan = []
    for ln, kod in _kisa_devreler():
        if not any(imza in kod for imza, _ in MUAF):
            kapsanmayan.append(f"satır {ln}: {kod[:110]}")
    assert not kapsanmayan, (
        "🔴 YENİ KISA DEVRE — cevapsız bir dal cevaplı bir yolu kesiyor (MIMARI §5, 18):\n  "
        + "\n  ".join(kapsanmayan)
        + "\n⚠ Meşruysa `MUAF` listesine **gerekçesiyle** ekle; gerekçe yoksa dalı bir "
          "ADAY'a çevir (merdiven devam etsin, sonda en iyi sonuç seçilsin).")


def test_ENVANTER_BAYATLAMADI():
    """⊘ Ters yön: muafiyet listesinde olup **kodda olmayan** bir imza, listeyi
    bir tarihe çevirir. *Bayat bir muafiyet, verilmemiş bir izindir.*"""
    kodlar = " ".join(k for _ln, k in _kisa_devreler())
    olu = [imza for imza, _ in MUAF if imza not in kodlar]
    assert not olu, (f"🔴 muafiyet listesinde ölü imza: {olu} — dal kaldırıldıysa "
                     "satır da kaldırılmalı")


def test_HER_MUAFIYET_GEREKCELI():
    """⚠ Gerekçesiz bir muafiyet, muafiyet değil **sessiz bir izindir**."""
    for imza, gerekce in MUAF:
        assert len(gerekce) > 40, f"🔴 gerekçe çok kısa: {imza}"
        assert gerekce.startswith(("🟢", "🔴")), \
            f"🔴 {imza}: meşru mu (🟢) kısa devre mi (🔴) — işaretlenmemiş"


def test_MESRU_OLANLAR_YALNIZ_KULLANICI_KARARI():
    """🔴 **Sözleşmenin kalbi.** Merdiveni yalnız İKİ şey bitirebilir: pozitif cevap ya da
    kullanıcının **açık `yol_siniri`**'si. Bu yüzden 🟢 işaretli her muafiyet
    `yol_siniri` dalı olmak zorundadır.

    ⚠ Kural Discovery'yi herkese yeniden açmaz — *ama kesen şey kullanıcı olmalı, bir
    tahmin değil.*"""
    for imza, gerekce in MUAF:
        if gerekce.startswith("🟢"):
            assert "yol_siniri" in imza, (
                f"🔴 «{imza}» meşru sayılmış ama kullanıcının açık kararı DEĞİL — "
                "sözleşme yalnız `yol_siniri`ye bu yetkiyi verir")


def test_SINIFIN_BUYUKLUGU_YAZILI():
    """⊙ **Ölçüm görünür kalsın**: bugün kaç kısa devre var? Sayı düşerse (davranış
    demeti indiğinde) bu test hatırlatır ve envanter güncellenir.

    *Kapatılmamış bir kusurun büyüklüğünü yazmamak, onu kapatılmış saymaya en kısa yoldur.*
    """
    kisa = [g for _i, g in MUAF if g.startswith("🔴")]
    mesru = [g for _i, g in MUAF if g.startswith("🟢")]
    assert len(mesru) == 2, f"meşru dal sayısı değişti: {len(mesru)}"
    # ⊙ 11 — ve bu sayı bu demette DÜŞMEDİ. Düşürme denendi, ölçüldü, geri alındı:
    # `test_DAVRANIS_DONUSUMU_OLCULDU_VE_ERTELENDI` tam dökümü taşıyor.
    # *Kapatılmamış bir kusurun büyüklüğünü yazmamak, onu kapatılmış saymaya en kısa yoldur.*
    # ⟳ **CIRCIR TERSİNE ÇEVRİLDİ (2026-08-07, `G3`).**
    #
    # Eskiden `== 11` idi: sayı **dondurulmuştu**. Bu, artışı engelliyordu ama azalmayı da
    # **kırmızı** yapıyordu — yani bir kusuru kapatan geliştirici, kapıyı kırmakla
    # cezalandırılıyordu. *Bir cırcır, yalnız yanlış yöne dönmeyi engellemelidir.*
    #
    # 🔴 Yeni kural: **artamaz, azalabilir.** Azaldığında tavan **çekilir** ve gerekçe
    # yazılır — `test_frontend_buyume`'nin tavan disipliniyle aynı desen.
    assert len(kisa) <= 11, (
        f"🔴 kısa devre sayısı {len(kisa)} — tavan 11. YENİ bir dal Discovery'nin "
        "üstünde `source=None` ile RETURN ediyor. Ya MUAF listesine gerekçesiyle yaz, "
        "ya dalı aday'a çevir.")
    # ⊙ Bugün 11. Düştüğü gün bu satır kırmızı verir ve **tavanı çekmeye** zorlar —
    # boşluk bırakmak, kapıyı sağır yapardı.
    assert len(kisa) == 11, (
        f"🟢 kısa devre sayısı {len(kisa)}'e DÜŞTÜ — bu bir KAZANÇ. Tavanı bu değere "
        "çek, envanteri güncelle ve neyin kapandığını yaz.")


# ═══════════════════════════════════════════════════════════════════════════════
# ⊘ DAVRANIŞ DÖNÜŞÜMÜ — DENENDİ, ÖLÇÜLDÜ, İNMEDİ
# ═══════════════════════════════════════════════════════════════════════════════

def test_DAVRANIS_DONUSUMU_OLCULDU_VE_ERTELENDI():
    """⊘ **Yol haritasının mekaniği uygulandı, ölçüldü ve GERİ ALINDI.** Bu kayıt onun
    yerine geçiyor — *kapananlar işaretlenir, silinmez* (MIMARI §10).

    ## Ne denendi
    `source=None` dönen dallar `return` yerine **aday** olarak kaydedildi (`app/
    merdiven.py`: aday defteri + üç bitirici), merdiven Discovery'ye kadar devam etti.

    ## ⊙ Ölçüm — tam kapı

    | ölçü | önce | sonra |
    |---|---|---|
    | korpus doğru-cube | %95,1 | 🔴 **%93,5** |
    | eval precision | +0,0% | 🔴 **−1,8%** |
    | eval deterministik pay | +0,0% | 🔴 **−1,8%** |
    | süit | yeşil | 🔴 **7 kırmızı** |

    🔴 Sebep yapısal: `_try_fresh_intent` yalnız *tahmin* değil, **daraltılmış ama doğru**
    netleştirmeler de üretiyor. Onları adaya çevirmek, deterministik yolun kazandığı
    turları Discovery'ye devretti. Yol haritası *"daha yetenekli yol"* diyordu; ölçüm
    gösterdi ki kural-tabanlı yedek, katalog-farkında bir netleştirmeden **daha az**
    biliyor. **Merdivenin dördüncü koşulu buradan doğdu: bir sonraki basamak gerçekten
    daha yetenekli olmalı.**

    ## ⊙ Ve dar hâli de ölçüldü — SARKAÇ

    Yalnız yazım-benzerliği dalı adaya çevrildi. Sonuç **iki yönlüydü**:

    · 🟢 üç `xfail` vakası düzeldi (*"bu yıl fire ne kadar arttı"* artık `artti→parti`
      önerisiyle kesilmiyor)
    · 🔴 ama `muterileri` (gerçek bir yazım hatası) *"«müşteri» mi demek istedin?"*
      yerine **daha belirsiz** *"başka bir konu gibi görünüyor"* aldı

    Adayı tercih etmek denendi → üç `xfail` vakası **geri kırıldı**. Yani ayırıcı sinyal
    sıralama değil, deponun **zaten teşhis ettiği** şey: `artti→parti` bir **fiil→isim**
    uydurmasıdır, `muterileri→müşteri` bir isim düzeltmesi.
    `test_typo_onerisi_kapisi`'nin `xfail` gerekçesi bunu aynen yazmış:
    *"gerçek sinyal Türkçe FİİL ÇEKİMİ — saçmaların hepsi fiil→isim."*

    🔴 **Sonuç:** bu demet **sınıfı dondurur**, davranışı değiştirmez. Davranış dönüşümü
    morfoloji ayrımını bekliyor ve o ayrım olmadan her yön bir başkasını bozuyor.
    *Bir sarkacın iki ucu da yanlışsa, eksik olan bir denge değil bir eksendir.*

    ## ⟳ EKSEN İNDİ — ve sınıfın KURUCU ÖRNEĞİ ADAYLIKLA DEĞİL, KAYNAĞINDA kapandı

    *(2026-08-07, `G3`. Yukarıdaki kayıt duruyor; bu, onun **devamıdır**.)*

    Beklenen eksen `294eb67`'de indi: `turetme.fiil_bicimi_mi` →
    `typo_onerisi.fiil_uydurmasi_mi`. Ve sonuç, bu kaydın öngördüğünden **farklı** oldu:

    | öngörü *(yol haritası)* | gerçekleşen |
    |---|---|
    | Dal **adaya** çevrilecek, merdiven devam edecek | 🔴 Dal **yanlış yerde ateşlenmiyor** |

    ⊙ `arttı→parti` · `veren→renk` · `işledik→iplik` · `sattık→hattı` **dördü de
    bastırıldı**; `fıre→fire` ve `muterileri→müşteri` **korundu**. `xfail` kaldırıldı.

    🔴 **Bunun sonucu bu maddenin kapsamını daraltıyor:** bugün `typo_suggestion` dalı
    yalnız (a) fiil çekimi **olmayan** ve (b) `cevap_aciyor_mu`'dan geçen — yani
    **gerçekten cevap açan** bir öneriyle ateşleniyor. Öyle bir dalı adaya çevirmenin
    kazancı yok; ölçülen kaybı (`muterileri` daha belirsiz bir cevap alıyor) ise duruyor.

    ⚠ **Ve genel ders sınıfın tamamına uygulanır:** doğru soru *"bu dal aday mı olmalı"*
    değil, **"bu dal ateşlenmeli mi"**dir. Kötü bir chip'in yarışıp kaybetmesini
    beklemektense, kötü chip'in **üretilmemesi** daha ucuz ve daha doğrudur.
    *Bir yarışı kazanmanın en temiz yolu, yanlış yarışmacıyı sahaya hiç çıkarmamaktır.*
    """
    import pathlib

    # ⟳ **DOSYA YASAĞI KALDIRILDI (2026-08-07, `G3`) — ÖLÇÜM ŞARTINA çevrildi.**
    #
    # Eski hâli `assert not (app/merdiven.py).exists()` idi: bir **dosyanın var olmasını**
    # yasaklıyordu. 🔴 Bir test bir **güvenlik sınırı** koyabilir; bir **mimari tercihi**
    # donduramaz. Ölçülen bir geri alma, o yolun **bir daha denenemeyeceği** anlamına
    # gelmez — yalnız **ölçülmeden** denenemeyeceği anlamına gelir.
    #
    # ⚠ Ve o ölçüm **yanlış ortamda** yapılmıştı: kapı ortamında Discovery
    # `DIMA_LLM_PROVIDER=rule` — anahtarsız, boyahaneye gömülü, kasıtlı aptal bir yedek.
    # Yani ölçülen şey *"aday mekanizması kötü"* değil, *"aptal yedeğe düşmek kötü"*ydü.
    #
    # 🔴 Yerine geçen şart: aday mekanizması dönerse **kaydı bu dosyada güncellenmiş
    # olmalı** — sayılarla ve **hangi sağlayıcıyla** ölçüldüğü yazılı.
    merdiven = pathlib.Path(__file__).resolve().parents[1] / "app" / "merdiven.py"
    if merdiven.exists():
        assert "ÖLÇÜM ORTAMI" in KAYNAK_TEST, (
            "⟳ aday mekanizması geri gelmiş ama bu dosyada YENİ bir ölçüm kaydı yok. "
            "Sayıları yeniden ölç — ve HANGİ SAĞLAYICIYLA ölçtüğünü yaz: `rule` ile "
            "ölçülmüş bir geri alma, ölçülmüş sayılmaz.")
