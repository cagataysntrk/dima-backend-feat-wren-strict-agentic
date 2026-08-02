"""FAZ B — compose çıktısı MOTORUN kendi doğrulayıcısından geçiyor (`context.validate_project`).

## Ölçülen boşluk

`wren.context.validate_project` motorda **hazır duruyordu** ve dokuz yapısal kuralı
denetliyordu — model adı/kolonu, `table_reference` XOR `ref_sql`, ilişkilerin var olan
modelleri göstermesi, çift ad, view'ın statement'ı, `primary_key`'in kolonlar arasında
bulunması… Compose çıktısı bunların **hiçbirinden geçmiyordu**.

Sonuç: bozuk bir ağaçtan MDL üretiliyor ve hata **sorgu anında** ortaya çıkıyordu.
MIMARI §5 zaten kaydediyor: *"`dry_plan`'ı doğrulama kapısı sanma — kolon varlığını
denetlemiyor."* Yani build zamanında yakalanmayan bir yapısal kusur, üretim zamanında
kullanıcının yüzüne çıkar.

**Kendi doğrulayıcımızı YAZMADIK.** MIMARI §5: *"motor zaten yapıyorsa yazma."* Bu kapı
bir doğrulayıcı değil, var olan doğrulayıcının **çağrıldığı yerdir**.

## Ölçüm (2 Ağustos 2026)

Dört demo projesinin **dördü de 0 hata / 0 uyarı** — bu kapıyı bugün açmak hiçbir meşru
yolu kırmıyor. Aynı disiplin `WrenConfig(strict_mode=True)` açılırken de uygulanmıştı:
*ölçmeden kısıtlama getirme.*
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.compose import ProjectValidationError, dogrula


def test_DERLENMIS_proje_temiz():
    """ASIL KAPI. Compose çıktısı motorun yapısal kurallarını geçmeli."""
    from app.config import get_settings

    rapor = dogrula(get_settings().resolved_project_dir())
    assert rapor["ok"] is True and rapor["errors"] == 0


def test_TUM_sirketler_temiz():
    """Kapı yalnız aktif şirkette değil, dört demo şirketinde de geçerli olmalı —
    aksi halde bir tenant'ın build'i kırılır ve bunu ancak o tenant açılınca görürüz."""
    kok = Path("demo/wren-projects")
    if not kok.is_dir():
        pytest.skip("derlenmiş proje ağacı yok")
    bakilan = 0
    for p in sorted(kok.iterdir()):
        if not (p / "wren_project.yml").exists():
            continue
        bakilan += 1
        assert dogrula(p)["errors"] == 0, f"{p.name} yapısal hata taşıyor"
    assert bakilan >= 1, "hiç proje taranmadı — test bir şey korumuyor"


def test_BOZUK_proje_MDL_URETMEZ(tmp_path):
    """FAIL-CLOSED. Yapısal olarak geçersiz bir projeden MDL üretmek, sonraki her katmana
    bozuk bir zemin verir. Build zamanında durmak, üretim zamanında yanlış cevap
    vermekten kesinlikle iyidir."""
    (tmp_path / "wren_project.yml").write_text(
        "catalog: k\nschema: s\ndata_source: duckdb\n", encoding="utf-8")
    models = tmp_path / "models"
    models.mkdir()
    # Kolonu OLMAYAN model → motorun 1. kuralı.
    (models / "bos.yml").write_text("name: bos\ntable_reference:\n  table: bos\n",
                                    encoding="utf-8")
    with pytest.raises(ProjectValidationError) as exc:
        dogrula(tmp_path)
    assert "YAPISAL HATA" in str(exc.value)
    assert "MDL üretilmedi" in str(exc.value), "gerekçe mesajda görünmeli"


def test_DOGRULAYICI_patlarsa_build_KIRILMAZ(monkeypatch, tmp_path):
    """Bu kapı bir EK GÜVENCEDİR, zorunlu bir bileşen değil: doğrulayıcının kendisi
    patlarsa build durmaz — ama sessiz de kalmaz (ADR-0020)."""
    import wren.context as wc

    def _patla(_p):
        raise RuntimeError("doğrulayıcı bozuk")

    monkeypatch.setattr(wc, "validate_project", _patla)
    rapor = dogrula(tmp_path)
    assert rapor["ok"] is None, "doğrulanamadı ↦ 'geçti' DEĞİL, 'bilinmiyor'"


def test_compose_RAPORU_dondurur():
    """`compose_and_build` doğrulama sonucunu bilgi sözlüğünde taşımalı — build'in
    doğrulanıp doğrulanmadığı görünür olsun."""
    import inspect

    from app import compose as c

    kaynak = inspect.getsource(c.compose_and_build)
    assert "dogrula(out)" in kaynak, "doğrulama compose_and_build'e bağlanmamış"
    assert "validation" in kaynak, "doğrulama sonucu rapora yazılmıyor"


def test_KENDI_dogrulayicimizi_yazmadik():
    """MIMARI §5: *motor zaten yapıyorsa yazma.* Bu modül motorun doğrulayıcısını
    ÇAĞIRIR; kural gövdesini kopyalarsa zamanla ondan ayrışır."""
    import inspect

    from app import compose as c

    kaynak = inspect.getsource(c.dogrula)
    assert "validate_project" in kaynak
    # YALNIZ GÖVDE denetlenir: docstring motorun kurallarını ANLATIR (ve anlatmalıdır),
    # ama kod onları UYGULAMAMALIDIR. Docstring'i de eleyen bir kontrol, belgeyi
    # cezalandırıp asıl kusuru (kopyalanmış kural) kaçırırdı.
    # `inspect.getdoc` DEDENT eder → kaynakla birebir eşleşmez. Ham `__doc__` girintiyi
    # olduğu gibi taşır ve çıkarılabilir.
    govde = kaynak.replace(c.dogrula.__doc__ or "", "")
    for kural in ("table_reference", "ref_sql", "primary_key"):
        assert kural not in govde, f"motorun kuralı ({kural}) burada tekrar yazılmış"
