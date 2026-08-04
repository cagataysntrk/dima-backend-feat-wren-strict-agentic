"""FAZ 0.14 / **K3 — TERS YETİM**: frontend'in beklediği ama backend'in VERMEDİĞİ alan.

## Neden kurulur

K1/K2 tek yönü tarar: *"backend üretiyor, frontend tüketiyor mu?"* Ters yön hiç
sorulmuyordu: **frontend bir alanı okuyor ama backend onu hiç göndermiyorsa** ekranda
sessizce `undefined` belirir — çökme yok, uyarı yok, yalnız **boş bir kutu**.

TypeScript bunu yakalamaz: `types.ts` elle yazılmış bir **beyandır**, `schemas.py`'den
türetilmiyor. İki taraf ayrıştığında derleyici mutlu, kullanıcı boş ekrana bakıyor.

> Bugün **temiz** — ve kapı tam bu yüzden kurulur: *temiz kalsın diye.*
> `MIMARI §14`: arka-ön sözleşmesi iki yönlüdür.
"""

from __future__ import annotations

import re

import pytest

from tests.kapi_ortak import frontend_dir, yorumsuz

#: FE'de tanımlı olup backend'de karşılığı ARANMAYAN alanlar — her biri GEREKÇELİ.
ISTEMCI_ALANI: dict[str, str] = {
    "steering_golgede": "İSTEMCİ TARAFINDA üretilir (`page.tsx`), backend bu alanı "
                        "GÖNDERMEZ — `types.ts`'in kendi yorumunda yazılı.",
}


def _fe_arayuz(ad: str) -> list[str]:
    """`types.ts`'teki bir arayüzün alan adları."""
    kaynak = yorumsuz((frontend_dir() / "lib" / "types.ts").read_text(encoding="utf-8"))
    m = re.search(rf"export interface {ad} \{{(.*?)\n\}}", kaynak, re.S)
    if not m:
        pytest.skip(f"`{ad}` arayüzü types.ts'te bulunamadı")
    return re.findall(r"^\s{2}(\w+)\??:", m.group(1), re.M)


def test_K3_FRONTENDIN_BEKLEDIGI_HER_ALANI_BACKEND_VERIYOR():
    """🔴 **ASIL KAPI.** `types.ts::AskResponse`'un her alanı `schemas.py::AskResponse`'ta
    da olmalı. Yoksa frontend `undefined` render eder ve kimse fark etmez."""
    from app.schemas import AskResponse

    be = set(AskResponse.model_fields)
    fe = _fe_arayuz("AskResponse")
    assert fe, "types.ts::AskResponse alanları okunamadı — çapa kaymış"
    ters = [a for a in fe if a not in be and a not in ISTEMCI_ALANI]
    assert not ters, (
        "TERS YETİM (frontend okuyor, backend GÖNDERMİYOR):\n  " + "\n  ".join(sorted(ters))
        + "\n\nEkranda sessizce `undefined` belirir — çökme yok, uyarı yok, boş kutu var.\n"
          "Ya backend'e ekle, ya FE'den çıkar, ya ISTEMCI_ALANI'na GEREKÇESİYLE yaz.")


def test_K3_ISTEMCI_ALANI_BEYANI_BAYATLAMAZ():
    """Muafiyet kendiliğinden erimemeli: artık FE'de olmayan bir alan için gerekçe
    taşımak, listeyi bir çöplüğe çevirir ve kapıyı okunamaz yapar."""
    fe = set(_fe_arayuz("AskResponse"))
    olmayan = sorted(a for a in ISTEMCI_ALANI if a not in fe)
    assert not olmayan, f"ISTEMCI_ALANI'nda artık FE'de olmayan alan(lar): {olmayan}"


def test_K3_ISTEMCI_ALANI_her_satirda_GEREKCE_tasir():
    for ad, gerekce in ISTEMCI_ALANI.items():
        assert len(gerekce) > 30, f"`{ad}` için gerekçe yetersiz: {gerekce!r}"
