"""Özellik bayrakları (feature flags) — katmanlı çözümleme (ADR-0009).

Değerler: "off" | "alpha" | "beta" | "prod".

İKİ katman:
1. FABRİKA AYARI (kod/YAML): sektör pack.yml → şirket company.yml (şirket kazanır).
   Yeni sektör paketi varsayılanlarını böyle getirir.
2. İŞLETME GERÇEĞİ (DB, admin panelden): FeatureOverride satırları — çözüm kuralı
   EN SPESİFİK KAZANIR: user > role > tenant > sector > global > fabrika ayarı.
   Tanımsız kapsam bir üstünü MİRAS alır; spesifik "off" = kill switch.

NOT: Bayrak = rollout/görünürlük. YETKİ değildir — aksiyon güvenliği her zaman
authorize() matrisinden geçer (permissions); bayrak onu gevşetemez.
"""

from __future__ import annotations

from pathlib import Path

import yaml

STAGES = ("off", "alpha", "beta", "prod")
SCOPE_TYPES = ("global", "sector", "tenant", "role", "user")
# Spesifiklik sırası (soldan sağa artar) — sağdaki tanım soldakini ezer.
_SCOPE_ORDER = ("global", "sector", "tenant", "role", "user")

# ── KANONİK KAYIT (registry) ─────────────────────────────────────────────────
# Platform bayraklarının TEK metadata kaynağı: insan-okur etiket + açıklama +
# kategori. VARSAYILAN AŞAMA burada DEĞİL — o YAML'da (demo/packs/features.yml)
# durur; böylece ops aşamayı git'ten yönetir, kod değişmez. Admin panel bu
# metadata'yı okunabilir etiket/açıklama olarak gösterir (ham snake_case yerine).
#
# YENİ HAM ÖZELLİĞİ FLAG ARKASINA ALMA REÇETESİ (ADR-0009):
#   1) Buraya bir satır ekle (etiket/açıklama/kategori).
#   2) demo/packs/features.yml'e varsayılan aşamayı yaz (genelde `beta` — böylece
#      herkese kapalı, admin panelden seçili müşteriye açılır).
#   3) Tüketen yüzeyi `useFeature("<key>")` ile geçitle (frontend).
#   4) Gerekiyorsa admin panelden tenant/rol/kullanıcı override'ı ile aç.
FLAG_REGISTRY: dict[str, dict[str, str]] = {
    "cikti_yorumlama": {
        "label": "Çıktı yorumu",
        "description": "Her tablo/grafik/rapor/KPI için deterministik doğal-dil "
                       "yorumu (OutputInsight, ADR-0022).",
        "category": "Analiz",
    },
    "sql_display": {
        "label": "SQL'i göster",
        "description": "Üretilen SQL sorgusunu kullanıcıya açar (rapor altında "
                       "'+ sql göster').",
        "category": "Şeffaflık",
    },
    "verify_button": {
        "label": "Doğrula (✓/✗)",
        "description": "Raporu doğru/yanlış işaretleme — VQR öğrenmesini besler "
                       "(aynı soru sonra LLM'siz cevaplanır).",
        "category": "Öğrenme",
    },
    "scheduled_reports": {
        "label": "Zamanlanmış raporlar",
        "description": "Raporu belirli aralıkla otomatik koşup bildirim üretir "
                       "(🔔 zamanla, ADR-0011).",
        "category": "Otomasyon",
    },
    "dashboards": {
        "label": "Panolar (dashboard)",
        "description": "Chat'te üretilen grafik/tabloyu panoya ekleyip canlı izleme "
                       "(kullanıcı başı ≤10 pano, §9).",
        "category": "Otomasyon",
    },
    "next_steps": {
        "label": "Sonraki adım önerileri",
        "description": "Rapordan deterministik kırılım/ölçek/zaman chip'leri — tıklayınca "
                       "LLM'siz koşar (rehberli analitik K2).",
        "category": "Rehber",
    },
    "ask_intent_first": {
        "label": "Intent-first yönlendirme (/ask)",
        "description": "/ask'te route() boş dönerse LLM'e ham SQL yerine bir Intent-JSON "
                       "(ölçü/boyut/filtre seçimi) doldurttur; deterministik derleyici SQL'i "
                       "üretir (Faz 1). route()'un kendisi bu bayraktan BAĞIMSIZ her zaman "
                       "dener (sıfır risk) — bu bayrak yalnız LLM-destekli Intent-JSON adımını "
                       "kademeli açar (davranış değişikliği taşıyan tek adım).",
        "category": "Yönlendirme",
    },
    "ask_async_discovery": {
        "label": "Discovery arka-plan işi",
        "description": "/ask'in Discovery (ham-SQL LLM) yolu senkron HTTP yerine arka-plan "
                       "işi (AskJob) olarak çalışır; istemci GET /ask/jobs/{id} ile poll eder "
                       "(Faz 4.1 — uzun LLM çağrılarında arayüz donmasın). BİLEREK "
                       "demo/packs/features.yml'e eklenmedi (varsayılan KAPALI) — mevcut "
                       "senkron davranış hiçbir tenant'ta değişmeden kalır; yalnız açıkça "
                       "override edilince devreye girer.",
        "category": "Yönlendirme",
    },
}


def flag_meta(key: str) -> dict[str, str]:
    """Bir bayrağın insan-okur metadata'sı. Kayıtta yoksa anahtarın kendisi etiket
    olur (panel bilinmeyen/DB-only bayrakta da okunur kalır)."""
    return FLAG_REGISTRY.get(key) or {"label": key, "description": "", "category": "Diğer"}


def known_flag_keys(settings) -> set[str]:
    """Bilinen tüm bayrak anahtarları: kanonik kayıt ⊕ YAML fabrika ayarı. Panel
    keşfi buradan — kayıtta olup YAML'da olmayan bayrak da (override edilebilsin
    diye) listelenir."""
    return set(FLAG_REGISTRY) | set(factory_defaults(settings))


def _load_yaml(p: Path) -> dict:
    try:
        return yaml.safe_load(p.read_text()) or {}
    except Exception:
        return {}


def company_sectors(settings) -> list[str]:
    """Aktif şirketin sektör pack anahtarları. İki biçim desteklenir:
    ``sektor: x`` (tekil, elle yazılmış) ve ``sektorler: [x, y]`` (materializer/
    çoklu — compose ile AYNI kural: listede önce gelen kazanır)."""
    base = settings.resolved_project_dir().parent
    cfg = _load_yaml(base / "companies" / settings.company / "company.yml")
    return cfg.get("sektorler") or ([cfg["sektor"]] if cfg.get("sektor") else [])


def factory_defaults(settings) -> dict[str, str]:
    """Fabrika ayarı: GLOBAL platform ⊕ sektör paketleri ⊕ şirket YAML'ı (sağdaki kazanır;
    sektörler arasında listede ÖNCE gelen kazanır). 'off' dahil DÖNER — panel bilinen
    bayrak listesini buradan keşfeder.

    Öncelik (en düşük → yüksek): packs/features.yml (GLOBAL platform, sektörden bağımsız) <
    sektör pack.yml < şirket company.yml. Böylece platform yetenekleri TEK yerde durur ve
    her şirketçe miras alınır; sektör pack'leri yalnız sektöre-özel bayrak taşır (ADR-0009)."""
    base = settings.resolved_project_dir().parent
    company_yml = _load_yaml(base / "companies" / settings.company / "company.yml")
    flags: dict[str, str] = {}
    # 1) GLOBAL platform varsayılanları (en düşük öncelik) — sektör/şirketten bağımsız.
    global_yml = _load_yaml(base / "packs" / "features.yml")
    flags.update({k: str(v) for k, v in (global_yml.get("features") or {}).items()})
    # 2) Sektör paketleri — ters sırayla uygula: sonda yazılan ezer → listede önce gelen kazanır.
    for sektor in reversed(company_sectors(settings)):
        pack = _load_yaml(base / "packs" / "sektor" / str(sektor) / "pack.yml")
        flags.update({k: str(v) for k, v in (pack.get("features") or {}).items()})
    # 3) Şirket YAML'ı (en yüksek fabrika önceliği).
    flags.update({k: str(v) for k, v in (company_yml.get("features") or {}).items()})
    return flags


def _db_overrides() -> list:
    """Tüm FeatureOverride satırları. Control-plane erişilemezse boş (bayraklar
    fabrika ayarına düşer — demo kırılmaz)."""
    try:
        from sqlmodel import Session, select

        from control_plane.db import engine
        from control_plane.models import FeatureOverride

        with Session(engine) as s:
            return list(s.exec(select(FeatureOverride)).all())
    except Exception:
        return []


def resolve_for(settings, principal=None) -> dict[str, str]:
    """Principal'a özel etkin bayrak seti ('off' olanlar elenir).

    Kapsam eşlemesi: sector = aktif şirketin pack anahtarı; tenant = principal
    tenant_id; role = principal rol anahtarları; user = principal user_id.
    """
    flags = dict(factory_defaults(settings))

    sectors = set(company_sectors(settings))
    tenant_id = getattr(principal, "tenant_id", None)
    roles = set(getattr(principal, "roles", None) or [])
    user_id = getattr(principal, "user_id", None)

    def _matches(o) -> bool:
        if o.scope_type == "global":
            return True
        if o.scope_type == "sector":
            return o.scope_id in sectors
        if o.scope_type == "tenant":
            return tenant_id is not None and o.scope_id == tenant_id
        if o.scope_type == "role":
            return o.scope_id in roles
        if o.scope_type == "user":
            return user_id is not None and o.scope_id == user_id
        return False

    # Spesifiklik sırasıyla uygula: sonra yazılan (daha spesifik) kazanır.
    overrides = _db_overrides()
    for scope in _SCOPE_ORDER:
        for o in overrides:
            if o.scope_type == scope and _matches(o) and o.stage in STAGES:
                flags[o.feature_key] = o.stage

    return {k: v for k, v in flags.items() if v != "off"}


def resolve(settings) -> dict[str, str]:
    """Geriye-uyum: principal'sız çözüm (fabrika ayarı + yalnız global/sector
    override'ları — kimliksiz bağlamlar için)."""
    return resolve_for(settings, principal=None)
