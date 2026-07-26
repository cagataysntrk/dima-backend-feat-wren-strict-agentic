# DIMA MARKETING MASTER PLAN



---

<!-- BEGIN README.md -->

# dima Marketing Site Implementation Pack

**Hazırlanma tarihi:** 26 Temmuz 2026  
**Hedef repo:** `UpcyTech/dima-frontend`  
**Çalışma modeli:** Stage-by-stage, her aşama bağımsız doğrulanabilir  
**Referans repo:** `UpcyTech/upcyman`  
**Yerel, salt-okunur referans yolu:** `/Users/enesteve/Desktop/Coding/Upcy/upcyman/upcyman`

Bu paket, `dima-frontend` içinde profesyonel bir B2B SaaS / AI analytics marketing sitesi kurmak için hazırlanmış araştırma, mimari karar, içerik stratejisi, tasarım sistemi ve uygulama prompt setidir.

## Önerilen kullanım

1. Önce `DIMA_MARKETING_MASTER_PLAN.md` dosyasını okuyun.
2. AI coding agent oturumunun başında `MASTER_PROMPT.md` içeriğini verin.
3. Ardından yalnızca çalışılacak stage dosyasını verin.
4. Agent bir stage'i bitirmeden sonraki stage'e geçmesin.
5. Her stage sonunda `pnpm lint`, `pnpm build` ve ilgili testler çalıştırılsın.
6. Her stage ayrı commit veya ayrı PR olarak tutulabilsin; ancak agent kullanıcı açıkça istemedikçe commit/push yapmasın.

## Dosya haritası

| Dosya | Amaç |
|---|---|
| `00_RESEARCH_SYNTHESIS.md` | Repo ve internet araştırmasının sentezi |
| `01_REPOSITORY_ARCHITECTURE_AUDIT.md` | Mevcut teknik yapı, riskler ve korunacak sınırlar |
| `02_POSITIONING_AND_CLAIMS.md` | Mesajlaşma, ürün vaadi ve iddia doğruluk matrisi |
| `03_INFORMATION_ARCHITECTURE_AND_CONTENT.md` | Sayfa haritası, navigasyon ve içerik sistemi |
| `04_DESIGN_SYSTEM_DIRECTION.md` | Dima'ya özgü görsel dil ve UpcyMan'den alınacak dersler |
| `05_TARGET_TECHNICAL_ARCHITECTURE.md` | Route groups, provider ayrımı, auth ve SEO mimarisi |
| `06_QUALITY_SECURITY_SEO.md` | Erişilebilirlik, performans, test, güvenlik ve SEO kapıları |
| `MASTER_PROMPT.md` | Tüm oturumlarda kullanılacak ana agent talimatı |
| `AGENT_RUNBOOK.md` | Agent çalışma protokolü ve stage teslim formatı |
| `SOURCE_MAP.md` | İncelenen kaynaklar ve doğrulama haritası |
| `stages/` | Uygulama aşamalarının bağımsız prompt dosyaları |

## Stage sırası

0. Preflight ve repo audit
1. Route mimarisi ve auth sınırları
2. Marketing design system
3. Ortak marketing shell
4. Homepage
5. Product + How It Works
6. Solutions + Textile/Dyehouse vertical
7. Security + Integrations + Trust
8. Company + Resources + Legal + Contact
9. SEO + Analytics + Performance + Accessibility
10. Testing + Release + Handoff

## Temel karar özeti

- Marketing ana sayfası `/` olacaktır.
- Mevcut authenticated ürün arayüzü `/app` altına taşınacaktır.
- Marketing, product ve auth route'ları aynı projede fakat ayrı route group/layout sınırlarında tutulacaktır.
- Mevcut API, auth, refresh-cookie, tenant, konuşma ve rapor business logic'i yeniden yazılmayacaktır.
- Marketing sayfaları server-first olacaktır; yalnızca gerçekten etkileşim gereken küçük adalar client component olacaktır.
- UpcyMan kodu doğrudan dependency, symlink veya cross-repo import olarak kullanılmayacaktır. Yalnızca tasarım/composition referansı olarak okunacaktır.
- Sahte logo, sahte müşteri sayısı, sahte testimonial, sahte güvenlik sertifikası, kesinleşmemiş fiyat veya roadmap özelliğini “hazır” gösteren iddia kullanılmayacaktır.
- Dima'nın ayırt edici anlatısı: **LLM önerir; modellenmiş semantik katman ve doğrulama motoru karar verir.**

<!-- END README.md -->


---

<!-- BEGIN 00_RESEARCH_SYNTHESIS.md -->

# 00 — Araştırma Sentezi

## 1. Dima ürününün gerçek çekirdeği

Dima, yalnızca bir “chat with your data” arayüzü değildir. İncelenen repo yapısına göre ürünün asıl değeri dört katmandan oluşur:

1. **Doğal dil arayüzü:** Kullanıcı iş sorusunu doğal dille sorar.
2. **Modeled context:** Sorgu, yalnızca ham veritabanı şemasına değil, MDL semantik modele ve tanımlı ilişkilere dayanır.
3. **Deterministic validation:** LLM SQL önerir; SELECT-only guard ve dry-plan sorguyu çalıştırmadan önce doğrular.
4. **Reusable analytics workflow:** Sonuç tablo/grafik/KPI olarak gösterilir; doğrulama, sözleşme, tekrar çalıştırma ve zamanlama akışları ürünün güven katmanını oluşturur.

Marketing sitesi bu dört katmanı görünür kılmalıdır. “AI ile rapor alın” gibi jenerik bir başlık Dima'nın teknik farkını gizler.

## 2. Repo topolojisinin marketing açısından anlamı

### `dima-frontend`
Asıl ürün UI'ıdır. Next.js 16 App Router, React 19, Tailwind 4, next-intl, Motion, TanStack Query, Zustand ve same-origin API proxy kullanır. Mevcut `/` route'u authenticated chat/report ürünüdür.

### `dima-frontend-demo`
Core ekibin demo/koşum arayüzüdür. Marketing geliştirmesinin hedefi değildir. Ürün UI ile demo UI birbirine yeniden bağlanmamalı veya tek repo haline getirilmemelidir.

### `dima-backend`
FastAPI köprüsü, auth/control-plane, NL→SQL, dry-plan, query, schema, features, verify, contracts, schedules ve notifications uçlarını barındırır. Marketing iddiaları burada gerçekten bulunan yeteneklerden türetilmelidir.

### `dima-wrenai`
Wren tabanlı semantik SQL/context motorudur. Dima'nın “modeled” ve “deterministic” iddialarının teknik temelidir. Ancak Wren'in kendi web sitesindeki tüm connector/roadmap iddiaları Dima'da otomatik olarak production-ready kabul edilmemelidir.

### `dima-admin-frontend`
Public marketing'e hiçbir şekilde bağlanmaması gereken lokal-only superadmin panelidir. Marketing nav/footer içinde admin linki bulunmamalıdır.

### `dima-changelog`
Core ve UI ekipleri arasındaki değişiklik kaydıdır. Public changelog sayfası oluşturulursa private repo içeriği doğrudan yayınlanmamalı; yayınlanabilir, ürün odaklı ve secrets/operasyon detayı temizlenmiş bir içerik katmanı kullanılmalıdır.

### `dima`
Umbrella repo; ADR'ler, branding ve sistem topolojisinin source of truth'udur. Marketing çalışmasında ürün iddialarının teknik doğrulaması için ilk referanslardan biridir.

## 3. Mevcut frontend'in güçlü yönleri

- Tokenize edilmiş, OKLCH tabanlı light/dark design system.
- Plus Jakarta Sans, JetBrains Mono ve marketing için ayrılabilecek Playfair Display.
- Motion için hızlı, amaçlı ve reduced-motion uyumlu ortak preset'ler.
- Next.js 16, React 19 ve strict TypeScript.
- next-intl altyapısı mevcut.
- Auth token'ın memory'de, refresh token'ın HTTP-only cookie'de tutulduğu güçlü bir session modeli.
- Same-origin `/api/*` proxy sayesinde backend origin browser'a sızmıyor.
- Ürün içinde gerçek proof yaratabilecek chat, SQL trace, chart, table, KPI, pivot ve schema surfaces bulunuyor.

## 4. Mevcut frontend'in marketing açısından engelleri

1. `/` şu anda ürün uygulamasıdır.
2. Root `<body>` `h-full` ve `overflow-hidden` olduğu için uzun marketing sayfaları için uygun değildir.
3. Proxy, auth sayfaları dışındaki hemen her route'u korur; public marketing route'ları açılamaz.
4. Root provider katmanı refresh çağrısı, React Query ve product-only runtime davranışını public marketing sayfalarına da taşıyabilir.
5. E2E testi `/` üzerinde ürün landing/chat akışını bekler.
6. Login sonrası redirect ve session route semantiği `/` kabulüne bağlıdır.
7. Mevcut çeviri dosyalarında marketing namespace'i yoktur.
8. Root metadata yalnızca tek ürün başlığına göre tanımlanmıştır.

Bu nedenle marketing çalışması ilk olarak route/layout/provider sınırlarını güvenli biçimde ayırmalıdır.

## 5. Güncel kategori araştırmasından çıkarılan dersler

AI analytics / conversational BI kategorisindeki güçlü ürünler ortak olarak şunları vurguluyor:

- **Trusted / governed answers**
- **Semantic or context layer**
- **Natural-language self-service**
- **Explainability and query visibility**
- **Permission-aware access**
- **Concrete product proof**
- **Deployment and data-source fit**
- **Role/industry use cases**

Dima için en iyi farklılaşma şudur:

> Türkçe-first, operasyonel ve endüstriyel işletme verileri için; doğal dil rahatlığını modellenmiş iş bağlamı ve deterministic query validation ile birleştiren güvenilir analitik ürün.

## 6. UpcyMan'den alınacak ve alınmayacak şeyler

### Alınacak ilkeler

- MarketingNavbar → Hero → proof → feature grid → FAQ → CTA → Footer ritmi.
- Editorial heading ile modern sans body kombinasyonu.
- Feature mockup'larının gerçek ürün yüzeylerine dayanması.
- Bento grid'in her kartı farklı bir ürün kanıtı taşıyacak şekilde kullanılması.
- Tasarım token'larının tek source of truth olması.
- Lucide icon standardizasyonu.
- Mobile-first responsive spacing.
- i18n namespace ayrımı.
- Motion'ın section reveal ve microinteraction seviyesinde kalması.

### Kopyalanmayacak unsurlar

- UpcyMan'in yeşil marka paleti.
- Rainbow button, yoğun particles veya her section'da farklı “wow” efekti.
- UpcyMan'e ait metin, KPI, müşteri logosu veya feature claim'leri.
- Monorepo veya dependency mimarisi.
- Cross-repo import, symlink veya local path dependency.
- Kopyalanmış üçüncü taraf component kodu; gerekiyorsa lisansı doğrulanmış resmi kaynaktan minimal kurulum yapılmalıdır.

## 7. Önerilen marketing stratejisi

Marketing sitesi, klasik “özellik listesi” yerine **kanıt sıralaması** üzerine kurulmalıdır:

1. **Problem:** İş verisine cevap almak yavaş, teknik ve güvensiz.
2. **Promise:** Doğal dilde sor; modellenmiş bağlama dayalı, doğrulanmış cevap al.
3. **Proof:** Gerçek Dima UI simülasyonu; soru → query plan → dry-plan verified → chart/table.
4. **Mechanism:** Deterministic · Intelligent · Modeled · Agentic.
5. **Use cases:** Üretim, OEE, fire, satış, finans, stok, termin, müşteri.
6. **Vertical proof:** Boyahane/textile workflow.
7. **Trust:** Auth, tenant isolation, audit, query visibility, permission model.
8. **CTA:** Demo talep et / Giriş yap.

## 8. Yapılmaması gerekenler

- Ana ekranda yalnızca büyük slogan ve dekoratif animasyon bırakmak.
- “20+ data source” gibi engine yeteneğini Dima production connector garantisi olarak sunmak.
- “Veriniz şirketinizden çıkmaz” iddiasını on-prem thin agent tamamlanmadan hazır özellik gibi yazmak.
- SOC 2, ISO 27001, GDPR/KVKK uyumu veya “enterprise-grade security” gibi doğrulanmamış sertifika iddiaları.
- Sahte müşteri logosu/testimonial/countdown/availability.
- Public marketing'den gerçek backend'e anonymous query göndermek.
- Root route değişiminde auth, refresh cookie, e2e veya konuşma state güvenliğini bozmak.

<!-- END 00_RESEARCH_SYNTHESIS.md -->


---

<!-- BEGIN 01_REPOSITORY_ARCHITECTURE_AUDIT.md -->

# 01 — Repository Architecture Audit

## A. Mevcut teknoloji tabanı

| Alan | Mevcut durum | Marketing kararı |
|---|---|---|
| Framework | Next.js 16 App Router | Korunacak |
| Runtime UI | React 19 | Korunacak |
| Styling | Tailwind CSS 4 + CSS variables | Yeni design system bunun üzerine kurulacak |
| State | TanStack Query + Zustand | Marketing'e taşınmayacak |
| i18n | next-intl, cookie-locale, URL prefix yok | İlk fazda korunacak; marketing namespace eklenecek |
| Theme | next-themes | Marketing shell ile uyumlu kullanılacak |
| Motion | `motion/react` + shared presets | Sınırlı ve reduced-motion uyumlu |
| Icons | Lucide | Tek ikon sistemi olarak korunacak |
| API | Axios, same-origin `/api/*` route handler | Marketing public demo backend çağırmayacak |
| Auth | memory access token + HTTP-only refresh cookie | Aynen korunacak |
| E2E | custom browser/CDP test | Route migrasyonuna göre güncellenecek |

## B. Kritik korunacak business logic

Aşağıdaki alanlar marketing çalışması sırasında refactor bahanesiyle yeniden yazılmamalıdır:

- `src/lib/api-client.ts`
- auth refresh/retry zinciri
- session cookie adı ve normalization
- `src/stores/conversations.ts`
- logout/login sırasında conversation reset güvenlik düzeltmesi
- ask / cube / verify / schedule / notification çağrıları
- report/chart/table/KPI/pivot analiz davranışı
- `/api/[...path]` route handler
- permission-based UI görünürlüğü
- tenant/session semantiği
- feature flags
- product E2E'nin API doğrulama bölümü

## C. Route kaynaklı riskler

### Risk 1 — `/` ürün route'u
Marketing'in `/` olması için product page taşınmalıdır. Dosyanın kopyalanıp eski route'un bırakılması iki farklı state entrypoint oluşturur. Doğru çözüm, tek product entrypoint'i `/app` altına taşımaktır.

### Risk 2 — Proxy
Mevcut proxy “auth dışındaki her şeyi koru” yaklaşımındadır. Marketing için çok sayıda public route eklemek, büyüyen allowlist'i hata eğilimli hale getirir. Önerilen konvansiyon:

- Tüm protected product route'ları `/app/**` altında.
- Proxy matcher yalnızca `/app/:path*` ve session-aware auth route'larını kapsar.
- Marketing route'ları proxy auth logic'ine girmez.
- `/api/**` güvenliği backend/token katmanında kalır.
- Unknown public route, login redirect yerine gerçek 404 gösterebilir.

### Risk 3 — Root layout overflow
Root body marketing için:
`min-h-screen bg-background text-foreground`

Product layout:
`h-dvh overflow-hidden`

Bu ayrım route-group layout'unda yapılmalıdır.

### Risk 4 — Root providers
Public marketing route'larında otomatik refresh çağrısı ve product QueryClient bootstrap istemiyoruz. Provider'lar iki gruba ayrılmalıdır:

- **Global/lightweight:** locale, theme, reduced-motion gibi tüm siteye gerekenler.
- **Product runtime:** QueryClient, AuthBootstrap, product Tooltip/Toaster ve diğer app runtime ihtiyaçları.

Bu refactor sırasında hydration ve theme flash test edilmelidir.

## D. Önerilen klasör sınırları

```text
src/
├── app/
│   ├── layout.tsx
│   ├── sitemap.ts
│   ├── robots.ts
│   ├── manifest.ts
│   ├── (marketing)/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── product/page.tsx
│   │   ├── how-it-works/page.tsx
│   │   ├── solutions/page.tsx
│   │   ├── solutions/textile-dyehouse/page.tsx
│   │   ├── security/page.tsx
│   │   ├── integrations/page.tsx
│   │   ├── about/page.tsx
│   │   ├── changelog/page.tsx
│   │   ├── contact/page.tsx
│   │   ├── privacy/page.tsx
│   │   └── terms/page.tsx
│   ├── (product)/
│   │   └── app/
│   │       ├── layout.tsx
│   │       └── page.tsx
│   └── (auth)/
│       ├── login/page.tsx
│       ├── register/page.tsx
│       └── forgot-password/page.tsx
├── components/
│   ├── marketing/
│   │   ├── layout/
│   │   ├── sections/
│   │   ├── proof/
│   │   └── ui/
│   ├── shell/
│   └── ui/
├── content/
│   └── marketing/
├── lib/
│   ├── marketing/
│   └── ...
└── i18n/
```

Route group adları URL'e girmez.

## E. Dependency politikası

### Öncelik sırası
1. Mevcut component ve dependency ile çöz.
2. Küçük bir component'i local ve dependency-free yaz.
3. Resmi shadcn/MagicUI kaynağından lisansı doğrulanmış minimal primitive ekle.
4. Yeni ağır dependency yalnızca ölçülmüş gerekçeyle.

### Marketing route'larına import edilmemesi gerekenler
- `@tanstack/react-query`
- Zustand product stores
- `@xyflow/react`
- Recharts/ECharts gibi chart runtime'ları, gerçek ihtiyaç yoksa
- product API client
- auth bootstrap
- WebGL / Three / canvas particle dependency'leri

Bir görsel proof için statik HTML/CSS mockup veya optimize screenshot yeterliyse chart runtime gönderilmemelidir.

## F. İ18n kararı

Mevcut yapı locale'i cookie'den çözüyor ve URL prefix kullanmıyor. İlk marketing release için:

- Türkçe canonical içerik.
- `messages/tr.json` ve `messages/en.json` altında `marketing` namespace.
- Dil switch mevcut mekanizmayla çalışabilir.
- Aynı URL'de cookie ile değişen dil için `hreflang` üretilmez.
- İngilizcenin ayrıca indexlenmesi istenirse, route-based locale migration ayrı bir ADR/stage olmalıdır.

## G. E2E migrasyonu

Mevcut test:
- `/` açar,
- product H1 arar,
- example query butonuna tıklar,
- ürün akışını doğrular.

Yeni test seti:
1. `/` public marketing smoke.
2. `/app` no-session → `/login?next=/app`.
3. Login/session sonrası `/app`.
4. Product browser flow artık `/app` üzerinde.
5. `/product`, `/how-it-works`, `/security`, `/solutions/textile-dyehouse` 200.
6. Marketing nav keyboard test.
7. 404 public kalır.
8. `/api` behavior değişmez.

## H. Güvenli migrasyon sırası

1. Baseline test çıktısını kaydet.
2. `/app` route'unu ekle fakat `/` geçici olarak product redirect olabilir.
3. Login/proxy/E2E'yi `/app` semantiğine geçir.
4. Product smoke test geçince `/` marketing page olsun.
5. Root/provider/layout ayrımını yap.
6. Marketing shell ve sayfaları ekle.
7. SEO ve production release.

Bu sıra, “önce marketing'i yazıp sonra auth kırığını çözme” riskini azaltır.

<!-- END 01_REPOSITORY_ARCHITECTURE_AUDIT.md -->


---

<!-- BEGIN 02_POSITIONING_AND_CLAIMS.md -->

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

<!-- END 02_POSITIONING_AND_CLAIMS.md -->


---

<!-- BEGIN 03_INFORMATION_ARCHITECTURE_AND_CONTENT.md -->

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

<!-- END 03_INFORMATION_ARCHITECTURE_AND_CONTENT.md -->


---

<!-- BEGIN 04_DESIGN_SYSTEM_DIRECTION.md -->

# 04 — Design System Direction

## 1. Creative direction

**Editorial Industrial Intelligence**

Dima'nın marketing görünümü:
- sofistike fakat gösterişsiz,
- veri ve doğrulama hissi veren,
- endüstriyel yazılım güveni taşıyan,
- sıcak editorial yüzeylerle teknik monospaced detayları birleştiren,
- gerçek ürün proof'unu dekorasyonun önüne koyan
bir dil olmalıdır.

## 2. Existing tokens as foundation

Mevcut Dima token'ları zaten güçlü bir temel sağlar:

- Warm off-white light background
- Editorial near-black dark background
- Monochrome primary
- Indigo-violet brand accent
- OKLCH color authoring
- Hairline borders
- Subtle shadows
- Chart palette
- `--font-sans`, `--font-mono`, `--font-display`

Marketing yeni, paralel bir renk sistemi üretmemeli. Gerekirse yalnızca semantic marketing token alias'ları eklenmeli:

```css
--marketing-surface-raised
--marketing-surface-inverse
--marketing-grid
--marketing-proof-glow
--marketing-section-rule
```

Bunlar mevcut root tokens'tan türemelidir.

## 3. Typography

### Display
Playfair Display yalnızca:
- hero H1,
- büyük section statement,
- kısa editorial quote
için.

### Sans
Plus Jakarta Sans:
- navigation,
- body,
- card headings,
- forms,
- CTA,
- FAQ.

### Mono
JetBrains Mono:
- SQL,
- query status,
- source labels,
- “dry-plan verified”,
- metric/code labels.

### Scale
Öneri:
- Hero: clamp(3rem, 7vw, 6.5rem), çok uzun Türkçe satırlarda kontrollü.
- H2: clamp(2rem, 4vw, 4.25rem).
- H3: 1.25–1.5rem.
- Body large: 1.125–1.25rem.
- Body: minimum 1rem.
- Eyebrow: 0.75rem uppercase/letter spacing, erişilebilir contrast.

Line length:
- Body max 65–75 karakter.
- Hero subhead max 55–65 karakter.

## 4. Layout

### Grid
- Max content width: 1200–1280px.
- Reading column: 680–760px.
- Desktop 12-column grid.
- Tablet 6-column.
- Mobile single-column.
- Section spacing: 96–144px desktop, 64–96px mobile.
- Header fixed/sticky ise page offset ve focus visibility test edilmeli.

### Section rhythm
Alternating:
- open editorial section,
- bordered proof surface,
- dense bento/use-case section,
- open trust section.

Her section'ın aynı card grid görünümüne dönüşmesinden kaçının.

## 5. Component grammar

### MarketingSection
- semantic `section`
- optional eyebrow/title/description
- predictable spacing
- anchor `scroll-mt-*`

### ProofFrame
- browser/app frame
- data source status
- query prompt
- validation timeline
- result view
- optional callout annotations

### PillarCard
- Letter D/I/M/A
- single mechanism
- status
- deep link

### EvidenceLabel
Monospace mini label:
- `MODELED`
- `SELECT ONLY`
- `DRY-PLAN VERIFIED`
- `TENANT SCOPED`

### CTA
- Primary: brand/ink high contrast
- Secondary: outline/ghost
- No rainbow
- No constant shimmer
- Hover transform max 1–2px, no layout shift

### Bento
Bento yalnızca farklı content density gerekiyorsa:
- large proof card
- narrow process card
- metric/card sample
- integration map
- trace snippet

## 6. Motion language

Mevcut Dima motion prensiplerini koruyun:

- transform + opacity
- fast ease-out
- 150–300ms microinteraction
- 350–550ms section reveal
- one-time viewport animation
- no scale-from-zero
- no continuous animation except subtle status pulse
- `prefers-reduced-motion` respected
- motion is never the sole carrier of meaning

Hero:
- text stagger minimal,
- proof frame enters after copy,
- no particle canvas,
- no scroll-jacking,
- no auto-rotating headline required.

## 7. Product proof visual

En güçlü visual bir “real UI choreography” olmalıdır:

1. Prompt typed or revealed.
2. Context tags appear.
3. Validation steps show.
4. Result chart/table renders.
5. SQL/trace detail is visible.

Public page gerçek API'ye bağlanmamalı. Bu akış:
- static typed data,
- deterministic local state,
- no PII,
- no network dependency,
- reduced-motion'da final state
ile çalışmalıdır.

## 8. UpcyMan reference protocol

Agent şu local path'i salt-okunur inceleyebilir:

`/Users/enesteve/Desktop/Coding/Upcy/upcyman/upcyman`

Öncelikli referanslar:
- marketing page composition
- navbar/footer
- hero structure
- bento grid
- feature mockups
- responsive section spacing
- i18n organization
- reduced-motion and animation primitives

Kurallar:
1. UpcyMan'de hiçbir dosyayı değiştirme.
2. Symlink oluşturma.
3. Cross-repo import yapma.
4. Dima repo'suna büyük klasör kopyalama.
5. Component fikrini Dima tokens ve semantics ile yeniden uygula.
6. Third-party primitive ise resmi source ve license'ı kullan.
7. UpcyMan brand/copy/assets taşınmaz.

## 9. Anti-patterns

- Her kartta glow/border beam.
- Hero'da canvas particles + grid + gradient + moving beam aynı anda.
- Çok sayıda font.
- Gradient text'in ana H1 okunabilirliğini bozması.
- Küçük muted text.
- Desktop screenshot'ı mobile'da sadece küçültmek.
- Hover-only content.
- Carousel içinde kritik bilgi.
- Infinite marquee içinde okunması gereken metin.
- Mockup'larda sahte/gerçek dışı numbers.
- Farklı sayfalarda farklı radius/shadow sistemi.

<!-- END 04_DESIGN_SYSTEM_DIRECTION.md -->


---

<!-- BEGIN 05_TARGET_TECHNICAL_ARCHITECTURE.md -->

# 05 — Target Technical Architecture

## 1. Route architecture

```text
app/
  layout.tsx                    # neutral global root
  (marketing)/
    layout.tsx                  # public, scrollable, marketing shell
    page.tsx                    # /
    product/page.tsx
    how-it-works/page.tsx
    ...
  (product)/
    app/
      layout.tsx                # h-dvh, product providers, noindex
      page.tsx                  # moved current product root
  (auth)/
    login/page.tsx
    register/page.tsx
    forgot-password/page.tsx
```

## 2. Root layout responsibilities

Root layout yalnızca:
- `<html lang>`
- global fonts
- global CSS
- lightweight global providers
- metadata defaults
taşımalıdır.

Root body:
- `min-h-screen`
- scroll'u engellemez
- product-specific flex/overflow class taşımaz

## 3. Product layout responsibilities

- `h-dvh`
- `overflow-hidden`
- QueryClient
- AuthBootstrap
- product shell assumptions
- noindex metadata
- any app-only tooltip/toaster runtime
- error boundary if needed

## 4. Marketing layout responsibilities

- Marketing navbar
- main landmark
- footer
- skip-to-content
- scrollable body
- public-safe providers
- optional structured data
- no auth refresh request
- no product store initialization

## 5. Server-first boundary

Pages ve statik sections default Server Components olmalıdır.

Client Components yalnızca:
- mobile navigation
- theme/language interactive control
- FAQ accordion if needed
- contact form state
- deterministic product proof animation
- minimal viewport reveal wrapper

Aşağıdaki pattern'den kaçının:
- tüm homepage'e `"use client"`
- tüm content'i client translation hook ile render etmek
- client component içinden statik metin listeleri üretmek
- marketing route'a QueryClient/Zustand taşımak

## 6. Auth and proxy policy

Protected convention:
- tüm ürün route'ları `/app/**`
- auth pages `/login`, `/register`, `/forgot-password`

Proxy:
- `/app/:path*` için cookie kontrolü
- no session → `/login?next=<path>`
- session + auth page → `/app`
- expired flag logic korunur
- marketing route'ları auth redirect'e girmez

Security note:
- proxy yalnızca page access gate'tir.
- API authorization backend Bearer/tenant/permission katmanında kalır.
- marketing public oluşu API'yi public yapmaz.

## 7. Redirect and link migration

Güncellenecek noktalar:
- login success redirect
- auth-page-with-session redirect
- logout redirect
- logo/home links
- search/new chat assumptions
- any `router.push("/")`
- E2E `FRONTEND_URL`
- docs/readme route descriptions
- metadata canonical
- error pages

Repo genelinde exact search:
- `href="/"`
- `router.push("/")`
- `router.replace("/")`
- `pathname === "/"`
- `redirect("/")`
- `next=/`

Her eşleşme bağlamıyla incelenmeli; kör replace yapılmamalı.

## 8. Content architecture

```ts
type CapabilityStatus = "available" | "beta" | "planned";

type MarketingCapability = {
  id: string;
  title: string;
  summary: string;
  status: CapabilityStatus;
  evidence?: {
    repoPath?: string;
    demoRoute?: string;
  };
};
```

Amaç:
- aynı claim'in farklı sayfalarda farklı status ile görünmesini önlemek,
- roadmap claim'lerini açıkça etiketlemek,
- launch öncesi claim review yapmak.

## 9. Asset architecture

```text
public/marketing/
  brand/
  product/
  industries/textile/
  og/
```

Kurallar:
- SVG logolar optimize.
- Screenshot'lar demo/sanitized.
- `next/image`.
- Dimensions sabit.
- Alt text content source'ta.
- Filenames semantic ve kebab-case.
- Büyük video gerekiyorsa poster + user initiated playback.
- LCP hero visual tek ve optimize.

## 10. SEO architecture

- `NEXT_PUBLIC_SITE_URL` veya server env ile `metadataBase`.
- Root title template.
- Her sayfada unique title/description.
- canonical.
- Open Graph/Twitter.
- `sitemap.ts`.
- `robots.ts`.
- `/app`, `/api`, auth noindex/disallow.
- Organization JSON-LD.
- SoftwareApplication JSON-LD yalnızca factual fields.
- FAQ structured data yalnızca görünür içerikle birebir ve policy uygunsa.
- Cookie-based TR/EN için hreflang yok.

## 11. Error and loading states

Marketing:
- custom 404.
- contact form validation.
- no skeleton needed for static content.
- optional dynamic content için stable dimensions.

Product:
- mevcut loading/error behavior korunur.
- route migration nedeniyle yeni hydration flash oluşmamalı.

## 12. Deployment

- Vercel config korunur.
- Backend origin server-side kalır.
- Marketing build backend erişimi gerektirmemeli.
- Static generation mümkün olan tüm public pages için.
- Contact endpoint/network unavailable olsa bile homepage build'i bozulmamalı.
- Preview deployment'ta robots noindex kararı değerlendirilmeli.

<!-- END 05_TARGET_TECHNICAL_ARCHITECTURE.md -->


---

<!-- BEGIN 06_QUALITY_SECURITY_SEO.md -->

# 06 — Quality, Security, SEO and Release Gates

## 1. Definition of Done

Bir marketing stage yalnızca görsel olarak tamamlandığında bitmiş sayılmaz. Aşağıdaki kapılar geçmelidir:

- TypeScript strict compile
- ESLint
- production build
- route/auth regression
- responsive checks
- keyboard navigation
- reduced motion
- metadata/SEO
- no false claims
- no sensitive asset
- no product business logic regression

## 2. Performance budgets

### Mimari bütçe
- Marketing route'ları React Query, Zustand, React Flow ve chart runtime import etmez.
- WebGL/Three/particle canvas yok.
- Hero LCP element tek ve ölçülü.
- Fonts `next/font`.
- Images `next/image`, width/height reserved.
- Below-fold assets lazy.
- Client component adaları küçük.
- Heavy interactive proof dynamic import edilebilir, stable placeholder ile.

### Outcome targets
75. percentile field target:
- LCP ≤ 2.5s
- INP ≤ 200ms
- CLS ≤ 0.1

Lab target:
- Lighthouse mobile Performance ≥ 90
- Accessibility ≥ 95
- Best Practices ≥ 95
- SEO ≥ 95

Skorlar çevreye göre değişebilir; temel amaç stage öncesine göre regresyon yaratmamaktır.

## 3. Accessibility target

WCAG 2.2 AA baseline:

- Semantic landmarks.
- Tek H1.
- Logical heading order.
- Skip link.
- Keyboard-operable nav, menu, accordion, form.
- Visible focus; tercihen 2px solid perimeter ve 3:1 contrast.
- Minimum pointer target 24×24px; primary controls için practical 44×44px.
- Focus sticky header/modal altında kalmaz.
- Body text contrast minimum.
- Color tek bilgi taşıyıcısı değildir.
- Reduced motion.
- Images alt text.
- Decorative SVG `aria-hidden`.
- Form errors field ile programmatically associated.
- Status messages announced.
- No autoplay audio/video.
- 200% zoom ve 320px reflow.

## 4. Security gates

- Public page backend origin göstermemeli.
- Anonymous product query endpoint açılmamalı.
- Contact form server validation.
- Rate limit / honeypot / anti-abuse.
- User-provided content HTML olarak render edilmez.
- External links `rel` policy.
- No API key in `NEXT_PUBLIC_*`.
- No real customer data/screenshots.
- No admin URL/navigation.
- CSP eklenirse önce Report-Only ve Next/Motion inline style compatibility ölçümü.
- Existing security headers korunur.
- Dependency eklenirse license ve vulnerability kontrolü.

## 5. Auth regression matrix

| Durum | URL | Beklenen |
|---|---|---|
| Logged out | `/` | Marketing 200 |
| Logged out | `/product` | Public 200 |
| Logged out | `/app` | `/login?next=/app` |
| Logged in | `/login` | `/app` |
| Expired cookie flag | `/login?expired=1` | Cookie temizlenir, login görünür |
| Logged in | `/app` | Product app |
| Logged out | unknown URL | Public 404, login redirect değil |
| Any | `/api/*` | Existing proxy/backend auth semantics |

## 6. SEO checklist

- Unique title, description.
- Canonical.
- Open Graph 1200×630.
- Social image has safe margins and readable text.
- Sitemap only indexable public routes.
- Robots blocks app/auth/API.
- Product and auth `noindex`.
- JSON-LD validates.
- Internal link graph.
- No empty/duplicate pages.
- Turkish copy spellchecked.
- English copy human-reviewed before indexing.
- Site URL env correct in preview/prod.
- 404 returns real 404 status.

## 7. Analytics policy

Provider bağımsız event schema:

```text
marketing_page_view
marketing_nav_clicked
marketing_cta_clicked
marketing_demo_form_started
marketing_demo_form_submitted
marketing_demo_form_failed
marketing_faq_opened
marketing_product_proof_interacted
```

Event properties:
- page
- placement
- locale
- campaign/utm
- device class

Gönderilmemesi gereken:
- query content
- email/name/company
- database/schema name
- tenant slug
- SQL
- free-form form message

Consent ve privacy metni provider seçimine göre uygulanmalıdır.

## 8. Visual QA matrix

Viewport:
- 320×568
- 375×812
- 768×1024
- 1024×768
- 1440×900
- 1920×1080

Theme:
- light
- dark
- system

Language:
- TR
- EN, mevcutsa

Input:
- keyboard
- pointer
- touch simulation

Browser:
- Chromium
- Safari/WebKit
- Firefox

## 9. Test commands

Mevcut scriptlere göre:

```bash
pnpm lint
pnpm build
pnpm e2e
```

Stage 9/10'da mümkünse:
```bash
# Repo'ya uygun test tooling varsa
pnpm test
pnpm test:e2e
pnpm lighthouse
```

Olmayan script uydurulmaz; agent önce `package.json` kontrol eder.

## 10. Release checklist

- Clean git diff review.
- No debug logs.
- No temporary copy.
- No placeholder link.
- Forms point to production-safe endpoint.
- OG image current.
- Sitemap/robots current.
- Preview smoke.
- Production env.
- Rollback commit/PR identifiable.
- Product login/query/report smoke.
- Changelog entry.
- Owner sign-off on claims.
- Security sign-off on Security page.
- Legal sign-off on privacy/terms.

<!-- END 06_QUALITY_SECURITY_SEO.md -->


---

<!-- BEGIN 07_COMPETITIVE_BEST_PRACTICE_RESEARCH.md -->

# 07 — Competitive and Best-Practice Research

## 1. Research goal

The goal was not to copy a competitor page. The goal was to understand what the current AI analytics / conversational BI category has trained buyers to expect, then identify where Dima should conform and where it should diverge.

## 2. Category pattern: natural language is no longer enough

Across current category leaders, “ask a question in plain English” is table stakes. Stronger products increasingly emphasize:

- governed or trusted answers,
- a semantic/context layer,
- permissions,
- explainability,
- reusable workflows,
- integration with the existing data stack,
- visible product evidence.

Therefore, Dima's homepage should not lead with “AI can write SQL.” It should lead with the trust architecture around that SQL.

## 3. WrenAI pattern

WrenAI positions itself around an open context layer and governed BI for agents. Its strongest reusable lesson is:

- schema alone is not business meaning,
- approved definitions and relationships need a reviewable layer,
- agents need deterministic primitives, not only prompt instructions.

Dima should translate this into a customer-facing workflow rather than presenting itself as a developer engine:

> Dima understands the modeled business meaning, validates the query, and presents a traceable answer inside an end-user product.

Avoid reusing Wren's exact “Generate · Deploy · Know” framework or implying all Wren OSS capabilities are production-ready in Dima.

## 4. ThoughtSpot pattern

ThoughtSpot's current messaging uses AI analytics, natural-language exploration and trust/governance. The lesson is that enterprise buyers expect:

- permissions and governance,
- broad self-service,
- embedded/product workflows,
- security proof.

Dima should not try to out-broaden ThoughtSpot. It should be more concrete:
- Turkish-first,
- operational data,
- modeled SQL validation,
- textile/dyehouse proof,
- inspectable SQL and query lifecycle.

## 5. Hex pattern

Hex presents a collaborative workspace that combines analysis, notebooks, apps and AI. The lesson is product proof: the site shows the actual working surface and how different roles collaborate.

Dima should similarly show:
- real prompt,
- plan,
- validated query,
- report,
- follow-up,
rather than abstract AI gradients.

Dima should not imitate notebook positioning; its advantage is a simpler business-user workflow.

## 6. Omni pattern

Omni emphasizes a governed semantic model combined with flexible exploration and AI. The relevant lesson:

- semantic model should appear as a value enabler, not an implementation burden,
- governance and self-service can coexist.

Dima's copy should explain “modeled” in business language:
- metric definitions,
- joins,
- units,
- approved logic,
not only “MDL.”

## 7. Metabase pattern

Metabase historically wins on accessibility and fast self-service. Its AI messaging extends an already understandable BI product.

The lesson:
- do not let AI terminology obscure the basic job,
- show that users can get a table, chart or dashboard quickly,
- keep the interface approachable.

Dima should use its technical trust mechanism beneath a very simple top-level promise.

## 8. Seek AI pattern

Seek AI focuses on natural-language data access and data-team productivity. The lesson is to address both:
- business users want fast answers,
- data teams want control and reduced ad-hoc workload.

Dima's persona narrative should explicitly include IT/data owners, not only factory managers.

## 9. Recommended category conformity

Dima should include expected buyer information:

- Product
- How it works
- Solutions
- Security
- Integrations
- Contact/demo
- visible login
- real screenshots
- deployment/data source explanation
- FAQ
- legal pages

## 10. Recommended differentiation

Dima should own:

1. **Deterministic trust pipeline**
   `Question → modeled context → guarded SQL → dry-plan → result`

2. **Inspectable answer**
   SQL, trace, source and result are visible.

3. **Operational/industrial proof**
   OEE, fire, recipe, energy, deadline, shipment.

4. **Turkish-first product language**
   Not a translated generic US SaaS page.

5. **Reusable analytics**
   Verify, contract, schedule and notification with honest status labels.

## 11. Landing-page best practices derived from research

### Above the fold
- One category statement.
- One differentiator.
- One primary CTA.
- Immediate proof.
- No overloaded logo cloud.

### Product proof
- Use a realistic task.
- Show state transitions.
- Annotate the trust mechanism.
- Keep the visual legible on mobile.
- Avoid video-only explanation.

### Information scent
Navigation labels should be conventional. Clever labels reduce discoverability.

### Conversion
For an early B2B product:
- Primary: Demo request.
- Secondary: Login.
- Optional tertiary: See how it works.
Pricing should not be invented.

### Trust
Use mechanism proof before compliance badges:
- read-only query policy,
- modeled context,
- permission boundary,
- auditability,
- query visibility.

## 12. Next.js implementation best practices

Official App Router guidance supports:

- layouts/pages as Server Components by default,
- Client Components only for state, event handlers and browser APIs,
- route groups to organize layouts without changing URLs,
- route-level metadata and generated OG assets,
- `next/font` and `next/image`,
- production build and performance validation.

For Dima this means:
- marketing sections are server-rendered,
- product proof animation is a small client island,
- product providers stay outside marketing,
- route groups isolate scroll/runtime assumptions.

## 13. Web performance best practices

Core Web Vitals targets:
- LCP at or below 2.5 seconds,
- INP at or below 200 milliseconds,
- CLS at or below 0.1,
measured at the 75th percentile.

Dima-specific implications:
- no product chart bundle on homepage,
- no canvas particle field,
- reserve screenshot dimensions,
- keep hero image optimized,
- avoid client-rendering all marketing copy,
- keep sticky header from creating layout shifts.

## 14. WCAG 2.2 implications

WCAG 2.2 AA adds particular relevance for:
- focus not obscured,
- dragging alternatives,
- minimum target sizing,
- accessible authentication.

Implementation targets:
- 24×24px minimum pointer target or required spacing,
- 44×44px practical target for primary controls,
- visible focus, ideally a clear 2px perimeter,
- keyboard menu and accordion,
- no focus hidden by sticky header,
- no CAPTCHA/cognitive test without accessible alternative,
- reduced motion and predictable focus behavior.

## 15. Structured data

Use only structured data matching visible, factual content:
- Organization
- SoftwareApplication

Do not add:
- aggregateRating without real reviews,
- offers/pricing without actual public price,
- FAQ schema for hidden or mismatched content,
- fake award/certification fields.

## 16. Competitive anti-copy rule

Do not reproduce:
- competitor headlines,
- distinctive animations,
- illustrations,
- comparison tables,
- customer logos,
- screenshots,
- proprietary UI code.

Research informs strategy; Dima implementation must be original.

<!-- END 07_COMPETITIVE_BEST_PRACTICE_RESEARCH.md -->


---

<!-- BEGIN 08_PAGE_COPY_BLUEPRINT.md -->

# 08 — Page Copy Blueprint

This is a working copy blueprint, not final legal/commercial approval. All copy must be checked against `02_POSITIONING_AND_CLAIMS.md`.

## Homepage

### Hero
**Eyebrow:** Güvenilir konuşmalı analitik

**Headline:** İşletme verinizle konuşun. Cevabın nasıl üretildiğini görün.

**Subhead:** dima, doğal dilde sorduğunuz soruları modellenmiş iş bağlamına dayalı SQL'e dönüştürür, sorguyu çalıştırmadan önce doğrular ve sonucu açıklanabilir bir rapor olarak sunar.

**Primary CTA:** Demo talep et  
**Secondary CTA:** Giriş yap

**Process line:** Doğal dil → Modeled context → Dry-plan doğrulama → Rapor

### Product proof
**Prompt:** Makine bazında OEE ve fire oranı nedir?

**Context labels:**
- Vardiya kayıtları
- Makineler
- Partiler
- OEE
- Fire oranı

**Validation labels:**
- Soru çözümlendi
- Semantic model eşleşti
- SELECT-only guard geçti
- Dry-plan doğrulandı
- Sonuç üretildi

### Pillars introduction
**Heading:** Güven, yalnızca doğru görünen bir cevaptan gelmez.

**Body:** dima'nın her cevabı; iş anlamını taşıyan model, sorgu güvenlik sınırları ve görünür bir çözüm izi üzerinde oluşur.

#### Deterministic
LLM sorguyu önerir. Guard ve dry-plan çalıştırılabilir, izinli sorguyu doğrular.

#### Intelligent
Tablo ve kolon adı bilmeden, iş dilinde soru sorun.

#### Modeled
Metrikler, ilişkiler, birimler ve onaylanmış tanımlar tek bir semantik bağlamda tutulur.

#### Agentic
Doğrulanan analitiği tekrar kullanılabilir rapor, sözleşme ve zamanlama akışlarına dönüştürün.  
`Beta/Planned status required`

### How it works teaser
**Heading:** Sorudan rapora, görünür bir zincir.

1. Veri kaynağınızı ve iş modelinizi tanımlayın.
2. Doğal dilde sorun.
3. dima sorguyu planlasın ve doğrulasın.
4. Sonucu, SQL'i ve çözüm izini inceleyin.
5. Doğrulayın, yeniden kullanın veya zamanlayın.

### Use cases
**Operations:** Bugünkü üretim planına göre geride kalan makineler hangileri?  
**OEE:** En yüksek performans kaybı hangi vardiya ve makinede?  
**Finance:** Nakit dönüşüm süresi bu çeyrekte nasıl değişti?  
**Sales:** Brüt kârı düşen müşteri ve ürün grupları hangileri?  
**Inventory:** Kritik stok seviyesine yaklaşan malzemeler hangileri?  
**Executive:** Bu hafta hedeflerden en fazla sapan üç KPI nedir?

### Textile section
**Heading:** Boyahane verisini rapor beklemeden anlayın.

**Body:** Parti, reçete, makine, vardiya, fire, kalite, su, enerji, termin ve sevkiyat verilerini tek bir modellenmiş analitik bağlamda sorgulayın.

### Trust section
**Heading:** Cevabın arkasındaki mekanizmayı görün.

**Points:**
- Read-only query controls
- Dry-plan validation
- Modeled relationships
- Visible SQL and trace
- Permission-aware access
- Audit-ready workflow, if approved

### Final CTA
**Heading:** İlk gerçek iş sorunuzla başlayalım.

**Body:** Veri yapınızı ve öncelikli rapor ihtiyacınızı birlikte değerlendirelim.

**CTA:** Demo talep et

## Product page

### Hero
**Headline:** İş sorusundan doğrulanmış rapora, tek ürün akışında.

**Subhead:** dima, doğal dil arayüzünü semantic modeling, query validation ve açıklanabilir sonuç yüzeyleriyle birleştirir.

### Ask
İş dilinde sorun; tablo ve kolon adı ezberlemeyin.

### Model
Şemayı iş anlamıyla zenginleştirin: ölçüler, boyutlar, ilişkiler, birimler ve tanımlar.

### Validate
Sorgu, çalıştırılmadan önce izin ve planlama katmanlarından geçer.

### Explore
Sonucu tablo, grafik, KPI veya pivot olarak inceleyin.

### Verify
Doğru/yanlış feedback'i ve çözüm iziyle analitiği iyileştirin.

### Reuse
Onaylanan analitiği tekrar çalıştırılabilir hale getirin.  
`Status label required`

## How It Works page

### Hero
**Headline:** LLM'nin önerdiği sorguyu doğrudan çalıştırmıyoruz.

**Subhead:** Dima, doğal dil rahatlığını semantic context ve deterministic validation ile sınırlar.

### Raw LLM problem
Bir veritabanı şeması, “ciro”, “aktif müşteri” veya “fire” kavramlarının işletmenizde nasıl hesaplandığını tek başına söylemez.

### Modeled context
Dima, iş tanımlarını ve ilişkileri modele taşır.

### Guard
Yazma/silme işlemleri yerine izinli okuma sorguları.

### Dry-plan
Sorgunun semantic model üzerinden planlanabildiğini çalıştırmadan önce doğrular.

### Result
Kullanıcı yalnızca cevabı değil, SQL ve çözüm izini de görebilir.

## Solutions page

### Hero
**Headline:** Her ekip için aynı veri, aynı tanım, daha hızlı cevap.

### Executive
Hedef ve sapmaları tek görünümde anlayın.

### Operations
Üretim kaybını makine, vardiya ve süreç bazında sorgulayın.

### Finance
KPI formül ve bileşenlerini görünür tutun.

### Sales
Müşteri, ürün, fiyat ve kârlılık trendlerini karşılaştırın.

### Data/IT
Ad-hoc talepleri azaltırken query governance'ı koruyun.

## Textile/Dyehouse page

### Hero
**Headline:** Boyahanenizin üretim verisine iş dilinde erişin.

**Subhead:** Dima, parti ve reçeteden OEE, fire, enerji ve termin analizine kadar boyahane verisini modellenmiş bir bağlamda sorgulamanıza yardımcı olur.

### Sample questions
- Bu ay makine bazında OEE nedir?
- En yüksek fire hangi aşamada?
- Vardiya × haftanın günü verimliliği nasıl değişti?
- Reçete bazında kimyasal maliyet katkısı nedir?
- Termin riski taşıyan siparişler hangileri?
- Kilogram başına su ve enerji tüketimi nasıl değişiyor?

### Scope clarity
Dima bir MES/ERP yerine geçmez; mevcut operasyonel verinin üzerinde analitik ve raporlama katmanı olarak konumlanır.

## Security page

### Hero
**Headline:** Analitik hızlanırken veri erişim sınırları görünmez olmamalı.

### Read-only
Dima'nın query akışı izinli okuma sorgularına göre sınırlandırılır.

### Session
Kısa ömürlü access token ve HTTP-only refresh cookie mimarisi.

### Tenant
Her kullanıcı, tenant ve permission bağlamında çalışır.  
`Production scope approval required`

### Audit
Kritik sorgu ve yönetim eylemlerinin izlenebilirliği.  
`Public claim approval required`

## Integrations page

### Hero
**Headline:** Mevcut veri altyapınızın üzerinde modellenmiş analitik.

### Process
1. Bağlantı
2. Şema keşfi
3. Semantic model
4. Validation
5. Kullanıcı erişimi

### Support wording
“Desteklenen kaynaklar” listesi current-tested / engine-capable / planned olarak ayrılmalıdır.

## Contact page

### Headline
**Dima'yı kendi veriniz ve iş sorularınızla değerlendirin.**

### Supporting text
Veri kaynağınızı, sektörünüzü ve ilk çözmek istediğiniz rapor ihtiyacını paylaşın. Uygun demo senaryosunu birlikte hazırlayalım.

<!-- END 08_PAGE_COPY_BLUEPRINT.md -->


---

<!-- BEGIN 09_COMPONENT_INVENTORY.md -->

# 09 — Proposed Marketing Component Inventory

## Layout

- `MarketingLayout`
- `MarketingNavbar`
- `MobileMarketingMenu`
- `MarketingFooter`
- `SkipLink`
- `MarketingContainer`
- `MarketingSection`
- `SectionHeader`
- `SectionRule`

## Brand

- `DimaWordmark`
- `DimaMark`
- `DimaPillarMark`
- `EvidenceLabel`
- `CapabilityStatusBadge`

## Hero/proof

- `MarketingHero`
- `ProductProofFrame`
- `QueryComposerDemo`
- `ContextTagList`
- `ValidationTimeline`
- `ResultPreview`
- `SqlPreview`
- `TracePreview`
- `ProofAnnotation`

## Content

- `PillarGrid`
- `PillarCard`
- `WorkflowSteps`
- `UseCaseGrid`
- `UseCaseCard`
- `IndustryProof`
- `SecurityFeatureList`
- `IntegrationFlow`
- `ArchitectureDiagram`
- `FaqList`
- `FinalCta`

## Pages

- `ProductCapabilitySection`
- `HowItWorksStep`
- `SolutionOutcomeCard`
- `TextileQuestionCard`
- `SecurityBoundaryCard`
- `IntegrationStatusTable`
- `ContactForm`

## Reuse rules

- Page files compose sections; they do not contain large local UI implementations.
- Copy resides in typed content/i18n.
- Data arrays are not duplicated.
- A component is shared only when semantics match, not only visual similarity.
- Avoid a universal “Card” with dozens of variants.
- Server component by default.
- Client components isolated to menu/form/proof interaction.
- No component should require product QueryClient or stores.

## Proposed source structure

```text
src/components/marketing/
  brand/
    DimaWordmark.tsx
    EvidenceLabel.tsx
    CapabilityStatusBadge.tsx
  layout/
    MarketingNavbar.tsx
    MobileMarketingMenu.tsx
    MarketingFooter.tsx
    MarketingContainer.tsx
    MarketingSection.tsx
  proof/
    ProductProofFrame.tsx
    QueryComposerDemo.tsx
    ValidationTimeline.tsx
    ResultPreview.tsx
  sections/
    MarketingHero.tsx
    PillarGrid.tsx
    WorkflowSteps.tsx
    UseCaseGrid.tsx
    IndustryProof.tsx
    TrustArchitecture.tsx
    FaqList.tsx
    FinalCta.tsx
  forms/
    ContactForm.tsx
```

## Import boundary

Allowed:
- `components/ui`
- `lib/utils`
- `lib/motion`
- `content/marketing`
- i18n
- `lucide-react`
- `motion/react` only in client islands

Avoid:
- product `stores`
- `api-client`
- `@tanstack/react-query`
- product shell
- report/chart modules
- React Flow
- backend calls on homepage

## Component acceptance checklist

Each component:
- semantic element,
- accessible name,
- keyboard behavior if interactive,
- dark/light,
- mobile,
- no hardcoded duplicate copy,
- no layout shift,
- reduced motion,
- typed props,
- no `any`,
- no arbitrary z-index without scale,
- no magic brand colors outside tokens.

<!-- END 09_COMPONENT_INVENTORY.md -->


---

<!-- BEGIN AGENT_RUNBOOK.md -->

# Agent Runbook

Bu runbook, master prompt ve stage dosyalarıyla çalışan AI coding agent için ortak yürütme protokolüdür.

## 1. Oturum başında

Agent önce:

```bash
pwd
git status --short
git branch --show-current
git log -5 --oneline
cat package.json
```

Ardından:
- mevcut uncommitted değişiklikleri listeler,
- hiçbir değişikliği silmez veya overwrite etmez,
- hedef stage dışındaki dosyalara dokunmaz,
- ilgili repo docs/standards/CLAUDE/AGENTS dosyalarını okur.

## 2. Referans inceleme

Dima repo içi source of truth:
- `README.md`
- `src/app`
- `src/proxy.ts`
- `src/app/layout.tsx`
- `src/app/globals.css`
- `src/lib/providers.tsx`
- `src/lib/motion.ts`
- `messages/*.json`
- `e2e/`
- `saka-standards` ve proje yönergeleri

UpcyMan salt-okunur:
`/Users/enesteve/Desktop/Coding/Upcy/upcyman/upcyman`

Agent:
- yalnızca inceleyebilir,
- değiştiremez,
- import/symlink/dependency yapamaz,
- Dima'ya uygun yeniden uygulama yapar.

## 3. Stage başlamadan önce verilecek kısa rapor

```markdown
## Stage Preflight
- Current branch:
- Working tree:
- Relevant current files:
- Constraints discovered:
- Planned files to change:
- Risks:
```

Kullanıcı açıkça “devam et” beklenmesini istemediyse agent doğrudan implement edebilir; ancak bu preflight'i kendi çalışma logunda tutmalıdır.

## 4. Implementation rules

- Strict TypeScript, `any` yok.
- Server Component default.
- Client boundary minimum.
- Existing business logic untouched.
- No broad formatting churn.
- No dependency without explanation.
- No fake content.
- No secrets/PII.
- Accessible semantics.
- Responsive by construction.
- Tests after meaningful checkpoints.
- One stage, one scope.

## 5. Validation order

1. Targeted type/lint.
2. Full lint.
3. Production build.
4. Stage-specific test.
5. Auth/product smoke if routing/providers touched.
6. Visual responsive check.
7. Git diff review.

## 6. Hata yaklaşımı

Bir test mevcut baseline'da zaten fail ediyorsa:
- exact command,
- exact failure,
- neden stage kaynaklı olmadığını,
- stage'in yeni failure ekleyip eklemediğini
belgele.

Testi susturmak, skip etmek veya config'i gevşetmek çözüm değildir.

## 7. Stage sonu raporu

```markdown
# Stage Completion Report

## Summary
## Files changed
## Key implementation decisions
## Validation performed
- `command` — PASS/FAIL

## Accessibility checks
## Performance considerations
## Security/auth regression checks
## Known limitations
## Deferred work
## Recommended next stage
```

## 8. Git davranışı

- Kullanıcı istemedikçe commit yapma.
- Kullanıcı istemedikçe push yapma.
- Branch değiştirme veya reset yapma.
- `git clean`, `git reset --hard`, force push yok.
- UpcyMan repo'sunda hiçbir git komutu değişiklik üretmemeli.

<!-- END AGENT_RUNBOOK.md -->


---

<!-- BEGIN MASTER_PROMPT.md -->

# MASTER PROMPT — dima Marketing Website

You are the staff-level frontend engineer, product designer, technical writer, accessibility reviewer, and release owner responsible for building the public marketing website inside `UpcyTech/dima-frontend`.

## Mission

Build a production-quality, high-trust B2B SaaS marketing website for **dima** while preserving every existing product, authentication, API, tenant, reporting, and security behavior.

The marketing website must communicate Dima's real differentiator:

> Natural-language analytics grounded in a modeled semantic layer, with deterministic SQL guards and dry-plan validation. The LLM proposes; the engine validates.

You will work stage-by-stage. Do not automatically continue to another stage after completing the assigned stage.

## Working repository

Run from the root of `dima-frontend`.

Before any change:
```bash
pwd
git status --short
git branch --show-current
git log -5 --oneline
cat package.json
```

Read all applicable project instructions, including repository standards, `README.md`, `CLAUDE.md`/`AGENTS.md` if present, and relevant `saka-standards` documents.

Never delete, reset, overwrite, or stash existing user work.

## Source repositories to understand

Use the repository code/docs as source of truth:
- `UpcyTech/dima`
- `UpcyTech/dima-backend`
- `UpcyTech/dima-wrenai`
- `UpcyTech/dima-frontend-demo`
- `UpcyTech/dima-admin-frontend`
- `UpcyTech/dima-changelog`
- `UpcyTech/dima-frontend`

Do not merge these repositories or create cross-repo runtime coupling.

## Read-only design reference

You may inspect this local repository as a visual/composition reference:

`/Users/enesteve/Desktop/Coding/Upcy/upcyman/upcyman`

Strict rules:
- READ ONLY.
- Do not edit, format, install, commit, or generate files inside it.
- Do not create symlinks.
- Do not import components across repositories.
- Do not add it as a workspace or file dependency.
- Do not copy its brand, green palette, marketing claims, logos, customer proof, or product-specific copy.
- Reimplement useful composition ideas in Dima using Dima's tokens, semantics, stack, and accessibility requirements.
- For third-party UI primitives, use the official source and verify the license; do not blindly copy a local component.

High-value inspiration:
- marketing page composition and section rhythm,
- navbar/footer behavior,
- editorial typography,
- bento layout,
- product-derived feature mockups,
- responsive spacing,
- i18n organization,
- restrained motion.

Avoid:
- heavy particle canvases,
- rainbow buttons,
- effect stacking,
- fake statistics,
- excessive animated text,
- WebGL/Three for marketing decoration.

## Non-negotiable product boundaries

Do not rewrite or weaken:
- `src/lib/api-client.ts` and same-origin API proxy behavior,
- access-token-in-memory / HTTP-only-refresh-cookie flow,
- 401 refresh-and-retry,
- expired-cookie login handling,
- permission-based UI behavior,
- tenant/session semantics,
- conversation state and cross-user reset protections,
- ask/cube/verify/contracts/schedules/notifications logic,
- report/chart/table/KPI/pivot business logic,
- backend origin secrecy,
- security headers,
- product E2E behavior except required route updates.

Do not expose the local-only admin UI or admin endpoints in public navigation.

## Target route architecture

The intended architecture is:

- `/` and other marketing pages: public
- `/app/**`: authenticated product
- `/login`, `/register`, `/forgot-password`: auth
- route groups separate marketing/product/auth layouts without changing URLs

Expected direction:
```text
src/app/
  layout.tsx
  (marketing)/
  (product)/app/
  (auth)/
```

The root layout must be scroll-neutral. Product full-height/overflow behavior belongs in the product layout.

The existing product root page must have one canonical home at `/app`; do not duplicate product state across `/` and `/app`.

Proxy/session redirects must be migrated safely:
- logged out `/app` → `/login?next=/app`
- logged in auth page → `/app`
- public marketing remains public
- expired-cookie behavior remains intact
- unknown public URL should render a real 404, not force login

## Architecture principles

- Next.js App Router best practices.
- Server Components by default.
- Minimal client islands.
- Marketing must not import product QueryClient, Zustand stores, React Flow, chart runtime, or API client unless explicitly required and justified.
- Split lightweight global providers from product runtime providers if necessary.
- Static generation for public pages where possible.
- Existing Tailwind 4 + OKLCH Dima tokens are the source of truth.
- Playfair Display is marketing-only; Plus Jakarta Sans is primary UI/body; JetBrains Mono is technical evidence.
- Lucide is the icon system.
- Motion uses transform/opacity, fast purposeful easing, and respects reduced motion.
- No new dependency unless existing tools cannot solve the requirement; document every addition.

## Brand and content principles

Product name is lowercase: **dima**.

Official pillars:
- Deterministic
- Intelligent
- Modeled
- Agentic

Use the pillars as mechanisms, not decorative slogans.

Preferred positioning:
> İşletme verinizle konuşun. Cevabın nasıl üretildiğini görün.

Preferred trust line:
> LLM önerir; modellenmiş bağlam ve doğrulama motoru karar verir.

Never publish:
- fake logos, testimonials, customer/user counts, ROI, uptime, or benchmarks,
- unverified prices,
- unverified certifications,
- “100% accurate”, “hallucination-free”, “zero risk”,
- “raw data never leaves the LAN” until the thin-agent/on-prem capability is truly available,
- engine connector count as Dima production support without verification,
- planned capabilities without `Beta` or `Planned` status.

Use only sanitized demo data and assets.

## Initial page scope

Primary:
- `/`
- `/product`
- `/how-it-works`
- `/solutions`
- `/solutions/textile-dyehouse`
- `/security`
- `/integrations`
- `/about`
- `/contact`
- `/privacy`
- `/terms`

Conditional:
- `/changelog` only with public-safe curated content.
- No `/pricing` until pricing is approved.
- No blog until ownership and publishing workflow exist.

## Homepage narrative

1. Hero and CTAs.
2. Immediate real product proof.
3. D-I-M-A pillars.
4. How it works / trust pipeline.
5. Use cases.
6. Textile/dyehouse vertical proof.
7. Security/governance.
8. Integrations/deployment.
9. FAQ.
10. Final CTA and footer.

The product proof should be a deterministic, local, sanitized simulation of:
question → modeled context → guard/dry-plan → result/SQL/trace.

Do not call the real backend anonymously from the public page.

## Accessibility standard

Target WCAG 2.2 AA:
- semantic landmarks,
- one H1,
- logical headings,
- skip link,
- full keyboard navigation,
- visible focus,
- focus not obscured,
- minimum 24×24 targets and practical 44×44 primary targets,
- adequate contrast,
- reduced motion,
- reflow at 320px,
- accessible forms/errors/status,
- no hover-only critical content,
- no motion-only meaning.

## Performance standard

Marketing route must avoid shipping product-heavy code.

Targets:
- LCP ≤ 2.5s
- INP ≤ 200ms
- CLS ≤ 0.1
- Lighthouse mobile performance ≥ 90 where environment permits
- Accessibility/Best Practices/SEO ≥ 95 where environment permits

Do not game scores by removing useful semantics or tests.

## SEO standard

Implement:
- metadata base via site URL env,
- title template,
- unique page metadata,
- canonical,
- Open Graph/Twitter,
- sitemap,
- robots,
- noindex for `/app` and auth,
- Organization JSON-LD,
- factual SoftwareApplication JSON-LD,
- real 404.

Current locale is cookie-based without URL prefixes. Do not generate misleading hreflang. A route-based locale migration is separate scope unless the assigned stage explicitly requires it.

## Testing standard

At every stage, inspect actual scripts before running commands.

Minimum:
```bash
pnpm lint
pnpm build
```

Routing/provider/product stages must also run the existing E2E and product smoke checks.

Do not disable tests, loosen TypeScript, add `any`, or suppress errors to pass.

## Stage execution protocol

For the assigned stage:

1. Read this master prompt.
2. Read the complete stage file.
3. Audit the current repo; do not assume paths are unchanged.
4. State the stage plan in your work log.
5. Implement only the stage scope.
6. Preserve user changes.
7. Run required validation.
8. Review the final diff.
9. Produce the completion report format from `AGENT_RUNBOOK.md`.
10. Stop. Do not start the next stage.

## Completion report

Include:
- summary,
- exact files changed,
- decisions,
- commands and PASS/FAIL,
- accessibility checks,
- performance impact,
- auth/security regression checks,
- known limitations,
- deferred work,
- recommended next stage.

Do not commit or push unless the user explicitly asks.

<!-- END MASTER_PROMPT.md -->


---

<!-- BEGIN stages/STAGE_00_PREFLIGHT_AND_REPO_AUDIT.md -->

# STAGE 00 — Preflight, Baseline and Repository Audit

## Objective

Create a verified baseline before any marketing implementation. This stage produces documentation and, only if necessary, non-behavioral test helpers. It must not redesign pages.

## Required reading

- `MASTER_PROMPT.md`
- `AGENT_RUNBOOK.md`
- repo `README.md`
- `package.json`
- all repo instruction files
- `src/app/**`
- `src/proxy.ts`
- `src/lib/providers.tsx`
- `src/lib/api-client.ts`
- auth pages
- `messages/*.json`
- `e2e/**`
- `next.config.ts`
- `vercel.json`

Read-only reference:
`/Users/enesteve/Desktop/Coding/Upcy/upcyman/upcyman`

## Tasks

1. Record:
   - branch,
   - HEAD SHA,
   - uncommitted files,
   - Node/pnpm versions,
   - available scripts,
   - current route tree,
   - current provider tree,
   - current proxy matcher,
   - current auth redirect targets,
   - current metadata/robots/sitemap state.

2. Build a route/auth dependency map:
   - every exact `/` redirect or link,
   - every `router.push("/")`, `replace("/")`, `redirect("/")`,
   - every test assuming `/`,
   - all page access decisions.

3. Build a client-bundle risk map:
   - which root providers are client-side,
   - which heavy product dependencies could leak into marketing,
   - which page/component is `"use client"`.

4. Run baseline:
   ```bash
   pnpm lint
   pnpm build
   pnpm e2e
   ```
   Use actual scripts only.

5. Create/update a repo-local planning document such as:
   `docs/marketing/00-baseline-audit.md`
   Include exact findings; do not duplicate the entire external pack.

6. Identify files that are likely to be touched in Stage 01 and mark risk level.

## Out of scope

- No route move.
- No marketing components.
- No visual design.
- No dependency changes.
- No auth logic rewrite.
- No broad formatting.

## Acceptance criteria

- Baseline commands and results documented.
- All root-route assumptions identified.
- All protected/public routes identified.
- Product business logic boundaries listed.
- UpcyMan reviewed read-only; no modifications.
- Working tree preservation confirmed.

## Stage delivery report

At the end, return:

```markdown
# Stage Completion Report
## Summary
## Files changed
## Decisions
## Validation
## Accessibility
## Performance
## Security/auth regression
## Known limitations
## Deferred
## Next recommended stage
```

Do not commit or push unless explicitly requested. Stop after this stage.

<!-- END stages/STAGE_00_PREFLIGHT_AND_REPO_AUDIT.md -->


---

<!-- BEGIN stages/STAGE_01_ROUTE_ARCHITECTURE_AND_AUTH_BOUNDARIES.md -->

# STAGE 01 — Route Architecture and Authentication Boundaries

## Objective

Make `/` safely available for public marketing and move the single canonical authenticated product entrypoint to `/app`, without changing product behavior.

## Preconditions

- Stage 00 complete.
- Baseline failures, if any, understood.
- No unresolved user changes in route/auth files.

## Target

```text
app/
  layout.tsx
  (marketing)/page.tsx            # temporary minimal public shell
  (product)/app/layout.tsx
  (product)/app/page.tsx          # current product
  (auth)/...
```

The temporary `/` page can be minimal and factual. Full design is Stage 04.

## Tasks

1. Move current product root page to `/app`.
   - Do not duplicate the product component.
   - Preserve imports, state, mutations, report behavior and shell.
   - A shared internal component is acceptable if needed, but there must be one canonical route.

2. Split layout responsibilities:
   - root layout scroll-neutral,
   - product layout full-height/overflow-hidden,
   - marketing layout scrollable.

3. Split providers if root currently causes product runtime on public pages.
   - Keep locale/theme/reduced-motion as needed globally.
   - Keep QueryClient/AuthBootstrap/product runtime in protected product/auth boundary.
   - Do not create theme hydration regressions.

4. Update proxy:
   - protect `/app/:path*`,
   - preserve expired-cookie logic,
   - logged-in auth route → `/app`,
   - no session `/app` → login with `next`,
   - public marketing not gated,
   - unknown route can reach 404.

5. Audit and update exact root redirect/link assumptions.
   - Login success.
   - Logout.
   - Session restore.
   - Auth page redirect.
   - logo/home links.
   - test URLs.
   - docs comments where directly relevant.

6. Add route metadata:
   - `/app` noindex.
   - auth noindex.
   - temporary marketing metadata.

7. Update E2E:
   - product browser flow uses `/app`,
   - public `/` smoke,
   - auth redirect matrix.

8. Preserve API proxy and backend origin secrecy.

## Out of scope

- Full marketing page.
- New marketing design system.
- New analytics.
- Contact form.
- New dependencies.
- Product UI redesign.

## Required validation

```bash
pnpm lint
pnpm build
pnpm e2e
```

Manual/automated matrix:
- logged out `/`
- logged out `/app`
- logged in `/login`
- expired `/login?expired=1`
- unknown route
- product query flow at `/app`

## Acceptance criteria

- `/` public.
- `/app` protected.
- Existing product behavior unchanged.
- Root marketing scroll works.
- Product remains `h-dvh`/overflow-controlled.
- No anonymous backend query.
- No cross-user conversation regression.
- No duplicated product state entrypoint.

## Stage delivery report

At the end, return:

```markdown
# Stage Completion Report
## Summary
## Files changed
## Decisions
## Validation
## Accessibility
## Performance
## Security/auth regression
## Known limitations
## Deferred
## Next recommended stage
```

Do not commit or push unless explicitly requested. Stop after this stage.

<!-- END stages/STAGE_01_ROUTE_ARCHITECTURE_AND_AUTH_BOUNDARIES.md -->


---

<!-- BEGIN stages/STAGE_02_MARKETING_DESIGN_SYSTEM.md -->

# STAGE 02 — Marketing Design System and Primitives

## Objective

Create the Dima-specific marketing visual system using existing Tailwind 4/OKLCH tokens and minimal reusable primitives. Do not build full pages yet.

## Design direction

Editorial Industrial Intelligence:
- warm editorial surfaces,
- near-black inverse sections,
- indigo-violet brand accent,
- thin rules,
- technical mono evidence labels,
- product proof over decoration,
- restrained motion.

## Tasks

1. Audit existing tokens and component primitives.
2. Add only missing semantic marketing tokens.
3. Define typography utilities/components:
   - display,
   - section heading,
   - body,
   - eyebrow,
   - mono evidence.
4. Build primitives:
   - `MarketingContainer`
   - `MarketingSection`
   - `SectionHeader`
   - `EvidenceLabel`
   - `MarketingButton` variants or extend existing Button safely
   - `ProofFrame`
   - `PillarCard`
   - `StatusBadge`
   - `SectionRule`
5. Define motion wrappers using existing presets:
   - reveal,
   - stagger,
   - reduced-motion final state.
6. Build a development-only visual showcase route or Storybook story only if the repo already supports that pattern. Do not expose an unfinished public route.
7. Add design documentation:
   `docs/marketing/01-design-system.md`
8. Inspect UpcyMan's design system and marketing primitives read-only; reimplement, do not copy wholesale.
9. Verify both light and dark themes.
10. Verify 320px–1920px behavior.

## Dependency policy

No new dependency by default. A new primitive package requires:
- feature gap,
- bundle impact,
- license,
- exact components imported,
- reason existing Radix/custom components are insufficient.

## Accessibility

- focus ring visible,
- target sizes,
- semantic heading API,
- no div-as-button,
- contrast,
- reduced motion,
- decorative SVG semantics.

## Out of scope

- Navbar/footer.
- Homepage composition.
- Content claims.
- Product route changes.
- New chart libraries.

## Required validation

```bash
pnpm lint
pnpm build
```

Also inspect generated CSS/client boundaries.

## Acceptance criteria

- Existing product tokens not broken.
- Marketing primitives are original and Dima-branded.
- No UpcyMan runtime coupling.
- No effect soup.
- No unnecessary client boundary.
- Dark/light accessible.

## Stage delivery report

At the end, return:

```markdown
# Stage Completion Report
## Summary
## Files changed
## Decisions
## Validation
## Accessibility
## Performance
## Security/auth regression
## Known limitations
## Deferred
## Next recommended stage
```

Do not commit or push unless explicitly requested. Stop after this stage.

<!-- END stages/STAGE_02_MARKETING_DESIGN_SYSTEM.md -->


---

<!-- BEGIN stages/STAGE_03_SHARED_MARKETING_SHELL.md -->

# STAGE 03 — Shared Marketing Shell

## Objective

Build the reusable public navigation, mobile menu, footer, skip link and route-level shell.

## Tasks

1. Create typed navigation source.
2. Build desktop navbar:
   - wordmark,
   - Product,
   - How it works,
   - Solutions,
   - Security,
   - Integrations,
   - language,
   - Login,
   - Demo CTA.
3. Build accessible mobile menu:
   - semantic trigger,
   - focus management,
   - Escape,
   - close on navigation,
   - scroll lock,
   - 44px primary targets.
4. Build footer:
   - product links,
   - solutions,
   - company,
   - legal,
   - login/demo,
   - factual copyright/company.
5. Add skip-to-content.
6. Add active/hover/focus states.
7. Ensure sticky header never obscures focused content.
8. Ensure marketing layout has one `<main id="main-content">`.
9. Add minimal factual 404 using the shell.
10. Create typed nav/footer translation namespaces in TR and EN.
11. Do not link admin.
12. Do not create empty routes in navigation.

## Design requirements

- Header may be subtly floating or bordered, but not visually detached from Dima tokens.
- No glass with unreadable contrast.
- Header layout stable on scroll.
- Logo click → `/`.
- Login → `/login`.
- Demo → `/contact`.
- Product app link is “Giriş yap”, not an anonymous `/app` CTA.

## Out of scope

- Full homepage.
- Contact form backend.
- Mega-menu unless content truly requires it.
- Announcement banner without a real announcement.

## Validation

```bash
pnpm lint
pnpm build
```

Manual:
- keyboard tab order,
- screen-reader names,
- mobile open/close,
- no horizontal scroll,
- dark/light,
- TR/EN.

## Acceptance criteria

- Shell used by all marketing pages.
- No nav dead link.
- Mobile menu accessible.
- Product/auth layout unaffected.
- Focus never hidden.

## Stage delivery report

At the end, return:

```markdown
# Stage Completion Report
## Summary
## Files changed
## Decisions
## Validation
## Accessibility
## Performance
## Security/auth regression
## Known limitations
## Deferred
## Next recommended stage
```

Do not commit or push unless explicitly requested. Stop after this stage.

<!-- END stages/STAGE_03_SHARED_MARKETING_SHELL.md -->


---

<!-- BEGIN stages/STAGE_04_HOMEPAGE.md -->

# STAGE 04 — Homepage

## Objective

Build the complete public homepage at `/` with an original Dima-specific narrative and real product proof.

## Required section order

1. Hero
2. Product proof
3. D-I-M-A pillars
4. How it works
5. Use cases
6. Textile/dyehouse proof
7. Trust/security
8. Integrations/deployment
9. FAQ
10. Final CTA

## Hero content

Preferred:
- Eyebrow: `Güvenilir konuşmalı analitik`
- H1: `İşletme verinizle konuşun. Cevabın nasıl üretildiğini görün.`
- Subhead: modeled context + validation + report
- Primary: `Demo talep et` → `/contact`
- Secondary: `Giriş yap` → `/login`

Copy must live in i18n content, not hardcoded across components.

## Product proof

Build a deterministic public-safe visual:
- sample boyahane question,
- context tags,
- parse/catalog/plan/verify/run steps,
- `DRY-PLAN VERIFIED`,
- chart/table/KPI-like result,
- SQL or trace preview.

Rules:
- no real backend call,
- no auth bypass,
- no real customer data,
- no heavy chart runtime if CSS/SVG/HTML can render it,
- reduced-motion renders final stable state,
- mobile-specific composition.

## Pillars

D/I/M/A each explain a real mechanism.
Status-label Agentic/Beta/Planned if needed.

## Use cases

Each use-case card includes a realistic sample question, not only a noun.

## Textile proof

Link to `/solutions/textile-dyehouse`.
Use only sanitized demo terminology.

## Trust

Explain read-only guard, dry-plan, modeled context, SQL visibility, permissions/audit only to verified extent.

## FAQ

Use visible accessible content. Do not add FAQ schema until Stage 09 and only if policy/visibility match.

## Visual constraints

- no particles/WebGL,
- no rainbow CTA,
- no fake logo cloud,
- no fake stats,
- no fake testimonials,
- one primary visual motif,
- no autoplay carousel,
- avoid excessive client JS.

## Validation

```bash
pnpm lint
pnpm build
```

Checks:
- 320px,
- 375px,
- 768px,
- 1440px,
- light/dark,
- reduced motion,
- keyboard,
- LCP asset,
- no product dependency imports.

## Acceptance criteria

- User understands product, mechanism and target use cases within first screen + first proof.
- Every claim traceable to approved claim matrix.
- CTAs work.
- No public API call.
- Original Dima visual identity.

## Stage delivery report

At the end, return:

```markdown
# Stage Completion Report
## Summary
## Files changed
## Decisions
## Validation
## Accessibility
## Performance
## Security/auth regression
## Known limitations
## Deferred
## Next recommended stage
```

Do not commit or push unless explicitly requested. Stop after this stage.

<!-- END stages/STAGE_04_HOMEPAGE.md -->


---

<!-- BEGIN stages/STAGE_05_PRODUCT_AND_HOW_IT_WORKS.md -->

# STAGE 05 — Product and How It Works Pages

## Objective

Build `/product` and `/how-it-works` as complementary deep pages: one product-led, one mechanism-led.

## `/product` structure

1. Product hero
2. Ask
3. Modeled context
4. Validate
5. Explore (table/chart/KPI/pivot)
6. Verify/trace
7. Reuse/schedule, status-labeled
8. Govern
9. CTA

Every section should use real Dima surfaces or sanitized coded mockups.

## `/how-it-works` structure

1. Why raw text-to-SQL is insufficient
2. Connection and schema/model onboarding
3. Business semantics / MDL
4. NL interpretation
5. SELECT guard
6. Dry-plan
7. Execution
8. Result/provenance
9. Verify/reuse
10. Security boundary
11. Planned architecture, clearly labeled

## Technical accuracy rules

- Do not say dry-plan proves business correctness; it validates planning/semantic executability.
- Do not say SELECT-only eliminates all risk.
- Do not imply LLM directly executes arbitrary SQL.
- Distinguish model definitions from raw schema.
- Distinguish engine connector capability from Dima production-tested connector support.
- On-prem/thin agent must be status-labeled.

## Components

Prefer shared:
- workflow timeline,
- architecture diagram,
- product surface frame,
- capability status,
- code/SQL block,
- source/context callout.

Architecture diagram must have text alternative.

## SEO

Unique copy and metadata; do not duplicate homepage paragraphs.

## Validation

```bash
pnpm lint
pnpm build
```

Plus links, heading hierarchy, diagram accessibility, mobile reflow.

## Acceptance criteria

- Product page answers “What can I do?”
- How It Works answers “Why should I trust it?”
- Claims are nuanced and accurate.
- No heavy duplicated runtime.

## Stage delivery report

At the end, return:

```markdown
# Stage Completion Report
## Summary
## Files changed
## Decisions
## Validation
## Accessibility
## Performance
## Security/auth regression
## Known limitations
## Deferred
## Next recommended stage
```

Do not commit or push unless explicitly requested. Stop after this stage.

<!-- END stages/STAGE_05_PRODUCT_AND_HOW_IT_WORKS.md -->


---

<!-- BEGIN stages/STAGE_06_SOLUTIONS_AND_TEXTILE_VERTICAL.md -->

# STAGE 06 — Solutions and Textile/Dyehouse Vertical

## Objective

Build `/solutions` and `/solutions/textile-dyehouse` with concrete jobs-to-be-done and sector-specific product proof.

## `/solutions`

Group by outcome, not org chart only:
- Executive visibility
- Production/OEE
- Sales/customer
- Finance/KPI
- Inventory/supply
- Data/IT governance

Each card:
- problem,
- sample question,
- Dima mechanism,
- expected output,
- link/deep CTA.

## `/solutions/textile-dyehouse`

### Required narrative

1. Vertical hero
2. Data landscape
3. Real questions
4. Production/OEE
5. Fire/quality
6. Recipe/chemical
7. Water/energy
8. Orders/deadlines/shipments
9. Integration/onboarding
10. Demo CTA

### Demo model vocabulary

Use only sanitized/public demo terms:
- partiler
- vardiya kayıtları
- siparişler
- sevkiyatlar
- reçete/kimyasal
- makineler
- müşteriler
- personel
- fire
- OEE
- renk sapması
- su/enerji
- termin

### Proof

- data relationship mini-map,
- sample query cards,
- one realistic result visual,
- no real customer data,
- no claim of direct Egemen integration unless actually implemented and approved.

### Industry tone

Avoid pretending Dima is a full MES/ERP. Clearly position it as an analytics/context/reporting layer over operational data.

## SEO/content

- Turkish industrial terminology.
- Unique metadata.
- No keyword stuffing.
- Add internal links to Product, How It Works, Security and Contact.

## Validation

```bash
pnpm lint
pnpm build
```

Check:
- diagram reflow,
- screen-reader alternative,
- claim status,
- no customer trademark misuse,
- mobile.

## Acceptance criteria

- A dyehouse operator can recognize their workflow.
- Dima scope is clear.
- Vertical page contains real proof, not generic factory imagery.

## Stage delivery report

At the end, return:

```markdown
# Stage Completion Report
## Summary
## Files changed
## Decisions
## Validation
## Accessibility
## Performance
## Security/auth regression
## Known limitations
## Deferred
## Next recommended stage
```

Do not commit or push unless explicitly requested. Stop after this stage.

<!-- END stages/STAGE_06_SOLUTIONS_AND_TEXTILE_VERTICAL.md -->


---

<!-- BEGIN stages/STAGE_07_SECURITY_INTEGRATIONS_AND_TRUST.md -->

# STAGE 07 — Security, Integrations and Trust

## Objective

Build `/security` and `/integrations` with precise, non-inflated technical communication.

## `/security`

Recommended sections:
1. Security philosophy
2. Read-only query controls
3. Session security
4. Tenant and permission boundary
5. Auditability
6. Data flow
7. Deployment status/options
8. Responsible security contact
9. FAQ/CTA

## Security claim review

Before publishing each claim, find exact code/doc evidence.

Do not publish:
- SOC 2/ISO badges,
- “fully KVKK/GDPR compliant,”
- “military-grade,”
- “zero trust” unless architecture formally supports it,
- “data never leaves premises” before thin-agent deployment is ready.

Use language like:
- “designed to”
- “the current architecture”
- “available in the current deployment”
- “planned”
where appropriate.

## `/integrations`

Distinguish:
1. Current tested Dima connectors.
2. Engine-level capabilities.
3. Planned/partner integrations.
4. Generic onboarding process.

Show:
- source connection,
- schema discovery,
- semantic modeling,
- validation,
- tenant scoping.

Do not display vendor logos without right/need. Plain text list is acceptable.

## Architecture visual

Create an accessible data-flow diagram:
User → Dima UI → Dima API → semantic model/Wren → guarded query → customer DB.

If showing cloud/on-prem modes, status-label each.

## Contact CTA

Security/integration inquiry route to `/contact` with safe query parameter only if form supports it.

## Validation

```bash
pnpm lint
pnpm build
```

Plus:
- security copy technical review,
- no secret/internal hostname,
- no admin link,
- no customer credentials,
- external links safe,
- diagram alt.

## Acceptance criteria

- Technical reader can understand trust boundaries.
- No absolute or unverified security claim.
- Connector support accurately segmented.

## Stage delivery report

At the end, return:

```markdown
# Stage Completion Report
## Summary
## Files changed
## Decisions
## Validation
## Accessibility
## Performance
## Security/auth regression
## Known limitations
## Deferred
## Next recommended stage
```

Do not commit or push unless explicitly requested. Stop after this stage.

<!-- END stages/STAGE_07_SECURITY_INTEGRATIONS_AND_TRUST.md -->


---

<!-- BEGIN stages/STAGE_08_COMPANY_RESOURCES_LEGAL_CONTACT.md -->

# STAGE 08 — Company, Resources, Legal and Contact

## Objective

Complete the supporting marketing surface: `/about`, optional `/changelog`, `/contact`, `/privacy`, `/terms`.

## `/about`

Include only verified facts:
- Dima product purpose.
- UpcyTech relationship.
- Product principles.
- Why modeled/deterministic analytics.
- Team/company details only if approved.
- No fabricated office, customer or investor claims.

## `/changelog` — conditional

Build only if there is a safe publishing source.

Private `dima-changelog` must not be streamed directly to public users.

Public entry should:
- be curated,
- omit SHAs/internal hosts/credentials/operational details,
- use user-facing Added/Changed/Fixed language,
- have date and version,
- be static at build or imported from a public-safe content file.

If safe source does not exist, defer page and remove nav link.

## `/contact`

Implement:
- typed validation,
- accessible labels/errors,
- success/error/retry,
- server-side processing,
- anti-abuse,
- privacy acknowledgement,
- no PII analytics.

Do not fake successful submission if endpoint is missing. Use an explicit development-safe state and document backend requirement.

## `/privacy` and `/terms`

Do not invent legal commitments. Use:
- approved legal copy,
- clearly marked review status,
- effective date,
- contact channel.

If legal text is unavailable, create structurally complete placeholders marked `LEGAL REVIEW REQUIRED` in non-production content and block production release.

## Metadata

Unique titles and descriptions.

## Validation

```bash
pnpm lint
pnpm build
```

Contact:
- keyboard,
- server validation,
- rate limit behavior,
- error messages,
- network failure,
- success state.

## Acceptance criteria

- No empty/dead page.
- Contact submission is honest.
- Legal review status explicit.
- Private changelog data not exposed.

## Stage delivery report

At the end, return:

```markdown
# Stage Completion Report
## Summary
## Files changed
## Decisions
## Validation
## Accessibility
## Performance
## Security/auth regression
## Known limitations
## Deferred
## Next recommended stage
```

Do not commit or push unless explicitly requested. Stop after this stage.

<!-- END stages/STAGE_08_COMPANY_RESOURCES_LEGAL_CONTACT.md -->


---

<!-- BEGIN stages/STAGE_09_SEO_ANALYTICS_PERFORMANCE_ACCESSIBILITY.md -->

# STAGE 09 — SEO, Analytics, Performance and Accessibility Hardening

## Objective

Apply cross-cutting production hardening after all main pages exist.

## SEO tasks

1. Site URL env and metadataBase.
2. Root title template.
3. Unique metadata all public routes.
4. Canonicals.
5. Open Graph/Twitter.
6. 1200×630 Dima OG.
7. `sitemap.ts`.
8. `robots.ts`.
9. `/app`, auth, API noindex/disallow.
10. Organization JSON-LD.
11. Factual SoftwareApplication JSON-LD.
12. Real 404.
13. Internal link audit.
14. No hreflang for cookie-only locale.
15. Preview deployment noindex policy.

## Analytics tasks

1. Confirm provider and consent requirements.
2. Implement provider abstraction.
3. Add approved events.
4. Exclude PII/query/SQL/tenant data.
5. Respect Do Not Track/consent policy as required.
6. Verify events in preview.
7. Document event dictionary.

Do not install analytics provider without approval if none selected.

## Performance tasks

1. Run bundle/build analysis using available tooling.
2. Verify marketing chunks do not include:
   - React Query,
   - Zustand product stores,
   - React Flow,
   - chart libs,
   - product API client.
3. Optimize LCP.
4. Image sizes/formats.
5. Font loading.
6. Dynamic import only where useful.
7. CLS audit.
8. Remove unused effects/dependencies.
9. Test slow network/CPU if tooling permits.

## Accessibility tasks

WCAG 2.2 AA review:
- landmarks,
- headings,
- labels,
- keyboard,
- focus visible/not obscured,
- target size,
- contrast,
- reduced motion,
- zoom/reflow,
- form errors,
- mobile menu,
- accordion,
- diagrams,
- skip link,
- status announcement.

Use axe/Playwright if installed; do not add a large framework solely for one scan without justification.

## Required validation

```bash
pnpm lint
pnpm build
pnpm e2e
```

Plus Lighthouse/axe if available.

## Acceptance criteria

- Indexing surfaces correct.
- No duplicate metadata.
- No misleading structured data.
- No PII analytics.
- Marketing bundle separated from product-heavy code.
- No critical accessibility issue.
- Performance targets met or documented with exact blockers.

## Stage delivery report

At the end, return:

```markdown
# Stage Completion Report
## Summary
## Files changed
## Decisions
## Validation
## Accessibility
## Performance
## Security/auth regression
## Known limitations
## Deferred
## Next recommended stage
```

Do not commit or push unless explicitly requested. Stop after this stage.

<!-- END stages/STAGE_09_SEO_ANALYTICS_PERFORMANCE_ACCESSIBILITY.md -->


---

<!-- BEGIN stages/STAGE_10_TESTING_RELEASE_AND_HANDOFF.md -->

# STAGE 10 — Testing, Release and Handoff

## Objective

Complete regression, release readiness, documentation and maintainable handoff.

## Automated tests

Expand/update tests for:

### Public routes
- `/`
- `/product`
- `/how-it-works`
- `/solutions`
- `/solutions/textile-dyehouse`
- `/security`
- `/integrations`
- `/about`
- `/contact`
- legal pages

### Auth
- logged out `/app`
- logged in auth redirect
- expired cookie
- logout/login conversation reset
- unknown route 404

### Product
- existing ask flow at `/app`
- schema/report UI
- no API proxy regression

### UI
- nav/mobile menu
- CTA links
- contact validation
- reduced motion where testable
- metadata/robots/sitemap basic assertions

## Visual QA

Capture/review:
- mobile,
- tablet,
- desktop,
- light/dark,
- TR/EN,
- long translations,
- 200% zoom,
- keyboard.

Do not approve screenshots containing real credentials/data.

## Content/claim review

Create final checklist:
- available/beta/planned,
- security claims,
- connector claims,
- customer proof permissions,
- legal approval,
- pricing omission/approval,
- contact owner.

## Documentation

Update:
- repo README route map,
- marketing architecture,
- content editing guide,
- asset guide,
- claim status guide,
- analytics events,
- deployment env,
- run/test commands.

## Release

1. Preview deployment.
2. Smoke.
3. Production env review.
4. Domain/canonical.
5. robots/sitemap.
6. form destination.
7. rollback plan.
8. release note.
9. monitoring owner.

## Required validation

```bash
pnpm lint
pnpm build
pnpm e2e
```

Run every available relevant test. Review final diff for:
- debug logs,
- TODO copy,
- dead links,
- placeholders,
- unexpected dependencies,
- broad formatting churn.

## Acceptance criteria

- Full route/auth/product regression passes.
- Production release checklist signed.
- Documentation sufficient for another developer.
- Known limitations explicit.
- Rollback path identified.

## Stage delivery report

At the end, return:

```markdown
# Stage Completion Report
## Summary
## Files changed
## Decisions
## Validation
## Accessibility
## Performance
## Security/auth regression
## Known limitations
## Deferred
## Next recommended stage
```

Do not commit or push unless explicitly requested. Stop after this stage.

<!-- END stages/STAGE_10_TESTING_RELEASE_AND_HANDOFF.md -->
