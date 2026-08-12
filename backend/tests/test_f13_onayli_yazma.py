"""🔴 `§F13` — *«AGENTIC'İN ASIL KİLİDİ»*: NE **VAR**, NE **YOK** — ölçüldü.

## Kartın iddiası

> Bugün `_yazma_araclari` **bilerek** `llm_araclari` dışında — *«ajan YAZAMAZ»*. Sonuç:
> *«bunu panoya ekle»* · *«her pazartesi yolla»* **yapılamıyor**. ⊙ Yasak **kaldırılmaz,
> KADEMELENDİRİLİR** — ajan yazma aracını **öneri** olarak üretir → kullanıcı **onaylar**
> → `authorize()` + audit (**ikisi de zaten var**) → çalışır.

## Ölçüm (2026-08-12) — ONAY ALTYAPISI ZATEN CANLI

| parça | durum |
|---|---|
| `app/onay_akisi.py` (**289 satır**) | ✅ durumlar · risk kademeleri (`dusuk`/`orta`/`geri_alinamaz`) · bilet ömrü · **yasak argüman** listesi (parola/token…) |
| `app/yazma_araclari.py` | ✅ *«Yalnız `onay_akisi` üzerinden çağrılabilir — doğrudan çağrı, onayı bir **süs** yapardı»* |
| `POST /ask/eylem` | ✅ canlı uç; `onay_akisi.bilet_dogrula` çağırıyor |
| `schemas.py` bilet alanı | ✅ **fail-closed** varsayılan (`""`) |
| `authorize()` + audit | ✅ ikisi de var (kartın kendi tespiti) |

🔴 **VE BAYRAĞIN ADI YANILTIYOR — kartı okuyanın düşeceği tuzak.** `onay_akisi: "off"`
bir *«onay akışı kapalı»* **değildir**; bayrağın kendi açıklaması tersini söylüyor:

> *«D9: kapsam **İÇİ** ve **GERİ ALINABİLİR** bir eylem **İSTEMSİZ** koşar… ⚠ YAZMA
> YÜZEYİ BÜYÜMEZ: ajan hâlâ yazma aracı **ÇAĞIRMIYOR**; değişen tek şey kullanıcının
> **KENDİ** eyleminin kaç tıkla tamamlandığı.»*

Yani bayrak **istem kaldırır**, onay eklemez. Kapalıyken davranış *«her yazmaya istem»* —
yani **daha muhafazakâr** olan. *Bir bayrağın adı, ne yaptığının kanıtı değildir.*

## 🔴 GERÇEKTEN EKSİK OLAN TEK ŞEY

Ajanın bir yazma aracını **öneri olarak üretmesi**: `tools.KAYIT`'ta `yan_etki="yazar"`
araç **yok** (`§C3`'te ölçüldü: `{'yok': 25}`), dolayısıyla planlayıcı onu **seçemez**.
Zincirin *«kullanıcı onaylar → çalışır»* yarısı **kurulu**; *«ajan önerir»* yarısı **yok**.

⊙ Bu bir **kablolama** değil bir **karar** işidir: kayda bir `yazar` araç girdiği an
`§C3`'ün MCP kapısı da kırmızıya döner (orası *«yazma aracı yok»*u bir açılış şartı
sayıyor). İkisi **aynı kararın iki yüzü** ve birlikte verilmeli.

*Bir kilidin iki yarısından biri kuruluysa, eksik olan yarı değil KARARDIR.*
"""

from __future__ import annotations

import pathlib

import yaml

from app import onay_akisi, tools

_APP = pathlib.Path(__file__).parent.parent / "app"
_PACK = pathlib.Path(__file__).parent.parent / "demo" / "packs" / "features.yml"


def _bayrak(ad: str) -> str:
    d = yaml.safe_load(_PACK.read_text(encoding="utf-8")) or {}
    for blok in (d.values() if isinstance(d, dict) else []):
        if isinstance(blok, dict) and ad in blok:
            return str(blok[ad])
    return ""


# --- KURULU YARI: kilitlenir, sessizce kaybolamaz --------------------------------

def test_ONAY_AKISI_kurulu():
    """Risk kademeleri + durum makinesi + bilet — kartın *«zaten var»* dediği yarı."""
    assert onay_akisi.DURUMLAR
    assert {onay_akisi.RISK_DUSUK, onay_akisi.RISK_ORTA,
            onay_akisi.RISK_GERI_ALINAMAZ} <= set(dir(onay_akisi)) | {
        onay_akisi.RISK_DUSUK, onay_akisi.RISK_ORTA, onay_akisi.RISK_GERI_ALINAMAZ}
    assert hasattr(onay_akisi, "bilet_dogrula")


def test_YASAK_ARGUMAN_listesi_SIR_kacirmiyor():
    """Onay biletine parola/token yazılamaz — *bir onay ekranı, sırrı gösterdiği anda
    bir sızıntı yüzeyi olur.*"""
    y = {a.lower() for a in onay_akisi.YASAK_ARGUMAN}
    assert {"password", "token"} <= y


def test_YAZMA_ARACLARI_yalniz_ONAYDAN_gecer():
    """`yazma_araclari`'nın kendi sözleşmesi: doğrudan çağrı onayı bir **süs** yapardı."""
    src = (_APP / "yazma_araclari.py").read_text(encoding="utf-8")
    assert "onay_akisi" in src


def test_EYLEM_UCU_bileti_DOGRULUYOR():
    """`/ask/eylem` biletsiz çalışmaz; şema varsayılanı **fail-closed** (`\"\"`)."""
    e = (_APP / "routers" / "eylem.py").read_text(encoding="utf-8")
    assert "bilet_dogrula" in e and "OnayHatasi" in e


# --- BAYRAĞIN ADI YANILTIYOR: kayda geçiyor --------------------------------------

def test_ONAY_AKISI_BAYRAGI_ONAY_EKLEMEZ_ISTEM_KALDIRIR():
    """🔴 Kartı okuyanın düşeceği tuzak. `off` **daha muhafazakâr** olandır; bayrak
    açılınca *kapsam içi ve geri alınabilir* eylemler istemsiz koşar."""
    from app.features import FLAG_REGISTRY
    aciklama = (FLAG_REGISTRY.get("onay_akisi") or {}).get("description", "")
    assert "İSTEMSİZ" in aciklama or "istemsiz" in aciklama
    assert "YAZMA YÜZEYİ BÜYÜMEZ" in aciklama, (
        "bayrağın kendi sınırı silinmiş — adı yaptığını anlatmıyor")
    assert _bayrak("onay_akisi") == "off"


# --- EKSİK YARI: karar verilmeden yazılamaz --------------------------------------

def test_YAZMA_ARACI_ONAYSIZ_KOSAMAZ():
    """🔴 ⟳ **F13'ün EKSİK YARISI KAPANDI (2026-08-12) — ve ölçüm iddiayı düzeltti.**

    Borç şöyle yazılmıştı: *«ajan yazma aracını öneri olarak üretsin — `tools.KAYIT`'ta
    `yan_etki="yazar"` araç YOK»*. Ölçüm bunu **çürüttü**:

    | iddia | ölçülen |
    |---|---|
    | kayıtta `yazar` araç yok | ⊘ **`app/yazma_araclari.py` ZATEN VAR** — üç araç, `YAZMA_KAYIT` |
    | ajan öneremiyor | ⊘ `tools.py:643` **`KAYIT = KAYIT + … + _yazma_araclari()`** — tam bağlı |
    | eksik olan kablolama | 🔴 eksik olan **BAYRAK DEĞİL, KAPI** |

    ⊙ *«Yazılmış ama bağlanmamış»* değil — **yazılmış, bağlanmış, korunmamış.**

    ## 🔴 Asıl bulgu: değişmez DÜZYAZIYDI

    `yazma_araclari.py` *«yalnız `onay_akisi` üzerinden çağrılabilir»* diye ilan
    ediyordu ve bunu üç aracın `notlar` alanına da yazıyordu. Ölçüldü:
    `Planlayici.calistir()`'in dört kapısında `yan_etki` · `onay` · `bilet`
    kelimelerinin **hiçbiri geçmiyordu**.

    ## ⚠ Ve boşluğu GİZLEYEN şey ikinci bir kusurdu

    Neden hiç fark edilmedi? Çünkü araçlar **zaten çalışmıyordu**: ilan edilen `girdi`
    (`title`·`cube_query`) gerçek imzayla (`request`·`did`·`body`·`session`) tutmuyor
    ve çağrı `TypeError` veriyor. Bugünkü güvenlik bir kapı değil bir **uyumsuzluktu**
    — ve bir `TypeError` bir **red değildir**: gerekçe söylemez, denetim kaydına
    geçmez, ve uyumsuzluk bir gün giderilirse **sessizce yazmaya döner**.

    ✅ Beşinci kapı: `Planlayici._onay_kapisi` — `yan_etki != "yok"` ise geçerli bir
    **onay bileti** şart, yoksa `AracReddi`. Fail-closed: `onay_biletleri` varsayılan
    olarak **boş**tur, yani bir planlayıcıyı elle kurmak yazma yetkisi vermez.
    """
    from app.planner import AracReddi, Planlayici
    from tests.kapi_ortak import yazma_araclari_acik

    with yazma_araclari_acik() as tools:
        yazanlar = [a for a in tools.KAYIT if a.yan_etki != "yok"]
        assert yazanlar, (
            "⊘ ölçüm tabanı çöktü: bayrak açıkken bile kayıtta yazan araç yok — bu test "
            "o hâlde hiçbir şey ölçmüyor demektir.")

        p = Planlayici(kaynaklar={})
        try:
            p.calistir(yazanlar[0].ad, title="x")
        except AracReddi as red:
            assert "ONAY" in str(red).upper(), (
                f"red DÜRÜST değil — gerekçesi yazılmamış: {red}")
        except TypeError as exc:                              # pragma: no cover
            raise AssertionError(
                "🔴 ONAY KAPISI ÇALIŞMADI: çağrı araca kadar gitti ve `TypeError` ile "
                f"düştü ({exc}). Bir `TypeError` bir red değildir — bugün yazmıyorsa "
                "bunun sebebi bir kapı değil, bir imza uyumsuzluğudur.") from exc
        else:                                                 # pragma: no cover
            raise AssertionError(
                f"🔴 {yazanlar[0].ad} ONAYSIZ KOŞTU — `F13`'ün tek değişmezi çiğnendi.")


def test_ONAY_KAPISI_DORDUN_YANINDA_BESINCI():
    """Kapı **kod yolunda**, bir yorumda değil: `calistir()` onu gerçekten çağırmalı."""
    import inspect

    from app.planner import Planlayici

    src = inspect.getsource(Planlayici.calistir)
    assert "_onay_kapisi" in src, (
        "🔴 onay kapısı `calistir()` yolunda DEĞİL — yazılmış ama çağrılmayan bir kapı, "
        "yazılmamış bir kapıdır (bu oturumda ölçülen en sık kusur sınıfı).")


def test_YAZMA_ARACLARININ_GIRDI_BEYANI_HALA_UYUMSUZ():
    """⊘ **AÇIK KALAN YARIM — ve kapatılmadığı KAYITLI.**

    Üç yazma aracının ilan ettiği `girdi`, işaret ettiği fonksiyonun imzasıyla
    tutmuyor (`add_widget(request, did, body, session)`). Yani araçlar bugün **onay
    bileti verilse bile** koşamaz.

    🔴 ⟳ **KÖK NEDEN ÖLÇÜLDÜ (2026-08-12) — ve «adaptör yaz» YANLIŞ TEŞHİSTİ.**

    İlk kayıt *«aradaki adaptör `FAZ H`'nin işidir»* diyordu. Ölçüm başka bir şey
    gösterdi: **adaptör zaten var**, yalnız araç kaydı ona bağlı değil.

        EYLEM_KAYIT (çalışan onay yolu, `/ask/eylem`)
            pano.ekle · tercih.kaydet · zamanla.olustur      ← alanları: ad·izin·**uc**·…
        YAZMA_KAYIT (ajanın araç kaydı)
            dashboards.create · measures.approve · schedules.create
        AD ÖRTÜŞMESİ: **SIFIR**

    ⊙ `EylemBeyani.uc` tam olarak *«bu eylem hangi uçtan koşar»*ı taşıyor — yani
    aranan adaptör odur. `YAZMA_KAYIT` ise `modul`+`fonksiyon` ile **FastAPI rota
    işleyicisine** işaret ediyor (`add_widget(request, did, body, session)`) ve o
    imza `Depends`/`Request` istediği için hiçbir zaman doğrudan çağrılamaz.

    🔴 Ve iki kayıt **aynı kümeyi bile kapsamıyor**: `measures.approve`'ın eylem
    karşılığı yok, `tercih.kaydet`'in araç karşılığı yok. İkisi ayrı ayrı büyüyor.

    ⚠ Bu, `§C1`'in (fiil kaydı ↔ araç kaydı, örtüşme **sıfır**) **ikinci vakasıdır** —
    aynı desen, bu kez yazma tarafında. *Bir ilkenin (KAT-1) ihlali bir kez ölçülünce,
    ikinci vakası aranmalıdır; çünkü sınıfı olan bir kusurun tek örneği olmaz.*

    ⊙ **Doğru iş** artık adıyla yazılı: yeni bir adaptör katmanı DEĞİL, `YAZMA_KAYIT`'ı
    `EYLEM_KAYIT`'a **bağlamak** (araç `uc`u beyan etsin ya da doğrudan eylem adını
    taşısın) — ve `KURAL B`: bugünkü `/ask/eylem` davranışı bayt bayt aynı kalmalı.

    Bu test onu **gizlemiyor**: uyumsuzluk giderildiği gün kırılır ve o gün onay
    kapısının gerçekten tek koruma olduğu hatırlanır.

    *Bir eksiği bir testle kaydetmek, onu yapmak değildir — ama sessizce bırakmaktan
    farkı, bir gün mutlaka konuşacak olmasıdır.*
    """
    import inspect

    from tests.kapi_ortak import yazma_araclari_acik

    with yazma_araclari_acik():
        from app.yazma_araclari import YAZMA_KAYIT
        uyumsuz = []
        for a in YAZMA_KAYIT:
            try:
                fn = a.cagir(None)
                params = set(inspect.signature(fn).parameters)
            except Exception:                                 # noqa: BLE001
                continue
            if not set(a.girdi) <= params:
                uyumsuz.append(a.ad)
        assert uyumsuz, (
            "✅ Yazma araçlarının `girdi` beyanı artık gerçek imzayla UYUMLU — yani "
            "araçlar gerçekten çağrılabilir hâle gelmiş. O hâlde tek koruma "
            "`_onay_kapisi`dir: `FAZ H` adaptörleriyle birlikte onay akışının uçtan uca "
            "canlı olduğunu doğrulayın ve bu kaydı GÜNCELLEYİN.")

# --- ⟳ ARAÇ ↔ EYLEM BAĞLAMASI (2026-08-12) — `§C1`'in ikinci vakası kapandı ---------

def test_HER_YAZMA_ARACININ_ONAY_YOLU_VAR():
    """🔴 **Onay yolu olmayan bir öneri, bir öneri değil bir çıkmazdır.**

    Ajan bir yazma aracı önerebiliyorsa, kullanıcı onu **onaylayabilmelidir**.
    `/ask/eylem` kaydı (`EYLEM_KAYIT`) fail-closed'dır: kayıtta olmayan bir eylem
    **400** döner. Yani araç kaydında olup eylem kaydında olmayan bir kalem, kullanıcıyı
    onaylayamayacağı bir öneriyle baş başa bırakırdı.

    ⊙ Ölçüldü (2026-08-12): `measures.approve` tam olarak buydu → **kayıttan çıkarıldı**,
    gerekçesi `yazma_araclari.py`'de yazılı.
    """
    from app import eylem as _e
    from tests.kapi_ortak import yazma_araclari_acik

    with yazma_araclari_acik() as tools:
        from app.yazma_araclari import ARAC_EYLEM

        yazanlar = {a.ad for a in tools.KAYIT if a.yan_etki != "yok"}
        assert yazanlar, "⊘ ölçüm tabanı çöktü: bayrak açıkken yazan araç yok"
        eksik = sorted(yazanlar - set(ARAC_EYLEM))
        assert not eksik, (
            f"🔴 onay yolu OLMAYAN yazma aracı: {eksik}. Ya `ARAC_EYLEM`'e bir eylem "
            "bağla ya kayıttan çıkar — üçüncü seçenek, kullanıcının onaylayamayacağı "
            "bir öneridir.")
        for arac_adi, eylem_adi in ARAC_EYLEM.items():
            _e.beyan(eylem_adi)          # fail-closed: yoksa KeyError


def test_TURETILEN_ALANLAR_EYLEMLE_BAYT_BAYT_AYNI():
    """🔴 `KAT-1` — `izin`/`modul`/`fonksiyon`ın **tek sahibi** `app/eylem.py`.

    Bu üç alan önce iki yerde ayrı ayrı yazılıydı ve bugün **tutarlıydılar**; ama iki
    sahip ayrışır. Türetme sonrası değerler elle yazılmış hâlleriyle **birebir aynı**
    çıkıyor (ölçüldü: `query:run` · `app.routers.dashboards` · `add_widget`) — yani
    `KURAL B`: davranış değişmedi, **sahip** değişti.
    """
    from app import eylem as _e
    from tests.kapi_ortak import yazma_araclari_acik

    with yazma_araclari_acik() as tools:
        from app.yazma_araclari import ARAC_EYLEM

        for a in tools.KAYIT:
            if a.yan_etki == "yok":
                continue
            b = _e.beyan(ARAC_EYLEM[a.ad])
            modul, _, fonksiyon = b.uc.rpartition(".")
            assert a.izin == b.izin, f"{a.ad}: izin ayrıştı ({a.izin} ≠ {b.izin})"
            assert a.modul == f"app.routers.{modul}", f"{a.ad}: modül ayrıştı"
            assert a.fonksiyon == fonksiyon, f"{a.ad}: fonksiyon ayrıştı"


def test_GERI_ALINABILIRLIK_iki_kayitta_CELISMEZ():
    """`geri_alinabilir` (eylem, bool) ↔ `geri_alma_ref` (araç, yol) **aynı olgudur**.

    ⚠ Türetilmedi çünkü araç tarafı **daha fazlasını** taşıyor (geri alma YOLU); ama
    çelişmeleri bir kapıyla yasak. *İki kodlamayı birleştiremiyorsan, en azından
    ayrışmalarını duyulur yap.*
    """
    from app import eylem as _e
    from tests.kapi_ortak import yazma_araclari_acik

    with yazma_araclari_acik() as tools:
        from app.yazma_araclari import ARAC_EYLEM

        for a in tools.KAYIT:
            if a.yan_etki == "yok":
                continue
            b = _e.beyan(ARAC_EYLEM[a.ad])
            assert bool(a.geri_alma_ref) == b.geri_alinabilir, (
                f"{a.ad}: geri alınabilirlik ÇELİŞİYOR — araç "
                f"{a.geri_alma_ref!r}, eylem {b.geri_alinabilir}")


def test_IMPORT_SIRASI_DAIRESEL_DEGIL():
    """⚠ Ölçüldü: bayrak açıkken `yazma_araclari`'yı `tools`'tan **önce** almak
    `ImportError: partially initialized` veriyordu. Uygulama yolunda `tools` önce
    geldiği için görünmüyordu.

    *Yalnız bir sıralama sayesinde çalışan bir şey, çalışmıyor demektir; henüz sırası
    gelmemiştir.*
    """
    import subprocess
    import sys

    kod = ("from app.yazma_araclari import YAZMA_KAYIT\n"
           "from app import tools\n"
           "assert len(YAZMA_KAYIT) >= 1 and len(tools.KAYIT) > len(YAZMA_KAYIT)\n")
    r = subprocess.run([sys.executable, "-c", kod], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "DIMA_YAZMA_ARACLARI": "on",
                            "DIMA_VQR_EMBEDDER": "off", "PYTHONPATH": "/app"},
                       cwd="/app")
    assert r.returncode == 0, (
        "🔴 dairesel import geri geldi (`yazma_araclari` önce):\n" + r.stderr[-600:])


def test_KURAL_B_bayrak_kapaliyken_KAYIT_DEGISMEDI():
    """Bağlama bir **sahip** değişikliğidir, bir davranış değişikliği değil."""
    from app import tools

    assert all(a.yan_etki == "yok" for a in tools.KAYIT), (
        "bayrak kapalıyken kayda yazan araç girmiş — `KURAL B` ihlali")
