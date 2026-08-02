"""Bildirim teslimi — BİRLEŞİK kanal mimarisi (ADR-0011).

Her teslim hedefi bir KANAL: ``inapp`` (bell), ``email`` (MJML+Resend), ileride
``push``/``slack``/``webhook``. Tek anlamsal ``NotificationEvent`` → ``dispatch()`` →
çözülen kanallara fan-out. In-app ARTIK ÖZEL DEĞİL — registry'de bir kanal (varsayılan
hep açık). Yeni kanal = registry'ye bir handler; ``dispatch``'e dokunma yok. Kanal
hatası izole (koşumu ve diğer kanalları kırmaz).

İki tercih KATMANI (dispatcher birler):
  * kullanıcı tercihi (self)      → NotificationPreference (kategori × kanal matrisi)
  * schedule.delivery (recipient) → rapor dağıtım listesi (bu kişilere gitsin)

Şablon KAYNAĞI ``render_email`` dikişinin arkasında (bugün MJML; yarın React-Email
export-HTML olabilir) — bu katman şablonun ne olduğunu bilmez. Ürün maili BACKEND'de
yönetilir; frontend'deki Resend yalnız pazarlama iletişim formu (ayrı yol).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from app.config import get_settings
from app.logging_setup import get_logger

_log = get_logger("channels")

# Bildirim kategorileri — kullanıcı tercih matrisinin satır ekseni.
CATEGORIES = ("report", "alert", "anomaly", "system")


@dataclass
class NotificationEvent:
    """Kanaldan BAĞIMSIZ anlamsal bildirim — her kanal kendi biçimine render eder."""

    category: str                                    # report | alert | anomaly | system
    severity: str                                    # info | warning | critical
    title: str                                       # kısa başlık (label)
    summary: str                                     # tek cümle özet (mesaj)
    rows: list[dict] = field(default_factory=list)   # veri tablosu (email gövdesi)
    viz: dict | None = None                          # VizSpec (ADR-0024) — email grafik kararı
    violations: list[str] = field(default_factory=list)  # eşik/anomali ihlalleri
    # NEDEN (Faz F3): ihlali sürükleyen segmentler — `violations` NE olduğunu, bu NİYE
    # olduğunu söyler. Etiketler PII-maskelidir (bildirimin kime ulaşacağı önceden
    # bilinemez) ve tıklanabilir `cube_query` TAŞIMAZ (maskeli değere filtre boş döner).
    neden: list[str] = field(default_factory=list)
    neden_not: str | None = None                     # kırpma/tarama sınırı ya da dürüst red
    contract_id: str | None = None
    schedule_id: str | None = None
    tenant_id: str | None = None
    period: str | None = None
    row_count: int | None = None
    extra: dict = field(default_factory=dict)        # kanal-özel / cube_query / manual


@dataclass
class DispatchContext:
    """Kanalların ihtiyaç duyduğu dış bağımlılıklar (DI) — channels.py DB/store'a
    doğrudan bağlanmasın diye enjekte edilir (döngüsel import + test kolaylığı)."""

    inapp_sink: Callable[[dict], dict] | None = None  # notification_log DB yazıcısı
    siblings: list[dict] | None = None                # bu kanaldan ÖNCE teslim edilenlerin
    #                                                   durumları (inapp log kaydına gömülür)


# Kanal registry: ad → handler(event, target, ctx) -> durum dict'i.
_CHANNELS: dict[str, Callable[[NotificationEvent, dict, DispatchContext], dict]] = {}


def register(name: str) -> Callable:
    def deco(fn: Callable) -> Callable:
        _CHANNELS[name] = fn
        return fn
    return deco


def dispatch(event: NotificationEvent, targets: list[dict],
             ctx: DispatchContext | None = None) -> list[dict]:
    """event'i çözülmüş kanallara fan-out eder. ``targets``: ``[{"channel":..., ...cfg}]``.
    Kanal başına durum listesi döner. Bir kanal patlarsa İZOLE (diğerleri devam eder)."""
    ctx = ctx or DispatchContext()
    out: list[dict] = []
    for target in targets:
        name = target.get("channel")
        handler = _CHANNELS.get(name)
        if handler is None:
            out.append({"channel": name, "ok": False, "detail": "bilinmeyen kanal"})
            continue
        ctx.siblings = out  # önce teslim edilenler → inapp log kaydına gömülebilsin
        try:
            out.append(handler(event, target, ctx))
        except Exception as exc:  # noqa: BLE001 — kanal hatası koşumu kırmasın
            _log.warning("kanal teslimi başarısız: %s", name, exc_info=True)
            out.append({"channel": name, "ok": False, "detail": str(exc)})
    return out


def resolve_targets(category: str, *, schedule_delivery: dict | None = None,
                    prefs: list[dict] | None = None, user_email: str | None = None) -> list[dict]:
    """SAF fonksiyon (DB yok, test kolay): kategori için teslim hedeflerini üretir.

    Katmanlar birleştirilir: (1) schedule.delivery = rapor dağıtım listesi (recipient),
    (2) kullanıcı tercihi (self) = enabled kanallar + adres, (3) inapp EN SON [Faz-1
    varsayılan hep açık; Faz-2'de tercihle kapatılabilir] — dış kanallar ÖNCE teslim
    edilsin ki sonuçları inapp log kaydına gömülsün. (kanal, adres) çiftine göre tekil."""
    targets: list[dict] = []

    if schedule_delivery:
        for ch, cfg in schedule_delivery.items():
            cfg = cfg or {}
            if ch == "email":
                to = [str(x).strip() for x in (cfg.get("to") or []) if str(x).strip()]
                if to:
                    targets.append({"channel": "email", "to": to})
            else:
                targets.append({"channel": ch, **cfg})

    for pref in prefs or []:
        if not pref.get("enabled", True) or pref.get("channel") == "inapp":
            continue
        ch = pref.get("channel")
        addr = pref.get("address") or (user_email if ch == "email" else None)
        if ch == "email" and addr:
            targets.append({"channel": "email", "to": [addr]})
        elif ch == "push" and addr:
            targets.append({"channel": "push", "token": addr})

    targets.append({"channel": "inapp"})  # EN SON: dış teslim sonuçları log kaydına girsin

    # Tekilleştir: aynı kanal + aynı hedef iki kez teslim etmesin.
    seen: set = set()
    uniq: list[dict] = []
    for t in targets:
        key = (t.get("channel"), tuple(sorted(t.get("to", []))) or t.get("token"))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(t)
    return uniq


# -- inapp (bell) ---------------------------------------------------------

@register("inapp")
def _inapp_channel(event: NotificationEvent, target: dict, ctx: DispatchContext) -> dict:
    """In-app bell — notification_log DB'ye yazar (sink DI ile enjekte). Bu kanal da
    registry'de: 'her şey kanal' ilkesi. Sink yoksa (test/DB-down) zarifçe atlar."""
    if ctx.inapp_sink is None:
        return {"channel": "inapp", "ok": False, "detail": "sink yok"}
    payload = {
        "schedule_id": event.schedule_id,
        "tenant_id": event.tenant_id,
        "label": event.title,
        "kind": event.category,
        "message": event.summary,
        "contract_id": event.contract_id,
        "row_count": event.row_count,
        "neden": event.neden or None,
        "neden_not": event.neden_not,
        "cube_query": event.extra.get("cube_query"),
        "manual": event.extra.get("manual", False),
    }
    # Dış kanal teslim sonuçlarını (email vb.) AYNI kalıcı kayda göm → her gönderim loglanır.
    delivered = [s for s in (ctx.siblings or []) if s.get("channel") != "inapp"]
    if delivered:
        payload["delivery"] = delivered
    rec = ctx.inapp_sink(payload)
    return {"channel": "inapp", "ok": True, "notification_id": rec.get("id"), "record": rec}


# -- email (MJML + Resend) ------------------------------------------------

def _send_email(to: list[str], subject: str, html: str, text: str) -> dict:
    """Resend REST API ile e-posta yollar. Ayrı fonksiyon → testler monkeypatch'ler.
    Key/alıcı eksikse ÇAĞRILMAZ (kanal handler eler)."""
    import httpx

    s = get_settings()
    resp = httpx.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {s.resend_api_key}"},
        json={"from": s.resend_from, "to": to, "subject": subject, "html": html, "text": text},
        timeout=15.0,
    )
    resp.raise_for_status()
    return {"id": resp.json().get("id")}


@register("email")
def _email_channel(event: NotificationEvent, target: dict, ctx: DispatchContext) -> dict:
    to = [str(x).strip() for x in (target.get("to") or []) if str(x).strip()]
    if not get_settings().resend_api_key:
        return {"channel": "email", "ok": False, "skipped": True, "detail": "resend key yok"}
    if not to:
        return {"channel": "email", "ok": False, "skipped": True, "detail": "alıcı yok"}
    from app.email_render import render_email  # dikiş: bugün MJML, yarın React-export

    subject, html, text = render_email(event)
    res = _send_email(to, subject, html, text)
    return {"channel": "email", "ok": True, "to": to, "provider_id": res.get("id")}
