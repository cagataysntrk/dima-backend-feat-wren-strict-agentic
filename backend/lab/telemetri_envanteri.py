"""FAZ 0 — ÖLÇÜM ENVANTERİ. Planın üç çıktısını tek komutla üretir.

    python lab/telemetri_envanteri.py            # özet
    python lab/telemetri_envanteri.py --json      # makine-okur

## Neden ayrı bir araç, neden bir uç noktası değil

Planın Faz 0 çıktısı üç **sayı**: (1) 2 haftalık kaynak dağılımı, (2) **en sık 20 red
gerekçesi**, (3) `auto_cube`'un **ölçülen yanlış-oranı**. Bunlar bir ürün yüzeyi değil, bir
**karar girdisi** — Faz 2b'nin (`auto_cube` kararı) ve terfi kuyruğu önceliğinin dayanağı.

`route-distribution` uç noktası zaten var ama **admin plane'de** (`/sadmin/*`, ayrı ASGI +
ayrı JWT — ADR-0015) ve **admin frontend yok** (ölçüldü: `admin-dev/` yalnız bir başlatıcı
`package.json`). Yani o uca bakabilmek için ya admin arayüzü inşa edilmeli (UI/UX planının
işi, ayrı dosyaya taşındı) ya da veriye doğrudan bakılmalı. Bu araç ikincisini yapar —
**Faz 0'ın çıktısı bir panele bağımlı değildir**.

## Dürüstlük kuralı

Bu araç **hiçbir rakamı devralmaz**. Raporun *"interaction_log'da 7 satır var"* iddiası bu
checkout'ta doğrulanamadı (yerel DB 0 bayt, tablosuz) ve planda öyle kaydedildi. Burada
ölçülen ne çıkarsa o yazılır; veri yoksa **"veri yok" denir**, tahmin edilmez.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

VARSAYILAN_GUN = 14


def _oturum():
    from sqlmodel import Session

    from control_plane.db import engine

    return Session(engine)


def kaynak_dagilimi(gun: int = VARSAYILAN_GUN) -> dict:
    """(1) `kind` × `source` dağılımı. `by_source` AYRI tutulur çünkü `_source_kind()`
    `cube` ile `cube+llm`'i birleştiriyor — ikisinin güveni farklı (1.0 vs 0.85) ve
    "Intent-JSON ne kadar işe yarıyor" sorusu ancak ham `source`'tan cevaplanır."""
    from sqlmodel import func, select

    from control_plane.models import InteractionLog

    esik = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=gun)
    with _oturum() as s:
        toplam = s.exec(select(func.count()).select_from(InteractionLog)).one()
        pencere = s.exec(select(func.count()).select_from(InteractionLog)
                         .where(InteractionLog.ts >= esik)).one()
        by_kind = dict(s.exec(select(InteractionLog.kind, func.count())
                              .where(InteractionLog.ts >= esik)
                              .group_by(InteractionLog.kind)).all())
        by_source = dict(s.exec(select(InteractionLog.source, func.count())
                                .where(InteractionLog.ts >= esik)
                                .group_by(InteractionLog.source)).all())
    return {"toplam_satir": toplam, "pencere_gun": gun, "pencere_satir": pencere,
            "by_kind": by_kind, "by_source": by_source}


def red_gerekceleri(gun: int = VARSAYILAN_GUN, ilk: int = 20) -> dict:
    """(2) En sık red gerekçeleri — `route()` HANGİ dalda pes etti (R1…R10).

    Bu, Faz 0'ın **asıl** çıktısıdır: kalan %36'nın nasıl dağıldığını gösterir ve
    "hangi kaldıraca yatırım yapılmalı" sorusunu ölçüme bağlar. `reject_reason` NULL olan
    satırlar `route()`'un pes ETMEDİĞİ (cevap ürettiği) sorulardır."""
    from sqlmodel import func, select

    from app.cube_router import RED_KODLARI
    from control_plane.models import InteractionLog

    esik = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=gun)
    with _oturum() as s:
        satirlar = s.exec(select(InteractionLog.reject_reason, func.count())
                          .where(InteractionLog.ts >= esik)
                          .group_by(InteractionLog.reject_reason)).all()
    sayac = Counter({(k or "—cevap üretildi—"): v for k, v in satirlar})
    reddedilen = sum(v for k, v in sayac.items() if k in RED_KODLARI)
    return {
        "reddedilen_toplam": reddedilen,
        "en_sik": [{"kod": k, "adet": v, "gerekce": RED_KODLARI.get(k, "—")}
                   for k, v in sayac.most_common(ilk)],
        "kapsanmayan_kod": sorted(k for k in sayac if k not in RED_KODLARI
                                  and k != "—cevap üretildi—"),
    }


def auto_cube_envanteri(ornek: int = 50) -> dict:
    """(3) §1.7 — `auto_cube` VQR envanteri.

    `vqr.py:153-158` `auto_cube`'u GÜVENİLİR kaynaklar listesine koyuyor: `cube` ve
    `cube+llm` cevapları **insan onayı olmadan** doğrudan tekrar-oynatılabilir havuza
    yazılıyor. Kodun gerekçesi *"katalogla doğrulanmış CubeQuery'den derlenmiş SQL"* —
    ama bu **yapısal** geçerliliği **semantik** doğrulukla karıştırıyor. §2.1'in ölçtüğü
    **%86,3 doğru-cube** ikisinin aynı şey olmadığının kanıtı: yapısal olarak geçerli,
    `parse_cube_query`'den geçmiş cevapların **~%14'ü** yine de yanlış cube seçiyor.

    Bu fonksiyon **oranı hesaplamaz** — denetlenecek örneklemi ÇIKARIR. Doğru/yanlış kararı
    insan işidir; plan da öyle diyor (*"rastgele 50'lik bir örneklem doğru/yanlış diye
    DENETLENİR"*). Otomatik bir "doğruluk" üretmek, tam olarak eleştirilen hatanın
    (yapısal ≠ semantik) tekrarı olurdu.
    """
    import random

    from sqlmodel import col, func, select

    from control_plane.models import VerifiedQuery

    with _oturum() as s:
        by_source = dict(s.exec(
            select(VerifiedQuery.source, func.count())
            .where(col(VerifiedQuery.deleted_at).is_(None))
            .group_by(VerifiedQuery.source)).all())
        auto = s.exec(select(VerifiedQuery)
                      .where(VerifiedQuery.source == "auto_cube",
                             col(VerifiedQuery.deleted_at).is_(None))).all()
    rnd = random.Random(20260802)   # sabit tohum: örneklem TEKRARLANABİLİR olmalı
    sec = rnd.sample(list(auto), min(ornek, len(auto)))
    insan_onayli = sum(v for k, v in by_source.items()
                       if k in ("user", "user_verified", "chip_approved"))
    return {
        "by_source": by_source,
        "auto_cube_adet": len(auto),
        "insan_onayli_adet": insan_onayli,
        "denetim_orneklemi": [{"id": str(v.id), "soru": v.question,
                               "cube_query": json.loads(v.cube_query_json or "{}")}
                              for v in sec],
        "_not": "yanlış-oranı BU ARAÇ HESAPLAMAZ — örneklem insan tarafından denetlenir "
                "(yapısal geçerlilik ≠ semantik doğruluk; §1.7'nin tam eleştirisi bu).",
    }


def _teshis(exc: Exception) -> dict:
    """Hatayı bir TEŞHİSE çevirir. *"Tablo yok"* ile *"tablo boş"* **farklı** şeylerdir ve
    farklı eylem gerektirir:
      * tablo YOK   → şema bu ortamda hiç kurulmamış (migration koşmamış) — telemetri
                      hakkında hiçbir şey söylemez
      * tablo BOŞ   → şema var, telemetri AKMIYOR — asıl bulgu budur
    İkisini tek "hata" başlığı altında birleştirmek, ölçümü okunamaz yapardı.
    """
    m = str(exc)
    if "no such table" in m or "does not exist" in m:
        return {"durum": "sema_yok",
                "aciklama": "Bu ortamda tablo YOK — migration koşmamış. Telemetrinin akıp "
                            "akmadığı hakkında bir şey SÖYLEMEZ; önce şema kurulmalı."}
    return {"durum": "hata", "aciklama": f"{type(exc).__name__}: {exc}"}


def topla(gun: int = VARSAYILAN_GUN) -> dict:
    out: dict = {"olculdu": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    for ad, fn in (("kaynak_dagilimi", lambda: kaynak_dagilimi(gun)),
                   ("red_gerekceleri", lambda: red_gerekceleri(gun)),
                   ("auto_cube", auto_cube_envanteri)):
        try:
            out[ad] = fn()
        except Exception as exc:  # noqa: BLE001 — ölçüm aracı, tek bölüm ötekini düşürmesin
            out[ad] = _teshis(exc)
    return out


def _yazdir(d: dict) -> None:
    print("=" * 72)
    print("FAZ 0 — TELEMETRİ ENVANTERİ   ·", d["olculdu"])
    print("=" * 72)

    k = d.get("kaynak_dagilimi") or {}
    if k.get("durum"):
        print(f"\n(1) KAYNAK DAĞILIMI: {k['durum'].upper()}\n    {k['aciklama']}")
    elif not k.get("toplam_satir"):
        print("\n(1) KAYNAK DAĞILIMI: interaction_log BOŞ (0 satır).")
        print("    → Telemetri henüz akmıyor. Bu bir ÖLÇÜMDÜR, bir hata değil:")
        print("      raporun '7 satır' iddiası devralınmadı, yeniden ölçüldü.")
    else:
        print(f"\n(1) KAYNAK DAĞILIMI — son {k['pencere_gun']} gün: "
              f"{k['pencere_satir']}/{k['toplam_satir']} satır")
        for ad, m in (("kind", k["by_kind"]), ("source (ham — cube/cube+llm AYRI)",
                                               k["by_source"])):
            print(f"    {ad}:")
            for key, v in sorted(m.items(), key=lambda x: -x[1]):
                print(f"      {str(key or '—'):<24} {v}")

    r = d.get("red_gerekceleri") or {}
    if r.get("durum"):
        print(f"\n(2) RED GEREKÇELERİ: {r['durum'].upper()}\n    {r['aciklama']}")
    elif not r.get("en_sik"):
        print("\n(2) RED GEREKÇELERİ: veri yok.")
    else:
        print(f"\n(2) EN SIK RED GEREKÇELERİ (reddedilen toplam: {r['reddedilen_toplam']})")
        for e in r["en_sik"]:
            print(f"      {e['kod']:<22} {e['adet']:>6}  {e['gerekce']}")
        if r["kapsanmayan_kod"]:
            print(f"    ⚠ RED_KODLARI'nda olmayan kod(lar): {r['kapsanmayan_kod']}")

    a = d.get("auto_cube") or {}
    if a.get("durum"):
        print(f"\n(3) auto_cube ENVANTERİ: {a['durum'].upper()}\n    {a['aciklama']}")
    else:
        print(f"\n(3) auto_cube ENVANTERİ (§1.7)")
        print(f"      insan ONAYI OLMADAN replay'e giren : {a['auto_cube_adet']}")
        print(f"      insan onaylı                        : {a['insan_onayli_adet']}")
        for key, v in sorted((a.get("by_source") or {}).items(), key=lambda x: -x[1]):
            print(f"        {str(key):<22} {v}")
        print(f"      denetim örneklemi                   : {len(a['denetim_orneklemi'])} soru")
        print(f"      {a['_not']}")
    print()


def main() -> None:
    ap = argparse.ArgumentParser(description="Faz 0 telemetri envanteri")
    ap.add_argument("--gun", type=int, default=VARSAYILAN_GUN)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    d = topla(args.gun)
    if args.json:
        print(json.dumps(d, ensure_ascii=False, indent=2, default=str))
    else:
        _yazdir(d)


if __name__ == "__main__":
    main()
