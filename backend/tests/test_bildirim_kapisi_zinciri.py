"""**FAZ 5.9 — BİLDİRİM KAPISI BAĞLANDI.** [bayraksız: kural]

## 🔴 Ölçülen kusur

`app/bildirim_kapisi.py` — **146 satır, 14 test** — üretim kodunda **hiç import
edilmiyordu**. Dört sıralı adım (tekilleştirme → bastırma → gruplama → tercih) yazılmış,
**hiçbir bildirim ondan geçmiyordu**. Denetimin *"12 yetim modül"* bulgusunun beşinci
kalemi.

⚠ Yetim modül: **12 → 6** (`certification` · `onay_akisi` · `tazelik` · `kpi_pin` ·
`bildirim_kapisi`; `main` yanlış-pozitif).

## 🔴 İlk yazımım anahtarı YANLIŞ kuruyordu — okuyarak yakalandı

`NotificationEvent`'te `source_id`/`direction` diye alanlar **yok**. `getattr(..., "")`
ile onları varsaymak, dedup anahtarını **her olayda aynı** yapardı ve kapı aynı
kategorideki **her ikinci bildirimi** bastırırdı — sessizce.

> 🔴 *Bir varsayılan, olmayan bir alanı sessizce bir sabite çevirir.*

Gerçek kimlik alanlar **okunarak** kuruldu: kaynak = `schedule_id` → `contract_id` →
`title`; yön = `violations`.

## Kalan yetimlerin AYRIMI — hepsi kusur değil

| modül | neden bağlı değil | kusur mu |
|---|---|---|
| `embed_kapsam` | 🔴 `AÇILAMAZ` — P0 (`motor_cls=off`) | **hayır**, bloke |
| `sinonim_onerici` | *"OFFLINE, çalışma-anı sorgu yoluna GİRMEZ"* | **hayır**, tasarım |
| `kanal_kimlik` | Slack/Teams adaptörü yok | **hayır**, ön koşul |
| `bayrak_profilleri` | test tarafı yardımcısı | **hayır** |
| `netlestirme` · `rules` | — | ✅ **evet**, sırada |

> ⚠ *Bir sayıyı bir kusur listesi sanmak, dördünü haksız yere borç yazar.*
"""

from __future__ import annotations

import ast
from pathlib import Path

_KOK = Path(__file__).resolve().parents[1]


def _dispatch_src() -> str:
    agac = ast.parse((_KOK / "app/channels.py").read_text(encoding="utf-8"))
    return ast.unparse(next(n for n in agac.body
                            if isinstance(n, ast.FunctionDef) and n.name == "dispatch"))


def test_MODUL_ARTIK_CAGRILIYOR():
    assert "bildirim_kapisi.kapidan_gecir(" in _dispatch_src()


def test_KAPI_HEDEFLERDEN_ONCE_kosuyor():
    """⚠ Bastırılmış bir olay **hiçbir kanala** gitmemeli; sonra koşsaydı *"bastırıldı"*
    yalnız bir **etiket** olurdu."""
    govde = _dispatch_src()
    i = govde.index("kapidan_gecir(")
    j = govde.index("for target in targets")
    assert i < j, "🔴 kapı fan-out'tan SONRA koşuyor"


def test_ANAHTAR_GERCEK_ALANLARDAN():
    """🔴 `source_id`/`direction` **yok**. Onları varsaymak, anahtarı her olayda aynı
    yapar ve **her ikinci bildirim** bastırılırdı."""
    from app.channels import NotificationEvent

    alanlar = set(NotificationEvent.__dataclass_fields__)
    assert "source_id" not in alanlar and "direction" not in alanlar
    govde = _dispatch_src()
    assert "schedule_id" in govde and "contract_id" in govde and "violations" in govde
    assert "'source_id'" not in govde and '"source_id"' not in govde


def test_YON_ANAHTARIN_PARCASI():
    """🔴 `dedup_key`'in kendi gerekçesi: *"fire yükseldi"* ile *"fire normale döndü"*
    aynı kaynaktan gelir ama **farklı haberlerdir**. Yön çıkarılırsa iyi haber kötü
    haberin penceresinde bastırılır ve kullanıcı sorunun **çözüldüğünü hiç öğrenmez**."""
    from app import bildirim_kapisi as bk

    a = bk.dedup_key("alert", "s1", "yukseldi")
    b = bk.dedup_key("alert", "s1", "normale_dondu")
    assert a != b


def test_CRITICAL_BASTIRILMIYOR():
    """🔴 Tekrar rahatsız edicidir; **kaçırılan bir kritik sinyal geri alınamaz**."""
    from app import bildirim_kapisi as bk

    anahtar = bk.dedup_key("alert", "s1", "y")
    gecmis = {anahtar: 100.0}
    assert bk.bastirilir_mi(anahtar, "warning", gecmis, 101.0) is True
    assert bk.bastirilir_mi(anahtar, "critical", gecmis, 101.0) is False


def test_BASTIRILAN_KAYIT_DONUYOR():
    """🔴 *Kayıt silinirse "neden bana haber verilmedi" sorusunun cevabı kimsede olmaz —
    ve o soru bir olaydan SONRA sorulur.*"""
    govde = _dispatch_src()
    assert "'bastirildi': True" in govde or '"bastirildi": True' in govde
    assert "kayıt tutuldu" in govde


def test_KAPI_BILDIRIMI_DUSURMUYOR():
    """⚠ Kapı koşulamazsa olay **geçer** (fail-open) ve bu **loglanır**: bir görünürlük
    filtresi, bildirimin kendisini riske atamaz."""
    govde = _dispatch_src()
    i = govde.index("kapidan_gecir(")
    assert "except Exception" in govde[i:i + 900]
    assert "_log.warning" in govde[i:i + 900]


def test_BELLEK_SINIRI_YAZILI():
    """⚠ Süreç-içi bellek: bir yeniden başlatma geçmişi sıfırlar ve **bir tekrar bildirim
    geçer**. *Sessizce süresiz bir bellek uydurmak yerine sınır yazılıyor.*"""
    src = (_KOK / "app/channels.py").read_text(encoding="utf-8")
    assert "yeniden başlatma geçmişi sıfırlar" in src


def test_YETIM_AYRIMI_yazili():
    """⚠ *Bir sayıyı bir kusur listesi sanmak, dördünü haksız yere borç yazar.*"""
    doc = __doc__ or ""
    assert "hepsi kusur değil" in doc and "AÇILAMAZ" in doc
