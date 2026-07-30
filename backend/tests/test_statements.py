"""GL yapısal tablo builder testleri — Tekdüzen gelir tablosu + bilanço. Mock mizan
satırlarıyla (gitas GL gerekmez). Deterministik aritmetik; işaret + ara toplam doğrulanır."""

from app.statements import build_balance_sheet, build_income_statement


def _line(stmt, label):
    return next(x for x in stmt if x["label"] == label)


def test_income_statement_signs_and_subtotals():
    rows = [
        {"hesap_kodu": "600.01", "bakiye": -1_000_000},  # yurtiçi satış (alacak → gelir +)
        {"hesap_kodu": "610.01", "bakiye": 50_000},      # satış iadesi (borç → indirim −)
        {"hesap_kodu": "620.01", "bakiye": 600_000},     # STMM (borç → gider −)
        {"hesap_kodu": "632.01", "bakiye": 100_000},     # genel yönetim gid.
    ]
    st = build_income_statement(rows)
    assert _line(st, "Brüt Satışlar")["amount"] == 1_000_000
    assert _line(st, "Satış İndirimleri (-)")["amount"] == -50_000
    assert _line(st, "Net Satışlar")["amount"] == 950_000            # 1.000.000 − 50.000
    assert _line(st, "BRÜT SATIŞ KARI/ZARARI")["amount"] == 350_000  # 950.000 − 600.000
    assert _line(st, "FAALİYET KARI/ZARARI")["amount"] == 250_000    # 350.000 − 100.000
    assert _line(st, "DÖNEM KARI/ZARARI")["amount"] == 250_000
    assert _line(st, "Net Satışlar")["kind"] == "subtotal"


def test_income_statement_empty():
    st = build_income_statement([])
    assert _line(st, "DÖNEM KARI/ZARARI")["amount"] == 0


def test_income_ignores_non_income_accounts():
    # Bilanço hesapları (1xx) gelir tablosuna girmez.
    st = build_income_statement([{"hesap_kodu": "100.01", "bakiye": 99_999}])
    assert _line(st, "Brüt Satışlar")["amount"] == 0


def test_balance_sheet_balances():
    rows = [
        {"hesap_kodu": "100.01", "bakiye": 50_000},    # kasa (aktif, borç)
        {"hesap_kodu": "255.01", "bakiye": 200_000},   # demirbaş (duran)
        {"hesap_kodu": "320.01", "bakiye": -100_000},  # satıcılar (KV, alacak)
        {"hesap_kodu": "500.01", "bakiye": -150_000},  # sermaye (özkaynak, alacak)
    ]
    bs = build_balance_sheet(rows)
    assert bs["aktif_toplam"] == 250_000
    assert bs["pasif_toplam"] == 250_000
    assert bs["dengede"] is True
    assert next(x for x in bs["aktif"] if "DÖNEN" in x["label"])["amount"] == 50_000
    assert next(x for x in bs["pasif"] if "ÖZKAYNAK" in x["label"])["amount"] == 150_000


def test_balance_sheet_imbalance_flagged():
    bs = build_balance_sheet([{"hesap_kodu": "100.01", "bakiye": 50_000}])
    assert bs["dengede"] is False  # yalnız aktif, pasif 0


class _MockSvc:
    """cube_sql + query stub'ı — resolver'ı DB'siz test eder (gitas gerekmez)."""

    def __init__(self, rows):
        self._rows = rows

    def cube_sql(self, cq):
        assert cq["cube"] == "mizan"  # resolver mizan'ı sorgular
        return "SELECT hesap_kodu, SUM(borc-alacak) bakiye FROM mizan_src GROUP BY 1"

    def query(self, sql, limit=None):
        return {"rows": self._rows, "columns": ["hesap_kodu", "bakiye"],
                "row_count": len(self._rows)}


def test_resolve_statement_gelir():
    from app.statements import resolve_statement

    svc = _MockSvc([{"hesap_kodu": "600.01", "bakiye": -1_000_000},
                    {"hesap_kodu": "620.01", "bakiye": 600_000}])
    out = resolve_statement(svc, "gelir")
    assert out["kind"] == "gelir"
    assert _line(out["statement"], "BRÜT SATIŞ KARI/ZARARI")["amount"] == 400_000


def test_resolve_statement_bilanco():
    from app.statements import resolve_statement

    svc = _MockSvc([{"hesap_kodu": "100.01", "bakiye": 100_000},
                    {"hesap_kodu": "500.01", "bakiye": -100_000}])
    out = resolve_statement(svc, "bilanco")
    assert out["kind"] == "bilanco" and out["balance"]["dengede"] is True


def test_statement_kind_detection():
    from app.routers.ask import _statement_kind
    from app.cube_router import _norm
    assert _statement_kind(_norm("gelir tablosu")) == "gelir"
    assert _statement_kind(_norm("bu yıl bilanço")) == "bilanco"
    assert _statement_kind(_norm("makine bazında satış")) is None


def test_statement_result_table():
    from app.routers.ask import _statement_result
    r = _statement_result({"kind": "gelir",
                           "statement": [{"label": "Brüt Satışlar", "amount": 1000, "kind": "line"}]})
    assert r.columns == ["Kalem", "Tutar (₺)"]
    assert r.rows[0]["Kalem"] == "Brüt Satışlar" and r.rows[0]["Tutar (₺)"] == 1000
