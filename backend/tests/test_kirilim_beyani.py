"""🔴 `§89` — **İSTENEN KIRILIM KARŞILANMADIYSA BEYAN EDİLİR.**

## Ölçülen kusur (canlı, `belgeler/arastirma/2026-08-25_MIMARI-CIKMAZ-ARASTIRMASI.md` §10-13)

Kullanıcı *"…ağırlığı en fazla olan kalemler…"* dedi. `niyet.coz()` "kalem"i **gerçek
bir boyut adı** olarak eşleştirdi (`butce` küpünde var) — ama plan `parti` küpünü
kullandı ve `parti`'de "kalem" **yok**; plan sessizce `musteri`/`kumas_cinsi`
kullandı. Kullanıcıya bu hiç söylenmedi.

Kök neden `plan_onarim` **değil**: `plan_onarim`'in üçüncü şartı ("taşıma sonucu
sorgunun anlamını değiştirmiyor") burada sağlanmıyor — bu bir `iki_cube` durumu
(`MIMARI §2.0.3`), mekanik bir kayma değil. Çözüm burada **onarmak değil beyan
etmek**.
"""

from __future__ import annotations

from unittest.mock import patch

from app.niyet import Niyet
from app.plan_tuketici import _kirilim_beyani, _kullanilan_boyutlar, kosum_yaniti

_SORGU_CQ = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["musteri"]}
_PLAN = {"adimlar": [{"fiil": "SORGU", "cube_query": _SORGU_CQ}]}
_OUT = {"ciktilar": [[{"musteri": "X", "toplam_ciro": 1}]],
        "sorgular": [_SORGU_CQ], "makbuz": [], "sorgu_sayisi": 1, "onarimlar": []}


def test_KAYIP_KIRILIM_BEYAN_URETIR():
    """🔴 **ASIL DEĞİŞMEZ.** "kalem" istendi, kullanılmadı → beyan var."""
    with patch("app.niyet.coz", return_value=Niyet(
            soru="…kalemler…", kirilim_istendi=True, kirilimlar=["kalem"])):
        beyan = _kirilim_beyani({}, "…kalemler…", _OUT, _PLAN)
    assert beyan is not None, "🔴 kayıp kırılım sessiz kaldı"
    assert "kalem" in beyan and "musteri" in beyan, f"🔴 beyan eksik: {beyan!r}"


def test_KARSILANAN_KIRILIM_BEYAN_URETMEZ():
    """🆃 Kapının kurbanı: HER kırılım isteğinde beyan basmak da yeşil kalırdı —
    gürültü üretir, gerçek arızayı boğar. "musteri" zaten kullanıldıysa **sessiz**."""
    with patch("app.niyet.coz", return_value=Niyet(
            soru="…müşteri…", kirilim_istendi=True, kirilimlar=["musteri"])):
        beyan = _kirilim_beyani({}, "…müşteri…", _OUT, _PLAN)
    assert beyan is None, f"🔴 karşılanan kırılım için gereksiz beyan: {beyan!r}"


def test_ZIT_OLCUT_KIRILIM_ISTENDI_YANLISKEN_BILE_KAYIP_KIRILIM_BEYAN_ALIR():
    """🆃🔴 **Canlıda ölçülen gerçek regresyon.** İlk yazım `kirilim_istendi`yi de şart
    koşuyordu; kullanıcının BİREBİR cümlesinde (`§10.3`) metin klasik bir kırılım
    kalıbı ("göre"/"bazında") TAŞIMIYOR — `kirilim_istendi=False` — ama şema eşleştirmesi
    `kirilimlar=['kalem','satis_temsilcisi']`'i YİNE DE buldu. Eski kod bu yüzden
    **tam düzeltmek istediği kusuru tekrarladı**: sessiz kaldı. `niyet.py`'nin kendi
    ayrımı (kirilim_istendi=kalıp-tetikli, kirilimlar=şema-eşleşmesi) burada kasıtlı
    olarak yalnız İKİNCİSİNE bakılmasını gerektiriyor."""
    with patch("app.niyet.coz", return_value=Niyet(
            soru="…kalemler…", kirilim_istendi=False,
            kirilimlar=["kalem", "satis_temsilcisi"])):
        beyan = _kirilim_beyani({}, "…kalemler…", _OUT, _PLAN)
    assert beyan is not None, "🔴 REGRESYON: kirilim_istendi=False iken beyan yine sessiz kaldı"
    assert "kalem" in beyan and "satis_temsilcisi" in beyan


def test_KIRILIM_ISTENMEDIYSE_BEYAN_YOK():
    """Kullanıcı hiç kırılım istemediyse (`kirilim_istendi=False`) beyanın konusu yok."""
    with patch("app.niyet.coz", return_value=Niyet(soru="toplam ciro")):
        beyan = _kirilim_beyani({}, "toplam ciro", _OUT, _PLAN)
    assert beyan is None


def test_KULLANILAN_BOYUTLAR_SORGULARI_VE_ADIMLARI_BIRLESTIRIR():
    """`_kullanilan_boyutlar` hem çözülmüş `sorgular`'ı hem plandaki ham
    `cube_query`'leri (AYRISTIR/GORSEL gibi) tarar."""
    plan = {"adimlar": [
        {"fiil": "SORGU", "cube_query": _SORGU_CQ},
        {"fiil": "GORSEL", "cube_query": {"cube": "parti", "dimensions": ["kumas_cinsi"]}},
    ]}
    boyutlar = _kullanilan_boyutlar(_OUT, plan)
    assert boyutlar == {"musteri", "kumas_cinsi"}, f"🔴 eksik/fazla: {boyutlar!r}"


def test_KOSUM_YANITI_NOTE_SONUNA_BEYAN_EKLER():
    """Uçtan uca: `kosum_yaniti`'nin `note`'u, makbuz cümlesini **korur** ve beyanı sona ekler."""
    with patch("app.niyet.coz", return_value=Niyet(
            soru="…kalemler…", kirilim_istendi=True, kirilimlar=["kalem"])):
        yanit = kosum_yaniti(_OUT, _PLAN, schema={}, soru="…kalemler…")
    assert "adımda üretildi" in yanit["note"], "🔴 makbuz cümlesi kayboldu"
    assert "kalem" in yanit["note"], f"🔴 beyan `note`'a eklenmedi: {yanit['note']!r}"


def test_ZIT_OLCUT_NIYET_PATLARSA_CEVAP_DUSMEZ():
    """🆃 `niyet.coz` bir istisna atarsa (kapsam dışı bir soru, beklenmeyen şema) —
    `ADR-0020`'nin `_guvenli` ilkesiyle aynı: düşen bir **gözlem**dir, **cevap** değil."""
    with patch("app.niyet.coz", side_effect=RuntimeError("boom")):
        beyan = _kirilim_beyani({}, "…", _OUT, _PLAN)
    assert beyan is None
    with patch("app.niyet.coz", side_effect=RuntimeError("boom")):
        yanit = kosum_yaniti(_OUT, _PLAN, schema={}, soru="…")
    assert yanit["result"] is not None, "🔴 niyet patladı diye cevabın kendisi düştü"
