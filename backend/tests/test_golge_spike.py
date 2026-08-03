"""FAZ 7 — ARAŞTIRMA SIÇRAMALARI: ölçüldü, **ÜÇÜ DE BENİMSENMEDİ**.

Planın disiplini: *"Kör benimseme YOK — önce **ölçülmüş** gölge-mod spike. **Kazanç yoksa
entegre EDİLMEZ.**"* Gölge araç (`lab/golge_spike.py`) kazancın **ÜST SINIRINI** ölçer:
bir teknoloji **en iyi ihtimalle** kaç soruyu kurtarabilirdi? Üst sınır küçükse teknolojiyi
denemenin **maliyeti bile gereksizdir** — ve bu, kütüphaneyi kurmadan bilinebilir.

## (1) Türkçe morfoloji (Zeyrek) — **BENİMSENMEDİ**, üst sınır **%0,48**

2511 gerçekçi isim çekimi denendi; **228'i** çözülemedi. Ama:

* **186'sı olumsuzluk eki** (`-sIz`) ve o red **DOĞRUDUR**: *"firesiz"* semantik olarak
  *"fire"*'ın **zıddıdır**; onu kurtarmak sessiz-yanlış üretirdi. `_NEGATION_SUFFIXES`
  tam bu yüzden var — yani bir kütüphanenin burada "kazancı" değil **zararı** olurdu.
* **30'u** zaten `_SUFFIX_ATOMS`'ta olan eklerden; kayıp morfoloji değil belirsizlik.
* Geriye **12 vaka (%0,48)** kalıyor: `-cIlIk` · `-lArImIz` · `-lArIndA`.

**Karar: entegre EDİLMEZ.** JVM bağımlılığı (Zemberek) ya da bakımı belirsiz bir kısmi
port (Zeyrek) %0,48 için alınmaz. Whitelist gerçekçi çekimlerin **%91'ini** kapsıyor ve
**olumsuzluğu doğru reddediyor** — bir kütüphanenin garanti etmediği şey.

## (2) Semantik eşleştirme (embedding) — **BENİMSENMEDİ**, hedef kümesi YANLIŞ

Embedding ancak leksik yolun **tamamen boş** olduğu yerde (R1) yeni bilgi getirebilir:
**99/470 (%21)**. Ama §6.1h ölçtü: **R1'in tamamı GERÇEK ölçü-düzeyi belirsizliğidir**
(aynı ad iki cube'da). Embedding belirsizliği **çözmez**, yalnız aday üretir — ve o
adaylar §6.1g'nin netleştirme chip'inde **zaten var**. Yani embedding'in hedefi, çözülmüş
bir problem.

## (3) SLM — **spike bile değil**

Eğitim verisi: `verified_query` **0**, `measure_candidate` **0**. Plan zaten *"bugün için
erken, yalnız gözlem"* diyordu; ölçüm onu doğruladı.

## Kısıtlar dürüstçe

`pip install zeyrek` **ağ ister** (CI: `--network none`), `DIMA_VQR_EMBEDDER=off`.
Kütüphanelerin kendisi burada koşturulamadı — ölçülen şey **onların HEDEFİDİR**. Bu bir
zayıflık değil, spike'ın **doğru** biçimi: hedef küçükse kütüphaneyi kurmak gereksizdir.
"""

from __future__ import annotations

import inspect

from app import cube_router as cr
from lab import golge_spike as gs


def test_OLUMSUZLUK_eki_KURTARILMAMALI(schema):
    """Bu fazın en önemli bulgusu: `-sIz` reddi bir KAYIP DEĞİL, doğru davranış."""
    assert {"siz", "suz"} <= set(cr._NEGATION_SUFFIXES)
    cr.reddi_sifirla()
    assert cr.route(cr._norm("bu yil firesiz"), schema) is None, \
        "'firesiz' 'fire' sayıldı — sinonimin ZIDDI, sessiz-yanlış"


def test_SPIKE_olumsuzlugu_KAYIP_saymiyor():
    """Ölçüm aracının kendisi bir bağımlılıktır (MIMARI §6.4). İlk sürüm `-sIz`'i kayıp
    sayıyordu ve Zeyrek'in kazancını **16 kat** abartıyordu."""
    govde = inspect.getsource(gs.morfoloji_spike)
    assert "_NEGATION_SUFFIXES" in govde, "olumsuzluk eki hâlâ kayıp sayılıyor olabilir"
    assert "olumsuzluk_DOGRU_RED" in govde


def test_SPIKE_ISIM_cekimi_kullaniyor():
    """⚠️ İlk sürüm `-(y)İz`'i İSME ekliyordu (`agirlik+yiz` = *"agirlikyiz"*) ve %100
    "kurtarılabilir" gibi anlamsız bir sonuç veriyordu. `-(y)İz` FİİLE eklenir."""
    assert not hasattr(gs, "EKSIK_EK_ADAYLARI"), "hatalı ilk sürüm hâlâ duruyor"
    assert "yiz" not in gs.ISIM_CEKIMLERI, "fiil eki isim çekimi listesinde"
    assert {"lar", "ler", "den", "dan", "imiz"} <= set(gs.ISIM_CEKIMLERI)


def test_WHITELIST_yaygin_cekimleri_KAPSIYOR(schema):
    """Kararın pozitif dayanağı: whitelist zaten iş görüyor."""
    cr.reddi_sifirla()
    temel = cr.route(cr._norm("bu yil ciro"), schema)
    assert temel is not None
    for ek in ("lar", "den", "imiz", "leri", "daki"):
        cr.reddi_sifirla()
        assert cr.route(cr._norm(f"bu yil ciro{ek}"), schema) is not None, \
            f"'ciro{ek}' çözülemedi — whitelist yaygın çekimi kaçırıyor"


def test_GOLGE_araci_CEVABA_karismaz():
    """`--live` yok, yazma yok, `route()` davranışını değiştiren hiçbir şey yok:
    spike **ölçer**, entegre etmez."""
    kaynak = inspect.getsource(gs)
    for yasak in ("_SUFFIX_ATOMS =", "_NEGATION_SUFFIXES =", "cr.route =", "monkeypatch"):
        assert yasak not in kaynak, f"gölge aracı üretimi değiştiriyor: {yasak}"


def test_SPIKE_kisitlarini_ITIRAF_ediyor():
    """Ölçülemeyen kısım gizlenmez: kütüphaneler CI'da koşturulamadı."""
    kaynak = inspect.getsource(gs)
    assert "--network none" in kaynak and "DIMA_VQR_EMBEDDER=off" in kaynak
    assert "HEDEF" in kaynak.upper()


def test_EMBEDDING_hedefi_COZULMUS_problem(schema):
    """R1'in tamamı gerçek belirsizlik (§6.1h) ve netleştirme chip'i (§6.1g) onu zaten
    yüzeye çıkarıyor — embedding'in getireceği yeni bilgi YOK."""
    cr.reddi_sifirla()
    assert cr.route(cr._norm("bu yil bakiye"), schema) is None
    assert cr.red_gerekcesi() == "R1"
    adaylar = cr.measure_cube_candidates(cr._norm("bu yil bakiye"), schema)
    chips = cr.olcu_netlestirme([x for x in {c["name"]: (c, m) for c, m in adaylar}.values()],
                                schema)
    assert len(chips) >= 2, "belirsizlik chip'e dönmüyor — embedding argümanı değişir"
