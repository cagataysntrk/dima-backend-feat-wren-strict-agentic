"""İLİŞKİ SERTİFİKASI — beyan edilen her join'in VERİYLE ölçülmüş sağlık kaydı (Faz D2).

## Neden bir modül, neden bir artefakt

Sektörde standart pratik ilişki kardinalitesini **modelciye beyan ettirmektir**: Cube, LookML,
MetricFlow ve Snowflake hepsi böyle çalışır; Databricks kendi dokümanında `at_most_one_match`
için açıkça *"runtime'da doğrulanmaz"* der. Beyan yanlışsa sonuç **hatasız, uyarısız ve
`source="cube"` rozetiyle şişmiş** bir sayıdır.

Dima bunu ölçüyordu — ama yalnız `tests/test_relationship_health.py` içinde, koşum anında,
ve ölçümün kendisi **hiçbir yerde saklanmıyordu**. MIMARI §9.1 bu ölçümü *"dünyada ilk"*
sayan bir iddia taşıyor; **artefakt olmadan iddia karşılıksızdır**: kullanıcı bir kırılıma
bakıp *"bu join ölçüldü mü"* diye soramaz, cevabın makbuzu da bunu taşıyamaz.

Bu modül üç şeyi ayırır ve tekleştirir:

1. **Ölçüm** (`certify`) — saf; bir `sorgu(sql) -> satırlar` geri-çağrısı alır, bağlantı
   türü bilmez (DuckDB, MSSQL, WrenService konnektörü — hepsi olur).
2. **Artefakt** (`yaz` / `oku`) — `<proje>/target/fanout_certificate.json`. Build çıktısıdır;
   MDL'in yanında durur ve onunla birlikte sürümlenir.
3. **Tüketiciler** — regresyon testi, `WrenService.schema()` (boyut kökenine `certified`
   damgası), Query Contract (`provenance_json`), ve ileride UI rozeti (Faz H5).

Test artık kendi SQL'ini yazmaz, bu modülü **çağırır**. Aksi halde aynı kural iki yerde
yaşardı — bu depoda defalarca ölçülmüş ve her seferinde sapmayla sonuçlanmış bir desen
(`drill.flag_outliers` ↔ `schedules.detect_anomalies`, `interpret._fmt` ↔ `schedules._fmt_deger`).

## Ölçülen üç şey

| Boyut | Soru | Bozulunca ne olur |
|---|---|---|
| **FAN-OUT** | Hedef ("bir" tarafı) anahtarı BENZERSİZ mi? | Join satırları çoğaltır, `SUM`'lar şişer. `wren_core` `join_type`'ı **okumaz** (ölçüldü: MANY_TO_ONE ile MANY_TO_MANY aynı SQL) — motorda hiçbir koruma yoktur. |
| **NULL** | Hedef anahtarında NULL var mı? | Benzersizlik testini sessizce deler. |
| **ÖKSÜZ** | Kaynak satırlarının hepsi bir hedef buluyor mu? | Öksüzler kırılımda NULL kovasına düşer ve o kolona konan HER filtre onları eler. Kanıtlanmış vaka: `cari_kodu` polimorfiktir (`M1001` müşteri, `T-204` tedarikçi) — `cari_hareketler → musteriler` eklenirse satırların %53'ü öksüz kalır. |

Sertifika **tanı koymaz, ölçer**. Eşik kararı (`MAX_ORPHAN_RATE` gibi) tüketicinindir.
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Callable, Iterable
from pathlib import Path

_log = logging.getLogger("dima.app")

SERTIFIKA_DOSYASI = "fanout_certificate.json"
SURUM = 1


def _simdi() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

# `models: [çok, bir]` + `condition: "a.k = b.k"`. Bileşik/karmaşık join'ler ayrıştırılamaz
# ve bilinçli olarak ölçülmez — `expose:` de onları zaten reddediyor (compose.py).
_COND_RE = re.compile(r"^\s*(\w+)\.\"?(\w+)\"?\s*=\s*(\w+)\.\"?(\w+)\"?\s*$")

# `sorgu` geri-çağrısının sözleşmesi: SQL al, satır demetlerinin listesini döndür.
Sorgu = Callable[[str], list[tuple]]


def ayristir(rel: dict) -> tuple[str, str, str, str] | None:
    """`(cok_tablo, cok_kolon, bir_tablo, bir_kolon)` — "çok" → "bir" yönünde.

    `condition`'daki taraf sırası `models` sırasıyla TERS olabilir; yön `models`'ten
    okunur (ilk eleman "çok" tarafıdır), koşulun yazım sırasından değil.
    """
    m = _COND_RE.match(rel.get("condition") or "")
    if not m:
        return None
    la, lc, _ra, rc = m.groups()
    models = rel.get("models") or []
    if len(models) != 2:
        return None
    cok, bir = models[0], models[1]
    src, dst = (lc, rc) if la == cok else (rc, lc)
    return cok, src, bir, dst


def certify(rels: Iterable[dict], sorgu: Sorgu, *, tablolar: set[str] | None = None,
            nitelikli: Callable[[str], str] | None = None,
            mdl_version: str | None = None) -> dict:
    """Her ilişki için ölçülmüş sağlık kaydı. Saf: yalnız `sorgu` üzerinden veriye dokunur.

    `tablolar` verilirse mevcut olmayan tabloya dokunan ilişkiler `durum="atlandi"` ile
    kaydedilir — **sessizce düşürülmez**. "Ölçülmedi" ile "ölçüldü, temiz" ayrı şeylerdir
    ve sertifikanın tüm değeri bu ayrımdadır.

    `nitelikli` mantıksal tablo adını FİZİKSEL nitelikli ada çevirir. Varsayılan `main.<ad>`
    yalnız doğrudan DuckDB bağlantısında doğrudur; konnektör üzerinden gidildiğinde katalog
    adı farklıdır (`boyahane.musteriler` — ölçüldü) ve `WrenService._physical_name`
    verilmelidir. Sabit kodlanmış şema adı bu modülün taşınabilirliğini bitirirdi.
    """
    nitelikli = nitelikli or (lambda t: f"main.{t}")
    kayit: dict[str, dict] = {}
    # ÖLÇÜM ZAMANI + ŞEMA SÜRÜMÜ: sertifika bir GEÇMİŞ ölçümdür. "Bu join güvenli" demek
    # ancak "ne zaman ve hangi şemaya karşı ölçüldü" ile birlikte anlamlıdır — veri
    # değişince tekillik de değişebilir (`operator = ad_soyad` bugün benzersiz, yarın
    # aynı adı taşıyan ikinci personelde değil). MIMARI §9'un hedef diyagramı bu alanı
    # `doğrulama_tarihi` adıyla zaten söz veriyordu.
    for r in rels:
        ad = r.get("name") or "?"
        p = ayristir(r)
        if p is None:
            kayit[ad] = {"durum": "ayristirilamadi",
                         "not": "bileşik/karmaşık condition — ölçülemedi"}
            continue
        cok, src, bir, dst = p
        temel = {"cok": cok, "cok_kolon": src, "bir": bir, "bir_kolon": dst}
        if tablolar is not None and (cok not in tablolar or bir not in tablolar):
            eksik = [t for t in (cok, bir) if t not in tablolar]
            kayit[ad] = {**temel, "durum": "atlandi", "not": f"tablo yok: {', '.join(eksik)}"}
            continue
        try:
            bir_t, cok_t = nitelikli(bir), nitelikli(cok)
            n, farkli, nulls = sorgu(
                f'select count(*), count(distinct "{dst}"), '
                f'count(*) filter (where "{dst}" is null) from {bir_t}')[0]
            toplam, eslesen = sorgu(
                f'select count(*), count(*) filter (where o."{dst}" is not null) '
                f'from {cok_t} s left join {bir_t} o on s."{src}" = o."{dst}"')[0]
        except Exception as exc:                       # ADR-0020: sessiz yutma yok
            _log.warning("fan-out sertifikası ölçülemedi (%s): %s", ad, exc)
            kayit[ad] = {**temel, "durum": "hata", "not": str(exc)[:200]}
            continue
        benzersiz = (n == farkli)
        oksuz = ((toplam - eslesen) / toplam) if toplam else 0.0
        kayit[ad] = {
            **temel,
            "durum": "olculdu",
            "bir_satir": n, "bir_farkli": farkli, "bir_null": nulls,
            "cok_satir": toplam, "cok_eslesen": eslesen,
            "benzersiz": benzersiz, "oksuz_oran": round(oksuz, 6),
            # `saglikli` = fan-out YOK + NULL YOK + öksüz YOK. Eşik değil, ölçümün özeti.
            "saglikli": bool(benzersiz and not nulls and oksuz == 0.0),
        }
    return {"version": SURUM, "olculme_zamani": _simdi(),
            "mdl_version": mdl_version, "relationships": kayit}


def yaz(project_dir: str | Path, sert: dict) -> Path:
    """Sertifikayı `<proje>/target/fanout_certificate.json`'a yazar (MDL'in yanına)."""
    hedef = Path(project_dir) / "target" / SERTIFIKA_DOSYASI
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(json.dumps(sert, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return hedef


def oku(project_dir: str | Path) -> dict:
    """Sertifikayı okur; yoksa/bozuksa **boş** döner — sertifika bir KOLAYLIKTIR, kapı değil.

    Fail-closed yapmak yanlış olurdu: sertifika üretilmemiş bir kurulumda sistem cevap
    vermeyi bırakmamalı, yalnız *"bu join ölçüldü"* diyememeli.
    """
    f = Path(project_dir) / "target" / SERTIFIKA_DOSYASI
    if not f.exists():
        return {}
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        _log.warning("fan-out sertifikası okunamadı: %s", f, exc_info=True)
        return {}
    return d if isinstance(d, dict) else {}


def kanit(
    sert: dict,
    rel_adi: str | None,
    *,
    current_mdl_version: str | None = None,
) -> dict | None:
    """Typed-ish fanout proof without inventing freshness.

    Backward/legacy callers may omit `current_mdl_version`; in that compatibility mode
    the historical measured relationship status is exposed exactly as before.  Day7
    governed consumers MUST pass the current Wren MDL version.  Missing/corrupt/mismatched
    certificates then fail closed to `olculmedi`.
    """
    if not rel_adi:
        return None

    sert = sert if isinstance(sert, dict) else {}
    certificate_mdl_version = sert.get("mdl_version")
    measured_at = sert.get("olculme_zamani")
    relationship = ((sert.get("relationships") or {}).get(rel_adi))

    status = "MISSING"
    certified = "olculmedi"
    if current_mdl_version is not None:
        if not certificate_mdl_version:
            status = "MDL_VERSION_MISSING"
        elif str(certificate_mdl_version) != str(current_mdl_version):
            status = "MDL_MISMATCH"
        elif not isinstance(relationship, dict):
            status = "RELATIONSHIP_UNMEASURED"
        elif relationship.get("durum") != "olculdu":
            status = "RELATIONSHIP_UNMEASURED"
        elif relationship.get("saglikli"):
            status = "HEALTHY"
            certified = "olculdu:saglikli"
        else:
            status = "RISKY"
            certified = "olculdu:riskli"
    else:
        # Historical behavior for non-Day7 callers.
        if not isinstance(relationship, dict):
            status = "RELATIONSHIP_UNMEASURED"
        elif relationship.get("durum") != "olculdu":
            status = "RELATIONSHIP_UNMEASURED"
        elif relationship.get("saglikli"):
            status = "HEALTHY"
            certified = "olculdu:saglikli"
        else:
            status = "RISKY"
            certified = "olculdu:riskli"

    return {
        "relationship": rel_adi,
        "status": status,
        "certified": certified,
        "certificate_mdl_version": certificate_mdl_version,
        "current_mdl_version": current_mdl_version,
        "measured_at": measured_at,
    }


def rozet(
    sert: dict,
    rel_adi: str | None,
    *,
    current_mdl_version: str | None = None,
) -> str | None:
    """Relationship badge; Day7 callers may bind it to the exact current MDL."""
    proof = kanit(
        sert,
        rel_adi,
        current_mdl_version=current_mdl_version,
    )
    return None if proof is None else str(proof["certified"])


#: 🔴 `§F3` — ROZETİN TÜRKÇESİ, TEK SAHİPLİ (`KAT-1`).
#:
#: Rozet bir **kod**tur (`olculdu:saglikli`); kullanıcı onu okumaz. Cümleyi çağıranın
#: yazması, aynı kuralın ikinci bir sahibi demekti — bu depoda defalarca ölçülmüş ve her
#: seferinde sapmayla biten desen. Sözlük burada, `rozet()`'in **yanında** durur: bir
#: gün üçüncü bir durum eklenirse ikisi birlikte değişir.
#:
#: ⚠ Metinler bilerek **fan-out'un sonucunu** söyler, mekanizmasını değil: kullanıcı
#: *"benzersiz anahtar"* değil *"sayı şişer mi"* sorusunu sorar.
_ROZET_BEYANI = {
    "olculdu:saglikli": "bu ilişki fan-out açısından ölçüldü, sayılar şişmiyor",
    "olculdu:riskli": "🔴 bu ilişki ölçüldü ve RİSKLİ — hedef anahtar benzersiz değil, "
                      "toplamlar şişmiş olabilir",
    "olculmedi": "⚠ bu ilişki fan-out açısından ÖLÇÜLMEDİ",
}


def beyan(rozet_kodu: str | None) -> str | None:
    """Rozet kodu → kullanıcıya söylenecek Türkçe cümle parçası. Bilinmeyen kod → `None`.

    🔴 **Neden ölçülmüş bir sağlık BEYAN EDİLİYOR, sessizce geçilmiyor:** bu modülün
    tüm değeri *"ölçülmedi"* ile *"ölçüldü, temiz"* ayrımındadır (bkz. `schema()`'nın
    kendi notu). O ayrım **yalnız damgada** kalırsa kullanıcı için yoktur: soyağacı
    cümlesi *"bu boyut iki tablo öteden geldi"* der ve okuyan, sayının şişip şişmediğini
    **bilemez**. Omni'nin `$55,5 milyar`lık kartezyen felaketi (`§23.1`) tam olarak bu
    boşlukta doğdu — orada ölçüm de yoktu; burada **var ve söylenmiyordu**.

    ⚠ Bilinmeyen kodda **uydurulmaz**, susulur: olmayan bir garantiyi rozetlemek,
    hiç rozetlememekten kötüdür.
    """
    if not rozet_kodu:
        return None
    return _ROZET_BEYANI.get(str(rozet_kodu))


def duckdb_sorgu(con) -> Sorgu:
    """DuckDB bağlantısını `Sorgu` sözleşmesine sarar (testlerin doğrudan kullandığı yol)."""
    return lambda sql: con.execute(sql).fetchall()


def konnektor_sorgu(svc) -> Sorgu:
    """`WrenService._connector()`'ü `Sorgu` sözleşmesine sarar — **datasource-bağımsız**.

    Sertifika ölçümü semantik katmana ihtiyaç duymaz (fiziksel `COUNT`'lar), o yüzden
    `_connector` doğru seviyedir: DuckDB dizini, MSSQL, Postgres — hepsinde aynı kod.
    Kullanıcı SQL'i buradan GEÇMEZ; bu yol yalnız build-time ölçüm içindir.
    """
    def _q(sql: str) -> list[tuple]:
        satirlar = svc._connector().query(sql).to_pylist()
        return [tuple(r.values()) for r in satirlar]
    return _q


def certify_wren_service(svc) -> dict:
    """Measure the compiled Wren project's declared relationships against current MDL.

    This is an explicit build/preflight operation. It never runs from `schema()` and
    therefore does not move the 2×COUNT-per-relationship cost onto the Product hot path.
    The returned certificate is not authority until ordinary consumers bind it to the
    exact current `mdl_version`.
    """
    import yaml

    proje = Path(svc.project_dir)
    rels_f = proje / "relationships.yml"
    if not rels_f.exists():
        raise FileNotFoundError(f"relationships.yml yok: {rels_f}")
    rels = (
        yaml.safe_load(rels_f.read_text(encoding="utf-8")) or {}
    ).get("relationships") or []

    mdl = json.loads(svc._mdl_bytes())
    # Keep physical-name ownership in WrenService/the service implementation instead of
    # duplicating tableReference rules here.
    fiziksel = {
        model.get("name"): svc._physical_name(model)
        for model in (mdl.get("models") or [])
        if model.get("name")
    }
    return certify(
        rels,
        konnektor_sorgu(svc),
        tablolar=set(fiziksel),
        nitelikli=lambda table: fiziksel.get(table, f"main.{table}"),
        mdl_version=svc.mdl_version,
    )


def refresh_wren_service_certificate(svc) -> tuple[Path, dict]:
    """Atomically refresh the derived fanout artifact for one compiled Wren service."""
    certificate = certify_wren_service(svc)
    return yaz(svc.project_dir, certificate), certificate


def _cli() -> int:
    """`python -m app.fanout [proje_dizini]` → sertifikayı üretir ve özetini basar."""
    import sys

    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    proje = Path(sys.argv[1]) if len(sys.argv) > 1 else s.resolved_project_dir()
    svc = WrenService(project_dir=proje, datasource=s.datasource,
                      connection_info=s.connection_dict())
    try:
        hedef, sert = refresh_wren_service_certificate(svc)
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    kayit = sert["relationships"]
    olculdu = [k for k in kayit.values() if k.get("durum") == "olculdu"]
    riskli = [a for a, k in kayit.items() if k.get("durum") == "olculdu" and not k.get("saglikli")]
    print(f"{hedef}: {len(kayit)} ilişki · {len(olculdu)} ölçüldü · {len(riskli)} riskli")
    for a in riskli:
        k = kayit[a]
        print(f"  ⚠ {a}: benzersiz={k['benzersiz']} null={k['bir_null']} "
              f"öksüz=%{k['oksuz_oran']*100:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
