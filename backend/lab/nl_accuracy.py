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
# ## Vaka setinin İKİ YARISI ve neden ikisi de gerekli (Faz A2, 3 Ağustos 2026)
#
# **1 · KATALOGDAN ÜRETİLEN (30 vaka).** Her cube'un belirsiz OLMAYAN ölçüleri + ilk
# boyutu. Bunlar **inşa gereği** doğrudur (üretilirken `route()`'un o cube'a çözdüğü
# doğrulandı) — yani *yargı* değil **REGRESYON** değeri taşırlar: bugün doğru olanın
# yarın da doğru kalmasını kilitlerler. Tek başlarına yeterli DEĞİLDİR ve öyleymiş gibi
# sunulmaları yanıltıcı olurdu.
#
# **2 · ZOR KAZANILMIŞ VAKALAR (aşağıda `# ⟳` ile).** Bu oturumda ÖLÇÜLEREK bulunmuş ve
# düzeltilmiş kusurlar. Asıl değer burada: her biri bir kez gerçekten YANLIŞ cevap
# vermişti ve hangi ilkeyle düzeldiği kayıtlı.
#
# ⚠️ Bu ayrım **açıkça yazıldı** çünkü üretilen vakaların %100 geçmesi bir başarı
# göstergesi DEĞİLDİR — tautolojidir. Kapının gücü ikinci yarıdan gelir.
CASES: dict[str, list[dict]] = {
    "boyahane": [
        {"q": "makine bazında ortalama oee bu yıl", "cube": "oee",
         "measures": ["ort_oee"], "dims": ["makine"]},

        # ── KATALOGDAN ÜRETİLEN (regresyon kilidi) ────────────────────────────────
        {"q": "bu yıl arıza sayısı", "cube": "bakim", "measures": ["ariza_sayisi"]},
        {"q": "bu yıl arıza duruşu", "cube": "bakim", "measures": ["toplam_durus_dakika"]},
        {"q": "bu yıl ortalama duruş", "cube": "bakim", "measures": ["ort_durus_dakika"]},
        {"q": "bu yıl hareket sayısı", "cube": "cari", "measures": ["hareket_sayisi"]},
        {"q": "bu yıl enpg", "cube": "enerji_sapma", "measures": ["toplam_enpg"]},
        {"q": "bu yıl sapma yüzdesi", "cube": "enerji_sapma", "measures": ["sapma_yuzde"]},
        {"q": "bu yıl gerçekleşen", "cube": "enerji_sapma", "measures": ["toplam_gerceklesen"]},
        {"q": "bu yıl ges payı", "cube": "enerji_tesis", "measures": ["ges_payi_yuzde"]},
        {"q": "bu yıl birim bedel", "cube": "enerji_tesis", "measures": ["birim_elektrik_tl_kwh"]},
        {"q": "bu yıl elektrik yoğunluğu tesis", "cube": "enerji_tesis", "measures": ["elektrik_yogunlugu_kwh_kg"]},
        {"q": "bu yıl brüt maaş", "cube": "ik", "measures": ["toplam_brut_maas"]},
        {"q": "bu yıl net maaş", "cube": "ik", "measures": ["toplam_net_maas"]},
        {"q": "bu yıl işveren maliyeti", "cube": "ik", "measures": ["toplam_isveren_maliyeti"]},
        {"q": "bu yıl rework kg", "cube": "kalite", "measures": ["toplam_rework_kg"]},
        {"q": "bu yıl rework sayısı", "cube": "kalite", "measures": ["rework_sayisi"]},
        {"q": "bu yıl ek süre", "cube": "kalite", "measures": ["toplam_ek_sure_dk"]},
        {"q": "bu yıl toplam duruş dakikası", "cube": "makine_duruslari", "measures": ["toplam_sure_dk"]},
        {"q": "bu yıl duruş sayısı", "cube": "makine_duruslari", "measures": ["duru\u015f_sayisi"]},
        {"q": "bu yıl kullanılabilirlik", "cube": "oee", "measures": ["ort_kullanilabilirlik"]},
        {"q": "bu yıl performans", "cube": "oee", "measures": ["ort_performans"]},
        {"q": "bu yıl kalite", "cube": "oee", "measures": ["ort_kalite"]},
        {"q": "bu yıl fire", "cube": "parti", "measures": ["toplam_fire_kg"]},
        {"q": "bu yıl fire oranı", "cube": "parti", "measures": ["fire_orani_yuzde"]},
        {"q": "bu yıl ağırlık", "cube": "parti", "measures": ["toplam_agirlik_kg"]},
        {"q": "bu yıl su yoğunluğu", "cube": "surdurulebilirlik", "measures": ["su_yogunlugu_lt_kg"]},
        {"q": "bu yıl enerji yoğunluğu", "cube": "surdurulebilirlik", "measures": ["enerji_yogunlugu_kwh_kg"]},
        {"q": "bu yıl doğalgaz yoğunluğu", "cube": "surdurulebilirlik", "measures": ["dogalgaz_yogunlugu_sm3_kg"]},
        {"q": "bu yıl matrah", "cube": "ticaret", "measures": ["toplam_matrah"]},
        {"q": "bu yıl fatura tutarı", "cube": "ticaret", "measures": ["toplam_tutar"]},
        {"q": "bu yıl fatura sayısı", "cube": "ticaret", "measures": ["fatura_sayisi"]},

        # ── ⟳ ZOR KAZANILMIŞ: 2a-3 "en spesifik ölçü kazanır" (kimlik asimetrisi) ──
        # `parti` kimliğindeki çıplak "sapma", `enerji_sapma`'nın "sapma yüzdesi"ni
        # gölgeliyordu; `_match_cube`'un tek-aday dalı ölçü-kanıtını uygulamıyordu.
        {"q": "bu yıl sapma yüzdesi", "cube": "enerji_sapma", "measures": ["sapma_yuzde"]},

        # ── ⟳ ZOR KAZANILMIŞ: 2a-1 `elektrik` ailesi (kimlik SİLMEDEN çözüldü) ─────
        # Sinonimi taşımak erişimi %64→%56 düşürmüştü; doğru çözüm SPESİFİKLİKTİ.
        #
        # ⚠️ **ETİKETİ ÖNCE YANLIŞ YAZDIM** (`enerji_tesis`) ve alet yakaladı. Katalogdan
        # doğrulandı: `elektrik tuketimi` **`enerji_makine.toplam_elektrik_kwh`**'nin
        # BİREBİR sinonimi; `enerji_tesis`'inki NİTELİKLİ (*"elektrik tuketimi tesis"*).
        # Yani sistem doğru, beklentim yanlıştı — bu turda **beşinci** kez.
        # Etiketli vaka setinin değeri tam da bu: beklentiyi yazmak, onu SINANABİLİR yapar.
        {"q": "bu yıl elektrik tüketimi", "cube": "enerji_makine",
         "measures": ["toplam_elektrik_kwh"]},
        {"q": "bu yıl doğalgaz tüketimi", "cube": "enerji_makine",
         "measures": ["toplam_dogalgaz_sm3"]},
        # Nitelikli biçim AYRI cube'a gitmeli — spesifiklik kuralının ters yönü:
        {"q": "bu yıl toplam elektrik", "cube": "enerji_tesis",
         "measures": ["elektrik_tuketimi_kwh"]},

        # ── ⟳ ZOR KAZANILMIŞ: 2a-5 liste niyeti — GERÇEK kırılım şart ─────────────
        # R2'yi tümden kaldırmak "döküm" isteğine dejenere tek toplam döndürürdü.
        {"q": "bu yıl en çok ciro yapan 10 müşteriyi listele", "cube": "parti",
         "measures": ["toplam_ciro"], "dims": ["musteri"]},

        # ── ⟳ ZOR KAZANILMIŞ: -0.5a bitişik çoklu ay (sessiz "yalnız Ocak") ───────
        {"q": "ocak şubat mart ayları ciro", "cube": "parti", "measures": ["toplam_ciro"]},

        # ── ⟳ ZOR KAZANILMIŞ: 2a-4 ayrık ay (motor ifade edemiyordu) ─────────────
        {"q": "ocak ve mart ayları toplam fire", "cube": "parti",
         "measures": ["toplam_fire_kg"]},

        # ── ⟳ ZOR KAZANILMIŞ: D1 sosyal önek bir veri sorusunu DÜŞÜRMEZ ──────────
        # Ölçüldü: "merhaba …" → R10, "iyi çalışmalar, …" → R1 (`oee` sinonimi
        # `calisma` rakip kimlik enjekte ediyordu).
        {"q": "merhaba bu yıl makine bazında oee", "cube": "oee",
         "measures": ["ort_oee"], "dims": ["makine"]},
        {"q": "teşekkürler, bu yıl toplam ciro ne kadar", "cube": "parti",
         "measures": ["toplam_ciro"]},
        {"q": "iyi çalışmalar, geçen ay fire nedir", "cube": "parti",
         "measures": ["toplam_fire_kg"]},

        # ── ⟳ ZOR KAZANILMIŞ: 1b sızıntı kapanı (jenerik token kardeş boyutu çekmez)
        {"q": "bu yıl müşteri bazında ciro", "cube": "parti",
         "measures": ["toplam_ciro"], "dims": ["musteri"]},
    ],
    # ── DÖRT ŞİRKET: farklı KATALOGLAR, aynı kapı ────────────────────────────────
    # `nl_corpus` bu şirketleri "doğru cube'a düştü mü" düzeyinde ölçüyor; burada
    # ölçü/boyut düzeyinde kilitleniyorlar. Sinonim çakışması katalog başına farklı
    # olduğu için (aynı kelime farklı cube'a ait olabilir) bu ayrı bir kapıdır.
    "atiksan": [
        {"q": "bu yıl borç", "cube": "cari", "measures": ["toplam_borc"]},
        {"q": "bu yıl alacak", "cube": "cari", "measures": ["toplam_alacak"]},
        {"q": "bu yıl açık bakiye", "cube": "cari_finans", "measures": ["acik_bakiye"]},
        {"q": "bu yıl açık borç", "cube": "cari_finans", "measures": ["acik_borc"]},
        {"q": "bu yıl brüt kar", "cube": "karlilik", "measures": ["brut_kar"]},
        {"q": "bu yıl marj", "cube": "karlilik", "measures": ["brut_marj_yuzde"]},
        {"q": "bu yıl satış miktarı", "cube": "ticaret", "measures": ["satis_miktari"]},
        {"q": "bu yıl alım", "cube": "ticaret", "measures": ["alim_tutari"]},
    ],
    "gulteks": [
        {"q": "bu yıl borç", "cube": "cari", "measures": ["toplam_borc"]},
        {"q": "bu yıl alacak", "cube": "cari", "measures": ["toplam_alacak"]},
        {"q": "bu yıl açık bakiye", "cube": "cari_finans", "measures": ["acik_bakiye"]},
        {"q": "bu yıl açık borç", "cube": "cari_finans", "measures": ["acik_borc"]},
        {"q": "bu yıl brüt kar", "cube": "karlilik", "measures": ["brut_kar"]},
        {"q": "bu yıl marj", "cube": "karlilik", "measures": ["brut_marj_yuzde"]},
        {"q": "bu yıl satış miktarı", "cube": "mal", "measures": ["satis_miktari"]},
        {"q": "bu yıl alım miktarı", "cube": "mal", "measures": ["alim_miktari"]},
        {"q": "bu yıl brüt satış", "cube": "ticaret", "measures": ["brut_satis"]},
        {"q": "bu yıl alım", "cube": "ticaret", "measures": ["alim_tutari"]},
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



# ---------------------------------------------------------------- FAZ A3: A/B KOŞUCUSU

class _BayrakZorla:
    """Bir bayrağı AÇIK ya da KAPALI zorlar — YAML/DB'ye dokunmadan.

    `app.features.resolve_for` **her tüketicide fonksiyon içinde** import ediliyor
    (`ask.py:123`, `answer.py:245` …) → modül düzeyinde yamalamak hepsini kapsar.
    YAML dosyasını değiştirmek yerine bu yol seçildi: ölçüm, ölçtüğü sistemin
    yapılandırmasını **kalıcı olarak değiştirmemelidir**.
    """

    def __init__(self, bayrak: str, acik: bool):
        self.bayrak, self.acik, self._eski = bayrak, acik, None

    def __enter__(self):
        from app import features

        self._eski = features.resolve_for

        def _sarmal(settings, principal=None):
            f = dict(self._eski(settings, principal))
            if self.acik:
                f[self.bayrak] = "beta"
            else:
                f.pop(self.bayrak, None)
            return f

        features.resolve_for = _sarmal
        return self

    def __exit__(self, *a):
        from app import features

        features.resolve_for = self._eski
        return False


def _vakalari_kos(c, cases: list[dict]) -> dict[str, bool]:
    """Vaka → geçti mi. Aynı istemci, aynı sıra; yalnız bayrak değişir."""
    out = {}
    for case in cases:
        d = c.post("/ask", json={"question": case["q"], "execute": False}).json()
        out[case["q"]] = not _check(case, d)
    return out


def ab_kos(bayrak: str) -> int:
    """A/B: etiketli vaka seti bayrak KAPALI vs AÇIK — **gerileme** ölçümü.

    ## Neden bu ölçüm, "kazanç" ölçümünden AYRI

    Etiketli vakaların hepsi `route()`'un zaten çözdüğü sorulardır. Bir LLM bayrağı
    burada **kazanç üretemez** (kazanılacak bir şey yok) — ama **bozabilir**. Yani bu
    koşum, planın B2 ölçütünün ikinci yarısıdır: *"…ve doğru-cube GERİLEMEDİ."*

    Kazanç yarısı ayrı bir korpus ister (bayrağın hedef nüfusu): `prompt_enhancer` için
    `route()`'un ÇÖZEMEDİĞİ sorular — onu `--ab-kurtarma` ölçer.
    """
    print(f"A/B — bayrak: {bayrak!r}   (etiketli vaka seti · GERİLEME ölçümü)", flush=True)
    toplam_bozulan, toplam_kurtarilan, toplam = 0, 0, 0
    for name, (login, pw, slug) in ACCOUNTS.items():
        cases = CASES.get(name) or []
        if not cases:
            continue
        c = _client(login, pw, slug)
        try:
            with _BayrakZorla(bayrak, acik=False):
                kapali = _vakalari_kos(c, cases)
            with _BayrakZorla(bayrak, acik=True):
                acik = _vakalari_kos(c, cases)
        finally:
            c.__exit__(None, None, None)
        bozulan = [q for q in kapali if kapali[q] and not acik[q]]
        kurtarilan = [q for q in kapali if not kapali[q] and acik[q]]
        toplam += len(cases)
        toplam_bozulan += len(bozulan)
        toplam_kurtarilan += len(kurtarilan)
        print(f"  [{name}] {len(cases)} vaka · bozulan={len(bozulan)} "
              f"kurtarılan={len(kurtarilan)}")
        for q in bozulan:
            print(f"      ✗ BOZULDU: {q!r}")
        for q in kurtarilan:
            print(f"      ✓ kurtarıldı: {q!r}")
    print(f"\n=== A/B {bayrak}: {toplam} vaka · BOZULAN {toplam_bozulan} · "
          f"kurtarılan {toplam_kurtarilan} ===")
    if toplam_bozulan:
        print("KAPI KIRMIZI — bayrak çalışan bir vakayı bozuyor.")
    return 1 if toplam_bozulan else 0


def ab_kurtarma_kos(bayrak: str, n: int = 20) -> int:
    """A/B: `route()`'un ÇÖZEMEDİĞİ sorularda bayrak kaç soruyu KURTARIYOR — **kazanç**.

    Korpus **katalogdan** üretilir (elle soru yazmak ölçümü kurgulardı): `route()`'un
    çözemediği ölçü sinonimleri — LLM yollarının GERÇEK tüketicisi orasıdır.

    ⚠️ Gerçek sağlayıcı ister (`--live`); `rule` ile koşmak LLM hakkında hiçbir şey
    ölçmez. Hız sınırı: tur arası bekleme (10 sn'de 10 istek tavanı).
    """
    import time

    from app import cube_router as cr

    login, pw, slug = ACCOUNTS["boyahane"]
    c = _client(login, pw, slug)
    sch = c.get("/schema").json()
    adaylar, gorulen = [], set()
    for cube in sch.get("cubes") or []:
        for syns in (cube.get("measure_synonyms") or {}).values():
            for sy in syns:
                nrm = cr._norm(str(sy))
                if nrm in gorulen or len(nrm) < 4:
                    continue
                gorulen.add(nrm)
                cr.reddi_sifirla()
                if cr.route(f"bu yil {sy}", sch) is None:
                    adaylar.append(f"bu yıl {sy}")
    secilen = adaylar[:n]
    print(f"A/B KURTARMA — bayrak: {bayrak!r} · korpus: {len(adaylar)} çözülemeyen "
          f"soru → örneklem {len(secilen)}", flush=True)

    def _kos(acik: bool) -> set[str]:
        cevaplanan = set()
        with _BayrakZorla(bayrak, acik=acik):
            for q in secilen:
                d = c.post("/ask", json={"question": q, "execute": False}).json()
                if d.get("sql") or (d.get("cube_query") or {}).get("cube"):
                    cevaplanan.add(q)
                time.sleep(5.0)
        return cevaplanan

    kapali = _kos(False)
    acik = _kos(True)
    c.__exit__(None, None, None)
    kurtarilan = sorted(acik - kapali)
    kaybedilen = sorted(kapali - acik)
    print(f"\n  bayrak KAPALI cevaplanan : {len(kapali)}/{len(secilen)}")
    print(f"  bayrak AÇIK   cevaplanan : {len(acik)}/{len(secilen)}")
    print(f"  KURTARILAN: {len(kurtarilan)}  ·  kaybedilen: {len(kaybedilen)}")
    for q in kurtarilan[:8]:
        print(f"      ✓ {q!r}")
    for q in kaybedilen[:8]:
        print(f"      ✗ KAYBEDİLDİ: {q!r}")
    print("\nKABUL ÖLÇÜTÜ (B2): kurtarma > 0 VE etiketli sette bozulan = 0.")
    return 0


def main() -> int:
    if "--live" in sys.argv:
        _sag = _canli_ortami_geri_yukle()
        print(f"CANLI MOD — sağlayıcı: {_sag} · embedder: "
              f"{os.environ.get('DIMA_VQR_EMBEDDER') or 'AÇIK (varsayılan)'}", flush=True)
    if "--ab" in sys.argv:
        return ab_kos(sys.argv[sys.argv.index("--ab") + 1])
    if "--ab-kurtarma" in sys.argv:
        return ab_kurtarma_kos(sys.argv[sys.argv.index("--ab-kurtarma") + 1])
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
