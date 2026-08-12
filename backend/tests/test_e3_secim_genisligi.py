r"""🔴🔴 `§E3` — **TARAMA BEYANI DÖRT YERİN BİRİNDEYDİ.**

## Ölçülen boşluk (denetim ajanı, ⟳ 2026-08-12)

`stats.tarama_beyani`'nin **tek** çağrı yeri vardı: `interpret.py:427` (aykırılık
sinyali, `n_aday = len(rows)`). Ajan **dört** tarama yeri saydı; üçü hiçbir şey beyan
etmiyordu:

| # | tarama yeri | seçim kuralı | beyan |
|---|---|---|---|
| 1 | `interpret._signals` | `\|z\| ≥ 2` **kesimi** | ✅ vardı |
| 2 | `kok_neden._en_ayristiran` | aday kırılımlar arasında **max yayılım** | 🔴 yoktu |
| 3 | `kok_neden.derinles` | ikinci kırılım × alt-segment (**bileşik**) | 🔴 yoktu |
| 4 | `kok_neden.toplam_turu` | kırılımdaki **en büyük** segment | 🔴 yoktu |
| 5 | `contribution.arastir` | `MAX_BOYUT` kırılım × bulgu süpürmesi | 🔴 yoktu |

## Neden `tarama_beyani` oraya **doğrudan** bağlanamazdı

Cümlesi bir **z-kesimine** bağlıdır (*«N aday tarandı, M'i `|z| ≥ 2` eşiğini geçti»*) ve
şans payını o eşiğin normal dağılımdaki oranından okur. 2–5'te **eşik yok**, bir
`max(...)` **seçimi** var. Orada o cümleyi basmak, olmayan bir eşiği varmış gibi
yazmak olurdu — *doğru hesaplanmış bir sayı yanlış bir cümlede hâlâ yanlıştır.*

✅ Çözüm: **aynı sahibe ikinci bir kip** (`stats.secim_beyani`), rakip bir cümle sahibi
değil (`KAT-1`). Genişliği yazar, **şans payını yazmaz** ve **neden yazmadığını söyler**
— `§E2`'de forecast, `§E3`'te BH için verilen kararın aynısı.

⚠ Ve taranan sayı **dilimlenmiş** listeden okunur: `_adaylar` 20 olsa da yalnız
`AZAMI_ADAY` tanesi koşulur. Büyük sayıyı yazmak taramayı olduğundan **geniş**
gösterirdi — *bir tavanın pratikte var olması, ilan edilmiş olması demek değildir.*
"""

from __future__ import annotations

import inspect

from app import contribution, kok_neden
from app.stats import ASGARI_ADAY_SECIM, secim_beyani, tarama_beyani

_BOYUT, _OLCU = "kaynak", "toplam_enpg"
_CQ = {"cube": "enerji_sapma", "measures": [_OLCU], "dimensions": [_BOYUT], "filters": []}
_META = {"name": "enerji_sapma", "lower_is_better": [_OLCU],
         "measure_expressions": {_OLCU: f"SUM({_OLCU})"},
         "dimensions": [_BOYUT], "measures": [_OLCU]}


def _kos(degerler: list[float]):
    satirlar = [{_BOYUT: f"S{i}", _OLCU: v} for i, v in enumerate(degerler)]
    return lambda cq: list(satirlar)


def test_SECIM_BEYANI_SANS_PAYI_UYDURMUYOR():
    """🔴 **ASIL AYRIM.** `tarama_beyani` bir eşiğin şans payını yazar (`|z|≥2` →
    ~%4,6); `secim_beyani` **yazmaz** ve yazmadığını **söyler**. Bir max-seçiminde o
    payı hesaplamak, adayların dağılımı hakkında **ölçülmemiş** bir varsayım dayatmak
    olurdu."""
    s = secim_beyani(7, "en büyük segment")
    assert "7 aday" in s, f"⊘ genişlik yazılmıyor: {s!r}"
    assert "%" not in s, (
        f"🔴 max-seçimi beyanında bir YÜZDE var — şans payı uydurulmuş olabilir:\n{s!r}")
    assert "eşik testi değil" in s, (
        f"🔴 beyan, neden şans payı vermediğini SÖYLEMİYOR — okuyucu eksikliği bir "
        f"unutma sanar:\n{s!r}")
    # ⊙ Kardeş kip hâlâ eşiği ve payını yazıyor — düzeltme onu yutmamalı.
    z = tarama_beyani(100, 6, 2.0)
    assert "|z| ≥ 2" in z and "%" in z, f"🔴 z-kesimi beyanı bozuldu:\n{z!r}"


def test_TEK_ADAY_BIR_SECIM_DEGILDIR():
    """⚠ `§101.1` — *«bir yanlış-pozitif, kusurdan pahalıdır.»* Tek adaylı bir
    *«seçim»*e uyarı basmak, her raporun altına anlamsız bir cümle düşürürdü."""
    assert secim_beyani(1, "en büyük segment") == ""
    assert secim_beyani(ASGARI_ADAY_SECIM, "x") != ""
    assert secim_beyani(9, "") == "", "⊘ ölçütsüz beyan bir şey anlatmaz"


def test_TOPLAM_TURU_SECIMIN_GENISLIGINI_SOYLUYOR():
    """🔴 `toplam_turu` *«N segment ölçüldü»* diyordu — bu bir **kapsam** cümlesidir.
    *«Bunların en büyüğü seçildi»* ise bir **seçimdir** ve genişliği ayrı bir bilgidir.
    """
    r = kok_neden.toplam_turu(_CQ, _META, kos=_kos([100.0, 50.0, 30.0, 20.0]))
    assert r, "⊘ ölçüm tabanı çöktü: `toplam_turu` cümle üretmedi"
    m = " ".join(str(a) for a in (r.get("adimlar") or []))
    assert "4 aday arasından" in m, (
        f"🔴 en büyük segment seçiminin GENİŞLİĞİ beyan edilmiyor:\n{m[:400]}")
    assert "eşik testi değil" in m


def test_ARASTIR_TARANAN_HIPOTEZI_BEYAN_EDIYOR_yapisal():
    """🔴 `arastir` *«neye bakmadım»*ı (`taranmayan_boyut`/`taranmayan_adlar`) sayıyordu
    ama *«kaç aday arasından seçtim»*i **hiç** söylemiyordu — `rank_dimensions` bir
    seçimdir.

    ⚠ Yüklem **yapısal** (`ast`): `arastir` gerçek bir `service` + motor ister; ürünü
    ortam kurulumuna bağlamak, `§E3`'ün kapısını `§F16`'nın düştüğü yere düşürürdü
    (*ortam ≠ ürün*).
    """
    import ast
    import textwrap

    agac = ast.parse(textwrap.dedent(inspect.getsource(contribution.arastir)))
    adlar = {n.id for n in ast.walk(agac) if isinstance(n, ast.Name)}
    assert "_secim_beyani" in adlar, (
        "🔴 `arastir` tarama genişliğini artık beyan etmiyor — `taranmayan_*` alanları "
        "**bakılmayanı** sayar, taranan hipotezi değil.")
    anahtarlar = {k.value for n in ast.walk(agac) if isinstance(n, ast.Dict)
                  for k in n.keys if isinstance(k, ast.Constant)}
    assert "tarama_beyani" in anahtarlar, (
        "🔴 beyan üretiliyor ama DÖNDÜRÜLMÜYOR — üretilip taşınmayan bir alan, hiç "
        "üretilmemiş gibidir (`§E2`'nin ölçtüğü kusur).")


def test_ALAN_SEMADA_VAR_tel_ustunde_dusmuyor():
    """🔴🔴 `§E2`'nin dersi burada **tekrarlanmasın**: dört alan üretilip Pydantic
    sınırında sessizce siliniyordu. Bir alanı üretmek, onu taşıyan sözleşmeye yazmakla
    tamamlanır."""
    from app.schemas import ContributionResponse

    assert "tarama_beyani" in ContributionResponse.model_fields, (
        "🔴 `tarama_beyani` şemada YOK — `/ask/contribution` onu sessizce düşürür.")


def test_TARANAN_SAYI_DILIMDEN_OKUNUYOR_yapisal():
    """⚠ `AZAMI_ADAY` tavanı: 20 aday olsa da yalnız 3'ü koşulur. Beyanda 20 yazmak,
    taramayı olduğundan **geniş** göstermek olurdu — *bir tavanın pratikte var olması,
    ilan edilmiş olması demek değildir.*

    Yüklem yapısal: `_en_ayristiran` çağrılarında dilim **adlandırılmış** bir değişkene
    alınmalı ve beyan **onu** saymalı; ham aday listesini saymamalı.
    """
    kaynak = inspect.getsource(kok_neden)
    assert "_secim_beyani(len(_tarananlar)" in kaynak, (
        "🔴 seçim beyanı DİLİMLENMEMİŞ aday listesini sayıyor olabilir — taranan sayı "
        "`[:AZAMI_ADAY]` sonrası okunmalı.")
    assert "_secim_beyani(len(_adaylar)" not in kaynak, (
        "🔴 ham aday listesi sayılıyor: tavan uygulanmadan önceki sayı beyan ediliyor.")


def test_KAPSAM_DORT_YERIN_DORDU_yapisal():
    """🔴 **KAPSAM KİLİDİ.** Bir sonraki tur bir tarama yerini sessizce beyan-sız
    bırakmasın: `kok_neden` **üç**, `contribution` **bir** çağrı taşımalı.

    ⊘ *«Kapı yok» ≠ «boşluk var»* dersinin tersi: burada boşluk **ölçüldü** ve kapı
    onu **sayıyla** kilitliyor.
    """
    kn = inspect.getsource(kok_neden).count("_secim_beyani(")
    ct = inspect.getsource(contribution).count("_secim_beyani(")
    assert kn >= 3, f"🔴 `kok_neden`'de seçim beyanı {kn} yerde (beklenen ≥3)"
    assert ct >= 1, f"🔴 `contribution`'da seçim beyanı {ct} yerde (beklenen ≥1)"
