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


def test_TICARET_SOZLESMESI_BILEREK_YOK():
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
    olu = [m["name"] for m in (SOZLUK.get("metrikler") or []) if m["name"] not in gercek]
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
