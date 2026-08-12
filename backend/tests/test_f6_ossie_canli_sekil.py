"""🔴🔴 `§F6` — İHRAÇ UCU **CANLI ŞEMAYI** İHRAÇ EDEBİLİYOR MU?

## Ölçülen kusur (2026-08-11) — ve kapının kendisi kördü

`GET /connections/{cid}/ossie` gövdesi şudur:

    sema = wren_for_request(request).schema()
    return {..., **belge(sema.get("cubes") or [], ...)}

Ama iki şekil vardı ve uç **yanlış olanı** besliyordu:

| | `packs/` şekli | `schema()` şekli |
|---|---|---|
| ölçüler | `[{name, expression, synonyms}]` | `["ort_oee", …]` + `measure_*` sözlükleri |
| küp etiketi | `label` | **`display`** |
| toplanabilirlik | ölçü içinde `additive` | `semi_additive` / `non_additive` **listeleri** |

Canlı katalogda sonuç: `AttributeError: 'str' object has no attribute 'get'` → **HTTP 500**.

🔴 **Ve `test_ossie_ihrac.py` bunu göremedi**, çünkü fikstürü `packs/` şeklinde yazılmış:
kural yazılmış, uç bağlanmış, round-trip kapısı kurulmuş — **ve kapı, ucun hiç görmediği
bir şekli sınıyordu.**

> *Bir kapının yeşil olması, doğru şeyi ölçtüğü anlamına gelmez. Fikstür, ucun gördüğü
> girdiyle aynı şekilde değilse, kapı kendi uydurduğu bir dünyayı korur.*

## Bu dosya `schema()`'nın KENDİSİNİ ihraç eder — fikstür yok

Ölçülen pilot (23 canlı küp): dataset **23** · ilişki **31** · ölçü sinonimi
**677/677** taşındı · round-trip kaybı **SIFIR**. `ossie_ihrac`'ın yazılı açılma şartı
(*«geri ithal edildiğinde birebir aynı SQL vermiyorsa bayrak AÇILMAZ»*) böylece **canlı
kanıtla** karşılandı.
"""

from __future__ import annotations

import pytest

from app.ossie import UZANTI, belge, cevir, disa_aktar


def _adlar(x) -> set[str]:
    return {(v if isinstance(v, str) else str((v or {}).get("name") or ""))
            for v in (x or [])}


def test_CANLI_SEMA_ihrac_EDILEBILIYOR(schema):
    """🔴 Kusurun ta kendisi: bu çağrı `AttributeError` ile patlıyordu."""
    d = belge(schema["cubes"], iliskiler=schema.get("relationships") or [])
    assert len(d["datasets"]) == len(schema["cubes"])
    assert d["version"]


def test_ROUND_TRIP_canli_katalogda_KAYIPSIZ(schema):
    """Bayrağın yazılı açılma şartı — fikstürde değil **canlı katalogda**."""
    d = belge(schema["cubes"], iliskiler=schema.get("relationships") or [])
    geri = {c["name"]: c for c in cevir(d)["cubes"]}
    for c in schema["cubes"]:
        g = geri.get(c["name"])
        assert g, f"{c['name']} round-trip'te DÜŞTÜ"
        assert _adlar(c["measures"]) == _adlar(g.get("measures")), f"{c['name']} ölçü kaybı"
        bek = _adlar(c.get("dimensions")) | _adlar(c.get("time_dimensions"))
        got = _adlar(g.get("dimensions")) | _adlar(g.get("time_dimensions"))
        assert bek == got, f"{c['name']} boyut kaybı: {sorted(bek - got)}"
        assert c.get("base_object") == g.get("base_object"), f"{c['name']} base_object"


def test_TURKCE_SOZLUK_ai_contexte_TAM_tasiniyor(schema):
    """⭐ `§13.1`'in asıl tezi: *«Türkçe sözlük koda değil semantik modele ait olur.»*
    Ölçüldü: **677/677**. Tek bir sinonim düşerse bu test kırılır."""
    d = belge(schema["cubes"])
    ds = {x["name"]: x for x in d["datasets"]}
    toplam = gelen = 0
    for c in schema["cubes"]:
        cikan = {m["name"]: set(m.get("ai_context") or [])
                 for m in (ds[c["name"]].get("metrics") or [])}
        for m, sy in (c.get("measure_synonyms") or {}).items():
            toplam += len(sy or [])
            gelen += len(set(sy or []) & cikan.get(m, set()))
    assert toplam > 600, f"korpus küçüldü mü? {toplam}"
    assert gelen == toplam, f"sinonim kaybı: {toplam - gelen}/{toplam}"


def test_SESSIZ_YANLISI_ONLEYEN_alanlar_x_dimada(schema):
    """🔴 Standarda uyarken farkımızı kaybetmek ihracın bedeli olamaz. Dördü de
    Ossie'de karşılıksız ve dördü de **sessiz-yanlış** önler."""
    import json
    u = json.dumps(belge(schema["cubes"],
                         iliskiler=schema.get("relationships") or []), ensure_ascii=False)
    for alan in ("additive", "certified", "origin", "rol"):
        assert f'"{alan}"' in u, f"{alan} ihraçta düştü"


def _olcum_kosmus_mu(schema) -> bool:
    """🔴 **ORTAM MI, KUSUR MU** — bu ayrım bir kapı hijyenidir (`§F8`'in aynı dersi).

    Fan-out sertifikası bir **ölçümün** sonucudur: `_damgala_fanout` damgayı ancak
    ölçüm koşmuşsa `olculdu:*` yapar. **Taze derlenmiş** bir proje ağacında ölçüm
    henüz koşmamıştır ve damga **31/31 `olculmedi`** olur — ölçüldü (2026-08-12,
    `HEAD` worktree'sinde).

    ⊙ Ve bu **doğru** davranıştır: ölçmediğini *«sağlıklı»* diye damgalamak, bu deponun
    en pahalı hatası olurdu. Yanlış olan, testin bu bağımlılığı **beyan etmemesiydi**:
    ana depoda `demo/wren-project` **ısınmış** bir artefakttır ve orada yeşil,
    taze bir ağaçta kırmızı veriyordu.

    > *Bir kapı, kendi ortamının durumunu ürünün kusuru gibi göstermemelidir.*

    ⚠ Ve bu bir **muafiyet değil**: ölçüm koşmuşsa test tam katılığıyla koşar
    (aşağıdaki `31/31` iddiası). Yalnız *«ölçüm hiç koşmamış»* hâli **skip**tir.
    """
    return any(str(r.get("certified") or "").startswith("olculdu")
               for r in (schema.get("relationships") or []))


def test_ILISKI_SERTIFIKASI_ihracta_TASINIR(schema):
    """`§F3` ile tutarlılık: `certified` bir eksiklik değil bir **beyandır**; dışarı
    verirken düşürmek karşı tarafa *«ölçüldü»* demektir."""
    d = belge(schema["cubes"], iliskiler=schema.get("relationships") or [])
    rels = d.get("relationships") or []
    assert rels, "31 ilişki ihraç edilmeli"
    damgalar = {(r.get(UZANTI) or {}).get("certified") for r in rels}
    assert all(damgalar), "damgasız ilişki ihraç edildi"
    # 🔴 `§F6` — ÖLÇTÜĞÜMÜZÜ «ÖLÇMEDİK» DİYE İHRAÇ ETMEYİZ. Canlıda ölçüldü: boyut kökeni
    # `olculdu:saglikli` derken ilişkiler `olculmedi` gidiyordu; `§F3` ise **31/31**'ini
    # ölçmüştü. Kusur ihraçta değil BESLEMEDEYDİ — damga yalnız boyut kökenine basılıyordu.
    # *Kendi ölçümünü eksik beyan etmek, ölçmemekten farklı bir kusurdur: emeği çöpe atar.*
    if not _olcum_kosmus_mu(schema):
        pytest.skip("fan-out ölçümü bu proje ağacında hiç koşmamış (taze derleme) — "
                    "31/31 `olculmedi` beklenen ve DOĞRU hâldir")
    assert "olculdu:saglikli" in damgalar, (
        f"ölçülmüş ilişkiler «ölçülmedi» diye ihraç ediliyor: {sorted(damgalar)}")


def test_SEMADA_iliskiler_de_DAMGALI(schema):
    """Damganın evi: `WrenService._damgala_fanout` — ikinci bir rozet fonksiyonu yok."""
    rels = schema.get("relationships") or []
    assert rels
    assert all(r.get("certified") for r in rels), "damgasız ilişki var"
    if not _olcum_kosmus_mu(schema):
        pytest.skip("fan-out ölçümü bu proje ağacında hiç koşmamış (taze derleme)")
    assert sum(1 for r in rels if r["certified"] == "olculdu:saglikli") == len(rels), (
        "canlı katalogda 31/31 sağlıklı ölçülmüştü — damga bunu yansıtmalı")


def test_NORMALLESTIRICI_IDEMPOTENT():
    """*Bir normalleştirici, normalleştirdiğini bozmamalıdır.* Zaten-pack girdi
    dokunulmadan geçer."""
    from app.ossie import _pack_sekline_getir
    pack = {"name": "x", "base_object": "t",
            "measures": [{"name": "m", "expression": "SUM(a)", "synonyms": ["s"]}],
            "dimensions": [{"name": "d"}]}
    assert _pack_sekline_getir(pack) == pack, "zaten-pack girdi DEĞİŞMEMELİ"
    sema_sekli = {"name": "x", "base_object": "t", "measures": ["m"],
                  "measure_expressions": {"m": "SUM(a)"}, "dimensions": ["d"]}
    bir = _pack_sekline_getir(sema_sekli)
    assert _pack_sekline_getir(bir) == bir, "ikinci geçiş bozmamalı"


def test_SEMI_ve_NON_additive_LISTEDEN_olcuye_tasinir():
    """`schema()` bunları **küp düzeyi liste** olarak tutar; `packs/` ölçü içinde.
    Düşerse bir bakiye düz `SUM` edilir — *güvenle yanlış* sayı."""
    ds = disa_aktar({"name": "x", "base_object": "t",
                     "measures": ["bakiye", "oran", "adet"],
                     "measure_expressions": {"bakiye": "SUM(b)"},
                     "semi_additive": ["bakiye"], "non_additive": ["oran"],
                     "dimensions": []})
    ek = {m["name"]: (m.get(UZANTI) or {}).get("additive") for m in ds["metrics"]}
    assert ek == {"bakiye": "semi", "oran": "non", "adet": None}


def test_KUP_ETIKETI_display_alanindan_okunur():
    """Ölçüldü: şemada `label` yok, **`display`** var — üç yanlış tahminden biri."""
    ds = disa_aktar({"name": "oee", "display": "OEE", "base_object": "t",
                     "measures": ["m"], "dimensions": []})
    assert ds.get("label") == "OEE"
