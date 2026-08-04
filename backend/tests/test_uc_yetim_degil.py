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
SARMALAYICI_MUAF: dict[str, str] = {
    "runQuery": "🔴 ÖLÇÜLDÜ ve KAYITLI ölü sarmalayıcı ([KANIT §0.1-6]): `POST /query`'nin "
                "sarmalayıcısı var, çağıranı yok. **FAZ 0.7**'nin konusu — orada ya "
                "silinecek ya bağlanacak ve bu muafiyet KALDIRILACAK. Muafiyet burada "
                "kusuru gizlemiyor, SAHİBİNE işaret ediyor.",
}

API_ONLY: dict[str, str] = {
    "/metrics": "FAZ 0.18 — metrik kaydının OKUNABİLİR yüzeyi. Yol haritasının kendi "
                "beyanı: *«frontend: — (sahiplik ekranı 2.2b'de kalır)»*. Uç bugün "
                "kayıt + çakışan terim envanterini döner; **sahiplik EKRANI** (terimi "
                "bir cube'a atama) II-B/2.2b'nin işidir. Kapı bu ucu kurulduğu ANDA "
                "yakaladı — beyan o yüzden burada, sessizce değil.",
    "/contracts": "🔴 FAZ 0.14/K1'İN İLK AVI. Alt-dize taraması bu ucu YEŞİL sanıyordu: "
                  "`/contracts` dizesi `` `/contracts/${cid}` `` içinde VE bir yorum "
                  "satırında geçiyor. Tam-yol + yorumsuz tarama onu açığa çıkardı — "
                  "[KANIT §0.1-5] kapı tarafından yeniden üretildi. **FAZ 0.6**'nın "
                  "konusu: ya kanıt-geçmişi görünümüne bağlanacak (yeni panel DEĞİL, "
                  "`ContractDetailPanel`'in giriş listesi) ya da kalıcı `API_ONLY` "
                  "gerekçesi yazılacak. Bu satır o karara kadar geçerlidir.",
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
