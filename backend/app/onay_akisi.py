"""FAZ 6.1 — **ONAY AKIŞI: tek modül, beş tüketici.** [bayrak: `onay_akisi`]

> **Karar kaydı: `ADR-0031` komşusu** — MCP yüzeyi ile **aynı şekli** paylaşır.

## 🔴 "ONAY BİR BUTON DEĞİLDİR"

EU AI Act + NIST AI RMF **gösterilebilir, ölçülebilir** insan gözetimi istiyor. Bir onay
akışı üç şeyi taşımak zorunda:

1. **Onay kapsamı bir NESNEDİR** — hangi araç, hangi argümanlar, hangi kaynak.
   *"Evet"in sınırı yazılı olmalı*; sınırsız bir *"evet"*, onay değil bir **imzadır**.
2. **Riske göre yönlendirme** — `geri_alinamaz` → **senkron** istem; `orta` → **kuyruk**.
3. **SÜRE AŞIMI** — varsayılan **30 dk**. Süresi geçmiş bir onayla çalıştırma
   **reddedilir**: *dün verilmiş bir "evet", bugünün dünyasına verilmemiştir.*

## 🔴 DÖRDÜNCÜ PARÇA — D9: *"her yazmaya onay"* ÖLÇÜLMÜŞ BİR HATADIR

Anthropic telemetrisi: kullanıcılar izin isteklerinin **~%93'ünü onaylıyor**; *"bir
kullanıcı ne kadar çok onay görürse her birine o kadar az dikkat eder."* **Onay
yorgunluğu ölçülmüş bir olgudur** ve OS düzeyi izolasyon istemleri **%84 azaltmış**.

> Tasarım kuralı: ***izolasyon gücünü kullanıcının gözetim kapasitesine göre ayarla.***
> Teknik olmayan kullanıcı **daha çok diyalog** değil, **daha sert sınır** ister.

Bu yüzden **varsayılan SINIR, istem değil** (FAZ 6.0 · `eylem.d9_istemsiz_mi`) ve bu
modül yalnız **istem gereken** hâli yönetir.

## ⚠ MCP hizalaması `[DOĞRULANMADI]`

`OnayTalebi`'nin şekli MCP `elicitation`'a hizalanır — aynı şekil MCP yüzeyini
**bedavaya** onay-yetenekli yapar. **Ama spec sürümü çelişkili**: bir kaynak *"Linux
Foundation · 2026-07-28"*, öteki *"Agentic AI Foundation · 2025-11-25"* diyor. Sürüm
**doğrulanmadan** hizalama bir **iddia** olarak kalır ve `MCP_HIZALAMA` sabiti bunu
taşır. *Doğrulanmamış bir uyumluluk beyanı, uyumsuzluktan kötüdür.*

🔴 Spec'in normatif kuralına **uyuluyor**: *"form modu parola/API anahtarı/token/ödeme
bilgisi istemekte kullanılmamalıdır"* — `YASAK_ARGUMAN` bunu kapıya çeviriyor.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

# --- DURUM MAKİNESİ ---------------------------------------------------------------
TASLAK = "taslak"
ONAY_BEKLIYOR = "onay_bekliyor"
ONAYLANDI = "onaylandi"
REDDEDILDI = "reddedildi"
GERI_ALINDI = "geri_alindi"

DURUMLAR = (TASLAK, ONAY_BEKLIYOR, ONAYLANDI, REDDEDILDI, GERI_ALINDI)

#: 🔴 İzinli geçişler. **Kapalı bir makine**: listede olmayan her geçiş **reddedilir**.
#: *Serbest bir durum alanı, bir durum makinesi değil bir dilektir.*
GECISLER: dict[str, tuple[str, ...]] = {
    TASLAK: (ONAY_BEKLIYOR,),
    ONAY_BEKLIYOR: (ONAYLANDI, REDDEDILDI),
    # ⚠ Onaylanmış bir iş **geri alınabilir** ama reddedilmiş bir iş **geri alınamaz**:
    # yapılmamış bir şeyi geri almak, olmayan bir olayı kayda geçirmektir.
    ONAYLANDI: (GERI_ALINDI,),
    REDDEDILDI: (),
    GERI_ALINDI: (),
}

# --- RİSK -------------------------------------------------------------------------
RISK_DUSUK = "dusuk"
RISK_ORTA = "orta"
RISK_GERI_ALINAMAZ = "geri_alinamaz"

#: Varsayılan ömür — **30 dk**. ⚠ Sonsuz bir onay **yoktur**: *dün verilmiş bir "evet",
#: bugünün dünyasına verilmemiştir.*
VARSAYILAN_OMUR_SN = 30 * 60

#: 🔴 MCP spec'inin normatif yasağı: form modu **parola/API anahtarı/token/ödeme
#: bilgisi** istemekte kullanılmamalıdır. Bir onay talebi bunları **taşıyamaz**.
YASAK_ARGUMAN = ("password", "parola", "sifre", "api_key", "apikey", "token",
                 "secret", "gizli", "card", "kart", "iban", "cvv", "pin")

#: ⚠ MCP hizalaması **`[DOĞRULANMADI]`** — spec sürümü çelişkili (bkz. modül docstring).
#: *Doğrulanmamış bir uyumluluk beyanı, uyumsuzluktan kötüdür.*
MCP_HIZALAMA = "[DOĞRULANMADI] elicitation şekli — spec sürümü çelişkili"


class OnayHatasi(ValueError):
    """Onay akışı **fail-closed** reddetti."""


@dataclass
class OnayTalebi:
    """Onay kapsamı **bir nesnedir** — *"evet"*in sınırı yazılı.

    ⚠ `geri_alma_fonksiyonu_ref` bir **metin referanstır**, çağrılabilir değil: bir
    çağrılabiliri kayda koymak onu serileştirilemez ve **denetlenemez** yapardı.
    """

    arac: str
    argumanlar: dict[str, Any]
    kaynak: str                                  # kim/ne istedi (ör. "kullanici", "ajan")
    risk: str = RISK_ORTA
    son_gecerlilik: datetime | None = None
    geri_alma_fonksiyonu_ref: str | None = None
    id: str = field(default_factory=lambda: "o-" + uuid.uuid4().hex[:10])
    durum: str = TASLAK

    def sozluk(self) -> dict[str, Any]:
        return {
            "id": self.id, "arac": self.arac, "argumanlar": self.argumanlar,
            "kaynak": self.kaynak, "risk": self.risk, "durum": self.durum,
            "son_gecerlilik": (self.son_gecerlilik.isoformat()
                               if self.son_gecerlilik else None),
            "geri_alma_fonksiyonu_ref": self.geri_alma_fonksiyonu_ref,
            "mcp_hizalama": MCP_HIZALAMA,
        }


def _simdi() -> datetime:
    return datetime.now(timezone.utc)


def olustur(arac: str, argumanlar: dict[str, Any], *, kaynak: str,
            risk: str = RISK_ORTA, omur_sn: int | None = None,
            geri_alma_ref: str | None = None, simdi: datetime | None = None) -> OnayTalebi:
    """Talep üretir ve **kapsamını doğrular**. İhlalde `OnayHatasi`.

    🔴 **Yasak argüman taşıyan bir talep ÜRETİLMEZ.** Spec'in normatif kuralı bu; ama
    asıl sebep daha basit: bir onay kartında görünen parola, **ekran görüntüsüne** ve
    **audit satırına** girer.
    """
    if risk not in (RISK_DUSUK, RISK_ORTA, RISK_GERI_ALINAMAZ):
        raise OnayHatasi(f"bilinmeyen risk: {risk!r}")
    for k in argumanlar or {}:
        if str(k).lower() in YASAK_ARGUMAN:
            raise OnayHatasi(
                f"`{k}` bir onay talebinde TAŞINAMAZ (MCP normatif yasağı): bir onay "
                f"kartında görünen sır, ekran görüntüsüne ve audit satırına girer.")
    t = _simdi() if simdi is None else simdi
    return OnayTalebi(arac=arac, argumanlar=dict(argumanlar or {}), kaynak=kaynak,
                      risk=risk,
                      son_gecerlilik=t + timedelta(seconds=omur_sn or VARSAYILAN_OMUR_SN),
                      geri_alma_fonksiyonu_ref=geri_alma_ref)


def senkron_mu(risk: str) -> bool:
    """**Riske göre yönlendirme**: `geri_alinamaz` → senkron; `orta` → kuyruk.

    ⚠ `dusuk` buraya **hiç gelmemeli** (FAZ 6.0'ın D9 dalı onu istemsiz koşturur); ama
    gelirse **kuyruğa** düşer — bir düşük riskli işi senkron istem yapmak, tam da
    ölçülmüş yorgunluğu üretir.
    """
    return risk == RISK_GERI_ALINAMAZ


def gecis(talep: OnayTalebi, yeni: str) -> OnayTalebi:
    """Durum geçişi — **kapalı makine**. İzinsiz geçişte `OnayHatasi`."""
    if yeni not in DURUMLAR:
        raise OnayHatasi(f"bilinmeyen durum: {yeni!r}")
    izinli = GECISLER.get(talep.durum, ())
    if yeni not in izinli:
        raise OnayHatasi(
            f"`{talep.durum}` → `{yeni}` geçişi YOK. İzinli: {izinli or '(son durum)'}. "
            f"Serbest bir durum alanı, bir durum makinesi değil bir dilektir.")
    talep.durum = yeni
    return talep


def suresi_gecti_mi(talep: OnayTalebi, simdi: datetime | None = None) -> bool:
    """*Dün verilmiş bir "evet", bugünün dünyasına verilmemiştir.*"""
    if talep.son_gecerlilik is None:
        return False
    return (simdi or _simdi()) > talep.son_gecerlilik


def calistirilabilir_mi(talep: OnayTalebi, simdi: datetime | None = None) -> None:
    """Çalıştırma **ön koşulu**. Karşılanmazsa `OnayHatasi` — sessiz `False` **değil**.

    🔴 Bir çalıştırma reddi **sebebiyle birlikte** gelmeli: *"onay geçersiz"* diyen bir
    `False`, kullanıcıya neyi düzelteceğini söylemez.
    """
    if talep.durum != ONAYLANDI:
        raise OnayHatasi(f"talep `{talep.durum}` durumunda — yalnız `{ONAYLANDI}` çalışır.")
    if suresi_gecti_mi(talep, simdi):
        raise OnayHatasi(
            "onayın süresi doldu — dün verilmiş bir «evet», bugünün dünyasına "
            "verilmemiştir. Yeniden onaylayın.")


# --- TELEMETRİ: ONAY YORGUNLUĞU ----------------------------------------------------

def istem_orani(tur_sayisi: int, istem_sayisi: int) -> dict[str, Any]:
    """🔴 **İstem sayısı / tur** — *artarsa KIRMIZI*.

    Anthropic telemetrisi kullanıcıların izin isteklerinin **~%93'ünü** onayladığını
    ölçtü: *"ne kadar çok onay görürse her birine o kadar az dikkat eder."* Bu oran o
    yorgunluğun **göstergesidir** ve bir hedef değil bir **alarmdır**.

    ⚠ `tur_sayisi == 0` → `None`. *Hiç tur yokken "%0 istem" demek, çalışmayan bir
    sistemi başarılı göstermek olurdu.*
    """
    if tur_sayisi <= 0:
        return {"oran": None, "not": "⊘ ÖLÇÜLEMEDİ — hiç tur yok"}
    oran = istem_sayisi / tur_sayisi
    return {"oran": round(oran, 4), "tur": tur_sayisi, "istem": istem_sayisi,
            "not": ("⚠ Onay yorgunluğu göstergesi: bu oran ARTARSA kullanıcı her isteme "
                    "daha az dikkat eder (~%93 otomatik onay ölçüldü).")}

# ── ONAY BİLETİ: §C ölçüt 6'nın "süre aşımı 30 dk" şartı ─────────────────────────────
#
# 🔴 **Ölçülen boşluk (2026-08-05, OKUNARAK bulundu).** §C ölçüt 6 *"onaysız yazma
# imkânsız + onay başına audit satırı + **süre aşımı 30 dk**"* diyor ve ölçüt raporda
# 🟢 işaretliydi. Canlı onay yolu (`app/routers/eylem.py::eylem_onayla`) okundu:
# **hiçbir süre kontrolü yok** — üç saat önceki bir öneri onaylanıp koşabilirdi.
# `VARSAYILAN_OMUR_SN = 30 * 60` yalnız **bu modülde** duruyordu ve modülün **hiçbir
# üretim tüketicisi yoktu** (denetimin *"12 yetim modül"* bulgusunun ikinci kalemi).
#
# ⚠ **Neden istemciden gelen bir zaman damgası YETMEZ:** istemci her seferinde *"şimdi"*
# gönderebilir ve süre kontrolü bir **törene** dönüşür. Bilet bu yüzden **imzalıdır**.
#
# ⚠ **Neden ikinci bir secret üretilmiyor:** `paylasim.py`'nin kendi gerekçesi burada da
# geçerli — rotasyonu, saklanması ve sızma davranışı olan **bir** anahtar vardır.
# *İki anahtar, iki kez yanlış yönetilir.*

import base64
import hashlib
import hmac
import json as _json
import time as _time


def _gizli() -> bytes:
    from control_plane.config import get_auth_settings

    s = str(getattr(get_auth_settings(), "jwt_secret", "") or "")
    if not s:
        raise OnayHatasi(
            "Onay bileti için `jwt_secret` gerekli. Anahtarsız bir imza, imza değildir.")
    return s.encode("utf-8")


def _b64(ham: bytes) -> str:
    return base64.urlsafe_b64encode(ham).decode("ascii").rstrip("=")


def _b64_coz(m: str) -> bytes:
    return base64.urlsafe_b64decode(m + "=" * (-len(m) % 4))


def bilet(eylem: str, *, omur: int | None = None, simdi: float | None = None) -> str:
    """Bir eylem önerisi için **imzalı ve süreli** onay bileti.

    ⚠ Yük **yalnız eylem adı + son kullanma**: argümanlar biletin içine konmaz. Konsaydı
    bilet, argümanları da **doğrulanmış** gösterirdi — oysa `eylem_onayla` onları zaten
    kendi kapılarından geçiriyor ve iki doğrulama, ikisi de eksik olurdu.
    """
    govde = {"e": eylem,
             "exp": int((simdi if simdi is not None else _time.time())
                        + int(omur or VARSAYILAN_OMUR_SN))}
    ham = _json.dumps(govde, ensure_ascii=False, separators=(",", ":"),
                      sort_keys=True).encode("utf-8")
    return f"{_b64(ham)}.{_b64(hmac.new(_gizli(), ham, hashlib.sha256).digest())}"


def bilet_dogrula(token: str, eylem: str, *, simdi: float | None = None) -> None:
    """Bilet geçerli mi — **fail-closed**, geçersizse `OnayHatasi`.

    🔴 İmza **sabit-zamanlı** karşılaştırılır: normal `==`, bileti bayt bayt tahmin
    etmeye açık bir zamanlama kanalı bırakırdı.
    🔴 Eylem adı **biletin içinde** doğrulanır: bir *"tercih kaydet"* bileti bir
    *"zamanla"* onayına iliştirilebilseydi, süre kapısı **yanlış eylemi** korurdu.
    """
    try:
        g_b64, i_b64 = str(token or "").split(".", 1)
        ham, imza = _b64_coz(g_b64), _b64_coz(i_b64)
    except Exception as exc:                                  # noqa: BLE001
        raise OnayHatasi("Onay bileti bozuk.") from exc
    if not hmac.compare_digest(hmac.new(_gizli(), ham, hashlib.sha256).digest(), imza):
        raise OnayHatasi("Onay bileti doğrulanamadı (imza uyuşmuyor).")
    try:
        govde = _json.loads(ham.decode("utf-8"))
    except Exception as exc:                                  # noqa: BLE001
        raise OnayHatasi("Onay bileti okunamadı.") from exc
    if govde.get("e") != eylem:
        raise OnayHatasi("Onay bileti BAŞKA bir eylem için verilmiş.")
    if float(govde.get("exp") or 0) < (simdi if simdi is not None else _time.time()):
        raise OnayHatasi(
            f"Onay süresi doldu ({VARSAYILAN_OMUR_SN // 60} dk). Öneriyi yeniden alın — "
            f"aradan geçen sürede veri ya da yetki değişmiş olabilir.")
