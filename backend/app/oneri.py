r"""🔴 `FAZ 5` — **ÖNERİ MOTORU** (yazarken-ara / typeahead).

Kullanıcı yazarken katalogdan aday terim önerir. **Saf**: sorgu koşmaz, LLM çağırmaz,
`/ask` yoluna **hiç** dokunmaz (`E-8`: sıcak yolda seri ikinci tur yok).

## Ön koşul — ve neden yazılı

`FAZ 0` ölçtü: **`Recall@3 = %89,5`** (vektör ayağı, `intfloat/multilingual-e5-large`,
payda **19**). Eşik `%85`'ti; faz bu ölçümle açıldı. Kapı:
`tests/test_oneri_on_kosulu_model_kimligi.py` — üretim gömücüsü ölçülenden ayrılırsa
kırmızı verir 🅕.

## 🔴 `5.2` — YETKİ SÜZMESİ **SIRALAMADAN ÖNCE** (fazın tek güvenlik kalemi)

Bir öneri listesi **envanterdir**. Yetkisiz bir ölçünün adını açılır listede göstermek,
o ölçüyü koşturmaya izin vermesek bile **bilgi sızıntısıdır**. Bu yüzden süzme
**sıralamadan önce** yapılır: sıralama yalnız **görmeye hakkı olan** kümede çalışır.

⚠ ㊱ **Planın adlandırması yanlıştı ve düzeltildi.** Plan *«`authorize()` süzmesi»*
diyordu; ölçüldü ki `authorize(principal, action, resource)` **eylem düzeyi** kaba bir
kapıdır (Katman A) ve izin varsa **sessiz döner** — kaynak başına süzemez. Kaynak
başına yetki **Katman B**'dedir: `katman_b.karar(referanslar, izinliler)`, **saf**
fonksiyon, ve *«yapılandırılmamış»* (`izinliler is None`) ile *«boş allowlist»*
ayrımını **o** taşır. Burada o fonksiyon **çağrılır**; ikinci bir yetki kuralı
yazılmaz (`KAT-1`).

Küp → model bağı `base_object`'tir (`wren_service.py:793`).

## `5.8` — Gömücü soğuksa ÇÖKME, leksik kipe düş

`vqr._embedder()` tembel ve **bloklamayan**: başka bir iş parçacığı modeli indiriyorsa
`None` döner (ölçülmüş kusur: eskiden bloklayan kilit bir isteği **dakikalarca**
astırıyordu). Bu modül o `None`'ı bir **hâl** olarak kabul eder — vektör ayağı düşer,
leksik ayak cevabı verir, `kip` alanı bunu **beyan eder** 🅖.

## Füzyon — `k` bilinçli seçildi ve YAZILDI

RRF (`1/(k+sıra)`) için literatürün `k=60`'ı **uzun** listeler içindir; orada amaç
sıra farklarını **yumuşatmaktır**. Burada aday havuzu kısadır (ayak başına `_HAVUZ`),
ve `k=60` seçilseydi `1/61` ile `1/70` arasındaki fark **binde bir**e inerdi: füzyon
**hiçbir şey sıralamaz**, çıktı iki ayağın rastgele birleşimi olurdu. Bu yüzden
`_RRF_K = 10` — sıra **anlamını korusun** diye.

⚠ 🅖 **Bu sayı kalibre EDİLMEDİ**, seçildi. Kalibrasyonu `FAZ 0` paydasının **19 → 30–40**
büyütülmesine bağlıdır (açık borç). Bir sayının gerekçesi olması, ölçülmüş olması
demek değildir.

## ⚠ MUTLAK EŞİK YOK

`FAZ 0`'ın ikinci bulgusu bağlayıcı: gürültü kelimesi *«vardya»* kosinüs **0,851**
aldı — yani *«skor > X ⇒ iyi aday»* **çalışmaz**. Bu modül hiçbir yerde çıplak bir
kosinüs eşiği kullanmaz; vektör ayağı yalnız **sıra** üretir. Leksik ayakta kullanılan
eşik (`_TYPO_MID`) katalog kelimeleri için **kalibre edilmiş** bir sabittir ve
`cube_router`'dan **ödünç alınır**, yeniden tanımlanmaz (`KAT-1`).
"""

from __future__ import annotations

import difflib
import hashlib
from dataclasses import dataclass

from app.llm import _norm

__all__ = ["Aday", "ara", "terimler"]

#: Ayak başına havuz — füzyona giren aday sayısı. Kısa tutulur: typeahead'de
#: yirminci aday hiçbir zaman görülmez, ama her aday bir gömme kıyası demektir.
_HAVUZ = 20

#: RRF sabiti — gerekçesi modül başlığında. **Kalibre değil, seçilmiş** 🅖.
_RRF_K = 10

#: Öneri şeridinin tavanı (`FAZ 6.4`: **≤7**).
VARSAYILAN_LIMIT = 7


@dataclass(frozen=True)
class Aday:
    """Bir öneri. `kip` **hangi ayağın** bulduğunu beyan eder 🅖."""

    kimlik: str        # `cube.olcu` — tıklanınca sorguyu kuran taraf bunu çözer
    etiket: str        # kullanıcıya görünen ad
    cube: str
    kip: str           # "leksik" | "vektor" | "leksik+vektor"


def terimler(schema: dict, izinliler: set[str] | None) -> list[Aday]:
    """🔴 `5.2` — **ÖNCE YETKİ, SONRA HER ŞEY.**

    Katalogdan aday terimleri toplar; **görmeye hakkı olmayan** küplerin hiçbir terimi
    listeye girmez. Sıralama bu listenin **üstünde** çalışır, tersi değil.

    `izinliler is None` → Katman B bu tenant'ta yapılandırılmamış; kararı
    `katman_b.karar` verir (Katman A yönetir). Kural burada **tekrarlanmaz**.
    """
    from app.katman_b import karar

    out: list[Aday] = []
    for c in schema.get("cubes") or []:
        model = c.get("base_object") or c.get("name") or ""
        gecer, _ = karar({model} if model else set(), izinliler)
        if not gecer:
            continue  # 🔴 yetkisiz küp → adı bile geçmez (envanter sızıntısı)
        cube = str(c.get("name") or "")
        gorunen = c.get("measure_synonyms_display") or {}
        for olcu, etiket in gorunen.items():
            out.append(Aday(kimlik=f"{cube}.{olcu}", etiket=str(etiket), cube=cube,
                            kip="leksik"))
    return out


def _leksik_sira(kismi: str, adaylar: list[Aday]) -> list[int]:
    """Edge n-gram **önce**, bulanık benzerlik **sonra** (`5.3`).

    Önek eşleşmesi typeahead'in doğal davranışıdır ve **bedavadır**; bulanık ayak
    yalnız önek hiçbir şey bulamadığında anlamlıdır. Eşik `cube_router`'dan **ödünç
    alınır** — bu depoda o sabitler katalog kelimeleriyle kalibre edildi (`KAT-1`).
    """
    from app.cube_router import _TYPO_MID

    q = _norm(kismi).strip()
    if not q:
        return []
    onek, bulanik = [], []
    for i, a in enumerate(adaylar):
        e = _norm(a.etiket)
        if e.startswith(q) or any(p.startswith(q) for p in e.split()):
            onek.append((0.0, i))
            continue
        r = difflib.SequenceMatcher(None, q, e).ratio()
        if r >= _TYPO_MID:
            bulanik.append((-r, i))
    onek.sort(key=lambda t: (t[0], len(adaylar[t[1]].etiket)))
    bulanik.sort()
    return [i for _, i in onek][:_HAVUZ] + [i for _, i in bulanik][:_HAVUZ]


#: 🔴 `5.7` — **İNDEKS: SÜRÜM ANAHTARLI, BELLEKTE, BAYATLAYAMAZ.**
#:
#: ⊙ Ölçülen maliyet: her `/oneri` isteği katalogdaki **136 ölçü** etiketini yeniden
#: gömüyordu. Debounce (200 ms) bunu seyreltir ama **kaldırmaz** — bir kullanıcı bir
#: cümlede onlarca istek üretir.
#:
#: ⚠ **Planın «tazelik damgası» maddesi burada bir ADIM İLERİ taşındı** 🅐: bir damga
#: bayatlığı *«beyan eder»*; **sürüm anahtarlı bir önbellek** onu **imkânsız kılar**.
#: Anahtar `schema["version"]`'dır (`mdl_version` deseni — `contracts.py:75` bayatlığı
#: tam bu kıyasla ölçer). Şema değişince anahtar değişir, eski girdi **kullanılamaz**.
#: *Bir değişmezi ilan etmek onu kurmaz; anahtarı değişmezin kendisi yapmak kurar.*
#:
#: ⊘ **Diskte artefakt YOK** ⑪: bu depo bir kez *«gitignore'lu bir derleme
#: artefaktından okuyan ölçüm»* yüzünden aynı kaynakta farklı sayı gördü. Bellekteki
#: önbellek süreçle doğar, süreçle ölür — okunacak bayat bir dosya yoktur.
_INDEKS: dict[str, tuple[tuple[str, ...], object]] = {}


def _anahtar(surum: str, kimlikler: tuple[str, ...]) -> str:
    """Önbellek anahtarının **tek sahibi** ㊲.

    ⚠ İlk yazılışta anahtar **iki yerde** kuruluyordu: `_vektor_sira` `f"{surum}|{n}"`
    üretiyor, `indeks_durumu` düz `surum` arıyordu — yani durum beyanı **hep «yok»**
    diyordu ve kapı bunu ilk koşumda yakaladı. *İki satırın aynı işi yaptığı yerde,
    bir gün biri değişir.*

    ⟳🔴 **DÜZELTİLDİ (denetim ajanı):** anahtar **aday SAYISINA** bağlıydı. Farklı
    allowlist'li iki kiracı aynı sayıya düşerse **aynı girdiye** yazıyorlardı: kimlik
    kontrolü doğruluğu koruyordu ama önbellek **her istekte ıskalıyordu** — yani ölçülen
    `p95 = 49,23 ms` **tek havuzludur** ve çok kiracılıya **taşınmaz** 🅕.
    ⊙ Artık anahtar **kimliklerin özetini** taşıyor: iki farklı havuz **iki ayrı girdi**.
    """
    ozet = hashlib.blake2s("\x00".join(kimlikler).encode("utf-8"),
                           digest_size=8).hexdigest()
    return f"{surum}|{len(kimlikler)}|{ozet}"


def indeks_durumu(schema: dict) -> dict:
    """`④` — indeksin **beyanı**. `durum`: `taze` (bu sürüm önbellekte) ·
    `yok` (henüz kurulmadı) · `kapali` (gömücü yok → vektör ayağı hiç çalışmaz)."""
    from app import vqr

    surum = str(schema.get("version") or "")
    if vqr._embedder() is None:
        return {"durum": "kapali", "surum": surum}
    onek = f"{surum}|"
    taze = any(k.startswith(onek) for k in _INDEKS)
    return {"durum": "taze" if taze else "yok", "surum": surum}


def _vektor_sira(kismi: str, adaylar: list[Aday], _surum: str = "") -> list[int]:
    """Vektör ayağı — **yalnız sıra üretir**, eşik üretmez (`FAZ 0` bulgusu).

    `5.8`: gömücü hazır değilse (`None`) **boş liste** döner ve çağıran leksik ayakla
    devam eder. Bu bir hata değil bir **hâl**dir.

    ⚠ E5 burada **simetrik** kullanılır (soru↔terim): `query: ` öneki **iki tarafa** da
    konur — `FAZ 0` ölçümü de böyle yapıldı, aksi hâlde ölçüm taşınmaz 🅕.
    """
    from app import vqr

    model = vqr._embedder()
    if model is None or not adaylar:
        return []
    onek = "query: "
    try:
        import numpy as np

        # 🔴 `5.7` — aday gömmeleri **sürüm anahtarıyla** önbellekte. Anahtar hem şema
        # sürümünü hem aday **kimliklerini** taşır: allowlist daraldığında havuz da
        # daralır ve eski matris o havuza **uymaz** — sessiz bir hizasızlık yerine
        # açık bir önbellek ıskası olur ㊴.
        kimlikler = tuple(a.kimlik for a in adaylar)
        anahtar = _anahtar(_surum, kimlikler)
        onbellek = _INDEKS.get(anahtar)
        if onbellek is not None and onbellek[0] == kimlikler:
            M = onbellek[1]
        else:
            M = np.asarray(list(model.embed([onek + a.etiket for a in adaylar])),
                           dtype="float32")
            M /= (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
            _INDEKS[anahtar] = (kimlikler, M)
        qv = list(model.embed([onek + kismi]))[0]
        qn = np.asarray(qv, dtype="float32")
        qn /= (np.linalg.norm(qn) + 1e-9)
        skor = M @ qn
        return [int(i) for i in skor.argsort()[::-1][:_HAVUZ]]
    except Exception:  # noqa: BLE001 — öneri katmanı **cevabı bozmaz** (§101.1)
        return []


def ara(kismi: str, schema: dict, *, izinliler: set[str] | None = None,
        limit: int = VARSAYILAN_LIMIT) -> list[Aday]:
    """`5.1` — **saf** arama. Sorgu koşmaz, LLM çağırmaz, durum tutmaz.

    Sıra: ① yetki süzmesi ② iki ayak ③ **RRF** füzyonu ④ kesme.
    """
    havuz = terimler(schema, izinliler)
    if not havuz:
        return []

    lek = _leksik_sira(kismi, havuz)
    vek = _vektor_sira(kismi, havuz, str(schema.get("version") or ""))

    puan: dict[int, float] = {}
    kipler: dict[int, set[str]] = {}
    for ayak, sira in (("leksik", lek), ("vektor", vek)):
        for yer, i in enumerate(sira):
            puan[i] = puan.get(i, 0.0) + 1.0 / (_RRF_K + yer + 1)
            kipler.setdefault(i, set()).add(ayak)

    # ⚠ Eşitlikte **leksik önde** olan kazanır: bir önek eşleşmesi kullanıcının
    # yazdığının **birebir** karşılığıdır; vektör benzerliği bir tahmindir ㊼.
    lek_yer = {i: y for y, i in enumerate(lek)}
    sirali = sorted(puan, key=lambda i: (-puan[i], lek_yer.get(i, 10**6), havuz[i].etiket))
    out: list[Aday] = []
    for i in sirali[:limit]:
        a = havuz[i]
        out.append(Aday(kimlik=a.kimlik, etiket=a.etiket, cube=a.cube,
                        kip="+".join(sorted(kipler[i]))))
    return out
