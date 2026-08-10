"""🔴🔴 `B8`/`T-3` — **KANONİK VARLIK EKSENİ**: faz 1, *beyan*.

`cekirdek/` bir anlam katmanıdır ve içinde `metrikler` (ölçü tarafı) vardı;
**`varliklar` YOKTU.** `blend_sql` eşleşmeyi **ham boyut ADI** üzerinden kuruyor
(`key_cols`), dolayısıyla aynı gerçek varlığa farklı ad veren küpler **birleşemiyor**.

## ⊙ Ölçüm borcu DARALTTI

58 boyut adının 27'si çok küplü — ama çoğu **zaten kanonik** (`makine` **10** küpte,
`hat` 6, `bolum` 6, `vardiya` 5). Gerçekten kırık **tek eksen var: müşteri** (üç ayrık
aile). *Bir borcu ölçmeden büyütmek, onu ödenemez göstermenin en kolay yoludur.*

## Bu dosya `blend`'i DEĞİŞTİRMEZ — ve bu bilinçli

`B8` iki fazdır; bu **birincisidir**: beyan. Anahtarı kanonik varlığa çevirmek ikinci
fazdır ve **grain sözleşmesi** ister — `cari` hesap düzeyinde, `parti` sipariş veren
müşteri düzeyinde. *Bir eşleşme kuralını, neyi eşleştireceğini yazmadan değiştirmek,
ölçülemeyen bir davranış değişikliğidir.*
"""

from __future__ import annotations

import collections
import pathlib

import yaml

_SOZLUK = (pathlib.Path(__file__).resolve().parents[1] / "demo" / "packs" /
           "cekirdek" / "varlik_sozlugu.yml")


def _sozluk() -> dict:
    return yaml.safe_load(_SOZLUK.read_text(encoding="utf-8")) or {}


def _cok_kuplu(schema) -> dict[str, list[str]]:
    d: dict[str, list[str]] = collections.defaultdict(list)
    for c in schema.get("cubes") or []:
        for b in (c.get("dimensions") or []):
            d[str(b)].append(str(c.get("name")))
    return {b: k for b, k in d.items() if len(k) >= 2}


def test_HER_COK_KUPLU_BOYUT_SINIFLANDIRILMIS(schema):
    """🔴 Üçüncü seçenek yok: ya bir **varlığa bağlı**, ya **zaten kanonik**, ya
    açıkça **varlık değil**.

    ⚠ Beyansız bırakmak *"bakılmadı"* ile *"bakıldı, gerek yok"*u aynı şey yapardı —
    ve o ayrım kaybolursa aynı eksen her turda yeniden tartışılır.
    """
    s = _sozluk()
    bagli = {str(b.get("kimlik")) for v in (s.get("varliklar") or [])
             for b in (v.get("baglamalar") or [])}
    bagli |= {str(b.get("ad")) for v in (s.get("varliklar") or [])
              for b in (v.get("baglamalar") or [])}
    bagli |= {str(v.get("kanonik")) for v in (s.get("varliklar") or [])
              if v.get("zaten_kanonik")}
    degil = {str(x.get("ad")) for x in (s.get("varlik_degil") or [])}
    sessiz = sorted(set(_cok_kuplu(schema)) - bagli - degil)
    assert not sessiz, (
        f"🔴 {len(sessiz)} çok küplü boyut sınıflandırılmamış: {sessiz}\n"
        "  `varlik_sozlugu.yml`'de ya bir varlığa **bağla**, ya `zaten_kanonik` yaz, "
        "ya da `varlik_degil`'e **gerekçesiyle** koy.")


def test_MUSTERI_UC_AILEYI_DE_KAPSIYOR(schema):
    """🔴 Borcun kendisi: üç aile **kesişmiyor** ve üçü de bağlanmış olmalı."""
    s = _sozluk()
    musteri = next((v for v in (s.get("varliklar") or [])
                    if v.get("kanonik") == "musteri"), None)
    assert musteri, "`musteri` varlığı beyan edilmemiş"
    kimlikler = {str(b.get("kimlik")) for b in (musteri.get("baglamalar") or [])}
    assert {"cari_kodu", "musteri", "musteri_kod"} <= kimlikler, kimlikler
    kupler = {str(b.get("kup")) for b in musteri["baglamalar"]}
    # ⚠ Sayı **canlı şemadan**: rapor 11 küp sanıyordu, `mal`/`yaslandirma` bu
    # bileşimde yüklü değil. *Bir beyanı bayat bir tabloya göre yazmak, onu ilk
    # koşumda yalan yapar.*
    assert len(kupler) >= 9, f"eksik küp bağlaması: {sorted(kupler)}"


def test_BAGLANAN_KUP_VE_BOYUT_GERCEKTEN_VAR(schema):
    """⚠ Var olmayan bir küpe/boyuta bağlanan beyan, **sessizce hiçbir şey yapmaz**."""
    index = {str(c.get("name")): c for c in (schema.get("cubes") or [])}
    for v in (_sozluk().get("varliklar") or []):
        for b in (v.get("baglamalar") or []):
            kup = index.get(str(b.get("kup")))
            assert kup, f"{v['kanonik']}: `{b.get('kup')}` diye bir küp YOK"
            boyutlar = set(kup.get("dimensions") or [])
            for alan in ("kimlik", "ad"):
                assert str(b.get(alan)) in boyutlar, (
                    f"{v['kanonik']}/{b['kup']}: `{b.get(alan)}` o küpün boyutu değil")


def test_HER_BEYAN_GEREKCE_TASIR():
    """*Gerekçesiz bir sınıflandırma, bir karar değil bir tahmindir.*"""
    s = _sozluk()
    for v in (s.get("varliklar") or []):
        assert len(str(v.get("gerekce") or "").strip()) >= 30, v.get("kanonik")
    for x in (s.get("varlik_degil") or []):
        assert len(str(x.get("neden") or "").strip()) >= 15, x.get("ad")


def test_BLEND_HENUZ_DEGISMEDI():
    """🔴 Faz 1 **yalnız beyandır**; `blend` hâlâ ham ada bakıyor ve bu **bilinçli**.

    Bu kapı, ikinci fazın sessizce yarım inmesini engeller: anahtar değiştiğinde bu
    test kırılır ve değiştiren, **grain sözleşmesini** yazdığını beyan etmek zorunda
    kalır. *Adları eşitlemek tek başına «birleşti» yanılsaması üretir.*
    """
    kaynak = (pathlib.Path(__file__).resolve().parents[1] /
              "app" / "wren_service.py").read_text(encoding="utf-8")
    assert "key_cols = [f'{td[\"dimension\"]}__{td[\"granularity\"]}'" in kaynak, (
        "`blend` anahtarı değişmiş — faz 2'ye geçildiyse GRAIN SÖZLEŞMESİ yazılmış "
        "olmalı ve bu test gerekçesiyle güncellenmeli.")
