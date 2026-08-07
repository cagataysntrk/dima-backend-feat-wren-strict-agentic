# ⚠ BU DİZİN BİR **KOPYADIR** — kaynak `~/.claude/plans/`

> 🔴 **Yerleşim kuralına aykırı bir durum ve bilerek yazılıyor:** `00-INDEKS.md` bir
> belgenin yerini *"ne zaman bayatladığına"* göre belirler. Bu dizin o kurala girmiyor
> çünkü buradaki dosyalar **başka bir yerde yaşıyor** ve buraya **kopyalanıyor**.

## Neden kopyalandı

Planlar `~/.claude/plans/` altında tutuluyordu. Ölçülen üç zararı:

| # | Zarar | Kanıt |
|---|---|---|
| 1 | **Versiyonlanmıyor** | Plana `§6.Ω` bölümü enjekte edildi; `git add -A && git commit` *"işlenecek bir şey yok"* dedi. O değişikliğin tarihçesi **yok** — kim, ne zaman, geri alınabilir mi: hiçbiri kayıtlı değil |
| 2 | **Paylaşılmıyor** | Depo başka bir geliştiriciyle paylaşılıyor; `~/.claude/` kişisel bir dizin. `CLAUDE.md` planı **mutlak yolla** işaret ediyor — o yolu olmayan biri için o satır ölü |
| 3 | **Hiçbir kapı göremiyor** | Depo içi belgeler kapılarla denetleniyor (`test_beyanlar_curumesin` · `test_yol_haritasi_butunlugu`). Plan dışarıda olduğu için denetimsiz. Bedeli ölçüldü: `§13.6` *"beş şey"* deyip **altı** satır listeliyordu ve bu sayım hatası **kayıt #4'ün düşmesini kolaylaştırdı** |

## 🔴 KAYNAK HANGİSİ — ve neden bu bir BORÇ

**Kaynak hâlâ `~/.claude/plans/`.** `CLAUDE.md`'nin operasyon başlığı oraya işaret ediyor
ve o satır değiştirilmedi. Buradakiler **türev**dir.

⚠ Yani şu anda **aynı belgenin iki kopyası** var — ve bu, bu deponun adıyla andığı
*"aynı kuralın iki sahibi"* sınıfının belge tarafındaki hâlidir. Kopya, kaynağı
güncellendiğinde **sessizce bayatlar**.

> *Bir belgeyi kopyalamak, onu paylaşılabilir yapar ama iki gerçek yaratır; hangisinin
> gerçek olduğunu yazmazsan, altı ay sonra ikisi de değildir.*

**Kalıcı çözüm iki seçenekten biri** ve bir karar bekliyor:

1. **Taşı** — kaynak buraya gelir, `~/.claude/plans/` altındaki bir sembolik bağa
   dönüşür, `CLAUDE.md` göreli yola çevrilir. *(Önerilen: tek gerçek kalır.)*
2. **Kopya kal, ama kapıya bağla** — bir test iki dosyanın **aynı** olduğunu doğrular;
   ayrıştıkları gün kırmızı verir.

Bu karar verilene kadar **kaynak `~/.claude/plans/`'tır** ve buradaki kopya
**yalnız okuma amaçlıdır** — buradaki bir dosyayı düzenlemek, kaynağı güncellemez.

## Kopyalanan dosyalar

| dosya | kaynak | kopyalandığı an |
|---|---|---|
| `DIMA-GARSON-ARA-FAZ.md` | `~/.claude/plans/` | 2026-08-07 |
| `DIMA-V1-YOL-HARITASI.md` | `~/.claude/plans/` | 2026-08-07 |
