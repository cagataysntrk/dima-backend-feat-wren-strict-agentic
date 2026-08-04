"""FAZ 1.8 — **AUDIT ZİNCİRİ + OTel eşlemesi.** Bir kayıt silinirse **görünür** olmalı.

## Neden zincir

`AuditLog` *"append-only erişim kanıtı"* diyor — ama **append-only bir BEYANDIR**, bir
mekanizma değil: bir satır `DELETE` edilirse geriye **hiçbir iz** kalmaz. Bir kanıt kaydı,
eksildiğini **kendisi** söyleyemiyorsa kanıt değildir.

Her kayıt bir öncekinin hash'ini taşır (`onceki_kayit_hash`); ilki `genesis`. Bir satır
silinir ya da değiştirilirse zincir **kopar** ve doğrulama onu **adıyla** gösterir.

## 🔴 ZİNCİRİN GARANTİ ETTİĞİ VE ETMEDİĞİ — ikisi de yazılı

**Eder:** silme ve **değiştirme** tespiti. Bir satırın alanı değişirse hash'i değişir ve
**sonraki** satırın `onceki_kayit_hash`'i tutmaz.

**ETMEZ:** eşzamanlı yazımların **sıralanması**. İki istek aynı anda yazarsa ikisi de aynı
*"son kayıt"*ı okuyup **çatal** üretebilir. ⚠ Bu bir kusur değil bir **sınırdır** ve
gizlenmez: çatal da **tespit edilir** (aynı `onceki_kayit_hash`'i taşıyan iki kayıt) ve
doğrulama onu ayrı bir bulgu olarak raporlar. Kilitle serileştirmek her audit yazımına bir
kilit maliyeti bindirirdi; *"başarı audit yazılmadan raporlanmaz"* değişmezi için bu takas
bilinçle ters yönde yapıldı.

**ETMEZ:** kötü niyetli bir yöneticinin **tüm zinciri** yeniden yazmasını. Bunun için
harici bir çıpa (dış zaman damgası / WORM depolama) gerekir ve o **bu maddede yok** —
yazılmadığı için de *"korunuyoruz"* denmiyor.

## OTel GenAI — yeni kolon YAZILMAZ, EŞLEME yapılır

Ölçüldü: `InteractionLog` **zaten** `llm_model` · `llm_input_tokens` ·
`llm_output_tokens` · `llm_latency_ms` · `source` taşıyor. OTel'in adlarıyla ikinci bir
kolon kümesi açmak, aynı gerçeğin **iki kopyası** olurdu — bu deponun 1 numaralı kusuru.
`otel_nitelikleri()` var olan satırı **standart adlara çevirir**; depo tek kalır.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

#: Zincirin ilk halkası. `None` değil bir **değer**: `None` *"hash hesaplanmadı"* ile
#: karıştırılırdı; `genesis` *"burası başlangıç"* der.
GENESIS = "genesis"

#: Hash'e giren alanlar — **anlamı taşıyanlar**. `id` girmez (rastgele) ve `ts` **girer**
#: (bir kaydın zamanını değiştirmek, kaydı değiştirmektir).
ZINCIR_ALANLARI = (
    "tenant_id", "ts", "actor_user_id", "actor_kind", "role_key", "action",
    "nl_question", "generated_sql", "touched_models_json", "rows_returned",
    "masked_columns_json", "ip", "contract_id",
)


def kayit_hash(payload: dict[str, Any], onceki: str | None) -> str:
    """Bir audit kaydının zincir hash'i — **saf fonksiyon**.

    Kanonik JSON (`sort_keys`) **zorunlu**: alan sırası değiştiğinde hash değişseydi
    zincir **kendiliğinden** koparıdı ve doğrulama gürültüye boğulurdu — *gürültüyle
    ateşleyen bir kapı kapatılır.*
    """
    gövde = {a: _kanonik(payload.get(a)) for a in ZINCIR_ALANLARI}
    gövde["_onceki"] = onceki or GENESIS
    ham = json.dumps(gövde, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(ham.encode("utf-8")).hexdigest()


def _kanonik(v: Any) -> Any:
    """`datetime`/`UUID` → ISO/str. Tip temsili değişirse hash değişir ve zincir
    **yanlış** kopardı; bu dönüşüm o kaymayı kapatır."""
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    iso = getattr(v, "isoformat", None)
    return iso() if callable(iso) else str(v)


def zinciri_dogrula(kayitlar: list[dict[str, Any]]) -> list[str]:
    """Zincir bulgularını döndürür — **boş liste = sağlam**.

    Üç ayrı bulgu sınıfı, üçü de **adıyla**:
    * **KOPUK** — bir kaydın `onceki_kayit_hash`'i öncekinin hash'iyle tutmuyor
      (silme ya da değiştirme).
    * **BOZULMUŞ** — kaydın kendi `kayit_hash`'i içeriğinden yeniden üretilemiyor.
    * **ÇATAL** — iki kayıt aynı `onceki_kayit_hash`'i taşıyor (eşzamanlı yazım).

    ⚠ Üçünü tek bir *"zincir bozuk"* mesajına indirmek, **hangi** olayın yaşandığını
    gizlerdi — ve silme ile eşzamanlılık **çok farklı** şeylerdir.
    """
    bulgular: list[str] = []
    onceki_hash = GENESIS
    goruldu: dict[str, int] = {}
    for i, k in enumerate(kayitlar or []):
        beklenen = kayit_hash(k, k.get("onceki_kayit_hash"))
        if k.get("kayit_hash") and k["kayit_hash"] != beklenen:
            bulgular.append(f"BOZULMUŞ #{i}: kayıt içeriği hash'iyle uyuşmuyor "
                            f"(ts={k.get('ts')})")
        bagli = k.get("onceki_kayit_hash") or GENESIS
        if bagli != onceki_hash:
            bulgular.append(
                f"KOPUK #{i}: `onceki_kayit_hash` beklenenle tutmuyor "
                f"(beklenen {onceki_hash[:12]}…, gelen {str(bagli)[:12]}…) — "
                "aradaki bir kayıt SİLİNMİŞ ya da DEĞİŞTİRİLMİŞ olabilir")
        if bagli in goruldu and bagli != GENESIS:
            bulgular.append(
                f"ÇATAL #{i}: `{bagli[:12]}…` hem #{goruldu[bagli]} hem #{i} tarafından "
                "izleniyor — eşzamanlı yazım (zincirin BİLİNEN sınırı, bkz. modül belgesi)")
        goruldu[bagli] = i
        onceki_hash = k.get("kayit_hash") or beklenen
    return bulgular


# ── OTel GenAI eşlemesi — YENİ KOLON YOK ────────────────────────────────────

def otel_nitelikleri(kayit: dict[str, Any]) -> dict[str, Any]:
    """`InteractionLog` satırı → **OTel GenAI semantic conventions** adları.

    🔴 **Yeni kolon yazılmadı.** Ölçüldü: veri **zaten** orada (`llm_model` ·
    `llm_input_tokens` · `llm_output_tokens` · `llm_latency_ms` · `source`). OTel adlarıyla
    ikinci bir kolon kümesi açmak, aynı gerçeğin **iki kopyası** olurdu ve ikisi zamanla
    ayrışırdı. Bu fonksiyon bir **çeviricidir**, bir depo değil.

    ⚠ Yalnız **dolu** alanlar döner: OTel'de eksik bir nitelik **yokluktur**, `None`
    değil — `gen_ai.usage.input_tokens=null` yayınlamak *"ölçüldü ve sıfırdı"* gibi okunur.
    """
    kaynak = str(kayit.get("source") or "")
    saglayici = kaynak.split(":", 1)[1] if kaynak.startswith("llm:") else (
        "none" if kaynak in ("", "cube", "rule") else kaynak)
    ham = {
        "gen_ai.system": saglayici if kaynak.startswith("llm:") else None,
        "gen_ai.operation.name": kayit.get("kind"),
        "gen_ai.request.model": kayit.get("llm_model"),
        "gen_ai.usage.input_tokens": kayit.get("llm_input_tokens"),
        "gen_ai.usage.output_tokens": kayit.get("llm_output_tokens"),
        "gen_ai.server.time_to_response": kayit.get("llm_latency_ms"),
        # W3C PROV-O çerçevesi: kim (Agent) · ne (Activity) · neye (Entity).
        "prov:wasAssociatedWith": kayit.get("user_id"),
        "prov:activity": kayit.get("kind"),
        "prov:used": kayit.get("cube_query_json") and "cube_query",
    }
    return {k: v for k, v in ham.items() if v is not None}
