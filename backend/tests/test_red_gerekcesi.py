"""FAZ 0 — RED GEREKÇESİ: `route()` hangi dalda pes etti, artık SAYILABİLİR.

## Neden bu ölçüm Faz 0'ın asıl değeri

`cube_router.route()` **on ayrı yerde** `None` döner. Bugüne kadar hangisinde pes ettiği
yalnız `trace` metninde ve `source=None`'da görünüyordu — **sayısal olarak gruplanamıyordu**.

Planın §2.3 tezi tam bu: *"çoğu soru LLM'e gidiyor"* bir **hipotez**, ölçüm değil.
Deterministik tavanın **%64** olduğu ölçüldü ama kalan **%36'nın nasıl dağıldığı**
bilinmiyor — netleştirme chip'i mi, Intent-JSON mu, Discovery mi? Plan bunu şöyle yazıyor:

> *"Bu olmadan diğer üç kaldıracın hiçbiri önceliklendirilemez."*

## Neden ContextVar, neden imza değişmedi

`route()`'un beş çağıranı var. Dönüş tipini `tuple`a çevirmek hepsini kırar ve gerekçeyi
zincirin her katmanından elle taşıtırdı. Bu deponun **kanıtlanmış** çözümü var:
`app/llm.py`'nin `_llm_usage_var` + `reset/record/get` kalıbı tam bu şekli çözüyor.
Yeni bir mekanizma **icat edilmedi**, var olan kalıp ikinci kez kullanıldı.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from app import cube_router as cr

ROUTER = pathlib.Path(__file__).resolve().parents[1] / "app/cube_router.py"


def _route_govdesi() -> list[str]:
    src = ROUTER.read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(src) if l.startswith("def route("))
    end = next(i for i in range(start + 1, len(src))
               if src[i].startswith("def ") or src[i].startswith("@"))
    return src[start:end]


# --- YAPISAL: her dal etiketli, kodlar TAM ve SIRALI -----------------------------

def test_HER_return_None_dali_ETIKETLI():
    """Etiketsiz bir dal, telemetride **görünmez bir kayıp** demektir: soru deterministik
    yoldan çıkamamıştır ama nedeni sayılamaz. Bu testin varlık sebebi, yeni bir `return
    None` eklendiği gün sessizce etiketsiz kalmasını engellemektir."""
    govde = _route_govdesi()
    etiketsiz = []
    for i, l in enumerate(govde):
        if l.strip().startswith("return None"):
            onceki = govde[i - 1].strip() if i else ""
            if not onceki.startswith('_reddet("R'):
                etiketsiz.append(f"{l.strip()[:70]}")
    assert not etiketsiz, ("etiketsiz `return None` dalı:\n  " + "\n  ".join(etiketsiz))


def test_KODLAR_TAM_ve_SIRALI():
    """R1…RN kesintisiz ve konum sırasında olmalı. İlk denememde yorumlu `return None`
    satırları atlanınca numaralandırma **konum sırasıyla eşleşmedi** — R kodları
    telemetride gruplama anahtarıdır; kayarsa geçmiş veri anlamsızlaşır."""
    kodlar = re.findall(r'_reddet\("(R\d+)"\)', "\n".join(_route_govdesi()))
    assert kodlar == [f"R{i}" for i in range(1, len(kodlar) + 1)], (
        f"kodlar sırasız/kesintili: {kodlar}")
    assert len(kodlar) == 10, f"{len(kodlar)} dal etiketli (plan 10 diyor — §2.4)"


def test_RED_KODLARI_sozlugu_dallarla_ORTUSUYOR():
    """Kod → gerekçe sözlüğü koddaki dallarla birebir eşleşmeli; aksi halde telemetri
    ham `R7` gösterir ve kimse ne olduğunu bilmez."""
    kodlar = set(re.findall(r'_reddet\("(R\d+)"\)', "\n".join(_route_govdesi())))
    assert kodlar == set(cr.RED_KODLARI), (
        f"kodda var/sözlükte yok: {sorted(kodlar - set(cr.RED_KODLARI))} · "
        f"sözlükte var/kodda yok: {sorted(set(cr.RED_KODLARI) - kodlar)}")
    for kod, metin in cr.RED_KODLARI.items():
        assert len(metin) >= 10, f"{kod} gerekçesi çok kısa — telemetriyi okuyan anlamalı"


def test_IMZA_DEGISMEDI():
    """Beş çağıran var; imza değişseydi hepsi kırılırdı. Kalıp `llm.py`'den alındı —
    yeni bir mekanizma icat edilmedi.

    ⟳ **2026-08-03 (Faz 2a-5) — testin İDDİASI keskinleştirildi, gevşetilmedi.**
    Eskiden `list(sig.parameters) == ["question", "schema"]` deniyordu. Korunmak istenen
    şey **çağıranların kırılmaması**; varsayılanı olan **anahtar-kelime** argümanı bunu
    bozmaz ama harfi harfine iddia onu da yasaklıyordu. Artık gerçek değişmez kilitli:

      * konumsal parametreler **aynen** `question, schema` — sırası/adı değişemez
      * eklenen her parametre **KEYWORD_ONLY** ve **varsayılanı olmalı**
        (yoksa mevcut çağrılar kırılır — testin asıl derdi buydu)
    """
    import inspect

    sig = inspect.signature(cr.route)
    konumsal = [a for a, p in sig.parameters.items()
                if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    assert konumsal == ["question", "schema"], f"konumsal imza değişti: {konumsal}"
    for ad, p in sig.parameters.items():
        if ad in konumsal:
            continue
        assert p.kind is p.KEYWORD_ONLY, f"{ad} konumsal eklenmiş — çağıranlar kırılır"
        assert p.default is not inspect.Parameter.empty, \
            f"{ad} varsayılansız — mevcut çağrılar kırılır"
    assert "contextvars" in ROUTER.read_text(encoding="utf-8")


# --- DAVRANIŞ: gerçekten doğru dal işaretleniyor mu? ------------------------------

def test_BASARILI_route_gerekce_BIRAKMAZ(schema):
    """`route()` cevabı ürettiyse `reject_reason` NULL kalmalı — kolonun DOLULUĞU
    doğrudan "deterministik yoldan çıkamayan sorular" kümesini verir."""
    hit = cr.route("bu yıl toplam ciro", schema)
    if hit:                                   # katalog bu soruyu çözebiliyorsa
        assert cr.red_gerekcesi() is None


# Ölçülmüş vakalar (2026-08-02, demo-boyahane) — TAHMİN DEĞİL. İlk sürümde
# "zxqw plmk asdf" için R10 beklemiştim; gerçekte **R1** çıkıyor çünkü hiçbir cube
# eşleşmiyor ve kapsam kapısına SIRA GELMİYOR. Dal SIRASI anlamlıdır ve test onu
# ölçüme göre kilitler, sezgiye göre değil.
_OLCULEN = [
    ("bu yıl ciro zxqwplmk",       "R10", "cube eşleşti ama tanınmayan kelime kaldı"),
    ("merhaba nasilsin",           "R1",  "hiç cube eşleşmedi — kapsam kapısına sıra gelmez"),
    ("zxqw plmk asdf",             "R1",  "aynı: R10 DEĞİL"),
    ("makine bazında ciro dökümü", "R2",  "liste/döküm politikası — Faz 2a'nın hedefi"),
    ("ortalama ciro",              "R5",  "ortalama ölçü tanımlı değil"),
    ("zzz bazında ciro",           "R9",  "kırılım istendi ama boyut eşleşmedi"),
]


@pytest.mark.parametrize("soru,kod,neden", _OLCULEN)
def test_OLCULEN_DALLAR_dogru_kodu_uretiyor(schema, soru, kod, neden):
    """Mekanizma yapısal olarak doğru olsa bile YANLIŞ dalı işaretleyebilir. Bu vakalar
    çalıştırılarak ölçüldü; telemetriyi okuyan kişi kodun ne anlama geldiğine güvenebilmeli."""
    assert cr.route(soru, schema) is None, f"{soru!r} artık cevap üretiyor — vaka bayat"
    assert cr.red_gerekcesi() == kod, f"{soru!r} → {kod} bekleniyordu ({neden})"


def test_DAL_SIRASI_R1_R10_dan_ONCE(schema):
    """R1 (cube eşleşmedi) R10'dan (kapsam kapısı) ÖNCE gelir. Bu bir kusur değil bir
    SIRA: hiçbir cube tanınmıyorsa kapsamı ölçmenin anlamı yok. Telemetriyi okuyan bunu
    bilmeli — yoksa "R1 çok yüksek" görüp yanlış kaldıraca yatırım yapar."""
    cr.route("zxqw plmk asdf", schema)
    assert cr.red_gerekcesi() == "R1"
    cr.route("bu yıl ciro zxqwplmk", schema)
    assert cr.red_gerekcesi() == "R10"


def test_SIFIRLAMA_onceki_cagriyi_TASIMAZ(schema):
    """Her `route()` çağrısı kendi gerekçesini üretir; bir öncekinin kalıntısı
    telemetriye YANLIŞ bir dal yazdırırdı."""
    cr.route("zxqw plmk asdf", schema)
    assert cr.red_gerekcesi() == "R1"
    hit = cr.route("bu yıl toplam ciro", schema)
    assert hit, "vaka bayat: bu soru artık cevap üretmiyor"
    assert cr.red_gerekcesi() is None, "önceki reddin kalıntısı taşındı"


def test_KOVA_KURULMADAN_cagri_PATLAMAZ():
    """`llm.py`'nin aynı davranışı: eval/test/iç sonda çağrılarında kova kurulmamış
    olabilir — sessizce atlanmalı, akış kırılmamalı."""
    cr.reddi_sifirla()
    cr._reddet("R3")
    assert cr.red_gerekcesi() == "R3"


# --- TELEMETRİ: kolon gerçekten yazılıyor mu? ------------------------------------

def test_INTERACTION_LOG_kolonu_VAR():
    from control_plane.models import InteractionLog

    assert "reject_reason" in InteractionLog.model_fields


def test_ANSWER_zinciri_gerekceyi_YAZIYOR():
    """Kolonu eklemek yetmez — kapanış zinciri onu DOLDURMALI. `_log_interaction`
    `seal()`'in parçası, yani her cevap yolu bundan geçer."""
    import inspect

    from app import answer

    govde = inspect.getsource(answer._log_interaction)
    assert "reject_reason=" in govde, "kolon yazılmıyor"
    assert "red_gerekcesi" in govde, "gerekçe `cube_router`'dan okunmuyor"


def test_MIGRATION_var():
    """Kolon bir migration olmadan üretime çıkamaz."""
    mig = (pathlib.Path(__file__).resolve().parents[1] / "migrations/versions").glob("*.py")
    metin = "\n".join(f.read_text(encoding="utf-8") for f in mig)
    assert "reject_reason" in metin and "interaction_log" in metin


def test_NOTE_kolonuna_SIKISTIRILMADI():
    """`note` serbest METİNDİR ve `mine_candidates` onu zaten başarısızlık açıklaması
    olarak okuyor. Sabit bir kodu oraya sıkıştırmak iki farklı anlamı tek alana yığar ve
    ikisini de sorgulanamaz yapardı — plan bunu açıkça yasaklıyor."""
    import inspect

    from app import answer

    govde = inspect.getsource(answer._log_interaction)
    assert "note=resp.note" in govde, "`note` başka bir amaçla ezilmiş"


# --- ENVANTER ARACI ---------------------------------------------------------------

def test_ENVANTER_araci_UC_BOLUM_uretir():
    """Planın Faz 0 çıktısı üç sayı: dağılım · en sık 20 red gerekçesi · auto_cube
    yanlış-oranı. Araç veri yokken de ÇALIŞMALI ve "veri yok" demeli — çökmemeli."""
    import importlib.util

    yol = pathlib.Path(__file__).resolve().parents[1] / "lab/telemetri_envanteri.py"
    spec = importlib.util.spec_from_file_location("telemetri_envanteri", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    d = mod.topla(gun=14)
    assert set(d) >= {"kaynak_dagilimi", "red_gerekceleri", "auto_cube", "olculdu"}


def test_ENVANTER_auto_cube_ORANI_UYDURMAZ():
    """§1.7'nin eleştirisi tam olarak *"yapısal geçerlilik ≠ semantik doğruluk"*.
    Araç otomatik bir "doğruluk oranı" üretseydi, eleştirdiği hatayı tekrarlardı —
    örneklem ÇIKARIR, kararı insana bırakır (plan: *"örneklem doğru/yanlış diye
    DENETLENİR"*)."""
    yol = pathlib.Path(__file__).resolve().parents[1] / "lab/telemetri_envanteri.py"
    kaynak = yol.read_text(encoding="utf-8")
    assert "denetim_orneklemi" in kaynak
    assert "yanlış-oranı BU ARAÇ HESAPLAMAZ" in kaynak


@pytest.mark.parametrize("kod", ["R1", "R5", "R10"])
def test_KODLAR_STABIL_KALMALI(kod):
    """R kodları telemetride gruplama anahtarıdır — metin değişebilir, KOD değişemez.
    Değişirse geçmiş veri yeni veriyle kıyaslanamaz hale gelir."""
    assert kod in cr.RED_KODLARI
