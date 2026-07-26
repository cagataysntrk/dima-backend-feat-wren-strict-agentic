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
