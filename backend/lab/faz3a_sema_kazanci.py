"""FAZ 3a — ŞEMA-KISITLI ÇIKTININ KAZANCI: A/B ölçümü (GERÇEK sağlayıcı gerekir).

    python lab/faz3a_sema_kazanci.py            # 16 soru, 5 sn aralık
    python lab/faz3a_sema_kazanci.py 24 5       # örneklem, bekleme

## Neden bu araç var

Faz 3a'nın kabul kapısı planda şöyleydi: *"whitelist reddi oranı ölçülüp **düşüşü**
doğrulanır."* Faz 3a landing ettiğinde bu **karşılanamadı** — o ortamda gerçek bir LLM
sağlayıcı yoktu ve ölçüm `--live` turuna devredildi. Bu dosya o borcu kapatır.

## ⚠️ KABUL ÖLÇÜTÜ YANLIŞ TANIMLANMIŞTI (ölçümle bulundu, 3 Ağustos 2026)

*"Red oranı düşmeli"* iki **farklı** olayı tek kefeye koyuyor:

* **dürüst red** (`cube:null`) — model *"bunların hiçbiri"* diyor. Bu **DOĞRU
  davranıştır** ve Faz 3a'nın kendi tasarım kararıdır (*"'hiçbiri' seçeneği olmayan bir
  kısıt modeli GEÇERLİ AMA YANLIŞ seçime zorlar"*). Bunu düşürmek **zarardır**.
* **geçersiz alan** — cube geçerli ama ölçü/boyut katalogda yok; `parse_cube_query` tüm
  sorguyu düşürür. Mekanizmanın hedefi **budur**.

ÖLÇÜLDÜ (gerçek Gemini, `gemini-flash-lite-latest`, iki bağımsız koşum):

    koşum        yapılandırma      toplam red   dürüst red   GEÇERSİZ ALAN   doğru cube
    8 soru       şemasız               3            3              0            5/8
    8 soru       şema-kısıtlı          2            2              0            4/8
    16 soru      şemasız               6            6              0            6/16
    16 soru      şema-kısıtlı          6            6              0            6/16

**SONUÇ: bu katalogda ÖLÇÜLEBİLİR KAZANÇ YOK.** Şemasız yol, bugünkü prompt'uyla, 24
ölçülen soruda **hiç geçersiz alan üretmedi** — yani kısıtın kaldıracağı bir şey yoktu.
Reddin tamamı **dürüst red**tir ve o zaten korunması gereken davranıştır.

Bu, Faz 7'nin (üç sıçrama, üçü de benimsenmedi) ve 2a-1'in (`elektrik`, ölçülüp
reddedildi) aynı disiplinidir: **kazanç yoksa yazılır.**

**Mekanizma yine de KALIYOR** ve gerekçesi ölçüm değil **yapıdır**: kısıtlı yolda geçersiz
ad üretmek *"ölçülen 24 soruda görülmedi"* değil, **imkânsızdır**. Bu, bu deponun 9.3'te
verdiği kararla aynı: *"bir ÖLÇÜM, yapısal garanti değildir."* Maliyeti ölçüldü ve **sıfır**
(red bileşimi ve doğru-cube iki koşumda da eşit).

⚠️ **İLK ÖLÇÜMÜM YANLIŞTI ve inandırıcıydı** (bu oturumda dokuzuncu kez ölçüm aracı
yanıldı; MIMARI §6.4). Reddedilen çıktıyı sınıflandırmak yerine **LLM'i YENİDEN
ÇAĞIRIYORDUM** — yani teşhis, reddedilen üretimin değil **başka bir üretimin** üzerinde
yapılıyordu. *"3 geçersiz alan → 0"* diye bir kazanç raporlayacaktım. Bu dosya sınıflamayı
**aynı ham çıktı üzerinde, aynı döngüde** yapar; tekrar koşumu farkı ortaya çıkardı.

## Tasarım kararları

* Korpus **katalogdan** üretilir: `route()`'un çözemediği ölçü sinonimleri — Intent
  yolunun GERÇEK tüketicisi orasıdır. Elle soru yazmak ölçümü kurgulardı.
* `select_cube` **doğrudan** çağrılır (k=1). `/ask` üzerinden ölçmek `consistency_k=3`
  yüzünden **üç kat** LLM maliyeti demekti; ölçülen şey aynı.
* **Katmanlı örneklem**: her cube'dan sırayla — tek bir cube'un sinonimleri sonucu ele
  geçirmesin. (Bu oturumda ölçüm aracı kendi örneklemiyle beş kez yanıldı; MIMARI §6.4.)
* **HIZ SINIRI**: ölçülen gerçek sınır **10 saniyede 10 istek**. Varsayılan 5 sn bekleme
  → 10 sn'de 4 çağrı, tavanın açık ara altında.

⚠️ **Örneklem küçüktür (2 koşum · 24 soru · 48 çağrı) ve LLM deterministik değildir.**
İki koşum aynı sonucu verdi (geçersiz alan 0/0), ama bu *"asla üretmez"* demek değildir —
*"bu katalogda, bu prompt'la, ölçülen 24 soruda üretmedi"* demektir. Daha büyük bir koşum
gerekirse `N` artırılır; kararı değiştirecek bulgu **geçersiz alanın şemasız yolda
görülmesi** olurdu.
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

CIKTI = Path("/tmp/faz3a_sema_kazanci.json")


def _tani(ham: str, index: dict) -> str:
    """Reddin SEBEBİ — bu ayrım olmadan ölçüm yanlış şeyi sayar."""
    try:
        s = (ham or "").strip().removeprefix("```json").removeprefix("```").removesuffix("```")
        j = json.loads(s)
    except Exception:
        return "BOZUK JSON"
    if j.get("cube") is None:
        return "DÜRÜST RED"
    if j.get("cube") not in index:
        return "GEÇERSİZ CUBE"
    return "GEÇERSİZ ÖLÇÜ/BOYUT"


def main() -> None:
    n_hedef = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    bekle = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0

    from app import cube_router as cr
    from app.config import get_settings
    from app.llm import build_generator
    from app.wren_service import WrenService

    s = get_settings()
    sch = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict()).schema()
    katalog, index = cr.build_catalog(sch)
    sema = cr.cube_query_json_schema(index)
    llm = build_generator(s)
    if not hasattr(llm, "select_cube"):
        print("sağlayıcıda select_cube YOK — bu ölçüm gerçek bir sağlayıcı gerektirir")
        raise SystemExit(2)

    adaylar, gorulen = [], set()
    for c in sch["cubes"]:
        for syns in (c.get("measure_synonyms") or {}).values():
            for sy in syns:
                nrm = cr._norm(str(sy))
                if nrm in gorulen or len(nrm) < 4:
                    continue
                gorulen.add(nrm)
                cr.reddi_sifirla()
                if cr.route(f"bu yil {sy}", sch) is None:
                    adaylar.append((f"bu yil {sy}", c["name"]))

    kova: dict[str, list] = defaultdict(list)
    for q, cube in adaylar:
        kova[cube].append((q, cube))
    secilen: list = []
    while len(secilen) < n_hedef and any(kova.values()):
        for cube in list(kova):
            if kova[cube] and len(secilen) < n_hedef:
                secilen.append(kova[cube].pop(0))

    print(f"korpus: {len(adaylar)} çözülemeyen soru → katmanlı örneklem {len(secilen)}",
          flush=True)
    sonuc = []
    for k, (q, beklenen) in enumerate(secilen, 1):
        satir = {"soru": q, "beklenen_cube": beklenen}
        for etiket, sm in (("semasiz", None), ("sema_kisitli", sema)):
            try:
                ham = llm.select_cube(q, katalog, sm)
                cq = cr.parse_cube_query(ham, index)
                satir[etiket] = {
                    "reddedildi": cq is None,
                    "tani": _tani(ham, index) if cq is None else None,
                    "cube": (cq or {}).get("cube"),
                    "dogru_cube": bool(cq) and cq.get("cube") == beklenen,
                }
            except Exception as exc:  # noqa: BLE001 — bir soru koşumu düşürmez
                satir[etiket] = {"hata": f"{type(exc).__name__}: {exc}"[:120]}
            time.sleep(bekle)
        sonuc.append(satir)
        print(f"  {k}/{len(secilen)} {q[:32]:<34} "
              f"şemasız={satir['semasiz'].get('tani') or satir['semasiz'].get('cube')}"
              f"  kısıtlı={satir['sema_kisitli'].get('tani') or satir['sema_kisitli'].get('cube')}",
              flush=True)

    CIKTI.write_text(json.dumps(sonuc, ensure_ascii=False, indent=1), encoding="utf-8")
    n = len(sonuc)
    print(f"\n{'yapılandırma':<20}{'red':>6}{'dürüst':>9}{'GEÇERSİZ':>11}{'doğru cube':>13}")
    for et, ad in (("semasiz", "şemasız (bugün)"), ("sema_kisitli", "şema-kısıtlı")):
        red = [x[et] for x in sonuc if x[et].get("reddedildi")]
        durust = sum(1 for r in red if r.get("tani") == "DÜRÜST RED")
        print(f"{ad:<20}{len(red):>6}{durust:>9}{len(red) - durust:>11}"
              f"{sum(1 for x in sonuc if x[et].get('dogru_cube')):>10}/{n}")
    print("\nKABUL ÖLÇÜTÜ: geçersiz alan üretimi DÜŞMELİ, dürüst red DÜŞMEMELİ.")
    print(f"JSON: {CIKTI}")


if __name__ == "__main__":
    main()
