# Yol haritası — Konuşmaya dayalı BI (ADR-0007)

Tek-atış sorgu → **sohbet + canlı rapor**. Fazlı ilerlenir; her faz kendi başına çalışır.
Mevcut cube/router/chart altyapısı yeniden kullanılır (bkz. ADR-0004/0005).

## Faz A — UI iskeleti (estetik + split)
- [ ] İki bölmeli düzen: **solda sohbet**, **sağda canlı rapor** (grafik/tablo/KPI).
- [ ] Veri modeli (şema) ana yüzeyden çıkar → **Ayarlar** (drawer/modal) altına taşınır.
- [ ] Estetik geçiş: başlık çubuğu, boşluk/tipografi, kart tasarımı, koyu/açık tema.
- [ ] Mevcut tek-atış `ask` akışı yeni düzende çalışmaya devam eder (thread + sağ panel).

## Faz B — Konuşmasal durum (CubeQuery = rapor durumu)
- [ ] Client'ta evrilen **CubeQuery** durumu + sohbet geçmişi (stateless backend, ADR-0007 K5).
- [ ] Backend uç noktası: `{mevcut CubeQuery, mesaj, şema} → {yeni CubeQuery, netleştirme?}`.
- [ ] Düzenleme yorumlayıcı (deterministik-önce): boyut/filtre/dönem/dışlama ekle-çıkar;
      belirsiz ifade LLM'e. ("aylara göre", "elyaf kırılımı", "temmuzu çıkar").
- [ ] Sağ panel her turda yerinde güncellenir (yığmaz).

## Faz C — Clarification (belirsizlik → soru)
- [ ] Zorunlu slot (dönem) eksikse **chip'li soru**: [Bugün] [Bu hafta] [Bu ay] [Bu yıl] + serbest.
- [ ] Uygulanan dönem **daima görünür** (chip) + override edilebilir.
- [ ] Diğer belirsizlikler (ölçü/kırılım) için de genelleştirilebilir slot mantığı.

## Faz D — Çok-boyut, dışlama, parlatma
- [ ] İki boyutlu kırılımda otomatik gruplu/ısı grafiği (mevcut chart.ts genişletme).
- [ ] Dönem/kategori **dışlama** ("temmuzu çıkar", "iç piyasa hariç").
- [ ] Rapor dışa aktarma (PNG/CSV), kaydedilen raporlar, zamanlanmış worker'lar (uzun vade).

## Çapraz kesen
- [ ] Provenance: `source` rozeti + uygulanan dönem chip'i her raporda.
- [ ] Erişilebilirlik + mobil/dar ekran davranışı.
