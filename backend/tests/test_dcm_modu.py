"""FAZ 7.11 kapısı — **DCM: Deterministik Cevap Modu.** [bayrak: `ui_dcm_modu`]

Yol haritasının kapısı birebir: *"`AI_MODE=off` iken **3 tıkta** cevaba ulaşılıyor;
serbest metin kutusu **yok**."*

## 🔴 Metin kutusunu gizlemek bir garanti değildir

Bu maddenin en kolay yanlış uygulaması `<textarea>`'yı `hidden` yapıp işi bitmiş
saymaktır. O bir **görünüm kararıdır**: kullanıcı (ya da bir betik) uca doğrudan serbest
metin gönderebilir ve akış LLM'e düşer.

**Garantiyi akışın kendisi verir**: `POST /cube` bir `cube_query`'yi **LLM'siz** koşar —
serbest metin diye bir şey **hiç oluşmaz**, gizlenmez. Kapı bu yüzden *"`<textarea>` var
mı"* diye değil, *"`ask()` çağrılıyor mu"* diye sorar.

## ⚠ "Altın rozet" maddesi bilinçle UYGULANMADI — ve çatışma gizlenmiyor

Yol haritası *"tüm sonuçlar **altın rozet**"* diyor. FAZ 7.8/K2 tam da onu **kaldırdı**
(`🥇` + `Yüksek güven (100%)` = kalibre edilmemiş bir yol etiketi; MIMARI §9:
*"güven değil bir SÜS"*).

> 🔴 **İki madde çatışıyorsa mimari kural kazanır.** Ve DCM'in vaadi zaten `◆ CUBE`
> rozetinde **ölçülmüş** olarak duruyor. *Bir garantiyi ikinci kez, kalibre edilmemiş
> bir sayıyla söylemek onu güçlendirmez — zayıflatır.*

## Neden varsayılan `off`

DCM bir **kısıtlamadır**. İstemeden açılırsa kullanıcı ürünü **bozuk sanar**
(*"neden yazamıyorum?"*) — ve bu, bir bayrağın verebileceği en pahalı yanlış izlenimdir.
"""

from __future__ import annotations

import re

import pytest

from tests.kapi_ortak import fe_dosyalari, fe_kaynak

_DCM = "components/DcmAkisi.tsx"


def test_UC_TIKTA_cevap():
    """🔴 Kapının sayısal şartı. Üç adım: **ölçü → analiz → dönem**, ve üçüncü seçim
    **doğrudan koşar**.

    ⚠ Ayrı bir *"çalıştır"* düğmesi kapıyı **dört tığa** çıkarır ve hiçbir bilgi
    eklemezdi: üçüncü seçimden sonra sorunun tanımı **tamamlanmıştır**.
    """
    src = fe_dosyalari()[_DCM]
    assert src.count("<Adim") == 3, "🔴 adım sayısı üç değil"
    # Üçüncü adımın seçeneği doğrudan `calistir` çağırır.
    ucuncu = src[src.index('baslik="dönem"'):]
    assert "onClick={() => calistir(d.id)}" in ucuncu, (
        "🔴 Üçüncü seçim doğrudan koşmuyor — dördüncü bir tık gerekiyor.")
    # ⚠ Kelime değil **düğme** aranır: ilk sürüm `"çalıştır" not in src` yazdı ve hata
    # mesajındaki *"Sorgu çalıştırılamadı"* cümlesini yakaladı. *Bir yasağı kelime
    # düzeyinde yazmak, onu cümlelere de uygular.*
    dugmeler = re.findall(r">\s*(çalıştır|Çalıştır|çalistir)\s*<", src)
    assert not dugmeler, "🔴 Ayrı bir «çalıştır» düğmesi var — kapı dört tık."


def test_SERBEST_METIN_kutusu_YOK():
    """DCM akışında bir metin girişi **hiç yok**."""
    src = fe_dosyalari()[_DCM]
    for etiket in ("<textarea", "<input"):
        assert etiket not in src, f"🔴 DCM akışında `{etiket}` var — serbest metin yolu"


def test_GARANTI_SUNUCUDA_ask_CAGRILMIYOR():
    """🔴 **Asıl kapı budur.** Gizlemek değil, **hiç kurmamak**: akış `askCube`
    (`POST /cube`, LLM'siz) kullanır ve `ask()`'e **hiç** dokunmaz."""
    src = fe_dosyalari()[_DCM]
    assert "askCube" in src, "🔴 deterministik uç kullanılmıyor"
    assert not re.search(r"\bask\(", src), (
        "🔴 DCM akışı `ask()` çağırıyor — o yol LLM'e düşebilir ve mod bir GÖRÜNÜM "
        "kararına iner.")


def test_CUBE_QUERY_istemcide_kuruluyor_CUMLE_hic_olusmuyor():
    """⚠ *Çözülecek bir cümle yoksa, yanlış çözülecek bir cümle de yoktur.*"""
    src = fe_dosyalari()[_DCM]
    assert "const cq: CubeQuery = { cube: olcu.cube, measures: [olcu.measure] };" in src


def test_SECENEK_KUMESI_kapali():
    """⚠ Serbest metin kabul etmeyen bir modda **seçenek kümesi de kapalı** olmalı:
    bir *"diğer…"* maddesi, serbest metni **arka kapıdan** geri getirirdi."""
    src = fe_dosyalari()[_DCM]
    assert "as const;" in src
    assert "diğer" not in src.lower()


def test_MUMKUN_OLMAYAN_analiz_SESSIZCE_DEJENERE_olmuyor():
    """🔴 Boyutu olmayan bir cube'da *"kırılım"* seçilebilseydi sonuç **tek toplam**
    dönerdi — ve kullanıcı ona *"kırılım budur"* derdi. Sessiz bir dejenerasyon, açık
    bir hatadan **daha pahalıdır**.

    ⚠ İki kapı var: seçenek `disabled` **ve** `calistir` içinde ikinci bir savunma.
    """
    src = fe_dosyalari()[_DCM]
    assert "kirilimMumkun" in src and "trendMumkun" in src
    assert "if (boyut)" in src, "🔴 çalıştırma yolunda ikinci savunma yok"


def test_ROZET_HER_ekranda_sabit():
    """*Bir mod, ancak açık olduğu **görülüyorsa** bir moddur*; sessiz bir kısıtlama
    kullanıcıya ürünü **bozuk** gösterir."""
    src = fe_dosyalari()[_DCM]
    assert "DCM Aktif" in src
    assert "title=" in src[src.index("DCM Aktif") - 400:src.index("DCM Aktif")], (
        "🔴 Rozet ne anlama geldiğini SÖYLEMİYOR — bir rozet, açıklamasız bir sırdır.")


def test_ALTIN_ROZET_uygulanMADI_ve_GEREKCE_yazili():
    """🔴 Bir maddeyi uygulamamak bir **karardır** ve kararın yeri koddur, sohbet değil.

    FAZ 7.8/K2 madalyayı kaldırdı; DCM'in *"altın rozet"* maddesi onu geri getirirdi.
    *İki madde çatışıyorsa mimari kural kazanır — ve çatışma gizlenmez.*
    """
    # 🔴 Gerekçe bir **yorumdur** ve `fe_dosyalari()` yorumları AYIKLAR — bu kapı ham
    # dosyayı okumak zorunda. *Ölçüm aracının varsayılanı, ölçülecek şeye göre seçilir:*
    # koda bakan taramalar yorumsuz, **belgeye** bakanlar ham okur.
    from tests.kapi_ortak import frontend_dir

    ham = (frontend_dir() / "components/DcmAkisi.tsx").read_text(encoding="utf-8")
    assert "K2" in ham and "MIMARI §9" in ham, (
        "🔴 Uygulanmayan maddenin gerekçesi kodda yazılı değil — bir gün biri onu "
        "«unutulmuş» sanıp geri ekler.")
    # Ve gerçekten eklenmemiş olmalı — bu yarısı **yorumsuz** kaynakta, çünkü gerekçe
    # metni madalyaları ANLATIYOR ve ham tarama kendi belgesini yakalardı.
    for madalya in ("🥇", "🥈", "🥉"):
        assert madalya not in fe_dosyalari()[_DCM]


def test_SONUC_var_olan_gecmise_yaziliyor():
    """⚠ DCM ayrı bir sonuç yolu **açmaz**: ikinci bir depo, aynı cevabın iki farklı
    geçmişte yaşaması demek olurdu ve kullanıcı hangisinin doğru olduğunu bilemezdi."""
    src = fe_dosyalari()["app/page.tsx"]
    assert "addHistory(r);" in src


def test_BAYRAK_kayitli_ve_VARSAYILAN_kapali():
    """🔴 Varsayılan `off` bir **karar**: DCM bir kısıtlamadır ve istemeden açılırsa
    kullanıcı ürünü bozuk sanar."""
    from pathlib import Path

    import yaml

    from app.features import FLAG_REGISTRY

    assert "ui_dcm_modu" in FLAG_REGISTRY
    d = yaml.safe_load((Path(__file__).resolve().parents[1] / "demo/packs/features.yml")
                       .read_text(encoding="utf-8"))
    assert ((d or {}).get("features") or {}).get("ui_dcm_modu") == "off", (
        "🔴 DCM varsayılan olarak AÇIK — bir kısıtlama sessizce açılamaz.")


def test_BAYRAK_UI_da_okunuyor_ve_AKISI_KESIYOR():
    """*Kill-switch yalnız kayıtta varsa yarımdır.* Ve bayrak açıkken sohbet yüzeyine
    **hiç girilmemeli** — yanına eklenmemeli."""
    src = fe_dosyalari()["app/page.tsx"]
    assert 'useFeature("ui_dcm_modu")' in src
    assert "{dcmModu ? (" in src, (
        "🔴 DCM sohbet akışını KESMİYOR, yanına ekleniyor — serbest metin yolu açık kalır.")


def test_GORELI_DONEM_istemcide_HESAPLANMIYOR():
    """⚠ *"Bu yıl"* gibi göreli bir ifadenin çözümü bir **tarih hesabıdır** ve sahibi
    backend'dir (`cube_router`). İki sahip, iki farklı *"bu yıl"* demektir."""
    src = fe_dosyalari()[_DCM]
    assert "new Date(" not in src, "🔴 İstemci tarih hesaplıyor — ikinci bir dönem sahibi"


@pytest.mark.parametrize("gran", ["month", "quarter", "year"])
def test_DONEM_secenekleri_CUBE_granularity_degerleri(gran):
    """Seçenekler uydurma etiketler değil, motorun **anladığı** değerler olmalı."""
    assert f'id: "{gran}"' in fe_dosyalari()[_DCM]


def test_HATA_gizlenmiyor():
    """⚠ DCM'in vaadi **görünürlüktür**; sessizce boş dönen bir akış o vaadi tam da en
    çok gerektiği anda bozar."""
    src = fe_dosyalari()[_DCM]
    assert "kos.isError" in src


def test_DCM_yeni_PANEL_acmadi():
    """K5 tavanı 13/13 — *bir yetenek bir panel doğurmaz.*"""
    from tests.test_panel_sayisi import DESEN

    assert not DESEN.findall(fe_kaynak() and fe_dosyalari()[_DCM])
