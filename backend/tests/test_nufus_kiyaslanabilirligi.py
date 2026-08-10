"""🔴🔴 `A12` — **PAYDANIN BİLEŞİMİ DE BİR DEĞİŞKENDİR.**

## Ölçülen kusur — ve bedeli DÖRT kapı koşumu (2026-08-10)

`D8` turunda kataloğa **üç boyut** eklendi. Kapı `doğru 95→79 · sessiz_yanlis 8→10`
dedi ve **GERİLEME** etiketi bastı. Üç ayrı biçim denendi, üçü de kırmızı.

⊙ Sonra in-process A/B koşuldu (aynı şema, tek fark üç boyut):
**1072 gerçek korpus sorusunda DEĞİŞEN: 0.** Route davranışı **birebir aynıydı**.

🔴 Sebep: korpus sorularını **katalogdan türetiyor**. Katalog büyüyünce üretilen soru
kümesi baştan sona kaydı — farklı sorular, farklı sınıflar. Toplam sayılar **iki farklı
popülasyondan** geliyordu.

⚠ Bu, `KAPI-DEFTERI`'nin ilk kaydının **ayna görüntüsüdür**: orada `gitas` düşünce payda
445→342 indi ve doğruluk **YÜKSELDİ** (sistem bozulurken sayı iyileşti). Burada sistem
**hiç değişmedi** ve sayı **kötüleşti**.

*Bir metriğin kıpırdaması, ölçtüğü şeyin kıpırdadığı anlamına gelmez.*
"""

import json

import pytest

from lab import gercek_dunya as gd


def _sonuc(sorular, sapan=()):
    """`kos()` çıktısının bu kapının dokunduğu yüzeyi.

    ⚠ **İki alan birden** gerekiyor ve bunu kapı bana öğretti: ilk fikstürüm yalnız
    `ayrinti` dolduruyordu ve `_ozet` sayıları `sayac`tan okuduğu için **payda 0**
    çıkıyordu — yani test, ölçmek istediği şeyin sıfır olduğu bir dünyada koşuyordu.
    *Bir fikstür, ölçülen yüzeyin tamamını taşımıyorsa yeşil verir ve hiçbir şey söylemez.*
    """
    sapanlar = dict(sapan)
    siniflar = [sapanlar.get(q, gd.DOGRU) for q in sorular]
    sayac = {"K1": {"toplam": len(sorular), "kabul": len(sorular)}}
    for c in siniflar:
        sayac["K1"][c] = sayac["K1"].get(c, 0) + 1
    return {"ayrinti": [{"soru": q, "sinif": c} for q, c in zip(sorular, siniflar)],
            "sayac": sayac}


def test_AYNI_SORU_KUMESI_AYNI_IMZA():
    """İmza soru kümesinin **kimliğidir**: sıra değişse bile aynı kalmalı, yoksa her
    koşum kendini farklı sanardı."""
    a = gd.nufus_imzasi(_sonuc(["a", "b", "c"]))
    b = gd.nufus_imzasi(_sonuc(["c", "a", "b"]))
    assert a == b


def test_TEK_SORU_EKLENMESI_IMZAYI_DEGISTIRIR():
    """🔴 Kapının kalbi: **bir** soru eklenmesi bile popülasyonu değiştirir ve toplam
    sayıları kıyaslanamaz yapar."""
    assert gd.nufus_imzasi(_sonuc(["a", "b"])) != gd.nufus_imzasi(_sonuc(["a", "b", "c"]))


def test_IMZA_SAYIYI_TASIR():
    """⊙ İmza okunabilir bir sayı taşır (`n:özet`) — bir insanın *«2286 → 2288»* diye
    okuyabilmesi, teşhisin yarısıdır."""
    assert gd.nufus_imzasi(_sonuc(["a", "b"])).startswith("2:")


def test_NUFUS_DEGISINCE_KAPI_KIYASLANAMAZ_DER_VE_YESIL_DEGILDIR(tmp_path, monkeypatch):
    """🔴🔴 **Kapının en önemli satırı, ve iki yönlü.**

    (1) Nüfus değişince **GERİLEME etiketi basılmaz** — o etiket bir davranış iddiasıdır
        ve burada davranış hakkında hiçbir şey bilinmiyor.
    (2) Ama kapı **yeşil de olmaz**: *«kıyaslayamıyorum»* bir geçiş sebebi değildir
        (`BILINMIYOR` dalının aynı dersi — `test_KAPI_kirmizi_VEREBILIR_dekor_degil`).
    """
    taban = tmp_path / "taban.json"
    monkeypatch.setattr(gd, "TABAN_YOLU", taban)
    eski = _sonuc(["a", "b", "c"])
    gd.kapi(eski, yaz=True)                                  # taban yazılır
    assert json.loads(taban.read_text())["_nufus"].startswith("3:")

    # 🔴 Popülasyon büyüdü (katalog büyüdü) ve sayılar kötüleşti — ama bu bir gerileme
    # DEĞİL, çünkü sorular artık başka sorular.
    kod, mesaj = gd.kapi(_sonuc(["a", "b", "c", "d"], sapan={"a": gd.SESSIZ_YANLIS}))
    assert kod != 0, "🔴 «kıyaslayamıyorum» bir geçiş sebebi olamaz"
    assert "KIYASLANAMAZ" in mesaj
    # ⚠ Yüklem **etiketi** arar, kelimeyi değil: mesajın kendisi *«bu bir GERİLEME
    # DEĞİL»* diyor ve kaba bir alt-dize araması onu **ihlal sanıyordu**. Bugün üçüncü
    # kez tekrarlayan sınıf (`import niyet` · `RAM-l` · bu) — ve `§101.1`'i içeriden
    # doğruluyor: *bir yanlış-pozitif yüklem HER SEFERİNDE yanlıştır.*
    assert "KAPI KIRMIZI — 🔴 GERİLEME" not in mesaj, \
        "🔴 davranış hakkında bilgi yokken gerileme ETİKETİ basılamaz"
    assert "popülasyon" in mesaj.lower()


def test_AYNI_NUFUSTA_GERILEME_HALA_YAKALANIR(tmp_path, monkeypatch):
    """⚠ **Kapı fazla ileri gitmemeli.** Nüfus aynıysa eski davranış birebir sürer —
    `sessiz_yanlis` artışı hâlâ kırmızıdır. *Bir yanlış-pozitifi kapatırken gerçek
    pozitifi kapatmak, kapıyı dekora çevirir.*"""
    taban = tmp_path / "taban.json"
    monkeypatch.setattr(gd, "TABAN_YOLU", taban)
    gd.kapi(_sonuc(["a", "b", "c"]), yaz=True)
    kod, mesaj = gd.kapi(_sonuc(["a", "b", "c"], sapan={"a": gd.SESSIZ_YANLIS}))
    assert kod != 0
    assert "KIYASLANAMAZ" not in mesaj, "aynı popülasyonda kıyas GEÇERLİDİR"


def test_ESKI_TABANDA_NUFUS_YOKSA_ESKI_YOL_SURER(tmp_path, monkeypatch):
    """⚠ Geriye dönük uyum: `_nufus` taşımayan bir taban (eski şema) kapıyı
    **kilitlemez** — o durumda eski karar yolu aynen çalışır. *Yeni bir alan, onu
    taşımayan geçmişi geçersiz kılmamalıdır.*"""
    taban = tmp_path / "taban.json"
    monkeypatch.setattr(gd, "TABAN_YOLU", taban)
    gd.kapi(_sonuc(["a", "b", "c"]), yaz=True)
    d = json.loads(taban.read_text())
    d.pop("_nufus")
    taban.write_text(json.dumps(d, ensure_ascii=False))
    kod, mesaj = gd.kapi(_sonuc(["a", "b", "c", "d"]))
    assert "KIYASLANAMAZ" not in mesaj


@pytest.mark.parametrize("sapan", [{}, {"a": gd.SESSIZ_YANLIS}, {"b": "devir"}])
def test_NUFUS_DEGISIMINDE_SORU_LISTESI_YINE_BASILIR(tmp_path, monkeypatch, sapan):
    """🔴 Kıyaslanamaz demek **susmak değildir**: hangi soruların değiştiği yine basılır,
    çünkü teşhis oradan yapılacak. *Bir ölçümün kıyaslanamaz olması, hiçbir şey
    söylemeyeceği anlamına gelmez.*"""
    taban = tmp_path / "taban.json"
    monkeypatch.setattr(gd, "TABAN_YOLU", taban)
    gd.kapi(_sonuc(["a", "b", "c"], sapan={"b": "devir"}), yaz=True)
    _kod, mesaj = gd.kapi(_sonuc(["a", "b", "c", "d"], sapan=sapan))
    assert "taban nüfus" in mesaj and "bugün nüfus" in mesaj


def test_NUFUSSUZ_TABANDA_ATILLIK_SOYLENIR(tmp_path, monkeypatch):
    """🔴🔴 **ATIL BİR KAPI, OLMAYAN BİR KAPIDIR — ve sessizce atıl olması en kötüsü.**

    `_nufus` taşımayan bir taban `A12`'yi hiç ateşlemez. Bu, `lab/kapi.py` yorumunda
    kayıtlı tuzağın aynısı: *«dört bileşenli bir kapının dörtte biri sessizce dekordu.»*

    ⊙ Çözüm boşluğu **doldurmak** değil — çevrimdışı yeniden hesaplanan bir imza
    gerçeğinden bir tık saparsa **her koşumda** yanlış-pozitif üretirdi — boşluğu
    **konuşturmak**. Ve not **yeşil** çıkışa da basılır: nüfus kontrolü atılken verilen
    bir yeşil, güvenilmez bir yeşildir.

    *Bir kapının neyi sınamadığını söylemesi, sınadıklarını saymasından önemlidir.*
    """
    taban = tmp_path / "taban.json"
    monkeypatch.setattr(gd, "TABAN_YOLU", taban)
    gd.kapi(_sonuc(["a", "b", "c"]), yaz=True)
    d = json.loads(taban.read_text())
    d.pop("_nufus")
    taban.write_text(json.dumps(d, ensure_ascii=False))

    kod, mesaj = gd.kapi(_sonuc(["a", "b", "c"]))          # değişmemiş → yeşil
    assert kod == 0
    assert "ATIL" in mesaj, "🔴 atıllık SESSİZ kaldı — dekor tuzağı"
    assert "--taban-yaz" in mesaj, "çıkış yolu da söylenmeli"
