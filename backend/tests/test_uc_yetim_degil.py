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

# --- API-ONLY BEYANI: frontend tüketicisi OLMAYACAK uçlar, gerekçesiyle ------------
#
# Buraya bir yol eklemek bir KARARDIR ve gerekçesi burada durur. "Şimdilik" diye eklenen
# her satır, kapının varlık sebebini bir parça yer.
API_ONLY: dict[str, str] = {
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
    """`/measures/candidates/{cid}/preview` → `/measures/candidates/<herhangi>/preview`."""
    # `re.escape` süslü parantezleri de kaçırır; şablon yerini bulabilmek için geri açılır.
    # Yerine konan joker `\s` içerdiğinden `re.sub` REPL'i olarak veremeyiz (repl'de
    # ters-bölü kaçışları yeniden yorumlanır ve `\s` "bad escape" verir) → lambda ile.
    kacisli = re.escape(yol).replace(r"\{", "{").replace(r"\}", "}")
    return re.compile(re.sub(r"\{[^}]+\}", lambda _m: r"[^\"'`\s]+", kacisli))


def test_HER_UC_ya_frontendde_ya_API_ONLY(client):
    """ASIL KAPI. Yeni bir uç eklenip UI'a bağlanmazsa bu test kırılır."""
    fe = _frontend_kaynak(_frontend_dir())
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

    fe = _frontend_kaynak(_frontend_dir())
    artik_kullanilan = sorted(y for y in API_ONLY if _aranan(y).search(fe))
    assert not artik_kullanilan, (
        f"API_ONLY beyanı yanlış — bu yol(lar) frontend'de KULLANILIYOR: {artik_kullanilan}. "
        "Beyanı kaldırın; 'UI tüketicisi olamaz' artık doğru değil.")


def test_API_ONLY_her_satirda_GEREKCE_tasir():
    """Gerekçesiz bir beyan, beyan değil bir istisnadır."""
    for yol, gerekce in API_ONLY.items():
        assert len(gerekce.strip()) >= 30, f"{yol}: gerekçe çok kısa/yok"


def test_bu_turda_KAPATILAN_iki_yetim(client):
    """Kayıt: bu iki uç bu oturumda YAZILDI ve frontend tüketicisi OLMADAN bırakıldı.
    Faz H2'de kapatıldılar; test onları adıyla anar ki geri açılırlarsa fark edilsin."""
    fe = _frontend_kaynak(_frontend_dir())
    for yol in ("/ask/contribution", "/measures/candidates/{cid}/preview"):
        assert yol in set(_yollar(client)), f"{yol} kayboldu"
        assert _aranan(yol).search(fe), (
            f"{yol} yeniden yetim kaldı — Faz H2'de kapatılmıştı")
