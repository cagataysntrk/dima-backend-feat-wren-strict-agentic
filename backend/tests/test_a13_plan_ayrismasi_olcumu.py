r"""⚠ `§A13` — *«Planın neden AYRIŞMADIĞINI ölç»*: ARAÇ korunur, SAYI korunamaz.

## Ölçülen boşluk

`§A13` ✅ *«ÖLÇÜLDÜ»* diye kapatılmıştı. Bir denetim ajanı sordu, ölçüm doğruladı:
araç **gerçek** (`/stats/plan` → `plan_garson.sayaclar()`), ama

* **kapı yok** — alanlardan biri düşse hiçbir kırmızı konuşmaz,
* ölçüm **tek seferlik**, sayaç **bellek içi**: süreç yeniden başlayınca sıfırlanır.

Canlı doğrulama (2026-08-12): `tek_adimli 3 · cok_adimli 0` — yayınlanan `%79`'u ne
doğrular ne çürütür (payda 3), yalnız **korunmadığını** gösterir.

## Bu kapı neyi korur — ve neyi bilerek KORUMAZ

✅ **Korur:** sayacın **var olduğunu** ve **ilan ettiği alanları ürettiğini**. Bir alan
sessizce düşerse `§A13`'ün cevabı *«ölçemiyoruz»*a döner ve bunu kimse duymaz.

⊘ **Korumaz: sayının kendisini.** Sayaç süreç-içi ve payda kullanıma bağlı; bir kapıda
dondurmak, ölçümü **ölçtüğü şeyden** koparmak olurdu. `§F8`'in aynı ilkesi:

> *Bir yayının kapısı, yayını üreten yolu korur; yayını yeniden üretmez.*

⚠ Bu yüzden `§A13`'ün yayınlanan `%79`'u **korunmasız kalıyor ve bu yazılı** — bir kapı
sanılmasın. Gerçek koruma, sayacın **kalıcı** bir yere yazıldığı gün gelir (`interaction_log`
deseni); o gün bu dosyanın yüklemi güçlenir.
"""

from __future__ import annotations


#: 🔴 `/stats/plan`'in **ilan ettiği** sözleşme. Kapalı liste: bir alan eklemek ürünün
#: sözleşmesini büyütmektir; çıkarmak `§A13`'ün cevabını daraltır — ikisi de görünür olmalı.
BEKLENEN_ALANLAR = {
    "adim_toplami", "cok_adimli", "denendi", "dustu", "gecerli", "onarildi",
    "onarim_tutma_yuzde", "red_nedenleri", "red_orani_yuzde", "tek_adimli",
    "yedege_dondu",
    # 🔴 **TUR KIRILIMI — İLAN EDİLDİ** (2026-08-13, tam kapı ölçümü).
    # `plan_garson:343` onarım turunu **dinamik anahtarla** sayıyor
    # (`onarildi_tur1`, `onarildi_tur2`, …). Eskiden bunlar `sayaclar()` çıktısında
    # **üst düzeye** seriliyordu; izole koşumda o yol hiç çalışmadığı için kapı
    # yeşil kalıyor, tam süitte bir onarım tetiklendiği anda `onarildi_tur1`
    # beliriyor ve bu yüklem *«ilan edilmemiş alan»* diye kırmızı veriyordu 🅢.
    # ⊙ Kapı **gevşetilmedi**: ürün, kırılımı `red_nedenleri` gibi **iç içe** bir
    # alana taşıdı ㊲ — üst düzey anahtar uzayı **kapalı**, bilgi **kaybolmadı**.
    "onarildi_turlere_gore",
}


def test_SAYAC_VAR_ve_ALANLARI_TAM():
    """🔴 **ASIL KAPI.** Sayaç, ilan ettiği alanların **hepsini** üretmeli."""
    from app.plan_garson import sayaclar

    d = sayaclar()
    assert isinstance(d, dict) and d, "⊘ ölçüm tabanı çöktü: sayaç boş döndü"
    eksik = BEKLENEN_ALANLAR - set(d)
    assert not eksik, (
        f"🔴 plan sayacından alan DÜŞMÜŞ: {sorted(eksik)}. `§A13`'ün cevabı "
        "(*«plan neden ayrışmıyor»*) o alanlardan üretiliyor; biri gidince soru "
        "cevapsız kalır ve **kimse duymaz**.")
    fazla = set(d) - BEKLENEN_ALANLAR
    assert not fazla, (
        f"⚠ sayaçta İLAN EDİLMEMİŞ alan var: {sorted(fazla)}. Yeni bir alan ürünün "
        "sözleşmesini büyütür — `BEKLENEN_ALANLAR`'a **gerekçesiyle** eklensin. "
        "*Sessizce büyüyen bir sözleşme, denetlenemeyen bir sözleşmedir.*")


def test_UC_BAGLI():
    """⚠ Sayaç var ama uç bağlı değilse ölçüm **dışarıdan alınamaz**.

    Yüklem `ast` üstünde: `grep` docstring'i de yakalar (bu deponun ölçülmüş dersi).
    """
    import ast
    import pathlib

    kaynak = (pathlib.Path(__file__).parent.parent / "app" / "routers"
              / "stats.py").read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    fn = next((n for n in ast.walk(agac)
               if isinstance(n, ast.FunctionDef) and n.name == "stats_plan"), None)
    assert fn is not None, "🔴 `/stats/plan` uç fonksiyonu yok"
    cagrilar = {n.func.id for n in ast.walk(fn)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "sayaclar" in cagrilar, (
        "🔴 `stats_plan` artık `sayaclar()` çağırmıyor — uç başka bir şey döndürüyor "
        "olabilir. *Bir ucun adı, ne döndürdüğünün kanıtı değildir.*")


def test_KORUMASIZLIK_YAZILI():
    """🔴 **Beyan kültürü:** neyi koruMADIĞIMIZ da yazılı olmalı.

    Bu dosya `§A13`'ün yayınlanan `%79`'unu **korumuyor** ve bunu açıkça söylüyor.
    Cümle silinirse, bir sonraki okuyucu bu kapıyı sayının kapısı sanar — ve
    *«kapı var»* ile *«sayı korunuyor»* arasındaki farkı kaybeder.
    """
    import pathlib

    m = pathlib.Path(__file__).read_text(encoding="utf-8")
    assert "Korumaz: sayının kendisini" in m and "korunmasız kalıyor ve bu yazılı" in m, (
        "🔴 korumasızlık beyanı silinmiş — *bir kapının kapsamı, kapının kendisi kadar "
        "bir vaattir.*")
