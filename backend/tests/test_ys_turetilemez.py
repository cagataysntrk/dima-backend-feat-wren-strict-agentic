"""🔴🔴 `§YS` — *«YOK SAYILAN»* **TÜRETİLEMEZ**: içerik ile dilbilgisini ayıran tek merci garsondur.

## Ölçülen durum (2026-08-12)

Kanal **eksiksiz kurulu**: alan hem küp şemasında (`intent_semasi`) hem plan şemasında
(`plan_semasi`, 8.628 karakterlik istem) tanımlı, istemde **örneğiyle** isteniyor
(*«…kataloğumda para birimi yok, o yüzden `"yok_sayilan":["dolar"]`»*), tüketicisi iki
yolda da bağlı (`uyum.yok_sayilan_beyani` · `plan_tuketici`), ve iki deterministik
süzgeci var.

🔴 **Ama model onu yazmıyor.** Ölçüldü:

    canlı kütükte `yok_sayilan` geçen satır sayısı:  **0**
    «dolar bazında ciro» · «ciroyu euro olarak göster» · «cironun dolar karşılığı»
    «müşteri kohort analizi yap» (plan yolu, 4-5 adım)   → hiçbirinde beyan yok

⊙ Bu, bu deponun **kendi ölçtüğü** desenin tekrarı (`§C3-D`): *«Bir modelden cevabı
taşımayan bir alanı doldurmasını istemek, ona bir dipnot yazdırmaktır; cevabı verir,
dipnotu atlar.»* O zaman çözüm **türetmek** olmuştu (`ters_yon.eslesen_terim_cikar`).

## 🔴 Peki BURADA da türetilebilir mi — ÖLÇÜLDÜ, HAYIR

En doğal aday: `partial_unknowns`'un **bilinmeyen** listesini `yok_sayilan_beyani`'ye
girdi vermek (iki süzgeci zaten var). Ölçüm:

| soru | bilinmeyen | beyan | doğru mu |
|---|---|---|---|
| *«dolar bazında ciro»* | `['dolar']` | ✅ | **doğru** |
| *«müşteri kohort analizi yap»* | `['kohort', 'analizi']` | ✅ | kohort doğru, `analizi` **gürültü** |
| *«en çok fire **veren** makine hangisi»* | `['veren']` | ✅ | 🔴 **YANLIŞ** |
| *«bu yıl makine bazında ortalama oee»* | `[]` | — | doğru (susuyor) |

🔴 `veren` bir **fiil**dir, bir içerik sözcüğü değil. Onu *«cevaba yansımadı»* diye
bildirmek, doğru bir cevaba **yanlış bir uyarı** iliştirmek olurdu — ve bu deponun
`§101.1` kuralı bunu kapattığı kusurdan **daha pahalı** sayar.

⚠ Ayrımı kurmak için *«hangi sözcük içerik, hangisi dilbilgisi»* listesi gerekir — açık
uçlu bir kelime listesi, yani `ADR-0008`'in yasağı. Ve istemin kendi cümlesi zaten bunu
söylüyor: *«Soru sözcükleri ve nezaket kalıpları yok sayılan DEĞİLDİR — yalnız İÇERİK
taşıyan sözcükleri yaz.»*

> *Bir alanı türetmek, onu üreten yargıyı da türetebiliyorsan mümkündür; içerikle
> dilbilgisini ayıran yargı bizde yok, garsonda var.*

⊘ **KARAR: kanal model-güdümlü KALIYOR.** Eksik olan tesisat değil **garsonun
davranışı**; ve onu ölçecek taban `§26` (garson doğruluk ölçümü) ile park edilmiş.
Bu dosya kararı ve **ölçümünü** kayda geçirir ki bir sonraki tur *«kanal yok»* sanmasın.
"""

from __future__ import annotations

import types

from app import cube_router as cr, uyum


def test_KANAL_KURULU_KUP_YOLUNDA():
    """⊘ Ön koşul: alan küp şemasında **isteniyor**.

    ⚠ Yüklem **metne değil ÜRETİLEN ŞEMAYA** bağlı: ilk yazımım kaynakta
    `'"yok_sayilan"'` (çift tırnaklı) aradı, oysa kod `props["yok_sayilan"]` yazıyor —
    yani doğru şeyi yanlış biçimde aradım. *Bir alanın varlığını metinde aramak, onu
    yazan biçime bağlanmaktır* (ders ⑭)."""
    import pathlib

    kaynak = (pathlib.Path(__file__).parent.parent / "app"
              / "intent_semasi.py").read_text(encoding="utf-8")
    assert "yok_sayilan" in kaynak, "küp şemasında alan hiç geçmiyor"
    assert "yansımayan" in kaynak, (
        "alan var ama İSTENMİYOR — açıklaması olmayan bir alan modelce doldurulmaz.")


def test_KANAL_KURULU_PLAN_YOLUNDA():
    """⊘ Ön koşul: plan şemasında **ve** isteminde."""
    from app import plan_semasi as ps

    sema = ps.plan_json_schema({"parti": {"measures": ["toplam_ciro"],
                                          "dimensions": ["musteri"],
                                          "time_dimensions": ["tarih"]}})
    assert "yok_sayilan" in (sema.get("properties") or {}), "plan şemasında alan yok"
    metin = ps.plan_sistem_metni("KATALOG")
    assert "yok_sayilan" in metin and "atlamak bir hatadır" in metin, (
        "🔴 şemada olup istemde istenmeyen bir alan, yazılmayan bir alandır.")


def test_HAM_BILINMEYEN_TURETIM_ICIN_GUVENLI_DEGIL(schema):
    """🔴🔴 **ASIL KAYIT.** *«Türetelim»* çözümü ölçüldü ve **yanlış-pozitif** verdi.

    `«en çok fire VEREN makine hangisi»` → `bilinmeyen=['veren']`. `veren` bir **fiil**;
    onu *«cevaba yansımadı»* diye bildirmek doğru bir cevabı lekelerdi (`§101.1`).

    ⚠ Bu test bir eksiği dondurmuyor: bir gün içerik/dilbilgisi ayrımı **yapısal** olarak
    kurulursa (kelime listesiyle değil) kırılır ve karar yeniden okunur.
    """
    bil, _ = cr.partial_unknowns(cr._norm("en çok fire veren makine hangisi"), schema)
    assert "veren" in bil, (
        "✅ `veren` artık bilinmeyen sayılmıyor — içerik/dilbilgisi ayrımı gelişmiş "
        "olabilir; `§YS` türetme kararı yeniden okunsun.")
    cq = {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["makine"],
          "filters": [], "period_expr": ""}
    cm = next((c for c in schema["cubes"] if c["name"] == "parti"), None)
    kabuk = types.SimpleNamespace(note="", trace=[])
    assert uyum.yok_sayilan_beyani(kabuk, "en çok fire veren makine hangisi",
                                   cq, cm, schema, bil) is True, (
        "⊘ ölçüm tabanı çöktü: süzgeçler `veren`'i zaten eliyor olabilir — o hâlde "
        "türetme kararı yeniden değerlendirilmeli (iyi haber).")
    assert "veren" in kabuk.note, "ölçülen yanlış-pozitif kayboldu"


def test_ICERIK_SOZCUGU_DOGRU_BILDIRILIYOR(schema):
    """✅ Süzgeçler doğru çalışıyor — sorun süzgeçte değil **girdide**."""
    cq = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": [],
          "filters": [], "period_expr": ""}
    cm = next((c for c in schema["cubes"] if c["name"] == "parti"), None)
    kabuk = types.SimpleNamespace(note="", trace=[])
    assert uyum.yok_sayilan_beyani(kabuk, "dolar bazında ciro", cq, cm, schema,
                                   ["dolar"]) is True
    assert "dolar" in kabuk.note


def test_KARAR_YAZILI():
    """🔴 Bir kararın kaydı, kararın kendisidir. *Bir sonraki tur «kanal yok» sanmasın.*"""
    import pathlib

    m = pathlib.Path(__file__).read_text(encoding="utf-8")
    assert "model-güdümlü KALIYOR" in m and "§26" in m, (
        "karar metni silinmiş — bu dosyanın varlık sebebi o karardır.")
