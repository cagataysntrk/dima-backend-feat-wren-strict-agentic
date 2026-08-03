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
