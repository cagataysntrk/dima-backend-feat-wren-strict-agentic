"""FAZ 6.6 — **sohbet kimliği → DİMA kimliği eşlemesi.** [bayrak: `kanal_kimlik`]

## 🔴 EŞLEMESİ OLMAYAN KANAL KULLANICISININ SORUSUNA **YANIT VERİLMEZ**

Yol haritasının tek kapısı budur ve sertliği bilinçlidir. Alternatif — *"eşleme yoksa
sınırlı bir cevap ver"* — bir **kimliksiz** kullanıcıya veri göstermek olurdu; ve
sınırın ne olduğunu kimse söyleyemezdi, çünkü RLS **kimliğe** dayanır.

## 🔴 E-POSTA BİR İDDİADIR, KİMLİK KANITI DEĞİL

En cazip kısayol: *"Slack e-postası `ali@x.com`, DİMA'da da `ali@x.com` var, demek ki
aynı kişi."* **Değildir**:

- kanal yöneticisi görünen e-postayı **değiştirebilir**,
- bir takma hesap aynı adresi **gösterebilir**,
- ve bir kez yanlış eşlenen kimlik, o kişinin **göremeyeceği veriyi** ona açar.

> *Bir kimliği çıkarımla kurmak, RLS'i çıkarımla kurmaktır.*

Microsoft'un kendi belgesi Slack e-postasının Teams hesabına güvenilir eşlenemeyeceğini
söylüyor `[DOĞRULANMADI — birincil kaynak okunmadı]`.

⚠ Bu modül **e-posta okumaz**: parametrelerinde bile yoktur. *Bir kısayolu yasaklamanın
en güvenilir yolu, onu mümkün kılan veriyi hiç almamaktır.*
"""

from __future__ import annotations

from typing import Any

KANALLAR = ("slack", "teams", "whatsapp")


class KimlikYok(PermissionError):
    """Eşleme yok → **yanıt verilmez**. Fail-closed."""


def eslesme_bul(kayitlar: list[dict[str, Any]] | None, kanal: str,
                kanal_kullanici_id: str) -> dict[str, Any] | None:
    """Eşlemeyi bulur. Silinmiş (soft-delete) kayıt **eşleşme değildir**.

    ⚠ Saf fonksiyon: DB erişimi çağıranın işidir ve bu, kuralın **DB'siz test
    edilebilmesini** sağlar — bir güvenlik kuralının testi bir veritabanına bağlı
    olmamalı.
    """
    for k in kayitlar or []:
        if k.get("deleted_at"):
            continue
        if (str(k.get("kanal")) == str(kanal)
                and str(k.get("kanal_kullanici_id")) == str(kanal_kullanici_id)):
            return k
    return None


def cozumle(kayitlar: list[dict[str, Any]] | None, kanal: str,
            kanal_kullanici_id: str) -> str:
    """Kanal kullanıcısı → `dima_user_id`. Eşleme yoksa **`KimlikYok`**.

    🔴 Dönüş bir `None` **değil bir istisnadır**: `None` dönseydi çağıran onu *"anonim
    kullanıcı"* diye yorumlayabilir ve akış devam ederdi. *Bir kimlik kararı sessizce
    başarısız olamaz.*
    """
    if kanal not in KANALLAR:
        raise KimlikYok(f"bilinmeyen kanal: {kanal!r}")
    e = eslesme_bul(kayitlar, kanal, kanal_kullanici_id)
    if e is None:
        raise KimlikYok(
            f"`{kanal}` kullanıcısı `{kanal_kullanici_id}` için onaylanmış bir kimlik "
            f"eşlemesi YOK — soruya yanıt verilmez. Bir yönetici eşlemeyi onaylamalı; "
            f"e-posta benzerliği bir kimlik kanıtı DEĞİLDİR.")
    # 🔴 Onaylayan admin **kayıtta olmak zorunda**: yoksa bu eşleme bir insan tarafından
    # onaylanmamış demektir ve bir çıkarımdan farkı yoktur.
    if not str(e.get("onaylayan_admin_id") or "").strip():
        raise KimlikYok(
            "eşleme kaydında `onaylayan_admin_id` YOK — bu eşleme bir insan tarafından "
            "onaylanmamış ve bir çıkarımdan farkı yoktur.")
    uid = str(e.get("dima_user_id") or "").strip()
    if not uid:
        raise KimlikYok("eşleme kaydında `dima_user_id` boş.")
    return uid
