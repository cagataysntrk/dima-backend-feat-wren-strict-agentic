"""🔴🔴 `B9` — **ODAK VARLIK**: bir önceki turun seçtiği varlık, sonraki turda yaşar.

## Ölçülen kusur — canlıda İKİ thread'de, aynı kök

| thread | tur | soru | olan | olması gereken |
|---|---|---|---|---|
| A | 3 | *«peki neden düşük»* | 11 makinenin hepsi | tur 2'nin seçtiği **RAM-3** |
| B | 5 | *«o ayda hangi makine sorumlu»* | yılın tamamı → Haziran | tur 4'ün seçtiği **ay** |

Taze sorulduğunda (*«ram 3 neden düşük»*) sistem doğru çalışıyor; kaybolan şey soru
değil **referans**tı.

⚠ Bu üç kez takip adımlarını **atlayarak** denendi; üçü de ölçülüp geri alındı.
*Bir zinciri, eksik halkasını atlayarak onaramazsın.*
"""

from __future__ import annotations

from app.diyalog import odak_belirle, odak_suzgeci

_SEMA = {"cubes": [{"name": "oee", "dimensions": ["makine", "vardiya"],
                    "time_dimensions": ["tarih"]},
                   {"name": "parti", "dimensions": ["makine"],
                    "time_dimensions": ["tarih"]}]}


# ── odak KURULUR mu ────────────────────────────────────────────────────────────
def test_SIRALI_KIRILIMDA_ILK_SATIR_ODAKTIR():
    """Thread A/2: *«en düşük olanı hangisi»* → RAM-3."""
    cq = {"cube": "oee", "dimensions": ["makine"],
          "order": {"measure": "ort_oee", "direction": "asc"}}
    assert odak_belirle(cq, [{"makine": "RAM-3"}]) == {"boyut": "makine",
                                                      "deger": "RAM-3"}


def test_SIRASIZ_KIRILIMDA_ODAK_KURULMAZ():
    """🔴 Sırasız bir kırılımda 0. satırın imtiyazı YOKTUR — motorun satır sırasını
    bir anlam saymak, veriyi değil tesadüfü okumaktır."""
    assert odak_belirle({"cube": "oee", "dimensions": ["makine"]},
                        [{"makine": "RAM-1"}]) is None


def test_ZAMAN_EKSENI_DE_BIR_VARLIKTIR():
    """🔴 *«o ayda»* — odağı en çok gereken vaka. İlk yazımda yalnız `dimensions`
    sayıldı ve bu vaka sessizce dışarıda kaldı."""
    cq = {"cube": "parti", "timeDimensions": [{"dimension": "tarih",
                                               "granularity": "month"}],
          "order": {"measure": "toplam_ciro", "direction": "asc"}}
    assert odak_belirle(cq, [{"tarih__month": "2026-01-01T00:00:00"}]) == {
        "boyut": "tarih", "deger": "2026-01-01T00:00:00", "granulerlik": "month"}


def test_IKI_EKSEN_VARSA_ODAK_KURULMAZ():
    """⚠ Hangi varlığın kastedildiği belirsizdir — *belirsizi seçmek, seçmemekten
    kötüdür.*"""
    cq = {"cube": "oee", "dimensions": ["makine"],
          "timeDimensions": [{"dimension": "tarih", "granularity": "month"}],
          "order": {"measure": "ort_oee", "direction": "asc"}}
    assert odak_belirle(cq, [{"makine": "RAM-1", "tarih__month": "x"}]) is None


# ── odak OKUNUR mu ─────────────────────────────────────────────────────────────
_ODAK = {"odak": {"boyut": "makine", "deger": "RAM-3"}}
_CQ = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["vardiya"]}


def test_KOK_NEDEN_TAKIBI_ODAGA_DARALIR():
    """Thread A/3 — kusurun kendisi."""
    assert odak_suzgeci("peki neden düşük", _CQ, _ODAK, _SEMA) == [
        {"dimension": "makine", "operator": "eq", "value": "RAM-3"}]


def test_ZAMAN_ODAGI_YARI_ACIK_ARALIKTIR():
    """🔴 Thread B/5 — canlıda çalışmadı ve sebebi öğreticiydi.

    Zaman odağı bir **değer** değil bir **kova**dır: `eq` ile süzmek ayın yalnız ilk
    anını seçerdi. Ve kapalı üst sınır (`lte`) son günü düşürürdü — *bir gün eksik
    bir ay, sessizce yanlış bir sayıdır.*
    """
    odak = {"odak": {"boyut": "tarih", "deger": "2026-01-01T00:00:00",
                     "granulerlik": "month"}}
    sema = {"cubes": [{"name": "parti", "dimensions": ["makine"],
                       "time_dimensions": ["tarih"]}]}
    cq = {"cube": "parti", "dimensions": ["makine"],
          "filters": [{"dimension": "tarih", "operator": "gte",
                       "value": "2026-01-01"}]}
    assert odak_suzgeci("o ayda hangi makine sorumlu", cq, odak, sema) == [
        {"dimension": "tarih", "operator": "gte", "value": "2026-01-01T00:00:00"},
        {"dimension": "tarih", "operator": "lt", "value": "2026-02-01T00:00:00"}]


def test_KAPSAM_BIR_PIN_DEGILDIR():
    """🔴 Var olan bir **aralık** atfı engellemez; bir **`eq` pini** engeller.
    *Bir kapsamı bir pin sanmak, hatırlamayı imkânsız kılar.*"""
    sema = {"cubes": [{"name": "parti", "dimensions": ["makine"],
                       "time_dimensions": ["tarih"]}]}
    odak = {"odak": {"boyut": "makine", "deger": "RAM-3"}}
    kapsam = {"cube": "parti", "dimensions": ["makine"],
              "filters": [{"dimension": "tarih", "operator": "gte", "value": "x"}]}
    assert odak_suzgeci("o makinede neden düşük", kapsam, odak, sema)


def test_ISARET_SIFATI_ODAGA_DARALIR():
    assert odak_suzgeci("o makinede fire ne kadar", _CQ, _ODAK, _SEMA)


def test_BU_YIL_BIR_ISARET_SIFATI_DEGILDIR():
    """🔴🔴 KENDİ YÜKLEMİM YANLIŞ-POZİTİF VERDİ — kapı bunun için var.

    *«**bu** yıl toplam ciro»* hiçbir atfı olmayan **taze** bir sorudur; ilk yazımda
    odak süzgecini aldı ve bir önceki turun varlığına sessizce daraltılacaktı. Bu,
    deponun üç kez ısırıldığı sınıfın aynısı (`göre`/`bazında` aşırı yüklemesi) ve
    `§101.1`'in tarifi: *yanlış-pozitif bir yüklem, kapattığı kusurdan pahalıdır.*

    ⊙ Ayrım için yeni liste yazılmadı: `_period_hit_words` zaten dönem ifadesinin
    tükettiği kelimeleri biliyor. *Bir kelimenin sınıfını, onu zaten tüketen kurala
    sormak; ikinci bir sözlük yazmaktan hem ucuz hem tek sahiplidir.*

    🔴 Ama o sahip de **her şeyi tüketmiyor**: bu kapı `bu hafta`yı geçirdi, `bu
    çeyrek`i geçirmedi (canlıda `granülerlik=quarter` olarak çözülüyor, `bu` açıkta
    kalıyor). Sonuç: `bu` işaret sıfatları kümesinden **çıkarıldı** — gerekçesi
    `diyalog.ISARET_SIFATLARI` başında yazılı. *Bir kuralı, sahibinin kapsamadığı
    yerde de doğru sanmak; kuralı hiç yazmamaktan tehlikelidir.*
    """
    for taze in ("bu yıl toplam ciro", "bu ay fire", "bu hafta oee", "bu çeyrek ciro"):
        assert odak_suzgeci(taze, _CQ, _ODAK, _SEMA) is None, taze


def test_ATIFSIZ_TAKIP_ODAGA_DOKUNMAZ():
    """*«aylık göster»* bir daraltma değil bir granülerlik isteğidir."""
    assert odak_suzgeci("aylık göster", _CQ, _ODAK, _SEMA) is None


def test_KULLANICININ_KENDI_SUZGECI_KAZANIR():
    """🔴 Açıkça yazılmış bir süzgeç, hatırlanan bir odaktan üstündür."""
    cq = {**_CQ, "filters": [{"dimension": "makine", "operator": "eq",
                              "value": "RAM-1"}]}
    assert odak_suzgeci("o makinede neden düşük", cq, _ODAK, _SEMA) is None


def test_KUP_O_BOYUTU_TASIMIYORSA_CEKILIR():
    """⚠ Başka bir konuya geçilmişse odak geçersizdir — *bir referansı çözememek,
    onu yanlış çözmekten iyidir.*"""
    sema = {"cubes": [{"name": "oee", "dimensions": ["vardiya"]}]}
    assert odak_suzgeci("peki neden düşük", _CQ, _ODAK, sema) is None


def test_ODAK_YOKSA_HICBIR_SEY_UYDURULMAZ():
    assert odak_suzgeci("peki neden düşük", _CQ, None, _SEMA) is None
    assert odak_suzgeci("peki neden düşük", _CQ, {"tur_no": 2}, _SEMA) is None
