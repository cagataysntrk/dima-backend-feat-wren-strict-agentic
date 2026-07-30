"""E-posta render dikişi (Jinja2 + mrml) — deterministik, ağ yok. Şablon KAYNAĞI
değişse de (MJML→React-export) bu sözleşme sabit kalmalı: (subject, html, text)."""

from app.channels import NotificationEvent
from app.email_render import render_email


def test_report_renders_table_and_escapes():
    ev = NotificationEvent(category="report", severity="info", title="Haftalık Ciro",
                           summary="rapor hazır", rows=[{"sehir": "İstanbul", "ciro": 8200}],
                           row_count=1)
    subject, html, _ = render_email(ev)
    assert subject.startswith("[dima]") and "Haftalık Ciro" in subject
    assert "İstanbul" in html and "8200" in html   # veri tabloya girdi
    assert "<!doctype html>" in html.lower()        # mrml email-safe HTML üretti


def test_alarm_shows_violations_and_accent():
    ev = NotificationEvent(category="anomaly", severity="warning", title="Enerji",
                           summary="olağandışı — m3: 512", violations=["m3: 512 (z=+2.8)"],
                           rows=[{"m": "m3", "kwh": 512}])
    _, html, text = render_email(ev)
    assert "m3: 512 (z=+2.8)" in html               # ihlal listelendi
    assert "#b45309" in html                          # warning aksan rengi
    assert "m3: 512" in text                          # düz metin fallback


def test_html_escapes_injection():
    ev = NotificationEvent(category="report", severity="info", title="<script>x</script>",
                           summary="ok", rows=[{"c": "<b>bad</b>"}])
    _, html, _ = render_email(ev)
    assert "<script>x</script>" not in html           # başlık escape edildi
    assert "&lt;b&gt;bad" in html                      # hücre escape edildi
