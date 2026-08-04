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

from tests.kapi_ortak import fe_dosyalari
from tests.kapi_ortak import yorumsuz as _ortak_yorumsuz

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
    """→ `tests/kapi_ortak.yorumsuz` (**TEK SAHİP**). Ad geriye dönük uyum için duruyor.

    İkinci bir ayıklayıcı yaşatmak, bu deponun 1 numaralı kusurunu (aynı kuralın iki
    sahibi) kapının **içine** koymak olurdu — ve ilk sürümü zaten yarımdı (çok satırlı
    blokların devam satırları sızıyordu, 8 satır ölçüldü)."""
    return _ortak_yorumsuz(m)


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


def test_RAPORLANABILIRLIK_SAYMIYOR_KAPATIYOR():
    """🔴 **KAT-5.** İlk sürüm gövde alanlarını SAYIYORDU
    (`result|kpi|contribution|prescription`) ve denetim bedelini ölçtü: listede olmayan
    **beşinci** gövde alanı `eylem_onerisi` — FAZ H'nin *"Onayla"* kartı, ürünün manşet
    vaadi — kapının dışında kalıyordu. `ReportCard`'ın TEK tüketicisi bu kapının
    arkasında; yani onay kartı **hiç render edilmiyordu**. 0.23'ün düzelttiği hatanın
    birebir aynısı, düzeltmenin KENDİ İÇİNE kodlanmıştı.

    Doğru biçim: **gövdeyi sayma, gövdesizliği kapat.** Bu test o yönü kilitler."""
    kod = _yorumsuz_kod(_panel_metni())
    assert "SAF_NOT_ALANLARI" in kod, \
        "kapı hâlâ gövde SAYIYOR — yeni her gövde alanı sessizce görünmez kalır"
    i = kod.index("SAF_NOT_ALANLARI = new Set")
    kume = kod[i:kod.index("]", i)]
    for govde in ("result", "kpi", "contribution", "prescription", "eylem_onerisi",
                  "interpretation", "recommendations", "viz"):
        assert f'"{govde}"' not in kume, (
            f"`{govde}` bir GÖVDE alanı ama «saf not» kümesine konmuş → o alanı taşıyan "
            "cevap hiçbir zaman render edilmez (backend üretir, ekran göstermez)")


def test_ONAY_KARTI_ULASILABILIR():
    """`eylem_onerisi` cevabı (`result`/`kpi`/`contribution`/`prescription` HEPSİ None)
    kapıdan GEÇMELİ — yoksa *"onayla iş yapabilen meslektaş"* vaadi ekranda yoktur."""
    kart = (FE / "components" / "ReportCard.tsx").read_text(encoding="utf-8")
    assert "eylem_onerisi" in kart, "onay kartı ReportCard'da YOK"
    kod = _yorumsuz_kod(_panel_metni())
    i = kod.index("SAF_NOT_ALANLARI = new Set")
    assert '"eylem_onerisi"' not in kod[i:kod.index("]", i)], \
        "onay kartı «saf not» sayılıyor → Onayla düğmesi HİÇ ÇIKMAZ (denetimde bulundu)"


def test_SAF_NOT_dalinda_NEXT_STEPS_var():
    """Netleştirme cevabı (`result=None`, yalnız `note`) *"Hangi ölçüyü istiyorsun?"* diye
    soruyordu ve **altında tıklanacak hiçbir şey yoktu** — `next_steps` render'ı YALNIZ
    `ReportCard`'da vardı, not dalında yoktu (ölçüldü: 0 isabet).

    Chip `onCubeEdit` kullanır → `/cube` → **0 LLM**. `suggestions`'tan AYRIDIR: o yeni bir
    SORU sorar, bu mevcut sorguyu DÜZENLER."""
    # ⚠ İlk sürüm dosyanın TAMAMINDA `"it.next_steps"` arıyordu, üstelik yorumları
    # ayıklamadan: dal silinse bile bir YORUM SATIRI testi yeşil tutardı. Aynı dosyanın
    # 80-88. satırlarındaki kendi eleştirisi (*"alan FE kaynağında geçiyor bir TÜKETİCİ
    # kanıtı değil, METİN kanıtıdır"*) bir ekran aşağıda çiğneniyordu. (Denetim buldu.)
    kod = _yorumsuz_kod(_panel_metni())
    i = kod.find("if (it.note)")
    assert i > 0, "saf-not dalı (`if (it.note)`) bulunamadı — kapı çapası kaymış"
    dal = kod[i:]
    assert "it.next_steps" in dal or "steps={it.next_steps}" in dal, \
        "saf-not dalında `next_steps` render'ı YOK"

    # Chip'in kendisi TEK SAHİPTEDİR (`NextStepChips`) — deterministik /cube yolunu
    # kullandığı orada kilitlenir, burada tekrar aranmaz (ikinci sahip doğmasın).
    chip = (FE / "components" / "NextStepChips.tsx")
    assert chip.exists(), "`NextStepChips` tek sahibi YOK — blok yine kopyalanmış olabilir"
    assert "onCubeEdit({ cq: step.cube_query" in chip.read_text(encoding="utf-8"), \
        "`next_steps` chip'i deterministik /cube yolunu kullanmıyor (LLM'e düşer)"


def test_REPORTCARD_KONUSMA_dalindaki_BILINCLI_gizleme_KORUNDU():
    """🔴 **GERİ ALMAYIN uyarısı testle kilitlendi.** `ReportCard.tsx:887`'nin
    `!item.contribution` koşulu bir EKSİK DEĞİL, tasarımdır: konuşma cevabında gezinme
    `ContributionLayer`'ın TIKLANABİLİR SEGMENTLERİNDEN gelir; `next_steps`'i orada da
    göstermek aynı listeyi **İKİ KEZ**, üstelik ikincisini **YANLIŞ BAŞLIKLA**
    (*"sonraki adım"*) sunardı. 0.23 bu koşula DOKUNMAZ."""
    if not FE.exists():
        pytest.skip("frontend kaynağı mount edilmemiş")
    # ⚠ İlk sürüm BİREBİR bir ifadeyi arıyordu ve chip bloğu tek sahibe (`NextStepChips`)
    # taşınınca **yanlış-kırmızı** verdi — kural yerindeydi, kapı metni ölçüyordu (bu
    # turda beşinci kez). Doğru ölçüm: chip kullanımını BULup KORUYUCUSUNA bakmak.
    kart = _yorumsuz_kod((FE / "components" / "ReportCard.tsx").read_text(encoding="utf-8"))
    i = kart.find("<NextStepChips")
    assert i > 0, "ReportCard chip'leri tek sahip üzerinden render etmiyor"
    koruyucu = kart[max(0, i - 200):i]
    assert "!item.contribution" in koruyucu, (
        "ReportCard'ın bilinçli gizlemesi kaldırılmış — konuşma cevabında `next_steps` "
        "İKİ KEZ görünür (ikincisi yanlış başlıkla). Kodun kendi gerekçesi bunu yasaklar.")


# ═══ FAZ 0.14 / K2 — ÜÇ KÖR NOKTA KAPATILIYOR ════════════════════════════════════
#
# Kapı bugüne kadar yalnız `AskResponse.model_fields`'in **1. seviyesine** ve yalnız
# alanın FE kaynağında **geçip geçmediğine** bakıyordu. Üç körlük ölçüldü:
#   (a) İÇ İÇE alanlar görünmüyor  — `agent_run.steps[].receipt` bir `dict` içinde saklı
#   (b) YALNIZ `AskResponse`       — `DrillResponse`/`ContributionResponse`/`DecisionIn`/`AskRequest`
#   (c) *"geçiyor mu"* ≠ *"ULAŞILABİLİR mi"* — bu deponun en pahalı kusur sınıfı

#: K2/(b) — taranacak diğer sözleşme sınıfları. `AskRequest` **istek** tarafıdır:
#: backend okuyor ama FE hiç GÖNDERMİYORSA o da bir yetimdir.
DIGER_SOZLESMELER = ("DrillResponse", "ContributionResponse", "DecisionIn", "AskRequest")

#: K2/(a)+(b) muafiyetleri — **her biri bir SAHİP gösterir**, gerekçesiz giriş YOK.
#: ✅ **ÜÇÜ KAPANDI (FAZ 0.8 · 0.9 · 0.11)** — muafiyetleri **silindi**, çünkü metinleri
#: *"…'de KALKAR"* diyordu ve o faz indi. Yaşayan bir muafiyet kapıyı eritir.
IC_ICE_MUAF: dict[str, str] = {
    "AskRequest.execute": "FAZ 0.11 — istemci bu alanı GÖNDERMİYOR; backend varsayılanı "
                          "(`True`) her zaman doğru davranışı veriyor. Alan `lab/` "
                          "araçları ve `/ask/verify` için duruyor (SQL üretip "
                          "ÇALIŞTIRMADAN doğrulama). Kaldırmak o yolu kırardı.",
    "AskRequest.limit": "FAZ 0.11 — istemci göndermiyor; backend `settings.max_result_rows` "
                        "tavanını uyguluyor. ⚠ Ham alt-dize taraması bunu YANLIŞLIKLA "
                        "'tüketiliyor' saymıştı: tek isabet DrillDownPanel'deki "
                        "`limit: 50`, yani **DrillRequest** — `AskRequest.limit` DEĞİL. "
                        "Sayaç SINIF AYRIMI yapmıyordu; K2/(b) bunu açığa çıkardı.",
}


def _fe_yorumsuz() -> str:
    return "\n".join(fe_dosyalari().values())


def test_FAZ_0_8_MAKBUZ_KIMLIGI_render_ediliyor():
    """✅ **FAZ 0.8.** `agent_run.steps[].receipt` yalnız `types.ts`'te geçiyordu —
    yani bir **tip beyanıydı**, tüketici değil. Makbuz kimliği bir adımın ürettiği
    KANITIN kimliğidir; görünmezse *"her sayının kaynağını kanıtlayabilen"* vaadi
    adım seviyesinde **beyandan ibaret** kalır."""
    kart = _yorumsuz_kod((FE / "components" / "ReportCard.tsx").read_text(encoding="utf-8"))
    assert "s.receipt" in kart, "adım makbuzu render EDİLMİYOR"
    assert "/contracts/${s.receipt}" in kart, \
        "makbuz kimliği KANITIN KENDİSİNE gitmiyor — tıklanamayan bir kimlik, kimlik değildir"


def test_FAZ_0_9_EXPLAIN_PATH_render_ediliyor():
    """✅ **FAZ 0.9.** Rozet *"ne"* der, `explain.path` *"nereden"* der — ikisi birlikte
    MIMARI §5'in `source` sözleşmesini tamamlar."""
    kart = _yorumsuz_kod((FE / "components" / "ReportCard.tsx").read_text(encoding="utf-8"))
    assert "item.explain?.path" in kart or "explain.path" in kart, \
        "`explain.path` HÂLÂ render edilmiyor — tip var, tüketici yok"


def test_FAZ_0_11_SUPERSEDES_BAGLANDI_silinmedi():
    """✅ **FAZ 0.11.** Yol haritası açık: *"`supersedes` **BAĞLANIR** (silinmez —
    II-E.7 ona dayanıyor)"*. Karar **silinmez** (`decision.py:35`): revizyon YENİ bir
    kayıt yazar ve eskisini işaret eder. Bu alan olmadan revizyon zinciri kurulamaz."""
    from app.routers.decisions import DecisionIn

    assert "supersedes" in DecisionIn.model_fields, "backend alanı SİLİNMİŞ"
    istemci = _yorumsuz_kod((FE / "lib" / "api-client.ts").read_text(encoding="utf-8"))
    assert "supersedes" in istemci, "istemci `supersedes` GÖNDEREMİYOR — yetim sürüyor"
    katman = _yorumsuz_kod(
        (FE / "components" / "PrescriptionLayer.tsx").read_text(encoding="utf-8"))
    assert "supersedes:" in katman, "revizyon zinciri UI'da bağlanmamış"


def test_FAZ_0_7_OLU_SARMALAYICI_SILINDI():
    """✅ **FAZ 0.7.** `runQuery()` sarmalayıcısı vardı, **çağıranı yoktu**. Uç kapısı
    onu yeşil sanıyordu çünkü `/query` dizesi sarmalayıcının KENDİ içinde geçiyordu."""
    istemci = _yorumsuz_kod((FE / "lib" / "api-client.ts").read_text(encoding="utf-8"))
    assert "export async function runQuery" not in istemci, \
        "ölü sarmalayıcı HÂLÂ duruyor — 'bir gün lazım olur' bir gerekçe değildir"


def test_FAZ_0_3_TUVAL_ROZETI_var():
    """✅ **FAZ 0.3.** MIMARI §5: bir cevabın `source`'unu **gizlemek ya da eşitlemek**
    yasaktır. Aynı cevap sohbette rozetli, tuvalde rozetsizdi."""
    tuval = _yorumsuz_kod((FE / "components" / "AnalysisCanvas.tsx").read_text(encoding="utf-8"))
    assert "SourceBadge" in tuval, "tuval HÂLÂ rozetsiz (§5 ihlali)"
    assert "function SourceBadge" not in tuval, \
        "tuvale İKİNCİ bir rozet render edici yazılmış — tek sahip `ChatPanel.SourceBadge`"


def test_K2a_IC_ICE_ALANLAR_da_taranir():
    """🔴 **(a) İÇ İÇE ALAN KÖRLÜĞÜ.** Kapı yalnız `AskResponse.model_fields`'e bakıyordu;
    `agent_run` bir `dict[str, Any]` olduğu için içindeki `steps[].receipt` **hiç
    sorulmuyordu**. Bir alanın tipinin `dict` olması onu güvenli yapmaz — tersine,
    yetimler tam orada saklanır."""
    metin = _fe_yorumsuz()
    for ad in ("agent_run.steps[].receipt", "explain.path"):
        yaprak = ad.split(".")[-1].rstrip("[]")
        if ad in IC_ICE_MUAF:
            continue
        assert yaprak in metin, f"İÇ İÇE YETİM ALAN (muafiyetsiz): {ad}"
    for ad, gerekce in IC_ICE_MUAF.items():
        assert "FAZ" in gerekce, f"`{ad}` muafiyeti bir SAHİP göstermiyor: {gerekce[:60]}"


def test_K2b_DIGER_SOZLESMELER_de_taranir():
    """🔴 **(b) TEK SINIF KÖRLÜĞÜ.** `AskResponse` dışındaki sözleşmelerin alanları hiç
    sorulmuyordu — oysa ölçülmüş yetimlerin üçü tam orada."""
    import app.schemas as S

    metin = _fe_yorumsuz()
    bulunan = [s for s in DIGER_SOZLESMELER if hasattr(S, s)]
    assert bulunan, f"beklenen sözleşme sınıflarının hiçbiri yok: {DIGER_SOZLESMELER}"
    yetim = [f"{sinif}.{alan}"
             for sinif in bulunan
             for alan in getattr(S, sinif).model_fields
             if f"{sinif}.{alan}" not in IC_ICE_MUAF and alan not in MUAF
             and alan not in metin]
    assert not yetim, (
        "YETİM SÖZLEŞME ALANI (AskResponse DIŞINDAKİ sınıflarda):\n  "
        + "\n  ".join(sorted(yetim))
        + "\n\nYa bir tüketici bağla, ya IC_ICE_MUAF'a SAHİBİYLE ekle.")


def test_K2c_ERISILEBILIRLIK_kapisi_SILINEMEZ():
    """🔴 **(c) EN PAHALI KÖRLÜK — *«geçiyor mu»* ≠ *«ULAŞILABİLİR mi»*.**

    `contribution` alanı `ReportCard.tsx`'te **geçiyordu** → kapı yeşildi. Ama o alanı
    üreten cevapta (`result=None`) `ReportPanel` kartı **hiç render etmiyordu** → alan
    kullanıcıya **ulaşamıyordu**. Kapı *"var mı"* soruyordu; sorması gereken
    ***"ulaşılabilir mi"***. Aynı körlük **ikinci, bağımsız bir kapıda** da vardı
    (`lab/deneyim.py` API cevabını ölçüyor, render'ı değil) — yani körlük **sınıfsal**.

    Bu test erişilebilirlik iddialarının **silinemez** olmasını sağlar."""
    kendi = pathlib.Path(__file__).read_text(encoding="utf-8")
    zorunlu = ("test_RAPORLANABILIRLIK_SAYMIYOR_KAPATIYOR", "test_ONAY_KARTI_ULASILABILIR")
    eksik = [z for z in zorunlu if z not in kendi]
    assert not eksik, (
        f"K2/(c) ERİŞİLEBİLİRLİK kapısı EKSİK: {eksik}. Alanın FE kaynağında geçmesi bir "
        "TÜKETİCİ kanıtı değil, bir METİN kanıtıdır — 0.23'te üç ödenmiş özellik tam bu "
        "yüzden ekranda yoktu.")
