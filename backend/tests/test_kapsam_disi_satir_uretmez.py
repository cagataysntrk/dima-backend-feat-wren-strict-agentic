"""🔴 ⑧ — KAPSAM DIŞI BİR SORU **BİR SATIRA DÖNÜŞEMEZ**.

## Ölçülen kusur (canlı, 2026-08-12 — dört tur, dördü de aynı)

*«hava durumu nasıl»* → `source=llm:openrouter` · `cube=adhoc` · **1 satır**:

    tur 1-2:  {"mesaj": "Hava durumu ile ilgili veri bulunmamaktadır."}
    tur 3-4:  {"1": 1}

İkisi de **uydurma**: satır küpten değil **modelden** geliyor. `§38.4`'ün değişmezi
açık — *sayıyı küp koyar*.

## Neden mevcut guard'lar göremedi

| guard | ne sorar | `SELECT 1`'e cevabı |
|---|---|---|
| `guard_sql` | salt-okuma mu, tek ifade mi | ✅ geçer |
| `dry_plan` | motor bunu planlayabilir mi | ✅ geçer (planlanacak bir şey yok) |
| `katman_b` | modele erişim yetkisi var mı | ✅ geçer (model yok) |

⊙ **Dürüst red yolu ZATEN VARDI** (`soz.py`: *«Bu soru için güvenilir bir sorgu
üretemedim»*) — bazı turlarda gerçekten o çalıştı. Model onu **sözdizimsel olarak
geçerli bir SELECT yazarak** atlıyordu.

> *Bir reddin kapısı, reddedilmek istenen şeyin o kapıdan geçebildiği yerde
> kurulmuşsa, kapı değil bir geçittir.*

## ⚠ Ve bu, raporun kendi FARKLILAŞMA iddiasının test edilmemiş yarısıydı

Rapor (`§1232`): *«dbt'nin cümlesi: semantik katmanda başarısızlık bir HATA MESAJIDIR.
Power BI kapsam dışında **uyduruyor** — biz **söylüyoruz**.»* Ölçüm bu iddianın
Discovery yolunda **karşılıksız** olduğunu gösterdi: biz de bir satır üretiyorduk,
yalnız içi boştu.

*Bir farklılaşmayı ilan etmek, onu ölçmeden korumaz.*
"""

from __future__ import annotations

import pytest

from app.wren_service import veriye_dokunmuyor

#: 🔴 Canlıda **gerçekten ölçülmüş** iki biçim + gramerin aynı sınıfa soktuğu üçü.
#: Liste kapalı: her kalem ya canlı bir turdan ya da SQL gramerinden gelir — bir
#: dilek listesi değil.
DOKUNMAYAN = [
    "SELECT 1",                                              # canlı tur 3-4
    "SELECT 'Hava durumu ile ilgili veri bulunmamaktadır.' AS mesaj",   # canlı tur 1-2
    "SELECT 1 AS x, 'y' AS z",
    "WITH t AS (SELECT 1 AS a) SELECT * FROM t",             # CTE gerçek tablo DEĞİL
    "SELECT NOW()",
]

#: Gerçek bir tabloya dokunanlar — **hiçbiri** susturulmamalı.
DOKUNAN = [
    "SELECT * FROM faturalar",
    "SELECT SUM(tutar) FROM ticaret WHERE tur = 'satis'",
    "WITH t AS (SELECT * FROM faturalar) SELECT COUNT(*) FROM t",
    'SELECT a.x FROM "parti" a JOIN oee b ON a.id = b.id',
    "SELECT 1 FROM faturalar",                               # sabit seçim ama TABLO var
]


@pytest.mark.parametrize("sql", DOKUNMAYAN)
def test_VERIYE_DOKUNMAYAN_sorgu_YAKALANIR(sql):
    """🔴 Kusurun ta kendisi: bunların hiçbiri bir cevap değildir."""
    assert veriye_dokunmuyor(sql) is True, f"kaçtı: {sql}"


@pytest.mark.parametrize("sql", DOKUNAN)
def test_GERCEK_SORGU_susturulmaz(sql):
    """⚠ `§101.1` — bir yanlış pozitifin bedeli kusurun kendisinden ağırdır. Meşru bir
    Discovery cevabını kesmek, kapsam dışı bir satırı basmaktan **daha pahalıdır**."""
    assert veriye_dokunmuyor(sql) is False, f"meşru sorgu susturuldu: {sql}"


def test_CTE_ADI_gercek_tablo_SANILMAZ():
    """`WITH t AS (SELECT 1) SELECT * FROM t` — `t` bir tablo referansı gibi görünür ama
    **kendi sorgusunun içinde tanımlıdır**. CTE adlarını düşmeyen bir sürüm bu kusuru
    kaçırırdı; ve `SELECT * FROM t` kullanıcının gördüğü satırı yine uydururdu."""
    assert veriye_dokunmuyor("WITH t AS (SELECT 1 AS a) SELECT * FROM t") is True
    assert veriye_dokunmuyor(
        "WITH t AS (SELECT * FROM faturalar) SELECT * FROM t") is False


def test_AYRISTIRILAMAYAN_sql_FAIL_OPEN():
    """⚠ Bilinçli **fail-open**: bu bir güvenlik kapısı değil bir **içerik** kapısıdır.

    Reddi güvenlik guard'ları (`guard_sql` · `dry_plan` · `katman_b`) zaten veriyor.
    Ayrıştırma hatasında susturmak, ayrıştırıcının anlamadığı **geçerli** bir cevabı
    kesmek olurdu. Anlaşılmayan SQL zaten `dry_plan`'a çarpar."""
    assert veriye_dokunmuyor(")))) bu SQL değil ((((") is False
    assert veriye_dokunmuyor("") is False


def test_KURAL_ASK_YOLUNA_BAGLI():
    """🔴 Yazılıp çağrılmayan bir kural, yazılmamış bir kuraldır."""
    import pathlib

    kaynak = (pathlib.Path(__file__).parent.parent
              / "app" / "routers" / "ask.py").read_text(encoding="utf-8")
    assert "kapsam_disi_reddi" in kaynak, (
        "🔴 kapsam kuralı `ask.py`'de ÇAĞRILMIYOR — kural yazıldı ama bağlanmadı.")
    i = kaynak.index("kapsam_disi_reddi")
    assert "_honest_refusal" in kaynak[i:i + 400], (
        "kural çağrılıyor ama DÜRÜST REDDE bağlanmamış — bir tespit, sonucu yoksa "
        "bir gözlemdir.")


def test_KURAL_ONARIMDAN_SONRA_kosuyor():
    """🔴🔴 **YERİN KENDİSİ BİR ÖLÇÜMDÜ — ve ilk yazım YANLIŞ YERDEYDİ.**

    İlk sürüm kuralı SQL'in **üretildiği** yere koydu. Hedefli testler yeşildi, kapı
    yeşildi — ama **canlı curl** onu çürüttü: uydurma satır gelmeye devam etti. İz
    sebebi söyledi:

        Discovery: ham-SQL üretimi (Intent-path kapsamadı)
        dry_plan hatası → kendi kendini onarma: Yalnızca SELECT/WITH sorgularına izin verilir.
        Discovery: dry_plan geçti, çalıştırılıyor…
        → SQL: SELECT 'Hava durumu verisi mevcut degildir.' AS mesaj;

    Yani uydurma SQL **üretimden değil ONARIMDAN** (`llm.repair`) doğuyordu ve
    onarılan SQL bir daha denetlenmiyordu. Kural, doğumun **bir** yolunun yanına
    konmuştu; oysa iki yol vardı.

    > *Bir kuralı doğuşun yanına koymak, doğumun tek yolunun o olduğunu varsaymaktır.*

    ⊙ Bu, bu oturumun **1 numaralı** dersinin (*«ulaşılamayan katmana konan kural →
    canlı curl ile doğrula»*) bir kez daha ödenmesidir; ve `§YV`'de olduğu gibi
    çürüten şey yine **süit değil canlı** oldu.

    Bu test yeri kilitler: kural `llm.repair` çağrısından **sonra** koşmalı.
    """
    import pathlib

    kaynak = (pathlib.Path(__file__).parent.parent
              / "app" / "routers" / "ask.py").read_text(encoding="utf-8")
    # 🔴🔴 **HER onarım denetlenmeli — SAYARAK ölç, ilk oluşuma bakma.**
    #
    # ⚠ İlk sürümüm `kaynak.index(...)` ile **ilk** `llm.repair`i alıyordu ve dosyadaki
    # **İKİNCİ** onarımı (çalıştırma hatası dalı, `ask.py:~5300`) yapısal olarak
    # göremiyordu. Bir denetim ajanı bunu bağımsız olarak buldu: o dalda kapsam
    # denetimi **yoktu** ve uydurma SQL `motor.query`ye kadar gidiyordu.
    #
    # ⊙ Yani hem kod hem kapı aynı varsayımı paylaşıyordu: *«tek bir onarım var»*.
    # *Bir kapı, ölçtüğü şeyin KAÇ TANE olduğunu saymıyorsa, ikincisini hiç görmez.*
    onarimlar = [i for i in range(len(kaynak))
                 if kaynak.startswith("llm.repair(body.question", i)]
    kurallar = [i for i in range(len(kaynak))
                if kaynak.startswith("kapsam_disi_reddi", i)]
    assert onarimlar, "⊘ ölçüm tabanı çöktü: `llm.repair` çağrısı bulunamadı"
    # Her onarımdan SONRA (ve bir sonraki onarımdan önce) bir kapsam denetimi olmalı.
    for i, o in enumerate(onarimlar):
        sinir = onarimlar[i + 1] if i + 1 < len(onarimlar) else len(kaynak)
        assert any(o < k < sinir for k in kurallar), (
            f"🔴 {i + 1}. `llm.repair` (offset {o}) sonrası kapsam denetimi YOK — "
            "onarımın ürettiği SQL denetimsiz kalır ve kusur birebir geri gelir "
            "(canlı curl ile ölçüldü, ve ikinci onarım bir denetim ajanıyla bulundu).")
