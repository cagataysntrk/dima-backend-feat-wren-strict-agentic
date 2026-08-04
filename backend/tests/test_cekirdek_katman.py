"""FAZ 2.1 — **ÇEKİRDEK KATMAN + GRAIN SÖZLEŞMESİ** kapısı (adım *a*: sözlük birleştirme).

Ölçülen kusur: `ticaret` cube'u **üç ERP'de** aynı adı, aynı sinonimi ve aynı ölçü adını
(`satis_tutari`) taşıyor ama **farklı grain**'de — mikro `stok_hareketleri`, logo/netsis
`faturalar`. *"Bu yıl satış"* üç şirkette **karşılaştırılamaz üç sayı** döndürüyor ve
**hiçbir yerde beyan yok**. *Aynı adı taşıyan iki sayının farklı şeyler olduğunu
söylemeyen bir semantik katman, semantik katman değildir.*
"""

from __future__ import annotations

import ast
import pathlib
import tempfile

import pytest
import yaml

from app import cekirdek

KOK = pathlib.Path(__file__).resolve().parents[1]
DEMO = KOK / "demo"
SOZLUK = cekirdek.sozluk_yukle(DEMO)


# ── 1 · KURAL B — bayrak KAPALIYKEN çıktı BİREBİR ───────────────────────────

def test_KAPALIYKEN_HICBIR_SEY_YAPMIYOR(monkeypatch):
    """🔴 **KURAL B.** Kapalı bir bayrak *"biraz"* çalışamaz: geri alma ancak çıktı
    **birebir** aynıysa gerçek bir geri almadır."""
    monkeypatch.setattr(cekirdek, "kademe", lambda: "off")
    meta = {"name": "t", "base_object": "faturalar",
            "measures": [{"name": "satis_tutari", "expression": "SUM(X)"}]}
    from app.compose import _merge_cube_metadata

    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td)
        (out / "cubes" / "t").mkdir(parents=True)
        yol = out / "cubes" / "t" / "metadata.yml"
        yol.write_text(yaml.safe_dump(meta), encoding="utf-8")
        once = yol.read_bytes()
        _merge_cube_metadata(DEMO, out)
        assert yol.read_bytes() == once, "bayrak KAPALI ama dosya DEĞİŞMİŞ"


def test_VARSAYILAN_OFF():
    """Varsayılan `shadow` bile değil `off`: bu madde **derleme çıktısını** değiştirir ve
    bir derleme hatası **tüm tenant'ı** düşürür (`compose` fail-closed)."""
    from app.config import Settings

    assert Settings.model_fields["cekirdek_katman"].default == "off"


def test_KADEMELER_MOTOR_RLS_ILE_AYNI():
    """İkinci bir kademe sözlüğü yazmak, iki mekanizmanın **ayrışması** demekti."""
    from app import rls

    assert cekirdek.KADEMELER == rls.KADEMELER


# ── 2 · GÖLGE YAZMAZ ────────────────────────────────────────────────────────

def test_SHADOW_YAZMIYOR(monkeypatch):
    """🔴 **Yazan bir gölge, gölge değildir.** FAZ 1.1'de birebir bu kusur ölçüldü:
    `motor_rls` gölgesi manifeste RLAC yazıyordu ve *"shadow"* adı altında **servis edilen
    cevabı** değiştirecekti."""
    monkeypatch.setattr(cekirdek, "kademe", lambda: "shadow")
    from app.compose import _merge_cube_metadata

    meta = {"name": "t", "base_object": "faturalar",
            "measures": [{"name": "satis_tutari", "expression": "SUM(X)"}]}
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td)
        (out / "cubes" / "t").mkdir(parents=True)
        yol = out / "cubes" / "t" / "metadata.yml"
        yol.write_text(yaml.safe_dump(meta), encoding="utf-8")
        once = yol.read_bytes()
        _merge_cube_metadata(DEMO, out)
        assert yol.read_bytes() == once, "GÖLGE YAZMIŞ — gölge değil, sessiz bir uygulama"


# ── 3 · SÖZLÜK ile İFADE AYRI ───────────────────────────────────────────────

def test_IFADEYE_DOKUNMUYOR():
    """🔴 Adım (a) **yalnız sözlüğü** birleştirir. `cari`'nin ölçü ADLARI aynı ama
    İFADELERİ farklı (`SUM(CASE WHEN cha_tip=0…)` ↔ `SUM(BORC)`) — *aynı ada sahip iki
    ifadeyi "saf tekrar" sanıp birleştirmek, bu fazın üretebileceği en sessiz hatadır.*"""
    meta = {"name": "ticaret", "base_object": "faturalar",
            "measures": [{"name": "satis_tutari", "expression": "SUM(NETTOTAL)",
                          "type": "DOUBLE"}]}
    yeni, _ = cekirdek.cube_birlestir(meta, SOZLUK)
    m = yeni["measures"][0]
    assert m["expression"] == "SUM(NETTOTAL)" and m["type"] == "DOUBLE"
    assert yeni["base_object"] == "faturalar"


def test_CEKIRDEK_SOZLUKTE_BASE_OBJECT_ve_IFADE_YOK():
    """⚠ Fiziksel bağlama ERP'den ERP'ye **gerçekten** değişir; anlam değişmez.
    `base_object`'i çekirdeğe koymak, üç ERP'nin **birine ayrıcalık** tanımak olurdu."""
    for m in SOZLUK.get("metrikler") or []:
        assert "base_object" not in m, f"{m.get('name')}: çekirdekte base_object VAR"
        assert "expression" not in m, f"{m.get('name')}: çekirdekte ifade VAR"


def test_SINONIM_ADDITIVE_BIRLESIYOR():
    meta = {"name": "t", "base_object": "faturalar",
            "measures": [{"name": "satis_tutari", "expression": "X", "synonyms": ["yerel"]}]}
    yeni, degisti = cekirdek.cube_birlestir(meta, SOZLUK)
    syn = yeni["measures"][0]["synonyms"]
    assert "yerel" in syn, "ERP'nin kendi sinonimi SİLİNMİŞ"
    assert "ciro" in syn, "çekirdek sinonimi eklenmemiş"
    assert degisti


def test_VAR_OLAN_BIRIM_EZILMIYOR():
    """🔴 *Çekirdek, EKSİK olanı tamamlar; var olanı DÜZELTMEZ.* ERP bir birimi bilerek
    farklı yazmış olabilir (miktar `kg` ↔ `adet`); ezmek **sessizce yanlış birim** demekti
    — `1.9` numeric-fidelity kapısının tam olarak engellediği şey."""
    meta = {"name": "t", "base_object": "faturalar",
            "measures": [{"name": "satis_miktari", "expression": "X", "unit": "kg",
                          "additive": "semi"}]}
    yeni, _ = cekirdek.cube_birlestir(meta, SOZLUK)
    assert yeni["measures"][0]["unit"] == "kg"
    assert yeni["measures"][0]["additive"] == "semi"


def test_BAKIYE_SEMI_ADDITIVE_BEYAN_EDILIYOR():
    """Bir bakiyeyi net-hareket gibi **toplamak**, sistemin verebileceği en sessiz
    yanlıştır — sözlük bunu beyan etmek zorunda."""
    assert cekirdek.metrik_haritasi(SOZLUK)["bakiye"]["additive"] == "semi"


# ── 4 · GRAIN SÖZLEŞMESİ — fail-closed ──────────────────────────────────────

def test_GRAIN_IHLALI_BULUNUYOR():
    sozluk = {"grain_sozlesmeleri": {
                  "fatura": {"base_object_adlari": ["faturalar"]},
                  "stok_hareketi": {"base_object_adlari": ["stok_hareketleri"]}},
              "metrikler": [{"name": "satis_tutari", "grain": "fatura"}]}
    meta = {"name": "ticaret", "base_object": "stok_hareketleri",
            "measures": [{"name": "satis_tutari", "expression": "X"}]}
    ihlaller = cekirdek.grain_denetle("ticaret", meta, sozluk)
    assert len(ihlaller) == 1 and "stok_hareketi" in ihlaller[0]


def test_AYNI_GRAIN_IHLAL_DEGIL():
    sozluk = {"grain_sozlesmeleri": {"fatura": {"base_object_adlari": ["faturalar"]}},
              "metrikler": [{"name": "satis_tutari", "grain": "fatura"}]}
    meta = {"name": "t", "base_object": "faturalar",
            "measures": [{"name": "satis_tutari"}]}
    assert cekirdek.grain_denetle("t", meta, sozluk) == []


def test_BILINMEYEN_GRAIN_SERBEST():
    """🔴 `None` *"ihlal"* DEĞİL, *"bilinmiyor"* demektir. Sözleşmede sayılmamış bir tabloyu
    ihlal saymak, çekirdek sözlük büyümeden **her yeni ERP'yi reddederdi** —
    *bilinmeyeni yasak saymak, katmanı büyütmeyi cezalandırırdı.*"""
    sozluk = {"grain_sozlesmeleri": {"fatura": {"base_object_adlari": ["faturalar"]}},
              "metrikler": [{"name": "satis_tutari", "grain": "fatura"}]}
    meta = {"name": "t", "base_object": "bilinmeyen_tablo",
            "measures": [{"name": "satis_tutari"}]}
    assert cekirdek.grain_denetle("t", meta, sozluk) == []
    assert cekirdek.grain_adi(sozluk, "bilinmeyen_tablo") is None


def test_IHLAL_ON_KADEMESINDE_COMPOSE_U_REDDEDIYOR(monkeypatch):
    """🔴 **FAIL-CLOSED, uyarı DEĞİL.** Bir uyarı derlenmiş ve dağıtılmış bir MDL bırakır;
    o MDL'yi kimse geri almaz ve yanlış sayı **üretimde** çıkar. *Build zamanında durmak,
    üretim zamanında yanlış cevap vermekten kesinlikle iyidir.*"""
    sozluk = {"grain_sozlesmeleri": {
                  "fatura": {"base_object_adlari": ["faturalar"]},
                  "stok_hareketi": {"base_object_adlari": ["stok_hareketleri"]}},
              "metrikler": [{"name": "satis_tutari", "grain": "fatura"}]}
    monkeypatch.setattr(cekirdek, "kademe", lambda: "on")
    monkeypatch.setattr(cekirdek, "sozluk_yukle", lambda _b: sozluk)
    from app.compose import _merge_cube_metadata

    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td)
        (out / "cubes" / "ticaret").mkdir(parents=True)
        (out / "cubes" / "ticaret" / "metadata.yml").write_text(yaml.safe_dump(
            {"name": "ticaret", "base_object": "stok_hareketleri",
             "measures": [{"name": "satis_tutari", "expression": "X"}]}), encoding="utf-8")
        with pytest.raises(cekirdek.GrainIhlali):
            _merge_cube_metadata(DEMO, out)


def test_IHLAL_SHADOWDA_REDDETMIYOR(monkeypatch):
    """Gölge **ölçer**, kırmaz: bir kademenin amacı, açmadan önce **bedeli görmektir**."""
    sozluk = {"grain_sozlesmeleri": {
                  "fatura": {"base_object_adlari": ["faturalar"]},
                  "stok_hareketi": {"base_object_adlari": ["stok_hareketleri"]}},
              "metrikler": [{"name": "satis_tutari", "grain": "fatura"}]}
    monkeypatch.setattr(cekirdek, "kademe", lambda: "shadow")
    monkeypatch.setattr(cekirdek, "sozluk_yukle", lambda _b: sozluk)
    from app.compose import _merge_cube_metadata

    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td)
        (out / "cubes" / "ticaret").mkdir(parents=True)
        (out / "cubes" / "ticaret" / "metadata.yml").write_text(yaml.safe_dump(
            {"name": "ticaret", "base_object": "stok_hareketleri",
             "measures": [{"name": "satis_tutari", "expression": "X"}]}), encoding="utf-8")
        _merge_cube_metadata(DEMO, out)      # patlamamalı


def test_GRAIN_SOZLESMESI_OLCULEN_KUSURU_KAPSIYOR():
    """Ölçüldü: mikro `stok_hareketleri` ↔ logo/netsis `faturalar`. Sözleşme **ikisini de**
    tanımalı, yoksa ihlal hiç görünmez."""
    for bo in ("stok_hareketleri", "faturalar"):
        assert cekirdek.grain_adi(SOZLUK, bo) is not None, f"{bo} sözleşmede YOK"
    assert cekirdek.grain_adi(SOZLUK, "faturalar") != cekirdek.grain_adi(
        SOZLUK, "stok_hareketleri")


# ── 5 · BEŞİNCİ ÜRETEÇ — yeni desen icat edilmedi ───────────────────────────

def test_COMPOSE_BES_URETEC_TASIYOR():
    """*Yeni desen icat edilmiyor:* `compose()` zaten dört YAML üreteci taşıyordu;
    `_merge_cube_metadata` **beşincisidir**."""
    agac = ast.parse((KOK / "app" / "compose.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "compose")
    uretecler = {getattr(n.func, "id", "") for n in ast.walk(fn) if isinstance(n, ast.Call)}
    beklenen = {"_merge_cube_synonyms", "_compose_derived_metrics",
                "_compose_relationship_dimensions", "_compose_kpis", "_merge_cube_metadata"}
    assert beklenen <= uretecler, f"eksik üreteç: {sorted(beklenen - uretecler)}"


def test_ERP_CUBE_DOSYALARI_YERINDE():
    """🔴 **SİLME YOK** (göç reçetesi madde 4). Geri alma = **bayrağı kapatmak**; bir
    dosya silinmişse bayrak artık geri almıyor demektir."""
    for pack in ("mikro-v16", "logo-3", "netsis"):
        yol = DEMO / "packs" / "kaynak" / pack / "cubes" / "ticaret" / "metadata.yml"
        assert yol.is_file(), f"{pack}/ticaret SİLİNMİŞ — geri alma artık mümkün değil"


# ── 6 · GÖLGE DIFF — ölçüm aracının kendisi ─────────────────────────────────

def test_MDL_DIFF_ARACI_SAYIYI_SOZLUKTEN_AYIRIYOR():
    """🔴 Bir göçün *"sayı değişmedi ama sözlük büyüdü"* olması **beklenen** sonuçtur;
    ikisini aynı kovaya koymak, gerçek bir ifade değişikliğini **sözlük gürültüsünde**
    gizlerdi."""
    kaynak = (KOK / "lab" / "mdl_diff.py").read_text(encoding="utf-8")
    assert "sayi_farklari" in kaynak and "sozluk_farklari" in kaynak
    assert 'k.startswith("~")' in kaynak, "iki kova AYRILMIYOR"


def test_MDL_DIFF_OLCULEMEYENI_YESIL_SAYMIYOR():
    """⊘ üçüncü durum: ölçülemeyen bir şirketi *"fark yok"* diye raporlamak, **risk yok
    YALANI** üretirdi."""
    kaynak = (KOK / "lab" / "mdl_diff.py").read_text(encoding="utf-8")
    i = kaynak.index("ÖLÇÜLEMEDİ")
    assert "kirmizi += 1" in kaynak[i:i + 200]


@pytest.mark.parametrize("sirket", ["demo-boyahane", "gitas", "atiksan", "gulteks"])
def test_OLCULDU_SAYI_ETKISI_SIFIR(sirket):
    """🔴 **KABUL ÖLÇÜTÜ — göç reçetesinin 1. maddesi.** Ölçüldü (2026-08-04,
    `python lab/mdl_diff.py`): dört şirketin **dördünde de sayı-etkisi 0 fark**; sözlük
    farkı sırasıyla **2 · 8 · 5 · 7**. Bu test o ölçümü **kilitler**: çekirdek katman bir
    gün bir ifadeye dokunursa burada kırmızı verir.

    ⚠ **Bu sayı bir kez YANLIŞ ÇIKTI ve düzeltildi:** aracın ilk sürümü `additive`'i
    *sözlük* kovasında sayıyordu ve *"0 fark"* diyordu; kova düzeltilince **beş gerçek
    fark** göründü (`mal`/`ticaret` ölçülerine yazılan `additive: full`). Bugünkü 0,
    **düzeltilmiş** araçla ölçülmüş 0'dır.

    ⚠ `demo/` yoksa `skip` — ölçüm ön koşulu sağlanmayan bir vakayı yeşil saymak, bu
    deponun `⊘ ÖLÇÜLEMEDİ` disiplininin ihlali olurdu.
    """
    if not (DEMO / "companies" / sirket).is_dir():
        pytest.skip(f"{sirket} bu koşumda mount edilmemiş")
    import sys

    sys.path.insert(0, str(KOK / "lab"))
    from mdl_diff import diff                                    # noqa: PLC0415

    sayi, _sozluk = diff(sirket)
    assert not sayi, f"{sirket}: çekirdek katman SAYIYI etkiliyor → {list(sayi)[:5]}"


# ── 7 · ⚠ GRAIN SÖZLEŞMESİ BUGÜN HİÇBİR METRİKTE BEYAN EDİLMEDİ ────────────

def test_CARI_GRAIN_SOZLESMESI_ATESLIYOR():
    """⟳ **TUZAKTAN KAPIYA — adım (b) indi, kapı TERS ÇEVRİLDİ.**

    Eski yön: *"hiçbir metrik henüz `grain:` beyan etmiyor; kapı ARMED ama ateşlemiyor"*.
    Adım (b) geldi. Yeni yön: **`cari` metrikleri sözleşme beyan ediyor ve üç ERP'nin
    üçü de ona UYUYOR** — yani kapı artık gerçek veri üstünde **çalışıyor**.

    🔴 `cari` sözleşmeyi beyan etmek için **doğru yerdi**: üç ERP'de de aynı grain (cari
    hareket), aynı ölçü adları; farklı olan yalnız **ifade**. `ticaret` ise **uymuyor** —
    onun sözleşmesi bilerek adım (c)'ye bırakıldı.
    """
    beyan = {m["name"]: m["grain"] for m in (SOZLUK.get("metrikler") or []) if m.get("grain")}
    assert beyan, "adım (b) geri mi alındı? hiçbir metrik grain beyan etmiyor"
    for ad in ("bakiye", "toplam_borc", "toplam_alacak", "hareket_sayisi"):
        assert beyan.get(ad) == "cari_hareket", f"{ad} sözleşmesi YOK"

    # ⚠ Ve sözleşme GERÇEK pack'lerde ateşliyor: üç ERP'nin `cari` cube'u da tanınmalı,
    # yoksa `grain_adi()` None döner ve kapı SESSİZCE kapalı kalırdı.
    for pack in ("mikro-v16", "logo-3", "netsis"):
        yol = DEMO / "packs" / "kaynak" / pack / "cubes" / "cari" / "metadata.yml"
        meta = yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
        assert cekirdek.grain_adi(SOZLUK, meta.get("base_object")) == "cari_hareket", (
            f"{pack}/cari `base_object`'i ({meta.get('base_object')}) sözleşmede TANINMIYOR — "
            "kapı ARMED görünüp hiç ateşlemez")
        assert cekirdek.grain_denetle("cari", meta, SOZLUK) == [], f"{pack}/cari İHLAL"


def test_TICARET_KARARI_KAYITLI():
    """⟳ **TUZAKTAN KAPIYA — adım (c) kararı verildi (2026-08-04).**

    Eski yön: *"`satis_tutari` grain beyan etmiyor; karar adım (c)'nin"*. Karar verildi:
    **kanonik grain = `fatura`**, karşı grain'ler ayrı metrik olarak kayıtlı
    (`satis_tutari_hareket` @stok_hareketi · `satis_tutari_kalem` @fatura_kalem) —
    *tek metrik iki anlama BÜKÜLMEZ.*

    🔴 Ve karar **kalem · sahip · tarih** taşımak zorunda: gerekçesiz bir karar, bir
    sonraki tur tarafından *"neden böyle?"* diye yeniden açılır ve aynı ölçüm yeniden
    yapılır.
    """
    h = cekirdek.metrik_haritasi(SOZLUK)
    assert h["satis_tutari"]["grain"] == "fatura"
    assert h["satis_tutari_hareket"]["grain"] == "stok_hareketi"
    assert h["satis_tutari_kalem"]["grain"] == "fatura_kalem"
    kaynak = (DEMO / "packs" / "cekirdek" / "metrik_sozlugu.yml").read_text(encoding="utf-8")
    for gereken in ("**Karar**", "**Gerekçe**", "**Sahip**", "**Tarih**", "2026-08-04"):
        assert gereken in kaynak, f"karar kaydında `{gereken}` YOK"


def test_FATURA_ile_FATURA_KALEMI_AYRI_GRAIN():
    """🔴 **Sözleşmenin kendi içindeki hata — ölçümle bulundu.** İlk yazımda `fatura_kalem`
    `fatura` grain'inin takma adları arasındaydı: yani *"fatura"* ile *"fatura kalemi"*
    aynı sayılıyordu. Değiller — bir faturanın **çok** kalemi olur ve kalem düzeyinde
    toplanan bir tutar, fatura düzeyinde toplanandan **farklı** olabilir (satır bazlı
    iskonto/iade). *Bu, sözleşmenin engellemek için var olduğu hatanın sözleşmenin kendi
    içindeki hâliydi.*"""
    assert cekirdek.grain_adi(SOZLUK, "faturalar") == "fatura"
    assert cekirdek.grain_adi(SOZLUK, "fatura_satirlari") == "fatura_kalem"


def test_AD_GOCU_INDI_AYRISMA_KAPANDI():
    """⟳ **TUZAKTAN KAPIYA — adım (c2) indi (2026-08-04).**

    Eski yön: *"`satis_tutari` üç grain / beş cube; `gitas` içinde iki grain"*. Ad göçü
    indi ve ayrışma **kapandı**: artık `satis_tutari` **yalnız `fatura`** grain'inde;
    öteki grain'ler kendi adlarını taşıyor (`_hareket` · `_kalem`).

    🔴 **Sinonimler DEĞİŞMEDİ** — kullanıcı hâlâ *"satış"*/*"ciro"* diye sorabiliyor.
    Değişen yalnız metriğin **kimliği**. *Bir kullanıcıyı kendi kelimesinden etmek,
    sözleşmenin amacı değildir.*
    """
    grainler: dict[str, str] = {}
    sinonimli: list[str] = []
    for yol in (DEMO / "packs").rglob("cubes/*/metadata.yml"):
        meta = yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
        for m in meta.get("measures") or []:
            ad = str(m.get("name") or "")
            if not ad.startswith("satis_tutari"):
                continue
            g = cekirdek.grain_adi(SOZLUK, meta.get("base_object")) or "?"
            anahtar = f"{yol.parts[-4]}/{meta.get('name')}.{ad}"
            grainler[anahtar] = g
            # ⚠ **ÖLÇÜLDÜ, varsayılmadı:** `mal` cube'larının ölçüleri `satış tutarı`
            # taşıyor, çıplak `satış` değil (o cube-düzeyinde duruyor). Doğru değişmez
            # "şu token var mı" değil, **sinonim listesi BOŞALMADI mı** — göç yalnız
            # KİMLİĞİ değiştirmeliydi.
            if m.get("synonyms"):
                sinonimli.append(anahtar)
    kanonik = {k: v for k, v in grainler.items() if k.endswith(".satis_tutari")}
    assert set(kanonik.values()) == {"fatura"}, (
        f"`satis_tutari` hâlâ birden çok grain'de: {kanonik}")
    assert len(grainler) == 5, f"beş ölçü bekleniyordu: {grainler}"
    assert len(sinonimli) == len(grainler), (
        f"bir ölçünün sinonimleri göçte KAYBOLMUŞ ({sorted(set(grainler) - set(sinonimli))}) "
        "— kullanıcı kendi kelimesinden edilmiş olur")


def _KULLANILMIYOR_test_UC_GRAIN_BES_CUBE_OLCUMU_KAYITLI():
    """⚠ **Yol haritasının teşhisinden AĞIR çıktı ve ölçüm yazıldı.** Yol haritası
    *"`ticaret` üç ERP'de farklı grain"* diyordu; sayım **üç grain / beş cube** gösterdi —
    ve ayrışma **şirket içinde**: `gitas` (netsis) `satis_tutari`'yi hem `ticaret`@fatura
    hem `mal`@stok_hareketi olarak taşıyor. *Aynı şirkette aynı soruya iki sayı.*"""
    bulunan: dict[str, str] = {}
    for yol in (DEMO / "packs").rglob("cubes/*/metadata.yml"):
        meta = yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
        adlar = {m.get("name") for m in (meta.get("measures") or [])}
        if "satis_tutari" in adlar:
            bulunan[f"{yol.parts[-4]}/{meta.get('name')}"] = (
                cekirdek.grain_adi(SOZLUK, meta.get("base_object")) or "?")
    assert len(bulunan) == 5, f"beş cube bekleniyordu, {len(bulunan)} bulundu: {bulunan}"
    assert len(set(bulunan.values())) == 3, f"üç grain bekleniyordu: {bulunan}"
    netsis = {k: v for k, v in bulunan.items() if k.startswith("netsis/")}
    assert len(set(netsis.values())) == 2, (
        f"netsis içi ayrışma KAPANMIŞ ({netsis}) — ad göçü indiyse bu test GÜNCELLENMELİ")


def _KULLANILMIYOR_test_TICARET_SOZLESMESI_BILEREK_YOK():
    """⚠ `satis_tutari`'nın kanonik grain'i (fatura mı, stok hareketi mi) bir **karardır**
    ve göç reçetesinin **adım (c)**'sine aittir: *"ikisi de meşru olabilir → çekirdekte
    İKİ ayrı metrik"*. Bugün beyan etmek, üç ERP'den ikisini **derleme zamanında
    reddetmek** demekti.

    *Yazılmamış bir kararı kapıya çevirmek, kararı vermiş gibi yapmaktır.*
    """
    beyan = {m["name"]: m.get("grain") for m in (SOZLUK.get("metrikler") or [])}
    assert not beyan.get("satis_tutari"), (
        "`satis_tutari` grain beyan ediyor — adım (c) kararı VERİLDİYSE bu test "
        "GÜNCELLENMELİ, silinmemeli (ve iki ayrı metrik yazılmalı)")
    kaynak = (DEMO / "packs" / "cekirdek" / "metrik_sozlugu.yml").read_text(encoding="utf-8")
    assert "adım (c)" in kaynak, "kararın SAHİBİ yazılı değil — bir sonraki tur unutur"


def test_SOZLUK_GIRDILERI_OLU_DEGIL():
    """🔴 **Ölçülen kusur:** ilk sözlükte `borc_toplami`/`alacak_toplami` yazıyordu;
    cube'lardaki gerçek adlar `toplam_borc`/`toplam_alacak`. Eşleşme **adla** olduğu için
    o iki girdi **hiçbir şeye dokunmuyordu** — sessizce ölü sözlük satırları.
    *Kimseyle eşleşmeyen bir sözlük girdisi, yazılmamış bir girdiyle aynı şeydir.*

    Kapı: her çekirdek metrik, **en az bir** gerçek cube ölçüsüyle eşleşmeli.
    """
    gercek: set[str] = set()
    for yol in (DEMO / "packs").rglob("cubes/*/metadata.yml"):
        meta = yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
        gercek |= {str(m.get("name")) for m in (meta.get("measures") or [])}
    # ⚠ `karar_kaydi: true` MUAF — ve gerekçesi yazılı: bunlar bir **kararın kaydıdır**
    # (`satis_tutari_hareket` · `satis_tutari_kalem`), bir eşleşme beklentisi değil.
    # Ad göçü inene kadar hiçbir cube bu adları taşımaz; muafiyeti yazmamak, kararı
    # "ölü satır" diye sildirirdi — yani kararın kendisini kaybettirirdi.
    olu = [m["name"] for m in (SOZLUK.get("metrikler") or [])
           if m["name"] not in gercek and not m.get("karar_kaydi")]
    assert not olu, f"ÖLÜ sözlük girdisi (hiçbir cube ölçüsüyle eşleşmiyor): {olu}"


def test_UC_ERPNIN_GRAIN_AYRISMASI_HALA_DURUYOR():
    """⚠ Ölçülen kusur **kapanmadı**, yalnız **görünür** oldu: sözleşme grain'leri tanıyor
    ama `ticaret` hâlâ üç ERP'de iki farklı grain'de duruyor. *Bir kusuru ölçülebilir
    kılmak onu çözmez — ama çözülene kadar sessiz kalmasını engeller.*"""
    grainler = {}
    for pack in ("mikro-v16", "logo-3", "netsis"):
        yol = DEMO / "packs" / "kaynak" / pack / "cubes" / "ticaret" / "metadata.yml"
        meta = yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
        grainler[pack] = cekirdek.grain_adi(SOZLUK, meta.get("base_object"))
    assert grainler["mikro-v16"] == "stok_hareketi"
    assert grainler["logo-3"] == grainler["netsis"] == "fatura"
    assert len(set(grainler.values())) == 2, "ayrışma kapanmışsa adım (c) İNMİŞ demektir"


def test_ADDITIVE_SAYI_KOVASINDA_SOZLUKTE_DEGIL():
    """🔴 **ÖLÇÜM ARACININ KENDİ KUSURU — ve düzeltmesi.**

    İlk sürüm `additive`'i *sözlük* kovasına koymuştu (sinonim/birimle birlikte, yani
    *"zararsız"* tarafa). Oysa `additive: semi` motorun **toplama semantiğini** değiştirir:
    dönem boyunca toplamak yerine **dönem sonu** alınır. Bir gün bir cube `additive`
    beyan etmeyi unutsaydı, çekirdek onu doldururdu ve araç bunu **zararsız bir sözlük
    değişikliği** diye raporlardı — yani gölge diff'in tek işi olan *"sayı değişti mi"*
    sorusuna **yanlış** cevap verirdi.

    Bugün gerçek pack'lerde etkisi yok (üç `cari` cube'unun üçü de `additive`'i **zaten**
    beyan ediyor ve `cube_birlestir` yalnız **eksik** olanı doldurur) — ama bir ölçüm
    aracının doğruluğu bugünkü veriye bağlı olamaz.

    *Ölçüm aracının kendisi de bir bağımlılıktır* (MIMARI §6.4).
    """
    kaynak = (KOK / "lab" / "mdl_diff.py").read_text(encoding="utf-8")
    i = kaynak.index('out[f"~{cube}')
    sozluk_blogu = kaynak[i:i + 300]
    assert '"additive"' not in sozluk_blogu, "`additive` hâlâ SÖZLÜK kovasında"
    j = kaynak.index('out[f"{cube}.{tur[:-1]}.{ad}"]')
    assert "additive" in kaynak[j:j + 300], "`additive` SAYI kovasında değil"


def test_ADDITIVE_BIRLESTIRILMIYOR():
    """🔴 **ÖLÇÜM ARACI, GÖNDERMEK ÜZERE OLDUĞUM DAVRANIŞ DEĞİŞİKLİĞİNİ YAKALADI.**

    İlk sürüm `additive`'i de dolduruyordu ve gölge diff **0 fark** diyordu — çünkü aracın
    kendisi `additive`'i *sözlük* (zararsız) kovasına koymuştu. Kova düzeltilir düzeltilmez
    gerçek çıktı: `mal` ve `ticaret` cube'ları `additive` **beyan etmiyor** ve çekirdek
    onlara `additive: full` **yazıyordu** — yani *"hiçbir sayıya dokunmuyor"* diye ilan
    edilen bir göç, motorun **toplama semantiğini** değiştiriyordu.

    ⚠ Doğru değer **ifadeye** bağlı: `cari.bakiye` üç ERP'de `SUM(borç − alacak)` yani bir
    **hareket toplamı**; bir stok anlık görüntüsü olsaydı `semi` olurdu. Merkezî olarak,
    ifadeye bakmadan karara bağlamak, bu maddenin engellemek için var olduğu hatanın
    ta kendisidir. Karar **adım (c)**'nin.
    """
    meta = {"name": "t", "base_object": "faturalar",
            "measures": [{"name": "bakiye", "expression": "SUM(BORC - ALACAK)"}]}
    yeni, _ = cekirdek.cube_birlestir(meta, SOZLUK)
    assert "additive" not in yeni["measures"][0], (
        "çekirdek `additive` YAZIYOR — toplama semantiği merkezî olarak, İFADEYE "
        "bakmadan karara bağlanmış olur")
    assert cekirdek.metrik_haritasi(SOZLUK)["bakiye"].get("additive") == "semi", (
        "sözlükteki BEYAN silinmiş — beyan kalır, yazma yapılmaz (adım c'nin girdisi)")


# ── 8 · TÜREV KATMAN — sürüklenme BİR KAT YUKARIDA tekrar üretiliyordu ──────

def test_TUREV_KUPUN_GRAINI_DAMGALANIYOR():
    """🔴 **KAPIYI KÖR EDEN ŞEY, ONUN KENDİ GÜVENLİ VARSAYIMIYDI.**

    `karlilik` türev küpü aynı sürüklenmeyi bir kat yukarıda tekrar üretiyordu:
    `base_model` mikro'da `stok_hareketleri`, logo-3'te `fatura_satirlari`, netsis'te
    `stok_hareketleri`. Ama küpün `base_object`'i türetilmiş görünüm adıdır
    (`karlilik_src`) ve o ad hiçbir sözleşmede geçmez → *"bilinmeyen grain SERBEST"*
    kuralı **gerçek bir ihlali koruyordu**.

    `compose` artık türev küpe kaynağın `base_model`'ini damgalıyor (`grain_kaynak`) ve
    grain kararı ondan türüyor.
    """
    kaynak = (KOK / "app" / "compose.py").read_text(encoding="utf-8")
    assert 'cube["grain_kaynak"] = binding["base_model"]' in kaynak, \
        "türev küpe grain damgası VURULMUYOR — kapı türev katmanda kör"
    ck = (KOK / "app" / "cekirdek.py").read_text(encoding="utf-8")
    assert 'meta.get("grain_kaynak") or meta.get("base_object")' in ck, \
        "grain kararı damgayı OKUMUYOR"

    # Damga gerçekten karar değiştiriyor mu — yapısal değil DAVRANIŞSAL kontrol.
    sozluk = {"grain_sozlesmeleri": {
                  "fatura": {"base_object_adlari": ["faturalar"]},
                  "stok_hareketi": {"base_object_adlari": ["stok_hareketleri"]}},
              "metrikler": [{"name": "satis_tutari", "grain": "fatura"}]}
    meta = {"name": "karlilik", "base_object": "karlilik_src",
            "grain_kaynak": "stok_hareketleri",
            "measures": [{"name": "satis_tutari", "expression": "X"}]}
    assert cekirdek.grain_denetle("karlilik", meta, sozluk), \
        "damgalı küpte ihlal GÖRÜLMÜYOR — kapı hâlâ kör"


def test_TUREV_METRIGIN_KIMLIGI_AYRI_ve_KIYASLANAMAZ():
    """⚠ `karlilik.satis_tutari` → `satis_tutari_turev`. Kanonik ad OLAMAZ (hiçbir ERP'de
    fatura grain'inde değil), `_hareket`/`_kalem` de olamaz (grain'i SABİT değil).
    Dördüncü kimlik, grain'i **bilinçli olarak beyan edilmemiş** — ve bu bir eksiklik
    değil, **ölçülen gerçeğin kaydıdır**.

    🔴 `kiyaslanamaz: true` bir SÜS değil, bir uyarıdır: iki şirketin bu sayısını yan yana
    koymak, iki farklı şeyi karşılaştırmaktır."""
    h = cekirdek.metrik_haritasi(SOZLUK)
    t = h["satis_tutari_turev"]
    assert not t.get("grain"), "türev metriğe SABİT grain dayatılmış — üç ERP'den ikisi düşer"
    assert t.get("kiyaslanamaz") is True, "kıyaslanamazlık BEYAN EDİLMEMİŞ"
    kaynak = (DEMO / "packs" / "modul" / "turev" / "karlilik.yml").read_text(encoding="utf-8")
    assert "satis_tutari_turev" in kaynak and "name: satis_tutari\n" not in kaynak
    assert "KIYASLANMAZ" in kaynak, "kıyaslanamazlık ÖLÇÜNÜN YANINDA yazılı değil"


# ── 9 · AÇMA KARARI — ölçüldü, `off` KALDI ve nedeni yazılı ─────────────────

def test_ACMA_KARARI_OLCULDU_ve_OFF_KALDI():
    """🔴 **Bayrak `on` yapılMADI — ve bu bir unutma değil, ÖLÇÜLMÜŞ bir karar.**

    Ölçüldü (2026-08-04, `DIMA_CEKIRDEK_KATMAN=on python lab/kapi.py --tam`):

    | | `off` | `on` |
    |---|---|---|
    | TOPLAM doğru-cube | %93,1 | **%93,1** |
    | `gitas` doğru/payda | 1515/1694 | 1517/1696 |
    | semantik vaka | %91,5 | %91,7 |

    Yani **kazanç ölçülemedi**. Yol haritasının karar kuralı (§C): *"kazanç varsa `beta`,
    yoksa `off` **ve nedeni yazılır**."* Nedeni burada yazılı.

    ⚠ **Sözleşmenin dişleri bayrağa BAĞLI DEĞİL:** grain ihlallerini `on` beklemeden
    `tests/test_cekirdek_katman.py` + `lab/mdl_diff.py` yakalıyor (ikisi de bayraktan
    bağımsız koşar) — türev katmandaki gizli ihlali bulan da tam olarak buydu.
    *Bir sözleşmenin değeri, uygulandığı anda değil, İHLALİ GÖRÜLDÜĞÜ anda başlar.*
    """
    from app.config import Settings

    assert Settings.model_fields["cekirdek_katman"].default == "off"
    kaynak = pathlib.Path(__file__).read_text(encoding="utf-8")
    assert "kazanç ölçülemedi" in kaynak, "karar GEREKÇESİZ — bir sonraki tur yeniden ölçer"


# ── 10 · BORÇ #11 — GRAIN-FARKINDA ÇAPRAZ-CUBE GEÇİŞİ ──────────────────────

def _sema():
    """Ad göçü sonrası gerçekçi mini şema: `ticaret`@fatura ↔ `mal`@stok_hareketi."""
    return {"cubes": [
        {"name": "ticaret", "display": "satış", "measures": ["satis_tutari"],
         "dimensions": ["cari_adi"], "synonyms": ["satış"],
         "dimension_synonyms": {"cari_adi": ["musteri", "müşteri", "cari"]},
         "measure_synonyms": {"satis_tutari": ["satış", "ciro"]},
         "measure_synonyms_display": {"satis_tutari": "satış tutarı"},
         "cekirdek_metrik": {}},
        {"name": "mal", "display": "stok", "measures": ["satis_tutari_hareket"],
         "dimensions": ["stok_adi"], "synonyms": ["stok", "ürün"],
         "dimension_synonyms": {"stok_adi": ["urun", "ürün", "stok adi"]},
         "measure_synonyms": {"satis_tutari_hareket": ["satış tutarı"]},
         "measure_synonyms_display": {"satis_tutari_hareket": "satış tutarı (hareket)"},
         "cekirdek_metrik": {"satis_tutari_hareket": "satis_tutari"}},
        {"name": "karlilik", "display": "kârlılık", "measures": ["satis_tutari_turev"],
         "dimensions": ["stok_adi"], "synonyms": ["kâr"],
         "dimension_synonyms": {"stok_adi": ["urun", "ürün", "stok adi"]},
         "measure_synonyms": {"satis_tutari_turev": ["satış"]},
         "measure_synonyms_display": {"satis_tutari_turev": "satış (kârlılık girdisi)"},
         "cekirdek_metrik": {"satis_tutari_turev": "satis_tutari"},
         "kiyaslanamaz": ["satis_tutari_turev"]},
    ]}


def test_KIYASLANAMAZ_OLCUYE_GECILMIYOR():
    """🔴 `satis_tutari_turev`'in grain'i ERP'ye göre **değişir**. Oraya geçmek,
    kullanıcıya *"aynı şeyin kırılımı"* diye **başka bir şeyi** göstermek olurdu —
    ve `karlilik` de `stok_adi` taşıdığı için geçiş oraya **düşebilirdi**."""
    from app import cube_router as cr

    dsw = cr.cross_cube_dim_switch({"cube": "ticaret", "measures": ["satis_tutari"]},
                                   "urun bazli", _sema())
    assert dsw is not None and dsw["cube"] == "mal", \
        f"kıyaslanamaz küpe geçilmiş ya da geçiş bulunamamış: {dsw}"


def test_BELIRSIZ_VARYANT_SESSIZCE_COZULMUYOR():
    """🔴 Aynı kavramın **iki** varyantını taşıyan bir hedefte geçiş **reddedilir**.
    Belirsizliği sessizce çözmek — birini seçip ötekini yok saymak — tam olarak bu
    maddenin engellemek için var olduğu şeydir. *Gerçek belirsizlik chip'e gider,
    tahmine değil.*"""
    from app import cube_router as cr

    sema = _sema()
    sema["cubes"][1]["measures"].append("satis_tutari_kalem")
    sema["cubes"][1]["cekirdek_metrik"]["satis_tutari_kalem"] = "satis_tutari"
    assert cr.cross_cube_dim_switch({"cube": "ticaret", "measures": ["satis_tutari"]},
                                    "urun bazli", sema) is None


def test_UYARI_CEVABIN_NOTUNA_GIRIYOR():
    """🔴 **K2 — yetim uç yok.** Bir uyarı, kullanıcıya ULAŞMIYORSA yoktur.
    `ask.py` konu-değişimi notunu `grain_uyarisi` ile birleştiriyor."""
    kaynak = (KOK / "app" / "routers" / "ask.py").read_text(encoding="utf-8")
    i = kaynak.index('note=f"Konu değişti:')
    assert "grain_uyarisi" in kaynak[i:i + 300], \
        "tanelik uyarısı cevabın notuna GİRMİYOR — kullanıcı göremez"
