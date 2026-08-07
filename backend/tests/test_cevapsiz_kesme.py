"""🔴 `G3.4` — **CEVAPSIZ KESME ORANI**: merdiveni erken bitiren tur oranı.

## Ölçüt uydurulmadı — yasağın kendi cümlesinden türetildi

`MIMARI §5`'in **18. yasağı**:

> *"Merdiveni yalnız **pozitif cevap** ya da kullanıcının **açık `yol_siniri`**'si
> bitirebilir."*

Ölçüt bunun birebir karşılığıdır:

    cevapsız kesme  =  cevap YOK  ∧  kullanıcı durdurmadı  ∧  Discovery hiç koşmadı

## Üçüncü şart AYIRT EDİCİDİR — ve olmadan ölçüt yanlış olurdu

Merdiven **sonuna kadar koşup** cevap bulamadıysa bu bir **kesme değil**, bir **kapsam
sınırıdır**. Kesme, altta çalışabilir bir basamak **varken** durmaktır.

*Bir kaybı ölçen metrik, kaybın nedenini ayırt etmiyorsa iki farklı sorunu tek sayıya
çöker ve ikisini de görünmez yapar.*

## Neden `G3`'ün ön koşulu

`G3`'ün kararı (**askıda**, reddedilmiş değil) iki ortamlı bir ölçüme bağlı: geri alma
`rule` sağlayıcısıyla ölçülmüştü — *"garsonun yerine mutfağın en aptal yedeğini
koyunca"*. Ama o karşılaştırmayı yapabilmek için **önce kesmenin kendisini sayabilmek**
gerekiyor. Bu ölçüt olmadan `G3.1`/`G3.2` bir sayı üretemez.
"""

from __future__ import annotations

from lab.nl_corpus import _cevapsiz_kesme


def test_POZITIF_CEVAP_kesme_DEGIL():
    """Meşru bitiş #1: bir cevap üretildi."""
    assert not _cevapsiz_kesme({"source": "cube", "trace": []})
    assert not _cevapsiz_kesme({"source": "llm:gemini", "trace": []})


def test_KULLANICI_DURDURDUYSA_kesme_DEGIL():
    """Meşru bitiş #2: kullanıcının **açık** talimatı.

    ⚠ *"Yalnız deterministik"* diyen kullanıcı yine kesilir — **ama kullanıcı öyle dediği
    için, bir yazım tahmini öyle dediği için değil.*"""
    assert not _cevapsiz_kesme({"source": None, "yol_siniri": "deterministik",
                                "trace": []})


def test_DISCOVERY_KOSTUYSA_kesme_DEGIL():
    """🔴 Ayırt edici şart: merdiven **sonuna kadar** koştu ve cevap bulamadı.
    Bu bir **kapsam sınırıdır**, bir kesme değil."""
    assert not _cevapsiz_kesme({
        "source": None,
        "trace": ["route: R1", "Discovery: VQR few-shot ile ham-SQL üretimi",
                  "Discovery SQL üretimi başarısız"]})


def test_DISCOVERY_HIC_KOSMADIYSA_KESME():
    """🔴 Asıl vaka: bir dal cevap üretmeden **döndü** ve altındaki basamak hiç çalışmadı.

    Yol haritasının ölçtüğü kusur tam bu: *"13 turun dördünde yazım-benzerliği kısa
    devresi turu öldürüyor."*"""
    assert _cevapsiz_kesme({
        "source": None,
        "trace": ["route: R1", "«artti» yerine «parti» mi demek istedin?"]})


def test_IZSIZ_CEVAP_da_KESME():
    """İz hiç yoksa Discovery de koşmamıştır — güvenli taraf **kesme** saymaktır.
    *Şüphede bir kaybı saymak, onu görmezden gelmekten iyidir.*"""
    assert _cevapsiz_kesme({"source": None})
    assert _cevapsiz_kesme({"source": None, "trace": []})


def test_OLCUT_YASAGIN_UC_SARTINI_da_TASIYOR():
    """⚠ `yol_siniri` bu korpusta hiç gönderilmiyor, yani ikinci şart bugün **daima**
    sağlanıyor. Yine de koşulda yazılı olmalı: ölçüt korpusun bugünkü kurulumuna değil
    **yasağın tanımına** bağlı kalmalı.

    *Bir ölçütü bugünkü koşullara göre sadeleştirmek, onu yarın yanlış yapar.*"""
    import inspect

    src = inspect.getsource(_cevapsiz_kesme)
    assert "yol_siniri" in src, "🔴 ikinci meşru bitiş şartı ölçütten düşmüş"
    assert "source" in src and "trace" in src


def test_KORPUS_HAM_SAYILARI_da_RAPORLUYOR():
    """🔴 Bir oran, **paydası görünmeden** yorumlanamaz — bu deponun `gitas` dersi:
    payda 445→342 düştüğünde doğruluk **yükselmişti** ve sistem bozuluyordu."""
    import pathlib

    src = (pathlib.Path(__file__).resolve().parents[1]
           / "lab/nl_corpus.py").read_text(encoding="utf-8")
    assert '"kesme_sayi"' in src and '"kesme_payda"' in src, (
        "🔴 ham sayılar raporlanmıyor — yalnız oran, paydası bilinmeyen bir sayıdır")
    assert "kesme_sayi\": sum(" in src, "🔴 dilimler arasında toplanmıyor"


# --- 🔴 ÖLÇÜM ARACININ KENDİ BÜTÜNLÜĞÜ -------------------------------------------

def test_OLCUM_ARACINDA_ULASILAMAZ_KOD_YOK():
    """🔴 **Bu kapı bir kusurdan doğdu ve kusuru ben yaptım.**

    `_cevapsiz_kesme` eklenirken tanım `run_company`'nin **gövdesinin ortasına** düştü.
    Python bunu şikâyet etmez: fonksiyon orada biter, kalan gövde yeni fonksiyonun
    `return`'ünden **sonra** kalır ve **ölü koda** dönüşür. Sonuç:

    * korpusun **süreç (çok turlu) yarısı hiç koşmadı**;
    * `run_company` sessizce `None` döndü;
    * kapı `birlestir`'de `AttributeError` ile patladı — yani **kusurun doğduğu yerde
      değil, üç fonksiyon ötede**;
    * ⚠ ve arada bir tur, ölçüm daraldığı için **taban güncellendi** (`dogru 83→69`,
      *"korunum"* diye gerekçelendirildi).

    *Bir aletin sessizce daralması, bir gerilemeden pahalıdır: gerileme kırmızı verir,
    daralma yeni bir taban verir.*

    Tarama genel: aynı blokta `return`/`raise`/`continue`/`break`'ten **sonra** gelen
    çalıştırılabilir ifade. Yorum ve docstring sayılmaz.
    """
    import ast
    import pathlib

    kok = pathlib.Path(__file__).resolve().parent.parent / "lab"
    suclu: list[str] = []
    for yol in sorted(kok.glob("*.py")):
        agac = ast.parse(yol.read_text(encoding="utf-8"))
        for dugum in ast.walk(agac):
            govde = getattr(dugum, "body", None)
            if not isinstance(govde, list):
                continue
            for i, ifade in enumerate(govde[:-1]):
                if isinstance(ifade, (ast.Return, ast.Raise, ast.Continue, ast.Break)):
                    sonraki = govde[i + 1]
                    if isinstance(sonraki, ast.Expr) and isinstance(
                            getattr(sonraki, "value", None), ast.Constant):
                        continue                      # yalnız bir metin — zararsız
                    suclu.append(f"{yol.name}:{sonraki.lineno}")
    assert not suclu, (
        "🔴 ÖLÇÜM ARACINDA ULAŞILAMAZ KOD: " + ", ".join(suclu) +
        " — bir ölçüm aracının sessizce daralması, ölçtüğü şeyin gerilemesinden "
        "daha pahalıdır.")


def test_RUN_COMPANY_SOZLUK_DONER():
    """`birlestir` her dilimin bir sözlük olduğunu varsayar; `None` dönen tek bir dilim
    **tüm şirketi** çökertir. Sözleşme burada yazılı."""
    import ast
    import inspect

    from lab import nl_corpus

    agac = ast.parse(inspect.getsource(nl_corpus.run_company))
    fn = agac.body[0]
    son = fn.body[-1]
    assert isinstance(son, ast.Return) and son.value is not None, (
        "🔴 `run_company` bir dönüş İFADESİYLE bitmiyor — düşen yol `None` üretir ve "
        "`birlestir` onu üç fonksiyon ötede `AttributeError` olarak gösterir.")
