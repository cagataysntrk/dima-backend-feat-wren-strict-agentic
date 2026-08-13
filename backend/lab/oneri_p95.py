r"""🔴 `FAZ 5` kapı `②` — **ÖNERİ MOTORUNUN GECİKMESİ** (`p95 < 300 ms`).

Planın kapı listesi bir hız eşiği koyuyor ve kendi uyarısını da yazıyor: *«kapının
kendi maliyeti de ölçülür»*. Bu araç o ölçümü yapar.

## Neyi ölçüyor — ve neyi ÖLÇMÜYOR

Ölçülen: `oneri.ara(kismi, schema, izinliler)` — **motorun kendisi**. HTTP çerçevesi,
ağ ve tarayıcı **dışarıda**: onlar başka bileşenlerin borcudur ve bu sayıya karışırsa
motorun kendi gecikmesi **görünmez** olur 🅫.

⚠ **SOĞUK ile ILIK ayrı raporlanır** 🅖. İlk çağrı katalogdaki tüm etiketleri gömer
(sürüm anahtarlı indeksi kurar); sonrakiler yalnız **sorguyu** gömer. Bu ikisini tek
sayıda toplamak, kullanıcının hiç yaşamadığı bir ortalama üretirdi:

* **soğuk** — süreçte o şema sürümü için **ilk** istek (kullanıcı başına en fazla bir kez)
* **ılık** — sonraki tüm istekler (typeahead'in gerçek hâli)

⚠ 🅕 **Gömücüsüz koşum bir p95 değildir.** `DIMA_VQR_EMBEDDER=off` altında vektör ayağı
hiç çalışmaz; çıkan sayı **leksik yolun** sayısıdır ve vektörlü yola **taşınmaz**. Araç
bunu ölçer ve raporun `kip` alanına **yazar**.

⚠ ㉗🅜 Sonuç **ms** cinsindendir ve **payda** (koşum sayısı) raporda durur; paydasız
bir yüzdelik bir gözlemdir, bir ölçüm değil.

## Koşum

    docker run --rm --network none -v "$PWD/backend:/app" -w /app \
      -v dima-backend-feat-wren-strict-agentic_dima_hf_cache:/tmp/fastembed_cache \
      -e HF_HUB_OFFLINE=1 dima-test python lab/oneri_p95.py

⚠ `DIMA_VQR_EMBEDDER` **koyulmaz** — koyulursa leksik yol ölçülür.
"""

from __future__ import annotations

import json
import pathlib
import statistics
import sys
import time

_KOK = pathlib.Path(__file__).resolve().parents[1]
if str(_KOK) not in sys.path:                                  # pragma: no cover
    sys.path.insert(0, str(_KOK))

#: Plan `§42 · FAZ 5` kapı `②`.
ESIK_MS = 300.0

#: Gerçek typeahead girdileri: kullanıcı **harf harf** yazar, yani sorguların çoğu
#: **kısa öneklerdir**. Uzun ve tam terimlerle ölçmek, en sık hâli atlamak olurdu ㊳.
SORGULAR: tuple[str, ...] = (
    "fi", "fir", "fire", "fire o", "ci", "cir", "ciro", "oe", "oee", "ma",
    "mak", "maki", "makine", "du", "dur", "duru", "duruş", "ka", "kar", "kâr",
    "te", "tes", "tesl", "teslim", "or", "ort", "orta", "ortalama", "sip", "sipar",
)


def _sema() -> dict:
    """Gerçek katalog — uydurma bir fikstürle ölçmek, ölçülen şeyi değiştirir ㊱.

    ⚠ Kurulum `lab/oneri_olcum.py:211`'den **ödünç alındı**, yeniden yazılmadı: ilk
    denemem `WrenService()` diye çağırdı ve `TypeError` aldı — imza **üç** zorunlu
    argüman ister. *Bir kurucunun şeklini hatırlamak değil, okumak gerekir* ㊱.
    """
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    w = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                    connection_info=s.connection_dict())
    return w.schema()


def kos(tekrar: int = 3) -> dict:
    from app import oneri, vqr

    sema = _sema()
    kip = "vektor" if vqr._embedder() is not None else "leksik"
    n_terim = len(oneri.terimler(sema, None))

    # SOĞUK — indeksi kuran ilk çağrı.
    t0 = time.perf_counter()
    oneri.ara(SORGULAR[0], sema, izinliler=None)
    soguk_ms = (time.perf_counter() - t0) * 1000.0

    # ILIK — indeks kurulu; typeahead'in gerçek hâli.
    olcumler: list[float] = []
    for _ in range(tekrar):
        for q in SORGULAR:
            t = time.perf_counter()
            oneri.ara(q, sema, izinliler=None)
            olcumler.append((time.perf_counter() - t) * 1000.0)

    olcumler.sort()
    p = lambda k: olcumler[min(len(olcumler) - 1, int(len(olcumler) * k))]  # noqa: E731
    return {
        "kip": kip,
        "esik_ms": ESIK_MS,
        "terim_sayisi": n_terim,
        "payda": len(olcumler),
        "soguk_ms": round(soguk_ms, 1),
        "ilik_p50_ms": round(statistics.median(olcumler), 2),
        "ilik_p95_ms": round(p(0.95), 2),
        "ilik_azami_ms": round(olcumler[-1], 2),
        "gecti": p(0.95) < ESIK_MS,
    }


if __name__ == "__main__":                                     # pragma: no cover
    d = kos()
    hedef = _KOK / "lab" / "reports" / "oneri_p95.json"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    isaret = "✅" if d["gecti"] else "🔴"
    print(f"{isaret} kip={d['kip']} · terim={d['terim_sayisi']} · payda={d['payda']}")
    print(f"   soğuk {d['soguk_ms']} ms  ·  ılık p50 {d['ilik_p50_ms']} ms  ·  "
          f"p95 {d['ilik_p95_ms']} ms  (eşik {ESIK_MS} ms)")
    if d["kip"] == "leksik":
        print("   ⚠ 🅕 GÖMÜCÜ KAPALI — bu sayı LEKSİK yolun sayısıdır, vektörlü yola "
              "TAŞINMAZ.")
    sys.exit(0 if d["gecti"] else 1)
