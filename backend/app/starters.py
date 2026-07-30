"""Rehberli analitik K1 — rol/sektör bazlı BAŞLANGIÇ soruları (starter questions).

Küratörlü starter'lar pack zincirinden çözülür (şirket company.yml → sektör pack.yml →
global packs/starters.yml), features çözümüyle AYNI desen. En SPESİFİK non-boş kazanır
(liste olduğundan flag gibi merge DEĞİL, ikame). Rol etiketi opsiyonel: starter'ın
``roles``'ü kullanıcının rolleriyle kesişmiyorsa (ve boş değilse) elenir → rol bazlı.
Küratör yoksa çağıran katalog-türevi otomatik öneriye düşer. Deterministik (LLM yok).
"""

from __future__ import annotations

from app.features import _load_yaml, company_sectors


def _curated(settings) -> list:
    """En spesifik non-boş kaynak: şirket > sektör(ler) > global. Liste (ikame, merge değil)."""
    base = settings.resolved_project_dir().parent
    company = _load_yaml(base / "companies" / settings.company / "company.yml")
    if company.get("starters"):
        return company["starters"]
    for sektor in company_sectors(settings):
        pack = _load_yaml(base / "packs" / "sektor" / str(sektor) / "pack.yml")
        if pack.get("starters"):
            return pack["starters"]
    return (_load_yaml(base / "packs" / "starters.yml") or {}).get("starters") or []


def starter_questions(settings, principal=None) -> list[dict]:
    """Rol-filtreli küratörlü başlangıç soruları ``[{label, query}]``. Küratör yoksa boş
    (çağıran katalog otomatiğine düşer)."""
    roles = set(getattr(principal, "roles", None) or [])
    out: list[dict] = []
    for s in _curated(settings):
        if not isinstance(s, dict) or not s.get("query"):
            continue
        want = set(s.get("roles") or [])
        if want and not (want & roles):
            continue  # role-tagged ama kullanıcı o rolde değil → gösterme
        out.append({"label": str(s.get("label") or s["query"]), "query": str(s["query"])})
    return out
