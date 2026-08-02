"""E-posta gövdesi render DİKİŞİ (ADR-0011) — ``render_email(event)`` tek soyutlama.

Bugün: Jinja2 (veri → MJML markup) + mrml (MJML → email-safe HTML; Rust, Node yok).
Yarın: UI ekibi React Email'de tasarlar → HTML export → burada Jinja2 ile jinja-fy
edilir; ``channels``/``dispatch``/tercih katmanları DEĞİŞMEZ (geçiş = bu dosya).

MJML e-posta HTML endüstri standardı: responsive + Outlook/Gmail/Apple Mail tutarlı.
Görsel tavan client CSS kısıtıyla belirlenir (MJML seçimiyle değil). Deterministik:
ham veri LLM'e gitmez, sadece Python string işleme.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from app.channels import NotificationEvent

_DIR = Path(__file__).parent / "email"


@lru_cache
def _env():
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    return Environment(
        loader=FileSystemLoader(str(_DIR)),
        autoescape=select_autoescape(default=True),  # {{ }} HTML-escape (injection guard)
        trim_blocks=True,
        lstrip_blocks=True,
    )


# Kategori → gövde şablonu. alarm/anomaly aynı callout şablonunu paylaşır (aksan farkı).
_TEMPLATES = {
    "report": "report.mjml.j2",
    "alert": "alarm.mjml.j2",
    "anomaly": "alarm.mjml.j2",
    "system": "report.mjml.j2",
}

# Önem → aksan rengi (callout + başlık).
_ACCENT = {"critical": "#b91c1c", "warning": "#b45309", "info": "#0f766e"}


def render_email(event: NotificationEvent) -> tuple[str, str, str]:
    """(subject, html, text) döner. html = MJML→email-safe; text = düz metin fallback."""
    import mrml

    cols = list(event.rows[0].keys()) if event.rows else []
    template = _TEMPLATES.get(event.category, "report.mjml.j2")
    accent = _ACCENT.get(event.severity, _ACCENT["info"])
    # VİZ (ADR-0024 cross-surface): backend grafik kararı → email-safe HTML/CSS grafik (JS yok).
    # Üretilemez/uygun değilse None → template yalnız tabloyu gösterir (dürüst fallback).
    from app import viz_email

    try:
        chart_html = viz_email.render_chart_html(event.viz, event.rows, accent=accent)
    except Exception:
        chart_html = None
    mjml_src = _env().get_template(template).render(
        e=event,
        cols=cols,
        rows=event.rows[:20],
        more=max(0, len(event.rows) - 20),
        accent=accent,
        chart_html=chart_html,
    )
    html = mrml.to_html(mjml_src).content

    subject = f"[dima] {event.title}: {event.summary.split(' — ')[0]}"
    text_lines = [event.title, "", event.summary]
    if event.violations:
        text_lines += ["", *[f"• {v}" for v in event.violations[:10]]]
    # Düz metin yedeği HTML ile AYNI bilgiyi taşımalı: "Neden?" yalnız zengin istemcide
    # görünseydi, e-postayı metin okuyan kullanıcı gerekçesiz bir uyarı alırdı.
    if event.neden or event.neden_not:
        text_lines += ["", "Neden?", *[f"↳ {n}" for n in event.neden]]
        if event.neden_not:
            text_lines.append(event.neden_not)
    text = "\n".join(text_lines)
    return subject, html, text
