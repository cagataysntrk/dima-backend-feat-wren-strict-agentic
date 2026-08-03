"""FAZ 0.5 — KONUŞMA SENARYOSU DOĞRULAMA (§4.7). Sınıf başına vaka raporu.

    python lab/konusma_senaryolari.py              # hızlı/yapısal (LLM yok, ağsız)
    python lab/konusma_senaryolari.py --json
    python lab/konusma_senaryolari.py --live       # GERÇEK sağlayıcı, SIRALI, hız-sınırlı

## Neden AYRI bir araç, neden `nl_corpus.py`'ye eklenmedi

`nl_corpus.py` **günlük regresyon kilididir** ve sınıf-başına-sayım sözleşmesi
(`nl_corpus_baseline.json`) ona bağlıdır. Yeni senaryo sınıflarını oraya karıştırmak o
tabanı kirletirdi — KURAL A'nın tam olarak yasakladığı şey. Bu araç aynı harness
kalıbını (aynı monkeypatch'ler, aynı TestClient) **çağırır**, kopyalamaz.

## Planın ⟳ SINIR KURALI — bu dosyanın en önemli tasarım kararı

Planın *"her senaryo kendi vaka raporunu üretir"* maddesi bugünkü üreteçle
**sınırsızdır**: `gen_processes` dört şirkette **10.865 tur** üretiyor. Birebir
uygulanırsa binlerce `.md` doğar ve *"her vaka görünür olsun"* amacının **tam tersi**
olur — kimse okuyamaz. Bu yüzden:

* vaka raporu **senaryo SINIFI** başına (tur başına DEĞİL),
* her sınıf raporu **temsilci turun TAM adımlarını** + sınıf-düzeyi özeti taşır,
* `--live` sınıf başına **katmanlı örneklem** koşar ve **düşürülen tur sayısını
  RAPORLAR** — sessiz kırpma yok.

## ERİŞİM ve DOĞRULUK AYRI ölçülür (§4.7-6)

*"Cevap geldi mi"* yeterli değil: gelen `cube_query` **gerçekten** doğru cube/ölçü/
boyutu mu seçti? Bu ayrım **zorunludur**, çünkü bir düzeltmenin "çalıştığı" görünmesi
DOĞRU şeyi düzelttiği anlamına gelmez — 2a-1'de (`elektrik`) tam olarak bu oldu:
yanlış→cevapsız dönüşümü "iyileşme" gibi görünmüştü.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tests.conftest as _conf  # noqa: E402,F401  (env kurulumu)
from tests.conftest import make_tenant_user  # noqa: E402

RAPOR_DIZINI = Path(__file__).resolve().parent / "reports" / "konusma_senaryolari"
#: `--live` sınıf başına kaç senaryo koşar (katmanlı örneklem).
LIVE_ORNEKLEM = 3
#: `--live` turlar arası bekleme (saniye) — API'ye yığılma YOK (planın açık kısıtı).
LIVE_BEKLE = 1.5


# ---------------------------------------------------------------- katalog yardımcıları

def _olculer(cube: dict) -> list[tuple[str, str]]:
    """(ölçü_adı, NL kelimesi) — cube'un KENDİ sözlüğünden, elle yazılmaz."""
    disp = cube.get("measure_synonyms_display") or {}
    syn = cube.get("measure_synonyms") or {}
    out = []
    for m in cube.get("measures") or []:
        ad = m if isinstance(m, str) else m.get("name")
        kelime = disp.get(ad) or next(iter(syn.get(ad) or []), None) or ad
        out.append((ad, str(kelime)))
    return out


def _boyutlar(cube: dict) -> list[tuple[str, str]]:
    disp = cube.get("dimension_synonyms_display") or {}
    syn = cube.get("dimension_synonyms") or {}
    out = []
    for d in cube.get("dimensions") or []:
        ad = d if isinstance(d, str) else d.get("name")
        kelime = disp.get(ad) or next(iter(syn.get(ad) or []), None) or ad
        out.append((ad, str(kelime)))
    return out


# ---------------------------------------------------------------- senaryo sınıfları

def _uret(schema: dict) -> list[dict]:
    """Kataloğa göre senaryo üretir. Her sınıf: {sinif, ad, adimlar, bekle}.

    `bekle(adim_index, cevap)` → (gecti: bool, aciklama: str). ERİŞİM ve DOĞRULUK
    ayrı ayrı raporlanır; `bekle` DOĞRULUK kanalıdır.
    """
    cubes = [c for c in (schema.get("cubes") or []) if _olculer(c)]
    senaryolar: list[dict] = []

    from app import cube_router as _cr

    def _net_olcu(cube: dict) -> tuple[str, str] | None:
        """Cube'un BELİRSİZ OLMAYAN ilk ölçüsü — yoksa None.

        ⚠️ **FAZ 8'İN KENDİ BULGUSU (2026-08-03).** İlk sürüm `_olculer(c)[0]`'ı körlemesine
        alıyordu. `bakim` için bu `borç`a, `cari` için yine `borç`a denk geliyordu — ve
        `borç` GERÇEKTEN belirsizdir (`cari` + `mizan`), yani §6.1g'nin netleştirme chip'i
        **doğru şekilde** ateşliyordu. Senaryo o zaman *niyet ettiği şeyi* (konu değişimi ·
        dönem daraltma) değil, **netleştirme yolunu** test ediyor ve "başarısız" raporluyordu.

        `konu_degisimi` **2/5** ve `donem_duzeltme`'nin kalan başarısızlığı bu yüzdendi —
        ikisi de ÜRÜN HATASI DEĞİL, ölçüm aracının hatası. Bu oturumda **beşinci kez**
        aracın kendisi yanlış ölçtü (MIMARI §6.4: *"ölçüm aracının kendisi de bir
        bağımlılıktır"*).
        """
        for m_ad, m_kel in _olculer(cube):
            _cr.reddi_sifirla()
            hit = _cr.route(_cr._norm(f"bu yil {m_kel}"), schema)
            if hit and (hit.get("cube_query") or {}).get("cube") == cube["name"]:
                return (m_ad, m_kel)
        return None

    def ekle(sinif, ad, adimlar, bekle):
        senaryolar.append({"sinif": sinif, "ad": ad, "adimlar": adimlar, "bekle": bekle})

    def _cube_dogru(hedef):
        def f(i, d):
            cq = d.get("cube_query") or {}
            if not cq:
                return False, f"cube_query YOK (source={d.get('source')}, not={d.get('note')!r})"
            if cq.get("cube") != hedef:
                return False, f"cube={cq.get('cube')} beklenen={hedef}"
            return True, f"cube={hedef}"
        return f

    for c in cubes[:6]:                      # katmanlı: ilk 6 cube yeter, hepsi değil
        ad = c["name"]
        _net = _net_olcu(c)
        if _net is None:
            continue          # bu cube'un HİÇBİR ölçüsü tek başına çözülmüyor → senaryo kurulamaz
        (m_ad, m_kel) = _net
        dims = _boyutlar(c)
        d_kel = dims[0][1] if dims else None
        zaman = (c.get("time_dimensions") or [None])[0]
        if not zaman:
            continue

        # a1/a2 — ÇOKLU AY (bitişik). İki alt-vaka: §1.6'nın gözlemlenen "tümü" hatası
        # ("trend" kapsam kapısını kırıyor) ve DAHA KÖTÜ olan sessiz "Ocak-only".
        def _bitisik(i, d, _z=zaman):
            cq = d.get("cube_query") or {}
            fs = [f for f in (cq.get("filters") or []) if f.get("dimension") == _z]
            if not fs:
                return False, "dönem filtresi YOK — 'tüm zamanlar'a düştü (§1.6 hatası)"
            gte = next((f["value"] for f in fs if f["operator"] == "gte"), None)
            lte = next((f["value"] for f in fs if f["operator"] == "lte"), None)
            if not (gte and lte):
                return False, f"aralık yarım: gte={gte} lte={lte}"
            if not (str(gte).endswith("-01-01") and str(lte).startswith(str(gte)[:4] + "-03")):
                return False, f"aralık ocak–mart değil: {gte}..{lte}"
            return True, f"{gte}..{lte}"

        ekle("coklu_ay_trendli", f"{ad}-trendli",
             [f"ocak şubat mart {m_kel} değişim trendi"], _bitisik)
        ekle("coklu_ay_trendsiz", f"{ad}-trendsiz",
             [f"ocak şubat mart {m_kel}"], _bitisik)

        # a7 — AYRIK AY (2a-4). Yeni yetenek; tabanı BURADA alınır.
        def _ayrik(i, d):
            cq = d.get("cube_query") or {}
            isaret = cq.get("ayrik_aylar") or {}
            if not isaret:
                # Netleştirmeye düşmek de KABUL EDİLEBİLİR bir sonuçtur (sessiz-yanlış
                # değil) — ama "cevaplandı" saymayız; ayrımı rapor gösterir.
                return False, ("netleştirmeye düştü" if d.get("suggestions")
                               else f"ayrik_aylar YOK (source={d.get('source')})")
            aylar = isaret.get("aylar") or []
            return (len(aylar) == 2, f"aylar={aylar}")

        ekle("ayrik_ay", f"{ad}-ayrik", [f"ocak ve mart {m_kel}"], _ayrik)

        # a2 — DÖNEM DÜZELTME TAKİBİ: kontrollü GENİŞ ilk soru + doğal dilde daraltma.
        def _daraldi(i, d):
            """⚠️ ÖLÇÜM ARACININ KENDİ HATASI DÜZELTİLDİ (2026-08-03).

            İlk sürüm beklenen cube'un zaman boyutunu (`_z`) SABİTLİYORDU. Ama `route()`
            soruyu BAŞKA bir cube'a çözebilir (ör. `elektrik` → `surdurulebilirlik`, bilinen
            açık sahiplik kararı) ve o cube'un zaman boyutu FARKLIDIR — kontrol, çalışan bir
            düzeltmeyi "başarısız" sayıyordu. `enerji_makine-daralt` tam olarak böyle YANLIŞ
            raporlandı; elle koşulduğunda `gte 2026-05-02` üretiyordu.

            MIMARI §6.4'ün dersi: *"ölçüm aracının kendisi de bir bağımlılıktır"* —
            `lab/nl_corpus.py` aylarca kırıkken kimse fark etmemişti. Artık dönem filtresi
            CEVABIN KENDİ cube'una göre aranır; hangi boyut olduğu VARSAYILMAZ.
            """
            if i == 0:
                return bool(d.get("cube_query")), "ilk soru"
            cq = d.get("cube_query") or {}
            if not cq:
                return False, f"düzeltme cevabı YOK (not={d.get('note')!r})"
            gelen = cq.get("cube")
            zamanlar = {t for c2 in (schema.get("cubes") or [])
                        if c2.get("name") == gelen
                        for t in (c2.get("time_dimensions") or [])}
            fs = [f for f in (cq.get("filters") or [])
                  if f.get("dimension") in zamanlar]
            return (bool(fs), f"cube={gelen} dönem filtresi={fs or 'YOK'}")

        ekle("donem_duzeltme", f"{ad}-daralt",
             [f"tüm zamanlar {m_kel}", "sadece son 3 ay"], _daraldi)

        # a5 — GÖRÜNÜM DÖNÜŞÜMÜ: yapı SİLİNMEMELİ (Faz 5'in şartının doğrudan testi).
        if d_kel:
            def _gorunum(i, d):
                if i == 0:
                    return bool(d.get("cube_query")), "ilk rapor"
                if not d.get("cube_query"):
                    return False, "görünüm değişince YAPI KAYBOLDU (Faz 5 şartı ihlali)"
                return (d.get("view_hint") == "pie",
                        f"view_hint={d.get('view_hint')}")

            ekle("gorunum_donusumu", f"{ad}-pasta",
                 [f"bu yıl {d_kel} bazında {m_kel}", "pasta grafik"], _gorunum)

            # a6 — LİSTE NİYETİ (2a-5). Yeni yetenek; tabanı BURADA alınır.
            def _liste(i, d, _hedef=ad):
                cq = d.get("cube_query") or {}
                if not cq:
                    return False, f"cevapsız (not={d.get('note')!r})"
                if not cq.get("dimensions"):
                    return False, "kırılım YOK — döküm isteğine dejenere toplam"
                return (d.get("view_hint") == "table",
                        f"dims={cq.get('dimensions')} view_hint={d.get('view_hint')}")

            ekle("liste_niyeti", f"{ad}-listele",
                 [f"bu yıl {d_kel} bazında {m_kel} listele"], _liste)

        # a4 — KONU DEĞİŞİMİ ORTASINDA (başka cube'un ölçüsüne atla).
        digeri, o_net = None, None
        for x in cubes:
            if x["name"] == ad:
                continue
            o_net = _net_olcu(x)
            if o_net:
                digeri = x
                break
        if digeri and d_kel and o_net:
            o_kel = o_net[1]

            def _konu(i, d, _hedef=digeri["name"]):
                if i < 2:
                    return bool(d.get("cube_query")), "hazırlık adımı"
                cq = d.get("cube_query") or {}
                if not cq:
                    return False, f"konu değişince cevap kayboldu (not={d.get('note')!r})"
                return (cq.get("cube") == _hedef, f"cube={cq.get('cube')} beklenen={_hedef}")

            ekle("konu_degisimi", f"{ad}→{digeri['name']}",
                 [f"bu yıl {m_kel}", f"{d_kel} bazında", f"bu yıl {o_kel}"], _konu)

    # a3 — NETLEŞTİRME CHIP'İNE CEVAP VERME (2a-2'nin ürettiği chip'ler gerçekten
    # tıklanabiliyor mu). Belirsiz sinonim KATALOGDAN bulunur, elle yazılmaz.
    from app import cube_router as cr

    belirsiz = None
    for c in cubes:
        for syns in (c.get("measure_synonyms") or {}).values():
            for sy in syns:
                cr.reddi_sifirla()
                if cr.route(f"bu yil {sy}", schema) is None and cr.red_gerekcesi() == "R1":
                    adaylar = cr.measure_cube_candidates(cr._norm(f"bu yil {sy}"), schema)
                    if len({x["name"] for x, _ in adaylar}) >= 2:
                        belirsiz = str(sy)
                        break
            if belirsiz:
                break
        if belirsiz:
            break
    if belirsiz:
        def _chip(i, d):
            if i == 0:
                chips = d.get("suggestions") or []
                return (len(chips) >= 2,
                        f"chip={[s['label'] for s in chips]} not={bool(d.get('note'))}")
            return (bool(d.get("cube_query")),
                    f"chip tıklanınca cube_query={(d.get('cube_query') or {}).get('cube')}")

        # 2. adım çalışma anında ilk chip'in `query`'siyle DOLDURULUR (aşağıda).
        # ⚠️ ERİŞİM MUHASEBESİ NOTU: bu sınıfın İLK adımı BİLEREK `cube_query` üretmez —
        # netleştirme chip'i **geçerli ve doğru** bir cevaptır (§6.1g). `erisim` sayacı
        # "sql/cube_query geldi mi" diye baktığı için bu sınıf **0/1** görünür. Bu bir
        # kusur DEĞİL bir muhasebe artefaktıdır; `dogruluk` kanalı (1/1) gerçeği söyler.
        # Sayacı bu sınıf için gevşetmek metriği ZAYIFLATIRDI (her netleştirme "erişim"
        # sayılırdı) — o yüzden sayaç değil, KAYIT düzeltiliyor.
        ekle("netlestirme_cevabi", f"belirsiz:{belirsiz}",
             [f"bu yıl {belirsiz}", "__CHIP__"], _chip)

    # B — §1.7 VQR KALICILIK: bilerek yanlış çözülen bir soru öğrenilip PARAFRAZINDA
    # aynı yanlış cevabı `source="vqr"` ile geri veriyor mu? Planın ZORUNLU çıktısı.
    def _vqr(i, d):
        if i == 0:
            return bool(d.get("sql")), f"ilk cevap source={d.get('source')}"
        kaynak = d.get("source") or ""
        if kaynak == "vqr":
            return False, ("PARAFRAZ VQR'DAN GELDİ — §1.7 riski CANLI "
                           "(insan onayı olmadan tekrar oynatıldı)")
        return True, f"parafraz source={kaynak} (replay YOK)"

    ekle("vqr_kalicilik", "elektrik-parafraz",
         ["bu yıl elektrik", "bu yılki elektrik tüketimimiz ne kadar"], _vqr)

    return senaryolar


# ---------------------------------------------------------------- koşum

def kos(schema, c, senaryolar, *, live: bool, orneklem: int) -> tuple[list[dict], dict]:
    """Senaryoları koşar. Döner: (sonuçlar, {sınıf: düşürülen_tur}) — SESSİZ KIRPMA YOK."""
    from collections import defaultdict

    sinifta: dict[str, int] = defaultdict(int)
    dusurulen: dict[str, int] = defaultdict(int)
    sonuclar: list[dict] = []

    for sen in senaryolar:
        s = sen["sinif"]
        if live and sinifta[s] >= orneklem:
            dusurulen[s] += 1
            continue
        sinifta[s] += 1
        cq = None
        adimlar_raporu = []
        erisim_ok = dogruluk_ok = True
        for i, adim in enumerate(sen["adimlar"]):
            if adim == "__CHIP__":
                chips = (adimlar_raporu[-1]["cevap"].get("suggestions") or []) if adimlar_raporu else []
                if not chips:
                    dogruluk_ok = False
                    adimlar_raporu.append({"soru": "__CHIP__", "cevap": {},
                                           "gecti": False, "aciklama": "tıklanacak chip YOK"})
                    break
                adim = chips[0]["query"]
            body = {"question": adim, "execute": False}
            if cq is not None and i:
                body["cube_query"], body["history"] = cq, ["önceki"]
            rr = c.post("/ask", json=body)
            d = rr.json() if rr.status_code == 200 else {"_http": rr.status_code}
            gecti, aciklama = sen["bekle"](i, d)
            if not d.get("sql") and not d.get("cube_query"):
                erisim_ok = False
            if not gecti:
                dogruluk_ok = False
            adimlar_raporu.append({"soru": adim, "cevap": d, "gecti": gecti,
                                   "aciklama": aciklama})
            if d.get("cube_query"):
                cq = d["cube_query"]
            if live:
                time.sleep(LIVE_BEKLE)      # API'ye yığılma YOK
        sonuclar.append({"sinif": s, "ad": sen["ad"], "adimlar": adimlar_raporu,
                         "erisim": erisim_ok, "dogruluk": dogruluk_ok})
    return sonuclar, dict(dusurulen)


def _rapor_yaz(sonuclar: list[dict], dusurulen: dict, live: bool) -> None:
    """Vaka raporu SINIF başına — tur başına DEĞİL (planın ⟳ sınır kuralı)."""
    from collections import defaultdict

    RAPOR_DIZINI.mkdir(parents=True, exist_ok=True)
    gruplar: dict[str, list[dict]] = defaultdict(list)
    for r in sonuclar:
        gruplar[r["sinif"]].append(r)

    for sinif, rs in gruplar.items():
        erisim = sum(1 for r in rs if r["erisim"])
        dogru = sum(1 for r in rs if r["dogruluk"])
        # TEMSİLCİ TUR: başarısız varsa İLK BAŞARISIZ (öğretici olan odur), yoksa ilki.
        temsilci = next((r for r in rs if not r["dogruluk"]), rs[0])
        satirlar = [
            f"# Senaryo sınıfı: `{sinif}`", "",
            f"- senaryo sayısı: **{len(rs)}**",
            f"- **ERİŞİM** (cevap üretildi): **{erisim}/{len(rs)}**",
            f"- **DOĞRULUK** (doğru cube/dönem/yapı): **{dogru}/{len(rs)}**",
            f"- düşürülen tur (örneklem sınırı): **{dusurulen.get(sinif, 0)}**"
            + ("" if live else "  _(hızlı modda örneklem uygulanmaz)_"),
            "",
            "> ERİŞİM ve DOĞRULUK **ayrı** ölçülür: bir düzeltmenin *çalıştığı* görünmesi,",
            "> DOĞRU şeyi düzelttiği anlamına gelmez (2a-1 `elektrik` dersi — yanlış→cevapsız",
            "> dönüşümü 'iyileşme' gibi görünmüştü).", "",
            f"## Temsilci tur — `{temsilci['ad']}`"
            + ("  ⚠️ (ilk BAŞARISIZ vaka)" if not temsilci["dogruluk"] else ""), "",
        ]
        for i, a in enumerate(temsilci["adimlar"]):
            d = a["cevap"]
            cq = d.get("cube_query") or {}
            satirlar += [
                f"### adım {i + 1}: `{a['soru']}`", "",
                f"- sonuç: {'✅' if a['gecti'] else '❌'} — {a['aciklama']}",
                f"- source: `{d.get('source')}`",
                f"- cube_query: `{json.dumps(cq, ensure_ascii=False) if cq else 'YOK'}`",
                f"- not: {d.get('note') or '—'}",
                f"- chip: {[s['label'] for s in (d.get('suggestions') or [])] or '—'}",
                f"- trace (son): {(d.get('trace') or ['—'])[-1]}", "",
            ]
        if len(rs) > 1:
            satirlar += ["## Sınıfın tüm vakaları", "",
                         "| senaryo | erişim | doğruluk |", "|---|---|---|"]
            satirlar += [f"| `{r['ad']}` | {'✅' if r['erisim'] else '❌'} "
                         f"| {'✅' if r['dogruluk'] else '❌'} |" for r in rs]
        (RAPOR_DIZINI / f"{sinif}.md").write_text("\n".join(satirlar) + "\n",
                                                  encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Faz 0.5 — konuşma senaryosu doğrulama")
    ap.add_argument("--live", action="store_true",
                    help="GERÇEK sağlayıcı, SIRALI ve hız-sınırlı (ağ ister; CI dışı)")
    ap.add_argument("--orneklem", type=int, default=LIVE_ORNEKLEM)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    from fastapi.testclient import TestClient

    import app.wren_service as ws
    from app.main import create_app

    if not args.live:
        # Hızlı/yapısal mod — `nl_corpus.py` ile AYNI kalıp: DB'ye bağlanmaz, LLM yok.
        ws.WrenService._enrich_categorical = lambda self, *a, **k: None
        ws.WrenService._enrich_cube_dim_values = lambda self, *a, **k: None
        ws.WrenService.dry_plan = lambda self, sql, *a, **k: sql

    make_tenant_user("owner@dima.local", "owner-parola-123", tenant_slug=None)
    c = TestClient(create_app())
    c.__enter__()
    r = c.post("/auth/login", json={"email": "owner@dima.local",
                                    "password": "owner-parola-123"})
    assert r.status_code == 200, r.text
    c.headers["Authorization"] = f"Bearer {r.json()['access_token']}"
    schema = c.get("/schema").json()

    senaryolar = _uret(schema)
    sonuclar, dusurulen = kos(schema, c, senaryolar, live=args.live,
                              orneklem=args.orneklem)
    c.__exit__(None, None, None)
    _rapor_yaz(sonuclar, dusurulen, args.live)

    from collections import defaultdict
    ozet: dict = defaultdict(lambda: {"n": 0, "erisim": 0, "dogruluk": 0})
    for s in sonuclar:
        o = ozet[s["sinif"]]
        o["n"] += 1
        o["erisim"] += int(s["erisim"])
        o["dogruluk"] += int(s["dogruluk"])
    cikti = {"mod": "live" if args.live else "yapisal",
             "sinif_sayisi": len(ozet), "senaryo_sayisi": len(sonuclar),
             "dusurulen_tur": dusurulen, "siniflar": dict(ozet),
             "rapor_dizini": str(RAPOR_DIZINI)}
    if args.json:
        print(json.dumps(cikti, ensure_ascii=False, indent=2))
        return
    print("=" * 74)
    print(f"FAZ 0.5 — KONUŞMA SENARYOSU DOĞRULAMA  ·  mod={cikti['mod']}")
    print("=" * 74)
    print(f"{'sınıf':<24}{'n':>4}{'ERİŞİM':>9}{'DOĞRULUK':>11}   düşürülen")
    for s, o in sorted(ozet.items()):
        print(f"  {s:<22}{o['n']:>4}{o['erisim']:>9}{o['dogruluk']:>11}"
              f"{dusurulen.get(s, 0):>12}")
    print(f"\nVaka raporları (SINIF başına): {RAPOR_DIZINI}")
    if dusurulen:
        print(f"⚠ örneklem sınırıyla DÜŞÜRÜLEN tur: {dusurulen} — sessiz kırpma yok")


if __name__ == "__main__":
    main()
