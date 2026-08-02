"""FAZ 4.2 — terfi kuyruğunda DIFF ÖNİZLEMESİ: onaylamadan önce ne değişeceğini gör.

Plan *"Omni tarzı checkbox + diff onayı"* istiyordu ve `MeasureCandidate` altyapısının
inceleme/onay/blast-radius/altın-vaka/`dry_plan` yarısı ZATEN vardı. Eksik olan yarı şuydu:
inceleyen kişi onaylıyor ve MDL değişikliğini ancak **olup bittikten sonra** görebiliyordu.
Yanlış bir ölçünün blast-radius'u kategorik olarak büyüktür (yeni SQL/join/agregasyon →
çift sayım, grain uyuşmazlığı) ve inceleme ancak GÖRÜLEN bir değişiklik üzerinde yapılabilir.

İki tasarım kararı bu dosyada kilitlenir:

1. **Diff, üretimdeki yazıcının KENDİSİ çalıştırılarak üretilir** (geçici bir kopya
   üzerinde), yeniden uygulanmış bir taklitle değil. Taklit zamanla asıl yazıcıdan ayrışır
   ve inceleyene yalan söyler — önizlemenin tek işi doğru olmaktır.
2. **Önizleme hiçbir şey değiştirmez.** `resolve_cube_yaml_for_edit` pack'ten gelen bir
   cube'u şirket katmanına KOPYALAR; önizleme bunu yapamaz, çünkü inceleyen vazgeçtiğinde
   geride yeni bir dosya kalmamalıdır. Bunun için yan etkisiz ikizi
   (`cube_yaml_source_for_preview`) yazıldı.
"""

from __future__ import annotations

import pytest

from tests.conftest import make_tenant_user
from tests.test_auth import _login_as
from tests.test_measure_promote import _TEST_CUBE, _TEST_MEASURE, clean_promote_artifacts  # noqa: F401

_EXPR = "MAX(CASE WHEN ilk_seferde_tamam = 0 THEN kg ELSE 0 END)"


def _aday(company="demo-boyahane") -> str:
    import json

    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import MeasureCandidate

    with Session(engine) as s:
        c = MeasureCandidate(
            company=company, question="önizleme testi: parti başına maks fire kg",
            sql=f"SELECT {_EXPR} FROM partiler",
            sample_rows_json=json.dumps({"columns": ["max_fire"], "rows": [[12.5]]}),
        )
        s.add(c)
        s.commit()
        s.refresh(c)
        return str(c.id)


def _govde(**kw):
    return {"cube": _TEST_CUBE, "measure_name": _TEST_MEASURE, "expression": _EXPR,
            "type": "DOUBLE", "synonyms": ["önizleme geçici ölçü"],
            "lower_is_better": True, **kw}


@pytest.fixture
def okuyucu(client):
    """`analyst` — `measure:read` var, `measure:approve` YOK. Önizleme hiçbir şey
    değiştirmediği için bu role açık olmalı."""
    make_tenant_user("faz42-analyst@dima.local", "faz42-parola-1", "analyst")
    return _login_as(client, "faz42-analyst@dima.local", "faz42-parola-1")


def test_analyst_onizleyebilir(okuyucu, clean_promote_artifacts):
    r = okuyucu.post(f"/measures/candidates/{_aday()}/preview", json=_govde())
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["changed"] and d["diff"]


def test_diff_EKLENEN_olcuyu_gosterir(okuyucu, clean_promote_artifacts):
    d = okuyucu.post(f"/measures/candidates/{_aday()}/preview", json=_govde()).json()
    eklenen = [s for s in d["diff"].splitlines() if s.startswith("+") and not s.startswith("+++")]
    metin = "\n".join(eklenen)
    assert _TEST_MEASURE in metin, metin
    assert "ilk_seferde_tamam" in metin, metin
    assert "önizleme geçici ölçü" in metin, metin


def test_diff_INCELENEBILIR_kalir(okuyucu, clean_promote_artifacts):
    """ASIL KAPI. Bir ölçü eklemek dosyanın TAMAMINI değiştirmemeli.

    Ölçüldü (düzeltme öncesi): 266 satırlık `parti/metadata.yml`'ın **266 satırı da**
    değişmiş görünüyordu — `mdl_writer._yaml()` liste girintisini `  - x` diye sabitlemişti,
    repo dosyaları ise `- x` kullanıyor. İçerik aynıydı, yalnız her satır 2 boşluk kaymıştı.
    Kimse fark etmemişti çünkü kimse diff'e bakmıyordu; bu önizleme onu görünür kıldı.
    Girinti artık düzenlenen dosyadan sezildiği için diff birkaç satıra indi.

    Sıfır artık talep EDİLMİYOR: kaynak dosyada sarılmış (çok uzun) ifadeler ruamel
    tarafından tek satıra açılıyor. İçerik kaybı yok, gürültü sınırlı — bunu kovalamak
    ruamel'in satır-sarma sezgisine karşı sonsuz bir savaş olurdu. Ölçülen şey İNCELENEBİLİRLİK.
    """
    d = okuyucu.post(f"/measures/candidates/{_aday()}/preview", json=_govde()).json()
    from pathlib import Path

    toplam = len(Path(d["yaml_path"]).read_text(encoding="utf-8").splitlines())
    degisen = [s for s in d["diff"].splitlines()
               if (s.startswith(("+", "-")) and not s.startswith(("+++", "---")))]
    assert len(degisen) < toplam * 0.10, (
        f"{toplam} satırlık dosyada {len(degisen)} satır değişti — biçimlendirme gürültüsü "
        f"incelemeyi imkânsız kılar:\n" + "\n".join(degisen[:20]))


def test_diff_ICERIK_KAYBETMEZ(okuyucu, clean_promote_artifacts):
    """Küçük diff yetmez — küçük OLUP bir şey silmemeli de. Var olan her ölçü/boyut adı
    yazımdan sonra da durmalı."""
    import re
    from pathlib import Path

    d = okuyucu.post(f"/measures/candidates/{_aday()}/preview", json=_govde()).json()
    kaynak = Path(d["yaml_path"]).read_text(encoding="utf-8")
    adlar = set(re.findall(r"^\s*-?\s*name:\s*(\S+)", kaynak, re.M))
    silinen = "\n".join(s for s in d["diff"].splitlines()
                        if s.startswith("-") and not s.startswith("---"))
    kaybolan = [a for a in adlar if f"name: {a}" in silinen]
    assert not kaybolan, f"diff var olan tanımları siliyor: {kaybolan}"


def test_onizleme_DOSYA_YARATMAZ(okuyucu, clean_promote_artifacts):
    """En kritik kapı: `parti` pack katmanında yaşar, yani onay onu şirket katmanına
    kopyalar. Önizleme aynı yolu kullansaydı "bir bakayım" demek kalıcı bir override
    yaratırdı — ve o dosya bundan sonra bu tenant için pack'i EZERDİ."""
    hedef = clean_promote_artifacts["company_yaml"]
    assert not hedef.exists()
    okuyucu.post(f"/measures/candidates/{_aday()}/preview", json=_govde())
    assert not hedef.exists(), f"önizleme {hedef} dosyasını YARATTI"


def test_onizleme_ALTIN_VAKA_dosyasina_dokunmaz(okuyucu, clean_promote_artifacts):
    once = clean_promote_artifacts["cases_path"].read_text(encoding="utf-8")
    okuyucu.post(f"/measures/candidates/{_aday()}/preview", json=_govde())
    assert clean_promote_artifacts["cases_path"].read_text(encoding="utf-8") == once


def test_onizleme_aday_DURUMUNU_degistirmez(okuyucu, clean_promote_artifacts):
    cid = _aday()
    okuyucu.post(f"/measures/candidates/{cid}/preview", json=_govde())
    assert okuyucu.get(f"/measures/candidates/{cid}").json()["status"] == "draft"


def test_sirket_katmanina_tasinma_UYARISI(okuyucu, clean_promote_artifacts):
    """Diff'te GÖRÜNMEYEN ama bilinmesi gereken sonuç: onay, pack'ten gelen cube'u bu
    tenant'ın şirket katmanına taşır. İnceleyen bunu diff'e bakarak anlayamaz."""
    d = okuyucu.post(f"/measures/candidates/{_aday()}/preview", json=_govde()).json()
    assert d["creates_company_override"] is True


def test_sozdizimi_bozuk_expression_ONIZLEMEDE_yakalanir(okuyucu, clean_promote_artifacts):
    """Önizleme onayın KURU KOŞUMUDUR — onayın reddedeceği her şeyi o da reddetmeli,
    yoksa inceleyen "diff güzel" deyip onayda patlar."""
    r = okuyucu.post(f"/measures/candidates/{_aday()}/preview",
                     json=_govde(expression="SUM(((("))
    assert r.status_code == 400 and "dry_plan" in r.text


def test_UYDURMA_KOLON_gecer_bu_ONAYIN_bilinen_zaafi(okuyucu, clean_promote_artifacts):
    """Önizleme, onayın zaafını da AYNEN paylaşmalı — daha SIKI olmamalı.

    `dry_plan` `strict_mode=False` ile çalışıyor ve kolon VARLIĞINI denetlemiyor
    (MIMARI.md §5: *"dry_plan'ı doğrulama kapısı sanma"*). Yani uydurma kolonlu bir ifade
    hem önizlemeden hem ONAYDAN geçer ve müşteri DB'sinde patlar. Bu, önizlemenin değil
    ONAYIN kusurudur ve ayrı bir tur ister (üye taraması / `LIMIT 0` gerçek çalıştırma).

    Test burada duruyor ki önizleme onaydan AYRIŞMASIN: önizleme reddedip onay kabul
    etseydi inceleyen "önizleme bozuk" der ve önizlemeye güvenmeyi bırakırdı; tersi
    olsaydı zaten bugünkü durum sürerdi. İkisi de aynı kararı vermeli — kusur ortak
    olsa bile.
    """
    r = okuyucu.post(f"/measures/candidates/{_aday()}/preview",
                     json=_govde(expression="SUM(boyle_bir_kolon_yok)"))
    assert r.status_code == 200, (
        "önizleme uydurma kolonu reddetti ama onay etmiyor — ikisi ayrıştı. Eğer bu "
        "gerçekten düzeltildiyse ONAY tarafında da düzeltilmiş olmalı; bu testi güncelle.")


def test_var_olan_olcu_adi_ONIZLEMEDE_catisir(okuyucu, clean_promote_artifacts):
    r = okuyucu.post(f"/measures/candidates/{_aday()}/preview",
                     json=_govde(measure_name="toplam_fire_kg"))
    assert r.status_code == 409, r.text


def test_bilinmeyen_cube_reddedilir(okuyucu, clean_promote_artifacts):
    r = okuyucu.post(f"/measures/candidates/{_aday()}/preview", json=_govde(cube="yok_boyle"))
    assert r.status_code == 400


def test_baska_tenantin_adayi_GORULEMEZ(okuyucu, clean_promote_artifacts):
    """Kiracı izolasyonu önizlemede de geçerli — yeni uç nokta `_get_candidate`'in
    kapsam süzgecini atlamamalı."""
    r = okuyucu.post(f"/measures/candidates/{_aday(company='baska-sirket')}/preview",
                     json=_govde())
    assert r.status_code in (403, 404), r.text


def test_ONIZLEME_ile_ONAY_ayni_sonucu_uretir(client, okuyucu, clean_promote_artifacts):
    """Önizlemenin BİRİCİK sözleşmesi: gösterdiği diff, onayın gerçekten yazacağı şey
    olmalı. Bu test ikisini yan yana koyar — önizleme alınır, sonra onay çalıştırılır ve
    ortaya çıkan dosya, önizlemedeki diff'in ürettiği satırları taşımalıdır."""
    cid = _aday()
    onizleme = okuyucu.post(f"/measures/candidates/{cid}/preview", json=_govde()).json()

    make_tenant_user("faz42-admin@dima.local", "faz42-parola-1", "admin")
    admin = _login_as(client, "faz42-admin@dima.local", "faz42-parola-1")
    r = admin.post(f"/measures/candidates/{cid}/approve", json={
        **_govde(),
        "golden_case": {"id": "faz42-onizleme-vaka", "q": "önizleme testi",
                        "shape": {"cube": _TEST_CUBE, "measures": [_TEST_MEASURE]}}})
    assert r.status_code == 200, r.text

    yazilan = clean_promote_artifacts["company_yaml"].read_text(encoding="utf-8")
    eklenen = [s[1:] for s in onizleme["diff"].splitlines()
               if s.startswith("+") and not s.startswith("+++")]
    assert eklenen, "önizleme hiç ekleme göstermedi"
    eksik = [s for s in eklenen if s.strip() and s not in yazilan]
    assert not eksik, (
        "önizleme onaydan AYRIŞTI — inceleyene gösterilmeyen satırlar yazıldı:\n"
        + "\n".join(eksik))
