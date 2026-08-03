"""FAZ 9.2 + 9.3 — ÇÖZÜLMEYEN CHIP ÜRETİLMEZ, ve doğrulama SONDASI iz bırakmaz.

## Ölçülen kusur (denetim + canlı tur)

**9.2 — denetimin öncülü ÖLÇÜLDÜ ve ÇÜRÜDÜ; kapı yine de kaldı.** Rapor, kardeş
netleştirme dallarının (`cube_only_match` · `partial_unknowns` · daraltma · katalog
örnekleri · beraberlik) `Suggestion(label=lb, query=lb)` ile **kırık** chip ürettiğini
söylüyordu. Ölçüm bunu çürüttü — katalogdan türeyen **85 etiketin hepsi** bir yere varıyor:

    tıklanınca doğrudan CEVAP : 2
    DARALTAN chip üretti      : 83
    ÇIKMAZ SOKAK              : 0

`route()`=`None` bir chip'i kırık YAPMIYOR: *"sürdürülebilirlik"* R4 verir ama `/ask`
*"hangi ölçüyü istiyorsun?"* + 6 çalışan chip döndürür — **duvar değil huni**. İlk
düzeltmem `route()`'u tek ölçüt aldığı için çalışan üç yolu kesti ve **üç golden test**
bunu yakaladı. Ölçüt düzeltildi (`chip_kullanisli_mi`, dört kollu).

2a-2'deki **39 gerçek kırık chip** ise katalog etiketi değil **sentezlenmiş** dizelerdi
(*"mizan (hesap bakiyeleri) borç"*). Kural bu ayrımda: katalogun TANIDIĞI terim geçerli
bir huni girişidir; SENTEZLENMİŞ sorgu doğrulanmak zorundadır.

**9.3 — ölçüm ≠ garanti.** `_calisan_sorgu`'nun son çaresi hiçbir aday çözülmezse **ham
etiketi** yine chip yapıyordu. Gerekçesi *"chip yine bir İPUCU taşır"*dı; ama tıklanınca
çalışmayan bir chip, kullanıcıyı aynı duvara **ikinci kez** çarptırır — kendi
docstring'inin dört satır yukarıda yazdığı kuralın ihlali. *"39 → 0"* bir **ölçümdü**.

**9.2'nin kendisi 9.2'yi kırdı — ve bu testin asıl varlık sebebi bu.** İlk düzeltme
`route()`'u `ask.py`'den **doğrudan** çağırdı. `route()` girişte `reddi_sifirla()` yapar;
`answer.py:198` red gerekçesini **seal anında**, yani chip'ler kurulduktan SONRA okur.
Ölçüldü:

    kullanıcının red gerekçesi ÖNCE : R4
    chip sondalarından SONRA        : R1   ← telemetriye BU yazılacaktı

Yani düzeltme, bu oturumda **bir kez kapatılmış** kusuru başka bir kapıdan yeniden açtı.
Çözüm yama değil **kapı**: `cube_router.chip_cozuluyor_mu` sarmalı kendi içinde taşır.
"""

from __future__ import annotations

import inspect

from app import cube_router as cr
from app.routers import ask as ask_mod

#: Katalogda hiçbir karşılığı olmayan, `route()`'un ASLA çözemeyeceği etiket.
COZULMEZ = "zzz olmayan bir olcu qwerty"

#: `route()` doğrulamasından MUAF chip ifadeleri ve **gerekçeleri**. Gerekçesiz muafiyet
#: kapıyı kendiliğinden eritir — bu depoda `test_cevap_alani_yetim_degil`'in kalıbı.
MUAF: dict[str, str] = {
    "etiket": "`_dogrulanmis_chipler`'in KENDİ inşası — bu satıra gelmiş olması zaten "
              "`chip_cozuluyor_mu`'dan geçtiği anlamına gelir",
    "'neler sorabilirim'": "META chip: `route()`'a değil `_is_catalog_query` katalog "
                           "yoluna gider; `route()` ile ölçmek YANLIŞ mekanizmayı ölçerdi",
}


# --- 9.2: beş kardeş dalın hepsi doğrulamadan geçiyor -----------------------------

def test_HICBIR_DAL_cıplak_etiketi_chip_YAPMIYOR():
    """Kapının kendisi: `Suggestion(label=X, query=X)` — aynı ifadeyi hem etiket hem
    sorgu yapan **doğrulanmamış** chip — `ask.py`'de KALMAMALI.

    Beş dalı tek tek saymak yerine kalıbı yasaklıyoruz: altıncı dalı ekleyen kişi de aynı
    kapıya çarpsın. Sayarak kilitlemek, tam olarak bu kusurun doğuş biçimiydi.

    ⚠️ İlk sürüm bu kalıbı **metinde** aradı ve KENDİ DOCSTRING'İMDEKİ alıntıyı yakaladı —
    bu oturumda **dördüncü** kez bir testim metni davranış sandı. Artık `ast` ile gerçek
    ÇAĞRI düğümlerine bakılıyor; yorumlar ve docstring'ler kapının dışında."""
    import ast

    agac = ast.parse(inspect.getsource(ask_mod))
    ihlal = []
    for d in ast.walk(agac):
        if not (isinstance(d, ast.Call) and getattr(d.func, "id", None) == "Suggestion"):
            continue
        kw = {k.arg: k.value for k in d.keywords}
        if "label" not in kw or "query" not in kw:
            continue
        if ast.dump(kw["label"]) != ast.dump(kw["query"]):
            continue
        if ast.unparse(kw["label"]) in MUAF:
            continue
        ihlal.append((d.lineno, ast.unparse(kw["label"])))
    assert not ihlal, (
        f"DOĞRULANMAMIŞ CHIP: ham etiket sorgu olarak kullanılıyor → {ihlal}. "
        "`_dogrulanmis_chipler(...)` üzerinden geçir.")


def test_MUAF_LISTESI_bayatlamiyor():
    """Muafiyet listesi kendiliğinden erimemeli: artık var olmayan bir ifade için muafiyet
    taşımak, kapıyı okunamaz yapar ve bir gün gerçek bir ihlali örter."""
    import ast

    agac = ast.parse(inspect.getsource(ask_mod))
    gorulen = {ast.unparse(k.value)
               for d in ast.walk(agac)
               if isinstance(d, ast.Call) and getattr(d.func, "id", None) == "Suggestion"
               for k in d.keywords if k.arg == "label"}
    assert not (set(MUAF) - gorulen), \
        f"MUAF listesinde artık üretilmeyen chip(ler): {sorted(set(MUAF) - gorulen)}"


def test_YUKLEME_chipleri_VERI_SEMASIYLA_dogrulaniyor():
    """Yükleme chip'leri tenant kataloğunda DEĞİL, yüklenen dosyanın cube'unda çözülür
    (`_service_for` aynı `session_id`'de dataset servisini seçer). Tenant şemasıyla
    doğrulamak hepsini gerekçesiz düşürürdü — kapı, chip'in GERÇEKTEN gideceği şemaya
    karşı ölçmezse bir kapı değil bir gürültü kaynağıdır."""
    govde = inspect.getsource(ask_mod.upload_dataset)
    assert "_dogrulanmis_chipler(ham, veri_semasi" in govde, \
        "yükleme chip'leri doğrulanmıyor"
    assert "svc.schema()" in govde, \
        "yükleme chip'leri YANLIŞ şemaya karşı doğrulanıyor olabilir"


def test_BES_DALIN_hepsi_yardimciyi_cagiriyor():
    """Denetimde bulunan beş çağrı yeri: sayı DÜŞERSE bir dal kaçmış demektir."""
    kaynak = inspect.getsource(ask_mod)
    assert kaynak.count("_dogrulanmis_chipler(") >= 6, (
        "beş çağrı yeri + tanım beklenirken daha azı var — bir netleştirme dalı "
        "doğrulama kapısının DIŞINDA kalmış olabilir")


def test_KULLANISSIZ_etiket_DUSURULUYOR(schema):
    tutulan = ask_mod._dogrulanmis_chipler(["ciro", COZULMEZ], schema, en_fazla=8)
    assert COZULMEZ not in [s.label for s in tutulan], "hiçbir yere varmayan etiket chip oldu"


def test_HUNI_chipleri_KESILMIYOR(schema):
    """⚠️ İlk düzeltmemin gerilemesi — burada kilitleniyor. `route()` çözemese bile
    katalogun tanıdığı etiket bir DARALTMAYA götürür; kesmek çalışan bir yolu yok eder."""
    for huni in ("sürdürülebilirlik", "makine"):
        assert cr.route(huni, schema) is None, f"ön koşul: {huni!r} route ile çözülmemeli"
        tutulan = ask_mod._dogrulanmis_chipler([huni], schema, en_fazla=4)
        assert [s.label for s in tutulan] == [huni], (
            f"{huni!r} chip'i KESİLDİ — ama tıklanınca daraltıcı chip'ler döndürüyor "
            "(ölçüldü: 85 etiketin 0'ı çıkmaz sokak)")


def test_COZULEN_etiket_KORUNUYOR(schema):
    """Kapı fazla geniş olmamalı: çalışan chip'i kesmek kapsamı gerekçesiz daraltır."""
    tutulan = ask_mod._dogrulanmis_chipler(["ciro"], schema, en_fazla=8)
    assert [s.label for s in tutulan] == ["ciro"]
    assert tutulan[0].query == "ciro", "chip'in sorgusu etiketiyle aynı olmalı"


def test_EN_FAZLA_siniri_TUTULANA_uygulaniyor(schema):
    """Sınır düşenlere değil TUTULANLARA uygulanmalı — yoksa bir çözülmez etiket,
    çözülen bir chip'in yerini yer ve kullanıcı sebepsiz daha az seçenek görür."""
    tutulan = ask_mod._dogrulanmis_chipler([COZULMEZ, "ciro", "fire"], schema, en_fazla=2)
    assert len(tutulan) == 2, f"düşen etiket kotayı yedi: {[s.label for s in tutulan]}"


def test_DUSEN_chip_LOGLANIYOR():
    """Sessiz kırpma yok (§0.5 sınır kuralı)."""
    govde = inspect.getsource(ask_mod._dogrulanmis_chipler)
    assert "_log.info" in govde and "düşürüldü" in govde


# --- 9.2'nin kendi tuzağı: sonda telemetriyi EZMEZ --------------------------------

def test_CHIP_SONDASI_kullanicinin_RED_GEREKCESINI_ezmiyor(schema):
    """Bu oturumda **iki kez** ısıran kusur. `answer.py:198` red gerekçesini seal anında,
    yani chip'ler kurulduktan SONRA okur — sonda ezerse telemetri YANLIŞ kolona yazar."""
    cr.reddi_sifirla()
    cr.route("son 6 ay personel bazlı çalışma süreleri kıyasla", schema)
    once = cr.red_gerekcesi()
    assert once, "ön koşul: bu soru gerçekten reddedilmeli (test kendini doğruluyor)"

    ask_mod._dogrulanmis_chipler(["ciro", "fire", COZULMEZ, "makine"], schema, en_fazla=8)
    assert cr.red_gerekcesi() == once, (
        f"chip sondası red gerekçesini EZDİ: {once} → {cr.red_gerekcesi()}. "
        "Faz 0 telemetrisi ve Faz 2b'nin triyajı bu kolondan besleniyor.")


def test_SONDA_YALITIMI_yardimcinin_ICINDE(schema):
    """Yalıtım çağrı yerinde DEĞİL fonksiyonun içinde olmalı — altıncı dalı ekleyen
    kişinin sarmalı hatırlamasına bağlı bir koruma, koruma değildir."""
    assert "cube_router.route(" not in inspect.getsource(ask_mod._dogrulanmis_chipler), \
        "yardımcı route()'u DOĞRUDAN çağırıyor — sonda yalıtımı baypas ediliyor"
    cr.reddi_sifirla()
    cr.route("son 6 ay personel bazlı çalışma süreleri kıyasla", schema)
    once = cr.red_gerekcesi()
    cr.chip_kullanisli_mi(COZULMEZ, schema)
    cr.chip_cozuluyor_mu(COZULMEZ, schema)
    assert cr.red_gerekcesi() == once


def test_IKI_OLCUT_AYRI_seyleri_olcuyor(schema):
    """Yalıtım doğru ama cevap yanlış olsaydı kapı ters yönde zarar verirdi. İki ölçüt
    BİLEREK farklıdır: `chip_cozuluyor_mu` SENTEZLENMİŞ sorgu içindir (tam cevap şartı),
    `chip_kullanisli_mi` KATALOG etiketi içindir (huni yeter)."""
    assert cr.chip_kullanisli_mi("ciro", schema) is True
    assert cr.chip_kullanisli_mi(COZULMEZ, schema) is False
    assert cr.chip_kullanisli_mi("ciro", None) is True, \
        "şema yokken doğrulama İMKÂNSIZ — chip gerekçesiz kesilmemeli"

    # AYRIM: huni etiketi kullanışlıdır ama tam ÇÖZÜLMEZ. İkisi aynı olsaydı biri
    # gereksiz olurdu ve sentezlenmiş sorgular denetimsiz kalırdı.
    assert cr.chip_kullanisli_mi("sürdürülebilirlik", schema) is True
    assert cr.chip_cozuluyor_mu("sürdürülebilirlik", schema) is False


# --- 9.3: son çare artık None ------------------------------------------------------

def test_SON_CARE_ham_etiket_DONDURMUYOR():
    govde = inspect.getsource(cr._calisan_sorgu)
    son = govde.rstrip().splitlines()[-1].strip()
    assert son == "return None", (
        f"`_calisan_sorgu`'nun son çaresi hâlâ bir etiket döndürüyor: {son!r}")


def test_NETLESTIRME_cozulmeyen_chipi_ELIYOR(schema):
    """`olcu_netlestirme` `None` dönen adayı düşürmeli — yoksa `query=None` bir chip
    frontend'e gider ve tıklanınca boş sorgu gönderir."""
    sahte = [({"name": "yok_boyle_cube", "synonyms": ["qwertyuiop"]}, "zzz olcu"),
             ({"name": "yok_boyle_cube2", "synonyms": ["asdfghjkl"]}, "zzz olcu")]
    assert cr.olcu_netlestirme(sahte, schema) == []


def test_URETILEN_HER_CHIPIN_sorgusu_COZULUYOR(schema):
    """9.3'ün ASIL iddiası: *"116'sının 116'sı çözülüyor"* bir ölçümdü — burada yapısal
    garantiye çevriliyor. Katalogdaki HER belirsiz ölçü için üretilen her chip
    `route()`'tan geçmek zorunda."""
    gorulen: set[str] = set()
    kirik: list[tuple[str, str]] = []
    uretilen = 0
    for c in schema["cubes"]:
        for syns in (c.get("measure_synonyms") or {}).values():
            for sy in syns:
                n = cr._norm(str(sy))
                if n in gorulen:
                    continue
                gorulen.add(n)
                adaylar = cr.measure_cube_candidates(n, schema)
                tekil = {x["name"]: (x, m) for x, m in adaylar}
                if len(tekil) < 2:
                    continue
                for o in cr.olcu_netlestirme(list(tekil.values()), schema):
                    uretilen += 1
                    assert o["query"], f"chip sorgusuz üretildi: {o}"
                    cr.reddi_sifirla()
                    if cr.route(str(o["query"]), schema) is None:
                        kirik.append((o["label"], str(o["query"])))
    assert uretilen > 50, f"ön koşul: anlamlı sayıda chip üretilmeli (bulunan: {uretilen})"
    assert not kirik, f"ÇÖZÜLMEYEN CHIP ÜRETİLDİ ({len(kirik)}/{uretilen}): {kirik[:5]}"


def test_DUSEN_netlestirme_chipi_LOGLANIYOR():
    govde = inspect.getsource(cr.olcu_netlestirme)
    assert "_log.info" in govde and "DÜŞÜRÜLDÜ" in govde, \
        "chip düşürmek bir KARARDIR; sessiz kalırsa kaç chip yutulduğu sorulamaz"
