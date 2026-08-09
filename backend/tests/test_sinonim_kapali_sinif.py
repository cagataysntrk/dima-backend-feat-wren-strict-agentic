"""🔴🔴 `§SY` — **BİR SİNONİM, DİLİN KAPALI SINIFIYLA ÇARPIŞAMAZ.**

## Ölçülen kusur (canlı `VII/B4`, 2026-08-10)

Bir thread'in dördüncü turunda kullanıcı *«bir **de** gecikme ekle»* dedi ve cevaba
`ort_renk_sapmasi` (renk sapması) eklendi — **gecikme değil**. Rozet `source=cube`,
yani **deterministik yol**, ve **hiçbir beyan yok**:

    _match_measure("bir de gecikme ekle", parti) → ('ort_renk_sapmasi', 'de')

Eşleşen sinonim `de` idi: `ΔE`'nin kısaltması pack'te `"dE!"` diye yazılmış ve
normalleşince Türkçenin **bağlaç eki** `de` oluyor.

## ⚠ VE ÇAREYİ, ÇARENİN KENDİSİ DOĞURDU

Pack'in kendi yorumu şunu diyordu:

> *"`dE!` TAM-KELİME (sonu `!`): 2 harfli kısa sinonim substring-eşleşmede tehlikeli"*

Yani tehlike **biliniyordu** ve `!` işareti bir **önlem** olarak konmuştu. Ama `!` tam
tersini yapar: sinonimu **tam kelime** olarak eşleştirir — ve `de` tam olarak bir tam
kelimedir, üstelik Türkçenin en sık kullanılan eklerinden biri.

*Bir tehlikeyi daraltarak çözmek, bazen onu tam olarak isabet ettirmektir.*

## Sınır — ADR-0008'e uygun

Bu kapı bir **kelime listesi** kurmuyor (o yasak). Türkçenin **kapalı sınıflarını**
sayıyor — bağlaçlar, işaret sıfatları, soru ekleri — ve bunlar tanım gereği sonlu,
tarihsel olarak sabit kümelerdir. ADR-0008 açık uçlu sözlükleri yasaklar, kapalı
dilbilgisi sınıflarına izin verir (`ask.py`'nin gösterim süzgeci aynı disiplindedir).
"""

from __future__ import annotations

import pathlib

import yaml

PACKS = pathlib.Path(__file__).resolve().parents[1] / "demo" / "packs"

#: Türkçenin **kapalı** sınıfları — sonlu, tarihsel olarak sabit. Bir ölçü/küp adı
#: bunlardan biriyle çakışırsa, o ad her cümlede rastgele ateşlenir.
KAPALI_SINIF = frozenset({
    "de", "da", "ki", "mi", "mu", "mı", "mü", "ve", "ile", "ya", "veya", "ama",
    "bu", "şu", "su", "o", "her", "bir", "en", "gibi", "için", "icin", "da", "ise",
})

#: 🔴 Yazılı **muafiyet** — her satır bir ölçüm taşır, bir tercih değil.
#: ⚠ `su` gerçek bir kaynaktır (`toplam_su_lt`) ve Türkçede `şu` normalleşince `su`
#: olur. Canlıda sınandı (`VII`): *«şu makinede fire ne kadar»* ve *«şu ay toplam
#: üretim»* → **ikisi de doğru küpe** (`parti`) çözüldü, su ölçüsü ateşlenmedi;
#: route'un öteki kanıtları ağır bastı. Yani risk **gizli**, canlı değil — ve `su`'yu
#: kaldırmak gerçek bir yeteneği kaybetmek olurdu.
#: *Ölçülmemiş bir riski gidermek için ölçülmüş bir yeteneği atmak, bir takas değil
#: bir kayıptır.* Yeniden ölçülürse bu satır düşer.
MUAFIYET = {("surdurulebilirlik", "su")}


def _sinonimler():
    """Tüm pack'lerdeki (sahip, sinonim) çiftleri — normalleştirilmiş."""
    from app.cube_router import _norm

    for f in PACKS.rglob("*.yml"):
        try:
            veri = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        for c in (veri.get("cubes") or []):
            if not isinstance(c, dict):
                continue
            ad = str(c.get("name") or f.stem)
            for s in (c.get("synonyms") or []):
                yield ad, str(s), f
            for m in (c.get("measures") or []):
                if isinstance(m, dict):
                    for s in (m.get("synonyms") or []):
                        yield ad, str(s), f
        _ = _norm


def test_SINONIM_KAPALI_SINIFLA_CARPISMAZ():
    """🔴 Ölçüldü: `"dE!"` → *«bir **de** gecikme ekle»* yanlış ölçü ekledi, beyansız."""
    from app.cube_router import _norm

    ihlal = []
    for sahip, s, f in _sinonimler():
        t = _norm(s.rstrip("!").strip())
        if t in KAPALI_SINIF and (sahip, t) not in MUAFIYET:
            ihlal.append(f"{sahip} ← «{s}» ({f.relative_to(PACKS)})")
    assert not ihlal, (
        "🔴 Bir sinonim Türkçenin KAPALI sınıfıyla çarpışıyor — her cümlede rastgele "
        "ateşlenir:\n  " + "\n  ".join(ihlal)
        + "\n\nYa sinonimi kaldır (uzun karşılığı zaten varsa kayıp yoktur) ya da "
          "`MUAFIYET`'e **ölçümüyle** yaz.")


def test_MUAFIYET_OLCUMSUZ_BUYUMEZ():
    """⚠ Muafiyet listesi bir kaçış deliği olmamalı: her satırın canlı bir ölçümü var.

    ⊙ Bugün **bir** satır: `su` (canlıda iki soruyla sınandı, ateşlenmedi). Liste
    büyüyorsa gerekçesi de büyümeli — *bir muafiyet, gerekçesi olmadan bir istisnadır
    ve istisnalar kuralı yer.*
    """
    assert len(MUAFIYET) <= 1, (
        "muafiyet listesi büyümüş — her yeni satır CANLI bir ölçümle gerekçelenmeli")


def test_KAPALI_SINIF_GERCEKTEN_KAPI_MI():
    """🔴 Meta-kapı: yüklem gerçekten yakalıyor mu? Kaldırılan `"dE!"` yeniden konsa
    kırmızı vermeli — yoksa bu dosya bir belge, bir kapı değil."""
    from app.cube_router import _norm

    assert _norm("dE!".rstrip("!")) in KAPALI_SINIF, \
        "yüklem `dE!`'yi yakalamıyor — kapı konusuz"
    assert _norm("delta e") not in KAPALI_SINIF, \
        "yüklem meşru sinonimi de yakalıyor olurdu (yanlış pozitif)"
