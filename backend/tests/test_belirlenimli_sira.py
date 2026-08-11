"""🔴🔴 `§SB` — **SIRASIZ BİR KIRILIM, HER KOŞUMDA BAŞKA BİR RAPORDUR.**

⊙ Ölçüldü (curl `CC` turu, CC-5…CC-8): **aynı** `cube_query` dört kez koşuldu, dört
farklı ilk satır geldi — `RAM-1` · `DİJİTAL BASKI` · `RAM-1` · `FERRARO SANFOR-1`.

## 🔴 Ve ilk çözümüm bir gerileme satın aldı — **tam kapı yakaladı, korpus göremedi**

SQL'e varsayılan bir dış `ORDER BY` konmuştu. Korpus **taban ile birebir** geçti
(`doğru=95 · sessiz_yanlış=8 · payda=2286`), ama süit iki testi kırdı: `dry_plan`
**JOIN budamayı** kaybediyordu (`parti` 0 → **3**, `mizan` 0 → 2). Bir sunum kararı,
planlayıcının maliyet varsayımını bozuyordu.

*Bir belirlenimsizliği düzeltmek için doğru katmanı seçmek, düzeltmenin kendisinden
önemlidir: yanlış katman, çözdüğünden pahalı bir şey bozar.*
"""

from __future__ import annotations

from types import SimpleNamespace

from app.result_shape import belirlenimli_sirala


def _yanit(cq, satirlar):
    return SimpleNamespace(cube_query=cq, result=SimpleNamespace(rows=satirlar))


_KIRILIM = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["musteri"]}
_SATIR = [{"musteri": "A", "toplam_ciro": 10.0},
          {"musteri": "B", "toplam_ciro": 30.0},
          {"musteri": "C", "toplam_ciro": 20.0}]


def test_SIRASIZ_KIRILIM_AZALAN_SIRAYA_KONUR():
    r = _yanit(_KIRILIM, list(_SATIR))
    assert belirlenimli_sirala(r) is True
    assert [s["musteri"] for s in r.result.rows] == ["B", "C", "A"]


def test_AYNI_GIRDI_AYNI_CIKTI():
    """Kapının asıl ölçüsü: iki farklı motor sırası **aynı** rapora çıkmalı."""
    a, b = _yanit(_KIRILIM, list(_SATIR)), _yanit(_KIRILIM, list(reversed(_SATIR)))
    belirlenimli_sirala(a), belirlenimli_sirala(b)
    assert a.result.rows == b.result.rows


def test_SIFIR_DEGERLI_KIRILIM_DA_SIRALANIR():
    """⚠ `sayi()` sıfır için `0.0` döner ve bir doğruluk sınavında **yanlış** okunur —
    sıfırlı bir kırılım sıralanmadan kalırdı ve kusur tam o raporlarda sürerdi."""
    r = _yanit(_KIRILIM, [{"musteri": "A", "toplam_ciro": 0},
                          {"musteri": "B", "toplam_ciro": 5}])
    assert belirlenimli_sirala(r) is True
    assert r.result.rows[0]["musteri"] == "B"


def test_METIN_DONEN_OLCU_DE_SIRALANIR():
    """Motor bazı ölçüleri **metin** döndürüyor (`"316"` — canlıda ölçüldü); `sayi()`
    ikizi tam bu yüzden var."""
    r = _yanit({"cube": "ik", "measures": ["saat"], "dimensions": ["d"]},
               [{"d": "A", "saat": "10"}, {"d": "B", "saat": "30"}])
    assert belirlenimli_sirala(r) is True
    assert r.result.rows[0]["d"] == "B"


def test_LIMIT_VARSA_DOKUNULMAZ():
    """🔴 `limit` ile birlikte bir sıra, hangi satırların döndüğünü **seçerdi** —
    bir sunum kararı bir veri kararına dönüşürdü."""
    assert belirlenimli_sirala(_yanit({**_KIRILIM, "limit": 5}, list(_SATIR))) is False


def test_KULLANICININ_KENDI_SIRASI_EZILMEZ():
    assert belirlenimli_sirala(
        _yanit({**_KIRILIM, "order": {"measure": "toplam_ciro", "direction": "asc"}},
               list(_SATIR))) is False


def test_ZAMAN_SERISI_KRONOLOJIK_KALIR():
    """Bir trend grafiğini ölçüye göre sıralamak onu okunamaz hâle getirirdi."""
    assert belirlenimli_sirala(_yanit(
        {**_KIRILIM, "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]},
        list(_SATIR))) is False


def test_KIRILIMSIZ_TOPLAM_DOKUNULMAZ():
    assert belirlenimli_sirala(_yanit(
        {"cube": "parti", "measures": ["toplam_ciro"]}, [{"toplam_ciro": 1.0}])) is False


def test_SAYISAL_OLMAYAN_OLCUDE_SUSAR():
    assert belirlenimli_sirala(_yanit(
        _KIRILIM, [{"musteri": "A", "toplam_ciro": None},
                   {"musteri": "B", "toplam_ciro": 5}])) is False


def test_YORUMDAN_ONCE_KOSAR():
    """⚠ `interpret()` *«en yüksek»* gibi olguları **satır sırasından** okuyor; sonradan
    sıralamak, yorumun okuduğu tabloyu altından çekerdi.

    *Bir sırayı, ona bakan gözden sonra düzeltmek, düzeltmek değildir.*"""
    import inspect

    from app import answer

    kaynak = inspect.getsource(answer.seal)
    assert (kaynak.index("_belirlenimli_sirala(resp)")
            < kaynak.index("_maybe_interpret(request, resp)"))
