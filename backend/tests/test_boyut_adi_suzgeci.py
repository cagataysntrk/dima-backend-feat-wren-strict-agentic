"""🔴🔴 `§DB` — **BİR BOYUTUN ADI, O BOYUTUN DEĞERİ OLAMAZ.**

## Ölçülen kusur (curl `X` turu, 2026-08-11 · X18)

    «bu yıl operatör bazında ilk seferde doğru oranı»
      garson (self-consistency %100) →
        {"dimension": "operator", "operator": "eq", "value": "Operatör"}
      §DK-2 → «Operatör» operator listesinde yok. Var olanlar: AYLİN BULUT · … (+1)
              Hangisini istersin?

`§DK-2` **doğru** davrandı — ama kullanıcı bir **kırılım** istemişti. Yani dürüst bir
red, **çıkmaz** bir red oldu: dokuz operatör adı listelendi ve sorunun kendisi cevapsız
kaldı. *Dürüst bir red bir başarı değildir.*

🔴 Kök bir dil sorunu değil bir **tür** sorunudur: hiç kimse `operator = "Operatör"` diye
süzmez. Ve kanıt katalogdadır — değer, süzdüğü boyutun **kendi adı/etiketidir**.
"""

from app import deger_capasi as dc

_SEMA = {"cubes": [{
    "name": "parti",
    "dimensions": ["operator", "musteri"],
    "dimension_labels": {"operator": "operatör", "musteri": "müşteri"},
    "dimension_synonyms": {"operator": ["operatör", "çalışan"], "musteri": ["müşteri"]},
    "dimension_values": {"operator": ["AYLİN BULUT", "MURAT DEMİR"],
                         "musteri": ["TOROS ÖRME"]},
}]}


def _cq(deger):
    return {"cube": "parti", "measures": ["ilk_seferde_tamam_yuzde"],
            "dimensions": ["operator"],
            "filters": [{"dimension": "operator", "operator": "eq", "value": deger}]}


def test_BOYUT_ADI_SUZGECI_DUSER():
    """🔴 **Kapının kalbi** — ölçülen vakanın kendisi."""
    cq = _cq("Operatör")
    b = dc.denetle(cq, _SEMA)
    assert b and b[0].boyut_adi, f"🔴 yakalanmadı: {b}"
    not_ = dc.duzelt_yerinde(cq, b)
    assert cq["filters"] == [], "🔴 süzgeç düşmedi"
    assert not_ and "kırılım" in not_


def test_TEKNIK_AD_DA_SAYILIR():
    """⚠ Etiket (`operatör`) kadar teknik ad (`operator`) da boyutun kendi adıdır."""
    cq = _cq("operator")
    assert dc.denetle(cq, _SEMA)[0].boyut_adi


def test_SINONIM_SAYILMAZ_ARTIK():
    """⟳ Bu test bir zamanlar **tersini** iddia ediyordu (*«sinonim de sayılır»*) ve tam
    kapı onu ölçümle çürüttü: katalog bir boyutun **değerlerini** sinonim yazabiliyor
    (`cinsiyet → [kadın, erkek]`). Bkz. `test_GECERLI_DEGER_ONCE_KAZANIR`.

    *Bir sözleşme değişince onu ölçen testin de değişmesi, kapının çalıştığının
    kanıtıdır.*"""
    cq = _cq("çalışan")
    assert not any(b.boyut_adi for b in dc.denetle(cq, _SEMA))


def test_GERCEK_DEGERE_DOKUNULMAZ():
    """🔴🔴 **Yanlış-pozitif kapısı** (`§101.1`): gerçek bir operatör adı süzgeci
    **aynen** kalır — yoksa bir kusuru düzeltirken kullanıcının gerçek filtresini
    silerdik."""
    cq = _cq("MURAT DEMİR")
    b = dc.denetle(cq, _SEMA)
    assert not any(x.boyut_adi for x in b)
    dc.duzelt_yerinde(cq, b)
    assert cq["filters"], "🔴 gerçek süzgeç düştü"


def test_BASKA_BOYUTUN_ADI_SAYILMAZ():
    """⚠ Yüklem **dar**: değer, süzdüğü boyutun **kendi** adına eşit olmalı. `musteri`
    boyutunu *«operatör»* diye süzmek gerçekten anlamsız olabilir ama onu bu kapı değil
    `§DK-2` (katalogda yok → netleştirme) karşılar. *Bir yüklemi genişletmek, onun
    kanıtını zayıflatmaktır.*"""
    cq = {"cube": "parti", "measures": ["x"], "dimensions": ["musteri"],
          "filters": [{"dimension": "musteri", "operator": "eq", "value": "operatör"}]}
    assert not any(b.boyut_adi for b in dc.denetle(cq, _SEMA))


def test_BEYAN_DISLAMA_CUMLESIYLE_KARISMAZ():
    """⚠ *«Etkisiz bir dışlama»* burada **yalan** olurdu: ortada bir dışlama yok, bir
    tür karışıklığı var. *Bir beyan, ölçebildiğinden fazlasını söylediği anda bir
    varsayıma dönüşür.*"""
    cq = _cq("Operatör")
    not_ = dc.duzelt_yerinde(cq, dc.denetle(cq, _SEMA))
    assert "dışlama" not in not_


def test_GECERLI_DEGER_ONCE_KAZANIR():
    """🔴🔴 **TAM KAPI BENİ İKİ KIRMIZIYLA DURDURDU — ve haklıydı.**

    İlk yazımda `§DB` kontrolü *«değer katalogda geçerli mi»* kontrolünden **ÖNCE**
    duruyordu ve `dimension_synonyms` de *«boyutun adı»* sayılıyordu. Kapı ölçtü:

        test_kirilimli_soru_da_donem_sorar → `cinsiyet = "Kadın"` süzgeci **SİLİNDİ**
        eval answered_precision            → `1.0` → **0.9741**

    Sebep katalogda yazılı: `cinsiyet`in sinonimleri `[cinsiyet, kadın, erkek, cinsiyete
    göre]` — yani sinonim kümesi bilerek **DEĞER** taşıyor (kullanıcı *«kadın
    çalışanlar»* deyince boyut bulunsun diye).

    İki düzeltme: (1) geçerli bir katalog değeri **hiçbir zaman** boyutun adı sayılmaz —
    sıra artık *önce geçerlilik*; (2) ad kümesi yalnız **ad + etiket**.

    *Bir kümeyi ne için kurulduğunu sormadan kullanmak, onun taşıdığı şeyi değil adını
    ödünç almaktır.*"""
    sema = {"cubes": [{
        "name": "ik", "dimensions": ["cinsiyet"],
        "dimension_labels": {"cinsiyet": "cinsiyet"},
        "dimension_synonyms": {"cinsiyet": ["cinsiyet", "kadın", "erkek"]},
        "dimension_values": {"cinsiyet": ["Kadın", "Erkek"]},
    }]}
    cq = {"cube": "ik", "measures": ["x"], "dimensions": ["cinsiyet"],
          "filters": [{"dimension": "cinsiyet", "operator": "eq", "value": "Kadın"}]}
    b = dc.denetle(cq, sema)
    assert not any(x.boyut_adi for x in b), "🔴 geçerli DEĞER, boyut adı sanıldı"
    dc.duzelt_yerinde(cq, b)
    assert cq["filters"], "🔴 meşru süzgeç silindi"


def test_SINONIM_ARTIK_AD_SAYILMAZ():
    """⚠ Yukarıdaki dersin kapısı: sinonim kümesi **değer** taşıyabilir, o yüzden
    *«boyutun adı»* sorusuna cevap veremez."""
    import inspect

    # ⚠ Yorum satırları **elenerek** ölçülür: bu depoda yorumlar gerekçe taşır ve bu
    # fonksiyonun yorumu tam da *neden* sinonim kullanılmadığını anlatıyor. Ham metinde
    # aramak, gerekçeyi ihlal sanmak olurdu — ilk yazımda öyle oldu ve test kırmızı verdi.
    kaynak = inspect.getsource(dc._boyutun_kendi_adi)
    kod = "\n".join(x for x in kaynak.splitlines() if not x.strip().startswith("#"))
    kod = kod.split('"""')[-1]
    assert "dimension_synonyms" not in kod
