"""FAZ 6.2 — **YAZMA ARAÇLARI: `yan_etki="yazar"` ile kayıtlı İLK araç sınıfı.**
[bayrak: `yazma_araclari` — `Settings`, feature-flag değil]

> **Karar kaydı:** MIMARI §4 değişmez 2/3 (read-only) — ve bu modül o değişmezi
> **gevşetmez, kademelendirir**.

## 🔴 BUGÜNE KADAR KAYITTA **SIFIR** YAZAN ARAÇ VARDI — ve bu bilinçliydi

`app/tools.py`'nin kendi notu: *"`dashboards.create` / `schedules.create` /
`measures.approve` → `yan_etki="yazar"`. Ajanın yazma yetkisi **ayrı bir mimari
karardır**."* Bu modül o kararı verir ve **üç şartla** verir.

## Üç şart — üçü de kapılı

| şart | neden |
|---|---|
| **Yalnız `onay_akisi` üzerinden çağrılabilir** | doğrudan çağrı, onayı bir **süs** yapardı |
| **Her araç `geri_alma_ref` taşır** | geri alınamazsa `None` — ve bu **açıkça** işaretlidir |
| **Bayrak kapalıyken kayda HİÇ girmez** | *geri alma "kapatmak" değil **hiç açmamaktır*** |

## 🔴 GERİ ALINAMAZLIK GİZLENMEZ

`schedules.create` bir kez koştuğunda **dışarıya e-posta çıkar** ve gönderilmiş bir
bildirim geri çekilemez. `geri_alma_ref=None` bunu **söyler** ve onay kartı onu
kullanıcıya **gösterir**.

> *Geri alınamazlığı gizlemek, onu geri alınabilir sanmaktan kötüdür: kullanıcı bir daha
> hiç sormaz.*

## ⚠ Bu modül YENİ BİR UÇ AÇMAZ

Üç aracın üçü de **kullanıcının kendi eliyle çağırabileceği** var olan uçları gösterir.
*"Güvenlik imzadan değil, yetki yüzeyinin genişlememesinden geliyor"* — ve yüzey burada
**genişlemiyor**, yalnız **ajana görünür** hâle geliyor.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:                                  # pragma: no cover
    from app.tools import Arac

#: 🔴🔴 **ARAÇ ↔ EYLEM BAĞLAMASI** *(`§F13` açık yarısı, 2026-08-12)*.
#:
#: ## Ölçülen kusur — `§C1`'in İKİNCİ VAKASI
#:
#: Aynı üç yazma işi **iki kayıtta** ayrı ayrı beyan ediliyordu ve ad örtüşmesi
#: **SIFIR**dı:
#:
#:     EYLEM_KAYIT (`/ask/eylem`, ÇALIŞAN onay yolu)
#:         pano.ekle · zamanla.olustur · tercih.kaydet     [alanlar: izin · uc · geri_alinabilir]
#:     YAZMA_KAYIT (ajanın araç kaydı)
#:         dashboards.create · schedules.create · measures.approve
#:
#: Ve **aynı gerçekler iki kez** yazılıydı: `pano.ekle.uc = "dashboards.add_widget"`
#: ile aracın `modul="app.routers.dashboards"` + `fonksiyon="add_widget"`'i **aynı
#: hedefi** gösteriyordu; `geri_alinabilir=True` ile `geri_alma_ref="…remove_widget"`
#: **aynı olguyu**. Bugün tutarlılar — ama iki sahip **ayrışır**, ve bu deponun bir
#: numaralı kusur sınıfı tam olarak budur (`KAT-1`).
#:
#: ⊙ Ve *«aranan adaptör»* zaten oradaydı: `EylemBeyani.uc`. `FAZ H` bir **yeni katman**
#: değil, bir **bağlama** işiydi.
#:
#: ## Kural: eylemi olan araç ondan TÜRER
#:
#: `izin` · `modul` · `fonksiyon` · `geri_alma_ref` artık **eylem beyanından** okunur.
#: Araca özgü kalan tek şey **anlatım**dır (`ozet` · `girdi` · `notlar`) — yani LLM'e
#: *ne zaman kullanılır / kullanılmaz* diyen kısım.
#:
#: 🔴 `KURAL B`: bayrak kapalıyken kayıt bugünküyle **birebir aynı** (araçlar hiç
#: girmez); açıkken de türetilen alanlar elle yazılmış değerlerle **bayt bayt** aynı
#: çıkar — `test_f13_onayli_yazma.py` bunu kilitler.
#:
#: ⚠ **`measures.approve` KAYITTAN ÇIKARILDI** — ve bu bir eksiklik değil bir karar:
#: `/ask/eylem`'in kaydında karşılığı **YOK** (`beyan()` fail-closed → 400). Yani ajan
#: onu önerse kullanıcı **onaylayamazdı**. *Onay yolu olmayan bir öneri, bir öneri
#: değil bir çıkmazdır.* Eklenmesi `EYLEM_KAYIT`'a yeni bir eylem yazmayı gerektirir ve
#: o, `/ask/eylem`'in kabul kümesini değiştirir — ayrı bir karar, ayrı bir ölçüm.

#: `araç adı → eylem adı`. **Kapalı** ve her kalem `EYLEM_KAYIT`'ta **var olmalı**
#: (kapı doğrular): olmayan bir eylemi işaret eden araç, çıkmaz bir öneri üretirdi.
ARAC_EYLEM: dict[str, str] = {
    "dashboards.create": "pano.ekle",
    "schedules.create": "zamanla.olustur",
}


def _eylemden(arac_adi: str) -> dict:
    """Eylem beyanından türeyen alanlar — **tek sahip `app/eylem.py`**."""
    from app import eylem as _e

    b = _e.beyan(ARAC_EYLEM[arac_adi])
    modul, _, fonksiyon = b.uc.rpartition(".")
    return {"izin": b.izin, "modul": f"app.routers.{modul}", "fonksiyon": fonksiyon}


def _kurul() -> tuple["Arac", ...]:
    """Kaydı **çağrı anında** kurar.

    ⚠ Modül düzeyinde `from app.tools import Arac` yazmak **dairesel import** üretiyordu
    (ölçüldü 2026-08-12): `tools.py:643` kaydı kurarken bu modülü çağırıyor, bu modül de
    `tools`'u import ediyordu. Uygulama yolunda `tools` önce geldiği için görünmüyordu —
    yani kırılganlık **import sırasına** bağlıydı ve bir gün başka bir çağıran onu
    ortaya çıkaracaktı. *Yalnız bir sıralama sayesinde çalışan bir şey, çalışmıyor
    demektir; henüz sırası gelmemiştir.*
    """
    from app.tools import Arac

    return (
    Arac(
        ad="dashboards.create",
        ozet="Bir raporu kullanıcının kendi panosuna widget olarak ekler. "
             "[Erişim: kullanıcının KENDİ panosu] "
             "[Ne zaman: kullanıcı bir raporu sabitlemek istediğinde] "
             "[NE ZAMAN KULLANILMAZ: başkasının panosuna; paylaşılan/kurumsal panolara; "
             "kullanıcı istemeden 'faydalı olur' diye]",
        girdi={"title": "widget başlığı", "cube_query": "doğrulanmış CubeQuery (JSON)"},
        cikti="oluşturulan widget kimliği",
        determinizm="deterministik",
        maliyet="ucuz",
        yan_etki="yazar",
        makbuz=None,
        **_eylemden("dashboards.create"),
        # 🔴 GERİ ALINABİLİR: widget soft-delete ile kaldırılır (ADR-0019).
        geri_alma_ref="dashboards.remove_widget",
        notlar="Yalnız ONAY AKIŞI üzerinden çağrılabilir; doğrudan çağrı onayı bir SÜS "
               "yapardı. Kapsam içi + geri alınabilir olduğu için D9 gereği istem "
               "ÜRETMEDEN koşabilir (FAZ 6.0).",
        etiketler=("yazma", "pano"),
    ),
    Arac(
        ad="schedules.create",
        ozet="Bir raporu düzenli aralıklarla e-posta/bildirim olarak gönderir. "
             "[Erişim: kullanıcının KENDİ zamanlamaları + teslim kanalları] "
             "[Ne zaman: kullanıcı açıkça bir periyot söylediğinde] "
             "[NE ZAMAN KULLANILMAZ: periyot söylenmemişse (SOR, uydurma); tek seferlik "
             "bir gönderim için; başkası adına]",
        girdi={"label": "zamanlama etiketi", "cube_query": "doğrulanmış CubeQuery (JSON)",
               "every": "hour | day | week", "at": "HH:MM (saatlik hariç)"},
        cikti="oluşturulan zamanlama kimliği",
        determinizm="deterministik",
        maliyet="ucuz",
        yan_etki="yazar",
        makbuz=None,
        **_eylemden("schedules.create"),
        # 🔴 **GERİ ALINAMAZ — ve bu GİZLENMİYOR.** Zamanlama kaydı silinebilir ama
        # gönderilmiş bir bildirim geri çekilemez: dışarıya çıkmış bir e-posta,
        # sistemin sınırının dışındadır.
        geri_alma_ref=None,
        notlar="🔴 GERİ ALINAMAZ: kayıt silinse bile GÖNDERİLMİŞ bildirim geri "
               "çekilemez. D9 gereği HER ZAMAN senkron onay ister (FAZ 6.1). Periyot "
               "söylenmemişse araç ÇAĞRILMAZ — sorulur.",
        etiketler=("yazma", "zamanlama"),
    ),
    # ⊘ **`measures.approve` BURADA YOK — ve bu bir KARARDIR** (2026-08-12).
    #
    # `/ask/eylem`'in kaydında (`EYLEM_KAYIT`) karşılığı **yok**: `beyan()` fail-closed
    # olduğu için kullanıcı onu **onaylayamaz** (400). Yani ajan onu önerse, kullanıcı
    # önerinin karşısında hiçbir şey yapamazdı.
    #
    # > *Onay yolu olmayan bir öneri, bir öneri değil bir çıkmazdır.*
    #
    # ⚠ Ve bu bir "sonra ekleriz" değil: eklemek `EYLEM_KAYIT`'a yeni bir eylem yazmayı
    # gerektirir ve o, `/ask/eylem`'in **kabul kümesini** değiştirir — ayrı bir karar,
    # ayrı bir ölçüm. Ölçü de yazılı: `measure:approve` bir ölçüyü **kataloğa** alır,
    # yani kapsamı bir panodan geniştir (aracın kendi eski notu).
)


#: Kayıt **çağrı anında** kurulur (dairesel import gerekçesi `_kurul`'da yazılı).
YAZMA_KAYIT: tuple["Arac", ...] = _kurul()


def geri_alinamaz_olanlar() -> list[str]:
    """`geri_alma_ref` taşımayan yazma araçları — **kullanıcıya gösterilecek liste**.

    *Geri alınamazlığı gizlemek, onu geri alınabilir sanmaktan kötüdür.*
    """
    return [a.ad for a in YAZMA_KAYIT if not a.geri_alma_ref]
