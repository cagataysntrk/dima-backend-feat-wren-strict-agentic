"""FAZ 6 (§4.5) — OFFLINE, İNSAN-ONAYLI sinonim önerici. Çalışma-anı sorgu yoluna GİRMEZ.

## Doldurduğu boşluk

`db_introspect` + `mdl_writer` canlı şemadan taslak MDL üretiyor (ADR-0017) ve **sinonim
bilerek ÜRETMİYOR** — `mdl_writer.py`'nin kendi sözü: *"burada TAHMİNİ sinonim
UYDURULMAZ."* Bu doğru bir karar: tahmini bir sinonim `route()`'un **canlı davranışını**
değiştirir. Ama sonuç, tablo adından başka etiketi olmayan **çıplak** bir cube — `route()`
onu neredeyse hiç eşleştiremez.

§2.1'in ölçtüğü darboğaz tam burada: **mekanizma üretiliyor, sözlük üretilmiyor.**
`compose.py`'nin üreteci bile bunu itiraf ediyor: *"sözlük kürasyonu işin indirgenemez
insan kısmıdır."*

## LLM'in meşru olduğu TEK yer

**Offline, insan-onaylı öneri — asla çalışma-anı sorgu yolu.** Bu modül:

* yalnız **çağrıldığında** çalışır (hiçbir `/ask` yolundan tetiklenmez),
* çıktıyı **doğrudan yazmaz**; `SynonymOverride(approved=False)` kuyruğuna **aday** koyar,
* o kuyruk zaten var ve `compose` **yalnız `approved=True`** olanları okur (ADR-0018 1e),
* yani bir öneri **insan onaylamadan hiçbir sorguyu etkileyemez**.

K1'in ad-hoc cube'unda kurulan *"yapı ≠ güven"* ayrımının **offline karşılığı**: LLM bir
taslak üretir, otorite insanda kalır.
"""

from __future__ import annotations

import json

from app.logging_setup import get_logger

_log = get_logger("sinonim")

#: Bir öneri en fazla bu kadar eşanlam taşır — uzun liste incelemeyi zorlaştırır ve
#: onaylayanı "hepsini kabul et"e iter (onay kalitesini düşüren bir kalıp).
MAKS_ONERI = 6


def _temizle(ham: str) -> list[str]:
    """LLM çıktısı → temiz eşanlam listesi. Bozuk/şüpheli her şey **düşer**.

    Cömert bir ayrıştırıcı burada yanlış olurdu: bu liste bir insanın önüne konacak ve
    gürültü, onaylayanın dikkatini tüketir.
    """
    try:
        veri = json.loads((ham or "").strip().strip("`").removeprefix("json").strip())
    except Exception:
        return []
    if not isinstance(veri, list):
        return []
    out: list[str] = []
    for x in veri:
        s = str(x).strip().lower()
        if not s or len(s) < 2 or len(s) > 40 or s in out:
            continue
        out.append(s)
    return out[:MAKS_ONERI]


def oner(llm, teknik_ad: str, baglam: str = "") -> list[str]:
    """Tek bir teknik ad için eşanlam TASLAĞI. Sağlayıcı yoksa/patlarsa **boş liste**.

    Boş dönmek bir hata değil bir karardır: öneri üretemeyen bir adım, kuyruğa gürültü
    koyan bir adımdan iyidir.
    """
    if llm is None or not hasattr(llm, "sinonim_oner"):
        return []
    try:
        return _temizle(llm.sinonim_oner(teknik_ad, baglam))
    except Exception:  # noqa: BLE001 — offline araç, hiçbir cevabı düşürmez
        _log.info("sinonim önerisi alınamadı: %s", teknik_ad, exc_info=True)
        return []


def kuyruga_koy(session, *, cube: str, field_kind: str, field_name: str | None,
                synonyms: list[str], scope_type: str = "global",
                scope_id: str | None = None) -> object | None:
    """Öneriyi **onaysız aday** olarak kuyruğa yazar. Döner: kayıt ya da None (boş öneri).

    `approved=False` **zorunludur ve burada sabittir** — parametre olarak dışarı
    açılmamıştır. Açılsaydı bir çağıran onu `True` geçebilir ve LLM önerisi **insan
    görmeden canlıya inerdi**; o an bu modülün tüm gerekçesi çökerdi.

    `source="llm_oneri"` ayrı tutulur: `manual` (insan yazdı) ve `mined` (deterministik
    madencilik) ile **aynı kutuya** koymak, onaylayanın önerinin nereden geldiğini
    görmesini engellerdi — ve bir LLM önerisi, bir insan girdisiyle aynı güvene sahip
    değildir.
    """
    from control_plane.models import SynonymOverride

    temiz = [s for s in (synonyms or []) if s]
    if not temiz:
        return None
    kayit = SynonymOverride(
        scope_type=scope_type, scope_id=scope_id, cube=cube,
        field_kind=field_kind, field_name=field_name,
        synonyms_json=json.dumps(temiz, ensure_ascii=False),
        lang="tr",
        approved=False,          # SABİT — bkz. docstring
        source="llm_oneri",
    )
    session.add(kayit)
    return kayit


def ciplak_cube_icin(llm, cube: dict) -> dict[str, list[str]]:
    """Çıplak bir cube'un ölçü/boyutları için toplu öneri: {alan_adı: [eşanlamlar]}.

    Yalnız **gerçekten çıplak** alanlar hedeflenir: zaten sinonimi olan bir alana öneri
    üretmek, var olan küratörlü sözlüğü gürültüyle sulandırırdı.
    """
    out: dict[str, list[str]] = {}
    msyn = cube.get("measure_synonyms") or {}
    dsyn = cube.get("dimension_synonyms") or {}
    etiket = cube.get("display") or cube.get("label") or cube.get("name") or ""
    for ad in cube.get("measures") or []:
        n = ad if isinstance(ad, str) else ad.get("name")
        if n and len(msyn.get(n) or []) <= 1:      # yalnız kendi adı → çıplak
            o = oner(llm, str(n), f"{etiket} tablosunun bir ölçüsü")
            if o:
                out[str(n)] = o
    for ad in cube.get("dimensions") or []:
        n = ad if isinstance(ad, str) else ad.get("name")
        if n and len(dsyn.get(n) or []) <= 1:
            o = oner(llm, str(n), f"{etiket} tablosunun bir kırılım boyutu")
            if o:
                out[str(n)] = o
    return out
