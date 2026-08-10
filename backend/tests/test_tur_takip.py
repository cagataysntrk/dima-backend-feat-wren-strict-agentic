"""FAZ 5.1 kapısı — **6. tür: *"bunu takip et"***. [bayrak: `tur_takip`]

## Ölçülen erişilemezlik

`followup.sinifla` koşuldu: *"bunu takip et"* → **`SINIF_YENI`** → kapsam kapısı **R10** →
dürüst red. `takip et` grep'i `followup.py` ve `cube_router.py`'de **sıfırdı**. Yani
panoya/zamanlamaya giden **hiçbir doğal-dil yolu yoktu** — kullanıcı 🔔 ve *"+ panoya
ekle"* düğmelerini **fareyle bulmak zorundaydı**. MIMARI §12.11 bunu kendisi itiraf
ediyor: *"**Henüz YOK** — reçete kartından tek tıkla `schedules.create`"*.

## 🔴 Bu fazın en kolay hatası: ikinci bir zamanlama yolu açmak

`zamanla.olustur` eylemi, `EYLEM_KAYIT`, onay ucu ve `schedules.create_schedule`
**zaten vardı**. Eksik olan tek şey **erişimdi**. Kapı, yeni bir motor yazılmadığını
kilitler.
"""

from __future__ import annotations

import pytest

from app import eylem, followup
from app.cube_router import _norm

_CQ = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}

#: 🔴 **≥10 GERÇEK İFADE VARYANTI** (5.3 disiplini: tasarımcının değil kullanıcının
#: kelimeleri). Hepsi bir **işaret zamiri** ya da **kısa soru** taşır — aksi hâlde tür
#: konu değişimini çalardı.
_VARYANTLAR = [
    "bunu takip et",
    "bunu takibe al",
    "bunu izle",
    "bunu izlemeye al",
    "bunu bildir",
    "bu raporu takip et",
    "bu raporu izle",
    "bundan haberim olsun",
    "bunu gundemde tut",
    "bunu takipte kal",
    "takip et",
    "izle",
]


@pytest.mark.parametrize("ifade", _VARYANTLAR)
def test_ON_IKI_GERCEK_IFADE_tanINIR(ifade):
    """*"Bunu takip et"* artık **R10'a düşmüyor**."""
    n = followup.sinifla(ifade, baglam_var=True)
    assert n.sinif == followup.SINIF_KONUSMA, (
        f"`{ifade}` konuşma sınıfına girmedi → {n.sinif}/{n.kural}. Ölçülen erişilemezlik "
        f"tam olarak buydu: kullanıcı düğmeyi fareyle aramak zorunda kalıyordu.")
    assert n.tur == followup.TUR_TAKIP


def test_KONU_DEGISIMINI_calmaz():
    """🔴 *"Fire takibi nasıl yapılır"* eldeki raporu zamanlamak **değil**, yeni bir konu.

    Zamir/kısalık şartı olmasa bu tür `konu_degisimi` senaryo sınıfını **çalardı** —
    `TUR_ANLAT`'ın aynı disiplini ve aynı gerekçesi.
    """
    for yeni_konu in ("fire takibi nasil yapilir",
                      "makine bazinda enerji takibi icin ne gerekir",
                      "kalite izleme sureci nedir"):
        n = followup.sinifla(yeni_konu, baglam_var=True)
        assert n.tur != followup.TUR_TAKIP, f"`{yeni_konu}` konu değişimini çaldı"


def test_baglam_YOKKEN_takip_turu_ACILMAZ():
    n = followup.sinifla("bunu takip et", baglam_var=False)
    assert n.sinif == followup.SINIF_YENI and n.kural == "baglam-yok"


def test_PERIYOT_UYDURULMAZ_sorulur():
    """🔴 *"Bunu takip et"* bir **sıklık söylemez**.

    Sessizce haftalığa çevirmek, kullanıcının **istemediği** bir zamanlama kurmak olurdu —
    ve zamanlama `geri_alinabilir=False`'tır: kurulmuş bir gönderim geçmişe dönük
    silinemez. Bu, `ADR-0007-K3`'ün (*dönem eksikse SOR*) **yazma tarafındaki** karşılığı.
    """
    k = eylem.takip_karari(_norm("bunu takip et"), _CQ, schema=None)
    assert k is not None
    assert k.oneri is None, (
        "🔴 Periyot söylenmeden bir zamanlama ÖNERİSİ üretilmiş. Onay kartında bir sıklık "
        "görünecek ve o sıklığı kullanıcı SÖYLEMEDİ — uydurulmuş bir varsayılan, onay "
        "alınmış gibi görünen bir uydurmadır.")
    assert k.chipler, "periyot sorulmalı — chip'siz bir soru cevaplanamaz"
    assert any("hafta" in c for c in k.chipler)


def test_PERIYOT_VARSA_var_olan_ZAMANLA_dali_kullanilir():
    """🔴 **Yeni motor YAZILMADI** — `degerlendir()`'in kendi dalı çağrılır."""
    k = eylem.takip_karari(_norm("bunu her hafta pazartesi gonder"), _CQ, schema=None)
    assert k is not None and k.oneri is not None
    assert k.oneri["eylem"] == eylem.ZAMANLA
    assert k.oneri["izin"] == "schedule:create"
    assert k.oneri["geri_alinabilir"] is False, (
        "🔴 Zamanlama GERİ ALINABİLİR işaretlenmiş — kurulmuş bir gönderim geçmişe dönük "
        "silinemez ve onay kartı bunu yanlış anlatır.")
    assert k.oneri["argumanlar"]["every"] == "week"


def test_CAPA_YOKKEN_durust_sinir_beyani():
    """Rapor yoksa *"neyi takip edeyim"* — sessiz düşme YOK."""
    k = eylem.takip_karari(_norm("bunu takip et"), None, schema=None)
    assert k is not None and k.oneri is None
    assert "önce" in k.not_.lower() or "neyi" in k.not_.lower()


def test_ONAYSIZ_ZAMANLAMA_OLUSMAZ():
    """🔴 **Değişmez:** öneri bir zamanlama **kurmaz**; onay ayrı bir HTTP isteğidir.

    ⚠ Belirteç **AST**: `takip_karari` bir `Karar` döner ve o `Karar` yalnız bir **öneri
    sözlüğü** taşır. Fonksiyonun içinde bir zamanlama yazıcısı çağrılıyorsa bu değişmez
    çiğnenmiştir.
    """
    import ast
    from pathlib import Path

    agac = ast.parse((Path(__file__).resolve().parents[1] / "app/eylem.py")
                     .read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "takip_karari")
    cagrilar = {getattr(c.func, "attr", getattr(c.func, "id", ""))
                for c in ast.walk(fn) if isinstance(c, ast.Call)}
    for yasak in ("create_schedule", "add", "commit", "exec"):
        assert yasak not in cagrilar, (
            f"🔴 `takip_karari` `{yasak}` çağırıyor — ÖNERİ bir yazma yapamaz. Onay, "
            f"kullanıcının kendi kimliğiyle attığı AYRI bir istektir (FAZ H değişmezi).")


def test_ZAMANLA_eylemi_KAYITTA_ve_yetkisi_dogru():
    """Yazma yüzeyi `EYLEM_KAYIT`'ın boyu kadardır — ve o kayıt okunabilir."""
    b = eylem.beyan(eylem.ZAMANLA)
    assert b.izin == "schedule:create"
    assert b.geri_alinabilir is False
    assert b.uc == "schedules.create_schedule"


def test_BAYRAK_kayitli_ve_ACIK():
    """🔴 `F6`/`D1` — **AÇILDI (2026-08-10) ve bu test onun KAYDIDIR.**

    Bu kapı bayrağın **kapalı** olduğunu kilitliyordu ve doğru yapıyordu: bir
    bayrağın durumu, kimsenin farkına varmadan değişebilecek bir şey olmamalı.
    Açmak **bilinçli bir edimdir** ve bedeli bu satırı gerekçesiyle güncellemektir.

    ⊙ Gerekçe: *«yeni motor yazılmadı, yalnız ERİŞİM açılıyor»* — `zamanla.olustur`
    zaten var ve bu dosyanın kalan testleriyle kapılı. Kapalı kalmasının sebebi bir
    tasarım kararı değil bir **unutulmuşluktu**.

    *Bir bayrağın durumunu bir teste bağlamak, onu değiştirmeyi zorlaştırmak için
    değil; değiştirenin gerekçe yazmasını zorunlu kılmak içindir.*
    """
    from app.features import FLAG_REGISTRY

    assert "tur_takip" in FLAG_REGISTRY
    import yaml
    from pathlib import Path

    d = yaml.safe_load((Path(__file__).resolve().parents[1] / "demo/packs/features.yml")
                       .read_text(encoding="utf-8"))
    assert d["features"]["tur_takip"] == "beta", (
        "bayrak durumu değişmiş — bu bir kaza olamaz. Değiştiren, bu testin "
        "docstring'ine GEREKÇESİNİ yazmalı. `on`'a çıkarken de aynı kural: "
        "yazılı bir `on` şartı olmadan hiçbir bayrak `on` olmaz (`E-4`).")
