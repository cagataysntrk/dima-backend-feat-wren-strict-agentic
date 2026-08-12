"""FAZ 5.17 — **TEK SES: metin katalogu.** [bayraksız: kök neden]

## Ölçülen kusur

Kullanıcıya dönen metinlerin **hepsi satır içi f-string**: `ask.py` (~20 dal) +
`eylem.py` + `contribution.py`. **Merkezî katalog YOKTU** ve üç somut sonucu vardı:

| ölçülen | örnek |
|---|---|
| 🔴 **Hitap aynı oturumda değişiyor** | `ask.py` **"sen"** (*"istediğini"*) ↔ `eylem.py` **"siz"** (*"kastettiğinizi"*) |
| Aynı cümle **iki yerde birebir** | *"Bu soru için güvenilir bir sorgu üretemedim."* |
| **Jargon sızıntısı** | kullanıcıya *"yapısal bir `cube_query` taşımıyor (Discovery/ham SQL)"* |

## 🔴 ROBOTİKLİĞİN ASIL KAYNAĞI METNİN ŞEKLİ

> *"Neyi karşılaştırmak istediğini anlayamadım"* bir **form doğrulayıcısıdır**, bir soru
> değil.

**Kural: ÖNCE NE ANLADIĞINI SÖYLE, SONRA SOR.**

| Bugün | Olacak |
|---|---|
| *"Hangi dönem için?"* | *"Fire toplamını çıkarabilirim — **hangi dönem?**"* |
| *"…tanıdığım konu geçmiyor"* | *"Bu soruda tanıdığım bir ölçü yakalayamadım. **Şunlardan biri mi?**"* |

## Bu bir VERİ MODÜLÜ, yeni bir soyutlama değil

Sözlük + üç alan (`metin` · `kind` · `hitap`). Şablon motoru yok, i18n çerçevesi yok,
sınıf hiyerarşisi yok. *Bir metin katalogunun tek işi metinleri bir yerde tutmaktır;
ikinci bir işi olduğu anda kimse ona metin yazmaz.*

## ⚠ `note` YENİDEN KULLANILMAZ

`AskResponse.note` bugün **dört** anlam taşıyor (dürüst ret · netleştirme · kırpılma
uyarısı · upload bildirimi) **ve kalıcı `payload_json` geçmişi ona bağlı**. Yeni alan
`soz`; frontend `soz ?? note` okur → **eski kayıtlar aynen çalışır**.

> **Karar kaydı: `ADR-0033`** — tek ses — kullanıcıya dönen metin tek katalogdan.
> ⚠ Atıf, kararın **yaşadığı yere** yazılır: kayıt ile kod birbirini ancak
> böyle doğrulayabilir (`tests/test_adr_dosyalari.py` iki yönü de kilitler).
"""

from __future__ import annotations

from typing import Any

#: 🔴 **TEK HİTAP KİPİ: "sen".** Ölçüldü — `ask.py` 15 isabetle *"sen"*, `eylem.py`
#: *"siz"*. İkisi aynı oturumda karşılaşınca ürün **iki kişi gibi** konuşuyordu.
#: *Hangi kipin seçildiği önemli değil; SEÇİLMİŞ olması önemli.*
HITAP = "sen"

#: Metin türleri. `netlestirme` olanlar **soru işaretiyle biter** (kapı zorlar).
TURLER = ("netlestirme", "ret", "sosyal", "bilgi")

#: 🔴 **JARGON YASAK LİSTESİ.** Kullanıcıya iç terim söylemek, ona **bizim sorunumuzu**
#: anlatmaktır. Kapı bunu her kayıtta arar.
JARGON = ("cube_query", "cube query", "discovery", "ham sql", "raw sql", "mdl",
          "intent-json", "intent json", "route()", "vqr", "r1", "r10")

#: Katalog. **Kararlı ID** — metin değişebilir, ID değişmez (kayıtlar ID'ye bağlanır).
KATALOG: dict[str, dict[str, Any]] = {
    # --- TEMELLENDİRME: kıyası da "ne anladım"a yaz ------------------------------
    "temellendirme.kiyas_cift": {
        "metin": "{kaynak} ↔ {hedef}",
        "kind": "bilgi",
        "not": "🔴 `G6.3`: iki UÇ adlandırıldığında makbuz `mom` demez, dönemleri söyler.",
    },
    "temellendirme.kiyas_yoy": {
        "metin": "geçen yıla göre",
        "kind": "bilgi",
        "not": "Göreli kıyas: iki uç adlandırılmadı, mod adlandırıldı.",
    },
    "temellendirme.kiyas_mom": {
        "metin": "geçen aya göre",
        "kind": "bilgi",
        "not": "Göreli kıyas — `yoy`'un kardeşi; ikisi `app/yoy.py`'nin bildiği tek iki mod.",
    },
    # --- NETLEŞTİRME: önce ne anladığını söyle, sonra sor -------------------------
    "netlestirme.donem": {
        "metin": "{ne} çıkarabilirim — hangi dönem için?",
        "kind": "netlestirme",
        "not": "ADR-0007-K3: dönem eksikse SOR. `{ne}` çağıranın anladığı şey.",
    },
    "netlestirme.donem_sade": {
        "metin": "Bunu çıkarabilirim — hangi dönem için?",
        "kind": "netlestirme",
        "not": "`{ne}` bilinmiyorsa: yine de ÖNCE ne yapabileceğini söyle.",
    },
    "netlestirme.olcu": {
        "metin": "Bu soruda tanıdığım bir ölçü yakalayamadım. Şunlardan biri mi?",
        "kind": "netlestirme",
    },
    "netlestirme.konu": {
        "metin": "Birden fazla konu anlaşıldı — hangisini istiyorsun?",
        "kind": "netlestirme",
    },
    "netlestirme.kirilim": {
        "metin": "Bu raporu hangi kırılıma göre detaylandırayım?",
        "kind": "netlestirme",
    },
    # --- RET: dürüst sınır, suçlayıcı değil ---------------------------------------
    "ret.sorgu_uretilemedi": {
        "metin": "Bu soru için güvenilir bir sorgu üretemedim.",
        "kind": "ret",
        "not": "🔴 Bu cümle ÖLÇÜLDÜ: iki ayrı yerde BİREBİR tekrar ediyordu.",
    },
    "ret.kapsam_disi": {
        "metin": "Bu soruyu verinden cevaplayamıyorum — sorduğun şey "
                 "kataloğunda hiçbir tabloya karşılık gelmiyor.",
        "kind": "ret",
        "not": "🔴 ⑧ (2026-08-12): Discovery, kapsam dışı soruda HİÇBİR TABLOYA "
               "dokunmayan bir SELECT yazıp onu veri satırı gibi sunuyordu "
               "(`{\"1\": 1}` · `{\"mesaj\": \"…veri bulunmamaktadır.\"}`, dört "
               "turda dördü). Dürüst red yolu vardı; model onu GEÇERLİ bir SELECT "
               "yazarak atlıyordu.",
    },
    "ret.takip_baglanamadi": {
        "metin": "Bunu üstteki raporla bağlayamadım — yeni bir soru olarak sorayım mı?",
        "kind": "ret",
        "not": "Eski hâli bir form hatasıydı: *«ilişkilendiremedim»*.",
    },
    "ret.rapor_bayat": {
        "metin": "Üstteki rapor artık çalıştırılamıyor (şema değişmiş olabilir). "
                 "Yeni bir soru olarak sorar mısın?",
        "kind": "ret",
    },
    "ret.capa_yok": {
        "metin": "Bunun için önce bir rapor gerekiyor — hangi raporu kastettiğini "
                 "bilmiyorum. Önce sorunu sor, sonra cevabın altından bu isteği "
                 "tekrarla.",
        "kind": "ret",
        "not": "🔴 Eski hâli 'siz' kipindeydi (`eylem.py`) — hitap ölçülen kusurdu.",
    },
    "ret.konusma_capasiz": {
        "metin": "Bunu hangi rapor üstünde konuşalım? Önce bir soru sor, sonra cevabın "
                 "üstünde konuşabiliriz.",
        "kind": "ret",
    },
    # --- BİLGİ ---------------------------------------------------------------------
    "bilgi.periyot_desteklenmiyor": {
        "metin": "Bu sıklıkta zamanlama henüz kuramıyorum. Şu an saatlik, günlük ve "
                 "haftalık gönderim yapabiliyorum — bunlardan birini söylersen hemen "
                 "hazırlarım.",
        "kind": "bilgi",
    },
    "bilgi.yapisal_sorgu_yok": {
        "metin": "Bu cevap tablo hâlinde bir sonuç taşımıyor, o yüzden ayrıştıramıyorum.",
        "kind": "bilgi",
        "not": "🔴 Eski hâli JARGON sızdırıyordu: *«yapısal bir `cube_query` taşımıyor "
               "(Discovery/ham SQL)»* — kullanıcıya BİZİM sorunumuzu anlatıyordu.",
    },
}


class BilinmeyenSoz(KeyError):
    """Katalogda olmayan ID. **Fail-closed**: uydurulmuş bir ID, sessizce boş metin
    üretir ve kullanıcı **hiçbir şey** görmez."""


def soz(kimlik: str, **alanlar: Any) -> str:
    """ID → metin. Eksik bir alan **patlamaz**, `{alan}` olarak kalmaz — silinir.

    ⚠ Biçimlendirme hatası bir cevabı **düşürmemeli**: kullanıcı eksik bir kelimeyle
    yaşayabilir, cevapsızlıkla yaşayamaz.
    """
    try:
        kalip = str(KATALOG[kimlik]["metin"])
    except KeyError:
        raise BilinmeyenSoz(
            f"Katalogda olmayan söz: {kimlik!r}. Katalogda {len(KATALOG)} kalem var — adlar hata mesajında SIZDIRILMAZ (⟳ 08-12).") from None
    try:
        return kalip.format(**alanlar)
    except (KeyError, IndexError):
        import re

        return re.sub(r"\s*\{[^}]*\}\s*", " ", kalip).strip()


def tur(kimlik: str) -> str:
    return str(KATALOG[kimlik]["kind"])
