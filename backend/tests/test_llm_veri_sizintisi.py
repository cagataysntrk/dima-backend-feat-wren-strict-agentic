"""FAZ A1 — DEĞİŞMEZ §4-1'in CI kapısı: LLM'e kişisel veri GİTMEZ.

`MIMARI.md §4-1` yıllardır *"LLM ham değer görmez"* diyordu **ve bu doğru değildi**.
Ölçüldü (2 Ağustos 2026): `app/llm.py::_schema_prompt` her modelin her VARCHAR kolonundan
örneklenmiş **1391 gerçek değeri** prompt'a yazıyordu — içinde çalışanların **tam ad-soyadı**,
**SGK numaraları**, **IBAN**'lar. `app/cube_router.py::build_catalog` ise daha dar bir politika
uyguluyordu (358 değer): **aynı LLM'e iki farklı gizlilik politikası.**

Değişmezin kendi metni bu testi zaten istiyordu: *"Bu bir CI testi olmalı, niyet beyanı değil."*

## Bu test neden ÜRETİCİYİ değil ÇIKTIYI denetler

Süzgeci (`app/sensitivity.py::prompt_safe_values`) bugün iki üretici çağırıyor. Üçüncü bir
üretici eklenirse "hepsi süzgeci çağırıyor mu?" diye bakan bir test onu **kaçırır**. Bu yüzden
test, gerçek veritabanından kişisel-veri kümesini çeker ve **üretilen metnin içinde** arar.
Yeni bir üretici eklendiğinde tek yapılacak onu `URETICILER` listesine eklemektir; süzgeci
çağırmayı unutursa test **kırılır**.

## Neden değerler tamamen silinmiyor

`cube_router.route()` de aynı `values` alanını okuyor ve *"Aylin Bulut'un firesi"* gibi bir
soruyu **LLM'siz** çözebilmesi için değerleri görmesi gerekir — o kod **süreç içinde** çalışır,
veri kurumdan çıkmaz. Sınır *"kim görüyor"* değil **"nereye gidiyor"**dur.
"""

from __future__ import annotations

import pytest

from app import cube_router, llm
from app.sensitivity import classify, is_sensitive, prompt_safe_values

# LLM prompt'u üreten HER fonksiyon buraya eklenir. Yeni bir üretici eklenip buraya
# yazılmazsa bu test onu göremez — o yüzden `test_uretici_listesi_TAM` ikinci bir kapı kurar.
URETICILER = (
    ("llm._schema_prompt", lambda sc: llm._schema_prompt(sc)),
    ("cube_router.build_catalog", lambda sc: cube_router.build_catalog(sc)[0]),
)

# Demo şemasında KİŞİYİ tanımlayan kolonlar (tablo, kolon). Test bunların GERÇEK değerlerini
# veritabanından çeker — sabit liste tutmak veri değişince testi kör bırakırdı.
KISI_KOLONLARI = (
    ("personel", "ad_soyad"), ("personel", "personel_kodu"),
    ("personel_ozluk", "tc_kimlik"), ("personel_ozluk", "sgk_no"),
    ("partiler", "operator"), ("ariza_kayitlari", "mudahale_eden"),
    ("bakim_planlari", "sorumlu"), ("banka_hesaplari", "iban"),
)


@pytest.fixture(scope="module")
def kisi_degerleri():
    """Gerçek veritabanından kişisel-veri değer kümesi."""
    import duckdb

    from app.config import get_settings

    s = get_settings()
    con = duckdb.connect(str((s.connection_dict() or {}).get("path")
                             or "demo/data/boyahane.duckdb"), read_only=True)
    try:
        out: set[str] = set()
        for tablo, kolon in KISI_KOLONLARI:
            try:
                out |= {str(r[0]) for r in con.execute(
                    f'SELECT DISTINCT "{kolon}" FROM main."{tablo}" '
                    f'WHERE "{kolon}" IS NOT NULL').fetchall()}
            except Exception:  # noqa: BLE001 — bu kolon bu şemada yoksa test onu atlar
                continue
    finally:
        con.close()
    # Çok kısa değerler (1-2 karakter) rastgele alt-dize eşleşmesi üretir → elenir.
    return {v for v in out if len(v) > 2}


def test_kisi_verisi_kumesi_BOS_DEGIL(kisi_degerleri):
    """Kapının kendisi çalışıyor mu: aranacak veri gerçekten var mı? Bu olmadan test
    her zaman yeşil kalır ve hiçbir şey kanıtlamaz."""
    assert len(kisi_degerleri) >= 20, (
        f"yalnız {len(kisi_degerleri)} kişisel değer bulundu — KISI_KOLONLARI listesi "
        "şemayla uyumsuz olabilir, test kör kalır")


@pytest.mark.parametrize("ad,uretici", URETICILER, ids=[u[0] for u in URETICILER])
def test_prompt_KISISEL_VERI_icermez(schema, kisi_degerleri, ad, uretici):
    """ASIL KAPI. Üretilen prompt metninde gerçek kişisel veri geçemez."""
    metin = uretici(schema)
    sizan = sorted(v for v in kisi_degerleri if v in metin)
    assert not sizan, (
        f"{ad} LLM prompt'una KİŞİSEL VERİ yazıyor ({len(sizan)} değer): {sizan[:8]}\n"
        "Değerler `app/sensitivity.py::prompt_safe_values` süzgecinden geçmeli. Kolon "
        "ad-tabanlı emniyet ağına takılmıyorsa model YAML'ında `sensitivity: person` "
        "BEYAN edilmeli.")


@pytest.mark.parametrize("ad,uretici", URETICILER, ids=[u[0] for u in URETICILER])
def test_prompt_HALA_ise_yarar(schema, ad, uretici):
    """Süzgeç her şeyi silmemeli: hassas OLMAYAN değerler (renk, aşama, makine) LLM'in
    doğru `WHERE` yazabilmesi için prompt'ta KALMALI. Aksi halde gizliliği doğruluğu
    tamamen feda ederek satın almış oluruz."""
    metin = uretici(schema)
    assert "∈" in metin, f"{ad}: enum bloğu tamamen kayboldu"
    assert "Beyaz" in metin or "KASAR" in metin, (
        f"{ad}: hassas olmayan kategorik değerler de silinmiş — süzgeç fazla geniş")


def test_deterministik_yol_degerleri_HALA_goruyor(schema):
    """Sınır *"kim görüyor"* değil *"nereye gidiyor"*. `route()` süreç içinde çalışır ve
    "Aylin Bulut'un firesi" gibi soruları LLM'siz çözebilmek için değerleri görmelidir.
    Değerler kaynakta silinseydi bu yetenek sessizce ölürdü — ilk tasarım buydu, ölçüp
    vazgeçildi."""
    cols = {c["name"]: c for m in schema.get("models", []) for c in m["columns"]}
    op = cols.get("operator")
    assert op and op.get("values"), "operator değerleri şemadan silinmiş — route() körleşir"
    assert is_sensitive(op), "operator hassas işaretlenmemiş"
    assert prompt_safe_values(op) == [], "hassas kolon prompt'a değer sızdırıyor"


def test_uretilen_calc_kolonu_hassasiyeti_MIRAS_ALIR(schema):
    """`expose:` üreteci bir kolonun DEĞERLERİNİ yeni bir adla yeniden doğurur
    (`partiler.operator` → `tamir_rework.partiler_operator`). Hassasiyet miras alınmazsa
    üreteç, beyanı sessizce sıfırlar ve veri yeni adıyla prompt'a sızar — ölçülen vaka bu."""
    cols = [c for m in schema.get("models", []) for c in m["columns"]
            if c.get("name", "").endswith("_operator")]
    if not cols:
        pytest.skip("bu katalogda türev operatör kolonu yok")
    for c in cols:
        assert is_sensitive(c), f"{c['name']} hassasiyeti miras almamış: {c}"


def test_beyan_emniyet_agini_EZER():
    """Beyan her zaman kazanır — hem `person` demek hem de bir yanlış pozitifi geri almak
    için. (Ör. `stok_kart_no` gibi bir kolon `kart_no` ağına takılır ama kişisel değildir.)"""
    assert classify({"name": "operator"}) == "normal"                      # ağ yakalamaz
    assert classify({"name": "operator", "sensitivity": "person"}) == "person"
    assert classify({"name": "musteri_kart_no"}) == "person"               # ağ yakalar
    assert classify({"name": "musteri_kart_no", "sensitivity": "normal"}) == "normal"


def test_ozel_nitelikli_ayri_siniflanir():
    """KVKK md. 6 (özel nitelikli) ayrı ve daha katı bir rejime tabidir; tek bir 'hassas'
    bayrağı bu ayrımı kaybederdi."""
    assert classify({"name": "kan_grubu"}) == "special"
    assert classify({"name": "sendika_uyeligi"}) == "special"
    assert classify({"name": "tc_kimlik"}) == "person"


def test_uretici_listesi_TAM():
    """İkinci kapı: `URETICILER` listesi eksik kalırsa asıl test kör olur. Prompt üreten
    fonksiyonları kabaca tarayıp listenin dışında kalan var mı diye bakar."""
    import inspect
    import re

    aday = set()
    for mod in (llm, cube_router):
        for ad, fn in vars(mod).items():
            if not callable(fn) or not getattr(fn, "__module__", "").startswith("app."):
                continue
            try:
                kaynak = inspect.getsource(fn)
            except (OSError, TypeError):
                continue
            # "∈" işareti Dima'da YALNIZ prompt enum bloklarında kullanılıyor.
            if "∈" in kaynak and re.search(r"\bvalues\b|prompt_safe_values", kaynak):
                aday.add(f"{mod.__name__.split('.')[-1]}.{ad}")
    bilinen = {u[0].split(".")[-1] for u in URETICILER}
    eksik = {a for a in aday if a.split(".")[-1] not in bilinen}
    assert not eksik, (
        f"prompt enum'u üreten ama URETICILER listesinde OLMAYAN fonksiyon(lar): {sorted(eksik)} "
        "— listeye ekleyin, yoksa sızıntı testi onları denetlemez")
