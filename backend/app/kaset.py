"""🔴🔴 `A1` — **KASET**: sağlayıcı yanıtlarını kaydet, sonra **diskten** oynat.

## Neden var — ve neden bugünkü "kaset" bir DEKORDU

Raporun `§4i` kararı: kapının yeni merkezi **kasetli garson korpusu** olmalı, çünkü

> *"`/ask` yolunda `route()` her zaman denenir — dolayısıyla tam `/ask` yolundan koşan
> bir garson korpusu, route'u da koşturur ve bugünkü LLM'siz korpusun ölçtüğü her şeyi
> **artı devri** ölçer."*

Ve kullanıcının sert kısıtı (`§4g`): *"binlerce canlı test API'yi tıkar."* Kaset bu iki
şartı birden karşılar — **bir kez** canlı kaydedilir, sonraki her koşum **sıfır API**.

⊙ Ama depoda bulduğum "kaset" bunu yapmıyordu:

| iddia | gerçek |
|---|---|
| `lab/garson.py:472` docstring: *"Sağlayıcı yanıtlarını kaydet"* | **son `/ask` yanıtını** yazıyor, sağlayıcıyı değil |
| `--kaset` bayrağı var | yazılan dosya **hiçbir yerde okunmuyor** — oynatma **YOK** |

Yani `--kaset` bir artefakt üretiyor ve o artefakt hiçbir kapıyı beslemiyordu.
Bu, deponun kendi adını koyduğu tuzağın birebir aynısı: *kırmızı veremeyen bir kapı,
bir dekordur* — burada **hiç koşmayan** bir kayıt.

## Nasıl çalışır — ve ilk tasarımım neden YANLIŞTI

Kaset, sağlayıcının **taşıma** metodunu (`_chat` · `_ask`) yakalar; anahtar `(system,
user, model)` üçlüsünden üretilir.

⊙ İlk yazımda **anlam** yüzeylerini sarmıştım (`select_cube`, `generate_sql`) ve canlı
bir koşum **0 kayıtla** çıktı — LLM defalarca çağrıldığı hâlde. Loglar sebebi söyledi:
`plan_kur` diye **üçüncü** bir yüzey vardı. Sayınca `llm.py`'de **11'den fazla** anlam
yüzeyi olduğunu gördüm.

🔴 Onları tek tek saymak, *«tek tek sinonim yazmak aptallık»* kuralının başka kılığıdır:
liste bugün tamamlansa bile **yarın eklenen yüzey sessizce kaset dışında kalır**. Ağa
çıkan yer ise **iki** tanedir ve hepsi oradan geçer.

*Bir kaset, anlamı değil **teli** dinlemelidir: anlamlar çoğalır, tel çoğalmaz.*

    kayıt:  DIMA_KASET=kayit  DIMA_KASET_YOLU=lab/kasetler/x.json
    oynat:  DIMA_KASET=oynat  DIMA_KASET_YOLU=lab/kasetler/x.json

🔴 **OYNATMADA EKSİK ANAHTAR SESSİZCE GEÇEMEZ.** Kaydedilmemiş bir soru gelirse
`KasetEksik` fırlatılır. Sessiz bir yedek (canlıya düşmek ya da boş dönmek), kapının
**kaydedilmemiş** sorularda yeşil vermesi demek olurdu — ve o, ölçtüğünü sanan bir
ölçüm aracıdır. *Bir kasetin sınırı, kasetin kendisi kadar önemlidir.*

## İki sert sınır — raporun kendi yazdığı, burada kod olarak duruyor

| sınır | sonucu |
|---|---|
| Kaset yalnız **kaydedilmiş** soruları taşır | Payda **kayıt kümesidir**; *«korpus %»* demek onun hakkı değildir |
| Kaset **istem sürümüne** bağlıdır | İstem değişince kaset **BAYAT**; yeniden kaydedilmeli |

İkincisi bir yorum değil, `muhur()` ile **ölçülür**: kayıt anındaki istem parmak izi
dosyaya yazılır ve oynatmada karşılaştırılır. Uyuşmazsa uyarı basılır — çünkü
*bir kaset, kaydedildiği günün modelini ölçer; bugünün modelini değil.*
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from app.logging_setup import get_logger

_log = get_logger(__name__)

#: Kaset dosyasının şema sürümü. Biçim değişirse eski kasetler **bayat** sayılır.
SURUM = 1


class KasetEksik(RuntimeError):
    """🔴 Oynatmada kaydı olmayan bir çağrı geldi.

    Sessizce geçmek yerine **patlar**: kaydedilmemiş bir soru üzerinde yeşil veren bir
    kapı, ölçmediğini ölçtüğünü sanır.
    """


def _anahtar(yuzey: str, *parcalar: Any) -> str:
    """Çağrı girdisinden **kararlı** bir anahtar.

    ⚠ `json.dumps(..., sort_keys=True)`: sözlük sırası Python sürümleri arasında
    değişebilir ve anahtar kaymış olurdu — kaset o gün sessizce **tamamen** ıskalardı.
    """
    ham = yuzey + "␟" + "␟".join(
        p if isinstance(p, str) else json.dumps(p, sort_keys=True, ensure_ascii=False)
        for p in parcalar)
    return hashlib.sha256(ham.encode("utf-8")).hexdigest()[:32]


def _sema_izi(sema: dict | None) -> str:
    """Şemanın **kimliği** — tamamı değil.

    Tam şemayı anahtara koymak, tek bir ölçü eklendiğinde **bütün kaseti** bayatlatırdı.
    Kimlik olarak küp+ölçü adları yeter: cevabı belirleyen şey odur.
    """
    if not isinstance(sema, dict):
        return ""
    return json.dumps(
        sorted((str(c.get("name")), tuple(sorted(map(str, c.get("measures") or []))))
               for c in (sema.get("cubes") or [])),
        ensure_ascii=False)


class Kaset:
    """Kayıt/oynatma deposu. Tek dosya, tek sorumluluk."""

    def __init__(self, yol: str | Path, mod: str) -> None:
        self.yol = Path(yol)
        self.mod = mod
        self.kayitlar: dict[str, str] = {}
        self.muhur: str = ""
        #: Oynatmada **istatistik**: kaç isabet, kaç ıska. Kapı bunu basar.
        self.isabet = 0
        self.iska = 0
        #: 🔴🔴 **AYNI İSTEM KAÇINCI KEZ SORULUYOR** — kasetin en ince yeri.
        #:
        #: Sistem `consistency_k=3` ile **aynı istemi üç kez** sorar ve üç cevabı
        #: oylar. İçerikle anahtarlayınca üçü **tek kayda çöküyordu**; oynatmada üçü de
        #: aynı cevabı alıyor, oy birliği zorla **%100** oluyor, sistem farklı karar
        #: veriyor ve sonraki istemler artık kasette bulunmuyordu. Ölçüldü: **10 ıska**.
        #:
        #: ⊙ Yani kaset, ölçtüğü davranışı **değiştiriyordu** — bir ölçüm aracının
        #: yapabileceği en sinsi şey. Onarım: anahtar `(istem, kaçıncı kez)` olur;
        #: üç örnek üç ayrı kayıttır ve oynatmada **aynı sırayla** geri verilir.
        #:
        #: *Bir kayıt, söylenenleri değil **söyleniş sırasını** da tutmalıdır; yoksa
        #: tekrarı bir koro değil tek bir ses olarak çalar.*
        self.sayac: dict[str, int] = {}
        #: 🔴 Kayıt modu **BİRİKTİRİR**, sıfırlamaz.
        #:
        #: İlk yazımda her `--kaydet` dosyayı sıfırdan yazıyordu. Sonucu ölçüldü:
        #: oynatmada **1 ıska** kaldı (zincirin ilerisindeki bir istem, kayıt turunda
        #: hiç oluşmamıştı — çünkü o turda LLM farklı karar vermişti) ve o tek boşluğu
        #: kapatmak **bütün korpusu yeniden ödemek** demekti (~5 dk canlı API).
        #:
        #: ⊙ Biriktirici kayıtta yalnız **eksik anahtar** API'ye gider; var olanlar
        #: diskten gelir. Yani kaset, ardışık koşumlarla **kendi boşluklarını kapatır**.
        #: *Bir kaydı tamamlamanın yolu, onu her seferinde baştan almak değildir.*
        if self.yol.exists():
            ham = json.loads(self.yol.read_text(encoding="utf-8"))
            if int(ham.get("surum") or 0) != SURUM:
                raise KasetEksik(
                    f"kaset sürümü {ham.get('surum')} ≠ {SURUM} — BAYAT, yeniden kaydet")
            self.kayitlar = dict(ham.get("kayitlar") or {})
            self.muhur = str(ham.get("muhur") or "")
        elif mod == "oynat":
            raise KasetEksik(f"kaset dosyası yok: {self.yol}")

    # ── kayıt ──────────────────────────────────────────────────────────────────
    def yaz(self, muhur: str = "") -> Path:
        self.yol.parent.mkdir(parents=True, exist_ok=True)
        self.yol.write_text(json.dumps(
            {"surum": SURUM, "muhur": muhur or self.muhur,
             "kayitlar": self.kayitlar}, ensure_ascii=False, indent=1), encoding="utf-8")
        return self.yol

    # ── ortak yüzey ────────────────────────────────────────────────────────────
    def coz(self, anahtar: str, uret) -> str:
        """Kayıttan oku, yoksa **moda göre** ya üret-ve-kaydet ya da patla.

        ⚠ Anahtar burada **tekrar sırasıyla** genişletilir (`…#0`, `…#1`, `…#2`):
        `consistency_k` örneklemesi ancak böyle birebir tekrar oynatılabilir.
        """
        n = self.sayac.get(anahtar, 0)
        self.sayac[anahtar] = n + 1
        anahtar = f"{anahtar}#{n}"
        if self.mod == "oynat":
            if anahtar not in self.kayitlar:
                self.iska += 1
                raise KasetEksik(
                    f"kasette kayıt yok (anahtar={anahtar[:12]}…). Bu soru "
                    "kaydedilmemiş — kaseti yeniden kaydet ya da soruyu korpustan çıkar. "
                    "⚠ Sessizce geçmek, ölçülmemiş bir soruda YEŞİL vermek olurdu.")
            self.isabet += 1
            return self.kayitlar[anahtar]
        if anahtar in self.kayitlar:
            self.isabet += 1                    # biriktirici kayıt: API'ye GİTME
            return self.kayitlar[anahtar]
        self.iska += 1
        cevap = uret()
        self.kayitlar[anahtar] = cevap
        return cevap


#: 🔴🔴 **KASET, AĞIN OLDUĞU YERE KURULUR — ANLAMIN OLDUĞU YERE DEĞİL.**
#:
#: İlk yazımda iki **anlam** yüzeyini sarmıştım (`select_cube`, `generate_sql`) ve kaset
#: canlı bir koşumda **0 kayıtla** çıktı — LLM defalarca çağrıldığı hâlde. Loglar sebebi
#: söyledi: `plan_kur` diye **üçüncü** bir yüzey vardı ve sarmalayıcının `__getattr__`'ı
#: onu sessizce alta geçiriyordu.
#:
#: ⊙ Sayınca gördüm: `llm.py`'de **11'den fazla** anlam yüzeyi var — `select_cube` ·
#: `plan_kur` · `plan_sec` · `refine_cube` · `prompt_enhance` · `anlat` ·
#: `generate_followup_sql` · `generate_sql` · … Bunları tek tek saymak, kullanıcının
#: *«tek tek sinonim yazmak aptallık»* dediği hatanın başka kılığıdır: liste bugün
#: tamamlansa bile **yarın eklenen yüzey sessizce kaset dışında kalır**.
#:
#: Ağa çıkan yer ise **iki** tanedir ve hepsi oradan geçer:
#:   `OpenAICompatibleSqlGenerator._chat`  ·  `AnthropicSqlGenerator._ask`
#:
#: *Bir kaset, anlamı değil **teli** dinlemelidir: anlamlar çoğalır, tel çoğalmaz.*
TASIMA_YUZEYLERI = ("_chat", "_ask")


def _sar_tasima(uretec: Any, kaset: Kaset) -> bool:
    """Bir sağlayıcı örneğinin taşıma metodunu kasete bağlar. Döner: sarıldı mı."""
    sarildi = False
    for ad in TASIMA_YUZEYLERI:
        ozgun = getattr(uretec, ad, None)
        if not callable(ozgun) or getattr(ozgun, "_kasetli", False):
            continue

        def yeni(system: str, user: str, model: str | None = None,
                 _ozgun=ozgun, _ad=ad) -> str:
            return kaset.coz(_anahtar(_ad, system, user, model or ""),
                             lambda: _ozgun(system, user, model))

        yeni._kasetli = True                                   # type: ignore[attr-defined]
        setattr(uretec, ad, yeni)
        sarildi = True
    return sarildi


def belki_sar(llm: Any) -> Any:
    """Ortam kasetli mi? Öyleyse sar, değilse **dokunma**.

    🔴 `KURAL B`'nin gereği: değişken yokken davranış **birebir** bugünkü. Kaset bir
    ölçüm aletidir ve bir ölçüm aleti, ölçtüğü sistemin varsayılan yolunu değiştiremez.
    """
    mod = (os.environ.get("DIMA_KASET") or "").strip().lower()
    if mod not in ("kayit", "oynat"):
        return llm
    yol = os.environ.get("DIMA_KASET_YOLU") or ""
    if not yol:
        _log.warning("DIMA_KASET=%s ama DIMA_KASET_YOLU boş — kaset KURULMADI", mod)
        return llm
    kaset = Kaset(yol, mod)
    # `FailoverSqlGenerator` bir **liste** taşır (`_gens`); her sağlayıcının kendi
    # taşıma metodu vardır ve failover sırasında herhangi biri konuşabilir.
    hedefler = list(getattr(llm, "_gens", None) or [llm])
    n = sum(1 for g in hedefler if _sar_tasima(g, kaset))
    if not n:
        # 🔴 Sessizce geçmek, kasetin **hiç kurulmadığını** gizlerdi — ve oynatma
        # modunda bu, *"her şey kayıttan geldi"* sanılan bir canlı koşum demektir.
        _log.warning("🔴 KASET KURULAMADI — %d sağlayıcının hiçbirinde %s yok. "
                     "Ölçüm CANLI koşuyor olabilir.", len(hedefler), TASIMA_YUZEYLERI)
    else:
        _log.info("kaset %s: %s (%d kayıt · %d/%d sağlayıcı sarıldı)",
                  mod, yol, len(kaset.kayitlar), n, len(hedefler))
    llm.kaset = kaset                                          # koşucu buradan okur
    return llm
