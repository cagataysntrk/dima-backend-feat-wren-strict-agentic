"""FAZ 9.6 + 9.7 — ÖLÇÜM ARACININ KENDİSİ DENETLENİYOR.

> MIMARI §6.4: *"ölçüm aracının kendisi de bir bağımlılıktır"* — `lab/nl_corpus.py`
> aylarca kırıkken kimse fark etmedi. Bu oturumda araç **beş kez** yanlış ölçtü.

## 9.6 — `vqr_kalicilik` yapısal olarak ÖLÇEMİYORDU, ama ✅ raporluyordu

İki bağımsız neden:

1. **Koşum** her 2. adıma önceki `cube_query`'yi iliştiriyordu → `ask.py` takip
   sorularında `near_exact`'i **tümden atlıyor**. Yani senaryo, ölçmek için var olduğu
   replay yolunu **hiç çalıştırmadan** *"replay YOK ✅"* diyordu.
2. `ask.py:2306` `learn=(intent_source == "cube+llm")` → **saf `cube` yolu VQR'a hiç
   yazmaz**. Bu bir kusur DEĞİL, Faz 2b-2'nin ölçülmüş kararı. Ama sonucu şu: LLM'siz
   (CI) modda §1.7 riski **doğamaz**, dolayısıyla *"risk yok"* çıkarımı dayanaksızdır.

MIMARI §6.5z boş sonucu yalnız *"embedder kapalı"* ile açıklıyordu — **eksik teşhis**:
embedder açılsa bile yazan kimse yok.

**Çözüm üçüncü bir durum:** `⊘ ÖLÇÜLEMEDİ`. Yeşile yuvarlamak *"risk yok"* yalanı,
kırmızıya yuvarlamak sahte alarm üretirdi.

## 9.7 — DOĞRULUK kanalı, adını taşıdığı şeyin bir parçasını hiç ölçmüyordu

`_cube_dogru` **hiçbir yerden çağrılmıyordu**; dokuz sınıftan yalnız `konu_degisimi`
cevabın cube'una bakıyordu. Rapor başlığı *"DOĞRULUK (doğru cube/dönem/yapı)"* diyordu:
cevap **yanlış cube'dan** gelse bile vaka ✅ raporlanabiliyordu — yani araç, görünür
kılmak için var olduğu **sessiz-yanlış** sınıfına karşı kördü.

`_bitisik` ise beklenen cube'un zaman boyutunu **sabitliyordu** — `_daraldi`'da
düzeltilen hatanın aynı dosyadaki ikinci kopyası (*"kimlik asimetrisi"*, bu kez ölçüm
aracının içinde).
"""

from __future__ import annotations

import inspect

from lab import konusma_senaryolari as ks


# --- 9.6: üçüncü durum gerçekten VAR ve DOĞRU yerde ------------------------------

def test_UCUNCU_DURUM_olculemedi_destekleniyor():
    """`bekle` `None` dönebilmeli ve koşum bunu geçti/kaldı'ya YUVARLAMAMALI."""
    govde = inspect.getsource(ks.kos)
    assert "gecti is None" in govde, "koşum ÖLÇÜLEMEDİ durumunu tanımıyor"
    assert "olculemedi" in govde


def test_VQR_senaryosu_BAGIMSIZ_kosuyor():
    """Takip sorusu olarak gönderilirse `near_exact` hiç çalışmaz ve senaryo ölçtüğünü
    SANIR — bu sınıfın yapısal olarak ölçememesinin birinci nedeni."""
    govde = inspect.getsource(ks._uret)
    i = govde.index('ekle("vqr_kalicilik"')
    assert "bagimsiz=True" in govde[i:i + 400], \
        "vqr senaryosu hâlâ takip sorusu olarak gidiyor — replay yolu koşulmuyor"


def test_BAGIMSIZ_bayragi_KOSUMDA_onurlandiriliyor():
    """Bayrak var ama koşum ona bakmıyorsa, beyan koddan kopar — bu oturumun on dört
    kez avladığı sınıf."""
    govde = inspect.getsource(ks.kos)
    assert 'sen.get("bagimsiz")' in govde, "koşum `bagimsiz` bayrağını YOK SAYIYOR"


def test_VQR_kontrolu_ON_KOSULU_dogruluyor():
    """`cube+llm` olmadan VQR'a yazılmaz; kontrol bunu ÖLÇÜLEMEDİ saymalı, geçti değil."""
    govde = inspect.getsource(ks._uret)
    i = govde.index("def _vqr(")
    pencere = govde[i:i + 1800]
    assert "cube+llm" in pencere, "kontrol yazma ön koşulunu bilmiyor"
    assert "return None," in pencere, "ön koşul sağlanmadığında ÖLÇÜLEMEDİ dönmüyor"


def test_OLCULEMEDI_RAPORDA_gorunuyor():
    """Sessiz bir ⊘, sahte bir ✅ kadar kötüdür: rapor onu ayrı SÜTUNDA göstermeli."""
    kaynak = inspect.getsource(ks)
    assert "ÖLÇÜLEMEDİ" in kaynak
    assert '"dogruluk"] is True' in kaynak, \
        "doğruluk sayacı `None`'ı da 'doğru' sayıyor olabilir (truthiness tuzağı)"


# --- 9.7: DOĞRULUK kanalı cube'u GERÇEKTEN ölçüyor -------------------------------

def test_CUBE_KONTROLU_yetim_degil():
    """Bu kusurun tam biçimi: yardımcı yazılmış, çağrılmamış."""
    import ast
    import textwrap

    # ⚠️ METİN DEĞİL DAVRANIŞ: ilk sürüm `"_cube_dogru" not in govde` diyordu ve KENDİ
    # DOCSTRING'İMDEKİ tarihçe alıntısını yakaladı — bu oturumda beşinci kez bir testim
    # metni davranış sandı. Artık ÇAĞRI ve TANIM düğümlerine bakılıyor.
    agac = ast.parse(textwrap.dedent(inspect.getsource(ks._uret)))
    cagrilar = [d.func.id for d in ast.walk(agac)
                if isinstance(d, ast.Call) and isinstance(d.func, ast.Name)]
    tanimlar = {d.name for d in ast.walk(agac) if isinstance(d, ast.FunctionDef)}

    assert cagrilar.count("_ve_cube") >= 6, (
        f"cube kontrolü yalnız {cagrilar.count('_ve_cube')} sınıfa bağlanmış — rapor "
        "başlığı 'doğru cube' diyorsa sınıfların hepsinde ölçülmeli")
    assert "_cube_dogru" not in tanimlar, "ölü yardımcı hâlâ TANIMLI"


def test_VE_CUBE_yanlis_cubeu_YAKALIYOR():
    """Sarmalın kendisi doğru çalışmazsa kapı bir dekordan ibaret kalır."""
    sarmal = None

    # `_ve_cube` `_uret`'in içinde kapalı bir fonksiyon; davranışını aynı sözleşmeyle
    # yeniden kurmak yerine kaynağından çalıştırılabilir bir kopya elde ediyoruz.
    kaynak = inspect.getsource(ks._uret)
    bas = kaynak.index("    def _ve_cube(")
    son = kaynak.index("\n    for c in cubes[")
    kod = "\n".join(s[4:] if s.startswith("    ") else s
                    for s in kaynak[bas:son].splitlines())
    ns: dict = {}
    exec(compile(kod, "<_ve_cube>", "exec"), ns)  # noqa: S102 — test içi, sabit kaynak
    sarmal = ns["_ve_cube"]

    dogru = sarmal(lambda i, d: (True, "ok"), "parti")
    assert dogru(0, {"cube_query": {"cube": "parti"}})[0] is True
    yanlis = dogru(0, {"cube_query": {"cube": "mizan"}})
    assert yanlis[0] is False and "YANLIŞ CUBE" in yanlis[1], \
        "yanlış cube'dan gelen cevap DOĞRU raporlanıyor — sessiz-yanlış görünmez kalır"


def test_VE_CUBE_altindaki_kontrolu_EZMIYOR():
    """Sarmal fazla geniş olmamalı: alttaki kontrol zaten başarısızsa gerekçesi KORUNUR,
    yoksa vaka raporu neyin kırıldığını söyleyemez."""
    kaynak = inspect.getsource(ks._uret)
    bas = kaynak.index("    def _ve_cube(")
    son = kaynak.index("\n    for c in cubes[")
    kod = "\n".join(s[4:] if s.startswith("    ") else s
                    for s in kaynak[bas:son].splitlines())
    ns: dict = {}
    exec(compile(kod, "<_ve_cube>", "exec"), ns)  # noqa: S102
    f = ns["_ve_cube"](lambda i, d: (False, "dönem filtresi YOK"), "parti")
    assert f(0, {"cube_query": {"cube": "mizan"}}) == (False, "dönem filtresi YOK")


def test_BITISIK_beklenen_cubeun_zamanini_SABITLEMIYOR():
    """`_daraldi`'da düzeltilen hatanın ikinci kopyası. Cevabın cube'u farklıysa onun
    zaman boyutuna bakılmalı; sabitlemek ÇALIŞAN bir filtreyi 'YOK' diye raporlar."""
    import ast
    import textwrap

    agac = ast.parse(textwrap.dedent(inspect.getsource(ks._uret)))
    fn = next(d for d in ast.walk(agac)
              if isinstance(d, ast.FunctionDef) and d.name == "_bitisik")
    # DAVRANIŞ: varsayılan argümanla cube'a özel bir değer KAPATILMIŞ mı (`_z=zaman`)?
    assert not fn.args.defaults and not fn.args.kw_defaults, (
        "`_bitisik` hâlâ beklenen cube'un zaman boyutunu varsayılan argümanla "
        "SABİTLİYOR — çalışan bir filtreyi 'YOK' diye raporlar")
    govde_metni = ast.unparse(ast.Module(body=fn.body, type_ignores=[]))
    assert "cq.get('cube')" in govde_metni or 'cq.get("cube")' in govde_metni, \
        "zaman boyutu CEVABIN cube'undan okunmuyor"


# --- `--live` HİÇBİR ZAMAN CANLI DEĞİLDİ (canlı thread turunda bulundu) -----------
#
# ## Ölçülen kusur (3 Ağustos 2026)
#
# `lab/konusma_senaryolari.py` env kurulumu için `tests.conftest`'i import ediyor.
# `conftest.py:15` **koşulsuz** `DIMA_LLM_PROVIDER="rule"`, `:26` `DIMA_VQR_EMBEDDER="off"`
# yazar — testlerin ağa çıkmaması için DOĞRU bir karardır. Ama `--live` o yan etkiyi de
# devralıyordu: bayrak yalnız monkeypatch'leri (dry_plan/enrich) atlıyor, **sağlayıcıyı
# değiştirmiyordu**.
#
# Yani *"GERÇEK sağlayıcı, SIRALI, hız-sınırlı"* beyanı **karşılıksızdı** ve o modda
# alınan her ölçüm LLM hakkında hiçbir şey söylemiyordu — `cube+llm` üretilmiyor, VQR
# benzerliği hiç tetiklenmiyor, red gerekçesi hiç yazılmıyordu. MIMARI §6.4'ün dersi
# (*"ölçüm aracının kendisi de bir bağımlılıktır"*) bu turda **en pahalı** biçimde ısırdı:
# ölçüm aracı çalışıyor görünüyor ve ölçtüğünü iddia ettiği şeyi hiç görmüyordu.

def test_LIVE_MODU_sagayiciyi_GERI_YUKLUYOR():
    """`--live` conftest'in `rule` sabitlemesini geri almalı."""
    kaynak = inspect.getsource(ks)
    assert "_GERCEK_ORTAM" in kaynak, "gerçek ortam import ÖNCESİ yakalanmıyor"
    assert "_canli_ortami_geri_yukle" in kaynak
    i = kaynak.index("_GERCEK_ORTAM = {")
    j = kaynak.index("import tests.conftest")
    assert i < j, ("gerçek ortam conftest'ten SONRA yakalanıyor — o noktada değerler "
                   "zaten EZİLMİŞ olur ve geri yükleme `rule`'u geri yükler")


def test_LIVE_gercek_saglayici_YOKSA_KOSMUYOR():
    """Fail-closed: sessizce `rule` ile koşan bir 'canlı' tur, hiç koşmamaktan KÖTÜDÜR —
    yanlış bir güven verir ve o güvene dayanarak karar alınır (bu turda alındı)."""
    govde = inspect.getsource(ks._canli_ortami_geri_yukle)
    assert "SystemExit" in govde, "sağlayıcı yokken --live yine de koşuyor"
    assert '"rule"' in govde, "`rule` sağlayıcı geçerli sayılıyor olabilir"


def test_CANLI_YOLU_SUSTURAN_anahtarlar_geri_aliniyor():
    """Yalnız sağlayıcı yetmez: embedder kapalıyken VQR benzerliği, telemetri kapalıyken
    red gerekçesi HİÇ üretilmez — üçü de canlı-özel yollardır."""
    govde = inspect.getsource(ks._canli_ortami_geri_yukle)
    for anahtar in ("DIMA_LLM_PROVIDER", "DIMA_VQR_EMBEDDER", "DIMA_INTERACTION_LOG"):
        assert anahtar in govde, f"{anahtar} geri alınmıyor"
    assert "DIMA_DATABASE_URL" not in inspect.getsource(ks._canli_ortami_geri_yukle).split(
        "CANLI_YOLU_SUSTURANLAR")[1], \
        "DB izolasyonu bozuluyor olabilir — canlı ölçüm kullanıcının verisini kirletmemeli"


def test_YAPISAL_MOD_degismedi():
    """Düzeltme yalnız `--live`'ı etkilemeli: hızlı mod CI'ın günlük kilididir ve ağsız
    kalmak ZORUNDADIR."""
    kaynak = inspect.getsource(ks)
    i = kaynak.index("if not args.live:")
    pencere = kaynak[i:i + 500]
    assert "_enrich_categorical" in pencere and "dry_plan" in pencere, \
        "yapısal mod monkeypatch'leri kaybolmuş"
    assert "_canli_ortami_geri_yukle" not in pencere, \
        "yapısal mod da gerçek sağlayıcıya geçiyor — CI ağa çıkar"
