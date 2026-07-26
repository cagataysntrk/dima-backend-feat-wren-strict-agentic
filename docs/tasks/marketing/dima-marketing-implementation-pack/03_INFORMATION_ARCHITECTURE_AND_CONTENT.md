# 03 — Information Architecture and Content System

## 1. Launch page map

### Primary launch pages

| URL | Rol | Primary CTA |
|---|---|---|
| `/` | Kategori, değer ve ürün proof | Demo talep et |
| `/product` | Ürün surfaces ve capability overview | Ürünü keşfet / Demo |
| `/how-it-works` | Trust pipeline ve teknik mekanizma | Teknik görüşme |
| `/solutions` | Persona/use-case index | Çözümü keşfet |
| `/solutions/textile-dyehouse` | Boyahane vertical proof | Boyahane demosu |
| `/security` | Güvenlik ve governance | Security görüşmesi |
| `/integrations` | Veri kaynağı ve deployment yaklaşımı | Entegrasyon görüşmesi |
| `/about` | Dima/UpcyTech hikâyesi | İletişim |
| `/contact` | Qualified demo request | Form gönder |
| `/privacy` | Gizlilik | — |
| `/terms` | Kullanım şartları | — |

### Secondary / gated pages

| URL | Karar |
|---|---|
| `/changelog` | Public-safe curated content varsa aç |
| `/pricing` | Fiyat modeli kesinleşene kadar oluşturma |
| `/blog` | İçerik operasyonu ve yayın sahibi belirlenmeden açma |
| `/docs` | Product docs ayrı domain/repo ise nav linki; boş placeholder açma |
| `/case-studies` | En az bir gerçek case study olmadan açma |

## 2. Global navigation

### Sol
- dima wordmark
- Product
- How it works
- Solutions
- Security
- Integrations

### Sağ
- TR/EN language
- Giriş yap
- Demo talep et

Mobil:
- Tek hamburger/menu sheet
- Focus trap
- Escape ile kapanma
- Route değişiminde kapanma
- CTA'lar menu içinde 44px target
- Scroll lock ve body layout shift önleme

## 3. Homepage section order

### 1. Announcement strip — opsiyonel
Yalnızca gerçek bir launch, beta veya etkinlik mesajı varsa. Kalıcı dekoratif banner kullanmayın.

### 2. Hero
- Eyebrow
- H1
- 2–3 satır subhead
- Primary + secondary CTA
- Trust/process strip
- Product proof visual

### 3. Product proof
Static/sanitized UI simulation:
- Soru: “Makine bazında OEE ve fire oranı nedir?”
- Modeled context selected
- Dry-plan verified
- Chart/table result
- SQL / trace toggle görünümü

Bu bölüm, dekoratif abstract illustration yerine gerçek ürün davranışını göstermelidir.

### 4. Four Dima pillars
D-I-M-A kartları. Her kart:
- tek cümle değer,
- mekanizma,
- status badge gerekiyorsa,
- ilgili deep-link.

### 5. How it works
Dört adım:
1. Bağlantı ve modelleme
2. Doğal dilde soru
3. Guard + dry-plan
4. Rapor, verify, reuse/schedule

### 6. Use-case gallery
- Operations
- Production/OEE
- Finance
- Sales/customer
- Inventory
- Executive reporting

Her kartta örnek soru olmalıdır; jenerik icon + metin yeterli değildir.

### 7. Textile/dyehouse vertical
- Parti ve reçete
- Makine/OEE
- Fire/kalite
- Su/enerji/kimyasal
- Sipariş/termin/sevkiyat

“Gerçek sektör terminolojisinden türetilmiş demo” ifadesi uygun; müşteri sistemiyle birebir entegrasyon iddiası doğrulanmadan yazılmamalı.

### 8. Trust architecture
Görsel pipeline:
User → Dima → Semantic Model → Guard/Dry Plan → Customer DB → Auditable Result

### 9. FAQ
Önerilen sorular:
- Dima bir chatbot mu?
- SQL'i kim doğruluyor?
- Veritabanım değişirse ne olur?
- Hangi veri kaynaklarını destekliyor?
- Yetkiler nasıl korunuyor?
- Dima mevcut BI aracımın yerine mi geçiyor?
- On-prem kullanılabilir mi?
- Bir demo nasıl çalışıyor?

Cevaplar status-aware olmalıdır.

### 10. Final CTA
“İlk gerçek iş sorunuzla başlayalım.”
- Demo talep et
- Giriş yap

## 4. Product page

Ürün sayfası feature dump değil, ürün workflow'u olmalıdır:

1. Ask — doğal dil input
2. Understand — semantic model/context
3. Validate — SQL/guard/dry-plan
4. Explore — chart/table/KPI/pivot
5. Verify — correct/wrong feedback and trace
6. Reuse — contract/schedule/notification, status-labeled
7. Govern — auth/permissions/audit
8. Integrate — data sources/deployment

Her section gerçek UI crop veya coded mockup ile desteklenmeli.

## 5. How It Works page

Teknik okuyucu için:

- Neden ham LLM text-to-SQL yetmez?
- Semantic model neyi çözer?
- Guard neden önemlidir?
- Dry-plan neyi doğrular, neyi garanti etmez?
- Query execution nasıl sınırlandırılır?
- SQL/provenance nasıl görünür?
- Tenant/permission sınırı nerede uygulanır?
- Data source onboarding nasıl işler?
- Planned thin-agent/on-prem model ayrı status ile.

## 6. Textile/Dyehouse page

### Hero
“Boyahanenizin üretim verisine iş dilinde erişin.”

### Gerçek soru örnekleri
- Bu ay makine bazında OEE nedir?
- En yüksek fire hangi aşamada?
- Vardiya × haftanın günü verimliliği nasıl değişti?
- Reçete bazında kimyasal maliyet katkısı nedir?
- Termin riski taşıyan siparişler hangileri?
- Su ve enerji tüketimi kilogram başına nasıl değişiyor?
- Renk sapması en yüksek parti ve reçeteler hangileri?

### Proof model
10 tablo/ilişkili demo modelinden görsel bir data map gösterilebilir; gerçek customer schema gösterilmemeli.

## 7. Security page content boundaries

Kullanılabilecek başlıklar:
- Session security
- Permission-aware UI
- Tenant isolation
- Read-only query guards
- Auditability
- Deployment architecture
- Responsible disclosure/contact

Kullanılmaması gereken:
- Sertifikasız badge
- “Bank-grade”
- “Military-grade”
- “Zero risk”
- Legal review olmadan GDPR/KVKK guarantee
- Planned on-prem'i current olarak göstermek

## 8. Contact/demo form

Minimum alanlar:
- Ad soyad
- İş e-postası
- Şirket
- Rol
- Veri kaynağı / ERP (opsiyonel)
- En önemli analiz ihtiyacı
- KVKK/privacy acknowledgement

Form:
- Server action veya mevcut backend'e özel endpoint.
- Honeypot + server validation + rate limit.
- Success state ve retry.
- PII analytics'e gönderilmez.
- Endpoint hazır değilse mailto yerine gerçek, izlenebilir lead flow kararı alınmalı.

## 9. Content source-of-truth

Önerilen model:
- UI copy: `messages/{locale}.json` altında `marketing.*`
- Uzun, sık güncellenen içerik: typed local content object veya MDX
- Feature/status: tek `src/content/marketing/capabilities.ts`
- Nav/footer: tek `src/content/marketing/navigation.ts`
- FAQ: tek typed source
- Claims: `status: "available" | "beta" | "planned"`

Aynı feature metni farklı sayfalarda kopyalanmamalı; merkezi content object'ten türetilmelidir.
