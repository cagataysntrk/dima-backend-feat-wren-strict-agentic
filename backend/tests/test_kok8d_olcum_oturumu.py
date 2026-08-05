"""🔴 KÖK-8d — **ölçüm oturumu ürünün token ömrünü aşmasın.** (denetim raporu KN-4)

Ölçülen: `access_ttl_seconds = 15 * 60`; süit tek süreçte **19:15** koşuyor → 15.
dakikadan sonraki **90 test** `401` alıp **KIRMIZI** raporlanıyordu. Aynı testler
`-n 8` ile 6 dakikada koşunca **0 hata**.

🔴 Tehlikesi hatanın kendisi değil, **yanlış okunması**: rapor 112 hata gösterdi,
gerçek 22'ydi. *Bir kapı, ölçemediği şeyi "başarısız" diye raporlarsa, ölçüm aracının
kendisi bir kusur kaynağıdır.*
"""

from __future__ import annotations

from tests.conftest import ask


def test_SURESI_DOLMUS_TOKEN_OLCUMU_DURDURMUYOR(client):
    """🔴 **ASIL KAPI.** Token geçersizleşince istemci **tek uçuşta yeniler ve tekrarlar**
    — ürünün kendi `api-client.ts` deseninin aynısı.

    ⚠ Gerçek süre aşımını beklemek 15 dakika sürerdi; bozuk bir token **aynı 401'i**
    üretir ve kapı saniyeler içinde koşar. *Bir mekanizmayı sınamak için sebebini değil,
    belirtisini üretmek yeter — yeter ki belirti birebir aynı olsun.*"""
    client.headers["Authorization"] = "Bearer bozuk.token.degeri"
    d = ask(client, "bu yıl makine bazında oee")     # ask() 200 bekler → 401 olsa patlar
    assert (d.get("result") or {}).get("row_count", 0) > 0, "ölçüm yenilemeden sonra boş"


def test_YENILEME_AUTH_UCLARINI_DONGUYE_SOKMUYOR(client):
    """⚠ `/auth/login` 401 verirse yeniden login denemek **sonsuz döngü** olurdu."""
    r = client.post("/auth/login", json={"email": "yok@yok", "password": "yanlis"})
    assert r.status_code in (400, 401, 422)


def test_URUN_TOKEN_OMRU_BEYANI_DURUYOR():
    """⊡ Kapının dayandığı sayı **kaynakta** — bayatlarsa kapı da yeniden ölçülmeli."""
    from control_plane.config import get_auth_settings

    ttl = getattr(get_auth_settings(), "access_ttl_seconds", None)
    assert ttl and ttl <= 60 * 60, f"token ömrü beklenmedik: {ttl}"
