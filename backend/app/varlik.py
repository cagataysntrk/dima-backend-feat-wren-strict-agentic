"""🔴 `G0b.6` — **VARLIK PERDESİ**: çözülen bir değer sağlayıcıya HAM gitmez.

## Ölçülen durum — ve neyin kusur OLMADIĞI

`app/value_index.py` bir yazım hatasını gerçek bir katalog değerine çözer (*"efe dokma"*
→ *"efe dokuma"*). Endişe şuydu: o **çözülmüş gerçek ad** LLM'e sızar mı?

⊙ **Sızmıyor** — ve bu bir tasarım kararıydı, tesadüf değil: `ask.py:2717`'nin ürettiği
`corrected_q` yalnız **deterministik yeniden yönlendirmede** kullanılır; LLM'e giden şey
her zaman `body.question`, yani **kullanıcının kendi yazdığı** metindir.

🔴 **Ama başka bir kapıdan çıkıyor.** `cube_router.build_catalog` prompt'a şunu yazıyor:

    Filtre değerleri (birebir kullan):
      parti.musteri ∈ {…}

Yani boyutların **gerçek değerleri** (≤25) her istekte sağlayıcıya gidiyor. Bu bilinçli
ve süzgeçli (`sensitivity.prompt_safe_values`) — ama kullanıcının sorusunda **zaten
geçen** bir değer için o listeyi de, ham değeri de göndermek gereksizdir.

## Bu modülün yaptığı — ve neden bir KAYIP değil KAZANÇ

Sorudaki katalog değerini `{{ENT_i}}` ile perdeler ve prompt'a bir **kural** yazar:

    {{ENT_1}} = `musteri` değeri (filtrede yer tutucuyu BİREBİR yaz)

⚠ Bu, modele bilgi **kaybettirmez, kazandırır**: ham değer *"bu ne?"* sorusunu açık
bırakır, yer tutucu **hangi boyuta ait olduğunu söyler**. Deterministik katman zaten
çözmüştü; modelin onu yeniden çözmesi gerekmiyor.

*Bir katmanın çözdüğü şeyi bir sonrakine yeniden çözdürmek, iki cevap üretme riskidir.*

## FAIL-CLOSED

`geri_koy` bir yuvayı haritada bulamazsa **sorgunun tamamını düşürür** (`None`). Yarım
geri konmuş bir filtre, `{{ENT_1}}` diye bir müşteri arardı — hiç satır dönmez ve cevap
*"veri yok"* olurdu. **Yanlış boşluk, görünür bir hatadan beterdir.**

⚠ **Süzgecin sahibi bu modül DEĞİL.** *"Hangi değer görülebilir"* sorusunun tek sahibi
`app/sensitivity.py`'dir ve `build_catalog` da ona sorar; burada ikinci bir politika
yazılsaydı iki prompt üreticisi farklı değer kümesi görürdü (bu depoda **bir kez oldu**,
`build_catalog`'un kendi şerhinde yazılı).
"""

from __future__ import annotations

import re
from typing import Any

from app.logging_setup import get_logger

_log = get_logger("varlik")

#: Yer tutucu deseni — `app/yayilim.py`'nin `{{TUR_i}}` ailesiyle **aynı biçim**.
#: ⚠ İkinci bir biçim icat etmek, iki geri-koyucu demekti.
YUVA_RE = re.compile(r"\{\{ENT_\d+\}\}")

#: Perdelenecek en kısa değer. Kısa değerler (`"A"`, `"3"`) soruda tesadüfen geçer ve
#: perdelenirse cümlenin ortasından bir harf sökülür. *Bir maske, maskelediğinden fazlasını
#: örtüyorsa maske değil sansürdür.*
_MIN_UZUNLUK = 3


def perdele(q: str, schema: dict) -> tuple[str, dict[str, str], str]:
    """`(perdeli_soru, harita, kural_metni)` — soruda geçen katalog değerlerini yuvalar.

    Uzundan kısaya taranır: kısa bir değer uzun birinin içinde geçiyorsa (`"RAM"` ⊂
    `"RAM 3"`) önce uzunu almak **yarım perdelemeyi** önler — `yayilim.perdele`'nin
    ölçülmüş dersi, burada tekrar edilmiyor **izleniyor**.
    """
    from app.sensitivity import prompt_safe_values

    cols = {c["name"]: c for m in schema.get("models") or [] for c in m.get("columns") or []}
    # (değer, boyut) çiftleri — aynı değer birden çok boyutta geçebilir; İLK sahip kazanır
    # ve bu bilinçli: iki boyut adı yazmak modele bir seçim yaptırırdı, oysa amaç seçimi
    # ondan ALMAKTI.
    # 🔴 **SÖZLÜKLE ÇAKIŞAN DEĞER PERDELENMEZ — ölçülerek bulundu.** İlk sürüm
    # *"gecen ay toplam ciro"* sorusunu *"gecen ay toplam `{{ENT_1}}`"* yapıyordu: bu
    # katalogda `ciro` **hem bir ölçü sinonimi hem bir boyut değeri**. Perde onu yutunca
    # sorudan **ölçü** silinmiş oluyordu — yani maske, koruduğu şeyi bozuyordu.
    #
    # ⚠ Kural `typo_suggest`'in kendi kuralının aynısı (*"çapraz-konu terimi — yazım
    # hatası değil"*): bir kelime hem sözlükte hem değer listesinde geçiyorsa
    # **belirsizdir**, ve belirsizliği maskeyle çözmek onu yanlış yöne çözmektir.
    #
    # *Bir maske, maskelediğinden fazlasını örtüyorsa maske değil sansürdür.*
    from app.cube_router import _catalog_vocabulary

    sozluk = {s.lower() for s in _catalog_vocabulary(schema)}

    adaylar: dict[str, str] = {}
    for c in schema.get("cubes") or []:
        for dim in c.get("dimensions") or []:
            col = cols.get(dim)
            if not col:
                continue
            for v in prompt_safe_values(col) or []:
                s = str(v).strip()
                if len(s) >= _MIN_UZUNLUK and s.lower() not in sozluk:
                    adaylar.setdefault(s, dim)

    harita: dict[str, str] = {}
    kurallar: list[str] = []
    out = q
    for deger in sorted(adaylar, key=len, reverse=True):
        if deger.lower() not in out.lower():
            continue
        yuva = "{{ENT_%d}}" % (len(harita) + 1)
        harita[yuva] = deger
        kurallar.append(f"  {yuva} = `{adaylar[deger]}` değeri")
        out = re.sub(re.escape(deger), yuva, out, flags=re.IGNORECASE)

    if not harita:
        return q, {}, ""
    _log.info("varlık perdesi: %d yuva (GERÇEK DEĞER YAZILMAZ)", len(harita))
    return out, harita, (
        "\n\nVarlık yer tutucuları — gerçek değerler PERDELENDİ. Filtre yazarken "
        "`value` alanına yer tutucuyu **birebir** koy (çözmeye çalışma):\n"
        + "\n".join(kurallar))


def geri_koy(cq: Any, harita: dict[str, str]) -> Any:
    """Sorgudaki yuvaları gerçek değerle değiştirir — **çözülemeyen varsa `None`**.

    🔴 Fail-closed: yarım geri konmuş bir filtre `{{ENT_1}}` diye bir değer arardı, hiç
    satır dönmezdi ve cevap *"veri yok"* olurdu. Kullanıcı bunu bir **bulgu** sanar.
    *Yanlış bir boşluk, görünür bir hatadan beterdir.*
    """
    if not harita or cq is None:
        return cq

    kayip = False

    def _coz(x: Any) -> Any:
        nonlocal kayip
        if isinstance(x, str):
            def _d(m: re.Match) -> str:
                nonlocal kayip
                if m.group(0) not in harita:
                    kayip = True
                    return m.group(0)
                return harita[m.group(0)]
            return YUVA_RE.sub(_d, x)
        if isinstance(x, list):
            return [_coz(i) for i in x]
        if isinstance(x, dict):
            return {k: _coz(v) for k, v in x.items()}
        return x

    out = _coz(cq)
    if kayip:
        _log.warning("varlık perdesi: ÇÖZÜLEMEYEN yuva — sorgu düşürüldü (fail-closed)")
        return None
    return out
