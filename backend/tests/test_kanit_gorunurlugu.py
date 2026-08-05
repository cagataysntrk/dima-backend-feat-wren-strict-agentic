"""FAZ 7.8 kapısı — **ayırt edicileri görünür kıl.** [bayrak: `ui_kanit_gorunurlugu`]

İki kalem, ve **biri bir ÇIKARMADIR**.

## 🔴 K1 — makbuz katmanlı değildi, ve D3 *"zaten yapılmış"* diye YANLIŞ kapatılmıştı

Ölçüm: `grep -rn "<details\\|<summary" src/` → **2**, ikisi de `ConnectionReviewPanel`'de.
Cevap kartında **sıfır**. Yani *"makbuz katmanlı"* bir **beyandı**, kod onu tanımıyordu —
bu deponun en sık kusur sınıfı, bu kez bir **denetim kapanışında**.

Bugünkü hâl **üç kopuk yüzey, sıfır kademe**: `?` toggle'ı üç düz listeyi aynı görsel
seviyede açıyor · SQL ayrı toggle · `contract_id` ayrı modal.

## 🔴 K2 — madalya KALDIRILDI (bir çıkarma kalemi)

`ChatPanel.confidenceBadge` 🥇/🥈/🥉 **ve yüzde** basıyordu: `Yüksek güven (100%)`.
Kaynağı `answer.py::_EXPLAIN_PATH` — **sabit kodlu bir yol etiketi**
(`cube→1.0 · vqr→0.95 · cube+llm→0.85`), hesaplanmış değil.

> MIMARI §9'un kendi yasağının üründe **canlı ihlali**:
> *"kalibre edilmediği sürece o sayı bir güven değil bir **SÜSTÜR**."*

⚠ Ve süs zararsız değil: **bir rozetin en kötü hâli, denetlemeyi gereksiz
göstermesidir.** %100 gördüğü bir cevabı kimse denetlemez.

## Neden kademe — bir tercih değil, bir ölçüm

> *"Daha uzun açıklamalar, **doğruluğu artırmadan** kullanıcı güvenini artırıyor."*
> — Steyvers ve ark., *Nature Machine Intelligence* 7:221-231 (2025)

Varsayılan **kısa**, ayrıntı **talep üzerine**.
"""

from __future__ import annotations

import re

import pytest

from tests.kapi_ortak import fe_dosyalari, fe_kaynak


# --- K2: madalya ve yüzde YOK ----------------------------------------------------------

#: 🔴 Yasak **madalyaya** değil, madalyanın **GÜVEN bağlamına** konur — ve bu ayrım
#: ölçümle öğrenildi: ilk sürüm `🥇`'i her yerde yasakladı ve `OutputInsight`'ın
#: `top: "🥇"` **olgu ikonunu** yakaladı. O bir *"en yüksek kalem"* işaretidir, bir güven
#: iddiası değil. *Bir kuralı gereğinden geniş yazmak, doğru bir kodu kırmızıya boğar.*
_MADALYA = ("🥇", "🥈", "🥉")
_GUVEN_SOZCUKLERI = ("güven", "confidence", "confidenceBadge")


def test_K2_MADALYA_GUVEN_BAGLAMINDAN_kaldirildi():
    """🔴 Bir **çıkarma** kalemi. Tarama **yorumsuz** kaynakta: `ChatPanel`'in kaldırma
    gerekçesi madalyaları **anlatıyor** ve bir metin taraması kendi belgesini yakalarsa
    kapı, düzeltilmiş bir kusuru düzeltilmemiş sanır."""
    for yol, kaynak in fe_dosyalari().items():
        for madalya in _MADALYA:
            for i in (j for j in range(len(kaynak)) if kaynak.startswith(madalya, j)):
                pencere = kaynak[max(0, i - 200):i + 200].lower()
                catisan = [w for w in _GUVEN_SOZCUKLERI if w.lower() in pencere]
                assert not catisan, (
                    f"🔴 {yol}: `{madalya}` bir GÜVEN bağlamında ({catisan}) — kalibre "
                    f"edilmemiş bir güven göstergesi denetlemeyi GEREKSİZ gösterir.")


def test_K2_GUVEN_YUZDESI_basilmiyor():
    """🔴 Asıl ihlal madalya değil **yüzdeydi**: `Yüksek güven (100%)`."""
    kaynak = fe_kaynak()
    assert "confidenceBadge" not in kaynak
    assert not re.search(r"güven\s*\(\$\{?\w*pct", kaynak, re.I), (
        "🔴 Güven yüzdesi yeniden basılıyor — `_EXPLAIN_PATH` bir YOL ETİKETİDİR, "
        "hesaplanmış bir kalibrasyon değil.")


def test_K2_YOL_ROZETI_yerinde_KALDI():
    """⚠ Çıkarma bir **kayıp** olmamalı: `SourceBadge` yolu söylemeye devam ediyor —
    ve yol, ölçülmüş bir olgudur. *Bir süsü kaldırmak, bilgiyi kaldırmak değildir.*"""
    src = fe_dosyalari()["components/ChatPanel.tsx"]
    assert "export function SourceBadge" in src
    assert "◆ CUBE" in src and "◆ VQR" in src


def test_K2_confidence_PROP_u_de_kalkti():
    """🔴 *Bir alanı okumayı bırakıp prop'u bırakmak, kusuru bir sonraki geliştiriciye
    hazır bırakmaktır*: `confidence` prop'u dursaydı biri onu yeniden basardı."""
    src = fe_dosyalari()["components/ChatPanel.tsx"]
    assert "confidence?: number | null;" not in src
    for yol in ("components/ReportCard.tsx", "components/AnalysisCanvas.tsx"):
        assert "confidence={" not in fe_dosyalari()[yol], f"🔴 {yol} hâlâ geçiriyor"


# --- K1: üç katman, TEK kapsayıcı -------------------------------------------------------

def test_K1_DETAILS_var_ve_CEVAP_KARTINDA():
    """Yol haritasının kapısı birebir: *"tek kapsayıcı; `<details>` sayısı **≥1**"*."""
    src = fe_dosyalari()["components/Makbuz.tsx"]
    assert src.count("<details") >= 2, (
        "🔴 İki kademe yok — katman 3 (tam iz) katman 2'nin içinde katlanmalı.")
    assert "<summary" in src


def test_K1_KATMAN1_TEK_SATIR_ve_KISA():
    """🔴 Varsayılan **kısa** olmalı (Steyvers 2025). Katman 1 `<summary>`'dedir: yol +
    adım + ms. ⚠ Trace'in **kendisi** özet satırında olsaydı kademe olmazdı."""
    src = fe_dosyalari()["components/Makbuz.tsx"]
    ozet = src[src.index("<summary"):src.index("</summary>")]
    assert "yolAdi(item.source)" in ozet and "adım" in ozet and "ms" in ozet
    assert "item.trace.map" not in ozet, "🔴 Tam iz özet satırında — kademe yok"


def test_K1_KATMAN2_cube_querydan_DETERMINISTIK():
    """🔴 Backend'e ikinci bir *"bunu anlat"* ucu eklemek, aynı gerçeğin **iki sahibini**
    yaratırdı — ve ikisi bir gün ayrışırdı. Katman 2 `cube_query`'den türetilir."""
    src = fe_dosyalari()["components/Makbuz.tsx"]
    assert "export function neYaptim" in src
    for alan in ("cube", "measures", "dimensions", "timeDimensions", "filters"):
        assert alan in src, f"🔴 katman 2 `{alan}`'ı okumuyor"


def test_K1_UYDURMA_YOK_olmayan_alan_YAZILMAZ():
    """⚠ *"Filtre yok"* yazmak ile filtre satırını **hiç yazmamak** aynı şey değildir:
    ilki bir **iddiadır** ve `cube_query` şekli değişirse sessizce yanlış olur."""
    src = fe_dosyalari()["components/Makbuz.tsx"]
    assert '"filtre yok"' not in src.lower() and "filtre yok" not in src.lower()
    assert "if (!cq || typeof cq !== \"object\") return [];" in src, (
        "🔴 `cube_query` yokken katman 2 boş DÖNMÜYOR — bir şey uydurulabilir.")


def test_K1_AYRINTI_SILINMEDI_yalniz_KATLANDI():
    """🔴 *Denetlenebilirlik bir kademelendirmeye feda edilemez.* Eski blokta görünen
    **her şey** katman 3'te olmalı."""
    src = fe_dosyalari()["components/Makbuz.tsx"]
    for parca in ("item.trace.map", "agent_run", "explain?.path", "item.sql",
                  "planned_sql", "contract_id", "s.receipt", "s.error"):
        assert parca in src, f"🔴 eski makbuzun `{parca}` parçası KAYBOLDU"


def test_K1_REDDEDILEN_adimlar_gizlenmiyor():
    """⚠ *Sessizce kaybolan bir adım, yapılmamış bir adım gibi okunur* — ve koşumun
    maliyeti anlaşılmaz olur."""
    src = fe_dosyalari()["components/Makbuz.tsx"]
    assert "s.error &&" in src and "truncated" in src


def test_K1_YETIM_ALAN_receipt_TIKLANABILIR():
    """FAZ 0.8'in yetim alanı: `agent_run.steps[].receipt` bir kimlik dizgisi olarak
    kalırsa **kimse açamaz**."""
    src = fe_dosyalari()["components/Makbuz.tsx"]
    assert 'href={`/contracts/${s.receipt}`}' in src


def test_K1_UC_KOPUK_YUZEY_birlesti():
    """🔴 Ölçülen kusur *"üç kopuk yüzey"*di. Bayrak açıkken üçü de **tek kapsayıcıda**;
    `ReportCard`'da ikinci bir sahip kalmamalı."""
    src = fe_dosyalari()["components/ReportCard.tsx"]
    # Alt şeritteki `contract_id` düğmesi ve ayrı SQL bloğu YALNIZ bayrak kapalıyken.
    assert src.count("!makbuzKatmanli") >= 3, (
        "🔴 Eski yüzeylerden biri bayraktan bağımsız duruyor — iki sahip AYRIŞIR.")


# --- KURAL B: kapalıyken eski davranış BİREBİR -----------------------------------------

def test_KURALB_bayrak_KAPALIYKEN_eski_yuzey_BIREBIR():
    """🔴 *Bir geri-alma yolunun değeri, geri aldığı şeyin **birebir aynısını**
    vermesindedir*; "biraz daha iyi" bir eski hâl, geri almayı bir **üçüncü** davranışa
    çevirir ve kıyas ölçülemez olur."""
    src = fe_dosyalari()["components/Makbuz.tsx"]
    assert "export function MakbuzDuz" in src, "🔴 kapalı yol yok — geri alma YOK"
    duz = src[src.index("export function MakbuzDuz"):]
    assert "<details" not in duz, "🔴 Kapalı yol da kademeli — geri alma bir üçüncü hâl"
    assert "nasıl çözüldü" in duz, "🔴 eski başlık değişmiş"


def test_KURALB_BAYRAK_kayitli_ve_FABRIKA_varsayilani_var():
    """⚠ *İki liste ayrı ayrı doğrudur ama birlikte eksik olabilir* — kayıtta olup
    `features.yml`'de olmayan bir bayrak `getFeatures()` yanıtında hiç görünmez ve
    özellik **sessizce ölür**."""
    from pathlib import Path

    import yaml

    from app.features import FLAG_REGISTRY

    assert "ui_kanit_gorunurlugu" in FLAG_REGISTRY
    d = yaml.safe_load((Path(__file__).resolve().parents[1] / "demo/packs/features.yml")
                       .read_text(encoding="utf-8"))
    assert "ui_kanit_gorunurlugu" in ((d or {}).get("features") or {})


def test_KURALB_BAYRAK_UI_da_okunuyor():
    """🔴 *Kill-switch yalnız kayıtta varsa yarımdır*: bayrak bir yerde okunmalı."""
    assert 'useFeature("ui_kanit_gorunurlugu")' in fe_kaynak()


@pytest.mark.parametrize("yol", ["cube", "cube+llm", "vqr", "rule"])
def test_YOL_ADI_dort_yolu_da_biliyor(yol):
    """⚠ Bilinmeyen bir yol `source`'un ham hâline düşer — **gizlenmez**. Bir yolu
    tanımamak, onu saklamak için bir sebep değildir."""
    src = fe_dosyalari()["components/Makbuz.tsx"]
    assert f'"{yol}"' in src or f"{yol}:" in src
