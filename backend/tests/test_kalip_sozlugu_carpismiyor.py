"""KALIP SÖZLÜKLERİ KATALOGLA ÇARPIŞMIYOR — ölçüm disiplininin KAPIYA çevrilmiş hâli.

## Neden bu kapı var (kayma ölçüldü, 3 Ağustos 2026)

Faz E'de atıf sözlüğünü yazarken adayları katalogda **taradım** ve temiz çıktılar. Sonra
*"tekrar ailesi"*ni (`tekrar`, `yeniden`, `tekrarla`…) **taramadan** ekledim. Sonuç:

    test_sinonim_carpismasi: YENİ sinonim çakışması doğdu:
        'yeniden islenen': kalite → parti

`yeniden islenen` `kalite` cube'unun GERÇEK sinonimiydi; `yeniden` sözcüğünü ayıklamak
o kimliği yok ediyordu. Bu, 2a-1'in (`elektrik` kimliği silinince **388 cevap kayboldu**)
aynı hatasıdır ve `_misc_hit_words`'ün kendi notunda da yazılıdır:

> *"`fark` BİLEREK EKLENMEDİ — ölçüldü: gerçek ölçü sinonimi."*

Yani kural zaten yazılıydı; uygulanmasını **bir insan dikkatine** bırakmıştım. Bu dosya
onu bir kapıya çevirir: TEK SÖZCÜKLÜ her kalıp, katalogda sahipsiz OLMAK ZORUNDA.

## Neden yalnız TEK SÖZCÜKLÜ kalıplar

Çok sözcüklü kalıp (`yeniden ver`, `az once dedigin`) yapısı gereği güvenlidir: yalnız o
sözcükler **yan yana** geldiğinde eşleşir ve `yeniden islenen` dokunulmadan kalır.
Tehlike, koşulsuz silen tek sözcüktedir.

`_SOSYAL_*` bu kapıya DAHİL DEĞİL ve bu bilinçli: `iyi calismalar`'ın `calisma` sözcüğü
katalogda gerçekten vardır ve D1 bunu bir istisna listesiyle değil **tam kaplama**
ilkesiyle çözer (bkz. `cube_router.sosyal_edim`). Oradaki koruma başka bir mekanizmadır.
"""

from __future__ import annotations

import re

import pytest

from app.cube_router import _ATIF_KALIP
from app.llm import _norm
from app.tercih import _KALICI_ISARET

TEK_SOZCUKLU = sorted({k for k in (*_ATIF_KALIP, *_KALICI_ISARET) if " " not in k})


def _katalog_havuzu(schema: dict) -> set[str]:
    havuz: set[str] = set()

    def gez(o):
        if isinstance(o, str):
            havuz.add(_norm(o))
        elif isinstance(o, dict):
            for v in o.values():
                gez(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                gez(v)

    gez(schema.get("cubes") or [])
    return havuz


def test_TEK_SOZCUKLU_KALIP_VAR_ki_kapi_anlamli():
    """Kapı boş kümeyi test ediyorsa hiçbir şeyi korumuyordur."""
    assert TEK_SOZCUKLU, "tek sözcüklü kalıp kalmamış — kapı anlamsızlaştı"


@pytest.mark.parametrize("kelime", TEK_SOZCUKLU)
def test_TEK_SOZCUKLU_KALIP_KATALOGDA_SAHIPSIZ(kelime, schema):
    """Koşulsuz silinen bir sözcük, katalogda bir kimliğe ait OLAMAZ."""
    sahipler = [h for h in _katalog_havuzu(schema)
                if h and re.search(rf"\b{re.escape(kelime)}\b", h)]
    assert not sahipler, (
        f"{kelime!r} katalogda SAHİPLİ ({sahipler[:3]}) — koşulsuz ayıklanırsa o kimlik "
        f"kaybolur. Ya kalıbı çok sözcüklü yap ('{kelime} ver') ya da listeden çıkar.")
