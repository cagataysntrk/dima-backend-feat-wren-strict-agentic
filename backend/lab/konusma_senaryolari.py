"""FAZ 0.5 — KONUŞMA SENARYOSU DOĞRULAMA (§4.7). Sınıf başına vaka raporu.

    python lab/konusma_senaryolari.py              # hızlı/yapısal (LLM yok, ağsız)
    python lab/konusma_senaryolari.py --json
    python lab/konusma_senaryolari.py --live       # GERÇEK sağlayıcı, SIRALI, hız-sınırlı

## Neden AYRI bir araç, neden `nl_corpus.py`'ye eklenmedi

`nl_corpus.py` **günlük regresyon kilididir** ve sınıf-başına-sayım sözleşmesi
(`nl_corpus_baseline.json`) ona bağlıdır. Yeni senaryo sınıflarını oraya karıştırmak o
tabanı kirletirdi — KURAL A'nın tam olarak yasakladığı şey. Bu araç aynı harness
kalıbını (aynı monkeypatch'ler, aynı TestClient) **çağırır**, kopyalamaz.

## Planın ⟳ SINIR KURALI — bu dosyanın en önemli tasarım kararı

Planın *"her senaryo kendi vaka raporunu üretir"* maddesi bugünkü üreteçle
**sınırsızdır**: `gen_processes` dört şirkette **10.865 tur** üretiyor. Birebir
uygulanırsa binlerce `.md` doğar ve *"her vaka görünür olsun"* amacının **tam tersi**
olur — kimse okuyamaz. Bu yüzden:

* vaka raporu **senaryo SINIFI** başına (tur başına DEĞİL),
* her sınıf raporu **temsilci turun TAM adımlarını** + sınıf-düzeyi özeti taşır,
* `--live` sınıf başına **katmanlı örneklem** koşar ve **düşürülen tur sayısını
  RAPORLAR** — sessiz kırpma yok.

## ERİŞİM ve DOĞRULUK AYRI ölçülür (§4.7-6)

*"Cevap geldi mi"* yeterli değil: gelen `cube_query` **gerçekten** doğru cube/ölçü/
boyutu mu seçti? Bu ayrım **zorunludur**, çünkü bir düzeltmenin "çalıştığı" görünmesi
DOĞRU şeyi düzelttiği anlamına gelmez — 2a-1'de (`elektrik`) tam olarak bu oldu:
yanlış→cevapsız dönüşümü "iyileşme" gibi görünmüştü.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

#: ⚠️ **`tests.conftest` IMPORT EDİLİR EDİLMEZ SAĞLAYICIYI SABİTLER.** `conftest.py:15`
#: koşulsuz `DIMA_LLM_PROVIDER="rule"`, `:26` `DIMA_VQR_EMBEDDER="off"` yazar — testlerin
#: ağa çıkmaması için DOĞRU bir karardır. Ama bu dosya o modülü **env kurulumu** (JWT
#: sırları, geçici DB) için import ediyor ve yan etkiyi de devralıyordu.
#:
#: **SONUÇ: `--live` modu hiçbir zaman GERÇEK sağlayıcı kullanmadı.** Bayrak yalnız
#: monkeypatch'leri (dry_plan/enrich) atlıyordu; LLM hâlâ `rule`, embedder hâlâ kapalıydı.
#: Yani *"gerçek sağlayıcı, sıralı, hız-sınırlı"* beyanı **karşılıksızdı** ve o modla
#: alınan her ölçüm LLM hakkında hiçbir şey söylemiyordu (MIMARI §6.4: *"ölçüm aracının
#: kendisi de bir bağımlılıktır"*).
#:
#: Düzeltme: gerçek ortam değerleri import'tan **ÖNCE** yakalanır, `--live`'da geri
#: yüklenir. `--live` gerçek bir sağlayıcı bulamazsa **koşmaz** (fail-closed): sessizce
#: `rule` ile koşan bir "canlı" tur, hiç koşmamaktan kötüdür — yanlış bir güven verir.
_GERCEK_ORTAM = {k: os.environ.get(k) for k in
                 ("DIMA_LLM_PROVIDER", "DIMA_VQR_EMBEDDER", "DIMA_VQR_PATH",
                  "DIMA_DATABASE_URL", "DIMA_INTERACTION_LOG")}

import tests.conftest as _conf  # noqa: E402,F401  (env kurulumu)
from tests.conftest import make_tenant_user  # noqa: E402


def _canli_ortami_geri_yukle() -> str:
    """`--live` için gerçek sağlayıcıyı geri koyar. Döner: sağlayıcı adı.

    Fail-closed: gerçek bir sağlayıcı yoksa `SystemExit`. *"Canlı"* diye raporlanan bir
    koşumun aslında `rule` ile koşması, bu deponun avladığı *"beyan var, karşılığı yok"*
    sınıfının ta kendisidir."""
    # HANGİ ANAHTAR GERİ ALINIR — ve neden AYRIM var:
    #
    # * `DIMA_LLM_PROVIDER` · `DIMA_VQR_EMBEDDER` · `DIMA_INTERACTION_LOG`:
    #   conftest'in değeri **canlı-özel yolları SUSTURUR** (`cube+llm` üretilmez, VQR
    #   benzerliği hiç tetiklenmez, red gerekçesi hiç yazılmaz). Ortamda değer yoksa
    #   override **silinir** ki üretim varsayılanı geçerli olsun.
    # * `DIMA_DATABASE_URL` · `DIMA_VQR_PATH`: conftest'in İZOLASYONU **korunur** — canlı
    #   bir ölçüm, kullanıcının verisini kirletmemelidir. Yalnız ortamda açıkça verilmişse
    #   ona uyulur.
    CANLI_YOLU_SUSTURANLAR = ("DIMA_LLM_PROVIDER", "DIMA_VQR_EMBEDDER",
                              "DIMA_INTERACTION_LOG")
    for k, v in _GERCEK_ORTAM.items():
        if v is not None:
            os.environ[k] = v
        elif k in CANLI_YOLU_SUSTURANLAR:
            os.environ.pop(k, None)
    # ⚠️ FAZ 0.16 — AYRILMIŞ ÖLÇÜM ANAHTARI, **tek sahipte**. Burada olması bilinçli:
    # `--live` koşan dört aracın dördü de bu fonksiyondan geçer (`deneyim` · `vk_taban` ·
    # `nl_accuracy` · `konusma_senaryolari`), yani anahtar seçimi **bir kez** yazılır.
    # Tanımsızsa hiçbir şey değişmez — bugünkü davranış aynen korunur.
    _olcum_anahtari = os.environ.get("DIMA_MEASURE_KEY", "").strip()
    _olcum_saglayici = os.environ.get("DIMA_MEASURE_PROVIDER", "").strip()
    if _olcum_saglayici:
        os.environ["DIMA_LLM_PROVIDER"] = _olcum_saglayici
    saglayici = os.environ.get("DIMA_LLM_PROVIDER", "")
    if _olcum_anahtari and saglayici not in ("", "rule", "auto"):
        os.environ[f"DIMA_{saglayici.upper()}_API_KEY"] = _olcum_anahtari
    if saglayici in ("", "rule"):
        raise SystemExit(
            "--live GERÇEK bir sağlayıcı ister. `DIMA_LLM_PROVIDER` boş ya da 'rule' — "
            "bu modda koşmak LLM hakkında HİÇBİR ŞEY ölçmez ve 'canlı' etiketi yanıltır. "
            "Sağlayıcıyı ve API anahtarını ayarlayıp tekrar deneyin.")

    # ⚠⚠ ORTAMI GERİ YÜKLEMEK YETMİYOR — AYAR ÖNBELLEĞİ DE TEMİZLENMELİ.
    #
    # `app.config.get_settings` `@lru_cache`'lidir ve **`import app.main` onu DOLDURUR**
    # (ölçüldü: `import app.main` sonrası `cache_info(currsize=1)`). Bu araçlar
    # `tests.conftest`'i modül seviyesinde yükler (env kurulumu için) — yani önbelleğe
    # `provider="rule"` girer ve sonradan yapılan env geri yüklemesi ona HİÇ ULAŞMAZ.
    #
    # Sonuç: `--live` bayrağı **ÜÇÜNCÜ KEZ** karşılıksız kaldı. İlk kusur (conftest'in
    # env'i sabitlemesi) düzeltilmişti; ama o düzeltme ortamı onarıyor, **ayarı** değil.
    # Log kanıtı: "CANLI MOD" yazarken `LLM sağlayıcı: RuleBasedSqlGenerator`.
    from app.config import get_settings

    get_settings.cache_clear()

    # …ve BEYAN ARTIK ÖLÇÜLÜYOR. Env'e bakıp *"canlı"* demek yetmez; gerçekten canlı bir
    # ÜRETİCİ kuruluyor mu, onu sor. Fail-closed: kurulmuyorsa koşma.
    from app.llm import build_generator

    _uretici_nesnesi = build_generator(get_settings())
    uretici = type(_uretici_nesnesi).__name__
    if uretici == "RuleBasedSqlGenerator":
        raise SystemExit(
            f"--live: ortam `{saglayici}` diyor ama kurulan üretici {uretici} — "
            "anahtar yok/geçersiz ya da ayar önbelleği bayat. Bu koşum LLM hakkında "
            "HİÇBİR ŞEY ölçmez; 'canlı' etiketiyle raporlanması yanıltıcı olurdu.")

    _kota_on_ucusu(_uretici_nesnesi)
    kaynak = "ÖLÇÜM anahtarı (ayrılmış)" if _olcum_anahtari else "ürün anahtarı (PAYLAŞIMLI)"
    return f"{saglayici} ({uretici}) · {kaynak}"


def _kota_on_ucusu(uretici) -> None:
    """🔴 FAZ 0.16 KAPISI — **kota tükendiyse KOŞMA.**

    *"Sağlayıcı kuruldu"* ile *"sağlayıcı cevap veriyor"* farklı şeylerdir. Ücretsiz
    katman doyduğunda üretici **kurulur** ama her çağrı `429` döner; koşum yine de
    ilerler ve sonuçta ya boş ya `rule` cevapları ölçülür. Bu operasyonun kendi kaydı:
    *"nemotron-ultra ⊘ **54×429** — ücretsiz katman doydu."*

    Bir **tek** ucuz çağrıyla ön uçuş yapılır. Başarısızsa `SystemExit`: yarım kotayla
    üretilmiş bir sayı, hiç sayı olmamasından **kötüdür** — çünkü ona bakılıp bayrak
    kararı verilir.

    ⚠ Ön uçuş **bir çağrı harcar** ve bu bilinçlidir: bir turun 12-15 çağrısını boşa
    harcamaktansa bir çağrıyla durmak ucuzdur.

    ## 🔴 ÖN UÇUŞ BİR KEZ YANLIŞ ÇAĞRIYI ÖLÇTÜ — ve bir koşumu yanlış-yeşil yaptı

    İlk sürüm yalnız `generate_sql`'i deniyordu. Ölçüldü (2026-08-04, `faz0_4_netlestirme
    --live`): ön uçuş **GEÇTİ**, sonra koşumun her turu *"TÜM sağlayıcılar başarısız"*
    (`429` · `503`) verdi ve alet, LLM hiç cevap vermediği hâlde bir **KARAR** bastı.

    Sebep **kimlik asimetrisi**: Intent yolu `generate_sql`'i değil **`select_cube`**'u
    çağırır, ve o **ayrı bir modele** gider (`*_select_model` — ucuz katman). İki çağrının
    **kotası da ayrıdır**. Yani ön uçuş, koşumun kullanmadığı bir yolu sertifikalıyordu:
    *"ölçüm aracının kendisi de bir bağımlılıktır"* (MIMARI §6.4) sınıfının ön-koşul hâli.

    ⚠ **Ve ön uçuş TEK BAŞINA yetmez:** kota koşumun **ortasında** da tükenebilir. Ön
    koşul bir son koşulun yerini tutmaz — canlı ölçüm yapan alet, LLM'in **gerçekten
    katıldığını** kendi verisinden de doğrulamalıdır (bkz. `faz0_4_netlestirme.karar_ver`).
    """
    import os as _os

    if _os.environ.get("DIMA_KOTA_ON_UCUSU", "").lower() in ("0", "off", "kapali"):
        print("⚠ kota ön uçuşu ATLANDI (DIMA_KOTA_ON_UCUSU kapalı) — koşum kotanın "
              "tükenmiş olması ihtimaline karşı KORUMASIZ", flush=True)
        return
    try:
        cikti = uretici.generate_sql("kaç kayıt var", {"cubes": []})
    except Exception as exc:                                   # noqa: BLE001
        raise SystemExit(
            f"--live KOTA ÖN UÇUŞU BAŞARISIZ: {type(exc).__name__}: {str(exc)[:200]}\n"
            "Kota tükenmiş ya da anahtar geçersiz olabilir. Yarım kotayla üretilmiş bir "
            "ölçüm, bayrak kararına dayanak yapılamaz — koşum DURDURULDU (fail-closed).\n"
            "Ayrılmış ölçüm anahtarı için: DIMA_MEASURE_KEY (+ DIMA_MEASURE_PROVIDER)."
        ) from exc
    if not (cikti or "").strip():
        raise SystemExit(
            "--live KOTA ÖN UÇUŞU BOŞ DÖNDÜ: üretici kuruldu ama cevap üretmiyor. "
            "Koşum DURDURULDU (fail-closed) — bkz. DIMA_MEASURE_KEY.")

    # ── İKİNCİ AYAK: Intent yolunun GERÇEKTEN kullandığı çağrı ────────────────
    # `select_cube` ayrı bir modele gider ve kotası ayrıdır; `generate_sql`'in yeşili
    # onun adına konuşamaz. Üreticide yoksa (eski/dar sağlayıcı) sessizce atlanır —
    # olmayan bir yeteneği zorunlu kılmak, ölçülemeyeni kırmızı göstermek olurdu.
    if not hasattr(uretici, "select_cube"):
        return
    try:
        secim = uretici.select_cube("kaç kayıt var", "", {})
    except Exception as exc:                                   # noqa: BLE001
        raise SystemExit(
            f"--live KOTA ÖN UÇUŞU (select_cube) BAŞARISIZ: {type(exc).__name__}: "
            f"{str(exc)[:200]}\n"
            "`generate_sql` çalışıyor ama Intent yolunun kullandığı `select_cube` "
            "çalışmıyor — İKİSİ AYRI MODELE ve AYRI KOTAYA gider. Bu asimetri bir kez "
            "yanlış-yeşil üretti (2026-08-04). Koşum DURDURULDU (fail-closed).")
    if secim is None:
        raise SystemExit(
            "--live KOTA ÖN UÇUŞU (select_cube) BOŞ DÖNDÜ: Intent yolu cevap üretmiyor. "
            "Koşum DURDURULDU (fail-closed) — Intent'e dayanan her ölçüm anlamsız olurdu.")

RAPOR_DIZINI = Path(__file__).resolve().parent / "reports" / "konusma_senaryolari"
#: `--live` sınıf başına kaç senaryo koşar (katmanlı örneklem).
LIVE_ORNEKLEM = 3
#: `--live` turlar arası bekleme (saniye) — API'ye yığılma YOK (planın açık kısıtı).
#:
#: ⚠️ **ÖLÇÜLEN GERÇEK SINIR (kullanıcı, 2026-08-03): 10 SANİYEDE 10 İSTEK.** Günlük kota
#: değil, **hız** sınırı. Ve bir `/ask` Intent yolunda `consistency_k=3` ile **ÜÇ** LLM
#: çağrısı yapar — yani tur başına maliyet 1 değil 3'tür. 1,5 sn'lik ilk değer saniyede
#: 2 çağrı = 10 sn'de **20 çağrı** demekti, sınırın **iki katı**.
#: 5 sn → 10 sn'de 6 çağrı: tavanın altında ve kaç örneklem koşulursa koşulsun güvenli.
LIVE_BEKLE = 5.0


# ---------------------------------------------------------------- katalog yardımcıları

def _olculer(cube: dict) -> list[tuple[str, str]]:
    """(ölçü_adı, NL kelimesi) — cube'un KENDİ sözlüğünden, elle yazılmaz."""
    disp = cube.get("measure_synonyms_display") or {}
    syn = cube.get("measure_synonyms") or {}
    out = []
    for m in cube.get("measures") or []:
        ad = m if isinstance(m, str) else m.get("name")
        kelime = disp.get(ad) or next(iter(syn.get(ad) or []), None) or ad
        out.append((ad, str(kelime)))
    return out


def _boyutlar(cube: dict) -> list[tuple[str, str]]:
    disp = cube.get("dimension_synonyms_display") or {}
    syn = cube.get("dimension_synonyms") or {}
    out = []
    for d in cube.get("dimensions") or []:
        ad = d if isinstance(d, str) else d.get("name")
        kelime = disp.get(ad) or next(iter(syn.get(ad) or []), None) or ad
        out.append((ad, str(kelime)))
    return out


# ---------------------------------------------------------------- senaryo sınıfları

def _uret(schema: dict) -> list[dict]:
    """Kataloğa göre senaryo üretir. Her sınıf: {sinif, ad, adimlar, bekle}.

    `bekle(adim_index, cevap)` → (gecti: bool, aciklama: str). ERİŞİM ve DOĞRULUK
    ayrı ayrı raporlanır; `bekle` DOĞRULUK kanalıdır.
    """
    cubes = [c for c in (schema.get("cubes") or []) if _olculer(c)]
    senaryolar: list[dict] = []

    from app import cube_router as _cr

    def _net_olcu(cube: dict) -> tuple[str, str] | None:
        """Cube'un BELİRSİZ OLMAYAN ilk ölçüsü — yoksa None.

        ⚠️ **FAZ 8'İN KENDİ BULGUSU (2026-08-03).** İlk sürüm `_olculer(c)[0]`'ı körlemesine
        alıyordu. `bakim` için bu `borç`a, `cari` için yine `borç`a denk geliyordu — ve
        `borç` GERÇEKTEN belirsizdir (`cari` + `mizan`), yani §6.1g'nin netleştirme chip'i
        **doğru şekilde** ateşliyordu. Senaryo o zaman *niyet ettiği şeyi* (konu değişimi ·
        dönem daraltma) değil, **netleştirme yolunu** test ediyor ve "başarısız" raporluyordu.

        `konu_degisimi` **2/5** ve `donem_duzeltme`'nin kalan başarısızlığı bu yüzdendi —
        ikisi de ÜRÜN HATASI DEĞİL, ölçüm aracının hatası. Bu oturumda **beşinci kez**
        aracın kendisi yanlış ölçtü (MIMARI §6.4: *"ölçüm aracının kendisi de bir
        bağımlılıktır"*).
        """
        for m_ad, m_kel in _olculer(cube):
            _cr.reddi_sifirla()
            hit = _cr.route(_cr._norm(f"bu yil {m_kel}"), schema)
            if hit and (hit.get("cube_query") or {}).get("cube") == cube["name"]:
                return (m_ad, m_kel)
        return None

    def ekle(sinif, ad, adimlar, bekle, *, bagimsiz=False):
        """`bagimsiz=True` → adımlar TAKİP sorusu olarak gönderilmez.

        ⚠️ FAZ 9.6 — `vqr_kalicilik` bu bayrak olmadan **yapısal olarak ölçemiyordu**:
        koşum her 2. adıma önceki `cube_query`'yi iliştiriyor, `ask.py` de takip
        sorularında `near_exact`'i **tümden atlıyor**. Yani senaryo, ölçmek için var
        olduğu replay yolunu hiç çalıştırmadan *"replay YOK"* diye ✅ raporluyordu.
        Yeşil bir kapı, ölçmediğini ölçmüş gibi göstermek kırmızıdan kötüdür.
        """
        senaryolar.append({"sinif": sinif, "ad": ad, "adimlar": adimlar, "bekle": bekle,
                           "bagimsiz": bagimsiz})

    def _ve_cube(kontrol, hedef):
        """FAZ 9.7 — DOĞRULUK kanalına **cube kimliği** de dâhil edilir.

        ## Ölçülen kusur

        Bu dosyanın rapor başlığı *"**DOĞRULUK** (doğru cube/dönem/yapı)"* diyordu, ama
        `_cube_dogru` **hiçbir yerden çağrılmıyordu** (denetim, Faz 9). Dokuz sınıftan
        yalnız `konu_degisimi` cevabın cube'una bakıyordu; kalanlarda cevap **yanlış
        cube'dan** gelse bile — dönem filtresi ve `view_hint` doğruysa — vaka **✅ DOĞRU**
        raporlanıyordu. Yani araç, ölçtüğünü iddia ettiği şeyin bir parçasını hiç ölçmüyordu.

        Bu, planın §4.7-6'da *zorunlu* kıldığı ayrımın (erişim ≠ doğruluk) yarım kalması
        demekti: **sessiz-yanlış**, tam da bu aracın görünür kılmak için var olduğu sınıf.

        ## Neden SARMAL, yeni bir kontrol değil

        Hedef cube **inşa gereği** bellidir: `_net_olcu` yalnız `bu yil {m_kel}` sorusunu
        **bu cube'a** çözen bir ölçü seçer. Sarmal, var olan kontrolü bozmadan üstüne biner;
        her sınıfın kendi kontrolünü yeniden yazmak, aynı kuralın dokuz kopyasını doğururdu
        — bu dosyanın az önce `_bitisik`/`_daraldi` ile ödediği bedelin ta kendisi.
        """
        def f(i, d):
            gecti, aciklama = kontrol(i, d)
            if not gecti:
                return gecti, aciklama
            cq = d.get("cube_query") or {}
            gelen = cq.get("cube")
            if gelen and gelen != hedef:
                return False, f"YANLIŞ CUBE: {gelen} (beklenen {hedef}) — {aciklama}"
            return True, aciklama
        return f

    for c in cubes[:6]:                      # katmanlı: ilk 6 cube yeter, hepsi değil
        ad = c["name"]
        _net = _net_olcu(c)
        if _net is None:
            continue          # bu cube'un HİÇBİR ölçüsü tek başına çözülmüyor → senaryo kurulamaz
        (m_ad, m_kel) = _net
        dims = _boyutlar(c)
        d_kel = dims[0][1] if dims else None
        zaman = (c.get("time_dimensions") or [None])[0]
        if not zaman:
            continue

        # a1/a2 — ÇOKLU AY (bitişik). İki alt-vaka: §1.6'nın gözlemlenen "tümü" hatası
        # ("trend" kapsam kapısını kırıyor) ve DAHA KÖTÜ olan sessiz "Ocak-only".
        def _bitisik(i, d):
            """⚠️ FAZ 9.7 — `_daraldi`'da düzeltilen hatanın AYNI DOSYADAKİ İKİNCİ KOPYASI.

            Eski sürüm beklenen cube'un zaman boyutunu (`_z=zaman`) **sabitliyordu**. Ama
            `route()` soruyu BAŞKA bir cube'a çözebilir ve o cube'un zaman boyutu farklıdır
            → çalışan bir dönem filtresi "YOK" diye raporlanırdı. Düzeltme `_daraldi`'ya
            yazıldı, kardeşine yazılmadı: bu deponun kendi *"kimlik asimetrisi"* sınıfı,
            bu kez **ölçüm aracının içinde**.

            MIMARI §6.4: *"ölçüm aracının kendisi de bir bağımlılıktır."*
            """
            cq = d.get("cube_query") or {}
            zamanlar = {t for c2 in (schema.get("cubes") or [])
                        if c2.get("name") == cq.get("cube")
                        for t in (c2.get("time_dimensions") or [])}
            fs = [f for f in (cq.get("filters") or []) if f.get("dimension") in zamanlar]
            if not fs:
                return False, "dönem filtresi YOK — 'tüm zamanlar'a düştü (§1.6 hatası)"
            gte = next((f["value"] for f in fs if f["operator"] == "gte"), None)
            lte = next((f["value"] for f in fs if f["operator"] == "lte"), None)
            if not (gte and lte):
                return False, f"aralık yarım: gte={gte} lte={lte}"
            if not (str(gte).endswith("-01-01") and str(lte).startswith(str(gte)[:4] + "-03")):
                return False, f"aralık ocak–mart değil: {gte}..{lte}"
            return True, f"{gte}..{lte}"

        ekle("coklu_ay_trendli", f"{ad}-trendli",
             [f"ocak şubat mart {m_kel} değişim trendi"], _ve_cube(_bitisik, ad))
        ekle("coklu_ay_trendsiz", f"{ad}-trendsiz",
             [f"ocak şubat mart {m_kel}"], _ve_cube(_bitisik, ad))

        # a7 — AYRIK AY (2a-4). Yeni yetenek; tabanı BURADA alınır.
        def _ayrik(i, d):
            cq = d.get("cube_query") or {}
            isaret = cq.get("ayrik_aylar") or {}
            if not isaret:
                # Netleştirmeye düşmek de KABUL EDİLEBİLİR bir sonuçtur (sessiz-yanlış
                # değil) — ama "cevaplandı" saymayız; ayrımı rapor gösterir.
                return False, ("netleştirmeye düştü" if d.get("suggestions")
                               else f"ayrik_aylar YOK (source={d.get('source')})")
            aylar = isaret.get("aylar") or []
            return (len(aylar) == 2, f"aylar={aylar}")

        ekle("ayrik_ay", f"{ad}-ayrik", [f"ocak ve mart {m_kel}"], _ve_cube(_ayrik, ad))

        # a2 — DÖNEM DÜZELTME TAKİBİ: kontrollü GENİŞ ilk soru + doğal dilde daraltma.
        def _daraldi(i, d):
            """⚠️ ÖLÇÜM ARACININ KENDİ HATASI DÜZELTİLDİ (2026-08-03).

            İlk sürüm beklenen cube'un zaman boyutunu (`_z`) SABİTLİYORDU. Ama `route()`
            soruyu BAŞKA bir cube'a çözebilir (ör. `elektrik` → `surdurulebilirlik`, bilinen
            açık sahiplik kararı) ve o cube'un zaman boyutu FARKLIDIR — kontrol, çalışan bir
            düzeltmeyi "başarısız" sayıyordu. `enerji_makine-daralt` tam olarak böyle YANLIŞ
            raporlandı; elle koşulduğunda `gte 2026-05-02` üretiyordu.

            MIMARI §6.4'ün dersi: *"ölçüm aracının kendisi de bir bağımlılıktır"* —
            `lab/nl_corpus.py` aylarca kırıkken kimse fark etmemişti. Artık dönem filtresi
            CEVABIN KENDİ cube'una göre aranır; hangi boyut olduğu VARSAYILMAZ.
            """
            if i == 0:
                return bool(d.get("cube_query")), "ilk soru"
            cq = d.get("cube_query") or {}
            if not cq:
                return False, f"düzeltme cevabı YOK (not={d.get('note')!r})"
            gelen = cq.get("cube")
            zamanlar = {t for c2 in (schema.get("cubes") or [])
                        if c2.get("name") == gelen
                        for t in (c2.get("time_dimensions") or [])}
            fs = [f for f in (cq.get("filters") or [])
                  if f.get("dimension") in zamanlar]
            return (bool(fs), f"cube={gelen} dönem filtresi={fs or 'YOK'}")

        ekle("donem_duzeltme", f"{ad}-daralt",
             [f"tüm zamanlar {m_kel}", "sadece son 3 ay"], _ve_cube(_daraldi, ad))

        # a5 — GÖRÜNÜM DÖNÜŞÜMÜ: yapı SİLİNMEMELİ (Faz 5'in şartının doğrudan testi).
        if d_kel:
            def _gorunum(i, d):
                if i == 0:
                    return bool(d.get("cube_query")), "ilk rapor"
                if not d.get("cube_query"):
                    return False, "görünüm değişince YAPI KAYBOLDU (Faz 5 şartı ihlali)"
                return (d.get("view_hint") == "pie",
                        f"view_hint={d.get('view_hint')}")

            ekle("gorunum_donusumu", f"{ad}-pasta",
                 [f"bu yıl {d_kel} bazında {m_kel}", "pasta grafik"], _ve_cube(_gorunum, ad))

            # a6 — LİSTE NİYETİ (2a-5). Yeni yetenek; tabanı BURADA alınır.
            def _liste(i, d, _hedef=ad):
                cq = d.get("cube_query") or {}
                if not cq:
                    return False, f"cevapsız (not={d.get('note')!r})"
                if not cq.get("dimensions"):
                    return False, "kırılım YOK — döküm isteğine dejenere toplam"
                return (d.get("view_hint") == "table",
                        f"dims={cq.get('dimensions')} view_hint={d.get('view_hint')}")

            ekle("liste_niyeti", f"{ad}-listele",
                 [f"bu yıl {d_kel} bazında {m_kel} listele"], _ve_cube(_liste, ad))

        # a4 — KONU DEĞİŞİMİ ORTASINDA (başka cube'un ölçüsüne atla).
        digeri, o_net = None, None
        for x in cubes:
            if x["name"] == ad:
                continue
            o_net = _net_olcu(x)
            if o_net:
                digeri = x
                break
        if digeri and d_kel and o_net:
            o_kel = o_net[1]

            def _konu(i, d, _hedef=digeri["name"]):
                if i < 2:
                    return bool(d.get("cube_query")), "hazırlık adımı"
                cq = d.get("cube_query") or {}
                if not cq:
                    return False, f"konu değişince cevap kayboldu (not={d.get('note')!r})"
                return (cq.get("cube") == _hedef, f"cube={cq.get('cube')} beklenen={_hedef}")

            ekle("konu_degisimi", f"{ad}→{digeri['name']}",
                 [f"bu yıl {m_kel}", f"{d_kel} bazında", f"bu yıl {o_kel}"], _konu)

    # a3 — NETLEŞTİRME CHIP'İNE CEVAP VERME (2a-2'nin ürettiği chip'ler gerçekten
    # tıklanabiliyor mu). Belirsiz sinonim KATALOGDAN bulunur, elle yazılmaz.
    from app import cube_router as cr

    belirsiz = None
    for c in cubes:
        for syns in (c.get("measure_synonyms") or {}).values():
            for sy in syns:
                cr.reddi_sifirla()
                if cr.route(f"bu yil {sy}", schema) is None and cr.red_gerekcesi() == "R1":
                    adaylar = cr.measure_cube_candidates(cr._norm(f"bu yil {sy}"), schema)
                    if len({x["name"] for x, _ in adaylar}) >= 2:
                        belirsiz = str(sy)
                        break
            if belirsiz:
                break
        if belirsiz:
            break
    if belirsiz:
        def _chip(i, d):
            if i == 0:
                chips = d.get("suggestions") or []
                return (len(chips) >= 2,
                        f"chip={[s['label'] for s in chips]} not={bool(d.get('note'))}")
            return (bool(d.get("cube_query")),
                    f"chip tıklanınca cube_query={(d.get('cube_query') or {}).get('cube')}")

        # 2. adım çalışma anında ilk chip'in `query`'siyle DOLDURULUR (aşağıda).
        # ⚠️ ERİŞİM MUHASEBESİ NOTU: bu sınıfın İLK adımı BİLEREK `cube_query` üretmez —
        # netleştirme chip'i **geçerli ve doğru** bir cevaptır (§6.1g). `erisim` sayacı
        # "sql/cube_query geldi mi" diye baktığı için bu sınıf **0/1** görünür. Bu bir
        # kusur DEĞİL bir muhasebe artefaktıdır; `dogruluk` kanalı (1/1) gerçeği söyler.
        # Sayacı bu sınıf için gevşetmek metriği ZAYIFLATIRDI (her netleştirme "erişim"
        # sayılırdı) — o yüzden sayaç değil, KAYIT düzeltiliyor.
        ekle("netlestirme_cevabi", f"belirsiz:{belirsiz}",
             [f"bu yıl {belirsiz}", "__CHIP__"], _chip)

    # B — §1.7 VQR KALICILIK: bilerek yanlış çözülen bir soru öğrenilip PARAFRAZINDA
    # aynı yanlış cevabı `source="vqr"` ile geri veriyor mu? Planın ZORUNLU çıktısı.
    def _vqr(i, d):
        """⚠️ FAZ 9.6 — ÜÇÜNCÜ DURUM: `None` = **ÖLÇÜLEMEDİ**.

        §1.7'nin riski yalnız VQR'a bir kayıt YAZILDIYSA doğabilir. `ask.py:2306`
        `learn=(intent_source == "cube+llm")` — yani **saf `cube` yolu VQR'a hiç
        yazmaz**. Bu bir kusur değil, Faz 2b-2'nin ölçülmüş kararıdır: deterministik
        bir cevabı dondurmak kazanç getirmez, router iyileşir ama kayıt iyileşmez.

        Sonuç: LLM'siz (CI) modda bu senaryo **yapısal olarak** replay üretemez.
        Eski sürüm bunu *"parafraz replay YOK ✅"* diye raporluyordu — **ölçmediği bir
        şeyi ölçmüş gibi**. MIMARI §6.5z'nin *"embedder kapalı"* teşhisi de bu yüzden
        eksikti: embedder açılsa bile yazan kimse yok.

        Risk yalnız `--live` + gerçek sağlayıcı + `cube+llm` yolunda görünür.
        """
        if i == 0:
            # ⟳ İKİNCİ TUR: ön koşulun SAĞLANMAMASI bir ürün hatası DEĞİLDİR. Eski sürüm
            # *"ilk cevap üretilmedi"* durumunda `False` dönüyordu ve senaryo, ölçemediği
            # bir riski **başarısız** diye raporluyordu — sahte bir kırmızı, sahte bir
            # yeşil kadar yanıltıcıdır. Her iki durum da artık ⊘ ÖLÇÜLEMEDİ.
            if d.get("source") != "cube+llm":
                return None, (f"ÖLÇÜLEMEDİ — ilk cevap source={d.get('source')}, "
                              "VQR'a YAZILMADI (learn yalnız cube+llm yolunda açık). "
                              "§1.7 riski bu koşumda DOĞAMAZ.")
            return True, "ilk cevap cube+llm → VQR'a yazıldı (ön koşul sağlandı)"
        if (d.get("source") or "") == "vqr":
            return False, ("PARAFRAZ VQR'DAN GELDİ — §1.7 riski CANLI "
                           "(insan onayı olmadan tekrar oynatıldı)")
        return True, f"parafraz source={d.get('source')} (replay YOK)"

    # `bagimsiz=True`: parafraz TAZE bir soru olarak gider. Takip sorusu olarak
    # gönderilseydi `near_exact` hiç çalışmaz, senaryo ölçtüğünü sanırdı.
    # SORU KATALOGDAN SEÇİLİR — elle yazılmaz. Şart: `route()` çözemeyecek ki soru
    # Intent (`cube+llm`) yoluna düşsün; §1.7 riski YALNIZ orada doğabilir (VQR'a yazan
    # tek yol `learn=(intent_source == "cube+llm")`).
    #
    # ⟳ FAZ 9.6 (ikinci tur, `--live` ölçümünden sonra): eski sürüm *"bu yıl elektrik"*
    # sabitliyordu ve o soru **deterministik çözülüyor** → senaryo `cube+llm` yoluna hiç
    # düşmüyor, ⊘ ÖLÇÜLEMEDİ kalıyordu. Bayrak doğruydu, SORU yanlıştı.
    _vqr_soru = None
    for c in cubes:
        for syns in (c.get("measure_synonyms") or {}).values():
            for sy in syns:
                if len(str(sy)) < 5:
                    continue
                _cr.reddi_sifirla()
                if _cr.route(f"bu yil {sy}", schema) is None:
                    _vqr_soru = str(sy)
                    break
            if _vqr_soru:
                break
        if _vqr_soru:
            break

    if _vqr_soru:
        ekle("vqr_kalicilik", f"{_vqr_soru}-parafraz",
             [f"bu yıl {_vqr_soru}", f"bu yılki {_vqr_soru} durumumuz ne kadar"], _vqr,
             bagimsiz=True)

    return senaryolar


# ---------------------------------------------------------------- koşum

def kos(schema, c, senaryolar, *, live: bool, orneklem: int) -> tuple[list[dict], dict]:
    """Senaryoları koşar. Döner: (sonuçlar, {sınıf: düşürülen_tur}) — SESSİZ KIRPMA YOK."""
    from collections import defaultdict

    sinifta: dict[str, int] = defaultdict(int)
    dusurulen: dict[str, int] = defaultdict(int)
    sonuclar: list[dict] = []

    for sen in senaryolar:
        s = sen["sinif"]
        if live and sinifta[s] >= orneklem:
            dusurulen[s] += 1
            continue
        sinifta[s] += 1
        cq = None
        adimlar_raporu = []
        erisim_ok = dogruluk_ok = True
        #: FAZ 9.6 — ÜÇÜNCÜ DURUM. `bekle` `None` dönerse vaka ne GEÇTİ ne KALDI:
        #: **ölçülemedi**. İkisinden birine yuvarlamak bilgi yok eder — yeşile
        #: yuvarlamak *"risk yok"* yalanını, kırmızıya yuvarlamak sahte alarm üretir.
        olculemedi = False
        for i, adim in enumerate(sen["adimlar"]):
            if adim == "__CHIP__":
                chips = (adimlar_raporu[-1]["cevap"].get("suggestions") or []) if adimlar_raporu else []
                if not chips:
                    dogruluk_ok = False
                    adimlar_raporu.append({"soru": "__CHIP__", "cevap": {},
                                           "gecti": False, "aciklama": "tıklanacak chip YOK"})
                    break
                adim = chips[0]["query"]
            body = {"question": adim, "execute": False}
            if cq is not None and i and not sen.get("bagimsiz"):
                body["cube_query"], body["history"] = cq, ["önceki"]
            rr = c.post("/ask", json=body)
            d = rr.json() if rr.status_code == 200 else {"_http": rr.status_code}
            gecti, aciklama = sen["bekle"](i, d)
            if not d.get("sql") and not d.get("cube_query"):
                erisim_ok = False
            if gecti is None:
                olculemedi = True
            elif not gecti:
                dogruluk_ok = False
            adimlar_raporu.append({"soru": adim, "cevap": d, "gecti": gecti,
                                   "aciklama": aciklama})
            if d.get("cube_query"):
                cq = d["cube_query"]
            if live:
                time.sleep(LIVE_BEKLE)      # API'ye yığılma YOK
        sonuclar.append({"sinif": s, "ad": sen["ad"], "adimlar": adimlar_raporu,
                         "erisim": erisim_ok,
                         "dogruluk": (None if olculemedi else dogruluk_ok),
                         "olculemedi": olculemedi})
    return sonuclar, dict(dusurulen)


def _rapor_yaz(sonuclar: list[dict], dusurulen: dict, live: bool) -> None:
    """Vaka raporu SINIF başına — tur başına DEĞİL (planın ⟳ sınır kuralı)."""
    from collections import defaultdict

    RAPOR_DIZINI.mkdir(parents=True, exist_ok=True)
    gruplar: dict[str, list[dict]] = defaultdict(list)
    for r in sonuclar:
        gruplar[r["sinif"]].append(r)

    for sinif, rs in gruplar.items():
        erisim = sum(1 for r in rs if r["erisim"])
        dogru = sum(1 for r in rs if r["dogruluk"] is True)
        olculemez = sum(1 for r in rs if r.get("olculemedi"))
        # TEMSİLCİ TUR: başarısız varsa İLK BAŞARISIZ (öğretici olan odur), yoksa ilki.
        temsilci = next((r for r in rs if r["dogruluk"] is False), rs[0])
        satirlar = [
            f"# Senaryo sınıfı: `{sinif}`", "",
            f"- senaryo sayısı: **{len(rs)}**",
            f"- **ERİŞİM** (cevap üretildi): **{erisim}/{len(rs)}**",
            f"- **DOĞRULUK** (doğru cube/dönem/yapı): **{dogru}/{len(rs) - olculemez}**"
            + (f"  · **ÖLÇÜLEMEDİ: {olculemez}**" if olculemez else ""),
            f"- düşürülen tur (örneklem sınırı): **{dusurulen.get(sinif, 0)}**"
            + ("" if live else "  _(hızlı modda örneklem uygulanmaz)_"),
            "",
            "> ERİŞİM ve DOĞRULUK **ayrı** ölçülür: bir düzeltmenin *çalıştığı* görünmesi,",
            "> DOĞRU şeyi düzelttiği anlamına gelmez (2a-1 `elektrik` dersi — yanlış→cevapsız",
            "> dönüşümü 'iyileşme' gibi görünmüştü).", "",
            f"## Temsilci tur — `{temsilci['ad']}`"
            + ("  ⚠️ (ilk BAŞARISIZ vaka)" if temsilci["dogruluk"] is False
               else "  ⚠️ (ÖLÇÜLEMEDİ)" if temsilci.get("olculemedi") else ""), "",
        ]
        for i, a in enumerate(temsilci["adimlar"]):
            d = a["cevap"]
            cq = d.get("cube_query") or {}
            satirlar += [
                f"### adım {i + 1}: `{a['soru']}`", "",
                f"- sonuç: {'✅' if a['gecti'] else ('⊘ ÖLÇÜLEMEDİ' if a['gecti'] is None else '❌')}"
                f" — {a['aciklama']}",
                f"- source: `{d.get('source')}`",
                f"- cube_query: `{json.dumps(cq, ensure_ascii=False) if cq else 'YOK'}`",
                f"- not: {d.get('note') or '—'}",
                f"- chip: {[s['label'] for s in (d.get('suggestions') or [])] or '—'}",
                f"- trace (son): {(d.get('trace') or ['—'])[-1]}", "",
            ]
        if len(rs) > 1:
            satirlar += ["## Sınıfın tüm vakaları", "",
                         "| senaryo | erişim | doğruluk |", "|---|---|---|"]
            satirlar += [f"| `{r['ad']}` | {'✅' if r['erisim'] else '❌'} "
                         f"| {'✅' if r['dogruluk'] is True else ('⊘' if r.get('olculemedi') else '❌')} |"
                         for r in rs]
        (RAPOR_DIZINI / f"{sinif}.md").write_text("\n".join(satirlar) + "\n",
                                                  encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Faz 0.5 — konuşma senaryosu doğrulama")
    ap.add_argument("--live", action="store_true",
                    help="GERÇEK sağlayıcı, SIRALI ve hız-sınırlı (ağ ister; CI dışı)")
    ap.add_argument("--orneklem", type=int, default=LIVE_ORNEKLEM)
    ap.add_argument("--json", action="store_true")
    # 🔴 FAZ 0.16 — SAHTE KAPI KAPATILDI. Bu iki bayrak olmadan `main()` her yolda
    # `None` dönüyordu ve süreç **her zaman 0** ile çıkıyordu; yani `lab/kapi.py`'nin
    # dördüncü adımı hiçbir koşulda kırmızı veremiyordu (ölçüldü: `returncode == 0`).
    ap.add_argument("--kapi", action="store_true",
                    help="dondurulmuş tabana göre gerileme varsa ÇIKIŞ KODU 1")
    ap.add_argument("--kapi-guncelle", action="store_true",
                    help="mevcut sonucu taban yapar — BİLİNÇLİ bir karardır, "
                         "tabanı düşürmek gerilemeyi kalıcılaştırır")
    args = ap.parse_args()

    from fastapi.testclient import TestClient

    import app.wren_service as ws
    from app.main import create_app

    if not args.live:
        # Hızlı/yapısal mod — `nl_corpus.py` ile AYNI kalıp: DB'ye bağlanmaz, LLM yok.
        ws.WrenService._enrich_categorical = lambda self, *a, **k: None
        ws.WrenService._enrich_cube_dim_values = lambda self, *a, **k: None
        ws.WrenService.dry_plan = lambda self, sql, *a, **k: sql
    else:
        # ⚠️ `tests.conftest` sağlayıcıyı `rule`'a SABİTLEMİŞTİ (bkz. modül başındaki not).
        # Bu satır olmadan `--live` etiketi yalan söylüyordu.
        _sag = _canli_ortami_geri_yukle()
        print(f"CANLI MOD — sağlayıcı: {_sag} · embedder: "
              f"{os.environ.get('DIMA_VQR_EMBEDDER') or 'AÇIK (varsayılan)'} · "
              f"telemetri: {os.environ.get('DIMA_INTERACTION_LOG') or 'AÇIK (varsayılan)'}",
              flush=True)

    make_tenant_user("owner@dima.local", "owner-parola-123", tenant_slug=None)
    c = TestClient(create_app())
    c.__enter__()
    r = c.post("/auth/login", json={"email": "owner@dima.local",
                                    "password": "owner-parola-123"})
    assert r.status_code == 200, r.text
    c.headers["Authorization"] = f"Bearer {r.json()['access_token']}"
    schema = c.get("/schema").json()

    senaryolar = _uret(schema)
    sonuclar, dusurulen = kos(schema, c, senaryolar, live=args.live,
                              orneklem=args.orneklem)
    c.__exit__(None, None, None)
    _rapor_yaz(sonuclar, dusurulen, args.live)

    from collections import defaultdict
    ozet: dict = defaultdict(lambda: {"n": 0, "erisim": 0, "dogruluk": 0, "olculemedi": 0})
    for s in sonuclar:
        o = ozet[s["sinif"]]
        o["n"] += 1
        o["erisim"] += int(s["erisim"])
        o["dogruluk"] += int(s["dogruluk"] is True)
        o["olculemedi"] += int(bool(s.get("olculemedi")))
    cikti = {"mod": "live" if args.live else "yapisal",
             "sinif_sayisi": len(ozet), "senaryo_sayisi": len(sonuclar),
             "dusurulen_tur": dusurulen, "siniflar": dict(ozet),
             "rapor_dizini": str(RAPOR_DIZINI)}
    if args.json:
        print(json.dumps(cikti, ensure_ascii=False, indent=2))
        return
    print("=" * 74)
    print(f"FAZ 0.5 — KONUŞMA SENARYOSU DOĞRULAMA  ·  mod={cikti['mod']}")
    print("=" * 74)
    print(f"{'sınıf':<24}{'n':>4}{'ERİŞİM':>9}{'DOĞRULUK':>11}{'ÖLÇÜLEMEDİ':>12}   düşürülen")
    for s, o in sorted(ozet.items()):
        print(f"  {s:<22}{o['n']:>4}{o['erisim']:>9}{o['dogruluk']:>11}"
              f"{o['olculemedi']:>12}{dusurulen.get(s, 0):>12}")
    if any(o["olculemedi"] for o in ozet.values()):
        print("⊘ ÖLÇÜLEMEDİ: vaka ne geçti ne kaldı — ölçüm ön koşulu sağlanmadı "
              "(ör. VQR kalıcılığı için `cube+llm` yolu gerekir; CI'da LLM yok). "
              "Yeşile yuvarlamak 'risk yok' YALANI üretirdi.")
    print(f"\nVaka raporları (SINIF başına): {RAPOR_DIZINI}")
    if dusurulen:
        print(f"⚠ örneklem sınırıyla DÜŞÜRÜLEN tur: {dusurulen} — sessiz kırpma yok")

    if args.kapi_guncelle:
        _tabani_dondur(ozet, kaynak=" ".join(sys.argv[1:]) or "elle")
    if args.kapi:
        gecti, satirlar = kapi_degerlendir(ozet, dusurulen)
        print("\n" + "\n".join(satirlar))
        if not gecti:
            print("\nKAPI KIRMIZI — dondurulmuş tabana göre gerileme var.")
            raise SystemExit(1)
        print("\nKAPI YEŞİL")


#: Dondurulmuş taban — `nl_corpus.py`'nin deseniyle **aynı**, ayrı dosyada.
KAPI_TABANI = Path(__file__).resolve().parent / "konusma_senaryolari_baseline.json"


def kapi_degerlendir(ozet: dict, dusurulen: dict) -> tuple[bool, list[str]]:
    """Taze koşumu **dondurulmuş tabanla** kıyaslar. Döner: (geçti, satırlar).

    🔴 **BU FONKSİYON BİR SAHTE KAPIDAN DOĞDU.** `main()` her yolda `None` dönüyordu →
    süreç **her zaman 0** ile çıkıyordu → `lab/kapi.py`'nin dördüncü adımı *"konuşma
    senaryoları"* **hiçbir koşulda kırmızı veremiyordu**. Kapının *"düşürülen 0"* satırı
    bir **rapor**du, bir kapı değil; ve kıpırdamamasının sebebi de buydu. Ölçüldü:
    `subprocess.run(...).returncode == 0` — senaryo tümden çökse bile.

    *"Ölçüm aracının kendisi de bir bağımlılıktır"* (MIMARI §6.4) — bu, o sınıfın
    **kapının kendi içindeki** örneğidir ve en pahalısıdır: dört bileşenli bir kapının
    dörtte biri sessizce dekordu.

    İki şart, ikisi de **sessiz kırpma yasağının** doğrudan uygulanması:
    1. **Düşürülen tur = kırmızı.** Örneklem sınırı bir turu düşürdüyse ölçüm eksiktir.
    2. **Sınıf başına DOĞRULUK tabanın altına düşemez.** `⊘ ÖLÇÜLEMEDİ` bir gerileme
       DEĞİLDİR (üçüncü durum) ama **taban da onu doğru saymaz** — ayrı raporlanır.
    """
    import json as _json

    if not KAPI_TABANI.exists():
        return True, [f"TABAN YOK ({KAPI_TABANI.name}) — kapı ilk koşumda ÖĞRENİR. "
                      "`--kapi-guncelle` ile dondur."]
    taban = _json.loads(KAPI_TABANI.read_text(encoding="utf-8"))
    beklenen = taban.get("siniflar") or {}
    satirlar = [f"TABAN: {taban.get('kaynak', '—')}"]
    gecti = True

    if dusurulen:
        gecti = False
        satirlar.append(f"  🔴 DÜŞÜRÜLEN TUR: {dusurulen} — sessiz kırpma yasağı ihlali")

    for sinif, o in sorted(ozet.items()):
        b = beklenen.get(sinif)
        if b is None:
            satirlar.append(f"  {sinif}: doğruluk {o['dogruluk']}/{o['n']} (tabanda YOK)")
            continue
        isaret = "✅" if o["dogruluk"] >= b else "🔴"
        if o["dogruluk"] < b:
            gecti = False
        satirlar.append(f"  {sinif}: doğruluk {o['dogruluk']}/{o['n']} (taban {b}) {isaret}"
                        + (f" · ⊘ {o['olculemedi']}" if o["olculemedi"] else ""))
    return gecti, satirlar


def _tabani_dondur(ozet: dict, kaynak: str) -> None:
    """`--kapi-guncelle`: mevcut sonucu taban yapar. **Bilinçli bir karardır** —
    tabanı düşürmek, gerilemeyi kalıcılaştırmaktır; gerekçesi commit mesajına yazılır."""
    import json as _json

    KAPI_TABANI.write_text(_json.dumps(
        {"kaynak": kaynak,
         "siniflar": {s: o["dogruluk"] for s, o in sorted(ozet.items())}},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\ntaban donduruldu → {KAPI_TABANI}")


if __name__ == "__main__":
    main()
