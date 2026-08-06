"""⊘ KÖK-7b — **DENENDİ, ÖLÇÜLDÜ, İNMEDİ.** Kararın yazılı kaydı.

🔴 Bu dosya bir kusuru kapatmaz; bir **kararın sessizce unutulmasını** kapatır. Depo
`MIMARI.md §10` kuralını taşır: *"kapananlar işaretlenir, silinmez."* Denenip
reddedilmiş bir çözüm de aynı muameleyi hak eder — yoksa bir sonraki tur onu **baştan**
dener ve **aynı bedeli** öder.

## Ne denendi

Raporun KÖK-7b'si: *"`_STOP_STEMS`'e kelime eklemek yerine yapısal kural — katalogda
karşılığı olmayan, Türkçe çekim eki taşıyan fiil/soru token'ı dolgudur."*
Ölçüt: **§4 probu ≥%90 HIT, `_STOP_STEMS`'e tek kelime eklenmeden.**

Uygulandı (`app/dolgu_kurali.py`, üç yapısal kural — hiçbiri kelime listesi değil):

1. **fiil kişi/zaman eki** taşıyan token (`verdik` · `sattık` · `düşüyor`)
2. **yüklem konumu**: ardından soru klitiği gelen token (`iyi mi` · `düştü mü`)
3. **kapalı soru sınıfı** ve ona bitişik token (`kaç` · `durumu ne`)

Hepsinin üstünde bir ön şart: **katalogda karşılığı olan kelime dolgu sayılamaz.**

## ⊙ Ölçüm — ölçüt TUTTU, ürün BOZULDU

| | önce | sonra |
|---|---|---|
| §4 probu | %31,2 (35/112) | 🟢 **≥%90** *(yalnız `söyle` kaldı)* |
| `_STOP_STEMS`'e eklenen kelime | — | 🟢 **0** |
| gerçek-dünya **kabul** | 1150 | 🔴 **1117** |
| gerçek-dünya **sessiz_yanlis** | 12 | 🔴 **30** |

🔴 **Kabul DÜŞTÜ** — kapsam açan bir değişiklikten beklenenin tersi. Sebep: yapısal
dolgu kuralı anlamlı kelimeleri de yutunca soru **anlaşılmış gibi** görünüp **yanlış
cube'a** gidiyor; yani kayıp `kabul`den `sessiz_yanlis`e **taşınıyor**.

> *Bir ölçütü tutturmak, ölçütün ölçmediği şeyi bozmama garantisi vermez. §4 probu
> "kaç soru cevaplanıyor" diye sorar; "doğru mu cevaplanıyor" diye sormaz.*

## ⚠ Ve ölçümün kendisi bir kez YALAN SÖYLEDİ

İlk turda 7b **8** sessiz-yanlış ile yeşil göründü ve neredeyse bu hâliyle indi.
O sayı **bayat bir derleme artefaktından** geliyordu (`tests/test_olcum_semasi_taze.py`).
Taze derlemeyle gerçek sayı **30** çıktı. *Bir çözümün yeşil görünmesi, ölçümün taze
olduğunu kanıtlamaz — ve bu tur, sıralamanın tersini denedi.*

## Sonraki tur için — nereden devam edilmeli

⊙ Kural **fazla cömert**: `_covers` ön şartı katalog kelimelerini koruyor ama katalog
**dışı** anlamlı kelimeleri (özel ad, değer, argo) koruyamıyor. Muhtemel yön: yapısal
dolgu **kapsamı açmasın**, yalnız **netleştirme metnini** iyileştirsin — yani `verdik`
yüzünden ölen soru *"«verdik» kısmını anlamadım"* demek yerine *"fire mi fire oranı mı?"*
diye sorsun. Bu, raporun kendi *"kapının açılış tasarımının şartı"* cümlesidir:

> *"Kapı, «bilmiyorum» ile «iki adaydan hangisi?» ayrımını korumak zorundadır."*

🔴 Yani 7b'nin evi **KÖK-9**'dur (belirsizlik→chip), kapsam kapısı değil.
"""

from __future__ import annotations

import pathlib

APP = pathlib.Path(__file__).resolve().parents[1] / "app"


def test_YAPISAL_DOLGU_INMEDI():
    """⊘ Karar kapısı: `app/dolgu_kurali.py` **bilerek yok**. Bir gün inerse bu test
    kırmızı verir ve yukarıdaki ölçümün yeniden yapılmasını zorlar.

    ⚠ Bu bir *"asla yapılmasın"* kapısı DEĞİL — bir **hatırlatma** kapısıdır. Kırmızı
    verdiğinde doğru tepki, testi silmek değil, `kabul` ve `sessiz_yanlis` sayılarını
    yeniden ölçüp bu docstring'i güncellemektir."""
    assert not (APP / "dolgu_kurali.py").exists(), (
        "⟳ KÖK-7b geri gelmiş. Ölçülmüş bedeli: kabul 1150 → 1117, sessiz_yanlis "
        "12 → 30 (taze derlemeyle). §4 probu %90'ı geçiyordu ama ürün bozuluyordu — "
        "`tests/test_kok7b_karar_kaydi.py` docstring'ini oku ve sayıları YENİDEN ölç.")


def test_KAPSAM_KAPISI_HALA_SOZLUKTEN_KARAR_VERIYOR():
    """⊙ Kusurun **hâlâ açık** olduğunun kaydı: `_is_stop_word` elle yazılmış bir listeye
    bakıyor ve `yaptık`✅ / `verdik`❌ asimetrisi **duruyor**.

    *Kapatılmamış bir kusuru kapatılmış saymak, kapatmaktan daha zararlıdır.*"""
    from app.cube_router import _is_stop_word

    assert _is_stop_word("yaptik"), "⊘ vaka bayatlamış"
    assert not _is_stop_word("verdik"), (
        "⟳ asimetri kapanmış — KÖK-7b başka bir yoldan inmiş olabilir; "
        "karar kaydını güncelle")
