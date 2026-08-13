r"""🔴 `§7 ②` kapısı — **adlandırılmış makro**: tek öneri, N deterministik adım.

## Bu kapının ㉕ zinciri

Yüklemler kendi *«plan doğru görünüyor»* fikrimi ölçmez; planı **ürünün kendi
doğrulayıcısına** (`plan_kosucu.dogrula`) verir. O doğrulayıcı bir planı **koşmadan**
denetler ve tip uyuşmazlıklarını (`SORGU($3)` bir `HESAPLA` adımını gösteriyorsa) yakalar.

*Bir kapıyı kendi beklentine bağlarsan, beklentin yanıldığında kapı da yanılır.*
"""

from __future__ import annotations

import pytest

from app import makro
from app.plan_kosucu import dogrula

_CQ = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}


# ── 🔴🔴 ASIL KAPI — üç reçete de ÜRÜNÜN doğrulayıcısından geçer ────────────

@pytest.mark.parametrize("ad,boyut", [("neden", "vardiya"), ("gecen_yil", ""),
                                      ("en_kotu", "makine")])
def test_RECETE_URUNUN_DOGRULAYICISINDAN_GECER(ad, boyut):
    """🔴 `②` kademesinin tamamı buna dayanır: makro bir **plan** üretir ve o plan
    ürünün kendi kurallarına uyar. Uymazsa kullanıcı **çalışmayan bir düğme** görür 🆘.

    🅑 Mutasyon: `_neden_bu_seviyede`'deki `"$3"` referansı `"$2"` yapılırsa (`KIYASLA`
    → `olcum`, oysa `SORGU` **sorgu** bekler) bu yüklem kırılır.
    """
    plan = makro.plan_uret(ad, _CQ, boyut=boyut)
    dogrula(plan)          # fırlatırsa kapı kırmızı — mesajı testin çıktısına düşer 🅤


def test_ANLAT_YALNIZ_SON_ADIM():
    """Kapalı gramerin kuralı: *«`ANLAT` — YALNIZ son adım olabilir»*. Üç reçetede de."""
    for ad, boyut in (("neden", "vardiya"), ("gecen_yil", ""), ("en_kotu", "makine")):
        adimlar = makro.plan_uret(ad, _CQ, boyut=boyut)["adimlar"]
        yerler = [i for i, a in enumerate(adimlar) if a["fiil"] == "ANLAT"]
        assert yerler == [len(adimlar) - 1], f"{ad}: ANLAT son adım değil ({yerler})"


# ── `E-8` — SICAK YOLDA İKİNCİ LLM TURU YOK ────────────────────────────────

def test_MAKRO_LLM_CAGIRMAZ():
    """🔴 `§7`'nin tablosu `②` için LLM'i **⊘** işaretler. Makro LLM çağırsaydı `③` ile
    aynı şey olurdu ve kademe ayrımı **anlamını yitirirdi**.

    ⚠ Yüklem **kullanımı** arar, sözü değil 🅞: yorumda geçen *«LLM»* kelimesi kapıyı
    kırmamalı, `import` kırmalı. Bu yüzden docstring'ler ayıklanır.
    """
    import pathlib

    from tests._kod_ayikla import kodu_ayikla

    kaynak = kodu_ayikla(
        (pathlib.Path(__file__).resolve().parents[1] / "app" / "makro.py")
        .read_text(encoding="utf-8"))
    for yasak in ("from app import llm", "import llm", "plan_garson", "sarmala",
                  "openai", "anthropic"):
        assert yasak not in kaynak, f"🔴 makro LLM yoluna bağlanmış: {yasak!r} (`E-8`)"


def test_MAKRO_BELIRLENIMSIZ_DEGIL():
    """㉝ Aynı girdi → **aynı** plan. Belirlenimsiz bir makro, tıklandığında her seferinde
    başka bir şey yapan bir düğmedir."""
    a = makro.plan_uret("neden", _CQ, boyut="vardiya")
    b = makro.plan_uret("neden", _CQ, boyut="vardiya")
    assert a == b


# ── ÇAPASIZ / ARGÜMANSIZ HÂLLER — ÖNERİLMEZ, uydurulmaz ────────────────────

def test_CAPASIZ_MAKRO_ONERILMEZ():
    """Çapasız *«neden bu seviyede?»*'nin **öznesi yoktur**. Uydurma çapa yok."""
    assert makro.makrolar_icin(None) == []
    assert makro.makrolar_icin({}) == []


def test_BOYUTSUZ_RECETE_LISTELENMEZ():
    """🆘 Eksik argümanlı bir öneri, tıklandığında düşen bir düğmedir — hiç gösterilmez."""
    adlar = {m["ad"] for m in makro.makrolar_icin(_CQ, boyutlar=[])}
    assert "neden" not in adlar and "en_kotu" not in adlar
    assert "gecen_yil" in adlar, "boyut istemeyen reçete boyutsuz da önerilebilmeli"

    hepsi = {m["ad"] for m in makro.makrolar_icin(_CQ, boyutlar=["vardiya"])}
    assert hepsi == {"neden", "gecen_yil", "en_kotu"}


def test_BILINMEYEN_MAKRO_SESSIZ_DEGIL():
    """🅤 Sessiz boş plan = hiçbir şey yapmayan düğme, üstelik **izsiz**."""
    with pytest.raises(ValueError, match="bilinmeyen makro"):
        makro.plan_uret("olmayan", _CQ)
    with pytest.raises(ValueError, match="kırılım boyutu"):
        makro.plan_uret("neden", _CQ)          # boyut zorunlu, verilmedi


# ── CÜMLE — kullanıcıya GÖRÜNEN yüzü ───────────────────────────────────────

def test_CUMLE_KURULMUS_DONER():
    """`§3.3`: bu bir **tamamlama**dır — kullanıcı ham bir şablon değil, bir **cümle**
    görür. Yer tutucu sızarsa kullanıcı `{olcu}` okur."""
    for m in makro.makrolar_icin(_CQ, boyutlar=["vardiya"], olcu_etiketi="ortalama OEE",
                                 boyut_etiketi="vardiya"):
        assert "{" not in m["metin"] and "}" not in m["metin"], m["metin"]
        assert m["metin"] and m["metin"][0] != " "
        assert m["adim_sayisi"] >= 3, "makro tek adımlıysa `①` kademesidir, `②` değil"


# ── ⚠ MAKRO ENFLASYONU — planın kendi uyarısı 🆞 ───────────────────────────

def test_MAKRO_ENFLASYONU_TAVANI():
    """🔴 *«Her kombinasyon adlandırılırsa uzayı SAYMIŞ olursun. Bir makro adını
    olasılıkla değil SIKLIKLA kazanır.»*

    Bu yüklem bir **tavan**dır: yeni makro eklemek serbest değil, bir **ölçüm** ister
    (`InteractionLog` sıklığı) 🅗. Tavan bilinçli olarak dardır — liste uzatmak 🆞 bir
    çözüm değil bir borçtur.
    """
    assert len(makro.MAKROLAR) <= 5, (
        f"🔴 {len(makro.MAKROLAR)} makro — tavan 5. Yeni bir ad eklemeden önce SIKLIK "
        "ölçülmeli; ölçülmemiş bir makro, sayılmış bir kombinasyon uzayıdır.")


# ── 🔴🔴 `②` KADEMESİ KOŞUM UCU — ve LLM'e DEĞMEME ŞARTI ────────────────────

def test_MAKRO_UCU_ORKESTRATORUN_LLM_KAPISINDAN_GECMEZ():
    """🔴 `§7`'nin tablosu `②` için LLM'i **⊘** işaretler ve kademelerin *«karışmamalı»*
    olması o tablonun başlığıdır.

    ⊙ Ölçüldü (`plan_tuketici.py:405`): `cevap()` *«boşluğun tek kapısı»*dır ve **LLM
    çağrısını kendi içinde** yapar. Makro ucu oradan geçseydi `②` sessizce `③`'e dönerdi
    — üstelik hiçbir kapı bunu söylemezdi, çünkü cevap yine doğru çıkardı 🅯.

    🅑 Mutasyon: uçtaki `plan_tuketici.calistir` çağrısı `plan_tuketici.cevap` yapılırsa
    bu yüklem kırılır.
    """
    import pathlib

    from tests._kod_ayikla import kodu_ayikla

    src = kodu_ayikla((pathlib.Path(__file__).resolve().parents[1] / "app" / "routers"
                       / "oneri.py").read_text(encoding="utf-8"))
    assert "plan_tuketici.calistir(" in src, (
        "🔴 makro ucu planı kendisi koşmuyor — `②` kademesinin tanımı bu.")
    assert "plan_tuketici.cevap(" not in src, (
        "🔴 makro ucu orkestratörün LLM kapısından geçiyor → `②` değil `③` olur (`E-8`).")
    assert "plan_kosucu.dogrula(" in src, (
        "🔴 canlı çapayla kurulan plan **koşmadan** denetlenmeli — motora giden geçersiz "
        "bir plan, motorun hatasıyla değil bizim ihmalimizle düşer.")


def test_LOWER_IS_BETTER_BIRLESIMI_TEK_SAHIP():
    """㊲ *«hangi ölçüde küçük iyidir»* sorusunun **iki** cevabı olamaz.

    Birleşim iki yerden isteniyor (orkestratörün yolu + makro ucu). İkisi ayrı ayrı
    yazsaydı bir gün biri yeni bir kaynağı okumaya başlar, öteki okumazdı — ve bir küpün
    yönü cevabın **işaretini** belirler.
    """
    import pathlib

    from tests._kod_ayikla import kodu_ayikla

    kok = pathlib.Path(__file__).resolve().parents[1] / "app"
    sayac = 0
    for p in (kok / "plan_tuketici.py", kok / "routers" / "oneri.py"):
        sayac += kodu_ayikla(p.read_text(encoding="utf-8")).count('"lower_is_better"')
    assert sayac <= 2, (
        f"🔴 `lower_is_better` birleşimi {sayac} yerde kuruluyor — tek sahip "
        "`plan_tuketici.kosum_cube_meta` olmalı ㊲.")
