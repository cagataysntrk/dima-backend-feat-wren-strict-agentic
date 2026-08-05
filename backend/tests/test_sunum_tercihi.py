"""FAZ E · KALICI SUNUM TERCİHİ — *"bundan sonra hep aylık göster"*.

## Ölçülen kusur (3 Ağustos 2026)

    "hep aylık göster"                     → *"Bu takip mesajını ilişkilendiremedim"*
    "bundan sonra hep tablo olarak göster" → *"«bundan» yerine «unvan» mi demek istedin?"*

Kullanıcı tercihini söylüyor, sistem **anlamıyor bile**; deposu da yoktu.

## Kapsam neden DAR (raporun önerisi AYNEN uygulanmadı)

Rapor genel bir *"Memories"* katmanı öneriyordu. İki yarısından biri bu depoda **zaten
var**: terminoloji (*"biz fire'yi kg konuşuruz"*) `SynonymOverride`'dır. Eksik olan
yalnız **sunum** yarısıydı; genel bir bellek açmak, kaynağı kullanıcının kendi geçmiş
cümlesi olan bir sessiz-yanlış yüzeyi doğururdu.

## Üç değişmez bu süitte kilitlenir

1. Tercih **ölçü/cube seçimine karışmaz**.
2. Tercih **sessiz uygulanmaz** ve **açık isteği ezmez**.
3. Tercih **yazmak bir yazmadır** → Faz H'nin onay kademesinden geçer (muafiyet yok).
"""

from __future__ import annotations

import pytest

from app import eylem, tercih
from tests.conftest import ask


@pytest.fixture(autouse=True)
def _temiz(client):
    """Her test kendi tercihiyle başlar — depoda kalıntı bırakmaz."""
    for a in tercih.ANAHTARLAR:
        client.delete(f"/tercihler/{a}")
    yield
    for a in tercih.ANAHTARLAR:
        client.delete(f"/tercihler/{a}")


def _onayla(client, d) -> dict:
    oneri = d["eylem_onerisi"]
    r = client.post("/ask/eylem", json={"eylem": oneri["eylem"],
                                        "argumanlar": oneri["argumanlar"],
                                        "bilet": oneri.get("bilet", "")})
    assert r.status_code == 200, r.text
    return r.json()


# --- 1) TESPİT: kapı İKİ KANATLI ----------------------------------------------------

@pytest.mark.parametrize("q,anahtar,deger", [
    ("bundan sonra hep aylık göster", "granularity", "month"),
    ("hep haftalık göster", "granularity", "week"),
    ("raporları her zaman yıllık ver", "granularity", "year"),
    ("bundan sonra hep tablo olarak göster", "view", "table"),
])
def test_KALICI_TERCIH_TANINIR(client, q, anahtar, deger):
    d = ask(client, q)
    oneri = d.get("eylem_onerisi")
    assert oneri, f"tercih tanınmadı: {q!r} → not={d.get('note')!r}"
    assert oneri["eylem"] == eylem.TERCIH_KAYDET
    assert oneri["argumanlar"]["anahtar"] == anahtar
    assert oneri["argumanlar"]["deger"] == deger
    assert not d.get("sql"), "tercih cümlesi SQL üretti"


@pytest.mark.parametrize("q", [
    "aylık göster",                 # hedef VAR, kalıcılık işareti YOK → tek turluk istek
    "bu yıl aylık oee",             # aynı sınıf
    "hep en yüksek fireyi ver",     # kalıcılık işareti VAR, sunum hedefi YOK
    "her zaman çalışan makineler",  # aynı sınıf
])
def test_TEK_KANAT_YETMEZ(client, q):
    """Yalnız işaret aransaydı *"hep en yüksek fire"* tercih sanılırdı; yalnız hedef
    aransaydı **her** aylık soru bir tercihe dönüşürdü."""
    assert tercih.tespit(q.replace("ı", "i"), gorunum=None) is None or "hep" not in q
    d = ask(client, q)
    assert (d.get("eylem_onerisi") or {}).get("eylem") != eylem.TERCIH_KAYDET, \
        f"meşru istek kalıcı tercih sanıldı: {q!r}"


# --- 2) ONAYSIZ YAZMA YOK (Faz H değişmezi, muafiyet açılmadı) ---------------------

def test_ONAYSIZ_YAZILMAZ(client):
    ask(client, "bundan sonra hep aylık göster")
    assert client.get("/tercihler").json()["tercihler"] == [], \
        "tercih ONAY OLMADAN yazıldı — Faz H değişmezi çiğnendi"


def test_TERCIH_YAZMA_UCU_YOK():
    """`POST /tercihler` OLMAMALI: yazma tek kapıdan (onay) geçmeli. İkinci bir yazma
    yolu, bir faz önce kurulan kademeyi sessizce atlatırdı."""
    from app.routers import tercihler as r

    yollar = {(list(x.methods)[0], x.path) for x in r.router.routes}
    assert ("POST", "/tercihler") not in yollar, yollar
    assert ("GET", "/tercihler") in yollar and ("DELETE", "/tercihler/{anahtar}") in yollar


def test_ONAY_YAZAR_ve_LISTELENIR(client):
    d = ask(client, "bundan sonra hep aylık göster")
    _onayla(client, d)
    kayitlar = client.get("/tercihler").json()["tercihler"]
    assert [(k["anahtar"], k["deger"]) for k in kayitlar] == [("granularity", "month")]
    assert kayitlar[0]["etiket"] == "aylık"
    assert kayitlar[0]["kaynak_ifade"] == "bundan sonra hep aylık göster", \
        "tercihi doğuran cümle saklanmadı — kullanıcı 'bunu ne zaman söylemişim?' diyemez"


def test_BILINMEYEN_ANAHTAR_REDDEDILIR(client):
    r = client.post("/ask/eylem", json={
        "eylem": eylem.TERCIH_KAYDET,
        "argumanlar": {"anahtar": "cube", "deger": "oee"}})
    assert r.status_code == 400, r.text


def test_SILME_IDEMPOTENT(client):
    d = ask(client, "bundan sonra hep aylık göster")
    _onayla(client, d)
    assert client.delete("/tercihler/granularity").status_code == 200
    assert client.delete("/tercihler/granularity").status_code == 200  # ikinci kez
    assert client.get("/tercihler").json()["tercihler"] == []


# --- 3) UYGULAMA: sesli, açık isteği ezmez, ölçüye karışmaz ------------------------

def test_TERCIH_UYGULANIR_ve_SOYLENIR(client):
    d = ask(client, "bundan sonra hep aylık göster")
    _onayla(client, d)
    r = ask(client, "bu yıl oee")
    td = (r.get("cube_query") or {}).get("timeDimensions") or []
    assert td and td[0]["granularity"] == "month", r.get("cube_query")
    assert "tercihiniz uygulandı" in (r.get("note") or ""), \
        f"tercih SESSİZ uygulandı (not={r.get('note')!r})"


def test_ACIK_ISTEK_TERCIHI_EZER(client):
    """Tercihin, kullanıcının O TURDA yazdığını ezmesi, geçmiş cümlesini bugünküne
    tercih etmek olurdu."""
    d = ask(client, "bundan sonra hep aylık göster")
    _onayla(client, d)
    r = ask(client, "bu yıl haftalık oee")
    td = (r.get("cube_query") or {}).get("timeDimensions") or []
    assert td and td[0]["granularity"] == "week", r.get("cube_query")


def test_TERCIH_OLCU_VE_CUBE_SECIMINE_KARISMAZ(client):
    d = ask(client, "bundan sonra hep aylık göster")
    _onayla(client, d)
    tercihli = ask(client, "bu yıl oee")
    client.delete("/tercihler/granularity")
    tercihsiz = ask(client, "bu yıl oee")
    for alan in ("cube", "measures", "dimensions", "filters"):
        assert (tercihli.get("cube_query") or {}).get(alan) == \
               (tercihsiz.get("cube_query") or {}).get(alan), \
            f"tercih `{alan}` alanına karıştı — SUNUM dışına çıktı"


def test_TERCIHSIZ_DAVRANIS_BIREBIR_AYNI(client):
    """KURAL B: tercih yokken bugünkü davranış değişmez."""
    r = ask(client, "bu yıl oee")
    assert not (r.get("cube_query") or {}).get("timeDimensions")
    assert "tercihiniz" not in (r.get("note") or "")


def test_TAKIPTE_UYGULANMAZ(client):
    """Takipte kullanıcı var olan bir raporu YÖNLENDİRİYORDUR; aylar önce söylenmiş bir
    tercihin o canlı konuşmayla çekişmesi doğru olmaz."""
    d = ask(client, "bundan sonra hep aylık göster")
    _onayla(client, d)
    taban = ask(client, "bu yıl makine bazında oee")   # taze → tercih uygulanır
    devam = ask(client, "hat bazında", cube_query={
        **(taban.get("cube_query") or {}), "timeDimensions": []})
    assert not (devam.get("cube_query") or {}).get("timeDimensions"), devam.get("cube_query")


# --- 4) FRONTEND TÜKETİCİSİ (yetim alan kapısı) ------------------------------------

def test_FRONTEND_TUKETICISI_var():
    import pathlib

    fe = pathlib.Path(__file__).resolve().parents[2] / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend kaynağı mount edilmemiş")
    metin = "\n".join(f.read_text(encoding="utf-8", errors="ignore")
                      for f in fe.rglob("*.ts*"))
    assert "/tercihler" in metin, "tercih ucu frontend'den HİÇ çağrılmıyor"
    assert "TercihlerPanel" in metin, "kullanıcı tercihlerini GÖREMİYOR"
    assert "silTercih" in metin, "kullanıcı tercihini KALDIRAMIYOR"
