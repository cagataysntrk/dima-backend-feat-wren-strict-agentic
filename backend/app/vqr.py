"""Verified Query Repository (A#4 / literatür önerisi #2 — Snowflake VQR deseni).

Onaylı soru→çift saklanır ve üç yolla kullanılır:
1. BİREBİR eşleşme → LLM'siz deterministik tekrar oynatma ("doğrulanmış" — en yüksek güven).
2. Top-k benzer çift → LLM select/generation prompt'una FEW-SHOT (DAIL-SQL ana kazancı).
3. Chip/verify-onaylı cevaplar depoya GERİ yazılır → sistem sora sora öğrenir.

Çift iki şekilden biri olabilir (bkz. ``store``/``few_shot_block``): eski hibrit yoldan
CubeQuery, ya da strict-agentic ``/ask`` yolundan ``{"wren_sql": "..."}``. VQR ikisini de
opak JSON olarak taşır — hangi şekil olduğunu yalnız üst katman (routers/ask.py) bilir.

Çiftler Postgres'te yaşar (verified_query tablosu, şirket kapsamlı) — eskiden
companies/<şirket>/verified/queries.jsonl'daydı ama Railway volume dışı olduğundan
redeploy'da siliniyordu (ADR-0005/0008). Başlangıçta belleğe yüklenir; retrieval RAM'de.
Dönem filtreleri SAKLANMAZ: sorgu ŞEKLİ öğrenilir, dönem her mesajdan yeniden çözülür.

Embedding: multilingual-e5-LARGE (fastembed/ONNX; TR retrieval'da MiniLM'den +10 puan
— bkz. docs/research/turkce-llm-embedding-raporu.md; fastembed e5-small'ı desteklemiyor,
bkz. `_embedder()`). ~2.2 GB indirir → `DIMA_VQR_EMBEDDER=off` ile tamamen kapatılabilir
(testler bunu kullanır; gerekçe config.py). e5 kuralı: simetrik soru→soru
eşlemede İKİ tarafa da "query: " öneki. Model yoksa F5-token sözlüksel fallback
(Can et al.: ilk-5-karakter kökleme ≈ tam lemmatizer) — testler deterministik kalır.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime

from app.llm import _norm
from app.logging_setup import get_logger

_log = get_logger("vqr")

_EXACT_THRESHOLD = 0.92  # embedding kosinüsü için birebir-sayılma eşiği
_LEX_EXACT_THRESHOLD = 0.85  # sözlüksel fallback daha kaba → daha yüksek eşik

_emb_lock = threading.Lock()
_emb_model = None
_emb_tried = False


def _embedder():
    """fastembed e5-small (lazy). Kurulu/indirilebilir değilse None → sözlüksel fallback.

    Canlı bulgu (1 Ağustos 2026): ONNX model dosyası ~1GB+ ve HF Hub'dan kimliksiz
    (HF_TOKEN'sız) indirme YAVAŞ/oranlanmış olabiliyor (bkz. fastembed'in kendi uyarısı).
    ÖNCEDEN bu fonksiyon `with _emb_lock:` (BLOKLAYAN kilit) kullanıyordu — `main.py`'nin
    arka-plan ısıtma thread'i (`_warm(_embedder)`) indirme SÜRERKEN gerçek bir kullanıcı
    isteği de `_embedder()`'ı çağırırsa, o istek thread'i indirme BİTENE KADAR (dakikalarca)
    SONSUZ BEKLİYORDU — hiçbir zaman timeout/hata OLMADAN (`requests`/`fastembed`'in kendi
    ağ çağrılarında bir üst-sınır yok). Kullanıcıya "LLM'e istek hiç gitmiyor, internal
    server hatası" olarak görünüyordu (aslında istek LLM'e ULAŞAMADAN, VQR embedder'da
    asılı kalıyordu). Düzeltme: kilit NON-BLOCKING denenir — biri ZATEN indiriyorsa
    (ör. arka-plan ısıtması), bu çağrı BEKLEMEDEN `None` döner (mevcut sözlüksel fallback
    YOLU zaten buna göre tasarlı, bkz. `_scores()`/`near_exact()`) — model hazır olunca
    (`_emb_tried` True + `_emb_model` set) sonraki TÜM çağrılar hızlı yoldan (kilitsiz)
    döner. Tek indiren thread garantisi KORUNUR (yalnız kilidi TUTAN thread indirir)."""
    global _emb_model, _emb_tried
    if _emb_tried:
        return _emb_model
    # AÇIK KAPATMA ANAHTARI (`DIMA_VQR_EMBEDDER=off`, bkz. config.py gerekçesi): indirme
    # HİÇ denenmez. Testler bunu kullanır — non-blocking kilit yalnız İKİNCİ thread'i korur,
    # indiren thread'in kendisinde timeout YOKTUR, dolayısıyla ağa bağımlı bir test paketi
    # süresiz asılabilir (ölçüldü). `_emb_tried` işaretlenir → sonraki çağrılar hızlı yoldan.
    from app.config import get_settings

    if str(get_settings().vqr_embedder).strip().lower() == "off":
        _emb_tried = True
        _emb_model = None
        _log.info("vqr embedder kapalı (DIMA_VQR_EMBEDDER=off) → sözlüksel fallback")
        return None
    if not _emb_lock.acquire(blocking=False):
        return None  # başka bir thread (ör. başlangıç ısıtması) zaten indiriyor — BEKLEME
    try:
        if _emb_tried:
            return _emb_model
        _emb_tried = True
        try:
            from fastembed import TextEmbedding

            # fastembed e5-small'ı desteklemiyor; e5-LARGE TR retrieval'da zaten en iyi
            # (TR-MTEB 60.6 nDCG@10). İlk kullanımda ONNX indirir (lazy, thread-safe).
            _emb_model = TextEmbedding("intfloat/multilingual-e5-large")
        except Exception as exc:
            # ADR-0020: sessiz yutma YOK. Fallback meşru bir yol ama SEBEBİ görünmeli —
            # "neden benzer sorular eşleşmiyor" sorusunun cevabı çoğu zaman burasıdır.
            _emb_model = None
            _log.warning("vqr embedder yüklenemedi (%s: %s) → sözlüksel fallback",
                         type(exc).__name__, exc)
        return _emb_model
    finally:
        _emb_lock.release()


def _tokens(text: str) -> set[str]:
    import re

    return {w for w in re.findall(r"[a-z]+", _norm(text)) if len(w) >= 2}


def _tok_match(x: str, y: str) -> bool:
    """TR çekim toleransı: önek ilişkisi ("var"⊂"vardı") YA DA ≥4 karakter ortak kök
    ("renkte"~"renklerde" → "renk"). Can et al. F5 fikrinin önek-esnek hali."""
    if x.startswith(y) or y.startswith(x):
        return True
    lcp = 0
    for cx, cy in zip(x, y):
        if cx != cy:
            break
        lcp += 1
    return lcp >= 4


def _lex_score(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    ma = sum(1 for x in ta if any(_tok_match(x, y) for y in tb))
    mb = sum(1 for y in tb if any(_tok_match(y, x) for x in ta))
    return (ma + mb) / (len(ta) + len(tb))  # Dice-benzeri, çekime dayanıklı


def _strip_dates(cq: dict) -> dict:
    out = json.loads(json.dumps(cq))
    if "filters" in out:
        out["filters"] = [f for f in out["filters"] if f.get("dimension") != "tarih"]
        if not out["filters"]:
            out.pop("filters")
    return out


# --- GÜVEN KAPISI (Faz 4.1) ----------------------------------------------------
# TEKRAR OYNATMA (`near_exact`) ile ÖRNEK GÖSTERME (`few_shot_block`) AYNI RİSKTE DEĞİLDİR
# ve bu yüzden aynı kapıdan geçmezler:
#
#   replay   → saklanan SQL'i BİREBİR, yeniden doğrulanmadan, üstelik BENZER (birebir değil;
#              eşik 0,92 embedding / 0,85 sözlüksel) bir soru için çalıştırır. Kullanıcı
#              cevabı `source="vqr"` rozetiyle görür. Blast radius: TAM.
#   few-shot → bir ÜRETECE örnek verir; üretecin çıktısı ayrıca doğrulanır. Blast radius:
#              dolaylı.
#
# Bulunan kusur (2 Ağustos 2026, ask.py:2320): başarılı HER bağımsız Discovery cevabı, ham
# LLM SQL'iyle birlikte incelenmeden VQR'a yazılıyordu ve `near_exact` kaynağa BAKMIYORDU —
# yani LLM'in kendi tahmini, insan onaylı bir kayıtla AYNI otoriteyle tekrar oynatılıyordu.
# Ham SQL semantik katmanın yönetmediği kolonlara/filtrelere erişebilir ve `always_filter`
# baypası (MIMARI.md §6.3) bu yolla ÖĞRENİLMİŞ hale gelir. Planın alıntıladığı Snowflake
# uyarısı tam bu vakadır: *kötü kayıt doğruluğu aktif olarak düşürür.*
#
# `auto_cube` GÜVENİLİRDİR çünkü orada saklanan şey LLM'in serbest metni değil, katalogla
# doğrulanmış bir CubeQuery'den derlenmiş SQL'dir (`parse_cube_query` + `dry_plan`).
_TRUSTED_SOURCES = frozenset({
    "user",            # elle/küratörlü çift (makine yazımı değil)
    "user_verified",   # insan ✓ verdi
    "chip_approved",   # insan chip'e tıklayarak onayladı
    "auto_cube",       # Intent-JSON → katalogla doğrulanmış CubeQuery → derlenmiş SQL
})
_UNTRUSTED_SOURCES = frozenset({
    "auto_discovery",  # ham LLM SQL'i, HİÇ incelenmedi
    "auto",            # ayrım ÖNCESİ eski kayıt — kökeni kayıtta YOK, bir kısmı ham SQL
})

# İzin listesi (deny-list değil) BİLİNÇLİ bir güvenlik tercihi: yarın eklenecek bir
# `auto_<birşey>` kaynağı sessizce GÜVENİLİR sayılmasın. Bedeli, yeni bir kaynak adının
# sessizce ENGELLENMESİ — `tests/test_vqr_guven_kapisi.py::test_her_kaynak_SINIFLANDIRILMIS`
# bunu yakalar: koddaki her `source=` literali iki kümeden birinde olmak zorunda.
KNOWN_SOURCES = _TRUSTED_SOURCES | _UNTRUSTED_SOURCES


def is_trusted(source: str | None) -> bool:
    """Bu kayıt TEKRAR OYNATILABİLİR mi? (Örnek gösterme ayrı kapıdan geçer.)"""
    return (source or "") in _TRUSTED_SOURCES


class VQR:
    def __init__(self, company: str, tenant_id: str | None = None):
        # Kapsam: şirket (settings.company). Çiftler Postgres'te yaşar (verified_query),
        # başlangıçta BİR KEZ belleğe yüklenir; retrieval RAM'de (embedding matrisi).
        self.company = company
        self.tenant_id = tenant_id
        self._lock = threading.Lock()
        self._pairs: list[dict] | None = None
        self._vecs = None  # embedding matrisi (pairs ile hizalı) — lazy

    # -- storage (Postgres; DB erişilemezse VQR pasif/advisory — akış kırılmaz) -----
    def _session(self):
        from sqlmodel import Session

        from control_plane.db import engine
        return Session(engine)

    def _load(self) -> list[dict]:
        """Şirket kapsamındaki SİLİNMEMİŞ çiftleri bir kez belleğe yükler."""
        if self._pairs is None:
            pairs: list[dict] = []
            try:
                from sqlmodel import col, select

                from control_plane.models import VerifiedQuery
                with self._session() as s:
                    rows = s.exec(
                        select(VerifiedQuery)
                        .where(VerifiedQuery.company == self.company,
                               col(VerifiedQuery.deleted_at).is_(None))
                        .order_by(col(VerifiedQuery.created_at))
                    ).all()
                for r in rows:
                    try:
                        pairs.append({"question": r.question,
                                      "cube_query": json.loads(r.cube_query_json),
                                      "source": r.source})
                    except Exception:
                        continue
            except Exception:
                _log.warning("VQR DB yüklenemedi (pasif — advisory)", exc_info=True)
                pairs = []
            self._pairs = pairs
        return self._pairs

    def store(self, question: str, payload: dict, source: str = "user",
              extra: dict | None = None) -> bool:
        """Çifti ekler. Aynı norm-soru varsa günceller.

        ``payload`` iki şekilden biri olabilir:
        - CubeQuery (``{"cube": ..., "measures": [...], ...}``) — dönem filtresi düşülür
          (sorgu ŞEKLİ öğrenilir).
        - Wren SQL sarmalayıcı (``{"wren_sql": "SELECT ..."}``) — strict-agentic /ask
          akışının doğrulanmış SQL'i; olduğu gibi saklanır (tarih genelde SQL'in
          içindedir, ayrıca düşürülemez).

        ``extra``: kayda eklenecek kimlik/iz alanları (ör. verified_by, tenant_id) —
        kim doğrulamış görünür olsun (KVKK erişim izi + küratörlük)."""
        q = (question or "").strip()
        if not q or not payload:
            return False
        if q.lower().startswith("chip:"):
            return False  # chip etiketleri soru değildir
        cq = _strip_dates(payload) if payload.get("cube") else dict(payload)
        meta = {k: v for k, v in (extra or {}).items() if v is not None}
        qn = _norm(q)
        with self._lock:
            pairs = self._load()
            for p in pairs:
                if _norm(p["question"]) == qn:
                    p["cube_query"] = cq
                    p["source"] = source
                    break
            else:
                pairs.append({"question": q, "cube_query": cq, "source": source})
            self._vecs = None  # indeks bayatladı
            self._db_upsert(q, qn, cq, source, meta)
        return True

    def _db_upsert(self, question: str, qn: str, cq: dict, source: str, meta: dict) -> None:
        """Çifti verified_query'ye upsert eder (norm-soru + şirket ile tekil). Bellek zaten
        güncel — DB yazımı best-effort (hata akışı düşürmez, warning'e yazar)."""
        try:
            from sqlmodel import col, select

            from control_plane.models import VerifiedQuery
            cj = json.dumps(cq, ensure_ascii=False)
            vby = str(meta["verified_by"]) if meta.get("verified_by") else None
            tid = str(meta["tenant_id"]) if meta.get("tenant_id") else self.tenant_id
            with self._session() as s:
                row = s.exec(select(VerifiedQuery).where(
                    VerifiedQuery.company == self.company,
                    VerifiedQuery.question_norm == qn,
                    col(VerifiedQuery.deleted_at).is_(None))).first()
                # `verified_at` yalnız İNSAN onayında damgalanır (Faz 4.1) — otomatik
                # yazımlar bir doğrulama DEĞİLDİR ve öyleymiş gibi görünmemelidir.
                vat = datetime.utcnow() if source in ("user_verified", "chip_approved") else None
                if row:
                    row.cube_query_json = cj
                    row.source = source
                    row.updated_at = datetime.utcnow()
                    if vby:
                        row.verified_by = vby
                    if tid:
                        row.tenant_id = tid
                    if vat:
                        row.verified_at = vat
                else:
                    row = VerifiedQuery(company=self.company, tenant_id=tid, question=question,
                                        question_norm=qn, cube_query_json=cj, source=source,
                                        verified_by=vby, verified_at=vat)
                s.add(row)
                s.commit()
        except Exception:
            _log.warning("VQR DB yazılamadı (bellek güncel, best-effort)", exc_info=True)

    def remove(self, question: str) -> bool:
        """Çifti depodan çıkarır (geri alma / "✗ yanlış" geri bildirimi).
        Norm-eşit soru + yakın-eşleşme (near_exact) hedeflenir."""
        q = (question or "").strip()
        if not q:
            return False
        with self._lock:
            pairs = self._load()
            qn = _norm(q)
            keep = [p for p in pairs if _norm(p["question"]) != qn]
            target_qn = qn
            if len(keep) == len(pairs):
                # birebir yoksa yakın-eşleşen tek çift hedeflenir (yanlış replay kaynağı)
                hit = self.near_exact(q)
                if hit is None:
                    return False
                keep = [p for p in pairs if p is not hit]
                target_qn = _norm(hit["question"])
            self._pairs = keep
            self._vecs = None  # indeks bayatladı
            self._db_soft_delete(target_qn)
        return True

    def _db_soft_delete(self, qn: str) -> None:
        """Çifti soft-delete eder (deleted_at damgası; fiziksel silinmez — ADR-0019).
        Best-effort — bellek zaten güncel."""
        try:
            from sqlmodel import col, select

            from control_plane.models import VerifiedQuery
            with self._session() as s:
                row = s.exec(select(VerifiedQuery).where(
                    VerifiedQuery.company == self.company,
                    VerifiedQuery.question_norm == qn,
                    col(VerifiedQuery.deleted_at).is_(None))).first()
                if row:
                    row.deleted_at = datetime.utcnow()
                    s.add(row)
                    s.commit()
        except Exception:
            _log.warning("VQR DB soft-delete yazılamadı (bellek güncel, best-effort)",
                         exc_info=True)

    # -- retrieval -------------------------------------------------------
    def _scores(self, question: str) -> list[float]:
        pairs = self._load()
        if not pairs:
            return []
        model = _embedder()
        if model is not None:
            try:
                import numpy as np

                if self._vecs is None:
                    texts = [f"query: {p['question']}" for p in pairs]
                    self._vecs = np.array([v for v in model.embed(texts)])
                    self._vecs /= np.linalg.norm(self._vecs, axis=1, keepdims=True)
                qv = np.array(list(model.embed([f"query: {question}"]))[0])
                qv /= np.linalg.norm(qv)
                return (self._vecs @ qv).tolist()
            except Exception:
                pass
        return [_lex_score(question, p["question"]) for p in pairs]

    def recall(self, question: str, k: int = 3) -> list[tuple[dict, float]]:
        pairs = self._load()
        scores = self._scores(question)
        ranked = sorted(zip(pairs, scores), key=lambda t: -t[1])
        return [(p, s) for p, s in ranked[:k] if s > 0.3]

    def near_exact(self, question: str) -> dict | None:
        """Birebir (ya da eşik-üstü) eşleşme → LLM'siz tekrar oynatılabilir çift.

        YALNIZ GÜVENİLİR kaynaklar (Faz 4.1, bkz. `_TRUSTED_SOURCES`). Güvenilmez bir kayıt
        depoda KALIR — silinmez, çünkü hem terfi kuyruğunun ham maddesidir hem de
        `few_shot_block` için değerlidir; yalnız TEKRAR OYNATILMAZ.

        Not: birebir soru eşleşmesi bile güven kapısından muaf DEĞİLDİR. Aynı soruyu ikinci
        kez soran kullanıcı, ilk seferde LLM'in ürettiği ham SQL'i "doğrulanmış" rozetiyle
        geri almamalıdır — o cevap hiç incelenmedi.
        """
        pairs = self._load()
        guvenilir = [i for i, p in enumerate(pairs) if is_trusted(p.get("source"))]
        qn = _norm(question)
        for i in guvenilir:
            if _norm(pairs[i]["question"]) == qn:
                return pairs[i]
        if not guvenilir:
            return None
        scores = self._scores(question)
        if not scores:
            return None
        threshold = _EXACT_THRESHOLD if _embedder() is not None else _LEX_EXACT_THRESHOLD
        best_i = max(guvenilir, key=lambda i: scores[i])
        if scores[best_i] >= threshold:
            return pairs[best_i]
        return None

    def few_shot_block(self, question: str, k: int = 3) -> str:
        """Select/SQL üretim prompt'una eklenecek doğrulanmış örnekler bloğu ("" olabilir).
        Çift wren_sql sarmalayıcıysa (strict-agentic /ask) SQL olarak, CubeQuery ise
        JSON olarak gösterilir — DAIL-SQL desenindeki few-shot kazancı iki şekle de uygular."""
        hits = self.recall(question, k)
        if not hits:
            return ""
        lines = ["Doğrulanmış örnekler (benzer sorular — deseni izle):"]
        for p, _s in hits:
            payload = p["cube_query"]
            lines.append(f"- Soru: {p['question']}")
            if isinstance(payload, dict) and payload.get("wren_sql"):
                lines.append(f"  SQL: {payload['wren_sql']}")
            else:
                lines.append(f"  CubeQuery: {json.dumps(payload, ensure_ascii=False)}")
        return "\n".join(lines)
