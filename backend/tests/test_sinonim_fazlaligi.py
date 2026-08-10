"""🔴🔴 `C4` — **FAZLALIK ÖLÇÜLDÜ, VE KARAR TERSİNE DÖNDÜ.**

Rapor `C4`: *"Sınıf A elden alınır — kök/çekim normalleştirmesi | **788 beyan elle
bakımdan çıktı**."*

## ⊙ Ölçüm — ve iki düzeltme

**(1) Sayı.** Rapor **788/1432 (%55)** diyordu; o sayı **statik** ve **boyut
sinonimlerini de** içeriyordu, üstelik sınıflandırma *"teknik adla kök paylaşıyor mu"*
diye **göz kararıydı**. Canlı derlenmiş şemada **ölçü** sinonimi beyanı **677**, ve
**kanıtlanabilir** biçimde gereksiz olan — yani *silinse kalan beyanlardan biri onu
morfolojiyle yine yakalar* — **113 (%17)**.

**(2) 🔴 Ve silmek YANLIŞ olurdu.** Raporun kendi `B-8` bölümü uyarıyor:

> *"Sinonimler oradan çıkarsa route yavaşlamaz — **garson körleşir**."*

Bir beyan `route()` için gereksiz olabilir (`borclar` zaten `borc`tan türer) ama
**katalog metni** için değildir: garsonun iş terimleri hakkında **tek** bilgi kaynağı
o metindir ve `borc tutari` · `cari borc` · `alacak toplami` kullanıcının **gerçekten
yazdığı** ifadelerdir. Ölçülmüş bedeli var: sözlüksüz dönemde **9/9 `{"cube":null}`**.

## Doğru iş: SİLMEK değil, ELLE YAZMAYI bırakmak

*Bir beyanın gereksiz olduğu yer, onun tek tüketicisi değildir.* Fazlalık **route**
tarafındadır; menü tarafında aynı beyan bir **varlık şartıdır**. Bu yüzden `C4`'ün
doğru hedefi 113 satırı silmek değil, çekim varyantlarının **üretilmesi** — bakım yükü
düşer, menü zenginliği **durur**.

⚠ Bu kapı o hedefin **ölçüsüdür**: fazlalık oranı **büyürse** biri elle çekim varyantı
yazmaya başlamış demektir.
"""

from __future__ import annotations

from app.cube_router import _norm, _syn_hit

#: Ölçülen taban (2026-08-10, canlı derlenmiş şema): 113/677.
#: ⚠ **Tavan, hedef değil**: bu sayının düşmesi iyidir, artması bir **elle yazım**
#: sinyalidir. *Bir oranın tavanı, onun hedefi sanılırsa borç kalıcılaşır.*
FAZLALIK_TAVANI = 130


def _fazlalik(schema) -> tuple[int, int, list[str]]:
    toplam = gereksiz = 0
    ornek: list[str] = []
    for c in schema.get("cubes") or []:
        for olcu, sinonimler in (c.get("measure_synonyms") or {}).items():
            sinonimler = [s for s in (sinonimler or []) if isinstance(s, str)]
            for s in sinonimler:
                toplam += 1
                kalan = [x for x in sinonimler if x != s]
                if any(_syn_hit(_norm(s), _norm(k).rstrip("!")) for k in kalan):
                    gereksiz += 1
                    if len(ornek) < 10:
                        ornek.append(f"{c['name']}.{olcu}:{s}")
    return gereksiz, toplam, ornek


def test_FAZLALIK_TAVANI_ASILMIYOR(schema):
    """🔴 Fazlalık **artarsa** biri elle çekim varyantı yazıyor demektir.

    ⚠ Kapı silmeyi **zorlamaz** — silmek garsonu körleştirirdi. Yalnız *elle yazmanın*
    geri gelmesini görünür kılar.
    """
    gereksiz, toplam, ornek = _fazlalik(schema)
    assert gereksiz <= FAZLALIK_TAVANI, (
        f"🔴 türetilebilir sinonim beyanı ARTTI: {gereksiz}/{toplam} "
        f"(tavan {FAZLALIK_TAVANI}). Örnek: {ornek}\n"
        "  Çekim varyantları ELLE yazılmamalı — `_ek_gecerli` onları zaten çözüyor.\n"
        "  ⚠ Ama var olanları SİLME: katalog metni garsonun tek bilgi kaynağıdır ve "
        "orada aynı beyan bir VARLIK ŞARTIDIR (`B-8`: *sinonimler çıkarsa garson "
        "körleşir* — ölçüldü: 9/9 `{\"cube\":null}`).")


def test_OLCU_SINONIMI_PAYDASI_ILAN_EDILMIS(schema):
    """⚠ Payda ilan edilmezse oran bir sayı değil bir izlenimdir."""
    _gereksiz, toplam, _o = _fazlalik(schema)
    assert toplam >= 400, f"ölçü sinonimi paydası beklenenden küçük: {toplam}"


def test_MORFOLOJI_DUZ_CEKIMI_COZUYOR():
    """🔴 `C4`'ün dayanağı: **düz** çekim eki bir beyan gerektirmez."""
    assert _syn_hit(_norm("renkler bazinda fire"), "renk")
    assert _syn_hit(_norm("renkleri"), "renk")
    assert _syn_hit(_norm("borclar toplami"), "borc")
    assert _syn_hit(_norm("hatlar"), "hat")


def test_UNSUZ_IKIZLESMESI_COZULMUYOR_VE_BU_YAZILI():
    """🔴🔴 **KAPI BENİ DÜZELTTİ — ve bulgusu `C4`'ün kararını GÜÇLENDİRDİ.**

    Bu testi ilk yazımda `hatti ~ hat` eşleşir sanmıştım. Eşleşmiyor: Türkçede
    iyelik ekinden önce **ünsüz ikizleşmesi** olur (`hat` → `hat**t**ı`) ve
    `_ek_gecerli` bir **çekim doğrulayıcıdır**, bir kök çözümleyici değil — kökün
    kendisi değişince onu takip edemez.

    ⊙ Yani katalogdaki `hatti` beyanı bir **fazlalık değil bir zorunluluktur**, ve bu
    bulgu `C4`'ün *«788 beyanı sil»* hedefinin neden yanlış olduğunun ikinci kanıtıdır:
    beyanların bir kısmı morfolojinin **erişemediği** yerdedir.

    ⚠ Bu bir borç DEĞİL bir **sınır**: kök çözümleyici yazmak, `ADR-0008`'in
    *"route'a dil kuralı ekleme"* yasağının tam ortasına düşer. Doğru cevap, bu
    kelimelerin **beyan edilmiş kalması**dır.

    *Bir aracın çözemediği şeyi ona yaptırmaya çalışmak, aracı bozar; onu beyan etmek
    ise yalnız bir satırdır.*
    """
    assert not _syn_hit(_norm("hatti bazinda"), "hat"), (
        "ünsüz ikizleşmesi artık çözülüyorsa bu bir KAZANÇTIR — testi güncelle ve "
        "`hatti` gibi beyanların artık fazlalık olduğunu ölç.")
