# DIMA + METABASE — DENETİM DEFTERİ

## A. Her oturum başı

- [ ] Aktif branch tam olarak `feat/dima-metabase-platform`.
- [ ] Base `3774484167f1056d89da0e0609246fb4a05057ec` mevcut HEAD'in ancestor'ı.
- [ ] `feat/ask-v2-mvp` yalnız read-only referans olarak kullanılıyor.
- [ ] İki mühürlü normatif belgenin Git blob SHA'ları SOURCE_LOCK ile aynı.
- [ ] Son living status okundu.
- [ ] Açık failure/decision receipt'leri okundu.
- [ ] Bir sonraki ticket yol haritasındaki sıraya uygun.

## B. Her write öncesi

- [ ] GitHub write hedefinde branch explicit `feat/dima-metabase-platform`.
- [ ] Beklenen branch HEAD yeniden okundu.
- [ ] Aynı path için yarışan başka write yok.
- [ ] files-to-touch / files-not-to-touch belli.
- [ ] Source branch'e write API çağrısı yok.

## C. Her ticket kapanışı

- [ ] doğru abstraction düzeltildi; vaka yaması yapılmadı.
- [ ] focused proof green.
- [ ] gerekiyorsa live/sentinel green.
- [ ] RED olduysa receipt patchten önce açıldı.
- [ ] authority/security/provenance invariantları kontrol edildi.
- [ ] durum dosyası SHA ve test sonucu ile güncellendi.
- [ ] open debt gizlenmedi.

## D. P0 bootstrap exit gate

```text
new branch exists from immutable certified SHA
sealed report committed
sealed roadmap committed
source lock committed
operation/audit/status committed
failure receipts committed
decision receipts committed
governance CI active
ask-v2 writes = 0
product code changes = 0
```

## E. P1 öncesi özel kontrol

P1'de ask-v2 sonrası düzeltmeler "source branchte var" diye otomatik kabul edilmez.
Özellikle şu invariants platform branchinde yeniden kanıtlanacaktır:
- partial semantic surface silent-loss = 0;
- Standard/Research double authority = 0;
- semantic linker / temporal normalizer role separation;
- Wren behavior drift = 0.

## F. Denetçinin yasakları

Denetim:
- sonuca göre oracle değiştirmez;
- hidden/case metnini prompta taşımaz;
- transport fail'i semantic fail diye yamamaz;
- Metabase query success'i semantic equivalence saymaz;
- source branch moving HEAD'ini "daha yeni = daha doğru" kabul etmez.
