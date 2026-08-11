"""🔴🔴 `§KV` — **VARLIK SORUSU: «kaç makinemiz var» bir metrik sorusu DEĞİLDİR.**

Bu modül `cube_router`'dan **çıkarıldı** ve bunu bir kapı istedi: modül büyüme tavanı
kırmızı verdi ve kendi mesajını yazdı — *«yeni davranışı modüle çıkar, tavanı
yükseltme»*. `veri_araligi`, `simge` ve `deger_capasi` de aynı şekilde doğdu.

⚠ **Yönlendirmeye (routing) dokunmaz.** Garson fişi zaten üretmiştir; burada yapılan
tek şey o fişin **şeklini** düzeltmektir: ölçü ve varsayılan dönem düşer. İş bölümü
doktrinin kendisi — *garson çevirir, biz şekli düzeltiriz.*
"""

from __future__ import annotations

import re

from app.cube_router import _LISTE_RE, _match_measure, _norm, date_filters

#: `§KV` — **VARLIK SORUSU** tetikleyicisi. Kapalı bir **dilbilgisi sınıfı**: soru
#: zamiri (`kaç`/`hangi`) + varlık yüklemi (`var`). ADR-0008'in yasakladığı açık uçlu
#: sözlük değildir — küme dilin kendi soru kalıbı kadar kapalıdır ve **hiçbir alan
#: terimi** içermez; alan bilgisi katalogdan gelir.
_VARLIK_RE = re.compile(r"\b(kac|hangi)\b[^?]{0,40}\bvar(dir|mis)?\b")


def sorusu(q: str, schema: dict) -> bool:
    """🔴🔴 `§KV` — **BİR VARLIĞI SAYMAK, ONUN BİR ÖLÇÜSÜNÜ HESAPLAMAK DEĞİLDİR.**

    ## Ölçülen kusur (curl `V` turu, 2026-08-11 · dört vaka)

        «kaç makinemiz var»        → 11 satır `makine × ort_oee` + **uydurma 12 aylık dönem**
        «hangi müşterilerimiz var» → `cari_kodu × hareket_sayisi` + uydurma dönem
        «kaç müşterimiz var»       → 🔴 **TEK satır** `{M1001, hareket_sayisi: 23}`
        «makineleri listele»       → 11 satır `makine × ort_oee` + uydurma dönem

    Üçüncüsü en kötüsü: *«kaç müşterimiz var»* sorusuna **bir müşterinin hareket
    sayısı** dönüyor. Kullanıcı bir **sayım** istedi, bir **metrik** aldı — ve yanında
    hiç sormadığı bir dönem varsayımı.

    ## Ayrım kataloğun kendisinden: soruda bir ÖLÇÜ terimi var mı

    ⊙ Negatif kontrol ölçüldü ve ayrımı doğruluyor: *«kaç parti üretildi bu yıl»* →
    `parti_sayisi = 7595` **doğru**. Çünkü orada `parti` bir **ölçünün** sinonimidir
    (`kac parti`), bir boyut değil. Yüklem *«soruda bir ölçü terimi geçiyor mu»* diye
    sorar; geçiyorsa **hiç karışmaz**.

    ⚠ `§101.1` — yanlış-pozitif buradaki kusurdan pahalıdır: bir metrik sorusunu varlık
    sorusu sanmak, kullanıcının istediği sayıyı **silmek** olurdu. İki şart birlikte
    aranır: (1) kapalı soru kalıbı, (2) katalogda **hiçbir ölçü** karşılığı yok.

    ## 🔴 BOYUT ŞARTI BURADA DEĞİL — VE BU BİR TERCİH DEĞİL, BİR KURAL

    İlk yazımda üçüncü bir şart vardı: *«katalogda bir boyut karşılığı olsun»*
    (`_match_dims`). Ölçüldü ve **düştü**: `«hangi müşterilerimiz var»` eşleşiyor ama
    `«kaç müşterimiz var»` ve `«kaç makinemiz var»` **eşleşmiyor** — 1. çoğul iyelik eki
    (`makine`+`miz`) ek zincirinde yok.

    ⚠ Ve çözüm **route'a o eki öğretmek DEĞİL**: en üst kural açık — *route'a dil kuralı
    ekleme (morfoloji · ek · yumuşama); bir cümle anlaşılmıyorsa çözüm route'u
    genişletmek değil devri tetiklemektir.* Devir zaten olmuş: garson bu soruya
    `dimensions: [makine]` taşıyan bir fiş üretiyor. Yani **boyutu garsonun kendi
    fişinden** okuruz; bu yüklem yalnız sorunun *biçimine* bakar.

    *Bir dilbilgisi kuralını yüklemin içine yazmak, o kuralın eksik kaldığı her yerde
    yüklemi de eksik yapar; oysa çeviriyi zaten anlayan biri var.*
    """
    qn = _norm(q or "")
    if not qn:
        return False
    if not (_VARLIK_RE.search(qn) or _LISTE_RE.search(qn)):
        return False
    return not any(_match_measure(qn, c)[0] for c in ((schema or {}).get("cubes") or []))


def fisi(q: str, cq: dict | None, schema: dict) -> tuple[dict | None, str | None]:
    """`§KV` — bir varlık sorusunun fişini **düzeltir**: ölçü YOK, varsayılan dönem YOK.

    Döner: **her zaman** `(cq, beyan)`. Dokunulacak bir şey yoksa `(cq, None)` —
    yani çağıran yerde `if` yok. ⚠ Bu bir üslup tercihi değil bir **tavan** kararı:
    `ask()` tam tavanındaydı ve dallanma çağırana yazılsaydı iki satır daha eklerdi.

    Üç şey yapar ve üçü de **eksiltmedir** — hiçbir şey uydurulmaz:

    1. **Ölçüler düşer.** Kullanıcı bir metrik sormadı; `measures: []` motorun
       desteklediği biçimdir (ölçüldü: `SELECT makine FROM oee_vardiya GROUP BY 1`).
    2. **Varsayılan dönem düşer** — *yalnız kullanıcı bir dönem yazmadıysa*. Bir
       makinenin listesi bir döneme ait değildir; *«son 12 ayı aldım»* demek burada bir
       varsayım değil bir **yanlış**tır. Kullanıcı dönem yazdıysa (`date_filters` boş
       dönmez) ona **dokunulmaz** — bir seçim ezilmez, bir boşluk doldurulur.
    3. **Beyan yazılır.** Sessiz bir daraltma bu deponun en pahalı kusur sınıfıdır.

    ⚠ Boyut yoksa `None` döner: boyutsuz bir varlık sorusu, cevaplanacak bir liste
    değildir ve orada susmak doğrudur (`§101.1`).
    """
    if not isinstance(cq, dict) or not (cq.get("dimensions") or []):
        return cq, None
    if not sorusu(q, schema):
        return cq, None
    qn = _norm(q or "")
    yeni = {k: v for k, v in cq.items() if k not in ("measures", "order", "limit")}
    yeni["measures"] = []
    _kup = next((c for c in (schema.get("cubes") or [])
                 if c.get("name") == cq.get("cube")), {}) or {}
    _td = (_kup.get("time_dimensions") or ["tarih"])[0]
    _kullanici_donemi = bool(date_filters(qn, _td))
    if not _kullanici_donemi:
        yeni["filters"] = [f for f in (yeni.get("filters") or [])
                           if str((f or {}).get("dimension") or "") != _td]
        yeni.pop("timeDimensions", None)
    _ad = ", ".join(str(d) for d in (cq.get("dimensions") or [])[:2])
    beyan = (f"Bu bir **varlık sorusu** olarak okundu: **{_ad}** listesi verildi — "
             f"bir ölçü hesaplanmadı"
             + ("." if _kullanici_donemi else " ve bir dönem varsayılmadı."))
    return yeni, beyan


def beyan_ekle(resp, beyan: str | None) -> None:
    """`§KV` — daraltmayı **söyler**: nota başa yazılır, ize `§KV:` satırı düşer.

    ⚠ Sessiz bir daraltma bu deponun en pahalı kusur sınıfıdır — kullanıcı ölçüsüz bir
    liste aldığını **görmelidir**. ⚠ Var olan not **ezilmez**, önüne eklenir.
    """
    if not beyan or resp is None:
        return
    resp.note = beyan + (f"\n\n{resp.note}" if getattr(resp, "note", None) else "")
    resp.trace = [*(getattr(resp, "trace", None) or []), f"§KV: {beyan}"]
