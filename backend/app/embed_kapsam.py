"""FAZ 6.5 — **gömme kapsamı ve kota.** [bayrak: `embed` — 🔴 **AÇILAMAZ**]

## 🔴 P0: `embed` BAYRAĞI BU TURDA AÇILAMAZ — ve sebebi ÖLÇÜLDÜ

Yol haritasının bağlayıcı şartı:

> *"Wren RLS'i gömülü pano grafiklerini kapsamıyorsa `embed` **AÇILMAZ**;
> `always_filter` tek başına yeterli sayılmaz."*

**Ölçüm:** `Settings.motor_cls == "off"` — motor-RLS **hiç açık değil** ve açılması **36
çağrı sitesinin kimlik geçirmesine** bağlı (açık borç #1). Yani şartın *"kapsıyor mu"*
sorusu bile sorulamıyor: **kapsayacak bir mekanizma çalışmıyor.**

> ⚠ `1.1`'in inmiş olması `6.5`'i güvenli **YAPMAZ** — yol haritasının kendi cümlesi.

Bu yüzden bu modül **kapsam kararlarını yazar** ama bayrak **kapalı doğar**. *Bir
güvenlik sınırını ölçmeden açmak, onu hiç kurmamaktan kötüdür: kurulduğu sanılır.*

## Kapsam bir KAYITTIR, bir URL parametresi değil

🔴 **Looker'ın imzalı-URL modeli reddedildi.** İmzalı bir URL'de kapsamı değiştirmek
imzayı bozar — ama **iptal etmek imkânsızdır**: dağıtılmış bir URL geri çağrılamaz.
`EmbedToken.iptal_edildi` **anında** düşer.
"""

from __future__ import annotations

from typing import Any


class EmbedReddi(ValueError):
    """Gömme çağrısı **fail-closed** reddedildi."""


def p0_engeli(settings: Any) -> str | None:
    """🔴 `embed` açılabilir mi? Açılamazsa **sebep**, açılabilirse `None`.

    ⚠ Bu fonksiyon bir **kapıdır**, bir öneri değil: `embed` bayrağını okuyan her yol
    önce buradan geçmeli. *Bir ön koşulu belgeye yazıp koda yazmamak, onu ilan edip
    uygulamamaktır.*
    """
    cls = str(getattr(settings, "motor_cls", "off") or "off").lower()
    if cls != "on":
        return (f"🔴 P0: motor-RLS `{cls}` — gömülü yüzeyde çapraz-tenant sızıntısını "
                f"engelleyecek mekanizma ÇALIŞMIYOR. Yol haritası: *«`always_filter` "
                f"tek başına yeterli sayılmaz»*. `embed` AÇILAMAZ.")
    return None


def kapsam_izin_veriyor_mu(scope: dict[str, Any] | None, cube: str,
                           olculer: list[str] | None = None,
                           boyutlar: list[str] | None = None) -> None:
    """Token kapsamı bu sorguya izin veriyor mu? İzin yoksa `EmbedReddi`.

    🔴 **Fail-closed ve BEYAZ LİSTE**: kapsamda **olmayan** her şey **yasaktır**. Bir
    kara liste, yarın eklenen bir cube'u **sessizce açardı**.

    ⚠ Boş/eksik kapsam **her şeyi açmaz, hiçbir şeyi açmaz**: *"kapsam belirtilmedi"* ile
    *"kapsam sınırsız"* aynı şey değildir ve ikincisi asla varsayılan olamaz.
    """
    s = scope or {}
    izinli_cubelar = s.get("cubes")
    if not izinli_cubelar:
        raise EmbedReddi(
            "gömme token'ı kapsamsız — «kapsam belirtilmedi» ile «kapsam sınırsız» aynı "
            "şey değildir ve ikincisi asla varsayılan olamaz.")
    if cube not in izinli_cubelar:
        raise EmbedReddi(f"`{cube}` bu token'ın kapsamı dışında.")
    tanim = (s.get("izin") or {}).get(cube) or {}
    for alan, istenen in (("measures", olculer or []), ("dimensions", boyutlar or [])):
        izinli = tanim.get(alan)
        if izinli is None:
            continue                     # o eksende kısıt yok
        disari = [x for x in istenen if x not in izinli]
        if disari:
            raise EmbedReddi(f"`{cube}.{alan}` kapsamı dışında: {disari}")


def kota_kontrol(kota: int | None, kullanim: int) -> None:
    """Kota aşımı → `EmbedReddi` (uç bunu **429**'a çevirir).

    🔴 `kota is None` **sınırsız DEĞİL**, *"kota belirtilmedi"* demektir ve **reddedilir**:
    sınırsız bir gömme token'ı, faturayı **bilinmez** yapar ve bir gün kimsenin
    açıklayamadığı bir maliyet üretir.
    """
    if kota is None:
        raise EmbedReddi(
            "gömme token'ında kota belirtilmemiş — sınırsız bir token, faturayı bilinmez "
            "yapar. Kota bir sayı olmalı.")
    if kullanim >= kota:
        raise EmbedReddi(f"kota doldu ({kullanim}/{kota}).")


def token_gecerli_mi(iptal_edildi: bool) -> None:
    """🔴 İptal **anında** düşer — imzalı bir URL'nin yapamadığı tek şey budur."""
    if iptal_edildi:
        raise EmbedReddi("bu gömme token'ı iptal edilmiş.")
