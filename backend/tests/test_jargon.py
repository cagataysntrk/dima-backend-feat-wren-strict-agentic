"""§7b teknik EN jargonu (code-switching) — arketip katmanı EN terimleri taşır ve
_match_measure onları route eder ("makine bazında efficiency" → ort_oee). Deterministik."""

from app.archetypes import dim_synonyms_for, synonyms_for
from app.cube_router import _match_dims, _match_measure
from app.llm import _norm


def test_synonyms_for_includes_english_jargon():
    assert "efficiency" in synonyms_for("ort_oee")
    assert "downtime" in synonyms_for("toplam_durus_dakika")
    assert "revenue" in synonyms_for("toplam_ciro")


def test_tr_archetype_comes_before_en_jargon():
    # Ana-dil önceliği: TR arketip önce, teknik EN sonra.
    syns = synonyms_for("kar")
    assert syns.index("kazanç") < syns.index("profit")


def test_unknown_measure_empty():
    assert synonyms_for("olmayan_olcu") == []


def test_lang_subset_selects_only_requested():
    # Aktif dil seti daralınca yalnız o dilin bloğu gelir (ort_oee'nin tr arketipi yok).
    assert synonyms_for("ort_oee", ("tr",)) == []
    assert "efficiency" in synonyms_for("ort_oee", ("en",))


def test_lang_order_controls_priority():
    # Dil sırası tie-önceliği: ("en","tr") → EN önce gelir (soft-prior sıra korunur).
    syns = synonyms_for("kar", ("en", "tr"))
    assert syns.index("profit") < syns.index("kazanç")


def test_arbitrary_language_set_tolerates_unpopulated():
    # N-dil set (ör. 2 yerel + teknikler): tanımsız dil (zh) sessizce atlanır, union bozulmaz.
    assert synonyms_for("kar", ("tr", "en", "zh", "de")) == synonyms_for("kar", ("tr", "en"))


def test_match_measure_routes_english_term():
    # Şema build'i synonyms_for'u measure_synonyms'a birleştirir; burada o sonrası simüle.
    cube = {"measure_synonyms": {
        "ort_oee": [_norm(s) for s in synonyms_for("ort_oee")],
        "toplam_durus_dakika": [_norm(s) for s in synonyms_for("toplam_durus_dakika")],
    }}
    assert _match_measure(_norm("makine bazında efficiency"), cube)[0] == "ort_oee"
    assert _match_measure(_norm("downtime raporu"), cube)[0] == "toplam_durus_dakika"


def test_dimension_i18n_routes_english():
    assert "machine" in dim_synonyms_for("makine")
    cube = {"dimension_synonyms": {
        "makine": [_norm(s) for s in ["makine", *dim_synonyms_for("makine")]],
        "vardiya": [_norm(s) for s in ["vardiya", *dim_synonyms_for("vardiya")]],
    }}
    assert "makine" in _match_dims(_norm("by machine"), cube)
    assert "vardiya" in _match_dims(_norm("shift bazında"), cube)


def test_auxiliary_language_is_technical_scope_only():
    # KAPSAM AYRIMI (yanlış-dost garantisi): yerel-yalnız set yardımcı dili ARAMAZ —
    # İngilizce yalnız yardımcı-teknik dil aktifken devreye girer, "genel" aranmaz.
    assert dim_synonyms_for("makine", ("tr",)) == []          # yerel-yalnız → EN yok
    assert "machine" in dim_synonyms_for("makine", ("tr", "en"))
    # tr bloğu i18n'e karışmaz: teknik alt-küme yalnız küratörlü terim taşır.
    assert synonyms_for("ort_oee", ("tr",)) == []
