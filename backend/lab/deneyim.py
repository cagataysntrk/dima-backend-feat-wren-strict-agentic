"""FAZ X — DENEYİM SÜİTİ: *"akıyor mu?"* sorusunun **sayısal** cevabı.

    python lab/deneyim.py --live            # GERÇEK sağlayıcı (asıl ölçüm)
    python lab/deneyim.py                   # yapısal duman — KAPI DEĞİL, dürüstçe söylenir
    python lab/deneyim.py --live --senaryo analist_turu

## Bu araç neyi ölçer — ve neden var olan üç araç yetmedi

| araç | sorduğu soru |
|---|---|
| `eval/run.py` | *tek soruda* doğru cube seçildi mi? |
| `lab/nl_corpus.py` | dört şirkette **regresyon** var mı? |
| `lab/konusma_senaryolari.py` | bir takip **turu** doğru çözüldü mü? |
| **`lab/deneyim.py`** | **bir KONUŞMA tatmin edici miydi?** |

Üçü de *bir turu* ölçüyor. Ürün vaadi ise bir **thread**: *"bir veri analisti gibi
konuşan, anlayan, anlatan"*. O vaadin ölçüsü tur değil, **sözleşmedir**.

## Ürün sözleşmesi — yedi satır (plandan aynen)

    1  Konuşma turu YENİ SQL YAZMAZ, mevcut makbuza çapalanır
    2  "Bunu analiz et" → ≥3 olgu + guard'lı anlatı + ≥2 devam chip'i
    3  5 turluk thread'de yapı HİÇ kaybolmaz ("ilişkilendiremedim" 0 kez)
    4  Sosyal ifade: 0 LLM · 0 SQL
    5  Belirsizlikte TAHMİN YOK, SORU var; onay bağlama yazılır
    6  Her cevap MAKBUZLU
    7  GERİ DÖNÜLEBİLİR: her karta dönüp devam → `POST /cube` ile 0 LLM

Her senaryo yalnız **kendisini ilgilendiren** satırları ölçer; ilgilendirmeyen satır
`⊘ ÖLÇÜLEMEDİ`'dir — yeşile yuvarlamak *"risk yok"* yalanı üretirdi (Faz 9.6 kararı).

## Kalıp KOPYALANMADI

`_canli_ortami_geri_yukle`, `LIVE_BEKLE` ve istemci kurulumu
`lab/konusma_senaryolari.py`'den **import edilir**. Planın açık şartı budur ve gerekçesi
ölçülmüştür: `--live` bayrağı bir kez zaten yalan söylemişti (`tests.conftest`
sağlayıcıyı `rule`'a sabitliyordu) ve o düzeltmenin **tek** bir yerde durması gerekir.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# ⚠ SIRA ÖNEMLİ: `konusma_senaryolari` gerçek ortamı `tests.conftest`'ten ÖNCE yakalar.
# Buradan import etmek o yakalamayı da devralır — kendi kopyamızı yazsaydık `--live`
# yeniden sessizce `rule`'a düşerdi (ölçülmüş kusur, MIMARI §6.4).
from lab.konusma_senaryolari import (  # noqa: E402
    LIVE_BEKLE,
    _canli_ortami_geri_yukle,
)

RAPOR_DIZINI = Path(__file__).resolve().parent / "reports" / "deneyim"

# --- SÖZLEŞME SATIRLARI -------------------------------------------------------------

S1_CAPA = "1·çapa: konuşma turu yeni SQL yazmaz"
S2_ANLAT = "2·anlat: ≥3 olgu + anlatı + ≥2 chip"
S3_SUREKLILIK = "3·süreklilik: bağlam hiç kopmaz"
S4_SOSYAL = "4·sosyal: 0 LLM · 0 SQL"
S5_BELIRSIZLIK = "5·belirsizlik: tahmin yok, soru var"
S6_MAKBUZ = "6·makbuz: her cevap gerekçeli"
S7_GERI_DONUS = "7·geri dönüş: 0 LLM ile replay"

KOPMA_IZI = "ilişkilendiremedim"


def _llm_yolu(d: dict) -> bool:
    return str(d.get("source") or "").startswith(("llm", "rule"))


def _makbuzlu(d: dict) -> bool:
    """Makbuz = *"bu cevap nereden geldi"* sorusunun cevabı. Üç taşıyıcıdan biri
    yeterlidir; üçü de yoksa cevap gerekçesizdir."""
    return bool(d.get("explain") or d.get("trace") or d.get("contract_id"))


# --- SENARYOLAR (thread = ÇOK TURLU konuşma) ----------------------------------------
#
# Her senaryo: (ad, açıklama, turlar, ölçülen sözleşme satırları).
# Tur bir dize ya da ("__CUBE__", indeks) — ikincisi `POST /cube` ile GERİ DÖNÜŞTÜR.

SENARYOLAR: tuple[dict, ...] = (
    {
        "ad": "analist_turu",
        "aciklama": "Bir veri analistinin doğal turu: rapor → anla → neden → ne yapmalı.",
        "turlar": ["bu yıl makine bazında oee",
                   "bunu analiz et",
                   "bu neden böyle?",
                   "ne yapmalıyız?",
                   "peki fire ne durumda?"],
        "olculen": (S1_CAPA, S2_ANLAT, S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "grafik_ustunde",
        "aciklama": "Kullanıcı grafiğe bakıp onun ÜSTÜNDE konuşuyor — yeni sorgu yazmadan.",
        "turlar": ["son 6 ayda aylık toplam fire kg",
                   "bunu yorumla",
                   "en kötü ay hangisi?",
                   "o ayı makine bazında aç"],
        "olculen": (S1_CAPA, S2_ANLAT, S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "donem_duzeltme",
        "aciklama": "Dönem yanlış anlaşıldı; kullanıcı KONUŞMA DİLİYLE düzeltiyor.",
        # Gerçek kullanıcı "son 3 ay" demez, "yok ya son 3 ayı ver" der; ve yer-durum
        # ekini (son 6 ayDA) doğal olarak kullanır — Faz X'te ölçülen kusur tam buydu.
        "turlar": ["makine bazında oee",
                   "bu yıl",
                   "yok ya sadece son 3 ayda",
                   "aylık göster",
                   "en düşük hangisi"],
        "olculen": (S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "belirsizlik",
        "aciklama": "İki cube'un ölçüsü aynı adı taşıyor → TAHMİN DEĞİL SORU beklenir.",
        # ⚠ Üçüncü tur `cari` cube'unda GERÇEKTEN olan bir kırılım olmalı: ilk yazımda
        # "makine bazında" demiştim ve `cari`'de makine boyutu YOK — gelen dürüst ret
        # bir bağlam kopması DEĞİL, doğru davranıştı. Ölçüt değil SENARYO kusurluydu.
        "turlar": ["bu yıl bakiye", "__CHIP__", "aylara göre"],
        "olculen": (S5_BELIRSIZLIK, S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "kompozisyon",
        "aciklama": "İki ölçü tek raporda — MIMARI §9.2'nin iki adımlı çözümü (takip yolu).",
        "turlar": ["bu yıl makine bazında oee",
                   "bir de fire ekle",
                   "bunu analiz et"],
        "olculen": (S2_ANLAT, S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "sosyal_isten_ise",
        "aciklama": "Selam → iş → teşekkür. Sosyal turlar SIFIR maliyet olmalı.",
        "turlar": ["merhaba", "bu yıl makine bazında oee", "teşekkürler", "iyi çalışmalar"],
        "olculen": (S4_SOSYAL, S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "konu_degisimi",
        "aciklama": "Konu değişiyor, sonra ESKİ konuya dönülüyor — bağlam iki yönde de sağlam mı?",
        "turlar": ["bu yıl makine bazında oee", "peki bu yıl ciro?", "aylara göre",
                   "tamam yine oee'ye dönelim", "vardiya bazında"],
        "olculen": (S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "atif_ifadesi",
        "aciklama": "FAZ E: 'az önce dediğin gibi…' cevabı öldürmemeli (ölçülmüş kusur).",
        "turlar": ["bu yıl oee",
                   "az önce dediğin gibi makine bazında ayır",
                   "yukarıdaki raporu vardiya bazında ver"],
        "olculen": (S3_SUREKLILIK, S1_CAPA, S6_MAKBUZ),
    },
    {
        "ad": "geri_donus",
        "aciklama": "FAZ D4 checkpoint: üç tur sonra İLK karta dönüp oradan devam.",
        "turlar": ["bu yıl makine bazında oee",
                   "vardiya bazında",
                   "aylık göster",
                   ("__CUBE__", 0)],
        "olculen": (S7_GERI_DONUS, S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "eylem_onerisi",
        "aciklama": "FAZ H: 'her pazartesi yolla' SQL uydurmamalı, ÖNERİ üretmeli.",
        "turlar": ["bu yıl makine bazında oee",
                   "her pazartesi bu raporu bana yolla",
                   "bunu panoya ekle"],
        "olculen": (S1_CAPA, S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "liste_niyeti",
        "aciklama": "Toplam değil LİSTE isteniyor; sonra sıralama ve kırpma.",
        "turlar": ["bu yıl partileri listele", "en çok fire vereni üste al", "ilk 5'i göster"],
        "olculen": (S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "kapsam_disi",
        "aciklama": "Cevabı OLMAYAN soru: dürüst ret + NE YAPABİLDİĞİ (proaktif sınır).",
        "turlar": ["bu yıl personel bazında verimlilik", "peki makine bazında?"],
        "olculen": (S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "uretim_muduru_sabahi",
        "aciklama": "GERÇEK bir sabah rutini: selam → dünkü durum → en kötüsü → neden → "
                    "geçen haftayla kıyas → haftalık zamanla → teşekkür. Merdivenin HER "
                    "basamağı tek bir thread'de.",
        "turlar": ["günaydın",
                   "geçen haftada makine bazında oee",
                   "en düşük hangisi",
                   "bu neden böyle?",
                   "geçen yılla kıyasla",
                   "her pazartesi bu raporu bana yolla",
                   "teşekkürler"],
        "olculen": (S1_CAPA, S3_SUREKLILIK, S4_SOSYAL, S6_MAKBUZ),
    },
    {
        "ad": "yazim_hatali_gercek_kullanici",
        "aciklama": "Gerçek kullanıcı düzgün yazmaz: yazım hatası, eksik cümle, küçük "
                    "harf, konuşma dili. Sistem bunlara da dayanmalı.",
        "turlar": ["bu yil makina bazinda oee",
                   "aylik goster",
                   "en kotusu hangisi",
                   "bunu yorumla"],
        "olculen": (S2_ANLAT, S3_SUREKLILIK, S6_MAKBUZ),
    },
    {
        "ad": "kiyas_turu",
        "aciklama": "Geçen yılla kıyas → sürükleyeni bul → yorumla.",
        "turlar": ["bu yıl makine bazında oee", "geçen yılla kıyasla", "bunu analiz et"],
        "olculen": (S1_CAPA, S2_ANLAT, S3_SUREKLILIK, S6_MAKBUZ),
    },
)


def _olc(senaryo: dict, turlar: list[dict]) -> dict[str, bool | None]:
    """Sözleşme satırlarını ölçer. `None` = ⊘ ölçülemedi (ön koşul sağlanmadı)."""
    olcum: dict[str, bool | None] = {}
    ilgili = set(senaryo["olculen"])
    # ÖLÇÜM DIŞI turlar (ör. tıklanacak chip yokken `__CHIP__`) hiçbir satırda sayılmaz:
    # onlar bir cevap değil, bir önkoşul yokluğudur.
    turlar = [t for t in turlar if t["tur_tipi"] != "olcum_disi"]
    if not turlar:
        return {s: None for s in ilgili}

    def yaz(satir: str, deger: bool | None) -> None:
        if satir in ilgili:
            olcum[satir] = deger

    # 3 · SÜREKLİLİK — "ilişkilendiremedim" hiç görülmemeli.
    kopma = sum(1 for t in turlar if KOPMA_IZI in (t["cevap"].get("note") or "").lower())
    yaz(S3_SUREKLILIK, kopma == 0)

    # 6 · MAKBUZ — her cevap gerekçeli.
    yaz(S6_MAKBUZ, all(_makbuzlu(t["cevap"]) for t in turlar))

    # 1 · ÇAPA — "analiz et / yorumla / panoya ekle / yolla" turları YENİ SQL YAZMAZ.
    capa_turlari = [i for i, t in enumerate(turlar) if t["tur_tipi"] == "konusma"]
    if capa_turlari:
        tamam = True
        for i in capa_turlari:
            onceki = turlar[i - 1]["cevap"].get("cube_query") if i else None
            simdi = turlar[i]["cevap"].get("cube_query")
            if onceki and simdi != onceki:
                tamam = False
        yaz(S1_CAPA, tamam)
    else:
        yaz(S1_CAPA, None)

    # 2 · ANLAT — olgu + anlatı + ≥2 devam chip'i.
    #
    # ⚠ ÖLÇÜT ŞEKİLDEN TÜRETİLİR — ve buna ÜÇ ölçümden sonra varıldı (kayıt için):
    #
    #     "bu yıl makine bazında oee"             → 2  ['top','bottom']     (boyut, zaman yok)
    #     "son 6 ayda aylık toplam fire kg"       → 2  ['trend','peak']     (zaman, boyut yok)
    #     "bu yıl aylara göre makine bazında oee" → 3  ['trend','peak','shape']
    #
    # `interpret()` deterministiktir: `shape` bir BOYUT, `trend`/`peak` bir ZAMAN EKSENİ
    # ister. Yani üçüncü olgu ancak İKİSİ BİRDEN varken doğar. Sabit "≥3" şartı,
    # yapısal olarak üretilemeyeni şart koşuyordu ve önce düz kırılımı, sonra düz zaman
    # serisini haksız yere kırmızı gösterdi — ölçüt bu turda ÜÇ KEZ düzeltildi.
    #
    # Ders (MIMARI §6.4'ün genişletilmiş hâli): bir eşiği tahminle ayarlamak yerine
    # ÜRETEN MEKANİZMADAN türet. Aksi hâlde araç, ürünü değil kendi varsayımını ölçer.
    anlat = [t for t in turlar if t["tur_tipi"] == "anlat"]
    if anlat:
        d = anlat[-1]["cevap"]
        yorum = d.get("interpretation") or {}
        cq = d.get("cube_query") or {}
        alt_sinir = 3 if (cq.get("timeDimensions") and cq.get("dimensions")) else 2
        olgu = len(yorum.get("facts") or [])
        chip = len(d.get("suggestions") or []) + len(d.get("next_steps") or [])
        # `narration` YALNIZ `t2_anlatici` bayrağı açıkken dolar; kapalıysa deterministik
        # `summary` yerinde kalır ve bu KUSUR DEĞİL, beyan edilmiş bir yoldur.
        anlati_var = bool(yorum.get("narration") or yorum.get("summary"))
        if not yorum:
            # `cikti_yorumlama` bayrağı kapalı → satır ÖLÇÜLEMEZ. Kırmızı göstermek
            # sahte alarm, yeşil göstermek "risk yok" yalanı olurdu.
            yaz(S2_ANLAT, None)
        else:
            yaz(S2_ANLAT, olgu >= alt_sinir and anlati_var and chip >= 2)
    else:
        yaz(S2_ANLAT, None)

    # 4 · SOSYAL — 0 LLM · 0 SQL.
    sosyal = [t for t in turlar if t["tur_tipi"] == "sosyal"]
    if sosyal:
        yaz(S4_SOSYAL, all(not t["cevap"].get("sql") and not _llm_yolu(t["cevap"])
                           for t in sosyal))
    else:
        yaz(S4_SOSYAL, None)

    # 5 · BELİRSİZLİK — tahmin değil SORU; sonraki tur onayı taşır.
    if S5_BELIRSIZLIK in ilgili:
        ilk = turlar[0]["cevap"]
        sordu = bool(ilk.get("suggestions")) and not ilk.get("sql")
        tasidi = bool(turlar[1]["cevap"].get("cube_query")) if len(turlar) > 1 else False
        yaz(S5_BELIRSIZLIK, sordu and tasidi)

    # 7 · GERİ DÖNÜŞ — `POST /cube` 0 LLM ile aynı raporu verir.
    donus = [t for t in turlar if t["tur_tipi"] == "geri_donus"]
    if donus:
        d = donus[-1]["cevap"]
        yaz(S7_GERI_DONUS, bool(d.get("sql")) and not _llm_yolu(d)
            and d.get("cube_query") == donus[-1]["hedef_cq"])
    else:
        yaz(S7_GERI_DONUS, None)
    return olcum


def _tur_tipi(soru) -> str:
    if isinstance(soru, tuple):
        return "geri_donus"
    s = soru.lower()
    if any(k in s for k in ("analiz et", "yorumla", "özetle", "değerlendir")):
        return "anlat"
    if any(k in s for k in ("merhaba", "teşekkür", "iyi çalışmalar", "görüşürüz", "selam")):
        return "sosyal"
    if any(k in s for k in ("panoya", "yolla", "e-postala", "gönder")):
        return "konusma"
    if any(k in s for k in ("neden böyle", "ne yapmalıyız", "normal mi")):
        return "konusma"
    return "veri"


def kos(c, senaryo: dict, *, live: bool) -> dict:
    turlar: list[dict] = []
    cq = None
    kartlar: list[dict] = []          # geri dönüş için: her turun cube_query'si
    for i, soru in enumerate(senaryo["turlar"]):
        tip = _tur_tipi(soru)
        hedef_cq = None
        if tip == "geri_donus":
            hedef_cq = kartlar[soru[1]] if soru[1] < len(kartlar) else None
            if hedef_cq is None:
                turlar.append({"soru": f"__CUBE__[{soru[1]}]", "tur_tipi": tip,
                               "cevap": {}, "hedef_cq": None})
                continue
            rr = c.post("/cube", json={"cube_query": hedef_cq})
            gosterilen = f"↩ karta dön (#{soru[1] + 1})"
        elif soru == "__CHIP__":
            chips = turlar[-1]["cevap"].get("suggestions") if turlar else None
            if not chips:
                # ⚠ Tıklanacak chip YOKSA bu tur bir CEVAP DEĞİLDİR — ölçüm önkoşulu
                # sağlanmamıştır. İlk sürümde boş bir `{}` cevap gibi listeye giriyordu
                # ve MAKBUZ satırını (S6) haksız kırmızı yapıyordu: aynı kusur (chip
                # üretilmedi) İKİ satırda sayılıyordu. Chip'in üretilmemesi zaten
                # S5'in ölçtüğü şeydir; ikinci kez cezalandırmak sinyali bozar.
                turlar.append({"soru": "__CHIP__ (tıklanacak chip YOK)",
                               "tur_tipi": "olcum_disi", "cevap": {}, "hedef_cq": None})
                continue
            gosterilen = chips[0]["query"]
            rr = c.post("/ask", json={"question": gosterilen, "execute": True,
                                      **({"cube_query": cq, "history": [turlar[-1]["soru"]]}
                                         if cq else {})})
            tip = "veri"
        else:
            gosterilen = soru
            govde: dict = {"question": soru, "execute": True}
            if cq is not None and i:
                govde["cube_query"] = cq
                govde["history"] = [t["soru"] for t in turlar[-2:]]
            rr = c.post("/ask", json=govde)
        d = rr.json() if rr.status_code == 200 else {"_http": rr.status_code}
        turlar.append({"soru": gosterilen, "tur_tipi": tip, "cevap": d,
                       "hedef_cq": hedef_cq})
        if d.get("cube_query"):
            cq = d["cube_query"]
            kartlar.append(d["cube_query"])
        if live:
            time.sleep(LIVE_BEKLE)      # ölçülen sınır: 10 istek / 10 sn
    return {"ad": senaryo["ad"], "aciklama": senaryo["aciklama"], "turlar": turlar,
            "olcum": _olc(senaryo, turlar)}


def _isaret(v: bool | None) -> str:
    return "✅" if v is True else ("❌" if v is False else "⊘")


def _rapor_yaz(sonuc: dict, live: bool) -> None:
    RAPOR_DIZINI.mkdir(parents=True, exist_ok=True)
    s = [f"# Deneyim senaryosu — {sonuc['ad']}", "",
         f"> {sonuc['aciklama']}", "",
         f"**Mod:** {'CANLI (gerçek sağlayıcı)' if live else 'yapısal duman — KAPI DEĞİL'}",
         "", "## Sözleşme", "", "| satır | sonuç |", "|---|---|"]
    for satir, v in sorted(sonuc["olcum"].items()):
        s.append(f"| {satir} | {_isaret(v)} |")
    s += ["", "⊘ = bu senaryo o satırı ölçmez (ön koşul yok). Yeşile yuvarlamak "
          "*'risk yok'* yalanı üretirdi.", "", "## Turlar", ""]
    for i, t in enumerate(sonuc["turlar"], 1):
        d = t["cevap"]
        s += [f"### {i}. `{t['soru']}`  ·  _{t['tur_tipi']}_", "",
              f"- **kaynak:** `{d.get('source')}`  ·  **sql:** "
              f"{'var' if d.get('sql') else 'yok'}  ·  **satır:** "
              f"{(d.get('result') or {}).get('row_count')}",
              f"- **cube_query:** `{json.dumps(d.get('cube_query'), ensure_ascii=False)}`"]
        if d.get("note"):
            s.append(f"- **not:** {d['note']}")
        yorum = d.get("interpretation") or {}
        if yorum.get("summary") or yorum.get("narration"):
            s.append(f"- **anlatı:** {yorum.get('narration') or yorum.get('summary')}")
        if yorum:
            _tipler = [f.get("type") for f in (yorum.get("facts") or [])]
            s.append(f"- **olgu:** {len(_tipler)} {_tipler}  ·  **chip:** "
                     f"{len(d.get('suggestions') or [])}+{len(d.get('next_steps') or [])}")
        if d.get("eylem_onerisi"):
            s.append(f"- **eylem önerisi:** {d['eylem_onerisi'].get('ozet')}")
        chips = [x.get("label") or x.get("query") for x in (d.get("suggestions") or [])]
        if chips:
            s.append(f"- **chip:** {', '.join(map(str, chips[:5]))}")
        s.append("")
    (RAPOR_DIZINI / f"{sonuc['ad']}.md").write_text("\n".join(s), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Faz X — deneyim süiti (thread bazlı)")
    ap.add_argument("--live", action="store_true",
                    help="GERÇEK sağlayıcı, sıralı ve hız-sınırlı (asıl ölçüm)")
    ap.add_argument("--senaryo", help="yalnız bu senaryoyu koş")
    ap.add_argument("--bayrak", help="bir özellik bayrağını AÇIK zorla (ör. "
                                     "netlestirme_onceligi) — YAML'a DOKUNMAZ")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    from fastapi.testclient import TestClient

    import app.wren_service as ws
    from app.main import create_app
    from tests.conftest import make_tenant_user

    if args.live:
        sag = _canli_ortami_geri_yukle()
        print(f"CANLI MOD — sağlayıcı: {sag} · tur arası {LIVE_BEKLE}s", flush=True)
    else:
        # Yapısal duman: LLM yok, ağ yok. **KAPI DEĞİL** ve bu her yerde yazılır —
        # LLM'in olmadığı bir koşumda "anlatı" satırı hiçbir şey söylemez.
        ws.WrenService._enrich_categorical = lambda self, *a, **k: None
        ws.WrenService._enrich_cube_dim_values = lambda self, *a, **k: None
        print("YAPISAL DUMAN — LLM YOK. Bu bir KAPI DEĞİL: anlatı/Intent yolları "
              "ölçülemez. Asıl ölçüm: --live", flush=True)

    make_tenant_user("owner@dima.local", "owner-parola-123", tenant_slug=None)
    c = TestClient(create_app())
    c.__enter__()
    r = c.post("/auth/login", json={"email": "owner@dima.local",
                                    "password": "owner-parola-123"})
    assert r.status_code == 200, r.text
    c.headers["Authorization"] = f"Bearer {r.json()['access_token']}"

    # Bayrak zorlaması `lab/nl_accuracy._BayrakZorla`'dan ÇAĞRILIR (kopya değil): ölçüm,
    # ölçtüğü sistemin YAPILANDIRMASINI kalıcı değiştirmemelidir.
    from contextlib import nullcontext

    from lab.nl_accuracy import _BayrakZorla

    bayrak_ctx = _BayrakZorla(args.bayrak, True) if args.bayrak else nullcontext()

    secili = [s for s in SENARYOLAR if not args.senaryo or s["ad"] == args.senaryo]
    if not secili:
        print(f"Senaryo bulunamadı: {args.senaryo!r}")
        return 2
    sonuclar = []
    with bayrak_ctx:
        if args.bayrak:
            print(f"BAYRAK ZORLANDI: {args.bayrak}=AÇIK (YAML değişmedi)", flush=True)
        for s in secili:
            print(f"▶ {s['ad']} ({len(s['turlar'])} tur)", flush=True)
            sonuc = kos(c, s, live=args.live)
            _rapor_yaz(sonuc, args.live)
            sonuclar.append(sonuc)
    c.__exit__(None, None, None)

    if args.json:
        print(json.dumps([{"ad": s["ad"], "olcum": s["olcum"]} for s in sonuclar],
                         ensure_ascii=False, indent=2))
        return 0

    satirlar = [S1_CAPA, S2_ANLAT, S3_SUREKLILIK, S4_SOSYAL, S5_BELIRSIZLIK,
                S6_MAKBUZ, S7_GERI_DONUS]
    print("\n" + "=" * 96)
    print(f"FAZ X — DENEYİM SÜİTİ  ·  mod={'CANLI' if args.live else 'yapısal duman'}")
    print("=" * 96)
    print(f"{'senaryo':<22}" + "".join(f"{s.split('·')[0]:>4}" for s in satirlar))
    kirmizi = 0
    for s in sonuclar:
        hucre = "".join(f"{_isaret(s['olcum'].get(x)):>4}" for x in satirlar)
        kirmizi += sum(1 for x in satirlar if s["olcum"].get(x) is False)
        print(f"  {s['ad']:<20}{hucre}")
    olculemedi = sum(1 for s in sonuclar for x in satirlar if s["olcum"].get(x) is None)
    print(f"\n✅ geçen: {sum(1 for s in sonuclar for x in satirlar if s['olcum'].get(x) is True)}"
          f"   ❌ kalan: {kirmizi}   ⊘ ölçülemedi: {olculemedi}")
    print(f"Raporlar: {RAPOR_DIZINI}")
    if not args.live:
        print("⚠ Bu koşum bir KAPI DEĞİLDİR (LLM yok). Sözleşmenin anlatı/Intent "
              "satırları yalnız --live ile ölçülür.")
    return 1 if kirmizi else 0


if __name__ == "__main__":
    raise SystemExit(main())
