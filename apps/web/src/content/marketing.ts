export type MarketingLocale = "tr" | "en";
export type CapabilityStatus = "available" | "pilot" | "planned";
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
    textile: string;
    rights: string;
  };
  common: {
    learnMore: string;
    available: string;
    pilot: string;
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
    reasonsTitle: string;
    reasons: Array<{ title: string; body: string }>;
    textileTitle: string;
    textileBody: string;
    useCasesTitle: string;
    useCasesBody: string;
    useCases: Array<{ title: string; question: string }>;
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
    textile: "Boyahane çözümü",
    rights: "Tüm hakları saklıdır.",
  },
  common: {
    learnMore: "İncele",
    available: "Dima’da doğrulandı",
    pilot: "Pilot kapsamı",
    planned: "Planlanıyor",
    finalTitle: "İlk sorunuzla başlayalım.",
    finalBody:
      "Veri kaynağınızı ve karar vermek istediğiniz ilk soruyu birlikte netleştirelim.",
    demo: "Demo talep et",
    login: "Giriş yap",
  },
  home: {
    eyebrow: "Güvenilir konuşmalı analitik",
    title: "İşletme verinizle konuşun.",
    description:
      "Günlük dille sorun; dima soruyu iş tanımlarınızla eşleştirir, sorguyu çalıştırmadan önce kontrol eder ve sonucu dayanağıyla gösterir.",
    process: ["Sorunuzu yazın", "İş anlamını eşleştirin", "Çalıştırmadan önce kontrol edin", "Cevabı kaynağıyla görün"],
    proofTitle: "Cevabın içini görün.",
    proofBody:
      "Soru, iş tanımı, sorgu kontrolü ve sonuç aynı inceleme yüzeyinde. Cevabın nereden geldiğini ekibinizle birlikte değerlendirin.",
    reasonsTitle: "Güven, görünür bir çalışma biçimidir.",
    reasons: [
      { title: "İş dilinden başlar", body: "Tablo ve kolon adı bilmeden sorun; kurumunuzun kullandığı terimler bağlama girer." },
      { title: "Kontrol edilerek ilerler", body: "Yapay zekâ önerir; yalnızca izinli okuma ve çalıştırılabilirlik kontrollerinden geçen sorgu ilerler." },
      { title: "Kaynağıyla teslim edilir", body: "Sonucu, sorguyu ve kullanılan tanımları birlikte inceleyin." },
    ],
    textileTitle: "Boyahane verisinden karara.",
    textileBody: "Parti, makine, reçete ve termin sorularını tek bir üretim bağlamında görün. Örnek anlatı anonim verilerle hazırlanmıştır.",
    useCasesTitle: "İlk soruyu nerede sorarsınız?",
    useCasesBody: "Operasyon, üretim, finans ve yönetim için başlangıç soruları.",
    useCases: [
      { title: "Operasyon", question: "Bu hafta hedefinden en çok sapan adım hangisi?" },
      { title: "Üretim", question: "Hangi makineyi önce incelemeliyiz?" },
      { title: "Finans", question: "Hangi ürün grubu hedef marjın altında kaldı?" },
      { title: "Stok", question: "Hangi malzeme kritik seviyeye yaklaşıyor?" },
      { title: "Yönetim", question: "Bu hafta hangi üç sapma karar bekliyor?" },
    ],
    trustTitle: "Kontrol, yetki ve kaynak aynı akışta.",
    trustBody:
      "Yalnızca okuma sınırı, çalıştırma öncesi kontrolü, sunucu yetkisi ve görünür kaynak birlikte çalışır.",
    integrationTitle: "Mevcut veri kaynaklarınızla başlayın.",
    integrationBody:
      "DuckDB örnek akışta, Postgres mevcut bağlantı kapsamında. Diğer kaynaklar test edilmeden desteklenmiş sayılmaz.",
    faqTitle: "Sık sorulanlar",
    faq: [
      {
        question: "dima yalnızca bir sohbet aracı mı?",
        answer:
          "Hayır. Sohbet başlangıçtır; cevaplar iş tanımları, kontrollü sorgu ve görünür rapor akışıyla oluşur.",
      },
      {
        question: "Sorgu nasıl kontrol ediliyor?",
        answer:
          "Yapay zekâ sorguyu önerir. dima, izinli veriyi okuduğunu ve çalıştırılabilir olduğunu kaynağa göndermeden önce kontrol eder.",
      },
      {
        question: "Bu kontrol neyi garanti etmez?",
        answer:
          "İş tanımlarının, kaynak verinin veya yorumun doğruluğunu tek başına kanıtlamaz; insan değerlendirmesi gerekir.",
      },
      {
        question: "Hangi veri kaynakları destekleniyor?",
        answer:
          "DuckDB örnek akışta, Postgres mevcut bağlantı kapsamında kullanılır. Diğer kaynaklar canlı testten sonra desteklenmiş sayılır.",
      },
    ],
  },
  pages: {
    product: {
      eyebrow: "Ürün",
      title: "İş sorusundan cevaba.",
      description:
        "Sorunuzu günlük dille yazın; dima ilgili veriyi bulur, sorguyu kontrol eder ve sonucu dayanağıyla gösterir.",
      cta: "Kendi sorunuzla başlayın",
      sections: [
        { id: "ask", title: "İş dilinde sorun", body: "Tablo veya kolon adı ezberlemeden, ekibinizin kullandığı ifadelerle başlayın.", points: ["Takip soruları", "Konuşma bağlamı"] },
        { id: "model", title: "Tanımlar ortak olsun", body: "Ölçüler, ilişkiler ve birimler herkesin aynı anlamda kullandığı bir modelde buluşur.", points: ["Ortak iş tanımları", "İlişkiler", "Birimler"] },
        { id: "validate", title: "Çalıştırmadan önce kontrol edin", body: "Önerilen sorgu, izinli okuma ve çalıştırılabilirlik açısından kaynağa gitmeden önce kontrol edilir.", points: ["Yalnızca okuma", "Görünür sorgu"] },
        { id: "explore", title: "Cevabı istediğiniz görünümde inceleyin", body: "Sonucu tablo, grafik veya karşılaştırma olarak görün; soruyu ayrıntıya indirerek takip edin.", points: ["Tablo", "Grafik", "Karşılaştırma"] },
        { id: "govern", title: "Yetki sınırlarını koruyun", body: "Oturum, kurum kapsamı ve kullanıcı yetkileri sunucuda yeniden değerlendirilir.", points: ["Oturum", "Kurum kapsamı", "Kullanıcı yetkisi"] },
        { id: "reuse", title: "Yararlı analizi yeniden kullanın", body: "Kaydetme, yeniden çalıştırma ve zamanlama akışları kontrollü biçimde geliştirilmektedir.", status: "pilot" },
      ],
    },
    how: {
      eyebrow: "Nasıl çalışır?",
      title: "Cevap gelmeden önce neyin kontrol edildiğini görün.",
      description:
        "Soru, iş anlamı, sorgu, yetki ve kaynak tek görünür akışta ilerler.",
      cta: "Teknik kapsamı birlikte inceleyin",
      sections: [
        { id: "problem", title: "Ham metin tek başına yetmez", body: "Çalışan bir sorgu, doğru metriğin veya doğru yetki sınırının seçildiğini tek başına göstermez.", visual: { key: "question", caption: "Soru ve anlam ayrımı" } },
        { id: "semantics", title: "İş tanımlarını ortaklaştırın", body: "Metrikler, zaman aralıkları, birimler ve kurum terimleri aynı iş anlamında buluşur.", visual: { key: "definitions", caption: "Modellenmiş bağlam" } },
        { id: "interpretation", title: "Soruyu bağlama taşıyın", body: "Ölçü, ayrıntı, zaman ve ilişki seçimleri görünür hale gelir; belirsizlik saklanmaz." },
        { id: "guard", title: "Sorguyu çalıştırmadan önce sınayın", body: "Yapay zekâ önerisi yalnızca izinli okuma biçimleri ve çalıştırılabilirlik açısından kontrol edilir.", visual: { key: "checks", caption: "Sorgu kontrolleri" } },
        { id: "permissions", title: "Yetkiyi her istekte doğrulayın", body: "Sunucu; oturum, kurum ve kullanıcı kapsamını arayüzden bağımsız olarak yeniden değerlendirir.", visual: { key: "access", caption: "Yetki sınırları" } },
        { id: "answer", title: "Sonucu, sorguyu ve kaynağı birlikte görün", body: "Kontrol, cevabın güvenli ve çalıştırılabilir akışını destekler; iş tanımı ve kaynak doğruluğu için insan değerlendirmesi yine gerekir.", visual: { key: "source", caption: "Cevap kaynağı" } },
      ],
    },
    solutions: {
      eyebrow: "Çözümler",
      title: "Her ekip, kendi sorusuyla başlar.",
      description:
        "Operasyon, üretim, finans, satış, stok ve yönetim sorularını ortak iş tanımlarıyla inceleyin.",
      cta: "Öncelikli soruyu konuşalım",
      sections: [
        { id: "operations", title: "Bu hafta hangi operasyon adımı saptı?", body: "Hedefi, gerçekleşeni ve sapma nedenini aynı dönem ve süreç bağlamında inceleyin.", points: ["Hedef ve gerçekleşen", "Takip soruları"] },
        { id: "production", title: "Hangi makineyi önce incelemeliyiz?", body: "Makine, vardiya, parti, OEE ve fire sinyallerini tek soruda karşılaştırın.", points: ["OEE ve fire", "Parti ve vardiya"] },
        { id: "finance", title: "Hangi ürün grubu hedef marjın altında?", body: "Gelir, maliyet ve dönem tanımlarını ortak bir finans görünümünde izleyin.", points: ["Gelir ve maliyet", "Sonuçtan ayrıntıya"] },
        { id: "sales", title: "Hangi müşteri veya ürün grubu riskte?", body: "Müşteri, sipariş ve ürün bağlamını birleştirerek değişen ticari sinyalleri görün.", points: ["Müşteri ve sipariş", "Karşılaştırma"] },
        { id: "inventory", title: "Hangi malzeme kritik seviyeye yaklaşıyor?", body: "Malzeme, hareket, rezervasyon ve ihtiyaç dönemini birlikte takip edin.", points: ["Kritik stok", "İhtiyaç ve hareket"] },
        { id: "executive", title: "Bu hafta hangi üç sapma karar bekliyor?", body: "Öncelikli göstergeleri, onları oluşturan tanım ve ayrıntılarla birlikte görün.", points: ["Önceliklendirme", "Ayrıntıya inme"] },
      ],
    },
    textile: {
      eyebrow: "Boyahane çözümü",
      title: "Boyahane verisini üretim kararına bağlayın.",
      description: "Parti, reçete, makine, kalite, kaynak tüketimi ve sevkiyat riskini tek bağlamda inceleyen anonim örnek anlatı.",
      cta: "Boyahane sorusunu konuşalım",
      sections: [
        { id: "question", title: "Bugün hangi parti risk taşıyor?", body: "Parti, sipariş, makine ve kalite sapmasını birlikte sorarak incelemeye nereden başlayacağınızı görün.", points: ["Parti ve sipariş", "Renk sapması"], visual: { key: "question", caption: "Parti ve kalite sorusu" } },
        { id: "production", title: "Hangi makine OEE ve fireyi etkiliyor?", body: "Makine, vardiya ve üretim kaydı boyunca OEE, fire ve duruşu karşılaştırın.", points: ["OEE ve fire", "Makine ve vardiya"], visual: { key: "coordination", caption: "Üretim göstergeleri" } },
        { id: "recipe", title: "Reçete ve kaynak tüketimi nasıl açıklanıyor?", body: "Reçete, kimyasal, su ve enerji kullanımını aynı soru zincirinde görün.", points: ["Reçete ve kimyasal", "Su ve enerji"], visual: { key: "definitions", caption: "Reçete ve kaynak tanımları" } },
        { id: "quality", title: "Kalite sapması hangi koşullarla birlikte görülüyor?", body: "Kalite sonucu, proses koşulları ve parti ayrıntısını görünür tanımlarla karşılaştırın.", points: ["Kalite sapması", "İncelenebilir kaynak"], visual: { key: "checks", caption: "Kalite kontrol zinciri" } },
        { id: "orders", title: "Hangi siparişin termin riski artıyor?", body: "Sipariş tarihi, üretim ilerlemesi ve sevkiyat durumunu karar verilmesi gereken risk etrafında inceleyin.", points: ["Termin görünümü", "Sevkiyat riski"], visual: { key: "priority", caption: "Sipariş ve termin önceliği" } },
        { id: "integration", title: "Örnek anlatı gerçek kapsama nasıl taşınır?", body: "Kaynak erişimi, tablo keşfi, iş tanımları ve yetki sınırları doğrulanmadan müşteri kurulumu iddia edilmez.", points: ["Anonim örnek terimler", "Pilot değerlendirme"], status: "pilot", visual: { key: "connection", caption: "Bağlantı ve modelleme akışı" } },
      ],
    },
    security: {
      eyebrow: "Güvenlik",
      title: "Hızlı cevap, görünmez yetki demek değildir.",
      description:
        "Doğrulanmış mekanizmaları açıkça anlatıyoruz; sertifika veya mutlak güvenlik iddiası üretmiyoruz.",
      cta: "Güvenlik kapsamını konuşalım",
      sections: [
        { id: "read-only", title: "Yalnızca okuma", body: "Sorgular izin verilen okuma biçimleriyle sınırlandırılır ve çalıştırılmadan önce kontrol edilir." },
        { id: "session", title: "Oturum güvenliği", body: "Kısa ömürlü erişim anahtarı bellekte, yenileme anahtarı tarayıcı koduna kapalı güvenli çerezde tutulur." },
        { id: "tenant", title: "Kurum ve yetki kapsamı", body: "Sunucu, her istekte oturum, kurum ve kullanıcı yetkisini yeniden doğrular." },
        { id: "audit", title: "İzlenebilirlik", body: "Sorgu, kimlik doğrulama ve yönetim eylemleri kurulum kapsamına göre kayıt altına alınabilir." },
        { id: "deployment", title: "Kurulum seçenekleri", body: "Mevcut bulut kurulumu kullanılabilir. Kurum içi hibrit bağlantı yaklaşımı planlanmaktadır.", status: "planned", visual: { key: "deployment", caption: "Kurulum ve veri akışı" } },
      ],
    },
    integrations: {
      eyebrow: "Entegrasyonlar",
      title: "Mevcut veri kaynaklarınızla başlayın.",
      description:
        "Kaynak durumunu açıkça ayırıyoruz: Dima’da doğrulandı, teknik olarak mümkün veya planlanıyor.",
      cta: "Bağlantı kapsamını değerlendirin",
      sections: [
        { id: "duckdb", title: "DuckDB örnek kaynağı", body: "Ürün akışını gerçek müşteri verisi olmadan gösteren anonim örnek kaynaktır.", status: "available" },
        { id: "postgres", title: "Postgres", body: "Mevcut bağlantı kapsamında kullanılan ve doğrulanan veri kaynağıdır.", status: "available" },
        { id: "engine", title: "MSSQL ve Oracle", body: "Teknik bağlantı imkânı vardır; Dima desteği canlı bağlantı ve sorgu testinden sonra sunulur.", status: "planned" },
        { id: "process", title: "Kurulum akışı", body: "Bağlantı → tablo keşfi → iş tanımları → sorgu kontrolü → kullanıcı erişimi.", visual: { key: "connection", caption: "Bağlantı ve modelleme akışı" } },
        { id: "status", title: "Destek ne anlama gelir?", body: "Her kaynak gerçek doğrulama durumuyla etiketlenir; teknik imkân, ürün desteği yerine geçmez." },
      ],
    },
    about: {
      eyebrow: "Hakkımızda",
      title: "İşletme verisini daha anlaşılır kılmak için.",
      description:
        "dima, UpcyTech Teknoloji Anonim Şirketi tarafından geliştirilen konuşmalı analitik ürünüdür.",
      cta: "Ekiple tanışın",
      sections: [
        { id: "purpose", title: "Neden dima?", body: "İş ekiplerinin cevaba daha hızlı ulaşmasını, veri ekiplerinin kontrolü korumasını istiyoruz." },
        { id: "principles", title: "Nasıl çalışıyoruz?", body: "İş dili, ortak tanım ve kontrolü tek analitik akışta buluşturuyoruz.", points: ["Yapay zekâ önerir; sistem kontrol eder", "İş tanımları ortak kalır", "Kaynak ve sonuç birlikte görünür"] },
        { id: "truth", title: "Kanıtı iddianın önüne koyuyoruz", body: "Sahte istatistik, sertifika, müşteri logosu veya doğrulanmamış gelecek planı kullanmıyoruz.", visual: { key: "truth", caption: "Kanıt ve sınırların birlikte görünümü" } },
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
        { id: "pilot", title: "8. Pilot ve planlanan özellikler", body: "Pilot kapsamındaki özellikler değişebilir, sınırlı desteklenebilir veya kaldırılabilir. Planlanan özellikler taahhüt edilmiş teslim tarihi oluşturmaz. Kayıtlı sorgu tanımları, doğrulama, zamanlama ve bildirim kapsamı kurum özellikleri ve sözleşmeyle belirlenir." },
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
    textile: "Textile dyehouse",
    rights: "All rights reserved.",
  },
  common: {
    learnMore: "Explore",
    available: "Verified in Dima",
    pilot: "Pilot scope",
    planned: "Planned",
    finalTitle: "Let’s begin with your first question.",
    finalBody: "We can clarify your data source and the first decision you need to support.",
    demo: "Request a demo",
    login: "Sign in",
  },
  home: {
    eyebrow: "Trustworthy conversational analytics",
    title: "Talk to your business data.",
    description:
      "Ask in everyday language; dima matches the question to your business definitions, checks the query before execution, and shows the result with its source.",
    process: ["Write a question", "Match business meaning", "Check before execution", "See the source"],
    proofTitle: "See inside the answer.",
    proofBody:
      "The question, business definition, query check, and result stay in one review surface so your team can assess where the answer came from.",
    reasonsTitle: "Trust is a visible way of working.",
    reasons: [
      { title: "Start in business language", body: "Ask without table or column names; your organization’s terms become part of the context." },
      { title: "Move through checks", body: "AI proposes; only a query that passes permitted-read and executable-plan checks moves forward." },
      { title: "Deliver the source", body: "Review the result, query, and definitions that support it together." },
    ],
    textileTitle: "From dyehouse data to decisions.",
    textileBody: "See batch, machine, recipe, and deadline questions in one production context. The narrative uses anonymized example data.",
    useCasesTitle: "Where would you start?",
    useCasesBody: "Starting questions for operations, production, finance, and leadership.",
    useCases: [
      { title: "Operations", question: "Which step moved furthest from target this week?" },
      { title: "Production", question: "Which machine should we inspect first?" },
      { title: "Finance", question: "Which product group fell below margin target?" },
      { title: "Inventory", question: "Which material is nearing critical stock?" },
      { title: "Executive", question: "Which three gaps need a decision this week?" },
    ],
    trustTitle: "Checks, access, and source stay together.",
    trustBody:
      "Read-only boundaries, pre-execution checks, server-side permissions, and a visible source work together.",
    integrationTitle: "Start with your existing data sources.",
    integrationBody:
      "DuckDB powers the sample flow and Postgres is in the current connection scope. Other sources require live validation.",
    faqTitle: "Frequently asked questions",
    faq: [
      { question: "Is dima only a chat tool?", answer: "No. Chat is the starting point; answers use business definitions, controlled queries, and a visible reporting flow." },
      { question: "How is a query checked?", answer: "AI may propose it. dima checks permitted reads and executability before the query reaches the source." },
      { question: "What do those checks not prove?", answer: "They do not independently prove business definitions, source quality, or interpretation. People still review the result." },
      { question: "Which sources are supported?", answer: "DuckDB powers the sample flow and Postgres is in the current connection scope. Other sources require live validation." },
    ],
  },
  pages: {
    product: {
      eyebrow: "Product",
      title: "From question to answer.",
      description: "Ask in everyday language; dima finds the relevant data, checks the query, and shows the result with its source.",
      cta: "Start with your question",
      sections: [
        { id: "ask", title: "Ask in business language", body: "Start with the terms your team knows without memorizing tables or columns.", points: ["Follow-up questions", "Conversation context"] },
        { id: "model", title: "Share the same definitions", body: "Measures, relationships, and units meet in one business model.", points: ["Shared definitions", "Relationships", "Units"] },
        { id: "validate", title: "Check before execution", body: "The proposed query is checked for permitted reads and executability before it reaches the source.", points: ["Read-only", "Visible query"] },
        { id: "explore", title: "Review the answer your way", body: "See the result as a table, chart, or comparison and ask the next question.", points: ["Table", "Chart", "Comparison"] },
        { id: "govern", title: "Preserve access boundaries", body: "Session, organization, and user permissions are rechecked on the server.", points: ["Session", "Organization scope", "User access"] },
        { id: "reuse", title: "Reuse useful analysis", body: "Saving, replay, and scheduling flows are being developed under controlled status.", status: "pilot" },
      ],
    },
    how: {
      eyebrow: "How it works",
      title: "See what is checked before the answer arrives.",
      description: "Question, business meaning, query, access, and source move through one visible flow.",
      cta: "Review the technical scope",
      sections: [
        { id: "problem", title: "Raw text alone is not enough", body: "A query that runs does not prove that it used the right metric or permission boundary.", visual: { key: "question", caption: "Question and meaning" } },
        { id: "semantics", title: "Share business definitions", body: "Metrics, time periods, units, and approved terms meet in one shared meaning.", visual: { key: "definitions", caption: "Modeled context" } },
        { id: "interpretation", title: "Move the question into context", body: "Metric, detail, time, and relationship choices become visible; unresolved ambiguity stays visible too." },
        { id: "guard", title: "Check the query before execution", body: "The AI proposal is restricted to permitted reads and executable plans.", visual: { key: "checks", caption: "Query checks" } },
        { id: "permissions", title: "Recheck access on every request", body: "The server evaluates session, organization, and user scope independently of the interface.", visual: { key: "access", caption: "Permission boundaries" } },
        { id: "answer", title: "Show the result, query, and source", body: "The checks support a safe, executable flow; people still review business definitions, source quality, and interpretation.", visual: { key: "source", caption: "Answer source" } },
      ],
    },
    solutions: {
      eyebrow: "Solutions",
      title: "Every team starts with its own question.",
      description: "Bring operations, production, finance, sales, inventory, and leadership questions to shared business definitions.",
      cta: "Discuss your priority question",
      sections: [
        { id: "operations", title: "Which operational step moved from target?", body: "Inspect target, actual, and driver in the same period and process context.", points: ["Target and actual", "Follow-up questions"] },
        { id: "production", title: "Which machine should we inspect first?", body: "Compare machine, shift, batch, OEE, and waste signals in one question.", points: ["OEE and waste", "Batch and shift"] },
        { id: "finance", title: "Which product group fell below margin target?", body: "Follow shared revenue, cost, and period definitions from result to detail.", points: ["Revenue and cost", "Result to detail"] },
        { id: "sales", title: "Which customer or product group is at risk?", body: "Combine customer, order, and product context to review changing commercial signals.", points: ["Customer and order", "Comparison"] },
        { id: "inventory", title: "Which material is nearing critical stock?", body: "Follow material, movement, reservation, and required-period context together.", points: ["Critical stock", "Need and movement"] },
        { id: "executive", title: "Which three gaps need a decision this week?", body: "See priority indicators with the definitions and details that produced them.", points: ["Prioritize gaps", "Explore details"] },
      ],
    },
    textile: {
      eyebrow: "Textile dyehouse",
      title: "Connect dyehouse data to production decisions.",
      description: "An anonymized example narrative for reviewing batches, recipes, machines, quality, resource use, and shipment risk in one context.",
      cta: "Discuss the dyehouse question",
      sections: [
        { id: "question", title: "Which batch carries the highest risk?", body: "Connect batch, order, machine, and quality deviation context to see where review should begin.", points: ["Batch and order", "Color deviation"], visual: { key: "question", caption: "Batch and quality question" } },
        { id: "production", title: "Which machine affects OEE and waste?", body: "Compare OEE, waste, and downtime across machines, shifts, and production records.", points: ["OEE and waste", "Machine and shift"], visual: { key: "coordination", caption: "Production indicators" } },
        { id: "recipe", title: "How do recipe and resource use change?", body: "Review recipe, chemical, water, and energy use in one question chain using anonymized example data.", points: ["Recipe and chemicals", "Water and energy"], visual: { key: "definitions", caption: "Recipe and resource definitions" } },
        { id: "quality", title: "Which conditions appear with a quality deviation?", body: "Compare quality outcomes, process conditions, and batch detail through visible definitions.", points: ["Quality deviation", "Reviewable source"], visual: { key: "checks", caption: "Quality checking chain" } },
        { id: "orders", title: "Which order has rising deadline risk?", body: "Review order dates, production progress, and shipment status around the decision that needs attention.", points: ["Deadline view", "Shipment risk"], visual: { key: "priority", caption: "Order and deadline priority" } },
        { id: "integration", title: "How does the example become real scope?", body: "Source access, table discovery, definitions, and permission boundaries come before any deployment claim.", points: ["Anonymized example terms", "Pilot evaluation"], status: "pilot", visual: { key: "connection", caption: "Connection and modeling flow" } },
      ],
    },
    security: {
      eyebrow: "Security",
      title: "Fast answers should not hide access boundaries.",
      description: "We describe verified mechanisms—not certifications or absolute security claims.",
      cta: "Discuss the security scope",
      sections: [
        { id: "read-only", title: "Read-only access", body: "Queries are limited to permitted reads and checked before execution." },
        { id: "session", title: "Session security", body: "Short-lived access tokens stay in memory; refresh tokens use secure, script-inaccessible cookies." },
        { id: "tenant", title: "Organization and permission scope", body: "The server rechecks session, organization, and user access on every request." },
        { id: "audit", title: "Activity records", body: "Query, authentication, and management actions can be recorded within the agreed deployment scope." },
        { id: "deployment", title: "Setup options", body: "The current cloud setup is available. A hybrid on-premises connection remains planned.", status: "planned", visual: { key: "deployment", caption: "Setup and data flow" } },
      ],
    },
    integrations: {
      eyebrow: "Integrations",
      title: "Start with your existing data sources.",
      description: "We separate every source into verified in Dima, technically possible, or planned.",
      cta: "Assess the connection scope",
      sections: [
        { id: "duckdb", title: "DuckDB sample source", body: "An anonymized source that demonstrates the product flow without customer data.", status: "available" },
        { id: "postgres", title: "Postgres", body: "A source used in the current Dima connection scope and verified there.", status: "available" },
        { id: "engine", title: "MSSQL and Oracle", body: "The engine can connect technically; Dima support follows live connection and query testing.", status: "planned" },
        { id: "process", title: "Setup flow", body: "Connection → table discovery → business definitions → query checks → user access.", visual: { key: "connection", caption: "Connection and modeling flow" } },
        { id: "status", title: "What support means", body: "Each source carries a real validation label; technical possibility is not product support." },
      ],
    },
    about: {
      eyebrow: "About",
      title: "Making business data easier to understand.",
      description: "dima is a conversational analytics product built by UpcyTech Teknoloji Anonim Şirketi.",
      cta: "Meet the team",
      sections: [
        { id: "purpose", title: "Why dima?", body: "To help business teams reach answers sooner while preserving the control data teams need." },
        { id: "principles", title: "How we build", body: "We bring business language, shared definitions, and checks into one analytical flow.", points: ["AI proposes; the system checks", "Business definitions stay shared", "Source and result stay together"] },
        { id: "truth", title: "Evidence before claims", body: "We do not use fabricated statistics, certifications, customer logos, or unverified future plans.", visual: { key: "truth", caption: "Evidence and boundaries in view" } },
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
        { id: "pilot", title: "8. Pilot and planned features", body: "Pilot-scope features may change, receive limited support, or be withdrawn. Planned features are not committed delivery dates. Query contracts, verification, scheduling, and notifications depend on tenant features and contract scope." },
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
  "/solutions/textile-dyehouse",
  "/security",
  "/integrations",
  "/about",
  "/contact",
  "/privacy",
  "/terms",
] as const;
