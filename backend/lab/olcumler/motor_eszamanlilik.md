# MOTOR EŞ ZAMANLILIK — `FAZ 4`'ün ön koşulu (2026-08-09)

> Alet: `lab/motor_eszamanlilik.py` · şirket `demo-boyahane` · aynı `WrenService` örneği
> üzerinde `cube_sql → dry_plan → query` üçlüsü

| işçi | tur | seri | paralel | 🔴 hata | 🔴 sapma | hızlanma |
|---|---|---|---|---|---|---|
| 4 | 3 | 375 ms | 193·131·122 ms | **0** | **0** | **2,52×** |
| 8 | 5 | 714 ms | 352·425·381·439·324 ms | **0** | **0** | **1,86×** |

**Sapma** = paralel sonucun seri sonuçtan bayt farkı. Asıl ölçülen budur: hızlanma
ikincildir, **aynı cevabı** vermek birincil.

## Okuma

* 🟢 Yarış **görülmedi**: 32 eş zamanlı sorguda ne hata ne sapma.
* ⚠ İşçi 4→8'de hızlanma **düştü** (2,52× → 1,86×). Yani tavan **4**'tür; sekiz işçi
  yalnız çekişme ekliyor. Araştırmanın önerdiği tavan (4) ölçümle doğrulandı.
* 🔴 *«Görülmedi» ≠ «yok»*: bu bir **örneklemdir**. Bu yüzden paralellik bir bayrağa
  değil, **yapısal bir sınıra** bağlandı: yalnız `SORGU`, yalnız aynı DAG katmanında,
  tavan 4, çıktılar **adım sırasına** yazılır (tamamlanma sırasına değil).

## Neden bu ölçüm yapılmadan açılamazdı

Bu depo aynı dersi bir kez **ödedi**: iki test konteyneri paralel koşunca paylaşılan
derleme dizininde yarış çıktı ve süit **934 hata** verdi. Yasak sonradan **izolasyonla**
kalktı — yani çözüm *"paralel koşma"* değil, **yarışın olmadığını göstermek**ti.

⚠ Aracın kendi kusuru da bu ölçümde bulundu: ilk hâli `connection_info={}` ile servis
kuruyordu; şema okunuyor ama sorgu koşulmuyordu (`Catalog does not exist`). Yani alet
**ölçtüğünü sanıp hiçbir şey ölçmüyordu**. *Bir ölçüm aracının en tehlikeli kusuru
yanlış sayı vermek değil, sayı verdiğini sanmaktır.*

*Bir hızlanmayı, doğruluğunu ölçmeden satın almak, ölçmediğin bir borcu üstlenmektir.*
