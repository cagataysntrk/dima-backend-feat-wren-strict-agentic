"""FAZ 5.2 — **PAYLAŞILABİLİR LİNK.** [bayrak: `tur_paylas`]

## Ölçülen erişilemezlik — ve neden en öğretici bulgu

*"Müdüre 3 cümle yaz"* niyet olarak **`TUR_ANLAT`'a çok yakın** (`followup.py`'nin
`_ANLAT` sözlüğü: *analiz et · yorumla · özetle · anlat*), ama sözlükte *"yaz"* /
*"3 cümle"* olmadığı için **yakalanmıyordu**. Yani:

> 🔴 **Çalışan, testli bir yetenek — bir kelime yüzünden kullanıcıya kapalı.**

`share|public` uç sayısı da **sıfırdı**. Bu faz **yeni bir anlatı motoru yazmaz**;
`TUR_ANLAT`'ın zaten ürettiği şeye **erişim** ve **taşınabilirlik** ekler.

## 🔴 ÜÇ DEĞİŞMEZ — ve neden üçü de zorunlu

| değişmez | olmasaydı |
|---|---|
| **İmzalı** | token uydurulur; herhangi biri başkasının raporunu açar |
| **Süreli** | bir kez sızan link **süresiz** bir veri kapısı olur |
| **Maskeli** | link **kimliksiz** açılır → maskesiz bir yükü herkese vermek olurdu |

⚠ **Maskeleme burada YENİDEN YAZILMAZ:** `pii.py` tek çıkış noktasıdır ve bu modül onu
**çağırır**. İkinci bir maskeleyici, iki maskenin **ayrışması** demekti — ve ayrışan
taraf her zaman **daha gevşek** olanıdır.

## ⚠ Link kimliksiz açılır — bu yüzden yük DARALTILIR

Paylaşılan şey bir **rapor görüntüsüdür**, bir sorgu yüzeyi değil: `cube_query` **taşınır
ama çalıştırılmaz**. Aksi hâlde link, tenant'ın veri yüzeyine **kimliksiz bir kapı**
açardı. *Bir paylaşım linki bir oturum değildir.*
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

#: Varsayılan ömür — **7 gün**. ⚠ Sonsuz bir seçenek **yoktur**: bir kez sızan süresiz
#: link, geri alınamayan bir veri kapısıdır.
VARSAYILAN_TTL = 7 * 24 * 3600

#: Azami ömür. İstemci daha uzun isterse **kırpılır** (sessizce değil — `ttl` yanıtta
#: döner ve kullanıcı gerçek süreyi görür).
AZAMI_TTL = 30 * 24 * 3600


class PaylasimHatasi(ValueError):
    """Token geçersiz/süresi dolmuş. **Fail-closed** — şüphede açılmaz."""


def _gizli() -> bytes:
    """İmza anahtarı — **control-plane'in kendi JWT secret'ı**.

    🔴 İkinci bir secret **üretilmez**: rotasyonu, saklanması ve sızma davranışı olan
    ikinci bir sır, unutulan bir sırdır. ⚠ Secret yoksa **hata** — anahtarsız bir imza,
    imza değildir ve fail-open bir paylaşım kapısı açardı.
    """
    from control_plane.config import get_auth_settings

    s = str(getattr(get_auth_settings(), "jwt_secret", "") or "")
    if not s:
        raise PaylasimHatasi(
            "Paylaşım imzası için `jwt_secret` gerekli. Anahtarsız bir imza, imza "
            "değildir — bu uç fail-closed davranır ve link üretmez.")
    return s.encode("utf-8")


def _b64(ham: bytes) -> str:
    return base64.urlsafe_b64encode(ham).decode("ascii").rstrip("=")


def _b64_coz(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def uret(yuk: dict[str, Any], *, ttl: int | None = None, simdi: float | None = None) -> str:
    """Maskeli yükü **imzalı ve süreli** bir token'a çevirir.

    ⚠ Yük **çağıran tarafından maskelenmiş** gelmelidir; bu fonksiyon maskelemez ve
    maskelendiğini **varsaymaz** — `paylasim_yuku()` o işi yapar ve kapı ikisinin
    birlikte kullanıldığını kilitler.
    """
    omur = min(int(ttl or VARSAYILAN_TTL), AZAMI_TTL)
    govde = dict(yuk)
    govde["exp"] = int((simdi if simdi is not None else time.time()) + omur)
    ham = json.dumps(govde, ensure_ascii=False, separators=(",", ":"),
                     sort_keys=True).encode("utf-8")
    imza = hmac.new(_gizli(), ham, hashlib.sha256).digest()
    return f"{_b64(ham)}.{_b64(imza)}"


def coz(token: str, *, simdi: float | None = None) -> dict[str, Any]:
    """Token → yük. **Fail-closed:** imza ya da süre bozuksa `PaylasimHatasi`.

    🔴 İmza **sabit-zamanlı** karşılaştırılır (`compare_digest`): normal `==`, token'ı
    bayt bayt tahmin etmeye açık bir zamanlama kanalı bırakırdı.
    """
    try:
        g_b64, i_b64 = str(token or "").split(".", 1)
        ham, imza = _b64_coz(g_b64), _b64_coz(i_b64)
    except Exception as exc:                                  # noqa: BLE001
        raise PaylasimHatasi("Bozuk paylaşım linki.") from exc
    if not hmac.compare_digest(hmac.new(_gizli(), ham, hashlib.sha256).digest(), imza):
        raise PaylasimHatasi("Paylaşım linki doğrulanamadı (imza uyuşmuyor).")
    try:
        govde = json.loads(ham.decode("utf-8"))
    except Exception as exc:                                  # noqa: BLE001
        raise PaylasimHatasi("Bozuk paylaşım yükü.") from exc
    son = float(govde.get("exp") or 0)
    if son <= (simdi if simdi is not None else time.time()):
        raise PaylasimHatasi("Paylaşım linkinin süresi doldu.")
    return govde


def paylasim_yuku(resp: Any) -> dict[str, Any]:
    """`AskResponse` → **paylaşılabilir, maskeli, DARALTILMIŞ** yük.

    🔴 **`cube_query` TAŞINIR AMA ÇALIŞTIRILMAZ.** Link kimliksiz açılır; çalıştırılabilir
    bir sorgu taşımak, tenant'ın veri yüzeyine **kimliksiz bir kapı** açardı.
    *Bir paylaşım linki bir oturum değildir.*

    🔴 **`sql` TAŞINMAZ.** Üretilen SQL şema hakkında bilgi sızdırır ve paylaşılan şey
    bir **rapor görüntüsüdür**, bir sorgu değil.

    ⚠ Maskeleme `pii.py`'nin **kendi** fonksiyonuyla yapılır — ikinci bir maskeleyici
    yazmak, iki maskenin ayrışması demekti.
    """
    from app import pii

    d = resp.model_dump() if hasattr(resp, "model_dump") else dict(resp or {})
    satirlar = ((d.get("result") or {}).get("rows")
                if isinstance(d.get("result"), dict) else None) or []
    maskeli, _ = pii.mask_rows([r for r in satirlar if isinstance(r, dict)])
    return {
        "question": pii.mask_text(str(d.get("question") or "")),
        "note": pii.mask_text(str(d.get("note") or "")) or None,
        "narration": pii.mask_text(str(d.get("narration") or "")) or None,
        "columns": ((d.get("result") or {}).get("columns")
                    if isinstance(d.get("result"), dict) else None) or [],
        "rows": maskeli,
        "source": d.get("source"),
        # Görüntü ipucu taşınır (grafik aynı görünsün); sorgu **taşınmaz**.
        "view_hint": d.get("view_hint"),
    }
