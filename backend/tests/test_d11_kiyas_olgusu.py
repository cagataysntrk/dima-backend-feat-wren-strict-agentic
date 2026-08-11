"""🔴 `§D11` — SONUÇTA DURAN KIYAS, CEVAPTA SÖYLENMELİ.

Ölçüldü (canlı curl, 2026-08-11): *«geçen yıla göre nasıl gidiyoruz»* sonucunda
`toplam_ciro_gecen` ve **`toplam_ciro_degisim_yuzde`** kolonları **vardı**; üretilen
olgular yalnız `single` + `measures` idi. Yani kıyas hesaplanıp yorum katmanında
atılıyordu — kullanıcı *«geçen yıla göre»* diye sordu, cevap değişimi **hiç söylemedi**.

⊙ `yoy.py:76-80` o kolonları üretiyor; `interpret.py` içinde `_gecen`/`_degisim_yuzde`
sözcükleri **hiç geçmiyordu** (`§12.12`'nin deseni, bu kez iki modül arasında).
"""

from app.interpret import interpret


def _sonuc(**kolonlar):
    return {"columns": list(kolonlar), "rows": [dict(kolonlar)], "row_count": 1}


_CQ = {"cube": "parti", "measures": ["toplam_ciro"]}


def test_kiyas_kolonu_varsa_DEGISIM_SOYLENIR():
    y = interpret(_sonuc(toplam_ciro=100.0, toplam_ciro_gecen=80.0,
                         toplam_ciro_degisim_yuzde=25.0),
                  cube_query=_CQ, units={"toplam_ciro": "₺"})
    kiyas = [f for f in y["facts"] if f["type"] == "kiyas"]
    assert kiyas, "kıyas kolonu vardı ama olgu üretilmedi"
    assert kiyas[0]["pct"] == 25.0
    assert "arttı" in kiyas[0]["text"] and "önceki dönem" in kiyas[0]["text"]
    # tek değer olgusu KORUNUR — kural ekleyicidir, daraltıcı değil
    assert any(f["type"] == "single" for f in y["facts"])


def test_kiyas_YOKSA_hicbir_sey_eklenmez():
    """`KURAL B` ruhu: kıyas kolonu olmayan bir cevap bugünküyle birebir."""
    y = interpret(_sonuc(toplam_ciro=100.0), cube_query=_CQ, units={"toplam_ciro": "₺"})
    assert not [f for f in y["facts"] if f["type"] == "kiyas"]


def test_yon_yargisi_YALNIZ_beyanli_olcude():
    """Nötr bir ölçüde *«yüksek=iyi»* varsaymayız — `_tone`'un kendi kuralı."""
    nötr = interpret(_sonuc(toplam_ciro=100.0, toplam_ciro_gecen=80.0,
                            toplam_ciro_degisim_yuzde=25.0), cube_query=_CQ)
    k = [f for f in nötr["facts"] if f["type"] == "kiyas"][0]
    assert k["favorable"] is None and "olumsuz" not in k["text"]

    beyanli = interpret(_sonuc(fire_orani=12.0, fire_orani_gecen=8.0,
                               fire_orani_degisim_yuzde=50.0),
                        cube_query={"cube": "parti", "measures": ["fire_orani"]},
                        lower_is_better={"fire_orani"})
    kb = [f for f in beyanli["facts"] if f["type"] == "kiyas"][0]
    assert kb["favorable"] is False and "olumsuz" in kb["text"], (
        "düşük-iyi bir ölçüde artış OLUMSUZ diye çerçevelenmeli")


def test_bozuk_kiyas_degeri_SESSIZCE_atlanir():
    """⚠ `§101.1` — emin olunmayan bir cümle, olmayan bir cümleden pahalıdır."""
    y = interpret(_sonuc(toplam_ciro=100.0, toplam_ciro_gecen=80.0,
                         toplam_ciro_degisim_yuzde="bilinmiyor"),
                  cube_query=_CQ)
    assert not [f for f in y["facts"] if f["type"] == "kiyas"]


def test_yatay_seyir_ARTTI_denmez():
    y = interpret(_sonuc(toplam_ciro=100.0, toplam_ciro_gecen=99.5,
                         toplam_ciro_degisim_yuzde=0.5), cube_query=_CQ)
    k = [f for f in y["facts"] if f["type"] == "kiyas"][0]
    assert "yatay seyretti" in k["text"]
