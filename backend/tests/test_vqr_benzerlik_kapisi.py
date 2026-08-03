"""CANLI TUR — §1.7'nin riski GERÇEK çıktı ve plandakinden DAHA KÖTÜ.

## Ölçülen vaka (2026-08-03, gerçek konteyner)

Kullanıcı *"geçen ay toplam **FİRE**"* sordu. VQR embedding benzerliğiyle *"geçen ay
toplam **CİRO**"* kaydını eşleştirdi ve `SELECT SUM(ciro_tl)` döndürdü — `source="vqr"`,
`confidence=0.95`, *"önceden doğrulanmış sorgu"* rozetiyle. **Sorulanın ZIDDI bir ölçü.**

İki soru **tek kelime** farklıydı ve o kelime **ölçünün kendisiydi**: beş token'ın dördü
eşleşince kosinüs 0,92 eşiğini aşıyor. Embedding için bu bağlamda "fire" ile "ciro"
neredeyse aynı; **anlamca zıt** oldukları görülmüyor.

## Faz 2b'nin kararı doğruydu ama YETERSİZDİ

`auto_cube`'u replay'den çıkarmak doğru bir karardı — ama bu kayıt **`user_verified`**'dı,
yani **insan onaylıydı**. Risk kaynağın güveninde değil, **benzerlik eşiğinin kendisinde**.
Plan §1.7'yi *"auto_cube güven listesinde"* diye çerçevelemişti; ölçüm çerçeveyi genişletti.

## Kural (ADR-0008'in "deterministik-önce"si, merdivene uygulanmış)

* **BİREBİR** (normalize) eşleşme → replay **KALIR**. Aynı soruyu ikinci kez soran
  kullanıcı aynı cevabı hak eder; burada tahmin yok.
* **BENZERLİK** eşleşmesi → `route()` bir cevap üretebiliyorsa **o kazanır**. Deterministik
  ve tam bir cevap, olasılıksal ve yaklaşık bir eşleşmeye tercih edilir.
* `route()` çözemezse benzerlik kaydı **yine devreye girer** — kapsam kaybedilmez, yalnız
  **sıra** düzeltilir.

## Neden hiçbir test yakalamamıştı

CI `DIMA_VQR_EMBEDDER=off` koşuyor → benzerlik eşiği **leksik** (0,85) ve seed'siz bir
depoda hiç tetiklenmiyor. Risk yalnız **embedder AÇIK + depoda kayıt VARKEN** görünür —
yani canlı ortamda. Faz 0.5'in VQR senaryosu bu yüzden *"replay tetiklenmedi"* demişti ve
ben onu **riski çürütmez** diye kaydetmiştim; doğru kayıtmış.
"""

from __future__ import annotations

import inspect

from app.routers import ask as ask_mod


def test_BENZERLIK_esleşmesi_ROUTEa_yeniliyor():
    """Kapının kendisi: benzerlik eşleşmesi geldiğinde `route()` denenmeli."""
    kaynak = inspect.getsource(ask_mod)
    i = kaynak.index("cached = vqr.near_exact(")
    pencere = kaynak[i:i + 2600]
    assert 'cube_router._norm(cached.get("question")' in pencere, \
        "birebir/benzerlik AYRIMI yapılmıyor — her replay aynı muameleyi görüyor"
    assert "cube_router.route(" in pencere, \
        "benzerlik eşleşmesinde route() DENENMİYOR"
    assert "cached = None" in pencere, "route() kazandığında kayıt bırakılmıyor"


def test_BIREBIR_tekrar_KORUNUYOR():
    """Kapı fazla geniş olmamalı: aynı soruyu tekrar soran kullanıcı replay'i hak eder.
    Koşul `!=` ile yazılmış — yani birebir eşleşmede blok HİÇ çalışmaz."""
    kaynak = inspect.getsource(ask_mod)
    i = kaynak.index("cached = vqr.near_exact(")
    pencere = kaynak[i:i + 2600]
    assert '!= q_norm' in pencere, \
        "birebir eşleşme de atlanıyor olabilir — replay tamamen ölür"


def test_ROUTE_cozemezse_KAYIT_yine_kullanilir():
    """Kapsam KAYBEDİLMEZ: `route()` `None` dönerse benzerlik kaydı devrede kalır."""
    kaynak = inspect.getsource(ask_mod)
    i = kaynak.index("cached = vqr.near_exact(")
    pencere = kaynak[i:i + 2600]
    assert "if _det:" in pencere, \
        "route() sonucu KOŞULSUZ uygulanıyor — çözemediğinde de kayıt atılıyor olabilir"


def test_ATLAMA_LOGLANIYOR():
    """Sessiz bir atlama, sessiz bir replay kadar kötüdür: hangi kaydın neden atlandığı
    görünmeli."""
    kaynak = inspect.getsource(ask_mod)
    assert "VQR benzerlik eşleşmesi ATLANDI" in kaynak


def test_FAZ_2b_karari_KORUNUYOR():
    """Bu düzeltme Faz 2b'nin kararının YERİNE geçmez, ÜSTÜNE biner: `auto_cube` hâlâ
    doğrudan replay edilemez."""
    from app import vqr as vqr_mod

    assert not vqr_mod.is_trusted("auto_cube")
    assert "auto_cube" in vqr_mod._FEW_SHOT_ONLY_SOURCES


def test_SEED_senaryo_fixtureleri_VAR():
    """Bu riski görünür kılan şey seed'in VQR ÇİFTİYDİ (aynı yapı, farklı kaynak).
    Fixture olmadan depo boş kalır ve replay yolu **hiç** koşmaz — yani test ortamı
    'yeşil' görünür ve hiçbir şey ölçmez."""
    from control_plane import seed

    govde = inspect.getsource(seed._senaryo_fixtureleri)
    assert "user_verified" in govde and "auto_cube" in govde

    # ⚠️ İlk sürüm `'replace("demo-"' not in govde` diyordu ve KENDİ YORUMUMDAKİ
    # tarihçe alıntısını yakalıyordu. Yorum bir davranış değildir — ölçülmesi gereken
    # ATAMANIN kendisi. (Bu oturumda üçüncü kez bir testim metni davranış sandı.)
    atama = [s.strip() for s in govde.splitlines()
             if s.strip().startswith("sirket =")]
    assert atama == ["sirket = tenant.slug"], (
        f"şirket kapsamı TAHMİN ediliyor ({atama}) — fixture'lar `settings.company` ile "
        "eşleşmez ve replay yolu sessizce hiç koşmaz")


# --- İKİNCİ KAPI: route() çözemediğinde de koru ----------------------------------

def test_OLCU_TUTARLILIK_kapisi_VAR(schema):
    """Deterministik-önce kuralı bir HAFİFLETMEDİR: yalnız `route()` cevap üretebildiğinde
    korur. Ölçülen boşluğun (~%31) içinde `route()` çözemez ve benzerlik kaydı YİNE cevap
    olur — *"fire → ciro"* vakasının mümkün kaldığı yer tam orası."""
    kayit = {"question": "geçen ay toplam ciro",
             "cube_query": {"cube": "parti", "measures": ["toplam_ciro"]}}
    # Soru ölçüyü AÇIKÇA adlandırıyor ve kayıt BAŞKA ölçü taşıyor → replay REDDEDİLMELİ
    assert not ask_mod._vqr_olcu_tutarli(
        cr_norm := __import__("app.cube_router", fromlist=["x"])._norm("gecen ay toplam fire"),
        kayit, schema), "ölçü tutarsız bir kayıt replay edilebiliyor"
    # Aynı ölçü → replay SERBEST
    assert ask_mod._vqr_olcu_tutarli(
        __import__("app.cube_router", fromlist=["x"])._norm("gecen ay toplam ciro"),
        kayit, schema)
    assert cr_norm


def test_OLCU_ADLANDIRILMAMISSA_kapi_KARISMAZ(schema):
    """Fazla dar bir kapı kapsamı gerekçesiz keserdi: soru ölçü adlandırmıyorsa
    tutarsızlık İDDİA EDİLEMEZ."""
    kayit = {"question": "geçen ay toplam ciro",
             "cube_query": {"cube": "parti", "measures": ["toplam_ciro"]}}
    from app import cube_router as cr

    assert ask_mod._vqr_olcu_tutarli(cr._norm("gecen ayki durum nedir"), kayit, schema)


def test_HAM_SQL_kaydina_KARISMAZ(schema):
    """Ham SQL kaydının ölçü İDDİASI yoktur — kapı ona karışmaz (sürüm kapısı ilgilenir)."""
    assert ask_mod._vqr_olcu_tutarli(
        "x", {"cube_query": {"wren_sql": "SELECT 1"}}, schema)


def test_PROVENANCE_SORU_chip_tiklamada_KORUNUYOR():
    """Faz 3b'nin makbuz izi. Beyaz liste bunu düşürseydi chip tıklandığı an iz KOPARDI —
    `adhoc_id` için düzeltilen kusurun AYNISI, farklı alanda."""
    import json

    from app import cube_router as cr

    index = {"parti": {"measures": ["toplam_ciro"], "dimensions": [], "time_dimensions": []}}
    cq = cr.parse_cube_query(json.dumps({
        "cube": "parti", "measures": ["toplam_ciro"],
        "provenance_soru": {"question_original": "hasılatımız",
                            "question_normalized": "ciro"}}), index)
    assert cq.get("provenance_soru", {}).get("question_original") == "hasılatımız"
