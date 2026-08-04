"""FAZ 1.11 — **KADEMELİ DÜŞÜŞ: hangi seviyede koşuyoruz?**

## Ölçülen boşluk — ve yol haritasının *"yeni kod YOK"* demesinin nedeni

`FailoverSqlGenerator` **zaten** sırayla dener: `anthropic → gemini → groq → xai →
ollama → rule`. Yani **düşüş mekanizması var**. Eksik olan iki şey:

1. **Kayıt**: bir sağlayıcı düşüp ötekine geçildiğinde `AuditLog`'a **hiçbir satır**
   yazılmıyordu — yalnız `_ask`/`_chat` içinde bir `WARNING` kütüğü. Kütük **aranabilir
   değildir**; *"dün kaç kez ikinci seviyeye düştük"* sorusu **cevapsızdı**.
2. **Gösterge**: kullanıcı hangi seviyede cevap aldığını **göremiyordu**. Bir cevap
   `rule` ile üretildiyse bu **kategorik** olarak farklı bir cevaptır ve rozet bunu
   söylemek zorundadır.

## 🔴 ÜÇ SEVİYE — sağlayıcı sayısı değil, KATEGORİ

Failover listesi beş sağlayıcı taşıyabilir; **kullanıcı için** anlamlı olan üç kategori:

| seviye | ne | kullanıcıya anlamı |
|---|---|---|
| **1** | birincil LLM | normal |
| **2** | **yedek** LLM | *"birincil sağlayıcı yanıt vermedi"* — cevap aynı sınıfta |
| **3** | `rule` (**LLM YOK**) | 🔴 **kategorik olarak farklı** cevap |

*Beş seviyeli bir gösterge, kullanıcının kararını değiştirmeyen bir ayrımı ekrana
taşırdı.* Seviye 2 ile 3 arasındaki fark **kararı değiştirir**; gemini ile groq
arasındaki fark **değiştirmez**.

## ⚠ Bu modül düşüşü YAPMAZ — SINIFLANDIRIR

Düşüş `FailoverSqlGenerator`'ın işidir ve **dokunulmadı** (yol haritası: *"yeni kod
yok"*). Burada olan tek şey: *"bu üretici hangi seviyeye karşılık geliyor"* sorusunun
**tek sahipli** cevabı. İkinci bir sınıflandırma yazmak, rozet ile audit'in **ayrışması**
demekti — biri *"seviye 2"* derken öteki *"seviye 3"* gösterirdi.
"""

from __future__ import annotations

from typing import Any

#: Kullanıcı için anlamlı üç kategori.
SEVIYELER = (1, 2, 3)

#: LLM'siz üreticinin sınıf adı — seviye 3'ün belirteci.
KURAL_URETICI = "RuleBasedSqlGenerator"

_ETIKET = {
    1: "birincil",
    2: "yedek sağlayıcı",
    3: "LLM YOK — kural tabanlı",
}


def uretici_adi(gen: Any) -> str:
    """Üreticinin insan-okur adı — `_provider` varsa o, yoksa sınıf adı.

    `FailoverSqlGenerator`'ın kendi hata biçimiyle **aynı** kural; ikinci bir adlandırma
    yazmak, audit satırıyla kütük satırının **farklı adlar** kullanması demekti.
    """
    return str(getattr(gen, "_provider", None) or type(gen).__name__)


def seviye(gen: Any, *, sira: int) -> int:
    """`(üretici, listedeki sıra)` → **kullanıcı için anlamlı** seviye.

    🔴 Sıra 0 **her zaman** seviye 1 değildir: yapılandırma `rule`'u tek başına
    bırakabilir (anahtarsız kurulum) ve o durumda **birinci** sağlayıcı zaten seviye
    **3**'tür. Sırayı seviyeyle karıştırmak, LLM'siz bir kurulumu *"normal"* gösterirdi.
    """
    if type(gen).__name__ == KURAL_URETICI:
        return 3
    return 1 if sira == 0 else 2


def etiket(sv: int) -> str:
    return _ETIKET.get(sv, "bilinmiyor")


def dusus_kaydi(yeni: Any, *, yeni_sira: int, onceki_seviye: int = 1) -> dict[str, Any] | None:
    """Bir düşüş **olayı** — ya da `None` (düşüş yoksa).

    `None` döner eğer seviye **değişmediyse**: gemini'den groq'a geçmek kullanıcı için
    bir olay **değildir** (ikisi de seviye 2) ve her sağlayıcı denemesini audit'e yazmak,
    kaydı **gürültüye** boğar — *gürültüyle dolan bir kanıt defteri okunmaz olur.*

    🔴 **`onceki_seviye` AÇIKÇA VERİLİR — ve bu bir düzeltme.** İlk sürüm önceki
    ÜRETİCİYİ alıp seviyesini `sira=0` ile hesaplıyordu; yani *"önceki her zaman listenin
    başıdır"* diye **gizli bir varsayım** taşıyordu. Kendi sınamam onu gösterdi:
    `dusus_kaydi(gemini, gemini, yeni_sira=2)` — aynı üretici, aynı seviye — bir **olay**
    üretti. *Gizli bir varsayım, doğru olduğu sürece görünmez; yanlış olduğu gün
    açıklanamaz bir kayıt bırakır.*
    """
    sv_yeni = seviye(yeni, sira=yeni_sira)
    sv_onceki = onceki_seviye if onceki_seviye in SEVIYELER else 1
    if sv_yeni <= sv_onceki:
        return None
    return {
        "onceki_seviye": sv_onceki,
        "seviye": sv_yeni,
        "uretici": uretici_adi(yeni),
        "ozet": f"seviye {sv_onceki} → {sv_yeni} ({etiket(sv_yeni)})",
    }


def istekten_rapor(request: Any) -> dict[str, Any]:
    """`request` → seviye raporu. Göstergenin **tek** veri kaynağı.

    ⚠ **Yeni bir uç AÇILMADI:** rozet `/schema`'yı **zaten** yokluyor; ikinci bir poll
    eklemek, aynı bilgiyi iki kanaldan taşımak ve ikisinin **ayrışması** demekti.

    `_last` (son BAŞARILI üretici) okunur, listenin başı değil: kullanıcının **aldığı**
    cevap hangi seviyeden geldiyse gösterge onu söylemelidir — *"birinci sağlayıcı
    tanımlı"* ile *"birinci sağlayıcı cevap veriyor"* aynı şey değildir.
    """
    try:
        llm = getattr(getattr(request, "app", None), "state", None)
        llm = getattr(llm, "llm", None) if llm is not None else None
        if llm is None:
            return {}
        gens = getattr(llm, "_gens", None)
        if gens:
            son = getattr(llm, "_last", None) or gens[0]
            return rapor(son, sira=gens.index(son) if son in gens else 0)
        return rapor(llm, sira=0)
    except Exception:                          # noqa: BLE001 — gösterge akışı KIRMAZ
        return {}


def rapor(gen: Any, *, sira: int = 0) -> dict[str, Any]:
    """Göstergeye giden blok: `{llm_seviye, llm_seviye_etiket, llm_uretici}`.

    ⚠ Seviye **3** bir hata değil bir **durumdur**: sistem çalışıyor, ama cevaplar
    **kategorik olarak farklı** bir yoldan geliyor. Rozet bunu *"çevrimdışı"* gibi
    göstermemelidir — *"çalışıyor ama LLM yok"* ile *"hiç çalışmıyor"* aynı şey değildir.
    """
    sv = seviye(gen, sira=sira)
    return {"llm_seviye": sv, "llm_seviye_etiket": etiket(sv), "llm_uretici": uretici_adi(gen)}
