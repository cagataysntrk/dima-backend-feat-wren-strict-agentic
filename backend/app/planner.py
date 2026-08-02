"""PLANLAYICI ÇEKİRDEĞİ — bütçeli, denetlenen, makbuzlu adım yürütücü (Faz F2).

## Ne yapar, ne YAPMAZ

Bu modül **bir LLM döngüsü değildir.** Bir ReAct planlayıcısının *"hangi adımı seçeyim"*
kısmı henüz yok ve bilinçli olarak yok: o karar telemetriyle kalibre edilmeli (Faz E-1) ve
bugün telemetri **boş**. Ölçülmemiş bir kararı LLM'e devretmek, bu turda altı kez ölçülen
*"beyan var, kanıt yok"* sınıfının en pahalı örneği olurdu.

Burada olan şey **yürütmenin YÖNETİŞİMİDİR**: bir plan hangi araçları çağırırsa çağırsın,
her adım bütçeye, yetkiye ve deterministik-önce kuralına **tabidir** ve **makbuz üretir**.

> Planlayıcı zekâsı olmadan yönetişim işe yarar (bugünkü sabit kompozisyonlar da ondan
> geçebilir). Yönetişim olmadan planlayıcı zekâsı **tehlikelidir** — sınırsız bir döngü,
> denetlenmeyen bir yetki ve izlenmeyen bir maliyet demektir. Sıra bu yüzden böyle.

## Dört kapı

| Kapı | Ne yapar | Neden |
|---|---|---|
| **Kayıt** | Araç `app/tools.py`'de yoksa **red** | Planlayıcı araç UYDURAMAZ |
| **Yetki** | `izinli_araclar(principal)` dışındaysa **red** | Ajan kullanıcının yetkisini aşamaz |
| **Deterministik-önce** | Deterministik kardeşi DENENMEDEN LLM aracı **seçilemez** | Merdivenin felsefesi (MIMARI §2) plan seviyesinde |
| **Bütçe** | Adım/süre/sorgu tavanı aşılırsa **dur** | Şartname 4.16 — bugüne kadar SIFIR tavan vardı |

## Bütçe aşımı = DÜRÜST KISMİ CEVAP

Tavan aşıldığında koşum **sessizce kesilmez**: o ana kadar toplanan adımlar geçerlidir ve
`Kosum.kisildi` + `kisilma_nedeni` ile birlikte döner. Çağıran bunu kullanıcıya
söylemekle yükümlüdür — `contribution`'ın `kirpilan_segment`'i ve `taranmayan_boyut`'u ile
**aynı desen**: kapsamı daraltan her sınır görünür olur.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from app import tools
from app.logging_setup import get_logger

_log = get_logger("planner")


class ButceAsimi(RuntimeError):
    """Tavan aşıldı — koşum durur ama o ana kadarki adımlar GEÇERLİDİR."""


class AracReddi(RuntimeError):
    """Araç kaydı / yetki / deterministik-önce kapısı reddetti."""


@dataclass(frozen=True)
class Butce:
    """Bir ajan koşusunun tavanları. `0`/`None` = o eksende sınırsız.

    Varsayılanlar **muhafazakârdır**: bir kullanıcı sorusunun cevabı 8 adımı geçiyorsa
    büyük olasılıkla plan yanlıştır ve daha fazla adım daha iyi bir cevap değil, daha
    pahalı bir başarısızlık üretir.

    `token` bugün **ölçülemiyor** (telemetri boş — Faz E-1) ve bu yüzden varsayılanı
    sınırsızdır. Ölçülmemiş bir eşik koymak, kapsamı gerekçesiz daraltmak olurdu; alan
    şimdiden var ki telemetri gelince **kod değil yalnız değer** değişsin.
    """

    adim: int = 8
    saniye: float = 30.0
    sorgu: int = 12
    token: int = 0


@dataclass
class Adim:
    """Tek bir araç çağrısının kaydı — makbuz ağacının yaprağı."""

    arac: str
    determinizm: str
    sure_ms: int
    makbuz: str | None = None
    hata: str | None = None

    def ozet(self) -> dict[str, Any]:
        return {"tool": self.arac, "determinism": self.determinizm,
                "ms": self.sure_ms, "receipt": self.makbuz,
                **({"error": self.hata} if self.hata else {})}


@dataclass
class Kosum:
    """Bir ajan koşusunun tamamı: adımlar + bütçe durumu + kısılma gerekçesi."""

    adimlar: list[Adim] = field(default_factory=list)
    kisildi: bool = False
    kisilma_nedeni: str = ""
    kok_makbuz: str | None = None

    @property
    def sorgu_sayisi(self) -> int:
        """Veriye dokunan adımlar (maliyet sınıfı `sifir` olmayanlar)."""
        return sum(1 for a in self.adimlar
                   if tools.get(a.arac).maliyet != "sifir")

    def makbuza(self) -> dict[str, Any]:
        """Kök makbuza yazılacak biçim — adım ağacı + kısılma kaydı.

        `truncated` alanı **her zaman** yazılır (False olsa bile): *"kısılmadı"* ile
        *"kısılma sorulmadı"* farklı şeylerdir ve bu ayrım denetçinin işine yarar.
        """
        return {
            "agent_run": {
                "steps": [a.ozet() for a in self.adimlar],
                "step_count": len(self.adimlar),
                "query_count": self.sorgu_sayisi,
                "truncated": self.kisildi,
                "truncation_reason": self.kisilma_nedeni or None,
            }
        }


class Planlayici:
    """Araç çağrılarını yöneten yürütücü. **Plan seçmez, planı UYGULAR.**

    Kullanım:

        p = Planlayici(principal=principal, butce=Butce(adim=5))
        try:
            cq = p.calistir("route", soru, schema)
            rapor = p.calistir("contribution.decompose", ...)
        except ButceAsimi:
            pass          # o ana kadarki adımlar GEÇERLİ — kısmi cevap ver
        makbuz = p.kosum.makbuza()
    """

    def __init__(self, *, principal: Any = None, butce: Butce | None = None,
                 kaynaklar: dict[str, Any] | None = None) -> None:
        self.principal = principal
        self.butce = butce or Butce()
        # Servise bağlı araçlar için istek-kapsamlı nesneler: {"servis:wren": svc, …}
        self.kaynaklar = kaynaklar or {}
        self.kosum = Kosum()
        self._baslangic = time.monotonic()
        # Bu koşumda DENENMİŞ deterministik ARAÇ ADLARI — deterministik-önce kapısının belleği.
        # DİKKAT: ad tutulur, etiket değil. İlk sürüm etiket tutuyor ve araç ADLARINI o
        # kümeye karşı sınıyordu — kapı `route` çalıştıktan sonra bile reddediyordu
        # (kendi testim yakaladı). Kapının yanlış-pozitifi, kapının olmamasından kötüdür:
        # meşru bir merdiven basamağını kapatır ve kural "işe yaramıyor" diye sökülür.
        self._denenen_araclar: set[str] = set()

    # --- kapılar -----------------------------------------------------------------

    def _yetki_kapisi(self, arac: tools.Arac) -> None:
        if self.principal is None:
            return          # kimliksiz çağrı (test/dahili) — yetki kapısı uygulanmaz
        if arac not in tools.izinli_araclar(self.principal):
            raise AracReddi(
                f"{arac.ad}: bu kullanıcının yetkisi yok ({arac.izin}). Ajan, kullanıcının "
                "kendi eliyle yapamayacağı bir işi onun adına YAPAMAZ.")

    def _deterministik_once_kapisi(self, arac: tools.Arac) -> None:
        """LLM aracı, aynı etiketteki deterministik kardeşi DENENMEDEN seçilemez.

        Bu, MIMARI §2'nin merdiven felsefesinin plan seviyesindeki karşılığıdır ve bir
        **kural değil bir KAPIDIR**: kural denetlenemezse kural değildir (bu turda
        `consistency_k`, `expose:` üreteci, fan-out ölçümü ve `_select_consistent`
        aynı sınıfta ölçüldü — hepsi beyan edilmiş, hiçbiri uygulanmamıştı).
        """
        if arac.determinizm != "llm":
            return
        kardesler = [
            d for d in tools.deterministik_olanlar()
            if set(d.etiketler) & (set(arac.etiketler) - {"llm"})
        ]
        denenmemis = [d.ad for d in kardesler if d.ad not in self._denenen_araclar]
        if kardesler and denenmemis:
            raise AracReddi(
                f"{arac.ad}: DETERMİNİSTİK-ÖNCE ihlali — önce {denenmemis} denenmeli. "
                "Bir işi deterministik bir araç yapabiliyorsa LLM aracı seçilemez.")

    def _butce_kapisi(self, arac: tools.Arac) -> None:
        b = self.butce
        if b.adim and len(self.kosum.adimlar) >= b.adim:
            self._kis(f"adım tavanı ({b.adim})")
        gecen = time.monotonic() - self._baslangic
        if b.saniye and gecen >= b.saniye:
            self._kis(f"süre tavanı ({b.saniye:.0f} sn)")
        if b.sorgu and arac.maliyet != "sifir" and self.kosum.sorgu_sayisi >= b.sorgu:
            self._kis(f"sorgu tavanı ({b.sorgu})")

    def _kis(self, neden: str) -> None:
        self.kosum.kisildi = True
        self.kosum.kisilma_nedeni = neden
        _log.info("ajan koşusu kısıldı: %s (adım=%d sorgu=%d)",
                  neden, len(self.kosum.adimlar), self.kosum.sorgu_sayisi)
        raise ButceAsimi(neden)

    # --- yürütme -----------------------------------------------------------------

    def calistir(self, arac_adi: str, *args: Any, makbuz: str | None = None,
                 **kwargs: Any) -> Any:
        """Tek bir aracı **dört kapıdan geçirerek** çalıştırır ve adımı kaydeder.

        `makbuz`: bu adımın ürettiği kanıtın kimliği (çağıran biliyorsa geçirir).
        Araç `makbuz` beyan ediyor ama çağıran kimlik vermiyorsa bu bir **boşluktur**
        ve adım kaydında `receipt=None` olarak görünür — gizlenmez.
        """
        arac = tools.get(arac_adi)                 # KAYIT kapısı (uydurma araç = KeyError)
        self._yetki_kapisi(arac)
        self._deterministik_once_kapisi(arac)
        self._butce_kapisi(arac)

        kaynak = self.kaynaklar.get(arac.baglanma) if arac.baglanma != "modul" else None
        t0 = time.monotonic()
        hata = None
        try:
            fn = arac.cagir(kaynak)
            sonuc = fn(*args, **kwargs)
        except Exception as exc:
            hata = f"{type(exc).__name__}: {exc}"[:200]
            raise
        finally:
            # Adım BAŞARISIZ olsa da kaydedilir: bütçe tüketildi ve denetçi neyin
            # denendiğini görmeli. Sessizce kaybolan bir adım, yapılmamış bir adım
            # gibi okunur ve koşumun maliyeti anlaşılmaz olur.
            self.kosum.adimlar.append(Adim(
                arac=arac.ad, determinizm=arac.determinizm,
                sure_ms=int((time.monotonic() - t0) * 1000),
                makbuz=makbuz, hata=hata,
            ))
            if arac.determinizm == "deterministik":
                self._denenen_araclar.add(arac.ad)
        return sonuc

    def kalan(self) -> dict[str, Any]:
        """Bütçenin kalanı — çağıran bir sonraki adımı göze alıp alamayacağını sorabilir."""
        b = self.butce
        return {
            "adim": max(0, b.adim - len(self.kosum.adimlar)) if b.adim else None,
            "saniye": max(0.0, b.saniye - (time.monotonic() - self._baslangic))
                      if b.saniye else None,
            "sorgu": max(0, b.sorgu - self.kosum.sorgu_sayisi) if b.sorgu else None,
        }
