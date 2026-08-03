"""VK-1…VK-6 · TABAN ÖLÇÜMÜ — yol haritası §G.6e'nin *"Bugün"* sütunu, ÖLÇÜLEREK.

    python lab/vk_taban.py           # yapısal (LLM yok) — ücretsiz, hızlı
    python lab/vk_taban.py --live    # GERÇEK sağlayıcı — asıl ölçüm
    python lab/vk_taban.py --json

## Neden bu araç var — ve neden BELGE ONARIMINDAN ÖNCE koşulur

`DIMA-V1-YOL-HARITASI.md` §G.6e altı **adı konmuş kabul vakası** tanımlıyor ve her birine
bir *"Bugün"* hükmü yazıyor (*"🔴 «degisti» yerine «egitim» mi demek istedin?"* gibi).
O hükümler **bir denetim turunda elle** üretilmiş. Bu araç onları **yeniden üretilebilir**
kılar.

Sıra bağlayıcıdır ve yol haritasının kendi `KAT-4`'ünden gelir:

> **Belge onarımından SONRA koşulursa, *"düzeldi mi"* sorusunun kıyaslayacağı bir ÖNCESİ
> olmaz.** Taban, düzeltmeden önce alınır — sonra alınan taban taban değildir.

## Ne ölçer, ne ÖLÇMEZ

**Ölçer:** her turun `source`'u · SQL üretti mi · `cube_query` · `note` · **red gerekçesi**
(`cube_router.red_gerekcesi()` ContextVar'ı) · chip sayısı · gövde alanlarının (
`contribution`/`prescription`/`next_steps`) DOLULUĞU.

**ÖLÇMEZ — ve bu bilinçli:** *"geçti/kaldı"*. Taban ölçümünde beklenen değer **yoktur**;
beklenti §G.6e'nin kayıt biçimiyle (`beklenen SINIF · beklenen source · yasak davranışlar`)
maddeler indikçe yazılır. Bugün bir ✅/❌ basmak, henüz yazılmamış bir sözleşmeye karşı
hüküm vermek olurdu.

⚠ **Gövde alanı DOLULUĞU ≠ GÖRÜNÜRLÜK.** VK-3'ün ölçtüğü şey render'dır; bu araç API
cevabına bakar. `lab/deneyim.py`'nin `S2` kör noktasıyla **aynı sınıf** — ve yol haritası
bunu `S8` satırıyla kapatmayı planlıyor. Rapor bunu her koşumda yazar.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Tek sahip: canlı ortam geri yükleme + ayar önbelleği temizliği + canlılık DOĞRULAMASI.
from lab.konusma_senaryolari import LIVE_BEKLE, _canli_ortami_geri_yukle  # noqa: E402

RAPOR = Path(__file__).resolve().parent / "reports" / "vk_taban.md"

#: Tur tipleri: "ask" = normal soru · "chip" = önceki cevabın ilk chip'ine TIKLA
#: · "yazi" = önceki netleştirmeye ELLE yazarak cevap ver (VK-2'nin ikinci yolu)
VAKALAR: tuple[dict, ...] = (
    {
        "id": "VK-1",
        "olctugu": "kısa devre yok + adlı dönem kıyası",
        "madde": "AJ0 · AJ2",
        "belge_bugun": "🔴 «degisti» yerine «egitim» mi demek istedin?",
        "turlar": [("ask", "mart ayında ciro şubat ayına göre nasıl değişti")],
    },
    {
        "id": "VK-2",
        "olctugu": "kapanan söz alışverişi — chip YOLU ile YAZI YOLU aynı rapora çıkmalı",
        "madde": "0.5b · AJ0b",
        "belge_bugun": "🔴 yazınca KURAL_TAZE — yeni soru sanılıyor",
        # İki yol AYRI thread gibi koşar: önce sor → chip'e tıkla; sonra tekrar sor → yaz.
        "turlar": [("ask", "fire"), ("chip", None),
                   ("ask", "fire"), ("yazi", "fire oranı")],
    },
    {
        "id": "VK-3",
        "olctugu": "görünürlük — gövde alanları render dalına düşüyor mu",
        "madde": "0.23",
        "belge_bugun": "🔴 hesaplanıyor, ekranda yok",
        "turlar": [("ask", "bu yıl makine bazında oee"), ("ask", "bu neden böyle?")],
    },
    {
        "id": "VK-4",
        "olctugu": "onarım — slot düzeltilir, baştan başlamaz",
        "madde": "AJ0b",
        "belge_bugun": "🔴 baştan başlıyor",
        "turlar": [("ask", "ocak ayında fire"), ("ask", "hayır, şubat demiştim")],
    },
    {
        "id": "VK-5",
        "olctugu": "KUZEY YILDIZI — ayrıştırma + adım zinciri + dil + rapor",
        "madde": "AJ5 · AJ5b · AJ2 · AJ6",
        "belge_bugun": "🔴 R1/R10 ile ölüyor · `verimlilik` katalogda YOK",
        "turlar": [("ask", "son 6 aylık ciro ve her bir satış üreten ürün kalemiyle "
                           "mukayesesi ve bunların verimliliği ve karlılıklarını analiz "
                           "ettiğin bir rapor yaz")],
    },
    {
        "id": "VK-6",
        "olctugu": "eşzamanlılık — netleştirme terminal mi",
        "madde": "AJ3b",
        "belge_bugun": "🔴 netleştirme terminal — imkânsız",
        "turlar": [("ask", "son 6 aylık ciro raporu hazırla"),
                   ("ask", "şu kısmı anlamadım, ürün kalemi ne demek"),
                   ("ask", "tamam, stok adı olarak al")],
    },
)


def _red_gerekcesi(soru: str, schema: dict) -> str | None:
    """`route()`'un red kodu (R1…R10) — ContextVar'dan okunur.

    VK-5 için KRİTİK: yol haritası *"kırmızının SEBEBİ raporlanır — «ifade edilemedi
    (R11)» mi, «katalogda yok» mu? İkisi FARKLI iştir"* diyor. Red kodu bu ayrımın
    ölçülebilir yarısıdır.
    """
    from app import cube_router

    try:
        cube_router.route(cube_router._norm(soru), schema)
        return cube_router.red_gerekcesi()
    except Exception:
        return None


def _ozet(d: dict) -> dict:
    cq = d.get("cube_query") or {}
    yorum = d.get("interpretation") or {}
    return {
        "source": d.get("source"),
        "sql": bool(d.get("sql")),
        "satir": (d.get("result") or {}).get("row_count"),
        "cube": cq.get("cube"),
        "measures": cq.get("measures"),
        "dimensions": cq.get("dimensions"),
        "compare": cq.get("compare"),
        "note": d.get("note"),
        "chip": len(d.get("suggestions") or []),
        "next_steps": len(d.get("next_steps") or []),
        # ⚠ DOLULUK, görünürlük DEĞİL (bkz. modül docstring'i).
        "contribution_dolu": bool(d.get("contribution")),
        "prescription_dolu": bool(d.get("prescription")),
        "olgu": len(yorum.get("facts") or []),
        "trace": d.get("trace") or [],
    }


def kos(c, vaka: dict, schema: dict, *, live: bool) -> dict:
    turlar: list[dict] = []
    cq = None
    for tip, metin in vaka["turlar"]:
        if tip == "chip":
            chips = turlar[-1]["cevap"].get("suggestions") if turlar else None
            if not chips:
                turlar.append({"tip": tip, "soru": "(tıklanacak chip YOK)",
                               "cevap": {}, "olcum": None})
                continue
            gosterilen = chips[0]["query"]
            govde = {"question": gosterilen, "execute": True}
            if cq:
                govde["cube_query"] = cq
        elif tip == "yazi":
            gosterilen = metin
            govde = {"question": metin, "execute": True}
            # YAZI YOLU: istemci bağlamı taşır (frontend böyle yapıyor) — chip yolundan
            # tek farkı, metnin kullanıcı tarafından YAZILMASI olmalı.
            if cq:
                govde["cube_query"] = cq
                govde["history"] = [turlar[-1]["soru"]] if turlar else []
        else:
            gosterilen = metin
            govde = {"question": metin, "execute": True}
            if cq and turlar:
                govde["cube_query"] = cq
                govde["history"] = [t["soru"] for t in turlar[-2:]]
        r = c.post("/ask", json=govde)
        d = r.json() if r.status_code == 200 else {"_http": r.status_code}
        turlar.append({"tip": tip, "soru": gosterilen, "cevap": d, "olcum": _ozet(d),
                       "red": _red_gerekcesi(gosterilen, schema)})
        if d.get("cube_query"):
            cq = d["cube_query"]
        if live:
            time.sleep(LIVE_BEKLE)
    return {**{k: v for k, v in vaka.items() if k != "turlar"}, "turlar": turlar}


def _rapor_yaz(sonuclar: list[dict], live: bool, saglayici: str) -> None:
    RAPOR.parent.mkdir(parents=True, exist_ok=True)
    s = ["# VK-1…VK-6 · TABAN ÖLÇÜMÜ", "",
         f"**Mod:** {'CANLI — ' + saglayici if live else 'yapısal (LLM YOK)'}", "",
         "> Bu bir **taban**tır: geçti/kaldı **basmaz**. Beklenen değer §G.6e'nin kayıt",
         "> biçimiyle maddeler indikçe yazılacak; bugün hüküm vermek, henüz yazılmamış",
         "> bir sözleşmeye karşı hüküm vermek olurdu.",
         "",
         "> ⚠ **Gövde alanı DOLULUĞU ≠ GÖRÜNÜRLÜK.** Bu araç API cevabına bakar;",
         "> VK-3'ün ölçtüğü şey render'dır (`lab/deneyim.py::S2` ile aynı kör nokta).",
         ""]
    for r in sonuclar:
        s += [f"## {r['id']} — {r['olctugu']}", "",
              f"- **madde:** {r['madde']}",
              f"- **belgenin «Bugün» hükmü:** {r['belge_bugun']}", ""]
        for i, t in enumerate(r["turlar"], 1):
            o = t["olcum"] or {}
            s += [f"### {i}. `{t['soru']}`  ·  _{t['tip']}_", "",
                  f"- **source:** `{o.get('source')}` · **sql:** {o.get('sql')} · "
                  f"**satır:** {o.get('satir')} · **red kodu:** `{t.get('red')}`",
                  f"- **cube_query:** cube=`{o.get('cube')}` ölçü=`{o.get('measures')}` "
                  f"boyut=`{o.get('dimensions')}` compare=`{o.get('compare')}`",
                  f"- **chip:** {o.get('chip')} · **next_steps:** {o.get('next_steps')} · "
                  f"**olgu:** {o.get('olgu')} · **contribution:** "
                  f"{o.get('contribution_dolu')} · **prescription:** "
                  f"{o.get('prescription_dolu')}"]
            if o.get("note"):
                s.append(f"- **not:** {o['note']}")
            for iz in (o.get("trace") or [])[:6]:
                s.append(f"  - iz: {iz}")
            s.append("")
    RAPOR.write_text("\n".join(s), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="VK-1…VK-6 taban ölçümü")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    from fastapi.testclient import TestClient

    import app.wren_service as ws
    from app.main import create_app
    from tests.conftest import make_tenant_user

    saglayici = "rule (yapısal)"
    if a.live:
        saglayici = _canli_ortami_geri_yukle()
        print(f"CANLI MOD — sağlayıcı: {saglayici} · tur arası {LIVE_BEKLE}s", flush=True)
    else:
        ws.WrenService._enrich_categorical = lambda self, *x, **k: None
        ws.WrenService._enrich_cube_dim_values = lambda self, *x, **k: None
        print("YAPISAL MOD — LLM YOK. Intent/Discovery yolları ölçülemez; asıl ölçüm: --live",
              flush=True)

    make_tenant_user("owner@dima.local", "owner-parola-123", tenant_slug=None)
    c = TestClient(create_app())
    c.__enter__()
    tok = c.post("/auth/login", json={"email": "owner@dima.local",
                                      "password": "owner-parola-123"})
    assert tok.status_code == 200, tok.text
    c.headers["Authorization"] = f"Bearer {tok.json()['access_token']}"
    schema = c.get("/schema").json()

    sonuclar = []
    for v in VAKALAR:
        print(f"▶ {v['id']} ({len(v['turlar'])} tur)", flush=True)
        sonuclar.append(kos(c, v, schema, live=a.live))
    c.__exit__(None, None, None)
    _rapor_yaz(sonuclar, a.live, saglayici)

    if a.json:
        print(json.dumps([{"id": r["id"],
                           "turlar": [{"soru": t["soru"], **(t["olcum"] or {})}
                                      for t in r["turlar"]]}
                          for r in sonuclar], ensure_ascii=False, indent=2))
        return 0

    print("\n" + "=" * 100)
    print(f"VK TABAN  ·  mod={'CANLI' if a.live else 'yapısal'}")
    print("=" * 100)
    print(f"{'vaka':<7}{'tur':<5}{'source':<12}{'sql':<5}{'red':<6}{'chip':<6}{'gövde':<7}soru")
    for r in sonuclar:
        for i, t in enumerate(r["turlar"], 1):
            o = t["olcum"] or {}
            govde = "+".join(x for x, v in (("c", o.get("contribution_dolu")),
                                            ("p", o.get("prescription_dolu")),
                                            ("n", bool(o.get("next_steps")))) if v) or "-"
            print(f"  {r['id']:<5}{i:<5}{str(o.get('source')):<12}"
                  f"{'var' if o.get('sql') else 'yok':<5}{str(t.get('red') or '-'):<6}"
                  f"{o.get('chip', 0):<6}{govde:<7}{t['soru'][:42]}")
    print(f"\nRapor: {RAPOR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
