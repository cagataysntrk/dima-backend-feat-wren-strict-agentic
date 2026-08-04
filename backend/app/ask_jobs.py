"""FAZ 1.12 — **İş iptali** (AI Act Md.14: insan gözetimi / durdurma).

## 🔴 İPTAL, İŞİ ÖLDÜRMEZ — SONUCU YAYIMLATMAZ

Çalışan bir thread'i zorla sonlandırmak yarım yazılmış bir sonuç ya da kayıt bırakabilir.
İşaretleme ise **kesin**: iş bittiğinde sonucu **yayımlanmaz** ve kullanıcı beklemekten
kurtulur. *Yarım bir sonucu yayımlamamak, hızlı öldürmekten daha güvenlidir.*

## 🔴 DEPO `AskJob` SATIRIDIR — İKİNCİ BİR DEPO YOK

⚠ **Bu bir düzeltmedir.** İlk sürüm iptali süreç-içi bir `set()`'te tutuyor ve durumu
`request.app.state.ask_jobs`'tan okuyordu — **öyle bir depo yok**: işler `AskJob`
tablosunda tutulur. Yani uç *"böyle bir iş yok"* demekten başka bir şey **yapamazdı**,
ve kendi sınamam bunu **göremezdi** çünkü sınama o olmayan deponun sahtesini kuruyordu.
Bu deponun tam olarak kaydettiği iki sınıf: *"beyan var, kod onu tanımıyor"* ve *"testler
METNİ ölçtü, davranışı değil"*.

Süreç-içi bir işaret ayrıca **ikinci bir gerçeklik** olurdu: süreç yeniden başladığında
iptal kaybolur, satır *"running"* kalır ve kullanıcı durdurduğu işin cevabını alırdı.

## ⚠ Bitmiş bir iş iptal EDİLEMEZ

Ve bu sessizce *"iptal edildi"* diye raporlanmaz: sonuç zaten kullanıcıya gitmiş olabilir;
ona *"durdurdum"* demek **yalan** olurdu. `bitti` ile `iptal` **farklı** şeylerdir ve
kullanıcıya farklı şey söylerler; *yok* olan iş buraya hiç gelmez (okuyucu 404 verir).

## Neden ayrı modül

`routers/ask.py` **risk sınırındadır** ve `0.21`'in büyüme kapısı dosyayı tavanında
tutuyor. Karar burada — saf, tek sahipli, test edilebilir; uç yalnız **çağırır**. Durumu
okuyan tek yer ise `ask.py::_job_durum_oku`'dur (tenant izolasyonunu **o** uygular);
buraya ikinci bir okuyucu yazmak, izolasyonun ikinci sahibi demekti.
"""

from __future__ import annotations

from typing import Any

#: `AskJob.status` sözlüğü (`control_plane/models.py`) — **oradaki adlar**, uydurma değil.
DURUM_IPTAL = "cancelled"
BITMIS_DURUMLAR = ("completed", "failed", DURUM_IPTAL)

_NOT = {
    "iptal": "İş durduruldu; sonucu yayımlanmayacak.",
    "bitti": "İş ZATEN BİTMİŞTİ — durdurulamaz (sonuç üretilmiş olabilir).",
}


def yayimlanabilir_mi(durum: Any) -> bool:
    """Arka-plan işi sonucunu **yazabilir mi**? Koşucu bunu yazmadan **önce** sorar.

    🔴 Tek soru budur: *"kullanıcı bu işi durdurdu mu?"* Durdurduysa cevap üretilmiş olsa
    bile **yayımlanmaz** — Md.14'ün istediği durdurma, bir isteğin **sonucunu** durdurmaktır.
    """
    return str(durum or "") != DURUM_IPTAL


def karar(durum: Any) -> str:
    """`durum` → `iptal` | `bitti`. **Saf**: ne okur ne yazar.

    Yokluk (`404`) buraya hiç gelmez — onu `ask.py::_job_durum_oku` **tenant izolasyonuyla
    birlikte** verir. İkinci bir *"bu iş var mı"* kontrolü, izolasyonun ikinci sahibi olurdu.
    """
    return "bitti" if str(durum or "").lower() in BITMIS_DURUMLAR else "iptal"


def iptal_et(job_id: str, durum: Any) -> dict[str, Any]:
    """Uçtan dönen gövde — ve gerekiyorsa `AskJob` satırına `cancelled` yazar.

    ⚠ **Yarış penceresi bilinçli olarak açık bırakıldı ve yazıldı:** koşucu tam bu anda
    sonucu yazıyorsa iptal onu yakalamayabilir. Kapatmanın yolu bir kilit ya da ayrı bir
    iptal tablosu olurdu; ikisi de **ikinci bir gerçeklik** getirirdi. Pencere
    milisaniyedir ve kaybedilen şey *"biraz geç durdurdum"*tur — *ölçülmemiş bir kilit,
    ölçülmüş bir milisaniyeden daha risklidir.*
    """
    sonuc = karar(durum)
    if sonuc == "iptal":
        _durumu_yaz(job_id, DURUM_IPTAL)
    return {"job_id": str(job_id), "durum": sonuc, "iptal_edildi": sonuc == "iptal",
            "not": _NOT[sonuc]}


def _durumu_yaz(job_id: str, durum: str) -> None:
    """`AskJob.status` → `cancelled`. **Tek yazma noktası.**

    ⚠ Hata **yutulmaz**: yazamazsak kullanıcıya *"durdurdum"* demiş oluruz ve bu yanlış
    olurdu — istisna yukarı çıkar, uç 500 döner ve kullanıcı **durmadığını** öğrenir.
    *Bir durdurma düğmesinin sessizce çalışmaması, hiç olmamasından beterdir.*
    """
    import uuid as _uuid

    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import AskJob

    with Session(engine) as s:
        j = s.get(AskJob, _uuid.UUID(str(job_id)))
        if j is None:                      # okuyucu 404 verdiyse buraya hiç gelinmez
            return
        j.status = durum
        s.add(j)
        s.commit()
