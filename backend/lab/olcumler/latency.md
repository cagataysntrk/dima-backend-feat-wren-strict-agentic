# `/ask` GECİKME TABANI — FAZ O-0

> Bu dosya bir **ölçüm kaydıdır**, elle yazılmış bir hedef değil. Kaynağı kapının kendi
> kütüğüdür: `answer.py` her cevaba `süre=…ms` yazıyor ve korpus koşumu binlerce istek
> üretiyor. Buradaki sayılar o kütükten **okundu**.

## Ölçüm · 2026-08-09 · korpus koşumu

| n | min | **p50** | p90 | p99 | max |
|---|---|---|---|---|---|
| **15.149** | 77 ms | **445 ms** | 801 ms | 1923 ms | 3472 ms |

süre=445ms

## ⟳ Devralınan iddia DÜZELTİLDİ

Bağımsız ajanın kapı-yavaşlaması raporu *"`/ask` 47 ms → **177 ms**"* diyordu. Bu ölçüm
**445 ms** veriyor. İkisi **çelişmiyor** — farklı paydalar:

| kaynak | payda | p50 |
|---|---|---|
| ajan raporu | bir örneklem (400 istek) | 177 ms |
| **bu ölçüm** | **tam korpus (15.149 istek)** | **445 ms** |

⊙ Korpus daha **zor** soruları da içerir: netleştirme, çapraz-konu, kapsam kapısı,
garson turu. Yani 445, ürünün gerçek karışımına daha yakındır.

*Bir tabanı iki kez ölçmek, ikisinin de neyi ölçtüğünü yazmayı gerektirir.*

## ⚠ AÇIK BORÇ — ölçümün KALICILIĞI

Bu dosya **elle** yazıldı çünkü `nl_corpus.py`'nin `sure_sn` alanı henüz bir rapora
**yazılmıyor** (bu turda eklendi, dilim dağılımı için kullanılıyor). Kapı
(`test_latency_tavani.py`) bu dosyayı okuyor ve **kayıt yoksa atlanıyor** — uydurma bir
sayı üretmiyor.

🔴 **Sıradaki adım:** korpus koşumu bu dosyayı **kendisi** yazsın. O zamana kadar kapı bir
**cırcır** değil bir **kayıt**tır ve bu, docstring'inde de yazılıdır.

*Ölçemediğini yeşil sayan bir kapı, olmayan bir kapıdır; ölçemediğini söyleyen bir kapı,
henüz kurulmamış bir kapıdır — ikisi aynı şey değildir.*

## 🔴 NEDEN `lab/reports/` DEĞİL — bir ders, ikinci kez

İlk yazımda bu dosyayı `lab/reports/`e koydum ve `git add` **reddetti**:
`lab/reports` **gitignore'lu bir derleme çıktısı**.

⊙ Yani kapı, temiz bir çalışma kopyasında (CI · yeni klon) bu dosyayı **bulamaz** ve
sessizce **atlar** — ölçtüğünü sanan, ölçmeyen bir kapı.

🔴 Bu, `CLAUDE.md`'nin adıyla kaydettiği dersin **birebir kardeşi**: *«ölçüm aracı
şemasını kendi derlemesinden alır… `demo/wren-project` gitignore'lu bir derleme
artefaktıdır ve bir ölçüm aracı oradan okursa bayat bir katalogla koşar»*. Orada **girdi**
bir artefakttaydı; burada **kaydın kendisi**.

*Bir ölçümü izlenmeyen bir yere yazmak, onu ölçmemekle aynı kapıya çıkar — ama daha
kötüdür, çünkü ölçülmüş görünür.*
