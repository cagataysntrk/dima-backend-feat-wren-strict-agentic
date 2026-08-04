"""FAZ 0.16 — ÖLÇÜM BÜTÇESİ ve KOŞUM HİJYENİ.

## Neden

Bu belgenin **151 maddesinin her «önce ölç» kapısı** bir API kotasına bağlı. Geliştiricinin
kendi kaydı (`50402d3`): *"gemini-flash-lite **2×429** … nemotron-ultra ⊘ **54×429** —
ücretsiz katman doydu"* ve *"ölçümün gerçek gürültü kaynağı **BENİMDİ**: üç konteyner aynı
anda API'yi dövüyordu."* Deneyimin kalbi olan `t2_anlatici` **tam bu yüzden** hâlâ ⊘.

## Üç parça

1. **Ayrılmış ölçüm anahtarı** (`DIMA_MEASURE_KEY`) — ürün trafiğiyle kota rekabeti biter.
   Tanımsızsa davranış **birebir bugünkü** (GERİ AL).
2. **Kota ön uçuşu** — *"sağlayıcı kuruldu"* ≠ *"sağlayıcı cevap veriyor"*. Tek ucuz
   çağrı; başarısızsa **koşma** (fail-closed).
3. **Koşum hijyeni** — konteyner adlandırılır, `-d` ile koşulur, açıkça kapatılır.
   `--rm` yetmiyor: kütüğü siler ve kabuk ölürse özet **tamamen kaybolur** (bu operasyonda
   iki koşum böyle kayboldu).

## Tek sahip

Üçü de `konusma_senaryolari._canli_ortami_geri_yukle`'de — çünkü `--live` koşan **dört
aracın dördü de** oradan geçer (`deneyim` · `vk_taban` · `nl_accuracy` · kendisi).
Anahtarı ya da ön uçuşu tüketicilerin her birine yazmak, dördüncüsünü unutmak demekti.
"""

from __future__ import annotations

import inspect

import pytest

from lab import konusma_senaryolari as ks


def test_OLCUM_ANAHTARI_AYARDA_var():
    """`DIMA_MEASURE_KEY` bir **ayardır**, sihirli bir ortam değişkeni değil."""
    from app.config import Settings

    for alan in ("measure_api_key", "measure_provider"):
        assert alan in Settings.model_fields, f"`{alan}` ayarı YOK"
    assert Settings().measure_api_key == "", \
        "ölçüm anahtarının varsayılanı BOŞ olmalı — tanımsızsa bugünkü davranış korunur"


def test_ANAHTAR_SECIMI_TEK_SAHIPTE():
    """Dört `--live` tüketicisinin dördü de bu fonksiyondan geçer; anahtar seçimi
    burada **bir kez** yazılır. İkinci bir sahip, dördüncüsünü unutmak demektir."""
    govde = inspect.getsource(ks._canli_ortami_geri_yukle)
    assert "DIMA_MEASURE_KEY" in govde, "ölçüm anahtarı tek sahipte OKUNMUYOR"
    assert "_kota_on_ucusu" in govde, "kota ön uçuşu tek sahipten ÇAĞRILMIYOR"

    # Tüketiciler gerçekten bu sahibi çağırıyor mu (beyan değil, çağrı)?
    for arac in ("deneyim", "vk_taban", "nl_accuracy"):
        mod = __import__(f"lab.{arac}", fromlist=["x"])
        assert "_canli_ortami_geri_yukle" in inspect.getsource(mod), \
            f"`lab/{arac}.py` canlı-ortam sahibini çağırmıyor — kendi kopyası olabilir"


def test_TANIMSIZSA_BUGUNKU_DAVRANIS(monkeypatch):
    """**GERİ AL:** `DIMA_MEASURE_KEY` yoksa sağlayıcı anahtarı DEĞİŞMEZ."""
    monkeypatch.delenv("DIMA_MEASURE_KEY", raising=False)
    monkeypatch.setenv("DIMA_GEMINI_API_KEY", "urun-anahtari")
    monkeypatch.setenv("DIMA_LLM_PROVIDER", "gemini")
    import os

    govde = inspect.getsource(ks._canli_ortami_geri_yukle)
    assert 'os.environ.get("DIMA_MEASURE_KEY", "").strip()' in govde
    # Boş anahtar hiçbir şeyi ezmemeli (kod yolunun kendisi `if _olcum_anahtari` ile korunur)
    assert 'if _olcum_anahtari and saglayici not in' in govde, \
        "boş ölçüm anahtarı sağlayıcı anahtarını EZEBİLİR — GERİ AL kırılır"
    assert os.environ["DIMA_GEMINI_API_KEY"] == "urun-anahtari"


class _Doymus:
    def generate_sql(self, *a, **k):
        raise RuntimeError("429 Too Many Requests: quota exceeded")


class _Sessiz:
    def generate_sql(self, *a, **k):
        return "   "


class _Calisan:
    def generate_sql(self, *a, **k):
        return "SELECT 1"


def test_KOTA_DOLUYSA_KOSMAZ(monkeypatch):
    """🔴 **KAPI.** Kota tükenmişse koşum **durur** — sessizce `rule`'a düşmez ve
    yarım kotayla üretilmiş bir sayı bayrak kararına dayanak yapılmaz."""
    monkeypatch.delenv("DIMA_KOTA_ON_UCUSU", raising=False)
    with pytest.raises(SystemExit) as e:
        ks._kota_on_ucusu(_Doymus())
    assert "429" in str(e.value) and "DURDURULDU" in str(e.value)
    assert "DIMA_MEASURE_KEY" in str(e.value), \
        "hata mesajı ÇÖZÜMÜ göstermiyor — kullanıcı ne yapacağını bilmeli"


def test_BOS_CEVAP_da_KOSMAZ(monkeypatch):
    """*"Üretici kuruldu"* ≠ *"üretici cevap veriyor"*. Boş dönen bir sağlayıcı,
    429 veren kadar ölçümü bozar — ve daha sinsidir çünkü istisna atmaz."""
    monkeypatch.delenv("DIMA_KOTA_ON_UCUSU", raising=False)
    with pytest.raises(SystemExit, match="BOŞ DÖNDÜ"):
        ks._kota_on_ucusu(_Sessiz())


def test_CALISAN_SAGLAYICIDA_ENGEL_YOK(monkeypatch):
    """Ön uçuş bir **kapı**dır, bir engel değil: çalışan sağlayıcıda sessizce geçer."""
    monkeypatch.delenv("DIMA_KOTA_ON_UCUSU", raising=False)
    ks._kota_on_ucusu(_Calisan())        # istisna atmamalı


def test_ON_UCUS_KAPATILABILIR_ama_SESSIZ_DEGIL(monkeypatch, capsys):
    """Kaçış kapağı var (ağ arızası bir turu kilitlemesin) ama **sessiz değil**:
    korumasız koştuğunu SÖYLER. Sessiz bir kaçış kapağı, kapının kendisini eritir."""
    monkeypatch.setenv("DIMA_KOTA_ON_UCUSU", "0")
    ks._kota_on_ucusu(_Doymus())         # atmamalı
    assert "KORUMASIZ" in capsys.readouterr().out


def test_KOSUM_HIJYENI_KURALI_YAZILI():
    """*"`--rm` istemci ölünce yetmiyor"* — bu operasyonda **iki kapı koşumunun özeti
    böyle kayboldu**. Kural `OPERASYON.md`'de yazılı olmalı, yoksa tekrar edilir."""
    import pathlib

    # ⚠ `OPERASYON.md` repo kökündedir ve kapı konteynerine **mount EDİLMEZ** → orada
    # aranırsa test her koşumda `skip` olur. **Atlanan bir kapı, kapı değildir.**
    # Kural bu yüzden `backend/CLAUDE.md`'ye de yazıldı (her zaman mount edilir);
    # kök varsa o da kontrol edilir.
    kok = pathlib.Path(__file__).resolve().parents[2]
    kaynaklar = [kok / "OPERASYON.md", pathlib.Path(__file__).resolve().parents[1] / "CLAUDE.md"]
    m = "\n".join(k.read_text(encoding="utf-8") for k in kaynaklar if k.exists())
    assert m, "ne OPERASYON.md ne CLAUDE.md bulunabildi"
    assert "--rm" in m and "-d" in m, "konteyner hijyeni kuralı YAZILI DEĞİL"
    assert "docker wait" in m, "kütüğün nasıl korunacağı yazılmamış"
