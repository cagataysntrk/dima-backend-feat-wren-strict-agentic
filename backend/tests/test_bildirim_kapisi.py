"""FAZ 5.9 kapısı — **bildirim kapısı: dört sıralı adım.**

## Ölçülen boşluk

`brief|digest` grep'i **sıfırdı**: her schedule **ayrı bildirim** atıyordu.
🔴 *Bir uyarı sistemi, susturulduğu anda ölür* — ve susturulmasının en hızlı yolu
**tekrarıdır**, yanlışlığı değil.

## Sıra bağlayıcı

    dedup_key → suppression_window → önem sıralaması → correlation_group

Ters sırada bir birleştirme, bastırılacak bir sinyali gruba sokup **grubun tamamını**
kurtarırdı — yani bastırma kuralı **sessizce delinirdi**.
"""

from __future__ import annotations

import pytest

from app.bildirim_kapisi import (
    MUAF_ONEM,
    VARSAYILAN_PENCERE,
    bastirilir_mi,
    correlation_group,
    dedup_key,
    kapidan_gecir,
    tercih_izin_veriyor_mu,
)


def _o(kaynak_id="s1", yon="yukseldi", onem="warning", tip="schedule"):
    return {"kaynak_tip": tip, "kaynak_id": kaynak_id, "yon": yon, "onem": onem}


def test_AYNI_anahtar_pencere_icinde_IKINCI_KEZ_gonderilmez():
    a = dedup_key("schedule", "s1", "yukseldi")
    gecmis = {a: 1000.0}
    assert bastirilir_mi(a, "warning", gecmis, 1000.0 + 60) is True
    assert bastirilir_mi(a, "warning", gecmis, 1000.0 + VARSAYILAN_PENCERE + 1) is False


def test_BASTIRILAN_KAYITTA_DURUYOR():
    """🔴 *Bastırma bir GÖRÜNÜRLÜK kararıdır, bir KAYIT kararı değil.*

    Kayıt silinirse *"neden bana haber verilmedi"* sorusunun cevabı kimsede olmaz — ve
    o soru bir olaydan **sonra** sorulur.
    """
    a = dedup_key("schedule", "s1", "yukseldi")
    r = kapidan_gecir([_o()], {a: 1000.0}, 1060.0)
    assert r["gonderilecek"] == []
    assert len(r["bastirilan"]) == 1
    assert r["bastirilan"][0]["bastirildi"] is True
    assert r["bastirilan"][0]["dedup_key"] == a


def test_YON_anahtarin_PARCASI():
    """⚠ *"Fire yükseldi"* ile *"fire normale döndü"* **aynı kaynaktan** gelir ama
    **farklı haberlerdir**.

    Yönü anahtardan çıkarmak, **iyi haberi kötü haberin penceresinde bastırırdı** ve
    kullanıcı sorunun **çözüldüğünü** hiç öğrenmezdi.
    """
    assert dedup_key("schedule", "s1", "yukseldi") != dedup_key("schedule", "s1", "dustu")
    gecmis = {dedup_key("schedule", "s1", "yukseldi"): 1000.0}
    r = kapidan_gecir([_o(yon="dustu")], gecmis, 1060.0)
    assert len(r["gonderilecek"]) == 1, (
        "🔴 İyi haber, kötü haberin penceresinde bastırıldı — kullanıcı sorunun "
        "çözüldüğünü hiç öğrenmez.")


def test_CRITICAL_bastirilmaz():
    """🔴 *Tekrar rahatsız edicidir; kaçırılan bir kritik sinyal **geri alınamaz**.*"""
    assert "critical" in MUAF_ONEM
    a = dedup_key("schedule", "s1", "yukseldi")
    assert bastirilir_mi(a, "critical", {a: 1000.0}, 1001.0) is False
    r = kapidan_gecir([_o(onem="critical")], {a: 1000.0}, 1001.0)
    assert len(r["gonderilecek"]) == 1 and not r["bastirilan"]


def test_ONEM_SIRALAMASI_kararli():
    """⚠ Aynı önemde **geliş sırası** korunur: aksi hâlde aynı girdi farklı turlarda
    farklı sıralanır ve kullanıcı bunu bir **değişiklik** sanardı."""
    olaylar = [_o("a", onem="info"), _o("b", onem="critical"),
               _o("c", onem="info"), _o("d", onem="warning")]
    sirali = kapidan_gecir(olaylar, {}, 0.0)["gonderilecek"]
    assert [x["kaynak_id"] for x in sirali] == ["b", "d", "a", "c"]


def test_CORRELATION_GROUP_yonu_ICERMEZ():
    """*Gruplama bir SUNUM kararı, dedup bir GÖNDERİM kararıdır.*"""
    assert (correlation_group(_o(yon="yukseldi"))
            == correlation_group(_o(yon="dustu")))
    assert correlation_group(_o("s1")) != correlation_group(_o("s2"))


def test_GRUPLAMA_bastirilmislari_KURTARMAZ():
    """🔴 **Sıranın tüm sebebi bu.**

    Ters sırada bir birleştirme, bastırılacak bir sinyali gruba sokup **grubun tamamını**
    kurtarırdı — bastırma kuralı sessizce delinirdi.
    """
    a = dedup_key("schedule", "s1", "yukseldi")
    r = kapidan_gecir([_o("s1", yon="yukseldi"), _o("s1", yon="dustu")],
                      {a: 1000.0}, 1060.0)
    tum = [x for g in r["gruplar"].values() for x in g]
    assert len(tum) == 1, "🔴 Bastırılan olay gruba sızdı ve grup onu kurtardı."
    assert tum[0]["yon"] == "dustu"


def test_TERCIH_opt_out_UYGULANIR():
    """🔴 `NotificationPreference` bugüne kadar **yetim** tabloydu (0 satır, router yok).

    *Beyan edilmiş ama okunmayan bir tercih, verilmemiş bir sözden kötüdür.*
    """
    tercihler = [{"category": "alert", "channel": "email", "enabled": False},
                 {"category": "report", "channel": "email", "enabled": True}]
    assert tercih_izin_veriyor_mu("alert", "email", tercihler) is False
    assert tercih_izin_veriyor_mu("report", "email", tercihler) is True


def test_TERCIH_KAYDI_YOKSA_varsayilan_ACIK():
    """⚠ Opt-out bir **karardır**; kaydın yokluğu bir karar değildir.

    Yokluğu *"kapalı"* saymak, hiç ayar yapmamış bir kullanıcıyı **sessize alırdı**.
    """
    assert tercih_izin_veriyor_mu("alert", "email", None) is True
    assert tercih_izin_veriyor_mu("alert", "email", []) is True


def test_SILINMIS_tercih_YOK_SAYILIR():
    """Soft-delete (ADR-0019): silinmiş bir tercih bir tercih değildir."""
    t = [{"category": "alert", "channel": "email", "enabled": False,
          "deleted_at": "2026-01-01"}]
    assert tercih_izin_veriyor_mu("alert", "email", t) is True


def test_SLACK_kanali_KAYITLI():
    """🔴 Desen hazırdı, kanal yoktu: `@register("slack")` grep'i **sıfırdı**."""
    from app import channels

    assert "slack" in channels._CHANNELS, (
        "🔴 Slack kanalı kayıtlı değil — bir kayıt mekanizması vardı, ona kayıtlı üç "
        "kanaldan biri yoktu.")


def test_SLACK_anahtarsizken_ATLANIR_patlamaz(monkeypatch):
    """⚠ Bir kanalın yapılandırılmamış olması, **ötekilerin teslimini durdurmamalı**."""
    from app import channels

    class _S:
        slack_webhook = ""

    monkeypatch.setattr(channels, "get_settings", lambda: _S())
    r = channels._CHANNELS["slack"](
        type("E", (), {"title": "t", "message": "m"})(), {}, None)
    assert r["ok"] is False and r["skipped"] is True


@pytest.mark.parametrize("onem", ["info", "warning"])
def test_bastirma_TUM_normal_onemlerde_calisir(onem):
    a = dedup_key("x", "1", "y")
    assert bastirilir_mi(a, onem, {a: 0.0}, 1.0) is True
