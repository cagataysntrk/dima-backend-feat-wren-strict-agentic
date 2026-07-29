# 02 — Positioning, Messaging and Claims

## 1. Positioning statement

> **dima**, işletme verilerine doğal dilde erişimi; modellenmiş iş bağlamı, doğrulanmış SQL ve izlenebilir raporlama akışıyla birleştiren güvenilir konuşmalı analitik platformudur.

Daha kısa form:

> **Verinle konuş. Cevabın nasıl üretildiğini gör.**

Kategori açıklaması:

> Conversational analytics / governed text-to-SQL / modeled business intelligence.

## 2. Mesaj hiyerarşisi

### Primary promise
Teknik ekip beklemeden iş sorularına cevap alın.

### Trust mechanism
LLM yalnızca önerir; sorgu semantik model, SELECT-only guard ve dry-plan katmanından geçer.

### Product proof
Kullanıcı SQL'i, veri kaynağını, raporu ve nasıl çözüldüğünü görebilir; sonucu doğrulayabilir ve tekrar kullanılabilir hale getirebilir.

### Vertical proof
Boyahane demosu; üretim, OEE, fire, vardiya, reçete, su/enerji, termin ve sevkiyat gibi gerçek sektör terimleriyle çalışır.

### Enterprise direction
Tenant isolation, permissions, audit, feature flags ve deployment topolojisi. Yalnızca gerçek ve doğrulanmış durumlar public claim olarak kullanılmalıdır.

## 3. Hero için önerilen copy

### Eyebrow
**Güvenilir konuşmalı analitik**

### H1
**İşletme verinizle konuşun. Cevabın nasıl üretildiğini görün.**

### Subhead
**dima, doğal dilde sorduğunuz soruları modellenmiş iş bağlamına dayalı SQL'e dönüştürür, sorguyu çalıştırmadan önce doğrular ve sonucu açıklanabilir bir rapor olarak sunar.**

### Primary CTA
**Demo talep et**

### Secondary CTA
**Giriş yap**

### Proof line
**Doğal dil → modeled context → dry-plan doğrulama → rapor**

Alternatif daha kısa H1:
- **Verinize sorun. Tahmine değil, doğrulanmış sorguya güvenin.**
- **İş sorusundan doğrulanmış rapora, tek akışta.**

## 4. D-I-M-A sütunlarının public anlatımı

### Deterministic
**LLM önerir; kurallar doğrular.**  
SQL yalnızca izin verilen okuma işlemlerine göre kontrol edilir ve dry-plan ile çalıştırılabilirliği doğrulanır.

### Intelligent
**İş dilinde sorular.**  
Kullanıcı tablo ve kolon adı bilmeden doğal dilde soru sorabilir.

### Modeled
**İş anlamı şemadan daha fazlasıdır.**  
Metrikler, ilişkiler, birimler ve onaylanmış tanımlar semantik modelde tutulur.

### Agentic
**Tek seferlik cevaptan tekrar kullanılabilir analitiğe.**  
Doğrulanan sorguların rapor, kontrat, zamanlama ve bildirim akışlarına dönüşmesi hedeflenir.

“Agentic” metni, production durumuna göre `Available`, `Beta` veya `Planned` etiketiyle kullanılmalıdır.

## 5. Claims truth matrix

Bu tablo kod ve dokümantasyondan çıkarılmış başlangıç sınıflandırmasıdır. Public launch öncesi ürün sahibi ve teknik sorumlu tarafından yeniden onaylanmalıdır.

| Claim | Önerilen statü | Public kullanım |
|---|---|---|
| Doğal dil → SQL → sonuç | Available | Kullanılabilir |
| SELECT/WITH-only guard | Available | Teknik “How it works” sayfasında |
| Dry-plan doğrulama | Available | Ana farklılaştırıcı |
| MDL semantic model | Available | Ana farklılaştırıcı |
| SQL görünürlüğü / trace | Available | Product proof |
| Tablo, chart, KPI, pivot | Available | Ekran görüntüsüyle |
| Auth + HTTP-only refresh | Available | Security sayfasında sade anlatım |
| MFA desteği | Available in backend | UI/production doğrulandıktan sonra |
| Tenant isolation / RLS | Implemented architecture | Security review sonrası |
| Audit log | Implemented architecture | Gerçek production kapsamı doğrulandıktan sonra |
| Verify/correct akışı | Available/Beta | Ürün içi duruma göre etiketli |
| Query contracts/replay | Beta | Yalnız gerçek UI akışı varsa |
| Scheduled reports | Beta | Kullanıcı erişimi ve delivery doğrulanırsa |
| Notifications | Beta | Kanal ve teslimat kapsamı belirtilmeli |
| 20+/22+ data sources | Engine capability | Dima production support listesi ayrı doğrulanmalı |
| Postgres connector | Available/configurable | Test edilen kapsam belirtilmeli |
| MSSQL/Oracle | Target/roadmap olabilir | Hazır gibi yazılmamalı |
| Raw data never leaves LAN | Planned thin-agent architecture | Hazır özellik gibi yazılmamalı |
| On-prem deployment | Architecture direction | Paket ve operasyon süreci hazırsa |
| SOC 2 / ISO 27001 | Unverified | Kullanılmamalı |
| GDPR/KVKK compliant | Legal review required | Kesin claim kullanılmamalı |
| “Hallucination-free” | Impossible absolute | Kullanılmamalı |
| “100% accurate” | Impossible absolute | Kullanılmamalı |

## 6. Proof policy

Her sayısal veya kurumsal kanıt için şu kuralları uygulayın:

- Müşteri logosu yalnızca yazılı izinle.
- Testimonial gerçek isim/rol/şirket ve onayla.
- “X soru”, “Y kullanıcı”, “Z saat tasarruf” gibi sayılar analytics veya imzalı case study ile.
- Demo ekranlarında yalnızca sentetik/boyahane demo verisi.
- Gerçek şirket/kişi e-postası, token, tenant slug veya veri görünmez.
- Security badge yalnızca gerçekten alınmış sertifikaya linklenebilir.
- Partner logoları yalnızca aktif ve izinli ilişki varsa.

## 7. Persona ve Jobs-to-be-Done

### Genel Müdür / Fabrika Müdürü
- Bugünkü üretim, fire, termin ve kapasiteyi görmek.
- Teknik rapor beklemeden istisnaları bulmak.
- Cevabın hangi veriye dayandığını görmek.

### Operasyon / Üretim Müdürü
- Makine, vardiya, personel ve reçete kırılımında OEE/verim analizi.
- Anomali ve kayıp nedenlerini karşılaştırmak.
- Tekrarlanan raporları standardize etmek.

### Finans / Ticari Ekip
- Ciro, brüt kâr, tahsilat, stok ve müşteri trendlerini sormak.
- KPI formülünü ve bileşenlerini görmek.
- Aynı metriğin farklı ekiplerde farklı hesaplanmasını önlemek.

### Data / IT
- Query governance, schema mapping ve permission sınırlarını korumak.
- Self-service taleplerini azaltmak.
- Üretilen SQL'in denetlenebilir olmasını sağlamak.

## 8. Tone of voice

- Net, teknik olarak doğru, abartısız.
- Türkçe doğal; teknik terimler gerektiğinde İngilizce bırakılabilir.
- “Sihir”, “devrim”, “her şeyi otomatik yapar” gibi belirsiz hype yok.
- “Nasıl çalışır?” sorusunu görseller ve mekanizma ile cevapla.
- Her section tek bir iddia taşır.
- Başlıklar kısa; body metni kanıta gider.
