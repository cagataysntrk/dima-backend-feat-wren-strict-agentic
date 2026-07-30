"""TenantConfig → companies/<slug>/company.yml materializer'ı.

Mimari (onaylı tasarım): admin-api ile dima-api DİSK PAYLAŞMAZ; kaynak control-plane
DB'deki TenantConfig satırıdır. dima-api bu satırları company.yml dosyalarına yazar
(türetilmiş çıktı — wren-project gibi) ve AKTİF şirketinki değiştiyse yeniden
compose+build eder. Tetik: startup + 60 sn'lik scheduler döngüsü.

Config satırı olmayan tenant'a DOKUNULMAZ (repo'daki elle yazılmış company.yml
geçerli kalır); satır varsa DB kazanır.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

_HEADER = (
    "# BU DOSYA TÜRETİLMİŞTİR — kaynak: control-plane DB (tenant_config), admin panel.\n"
    "# Elle düzenleme bir sonraki materialize'da EZİLİR. (ADR-0005 + TenantConfig)\n"
)


def _render(slug: str, sektorler: list[str], moduller: list[str] | None,
            kaynaklar: list[str] | None = None,
            firma_no: int | None = None, donem_no: int | None = None,
            diller: list[str] | None = None) -> str:
    doc: dict = {"name": slug, "sektorler": sektorler}
    if moduller is not None:
        doc["moduller"] = moduller
    if diller:
        doc["diller"] = diller  # §7b aktif dil seti → routing synonyms_for(langs) okur
    if kaynaklar:
        doc["kaynaklar"] = kaynaklar
        # Önekli şemalarda (Logo) model bağlama kapsamı — compose bunu okumaz,
        # model üretimi/onboarding okur (ADR-0017 Karar 4).
        if firma_no is not None:
            doc["firma_no"] = firma_no
        if donem_no is not None:
            doc["donem_no"] = donem_no
    return _HEADER + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False)


def materialize_tenant_configs(settings, companies_dir: Path | None = None) -> list[str]:
    """DB'deki tüm TenantConfig'leri diske yazar; DEĞİŞEN slug listesini döner.
    Control-plane erişilemezse sessizce boş döner (demo kırılmaz)."""
    base = Path(companies_dir) if companies_dir else (
        settings.resolved_project_dir().parent / "companies"
    )
    changed: list[str] = []
    try:
        from sqlmodel import Session, select

        from control_plane.db import engine
        from control_plane.models import Tenant, TenantConfig

        with Session(engine) as s:
            rows = s.exec(select(TenantConfig, Tenant).where(
                TenantConfig.tenant_id == Tenant.id)).all()
    except Exception as exc:  # DB geçici hatası: döngüyü öldürme, GÖRÜNÜR bırak
        print(f"[materialize] control-plane okunamadı: {exc}", file=sys.stderr)
        return []

    for cfg, tenant in rows:
        try:
            sektorler = json.loads(cfg.sektorler_json) or []
            moduller = json.loads(cfg.moduller_json) if cfg.moduller_json else None
            kaynaklar = json.loads(cfg.kaynaklar_json) if cfg.kaynaklar_json else None
            diller = json.loads(cfg.diller_json) if cfg.diller_json else None
        except ValueError:
            continue
        content = _render(tenant.slug, sektorler, moduller, kaynaklar,
                          cfg.firma_no, cfg.donem_no, diller)
        path = base / tenant.slug / "company.yml"
        try:
            if path.exists() and path.read_text() == content:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            changed.append(tenant.slug)
        except OSError as exc:
            print(f"[materialize] {tenant.slug} yazılamadı: {exc}", file=sys.stderr)
            continue
    return changed


_last_overlay_sig: str | None = None


def _overlay_signature() -> str:
    """Onaylı sinonim overlay'lerinin imzası (ADR-0018 katman 3) — değişince schema
    cache tazelenir → yeni sinonim ~1 dk'da canlı, deploy'suz. DB hatası → sabit imza."""
    try:
        from sqlmodel import Session, select

        from control_plane.db import engine
        from control_plane.models import SynonymOverride

        with Session(engine) as s:
            rows = s.exec(select(SynonymOverride).where(
                SynonymOverride.approved == True)).all()  # noqa: E712
        return "|".join(sorted(f"{r.id}:{r.updated_at.isoformat()}" for r in rows))
    except Exception:
        return _last_overlay_sig or ""


def materialize_and_recompose(state, settings) -> list[str]:
    """Döngü/startup kancası: materialize + aktif şirket değiştiyse compose+build
    ve şema önbelleğini tazele (yeni cube seti anında görünür). Ayrıca sinonim
    overlay'i değiştiyse (ADR-0018) schema cache'i tazeler — compose gerekmez."""
    global _last_overlay_sig
    changed = materialize_tenant_configs(settings)
    registry = getattr(state, "company_registry", None)
    if registry is not None:
        for slug in changed:
            registry.invalidate(slug)  # sonraki istekte tazeden derlenir
    if settings.company in changed:
        from app.compose import compose_and_build

        compose_and_build(settings)
        wren = getattr(state, "wren", None)
        if wren is not None:
            wren.invalidate_schema_cache()

    # Overlay değişimi: compose'a gerek yok, yalnız schema cache'leri düşür.
    sig = _overlay_signature()
    if sig != _last_overlay_sig:
        _last_overlay_sig = sig
        wren = getattr(state, "wren", None)
        if wren is not None:
            wren.invalidate_schema_cache()
        if registry is not None:
            for svc in list(getattr(registry, "_services", {}).values()):
                svc.invalidate_schema_cache()
    return changed
