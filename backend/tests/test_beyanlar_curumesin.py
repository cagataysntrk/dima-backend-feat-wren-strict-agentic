"""BÜTÜNSEL DENETİM — "tüketicisi yok" beyanları ÇÜRÜMESİN.

## Neden bu dosya var

Bu depoda üç primitif bilinçle **tüketicisiz** duruyor ve her biri MIMARI'de gerekçesiyle
kayıtlı. Bu meşrudur — ama **bir yorum çürüyebilir**. Bu turda sekiz kez ölçülen desen
(*beyan var, kod tanımaz*) tam olarak böyle doğar: birisi doğru bir cümle yazar, dünya
değişir, cümle kalır.

Buradaki testler o beyanları **kapıya** çevirir: beyan yanlışlaşırsa CI kırılır ve düzelten
kişi ya primitifi bağlar ya beyanı günceller. Üçüncü seçenek yoktur — `test_uc_yetim_degil`
uç seviyesinde ne yapıyorsa, bu dosya **modül seviyesinde** onu yapar.
"""

from __future__ import annotations

import pathlib
import re

APP = pathlib.Path(__file__).resolve().parents[1] / "app"


def _app_kaynagi(haric: str) -> str:
    return "\n".join(f.read_text(encoding="utf-8", errors="ignore")
                     for f in APP.rglob("*.py") if f.name != haric)


# --- G4: anlatım doğrulayıcı --------------------------------------------------

def test_ANLATIM_DOGRULAYICI_beyani_HALA_dogru():
    """MIMARI §12.6: *"Tüketicisi HENÜZ YOK ve bu açıkça kaydedilir: bugün sistemde
    LLM-üretimi düz metin HİÇ YOKTUR (`interpret` deterministiktir, sayıları sonuçtan
    gelir)."*

    Beyan iki şeyi birden iddia eder ve **ikisi de** doğrulanmalı:
      1. `narration_guard` üretim yolundan çağrılmıyor (yoksa beyan bayat),
      2. LLM'den düz metin gelen bir yol yok (yoksa beyan YANLIŞ ve **korumasız bir
         uydurma yüzeyi** var demektir).

    İkincisi asıl tehlikedir: birisi bir gün `/ask` yanıtına LLM-üretimi bir özet
    eklerse, doğrulayıcı yazılmış ve test edilmiş olduğu hâlde **devrede olmaz**.
    """
    kaynak = _app_kaynagi("narration_guard.py")
    cagriliyor = ("narration_guard" in kaynak or "guvenli_anlatim" in kaynak)

    # LLM sağlayıcısının ürettiği HER ŞEY yapısaldır: SQL ya da CubeQuery JSON.
    # Düz metin üreten bir yöntem eklenirse bu liste büyür ve test uyarır.
    llm = (APP / "llm.py").read_text(encoding="utf-8")
    uretenler = set(re.findall(r"def (generate_\w+|\w*_?(?:narrate|anlat|prose)\w*)\(", llm))
    # `sql`/`cube`/`select` içeren adlar YAPISAL çıktı üretir (SQL ya da CubeQuery JSON) —
    # doğrulayıcının konusu değil. `generate_followup_sql` da bunlardan biridir: takip
    # sorusundan SQL üretir, cümle değil.
    metin_ureten = {a for a in uretenler
                    if not any(x in a for x in ("sql", "cube", "select", "refine", "repair"))}

    if metin_ureten and not cagriliyor:
        raise AssertionError(
            f"LLM'den DÜZ METİN üreten yöntem(ler) belirdi: {sorted(metin_ureten)} — ama "
            "`narration_guard` hiçbir üretim yolundan çağrılmıyor. Doğrulayıcı yazılmış ve "
            "test edilmiş olduğu hâlde DEVREDE DEĞİL: korumasız bir uydurma yüzeyi var.\n"
            "İki seçenek: (1) `guvenli_anlatim`'ı o yola tak, (2) MIMARI §12.6'yı güncelle.")

    if cagriliyor:
        raise AssertionError(
            "`narration_guard` artık ÇAĞRILIYOR — MIMARI §12.6'daki "
            "\"Tüketicisi HENÜZ YOK\" beyanı BAYAT. Beyanı güncelle ve bu testi "
            "doğrulayıcının GERÇEKTEN devrede olduğunu ölçen bir teste çevir.")


# --- E-2: cube_query_hash -----------------------------------------------------

def test_CUBE_QUERY_HASH_beyani_HALA_dogru():
    """MIMARI §5: *"primitif, tüketici bekliyor"* (sonuç cache'i, Faz E-2 — plan onu
    ölçülen tekrar oranı eşiği aşmadan kurmamayı söylüyor). Cache kurulduğu gün bu
    test kırılır ve beyanın güncellenmesini zorlar."""
    kaynak = _app_kaynagi("contracts.py")
    assert "cube_query_hash" not in kaynak, (
        "`cube_query_hash` artık kullanılıyor — MIMARI'deki \"tüketici bekliyor\" "
        "beyanı bayat. Beyanı güncelle.")


# --- F4: LLM'e verilecek araç listesi -----------------------------------------

def test_LLM_ARAC_LISTESI_beyani_HALA_dogru():
    """`tools.llm_araclari()` planlayıcının LLM yüzeyi için yazıldı; F4 (plan SEÇİMİ)
    telemetriye bağlı olduğu için henüz tüketicisi yok. Bağlandığı gün bu test kırılır."""
    kaynak = _app_kaynagi("tools.py")
    assert "llm_araclari" not in kaynak, (
        "`tools.llm_araclari` artık çağrılıyor — MIMARI §11.6d'deki \"F4 henüz yok\" "
        "beyanı bayat.")


# --- Planlayıcının itiraf mekanizması -----------------------------------------

def test_DIS_ADIM_API_si_KORUNUR_ama_tuketicisi_YOK():
    """`Planlayici.dis_adim()` kayıtsız adımları makbuzda `gated: false` ile itiraf eder.
    Faz F3'te `contribution.report` kayda girince tek tüketicisi kalktı.

    API **silinmedi** ve bu bilinçlidir: gerçek kayıtsız adımlar için itiraf mekanizması
    hâlâ doğru şeydir. Ama tüketicisi olmadığı **kaydedilmeli** — sessizce durması, bir
    sonraki geliştiricinin "demek ki bileşikler zaten itiraf ediliyor" diye varsaymasına
    yol açardı.
    """
    from app import planner

    assert hasattr(planner.Planlayici, "dis_adim")
    kaynak = _app_kaynagi("planner.py")
    # Yorumlar tarihçe anlatır; ÇAĞRI aranır (`plan.dis_adim(` / `.dis_adim(`).
    cagrilar = [s for s in kaynak.splitlines()
                if ".dis_adim(" in s and not s.strip().startswith("#")]
    assert not cagrilar, (
        "`dis_adim` yeniden çağrılıyor:\n  " + "\n  ".join(cagrilar)
        + "\nBu meşru olabilir (gerçek bir kayıtsız adım) ama MIMARI §11.6c'nin "
          "\"itiraf artık gereksiz\" cümlesi güncellenmeli.")


# --- Gerçekten ÖLÜ kod ---------------------------------------------------------

def test_OLU_AUTH_yardimcisi_GERI_gelmesin():
    """`app/auth/dependencies.require_superadmin` **silindi** (bütünsel denetim,
    2026-08-02): sıfır çağıranı vardı. Public plane'de superadmin-only bir uç YOK; admin
    plane AYRI bir serviste (ADR-0015) kendi kontrolünü yapıyor —
    `control_plane.auth_service`'in `require_superadmin` **parametresi** farklı bir şeydir
    ve o yaşıyor.

    Ölü bir YETKİ yardımcısı zararsız değildir: birisi onu "hazır" sanıp kullanır ve
    **yanlış plane'in** kontrolünü uygulamış olur. Bu test geri gelmesini engellemez —
    geri gelirse *kullanılmadan* durmasını engeller."""
    dep = (APP / "auth/dependencies.py").read_text(encoding="utf-8")
    if "def require_superadmin" in dep:
        kaynak = _app_kaynagi("dependencies.py")
        assert "require_superadmin" in kaynak, (
            "`require_superadmin` yeniden tanımlanmış ama HİÇBİR yerden kullanılmıyor — "
            "ya bağla ya sil (MIMARI §5: ölçülmemiş ihtiyaç için altyapı kurma). Public "
            "plane'de superadmin kontrolü gerekiyorsa önce ADR-0015'i (iki-plane ayrımı) "
            "gözden geçir.")
