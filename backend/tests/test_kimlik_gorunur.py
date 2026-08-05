"""FAZ 7.7 (kimlik yarısı) — **`/auth/me` görünür, ve tipi artık YALAN SÖYLEMİYOR.**
[bayraksız: K2'nin erişilebilirlik boyutu]

## Ölçülen iki kusur — biri diğerinden ciddiydi

| # | Kusur | Ölçüm |
|---|---|---|
| 1 | *"`getMe()` tek yerde ve yalnız `permissions` okunuyor"* | ✅ **doğru** — `usePermission` |
| 2 | 🔴 **Tip, telde olmayan bir alanı ZORUNLU ilan ediyordu** | `AuthUser.email: string` ⟷ `MeResponse`'ta `email` **YOK** |

(2) daha ciddidir: TypeScript `me.email`in **var** olduğuna inanıyordu ve çalışma
zamanında `undefined` geliyordu. *Bir tür sistemi, tam da engellemesi gereken şeyi
onaylıyordu.* Bir gün biri `me.email.toLowerCase()` yazsaydı, üretimde patlardı ve
derleyici **hiçbir uyarı vermezdi**.

> 🔴 *Bir tipin telde karşılığı yoksa, o tip bir belge değil bir **yanlış beyandır**.*

## Neden e-posta `login()`'den değil `/auth/me`'den gelir

Frontend `login()`'in döndürdüğü kullanıcıyı zaten **atıyordu** (`await login(...)`).
Atmasaydı bile bir **sayfa yenilemesinden sonra kaybolurdu**: erişim token'ı yalnız
bellekte durur, oturum refresh çerezinden **yeniden** kurulur ve o yolda `login()` hiç
çağrılmaz. *Bir kimliği yalnız giriş anında bilmek, onu bilmemektir.*

⚠ **`Principal`e eklenmedi**: sözleşmesi *"tümü token'dan türetilir"* (ADR-0014 Karar 1)
ve e-postayı token'a koymak, **her istekte taşınan bir PII** demek olurdu.
"""

from __future__ import annotations

import ast
from pathlib import Path

from tests.kapi_ortak import fe_dosyalari, fe_kaynak

_KOK = Path(__file__).resolve().parents[1]


def test_ME_YANITINDA_eposta_VAR():
    """🔴 Alan **şemada** olmalı — bir sunucu alanını yalnız handler'da doldurmak,
    OpenAPI'yi ve istemci tipini bir sonraki tura kadar yanlış bırakır."""
    from app.auth.schemas import MeResponse

    assert "email" in MeResponse.model_fields


def test_EPOSTA_OPSIYONEL_ve_bu_bir_KARAR():
    """⚠ *Bulunamayan bir e-postayı boş dizgeyle doldurmak, "yok" ile "boş" ayrımını
    siler.* Kullanıcı kaydı silinmiş olabilir; `None` bunu **söyler**."""
    from app.auth.schemas import MeResponse

    alan = MeResponse.model_fields["email"]
    assert not alan.is_required(), "🔴 `email` zorunlu — silinmiş bir kayıt 500 üretir"


def test_PRINCIPALE_EKLENMEDI_token_sekli_KORUNDU():
    """🔴 `Principal`in sözleşmesi: *"tümü token'dan türetilir"* (ADR-0014 Karar 1).
    E-postayı oraya koymak, onu **her istekte taşınan bir PII** yapardı."""
    from control_plane.authorize import Principal

    assert not hasattr(Principal, "email") and "email" not in Principal.__annotations__, (
        "🔴 `Principal` e-posta taşıyor — token'a bir PII girdi.")


def test_KIMLIK_OKUMASI_BOZUK_ID_de_500_URETMIYOR():
    """⚠ `User.id` bir **UUID sütunudur**, `principal.user_id` ise token'dan gelen bir
    **dizgedir** — ve token'daki değer geçerli bir UUID olmak **zorunda değildir**.

    🔴 İlk yazım `session.get(User, principal.user_id)` idi ve sürücü katmanında
    `AttributeError: 'str' object has no attribute 'hex'` verdi; **üç mevcut test** bunu
    yakaladı. *Bir kimlik okuması, kötü biçimli bir kimlik yüzünden 500 dönmemeli.*
    """
    src = (_KOK / "app/auth/router.py").read_text(encoding="utf-8")
    agac = ast.parse(src)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "me")
    govde = ast.unparse(fn)
    assert "uuid.UUID(str(principal.user_id))" in govde
    assert "except" in govde, "🔴 bozuk UUID yakalanmıyor"


# --- Frontend: tip yalanı ve render ---------------------------------------------------

def test_getMe_DONUS_TIPI_AuthUser_DEGIL():
    """🔴 *Bir tipin telde karşılığı yoksa, o tip bir belge değil bir yanlış beyandır.*

    `/auth/me` `MeResponse` döndürür: `user_id` (`id` değil) · `branch_ids`
    (`AuthUser`'da yok). İkisini aynı tiple göstermek, **iki farklı sözleşmeyi** tek
    isimle çağırmaktı.
    """
    src = fe_dosyalari()["lib/api-client.ts"]
    assert "export async function getMe(): Promise<Me> {" in src, (
        "🔴 `getMe()` hâlâ `AuthUser` döndürüyor — telde olmayan bir `email` zorunlu "
        "ilan ediliyor ve `me.email.x` derleyiciden GEÇER.")
    assert "export interface Me {" in src
    assert "email: string | null;" in src, "🔴 `Me.email` nullable değil"


def test_KIMLIK_RENDER_EDILIYOR():
    """K2'nin **erişilebilirlik** boyutu: *yalnız kaynakta geçmesi yetmez.*"""
    src = fe_dosyalari()["components/KimlikSeridi.tsx"]
    assert "ben.email" in src, "🔴 e-posta render edilmiyor"
    assert "ben.roles" in src, "🔴 rol render edilmiyor"
    assert "is_superadmin" in src, "🔴 süperadmin hâli render edilmiyor"


def test_SERIT_UYGULAMANIN_HER_YERINDE():
    """Bir kimlik göstergesi tek bir sayfada olursa, diğer sayfalarda **kim olduğun
    bilinmez** — ve çok kiracılı bir üründe bu, yanlış şirket hakkında karar vermektir."""
    src = fe_dosyalari()["app/layout.tsx"]
    assert "<KimlikSeridi />" in src


def test_LOGIN_sayfasinda_SORULMUYOR():
    """⚠ `/login`'de kimlik **yoktur**; sormak 401 üretir ve bu, bir hata gibi görünen
    bir gürültüdür."""
    src = fe_dosyalari()["components/KimlikSeridi.tsx"]
    assert "enabled: !girisSayfasi" in src


def test_SUPERADMIN_hali_SABIT_gorunur():
    """🔴 *Geçici bir yetkiyi görünmez yapmak, onu kalıcı bir yetkiye çevirir.*"""
    src = fe_dosyalari()["components/KimlikSeridi.tsx"]
    i = src.index("is_superadmin")
    assert "title=" in src[i:i + 900], "🔴 süperadmin rozeti ne anlama geldiğini söylemiyor"


def test_ROL_MATRISI_UIya_KOPYALANMADI():
    """CLAUDE.md: *"rol matrisi backend'dedir, UI'a KOPYALANMAZ."* Şerit rolü
    **gösterir**, ondan bir yetki **çıkarmaz**."""
    src = fe_dosyalari()["components/KimlikSeridi.tsx"]
    for yasak in ("owner", "analyst", "viewer"):
        assert f'"{yasak}"' not in src, (
            f"🔴 Rol adı `{yasak}` UI'da bir KARARA bağlanmış — matris kopyalanıyor.")


def test_EPOSTA_YOKSA_HAL_YAZILIYOR():
    """⚠ Boş bir alan *"yüklenmedi"* gibi okunur; oysa burada bilgi **yok**."""
    src = fe_dosyalari()["components/KimlikSeridi.tsx"]
    assert "e-posta kayıtlı değil" in src


def test_KIMLIK_yeni_PANEL_acmadi():
    """K5 tavanı 13/13."""
    from tests.test_panel_sayisi import DESEN

    assert not DESEN.findall(fe_dosyalari()["components/KimlikSeridi.tsx"])


def test_ESKI_TIP_YALANI_geri_gelmedi():
    """⚠ `AuthUser` **duruyor** (login onu döndürüyor ve orada `email` gerçekten var);
    yasak olan `getMe`'nin onu döndürmesiydi."""
    kaynak = fe_kaynak()
    assert "apiClient.get<AuthUser>(\"/auth/me\")" not in kaynak
