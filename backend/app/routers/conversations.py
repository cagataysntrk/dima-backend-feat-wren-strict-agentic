"""/conversations — kullanıcı sohbet geçmişi (per-user, tenant-izole).

Sohbetler /ask + /cube sırasında OTOMATİK kaydedilir (ask._persist_message); bu router
yalnız OKUMA + silme sağlar: liste (kenar çubuğu), getir (resume), sil. İzolasyon: yalnız
Principal.user_id'e ait sohbetler görünür/silinir (sahiplik kontrolü her uçta)."""

from __future__ import annotations

import json
import uuid as _uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.auth.dependencies import require_company
from app.schemas import ConversationDetail, ConversationOut
from control_plane.db import engine
from control_plane.models import Conversation, ConversationMessage

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _uid(request: Request) -> str | None:
    p = getattr(request.state, "principal", None)
    return getattr(p, "user_id", None) if p else None


@router.get("", response_model=list[ConversationOut])
def list_conversations(request: Request) -> list[ConversationOut]:
    """Kullanıcının sohbetleri, en son güncellenene göre (geçmiş kenar çubuğu)."""
    uid = _uid(request)
    if not uid:
        return []
    with Session(engine) as s:
        rows = s.exec(select(Conversation).where(
            Conversation.user_id == uid,
            Conversation.deleted_at.is_(None))  # soft-delete: silinmiş sohbetler gizli
            .order_by(Conversation.updated_at.desc())).all()
        # `§K12` — SON TUR SORUSU: aynı başlıklı sohbetleri ayırt eden asıl sinyal
        # (bkz. `ConversationOut.last_question` docstring'i). Kullanıcı başına liste
        # küçük (kenar çubuğu) — konuşma başına tek satır sorgu kabul edilebilir.
        son_sorular: dict[_uuid.UUID, str] = {}
        for c in rows:
            m = s.exec(select(ConversationMessage.question)
                       .where(ConversationMessage.conversation_id == c.id)
                       .order_by(ConversationMessage.seq.desc())
                       .limit(1)).first()
            if m:
                son_sorular[c.id] = m
    return [ConversationOut(
        id=str(c.id), title=c.title or "(başlıksız)", session_id=c.session_id,
        message_count=c.message_count, updated_at=c.updated_at.isoformat(),
        last_question=son_sorular.get(c.id)) for c in rows]


def _owned(request: Request, cid: str) -> Conversation:
    uid = _uid(request)
    try:
        conv = None
        with Session(engine) as s:
            conv = s.get(Conversation, _uuid.UUID(cid))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz sohbet id")
    # sahiplik + soft-delete: başkasının ya da silinmiş sohbet 404 (varlık sızdırma yok)
    if conv is None or conv.user_id != uid or conv.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Sohbet bulunamadı")
    return conv


def _refresh_viz(payload: dict, schema: dict) -> None:
    """Faz 2d+3 (viz.py↔chart.ts birleştirme, 31 Temmuz 2026): kayıtlı `viz` DONDURULMUŞ
    bir anlık görüntüdür (`ConversationMessage.payload_json` — "yeniden çalıştırma yok,
    veri sabit kalır" ADR ilkesi, bkz. control_plane/models.py `ConversationMessage`
    docstring'i). Bu doğru — SONUÇ/SAYILAR asla resume'de değişmemeli. Ama `viz` bir
    SUNUM KARARIDIR, veri değil: eski bir algoritma sürümüyle (ya da `recommend()`
    o an başarısız olduğu için hiç) hesaplanmış donuk bir `viz`, kullanıcıyı frontend'in
    KENDİ yerel `chart.ts::analyze()` yedeğine düşürür — bu, `recommend()`'in birim-
    farkındalı zenginleştirme katmanını (scatter/facet_measure/stacked/pivot/partition)
    HİÇ taşımayan, daha az yetenekli bir kopya (bağımsız araştırmayla doğrulandı). Sayılar
    SABİT kalırken (`result` asla dokunulmaz) `viz`'i HER resume'de TAZE hesaplamak bu
    sessiz-geriye-düşüşü kapatır — deterministik/saf bir fonksiyonun güncel sürümünü
    uygulamak "tek backend-hesaplı spec" ilkesini bozmaz, güçlendirir. Best-effort: hata
    olursa kayıtlı (varsa eski) `viz` korunur, resume asla kırılmaz."""
    result = payload.get("result")
    if not result:
        return
    try:
        from app import cube_router, viz

        cq = payload.get("cube_query")
        cmeta = cube_router._cube_meta(schema, cq["cube"]) if cq and cq.get("cube") else None
        # Metadata argümanları TEK KAYNAKTAN (`viz.meta_args`, Faz I1): resume edilen bir
        # sohbet, canlı cevapla AYNI grafik kararını almalı. Elle toplanan argüman listeleri
        # tam olarak burada ayrışırdı — ve ayrışma sessiz olurdu.
        payload["viz"] = viz.recommend(result, cube_query=cq, **viz.meta_args(cmeta))
    except Exception:
        pass  # best-effort — donmuş (varsa eski) viz korunur, resume kırılmaz


@router.get("/{cid}", response_model=ConversationDetail,
           dependencies=[Depends(require_company)])
def get_conversation(cid: str, request: Request) -> ConversationDetail:
    """Bir sohbet + tüm mesajları (resume): kayıtlı AskResponse payload'ları sırayla.
    `viz` (sunum kararı) her resume'de TAZE hesaplanır (bkz. `_refresh_viz`); `result`
    (sayılar) asla dokunulmaz."""
    conv = _owned(request, cid)
    with Session(engine) as s:
        msgs = s.exec(select(ConversationMessage)
                      .where(ConversationMessage.conversation_id == conv.id)
                      .order_by(ConversationMessage.seq)).all()
    payloads = []
    for m in msgs:
        try:
            payloads.append(json.loads(m.payload_json))
        except (ValueError, TypeError):
            continue
    if payloads:
        try:
            from app.company_registry import wren_for_request

            schema = wren_for_request(request).schema()
            for p in payloads:
                _refresh_viz(p, schema)
        except Exception:
            pass  # best-effort — şema alınamazsa kayıtlı viz'lerle devam edilir
    return ConversationDetail(id=str(conv.id), title=conv.title, session_id=conv.session_id,
                              messages=payloads)


@router.post("/{cid}/geri-al", status_code=200)
def geri_al_conversation(cid: str, request: Request) -> dict:
    """**SİLMEYİ GERİ AL** — `deleted_at` damgasını kaldırır. *(denetim F2)*

    ## 🔴 Ölçülen kusur

    Sunucu beş nesneyi **silmiyor, damgalıyor**; kayıt duruyor. Ama arayüzde — ve
    **hiçbir uçta** — silinmiş bir şeyi geri getiren **tek bir yol yoktu**. Yani
    kullanıcı açısından soft-delete ile hard-delete **birebir aynı deneyimdi** ve
    ADR-0019'un bedeli ödenmiş güvenlik ağı **kimseye ulaşmıyordu**.

    > 🔴 *Geri alınamayan bir soft-delete, pahalı bir hard-delete'tir.*

    ## Neden ayrı bir uç, `PATCH` değil

    `PATCH /{cid}` bir **alan güncellemesidir** ve `deleted_at`'i oraya açmak, silinmiş
    bir kaydı **kazara** dirilten bir yol bırakırdı. Geri alma bir **niyettir**; niyeti
    kendi ucunda tutmak, onu denetlenebilir de yapar (`audit`).

    ## ⚠ Neden süre sınırı YOK

    Kayıt duruyorsa geri alınabilir. Bir süre sınırı koymak, kullanıcıya *"beş saniyede
    karar ver"* demekti; oysa asıl güvence kaydın **durmasıdır**. Arayüzdeki şerit
    geçicidir — **yetenek değil**.

    ⚠ Zaten silinmemiş bir sohbette **hata değil, no-op**: kullanıcı iki kez geri-al'a
    bastığında bir hata görmemeli. *Bir düzeltmenin ikinci kez uygulanması, bir hata
    değildir.*
    """
    import uuid as _u

    uid = _uid(request)
    try:
        anahtar = _u.UUID(cid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz sohbet id") from None

    with Session(engine) as s:
        c = s.get(Conversation, anahtar)
        # 🔴 `_owned` KULLANILMAZ: o, silinmiş kaydı 404 sayar — yani tam da geri almak
        # istediğimiz durumu görünmez yapardı. Sahiplik burada elle doğrulanır.
        if c is None or c.user_id != uid:
            raise HTTPException(status_code=404, detail="Sohbet bulunamadı")
        if c.deleted_at is not None:
            c.deleted_at = None
            s.add(c)
            s.commit()
        baslik = c.title

    from control_plane import audit

    audit.record(getattr(request.state, "principal", None), "conversation_restore",
                 nl_question=cid,
                 ip=request.client.host if request.client else None)
    return {"ok": True, "id": cid, "title": baslik}


@router.delete("/{cid}", status_code=204)
def delete_conversation(cid: str, request: Request) -> None:
    """SOFT DELETE (proje kuralı: hard-delete YOK): deleted_at damgası. Kayıt+mesajlar kalır
    (audit/kurtarma); liste/getir onları süzer."""
    conv = _owned(request, cid)
    with Session(engine) as s:
        c = s.get(Conversation, conv.id)
        if c is not None and c.deleted_at is None:
            c.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
            s.add(c); s.commit()
