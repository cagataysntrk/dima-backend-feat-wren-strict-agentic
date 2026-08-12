r"""🔴🔴 `§F1` — **ARŞİVLENMİŞ MOTOR DİRİLMEZ.** Motor **in-process**tir, bir servis değil.

## Kullanıcı kararı (2026-08-12) — ve bu kapının varlık sebebi

> *«Eski o kaldırdığımız Wren motorunu ayağa kaldırmadın di mi? Bu riski almayalım, onu
> temizle ve **kural olarak ekle**. Yeni motor çalışacak, mutlaka dikkat edelim.»*

Bu depoda **İKİ AYRI ŞEY** benzer adlar taşıyor ve karıştırılmaları ürünü sessizce
bozabilir:

| | **YENİ — yaşayan** | **ESKİ — arşivlenmiş** |
|---|---|---|
| ne | `wren.engine.WrenEngine` — **Python kütüphanesi** | `ghcr.io/canner/wren-engine` — **Docker servisi** |
| nasıl | `from wren.engine import WrenEngine` (`wren_service.py:18`), **in-process**, subprocess YOK | HTTP, `:8080`, `WREN_ENGINE_URL` ile |
| durumu | ✅ üretimde, her cevabın SQL'ini bu derliyor | ⊘ **kapatıldı** (`§F1`, 2026-08-11) |
| kaynağı | `wren` paketi (kurulu, 28 alt modül) | **arşivlenmiş** depo (`Canner/wren-engine` → `WrenAI` `core/`, salt-okunur), üstelik `latest` etiketiyle |

⚠ `demo/wren-project` **YENİ** motora aittir (semantik model dizini, `DIMA_PROJECT_DIR`) —
adı benzediği için eski motorun kalıntısı sanılmamalı. *İki şeyin adı benziyorsa, kapı
onları ADIYLA değil YOLUYLA ayırmalıdır.*

## Bu turda ölçülen gerçek kalıntı

Kapatma kararı 2026-08-11'de verilmiş ve `docker-compose.yml` doğru yazılmıştı. Ama
2026-08-12'de ölçüldü: **koşan backend konteyneri hâlâ `WREN_ENGINE_URL=http://wren-engine:8080`
taşıyordu** — çünkü o konteyner, satır yoruma alınmadan **önceki** bir compose'dan
yaratılmıştı. Değişken **ölü**ydü (okuyan kod: **0**), ama ölü bir işaretçi, bir gün
okunduğunda ölü kalmaz.

⊙ Temizlik: konteyner temiz env ile yeniden yaratıldı · kalıntı konteyner kaldırıldı ·
arşivlenmiş **imaj (679 MB)** silindi · `:8080` boş · canlı curl ile yeni motorun
çalıştığı doğrulandı (`source=cube`, gerçek SQL, gerçek satır).

> *Bir bağımlılığı yapılandırmadan çıkarmak onu ortamdan çıkarmaz; çalışan süreç,
> yazıldığı günün yapılandırmasını taşır.*
"""

from __future__ import annotations

import pathlib
import re

import pytest

_BACKEND = pathlib.Path(__file__).parent.parent
_KOK = _BACKEND.parent
_COMPOSE = _KOK / "docker-compose.yml"

#: 🔴 Eski **HTTP-servis** mimarisinin izleri. Kapalı bir küme: her biri o mimariye
#: özgüdür ve yeni (in-process) motorda karşılığı **yoktur**.
#: ⚠ `wren-project` **BURADA DEĞİL** — o yeni motorun model dizinidir.
SERVIS_IZLERI = ("WREN_ENGINE_URL", "wren-engine", "WREN_ENGINE_PORT")

#: Ürün ve laboratuvar ağaçları. `tests/` **bilerek dışarıda**: bu dosyanın kendisi
#: yasaklı dizgeleri **anlatmak** için içeriyor ve bir kuralın metni, kuralın ihlali
#: değildir (bu deponun 🅐 dersi: ilanı ölçmek ≠ değişmezi ölçmek).
_AGACLAR = ("app", "lab")


def test_URUN_KODUNDA_SERVIS_IZI_YOK():
    """🔴🔴 **ASIL KAPI.** `app/` ve `lab/` altında eski servis mimarisinin izi olamaz.

    Kırmızı verirse biri motoru yeniden **HTTP servisi** olarak konuşmaya başlamış
    demektir — ve o an `LLM SQL yazmaz` zincirinin derleyici ucu, bakımı bırakılmış
    bir imaja bağlanmış olur.
    """
    bulunan: dict[str, str] = {}
    for kok in _AGACLAR:
        d = _BACKEND / kok
        if not d.is_dir():
            continue
        for f in d.rglob("*.py"):
            metin = f.read_text(encoding="utf-8", errors="ignore")
            for iz in SERVIS_IZLERI:
                if iz in metin:
                    bulunan[f"{kok}/{f.relative_to(d)}"] = iz
    assert not bulunan, (
        f"🔴 ARŞİVLENMİŞ MOTOR GERİ GELİYOR: {bulunan}\n"
        "Motor **in-process**tir (`from wren.engine import WrenEngine`). Bir HTTP "
        "servisine bağlanmak, bakımı bırakılmış (`latest` etiketli, arşivlenmiş) bir "
        "imajı ürünün SQL derleyicisi yapmaktır. Karar `§F1`'de yazılı.")


def test_YENI_MOTOR_IN_PROCESS_ve_AYAKTA():
    """⊘ **Ön koşul — ve kullanıcının asıl şartı:** *«yeni motor çalışacak, mutlaka».*

    Bir *«eski motor yok»* kapısı, yeni motorun **var** olduğunu ölçmezse bir gün ikisi
    birden yokken de yeşil kalır. *Bir yasağı ölçmek, yerine geçenin çalıştığını
    ölçmeden yarım bir güvencedir.*
    """
    kaynak = (_BACKEND / "app" / "wren_service.py")
    assert kaynak.is_file(), "⊘ ölçüm tabanı çöktü: `app/wren_service.py` yok"
    metin = kaynak.read_text(encoding="utf-8")
    assert "from wren.engine import WrenEngine" in metin, (
        "🔴 motor artık kütüphane olarak içe aktarılmıyor — in-process mimari kalkmış "
        "olabilir.")
    from app.wren_service import WrenService

    assert hasattr(WrenService, "query") and hasattr(WrenService, "dry_plan"), (
        "🔴 `WrenService` yüzeyi değişti; güvenlik zinciri (`dry_plan`) kaybolmuş olabilir.")


def test_COMPOSE_BLOGU_YORUMDA_KALIYOR():
    """⚠ `MIMARI §10`: *«kapananlar işaretlenir, silinmez»* — blok duruyor ama
    **yorumda** durmalı.

    ⊙ Yüklem yapısal: yasaklı dizgeyi taşıyan **her** satır `#` ile başlamalı. Blok bir
    gün yorumdan çıkarılırsa bu kapı konuşur; metnin kendisi silinirse `§F1`'in
    gerekçesi kaybolur, o yüzden silinmesi de istenmiyor.
    """
    if not _COMPOSE.is_file():
        pytest.skip("⊘ `docker-compose.yml` bağlanmamış (konteyner kökü mount edilmemiş)")
    kacak = []
    for n, satir in enumerate(_COMPOSE.read_text(encoding="utf-8").splitlines(), 1):
        if any(iz in satir for iz in SERVIS_IZLERI) and not satir.lstrip().startswith("#"):
            kacak.append(f"{n}: {satir.strip()[:70]}")
    assert not kacak, (
        f"🔴 `docker-compose.yml`'de arşivlenmiş motor YORUMDAN ÇIKMIŞ:\n" +
        "\n".join(kacak) +
        "\n*Çalışmayan bir bağımlılık, olmayan bir bağımlılıktan pahalıdır: bakım "
        "ister, kaynak yakar, hiçbir iş görmez.*")
    assert "wren-engine" in _COMPOSE.read_text(encoding="utf-8"), (
        "⚠ `§F1`'in gerekçe bloğu silinmiş — `MIMARI §10` kapananların **işaretlenmesini** "
        "ister; silinen bir karar, bir sonraki turda yeniden verilir.")


def test_AYRIM_YAZILI_wren_project_YENI_MOTORUN():
    """⚠ *«Adı benziyor»* tuzağı bir kapıya bağlanıyor.

    `demo/wren-project` **yeni** motorun model dizinidir (`DIMA_PROJECT_DIR`); bir
    temizlik turunda eski motorun kalıntısı sanılıp silinirse **her cevap** düşer.
    Bu yüzden ayrım bu dosyada **yazılı** ve yazılı kalmalı.
    """
    m = pathlib.Path(__file__).read_text(encoding="utf-8")
    assert "wren-project" in m and "DIMA_PROJECT_DIR" in m, (
        "🔴 `wren-project` ↔ `wren-engine` ayrımı silinmiş — *iki şeyin adı benziyorsa, "
        "kapı onları ADIYLA değil YOLUYLA ayırmalıdır.*")
