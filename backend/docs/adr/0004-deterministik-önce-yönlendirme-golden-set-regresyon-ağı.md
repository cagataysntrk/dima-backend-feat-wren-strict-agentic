# ADR-0004 — Deterministik-önce yönlendirme + golden-set regresyon ağı

**Durum:** kabul edildi (kod tarafından **yürürlükte**) · **Atıf:** kodda **6** kez · **Rekonstrüksiyon:** FAZ 4.6 @`5d2f37b`

> ## ⚠ BU BİR REKONSTRÜKSİYONDUR — ORİJİNAL DEĞİL
>
> Bu karar **alındığı gün yazılmadı**. Kodda **6 atıf** aldı ve `docs/adr/` dizini
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

Bir soruyu LLM'e vermek **her zaman mümkündür**; sorun mümkün olması değil, **ucuz görünüp pahalı olmasıdır**: olasılıksal bir seçim, deterministik olarak bilinebilecek bir şeyin yerine geçtiğinde hata **sessiz** olur.

## Karar

Bir soru **deterministik olarak çözülebiliyorsa LLM'e GİTMEZ**. `route()` sıfır-LLM çalışır ve merdivenin ilk basamağıdır. Regresyon, kuratörlü bir **golden-set** ile kilitlenir.

## Sonuçlar

- Bu ilke `Planlayici`'nin **deterministik-önce kapısına** kadar taşındı (ADR-0008 disipliniyle birlikte).
- ⚠ `eval` MIMARI §7'nin kendi ifadesiyle *"zaten çalışan şeye göre kuratörlenmiş"* bir **regresyon kilididir** — bir doğruluk ölçütü DEĞİL. Karıştırmak, ürünü olduğundan iyi gösterir (bkz. FAZ 4.8).

## Kanıt — **tek doğrulama yolu**

- `app/cube_router.py` docstring
- `eval/run.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**. Rekonstrüksiyon bir kayıttır, bir otorite değil (MIMARI §8.2).
