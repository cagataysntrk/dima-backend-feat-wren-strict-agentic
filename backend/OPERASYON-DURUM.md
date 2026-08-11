
### ✅ FAZ 1 KAPISI — taban birebir korundu, 7 kırmızı kapatıldı *(2026-08-11)*

**Kapı `--hepsi` koşuldu (3 dk 36 sn). Önce en önemlisi: ÜRÜN GERİLEMEDİ.**

```
TOPLAM doğru-cube: %95.1 (taban %94.4) ✅
🔴 cevapsız: 2980/14957 (%19.9) · semantik vaka: 554/590 · şişme 25.4×
doğru=95 · devir=2142 · netleştirme=0 · beyanlı_kısmi=41 · sessiz_yanlış=8 · payda=2286
eval.run: precision +0.0% · coverage −0.8% · deterministik pay +0.0%
```

🔴 **7 test kırmızıydı ve yedisi de kendi işimin muhasebesiydi** — hiçbiri ürün
gerilemesi değil:

| kapı | teşhis | çözüm |
|---|---|---|
| `test_alan_haritasi` | yeni `app/bicim.py` **sınıfsız** | 🎨 SUNUM olarak haritaya yazıldı |
| `test_bayrak_on_sarti` | **4 beta bayrak** yazılı `on` şartı taşımıyor (`vqr_few_shot` B2'den beri borçmuş) | dördüne de **gözlenebilir ölçüt** yazıldı |
| `test_modul_buyume` ×3 | `ask()` **+1** · `cube_router.py` **+44** · `ask.py` **+1** | muafiyet: **sha + Δ + gerekçe** |
| `test_ask_golden` | `/cube` izinde yeni `§D3` satırı | altın güncellendi — *«bir altın testin işi soru sormaktır»* |

⊙ **Kapı iki gerçek borç adlandırdı:** ① bayrakların açılma ölçütü yazılmamıştı — dördü
de artık *«hangi ölçüm görülünce `on`»* diyor ② `bicim.py` sınıflandırılmamıştı.

**Sonuç: `5038 passed, 57 skipped` — süit yeşil.**
⚠ `konuşma senaryoları` ⊘ **ölçülemedi** (ön koşul sağlanmadı — `cube+llm` yolu CI'da
kapalı); bu bir gerileme değil, **bilinen** bir ölçüm boşluğu.
