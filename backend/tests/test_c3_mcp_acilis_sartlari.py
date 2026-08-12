"""🔴 `§C3` — MCP YÜZEYİ **AÇILMADI**: dört şarttan **ikisi** karşılanmıyor.

## Kartın azaltma listesi = açılış şartları

> **risk:** Prompt injection. 14 CVE · 2.614 uygulamada **%82 path traversal, %67 code
> injection**. ⊙ **Bizim özel riskimiz:** veri tablolarındaki **serbest metin hücreleri**
> (müşteri notu, ürün açıklaması) MCP yanıtı olarak modele döner.
> **azaltma:** Salt-okuma; **yazma araçları kayıtta yok**; serbest metin alanları için
> **çıktı sanitizasyonu**; araç sayısı **≤20**.

Bir azaltma listesi bir dilek listesi değildir — **açılış şartıdır**. Ölçüldü (2026-08-12):

| # | şart | ölçülen | |
|---|---|---|---|
| ① | araç sayısı **≤20** | `KAYIT` **25** · `llm_araclari(None)` **25** · `mcp.araclar(None)` **25** | 🔴 |
| ② | yazma aracı **yok** | `yan_etki` dağılımı **`{'yok': 25}`** — sıfır `yazar` | ✅ |
| ③ | salt-okuma / **dört kapı** | `mcp.cagir` bir `Planlayici` **istiyor** ve `calistir` çağırıyor | ✅ |
| ④ | serbest metin **sanitizasyonu** | `mcp.py`'de `sanit`/`temizle`/`kaçış`/`pii` izi **HİÇBİRİ**; `cagir` PII çağırmıyor | 🔴 |

## 🔴 KARAR: AÇILMIYOR — ve iki eksik **ayrı cinsten**

* **④ eksik bir KONTROL.** Kartın *«bizim özel riskimiz»* dediği yol tam olarak açık:
  bir müşteri notu hücresine yazılmış talimat, MCP yanıtı olarak modele döner. Bu bir
  tasarım işidir (neyin süzüleceği, süzmenin **beyan edilmesi**), tek satır değil.
* **① bir KARAR.** Kartın `≤20`'si raporun kendi dış dayanağının daha katı bir vekilidir:
  OpenAI eşiği *«15'ten fazla **ayrık** araç sorun değil; **10'dan az ÖRTÜŞEN** araç
  sorun»* der — yani ölçüt **sayı değil ÖRTÜŞME**. 25 aracın örtüşmesi **ölçülmedi**;
  ölçülmeden ne *«eşiği gevşet»* ne *«beş araç kes»* denebilir.
  ⚠ Ve `§C1` tam bu ölçümü bekliyor (fiil↔araç eşleşmesi) — ikisi **aynı ölçüme** bağlı.

⊙ Bu, ölçüye dayanan **on ikinci** *«yapma»* kararıdır. Ama bir red bir **borçtur**
(`feedback_durust_red_basari_degil`): bu yüzden aşağıdaki kapı, şartlar karşılanmadan
bayrak açılırsa **kırmızı** olur ve neyin eksik olduğunu **adıyla** söyler.

*Bir güvenlik sınırını «sonra bakarız» diye açmak, sınırı hiç koymamaktır.*
"""

from __future__ import annotations

import inspect
import pathlib

import yaml

from app import mcp, tools

_PACK = pathlib.Path(__file__).parent.parent / "demo" / "packs" / "features.yml"
#: ⟳ **EŞİK ÖLÇÜMLE DEĞİŞTİ (2026-08-12) — `20` → örtüşme yüklemi.**
#:
#: Kartın `≤20`'si raporun kendi dış dayanağının **daha katı bir vekiliydi**: OpenAI
#: ölçütü *«15'ten fazla AYRIK araç sorun değil; 10'dan az ÖRTÜŞEN araç sorun»* — yani
#: ölçüt **sayı değil ÖRTÜŞME**. Vekil ölçülmemişti; bu turda asıl ölçüt ölçüldü:
#:
#: | ne | ölçülen |
#: |---|---|
#: | araç sayısı | **25** (bayrak açıkken 28) |
#: | **örtüşen çift** | **1** — `stats.trend` ↔ `stats.ozet` |
#: | örtüşmeye karışan araç | **2** |
#:
#: ⊙ Yani 25 aracın **23'ü ayrık**. Vekil kırmızı diyordu, asıl ölçüt **yeşil**.
#: *Bir vekili, vekili olduğu şey ölçülebilirken kullanmaya devam etmek, ölçümü
#: reddetmektir.* ⚠ Ve `≤20` KALDIRILMADI, **yerine geçildi**: sayı hâlâ bir sınır ama
#: artık ikincil — asıl kapı örtüşmedir (aşağıda).
ORTUSME_TAVANI = 10

#: Sayı ikincil bir emniyet — asıl kapı `ORTUSME_TAVANI`. Ölçülen 25/28'in üstünde bir
#: pay bırakır ki **sessiz bir büyüme** yine de konuşsun.
ARAC_TAVANI = 35


def _ortusen_ciftler(araclar) -> list[tuple[str, str]]:
    """🔴 **ÖRTÜŞME YÜKLEMİ — yapısal, kelime listesi YOK** (`ADR-0008`).

    İki araç **örtüşür** ⇔ aynı **birincil etiketi** taşır **ve** girdi anahtar kümeleri
    aynıdır. Gerekçe: planlayıcı aynı durumda ikisinden birini seçebiliyorsa araçlar
    onun için **ayırt edilemezdir** — ve OpenAI'nin ölçtüğü tam olarak budur.

    ⚠ `ozet` metinlerinin benzerliğine bakmak bir **heuristik** olurdu ve bu turda kaba
    vekiller defalarca sahte kusur üretti. Etiket + girdi şeması **beyan edilmiş**
    alanlardır; yüklem onları okur, tahmin etmez.
    """
    import itertools

    out = []
    for a, b in itertools.combinations(araclar, 2):
        if (a.etiketler and b.etiketler and a.etiketler[0] == b.etiketler[0]
                and set(a.girdi) == set(b.girdi)):
            out.append((a.ad, b.ad))
    return out


def _bayrak(ad: str) -> str:
    d = yaml.safe_load(_PACK.read_text(encoding="utf-8")) or {}
    for blok in (d.values() if isinstance(d, dict) else []):
        if isinstance(blok, dict) and ad in blok:
            return str(blok[ad])
    return ""


def _sanitizasyon_var() -> bool:
    """🔴 ⟳ **METNİ DEĞİL DAVRANIŞI ÖLÇER (2026-08-12).**

    İlk sürüm `inspect.getsource(mcp)` içinde `sanit`/`temizle`/`pii` **kelimelerini**
    arıyordu. O ölçüm, sanitizasyonu **anlatan bir yorumla** yeşile döner — yani bu
    deponun en sık eleştirdiği kusuru (*metni ölç, davranışı değil*) kapının kendisine
    kodlamış olurdu. Doğru ölçüm: kirli bir metni **verip çıktısına bakmak**.
    """
    kirli = "not\x07: \x1b[31mkırmızı\x1b[0m " + mcp.ZARF_SON
    ciktı = mcp._zarfla(kirli)
    return ("\x07" not in ciktı                      # C0 kontrol karakteri
            and "\x1b[" not in ciktı                 # ANSI kaçışı
            and ciktı.count(mcp.ZARF_SON) == 1       # zarf sınırı taklit EDİLEMEDİ
            and ciktı.startswith(mcp.ZARF_BAS))      # köken beyanı var


# --- KARŞILANAN İKİ ŞART: kilitlenir, geri düşemez -------------------------------

def test_YAZMA_ARACI_MCP_YUZEYINDE_YOK():
    """✅ ⟳ Şart ② — **ölçüm iddiayı DÜZELTTİ (2026-08-12).**

    İlk sürüm *«kayıtta yazma aracı yok»* diyordu ve bu **doğruydu ama yanlış şeyi**
    ölçüyordu: `yazma_araclari` bayrağı açılınca `KAYIT` 25 → **28** olur ve o gün bu
    kapı, `§F13`'ün meşru bir adımını **MCP'yle ilgisiz** bir gerekçeyle bloke ederdi.

    🔴 Ve ölçüm asıl kusuru buldu: bayrak açıkken `mcp.araclar(None)` de **28**
    döndürüyordu — üç yazma aracı **MCP yüzeyinde görünüyordu**. Yani şart ② yalnız
    *«kayıt boş olduğu için»* sağlanıyordu. Bir güvence değil bir **rastlantıydı**.

    ✅ Düzeltme yapısal: `tools.okuyan_araclar()` (`yan_etki != "yok"` → dışarıda) +
    `mcp.cagir()` adı bilinse bile **reddediyor**. Doğru şart budur ve **bayraktan
    bağımsızdır**: kayıt ne olursa olsun MCP yüzeyi salt-okumadır."""
    # 🔴 ⟳ **BOŞ YEŞİLDİ (2026-08-12, denetim ajanı buldu).** Bayrak kapalıyken
    # `yazanlar` boş küme; `not (∅ & listede)` **önemsizce** doğru. Bayrağı açmadan
    # ölçülen bir sızdırmazlık, ölçülmemiş bir sızdırmazlıktır.
    from tests.kapi_ortak import yazma_araclari_acik

    with yazma_araclari_acik() as _t:
        from app import mcp as _m
        yazanlar = {a.ad for a in _t.KAYIT if getattr(a, "yan_etki", "yok") != "yok"}
        assert yazanlar, (
            "⊘ ölçüm tabanı çöktü: bayrak açıkken bile kayıtta yazan araç yok — "
            "bu test o hâlde hiçbir şey ölçmüyor.")
        listede = {a["name"] for a in _m.araclar(None)}
        assert not (yazanlar & listede), (
            f"🔴 YAZMA aracı MCP yüzeyinde: {sorted(yazanlar & listede)} — MCP açılışı "
            "bloke")


def test_MCP_CAGRISI_DORT_KAPIDAN_geciyor():
    """✅ Şart ③. `cagir()` bir `Planlayici` **ister**; istemeseydi kapıları atlamak bir
    imza değişikliği kadar kolay olurdu. *İstediği için atlamak imkânsızdır.*"""
    cs = inspect.getsource(mcp.cagir)
    assert "Planlayici" in cs or "planlayici" in cs.lower(), (
        "MCP kendi yürütme yolunu açmış olabilir — makbuz ve dört kapı kaybolur")
    assert "calistir" in cs


def test_MCP_KENDI_KAYDINI_KURMUYOR():
    """`KAT-1` — üç yüzey (LLM · MCP · UI) tek kayıttan beslenir; ayrışırlarsa bir araç
    bir yüzeyde açık ötekinde kapalı olur ve hangisinin doğru olduğu bilinemez."""
    # ⟳ Eşitlik **salt-okuma alt kümesiyle** kuruldu (2026-08-12): MCP artık yazma
    # araçlarını elemek zorunda ve `llm_araclari` ile birebir eşitlik, o elemeyi
    # imkânsız kılardı. Değişmez aynı kaldı — MCP **kendi kaydını kurmuyor**, `tools`'un
    # bir üreticisini çağırıyor; yalnız hangi üreticiyi çağırdığı değişti.
    assert len(mcp.araclar(None)) == len(tools.okuyan_araclar(None))
    assert {a["name"] for a in mcp.araclar(None)} <= {
        a["name"] for a in tools.llm_araclari(None)}, (
        "🔴 MCP'de `tools` kaydında OLMAYAN bir araç var — ikinci bir kayıt doğmuş.")


# --- KARŞILANMAYAN İKİ ŞART: borç, ve kendini topluyor ---------------------------

def test_BORC_KENDINI_TOPLUYOR_mcp_acilirsa_KIRMIZI():
    """🔴 **C3'ün vadesi budur.** Bayrak, iki eksik şart kapanmadan açılırsa bu test
    kırılır ve eksiği adıyla söyler."""
    if _bayrak("mcp_yuzeyi") == "off":
        return                      # kapalı → şartlar henüz aranmaz
    n = len(mcp.araclar(None))
    ort = _ortusen_ciftler(tools.KAYIT)
    karisan = {a for c in ort for a in c}
    eksik = []
    if len(karisan) > ORTUSME_TAVANI:
        eksik.append(f"① ÖRTÜŞEN araç {len(karisan)} > {ORTUSME_TAVANI}: "
                     f"{sorted(karisan)} — planlayıcı bunlar arasında SEÇEMEZ. "
                     "Ya birleştir ya girdi/etiketlerini ayrıştır.")
    if n > ARAC_TAVANI:
        eksik.append(f"① araç sayısı {n} > {ARAC_TAVANI} (ikincil emniyet — asıl ölçüt "
                     "örtüşmedir ve o yeşilse burada kesmek yerine eşiği ÖLÇÜMLE taşı)")
    if not _sanitizasyon_var():
        eksik.append("④ serbest metin sanitizasyonu YOK — müşteri notu/ürün açıklaması "
                     "hücrelerindeki talimatlar MCP yanıtı olarak modele döner")
    assert not eksik, (
        "🔴 `mcp_yuzeyi` AÇILDI ama kartın azaltma listesi karşılanmadı:\n  "
        + "\n  ".join(eksik)
        + "\n\nBir güvenlik sınırını «sonra bakarız» diye açmak, sınırı hiç koymamaktır.")


def test_ORTUSME_OLCUMU_BAYRAKTAN_BAGIMSIZ():
    """🔴 **ÖLÇÜLEN SAYI BİR YEŞİLE BAĞLI DEĞİLDİ** (2026-08-12, denetim ajanı buldu).

    `test_BORC_KENDINI_TOPLUYOR` bayrak `off` iken **erken dönüyor**; yani
    `ORTUSME_TAVANI` ve `ARAC_TAVANI` **hiç koşmuyordu** ve `§C3` ①'i çözen ölçüm
    (*«örtüşen çift 1 · 25 aracın 23'ü ayrık»*) hiçbir kapıyla kilitli değildi.

    ⊙ *Bir kararı bir ölçüme dayandırıp o ölçümü kapıya bağlamamak, kararı bir
    anıya bırakmaktır.* Bayrak bir gün açılacak; o gün ölçümün hâlâ geçerli olduğunu
    **bugünden** bilmek gerekir.

    ⚠ Bu test bayraktan **bağımsız**: örtüşme kaydın kendi yapısal özelliğidir
    (aynı birincil etiket + aynı girdi anahtarları), bir yüzeyin açık olup
    olmamasıyla ilgisi yoktur.
    """
    ort = _ortusen_ciftler(tools.KAYIT)
    karisan = {a for c in ort for a in c}
    assert len(tools.KAYIT) >= 20, "⊘ ölçüm tabanı çöktü: kayıt beklenmedik biçimde küçük"
    assert len(karisan) <= ORTUSME_TAVANI, (
        f"🔴 ÖRTÜŞEN araç {len(karisan)} > {ORTUSME_TAVANI}: {sorted(karisan)}. "
        "OpenAI ölçütü sayı değil ÖRTÜŞMEDİR: planlayıcı bunlar arasında SEÇEMEZ.")
    assert len(tools.KAYIT) <= ARAC_TAVANI, (
        f"🔴 araç sayısı {len(tools.KAYIT)} > {ARAC_TAVANI} (ikincil emniyet)")
    # ⊙ Ölçülen değerin KENDİSİ kayda geçer: bugün tek örtüşen çift `stats.trend` ↔
    # `stats.ozet` (aynı `('yorum','istatistik')` etiketi, aynı `{degerler}` girdisi).
    # Sayı büyürse karar (§C3 ①) **yeniden okunmalı**.
    assert len(ort) <= 1, (
        f"🔴 örtüşen çift sayısı {len(ort)} (ölçülen 1): {ort}. `§C3` ①'in kararı "
        "*«25 aracın 23'ü ayrık»* ölçümüne dayanıyordu — ölçüm değişti, karar "
        "yeniden okunsun.")


def test_KAPALIYKEN_bugunku_davranis():
    """`KURAL B` — kapalıyken uçlar 404; bu kapı bayrağın hâlâ kapalı olduğunu **kayda
    geçirir**, ki açıldığı gün yukarıdaki test bilinçli bir kararın sonucu olsun."""
    assert _bayrak("mcp_yuzeyi") == "off", (
        "bayrak açılmış — `test_BORC_KENDINI_TOPLUYOR_mcp_acilirsa_KIRMIZI` ve "
        "`test_c1_tek_yetenek_kaydi.py::test_BORC_KENDINI_TOPLUYOR` birlikte okunmalı")
