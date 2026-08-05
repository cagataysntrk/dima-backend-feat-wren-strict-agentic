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

from app.tools import Arac

#: 🔴 `yan_etki="yazar"` ile kayda giren **ilk** araçlar. Üçü de:
#:   · `izin` — `authorize()` matrisinde **var olan** bir aksiyon (yeni izin icat YOK),
#:   · `geri_alma_ref` — geri alınabilirse **yolu**, değilse `None` (**açıkça**),
#:   · `notlar` — *ne zaman KULLANILMAZ* (6.3'ün dört bileşenli `ozet` disiplininin
#:     habercisi; yanlış-araç-seçimi karşı önlemi).
YAZMA_KAYIT: tuple[Arac, ...] = (
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
        izin="query:run",
        makbuz=None,
        modul="app.routers.dashboards",
        fonksiyon="add_widget",
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
        izin="schedule:create",
        makbuz=None,
        modul="app.routers.schedules",
        fonksiyon="create_schedule",
        # 🔴 **GERİ ALINAMAZ — ve bu GİZLENMİYOR.** Zamanlama kaydı silinebilir ama
        # gönderilmiş bir bildirim geri çekilemez: dışarıya çıkmış bir e-posta,
        # sistemin sınırının dışındadır.
        geri_alma_ref=None,
        notlar="🔴 GERİ ALINAMAZ: kayıt silinse bile GÖNDERİLMİŞ bildirim geri "
               "çekilemez. D9 gereği HER ZAMAN senkron onay ister (FAZ 6.1). Periyot "
               "söylenmemişse araç ÇAĞRILMAZ — sorulur.",
        etiketler=("yazma", "zamanlama"),
    ),
    Arac(
        ad="measures.approve",
        ozet="Terfi kuyruğundaki bir ölçü adayını onaylar (kataloğa girer). "
             "[Erişim: tenant'ın metrik kataloğu] "
             "[Ne zaman: bir incelemeci adayı değerlendirip karar verdiğinde] "
             "[NE ZAMAN KULLANILMAZ: ajanın kendi başına 'iyi görünüyor' demesiyle; "
             "değerlendirilmemiş adaylar için]",
        girdi={"candidate_id": "aday kimliği"},
        cikti="onaylanan adayın yeni durumu",
        determinizm="deterministik",
        maliyet="ucuz",
        yan_etki="yazar",
        izin="measure:approve",
        makbuz=None,
        modul="app.routers.measures",
        fonksiyon="approve_candidate",
        # Onay geri alınabilir: aday `deprecated`e çekilir (kayıt silinmez, ADR-0019).
        geri_alma_ref="measures.deprecate",
        notlar="Yalnız ONAY AKIŞI üzerinden. ⚠ Bir ölçüyü kataloğa almak, onu HER "
               "kullanıcının sorusuna açar — kapsamı bir panodan geniştir ve bu yüzden "
               "D9'un 'kapsam içi' şartını KARŞILAMAZ: her zaman istem üretir.",
        etiketler=("yazma", "terfi"),
    ),
)


def geri_alinamaz_olanlar() -> list[str]:
    """`geri_alma_ref` taşımayan yazma araçları — **kullanıcıya gösterilecek liste**.

    *Geri alınamazlığı gizlemek, onu geri alınabilir sanmaktan kötüdür.*
    """
    return [a.ad for a in YAZMA_KAYIT if not a.geri_alma_ref]
