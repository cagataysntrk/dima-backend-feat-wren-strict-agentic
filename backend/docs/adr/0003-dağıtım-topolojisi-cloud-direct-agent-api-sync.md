# ADR-0003 — Dağıtım topolojisi: `cloud_direct` | `agent` | `api_sync`

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **2** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **2 atıf** aldı ve `docs/adr/` dizini
> *"ne diskte ne git geçmişinde"* vardı (MIMARI §8.2, ölçüldü). Bu dosya, o atıfların
> **bağlamından ve kodun kendisinden** türetildi (FAZ 4.6 @`5d2f37b`).
>
> **Başlıklar alıntı değildir.** Bir cümle *"ADR şöyle diyordu"* diye okunamaz; yalnız
> *"kod bugün şöyle davranıyor ve gerekçesi şu"* diye okunabilir. **Kanıt sütunu tek
> doğrulama yoludur** — çelişkide **kod kazanır**, bu dosya değil.
>
> *Var olmayan bir belgeye atıf yapmak bir eksiklikti; onu uydurulmuş bir tarihle
> doldurmak bir sahtekârlık olurdu.*


## Bağlam

Müşteri verisi üç farklı yerde durabiliyor: bizim bulutumuzda, müşterinin kendi ağında (ajan), ya da bir API üzerinden senkronlanarak. Bu üçü **farklı güven sınırlarıdır** ve tek bir bağlantı tipi varsaymak, en dar sınırı en geniş gibi işletmek olurdu.

## Karar

Topoloji bir **tenant özniteliğidir** ve bağlantı kaydında taşınır. Kod topolojiyi **tahmin etmez**, okur.

## Sonuçlar

- Clone/sync motoru topolojiden **bağımsız** yazılabildi (bkz. ADR-0017 §9).
- ⚠ Topoloji bir **yetki sınırı değildir** — güvenlik her zaman `authorize()`.

## Kanıt — **tek doğrulama yolu**

- `control_plane/models.py` — `Tenant`/`Connection` topoloji alanları

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
