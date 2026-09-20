"""FAZ H1 — YETİM UÇ = KIRMIZI CI. "Tanım Tamamlandı" = arka + ön + test.

## Neden bu kapı var

Bu turda **ben kendim iki yetim uç ürettim** ve bunu ancak denetimde fark ettim:
`POST /ask/contribution` (katkı ayrıştırması + PVM, Faz 5.1/5.2) ve
`POST /measures/candidates/{cid}/preview` (diff önizlemesi, Faz 4.2). İkisi de çalışıyor,
ikisinin de testi var, ikisini de **hiç kimse göremiyordu**. Kullanıcının sözleriyle:
*"arkada geliştirip önde hiç kullanılmayan ucubeler olmasın."*

Bu kapı `_uncovered`'ın "kapsam kapısı" fikrinin API tarafındaki karşılığıdır: backend'in
OpenAPI şemasındaki her yol ya frontend kaynağında **aranır**, ya da aşağıda gerekçesiyle
`API_ONLY` beyan edilir. Üçüncü seçenek yoktur.

## Eşleştirme neden metin araması

Frontend TypeScript'tir ve URL'ler `apiClient.post("/ask/drill", …)` gibi **string
literal** olarak yazılır (saka-standards: tüm HTTP `api-client.ts`'ten geçer). Bir AST
çözümleyicisi daha zarif olurdu ama Python tarafında TS AST'i yok ve bu kapının işi
"çağrıldı mı" sorusunu %100 kesinlikle cevaplamak değil — **unutulmuş uç var mı** sorusunu
cevaplamaktır. Parametreli yollar (`/{cid}/`) joker'e çevrilir çünkü frontend orada
şablon değişkeni yazar (`/measures/candidates/${id}/preview`).

## Bu kapının YAKALAYAMADIĞI şey

*"Frontend'de string var ama hiçbir kullanıcı etkileşimine bağlı değil"* durumunu ayırt
edemez. O bir kod okuma işidir; kapı yalnız **hiç bahsedilmeyeni** yakalar. Sınırın
kaydedilmesi, olmayan bir garantiyi rozetlememek içindir.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.kapi_ortak import fe_kaynak, tam_yol_deseni, tuketiliyor

# --- API-ONLY BEYANI: frontend tüketicisi OLMAYACAK uçlar, gerekçesiyle ------------
#
# Buraya bir yol eklemek bir KARARDIR ve gerekçesi burada durur. "Şimdilik" diye eklenen
# her satır, kapının varlık sebebini bir parça yer.
#: `api-client.ts`'ten export edilip DIŞARIDA çağrılmayan sarmalayıcılar için muafiyet.
#: ⚠ Boş başlar ve **öyle kalmalı**: her giriş bir KARARDIR, gerekçesiz muafiyet kapıyı
#: kendiliğinden eritir. `POST /query` + `runQuery()` ölü sarmalayıcısı **FAZ 0.7**'nin
#: konusudur — buraya muafiyet yazılarak değil, **silinerek ya da bağlanarak** kapanır.
#: 🔴 **BOŞ — ve bu bir KAZANIMDIR.** Burada `runQuery` vardı ([KANIT §0.1-6]: sarmalayıcı
#: var, çağıranı yok). Muafiyetin metni *"**FAZ 0.7**'de … bu muafiyet KALDIRILACAK"*
#: diyordu ve **kaldırıldı**: sarmalayıcı **silindi**. Süresi dolmuş bir muafiyet
#: silinmezse kapının kendisini eritir.
SARMALAYICI_MUAF: dict[str, str] = {}

API_ONLY: dict[str, str] = {
    "/ask-v2": "V2 geliştirme yüzeyi feature-flag ile karanlık; çağıranı P4/P5/P6 geliştirici "
               "acceptance akışı ve HTTP contract testleridir. UI tüketicisi Core MVP'de "
               "bağlanacak; request-level legacy fallback yerine bu uç bilinçli olarak ayrı tutulur.",
    "/stats/plan": "🔴 `A9` — bir **ÖLÇÜM ALETİDİR**, bir ürün özelliği değil. Garson "
                   "planlarının red sınıflarını (`boyut_yok` · `olcu_yok` · `operator` …) "
                   "ve onarım tutma oranını yayımlar; tüketicisi kapıyı koşan "
                   "**operatördür**, son kullanıcı değil. Bir panele bağlamak, "
                   "kullanıcıya *«planlarımızın %19'u reddediliyor»* demek olurdu — "
                   "sıfır değer, ekran tavanına bir satır. ⚠ Kullanıcının bu bilgiye "
                   "karşılığı zaten var: red hâlinde cevabın kendisi gerekçesini söyler "
                   "(`plan_onarim.gerekce`), yani sayı değil **o soruya ait sebep** "
                   "gösteriliyor — doğru katman budur.",
    "/stats/katalog": "🔴 `A11` — kataloğun **envanteri**; `/stats/plan` ile aynı sınıf: "
                      "ölçüm aleti. Rapor `§B-0` üç çelişkili sayı (127/132/141) "
                      "bulmuştu; bu uç tek kaynağı yayımlar (`katalog_metni.envanter`). "
                      "Tüketicisi kapı ve denetim ajanıdır. Kullanıcının *«neyi "
                      "sorabilirim»* sorusunun karşılığı bu sayı DEĞİL, zaten var olan "
                      "katalog listesi ve dürüst reddin yanındaki yetenek beyanıdır — "
                      "*bir envanter sayısı, bir yetenek cevabı değildir.*",
    "/mcp/tools": "FAZ 4.5 — MCP bir **MAKİNE YÜZEYİDİR**: tüketicisi kendi UI'ımız "
                  "değil, kullanıcının kendi ajanıdır (Claude Desktop · dbt · Cube MCP "
                  "istemcileri). Bunu bir panele bağlamak, *«bizim UI'ımızdan bizim "
                  "araçlarımızı çağır»* gibi bir tur atmaktan ibaret olurdu — kullanıcıya "
                  "sıfır değer, ekran tavanına (K5 13/13) bir satır. ⚠ Yüzeyin AÇIK olup "
                  "olmadığı kullanıcıya zaten görünüyor: `mcp_yuzeyi` bayrağı admin "
                  "bayrak panelinde listeleniyor (FLAG_REGISTRY tek kaynak).",
    "/mcp/call": "FAZ 4.5 — aynı gerekçe (`/mcp/tools`). Çağrıyı UI'dan yapmak, HTTP "
                 "yolunun MCP'ye çevrilip geri çevrilmesi demek olurdu; oysa madde tam "
                 "tersini söylüyor: MCP, HTTP'nin YANINA değil İÇİNE bağlanır ve "
                 "`Planlayici.calistir()`'in AYNI dört kapısından geçer.",
    "/stats/gecikme": "FAZ 0.17 — yol başına p50/p95. Yol haritasının kendi beyanı: "
                      "*«frontend: `ui_gelisim_paneli`'nin bir satırı (7.7)»* — yani "
                      "tüketici **FAZ 7.7**'de gelir. Uç şimdi iniyor çünkü ölçüm, "
                      "onu gösterecek ekrandan ÖNCE gelmeli: FAZ 2'nin semantik "
                      "ameliyatı gecikmeyi değiştirirse, o değişimi görebilmek için "
                      "verinin ZATEN birikiyor olması gerekir. Kapı bu ucu kurulduğu "
                      "ANDA yakaladı — beyan o yüzden burada, sessizce değil.",
    "/query": "FAZ 0.7 — ham-SQL yürütme yüzeyi kullanıcıya **bilinçli olarak** "
              "açılmamıştır (MIMARI §5: *«yüklenen dosyaya serbest Python»* ile aynı "
              "gerekçe — uydurma sayının kapısı). Uç duruyor: `/ask/verify` ve lab "
              "araçları onu kullanır. Ölü olan **sarmalayıcıydı** ve silindi.",
    # ⟳ `/metrics` **BEYANDAN ÇIKARILDI** — FAZ 3.1b sahiplik bölümünü `SchemaPanel`'e
    # bağladı (`getMetrics`/`setMetrikSahibi`), yani *"UI tüketicisi olamaz"* artık
    # DOĞRU DEĞİL. Kapı bunu bir sonraki uç eklenirken yakaladı: **bayat bir muafiyet,
    # muafiyeti olmayan bir uçtan tehlikelidir** — çünkü sessizce doğru görünür.
    "/health": "altyapı canlılık probu (Docker/Railway healthcheck) — UI tüketicisi olamaz",
    "/health/ready":
        "altyapı hazırlık probu (motor + DB erişimi); UI aynı bilgiyi ConnectionBadge'de "
        "kendi çağrısından alır",
    "/dry-plan":
        "motor doğrulama sondası (hata ayıklama/geliştirici aracı): bir SQL'i çalıştırmadan "
        "planlatır. Ürün akışında karşılığı yoktur — üretim yolları zaten dry_plan'dan "
        "geçer ve kullanıcı SQL yazmaz",
}


def _frontend_dir() -> Path:
    """Frontend kaynak ağacı. Bulunamazsa test ATLANIR — backend deposu tek başına da
    klonlanabilir olmalı ve kapı orada 'kırmızı' değil 'ölçülemedi' demelidir."""
    for aday in (
        Path(__file__).resolve().parents[2] / "dima-frontend-demo-master" / "src",
        Path(__file__).resolve().parents[1] / "dima-frontend-demo-master" / "src",
    ):
        if aday.is_dir():
            return aday
    pytest.skip("frontend kaynağı bulunamadı — yetim uç kapısı bu ortamda ölçülemez")


def _frontend_kaynak(d: Path) -> str:
    return "\n".join(
        f.read_text(encoding="utf-8", errors="ignore")
        for f in sorted(d.rglob("*"))
        if f.is_file() and f.suffix in (".ts", ".tsx")
    )


def _yollar(client) -> list[str]:
    return sorted((client.app.openapi().get("paths") or {}))


def _aranan(yol: str) -> re.Pattern:
    """→ `tests/kapi_ortak.tam_yol_deseni` (TEK SAHİP). Burada yalnız ad korunuyor."""
    return tam_yol_deseni(yol)


def test_HER_UC_ya_frontendde_ya_API_ONLY(client):
    """ASIL KAPI. Yeni bir uç eklenip UI'a bağlanmazsa bu test kırılır."""
    fe = fe_kaynak()
    assert len(fe) > 10_000, "frontend kaynağı beklenenden küçük — tarama güvenilir değil"

    yetim = [y for y in _yollar(client)
             if y not in API_ONLY and not _aranan(y).search(fe)]
    assert not yetim, (
        "YETİM UÇ (frontend tüketicisi yok, API_ONLY beyanı da yok):\n  "
        + "\n  ".join(yetim)
        + "\n\nÜç seçenek var: (1) UI'a bağla, (2) gerekçesiyle API_ONLY'ye ekle, "
          "(3) ucu sil. 'Şimdilik böyle kalsın' bir seçenek DEĞİL — bu kapı tam olarak "
          "onu engellemek için var."
    )


def test_API_ONLY_beyani_BAYATLAMAZ(client):
    """Beyan listesi de bakım ister: silinmiş ya da artık UI'da kullanılan bir yol
    listede kalırsa, liste bir gerekçe kaydı olmaktan çıkıp bir çöplüğe dönüşür."""
    mevcut = set(_yollar(client))
    hayalet = sorted(set(API_ONLY) - mevcut)
    assert not hayalet, f"API_ONLY'de artık var olmayan yol(lar): {hayalet}"

    fe = fe_kaynak()
    artik_kullanilan = sorted(y for y in API_ONLY if _aranan(y).search(fe))
    assert not artik_kullanilan, (
        f"API_ONLY beyanı yanlış — bu yol(lar) frontend'de KULLANILIYOR: {artik_kullanilan}. "
        "Beyanı kaldırın; 'UI tüketicisi olamaz' artık doğru değil.")


def test_SARMALAYICI_VAR_CAGIRANI_YOK():
    """🔴 **FAZ 0.14/K1 — ikinci kör nokta.** Bir uç frontend'de *"geçiyor"* olabilir ama
    yalnız **ölü bir sarmalayıcının** içinde geçiyordur. Ölçüldü ([KANIT §0.1-6]):
    `POST /query` + `runQuery()` — sarmalayıcı `api-client.ts`'te **var**, çağıranı
    **yok**. Uç kapısı yeşil, özellik ölü.

    Kural: `api-client.ts`'ten **export edilen** her fonksiyonun, o dosyanın **dışında**
    en az bir çağıranı olmalı. Yoksa ya bağlanır, ya silinir, ya gerekçesiyle muaf yazılır.
    """
    fe_dir = _frontend_dir()
    istemci = fe_dir / "lib" / "api-client.ts"
    if not istemci.exists():
        pytest.skip("api-client.ts bulunamadı")
    kaynak = istemci.read_text(encoding="utf-8")
    disari = "\n".join(
        f.read_text(encoding="utf-8", errors="ignore")
        for f in fe_dir.rglob("*")
        if f.is_file() and f.suffix in (".ts", ".tsx") and f != istemci)

    # ⚠ **KAPSAM: yalnız UÇ SARMALAYICILARI.** `setAccessToken`/`getAccessToken` gibi
    # iç yardımcılar bir uca bağlı değildir; onları "ölü uç" saymak kapıyı yanlış-pozitif
    # yapar. Ölçüt yapısal: fonksiyon gövdesinde bir **yol değişmezi** (`"/…"` ya da
    # `` `/…` ``) geçiyor mu?
    adlar: list[str] = []
    for m in re.finditer(r"^export (?:async )?function (\w+)", kaynak, re.M):
        govde = kaynak[m.end():m.end() + 1200]
        if re.search(r"""["'`]/[a-z]""", govde):
            adlar.append(m.group(1))
    assert adlar, "api-client.ts'te uç sarmalayıcısı bulunamadı — çapa kaymış"

    # ⚠ **TÜKETİM = ÇAĞRI DEĞİL, KULLANIM.** İlk sürüm `ad\s*\(` arıyordu ve
    # `queryFn: listConversations` gibi **fonksiyon referanslarını** göremedi → dört
    # canlı sarmalayıcıyı "ölü" ilan etti. (Bu turda kapımın METİN ölçtüğü **altıncı**
    # vaka.) Doğru ölçüm: `import` satırları DIŞINDA adın geçmesi yeterlidir — kullanılmayan
    # bir import zaten eslint'e takılır.
    olu = [a for a in adlar
           if a not in SARMALAYICI_MUAF and not tuketiliyor(a, disari)]
    assert not olu, (
        "ÖLÜ SARMALAYICI (api-client.ts'te export edilmiş, DIŞARIDA çağıranı yok):\n  "
        + "\n  ".join(sorted(olu))
        + "\n\nUç kapısı bunları YEŞİL sanar: uç adı sarmalayıcının içinde 'geçiyor'. "
          "Üç seçenek: (1) UI'a bağla, (2) sil, (3) SARMALAYICI_MUAF'a GEREKÇESİYLE ekle."
    )


def test_SARMALAYICI_MUAF_BAYATLAMAZ():
    """Muafiyet listesi kendiliğinden erimemeli — artık var olmayan bir ad için muafiyet
    taşımak, listeyi bir çöplüğe çevirir."""
    fe_dir = _frontend_dir()
    istemci = fe_dir / "lib" / "api-client.ts"
    if not istemci.exists():
        pytest.skip("api-client.ts bulunamadı")
    adlar = set(re.findall(r"^export (?:async )?function (\w+)",
                           istemci.read_text(encoding="utf-8"), re.M))
    olmayan = sorted(a for a in SARMALAYICI_MUAF if a not in adlar)
    assert not olmayan, f"SARMALAYICI_MUAF'ta artık var olmayan ad(lar): {olmayan}"


def test_API_ONLY_her_satirda_GEREKCE_tasir():
    """Gerekçesiz bir beyan, beyan değil bir istisnadır."""
    for yol, gerekce in API_ONLY.items():
        assert len(gerekce.strip()) >= 30, f"{yol}: gerekçe çok kısa/yok"


def test_bu_turda_KAPATILAN_iki_yetim(client):
    """Kayıt: bu iki uç bu oturumda YAZILDI ve frontend tüketicisi OLMADAN bırakıldı.
    Faz H2'de kapatıldılar; test onları adıyla anar ki geri açılırlarsa fark edilsin."""
    fe = fe_kaynak()
    for yol in ("/ask/contribution", "/measures/candidates/{cid}/preview"):
        assert yol in set(_yollar(client)), f"{yol} kayboldu"
        assert _aranan(yol).search(fe), (
            f"{yol} yeniden yetim kaldı — Faz H2'de kapatılmıştı")


def test_FAZ_0_6_KANIT_GECMISI_BAGLANDI():
    """✅ **FAZ 0.6.** `GET /contracts` (liste) tüketicisizdi [KANIT §0.1-5] ve uç kapısı
    onu **yeşil sanıyordu**: `/contracts` dizesi hem `` `/contracts/${cid}` `` içinde hem
    bir **yorum satırında** geçiyordu. FAZ 0.14/K1'in tam-yol + yorumsuz taraması onu
    açığa çıkardı — kapı, kurulmasının üzerinden **bir madde geçmeden** iş gördü.

    🔴 **YENİ PANEL AÇILMADI.** Panel tavanı **13/13, pay 0** (`PK-23`) ve yol haritası
    zaten *"yeni panel değil"* diyordu: liste `ContractDetailPanel`'in **giriş
    görünümü** oldu. *"Yeni özellik yeni panel doğurmaz."*

    Kanıt kaydı ancak **bulunabiliyorsa** bir kanıttır: tek tek `contract_id` bilmek
    gereken bir arşiv, arşiv değildir."""
    from tests.kapi_ortak import fe_dosyalari

    dosyalar = fe_dosyalari()
    istemci = dosyalar.get("lib/api-client.ts", "")
    assert "listContracts" in istemci, "`GET /contracts` sarmalayıcısı YOK"
    panel = dosyalar.get("components/ContractDetailPanel.tsx", "")
    assert "listContracts" in panel, "kanıt geçmişi hiçbir yüzeyden çağrılmıyor"
    # Yeni panel AÇILMADIĞI ayrıca K5'te (tavan 13) kilitli; burada niyeti kaydediyoruz.
    assert "function ContractGecmisPanel" not in panel, \
        "yeni bir panel açılmış — tavan 13/13 dolu, 'yeni özellik yeni panel doğurmaz'"
