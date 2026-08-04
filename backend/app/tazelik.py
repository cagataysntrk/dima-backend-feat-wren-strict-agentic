"""FAZ 1.7 — **TAZELİK MERDİVENİ.** *"Bu sayı ne kadar eski?"*

## Ölçülen boşluk

`grep -rl freshness backend/app/` → **0**. `SyncState.last_synced_at` **yalnız admin klon
yolunda** (`admin_app/routers/clone.py:203`) ve `/ask`'e **hiç ulaşmıyor**. Kullanıcı
*"8 gündür veri gelmiyor"*u **göremiyor** — ve *"bu sayı neden düşük?"* sorusunun **en sık
gerçek cevabı** tam olarak budur.

## 🔴 B4 — BİLİNMEYEN TAZELİK, TAZE DEĞİLDİR

Dört kademe var ama **üçü aynı sonucu doğurur**:

| kademe | anlamı | sayı gösterilir mi |
|---|---|---|
| `taze` | eşiğin altında | ✅ işaret bile yok |
| `uyari` | `warn_after` aşıldı | ✅ **ama** görsel uyarıyla |
| `hata` | `error_after` aşıldı | 🔴 **HAYIR** |
| `bilinmiyor` | ölçülemedi | 🔴 **HAYIR** — `hata` ile **aynı** muamele |

`bilinmiyor`'u `taze` saymak, ölçemediğimiz bir şeyi **iyi** varsaymaktır; bu belgenin
`⊘ ÖLÇÜLEMEDİ` üçüncü hâlinin tam tersi olurdu. Kaynak planlar bunun **tersini**
yazmıştı ve yol haritası bunu *"bugünkü davranıştan **kasıtlı bir sertleşme**"* diye
düzeltti — burada o düzeltme uygulanıyor.

## 🔴 TEK SAYI YAPILANDIRILIR, İKİ EŞİK TÜRETİLİR

`warn_after` ve `error_after` **ayrı ayrı** ayarlanabilseydi biri ötekini geçebilirdi
(`warn=10g`, `error=3g`) ve merdiven **anlamsızlaşırdı** — bir kullanıcı `uyari`'yı hiç
görmeden `hata`'ya düşerdi. Yapılandırılan tek şey **beklenen periyottur**; eşikler
**2×** ve **5×** olarak ondan türer. *Çelişebilen iki ayar, çelişecek demektir.*

## ⚠ KAYNAK: `SyncState.last_synced_at` — ve neden zaman boyutunun `max()`'ı DEĞİL

Yol haritası ikisini birden anıyor. Ölçüm kararı: `last_synced_at` **indeksli tek bir
satır okumasıdır**; zaman boyutunun `max()`'ı **her soruda ek bir DB sorgusu** demektir
ve FAZ 0.17'nin gecikme bütçesi tam bunun için kuruldu.

⚠ **İkisi aynı şey DEĞİL ve alan adı bunu gizlememeli:** `last_synced_at` *"boru hattı en
son ne zaman çalıştı"*, zaman boyutunun `max()`'ı *"veri en son ne zamana ait"* der. Boru
hattı çalışıp **boş** dönebilir. Keskin sinyal ikincisidir ama bedeli ölçülmeden
alınmaz — o karar `1.7`'nin kuyruğunda, **uydurulmadan** duruyor.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

#: Dört kademe. Sıra **kötüleşen** — `en_kotu()` bunu kullanır.
KADEMELER = ("taze", "uyari", "hata", "bilinmiyor")

#: Beklenen senkron periyodunun varsayılanı (saat). Tek yapılandırılan sayı budur.
VARSAYILAN_PERIYOT_SAAT = 24

#: Eşikler periyottan **türer** — ayrı ayrı ayarlanamaz (çelişemezler).
UYARI_CARPANI = 2
HATA_CARPANI = 5

#: 🔴 Sayı gösterilmeyen kademeler. `bilinmiyor` burada ve bu **B4'ün kendisidir**.
SAYI_GIZLENEN = ("hata", "bilinmiyor")


def esikler(periyot_saat: int | None) -> tuple[timedelta, timedelta]:
    """`(uyari_esigi, hata_esigi)` — **tek** sayıdan türer.

    `None`/geçersiz → varsayılan. Sıfır ya da negatif bir periyot **anlamsızdır** ve
    varsayılana düşer: `0` kabul etseydik her cevap anında `hata` olurdu.
    """
    p = periyot_saat if isinstance(periyot_saat, int) and periyot_saat > 0 \
        else VARSAYILAN_PERIYOT_SAAT
    return timedelta(hours=p * UYARI_CARPANI), timedelta(hours=p * HATA_CARPANI)


def kademe(son_senkron: datetime | None, *, periyot_saat: int | None = None,
           simdi: datetime | None = None) -> str:
    """Tazelik kademesi — **saf fonksiyon**.

    `son_senkron is None` → **`bilinmiyor`**, ve bu `taze` DEĞİLDİR (B4).
    Gelecekte bir zaman damgası → **`bilinmiyor`**: saat kayması bir tazelik kanıtı
    değildir ve *"çok taze"* diye okumak, bozuk bir saati **güvence** yapardı.
    """
    if son_senkron is None:
        return "bilinmiyor"
    simdi = simdi or datetime.now(timezone.utc)
    if son_senkron.tzinfo is None:
        son_senkron = son_senkron.replace(tzinfo=timezone.utc)
    yas = simdi - son_senkron
    if yas < timedelta(0):
        return "bilinmiyor"
    uyari, hata = esikler(periyot_saat)
    if yas >= hata:
        return "hata"
    if yas >= uyari:
        return "uyari"
    return "taze"


def sayi_gosterilir_mi(kademe_adi: str | None) -> bool:
    """🔴 **`hata` kademesinde SAYI GÖSTERİLMEZ** — ve `bilinmiyor` aynı muameleyi görür.

    Kaynak planlar bunun **tersini** yazıyordu; yol haritası *"bugünkü davranıştan
    kasıtlı bir sertleşme"* diye düzeltti. Gerekçe: sekiz gün eski bir sayıyı normal
    gibi göstermek, kullanıcıyı **yanlış bir karara** götürür — ve o karar geri alınamaz.
    Sayının yerine **açıklama** gelir: *neden* gösterilmediği, sayının kendisinden
    daha değerlidir.
    """
    return (kademe_adi or "bilinmiyor") not in SAYI_GIZLENEN


def en_kotu(kademeler) -> str:
    """Birden çok kaynağın **en kötü** kademesi. Bir cevap iki tabloya dayanıyorsa,
    tazeliği **en bayat** olanı belirler — ortalama almak, bayat yarıyı gizlerdi."""
    sira = {k: i for i, k in enumerate(KADEMELER)}
    gecerli = [k for k in (kademeler or []) if k in sira]
    return max(gecerli, key=lambda k: sira[k]) if gecerli else "bilinmiyor"


def rapor(son_senkron: datetime | None, *, periyot_saat: int | None = None,
          simdi: datetime | None = None) -> dict:
    """Sözleşmeye giden blok: `{freshness, son_veri_ts, yas_saat, aciklama}`.

    ⚠ `son_veri_ts` **son BAŞARILI SENKRONdur**, verinin kendi zaman damgası değil —
    ikisi aynı şey değildir ve açıklama metni bunu **söyler** (boru hattı çalışıp boş
    dönebilir). Keskin sinyal (zaman boyutunun `max()`'ı) her soruda ek bir DB sorgusu
    ister; o karar ölçülmeden alınmadı.
    """
    k = kademe(son_senkron, periyot_saat=periyot_saat, simdi=simdi)
    simdi = simdi or datetime.now(timezone.utc)
    yas = None
    if son_senkron is not None:
        ts = son_senkron if son_senkron.tzinfo else son_senkron.replace(tzinfo=timezone.utc)
        yas = round((simdi - ts).total_seconds() / 3600, 1)
    aciklama = {
        "taze": None,
        "uyari": f"Veri {yas} saattir güncellenmedi — sayı gösteriliyor ama eskimiş olabilir.",
        "hata": f"Veri {yas} saattir güncellenmedi. Sayı **gösterilmiyor**: bu kadar bayat "
                "bir değerle karar vermek, karar vermemekten kötüdür.",
        "bilinmiyor": "Verinin ne zaman güncellendiği **bilinmiyor**. Bilinmeyen tazelik "
                      "taze DEĞİLDİR (B4): ölçemediğimiz bir şeyi iyi varsaymayız.",
    }[k]
    return {
        "freshness": k,
        "son_veri_ts": son_senkron.isoformat() if son_senkron else None,
        "yas_saat": yas,
        "aciklama": aciklama,
    }
