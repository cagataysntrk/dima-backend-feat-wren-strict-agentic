"""🔴 `G6` — **KIYAS CEBİRİ**: mutlak kıyas → göreli kıyas indirgemesi.

Motor (`yoy.py`) zaten vardı; eksik olan cebirdi. *"Mart'ı şubat ile kıyasla"* sorusunun
cevabı **yeni bir motor** değil, *"mart cirosu + `mom`"* ifadesidir.

⚠ En kritik kural **fail-closed**: indirgeme **tam** değilse yapılmaz. Yaklaşık bir
kıyas, kıyas olmamaktan kötüdür — kullanıcı sayıya bakar, hangi iki dönemin
kıyaslandığına bakmaz.
"""

from __future__ import annotations

from app.kiyas_cebiri import indirge

_T = "tarih"


def _ara(g: str, l: str, *ek: dict) -> list[dict]:
    return [{"dimension": _T, "operator": "gte", "value": g},
            {"dimension": _T, "operator": "lte", "value": l}, *ek]


# --- İNDİRGENENLER ----------------------------------------------------------------


def test_BITISIK_IKI_AY_mom_olur():
    """🔴 Ölçülen kusurun tam vakası: *"mart cirosunu şubat ile kıyasla"* bugün
    `gte 2026-02-01` + `lte 2026-03-31` üretiyor — yani **iki ayın toplamı**."""
    sonuc = indirge(_ara("2026-02-01", "2026-03-31"))
    assert sonuc is not None
    filtreler, mode = sonuc
    assert mode == "mom"
    assert {(f["operator"], f["value"]) for f in filtreler} == {
        ("gte", "2026-03-01"), ("lte", "2026-03-31")}


def test_AYNI_AY_BIR_YIL_ARAYLA_yoy_olur():
    sonuc = indirge(_ara("2025-03-01", "2026-03-31"))
    assert sonuc is not None
    filtreler, mode = sonuc
    assert mode == "yoy"
    assert ("gte", "2026-03-01") in {(f["operator"], f["value"]) for f in filtreler}


def test_ARDISIK_IKI_YIL_yoy_olur():
    """*"2025 ile 2026 karşılaştır"* — ölçümde **hiç dönem filtresi olmadan**
    cevaplanan sınıfın kardeşi."""
    sonuc = indirge(_ara("2025-01-01", "2026-12-31"))
    assert sonuc is not None
    filtreler, mode = sonuc
    assert mode == "yoy"
    assert {(f["operator"], f["value"]) for f in filtreler} == {
        ("gte", "2026-01-01"), ("lte", "2026-12-31")}


def test_BAZ_DAIMA_GEC_OLAN_DONEM():
    """🔴 Yön kritiktir: `yoy.compute` bazı alıp **geriye** kaydırır. Cebir ters yöne
    bakarsa değişim yüzdesinin **işareti** ters çıkar — en sessiz yanlış türü."""
    filtreler, _ = indirge(_ara("2026-02-01", "2026-03-31"))
    gte = next(f for f in filtreler if f["operator"] == "gte")
    assert gte["value"].startswith("2026-03"), "baz geç dönem olmalı, erken değil"


def test_ZAMAN_DISI_FILTRELER_KORUNUR():
    """Kırılım/dışlama filtreleri indirgemeden **etkilenmez** — cebir yalnız zaman
    eksenine dokunur."""
    ek = {"dimension": "renk", "operator": "eq", "value": "Beyaz"}
    filtreler, _ = indirge(_ara("2026-02-01", "2026-03-31", ek))
    assert ek in filtreler
    assert len([f for f in filtreler if f["dimension"] == _T]) == 2


# --- 🔴 İNDİRGENMEYENLER — SINIR, KUSUR DEĞİL --------------------------------------


def test_UZAK_IKI_AY_INDIRGENMEZ():
    """*"ocak ve haziran karşılaştır"* — `mom` burada **yanlış** iki dönemi kıyaslardı
    (mayıs vs haziran). İndirgeme yok; soru `uyum` tarafından etiketli kalır."""
    assert indirge(_ara("2026-01-01", "2026-06-30")) is None


def test_IKI_YIL_ATLAYAN_ARALIK_INDIRGENMEZ():
    assert indirge(_ara("2024-01-01", "2026-12-31")) is None


def test_TEK_UCLU_ARALIK_INDIRGENMEZ():
    """Açık uçlu dönem (*"mart'tan beri"*) bir kıyas değildir."""
    assert indirge([{"dimension": _T, "operator": "gte", "value": "2026-03-01"}]) is None


def test_AY_SINIRINA_OTURMAYAN_ARALIK_INDIRGENMEZ():
    """*"15 Şubat – 20 Mart"* iki ay değil, bir penceredir."""
    assert indirge(_ara("2026-02-15", "2026-03-20")) is None


def test_FILTRESIZ_ve_BOZUK_GIRDI():
    assert indirge(None) is None
    assert indirge([]) is None
    assert indirge(_ara("bozuk", "2026-03-31")) is None


def test_TERS_ARALIK_INDIRGENMEZ():
    assert indirge(_ara("2026-03-31", "2026-02-01")) is None


def test_EQ_OPERATORU_INDIRGENMEZ():
    """`eq`/`in` bir aralık değildir — indirgeme **tanımsız**dır, uydurulmaz."""
    assert indirge([{"dimension": _T, "operator": "eq", "value": "2026-03-01"}]) is None


# --- MOTORLA UYUM -----------------------------------------------------------------


def test_MOTORUN_KAYDIRMASIYLA_TUTARLI():
    """🔴 Cebir ile motor **aynı** iki dönemi konuşmalı: indirgemenin ürettiği bazı
    `shift_period_back` geri kaydırınca, kullanıcının andığı **öteki** dönem çıkmalı.
    Ayrışırlarsa sistem bir kıyas gösterir ama **başka** bir kıyas hesaplar."""
    from app.cube_router import shift_period_back

    filtreler, mode = indirge(_ara("2026-02-01", "2026-03-31"))
    geri = shift_period_back(filtreler, mode, _T)
    assert {(f["operator"], f["value"]) for f in geri} == {
        ("gte", "2026-02-01"), ("lte", "2026-02-28")}


# --- 🔴 YETİM UÇ KAPANI — uçtan uca ------------------------------------------------


def test_UCTAN_UCA_KIYAS_CEVABI_DONUYOR(client):
    """🔴 **Bir alan üretmek, onu okuyan biri olmadan bir yetenek değil bir yalandır.**

    `route()` artık `compare` kurabiliyor; ama `_kiyas_cevabi`'nin iki çağıranı da
    `route_hit is None` dalındaydı. Bu bağlanmasaydı cevap **Mart toplamı** olur,
    `compare` sessizce yutulur ve üstelik `uyum` kapısı `compare` dolu diye ihlali
    **bastırırdı** — yani kapattığımız sessiz-yanlış sınıfının yeni bir örneği.

    ⚠ Kanıt **yapısaldır, veriye bağlı değil**: ilk yazım `columns` içinde
    `_gecen`/`_degisim` aradı ve demo veritabanında Mart 2026 satırı olmadığı için
    boş döndü — yani *"kapı çalışmıyor"* diye okunacak bir **veri yokluğu**. Bir
    bağlantının kurulduğunun kanıtı, o bağlantıdan geçen verinin varlığı değildir.
    """
    from tests.conftest import ask

    d = ask(client, "mart cirosunu şubat ile kıyasla")
    if d.get("source") not in ("cube", "cube+llm"):
        import pytest
        pytest.skip(f"⊘ bu soru cube yolundan dönmedi: {d.get('source')}")
    assert "mutlak kıyas" in " ".join(d.get("trace") or []), (
        f"🔴 kıyas dalı hiç koşmadı — `compare` yutulmuş: {d.get('trace')}")
    assert (d.get("cube_query") or {}).get("compare") == "mom", (
        f"🔴 kıyas cevaba taşınmamış: {d.get('cube_query')}")
    assert not d.get("eksik_niyet"), "kıyas kurulduysa eksik-niyet etiketi kalmamalı"


def test_AYIKLA_saf_ve_yikici_degil():
    """`ayikla` girdiyi **değiştirmez** — `route_hit` çağıranda hâlâ bütün olmalı."""
    from app.kiyas_cebiri import ayikla

    hit = {"cube_query": {"cube": "satis", "measures": ["m"], "compare": "mom"}}
    baz, mode = ayikla(hit)
    assert mode == "mom" and "compare" not in baz
    assert hit["cube_query"]["compare"] == "mom", "girdi bozuldu"
    assert ayikla({"cube_query": {"cube": "x"}}) is None
    assert ayikla(None) is None


# --- 🔴 `B-G4` — LLM YOLU DA KIYAS İFADE EDEBİLİR --------------------------------


def test_INTENT_SEMASINDA_compare_VAR(schema):
    """🔴 Borç `B-G4`: *"Intent-JSON'da `compare`/`blend` YOK → `5.6` (peer) BLOKE."*

    ⚠ `oneOf` yapısı **korunur** (§7.4/(c)): alan her cube'un KENDİ dalına eklenir,
    ortak bir üst gövdeye değil — yoksa reddetme dalı (`{cube: null}`) da `compare`
    kabul eder görünürdü.
    """
    from app.intent_semasi import cube_query_json_schema as kur

    index = {c["name"]: {"measures": list((c.get("measure_synonyms") or {}).keys()),
                         "dimensions": [], "time_dimensions": ["tarih"]}
             for c in schema["cubes"][:2] if c.get("measure_synonyms")}
    if not index:
        import pytest
        pytest.skip("⊘ ölçülü cube yok")
    s = kur(index)
    assert "oneOf" in s, "🔴 oneOf yapısı bozulmuş"
    zamanli = [d for d in s["oneOf"] if "compare" in (d.get("properties") or {})]
    assert zamanli, "🔴 zaman boyutlu dalda `compare` yok — LLM kıyası ifade edemez"
    assert zamanli[0]["properties"]["compare"]["enum"] == ["yoy", "mom"]
    red = next(d for d in s["oneOf"] if d.get("title") == "cevaplanamaz")
    assert "compare" not in (red.get("properties") or {}), (
        "🔴 reddetme dalı `compare` kabul ediyor — dal ayrımı delinmiş")


def test_PARSE_compare_ARTIK_DUSMUYOR(schema):
    """🔴 Şema izin verse bile `parse_cube_query` alanı **düşürüyordu**: LLM doğru cevabı
    üretse dahi kıyas mutfak kapısında ölürdü. *Bir alanı elle geri eklemek zorunda
    kalmak (`dashboards.py:187`), onun düşürülmemesi gerektiğinin kanıtıdır.*"""
    import json

    from app.cube_router import parse_cube_query

    c = next(c for c in schema["cubes"] if c.get("measure_synonyms"))
    olcu = list(c["measure_synonyms"].keys())[0]
    index = {c["name"]: {"measures": [olcu], "dimensions": [], "time_dimensions": []}}
    # ⚠ `parse_cube_query` **metin** alır, sözlük değil — imzayı varsaymak yerine okudum
    # (ilk yazım sözlük geçirdi ve `json.loads` sessizce `None` döndürdü: kapı kırmızı
    # verdi ama sebep koddaki bir kusur değil, TESTİN kendi hatasıydı).
    out = parse_cube_query(json.dumps(
        {"cube": c["name"], "measures": [olcu], "compare": "yoy"}), index)
    assert out and out.get("compare") == "yoy", f"compare düştü: {out}"
    kotu = parse_cube_query(json.dumps(
        {"cube": c["name"], "measures": [olcu], "compare": "uydurma"}), index)
    assert kotu and "compare" not in kotu, "🔴 tanımsız mod geçirildi — motor onu yutar"


def test_TOPN_ILE_KIYAS_SIRALAMAYI_KAYBETMIYOR(schema):
    """🔴 Ölçülen uç durum: *"en çok ciro yapan 5 müşteri mart ile nisanı kıyasla"* hem
    `compare=mom` hem `order`+`limit` taşır.

    `route()` `order`/`limit`'i **ayrı alanlar** olarak döner ve `ask()` onları `cq`'nun
    içine gömer (Gitaş logu 2026-07-24). Kıyas dalı o gömmeden **önce** çağrılırsa kıyas
    **sıralamasız ve limitsiz** hesaplanır — aynı kusurun ikinci kez doğuşu.
    *Bir alanı taşımak için yazılmış kodun üstünde durmak, onu taşımamaktır.*
    """
    from pathlib import Path

    from app import cube_router as cr

    metin = (Path(__file__).resolve().parents[1]
             / "app/routers/ask.py").read_text(encoding="utf-8")
    assert metin.index("kiyas_cebiri.ayikla") > metin.index(
        'cq = {**cq, "limit": route_hit["limit"]}'), (
        "🔴 kıyas dalı `order`/`limit` gömülmeden ÖNCE koşuyor — top-N'li bir kıyas "
        "sorusu sıralamasını kaybeder")

    hit = cr.route(cr._norm("en çok ciro yapan 5 müşteri mart ile nisanı kıyasla"), schema)
    if hit is None:
        import pytest
        pytest.skip("⊘ vaka bayat")
    if (hit.get("cube_query") or {}).get("compare"):
        assert hit.get("order") or hit.get("limit"), "⊘ vaka artık top-N taşımıyor"


def test_KIYAS_CHIPI_MOM_KIPINI_TANIYOR():
    """🔴 `DA-9` — chip `=== "yoy"` sabit kodluydu; `kiyas_cebiri` `mom` de üretiyor.

    Kusur iki katlıydı: `mom` aktifken chip **"kapalı"** gösteriyordu **ve** tıklayınca
    kullanıcının kıyasını **sessizce `yoy`'a çeviriyordu** — bir gösterge, kapatmaya
    çalıştığı şeyi DEĞİŞTİRİYORDU.

    *Bir anahtarın yalnız bir değeri tanıması, öteki değeri yok saymak değil BOZMAKTIR.*
    """
    import pathlib

    fe = (pathlib.Path(__file__).resolve().parents[2]
          / "dima-frontend-demo-master/src/components/InterpretationBar.tsx")
    if not fe.exists():
        import pytest
        pytest.skip("⊘ frontend mount edilmemiş")
    src = fe.read_text(encoding="utf-8")
    assert 'mod === "yoy" || mod === "mom"' in src, (
        "🔴 kıyas chip'i `mom` kipini tanımıyor — backend üretiyor, ekran görmüyor")
    assert '"geçen aya göre"' in src, "🔴 `mom` için etiket yok"
