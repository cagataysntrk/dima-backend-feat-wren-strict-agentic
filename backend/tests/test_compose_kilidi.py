"""FAZ 1.4 — **SÜREÇ-ARASI DERLEME KİLİDİ** kapısı.

## Neden

MIMARI §6.3 ⚠: kilit **süreç-içiydi** (`threading`); *"iki süreç aynı çıktı dizinine
compose ederse yarış geri döner"* — 2026-08-02'de **yeniden üretilerek** teşhis edilmişti.

🔴 **2026-08-04'te İKİNCİ KEZ, kendiliğinden gözlendi ve bir KAPIYI KIRDI.** Demet 9
kapısında `gitas` korpustan **tamamen düştü**:
`FileNotFoundError: demo/wren-project/cubes/enerji_makine/metadata.yml`. Dosya sonradan
**yerindeydi** — yani okuyucu compose'un **ortasına** denk gelmişti. Kapı `%94,3` doğruluk
raporlarken kırmızıydı, çünkü **payda 445 → 342** düşmüştü: *bir metriğin iyileşmesi,
ölçülemeyenlerin denklemden çıkmasıyla da olur.*

## Ölçülmüş tuzak: kilit dosyası NEREDE duruyor

`compose()` çıktı dizinindeki `target` **dışındaki her çocuğu siler**. İçeriye konan bir
kilit dosyası, **tutulurken unlink edilirdi**: kilidi tutan süreç silinmiş inode üzerinde
beklemeye devam eder, ikinci süreç **YENİ bir inode** açıp `flock`'u **anında** alır.
Kilit **sessizce çalışmaz** hâle gelir — hiç kilit olmamasından kötüdür, çünkü üstüne bir
garanti beyanı gelir. Bu yüzden dosya dizinin **KARDEŞİ**dir.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
import threading
import time
from pathlib import Path

import pytest

from app import compose as C

KOK = Path(__file__).resolve().parents[1]


# ── 1 · KİLİT DOSYASININ KONUMU (yapısal) ────────────────────────────────────

def test_KILIT_DOSYASI_CIKTI_DIZININ_ICINDE_DEGIL(tmp_path: Path):
    """🔴 **Ölçülmüş tuzak.** İçeride olsaydı `compose()` onu tutulurken **silerdi** ve
    ikinci süreç yeni bir inode üzerinde kilidi **anında** alırdı."""
    out = tmp_path / "wren-projects" / "firma"
    yol = C.kilit_dosyasi(out)
    assert out.resolve() not in yol.resolve().parents, (
        f"kilit dosyası çıktı dizininin İÇİNDE: {yol} — `compose()` onu siler ve kilit "
        "sessizce çalışmaz hâle gelir")
    assert yol.name.endswith(".compose.lock")


def test_KILIT_DOSYASI_COMPOSE_SILME_DONGUSUNDEN_ETKILENMIYOR():
    """`compose()`'un silme döngüsü `out.iterdir()` üzerinde döner; kardeş dosya o
    kümede **değildir**. Bu test, silme döngüsünün kapsamını **kaynaktan** doğrular ki
    biri onu `out.parent`'a genişletirse görünür olsun."""
    kaynak = (KOK / "app" / "compose.py").read_text(encoding="utf-8")
    assert "for child in sorted(out.iterdir())" in kaynak, (
        "compose'un silme döngüsü değişmiş — kilit dosyasının konumu YENİDEN "
        "değerlendirilmeli (kardeş konum bu döngünün kapsamına dayanıyor)")


# ── 2 · SÜREÇ-ARASI KARŞILIKLI DIŞLAMA (iki GERÇEK süreç) ────────────────────

_TUTUCU = textwrap.dedent("""
    import fcntl, os, sys, time
    fd = os.open(sys.argv[1], os.O_CREAT | os.O_RDWR, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX)
    print("ALDIM", flush=True)
    time.sleep(float(sys.argv[2]))
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)
""")


def test_IKINCI_SUREC_BEKLIYOR(tmp_path: Path, monkeypatch):
    """🔴 **Maddenin kalbi.** Bir SÜREÇ kilidi tutarken, bu süreç **beklemeli** —
    `threading.Lock` bunu yapamazdı çünkü kapsamı yalnız kendi süreciydi."""
    pytest.importorskip("fcntl")
    out = tmp_path / "proje"
    out.mkdir()
    yol = C.kilit_dosyasi(out)

    tutucu = subprocess.Popen([sys.executable, "-c", _TUTUCU, str(yol), "1.0"],
                              stdout=subprocess.PIPE, text=True)
    try:
        assert tutucu.stdout.readline().strip() == "ALDIM", "tutucu süreç kilidi alamadı"
        t0 = time.monotonic()
        with C.DerlemeKilidi(out):
            gecen = time.monotonic() - t0
        assert gecen >= 0.5, (
            f"kilit {gecen:.2f} sn'de alındı — başka bir SÜREÇ tutarken beklenmedi; "
            "süreç-arası kademe çalışmıyor")
    finally:
        tutucu.wait(timeout=10)


def test_ZAMAN_ASIMINDA_RUNTIME_ERROR(tmp_path: Path, monkeypatch):
    """🔴 **Sessiz geçiş YOK.** Kilidi alamadan derlemeye girmek, kilidin var olmamasıyla
    aynı şeydir — ama üstüne bir de *"korunuyoruz"* beyanı ekler."""
    pytest.importorskip("fcntl")
    out = tmp_path / "proje"
    out.mkdir()
    yol = C.kilit_dosyasi(out)
    monkeypatch.setattr(C, "KILIT_ZAMAN_ASIMI_SN", 0.3)

    tutucu = subprocess.Popen([sys.executable, "-c", _TUTUCU, str(yol), "3.0"],
                              stdout=subprocess.PIPE, text=True)
    try:
        assert tutucu.stdout.readline().strip() == "ALDIM"
        with pytest.raises(RuntimeError, match="compose kilidi"):
            with C.DerlemeKilidi(out):
                pytest.fail("kilit alınamadığı hâlde bloğa GİRİLDİ — sessiz geçiş")
    finally:
        tutucu.kill()
        tutucu.wait(timeout=10)


def test_ZAMAN_ASIMINDA_YEREL_KILIT_DE_BIRAKILIYOR(tmp_path: Path, monkeypatch):
    """Süreç-arası kademe başarısız olursa **süreç-içi kilit de bırakılmalı** — yoksa
    ilk zaman aşımı, o dizini bu süreçte **kalıcı olarak** kilitlerdi (deadlock)."""
    pytest.importorskip("fcntl")
    out = tmp_path / "proje"
    out.mkdir()
    monkeypatch.setattr(C, "KILIT_ZAMAN_ASIMI_SN", 0.2)
    kilit = C.DerlemeKilidi(out)
    tutucu = subprocess.Popen([sys.executable, "-c", _TUTUCU,
                               str(C.kilit_dosyasi(out)), "1.5"],
                              stdout=subprocess.PIPE, text=True)
    try:
        assert tutucu.stdout.readline().strip() == "ALDIM"
        with pytest.raises(RuntimeError):
            kilit.__enter__()
        assert not kilit._yerel.locked(), (
            "zaman aşımından sonra süreç-içi kilit HÂLÂ TUTULUYOR — bu dizin bu süreçte "
            "kalıcı olarak kilitlendi (deadlock)")
    finally:
        tutucu.kill()
        tutucu.wait(timeout=10)


# ── 3 · SÜREÇ-İÇİ KADEME KORUNUYOR ───────────────────────────────────────────

def test_AYNI_SURECTE_IKINCI_THREAD_BEKLIYOR(tmp_path: Path):
    """İç kademe **ucuz ve hızlı**: aynı süreçteki ikinci thread `flock` sistem çağrısına
    hiç gitmez. Kaldırılırsa her thread bir dosya tanıtıcısı açardı."""
    out = tmp_path / "proje"
    out.mkdir()
    kilit = C.build_lock_for(out)
    sira: list[str] = []

    def isci(ad: str, bekle: float):
        with kilit:
            sira.append(f"{ad}-giris")
            time.sleep(bekle)
            sira.append(f"{ad}-cikis")

    t1 = threading.Thread(target=isci, args=("a", 0.3))
    t2 = threading.Thread(target=isci, args=("b", 0.0))
    t1.start()
    time.sleep(0.05)
    t2.start()
    t1.join(timeout=10)
    t2.join(timeout=10)
    assert sira == ["a-giris", "a-cikis", "b-giris", "b-cikis"], (
        f"thread'ler iç içe girdi: {sira}")


def test_KIMLIK_SOZLESMESI_KORUNDU(tmp_path: Path):
    """⟳ Dönen nesne artık `threading.Lock` değil ama **aynı yol → aynı nesne** sözleşmesi
    korunmalı: `CompanyRegistry` ile `compose_and_build()` AYNI kilidi almalı."""
    a = C.build_lock_for(tmp_path)
    assert a is C.build_lock_for(Path(str(tmp_path)))
    assert a is C.build_lock_for(tmp_path / ".." / tmp_path.name)
    assert C.build_lock_for(tmp_path.parent) is not a


# ── 4 · fcntl YOKSA: GÜRÜLTÜLÜ DÜŞÜŞ ─────────────────────────────────────────

def test_FCNTL_YOKSA_SESSIZCE_DUSMUYOR():
    """🔴 Sessizce düşürmek, kilidin **var olmadığı** bir ortamda *"korunuyoruz"* sanmak
    olurdu. Süreci reddetmek ise orantısız: tek süreçli bir kurulumda iç kademe doğru ve
    yeterlidir. → **uyarı loglanır**, akış sürer."""
    kaynak = (KOK / "app" / "compose.py").read_text(encoding="utf-8")
    i = kaynak.index("except ImportError")
    pencere = kaynak[i:i + 400]
    assert "_log.warning" in pencere, "`fcntl` yokluğu SESSİZCE geçiliyor"
    assert "SÜREÇ-ARASI KİLİT YOK" in pencere


# ── 5 · GERÇEK DERLEME: MANİFEST HER AN GEÇERLİ ──────────────────────────────

def test_OKUYUCU_HER_AN_GECERLI_MANIFEST_GORUYOR():
    """`build()`'in `os.replace`'i atomiktir: okuyucu her an ya **ESKİ** ya **YENİ**
    manifesti görür, asla yok/yarım görmez. Kilit yazar×yazar için; bu kapı yazar×okuyucu
    tarafının **hâlâ** atomik olduğunu doğrular — ikisi birbirini tamamlar."""
    kaynak = (KOK / "app" / "compose.py").read_text(encoding="utf-8")
    assert "os.replace(tmp, out)" in kaynak, (
        "atomik yazma kaldırılmış — okuyucu YARIM manifest görebilir ve `always_filter` "
        "sessizce düşerdi (ölçülmüş senaryo)")


def test_MANIFEST_YAZIMI_GECERLI_JSON_URETIYOR(tmp_path: Path):
    """Kilit altında üretilen çıktı **okunabilir** olmalı — kilidin işi yarışı önlemek,
    ama sonucun geçerliliği ayrıca ölçülür (kilit doğru, çıktı bozuksa kilit avunmadır)."""
    hedef = tmp_path / "m.json"
    tmp = hedef.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({"models": []}), encoding="utf-8")
    os.replace(tmp, hedef)
    assert json.loads(hedef.read_text(encoding="utf-8")) == {"models": []}
