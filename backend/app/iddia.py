"""🔴 `G4` — **İDDİA KAPISI**: LLM'in her İDDİASI şemaya karşı doğrulanır.

## Ölçülen boşluk — `narration_guard` kendi sınırını itiraf ediyor

> *"Sayı **İÇERMEYEN** cümleler geçer: bu kapı **sayı uydurmasını** engeller, **üslubu
> değil**."*  — `narration_guard.dogrula` docstring'i

Yani bugün şu üç cümle **hiçbir kapıdan takılmaz**:

| cümle | sınıf |
|---|---|
| *"Fire verisi 2019'dan beri kayıtlı."* | **şema iddiası** — doğrulanmamış |
| *"İstersen tedarikçi kırılımı da ekleyebilirim."* | 🔴 **yetenek iddiası** — o boyut yoksa kullanıcı *"olsun"* der ve **sistem çuvallar** |
| *"Hesabın doğru olduğundan eminim."* | **doğrulanamaz güven beyanı** |

⚠ Üçüncüsü danışman belgesinin **kendi örnek çıktısında** vardı — yani kapının
engellemesi gereken şey, kapıyı öneren belgenin vitrininde duruyordu.

## §4'ün değişmezi İKİYE BÖLÜNÜR

| # | değişmez | neyi korur | kapı |
|---|---|---|---|
| 1 | Sayıyı **KÜP** koyar | **rakam** | `narration_guard` ±%2 |
| 2 | LLM'in her **İDDİASI** şemaya karşı doğrulanır | **cümle** | 🔴 **bu modül** |

Bu §4'ü **gevşetmiyor, İKİYE BÖLÜYOR**. Sayı yolu birebir aynı kalır. Değişen tek şey:
*"cümleyi kim kurar"* sorusunun cevabı artık **ayrı bir kapıya** bağlanıyor, sayı
kapısının yan ürünü olmaktan çıkıyor.

## Desen `narration_guard`'dan — ikinci bir mimari İCAT EDİLMEZ

Cümle cümle çalışır · **düşen cümleyi düşürür** (metnin tamamını değil) · **fail-closed**
· düşme oranını **loglar**. İkisi de `answer.py::seal()`'in önünde durur.

🔴 Ve `narration_guard`'ın kendi dersi burada da geçerli: *"kullanılamayan kapı kapatılır
ve o zaman hiç yoktur."* Bu yüzden düşme oranı **ölçülür** — kapı agresifse gevşetilir,
ama **ölçüyle**, sezgiyle değil.

## Bedava denetim

Kapı **deterministik** metinlerde de koşar. Orada bir cümle düşerse **deterministik yolda
bir kusur var demektir** — yani bu kapı LLM'i denetlerken kendi mutfağını da denetler.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.logging_setup import get_logger

_log = get_logger("iddia")

#: 🔴 **CÜMLE AYIRICI ÖDÜNÇ ALINIR, KOPYALANMAZ.**
#:
#: İlk sürüm kendi regex'ini yazdı ve `test_IKINCI_DOGRULAMA_MIMARISI_YOK` **haklı olarak**
#: kırmızı verdi: yazdığım desen (`(?<=[.!?])\s+`) sahibinin deseninden **farklıydı**
#: (gerçeği: `(?<=[.!?…])\s+(?=[^\d])|\n+` — üç nokta ve *"1. madde"* koruması var).
#: İki farklı cümle tanımı, iki farklı kapı davranışı demekti — ve fark **sessiz** olurdu.
#: *Bir deseni varsaymak, onu okumaktan her zaman daha pahalıdır.*
from app.narration_guard import _CUMLE_RE  # noqa: E402  (tek sahip)

_TOKEN_RE = re.compile(r"[0-9A-Za-zçÇğĞıİöÖşŞüÜ_]+")

#: 🔴 **İZİNLİ SÖZ-EDİMLERİ** — kapalı liste, gerekçeli.
#:
#: Garson bunları **serbestçe** söyleyebilir çünkü hiçbiri şema hakkında bir iddia
#: taşımaz: *sor · var olanı öner · ne yaptığını açıkla · bilmediğini söyle*.
#: ⚠ Liste **kapalı** ve kısa; büyümesi bir ürün kararıdır, bir düzeltme değil.
_IZINLI_KALIPLAR = (
    "hangi", "ister misin", "mi demek istedin", "seçebilirsin", "bakabilirim",
    "gösterebilirim", "anladığım", "bu soruyu", "kapsam dışı", "veri yok",
    "bulamadım", "anlayamadım", "yapamıyorum", "desteklenmiyor",
)

#: 🔴 **YETENEK VAADİ** kalıpları — en tehlikeli sınıf.
#:
#: Ölçülmüş hasar: *"İstersen tedarikçi kırılımı da ekleyebilirim"* → o boyut yoksa
#: kullanıcı *"olsun"* der ve **sistem çuvallar**. Bir vaat, tutulamadığında bir
#: kusurdan **daha pahalıdır**: kullanıcı ona göre plan yapar.
_VAAT_KALIPLARI = (
    "ekleyebilirim", "çıkarabilirim", "hesaplayabilirim", "tahmin edebilirim",
    "öngörebilirim", "kırılım da", "detaylandırabilirim", "karşılaştırabilirim",
)

#: 🔴 **DOĞRULANAMAZ GÜVEN** — sistem kendi doğruluğuna kefil olamaz.
#:
#: Kanıt `QueryContract`'tadır; bir cümle onun yerine geçemez. *"Eminim" demek, kanıtı
#: göstermenin yerine geçmez; kanıtın yerine geçtiğini sanmak ise onu gizler.*
_GUVEN_KALIPLARI = (
    "eminim", "kesinlikle doğru", "hatasız", "garanti ederim", "şüphesiz",
    "kesin olarak", "yüzde yüz",
)


@dataclass
class Rapor:
    """`narration_guard.Rapor` ile **aynı şekil** — çağıran iki kapıyı aynı biçimde okur."""

    gecti: bool
    temiz_metin: str
    reddedilen: list[str] = field(default_factory=list)
    gerekceler: list[str] = field(default_factory=list)
    #: 🔴 `Ö5` — **PAYDA** (bkz. `narration_guard.Rapor.toplam_cumle`). Bölmeyi yapan
    #: fonksiyon üretir; çağıran yeniden bölmez.
    toplam_cumle: int = 0

    def makbuza(self) -> dict:
        return {"dusen_cumle": len(self.reddedilen),
                "gerekceler": self.gerekceler[:10]}


def katalog_terimleri(schema: dict | None, *, norm=None) -> set[str]:
    """Şemadaki **tüm** ad ve sinonimler — bir iddianın dayanabileceği kelime kümesi.

    🔴 **İKİ SAHİPTİ, TEKE İNDİ — ve ikisinden biri EKSİK OKUYORDU.**

    `app/yetenek.py` bu taramanın ikinci bir kopyasını taşıyordu ve o kopyanın kendi
    şerhi buradaki kusuru **zaten yazmıştı**:

    > *"`WrenService.schema()` şekli paket YAML'ından **farklıdır**… İlk yazımda yalnız
    > paket şekli okundu ve gerçek şemada küme **boş kaldı**."*

    O ders orada öğrenildi, **burada uygulanmadı**. Buradaki sürüm gerçek şemada:

    | eksik | sonucu |
    |---|---|
    | `dimension_synonyms` hiç okunmuyordu *(`dimension_labels` aranıyordu — o alan YOK)* | boyut sinonimi anan meşru bir vaat **düşürülüyordu** |
    | `time_dimensions` hiç okunmuyordu | aynı |
    | `!` soneki soyulmuyordu | *"ciro!"* ≠ *"ciro"* |

    ⚠ Yön önemli: kapı *"vaat katalogda karşılık buluyor mu"* diye sorar, yani eksik bir
    küme **yanlış DÜŞÜRME** üretir — sessiz bir kapsam kaybı. Fail-closed bir kapının
    eksik beslenmesi, onu katı değil **kör** yapar.

    *Bir dersi bir dosyada öğrenip ötekine taşımamak, onu öğrenmemekle aynı sonucu verir.*

    `norm` — çağıranın eşleştirme politikası. Tarama katalog bilgisidir ve **burada**;
    normalleştirme eşleştirme politikasıdır ve **çağıranındır** (`yetenek` Türkçe
    düzleştirme ister, bu modül düz `lower()` ile çalışır).
    """
    f = norm or (lambda s: str(s).lower())
    out: set[str] = set()
    for c in (schema or {}).get("cubes", []) or []:
        for anahtar in ("name", "label"):
            if v := c.get(anahtar):
                out.add(f(str(v)))
        for s in c.get("synonyms") or []:
            out.add(f(str(s).removesuffix("!")))
        # `schema()` şekli: ad listeleri + AYRI sinonim sözlükleri.
        for alan in ("measures", "dimensions", "time_dimensions"):
            for m in c.get(alan) or []:
                if isinstance(m, dict):                       # paket şekli
                    if ad := m.get("name"):
                        out.add(f(str(ad)))
                    for s in m.get("synonyms") or []:
                        out.add(f(str(s).removesuffix("!")))
                elif m:
                    out.add(f(str(m)))
        for anahtar in ("measure_synonyms", "dimension_synonyms"):
            for _ad, syns in (c.get(anahtar) or {}).items():
                for s in syns or []:
                    out.add(f(str(s).removesuffix("!")))
    out.discard("")
    return out


def _izinli_mi(cumle_kucuk: str) -> bool:
    return any(k in cumle_kucuk for k in _IZINLI_KALIPLAR)


def dogrula(metin: str | None, schema: dict | None = None) -> Rapor:
    """Cümle cümle denetler; **iddia taşıyan cümleyi DÜŞÜRÜR**, metnin tamamını değil.

    🔴 **Fail-closed:** şüphede cümle düşer. Bir cümle eksik kalmak, tutulamayan bir
    vaatten **ucuzdur** — *ikisi aynı ağırlıkta değildir.*

    ⚠ İzinli söz-edimi taşıyan cümle **önce** geçer: *"hangi dönem için bakayım?"*
    içinde `bakabilirim` benzeri bir kalıp geçse de o bir **soru**dur, bir vaat değil.
    """
    if not metin or not metin.strip():
        return Rapor(gecti=True, temiz_metin="")

    kalan: list[str] = []
    reddedilen: list[str] = []
    gerekceler: list[str] = []
    katalog = katalog_terimleri(schema)

    for cumle in (c for c in _CUMLE_RE.split(metin) if c.strip()):
        c = cumle.strip()
        kucuk = c.lower()

        if _izinli_mi(kucuk):
            kalan.append(c)
            continue

        sebep = None
        if any(k in kucuk for k in _GUVEN_KALIPLARI):
            sebep = "doğrulanamaz güven beyanı"
        elif any(k in kucuk for k in _VAAT_KALIPLARI):
            # Vaat ancak **katalogda karşılığı varsa** meşrudur. Katalog verilmediyse
            # doğrulanamaz → fail-closed.
            if not katalog:
                sebep = "yetenek vaadi (katalog yok — doğrulanamaz)"
            else:
                anilan = {t for t in _TOKEN_RE.findall(kucuk) if len(t) >= 4}
                if not (anilan & katalog):
                    sebep = "yetenek vaadi (katalogda karşılığı YOK)"

        if sebep:
            reddedilen.append(c)
            gerekceler.append(f"{sebep}: {c[:60]}")
        else:
            kalan.append(c)

    if reddedilen:
        _log.info("İDDİA KAPISI: %d cümle düştü — %s",
                  len(reddedilen), "; ".join(gerekceler[:3]))
    return Rapor(gecti=not reddedilen, temiz_metin=" ".join(kalan),
                 reddedilen=reddedilen, gerekceler=gerekceler,
                 toplam_cumle=len(kalan) + len(reddedilen))
