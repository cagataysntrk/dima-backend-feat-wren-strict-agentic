"""FAZ 2a — ETİKET ÇAKIŞMASI TUZAĞI: belirsizlik görülüyor ama chip SESSİZCE atlanıyordu.

## Ölçülen kusur zinciri (2026-08-02) — üç adımı da sessiz

1. `measure_cube_candidates` belirsizliği **doğru tespit ediyor** (`bakiye` → `cari` +
   `mizan`).
2. Chip'ler yalnız ölçünün **görünen adıyla** kuruluyordu. İki cube aynı adı taşıdığında
   (*"bakiye"* / *"bakiye"*) liste tekilleşip **1'e düşüyor**.
3. `if len(...) >= 2` kapısı chip'i **sessizce atlıyor** → soru **Discovery'ye** düşüyor →
   ham SQL, `cube_query=None`.

Yani netleştirme yolunun kendisi, planın §1'de tarif ettiği **uçuruma** açılıyordu:
kullanıcı bir soru yerine yapısız bir cevap alıyordu ve kimse bunu göremiyordu.

**Ölçüldü: 54 belirsiz sinonimin 33'ü (%61) bu tuzaktaydı** — `bakiye · borç · alacak ·
fire · ilk seferde tamam · doğalgaz` aileleri.

## Kural

Ayırt edici bilgi **ölçü adı değil CUBE'un kendisi**: *"bakiye (cari hesap)"* /
*"bakiye (mizan)"*. Çakışmayan etiket dokunulmadan kalır — gereksiz gürültü üretilmez.

## İkinci kusur: chip'in SORGUSU çalışmıyordu

İlk düzeltmem `query = f"{cube_display} {etiket}"` üretti ve **39 chip çözülmüyordu**:
`display` bir insan etiketidir (`mizan`'ınki *"mizan (hesap bakiyeleri)"*), sorgu kelimesi
değil. Cube **sinonimleri** ise tanım gereği `_match_cube`'un tanıdığı kelimelerdir.
Artık sorgu `route()` ile **doğrulanıyor** — tıklanınca çalışmayan bir chip, kullanıcıyı
aynı duvara ikinci kez çarptırır ve chip olmamasından kötüdür.

Ölçülen sonuç: **sessiz 33 → 0**, **kırık sorgu 39 → 0**.
"""

from __future__ import annotations

import pytest

from app import cube_router as cr


def _belirsizler(schema) -> list[tuple[str, dict]]:
    """`route()` R1 veren ve ≥2 aday cube'u olan benzersiz ölçü sinonimleri."""
    out, gorulen = [], set()
    for c in schema.get("cubes") or []:
        for syns in (c.get("measure_synonyms") or {}).values():
            for sy in syns:
                q = f"bu yil {sy}"
                if cr.route(q, schema) is not None or cr.red_gerekcesi() != "R1":
                    continue
                syn = cr._norm(str(sy))
                if syn in gorulen:
                    continue
                gorulen.add(syn)
                cands = cr.measure_cube_candidates(cr._norm(q), schema)
                dc = {x["name"]: (x, m) for x, m in cands}
                if len(dc) >= 2:
                    out.append((syn, dc))
    return out


# --- ASIL KAPI: hiçbir belirsizlik SESSİZ kalmıyor -------------------------------

def test_HICBIR_belirsizlik_SESSIZ_kalmiyor(schema):
    """Ölçüldü: 54 belirsiz sinonimin 33'ü chip üretemiyordu (etiketler tekilleşiyordu)
    ve soru Discovery'ye düşüyordu. Bu testin kilitlediği şey **sıfır sessizlik**."""
    sessiz = [syn for syn, dc in _belirsizler(schema)
              if len(cr.olcu_netlestirme(list(dc.values()), schema)) < 2]
    assert not sessiz, (
        f"{len(sessiz)} belirsiz sinonim chip üretmiyor → Discovery'ye düşüyor:\n  "
        + ", ".join(sorted(sessiz)[:15]))


def test_HER_CHIP_SORGUSU_gercekten_cozuluyor(schema):
    """En sert kapı. Tıklanınca çalışmayan bir chip, kullanıcıyı aynı duvara ikinci kez
    çarptırır — chip olmamasından KÖTÜDÜR. İlk düzeltmemde `display` kullanınca 39 chip
    kırıktı (`"mizan (hesap bakiyeleri) borç"` gibi sorgular); sorgu artık `route()` ile
    doğrulanıyor."""
    kirik = []
    for syn, dc in _belirsizler(schema):
        for o in cr.olcu_netlestirme(list(dc.values()), schema):
            if cr.route(f"bu yil {o['query']}", schema) is None:
                kirik.append(f"{syn}: {o['label']!r} → {o['query']!r}")
    assert not kirik, ("çözülmeyen chip sorgusu:\n  " + "\n  ".join(kirik[:15]))


# --- ETİKET: yalnız çakışmada nitelenir ------------------------------------------

def test_CAKISAN_etiket_CUBE_ile_nitelenir(schema):
    """`bakiye` iki cube'da da aynı adla görünüyor — ayırt edici bilgi cube."""
    dc = dict(_belirsizler(schema))
    assert "bakiye" in dc, "vaka bayat: `bakiye` artık belirsiz değil"
    etiketler = [o["label"] for o in cr.olcu_netlestirme(list(dc["bakiye"].values()), schema)]
    assert len(etiketler) == len(set(etiketler)), f"etiketler hâlâ çakışıyor: {etiketler}"
    assert all("(" in e for e in etiketler), f"cube ile nitelenmemiş: {etiketler}"


def test_CAKISMAYAN_etikete_GURULTU_eklenmez(schema):
    """`adet` sorusunda ölçü adları zaten farklı (arıza sayısı · parti sayısı …) —
    hepsine cube adı eklemek gereksiz gürültü olurdu."""
    dc = dict(_belirsizler(schema))
    if "adet" not in dc:
        pytest.skip("bu katalogda `adet` belirsizliği yok")
    etiketler = [o["label"] for o in cr.olcu_netlestirme(list(dc["adet"].values()), schema)]
    assert any("(" not in e for e in etiketler), (
        f"çakışmayan etiketler de nitelenmiş (gürültü): {etiketler}")


def test_ETIKETLER_TEKIL(schema):
    """Aynı etiketten iki chip, kullanıcıya seçim değil bulmaca sunar."""
    for syn, dc in _belirsizler(schema):
        et = [o["label"] for o in cr.olcu_netlestirme(list(dc.values()), schema)]
        assert len(et) == len(set(et)), f"{syn}: yinelenen etiket {et}"


# --- SORGU ÜRETİMİ: display değil SİNONİM ----------------------------------------

def test_SORGU_display_yerine_SINONIM_kullanir():
    """`display` bir İNSAN ETİKETİDİR. `mizan`'ınki *"mizan (hesap bakiyeleri)"* ve ondan
    üretilen sorgu anlamsızdı. Cube sinonimleri ise `_match_cube`'un TANIDIĞI kelimelerdir."""
    import inspect

    govde = inspect.getsource(cr._calisan_sorgu)
    assert 'cube.get("synonyms")' in govde, "sinonimler kullanılmıyor"
    assert "route(" in govde, "sorgu doğrulanmıyor"


def test_CIPLAK_etiket_CALISIYORSA_dokunulmaz(schema):
    """En kısa, en doğal ifade tercih edilir — gereksiz nitelemek chip'i uzatır."""
    sahte = [
        ({"name": "parti", "display": "parti", "synonyms": ["parti"],
          "measure_synonyms_display": {"toplam_ciro": "ciro"}}, "toplam_ciro"),
    ]
    sec = cr.olcu_netlestirme(sahte, schema)
    assert sec and sec[0]["query"] in ("ciro", "parti ciro")


def test_SEMA_YOKSA_patlamaz():
    """`schema=None` (birim test/çağrı kolaylığı) doğrulamayı atlar, çökmez."""
    sahte = [({"name": "a", "display": "A", "synonyms": ["a"],
               "measure_synonyms_display": {"m": "x"}}, "m"),
             ({"name": "b", "display": "B", "synonyms": ["b"],
               "measure_synonyms_display": {"m": "x"}}, "m")]
    sec = cr.olcu_netlestirme(sahte)
    assert len(sec) == 2 and all(o["query"] for o in sec)


# --- ENTEGRASYON: /ask gerçekten chip döndürüyor mu? -----------------------------

@pytest.mark.parametrize("soru", ["bu yıl bakiye", "bu yıl alacak", "bu yıl borç"])
def test_ASK_ZINCIRI_chip_donduruyor(client, soru):
    """Uçtan uca. Bu üç soru daha önce **sessizce Discovery'ye** düşüyordu
    (`source=rule`, `cube_query=None`, not YOK, chip YOK)."""
    d = client.post("/ask", json={"question": soru, "session_id": "t"}).json()
    chips = [s["label"] for s in (d.get("suggestions") or [])]
    assert len(chips) >= 2, f"{soru!r} hâlâ chip üretmiyor: source={d.get('source')}"
    assert len(chips) == len(set(chips)), f"yinelenen chip: {chips}"
    assert d.get("note"), "netleştirme notu yok — kullanıcı neden chip geldiğini anlamaz"


def test_ASK_chip_TIKLANINCA_calisiyor(client):
    """Chip'in `query`'si yeni bir soru olarak koşar. Uçtan uca doğrulama."""
    d = client.post("/ask", json={"question": "bu yıl bakiye", "session_id": "t"}).json()
    for s in (d.get("suggestions") or [])[:2]:
        r = client.post("/ask", json={"question": s["query"], "session_id": "t"}).json()
        assert r.get("cube_query"), (
            f"chip {s['label']!r} → query {s['query']!r} yapısal cevap üretmedi "
            f"(source={r.get('source')})")
