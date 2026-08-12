"""TEST ORTAMININ KENDİ BÜTÜNLÜĞÜ — *aleti kim ölçüyor?*

Bu dosya ürünü sınamaz; **test ortamının kendisini** sınar. Gerekçesi ölçülmüş:
`belgeler/denetim/2026-08-05_TEST-ORTAMI-RAPORU.md §5` üç riski *"AÇIK"* diye işaretledi ve üçü de
aynı sınıftandı — **bir kural yazılmış ama onu koruyan kapı yok**.

> 🔴 *Bir denetim turunun bulduğu şey, kapıya çevrilmezse bir sonraki turda yeniden
> bulunur.* Bu deponun defterinde bu, en pahalı tekrar sınıfı: aynı kusuru üç kez
> bulmak, onu bir kez kapatmaktan üç kat pahalıdır.
"""

from __future__ import annotations

import pathlib

import yaml

_KOK = pathlib.Path(__file__).resolve().parents[1]
_PACKS = _KOK / "demo" / "packs"


def test_YETIM_CUBE_YOK_her_modul_bir_pakete_bagli():
    """🔴 **Ölçülmüş kusur** (`@bf5a7eb` öncesi): on yeni cube diskte duruyordu ama
    `pack.yml`'nin `moduller` listesinde olmadığı için **katalogda görünmüyordu**.
    Hiçbir soru onlara ulaşamıyordu ve **hiçbir test kırmızı vermiyordu**.

    Bu, `DENETIM-RAPORU §8`'in *«yetim modül»* sınıfının **veri katmanındaki** hâli:
    *bir cube yazmak onu bağlamak değildir.*

    ⚠ Kapı **iki yönlü değil**: bir modülün hiçbir sektörde kullanılmaması meşru
    olabilir (başka sektör için yazılmış). Yakalanan şey **tersi**: modül var,
    cube'u var, ama **hiçbir** pakette anılmıyor → kimse onu göremez.
    """
    modul_dizinleri = {d.name for d in (_PACKS / "modul").iterdir()
                       if d.is_dir() and (d / "cubes").is_dir()}
    anilan: set[str] = set()
    for pack in (_PACKS / "sektor").glob("*/pack.yml"):
        cfg = yaml.safe_load(pack.read_text(encoding="utf-8")) or {}
        anilan |= {str(m) for m in (cfg.get("moduller") or [])}
    yetim = sorted(modul_dizinleri - anilan)
    assert not yetim, (
        "🔴 YETİM MODÜL — cube'ları diskte var, hiçbir sektör paketinde anılmıyor, "
        f"yani katalogda GÖRÜNMEZ: {yetim}. "
        "`demo/packs/sektor/<sektör>/pack.yml` → `moduller` listesine ekle."
    )


def test_GENISLETME_yalniz_EKLER_mevcut_tabloya_dokunmaz():
    """⚠ `genisletme.py`'nin sözleşmesi: *"yalnız ekler; hiçbir mevcut tabloyu
    değiştirmez, silmez, yeniden üretmez"*.

    🔴 Bu söz **korpusun paydasını** koruyor: `nl_corpus`'un %93,1 tabanı mevcut 47
    tablonun üstünde duruyor. Genişletme bir mevcut tabloyu `DROP`/`ALTER` etseydi
    payda kayar ve **gerileme mi genişleme mi** olduğu ayırt edilemezdi.

    *Bir sözleşme, onu sınayan kapı olmadan bir niyet beyanıdır.*
    """
    src = (_KOK / "demo" / "genisletme.py").read_text(encoding="utf-8")
    yasak = [k for k in ("DROP TABLE", "ALTER TABLE", "DELETE FROM", "UPDATE ",
                         "TRUNCATE") if k in src.upper()]
    assert not yasak, f"🔴 genişletme mevcut veriye dokunuyor: {yasak}"
    # Yalnız `CREATE OR REPLACE` ile YENİ tablolar kurulmalı; adları da mevcut 47'nin
    # dışında olmalı. ⚠ Ad çakışması sessizce eski tabloyu ezerdi.
    import re
    yeni = set(re.findall(r'CREATE OR REPLACE TABLE (\w+)', src)) | \
        set(re.findall(r'_yaz\(con, "(\w+)"', src))
    mevcut = set(re.findall(r'CREATE TABLE (\w+)',
                            (_KOK / "demo" / "build_data.py").read_text(encoding="utf-8")))
    cakisan = sorted(yeni & mevcut)
    assert not cakisan, f"🔴 genişletme mevcut bir tabloyu EZİYOR: {cakisan}"


def test_KAYNAK_DAGILIMI_tek_kaynak_hakim_olmaz():
    """⚠ **Sözlük yanlılığı** — literatürde ölçülmüş sınıf, bizde de var.

    Elle yazılan vakaların çoğunun `kaynak`'ı aynı belgeyse, *korpusu yazan akıl ile
    kataloğu yazan akıl aynıdır* ve ölçüm kendi kendini doğrular.

    > 🔴 Yasak koymak yanlılığı **kaldırmaz**, yalnız **kaynağını değiştirir.**
    > Birincil kaynak canlı gözlem olmalı: `deneyim.py` · `REAL_PHRASINGS` ·
    > borç defterinin canlı bulguları.

    Eşik **%55**: tek bir kaynak vakaların yarısından fazlasını veriyorsa korpus o
    kaynağın bakış açısını ölçüyor demektir.
    """
    from collections import Counter

    from lab.gercek_dunya import VAKALAR

    aileler = Counter()
    for v in VAKALAR:
        k = str(v["kaynak"])
        aile = ("deneyim" if "deneyim" in k else
                "REAL_PHRASINGS" if "PHRASINGS" in k else
                "borç defteri" if "borç" in k else
                "nl_corpus" if "nl_corpus" in k else
                "§9.6/§9.7" if "§9" in k else "diğer")
        aileler[aile] += 1
    toplam = sum(aileler.values())
    en_buyuk, adet = aileler.most_common(1)[0]
    oran = 100 * adet / toplam
    assert oran <= 55, (
        f"🔴 kaynak yanlılığı: «{en_buyuk}» vakaların %{oran:.0f}'ini veriyor "
        f"({adet}/{toplam}) — dağılım: {dict(aileler)}"
    )


def test_RAPOR_CIKTISI_gitignore_yuzunden_kaybolmaz():
    """⚠ `lab/reports/` `.gitignore`'da: ölçüm çıktısı **yerel**. CI'da koşsa bile
    sonuç kaybolur ve başka bir makinede *"taban neydi"* sorusu cevapsız kalır.

    🔴 Çözüm raporu commit'lemek DEĞİL (her koşumda değişen bir dosya diff'i
    gürültüye boğar) — **tabanı** commit'lemek. Taban küçük, anlamlı ve
    kıyaslanabilir; rapor ise türevi.

    *Kaybolan bir ölçüm, alınmamış bir ölçümdür.*
    """
    gi = (_KOK / ".gitignore").read_text(encoding="utf-8")
    assert "lab/reports" in gi, "beklenti değişmiş — bu testin gerekçesi güncellensin"
    # Taban `lab/` altında ve `reports/` DIŞINDA olmalı ki commit'lenebilsin.
    from lab.gercek_dunya import TABAN_YOLU
    assert "reports" not in str(TABAN_YOLU), \
        "🔴 taban dosyası gitignore'lu dizinde — commit'lenemez, gerileme görülemez"
    assert TABAN_YOLU.parent.name == "lab"


def test_KAPI_kirmizi_VEREBILIR_dekor_degil():
    """🔴 **`konusma_senaryolari` tuzağı** — `lab/kapi.py` kendi yorumunda kayıtlı:
    o adım bayraksız koşumda **her yolda `0`** döndüğü için *"dört bileşenli bir
    kapının dörtte biri sessizce dekordu"*.

    *Kırmızı veremeyen bir kapı, kapı değildir.* Bu test `kapi()`'nin gerçekten
    sıfırdan farklı dönebildiğini **çağırarak** kanıtlar — kaynağı okuyarak değil.
    """
    import json
    import tempfile

    from lab import gercek_dunya as G

    with tempfile.TemporaryDirectory() as d:
        eski = G.TABAN_YOLU
        try:
            G.TABAN_YOLU = pathlib.Path(d) / "taban.json"
            G.TABAN_YOLU.write_text(json.dumps(
                {"vaka": 100, "kabul": 50, "dogru": 20, "sessiz_yanlis": 0}))
            # Gerileme senaryosu: kabul ve doğru düşmüş, sessiz-yanlış artmış.
            kod, mesaj = G.kapi({"sayac": {"K1": {
                "toplam": 100, "kabul": 10, G.DOGRU: 2, G.SESSIZ_YANLIS: 7}}})
            assert kod == 1, "🔴 gerileme varken kapı yeşil verdi — DEKOR"
            assert "kabul" in mesaj and "sessiz_yanlis" in mesaj
            # Gerileme yoksa yeşil.
            kod2, _ = G.kapi({"sayac": {"K1": {
                "toplam": 100, "kabul": 60, G.DOGRU: 25, G.SESSIZ_YANLIS: 0}}})
            assert kod2 == 0, "gerileme yokken kırmızı verdi"
        finally:
            G.TABAN_YOLU = eski


def test_TABAN_yazildiginda_COMMIT_uyarisi_verir():
    """🔴 **Dekor tuzağının ikinci kılığı** — kapının kendisinden daha sinsi.

    Taban dosyası commit edilmezse her koşum onu yeniden yazar ve kıyaslama her
    seferinde **kendisiyle** yapılır: kapı hiçbir zaman kırmızı veremez ama yeşil
    görünür. *Kendi yazdığı tabanla kıyaslanan bir kapı, aynadaki kendine bakıp
    "değişmemiş" diyen bir ölçümdür.*

    Dosyanın **var olması** yetmez; paylaşılıyor olması gerekir — ve bunu kullanıcıya
    söyleyen tek şey bu uyarıdır."""
    import json
    import tempfile

    from lab import gercek_dunya as G

    with tempfile.TemporaryDirectory() as d:
        eski = G.TABAN_YOLU
        try:
            G.TABAN_YOLU = pathlib.Path(d) / "yok.json"
            kod, mesaj = G.kapi({"sayac": {"K1": {"toplam": 5, "kabul": 3, G.DOGRU: 1}}})
            assert kod == 0, "ilk koşum taban yazmalı, kırmızı vermemeli"
            assert "COMMIT ET" in mesaj, "🔴 commit uyarısı yok — sessiz dekor riski"
            assert json.loads(G.TABAN_YOLU.read_text())["kabul"] == 3
        finally:
            G.TABAN_YOLU = eski


def test_TABAN_yolu_gitignore_disinda():
    """Taban `lab/` altında ve `lab/reports/` DIŞINDA olmalı ki commit'lenebilsin.
    ⚠ `.gitignore` `lab/data/` · `lab/backups/` · `lab/reports/` · `lab/generated/*.jsonl`
    yok sayıyor; taban bunların hiçbirinde değil."""
    from lab.gercek_dunya import TABAN_YOLU

    gi = (_KOK / ".gitignore").read_text(encoding="utf-8")
    yasakli = [x.strip() for x in gi.splitlines()
               if x.strip().startswith("lab/") and not x.strip().startswith("#")]
    yol = f"lab/{TABAN_YOLU.name}"
    carpisan = [y for y in yasakli if yol.startswith(y.rstrip("*").rstrip("/"))
                and y.rstrip("*").rstrip("/") != "lab"]
    assert not carpisan, f"🔴 taban gitignore'lu yolda: {carpisan} — commit edilemez"

def test_KAPI_KAYBETTIGI_KAPSAMI_BILDIRIR():
    """🔴🔴 **BİR KAPIYI SUSTURMAK DÜRÜSTLÜKTÜR; SUSMAYI DUYURMAMAK KAPSAM KIRPMAKTIR.**

    ## Ölçülen kusur (2026-08-12) — bir denetim ajanı buldu

        belgeler BAĞLI DEĞİL  → 11 skipped in 0.12s
        belgeler BAĞLI        → 11 passed in 4.85s

    Ve **hiçbir belgeli reçete** `-v "$PWD/belgeler:/belgeler:ro"` içermiyordu. Yani
    *«yayınlanmış bir sayı çürümesin»* diye kurulan iki kapı — `§F8` doğruluk yayını ve
    `§0.6` karne manşeti — **hiç koşmuyordu**; `pytest` bunu `skipped` diye, yani **iyi
    haber gibi** raporluyordu.

    ⊙ `§F8` hijyeni *«kapı, ortam eksiğini ürün kusuru gibi göstermemeli»* diyordu ve
    doğruydu — ama **yarısıydı**. Öteki yarısı: **koşucu o eksiği sessizce yutmamalı.**

    ## Bu kapı ne ölçer

    `lab/kapi.py` kaybettiği kapsamı **adıyla** bildiriyor mu. Koşumu düşürmez (yerel
    geliştirici `belgeler` olmadan da koşabilmeli) — yalnız *«yeşil özet, o kapıların
    koştuğu anlamına gelmez»* der.

    ⚠ Yüklem **gövdeye** kurulu: bildirim fonksiyonu ÇAĞRILIYOR mu (`ast`), ve listesi
    gerçekten `belgeler`e bağımlı dosyaları mı sayıyor.
    """
    import ast

    kaynak = (_KOK / "lab" / "kapi.py").read_text(encoding="utf-8")
    agac = ast.parse(kaynak)

    # ① Bildirim fonksiyonu var ve ÇAĞRILIYOR (yazılıp çağrılmayan bir bildirim yoktur).
    # ⚠ **KAÇ ÇIKIŞTA çağrıldığını SAY** — bu oturumun taze dersi (`«tek boğaz»`
    # iddiası bir ikinci `llm.repair` yüzünden çürümüştü). `lab/kapi.py`'nin **iki**
    # çıkışı var: `hizli()` kendi özetini basıp dönüyor, `--tam`/`--hepsi` ise
    # `FAZ KAPISI ÖZETİ` bloğunu. İlk yazımda bildirim yalnız ikincisindeydi ve hızlı
    # koşumda **34 test atlanırken** özet yine yeşildi.
    #
    # *İki çıkışı olan bir koşucuda, tek çıkışa konan bir bildirim yarım bir bildirimdir.*
    bildiren = {fn.name for fn in ast.walk(agac)
                if isinstance(fn, ast.FunctionDef)
                and any(isinstance(n, ast.Call) and getattr(n.func, "id", "")
                        == "_belgeler_bildirimi" for n in ast.walk(fn))}
    assert "hizli" in bildiren, (
        "🔴 `--hizli` yolu kaybettiği kapsamı BİLDİRMİYOR — o yol kendi çıkışını "
        "kullanıyor ve ölçüldü: 34 test atlanırken özet yeşil görünüyordu.")
    assert len(bildiren) >= 2, (
        f"🔴 bildirim yalnız {sorted(bildiren)} içinde — `lab/kapi.py`'nin İKİ çıkışı "
        "var (`hizli` ve tam-kapı özeti); ikisi de bildirmeli.")

    # ② Liste GERÇEKTEN `belgeler`e bağımlı dosyaları sayıyor mu — boş yeşil avı.
    from lab.kapi import BELGELERE_BAGLI_KAPILAR

    assert BELGELERE_BAGLI_KAPILAR, "⊘ liste boş — bildirim hiçbir şey söylemez"
    for ad in BELGELERE_BAGLI_KAPILAR:
        f = _KOK / "tests" / ad
        assert f.is_file(), f"bildirimde olmayan dosya: {ad}"
        icerik = f.read_text(encoding="utf-8")
        assert "skipif" in icerik and "belgeler" in icerik, (
            f"🔴 `{ad}` bildirimde ama `belgeler` yokluğunda ATLAMIYOR — liste bayat. "
            "Bir bildirimi, bildirdiği şey doğru değilken taşımak gürültüdür.")
