# ADR-0012 — Canlıya alma / hosting topolojisi

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

Dağıtım kararları koda sızarsa, ortam değiştirmek bir kod değişikliği olur.

## Karar

Hosting kararları **env** ve dağıtım katmanında kalır; uygulama ortamı **okur**, varsaymaz.

## Sonuçlar

- ⚠ Bu ADR'nin atıf sayısı **en düşük olanlardan** (2) — yani rekonstrüksiyonu da **en zayıf kanıta** dayanıyor. Bu satır bir sınır beyanıdır, bir güvence değil.

## Kanıt — **tek doğrulama yolu**

- `backend/README.md:163`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
