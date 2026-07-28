export type MarketingLocale = "tr" | "en";
export type CapabilityStatus = "available" | "beta" | "planned";
export type MarketingSceneKey =
  | "question"
  | "definitions"
  | "checks"
  | "results"
  | "source"
  | "reuse"
  | "access"
  | "priority"
  | "coordination"
  | "memory"
  | "session"
  | "audit"
  | "data-flow"
  | "deployment"
  | "database"
  | "connection"
  | "support"
  | "purpose"
  | "principles"
  | "company"
  | "truth";

export type ContentSection = {
  id: string;
  title: string;
  body: string;
  points?: string[];
  status?: CapabilityStatus;
  visual?: {
    key: MarketingSceneKey;
    caption: string;
    technicalNote?: string;
  };
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
    rotateWords: string[];
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
      "İşletme verisine soru sormayı, cevabı anlamayı ve dayanağını görmeyi kolaylaştıran analitik.",
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
    available: "Dima’da doğrulandı",
    beta: "Beta",
    planned: "Planlanıyor",
    finalTitle: "İlk gerçek iş sorunuzla başlayalım.",
    finalBody:
      "Veri yapınızı ve öncelikli rapor ihtiyacınızı birlikte değerlendirelim.",
    demo: "Demo talep et",
    login: "Giriş yap",
  },
  home: {
    eyebrow: "İşletme verisini anlamanın daha kolay yolu",
    title: "Verinize sorun. Sonucu",
    rotateWords: ["anlayın.", "karşılaştırın.", "paylaşın."],
    description:
      "dima, günlük iş dilinizle sorduğunuz soruları verinizde bulur; sonucu tablo veya grafikle gösterir ve cevabın nereden geldiğini açıklar.",
    process: ["Sorunuzu yazın", "İş tanımlarıyla eşleşsin", "Kontrol edilsin", "Sonucu görün"],
    proofTitle: "Yalnızca cevabı değil, dayanağını da görün.",
    proofBody:
      "Hangi tanımların kullanıldığını, sorgunun hangi kontrollerden geçtiğini ve sonucun nasıl oluştuğunu tek yerde inceleyin.",
    pillarsTitle: "Güven, yalnızca doğru görünen bir cevaptan gelmez.",
    pillarsBody:
      "Her cevap; iş anlamını taşıyan model, sorgu güvenlik sınırları ve görünür bir çözüm izi üzerinde oluşur.",
    workflowTitle: "Sorudan rapora, görünür bir zincir.",
    workflow: [
      {
        title: "Veri kaynağını bağlayın",
        body: "Tablolar, ilişkiler ve kurumunuzun kullandığı iş tanımları birlikte hazırlanır.",
      },
      {
        title: "Sorunuzu yazın",
        body: "Tablo veya kolon adı bilmeden, ekibinizin kullandığı dille sorun.",
      },
      {
        title: "Kontroller tamamlansın",
        body: "Sorgu veri kaynağına gitmeden önce yalnızca okuma ve çalıştırma kontrollerinden geçer.",
      },
      {
        title: "Sonucu inceleyin",
        body: "Cevabı, grafiği ve kaynağını görün; yararlı analizi daha sonra yeniden kullanın.",
      },
    ],
    useCasesTitle: "Ekiplerin sorduğu gerçek sorular.",
    useCases: [
      { title: "Operasyon", question: "Bu hafta hedefinden en fazla sapan göstergeler hangileri?" },
      { title: "Finans", question: "Brüt kârı hedefin altında kalan ürün grupları hangileri?" },
      { title: "Finans", question: "Nakit dönüşüm süresi bu çeyrekte nasıl değişti?" },
      { title: "Satış", question: "Brüt kârı düşen müşteri ve ürün grupları hangileri?" },
      { title: "Stok", question: "Kritik seviyeye yaklaşan malzemeler hangileri?" },
      { title: "Yönetim", question: "Bu hafta hedeflerden en fazla sapan üç gösterge nedir?" },
    ],
    operationsTitle: "Operasyonun tamamını aynı iş diliyle anlayın.",
    operationsBody:
      "Finans, satış, stok, müşteri ve operasyon verilerini ortak tanımlar üzerinde sorgulayın; ekipler aynı metriğin farklı yorumlarıyla uğraşmasın.",
    trustTitle: "Cevabın nasıl korunduğunu görün.",
    trustBody:
      "Yalnızca okuma, çalıştırma öncesi kontrol, görünür sorgu ve yetkiye dayalı erişim birlikte çalışır.",
    integrationTitle: "Mevcut veri altyapınızın üzerinde çalışır.",
    integrationBody:
      "Bağlantı, şema keşfi, ortak iş tanımları ve kontroller; her veri kaynağının gerçek destek durumuyla birlikte gösterilir.",
    faqTitle: "Sık sorulanlar",
    faq: [
      {
        question: "dima yalnızca bir sohbet aracı mı?",
        answer:
          "Hayır. Sohbet arayüzü giriş noktasıdır; cevaplar modellenmiş iş bağlamı, kontrollü sorgu üretimi ve görünür raporlama akışı üzerinde oluşur.",
      },
      {
        question: "Oluşturulan sorgu nasıl kontrol ediliyor?",
        answer:
          "Yapay zekâ sorguyu önerir. Dima, sorgunun yalnızca izin verilen veriyi okuduğunu ve çalıştırılabilir olduğunu veri kaynağına göndermeden önce kontrol eder.",
      },
      {
        question: "Çalıştırma öncesi kontrol kesin doğruluk sağlar mı?",
        answer:
          "Hayır. Bu kontrol sorgunun güvenli ve çalıştırılabilir olup olmadığını sınar. İş tanımlarının ve kaynak verinin doğruluğu ayrıca kullanıcı tarafından değerlendirilir.",
      },
      {
        question: "Hangi veri kaynakları destekleniyor?",
        answer:
          "DuckDB örnek gösterimde, Postgres ise mevcut bağlantı kapsamında kullanılır. Diğer veri kaynakları Dima’da gerçek bağlantı testleri tamamlandıktan sonra desteklenmiş sayılır.",
      },
      {
        question: "Kurum içi kurulum kullanılabilir mi?",
        answer:
          "Kurum ağı içinde çalışan hibrit bağlantı yaklaşımı planlanmaktadır; bugün hazır bir özellik olarak sunulmamaktadır.",
      },
    ],
  },
  pages: {
    product: {
      eyebrow: "Ürün",
      title: "Bir iş sorusundan anlaşılır bir rapora.",
      description:
        "Sorunuzu günlük dille yazın. dima ilgili veriyi bulsun, kontrolleri tamamlasın ve sonucu inceleyebileceğiniz biçimde göstersin.",
      cta: "Ürünü kendi verinizle değerlendirin",
      sections: [
        { id: "ask", title: "İş dilinde sorun", body: "Tablo ve kolon adı ezberlemeden, kurumunuzun kullandığı ifadelerle sorun.", points: ["Takip soruları", "Konuşma bağlamı", "Doğal Türkçe deneyimi"] },
        { id: "model", title: "Herkes aynı tanımı kullansın", body: "Ölçüler, ilişkiler, birimler ve onaylanmış tanımlar ortak bir iş anlamında buluşur.", points: ["Ortak iş tanımları", "İlişkiler", "Anlaşılır adlar ve birimler"] },
        { id: "validate", title: "Çalıştırmadan önce kontrol edin", body: "Önerilen sorgu yalnızca izin verilen veriyi okuma ve çalıştırılabilirlik açısından kontrol edilir.", points: ["Yalnızca okuma", "Çalıştırma öncesi kontrol", "Görünür sorgu"] },
        { id: "explore", title: "Sonucu size uygun biçimde görün", body: "Aynı sonucu tablo, grafik, özet gösterge veya karşılaştırmalı görünümde inceleyin.", points: ["Tablo", "Grafik", "Özet göstergeler", "Karşılaştırma"] },
        { id: "verify", title: "Cevabı değerlendirin", body: "Geri bildirim ve cevap kaynağı, analizin nasıl oluştuğunu görünür tutar.", status: "beta" },
        { id: "reuse", title: "Yararlı cevabı yeniden kullanın", body: "Kaydedilen analizleri yeniden çalıştırma, zamanlama ve bildirim özellikleri kontrollü olarak geliştirilmektedir.", status: "beta" },
        { id: "govern", title: "Yetki sınırlarını koruyun", body: "Oturum, kurum kapsamı ve kullanıcı yetkileri hem ürün hem sunucu tarafında uygulanır." },
      ],
    },
    how: {
      eyebrow: "Nasıl çalışır?",
      title: "Yapay zekânın önerisini kontrol etmeden çalıştırmıyoruz.",
      description:
        "Soruyu anlamaktan sonucu göstermeye kadar her adım görünür ve denetlenebilir bir akışta ilerler.",
      cta: "Teknik bir görüşme planlayın",
      sections: [
        { id: "onboarding", title: "Veri kaynağını tanımlayın", body: "Bağlantı kurum kapsamında yönetilir; tablolar ve ilişkiler kontrollü biçimde keşfedilir." },
        { id: "semantics", title: "İş tanımlarını ekleyin", body: "Metrikler, zaman aralıkları, birimler ve kurumun kullandığı terimler ortak bir anlamda buluşur." },
        { id: "dry-plan", title: "Öneriyi kontrol edin", body: "Yapay zekânın önerdiği sorgu, yalnızca okuma ve çalıştırılabilirlik kontrollerinden geçmeden veri kaynağına ulaşmaz." },
        { id: "execute", title: "Sonucu ve kaynağını görün", body: "İzinli sorgu çalışır; sonuç, sorgu ve cevabın kaynağı aynı inceleme alanında sunulur." },
        { id: "planned", title: "Kurum içi hibrit bağlantı", body: "Müşteri ağından dışarı doğru güvenli bağlantı kuran yaklaşım planlanmaktadır; bugün hazır bir özellik değildir.", status: "planned" },
      ],
    },
    solutions: {
      eyebrow: "Çözümler",
      title: "Her ekip için aynı veri, aynı tanım, daha hızlı cevap.",
      description:
        "Dima, organizasyon şemasını değil karar verilmesi gereken gerçek sonuçları başlangıç noktası alır.",
      cta: "Öncelikli kullanım alanınızı konuşalım",
      sections: [
        { id: "executive", title: "Karar veren ekipler", body: "Hedeflerden sapan göstergeleri, sonucu oluşturan tanım ve ayrıntılarla birlikte görün.", points: ["Öncelikli sapmaları belirleyin", "Ayrıntıya inin"] },
        { id: "operations", title: "Operasyonel koordinasyon", body: "Hedef, gerçekleşen ve sapma nedenlerini ekip, süreç ve dönem bağlamında aynı iş diliyle sorgulayın.", points: ["Ortak metrik tanımları", "Takip sorularıyla derinleşme"] },
        { id: "data", title: "Kurumsal hafıza", body: "Tek seferlik rapor taleplerini azaltırken sorguyu, cevabın kaynağını ve yetki sınırlarını görünür tutun.", points: ["Yeniden kullanılabilir analizler", "Görünür cevap kaynağı"] },
      ],
    },
    security: {
      eyebrow: "Güvenlik",
      title: "Analitik hızlanırken erişim sınırları görünmez olmamalı.",
      description:
        "Mevcut güvenlik mimarisini doğrulanmış mekanizmalarla anlatıyor, sertifika veya mutlak güvenlik iddiası üretmiyoruz.",
      cta: "Güvenlik görüşmesi planlayın",
      sections: [
        { id: "read-only", title: "Yalnızca okuma", body: "Sorgular yalnızca izin verilen okuma biçimleriyle sınırlandırılır ve çalıştırılmadan önce kontrol edilir." },
        { id: "session", title: "Oturum güvenliği", body: "Kısa ömürlü erişim anahtarı tarayıcı belleğinde tutulur. Yenileme anahtarı tarayıcı kodunun erişemediği güvenli çerezde saklanır." },
        { id: "tenant", title: "Kurum ve yetki kapsamı", body: "Ekranda görünen işlemler sunucudan gelen yetkilere dayanır. Sunucu her isteği yeniden yetkilendirir." },
        { id: "audit", title: "İzlenebilirlik", body: "Sorgu, kimlik doğrulama ve yönetim eylemleri kurulum kapsamına göre kayıt altına alınabilir; ayrıntılar müşteri sözleşmesinde doğrulanır." },
        { id: "flow", title: "Veri akışı", body: "Kullanıcı isteği Dima üzerinden kontrollü sorguya dönüşür ve yalnızca izin verilen veri kaynağına ulaşır. Sunucu adresi tarayıcıya açılmaz." },
        { id: "deployment", title: "Kurulum seçenekleri", body: "Mevcut bulut kurulumu kullanılabilir. Kurum içi hibrit bağlantı yaklaşımı planlanmaktadır.", status: "planned" },
      ],
    },
    integrations: {
      eyebrow: "Entegrasyonlar",
      title: "Mevcut veri kaynaklarınızı değiştirmeden başlayın.",
      description:
        "Her bağlantının Dima’da doğrulanmış, teknik olarak mümkün veya planlanan durumunu açıkça gösteriyoruz.",
      cta: "Entegrasyon kapsamını değerlendirin",
      sections: [
        { id: "duckdb", title: "DuckDB örnek veri kaynağı", body: "Ürün akışını gerçek müşteri verisi kullanmadan gösteren örnek kaynaktır.", status: "available" },
        { id: "postgres", title: "Postgres", body: "Dima’nın mevcut bağlantı kapsamında kullandığı ve doğruladığı veri kaynağıdır.", status: "available" },
        { id: "engine", title: "MSSQL ve Oracle", body: "Altyapıda bağlantı imkânı vardır; Dima desteği gerçek bağlantı ve sorgu testleri tamamlandıktan sonra sunulur.", status: "planned" },
        { id: "process", title: "Kurulum akışı", body: "Bağlantı → tabloları keşfetme → iş tanımlarını ekleme → sorguyu kontrol etme → kullanıcı erişimi." },
        { id: "status", title: "Destek ne anlama gelir?", body: "Her kaynak “Dima’da doğrulandı”, “teknik olarak mümkün” veya “planlanıyor” olarak açıkça etiketlenir." },
      ],
    },
    about: {
      eyebrow: "Hakkımızda",
      title: "İşletme verisini daha anlaşılır ve denetlenebilir kılmak için.",
      description:
        "dima, UpcyTech Teknoloji Anonim Şirketi tarafından geliştirilen güvenilir konuşmalı analitik ürünüdür.",
      cta: "Bizimle iletişime geçin",
      sections: [
        { id: "purpose", title: "Neden dima?", body: "İş ekiplerinin cevap beklemesini azaltırken veri ekiplerinin ihtiyaç duyduğu kontrolü korumak için." },
        { id: "principles", title: "Dört ürün ilkesi", body: "Bu ilkeler yapay zekâ ile denetimi, iş dilini, ortak tanımları ve yeniden kullanılabilir çalışmaları bir araya getirir.", points: ["Yapay zekâ önerir; sistem kontrol eder", "İş dilinde erişim", "Onaylı iş tanımları", "Yeniden kullanılabilir analizler"] },
        { id: "company", title: "UpcyTech", body: "UpcyTech, ekiplerin karmaşık iş akışlarını daha anlaşılır ve yönetilebilir kılan yazılım ürünleri geliştirir. Dima bu ürün ekosisteminin analitik katmanıdır." },
        { id: "truth", title: "Kanıtı iddianın önüne koyuyoruz", body: "Sahte istatistik, sertifika, müşteri logosu veya doğrulanmamış gelecek planı kullanmıyoruz." },
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
        { id: "categories", title: "3. İşlenen veri kategorileri", body: "Kimlik ve iletişim verileri; şirket/rol bilgisi; hesap ve kurum tanımlayıcıları; oturum, IP, cihaz ve güvenlik kayıtları; destek/demo mesajları; ürün içinde kullanıcının yazdığı sorular, oluşturulan SQL, rapor üst verileri, doğrulama ve denetim kayıtları. Özel nitelikli veri talep etmiyoruz; serbest metin alanlarına bu tür veri girilmemelidir." },
        { id: "purposes", title: "4. Amaçlar ve hukuki sebepler", body: "Demo ve iletişim talepleri talep üzerine iletişim kurmak ve meşru B2B ilişki yönetimi için; hesap ve ürün verileri sözleşmenin kurulması/ifası için; güvenlik ve denetim kayıtları hukuki yükümlülükler ile temel haklara zarar vermeyen meşru menfaat için; açık rızaya dayanan ayrı bir pazarlama faaliyeti varsa yalnız ilgili rıza kapsamında işlenir." },
        { id: "collection", title: "5. Toplama yöntemi", body: "Veriler formlar, hesap ve oturum işlemleri, ürün kullanımı, same-origin API trafiği, destek iletişimi ve güvenlik logları üzerinden tamamen veya kısmen otomatik yöntemlerle elde edilir." },
        { id: "sharing", title: "6. Alıcı grupları", body: "Veriler; barındırma ve altyapı sağlayıcıları, e-posta teslim hizmeti, sözleşmeyle bağlı teknik hizmet sağlayıcılar, yetkili kamu kurumları ve hukuki yükümlülük halinde danışmanlarla yalnız gerekli kapsamda paylaşılabilir. Reklam veri brokerlarına satılmaz." },
        { id: "transfer", title: "7. Yurt dışı aktarım", body: "Vercel ve Resend gibi hizmetlerin kullanıldığı kurulumlarda hesap dışı teknik veriler ve iletişim formu verileri yurt dışında işlenebilir. Aktarım, KVKK m.9’daki yeterlilik, uygun güvence/standart sözleşme veya kanundaki istisnai aktarım şartlarından uygulanabilir olana dayanır. Resend üzerinden gönderim başlamadan önce uygun mekanizma ve Kurul bildirimi doğrulanır." },
        { id: "retention", title: "8. Saklama ve silme", body: "Demo/iletişim verileri son anlamlı etkileşimden itibaren 12 ay saklanır. Hesap, sözleşme ve müşteri verileri sözleşme süresince ve uygulanabilir yasal zamanaşımı/saklama sürelerince; güvenlik kayıtları risk ve mevzuatla orantılı süre boyunca tutulur. Süre dolunca veri silinir, yok edilir veya anonimleştirilir." },
        { id: "cookies", title: "9. Çerezler ve yerel depolama", body: "Tarayıcı kodunun erişemediği güvenli oturum çerezi kimlik doğrulama için, dima_locale çerezi dil tercihi için gereklidir. Tema tercihi tarayıcının yerel depolama alanında tutulabilir. Pazarlama analitiği bağlantısı başlangıçta devre dışıdır; analitik veya reklam çerezi yerleştirmez." },
        { id: "security", title: "10. Güvenlik", body: "Aynı kaynak üzerinden çalışan API geçidi, bellekte tutulan erişim anahtarı, güvenli yenileme çerezi, yetki kontrolleri, kurum kapsamı, güvenlik başlıkları ve denetim kayıtları gibi teknik/idari tedbirler uygulanır. Hiçbir internet iletimi veya depolama yöntemi mutlak güvenlik garantisi vermez." },
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
        { id: "service", title: "2. Hizmet", body: "dima; doğal dil sorularını modellenmiş iş tanımları üzerinden sorgu ve rapor akışına dönüştüren B2B SaaS analitik hizmetidir. Kapsam, kurum yapılandırması, lisanslanan modüller, özellik ayarları ve sipariş formuna göre değişebilir." },
        { id: "account", title: "3. Hesap ve güvenlik", body: "Kullanıcı doğru bilgi sağlamalı, kimlik bilgilerini paylaşmamalı, MFA ve güvenlik kontrollerini devre dışı bırakmamalı ve şüpheli erişimi gecikmeden bildirmelidir. Müşteri kullanıcı yetkilerini ve işten ayrılan kullanıcıların erişimini yönetmekten sorumludur." },
        { id: "license", title: "4. Sınırlı kullanım hakkı", body: "UpcyTech, sözleşme süresince müşteriye kendi iç iş amaçları için devredilemez, münhasır olmayan ve sınırlı bir kullanım hakkı verir. Hizmet satılmaz; fikri mülkiyet hakları UpcyTech ve lisans verenlerinde kalır." },
        { id: "acceptable", title: "5. Kabul edilebilir kullanım", body: "Hizmet hukuka aykırı faaliyet, yetkisiz erişim, güvenlik testi, tersine mühendislik, kaynak kod çıkarma, zararlı yazılım, aşırı otomatik yük, üçüncü kişi hak ihlali veya izin verilmeyen kişisel veri işleme için kullanılamaz. Güvenliği veya diğer kurum hesaplarını etkileyen kullanım askıya alınabilir." },
        { id: "customer-data", title: "6. Müşteri verisi", body: "Müşteri kendi verisinin ve talimatlarının hukuka uygunluğundan, gerekli aydınlatma/izinlerden ve veri kaynağı erişim yetkisinden sorumludur. UpcyTech müşteri verisini hizmeti sunmak, güvenliğini sağlamak ve belgelenmiş talimatları yerine getirmek için işler; veri üzerindeki hak müşteride kalır." },
        { id: "ai", title: "7. Yapay zekâ ve analitik çıktılar", body: "Yapay zekâ modeli sorgu veya yorum önerebilir; Dima güvenlik ve çalıştırma öncesi kontroller uygular. Bu kontroller iş tanımlarının, kaynak verinin veya sonucun mutlak doğruluğunu garanti etmez. Çıktılar profesyonel, hukuki, mali veya güvenlik kararlarında insan incelemesi olmadan tek dayanak yapılmamalıdır." },
        { id: "beta", title: "8. Beta ve planlanan özellikler", body: "Beta özellikler değişebilir, sınırlı desteklenebilir veya kaldırılabilir. Planlanan özellikler taahhüt edilmiş teslim tarihi oluşturmaz. Kayıtlı sorgu tanımları, doğrulama, zamanlama ve bildirim kapsamı kurum özellikleri ve sözleşmeyle belirlenir." },
        { id: "fees", title: "9. Ücret, vergi ve yenileme", body: "Ücretler, para birimi, ödeme takvimi, vergi, kullanım limitleri ve yenileme koşulları sipariş formu veya teklifte belirtilir. Public web sitesinde fiyat yayımlanmaması ücretsiz hizmet anlamına gelmez. Geciken tutarlar uygulanabilir hukuk ve sözleşme sınırlarında erişim kısıtına yol açabilir." },
        { id: "availability", title: "10. Değişiklik ve erişilebilirlik", body: "UpcyTech güvenlik, performans ve ürün gelişimi için hizmeti güncelleyebilir. Belirli uptime, destek süresi, bakım penceresi veya servis kredisi yalnız imzalı SLA veya sipariş formunda yazıyorsa geçerlidir." },
        { id: "confidentiality", title: "11. Gizlilik", body: "Taraflar hizmet ilişkisi içinde öğrendikleri kamuya açık olmayan teknik, ticari ve müşteri bilgilerini yalnız sözleşme amacıyla kullanır ve makul koruma tedbirleri uygular. Kanunen zorunlu açıklamalar mümkünse önceden bildirilir." },
        { id: "ip", title: "12. Fikri mülkiyet ve geri bildirim", body: "Dima yazılımı, modelleri, arayüzü, dokümantasyonu ve türevleri UpcyTech’e veya lisans verenlerine aittir. Müşteri verisi müşteriye aittir. Kullanıcı geri bildirimi gizli bilgi içermemek kaydıyla ürün geliştirmede bedelsiz kullanılabilir." },
        { id: "third-party", title: "13. Üçüncü taraf hizmetleri", body: "Veri kaynağı, yapay zekâ sağlayıcısı, barındırma veya e-posta teslimi gibi üçüncü taraflar kendi şartlarına tabi olabilir. UpcyTech seçtiği alt işleyenleri veri koruma yükümlülükleriyle bağlar; müşterinin bağımsız seçtiği entegrasyonlardan müşteri sorumludur." },
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
      "Analytics that makes it easier to ask questions, understand answers, and see what supports them.",
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
    available: "Verified in Dima",
    beta: "Beta",
    planned: "Planned",
    finalTitle: "Let’s begin with your first real business question.",
    finalBody: "We can assess your data model and highest-priority reporting need together.",
    demo: "Request a demo",
    login: "Sign in",
  },
  home: {
    eyebrow: "A clearer way to understand business data",
    title: "Ask your data. Then",
    rotateWords: ["understand it.", "compare it.", "share it."],
    description:
      "Ask in everyday business language. dima finds the relevant data, shows the result as a table or chart, and explains where the answer came from.",
    process: ["Write a question", "Match business definitions", "Run checks", "See the result"],
    proofTitle: "See the answer and what supports it.",
    proofBody:
      "Review the definitions used, the checks completed, and the steps that produced the result in one place.",
    pillarsTitle: "Trust takes more than an answer that looks right.",
    pillarsBody:
      "Every answer is grounded in shared business definitions, clear access boundaries, and a visible source.",
    workflowTitle: "A visible chain from question to report.",
    workflow: [
      { title: "Connect your data", body: "Prepare tables, relationships, and the business definitions your organization uses." },
      { title: "Write your question", body: "Ask in familiar language without knowing table or column names." },
      { title: "Complete the checks", body: "The query is checked for read-only access and execution before it reaches the data source." },
      { title: "Review the result", body: "See the answer, chart, and source; save useful analysis for later." },
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
    trustTitle: "See how every answer is protected.",
    trustBody:
      "Read-only access, pre-execution checks, visible queries, and permission-based access work together.",
    integrationTitle: "Built over your existing data infrastructure.",
    integrationBody:
      "Connections, schema discovery, shared business definitions, and checks are shown with the real support status of each source.",
    faqTitle: "Frequently asked questions",
    faq: [
      { question: "Is dima only a chat tool?", answer: "No. Chat is the starting point; dima connects each answer to shared business definitions, controlled queries, and a visible report." },
      { question: "How is a generated query checked?", answer: "AI may propose the query. Dima verifies that it only reads permitted data and can run safely before sending it to the data source." },
      { question: "Do pre-execution checks guarantee accuracy?", answer: "No. They confirm that a query is safe and executable. Business definitions and source data still require human ownership." },
      { question: "Which data sources are supported?", answer: "DuckDB powers the sample experience and Postgres is supported in the current connection scope. Other sources require live Dima validation." },
      { question: "Is an on-premises setup available?", answer: "A hybrid connection that runs inside the customer network is planned; it is not currently offered as a ready feature." },
    ],
  },
  pages: {
    product: {
      eyebrow: "Product",
      title: "From a business question to a clear report.",
      description: "Write the question in everyday language. dima finds the relevant data, completes its checks, and presents a result you can inspect.",
      cta: "Evaluate dima with your own data",
      sections: [
        { id: "ask", title: "Ask in business language", body: "Use the terms your organization knows without memorizing tables or columns.", points: ["Follow-up questions", "Conversation context", "Natural English experience"] },
        { id: "model", title: "Give everyone the same definitions", body: "Measures, relationships, units, and approved definitions meet in one shared business model.", points: ["Shared definitions", "Relationships", "Clear labels and units"] },
        { id: "validate", title: "Check before execution", body: "The proposed query is checked for permitted read access and execution.", points: ["Read-only access", "Pre-execution check", "Visible query"] },
        { id: "explore", title: "Review the result your way", body: "Inspect the same result as a table, chart, summary metric, or comparison.", points: ["Table", "Chart", "Summary metrics", "Comparison"] },
        { id: "verify", title: "Review the answer", body: "Feedback and answer sources keep the analytical path visible.", status: "beta" },
        { id: "reuse", title: "Reuse helpful answers", body: "Replay, scheduling, and notification capabilities are being developed under controlled feature status.", status: "beta" },
        { id: "govern", title: "Preserve access boundaries", body: "Sessions, organization scope, and user permissions are enforced by both the product and server." },
      ],
    },
    how: {
      eyebrow: "How it works",
      title: "We never run an AI suggestion without checking it.",
      description: "Every step—from understanding the question to showing the result—remains visible and reviewable.",
      cta: "Schedule a technical conversation",
      sections: [
        { id: "onboarding", title: "Define the data source", body: "The connection is managed within the organization scope while tables and relationships are discovered safely." },
        { id: "semantics", title: "Add business definitions", body: "Metrics, time periods, units, and approved terms come together in one shared meaning." },
        { id: "dry-plan", title: "Check the proposal", body: "An AI-proposed query cannot reach the data source before read-only and execution checks pass." },
        { id: "execute", title: "Show the result and its source", body: "The permitted query runs; the result, query, and answer source appear in one review surface." },
        { id: "planned", title: "Hybrid on-premises connection", body: "An outbound-only connection from the customer network is planned; it is not a current production feature.", status: "planned" },
      ],
    },
    solutions: {
      eyebrow: "Solutions",
      title: "The same data and definitions, with faster answers for every team.",
      description: "Dima starts with the outcome that needs a decision—not only the org chart.",
      cta: "Discuss your priority use case",
      sections: [
        { id: "executive", title: "Decision-making teams", body: "See performance gaps and exceptions together with the definitions and details that produced them.", points: ["Identify priority gaps", "Explore the details"] },
        { id: "operations", title: "Operational coordination", body: "Query targets, actuals, and drivers across teams, processes, and periods in one business language.", points: ["Shared metric definitions", "Deeper follow-up questions"] },
        { id: "data", title: "Institutional memory", body: "Reduce one-off report requests while keeping queries, answer sources, and permission boundaries visible.", points: ["Reusable analysis", "Visible answer source"] },
      ],
    },
    security: {
      eyebrow: "Security",
      title: "Access boundaries should not disappear as analytics gets faster.",
      description: "We describe verified mechanisms—not certifications or absolute security claims.",
      cta: "Schedule a security review",
      sections: [
        { id: "read-only", title: "Read-only access", body: "Queries are limited to permitted read operations and checked before execution." },
        { id: "session", title: "Session security", body: "Short-lived access tokens stay in memory. Refresh tokens use secure cookies that browser scripts cannot read." },
        { id: "tenant", title: "Organization and permission scope", body: "The interface follows permissions from the server, and the server authorizes every request again." },
        { id: "audit", title: "Activity records", body: "Query, authentication, and management actions can be recorded according to the agreed deployment scope." },
        { id: "flow", title: "Data flow", body: "A user request becomes a controlled query through Dima and reaches only the permitted customer data source." },
        { id: "deployment", title: "Setup options", body: "The current cloud setup is available. A hybrid on-premises connection remains planned.", status: "planned" },
      ],
    },
    integrations: {
      eyebrow: "Integrations",
      title: "Start without replacing your existing data sources.",
      description: "Every connection is clearly marked as verified in Dima, technically possible, or planned.",
      cta: "Assess your integration scope",
      sections: [
        { id: "duckdb", title: "DuckDB demo model", body: "A synthetic source that demonstrates the product flow without real customer data.", status: "available" },
        { id: "postgres", title: "Postgres", body: "A data source used in Dima connection configuration and supported in the current scope.", status: "available" },
        { id: "engine", title: "MSSQL and Oracle", body: "The underlying engine can connect to these sources. Dima support follows live connection and query testing.", status: "planned" },
        { id: "process", title: "Setup flow", body: "Connection → table discovery → business definitions → query checks → user access." },
        { id: "status", title: "What support means", body: "Each source is labeled “Verified in Dima,” “Engine capable,” or “Planned.”" },
      ],
    },
    about: {
      eyebrow: "About",
      title: "Making business data easier to understand and audit.",
      description: "dima is a trusted conversational analytics product built by UpcyTech Teknoloji Anonim Şirketi.",
      cta: "Contact us",
      sections: [
        { id: "purpose", title: "Why dima?", body: "To help business teams get answers sooner while preserving the control data teams need." },
        { id: "principles", title: "Four product principles", body: "These principles bring together AI with checks, business language, shared definitions, and reusable work.", points: ["AI proposes; the system checks", "Business-language access", "Approved business definitions", "Reusable analysis"] },
        { id: "company", title: "UpcyTech", body: "UpcyTech builds software that makes complex business workflows easier for teams to understand and manage. Dima is the analytics layer of this product ecosystem." },
        { id: "truth", title: "Evidence before claims", body: "We do not use fabricated statistics, certifications, customer logos, or unverified future plans." },
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
