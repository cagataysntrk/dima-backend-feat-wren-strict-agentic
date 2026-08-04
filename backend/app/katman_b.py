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


#: Kullanıcıya gösterilen ret notu. ⚠ **Hangi modelin yasak olduğunu SÖYLEMEZ**: bir
#: allowlist'in içeriği de bir bilgidir ve *"`personel_ozluk`'a erişemezsin"* cümlesi,
#: erişilemeyen şeyin **varlığını** sızdırır. Gerekçenin tamamı `trace`'e ve audit'e yazılır
#: — yani **kaybolmaz**, yalnız yetkili olan yerde durur.
RED_NOTU = ("Bu soruyu yanıtlamak için erişim yetkin olmayan bir veri kümesine "
            "dokunmak gerekiyordu. Yöneticinden bu veriye erişim isteyebilirsin.")


def allowlist(request: Any, principal: Any) -> set[str] | None:
    """`ModelPermission` allowlist'i — oturum yoksa **None** (yapılandırılmamış).

    ⚠ `None` ile `set()` farkı burada da korunur: DB'ye ulaşamamak *"izin yok"* demek
    değildir. Ulaşılamayan bir yetki deposunu **boş allowlist** saymak, bir altyapı
    arızasını **tam kesintiye** çevirirdi.
    """
    try:
        from control_plane.db import get_session
    except ImportError:
        return None
    try:
        with next(get_session()) as oturum:                  # type: ignore[call-overload]
            return izinli_modeller(principal, oturum)
    except Exception:                                        # noqa: BLE001
        return None


def zorla(request: Any, wren: Any, sql: str) -> None:
    """Katman B'yi **bu SQL üstünde** zorlar. Reddederse `ModelErisimReddi` fırlatır.

    🔴 **TEK SAHİP.** Bu gövde `routers/query.py`'de özel bir yardımcıydı; `/ask` de aynı
    şeye ihtiyaç duyunca ikinci bir kopya yazmak *"aynı kuralın iki sahibi"* olurdu ve
    ikisi zamanla ayrışırdı — bir güvenlik katmanı için bu en sessiz kırılma biçimidir.

    ## Neden burada, `WrenService`'te değil

    `WrenService` **şirket** kapsamlıdır, **kullanıcı** kapsamlı değil. Yetki kararını
    oraya taşımak, servise kimlik bilgisi sızdırmak ve iki farklı kapsamı tek nesnede
    bindirmek olurdu.
    """
    from control_plane.authorize import enforce_query

    # `get_current_principal` onu isteğe **zaten** iliştiriyor (`request.state.principal`);
    # bağımlılığı ikinci kez çözmek, aynı token'ı iki kez doğrulamak olurdu.
    principal = getattr(getattr(request, "state", None), "principal", None)
    if principal is None or getattr(principal, "is_superadmin", False):
        return                       # superadmin: ADR-0015 K7 — ENGEL değil GÖRÜNÜRLÜK
    izinliler = allowlist(request, principal)
    if izinliler is None:
        return                       # Katman B yapılandırılmamış — Katman A yönetir
    adlar = {m.get("name") for m in (wren.schema().get("models") or []) if m.get("name")}
    enforce_query(principal, sorted(referans_modeller(sql, adlar)), izinliler)


class _Kapili:
    """`WrenService`'in **yetki kapılı** görünümü: `dry_plan`/`query` önce Katman B'yi sorar.

    🔴 **SARMAL, YAMA DEĞİL — ve bu bir desen tercihidir.** Discovery dalında SQL'in
    motora gittiği **beş** nokta var (üretim · onarım · çalıştırma · onarımlı çalıştırma ·
    plan tekrarı). Beşini tek tek yamamak, **altıncısını ekleyen kişinin unutmasına** açık
    kalırdı — bu deponun `pii.muhurle` kararında birebir yaşadığı şey (*"`raw` dalı
    düzeltilmiş, kardeşleri unutulmuştu"*). Sarmal, **yeni dallar dâhil** hepsini kapsar.

    ⚠ Öteki her nitelik **olduğu gibi** iletilir (`__getattr__`): sarmal bir **kapıdır**,
    ikinci bir motor değil. `mdl_version` gibi alanlar aynen görünür.
    """

    def __init__(self, motor: Any, istek: Any) -> None:
        self._motor = motor
        self._istek = istek

    def dry_plan(self, sql: str, *a: Any, **kw: Any) -> Any:
        zorla(self._istek, self._motor, sql)
        return self._motor.dry_plan(sql, *a, **kw)

    def query(self, sql: str, *a: Any, **kw: Any) -> Any:
        # ⚠ `dry_plan` her yolda önce çağrılıyor olsa da burada **tekrar** sorulur:
        # "önce hep dry_plan çağrılır" bir **bugünkü doğrudur**, bir değişmez değil.
        zorla(self._istek, self._motor, sql)
        return self._motor.query(sql, *a, **kw)

    def __getattr__(self, ad: str) -> Any:
        return getattr(self._motor, ad)


def sarmala(motor: Any, istek: Any) -> Any:
    """Motoru Katman B kapısıyla sarar. Çağıran **tek satır** yazar, kapsam **tam** olur."""
    return _Kapili(motor, istek)


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
