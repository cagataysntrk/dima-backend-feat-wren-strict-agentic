"""FAZ 4 ÖN KOŞULU — **motor yeniden-girilebilir mi?** *(ölçüm, karar değil)*

## Neden bu ölçüm, paralellikten ÖNCE

`plan_kosucu.dogrula()` artık bağımsız `SORGU` adımlarını topolojik katmanlara ayırıyor.
Aynı katmanı paralel koşmak **gecikme** kazandırır. Ama bedeli gecikmede değil, **sessiz
veri bozulmasında** olabilir: `WrenEngine` süreç-içidir ve `plan_tuketici` aynı servis
örneği üzerinde `cube_sql` → `dry_plan` → `query` üçlüsünü çağırır.

🔴 Bu depo aynı dersi bir kez **ödedi**: iki test konteyneri paralel koşunca paylaşılan
derleme dizininde yarış çıktı ve süit **934 hata** verdi. O yasak sonradan **izolasyonla**
kalktı — yani çözüm "paralel koşma" değil, **yarışın olmadığını göstermek**ti.

⚠ Bu araç bir **karar vermez**. Üç sayı üretir; kararı insan verir:
  1. paralel koşumda **hata** var mı
  2. paralel sonuçlar seri sonuçlarla **birebir aynı** mı  *(asıl soru bu)*
  3. gerçekten **hızlanıyor** mu

*Bir hızlanmayı, doğruluğunu ölçmeden satın almak, ölçmediğin bir borcu üstlenmektir.*

## Kullanım

    python lab/motor_eszamanlilik.py                 # 4 eş zamanlı, 3 tur
    python lab/motor_eszamanlilik.py --isci 8 --tur 5
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _servis(sirket: str):
    """⚠ `connection_info` **ayarlardan** alınır, `{}` değil: boş sözlükle şema okunur ama
    sorgu koşulmaz (`Catalog does not exist`). Ölçüm aracının bunu bilmemesi, ölçtüğü şeyi
    ölçmediğini fark etmemesi demekti."""
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    return WrenService(project_dir=s.resolved_project_dir(),
                       datasource=s.datasource,
                       connection_info=s.connection_dict())


def _sorgular(schema: dict, n: int) -> list[dict]:
    """Farklı cube'lardan `n` bağımsız sorgu — aynı sorguyu tekrarlamak önbelleği ölçerdi."""
    out: list[dict] = []
    for c in (schema.get("cubes") or []):
        olculer = [m for m in (c.get("measures") or [])]
        if not olculer:
            continue
        out.append({"cube": c["name"], "measures": [olculer[0]]})
        if len(out) >= n:
            break
    return out


def _kos(svc, cq: dict):
    sql = svc.cube_sql(cq)
    svc.dry_plan(sql)
    return svc.query(sql, limit=50)


def main() -> int:
    ap = argparse.ArgumentParser(description="Motor eş zamanlılık ölçümü (FAZ 4 ön koşulu)")
    ap.add_argument("--isci", type=int, default=4)
    ap.add_argument("--tur", type=int, default=3)
    a = ap.parse_args()

    svc = _servis('')
    cqs = _sorgular(svc.schema(), a.isci)
    print(f"sorgular: {[c['cube'] for c in cqs]}")

    # 1) SERİ — hakikat kaynağı
    t0 = time.monotonic()
    seri = [_kos(svc, c) for c in cqs]
    seri_ms = int((time.monotonic() - t0) * 1000)

    hatalar: list[str] = []
    sapma: list[str] = []
    paralel_ms: list[int] = []
    for tur in range(a.tur):
        t0 = time.monotonic()
        with ThreadPoolExecutor(max_workers=a.isci) as ex:
            try:
                par = list(ex.map(lambda c: _kos(svc, c), cqs))
            except Exception as e:                       # noqa: BLE001
                hatalar.append(f"tur {tur}: {type(e).__name__}: {e}")
                continue
        paralel_ms.append(int((time.monotonic() - t0) * 1000))
        for i, (s, p) in enumerate(zip(seri, par)):
            if json.dumps(s.get("rows"), sort_keys=True, default=str) != \
               json.dumps(p.get("rows"), sort_keys=True, default=str):
                sapma.append(f"tur {tur} · sorgu {i} ({cqs[i]['cube']})")

    print(f"\nseri     : {seri_ms} ms")
    print(f"paralel  : {paralel_ms} ms  (işçi={a.isci}, tur={a.tur})")
    print(f"🔴 hata   : {len(hatalar)}  {hatalar[:3]}")
    print(f"🔴 sapma  : {len(sapma)}  {sapma[:3]}")
    if paralel_ms and not hatalar and not sapma:
        _ort = sum(paralel_ms) / len(paralel_ms)
        print(f"\n✅ YARIŞ GÖRÜLMEDİ · hızlanma {seri_ms / _ort:.2f}×")
        print("⚠ «görülmedi» ≠ «yok»: bu bir ÖRNEKLEM. Kararı insan verir.")
    else:
        print("\n🔴 PARALELLİK AÇILMAZ — yukarıdaki sayı bir karar değil, bir DELİLDİR.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
