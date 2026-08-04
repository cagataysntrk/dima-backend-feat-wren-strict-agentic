"""NL korpus motoru — ~1000 soru + çok-adımlı süreç, TÜM şirketlerde (ADR-0018).

Kullanıcı direktifi (2026-07-24): "bine yakın alakalı/alakasız soru ve süreç üret,
elimizdeki DB tablolarından faydalan, tüm sektör/şirketlerde test et, her soruya
tepkiyi ölç." Bu harness bunu yapar ve taksonomi çıkarır — kurgu yeniden-tasarımının
(arketip + konuşma çekirdeği) önce/sonra kanıt motorudur.

Tasarım: /ask HTTP yolunu (route→refine→chip→dönem→LLM merdiveni) TAM koşar ama
DB'ye BAĞLANMAZ — execute=False + enrichment no-op → dört şirket de yerelde/hızlı.
LLM yok (rule provider): deterministik çekirdeğin tavanı ölçülür.

Koşum:  .venv/bin/python lab/nl_corpus.py            # dört şirket
Çıktı:  lab/reports/nl_corpus.md  (+ nl_corpus.json ham)
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tests.conftest as _conf  # noqa: E402,F401  (env kurulumu)
from tests.conftest import make_tenant_user  # noqa: E402

# Şirket → (login, tenant_slug). demo-boyahane aktif şirkettir (slug=None).
COMPANIES = [
    ("boyahane", "owner@dima.local", "owner-parola-123", None),
    ("atiksan", "owner@atiksan.test", "atiksan-parola-1", "atiksan"),
    ("gulteks", "owner@gulteks.test", "gulteks-parola-1", "gulteks"),
    ("gitas", "owner@gitas.test", "gitas-parola-1", "gitas"),
]

PERIODS = ["", "bu yıl", "geçen ay", "son 3 ay", "temmuz ayı", "2. çeyrek", "geçen yıl",
           "bu ay", "son 30 gün", "2025", "tüm zamanlar"]

# İlişkisiz/gürültü/kötü-niyet — sistem bunlara DÜRÜST duvar ya da meta ile cevap vermeli
NOISE = [
    "merhaba", "dima nedir", "teşekkürler", "asdf qwerty zxcv", "1234567",
    "bana bir fıkra anlat", "hava nasıl", "seni seviyorum", "@#$%^&*",
    "select * from users", "drop table faturalar", "python kodu yaz",
    "en iyi film hangisi", "kaç yaşındasın", "",
]

# Yetenek/niyet kalıpları — global olması gerekenler (log kanıtı: dar kalıp)
CAPABILITY = [
    "hangi kırılımlar var", "hangi kırılımlara göre detaylandırabilirim",
    "kırılımları ver", "kırılımları göster", "başka ne sorabilirim",
    "neler yapabilirsin", "hangi ölçüler var", "bu raporu nasıl detaylandırırım",
]

# GERÇEK KULLANICI DAĞARCIĞI (metadata'dan BAĞIMSIZ — zorluk katmanı, ADR-0018).
# Ölçü adı → bir müşterinin GERÇEKTE yazacağı ifadeler. Sistem bunları tanımalı;
# tanımıyorsa sinonim/arketip boşluğu (harness'in asıl ölçtüğü). Bilinçli olarak
# etiket kelimesini DIŞLAR — yalnız "zor" (alternatif) ifadeler.
REAL_PHRASINGS = {
    "satis_tutari": ["hasılat", "ne kadar sattık", "satışlarımız", "gelirimiz", "cirosu"],
    "alim_tutari": ["ne kadar aldık", "alımlarımız", "satın almalar", "tedariğimiz"],
    "bakiye": ["kalan borcu", "hesap durumu", "ne kadar borçlu"],
    "toplam_borc": ["borçları", "borç durumu", "ne kadar borcu var"],
    "toplam_alacak": ["tahsilatlar", "alacaklarımız", "ne kadar alacağımız var"],
    "satis_miktari": ["kaç kilo satıldı", "satılan miktar", "ne kadar sevk ettik"],
    "alim_miktari": ["kaç kilo aldık", "alınan miktar", "topladığımız"],
    "hareket_sayisi": ["kaç işlem oldu", "kaç hareket var", "işlem adedi"],
    "satis_fatura_sayisi": ["kaç fatura kesildi", "fatura adedi"],
    "toplam_ciro": ["hasılat", "gelirimiz", "ne kadar sattık"],
    "kar": ["kazancımız", "ne kadar kar ettik", "kârımız"],
    "fire_orani_yuzde": ["ne kadar fire verdik", "fire durumu", "zayiat oranı"],
    "ort_oee": ["verimliliğimiz", "makine verimi", "randıman"],
}

# Takip adımları (çok-adımlı süreç yapı taşları)
STEP_GRAN = ["aylık", "haftalık", "günlük", "çeyreklere göre", "yıllık", "kova:çeyrek"]
STEP_SORT = ["en yüksekten sırala", "en düşük 3", "ilk 5", "ilk 10", "tabloyu sırala"]
STEP_PERIOD = ["bu yıl", "geçen ay", "tüm zamanlar", "2. çeyrek", "son 3 ay"]
STEP_VIEW = ["grafik ver", "çizgi grafik", "tablo göster", "pasta grafik"]
STEP_NOISE = ["teşekkürler", "peki", "asdf", "bunu beğenmedim"]


def _sinif(d, expected=None):
    if d.get("_http"):
        return f"HTTP{d['_http']}"
    if d.get("sql"):
        cube = (d.get("cube_query") or {}).get("cube")
        if expected == "NOISE":
            return "YANLIS-OK(gürültüye SQL)"
        if isinstance(expected, set) and cube not in expected:
            return f"CUBE-SAPMA({cube})"
        return "OK"
    note = d.get("note") or ""
    src_trace = " ".join(d.get("trace") or [])
    if "meta/ürün" in src_trace:
        return "META" if expected == "NOISE" else "META-SAPMA"
    if "dönem" in note or "Hangi dönem" in note:
        return "CLARIFY:dönem"
    if "ölçü" in note or "Hangi ölçü" in note:
        return "CLARIFY:ölçü"
    if "konu" in note.lower() or "birden çok" in note:
        return "CLARIFY:konu"
    if note:
        return "NOTE" if expected != "NOISE" else "NOTE(gürültü✓)"
    return "BOŞ"


def _measure_words(cube):
    ms = cube.get("measure_synonyms_display") or {}
    return [(m, (v if isinstance(v, str) else (v or [m])[0])) for m, v in ms.items()]


def _dim_words(cube):
    dl = cube.get("dimension_labels") or {}
    return [v for v in dl.values() if v]


def gen_single(schema):
    """Tek-soru korpusu: ölçü×dönem×kırılım×topN + gürültü + yetenek + çapraz-ölçü."""
    cubes = schema.get("cubes", [])
    valid = {c["name"] for c in cubes}
    out = []  # (soru, beklenti)
    for cube in cubes:
        dims = _dim_words(cube)
        # ÖLÇÜM KÖR NOKTASI DÜZELTMESİ (2 Ağustos 2026): eskiden yalnız `dims[:2]`
        # sorulurdu. İlişki-türevi boyutlar (Faz 1) cube metadata'sının SONUNA eklendiği
        # için korpus onları HİÇ sormuyordu — yani planın ana ölçüm aracı, ölçmesi gereken
        # geliştirmeye YAPISAL OLARAK KÖRDÜ (üreteç 7 cube'a boyut ekledi, korpusun toplam
        # tur sayısı DEĞİŞMEDİ). Baş + son 2 boyut alınır: hem eski kapsam korunur hem
        # yeni eklenenler görünür. Tümünü almak korpusu 5-7 katına çıkarırdı.
        dims = list(dict.fromkeys(dims[:2] + dims[-2:]))
        for m, word in _measure_words(cube):
            for p in PERIODS:
                kaynak = {cube["name"]}   # soruyu HANGİ cube'un sözlüğünden ürettik
                # ⚠️ FAZ 0.19 — **SEMANTİK VAKA ANAHTARI** `(cube, ölçü, niyet)`.
                # Bu üçlü döngü bir **KARTEZYEN ÜRÜNDÜR** ve iki yönde çarpıtır:
                #  · YUKARI: `elektrik`in TEK sahiplik hatası, 11 dönem × boyut =
                #    **10+ ayrı başarısızlık** olarak sayılır → yanlış-cube yüzdesinin içi
                #    birkaç terimin **çarpımıdır**.
                #  · AŞAĞI: üreteç yalnız **kataloğun bildiği** ifadeleri kurar; bir kusur
                #    sınıfı korpusta **yapısal olarak görünmez** olabilir.
                # Anahtar **dönem ve boyutu İÇERMEZ** — çarpım tek vakaya çöker. Ham tur
                # paydası **korunur** (KURAL A: geçmiş tabanlar ona bağlı).
                _c = cube["name"]
                out.append((f"{p} {word}".strip(), valid, kaynak, (_c, m, "düz")))
                for dw in dims:
                    out.append((f"{p} {dw} bazında {word}".strip(), valid, kaynak,
                                (_c, m, "kırılım")))
                if dims:
                    out.append((f"en çok {word} yapılan 5 {dims[0]} {p}".strip(), valid,
                                kaynak, (_c, m, "üstünlük")))
                    out.append((f"en düşük {word} olan {dims[0]} {p}".strip(), valid,
                                kaynak, (_c, m, "üstünlük")))
    # ZORLUK KATMANI: gerçek kullanıcı ifadeleri (metadata'da OLMAYAN kelimeler).
    # Beklenti = o ölçüyü içeren cube'lar; sistem arketip/sinonimle tanımalı.
    measure_to_cubes: dict[str, set] = {}
    for cube in cubes:
        for mn in cube.get("measures") or []:
            measure_to_cubes.setdefault(mn, set()).add(cube["name"])
    for mn, phrasings in REAL_PHRASINGS.items():
        target = measure_to_cubes.get(mn)
        if not target:
            continue
        for ph in phrasings:
            for p in ("", "bu yıl", "geçen ay"):
                out.append((f"{p} {ph}".strip(), target, target, (None, mn, "gerçek-ifade")))
    for n in NOISE:
        # Gürültü/kapasite turlarının **semantik vakası yoktur** — `(cube, ölçü, niyet)`
        # üçlüsüne oturmazlar. `None` ile işaretlenir ve semantik paydaya GİRMEZLER;
        # ham payda onları saymaya devam eder (KURAL A).
        out.append((n, "NOISE", None, None))
    for cap in CAPABILITY:
        out.append((cap, "CAP", None, None))
    # tekilleştir
    seen, uniq = set(), []
    for q, e, kaynak, vaka in out:
        if q and q not in seen:
            seen.add(q)
            uniq.append((q, e, kaynak, vaka))
    return uniq


def gen_processes(schema):
    """Çok-adımlı süreçler (3/5/10 adım): drill-down, pivot, çapraz-cube, gürültü enj."""
    cubes = schema.get("cubes", [])
    valid = {c["name"] for c in cubes}
    procs = []  # (ad, [adımlar])
    for cube in cubes:
        mws = _measure_words(cube)
        if not mws:
            continue
        _, w0 = mws[0]
        dims = _dim_words(cube)
        d0 = dims[0] if dims else None
        # 3 adım: aç → gran → sırala
        procs.append((f"{cube['name']}-drill3",
                      [f"bu yıl {w0}", "aylık", "en yüksekten sırala"]))
        # 5 adım: aç → kırılım → gran → topN → görünüm
        if d0:
            procs.append((f"{cube['name']}-pivot5",
                          [f"bu yıl {w0}", f"{d0} bazında", "aylık",
                           f"en çok 5 {d0}", "grafik ver"]))
        # 10 adım: uzun keşif + gürültü + dönem değişimi + çapraz-cube
        other = next((c for c in cubes if c["name"] != cube["name"]), None)
        ow = _measure_words(other)[0][1] if other and _measure_words(other) else w0
        procs.append((f"{cube['name']}-uzun10",
                      [f"bu yıl {w0}", "aylık", d0 and f"{d0} bazında" or "haftalık",
                       "teşekkürler", "geçen ay", "en düşük 3",
                       "çeyreklere göre", "tüm zamanlar",
                       f"{ow}", "grafik ver"]))
    return procs, valid


def run_company(name, login, pw, slug):
    from fastapi.testclient import TestClient

    import app.wren_service as ws
    from app.main import create_app

    # DB-bağımsız harness: canlı değer zenginleştirme + dry_plan'ı kapat — bu harness
    # ROUTING KALİTESİNİ ölçer (icra değil); dry_plan mssql bağlantı nesnesi ister ve
    # tünelsiz patlar, routing başarısını NOTE olarak gizlerdi. Kimlik dönüşü → route
    # başardıysa cube yanıtı üretilir, dört şirket eşit ölçülür.
    # `*a` BİLİNÇLİ: Faz B1 bu metoda ikinci bir parametre (fiziksel ad haritası) ekledi ve
    # buradaki iki-argümanlı lambda sessizce KIRILDI — ölçüm aracı `TypeError` verip her
    # şirketi "HATA" olarak raporluyordu, yani DETERMİNİSTİK TAVAN AYLARCA ÖLÇÜLEMEZDİ.
    # Bu bir monkeypatch olduğu için hiçbir tip denetimi yakalayamaz; imzayı sabitlemek
    # yerine esnetmek tek dayanıklı çözümdür (gövde zaten hiçbir argüman kullanmıyor).
    ws.WrenService._enrich_categorical = lambda self, *a, **k: None
    ws.WrenService._enrich_cube_dim_values = lambda self, *a, **k: None
    ws.WrenService.dry_plan = lambda self, sql, *a, **k: sql

    make_tenant_user(login, pw, tenant_slug=slug)
    c = TestClient(create_app())
    c.__enter__()
    r = c.post("/auth/login", json={"email": login, "password": pw})
    assert r.status_code == 200, f"{name}: {r.text}"
    c.headers["Authorization"] = f"Bearer {r.json()['access_token']}"

    schema = c.get("/schema").json()
    cats = Counter()
    fails = defaultdict(list)
    dogru = Counter()          # doğru-cube kanalı (erişimden AYRI)
    yanlis_ornek: list = []
    discovery_ornek: list = []

    def ask(q, cq=None):
        body = {"question": q, "execute": False}
        if cq is not None:
            body["cube_query"], body["history"] = cq, ["önceki"]
        rr = c.post("/ask", json=body)
        return rr.json() if rr.status_code == 200 else {"_http": rr.status_code}

    # tekil
    singles = gen_single(schema)
    # FAZ 0.19 — vaka → {tüm varyantları doğru mu}. **KATI (AND):** bir vakanın
    # varyantlarından biri bile yanlış cube'a giderse vaka **yanlıştır**. Gevşek (OR/
    # çoğunluk) sayım, tek bir doğru varyantla bir sahiplik hatasını gizlerdi.
    vaka_sonuc: dict[tuple, bool] = {}
    for q, exp, kaynak, vaka in singles:
        d = ask(q)
        s = _sinif(d, exp)
        cats[f"tekil::{s}"] += 1
        # DOĞRULUK KANALI (2 Ağustos 2026): `exp` TÜM cube adlarıdır, yani yukarıdaki
        # sınıflandırma "SQL üretebildi mi"yi (ERİŞİM) ölçer — yanlış cube'a gitmek de
        # OK sayılır. Kanıt: üreteç "bölüm bazında oee"yi enerji_makine'den oee'ye
        # taşıdı ve bu metrik yalnız +2 gördü. `kaynak` sorunun HANGİ cube'un
        # sözlüğünden üretildiğini taşır → gerçek doğruluk ölçülebilir. Eski metrik
        # KORUNUR (karşılaştırılabilirlik), bu AYRI bir kanaldır.
        if kaynak and d.get("sql"):
            secilen = (d.get("cube_query") or {}).get("cube")
            # ÜÇ AYRI SONUÇ (ikisini birbirine karıştırmak yanıltıcı olur):
            #   dogru     → beklenen cube'dan yapısal cevap
            #   yanlis    → BAŞKA bir cube'dan yapısal cevap (asıl belirsizlik sınıfı)
            #   discovery → hiç cube_query yok (ham SQL) — yanlış cube DEĞİL, cube YOK.
            #               Deterministik katmanın kapsayamadığı soru; chip/drill de yok.
            if secilen is None:
                dogru["discovery"] += 1
                if vaka is not None:
                    vaka_sonuc[vaka] = False
                discovery_ornek.append((q, sorted(kaynak)))
            elif secilen in kaynak:
                dogru["dogru"] += 1
                if vaka is not None:
                    vaka_sonuc.setdefault(vaka, True)
            else:
                dogru["yanlis"] += 1
                if vaka is not None:
                    vaka_sonuc[vaka] = False
                yanlis_ornek.append((q, sorted(kaynak), secilen))
        # NOTE = duvar (beklenen cube vardı ama route/refine başaramadı) — asıl hedef.
        if any(s.startswith(x) for x in ("CUBE-SAPMA", "YANLIS", "HTTP", "BOŞ", "META-SAPMA", "NOTE")) \
                and exp not in ("NOISE", "CAP"):
            fails[s].append((q, (d.get("note") or "")[:60], (d.get("trace") or [])[-1:]))

    # süreç
    procs, valid = gen_processes(schema)
    n_steps = 0
    for pname, steps in procs:
        cq = None
        for i, step in enumerate(steps):
            if not step:
                continue
            n_steps += 1
            d = ask(step, cq=cq if i else None)
            exp = "NOISE" if step in STEP_NOISE else (valid if i == 0 else None)
            s = _sinif(d, exp)
            cats[f"süreç::{s}"] += 1
            if d.get("sql") and d.get("cube_query"):
                cq = d["cube_query"]  # bağlamı ilerlet
            if any(s.startswith(x) for x in ("HTTP", "BOŞ", "YANLIS")):
                fails[f"süreç:{s}"].append((f"[{pname}#{i}] {step}", "", (d.get("trace") or [])[-1:]))

    c.__exit__(None, None, None)
    return {"company": name, "n_single": len(singles), "n_proc_steps": n_steps,
            "cats": dict(cats), "fails": {k: v[:12] for k, v in fails.items()},
            "dogru_cube": dict(dogru), "yanlis_cube_ornek": yanlis_ornek[:20],
            # FAZ 0.19 — İKİNCİ PAYDA. Ham tur paydası yukarıda AYNEN duruyor.
            "vaka_toplam": len(vaka_sonuc),
            "vaka_dogru": sum(1 for v in vaka_sonuc.values() if v),
            "discovery_ornek": discovery_ornek[:20]}



# ---------------------------------------------------------------- FAZ 9.5: GERİLEME KAPISI

TABAN = Path(__file__).resolve().parent / "nl_corpus_baseline.json"
#: Erişim yüzdesinde kabul edilen sapma (puan). Korpus üretimi deterministiktir ama
#: yüzdeler tam sayıya yuvarlanır; 1 puan tek bir turun kenar durumundan gelebilir.
TOLERANS_PUAN = 1
#: Toplam doğru-cube oranında kabul edilen sapma (puan). ZORUNLU olarak daha DAR:
#: doğruluk bu planın ana metriğidir ve *"sessiz-yanlış"* tam olarak burada görünür.
TOLERANS_DOGRULUK = 0.5


def _taban_beklenen() -> dict:
    """Tabanın **en son turunu** döndürür — kök değerleri değil.

    Kök alanlar 2 Ağustos'un dondurulmuş *"önce"* fotoğrafıdır (KURAL A) ve önce/sonra
    kıyası için oradadır. Bir **gerileme kapısı** ise bugünkü seviyeyi korumalıdır:
    %93,2'den %86,3'e düşmek, köke bakan bir kapıda **yeşil** görünürdü — yani kapı tam
    da korumak için var olduğu şeyi kaçırırdı.
    """
    d = json.loads(TABAN.read_text())
    turlar = d.get("_turlar") or []
    son = turlar[-1] if turlar else {}
    sirketler = {}
    for ad, v in (d.get("sirketler") or {}).items():
        sirketler[ad] = dict(v)
    for ad, v in (son.get("sirketler") or {}).items():
        sirketler.setdefault(ad, {}).update(v)
    return {
        "kaynak": son.get("faz") or "kök taban",
        # FAZ 0.19 — semantik taban: en son turda varsa o, yoksa kök. Kapı bunu
        # bulamazsa *"tabanda YOK"* der ve ters-yön kontrolünü **atlar** — yani
        # dondurulmadığı sürece kapı sessizce devre dışıdır (bilinen, yazılı sınır).
        "vaka_dogru_yuzde": son.get("vaka_dogru_yuzde", d.get("vaka_dogru_yuzde")),
        "sirketler": sirketler,
        "dogru_cube_yuzde": son.get("toplam_dogru_cube_yuzde",
                                    d.get("toplam_dogru_cube_yuzde")),
    }


def kapi_degerlendir(reports: list[dict]) -> tuple[bool, list[str]]:
    """Taze koşumu dondurulmuş tabanla kıyaslar. Döner: (gecti, satırlar).

    ## Neden bu kapı var (denetim, Faz 9.5)

    `nl_corpus_baseline.json` sürüm kontrolündeydi ve **hiçbir tüketicisi yoktu**: KURAL
    A'nın *"taban dondurulur"* maddesi bir **not**tu, kapı değil. `eval` tarafı kapılı
    (`test_eval_gate.py`), korpus tarafı değildi — yani bu planın **ana metriğinin**
    (doğru-cube %) gerilemesi sessizce kaybolabilirdi.

    Kapı fail-closed DEĞİL bilerek: korpus koşumu dakikalar sürer ve CI reçetesinin
    dışındadır. Ama koşulduğunda **kararı kendisi verir**, insan gözüne bırakmaz.
    """
    beklenen = _taban_beklenen()
    satirlar = [f"TABAN: {beklenen['kaynak']}"]
    gecti = True
    toplam_d = toplam_p = 0
    for rep in reports:
        if rep.get("error"):
            satirlar.append(f"  {rep['company']}: HATA — kıyaslanamadı")
            gecti = False
            continue
        total = sum(rep["cats"].values())
        ok = sum(v for k, v in rep["cats"].items() if "::OK" in k)
        erisim = 100 * ok / max(total, 1)
        dc = rep.get("dogru_cube") or {}
        toplam_d += dc.get("dogru", 0)
        toplam_p += sum(dc.get(k, 0) for k in ("dogru", "yanlis", "discovery"))
        b = (beklenen["sirketler"].get(rep["company"]) or {}).get("erisim_yuzde")
        if b is None:
            satirlar.append(f"  {rep['company']}: erişim %{erisim:.0f} (tabanda YOK)")
            continue
        fark = erisim - b
        isaret = "✅" if fark >= -TOLERANS_PUAN else "❌ GERİLEME"
        satirlar.append(f"  {rep['company']}: erişim %{erisim:.0f} (taban %{b}) {isaret}")
        if fark < -TOLERANS_PUAN:
            gecti = False
    if toplam_p:
        yuzde = 100 * toplam_d / toplam_p
        b = beklenen["dogru_cube_yuzde"]
        isaret = "✅" if yuzde >= b - TOLERANS_DOGRULUK else "❌ GERİLEME"
        satirlar.append(f"  TOPLAM doğru-cube: %{yuzde:.1f} (taban %{b}) {isaret}")

        # ═══ FAZ 0.19 — İKİ PAYDA TERS YÖNE GİDERSE **KIRMIZI** ═══════════════
        #
        # 🔴 *"Birkaç terimi düzelttim, sayı uçtu"* yanılsamasının kapanı. Ham tur paydası
        # bir **kartezyen üründür**: `elektrik`in TEK sahiplik hatası 11 dönem × boyut =
        # 10+ ayrı başarısızlık olarak sayılır. Yani **tek bir terimi** düzeltmek ham
        # yüzdeyi birkaç puan zıplatabilir — hiçbir yeni semantik vaka kazanılmadan.
        #
        # Ters yön daha da tehlikeli: semantik vaka sayısı **düşerken** ham yüzde
        # **artıyorsa**, kapsam daralmış ama şişme onu gizlemiştir.
        #
        # Kural: iki payda **aynı yöne** gitmeli. Ayrışma bir **yorum farkı değil,
        # bir KIRMIZIDIR** — çünkü ikisinden biri artık ölçtüğünü sanmadığı şeyi ölçüyordur.
        v_top = sum((r.get("vaka_toplam") or 0) for r in reports)
        v_dog = sum((r.get("vaka_dogru") or 0) for r in reports)
        b_vak = beklenen.get("vaka_dogru_yuzde")
        if v_top:
            v_yuzde = 100 * v_dog / v_top
            sisme = toplam_p / v_top if v_top else 0
            satirlar.append(
                f"  SEMANTİK VAKA: {v_dog}/{v_top} = %{v_yuzde:.1f}"
                + (f" (taban %{b_vak})" if b_vak is not None else " (tabanda YOK)")
                + f" · şişme katsayısı {sisme:.1f}×")
            if b_vak is not None:
                ham_yon = (yuzde > b + 0.05) - (yuzde < b - 0.05)
                vak_yon = (v_yuzde > b_vak + 0.05) - (v_yuzde < b_vak - 0.05)
                if ham_yon and vak_yon and ham_yon != vak_yon:
                    gecti = False
                    satirlar.append(
                        "  🔴 İKİ PAYDA TERS YÖNE GİDİYOR — ham "
                        f"%{yuzde:.1f} (taban %{b}) ↔ semantik %{v_yuzde:.1f} "
                        f"(taban %{b_vak}). Bu bir YORUM FARKI DEĞİL: biri kartezyen "
                        "şişmeyi, öteki gerçek kapsamı ölçüyor ve ikisi ayrıştı.")
        if yuzde < b - TOLERANS_DOGRULUK:
            gecti = False
    return gecti, satirlar


def main():
    reports = []
    for name, login, pw, slug in COMPANIES:
        try:
            reports.append(run_company(name, login, pw, slug))
            print(f"[{name}] tamam")
        except Exception as exc:
            print(f"[{name}] HATA: {type(exc).__name__}: {exc}")
            reports.append({"company": name, "error": str(exc)})

    Path("lab/reports").mkdir(exist_ok=True)
    Path("lab/reports/nl_corpus.json").write_text(json.dumps(reports, ensure_ascii=False, indent=1))

    lines = ["# NL korpus — tüm şirketler (ADR-0018 kanıtı)\n"]
    for rep in reports:
        lines.append(f"\n## {rep['company']}")
        if rep.get("error"):
            lines.append(f"- HATA: {rep['error']}")
            continue
        total = sum(rep["cats"].values())
        lines.append(f"- tekil senaryo: {rep['n_single']} · süreç adımı: {rep['n_proc_steps']} · toplam tur: {total}")
        # FAZ 0.19 — **İKİ PAYDA YAN YANA.** Ham tur paydası kartezyen şişmeyi taşır
        # (11 dönem × boyut aynı semantik vakayı defalarca sayar); semantik vaka paydası
        # `(cube, ölçü, niyet)` üçlüsüne çöker. İkisi **birlikte** okunur: biri artıp
        # öteki azalıyorsa *"birkaç terimi düzelttim, sayı uçtu"* yanılsaması vardır.
        vt, vd = rep.get("vaka_toplam") or 0, rep.get("vaka_dogru") or 0
        if vt:
            lines.append(
                f"- **SEMANTİK VAKA: {vd}/{vt} (%{100 * vd // vt})** — `(cube, ölçü, niyet)`; "
                f"dönem/boyut çarpımı TEK vakaya çöker. Ham tur paydası ({total}) "
                f"**korunur** (KURAL A): geçmiş tabanlar ona bağlı. "
                f"Şişme katsayısı: **{total / vt:.1f}×**")
        dc = rep.get("dogru_cube") or {}
        n_dc = sum(dc.get(k, 0) for k in ("dogru", "yanlis", "discovery"))
        if n_dc:
            lines.append(
                f"- **DOĞRU CUBE: {dc.get('dogru',0)}/{n_dc} (%{100*dc.get('dogru',0)//n_dc})**"
                f" · yanlış cube: {dc.get('yanlis',0)} · Discovery'ye düştü:"
                f" {dc.get('discovery',0)} — sorunun üretildiği cube ile cevabın cube'u aynı"
                " mı. Yukarıdaki OK oranı ERİŞİMİ ölçer (herhangi bir yoldan SQL üretildi"
                " mi); bu satır DOĞRULUĞU ölçer.")
        for q, bekl, secilen in (rep.get("yanlis_cube_ornek") or [])[:10]:
            lines.append(f"    - `{q}` beklenen={bekl} seçilen={secilen}")
        for k, v in sorted(rep["cats"].items(), key=lambda x: -x[1]):
            lines.append(f"  - {k}: {v} ({100*v//max(total,1)}%)")
        for k, items in rep["fails"].items():
            lines.append(f"  ### {k} ({len(items)})")
            for q, note, tr in items:
                lines.append(f"    - `{q}` {note} {tr}")
    Path("lab/reports/nl_corpus.md").write_text("\n".join(lines))
    print("\nRapor: lab/reports/nl_corpus.md")
    for rep in reports:
        if rep.get("error"):
            continue
        total = sum(rep["cats"].values())
        ok = sum(v for k, v in rep["cats"].items() if "::OK" in k)
        dc = rep.get("dogru_cube") or {}
        n_dc = sum(dc.get(k, 0) for k in ("dogru", "yanlis", "discovery"))
        dogru_str = (f" · DOĞRU-CUBE={dc.get('dogru',0)}/{n_dc} "
                     f"({100*dc.get('dogru',0)//n_dc}%) "
                     f"[yanlış={dc.get('yanlis',0)} discovery={dc.get('discovery',0)}]"
                     ) if n_dc else ""
        print(f"  {rep['company']}: {total} tur, erişim OK={ok} "
              f"({100*ok//max(total,1)}%){dogru_str}")

    # FAZ 9.5 — DONDURULMUŞ TABANA KARŞI GERİLEME KAPISI. `--kapi` ile çıkış kodu da
    # gerilemeyi taşır (betikten koşulabilsin); onsuz yalnız raporlar.
    gecti, satirlar = kapi_degerlendir(reports)
    print("\n" + "\n".join(satirlar))
    if "--kapi" in sys.argv and not gecti:
        print("\nKAPI KIRMIZI — dondurulmuş tabana göre gerileme var.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
