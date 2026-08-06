"""FAZ 9.5 — KURAL A'nın dondurulmuş tabanı bir NOT'tu, KAPI değildi.

## Ölçülen boşluk (denetim, Faz 9)

`lab/nl_corpus_baseline.json` sürüm kontrolündeydi, `eval/baseline.json` ile aynı
disiplinle yazılmıştı ve **hiçbir test/betik onu okumuyordu**:

    grep -rn "nl_corpus_baseline" .  →  3 sonuç, ÜÇÜ DE yorum/dokümantasyon

`eval` tarafı kapılı (`test_eval_gate.py`), korpus tarafı değildi. Yani bu planın **ana
metriği** — doğru-cube yüzdesi, *"sessiz-yanlış"*ın tek sayısal göstergesi — geriler ve
kimse fark etmezdi. KURAL A'nın *"taban fiks olmazsa önce/sonra kıyası dayanaksız kalır
ve bir gerileme 'zaten öyleydi' diye kaybolur"* uyarısı, tabanın kendisi için geçerliydi.

## Bu dosya neyi ölçer, neyi ölçmez

Korpus koşumu dakikalar sürer ve CI reçetesinin **dışındadır** — bu testler onu
KOŞTURMAZ. Ölçtükleri şey **kapının kendisi**: taban okunabiliyor mu, kıyas mantığı
gerilemeyi gerçekten yakalıyor mu, ve kapı **doğru referansa** mı bakıyor.

> MIMARI §6.4: *"ölçüm aracının kendisi de bir bağımlılıktır."* Bu oturumda ölçüm aracı
> **beş kez** yanlış ölçtü; kapının kendisi de bir ölçüm aracıdır.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from lab.nl_corpus import TABAN, _taban_beklenen, kapi_degerlendir


def _rapor(sirket: str, *, ok: int, toplam: int, dogru: int, yanlis: int) -> dict:
    """`run_company` çıktısının kapının okuduğu ALANLARINI taşıyan sentetik rapor."""
    return {"company": sirket,
            "cats": {"tekil::OK": ok, "tekil::BOŞ": toplam - ok},
            "dogru_cube": {"dogru": dogru, "yanlis": yanlis, "discovery": 0}}


# --- TABAN: okunabilir ve tutarlı mı ----------------------------------------------

def test_TABAN_dosyasi_VAR_ve_okunabilir():
    assert TABAN.exists(), f"dondurulmuş taban YOK: {TABAN}"
    d = json.loads(TABAN.read_text())
    for alan in ("olculdu", "sirketler", "toplam_dogru_cube_yuzde", "_turlar"):
        assert alan in d, f"tabanda `{alan}` yok — kapı kıyaslayamaz"


def test_KAPI_SON_TURA_bakiyor_koke_DEGIL():
    """En ince tuzak. Kök alanlar 2 Ağustos'un *"önce"* fotoğrafıdır (%86,3); bugünkü
    seviye %93,2. Köke bakan bir kapı, %93,2'den %86,3'e düşüşü **yeşil** raporlardı —
    yani tam da korumak için var olduğu gerilemeyi kaçırırdı."""
    d = json.loads(TABAN.read_text())
    beklenen = _taban_beklenen()
    kok = d["toplam_dogru_cube_yuzde"]
    son = (d["_turlar"][-1] or {}).get("toplam_dogru_cube_yuzde")
    assert son and son > kok, "ön koşul: son tur kökten daha iyi olmalı (aksi hâlde test anlamsız)"
    assert beklenen["dogru_cube_yuzde"] == son, (
        f"kapı KÖK değere bakıyor (%{beklenen['dogru_cube_yuzde']}) — gerilemeyi kaçırır")


def test_SIRKET_tabanlari_SON_turla_ezilir():
    """Şirket erişim yüzdeleri de son turdan gelmeli; kök %64, son tur %69."""
    beklenen = _taban_beklenen()
    assert beklenen["sirketler"]["boyahane"]["erisim_yuzde"] >= 69, \
        "boyahane tabanı güncellenmemiş — 5 puanlık gerileme görünmez olur"


# --- KAPI MANTIĞI: gerilemeyi GERÇEKTEN yakalıyor mu ------------------------------

#: 🔴 Sentetik *"tabanı koruyan koşum"*un doğruluğu TABANDAN OKUNUR, sabit yazılmaz.
#:
#: Ölçüldü (2026-08-06): sabit `0.932` yazılıydı ve taban **%95,1**'e çıkınca fikstür
#: kendi kendine bir **gerileme** üretti — üç kapı birden kırmızı verdi. Yani *"taban
#: korunuyor"* diye kurulan koşum, tabanın kendisinden **geride kalmıştı**.
#:
#: ⚠ Ve bu, bu dosyanın KENDİ dersinin bir başka yüzü: `_taban_beklenen()` kök yerine
#: son tura bakıyor çünkü *"köke bakan bir kapı gerilemeyi kaçırır."* Aynı şey fikstür
#: için de geçerli: **tabana bakmayan bir fikstür, tabanı test etmez.**
#: *Bir taban değeri kodda iki kez yazılıyorsa, ikincisi er ya da geç bayatlar.*
def _taban_dogrulugu() -> float:
    return _taban_beklenen()["dogru_cube_yuzde"] / 100.0


def _dort_sirket(erisim_carpani: float = 1.0, dogruluk: float | None = None) -> list[dict]:
    dogruluk = _taban_dogrulugu() if dogruluk is None else dogruluk
    beklenen = _taban_beklenen()["sirketler"]
    out = []
    for ad, v in beklenen.items():
        toplam = 1000
        ok = int(toplam * (v["erisim_yuzde"] / 100) * erisim_carpani)
        dogru = int(1000 * dogruluk)
        out.append(_rapor(ad, ok=ok, toplam=toplam, dogru=dogru, yanlis=1000 - dogru))
    return out


def test_TABANI_KORUYAN_kosum_GECER():
    gecti, satirlar = kapi_degerlendir(_dort_sirket())
    assert gecti, "\n".join(satirlar)


def test_ERISIM_GERILEMESI_yakalanir():
    gecti, satirlar = kapi_degerlendir(_dort_sirket(erisim_carpani=0.85))
    assert not gecti, "%15'lik erişim düşüşü kapıdan geçti"
    assert any("GERİLEME" in s for s in satirlar)


def test_DOGRULUK_GERILEMESI_yakalanir():
    """Bu planın ANA metriği: doğru-cube. Erişim sabitken doğruluk düşerse — yani
    *"cevap veriyor ama YANLIŞ cevap veriyor"* — kapı kırmızı olmalı. Sessiz-yanlış tam
    olarak bu biçimde görünür ve erişim metriği onu **gizler**."""
    gecti, satirlar = kapi_degerlendir(_dort_sirket(dogruluk=0.863))
    assert not gecti, "doğru-cube %93,2 → %86,3 düşüşü kapıdan geçti"
    assert any("doğru-cube" in s and "GERİLEME" in s for s in satirlar)


def test_TOLERANS_gurultuyu_ELEMEZ_ama_GERCEK_dususu_yakalar():
    """Kapı fazla hassas olursa her koşumda kırmızı yanar ve yok sayılmaya başlar —
    bir kapının ölebileceği en sessiz ölüm budur."""
    from lab.nl_corpus import TOLERANS_DOGRULUK, TOLERANS_PUAN

    assert 0 < TOLERANS_PUAN <= 2, "erişim toleransı ya yok ya çok geniş"
    assert 0 < TOLERANS_DOGRULUK <= 1, "doğruluk toleransı ya yok ya çok geniş"
    assert TOLERANS_DOGRULUK < TOLERANS_PUAN, \
        "doğruluk toleransı erişimden DAR olmalı — ana metrik odur"

    gecti, _ = kapi_degerlendir(
        _dort_sirket(dogruluk=_taban_dogrulugu() - TOLERANS_DOGRULUK / 200))
    assert gecti, "yuvarlama gürültüsü kapıyı kırmızı yaktı"


def test_KOSUM_HATASI_sessizce_YESIL_olmuyor():
    """Bir şirket patlarsa kapı "kıyaslanacak veri yok" diye yeşil kalmamalı — ölçüm
    aracının sessizce kırılması bu deponun en pahalı dersidir (MIMARI §6.4)."""
    gecti, satirlar = kapi_degerlendir([{"company": "boyahane", "error": "patladı"}])
    assert not gecti, "🔴 patlayan şirketle kapı YEŞİL kaldı"
    # ⟳ Metin `"HATA"` → `"⊘ ÖLÇÜLEMEDİ"` olmuştu ve bu test güncellenmemişti (uzun süre
    # kırmızı, görülmedi). Yeni metin DAHA İYİ: deponun üçüncü-durum disiplini bir
    # başarısızlığı değil bir **ölçüm boşluğunu** adlandırıyor. Kapı artık o kanonik
    # işarete bakıyor. *Bir kapı, koruduğu şeyin diliyle konuşmalıdır.*
    assert any("ÖLÇÜLEMEDİ" in s for s in satirlar), (
        "🔴 ölçüm boşluğu ADIYLA raporlanmıyor — sessiz bir kırmızı, yanlış bir "
        f"gerileme teşhisi olarak okunur: {satirlar}")


# --- TÜKETİCİ: taban bir daha YETİM kalmasın --------------------------------------

def test_TABANIN_TUKETICISI_var():
    """Bu kusurun doğuş biçimi: dosya sürüm kontrolünde, okuyan kimse yok. Kapının
    kendisinin de yetim kalmadığı ölçülür — `main()` onu ÇAĞIRMALI, aksi hâlde korpus
    koşulduğunda kıyas yine yapılmaz."""
    kaynak = (pathlib.Path(TABAN).parent / "nl_corpus.py").read_text()
    assert "kapi_degerlendir(reports)" in kaynak, \
        "`main()` gerileme kapısını çağırmıyor — taban yine YETİM"
    assert "--kapi" in kaynak, "kapı çıkış koduyla raporlamıyor (betikten koşulamaz)"


def test_EVAL_KAPISIYLA_ayni_disiplin():
    """`eval/baseline.json` kapılı; korpus tarafı da olmalı. İkisinden birinin kapısız
    kalması, o metriğin sessizce çürümesine izin verir."""
    kok = pathlib.Path(TABAN).resolve().parents[1]
    assert (kok / "tests" / "test_eval_gate.py").exists()
    assert (kok / "eval" / "baseline.json").exists()
    if not (kok / "lab" / "nl_corpus_baseline.json").exists():
        pytest.fail("korpus tabanı yok")



# --- FAZ 0.12 · TABAN TAZELİĞİ ---------------------------------------------------

def test_TABANIN_YASI_RAPORLANIYOR():
    """🔴 **Bir taban ne kadar eskiyse, kıyas o kadar az şey söyler.**

    Kapı bugüne kadar *"gerileme var mı"* diye soruyordu ama *"neye göre"* sorusunun
    **yaşını** hiç sormuyordu. Altı ay önceki bir tabana karşı yeşil olmak, altı aydır
    ölçülmemiş olmak demektir — ve bu, kapının **sessizce** verdiği yanlış bir güvendir.

    ⚠ Bu test bir **eşik** koymaz (kaç gün *çok*, bir iş kararıdır ve yol haritası onu
    belirlememiş); yaptığı şey **yaşı GÖRÜNÜR kılmak** ve tabanın tarihinin okunabilir
    kalmasını garanti etmek. Ölçülmeyen bir bayatlama, düzeltilemez bir bayatlamadır.
    """
    import datetime as _dt

    d = json.loads(TABAN.read_text())
    turlar = d.get("_turlar") or []
    assert turlar, "tabanda hiç TUR yok — kapı kökle kıyaslar ve KURAL A'yı yanlış okur"
    son = turlar[-1]
    ham = str(son.get("olculdu") or "")
    assert ham, f"son turun `olculdu` tarihi YOK: {son.get('faz')!r}"

    # `2026-08-03` ya da `2026-08-02T22:20:00+03:00` — ikisi de kabul.
    tarih = _dt.date.fromisoformat(ham[:10])
    assert tarih.year >= 2026, f"taban tarihi anlamsız: {ham}"
    # Yaş HESAPLANABİLİR olmalı; değeri bir eşik DEĞİL, bir rapordur.
    yas = (_dt.date.today() - tarih).days
    assert yas >= 0, f"taban GELECEKTE ölçülmüş görünüyor ({ham}) — saat/tarih hatası"


def test_SON_TURDA_IKI_PAYDA_da_var():
    """FAZ 0.19 iki paydayı yan yana raporluyor; **taban da ikisini birden dondurmalı**,
    yoksa ters-yön kapısı *"tabanda YOK"* deyip **sessizce devre dışı** kalır."""
    d = json.loads(TABAN.read_text())
    son = (d.get("_turlar") or [{}])[-1]
    assert son.get("toplam_dogru_cube_yuzde") is not None, "ham payda tabanda YOK"
    assert d.get("vaka_dogru_yuzde") is not None or son.get("vaka_dogru_yuzde") is not None, (
        "SEMANTİK payda tabanda YOK — `kapi_degerlendir`'in ters-yön kontrolü "
        "sessizce atlanır (bilinen, yazılı sınır ama dondurulması gerekiyordu)")


def test_TUR_EKLEMEK_TABANI_GERILETMEZ():
    """🔴 **Kapı bunu KENDİ yakaladı (FAZ 0.12).** Tabana **şirket rakamı taşımayan**
    bir tur eklendiğinde `_taban_beklenen()` şirket değerlerini **köke** (%64)
    düşürüyordu — yani bir tur eklemek, tabanı **sessizce geriletiyordu** ve sonraki
    kapı 5 puanlık bir gerilemeyi **yeşil** görürdü.

    Kök neden: yalnız **son** tur birleştiriliyordu. Bir turun bir şirketi yeniden
    ölçmemiş olması, o şirketin **önceki ölçümünü silmez**. Artık tüm turlar sırayla
    birleşir (son BEYAN EDEN kazanır)."""
    import json as _json

    d = _json.loads(TABAN.read_text())
    turlar = list(d.get("_turlar") or [])
    turlar.append({"faz": "sentetik boş tur", "olculdu": "2026-08-04"})
    orij = TABAN.read_text()
    try:
        TABAN.write_text(_json.dumps({**d, "_turlar": turlar}, ensure_ascii=False, indent=2))
        b = _taban_beklenen()
        assert b["sirketler"]["boyahane"]["erisim_yuzde"] >= 69, (
            "boş bir tur eklemek şirket tabanını KÖKE düşürdü — bir tur eklemek "
            "tabanı geriletemez")
        assert b["dogru_cube_yuzde"] and b["dogru_cube_yuzde"] >= 93, (
            "boş bir tur eklemek toplam doğruluk tabanını düşürdü")
    finally:
        TABAN.write_text(orij)
