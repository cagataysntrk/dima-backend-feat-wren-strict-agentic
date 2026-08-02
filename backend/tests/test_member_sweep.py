"""FAZ 1.2/G8 — ÜYE TARAMASI: her cube ölçüsü/boyutu GERÇEKTEN çalışıyor mu?

`dry_plan` bir doğrulama kapısı SANILIYOR ama değil. Dima hiç `WrenConfig` kurmadığı için
`strict_mode=False` (bkz. `wren/config.py`) ve `validate_sql_policy` yalnız TABLOLARI
denetler, KOLONLARI denetlemez. Ölçüldü (2 Ağustos 2026):

    dim expression "kesinlikle_yok_boyle_bir_kolon" → dry_plan BAŞARILI, joins=0
    çalıştırma                                       → BinderException: kolon yok

Yani `backend/CLAUDE.md`'nin *"LLM önerir, MOTOR DOĞRULAR — her üretilen SQL
çalıştırılmadan önce dry_plan'dan geçer"* değişmezi, KOLON düzeyinde geçerli DEĞİLDİR.
Uydurma ya da bayat bir kolon adı taşıyan cube üyesi build'den, testlerden ve dry_plan'dan
geçip MÜŞTERİNİN VERİTABANINDA patlar.

Bu risk Faz 1'le BÜYÜDÜ: ilişki-türevi boyutlar artık ÜRETİLİYOR ve bir üretim hatası
(yanlış calc adı, kaybolan hedef kolon) yalnız o boyutu değil — MDL analizi model
düzeyinde yapıldığı için — O MODELE OTURAN TÜM CUBE'LARI düşürebilir.

Bu tarama, her cube'un HER ölçüsünü ve HER boyutunu ayrı ayrı derleyip GERÇEKTEN
çalıştırır (LIMIT 1). Yavaş değil (~150 sorgu) ve tek başına bütün bir sessiz-bozulma
sınıfını kapatır — şema kayması (ERP kolon adı değişimi) dahil.
"""

from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def svc():
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    return WrenService(s.resolved_project_dir(), datasource=s.datasource,
                       connection_info=s.connection_dict())


def _cubes(schema):
    return [c for c in schema["cubes"] if c.get("measures")]


def test_katalog_bos_degil(schema):
    assert len(_cubes(schema)) >= 10, "katalog beklenenden küçük — compose bozulmuş olabilir"


def test_her_OLCU_gercekten_calisir(svc, schema):
    """Her ölçü, kırılımsız olarak derlenip ÇALIŞTIRILABİLMELİ."""
    hatalar = []
    for c in _cubes(schema):
        for m in c["measures"]:
            try:
                sql = svc.cube_sql({"cube": c["name"], "measures": [m]}, limit=1)
                svc.dry_plan(sql)
                svc.query(sql, limit=1)
            except Exception as exc:  # noqa: BLE001 - hepsini toplayıp tek raporla
                hatalar.append(f"{c['name']}.{m}: {type(exc).__name__}: {str(exc)[:160]}")
    assert not hatalar, "ÇALIŞMAYAN ÖLÇÜLER:\n  " + "\n  ".join(hatalar)


def test_her_BOYUT_gercekten_calisir(svc, schema):
    """Her boyut, cube'un ilk ölçüsüyle kırılım olarak çalıştırılabilmeli.

    İlişki-türevi boyutlar burada gerçek JOIN'leriyle sınanır — `dry_plan`'ın
    yakalayamadığı "kolon yok" sınıfı bu adımda ortaya çıkar.
    """
    hatalar = []
    for c in _cubes(schema):
        olcu = c["measures"][0]
        for d in c.get("dimensions") or []:
            try:
                sql = svc.cube_sql({"cube": c["name"], "measures": [olcu],
                                    "dimensions": [d]}, limit=1)
                svc.dry_plan(sql)
                svc.query(sql, limit=1)
            except Exception as exc:  # noqa: BLE001
                hatalar.append(f"{c['name']}.{d}: {type(exc).__name__}: {str(exc)[:160]}")
    assert not hatalar, "ÇALIŞMAYAN BOYUTLAR:\n  " + "\n  ".join(hatalar)


def test_her_ZAMAN_BOYUTU_kovalanabiliyor(svc, schema):
    hatalar = []
    for c in _cubes(schema):
        olcu = c["measures"][0]
        for t in c.get("time_dimensions") or []:
            try:
                sql = svc.cube_sql({"cube": c["name"], "measures": [olcu],
                                    "timeDimensions": [{"dimension": t,
                                                        "granularity": "month"}]}, limit=1)
                svc.dry_plan(sql)
                svc.query(sql, limit=1)
            except Exception as exc:  # noqa: BLE001
                hatalar.append(f"{c['name']}.{t}: {type(exc).__name__}: {str(exc)[:160]}")
    assert not hatalar, "ÇALIŞMAYAN ZAMAN BOYUTLARI:\n  " + "\n  ".join(hatalar)


def test_ILISKI_TUREVI_boyutlar_JOIN_uretiyor(svc, schema):
    """Provenance taşıyan her boyut GERÇEKTEN bir JOIN üretmeli.

    Aksi halde `dimension_origin` yalan söylüyor demektir — "bu kolon şu ilişkiden geldi"
    diyoruz ama plan hiç join içermiyor. Query Contract'ın güvenilirliği buna bağlı.
    """
    kontrol, hatalar = 0, []
    for c in _cubes(schema):
        olcu = c["measures"][0]
        for d in (c.get("dimension_origin") or {}):
            plan = svc.dry_plan(svc.cube_sql(
                {"cube": c["name"], "measures": [olcu], "dimensions": [d]}))
            kontrol += 1
            if plan.upper().count(" JOIN ") < 1:
                hatalar.append(f"{c['name']}.{d}: provenance var ama plan JOIN İÇERMİYOR")
    assert kontrol, "hiç ilişki-türevi boyut bulunamadı — üreteç çalışmamış olabilir"
    assert not hatalar, "\n  ".join(hatalar)
