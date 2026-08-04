"""FAZ 0.20 — **BAYRAK PROFİLLERİ.** Kombinasyonlar da test edilir, tek tek değil.

## Ölçülen boşluk

EK E'de **~70 bayrak** var ve §C/10'un hedefi *"ölü bayrak **0**"*. Her maddenin
`GERİ AL`'ı **tek tek** test ediliyor — *"bayrak `off` iken davranış birebir bugünkü"*.
Ama **kombinasyonlar hiç test edilmiyor**: iki bayrağın birlikte açık olması, ikisinin
ayrı ayrı doğru olmasından **bağımsız** bir davranıştır.

## Üç adlandırılmış profil

| Profil | Ne demek | Neden var |
|---|---|---|
| **`taban`** | hepsi `off` | `KURAL A`'nın kod karşılığı: *"dondurulmuş taban"*. Bir gerilemenin bayraktan mı yoksa koddan mı geldiğini ayıran **tek** ölçüm noktası |
| **`v1-varsayilan`** | bugün `features.yml`'de ne varsa | Kullanıcının **gerçekten gördüğü** sistem. Kapı buna karşı koşmazsa, ölçülen şey kimsenin kullanmadığı bir yapılandırmadır |
| **`v1-tam`** | v1 kapsamındaki her şey açık | *"Hedef durum bugün çöküyor mu?"* — bir bayrağı açmadan **önce** sorulması gereken soru |

## 🔴 YAŞAM DÖNGÜSÜ — bu maddenin asıl işi

`v1-varsayilan`'da **iki sürüm** açık kalan bir bayrak **SİLİNİR** (kod kalıcılaşır,
bayrak gider). Yoksa §C/10'un *"ölü bayrak 0"* hedefi, sayı büyüdükçe **matematiksel
olarak** tutturulamaz: her yeni özellik bir bayrak ekler, hiçbiri kaldırılmaz.

Bir bayrak bir **karar anıdır**, bir mülk değil.
"""

from __future__ import annotations

import pathlib
from typing import Any

import yaml

YAML_YOLU = pathlib.Path(__file__).resolve().parent.parent / "demo" / "packs" / "features.yml"

#: Profil adları. 🔴 Bu bir **SAYILAN KÜME değil**: kullanıcıya dönük bir anlam ekseni
#: değil, bir **koşum yapılandırması** taksonomisi. `KAT-5` anlam eksenlerinin literal
#: listelenmesini yasaklar; bunlar ölçüm senaryolarıdır.
TABAN = "taban"
V1_VARSAYILAN = "v1-varsayilan"
V1_TAM = "v1-tam"


def _yaml_bayraklari() -> dict[str, str]:
    d = yaml.safe_load(YAML_YOLU.read_text(encoding="utf-8")) or {}
    return dict(d.get("features") or {})


def profil(ad: str) -> dict[str, str]:
    """Adlandırılmış profilin bayrak haritası.

    `taban` **boş sözlük** döner — `resolve_for` bir bayrağı ancak sözlükte varsa
    açık sayar, yani boş harita *"hepsi kapalı"* demektir ve bu **`KURAL A`'nın kod
    karşılığıdır**.
    """
    if ad == TABAN:
        return {}
    if ad == V1_VARSAYILAN:
        return _yaml_bayraklari()
    if ad == V1_TAM:
        from app.features import FLAG_REGISTRY

        # v1-tam = kayıttaki HER bayrak `beta`. `prod` olanlar `prod` kalır: onlar zaten
        # kalıcılaşmış kararlardır, geri çevirmek profili yanıltıcı yapardı.
        bugun = _yaml_bayraklari()
        return {k: ("prod" if bugun.get(k) == "prod" else "beta") for k in FLAG_REGISTRY}
    raise ValueError(f"bilinmeyen profil: {ad!r} (geçerli: {TABAN}·{V1_VARSAYILAN}·{V1_TAM})")


def olu_bayraklar() -> dict[str, str]:
    """§C/10 — *"ölü bayrak 0"*. Üç sınıf, üçü de **gerekçesiyle** raporlanır.

    * **kayıtta var, YAML'de yok** → bayrak tanımlı ama hiçbir ortamda çözülmüyor
    * **YAML'de var, kayıtta yok** → değer var ama **belgesi yok** (admin ekranında
      etiketi/açıklaması olmayan bir anahtar)
    """
    from app.features import FLAG_REGISTRY

    yaml_b = _yaml_bayraklari()
    out: dict[str, str] = {}
    for k in sorted(set(FLAG_REGISTRY) - set(yaml_b)):
        out[k] = "kayıtta var, YAML'de yok — hiçbir ortamda çözülmüyor"
    for k in sorted(set(yaml_b) - set(FLAG_REGISTRY)):
        out[k] = "YAML'de var, kayıtta yok — etiketi/açıklaması olmayan anahtar"
    return out


def yasam_dongusu_borclari(gecmis: dict[str, int] | None = None,
                           esik: int = 2) -> dict[str, int]:
    """🔴 **İki sürüm açık kalan bayrak SİLİNMELİ** (kod kalıcılaşır, bayrak gider).

    `gecmis`: `bayrak → kaç sürümdür açık`. Kaynak dışarıdan verilir çünkü *"sürüm"*
    bu depoda bir **karardır**, otomatik türetilebilir bir sayı değil — uydurmak,
    ölçüm gibi görünen bir tahmin üretirdi.

    Boş `gecmis` → boş borç: **ölçülmemiş bir borç, borç değildir.** (`⊘` disiplini.)
    """
    if not gecmis:
        return {}
    acik = {k: v for k, v in _yaml_bayraklari().items() if v != "off"}
    return {k: n for k, n in sorted(gecmis.items()) if k in acik and n >= esik}


def profil_ozeti() -> dict[str, Any]:
    """Üç profilin yan yana özeti — *"hangi profilde kaç bayrak açık"*."""
    return {
        ad: {"acik": sum(1 for v in profil(ad).values() if v != "off"),
             "toplam": len(profil(ad))}
        for ad in (TABAN, V1_VARSAYILAN, V1_TAM)
    }
