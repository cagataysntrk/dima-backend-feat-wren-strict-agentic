"""FAZ 1.2b — **`safe_call()`: ham veri LLM'e gitmez, TEK kapıdan.**

## Ölçülen kusur — kuralın ÜÇ sahibi vardı

*"Ham veri LLM'e gitmez"* bugün **üç ayrı yerde** uygulanıyor:

| # | Yer | Ne yapıyor |
|---|---|---|
| 1 | `app/llm.py::_schema_prompt` | `prompt_safe_values` ile kolon değerlerini süzer |
| 2 | `app/cube_router.py::build_catalog` | aynısını **katalog** metni için yapar |
| 3 | `app/routers/ask.py:3815` | `is_sensitive` ile doğrudan süzer |

Üçü de **doğru** ama üçü de **girdi tarafında**. Girdiyi kuran yeni bir yol açılırsa
(ve `select_cube`'un kataloğu `llm.py` DIŞINDA kuruluyor) kural o yolda **hiç uygulanmaz**.
§D.2/1'in hükmü bu kurala dayanıyor ve **tekilleştirme hiçbir maddede yoktu**.

## Neden ÇIKIŞ tarafı — girdi süzgeçleri KALIYOR

`safe_call` üç süzgecin **yerine geçmez**, **arkalarına** durur: son savunma. Girdi
süzgeci *"bu değeri prompt'a koyma"* der; `safe_call` *"prompt'ta ne varsa **giderken**
bir daha bak"* der. İkisi farklı sorulardır ve ikincisi **yeni bir yol açıldığında** da
sorulur — tekilleştirmenin anlamı budur.

🔴 **Ateşlerse bu bir BULGUDUR, bir gürültü değil.** Girdi süzgeçleri çalışıyorsa
`safe_call` **hiç ateşlemez**. Ateşlediği gün, yukarıdaki üç süzgeçten birinin
kapsamadığı bir yol bulunmuş demektir — ve o bilgi `AuditLog`'a yazılır.

## Tespit `pii.py`'den — dördüncü bir desen sözlüğü YAZILMAZ

TCKN/e-posta/telefon/IBAN kalıplarının **tek sahibi** `app/pii.py`'dir. Burada ikinci bir
regex kümesi yazmak, bu deponun 1 numaralı kusuru olurdu: iki sözlük zamanla ayrışır ve
hangisinin doğru olduğu bilinemez. `pii.mask_text(x) != x` → *"bu metinde maskelenecek
bir şey var"*.
"""

from __future__ import annotations

from typing import Any, Callable

from app.logging_setup import get_logger

_log = get_logger("llm_guard")


class LlmVeriSizintisi(Exception):
    """Sağlayıcıya gidecek yükte **maskelenmemiş kişisel veri** bulundu. Çağrı **yapılmadı**."""


def ihlalleri_bul(yuk: str) -> list[str]:
    """Yükte maskelenmemiş kişisel veri var mı → bulunan **tür adları**.

    Değerin kendisi **döndürülmez ve loglanmaz**: bir sızıntıyı raporlarken sızdırmak,
    kapının kendisini bir sızıntı yüzeyine çevirirdi.
    """
    if not yuk:
        return []
    from app import pii

    bulunan: list[str] = []
    for ad, maske in (("TCKN", pii.mask_tckn), ("e-posta", pii.mask_email),
                      ("telefon", pii.mask_phone), ("IBAN", pii.mask_iban)):
        if maske(yuk) != yuk:
            bulunan.append(ad)
    return bulunan


def safe_call(gonder: Callable[[], Any], *, yuk: str, ad: str,
              principal: Any = None) -> Any:
    """Sağlayıcıya giden **tek kapı**. İhlalde çağrı **yapılmaz**.

    `gonder` bir **sıfır-argümanlı çağrılabilirdir** (closure): imzayı sarmalamak yerine
    çağrıyı geciktirmek, sağlayıcı imzaları birbirinden farklı olduğu için tek doğru
    çözüm — ortak bir imza uydurmak, üç sağlayıcının **dördüncü** bir temsilini yaratırdı.

    🔴 **Fail-closed.** İhlalde `LlmVeriSizintisi` fırlar ve çağrı **hiç yapılmaz**;
    maskeleyip göndermek **yanlış** olurdu: yükü sessizce değiştirmek, modelin gördüğü
    şeyle bizim sandığımız şeyi ayrıştırır ve hata **teşhis edilemez** hâle gelir.
    """
    ihlaller = ihlalleri_bul(yuk)
    if ihlaller:
        _log.error("LLM VERİ SIZINTISI ENGELLENDİ (%s): %s — çağrı YAPILMADI", ad,
                   ", ".join(ihlaller))
        try:
            from control_plane import audit

            audit.record(principal, "llm_leak_blocked",
                         generated_sql=f"{ad}: {', '.join(ihlaller)}")
        except Exception:                                    # noqa: BLE001
            _log.warning("sızıntı audit'e yazılamadı — kütükte kaldı", exc_info=True)
        raise LlmVeriSizintisi(
            f"`{ad}` çağrısının yükünde maskelenmemiş kişisel veri var "
            f"({', '.join(ihlaller)}). Çağrı YAPILMADI (fail-closed).\n"
            "Bu bir BULGUDUR: girdi süzgeçleri (`sensitivity.prompt_safe_values` · "
            "`cube_router.build_catalog` · `ask.py`) çalışıyorsa bu kapı HİÇ ateşlemez. "
            "Ateşlediyse, o üçünün kapsamadığı bir yol açılmış demektir.")
    return gonder()
