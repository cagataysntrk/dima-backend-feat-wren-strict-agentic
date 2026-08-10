"""FAZ 2a-5 — R2 (liste/döküm): dalın YARISI haklıydı, yarısı kapsam kaybıydı.

## Ölçüm (2026-08-02) — plan iddiasını doğruladı ama bir tuzak da gösterdi

R2 koşulsuz `None` dönüyordu: *"liste/döküm istekleri cube'a uymaz → LLM/kural"*.
11 gerçekçi vaka ölçüldü; R2 **9'unu** kesiyordu. Liste kelimesi SÖKÜLÜNCE:

| soru | R2 kesince | liste kelimesi sökülünce |
|---|---|---|
| `müşteri bazında ciro listele` | cevap YOK | `parti/toplam_ciro dims=[musteri]` ✓ |
| `en çok ciro yapan 10 müşteriyi listele` | cevap YOK | `dims=[musteri] limit=10` ✓ |
| `makine bazında oee detay` | cevap YOK | `oee/ort_oee dims=[makine]` ✓ |
| `renk bazında fire dökümü` | cevap YOK | `parti/toplam_fire_kg dims=[renk]` ✓ |
| **`bu yıl ciro dökümü`** | cevap YOK | `dims=None` → **DEJENERE TOPLAM** ⚠ |
| **`bu ay ciro detaylı göster`** | cevap YOK | `dims=None` → **DEJENERE TOPLAM** ⚠ |

Yani cube kırılımı **üretebildiğinde** cevap tam; **üretemediğinde** döküm isteyen
kullanıcıya **tek bir sayı** dönerdi — `source=cube` rozetiyle, yani planın kendi
*"en tehlikeli sınıf"* tanımı. **R2'yi tümden kaldırmak bu ikinci sınıfı açardı.**

## Kural

Liste niyeti YALNIZ gerçek bir kırılım eşleştiğinde onurlandırılır; yoksa R2 aynen kalır.
Bu, `route()`'un `_BREAKDOWN_HINTS` için zaten uyguladığı sessiz-yanlış korumasının
aynısı — yeni ilke değil, var olanın buraya da uygulanması.

## KURAL B

`liste_kirilimi` **anahtar-kelime argümanı**, varsayılanı `False`. `cube_router` istek/
principal görmez, bayrağı çağıran çözer. Varsayılan = **bugünkü davranış birebir**.
"""

from __future__ import annotations

import pytest

from app import cube_router as cr


def _plan(schema, soru, *, bayrak=True):
    cr.reddi_sifirla()
    return cr.route(cr._norm(soru), schema, liste_kirilimi=bayrak)


# --- KURAL B: bayrak kapalıyken BİREBİR ------------------------------------------

@pytest.mark.parametrize("soru", [
    "musteri bazinda ciro listele",
    "en cok ciro yapan 10 musteriyi listele",
    "makine bazinda oee detay",
    "renk bazinda fire dokumu",
    "vardiya bazinda uretim detayi",
])
def test_BAYRAK_KAPALIYKEN_hepsi_R2(schema, soru):
    """Geri dönüş yolu olmadan canlı cevap yolu değiştirilmez (KURAL B)."""
    assert _plan(schema, soru, bayrak=False) is None
    assert cr.red_gerekcesi() == "R2"


def test_VARSAYILAN_kapali(schema):
    """`route(q, schema)` — argümansız çağrı BUGÜNKÜ davranışı vermeli; beş çağıranın
    hiçbiri kırılmasın."""
    cr.reddi_sifirla()
    assert cr.route(cr._norm("musteri bazinda ciro listele"), schema) is None
    assert cr.red_gerekcesi() == "R2"


# --- ASIL KAZANÇ: kırılım eşleşiyorsa cube üretir --------------------------------

@pytest.mark.parametrize("soru,cube,olcu,dim", [
    ("musteri bazinda ciro listele", "parti", "toplam_ciro", "musteri"),
    ("makine bazinda oee detay", "oee", "ort_oee", "makine"),
    ("renk bazinda fire dokumu", "parti", "toplam_fire_kg", "renk"),
    ("vardiya bazinda uretim detayi", "oee", "toplam_uretim_kg", "vardiya"),
])
def test_KIRILIM_eslesince_CUBE_uretir(schema, soru, cube, olcu, dim):
    r = _plan(schema, soru)
    assert r is not None, f"{soru!r} hâlâ cevapsız (red={cr.red_gerekcesi()})"
    cq = r["cube_query"]
    assert cq["cube"] == cube and cq["measures"] == [olcu]
    assert cq["dimensions"] == [dim]


def test_TOP_N_de_korunuyor(schema):
    """*"en çok ciro yapan **10** müşteriyi listele"* — sayı bir satır limitidir ve
    liste niyeti onu düşürmemeli."""
    r = _plan(schema, "en cok ciro yapan 10 musteriyi listele")
    assert r is not None
    assert r["cube_query"]["dimensions"] == ["musteri"]
    assert (r["cube_query"].get("limit") or r.get("limit")) == 10


# --- SESSİZ-YANLIŞ KAPISI: kırılım yoksa R2 KALIR --------------------------------

@pytest.mark.parametrize("soru", [
    "bu yil ciro dokumu",          # dims=None → dejenere TEK TOPLAM olurdu
    "bu ay ciro detayli goster",   # aynı sınıf
])
def test_KIRILIM_YOKSA_R2_KALIR(schema, soru):
    """Bu testin koruduğu şey kapsam değil **dürüstlük**: döküm isteyen kullanıcıya
    tek bir toplam döndürmek, cevapsız kalmaktan KÖTÜDÜR (cube rozetiyle gelir)."""
    assert _plan(schema, soru) is None, "dejenere toplam üretildi"
    assert cr.red_gerekcesi() == "R2"


def test_OLCU_YOKSA_dogru_gerekce(schema):
    """*"müşterileri listele"* — kırılım var ama ÖLÇÜ yok. R2 değil R4 vermeli:
    red gerekçesi telemetride (Faz 0) doğru kümeye düşsün."""
    assert _plan(schema, "musterileri listele") is None
    assert cr.red_gerekcesi() == "R4"


def test_DOKUMA_tuzagi_KORUNUYOR(schema):
    """`dokum` altdizisi "DOKUMa"yı (kumaş!) yakalıyordu — kelime sınırı hâlâ yerinde."""
    assert not cr.liste_niyeti(cr._norm("dokuma kumas cirosu"))
    r = _plan(schema, "bu yil dokuma kumas cirosu")
    assert r is not None and r["cube_query"]["cube"] == "parti"


def test_GOSTER_liste_niyeti_DEGIL():
    """Genel "göster" dolgudur; liste niyeti saymak her soruyu bu dala sokardı."""
    assert not cr.liste_niyeti(cr._norm("bu yil ciro goster"))


# --- KAPSAM KAPISI: niyet anlaşıldıysa kelime kapsamı DELMEZ ---------------------

def test_LISTE_kelimesi_kapsami_DELMEZ(schema):
    """R2 dalı soruyu geçirdiyse kırılım gerçekten eşleşmiş demektir; o hâlde
    "listele"/"dökümü" bir dolgudur. İki taraf ayrışırsa niyet "anlaşıldı" sayılır ama
    kelime yine de R10 verirdi — sessiz bir kapsam kaybı."""
    for soru in ("musteri bazinda ciro listele", "renk bazinda fire dokumu",
                 "makine bazinda oee detay"):
        r = _plan(schema, soru)
        assert r is not None, f"{soru!r} → R10 (kapsam kapısı liste kelimesini yedi)"


def test_TEK_KAYNAK_regex():
    """`liste_niyeti` ile kapsam kapısı AYNI `_LISTE_RE`'yi okumalı."""
    import inspect

    assert "_LISTE_RE" in inspect.getsource(cr.liste_niyeti)
    assert "_LISTE_RE" in inspect.getsource(cr.route)


# --- UÇTAN UCA + GÖRÜNÜM NİYETİ --------------------------------------------------

def test_ASK_ZINCIRI_cube_cevabi(client):
    d = client.post("/ask", json={"question": "bu yıl müşteri bazında ciro listele",
                                  "session_id": "r2", "execute": True}).json()
    assert d.get("source") == "cube", f"source={d.get('source')} not={d.get('note')!r}"
    assert (d.get("cube_query") or {}).get("dimensions") == ["musteri"]
    assert (d.get("result") or {}).get("row_count")


def test_LISTE_niyeti_TABLO_gorunumu_ister(client):
    """*"listele"* diyen kullanıcı SATIRLARI görmek istiyor. Deterministik grafik kararı
    (ADR-0024) `bar` diyor ve teknik olarak haklı — ama kullanıcının AÇIKÇA söylediği şey
    bu değil. ADR-0024 ihlal edilmiyor: `viz` deterministik kalıyor, `view_hint` yalnız
    açık isteği taşıyor."""
    d = client.post("/ask", json={"question": "bu yıl müşteri bazında ciro listele",
                                  "session_id": "r2v", "execute": True}).json()
    assert d.get("view_hint") == "table"
    assert (d.get("viz") or {}).get("kind"), "viz kararı kaybolmuş olmamalı"


def test_ACIK_GRAFIK_istegi_TABLOYU_yener(client):
    """*"dökümü PASTA grafik yap"* — açık tip isteği liste varsayılanının ÜSTÜNDE."""
    d = client.post("/ask", json={"question": "bu yıl müşteri bazında ciro dökümü pasta grafik",
                                  "session_id": "r2v", "execute": True}).json()
    assert d.get("view_hint") == "pie"


def test_DONEMSIZ_liste_DONEMI_BEYAN_EDER(client):
    """Liste niyeti dönem kapısını devre dışı bırakmamalı.

    ⟳ **BEKLENTİ GÜNCELLENDİ (2026-08-10, `D3`) — ve gerekçesi bir ÖLÇÜMdür.**

    Bu test *«hâlâ SORUYOR mu»* diye kilitliyordu ve `varsayilan_donem` **kapalıyken**
    doğruydu. Bayrak `D3`'te ölçülüp **açıldı**: korpus doğru-cube **%94,9 → %95,0**,
    🔴 `sessiz_yanlis` **8 → 8 (değişmedi)** → `F1.1`'in durdurma şartı tetiklenmedi.

    ⊙ Değişmeyen şey **kapının kendisi**: dönem hâlâ bir karar noktası ve cevap hâlâ
    onu **beyan ediyor** — yalnız artık *sormak* yerine *söyleyerek varsayıyor*:
    *«⏱ Dönem belirtmedin — verinin son 12 ayı alındı (…). Başka bir dönem yazarsan
    onu uygularım.»* Netleştirme **kaldırılmadı**, ikinci seçenek oldu (aralık
    ölçülemezse fail-closed olarak yine sorar).

    🔴 Bu yüzden kilit **gevşetilmedi, YÖNÜ değişti**: eskiden *«soru soruyor mu»*,
    şimdi *«dönemi beyan ediyor mu»*. İkisi de aynı şeyi korur — **sessiz bir dönem
    varsayımı yasaktır**. *Bir varsayımı yapmak değil, yaptığını söylememek yasaktır.*

    ⚠ `D1`'in dersi burada uygulandı: bir bayrağın durumunu teste bağlamak değiştirmeyi
    zorlaştırmak için değil, **değiştirenin gerekçe yazmasını zorunlu kılmak** içindir.
    """
    d = client.post("/ask", json={"question": "müşteri bazında ciro listele",
                                  "session_id": "r2p", "execute": True}).json()
    assert d.get("note") and "dönem" in d["note"].lower(), \
        "🔴 dönem sessizce varsayıldı — beyan YOK"
    # 🔴 Ya cevap üretilip dönem BEYAN edilir, ya da netleştirme chip'leri sunulur.
    # İkisi de olmuyorsa dönem sessizce seçilmiş demektir ve o yasak.
    assert (d.get("cube_query") or {}).get("filters") \
        or [s["label"] for s in (d.get("suggestions") or [])], \
        "🔴 ne dönem süzgeci ne netleştirme — kapı fiilen kalkmış"
