"""🔴 `§72` — **PLANIN FAZLARI KAPANDI**: iddia bir cümle değil, bir **kapı**.

`§42` dokuz faz sayıyor (`FAZ 0`–`FAZ 8`). Bu operasyonun sonunda hepsinin bir kod
karşılığı var; ama *«kapandı»* demek bir **beyandır** ve bu depoda beyanlar kapıya
bağlanır ㉕ — yoksa bir dosya silindiğinde/yeniden adlandırıldığında iddia sessizce
yalan olur.

| faz | kod karşılığı | durum |
|---|---|---|
| `0` ölçüm | `lab/oneri_olcum.py` | ✅ |
| `1` `emin_miyim` | `app/emin_miyim.py` | ✅ |
| `2` marj kapılı oto-icra | `cube_router` ↔ `emin_miyim.karar` | ✅ |
| `3` aday yan kanalı | `AskResponse.suggestions` / chip'ler | ✅ |
| `4` kıyas temeli chip'i | `app/kiyas*` · `InterpretationBar` | ✅ |
| `5` öneri motoru | `app/oneri.py` | ✅ |
| `6` uç + FE şeridi | `routers/oneri.py` · `OneriSeridi.tsx` | ✅ |
| `7` çapa · pill · makro · **plan önizleme** | `pill.py` · `makro.py` · `plan_tuketici` · `PlanOnizleme.tsx` | ✅ *(planda ⊘ **DEMO DIŞI**'ydı; kullanıcı kararıyla açıldı — `§63`–`§70`)* |
| `8` hasat döngüsü | `app/hasat.py` · `lab/sozluk_hasadi.py` | ✅ **8.3 hariç** (ölçüme bağlı ⊘) |

⚠ `FAZ 7`'nin hikâyesi bir ders: plan onu *«iddiayı kanıtlamıyor, zenginleştiriyor»* diye
ertelemişti. Kullanıcı **tersini** söyledi — asıl iş **rol değişikliğiydi** ve o fazın
içindeydi. *Bir planın kendi önceliklendirmesi de bir varsayımdır.*

⚠ `8.3` (`ε` karıştırma) **kapanmadı ve kapanmamalı**: kendi kapısı
(`test_EPSILON_ERTELEMESI_HALA_GECERLI`) *«ölçmeden konan bir `ε` listeyi bozar ve
karşılığında hiçbir sayı üretmez»* diyor 🆕. Bu kapı onu **tekrar etmez**, yalnız
varlığını şart koşar ㊲.
"""

from __future__ import annotations

import pathlib

import pytest

_KOK = pathlib.Path(__file__).resolve().parents[1]
_FE = _KOK.parent / "dima-frontend-demo-master" / "src"

#: `§42`'nin fazları → **kodda** aranacak karşılık. ⚠ Dosya yolu, bir sözcük değil:
#: *«sözü değil kullanımı ara»* 🅞 ilkesinin dosya düzeyindeki hâli.
FAZ_KARSILIGI = {
    "0 ölçüm": "lab/oneri_olcum.py",
    "1 emin_miyim": "app/emin_miyim.py",
    "5 öneri motoru": "app/oneri.py",
    "6 uç": "app/routers/oneri.py",
    "7 pill": "app/pill.py",
    "7 makro": "app/makro.py",
    "7 plan önizleme": "app/plan_tuketici.py",
    "8 hasat": "app/hasat.py",
    "8.6 hasat koşucusu": "lab/sozluk_hasadi.py",
}


@pytest.mark.parametrize("faz", sorted(FAZ_KARSILIGI))
def test_FAZIN_KOD_KARSILIGI_DURUYOR(faz):
    """🔴 **ASIL DEĞİŞMEZ.** *«Kapandı»* iddiası, karşılığı silinince kırmızı vermeli."""
    yol = _KOK / FAZ_KARSILIGI[faz]
    assert yol.exists(), (
        f"🔴 `FAZ {faz}`'ın kod karşılığı yok: {FAZ_KARSILIGI[faz]}\n"
        "`ONGORU-DURUM.md §72` bu fazı **kapandı** ilan ediyor — ya dosya taşındı ve bu "
        "kapı güncellenmeli, ya da iddia artık yalan.")


def test_FAZ7_FE_YUZU_DURUYOR():
    """`FAZ 7` **arka uçta bitmez**: önizlemenin bir yüzü olmalı 🆘."""
    if not _FE.exists():
        pytest.skip("frontend mount edilmedi — kapı kapsamı dışında")
    assert (_FE / "components" / "PlanOnizleme.tsx").exists(), (
        "🔴 `FAZ 7`'nin yüzü yok — bir yetenek, tüketicisi olmadan «bitti» değildir")


def test_FAZ8_3_ERTELEMESI_KENDI_KAPISINDA():
    """⊘ `8.3` **açık** ve öyle kalmalı; ertelemenin bekçisi **kendi** kapısıdır ㊲ —
    bu dosya onu tekrar etmez, **varlığını** şart koşar (iki yerde savunulan bir karar,
    bir gün iki farklı karara dönüşür)."""
    kapi = _KOK / "tests" / "test_hasat_konum_yanliligi.py"
    assert kapi.exists(), "🔴 hasat kapısı yok"
    assert "test_EPSILON_ERTELEMESI_HALA_GECERLI" in kapi.read_text(encoding="utf-8"), (
        "🔴 `8.3` ertelemesinin bekçisi kaldırılmış — `ε` artık sessizce girebilir")


def test_ZIT_OLCUT_KAPI_GERCEKTEN_ARIYOR():
    """🆃 Var olmayan bir yol **kırmızı** vermeli; yoksa bu kapı bir süs olurdu."""
    assert not (_KOK / "app" / "olmayan_faz.py").exists()
