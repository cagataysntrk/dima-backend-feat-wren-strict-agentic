"""FAZ G1 — takip sorusunun ÜÇÜNCÜ sınıfı: "cevap üstünde konuşma".

## Ölçülen boşluk (2 Ağustos 2026, canlı `/ask` üzerinden)

Bir `parti` raporu üstünde sorulan altı sorunun **altısı da** duvara çarpıyordu:

    "bu neden böyle?"          → "Bu takip mesajını önceki raporla ilişkilendiremedim."
    "normal mi?"               → aynı ölü uç
    "ne yapmalıyız?"           → aynı ölü uç
    "şu düşüş ne?"             → "«dusus» kısmını anlayamadım"
    "bunu nasıl iyileştiririz?"→ "«bunu» yerine «gunu» mi demek istedin?"   ← anlamsız
    "sence iyi mi?"            → aynı ölü uç

Çünkü takip soruları **iki** sınıfa ayrılıyordu: sorguyu düzenle, ya da yeni ham SQL yaz.
*"Verdiğin cevap hakkında konuş"* diye bir sınıf yoktu.

## Bu sınıfın tanımı ve neden Discovery'ye DÜŞMEMELİ

Konuşma sınıfı **yeni bir cevap üretmez, var olanı açar**. Discovery'ye düşerse bağlamsız
ham SQL yazılır ve ölü tablo döner — ölçülen sorun tam olarak budur. Bir soru *"bu cevap
hakkında"* ise cevabı zaten elimizdedir; yeni SQL yazmak yanlış araçtır.
"""

from __future__ import annotations

import pytest

from app import followup as fu


def _s(soru: str, baglam_var: bool = True):
    return fu.sinifla(soru, baglam_var=baglam_var)


# --- ASIL KAPI: ölçülen altı soru artık konuşma sınıfında -----------------------

@pytest.mark.parametrize("soru,tur", [
    ("bu neden böyle?", fu.TUR_NEDEN),
    ("normal mi?", fu.TUR_NORMAL),
    ("ne yapmalıyız?", fu.TUR_NE_YAPMALI),
    ("şu düşüş ne?", fu.TUR_ISARET),
    ("bunu nasıl iyileştiririz?", fu.TUR_NE_YAPMALI),
    ("sence iyi mi?", fu.TUR_NORMAL),
])
def test_OLCULEN_ALTI_soru_konusma_sinifinda(soru, tur):
    """Bu altı soru canlı sistemde ölü uca çarpıyordu — ölçüldü, kayda geçti."""
    n = _s(soru)
    assert n.konusma, f"{soru!r} hâlâ {n.sinif!r} sınıfında (kural={n.kural})"
    assert n.tur == tur, f"{soru!r} → {n.tur} (beklenen {tur})"
    assert n.kanit, "hangi kalıbın eşleştiği kaydedilmemiş"


@pytest.mark.parametrize("soru", [
    "niçin arttı?", "niye?", "sebebi ne?", "bu nereden geliyor?",
    "bu sonuç olağan mı?", "endişelenmeli miyiz?", "burada bir sorun var mı?",
    "ne önerirsin?", "hangi aksiyonu almalıyız?", "bunu nasıl azaltırız?",
    "şu sıçrama ne?", "buradaki anomali ne?",
])
def test_konusma_dagarcigi(soru):
    assert _s(soru).konusma, f"{soru!r} konuşma sınıfına girmedi"


# --- YAPISAL ÖNCELİĞİ ------------------------------------------------------------

@pytest.mark.parametrize("soru", [
    "aylık", "makine bazında", "en yüksek 5", "renk kırılımı",
    "grafik ver", "çeyreklik göster", "sırala",
])
def test_yapisal_duzenleme_KONUSMA_degil(soru):
    """Bunlar sorguyu DEĞİŞTİRİR — konuşma sınıfına girerse kullanıcı beklediği yeni
    sayıları alamaz ve bunun yerine eski sonucun yorumunu görür."""
    assert _s(soru).sinif == fu.SINIF_YAPISAL, soru


def test_KARISIK_soruda_yapisal_KAZANIR():
    """"aylık neden düştü?" hem düzenleme hem konuşma gibi görünür. Öncelik yapısaldadır:
    kullanıcı yeni sayılar bekliyorsa önce onları vermek gerekir — konuşma bir sonraki
    turda hâlâ mümkündür, ama YANLIŞ SAYI geri alınamaz."""
    n = _s("aylık neden düştü?")
    assert n.sinif == fu.SINIF_YAPISAL and n.kanit == "aylik"


# --- BAĞLAM KAPISI ---------------------------------------------------------------

def test_baglam_YOKSA_konusma_TANIMSIZ():
    """Konuşulacak bir cevap yoksa "cevap üstünde konuşma" tanımsızdır. Bu kapı olmadan
    "bu neden böyle?" diye BAŞLAYAN bir oturum konuşma sınıfına düşer ve çapalanacağı
    bir makbuz bulamaz."""
    n = _s("bu neden böyle?", baglam_var=False)
    assert n.sinif == fu.SINIF_YENI and n.kural == "baglam-yok"


# --- YANLIŞ POZİTİF: yeni konular konuşma sanılmamalı ---------------------------

@pytest.mark.parametrize("soru", [
    "peki ciro?", "bu yıl fire", "makine listesi", "merhaba",
    "operatör bazında rework kg", "geçen ay oee",
])
def test_yeni_konu_KONUSMA_degil(soru):
    n = _s(soru)
    assert not n.konusma, f"{soru!r} yanlışlıkla konuşma sınıfına düştü (kanıt={n.kanit!r})"


def test_UZUN_neden_sorusu_ZAMIR_ister():
    """"neden" tek başına YENİ bir soru da olabilir ("fire neden yüksek olur?"). Uzun
    cümlelerde soruyu eldeki cevaba bağlayan bir işaret zamiri aranır."""
    assert not _s("fire oranı neden yüksek olur genel olarak").konusma
    assert _s("bu fire oranı neden yüksek?").konusma


def test_KISA_soru_zamir_ISTEMEZ():
    """"neden?" / "niye?" zaten eldeki cevaba dairdir — zamir aramak en doğal konuşma
    biçimini kapı dışında bırakırdı."""
    for q in ("neden?", "niye?", "sebebi?"):
        assert _s(q).konusma, q


# --- kelime sınırı disiplini (Faz D3'ün dersi) ----------------------------------

@pytest.mark.parametrize("soru", ["bedenler bazında", "gunu goster"])
def test_kelime_ORTASINDA_eslesmez(soru):
    """`_syn_hit` disiplini burada da geçerli: "neden" kalıbı "beden"i, "gunu" kalıbı
    başka bir şeyi yakalamamalı. Kural YENİDEN YAZILMAZ — `cube_router._syn_hit` çağrılır."""
    n = _s(soru)
    assert n.tur != fu.TUR_NEDEN, f"{soru!r} sahte 'neden' eşleşmesi verdi"


def test_bos_soru():
    assert _s("").sinif == fu.SINIF_YENI
    assert _s("   ").sinif == fu.SINIF_YENI


# --- makbuz ----------------------------------------------------------------------

def test_makbuz_KARARI_tasir():
    """"Neden bu cevap bu biçimde geldi?" — sınıflandırma kararı da kanıtın parçasıdır."""
    import json

    m = fu.makbuza(_s("bu neden böyle?"))
    assert m["followup_class"] == fu.SINIF_KONUSMA
    assert m["followup_kind"] == fu.TUR_NEDEN
    assert m["followup_rule"] == "konusma:neden" and m["followup_evidence"]
    assert json.dumps(m)


def test_NIYET_degismez():
    n = _s("normal mi?")
    with pytest.raises(Exception):
        n.sinif = "baska"  # type: ignore[misc]


def test_turler_TEKIL_ve_kapali():
    turler = {fu.TUR_NEDEN, fu.TUR_NORMAL, fu.TUR_NE_YAPMALI, fu.TUR_ISARET}
    assert len(turler) == 4
    siniflar = {fu.SINIF_YAPISAL, fu.SINIF_KONUSMA, fu.SINIF_YENI}
    assert len(siniflar) == 3


# --- UÇTAN UCA: ölü uç GERÇEKTEN kapandı mı? ------------------------------------

@pytest.mark.parametrize("soru", [
    "bu neden böyle?", "normal mi?", "ne yapmalıyız?",
    "şu düşüş ne?", "bunu nasıl iyileştiririz?", "sence iyi mi?",
])
def test_UCTAN_UCA_olu_uc_kapandi(client, soru):
    """ASIL KANIT. Sınıflandırıcı saf ve testli olabilir ama BAĞLANMAMIŞSA hiçbir şey
    ifade etmez. Bu test HTTP yolundan geçer ve ölçülen ölü uç metinlerinin ARTIK
    dönmediğini doğrular."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    assert ilk.get("cube_query"), f"ilk cevap kurulamadı: {ilk.get('note')!r}"

    d = ask(client, soru, cube_query=ilk["cube_query"], history=[ilk["question"]])
    note = (d.get("note") or "").lower()
    assert "ilişkilendiremedim" not in note, f"{soru!r} hâlâ ölü uçta"
    assert "demek istedin" not in note, f"{soru!r} anlamsız yazım önerisi aldı"
    # Ya bir sonuç ya tıklanır bulgu — ikisi de yoksa cevap boştur.
    assert d.get("result") or d.get("next_steps"), f"{soru!r} boş cevap döndü"


def test_UCTAN_UCA_konusma_DISCOVERYYE_dusmez(client):
    """Kritik: konuşma sınıfı Discovery'ye düşerse bağlamsız ham SQL yazılır ve ölü
    tablo döner — ölçülen sorun tam olarak buydu."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    d = ask(client, "bu neden böyle?", cube_query=ilk["cube_query"],
            history=[ilk["question"]])
    assert not (d.get("source") or "").startswith("llm:"), "konuşma Discovery'ye düştü"
    assert any("cevap üstünde konuşma" in t for t in (d.get("trace") or [])), \
        f"çapalanma izde görünmüyor: {d.get('trace')}"


def test_UCTAN_UCA_yapisal_takip_BOZULMADI(client):
    """Gerileme kilidi: üçüncü sınıf, yapısal düzenlemenin önüne geçmemeli."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    d = ask(client, "aylık", cube_query=ilk["cube_query"], history=[ilk["question"]])
    assert d.get("result"), f"yapısal takip bozuldu: {d.get('note')!r}"
    assert d.get("source") == "cube"


# --- UI SÖZLEŞMESİ: bulgular CEVABIN GÖVDESİDİR, "sonraki adım" değil ------------

def test_konusma_cevabi_ZENGIN_GOVDE_tasir(client):
    """ÖLÇÜLEN UX KUSURU (2 Ağustos 2026). Bulgular yalnız `next_steps` üzerinden
    taşınıyordu ve UI onları **"SONRAKİ ADIM"** başlığıyla gösteriyordu — yani kullanıcı
    *"bu neden böyle?"* diye soruyor, cevabın KENDİSİ bir "sonraki adım" gibi
    etiketleniyordu. Üstelik Δ tutarları, % paylar ve kırpma uyarısı tamamen
    kayboluyordu (chip yalnız etiket taşır).

    `contribution` alanı cevabın gövdesini taşır ve frontend onu MEVCUT
    `ContributionLayer` bileşeniyle render eder — TEK render edici, ikinci istek YOK.
    """
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    d = ask(client, "bu neden böyle?", cube_query=ilk["cube_query"],
            history=[ilk["question"]])

    k = d.get("contribution")
    assert k, "konuşma cevabı zengin gövde taşımıyor — UI chip'e düşer"
    assert k.get("measure") and k.get("mode") in ("yoy", "mom")
    # Dürüstlük kayıtları GÖVDEDE olmalı; chip'te taşınamazlar.
    assert "taranmayan_boyut" in k, "kapsam sınırı kayboldu"
    for r in k.get("raporlar") or []:
        assert "net_degisim" in r and "kirpilan_segment" in r
        for b in r.get("bulgular") or []:
            assert "delta" in b and "net_pay" in b and b.get("cube_query")


def test_yapisal_cevap_contribution_TASIMAZ(client):
    """Gerileme kilidi: normal bir rapor `contribution` taşımamalı — taşısaydı her
    cevapta katkı ayrıştırması ZORLA açılır ve kullanıcı istemediği bir analizle
    karşılaşırdı (kademeli açılım ilkesinin ihlali, MIMARI §14.2)."""
    from tests.conftest import ask

    d = ask(client, "bu yıl makine bazında işlenen kg")
    assert not d.get("contribution"), "istenmeden katkı ayrıştırması döndü"


# --- G2: GRAFİĞE ÇAPA — "nisandaki sıçrama" yapısal bir SEÇİMDİR ----------------

def test_capa_ALT_SORGUYA_cevrilir(client):
    """ASIL KAPI. Kullanıcı bir grafik hücresine işaret edip *"bu neden böyle?"* diyorsa
    konuşma O HÜCRENİN üstünde yürümeli — tüm raporun değil. Çapa bir metin numarası
    değil YAPISAL bir seçimdir: koordinat gerçek bir `cube_query` filtresine çevrilir."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    cq = ilk["cube_query"]
    dim = (cq.get("dimensions") or ["makine"])[0]
    deger = str((ilk["result"]["rows"][0])[dim])

    d = ask(client, "bu neden böyle?", cube_query=cq, history=[ilk["question"]],
            anchor={"dimension": dim, "value": deger})

    assert any("Çapa" in t for t in (d.get("trace") or [])), \
        f"çapa izde görünmüyor: {d.get('trace')}"
    kcq = d.get("cube_query") or {}
    filtreler = {f.get("dimension"): f.get("value") for f in (kcq.get("filters") or [])}
    assert filtreler.get(dim) == deger, "çapa filtreye çevrilmedi"
    assert dim not in (kcq.get("dimensions") or []), \
        "çapalanan boyut kırılımda KALDI — select_cube_query semantiği bozuk"


def test_GECERSIZ_capa_sessizce_yok_sayilir(client):
    """Uydurulmuş bir filtre, filtre olmamasından KÖTÜDÜR: cube'da olmayan bir boyuta
    çapa atılırsa konuşma tüm rapor üstünde yürür ve kullanıcı yanlış bir daraltmayla
    karşılaşmaz."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    # NOT: yapısal olarak BOZUK bir çapa (sözlük değil) Pydantic tarafından ŞEMA
    # seviyesinde 422 ile reddedilir ve bu DAHA İYİDİR — istemci hatası sessizce
    # yutulmaz. Burada sınanan şey farklı: şeması DOĞRU ama anlamı GEÇERSİZ çapa
    # (olmayan boyut, eksik alan). O sessizce yok sayılır çünkü kullanıcı hatası
    # değil bir eşleşme başarısızlığıdır.
    for kotu in ({"dimension": "olmayan_boyut", "value": "x"},
                 {"dimension": "makine"},          # değer yok
                 {"value": "M-01"}):               # boyut yok
        d = ask(client, "bu neden böyle?", cube_query=ilk["cube_query"],
                history=[ilk["question"]], anchor=kotu)
        assert not any("Çapa" in t for t in (d.get("trace") or [])), f"geçersiz çapa uygulandı: {kotu}"
        assert d.get("contribution") or d.get("note"), "cevap tamamen kayboldu"


def test_BOZUK_TIPLI_capa_SEMA_seviyesinde_reddedilir(client):
    """Sözlük olmayan bir çapa `422` alır — sessizce yutulmaz. İstemci hatası ile
    eşleşme başarısızlığı FARKLI şeylerdir ve farklı davranmalıdırlar."""
    r = client.post("/ask", json={"question": "bu neden böyle?", "execute": True,
                                  "session_id": "x", "anchor": "metin degil sozluk"})
    assert r.status_code == 422


def test_capasiz_konusma_BOZULMADI(client):
    """Gerileme kilidi: çapa opsiyoneldir."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    d = ask(client, "bu neden böyle?", cube_query=ilk["cube_query"], history=[ilk["question"]])
    assert d.get("contribution"), "çapasız konuşma bozuldu"
    assert not any("Çapa" in t for t in (d.get("trace") or []))


# --- FAZ F3: kompozisyon PLANLAYICIDAN geçiyor mu? ------------------------------

def test_konusma_AJAN_KOSUSU_izi_tasir(client):
    """F2'nin yönetişimi (bütçe · yetki · adım makbuzu) yazılmıştı ama HİÇBİR YOLA
    BAĞLI DEĞİLDİ — bu turda altı kez ölçtüğüm "beyan var, tüketici yok" sınıfının
    aynısı olurdu. Bu test bağlanmanın GERÇEK olduğunu HTTP yolundan doğrular."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    d = ask(client, "bu neden böyle?", cube_query=ilk["cube_query"], history=[ilk["question"]])
    izler = d.get("trace") or []
    assert any("Ajan koşusu" in t for t in izler), f"planlayıcı izi yok: {izler}"
    # Maliyet GİZLİ KALMAZ: adım ve sorgu sayısı izde görünür.
    kosu = next(t for t in izler if "Ajan koşusu" in t)
    assert "adım" in kosu and "sorgu" in kosu


def test_normal_mi_KAYITLI_araci_planlayicidan_gecirir(client):
    """`yoy.compute` kayıtlı bir araçtır → dört kapıdan geçmeli ve adım olarak sayılmalı."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    d = ask(client, "normal mi?", cube_query=ilk["cube_query"], history=[ilk["question"]])
    if not d.get("result"):
        pytest.skip("bu veri setinde dönemsel kıyas üretilemedi")
    kosu = next((t for t in (d.get("trace") or []) if "Ajan koşusu" in t), "")
    assert kosu and "1 adım" in kosu, f"yoy.compute adım olarak sayılmadı: {kosu!r}"


def test_BILESIK_adim_durustce_isaretlenir():
    """Katkı ayrıştırması kayıtlı TEK bir araç DEĞİL bir bileşiktir (boyut başına ayrı
    sorgu koşar). `tools.KAYIT`'a tek araçmış gibi yazmak YALAN olurdu: ne girdisi
    tipli, ne kapılardan geçiyor.

    `dis_adim` bunu İTİRAF EDER — makbuzda `gated: false` görünür. Kayıtsız bir adımı
    hiç yazmamak, koşumu olduğundan ucuz ve daha denetlenmiş göstermek olurdu."""
    from app.planner import Planlayici

    p = Planlayici()
    p.dis_adim("contribution.report", sure_ms=12, makbuz="c-x", not_="bileşik")
    adim = p.kosum.makbuza()["agent_run"]["steps"][0]
    assert adim["gated"] is False and adim["note"] == "bileşik"
    assert adim["receipt"] == "c-x"
    # Yönetişim eksik olsa da MALİYET MUHASEBESİ eksik değil.
    assert p.kosum.sorgu_sayisi == 1, "bileşik adım bütçeye sayılmadı"


def test_KAPISIZ_adim_da_butceyi_tuketir():
    """Bileşik adımlar kapıdan geçmez ama SINIRSIZ da değildir."""
    from app.planner import Butce, ButceAsimi, Planlayici

    p = Planlayici(butce=Butce(adim=2))
    p.dis_adim("bilesik.a", sure_ms=1)
    p.dis_adim("bilesik.b", sure_ms=1)
    with pytest.raises(ButceAsimi):
        p.calistir("route", "x", {"cubes": []})


# ─────────────────────────────────────────────────────────────────────────────
# FAZ 5.0 — K3: konuşma türleri thread'lerin bir sınıfına YAPISAL OLARAK kapalıydı
# ─────────────────────────────────────────────────────────────────────────────

def test_FAZ_5_0_sinifla_STRUCTURAL_BLOGUN_DISINDA():
    """🔴 **Kusurun kendisi yapısaldı** — ve düzeltmesi de yapısal olarak kilitlenmeli.

    `followup.sinifla`'nın TEK çağrısı `if structural_followup:` bloğunun **İÇİNDEYDİ**:
    istemci `cube_query` göndermiyorsa (Discovery / ham thread) beş konuşma türü de
    **erişilemezdi**. Bir gün biri çağrıyı yine bir `if`in içine taşırsa, bu kapı kırmızı
    olur.

    ⚠ Belirteç **AST**: `ask.py` 1.900+ satır ve bu kusurun kendi gerekçesi *"bir çağrının
    yanlış `if`in içinde olduğu görünmüyor"*. Alt-dize taraması onu da göremezdi.
    """
    import ast as _ast
    from pathlib import Path

    kaynak = (Path(__file__).resolve().parents[1] / "app/routers/ask.py").read_text(
        encoding="utf-8")
    agac = _ast.parse(kaynak)

    def _sinifla_cagrilari(dugum, kosul_icinde: bool):
        out = []
        for c in _ast.iter_child_nodes(dugum):
            icinde = kosul_icinde or isinstance(dugum, _ast.If)
            if (isinstance(c, _ast.Call)
                    and getattr(c.func, "attr", "") == "sinifla"
                    and getattr(getattr(c.func, "value", None), "id", "") == "followup"):
                out.append((c.lineno, kosul_icinde))
            out += _sinifla_cagrilari(c, icinde)
        return out

    cagrilar = _sinifla_cagrilari(agac, False)
    assert cagrilar, "🔴 `followup.sinifla` HİÇ çağrılmıyor — beş konuşma türü ölü."
    assert len(cagrilar) == 1, (
        f"🔴 `followup.sinifla` {len(cagrilar)} yerde çağrılıyor. Aynı kuralın iki "
        f"sahibi olursa ikisi AYRIŞIR — sınıflandırma tek yerde yapılmalı.")
    satir, if_icinde = cagrilar[0]
    assert not if_icinde, (
        f"🔴 `followup.sinifla` çağrısı (satır {satir}) yine bir `if` bloğunun İÇİNDE. "
        f"FAZ 5.0'ın düzelttiği kusur tam olarak buydu: `cube_query` göndermeyen "
        f"thread'lerde beş konuşma türü de ERİŞİLEMEZ olur.")


def test_FAZ_5_0_baglam_var_SABIT_TRUE_degil():
    """🔴 `baglam_var=True` sabitti → *"bağlam-yok"* kuralı **üretimde hiç ateşlenmiyordu**.

    *Sabit bir `True`, bir bayrak değil bir yalandır:* fonksiyonun imzası bir soru
    soruyor ve çağıran her seferinde aynı cevabı veriyorsa, o parametre yoktur.
    """
    import ast as _ast
    from pathlib import Path

    agac = _ast.parse((Path(__file__).resolve().parents[1] / "app/routers/ask.py")
                      .read_text(encoding="utf-8"))
    for c in _ast.walk(agac):
        if (isinstance(c, _ast.Call) and getattr(c.func, "attr", "") == "sinifla"):
            for kw in c.keywords:
                if kw.arg == "baglam_var":
                    assert not (isinstance(kw.value, _ast.Constant)
                                and kw.value.value is True), (
                        "🔴 `baglam_var=True` yine SABİT. `followup.py`'nin 'bağlam-yok' "
                        "kuralı üretimde hiç ateşlenmez ve yalnız birim testinde yaşar.")


def test_FAZ_5_0_baglam_YOKKEN_konusma_sinifi_ACILMAZ():
    """Bağlam gerçekten yoksa *"bu neden böyle?"* bir **yeni konudur** — çapalanacak
    bir makbuz yoktur."""
    from app import followup

    n = followup.sinifla("bu neden böyle?", baglam_var=False)
    assert n.sinif == followup.SINIF_YENI
    assert n.kural == "baglam-yok"


def test_FAZ_5_0_baglam_VARKEN_konusma_sinifi_ACILIR():
    """Bağlam varsa — **`cube_query` olmasa bile** — tür tanınır.

    Ham thread'de (Discovery ile başlamış bir sohbet) kullanıcı *"bu neden böyle?"*
    dediğinde artık sınıf **biliniyor**. Bu, 5.1/5.2'nin doğduğu andan itibaren her
    thread sınıfında çalışmasının ön koşulu.
    """
    from app import followup

    n = followup.sinifla("bu neden böyle?", baglam_var=True)
    assert n.sinif == followup.SINIF_KONUSMA
    assert n.tur == followup.TUR_NEDEN


def test_NC_CIPLAK_NEDEN_YAPISAL_SAYILMAZ():
    """🔴🔴 `§NÇ` — ölçüldü (curl `FF` turu, FF-6): *«departman bazında bu yıl kaza
    adedi»* → *«**neden**»* → `refine → deterministik düzenleme`, **8 satır**, açıklama
    **YOK**. `isg.kok_neden`'in sinonimleri arasında birebir «neden» var ve o boyut
    ekranda değil — kural *«kullanıcı yeni satır istiyor»* diye okudu.

    ⚠ Doğru ayrım bu dosyada **zaten yazılıydı**: `_kisa_soru`'nun docstring'i tam bu
    örneği veriyor (*«Çok kısa takip soruları («neden?», «niye?») zaten eldeki cevaba
    dairdir»*). `§NÇ` o yüklemi sormuyordu.

    *Bir dosyada iki kural aynı ayrımı yapıyorsa, biri ötekini sormak zorundadır.*"""
    from app import followup

    n = followup.sinifla("neden", baglam_var=True, acik_boyutlar=["neden", "kok neden"])
    assert n.sinif == followup.SINIF_KONUSMA, (n.sinif, n.kural)
    assert n.tur == followup.TUR_NEDEN


def test_NC_OLCULEN_DOGRU_POZITIF_KORUNUR():
    """Daraltma doğru-pozitifi öldürmemeli: *«en büyük **nedeni** hangi makinede»* beş
    kelimedir, kısa soru değildir → kural aynen ateşler ve tur **yapısal** kalır."""
    from app import followup

    n = followup.sinifla("en buyuk nedeni hangi makinede", baglam_var=True,
                         acik_boyutlar=["neden", "kok neden"])
    assert n.sinif == followup.SINIF_YAPISAL, (n.sinif, n.kural)
    assert n.kural == "§NÇ:ekranda-olmayan-boyut"
