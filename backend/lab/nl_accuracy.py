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

#: ⚠️ CANLI ORTAM GERİ YÜKLEME — **TEK SAHİP**: `lab/konusma_senaryolari`.
#:
#: Burada bir KOPYASI vardı ve kopyanın bedeli ölçüldü (Faz X, 3 Ağustos 2026): tek
#: sahipteki sözleşme *"ortamı geri yükle"*den *"AYAR ÖNBELLEĞİNİ de temizle ve gerçekten
#: canlı bir üretici kurulduğunu DOĞRULA"*ya yükseltilirken **bu kopya geride kaldı** —
#: yani `nl_accuracy --live` hâlâ sessizce `rule` ile koşuyordu ve o koşumlara dayanarak
#: bayrak kararı alınabilirdi. Bu deponun bir numaralı kusur sınıfının ölçüm katmanındaki
#: hâli.
#:
#: Import SIRASI kritik: `konusma_senaryolari` gerçek ortamı `tests.conftest`'ten ÖNCE
#: yakalar; buradan (conftest'e dokunmadan önce) import etmek o yakalamayı devralır.
from lab.konusma_senaryolari import _canli_ortami_geri_yukle  # noqa: E402

import tests.conftest as _conf  # noqa: E402,F401  (env kurulumu)
from tests.conftest import make_tenant_user  # noqa: E402


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
    """A/B: `route()`'un ÇÖZEMEDİĞİ **doğal ifadelerde** bayrak kaç soruyu kurtarıyor.

    ## ⚠️ KORPUS BİR KEZ YANLIŞ SEÇİLDİ — ve ölçüm bunu gösterdi

    İlk sürüm korpusu **katalog sinonimlerinden** üretiyordu (`route()`'un çözemediği
    ölçü sinonimleri). Sonuç: `prompt_enhancer` için **0/12 ↔ 0/12** — sıfır kurtarma.
    Ama bu *"kazanç yok"* demek DEĞİLDİ; **yanlış nüfusu** ölçmüştüm:

    * Katalog sinonimleri `route()`'ta çoğunlukla **BELİRSİZLİK** (R1) yüzünden düşer
      (`bakiye` iki cube'da) — ve **yeniden yazmak belirsizliği çözmez**.
    * Enhancer'ın hedefi ise **katalog DIŞI** ifadelerdir: *"hasılatımız"* → `ciro`.
      Canlı turda tam bu şekilde çalıştığı görülmüştü.

    Doğru korpus `lab/nl_corpus.py::REAL_PHRASINGS` — **doğal iş dili → ölçü** eşlemesi.
    Yeniden yazılmadı, **çağrıldı** (ayrı liste iki tarafı ayrıştırırdı).

    Bunun bir yan kazancı var: beklenen ölçü **bilindiği** için kurtarmanın yalnız
    *oluştuğu* değil **DOĞRU** olduğu da ölçülür — *"cevap geldi"* ile *"doğru cevap
    geldi"* bu depoda ayrı şeylerdir (§4.7-6).
    """
    import time

    from app import cube_router as cr
    from lab.nl_corpus import REAL_PHRASINGS

    # ⚠️ **FAIL-CLOSED: BU MOD GERÇEK SAĞLAYICI OLMADAN ANLAMSIZDIR.**
    #
    # Ölçüldü ve tam bu tuzağa düştüm: `--ab-kurtarma`'yı `--live` OLMADAN koştum,
    # `tests.conftest` sağlayıcıyı `rule`'a sabitledi, enhancer'ın LLM'i olmadığı için
    # **0/14 kurtarma** çıktı — ve bu *"kazanç yok"* gibi okunuyordu. Oysa ölçüm
    # *"ölçmedim"* diyordu.
    #
    # Kendi kurduğum kapıyı kullanmayı unutmak yeterli bir uyarı DEĞİLDİR; mod artık
    # kendi ön koşulunu **zorunlu kılar**. Bu, `konusma_senaryolari.py --live`'da verilen
    # kararın aynısı: sessizce `rule` ile koşan bir "kazanç ölçümü", hiç koşmamaktan
    # kötüdür çünkü bayrak kararı ona dayanır.
    _canli_ortami_geri_yukle()

    login, pw, slug = ACCOUNTS["boyahane"]
    c = _client(login, pw, slug)
    sch = c.get("/schema").json()

    # Katalogdaki ölçüler → hangi cube'a ait (kurtarmanın DOĞRULUĞU için)
    olcu_cube = {}
    for cube in sch.get("cubes") or []:
        for m in cube.get("measures") or []:
            ad = m if isinstance(m, str) else m.get("name")
            olcu_cube.setdefault(ad, cube["name"])

    adaylar = []
    for olcu, ifadeler in REAL_PHRASINGS.items():
        if olcu not in olcu_cube:
            continue                      # bu katalogda yok (şirkete özel ölçü)
        for ifade in ifadeler:
            q = f"bu yıl {ifade}"
            cr.reddi_sifirla()
            if cr.route(cr._norm(q), sch) is None:
                adaylar.append((q, olcu))
    secilen = adaylar[:n]
    print(f"A/B KURTARMA — bayrak: {bayrak!r} · korpus: DOĞAL İFADELER "
          f"({len(adaylar)} çözülemeyen) → örneklem {len(secilen)}", flush=True)

    def _kos(acik: bool) -> dict[str, str | None]:
        """soru → cevaplandıysa seçilen ölçü, yoksa None."""
        out: dict[str, str | None] = {}
        with _BayrakZorla(bayrak, acik=acik):
            for q, _ in secilen:
                d = c.post("/ask", json={"question": q, "execute": False}).json()
                cq = d.get("cube_query") or {}
                ms = cq.get("measures") or []
                out[q] = ms[0] if ms else (cq.get("cube") if cq else None)
                time.sleep(5.0)
        return out

    kapali = _kos(False)
    acik = _kos(True)
    c.__exit__(None, None, None)

    kurtarilan = [(q, o) for q, o in secilen if not kapali[q] and acik[q]]
    dogru = [(q, o) for q, o in kurtarilan if acik[q] == o]
    kaybedilen = [(q, o) for q, o in secilen if kapali[q] and not acik[q]]
    degisen = [(q, kapali[q], acik[q]) for q, _ in secilen
               if kapali[q] and acik[q] and kapali[q] != acik[q]]

    print(f"\n  bayrak KAPALI cevaplanan : {sum(1 for v in kapali.values() if v)}/{len(secilen)}")
    print(f"  bayrak AÇIK   cevaplanan : {sum(1 for v in acik.values() if v)}/{len(secilen)}")
    print(f"  KURTARILAN: {len(kurtarilan)}  (bunun DOĞRU ölçüyle: {len(dogru)})")
    print(f"  kaybedilen: {len(kaybedilen)}  ·  ölçü DEĞİŞEN: {len(degisen)}")
    for q, o in kurtarilan[:8]:
        isaret = "✓" if acik[q] == o else "⚠ YANLIŞ ÖLÇÜ"
        print(f"      {isaret} {q!r} → {acik[q]} (beklenen {o})")
    for q, o in kaybedilen[:5]:
        print(f"      ✗ KAYBEDİLDİ: {q!r}")
    print("\nKABUL ÖLÇÜTÜ (B2): DOĞRU kurtarma > 0 VE etiketli sette bozulan = 0.")
    return 0


def main() -> int:
    if "--live" in sys.argv:
        _sag = _canli_ortami_geri_yukle()
        print(f"CANLI MOD — sağlayıcı: {_sag} · embedder: "
              f"{os.environ.get('DIMA_VQR_EMBEDDER') or 'AÇIK (varsayılan)'}", flush=True)
    if "--ab" in sys.argv:
        return ab_kos(sys.argv[sys.argv.index("--ab") + 1])
    if "--ab-kurtarma" in sys.argv:
        # Örneklem CLI'dan verilebilir: kota bilinmiyor, ölçüm küçükten başlar.
        _n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 20
        return ab_kurtarma_kos(sys.argv[sys.argv.index("--ab-kurtarma") + 1], _n)
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
