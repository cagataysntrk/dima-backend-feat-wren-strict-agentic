"""🔴🔴 `§D10` — AYNI AD, **FARKLI FORMÜL**: bir kapsam farkı değil, bir TANIM farkı.

## Raporun iddiası ve ölçüm

> WisdomAI: *«biggest source of **unexplained trust erosion**»*. Bizde `§Cİ` bir terimin
> **iki küpte** olduğunu söylüyor — ama **iki farklı TANIMI** olduğunu söylemiyor.

Ölçüldü (2026-08-12, canlı katalog): **9 ölçü adı** birden çok küpte geçiyor.

| ölçü | küp | formül | |
|---|---|---|---|
| `toplam_fire_kg` | `oee` | `SUM(hatali_kg)` | 🔴 **FARKLI** |
| | `parti` | `SUM(CASE WHEN ilk_seferde_tamam = 0 THEN kg END)` | |
| `toplam_durus_dakika` | `bakim` | `SUM(durus_dakika)` | 🔴 **FARKLI** |
| | `oee` | `SUM(planli_durus_dk + plansiz_durus_dk)` | |
| `ilk_seferde_tamam_yuzde` | `oee` | `… / NULLIF(SUM(parti_sayisi),0)` | 🔴 **FARKLI** |
| | `parti` | `… / NULLIF(COUNT(*),0)` | |
| `bakiye` · `toplam_alacak` · `toplam_borc` · `toplam_dogalgaz_sm3` · `toplam_tep` · `toplam_uretim_kg` | — | **bayt bayt aynı** | ✅ |

⊙ Beyan dokuzunu da **aynı cümleyle** geçiyordu. İki durum aynı değil:

| durum | kullanıcı için |
|---|---|
| aynı formül, iki küp | bir **kapsam** tercihi — sayı ikisinde de aynı hesaplanır |
| **farklı formül** | bir **TANIM** farkı — öteki küpte sayı **başka bir şeydir** |

> *İki tanımı «aynı ad» diye bir araya koymak, farkı adın arkasına saklamaktır.*

⚠ Yüklem **yapısal**: `measure_expressions` karşılaştırılır — bir kelime listesi ya da
sezgi değil. İfade beyanı eksikse **fark iddia edilmez** (`§101.1`: bilinmeyeni bir fark
saymak, olmayan bir riski icat etmektir).
"""

from __future__ import annotations

import pytest

from app import belirsizlik_chipi as bc

_SEMA = {"cubes": [
    {"name": "oee", "measures": ["toplam_fire_kg"], "dimensions": ["makine"],
     "measure_expressions": {"toplam_fire_kg": "SUM(hatali_kg)"}},
    {"name": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["makine"],
     "measure_expressions": {
         "toplam_fire_kg": "SUM(CASE WHEN ilk_seferde_tamam = 0 THEN kg ELSE 0 END)"}},
    {"name": "cari", "measures": ["bakiye"], "dimensions": ["cari_kodu"],
     "measure_expressions": {"bakiye": "SUM(borc) - SUM(alacak)"}},
    {"name": "mizan", "measures": ["bakiye"], "dimensions": ["hesap"],
     "measure_expressions": {"bakiye": "SUM(borc) - SUM(alacak)"}},
    {"name": "beyansiz", "measures": ["toplam_fire_kg"], "dimensions": []},
]}


def test_FARKLI_FORMUL_YAKALANIR():
    """🔴 Kusurun ta kendisi: `toplam_fire_kg` iki küpte **başka bir hesap**."""
    assert bc.tanimlari_farkli_mi("toplam_fire_kg", ["oee", "parti"], _SEMA) is True


def test_AYNI_FORMUL_FARK_SAYILMAZ():
    """⊘ **Ön koşul — kapsam yutulmadı.** `bakiye` iki küpte aynı formülle hesaplanıyor;
    onu *«farklı tanım»* diye işaretlemek yanlış bir uyarıdır (`§101.1`)."""
    assert bc.tanimlari_farkli_mi("bakiye", ["cari", "mizan"], _SEMA) is False


def test_IFADE_BEYANI_EKSIKSE_FARK_IDDIA_EDILMEZ():
    """⚠ Bilinmeyeni bir fark saymak, olmayan bir riski icat etmektir."""
    assert bc.tanimlari_farkli_mi("toplam_fire_kg", ["oee", "beyansiz"], _SEMA) is False


def test_TEK_KUP_FARK_DEGILDIR():
    """⊘ Taban: tek küpte çakışma olmaz."""
    assert bc.tanimlari_farkli_mi("toplam_fire_kg", ["oee"], _SEMA) is False


def test_NOT_METNI_SERTLESIYOR():
    """🔴 Farklı tanımda cümle **başka bir şey söylemeli** — yoksa ayrımın kullanıcıya
    ulaşan bir karşılığı olmaz."""
    yumusak = bc.not_metni("toplam_fire_kg", "OEE", ["fire (parti)"])
    sert = bc.not_metni("toplam_fire_kg", "OEE", ["fire (parti)"], tanim_farkli=True)
    assert "FARKLI FORMÜLLE" in sert and "başka bir hesaptır" in sert
    assert "FARKLI FORMÜLLE" not in yumusak, "yumuşak cümle sertleşmiş — `KURAL B`"
    assert sert != yumusak


def test_KURAL_B_ESKI_CAGRI_BIREBIR_AYNI():
    """⚠ `tanim_farkli` **isteğe bağlı**: ölçmeyen çağıran eski cümleyi alır."""
    a = bc.not_metni("bakiye", "cari hesap", ["bakiye (mizan)"])
    b = bc.not_metni("bakiye", "cari hesap", ["bakiye (mizan)"], tanim_farkli=False)
    assert a == b
    assert a.startswith("«bakiye» birden fazla yerde tanımlı")


def test_ASK_YOLUNA_BAGLI():
    """🔴 Yazılıp çağrılmayan bir ayrım, yazılmamış bir ayrımdır.

    ⟳ **YÜKLEM İKİ KEZ YERE BAĞLANDI, İKİ KEZ KIRILDI (2026-08-12).** Önce `ask.py`'de
    `tanimlari_farkli_mi` çağrısını aradı; gövde `belirsizlik_chipi.not_metni`'ye
    taşınınca kırıldı. Sonra `olcu=next(iter(cq.get` dizisini aradı; gövde
    `beyani_ilistir`'e taşınınca yine kırıldı.

    ⊙ İki taşımayı da **büyüme kapısı** emretti (*«modüle çıkar, tavanı yükseltme»*) ve
    ikisi de doğruydu. Kırılan kapıydı, kural değil.

    *Bir kapıyı çağrının ADRESİNE bağlamak, ilk taşımada onu kırar* (ders ㉕).

    Yeni yüklem **zincirin iki halkasını** ölçer, adresini değil:
      ① `ask.py` belirsizlik beyanını **çağırıyor** mu
      ② sahibi farkı **gerçekten hesaplıyor** mu (çözülmüş ölçü adıyla)
    """
    import inspect
    import pathlib

    from app import belirsizlik_chipi as _bc

    kaynak = (pathlib.Path(__file__).parent.parent / "app" / "routers"
              / "ask.py").read_text(encoding="utf-8")
    assert "beyani_ilistir" in kaynak, (
        "🔴 `ask.py` belirsizlik beyanını çağırmıyor — beyan hiç iliştirilmez.")
    govde = inspect.getsource(_bc.beyani_ilistir) + inspect.getsource(_bc.not_metni)
    assert "tanimlari_farkli_mi" in govde, (
        "🔴 fark hesabı sahibinde yok — beyan yine dokuz vakayı aynı cümleyle geçer.")
    assert 'cq.get("measures")' in govde, (
        "🔴 karşılaştırma çözülmüş ÖLÇÜ ADIYLA yapılmıyor — kullanıcının sözcüğü "
        "`measure_expressions`'ta bulunmaz ve fark hep susar (canlı curl bunu yakaladı).")


@pytest.mark.parametrize("olcu,kupler", [
    ("toplam_fire_kg", ["oee", "parti"]),
    ("toplam_durus_dakika", ["bakim", "oee"]),
    ("ilk_seferde_tamam_yuzde", ["oee", "parti"]),
])
def test_GERCEK_KATALOGDA_UC_VAKA(olcu, kupler, schema):
    """🔴 **Gerçek katalogla** ölçülür: bu üçü bugün farklı formülle tanımlı.

    ⚠ Bir gün eşitlenirlerse bu test kırılır ve **iyi haber** verir — o gün kayıt
    güncellenmelidir. *Bir kusurun kapısı, kusur kalkınca da konuşmalıdır.*
    """
    assert bc.tanimlari_farkli_mi(olcu, kupler, schema) is True, (
        f"✅ `{olcu}` artık {kupler} küplerinde AYNI formülle tanımlı — tanım çakışması "
        "kalkmış olabilir; `§D10` kaydı güncellensin.")
