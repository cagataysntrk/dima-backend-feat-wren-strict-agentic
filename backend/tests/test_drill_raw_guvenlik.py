"""FAZ A2 — `/ask/drill action="raw"` üçlü baypası.

Denetimde (2 Ağustos 2026) bulunan en ciddi tek nokta: ham yaprak **`SELECT *`** yazıp
≤500 satır döndürüyor ve **üç ayrı değişmezi aynı 30 satırda kırıyordu**:

| Kırılan | Değişmez | Sonuç |
|---|---|---|
| `always_filter` uygulanmıyordu | §4-5 (fail-closed, sessiz düşmesi **P0**) | `ticaret.tur='satis'` olmadan `alis` satırları sızar (ölçülen vakada 34M TL) |
| PII maskesi çalışmıyordu | §4-1 / KVKK | `SELECT *` cube'un yayımlamadığı kolonları da getirir — `app/pii.py`'nin kendi docstring'i `personel_ozluk.tc_kimlik`'i örnek veriyor |
| `audit.record` yoktu | ADR-0014 K6 | Tenant verisinin ham satırları **iz bırakmadan** dışarı çıkıyordu |

MIMARI.md §6.3 bunu yalnız **birinci** boyutuyla kaydetmişti (*"drill raw leaf — açık"*);
PII ve audit boyutları belgede hiç yoktu.

**Savunma sırası bilinçli:** önce *seçme* (hassas kolon sorguya hiç girmez), sonra
*maskeleme* (serbest metne gömülü PII için), sonra *iz* (kim ne gördü). Maskeleme ilk
savunma olsaydı, maskeleyemediği bir alan (ad-soyad regex'le yakalanamaz) sızardı.
"""

from __future__ import annotations

import pytest

from app.drill import UnsafeDrillError, build_raw_row_sql

# --- saf fonksiyon: kolon seçimi -------------------------------------------------

def test_SELECT_YILDIZ_uretilmez():
    """Asıl düzeltme. `SELECT *` ham satırda "cube'un yayımlamadığı her kolon" demektir."""
    sql = build_raw_row_sql("partiler", [], columns=["parti_no", "kg"])
    assert "SELECT parti_no, kg FROM partiler" in sql
    assert "*" not in sql


def test_bos_kolon_listesi_REDDEDILIR():
    """`SELECT *`'a sessizce geri düşmek düzeltmenin kendisini iptal ederdi — bu yüzden
    boş liste bir HATA, varsayılan değil."""
    with pytest.raises(UnsafeDrillError, match="kolon listesi BOŞ"):
        build_raw_row_sql("partiler", [], columns=[])
    with pytest.raises(UnsafeDrillError):
        build_raw_row_sql("partiler", [], columns=None)


def test_guvensiz_kolon_adi_REDDEDILIR():
    """Kolon adları şema metadata'sından gelir, kullanıcıdan değil — ama savunma-derinliği
    (`base_object`/`dimension` için zaten var olan disiplin) kolonlara da uygulanır."""
    with pytest.raises(UnsafeDrillError, match="Güvensiz kolon"):
        build_raw_row_sql("partiler", [], columns=["kg; DROP TABLE x"])


# --- uçtan uca: üç değişmez ------------------------------------------------------

def _drill_raw(client, cube="parti", limit=5, **kw):
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    meta = next(c for c in svc.schema()["cubes"] if c["name"] == cube)
    cq = {"cube": cube, "measures": [meta["measures"][0]]}
    return client.post("/ask/drill", json={"cube_query": cq, "action": "raw",
                                           "limit": limit, **kw})


def test_ham_satir_HASSAS_KOLON_secmez(client):
    """Faz A1'in sınıflandırması burada da geçerli: hassas kolon sorguya HİÇ girmez."""
    r = _drill_raw(client)
    assert r.status_code == 200, r.text
    d = r.json()
    sql = d["sql"]
    assert "SELECT *" not in sql
    # `partiler.operator` Faz A1'de `sensitivity: person` beyan edildi.
    assert "operator" not in sql.split(" FROM ")[0], f"hassas kolon seçilmiş:\n{sql}"
    assert d["raw_rows"] and "operator" not in (d["raw_rows"]["columns"] or [])


def test_ham_satirda_KISISEL_VERI_donmez(client):
    """Sonuçta gerçek çalışan adı görünemez — ne kolon seçimiyle ne maskeyle."""
    import duckdb

    from app.config import get_settings

    s = get_settings()
    con = duckdb.connect(str((s.connection_dict() or {}).get("path")
                             or "demo/data/boyahane.duckdb"), read_only=True)
    try:
        adlar = {r[0] for r in con.execute(
            "select distinct ad_soyad from main.personel where ad_soyad is not null").fetchall()}
    finally:
        con.close()
    d = _drill_raw(client, limit=50).json()
    metin = str(d.get("raw_rows"))
    sizan = sorted(a for a in adlar if a and a in metin)
    assert not sizan, f"ham satırda kişisel veri: {sizan[:5]}"


def test_ALWAYS_FILTER_ham_satir_yolunda_UYGULANIR(client, monkeypatch):
    """`always_filter` fail-closed'dır (§4-5) ve sessizce düşmesi bir **P0**'dır: ölçülen
    vakada `ticaret.tur='satis'` atlanınca 34M TL'lik `alis` verisi filtreyi geçmişti.

    demo-boyahane katalogunda `always_filter` taşıyan cube YOK (o bir netsis/gitas
    özelliğidir), bu yüzden uçtan uca veriyle gösterilemiyor. Onun yerine **bağlantı**
    doğrulanır: ham yaprak `_inject_always_filter`'ı GERÇEKTEN çağırıyor mu? Eksik olan
    tam olarak buydu — fonksiyon vardı, bu yol onu çağırmıyordu.
    """
    from app.wren_service import WrenService

    cagrildi: list[tuple] = []
    orijinal = WrenService._inject_always_filter

    def _casus(self, sql, cube_name):
        cagrildi.append((sql, cube_name))
        return orijinal(self, sql, cube_name)

    monkeypatch.setattr(WrenService, "_inject_always_filter", _casus)
    assert _drill_raw(client).status_code == 200
    ham = [c for c in cagrildi if c[0].lstrip().upper().startswith("SELECT")
           and " FROM partiler" in c[0]]
    assert ham, (
        "ham satır yolu `_inject_always_filter`'ı ÇAĞIRMIYOR — always_filter taşıyan bir "
        f"cube'da satırlar sızar. Görülen çağrılar: {[c[1] for c in cagrildi]}")
    assert ham[0][1] == "parti", f"yanlış cube adıyla çağrılmış: {ham[0][1]!r}"


def test_ham_satir_AUDIT_izi_birakir(client):
    """ADR-0014 K6: tenant verisinin ham satırlarını dışarı veren bir yol iz bırakmadan
    çalışamaz. Denetlenebilirlik iddiası olan bir sistemde en çok iz gerektiren yüzey budur."""
    from sqlmodel import Session, col, select

    from control_plane.db import engine
    from control_plane.models import AuditLog

    with Session(engine) as s:
        once = len(s.exec(select(AuditLog).where(
            col(AuditLog.action).like("drill_raw_view%"))).all())
    assert _drill_raw(client).status_code == 200
    with Session(engine) as s:
        sonra = s.exec(select(AuditLog).where(
            col(AuditLog.action).like("drill_raw_view%"))).all()
    assert len(sonra) > once, "ham satır erişimi audit'e düşmedi"
    assert sonra[-1].rows_returned is not None


def test_drill_diger_actionlar_BOZULMADI(client):
    """Düzeltme yalnız `raw` dalını değiştirmeli; `explain`/`expand` aynen çalışmalı."""
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    meta = next(c for c in svc.schema()["cubes"] if c["name"] == "parti")
    cq = {"cube": "parti", "measures": [meta["measures"][0]]}
    r = client.post("/ask/drill", json={"cube_query": cq, "action": "explain"})
    assert r.status_code == 200 and r.json()["formula_explanation"]
    r = client.post("/ask/drill", json={"cube_query": cq, "action": "expand",
                                        "dimension": meta["dimensions"][0]})
    assert r.status_code == 200 and r.json().get("result")
