"""🔴 `G1` — **TEMELLENDİRME**: sistem ne anladığını SÖYLER.

Üretimdeki başarısızlığın **%69'u** (`WRONG_FILTER` %54,6 + `WRONG_SCOPE` %14,4)
*"SQL çalıştı, makul bir sayı döndü, ama başka bir sorunun cevabıydı"* sınıfıdır.
Garson siparişi **tekrarlar** — hatayı ilk saniyede görünür kılar.

⚠ Kural `soz.py:19`'da ZATEN yazılıydı (*"ÖNCE NE ANLADIĞINI SÖYLE"*) ama yalnız
**netleştirmede** uygulanıyordu. Bu kapı onu **her tura** genişletir.
"""

from __future__ import annotations

from app.temellendirme import kur


def test_olcu_donem_kirilim_okunur():
    cq = {"cube": "satis", "measures": ["toplam_ciro"], "dimensions": ["sube"],
          "filters": [{"dimension": "tarih", "value": "2026-03"}]}
    t = kur(cq, katalog={"toplam_ciro": "Satış Cirosu (TL)", "sube": "Şube"},
            cube_etiketi="Satış")
    assert t["olcu"] == "Satış Cirosu (TL)"
    assert t["donem"] == "2026-03"
    assert t["kirilim"] == ["Şube"]
    assert t["cube"] == "Satış"


def test_HAM_KOLON_ADI_BASILMAZ():
    """🔴 Kullanıcı `toplam_ciro_tl` görmez — görünen ad görür. Katalog yoksa bile
    alt çizgi temizlenir; *ham kolon adı bir arayüz metni değildir.*"""
    t = kur({"measures": ["satis.toplam_ciro_tl"]}, katalog=None)
    assert t["olcu"] == "toplam ciro tl"
    assert "_" not in t["olcu"]


def test_DONEM_ile_FILTRE_ayrilir():
    """Dönem bir **zaman** beyanıdır, filtre bir **kapsam** beyanı. Aynı kutuda
    gösterilirlerse *"hangi dönem"* sorusu kaybolur."""
    cq = {"measures": ["ciro"],
          "filters": [{"dimension": "tarih", "value": "2026-03"},
                      {"dimension": "sube", "value": "Merkez"}]}
    t = kur(cq, katalog={"sube": "Şube"})
    assert t["donem"] == "2026-03"
    assert t["filtreler"] == ["Şube: Merkez"]


def test_granulerlik_de_bir_DONEM_beyanidir():
    """Kullanıcı *"aylık"* dediyse onu duyduğumuzu söylemeliyiz."""
    t = kur({"measures": ["ciro"],
             "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]})
    assert t["granulerlik"] == "month"


def test_BOS_BEYAN_BASILMAZ():
    """*"Anladığım şu: (boş)"* bir beyan değil, bir **gürültüdür**."""
    assert kur({}) is None
    assert kur({"cube": "satis"}) is None          # yalnız cube adı yeterli değil
    assert kur(None) is None
    assert kur("saçma") is None                    # tip hatası cevabı düşürmez


def test_TEKRARLAR_TEKILLESTIRILIR():
    t = kur({"measures": ["ciro", "ciro"], "dimensions": ["sube", "sube"]},
            katalog={"ciro": "Ciro", "sube": "Şube"})
    assert t["olcu"] == "Ciro"
    assert t["kirilim"] == ["Şube"]


def test_LLM_COAGRISI_YOK():
    """🔴 0 token olması bir TASARIM ÖZELLİĞİDİR: LLM düşse bile bu satır basılır
    (bozulma merdiveninin 3. basamağı). Modül LLM'i **import bile etmez**."""
    import pathlib
    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app" / "temellendirme.py").read_text(encoding="utf-8")
    for yasak in ("from app.llm", "import llm", "safe_call", "requests"):
        assert yasak not in kaynak, f"temellendirme LLM'e uzanmış: {yasak}"


def test_SINIR_YAZILI():
    """Temellendirme hatayı **görünür** kılar, **engellemez** — ve bu sınır
    modülün kendi belgesinde yazılı olmalı (danışman belgesi onu garanti sanmıştı)."""
    import pathlib
    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app" / "temellendirme.py").read_text(encoding="utf-8")
    assert "garanti değil" in kaynak


# --- 🔴 CANLI KAPI BULDU — netleştirme turu da temellendirilir ----------------------


def test_NETLESTIRME_TURU_DA_TEMELLENDIRILIR(client):
    """🔴 `lab/garson.py --live` `8·temellendirme` satırında ❌ verdi ve sebebi ölçüldü:

        `fire kg` → source=None (dönem soruluyor) · cube_query={'cube':'parti',
                    'measures':['toplam_fire_kg']} · temellendirme=None

    `_temellendir` `source is None` ise dönüyordu; gerekçesi *"netleştirme cevabında
    temellendirilecek bir sorgu YOK"* idi ve **yanlıştı**. Kapı, temellendirmenin en
    değerli olduğu anda susuyordu: sistem *"hangi dönem?"* diye sorarken *"fire kg'yi
    anladım"* demiyordu.

    *Bir kapının gerekçesi, kapının kendisinden daha hızlı bayatlar.*
    """
    from tests.conftest import ask

    d = ask(client, "fire kg", session_id="tem-netlestirme")
    cq = d.get("cube_query") or {}
    if not cq.get("measures"):
        import pytest
        pytest.skip(f"⊘ vaka bayat — netleştirme kısmi sorgu taşımıyor: {cq}")
    t = d.get("temellendirme")
    assert isinstance(t, dict) and (t.get("olcu") or t.get("donem")), (
        f"🔴 netleştirme turu ne anladığını SÖYLEMİYOR: cq={cq} temellendirme={t}")


def test_DUZ_RETTE_GURULTU_YOK(client):
    """⚠ Ters yön: `cube_query` boş bir rette temellendirme **basılmaz** — yoksa her
    ret bir *"anladığım şu: (boş)"* gürültüsü üretirdi."""
    from tests.conftest import ask

    d = ask(client, "zxqw plmk asdf", session_id="tem-ret")
    if d.get("cube_query"):
        import pytest
        pytest.skip("⊘ bu soru kısmi sorgu üretti — vaka uygun değil")
    assert not d.get("temellendirme")


def test_KAPSAM_ROZETI_EKRANDA():
    """🔴 `DA-7` — `temellendirme.cube` üretiliyor, testleniyor, **tipli**… ve
    render EDİLMİYORDU.

    `G1`'in varlık gerekçesi ölçülmüş `WRONG_SCOPE` **%14,4**'tü: *"hangi konuyu
    anladım"* bu rozetin tam olarak cevapladığı soru. Kapsamı söylemeyen bir
    temellendirme, **en sık yanlışı** görünmez bırakır.

    *Bir beyanın en önemli parçasını düşürmek, beyanı süse çevirir.*
    """
    import pathlib

    fe = pathlib.Path(__file__).resolve().parents[2] / "dima-frontend-demo-master/src"
    if not fe.is_dir():
        import pytest
        pytest.skip("⊘ frontend mount edilmemiş")
    kaynak = (fe / "components" / "Temellendirme.tsx").read_text(encoding="utf-8")
    # ⚠ Liste `G1.7`'de **nesne dizisine** döndü (`{etiket, capa}`) çünkü rozetler artık
    # düzenleme çubuğuna götürüyor. Çapa `const rozetler` — sabit metin değil, o yüzden
    # `index()` yerine varlık kontrolü.
    i = kaynak.index("const rozetler")
    liste = kaynak[i:kaynak.index("].filter", i)]
    for alan in ("t.cube", "t.olcu", "t.donem"):
        assert alan in liste, f"🔴 `{alan}` rozet listesinde yok — üretilen alan ekranda YOK"


def test_ROZET_CAPALARI_DUZENLEME_CUBUGUYLA_ESLESIYOR():
    """🔴 `G1.7` — rozetler tıklanabilir, **ama düzenlemez: düzenleyene götürür.**

    Plan *"her rozet → o alanı değiştiren chip"* diyordu. Ölçüldü ve **olduğu gibi
    uygulanamaz**: `InterpretationBar` o alanların dördünü **zaten** düzenliyor
    (`next.measures` · `next.dimensions` · `next.filters` · `next.timeDimensions`).
    İkinci bir düzenleme yüzeyi, bu deponun bir numaralı kusurunu (*aynı kuralın iki
    sahibi*) doğrudan üretirdi ve iki yüzey zamanla **ayrışırdı**.

    *Bir yeteneği iki yere koymak, onu iki kez kazanmak değil; iki kez bakmaktır.*

    🔴 Bu kapının varlık sebebi: çapa adları ayrışırsa tıklama **sessizce hiçbir şey
    yapmaz** — kullanıcı için *"bozuk düğme"*, gelişt* için görünmez bir kusur.
    """
    import pathlib
    import re

    fe = pathlib.Path(__file__).resolve().parents[2] / "dima-frontend-demo-master/src"
    if not fe.is_dir():
        import pytest
        pytest.skip("⊘ frontend mount edilmemiş")

    tem = (fe / "components/Temellendirme.tsx").read_text(encoding="utf-8")
    ib = (fe / "components/InterpretationBar.tsx").read_text(encoding="utf-8")

    i = tem.index("const rozetler")
    isteyen = set(re.findall(r'capa:\s*"(\w+)"', tem[i:tem.index("].filter", i)]))
    # ⚠ Çapa **dinamik** de olabilir: `data-capa={... ? "donem" : "filtre"}`. Yalnız
    # sabit dizgeyi aramak, gerçek bir çapayı görmezden gelir ve kapı **sahte kırmızı**
    # verir — ilk yazımda tam bu oldu.
    # *Bir kapının ölçütü, ölçtüğü şeyin bütün yazım biçimlerini tanımak zorundadır.*
    veren = set()
    for blok in re.findall(r'data-capa=(\{[^}]*\}|"[^"]*")', ib):
        veren |= set(re.findall(r'"(\w+)"', blok))

    assert isteyen, "⊘ ölçüm tabanı çöktü: rozetlerde çapa yok"
    eksik = isteyen - veren
    assert not eksik, (
        f"🔴 ÇAPA AYRIŞMASI: rozet {sorted(eksik)} çapasına götürmek istiyor ama "
        f"`InterpretationBar`'da öyle bir `data-capa` YOK (mevcut: {sorted(veren)}). "
        "Tıklama sessizce hiçbir şey yapar — bozuk bir düğme, olmayan bir düğmeden kötüdür.")


def test_CUBE_ROZETI_TIKLANMAZ():
    """⚠ Sınır: `cube`'u değiştirmek bir **düzenleme değil, yeni bir sorudur** —
    `InterpretationBar` da onu düzenlemiyor. Yanlış cube'da doğru yol **netleştirmedir**.
    *Her rozeti tıklanabilir yapmak, tıklamanın anlamını da düzleştirir.*"""
    import pathlib

    fe = pathlib.Path(__file__).resolve().parents[2] / "dima-frontend-demo-master/src"
    if not fe.is_dir():
        import pytest
        pytest.skip("⊘ frontend mount edilmemiş")
    tem = (fe / "components/Temellendirme.tsx").read_text(encoding="utf-8")
    assert 'capa: null' in tem and 't.cube' in tem, (
        "🔴 `cube` rozeti tıklanabilir yapılmış — cube değişimi bir düzenleme değildir")
