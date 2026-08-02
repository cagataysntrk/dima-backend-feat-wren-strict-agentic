"""FAZ 1.2 / **G9** — KOMPOZİSYONELLİK: bir ölçünün değeri, YANINDAKİ ölçülere BAĞLI OLMAMALI.

Planın G9 kapısı bu oturumun sonuna kadar **yazılmamıştı** (2 Ağustos 2026 genel kontrolünde
bulundu). Oysa plan onu *"G2/G3'ün tek ucuz otomatik dedektörü"* diye tanımlıyor ve haklı:

`SELECT SUM(kg) FROM parti` ile `SELECT SUM(kg), COUNT(DISTINCT makine) FROM parti`
**aynı `SUM(kg)`'yi vermek zorundadır.** Vermiyorsa altta bir JOIN satırları çoğaltmış
demektir ve hangi sayının çoğaldığı SELECT listesine göre değişiyor demektir — kullanıcının
asla fark edemeyeceği bir hata sınıfı, çünkü tek başına bakınca sayı doğru.

Bu tam olarak ölçülmüş G2 ihlalinin belirtisidir: ters yönde (ONE_TO_MANY) handle üretilirse
join pruning kompozisyonelliği bozuyor ve aynı boyut/aynı cube'da makine sayısı **3 → 7.038**,
kapasite **4.700 → 11.026.200** ölçülmüştü. G2 o yönü ÜRETMEYEREK önlüyor; G9 ise önlemin
tuttuğunu **her build'de ölçüyor** — çünkü ilişkiler elle de yazılabilir (`relationships.yml`)
ve üreteci baypas eden bir el, G2'yi de baypas eder.

Kapı gerçek veriye karşı ve GERÇEK ÇALIŞTIRMAYLA işler: `dry_plan` yetmez (`strict_mode=False`,
bkz. MIMARI.md §5) — sayıların kendisi karşılaştırılır.
"""

from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def svc_ve_db():
    import duckdb

    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    con = duckdb.connect(str((s.connection_dict() or {}).get("path")
                             or "demo/data/boyahane.duckdb"), read_only=True)
    try:
        yield svc, con
    finally:
        con.close()


def _tek_deger(svc, con, cq):
    plan = svc.dry_plan(svc.cube_sql(cq))
    satirlar = con.execute(plan.replace('boyahane."main".', "main.")).fetchall()
    return satirlar


def _sayisal(v):
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def test_uretilen_boyutlu_cubelerde_OLCU_YALNIZ_kalinca_da_AYNI(svc_ve_db, schema):
    """Asıl kapı. İlişki-türevi boyut TAŞIYAN her cube'da, her ölçü tek başına ve tüm
    ölçülerle birlikte AYNI değeri vermeli.

    Neden yalnız türev-boyutlu cube'lar: fan-out riski JOIN'den doğar ve bu cube'lar join
    kuran cube'lardır. (Yerli-only cube'larda da koşmak zararsız ama pahalı; risk sıfır.)
    """
    svc, con = svc_ve_db
    sorunlar = []
    for c in schema.get("cubes", []):
        if not (c.get("dimension_origin") or {}):
            continue
        olculer = list(c.get("measures") or [])
        if len(olculer) < 2:
            continue
        try:
            hepsi = _tek_deger(svc, con, {"cube": c["name"], "measures": olculer})
        except BaseException as e:  # noqa: BLE001 — Rust PANIC `Exception` DEĞİLDİR
            sorunlar.append(f"{c['name']}: çoklu-ölçü sorgusu patladı: {type(e).__name__}")
            continue
        if not hepsi:
            continue
        birlikte = dict(zip(olculer, hepsi[0]))
        for m in olculer:
            try:
                tek = _tek_deger(svc, con, {"cube": c["name"], "measures": [m]})
            except BaseException as e:  # noqa: BLE001
                sorunlar.append(f"{c['name']}.{m}: tek-ölçü sorgusu patladı: {type(e).__name__}")
                continue
            a, b = _sayisal(tek[0][0] if tek else None), _sayisal(birlikte.get(m))
            if a is None or b is None:
                continue
            if abs(a - b) > max(1e-6, abs(a) * 1e-9):
                sorunlar.append(
                    f"{c['name']}.{m}: TEK BAŞINA {a} · YANINDA BAŞKA ÖLÇÜLERLE {b} — "
                    "bir JOIN satırları çoğaltıyor (fan-out). Hangi sayının şiştiği SELECT "
                    "listesine göre değişir; kullanıcı bunu fark EDEMEZ.")
    assert not sorunlar, "KOMPOZİSYONELLİK İHLALİ:\n  " + "\n  ".join(sorunlar)


def test_uretilen_BOYUT_eklemek_toplami_DEGISTIRMEZ(svc_ve_db, schema):
    """İkinci yüz: türev boyutla KIRILMIŞ bir ölçünün segment toplamı, kırılmamış toplama
    eşit olmalı. Değilse join ya satır çoğaltıyor ya da satır düşürüyor (INNER gibi
    davranıyor) — ikisi de sessizdir.

    Yalnız TOPLANABİLİR ölçülerde anlamlıdır; ortalama/oranda parçalar toplamı zaten bütünü
    vermez (bkz. `app/contribution.py::ayristirilabilir_mi`, aynı matematik).
    """
    from app.contribution import ayristirilabilir_mi

    svc, con = svc_ve_db
    sorunlar, denendi = [], 0
    for c in schema.get("cubes", []):
        origin = c.get("dimension_origin") or {}
        for boyut in origin:
            for m in (c.get("measures") or []):
                ok, _ = ayristirilabilir_mi(m, c)
                if not ok:
                    continue
                try:
                    butun = _tek_deger(svc, con, {"cube": c["name"], "measures": [m]})
                    parca = _tek_deger(svc, con, {"cube": c["name"], "measures": [m],
                                                  "dimensions": [boyut]})
                except BaseException as e:  # noqa: BLE001
                    sorunlar.append(f"{c['name']}.{m}×{boyut}: patladı {type(e).__name__}")
                    continue
                b = _sayisal(butun[0][0] if butun else None)
                p = sum(x for r in parca if (x := _sayisal(r[-1])) is not None)
                if b is None:
                    continue
                denendi += 1
                if abs(p - b) > max(1e-6, abs(b) * 1e-9):
                    sorunlar.append(
                        f"{c['name']}.{m} × {boyut}: kırılmamış {b} · segment toplamı {p} "
                        f"(fark {p - b:+,.2f}) — join satır çoğaltıyor ya da düşürüyor")
                break  # cube+boyut başına tek toplanabilir ölçü yeter (maliyet)
    assert denendi >= 5, f"yalnız {denendi} kombinasyon sınandı — kapı boşa dönüyor olabilir"
    assert not sorunlar, "TOPLAM KORUNMUYOR:\n  " + "\n  ".join(sorunlar)


def test_hop_derinligi_OLCULUYOR_sabit_degil():
    """G7 kaydı: `hops` eskiden sabit `1` yazılıyordu. Hedefteki kolonun KENDİSİ calc ise
    zincir 2 sıçramadır; sabit 1, yayımlanmış bir 2-sıçramalı boyutu yakınmış gibi gösterir
    ve derinliği okuyan her tüketici (chip sıralaması, Query Contract, ileride router
    tercihi) yanlış bilgiyle çalışırdı."""
    from app.compose import _hop_derinligi

    assert _hop_derinligi({"name": "bolum", "type": "VARCHAR"}) == 1
    assert _hop_derinligi({"name": "egitim", "is_calculated": True,
                           "expression": "personel_ozluk.egitim"}) == 2
    assert _hop_derinligi({"name": "egitim", "isCalculated": True}) == 2, (
        "MDL camelCase yazımı (`isCalculated`) tanınmıyor — build çıktısında sıçrama "
        "derinliği 1 görünür")


def test_yayimlanan_boyutlarin_derinligi_KATALOGDA_dogru(schema):
    """Bugün yayımlanan 7 üretilen boyutun hepsi gerçekten 1 sıçrama (2-sıçramalı kolonlar
    `dimension: false` ile yalnız calc olarak üretildi). Bu, `dimension_origin`'i okuyan
    Faz 3.4 chip sıralamasının bugün doğru veriyle çalıştığının kaydıdır."""
    import json

    from app.config import get_settings

    mdl = json.loads((get_settings().resolved_project_dir() / "target" / "mdl.json")
                     .read_text(encoding="utf-8"))
    modeller = {m["name"]: {c["name"]: c for c in m.get("columns", [])}
                for m in mdl.get("models", [])}
    yanlis = []
    for c in schema.get("cubes", []):
        for d, o in (c.get("dimension_origin") or {}).items():
            kolon = modeller.get(o["model"], {}).get(o["column"], {})
            beklenen = 2 if (kolon.get("isCalculated") or kolon.get("is_calculated")) else 1
            if o.get("hops") != beklenen:
                yanlis.append(f"{c['name']}.{d}: hops={o.get('hops')} ama gerçek {beklenen}")
    assert not yanlis, "SIÇRAMA DERİNLİĞİ YANLIŞ:\n  " + "\n  ".join(yanlis)
