# ADR-0007 — Konuşmaya dayalı BI + sohbet kalıcılığı — **K3: dönem eksikse SOR**

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **16** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **16 atıf** aldı ve `docs/adr/` dizini
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

*"Ciro ne kadar?"* sorusunun **doğru cevabı yoktur** — hangi dönem? Bir sistem burada sessizce *"tüm zamanlar"* seçerse, kullanıcı hiç sormadığı bir soruya **güvenle yanlış** bir cevap alır ve bunu asla fark etmez.

## Karar

🔴 **K3 — DÖNEM EKSİKSE SOR.** Dönemi belirsiz bir soruda sistem **tahmin etmez**, netleştirme sorar (`CLARIFY:dönem`). Sohbet **kalıcıdır**: onay bağlama yazılır ve sonraki tur onu taşır.

## Sonuçlar

- 🔴 **v1'in üçüncü çıkış ölçütü bu maddeye dayanıyor** (§C/3): `CLARIFY:dönem` (%13,6) **dokunulmazdır** — kapsam artırmak için bu payı eritmek, ölçütü ölçtüğü şeyi bozarak 'iyileştirmek' olurdu.
- ⚠ Netleştirme bir **cevapsızlık değildir**: kullanıcı bir tık sonra **deterministik** bir cevap alır (risk-kapsam eğrisinde ayrı bir kapıdır).

## Kanıt — **tek doğrulama yolu**

- `app/routers/conversations.py`
- `app/cube_router.py` (`CLARIFY:dönem`)

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
