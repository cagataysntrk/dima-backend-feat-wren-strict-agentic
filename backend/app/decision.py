"""KARAR KAYDI — *"bu sayıya bakarak ne karar verdik ve neden?"* (Faz E-4).

## Query Contract'ın bir üstü

Query Contract *"bu sayı nasıl hesaplandı"* sorusunu cevaplar ve bu ürünün temel
değişmezidir. Karar Kaydı **bir üst soruyu** cevaplar:

> *"Bu sayıya bakarak NE KARAR VERDİK, hangi seçenekler arasından, hangi gerekçeyle,
> kim ve ne zaman?"*

BI ürünlerinde eksik olan halka budur: **rapor kalır, kararın kendisi kaybolur.** Altı ay
sonra *"bunu neden yapmıştık"* sorusunun cevabı kimsede olmaz — ve o cevabı üretebilen bir
sistem, rapor üreten bir sistemden kategorik olarak daha değerlidir.

## Üç tasarım kararı

**1. Değerlendirilen TÜM seçenekler saklanır, yalnız seçilen değil.** *"Neden bu?"* sorusu
ancak *"hangilerine karşı?"* bilinirse cevaplanabilir. Yalnız seçileni saklamak kararın
gerekçesini yok eder ve kayıt bir duyuruya dönüşür.

**2. `content_hash` gizli anahtarlı bir İMZA DEĞİL.** Bu bir kimlik doğrulama değil
**kurcalama tespitidir**: kayıt sonradan değiştirilirse hash tutmaz ve okuma ucu bunu
söyler. Anahtarlı imza, anahtar yönetimi (rotasyon, saklama, iptal) demektir ve **ölçülmüş
bir tehdide** dayanmadan o karmaşıklığı almak, bu depoda kayıtlı *"ölçülmemiş ihtiyaç için
altyapı kurma"* kuralının ihlali olurdu. Tehdit modeli netleştiğinde hash'in yerine imza
konabilir — **şema değişmez**, yalnız `content_hash`'i üreten fonksiyon değişir.

**3. Kanıt bağı zorunlu değil ama ÖLÇÜLÜR.** Bir karar kaydı tek başına bir cümledir;
Query Contract kimliklerine bağlandığında **yeniden çalıştırılabilir bir iddiaya** dönüşür.
Kanıtsız kayda izin verilir (kullanıcı serbest metinle karar yazabilir) ama kanıtın
varlığı okumada görünür — *"kanıtsız"* ile *"kanıtlı"* aynı şey değildir.

## Append-only

Karar **silinmez**. İptal/revizyon yeni bir kayıt yazar ve `supersedes` ile eskisini
gösterir — `ContractLog`'un append-only disipliniyle aynı (ADR-0019 ruhu): kanıt silinmez.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from app.logging_setup import get_logger

_log = get_logger("decision")

# Hash'e giren alanlar. Sıra SABİTTİR ve `sort_keys` ile birlikte kanonikliği garanti eder;
# alan eklenirse eski kayıtların hash'i DOĞRULANAMAZ hale gelir — bu yüzden liste
# genişletilirken sürümleme gerekir (bugün tek sürüm var, `v1`).
#: 🔴 **SÜRÜMLÜ ALAN KÜMESİ.** Bu dosyanın kendi uyarısı şuydu: *"alan eklenirse eski
#: kayıtların hash'i DOĞRULANAMAZ hale gelir — liste genişletilirken sürümleme gerekir."*
#: FAZ 5.8 o alanı ekledi (`sablon`) ve uyarıya **uydu**: eski kayıtlar `v1` ile, yeniler
#: `v2` ile doğrulanır.
#:
#: ⚠ *"Sonradan eklenen bir alanı eski kayıtlara da uygulamak"* ile *"eski kayıtları
#: toptan kurcalanmış ilan etmek"* arasında bir seçim vardı ve ikincisi **daha kötüydü**:
#: her kayıt `verified: False` olsaydı kurcalama tespiti **kendi gürültüsünde boğulur**,
#: gerçek bir kurcalama artık fark edilmezdi.
_HASH_ALANLARI: dict[str, tuple[str, ...]] = {
    "v1": ("question", "chosen", "options", "rationale", "note", "contract_ids"),
    "v2": ("question", "chosen", "options", "rationale", "note", "contract_ids",
           "sablon"),
}
#: Yeni kayıtların sürümü.
HASH_SURUMU = "v2"

#: Doğrulamada denenecek sürümler — **yeniden eskiye**. ⚠ Bu, kurcalama tespitini
#: **zayıflatmaz**: her sürüm hâlâ içeriğin güçlü bir hash'idir ve saldırgan ikisinden
#: hiçbirini tutturamaz. Yalnız *meşru* biçimlerin kümesi ikiye çıkar.
#:
#: 🔴 **Bilinen sınır, yazılı:** `v1` ile yazılmış bir kayda **sonradan** şablon
#: eklenirse bu **fark edilmez** (v1 o alanı hiç hash'lemiyordu). Bu kaçınılmazdır —
#: alan yokken yazılmış bir imza, olmayan bir alanı koruyamaz.
_DOGRULAMA_SURUMLERI = ("v2", "v1")


def kanonik(veri: dict[str, Any], surum: str = HASH_SURUMU) -> str:
    """Hash'lenecek kanonik metin. `sort_keys` + sabit ayraç = aynı içerik → aynı metin.

    `default=str` bilinçli: bir `Decimal`/`datetime` sızarsa hash **patlamak yerine**
    kararlı bir metin üretir. Patlamak, kararın kaydedilmemesi demektir ve kanıt kaybı
    kurcalama riskinden daha somut bir zarardır.
    """
    ozet = {k: veri.get(k) for k in _HASH_ALANLARI[surum]}
    return json.dumps({"v": surum, **ozet}, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), default=str)


def hash_of(veri: dict[str, Any], surum: str = HASH_SURUMU) -> str:
    return "sha256:" + hashlib.sha256(kanonik(veri, surum).encode()).hexdigest()


def yeni_kimlik() -> str:
    return "d-" + uuid.uuid4().hex[:10]


def kaydet(*, question: str | None, chosen: dict | None, options: list | None,
           rationale: str | None, note: str | None, contract_ids: list[str] | None,
           tenant_id: str | None, user_id: str | None, session_id: str | None,
           supersedes: str | None = None,
           sablon: dict | None = None) -> dict[str, Any]:
    """Karar kaydını yazar ve `{id, content_hash, ...}` döner.

    **Fail-closed DEĞİL, fail-loud:** DB'ye yazılamazsa hata yükselir. Query Contract
    kaybolduğunda rapor yine döner (kanıt raporun kendisi değildir) — ama bir KARAR
    kaydedilemiyorsa kullanıcı bunu **bilmelidir**, çünkü kaydettiğini sanıp
    kaydedilmemiş olması en kötü sonuçtur.
    """
    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import DecisionRecord

    # 🔴 ŞABLON **HASH'E DAHİLDİR** (FAZ 5.8). Dışarıda bırakmak, kaydın *"hangi
    # analizi tekrarlanabilir kıldığı"* kısmının **sessizce değiştirilebilmesi** demekti
    # — ve o değişiklik `verified: True` ile birlikte görünürdü. *Kurcalama tespiti,
    # ancak tespit ettiği alan kadar geniştir.*
    icerik = {"question": question, "chosen": chosen, "options": options,
              "rationale": rationale, "note": note, "contract_ids": contract_ids or [],
              "sablon": sablon}
    kayit = DecisionRecord(
        id=yeni_kimlik(), tenant_id=tenant_id, user_id=user_id, session_id=session_id,
        question=question,
        chosen_json=json.dumps(chosen, ensure_ascii=False, default=str) if chosen else None,
        options_json=json.dumps(options, ensure_ascii=False, default=str) if options else None,
        rationale=rationale, note=note,
        contract_ids_json=json.dumps(contract_ids or [], ensure_ascii=False),
        content_hash=hash_of(icerik), supersedes=supersedes,
        sablon_json=(json.dumps(sablon, ensure_ascii=False, default=str)
                     if sablon else None),
    )
    with Session(engine) as s:
        s.add(kayit)
        s.commit()
        s.refresh(kayit)
    _log.info("karar kaydedildi: %s (kanıt=%d makbuz)", kayit.id, len(contract_ids or []))
    return oku_satir(kayit)


def oku_satir(kayit) -> dict[str, Any]:
    """DB satırı → API biçimi + **doğrulama sonucu**.

    `verified` üç değerli: `True` (hash tutuyor) · `False` (**KURCALANMIŞ**) ·
    `None` (kayıtta hash yok — eski/bozuk satır). Üçünü iki değere sıkıştırmak,
    *"doğrulanamadı"*yı *"doğrulanmadı"* gibi göstermek olurdu.
    """
    def _j(metin, yedek):
        try:
            return json.loads(metin) if metin else yedek
        except Exception:
            return yedek

    icerik = {
        "question": kayit.question,
        "chosen": _j(kayit.chosen_json, None),
        "options": _j(kayit.options_json, None),
        "rationale": kayit.rationale,
        "note": kayit.note,
        "contract_ids": _j(kayit.contract_ids_json, []),
        # ⚠ Şablon **doğrulanan içeriğe DAHİL** — `kaydet()` onu hash'e katıyor ve okuma
        # da aynı sözlükten hesaplamak zorunda. Aksi hâlde her eski kayıt (şablonsuz,
        # `None`) ile her yeni kayıt (şablonlu) arasında **sistematik bir hash uyuşmazlığı**
        # doğar ve `verified` **hepsinde `False`** olurdu — kurcalama tespiti, kendi
        # gürültüsünde boğulurdu.
        "sablon": _j(getattr(kayit, "sablon_json", None), None),
    }
    dogrulandi: bool | None = None
    eslesen_surum: str | None = None
    if kayit.content_hash:
        # Yeniden eskiye dene: kayıt hangi sürümle yazıldıysa o tutar.
        for _s in _DOGRULAMA_SURUMLERI:
            if hash_of(icerik, _s) == kayit.content_hash:
                dogrulandi, eslesen_surum = True, _s
                break
        else:
            dogrulandi = False
        if not dogrulandi:
            _log.warning("KARAR KAYDI KURCALANMIŞ: %s — hash tutmuyor", kayit.id)
    return {
        "id": kayit.id,
        "ts": kayit.ts.isoformat() if kayit.ts else None,
        "session_id": kayit.session_id,
        **icerik,
        "content_hash": kayit.content_hash,
        "verified": dogrulandi,
        # ⚠ Hangi sürümle doğrulandığı **görünür**: `v1` bir kayıt, `sablon` alanını
        # koruyamaz ve okuyucu bunu bilmelidir.
        "hash_surumu": eslesen_surum,
        # Kanıtın VARLIĞI okumada görünür: "kanıtsız" ile "kanıtlı" aynı şey değildir.
        "evidence_count": len(icerik["contract_ids"] or []),
        "supersedes": kayit.supersedes,
    }
