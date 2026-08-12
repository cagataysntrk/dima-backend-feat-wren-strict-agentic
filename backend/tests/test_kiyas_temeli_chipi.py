r"""🔴 `FAZ 4` — **KIYAS TEMELİ**: sistem neye göre kıyasladığını *seçer ve söyler*.

## Bu kapının doğuşu — ve planın kusuru

Planın gerekçesi şuydu: *«"RAM-3 neden düşük" cevapsız kalıyor; "diğerlerine göre"
eklenince cevaplanıyor — yani sistem kıyas temelini soramıyor.»*

⟳ **CANLIDA ÖLÇÜLDÜ (13 Ağustos 2026) — gerekçe BAYAT** 🅟. İki kip de cevaplanıyor:

* **çapalı**: *«RAM-3, öteki 10 makine ortalamasından %10,7 düşük (52,45 ↔ akran ort.
  58,76)»* — 11 satır, `contribution._akran_kiyasi`
* **çapasız**: `source=cube+llm`, makbuzun 2. adımı **`KIYASLA`** — *«bir varlığı
  akranlarıyla karşılaştırır (ortalamadan sapma)»* (`plan_semasi.FIIL_ANLAMI`)

㊷ *kartın yapılacağı yapılmış olabilir* — bu oturumda **on ikinci** kez.

**O hâlde bu kapı neden var?** Çünkü yetenek **kapısızdı**: hiçbir test `_akran_kiyasi`'yi
ya da kıyas-temeli chip'ini kod adıyla anmıyordu (㉙ ile arandı, **sıfır** dosya). ㉕ *bir
yetenek zincire bağlanmadıysa sessizce gerileyebilir* — ve gerilediğinde onu geri getiren
şey planın cümlesi değil, **kırmızı bir yüklem** olur.

## Planın `③` maddesi YANLIŞTI — ve buraya düzeltilerek yazıldı

Plan (`§42 · FAZ 4`) şunu istiyordu: *«yön beyansız ölçüde `[akran]` chip'i
sunulmuyor»*. Bu madde uygulansaydı **bugün çalışan cevabı kırardı**: `ort_oee`,
`_yon_beyanli()` gözünde **beyansızdır** — ama *«RAM-3 neden düşük»* onun üstünde
çalışır ve doğrudur.

⊙ Sebebi ölçüldü: katalog `ort_oee`'yi **beyan ediyor** (`oee/metadata.yml:23` →
`lower_is_better: false`, *«B-5 · yüksek = İYİ»*), fakat `wren_service.py:853`
projeksiyonu **yalnız doğru olanları** listeye alıyor → `false` ile *«alan yok»* aynı
kovaya düşüyor. 🆋 *Bir listede olmamak karşıt listede olmak değildir — ve üçüncü hâl
vardır.* Üç kova sayıldı: **72 `true` · 55 `false` · 46 alan yok**.

Doğru ölçüt yönün **beyanı** değil, yargının **yokluğu**dur (`GG8`): akran kıyası bir
**olgudur** (*«%10,7 düşük»*), bir yargı değil (*«kötü»*). Bu yüzden `③` aşağıda
*«chip basılmasın»* diye değil, **«yargı üretilmesin»** diye kapıya çevrildi.
"""

from __future__ import annotations

from app.bicim import KOVA_KIYAS, VARSAYILAN_KOTA
from app.cube_router import _MAX_NEXT_STEPS, suggest_next_steps

_INDEX = {
    "oee": {
        "name": "oee",
        "measures": ["ort_oee", "ort_kullanilabilirlik", "toplam_durus_dakika"],
        "dimensions": ["makine", "hat"],
        "time_dimensions": ["tarih"],
        "dimension_labels": {"makine": "makine", "hat": "hat"},
        "measure_synonyms_display": {"ort_oee": "OEE",
                                     "ort_kullanilabilirlik": "kullanılabilirlik",
                                     "toplam_durus_dakika": "duruş"},
    }
}

_CQ = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"],
       "timeDimensions": [{"dimension": "tarih"}]}


def _kiyas_chipleri(cq: dict, index: dict | None = None) -> list[dict]:
    """Kıyas temeli chip'leri — kaynağa **YENİ** bir `compare` ekleyenler.

    ⚠ *«`compare` taşıyanlar»* demek **yetmez** ve bu kapı yazılırken tam oradan
    kırıldı ③: chip'ler `{**cube_query, …}` ile üretilir, yani kaynak sorgu zaten
    `compare` taşıyorsa **her** chip onu miras alır. Süzgeç mirası değil **eklemeyi**
    aramalı.
    """
    return [a for a in suggest_next_steps(cq, index or _INDEX)
            if a.get("cube_query", {}).get("compare") != cq.get("compare")]


# ── ① KIYAS TEMELİ SUNULUR — ve bir VAAT taşır ────────────────────────────────

def test_kiyas_temeli_chipi_URETILIR():
    """🔴 `FAZ 4·①` — temel **verilmemişse** sistem bir temel **teklif eder**.

    Kullanıcı *«neye göre?»* sorusunu tahmin etmek zorunda kalmaz; şeritte durur.
    """
    assert _kiyas_chipleri(_CQ), (
        "🔴 kıyas temeli chip'i YOK — kullanıcı «diğerlerine göre» demeyi kendisi "
        "bilmek zorunda kalıyor (FAZ 4'ün ölçülmüş kusuru).")


def test_chip_CUBE_QUERY_tasir_sus_chip_yasak():
    """🆈 **Chip'in açıklaması bir vaattir.** `schemas.py:295` `cube_query`'yi zorunlu
    kılar: tıklanınca `/cube` ile **LLM'siz** koşabilmeli. Yalnız etiket taşıyan bir
    chip, tutulmayan bir vaattir."""
    for a in suggest_next_steps(_CQ, _INDEX):
        cq = a.get("cube_query")
        assert cq and cq.get("cube"), f"🔴 süs chip: {a.get('label')!r} — cube_query yok"


# ── ② YANLIŞ-POZİTİF KAPISI (§101.1) ──────────────────────────────────────────

def test_temel_ZATEN_verilmisse_chip_BASILMAZ():
    """🔴 `FAZ 4·②` — `§101.1`: *yanlış pozitif, kusurun kendisinden pahalıdır.*

    Kullanıcı temeli **söylemişse** (`compare` dolu) ona aynı şeyi teklif etmek,
    yaptığı işi geri almasını istemektir.
    """
    assert not _kiyas_chipleri({**_CQ, "compare": "yoy"}), (
        "🔴 kıyas temeli ZATEN verilmişken yine teklif ediliyor — kullanıcının "
        "kararını yok sayan bir chip.")


def test_tetikleyici_SORGUNUN_degil_KUPUN_zaman_ekseni():
    """⚠ ③ **Bu yüklem de önce yanlış yazıldı** — ve canlı ölçüm onu düzeltti.

    *«Sorguda `timeDimensions` yoksa dönem kıyası teklif edilmemeli»* diye yazmıştım;
    ürün chip'i yine basıyordu. **Ürün haklıydı.** `/cube` ile ölçüldü (13 Ağustos):
    zaman ekseni **taşımayan** bir `cube_query` + `compare: yoy` → **11 satır**,
    `ort_oee_gecen` · `ort_oee_degisim_yuzde` doldu. Vaat **tutuluyor** 🆈.

    Doğru tetikleyici **küpün** zaman ekseni sahibi olmasıdır (`index[...]
    ["time_dimensions"]`), sorgunun onu kullanması değil. Küpün ekseni yoksa
    dönem kıyası **anlamsızdır** ve teklif edilmez — asıl kapı budur.
    """
    zamansiz = {"oee": {**_INDEX["oee"], "time_dimensions": []}}
    assert not _kiyas_chipleri(_CQ, zamansiz), (
        "🔴 zaman ekseni OLMAYAN bir küpte dönem kıyası teklif ediliyor — "
        "tıklandığında karşılığı olmayan bir vaat.")
    # ve eksen varken teklif gerçekten geliyor (yüklem her şeye `boş` demiyor 🆊)
    assert _kiyas_chipleri(_CQ)


# ── ③ (DÜZELTİLMİŞ) YÖN BEYANI YOKSA YARGI DA YOKTUR ──────────────────────────

def test_yon_beyansiz_olcude_YARGI_uretilmez_ama_OLGU_uretilir():
    """🔴 `FAZ 4·③` — planın maddesi **ters çevrildi** (bkz. modül başlığı).

    `ort_oee` projeksiyonda beyansız görünür. Kapı *«chip sunma»* demez — çünkü canlı
    cevap doğrudur; kapı **yargı sızmasın** der (`GG8`).

    🅑 Mutasyon: `_yon_beyanli` `True` döndürmeye zorlanırsa `kok_neden` yön yargısı
    üretmeye başlar ve bu yüklem kırılır.
    """
    from app import kok_neden

    assert kok_neden._yon_beyanli("ort_oee", {"lower_is_better": []}) is False, (
        "🔴 beyansız ölçü beyanlı sayıldı — akran kıyası bir OLGU olmaktan çıkıp "
        "YARGI'ya döner (GG8 ihlali).")
    # ve beyan gerçekten okunuyor (yüklem her şeye `False` demiyor 🆊)
    assert kok_neden._yon_beyanli("toplam_durus_dakika",
                                  {"lower_is_better": ["toplam_durus_dakika"]}) is True


# ── ④ ⑯ KOMŞUSUNU BOZUYOR MU ──────────────────────────────────────────────────

def test_chip_tavani_asilmaz_ve_KURAL_B_korunur():
    """⑯ Kıyas chip'i şeride **eklenir**, şeridi **taşırmaz** (`_MAX_NEXT_STEPS`=6);
    ve kota verilmezse çıktı **bayt bayt** eskisidir (`KURAL B`)."""
    adimlar = suggest_next_steps(_CQ, _INDEX)
    assert len(adimlar) <= _MAX_NEXT_STEPS, (
        f"🔴 şerit taştı: {len(adimlar)} > {_MAX_NEXT_STEPS} — görünmeyen bir chip, "
        "olmayan bir chiptir.")
    assert suggest_next_steps(_CQ, _INDEX) == suggest_next_steps(_CQ, _INDEX, None)
    assert suggest_next_steps(_CQ, _INDEX) == suggest_next_steps(_CQ, _INDEX,
                                                                VARSAYILAN_KOTA)


def test_kiyas_kovasi_kapatilinca_chip_DUSER():
    """㉕ Chip **kotaya bağlıdır**, kaçak bir yoldan basılmaz: `KOVA_KIYAS`=0 ise
    kıyas temeli teklif edilmez. (Kova adı `bicim.py`'den gelir — ödünç ad değil 🅒.)"""
    kota = {**VARSAYILAN_KOTA, KOVA_KIYAS: 0}
    kalan = [a for a in suggest_next_steps(_CQ, _INDEX, kota)
             if a.get("cube_query", {}).get("compare")]
    assert not kalan, "🔴 kıyas chip'i kotayı by-pass ediyor — şerit kararı süs olur."
