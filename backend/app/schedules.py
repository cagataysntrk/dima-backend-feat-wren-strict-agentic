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

from app.arkaplan_kimlik import KimliksizArkaPlanIsi
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
                                   if rec.get("delivery") else None),
                    neden_json=(json.dumps({"satirlar": rec.get("neden") or [],
                                            "not": rec.get("neden_not")},
                                           ensure_ascii=False)
                                if (rec.get("neden") or rec.get("neden_not")) else None))
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
        # `neden_json` ESKİ satırlarda YOK (Faz F3 öncesi) ve kolonun kendisi de eski bir
        # şemada bulunmayabilir — `getattr` ikisini de karşılar. Neden yoksa alan hiç
        # görünmez: "boş neden" ile "neden üretilmedi" karışmasın.
        ham = getattr(r, "neden_json", None)
        if ham:
            n = json.loads(ham)
            if n.get("satirlar"):
                d["neden"] = n["satirlar"]
            if n.get("not"):
                d["neden_not"] = n["not"]
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
    """Gövdesi `app/fmt.py`'de (Faz C2)."""
    from app.fmt import sayi

    return sayi(v)


def _is_sayi(x) -> bool:
    """Gövdesi `app/result_shape.py`'de (Faz C2)."""
    from app.result_shape import is_num

    return is_num(x)


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
    # 🔴 **FAZ 5.15 — KOPYA SİLİNDİ.** Bu blok kendi ortalama/std/z-skorunu satır içi
    # hesaplıyordu; `app/stats.py` tam da bu kopyayı ortadan kaldırmak için yazılmıştı
    # ve dosyanın kendi docstring'i *"yeni bir istatistik motoru İCAT EDİLMEZ"* diyordu.
    # Yani niyet üç yerde yazılıydı ve **bir yerde uygulanmıyordu**.
    #
    # ⚠ Bu, bu deponun **altı kez ölçülmüş** hastalığı: *"anomali işine dokunan her faz
    # bunu tekilleştirmekle yükümlüdür."*
    #
    # ⚠ Şekil farkı korunuyor: `stats` **sayısal kararı** verir (indeks + z), etiket
    # üretimi burada kalır — *paylaşılan şey karar, sunum değil.*
    from app.stats import z_skorlari

    nums = [v for v in vals if v is not None]
    aykiri = z_skorlari(nums, k=k)
    if not aykiri:
        # ⚠ `None` (soru sorulamaz) ile `[]` (soruldu, yok) burada **aynı** sonucu verir
        # ve bu doğrudur: ikisinde de bildirilecek bir ihlal yoktur.
        return []
    # `z_skorlari` **nums** üzerindeki indeksleri döner; satır eşlemesi için `None`
    # atlanan konumlar geri haritalanır.
    ham_indeks = [i for i, v in enumerate(vals) if v is not None]
    z_haritasi = {ham_indeks[i]: z for i, z in aykiri}
    bad: list[str] = []
    for satir_i, (row, v) in enumerate(zip(rows, vals)):
        if v is None or satir_i not in z_haritasi:
            continue
        z = z_haritasi[satir_i]
        if True:
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


#: Bir uyarının nedeni için taranacak en fazla boyut. `/ask`'in 6'sından DAR: bu bir arka
#: plan işidir, kullanıcı beklemiyor ama koşum penceresi (60 sn'lik scheduler döngüsü)
#: paylaşımlı. Her boyut AYRI bir kıyas sorgusu (cari + geçen dönem) demek.
NEDEN_MAX_BOYUT = 2

#: Bildirimde gösterilecek en fazla bulgu. Bir uyarı bir HABERDİR, bir rapor değil.
NEDEN_MAX_BULGU = 3


def uyari_nedeni(svc, cq: dict, threshold: dict | None) -> tuple[list[str], str | None]:
    """Bir uyarının NEDENİNİ üretir: *"ne oldu"* değil *"neyin değişmesi bunu getirdi"*.

    Faz F3 kompozisyonu (`check_alert → contribution → dispatch`). Ölçülen boşluk: bugün
    uyarı ``⚠ fire: eşik ihlali — makine M-07: 45 (> eşik 30)`` diyor ve orada bitiyor.
    Kullanıcı *"neden 45?"* diye sorabileceği bir yere gitmek zorunda kalıyor — oysa
    cevabı üretecek motor (`app/contribution.py`) elimizde duruyor.

    Döner: ``(neden_satirlari, aciklama_notu)``. İkisi de boş olabilir ve bu bir HATA
    DEĞİLDİR: katkı ayrıştırması yalnız TOPLANABİLİR ölçülerde tanımlıdır (bkz.
    `contribution.ayristirilabilir_mi`) — `AVG`/oran/`COUNT(DISTINCT)` için "bu segment
    değişimin %40'ını açıklıyor" cümlesi matematiksel olarak yanlış olur. O durumda
    ayrıştırma YAPILMAZ ve nedeni `not` olarak döner.

    **PII fail-closed.** Segment etiketleri boyut DEĞERLERİNDEN gelir (operatör adı,
    cari unvanı) ve bir bildirimin kime ulaşacağı ÖNCEDEN BİLİNEMEZ — e-posta dağıtım
    listesi, in-app bell, push. Bu yüzden `run_schedule`'ın ana sonuçta uyguladığı
    disiplin burada da geçerlidir: satırlar ayrıştırmadan ÖNCE maskelenir.

    **Tıklanabilir `cube_query` bildirimde TAŞINMAZ.** Maskelenmiş bir değere (`Ahm** Y***`)
    filtre kuran bir sorgu boş döner; kullanıcıya "tıkla" diyip boş sonuç vermek, hiç
    tıklatmamaktan kötüdür. Kanıt yolu bildirimdeki `contract_id`'dir.
    """
    from app import contribution as _contrib
    from app.pii import mask_rows

    olcu = (threshold or {}).get("measure")
    # Uyarı hangi ölçü için kurulduysa ONUN değişimi açıklanır. Sorgunun ilk ölçüsünü
    # varsaymak, çok-ölçülü bir raporda YANLIŞ ölçüyü açıklardı.
    acq = dict(cq)
    if olcu and olcu in (acq.get("measures") or []):
        acq["measures"] = [olcu]

    try:
        out = _contrib.arastir(
            svc, svc.schema(), acq, mode="yoy", kind="segment",
            max_dimensions=NEDEN_MAX_BOYUT,
            # Makbuz YAZILMAZ: koşum zaten kendi kök `contract_id`'sini üretti
            # (aşağıda `contracts.record`) ve boyut başına ikinci bir kayıt, arka plan
            # işinde gürültüdür. `arastir`'ın imzası bunu bilinçli bir seçim yapar.
            kaydet=None,
            satir_donustur=lambda rows: mask_rows(rows)[0])
    except Exception:
        # Nedeni üretememek uyarıyı KIRMAZ: haber yine gider, yalnız gerekçesiz.
        _log.warning("uyarı nedeni üretilemedi (best-effort)", exc_info=True)
        return ([], None)

    raporlar = out.get("raporlar") or []
    if not raporlar:
        return ([], out.get("note"))
    ilk = raporlar[0]
    satirlar = [b["label"] for b in (ilk.get("bulgular") or [])[:NEDEN_MAX_BULGU]]
    # Sessiz kırpma YOK (aynı disiplin `contribution.decompose`'da da var): gösterilmeyen
    # segment sayısı söylenir, yoksa liste "her şey bu kadar" diye okunur.
    kirpilan = len(ilk.get("bulgular") or []) - len(satirlar) + int(ilk.get("kirpilan_segment") or 0)
    ek = []
    if kirpilan > 0:
        ek.append(f"+{kirpilan} segment daha (gösterilmedi, yok sayılmadı)")
    if out.get("taranmayan_boyut"):
        # ADIYLA söylenir: bir sayı ("3 boyut taranmadı") kullanıcıya hangi soruyu
        # sorabileceğini söylemez. Bildirim dar bir yüzey olduğu için ilk üçü yazılır.
        adlar = out.get("taranmayan_adlar") or []
        ek.append(f"{out['taranmayan_boyut']} boyut taranmadı"
                  + (f" ({', '.join(adlar[:3])}{'…' if len(adlar) > 3 else ''})" if adlar else ""))
    return (satirlar, " · ".join(ek) or None)


def run_schedule(state, sched: dict, *, manual: bool = False, principal=None) -> dict:
    """Bir zamanlanmış raporu KOŞAR: **kimlik** → dönem → sorgu → sözleşme → eşik → bildirim.

    `state` = FastAPI app.state (wren, contracts, schedules).

    ⟳ **FAZ 1.1b (2026-08-04) — KİMLİKSİZ KOŞMAZ.** Önceden zamanlayıcı döngüsü bunu
    `principal` olmadan çağırıyordu; `authorize()` **hiç çalışmıyordu** ve zamanlanmış bir
    rapor, sahibinin yetkisi **alındıktan sonra da** koşmaya devam ediyordu. `1.1` yalnız
    **istek yolunu** kapatmıştı — bu, *"istek yolu güvenli, zamanlayıcı yolu açık"*
    asimetrisinin kapanışı.

    `principal` verilmezse kayıttan çözülür (`run_as_user_id` → `created_by`); çözülemezse
    **fail-closed**: iş **koşmaz**. Elle koşumda (`manual=True`) uç kendi principal'ını
    geçer — orada canlı kullanıcı zaten yetkilendirilmiştir.
    """
    from app import cube_router
    from app.arkaplan_kimlik import yetkilendir

    if principal is None:
        from control_plane.db import get_session

        with next(get_session()) as _oturum:                  # type: ignore[call-overload]
            principal = yetkilendir(sched, _oturum)

    svc = _wren_for_schedule(state, sched)
    store: ScheduleStore = state.schedules

    cq = json.loads(json.dumps(sched.get("cube_query") or {}))
    period = str(sched.get("period") or "").strip()
    if period:
        dfs = cube_router.date_filters(cube_router._norm(period), "tarih")
        cq["filters"] = [f for f in cq.get("filters", []) if f.get("dimension") != "tarih"] + dfs

    sql = svc.cube_sql(cq)
    result = svc.query(sql, limit=1000)
    # PII maskeleme (doğrulama turu düzeltmesi, 1 Ağustos 2026): zamanlanmış teslim daha önce
    # HİÇ maskelemiyordu — sonuç doğrudan e-posta/bildirim gövdesine (`channels.NotificationEvent
    # .rows`, aşağıda) giriyordu. Burada `principal=None` KASITLI: bu ANLIK/canlı bir kullanıcı
    # DEĞİL, otomatik bir arka-plan işi — kimin (hangi e-posta alıcısının) göreceği ÖNCEDEN
    # bilinemez, bu yüzden `pii:view` bypass'ı YOK, HER ZAMAN maskelenir (fail-closed). Query
    # Contract kaydı da (aşağıda `contracts.record(..., result=result, ...)`) bu MASKELİ
    # sonucu alır — otomatik işler için ikincil bir sızıntı yüzeyi bırakılmaz.
    from app.pii import mask_query_result

    result, _ = mask_query_result(result, None)

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
    neden: list[str] = []
    neden_not: str | None = None
    if violations:
        kind = "anomaly" if alert_kind == "anomaly" else "alert"
        lead = "olağandışı değerler" if kind == "anomaly" else "eşik ihlali"
        severity = "warning" if kind == "anomaly" else "critical"
        message = (
            f"⚠ {sched.get('label') or sched.get('id')}: {lead} — "
            + "; ".join(violations[:3])
            + (f" (+{len(violations) - 3} satır)" if len(violations) > 3 else "")
        )
        # FAZ F3 — UYARININ NEDENİ. Kompozisyon: `check_alert → contribution → dispatch`.
        # YALNIZ ihlalde koşar: rutin rapor için boyut taraması, kimsenin sormadığı bir
        # soruya para ödemek olurdu (`arastir` maliyet sınıfı "pahali" beyanlı).
        neden, neden_not = uyari_nedeni(svc, cq, sched.get("threshold"))
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
        # NOT (31 Temmuz 2026): "measure_units" YANLIŞ anahtardı — schema() dict'i ölçü
        # birimlerini "units" adıyla taşıyor (bkz. app/wren_service.py:236) — AYNI hata
        # sınıfı /ask, /cube, dashboards.py, report.py'de de vardı (hepsi düzeltildi).
        viz_spec = _viz.recommend(result, cube_query=cq, **_viz.meta_args(_cmeta))
    except Exception:
        pass

    event = channels.NotificationEvent(
        category=kind, severity=severity,
        title=sched.get("label") or sched.get("id") or "Rapor",
        summary=message,
        rows=result.get("rows") or [],
        viz=viz_spec,
        violations=violations,
        neden=neden, neden_not=neden_not,
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
        except KimliksizArkaPlanIsi as exc:
            # 🔴 FAZ 1.1b — SAHİPSİZ İŞ BİR "ESKİ VERİ" DEĞİL, BİR BULGUDUR.
            # Genel `except`e düşürmek onu "tek zamanlama hatası" diye meşrulaştırır ve
            # delik sessizce açık kalırdı. Zamanlamanın adıyla loglanır.
            _log.warning("ARKA PLAN KİMLİĞİ: %s", exc)
            continue
        except Exception:
            continue  # tek zamanlama hatası diğerlerini durdurmasın
    return n


# --- KULLANICININ EŞİKLERİ (Faz G3) ----------------------------------------------
#
# Planın G3 kompozisyonu bir "hedef/eşik kıyası" istiyor. Ölçüldü: cube metadata'sında
# `target:`/`hedef:` diye bir beyan **hiçbir cube'da YOK**. Demo için hedef uydurmak,
# `pvm:` eşleştirmesinde reddedilen şeyin aynısı olurdu — GÜVENLE YANLIŞ bir sayı
# ("hedefin %12 altındasın") ve kimse onu sorgulamaz.
#
# Ama gerçek, BEYAN EDİLMİŞ bir eşik kaynağı zaten var: **kullanıcının kendi kurduğu
# alarmlar**. Kullanıcı `fire_kg > 30` alarmını kurduğunda "benim için kritik sınır bu"
# demiş olur. Bu, uydurulmuş bir hedef değil, kullanıcının kendi ifadesidir.

#: Eşiğe "yaklaşma" oranı: ihlal yoksa bile bu bandın içindeysek uyarılır.
YAKLASMA_ORANI = 0.90


def kullanicinin_esikleri(store, cube: str | None, olculer: list[str] | None,
                          *, tenant_id: str | None = None) -> list[dict]:
    """Bu cube+ölçü için kullanıcının kurduğu SABİT eşikler (anomali alarmları hariç).

    Anomali alarmları (`method=zscore`) dışarıda: onlar bir SINIR değil, baseline'dan
    öğrenen bir istatistiktir — `interpret._signals`'ın anomali dalı zaten aynı motoru
    (`detect_anomalies`) koşuyor ve ikisini karıştırmak aynı şeyi iki kez söylerdi.
    """
    if not cube or not olculer:
        return []
    try:
        tanimlar = store.list()
    except Exception:
        _log.warning("eşik kıyası: zamanlama listesi okunamadı (best-effort)", exc_info=True)
        return []
    olcu_kumesi = set(olculer)
    out: list[dict] = []
    for s in tanimlar:
        if not s.get("enabled", True):
            continue
        if tenant_id and s.get("tenant_id") and s["tenant_id"] != tenant_id:
            continue
        th = s.get("threshold") or {}
        if not th.get("measure") or th.get("measure") not in olcu_kumesi:
            continue
        if str(th.get("method", "")) in ("zscore", "anomali", "anomaly"):
            continue
        if (s.get("cube_query") or {}).get("cube") != cube:
            continue
        try:
            float(th.get("value"))
        except (TypeError, ValueError):
            continue
        out.append({"measure": th["measure"], "op": str(th.get("op", "gt")),
                    "value": float(th["value"]), "label": s.get("label") or s.get("id")})
    return out


def esik_sinyalleri(rows: list[dict], esikler: list[dict],
                    units: dict[str, str] | None = None) -> list[dict]:
    """Kullanıcının eşiklerine göre PROAKTİF sinyaller (`interpret._signals` biçiminde).

    İki durum bildirilir, üçüncüsü **bilinçle susar**:
      * **ihlal** → `critical`. Gövdeyi `check_threshold` üretir (aynı kural iki yerde
        yaşamasın: alarm koşumu ile ekrandaki uyarı AYNI matematiği kullanmalı, yoksa
        e-postada uyarı gelirken ekranda gelmeyen bir gün olur).
      * **yaklaşma** → `warning`. Eşiği aşmadan haber vermek, ürünün "reaktif değil
        proaktif" vaadinin (öz #6) en ucuz karşılığıdır.
      * **rahat** → SUSAR. "Eşiğin %40 altındasın" her cevaba eklenirse sinyal gürültüye
        döner ve asıl uyarılar okunmaz olur.

    Yaklaşma yalnız `value > 0` için hesaplanır. Negatif ya da sıfır eşikte "yüzde olarak
    yaklaşmak" tanımsızdır (0'a %90 yaklaşmak nedir?) — tanımsız bir sayı üretmektense
    sinyal verilmez; `contribution`ın `net_pay = None` disiplininin aynısı.
    """
    if not rows or not esikler:
        return []
    units = units or {}
    out: list[dict] = []
    for e in esikler:
        m, op, val = e["measure"], e["op"], e["value"]
        ihlaller = check_threshold({"measure": m, "op": op, "value": val}, {"rows": rows})
        birim = units.get(m)
        if ihlaller:
            out.append({
                "severity": "critical", "kind": "threshold",
                "text": (f"Kendi eşiğini aşıyor ({e['label']}: {m} "
                         f"{'>' if op.startswith('g') else '<'} {_ile_birim(_fmt_deger(val), birim)}) — "
                         + "; ".join(ihlaller[:2])
                         + (f" (+{len(ihlaller) - 2} satır)" if len(ihlaller) > 2 else ""))})
            continue
        if val <= 0:
            continue
        degerler = [float(r[m]) for r in rows if _is_sayi(r.get(m))]
        if not degerler:
            continue
        if op.startswith("g"):
            uc = max(degerler)
            yakin = uc >= val * YAKLASMA_ORANI
        else:
            uc = min(degerler)
            yakin = uc <= val / YAKLASMA_ORANI
        if yakin:
            out.append({
                "severity": "warning", "kind": "threshold",
                "text": (f"Eşiğine yaklaşıyor ({e['label']}: {m} "
                         f"{'>' if op.startswith('g') else '<'} {_ile_birim(_fmt_deger(val), birim)}) — "
                         f"şu an {_ile_birim(_fmt_deger(uc), birim)}")})
    return out
