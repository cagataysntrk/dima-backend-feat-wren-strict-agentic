# Dima — 13 Kritik UX/Analitik Bulgu: Kök-Neden Araştırması ve Tam Yol Haritası

## Uygulama Durumu (1 Ağustos 2026 — canlı güncellenir)

**Faz 0 + Faz A + Faz F + C1 + E(kısmi) + B(TAMAMI, konu/thread modeli dahil):
TAMAMLANDI, test edildi, doğrulandı.** Yalnız §D + C2 (agentic kök-neden motoru) kaldı —
**KULLANICI AÇIKÇA ERTELEDİ**: "kök nedene şimdi girme, ilerde yapılacak olarak kaydet,
her şey oturunca tam fokus gireceğiz" (1 Ağustos 2026) — kullanıcı önce §B'yi (thread
modeli) manuel test edecek, D'ye kesinlikle BAŞLANMAYACAK.

**Ek, 13 maddenin DIŞINDA bir ara-iş de TAMAMLANDI**: kapsamlı log-görünürlüğü (§LOG,
altta) — kullanıcı manuel test sırasında hata aldığında kaynağını (LLM/API/Docker/
frontend) ayırt edemiyordu, bu artık backend+frontend'in TEK giriş/çıkış noktalarında
(her `/ask`/`/cube`/`/ask/upload` isteği+cevabı, her LLM sağlayıcı denemesi/hatası, her
frontend HTTP çağrısı) net, yapılandırılmış loglarla görünür.

**§B.6'nın İLK sürümü kullanıcı tarafından REDDEDİLDİ ve DÜZELTİLDİ** (bkz. "§B.6
DÜZELTMESİ" bölümü altta) — kavramsal bir hata içeriyordu: `is_new_topic` sinyali
yanlışlıkla thread sınırı (yeni panel mi açılsın) kararına da karıştırılmıştı, bu yüzden
bir thread içinde konu değiştirildiğinde kullanıcı istemeden yeni bir thread'e
fırlatılıyordu. Düzeltilmiş model: thread SAF görsel gruplama (konudan bağımsız), yeni
thread YALNIZ sol komposer'la (her zaman taze), sağ panelin KENDİ komposer'ı bağlamsal
devamı taşır, kart-bazlı "yanıtla" + çoklu-seçim birleşik bağlam eklendi.

**İKİNCİ düzeltme turu (AYNI gün)**: ilk düzeltme mutation/bağlam mantığını doğru
kurdu ama SOL panelin GÖRSEL render'ını değiştirmeden bıraktı — hâlâ her thread'in TÜM
item'larını iç-içe/girintili gösteriyordu (eski, "sağa taşınması gereken" akış). Kullanıcı
tekrar reddetti: "sol chat hala bağlamsal ve threadsel çalışıyor... peşi sıra yazdığımız
iç içe ve altına giriyor... eski sol chat sağa geçmiş olacak." Düzeltme: sol panel ARTIK
DÜZ bir liste (her thread = TEK bağımsız satır, iç-içe YOK); follow-up öneri chip'leri ve
"bağlam: X" göstergesi TAMAMEN sağ panele taşındı (bkz. "§B.6 DÜZELTMESİ 2" altta).

**§BUG (VQR embedder kilidi) + §CUBE-ROUTER (3 genel kök-neden düzeltmesi) de
TAMAMLANDI**: sırasıyla LLM isteklerinin container yeniden başlatıldığında dakikalarca
asılı kalması (kod hatası değil, non-blocking kilit düzeltmesi) ve typo-önerisi/kırılım-
koruması/cube-çözümleme tie-break'indeki 3 genel (kelime-özel değil) kusur. Tam
`pytest` → 484 passed, aynı 2 bilinen pre-existing hata. Ayrıca ayrı bir araştırma turu
(arka planda) LLM/cube mimarisinin GENEL OLARAK sağlam olduğunu — "Intent-JSON" katmanı
zaten var, yalnız bir `raw_followup` "tuzağı" yüzünden trafik yakalayamıyor — doğruladı;
bu düzeltme henüz UYGULANMADI (kullanıcı onayı bekleniyor, bkz. "§CUBE-ROUTER" altındaki
not).

| Madde | Kapsam | Durum | Kanıt (dosya:satır / test) |
|---|---|---|---|
| A6 (13) | LLM/Discovery yolunda sayısal-kodlu zaman kolonu yanlış "ölçü" sayılıyordu | ✅ Düzeltildi | `app/viz.py::analyze()` (`_TIME_NAMES` isim-eşleşmesi değer tipinden bağımsız) — `tests/test_viz.py::test_llm_no_cube_query_numeric_month_stays_time_col` |
| A1 (1) | "nisan"→"lisans" yanlış typo-chip'i (çok-aylı kıyas sorularında) | ✅ Düzeltildi | `app/cube_router.py::_period_hit_words()` (`re.search`→`re.finditer`) — `tests/test_cube_router.py::test_iki_ayli_karsilastirma_typo_onerisine_donusmez` |
| A2 (8) | Jenerik "grafik yap" tabloyu grafiğe çevirmiyordu | ✅ Düzeltildi | `dima-frontend-demo-master/src/components/ResultView.tsx` (`defaultView()`) — backend golden: `test_grafik_tipi_ipucu_jenerik` |
| A3 (9, kısmi) | VQR, sohbet içi BİREBİR soru tekrarında hep atlanıyordu | ✅ Düzeltildi | `app/routers/ask.py` (`is_literal_repeat`) — `test_mid_conversation_literal_tekrar_vqr_uzerinden_doner` + negatif: `test_gercek_takip_sorusu_vqr_atlamiyor` |
| A4 (10) | Kırılım boyutu varken 2-birimli ölçüler tek eksende eziliyordu | ✅ Düzeltildi | `app/viz.py::recommend()` (facet_measure→series) + `chart.ts` (seri-gruplu render) — `tests/test_viz.py::test_two_units_with_series_dim_becomes_facet_measure`, tsx smoke-test ile programatik doğrulandı |
| A5 (11, kısmi) | "personel" sinonimi tanınmıyordu | ✅ Düzeltildi | `demo/packs/sektor/boyahane/cubes/parti/metadata.yml` — `test_personel_sinonimi_operator_boyutuna_coz` |
| F (12) | Düz-dil hesaplama açıklaması normal `/ask`e taşınmamıştı | ✅ Düzeltildi | `app/schemas.py` (`calculation_explanation`) + `_attach_viz` + `ReportPanel.tsx` — `test_cube_makine_oee`, `test_cube_query_olmayan_yanitta_calculation_explanation_yok` |
| C1 (2+3, kısmi) | Discovery/LLM yanıtında grafik tıklaması sessizce hiçbir şey yapmıyordu | ✅ Düzeltildi | `ResultView.tsx::handleChartDataPointClick` (koşulsuz bağlama + görünür ipucu) |
| C2 | LLM yanıtlarında kısmi related_cubes/ham-satır açma | ⏳ Beklemede | §D ile birlikte değerlendirilecek (plan §C madde 2) |
| E.1-E.3 (11, kalan) | Kişi/varlık bazlı bar grafiğinde ortalama referans çizgisi | ✅ Düzeltildi | `app/viz.py::recommend()` (`reference_line`) + `chart.ts` (`markLine`) — `tests/test_viz.py::test_reference_line_*` (3 test), tsx smoke-test |
| E.4 | route()'un tek-ölçü sınırlamasını tek-shot'ta gevşetme | ❌ Denendi, ETKİSİZ bulundu, GERİ ALINDI | Aşağıda "§E.4 bulgusu" — kanıtlı, kod okunarak doğrulanmış gerekçe |
| B.1-B.5 (4+6, kısmi) | is_new_topic sinyali + ChatPanel "yeni konu" ayracı + ReportPanel breadcrumb | ✅ Düzeltildi | `app/schemas.py` (`is_new_topic`) + `ChatPanel.tsx`/`ReportPanel.tsx` — `test_is_new_topic_taze_soruda_true_takipte_false` |
| B.6 (4+6, kalan) | Konu/thread modeli: sol panelde iç-içe gösterim, sağ panelde biriken rapor yığını | ⚠️ İLK sürüm REDDEDİLDİ, DÜZELTİLDİ ✅ | Bkz. "§B.6 — Konu/Thread Modeli" (ilk tasarım) VE "§B.6 DÜZELTMESİ" (kabul edilen son hal) bölümleri altta |
| D (5+7) | Agentic kök-neden motoru | ⏳ ERTELENDİ (kullanıcı talebi) | Kullanıcı: "şimdi değil, her şey oturunca tam fokus gireceğiz" — FAZ 4 (0→100 dosyası) zaten okundu, plan hazır olunca kullanılacak |

### §B.6 — Konu/Thread Modeli (1 Ağustos 2026 — TAMAMLANDI)

Kullanıcının kendi tarifi: bir panel açıkken yazılan mesajlar solda o panelin ana
mesajının altına iç-içe girer, sağda panel aynı konunun cevaplarını alta doğru biriktirir
(silinmez); bağlam değişince/kullanıcı çıkınca sağ panel temizlenir, istenildiğinde eski
konuya geri dönülüp kaldığı yerden devam edilebilir. "Tuval" (AnalysisCanvas) BU İŞE
KARIŞMAZ — o, FARKLI konuları birleştirmek içindir (kullanıcının kendi ayrımı).

**Ayrı bir Plan Mode turu** (2 paralel Explore agent'ı + 1 Plan agent'ı, kullanıcının
işaret ettiği `Dima-0-100-Gorev-Takip-Dosyasi (2).md` FAZ 2/3 bölümleri okunarak) ile
tasarlandı ve onaylandı. Plan agent'ı, İLK sezginin (düz listeyi `is_new_topic`
sınırlarında gruplamak) YANLIŞ olduğunu somut bir senaryoyla kanıtladı: Thread A (3 mesaj)
→ B (2 mesaj) → C (1 mesaj) → A'ya geri dönüp devam edilirse, SAF ardışık gruplama bu
mesajı yanlışlıkla C'nin thread'ine sokar. **Karar: gerçek bir `thread_id` alanı**
(backend: `AskRequest`/`AskResponse`/`CubeRequest`, salt pass-through, `is_followup`
mantığına KARIŞMAZ; client `is_new_topic`'i gördükten SONRA mint/etiketleme kararı verir).

**Ayrıca 2 kritik, ÖNCEDEN VAR OLAN bug bulundu ve düzeltildi** (thread modeli tam olarak
bu kod yolunu değiştirdiğinden bu turun parçası oldu):
1. `stores/history.ts` oturum başına yalnız SON 20 mesaj tutuyordu — derin bir thread'e
   girip çıkıp geri dönme senaryosunda birkaç thread sonra kök mesajlar KAYBOLUYORDU. Sınır
   KALDIRILDI.
2. `page.tsx`'in backend'e gönderdiği `history` dizisi YANLIŞ sıradaydı (YENİ→ESKİ
   gönderiliyordu, backend ESKİ→YENİ bekliyor ve `history[-1]`'i "bir önceki soru" sayıyor
   — `is_literal_repeat`, VQR çapraz-konu kontrolü, `generate_followup_sql` hep buna
   dayanıyor) VE thread'e özel değildi (eski bir thread'e dönülünce başka thread'lerin
   mesajları karışabiliyordu). Düzeltildi: artık AKTİF thread'in KENDİ kronolojik
   item'larından, doğru sırada kesiliyor.

**Uygulama** (kod-seviyesinde): `src/lib/threads.ts` (yeni) — `groupIntoThreads()`
(thread_id birincil, `is_new_topic`-sınırlı ardışık gruplamaya düşüş SADECE eski/
migrasyon-öncesi kayıtlar için), `mintThreadId()`, `threadContaining()`; tsx smoke-test
ile HEM sıra-dışı yeniden-giriş senaryosu HEM legacy-fallback HEM karma geçiş
doğrulandı (programatik, gerçek kod çalıştırılarak). `ReportPanel.tsx`'in eski 661
satırlık tek-rapor gövdesi `ReportCard.tsx`'e (yeni) ÇIKARILDI — `ReportPanel` artık
ince bir yığın kapsayıcısı (`thread: Thread | null` alır, raporlanabilir her item için
bir `<ReportCard>` render eder, `fb` verify-map'i paylaşılan tek state, `viewHint`
yalnız EN SON karta, `pending`/`error` artık tüm render'ı DEĞİŞTİRMEZ, yığının altına
eklenir). `ChatPanel.tsx` artık `threads`/`activeThreadId`/`onSelectThread` alır —
tek-seviyeli sabit girinti (merdiven YERİNE — derin thread'lerde metni ekran dışına
itmez), aktif thread'in TÜM bloğu tek konteynerde vurgulanır, tıklama THREAD'İN
TAMAMINI aktive eder (bağlam thread'in KENDİ SON item'ından geri yüklenir, tıklanan
tarihsel noktadan DEĞİL). Mevcut "bağlam: … · ×" düğmesi GENİŞLETİLDİ (yeni düğme
EKLENMEDİ) — artık `contextCq`+`prevSql`+`activeThreadId`+`viewHint` DÖRDÜNÜ birlikte
temizler ("konudan çık").

**Bilinçli sapma (plan'dan, gerekçeli)**: plan `threaded_chat` feature-flag'i ARKASINDA
aşamalı geçiş öneriyordu (mevcut `ask_async_discovery` deseniyle aynı). Uygulamaya
geçince bunun GERÇEKTEN faydalı olması için `ChatPanel`/`ReportPanel`'in ESKİ prop
şekillerini de KORUYUP flag'e göre dallandırmak gerekiyordu — bu, tek-kullanıcılı/aktif
geliştirme aşamasındaki bu ürün için gereksiz karmaşıklık (iki paralel kod yolu, ikisi de
test edilmeli) eklerdi ve kullanıcının "mükemmelce bitir, ben test edeceğim" isteğiyle
ÇELİŞİRdi. Flag YİNE DE `app/features.py`'ye KAYDEDİLDİ (`threaded_chat`, dokümantasyon +
gelecekte gerçek çok-tenant'lı kademeli açılış gerekirse hazır) ama page.tsx DOĞRUDAN
yeni bileşenlere geçti (flag'e bakmadan) — `ask_async_discovery` ile AYNI ilke
(`demo/packs/features.yml`'e BİLEREK eklenmedi, varsayılan her yerde kapalı/nötr).

**Doğrulama**: `pytest` tam paket → 463 passed, 2 pre-existing (`git stash` ile TEKRAR
doğrulandı, aynı 2 test: `test_vqr_yakin_eslesme_olcu_uyusmazliginda_atlanir`,
`test_eval_gate_answered_precision_dusmez`) — YENİ regresyon YOK. Frontend
`tsc --noEmit` → 0 hata; `eslint .` (tüm proje) → 0 hata, 4 pre-existing/alakasız uyarı.
Yeni backend testi: `test_thread_id_pass_through_ask_ve_cube`.

**Kullanıcının MANUEL test etmesi önerilen senaryolar** (kod-seviyesinde doğrulandı ama
gerçek tarayıcıda görülmedi — bu oturumda frontend'i çalıştırıp tıklayarak test etme
imkanı yok):
1. Bir konu başlat, birkaç takip sor (sağda birikip birikmediğini gözle).
2. "× konudan çık" → sağ panel temizleniyor mu, yeni soru yeni bir konu başlatıyor mu.
3. Konu A'da birkaç mesaj → konu B'ye geç (sol panelden eski bir mesaja tıkla ya da yeni
   bağımsız soru sor) → tekrar A'nın bir mesajına tıkla → A'nın TÜM geçmişi geri geliyor
   mu, oradan devam edince doğru bağlamla mı cevap geliyor.
4. Chip düzenleme (kırılım/dönem butonları) → doğru thread'in altına mı ekleniyor.
5. Excel/CSV yükleme → yeni, temiz bir konu başlatıyor mu.
6. Eski bir sohbeti "geçmiş"ten devam ettirme (resume) → en son konu doğru aktive
   oluyor mu, devam edince doğru bağlamla mı cevap geliyor.
7. Tuval modu → thread modelinden BAĞIMSIZ, eskisi gibi çalışıyor mu.

### §LOG — Kapsamlı log görünürlüğü (1 Ağustos 2026 — TAMAMLANDI)

Kullanıcı talebi (kelimesi kelimesine): "her girdiyi loglayan bir şey olsun konsolda hem
front hem backteki her şeyi mükemmelce logla çünkü bazen hata alıyorum ama çözemiyorum llm
mi patladı api mi docker mı front mu her şeyi görelim net şekilde her soru cevapta vs her
şeyde chatta üzerindeki her işlemde". 13 maddenin DIŞINDA, ayrı bir ihtiyaç — §B.6'nın
manuel test sürecine EŞLİK etmesi için.

**Kod okunarak KESİN tespit edilen 4 kör nokta** (spekülasyon değil):
1. `app/llm.py`'de HİÇ log yoktu. `FailoverSqlGenerator` bir sağlayıcı hata verip
   SONRAKİ başarılı olduğunda ARA hatayı SESSİZCE yutuyordu (yalnız yerel `errs`
   listesine ekleniyor, hiçbir yere yazılmıyordu) — Anthropic anahtarı geçersizken
   Gemini'ye sessizce düşülüyor, kullanıcı Anthropic'in patladığını HİÇBİR ZAMAN
   GÖREMİYORDU. TAM OLARAK "llm mi patladı" sorusunun kök nedeni.
2. `app/routers/ask.py`'de yalnız 44 adet `.warning(exc_info=True)` (hata yolu) vardı,
   SIFIR `.info()` (mutlu-yol izleme) — hangi isteğin geldiğini/hangi cevabın gittiğini
   gösteren TEK bir log satırı yoktu.
3. `app/main.py`'nin arka-plan zamanlayıcı döngüsünde GERÇEK bir `except Exception: pass`
   (TAMAMEN sessiz, ADR-0020'nin kendi "sessiz yutma yok" ilkesini ihlal ediyordu) +
   yapılandırılmış logger'ın DIŞINDA çıplak bir `print(..., file=sys.stderr)`.
4. Frontend'de (`dima-frontend-demo-master/src`) `console.log/error/warn` KULLANIMI SIFIRDI
   (exhaustive grep ile doğrulandı) — hiçbir HTTP çağrısı, başarı ya da hata, konsola
   düşmüyordu.

**Düzeltme — log-and-rethrow deseni (davranış HİÇ değişmez, yalnız görünürlük eklenir)**:
- `app/llm.py`: `AnthropicSqlGenerator._ask` ve `OpenAICompatibleSqlGenerator._chat`
  (Groq/Ollama/Gemini/xAI hepsi bu sınıftan geçer) artık her deneme öncesi/sonrası
  `_log.info(...)`, hata durumunda `_log.warning(..., exc_info=True)` ATIP YENİDEN
  FIRLATIYOR (exception'ın `FailoverSqlGenerator`'a ulaşması hiç değişmedi). `Failover
  SqlGenerator`'ın 5 metodu da (generate_sql/generate_followup_sql/repair/select_cube/
  refine_cube) TÜM sağlayıcılar tükendiğinde tek bir ÖZET `_log.error(...)` atıyor —
  "hangi sağlayıcı ne zaman patladı" ayrı ayrı, "hepsi tükendi" tek bakışta.
- `app/routers/ask.py`: `/ask` handler'ının başında "İSTEK /ask" (soru, session, thread,
  followup sinyalleri), `_finish()`'in (TEK choke-point, her başarılı `/ask` cevabı
  buradan geçer) sonunda "CEVAP /ask" (source, thread, satır sayısı, süre, varsa not) —
  aynı desen `/cube` ve `/ask/upload` için de eklendi (upload'ın dosya-işleme hata yolu
  ÖNCEDEN hiç loglamıyordu, artık `exc_info=True` ile logluyor).
- `app/main.py`: `run_due()` çağrısındaki sessiz `except: pass` → `_log.warning(...,
  exc_info=True)`; `materialize_and_recompose()` çağrısındaki çıplak `print` →
  yapılandırılmış logger. Ayrıca başlangıçta Wren motoru bağlantı bilgisi VE hangi LLM
  sağlayıcı zincirinin (failover sırasıyla) GERÇEKTEN aktif olduğu loglanıyor — "docker mı"
  sorusunun İLK adımı: sunucu ayağa kalkarken hangi sağlayıcı yapılandırılmış OLMALI.
- `dima-frontend-demo-master/src/lib/api-client.ts`: TEK entegrasyon noktası (saka-
  standards kuralı: tüm HTTP buradan geçer) — request interceptor'a her giden çağrının
  (method+url+özet payload, parola/base64 maskelenir) logu, response interceptor'a hem
  başarı (status+süre) hem hata logu eklendi. Hata logu KRİTİK bir ayrım yapıyor:
  `error.response` YOKSA "AĞ HATASI — backend'e ulaşılamadı (sunucu/Docker çalışıyor mu,
  CORS?)"; VARSA backend'in döndürdüğü asıl `detail` + durum kodu — kullanıcının
  "llm mi api mi docker mı front mu" sorusunu konsoldan TEK BAKIŞTA ayırt etmesini sağlar.

**Doğrulama**: `test_llm_logging.py` (6 yeni test — her sağlayıcının başarı/hata logu +
`FailoverSqlGenerator`'ın özet-hata logu + ara-hatanın başarılı failover'da bile GÖRÜNÜR
kaldığını kanıtlayan test), `test_ask_router_logging.py` (2 yeni test — gerçek `TestClient`
üzerinden `/ask` ve `/cube`'un istek+cevap logunu `caplog` ile doğrular). Tam `pytest` →
471 passed (463 + 8 yeni), aynı 2 pre-existing hata (`git stash` ile önceden defalarca
doğrulanmış, bu turla İLGİSİZ). Frontend `tsc --noEmit` → 0 hata; `eslint .` → 0 hata,
4 pre-existing/alakasız uyarı (bu dosyaya dokunmadı). `npx tsx` ile geçici bir smoke-test
(sahte axios adapter, gerçek ağ yok) 3 senaryoyu (başarı/backend-hatası/ağ-hatası) çalıştırıp
konsol çıktısının okunabilir olduğu gözle doğrulandı, sonra silindi.

### §B.6 DÜZELTMESİ — Thread ≠ Bağlam, Yanıtla + Çoklu-Seçim (1 Ağustos 2026 — TAMAMLANDI)

**Kullanıcı §B.6'nın ilk sürümünü reddetti**: "thread mantığı yanlış ben sana bağlam
penceri açıyoruz demedim... o thread içinde oee konuşurken satış pazarlama da
konuşabilir yani küp ya da bağlamdan bağımsız bir yapı olmalıydı." Kök hata: backend'in
`is_new_topic` sinyali (yalnız "bu cevap `cube_query`/`prev_sql` bağlamını taşıdı mı"
anlamına gelen bir alan) `page.tsx`'te yanlışlıkla thread-sınırı kararına da karışmıştı
(`startsNewThread = activeThreadId === null || data.is_new_topic`) — bir thread içinde
konu değiştirildiğinde kullanıcı istemeden yeni bir thread'e fırlatılıyordu.

**Düzeltilmiş model** (kullanıcının netleştirdiği, 2 kez vurguladığı KRİTİK nokta):
- **Thread = SAF görsel gruplama**, konudan/cube'dan TAMAMEN bağımsız.
- **Sol komposer (ChatPanel) ARTIK VE HER ZAMAN yeni bir thread açar** — aktif thread
  olsun ya da olmasın, İSTİSNASIZ. Eski bağlamsal/takip davranışının TAMAMI sağa taşındı.
- **Sağ panelin (ReportPanel) KENDİ komposer'ı** aktif thread'in GÜNCEL bağlamıyla devam
  eder — eski TEK komposer'ın bağlamsal işlevinin yeni evi.
- **Kart-bazlı "↳ yanıtla"**: her karta özel bir yanıt kutusu; kullanıcı SONRADAN
  netleştirdi ("ya da 3 ve 4 ün arasına girsin dedim ya vazgeçtim öyle olmasın... en sona
  gelsin cevap yine de") — sonuç KRONOLOJİK OLARAK SONA eklenir (araya sokulmaz), yalnız
  `reply_to_label` breadcrumb'ıyla hangi karta bağlandığı görünür kalır. Bağlam (cube_query/
  sql) o SPESİFİK çapa karttan gelir, thread'in güncel durumundan DEĞİL.
- **Çoklu-seçim**: birden fazla kart seçilip birleşik bağlamla soru sorulabilir — çapa
  (en-son seçilen) yapısal follow-up gibi davranır, diğerleri yalnız Discovery LLM
  promptuna grounding metni olarak eklenir (`extra_context`) — deterministik cube-routing
  yoluna BİLİNÇLİ olarak karışılmaz (golden-eval koruması).

**Uygulama**: `backend/app/schemas.py`/`ask.py` — iki YENİ, katkısal, salt pass-through/
grounding alanı (`reply_to_label` thread_id ile AYNI echo deseni; `extra_context` yalnız
`_with_extra_context()` yardımcısıyla `_run_discovery()`'nin İKİ LLM çağrısına enjekte
edilir, `resp.question`/VQR/deterministik yola HİÇ dokunmaz). `page.tsx` — eski TEK
`submit()`/`is_new_topic`'e dayalı `onSuccess` KALDIRILDI, yerine `AskMutationVars`
discriminated-union (`"new"|"continue"|"reply"|"reply-multi"`) — thread sınırı ARTIK
YALNIZCA hangi komposer kullanıldığına bağlı, `is_new_topic` hiçbir yerde okunmuyor.
`ChatPanel.tsx` — `compact` prop'u (thread aktifken panel daralır + "buraya yazmak her
zaman yeni thread açar" ipucu), "yeni konu" ayracı → "yeni yığın" (konu-çağrışımı
kaldırıldı), öneri-chip'leri artık `threadContaining()` ile pasif thread'i bulup o karta
anchor'lı yanıtlar. `ReportPanel.tsx` — seçim modu + "N seçili" + iki alt-komposer
(continue/reply-multi, karşılıklı dışlayıcı). `ReportCard.tsx` — "↳ yanıtla" popover
(mevcut dashOpen/schedOpen/wrongOpen dörtlüsüne katıldı, AYNI tek-açık/dışarı-tıklama
deseni), seçim checkbox'ı, `reply_to_label` öncelikli breadcrumb.

**Canlı bulgu (test yazarken)**: VQR'ın yakın-eşleşmesi (near_exact, embedding tabanlı)
TÜM test dosyaları arasında PAYLAŞILAN, session-ömürlü — "sevkiyat durumu" gibi başka
test dosyalarında da kullanılan bir soru, tam pytest koşumunda dosya sırasına bağlı
olarak "vqr" kaynağından dönüp Discovery'ye HİÇ düşmeyebiliyordu (izole çalıştırmada
geçen ama tam pakette başarısız olan gizli bir sıra-bağımlılığı). Çözüm: yeni Discovery
testlerinde `vqr.near_exact`'ı doğrudan `None` döndürecek şekilde monkeypatch'lemek —
hangi sırada koşulursa koşulsun sağlam.

**Doğrulama**: `backend/tests/test_ask_reply_context.py` (5 yeni test — `reply_to_label`
echo, `extra_context`'in LLM promptuna eklendiğini VE `resp.question`'ı değiştirmediğini,
yapısal takipte `extra_context`'in LLM'e HİÇ düşülmediğini kanıtlar). Tam `pytest` → 476
passed (471+5), aynı 2 pre-existing hata dışında sıfır regresyon. Frontend `tsc --noEmit`
→ 0 hata; `eslint .` → 0 hata (bir `react-hooks/set-state-in-effect` hatası bulunup React'ın
"render sırasında state ayarlama" desenine çevrilerek düzeltildi), 4 pre-existing/alakasız
uyarı.

**Kullanıcının MANUEL test etmesi gereken senaryolar** (kod-seviyesinde doğrulandı, tarayıcıda
görülmedi):
1. Bir thread içinde OEE sorup ARDINDAN satış/pazarlama sorunca YENİ bir thread'e
   ATILMADIĞINI, sağ panelin ikisini de ALT ALTA biriktirdiğini doğrula.
2. Sol komposer'a yazınca HER ZAMAN yeni bir thread açıldığını, sağ panelin kendi
   komposer'ına yazınca AYNI thread'e eklendiğini doğrula.
3. Eski bir karta "↳ yanıtla" ile yanıt ver → yeni kart LİSTENİN SONUNA eklenmeli, üstünde
   "↳ yanıt: {eski kartın etiketi}" görünmeli, o ESKİ kartın bağlamına göre çalışmalı.
4. Birden fazla kart seç → "N kart birleştirilerek soruluyor" çubuğuyla sor.
5. Thread aktifken sol panelin daraldığını + ipucu metninin göründüğünü doğrula.
6. Bir netleştirme/upload sonrası öneri-chip'ine (pasif bir thread'de bile) tıklayınca
   doğru thread'in aktifleştiğini ve doğru bağlamla devam ettiğini doğrula.

### §B.6 DÜZELTMESİ 2 — Sol Panel DÜZ Liste, Sağ Panel TAM Akış (1 Ağustos 2026 — TAMAMLANDI)

**İlk düzeltme (yukarıdaki "§B.6 DÜZELTMESİ") mutation/context mantığını doğru kurdu**
(`is_new_topic` artık thread sınırına karışmıyor, dual composer doğru yerlerde) **ama BİR
ŞEYİ atladı**: `ChatPanel.tsx`'in kendi RENDER'ı hâlâ İLK (reddedilen) B.6 tasarımından
kalma haldeydi — her thread'i `threads.map` → `items.map` ile İÇ İÇE, `j > 0 ? "ml-4" :
""` girintisiyle render ediyordu; "yeni yığın" ayracı, öneri-chip'leri (`item.
suggestions`) ve "bağlam: X · ×" göstergesi HÂLÂ sol paneldeydi. Kullanıcı test edip
tekrar reddetti: "sol chat hala bağlamsal ve threadsel çalışıyor... bir şey yazıyorum
peşi sıra yazdığımız iç içe ve altına giriyor bu eski bir feature düzeltmemişsin... eski
sol chat sağa geçmiş olacak... follow up önerileri artık sağda gelmeli çünkü artık thread
sağda akacak... bağlam olarak da mesela oee eklenebiliyor küp bağlamı olarak vs o da
sağda panelde olacak artık."

**Kök neden**: ilk düzeltmede "sol panel = daima yeni thread" mantığı DOĞRU kuruldu ama
sol panelin GÖRSEL sorumluluğu YENİDEN TASARLANMADI — sadece hafifçe uyarlandı (compact
mode, wording değişikliği). Oysa doğru model: eski sohbet akışının TAMAMI (iç-içe soru/
cevap, öneri chip'leri, bağlam göstergesi) SAĞ panele TAŞINMALIYDI; sol panel ise
YENİ, çok daha basit bir şey olmalıydı — her thread için TEK, bağımsız bir satır (bir
"panel listesi", tipik bir chat uygulamasının konuşma kenar çubuğu gibi).

**Düzeltme**:
- `ChatPanel.tsx`: `threads.map(items.map(...))` iç-içe render'ı TAMAMEN kaldırıldı,
  yerine `threads.map(...)` DÜZ liste — her satır thread'in KÖK sorusu + kısa bir durum
  özeti (son raporlanabilir item'ın satır sayısı/KPI/SourceBadge'i, ya da not metni, artı
  ">1 mesaj" rozeti). "yeni yığın" ayracı KALDIRILDI (her satır zaten trivially bağımsız
  bir thread). "bağlam: X · ×" göstergesi VE öneri-chip render'ı TAMAMEN kaldırıldı —
  `onSuggestionReply` prop'u da (artık gereksiz) silindi.
- `ReportPanel.tsx`: not-yalnız (result/kpi'siz) item'lar ARTIK render ediliyor (öncesinde
  `if (!(it.result || it.kpi)) return null` ile atlanıyordu) — hafif bir blok (soru + amber
  not kutusu + öneri chip'leri), chip tıklaması O SPESİFİK item'a anchor'lı `onReply` çağırır
  (aynı "yanıtla" mekanizması, page.tsx'te ayrı bir "pasif thread'i bul" koduna GEREK
  KALMADI — zaten aktif thread'in İÇİNDEYİZ). Başlık çubuğuna SOLDAN taşınan "◆ bağlam: X ·
  ×" göstergesi eklendi (seçim-modu toggle'ının yanına, `contextLabel`/`onClearContext`
  prop'larıyla).
- `page.tsx`: `submitSuggestionReply`/`threadContaining` kullanımı KALDIRILDI (dead code —
  chip'ler artık doğrudan ReportPanel içinden `onReply` çağırıyor). `pending` ARTIK
  `mutation.variables?.kind`'a göre AYRILIYOR: `isPendingNew` (kind==="new") solda "yeni
  panel oluşturuluyor" satırını tetikler, geri kalanı (`continue`/`reply`/`reply-multi`)
  sağda `pending` göstergesini tetikler — ikisi ASLA aynı anda gerçek olamaz (tek paylaşılan
  `mutation`). `contextLabel`/`onClearContext` artık `ChatPanel`'e değil `ReportPanel`'e
  geçiriliyor.

**Ders (belleğe kaydedildi)**: kullanıcı bir UI öğesinin/davranışın bir panelden diğerine
TAŞINDIĞINI söylediğinde, iki paneli YERİNDE hafifçe uyarlamak YETMEZ — render
sorumluluğunu GERÇEKTEN taşımak ve boşalan panelin YENİDEN NE OLMASI gerektiğini SIFIRDAN
düşünmek gerekir (düz bir liste, "daha az girintili eski sohbet" DEĞİLDİR — yapısal olarak
FARKLI, çok daha basit bir görünümdür).

**Doğrulama**: backend DEĞİŞMEDİ (bu tur salt frontend) — tam `pytest` yine de koşuldu,
476 passed, aynı 2 pre-existing hata. Frontend `tsc --noEmit` → 0 hata; `eslint .` → 0
hata, 4 pre-existing/alakasız uyarı.

### §BUG — VQR embedder kilidi, LLM isteklerini SONSUZA KADAR asıyordu (1 Ağustos 2026 — DÜZELTİLDİ)

**Kullanıcı bulgusu**: "LLM'e giden istekler çalışmıyor... internal server hatası... openrouter
ve gemini apilerine bakıyorum ama loglara düşmüyor... sistemden istek apilere gitmiyor...
bir önceki committe bu sorun yoktu." Canlı `dima-backend-core` container loglarıyla
doğrulandı: bağımsız/Discovery'ye düşen bir soru ("son 3 ay toplam üretim miktarı ve artıış
trendi") `İSTEK /ask` logunu bastıktan SONRA hiçbir zaman tamamlanmadı — ne `CEVAP /ask`
logu, ne hata, ne uvicorn erişim-logu satırı, ne de LLM sağlayıcılarına (gemini/groq/xai)
GERÇEKTEN bir istek gitti (bu yüzden sağlayıcı panellerinde hiçbir kayıt görünmüyordu).

**Kök neden (kod okunarak KESİN doğrulandı)**: `app/vqr.py::_embedder()` fastembed'in
`multilingual-e5-large` ONNX modelini (~1GB+) ilk kullanımda İNDİRİYOR — bu indirme
`main.py`'nin arka-plan ısıtma thread'inde (`_warm(_embedder)`) başlıyor. Container TAZE
başladığında (`/tmp/fastembed_cache` KALICI bir volume DEĞİL — her restart'ta silinir) bu
indirme HuggingFace Hub'ın kimliksiz (HF_TOKEN'sız) hız sınırlaması yüzünden ÇOK YAVAŞ
(canlı gözlem: 600MB+ parça 13+ dakikada hâlâ `.incomplete`). `_embedder()` `with
_emb_lock:` (BLOKLAYAN bir `threading.Lock`) kullanıyordu — ısıtma thread'i indirme
SÜRERKEN GERÇEK bir kullanıcı isteği (`vqr.near_exact`/`few_shot_block` üzerinden)
`_embedder()`'ı çağırırsa, o isteğin thread'i indirme TAMAMEN BİTENE KADAR (dakikalarca,
timeout YOK) SONSUZ BEKLİYORDU. Bu, `main.py`'nin KENDİ ısıtma yorumunun ("ilk soru 12sn
beklemesin") TAM TERSİYDİ — ama tasarım hatası ÖNCEDEN VAR OLAN bir bug'dı (bu oturumun
kodu DEĞİL); yalnızca bu oturumdaki kod değişiklikleri container'ın YENİDEN BAŞLATILMASINI
gerektirdiği için (önceki, ısınmış/cache'li process kaybedildi) İLK KEZ tetiklendi —
kullanıcının "önceki committe sorun yoktu" gözlemi bu YÜZDEN doğru ama neden KOD
DEĞİŞİKLİĞİ değil, YENİDEN BAŞLATMA idi.

**Düzeltme**: `_embedder()` artık kilidi NON-BLOCKING dener (`_emb_lock.acquire(blocking=
False)`) — biri ZATEN indiriyorsa (ör. arka-plan ısıtması) bu çağrı BEKLEMEDEN `None`
döner; mevcut sözlüksel fallback yolu (`_scores()`/`near_exact()`) bunu ZATEN doğru
işliyordu, yalnızca ULAŞILAMIYORDU. Tek-indiren-thread garantisi KORUNUR. Doğrudan
container İÇİNDE (aynı çalışma zamanı, gerçek `fastembed` indirmesi SÜRERKEN) test
edilerek doğrulandı: ikinci thread artık 0.000s'de `None` dönüyor (öncesinde dakikalarca
asılı kalırdı).

**Uygulanan adımlar**: (1) `backend/app/vqr.py::_embedder()` düzeltildi, (2)
`docker-compose build dima-backend` + container yeniden oluşturuldu (kod DEĞİŞİKLİĞİ
imaja BAKILI — canlı volume mount yok, restart tek başına YETMEZDİ), (3) düzeltme,
indirme SÜRERKEN ikinci bir thread'in artık BLOKE OLMADIĞI doğrudan test edilerek
doğrulandı. Tam `pytest` (476 passed, aynı 2 pre-existing hata) — regresyon yok.

**Kalıcı öneri (henüz UYGULANMADI, kullanıcı onayı gerekir)**: `/tmp/fastembed_cache`
(ya da `HF_HOME`) için `docker-compose.yml`'e KALICI bir volume eklenirse, model YALNIZ
BİR KEZ (ilk container ömründe) indirilir, sonraki HER restart'ta ANINDA hazır olur —
bu "yavaş ısınma" sınıfının TAMAMINI ortadan kaldırır. Alternatif/ek: `HF_TOKEN`
ortam değişkeni (varsa) indirmeyi de HIZLANDIRIR.

### §CUBE-ROUTER — 3 Genel Kök-Neden Düzeltmesi: typo/kırılım/cube-çözümleme (1 Ağustos 2026 — DÜZELTİLDİ)

**Kullanıcı bulgusu**: LLM-hang bug'ı düzeldikten hemen sonra, bir OEE thread'i içinde
"son 6 aylık satış trendini göster kalem kalem ayırarak" sorusunu denedi ve HİÇBİR
varyasyonunda doğru sonuç alamadı: "uygun cube mevcut değil", "'kalem' yerine 'kalite'
mi demek istedin?" (alakasız öneri), "türlere ayırarak" dediğinde cube çalıştı ama
kırılımı UYGULAMADI. Açık talep: "tikel değil genel sorunu görmeye çalış." Kapsamlı
araştırma (kod okunarak VE gerçek fonksiyonlar gerçek demo-boyahane şemasına karşı
ÇALIŞTIRILARAK) 3 AYRI, GENEL kök neden buldu — hepsi `cube_router.py`'de:

1. **Typo motorunun "alan-alaka" barajı yoktu**: cube çözülemeyince (`_match_cube` None)
   `typo_correct()`'in sözlük havuzu TÜM kataloğa genişliyor — bu rejimde "kalem"(5)/
   "kalite"(6) 0.7273 skorla eşleşip alakasız öneri üretiyordu (bu oturumda ZATEN
   görülen "nisan"/"lisans" — AYNI 0.7273/0.8333 — ile SAYISAL OLARAK BİREBİR AYNI
   desen; her seferinde kelimeye özel yama yapılmış, kök neden hiç düzeltilmemişti).
   **Düzeltme**: geniş havuzda öneri barajı `_TYPO_HIGH`'a çekildi (`_TYPO_MID_WIDE`) —
   tek-cube'a-daralmış (test edilmiş) davranış DEĞİŞMEDİ.
2. **Kırılım-koruması, trend kelimesi de varsa devre dışı kalıyordu**: var olan
   "sessiz-yanlış koruması" `not dims and not gran` şartıyla çalışıyordu; "trend"/
   "zaman" gibi JENERİK kelimeler `gran`'ı dolduruyor, karşılanamayan bir boyut-
   kırılımı isteği sessizce düşüyordu. **Düzeltme**: `gran` yalnız JENERİK (birim
   belirtmeyen) trend/zaman kelimesinden geliyorsa koruma yine çalışır; AÇIK birim
   ifadeleri ("aylara göre", "çeyreklere göre" — kendi başına meşru bir kırılım)
   ETKİLENMEZ (ilk taslak düzeltme bunu YANLIŞLIKLA kırmıştı — `test_time_gran_
   ceyrek_yil` canlı yakaladı, düzeltilip dar kapsamlı hale getirildi).
3. **Cube-çözümleme berabere kalınca ölçü-kanıtı TEK ölçüttü, boyut-uyumu hiç
   bakılmıyordu** (EN RİSKLİ): "satış"/"satis" hem `parti` (ölçü sinonimi) hem
   `ticaret`'in (YALNIZ cube-kimliği, hiçbir ölçüsünde YOK) sinonimüyken, rakip
   aday ölçü-kanıtı SIFIR olduğunda mevcut kod HER ZAMAN `parti`'yi kazandırıyordu
   — ama "tür" boyutu YALNIZ `ticaret`'te var. **Düzeltme**: rakip ölçü-kanıtı
   TAMAMEN boşsa VE soru açıkça bir kırılım istiyorsa VE adaylardan YALNIZ biri o
   kırılımı karşılayabiliyorsa, boyut-sahibi kazanır — YALNIZ zaten-belirsiz dalda,
   YALNIZ bu dar örüntüde devreye girer, `snd_syn` dolu olan mevcut test edilmiş
   senaryular HİÇ ETKİLENMEZ.

**Kapsam dışı (bilinçli)**: "kalem" (ürün kalemi) kataloğun HİÇBİR cube'unda bir
boyut olarak yok — gerçek bir veri-modeli boşluğu, yeni bir boyut UYDURULMADI. Ayrıca
gerçek `ticaret` cube'unun HİÇBİR ölçüsü "satış" sinonimi taşımıyor — Bug 3 düzeltmesi
`_match_cube`'u doğru cube'a (ticaret) yönlendirse bile, `route()` yine de ölçü
bulamayıp `None` döner (ÖNCEDEN parti'ye gidip YANLIŞ cube'dan veri veriyordu — şimdi
dürüstçe Discovery'ye/netleştirmeye düşüyor, sessizce yanlış cevap vermiyor). "ticaret"
ölçülerine "satış" sinonimi eklenmesi ayrı bir VERİ-MODELİ kararı, bu turda yapılmadı.

**Doğrulama**: her bug TAM `pytest` ile tek tek doğrulanıp bir SONRAKİNE geçildi (Bug 1
→ 2 → 3 sırası, Bug 3 EN RİSKLİ olduğu için en sona bırakıldı). 8 yeni test eklendi.
Tam `pytest` → 484 passed (476+8), AYNI 2 pre-existing hata. Bug 3 için EK güvenlik
turu: `DIMA_COMPANY=gulteks` ile hem `test_cube_router.py` hem tam takım koşuldu —
başarısız test listesi `git stash` ile ALINAN taban çizgiyle satır satır karşılaştırıldı,
tek fark BENİM yeni eklediğim (demo-boyahane'ye özgü kelime kullanan) 2 test — sıfır
davranış regresyonu, hiçbir ÖNCEDEN geçen test bozulmadı.

**Ayrı, çok daha büyük bir mimari soru** (bu turun konusu DEĞİL, ayrı bir araştırma
turunda ele alındı — bkz. proje hafızası "vqr-embedder-blocking-bug" yanındaki
mimari analiz): kullanıcı ayrıca "LLM'e giden yanıtların çoğu, cube'un kısıtlılığı
yüzünden zengin etkileşim (kırılım/drill-down/chip/follow-up) KAYBEDİYOR, LLM neden
sadece orkestratör/garson olamıyor" sorusunu sordu. Arka planda koşan bir araştırma
ajanı, bu codebase'in ZATEN "Intent-JSON" (`source="cube+llm"`, `ask_intent_first`
bayrağı) adında TAM OLARAK bu deseni (LLM yapısal sorgu doldurur, cube çalıştırır)
uyguladığını ama canlı loglarda SIFIR trafik yakaladığını buldu — kök neden: bir
konuşmada BİR TUR Discovery'ye düşerse (`raw_followup` state), o thread'in SONRAKİ
HER turu `route()`/Intent-JSON'a asla tekrar denenmeden doğrudan ham-SQL düzenlemeye
gidiyor (kalıcı bir "tuzak"). Rakip ürün araştırması (Cube.dev/WrenAI/LangChain/Vanna/
Zenlytic) bu codebase'in Intent-JSON tercihinin (LLM=yapısal-sorgu-dolduran, SQL-yazan
DEĞİL) sektörün daha olgun ucunda olduğunu doğruladı — öneri: mimariyi DEĞİŞTİRMEK
değil, `raw_followup` tuzağını KAPATMAK (en ucuz, en yüksek etkili düzeltme) — henüz
UYGULANMADI, kullanıcı onayı bekleniyor.

### §CUBE-ROUTER-4 — deterministic_refine sessiz-yanlış koruması + canlı 5-bulgu raporu (1 Ağustos 2026 — Bug 4 DÜZELTİLDİ, kalan 4'ü ANALİZ EDİLDİ)

**Kullanıcı bulgusu (3 bug düzeltmesi sonrası YENİDEN test edilerek)**: "bağlam kübe ait
değil" hatası artık gitmiş (Bug 1-3 doğrulandı) ama 5 AYRI bulgu daha bildirildi:

1. **"son 6 aylık satış trendini göster kalem kalem ayırarak" hâlâ "kalem yerine kalite
   mi demek istedin?" veriyor.** Canlı şemaya karşı doğrudan test edilerek KESİN
   doğrulandı: bu, Bug 1'in düzelttiği çapraz-alan (geniş havuz) tuzağı DEĞİL — `_match_
   cube` bu cümleyi doğru şekilde `parti`'ye çözüyor (None DEĞİL); gerçek neden `parti`
   cube'unun KENDİ `departman` boyutunun GERÇEK bir veri DEĞERİ olarak "Kalite" (Kalite
   departmanı) içermesi — yani kapsam-İÇİ, aynı-cube bir sözcüksel çakışma, kapsam-dışı
   kirlenme değil. Kapsam dışı bırakıldı (ayrı, veri-modeli düzeyinde bir konu — "kalem"
   hiçbir cube'da bir boyut olarak tanımlı değil, bkz. §CUBE-ROUTER "Kapsam dışı" notu).
2. **"son 6 ay satış yapılan ürünleri karşılaştır" → "Ürün bilgisi boyut olarak katalogda
   mevcut değil."** Kullanıcı kendisi doğruladı: "sanırım ürün türü yokmuş zaten" — GERÇEK
   bir veri-modeli boşluğu (ürün adı/kodu/türü hiçbir cube'da boyut olarak tanımlı değil),
   kod hatası DEĞİL. Kapsam dışı.
3. **"son 6 ay verimlilik trendini makine türlerine göre karşılatır" → doğru çalıştı**
   (cube+llm, chip'lerle). Regresyon yok, ek işlem gerekmedi.
4. **Var olan bir (makine/RAM-3) thread içinde "personel bazlı verimlilikleri karşılaştır
   son 6 ay" sorusu, YENİ bir konu olarak tanınmadı** — `deterministic_refine()` önceki
   `makine` boyutunu/filtresini SESSİZCE koruyup yalnız dönemi güncelleyerek "başarılı"
   gibi göründü, oysa OEE cube'unda `personel` boyutu YOK (yalnız `parti`'de var, onun da
   "verimlilik" ölçüsü yok — gerçek bir çapraz-cube istek). **Bu, Bug 2 ile AYNI
   sessiz-yanlış-cevap ilkesinin `deterministic_refine()`'da eksik olmasıydı** — `route()`
   Bug 2'de düzeltilmişti ama takip-mesajı yolu (`deterministic_refine`) aynı korumayı
   hiç almamıştı. **Düzeltme**: `route()`'daki AYNI `_BREAKDOWN_HINTS` ilkesi
   `deterministic_refine()`'a da eklendi — eşleşen boyut YOK, zaman-kovası da YOK, ama
   mesaj açıkça bir kırılım istiyorsa `None` döner; çağıran (`ask.py`) BUNUN İÇİN zaten
   bir düşme zinciri kuruyor (`cross_cube_add` → `cross_cube_dim_switch` → taze
   `route()`) ama bu fonksiyon önceden "changed=True" (yalnız dönem değişti) dönünce o
   zincire HİÇ ULAŞILAMIYORDU.
   **İlk taslak bir regresyon yarattı** (Bug 2'de İKİ kez görülen AYNI "göre"/"bazında"
   belirsizliği, ÜÇÜNCÜ kez): var olan `test_son_n_aya_gore_kova_degil` testi kırıldı,
   çünkü "son 4 aya göre yap" `_time_gran` tarafından BİLEREK `None` döndürülen bir
   DÖNEM ifadesidir (`_REL_DATE` zaten bunu söker — `_time_gran`'daki "DİL ÇAKIŞMASI"
   notuyla AYNI ilke), ama içinde "göre" geçtiği ve yeni boyut eşleşmediği için yeni
   guard'ım bunu YANLIŞLIKLA "karşılanamayan kırılım" sanıp `None` döndürdü. **Düzeltme**:
   `_time_gran`'ın KENDİ `_REL_DATE.sub()` tekniğiyle AYNI dil-çakışması ilkesini genel
   `_BREAKDOWN_HINTS` taramasına da uygulayan yeni bir desen (`_PERIOD_RANGE_REF`) eklendi
   — "son N ay/gün/hafta/yıl'a göre/bazında/bazlı" kalıbını (dönem-aralığının kendi edatı)
   ayrı tutar; yalnız bu dar kalıp DIŞINDA kalan `_BREAKDOWN_HINTS` eşleşmeleri guard'ı
   tetikler. Hem hedef vaka ("personel bazlı...") hem regresyon vakası ("son 4 aya göre
   yap") canlı, gerçek `demo-boyahane` şemasına karşı doğrudan test edilerek doğrulandı.
5. **Aynı soru (personel bazlı...) SOL/yeni-thread komposerinden sorulunca**: doğru
   içerik ham LLM (Discovery) üzerinden geldi ama chip YOK — bu, ayrı, ÖNCEDEN tespit
   edilmiş `raw_followup` tuzağının BAŞKA bir yüzü (bkz. proje hafızası "llm-cube-
   architecture-audit") — bir thread'in İLK turu Discovery'ye düşerse o thread bir daha
   `route()`/Intent-JSON'a dönemiyor. Kullanıcının açık tercihiyle (bkz. AskUserQuestion
   yanıtı "hangisini önerirsin") bu turda ERTELENDİ — yalnız Bug 4 (madde 4, silent-
   wrong-answer, DAHA CİDDİ: yanlışlıkla "başarılı" görünüyordu) düzeltildi; `raw_followup`
   tuzağı + typo-öneri-chip'inin Discovery'ye düşmesi geliştirmesi AYRI, gelecekteki bir
   tur için bekliyor.

**Doğrulama**: `pytest tests/test_cube_router.py` → 78 passed (2 yeni test: `test_refine_
karsilanamayan_kirilim_none_doner`, `test_refine_kirilim_acik_zaman_ifadesiyle_hala_
calisir`). `test_ask_golden.py` + `test_eval_gate.py` → aynı 2 pre-existing hata, başka
yok. Tam `pytest` → 486 passed, aynı 2 pre-existing hata — regresyon yok. Container
yeniden derlenip (`docker-compose build dima-backend`) yeniden başlatıldı; düzeltme canlı
`demo-boyahane` şemasına karşı doğrudan test edilerek doğrulandı (madde 4 hedef vaka →
`None` döner, madde 4'ün regresyon riski taşıyan "son 4 aya göre yap" vakası → hâlâ
çalışır).

### §RAW-FOLLOWUP — İki thread-tuzağı: raw_followup kilidi + yapısal zincir çıkmazı (1 Ağustos 2026 — DÜZELTİLDİ)

**Kullanıcı talebi**: "raw_followup tuzağını da şimdi düzeltelim" (bkz. proje hafızası
"llm-cube-architecture-audit") + canlı yeni bulgu: "personel bazlı verimlilikleri
karşılaştır son 6 ay" bir OEE thread'i içinde YİNE "devam" sanılıp yalnız OEE'de arandı —
"thread içinde bağlam değiştirebilir, küp değiştirebilir, yeni konuya geçebilir OLMALIDIR
ve GEÇMELİDİR." Araştırma İKİ AYRI, ilgili ama farklı tuzak ortaya çıkardı — ikisi de
`app/routers/ask.py`'de:

1. **raw_followup kilidi** (önceden teşhis edilmiş, bu turda DÜZELTİLDİ): bir thread'in İLK
   turu Discovery'ye (ham-SQL, `cube_query` YOK) düşerse, `raw_followup` o thread'in SONRAKİ
   HER turunda True kalıyordu ve `_try_fresh_intent()` (route()/typo/YoY/Intent-JSON) BİR
   DAHA HİÇ ÇAĞRILMIYORDU — konu tamamen değişse, yeni soru route() ile BEDAVA ve kesin
   çözülebilir olsa BİLE, doğrudan `generate_followup_sql`'e (önceki SQL'i bağlam alan ham-
   SQL düzenlemesi) gidiyordu. **Düzeltme**: yapısal takibin KENDİ "action==new" kaçış
   kapısıyla AYNI ilke — Discovery'nin ham-SQL takip üretimine düşmeden ÖNCE
   `_try_fresh_intent()` bir kez denenir. GÜVENLİ: yalnız KENDİNDEN EMİN olduğunda (route()
   eşleşmesi/doğrulanmış Intent-JSON) bir şey döner; gerçek bir ham-SQL devamı (ör. "temmuzu
   çıkar" — cube/ölçü kelimesi taşımayan bir kırpıntı) route()'ta hiç eşleşme bulamaz, None
   döner, mevcut akış DEĞİŞMEDEN çalışmaya devam eder (regresyon kilidi testiyle doğrulandı).

2. **Yapısal zincir çıkmazı** (bu turda YENİ tespit edildi — canlı `interaction_log` kanıtı):
   YAPISAL bir takipte (`cube_query` var) deterministik zincir (refine/cross_cube_add/
   cross_cube_dim_switch/fresh route()) VE LLM'in edit/new kararı TAMAMEN tükenince eskiden
   BURADA doğrudan dürüst ret dönerdi ("Bu takip mesajını önceki raporla ilişkilendiremedim").
   Ama AYNI soru ("personel bazlı verimlilikleri karşılaştır son 6 ay") taze/yeni-thread'den
   sorulunca Discovery (ham-SQL, cube sınırlarının ÖTESİNDE serbest tablo join'i) GERÇEKTEN
   cevaplayabiliyordu — canlı kanıt: `interaction_log`'da AYNI metin İKİ KEZ, biri (thread
   içi takip) dürüst ret + "OEE cube'u personel boyutu içermemektedir, parti cube'u ise OEE
   ölçüsünü barındırmamaktadır" notuyla, biri (taze soru) `source=llm:gemini` ile GERÇEK bir
   SQL join sonucuyla. **Düzeltme**: zincir tükenince artık `_try_fresh_intent()` bir kez
   daha denenir (action="new" DIŞINDAki — refine_cube hiç çağrılamadı/hata verdi gibi —
   durumları da kapsar), o da None dönerse dürüst ret YERİNE §5 Discovery'ye düşülür
   (`raw_followup` bu noktada hâlâ False — `_run_discovery` bu yüzden STALE prev_sql'e
   çapalamadan TAZE `generate_sql` üretir, tıpkı sorunun taze-thread halinde çalıştığı gibi).
   **KRİTİK güvenlik sınırı**: bu fallthrough KOŞULSUZ değil — `cube_router._match_cube(q,
   schema)` mesajda GERÇEK bir katalog kanıtı (ör. "verim" → oee) arar; bulamazsa (ör.
   "asdlkj qwerty zxcvb" gibi anlamsız metin) dürüst ret KORUNUR. Bu ayrım olmadan ilk taslak
   `test_convo_anlasilmayan_takip_serbest_sqle_dusmez`'i (anlamsız metin ASLA Discovery'nin
   rule-tabanlı sağlayıcısının alakasız varsayılan raporuna düşmemeli) VE eval-gate'in
   answered-precision'ını (92.9% → 92.0%) KIRDI — tam pytest bunu YAKALADI, `_match_cube`
   gate'i eklenince ikisi de düzeldi (bkz. "Hatalar ve düzeltmeler" altta).

**Doğrulama**: 3 yeni test (`test_raw_followup_tuzagi_yeni_konu_intent_pathe_doner`,
`test_raw_followup_gercek_devam_hala_generate_followupa_gider`,
`test_yapisal_takip_cikmazi_gercek_kelime_varsa_discoverye_duser`) — hepsi geçti. Tam
`pytest` → 489 passed, AYNI 2 pre-existing hata (regresyon yok). EK güvenlik turu (Bug 3
ile aynı disiplin — bu değişiklik TÜM tenant'lar için `/ask`'in çekirdek kontrol akışını
etkiliyor): `DIMA_COMPANY=gulteks` ile tam takım koşuldu, başarısız test listesi `git
stash` ile alınan taban çizgiyle (157 hata) satır satır karşılaştırıldı — TEK fark BENİM
yeni eklediğim 2 demo-boyahane-özgü test (gulteks'in cari/muhasebe şemasında "oee"/"makine"
kavramı yok, beklenen), sıfır davranış regresyonu. Container yeniden derlenip
(`docker-compose build dima-backend`) yeniden başlatıldı.

**Kapsam dışı (bilinçli, bu turda YAPILMADI)**: yapısal zincir çıkmazının Discovery
fallback'i, dürüst ret'in SPESİFİK açıklamasını (`reason`, ör. "OEE cube'u personel boyutu
içermemektedir...") Discovery'nin KENDİ trace/note'una TAŞIMIYOR — Discovery başarılı olursa
bu zaten önemsizleşiyor (kullanıcı gerçek bir cevap alıyor), ama Discovery de BAŞARISIZ
olursa kullanıcı yalnız Discovery'nin JENERİK dürüst-retini görür, yapısal zincirin
SPESİFİK nedenini DEĞİL — küçük bir netlik kaybı, ayrı bir iyileştirme olarak bırakıldı.

### §E.4 bulgusu (1 Ağustos 2026 — kod okunarak doğrulandı, denendi ve GERİ ALINDI)

Plan, route()'un tek-ölçü sınırlamasını (`cq = {"cube": cube, "measures": [measure]}`)
tek-shot sorularda gevşetmeyi, mevcut `cross_cube_add()`'i (şu an yalnız TAKİP
mesajlarında çalışıyor) fresh route() sonucuna da uygulayarak önerdi. Uygulandı,
canlı test edildi: **`_match_cube()`** (`app/cube_router.py:494-544`) — çapraz-cube
ADAY tespiti route()'un EN BAŞINDA olur (`cube_meta = _match_cube(q, schema)`,
satır 1337) — bu fonksiyon bilinçli olarak "birden fazla cube-düzeyi sinonim
eşleşirse ve KIRILAMAZSA → None (çapraz konu → LLM)" der. Bu şemadaki HER cube
kendi TEMEL ölçüsünü KENDİ üst-düzey sinonim listesinde de taşıyor (ör. `oee`
cube'unun `synonyms:` listesi `oee` kelimesini İÇERİR, yalnız ölçü-düzeyinde değil)
— yani "X hesapla, ayrıca Y ekle" cümlesinde Y BAŞKA bir cube'un ölçüsüyse, `_match_
cube` cümlenin TAMAMINA bakıp İKİ cube'u da "hit" sayar ve `route()` `cube_meta is
None` dalında DAHA cross_cube_add'e gelmeden None döner. Canlı doğrulama: "makine
bazında toplam ciro hesapla, ayrıca oee de ekle" → `_match_cube` → `None` (kod
okunarak VE çalıştırılarak doğrulandı). **Sonuç**: eklenen kod ZARARSIZDI (yalnız
`_ADD_RE` eşleşirse çalışır, route_hit zaten None ise hiç çağrılmaz) ama bu şemada
PRATİKTE neredeyse hiç tetiklenmiyor — gerçek bir çözüm `_match_cube`'ün KENDİSİNE
(projenin EN hassas, en çok test edilmiş fonksiyonu) bir "ekle-niyeti tespit edilirse
ambiguity kontrolünden ÖNCE cümleyi böl" mantığı eklemeyi gerektirir — bu, plan'ın
"SIKI doğrulanmalı" uyarısının kapsadığından ÇOK daha büyük/riskli bir değişiklik.
**Karar**: eklenen kod GERİ ALINDI (fayda-sıfır karmaşıklık istenmiyor); MEVCUT 2-
mesajlı akış ("X hesapla" → "ayrıca Y ekle", zaten çalışıyor ve test edilmiş) çapraz-
cube ölçü ekleme için desteklenen yol olarak KALIYOR. `_match_cube` üzerinde cümle-
bölme mantığı istenirse bu AYRI, dikkatli bir tasarım/onay turu gerektirir.

**Doğrulama (1 Ağustos 2026)**: `pytest` tam paket → 461 passed, 2 pre-existing (bu
oturumdan ÖNCE de başarısız, `git stash` ile TEKRAR doğrulandı: `test_vqr_yakin_
eslesme_olcu_uyusmazliginda_atlanir`, `test_eval_gate_answered_precision_dusmez`) —
YENİ regresyon YOK. Frontend `tsc --noEmit` → 0 hata; `eslint .` (tüm proje) → 0
hata, pre-existing/alakasız uyarılar dışında.

---

## Context

Kullanıcı ürünü canlı kullanırken 13 ayrı sorun/eksik gözlemledi (12'si ilk mesajda, 13.'sü
sohbet sırasında eklendi: LLM-kaynaklı grafiklerde zoom çalışmıyor). Talimat açıktı: HER
birinin kök nedenini KODDA araştır (tahmin yok), sonra hepsini TEK bir yol haritasına dök.
Bu KOD DEĞİŞİKLİĞİ İÇERMİYOR — yalnız araştırma + plan. 4 paralel Explore agent'ı ile HER
madde gerçek kod okuması, canlı-şemaya karşı test (Bug 1 üç kez tekrarlanıp doğrulandı),
git-log/commit tarihi kontrolü (Bug 13) ve repo-geneli grep ile (spekülasyon YOK)
araştırıldı. Aşağıdaki HER bulgu dosya:satır kanıtlıdır.

**DÜZELTME NOTU #1 (1 Ağustos 2026 — kullanıcı testiyle çürütüldü)**: Bu bölümün ilk taslağı
"Madde 13 zaten düzeltilmiş, Madde 1 yalnız VQR-cache görünümü" diyordu. Kullanıcı TEMİZ bir
rebuild (`sıfırdan kurdum`, **backend VE frontend ayrı ayrı rebuild edildi** — kullanıcı bunu
açıkça doğruladı, "frontu ayrıca rebuild ettim" — yani deploy-senkron teorisi ELENDİ) sonrası
HER İKİSİNİ de DEĞİŞMEDEN tekrar gözlemledi. Kök nedeni satır satır tekrar araştırıp
DOĞRULANMIŞ gerçek şu:

1. **Madde 1 için gizem YOK, benim yanlış ifademdi**: bu segment (13 maddenin araştırılması)
   SAF ARAŞTIRMA idi, `_period_hit_words()` düzeltmesi (§A1) HENÜZ KODA UYGULANMADI — yalnız
   PLANLANDI. "nisan→lisans" bugu'nun temiz DB'de, ilk mesajda AYNEN tekrar etmesi TAMAMEN
   BEKLENEN bir sonuçtur. §A1 aşağıda hâlâ geçerli ve YAPILACAK.
2. **Madde 13 — kod ikiliği YOK, KESİNLEŞTİ**: `_attach_viz()` (`backend/app/routers/
   ask.py:1255-1287`) her `/ask` dalına uygulanıyor (cube yolları: 1390/1433/1460/1605;
   Discovery/LLM yolu: **2129** — hepsi AYNI helper). `ResultView.tsx` TEK bileşen, `source`'a
   göre AYRI render dalı YOK. `withZoom()` (`chart.ts:208-224`) kaynağa bakmaksızın SARIYOR.
   Bu, "sistemde ikilik var" hipotezini KOD SEVİYESİNDE ÇÜRÜTÜYOR — ayrı bir bileşene
   "bağlanmadı" değil.
3. **Madde 13 — GERÇEK, DOĞRULANMIŞ kök neden bulundu (kod okunarak, KESİN)**: `_attach_viz`
   → `viz.recommend(result, units, lower_set, cube_query=cq)` çağırıyor; Discovery/LLM
   yolunda `cq=None` geçiliyor (`ask.py:2129`, yalnız `result` var, `cq` yok). `recommend()`
   içinde `_roles_from_cube_query(cube_query, columns)` (`app/viz.py:247-270`) `cube_query`
   `None` ise **`(None, None)` döndürüyor** — yani hiçbir OTORİTER boyut/zaman bilgisi YOK.
   Bu durumda `analyze()` (`app/viz.py:119-242`) kolon ROLÜNÜ (ölçü mü boyut mu) SAF DEĞER
   TİPİNDEN çıkarmak ZORUNDA kalıyor: **satır 146-148 — bir kolonun TÜM değerleri sayısalsa
   "ölçü" sayılıyor, sayısal-olmayan tek değer varsa "boyut"**. Bu, LLM/Discovery'nin ürettiği
   SQL'de AY/YIL/ÇEYREK gibi bir zaman-boyutu **sayısal** döndüğünde (ör.
   `EXTRACT(MONTH FROM tarih) AS ay` → 4, 5 gibi tam sayılar; küp yolunda bu HER ZAMAN
   kanonik metin/tarih string'i olurdu) YANLIŞ sınıflanmasına yol açar: gerçek bir ZAMAN/
   KATEGORİ boyutu yanlışlıkla İKİNCİ bir "ölçü" sayılır, `primary_dim`/`time_col` ya YANLIŞ
   ya da `None` kalır, `kind` "bar/line" yerine "table"a düşer (satır 217-231, `primary_dim`
   yoksa/`time_col` yoksa hiçbir kategorik-eksen mark'ı SEÇİLEMEZ) → FE hiç kategori-eksenli
   bir grafik ÜRETEMEZ → `withZoom()` zaten kategori ekseni gerektirdiğinden (`chart.ts:211`,
   `xAxis` yoksa/array ise erken çıkar) zoom'un GÖRÜNMEMESİ bu durumda TAMAMEN TUTARLIDIR.
   **Bu, cube_query yolunda YAŞANMAYAN, yalnız LLM/Discovery yolunda cq=None geçildiği için
   ortaya çıkan GERÇEK, kod-kanıtlı bir asimetridir** — Agent D'nin "zaten düzeltildi" bulgusu
   YANLIŞ değildi (o güne kadarki İKİ tetikleyiciyi — `viz` hiç hesaplanmaması + sohbet
   resume'inde bayatlaması — GERÇEKTEN kapatmıştı, bkz. `viz.py:18-31` docstring'indeki 31
   Temmuz notu) ama EKSİKTİ: `recommend()`'in KENDİ taban sınıflandırması, yetkili
   dim_cols/time_hint YOKKEN, sayısal-kodlu zaman/kategori kolonlarında YANLIŞ karar
   verebiliyor. **Netlik derecesi**: mekanizma kod okunarak KESİN doğrulandı; kullanıcının
   TAM O ANDA test ettiği sorgunun SQL'i elimde olmadığından "bu spesifik olayın birebir
   nedeni budur" %100 değil ama en güçlü, kod-kanıtlı adaydır — §0'da KESİNLEŞTİRİLECEK.
   Ayrıca `withZoom()` zoom'u yalnız kategori ekseninde **>8** kategori varken ekliyor
   (`chart.ts:214-215`) — bar/line doğru seçilse bile kategori sayısı azsa zoom BEKLENMEZ
   (bug değil); §0'da bu iki ihtimal AYRIŞTIRILACAK.
   Ayrıca **kırılım/kök-neden butonlarının** LLM cevabında GÖRÜNMEMESİ bir "bug" DEĞİL —
   `cube_query` yokluğuna bağlı, BİLİNÇLİ/TASARIM-GEREĞİ bir kısıtlama (§C, henüz YAPILMAMIŞ
   kapsam). Kullanıcının "hiçbir şey çalışmıyor" ifadesi muhtemelen İKİ farklı şeyi (gerçek
   zoom/sınıflandırma bugu + henüz-yapılmamış chip/drill genişletmesi) TEK gözlemde
   birleştiriyor — plan içinde AYRI ele alınıyor.

**DÜZELTME NOTU #2 (kullanıcının mimari sorusu — "viz.py kötü bir yapı olabilir, Wren motoru
zaten grafik üretmede uzman değil mi, daha özgür/serbest bir yapı gerekmez mi?")**: Vendored
`WrenAI-main/.claude/CLAUDE.md` ve `docs/core/guides/genbi.md` bizzat okunarak (spekülasyon
yok) doğrulandı:
- Güncel/aktif Wren projesi **artık SADECE bir semantik SQL motoru** (Rust `wren-core`:
  MDL→DataFusion→lehçe-SQL). Kendi CLAUDE.md'sinin AÇIKÇA belirttiği gibi: eski `wren-ui`/
  `wren-ai-service` (görsel arayüz İÇEREN eski WrenAI ürünü) `legacy/v1` dalına TAŞINDI,
  bu repoda YOK. Yani dima'nın gerçekten çağırdığı `WrenEngine` (`backend/app/wren_service.py`
  — `cube_sql`/`blend_sql`/`dry_plan`/`query`) SADECE SQL üretir/çalıştırır; grafik/görsel
  ile İLGİLİ HİÇBİR API'si YOK (grep: `wren_service.py` içinde `chart`/`viz` sıfır sonuç).
  `dima-frontend-demo-master/CLAUDE.md`'nin "WrenAI açık kaynak tarafında UI sunmadığından
  bu arayüz sıfırdan bizim ürünümüz" notu bununla TAM TUTARLI.
- Tek görsel-ile-ilgili özellik **GenBI** — ama bu, `/ask` gibi anlık bir sorguya "grafik tipi
  öner" API'si DEĞİL; tamamen FARKLI bir ürün: bir CLI-ajanının (`wren genbi build/register/
  verify/deploy`) doğal dilden STATİK, paylaşılabilir bir dashboard UYGULAMASI (Vercel/
  Cloudflare'a deploy edilen, `wren-core-wasm` + parquet-snapshot gömülü, KENDİ BAŞINA bir
  web app) İNŞA ETMESİ iş akışı. dima'nın gerçek-zamanlı `/ask` → JSON → inline-grafik akışıyla
  MİMARİ OLARAK ALAKASIZ — buradan çağrılabilecek bir "chart-recommend" servisi YOK.
- **Sonuç**: Wren'in "grafik üretmede zaten uzman" olduğu, dima'nın bunu göz ardı ettiği
  iddiası KOD/DOKÜMAN KANITIYLA DOĞRULANMADI — böyle bir yetenek mevcut/aktif Wren'de yok.
  `viz.py`'nin kendi mimarisi (sabit `kind` enum'u + `analyze()`/`recommend()` iki katmanı)
  AYRI bir soru: bu, projenin GENELİNDEKİ "LLM'e asla sahte/tahmini karar verdirme, deterministik
  ve test edilebilir kal" felsefesiyle (bkz. `interpret.py`, VQR, "asla sahte dallanma
  uydurma" ilkesi) TUTARLI, bilinçli bir tercih — "daha özgür/serbest" alternatif (LLM'in
  serbestçe ham ECharts/Vega spec'i üretmesi) bu felsefenin TERSİ olur (deterministik/test
  edilebilir olmaktan çıkar). **Tavsiye**: mimariyi DEĞİŞTİRME — asıl, kanıtlı sorun yukarıdaki
  #3'teki sınıflandırma bugu; kapsam-genişletme ihtiyacı zaten §E'de ("yeni `kind` ekle,
  mevcut iki-katman yapıyı KORU") ele alınıyor. Kullanıcı yine de "daha özgür yapı" istiyorsa
  bu AYRI, bilinçli bir mimari karar turu gerektirir (maliyeti: determinizm/test edilebilirlik
  kaybı) — şimdilik plan MEVCUT iki-katmanlı mimariyi korumayı ÖNERİYOR.

**Sonuç — Faz 0'ın gerçek kapsamı** (aşağıda güncellendi): "rebuild + tekrar test" GEREKSİZ
hale geldi (zaten yapıldı, sonuç değişmedi) — bunun yerine (i) Madde 13'ün kod-kanıtlı
sınıflandırma bugunu (yukarıdaki #3) KESİN doğrulayacak, kasıtlı olarak sayısal-kodlu bir
zaman/kategori kolonu üreten bir LLM sorgusuyla test, (ii) zoom eşiğini (>8 kategori) BUNDAN
AYRI olarak izole eden bir ikinci test.

---

## Öncelik/Faz yapısı (özet — detaylar §A-F'de)

| Faz | Kapsam | Madde(ler) | Büyüklük | Risk |
|---|---|---|---|---|
| 0 | Sınıflandırma-bugu doğrulama testi + zoom-eşiği izolasyonu | 13 | Çok küçük | Yok |
| A | Deterministik çekirdek düzeltmeleri (hızlı kazanç) | 1, 8, 9(kısmi), 10, 11(kısmi), 13 | Küçük-orta | Düşük |
| B | Sohbet/panel bağlam UX yeniden tasarımı | 4, 6 | Orta-büyük | Orta (mimari) |
| C | LLM-kaynaklı yanıtlarda kısmi chip/drill etkinleştirme | 2, 3 | Orta | Orta |
| D | Agentic kök-neden/nedensellik motoru | 5, 7 | ÇOK BÜYÜK | Yüksek |
| E | Gelişmiş çapraz-ölçü grafik kompozisyonu | 11 (kalan) | Orta-büyük | Orta |
| F | Düz-dil hesaplama açıklaması | 12 | Küçük-orta | Düşük |

Öneri sıralama: **0 → A → F → B → C → E → D**. Gerekçe: A/F küçük+düşük-riskli+hemen
güven kazandırır; B (UX mimarisi) C ve D'nin ÜSTÜNE oturacağı temel olduğu için onlardan
ÖNCE gelmeli; D (agentic motor) en büyük mimari kararı taşıdığı için EN SONA, kullanıcıyla
küçük bir prototip turu yapılmadan başlanmamalı (Faz 4.11'de izlenen "önce onay, sonra
uygula" deseniyle AYNI).

---

## §0 — Madde 13 sınıflandırma-bugunu doğrulama testi (kod değişikliği yok, hızlı)

A6'yı (aşağıda) UYGULAMADAN ÖNCE, KESİNLİK için tek bir hedefli test: route()'un kasıtlı
kapsam-dışı bıraktığı bir ifadeyle (ör. "her ay için ciroyu ayrı ayrı göster" gibi LLM/
Discovery yoluna düşecek bir soru) LLM'e sayısal-kodlu bir zaman/kategori kolonu ÜRETTİR
(ör. `EXTRACT(MONTH FROM ...)`), backend log'undan/`contract`'tan dönen `viz.kind`'ın
gerçekten "table" (beklenen: "bar"/"line" olmalıydı) olduğunu VE aynı veri şeklini üreten
bir KÜP sorgusunun (cube_query DOLU) doğru "bar"/"line" aldığını doğrula. Bu, yukarıdaki
#3 bulgusunu "kod okuyarak kesin" seviyesinden "canlı doğrulanmış kesin" seviyesine taşır.
AYRICA, BUNDAN BAĞIMSIZ: zoom'un yalnız >8 kategoride eklendiğini (`chart.ts:214-215`)
unutmayıp, test sorgusunun kategori sayısını BİLEREK 9+ tutarak zoom-eşiği davranışını
sınıflandırma bugundan AYRIŞTIR.

---

## §A — Deterministik çekirdek düzeltmeleri (hızlı kazanç, düşük risk)

### A1 — Madde 1: "nisan" → "lisans" yanlış typo-chip'i
**Kök neden (canlı şemaya karşı 3 kez doğrulandı, KESİN)**:
1. `app/cube_router.py` `_period_hit_words()` (satır ~1074-1092) ayları bulmak için
   `re.search()` KULLANIYOR — yalnız İLK eşleşmeyi buluyor. "mayıs ayı cirosunu nisan ayına
   göre karşılaştır" sorusunda yalnız `{'ayi','mayis'}` yakalanıyor, "nisan" SESSİZCE
   düşüyor → `partial_unknowns()` onu `unknown=['nisan']` olarak işaretliyor.
2. `_match_cube()` "ciro" üzerinden `parti` cube'una çözülüyor → `typo_correct()` fuzzy
   sözlüğü YALNIZ `parti`'nin kendi sözlüğüne daraltıyor (`_catalog_vocabulary(only_cube=
   parti)`).
3. `parti` cube'unun `egitim` (eğitim seviyesi) boyutunun GERÇEK kategorik değerleri
   arasında **"Lisans"** var (`demo/build_data.py:576`, tamamen tarihle ALAKASIZ bir alan) —
   `wren_service.py:384-428`'de runtime'da doldurulan `dimension_values`'tan geliyor.
4. difflib "nisan" vs "lisans" benzerliğini **0.727** buluyor — `_TYPO_MID=0.65` (öneri eşiği)
   ile `_TYPO_HIGH=0.82` (otomatik-düzelt eşiği) ARASINDA → tam olarak gözlenen
   `{"kind":"suggest","from":"nisan","to":"lisans"}` çıktısını üretiyor.
5. "İkinci seferde çalışıyor" gizemi ÇÖZÜLDÜ: `app/routers/ask.py:1445-1446` VQR'ın
   `near_exact()`'ini route()/typo_correct'ten ÖNCE çalıştırıyor; VQR her başarılı LLM/
   Discovery cevabını `source="auto"` ile OTOMATİK yazıyor (`ask.py:1386,2111`) — bu TAM
   METİN bir kez BAŞARIYLA (muhtemelen bu oturumdaki test sorgularından biri) cevaplanmışsa,
   sonraki AYNI soru literal-eşleşmeyle VQR'dan dönüyor, buggy typo-correct yoluna HİÇ
   uğramıyor.

**Düzeltme planı**:
- `_period_hit_words()`'ü `re.search` yerine `re.finditer` (TÜM ay eşleşmelerini topla)
  kullanacak şekilde düzelt — çok küçük, izole bir değişiklik.
- Daha DERİN, kalıcı düzeltme: `partial_unknowns()`/`typo_correct()`'e girmeden ÖNCE,
  `date_filters()`/`_period_hit_words()`'ün TANIDIĞI TÜM kelimeleri (yalnız İLKİNİ değil)
  "unknown" adaylığından ÇIKAR — tarih ifadeleri KENDİ deterministik mekanizmasıyla (date_
  filters) çözülüyor, typo-correction'ın bunlara HİÇ dokunmaması gerekir (ayrı bir kavram
  sınıfı). Bu, "ay adı + kategorik-değer çakışması" sınıfının TAMAMINI (yalnız bu örneği
  değil) kapatır.
- **Test**: `tests/test_cube_router.py`'ye "mayıs ayı cirosunu nisan ayına göre karşılaştır"
  İÇİN `typo_correct()` çağrısının `fixes == []` döndüğünü doğrulayan bir regresyon testi
  (mevcut `test_hesapla_fiili_typo_onerisine_donusmez` deseniyle AYNI).

### A2 — Madde 8: "grafik yap" tabloyu grafiğe çevirmiyor
**Kök neden (KESİN)**: `app/routers/ask.py:326-342` `_VIZ_MAP`'teki jenerik "grafi" kökü
`view_hint`'i literal `"chart"` string'ine set ediyor. Ama `dima-frontend-demo-master/src/
components/ResultView.tsx:206`'daki `hintKind` eşleştirmesi yalnız SPESİFİK grafik türlerini
(`line/bar/pie/heatmap/facet/...`) tanıyor — **"chart" listede YOK**. `defaultView()`
(206-224) yalnız `hintKind` varsa KOŞULSUZ override ediyor (satır 214); jenerik "chart" hint'i
bu kontrolü GEÇEMEDİĞİ için satır 219'a düşüyor: `return a.kind==="none" ? "table" : "chart"`
— yani yalnız backend'in KENDİ otomatik kararı zaten tablo/pivot DEĞİLSE kazanıyor. Backend
`app/viz.py:217-231` ise `len(dims)>2` ya da ölçü yoksa OTOMATİK "table" zorluyor. Sonuç:
SPESİFİK istek ("pasta grafik yap") çalışıyor, JENERİK istek ("grafik yap") çalışmıyor.
**Düzeltme**: `ResultView.tsx:214`'teki koşula `|| hintBase === "chart"` ekle (`hintBase`
zaten `_VIZ_MAP`'in kökünden gelen jenerik sinyal — mevcut değişkenin adını doğrula/kullan).
Küçük, tek satırlık, düşük riskli bir düzeltme. **Test**: mevcut `_viz_hint` golden testine
("pasta grafik" senaryosu) bir "genel grafik" varyantı ekle.

### A3 — Madde 9 (kısmi): VQR mid-conversation'da AYNI soruyu tekrar LLM'e gönderiyor
**Kök neden (KESİN)**: `app/routers/ask.py:1445` VQR kontrolünü YALNIZ `if not is_followup`
koşuluyla çalıştırıyor. `is_followup` (satır 1207-1209) `body.cube_query` YA DA
(`prev_sql`+`history`) varsa `True` olur — yani bir sohbet DEVAM ederken (normal durum)
gönderilen AYNI (literal tekrar) soru bile VQR'ı hiç GÖRMEDEN follow-up/refine yoluna düşüyor.
**Yazma tarafı ZATEN doğru** (`ask.py:1386,2111`, `source="auto"`, her başarılı LLM/Discovery
cevabından sonra) — **eşleştirme tarafı** (`vqr.py near_exact()`, önce literal-normalize eşitlik,
sonra embedding≥0.92/lexical-Dice≥0.85 yedek) da doğru — yalnız `is_followup` GATE'İ mid-
conversation'da devreye HİÇ girmesine izin vermiyor. **Kalıcılık**: `control_plane/models.py:
185-208 VerifiedQuery`, Postgres/SQLite (`control_plane/db.py`) — BİLİNÇLİ olarak DB'de
(dosya/YAML DEĞİL), `main.py`/`db.py`'de YIKICI bir reset YOK. **Bu KESİNLİKLE ephemeral
DEĞİL** — Docker resetlerinde veri KAYBOLUYORSA, bu koddan değil, kullanıcının DB volume'unu
DA silen bir reset komutundan kaynaklanıyor olmalı (bkz. §A3-not aşağıda).
**Düzeltme planı**: `is_followup` gate'ini gevşet — `body.cube_query`/`prev_sql` varlığından
BAĞIMSIZ olarak, gelen soru metni (normalize edilmiş) `history`'deki ÖNCEKİ bir soruyla YA DA
VQR'daki bir kayıtla LİTERAL eşleşiyorsa, follow-up mantığına düşmeden ÖNCE VQR'ı dene. Dikkat:
bu değişiklik "bağlamı algılaması lazım" (kullanıcının kendi notu) ile ÇELİŞMEMELİ — yalnız
GERÇEKTEN literal/near-literal tekrarlar için VQR'a öncelik ver, GERÇEK bir takip sorusunu
("aylara göre kır" gibi, `prev_sql`'e bağımlı) ETKİLEME. **Test**: mevcut VQR testlerine
"aynı soru, history DOLUYKEN tekrar sorulunca VQR'dan LLM'siz döner" senaryosu ekle.

**§A3-not (kullanıcıya iletilecek operasyonel bulgu)**: VQR'ın DB-tabanlı olması ZATEN
endüstri standardıdır ("semantic/verified query cache" deseni — LLM'e giden maliyetli/riskli
yolu ATLAMAK için DB'de saklanan soru→SQL çiftleri, tipik olarak Redis/Postgres/pgvector gibi
bir depoda tutulur, ASLA kod/YAML'a GÖMÜLMEZ çünkü sürekli BÜYÜYEN, deploy-bağımsız bir veri
sınıfıdır). Şema/ölçü/sinonim tanımları (cube YAML'ları) ise DOĞRU şekilde koda/YAML'a
gömülü — bunlar VERSİYONLANAN, gözden geçirilen, deploy edilen İÇERİKTİR, VQR'ın öğrendiği
GEÇİCİ/artımlı soru-cevap çiftleriyle AYNI KATEGORİ DEĞİLDİR. Eğer Docker resetlerinde VQR
verisi GERÇEKTEN kayboluyorsa, sorun kod DEĞİL, kullanılan reset komutunun DB volume'unu DA
sildiğidir (`docker compose down -v` gibi) — `-v` bayrağı OLMADAN (yalnız `down`+`up --build`)
resetlemek DB verisini KORUR. Bu, koddan ÖNCE kontrol edilmesi gereken bir operasyonel
detaydır.

### A4 — Madde 10: 2-birimli (ör. % ve kW) grafiklerin YANLIŞ birleştirilmesi
**Kök neden (KESİN)**: `app/viz.py:353-362` `unit_count==2` durumunda yalnız
`spec["dual_axis"]=True` SET EDİYOR (grafik türü bar/line KALIYOR) — ama `dualAxis`
frontend'de (`chart.ts:67,91`) PARSE ediliyor ve **repo-genelinde HİÇBİR YERDE tekrar
OKUNMUYOR** (grep ile doğrulandı — ölü bayrak). Bugün GERÇEKTEN çalışan 2-birim-ayırma,
TAMAMEN BAĞIMSIZ bir eski "combo" sezgiselinden geliyor (`chart.ts:242-346`) — yalnız
"tümü" ölçü modu + TEK paylaşılan x-ekseni + **hiçbir seri/kırılım boyutu YOKKEN** devreye
giriyor (satır 248 `!comboSeriesDim` şartı). **Somut boşluk**: sorguda 2-birimli ölçülerin
YANINDA bir KIRILIM boyutu DA varsa (ör. "ay VE makine bazında oee ve duruş dakikası"),
combo bloğu TAMAMEN atlanıyor, dual-axis yedeği DE YOK — iki birim TEK eksende EZİLİYOR
(kullanıcının "büyük hatalara sebep oluyor" dediği TAM senaryo).
**Düzeltme planı**: üç ayrı mekanizma (çalışan-ama-dar combo, ölü dual_axis bayrağı,
≥3-birim facet_measure) yerine TEK, TUTARLI bir kural: **kırılım boyutu OLAN 2-birimli
durumu, ZATEN VAR OLAN `facet_measure` (yan-yana ayrı grafikler) eşiğine DAHIL et** —
bugün yalnız `unit_count>=3`'te tetiklenen bu mekanizmayı `unit_count>=2 VE kırılım boyutu
mevcut` durumuna da GENİŞLET (backend `app/viz.py`'de eşik değişikliği + frontend
`facetMeasure` renderer'ının zaten var olan yan-yana grafik mantığını YENİDEN KULLAN — yeni
bir görsel dil İCAT ETME). Kırılımsız 2-birim durumu (mevcut combo) DOKUNULMADAN kalır —
zaten doğru çalışıyor. Ölü `dual_axis` bayrağı ya bu yeni mantığa entegre edilir ya da
BİLİNÇLİ olarak kaldırılır (kafa karıştırıcı, kullanılmayan bir alan olarak bırakılmamalı).
**Test**: `tests/` içinde `viz.py::recommend()`'e 2 farklı birimli ölçü + 1 kırılım boyutu
veren bir birim testi + `chart.ts`'e karşılık gelen bir doğrulama.

### A5 — Madde 11 (kısmi, hızlı kazanç): "personel" sinonim eksikliği
**Kök neden (KESİN)**: `route()`'un kapsam-kapısı (`_coverage_ok`/`_uncovered`,
`cube_router.py:1111-1130,1438-1459`) "personel" ve "etkisini" kelimelerini TANIMIYOR —
`parti` cube'unun operatör boyutu sinonimleri yalnız "operatör/çalışan baz/kişi baz"
(`parti/metadata.yml:15-17` — YORUM AÇIKÇA "verim/verimlilik OEE kimliğidir → parti'de
TUTULMAZ" diyor, kasıtlı bir ayrım). Bu YÜZDEN route() bu soruyu HONEST olarak LLM'e
bırakıyor (sessiz yanlış DEĞİL). **Düzeltme (küçük, düşük risk)**: "personel" kelimesini
operatör boyutunun sinonim listesine EKLE (`parti/metadata.yml` ve/veya `ik` cube'u,
mevcut sinonim-ekleme desenini kullanarak) — bu TEK örneği HEMEN çözer. Kalan (multi-measure
kompozisyon) kısmı §E'de.

### A6 — Madde 13 (asıl kod-kanıtlı kısım): LLM/Discovery yolunda sayısal-kodlu zaman/kategori
kolonu YANLIŞ "ölçü" sayılıyor
**Kök neden (kod okunarak KESİN, §0'da canlı doğrulanacak)**: `app/viz.py::recommend()`
Discovery/LLM yolunda `cube_query=None` alır (`ask.py:2129`) → `_roles_from_cube_query(None,
columns)` (`viz.py:247-270`) `(None, None)` döner → `analyze()` (`viz.py:136-149`) kolon
rolünü SAF DEĞER TİPİNDEN çıkarmak zorunda kalır: **bir kolonun TÜM değerleri sayısalsa
"ölçü" sayılır** (satır 144-148). Küp yolunda zaman/kategori boyutları HER ZAMAN metin/tarih
string'idir (schema'nın kendi biçimi); ama LLM'in ürettiği SQL ay/yıl/çeyreği SAYISAL
döndürebilir (ör. `EXTRACT(MONTH FROM tarih) AS ay`) — bu durumda gerçek bir boyut yanlışlıkla
İKİNCİL bir "ölçü" sayılır, `time_col`/`primary_dim` ya yanlış ya `None` kalır, `kind` "table"a
düşer (satır 217-231) — kategori-eksenli hiçbir mark ÜRETİLMEZ, dolayısıyla `withZoom()` da
(kategori ekseni gerektirir) hiç DEVREYE GİREMEZ. Bu, cube_query'li yolda YAŞANMAYAN, yalnız
`cq=None` geçildiği için ortaya çıkan gerçek bir asimetridir.
**Düzeltme planı**: `analyze()`'e (ya da `recommend()`'in LLM-yolu çağrısına) `dim_cols`/
`time_col_hint` YOKKEN de kullanılabilecek İKİNCİL bir sinyal ekle — mevcut `_TIME_NAMES`
kolon-adı sözlüğünü (satır 41-44) sayısal kolonlara da UYGULA (yalnız sayısal-olmayan
kolonlara değil): kolon adı `_TIME_NAMES` içindeyse (ör. "ay", "yil", "ceyrek") DEĞER TİPİNDEN
BAĞIMSIZ olarak boyut/zaman say. Ayrıca düşük-kardinaliteli (ör. ≤12 ayrık değer, satır
sayısının küçük bir oranı) sayısal kolonları da (isim eşleşmese bile) "muhtemel kategori/
boyut" adayı olarak değerlendiren bir sezgisel eklenebilir — ama bu İKİNCİ kısım YANLIŞ-
POZİTİF riski taşır (gerçek düşük-kardinaliteli bir ÖLÇÜYÜ — ör. "yıldız sayısı 1-5" — boyut
sanabilir), bu yüzden yalnız isim-eşleşmesi (birinci kısım) KESİN/düşük-riskli, ikinci kısım
OPSİYONEL ve dikkatli test gerektirir. **Test**: `tests/` içinde `viz.py::analyze()`'e
`dim_cols=None` + sayısal "ay" kolonu (`[1,2,3]` gibi) veren, `time_col=="ay"` ve
`kind in ("bar","line")` bekleyen bir birim testi — mevcut `analyze()`/`recommend()` test
desenleri YENİDEN KULLANILIR.

---

## §B — Sohbet/panel bağlam UX yeniden tasarımı (Madde 4 + 6, birleşik)

### Araştırma bulgusu (Madde 4)
`page.tsx`'teki `ChatPanel`'in `onSelect` handler'ı (satır 250-259) TIKLANAN geçmiş bir
mesaja geçildiğinde `active`/`contextCq`/`prevSql`'i O MESAJA doğru şekilde YENİDEN
ÇAPALIYOR — kod düzeyinde "hep en sonuncuyu bağlam sanma" iddiası YANLIŞ. Gerçek boşluk:
**"görüntüleme" ile "seçme" AYNI eylem** (`ChatPanel.tsx`'te ayrı bir "gözat" eylemi YOK,
kaydırma `active`'i HİÇ değiştirmiyor) VE sağ panelde o an hangi mesajın "aktif bağlam"
olduğunu gösteren KALICI/BELİRGİN bir gösterge YOK. Kullanıcı sol tarafta eski bir mesajı
OKUYORSA (tıklamadan) ama sağ panel BAŞKA bir şey gösteriyorsa, yazdığı yeni mesaj sağdaki
(doğru ama kullanıcının BEKLEMEDİĞİ) bağlamı kullanır. Bu bir MANTIK hatası değil, bir
İLETİŞİM/AFFORDANCE boşluğudur.

### Tasarım hedefi (Madde 6, kullanıcının kendi tarifi)
- Bağlamsal bir takip AYNI panelin ALTINA eklenir (kaydırılabilir, "cevap 2" gibi) — sağ
  panel bağlamı KORUR.
- Solda farklı konular AYRI mesaj olarak kalır.
- YENİ bir bağlam başladığında sohbette GÖRSEL bir işaretçi olur; tıklanınca TEMİZ panel
  açılır.

### Mevcut altyapıdan YENİDEN KULLANILABİLECEKler (araştırmayla doğrulandı)
`AnalysisCanvas.tsx` + `page.tsx`'teki `canvasMode`/`canvasItems` (Faz 4.11) ZATEN
"birden çok AskResponse'u biriktirip kaydırılabilir göster" mekanizmasının ÇEKİRDEĞİNİ
taşıyor (`CanvasCard` render deseni, `stableId` WeakMap kimlik mekanizması, sürükle-sırala
UI kabuğu — `@dnd-kit` ile). AMA bugünkü tasarımı: (a) `canvasMode` AÇIK DEĞİLSE HİÇ
biriktirmiyor (varsayılan davranışı DEĞİŞTİRMEMEK için BİLİNÇLİ), (b) TÜM biriken öğeleri
DÜZENSİZ, tek bir liste olarak tutuyor — "bu öğe şu öğenin DEVAMI" kavramı YOK, (c)
`ReportPanel` (tek-aktif-rapor modeli) ile `AnalysisCanvas` (tuval modeli) birbirinin
YERİNE geçen, TOGGLE'lı iki AYRI görünüm — Madde 6'nın istediği "OTOMATİK, konuya göre
grupla" davranışı YOK.

### Önerilen yaklaşım (yüksek seviye — detay tasarım AYRI bir onay turu gerektirir, Faz 4.11
ile AYNI ilke)
1. **"Konu/thread" kavramı tanımla**: iki ardışık mesaj AYNI "thread"e mi ait, yoksa YENİ
   bir konu mu — heuristik: `cube_query.cube` aynıysa VE/VEYA backend `is_followup`/
   `structural_followup` sinyali (`ask.py:1207-1209`, ZATEN hesaplanıyor ama şu an yalnız
   sorgu inşası için kullanılıyor, UI'a HİÇ YANSITILMIYOR) `True` ise → AYNI thread; aksi
   halde YENİ thread. Bu sinyali `AskResponse`'a (ör. `is_new_topic: bool`) EKLEYİP
   frontend'e TAŞI — YENİ bir tahmin mantığı İCAT ETME, zaten hesaplanan sinyali YENİDEN
   KULLAN.
2. **ReportPanel'i "thread yığını" modeline genişlet**: bugünkü tek `data: AskResponse`
   prop'u, aynı thread'e ait `AskResponse[]` dizisine (en altta en yeni, kaydırılabilir)
   dönüşür — `AnalysisCanvas.tsx`'in `CanvasCard` render mantığı BİREBİR yeniden
   kullanılabilir (kod tekrarı yerine ORTAK bir alt-bileşene çıkarılabilir).
3. **`ChatPanel.tsx`'e "yeni bağlam" işaretçisi**: `is_new_topic` true olan mesajların
   ÜSTÜNE ince bir ayraç + etiket ("yeni konu") eklenir; tıklanınca o thread'in İLK
   mesajından başlayan panel açılır (yalnız o thread'in item'ları gösterilir).
4. **Sağ panelde "hangi thread aktif" göstergesi**: küçük bir breadcrumb/başlık —
   kullanıcının Madde 4'te belirttiği kafa karışıklığını doğrudan giderir.
**Bu bir mimari karar** — kullanıcıyla küçük bir prototip/onay turu ÖNERİLİR (4.11'in
kendi planındaki gibi), doğrudan tam kapsamlı uygulamaya GEÇİLMEMELİ.

---

## §C — LLM-kaynaklı yanıtlarda chip/drill (Madde 2 + 3, birleşik)

### Araştırma bulgusu (KESİN — spekülasyon değil)
İncelenen HER chip/drill noktası (next_steps, recommendations, 🔔 zamanla, +panoya ekle,
⤵ kök neden butonu, grafik-tıklama→drill) `data.cube_query` doluluğuna KOŞULSUZ bağlı
(`app/routers/ask.py:603-645`'teki `_attach_next_steps`/`_attach_recommendations`'ın
`if not resp.cube_query: return` erken-çıkışı; `ReportPanel.tsx`'teki HER ilgili render
koşulu `data.cube_query &&` içeriyor). **Bu TASARIM GEREĞİ** — next_steps/recommendations
`cube_router.suggest_next_steps`'in kullanılmayan boyut/ölçü ÖNERMESİYLE çalışır, bu
BİLGİ yalnız yapısal bir cube_query'de VAR; ham SQL'de YOK. **"Görünen chip'ler çalışmıyor"
İDDİASI DOĞRULANMADI** — her render koşulunun ARKASINDA çalışan bir handler var; buton HİÇ
render EDİLMİYORSA (Discovery yanıtında olduğu gibi) "tıklasam da açılmıyor" aslında
kullanıcının GRAFİĞE tıkladığı (`onDataPointClick` prop'u da `data.cube_query` koşullu,
`undefined` ise `ResultView.tsx`'teki handler SESSİZCE erken çıkıyor — HİÇBİR hata/geri
bildirim YOK, "hiçbir şey olmadı" hissi TAM OLARAK BURADAN geliyor).

### Düzeltme yaklaşımı (iki katman)
1. **Küçük, hemen yapılabilir (UX dürüstlüğü)**: chart tıklaması/kök-neden butonu Discovery
   yanıtında GÖRÜNMÜYORSA bile, kullanıcı grafiğe tıkladığında SESSİZCE hiçbir şey
   olmaması yerine küçük bir ipucu göster (ör. "bu sonuç LLM tarafından üretildi, kırılım
   için 'sql göster'e bakabilirsin" tarzı bir tooltip/toast) — `ResultView.tsx`'in
   `handleChartDataPointClick`'ine `onDataPointClick` yoksa bir NO-OP yerine görünür bir
   geri bildirim ekle. Düşük risk, hemen değer.
2. **Orta-büyük (gerçek kapasite artışı)**: Discovery/LLM yanıtları için de EN AZINDAN
   "ilgili related_cubes" ve "ham satırlar" seviyesini AÇMANIN bir yolu var mı araştırılmalı
   — `app/drill.py::related_cubes()` yalnız cube+aktif-boyut gerektiriyor; Discovery'nin
   ürettiği SQL'den HANGİ cube/tabloların kullanıldığını (LLM'in kendi ürettiği
   `touched_models`/contract kaydından, `_record_contract`'ın zaten TUTTUĞU bilgiden)
   çıkarıp KISMİ bir "ilişkili veri" önerisi sunmak MÜMKÜN olabilir — ama bu YARIM/tahmini
   bir mekanizma olur, "asla sahte dallanma uydurma" ilkesiyle DİKKATLİCE dengelenmeli. Bu
   madde, aşağıdaki §D (agentic motor) ile BİRLEŞİK düşünülmeli — Discovery yanıtlarının
   GERÇEK çözümü muhtemelen "chip taklit etmek" değil, §D'nin sağladığı GERÇEK nedensel
   sorgulama yeteneğidir.

---

## §D — Agentic kök-neden/nedensellik motoru (Madde 5 + 7, EN BÜYÜK madde)

### Araştırma bulgusu (KESİN, en önemli bulgulardan biri)
`app/interpret.py` TAMAMEN deterministik ve YALNIZ "ne oldu"yu anlatıyor (`trend`/`peak`/
`bottom` fact türleri — modül docstring'i AÇIKÇA "LLM aritmetik YAPMAZ" diyor); HİÇBİR
şablon "X nedeniyle" / "caused by" türünde bir NEDEN cümlesi ÜRETMİYOR (grep: sıfır sonuç).
`app/drill.py` (Faz 4.10) tam olarak bu iş İÇİN tasarlandı ama KENDİ docstring'i AÇIKÇA
"İleride bir agent'ın AYNI mekanizmayı otomatik gezmesi HEDEFLENİR" diyor — yani BİLİNÇLİ
olarak yalnız İNSAN-tıklama-güdümlü bırakıldı. `ask()` (backend `app/routers/ask.py`,
~1000 satır) İÇİNDE `/ask/drill`'e ya da drill.py fonksiyonlarına TEK bir referans YOK
(grep: sıfır). **Sonuç: sistem BUGÜN "neden düştü" tarzı bir soruya OTONOM olarak
nedensellik ARAYAMIYOR — yalnız İNSAN, DrillDownPanel'de TEK TEK tıklayarak bu veriye
ulaşabiliyor.** Bu GERÇEK, doğrulanmış bir boşluk (varsayım değil).

### Ne inşa edilmeli (yüksek seviye tasarım — bu, AYRI ve DİKKATLİ bir tasarım turu
gerektiren en büyük karardır)
1. **Niyet tespiti**: bir soru "neden/sebep/ne oldu/nasıl düzeltirim" gibi NEDENSEL/
   TEŞHİS-türü mü, yoksa normal bir veri sorgusu mu — deterministik bir kelime-kalıbı
   kontrolüyle (route()'un kendi "kapsam kapısı" felsefesiyle TUTARLI, LLM'e SORMADAN
   ÖNCE ucuz bir ön-filtre) BAŞLANABİLİR, LLM-tabanlı niyet sınıflandırmasına
   GENİŞLETİLEBİLİR.
2. **Araç-çağıran (tool-calling) orkestrasyon**: nedensel niyet tespit edilirse, bir LLM
   (mevcut `app/llm.py::build_generator()` sağlayıcı soyutlaması YENİDEN KULLANILIR) bir
   dizi YAPISAL "araç" çağırır — BUNLAR YENİ kod DEĞİL, `app/drill.py`'nin ZATEN VAR OLAN
   saf fonksiyonları (`expand_cube_query`, `select_cube_query`, `flag_outliers`,
   `related_cubes`, `jump_to_related_cube`, `build_raw_row_sql`) `/ask/drill`'in kendi
   action-motoruyla AYNI şekilde SUNULUR — yalnız çağıran artık bir İNSAN tıklaması değil,
   LLM'in ARAÇ SEÇİMİdir (Anthropic tool-use / OpenAI function-calling deseni — HER İKİ
   sağlayıcı da destekliyor, `app/llm.py`'nin sağlayıcı-soyutlamasına YENİ bir metod
   eklenerek).
3. **Güvenlik/sınır ilkeleri (kritik, atlanmamalı)**:
   - **Maksimum hop sayısı** (ör. 5-6 adım) — sonsuz döngü/kontrolsüz maliyet riski YOK.
   - **HER adım kendi Query Contract kaydını ÜRETİR** (mevcut `_drill_record_contract`
     deseni AYNEN kullanılır) — agent'ın izlediği TÜM yol DENETLENEBİLİR kalır.
   - **Veri güvenliği** (kullanıcının kendi vurgusu): agent'a giden ARA sonuçlar PII-
     maskelenmiş olmalı (mevcut `app/pii.py::mask_query_result` AYNEN kullanılır) VE
     LLM'e yalnız ŞEMA+ÖZET gönderilir, ham satırlar İNTERPRET katmanından GEÇMEDEN
     asla LLM promptuna girmez (mevcut `interpret.py` ilkesiyle TUTARLI).
   - **Dürüst durma**: agent bir noktada "daha fazla ilişkili veri YOK" derse (mevcut
     `related_cubes()`'un boş dönmesi gibi), ZİNCİRİ UYDURMADAN dürüstçe durur.
4. **Sentezleme**: zincirin SONUNDA, agent topladığı GERÇEK bulguları (her adımın
   `formula_explanation`+sonuç verisi) tek bir Türkçe NEDENSEL anlatıya dönüştürür (ör.
   "Ciro düşüşü pazaryeri kanalından kaynaklanıyor (-%38); bu kanalda X ürününün stoğu
   tükenmiş, satış sıfırlanmış").
5. **Aksiyon-önerisi katmanı** (Madde 7'nin ikinci örneğinden): kök neden BULUNDUKTAN
   SONRA, "ne yapmalıyım" tarzı bir takip sorusu GELİRSE, sistem (a) somut bir öneri
   (tedarik süresi + önerilen sipariş adedi gibi — GERÇEK veriden hesaplanan, uydurma
   DEĞİL) + (b) opsiyonel bir "taslak hazırlayayım mı" AKSİYONU sunabilir. Bu AYRI, daha
   KÜÇÜK bir alt-özellik — muhtemelen bir "taslak e-posta oluştur" YENİ bir LLM-çağrısı
   şablonu (GERÇEK e-posta GÖNDERMEZ, yalnız TASLAK metni gösterir — kullanıcı onaylamadan
   hiçbir dış eylem TETİKLENMEZ, güvenlik ilkesi).

### Neden bu EN SONA bırakılmalı
- En BÜYÜK mimari karar (yeni bir "agent orkestrasyon" katmanı — bu projede HİÇ
  BENZERİ yok).
- Maliyet/gecikme etkisi (çok-adımlı LLM+araç döngüsü) dikkatli ÖLÇÜLMELİ.
- Güvenlik yüzeyi geniş (PII, veri sızıntısı, kontrolsüz döngü riski) — ACELE
  edilmemeli.
- §B (panel/thread UX) ve §C (Discovery yanıtlarında kısmi drill) TAMAMLANMADAN bu
  motorun SONUÇLARINI göstermek için sağlam bir UI YOK.
**Öneri**: bu bölüm İÇİN kullanıcıyla KÜÇÜK, somut bir prototip turu (ör. yalnız TEK bir
örnek senaryoyu — "ciro neden düştü" — uçtan uca çalıştıran, sınırlı-kapsamlı bir ilk
sürüm) AYRI bir onay turunda ele alınmalı.

---

## §E — Gelişmiş çapraz-ölçü grafik kompozisyonu (Madde 11, kalan kısım)

A5'te "personel" sinonim eksikliği (hızlı kazanç) düzeltildikten SONRA bile, KOMPLİKE
kompozisyon (kişi-bazlı sütun + ortalama çizgisi AYNI grafikte, ya da "ölçü A'nın ölçü B
üzerindeki etkisi" karşılaştırması) İÇİN mevcut hiçbir viz-türü TAM UYMUYOR (araştırma:
en yakın aday `scatter`/korelasyon, ama "kişi-bazlı bar + referans-çizgisi" AYRI bir
kalıp). **Yapılacak**: `app/viz.py::recommend()`'e YENİ bir kalıp ekle — "N ölçüsü + M
boyutu, M kategorik VE düşük-orta kardinaliteli İSE: birincil ölçü BAR (kategori-bazlı) +
İKİNCİL ölçü (ya da birincilin ORTALAMASI) YATAY REFERANS ÇİZGİSİ olarak AYNI grafikte"
— `chart.ts`'in ZATEN VAR OLAN combo (bar+line) altyapısı BÜYÜK ÖLÇÜDE yeniden
kullanılabilir (yalnız "ikinci ölçü" yerine "birincinin ortalaması" hesaplanan bir seri
eklenir). route()'un TEK-ölçü sınırlaması (bkz. A5 araştırması, `cube_router.py:1461`)
İÇİN: tek-shot'ta "X hesapla VE Y ile karşılaştır" kalıbını (bugün yalnız TAKİP
mesajlarında `cross_cube_add` ile çalışan mantığı) tek bir SORUYA da uygulayacak şekilde
GENİŞLET — orta-büyüklükte, dikkatli regresyon testi gerektiren bir değişiklik (golden-eval
precision'a DOKUNMAMAK için `tests/test_ask_golden.py`/`eval/cases.yaml` ile SIKI
doğrulanmalı).

---

## §F — Düz-dil hesaplama açıklaması (Madde 12)

### Araştırma bulgusu
**KPI kartları İÇİN bu ÖZELLİK ZATEN TAM ÇALIŞIYOR**: `app/kpi.py::resolve_kpi()` KPI
YAML'ındaki `explain:` alanını (`demo/packs/modul/kpi/cari-oran.yml:13-15` gibi, GERÇEKTEN
düz-dil bir paragraf) `AskResponse.kpi.explain`'e taşıyor, `KpiCard.tsx:132-134` bunu
RENDER EDİYOR. **Sıradan (KPI-olmayan) cube raporları İÇİN aynı yetenek VAR ama
YANLIŞ yere bağlı**: `app/drill.py::formula_explanation()` BİREBİR bu işi yapıyor (ölçü/
filtre/kırılım/zaman-granülerliğini düz Türkçe cümleye çeviriyor) ama YALNIZ `/ask/drill`
ucuna bağlı — normal bir `/ask` cevabı bunu HİÇ ÇAĞIRMIYOR (grep: `formula_explanation`'ın
TÜM 8 referansı `/ask/drill` endpoint'i İÇİNDE).
**Düzeltme (küçük, düşük risk, YENİ mantık İCAT ETMİYOR)**: CUBE-kaynaklı (`source` "cube"
ile başlayan) HER `AskResponse` için, yanıt inşa edilirken `drill.py::formula_explanation
(resp.cube_query, cube_meta)` ÇAĞRILIP sonucu YENİ bir alana (ör. `AskResponse.
calculation_explanation` — DİKKAT: mevcut `AskResponse.explain` ile KARIŞTIRMA, o
provenance/güven metadata'sı taşıyor, BAŞKA bir amaç) yazılır. Frontend'e "+ sql göster"in
YANINA (ya da ÖNÜNE — SQL okumayan kullanıcı İÇİN bu daha ÖNCELİKLİ olmalı) YENİ bir "nasıl
hesaplandı?" bölümü eklenir, bu metni HER ZAMAN (SQL göster açılmasa bile) gösterir. LLM/
Discovery-kaynaklı yanıtlar İÇİN (cube_query yok, deterministik formül-açıklama ÇALIŞMAZ):
ya bu bölüm hiç gösterilmez (dürüst, mevcut ilkeyle TUTARLI), ya da LLM'in KENDİSİNDEN aynı
üretim sırasında kısa bir düz-dil açıklama İSTENİR (küçük bir prompt-eklentisi, ayrı bir
LLM çağrısı GEREKTİRMEDEN). **Test**: `tests/test_drill.py`'nin `formula_explanation`
testlerini YENİDEN KULLANARAK, `/ask`'in normal cevabında da AYNI alanın dolduğunu
doğrulayan bir entegrasyon testi.

---

## Doğrulama (genel)

Her faz kendi alt-bölümünde belirtilen testlerle KAPANIR; §0 zaten mevcut testleri
DEĞİŞTİRMEZ. §A'nın HER maddesi küçük, izole birim testleriyle doğrulanabilir (mevcut
`tests/test_cube_router.py`/`tests/test_kpi.py`/`tests/test_ask_golden.py` desenleri
YENİDEN KULLANILIR). §B/§C/§D için: her biri kendi UYGULAMA turunda, kullanıcıyla küçük
bir prototip/onay adımıyla BAŞLAMALI (bu planın KENDİSİ yalnız YÖN çiziyor, detay tasarım
SONRAKİ turlarda netleşecek — tıpkı Faz 4.11'in kendi planlama-uygulama ayrımında olduğu
gibi).

---

## Kalıcı takip dosyası (kullanıcı talebi)

Kullanıcı talimatı (kelimesi kelimesine): "plan md sini direkt kopyala mv çalıştır vs bunda
vakit kaybetmeyelim yeter ki kontexti unutma" — yeniden yazma/biçimlendirme YOK, plan
onaylandıktan HEMEN SONRA ilk iş bu dosyanın OLDUĞU GİBİ repo köküne kopyalanması:
`cp ~/.claude/plans/genel-projeyi-anla-u-nifty-charm.md
./UX-KRITIK-BULGULAR-YOLHARITASI_2026-08-01.md` (mevcut `HANDOFF_2026-08-01_faz4-tamamlama.md`
/ `FAZ4-SONRASI-ONERILER_2026-08-01.md` isimlendirme kuralına uygun). Bu dosya HER faz
ilerledikçe (bir madde tamamlandığında/düzeltildiğinde) GÜNCELLENECEK — context kaybolsa bile
yalnız bu dosya okunarak 13 maddenin tam durumu anlaşılabilir olacak.
Not: proje kökündeki `CLAUDE.md`/`backend/CLAUDE.md`/`dima-frontend-demo-master/CLAUDE.md`
dosyalarının GÜNCEL OLMAYABİLECEĞİ kullanıcı tarafından belirtildi (1 Ağustos 2026) —
mimari/kural iddiaları için bu dosyalar yerine HANDOFF/FAZ4-SONRASI-ONERILER dosyaları ve
bizzat kod okunmalı.
