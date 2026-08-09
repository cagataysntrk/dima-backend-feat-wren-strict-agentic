"""FAZ 7b — KARAR MATRİSİ. *Bir karşılaştırma tablosu, bir karar değil.*

## Neden bu kapı `MIMARI §12.9`'la çelişmiyor

O bölüm *"seçenekler × ölçütler × ağırlıklar"* matrisini **bilinçle reddediyor**:
*«kontrol edilebilirlik · uygulama maliyeti · risk … hiçbiri veride yok ve tahmin
edilemez … `source=cube` rozetiyle uydurma sıralama»*.

| reddedilen | buradaki |
|---|---|
| ölçütler **uydurulur** | ölçütler **katalogda var olan ölçüler** |
| ağırlıklar modelden | 🔴 **ağırlık YOK** |
| sıralama bir **yargı** | sıralama bir **ölçüm** |
"""

from __future__ import annotations

from app.ilkeller import matris, sirala

A = [{"m": "X", "ciro": 100}, {"m": "Y", "ciro": 200}, {"m": "Z", "ciro": 150}]
B = [{"m": "X", "fire": 10}, {"m": "Y", "fire": 40}]          # ⚠ Z YOK — eksik hücre


def test_MATRIS_ADAYLARI_HIZALAR():
    r = {x["m"]: x for x in matris([A, B], "m")}
    assert r["X"] == {"m": "X", "ciro": 100, "fire": 10}
    assert set(r) == {"X", "Y", "Z"}, "bir adayda eksik ölçüt varsa aday DÜŞMEZ"


def test_EKSIK_HUCRE_SIFIR_YAZILMAZ():
    """🔴 Bir adayda o ölçü hiç yoksa *«sıfır»* demek, yokluğu bir değere çevirmektir."""
    r = {x["m"]: x for x in matris([A, B], "m")}
    assert "fire" not in r["Z"], f"eksik hücre uydurulmuş: {r['Z']}"


def test_YON_BEYANDAN_OKUNUR():
    """🔴 `§W-C` — *az olan iyi* mi, sözlükten değil **`lower_is_better` beyanından**."""
    m = matris([A, B], "m")
    yuksek = sirala(m, "m", ["ciro"])[0]["m"]
    dusuk = sirala(m, "m", ["ciro"], az_iyi={"ciro"})[0]["m"]
    assert (yuksek, dusuk) == ("Y", "X"), "yön beyanı sıralamayı çevirmedi"


def test_AGIRLIK_ALANI_YOK_VE_OLMAYACAK():
    """🔴🔴 *«Sayıyı her zaman küp koyar»* ilkesinin karar-matrisi karşılığı.

    Bir `agirliklar` alanı açmak yasakladığımız aritmetiği **arka kapıdan** geri
    getirirdi: model bir sayı uydurur, o sayı sıralamayı belirler ve sonuç
    `source=cube` rozetiyle döner.
    """
    import inspect

    from app.plan_semasi import ZORUNLU_ALANLAR, plan_json_schema
    assert "agirlik" not in str(ZORUNLU_ALANLAR).lower()
    _sema = plan_json_schema({"oee": {"measures": ["ciro"], "dimensions": ["m"]}})
    assert "agirlik" not in str(_sema).lower(), "şemaya ağırlık alanı sızmış"
    assert "agirlik" not in inspect.signature(sirala).parameters


def test_EKSIK_OLCUT_CEZA_DEGIL_VE_PAYDA_YAZILIR():
    """⚠ Eksik veriyle en kötü sıraya düşürmek, **ölçülmemiş** olanı ölçülmüş gibi
    cezalandırmaktır. Ve kaç ölçütle sıralandığı **görünmeden** sıra okunamaz."""
    r = {x["m"]: x for x in sirala(matris([A, B], "m"), "m", ["ciro", "fire"])}
    assert r["Z"]["_olcut_sayisi"] == 1 and r["X"]["_olcut_sayisi"] == 2
    assert r["Z"]["_skor"] is not None, "eksik ölçüt adayı skorsuz bıraktı"


def test_SKORSUZ_ADAY_SILINMEZ_SONA_KONUR():
    """⚠ Bir adayı listeden düşürmek, onu **değerlendirilmiş** göstermektir."""
    out = sirala([{"m": "X", "ciro": 5}, {"m": "Q"}], "m", ["ciro"])
    assert [x["m"] for x in out] == ["X", "Q"]
    assert out[-1]["_skor"] is None and out[-1]["_olcut_sayisi"] == 0


def test_TEK_SATIRDA_BOLME_YOK():
    """⚠ Min=maks olduğunda normalleştirme sıfıra bölerdi."""
    assert sirala([{"m": "X", "ciro": 7}], "m", ["ciro"])[0]["_skor"] == 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# FAZ 7c/7d · RAPOR · PANO — ve YAZMAMA yeminleri
# ═══════════════════════════════════════════════════════════════════════════════

def test_RAPOR_HICBIR_SEY_HESAPLAMAZ():
    """🔴 Sayıları koşmuş adımlar koydu; bu fiil yalnız **dizer**.

    *Bir raporu üretmekle, bir raporu kurgulamak aynı şey değildir; ikincisi sayı
    uydurmanın kapısıdır.*
    """
    from app.ilkeller import rapor
    r = rapor([A, B], "Aylık")
    assert r["baslik"] == "Aylık" and len(r["bolumler"]) == 2
    assert r["bolumler"][0]["satirlar"] == A, "satırlar dokunulmadan geçmedi"
    assert r["bolumler"][0]["kolonlar"] == ["m", "ciro"]


def test_RAPOR_BOS_BOLUMU_SAYAR():
    """⚠ Bir raporun eksiğini saklamak, onu tam göstermektir."""
    from app.ilkeller import rapor
    assert rapor([A, []], "x")["bos_bolum"] == 1


def test_RAPOR_SORGULARI_YENIDEN_KOSMAZ():
    """🔴 `report.compose_report` blok başına `cube_query` alıp her bloğu **koşar**.
    Plan o sorguları ZATEN koştu; onu çağırmak aynı sorguları ikinci kez ödemekti
    (`E6`'nın cezalandırdığı şey)."""
    import inspect

    from app import ilkeller
    kaynak = inspect.getsource(ilkeller.rapor)
    for yasak in ("compose_report", "service", "cube_sql", "query("):
        assert yasak not in kaynak.split('"""')[-1], f"`{yasak}` sızmış — rapor koşuyor"


def test_PANO_YAZMAZ_TASLAK_URETIR():
    """🔴🔴 Çalıştırıcı **salt-okunur ve idempotent** kalıyor.

    İlk yan etkili fiil bunu kırardı: yarıda kalan plan **yarım pano**, iki kez koşan
    plan **ikilenen pano**, düşen tur **geri alınamayan yazma** bırakır.
    *Bir yan etkiyi bir yorumlayıcıya koymak, geri alınamazlığı sessizce satın almaktır.*
    """
    import inspect

    from app.ilkeller import pano_taslagi
    import app.ilkeller as _ilk

    t = pano_taslagi([{"cube": "oee", "measures": ["v"]}], "Panom")
    assert t["kalici"] is False and "TASLAK" in t["not"]
    assert len(t["widgetlar"]) == 1 and t["widgetlar"][0]["cube_query"]["cube"] == "oee"
    kaynak = inspect.getsource(pano_taslagi).split('"""')[-1]
    for yasak in ("Session", "commit", "add_widget", "create", "insert"):
        assert yasak not in kaynak, f"pano taslağı `{yasak}` ile YAZIYOR"
    assert not hasattr(_ilk, "pano_kaydet"), "kayıt fonksiyonu ilkellere sızmış"


def test_PANO_AYNI_SORGUYU_IKILEMEZ():
    """⚠ Bir panoda aynı kartı iki kez göstermek bir bilgi değil bir gürültüdür."""
    from app.ilkeller import pano_taslagi
    cq = {"cube": "oee", "measures": ["v"]}
    assert len(pano_taslagi([cq, dict(cq), cq], "x")["widgetlar"]) == 1


def test_PANO_SATIR_KABUL_ETMEZ():
    """🔴 Widget'lar **satır değil SORGU** taşır: satır kaydetmek bir fotoğraf, sorgu
    kaydetmek bir pano yapar. Tip sistemi bunu plan düzeyinde de kilitler."""
    from app.ilkeller import pano_taslagi
    from app.plan_semasi import GIRDI_TIPI
    assert GIRDI_TIPI["PANO"]["kaynaklar"] == "sorgu"
    assert pano_taslagi([{"m": "X", "ciro": 100}], "x")["widgetlar"] == []
