"""FAZ 0.5 — `_match_dims` kavram-başına tahkim: fazla GROUP BY kolonu regresyon kilidi.

`_match_dims` eşleşen HER boyutu döndürüyordu; tek dedup'ı `_adi`/`_kodu` sonek çiftleri
ve sabit bir jenerik-token listesiydi. Paylaşılan bir sinonim parçası yüzünden eşleşen
boyutlar bu ağdan geçiyordu.

Canlı üretilen kanıt (demo-boyahane `parti` cube'u — ikisi de `"grubu"` sinonimini taşır):

    ham_grup  : ["ham grubu", "iplik grubu", "orgu tipi", "iplik", "grubu", ...]
    yas_grubu : ["yas", "yas grubu", "yasa gore", "yas araligi", "kac yas", "grubu", ...]

    "yas grubu bazinda fire orani" → ['ham_grup', 'yas_grubu']              (2 boyut)
    "ham grubu bazinda fire orani" → ['kumas_cinsi','ham_grup','yas_grubu'] (3 boyut)

Neden ciddi: her fazla kolon GROUP BY'ı böler. Kullanıcı "yaş grubuna göre fire oranı"
sorar, cevap yaş grubu × ham grubu kırılımı olarak gelir — satır sayısı da, HER HÜCREDEKİ
SAYI da farklıdır. Cevap `source="cube"` rozetiyle, Query Contract'ıyla ve chip'leriyle
sunulur; kullanıcının yanlış olduğunu anlamasının hiçbir yolu yoktur.

Kural (`_match_measure`'ın zaten uyguladığı disiplinin boyut karşılığı): bir boyut
YALNIZCA daha spesifik bir ifadenin PAYLAŞILAN parçası sayesinde eşleştiyse düşer.
"""

from __future__ import annotations

import pytest

from app.cube_router import _match_dims

# Kanıttaki gerçek sinonim listelerinin sadeleştirilmiş hali — testin bu dosyada
# kendi kendine yetmesi için (gerçek katalog testi aşağıda `schema` fixture'ıyla).
CUBE = {
    "name": "parti",
    "dimension_synonyms": {
        "kumas_cinsi": ["kumas cinsi", "kumas", "ham", "cins"],
        "ham_grup": ["ham grubu", "iplik grubu", "iplik", "grubu"],
        "yas_grubu": ["yas", "yas grubu", "yasa gore", "grubu"],
        "renk": ["renk", "color"],
        "renk_derinlik": ["derinlik", "ton", "ton derinligi"],
        "musteri": ["musteri", "firma"],
    },
}


@pytest.mark.parametrize("q,beklenen", [
    ("yas grubu bazinda fire orani", ["yas_grubu"]),
    ("ham grubu bazinda fire orani", ["ham_grup"]),
    ("iplik grubu bazinda uretim", ["ham_grup"]),
])
def test_paylasilan_sinonim_parcasi_fazla_boyut_EKLEMEZ(q: str, beklenen: list):
    assert _match_dims(q, CUBE) == beklenen


@pytest.mark.parametrize("q,beklenen", [
    # Farklı kavramlar → ikisi de kalmalı (kural fazla agresif olmamalı).
    ("renk ve ton bazinda fire", ["renk", "renk_derinlik"]),
    ("musteri ve renk bazinda ciro", ["renk", "musteri"]),
    # Tek boyut → dokunulmaz.
    ("renk bazinda fire orani", ["renk"]),
    ("musteri bazinda fire orani", ["musteri"]),
])
def test_gercekten_farkli_boyutlar_KORUNUR(q: str, beklenen: list):
    assert sorted(_match_dims(q, CUBE)) == sorted(beklenen)


def test_esit_eslesme_gercek_belirsizliktir_ve_burada_COZULMEZ():
    """İki boyut AYNI sinonimle eşleşirse (öz alt-dizi ilişkisi YOK) bu gerçek bir
    belirsizliktir; `_match_dims` sessizce birini SEÇMEZ.

    Kayıt amaçlı: doğru çözüm `route()`'un bir belirsizlik sinyali döndürüp chip sorması
    (Faz 3.1). Bu davranış değişirse test burada görünür kılar.
    """
    cube = {"dimension_synonyms": {"a_dim": ["ortak"], "b_dim": ["ortak"]}}
    assert sorted(_match_dims("ortak bazinda ciro", cube)) == ["a_dim", "b_dim"]


# --- gerçek katalog üzerinde uçtan uca --------------------------------------

def test_gercek_katalogda_yas_grubu_tek_boyut_uretir(schema):
    """Regresyon kilidi gerçek demo-boyahane kataloğuna karşı (sentetik cube'a değil)."""
    from app.cube_router import route

    plan = route("yaş grubu bazında fire oranı bu yıl", schema)
    assert plan is not None
    dims = plan["cube_query"].get("dimensions") or []
    assert dims == ["yas_grubu"], f"fazla GROUP BY kolonu: {dims}"


def test_gercek_katalogda_ham_grubu_tek_boyut_uretir(schema):
    from app.cube_router import route

    plan = route("ham grubu bazında fire oranı bu yıl", schema)
    assert plan is not None
    dims = plan["cube_query"].get("dimensions") or []
    assert dims == ["ham_grup"], f"fazla GROUP BY kolonu: {dims}"
