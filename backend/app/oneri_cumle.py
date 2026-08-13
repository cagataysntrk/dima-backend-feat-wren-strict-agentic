r"""🔴 **ÖNERİ ŞERİDİNİN CÜMLE ÜRETECİ** — ham alan adı değil, **Türkçe cümle**.

`app/oneri.py` bir **ad** üretir (`Aday.etiket`); bu modül o adlardan **tıklanabilir bir
cümle** kurar. İkisi ayrı sorulardır ve ayrı sahipleri vardır:

| | `app/oneri.py` | **bu modül** |
|---|---|---|
| soru | *«kullanıcı ne yazıyor olabilir?»* | *«bunu bir cümle olarak nasıl söylerim?»* |
| çıktı | sıralı `Aday` listesi (etiket) | `Oneri` listesi (**tam cümle** + `cube_query`) |
| bağlam | yok — katalog + kısmi girdi | **çapa** (görünen bağlam) + `Niyet` |

## 🔴 `§3.3` — MENÜ DEĞİL, **TAMAMLAMA**

Planın ayrımı kozmetik değil mimari: bir menü *«ancak bunları yapabilirim»* der, bir
tamamlama *«ne diyeceğini biliyorum»*. Bu modülün ürettiği hiçbir şey **zorunlu** değildir;
kullanıcı yazmaya devam edebilir. Bu yüzden burada bir **red**, bir **soru** ya da bir
**dal** yoktur: yalnız cümleler ve onların sorguları.

## 🔴 `§18.7` — ALAN ADI CÜMLEYE GİRMEZ

Bugünkü kusur ölçüldü: `/oneri` `fire` · `su` · `set` gibi **ham** parçalar döndürüyordu.
Planın kuralı: gömülen de gösterilen de **görünen ad**dır (`measure_synonyms_display` ·
`dimension_labels` · `display`). Bu modül bir etiketi **bulamazsa cümleyi kurmaz** —
`toplam_fire_kg` yazmaktansa o satırı hiç göstermemek yeğdir. *Bir iç adı kullanıcıya
göstermek, katalogun eksiğini kullanıcının sorunu yapmaktır.*

## 🔴 `E-8` — SAF: LLM YOK, SORGU YOK, IO YOK

Sıcak yolda seri ikinci tur yasak. Bu modül **hiçbir** şey koşmaz: ne SQL, ne LLM, ne
dosya. Aynı girdi → **aynı çıktı** (`test_ayni_girdi_ayni_cikti`). Tek dış bağımlılığı
`app/ek.py`'dir (Türkçe ek motoru) ve o da saf bir fonksiyon kümesidir.

## 🔴 `§6 · Thread 3` — SUNULAN HER ÖNERİ **TEMSİL EDİLEBİLİR** OLMALI 🆈

Planın kırılması aynen: *«BU RAPOR ÜZERİNDE önerisi JOIN gerektiriyor ve JOIN planlayıcı
yasağı var.»* Buradaki karşılığı **yapısal**: `BU RAPOR ÜZERİNDE` şeridine yalnız **çapanın
küpünden** aday girer. Başka küpün ölçüsü, çapanın kapsamına ancak bir JOIN ile girebilirdi
— o yüzden o aday `YENİ KONU` şeridine düşer, hiç kaybolmaz. *Bir öneriyi sunmadan önce
koşulabilir olduğunu bilmek, sunduktan sonra özür dilemekten ucuzdur.*

## ⚠ EK MOTORU **YAZILMADI, ÇAĞRILDI** (`KAT-1`)

Ünlü uyumu · yumuşama · kesme işareti · sayı okunuşu **`app/ek.py`'nindir** ve orada
ölçülmüştür. Burada yalnız o motorun kapsamadığı **iki** kural var ve ikisi de kapalı:

1. **İyelik tamlaması** (*«duruş nedeni» → «duruş nedenine»*) — kaynaştırma `-n-`;
   `ek.py`'nin kapsamı *metrik adı · boyut değeri · sayı · tarih*, tamlama değil.
2. **Ünlü düşmesi** (*«şehir» → «şehre»*) — kapalı bir istisna listesi, tıpkı `ek.py`'nin
   kendi `_YUMUSAMAZ` / `_INCE_OKUNAN` listeleri gibi.

🔴 Ve **üçüncü bir kural yazmak yerine ÜÇ KAÇIŞ KAPISI** var: ek güvenle takılamıyorsa
cümle **ek istemeyen** bir kuruluşa düşer —

| belirsizlik | kaçış |
|---|---|
| kısaltmanın okunuşu (*«ABC'nin»* mi *«ABC'ın»* mı?) | *«ABC **için** …»* |
| tamlananın iyelik eki yok (*«RAM-3'ün toplam fire (kg)»* eksik tamlama) | *«RAM-3 **için** …»* |
| **sert ünsüz sonu** (`p·ç·t·k`) — yumuşama bir **listeye** bağlı, kurala değil | *«hat **bazında** …»* |

🔴 Üçüncüsü **ölçüldü** ve genel bir kusurdur: yumuşamanın istisnaları `ek.py`'de kapalı
bir liste (`_YUMUSAMAZ`) ve o liste **anlatıcının** sözcükleriyle kalibre edilmiş. Bu
deponun boyut etiketlerinde `p·ç·t·k` ile biten **her** örnek o listenin dışında kalıyor
ve **üçü de yanlış** çekimleniyor:

    hat      → «hada»    (doğrusu «hatta»)   ⊘ `len < 3` koruması üç harfliyi kaçırır
    renk     → «renğe»   (doğrusu «renge»)   ⊘ `k → ğ` eşlemesi burada `k → g` olmalı
    cinsiyet → «cinsiyede» (doğrusu «cinsiyete»)  ⊘ `devlet`/`millet` sınıfı, listede yok

⟳ **VE ÜÇÜ DE ONARILDI** *(aynı gün, `ek.py`'de — bu paragrafın ilk hâli «onarım orada
değil» diyordu ve o **bayattır** 🅟)*: `hat → hatta` · `renk → renge` · `cinsiyet →
cinsiyete`. İkisi **sözlükseldi** (`_OZEL_GOVDE`/`_YUMUSAMAZ`), biri **kuraldı** — `k`
ünsüzden sonra yumuşamaz (`kürke`·`parka`), ünlüden sonra yumuşar (`göğe`). Kapı:
`tests/test_ek_motoru.py`.

⊙ **Buna rağmen `«… bazında»` kuruluşu KALDI** ve bu bilinçli: onarım üç **ölçülmüş**
etiketi kapattı, ama katalog büyür ve bir sonraki `p·ç·t·k` etiketi listede **olmayacak**.
Yani kuruluş bir yama değil bir **taban**dır: ek isteyen yol doğruyken güzelleşir, yanlış
olduğunda **bozulmaz**. Bu kuruluş bu depoda zaten üretiliyor (`app/drill.py:112`) ve her
sözcükle çalışır. *Bir motorun kapsamını genişletmek ile kapsamının dışına çıkmayan bir
cümle kurmak birbirinin alternatifi değil, birbirinin sigortasıdır.*

*Yanlış bir ek, eksik bir ekten daha görünür bir kusurdur.*
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover — yalnız tip; çalışma anında import YOK (hafiflik)
    from collections.abc import Sequence

    from app.oneri import Aday

__all__ = [
    "GRUP_RAPOR",
    "GRUP_YENI",
    "TUR_DONEM",
    "TUR_KIRILIM",
    "TUR_NEDEN",
    "TUR_OLCU_EKLE",
    "TUR_YENI",
    "Oneri",
    "cumleler",
    "kirilim_ifadesi",
    "tamlayan",
    "yonelme",
]

#: Şeridin iki bandı — `§5.1`'in görünür çapası bu ikisini **ayrı** çizer.
GRUP_RAPOR = "rapor_ustunde"     # ↳ BU RAPOR ÜZERİNDE
GRUP_YENI = "yeni_konu"          # ↳ YENİ KONU

#: Önerinin **ne değiştirdiği** — kapalı küme. Yeni bir tür, yeni bir cümle kalıbı demektir.
TUR_OLCU_EKLE = "olcu_ekle"      # ölçü değişti / eklendi   → `cube_query` taşır
TUR_KIRILIM = "kirilim"          # kırılım eklendi          → `cube_query` taşır
TUR_DONEM = "donem"              # dönem kaydı              → `cube_query` taşır
TUR_NEDEN = "neden"              # 🔴 MAKRO — sorgu değil, `§6/Thread 2`'nin 4 adımı
TUR_YENI = "yeni"                # çapa düştü, yeni rapor   → `cube_query` taşır

#: Cümlede dönemi ayıran çizgi — `§5.1` örneğiyle **birebir** (`—`, em dash).
_CIZGI = "—"

#: 🔴 **ÖNCEKİ DÖNEM — KAPALI TABLO, ve her değeri `date_filters` ile SINANIR.**
#:
#: Bu bir dil kuralı değil, beş ifadelik bir eşleme. Neden kapalı: `route()`'un dönem
#: çözücüsü (`cube_router.date_filters`) yalnız **tanıdığı** ifadeleri çözer; tanımadığı
#: bir ifadeyi öneri olarak sunmak, `§6/Thread 3`'ün *«temsil edilebilir olmalı»* kuralını
#: çiğnerdi. Kapı bunu ölçer: `test_ONCEKI_DONEM_ifadeleri_route_tarafindan_COZULUYOR`.
_ONCEKI_DONEM: dict[str, str] = {
    "bugün": "dün",
    "bu hafta": "geçen hafta",
    "bu ay": "geçen ay",
    "bu çeyrek": "geçen çeyrek",
    "bu yıl": "geçen yıl",
}

#: 3. tekil **iyelik eki** kuyruğu — *«oran-ı» · «neden-i» · «grub-u» · «gün-ü»*.
_IYELIK_SONU = "ıiuü"

#: 🔴 **ÜNLÜ DÜŞMESİ — İKİNCİ KAPALI LİSTE** (`ek.py`'nin `_YUMUSAMAZ` deseni).
#:
#: Ünlüyle başlayan ek alınca ikinci hecesinin ünlüsü düşen sözcükler: *şehir → şehre*.
#: Kuralla türetilemez (*«nehir → nehre»* ama *«demir → demire»*), bu yüzden bir **liste**.
#: ⚠ Liste **dar**: yalnız bir **boyut etiketi** olabilecekler alındı. Bir sözlüğü buraya
#: kopyalamak, kapsamı sessizce genişletmek olurdu.
#: ⚠ Ve yalnız **yönelme** (`-e`) için: bulunma hâlinde düşme **yoktur** (*«şehirde»*
#: doğru, *«şehrde»* değil) — bu modül boyut etiketine yalnız yönelme eki takar.
_UNLU_DUSEN: dict[str, str] = {
    "şehir": "şehr", "isim": "ism", "resim": "resm", "akıl": "akl", "fikir": "fikr",
    "burun": "burn", "ağız": "ağz", "oğul": "oğl", "karın": "karn", "beyin": "beyn",
    "boyun": "boyn", "göğüs": "göğs",
}

#: Yumuşamaya açık son ünsüzler (`ek.py::_YUMUSAMA`'nın anahtarları). Bu harflerle biten
#: bir etikete ek **istenmez**: yumuşayıp yumuşamayacağı bir kurala değil bir **listeye**
#: bağlıdır ve o liste (`ek.py::_YUMUSAMAZ`) başka bir kapsam için kalibre edilmiştir —
#: ölçüldü, bu deponun üç boyut etiketinin (`hat` · `renk` · `cinsiyet`) **üçü de** yanlış
#: çekimleniyor. Gerekçenin tamamı modül başlığında.
_SERT_SON = "pçtk"

#: Değerin **sonundaki** rakam öbeği — *«RAM-3»* → `3` → okunuş *«üç»* → `'ün`.
_SON_RAKAM = re.compile(r"(\d+)\s*$")

#: Değerin **sonundaki** harf öbeği. Yoksa (*«… (08-16)»*) ek takılmaz: bir noktalama
#: işaretinden sonra gelen ek, okunamayan bir ektir.
_SON_HARF = re.compile(r"[^\W\d_]+$", re.UNICODE)


@dataclass(frozen=True)
class Oneri:
    """Şeritte görünen **bir satır**.

    ⚠ `frozen`: bir öneri bir **okuma**dır. Değiştirilebilir olsaydı çağıran onu yerinde
    düzeltmeye başlar ve *«cümleyi kim yazdı»* sorusu doğardı — bu modülün kapatmak için
    var olduğu belirsizliğin ta kendisi (`app/niyet.py::Niyet`'in aynı gerekçesi).

    * `metin`     — **tam Türkçe cümle**; kullanıcıya bu görünür, başka bir şey değil.
    * `grup`      — `GRUP_RAPOR` | `GRUP_YENI` (şeridin hangi bandı).
    * `tur`       — kapalı küme (yukarıda).
    * `cube_query`— tıklanınca koşacak sorgu. `None` yalnız **makro** türlerde olabilir
                    (`TUR_NEDEN`) ve `cumleler()` bunu bir değişmez olarak korur.
    * `kimlik`    — kararlı, tekrarlanabilir kimlik: tıklama kaydı (`/oneri/tik`) ve ön
                    uçtaki `key` bunun üstünde durur.
    """

    kimlik: str
    metin: str
    grup: str
    tur: str
    cube_query: dict | None = None
    cube: str = ""

    @property
    def tiklanabilir(self) -> bool:
        """🔴 Değişmez: her cümle ya bir **sorgu** taşır ya bir **makro**dur."""
        return self.cube_query is not None or self.tur == TUR_NEDEN


# ─────────────────────────────────────────────────────────────────────────────
# TÜRKÇE ÇEKİM — `app/ek.py`'nin **üstünde** iki kural, ikisi de kapalı
# ─────────────────────────────────────────────────────────────────────────────


def iyelik_ekli_mi(etiket: str) -> bool:
    """Etiket bir **iyelik zincirinin** sonu mu — *«fire oranı»* ✅ · *«toplam fire (kg)»* ⊘.

    Ölçüt yapısal ve dar: **çok sözcüklü** bir etiketin **son sözcüğü** dar ünlüyle
    bitiyorsa (*ı/i/u/ü*) o sözcük 3. tekil iyelik eki taşıyor sayılır — Türkçedeki
    belirtisiz isim tamlamasının (*«makine grub-u»*) kuruluşu budur.

    ⚠ Tek sözcüklü etiketler **dışarıda**: *«müşteri»* bir tamlama değildir ve `-n-`
    kaynaştırması alsaydı *«müşterine»* gibi yanlış bir çekim doğardı.
    """
    p = str(etiket or "").split()
    return len(p) >= 2 and p[-1][-1:].lower() in _IYELIK_SONU


def yonelme(etiket: str) -> str:
    """Boyut etiketinin **yönelme** hâli — *«…-e göre»* kuruluşunun tek sahibi.

    *makine → makineye · vardiya → vardiyaya · şehir → şehre · duruş nedeni → duruş
    nedenine · yaş grubu → yaş grubuna · haftanın günü → haftanın gününe*

    Üç dal, üçü de `ek.ek_bagla`'ya iner (ünlü uyumunun ikinci bir sahibi **yok**):

    1. **iyelik tamlaması** → kaynaştırma `-n-`. Numara: gövdenin sonuna `n` eklenip
       `ek_bagla` çağrılır — ünsüzle biten bir gövdeye takılan yönelme eki zaten çıplak
       ünlüdür, yani `n` + `e` tam olarak aranan `-ne` kaynaştırmasıdır. *Bir kuralı
       yeniden yazmak yerine, var olan kuralın girdisi düzeltilir.*
    2. **ünlü düşmesi** → kapalı liste (`_UNLU_DUSEN`).
    3. **düz** → `ek_bagla(son, "e")`.
    """
    from app.ek import ek_bagla

    p = str(etiket or "").split()
    if not p:
        return str(etiket or "")
    son = p[-1]
    if len(p) >= 2 and son[-1:].lower() in _IYELIK_SONU:
        cekim = ek_bagla(son + "n", "e")
    elif son.lower() in _UNLU_DUSEN:
        cekim = ek_bagla(_UNLU_DUSEN[son.lower()], "e")
    else:
        cekim = ek_bagla(son, "e")
    return " ".join([*p[:-1], cekim])


def _ek_guvensiz(sozcuk: str) -> bool:
    """Sert ünsüzle (`p·ç·t·k`) biten sözcükte yönelme eki **güvenilmez**.

    *hat → «hada»* ⊘ · *renk → «renğe»* ⊘ · *cinsiyet → «cinsiyede»* ⊘ — üçü de gerçek
    boyut etiketi, üçü de yanlış. Kural değil **liste** işidir ve liste başka bir kapsam
    için yazılmıştır; burada ek istemek yerine ek istemeyen kuruluşa geçilir.
    """
    s = str(sozcuk or "")
    return bool(s) and s[-1].lower() in _SERT_SON


def kirilim_ifadesi(etiket: str) -> str:
    """*«makineye göre»* — ya da ek güvenilmezse *«hat bazında»*.

    🔴 Cümledeki kırılım kuruluşunun **tek sahibi**. İki kuruluş da bu depoda kullanılıyor
    (*«makineye göre»* `§5.1` · *«… bazında»* `app/drill.py:112`); aralarındaki seçim bir
    üslup tercihi değil bir **kesinlik** kararıdır: eki doğru yazabildiğimizde yönelme,
    yazamadığımızda ek istemeyen kuruluş.
    """
    p = str(etiket or "").split()
    if not p:
        return ""
    if _ek_guvensiz(p[-1]):
        return f"{etiket} bazında"
    return f"{yonelme(etiket)} göre"


def tamlayan(deger: str) -> str | None:
    """Bir **boyut değerinin** tamlayan (ilgi) hâli — *«RAM-3» → «RAM-3'ün»*.

    🔴 `None` = *«bu değere güvenle ek takamam»* ve bu bir **hâl**dir, bir hata değil.
    Çağıran o zaman ek istemeyen bir kuruluşa düşer (*«… için …»*). Üç durum:

    | değer | sonuç | neden |
    |---|---|---|
    | `RAM-3` | `RAM-3'ün` | ek **rakamın okunuşuna** göre (*üç* → `'ün`) — TDK |
    | `Merkez` | `Merkez'in` | özel ad → kesme, yumuşama yok (`ek.py`'nin `kesme=True`) |
    | `ABC` · `1. Vardiya (08-16)` | `None` | kısaltmanın **okunuşu** bilinmiyor · ek noktalamadan sonra gelemez |

    ⚠ Rakam dalında ek `ek_bagla(..., sayi=True)`'den **alınır**, hesaplanmaz: okunuş
    tablosunun (üç·kırk·milyon) ikinci bir kopyası doğmasın diye.
    """
    from app.ek import ek_bagla

    s = str(deger or "").strip()
    if not s:
        return None
    m = _SON_RAKAM.search(s)
    if m:
        cekimli = ek_bagla(m.group(1), "in", sayi=True)     # "3" → "3'ün"
        if "'" not in cekimli:                              # pragma: no cover — savunma
            return None
        return f"{s}'{cekimli.split(chr(39), 1)[1]}"
    h = _SON_HARF.search(s)
    if not h:
        return None                                          # noktalamayla bitiyor
    kuyruk = h.group(0)
    if kuyruk == kuyruk.upper() and kuyruk != kuyruk.lower():
        # 🔴 Kısaltma: *«ABC'nin»* okunuşa (*be-ce*) bağlıdır, harfe değil. Okunuşu
        # bilmiyoruz → ek **uydurulmaz**.
        return None
    return ek_bagla(s, "in", kesme=True)


def _kapsam(varlik: str, etiket: str) -> str:
    """*«RAM-3'ün fire oranı»* ya da *«RAM-3 için toplam fire (kg)»*.

    🔴 İyelik zinciri ancak **tamlanan da iyelik eki taşıyorsa** kurulur. *«RAM-3'ün
    toplam fire (kg)»* eksik bir tamlamadır (doğrusu *«…firesi»*) ve o eki üretmek
    parantezli/birimli etiketlerde uydurma olurdu. Ek gerektirmeyen `için` edatı her
    sözcükle çalışır — `§5.1`'in örneği (*«RAM-3'ün fire oranı»*) birinci dala düşer.
    """
    t = tamlayan(varlik)
    if t and iyelik_ekli_mi(etiket):
        return f"{t} {etiket}"
    return f"{varlik} için {etiket}"


def _donem_eki(donem: str) -> str:
    return f" {_CIZGI} {donem}" if donem else ""


# ─────────────────────────────────────────────────────────────────────────────
# ÇAPA — `§5.1`: bağlam **gizli durum** olmaktan çıkar
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class _Capa:
    """Çapanın **okunmuş** hâli. Yeni bir model değil, `cube_query`'nin izdüşümü."""

    cube: str
    cq: dict
    olculer: tuple[str, ...]
    kirilimlar: tuple[str, ...]
    donem: str          # `period_expr` — kullanıcının **kendi** ifadesi ("bu ay")
    varlik: str         # tekil filtre değeri ("RAM-3")
    varlik_boyut: str   # o filtrenin boyutu ("makine")


def _capa_oku(capa: dict | None) -> _Capa | None:
    """Çapayı oku — **uydurma yok**.

    Kabul edilen iki biçim: doğrudan bir `cube_query`, ya da onu `cube_query` anahtarında
    taşıyan bir sarmalayıcı (takip çapası bu depoda `cube_query`'dir). `cube` yoksa çapa
    da yoktur: `None` döner ve `BU RAPOR ÜZERİNDE` bandı **boş** kalır.

    ⚠ Dönem `period_expr`'den okunur, tarih filtrelerinden **geri çözülmez**: `2026-08-01
    ≤ tarih ≤ 2026-08-31` ifadesinden *«bu ay»*'a dönmek bir tahmindir ve `period_expr`
    zaten kullanıcının **kendi cümlesini** taşır (`cube_router:4937` beyaz listesi).
    """
    if not isinstance(capa, dict) or not capa:
        return None
    ic = capa.get("cube_query")
    cq = ic if isinstance(ic, dict) else capa
    cube = str(cq.get("cube") or "")
    if not cube:
        return None
    varlik, boyut = "", ""
    for f in cq.get("filters") or []:
        if not isinstance(f, dict) or f.get("operator") != "eq":
            continue
        d = str(f.get("dimension") or "")
        v = f.get("value")
        if isinstance(v, list):
            v = v[0] if len(v) == 1 else None
        if d and isinstance(v, (str, int, float)) and str(v).strip():
            varlik, boyut = str(v).strip(), d
            break
    return _Capa(
        cube=cube,
        cq=cq,
        olculer=tuple(str(m) for m in (cq.get("measures") or [])),
        kirilimlar=tuple(str(d) for d in (cq.get("dimensions") or [])),
        donem=str(cq.get("period_expr") or "").strip(),
        varlik=varlik,
        varlik_boyut=boyut,
    )


# ─────────────────────────────────────────────────────────────────────────────
# KATALOG ETİKETLERİ — tek kaynak, ve **bulunamazsa cümle kurulmaz**
# ─────────────────────────────────────────────────────────────────────────────


def _kup_meta(schema: dict | None, cube: str) -> dict:
    if not isinstance(schema, dict) or not cube:
        return {}
    for c in schema.get("cubes") or []:
        if isinstance(c, dict) and c.get("name") == cube:
            return c
    return {}


def _olcu_etiketi(schema: dict | None, cube: str, olcu: str) -> str:
    """`measure_synonyms_display` — yoksa **boş** (`§18.7`: ham ad basılmaz)."""
    return str((_kup_meta(schema, cube).get("measure_synonyms_display") or {}).get(olcu) or "")


def _boyut_etiketi(schema: dict | None, cube: str, boyut: str) -> str:
    """`dimension_labels` — yoksa **boş**; etiketsiz boyut cümleye girmez."""
    return str((_kup_meta(schema, cube).get("dimension_labels") or {}).get(boyut) or "")


def _kup_adi(schema: dict | None, cube: str) -> str:
    """Küpün insanca adı (`display`). Yoksa küp adının kendisi — bu bir **alan adı**
    değil bir **konu** adıdır (`satış` · `ticaret`) ve `§6/Thread 4` onu aynen kullanır."""
    return str(_kup_meta(schema, cube).get("display") or cube)


def _olcu_kodu(aday: Any) -> str:
    """`Aday.kimlik` = `cube.olcu` — sözleşmenin sahibi `app/oneri.py`, burada **okunur**."""
    kimlik, cube = str(getattr(aday, "kimlik", "")), str(getattr(aday, "cube", ""))
    if cube and kimlik.startswith(cube + "."):
        return kimlik[len(cube) + 1:]
    return kimlik.split(".", 1)[1] if "." in kimlik else kimlik


# ─────────────────────────────────────────────────────────────────────────────
# SORGU KURULUMU — yalnız `parse_cube_query` beyaz listesindeki alanlar
# ─────────────────────────────────────────────────────────────────────────────


def _zaman_filtresiz(cq: dict, schema: dict | None, cube: str) -> list[dict]:
    """Zaman ekseni filtrelerini **düşür** — dönem kaydırılırken çözülmüş tarihler kalırsa
    sorgu kendiyle çelişir. Zaman eksenlerinin listesi katalogdan okunur; tahmin edilmez."""
    zaman = set(_kup_meta(schema, cube).get("time_dimensions") or [])
    return [f for f in (cq.get("filters") or [])
            if isinstance(f, dict) and f.get("dimension") not in zaman]


def _yeni_sorgu(cube: str, olcu: str, *, boyut: str = "", donem: str = "",
                filtreler: list[dict] | None = None) -> dict:
    """Sıfırdan bir `cube_query` — **yalnız** beyaz listeden geçen alanlar."""
    cq: dict = {"cube": cube, "measures": [olcu]}
    if boyut:
        cq["dimensions"] = [boyut]
    if filtreler:
        cq["filters"] = list(filtreler)
    if donem:
        cq["period_expr"] = donem
    return cq


# ─────────────────────────────────────────────────────────────────────────────
# ÜRETEÇ
# ─────────────────────────────────────────────────────────────────────────────


def cumleler(adaylar: Sequence[Aday], *, capa: dict | None = None, niyet: Any = None,
             schema: dict | None = None, limit: int | None = None,
             soru: str = "") -> list[Oneri]:
    """Adaylardan **Türkçe cümleler** kurar. `§5.1`'in şeridi budur:

        ↳ BU RAPOR ÜZERİNDE                     (çapa varsa)
          • RAM-3'ün fire oranı — bu ay
          • fire ekle (aynı kırılım · aynı dönem)
          • fire neden bu seviyede?                    ← makro
        ↳ YENİ KONU
          • makineye göre toplam fire (kg) — bu ay

    * `adaylar` — `app/oneri.ara()` çıktısı (**sıralı**; sıra burada korunur, yeniden
      sıralanmaz — sıralamanın sahibi o modüldür).
    * `capa`    — görünen bağlam (`cube_query` ya da onu taşıyan sarmalayıcı). `None` ise
      **`BU RAPOR ÜZERİNDE` bandı boştur**; uydurma çapa yok.
    * `niyet`   — `app/niyet.Niyet` (isteğe bağlı). Yalnız `kirilimlar` okunur: kullanıcı
      bir boyutu **kendi sözcükleriyle** andıysa cümle onu taşır. Burada yeni bir
      çözümleme **yapılmaz** (`KAT-1`).
    * `schema`  — etiketlerin **tek** kaynağı. Verilmezse ölçü etiketleri yine adaylardan
      gelir, ama boyut/dönem/küp adı gerektiren cümleler **kurulmaz** (`§18.7`).
    * `limit`   — şeridin tavanı; varsayılanı `app/oneri.VARSAYILAN_LIMIT` (`FAZ 6.4`: ≤7).
      Sabit **ödünç alınır**, yeniden tanımlanmaz.
    """
    if limit is None:
        # ⚠ Tembel import: bu modül saf ve **hafif** kalsın diye (`app.oneri` gömücü
        # yolunu da yükler). Sabitin sahibi yine orası — ikinci bir tavan sayısı yok.
        from app.oneri import VARSAYILAN_LIMIT

        limit = VARSAYILAN_LIMIT
    if limit <= 0:
        return []

    c = _capa_oku(capa)
    ust = _rapor_ustunde(list(adaylar), c, niyet, schema) if c else []
    yeni = _yeni_konu(list(adaylar), c, niyet, schema, {o.metin for o in ust}, soru)

    # 🔴 **İKİ BANT DA TEMSİL EDİLİR.** `§5.1`'in şeridi iki başlık çizer; üsttekinin
    # tavanı yemesi, alttakini **görünmez** yapardı — ve `§6/Thread 3`'ün asıl kazancı
    # (*«kopuş tahmin edilmiyor, iki şerit gösteriliyor»*) tam olarak o görünürlüktür.
    ust_pay = limit if not yeni else max(1, limit - 1)
    secim = ust[:ust_pay]
    secim += yeni[: max(0, limit - len(secim))]
    return _ayirt_et(secim, schema)


def _rapor_ustunde(adaylar: list[Aday], c: _Capa, niyet: Any,
                   schema: dict | None) -> list[Oneri]:
    """`↳ BU RAPOR ÜZERİNDE` — **yalnız çapanın küpünden** (🆈 JOIN yasağı, `Thread 3`)."""
    out: list[Oneri] = []
    ayni_kup = [a for a in adaylar if str(getattr(a, "cube", "")) == c.cube]
    if not ayni_kup:
        # 🔴 `§6/Thread 3` — **KULLANICI KONUYU DEĞİŞTİRDİYSE ÜST BANT SUSAR.**
        #
        # Yazılanın çapanın küpüyle **hiçbir** kesişimi yoksa (*«ciro»* yazarken çapa
        # `fire`), açık rapor hakkında satır üretmek şeridi kullanıcının **sormadığı**
        # şeyle doldurur. Plan bu turda üst banda tek bir satır koyuyor ve o satır bir
        # JOIN gerektirdiği için zaten sunulamaz — geriye susmak kalır.
        #
        # ⚠ Çapa **düşmüyor**: kopuş tahmin edilmiyor, yalnız o turda sunacak bir şeyi
        # olmadığını beyan ediyor. *Boş bir bant, ilgisiz bir banttan dürüsttür.*
        return []
    donem = _donem_eki(c.donem)

    ekle_yazildi = False
    for a in ayni_kup:
        olcu, etiket = _olcu_kodu(a), str(getattr(a, "etiket", "")).strip()
        if not olcu or not etiket:
            continue
        # 🔴 `§42` — DEĞER ADAYI BU BANDA GİRMEZ. Ölçüldü (uçtan uca, `q=ram 3 neden`):
        # bu dal değer adayını bir **ölçü** sanıp şeride çıplak `RAM 3` yazıyordu ve
        # `measures: ["ort_oee#makine=RAM 3"]` gibi **koşamayacak** bir sorgu kuruyordu —
        # yani yalnız çirkin değil, **bozuk**. Varlığın cümlesini alt bant üretiyor
        # (`_yeni_konu`), bu bant ise *«bu raporun ölçüsünü değiştir»* bandıdır.
        # *Bir adayı yanlış bantta göstermek, onu yanlış bir şeye dönüştürür.*
        if _deger_ayikla(a, c.cube)[1]:
            continue
        if olcu not in c.olculer:
            # ① Kapsam aynı, ölçü değişiyor: *«RAM-3'ün fire oranı — bu ay»*
            govde = _kapsam(c.varlik, etiket) if c.varlik else etiket
            # 🔴 `§42` — BU BANT DA CÜMLE KURAR. Ölçüldü: çapada dönem yokken metin
            # `«fire»`ye iniyordu — yine **etiket** 🆡. ⚠ Dönem **uydurulmaz**: sorgu
            # çapanın kendi dönemini taşır (`c.cq`), o yüzden cümlede yalnız **çapanın**
            # dönemi anılır; yoksa hiç anılmaz ve cümle dönemsiz ama **doğru** kalır 🆁.
            out.append(Oneri(
                kimlik=f"{GRUP_RAPOR}:{TUR_OLCU_EKLE}:{c.cube}.{olcu}",
                metin=f"{(c.donem + ' ') if c.donem else ''}{govde} ne kadar?",
                grup=GRUP_RAPOR, tur=TUR_OLCU_EKLE, cube=c.cube,
                cube_query={**c.cq, "measures": [olcu]}))

            # ② Aynı rapora **ekleme**: *«fire ekle (aynı kırılım · aynı dönem)»*
            # ⚠ Yalnız **bir kez**: `§5.2`'nin uyarısı — tek bir `+` üç ayrı anlama gelir
            # ve bu depoyu üç kez ısırdı. Şeridi aynı fiilin tekrarıyla doldurmak, o
            # belirsizliği çoğaltmaktan başka bir şey yapmaz.
            if not ekle_yazildi and c.olculer:
                parca = [p for p, var in (("aynı kırılım", bool(c.kirilimlar)),
                                          ("aynı dönem", bool(c.donem))) if var]
                kuyruk = f" ({' · '.join(parca)})" if parca else ""
                out.append(Oneri(
                    kimlik=f"{GRUP_RAPOR}:{TUR_OLCU_EKLE}:ekle:{c.cube}.{olcu}",
                    metin=f"{etiket} ekle{kuyruk}", grup=GRUP_RAPOR, tur=TUR_OLCU_EKLE,
                    cube=c.cube,
                    cube_query={**c.cq, "measures": [*c.olculer, olcu]}))
                ekle_yazildi = True

    # ③ 🔴 MAKRO — sorgu değil, `§6/Thread 2`'nin dört adımı (tek tık).
    #
    # ⚠ Makro **açık rapora** sorulur, aday listesine değil: *«neden bu seviyede?»*
    # sorusunun öznesi ekrandaki sayıdır. Bu yüzden özne önce **çapanın ölçüsüdür**;
    # ancak onun etiketi bilinmiyorsa (şema verilmemiş) ilk adaya düşülür.
    capa_olcu = c.olculer[0] if c.olculer else ""
    ozne, ozne_kod = _olcu_etiketi(schema, c.cube, capa_olcu), capa_olcu
    if not ozne:
        # ⚠ `§42` — özne bir **ölçü** olmalı: değer adayı (`…#makine=RAM 3`) buraya
        # düşerse makro *«RAM 3 neden bu seviyede?»* diye sorar ve bir makinenin
        # *«seviyesi»* diye bir şey yoktur. Ölçüldü, uçtan uca görüldü.
        ilk = next((a for a in ayni_kup
                    if _olcu_kodu(a) and str(getattr(a, "etiket", "")).strip()
                    and not _deger_ayikla(a, c.cube)[1]), None)
        ozne = str(getattr(ilk, "etiket", "")).strip() if ilk else ""
        ozne_kod = _olcu_kodu(ilk) if ilk else ""
    if ozne and ozne_kod:
        out.append(Oneri(
            kimlik=f"{GRUP_RAPOR}:{TUR_NEDEN}:{c.cube}.{ozne_kod}",
            metin=f"{ozne} neden bu seviyede?", grup=GRUP_RAPOR, tur=TUR_NEDEN,
            cube=c.cube, cube_query=None))

    # ④ Kırılım — **kullanıcının kendi sözcüğünden** doğar, icat edilmez.
    out += _kirilim_onerisi(c, niyet, schema)
    # ⑤ Dönem kaydı — kapalı tablodan.
    out += _donem_onerisi(c, schema)
    return _tekille(out)


def _kirilim_onerisi(c: _Capa, niyet: Any, schema: dict | None) -> list[Oneri]:
    """*«vardiyaya göre OEE — bu ay»* — yalnız `Niyet` bir boyut **eşleştirdiyse**.

    🔴 Burada boyut **seçilmez**: kullanıcı bir kırılım andıysa `app/niyet.py` onu zaten
    eşleştirmiştir. İkinci bir eşleştirici yazmak, `KÖK-1`'in beş kez ölçülmüş kusurunu
    (aynı sorunun beş sahibi) altıncı kez üretmek olurdu.
    """
    boyutlar = [str(d) for d in (getattr(niyet, "kirilimlar", None) or [])]
    meta_boyutlar = set(_kup_meta(schema, c.cube).get("dimensions") or [])
    olcu = c.olculer[0] if c.olculer else ""
    olcu_et = _olcu_etiketi(schema, c.cube, olcu)
    if not olcu_et:
        return []                       # ham ölçü adı basmaktansa satır **hiç** olmasın
    for b in boyutlar:
        # ⚠ Süzülmüş boyutta kırılım **tek satır** döndürür (*«RAM-3'ü makineye böl»*):
        # bir öneri değil, bir tekrar. Zaten kırılımda olan boyut da eklenmez.
        if b in c.kirilimlar or b == c.varlik_boyut:
            continue
        if meta_boyutlar and b not in meta_boyutlar:
            continue
        b_et = _boyut_etiketi(schema, c.cube, b)
        if not b_et:
            continue
        return [Oneri(
            kimlik=f"{GRUP_RAPOR}:{TUR_KIRILIM}:{c.cube}.{b}",
            metin=f"{kirilim_ifadesi(b_et)} {olcu_et}{_donem_eki(c.donem)}",
            grup=GRUP_RAPOR, tur=TUR_KIRILIM, cube=c.cube,
            cube_query={**c.cq, "dimensions": [*c.kirilimlar, b]})]
    return []


def _donem_onerisi(c: _Capa, schema: dict | None) -> list[Oneri]:
    """*«RAM-3'ün fire oranı — geçen ay»* — aynı rapor, **kaydırılmış** dönem.

    ⚠ Şart üç katlı: çapa bir dönem **ifadesi** taşımalı, ifade kapalı tabloda olmalı ve
    ölçünün **etiketi** bilinmeli. Üçü de sağlanmıyorsa satır yazılmaz — bir dönem
    önerisini tahminle kurmak, `date_filters`'ın çözemeyeceği bir cümle üretme riskidir.
    """
    onceki = _ONCEKI_DONEM.get(c.donem.strip().lower())
    olcu = c.olculer[0] if c.olculer else ""
    olcu_et = _olcu_etiketi(schema, c.cube, olcu)
    if not onceki or not olcu_et or not schema:
        return []
    govde = _kapsam(c.varlik, olcu_et) if c.varlik else olcu_et
    yeni_cq = {**c.cq, "period_expr": onceki}
    filtreler = _zaman_filtresiz(c.cq, schema, c.cube)
    if filtreler:
        yeni_cq["filters"] = filtreler
    else:
        yeni_cq.pop("filters", None)
    return [Oneri(kimlik=f"{GRUP_RAPOR}:{TUR_DONEM}:{c.cube}.{olcu}#{onceki}",
                  metin=govde + _donem_eki(onceki), grup=GRUP_RAPOR, tur=TUR_DONEM,
                  cube=c.cube, cube_query=yeni_cq)]


def _yazilan_donem(soru: str) -> str:
    """Kullanıcının **kendi yazdığı** dönem — ve yalnız **kapalı listeden**.

    🔴 Bu fonksiyonun yapmadığı iki şey, yaptığı şeyden önemli:

    **① Süzgeçten geri çözmez.** `Niyet.donemler` bir **filtre**dir
    (`{'dimension':'tarih','operator':'gte','value':'2026-08-01'}`) ve bu modülün kendi
    kuralı onu yasaklar: *«`2026-08-01 ≤ tarih ≤ 2026-08-31` ifadesinden «bu ay»'a dönmek
    bir **tahmindir**»* (`_capa_oku`). Bir tahmini kullanıcıya **kendi cümlesi** diye
    göstermek, `§5.1`'in *«bağlam görünür olsun»* vaadinin tersidir.

    **② Yeni bir dil kuralı EKLEMEZ.** Metinden dönem çıkarmak route'a Türkçe öğretmek
    olurdu (en üst kural: *«route'a dil kuralı EKLEME»*). Bunun yerine **bu modülün
    zaten sahip olduğu** kapalı tablo okunuyor: `_ONCEKI_DONEM`'in anahtarları.

    ⊙ **Ve bu kaynak seçimi ölçümle düzeldi ③.** İlk yazımım `donem_capasi.
    DONEM_SECENEKLERI`'ni import etti; **saflık kapısı** onu reddetti ve **haklıydı**:
    `donem_capasi` yaprak bir modül değil — `cube_router` ve `veri_araligi` çekiyor, yani
    bu modülün *«LLM yok, sorgu yok, IO yok»* ilanını kırardı. `_ONCEKI_DONEM` ise
    **burada** yaşıyor ve üstelik daha güçlü bir güvenceyle: bir kapı her değerinin
    `route()` tarafından **çözülebildiğini** ölçüyor. *Aynı sözcük listesinin iki
    kaynağından, kapıya bağlı olanı seçilir.*

    ⚠ **En uzun eşleşme kazanır**: bugün *«bu ay»* ile *«bu yıl»* çakışmıyor ama tablo
    büyüyebilir; kısa olanı önce eşleştirmek, uzun olanı **sessizce** yutardı.
    ⚠ Eşleşme yoksa **boş** döner — uydurma dönem yazılmaz. Dönemsiz bir öneri hâlâ
    doğrudur; yanlış dönemli bir öneri **değildir** 🅫.
    """
    metin = (soru or "").lower()
    if not metin:
        return ""
    return next((d for d in sorted(_ONCEKI_DONEM, key=len, reverse=True)
                 if d in metin), "")


#: 🔴 `§40` — ÖNGÖRÜ **TAM CÜMLEDİR**, etiket değil.
#:
#: Kullanıcı ölçümü (2026-08-13, ekran görüntüsü): boş sayfada yazarken gelenler
#: `fire (parti)` · `fire (OEE)` · `fire oranı` idi — *«cümle bile değil»*. Modülün kendi
#: notu bunu zaten itiraf ediyordu: *«çapasız her öneri dönemsiz kalıyordu — yani cümle
#: değil etiket»* 🆡; çare **yarım** uygulanmıştı: dönem yalnız kullanıcı **yazdıysa**
#: ekleniyordu, yazmadıysa geriye çıplak etiket kalıyordu.
#:
#: ⚠ Bu ifade bir **sistem varsayımı değildir**: öneri, kullanıcının **yazacağı cümledir**.
#: Kullanıcı onu seçerse dönemi **kendisi söylemiş** olur — ve `cube_query` da **aynı**
#: dönemi taşır (`donem_c`), yoksa cümle sorgudan başka bir şey söylerdi 🆁.
_VARSAYILAN_DONEM = "bu ay"


def _deger_ayikla(aday: Any, cube: str) -> tuple[str, str, str]:
    """`oee.ort_oee#makine=RAM-3` → `("makine", "RAM-3", "ort_oee")`; değilse üç boş dize.

    Sözleşmenin **sahibi** `app/oneri.py::_deger_adaylari`; burada yalnız **okunur**
    (`_olcu_kodu`'nun kardeşi, `KAT-1`).
    """
    kod = _olcu_kodu(aday)
    if "#" not in kod:
        return "", "", ""
    olcu, kalan = kod.split("#", 1)
    if "=" not in kalan:
        return "", "", ""
    boyut, deger = kalan.split("=", 1)
    return (boyut.strip(), deger.strip(), olcu.strip()) if deger.strip() else ("", "", "")


def _olcu_etiketi(schema: dict | None, cube: str, olcu: str) -> str:
    """Ölçünün insan-okur adı — katalogdan, **ikinci bir sözlük açmadan** (`KAT-1`)."""
    meta = _kup_meta(schema, cube)
    gorenen = meta.get("measure_synonyms_display") or {}
    return str(gorenen.get(olcu) or olcu)


def _yeni_konu(adaylar: list[Aday], c: _Capa | None, niyet: Any, schema: dict | None,
               ust_metinler: set[str], soru: str = "") -> list[Oneri]:
    """`↳ YENİ KONU` — çapa **düşer**; dönem kalır (`§6/Thread 3`: kopuş bir yeni rapordur,
    yeni bir takvim değil).

    Kırılım iki **gerçek** kaynaktan gelebilir, ikisi de icat değil:
      · çapanın **süzdüğü** boyut → *«RAM-3»*'ten *«makineye göre»*'ye açılım (`§5.1`),
      · `Niyet`in eşleştirdiği boyut → kullanıcının kendi sözcüğü.
    """
    # 🔴 **ÖLÇÜLMÜŞ KUSUR (insan testi, 2026-08-13).** Burası `c` yoksa `""` diyordu ve
    # çapasız her öneri **dönemsiz** kalıyordu — yani cümle değil **etiket**: `fire (parti)`.
    # Üstelik kullanıcı *«bu ay fire»* **yazdığında bile**, çünkü yazdığı dönem hiç
    # okunmuyordu. *Yarım bir cümle bir etikettir* 🆡.
    donem = c.donem if c else _yazilan_donem(soru)
    niyet_boyutlari = [str(d) for d in (getattr(niyet, "kirilimlar", None) or [])]
    out: list[Oneri] = []
    for a in adaylar:
        cube, olcu = str(getattr(a, "cube", "")), _olcu_kodu(a)
        etiket = str(getattr(a, "etiket", "")).strip()
        if not cube or not olcu or not etiket:
            continue
        boyut = ""
        if c and cube == c.cube and c.varlik_boyut:
            boyut = c.varlik_boyut
        else:
            meta_boyutlar = set(_kup_meta(schema, cube).get("dimensions") or [])
            boyut = next((b for b in niyet_boyutlari if b in meta_boyutlar), "")
        donem_c = donem or _VARSAYILAN_DONEM
        # 🔴 `§40` — DEĞER ADAYI: `oee.ort_oee#makine=RAM-3`. Yazılan varlık cümlenin
        # **öznesi** olur; `_kapsam` Türkçe tamlamayı zaten kuruyor ㊲.
        v_boyut, v_deger, v_olcu = _deger_ayikla(a, cube)
        if v_deger:
            v_etiket = _olcu_etiketi(schema, cube, v_olcu)
            metin = f"{donem_c} {_kapsam(v_deger, v_etiket)} ne kadar?"
            if metin in ust_metinler:
                continue
            out.append(Oneri(
                kimlik=f"{GRUP_YENI}:{TUR_YENI}:{cube}.{v_olcu}#{v_boyut}={v_deger}",
                metin=metin, grup=GRUP_YENI, tur=TUR_YENI, cube=cube,
                cube_query=_yeni_sorgu(
                    cube, v_olcu, donem=donem_c,
                    filtreler=[{"dimension": v_boyut, "operator": "eq",
                                "value": v_deger}])))
            # 🔴 `§42` — VARLIĞIN **NEDEN**'İ: kullanıcı `ram 3 neden` yazmıştı; sistem
            # ona *«ne kadar»* öneriyordu. Makro (`TUR_NEDEN`) `rapor_ustunde` dalında
            # zaten vardı ㊷ — yeni konuda **yoktu**. Aynı değişmez korunur: makro
            # cümlesi `cube_query` taşımaz, `Oneri.gecerli` onu tür üzerinden kabul eder.
            out.append(Oneri(
                kimlik=f"{GRUP_YENI}:{TUR_NEDEN}:{cube}.{v_olcu}#{v_boyut}={v_deger}",
                metin=f"{_kapsam(v_deger, v_etiket)} neden bu seviyede?",
                grup=GRUP_YENI, tur=TUR_NEDEN, cube=cube, cube_query=None))
            continue
        b_et = _boyut_etiketi(schema, cube, boyut) if boyut else ""
        onek = f"{kirilim_ifadesi(b_et)} " if b_et else ""
        metin = f"{donem_c} {onek}{etiket} ne kadar?"
        if metin in ust_metinler:
            # Üst bantta **birebir aynı** cümle zaten var: aynı satırı iki başlık altında
            # göstermek, iki seçenek varmış gibi görünen tek bir seçenektir.
            continue
        out.append(Oneri(
            kimlik=f"{GRUP_YENI}:{TUR_YENI}:{cube}.{olcu}" + (f"#{boyut}" if b_et else ""),
            metin=metin, grup=GRUP_YENI, tur=TUR_YENI, cube=cube,
            cube_query=_yeni_sorgu(cube, olcu, boyut=boyut if b_et else "",
                                   donem=donem_c)))
    return _tekille(out)


def _tekille(oneriler: list[Oneri]) -> list[Oneri]:
    """Aynı kimlik iki kez yazılmaz — sıra **korunarak**."""
    gorulen: set[str] = set()
    out: list[Oneri] = []
    for o in oneriler:
        if o.kimlik in gorulen:
            continue
        gorulen.add(o.kimlik)
        out.append(o)
    return out


def _ayiricili(metin: str, kup: str) -> str:
    """Küp ayırıcısını **cümlenin içine** koyar — sonuna değil.

    🔴 `§40` — öngörü **tam cümle** olunca ayırıcının yeri de değişti: eskiden metin bir
    öbekti (`fire oranı`) ve sona eklemek doğaldı (`fire oranı (parti)`); şimdi cümle
    soru işaretiyle bitiyor ve aynı ekleme *«bu ay fire ne kadar? (OEE)»* gibi **cümleyi
    kesip arkasına etiket yapıştırıyordu**.

    ⚠ Ayırıcının **işi değişmedi** (aynı metinli iki öneriyi ayırmak) — yalnız **yeri**
    düzeldi. Kapı `test_AYNI_ETIKETLI_IKI_ONERI_kup_adiyla_AYRILIR` aynen geçerli.
    """
    ek = f" ({kup})"
    return f"{metin[:-1]}{ek}?" if metin.endswith("?") else f"{metin}{ek}"


def _ayirt_et(oneriler: list[Oneri], schema: dict | None) -> list[Oneri]:
    """🔴 `§6/Thread 4` — **AYNI ETİKETLİ İKİ ÖNERİ**: kullanıcı ayırt edemez.

    Planın ölçtüğü kırılma: *«müşteriye göre toplam ciro (satış)»* ile *«… (ticaret)»* aynı
    cümleyi kuruyor ve tıklama bir **kumar** oluyor. Çözüm etiketi değiştirmek değil —
    çakışan cümlelere **küpün adını** eklemek. Çakışma yoksa hiçbir cümle dokunulmaz
    (`KURAL B`: bugünkü metin bayt bayt aynı).

    ⚠ Ayırıcı kullanıcıya bir şey söylemiyorsa faydasızdır (planın kendi uyarısı); bu
    yüzden `display` kullanılır (*«satış»*), küpün iç adı değil.
    """
    sayim: dict[str, int] = {}
    for o in oneriler:
        sayim[o.metin] = sayim.get(o.metin, 0) + 1
    if all(n == 1 for n in sayim.values()):
        return oneriler
    return [o if sayim[o.metin] == 1
            else Oneri(kimlik=o.kimlik, metin=_ayiricili(o.metin, _kup_adi(schema, o.cube)),
                       grup=o.grup, tur=o.tur, cube_query=o.cube_query, cube=o.cube)
            for o in oneriler]
