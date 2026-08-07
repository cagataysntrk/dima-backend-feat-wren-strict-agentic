"""🔴 `G0b` — **KORUNAN YAYILIM**: gerçek değer ve sayı binadan ÇIKMAZ.

## Ölçülen kusur (2026-08-07)

`llm_guard.ihlalleri_bul` **PII kalıplarını** yakalıyor (TCKN · e-posta · telefon ·
IBAN). Ama `interpret.py:248` şunu üretiyor ve olduğu gibi sağlayıcıya gidiyordu:

    "En yüksek Makine: RAM 3 (12.430 kg)"
           gerçek boyut DEĞERİ ─┘        └─ gerçek SAYI

İkisi de hiçbir maskeye uymuyor. Dış sağlayıcıya (OpenRouter) geçildiği an bu
**binadan çıkan veridir**.

## Neden AYRI MODÜL — ve bunu bir kapı söyledi

İlk sürüm bu kodu `llm_guard.py`'ye koydu. `tests/test_llm_guard.py::
test_DESEN_SOZLUGU_KOPYALANMAMIS` **haklı olarak** kırmızı verdi: o modül
*"`re.compile` yazmayacaksın — desen sözlüğünün tek sahibi `pii.py`"* diye kilitli.

🔴 Kapıyı gevşetmek kendi lehine hile olurdu. Doğru okuma: **iki ayrı soru var.**

| modül | sorusu |
|---|---|
| `llm_guard` | *"bu yük **çıkabilir mi**?"* — kişisel veri kapısı, fail-closed |
| `yayilim` *(bu)* | *"**ne perdelenecek**?"* — gerçek değer/sayı dönüşümü |

Bu, `hava_boslugu.py` gibi **rakip bir kapı** değildir: çıkış kapısı hâlâ tek ve
`safe_call`'dır. Burası ondan **önce** çalışan bir dönüşümdür.

## Neden guard'ı ZAYIFLATMAZ — GÜÇLENDİRİR

Danışman belgesinin anonimleştirme önerisi `narration_guard` ile bağdaşmıyordu: LLM'e
**soyutlama** gönderiyordu (`"Segment_A"`, `"1,2 std üstü"`), o zaman guard'ın
doğrulayacağı bir sayı kalmıyordu. Yer tutucu bu tuzağa düşmez:

| | ±%2 eşleştirme *(bugün)* | yer tutucu *(bu modül)* |
|---|---|---|
| LLM gerçek sayıyı görür mü | evet → **dışarı çıkar** | **hayır** |
| doğrulama | metindeki sayıyı DB ile karşılaştır | her `{{NUM_i}}` **tam bir kez** mi — **yapısal** |
| uydurma sayı mümkün mü | tolerans içinde **evet** | 🔴 **hayır — rakam üretemez ki** |
| yıl/sıra muafiyeti gerekir mi | evet (`YIL_ARALIGI` · `SIRA_ESIGI`) | **hayır** — kavram ortadan kalkar |
"""

from __future__ import annotations

import re
from typing import Iterable

from app.logging_setup import get_logger

_log = get_logger("yayilim")

#: Metindeki sayı dizileri. ⚠ Bu bir **PII deseni değildir** — `pii.py`'nin kapsamıyla
#: çakışmaz; orası *"bu kişisel veri mi"*, burası *"bu bir rakam mı"* sorusunu sorar.
_SAYI_RE = re.compile(r"\d[\d.,]*")

#: Yer tutucu biçimi. Süslü parantez **bilinçli**: modeller onu bir şablon yuvası olarak
#: tanıyıp **bozmadan** taşıyor; `<X>` ya da `[X]` biçimleri doğal metinde de geçtiği
#: için karışırdı.
_YT_RE = re.compile(r"\{\{[A-Z]+_\d+\}\}")


def _yt(tur: str, no: int) -> str:
    return "{{%s_%d}}" % (tur, no)


def perdele(metinler: list[str], *,
            degerler: Iterable[str] = ()) -> tuple[list[str], dict[str, str]]:
    """Gerçek **değer** ve **sayı**ları yer tutucuya çevir. Döner: `(perdeli, harita)`.

    `degerler` — çağıranın bildiği gerçek boyut değerleri (sonuç satırlarından). Bunlar
    **önce** ve **uzundan kısaya** perdelenir: kısa bir değer uzun birinin içinde
    geçiyorsa (`"RAM"` ⊂ `"RAM 3"`) önce uzunu almak **yarım perdelemeyi** önler.

    🔴 **Harita ASLA sağlayıcıya gitmez** — çağıranda kalır, `geri_koy` ile kullanılır.

    ⚠ **Sayı taraması yer tutucuların İÇİNE girmez.** İlk sürüm giriyordu: `{{DIM_1}}`
    içindeki `1` bir sayı sanılıp `{{DIM_{{NUM_2}}}}` üretiliyordu. Ölçülen kusur —
    *bir maskenin kendi çıktısını yeniden maskelemesi, maskeyi bozar.*
    """
    harita: dict[str, str] = {}
    ters: dict[str, str] = {}          # gerçek değer → yer tutucu (aynı değer TEK yuva)

    def _yuva(tur: str, gercek: str) -> str:
        if gercek in ters:
            return ters[gercek]
        yt = _yt(tur, len(harita) + 1)
        harita[yt] = gercek
        ters[gercek] = yt
        return yt

    metinler = list(metinler)
    temiz = [str(d) for d in degerler if d is not None and str(d).strip()]
    for d in sorted(set(temiz), key=len, reverse=True):
        for i, m in enumerate(metinler):
            if d in m:
                metinler[i] = m.replace(d, _yuva("DIM", d))

    out: list[str] = []
    for m in metinler:
        # Yer tutucu parçalarını ATLA, yalnız aralarındaki metinde sayı ara.
        parcalar, son = [], 0
        for mo in _YT_RE.finditer(m):
            parcalar.append(_SAYI_RE.sub(lambda x: _yuva("NUM", x.group(0)),
                                         m[son:mo.start()]))
            parcalar.append(mo.group(0))
            son = mo.end()
        parcalar.append(_SAYI_RE.sub(lambda x: _yuva("NUM", x.group(0)), m[son:]))
        out.append("".join(parcalar))

    _log.info("perdeleme: %d metin · %d yer tutucu (DEĞER YAZILMAZ)", len(out), len(harita))
    return out, harita


def geri_koy(metin: str, harita: dict[str, str]) -> tuple[str, list[str]]:
    """Yer tutucuları gerçek değerle değiştir. Döner: `(metin, sorunlar)`.

    🔴 **Doğrulama YAPISALDIR ve ±%2'den güçlüdür:** model bir rakam *üretemez* — yalnız
    verdiğimiz yuvaları taşıyabilir. Bozduğu ya da uydurduğu yuva **sayılır**:

    * `eksik:{{X}}`   — verdiğimiz yuva metinde yok *(bilgi düşmüş)*
    * `uydurma:{{X}}` — haritada olmayan bir yuva var *(model yuva **icat etti**)*

    Çağıran bu listeyi görüp cümleyi **düşürür**. Sessizce geri koymak, modelin bozduğu
    bir cümleyi doğru göstermek olurdu — ve uydurma yuva **metinde bırakılır** ki
    gizlenmesin.
    """
    sorunlar: list[str] = []
    for yt in _YT_RE.findall(metin):
        if yt not in harita:
            sorunlar.append(f"uydurma:{yt}")
    for yt, gercek in harita.items():
        if yt not in metin:
            sorunlar.append(f"eksik:{yt}")
        else:
            metin = _yerine_koy(metin, yt, gercek)
    if sorunlar:
        _log.warning("yayılım bozuldu: %s", ", ".join(sorunlar))
    return metin, sorunlar


# --- 🔴 EK MOTORU BURAYA BAĞLANIR (`G7`'nin tek üretim tüketicisi) -------------------
#
# `G7` `app/ek.py`'yi yazdı ama **hiçbir yerden çağırmadı** — üç denetim ajanının üçü de
# bağımsız buldu (`DA-1`). *Bir modülün testli olması, kullanıldığını kanıtlamaz.*
#
# Bağlanacağı doğru yer burası ve sebebi yapısal: **yer tutucunun sınırını bilen tek
# modül bu.** Model `{{DIM_1}}` görür ve etrafına Türkçe yazar — *"en yüksek {{DIM_1}}'de"*
# gibi. Ama eki, yer tutucunun **arkasındaki gerçek değeri görmeden** seçmiştir; gerçek
# değer `Mart` ise doğrusu `Mart'ta`, `Kasım` ise `Kasım'da`.
#
# Düz `str.replace` bu eki **olduğu gibi** bırakıyordu: model ne yazdıysa o.
# *Bir değeri gizleyip yerine bir yuva koymak, o yuvanın dilbilgisini de üstlenmektir.*

#: Modelin yazdığı ek → `ek.py`'nin beş tipinden biri. **Yeni sözlük değil**: `ek_bagla`'nın
#: kendi tiplerinin ters haritası. Ünlü uyumunun her varyantı aynı tipe düşer.
_EK_TERS = {
    "de": "de", "da": "de", "te": "de", "ta": "de",
    "den": "den", "dan": "den", "ten": "den", "tan": "den",
    "e": "e", "a": "e", "ye": "e", "ya": "e",
    "i": "i", "ı": "i", "u": "i", "ü": "i",
    "yi": "i", "yı": "i", "yu": "i", "yü": "i",
    "in": "in", "ın": "in", "un": "in", "ün": "in",
    "nin": "in", "nın": "in", "nun": "in", "nün": "in",
}


def _yerine_koy(metin: str, yt: str, gercek: str) -> str:
    """`{{X}}` → gerçek değer, **arkasındaki ek yeniden çekimlenerek**.

    ⚠ Kapsam **kapalı**: yalnız kesme işaretiyle yazılmış ek (`{{DIM_1}}'de`). Bitişik
    yazılmış bir kuyruk bir ek de olabilir bir kelime de; ayırt etmek bir morfoloji işidir
    ve bu modülün kapsamı değil — *şüphede dokunmamak, yanlış çekimlemekten iyidir.*

    🔴 Sayı yuvaları (`{{NUM_i}}`) `sayi=True` ile gider: ek sayının **okunuşuna** göre
    seçilir (`3` → *üç* → `3'te`; `1.000.000` → *milyon* → `1.000.000'a`).
    """
    import re as _re

    from app.ek import ek_bagla

    sayi_mi = yt.startswith("{{NUM")
    desen = _re.compile(_re.escape(yt) + r"(?:['’]([a-zçğıöşü]{1,3}))?")

    def _degistir(m: _re.Match) -> str:
        kuyruk = (m.group(1) or "").lower()
        tip = _EK_TERS.get(kuyruk)
        if not tip:
            return gercek if not kuyruk else f"{gercek}'{kuyruk}"
        try:
            # 🔴 `kesme=True`: modelin yazdığı kesme işareti, sözcüğün **özel ad**
            # olduğunun beyanıdır — ve özel adlarda yumuşama yazıya geçmez (TDK).
            return ek_bagla(gercek, tip, sayi=sayi_mi, kesme=not sayi_mi)
        except Exception:                            # noqa: BLE001 — çekim cevabı düşürmez
            _log.warning("ek çekimlenemedi (%r + %r)", gercek, tip, exc_info=True)
            return f"{gercek}'{kuyruk}"

    return desen.sub(_degistir, metin)
