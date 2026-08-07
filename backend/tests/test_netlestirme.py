

# --- 🔴 G2.9 — `yuksek` DÜZEYİN KALAN FARKI: BOYUT --------------------------------


def test_BOYUT_ADAYLARI_OLCU_IKIZI():
    """🔴 `G2.9` — `netlestirme.py`'nin tablosu `yuksek` için *"belirsiz ölçü/**boyutta**
    da sorar"* diyor. Ölçü tarafı `normal`'da bile zaten soruluyor; yani `yuksek`'in
    gerçek deltası **boyut** ve o **hiç uygulanmamıştı**.

    ⚠ Yeni tarayıcı yazılmadı: eşleştirmeyi `_match_dims` yapıyor, yeni fonksiyon yalnız
    *"kaç cube sahiplendi"* diye sayıyor.
    *Bir soruyu iki kez sormak, iki kez cevaplamayı göze almaktır.*
    """
    import inspect

    from app import cube_router as cr

    assert hasattr(cr, "dimension_cube_candidates"), "🔴 boyut dedektörü yok"
    src = inspect.getsource(cr.dimension_cube_candidates)
    assert "_match_dims" in src, (
        "🔴 boyut eşleştirmesi yeniden yazılmış — `_match_dims` tek sahip olmalı")
    assert "_any_hit(q, c.get(\"synonyms\"))" in src, (
        "🔴 cube-düzeyi eşleşme hariç tutulmuyor — ikizindeki kural düşmüş")


def test_YUKSEK_VARSAYILAN_DEGIL_kural_B():
    """🔴 `KURAL B`: `normal` (varsayılan) davranışı **birebir bugünkü** kalmalı.

    Modülün kendi uyarısı: `yuksek` için *"kapsam düşer, sessiz-yanlış da"* — yani bu bir
    **takas** ve takası seçen **kiracıdır**.
    *Bir kapsam kaybını varsayılan yapmak, kullanıcı adına karar vermektir.*
    """
    import pathlib

    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app/routers/ask.py").read_text(encoding="utf-8")
    assert 'if _netlestirme_duzeyi(request) == "yuksek":' in kaynak, (
        "🔴 `yuksek` dalı yok — modülün tablosu uygulanmıyor")
    i = kaynak.index('== "yuksek"')
    assert "dimension_cube_candidates" in kaynak[i:i + 400], (
        "🔴 `yuksek` dalı boyut adaylarını eklemiyor")
