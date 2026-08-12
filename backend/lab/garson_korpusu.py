"""🔴🔴 `A2` — **KASETLİ GARSON KORPUSU**: kapının yeni merkezi.

    python lab/garson_korpusu.py --kaydet     # BİR KEZ, canlı API ile kaydeder
    python lab/garson_korpusu.py              # her demet sonunda, SIFIR API

## Neden bu, bugünkü korpusun yerini alıyor

Raporun `§4i` kararı, ve gerekçesi ölçülmüş:

> *"`/ask` yolunda `route()` **her zaman** denenir — dolayısıyla tam `/ask` yolundan
> koşan bir garson korpusu, route'u da koşturur ve bugünkü LLM'siz korpusun ölçtüğü her
> şeyi **artı devri** ölçer."*

| ölçü | bugünkü korpus (LLM'siz) | **bu** |
|---|---|---|
| route kapsamı | ✅ | ✅ (`source=cube`) |
| garson kapsamı | 🔴 **hiç** | ✅ (`source=cube+llm`) |
| **devir oranı** | 🔴 görünmez — **kayıp sanılıyor** | ✅ doğrudan |
| `(a)/(b)` ayrımı | 🔴 imkânsız | ✅ rozet farkından |
| 🥡 Discovery (mutfak eksiği) | 🔴 hiç | ✅ **ayrı sayılır** |

⊙ `G3` tam olarak bu körlükten geri alındı: korpus *«%95,1→%93,5»* dedi, düşüş
route→garson **devriydi** ve üretimde bir **kazançtı**. Sorulmadı, geri alındı.

## Sınırı — ve neden burada YAZILI

🔴 Payda **kayıt kümesidir**. Bu araç *«korpus %X»* demez, **kayıt kümesi üzerinde**
konuşur. Kaset yalnız kaydedilmiş soruları taşır; kaydedilmemiş bir soru geldiğinde
`KasetEksik` **patlar** — sessizce geçmek, ölçülmemiş bir soruda yeşil vermek olurdu.

⚠ Ve kaset **istem sürümüne** bağlıdır: istem değişince kaset bayatlar ve yeniden
kaydedilmelidir. *Bir kaset, kaydedildiği günün modelini ölçer; bugünün modelini değil.*
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

KASET_YOLU = pathlib.Path(__file__).resolve().parent / "kasetler" / "garson-korpus.json"
TABAN_YOLU = pathlib.Path(__file__).resolve().parent / "garson_korpus_baseline.json"

#: 🔴 Korpus **en basitten en zora** dizilir (döngü kuralı): tek soru → kısa zincir →
#: uzun zincir. Her thread kendi `turlar` listesidir; tur `n`, tur `n-1`'in
#: `cube_query` + `diyalog_durumu` çıktısını taşır.
#:
#: ⚠ Sorular **kullanıcının kelimeleriyle** yazılır, kataloğun kelimeleriyle değil —
#: bugünkü korpusun bilinen körlüğü (*"soruların ≥%97,1'i katalog türevi"*) burada
#: tekrarlanmasın diye.
KORPUS: list[dict] = [
    # ── 1 · en basit: tek soru, tek ölçü ──
    {"ad": "tekil-toplam", "turlar": ["bu yıl toplam ciro"]},
    {"ad": "tekil-kirilim", "turlar": ["bu yıl makine bazında ortalama oee"]},
    {"ad": "tekil-ustunluk", "turlar": ["en çok fire veren makine hangisi bu yıl"]},
    {"ad": "tekil-kiyas", "turlar": ["geçen yıla göre ciro nasıl değişti"]},
    # ── 2 · çok sahipli ölçü: sahibini SÖYLEMELİ ──
    {"ad": "cok-sahipli-bakiye", "turlar": ["bakiye ne kadar"]},
    {"ad": "cok-sahipli-uretim", "turlar": ["bu yıl toplam üretim kg"]},
    # ── 3 · sosyal / niyet ayrımı ──
    {"ad": "sosyal-saf", "turlar": ["teşekkürler"]},
    {"ad": "niyet-recete", "turlar": ["peki ne yapmalıyız"]},
    # ── 4 · yabancı dil: «anlamadım» YOK ──
    {"ad": "arapca", "turlar": ["ما هو إجمالي الإيرادات هذا العام"]},
    # ── 5 · kök-neden: orkestratör ──
    {"ad": "kok-neden", "turlar": ["ram 3 neden düşük"]},
    {"ad": "kok-neden-kiyasli",
     "turlar": ["ram 3 oee neden diğerlerine göre daha düşük bu yıl"]},
    # ── 6 · katalog boşluğu: BEYAN edilmeli, gizlenmemeli ──
    {"ad": "katalog-bosluk", "turlar": ["sebep bazında fire bu yıl"]},
    # ── 7 · kısa zincir (odak varlık) ──
    {"ad": "zincir-odak", "turlar": ["bu yıl makine bazında ortalama oee",
                                     "en düşük olanı hangisi",
                                     "peki neden düşük"]},
    # ── 8 · uzun zincir (zaman odağı + kompozisyon) ──
    {"ad": "zincir-uzun", "turlar": ["bu yıl toplam ciro",
                                     "aylık göster",
                                     "bir de fire ekle",
                                     "en kötü ay hangisi",
                                     "o ayda hangi makine sorumlu"]},
    # ── 9 · en komplike: çapraz küp ──
    {"ad": "capraz-kup",
     "turlar": ["makine bazında karlılık ve enerji tüketimi bu yıl"]},
]

#: Cevap rozetinden **merdiven basamağı**. Tek sahip: burada.
#:
#: ⊙ Bu eşleme raporun `A4` maddesinin ta kendisidir: `source=cube→llm` bir **devir**dir,
#: bir gerileme değil. Onu bir yerde **adlandırmadan** ayırt etmek imkânsızdı.
BASAMAKLAR = {
    "cube": "route",          # 🍳 aşçı kesin bildi — LLM'e hiç gidilmedi
    "vqr": "route",           # doğrulanmış soru deposu — yine sıfır LLM
    "meta": "sosyal",         # veri sorusu değil
    "catalog": "sosyal",      # «neler sorabilirim»
}


def _basamak(cevap: dict) -> str:
    """Bir `/ask` yanıtı merdivenin hangi basamağında bitti?"""
    src = cevap.get("source")
    if src is None:
        return "netlestirme"                       # 🔴 cevap YOK, soru soruldu
    if src in BASAMAKLAR:
        return BASAMAKLAR[src]
    if (cevap.get("cube_query") or {}).get("adhoc"):
        return "discovery"                         # 🥡 mutfak eksiği raporu
    if str(src).startswith("llm:"):
        return "discovery"
    if (cevap.get("plan") or {}).get("adimlar"):
        return "orkestra"                          # 🗣 garson parçalara ayırdı
    return "garson"                                # 🗣 tek fişle halletti


def _rapor_yolu() -> "pathlib.Path":
    """🔴 `§A1` — RAPOR YOLU **TEK SAHİPTE** ve ortamdan yönlendirilebilir.

    İki yerde ayrı ayrı yazılıydı (ön koşul denetimi + `main`) ve ikisi ayrışabilirdi:
    denetim bir dosyayı, yazım başkasını kontrol ederdi (`KAT-1`).

    ⚠ `DIMA_GARSON_RAPOR` bir kolaylık değil bir **onarım yolu**: çıktı dosyası bir
    `--user`'sız koşumdan root'a geçtiyse araç, sahibi olmadığı bir dosyaya yazmak
    zorunda kalmamalıdır. *Bir ölçüm, yazacağı yeri seçemiyorsa ortamına rehindir.*
    """
    import os
    if (_e := os.environ.get("DIMA_GARSON_RAPOR")):
        return pathlib.Path(_e)
    return pathlib.Path(__file__).resolve().parent / "reports" / "garson_korpusu.md"


def _ortam_kusuru_beyan_et() -> None:
    """🔴 `§A1` — ÖLÇÜM KOŞAMIYORSA **SEBEBİ EYLEME ÇEVRİLEBİLİR** OLMALI.

    Ölçüldü (2026-08-11): bu araç `--hepsi`'ye bağlanamıyordu çünkü kontrol-düzlemi
    SQLite dosyası **root sahipliğindeydi** — `--user` bayrağı unutulmuş **tek** bir
    konteyner koşumundan. `CLAUDE.md` bu kusur sınıfını **adıyla** yazıyor (*«bir unutma
    229 dosyayı root'a geçirdi»*) ama araç bunu `401` diye gösteriyordu: yani **ortam**
    kusuru bir **kimlik** kusuru gibi okunuyordu.

    ⚠ Bu fonksiyon bir onarım değil bir **teşhistir**: `chown` ayrıcalık ister ve o
    kararı araç veremez. Verebileceği tek şey, hangi komutun çözeceğini **söylemektir**.

    *Bir ölçüm koşamadığını söylemekle yetinirse, koşamadığı yerde kalır.*
    """
    import os
    import pathlib

    eksik: list[str] = []

    # ① KİMLİK KAYNAĞI — ölçüldü: tohumlanmış kullanıcılar **docker volume'ünde**
    # (`dima_logs`), repodaki `logs/` ise **bayat bir kopya** (yalnız `owner@dima.local`).
    # Varsayılan yapılandırma ise üçüncü bir dosyayı gösteriyor: `control_plane.db` —
    # root sahipliğinde, ürünün hiç kullanmadığı bir artefakt.
    url = os.environ.get("DIMA_DATABASE_URL", "")
    if not url:
        eksik.append(
            "  🔴 `DIMA_DATABASE_URL` YOK → varsayılan `logs/control_plane.db`, ki o\n"
            "     ürünün kullandığı DB **DEĞİL** (canlı: `/app/logs/dima.db`, docker\n"
            "     volume `dima_logs`). Tohumlanmış kullanıcı orada; repodaki kopyada yok.\n"
            "     ÇÖZÜM:  docker cp dima-backend-core:/app/logs/dima.db /tmp/canli.db\n"
            "             -v /tmp:/cp  -e DIMA_DATABASE_URL=sqlite:////cp/canli.db")
    elif url.startswith("sqlite:"):
        yol = pathlib.Path(url.replace("sqlite:///", "").replace("sqlite:", ""))
        if yol.exists() and not os.access(yol, os.W_OK):
            eksik.append(f"  🔴 `{yol}` YAZILAMIYOR — sahibi bu kullanıcı değil.\n"
                         f"     ONARIM:  sudo chown $(id -u):$(id -g) {yol}")

    # ② RAPOR DOSYASI — `--user` unutulmuş bir koşum onu root'a geçirdiyse ölçüm
    # **sonuna kadar koşar** ve son satırda düşer. En pahalı arıza budur: iş yapılır,
    # ürünü atılır.
    _rapor = _rapor_yolu()
    if _rapor.exists() and not os.access(_rapor, os.W_OK):
        eksik.append(f"  🔴 `{_rapor}` YAZILAMIYOR (root sahipli).\n"
                     f"     ONARIM:  sudo chown $(id -u):$(id -g) {_rapor}")

    # ③ KASET — bu aracın *"SIFIR API"* vaadi kasetin **kurulabilmesine** bağlıdır.
    # Kaset sağlayıcının taşıma metodunu (`_chat`/`_ask`) yamalar; sağlayıcı
    # `NoLlmGenerator` ise yamalanacak bir şey yoktur ve araç sessizce **canlı** koşmaya
    # çalışır — `--network none` altında bu bir çökmedir.
    if not os.environ.get("DIMA_LLM_PROVIDER"):
        eksik.append(
            "  ⚠ `DIMA_LLM_PROVIDER` YOK → sağlayıcı `NoLlmGenerator`, kaset\n"
            "     kurulamaz (`_chat`/`_ask` yok) ve araç CANLI koşmaya çalışır.\n"
            "     ÇÖZÜM:  -e DIMA_LLM_PROVIDER=<sağlayıcı>  (kaset oynatır, ağ gerekmez)")

    if eksik:
        raise SystemExit(
            "🔴 ÖLÇÜM KOŞULMADI — ön koşullar eksik (kimlik değil, **ORTAM**).\n"
            + "\n".join(eksik)
            + "\n\n⊙ Bu araç `--hepsi`'ye bu yüzden bağlı değildi: eksikler tek tek\n"
              "  keşfediliyordu. *Bir ölçüm koşamadığını söylerse yeter sanmak, onu\n"
              "  koşamadığı yerde bırakmaktır.*")


def _giris(istemci) -> dict[str, str]:
    """🔴 `/ask` **kimlik doğrulaması ister** — ve bu, ölçüm aracının ilk tuzağıydı.

    İlk yazımda başlık yoktu: her istek 401 döndü, ben onları `source=None` diye
    okudum ve **21/21 «netleştirme»** raporladım. Yani araç, ürünün hiç koşmadığı bir
    turu *"sistem soru sordu"* diye yazdı — ve kaset **0 kayıtla** yeşil göründü.

    *Bir ölçüm aracının en tehlikeli kusuru yanlış ölçmek değil, ölçmediğini
    ölçtüğünü sanmaktır.*
    """
    _ortam_kusuru_beyan_et()
    r = istemci.post("/auth/login", json={"email": "demo-boyahane@usedima.com",
                                          "password": "dima-demo-1234"})
    if r.status_code != 200:
        raise SystemExit(f"🔴 giriş başarısız ({r.status_code}) — ölçüm KOŞULMADI. "
                         "Sessizce devam etmek, kimliksiz bir turu ölçüm sanmak olurdu.")
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _kos(istemci, korpus: list[dict]) -> list[dict]:
    """Her thread'i sırayla koşar; tur `n`, `n-1`'in bağlamını **taşır**."""
    baslik = _giris(istemci)
    out = []
    for s in korpus:
        gecmis: list[str] = []
        cq = None
        durum = None
        for _tur, soru in enumerate(s["turlar"], 1):
            govde: dict = {"question": soru}
            if gecmis:
                govde["history"] = list(gecmis)
            if cq:
                govde["cube_query"] = cq
            if durum:
                govde["diyalog_durumu"] = durum
            r = istemci.post("/ask", json=govde, headers=baslik)
            # 🔴 HTTP hatası bir **cevap sınıfı değildir**. İlk yazımda 401'i
            # `source=None` diye okudum ve *«netleştirme»* saydım — ölçüm, ürünün hiç
            # koşmadığı bir turu bir ürün davranışı gibi raporladı.
            # *Bir hatayı bir sınıfa çevirmek, onu ölçümden silmektir.*
            if r.status_code != 200:
                out.append({"senaryo": s["ad"], "soru": soru, "tur": _tur, "basamak": "hata",
                            "cube": None, "not": f"HTTP {r.status_code}", "satir": 0})
                continue
            d = r.json()
            out.append({"senaryo": s["ad"], "soru": soru, "tur": _tur,
                        "basamak": _basamak(d),
                        "cube": (d.get("cube_query") or {}).get("cube"),
                        "not": (d.get("note") or "")[:120],
                        "satir": len(((d.get("result") or {}).get("rows")) or [])})
            gecmis.append(soru)
            cq = d.get("cube_query") or cq
            durum = d.get("diyalog_durumu") or durum
    return out


def ozet(sonuc: list[dict]) -> dict:
    """🔴 `A3` — **tek yüzde değil, basamak dökümü.**

    *Bir sayı, hangi basamaktan geldiği yazılmadan okunursa, iyileşme ile bozulma aynı
    işareti taşır.*
    """
    d: dict[str, int] = {}
    for r in sonuc:
        d[r["basamak"]] = d.get(r["basamak"], 0) + 1
    d["payda"] = len(sonuc)
    # 🥡 Discovery'nin her ateşlenmesi bir **mutfak eksikliği raporudur** — bir yol
    # değil bir **ölçü**. Ayrı basılır ki oranı sıfıra yaklaştırılabilsin.
    d["bos_cevap"] = sum(1 for r in sonuc
                         if r["basamak"] in ("route", "garson", "orkestra")
                         and r["satir"] == 0)
    return d


def rapor(sonuc: list[dict], iska: int = 0) -> str:
    """Korpus sonucunu markdown'a çevirir.

    🔴🔴 `iska` **ZORUNLU BAĞLAM** (⟳ 2026-08-12, denetim bulgusu). Öncesinde bu
    fonksiyon yalnız `sonuc` alıyordu ve ıska sayısı **artefakta hiç ulaşmıyordu** —
    oysa `kapi()` bir ıskada bile kırmızı veriyor. Bedeli ölçüldü:

        artefakt  : route 9 · garson 2 · orkestra 0 · netlestirme 9 · sosyal 1
        taban     : route 9 · garson 4 · orkestra 4 · netlestirme 3 · sosyal 1

    `route` ve `sosyal` **birebir sabit** (deterministik yol bozulmamış); yalnız
    **LLM'e bağlı** iki basamak çökmüş ve farkın tamamı `netlestirme`'ye gitmiş
    (`garson −2 · orkestra −4 · netlestirme +6`, toplam korunmuş). Bu bir **kaset
    ıskası imzasıdır**, bir ürün gerilemesi değil — ama artefakt bunu **söyleyemiyordu**
    ve iki tur boyunca *«gerileme mi ıska mı»* diye tartışıldı.

    > *Bir ölçümün kırmızısı, sebebini taşımıyorsa bir alarm değil bir muammadır.*
    """
    o = ozet(sonuc)
    sat = ["# Kasetli garson korpusu", "",
           f"payda **{o['payda']}** (⚠ kayıt kümesi — *«korpus %»* değil)", ""]
    if iska:
        sat += [f"🔴 **KASET ISKASI: {iska}** — bu turlar **ölçülmedi**; aşağıdaki "
                "sayılar bir ürün ölçümü DEĞİL, eksik bir kasetin gölgesidir. "
                "`route`/`sosyal` sabit kalıp `garson`/`orkestra` düşüyorsa sebep "
                "neredeyse kesin budur (kaseti tazeleyin).", ""]
    else:
        sat += ["✅ kaset ıskası **yok** — sayılar bir ürün ölçümüdür.", ""]
    sat.append("| basamak | n | pay |")
    sat.append("|---|---|---|")
    for k in ("route", "garson", "orkestra", "netlestirme", "sosyal", "discovery",
              "hata"):
        n = o.get(k, 0)
        isaret = " 🥡" if k == "discovery" and n else ""
        sat.append(f"| {k}{isaret} | {n} | %{100 * n / max(o['payda'], 1):.1f} |")
    sat.append("")
    if o["bos_cevap"]:
        sat.append(f"🔴 **boş cevap: {o['bos_cevap']}** — makbuzlu boş bir sonuç bir "
                   "yanlıştır: doğruluğunun kanıtı gibi görünür.")
        sat.append("")
    # 🔴🔴 `§A12` — **TUR BAZINDA KIRILIM.** SParC'ın ölçümü: Turn 1 **%38,6** → Turn 3
    # **%3,7** → Turn ≥4 **%1,1**; yani çok turlu bellekte doğruluk **çöküyor**. Kartın
    # şikâyeti *«bizde tur bazında hiç ölçüm yok»* idi — ve haklıydı: korpus turları
    # koşuyordu ama raporu **tur numarasını hiç yazmıyordu**.
    #
    # ⊙ Ölçüm **bedava**: `_kos` zaten tur sırasını biliyor. *Bir ölçümün eksikliği,
    # verinin yokluğu değil, onu yazmayan bir satırdır.*
    #
    # ⚠ Bu kırılım **cevaplanabilirlik** ölçer (bir küpe bağlandı mı), doğruluk değil —
    # ikisini karıştırmak SParC'ın sayısıyla bizimkini kıyaslanabilir sanmaktır.
    _tur_dagilim: dict[int, list[str]] = {}
    for r in sonuc:
        _tur_dagilim.setdefault(int(r.get("tur") or 1), []).append(r["basamak"])
    if len(_tur_dagilim) > 1:
        sat.append("## Tur bazında cevaplanabilirlik (`§A12`)")
        sat.append("")
        sat.append("| tur | n | cevaplanan | pay |")
        sat.append("|---|---|---|---|")
        for t in sorted(_tur_dagilim):
            b = _tur_dagilim[t]
            ok = sum(1 for x in b if x in ("route", "garson", "orkestra"))
            sat.append(f"| {t} | {len(b)} | {ok} | %{100 * ok / max(len(b), 1):.0f} |")
        sat.append("")
        sat.append("⚠ **Cevaplanabilirlik ≠ doğruluk.** SParC'ın *«Turn≥4 → %1,1»* sayısı "
                   "açık şemada **birebir SQL eşleşmesi** ölçer; bu tablo kapalı bir "
                   "semantik katmanda **bir küpe bağlanabilme**yi ölçer. İki sayı "
                   "kıyaslanamaz — *aynı adı taşıyan iki ölçüt, aynı şeyi ölçmez.*")
        sat.append("")
    sat.append("| senaryo | soru | tur | basamak | cube | satır |")
    sat.append("|---|---|---|---|---|---|")
    for r in sonuc:
        sat.append(f"| {r['senaryo']} | `{r['soru'][:44]}` | {r.get('tur', 1)} | "
                   f"{r['basamak']} | {r['cube'] or '—'} | {r['satir']} |")
    return "\n".join(sat)


def kapi(sonuc: list[dict], iska: int = 0) -> tuple[int, str]:
    """Gerileme kapısı — **eşik değil**, `gercek_dunya` ile aynı ilke.

    🔴 Kırmızı veren üç şey, ve üçü de *doğru cevap* eksenindedir:
      1. `discovery` arttı → mutfak eksiği büyüdü
      2. `bos_cevap` arttı → makbuzlu boşluk
      3. `route + garson + orkestra` toplamı düştü → **cevaplanabilirlik** azaldı

    ⚠ `route ↔ garson` arasındaki kayma kırmızı **DEĞİLDİR**: o bir **devir**dir ve
    raporun `A4`'ü tam olarak bunun için var. *Sistemin doğru yönde geliştiği anda
    kırmızı veren bir kapı, geliştirmeyi geri aldırır.*
    """
    yeni = ozet(sonuc)
    # 🔴 **BİR ISKA, SESSİZCE GEÇEMEZ.** İlk koşumda `36 isabet · 1 ıska` çıktı ve
    # koşum yeşil verdi: eksik kayıt bir istisna fırlattı, sağlayıcı zinciri onu yuttu
    # ve cevap **canlıya düşmeye çalıştı**. Yani kaset o soruda ölçmüyordu — ama rapor
    # onu ölçülmüş gibi yazdı.
    #
    # ⊙ Bu, kasetin kendi sözleşmesinin ihlali: *"sessizce geçmek, ölçülmemiş bir soruda
    # YEŞİL vermek olurdu."* İstisna doğru fırlatılıyordu; eksik olan **kapının onu
    # duymasıydı**. *Bir kuralı yazmak, onu duyan bir kulak koymak değildir.*
    if iska:
        return 1, (f"KAPI KIRMIZI — 🔴 kasette {iska} ıska: bu sorular ölçülMEDİ, "
                   "sonuç GEÇERSİZ. Kaseti yeniden kaydet (`--kaydet`).")
    if not TABAN_YOLU.exists():
        TABAN_YOLU.write_text(json.dumps(yeni, ensure_ascii=False, indent=1),
                              encoding="utf-8")
        return 0, f"TABAN YAZILDI → {yeni}\n  🔴 BU DOSYAYI COMMIT ET"
    eski = json.loads(TABAN_YOLU.read_text(encoding="utf-8"))
    dusen = []
    # 🔴 Bir tek HTTP hatası bile kapıyı kırmızı yapar: ölçülemeyen bir tur, ölçülmüş
    # sayılamaz. (Bu satır, aracın kendi 21/21 yanlış okumasının kapısıdır.)
    if yeni.get("hata", 0):
        dusen.append(f"🔴 {yeni['hata']} tur HTTP hatası verdi — ölçüm GEÇERSİZ")
    if yeni.get("discovery", 0) > eski.get("discovery", 0):
        dusen.append(f"🥡 discovery ARTTI: {eski.get('discovery', 0)} → "
                     f"{yeni['discovery']} — mutfak eksiği büyüdü")
    if yeni["bos_cevap"] > eski.get("bos_cevap", 0):
        dusen.append(f"🔴 boş cevap ARTTI: {eski.get('bos_cevap', 0)} → "
                     f"{yeni['bos_cevap']}")
    _c = lambda o: sum(o.get(k, 0) for k in ("route", "garson", "orkestra"))  # noqa: E731
    if _c(yeni) < _c(eski):
        dusen.append(f"🔴 cevaplanabilirlik düştü: {_c(eski)} → {_c(yeni)}")
    if dusen:
        return 1, "KAPI KIRMIZI:\n  " + "\n  ".join(dusen)
    return 0, f"kapı yeşil · {yeni}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kaydet", action="store_true",
                    help="🔴 CANLI API kullanır — bir kez koşulur, sonra kaset yeter")
    ap.add_argument("--kapi", action="store_true")
    ap.add_argument("--taban-yaz", action="store_true")
    a = ap.parse_args()

    # 🔴 `§A1` — ORTAM DENETİMİ **EN BAŞTA**. İlk yazımda bu çağrı `_giris()`'in içindeydi
    # ve **hiç ulaşılamıyordu**: kontrol-düzlemi şeması uygulama ayağa kalkarken hizalanır,
    # yani yazma denemesi `TestClient` kurulurken patlıyordu. Teşhis, teşhis edeceği
    # arızadan **sonra** koşuyordu. *Bir kapının yeri, koruduğu şeyden önce olmalıdır.*
    _ortam_kusuru_beyan_et()

    # 🔴 Ölçüm koşumunun **zamanlayıcıya işi yoktur** — ve o iş parçacığı süreci
    # ayakta tutuyordu: `main.py:109` bir `while True: time.sleep(60)` döngüsü kurar,
    # koşum korpusu bitirip kaseti yazdıktan sonra konteyner **8 dakika** asılı kaldı.
    # Her kapı koşumunun ardında asılı bir konteyner bırakmak, ölçümün kendisinden
    # pahalıya gelir. *Bir aletin bitmesi, işini bitirmesiyle aynı şey değildir.*
    # ⚠ `setdefault` DEĞİL: ortam dosyası zaten `true` taşıyorsa ezilmezdi ve
    # konteyner yine asılı kalırdı (ölçüldü). Bir ölçüm koşumunda bu karar
    # çağırana bırakılmaz.
    os.environ["DIMA_SCHEDULER_ENABLED"] = "false"
    os.environ["DIMA_KASET"] = "kayit" if a.kaydet else "oynat"
    os.environ["DIMA_KASET_YOLU"] = str(KASET_YOLU)
    if a.taban_yaz and TABAN_YOLU.exists():
        TABAN_YOLU.unlink()

    from fastapi.testclient import TestClient

    from app.main import app

    _iska = 0
    with TestClient(app) as istemci:
        if a.kaydet:
            # 🔴🔴 **KAYIT, KASET KENDİ OYNATMASI ALTINDA KAPANANA KADAR TEKRARLANIR.**
            #
            # ⊙ Ölçüldü: tek geçişli kayıt **hiçbir zaman** 0 ıskaya inmedi
            # (10 → 3 → 2 → 1 → 1 → 1). Sebep yapısal: bir geçiş, o geçişin kendi
            # yolundaki çağrıları kaydeder; ama kaset dolunca **yol değişir** (artık
            # her şey diskten geldiği için bütçe/zamanlama farklı davranır) ve yeni
            # yol, kaydedilmemiş bir çağrı isteyebilir. Kovaladığım tek ıska tam olarak
            # buydu ve dört koşum boyunca **elle** kapatmaya çalıştım.
            #
            # Doğru ölçüt bir sayı değil bir **sabit nokta**: kaset, kendi oynatması
            # altında yeni çağrı doğurmuyorsa kapalıdır.
            #
            # ⚠ Tavan var ve aşılırsa **söylenir** — yakınsamayan bir döngü, sessizce
            # sonsuza kadar denemekten iyidir.
            # *Bir kaydı tamamlamak, bir kez kaydetmek değil; kaydın kendini
            # doğurmayı bıraktığı ana kadar sürdürmektir.*
            for gecis in range(1, 6):
                sonuc = _kos(istemci, KORPUS)
                k = app.state.llm.kaset
                yeni_kayit = k.iska
                print(f"  geçiş {gecis}: {k.isabet} isabet · {yeni_kayit} YENİ kayıt")
                k.isabet = k.iska = 0
                if not yeni_kayit:
                    break
            else:
                print("  ⚠ 5 geçişte kapanmadı — kaset SABİT NOKTAYA ulaşmadı, "
                      "oynatmada ıska bekleyin")
            yol = app.state.llm.kaset.yaz(muhur="canli")
            print(f"kaset yazıldı: {yol} ({len(app.state.llm.kaset.kayitlar)} kayıt)")
        else:
            sonuc = _kos(istemci, KORPUS)
        if not a.kaydet:
            k = getattr(app.state.llm, "kaset", None)
            if k:
                _iska = k.iska
                print(f"kaset: {k.isabet} isabet · {k.iska} ıska")

    hedef = _rapor_yolu()
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(rapor(sonuc, iska=_iska), encoding="utf-8")
    print(f"Rapor: {hedef}")
    kod, mesaj = kapi(sonuc, iska=_iska)
    print(mesaj)
    return kod if a.kapi else 0


if __name__ == "__main__":
    raise SystemExit(main())
