"""FAZ O-8 — **MENÜ ÖLÇÜM ALETİ.** *"Menü, yazarın kelimesini taşıyor."* (`G1`)

## Ölçülen kusur

Dört tur dört ayrı kanıt verdi ve hepsi **aynı** sınıftı: mutfakta yemek **var**, menüde
adı **yok**.

| tur | soru | mutfakta var | eksik |
|---|---|---|---|
| `Y6` | *«tamir süresi»* | `bakim.ort_durus_dakika` | *«tamir süresi»* yazılı değil |
| `AA13` | *«üretim miktarı»* | `parti.toplam_agirlik_kg` | *«miktar»* yazılı değildi |
| `X8` | *«mesai ücreti»* | `ik.toplam_mesai_ucreti` | ifade eşleşmedi |
| `Z12` | *«bölgelere göre»* | `sikayet` + `bolge` | çekim eşleşmedi |

## 🔴 KÖK ÇÖZÜM SİNONİM ŞİŞİRMEK DEĞİL (`§99.1`)

Dört terimi elle eklemek dördünü kapatır ve **beşincisini göstermez**. Üstelik geniş
sinonim bir cube'u **açgözlü** yapar: `§99.1`'in ölçtüğü bedel budur. Gereken şey bir
liste değil, listeyi **kendiliğinden üreten** bir alettir.

## 🔴 BU ALET KARAR VERMEZ, İŞ LİSTESİ ÜRETİR

`lab/r1_envanteri.py`'nin dersi aynen geçerli: kararı **araç** verirse bir tenant'ın alan
bilgisi bütün tenant'lara dayatılır (ölçüldü: korpus %93,2 → %92,6). Burada üretilen şey
**kanıtlı bir iş listesidir**; kararı insan verir ve `cube_synonyms.yml`'a **tenant
kapsamlı** girer.

## Neyi ölçüyor — ve neden bu ayrım önemli

Cevapsız her soru aynı sınıf değildir. Alet **üç** kova ayırır:

| kova | anlamı | yapılacak iş |
|---|---|---|
| 🟡 **KONU TUTTU, ÖLÇÜ TUTMADI** | cube biliniyor, hangi ölçü olduğu bilinmiyor | **menüye ad yaz** *(G1'in tam hedefi)* |
| 🟠 **KONU TUTTU, BOYUT TUTMADI** | kırılım adı çekimli/eşanlamlı yazılmış | boyut sinonimi ya da çekim |
| 🔴 **HİÇBİR ŞEY TUTMADI** | konu bile bilinmiyor | **mutfak eksiği** — yeni ölçü/cube |

⊙ Üçünü tek sayıya toplamak, bu aleti *"cevapsız soru sayacı"*na indirgerdi — oysa ilk
iki kova **ucuz** (bir satır beyan), üçüncüsü **pahalı** (yeni bir yemek). *Bir eksikliği
ölçmenin değeri, onu ne kadar ucuza kapatılabileceğini de söylemesindedir.*

## Kullanım

    python lab/menu.py                                # yerleşik kanıt sorularıyla
    python lab/menu.py --sorular dosya.txt            # satır satır soru
    python lab/menu.py --sirket demo-boyahane --json
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

#: 🔴 `G1`'in **dört kanıtı** — ve her birinin **beklenen konusu**.
#:
#: ⚠ Beklenen konu bir süs değil, aletin **körlüğünü kapatan** şey: bir soru
#: cevaplanmışsa alet susardı, oysa *yanlış konudan* cevaplanmış olabilir. Beklenen
#: yazılıysa alet onu da görür. ⊙ Ve bu bir **yüklem değil, etikettir** (`§101.1`):
#: yanlış-pozitif üretemez, çünkü kararı sezgi değil insan vermiştir.
#: ⚠ Değer **birden çok** cube olabilir: bir soruya birden fazla doğru konu varsa, tekini
#: dayatmak aletin kendi yanlış-pozitifini üretirdi.
KANIT_SORULARI: dict[str, tuple[str, ...]] = {
    # `Y6` — 🔴 HÂLÂ AÇIK, ve artık *cevapsız* değil **yanlış**: tamir `bakim`'ın işi.
    "tamir süresi ne kadar": ("bakim",),
    # `AA13` — ⟳ RAPORUN BEKLENTİSİ DÜZELTİLDİ. Rapor `parti.toplam_agirlik_kg` diyordu;
    # o beklenti `miktar` terimi `parti`ye eklenMEDEN önce yazılmıştı. Bugün `oee`'nin
    # `toplam_uretim_kg`'si en az onun kadar doğru bir cevap — ikisini de kabul etmek,
    # aletin **kendi yanlış-pozitifini** üretmesini engeller (`§101.1`).
    "üretim miktarı nedir": ("parti", "oee"),
    # `X8` — ✅ KAPANDI: ölçüldü, `ik.toplam_mesai_ucreti` veriyor.
    "mesai ücreti ne kadar": ("ik",),
    # `Z12` — 🔴 HÂLÂ AÇIK: `sikayet` cube'u VAR ama çekimli yazılışı hiç tutmuyor.
    "şikayetleri bölgelere göre ver": ("sikayet",),
}

OLCU_YOK = "olcu_yok"
BOYUT_YOK = "boyut_yok"
KONU_YOK = "konu_yok"
YANLIS_KONU = "yanlis_konu"

KOVA_ADI = {
    YANLIS_KONU: "🔴🔴 BAŞKA KONUDAN CEVAPLANDI — sessiz yanlış",
    OLCU_YOK: "🟡 KONU TUTTU, ÖLÇÜ TUTMADI — menüye ad yaz",
    BOYUT_YOK: "🟠 KONU TUTTU, BOYUT TUTMADI — çekim/sinonim",
    KONU_YOK: "🔴 HİÇBİR ŞEY TUTMADI — mutfak eksiği",
}

KOVALAR = (YANLIS_KONU, OLCU_YOK, BOYUT_YOK, KONU_YOK)


def sema(sirket: str) -> dict:
    """⚠ Şema **taze derlemeden** okunur, `demo/wren-project`'ten değil.

    O dizin gitignore'lu bir **derleme artefaktıdır**; ölçüm aracı oradan okuduğunda aynı
    kaynakta farklı sayı üretti (ölçüldü: `sessiz_yanlis` 8 ve 17). Kapısı
    `tests/test_olcum_semasi_taze.py`.
    """
    from app.compose import build, compose
    from app.wren_service import WrenService

    td = tempfile.mkdtemp(prefix=f"menu-{sirket}-")
    out = Path(td) / "proje"
    compose(sirket, Path(__file__).resolve().parents[1] / "demo", out)
    build(out)
    return WrenService(out, datasource="duckdb", connection_info={}).schema()


def incele(soru: str, schema: dict, beklenen=None) -> dict | None:
    """Bir soruyu inceler. Boşluk yoksa `None` — alet **yalnız boşluğu** raporlar.

    ⚠ Hiçbir yeni eşleştirici yazılmıyor: `route` · `ilgili_cubelar` ·
    `measure_cube_candidates` **çağrılıyor**. Aletin gördüğü şey, üretimin gördüğünün
    tıpatıp aynısı olmalı — yoksa rapor gerçek olmayan bir kusuru anlatır.
    """
    from app import cube_router

    hit = cube_router.route(soru, schema)
    _cq = (hit or {}).get("cube_query") or {}
    if _cq.get("measures"):
        # 🔴🔴 CEVAPLANMIŞ OLMAK, DOĞRU CEVAPLANMIŞ OLMAK DEĞİLDİR. Bu dal olmasaydı alet
        # yapısal olarak **kör** olurdu: bir cevap gördüğü an susardı. Ölçüldü (`Y6`):
        # *«tamir süresi»* artık cevapsız değil — `kalite.toplam_ek_sure_dk` veriyor,
        # oysa tamir `bakim`'ın işi. *Bir boşluğu kapatmanın en sessiz yolu, onu yanlış
        # bir yemekle doldurmaktır.*
        _bek = (beklenen,) if isinstance(beklenen, str) else tuple(beklenen or ())
        if _bek and _cq.get("cube") not in _bek:
            return {"soru": soru, "kova": YANLIS_KONU, "cube": _cq.get("cube"),
                    "aday": [f"beklenen: {' | '.join(_bek)}"],
                    "kanit": f"verilen: {_cq.get('cube')}.{','.join(_cq.get('measures') or [])}"}
        return None

    konular = cube_router.ilgili_cubelar(soru, schema) or []
    olcu_adaylari = cube_router.measure_cube_candidates(soru, schema) or []
    if not konular and not olcu_adaylari:
        return {"soru": soru, "kova": KONU_YOK, "cube": None,
                "aday": [], "kanit": cube_router.teshis(soru, schema)}

    c = (konular[0] if konular else olcu_adaylari[0][0])
    ad = c.get("name")
    # Kırılım isteniyor mu — boyutun ADI mı tutmadı, ölçünün adı mı?
    _boyutlar = [str(d) for d in (c.get("dimensions") or [])]
    _boyut_tuttu = any(cube_router._syn_hit(soru, b) for b in _boyutlar)
    _kirilim_istendi = any(k in f" {soru.lower()} " for k in (" göre", " bazında", " bazlı"))
    kova = BOYUT_YOK if (_kirilim_istendi and not _boyut_tuttu) else OLCU_YOK
    aday = ([f"{ad}.{m}" for m in (c.get("measures") or [])] if kova == OLCU_YOK
            else [f"{ad}:{b}" for b in _boyutlar])
    return {"soru": soru, "kova": kova, "cube": ad, "aday": aday,
            "kanit": cube_router.teshis(soru, schema)}


def rapor(sorular, schema: dict) -> list[dict]:
    """`sorular`: dizi (beklenen yok) ya da `{soru: beklenen_cube}` sözlüğü."""
    _bek = sorular if isinstance(sorular, dict) else {}
    return [r for r in (incele(s, schema, _bek.get(s)) for s in sorular) if r]


def _yazdir(satirlar: list[dict]) -> None:
    for kova in KOVALAR:
        alt = [s for s in satirlar if s["kova"] == kova]
        if not alt:
            continue
        print(f"\n{KOVA_ADI[kova]}  ({len(alt)})")
        for s in alt:
            print(f"  • «{s['soru']}»")
            if s["cube"]:
                print(f"      konu: {s['cube']}  ·  aday: {', '.join(s['aday'][:6])}")
            if s["kanit"]:
                print(f"      red : {s['kanit']}")
    print(f"\nTOPLAM {len(satirlar)} boşluk — "
          + " · ".join(f"{KOVA_ADI[k].split(' — ')[0]}: "
                       f"{sum(1 for s in satirlar if s['kova'] == k)}"
                       for k in KOVALAR))


def main() -> int:
    ap = argparse.ArgumentParser(description="Menü ölçüm aleti (FAZ O-8 / G1)")
    ap.add_argument("--sirket", default="demo-boyahane")
    ap.add_argument("--sorular", help="satır satır soru içeren dosya")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.sorular:
        sorular = [s.strip() for s in
                   Path(a.sorular).read_text(encoding="utf-8").splitlines() if s.strip()]
    else:
        sorular = dict(KANIT_SORULARI)
    satirlar = rapor(sorular, sema(a.sirket))
    if a.json:
        print(json.dumps(satirlar, ensure_ascii=False, indent=2))
    else:
        _yazdir(satirlar)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
