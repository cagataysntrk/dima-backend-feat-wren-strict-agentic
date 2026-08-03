"""Çok-şirketli DOĞRULUK kapısı (§1) — etiketli soru → beklenen {cube, ölçü, boyut}.

`nl_corpus.py` "cube'a düştü mü"yü ölçer; bu harness "DOĞRU cube/ölçü/boyut mu"yu ölçer
(etiketli beklenti + regresyon kapısı). DB-BAĞIMSIZ (execute=False + enrichment no-op) →
dört şirket yerelde/hızlı. LLM yok (rule provider) → deterministik çekirdeğin tavanı.

Vaka şeması (CASES[company] elemanı) — verilen anahtarlar KISMİ asserte edilir:
  q          : soru (zorunlu)
  cube       : beklenen cube adı (opsiyonel)
  measures   : yanıtta BULUNMASI gereken ölçüler (⊇)
  dims       : yanıtta BULUNMASI gereken boyutlar (⊇)
  not_dims   : yanıtta BULUNMAMASI gereken boyutlar (∩ = ∅) — 1b tipi sızıntı kapanı

Koşum:  .venv/bin/python -m lab.nl_accuracy               # etiketli tüm şirketler
        .venv/bin/python -m lab.nl_accuracy --company gitas
Çıkış kodu: herhangi bir vaka FAIL → 1 (CI/regresyon kapısı olarak kullanılabilir).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

#: ⚠️ **`tests.conftest` IMPORT EDİLİR EDİLMEZ SAĞLAYICIYI SABİTLER** (`conftest.py:15`
#: koşulsuz `DIMA_LLM_PROVIDER="rule"`, `:26` `DIMA_VQR_EMBEDDER="off"`) — testlerin ağa
#: çıkmaması için DOĞRU bir karardır. Ama bu dosya o modülü **env kurulumu** için import
#: ediyor ve yan etkiyi de devralıyordu.
#:
#: Aynı kusur `konusma_senaryolari.py`'de ölçülmüştü: `--live` **hiçbir zaman canlı
#: değildi**. Bu araç `route()`'un deterministik tavanını ölçer (LLM'siz doğru), ama Faz
#: 3b/4/5'in **kazancı** yalnız gerçek sağlayıcıyla ölçülebilir — o yüzden `--live` burada
#: da gerekiyor ve aynı kalıpla kuruldu (kopyalama değil, **aynı sözleşme**).
_GERCEK_ORTAM = {k: os.environ.get(k) for k in
                 ("DIMA_LLM_PROVIDER", "DIMA_VQR_EMBEDDER", "DIMA_INTERACTION_LOG",
                  "DIMA_DATABASE_URL")}

import tests.conftest as _conf  # noqa: E402,F401  (env kurulumu)
from tests.conftest import make_tenant_user  # noqa: E402


def _canli_ortami_geri_yukle() -> str:
    """`--live` için gerçek sağlayıcıyı geri koyar. Döner: sağlayıcı adı.

    Fail-closed: gerçek sağlayıcı yoksa `SystemExit`. Sessizce `rule` ile koşan bir
    "canlı" ölçüm, hiç koşmamaktan **kötüdür** — yanlış bir güven verir ve o güvene
    dayanarak bayrak kararı alınır.

    `DIMA_DATABASE_URL` conftest'in **izolasyonunu korur** (ortamda açıkça verilmişse ona
    uyulur): canlı bir ölçüm kullanıcının verisini kirletmemelidir.
    """
    CANLI_YOLU_SUSTURANLAR = ("DIMA_LLM_PROVIDER", "DIMA_VQR_EMBEDDER",
                              "DIMA_INTERACTION_LOG")
    for k, v in _GERCEK_ORTAM.items():
        if v is not None:
            os.environ[k] = v
        elif k in CANLI_YOLU_SUSTURANLAR:
            os.environ.pop(k, None)
    saglayici = os.environ.get("DIMA_LLM_PROVIDER", "")
    if saglayici in ("", "rule"):
        raise SystemExit(
            "--live GERÇEK bir sağlayıcı ister. `DIMA_LLM_PROVIDER` boş ya da 'rule' — "
            "bu modda koşmak LLM yolları hakkında HİÇBİR ŞEY ölçmez ve 'canlı' etiketi "
            "yanıltır. Sağlayıcıyı ve API anahtarını ayarlayıp tekrar deneyin.")
    return saglayici

# Şirket → (login, parola, tenant_slug). demo-boyahane aktif şirket (slug=None).
ACCOUNTS = {
    "boyahane": ("owner@dima.local", "owner-parola-123", None),
    "atiksan": ("owner@atiksan.test", "atiksan-parola-1", "atiksan"),
    "gulteks": ("owner@gulteks.test", "gulteks-parola-1", "gulteks"),
    "gitas": ("owner@gitas.test", "gitas-parola-1", "gitas"),
}

# Etiketli vakalar (iskelet + 1b — tam set sonraki faz). Domain-kritik + regresyon.
CASES: dict[str, list[dict]] = {
    "boyahane": [
        {"q": "makine bazında ortalama oee bu yıl", "cube": "oee",
         "measures": ["ort_oee"], "dims": ["makine"]},
    ],
    "gitas": [
        # 1b REGRESYON: jenerik "adı" token'ı kardeş cari_adi'yi ÇEKMEMELİ.
        # "stok adı" → yalnız stok_adi kırılımı; cari_adi 'adi' ile sızmamalı.
        {"q": "stok adı bazında satış miktarı bu yıl", "cube": "mal",
         "measures": ["satis_miktari"], "dims": ["stok_adi"], "not_dims": ["cari_adi"]},
        # Kontrol: "adı" olmadan da doğru (sızıntı olmadan zaten çalışıyordu).
        {"q": "stok bazında satış miktarı bu yıl", "cube": "mal",
         "dims": ["stok_adi"], "not_dims": ["cari_adi"]},
        # Nitelikli tek-entity: cari kırılımı; kod açıkça istenmedi → cari_kodu gelmemeli.
        {"q": "cari adı bazında bakiye", "cube": "cari",
         "dims": ["cari_adi"], "not_dims": ["cari_kodu"]},
    ],
}


def _client(login: str, pw: str, slug: str | None):
    from fastapi.testclient import TestClient

    import app.wren_service as ws
    from app.main import create_app

    # DB-bağımsız: canlı değer zenginleştirme + dry_plan no-op (routing kalitesi ölçülür,
    # icra değil). nl_corpus.py ile aynı desen.
    # ⚠️ **BU ARAÇ SESSİZCE KIRIKTI** (Faz A'da ölçüldü, 3 Ağustos 2026):
    # `TypeError: <lambda>() takes 2 positional arguments but 3 were given` → **her iki
    # şirket de yüklenemiyor, 0 vaka koşuyordu.** Sebep: imzalar DAR yazılmıştı ve
    # `dry_plan` zamanla üçüncü bir argüman kazandı. Kardeş araç
    # (`konusma_senaryolari.py`) `*a, **k` ile toleranslı yazılmış; bu dosya eski katı
    # hâlde kalmış ve **CI'da koşmadığı için** kimse fark etmemişti.
    #
    # MIMARI §6.4'ün dersi birebir tekrarladı: *"ölçüm aracının kendisi de bir
    # bağımlılıktır"* — `lab/nl_corpus.py` aylarca kırıkken de kimse fark etmemişti.
    # Kırık bir alet üstüne vaka seti büyütmek (A2), ölçmediğini ölçtüğünü sanmak olurdu.
    ws.WrenService._enrich_categorical = lambda self, *a, **k: None
    ws.WrenService._enrich_cube_dim_values = lambda self, *a, **k: None
    ws.WrenService.dry_plan = lambda self, sql, *a, **k: sql

    make_tenant_user(login, pw, tenant_slug=slug)
    c = TestClient(create_app())
    c.__enter__()
    r = c.post("/auth/login", json={"email": login, "password": pw})
    assert r.status_code == 200, f"login: {r.text}"
    c.headers["Authorization"] = f"Bearer {r.json()['access_token']}"
    return c


def _check(case: dict, d: dict) -> list[str]:
    """Beklentiyi yanıta karşı doğrular; ihlal listesi döner ([] = geçti)."""
    cq = d.get("cube_query") or {}
    errs: list[str] = []
    if "cube" in case and cq.get("cube") != case["cube"]:
        errs.append(f"cube={cq.get('cube')}≠{case['cube']}")
    got_m = set(cq.get("measures") or [])
    for m in case.get("measures", []):
        if m not in got_m:
            errs.append(f"ölçü '{m}' yok (got {sorted(got_m)})")
    got_d = set(cq.get("dimensions") or [])
    for dim in case.get("dims", []):
        if dim not in got_d:
            errs.append(f"boyut '{dim}' yok (got {sorted(got_d)})")
    for dim in case.get("not_dims", []):
        if dim in got_d:
            errs.append(f"boyut '{dim}' SIZDI (got {sorted(got_d)})")
    return errs


def run_company(name: str) -> tuple[int, int, list[str]]:
    login, pw, slug = ACCOUNTS[name]
    cases = CASES.get(name, [])
    if not cases:
        return (0, 0, [])
    c = _client(login, pw, slug)
    passed, failed, lines = 0, 0, []
    for case in cases:
        d = c.post("/ask", json={"question": case["q"], "execute": False}).json()
        errs = _check(case, d)
        if errs:
            failed += 1
            lines.append(f"  ✗ {case['q']!r} → {'; '.join(errs)}")
        else:
            passed += 1
            lines.append(f"  ✓ {case['q']!r}")
    c.__exit__(None, None, None)
    return (passed, failed, lines)


def main() -> int:
    if "--live" in sys.argv:
        _sag = _canli_ortami_geri_yukle()
        print(f"CANLI MOD — sağlayıcı: {_sag} · embedder: "
              f"{os.environ.get('DIMA_VQR_EMBEDDER') or 'AÇIK (varsayılan)'}", flush=True)
    only = None
    if "--company" in sys.argv:
        only = sys.argv[sys.argv.index("--company") + 1]
    companies = [only] if only else [n for n in ACCOUNTS if CASES.get(n)]
    total_p, total_f = 0, 0
    for name in companies:
        try:
            p, f, lines = run_company(name)
        except Exception as exc:  # noqa: BLE001 — şirket yüklenemedi, rapor et, diğerine geç
            print(f"\n[{name}] YÜKLENEMEDİ: {type(exc).__name__}: {exc}")
            total_f += 1
            continue
        total_p += p
        total_f += f
        print(f"\n[{name}] {p} geçti · {f} kaldı")
        for ln in lines:
            print(ln)
    print(f"\n=== TOPLAM: {total_p} geçti · {total_f} kaldı ===")
    return 1 if total_f else 0


if __name__ == "__main__":
    raise SystemExit(main())
