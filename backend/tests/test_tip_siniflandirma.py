"""FAZ B — tip sınıflandırması MOTORUN kanonikleştiricisinden geçiyor.

## Ölçülen sessiz-yanlış (2 Ağustos 2026)

`db_introspect.classify_column` ham DB tip yazımlarını **elle tutulan iki kümeye** karşı
sınıyordu. 17 gerçek yazımla ölçüldü: **13'ü yanlış sınıflanıyordu** ve hepsi sessizce
`dimension`'a düşüyordu.

| Yazım | Lehçe | Elle | Olmalı |
|---|---|---|---|
| `numeric(18,2)` | postgres | dimension | **measure** — bir PARA TUTARI |
| `int8` · `int4` · `float8` | postgres | dimension | **measure** |
| `timestamptz` · `timestamp(3)` | postgres | dimension | **time** |
| `datetime2` · `datetimeoffset` | tsql | dimension | **time** |
| `decimal(10,4)` · `smallmoney` · `tinyint` | tsql | dimension | **measure** |
| `HUGEINT` · `UBIGINT` | duckdb | dimension | **measure** |

Sonuç: bir müşteri DB'sini introspect ettiğimizde taslak MDL **tutarları gruplama
anahtarı** yapıp **tarihleri zaman ekseninden** düşürürdü — ve bu, kullanıcıya
*"şemanı çıkardım"* diye sunulurdu.

## Neden elle liste kaybedilen bir yarış

Her lehçenin kendi yazımı var (`int8`/`float8` postgres · `datetime2`/`smallmoney` tsql ·
`HUGEINT`/`UBIGINT` duckdb) ve liste **ancak biri kırılınca** büyür. Motor bunu ZATEN
çözüyor — MIMARI §5: *"motor zaten yapıyorsa yazma."*
"""

from __future__ import annotations

import pytest

from app.db_introspect import IntrospectedColumn, _kanonik_tip, classify_column


def _kolon(tip: str, pk: bool = False) -> IntrospectedColumn:
    return IntrospectedColumn(name="x", type=tip, nullable=True, is_primary_key=pk)


# --- ASIL KAPI: ölçülen 13 kaçak --------------------------------------------------

@pytest.mark.parametrize("ham,lehce,beklenen", [
    # postgres — `information_schema` yerine `pg_catalog` bu kısa adları döndürür
    ("int8", "postgres", "measure"),
    ("int4", "postgres", "measure"),
    ("float8", "postgres", "measure"),
    ("numeric(18,2)", "postgres", "measure"),      # PARA TUTARI
    ("timestamptz", "postgres", "time"),
    ("timestamp(3)", "postgres", "time"),
    # tsql
    ("tinyint", "tsql", "measure"),
    ("smallmoney", "tsql", "measure"),
    ("decimal(10,4)", "tsql", "measure"),
    ("datetime2", "tsql", "time"),
    ("datetimeoffset", "tsql", "time"),
    # duckdb
    ("HUGEINT", "duckdb", "measure"),
    ("UBIGINT", "duckdb", "measure"),
])
def test_OLCULEN_kacaklar_kapandi(ham, lehce, beklenen):
    """Bu 13 yazım elle kümede yoktu ve hepsi `dimension`'a düşüyordu."""
    assert classify_column(_kolon(ham), dialect=lehce) == beklenen


@pytest.mark.parametrize("ham,lehce", [
    ("character varying(255)", "postgres"), ("nvarchar(50)", "tsql"), ("text", "postgres"),
])
def test_METIN_boyut_kalir(ham, lehce):
    assert classify_column(_kolon(ham), dialect=lehce) == "dimension"


def test_BIT_ve_BOOLEAN_bilincli_olarak_boyut():
    """Teknik olarak sayısaldır ama toplanması ANLAMSIZDIR: bayrakların toplamı bir ölçü
    değildir. Kanonikleştirici onları sayısal görse de küme dışında tutulur."""
    assert classify_column(_kolon("bit"), dialect="tsql") == "dimension"
    assert classify_column(_kolon("boolean"), dialect="postgres") == "dimension"


# --- Korunan davranışlar ---------------------------------------------------------

def test_PK_her_zaman_boyut():
    """PK kimlik/gruplama amaçlıdır — `bigint` bile olsa toplanmaz."""
    assert classify_column(_kolon("bigint", pk=True)) == "dimension"
    assert classify_column(_kolon("int8", pk=True), dialect="postgres") == "dimension"


def test_ESKI_yazimlar_bozulmadi():
    """Geriye uyum: elle kümedeki adlar çalışmaya devam etmeli."""
    for t, b in (("INTEGER", "measure"), ("BIGINT", "measure"), ("DATE", "time"),
                 ("TIMESTAMP", "time"), ("DOUBLE PRECISION", "measure")):
        assert classify_column(_kolon(t)) == b, t


# --- Kanonikleştirici ------------------------------------------------------------

def test_PARAMETRE_atilir():
    """Sınıflandırma ölçek/hassasiyete bakmaz: `DECIMAL(18,2)` ile `DECIMAL(4,0)`
    ikisi de ölçüdür."""
    assert _kanonik_tip("numeric(18,2)", "postgres") == "DECIMAL"
    assert _kanonik_tip("varchar(255)", "postgres") == "VARCHAR"


def test_COZULEMEYEN_tip_HAM_degere_duser():
    """Fail-closed YAPILMAZ: tanımadığı bir tip yüzünden tüm introspection'ı durdurmak,
    bilinmeyen tip için doğru varsayılan zaten "boyut" (en az iddialı sınıf) iken
    orantısız olurdu."""
    assert classify_column(_kolon("bizim_ozel_tipimiz")) == "dimension"
    assert _kanonik_tip("bizim_ozel_tipimiz") == "BIZIM_OZEL_TIPIMIZ"


def test_MOTOR_yoksa_patlamaz(monkeypatch):
    """Kanonikleştirici erişilemezse ham değere düşülür — bugünkü davranış korunur."""
    import builtins

    gercek = builtins.__import__

    def _patlat(ad, *a, **k):
        if ad == "wren.type_mapping":
            raise ImportError("yok")
        return gercek(ad, *a, **k)

    monkeypatch.setattr(builtins, "__import__", _patlat)
    assert classify_column(_kolon("BIGINT")) == "measure"      # elle küme yine çalışır
    assert classify_column(_kolon("int8")) == "dimension"       # motorsuz KAÇAR (kabul)


def test_ELLE_kume_KANONIK_adlar_uzerinde():
    """Küme artık ham yazımları değil KANONİK adları tutar — yeni bir lehçe eklendiğinde
    listeye dokunmak gerekmez. Ham yazım sızarsa bu test bozulur."""
    from app.db_introspect import _DATE_TYPES, _ESKI_YAZIMLAR, _NUMERIC_TYPES

    kanonik = _NUMERIC_TYPES | _DATE_TYPES
    # `TIMESTAMPTZ`/`SMALLMONEY` kanonik adın KENDİSİDİR (ölçüldü: parse_type onları
    # aynen döndürüyor) — onları "sızmış" saymak testi yanlış yapardı; ilk sürümde
    # tam olarak bu oldu.
    for ham, kanon in (("int8", "BIGINT"), ("int4", "INT"), ("float8", "DOUBLE"),
                       ("numeric", "DECIMAL"), ("datetime2", "TIMESTAMP")):
        assert ham.upper() not in kanonik, (
            f"{ham}: ham lehçe yazımı KANONİK kümeye sızmış — yeri `_ESKI_YAZIMLAR`")
        assert kanon in kanonik, f"{kanon} kanonik küme dışında"
    # Geriye uyum kuyruğu AYRI durur: karışık bir küme, hangi adın kanonik hangisinin
    # yama olduğunu gizler ve zamanla "kanonik küme" iddiası çürür.
    assert "NUMERIC" in _ESKI_YAZIMLAR and "NUMERIC" not in kanonik
