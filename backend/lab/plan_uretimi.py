"""PLAN ÜRETİM ÖLÇÜMÜ — *model sözleşmeye uyabiliyor mu?* **Motorsuz.**

## Neden bu alet

`lab/discovery_orani.py` curl çıktısı okur: motor, docker, seed, kota ister. Ama plan
katmanının asıl sorusu çok daha dar ve **çok daha ucuz** ölçülür:

> 20 soru ver — kaçı **şema-geçerli** bir plan üretiyor, üretemeyenler **neden**
> üretemiyor, ve kaç adımlık planlar çıkıyor?

⊙ Hiçbir sorgu koşulmaz, hiçbir cube derlenmez, hiçbir HTTP ucu ayakta olmaz. Yalnız
katalog + `plan_uret` + `_plani_oku`. *Bir katmanı ölçmenin maliyeti, o katmanı
geliştirmenin maliyetinden büyükse, o katman ölçülmez.*

## Ne ölçüyor

| sayı | anlamı |
|---|---|
| `gecerli` | ilk denemede şema-geçerli plan |
| `onarildi` | ilk deneme reddedildi, **tek** düzeltme turu kurtardı |
| `dustu` | ikisinde de olmadı — **sebepleriyle** |
| `adim_dagilimi` | `E9`'un ölçüsü: plan uzunluğu bir maliyettir |
| `fiil_kullanimi` | hangi fiiller **hiç** kullanılmıyor (tarifi eksik olabilir) |

🔴 `fiil_kullanimi` bu aletin en değerli sütunu: hiç kullanılmayan bir fiil ya
gereksizdir ya **anlatılmamıştır**, ve ikisi çok farklı işlerdir.

## Kullanım

    python lab/plan_uretimi.py --sorular ff.txt
    python lab/plan_uretimi.py            # yerleşik kök-neden sondaları
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

#: 🔴 Sondalar **kök-neden inişi** sınıfından — ve bu bilinçli. `§AA1` *«X neden
#: düşük»* sınıfını zaten kapattı (akran kıyası); orkestratörün boşluğu o değil,
#: *«o değerin hangi KIRILIMLARINDA ortaya çıktığı»*. Yanlış soru sınıfıyla kurulan
#: bir ölçüm, payda dolu olsa bile `+0,0` verir.
SONDALAR: tuple[str, ...] = (
    "en kötü makineyi bul ve o makinede hangi vardiyada kötüleştiğini göster",
    "fire oranı en yüksek hattı bul sonra o hatta hangi ürün grubu baskın",
    "en çok geciken bölgeyi bul ve o bölgede gecikmeyi hangi müşteri açıklıyor",
    "duruş süresi en uzun makinede duruş nedenlerini kır",
    "en düşük oee'li vardiyayı bul ortalamadan ne kadar kötü söyle",
    "ciro ve fire ve oee ile bu yılın özet raporunu hazırla",
    "makineleri oee ve duruş süresine göre sırala",
    "enerji ve su tüketimi için bir pano taslağı kur",
)


def _katalog():
    from app.config import get_settings
    from app.katalog_metni import metin_ve_indeks
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    return metin_ve_indeks(svc.schema(), None)


def main() -> int:
    ap = argparse.ArgumentParser(description="Plan üretim ölçümü (motorsuz)")
    ap.add_argument("--sorular")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    from app import plan_garson
    from app.config import get_settings
    from app.llm import build_generator

    sorular = ([s.strip() for s in Path(a.sorular).read_text(encoding="utf-8").splitlines()
                if s.strip()] if a.sorular else list(SONDALAR))
    catalog, index = _katalog()
    llm = build_generator(get_settings())
    if not getattr(llm, "plan_kurabilir", False):
        print("⊘ ÖLÇÜLEMEDİ: sağlayıcı plan kuramıyor — bir varsayım yazmak yerine "
              "ölçümü reddediyorum.")
        return 2

    gecerli, onarildi, dustu = [], [], []
    adimlar: Counter[int] = Counter()
    fiiller: Counter[str] = Counter()
    for q in sorular:
        _n: list[str] = []
        ham = llm.plan_kur(q, catalog, None)
        plan = plan_garson._plani_oku(ham, neden=_n)
        _onarim = False
        if plan is None and _n:
            _duzelt = (q + "\n\n🔴 ÖNCEKİ DENEMEN REDDEDİLDİ: " + "; ".join(_n)
                       + "\nAynı soruyu, bu kez sözleşmeye UYARAK yeniden planla.")
            plan = plan_garson._plani_oku(llm.plan_kur(_duzelt, catalog, None))
            _onarim = plan is not None
        if plan is None:
            dustu.append((q, "; ".join(_n) or "sebep yok"))
            continue
        (onarildi if _onarim else gecerli).append(q)
        adimlar[len(plan["adimlar"])] += 1
        for adim in plan["adimlar"]:
            fiiller[adim["fiil"]] += 1

    n = len(sorular)
    if a.json:
        print(json.dumps({"gecerli": len(gecerli), "onarildi": len(onarildi),
                          "dustu": [d[0] for d in dustu],
                          "adim_dagilimi": dict(adimlar),
                          "fiil_kullanimi": dict(fiiller)}, ensure_ascii=False, indent=2))
        return 0

    print(f"\npayda {n}")
    print(f"  ✅ ilk denemede geçerli   {len(gecerli):>3}  ({len(gecerli)/n*100:5.1f}%)")
    print(f"  ⟳  onarım turu kurtardı  {len(onarildi):>3}  ({len(onarildi)/n*100:5.1f}%)")
    print(f"  🔴 düştü                  {len(dustu):>3}  ({len(dustu)/n*100:5.1f}%)")
    for q, neden in dustu:
        print(f"      • «{q[:60]}» → {neden[:110]}")
    print(f"\nadım dağılımı: {dict(sorted(adimlar.items()))}")
    from app.plan_semasi import FIILLER
    hic = [f for f in FIILLER if not fiiller.get(f)]
    print(f"fiil kullanımı: {dict(fiiller.most_common())}")
    print(f"🔴 HİÇ kullanılmayan fiil: {hic}")
    print("⊙ Hiç kullanılmayan bir fiil ya GEREKSİZDİR ya ANLATILMAMIŞTIR — "
          "ve ikisi çok farklı işlerdir.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
