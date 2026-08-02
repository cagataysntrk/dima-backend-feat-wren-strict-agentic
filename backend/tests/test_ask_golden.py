"""Uçtan uca /ask golden'ları — gerçek loglardan türetilmiş konuşma akışları.

Deterministik koşum (provider=rule): meta, clarification, dönem chip'i, cube route ve
deterministik refine yolları ölçülür. Satır sayısı yalnız tarihten bağımsız vakalarda
kesin asserte edilir (veri Ocak–Tem 2026; bugün ilerledikçe dönemli sayılar değişir).
"""

from __future__ import annotations

from tests.conftest import ask

# --- meta/ürün soruları → yardım + örnek chip'leri ---------------------------

def test_meta_dima_nedir(client):
    d = ask(client, "dima nedir?")
    assert d["note"] and "dima" in d["note"]
    # Faz 1: source="meta" BİLİNÇLİ (route-dağılımı telemetrisi, /sadmin/interactions/
    # route-distribution — LLM'e HİÇ düşmeyen yolları None'dan ayırt eder). SQL yok.
    assert d["source"] == "meta" and not d["sql"]
    # Örnekler AKTİF KATALOGDAN üretilir (ADR-0018 d) — hard-coded değil.
    labels = [s["label"].lower() for s in d["suggestions"]]
    assert any("oee" in l for l in labels)  # boyahane kataloğundan gerçek örnek


def test_meta_dima_kimin(client):
    d = ask(client, "dima kimin?")
    assert d["note"] and d["source"] == "meta"  # log satır 25 regresyonu: rule/garbage değil


def test_meta_selamlama(client):
    d = ask(client, "merhaba")
    assert d["note"] and d["source"] == "meta"


def test_randiman_meta_degil(client):
    """'ranDIMAn' kelimesi 'dima' altdizisi içerir — meta sanılmamalı (tam-kelime).
    Dönem yok → clarification gelir ama cube_query DOĞRU kurulmuş olmalı."""
    d = ask(client, "cihaz bazında randıman")
    assert "dönem" in (d["note"] or "").lower()  # meta yardımı DEĞİL, dönem sorusu
    assert d["cube_query"]["measures"] == ["ort_oee"]
    assert d["cube_query"]["dimensions"] == ["makine"]


# --- deterministik cube yolu (dönem sorusu + "Tümü" chip'i ile) --------------
# Politika (kullanıcı kararı): dönem bilgisi yoksa KIRILIMLI sorularda da sorulur —
# sessiz tüm-zaman toplama yok; "Tümü" chip'i bilinçli tüm-zamanı tek tık yapar.

def _ask_all_time(client, q):
    """Soru → dönem clarification → 'Tümü' chip'i → rapor."""
    d1 = ask(client, q)
    assert "dönem" in (d1["note"] or "").lower(), f"clarification bekleniyordu: {d1}"
    assert any(s["label"] == "Tümü" for s in d1["suggestions"])
    return ask(client, "tüm zamanlar", cube_query=d1["cube_query"])


def test_cube_makine_oee(client):
    d = _ask_all_time(client, "makine bazında ortalama oee")
    assert d["source"] == "cube"
    assert d["result"]["row_count"] == 11  # 11 makine (47-tablo şema) — tarihten bağımsız
    assert d["cube_query"]["dimensions"] == ["makine"]
    assert "tüm zamanlar" in " ".join(d["trace"])  # bilinçli, sessiz değil
    # Madde 12 (1 Ağustos 2026): drill.py::formula_explanation artık normal /ask cevabında
    # da dolu — önceden yalnız /ask/drill'e bağlıydı (tests/test_drill.py'nin BİREBİR aynı
    # fonksiyonu, burada uçtan uca /ask akışında).
    assert d["calculation_explanation"]
    assert "makine bazında kırılımıdır" in d["calculation_explanation"]


def test_thread_id_pass_through_ask_ve_cube(client):
    """§B (Adım 0, 1 Ağustos 2026): thread_id salt PASS-THROUGH — is_followup/is_new_topic
    mantığına karışmaz, /ask VE /cube (chip düzenlemesi) yanıtlarına AYNEN echo edilir.
    Gönderilmezse None kalır (mevcut davranış bozulmaz)."""
    d0 = ask(client, "makine bazında ortalama oee")
    assert d0["thread_id"] is None  # gönderilmedi → None
    d1 = ask(client, "makine bazında ortalama oee", thread_id="t-abc")
    assert d1["thread_id"] == "t-abc"
    d2 = ask(client, "tüm zamanlar", cube_query=d1["cube_query"], thread_id="t-abc")
    assert d2["source"] == "cube"
    assert d2["thread_id"] == "t-abc"
    r = client.post("/cube", json={"cube_query": d2["cube_query"], "label": "test",
                                    "thread_id": "t-xyz"})
    assert r.status_code == 200 and r.json()["thread_id"] == "t-xyz"


def test_is_new_topic_taze_soruda_true_takipte_false(client):
    """§B (Madde 4+6, 1 Ağustos 2026): is_new_topic — bağımsız (taze) sorularda True, aynı
    raporun takibinde (cube_query gönderilince) False. Mevcut is_followup sinyalinin
    TERSİ — yeni mantık YOK, yalnız frontend'e taşınıyor (ChatPanel "yeni konu" ayracı,
    ReportPanel breadcrumb'ı)."""
    d1 = ask(client, "makine bazında ortalama oee")
    assert "dönem" in (d1["note"] or "").lower()
    assert d1["is_new_topic"] is True  # bağımsız soru, cube_query/prev_sql yok
    d2 = ask(client, "tüm zamanlar", cube_query=d1["cube_query"])
    assert d2["source"] == "cube"
    assert d2["is_new_topic"] is False  # yapısal takip (cube_query gönderildi)


def test_cube_query_olmayan_yanitta_calculation_explanation_yok(client):
    """cube_query YOKSA (ör. Discovery/LLM-kaynaklı ham-SQL cevapları, ya da bu testteki
    gibi dürüst-ret) deterministik formül-açıklama ÜRETİLEMEZ — dürüstçe None kalır
    (uydurma YOK, Madde 12'nin bilinçli sınırı — _attach_viz yalnız `cq` doluyken çalışır)."""
    d = ask(client, "kar oranı fizibilite")
    assert d["source"] is None  # kısmi anlama, dürüst ret (mevcut davranış)
    assert d.get("calculation_explanation") is None


def test_cube_hafta_gunu_grid(client):
    d = _ask_all_time(client, "Vardiya × haftanın günü verimliliği")
    assert d["source"] == "cube"
    assert d["result"]["row_count"] == 18  # 3 vardiya × 6 gün (üretim Pzt–Cmt) — tarihten bağımsız


def test_trendli_soru_donem_sormaz(client):
    """timeDimensions (aylık trend) zaten zaman ekseni taşır → dönem sorulmaz."""
    d = ask(client, "aylık üretim trendi")
    assert d["source"] == "cube" and d["result"] is not None
    assert d["cube_query"]["timeDimensions"][0]["granularity"] == "month"


# --- viz önerisi uçtan-uca (ADR-0024): endpoint viz'i iliştirir, motor kararı verir --------

def test_viz_attached_bar_for_category(client):
    """Tek kategorik boyut + ölçü → viz.kind bar (Show Me); endpoint viz alanını doldurur."""
    d = _ask_all_time(client, "makine bazında ortalama oee")
    assert d["viz"] is not None
    assert d["viz"]["kind"] == "bar"
    assert d["viz"]["primary_dim"] == "makine"


def test_viz_heatmap_for_two_category_grid(client):
    """Vardiya × gün matrisi (min eksen ≥3) → viz.kind heatmap."""
    d = _ask_all_time(client, "Vardiya × haftanın günü verimliliği")
    assert d["viz"] is not None and d["viz"]["kind"] == "heatmap"


def test_viz_line_for_time_series(client):
    """Zaman ekseni (aylık) → viz.kind line."""
    d = ask(client, "aylık üretim trendi")
    assert d["viz"] is not None and d["viz"]["kind"] == "line"
    assert d["viz"]["time_col"] is not None


# --- çok-blok / çok-sayfa rapor derleme (ADR-0024, /report) ------------------

def test_report_composes_pages_with_viz(client):
    """İki blok (kategori bar + zaman line) → sayfalı Report; her blok kendi viz kararını taşır."""
    oee = _ask_all_time(client, "makine bazında ortalama oee")
    trend = ask(client, "aylık üretim trendi")
    body = {
        "title": "Yönetim Raporu",
        "page_size": 1,
        "blocks": [
            {"cube_query": oee["cube_query"], "title": "Makine OEE", "period": "tüm zamanlar"},
            {"cube_query": trend["cube_query"], "title": "Aylık üretim"},
        ],
    }
    r = client.post("/report", json=body)
    assert r.status_code == 200, r.text
    rep = r.json()
    assert rep["title"] == "Yönetim Raporu"
    assert rep["block_count"] == 2
    assert len(rep["pages"]) == 2  # page_size=1 → iki sayfa
    b0 = rep["pages"][0][0]
    assert b0["title"] == "Makine OEE" and b0["result"] is not None
    assert b0["viz"]["kind"] == "bar"
    b1 = rep["pages"][1][0]
    assert b1["viz"]["kind"] == "line"


def test_report_skips_invalid_block(client):
    """Bozuk/eski cube_query bloğu raporu düşürmez — atlanır."""
    trend = ask(client, "aylık üretim trendi")
    body = {"blocks": [
        {"cube_query": {"cube": "yok_boyle_bir_cube", "measures": ["x"]}},
        {"cube_query": trend["cube_query"], "title": "Trend"},
    ]}
    r = client.post("/report", json=body)
    assert r.status_code == 200, r.text
    assert r.json()["block_count"] == 1  # geçersiz atlandı


def test_typo_sessiz_yanlis_cube_donmez(client):
    """Log satır 10 regresyonu: typo'da dejenere tüm-zaman cube DÖNMEMELİ."""
    d = ask(client, "m<kina bazında oee")
    bad = d["source"] == "cube" and not (d.get("cube_query") or {}).get("dimensions")
    assert not bad, f"sessiz-yanlış cube döndü: {d['sql']}"


# --- Faz C: dönem clarification + chip ---------------------------------------

def test_clarify_toplam_uretim(client):
    d = ask(client, "toplam üretim")
    assert d["note"] and "dönem" in d["note"].lower()
    assert [s["label"] for s in d["suggestions"]] == ["Bugün", "Bu hafta", "Bu ay", "Bu yıl", "Tümü"]
    assert d["cube_query"]["measures"] == ["toplam_uretim_kg"]  # kısmi durum taşınır


def test_clarify_then_period_chip(client):
    d1 = ask(client, "toplam üretim")
    d2 = ask(client, "bu yıl", cube_query=d1["cube_query"])
    assert d2["source"] == "cube"
    assert "tarih >=" in d2["sql"]
    assert d2["result"]["row_count"] == 1


def test_tumu_chipi_tarih_filtresini_kaldirir(client):
    """Log regresyonu: "bu yıl"dan sonra "Tümü" seçilirse eski tarih filtresi SİLİNMELİ."""
    d1 = ask(client, "toplam üretim")
    d2 = ask(client, "bu yıl", cube_query=d1["cube_query"])
    assert "tarih >=" in d2["sql"]
    d3 = ask(client, "tüm zamanlar", cube_query=d2["cube_query"])
    assert d3["source"] == "cube"
    # tarih FİLTRESİ kalktı ("tarih" kelimesi hafta-günü ifadesinde geçebilir)
    assert "tarih >=" not in d3["sql"] and "tarih <=" not in d3["sql"]
    assert "tüm zamanlar" in " ".join(d3["trace"])


def test_personel_sinonimi_operator_boyutuna_coz(client):
    """Madde 11 (kısmi, 1 Ağustos 2026): "personel" kelimesi route()'un kapsam-kapısında
    tanınmıyordu (yalnız "operatör/çalışan/kişi baz" sinonimleri vardı) — bu YÜZDEN
    "personel bazında ..." soruları dürüstçe LLM'e bırakılıyordu (sessiz yanlış değil,
    ama gereksiz bir LLM turu). Artık operator boyutunun sinonim listesinde — "operatör
    bazlı" ile AYNI deterministik yola (parti/operator) düşmeli."""
    d = ask(client, "personel bazında işlenen kg")
    # "işlenen kg" period_optional DEĞİL → dönem sorulur (test_kirilimli_soru_da_donem_sorar
    # ile AYNI politika) — asıl kontrol edilen "personel" kelimesinin route()'u LLM'e
    # DÜŞÜRMEDEN parti/operator'a ÇÖZMESİ (cube_query zaten DOĞRU kurulmuş olmalı).
    assert "dönem" in (d["note"] or "").lower()
    assert d["cube_query"]["cube"] == "parti"
    assert d["cube_query"]["dimensions"] == ["operator"]
    d2 = ask(client, "bu yıl", cube_query=d["cube_query"])
    assert d2["source"] == "cube"


def test_kirilimli_soru_da_donem_sorar(client):
    """Kırılım olsa da dönem yoksa sorulur (sessiz tüm-zaman yok — kullanıcı kararı).
    Kişi-demografi (cinsiyet/operatör) parti cube'unda (operatör→personel köprüsü) —
    OEE makine metriği kişi taşımaz; kişi-verimliliği partide. Filtre+kırılım korunur."""
    d = ask(client, "kadın operatörlerin haftanın günü bazında işlenen kg")
    assert d["note"] and "dönem" in d["note"].lower()
    cq = d["cube_query"]
    assert cq["cube"] == "parti"
    assert "hafta_gunu" in cq["dimensions"]  # kırılım + filtre korunarak sorulur
    assert {"dimension": "cinsiyet", "operator": "eq", "value": "Kadın"} in cq["filters"]
    # "Bu yıl" chip'i → filtreli + kırılımlı rapor
    d2 = ask(client, "bu yıl", cube_query=cq)
    assert d2["source"] == "cube" and "tarih >=" in d2["sql"]
    assert d2["result"]["row_count"] == 12  # kadın operatörler × üretim yaptıkları gün×operatör


# --- konuşmasal deterministik refine (log satır 45-48 akışı) -----------------

def test_convo_uretim_donem_aylara_gore(client):
    d1 = ask(client, "toplam üretim")
    d2 = ask(client, "son 6 ay", cube_query=d1["cube_query"])
    assert d2["source"] == "cube" and "tarih >=" in d2["sql"]
    d3 = ask(client, "aylara göre toplam üretim", cube_query=d2["cube_query"])
    assert d3["source"] == "cube"  # LLM'siz (provider=rule'da bile çalışmalı)
    assert "refine → deterministik düzenleme" in d3["trace"]
    assert d3["cube_query"]["timeDimensions"][0]["granularity"] == "month"
    # dönem filtresi zincir boyunca korunur
    assert any(f["dimension"] == "tarih" for f in d3["cube_query"]["filters"])


def test_convo_kirilim_ekleme(client):
    # NOT (Faz 1.5, "Tümü chip" politikası — bkz. _ask_all_time): dönemsiz kırılımlı
    # sorular dönem sorar; "Tümü" chip'i tıklanıp bilinçli tüm-zaman seçilir, sonra
    # kırılım eklenir — testin amacı (deterministik refine ile boyut ekleme) korunur.
    d1 = ask(client, "makine bazında ortalama oee")
    d1b = ask(client, "tüm zamanlar", cube_query=d1["cube_query"])
    assert d1b["source"] == "cube"
    d2 = ask(client, "vardiyalara göre de", cube_query=d1b["cube_query"])
    assert d2["source"] == "cube"
    assert d2["cube_query"]["dimensions"] == ["makine", "vardiya"]
    assert d2["result"]["row_count"] == 33  # 11 makine × 3 vardiya — tarihten bağımsız


def test_convo_anlasilmayan_takip_serbest_sqle_dusmez(client):
    d1 = ask(client, "makine bazında ortalama oee")
    d2 = ask(client, "asdlkj qwerty zxcvb", cube_query=d1["cube_query"])
    # provider=rule'da refine yok → dürüst not; ASLA alakasız rapor değil
    assert d2["note"] and d2["source"] is None


def test_yapisal_takip_cikmazi_gercek_kelime_varsa_discoverye_duser(client):
    """1 Ağustos 2026 canlı bulgu: "personel bazlı verimlilikleri karşılaştır son 6 ay" bir
    OEE thread'i içinde (structural followup) deterministik zincirin TAMAMI (refine/cross_
    cube_*/fresh route()) tükeniyordu — OEE'de personel boyutu yok, parti'de OEE ölçüsü yok
    (bkz. cube_router Bug 4). Eskiden bu doğrudan dürüst ret dönerdi; ama AYNI soru taze/
    yeni-thread'den sorulunca Discovery (cube sınırlarının ÖTESİNDE serbest join) GERÇEKTEN
    cevaplayabiliyordu (canlı interaction_log kanıtı). Yukarıdaki gibberish testinin TERSİ:
    `_match_cube` mesajda GERÇEK katalog kanıtı ("verim" → oee) bulduğu için artık dürüst ret
    DEĞİL, Discovery'ye düşer.

    GÜNCELLEME (2 Ağustos 2026, Faz 0.4 — kapsam kapısı ek-farkında yapıldı): davranış
    Discovery'den ÇAPRAZ-KONU NETLEŞTİRMESİNE taşındı ve bu bilinçli bir İYİLEŞTİRMEDİR.
    Kök neden: eski `_uncovered` herhangi-konum alt-dizi kullandığı için `"son"` (son 6 ay)
    kelimesi `"personel"`i SAHTE olarak kapsıyordu — yani sistem "personel"i anladığını
    SANIYOR, kapsam kapısından geçiyor ve nihayetinde Discovery'ye düşüyordu. Artık
    `personel` gerçekten kapsanmamış sayılıyor ve `partial_unknowns` doğru cevabı veriyor:

        not:   '"personel" başka bir konu gibi görünüyor. Hangisini istiyorsun?'
        chip'ler: ['oee', 'İK / bordro', 'parti']

    Bu, ölü bir Discovery tablosundan (12,5 sn · 24 bin token · chip yok · drill yok —
    canlı interaction_log kaydı) kesinlikle daha iyidir: kullanıcı tek tıkla TAM yapısal
    bir cevaba gider. ADR-0008'in "belirsizlikte SOR" ilkesiyle de örtüşür.

    GÜNCELLEME 2 (2 Ağustos 2026, Faz D3 — `_syn_hit` de ek-farkında yapıldı): netleştirme
    artık **doğru kelimeyi** gösteriyor. Değişen üç ölçüm:

      1. `ik` cube'u adaylardan DÜŞTÜ. Kimlik sinonimi `"ik"`, `verimlil**ik**leri`nin
         içinden sahte eşleşiyordu — 2 harflik bir cube adının kelime ortasında yakalanması
         `_syn_hit`'in alt-dizi körlüğünün ders kitabı örneğiydi.
      2. Cube `oee` yerine `parti`ye çözülüyor. Soru AÇIKÇA kırılım istiyor ("personel
         bazlı") ve o kırılımı adaylardan YALNIZ `parti` sağlayabiliyor (`operator` boyutu,
         Faz 1.1 ilişki-türevi). Bu, `_match_cube`'un BOYUT-UYUMU ÖNCELİĞİ kuralının
         tasarlandığı gibi çalışmasıdır — `oee` personel kırılımı YAPAMAZ.
      3. Bu yüzden işaretlenen kelime `"personel"` DEĞİL `"verimlilikleri"` oldu — ve bu
         **daha doğrudur**: "personel bazlı" cevaplanabilir bir isteğe karşılık gelir,
         cevaplanamayan şey `verimlilik` ölçüsüdür (o `oee`'de yaşar).

    Testin KORUDUĞU asıl endişe aynı: yapısal zincir tükendiğinde sistem ne SESSİZCE
    YANLIŞ bir cube cevabı verir ne de ÇIPLAK bir "anlamadım" döner. Doğrulama artık
    kelimeyi sabitlemek yerine **DAVRANIŞI** sabitler: işaretlenen kelime soruda GEÇMELİ
    ve chip'ler gerçek katalog kanıtından gelmeli.
    (Faz 1'de `oee` cube'u ilişki-türevi bir personel boyutu kazanınca bu soru
    doğrudan `source="cube"` dönmeli — o zaman bu test yeniden değerlendirilecek.)
    """
    d1 = ask(client, "makine bazında ortalama oee")
    d2 = ask(client, "personel bazlı verimlilikleri karşılaştır son 6 ay",
             cube_query=d1["cube_query"], history=["makine bazında ortalama oee"])
    # (a) SESSİZ-YANLIŞ yok: yanlış bir cube'a zorla oturtulmadı.
    assert d2["source"] != "cube"
    # (b) ÇIPLAK RET yok: ya Discovery bir şey üretti ya da netleştirme chip'i sunuldu.
    chips = [s["label"] for s in (d2.get("suggestions") or [])]
    assert d2["source"] is not None or chips, (
        f"çıplak dürüst ret döndü (chip yok, source yok): {d2.get('note')!r}"
    )
    # (c) Netleştirme yolundaysa: işaretlenen kelime UYDURULMAMIŞ olmalı (soruda geçmeli)
    #     ve aday konular GERÇEK katalog kanıtından gelmeli.
    if d2["source"] is None:
        note = (d2.get("note") or "").lower()
        soru_kokleri = ("personel", "verimlilik")
        assert any(k in note for k in soru_kokleri), (
            f"netleştirme soruda geçmeyen bir kelimeyi işaretledi: {note!r}")
        assert any("oee" in c.lower() for c in chips), chips


def test_raw_followup_tuzagi_yeni_konu_intent_pathe_doner(client):
    """1 Ağustos 2026 — "raw_followup tuzağı": bir thread'in İLK turu Discovery'ye (ham-SQL)
    düşerse (yalnız prev_sql+history dolu, cube_query YOK) eskiden `_try_fresh_intent()` bir
    daha ASLA denenmezdi — konu TAMAMEN değişse, yeni soru route() ile kolayca deterministik
    çözülebilir olsa BİLE, generate_followup_sql'e (ham-SQL "takip düzenlemesi") giderdi.
    Artık raw takipten önce _try_fresh_intent() bir kez denenir; route() kendinden eminse
    (Intent-path) o kazanır. Dönem AÇIKÇA belirtilir ("tüm zamanlar") ki route() bir
    clarification chip'ine (dönem sorusu) DEĞİL, doğrudan source=cube'a düşsün."""
    d = ask(client, "makine bazında ortalama oee tüm zamanlar",
            prev_sql="SELECT 1 AS x", history=["alakasız bir önceki soru"])
    assert d["source"] == "cube"
    assert any("Intent-path" in t for t in d["trace"])


def test_raw_followup_gercek_devam_hala_generate_followupa_gider(client):
    """Regresyon kilidi: route()'un ÇÖZEMEYECEĞİ, gerçekten prev_sql'e atıfta bulunan bir
    kırpıntı (cube/ölçü kelimesi taşımıyor) hâlâ mevcut ham-SQL takip akışına gider —
    _try_fresh_intent() eklenmesi BU akışı bozmaz (route() None döner, sessizce eskisi gibi
    generate_followup_sql'e düşülür)."""
    d = ask(client, "temmuzu çıkar",
            prev_sql="SELECT * FROM oee_vardiya", history=["makine bazında ortalama oee"])
    assert d["source"] != "cube"


# --- /cube: yorum çubuğu (chip) düzenlemeleri — deterministik, LLM'siz --------

def test_cube_endpoint_chip_edit(client):
    """Filtre/kırılım chip'i deterministik /cube: cinsiyet boyutu (parti — operatör köprüsü)."""
    cq = {"cube": "parti", "measures": ["toplam_agirlik_kg"], "dimensions": ["cinsiyet"]}
    r = client.post("/cube", json={"cube_query": cq, "label": "chip: cinsiyet → kırılım", "session_id": "eval"})
    assert r.status_code == 200, r.text
    d2 = r.json()
    assert d2["source"] == "cube"
    assert d2["result"]["row_count"] == 2  # Kadın + Erkek
    assert d2["trace"] == ["chip düzenleme → deterministik cube"]


def test_cube_endpoint_rejects_invalid(client):
    r = client.post("/cube", json={"cube_query": {"cube": "oee", "measures": ["uydurma"]}})
    assert r.status_code == 400


# --- ADR-0008: LLM çıktısı doğrulayıcıları (birim) ----------------------------

def test_drop_invented_filters():
    """LLM'in mesajda geçmeyen değer filtreleri ATILIR; meşru olanlar kalır."""
    from app.routers.ask import _drop_invented

    cq = {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["kumas_cinsi"],
          "timeDimensions": [{"dimension": "tarih", "granularity": "day"}],
          "filters": [
              {"dimension": "makine", "operator": "eq", "value": "HT-1"},      # uydurma
              {"dimension": "musteri", "operator": "eq", "value": "Beta Konfeksiyon"},  # uydurma
              {"dimension": "renk", "operator": "eq", "value": "Mavi"},        # mesajda VAR
          ]}
    out = _drop_invented(cq, "mavi kumas turlerine gore fire")
    vals = [f["value"] for f in out.get("filters", [])]
    assert vals == ["Mavi"]
    assert "timeDimensions" not in out  # kimse gün kovası istemedi


def test_drop_invented_prev_tasinan_mesru():
    from app.routers.ask import _drop_invented

    prev = {"filters": [{"dimension": "cinsiyet", "operator": "eq", "value": "Erkek"}]}
    cq = {"cube": "oee", "measures": ["ort_oee"],
          "filters": [{"dimension": "cinsiyet", "operator": "eq", "value": "Erkek"}]}
    out = _drop_invented(cq, "aylara gore", prev)
    assert out["filters"][0]["value"] == "Erkek"  # önceki rapordan taşınan korunur


def test_resolve_period_expr_ve_fallback():
    from app.routers.ask import _resolve_period

    prev = {"filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    cq = {"cube": "oee", "measures": ["ort_oee"]}
    # period_expr çözülür → yeni dönem
    out, unres = _resolve_period(prev, cq, "son 6 ay", "son 6 ay icin")
    assert not unres and out["filters"][0]["operator"] == "gte"
    assert out["filters"][0]["value"] != "2026-01-01"
    # çözülemeyen açık ifade → sor (önceki dönem korunarak)
    out, unres = _resolve_period(prev, cq, "geçen bayram haftası", "gecen bayram haftasi")
    assert unres and out["filters"][0]["value"] == "2026-01-01"
    # ifade yok → önceki dönem taşınır
    out, unres = _resolve_period(prev, cq, None, "vardiyalara gore de")
    assert not unres and out["filters"][0]["value"] == "2026-01-01"
    # tüm zamanlar → tarih kalkar
    out, unres = _resolve_period(prev, cq, "tüm zamanlar", "tum zamanlar")
    assert not unres and "filters" not in out


# --- ADR-0008: kapsam kapısı ---------------------------------------------------

def test_kapsam_kapisi_route(schema):
    """Tanınmayan içerik ("istanbul") → deterministik toplam DÖNMEZ; LLM devralır."""
    from app import cube_router as cr

    assert cr.route("oee istanbul", schema) is None
    assert cr.route("makine bazında ortalama oee", schema) is not None  # tam kapsanan ✓


def test_kapsam_kapisi_refine(schema):
    """No-op yutma kapandı: tanınmayan içerikli takip deterministik kısa devre yapamaz."""
    from app import cube_router as cr
    from app.llm import _norm

    prev = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["hafta_gunu"]}
    assert cr.deterministic_refine(prev, _norm("istanbul için haftanın günü ortalamaları"), schema) is None
    # tam kapsanan no-op hâlâ deterministik (hızlı yol korunur)
    assert cr.deterministic_refine(prev, _norm("haftanın günleri bazında"), schema) is not None


def test_konusuz_soru_tahmin_etmez(client):
    """Log regresyonu: 'bu yıl tüm aylarını karşılaştır' (NEYİ?) — serbest-SQL golden
    örneğini kopyalayıp personel raporu uyduruyordu. Artık ölçü chip'leriyle SORAR."""
    d = ask(client, "bu yıl tüm aylarını karşılaştır")
    assert d["source"] is None and d["note"]
    assert "neyi" in d["note"].lower()
    labels = [s["label"] for s in d["suggestions"]]
    assert labels and any("oee" in l or "verim" in l for l in labels)
    # konulu sorular etkilenmez
    d2 = ask(client, "makine bazında ortalama oee")
    assert d2["note"] is None or "neyi" not in (d2["note"] or "").lower()


# --- provenance & log ----------------------------------------------------------

def test_trace_ve_cube_query_donuyor(client):
    # NOT (Faz 1.5, "Tümü chip" politikası — bkz. _ask_all_time): dönemsiz kırılımlı
    # sorular artık her zaman dönem sorar; bu testin amacı (route() provenance +
    # cube_query round-trip) dönemi mesaja açıkça ekleyerek korunur.
    d = ask(client, "makine bazında ortalama oee bu yıl")
    assert d["trace"] and "cube_router.route" in d["trace"][0]
    assert d["cube_query"] is not None


# --- self-consistency (literatür #1) — birim testleri --------------------------

class _FakeLLM:
    """Sıralı select_cube yanıtları döndüren sahte LLM (oylama testi için)."""
    def __init__(self, answers):
        self._answers = list(answers)
        import threading
        self._lock = threading.Lock()

    def select_cube(self, question, catalog):
        with self._lock:
            return self._answers.pop(0) if self._answers else self._answers[-1]


def test_self_consistency_uyum(schema):
    import json

    from app import cube_router
    from app.routers.ask import _select_consistent

    _, index = cube_router.build_catalog(schema)
    a = json.dumps({"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]})
    cq, agree, axis, _ = _select_consistent(_FakeLLM([a, a, a]), "q", "cat", index, 3)
    assert cq is not None and agree == 1.0 and axis is None


def test_self_consistency_olcu_uyusmazligi(schema):
    """2/3 eşiğinin altında + tek eksen (measures) ayrışması → chip ekseni raporlanır."""
    import json

    from app import cube_router
    from app.routers.ask import _select_consistent

    _, index = cube_router.build_catalog(schema)
    a = json.dumps({"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["kumas_cinsi"]})
    b = json.dumps({"cube": "parti", "measures": ["toplam_agirlik_kg"], "dimensions": ["kumas_cinsi"]})
    cq, agree, axis, opts = _select_consistent(_FakeLLM([a, b]), "q", "cat", index, 2)
    assert cq is None and axis == "measures" and len(opts) == 2


def test_self_consistency_cogunluk_kazanir(schema):
    import json

    from app import cube_router
    from app.routers.ask import _select_consistent

    _, index = cube_router.build_catalog(schema)
    a = json.dumps({"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]})
    b = json.dumps({"cube": "oee", "measures": ["ort_kalite"], "dimensions": ["makine"]})
    cq, agree, axis, _ = _select_consistent(_FakeLLM([a, a, b]), "q", "cat", index, 3)
    assert cq is not None and cq["measures"] == ["ort_oee"]
    assert abs(agree - 2 / 3) < 1e-9


# --- VQR: Verified Query Repository (A#4 / literatür #2) -----------------------

def test_vqr_store_recall_near_exact():
    from sqlmodel import SQLModel

    from app.vqr import VQR
    from control_plane.db import engine
    from control_plane.models import VerifiedQuery  # noqa: F401 — metadata kaydı için

    SQLModel.metadata.create_all(engine)  # sqlite test DB: verified_query tablosu (idempotent)
    v = VQR("test-vqr-unit")  # izole şirket kapsamı — diğer testlerin çiftleriyle karışmaz
    assert v.store("Hangi renkte en çok fire var?", 
                   {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["renk"],
                    "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]})
    # dönem filtresi SAKLANMAZ (şekil öğrenilir)
    assert "filters" not in v._load()[0]["cube_query"]
    # çekim/diakritik farkına dayanıklı birebir eşleşme (F5 fallback)
    hit = v.near_exact("hangi renklerde en cok fire vardi")
    assert hit is not None and hit["cube_query"]["dimensions"] == ["renk"]
    # alakasız soru eşleşmez
    assert v.near_exact("aylık üretim trendi") is None
    # chip etiketi soru olarak saklanmaz
    assert not v.store("chip: dönem → Bu ay", {"cube": "oee", "measures": ["ort_oee"]})
    # few-shot bloğu üretilir
    assert "CubeQuery" in v.few_shot_block("renk fire")


def test_vqr_verify_ve_birebir_oynatma(client):
    """/verify ile yazılan çift, aynı soru geldiğinde LLM'siz oynatılır (dönem sorusuyla)."""
    cq = {"cube": "parti", "measures": ["ort_renk_sapmasi"], "dimensions": ["renk"]}
    r = client.post("/verify", json={"cube_query": cq, "label": "renklerin ortalama sapması nedir"})
    assert r.status_code == 200 and r.json()["stored"]
    d = ask(client, "renklerin ortalama sapması nedir")
    assert any("verified repository" in t for t in d["trace"])
    # dönem depoda yok → politika gereği sorulur; şekil doğru taşınır
    assert "dönem" in (d["note"] or "").lower()
    assert d["cube_query"]["measures"] == ["ort_renk_sapmasi"]
    d2 = ask(client, "tüm zamanlar", cube_query=d["cube_query"], history=["renklerin ortalama sapması nedir"])
    assert d2["source"] == "cube" and d2["result"]["row_count"] >= 1
    # chip tamamlanınca öğrenme izi düşer (çift zaten vardı → güncellendi)
    assert any("VQR" in t for t in d2["trace"])


def test_vqr_yakin_eslesme_olcu_uyusmazliginda_atlanir(client):
    """Log regresyonu: "müşteri bazında kar oranı" depodaki "müşterilere göre kâr
    dağılımı"na yakın çıkıp KAR (mutlak) şeklini oynattı — soru açıkça BAŞKA ölçü
    (kar_marji_yuzde) adlandırıyorsa replay iptal edilir, deterministik route sürer."""
    cq = {"cube": "parti", "measures": ["kar"], "dimensions": ["musteri"]}
    r = client.post("/verify", json={"cube_query": cq, "label": "müşterilere göre kâr dağılımı"})
    assert r.status_code == 200 and r.json()["stored"]
    d = ask(client, "müşteri bazında kar oranı bu yıl")
    assert d["source"] == "cube"
    assert d["cube_query"]["measures"] == ["kar_marji_yuzde"], d["trace"]


def test_vqr_baglam_parcasi_ogrenilmez(client):
    """Log regresyonu: "aylara göre" gibi konusuz takip parçaları chip-onayıyla VQR'a
    yazılıyordu — şekil önceki rapordan gelir, soru tek başına taşımaz → bağlamsız
    yanlış replay. Cube/ölçü sinonimi geçmeyen soru öğrenilmez."""
    prev = {"cube": "parti", "measures": ["fire_orani_yuzde"], "dimensions": ["kumas_cinsi"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    # konusuz parça → dönem chip'i tamamlasa da depoya yazılmaz
    d = ask(client, "bu yıl", cube_query=prev, history=["aylara göre"])
    assert d["source"] == "cube"
    assert not any("chip-onaylı" in t for t in d["trace"])
    # konu taşıyan soru (ölçü sinonimi "fire oranı") → öğrenilir
    d2 = ask(client, "bu yıl", cube_query=prev, history=["kumaş türlerine göre fire oranı"])
    assert any("chip-onaylı" in t for t in d2["trace"])


def test_mid_conversation_literal_tekrar_vqr_uzerinden_doner(client):
    """Madde 9 (1 Ağustos 2026): `is_followup` (cube_query/prev_sql VARLIĞI) ÖNCEDEN VQR
    kontrolünü HER ZAMAN atlıyordu — sohbet içinde kullanıcı BİREBİR (normalize) aynı soruyu
    tekrar sorarsa (frontend context'i KORUDUĞU için cube_query/history dolu gelir) bu bir
    takip DEĞİL, "aynısını tekrar ver" isteğidir → VQR'dan (LLM'siz) dönmeli."""
    cq = {"cube": "parti", "measures": ["fire_orani_yuzde"], "dimensions": ["kumas_cinsi"],
          "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    q = "kumaş türlerine göre aylık fire oranı"
    r = client.post("/verify", json={"cube_query": cq, "label": q})
    assert r.status_code == 200 and r.json()["stored"]
    # is_followup=True (cube_query + history dolu) AMA metin history[-1] ile BİREBİR aynı
    d = ask(client, q, cube_query=cq, history=[q])
    assert d["source"] == "vqr", d.get("trace")
    assert any("VQR" in t for t in d["trace"])


def test_gercek_takip_sorusu_vqr_atlamiyor(client):
    """Negatif regresyon: is_literal_repeat YALNIZ metin history[-1] ile BİREBİR aynıyken
    devreye girer. Takip metni ("bu yıl") için DECOY bir VQR kaydı olsa bile — metin farklı
    olduğundan (is_literal_repeat False) VQR'a hiç bakılmaz; gerçek follow-up/period-
    tamamlama mantığı (test_vqr_baglam_parcasi_ogrenilmez ile AYNI senaryo) bozulmaz."""
    decoy_cq = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"],
                "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    r = client.post("/verify", json={"cube_query": decoy_cq, "label": "bu yıl"})
    assert r.status_code == 200 and r.json()["stored"]
    prev = {"cube": "parti", "measures": ["fire_orani_yuzde"], "dimensions": ["kumas_cinsi"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    d = ask(client, "bu yıl", cube_query=prev, history=["kumaş türlerine göre fire oranı"])
    assert d["source"] == "cube"
    assert d["cube_query"]["cube"] == "parti"  # decoy'un "oee"sine KAÇMADI
    # follow-up REFINE ile çözüldü (VQR-REPLAY DEĞİL) — sonucun kendisi VQR'a chip-onayıyla
    # YAZILMASI (mevcut, ayrı bir mekanizma, test_vqr_baglam_parcasi_ogrenilmez'de görülen
    # "chip-onaylı" öğrenme izi) beklenir ve zararsızdır; asıl kontrol edilen "birebir eşleşme
    # → doğrulanmış SQL/CubeQuery tekrar oynatıldı" REPLAY izinin HİÇ oluşmamasıdır.
    assert any("refine" in t for t in d["trace"])
    assert not any("birebir eşleşme" in t for t in d["trace"])


def test_kismi_anlama_serbest_sqle_dusmez(client):
    """Log regresyonu (2026-07-20): "kar oranı [tanınmayan kavram]" serbest-SQL'e düşüp
    istenmemiş çok-metrikli rapor uyduruyordu — artık tanınmayan kelime açıkça söylenir,
    tanınan yorum chip olur."""
    d = ask(client, "kar oranı fizibilite")
    assert d["source"] is None and not d["sql"]
    assert "fizibilite" in d["note"]
    labels = [s["label"] for s in d["suggestions"]]
    assert any("kar" in lb for lb in labels)
    assert any("düşülmedi" in t for t in d["trace"])


def test_cok_degerli_filtre(client):
    """Log (2026-07-21): "sadece beyaz ve siyah renk ver" — LLM refine geçersiz edit
    üretiyordu; çok-değerli eşleşme artık deterministik `in` filtresi olur."""
    prev = {"cube": "parti", "measures": ["toplam_agirlik_kg"],
            "dimensions": ["kumas_cinsi", "renk"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    d = ask(client, "sadece beyaz ve siyah renk ver", cube_query=prev)
    assert d["source"] == "cube", d.get("note")
    flt = next(f for f in d["cube_query"]["filters"] if f["dimension"] == "renk")
    assert flt["operator"] == "in" and sorted(flt["value"]) == ["Beyaz", "Siyah"]
    assert "renk" in d["cube_query"]["dimensions"]  # kırılım korunur (karşılaştırma)
    # taze soruda da: karşılaştırma niyeti → in-filtre + boyut kırılımı
    d2 = ask(client, "beyaz ve siyah renkler için toplam fire bu yıl")
    assert d2["source"] == "cube", d2.get("note")
    flt2 = next(f for f in d2["cube_query"]["filters"] if f["dimension"] == "renk")
    assert flt2["operator"] == "in"
    assert "renk" in (d2["cube_query"].get("dimensions") or [])


def test_taze_soruda_gorunum_ipucu(client):
    """Log (2026-07-21, yeni chat): görünüm niyeti yalnız konuşma-içi hesaplanıyordu —
    TAZE "ağırlık ... her kumaş türü için ayrı ayrı grafik, aylık renklere göre"
    cevabı view_hint'siz döndü, UI tabloya düştü. Taze yol da facet:<dim> üretir."""
    d = ask(client, "ağırlık her kumaş türü için ayrı ayrı grafik ver, aylık olarak renklerine göre bu yıl")
    assert d["source"] == "cube", d.get("note")
    assert d["view_hint"] == "facet:kumas_cinsi"
    assert d["cube_query"]["timeDimensions"][0]["granularity"] == "month"


def test_grafik_tipi_ipucu_pasta(client):
    """Faz 4.4 (31 Temmuz 2026): `_viz_hint()`/`_VIZ_MAP` (app/routers/ask.py) TANIMLIYDI ama
    hiçbir yerden ÇAĞRILMIYORDU (ölü kod) — açık grafik-TİPİ isteği ("pasta grafik olarak
    göster") artık view_hint'e yansır. Facet YOKKEN devreye girer (facet her zaman öncelikli,
    bkz. test_taze_soruda_gorunum_ipucu/test_her_x_icin_ayri_grafik — bu ikisi ETKİLENMEZ)."""
    d = ask(client, "bu yıl makine bazında ortalama oee, pasta grafik olarak göster")
    assert d["source"] == "cube", d.get("note")
    assert d["view_hint"] == "pie"


def test_grafik_tipi_ipucu_jenerik(client):
    """Madde 8 (1 Ağustos 2026): SPESİFİK grafik-tipi isteği ("pasta grafik") view_hint
    üretiyordu ama JENERİK istek ("grafik yap"/"görsel göster") de _VIZ_MAP'te "chart"
    literaline eşleniyor — backend bunu doğru üretiyor (bu test onu kilitler); asıl bug
    frontend'de (ResultView.tsx defaultView() "chart" hint'ini tanımıyordu, ayrı düzeltme)."""
    d = ask(client, "bu yıl makine bazında ortalama oee, grafik yap")
    assert d["source"] == "cube", d.get("note")
    assert d["view_hint"] == "chart"


def test_grafik_tipi_ipucu_tablo(client):
    d = ask(client, "bu yıl makine bazında ortalama oee tablo olarak göster")
    assert d["source"] == "cube", d.get("note")
    assert d["view_hint"] == "table"


def test_her_x_icin_ayri_grafik(client):
    """Log (2026-07-21): "her kumaş türü için ayrı ayrı grafik ver, aylık olarak" —
    sohbet dolgusu kapsamı düşürüp salt-görünüme yutuluyordu. Artık VERİ düzenlemesi
    (ay kovası) + PANELLİ görünüm (facet:kumas_cinsi) birlikte döner."""
    prev = {"cube": "parti", "measures": ["toplam_ciro"],
            "dimensions": ["kumas_cinsi", "renk"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    # NOT (2026-07-29): dolgudan "senden" çıkarıldı — bu Türkçe ablatif zamir
    # deterministic_refine'da (cube_router, bu iş kapsamı DIŞI) coverage-harici bir yolla
    # bail'e yol açıyor (eski cube'larla da tekrarlanır → cube restructure regresyonu DEĞİL).
    # Testin niyeti (sohbet dolgusu + veri düzenleme + panelli görünüm birlikte) korunur.
    # TODO: deterministic_refine "senden" edge-case'i ayrı ele alınacak.
    d = ask(client, "şimdi şunu isteyeceğim, her kumaş türü için ayrı ayrı grafik ver, aylık olarak renklerine göre",
            cube_query=prev)
    assert d["source"] == "cube", d.get("note")
    assert d["view_hint"] == "facet:kumas_cinsi"
    assert d["cube_query"]["timeDimensions"][0]["granularity"] == "month"


def test_coklu_olcu_cikarma(client):
    """Log (2026-07-21): "fire oranı GÖSTERME, fire miktarı ve üretim miktarı tek grafik" —
    salt-görünüm sanılıp ölçü düzenlemesi yutuluyordu. Olumsuz fiil + ölçü → düşürülür;
    kalan ölçüler ve kırılım korunur."""
    prev = {"cube": "parti",
            "measures": ["fire_orani_yuzde", "toplam_fire_kg", "toplam_agirlik_kg"],
            "dimensions": ["asama"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    d = ask(client, "fire oranı gösterme, fire miktarı ve üretim miktarı tek grafik göster",
            cube_query=prev)
    assert d["source"] == "cube", d.get("note")
    assert d["cube_query"]["measures"] == ["toplam_fire_kg", "toplam_agirlik_kg"]
    assert d["cube_query"]["dimensions"] == ["asama"]


def test_hafta_gunu_parti_cubeunda(client):
    """Log (2026-07-21): "haftanın günlerine göre" fire raporunda 'oee'ye git' deniyordu —
    hafta_gunu artık parti/surd cube'larında da türev boyut; satış/fire gün desenleri çıkar."""
    prev = {"cube": "parti", "measures": ["fire_orani_yuzde"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    d = ask(client, "haftanın günlerine göre", cube_query=prev)
    assert d["source"] == "cube", d.get("note")
    assert d["cube_query"]["dimensions"] == ["hafta_gunu"]
    assert d["result"]["row_count"] == 6  # üretim Pzt–Cmt (6 gün)
    d2 = ask(client, "haftanın günlerine göre satış bu yıl")
    assert d2["source"] == "cube"
    assert d2["cube_query"]["measures"] == ["toplam_ciro"]
    assert d2["cube_query"]["dimensions"] == ["hafta_gunu"]


def test_verify_undo_ve_yanlis(client):
    """Geri bildirim döngüsü: doğrula → geri al → yanlış işaretle (yakın çift silinir)."""
    cq = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["renk"]}
    r = client.post("/verify", json={"cube_query": cq, "label": "renk bazında ciro dökümü x"})
    assert r.json()["stored"]
    # geri al
    r2 = client.post("/verify", json={"cube_query": cq, "label": "renk bazında ciro dökümü x",
                                      "undo": True})
    assert r2.json()["removed"] and not r2.json()["stored"]
    # tekrar yaz + "yanlış" verdikti → silinir
    client.post("/verify", json={"cube_query": cq, "label": "renk bazında ciro dökümü x"})
    r3 = client.post("/verify", json={"cube_query": cq, "label": "renk bazında ciro dökümü x",
                                      "verdict": "wrong"})
    assert r3.json()["removed"]


# --- Zamanlanmış raporlar + eşik alarmı (ADR-0011) ---------------------------

def test_schedule_olustur_kos_bildirim(client):
    """Zamanlama yaşam döngüsü: oluştur → manuel koş → bildirim + sözleşme → sil.
    Eşik kesin ihlalli (fire oranı > 0) → alarm bildirimi."""
    body = {"label": "Test fire alarmı",
            "cube_query": {"cube": "parti", "measures": ["fire_orani_yuzde"],
                           "dimensions": ["asama"]},
            "period": "bu yıl", "every": "day", "at": "08:00",
            "threshold": {"measure": "fire_orani_yuzde", "op": "gt", "value": 0}}
    r = client.post("/schedules", json=body)
    assert r.status_code == 200, r.text
    sid = r.json()["schedule"]["id"]
    assert any(s["id"] == sid for s in client.get("/schedules").json()["schedules"])

    note = client.post(f"/schedules/{sid}/run").json()["notification"]
    assert note["kind"] == "alert" and "eşik ihlali" in note["message"]
    assert note["contract_id"]  # her koşum sözleşme alır (ADR-0010)
    # dönem GÖRELİ çözüldü: cq'da bu yılın gte filtresi var
    assert any(f["dimension"] == "tarih" for f in note["cube_query"]["filters"])
    # bildirim listede
    assert any(n["id"] == note["id"] for n in client.get("/notifications").json()["notifications"])
    # eşik ihlalsiz → normal rapor bildirimi
    client.delete(f"/schedules/{sid}")
    r2 = client.post("/schedules", json={**body, "label": "N", "threshold": {"measure": "fire_orani_yuzde", "op": "gt", "value": 99}})
    sid2 = r2.json()["schedule"]["id"]
    note2 = client.post(f"/schedules/{sid2}/run").json()["notification"]
    assert note2["kind"] == "report"
    client.delete(f"/schedules/{sid2}")


def test_schedule_gecersiz_reddedilir(client):
    r = client.post("/schedules", json={"label": "x", "cube_query": {"cube": "parti", "measures": ["uydurma"]}})
    assert r.status_code == 400
    # eşik ölçüsü raporda olmalı
    r2 = client.post("/schedules", json={"label": "x",
        "cube_query": {"cube": "parti", "measures": ["toplam_ciro"]},
        "threshold": {"measure": "fire_orani_yuzde", "op": "gt", "value": 1}})
    assert r2.status_code == 400


def test_schedule_vade_hesabi():
    from datetime import datetime, timedelta, timezone

    from app.schedules import is_due

    now = datetime(2026, 7, 22, 9, 0, tzinfo=timezone.utc).astimezone()
    day = {"every": "day", "at": "08:00"}
    assert is_due(day, None, now)                                  # hiç koşmadı, slot geçti
    assert not is_due(day, now - timedelta(minutes=10), now)       # bugünkü slottan sonra koştu
    assert is_due(day, now - timedelta(days=1), now)               # dünkü koşum → vade geldi
    hour = {"every": "hour"}
    assert is_due(hour, now - timedelta(minutes=61), now)
    assert not is_due(hour, now - timedelta(minutes=10), now)


# --- Query Contract + Replay (ADR-0010) --------------------------------------

def test_query_contract_ve_replay(client):
    """Her başarılı rapor sözleşme alır; replay üç seviyeli teşhis üretir."""
    import json as _json

    d = ask(client, "makine bazında ortalama oee bu yıl")
    cid = d["contract_id"]
    assert cid and cid.startswith("c-")

    # 1) AYNI: veri/şema değişmedi → birebir doğrulama
    r = client.get(f"/contracts/{cid}/replay").json()
    assert r["replay"]["result_match"] and "AYNI" in r["replay"]["verdict"]
    assert r["replay"]["sql_match"] and not r["replay"]["schema_changed"]

    # sahte sözleşmelerle diğer iki seviye: TEK-KAYNAK DB'ye (contract_log) elle kayıt yaz
    orig = client.get(f"/contracts/{cid}").json()
    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import ContractLog
    _cqj = (_json.dumps(orig.get("cube_query"), ensure_ascii=False)
            if orig.get("cube_query") else None)
    with Session(engine) as _s:
        for _fid, _sql in (("c-fakeveri01", orig.get("sql")), ("c-faketanim1", "SELECT 1 AS x")):
            _s.add(ContractLog(
                id=_fid, session_id=orig.get("session"), tenant_id=orig.get("tenant_id"),
                question=orig.get("question"), cube_query_json=_cqj, sql=_sql,
                result_hash="sha256:degismis", row_count=orig.get("row_count"),
                schema_version=orig.get("schema_version"), source=orig.get("source")))
        _s.commit()

    # 2) VERİ DEĞİŞTİ: aynı SQL, farklı hash
    r2 = client.get("/contracts/c-fakeveri01/replay").json()
    assert "VERİ DEĞİŞTİ" in r2["replay"]["verdict"] and r2["replay"]["sql_match"]
    # 3) TANIM DEĞİŞTİ: CubeQuery bugün farklı SQL üretiyor
    r3 = client.get("/contracts/c-faketanim1/replay").json()
    assert "TANIM DEĞİŞTİ" in r3["replay"]["verdict"]
    # liste + 404
    assert any(c["id"] == cid for c in client.get("/contracts").json()["contracts"])
    assert client.get("/contracts/c-yok/replay").status_code == 404


def test_chip_duzenlemesi_de_sozlesme_alir(client):
    d1 = ask(client, "aşama bazında toplam fire bu yıl")
    r = client.post("/cube", json={"cube_query": d1["cube_query"],
                                   "label": "chip: test", "session_id": "eval"})
    assert r.json()["contract_id"]


def test_features_endpoint(client):
    """ADR-0009: bayraklar global ⊕ sektör ⊕ şirket katmanından çözülür; verify_button
    global platform bayrağı (demo'da beta)."""
    r = client.get("/features")
    assert r.status_code == 200
    assert r.json()["features"]["verify_button"] == "beta"


def test_capraz_cube_gecis_notu(client):
    """Çapraz-cube geçiş sessiz olmasın: OEE raporundayken kumaş sorusu parti cube'una
    geçer ve cevapla birlikte 'Konu değişti' notu döner."""
    prev = {"cube": "oee", "measures": ["toplam_uretim_kg"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    d = ask(client, "kumaş cinsine göre fire oranı bu yıl", cube_query=prev)
    assert d["source"] == "cube"
    assert d["cube_query"]["cube"] == "parti"
    assert d["note"] and "Konu değişti" in d["note"]
    assert "OEE" in d["note"] and "parti" in d["note"]


def test_rule_fallback_kapali_durust_ret(monkeypatch):
    """A#5: rule_fallback=False + LLM yok → kural-tabanlı TAHMİN yerine dürüst ret.
    (Kural yedeği yalnız demo şemasını bilir; gerçek şemada sessiz-yanlış üretirdi.)"""
    from app.config import get_settings

    monkeypatch.setenv("DIMA_RULE_FALLBACK", "false")
    monkeypatch.setenv("DIMA_LLM_PROVIDER", "auto")
    # anahtarları BOŞLA (env, .env dosyasını ezer) → hiç sağlayıcı yok
    for k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "XAI_API_KEY"):
        monkeypatch.setenv(f"DIMA_{k}", "")
    monkeypatch.setenv("DIMA_OLLAMA_BASE_URL", "http://127.0.0.1:9")  # kapalı port
    get_settings.cache_clear()
    try:
        from fastapi.testclient import TestClient

        from app.main import create_app
        from tests.conftest import TEST_USER, _ensure_test_users

        with TestClient(create_app()) as c:
            _ensure_test_users()
            tok = c.post("/auth/login", json=TEST_USER).json()["access_token"]
            c.headers["Authorization"] = f"Bearer {tok}"
            # cube'a düşmeyen bir soru (liste niyeti) → serbest-SQL yolu → dürüst ret
            r = c.post("/ask", json={"question": "reddedilen partileri listele",
                                     "execute": True, "session_id": "a5"})
            d = r.json()
            assert d["source"] is None and not d["sql"]
            assert d["note"]
    finally:
        get_settings.cache_clear()  # oturum client'ı eski ayarlarına dönsün


# --- Değer indeksi (lit #4): typo toleransı ---------------------------------

def test_typo_otomatik_duzeltme_deger(client):
    """"Siyh" → tek ve açık aday "Siyah" (renk) → görünür otomatik düzeltme, deterministik
    cevap (filtre uygulanır)."""
    d = ask(client, "Siyh için ciro bu yıl")
    assert d["source"] == "cube", d.get("note")
    assert any("yazım düzeltme" in t for t in d["trace"])
    assert {"dimension": "renk", "operator": "eq", "value": "Siyah"} in d["cube_query"]["filters"]


def test_typo_otomatik_duzeltme_sozluk(client):
    """"vardya" → "vardiya" (sözlük typo'su) → kırılım deterministik kurulur."""
    d = ask(client, "vardya bazında ortalama oee bu yıl")
    assert d["source"] == "cube", d.get("note")
    assert d["cube_query"]["dimensions"] == ["vardiya"]


def test_typo_orta_benzerlik_chip(client):
    """"müterileri" (çekim + typo) orta benzerlik → tahmin YOK, "şunu mu demek istedin?"
    chip'i; chip sorgusu düzeltilmiş sorudur → tıklayınca cevap gelir."""
    d = ask(client, "en çok satış yapan müterileri getir bu yıl")
    assert d["source"] is None and "demek istedin" in d["note"]
    sugg = d["suggestions"]
    assert any("musteri" in s["label"] for s in sugg)
    d2 = ask(client, next(s["query"] for s in sugg if "musteri" in s["label"]))
    assert d2["source"] == "cube"
    assert d2["cube_query"]["dimensions"] == ["musteri"]


# --- GL yapısal rapor (Faz 2a): gelir tablosu / bilanço --------------------------

def test_gelir_tablosu_dogru_cubea_gider(client):
    """"gelir tablosu" içindeki "gelir" kelimesi parti/ticaret cube'larının da ölçü
    sinonimidir — route()'a düşerse YANLIŞ cube'a (parti/toplam_ciro) yönlenip dönem
    sorardı (gerçek eval bulgusu). GL algılaması route()'tan/VQR'dan ÖNCE çalışmalı."""
    d = ask(client, "gelir tablosu")
    assert d["source"] == "statement"
    assert d["cube_query"]["cube"] == "mizan"
    assert d["result"]["row_count"] > 0
    labels = [r["Kalem"] for r in d["result"]["rows"]]
    assert "DÖNEM KARI/ZARARI" in labels


def test_bilanco_deterministik_cevap(client):
    d = ask(client, "bilanço")
    assert d["source"] == "statement"
    assert d["cube_query"]["cube"] == "mizan"
    bolumler = {r["Bölüm"] for r in d["result"]["rows"]}
    assert bolumler == {"AKTİF", "PASİF"}


def test_alakasiz_kelime_oneriye_donusmez(client):
    """"fizibilite" hiçbir katalog karşılığına benzemiyor → öneri DEĞİL dürüst not
    (yanlış öneri, öneri yokluğundan kötüdür)."""
    d = ask(client, "kar oranı fizibilite")
    assert d["source"] is None
    assert "fizibilite" in d["note"] and "demek istedin" not in d["note"]


def test_capraz_konu_chip(client):
    """"kar oranı sürdürülebilirlik": iki cube kimliği, biri ölçüsüz → kompozit serbest-SQL
    UYDURULMAZ; konular chip'lenir. "verim ve fire oranı" (her ikisi ölçülü) ise bilinçli
    çok-metrik istek → LLM yolu açık kalır."""
    d = ask(client, "kar oranı sürdürülebilirlik")
    assert d["source"] is None and not d["sql"]
    labels = [s["label"] for s in d["suggestions"]]
    assert "kar oranı" in labels and "sürdürülebilirlik" in labels
    assert any("çapraz konu" in t for t in d["trace"])
    d2 = ask(client, "makine bazında verim ve fire oranı bu yıl")
    assert not any("çapraz konu" in t for t in d2["trace"])  # çok-metrik → chip DEĞİL


def test_yetenek_chipleri_insanca_etiket(client):
    """Chip etiketi eşleşme kökü ("makin") değil insan-okur label ("makine") olmalı."""
    prev = {"cube": "oee", "measures": ["toplam_uretim_kg"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    d = ask(client, "hangi kırılımlara göre bunu detaylandırabilirim?", cube_query=prev)
    labels = [s["label"] for s in d["suggestions"]]
    assert "makine" in labels and "makin" not in labels
    assert "haftanın günü" in labels


def test_surdurulebilirlik_cube(client, schema):
    """Sürdürülebilirlik artık MEŞRU cube: "sürdürülebilirlik" → ölçü chip'leri;
    "makine bazında su yoğunluğu bu yıl" → deterministik yoğunluk (SUM/SUM)."""
    d = ask(client, "sürdürülebilirlik")
    assert d["source"] is None and d["suggestions"]  # ölçü sorulur (default yok)
    from app import cube_router
    plan = cube_router.route("makine bazında su yoğunluğu bu yıl", schema)
    assert plan is not None
    cq = plan["cube_query"]
    assert cq["cube"] == "surdurulebilirlik"
    assert cq["measures"] == ["su_yogunlugu_lt_kg"]
    assert cq["dimensions"] == ["makine"]
    d2 = ask(client, "makine bazında su yoğunluğu bu yıl")
    assert d2["source"] == "cube"
    assert d2["result"]["row_count"] == 11  # 11 makine
    # yoğunluk L/kg mertebesinde (toplam litre DEĞİL — SUM/SUM doğrulaması)
    v = d2["result"]["rows"][0]["su_yogunlugu_lt_kg"]
    assert 5 < v < 100


def test_gecen_ay_chip_gibi_calisir(client):
    """Log akışı: rapor açıkken "geçen ay" — netleştirme DEĞİL, önceki takvim ayına geçiş."""
    prev = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["musteri"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-07-01"}]}
    d = ask(client, "geçen ay", cube_query=prev)
    assert d["source"] == "cube", d.get("note")
    tarih = [f for f in d["cube_query"]["filters"] if f["dimension"] == "tarih"]
    assert {f["operator"] for f in tarih} == {"gte", "lte"}  # tam takvim aralığı


def test_eski_cube_adi_gocu_ve_olcu_duzeltme(client):
    """Log akışı (2026-07-20): istemcide eski "fire" adıyla kalan rapor + "fire oranı
    değil kar oranı" — bağlam KOPMAZ, kırılım/kova/dönem korunarak ölçü takas edilir."""
    prev = {"cube": "fire", "measures": ["fire_orani_yuzde"], "dimensions": ["musteri"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    d = ask(client, "fire oranı değil kar oranı", cube_query=prev)
    assert "cube adı göçü → parti" in d["trace"]
    assert not any("kopma" in t for t in d["trace"])
    assert d["source"] == "cube"
    assert d["cube_query"]["measures"] == ["kar_marji_yuzde"]
    assert d["cube_query"]["dimensions"] == ["musteri"]  # kırılım korunur
    assert d["cube_query"]["timeDimensions"][0]["granularity"] == "month"


def test_varlik_top_n_calisir(client):
    """"en çok satış yapılan 3 müşterininkileri göster": satır limiti değil — ciroya
    göre ilk 3 müşteri seçilir (in-filtre), trend o 3 müşteri için tam kalır."""
    prev = {"cube": "parti", "measures": ["kar_marji_yuzde"], "dimensions": ["musteri"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    d = ask(client, "en çok satış yapılan 3 müşterininkileri göster", cube_query=prev)
    assert d["source"] == "cube"
    assert " IN (" in d["sql"]
    assert any("varlık top-3" in t for t in d["trace"])
    musteriler = {r["musteri"] for r in d["result"]["rows"]}
    assert len(musteriler) == 3  # 3 müşteri, HER AY satırıyla (seri kesilmez)
    assert d["result"]["row_count"] > 3


def test_yetenek_sorusu_kirilim_chipleri(client):
    """Log regresyonu: "hangi kırılımlara göre detaylandırabilirim?" düzenleme DEĞİL —
    LLM tüm boyutları ekleyip 861 satır üretiyordu; artık kırılım chip'leri sunulur."""
    prev = {"cube": "oee", "measures": ["toplam_uretim_kg"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    d = ask(client, "hangi kırılımlara göre bunu detaylandırabilirim?", cube_query=prev)
    assert d["source"] is None and d["note"]
    labels = [s["label"] for s in d["suggestions"]]
    assert "makin" in " ".join(labels) and "vardiya" in labels
    # chip metni deterministik refine ile işlenir → kırılım eklenir
    d2 = ask(client, "vardiya kırılımı ekle", cube_query=prev)
    assert d2["source"] == "cube"
    assert "vardiya" in d2["cube_query"]["dimensions"]


def test_clarify_top5_order_limit_tasinir(client):
    """Gitaş logu 2026-07-24: "en çok satış yapılan 5 cari" → dönem chip'i araya
    girince order/limit kayboluyordu (763 satır). Artık cq'ya gömülü taşınır."""
    d1 = ask(client, "en çok ciro yapılan 5 müşteri")
    assert "dönem" in (d1["note"] or "").lower()
    assert d1["cube_query"].get("limit") == 5  # gömülü taşındı
    assert d1["cube_query"].get("order", {}).get("direction") == "desc"
    d2 = ask(client, "tüm zamanlar", cube_query=d1["cube_query"])
    assert d2["source"] == "cube"
    assert d2["result"]["row_count"] <= 5
    assert "ORDER BY" in d2["sql"].upper() and "LIMIT 5" in d2["sql"].upper()


def test_bayat_cube_query_500_yerine_durust_not(client):
    """Gitaş 500'ü (2026-07-24): istemcide eski oturumdan kalan cube_query, yeni
    şirketin veri düzleminde planlanamaz — endpoint çökmek yerine dürüst not döner."""
    d = ask(client, "tüm zamanlar",
            cube_query={"cube": "parti", "measures": ["boyle_bir_olcu_yok"]})
    assert d["source"] is None and not d["sql"]
    assert "çalıştırılamadı" in (d["note"] or "")


def test_capraz_cube_gecisi_donem_tasinir(client):
    """Gitaş logu 2026-07-24: refine mevcut cube'da karşılık bulamayınca kullanıcı
    'cube:mal' yazmak zorunda kalıyordu. Artık soru tüm kataloğa yeniden yönlendirilir,
    dönem filtresi taşınarak otomatik cube geçişi yapılır."""
    d1 = ask(client, "bu yılki toplam ciro")
    assert d1["source"] == "cube" and d1["cube_query"]["cube"] == "parti"
    tarih_f = [f for f in d1["cube_query"]["filters"] if f["dimension"] == "tarih"]
    assert tarih_f  # dönem raporda
    # parti raporundayken başka cube'un ölçüsü: sistem yeni cube'a GEÇER (kullanıcı
    # 'cube:mal' yazmak zorunda kalmaz). NOT: topic-switch yolunda dönem TAŞIMA henüz
    # yok (ADR-0018 backlog: konuşma çekirdeği birleştirmesi) — burada yalnız geçiş
    # doğrulanır; unavailable/no-op yollarındaki _try_cross_cube dönemi taşır.
    d2 = ask(client, "makine bazında ortalama oee", cube_query=d1["cube_query"])
    assert d2["source"] in ("cube", "cube+llm")
    assert d2["cube_query"]["cube"] == "oee"


def test_konu_degisimi_donem_tasir(client):
    """Canlı gitas log 2026-07-24: "bu yıl ciro" bağlamında "ortalama oee" konu değişimi
    → önceki dönem TAŞINIR (sessiz tüm-zaman SUM değil, panel K2)."""
    d1 = ask(client, "bu yılki toplam ciro")
    assert d1["cube_query"]["cube"] == "parti"
    per = [f for f in d1["cube_query"]["filters"] if f["dimension"] == "tarih"][0]["value"]
    d2 = ask(client, "ortalama oee", cube_query=d1["cube_query"])
    assert d2["source"] == "cube" and d2["cube_query"]["cube"] == "oee"
    tarih = [f for f in d2["cube_query"].get("filters", []) if f["dimension"] == "tarih"]
    assert tarih and tarih[0]["value"] == per  # dönem taşındı, dönem chip'i sorulmadı
