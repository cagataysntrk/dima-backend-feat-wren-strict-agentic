r"""🔴🔴 `§S06` — **SORULAN SORU, EKSİK OLAN ŞEYLE UYUŞMUYORDU.**

## Canlıda ölçülen (curl, 2026-08-12) — *«bu ay açılan partileri listele»*

```
note           : «Hangi KIRILIMI istiyorsun?»
diyalog_durumu : {"acik_slotlar": ["olcu"],
                  "kismi_cq": {"cube":"parti",
                               "dimensions":["makine","renk","musteri"],
                               "measures":[]}}          ← KIRILIM ZATEN ÜÇ TANE
next_steps     : [+ ortalama hız (measure)] [+ fire (measure)] …   ← chip'ler ÖLÇÜ sunuyor
```

**Chip'ler doğruydu, soru yanlıştı.** Sistem elinde üç kırılım varken *«hangi kırılım»*
diye soruyor, eksik olan **ölçü**yü sormuyordu. Kullanıcı sorulan soruyu **cevaplayamaz**
— cevabı zaten sorgunun içinde.

⚠ **Teşhisim iki kez daraldı:** önce *«chip yok»* dedim (yanlış alana baktım —
`suggestions` yerine `next_steps` ⑤), sonra *«chip'ler yanlış»* dedim (yanlıştı — chip'ler
**doğruydu**). Ölçüm ikisini de çürüttü ㉚.

## 🆃 İki ölçüt zıt yöne gidiyordu

| kaynak | neyi söyler | bu vakada |
|---|---|---|
| `eksen` | garsonun **örnekleri arasındaki** ayrışma (self-consistency %67) | `dimensions` |
| `diyalog.acik_slotlar` | **sorgunun kendisinde** neyin boş olduğu | `olcu` |

İkincisi **veriyi** okur, birincisi **oyları** — ve kullanıcının gördüğü şey **eksik
olandır**. İkinci bir yuva çözümleyicisi yazılmadı (`KAT-1`): `diyalog.acik_slotlar`
**tek sahiptir**, burada yalnız **çağrılıyor**; `eksen` **yedek** olarak duruyor.
"""

from __future__ import annotations


def test_OLCUM_TABANI_SLOT_COZUMLEYICI_CALISIYOR():
    """⊘ **Boş yeşil avı.** `acik_slotlar` bu vakayı görmüyorsa düzeltmenin dayanağı yok."""
    from app import diyalog

    cq = {"cube": "parti", "dimensions": ["makine", "renk"], "measures": []}
    assert diyalog.SLOT_OLCU in diyalog.acik_slotlar(cq), (
        f"⊘ ölçüm tabanı: ölçüsüz sorguda `olcu` açık sayılmıyor — "
        f"{diyalog.acik_slotlar(cq)}")
    assert diyalog.SLOT_OLCU not in diyalog.acik_slotlar(
        {"cube": "parti", "measures": ["toplam_ciro"]}), (
        "⊘ ölçüm tabanı: ölçü VARKEN de açık sayılıyor — yüklem ayırt etmiyor")


def test_SORU_EKSIK_OLAN_SLOTTAN_TURUYOR():
    """🔴🔴 **ASIL KAPI.** Üç kırılımı olan ama **ölçüsü olmayan** bir adayda soru
    *«hangi ölçü»* olmalı — `eksen` *«dimensions»* dese bile.

    ⚠ İlk kapım yalnız *«`acik_slotlar` çağrılıyor mu»*yu sınıyordu ve **mutasyon
    ısırmadı** (çağrı duruyor, karar bozuk). Yüklemi taşıyan yer modül düzeyine
    ayrıldı ki **davranış** sınansın 🅯.
    """
    from app.routers.ask import netlestirme_sorusu

    adaylar = [{"cube": "parti", "dimensions": ["makine", "renk", "musteri"],
                "measures": []}]
    assert netlestirme_sorusu(adaylar, "dimensions") == "Hangi ölçüyü istiyorsun?", (
        "🔴 SORULAN SORU EKSİK OLANLA UYUŞMUYOR: adayda üç kırılım var, ölçü YOK — "
        "yine de «hangi kırılım» diye soruluyor. Kullanıcı cevabı zaten sorgunun "
        "içinde olan bir soruyu cevaplayamaz 🆃.")


def test_YEDEK_YOL_KORUNDU_EKSEN_HALA_OKUNUYOR():
    """⚠ **`KURAL B` kenarı.** Yuva analizi bir şey söylemezse (ör. yalnız küp ayrışmış)
    eski davranış **birebir** kalmalı — düzeltme bir **daraltma** değil bir **öncelik**
    eklemesidir. 🆊 *Her şeyi işaretleyen bir ölçüt hiçbir şeyi işaretlemez.*"""
    import inspect

    from app.routers import ask

    kaynak = inspect.getsource(ask)
    assert '"dimensions": "Hangi kırılımı istiyorsun?"' in kaynak, (
        "🔴 `eksen` yedeği SİLİNMİŞ — yuva analizi susarsa soru metni kalmaz.")
    assert "Hangisini istiyorsun?" in kaynak, (
        "🔴 son çare metni silinmiş — bilinmeyen eksende soru boş kalır.")


def test_SLOT_SIRASI_ANLAMLI_KUP_OLCUDEN_ONCE():
    """⚠ ㊴ **Şartın yeri.** `acik_slotlar` sırayı *(cube → ölçü → dönem)* garanti eder;
    soru **ilk** açık slottan türüyor. Küp de ölçü de boşsa sorulacak şey **küptür** —
    ölçüyü sormak, hangi küpün ölçüsü olduğu bilinmeden anlamsızdır."""
    from app import diyalog

    acik = diyalog.acik_slotlar({})
    assert acik and acik[0] == diyalog.SLOT_CUBE, (
        f"🔴 slot sırası bozuldu: {acik} — soru yanlış yuvadan türer.")
