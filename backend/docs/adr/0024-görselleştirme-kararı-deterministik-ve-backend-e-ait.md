# ADR-0024 — Görselleştirme kararı deterministik ve backend'e ait

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **37** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **37 atıf** aldı ve `docs/adr/` dizini
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

Grafik seçimi bir **görsel dilbilgisi** işidir (Show-Me / Cleveland-McGill), bir yaratıcılık işi değil. LLM'e Vega ürettirmek determinizm felsefesiyle çelişir.

## Karar

`analyze()` → `recommend()` iki katmanlı ve **deterministiktir**; karar backend'de verilir, frontend **çizer**.

## Sonuçlar

- Aynı veri **her zaman** aynı grafiği verir — ekran görüntüsü bir kanıttır.
- ⚠ Referans çizgisi bugün **ortalamadır**, hedef değil; hedef `target:` beyanı varsa gelir (FAZ 2.5, bayrak `hedef_kiyasi`) — **hedef UYDURULMAZ**.

## Kanıt — **tek doğrulama yolu**

- `app/viz.py`
- `app/report.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
