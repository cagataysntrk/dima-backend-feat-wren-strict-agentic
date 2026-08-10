"""🔴 `C2`/`C5` — **SİNONİM HASADI**: liste elle yazılmaz, kullanımdan toplanır.

Kullanıcının kuralı: *"tek tek sinonim yazmak aptallık."* Doğru — ama ters yön
*"hiç yazma"* değil: **LLM Türkçeyi bilir, senin şirketini bilmez.** `iade → şikâyet`
bir eşanlam bile değil bir **iş kuralıdır** ve hiçbir genel model onu türetemez.
Ölçülmüş bedeli: sözlüksüz dönemde **9/9 Intent çağrısı `{"cube":null}`**.

⊙ Doğru iş listeyi kaldırmak değil, **kim yazacağını** değiştirmek: sistem kendi
bilmediği kelimeleri (`uncovered_words`) biriktirir, sıklık sıralar, sınıflandırır.
**Sıcak yolda sıfır** — girdi zaten her turda yazılıyor.

## `C5`'in üç sert şartı burada KOD

| şart | kapı |
|---|---|
| çok eşleşme → kuyruğa **girmez** | `test_COK_SAHIPLI_KELIME_ADAY_OLMAZ` |
| «hiçbiri» bir başarısızlık değildir | `test_SAHIPSIZ_KELIME_ADAYDIR` |
| tek görülen bir kelime **örüntü değil** | `test_SEYREK_KELIME_KUYRUGA_GIRMEZ` |
"""

from __future__ import annotations

from lab.sinonim_hasadi import ASGARI_SIKLIK, hasat, siniflandir


def test_COK_SAHIPLI_KELIME_ADAY_OLMAZ(schema):
    """🔴 `C5/1` — ≥2 sahip bir sinonim değil bir **BELİRSİZLİKTİR**.

    Sinonim yazmak `bakiye`nin ₺11,86 milyonluk sessiz seçimini **kalıcı** yapardı:
    *belirsizliği bir sözlüğe yazmak, onu çözmek değil GİZLEMEKTİR.*
    """
    sinif, sahipler = siniflandir("bakiye", schema)
    if len(sahipler) > 1:
        assert sinif == "belirsizlik", (sinif, sahipler)
    else:                                    # katalog değişmiş olabilir — sessiz geçme
        assert sinif in ("zaten_var", "aday"), (sinif, sahipler)


def test_KATALOGDA_OLAN_KELIME_BORC_DEGILDIR(schema):
    """⚪ route zaten çözüyorsa bu bir sinonim borcu değildir."""
    sinif, sahipler = siniflandir("fire", schema)
    assert sinif in ("zaten_var", "belirsizlik"), (sinif, sahipler)


def test_SAHIPSIZ_KELIME_ADAYDIR(schema):
    """🟢 Kapalı seçime gidecek **tek** sınıf budur.

    ⚠ Ve *«hiçbiri»* cevabı bir başarısızlık DEĞİLDİR: kelime gerçekten hiçbir şeyin
    eşanlamı değilse doğru cevap odur ve o bir **menü boşluğu** sinyalidir (`B-6`).
    """
    sinif, sahipler = siniflandir("zzzyokboylekelime", schema)
    assert sinif == "aday" and sahipler == []


def test_SEYREK_KELIME_KUYRUGA_GIRMEZ(schema, monkeypatch):
    """🔴 *Tek görülen bir kelime bir örüntü değil bir **olaydır**.*

    Tek olaydan sözlük yazmak, gürültüyü kalıcı kılar.
    """
    import lab.sinonim_hasadi as H

    # 🔴 Artık SORU verilir, kelime değil — hasat bilinmeyenleri kendisi hesaplar.
    monkeypatch.setattr(H, "_sorulari_oku",
                        lambda: ["birkezgorulen", "cokgorulen", "cokgorulen"])
    h = hasat(schema)
    assert any(k == "birkezgorulen" for k, _n, _s in h.get("seyrek") or [])
    assert not any(k == "birkezgorulen"
                   for k, _n, _s in (h.get("aday") or []))
    assert ASGARI_SIKLIK >= 2


def test_HASAT_SIFIR_LLM(schema, monkeypatch):
    """🔴 **Sıcak yolda sıfır** — ve çevrimdışı koşumda da LLM YOK.

    Hasat yalnız kütüğü okur ve `route()`'un deterministik eşleştiricisini kullanır.
    Bir gün buraya bir LLM çağrısı girerse bu kapı onu görmez — ama `lab/` aletinin
    sözleşmesi budur ve docstring'inde yazılıdır.
    """
    import lab.sinonim_hasadi as H

    monkeypatch.setattr(H, "_sorulari_oku", lambda: ["aaa bbb", "aaa"])
    h = hasat(schema)
    assert sum(len(v) for v in h.values()) == 2, h
