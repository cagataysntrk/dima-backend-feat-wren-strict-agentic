"""Query Contract + Replay (ADR-0010) — her raporun kanıt kaydı.

UpcyBrain'in QueryContract deseninin CubeQuery-natif hali: her başarılı rapor,
soru + CubeQuery + üretilen SQL + SONUÇ HASH'İ + şema sürümü ile mühürlenir ve
`GET /contracts/{id}/replay` ile yeniden oynatılabilir. Üç seviyeli teşhis:

    sonuç hash'i aynı  → AYNI (birebir doğrulandı)
    SQL aynı, hash farklı → VERİ DEĞİŞTİ (motor masum; kaynağa kayıt girmiş)
    SQL farklı            → TANIM DEĞİŞTİ (cube/şema evrimi — CubeQuery yeniden derlendi)

CubeQuery IR sözleşmelendiği için şema evrildiğinde bile "aynı soru bugünkü
şemada ne verirdi" cevaplanabilir (SQL-sözleşmeden daha güçlü). Depo TEK-KAYNAK
Postgres (`contract_log`).

DAYANIKLILIK (audit deseni, kullanıcı 2026-07-29): contract = raporun KANITI →
DB-down'da kaybolmamalı. Yol: DB'ye yaz → DB down ise `logs/contract-spool.jsonl`'e
ekle → `replay_spool()` startup'ta boşaltır. Contract'ın PK'sı SABİT (`cid`)
olduğundan replay `merge()` (upsert) ile IDEMPOTENT — audit'ten farklı olarak
çift-kayıt bile olmaz. Fail-closed DEĞİL: kanıt (raporun kendisi değil) olduğundan
disk+DB birlikte patlarsa raporu düşürmek yerine cid dönülür (kayıp yalnız bu uç).
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime

from app.config import BASE_DIR

_log = logging.getLogger("dima.contracts")
_SPOOL_PATH = BASE_DIR / "logs" / "contract-spool.jsonl"


def _row_from_payload(p: dict):
    """Payload → ContractLog (DB insert / spool replay ORTAK yolu; ts korunur)."""
    from control_plane.models import ContractLog
    return ContractLog(
        id=p["id"], session_id=p.get("session_id"), tenant_id=p.get("tenant_id"),
        question=p.get("question"), cube_query_json=p.get("cube_query_json"),
        sql=p.get("sql"), result_hash=p.get("result_hash"), row_count=p.get("row_count"),
        schema_version=p.get("schema_version"), source=p.get("source"),
        provenance_json=p.get("provenance_json"),
        ts=datetime.fromisoformat(p["ts"]) if p.get("ts") else datetime.utcnow())


def _persist(row) -> None:
    """merge() = PK (cid) varsa UPDATE, yoksa INSERT → replay idempotent (çift-kayıt yok)."""
    from sqlmodel import Session

    from control_plane.db import engine
    with Session(engine) as s:
        s.merge(row)
        s.commit()


def _spool_append(payload: dict) -> None:
    _SPOOL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _SPOOL_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")


def replay_spool() -> int:
    """Startup'ta spool'daki bekleyen contract'ları DB'ye boşaltır (boşaltılan sayı döner).
    Boşaltılamayanlar (DB hâlâ down) dosyada KALIR → sonraki startup'ta yeniden denenir.
    merge() sayesinde idempotent: aynı satır iki kez replay edilse bile çift-kayıt olmaz."""
    if not _SPOOL_PATH.exists():
        return 0
    try:
        lines = _SPOOL_PATH.read_text(encoding="utf-8").splitlines()
    except Exception:
        return 0
    remaining: list[str] = []
    flushed = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            _persist(_row_from_payload(json.loads(line)))
            flushed += 1
        except Exception:
            remaining.append(line)  # DB hâlâ yazılamıyor → sakla, sonra dene
    try:
        if remaining:
            _SPOOL_PATH.write_text("\n".join(remaining) + "\n", encoding="utf-8")
        else:
            _SPOOL_PATH.unlink()
    except Exception:
        pass
    if flushed:
        _log.info("contract spool boşaltıldı: %d kayıt DB'ye yazıldı", flushed)
    return flushed


def result_hash(result: dict | None) -> str | None:
    """Sonucun kanonik özeti — SIRA-BAĞIMSIZ küme eşitliği.

    ORDER BY'sız sorgularda motor satırları her koşumda farklı sırada döndürebilir
    (hash aggregate); sözleşmenin sorusu "SAYILAR değişti mi"dir, sunum sırası değil.
    Satırlar kanonik JSON temsilleriyle sıralanıp öyle hash'lenir."""
    if not result:
        return None
    rows = sorted(
        json.dumps(r, sort_keys=True, ensure_ascii=False, default=str)
        for r in result.get("rows") or []
    )
    payload = {"columns": result.get("columns"), "rows": rows}
    s = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return "sha256:" + hashlib.sha256(s.encode()).hexdigest()


# CubeQuery'nin AKIŞ bayrakları — sorunun ANLAMINI değiştirmezler, yalnız UI/merdiven
# durumunu taşırlar. Kimliğe girerlerse "dönem chip'ine tıklamadan önce" ve "tıkladıktan
# sonra" AYNI sorgu FARKLI hash alır; oysa üretilen SQL birebir aynıdır.
_NONSEMANTIC_KEYS = frozenset({"period_confirmed"})


def _strip_nonsemantic(v):
    if isinstance(v, dict):
        return {k: _strip_nonsemantic(x) for k, x in v.items() if k not in _NONSEMANTIC_KEYS}
    if isinstance(v, list):
        return [_strip_nonsemantic(x) for x in v]
    return v


def cube_query_hash(cube_query: dict | None, *, mdl_version: str | None = None,
                    company: str | None = None, tenant_id: str | None = None) -> str:
    """CubeQuery'nin KANONİK KİMLİĞİ (Faz 4.3).

    Sözleşme: **aynı hash ⇒ aynı ÇIKTI** (aynı sayılar DEĞİL — aynı tablo: kolonlar,
    sıraları ve satırlar). Bu, `result_hash`ten farklı bir sözleşmedir ve fark bilinçlidir:
    `result_hash` "sayılar değişti mi" diye sorar ve sunum sırasını umursamaz; bu fonksiyon
    ise bir CACHE ANAHTARI olabilecek kadar sıkı olmak zorundadır.

    Bundan çıkan kanonikleştirme kuralları:
      - `filters` **sıraya duyarsız** — saf AND birleşimidir, çıktıya hiçbir etkisi yoktur.
        `in`/`not_in` değer listeleri de sıralanır (`[Beyaz,Siyah]` ≡ `[Siyah,Beyaz]`).
      - `measures` / `dimensions` **sıraya DUYARLI** — kolon sırasını ve GROUP BY sırasını
        (dolayısıyla satır sırasını) belirlerler. Sıralanmış olsalardı `[a,b]` için
        önbelleğe alınan sonuç `[b,a]` sorgusuna kolonları TERS sırada döndürülürdü.
      - Akış bayrakları (`period_confirmed`) düşürülür — bkz. `_NONSEMANTIC_KEYS`.
      - `mdl_version`, `company`, `tenant_id` kimliğe **girer**: şema değişince aynı
        CubeQuery başka bir şey ifade eder, ve iki kiracının aynı sorgusu ASLA aynı
        anahtara düşmemelidir.

    Neden bugün bir cevap cache'i KURULMADI: tekrar oranı ÖLÇÜLMEDİ (`interaction_log`
    telemetrisi yeni kalıcı oldu, veri birikmedi). Ölçülmemiş bir ihtiyaç için altyapı
    kurulmaz. Bu fonksiyon cache için değil, ZATEN ihtiyaç duyulan yerler için vardır:
    sözleşme kimliği, terfi kuyruğu tekilleştirmesi, "aynı sorgu mu" karşılaştırması —
    ve biri cache eklemek isterse doğru anahtar hazır olsun diye.
    """
    cq = _strip_nonsemantic(cube_query or {})
    fs = cq.get("filters")
    if isinstance(fs, list):
        duz = []
        for f in fs:
            f = dict(f) if isinstance(f, dict) else f
            if isinstance(f, dict) and isinstance(f.get("value"), list):
                f["value"] = sorted(
                    f["value"],
                    key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False, default=str))
            duz.append(f)
        cq["filters"] = sorted(
            duz,
            key=lambda f: json.dumps(f, sort_keys=True, ensure_ascii=False, default=str))
    payload = {"cq": cq, "mdl": mdl_version, "company": company, "tenant": tenant_id}
    s = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                   separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(s.encode()).hexdigest()


def _norm_sql(sql: str | None) -> str:
    return " ".join((sql or "").split()).rstrip(";").lower()


def sql_equal(a: str | None, b: str | None) -> bool:
    return _norm_sql(a) == _norm_sql(b)


class ContractStore:
    """Query Contract deposu — TEK-KAYNAK DB (`contract_log`). contracts.jsonl kaldırıldı:
    volume dosyası tek-servis → admin plane (AYRI servis) replay/denetim için okuyamıyordu +
    managed backup yok + partial-write riski. Kanıt Postgres'te (admin-erişilir, yedekli)."""

    def _session(self):
        from sqlmodel import Session

        from control_plane.db import engine
        return Session(engine)

    def record(
        self,
        *,
        session_id: str | None,
        question: str,
        cube_query: dict | None,
        sql: str | None,
        result: dict | None,
        source: str | None,
        schema_version: str,
        tenant_id: str | None = None,
        provenance: dict | None = None,
    ) -> str:
        cid = "c-" + uuid.uuid4().hex[:10]
        # Alanlar bir kez çözülür → DB satırı ve spool payload'ı AYNI kaynaktan (ts + hash
        # dahil). Ham SONUÇ spool'lanmaz; yalnız result_hash (KVKK + boyut) — audit deseni.
        payload = {
            "id": cid, "session_id": session_id, "tenant_id": tenant_id, "question": question,
            "cube_query_json": (json.dumps(cube_query, ensure_ascii=False) if cube_query else None),
            "sql": sql, "result_hash": result_hash(result),
            "row_count": (result or {}).get("row_count"),
            "schema_version": schema_version, "source": source,
            # KÖKEN (Faz D2): hangi kırılım hangi join'den geldi ve o join ÖLÇÜLDÜ mü.
            # `None` ile `{}` farklı: `None` = ilişki-türevi boyut KULLANILMADI.
            "provenance_json": (json.dumps(provenance, ensure_ascii=False)
                                if provenance else None),
            "ts": datetime.utcnow().isoformat(),
        }
        try:
            _persist(_row_from_payload(payload))
        except Exception as db_exc:
            # DB down → dayanıklı spool: kanıt kaybolmaz, replay_spool() startup'ta boşaltır.
            try:
                _spool_append(payload)
                _log.warning("contract DB'ye yazılamadı, spool'a alındı: %s", db_exc)
            except Exception:
                # Disk+DB birlikte patladı → kanıt kaybı YALNIZ bu uçta; rapor yine döner
                # (fail-closed DEĞİL: contract raporun kendisi değil, kanıtı).
                _log.warning("contract DB VE spool yazılamadı (kanıt kaybı)", exc_info=True)
        return cid

    def record_v2_minimum(
        self,
        *,
        session_id: str | None,
        question: str,
        cube_query: dict,
        sql: str,
        result: dict,
        schema_version: str,
        tenant_id: str | None,
        provenance: dict,
    ) -> dict:
        """Persist one immutable Day-3 execution contract and report real durability.

        Legacy record() intentionally stays best-effort and is not changed. V2 needs a
        stronger answer: an execution may be called official only after its evidence is
        durably written either to the primary DB or to the existing replay spool.
        """
        cid = "c-" + uuid.uuid4().hex[:10]
        rhash = result_hash(result)
        payload = {
            "id": cid,
            "session_id": session_id,
            "tenant_id": tenant_id,
            "question": question,
            "cube_query_json": json.dumps(cube_query, ensure_ascii=False),
            "sql": sql,
            "result_hash": rhash,
            "row_count": result.get("row_count"),
            "schema_version": schema_version,
            "source": "v2_standard",
            "provenance_json": json.dumps(
                provenance,
                ensure_ascii=False,
                default=str,
                sort_keys=True,
            ),
            "ts": datetime.utcnow().isoformat(),
        }

        try:
            _persist(_row_from_payload(payload))
            return {
                "id": cid,
                "result_hash": rhash,
                "durability": "db",
                "sealed": True,
            }
        except Exception as db_exc:
            try:
                _spool_append(payload)
                _log.warning(
                    "V2 minimum contract DB'ye yazılamadı, spool'a alındı: %s",
                    db_exc,
                )
                return {
                    "id": cid,
                    "result_hash": rhash,
                    "durability": "spool_pending",
                    "sealed": True,
                }
            except Exception:
                _log.warning(
                    "V2 minimum contract DB VE spool yazılamadı — official seal yok",
                    exc_info=True,
                )
                return {
                    "id": cid,
                    "result_hash": rhash,
                    "durability": "none",
                    "sealed": False,
                }

    @staticmethod
    def _visible_row(r, tenant_id: str | None, include_legacy: bool) -> bool:
        """Tenant-RLS: kayıt sahibinin tenant'ı eşleşmeli. tenant_id'siz (RLS-öncesi)
        kayıtlar yalnız aktif şirketin tenant'ına görünür (include_legacy)."""
        if r.tenant_id is None:
            return include_legacy
        return r.tenant_id == tenant_id

    def _row_to_dict(self, r) -> dict:
        return {
            "id": r.id, "ts": r.ts.isoformat() if r.ts else None, "session": r.session_id,
            "tenant_id": r.tenant_id, "question": r.question,
            "cube_query": json.loads(r.cube_query_json) if r.cube_query_json else None,
            "sql": r.sql, "result_hash": r.result_hash, "row_count": r.row_count,
            "schema_version": r.schema_version, "source": r.source,
        }

    def get(self, cid: str, tenant_id: str | None = None,
            include_legacy: bool = True) -> dict | None:
        try:
            from sqlmodel import select

            from control_plane.models import ContractLog
            with self._session() as s:
                r = s.exec(select(ContractLog).where(ContractLog.id == cid)).first()
            if r is None:
                return None
            if tenant_id is not None and not self._visible_row(r, tenant_id, include_legacy):
                return None  # başka tenant'ın kaydı: varlığı da sızmaz (404 gibi)
            return self._row_to_dict(r)
        except Exception:
            _log.warning("contract okunamadı", exc_info=True)
            return None

    def recent(self, limit: int = 20, tenant_id: str | None = None,
               include_legacy: bool = True) -> list[dict]:
        try:
            from sqlmodel import col, select

            from control_plane.models import ContractLog
            with self._session() as s:
                # RLS sonrası limit'i doldurabilmek için fazladan çek (headroom)
                rows = s.exec(select(ContractLog)
                              .order_by(col(ContractLog.ts).desc())
                              .limit(max(limit * 3, limit))).all()
            items = [r for r in rows
                     if tenant_id is None or self._visible_row(r, tenant_id, include_legacy)]
            return [
                {k: self._row_to_dict(r).get(k)
                 for k in ("id", "ts", "session", "question", "row_count", "source")}
                for r in items[:limit]
            ]
        except Exception:
            _log.warning("contract listesi okunamadı", exc_info=True)
            return []

    def find_previous(self, cube_query: dict | None, *, tenant_id: str | None = None,
                      mdl_version: str | None = None,
                      company: str | None = None) -> dict | None:
        """FAZ 5.13a — **HAYALET SERİ**: aynı sorgunun **bir önceki** koşumu.

        🔴 **Sıfır yeni motor.** `cube_query_hash()` zaten var ve sözleşmesi tam da
        buydu: *aynı hash ⇒ aynı ÇIKTI*. Bu metot o anahtarla geçmişe bakar.

        ⚠ **`result` DÖNMEZ, `result_hash` ve `row_count` döner.** Ham sonuç zaten
        spool'lanmıyor (KVKK + boyut, `record`'un kendi kararı) ve onu burada uydurmak
        olmayan bir veriyi varmış gibi göstermek olurdu. *Hayalet seri bir
        KARŞILAŞTIRMA sinyalidir, ikinci bir cevap değil.*

        ⚠ Tenant-RLS: başka bir kiracının koşumu **hiç görünmez** — `cube_query_hash`
        `tenant_id`yi kimliğe katıyor, ama filtre yine de **açıkça** uygulanır.
        *Bir gizlilik sınırını tek bir hash'in içine gömmek, onu görünmez kılar.*
        """
        if not cube_query:
            return None
        try:
            from sqlmodel import select

            from control_plane.models import QueryContract
        except Exception:                                    # noqa: BLE001
            return None
        anahtar = cube_query_hash(cube_query, mdl_version=mdl_version,
                                  company=company, tenant_id=tenant_id)
        try:
            with self._session() as ses:
                sorgu = select(QueryContract).order_by(QueryContract.ts.desc())
                if tenant_id is not None:
                    sorgu = sorgu.where(QueryContract.tenant_id == tenant_id)
                for r in ses.exec(sorgu.limit(200)):
                    cq = None
                    try:
                        cq = json.loads(getattr(r, "cube_query_json", None) or "null")
                    except Exception:                        # noqa: BLE001
                        continue
                    if not cq:
                        continue
                    if cube_query_hash(cq, mdl_version=mdl_version, company=company,
                                       tenant_id=tenant_id) == anahtar:
                        return {"contract_id": r.id,
                                "ts": r.ts.isoformat() if r.ts else None,
                                "row_count": getattr(r, "row_count", None),
                                "result_hash": getattr(r, "result_hash", None)}
        except Exception:                                    # noqa: BLE001
            # ⚠ Hayalet seri bir **ek**tir: bulunamaması cevabı düşürmez.
            return None
        return None
