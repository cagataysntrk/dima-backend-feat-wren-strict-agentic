"""FAZ 1.5 — **METRİK SERTİFİKASYONU** kapısı (B8).

`source=cube` rozeti *"deterministik bir yoldan geldi"* der — doğru ama yetersiz.
Cevaplamadığı soru: *"bu metriğin tanımını **kim onayladı**, ve o onaydan beri **tanım
değişti mi**?"* Bir metrik **doğru hesaplanıp yanlış tanımlanmış** olabilir; determinizm
onu yakalamaz.
"""

from __future__ import annotations

import pathlib
from datetime import datetime, timedelta, timezone

import pytest

from app import certification as C

KOK = pathlib.Path(__file__).resolve().parents[1]
FE = KOK.parent / "dima-frontend-demo-master" / "src"

_TANIM = {"expression": "SUM(fire_kg)", "unit": "kg", "additive": True}
_KOKEN = {"olculer": [{"kaynak": "partiler", "ad": "toplam_fire"}],
          "boyutlar": [{"kaynak": "makineler", "ad": "makine_adi"}]}


def _sertifika(**kw):
    return {"seviye": "sertifikali",
            "definition_hash": C.tanim_hash(_TANIM),
            "lineage_set_hash": C.koken_hash(_KOKEN),
            "son_gecerlilik": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
            **kw}


def _durum(**kw):
    return C.durum(_sertifika(**kw), tanim=C.tanim_hash(_TANIM), koken=C.koken_hash(_KOKEN))


# ── 1 · B8: TANIM YA DA ÜST-AKIŞ KOLON KÜMESİ DEĞİŞİNCE DÜŞER ───────────────

def test_SAGLAM_SERTIFIKA_GECERLI():
    d = _durum()
    assert d["gecerli"] and not d["yeniden_dogrulama_gerekli"]
    assert C.rozet_kademesi(d) == "sertifikali"


def test_B8_TANIM_DEGISINCE_DUSUYOR():
    """`MetricDefinition` değişti → sertifika `yeniden_dogrulama_gerekli`."""
    d = C.durum(_sertifika(), tanim="BASKA_HASH", koken=C.koken_hash(_KOKEN))
    assert d["yeniden_dogrulama_gerekli"]
    assert d["otomatik_iptal_nedeni"] == [C.NEDEN_TANIM]


def test_B8_UST_AKIS_KOLON_KUMESI_DEGISINCE_DUSUYOR():
    """🔴 **`1.6`'nın ön koşul olmasının sebebi.** Bugünkü sırayla `1.5` önce inseydi
    `lineage_set_hash` ya **uydurulur** ya **hep `None`** olurdu — ikisi de *"beyan var,
    karşılığı yok"*."""
    d = C.durum(_sertifika(), tanim=C.tanim_hash(_TANIM), koken="BASKA_HASH")
    assert d["otomatik_iptal_nedeni"] == [C.NEDEN_KOKEN]


def test_TTL_DOLUNCA_DUSUYOR():
    """Zaman tek başına bir kusur değildir ama bir sertifika *"o gün doğruydu"* der;
    süresiz bir onay, **sorulmamış** bir sorudur."""
    eski = _sertifika(
        son_gecerlilik=(datetime.now(timezone.utc) - timedelta(days=1)).isoformat())
    d = C.durum(eski, tanim=C.tanim_hash(_TANIM), koken=C.koken_hash(_KOKEN))
    assert d["otomatik_iptal_nedeni"] == [C.NEDEN_SURE]
    assert C.GECERLILIK_GUN == 90


def test_BIRDEN_FAZLA_NEDEN_HEPSI_YAZILIYOR():
    """Bir kapının düşmesi ötekini **gizlemez** — *"neden düştü"* sorusunun cevabı
    kullanıcıya gösterilecek şeydir."""
    d = C.durum(_sertifika(
        son_gecerlilik=(datetime.now(timezone.utc) - timedelta(days=1)).isoformat()),
        tanim="X", koken="Y")
    assert set(d["otomatik_iptal_nedeni"]) == {C.NEDEN_TANIM, C.NEDEN_KOKEN, C.NEDEN_SURE}


# ── 2 · ÇÜRÜYEN SERTİFİKA SİLİNMEZ ──────────────────────────────────────────

def test_CURUYEN_SERTIFIKA_SEVIYESINI_KORUYOR():
    """🔴 Silmek, *"hiç sertifikalanmamış"* ile *"sertifikalanmış ama tanım değişmiş"*i
    karıştırırdı — ve ikincisi kullanıcı için **daha bilgilendiricidir** (biri bu metriğe
    bakmış, sonra dünya değişmiş)."""
    d = C.durum(_sertifika(), tanim="X", koken=C.koken_hash(_KOKEN))
    assert d["seviye"] == "sertifikali", "seviye silinmiş"
    assert d["yeniden_dogrulama_gerekli"]


def test_SERTIFIKASIZ_METRIK_NONE():
    """`None` = **hiç sertifikalanmamış**; çürümüş bir sertifikayla aynı şey değil."""
    assert C.durum(None) is None
    assert C.rozet_kademesi(None) is None


def test_CURUMUS_SERTIFIKA_KADEME_VERMIYOR():
    """🔴 Çürük bir onayı *"sertifikalı"* diye göstermek, rozeti bir **süse** çevirirdi —
    MIMARI'nin kalibre edilmemiş güven sayısına itirazının aynısı."""
    assert C.rozet_kademesi(C.durum(_sertifika(), tanim="X", koken="Y")) == "uyari"


# ── 3 · HASH DAVRANIŞI ──────────────────────────────────────────────────────

def test_SINONIM_EKLEMEK_SERTIFIKAYI_DUSURMUYOR():
    """⚠ Bir eşanlamlı eklemek metriğin **tanımını** değiştirmez, yalnız
    **bulunabilirliğini** artırır. Sinonimi hash'e katmak, sertifikayı katalog bakımının
    **her turunda** düşürürdü — ve gürültüyle ateşleyen bir kapı kapatılır."""
    assert C.tanim_hash({**_TANIM, "synonyms": ["fire", "zayiat"]}) == C.tanim_hash(_TANIM)


def test_HASH_KANONIK_SIRADAN_BAGIMSIZ():
    """`sort_keys` olmadan aynı tanım farklı sıralamayla farklı hash üretir ve sertifika
    **kendiliğinden** çürürdü."""
    a = C.tanim_hash({"expression": "SUM(x)", "unit": "kg"})
    b = C.tanim_hash({"unit": "kg", "expression": "SUM(x)"})
    assert a == b


def test_KOKEN_HASH_FILTRE_DEGERINDEN_BAGIMSIZ():
    """Bir filtrenin **değeri** sorudan soruya değişir; sertifikanın sorduğu soru
    *"aynı kolonlardan mı besleniyor"*dur."""
    a = C.koken_hash({**_KOKEN, "filtreler": [{"boyut": "ay", "deger": "ocak"}]})
    b = C.koken_hash({**_KOKEN, "filtreler": [{"boyut": "ay", "deger": "şubat"}]})
    assert a == b


def test_TANIMIN_KENDISI_SAKLANMIYOR():
    """🔴 Tanımın kendisini saklamak, aynı gerçeğin **ikinci bir kopyasını** üretirdi.
    Hash bir **parmak izidir**: değişip değişmediğini söyler, neyin değiştiğini değil —
    ve sertifikanın sorduğu soru tam olarak *"değişti mi"*dir."""
    kaynak = (KOK / "control_plane" / "models.py").read_text(encoding="utf-8")
    i = kaynak.index("class MetrikSertifikasi")
    govde = kaynak[i:i + 2200]
    assert "definition_hash" in govde and "expression" not in govde, \
        "tanımın kendisi tabloya kopyalanmış — ikinci bir kaynak"


# ── 4 · YETKİ (1.3'ün matrisi) ──────────────────────────────────────────────

def test_METRIC_CERTIFY_ADMIN_USTU():
    """Bir metriği *"sertifikalı"* ilan etmek, bir Discovery adayını kalıcı ölçüye
    yükseltmekle **aynı ağırlıkta** bir kurumsal beyandır → `measure:approve` ile aynı rütbe."""
    from control_plane.authorize import _ACTION_MIN_RANK

    assert _ACTION_MIN_RANK["metric:certify"] == _ACTION_MIN_RANK["measure:approve"] == 2


# ── 5 · SÖZLEŞME + FRONTEND (K2) ────────────────────────────────────────────

def test_SOZLESME_EXPLAIN_SERTIFIKA_TASIYOR():
    from app.schemas import Explain

    assert "sertifika" in Explain.model_fields
    assert Explain(path="cube").sertifika is None, "varsayılan None değil — KURAL B kırık"


def test_FRONTEND_KADEMEYI_GOSTERIYOR():
    """🔴 **K2:** yeni bir sözleşme alanı **frontend tüketicisi olmadan** eklenemez."""
    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    panel = (FE / "components" / "ChatPanel.tsx").read_text(encoding="utf-8")
    assert "sertifikaRozeti" in panel, "sertifika kademesi hiçbir yerde GÖSTERİLMİYOR"
    # 🔴 **YAPISAL ölçüm** — ve bu bir düzeltme: ilk sürüm *"yeni panel DEĞİL"* cümlesini
    # ARIYORDU ve cümle satır sonuna bölündüğü için kırmızı verdi (bu oturumda dördüncü
    # kez metin ölçme kusuru). Doğru soru bir cümle değil bir YER: kademe, var olan güven
    # rozetinin YANINDA mı duruyor? Aynı dosyada olmak, tam olarak bunun kanıtıdır.
    assert "confidenceBadge" in panel, (
        "sertifika kademesi güven rozetinden AYRI bir yere taşınmış — yol haritası birebir "
        "'güven rozetinin kademesi (yeni panel DEĞİL)' diyor; K5 panel tavanı 13/13, boşluk 0")
    yeni_panel = [f.name for f in (FE / "components").glob("*Sertifika*")]
    assert not yeni_panel, f"YENİ PANEL açılmış: {yeni_panel} — tavan 13/13, boşluk 0"


def test_FRONTEND_ESIK_KOPYALAMIYOR():
    """🔴 Kademe kararı **backend'de** (`certification.rozet_kademesi`); frontend'de ikinci
    bir eşik kümesi *"aynı kuralın iki sahibi"* olurdu."""
    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    panel = (FE / "components" / "ChatPanel.tsx").read_text(encoding="utf-8")
    i = panel.index("export function sertifikaRozeti")
    govde = panel[i:i + 1600]
    for sizinti in ("definition_hash", "lineage_set_hash", "GECERLILIK", "90"):
        assert sizinti not in govde, (
            f"çürüme kuralı frontend'e KOPYALANMIŞ ({sizinti!r}) — iki sahip")


# ── 6 · GÖÇ ZİNCİRİ TEK BAŞLI ───────────────────────────────────────────────

def test_ALEMBIC_TEK_HEAD():
    """🔴 **Bir kapı, kendi ölçüm hatamdan doğdu.** Bu turda `down_revision`'ları tek
    tırnak varsayan bir betikle **iki head** ölçtüm ve *"canlı bir göç engeli"* ilan
    ettim; Alembic'in kendisine sorunca **tek head** çıktı (`a4d8f2c6e903` çift tırnak
    kullanıyordu). Olmayan bir soruna yama yazmaktan **aracın kendisine sormak** kurtardı.

    Kapı artık **Alembic'in kendi grafiğini** kullanıyor: iki head gerçekten oluşursa
    `alembic upgrade head` *"Multiple head revisions"* ile patlar ve Postgres dağıtımı
    (CLAUDE.md: *"Postgres'te sahibi admin-api"*) **göç edemez**.
    """
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(KOK / "alembic.ini"))
    cfg.set_main_option("script_location", str(KOK / "migrations"))
    heads = ScriptDirectory.from_config(cfg).get_heads()
    assert len(heads) == 1, (
        f"{len(heads)} Alembic head'i var: {heads}. `alembic upgrade head` "
        "'Multiple head revisions' ile patlar — birleştirme göçü gerekir.")
