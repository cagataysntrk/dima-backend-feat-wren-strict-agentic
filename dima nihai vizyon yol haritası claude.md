Ready for review
Select text to add comments on the plan
Dima: Vizyon Dokümanı ↔ Mevcut Kod — Kapsamlı Gap Analizi ve Yol Haritası
Context (neden bu analiz, ne hedefleniyor)
Wren_Hibrit_GenBI_SaaS_Strateji.md — kodu görmeden yazılmış bir dış danışman dokümanı — Dima'nın kurumsal ölçekli, çok-kiracılı bir "GenBI SaaS" olması için WrenAI omurga + Cube-tarzı Intent Query Compiler + Zenlytic-tarzı Discovery→Promote döngüsü + Upsolve-tarzı Trust Plane + tam SaaS control-plane (RLS/RBAC/quota/BYO-LLM/region-pin) öneriyor.

Kullanıcı iki şeyi bilmiyor: (1) mevcut kod bu nihai hedefe ne kadar uygun/uzak, (2) oraya nasıl, hangi sırayla, fizibil şekilde varılır. Bu doküman, kodu 3 paralel derin-araştırma turuyla (cube_router/MDL/Trust-Plane; çok-kiracılık/RLS/control-plane; monorepo/MCP/chart/ vendoring) okuyup vizyonla karşılaştırdıktan VE taslak yol haritasını bağımsız bir fizibilite stres-testinden geçirdikten sonra yazıldı. Amaç: yönetilebilir, sıralaması doğru, "neden şimdi değil" gerekçeli, gerçekçi bir yol haritası.

Yönetici Özeti
Tek cümle: Vizyonun İLKELERİ sağlam ve büyük ölçüde koda zaten (dağınık halde) gömülü; asıl iş yeni bir mimari icat etmek değil, var olanı FORMEL HALE GETİRMEK + BAĞLAMAK + DOĞRU SIRAYA KOYMAK + tek gerçekten eksik yeteneği (Discovery→Promote-to-MDL) dikkatle inşa etmek — ve bunu yaparken vizyonun bazı parçalarını (monorepo, LLM chart-gen, MCP, dbt, embed, paylaşımlı-DB RLS) şu an için BİLİNÇLİ OLARAK ERTELEMEK.

En kritik tek bulgu: backend/app/cube_router.py (1400 satır) zaten vizyonun "Intent Query + Semantic Compiler" ikilisine şaşırtıcı derecede yakın — tipsiz de olsa bir CubeQuery DSL'i, whitelist doğrulayıcı (parse_cube_query), deterministik derleyici (cube_sql → wren_core + always_filter enjeksiyonu + dialect transpile). Yakın zamanda onaylanmamış bir iç göç raporu (DIMA_AGENTIC_MIGRATION_REPORT.md) bu dosyayı TAMAMEN SİLİP her soruyu ham-SQL LLM üretimine (/ask) yönlendirmeyi planlamıştı — vizyonun tam merkez önerisinin (LLM = niyet seçici, SQL = istisna) TERSİ yönünde.

KARAR (kesinleşti — kullanıcı onayı): cube_router.py silme planından KESİN OLARAK vazgeçildi. Yapı "strict-agentic" (her soru ham-SQL) yönünden vizyonun nihai hedefine (Intent Query Compiler önce, ham-SQL istisna) doğru ÇEVRİLECEK. Aşağıdaki Faz 0-d'deki zemin-gerçeği ölçümü artık bir "yapalım mı" kapısı DEĞİL — yalnız Faz 1'in kapsamını/sırasını kalibre etmek için tanı amaçlı bir ölçüm olarak kalır. Faz 1'deki mühendislik güvenceleri (rota-telemetrisi, kademeli geçiş, maliyet/gecikme bake-off'u, hızlı geri-dönüş) yine de uygulanmalı — bunlar "yapalım mı" sorusuna değil "nasıl güvenli yapılır" sorusuna hizmet eder.

İkinci önemli bulgu: Vizyonun bazı parçaları zaten beklenenden ÇOK daha olgun:

admin_app/ zaten gerçek bir ayrı-dağıtılabilir "control plane" (kendi JWT anahtar çifti, Wren/LLM'siz Docker imajı, kendi migration sahipliği) — vizyonun karşılaştırma tablosunun "Wren'in SaaS tenancy'si zayıf" varsayımından daha ileride.
backend/eval/ zaten gerçek bir Trust-Plane metodolojisi (129 altın vaka, Wilson-güven- aralıklı precision/coverage, commit'li baseline, regresyon kapısı) — ama HİÇBİR CI'a bağlı değil (ucuz, yüksek getirili bir kazanım).
admin_app/routers/synonyms.py'deki aday-kuyruğu→onay→additive-overlay deseni gerçek ve kanıtlanmış bir "Promote" iş akışı şekli — ama yalnız kelime/eşanlamlı seviyesinde.
Üçüncü önemli bulgu — gerçek, kanıtlanmış bir güvenlik açığı: app/schedules.py'de zamanlanmış raporlar varsayılan tenant'ın DB bağlantısını kullanıyor, kendi tenant'ına resolve etmiyor → B tenant'ının raporu A'nın verisini görebiliyor. Bu, vizyon hedefinden bağımsız, HEMEN düzeltilmesi gereken bir P0.

Dördüncü bulgu (stres-testten): Taslağımın ilk versiyonu Trust-Plane'i çok geç sıralıyordu, kiracı-sızıntısı denetimini çok geç bırakıyordu, ve Discovery→Promote için "sadece synonym desenini uzat" demek riski hafife alıyordu (bir ölçünün yanlış olması bir eşanlamlının yanlış olmasından KATEGORİK olarak daha tehlikeli — kompozisyon riski, çift-sayım, grain uyuşmazlığı). Aşağıdaki yol haritası bunları düzeltir.

Kapsamlı Boşluk Matrisi
Vizyon kavramı	Mevcut durum	Değerlendirme
Intent Query DSL (şema-kısıtlı JSON)	cube_router.py CubeQuery dict + parse_cube_query whitelist	%70 var — tipsiz dict, tek-cube (join-graph yok), silinme tehdidi altında
Semantic Compiler (Intent→SQL, RLS)	wren_service.cube_sql() (wren_core + always_filter + dialect transpile)	Var ama tek-cube kapsamlı; RLS'siz (always_filter yalnız iş-mantığı)
Discovery Path (ham-SQL istisna)	Bugünün TEK yolu haline gelmiş /ask (LLM ham Wren SQL)	Ters çevrilmiş — istisna değil, varsayılan olmuş
"Dynamic measure" taslağı	Yok (grep: sıfır)	Tamamen eksik — tek gerçekten yeni inşa gereken parça
Promote (cache/kelime)	promote_vqr, synonym approved kapısı	Var ama yalnız cache/kelime; yeni ölçü/cube MDL'e hiç giremiyor
MDL revizyon/draft→publish	mdl_version (içerik hash'i, yalnız tanı amaçlı)	Yok — dosya düzenlemek = yayınlamak; git tek versiyon
Trust Plane (golden+eval+CI)	eval/ (129 vaka, Wilson CI, baseline, regresyon testi)	Metodoloji sağlam, CI'a HİÇ bağlı değil
Query Contract / lineage	contracts.py (CubeQuery yolu için)	Ham-SQL/Discovery yolunda yok (göç raporunda bilerek çıkarılmış)
RBAC	authorize()/ROLE_RANK tam kodlu+test edilmiş	Uykuda — admin API yalnız owner rolüne izin veriyor
RLAC/CLAC (satır/kolon erişimi)	ModelPermission tablosu var	Stub, enforce_query() bilinçli no-op
SQL-seviyeli tenant RLS	always_filter mekanizması var ama...	...yalnız iş-mantığı için; tenant için hiç yok; ham-SQL yolunu kapsamıyor
Tenant izolasyonu	Connection-bazlı (her tenant kendi DB'si)	Çalışıyor ama KANITLANMIŞ sızıntı var (schedules.py)
API-key/makine auth	Yok (yalnız JWT+cookie)	Tamamen eksik — MCP'nin ön koşulu
Audit log	control_plane/audit.py — durable spool + fail-closed	Sağlam
Quota/billing	Yok (Tenant.status ikili switch dışında)	Eksik ama telemetri (token/latency) zaten toplanıyor
Per-tenant BYO-LLM	Süreç-global tek config	Eksik ama DbConnection'ın şifre deseni doğrudan yeniden kullanılabilir
Region pin	Yok	Sıfır — hatta config stub'ı bile yok
Control plane / data plane ayrımı	admin_app gerçekten ayrı süreç	Zaten büyük ölçüde başarılmış
MCP/agent-native yüzey	Dima'da yok	Yeşil-alan DEĞİL — vendored wren paketinde tam MCP server zaten var, bağlanmamış
Chart üretimi (kural+LLM Vega-Lite)	viz.py %100 deterministik, LLM yok	Kasıtlı olarak korunmalı; AMA backend/frontend'de elle senkronlanan kopya mantık var (canlı bakım riski)
dbt/MetricFlow, embed SDK	Yok	Sıfır, hiç prototip yok
Monorepo (packages/*)	Tek monolitik FastAPI + ayrı admin_app	Şu ölçekte gereksiz — ama iç modülerlik (adlandırma) ucuza şimdi kurulabilir
Worker/job kalıcılığı	Tek in-process 60sn daemon thread	Ayrı bir güvenilirlik sorunu (monorepo tartışmasından bağımsız)
WrenAI vendoring/pin riski	Düz kopya (submodule değil), gevşek versiyon aralığı	Gerçek risk, hiçbir fazda ele alınmamıştı — düzeltildi (Faz 0)
Yol Haritası (stres-testten sonra revize edilmiş)
Faz 0 — Hemen, günler (paralel iş kolları, "vizyon"dan bağımsız temel hijyen)
Bunların hiçbiri "SaaS vizyonuna ulaşma" hırsına bağlı değil — bekleyemeyecek kadar acil veya sonraki her fazın güvenilirliğini belirleyen ölçümler.

0-a. cube_router.py silme planı KESİN OLARAK İPTAL (karar verildi — dondurma değil, iptal). Bu dosya artık Faz 1'in temeli: en mükemmel hale getirilecek (tipli şema, whitelist doğrulama sağlamlaştırma, join-graph genişletme) — silinmeyecek, tersine BÜYÜTÜLECEK.

0-b. app/schedules.py kiracı-sızıntısı düzeltmesi — ŞİMDİ, tek başına. run_schedule varsayılan state.wren yerine company_registry.service_for(schedule.tenant_slug) kullanmalı.

0-c. Sistematik "yanlış tenant bağlantısı" denetimi (yalnız tek düzeltme değil). 0-b'nin kanıtladığı hata SINIFI — DB/servis handle'ı alan HER kod yolu (scheduler, clone job, admin işlemleri, arka plan thread'leri) tenant-doğruluğu için taranmalı. Kritik yeni öneri (stres- testten): bir fail-closed runtime invariant — tüm sorgu yürütmelerinin geçtiği TEK bir choke-point'te, "çözülen bağlantının tenant kimliği ile istekteki kimlik doğrulanmış tenant claim'i eşleşiyor mu" assert'i. Bir test suite'i yalnız düşünülen senaryoları yakalar; bu invariant her yolu kapsar. Bu, 0-b ile PARALEL yürütülmeli, sonraki fazları beklememeli.

0-d. Zemin-gerçeği analizi (artık bir "yapalım mı" kapısı DEĞİL — kalibrasyon ölçümü). Yön kesinleşti (Intent Query Compiler'a dönüş), bu ölçüm o kararı sorgulamıyor; yalnız Faz 1'in kapsamını kalibre ediyor. Mevcut cube_router.parse_cube_query/build_catalog'u eval/altın- küme'nin (129 vaka) ve varsa gerçek prod loglarının üzerinden koşturup: bugünkü CubeQuery şeması sorularının yüzde kaçını zaten kapsıyor, hangi soru kalıpları kapsam dışı (join-graph genişlemesi mi gerekiyor, yeni ölçü mü, yoksa yalnız sözdizimi mi)? Bu, Faz 1/2'nin İŞ LİSTESİNİ önceliklendirmek için kullanılır (en çok kapsam-dışı kalan soru kalıplarını önce kapatmaya odaklan).

0-e. WrenAI vendoring/pin riskini kapat. WrenAI-main/ düz kopya (submodule değil) — ya gerçek bir git submodule/fork'a çevir ya da net bir "hangi commit, ne zaman güncellenir" politikası yaz. pyproject.toml'daki wrenai>=0.13,<0.14 aralığını tam pin'e çevir VE Dockerfile'ın kendi itiraf ettiği prod/dev davranış farkını (yerel ayna ≠ PyPI paketi) çöz — aksi halde Faz 1/2'nin tüm doğruluk varsayımları kayan bir zemin üzerinde durur.

0-f. eval/ harness'ini CI'a bağla (GitHub Actions). Ucuz, yüksek getiri — AMA baseline.json'ın Faz 1 sonrası yeniden ölçüleceğini şimdiden not et (aşağıda).

0-g. Scheduler/worker güvenilirlik incelemesi (monorepo tartışmasından AYRI). Tek in-process daemon thread: (i) tek hata noktası, retry semantiği yok; (ii) birden fazla app replikası varsa/olacaksa, her replika bağımsız çalışıp zamanlanmış raporları/bildirimleri YİNELEYEBİLİR (0-b'deki hatayla aynı ailede bir risk). Bu ölçek büyümeden ucuz bir düzeltme (distributed lock veya tek-lider seçimi); ölçek büyüdükten sonra pahalı bir kesinti nedeni.

Faz 1 — Intent-first yönlendirme (KARARLAŞTIRILDI — kesin uygulanacak)
CubeQuery'ye resmi bir tip/şema kazandır (Pydantic/JSON-schema — vizyonun "şema ile kısıtlı" isteği). LLM artık cube SEÇMEK yerine tam Intent-JSON'ı DOLDURSUN (constrained/structured output). Önceki oturumda zaten kurulmuş VQR/meta-katalog-kapısı/takip-üretimi mekanizmaları "Route" aşaması olarak ÖNE geçer; ham-SQL üretimi artık "Discovery" adıyla AÇIKÇA etiketlenmiş istisna yoluna düşer (bugünkü gibi sessizce varsayılan değil).

Not (artık bir "yapalım mı" tartışması değil, uygulama sırasında akılda tutulacak mühendislik dengeleri): Ham-SQL/Discovery yolunun tamamen ortadan kalkmayacağını, Intent şemasının kapsamayacağı sorular için KALICI bir istisna yolu olarak kalacağını unutma — bu yüzden Faz 2 (Discovery→Promote) bu fazla birlikte anlam kazanıyor. AST-seviyeli SQL-doğrulama (tablo/kolon whitelist + tenant/iş-filtresi enjeksiyonu) fikri, Discovery yolunun GÜVENLİĞİNİ güçlendirmek için ayrıca değerlendirilebilir (DSL'in yerine değil, DSL'in kapsamadığı istisna yolunun ek güvencesi olarak).

Bu fazı önceki taslaktan ayıran, stres-testten gelen zorunlu eklemeler (yön kesinleşse de bunlar hâlâ geçerli — güvenli/ölçülebilir bir geçiş için):

Rota-dağılımı telemetrisi Faz 1 BAŞLAMADAN kurulmalı (Intent% vs Discovery% vs cache%) — aksi halde "flip gerçekten işe yaradı mı" hiç ölçülemez.
Kademeli devreye alma + hızlı geri-dönüş (canary/percentage rollout) — bu, yol haritasındaki EN riskli tek değişiklik; "tüm trafik anında flip" YOK.
Maliyet/gecikme bake-off'u: Intent-JSON'ın tüm alanları doldurması (büyük çıktı + olası doğrulama-onarım döngüleri) ham-SQL'den DAHA PAHALI olabilir — vizyonun kendi ekonomik argümanını baltalamasın diye, altın küme üzerinde flip'ten ÖNCE ölçülmeli.
eval/baseline.json bu faz sonrası yeniden ölçülmeli (0-f'nin CI kapısı, rota değiştiğinde eski baseline'a karşı yanlış alarm verir/vermez).
Trust-Plane genişlemesi bu fazla İÇ İÇE, ayrı bir sonraki faz değil: yeni Intent-yolu senaryoları için altın vaka eklemek + Discovery yoluna Query-Contract lineage'ı GÜN 1'den itibaren (Faz 3'e ertelenmeden) bağlamak.
Faz 2 — Semantik-model değişiklik-inceleme ve yaşam-döngüsü sistemi (yeniden sınıflandırıldı)
Stres-test bunu netleştirdi: bu, "synonym desenini uzatmak" DEĞİL — synonym onay iş akışının İSKELETİ (aday kuyruğu → onay → additive overlay → onaysız asla canlıya inmez) yeniden kullanılabilir, ama risk yüzeyi kategorik olarak farklı, bu yüzden gerçek bir tasarım gerekiyor:

Blast radius farkı: yanlış bir eşanlamlı tek bir soruyu zaten-doğrulanmış bir ölçüye yanlış yönlendirir (sıfır kompozisyon riski). Yanlış bir ÖLÇÜ yeni SQL demektir — join-yolu fan-out/fan-in (çift-sayım klasikleri), grain uyuşmazlığı, ve onaylandıktan sonra blend/ compare ile onay anında test edilmemiş başka ölçülerle birleşme riski taşır.
İncelemeci uzmanlığı farkı: "revenue brüt mü net mi" dilbilimsel bir karar; "bu agregasyon mantıksal doğru mu, bu join çift-sayım yapıyor mu, grain doğru mu" analitik- mühendislik code review'u. Reviewer'a SQL + join-yolu görünümü + örnek satırlar + benzer mevcut ölçülerle karşılaştırma gösterilmeli — tek-tıkla-onayla değil.
Test yükü farkı: bir ölçü onaylandığında EŞZAMANLI en az bir eşleşen altın-küme vakası yazılması ZORUNLU olmalı — yani Faz 2 ve genişletilmiş Trust-Plane bu noktada SIKI bağlı olmalı, ardışık fazlar değil.
Geri-alınabilirlik farkı: kötü bir ölçüyü "sertifikasız" yapmak boolean flip değil — deprecate/supersede/recall yaşam döngüsü gerekir (zaten dashboard'larda, blend sorgularında, VQR önbelleğinde, Contract'larda kullanılmış olabilir). Bunun ön koşulu: minimal bir MDL revizyon/draft kavramı inşa etmek (bugün YOK — dosya düzenlemek = yayınlamak). Bu, Faz 2'nin "tek satırlık" değil, gerçek bir alt-proje olduğu anlamına gelir.
Ad alanı/çakışma riski farkı: yeni bir ölçü kelime dağarcığını GENİŞLETİR (avg_order_ value vs zaten var olan average_order_value gibi ince-anlamlı çakışmalar) — izole incelenen bir kuyruk bunu yakalamaz; mevcut tüm semantik modele karşı bir çakışma ön- kontrolü gerekir.
Döngüyü kapat: yeni onaylanan bir ölçü, LLM'in statik knowledge/rules|sql/*.md bilgisine de yansıtılmalı (otomatik bir bilgi-parçası üretilerek veya reviewer'dan bunu da yazması istenerek) — yoksa LLM yeni ölçüyü hiç keşfedip kullanmayabilir (Faz 2 boşa gider).
Reviewer rolü ön koşulu: bu iş akışı gerçek bir "analyst/admin onaylar" rolü gerektirir — bu yüzden RBAC'ın en azından bu kullanım durumu için AKTİFLEŞTİRİLMESİ (bkz. Faz 4) Faz 2'nin bir ÖN KOŞULU, ayrı/ertelenmiş bir Faz-4 kalemi değil.
Faz 3 — Trust Plane sağlamlaştırma (Faz 1/2 ile iç içe yürütülür, ayrı/sonraki değil)
Tek "explain" nesnesi (path/confidence/assumptions — bugünün dağınık trace[]/source alanları yerine); Query Contract'ı Discovery yoluna da genişletmek (Faz 1'in GÜN 1'i, burada değil); altın-küme büyümesi her Faz 1/2 teslimatıyla birlikte, sona bırakılmadan.

Faz 4 — Çok-kiracılı güvenlik sağlamlaştırma (vizyon hırsından bağımsız, temel hijyen)
Fail-closed tenant-bağlantı invariant'ı (0-c'de detaylandırıldı — buraya değil oraya taşındı).
Paylaşımlı-DB RLS YAPMA kararı — yönü doğru ama maliyeti tek taraflı değil: connection-başına izolasyonun KENDİ maliyetleri var (connection-pool tükenmesi, tenant sayısı arttıkça per-tenant migration yükü, yeni tenant provizyonlama sürtünmesi) — bunlar büyüdükçe paylaşımlı-DB+RLS'e geçmeyi GEREKTİREBİLİR. Karar kriterleri (şimdi yazılı, ileride gözden geçirilecek): (a) hiçbir imzalı/geç-aşama müşteri paylaşımlı altyapı istemiyor, (b) connection-pool doluluğu tepe yükte açık bir eşiğin (örn. max_connections'ın %70'i) altında kalıyor, (c) yeni tenant provizyonlama süresi satış döngüsünde darboğaz olmuyor, (d) kurumsal güvenlik incelemeleri "ayrı DB" hikayesini itirazsız kabul etmeye devam ediyor. Bunlardan biri tersine dönerse karar gözden geçirilir. (Not: "ayrı fiziksel DB" hikayesi kurumsal satışta genelde "her sorguyu doğru filtreliyoruz" hikayesinden DAHA KOLAY satılır — lehte.)
RBAC: genel aktivasyon (viewer/analyst/admin rollerini herkese açmak) hâlâ ERTELENEBİLİR, ama Faz 2'nin reviewer ihtiyacı için DAR KAPSAMLI aktivasyon Faz 2'nin ön koşuluna taşındı.
RLAC/CLAC (ModelPermission stub) ve per-tenant BYO-LLM: somut müşteri talebi çıkınca inşa et (ikisi de altyapısı hazır — sırasıyla stub tablo ve DbConnection'ın şifre deseni — ucuz gecikmeli inşa).
Faz 5 — Fırsatçı/ertelenen (ama bazıları göründüğünden daha bağımlı/acil)
MCP: ertelenebilir AMA "ucuz çünkü kütüphane hazır" yeterli değil — gerçek ön koşulları var: API-key/makine auth (bugün yok) + canlı RBAC (bugün uykuda). Bunlar olmadan MCP bağlanamaz; "blocked-by" olarak takip edilmeli, sadece "sonra yaparız" değil. ait olduğu talep gerçekten oluşunca değerlendirilmeli — pazarlama/satış girdisi gerekir.
Region-pin: dbt/embed'den FARKLI kategoride — genelde uzun-vadeli altyapı (çoklu-bölge DB/replikasyon) gerektirir ve kurumsal RFP'lerde bir isim müşterisi olmadan ÖNCE bir kutu- işaretleme sorusu olarak çıkabilir. Öneri: kod yazmadan önce hafif bir keşif ("satış pipeline'ında bu ne sıklıkla soruluyor?") — tamamen dbt/embed gibi ertelemek yerine.
dbt/MetricFlow import, embed SDK: gerçek talep oluşana kadar ertelensin — ikisi de sıfır.
LLM Vega-Lite chart üretimi: mevcut deterministik viz.py'nin korunması ÖNERİLİR (maliyet ve tutarlılık için muhtemelen daha iyi) — AMA bu, backend (viz.py) ve frontend (chart.ts) arasındaki ELLE-SENKRONLANAN kopya mantığı sorununu ERTELEMEMELİ: bu canlı bir bakım/doğruluk riski (iki dilde el ile senkron tutulan aynı sezgisel algoritma), LLM chart-gen tartışmasından BAĞIMSIZ olarak Faz 1 veya 3'e alınmalı — tek bir backend-hesaplı spec, frontend yalnız render etsin.
Monorepo (packages/*) tam ayrıştırması: bu ölçekte YAPILMASIN — ama Faz 1/2 zaten kod yazarken, iç modülerlik (app/intent/, app/compiler/, app/discovery/, app/trust/ gibi temiz Python paketleri, TEK repo içinde) tasarım ilkesi olarak benimsenmeli — ileride gerçek bir ayrıştırma gerekirse maliyeti neredeyse sıfıra iner.
Quota/billing: hiçbir fazda sahibi yok, bilinçli olarak — kullanım telemetrisi (LLM token/gecikme) zaten InteractionLog'da toplanıyor, bu yüzden mühendislik ucuz olacak, AMA fiyatlandırma modeli önce bir ÜRÜN/İŞ kararı gerektiriyor — "mühendislik başlamadan önce iş kararı gerekli" olarak açıkça işaretlenmeli, sessizce atlanmamalı.
Doğrulama (her fazın "bitti" sayılması için)
Faz 0: (b) sızıntı testi — B tenant'ının zamanlanmış raporu çalıştırılır, yalnız B'nin verisini döndürdüğü doğrulanır. (c) invariant testi — sahte bir "yanlış tenant" bağlantısı enjekte edilip sorgunun reddedildiği (sessizce geçmediği) doğrulanır. (d) zemin-gerçeği raporu — somut bir yüzde ile teslim edilir, Faz 1'in git/gitme kararı bu sayıya bağlanır. (f) CI'da test_eval_gate.py'ın gerçekten push/PR'da çalıştığı görülür (yeşil/kırmızı).
Faz 1: canary'de rota-dağılımı telemetrisi Intent-payının arttığını gösterir; altın-küme regresyonsuz geçer; maliyet/gecikme bake-off'u Intent yolunun ham-SQL'den daha ucuz/hızlı (veya kabul edilebilir ölçüde farklı) olduğunu gösterir; geri-alma denenip çalışır.
Faz 2: bir test promosyonu uçtan uca yürütülür — aday yakalanır → reviewer SQL/join-yolu görür → onaylar → eşleşen altın-vaka birlikte yazılır → MDL'e (draft→publish adımıyla) girer → knowledge-base güncellenir → LLM sonraki soruda yeni ölçüyü gerçekten kullanır. Bir "geri-al" senaryosu da (deprecate) uçtan uca test edilir.
Faz 4: cross-tenant sızıntı test suite'i (yalnız schedules.py değil, tüm bağlantı- edinme yolları) CI'da yeşil; RLS kararının 4 kriteri çeyreklik gözden geçirilir.
Ürün Dönüşümü — "Bugün" ↔ "Yol Haritası Sonunda" Karşılaştırması
Boyut	BUGÜN (strict-agentic, basit sürüm)	YOL HARİTASI SONUNDA (nihai vizyon)
Soru→cevap mekanizması	Her soru LLM'e ham Wren SQL yazdırır (tek yol); cube_router yalnız /cube chip-düzenlemesinde kalıntı	LLM varsayılan olarak tipli Intent-JSON (CubeQuery) doldurur → deterministik derleyici SQL yazar; ham-SQL yalnız etiketli, izlenen bir "Discovery" istisnası
Aynı/benzer soru tekrarı	Her seferinde yeniden LLM'e düşer (önceki oturumda VQR eklendi ama Faz 1 öncesi hâlâ ham-SQL üzerinden)	Intent-yolu + VQR birlikte: tekrarlayan sorular çoğunlukla LLM'siz, ölçülebilir bir "Intent-payı" KPI'sı ile izlenir
Takip soruları / bağlam	prev_sql ile tek-adım takip düzenlemesi var (önceki oturum) ama CubeQuery'siz, yapısal değil	Intent-JSON'un kendisi yapısal durumdur — "aylara göre", "filtre ekle" gibi istekler CubeQuery alan düzenlemesi olarak ele alınır, WrenAI'ninkinden daha yapısal
Kapsam dışı / yeni ölçü ihtiyacı	LLM ham SQL uydurur, kalıcı hiçbir yere kaydolmaz (VQR yalnız soru-cevap önbelleği)	Discovery başarılı olursa yapılandırılmış bir "taslak ölçü" önerisi olarak yakalanır → analist inceler (SQL/join-yolu/örnek satır görür) → onaylanırsa MDL'e kalıcı, versiyonlu bir ölçü olarak girer, eşleşen altın-test'iyle birlikte
Grafik/görselleştirme	/ask (ham-SQL) yolunda viz.recommend bağlanmamıştı (bu oturumda düzeltildi); backend/frontend'de elle-senkron kopya sezgisel mantık var	Tek backend-hesaplı grafik kararı, frontend yalnız render eder (kopya mantık sorunu kapanır); LLM chart-gen bilinçli olarak eklenmez (maliyet/tutarlılık için deterministik tercih edilir)
Doğruluk/regresyon güvencesi	129 altın vaka + Wilson-CI eval harness VAR ama hiçbir CI'a bağlı değil — yalnız elle pytest	Her push/PR'da otomatik çalışan CI kapısı; Discovery yolu da altın-küme kapsamında; her yeni onaylı ölçü kendi test'iyle gelir
Kanıt/lineage (“bu sayı neden doğru”)	Query Contract yalnız CubeQuery yolunda; ham-SQL yolunda göç raporunca bilerek çıkarılmış	Tek, tutarlı "explain" nesnesi (path/confidence/varsayımlar) her iki yolda da; Discovery cevapları açıkça "sertifikasız" etiketlenir
Çok-kiracılık / izolasyon	Connection-bazlı izolasyon çalışıyor AMA kanıtlanmış bir cross-tenant sızıntısı var (scheduler)	Sızıntı kapatılmış + tüm bağlantı-edinme yolları için fail-closed bir invariant; paylaşımlı-DB RLS'e GEÇİLMEZ (bilinçli, kriterli bir karar — connection-bazlı izolasyon güçlendirilerek sürdürülür)
Rol/izin (RBAC)	Kodlu ve test edilmiş ama üründe yalnız owner rolü açık	Ölçü-onay iş akışı için dar kapsamlı analyst/admin rolü aktif; genel rol-açılışı hâlâ ihtiyaç oluşunca yapılır
Control plane / data plane	admin_app zaten ayrı süreç, ayrı JWT, ayrı Docker imajı — olgun	Aynı temel korunur; artık ölçü-onay kuyruğu ve genişletilmiş telemetri/rota-dağılımı raporları da buraya eklenir
Agent-native / MCP	Yok; Dima yalnız kendi REST API'siyle (frontend'den) çağrılıyor	Faz 5'te, API-key/makine auth + dar-kapsamlı RBAC ön koşulları karşılanınca vendored wren paketindeki hazır MCP server'a bağlanır — Claude/Cursor gibi ajanlar aynı sertifikalı ölçülere erişir
WrenAI bağımlılığı	Düz kopya (submodule değil), gevşek versiyon aralığı, prod/dev farklı paket kullanıyor (kendi Dockerfile'ının itirafı)	Tam pinlenmiş/submodule'lenmiş, tek tutarlı paket her ortamda — Intent-compiler'ın üzerine inşa edildiği zemin artık kaymıyor
Maliyet görünürlüğü	LLM token/gecikme her etkileşimde zaten loglanıyor ama hiçbir rapor/fatura tüketmiyor	Aynı telemetri; + rota-dağılımı (Intent% vs Discovery% vs cache%) KPI'sı; quota/billing yalnız iş kararı netleşince (mühendislik hazır, fiyatlandırma modeli bekliyor)
İş dışı bırakılanlar (bilinçli)	—	Monorepo tam ayrıştırması, dbt/MetricFlow import, embed SDK, region-pin, per-tenant BYO-LLM, quota/billing — hepsi somut talep/ölçek gerektirene kadar ERTELENDİ, unutulmadı (Faz 5'te gerekçeleriyle yazılı)
Özetle: Bugünün Dima'sı "hızlı ama kör" bir tek-yol ham-SQL asistanı; yol haritası sonunda Dima, vizyon dokümanının istediği gibi "varsayılan olarak ucuz ve tutarlı (Intent-yolu), gerektiğinde esnek (Discovery), kullanıldıkça büyüyen (Promote), her cevabı kanıtlanabilir (Trust Plane) ve kurumsal güvenlik/izolasyon hijyeni kanıtlanmış" bir GenBI platformu olur — ama bunu var olan admin_app/eval/VQR/cube_router temelini ATMADAN, üzerine inşa ederek yapar.

Kritik Dosyalar
backend/app/cube_router.py · backend/app/wren_service.py (cube_sql/blend_sql/ _inject_always_filter) · backend/app/routers/ask.py · backend/app/vqr.py · backend/app/compose.py · backend/app/kpi.py · backend/admin_app/routers/synonyms.py · backend/eval/{cases.yaml,run.py,baseline.json} · backend/tests/test_eval_gate.py · backend/app/contracts.py · backend/app/schedules.py · backend/app/company_registry.py · backend/control_plane/{models.py,authorize.py} · DIMA_AGENTIC_MIGRATION_REPORT.md · WrenAI-main/ (vendoring/pin) · backend/pyproject.toml / Dockerfile.