"""CI kapısı (literatür #5): answered-precision baseline'ın altına DÜŞEMEZ.

Eval, golden testlerden farklı olarak toplu davranış ölçer (eval/run.py):
    answered-precision = doğru cevap / tüm cevaplar  (yanlış-cevap oranının tersi)
    coverage           = cevaplanan / cevap-verilebilir vakalar

Kural (kullanıcı politikası "muazzam doğruluk"): hiçbir değişiklik yanlış-cevap
oranını ARTIRAMAZ. Coverage'a küçük tolerans tanınır (bilinçli bir dürüstlük kapısı
coverage'ı düşürebilir) — ama bunun da baseline'ı güncellenerek KAYDA GEÇMESİ gerekir:
    .venv/bin/python -m eval.run --update-baseline
"""

from __future__ import annotations

import json

import yaml

from eval.run import BASELINE, CASES, run_cases

COVERAGE_TOLERANCE = 0.02  # bilinçli dürüstlük değişimleri için küçük pay


def test_eval_gate_answered_precision_dusmez(client):
    cases = yaml.safe_load(CASES.read_text())
    m = run_cases(client, cases, slice_="det")
    b = json.loads(BASELINE.read_text())

    fails = "\n".join(
        f"  {f['id']}: bekl={f['expect']} oldu={f['actual']} {f['note']}"
        for f in m["failures"]
    )
    assert m["answered_precision"] >= b["answered_precision"], (
        f"answered-precision DÜŞTÜ: {m['answered_precision']:.1%} < "
        f"{b['answered_precision']:.1%} (baseline)\n{fails}"
    )
    assert m["coverage"] >= b["coverage"] - COVERAGE_TOLERANCE, (
        f"coverage baseline'ın belirgin altında: {m['coverage']:.1%} < "
        f"{b['coverage']:.1%} - {COVERAGE_TOLERANCE:.0%}\n{fails}"
    )


def test_eval_gate_deterministik_pay_dusmez(client):
    """Kapsam LLM'e KAYARAK artmasın (2 Ağustos 2026).

    Önceki kapı yalnız "doğru cevap oranı"na bakıyordu ve `classify()` `source` dolu olan
    her şeyi "answer" sayıyor — yani bir soru cube yolundan Discovery'ye kayarsa precision
    ve coverage AYNI kalır, kapı SESSİZ geçer. Oysa iki cevabın taşıdığı garanti farklı:
    cube cevabı chip/kırılım/drill/Query Contract taşır, Discovery cevabı tek atımlık düz
    tablodur (ve `always_filter`'ı baypas eder). Ürünün ana KPI'ı da budur:
    "Intent ≥%70 · Discovery <%30".

    Deterministik dilim (`DIMA_LLM_PROVIDER=rule`, ağsız) için beklenen pay 1.0'dır —
    bu dilimde bir cevabın `rule`/`llm:` kaynaklı olması, deterministik katmanın o soruyu
    kapsayamadığı anlamına gelir.
    """
    cases = yaml.safe_load(CASES.read_text())
    m = run_cases(client, cases, slice_="det")
    b = json.loads(BASELINE.read_text())
    floor = b.get("deterministic_share", 1.0)

    kaçanlar = "\n".join(
        f"  {r['id']}: source={r.get('source')} yol={r.get('path')}"
        for r in m["records"]
        if r["actual"] == "answer" and r.get("path") not in ("intent", "cache", "meta_katalog")
    )
    assert m["deterministic_share"] >= floor, (
        f"deterministik pay DÜŞTÜ: {m['deterministic_share']:.1%} < {floor:.1%} (baseline)\n"
        f"LLM'e kaçan cevaplar:\n{kaçanlar}"
    )
