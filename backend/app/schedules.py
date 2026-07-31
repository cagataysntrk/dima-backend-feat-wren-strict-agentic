"""Zamanlanmış raporlar + eşik alarmları (ADR-0011) — pull'dan push'a.

Tanım + koşum durumu (last_run) + bildirim HEPSİ Postgres'te (tek-kaynak DB): tanımlar
`schedule_definition`, koşum durumu `last_run` kolonu (atomik CAS → çok-instance double-fire
yok), bildirimler `notification_log`. Dönem GÖRELİ saklanır ("dün", "son 7 gün") ve her
koşumda tarih motoruyla çözülür — VQR'daki "dönem saklanmaz" ilkesinin aynısı.

Her koşum bir Query Contract (ADR-0010) alır: alarm eşiği ihlali sözleşme ID'siyle
kanıtlanabilir. Teslim: in-app bell (`notification_log` DB + UI zili) HER ZAMAN +
opsiyonel ek kanallar (`app/channels.py` — e-posta/Resend ilk; Slack/webhook pluggable).

Zamanlama basit tutuldu (cron ifadesi değil): every: hour | day | week (+ at/weekday).
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone

from app.logging_setup import get_logger

_log = get_logger("schedules")


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ScheduleStore:
    """Zamanlanmış rapor deposu — TEK-KAYNAK Postgres. Tanım (schedule_definition), koşum
    durumu (last_run + atomik CAS claim → çok-instance double-fire yok) ve bildirim
    (notification_log) hepsi DB'de. Eski dosya-state (schedule-state.json / notifications.jsonl)
    kaldırıldı: tek-servis volume çok-instance'ta çakışıyor + admin plane okuyamıyordu (ADR-0011)."""

    def __init__(self, company: str):
        # Tanım + koşum durumu (last_run) + bildirim HEPSİ DB'de (tek-kaynak) → dosya-yolu yok.
        self.company = company

    # -- tanımlar (Postgres; DB erişilemezse boş — akış kırılmaz) ---------
    def _session(self):
        from sqlmodel import Session

        from control_plane.db import engine
        return Session(engine)

    def _to_dict(self, r) -> dict:
        """DB satırı → router/koşum'un beklediği dict şekli (cube_query/threshold parse'lı)."""
        d = {
            "id": r.id, "label": r.label,
            "cube_query": json.loads(r.cube_query_json) if r.cube_query_json else {},
            "period": r.period, "every": r.every, "at": r.at,
            "enabled": r.enabled, "created_by": r.created_by, "tenant_id": r.tenant_id,
        }
        if r.weekday is not None:
            d["weekday"] = r.weekday
        if r.threshold_json:
            d["threshold"] = json.loads(r.threshold_json)
        if r.delivery_json:
            d["delivery"] = json.loads(r.delivery_json)
        return d

    def list(self) -> list[dict]:
        try:
            from sqlmodel import col, select

            from control_plane.models import ScheduleDefinition
            with self._session() as s:
                rows = s.exec(
                    select(ScheduleDefinition)
                    .where(ScheduleDefinition.company == self.company,
                           col(ScheduleDefinition.deleted_at).is_(None))
                    .order_by(col(ScheduleDefinition.created_at))
                ).all()
            return [self._to_dict(r) for r in rows]
        except Exception:
            _log.warning("schedule tanımları DB'den okunamadı", exc_info=True)
            return []

    def add(self, sched: dict) -> dict:
        sched = dict(sched)
        sched["id"] = sched.get("id") or ("s-" + uuid.uuid4().hex[:8])
        sched.setdefault("enabled", True)
        try:
            from control_plane.models import ScheduleDefinition
            with self._session() as s:
                s.add(ScheduleDefinition(
                    id=sched["id"], company=self.company, tenant_id=sched.get("tenant_id"),
                    label=sched.get("label") or "",
                    cube_query_json=json.dumps(sched.get("cube_query") or {}, ensure_ascii=False),
                    period=sched.get("period"), every=sched.get("every", "day"),
                    at=sched.get("at"), weekday=sched.get("weekday"),
                    threshold_json=(json.dumps(sched["threshold"], ensure_ascii=False)
                                    if sched.get("threshold") else None),
                    delivery_json=(json.dumps(sched["delivery"], ensure_ascii=False)
                                   if sched.get("delivery") else None),
                    enabled=sched.get("enabled", True), created_by=sched.get("created_by")))
                s.commit()
        except Exception:
            _log.warning("schedule tanımı DB'ye yazılamadı", exc_info=True)
        return sched

    def remove(self, sid: str) -> bool:
        """Soft-delete (deleted_at damgası; fiziksel silinmez — ADR-0019)."""
        try:
            from sqlmodel import col, select

            from control_plane.models import ScheduleDefinition
            with self._session() as s:
                row = s.exec(select(ScheduleDefinition).where(
                    ScheduleDefinition.id == sid,
                    ScheduleDefinition.company == self.company,
                    col(ScheduleDefinition.deleted_at).is_(None))).first()
                if row is None:
                    return False
                row.deleted_at = datetime.utcnow()
                s.add(row)
                s.commit()
            return True
        except Exception:
            _log.warning("schedule tanımı soft-delete edilemedi", exc_info=True)
            return False

    def get(self, sid: str) -> dict | None:
        return next((s for s in self.list() if s.get("id") == sid), None)

    # -- koşum durumu (TEK-KAYNAK DB; schedule-state.json kaldırıldı) ------
    # Neden DB: dosya-only state her instance'ın KENDİ volume'unu okur → çok-instance
    # prod'da aynı zamanlanmış rapor iki kez koşup mail atardı (double-fire). last_run
    # artık schedule_definition kolonunda; `try_claim` atomik CAS ile tek koşum garantisi.
    def last_run(self, sid: str) -> datetime | None:
        try:
            from sqlmodel import select

            from control_plane.models import ScheduleDefinition
            with self._session() as s:
                row = s.exec(select(ScheduleDefinition).where(
                    ScheduleDefinition.id == sid,
                    ScheduleDefinition.company == self.company)).first()
                return row.last_run if row else None
        except Exception:
            _log.warning("schedule last_run okunamadı", exc_info=True)
            return None

    def mark_run(self, sid: str, when: datetime) -> None:
        try:
            from sqlalchemy import update

            from control_plane.models import ScheduleDefinition
            with self._session() as s:
                s.execute(update(ScheduleDefinition)
                          .where(ScheduleDefinition.id == sid,
                                 ScheduleDefinition.company == self.company)
                          .values(last_run=when))
                s.commit()
        except Exception:
            _log.warning("schedule last_run güncellenemedi", exc_info=True)

    def try_claim(self, sid: str, now: datetime, prev: datetime | None) -> bool:
        """ATOMİK CLAIM (compare-and-swap): last_run'ı `prev`→`now` yalnız hâlâ `prev`
        iken günceller. rowcount==1 → bu instance koşumu ALDI; 0 → başka instance almış
        (double-fire engellendi). Çok-instance güvenli tek koşum garantisi."""
        try:
            from sqlmodel import col
            from sqlalchemy import update

            from control_plane.models import ScheduleDefinition
            cond = (col(ScheduleDefinition.last_run).is_(None) if prev is None
                    else ScheduleDefinition.last_run == prev)
            with self._session() as s:
                res = s.execute(update(ScheduleDefinition)
                                .where(ScheduleDefinition.id == sid,
                                       ScheduleDefinition.company == self.company, cond)
                                .values(last_run=now))
                s.commit()
                return (res.rowcount or 0) == 1
        except Exception:
            _log.warning("schedule claim başarısız", exc_info=True)
            return False

    # -- bildirimler (TEK-KAYNAK DB; notifications.jsonl dual-write kaldırıldı) --
    # Neden: `notification_log` DB'de zaten vardı → jsonl redundant'tı. İki okuyucu
    # (public bell + admin plane) TEK kaynaktan (Postgres) okur; yazım da tek yerde.
    def notify(self, rec: dict) -> dict:
        rec = dict(rec)
        rec.setdefault("ts", _now().isoformat(timespec="seconds"))
        # DB'ye yaz ve ATANAN id'yi rec'e koy → notify'ın döndürdüğü id, sonra
        # notifications() ile okunanla AYNI (tek stabil id; okuyucu/yazıcı tutarlı).
        new_id = self._log_to_db(rec)
        rec["id"] = new_id if new_id is not None else rec.get("id", "n-" + uuid.uuid4().hex[:8])
        return rec

    def _log_to_db(self, rec: dict) -> int | None:
        """Bildirimi `notification_log`'a yazar (tek-kaynak); atanan int id'yi döner.
        Best-effort — bir bildirim kaybı akışı/koşumu kırmaz (compliance değil, UX telemetrisi)."""
        try:
            from control_plane.models import NotificationLog
            with self._session() as s:
                row = NotificationLog(
                    company=self.company, tenant_id=rec.get("tenant_id"),
                    schedule_id=rec.get("schedule_id"), kind=str(rec.get("kind") or "report"),
                    message=str(rec.get("message") or ""), row_count=rec.get("row_count"),
                    contract_id=rec.get("contract_id"),
                    delivery_json=(json.dumps(rec["delivery"], ensure_ascii=False)
                                   if rec.get("delivery") else None))
                s.add(row)
                s.commit()
                return row.id
        except Exception:
            _log.warning("notification_log'a yazılamadı (best-effort)", exc_info=True)
            return None

    def _notif_to_dict(self, r) -> dict:
        d = {
            "id": r.id, "ts": r.ts.isoformat(timespec="seconds") if r.ts else None,
            "tenant_id": r.tenant_id, "schedule_id": r.schedule_id, "kind": r.kind,
            "message": r.message, "row_count": r.row_count, "contract_id": r.contract_id,
        }
        if r.delivery_json:
            d["delivery"] = json.loads(r.delivery_json)
        return d

    def notifications(self, limit: int = 20, tenant_id: str | None = None,
                      include_legacy: bool = True) -> list[dict]:
        try:
            from sqlmodel import col, select

            from control_plane.models import NotificationLog
            with self._session() as s:
                rows = s.exec(select(NotificationLog)
                              .where(NotificationLog.company == self.company)
                              .order_by(col(NotificationLog.ts).desc())
                              .limit(max(limit * 3, limit))).all()
            out = []
            for r in rows:
                # Tenant-RLS: tenant_id'siz (RLS-öncesi) kayıt yalnız aktif şirkete görünür.
                if tenant_id is not None:
                    if (r.tenant_id is None and not include_legacy) or (
                            r.tenant_id is not None and r.tenant_id != tenant_id):
                        continue
                out.append(self._notif_to_dict(r))
                if len(out) >= limit:
                    break
            return out
        except Exception:
            _log.warning("bildirimler okunamadı", exc_info=True)
            return []


def is_due(sched: dict, last: datetime | None, now: datetime) -> bool:
    """Basit zamanlama: every hour|day|week (+ at "HH:MM", weekday 1=Pzt..7=Paz).
    Saatler UTC değil YEREL kabul edilir (demo tek makinede koşar)."""
    local = now.astimezone()
    every = sched.get("every", "day")
    if every == "hour":
        return last is None or (now - last).total_seconds() >= 3600
    hh, mm = (str(sched.get("at", "08:00")) + ":0").split(":")[:2]
    slot = local.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
    if every == "week":
        wd = int(sched.get("weekday", 1))  # 1=Pzt
        if local.isoweekday() != wd:
            return False
    if local < slot:
        return False  # bugünkü slot henüz gelmedi
    if last is None:
        return True
    # last DB'den NAIVE-UTC gelir (last_run kolonu timezone'suz); astimezone() onu YEREL
    # sanıp UTC-olmayan host'ta offset kadar kaydırırdı → UTC etiketle, sonra yerele çevir.
    last_aware = last if last.tzinfo else last.replace(tzinfo=timezone.utc)
    return last_aware.astimezone() < slot


def check_threshold(threshold: dict | None, result: dict) -> list[str]:
    """Eşik ihlalleri: ölçü değeri op/value'yu aşan satırların insan-okur listesi."""
    if not threshold:
        return []
    m = threshold.get("measure")
    op = str(threshold.get("op", "gt"))
    try:
        val = float(threshold.get("value"))
    except (TypeError, ValueError):
        return []
    cmp = {
        "gt": lambda v: v > val, "gte": lambda v: v >= val,
        "lt": lambda v: v < val, "lte": lambda v: v <= val,
    }.get(op)
    if cmp is None or not m:
        return []
    bad: list[str] = []
    for row in result.get("rows") or []:
        v = row.get(m)
        if v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if cmp(fv):
            dims = [str(x) for k, x in row.items() if k != m]
            tag = " · ".join(dims) if dims else "toplam"
            sign = ">" if op.startswith("g") else "<"
            bad.append(f"{tag}: {fv:g} ({sign} eşik {val:g})")
    return bad


_AY_KISA = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def _fmt_deger(v: float) -> str:
    """İnsan-okur sayı — bilimsel gösterim (1.5576e+07) YOK; Türkçe binlik '.'/ondalık ','.
    15576000 → '15.576.000'; 12.34 → '12,34'."""
    n = round(float(v), 2)
    if n == int(n):
        return f"{int(n):,}".replace(",", ".")
    whole, frac = f"{n:.2f}".split(".")
    return f"{int(whole):,}".replace(",", ".") + "," + frac


def _is_sayi(x) -> bool:
    """x sayısal mı (float'a çevrilebilir)? — anomali tag'inde diğer ölçü/türev kolonları
    (ör. YoY _gecen / _degisim_yuzde) BOYUT sanılmasın diye eler; tarih/etiket kalır."""
    if isinstance(x, bool) or x is None:
        return False
    try:
        float(x)
        return True
    except (TypeError, ValueError):
        return False


def _fmt_boyut(x) -> str:
    """Boyut değerini okunur yap: ham datetime ('2026-04-01 00:00:00') → 'Nis 2026' (ay-başı)
    ya da '15.04.2026' (gün); diğerleri olduğu gibi."""
    s = str(x)
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12:
            return f"{_AY_KISA[mo - 1]} {y}" if d == 1 else f"{d:02d}.{mo:02d}.{y}"
    return s


def _ile_birim(s: str, unit: str | None) -> str:
    """Değere birim ekle — Türkçe: % ÖNDE (%12,3), diğerleri ARKADA (15.575.954,29 ₺)."""
    if not unit:
        return s
    return f"%{s}" if unit == "%" else f"{s} {unit}"


def detect_anomalies(result: dict, measure: str, k: float = 2.0, unit: str | None = None) -> list[str]:
    """Z-skoru anomalileri: ölçü serisinin ortalama ± k·std DIŞINA çıkan noktalar
    ("olağandışı enerji", "beklenmedik duraksama"). Sabit eşiğin aksine baseline
    veriden öğrenilir. Seri < 4 nokta ya da std=0 → boş (istatistik anlamsız).
    Deterministik (LLM yok) — insan-okur ihlal listesi döner."""
    rows = result.get("rows") or []
    vals: list[float | None] = []
    for row in rows:
        try:
            vals.append(float(row.get(measure)))
        except (TypeError, ValueError):
            vals.append(None)
    nums = [v for v in vals if v is not None]
    if len(nums) < 4:
        return []
    mean = sum(nums) / len(nums)
    std = (sum((v - mean) ** 2 for v in nums) / len(nums)) ** 0.5
    if std == 0:
        return []
    bad: list[str] = []
    for row, v in zip(rows, vals):
        if v is None:
            continue
        z = (v - mean) / std
        if abs(z) >= k:
            # Tag = yalnız BOYUT/tarih değerleri; diğer ölçü/türev kolonları (YoY _gecen/
            # _degisim_yuzde, blend ölçüleri) sayısaldır → tag'e girmez (kirlenme önlenir).
            dims = [_fmt_boyut(x) for kk, x in row.items() if kk != measure and not _is_sayi(x)]
            tag = " · ".join(dims) if dims else "nokta"
            yon = "yüksek" if z > 0 else "düşük"
            bad.append(f"{tag}: {_ile_birim(_fmt_deger(v), unit)} (olağandışı {yon}, z={z:+.1f})")
    return bad


def check_alert(config: dict | None, result: dict) -> tuple[str, list[str]]:
    """Alarm değerlendirme — iki tip TEK giriş: sabit EŞİK (op/value) VEYA ANOMALİ
    (method=zscore, baseline'dan öğrenir). Döner: (tip, ihlal listesi). Aynı
    ``threshold`` alanı iki şekli de taşır (şema değişmeden)."""
    if not config or not config.get("measure"):
        return ("", [])
    if str(config.get("method", "")) in ("zscore", "anomali", "anomaly"):
        return ("anomaly", detect_anomalies(result, config["measure"], float(config.get("k", 2.0))))
    return ("threshold", check_threshold(config, result))


def _tenant_slug(tenant_id: str) -> str | None:
    """tenant_id (UUID str) → Tenant.slug (company_registry'nin anahtarı)."""
    try:
        import uuid as _uuid

        from sqlmodel import Session, select

        from control_plane.db import engine
        from control_plane.models import Tenant
        with Session(engine) as s:
            row = s.exec(select(Tenant).where(Tenant.id == _uuid.UUID(tenant_id))).first()
            return row.slug if row else None
    except Exception:
        _log.warning(f"tenant {tenant_id} slug'ı çözülemedi", exc_info=True)
        return None


def _wren_for_schedule(state, sched: dict):
    """Zamanlanmış raporun GERÇEK sahibi tenant'ının WrenService'i — süreç varsayılanı
    (`state.wren`) DEĞİL. ÖNCEDEN `run_schedule` körlemesine `state.wren` kullanıyordu: B
    tenant'ının zamanlanmış raporu A'nın (varsayılan şirket) verisini görüyordu — kanıtlanmış
    cross-tenant sızıntı (KVKK md. 12 ihlali). `company_registry.vqr_for`/`wren_for_request`
    ile aynı desen: slug'a göre talep-üzerine derlenmiş servisi döner.

    Fail-closed: tenant_id set ama slug/servis çözülemiyorsa, YANLIŞ (varsayılan) tenant'ın
    verisini göstermek yerine raporu ÇALIŞTIRMAZ (istisna fırlatır)."""
    tenant_id = sched.get("tenant_id")
    if not tenant_id:
        return state.wren  # eski/tenant'sız kayıt (RLS-öncesi) — süreç varsayılanı zaten doğru
    slug = _tenant_slug(tenant_id)
    if slug is None:
        raise RuntimeError(f"schedule {sched.get('id')}: tenant {tenant_id} slug'ı bulunamadı "
                          "(fail-closed — varsayılan tenant'ın verisi gösterilmez)")
    if slug == getattr(state.wren, "company_slug", None):
        return state.wren  # zaten varsayılan şirket
    registry = getattr(state, "company_registry", None)
    if registry is None:
        raise RuntimeError(f"schedule {sched.get('id')}: company_registry yok, "
                          f"tenant {slug} servisi çözülemez (fail-closed)")
    return registry.service_for(slug)


def run_schedule(state, sched: dict, *, manual: bool = False) -> dict:
    """Bir zamanlanmış raporu KOŞAR: dönem çözülür → sorgu → sözleşme → eşik → bildirim.

    `state` = FastAPI app.state (wren, contracts, schedules)."""
    from app import cube_router

    svc = _wren_for_schedule(state, sched)
    store: ScheduleStore = state.schedules

    cq = json.loads(json.dumps(sched.get("cube_query") or {}))
    period = str(sched.get("period") or "").strip()
    if period:
        dfs = cube_router.date_filters(cube_router._norm(period), "tarih")
        cq["filters"] = [f for f in cq.get("filters", []) if f.get("dimension") != "tarih"] + dfs

    sql = svc.cube_sql(cq)
    result = svc.query(sql, limit=1000)

    contract_id = None
    contracts = getattr(state, "contracts", None)
    if contracts is not None:
        try:
            contract_id = contracts.record(
                session_id=f"schedule:{sched.get('id')}",
                question=f"[zamanlanmış] {sched.get('label') or sched.get('id')}"
                + (f" · {period}" if period else ""),
                cube_query=cq,
                sql=sql,
                result=result,
                source="schedule",
                schema_version=svc.mdl_version,
                tenant_id=sched.get("tenant_id"),
            )
        except Exception:
            pass

    alert_kind, violations = check_alert(sched.get("threshold"), result)
    if violations:
        kind = "anomaly" if alert_kind == "anomaly" else "alert"
        lead = "olağandışı değerler" if kind == "anomaly" else "eşik ihlali"
        severity = "warning" if kind == "anomaly" else "critical"
        message = (
            f"⚠ {sched.get('label') or sched.get('id')}: {lead} — "
            + "; ".join(violations[:3])
            + (f" (+{len(violations) - 3} satır)" if len(violations) > 3 else "")
        )
    else:
        kind = "report"
        severity = "info"
        message = (
            f"{sched.get('label') or sched.get('id')}: rapor hazır"
            + (f" · {period}" if period else "")
            + f" · {result.get('row_count')} satır"
        )

    # Birleşik teslim: anlamsal event → hedef çözümü (inapp + schedule.delivery +
    # ileride kullanıcı tercihi) → dispatcher fan-out (her kanal izole). "Her şey kanal":
    # in-app bell de registry'de bir kanal (inapp_sink DI ile notification_log'a yazar).
    from app import channels, viz as _viz

    # VİZ ÖNERİSİ (ADR-0024 cross-surface): e-posta da grafik/tablo kararını taşır (chat/pano ile
    # AYNI). Cube ölçü birimleri çok-birim politikasını besler; üretilemezse None (email tabloya düşer).
    viz_spec = None
    try:
        _cmeta = next(
            (c for c in (svc.schema().get("cubes") or []) if c.get("name") == cq.get("cube")), None
        )
        viz_spec = _viz.recommend(
            result, units=(_cmeta or {}).get("measure_units") or {},
            lower_set=(_cmeta or {}).get("lower_is_better") or [], cube_query=cq,
        )
    except Exception:
        pass

    event = channels.NotificationEvent(
        category=kind, severity=severity,
        title=sched.get("label") or sched.get("id") or "Rapor",
        summary=message,
        rows=result.get("rows") or [],
        viz=viz_spec,
        violations=violations,
        contract_id=contract_id,
        schedule_id=sched.get("id"),
        tenant_id=sched.get("tenant_id"),
        period=period or None,
        row_count=result.get("row_count"),
        extra={"cube_query": cq, "manual": manual},
    )
    targets = channels.resolve_targets(kind, schedule_delivery=sched.get("delivery"))
    statuses = channels.dispatch(
        event, targets, channels.DispatchContext(inapp_sink=store.notify))

    # inapp log kaydı dış teslim sonuçlarını (email) zaten içerir (notification_log).
    inapp = next((s for s in statuses if s.get("channel") == "inapp" and s.get("record")), None)
    note = inapp["record"] if inapp else {"kind": kind, "message": message,
                                          "delivery": [s for s in statuses] or None}

    if not manual:
        store.mark_run(sched["id"], _now())
    return note


def run_due(state) -> int:
    """Vadesi gelen tüm zamanlanmış raporları koşar; koşulan sayıyı döner."""
    store: ScheduleStore = state.schedules
    now = _now()
    n = 0
    for sched in store.list():
        if not sched.get("enabled", True):
            continue
        try:
            prev = store.last_run(sched["id"])
            if is_due(sched, prev, now):
                # ATOMİK CLAIM: yalnız claim eden instance koşar (çok-instance double-fire
                # engeli). Claim başarısız → başka instance zaten aldı → atla.
                if store.try_claim(sched["id"], now, prev):
                    run_schedule(state, sched)
                    n += 1
        except Exception:
            continue  # tek zamanlama hatası diğerlerini durdurmasın
    return n
