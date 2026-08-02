"""Kolon hassasiyet sınıflandırması (Faz A1) — **tek kaynak**.

## Neden var

`WrenService.schema()` düşük kardinaliteli kolonlardan gerçek değerleri örnekleyip `values`
alanına koyuyor; iki ayrı prompt üreticisi (`app/llm.py::_schema_prompt` ve
`app/cube_router.py::build_catalog`) bu değerleri **birebir LLM prompt'una** yazıyor.

**Ölçüldü (2 Ağustos 2026, demo-boyahane):** `_schema_prompt` **1391 değer / 188 satır**
gönderiyordu — içinde `personel.ad_soyad` (tam ad-soyad), `personel_ozluk.sgk_no`,
`banka_hesaplari.iban`, banka adları, müşteri/tedarikçi kodları. `build_catalog` ise daha dar
bir politika uyguluyordu (358 değer). Yani **aynı LLM'e iki farklı gizlilik politikası**.

Demo verisinde TCKN maskeli görünüyordu (`***674894**`) — ama bu maske **verinin kendisinde**,
kodda değil. Gerçek bir müşteri veritabanında gerçek TCKN prompt'a giderdi.

`app/pii.py` bunu yakalayamaz: o bir **çıktı** maskeleyicisidir (`apply_to_ask_response`) ve
prompt yolunda hiç çalışmaz. Ayrıca regex tabanlıdır — ad-soyad gibi serbest metni yapısal
olarak yakalayamaz (`mask_text("AYLİN BULUT")` → değişmeden döner).

## Çözümün yeri: PROMPT SINIRI (kaynak değil)

İlk tasarım değerleri **kaynakta** elemekti — ama bu bir işlevsellik kaybı olurdu:
`cube_router.route()` de aynı `values` alanını okuyor ve *"Aylin Bulut'un firesi ne kadar?"*
gibi bir soruyu **deterministik** (LLM'siz, sıfır token) çözmek için değerleri görmesi gerekir.
O kod **süreç içinde** çalışır; veri kurumdan çıkmaz.

Gerçek sınır *"veriyi kim görüyor"* değil, **"veri nereye gidiyor"**dur. Bu yüzden:
- `schema()` değerleri üretmeye devam eder ve kolona `sensitivity` **damgası** basar;
- **prompt sınırında** `prompt_safe_values()` süzer — LLM'e giden her yol bundan geçer;
- CI testi, hangi yoldan giderse gitsin prompt çıktısının hassas değer içermediğini doğrular.

Üçüncü bir prompt üreticisi eklenirse CI testi onu yakalar (üretici listesini değil, **çıktıyı**
denetler). MIMARI.md §5'in *"kök nedeni düzelt"* disiplini burada "tek süzgeç + çıktı denetimi"
olarak uygulanır.

## Sınıflar

- `person`  — kişisel veri (KVKK md. 5): ad-soyad, TCKN, iletişim, IBAN, sicil/SGK no, doğum.
- `special` — **özel nitelikli** kişisel veri (KVKK md. 6): sağlık, din, üyelik, biyometrik,
  ceza mahkûmiyeti. Ayrı ve daha katı hukuki rejime tabidir; bu yüzden ayrı sınıf.
- `normal`  — sınıflandırılmamış; değer örneklemesine ve prompt'a girebilir.

## Beyan > tahmin

Doğru yol kolonu **YAML'da beyan etmektir** (`sensitivity: person`). Ad-tabanlı sınıflandırma
bir **emniyet ağıdır**: kimse beyan etmeyi unutunca sık görülen kişisel-veri kolon adlarını
yine de yakalar. Emniyet ağı olduğu için **geniş** tutulur; yanlış pozitifin bedeli yalnız o
kolonun LLM'e örnek değer göndermemesidir (rapor/çıktı etkilenmez), yanlış negatifin bedeli
ise kişisel verinin üçüncü taraf bir LLM sağlayıcısına gitmesidir. **Asimetri bilinçlidir.**
"""

from __future__ import annotations

# Kişisel veri işaret eden ad parçaları (normalize edilmiş: küçük harf, Türkçe karakter
# düzleştirilmiş). Alt-dize eşleşmesi bilinçli — `musteri_ad_soyad`, `iletisim_eposta`,
# `p_tckn` gibi önekli/sonekli varyantları da yakalar.
_PERSON_TOKENS = (
    "tckn", "tc_kimlik", "tc_no", "kimlik_no", "vatandaslik",
    "ad_soyad", "adsoyad", "adi_soyadi", "isim_soyisim",
    "eposta", "e_posta", "email", "mail",
    "telefon", "gsm", "cep_no", "cep_tel",
    "iban", "hesap_no", "kart_no",
    "sgk", "sicil", "personel_no", "personel_kod",
    "dogum_tarihi", "dogum_yeri",
    "adres", "ikametgah",
    "plaka", "ehliyet", "pasaport",
)

# Özel nitelikli (KVKK md. 6) — daha katı rejim.
_SPECIAL_TOKENS = (
    "saglik", "hastalik", "tani", "rapor_kodu", "kan_grubu", "engel",
    "din", "mezhep", "inanc",
    "sendika", "dernek", "vakif_uye",
    "biyometrik", "parmak_izi", "genetik",
    "sabika", "ceza", "mahkumiyet",
    "etnik", "irk", "cinsel",
)

_GECERLI = ("person", "special", "normal")


def _norm_ad(ad: str) -> str:
    """Kolon adını sınıflandırma için normalize eder (Türkçe karakter → ASCII, küçük harf)."""
    s = (ad or "").lower()
    for a, b in (("ı", "i"), ("İ", "i"), ("ş", "s"), ("ğ", "g"),
                 ("ü", "u"), ("ö", "o"), ("ç", "c"), ("â", "a"), ("î", "i"), ("û", "u")):
        s = s.replace(a, b)
    return s


def classify(column: dict | None, *, column_name: str | None = None) -> str:
    """Kolonun hassasiyet sınıfı: `person` | `special` | `normal`.

    Beyan (`sensitivity` alanı) **her zaman kazanır** — hem `person` demek hem de bir emniyet
    ağı yanlış pozitifini `normal`'e çekmek için. Beyan yoksa ad-tabanlı emniyet ağı çalışır.
    """
    col = column or {}
    beyan = str(col.get("sensitivity") or "").strip().lower()
    if beyan in _GECERLI:
        return beyan

    ad = _norm_ad(column_name if column_name is not None else col.get("name") or "")
    if not ad:
        return "normal"
    if any(t in ad for t in _SPECIAL_TOKENS):
        return "special"
    if any(t in ad for t in _PERSON_TOKENS):
        return "person"
    return "normal"


def is_sensitive(column: dict | None, *, column_name: str | None = None) -> bool:
    """Bu kolonun değerleri LLM'e gösterilebilir mi? (Hassassa: hayır.)"""
    return classify(column, column_name=column_name) != "normal"


def prompt_safe_values(column: dict | None, *, column_name: str | None = None) -> list:
    """LLM prompt'una yazılabilecek değerler — hassas kolonda **boş liste**.

    **LLM'e giden HER yol bundan geçer.** Bugün iki çağıran var
    (`app/llm.py::_schema_prompt`, `app/cube_router.py::build_catalog`); üçüncüsü eklenirse
    `tests/test_llm_veri_sizintisi.py` onu çıktıdan yakalar — test üretici listesini değil
    **üretilen metni** denetler.

    Değerlerin tamamen kaybolması bir bilgi kaybıdır (LLM `WHERE` için birebir değer
    yazamaz), ama bu **kabul edilen** bedeldir: kişisel veri üçüncü taraf bir LLM
    sağlayıcısına gitmez. Deterministik yol (`cube_router.route()`) süreç içinde çalıştığı
    için değerleri görmeye devam eder ve o yetenek KORUNUR.
    """
    if is_sensitive(column, column_name=column_name):
        return []
    return list((column or {}).get("values") or [])
