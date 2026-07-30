"""NL senaryo harness'i — kurgu yeniden-tasarımının kanıt motoru (2026-07-24).

Katalogdan (boyahane + atiksan/mikro) OTOMATİK senaryo üretir: yeni-soru şablonları
(ölçü × dönem × kırılım × top-N) + takip zincirleri (gran/kırılım/top-N/çapraz-cube/
saçma metin). Her turu /ask'e koşar, sonucu sınıflandırır (OK/CLARIFY/NOTE/HATA/
YANLIŞ-CUBE) ve taksonomi raporu üretir. LLM YOK (rule provider) — tamamen
deterministik katman ölçülür; commit edilmez, çalışma-ağacı prototiplerini ölçmek içindir.

Koşum:  .venv/bin/python lab/nl_harness.py [--company atiksan] [--limit 300]
Çıktı:  lab/reports/nl_harness_<company>.md
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tests.conftest as conftest  # noqa: E402  (env kurulumunu tetikler)
from tests.conftest import TEST_USER, make_tenant_user  # noqa: E402

PERIODS = ["bu yıl", "geçen ay", "son 3 ay", "temmuz ayı", "2. çeyrek", ""]
FOLLOWUPS_GRAN = ["aylık", "haftalık", "günlük", "çeyreklere göre", "kova:çeyrek"]
FOLLOWUPS_MISC = ["en düşük 3", "ilk 5", "tüm zamanlar", "asdf qwerty", "teşekkürler",
                  "kırılımları ver", "kırılımları göster", "hangi kırılımlar var",
                  "haftanın günlerine göre"]


def _client(company_user: tuple[str, str, str | None]):
    from fastapi.testclient import TestClient

    from app.main import create_app

    email, pw, slug = company_user
    make_tenant_user(email, pw, tenant_slug=slug)  # slug None → aktif şirket
    c = TestClient(create_app())
    c.__enter__()
    r = c.post("/auth/login", json={"email": email, "password": pw})
    assert r.status_code == 200, r.text
    c.headers["Authorization"] = f"Bearer {r.json()['access_token']}"
    return c


def _ask(c, question: str, cq=None):
    body = {"question": question, "execute": False}
    if cq is not None:
        body["cube_query"] = cq
        body["history"] = ["önceki soru"]
    r = c.post("/ask", json=body)
    if r.status_code != 200:
        return {"_http": r.status_code, "note": r.text[:120], "trace": []}
    return r.json()


def _sinif(d, expected_cube=None):
    if d.get("_http"):
        return f"HTTP{d['_http']}"
    if d.get("sql"):
        cube = (d.get("cube_query") or {}).get("cube")
        if expected_cube and cube != expected_cube:
            return f"YANLIS-CUBE({cube}≠{expected_cube})"
        return "OK"
    note = d.get("note") or ""
    if "dönem" in note or "Hangi dönem" in note:
        return "CLARIFY:dönem"
    if "ölçü" in note:
        return "CLARIFY:ölçü"
    if note:
        return "NOTE"
    return "BOŞ"


def scenarios_from_schema(schema: dict, limit: int):
    """Katalogdan senaryo üret: her cube ölçü-sinonimi × dönem × (kırılım) × (top-N)."""
    out = []
    for cube in schema.get("cubes", []):
        cname = cube["name"]
        dims = cube.get("dimension_labels") or {}
        dim_words = [v for v in dims.values() if v][:2]
        for m, syns in (cube.get("measure_synonyms_display") or {}).items():
            word = syns if isinstance(syns, str) else (syns or [m])[0]
            for period in PERIODS:
                q = f"{period} {word}".strip()
                out.append(("yeni", q, cname))
                for dw in dim_words:
                    out.append(("yeni", f"{period} {dw} bazında {word}".strip(), cname))
                out.append(("yeni", f"en çok {word} yapılan 5 {dim_words[0] if dim_words else 'kayıt'} {period}".strip(), cname))
    # tekilleştir + kırp
    seen, uniq = set(), []
    for s in out:
        if s[1] not in seen:
            seen.add(s[1])
            uniq.append(s)
    return uniq[:limit]


def followup_chains(schema: dict):
    """Rapor aç → takip zinciri senaryoları (gran, top-N, çapraz-cube, gürültü)."""
    cubes = schema.get("cubes", [])
    chains = []
    for cube in cubes:
        m0 = (cube.get("measures") or [None])[0]
        if not m0:
            continue
        base_q = f"bu yıl {((cube.get('measure_synonyms_display') or {}).get(m0)) or m0}"
        steps = FOLLOWUPS_GRAN + FOLLOWUPS_MISC
        # çapraz-cube: diğer cube'ların ölçü kelimeleri
        for other in cubes:
            if other["name"] == cube["name"]:
                continue
            om = (other.get("measures") or [None])[0]
            if om:
                disp = (other.get("measure_synonyms_display") or {}).get(om) or om
                steps.append(f"ÇAPRAZ::{other['name']}::{disp} bazında değil {disp} göster")
                steps.append(f"ÇAPRAZ::{other['name']}::{disp}")
        chains.append((cube["name"], base_q, steps))
    return chains


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--company", default="boyahane",
                    choices=["boyahane", "atiksan"])
    ap.add_argument("--limit", type=int, default=300)
    args = ap.parse_args()

    if args.company == "atiksan":
        cu = ("owner@atiksan.test", "atiksan-parola-1", "atiksan")
    else:
        cu = (TEST_USER["email"], TEST_USER["password"], None)
    c = _client(cu)
    schema = c.get("/schema").json()

    results = Counter()
    fails: dict[str, list] = defaultdict(list)

    # 1) Yeni-soru senaryoları
    scen = scenarios_from_schema(schema, args.limit)
    for kind, q, expected in scen:
        d = _ask(c, q)
        s = _sinif(d, expected_cube=expected)
        results[f"yeni::{s}"] += 1
        if s.startswith(("YANLIS", "HTTP", "BOŞ")) or (s == "NOTE"):
            fails[s].append((q, (d.get("note") or "")[:80], d.get("trace", [])[-1:]))

    # 2) Takip zincirleri
    for cname, base_q, steps in followup_chains(schema):
        d0 = _ask(c, base_q)
        cq = d0.get("cube_query")
        if not d0.get("sql") or not cq:
            results["zincir::BAŞLATILAMADI"] += 1
            continue
        for step in steps:
            expected = None
            q = step
            if step.startswith("ÇAPRAZ::"):
                _, expected, q = step.split("::", 2)
            d = _ask(c, q, cq=cq)
            s = _sinif(d, expected_cube=expected)
            tag = "çapraz" if expected else "takip"
            results[f"{tag}::{s}"] += 1
            if s.startswith(("YANLIS", "HTTP", "BOŞ")) or (expected and s == "NOTE"):
                fails[f"{tag}:{s}"].append(
                    (f"[{cname}] {q}", (d.get("note") or "")[:80], d.get("trace", [])[-1:]))

    out = Path("lab/reports") / f"nl_harness_{args.company}.md"
    out.parent.mkdir(exist_ok=True)
    lines = [f"# NL harness — {args.company} ({sum(results.values())} tur)\n"]
    lines.append("## Sonuç dağılımı\n")
    for k, v in sorted(results.items()):
        lines.append(f"- {k}: {v}")
    lines.append("\n## Hata örnekleri\n")
    for k, items in fails.items():
        lines.append(f"### {k} ({len(items)})")
        for q, note, tr in items[:15]:
            lines.append(f"- `{q}` → {note} {tr}")
    out.write_text("\n".join(lines))
    print(f"\nRapor: {out}")
    for k, v in sorted(results.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
