"""FAZ 1.3b — **KATMAN B: model allowlist.** Beyan edilmiş ama BOŞ bir katmandı.

## Ölçülen kusur

`control_plane/authorize.py::enforce_query` docstring'i *"**Katman B kancası**: üretilen
SQL'in dokunduğu MDL modelleri, principal'ın `ModelPermission` allowlist'ine karşı
doğrulanır"* diyordu; **gövdesi tek satır: `return`**, üstünde `# TODO(faz-2)`. Yani
**ADR-0014 Karar 5'in beyan ettiği katman hiçbir şey yapmıyordu**.

🔴 **Ve daha kötüsü ölçüldü: `enforce_query`'nin ÇAĞIRANI DA YOKTU.** Yani katman sadece
boş değil, **bağlı bile değildi** — bir stub'ı doldurmak yetmez, onu çağıran bir yol da
gerekir. Bu, `0.5`'in *"19 altın vakalı ölü modül"* bulgusunun güvenlik katmanındaki hâli.

## 🔴 «Boş allowlist geçer» — fail-open, ve düzeltmesi göründüğü kadar basit DEĞİL

Yol haritası *"boş allowlist artık «geçer» DEMEZ (fail-open → fail-closed)"* diyor ve
**yön doğru**. Ama ölçüldü: `ModelPermission` tablosu **her tenant'ta boş**. Harfi harfine
uygulanırsa **her sorgu reddedilir** — yani bir güvenlik katmanı adına **tam kesinti**.

**Ayrım kurtarıyor: «yapılandırılmamış» ile «boş allowlist» AYNI ŞEY DEĞİL.**

| Tenant'ın `ModelPermission` satırı | Anlamı | Karar |
|---|---|---|
| **hiç yok** | Katman B bu tenant'ta **yapılandırılmamış** | Katman A yönetir *(ve bu **loglanır**)* |
| **var, ama model listede yok** | allowlist **aktif**, model **dışarıda** | 🔴 **RED** (fail-closed) |

Böylece yol haritasının şartı **anlamlı hâliyle** sağlanır: bir kez yapılandırıldığında
eksik allowlist **artık geçmez**. Ve yapılandırılmamış hâl **görünür** kalır — sessiz
değil. *Yapılandırılmamış bir katmanı "kapalı" saymak, onu sonsuza dek kapalı tutar.*

## Neden modelleri MOTORUN çözücüsüyle buluyoruz

Yetkilendirdiğimiz küme, motorun **gerçekten planladığı** küme olmalı. İkisi ayrışırsa
"izin verdik" ile "dokunuldu" farklı şeyler olur — ve bu, bir güvenlik katmanının en
sessiz kırılma biçimidir. O yüzden tablo adı çözümü `wren.policy.resolve_model_name` ile
yapılır: **motorun kendi fonksiyonu**, ikinci bir kopya değil.
"""

from __future__ import annotations

from typing import Any

#: Kademeler — `motor_rls` ve `strict_sql_policy` ile **aynı** disiplin.
KADEMELER = ("off", "shadow", "on")


class ModelErisimReddi(Exception):
    """Katman B reddi. `AuthzError` DEĞİL: o Katman A'nın (kaba yetki) hatasıdır ve
    ikisini aynı tipe bindirmek, hangi katmanın reddettiğini **audit'te** belirsizleştirir.
    """


def referans_modeller(sql: str, model_adlari: set[str]) -> set[str]:
    """SQL'in dokunduğu **MDL model** adları.

    🔴 Çözüm `wren.policy.resolve_model_name` ile yapılır — **motorun kendi fonksiyonu**.
    Kendi çözücümüzü yazmak, motorun planladığı kümeyle bizim yetkilendirdiğimiz kümenin
    **ayrışması** demekti; bir güvenlik katmanı için bu en sessiz kırılma biçimidir.

    MDL'de olmayan tablolar **döndürülmez**: onları `strict_mode`'un kaynak-konumu kapısı
    zaten fail-closed reddediyor (§5). Burada tekrar reddetmek, aynı kuralın ikinci sahibi
    olurdu ve iki kapı zamanla ayrışırdı.
    """
    import sqlglot
    from sqlglot import exp

    from wren.policy import resolve_model_name

    try:
        agac = sqlglot.parse_one(sql)
    except Exception as exc:                                 # noqa: BLE001
        raise ModelErisimReddi(
            f"SQL ayrıştırılamadı, Katman B karar veremez: {str(exc)[:120]} — "
            "karar verilemeyen bir yetki sorusu REDDEDİLİR (fail-closed)") from exc

    out: set[str] = set()
    for t in agac.find_all(exp.Table):
        if not t.name:
            continue
        tirnakli = bool(t.this.quoted) if isinstance(t.this, exp.Identifier) else False
        cozulen = resolve_model_name(t.name, tirnakli, model_adlari)
        if cozulen:
            out.add(cozulen)
    return out


def izinli_modeller(principal: Any, oturum: Any) -> set[str] | None:
    """Principal'ın `ModelPermission` allowlist'i. `None` = **yapılandırılmamış**.

    🔴 `None` ile `set()` **farklı** şeylerdir ve fark bu maddenin kalbidir:
    * `None` → bu tenant'ta Katman B **hiç kurulmamış** → Katman A yönetir.
    * `set()` → allowlist **var** ama boş → **hiçbir modele** izin yok (fail-closed).

    İkisini aynı değere indirgemek, ya tüm sistemi kapatır ya katmanı sonsuza dek açık
    bırakır — bu maddenin var olma sebebi tam olarak ikincisiydi.
    """
    from sqlmodel import select

    from control_plane.models import ModelPermission, Role

    tenant = getattr(principal, "tenant_id", None)
    if not tenant:
        return None
    satirlar = list(oturum.exec(
        select(ModelPermission).where(ModelPermission.tenant_id == tenant)))
    if not satirlar:
        return None                            # yapılandırılmamış — beyan değil, YOKLUK

    # 🔴 `Principal` **rol ANAHTARI** taşır (`roles: ["owner"]`), `ModelPermission` ise
    # **rol KİMLİĞİ** (UUID FK). Köprüyü `Role` tablosu kurar. Anahtarları kimliklere
    # çevirmeden tenant genelinde birleştirmek, allowlist'i **rol ayrımı olmadan**
    # uygulamak olurdu — yani istenenden GENİŞ bir izin, sessizce.
    anahtarlar = set(getattr(principal, "roles", None) or [])
    roller = list(oturum.exec(
        select(Role).where(Role.tenant_id == tenant))) if anahtarlar else []
    kimlikler = {r.id for r in roller if r.key in anahtarlar}
    if not kimlikler:
        # Rol çözülemedi: allowlist **kısmen anlaşıldı** demektir. Kısmen anlaşılmış bir
        # yetki kuralını uygulamak, yanlış yönde hata yapma riskini ikiye katlar —
        # `None` döndürüp Katman A'ya bırakmak DÜRÜST olandır (ve görünür kalır).
        return None
    return {s.model for s in satirlar if s.role_id in kimlikler}


def karar(referanslar: set[str], izinliler: set[str] | None) -> tuple[bool, str]:
    """`(geçer_mi, gerekçe)` — **saf fonksiyon**, DB'siz test edilebilir.

    `context.py` felsefesi: kararı veren şey saf kalsın ki kapı onu tek başına ölçebilsin.
    """
    if izinliler is None:
        return True, "Katman B bu tenant'ta YAPILANDIRILMAMIŞ — Katman A yönetiyor"
    disarida = sorted(referanslar - izinliler)
    if disarida:
        return False, (
            f"allowlist DIŞI model: {disarida} — izinli: {sorted(izinliler) or '(boş)'}")
    return True, "allowlist içinde"
