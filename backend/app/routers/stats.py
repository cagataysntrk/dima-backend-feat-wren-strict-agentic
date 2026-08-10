"""Faz 4.13c (1 Ağustos 2026) — dış yol haritası 2.18 "meta-güven şeridi": son-kullanıcıya
"bugün soruların %X'i yapay zekaya hiç gitmeden cevaplandı" özeti.

`admin_app/routers/interactions.py::route_distribution`'ın (superadmin, TÜM tenant'lar,
7-90 gün) KÜÇÜK, KULLANICI-görünür karşılığı: yalnız KENDİ tenant'ı, yalnız BUGÜN
(varsayılan) — aynı `interaction_log` kaynağından, aynı sınıflandırma ilkesiyle."""

from __future__ import annotations

from datetime import datetime, timedelta

import uuid as _uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session, func, select

from app.auth.dependencies import require, require_company


def _uuid_or_none(val):
    """str(uuid) → UUID (InteractionLog.tenant_id UUID kolonu — ham principal.tenant_id
    string'i doğrudan bind edilirse SQLAlchemy UUID adaptörü patlıyordu). Geçersiz/boş →
    None (aynı desen: app/routers/ask.py::_uuid_or_none)."""
    try:
        return _uuid.UUID(val) if val else None
    except (ValueError, TypeError):
        return None

router = APIRouter(prefix="/stats", tags=["stats"])


def _llm_free(kind: str | None) -> bool:
    """`_source_kind()`'ın (app/routers/ask.py) ürettiği normalize kind — LLM'e HİÇ
    düşmeyen yollar: cube/vqr/rule/meta/catalog/statement/upload. Yalnız 'llm' gerçek
    bir LLM çağrısı anlamına gelir."""
    return kind is not None and kind != "llm"


@router.get("/today", dependencies=[Depends(require("query:run")), Depends(require_company)])
def stats_today(request: Request, days: int = Query(1, ge=1, le=30)) -> dict:
    """Bugünkü (ya da son `days` gündeki) /ask cevaplarının kaçının LLM'e hiç gitmeden
    (deterministik cube/VQR/kural/meta/katalog) yanıtlandığı — KENDİ tenant'ına özel."""
    from control_plane.db import engine
    from control_plane.models import InteractionLog

    principal = getattr(request.state, "principal", None)
    tenant_id = _uuid_or_none(getattr(principal, "tenant_id", None))
    since = datetime.utcnow() - timedelta(days=days)

    with Session(engine) as s:
        stmt = select(InteractionLog.kind, func.count()).where(InteractionLog.ts >= since)
        if tenant_id:
            stmt = stmt.where(InteractionLog.tenant_id == tenant_id)
        stmt = stmt.group_by(InteractionLog.kind)
        rows = s.exec(stmt).all()

    total = sum(c for _, c in rows)
    llm_free = sum(c for k, c in rows if _llm_free(k))
    pct = round(llm_free / total * 100) if total else None
    message = (
        f"Bugün {pct}% soru yapay zekaya hiç gitmeden cevaplandı." if pct is not None
        else "Henüz bugüne ait bir soru yok."
    )
    return {"total": total, "llm_free": llm_free, "llm_free_pct": pct, "message": message}


# ═══ FAZ 0.17 — YOL BAŞINA GECİKME BÜTÇESİ ═══════════════════════════════════════
#
# 🔴 EK D'de **60+ eşik** var, **tek gecikme eşiği yok** — oysa kapalı dört LLM
# bayrağının `features.yml`'deki gerekçesi üç kez aynı cümle: *"sıcak yola LLM çağrısı
# ekliyor"*, yani **gecikme**. MIMARI §2.2'de ölçüm **var**: Discovery **12.567 ms** ↔
# cube **145-434 ms** (**30-85×**), ve `consistency_k=3` ile bir Intent turu **üç**
# çağrı yapar. **30-85× fark ölçülmüş, bütçeye çevrilmemiş.**
#
# ⚠ **VE DIŞ KANIT BEKLENTİYİ TERSİNE ÇEVİRİYOR** (240 katılımcı, TTFT 2s/9s/20s):
# **2 saniyede gelen cevap, 9 saniyede gelenden DAHA AZ** düşünülmüş ve faydalı bulundu;
# **9s en faydalı** koşuldu. *"Streaming algılanan kaliteyi artırır"* iddiasının hakemli
# çalışması **yok**. → Bu bütçe bir **hız yarışı değil**, bir **sürpriz kapanıdır**:
# `t2_anlatici`'yi kapalı tutan asıl soru gecikme değil **KAZANÇ** olmalı; bütçe yalnız
# *"30× fark fark edilmeden büyümesin"* diye vardır.
#
# ⚠ **YENİ ENSTRÜMANTASYON YOK** — `duration_ms` zaten `interaction_log`'da.

#: İlan edilen bütçe (p95, ms). **Öneridir ve ölçümle düzeltilir** — sabit bir hedef
#: değil, bir **sürpriz kapanı**. Bir yol bütçesini aşıyorsa cevap *"hızlandır"* değil,
#: önce *"neden"* olmalıdır: yol değişti mi, `consistency_k` mi arttı, kota mı doydu.
GECIKME_BUTCESI_MS: dict[str, int] = {
    "cube": 800,        # ölçüldü 145-434 ms — deterministik yol, LLM yok
    "vqr": 800,         # replay; cube ile aynı sınıf
    "rule": 800,        # kural-tabanlı üretici, ağ yok
    "meta": 300,        # sabit metin
    "catalog": 300,     # katalog listesi
    "llm": 20_000,      # Discovery ölçüldü 12.567 ms; Intent `consistency_k=3` ile 3 çağrı
}


def _yuzdelik(degerler: list[int], p: float) -> int | None:
    """`p` yüzdelik (0-1). Boş listede **None** — `0` DEĞİL.

    `0` *"çok hızlı"* demektir; `None` *"bu soru sorulamaz"*. Aynı ayrım
    `app/stats.py::z_skorlari` ve `context.SureklilikOlcumu.oran`'da da var ve aynı
    nedenle: **ölçülemeyeni iyi göstermek, ölçmemekten daha yanıltıcıdır.**
    """
    if not degerler:
        return None
    s = sorted(degerler)
    i = min(len(s) - 1, max(0, round(p * (len(s) - 1))))
    return int(s[i])


@router.get("/gecikme", dependencies=[Depends(require("query:run")), Depends(require_company)])
def stats_gecikme(request: Request, days: int = Query(7, ge=1, le=90)) -> dict:
    """Yol başına **p50/p95** gecikme + ilan edilen bütçe.

    Yol = `InteractionLog.kind` (`cube|vqr|rule|meta|catalog|llm|…`) — `/stats/today`
    ile **aynı sınıflandırma**; ikinci bir yol taksonomisi açılmaz.
    """
    from control_plane.db import engine
    from control_plane.models import InteractionLog

    principal = getattr(request.state, "principal", None)
    tenant_id = _uuid_or_none(getattr(principal, "tenant_id", None))
    since = datetime.utcnow() - timedelta(days=days)

    per_yol: dict[str, list[int]] = {}
    with Session(engine) as s:
        q = select(InteractionLog.kind, InteractionLog.duration_ms).where(
            InteractionLog.ts >= since, InteractionLog.duration_ms.is_not(None))
        if tenant_id is not None:
            q = q.where(InteractionLog.tenant_id == tenant_id)
        for kind, ms in s.exec(q).all():
            per_yol.setdefault(kind or "bilinmiyor", []).append(int(ms))

    yollar = []
    for yol, degerler in sorted(per_yol.items()):
        p95 = _yuzdelik(degerler, 0.95)
        butce = GECIKME_BUTCESI_MS.get(yol)
        yollar.append({
            "yol": yol,
            "n": len(degerler),
            "p50_ms": _yuzdelik(degerler, 0.50),
            "p95_ms": p95,
            "butce_ms": butce,
            # ⊘ ÜÇÜNCÜ DURUM: bütçe ilan edilmemiş bir yol "aştı" da denemez,
            # "aşmadı" da — soru sorulamaz.
            "asildi": None if (butce is None or p95 is None) else p95 > butce,
        })
    return {
        "gun": days,
        "yollar": yollar,
        "butce": GECIKME_BUTCESI_MS,
        "_not": ("Bütçe bir HIZ YARIŞI değil, bir SÜRPRİZ KAPANIDIR. Dış kanıt (240 "
                 "katılımcı, TTFT 2s/9s/20s): 2 saniyede gelen cevap, 9 saniyede "
                 "gelenden DAHA AZ faydalı bulundu. Bir yol bütçesini aşıyorsa cevap "
                 "'hızlandır' değil, önce 'NEDEN' olmalıdır."),
    }


@router.get("/plan", dependencies=[Depends(require("query:run")), Depends(require_company)])
def stats_plan() -> dict:
    """🔴🔴 `A9` — **PLAN REDDİ ARTIK BİR SAYI.**

    ⊙ Ölçüldü (rapor `§B-9`): `plan_garson.SAYAC` **vardı**, `sayaclar()` **vardı** ve
    **hiçbir tüketicisi yoktu**. Red oranı loglara gözle bakılarak tespit ediliyordu —
    yani bir düzeltmenin kaç redde dokunduğu **ölçülemiyordu**.

    ⚠ Süreç-içi sayaçtır: yeniden başlatınca sıfırlanır ve **öyle olmalı** — bu bir
    denetim kaydı değil, bir **tur ölçüsü**. Kalıcı olması gerekseydi `interaction_log`
    zaten var. *Bir ölçüyü kalıcı yapmak, onu ikinci kez yazmaya davet eder.*

    Döner: `denendi` · `gecerli` · `onarildi` · `dustu` · `red_orani_yuzde` ·
    `onarim_tutma_yuzde` · `tek_adimli`/`cok_adimli` · **`red_nedenleri`** (sınıf → adet).
    """
    from app.plan_garson import sayaclar

    return sayaclar()


@router.get("/katalog", dependencies=[Depends(require("query:run")), Depends(require_company)])
def stats_katalog(request: Request) -> dict:
    """🔴 `A11`/`B-0` — kataloğun envanteri **tek kaynaktan** (`katalog_metni.envanter`).

    ⊙ Rapor üç ayrı sayı bulmuştu (127/132/141); çelişki bir kusur değil **adsızlıktı**:
    *benzersiz ölçü adı* ≠ *ölçü tanımı* ≠ *pack'te yazılı*. Bu uç **çözülmüş şemayı**
    (bu kiracıya yüklü olanı) sayar ve alanlarını adıyla verir.
    """
    # ⚠ Servis **kiracıya göre** çözülür: `request.state.wren` yalnız varsayılan
    # olmayan tenant'ta set edilir ve `app.state`'i doğrudan okumak, bu deponun bir kez
    # ölçtüğü kusuru (VQR'ın tek şirket dışında sessizce kapanması) tekrarlardı.
    from app.company_registry import wren_for_request
    from app.katalog_metni import envanter

    return envanter(wren_for_request(request).schema())
