"""FAZ 5.9b kapısı — **yetim tablo kapandı.** [bayraksız]

`NotificationPreference` **0 satır, router yok** durumundaydı: kullanıcı bir kategoriyi
kapatabileceğini sanıyordu ama onu **yazacağı hiçbir yüzey yoktu**.

> 🔴 *Beyan edilmiş ama yazılamayan bir tercih, verilmemiş bir sözden kötüdür.*
"""

from __future__ import annotations

import pytest

from app.routers import bildirim_tercihleri as bt


def test_KATEGORI_ve_KANAL_kapali_liste():
    """🔴 Bilinmeyen bir kategori, **hiçbir gönderici tarafından okunmayacak** bir tercih
    üretirdi — kullanıcı kapattığını sanır, bildirim gelmeye devam eder."""
    assert set(bt.KATEGORILER) == {"report", "alert", "anomaly", "system"}
    assert "email" in bt.KANALLAR and "slack" in bt.KANALLAR


def test_KANALLAR_channels_kaydiyla_AYNI():
    """⚠ İki liste ayrışırsa, kullanıcı var olmayan bir kanalı kapatır ya da var olan
    bir kanalı hiç göremez."""
    from app import channels

    kayitli = set(channels._CHANNELS)
    assert kayitli <= set(bt.KANALLAR), (
        f"🔴 `channels.py`'de kayıtlı ama tercih listesinde YOK: "
        f"{sorted(kayitli - set(bt.KANALLAR))} — o kanal kapatılamaz.")


def test_TERCIH_SELF_baskasi_adina_yazilamaz():
    """⚠ Belirteç **AST**: uç, kullanıcı kimliğini **token'dan** almalı (`_kimlik`), istek
    gövdesinden **değil** (ADR-0014). Gövdeden alsaydı bir kullanıcı başkasının
    bildirimlerini kapatabilirdi."""
    import ast
    from pathlib import Path

    agac = ast.parse((Path(__file__).resolve().parents[1]
                      / "app/routers/bildirim_tercihleri.py").read_text(encoding="utf-8"))
    for fn in (n for n in ast.walk(agac)
               if isinstance(n, ast.FunctionDef) and n.name in ("yaz", "sil", "listele")):
        kaynak = ast.unparse(fn)
        assert "_kimlik" in kaynak, f"`{fn.name}` kimliği token'dan almıyor"
        assert '"user_id"' not in kaynak and "'user_id'" not in kaynak, (
            f"🔴 `{fn.name}` gövdeden `user_id` okuyor — bir kullanıcı BAŞKASININ "
            f"bildirimlerini kapatabilir (ADR-0014 ihlali).")


def test_SILME_KAPATMA_DEGILDIR():
    """🔴 Silmek tercihi *"hiç verilmemiş"* yapar → **varsayılan AÇIK**.

    *"Kapalı"* demek isteyen `enabled: false` yazar. Silmeyi kapatma sanmak, kullanıcıyı
    **sessize alır**.
    """
    import ast
    from pathlib import Path

    kaynak = (Path(__file__).resolve().parents[1]
              / "app/routers/bildirim_tercihleri.py").read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "sil")
    govde = ast.unparse(fn)
    assert "deleted_at" in govde, "🔴 hard-delete — ADR-0019 soft-delete ihlali"
    # ⚠ Belirteç **çağrı düğümlerine** bakar, metne değil: ilk yazımda `"delete(" not in
    # govde` **decorator'ın kendisini** (`@router.delete(...)`) yakaladı ve yanlış-kırmızı
    # verdi. *Bir kuralı ölçen belirteç, kuralın uygulandığı hâli cezalandırmamalı.*
    # ⚠ **DECORATOR LİSTESİ HARİÇ**: `@router.delete(...)` da bir `Call` düğümüdür ve
    # `ast.walk(fn)` onu da gezer. Yalnız **gövde** taranır.
    silme_cagrilari = {getattr(c.func, "attr", "")
                       for st in fn.body for c in ast.walk(st)
                       if isinstance(c, ast.Call)}
    assert "delete" not in silme_cagrilari, (
        "🔴 Oturumda hard-delete çağrısı var — ADR-0019 soft-delete ihlali.")
    assert "VARSAYILAN" in kaynak, (
        "🔴 Silmenin varsayılana DÖNDÜRDÜĞÜ kullanıcıya söylenmiyor.")


def test_LISTE_EKSIKLERI_de_anlatir():
    """⚠ *Bir listede görünmeyen ayar, kullanıcının olmadığını sandığı ayardır.*

    Kayıt olmayan (kategori × kanal) çiftleri `varsayilan: true` ile dönmeli.
    """
    from pathlib import Path

    kaynak = (Path(__file__).resolve().parents[1]
              / "app/routers/bildirim_tercihleri.py").read_text(encoding="utf-8")
    assert '"varsayilan": r is None' in kaynak, (
        "🔴 'Hiç ayarlanmadı' ile 'açık bırakıldı' aynı görünüyor.")


def test_KAPI_5_9a_ile_TUTARLI():
    """FAZ 5.9a'nın okuma tarafı (`tercih_izin_veriyor_mu`) ile bu yazma tarafı **aynı
    varsayılanı** paylaşmalı: kayıt yoksa **AÇIK**."""
    from app.bildirim_kapisi import tercih_izin_veriyor_mu

    assert tercih_izin_veriyor_mu("alert", "email", []) is True
    assert tercih_izin_veriyor_mu("alert", "email", None) is True


@pytest.mark.parametrize("kat", ["bilinmeyen", "", "REPORT"])
def test_BILINMEYEN_kategori_reddedilir(kat):
    assert kat not in bt.KATEGORILER
