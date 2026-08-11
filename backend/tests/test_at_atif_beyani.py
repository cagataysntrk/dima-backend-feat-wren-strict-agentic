"""🔴 `§AT` — ÇÖZÜLEMEYEN «O <BOYUT>» REFERANSI SESSİZCE DÜŞMEZ.

Ölçülen sessiz yanlış (canlı thread, 2026-08-11):

    ① «bu yıl makine bazında ortalama oee»  → 11 satır, ilk: ÖRGÜ HAT
    ② «o makinede vardiya kırılımı»          → **33 satır**, süzgeç YOK, beyan YOK

Kullanıcı tek makine sordu, 11 makine × vardiya aldı — ve cevap **makul görünüyor**,
çünkü ilk satır yine bir önceki turun en yükseği. *Doğruluğunun kanıtı gibi görünen bir
yanlış.*

⊙ Yüklem (`niyet_tasima.EKSIK_ATIF`) **kuruluydu** ve yalnız **taze** dalda çağrılıyordu.
`ask.py`'nin kendi cümlesi: *«bir kuralı yazmak, onu iki çağrı yerinin ikisinde de
kurmak değildir; eksik kurulan yer, kuralın hiç olmadığı yerden daha tehlikelidir.»*
"""

from app.uyum import atif_beyani

_CQ_SUZGECSIZ = {"cube": "oee", "measures": ["ort_oee"],
                 "dimensions": ["makine", "vardiya"],
                 "filters": [{"dimension": "tarih", "operator": "gte",
                              "value": "2026-01-01"}]}


def test_cozulmemis_atif_BEYAN_EDILIR():
    """Ölçülen vakanın ta kendisi."""
    b = atif_beyani("o makinede vardiya kırılımı", _CQ_SUZGECSIZ)
    assert b, "referans çözülmedi ama beyan üretilmedi"
    assert "çözemedim" in b and "makine" in b
    # Yol gösterir: kullanıcı ne yaparsa süzgeç kurulur
    assert "RAM-2" in b or "ör." in b


def test_SUZGEC_KURULMUSSA_beyan_YOK():
    """Referans çözülmüşse söylenecek bir eksik yoktur."""
    cq = {**_CQ_SUZGECSIZ,
          "filters": [*_CQ_SUZGECSIZ["filters"],
                      {"dimension": "makine", "operator": "eq", "value": "RAM-2"}]}
    assert atif_beyani("o makinede vardiya kırılımı", cq) == ""


def test_ISARET_SIFATI_YOKSA_beyan_YOK():
    """⚠ `§101.1` — yanlış pozitif, kusurdan pahalıdır: referans anılmamışsa susulur."""
    assert atif_beyani("makine bazında vardiya kırılımı", _CQ_SUZGECSIZ) == ""


def test_bozuk_girdide_SESSIZ():
    assert atif_beyani("", None) == ""
    assert atif_beyani("o makinede", {}) == ""


def test_SUZGEC_KURULMAZ_yalnizca_SOYLENIR():
    """🔴 Tahmin YOK: beyan bir cümledir, bir süzgeç değil.

    *«O makine»* çıkarımı yalnız **seçilmiş** bir varlıktan gelebilir; bir sıralama bir
    seçim değildir. Yanlış odak, hiç odak olmamasından pahalıdır.
    """
    import copy

    once = copy.deepcopy(_CQ_SUZGECSIZ)
    atif_beyani("o makinede vardiya kırılımı", _CQ_SUZGECSIZ)
    assert _CQ_SUZGECSIZ == once, "beyan `cube_query`'ye DOKUNMAMALI"
