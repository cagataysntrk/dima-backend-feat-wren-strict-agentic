"""Birleşik kanal mimarisi birim testleri — NotificationEvent + dispatch + resolve_targets
+ Resend e-posta kanalı + inapp log gömme. Gerçek HTTP yok: ``_send_email`` monkeypatch;
key ayarlarla enjekte. MJML render ayrı test edilir (test_email_render)."""

from types import SimpleNamespace

from app import channels
from app.channels import DispatchContext, NotificationEvent, dispatch, resolve_targets


def _event(category: str = "report") -> NotificationEvent:
    return NotificationEvent(category=category, severity="info", title="Rapor",
                             summary="özet", rows=[{"a": 1}], row_count=1)


def _with_key(monkeypatch, key: str = "re_test") -> None:
    monkeypatch.setattr(channels, "get_settings",
                        lambda: SimpleNamespace(resend_api_key=key, resend_from="dima <x@y.z>"))


# -- resolve_targets (saf) ------------------------------------------------

def test_resolve_default_is_inapp_only():
    assert resolve_targets("report") == [{"channel": "inapp"}]


def test_resolve_inapp_is_last():
    # Dış kanal ÖNCE, inapp EN SON (sonuçlar log kaydına gömülsün).
    t = resolve_targets("alert", schedule_delivery={"email": {"to": ["a@x.com"]}})
    assert t[0]["channel"] == "email" and t[-1]["channel"] == "inapp"


def test_resolve_merges_prefs_and_dedups():
    t = resolve_targets("alert",
                        schedule_delivery={"email": {"to": ["a@x.com"]}},
                        prefs=[{"channel": "email", "enabled": True, "address": "a@x.com"},
                               {"channel": "email", "enabled": True, "address": "b@y.com"}])
    emails = [x for x in t if x["channel"] == "email"]
    # a@x.com iki kez gelmemeli (schedule + pref aynı adres); b@y.com ayrı.
    to_sets = sorted(tuple(e["to"]) for e in emails)
    assert to_sets == [("a@x.com",), ("b@y.com",)]


def test_resolve_disabled_pref_skipped():
    t = resolve_targets("report", prefs=[{"channel": "email", "enabled": False, "address": "a@x.com"}])
    assert [x["channel"] for x in t] == ["inapp"]


# -- dispatch + inapp log gömme -------------------------------------------

def test_dispatch_inapp_records_and_embeds_email(monkeypatch):
    _with_key(monkeypatch)
    monkeypatch.setattr(channels, "_send_email", lambda to, s, h, t: {"id": "em_1"})
    # _email_channel render_email'i app.email_render'dan çağrı-anında import eder → orada patch.
    monkeypatch.setattr("app.email_render.render_email", lambda e: ("s", "<p>h</p>", "t"))

    saved = {}

    def sink(rec):
        saved.update(rec)
        rec = dict(rec)
        rec["id"] = "n-1"
        return rec

    targets = resolve_targets("report", schedule_delivery={"email": {"to": ["a@x.com"]}})
    out = dispatch(_event(), targets, DispatchContext(inapp_sink=sink))
    # email teslim edildi + inapp kaydına gömüldü (log)
    email = next(s for s in out if s["channel"] == "email")
    assert email["ok"] is True and email["provider_id"] == "em_1"
    assert "delivery" in saved and saved["delivery"][0]["channel"] == "email"


def test_dispatch_unknown_channel_isolated():
    out = dispatch(_event(), [{"channel": "telegram"}])
    assert out[0] == {"channel": "telegram", "ok": False, "detail": "bilinmeyen kanal"}


def test_email_skipped_without_key(monkeypatch):
    _with_key(monkeypatch, "")
    out = dispatch(_event(), [{"channel": "email", "to": ["a@x.com"]}])
    assert out[0]["skipped"] is True and "key" in out[0]["detail"]


def test_email_skipped_without_recipients(monkeypatch):
    _with_key(monkeypatch)
    out = dispatch(_event(), [{"channel": "email", "to": []}])
    assert out[0]["skipped"] is True and "alıcı" in out[0]["detail"]


def test_channel_error_isolated(monkeypatch):
    _with_key(monkeypatch)

    def boom(e):
        raise RuntimeError("mjml bozuk")

    monkeypatch.setattr("app.email_render.render_email", boom)
    out = dispatch(_event(), [{"channel": "email", "to": ["a@x.com"]}])
    assert out[0]["ok"] is False and "mjml bozuk" in out[0]["detail"]


def test_inapp_without_sink_skips():
    out = dispatch(_event(), [{"channel": "inapp"}])
    assert out[0] == {"channel": "inapp", "ok": False, "detail": "sink yok"}
