"""**SERTİFİKA OKUMA** — B8'in kayıtla cevabı buluşturan halkası.
[bayrak: `metrik_sertifikasi`]

## 🔴 Ölçüm yol haritasını DÜZELTTİ

FAZ 7.3(k) *"sarı drift bandı — **B8'in TEK kullanıcı-görünür yüzeyi**; arkası kurulu,
önü yoktu"* diyordu. Ölçüldü ve **arkası da kurulu değildi**:

| parça | var mı | bağlı mı |
|---|---|---|
| `MetrikSertifikasi` tablosu (`control_plane/models.py`) | ✅ | 🔴 **hiçbir okuyucu yok** |
| `app/certification.py` (`durum` · `rozet_kademesi`) | ✅ 12 test | 🔴 **hiçbir çağıran yok** |
| `AskResponse.sertifika` alanı (`schemas.py`) | ✅ | 🔴 **hiçbir dolduran yok** |
| `sertifikaRozeti()` (`ChatPanel.tsx`) | ✅ | 🔴 **hiç veri gelmiyor** |

Dört parça da **ayrı ayrı doğru**, ve **hiçbiri diğerine dokunmuyor**. Bu, bu deponun
en pahalı kusur sınıfının en büyük örneği: *"beyan var, kod onu tanımıyor"* — ve burada
**dört kez** üst üste.

> 🔴 *Bir zincirin her halkasını ayrı ayrı test etmek, zinciri test etmek değildir.*

## Neden `ask()` içine yazılmadı

`ask()` tavanı **1150/1151** — boşluk **1 satır**. Bir çağrı eklemek tavanı aşardı.
Ve zaten doğru ev burası değildi: sertifika bir **mühürleme** kararıdır (cevap
tamamlandıktan sonra okunur), `seal()`'in `_maybe_interpret`/`_build_explain` ile aynı
sırada durur.

## ⚠ Metrik referansı NASIL çözülür — ve neden ilk ölçü

Bir cevap birden çok ölçü taşıyabilir. Sertifika **ilk ölçüden** okunur çünkü rozet
**cevabın tamamı** hakkındadır ve *"üç ölçüden ikisi sertifikalı"* diye bir rozet
kullanıcıya hiçbir karar verdirmez.

🔴 **Ama bu bir kayıp değil, bir SINIR** ve yazılı: çok ölçülü bir cevapta sertifika
**en zayıf** halkayı göstermeli. Bugün ilk ölçüyü gösteriyor; `KISIT_COK_OLCU` bunu
kayda geçiriyor ki bir gün *"rozet yanlış"* denildiğinde sebep aranmasın.
"""

from __future__ import annotations

from typing import Any

from app import certification
from app.logging_setup import get_logger

_log = get_logger("ask")

#: ⚠ **Bilinen sınır** — çok ölçülü cevapta sertifika **ilk** ölçüden okunur.
#: Doğrusu *"en zayıf halka"*dır ve o, ölçü başına ayrı okuma + birleştirme kuralı ister.
#: *Bir sınırı yazmadan bırakmak, onu bir hataya çevirir.*
KISIT_COK_OLCU = ("çok ölçülü cevapta sertifika ilk ölçüden okunur; "
                  "doğrusu en zayıf halkadır")


def metrik_ref(cube_query: dict[str, Any] | None) -> str | None:
    """`cube_query` → `"<cube>.<ölçü>"`. Cube ya da ölçü yoksa **`None`** — ve bu
    bilinçli: uydurma bir referans, olmayan bir sertifikayı *"bulunamadı"* diye
    gösterirdi ve o, *"hiç sertifikalanmamış"*tan farklı okunurdu."""
    if not isinstance(cube_query, dict):
        return None
    cube = cube_query.get("cube")
    olculer = cube_query.get("measures") or []
    if not isinstance(cube, str) or not olculer:
        return None
    ilk = olculer[0]
    return f"{cube}.{ilk}" if isinstance(ilk, str) else None


def kayittan_oku(oturum, tenant_id, ref: str) -> dict[str, Any] | None:
    """`metrik_sertifikasi` tablosundan tek satır. Yoksa `None`.

    ⚠ `tenant_id` **zorunlu**: sertifika tenant'a aittir ve onsuz bir okuma, başka bir
    şirketin onayını bu şirkete gösterirdi.
    """
    from sqlmodel import select

    from control_plane.models import MetrikSertifikasi

    if not tenant_id or not ref:
        return None
    satir = oturum.exec(
        select(MetrikSertifikasi)
        .where(MetrikSertifikasi.tenant_id == tenant_id)
        .where(MetrikSertifikasi.metric_ref == ref)
    ).first()
    if satir is None:
        return None
    return {
        "seviye": satir.seviye,
        "definition_hash": satir.definition_hash,
        "lineage_set_hash": satir.lineage_set_hash,
        "son_gecerlilik": satir.son_gecerlilik,
        "otomatik_iptal_nedeni": satir.otomatik_iptal_nedeni,
    }


def blok(sertifika: dict[str, Any] | None, *, tanim: str | None = None,
         koken: str | None = None) -> dict[str, Any] | None:
    """Kayıt + bugünkü parmak izleri → `AskResponse.sertifika` gövdesi.

    🔴 **Çürüyen sertifika SİLİNMEZ**: `certification.durum()` seviyeyi korur ve üstüne
    `yeniden_dogrulama_gerekli` bayrağı düşürür. *"Hiç sertifikalanmamış"* ile
    *"sertifikalanmış ama tanım değişmiş"* farklı şeylerdir — ve ikincisi kullanıcı için
    **daha bilgilendiricidir**, çünkü bir zamanlar onaylanmış bir şeyin değiştiğini söyler.

    ⚠ `kademe` **burada** hesaplanır, frontend'de değil: rozet kademesi bir **karardır**
    ve iki sahibi olursa ayrışır. Frontend yalnız **gösterir**.
    """
    d = certification.durum(sertifika, tanim=tanim, koken=koken)
    if d is None:
        return None
    return {**d, "kademe": certification.rozet_kademesi(d), "kisit": KISIT_COK_OLCU}
