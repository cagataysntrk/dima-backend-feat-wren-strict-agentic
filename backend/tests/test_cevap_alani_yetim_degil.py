"""YETİM CEVAP ALANI KAPISI — `AskResponse`'a eklenen her alanın bir TÜKETİCİSİ olmalı.

## Neden bu kapı var

`tests/test_uc_yetim_degil.py` **uç** seviyesinde çalışıyor: bir endpoint'in frontend
tüketicisi var mı? Ama bir uç tüketilse bile **cevabın içindeki bir alan** tüketicisiz
kalabilir — ve o zaman backend "özellik bitti" der, kullanıcı hiçbir şey görmez.

Bu oturumda tam olarak bu oldu: **`agent_run`** (Faz 4'ün ajan makbuzu) `AskResponse`'a
eklendi, 23 testle kilitlendi ve **frontend'de hiç okunmuyordu**. Aynı denetimde
`Planlayici.sec()`'in de hiçbir çağıranı olmadığı çıktı. İkisi de bu oturumda on bir kez
eleştirilen *"beyan var, TÜKETİCİSİ yok"* sınıfının kendi kodumdaki hâliydi.

> Kural: **bir alanın testi, o alanın kullanıldığını kanıtlamaz.**

## Kapının biçimi

`AskResponse`'un **kullanıcıya bir şey GÖSTEREN** her alanı için frontend'de en az bir
okuma aranır. Muafiyet listesi **kısa ve gerekçeli**dir — gerekçesiz muafiyet kapıyı
kendiliğinden eritir.
"""

from __future__ import annotations

import pathlib

import pytest

from app.schemas import AskResponse

FE = pathlib.Path(__file__).resolve().parents[2] / "dima-frontend-demo-master" / "src"

#: Frontend tüketicisi ARANMAYAN alanlar ve **gerekçeleri**. Gerekçesiz muafiyet yok.
MUAF: dict[str, str] = {
    "question": "isteğin yankısı — FE zaten kendi gönderdiği metni biliyor",
    "planned_sql": "motorun plan çıktısı; `sql` gösteriliyor, bu denetim/log içindir",
    "is_new_topic": "salt bilgilendirici breadcrumb; FE thread'i kendi komposer'ından bilir",
    "reply_to_label": "thread rozeti — `threads.ts` gruplamasından türetiliyor",
}


def _fe_metni() -> str:
    if not FE.exists():
        pytest.skip("frontend kaynağı mount edilmemiş (CI reçetesinde -v ... :ro gerekir)")
    return "\n".join(f.read_text(encoding="utf-8", errors="ignore")
                     for f in FE.rglob("*.ts*"))


def test_HER_CEVAP_ALANININ_frontend_TUKETICISI_var():
    """Backend bir alan üretiyorsa kullanıcı onu görebilmeli — yoksa özellik BİTMEMİŞTİR."""
    metin = _fe_metni()
    yetim = [ad for ad in AskResponse.model_fields
             if ad not in MUAF and ad not in metin]
    assert not yetim, (
        "YETİM CEVAP ALANI: backend üretiyor, frontend HİÇ okumuyor → "
        f"{sorted(yetim)}\n"
        "Ya bir tüketici bağla ya MUAF sözlüğüne GEREKÇESİYLE ekle. "
        "Üçüncü seçenek yok — sessiz bir alan, yapılmamış bir özelliktir.")


def test_MUAF_LISTESI_bayatlamiyor():
    """Muafiyet listesi kendiliğinden erimemeli: artık var olmayan bir alan için muafiyet
    taşımak, listeyi bir çöplüğe çevirir ve kapıyı okunamaz yapar."""
    olmayan = [ad for ad in MUAF if ad not in AskResponse.model_fields]
    assert not olmayan, f"MUAF listesinde artık var olmayan alan(lar): {olmayan}"


def test_AGENT_RUN_gercekten_render_ediliyor():
    """Bu kapının doğduğu somut vaka. `agent_run` yalnız tipte geçmemeli — ekranda
    **render edilmeli**, yoksa "tüketici var" iddiası bir import'tan ibaret kalır."""
    metin = _fe_metni()
    assert "item.agent_run" in metin, "agent_run bir bileşende OKUNMUYOR"
    for beklenen in ("step_count", "truncated", "reddedildi"):
        assert beklenen in metin, (
            f"agent_run makbuzunun {beklenen!r} kısmı gösterilmiyor — kısmi render, "
            "denetlenebilirlik iddiasını boşa çıkarır")


# --- K2 · (c) BOYUTU: alanın GEÇMESİ yetmez, ULAŞILABİLİR olmalı ------------------
#
# 🔴 FAZ 0.23'ün dersi: yukarıdaki kapı `contribution` için **yanlış-pozitif yeşil**
# veriyordu — alan `ReportCard.tsx`'te geçiyordu ve kapı memnundu. Ama `ReportCard`'a
# **sıra hiç gelmiyordu**: `ReportPanel`'in kapısı `it.result || it.kpi` idi ve
# *"cevap üstünde konuş"* dalı `result` DÖNDÜRMEZ. Yani alan **kaynakta vardı,
# ekranda yoktu**. Faz D2/G1/G3'te ödenmiş üç özellik görünmüyordu.
#
# Ders: *"alan FE kaynağında geçiyor"* bir TÜKETİCİ kanıtı değil, bir **METİN** kanıtıdır.
# Bu deponun altıncı kez tekrarlayan kusuru: **testler METNİ ölçtü, davranışı değil.**

def _yorumsuz_kod(m: str) -> str:
    """`//` yorum satırlarını atar — kapı KODU ölçmeli, kodun ANLATIMINI değil."""
    return "\n".join(s for s in m.splitlines()
                     if not s.lstrip().startswith(("//", "*", "/*", "{/*")))


def _panel_metni() -> str:
    if not FE.exists():
        pytest.skip("frontend kaynağı mount edilmemiş (CI reçetesinde -v ... :ro gerekir)")
    return (FE / "components" / "ReportPanel.tsx").read_text(encoding="utf-8")


def test_RAPORLANABILIRLIK_kapisi_TEK_SAHIP():
    """Kapı İKİ yerde ayrı yazılıydı (`lastReportableIdx` + render dalı) → biri düzeltilse
    diğeri körlüğü miras alırdı. *"Aynı kuralın iki sahibi"* bu deponun 1 numaralı kusuru."""
    m = _panel_metni()
    assert "function raporlanabilir(" in m, \
        "raporlanabilirlik kapısının TEK SAHİBİ yok — kural yine kopyalanmış"
    assert m.count("raporlanabilir(it)") >= 2, \
        f"tek sahip yazılmış ama İKİ çağrı yeri de ona bağlanmamış: {m.count('raporlanabilir(it)')}"

    # ⚠ İlk sürümde bu iddia `m.count("it.result || it.kpi") == 0` idi ve KENDİ AÇIKLAMA
    # YORUMLARIMI sayıp kırmızı verdi — yani tam da eleştirdiğim *"METNİ ölç, davranışı
    # değil"* kusuruna düştüm (bu turda ikinci kez). Doğru ölçüm: **yorumlar ve tek sahibin
    # gövdesi çıkarıldıktan sonra** panelde `it.result` okuması KALMAMALI.
    kod = _yorumsuz_kod(m)
    bas = kod.index("function raporlanabilir(")
    sahip_disi = kod[:bas] + kod[kod.index("\n}", bas):]
    assert "it.result" not in sahip_disi and "it.kpi" not in sahip_disi, (
        "eski satır-içi kapı hâlâ duruyor (tek sahibin DIŞINDA `it.result`/`it.kpi` okuması "
        "var). Tek sahip varken ikinci bir kopya, düzeltmenin yarısının kaybolması demektir.")


def test_RESULT_YOKKEN_de_ULASILABILIR():
    """K2/(c): `result=None` iken gövdeyi taşıyan alanlar kapıdan GEÇMELİ.

    `ask.py`'nin *"cevap üstünde konuş"* dalı bilerek `result` döndürmez — kodun kendi
    yorumu: *"Bulgular CEVABIN GÖVDESİDİR … `contribution` alanı zengin gövdeyi taşır."*"""
    m = _panel_metni()
    govde = m[m.index("function raporlanabilir("):]
    govde = govde[:govde.index("\n}")]
    for alan in ("result", "kpi", "contribution", "prescription"):
        assert f"it.{alan}" in govde, (
            f"`{alan}` raporlanabilirlik kapısında YOK → o alanı taşıyan cevap "
            "hiçbir zaman render edilmez (backend üretir, ekran göstermez)")


def test_SAF_NOT_dalinda_NEXT_STEPS_var():
    """Netleştirme cevabı (`result=None`, yalnız `note`) *"Hangi ölçüyü istiyorsun?"* diye
    soruyordu ve **altında tıklanacak hiçbir şey yoktu** — `next_steps` render'ı YALNIZ
    `ReportCard`'da vardı, not dalında yoktu (ölçüldü: 0 isabet).

    Chip `onCubeEdit` kullanır → `/cube` → **0 LLM**. `suggestions`'tan AYRIDIR: o yeni bir
    SORU sorar, bu mevcut sorguyu DÜZENLER."""
    m = _panel_metni()
    assert "it.next_steps" in m, "saf-not dalında `next_steps` render'ı YOK"
    assert "onCubeEdit({ cq: step.cube_query" in m, \
        "`next_steps` chip'i deterministik /cube yolunu kullanmıyor (LLM'e düşer)"


def test_REPORTCARD_KONUSMA_dalindaki_BILINCLI_gizleme_KORUNDU():
    """🔴 **GERİ ALMAYIN uyarısı testle kilitlendi.** `ReportCard.tsx:887`'nin
    `!item.contribution` koşulu bir EKSİK DEĞİL, tasarımdır: konuşma cevabında gezinme
    `ContributionLayer`'ın TIKLANABİLİR SEGMENTLERİNDEN gelir; `next_steps`'i orada da
    göstermek aynı listeyi **İKİ KEZ**, üstelik ikincisini **YANLIŞ BAŞLIKLA**
    (*"sonraki adım"*) sunardı. 0.23 bu koşula DOKUNMAZ."""
    if not FE.exists():
        pytest.skip("frontend kaynağı mount edilmemiş")
    kart = (FE / "components" / "ReportCard.tsx").read_text(encoding="utf-8")
    assert "!item.contribution && onCubeEdit && (item.next_steps?.length ?? 0) > 0" in kart, (
        "ReportCard'ın bilinçli gizlemesi kaldırılmış — konuşma cevabında `next_steps` "
        "İKİ KEZ görünür (ikincisi yanlış başlıkla). Kodun kendi gerekçesi bunu yasaklar.")
