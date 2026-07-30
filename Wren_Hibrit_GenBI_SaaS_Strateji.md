**Wren Main Temelli Hibrit GenBI Stratejisi** |  Kurumsal Ölçeklenebilir SaaS  |  Gizli — Strateji Dokümanı 

# **KURUMSAL ÖLÇEKLENEBİLİR GenBI SaaS** 

### **WrenAI Main Temelli En Mükemmel Hibrit Strateji** 

_Cube · Zenlytic · Upsolve · Wren Karşılaştırmasının Neticesi  |  Referans Mimari & Yol Haritası_ 

Bu doküman; WrenAI main (Open Context Engine), Cube semantic layer felsefesi, Zenlytic Clarity Engine ve Upsolve Trust katmanının fizibilite analizinden türetilmiş, kurumsal ölçekte SaaS olarak piyasadaki tüm rakiplerden üstün olmayı hedefleyen hibrit mimari ve uygulama stratejisidir. 

## **1. Yönetici Özeti** 

Piyasadaki ürünler tek boyutta optimize edilmiştir: Wren esnek text-to-SQL ve açık context sunar; Cube deterministik metrik ve cache sunar; Zenlytic açıklanabilirlik ve dynamic promote sunar; Upsolve dbt hizası ve trust/eval sunar. Hiçbiri tek başına hem açık agent-native context, hem deterministik metrik derleme, hem promote döngüsü, hem çok kiracılı SaaS güvenlik, hem de düşük LLM maliyetini bir arada vermez. 

Strateji: WrenAI main’i omurga (context, MDL, memory, CLI/MCP, çok kaynaklı execution) alıp üzerine Cube-tarzı Intent Query dilini, Zenlytic-tarzı dynamic→promote döngüsünü ve Upsolvetarzı Trust katmanını eklemek. LLM’in rolü “SQL yazarı”ndan “niyet seçici / keşif ajanı”na çekilir; tekrarlayan iş semantic compiler + cache ile LLM’siz çalışır. 

**Tek cümlelik ilke:** LLM intent üretir; semantic layer SQL’i deterministik derler; keşif serbestliği promote ile kuruma döner; SaaS tenancy ve RLS compile-time uygulanır. 

## **2. Piyasa Karşılaştırmasının Neticesi** 

#### **2.1 Rakip konumları** 

|**Ürün**|**Güçlü yan**|**Zayıf yan**|**Bizim**<br>**alacağımız**|
|---|---|---|---|
|**WrenAI main**|Açık context, MDL, memory,<br>agent/CLI, çok DB|Klasik UI donmuş; her NL≈LLM SQL;<br>SaaS tenancy zayıf|**Omurga**|
|**Cube.dev**|Deterministik query, pre-agg, RLS,<br>embed|Model kurulum maliyeti; saf text-to-<br>SQL esnekliği düşük|**Compiler +**<br>**cache + RLS**|
|**Zenlytic**|Clarity: SQL + semantic map;<br>explain; promote|Kapalı SaaS; OSS/agent ekosistemi<br>sınırlı|**Dynamic +**<br>**promote +**<br>**explain**|
|**Upsolve**|dbt MetricFlow;<br>Structure/Meaning/Trust; embed<br>agent|dbt bağımlılığı; genel OSS context<br>zayıf|**Trust + golden**<br>**query + eval**|



#### **2.2 Kritik mimari ayrım** 

Text-to-SQL (Wren klasik, Zenlytic Clarity çekirdeği): LLM her seferinde SQL üretir → esnek, pahalı, drift riski. 

Text-to-Semantic-Query (Cube, dbt+agent): LLM measure/dimension/filter seçer → compiler SQL yazar → tutarlı, ucuz tekrar, dar keşif. 

Kazanan hibrit: Varsayılan yol semantic query; keşif yolu kontrollü SQL + dynamic field; başarılı keşif promote ile semantic’e girer. 

Sayfa _1_ / _12_ ·  Temmuz 2026 

**Wren Main Temelli Hibrit GenBI Stratejisi** |  Kurumsal Ölçeklenebilir SaaS  |  Gizli — Strateji Dokümanı 

## **3. Hedef Ürün Tanımı** 

#### **3.1 Vizyon** 

Kurumsal ve ISV müşterilere sunulan, çok kiracılı GenBI SaaS: doğal dil ve agent arayüzleriyle güvenilir SQL, grafik ve dashboard üretir; metrikler tek kaynaktan yönetilir; her cevap açıklanabilir ve denetlenebilir; LLM maliyeti ölçekte kontrol altındadır. 

#### **3.2 Tasarım ilkeleri** 

1. Semantic-first, SQL-second: Varsayılan üretim yolu Intent Query → compiler; serbest SQL istisna ve denetimli. 

2. Wren omurga: MDL, memory, connectors, dry-plan, multi-engine execution Wren core üzerinde kalır. 

3. Promote döngüsü: Dynamic/keşif alanları one-click veya review ile certified metric olur. 

4. Trust by default: Golden queries, eval setleri, regression kapıları, lineage ve “neden bu sayı?”. 

5. SaaS-native: Tenant isolation, RLS compile-time, quota, BYO-LLM, region pin, audit log. 

6. Agent-native: MCP/CLI/API birinci sınıf; UI ikinci sınıf tüketici, tek kaynak değil. 

7. Cost ceiling: Pin, cache, pre-agg ve exact-match memory ile LLM çağrı oranı bilinçli düşürülür. 

## **4. Referans Mimari (Hibrit)** 

#### **4.1 Katmanlar** 

Yukarıdan aşağı: 

1. Experience: Web GenBI UI, embedded SDK, Slack/Teams, MCP agents (Claude, Cursor), public API. 

2. Orchestration (Agent Runtime): Intent sınıflandırma, tool seçimi, multi-step plan, human-inthe-loop. 

3. Context & Memory (Wren): MDL store, instructions.md, queries.yml, LanceDB hybrid recall, schema fetch. 

4. Intent Query Layer (yeni — Cube felsefesi): measures, dimensions, filters, time, order, limit DSL; JSON şema ile kısıtlı. 

5. Semantic Compiler: Intent Query → SQL; join graph, metric math, RLS inject, dialect transpile (Wren Core + genişletme). 

6. Discovery Path (Zenlytic felsefesi): Semantic kapsamazsa kontrollü text-to-SQL + dynamic measure önerisi + explain. 

7. Trust Plane (Upsolve felsefesi): Golden set, online eval, anomaly, promotion workflow, audit. 

8. Execution: Warehouse/DB connectors, result cache, optional pre-aggregations, query governance. 

9. Presentation: Vega-Lite chart gen (sadece gerektiğinde LLM), dashboard pin, export, schedule. 

#### **4.2 İstek yaşam döngüsü (runtime)** 

|**Adım**|**İşlem**|**LLM?**|**Not**|
|---|---|---|---|
|**1. Ingress**|Auth, tenant, quota, PII policy|Hayır|SaaS kontrol düzlemi|



Sayfa _2_ / _12_ ·  Temmuz 2026 

**Wren Main Temelli Hibrit GenBI Stratejisi** |  Kurumsal Ölçeklenebilir SaaS  |  Gizli — Strateji Dokümanı 

|**2. Route**|Exact memory hit / saved dashboard / yeni NL?|Hayır|Hit ise LLM atlanır|
|---|---|---|---|
|**3. Retrieve**|MDL + memory recall + instructions|Embedder (ucuz)|Wren memory|
|**4a. Intent**|NL → Intent Query JSON (şema-kısıtlı)|Evet (küçük)|Varsayılan yol|
|**4b. Discover**|Kapsam dışı → supervised SQL + dynamic field|Evet|İstisna yolu|
|**5. Compile**|Intent → SQL + RLS + dialect|Hayır|Deterministik|
|**6. Validate**|Dry-plan, policy, cost estimate|Hayır|Wren dry-plan|
|**7. Execute**|Warehouse; cache/pre-agg tercih|Hayır|Veri LLM’e gitmez|
|**8. Present**|Tablo; chart (spec cache veya LLM); explain|Chart’ta bazen|Pin sonrası LLM yok|
|**9. Learn**|Store memory; promote adayı; eval skor|Hayır|Trust plane|



#### **4.3 Intent Query (örnek sözleşme)** 

LLM çıktısı serbest SQL değil, doğrulanabilir JSON olmalıdır. Örnek alanlar: measures[], dimensions[], filters[], timeRange, orderBy[], limit, chartHint. Şema dışı alan reddedilir; bilinmeyen measure → Discovery Path veya “metrik yok” cevabı. Bu, Cube Query modelinin Wren MDL üzerine uyarlanmış halidir. 

#### **4.4 Wren main’den devralınan bileşenler** 

- **core/wren-mdl:** Metrik ve model şeması; tek kaynak JSON Schema. 

- **core/wren (CLI) + memory:** Index, recall, store; agent skill yüzeyi. 

- **core connectors + dry-plan:** 20+ kaynak, doğrulama, execution. 

- **MCP / skills:** Harici agent’ların aynı context’e bağlanması. 

Legacy GenBI UI (v1-final) yalnızca referans UX ve chart davranışları için incelenir; production UI yeniden, semantic-first olacak şekilde yazılır. 

## **5. Rakiplerden Üstünlük Matrisi** 

|**Yetenek**|**Wren yalnız**|**Cube**|**Zenlytic**|**Upsolve**|**Hibrit hedef**|
|---|---|---|---|---|---|
|Açık OSS core|Evet|Core evet|Hayır|Hayır|**Evet + SaaS**|
|Deterministik metrik SQL|Kısmi|Güçlü|Hibrit|MetricFlow|**Intent compiler**|
|Keşif + promote|Zayıf|Zayıf|Güçlü|Orta|**Güçlü**|
|Memory / tribal<br>knowledge|Güçlü|Sınırlı|Memories|Golden|**Wren memory+**|
|Eval / Trust plane|Gelişmekte|Sınırlı|Orta|Güçlü|**Birinci sınıf**|
|Multi-tenant RLS SaaS|Zayıf|Güçlü|SaaS içi|Embed odaklı|**Compile-time RLS**|
|LLM maliyet kontrolü|Zayıf|İyi|Orta|Orta|**Route+cache+pin**|
|Agent / MCP|Güçlü|MCP var|Sınırlı|Agent Studio|**Birinci sınıf**|
|Chart / dashboard|Legacy iyi|Workbench|Ürün UI|Embed|**Vega+pin+API**|



## **6. SaaS Ölçeklenebilirlik Tasarımı** 

#### **6.1 Çok kiracılık** 

- Control plane: org, workspace, kullanıcı, rol, faturalama, feature flag. 

- Data plane: tenant_id her Intent Query ve SQL’e compile-time enjekte (Cube RLS modeli). 

- MDL ve memory tenant-scoped; cross-tenant retrieval yok. 

Sayfa _3_ / _12_ ·  Temmuz 2026 

**Wren Main Temelli Hibrit GenBI Stratejisi** |  Kurumsal Ölçeklenebilir SaaS  |  Gizli — Strateji Dokümanı 

- Warehouse bağlantıları: müşteri WH (prefer) veya managed duckdb/slot; credentials KMS. 

#### **6.2 Performans ve maliyet** 

- Result cache (sorgu imzası + tenant + TTL). 

- Pre-aggregation job’ları sık kullanılan Intent Query’ler için (opsiyonel, Cube pre-agg benzeri). 

- Exact NL hash → stored SQL/Intent bypass LLM. 

- Semantic hit oranı KPI: hedef %70+ sorgu Intent path; Discovery < %30. 

- Chart spec cache: aynı Intent + result shape → Vega yeniden üretilmez. 

#### **6.3 Güvenlik ve uyumluluk** 

- SOC2 yol haritası; audit log (kim, hangi intent, hangi SQL, satır sayısı). 

- BYO-LLM ve region pin; veri residency. 

- Row/column policy MDL’de; compiler zorunlu uygular. 

- PII sınıflandırma ve prompt redaksiyon (ham satır LLM’e gitmez). 

#### **6.4 API yüzeyi** 

- /v1/ask — NL → answer + explain + optional chart 

- /v1/intent — NL → Intent Query (dry) 

- /v1/query — Intent Query → data 

- /v1/promote — dynamic field review API 

- MCP server — agent tool’ları (wren skills ile hizalı) 

- Embed SDK — JWT tenant scoped charts/dashboards 

## **7. Ürün Yetenekleri (MVP → Ölçek)** 

#### **7.1 MVP (0–4 ay)** 

- Wren main core + tenant-aware MDL store 

- Intent Query şeması + LLM constrained decode + compiler (temel measure/dim/filter/time) 

- Discovery fallback + explain metni 

- Memory recall/store; pin dashboard; Vega chart (cached) 

- Tek bölge SaaS; Postgres/DuckDB/BigQuery connector alt kümesi 

- Eval harness: 100 golden NL→Intent→SQL 

#### **7.2 v1 (4–9 ay)** 

- Promote workflow (UI + API); role-based publish 

- Pre-agg ve akıllı cache; cost governor 

- RLS politikaları; embed SDK; Slack bot 

- dbt MetricFlow import (Upsolve parity) 

- Online eval + regression gate CI 

#### **7.3 v2 (9–18 ay)** 

- Multi-region; advanced pre-agg; workbook/AI dashboard agent 

Sayfa _4_ / _12_ ·  Temmuz 2026 

**Wren Main Temelli Hibrit GenBI Stratejisi** |  Kurumsal Ölçeklenebilir SaaS  |  Gizli — Strateji Dokümanı 

- Automated semantic suggestion from query logs 

- Marketplace connectors; on-prem bridge 

## **8. Uygulama Yol Haritası ve Organizasyon** 

#### **8.1 Fazlar** 

1. Faz 0 — Karar ve çatal: Wren main submodule/fork politikası; lisans (Apache core + SaaS proprietary control plane); rakip patent/claim taraması. 

2. Faz 1 — Intent Layer: JSON şema, prompt + constrained generation, compiler prototipi, 50 golden test. 

3. Faz 2 — Trust & Promote: review kuyruğu, eval CI, memory quality metrics. 

4. Faz 3 — SaaS control plane: tenancy, billing, RLS, embed. 

5. Faz 4 — Experience: yeni GenBI UI (legacy’den UX dersi); agent skill paketi. 

6. Faz 5 — Scale: pre-agg, multi-region, enterprise SSO/SCIM. 

#### **8.2 Ekip iskeleti (öneri)** 

- Platform: Wren core, compiler, connectors 

- AI: Intent gen, eval, prompt/schema 

- Semantic & Trust: MDL tooling, promote, golden sets 

- SaaS: identity, billing, tenancy, observability 

- Product/UX: chat, explain, dashboard, embed 

#### **8.3 KPI’lar** 

- Intent path oranı ≥ %70 

- Golden set execution accuracy ≥ %95 (covered metrics) 

- P95 latency Intent path < 3s (cache hariç compiler+WH) 

- LLM cost / active workspace ay bazında azalan trend 

- Promote edilen dynamic field’ların production kullanım oranı 

- NRR ve embed customer expansion 

## **9. Riskler ve Azaltma** 

|**Risk**|**Etki**|**Azaltma**|
|---|---|---|
|Wren main hızlı değişir / API<br>kırılır|Yüksek|Vendor-adapter katmanı; pinlenmiş core versiyon; upstream katkı|
|Intent şeması yetersiz kalır|Yüksek|Discovery path + promote; şema versiyonlama|
|LLM maliyeti ölçekte patlar|Orta|Route-before-LLM; cache; küçük model intent; pin|
|Yanlış metrik / güven kaybı|Kritik|Explain zorunlu; golden CI; human promote|
|Çok kiracı veri sızıntısı|Kritik|Compile-time RLS; pen-test; tenant isolation testleri|
|Cube/Zenlytic feature parity<br>baskısı|Orta|Farklılaşma: açık agent + promote + trust; gömülü OSS hikaye|



Sayfa _5_ / _12_ ·  Temmuz 2026 

**Wren Main Temelli Hibrit GenBI Stratejisi** |  Kurumsal Ölçeklenebilir SaaS  |  Gizli — Strateji Dokümanı 

## **10. Go-to-Market Farklılaşması** 

- **Açık context + kurumsal SaaS:** Rakipler ya kapalı ya da sadece semantic API. Siz ikisini birleştirirsiniz. 

- **Agent-first:** Claude/Cursor/MCP ile aynı certified metrics; UI tek kanal değil. 

- **Promote ekonomisi:** Data team bottleneck’i dynamic→certified ile ölçeklenir (Zenlytic’den açık ve API’li). 

- **Trust skoru:** Her cevapta confience + lineage + golden overlap (Upsolve’dan ürünleştirilmiş). 

- **Maliyet şeffaflığı:** Müşteriye Intent vs Discovery oranı ve LLM spend gösterilir — satış argümanı. 

## **11. Sonuç ve Karar** 

En verimli ve mantıklı strateji, WrenAI main’i terk etmek değil; onu semantic-first compiler ve trust düzlemi ile tamamlamaktır. Böylece: 

- Cube’un tutarlılık ve SaaS embed gücüne yaklaşırsınız 

- Zenlytic’in keşif ve promote deneyimini açık API ile geçersiniz 

- Upsolve’un dbt/trust disiplinini generic MDL + eval ile genelleştirirsiniz 

- Wren’in agent/memory/connector avantajını kaybetmezsiniz 

Kurumsal ölçeklenebilir SaaS için başarı formülü: 

###### **Wren Core (context + execute) + Intent Query Compiler (determinizm) + Discovery/Promote (esneklik) + Trust Plane (güven) + Tenant/RLS/Cache (SaaS).** 

Bu hibrit, tek ürünün optimize ettiği bir ekseni değil; production GenBI’nin dört eksenini birden hedefler. Uygulama disiplini (golden set, Intent oranı KPI, promote review) olmadan mimari tek başına yetmez; KPI’lar ürünün “piyasadakilerden daha iyi” iddiasının ölçülebilir kanıtı olmalıdır. 

#### **11.1 Hemen yapılacaklar (30 gün)** 

1. Wren main’den MDL + memory + dry-plan ile dahili POC; 20 gerçek iş sorusu. 

2. Intent Query JSON şeması v0 ve 20 sorunun elle Intent’e map’i. 

3. Basit compiler: 5 measure / 5 dimension → SQL; golden test CI iskeleti. 

4. Discovery fallback prototipi ve explain şablonu. 

5. SaaS tenancy veri modeli taslağı (org/workspace/tenant_id). 

6. Bu dokümandaki KPI baseline ölçümü. 

### **KURUMSAL GenBI SaaS — TAM MANTIK VE ÖZELLİK KİTABI** 

Wren Main Omurga · Cube Compiler Disiplini · Zenlytic Promote · Upsolve Trust _Her özellik: ne işe yarar · nasıl çalışır · geliştirici logic · avantaj · rakip kıyası_ 

Bu doküman geliştiriciye ürünün neden böyle tasarlandığını, her bileşenin runtime davranışını ve rakiplere (Wren yalnız, Cube, Zenlytic, Upsolve) göre üstünlüğünü açıklar. Uygulama kararı verirken “ne kodlamalıyım?” kadar “neden bu sıra?” sorusuna da cevap verir. 

Sayfa _6_ / _12_ ·  Temmuz 2026 

**Wren Main Temelli Hibrit GenBI Stratejisi** |  Kurumsal Ölçeklenebilir SaaS  |  Gizli — Strateji Dokümanı 

### **1. Ürünün ana logic’i (neden bu mimari?)** 

##### **1.1 Problem** 

Saf text-to-SQL (klasik Wren ask yolu): Her yeni cümle LLM’e gider, SQL uydurulur. Esnektir ama (a) her seferinde maliyet/latency, (b) “revenue” tanımı prompt’a bağlı kayar, (c) audit zordur, (d) multi-tenant RLS’i SQL string’ine sonradan eklemek risklidir. 

Saf semantic-only (klasik Cube AI): LLM yalnızca measure/dimension seçer, compiler SQL yazar. Tutarlı ve ucuz tekrardır ama semantic’te olmayan soru cevaplanamaz; kurulum yavaştır; keşif boğulur. 

Zenlytic Clarity: SQL esnekliği + semantic map + dynamic promote — doğru yön; kapalı ürün. Upsolve: trust/golden/dbt — doğru operasyon disiplini; generic açık context zayıf. 

##### **1.2 Bizim logic** 

Varsayılan yol Intent Query (Cube disiplini). Semantic kapsamazsa Discovery (kontrollü SQL + dynamic draft). İyi keşif Promote ile certified metric olur (Zenlytic). Her cevap Trust düzlemine (golden/eval) bağlanır (Upsolve). Context ve execution Wren main’den gelir. Tekrarlayan pin/dashboard LLM’siz çalışır. 

**Özet formül:** LLM = niyet seçici (ve nadiren keşif yazarı). Compiler = tek doğru SQL. Memory = few-shot ve exact bypass. Promote = semantic’i büyütür. RLS = compile-time. Cache = maliyeti keser. 

### **2. Mimari katmanlar — tek tek** 

###### **2.1 Experience katmanı (Web UI, Embed, MCP, API)** 

**Ne işe yarar:** Kullanıcı ve agent’ın ürüne dokunduğu yüzey. Chat, dashboard, modelleme ekranı, gömülü iframe, Claude/Cursor MCP araçları, public REST. 

**Nasıl çalışır:** Tüm yüzeyler aynı Ask/Query API’yi çağırır. UI özel iş mantığı barındırmaz; sadece path badge (Intent/Discovery/Cache), explain paneli, pin ve promote inbox gösterir. MCP tool’ları API’nin ince sarmalayıcısıdır. 

**Geliştirici logic:** apps/web → /v1/ask; packages/mcp-server tool listesi = list_metrics, parse_intent, run_intent, dry_plan, memory_recall, store_example. Embed JWT içinde workspace_id + row scope claim taşır. 

**Avantaj:** Tek backend, çok kanal: BI kullanıcısı ve coding agent aynı certified metric’i görür. Destek yükü ve “Slack’te başka sayı” problemi azalır. 

**Rakiplere kıyas:** Wren legacy UI donmuş ve agent-native değil. Cube MCP/API güçlü ama keşif/promote zayıf. Zenlytic UI güçlü, MCP/açık API zayıf. Biz hem insan UI hem agent-first. 

###### **2.2 Orchestration / Ask state machine** 

**Ne işe yarar:** Tek bir doğal dil isteğini doğru yola (cache, intent, discovery) yönlendirip sonucu paketlemek. 

**Nasıl çalışır:** Sıra sabit: Ingress → Route → Retrieve → Intent|Discovery → Validate → Execute → Present → Learn. Route adımı exact NL hash veya pin id görürse LLM’e hiç gitmez. 

**Geliştirici logic:** AskHandler içinde explicit state enum; her geçişte trace_id, path, llm_tokens loglanır. Timeout: LLM 30s, warehouse 60s. Idempotency-Key ile çift submit güvenli. 

**Avantaj:** Maliyet ve latency kontrolünün tek noktası. “Her prompt LLM” tuzağını kırar. Debug edilebilir, test edilebilir akış. 

**Rakiplere kıyas:** Klasik Wren ask pipeline’ı çoğunlukla her soruda generation. Cube chat her soruda model query gen (yine LLM) ama SQL değil. Biz route-first ile ikisinden de ucuz path ekleriz. 

###### **2.3 Context & Memory (Wren omurga)** 

**Ne işe yarar:** İş anlamını (MDL, talimatlar, geçmiş doğru NL→SQL) saklayıp soruya ilgili dilimleri getirmek. 

**Nasıl çalışır:** MDL published revision workspace’e bağlıdır. Memory: embedding + keyword hybrid recall (LanceDB veya pgvector). instructions.md eşdeğeri DB’de instruction kayıtları. Başarılı/onaylı sorular store edilir. 

**Geliştirici logic:** Retrieve sadece top-k şema kartı + few-shot örnek döner; ham tablo dump etmez. index job worker’da; ask path’i bloklamaz. Tenant partition zorunlu. 

**Avantaj:** LLM’e giden context küçülür, doğruluk artar, PII sızıntı riski düşer. Zamanla sistem “öğrenir” ama exact cache kadar ucuz değildir — ikisi birlikte kullanılır. 

**Rakiplere kıyas:** Wren’in en güçlü yanı; Cube’da zayıf; Zenlytic Memories benzeri ama kapalı; Upsolve golden’a yakın. Biz Wren memory’yi SaaS multi-tenant yaparız. 

###### **2.4 Intent Query Layer** 

**Ne işe yarar:** Doğal dili serbest SQL yerine dar, doğrulanabilir bir JSON niyet diline çevirmek. 

Sayfa _7_ / _12_ ·  Temmuz 2026 

**Wren Main Temelli Hibrit GenBI Stratejisi** |  Kurumsal Ölçeklenebilir SaaS  |  Gizli — Strateji Dokümanı 

**Nasıl çalışır:** LLM tool-call / constrained decode ile yalnızca şema alanlarını doldurur: measures, dimensions, filters, time, orderBy, limit, chartHint, confidence. Validator MDL’deki adlarla karşılaştırır; unknown → Discovery veya hata. 

**Geliştirici logic:** packages/intent: JSON Schema + zod/ajv; provider’a function schema ver; output’u reject-oninvalid. confidence < eşik ise orchestration Discovery’ye sapabilir. 

**Avantaj:** SQL hallucination yüzeyi daralır. Aynı niyet her zaman aynı compiler çıktısına gider → “tek sayı”. Test yazması kolay (intent fixture). 

**Rakiplere kıyas:** Birebir Cube Query felsefesi. Wren klasik text-to-SQL’den bilinçli sapma. Zenlytic yeni Clarity SQL-first’e kaydı; biz varsayılanı intent tutup SQL’i istisna yapıyoruz — maliyet/tutarlılık için daha iyi. 

###### **2.5 Semantic Compiler** 

**Ne işe yarar:** Intent JSON’u diyalekt SQL’ine, join’leri ve metrik matematiğini MDL’den alarak, RLS ile birlikte üretmek. 

**Nasıl çalışır:** MDL graph’ta measure’ın model’inden dimensions’a join yolu seçilir; metric expression expand edilir; filter/time parametreli predicate olur; tenant RLS AND ile eklenir; dialect renderer SQL string + params üretir. cache_key = hash(intent normalized + mdl version + tenant policies). 

**Geliştirici logic:** Fan-out / symmetric aggregate kuralları test suite’te. Compiler asla RLS’i opsiyonel bırakmaz. Çıktı: { sql, params, meta }. dry-plan Wren bridge ile doğrulanır. 

**Avantaj:** Deterministik: aynı intent → aynı SQL. Güvenlik compile-time. Pre-agg ve cache anahtarı stabil. LLM’e SQL düzelttirme döngüsü azalır. 

**Rakiplere kıyas:** Cube compiler parity. Wren engine execute/validate sağlar ama “intent DSL→SQL” katmanı Cube’dan alınır. Zenlytic Bridge SQL’i sonradan map eder; biz önce map’li dünyada üretiriz. 

###### **2.6 Discovery Path** 

**Ne işe yarar:** Semantic’in henüz kapsamadığı soruları cevaplamak; yeni metrik adayları üretmek; keşfi öldürmemek. 

**Nasıl çalışır:** Tetik: unknown measure, düşük confidence, veya mode=discovery. LLM’e MDL özeti + “certified listesi ile çelişme” kuralı + soru verilir. Çıktı SQL + dynamic_measures draft + assumptions[]. Zorunlu dry-plan ve cost tavanı. UI/API’de certified=false. 

**Geliştirici logic:** packages/discovery ayrı prompt ve parser. Başarı sonrası promote_candidates kuyruğu. Production default auto modda Intent dener, fail olursa Discovery (feature flag ile sıkılaştırılabilir). 

**Avantaj:** Kurulum bitmeden ürün kullanılabilir. Data team her soruyu önceden modellemek zorunda kalmaz. Yine de “bu sayı certified değil” şeffaflığı korunur. 

**Rakiplere kıyas:** Zenlytic Clarity/dynamic’in açık ve API’li hali. Cube’un zayıf noktası. Saf Wren her şeyi discovery yapar — biz onu bilinçli istisna yaparız. 

###### **2.7 Trust Plane** 

**Ne işe yarar:** Cevap kalitesini ölçmek, regresyonu engellemek, golden örneklerle agent’ı disipline etmek. 

**Nasıl çalışır:** golden_cases: question + expected intent ve/veya SQL. eval runner CI ve periyodik job. Skorlar: intent_exact, sql_equiv, row_match. Düşüşte merge kırılır. query_runs özellikleri online analiz için loglanır. 

**Geliştirici logic:** packages/trust; apps/worker eval job. PR check zorunlu. Workspace başına golden set. Promote approve öncesi ilgili golden’lar da koşturulabilir. 

**Avantaj:** “Demo’da çalışır prod’da bozulur” riskini düşürür. Satışta doğruluk iddiası kanıtlanır. Model/prompt değişince güvenlik ağı olur. 

**Rakiplere kıyas:** Upsolve golden/eval disiplininin platforma gömülmüş hali. Wren ve Cube’da second-class. Zenlytic review var ama açık eval CI vurgusu bizde daha sert. 

###### **2.8 Execution (Wren bridge + cache + preagg)** 

**Ne işe yarar:** SQL’i doğru depoda çalıştırmak; tekrarları ucuzlatmak; Wren core yeteneklerini izole tüketmek. 

**Nasıl çalışır:** wren-bridge dry-plan + execute. Sonuç cache: cache_key hit ise WH’ye gitme. preagg_specs: sık intent pattern’leri için materialized rollup job. Pin refresh path=pin, llm_tokens=0. 

**Geliştirici logic:** Adapter pattern: Wren sürüm pin. Hata structured. Cost governor: tahmini tarama > limit ise reddet veya onay iste. 

**Avantaj:** 20+ kaynak potansiyeli Wren’den; performans Cube preagg/cache’ten. LLM maliyeti execution’dan ayrılır. 

**Rakiplere kıyas:** Wren connectors + Cube performance habits. Tek başına Wren her seferinde pahalı path; tek başına Cube model yükü yüksek — hibrit ikisini böler. 

Sayfa _8_ / _12_ ·  Temmuz 2026 

**Wren Main Temelli Hibrit GenBI Stratejisi** |  Kurumsal Ölçeklenebilir SaaS  |  Gizli — Strateji Dokümanı 

###### **2.9 Presentation (Chart + Dashboard)** 

**Ne işe yarar:** Sonucu tablo ve grafikle göstermek; kaydedip paylaşmak. 

**Nasıl çalışır:** Chart: rule-based fallback (time→line, category→bar) veya LLM Vega-Lite; spec şema validate; cache by intent fingerprint. Dashboard pin sadece query/intent id tutar; refresh re-execute. PNG/SVG export client veya server render. 

**Geliştirici logic:** packages/charts. UI Chart tab legacy Wren UX’ten esinlenir ama API-first. Embed aynı pin’i JWT ile gösterir. 

**Avantaj:** Kullanıcı “soru sordum grafik geldi” deneyimi. Pin sonrası LLM yok → ölçekte ucuz. Agent da aynı chart API’yi kullanabilir. 

**Rakiplere kıyas:** Wren legacy chart güçlü referans. Cube workbooks. Zenlytic ürün içi viz. Biz Vega + pin + embed + agent ortak modeli. 

### **3. Kritik özellikler — derin mantık** 

###### **3.1 MDL (Modeling Definition Language)** 

**Ne işe yarar:** İş dilinde modeller, ilişkiler, metrikler, erişim kurallarının tek kaynağı. Agent ve compiler ham DDL yerine MDL okur. 

**Nasıl çalışır:** YAML/JSON revision’lar; draft→publish. Publish version++ ve cache invalidation. Metric: name, expression, model, grain. Relationship: from/to, type. RLAC/CLAC alanları compiler’a policy üretir. dbt MetricFlow import SHOULD. 

**Geliştirici logic:** mdl_revisions.content_jsonb; validator packages/mdl. UI editor + graph. API publish audit log. 

**Avantaj:** “Revenue nedir?” toplantı tartışması biter. AI ve BI aynı tanımı kullanır. Git-friendly governance mümkün. 

**Rakiplere kıyas:** Wren MDL + Cube data model + dbt metrics birleşimi. Zenlytic kendi layer’ı. Biz MDL’yi hem insan hem Intent hem RLS için merkez yaparız. 

###### **3.2 Exact-match ve Intent cache (LLM bypass)** 

**Ne işe yarar:** Aynı veya normalize edilmiş soruyu tekrar LLM’e sokmamak. 

**Nasıl çalışır:** nl_hash = normalize(question)+mdl_version+workspace. Hit → stored intent/sql. Pin id → doğrudan execute. Learn adımı başarılı run’ı cache’e yazar. 

**Geliştirici logic:** intent_cache tablosu; Route state ilk bakış. Normalize: lower, trim, sayısal tarih kanonikleştirme opsiyonel. 

**Avantaj:** Dashboard ve tekrar sorularda latency ve fatura çöker. Kullanıcı “her tıklamada AI bekliyorum” şikayetini keser. 

**Rakiplere kıyas:** Hiçbir rakip bunu ürünün merkez KPI’sı kadar vurgulamaz. Wren her prompt’ta gen yatkın; Cube query cache var ama NL hash route ayrı tasarlanmalı — biz zorunlu kılıyoruz. 

###### **3.3 Promote (dynamic → certified)** 

**Ne işe yarar:** Keşifte doğan iyi metrik tanımını kalıcı MDL’ye yükseltmek; semantic’i kullanımla büyütmek. 

**Nasıl çalışır:** Discovery dynamic_measures → promote_candidates (pending). Analyst approve → metric_patch MDL draft’a merge → publish. Reject not ile kapanır. İsteğe bağlı golden ekleme. 

**Geliştirici logic:** RBAC: sadece admin/analyst approve. Diff UI. API: approve endpoint. Event: mdl_published. 

**Avantaj:** Data team bottleneck’i azalır: her şeyi önceden modellemek yerine “kullanımdan öğren + onayla”. Semantic coverage zamanla artar, Discovery oranı düşer (hedef KPI). 

**Rakiplere kıyas:** Zenlytic’in en değerli operasyon döngüsü; biz API + audit + eval ile kurumsal hale getiririz. Cube’da yok. Wren’de yok. 

###### **3.4 Explain** 

**Ne işe yarar:** Kullanıcıya sayının neden doğru (veya certified olmadığı) bilgisini göstermek; güven oluşturmak. **Nasıl çalışır:** Intent path: hangi measures/dimensions, hangi MDL version, hangi filtreler. Discovery: assumptions[], tables used, certified=false. UI yan panel; API explain object. 

**Geliştirici logic:** Compiler meta + discovery assumptions birleşimi. i18n hazır yapı. “Show SQL” ayrı toggle (rol bazlı). 

**Avantaj:** Self-serve adoption artar; data team “her sayıyı elle doğrula” yükünden kurtulur. Compliance hikayesi güçlenir. 

**Rakiplere kıyas:** Zenlytic vurgu alanı. Cube “named metrics” ile dolaylı explain. Wren SQL breakdown kısmen. Biz her path’te zorunlu explain. 

Sayfa _9_ / _12_ ·  Temmuz 2026 

**Wren Main Temelli Hibrit GenBI Stratejisi** |  Kurumsal Ölçeklenebilir SaaS  |  Gizli — Strateji Dokümanı 

###### **3.5 RLS compile-time** 

**Ne işe yarar:** Çok kiracılı ve satır seviyesinde yetkiyi SQL üretiminin içine gömmek; sonradan filtre unutma riskini yok etmek. 

**Nasıl çalışır:** MDL veya policy store’dan tenant/user predicate şablonu. Compiler her SQL’e AND ekler. Test: tenant A token ile tenant B workspace → 0 row veya 403. 

**Geliştirici logic:** Policy escape hatch yok. Admin “bypass RLS” ayrı audit’li endpoint (opsiyonel, default kapalı). 

**Avantaj:** Embed ve müşteriye açık agent için olmazsa olmaz. Güvenlik review’dan geçme şansı artar. 

**Rakiplere kıyas:** Cube’un güçlü yanı; Wren MDL RLAC var ama SaaS multi-tenant enforcement bizde ürünleşir. Zenlytic/Upsolve kapalı tarafta. 

###### **3.6 Chart generation logic** 

**Ne işe yarar:** Sonuç setinden uygun görselleştirme üretmek. 

**Nasıl çalışır:** Önce rule-based: zaman boyutu+metrik→line; kategorik+metrik→bar; tek metrik oran→pie; aksi table. Yetersizse LLM Vega-Lite; JSON schema validate. Cache: aynı fingerprint tekrar LLM çağırmaz. Pin refresh chart spec’i saklar veya yeniden rule-based uygular. 

**Geliştirici logic:** packages/charts; invalid Vega → fallback table. Export PNG/SVG. 

**Avantaj:** Kullanıcı değeri yüksek; LLM maliyeti kontrollü (cache+rules). Agent’a da aynı endpoint. 

**Rakiplere kıyas:** Wren legacy Vega yolu. Cube viz workbench. Biz rule-first ile Zenlytic/Wren’e göre daha az LLM chart çağrısı. 

###### **3.7 MCP / Agent-native yüzey** 

**Ne işe yarar:** Coding agent ve dış LLM’lerin certified metrics ile konuşması; UI tek kanal olmasın. 

**Nasıl çalışır:** MCP server tool’ları tenant auth ile. Agent list_metrics ile keşfeder, parse_intent + run_intent ile sorar, store_example ile memory’ye ekler. Skills markdown (Wren tarzı) onboarding için. 

**Geliştirici logic:** packages/mcp-server; OAuth veya API key. Tool input şemaları Intent ile aynı dili konuşur. 

**Avantaj:** 2026 agent ekosisteminde dağıtım kanalı. “Claude’a sor, aynı sayı” satılır. Geliştirici ekibi kendi iç agent’ını bağlar. 

**Rakiplere kıyas:** Wren skills/MCP yönelimi + Cube MCP. Zenlytic zayıf. Upsolve Agent Studio kapalı. Biz açık tool sözleşmesi. 

###### **3.8 dbt MetricFlow import (SHOULD)** 

**Ne işe yarar:** Zaten dbt kullanan ekiplerin metriklerini yeniden yazmadan içeri almak. 

**Nasıl çalışır:** YAML/MetricFlow parse → MDL metrics/models map. Conflict’te diff UI. Periyodik sync job opsiyonel. 

**Geliştirici logic:** packages/mdl importer. Test fixture ile dbt örnek repo. 

**Avantaj:** Adoption sürtünmesi düşer; Upsolve’un dbt avantajı nötralize edilir. 

**Rakiplere kıyas:** Upsolve native. Cube dbt entegrasyonu. Wren ayrı MDL. Biz köprü. 

### **4. Runtime senaryoları (geliştirici için)** 

###### **Senaryo A — İlk kez sorulan, MDL’de olan metrik** 

Route miss → Retrieve MDL+memory → LLM Intent JSON → validate OK → compile SQL+RLS → dry-plan → execute → chart rule/LLM → learn store. path=intent. llm_tokens > 0 bir kez. 

###### **Senaryo B — Aynı soru ikinci kez** 

Route nl_hash hit → execute veya stored rows policy → present. path=cache. llm_tokens=0. 

###### **Senaryo C — Pin dashboard sabah açılışı** 

GET refresh → compile/execute or cache → path=pin. LLM yok. 

###### **Senaryo D — MDL’de olmayan “kargo gecikme skoru”** 

Intent unknown → Discovery SQL+dynamic draft → explain certified=false → kullanıcı faydalı bulursa promote → admin approve → sonraki sorular Intent path. 

###### **Senaryo E — Agent (Claude) MCP** 

list_metrics → parse_intent → run_intent → aynı compiler/RLS. UI ile sayı parity zorunlu test. 

Sayfa _10_ / _12_ ·  Temmuz 2026 

**Wren Main Temelli Hibrit GenBI Stratejisi** |  Kurumsal Ölçeklenebilir SaaS  |  Gizli — Strateji Dokümanı 

###### **Senaryo F — Kötü niyetli cross-tenant** 

Token workspace B, query workspace A id → 403. RLS test suite kırmızıya düşmeden release yok. 

### **5. Veri modeli ve API (özet referans)** 

Tablolar: orgs, workspaces, users, memberships, api_keys, connections, mdl_revisions, memory_items, intent_cache, query_runs, charts, dashboard_pins, promote_candidates, golden_cases, eval_runs, audit_logs, preagg_specs. Hepsi workspace/org scope. 

Ana API: POST /v1/ask, /v1/intent/parse, /v1/query, /v1/query/dry, MDL CRUD/publish, memory index/recall/store, promote approve, charts/generate, dashboards refresh, golden+eval, MCP tools. Ask cevabında path, explain, metrics.latency_ms, metrics.llm_tokens, metrics.cache_hit zorunlu — bu alanlar ürün KPI’sıdır. 

##### **5.1 Intent JSON (uygulama sözleşmesi)** 

<mark>{ "version":"0.1", "measures":[{"name":"revenue","agg":"sum"}],</mark> 

"dimensions":["region"], "filters":[{"field":"status","op":"eq","value":"paid"}], 

"time":{"field":"ordered_at","grain":"month","range":{"start":"-12m","end":"now"}}, "orderBy":[{"field":"revenue","dir":"desc"}], "limit":50, "chartHint":"bar", "confidence":0.86 } 

### **6. Monorepo modülleri — ne kodlanır, neden** 

1. **packages/intent:** Şema, LLM tool tanımları, reject-on-invalid. Neden ayrı: provider değişince orchestration dokunulmaz. 

2. **packages/compiler:** Join, metric expand, RLS, dialect. Neden ayrı: en kritik doğruluk; pure functions + golden SQL snapshot test. 

3. **packages/discovery:** SQL fallback prompt. Neden ayrı: Intent’ten daha riskli; feature flag ile kapatılabilir. 

4. **packages/memory:** Wren-uyumlu index/recall/store. Neden ayrı: vektör backend değişebilir. 

5. **packages/trust:** Golden + eval. Neden ayrı: CI’dan çağrılır, API’den çağrılır. 

6. **packages/charts:** Vega + rules + cache. Neden ayrı: UI ve API ortak. 

7. **packages/wren-bridge:** Core pin + execute/dry-plan. Neden ayrı: upstream kırılganlığı izole. 

8. **packages/auth:** JWT, API key, RBAC. Neden ayrı: tüm apps ortak. 

9. **apps/api:** State machine + OpenAPI. 

10. **apps/worker:** index, eval, preagg, promote notify. 

11. **apps/web:** Ask, Model, Promote, Dashboard, Eval — logic’siz ince istemci. 

12. **packages/mcp-server + sdk-js:** Agent ve embed dağıtımı. 

### **7. Sprint planı (kabul kriterli)** 

Sprint 0: monorepo, CI, auth, workspace CRUD — JWT ile 200. 

S1–2: MDL revisions + wren-bridge DuckDB — sample SELECT çalışır. 

S3–4: Intent+compiler, 30 golden intent→SQL — exact ≥ %90, execute OK. 

S5: memory + nl_hash cache — ikinci soru llm_tokens=0 veya few-shot. 

S6–7: Discovery+explain — unknown metrikte certified=false. 

S8: charts+pin — refresh path=pin, llm_tokens=0. 

S9: trust CI — eval kırmızıysa merge yok. 

S10–11: promote UI/API + Ask UI — approve sonrası metric listede. 

S12: RLS + Postgres/BigQuery — cross-tenant 0 row. 

S13–14: MCP+SDK embed — Claude E2E run_intent. 

S15–16: cost governor, preagg v0, load test — p95 intent < 3s warm. 

### **8. KPI’lar (ürünün “daha iyi” kanıtı)** 

1. Intent path oranı ≥ %70 (Discovery azalır = promote çalışıyor) 

2. Covered golden accuracy ≥ %95 

Sayfa _11_ / _12_ ·  Temmuz 2026 

**Wren Main Temelli Hibrit GenBI Stratejisi** |  Kurumsal Ölçeklenebilir SaaS  |  Gizli — Strateji Dokümanı 

   3. Pin/cache isteklerinde llm_tokens toplamı ≈ 0 

   4. P95 intent path latency < 3s (warm) 

   5. Cross-tenant isolation test %100 yeşil 

6. LLM cost / active workspace azalan trend 

Bu KPI’lar rakiplere karşı somut iddiadır: Cube kadar tutarlı covered alanda; Zenlytic kadar açıklanabilir keşifte; Wren kadar agent-native; Upsolve kadar eval disiplinli — ölçülerek. 

### **9. Riskler ve non-goals** 

13. **Risk Wren upstream kırılması:** wren-bridge pin + adapter test. 

14. **Risk Intent şeması yetmez:** Discovery + şema versioning + promote. 

15. **Risk LLM faturası:** Route-first, small model intent, cache, pin. 

16. **Risk yanlış sayı:** Explain + golden CI + human promote. 

17. **Non-goal MVP:** Legacy UI fork; her diyalektte perfect symmetric agg; autonomous promote without human; production default unlimited text-to-SQL. 

### **10. Geliştiriciye son talimat** 

Önce Intent şeması ve compiler golden testlerini yeşile çekin. Ask state machine’i path alanını zorunlu loglayacak şekilde yazın. RLS testini release gate yapın. UI’yi ince tutun. Wren’i köprüleyin, forklamayın. Her PR’de eval. Promote’u ikinci sınıf bırakmayın — Discovery oranını düşüren tek ürün mekanizması odur. 

Başarı: Kullanıcı yeni soruda hızlı ve tutarlı cevap alır; tekrarında AI beklemez; data team promote kuyruğundan semantic’i büyütür; agent aynı sayıyı üretir; fatura Intent oranıyla kontrol altında kalır. 

- v3 Mantık & Özellik Kitabı sonu — 

Sayfa _12_ / _12_ ·  Temmuz 2026 

