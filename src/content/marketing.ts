export type MarketingLocale = "tr" | "en";
export type CapabilityStatus = "available" | "beta" | "planned";

export type ContentSection = {
  id: string;
  title: string;
  body: string;
  points?: string[];
  status?: CapabilityStatus;
};

export type PageContent = {
  eyebrow: string;
  title: string;
  description: string;
  sections: ContentSection[];
  cta: string;
};

export type MarketingContent = {
  locale: MarketingLocale;
  nav: {
    product: string;
    how: string;
    solutions: string;
    security: string;
    integrations: string;
    login: string;
    demo: string;
    menu: string;
  };
  footer: {
    statement: string;
    product: string;
    company: string;
    legal: string;
    privacy: string;
    terms: string;
    about: string;
    contact: string;
    rights: string;
  };
  common: {
    learnMore: string;
    available: string;
    beta: string;
    planned: string;
    finalTitle: string;
    finalBody: string;
    demo: string;
    login: string;
  };
  home: {
    eyebrow: string;
    title: string;
    description: string;
    process: string[];
    proofTitle: string;
    proofBody: string;
    pillarsTitle: string;
    pillarsBody: string;
    workflowTitle: string;
    workflow: Array<{ title: string; body: string }>;
    useCasesTitle: string;
    useCases: Array<{ title: string; question: string }>;
    operationsTitle: string;
    operationsBody: string;
    trustTitle: string;
    trustBody: string;
    integrationTitle: string;
    integrationBody: string;
    faqTitle: string;
    faq: Array<{ question: string; answer: string }>;
  };
  pages: Record<string, PageContent>;
  legal: {
    lastUpdated: string;
    notice: string;
    privacy: PageContent;
    terms: PageContent;
  };
};

const tr: MarketingContent = {
  locale: "tr",
  nav: {
    product: "Ürün",
    how: "Nasıl çalışır?",
    solutions: "Çözümler",
    security: "Güvenlik",
    integrations: "Entegrasyonlar",
    login: "Giriş yap",
    demo: "Demo talep et",
    menu: "Menüyü aç",
  },
  footer: {
    statement:
      "Doğal dil rahatlığını modellenmiş iş bağlamı ve doğrulanmış sorgularla birleştiren konuşmalı analitik.",
    product: "Ürün",
    company: "Şirket",
    legal: "Yasal",
    privacy: "Gizlilik ve KVKK",
    terms: "Kullanım Şartları",
    about: "Hakkımızda",
    contact: "İletişim",
    rights: "Tüm hakları saklıdır.",
  },
  common: {
    learnMore: "Ayrıntıyı incele",
    available: "Kullanılabilir",
    beta: "Beta",
    planned: "Planlandı",
    finalTitle: "İlk gerçek iş sorunuzla başlayalım.",
    finalBody:
      "Veri yapınızı ve öncelikli rapor ihtiyacınızı birlikte değerlendirelim.",
    demo: "Demo talep et",
    login: "Giriş yap",
  },
  home: {
    eyebrow: "Güvenilir konuşmalı analitik",
    title: "İşletme verinizle konuşun. Cevabın nasıl üretildiğini görün.",
    description:
      "dima, doğal dilde sorduğunuz soruları modellenmiş iş bağlamına dayalı SQL’e dönüştürür, sorguyu çalıştırmadan önce doğrular ve sonucu açıklanabilir bir rapor olarak sunar.",
    process: ["Doğal dil", "Modeled context", "Dry-plan doğrulama", "Rapor"],
    proofTitle: "Cevaptan önce kanıt.",
    proofBody:
      "Hangi iş tanımının eşleştiğini, sorgunun hangi güvenlik sınırlarından geçtiğini ve sonucu üreten SQL’i aynı akışta görün.",
    pillarsTitle: "Güven, yalnızca doğru görünen bir cevaptan gelmez.",
    pillarsBody:
      "Her cevap; iş anlamını taşıyan model, sorgu güvenlik sınırları ve görünür bir çözüm izi üzerinde oluşur.",
    workflowTitle: "Sorudan rapora, görünür bir zincir.",
    workflow: [
      {
        title: "Bağla ve modelle",
        body: "Şema, ilişkiler, ölçüler, birimler ve onaylanmış iş tanımları tek bağlamda kurulur.",
      },
      {
        title: "İş dilinde sor",
        body: "Kullanıcı tablo veya kolon adı bilmeden gerçek operasyon sorusunu yazar.",
      },
      {
        title: "Planla ve doğrula",
        body: "Önerilen sorgu read-only guard ve semantic dry-plan aşamalarından geçer.",
      },
      {
        title: "İncele ve yeniden kullan",
        body: "Sonuç, SQL ve provenance görünür; doğrulanan analitik tekrar kullanılabilir.",
      },
    ],
    useCasesTitle: "Ekiplerin sorduğu gerçek sorular.",
    useCases: [
      { title: "Operasyon", question: "Bu hafta hedefinden en fazla sapan KPI’lar hangileri?" },
      { title: "Finans", question: "Brüt kârı hedefin altında kalan ürün grupları hangileri?" },
      { title: "Finans", question: "Nakit dönüşüm süresi bu çeyrekte nasıl değişti?" },
      { title: "Satış", question: "Brüt kârı düşen müşteri ve ürün grupları hangileri?" },
      { title: "Stok", question: "Kritik seviyeye yaklaşan malzemeler hangileri?" },
      { title: "Yönetim", question: "Bu hafta hedeflerden en fazla sapan üç KPI nedir?" },
    ],
    operationsTitle: "Operasyonun tamamını aynı iş diliyle anlayın.",
    operationsBody:
      "Finans, satış, stok, müşteri ve operasyon verilerini ortak tanımlar üzerinde sorgulayın; ekipler aynı metriğin farklı yorumlarıyla uğraşmasın.",
    trustTitle: "Cevabın arkasındaki mekanizmayı görün.",
    trustBody:
      "Read-only query kontrolleri, semantic model, dry-plan, görünür SQL ve permission-aware erişim; hız ile yönetişim arasında açık bir sınır kurar.",
    integrationTitle: "Mevcut veri altyapınızın üzerinde çalışır.",
    integrationBody:
      "Bağlantı, şema keşfi, semantic modeling ve doğrulama adımları kaynak desteğinin gerçek durumuyla birlikte anlatılır.",
    faqTitle: "Sık sorulanlar",
    faq: [
      {
        question: "dima bir chatbot mu?",
        answer:
          "Hayır. Sohbet arayüzü giriş noktasıdır; cevaplar modellenmiş iş bağlamı, kontrollü sorgu üretimi ve görünür raporlama akışı üzerinde oluşur.",
      },
      {
        question: "SQL’i kim doğruluyor?",
        answer:
          "LLM sorguyu önerebilir. Dima, izin verilen okuma biçimini guard ile kontrol eder ve sorgunun semantic model üzerinden planlanabilirliğini dry-plan ile doğrular.",
      },
      {
        question: "Dry-plan cevabın iş açısından kesin doğru olduğunu garanti eder mi?",
        answer:
          "Hayır. Dry-plan sorgunun planlanabilirliğini ve semantic uyumunu sınar; iş tanımlarının doğruluğu modellenmiş bağlamın kalitesine ve kullanıcı doğrulamasına bağlıdır.",
      },
      {
        question: "Hangi veri kaynakları destekleniyor?",
        answer:
          "DuckDB demo akışında, Postgres yapılandırılabilir mevcut kapsamda kullanılır. Motorun diğer connector yetenekleri Dima production desteği anlamına gelmez ve ayrı doğrulanır.",
      },
      {
        question: "On-prem kullanılabilir mi?",
        answer:
          "Thin-agent ve hibrit on-prem yaklaşımı planlanan mimaridir; hazır production özelliği olarak sunulmaz.",
      },
    ],
  },
  pages: {
    product: {
      eyebrow: "Ürün",
      title: "İş sorusundan doğrulanmış rapora, tek ürün akışında.",
      description:
        "Doğal dil arayüzü; semantic modeling, query validation ve açıklanabilir sonuç yüzeyleriyle birlikte çalışır.",
      cta: "Ürünü kendi verinizle değerlendirin",
      sections: [
        { id: "ask", title: "İş dilinde sorun", body: "Tablo ve kolon adı ezberlemeden, işletmenizin kullandığı terimlerle sorun.", points: ["Takip soruları", "Konuşma bağlamı", "Türkçe-first deneyim"] },
        { id: "model", title: "Şemayı iş anlamıyla zenginleştirin", body: "Ölçüler, boyutlar, ilişkiler, birimler ve onaylanmış tanımlar semantic modelde buluşur.", points: ["MDL semantic layer", "İlişki kataloğu", "Gösterim adları ve birimler"] },
        { id: "validate", title: "Çalıştırmadan önce doğrulayın", body: "Önerilen SQL, izinli okuma yapısı ve semantic planlanabilirlik bakımından kontrol edilir.", points: ["SELECT/WITH guard", "Dry-plan", "Görünür planned SQL"] },
        { id: "explore", title: "Sonucu uygun biçimde inceleyin", body: "Aynı veri tablo, grafik, KPI veya pivot yüzeyinde araştırılabilir.", points: ["Tablo", "Grafik", "KPI", "Pivot"] },
        { id: "verify", title: "Cevabı doğrulayın", body: "Kullanıcı geri bildirimi, provenance ve çözüm izi analitiğin nasıl oluştuğunu görünür tutar.", status: "beta" },
        { id: "reuse", title: "Tek seferlik cevabı iş akışına dönüştürün", body: "Query contract, yeniden çalıştırma, zamanlama ve bildirim kabiliyetleri kontrollü biçimde ilerler.", status: "beta" },
        { id: "govern", title: "Yetki sınırlarını koruyun", body: "Session, tenant ve permission bağlamları ürün ve backend tarafından birlikte uygulanır." },
      ],
    },
    how: {
      eyebrow: "Nasıl çalışır?",
      title: "LLM’nin önerdiği sorguyu doğrudan çalıştırmıyoruz.",
      description:
        "Doğal dil rahatlığı; semantic context ve deterministic validation katmanlarıyla sınırlandırılır.",
      cta: "Teknik bir görüşme planlayın",
      sections: [
        { id: "onboarding", title: "Kaynağı ve şemayı tanımla", body: "Bağlantı tenant bağlamında yönetilir; şema ve ilişkiler kontrollü biçimde keşfedilir." },
        { id: "semantics", title: "İş anlamını modelle", body: "İlişkiler, metrik ifadeleri, zaman boyutları, birimler ve onaylı terimler semantic modele eklenir." },
        { id: "dry-plan", title: "Öneriyi sınırla ve doğrula", body: "LLM önerisi SELECT/WITH guard’dan ve semantic dry-plan’dan geçmeden veri kaynağına ulaşmaz." },
        { id: "execute", title: "Çalıştır ve kanıtı göster", body: "İzinli sorgu çalışır; sonuç, SQL, kaynak ve çözüm izi aynı inceleme yüzeyinde sunulur." },
        { id: "planned", title: "Hibrit / thin-agent", body: "Müşteri ağına outbound-only ajan yaklaşımı mimari yöndür; mevcut production özelliği değildir.", status: "planned" },
      ],
    },
    solutions: {
      eyebrow: "Çözümler",
      title: "Her ekip için aynı veri, aynı tanım, daha hızlı cevap.",
      description:
        "Dima, organizasyon şemasını değil karar verilmesi gereken gerçek sonuçları başlangıç noktası alır.",
      cta: "Öncelikli kullanım alanınızı konuşalım",
      sections: [
        { id: "executive", title: "Karar veren ekipler", body: "Hedeflerden sapan KPI ve istisnaları, sonucu üreten tanım ve kırılımlarla birlikte görün.", points: ["Öncelikli sapmaları belirleyin", "Açıklanabilir kırılıma inin"] },
        { id: "operations", title: "Operasyonel koordinasyon", body: "Hedef, gerçekleşen ve sapma nedenlerini ekip, süreç ve dönem bağlamında aynı iş diliyle sorgulayın.", points: ["Ortak metrik tanımları", "Takip sorularıyla derinleşme"] },
        { id: "data", title: "Kurumsal hafıza ve yönetişim", body: "Ad-hoc talepleri azaltırken sorgu, provenance ve permission sınırlarını görünür tutun.", points: ["Yeniden kullanılabilir analitik", "Görünür çözüm izi"] },
      ],
    },
    security: {
      eyebrow: "Güvenlik",
      title: "Analitik hızlanırken erişim sınırları görünmez olmamalı.",
      description:
        "Mevcut güvenlik mimarisini doğrulanmış mekanizmalarla anlatıyor, sertifika veya mutlak güvenlik iddiası üretmiyoruz.",
      cta: "Güvenlik görüşmesi planlayın",
      sections: [
        { id: "read-only", title: "Read-only query controls", body: "Query akışı izinli SELECT/WITH biçimlerine göre sınırlandırılır ve planlama aşamasında doğrulanır." },
        { id: "session", title: "Session güvenliği", body: "Kısa ömürlü access token tarayıcı belleğinde; refresh token HTTP-only, same-origin cookie’de tutulur. Başarısız 401 zinciri tek refresh ve retry akışına girer." },
        { id: "tenant", title: "Tenant ve permission bağlamı", body: "UI görünürlüğü backend’den gelen izinlere dayanır; rol matrisi frontend’e kopyalanmaz. Backend her isteği yeniden yetkilendirir." },
        { id: "audit", title: "İzlenebilirlik", body: "Sorgu, auth ve yönetim eylemleri mevcut deployment kapsamına göre audit kanıtı üretebilir; kapsam müşteri sözleşmesinde doğrulanır." },
        { id: "flow", title: "Veri akışı", body: "Kullanıcı → Dima UI → same-origin Dima API → semantic engine → guarded query → müşteri veritabanı. Backend origin tarayıcıya açılmaz." },
        { id: "deployment", title: "Deployment seçenekleri", body: "Mevcut bulut topolojisi kullanılabilir. Thin-agent ve hibrit on-prem yaklaşımı planlanan durumdadır.", status: "planned" },
      ],
    },
    integrations: {
      eyebrow: "Entegrasyonlar",
      title: "Mevcut veri altyapınızın üzerinde modellenmiş analitik.",
      description:
        "Connector kabiliyetini, Dima’da doğrulanmış üretim desteğinden açıkça ayırıyoruz.",
      cta: "Entegrasyon kapsamını değerlendirin",
      sections: [
        { id: "duckdb", title: "DuckDB demo modeli", body: "Ürün akışını gerçek müşteri verisi kullanmadan gösteren sentetik veri kaynağıdır.", status: "available" },
        { id: "postgres", title: "Postgres", body: "Dima bağlantı konfigürasyonunda kullanılan ve mevcut kapsamda desteklenen kaynaktır.", status: "available" },
        { id: "engine", title: "MSSQL ve Oracle", body: "Wren motorunda connector kabiliyeti bulunur; Dima production desteği lehçe, model ve gerçek bağlantı testleri tamamlanmadan ilan edilmez.", status: "planned" },
        { id: "process", title: "Onboarding akışı", body: "Bağlantı → şema keşfi → semantic model → dry-plan doğrulaması → tenant-scoped kullanıcı erişimi." },
        { id: "status", title: "Destek ne anlama gelir?", body: "Her kaynak current-tested, engine-capable veya planned olarak açıkça etiketlenir; connector sayısı pazarlama metriğine çevrilmez." },
      ],
    },
    about: {
      eyebrow: "Hakkımızda",
      title: "İşletme verisini daha anlaşılır ve denetlenebilir kılmak için.",
      description:
        "dima, UpcyTech Teknoloji Anonim Şirketi tarafından geliştirilen güvenilir konuşmalı analitik ürünüdür.",
      cta: "Bizimle iletişime geçin",
      sections: [
        { id: "purpose", title: "Neden dima?", body: "İş ekiplerinin cevap için teknik rapor sırasına girmesi ile data ekiplerinin kontrol ihtiyacı arasındaki gerilimi azaltmak için." },
        { id: "principles", title: "Dört ürün ilkesi", body: "Deterministic, Intelligent, Modeled ve Agentic; slogan değil, ürün mekanizmalarını tarif eder.", points: ["LLM önerir; motor doğrular", "İş dilinde erişim", "Onaylı semantic context", "Tekrar kullanılabilir analitik"] },
        { id: "company", title: "UpcyTech", body: "UpcyTech, ekiplerin karmaşık iş akışlarını daha anlaşılır ve yönetilebilir kılan yazılım ürünleri geliştirir. Dima bu ürün ekosisteminin analitik katmanıdır." },
        { id: "truth", title: "Kanıtı iddianın önüne koyuyoruz", body: "Sahte istatistik, sertifika, müşteri logosu veya doğrulanmamış roadmap iddiası kullanmıyoruz." },
      ],
    },
  },
  legal: {
    lastUpdated: "26 Temmuz 2026",
    notice:
      "Bu metinler mevcut teknik mimari ve güncel mevzuat kaynakları esas alınarak hazırlanmıştır. Yayın öncesinde şirketin hukuk danışmanı tarafından şirket kaydı, veri aktarım mekanizması ve ticari hükümler doğrulanmalıdır.",
    privacy: {
      eyebrow: "Gizlilik ve KVKK",
      title: "Kişisel verilerinizi nasıl işlediğimizi açıkça anlatıyoruz.",
      description:
        "Bu politika dima web sitesi, demo talebi ve dima SaaS hizmetindeki temel veri işleme rollerini kapsar.",
      cta: "Gizlilik hakkında bize yazın",
      sections: [
        { id: "controller", title: "1. Veri sorumlusu", body: "UPCYTECH TEKNOLOJİ ANONİM ŞİRKETİ (“UpcyTech”), Reşitpaşa Mah. Katar Cad. İTÜ Tasarım ve Prototip Merkezi No:2/41 İç Kapı:19, 34469 Sarıyer/İstanbul. İletişim: contact@upcytech.com." },
        { id: "scope", title: "2. Roller ve kapsam", body: "UpcyTech; web sitesi, hesap yönetimi, güvenlik ve demo taleplerinde veri sorumlusudur. Müşterinin dima’ya yüklediği veya bağlı veri kaynağında tuttuğu iş verilerinde müşteri veri sorumlusu, UpcyTech ise sözleşme ve talimatlar çerçevesinde veri işleyen olabilir." },
        { id: "categories", title: "3. İşlenen veri kategorileri", body: "Kimlik ve iletişim verileri; şirket/rol bilgisi; hesap ve tenant tanımlayıcıları; oturum, IP, cihaz ve güvenlik kayıtları; destek/demo mesajları; ürün içinde kullanıcının yazdığı sorular, oluşturulan SQL, rapor metadata’sı, doğrulama ve audit kayıtları. Özel nitelikli veri talep etmiyoruz; serbest metin alanlarına bu tür veri girilmemelidir." },
        { id: "purposes", title: "4. Amaçlar ve hukuki sebepler", body: "Demo ve iletişim talepleri talep üzerine iletişim kurmak ve meşru B2B ilişki yönetimi için; hesap ve ürün verileri sözleşmenin kurulması/ifası için; güvenlik ve audit kayıtları hukuki yükümlülükler ile temel haklara zarar vermeyen meşru menfaat için; açık rızaya dayanan ayrı bir pazarlama faaliyeti varsa yalnız ilgili rıza kapsamında işlenir." },
        { id: "collection", title: "5. Toplama yöntemi", body: "Veriler formlar, hesap ve oturum işlemleri, ürün kullanımı, same-origin API trafiği, destek iletişimi ve güvenlik logları üzerinden tamamen veya kısmen otomatik yöntemlerle elde edilir." },
        { id: "sharing", title: "6. Alıcı grupları", body: "Veriler; barındırma ve altyapı sağlayıcıları, e-posta teslim hizmeti, sözleşmeyle bağlı teknik hizmet sağlayıcılar, yetkili kamu kurumları ve hukuki yükümlülük halinde danışmanlarla yalnız gerekli kapsamda paylaşılabilir. Reklam veri brokerlarına satılmaz." },
        { id: "transfer", title: "7. Yurt dışı aktarım", body: "Vercel ve Resend gibi hizmetlerin kullanıldığı deployment’larda hesap dışı teknik veriler ve iletişim formu verileri yurt dışında işlenebilir. Aktarım, KVKK m.9’daki yeterlilik, uygun güvence/standart sözleşme veya kanundaki istisnai aktarım şartlarından uygulanabilir olana dayanır. Resend üzerinden gönderim başlamadan önce uygun mekanizma ve Kurul bildirimi doğrulanır." },
        { id: "retention", title: "8. Saklama ve silme", body: "Demo/iletişim verileri son anlamlı etkileşimden itibaren 12 ay saklanır. Hesap, sözleşme ve müşteri verileri sözleşme süresince ve uygulanabilir yasal zamanaşımı/saklama sürelerince; güvenlik kayıtları risk ve mevzuatla orantılı süre boyunca tutulur. Süre dolunca veri silinir, yok edilir veya anonimleştirilir." },
        { id: "cookies", title: "9. Çerezler ve yerel depolama", body: "HTTP-only session cookie kimlik doğrulama için, dima_locale çerezi dil tercihi için gereklidir. Tema tercihi tarayıcı localStorage alanında tutulabilir. Marketing analytics adapter’ı başlangıçta no-op’tur; analitik veya reklam çerezi yerleştirmez." },
        { id: "security", title: "10. Güvenlik", body: "Same-origin API proxy, memory access token, HTTP-only refresh cookie, permission kontrolleri, tenant bağlamı, güvenlik başlıkları ve audit kayıtları gibi teknik/idari tedbirler uygulanır. Hiçbir internet iletimi veya depolama yöntemi mutlak güvenlik garantisi vermez." },
        { id: "rights", title: "11. KVKK m.11 hakları", body: "Verinizin işlenip işlenmediğini öğrenme, bilgi isteme, amacına uygun kullanımı öğrenme, aktarılan üçüncü kişileri bilme, düzeltme, silme/yok etme, düzeltme veya silmenin alıcılara bildirilmesini isteme, otomatik analiz sonucuna itiraz ve hukuka aykırı işlem nedeniyle zararın giderilmesini talep etme haklarına sahipsiniz." },
        { id: "application", title: "12. Başvuru yöntemi", body: "Talebinizi kimliğinizi ve talebinizi doğrulamaya yeterli bilgilerle contact@upcytech.com adresine veya şirketin kayıtlı adresine iletebilirsiniz. Başvurular niteliğine göre en kısa sürede ve en geç 30 gün içinde, mevzuattaki ücret istisnaları dışında ücretsiz sonuçlandırılır." },
        { id: "changes", title: "13. Değişiklikler", body: "Politika veri işleme faaliyetleri veya mevzuat değiştiğinde güncellenebilir. Önemli değişiklikler yürürlüğe girmeden önce uygun kanallardan duyurulur; güncel tarih sayfanın üstünde gösterilir." },
      ],
    },
    terms: {
      eyebrow: "Kullanım Şartları",
      title: "dima hizmetini kullanırken geçerli olan şartlar.",
      description:
        "Bu şartlar, UpcyTech ile dima hizmetini kullanan işletme ve yetkili kullanıcı arasındaki SaaS kullanım ilişkisini düzenler.",
      cta: "Şartlar hakkında bize yazın",
      sections: [
        { id: "party", title: "1. Taraflar ve kabul", body: "Bu şartlar UPCYTECH TEKNOLOJİ ANONİM ŞİRKETİ (“UpcyTech”) ile dima’ya erişen müşteri kuruluş ve onun yetkili kullanıcıları arasındadır. Sipariş formu, teklif, ana hizmet sözleşmesi veya veri işleme eki varsa özel hükümler bu genel şartlara üstün gelir. Kuruluş adına işlem yapan kişi bağlama yetkisi olduğunu beyan eder." },
        { id: "service", title: "2. Hizmet", body: "dima; doğal dil sorularını modellenmiş semantic context üzerinden sorgu ve rapor akışına dönüştüren B2B SaaS analitik hizmetidir. Kapsam, tenant konfigürasyonu, lisanslanan modüller, feature flag’ler ve sipariş formuna göre değişebilir." },
        { id: "account", title: "3. Hesap ve güvenlik", body: "Kullanıcı doğru bilgi sağlamalı, kimlik bilgilerini paylaşmamalı, MFA ve güvenlik kontrollerini devre dışı bırakmamalı ve şüpheli erişimi gecikmeden bildirmelidir. Müşteri kullanıcı yetkilerini ve işten ayrılan kullanıcıların erişimini yönetmekten sorumludur." },
        { id: "license", title: "4. Sınırlı kullanım hakkı", body: "UpcyTech, sözleşme süresince müşteriye kendi iç iş amaçları için devredilemez, münhasır olmayan ve sınırlı bir kullanım hakkı verir. Hizmet satılmaz; fikri mülkiyet hakları UpcyTech ve lisans verenlerinde kalır." },
        { id: "acceptable", title: "5. Kabul edilebilir kullanım", body: "Hizmet hukuka aykırı faaliyet, yetkisiz erişim, güvenlik testi, tersine mühendislik, kaynak kod çıkarma, zararlı yazılım, aşırı otomatik yük, üçüncü kişi hak ihlali veya izin verilmeyen kişisel veri işleme için kullanılamaz. Güvenliği veya diğer tenant’ları etkileyen kullanım askıya alınabilir." },
        { id: "customer-data", title: "6. Müşteri verisi", body: "Müşteri kendi verisinin ve talimatlarının hukuka uygunluğundan, gerekli aydınlatma/izinlerden ve veri kaynağı erişim yetkisinden sorumludur. UpcyTech müşteri verisini hizmeti sunmak, güvenliğini sağlamak ve belgelenmiş talimatları yerine getirmek için işler; veri üzerindeki hak müşteride kalır." },
        { id: "ai", title: "7. AI ve analitik çıktılar", body: "LLM sorgu veya yorum önerebilir; Dima guard ve dry-plan kontrolleri uygular. Bu kontroller iş tanımlarının, kaynak verinin veya sonucun mutlak doğruluğunu garanti etmez. Çıktılar profesyonel, hukuki, mali veya güvenlik kararlarında insan incelemesi olmadan tek dayanak yapılmamalıdır." },
        { id: "beta", title: "8. Beta ve planlanan özellikler", body: "Beta özellikler değişebilir, sınırlı desteklenebilir veya kaldırılabilir. Planlanan özellikler taahhüt edilmiş teslim tarihi oluşturmaz. Query contracts, doğrulama, zamanlama ve bildirim kapsamı tenant özelliği ve sözleşmeyle belirlenir." },
        { id: "fees", title: "9. Ücret, vergi ve yenileme", body: "Ücretler, para birimi, ödeme takvimi, vergi, kullanım limitleri ve yenileme koşulları sipariş formu veya teklifte belirtilir. Public web sitesinde fiyat yayımlanmaması ücretsiz hizmet anlamına gelmez. Geciken tutarlar uygulanabilir hukuk ve sözleşme sınırlarında erişim kısıtına yol açabilir." },
        { id: "availability", title: "10. Değişiklik ve erişilebilirlik", body: "UpcyTech güvenlik, performans ve ürün gelişimi için hizmeti güncelleyebilir. Belirli uptime, destek süresi, bakım penceresi veya servis kredisi yalnız imzalı SLA veya sipariş formunda yazıyorsa geçerlidir." },
        { id: "confidentiality", title: "11. Gizlilik", body: "Taraflar hizmet ilişkisi içinde öğrendikleri kamuya açık olmayan teknik, ticari ve müşteri bilgilerini yalnız sözleşme amacıyla kullanır ve makul koruma tedbirleri uygular. Kanunen zorunlu açıklamalar mümkünse önceden bildirilir." },
        { id: "ip", title: "12. Fikri mülkiyet ve geri bildirim", body: "Dima yazılımı, modelleri, arayüzü, dokümantasyonu ve türevleri UpcyTech’e veya lisans verenlerine aittir. Müşteri verisi müşteriye aittir. Kullanıcı geri bildirimi gizli bilgi içermemek kaydıyla ürün geliştirmede bedelsiz kullanılabilir." },
        { id: "third-party", title: "13. Üçüncü taraf hizmetleri", body: "Veri kaynağı, LLM sağlayıcısı, hosting veya e-posta teslimi gibi üçüncü taraflar kendi şartlarına tabi olabilir. UpcyTech seçtiği alt işleyenleri veri koruma yükümlülükleriyle bağlar; müşterinin bağımsız seçtiği entegrasyonlardan müşteri sorumludur." },
        { id: "termination", title: "14. Süre, askıya alma ve fesih", body: "Süre ve fesih hakları sipariş formunda belirlenir. Esaslı ihlal, güvenlik riski, hukuka aykırı kullanım veya ödeme temerrüdü halinde erişim bildirimle ya da acil riskte derhal askıya alınabilir. Fesih sonrası veri iadesi ve silme sözleşme/veri işleme eki ile yasal saklama yükümlülüklerine göre yürütülür." },
        { id: "warranty", title: "15. Garantilerin sınırı", body: "Emredici hukuk dışında hizmet “mevcut haliyle” sunulur. Kesintisizlik, her veri kaynağıyla uyum, her sorgunun doğru yorumlanması veya tüm hataların giderileceği garanti edilmez. UpcyTech üzerinde anlaşılan hizmeti mesleki özenle sunar." },
        { id: "liability", title: "16. Sorumluluk sınırı", body: "Emredici hukuk, kast, ağır kusur, gizlilik veya kişisel veri ihlalinde sınırlandırılamayan sorumluluklar saklıdır. Diğer hallerde UpcyTech’in toplam sözleşmesel sorumluluğu, talebe yol açan olaydan önceki 12 ayda ilgili hizmet için ödenen net ücretlerle sınırlıdır; dolaylı zarar ve kâr/veri kaybı uygulanabilir hukukun izin verdiği ölçüde kapsam dışıdır." },
        { id: "indemnity", title: "17. Üçüncü kişi talepleri", body: "Müşteri; hukuka aykırı müşteri verisi, yetkisiz veri kaynağı erişimi veya kabul edilebilir kullanım ihlalinden doğan üçüncü kişi taleplerinde, kendi kusuru ve sorumluluğu ölçüsünde UpcyTech’i savunur ve zararını karşılar." },
        { id: "force", title: "18. Mücbir sebep", body: "Tarafın makul kontrolü dışındaki afet, savaş, yaygın iletişim/enerji kesintisi, kamu otoritesi işlemi veya kritik tedarikçi kesintisinde etkilenen yükümlülükler olay süresince askıda kalabilir; etkilenen taraf makul azaltma çabası gösterir." },
        { id: "law", title: "19. Uygulanacak hukuk ve uyuşmazlık", body: "Şartlara Türkiye Cumhuriyeti hukuku uygulanır. Tacirler arasındaki uyuşmazlıklarda İstanbul Merkez (Çağlayan) Mahkemeleri ve İcra Daireleri yetkilidir. Emredici tüketici hükümleri uygulanıyorsa tüketicinin kanuni başvuru yerleri saklıdır." },
        { id: "changes", title: "20. Değişiklik ve iletişim", body: "Esaslı değişiklikler makul süre önce hesap içi bildirim, e-posta veya web duyurusuyla bildirilir. Değişikliği kabul etmeyen müşteri sözleşmedeki fesih haklarını kullanabilir. Sorular: contact@upcytech.com." },
      ],
    },
  },
};

const en: MarketingContent = {
  ...tr,
  locale: "en",
  nav: {
    product: "Product",
    how: "How it works",
    solutions: "Solutions",
    security: "Security",
    integrations: "Integrations",
    login: "Sign in",
    demo: "Request a demo",
    menu: "Open menu",
  },
  footer: {
    statement:
      "Conversational analytics combining natural-language access with modeled business context and validated queries.",
    product: "Product",
    company: "Company",
    legal: "Legal",
    privacy: "Privacy & KVKK",
    terms: "Terms of Service",
    about: "About",
    contact: "Contact",
    rights: "All rights reserved.",
  },
  common: {
    learnMore: "Explore the details",
    available: "Available",
    beta: "Beta",
    planned: "Planned",
    finalTitle: "Let’s begin with your first real business question.",
    finalBody: "We can assess your data model and highest-priority reporting need together.",
    demo: "Request a demo",
    login: "Sign in",
  },
  home: {
    eyebrow: "Trusted conversational analytics",
    title: "Talk to your business data. See how the answer was produced.",
    description:
      "dima turns natural-language questions into SQL grounded in modeled business context, validates the query before execution, and presents the result as an explainable report.",
    process: ["Natural language", "Modeled context", "Dry-plan validation", "Report"],
    proofTitle: "Evidence before answers.",
    proofBody:
      "See which business definitions matched, which query controls passed, and the SQL that produced the result.",
    pillarsTitle: "Trust takes more than an answer that looks right.",
    pillarsBody:
      "Every answer is formed on business semantics, query boundaries, and a visible resolution trace.",
    workflowTitle: "A visible chain from question to report.",
    workflow: [
      { title: "Connect and model", body: "Define schema, relationships, measures, units, and approved business definitions." },
      { title: "Ask in business language", body: "Users ask real operational questions without knowing table or column names." },
      { title: "Plan and validate", body: "The proposed query passes read-only guards and a semantic dry plan." },
      { title: "Inspect and reuse", body: "The result, SQL, and provenance remain visible and reusable." },
    ],
    useCasesTitle: "Questions real teams ask.",
    useCases: [
      { title: "Operations", question: "Which KPIs deviated most from target this week?" },
      { title: "Finance", question: "Which product groups are below gross-margin target?" },
      { title: "Finance", question: "How did the cash conversion cycle change this quarter?" },
      { title: "Sales", question: "Which customer and product groups lost gross margin?" },
      { title: "Inventory", question: "Which materials are approaching critical stock?" },
      { title: "Executive", question: "Which three KPIs deviated most from target this week?" },
    ],
    operationsTitle: "Understand the whole operation in one business language.",
    operationsBody:
      "Query finance, sales, inventory, customer, and operational data through shared definitions so teams do not interpret the same metric differently.",
    trustTitle: "See the mechanism behind the answer.",
    trustBody:
      "Read-only controls, the semantic model, dry-plan validation, visible SQL, and permission-aware access create an explicit governance boundary.",
    integrationTitle: "Built over your existing data infrastructure.",
    integrationBody:
      "Connection, schema discovery, semantic modeling, and validation are explained alongside the real support status of each source.",
    faqTitle: "Frequently asked questions",
    faq: [
      { question: "Is dima a chatbot?", answer: "No. Chat is the entry point; answers are produced through modeled context, controlled query generation, and explainable reporting." },
      { question: "Who validates the SQL?", answer: "The LLM may propose a query. Dima checks its permitted read structure and validates semantic planability with a dry plan." },
      { question: "Does dry-plan guarantee business correctness?", answer: "No. It checks planability and semantic execution. Business correctness also depends on the quality of model definitions and human verification." },
      { question: "Which data sources are supported?", answer: "DuckDB powers the demo and Postgres is configurable in the current scope. Engine connector capabilities are not automatically Dima production support." },
      { question: "Is on-prem available?", answer: "The thin-agent and hybrid on-prem model is planned architecture, not a currently available production capability." },
    ],
  },
  pages: {
    product: {
      eyebrow: "Product",
      title: "From business question to validated report in one product flow.",
      description: "Natural-language access works together with semantic modeling, query validation, and explainable result surfaces.",
      cta: "Evaluate dima with your own data",
      sections: [
        { id: "ask", title: "Ask in business language", body: "Use the terms your organization knows—without memorizing tables or columns.", points: ["Follow-up questions", "Conversation context", "Turkish-first experience"] },
        { id: "model", title: "Enrich schemas with business meaning", body: "Measures, dimensions, relationships, units, and approved definitions meet in the semantic model.", points: ["MDL semantic layer", "Relationship catalog", "Display labels and units"] },
        { id: "validate", title: "Validate before execution", body: "Proposed SQL is checked for permitted read structure and semantic planability.", points: ["SELECT/WITH guard", "Dry plan", "Visible planned SQL"] },
        { id: "explore", title: "Explore in the right format", body: "Inspect the same data as a table, chart, KPI, or pivot.", points: ["Table", "Chart", "KPI", "Pivot"] },
        { id: "verify", title: "Verify the answer", body: "Feedback, provenance, and the resolution trace keep the analytical path visible.", status: "beta" },
        { id: "reuse", title: "Turn one answer into a workflow", body: "Query contracts, replay, schedules, and notifications evolve under controlled feature status.", status: "beta" },
        { id: "govern", title: "Preserve access boundaries", body: "Session, tenant, and permission contexts are enforced by both product and backend." },
      ],
    },
    how: {
      eyebrow: "How it works",
      title: "We do not execute an LLM-proposed query directly.",
      description: "Natural-language convenience is bounded by semantic context and deterministic validation.",
      cta: "Schedule a technical conversation",
      sections: [
        { id: "onboarding", title: "Define the source and schema", body: "The connection is managed in tenant context; schema and relationships are discovered under control." },
        { id: "semantics", title: "Model business meaning", body: "Relationships, metric expressions, time dimensions, units, and approved terms are added to the semantic model." },
        { id: "dry-plan", title: "Bound and validate the proposal", body: "An LLM proposal cannot reach the source before the SELECT/WITH guard and semantic dry plan pass." },
        { id: "execute", title: "Execute and show evidence", body: "The permitted query runs; result, SQL, source, and resolution trace appear in one inspection surface." },
        { id: "planned", title: "Hybrid / thin agent", body: "An outbound-only customer-network agent is planned architecture, not a current production feature.", status: "planned" },
      ],
    },
    solutions: {
      eyebrow: "Solutions",
      title: "The same data and definitions, with faster answers for every team.",
      description: "Dima starts with the outcome that needs a decision—not only the org chart.",
      cta: "Discuss your priority use case",
      sections: [
        { id: "executive", title: "Decision-making teams", body: "See KPI deviations and exceptions together with the definitions and breakdowns that produced them.", points: ["Identify priority deviations", "Move into an explainable breakdown"] },
        { id: "operations", title: "Operational coordination", body: "Query targets, actuals, and drivers across teams, processes, and periods in one business language.", points: ["Shared metric definitions", "Deeper follow-up questions"] },
        { id: "data", title: "Institutional memory and governance", body: "Reduce ad-hoc requests while keeping queries, provenance, and permission boundaries visible.", points: ["Reusable analytics", "Visible resolution trace"] },
      ],
    },
    security: {
      eyebrow: "Security",
      title: "Access boundaries should not disappear as analytics gets faster.",
      description: "We describe verified mechanisms—not certifications or absolute security claims.",
      cta: "Schedule a security review",
      sections: [
        { id: "read-only", title: "Read-only query controls", body: "The query flow is constrained to permitted SELECT/WITH shapes and checked during planning." },
        { id: "session", title: "Session security", body: "Short-lived access tokens stay in memory; refresh tokens use HTTP-only same-origin cookies with single-flight refresh and retry." },
        { id: "tenant", title: "Tenant and permission context", body: "UI visibility comes from backend permissions; the role matrix is not duplicated in the frontend, and the backend reauthorizes each request." },
        { id: "audit", title: "Auditability", body: "Query, authentication, and management actions can produce audit evidence according to deployment scope; customer contracts confirm coverage." },
        { id: "flow", title: "Data flow", body: "User → Dima UI → same-origin Dima API → semantic engine → guarded query → customer database. The backend origin remains private." },
        { id: "deployment", title: "Deployment options", body: "The current cloud topology is available. Thin-agent and hybrid on-prem remain planned.", status: "planned" },
      ],
    },
    integrations: {
      eyebrow: "Integrations",
      title: "Modeled analytics over your existing data infrastructure.",
      description: "We distinguish engine capability from production-tested Dima support.",
      cta: "Assess your integration scope",
      sections: [
        { id: "duckdb", title: "DuckDB demo model", body: "A synthetic source that demonstrates the product flow without real customer data.", status: "available" },
        { id: "postgres", title: "Postgres", body: "A data source used in Dima connection configuration and supported in the current scope.", status: "available" },
        { id: "engine", title: "MSSQL and Oracle", body: "Connectors exist in the Wren engine; Dima production support requires dialect, model, and live-connection validation.", status: "planned" },
        { id: "process", title: "Onboarding flow", body: "Connection → schema discovery → semantic model → dry-plan validation → tenant-scoped access." },
        { id: "status", title: "What support means", body: "Each source is labeled current-tested, engine-capable, or planned. Connector counts are not used as marketing metrics." },
      ],
    },
    about: {
      eyebrow: "About",
      title: "Making business data easier to understand and audit.",
      description: "dima is a trusted conversational analytics product built by UpcyTech Teknoloji Anonim Şirketi.",
      cta: "Contact us",
      sections: [
        { id: "purpose", title: "Why dima?", body: "To reduce the tension between business teams waiting for reports and data teams preserving control." },
        { id: "principles", title: "Four product principles", body: "Deterministic, Intelligent, Modeled, and Agentic describe product mechanisms—not decorative slogans.", points: ["The LLM proposes; the engine validates", "Business-language access", "Approved semantic context", "Reusable analytics"] },
        { id: "company", title: "UpcyTech", body: "UpcyTech builds software that makes complex business workflows easier for teams to understand and manage. Dima is the analytics layer of this product ecosystem." },
        { id: "truth", title: "Evidence before claims", body: "We do not use fabricated statistics, certifications, customer logos, or unverified roadmap claims." },
      ],
    },
  },
  legal: {
    lastUpdated: "July 26, 2026",
    notice:
      "These documents reflect the current technical architecture and researched legal framework. Company registration details, international-transfer mechanisms, and commercial clauses must be confirmed by company counsel before publication.",
    privacy: {
      eyebrow: "Privacy & KVKK",
      title: "How we process personal data.",
      description: "This policy covers the dima website, demo requests, and the principal data-processing roles within the dima SaaS service.",
      cta: "Contact us about privacy",
      sections: [
        { id: "controller", title: "1. Data controller", body: "UPCYTECH TEKNOLOJİ ANONİM ŞİRKETİ (“UpcyTech”), Reşitpaşa Mah. Katar Cad. İTÜ Tasarım ve Prototip Merkezi No:2/41 İç Kapı:19, 34469 Sarıyer/İstanbul. Contact: contact@upcytech.com." },
        { id: "scope", title: "2. Roles and scope", body: "UpcyTech is the data controller for the website, account administration, security, and demo requests. For business data uploaded by a customer or held in a connected source, the customer may be controller and UpcyTech processor under the agreement and documented instructions." },
        { id: "categories", title: "3. Data categories", body: "We may process identity and contact details; company and role; account and tenant identifiers; session, IP, device, and security records; support and demo messages; user questions, generated SQL, report metadata, verification, and audit records. Do not enter special-category data into free-text fields." },
        { id: "purposes", title: "4. Purposes and legal grounds", body: "Demo and contact data supports requested communication and legitimate B2B relationship management; account and product data supports formation and performance of a contract; security and audit data supports legal duties and legitimate interests that do not override fundamental rights. Separate marketing based on consent is processed only within that consent." },
        { id: "collection", title: "5. Collection", body: "Data is collected wholly or partly by automated means through forms, account and session activity, product use, same-origin API traffic, support communications, and security logs." },
        { id: "sharing", title: "6. Recipients", body: "Data may be shared only as necessary with hosting and infrastructure providers, email delivery services, contracted technical providers, authorized public bodies, and advisers where legally required. It is not sold to advertising data brokers." },
        { id: "transfer", title: "7. International transfers", body: "In deployments using services such as Vercel and Resend, non-account technical data and contact-form data may be processed abroad. Transfers rely on an applicable mechanism under KVKK Article 9, such as adequacy, appropriate safeguards/standard contracts, or a statutory exception. The applicable mechanism and required Board notification must be confirmed before Resend delivery is enabled." },
        { id: "retention", title: "8. Retention and deletion", body: "Demo and contact data is retained for 12 months after the last meaningful interaction. Account, contract, and customer data is retained for the contract term and applicable statutory periods; security records are retained proportionately to risk and law. Expired data is deleted, destroyed, or anonymized." },
        { id: "cookies", title: "9. Cookies and local storage", body: "The HTTP-only session cookie is necessary for authentication and the dima_locale cookie stores language preference. Theme preference may use browser localStorage. The initial marketing analytics adapter is a no-op and sets no analytics or advertising cookies." },
        { id: "security", title: "10. Security", body: "Measures include a same-origin API proxy, in-memory access tokens, HTTP-only refresh cookies, permission checks, tenant context, security headers, and audit records. No internet transmission or storage method can guarantee absolute security." },
        { id: "rights", title: "11. Rights under KVKK Article 11", body: "You may ask whether and how your data is processed; learn the purpose and recipients; request correction, deletion, destruction, and recipient notification; object to outcomes based solely on automated analysis; and seek compensation for unlawful processing." },
        { id: "application", title: "12. Exercising your rights", body: "Send sufficient identity and request details to contact@upcytech.com or the registered address. Requests are resolved as soon as possible and no later than 30 days, free of charge except where legislation permits a fee." },
        { id: "changes", title: "13. Changes", body: "We may update this policy when processing or law changes. Material changes are announced through appropriate channels before taking effect, and the current date appears above." },
      ],
    },
    terms: {
      eyebrow: "Terms of Service",
      title: "The terms that apply when you use dima.",
      description: "These terms govern the SaaS relationship between UpcyTech, customer organizations, and their authorized users.",
      cta: "Contact us about the terms",
      sections: [
        { id: "party", title: "1. Parties and acceptance", body: "These terms are between UPCYTECH TEKNOLOJİ ANONİM ŞİRKETİ (“UpcyTech”), the customer organization accessing dima, and its authorized users. A signed order form, proposal, master agreement, or data-processing addendum prevails where it contains specific terms. A person acting for an organization represents authority to bind it." },
        { id: "service", title: "2. Service", body: "dima is a B2B SaaS analytics service that turns natural-language questions into query and reporting flows grounded in modeled semantic context. Scope may vary by tenant configuration, licensed modules, feature flags, and order form." },
        { id: "account", title: "3. Accounts and security", body: "Users must provide accurate information, protect credentials, avoid disabling MFA or security controls, and promptly report suspected access. Customers manage user permissions and remove access for departing personnel." },
        { id: "license", title: "4. Limited right to use", body: "During the contract term, UpcyTech grants the customer a limited, non-exclusive, non-transferable right to use the service for internal business purposes. The service is licensed, not sold; intellectual-property rights remain with UpcyTech and its licensors." },
        { id: "acceptable", title: "5. Acceptable use", body: "The service may not be used for unlawful activity, unauthorized access or security testing, reverse engineering, source extraction, malware, excessive automated load, infringement, or unauthorized personal-data processing. Use affecting security or other tenants may be suspended." },
        { id: "customer-data", title: "6. Customer data", body: "The customer is responsible for the lawfulness of its data and instructions, required notices and permissions, and authority to access each source. UpcyTech processes customer data to provide and secure the service and follow documented instructions; rights in customer data remain with the customer." },
        { id: "ai", title: "7. AI and analytical output", body: "An LLM may propose queries or interpretations; dima applies guard and dry-plan controls. These controls do not guarantee absolute correctness of business definitions, source data, or results. Output should not be the sole basis for professional, legal, financial, or security decisions without human review." },
        { id: "beta", title: "8. Beta and planned features", body: "Beta features may change, receive limited support, or be withdrawn. Planned features are not committed delivery dates. Query contracts, verification, scheduling, and notifications depend on tenant features and contract scope." },
        { id: "fees", title: "9. Fees, tax, and renewal", body: "Fees, currency, payment schedule, taxes, usage limits, and renewal are stated in the order form or proposal. The absence of public pricing does not make the service free. Overdue amounts may lead to access restrictions within applicable law and contract terms." },
        { id: "availability", title: "10. Changes and availability", body: "UpcyTech may update the service for security, performance, and product development. Uptime, support times, maintenance windows, or service credits apply only where written in a signed SLA or order form." },
        { id: "confidentiality", title: "11. Confidentiality", body: "Each party uses non-public technical, commercial, and customer information learned through the relationship only for the agreement and protects it with reasonable measures. Legally compelled disclosure is notified in advance where permitted." },
        { id: "ip", title: "12. Intellectual property and feedback", body: "Dima software, models, interface, documentation, and derivatives belong to UpcyTech or its licensors. Customer data belongs to the customer. Feedback that contains no confidential information may be used without charge to improve the product." },
        { id: "third-party", title: "13. Third-party services", body: "Data sources, LLM providers, hosting, and email delivery may be subject to third-party terms. UpcyTech binds its selected subprocessors to data-protection obligations; customers remain responsible for independently selected integrations." },
        { id: "termination", title: "14. Term, suspension, and termination", body: "Term and termination rights are stated in the order form. Material breach, security risk, unlawful use, or payment default may result in suspension after notice or immediately for urgent risk. Data return and deletion follow the agreement, data-processing addendum, and legal retention duties." },
        { id: "warranty", title: "15. Warranty limits", body: "Except where mandatory law requires otherwise, the service is provided as available. We do not guarantee uninterrupted operation, compatibility with every source, correct interpretation of every query, or correction of every defect. UpcyTech provides the agreed service with professional care." },
        { id: "liability", title: "16. Liability limits", body: "Liability that cannot be limited under mandatory law—including intent, gross negligence, confidentiality, or personal-data breach—remains unaffected. Otherwise, UpcyTech’s aggregate contractual liability is limited to net fees paid for the relevant service in the 12 months before the event; indirect damages and loss of profit or data are excluded to the extent permitted by law." },
        { id: "indemnity", title: "17. Third-party claims", body: "To the extent caused by its fault and responsibility, the customer defends and indemnifies UpcyTech against third-party claims arising from unlawful customer data, unauthorized source access, or breach of acceptable use." },
        { id: "force", title: "18. Force majeure", body: "Obligations affected by events beyond reasonable control—including disaster, war, widespread communications or power failure, public-authority action, or critical supplier outage—may be suspended for the event; the affected party uses reasonable mitigation efforts." },
        { id: "law", title: "19. Governing law and disputes", body: "The laws of the Republic of Türkiye govern these terms. For disputes between merchants, Istanbul Central (Çağlayan) Courts and Enforcement Offices have jurisdiction. Mandatory consumer venues remain available where consumer law applies." },
        { id: "changes", title: "20. Changes and contact", body: "Material changes are announced within a reasonable time through in-account notice, email, or the website. A customer that does not accept a change may exercise contractual termination rights. Questions: contact@upcytech.com." },
      ],
    },
  },
};

export function getMarketingContent(locale: string): MarketingContent {
  return locale === "en" ? en : tr;
}

export const publicRoutes = [
  "/",
  "/product",
  "/how-it-works",
  "/solutions",
  "/security",
  "/integrations",
  "/about",
  "/contact",
  "/privacy",
  "/terms",
] as const;
