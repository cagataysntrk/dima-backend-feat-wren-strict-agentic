"""FAZ 1 (K1) — Discovery sonucundan OTURUM-SCOPED ad-hoc cube: uçurumu kaldırır.

## Neden var

`answer.py::seal()` üç kapısını da **tek bir alana** bakarak açar: `resp.cube_query`.
Discovery cevabı onu hiç set etmiyor → chip · kırılım · zaman granülerliği · aksiyon
önerisi · köken · drill · katkı · doğru grafik (birim/toplanabilirlik) · rapor · pano ·
zamanlama · frontend butonları **hepsi birden** kapanıyor. Kullanıcının *"sistem
tıkanıyor"* dediği şey bu uçurumdur (plan §1).

Bu modül Discovery'nin **sonucundan** bir cube türetir: satırlar oturum DuckDB'sine
materyalize edilir, `dataset._role()` kolon rollerini verir, `dataset.build_mdl()` MDL'i
kurar. Excel yüklemesi için yazılmış hat **çağrılır, kopyalanmaz**.

## Kesin sınır — dürüstçe

Ad-hoc cube **SQL'in seçmediği bir boyutu ekleyemez.** Yani "tam kırılım" değil,
**dondurulmuş görünüm üzerinde tam etkileşim**. B'yi A'nın yerine koymaz.

## YAPI ≠ GÜVEN (MIMARI §5 — bu modülün en önemli cümlesi)

`source` **`llm:<sağlayıcı>` KALIR**, `explain.confidence` **`None` KALIR**. Yapı açılır,
rozet dürüst kalır. Bu otomatik olarak sağlanır: `_build_explain` güveni `source`'tan
okur, `cube_query`'nin varlığından değil.

## Dört risk — planın kabul kapıları

1. **DONDURULMUŞLUK.** `CREATE TABLE … AS SELECT` ile oturum `.duckdb` dosyasına
   materyalize edilir; sonraki chip/drill sorguları **kaynak DB'ye geri gitmez**. Bu,
   `always_filter` endişesini de kapatır — ama iddia değil, `tests/test_adhoc_cube.py`
   bunu ölçer.
2. **KIRPILMIŞ GÖRÜNÜM.** `row_count == limit` ise sonuç tavana **değmiş** olabilir ve o
   görünüm üzerinde `SUM`/`AVG`/`TOP-N` **kendinden emin ama yanlış** cevap verir — tam
   olarak bu deponun *"en tehlikeli sınıf"* tanımı, yeni bir kapıdan. `kirpilmis=True`
   işaretlenir ve toplama chip'leri **sunulmaz**.
3. **MASKELEME SIRASI.** Cube **MASKELİ** satırlardan kurulur — aksi halde oturum
   `.duckdb` dosyası diskte **maskesiz PII** taşırdı. Bedeli: `Ahm** Y***` değerine filtre
   kuran bir chip **boş** döner; o yüzden maskelenen kolonlarda filtre/drill chip'i
   **üretilmez** (`schedules.uyari_nedeni`'nde verilen aynı karar: boş dönen bir chip
   sunmak, hiç sunmamaktan kötüdür).
4. **KILL-SWITCH.** `adhoc_cube` özellik bayrağı; kapalıyken davranış bugünküyle birebir.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

#: Arrow tip adı (öneki) → DuckDB tipi. `wren_service.query()` Arrow şemasını
#: `column_types` olarak taşır; eskiden ATILIYORDU ve K1'in tek eksiği buydu
#: (tipsiz bir sonuçtan ölçü/boyut/zaman ayrımı yapılamaz).
_ARROW_DUCK = (
    ("timestamp", "TIMESTAMP"), ("date", "DATE"), ("time", "TIME"),
    ("decimal", "DOUBLE"), ("double", "DOUBLE"), ("float", "DOUBLE"), ("halffloat", "DOUBLE"),
    ("int", "BIGINT"), ("uint", "BIGINT"),
    ("bool", "BOOLEAN"),
)

#: Bu kadar satırdan sonra ad-hoc cube kurulmaz. Materyalizasyon senkron ve oturum
#: dizinine yazıyor; bir Discovery cevabı için sınırsız disk/zaman harcanmaz.
MAKS_SATIR = 5000


def _duck_tipi(arrow: str) -> str:
    a = (arrow or "").lower()
    for on, duck in _ARROW_DUCK:
        if a.startswith(on):
            return duck
    return "VARCHAR"


def _tablo_adi(cube_adi: str) -> str:
    """DuckDB identifier — enjeksiyon yüzeyi bırakmamak için slug'lanır (dataset.py ile
    aynı disiplin)."""
    s = re.sub(r"[^a-z0-9_]+", "_", (cube_adi or "").lower()).strip("_")
    return s or "adhoc"


def turet(result: dict[str, Any], session_dir: Path, *, cube_adi: str = "adhoc",
          etiket: str = "geçici model", kirpilmis: bool = False,
          maskeli_kolonlar: frozenset[str] = frozenset()) -> dict[str, Any] | None:
    """Discovery sonucu → (service, schema, cube_query, info). Kurulamıyorsa **None**.

    `None` dönmek bir hata değil bir karardır: kurulamayan bir cube'u zorlamak, yapısı
    olmayan bir cevaba yapı **rozeti** takmak olurdu. Çağıran bugünkü davranışa döner.
    """
    from app import dataset

    kolonlar = list(result.get("columns") or [])
    satirlar = list(result.get("rows") or [])
    tipler = list(result.get("column_types") or [])
    if not kolonlar or not satirlar or len(satirlar) > MAKS_SATIR:
        return None
    if len(tipler) != len(kolonlar):
        # Tip bilgisi yoksa rol ataması TAHMİN olurdu (her şey VARCHAR → boyut → ölçüsüz
        # cube). Tahmin etmek yerine yapı vaat etmemek doğrudur.
        return None

    tablo = _tablo_adi(cube_adi)
    alinan: set[str] = set()
    cols: list[dict[str, Any]] = []
    for ad, tip in zip(kolonlar, tipler):
        slug = dataset._slug(ad, alinan)
        duck = _duck_tipi(str(tip))
        cols.append({"orig": str(ad), "name": slug, "duck": duck,
                     "type": dataset._mdl_type(duck), "role": dataset._role(duck)})

    con = dataset._connect(session_dir)
    try:
        con.execute(f"DROP TABLE IF EXISTS {tablo}")
        ddl = ", ".join(f'"{c["name"]}" {c["duck"]}' for c in cols)
        con.execute(f"CREATE TABLE {tablo} ({ddl})")
        yer = ", ".join("?" for _ in cols)
        con.executemany(
            f"INSERT INTO {tablo} VALUES ({yer})",
            [[r.get(c["orig"]) for c in cols] for r in satirlar])
        n = con.execute(f"SELECT COUNT(*) FROM {tablo}").fetchone()[0]
    except Exception:
        # Materyalizasyon başarısızsa yapı VAAT EDİLMEZ; cevap bugünkü haliyle döner.
        return None
    finally:
        con.close()

    info = {"table": tablo, "catalog": "data",
            "columns": [{k: v for k, v in c.items() if k != "duck"} for c in cols],
            "row_count": int(n)}
    mdl = dataset.build_mdl(info, cube_name=cube_adi, label=etiket)
    svc = dataset.build_service(session_dir, mdl)
    sema = svc.schema()

    cube = next((c for c in sema.get("cubes") or [] if c["name"] == cube_adi), None)
    if cube is None:
        return None
    olculer = [m if isinstance(m, str) else m.get("name") for m in (cube.get("measures") or [])]
    if not olculer:
        return None

    # MASKELİ kolonlar slug'a çevrilir — chip üreten taraf orijinal adı değil cube'daki
    # boyut adını görür (bkz. §3 maskeleme sırası).
    maskeli_slug = frozenset(c["name"] for c in cols if c["orig"] in maskeli_kolonlar)

    cq: dict[str, Any] = {
        "cube": cube_adi,
        "measures": [olculer[0]],
        # YAPI ≠ GÜVEN: bu üç alan makbuza taşınır ve rozeti DÜRÜST tutar.
        "adhoc": True,
        "provenance": "llm_sql'den türetildi",
        "kirpilmis": bool(kirpilmis),
    }
    return {"service": svc, "schema": sema, "cube_query": cq, "info": info,
            "maskeli_kolonlar": maskeli_slug,
            "bos_kolonlar": frozenset(),
            "kirpilmis": bool(kirpilmis)}
