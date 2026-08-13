"""FAZ 6 (§4.5) — OFFLINE sinonim önericisi: LLM taslak üretir, OTORİTE İNSANDA kalır.

## Doldurduğu boşluk

`mdl_writer` bilerek *"TAHMİNİ sinonim UYDURULMAZ"* diyor — doğru bir karar, çünkü tahmini
bir sinonim `route()`'un **canlı** davranışını değiştirir. Ama sonuç **çıplak** bir cube:
tablo adından başka etiketi yok, `route()` onu neredeyse hiç eşleştiremez. §2.1'in ölçtüğü
darboğaz tam bu: **mekanizma üretiliyor, sözlük üretilmiyor.**

## LLM'in meşru olduğu TEK yer

**Offline, insan-onaylı öneri.** Bu dosyanın kilitlediği üç şey:

1. Öneri **hiçbir `/ask` yolundan** tetiklenmez.
2. Çıktı **doğrudan yazılmaz** — `SynonymOverride(approved=False)` kuyruğuna aday düşer.
3. `approved=False` **sabittir**, parametre değil: açılsaydı bir çağıran `True` geçer ve
   LLM önerisi **insan görmeden canlıya inerdi** — modülün tüm gerekçesi çökerdi.

K1'in *"yapı ≠ güven"* ayrımının offline karşılığı.

## Dikey modüller (`packs/modul/muhasebe|satis`) — ÖLÇÜLDÜ, YAZILMADI

Plan: *"Faz 0'ın verisi **sırayı söyler**."* Faz 0 ölçtü: `interaction_log` **0 satır** —
**sıra girdisi YOK**. Ve muhasebe ailesi demo katalogda **zaten var** (`mizan` · `cari` ·
`statements`). Sırasız ve kaynak tablosuz cube yazmak, planın sektör küpleri için açıkça
yasakladığı **spekülasyonun** aynısı olurdu. Kayıt: §6.10z.
"""

from __future__ import annotations

import inspect
import json

from app import sinonim_onerici as so


class _LLM:
    def __init__(self, cikti):
        self.cikti, self.cagrildi = cikti, []

    def sinonim_oner(self, teknik_ad, baglam=""):
        self.cagrildi.append((teknik_ad, baglam))
        return self.cikti


# --- ÜÇ DEĞİŞMEZ ------------------------------------------------------------------

def test_APPROVED_FALSE_sabittir_parametre_DEGIL():
    """Açılsaydı bir çağıran `True` geçer ve LLM önerisi İNSAN GÖRMEDEN canlıya inerdi."""
    sig = inspect.signature(so.kuyruga_koy)
    assert "approved" not in sig.parameters, \
        "`approved` dışarı açılmış — LLM önerisi onaysız canlıya inebilir"
    assert "approved=False," in inspect.getsource(so.kuyruga_koy)


def test_HICBIR_ASK_YOLUNDAN_cagrilmiyor():
    """Çalışma-anı sorgu yoluna ASLA girmez — planın literal şartı (`E-8`).

    ⟳🔴 **GÜÇLENDİRİLDİ 2026-08-13 — kapı bir KELİMEYİ ölçüyordu, bir ÇAĞRIYI değil.**

    ⊙ Ölçüldü: `FAZ 8`'de yazılan `app/hasat.py`, kuyruğun sahibini **açıklamasında**
    andı (*«yazan `sinonim_onerici.kuyruga_koy`'dur… ikinci bir hat kurulmadı»*) ve
    kapı **kırmızı** verdi — oysa dosyada o modüle **hiçbir çağrı yok**. 🅞 *Sözü
    değil kullanımı ara.*

    ⚠ **Zayıflatılmadı, KESİNLEŞTİRİLDİ:** metin araması bir **dinamik** sızıntıyı da
    yakalıyordu (`importlib.import_module("sinonim_onerici")` gibi bir dize). Bu yüzden
    yalnız `ast` ile *«import/çağrı var mı»* diye bakmak **yetmezdi** ②. Çözüm ikisini
    birden tutmak: **docstring'ler ayıklanır**, kalan kod (dize sabitleri **dâhil**)
    yine metin olarak aranır. Böylece bir açıklama kapıyı kırmaz, bir dize sızıntısı
    hâlâ kırar.

    *Bir yasağı ölçen kapı, yasağın kendisinden fazlasını yasaklıyorsa, bir gün onu
    doğru dürüst yazan kişiyi durdurur.*
    """
    import pathlib

    from tests._kod_ayikla import kodu_ayikla as _kodu_ayikla

    app_dir = pathlib.Path(inspect.getfile(so)).parent
    for f in app_dir.rglob("*.py"):
        if f.name in ("sinonim_onerici.py",):
            continue
        try:
            kod = _kodu_ayikla(f.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:                                    # pragma: no cover
            kod = f.read_text(encoding="utf-8", errors="ignore")
        assert "sinonim_onerici" not in kod, \
            f"{f.name} offline öneriyi çağırıyor — çalışma-anı yoluna sızmış olabilir"


def test_KAYNAK_ayri_tutuluyor():
    """`manual` (insan) ve `mined` (deterministik) ile AYNI kutuya koymak, onaylayanın
    önerinin nereden geldiğini görmesini engellerdi — bir LLM önerisi bir insan girdisiyle
    aynı güvene sahip DEĞİLDİR."""
    assert 'source="llm_oneri"' in inspect.getsource(so.kuyruga_koy)


# --- ÇIKTI TEMİZLİĞİ: gürültü onaylayanı yorar ------------------------------------

def test_BOZUK_cikti_BOS_liste():
    for ham in ("bu JSON değil", "", "null", '{"a":1}', "[1,2,3]"):
        assert so.oner(_LLM(ham), "x") == [] or all(
            isinstance(s, str) for s in so.oner(_LLM(ham), "x"))


def test_SAGLAYICI_YOKSA_bos():
    class _Kuralli:
        pass

    assert so.oner(_Kuralli(), "ciro_tl") == []
    assert so.oner(None, "ciro_tl") == []


def test_PATLARSA_bos():
    class _Patlak:
        def sinonim_oner(self, *a, **k):
            raise RuntimeError("yok")

    assert so.oner(_Patlak(), "ciro_tl") == []


def test_TEMIZ_cikti_ve_SINIR():
    ham = json.dumps(["Ciro", "hasılat", "ciro", "x", "gelir", "satış", "tutar",
                      "kazanç", "fazladan"])
    out = so.oner(_LLM(ham), "ciro_tl")
    assert len(out) <= so.MAKS_ONERI, "uzun liste onaylayanı 'hepsini kabul et'e iter"
    assert out == [s.lower() for s in out] and len(out) == len(set(out))
    assert "x" not in out, "tek harflik gürültü elenmedi"


def test_BOS_ONERI_kuyruga_YAZILMAZ():
    class _S:
        def __init__(self):
            self.eklenen = []

        def add(self, x):
            self.eklenen.append(x)

    s = _S()
    assert so.kuyruga_koy(s, cube="c", field_kind="measure", field_name="m",
                          synonyms=[]) is None
    assert not s.eklenen


# --- ÇIPLAK ALAN HEDEFLEMESİ ------------------------------------------------------

def test_YALNIZ_CIPLAK_alanlara_oneri():
    """Zaten sinonimi olan bir alana öneri üretmek, küratörlü sözlüğü gürültüyle
    sulandırırdı."""
    cube = {"name": "veri", "display": "yüklenen veri",
            "measures": ["ciro_tl", "adet"],
            "measure_synonyms": {"ciro_tl": ["ciro", "hasılat", "gelir"],  # ZENGİN
                                 "adet": ["adet"]},                        # ÇIPLAK
            "dimensions": [], "dimension_synonyms": {}}
    llm = _LLM('["sayı", "miktar"]')
    out = so.ciplak_cube_icin(llm, cube)
    assert "adet" in out and "ciro_tl" not in out, f"zengin alana öneri üretildi: {out}"
    assert [a for a, _ in llm.cagrildi] == ["adet"]


def test_PROMPT_uydurmayi_yasakliyor():
    from app import llm as llm_mod

    s = llm_mod._sinonim_system()
    assert "UYDURMA" in s
    assert "boş dizi döndürmek yanlış öneriden İYİDİR" in s


def test_FAILOVER_tasiyor_KURAL_TABANLI_tasimiyor():
    from app import llm as llm_mod

    assert hasattr(llm_mod.FailoverSqlGenerator, "sinonim_oner")
    assert not hasattr(llm_mod.RuleBasedSqlGenerator, "sinonim_oner")


# --- COMPOSE KAPISI: onaysız aday CANLIYA İNMEZ ------------------------------------

def test_HER_OKUYAN_ONAY_kapisini_uyguluyor():
    """Bu modülün tüm güvenliği bu kapıya dayanıyor (ADR-0018 1e) — **bir** okuyan bile
    kapıyı atlarsa onaysız öneri canlıya iner.

    ⟳ Testin ilk hâli `compose.py`'ye bakıyordu ve **kırıldı** — kapı orada değil,
    `materialize.py` ve `wren_service.py`'de. Yanlış dosyaya bakan bir kapı, kapı DEĞİLDİR:
    yeşil kalır ve hiçbir şeyi korumaz. Artık **SynonymOverride'ı okuyan HER dosya**
    taranıyor, yeri varsayılmıyor."""
    import pathlib
    import re

    app_dir = pathlib.Path(inspect.getfile(so)).parent
    kok = app_dir.parent
    okuyanlar = []
    for f in list(kok.rglob("*.py")):
        if "test" in f.parts or f.name == "sinonim_onerici.py":
            continue
        metin = f.read_text(encoding="utf-8", errors="ignore")
        # SEÇME (select) ifadesinde geçiyorsa okuyor demektir; yalnız import/yorum sayılmaz.
        if re.search(r"select\([^)]*SynonymOverride", metin, re.S):
            okuyanlar.append((f, metin))

    assert okuyanlar, "SynonymOverride'ı okuyan bulunamadı — test bayat"
    # MUAF OLANLAR ve GEREKÇELERİ — muafiyet listesi kısa ve gerekçeli olmalı, yoksa
    # kapı kendiliğinden erir.
    muaf = {
        "synonyms.py": "admin ONAY EKRANI — adayları GÖRMEK için okur",
        "seed.py": "idempotans kontrolü — 'bu aday zaten var mı' diye bakar, "
                   "canlıya bir şey İNDİRMEZ",
    }
    for f, metin in okuyanlar:
        if f.name in muaf:
            continue
        assert "SynonymOverride.approved" in metin, (
            f"{f.name} SynonymOverride okuyor ama ONAY kapısını uygulamıyor — "
            "onaysız bir LLM önerisi canlıya inebilir")
