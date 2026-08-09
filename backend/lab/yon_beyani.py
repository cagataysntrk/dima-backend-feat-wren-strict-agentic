"""YÖN BEYANI ENVANTERİ — *hangi ölçü «az olan iyi» olabilir ama beyan edilmemiş?*

## Neden bu alet — ölçülmüş bir sessiz yanlıştan doğdu

`ilkeller.bagla` *«en kötü hangisi»* sorusunu **beyandan** cevaplar (`lower_is_better`).
Beyan yoksa *«çok olan iyi»* varsayar. Ölçüldü (`GG8`, canlı):

    soru : «bu yıl en çok geciken müşteriyi bul»
    seçim: ort_gecikme_gun = **-25,3**      ← en ERKEN teslim edilen müşteri

⊙ `§W-C` bir sıfatın yönünü **sözlükten değil beyandan** okumayı öğretmişti. Ama beyan
yoksa okunacak bir şey de yoktur. *Eksik bir beyan, yanlış bir beyandan daha sessizdir:
yanlış beyan tartışılır, eksik beyan varsayılır.*

## 🔴 BU ALET KARAR VERMEZ — bir İŞ LİSTESİ üretir

`r1_envanteri`'nin dersi aynen geçerli (kararı araç verince korpus %93,2 → %92,6):
yön bir **alan kararıdır**. `iade` bir perakendecide kötüdür, bir kiralama şirketinde
işin kendisidir. Alet yalnız *«burada bir beyan eksik olabilir»* der.

⚠ Ve bu yüzden bir **kapı değil**: adına bakıp yön çıkaran bir yüklem, kendi
yanlış-pozitiflerini üretirdi (`§101.1`) — `maliyet_dusus_yuzde` adında `maliyet`
geçer ama artması iyidir.

## Kullanım

    python lab/yon_beyani.py
    python lab/yon_beyani.py --sirket gitas
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

#: Adında geçtiğinde **yön sorusu sorulmayı hak eden** kökler. ⚠ Bir cevap değil bir
#: **soru** listesi: her biri insana *«bunun azı mı iyi?»* diye sordurur.
KOTULUK_KOKLERI: tuple[str, ...] = (
    "gecikme", "geciken", "hata", "sikayet", "şikayet", "kaza_", "_kaza",
    "ariza", "arıza", "fire", "durus", "duruş", "kayip", "kayıp", "iade",
    "maliyet", "gider", "atik", "atık", "sapma", "red_", "_red",
)
#: ⟳ İlk hâlde `ret` · `devir` · `tuketim` · çıplak `kaza` vardı ve **yanlış-pozitif
#: üretti**: `ges_u**ret**imi_kwh` · `**kaza**nma_orani_yuzde` · `elektrik_tuketimi`
#: (tüketim bir işletmede kötü, bir satıcıda ciro). Ölçüldü ve ayıklandı.
#:
#: 🔴 Ve bu ayıklama aletin **kendi ilkesinin** gereği: yanlış-pozitiflerle dolu bir
#: rapor **okunmaz**, okunmayan bir rapor da olmayan bir rapordur (`§101.1`'in ruhu).
#: *Bir soru listesinin değeri, sorulmaya değer soru oranındadır.*


def envanter(schema: dict) -> list[dict]:
    out: list[dict] = []
    for c in (schema.get("cubes") or []):
        _az = set(c.get("lower_is_better") or [])
        for m in (c.get("measures") or []):
            ad = str(m).lower()
            if m in _az:
                continue
            vurulan = [k for k in KOTULUK_KOKLERI if k in ad]
            if vurulan:
                out.append({"cube": c.get("name"), "olcu": str(m), "kok": vurulan})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Yön beyanı envanteri")
    ap.add_argument("--sirket", default="")
    a = ap.parse_args()

    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    schema = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                         connection_info=s.connection_dict()).schema()
    r = envanter(schema)
    _beyanli = sum(len(c.get("lower_is_better") or []) for c in (schema.get("cubes") or []))
    print(f"\nbeyanlı ölçü: {_beyanli}  ·  🔴 SORU SORULACAK: {len(r)}\n")
    for x in r:
        print(f"  {x['cube']}.{x['olcu']:<32} (kök: {', '.join(x['kok'])})")
    print("\n⊙ Bu bir kusur listesi DEĞİL, bir SORU listesidir: her satır insana "
          "*«bunun azı mı iyi?»* diye sordurur.")
    print("⚠ Alet karar vermez — yön bir ALAN kararıdır (`iade` bir perakendecide "
          "kötüdür, bir kiralama şirketinde işin kendisidir).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
