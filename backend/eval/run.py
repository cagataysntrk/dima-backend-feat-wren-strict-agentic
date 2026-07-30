"""Seçici-tahmin değerlendirmesi (literatür #5): coverage + answered-precision.

Golden testler "bozduk mu?" sorusuna, bu eval "ne kadar iyiyiz?" sorusuna cevap verir.
Her vaka beklenen davranışla etiketlidir — sistemin üç meşru çıktısı vardır (ADR-0008):

    answer  → kesin: rapor üretildi (beklenen ŞEKİL ile karşılaştırılır)
    chip    → şüphe: netleştirme chip'leri sunuldu
    refuse  → anlaşılmadı: dürüst not, rapor yok

Metrikler:
    answered-precision = doğru cevap / tüm cevaplar   (yanlış-cevap oranının tersi;
                         chip/red beklenirken cevap vermek de YANLIŞ cevaptır)
    coverage           = cevap verilen / cevap-verilebilir (beklenen=answer) vakalar

CI kapısı (tests/test_eval_gate.py): answered-precision baseline'ın ALTINA DÜŞEMEZ.

Kullanım:
    .venv/bin/python -m eval.run                 # det dilimi (LLM'siz, deterministik)
    .venv/bin/python -m eval.run --slice llm     # canlı LLM dilimi (anahtar gerekir)
    .venv/bin/python -m eval.run --update-baseline
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import yaml

EVAL_DIR = Path(__file__).resolve().parent
CASES = EVAL_DIR / "cases.yaml"
BASELINE = EVAL_DIR / "baseline.json"
REPORT = EVAL_DIR / "report.json"


# --------------------------------------------------------------------------- #
# Sonuç sınıflandırma ve şekil karşılaştırma
# --------------------------------------------------------------------------- #

def classify(d: dict) -> str:
    """AskResponse → answer | chip | refuse."""
    if d.get("source"):
        return "answer"
    if d.get("suggestions"):
        return "chip"
    return "refuse"


def shape_ok(cq: dict | None, shape: dict) -> bool:
    """Üretilen CubeQuery beklenen şekle uyuyor mu? (Yalnız verilen anahtarlar denetlenir.)"""
    if not cq:
        return False
    if shape.get("cube") and cq.get("cube") != shape["cube"]:
        return False
    if shape.get("measures") and cq.get("measures") != shape["measures"]:
        return False
    if "dims" in shape and (cq.get("dimensions") or []) != shape["dims"]:
        return False
    if "dims_has" in shape and not set(shape["dims_has"]) <= set(cq.get("dimensions") or []):
        return False
    if shape.get("gran"):
        tds = cq.get("timeDimensions") or [{}]
        if tds[0].get("granularity") != shape["gran"]:
            return False
    if "filter_ops" in shape:  # tarih filtresi operatörleri (dönem doğruluğu)
        ops = sorted(f.get("operator", "") for f in cq.get("filters", [])
                     if f.get("dimension") == "tarih")
        if ops != sorted(shape["filter_ops"]):
            return False
    if "filter_eq" in shape:  # kategorik değer filtreleri [[boyut, değer], ...]
        flt = {(f.get("dimension"), f.get("value")) for f in cq.get("filters", [])}
        if not all((d0, v) in flt for d0, v in shape["filter_eq"]):
            return False
    if "in_filter_dim" in shape:  # varlık top-N → `in` filtresi
        if not any(f.get("dimension") == shape["in_filter_dim"] and f.get("operator") == "in"
                   for f in cq.get("filters", [])):
            return False
    return True


def step_result(d: dict, expect: str, step: dict) -> tuple[str, bool]:
    """(actual, correct). correct: davranış VE (cevapsa) şekil/not doğru."""
    actual = classify(d)
    if actual != expect:
        return actual, False
    if expect == "answer":
        if "shape" in step:
            return actual, shape_ok(d.get("cube_query"), step["shape"])
        return actual, True
    if "note_contains" in step:
        return actual, step["note_contains"].lower() in (d.get("note") or "").lower()
    if "chip_labels_has" in step:
        labels = [s.get("label", "") for s in d.get("suggestions") or []]
        return actual, all(x in labels for x in step["chip_labels_has"])
    return actual, True


# --------------------------------------------------------------------------- #
# Koşucu
# --------------------------------------------------------------------------- #

def run_cases(client, cases: list[dict], slice_: str = "det") -> dict:
    """Vakaları koşar, ham kayıtları döner. Akışlarda cube_query/history zinciri taşınır."""
    records: list[dict] = []
    for case in cases:
        if case.get("slice", "det") != slice_:
            continue
        steps = case.get("flow") or [case]
        cq, hist = None, []
        for i, step in enumerate(steps):
            payload = {"question": step["q"], "execute": True,
                       "session_id": f"eval-{case['id']}"}
            if cq:
                payload["cube_query"] = cq
            if hist:
                payload["history"] = hist
            r = client.post("/ask", json=payload)
            d = r.json() if r.status_code == 200 else {}
            actual, correct = step_result(d, step["expect"], step)
            records.append({
                "id": case["id"] + (f"#{i}" if len(steps) > 1 else ""),
                "tags": case.get("tags", []),
                "expect": step["expect"],
                "actual": actual,
                "correct": correct,
                "note": (d.get("note") or "")[:80],
                "cq": d.get("cube_query"),
            })
            cq = d.get("cube_query") or cq  # rapor durumu zincirde taşınır (UI davranışı)
            hist = hist + [step["q"]]
    return score(records)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    """Oran + Wilson %95 güven aralığı (küçük örneklemde güvenilir)."""
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return p, max(0.0, center - half), min(1.0, center + half)


def score(records: list[dict]) -> dict:
    answered = [r for r in records if r["actual"] == "answer"]
    correct_answers = [r for r in answered if r["correct"]]
    answerable = [r for r in records if r["expect"] == "answer"]
    covered = [r for r in answerable if r["actual"] == "answer"]
    chips = [r for r in records if r["expect"] == "chip"]
    chips_ok = [r for r in chips if r["correct"]]

    p, plo, phi = wilson(len(correct_answers), len(answered))
    c, clo, chi = wilson(len(covered), len(answerable))

    tags: dict[str, list] = {}
    for r in records:
        for t in r["tags"]:
            tags.setdefault(t, []).append(r)
    by_tag = {
        t: {"n": len(rs), "ok": sum(1 for r in rs if r["correct"])}
        for t, rs in sorted(tags.items())
    }
    return {
        "n": len(records),
        "answered": len(answered),
        "answered_precision": round(p, 4),
        "precision_ci95": [round(plo, 4), round(phi, 4)],
        "coverage": round(c, 4),
        "coverage_ci95": [round(clo, 4), round(chi, 4)],
        "chip_accuracy": round(len(chips_ok) / len(chips), 4) if chips else None,
        "by_tag": by_tag,
        "failures": [
            {k: r[k] for k in ("id", "expect", "actual", "note")}
            for r in records if not r["correct"]
        ],
        "records": records,
    }


def print_report(m: dict) -> None:
    print(f"\n## dima eval — {m['n']} adım")
    print(f"answered-precision : {m['answered_precision']:.1%}  "
          f"(CI95 {m['precision_ci95'][0]:.1%}–{m['precision_ci95'][1]:.1%}, "
          f"{m['answered']} cevap)")
    print(f"coverage           : {m['coverage']:.1%}  "
          f"(CI95 {m['coverage_ci95'][0]:.1%}–{m['coverage_ci95'][1]:.1%})")
    if m["chip_accuracy"] is not None:
        print(f"chip-accuracy      : {m['chip_accuracy']:.1%}")
    print("\netiket           n    doğru")
    for t, v in m["by_tag"].items():
        flag = "" if v["ok"] == v["n"] else "  ←"
        print(f"{t:16s} {v['n']:3d} {v['ok']:5d}{flag}")
    if m["failures"]:
        print(f"\nBAŞARISIZ ({len(m['failures'])}):")
        for f in m["failures"]:
            print(f"  {f['id']:34s} bekl={f['expect']:6s} oldu={f['actual']:6s} {f['note']}")


def _login_eval_user(client) -> None:
    """İzole control-plane DB'de eval kullanıcısı yaratır ve Bearer header takar
    (tüm veri uçları auth ister — ADR-0014)."""
    from sqlmodel import Session

    from control_plane.db import engine, init_db
    from control_plane.models import Membership, Role, Tenant, User
    from control_plane.security import hash_password

    from app.config import get_settings

    init_db()
    with Session(engine) as s:
        # Veri-düzlemi tenant-RLS bağı: eval kullanıcısı AKTİF şirketin tenant'ında olmalı.
        tenant = Tenant(slug=get_settings().company, name="Eval")
        s.add(tenant)
        s.commit()
        s.refresh(tenant)
        role = Role(tenant_id=tenant.id, key="owner", name="Owner")
        s.add(role)
        s.commit()
        user = User(tenant_id=tenant.id, email="eval@dima.local",
                    password_hash=hash_password("eval-parola-123"))
        s.add(user)
        s.commit()
        s.refresh(user)
        s.add(Membership(tenant_id=tenant.id, user_id=user.id, role_id=role.id))
        s.commit()
    r = client.post("/auth/login",
                    json={"email": "eval@dima.local", "password": "eval-parola-123"})
    assert r.status_code == 200, f"eval login başarısız: {r.text}"
    client.headers["Authorization"] = f"Bearer {r.json()['access_token']}"


def main() -> None:
    import argparse
    import os

    ap = argparse.ArgumentParser()
    ap.add_argument("--slice", default="det", choices=["det", "llm"])
    ap.add_argument("--update-baseline", action="store_true")
    args = ap.parse_args()

    if args.slice == "det":  # LLM'siz, ağsız, deterministik koşum
        os.environ["DIMA_LLM_PROVIDER"] = "rule"
    import tempfile

    os.environ["DIMA_VQR_PATH"] = os.path.join(
        tempfile.mkdtemp(prefix="dima-eval-vqr-"), "queries.jsonl"
    )
    os.environ["DIMA_INTERACTION_LOG"] = "false"  # eval koşumu canlı logu kirletmez
    # (contracts artık contract_log DB'de; eski DIMA_CONTRACTS_PATH ölü env kaldırıldı —
    # eval control-plane'i aşağıdaki izole SQLite'a düşer.)
    os.environ["DIMA_SCHEDULER_ENABLED"] = "false"
    # Control-plane izolasyonu: eval canlı auth DB'sini kirletmez; secret'lar sabit.
    os.environ["DIMA_DATABASE_URL"] = "sqlite:///" + os.path.join(
        tempfile.mkdtemp(prefix="dima-eval-cp-"), "control_plane.db"
    )
    os.environ.setdefault("DIMA_JWT_SECRET", "eval-public-access-secret")
    os.environ.setdefault("DIMA_JWT_REFRESH_SECRET", "eval-public-refresh-secret")
    from fastapi.testclient import TestClient

    from app.compose import compose_and_build
    from app.config import get_settings
    from app.main import create_app

    get_settings.cache_clear()
    compose_and_build(get_settings())
    cases = yaml.safe_load(CASES.read_text())
    with TestClient(create_app()) as client:
        _login_eval_user(client)
        m = run_cases(client, cases, slice_=args.slice)
    print_report(m)
    REPORT.write_text(json.dumps(m, ensure_ascii=False, indent=1))
    if args.update_baseline:
        BASELINE.write_text(json.dumps(
            {k: m[k] for k in ("n", "answered", "answered_precision", "coverage")},
            ensure_ascii=False, indent=1,
        ))
        print(f"\nbaseline güncellendi → {BASELINE}")
    elif BASELINE.exists():
        b = json.loads(BASELINE.read_text())
        dp = m["answered_precision"] - b["answered_precision"]
        dc = m["coverage"] - b["coverage"]
        print(f"\nbaseline'a göre: precision {dp:+.1%} · coverage {dc:+.1%}")


if __name__ == "__main__":
    main()
