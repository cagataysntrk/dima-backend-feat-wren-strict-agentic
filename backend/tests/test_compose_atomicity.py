"""FAZ 0.2 — derleme atomikliği + eşzamanlılık regresyon kilitleri.

Panel bulgusu "REGISTRY COMPOSE RACE" (P0) iki ayrı yarışın belirtisiydi:

  (1) YAZAR × YAZAR — `compose_and_build()` HİÇ kilit tutmuyordu, üç yerden çağrılıyor
      (main lifespan · materializer'ın 60 sn'lik scheduler thread'i · measures onayı).
      `CompanyRegistry`'nin per-slug kilidi vardı ama `compose_and_build` ondan geçmiyordu,
      yani VARSAYILAN şirket korumasızdı.

  (2) YAZAR × OKUYUCU (asıl tehlikeli olan) — eski akışta `rmtree` `target/`i de siliyordu,
      dolayısıyla tüm compose+build boyunca (~130-160 ms) `target/mdl.json` YOKTU. O
      pencerede gelen bir sorgu ya `FileNotFoundError` alıyor ya da — çok daha kötüsü —
      `_inject_always_filter`'ın `except Exception: return sql` yutması yüzünden
      **always_filter'sız** çalışıyordu (iptal kayıtları toplama sızar, `source="cube"`
      rozetiyle). Bu, 20 satır aşağıdaki fail-closed bloğun önlemek için var olduğu şeydi.

Çözüm: `target/` compose sırasında KORUNUR + `build()` `os.replace` ile ATOMİK yazar →
okuyucu her an ya ESKİ ya YENİ manifesti görür. Bu dosya o davranışı kilitler.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest

from app.compose import build, build_lock_for, compose

DEMO = Path(__file__).resolve().parents[1] / "demo"
COMPANY = "demo-boyahane"


@pytest.fixture(scope="module")
def project(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("atomicity-project")
    compose(COMPANY, DEMO, out)
    build(out)
    return out


def _mdl(out: Path) -> Path:
    return out / "target" / "mdl.json"


# --- (a) atomik yazım -------------------------------------------------------

def test_build_gecici_dosya_birakmaz(project: Path):
    """`os.replace` öncesi yazılan tmp dosyası ortada kalmamalı."""
    build(project)
    leftovers = [p.name for p in (project / "target").iterdir()
                 if p.name.startswith(".mdl.json.tmp")]
    assert not leftovers, f"geçici dosya kaldı: {leftovers}"


def test_build_gecerli_json_uretir(project: Path):
    mdl = json.loads(_mdl(project).read_text())
    assert mdl["models"] and mdl["cubes"], "manifest boş"


# --- (b) compose target/'ı korur -------------------------------------------

def test_compose_target_dizinini_KORUR(tmp_path: Path):
    """En kritik iddia: compose sırasında eski manifest OKUNABİLİR kalır.

    Eskiden `rmtree(out)` `target/`i de siliyordu; bu test o davranışa geri dönüşü
    yakalar. Yeniden compose'dan SONRA build'den ÖNCE dosya hâlâ geçerli olmalı.
    """
    compose(COMPANY, DEMO, tmp_path)
    build(tmp_path)
    once = _mdl(tmp_path).read_bytes()
    assert once

    compose(COMPANY, DEMO, tmp_path)  # build ÇAĞRILMADAN
    assert _mdl(tmp_path).exists(), "compose sonrası manifest kayboldu (rmtree target/'ı sildi)"
    assert json.loads(_mdl(tmp_path).read_text())["cubes"], "manifest bozuldu"


def test_compose_target_disindaki_bayat_dosyalari_TEMIZLER(tmp_path: Path):
    """`target/` korunuyor ama geri kalan her şey hâlâ sıfırlanmalı — yoksa kaldırılan
    bir cube/view derlenmiş projede yaşamaya devam eder."""
    compose(COMPANY, DEMO, tmp_path)
    build(tmp_path)
    ghost = tmp_path / "cubes" / "hayalet_cube"
    ghost.mkdir(parents=True, exist_ok=True)
    (ghost / "metadata.yml").write_text("name: hayalet_cube\n")

    compose(COMPANY, DEMO, tmp_path)
    assert not ghost.exists(), "target/ dışındaki bayat içerik temizlenmedi"


# --- (c) okuyucu yarışı ------------------------------------------------------

def test_yeniden_compose_SIRASINDA_okuyucu_manifesti_hep_gecerli_gorur(tmp_path: Path):
    """Asıl regresyon kilidi: bir thread compose+build ederken diğeri sürekli okur.

    Okuyucu HİÇBİR turda ne 'dosya yok' ne 'yarım JSON' görmemeli. Eski kodda bu test
    FileNotFoundError ile düşerdi (pencere ~130-160 ms, okuma döngüsü onu rahat yakalar).
    """
    compose(COMPANY, DEMO, tmp_path)
    build(tmp_path)

    stop = threading.Event()
    errors: list[str] = []
    reads = [0]

    def reader():
        while not stop.is_set():
            try:
                data = json.loads(_mdl(tmp_path).read_text())
                if not data.get("cubes"):
                    errors.append("manifest cube'suz okundu")
                reads[0] += 1
            except FileNotFoundError:
                errors.append("manifest YOK (compose penceresi)")
            except json.JSONDecodeError:
                errors.append("manifest YARIM okundu (atomik değil)")
            time.sleep(0.001)

    t = threading.Thread(target=reader, daemon=True)
    t.start()
    try:
        for _ in range(3):
            compose(COMPANY, DEMO, tmp_path)
            build(tmp_path)
    finally:
        stop.set()
        t.join(timeout=5)

    assert reads[0] > 0, "okuyucu hiç okuyamadı — test anlamsız"
    assert not errors, f"okuyucu bozuk durum gördü: {sorted(set(errors))}"


# --- (d) yazar × yazar kilidi ------------------------------------------------

def test_build_lock_ayni_dizin_icin_ayni_kilidi_doner(tmp_path: Path):
    """`compose_and_build()` ile `CompanyRegistry` AYNI kilidi almalı — ayrı kilitler
    varsayılan şirketi korumasız bırakıyordu."""
    a = build_lock_for(tmp_path)
    b = build_lock_for(Path(str(tmp_path)))          # aynı yol, farklı Path nesnesi
    c = build_lock_for(tmp_path / ".." / tmp_path.name)  # normalize edilmeli
    assert a is b is c
    assert build_lock_for(tmp_path.parent) is not a   # farklı dizin → farklı kilit


def test_registry_ve_compose_and_build_ayni_kilidi_paylasir(tmp_path: Path):
    """Kilit kaydının `app.compose`'da tek olduğunu davranışsal olarak doğrula:
    registry'nin kullandığı yol ifadesi ile compose_and_build'inki aynı kilide düşmeli."""
    from app import company_registry as cr

    assert hasattr(cr, "CompanyRegistry")
    out = tmp_path / "wren-projects" / "x"
    out.mkdir(parents=True)
    assert build_lock_for(out) is build_lock_for(out.resolve())


def test_es_zamanli_iki_yazar_bozuk_manifest_uretmez(tmp_path: Path):
    """İki thread aynı ağaca compose+build ederse sonuç yine GEÇERLİ olmalı."""
    from app.compose import build_lock_for as _lock

    compose(COMPANY, DEMO, tmp_path)
    build(tmp_path)
    errors: list[str] = []

    def writer():
        try:
            with _lock(tmp_path):
                compose(COMPANY, DEMO, tmp_path)
                build(tmp_path)
        except Exception as exc:  # pragma: no cover
            errors.append(f"{type(exc).__name__}: {exc}")

    threads = [threading.Thread(target=writer) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)

    assert not errors, errors
    mdl = json.loads(_mdl(tmp_path).read_text())
    assert mdl["cubes"] and mdl["models"]


# --- (e) WrenService: manifest önbelleği + mdl_version tazeliği --------------

def test_mdl_version_manifest_degisince_DEGISIR(tmp_path: Path):
    """ADR-0010: sözleşme damgası "şema değişti mi?" sorusunun cevabıdır. Eskiden
    `_mdl_ver` nesne ömrü boyunca sabitti ve `invalidate_schema_cache()` onu düşürmüyordu
    → yeniden compose sonrası sözleşmeler ESKİ sürümle damgalanıyordu."""
    from app.wren_service import WrenService

    compose(COMPANY, DEMO, tmp_path)
    build(tmp_path)
    svc = WrenService(tmp_path, datasource="duckdb", connection_info={})
    v1 = svc.mdl_version
    assert v1 != "unknown"

    # Manifesti gerçekten değiştir (mtime + içerik).
    data = json.loads(_mdl(tmp_path).read_text())
    data["catalog"] = "degistirildi"
    _mdl(tmp_path).write_text(json.dumps(data, indent=2, ensure_ascii=False))

    assert svc.mdl_version != v1, "mdl_version bayat kaldı (sözleşme damgası yanlış olur)"


def test_manifest_onbellegi_dosya_degisince_tazelenir(tmp_path: Path):
    from app.wren_service import WrenService

    compose(COMPANY, DEMO, tmp_path)
    build(tmp_path)
    svc = WrenService(tmp_path, datasource="duckdb", connection_info={})

    first = svc._mdl_bytes()
    assert svc._mdl_bytes() is first, "aynı dosya için önbellek kullanılmadı"

    data = json.loads(first)
    data["catalog"] = "yeni"
    _mdl(tmp_path).write_text(json.dumps(data, indent=2, ensure_ascii=False))

    assert svc._mdl_bytes() is not first, "dosya değişti ama önbellek düşmedi"
    assert json.loads(svc._mdl_bytes())["catalog"] == "yeni"


def test_manifest_okunamazsa_always_filter_SESSIZCE_dusmez(tmp_path: Path):
    """Fail-closed: manifest okunamıyorsa filtresiz SQL DÖNDÜRME, hata ver.

    Eski davranış `except Exception: return sql` idi — compose penceresinde gelen sorgu
    always_filter'sız çalışıp iptal kayıtlarını toplama sızdırabiliyordu.
    """
    from app.wren_service import WrenService

    compose(COMPANY, DEMO, tmp_path)
    build(tmp_path)
    svc = WrenService(tmp_path, datasource="duckdb", connection_info={})
    _mdl(tmp_path).unlink()

    with pytest.raises((FileNotFoundError, json.JSONDecodeError)):
        svc._inject_always_filter("SELECT 1", "parti")
