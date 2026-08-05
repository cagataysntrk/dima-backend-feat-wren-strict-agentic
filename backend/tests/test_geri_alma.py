"""**SİLMEYİ GERİ AL — soft-delete'in kullanıcıya ulaşan yarısı.** *(denetim F2)*

## 🔴 Ölçülen kusur

Sunucu beş nesneyi **silmiyor, damgalıyor** (`deleted_at`); kayıt **duruyor**. Ama
arayüzde — ve **hiçbir uçta** — silinmiş bir şeyi geri getiren tek bir yol yoktu
(`grep -rn "restore\\|geri_al\\|undelete"` → **0**).

> 🔴 *Kullanıcı açısından soft-delete ile hard-delete **birebir aynı deneyimdi**.*
> ADR-0019'un bedeli ödenmiş güvenlik ağı kimseye ulaşmıyordu —
> **geri alınamayan bir soft-delete, pahalı bir hard-delete'tir.**

Zincir tamamlandı: **onay (F1) ✅ → hata bildirimi (F3) ✅ → geri alma (F2) ✅**.

## Kapsam — ve kalanın gerekçesi

| nesne | geri alma | gerekçe |
|---|---|---|
| sohbet | ✅ | en sık silinen |
| **pano** | ✅ | kullanıcının **gözünün önünde** kaybolan iş |
| **widget** | ✅ | aynı |
| bağlantı | ⊘ | silme **admin** işidir ve sihirbazdan yeniden kurulur; ⚠ şifreli sır **duruyor** — kurtarma DB'den mümkün |
| sunum/bildirim tercihi | ⊘ | tek tıkla **yeniden kurulur**; bir geri-al şeridi, kazancından çok gürültü olurdu |

> ⚠ *Bir zinciri bir nesnede kurup "kapandı" demek, kalanları gizler.* Kalan ikisi
> **gizlenmiyor**: gerekçeleri yukarıda ve ikisi de **kayıp değil, yeniden kurulabilir**.
"""

from __future__ import annotations

import ast
from pathlib import Path

from tests.kapi_ortak import fe_dosyalari

_KOK = Path(__file__).resolve().parents[1]


def test_UC_VAR():
    """🔴 Ölçüldü: hiçbir geri-alma ucu yoktu."""
    src = (_KOK / "app/routers/conversations.py").read_text(encoding="utf-8")
    assert '@router.post("/{cid}/geri-al"' in src


def test_AYRI_UC_PATCH_degil():
    """⚠ `PATCH` bir **alan güncellemesidir**; `deleted_at`'i oraya açmak silinmiş bir
    kaydı **kazara** dirilten bir yol bırakırdı. Geri alma bir **niyettir** ve niyeti
    kendi ucunda tutmak onu denetlenebilir de yapar."""
    src = (_KOK / "app/routers/conversations.py").read_text(encoding="utf-8")
    agac = ast.parse(src)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "geri_al_conversation")
    assert "audit.record" in ast.unparse(fn)


def test_OWNED_KULLANILMIYOR_ve_SEBEBI_yazili():
    """🔴 `_owned` silinmiş kaydı **404** sayar — yani tam da geri almak istediğimiz
    durumu **görünmez** yapardı. Sahiplik elle doğrulanır."""
    src = (_KOK / "app/routers/conversations.py").read_text(encoding="utf-8")
    agac = ast.parse(src)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "geri_al_conversation")
    govde = ast.unparse(fn)
    assert "_owned(" not in govde, "🔴 `_owned` kullanılmış — silinmiş kayıt 404 olur"
    assert "c.user_id != uid" in govde, "🔴 sahiplik doğrulanmıyor"


def test_BASKASININ_SOHBETI_404():
    """⚠ Varlık sızdırmaz: *"bu id var ama senin değil"* demek, bir kaydın varlığını
    söylemektir."""
    src = (_KOK / "app/routers/conversations.py").read_text(encoding="utf-8")
    i = src.index("def geri_al_conversation")
    assert "status_code=404" in src[i:i + 2600]


def test_IKINCI_GERI_ALMA_HATA_DEGIL():
    """⚠ *Bir düzeltmenin ikinci kez uygulanması, bir hata değildir.* Kullanıcı iki kez
    geri-al'a bastığında hata görmemeli."""
    src = (_KOK / "app/routers/conversations.py").read_text(encoding="utf-8")
    agac = ast.parse(src)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "geri_al_conversation")
    govde = ast.unparse(fn)
    assert "if c.deleted_at is not None:" in govde, "🔴 no-op dalı yok"


def test_SURE_SINIRI_YOK_ve_SEBEBI_yazili():
    """🔴 Kayıt durduğu sürece geri alınabilir. Bir süre sınırı, kullanıcıya *"beş
    saniyede karar ver"* demekti — oysa asıl güvence kaydın **durmasıdır**."""
    src = (_KOK / "app/routers/conversations.py").read_text(encoding="utf-8")
    i = src.index("def geri_al_conversation")
    blok = src[i:i + 2600]
    assert "süre sınırı YOK" in blok


# --- Arayüz ---------------------------------------------------------------------------

def test_SERIT_VAR_ve_TUKETICISI_var():
    """K2: yeni bir uç **frontend tüketicisi olmadan** eklenemez."""
    assert "restoreConversation" in fe_dosyalari()["lib/api-client.ts"]
    assert "<GeriAlSeridi" in fe_dosyalari()["components/HistoryPanel.tsx"]


def test_SILINENIN_ADI_yaziliyor():
    """🔴 *"Silindi"* tek başına **neyin** silindiğini söylemez ve kullanıcı geri alıp
    almayacağına karar veremez."""
    src = fe_dosyalari()["components/GeriAlSeridi.tsx"]
    assert "{etiket}" in src and "silindi" in src


def test_AD_SILMEDEN_ONCE_yakalaniyor():
    """⚠ Silindikten sonra liste tazelenir ve satır kaybolur — o an adı sormanın yeri
    kalmaz."""
    src = fe_dosyalari()["components/HistoryPanel.tsx"]
    i = src.index("setSilinen({ id: c.id")
    j = src.index("del.mutate(c.id)")
    assert i < j, "🔴 ad silmeden SONRA yakalanıyor — o anda satır yok"


def test_SILME_BASARISIZSA_SERIT_YOK():
    """🔴 *Olmayan bir silmeyi geri almayı teklif etmek, kullanıcıya yanlış bir dünya
    tarif eder.*"""
    src = fe_dosyalari()["components/HistoryPanel.tsx"]
    i = src.index('hataMetni(e, "Sohbet silme")')
    assert "setSilinen(null)" in src[i - 400:i + 200]


def test_SERIT_ROLE_STATUS_alert_DEGIL():
    """⚠ Bu bir **hata değil**, kullanıcının kendi yaptığı bir işin bildirimi. Alarma
    çevirmek, her silmeyi bir olaya dönüştürürdü."""
    src = fe_dosyalari()["components/GeriAlSeridi.tsx"]
    assert 'role="status"' in src and 'role="alert"' not in src


def test_SERIT_OMRU_YETENEGI_SINIRLAMIYOR():
    """🔴 *Bir kolaylığın süresi, bir garantinin süresi değildir.* Şerit 8 sn durur;
    sunucuda süre sınırı **yoktur**."""
    src = fe_dosyalari()["components/GeriAlSeridi.tsx"]
    assert "OMUR_MS = 8000" in src
    from tests.kapi_ortak import frontend_dir
    ham = (frontend_dir() / "components/GeriAlSeridi.tsx").read_text(encoding="utf-8")
    assert "YETENEK kaybolmaz" in ham


def test_ZAMANLAYICI_yeni_silmede_SIFIRLANIYOR():
    """⚠ Art arda iki silmede ilk sayaç ikincisinin şeridini **erken kapatırdı**."""
    src = fe_dosyalari()["components/GeriAlSeridi.tsx"]
    assert "clearTimeout(zamanlayici.current)" in src


def test_SERIT_yeni_PANEL_acmadi():
    from tests.test_panel_sayisi import DESEN

    assert not DESEN.findall(fe_dosyalari()["components/GeriAlSeridi.tsx"])


def test_KAPSAM_ve_GEREKCELERI_yazili():
    """⊘ *Bir zinciri bir nesnede kurup "kapandı" demek, kalanları gizler.* Kalan iki
    nesnenin (bağlantı · tercih) **gerekçesi** belgede — ve ikisi de **kayıp değil,
    yeniden kurulabilir**."""
    doc = __doc__ or ""
    assert "yeniden kurulabilir" in doc and "gizlenmiyor" in doc

# --- Pano ve widget (aynı desen, ayrı sahiplik kapıları) -----------------------------

def test_PANO_ve_WIDGET_geri_alinabiliyor():
    """🔴 İkisi de kullanıcının **gözünün önünde** kaybolur — sohbetten daha görünür
    bir kayıp."""
    src = (_KOK / "app/routers/dashboards.py").read_text(encoding="utf-8")
    assert '@router.post("/dashboards/{did}/geri-al")' in src
    assert '@router.post("/dashboards/{did}/widgets/{wid}/geri-al")' in src


def test_PANO_GERI_ALMA_yalniz_SAHIBI():
    """⚠ `tenant` görünürlüğü **salt-okunurdur**: başkasının panosunu geri almak, silme
    kararını sahibinden almak olurdu.

    🔴 Ve alan adı **okunarak** doğrulandı: `Dashboard.user_id` — ilk yazımda `owner_id`
    varsaymıştım ve **öyle bir alan yok**. *Bir alan adını okumadan yazmak, bu turda
    üçüncü kez aynı kusuru üretti.*
    """
    from control_plane.models import Dashboard

    assert "user_id" in Dashboard.model_fields and "owner_id" not in Dashboard.model_fields
    src = (_KOK / "app/routers/dashboards.py").read_text(encoding="utf-8")
    i = src.index("def geri_al_dashboard")
    assert "d.user_id != p.user_id" in src[i:i + 1600]


def test_GET_OWNED_kullanilmiyor_PANODA():
    """🔴 `_get_owned` silinmiş panoyu **404** sayar — tam da geri almak istediğimiz
    durumu görünmez yapardı."""
    src = (_KOK / "app/routers/dashboards.py").read_text(encoding="utf-8")
    i = src.index("def geri_al_dashboard")
    govde = src[i:i + 1600]
    assert "_get_owned(" not in govde


def test_WIDGET_GERI_ALMA_PANO_SAHIPLIGINI_dogruluyor():
    """⚠ Widget'ı geri almak için **panosunun durması** gerekir — bu yüzden pano tarafında
    `_get_owned` doğru araçtır."""
    src = (_KOK / "app/routers/dashboards.py").read_text(encoding="utf-8")
    i = src.index("def geri_al_widget")
    assert "_get_owned(session, did, p, write=True)" in src[i:i + 900]


def test_UC_TUKETICISI_var():
    """K2: uç, tüketicisi olmadan **bitmiş sayılmaz**."""
    assert "restoreDashboard" in fe_dosyalari()["components/DashboardsPanel.tsx"]
    assert "restoreDashboardWidget" in fe_dosyalari()["components/DashboardView.tsx"]
    assert "<GeriAlSeridi" in fe_dosyalari()["components/DashboardsPanel.tsx"]
    assert "<GeriAlSeridi" in fe_dosyalari()["components/DashboardView.tsx"]


def test_SILME_BASARISIZSA_SERIT_YOK_panoda():
    src = fe_dosyalari()["components/DashboardsPanel.tsx"]
    i = src.index('hataMetni(e, "Pano silme")')
    assert "setSilinen(null)" in src[i - 400:i + 200]
