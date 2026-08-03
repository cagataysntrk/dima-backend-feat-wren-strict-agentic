"""Pydantic request/response models for the HTTP API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    sql: str = Field(..., description="SQL SELECT executed through the Wren semantic layer.")
    limit: int | None = Field(default=None, ge=1, description="Optional row cap.")


class UploadRequest(BaseModel):
    """Chat-scoped Excel/CSV yükleme (base modu). Dosya base64; python-multipart gerektirmez.
    Veri oturum DuckDB'sine iner (ephemeral) → oto-cube → mevcut NL pipeline."""

    session_id: str = Field(min_length=1)
    filename: str = Field(min_length=1)
    content_b64: str = Field(min_length=1)


class UploadResponse(BaseModel):
    dataset: str                       # kullanıcıya görünen ad (dosya kök adı)
    row_count: int
    columns: list[dict[str, Any]]      # [{orig, name, type, role}]
    suggestions: list[Suggestion] = Field(default_factory=list)  # örnek sorgular


class ConversationOut(BaseModel):
    """Sohbet listesi öğesi (geçmiş kenar çubuğu)."""

    id: str
    title: str
    session_id: str
    message_count: int
    updated_at: str


class ConversationDetail(BaseModel):
    """Tek sohbet + mesajları — resume için. messages = ham AskResponse payload'ları
    (frontend doğrudan render eder; yeniden çalıştırma yok)."""

    id: str
    title: str
    session_id: str
    messages: list[dict[str, Any]]


class AskRequest(BaseModel):
    question: str = Field(..., description="Natural-language question (Turkish or English).")
    limit: int | None = Field(default=None, ge=1)
    execute: bool = Field(default=True, description="If false, only generate + validate SQL.")
    # Konuşmasal daraltma (ADR-0007): önceki kullanıcı mesajları (eski→yeni) ve o anki
    # raporun yapısal CubeQuery durumu. Takip mesajları ("aylara göre", "temmuzu çıkar")
    # bunlarla yorumlanır; motor mevcut sorguyu düzenler.
    history: list[str] = Field(default_factory=list)
    cube_query: dict[str, Any] | None = None
    # Strict-agentic /ask'in takip (follow-up) bağlamı: bir önceki turun `AskResponse.sql`'i.
    # BİLEREK `cube_query`den AYRI bir alan — `cube_query` frontend'de scheduling/dashboard/
    # verify gibi başka özelliklerin de gate'i (gerçek CubeQuery şekli varsayıyorlar); onu
    # ham SQL taşımak için yeniden kullanmak o özellikleri yanlışlıkla wren_sql cevaplarında
    # da açardı. Yalnız history doluyken ve bu alan set edilmişken /ask bunu bir takip
    # düzenlemesi (edit) olarak ele alır (bkz. routers/ask.py generate_followup_sql).
    prev_sql: str | None = None
    # Sohbet oturumu kimliği (client üretir) — kalıcı logda chat'i yeniden kurmak için.
    session_id: str | None = None
    # §B (1 Ağustos 2026) — konu/thread kimliği (client üretir): PASS-THROUGH, is_followup
    # mantığına HİÇ KARIŞMAZ (yalnız etiketleme/echo) — frontend'in kendi thread modelini
    # kurabilmesi için AskResponse'a aynen geri yansıtılır (bkz. AskResponse.thread_id).
    thread_id: str | None = None
    # §B düzeltmesi (1 Ağustos 2026) — "bu karta yanıt ver": thread_id ile AYNI PASS-THROUGH
    # desen, is_followup/structural/raw mantığına HİÇ KARIŞMAZ. Frontend'in seçtiği ÇAPA
    # kartın kısa insan-okur etiketi — AskResponse'a aynen geri yansıtılır (bkz.
    # AskResponse.reply_to_label) ki ReportCard "↳ yanıt: {etiket}" breadcrumb'ını resume
    # sonrası (kalıcı loga _finish() üstünden düşer) da gösterebilsin.
    reply_to_label: str | None = None
    # §B düzeltmesi (1 Ağustos 2026) — çoklu-seçim birleşik bağlam: birincil bağlam HÂLÂ
    # tek `cube_query`/`prev_sql`'dir (kronolojik en-son seçili kart) — bu alan yalnız
    # DİĞER seçili kartların kısa, tek-satırlık insan-okur özetleridir (frontend üretir,
    # ör. "{soru} → {N} satır"). YALNIZ Discovery (ham-SQL) LLM promptuna grounding metni
    # olarak eklenir (bkz. routers/ask.py::_with_extra_context) — resp.question'ı ASLA
    # değiştirmez, deterministik cube-routing/Intent-JSON yoluna (cube_router.route/
    # deterministic_refine/select_cube/refine_cube) HİÇ karışmaz — bilinçli kapsam sınırı
    # (golden-eval hassasiyeti, tests/test_ask_golden.py).
    extra_context: list[str] | None = None
    # ── YOL SINIRI (Faz F2) — "yalnız küpün KANITLADIĞI cevapları göster" ────────────
    #
    # Araştırma raporu bunu *"güven eşiği ayarı"* diye önermişti: *"yalnız şu yüzdenin
    # üstünde güvenilen cevapları göster."* Sayısal eşik olarak **UYGULANMADI**, çünkü
    # MIMARI'nin açık kararına aykırı: *"kalibre edilmediği sürece o sayı bir güven değil
    # bir SÜStür."* Bizim `1.0/0.85/None` hesaplanmış bir olasılık değil, **yol etiketidir**.
    #
    # Dürüst hâli **merdivenin kendisine** bağlamaktır — üç ayrık seviye, uydurma
    # kalibrasyon yok:
    #
    #   "deterministik" → yalnız `route()` (LLM'e HİÇ gidilmez)
    #   "llm"           → route + Intent-JSON (katalogdan SEÇİM; ham SQL yok)
    #   None / "kesif"  → + Discovery (ham SQL) — **bugünkü varsayılan, DEĞİŞMEZ**
    #
    # Ve bu, rakiplerin **veremeyeceği** bir ayardır: onların yolu yok, tek bir kutu var.
    #
    # ⚠️ Sınırlama yüzünden cevapsız kalınırsa **nedeni yazılır** — sessizce boş dönmek,
    # kullanıcının kendi koyduğu sınırı unutmasına ve ürünü yeteneksiz sanmasına yol açardı.
    yol_siniri: str | None = Field(
        default=None,
        description="deterministik | llm | kesif (varsayılan: sınır yok = kesif)")
    # GRAFİĞE ÇAPA (Faz G2) — kullanıcının işaret ettiği HÜCRE: {"dimension": …, "value": …}.
    # "Nisandaki sıçrama ne?" bir metin numarası değil YAPISAL BİR SEÇİMDİR: koordinat
    # `drill.select_cube_query` ile GERÇEK bir alt-sorguya çevrilir (o boyut kırılımdan
    # çıkar, yerine `eq` filtresi girer) ve konuşma O sorgunun üstünde yürür.
    #
    # Frontend bunu grafik tıklamasından üretir ve ZATEN doğru korumaları uygular
    # (yalnız tek birincil kategorili basit şekiller; ECharts'ın BİÇİMLENDİRİLMİŞ
    # etiketi ham satırlarda tam eşleşmiyorsa SESSİZCE atlanır — yanlış bir filtre
    # göndermektense hiç göndermemek yeğdir).
    anchor: dict[str, Any] | None = None


class CubeRequest(BaseModel):
    """Yorum çubuğu (chip) düzenlemesi: client CubeQuery'yi doğrudan düzenler,
    motor deterministik çalıştırır (LLM yok). label: transkriptte görünen açıklama."""
    cube_query: dict[str, Any]
    label: str | None = None
    limit: int | None = Field(default=None, ge=1)
    session_id: str | None = None
    # §B (1 Ağustos 2026) — bkz. AskRequest.thread_id: chip-düzenlemesi HER ZAMAN aktif
    # thread'e etiketlenir (frontend zaten yalnız aktif thread'in kartlarında chip UI'ı
    # gösterir).
    thread_id: str | None = None
    # /verify geri bildirimi: verdict "right"|"wrong"; undo=True önceki doğrulamayı geri alır.
    verdict: str | None = None
    undo: bool = False
    # ✗ yanlış'ta opsiyonel kullanıcı yorumu (neden yanlış) → log madencisini besler (#57).
    comment: str | None = None


class AskVerifyRequest(BaseModel):
    """Strict-agentic /ask yanıtları için geri bildirim (CubeRequest/`/verify`'nin wren_sql
    karşılığı): kullanıcı bir /ask cevabını onaylar/reddederse VQR'a wren_sql çifti olarak
    yazılır/silinir — bu olmadan VQR asla büyümez ve sistem tekrarlanan sorularda dahi
    LLM'e düşmeye devam eder."""
    question: str = Field(..., min_length=1)
    sql: str | None = None  # onaylanan /ask yanıtının `sql` alanı (verdict=right/undo'da gerekmez)
    session_id: str | None = None
    verdict: str | None = None  # "right" (varsayılan) | "wrong"
    undo: bool = False
    comment: str | None = None


class ReportBlockSpec(BaseModel):
    """Rapor bloğu isteği (ADR-0024): kayıtlı cube_query + göreli dönem + opsiyonel başlık.
    Panodan ("raporu dışa aktar") ya da seçili sonuçlardan derlenir."""
    cube_query: dict[str, Any]
    title: str | None = None
    period: str | None = None
    view_hint: str | None = None  # widget'ın kayıtlı görünümü (rapor onurlandırır)


class ReportRequest(BaseModel):
    """Çok-blok / çok-SAYFA rapor derleme isteği. Her blok deterministik koşar + kendi viz
    kararını alır (app/report.compose_report). Bloklar page_size'lık sayfalara bölünür."""
    title: str | None = None
    blocks: list[ReportBlockSpec] = Field(default_factory=list)
    page_size: int | None = Field(default=None, ge=1)
    session_id: str | None = None


class ColumnMeta(BaseModel):
    name: str
    type: str
    # Düşük kardinaliteli (kategorik) kolonlar için örnek/olası değerler;
    # NL→SQL'in doğru WHERE filtresi yazabilmesi için (ör. müşteri/renk/aşama adları).
    values: list[str] | None = None


class ModelMeta(BaseModel):
    name: str
    columns: list[ColumnMeta]


class RelationshipMeta(BaseModel):
    name: str
    models: list[str]
    join_type: str = ""
    condition: str = ""


class SchemaResponse(BaseModel):
    catalog: str | None = None
    schema_name: str | None = None
    models: list[ModelMeta]
    relationships: list[RelationshipMeta] = []
    # Cube kataloğu (ad/ölçü/boyut + türev boyut değerleri) — yorum chip'lerinin
    # alternatif listeleri buradan beslenir.
    cubes: list[dict[str, Any]] = Field(default_factory=list)
    # Veri kaynağı erişilebilir mi (TCP): UI çevrimiçi/çevrimdışı rozeti. Ulaşılamazsa
    # şema yine döner (yapı) ama değerler zenginleşmez; badge kullanıcıyı uyarır.
    db_online: bool = True


class QueryResult(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int


class Suggestion(BaseModel):
    """Tıklanır hızlı-yanıt chip'i: label gösterilir, tıklanınca query gönderilir.
    Meta yanıtta örnek sorgular; clarification'da dönem seçenekleri (ADR-0007)."""
    label: str
    query: str


class NextStep(BaseModel):
    """K2 (rehberli analitik) — bir rapordan DETERMİNİSTİK 'sonraki adım' chip'i. label
    gösterilir; tıklanınca TAM cube_query `/cube` ile LLM'siz koşar (drill-down/ölçek/zaman).
    kind = dimension (kırılım) | measure (ölçek) | time (granülerlik) — FE gruplama/renk için."""
    label: str
    kind: str
    cube_query: dict[str, Any]


class Recommendation(BaseModel):
    """K4 (karar motoru) — bir SİNYALDEN (K3) türetilen aksiyon önerisi: "neye bakmalısın".
    text = deterministik öneri cümlesi; action opsiyonel = tıklanınca koşan drill (K2 reuse)
    — böylece içgörü→öneri→AKSİYON tek tıkla kapanır."""
    text: str
    action: NextStep | None = None


class Explain(BaseModel):
    """Faz 3 birleşik açıklama: `path` = source'un insan-okur normalize hâli (`_source_kind()`'ın
    yaptığı işin BİR ÜSTÜ — cube/cube+llm ayrımı KORUNUR, ikisinin güveni farklı); `confidence`
    yalnız deterministik/yarı-deterministik yollarda dolu (LLM/rule yollarında ÖLÇÜLEBİLİR bir
    güven skoru YOK — uydurma sayı yerine None); `assumptions` yalnız GERÇEKTEN sessiz bir
    varsayım yapıldıysa dolu (ör. dönem açıkça belirtilmedi → "tüm zamanlar" seçildi/onaylandı)."""

    path: str
    confidence: float | None = None
    assumptions: list[str] = Field(default_factory=list)


class AskResponse(BaseModel):
    question: str
    sql: str = ""
    planned_sql: str | None = None
    result: QueryResult | None = None
    # Provenance: SQL'i kim üretti — cube (deterministik 🥇) | llm:<sağlayıcı> | rule.
    source: str | None = None
    # Rapor cube ile üretildiyse yapısal durum — client bunu tutup takip mesajlarında
    # geri gönderir (konuşmasal daraltma, ADR-0007).
    cube_query: dict[str, Any] | None = None
    # Rapor üretilmediğinde dürüst açıklama (ör. istenen alan modelde yok, anlaşılamadı).
    # Bu durumda sql/result boştur; client mevcut raporu korur, bu notu mesaj olarak gösterir.
    note: str | None = None
    # Sorgunun nasıl çözüldüğü — pipeline adımları (cube route → refine → llm ...).
    # UI'da "?" ile gösterilir; ayrıca kalıcı loga yazılır. Ürün geliştirmeye yardımcı.
    trace: list[str] = Field(default_factory=list)
    # Tıklanır chip'ler — meta örnek sorgular / dönem clarification seçenekleri.
    suggestions: list[Suggestion] = Field(default_factory=list)
    # Görünüm isteği ("grafik ver", "tablo olarak") — veri değil sunum: client mevcut
    # raporun görünümünü değiştirir (chart|table|line|bar|pie|heatmap).
    view_hint: str | None = None
    # §B (Madde 4+6, 1 Ağustos 2026): bu mesaj YENİ bir konu mu (True) yoksa ÖNCEKİ raporun
    # takibi mi (False)? `/ask`'in ZATEN hesapladığı `is_followup`/`structural_followup`
    # sinyalinin TERSİ (YENİ mantık İCAT EDİLMEDİ) — frontend'e taşınır ki ReportCard kart
    # başına bilgilendirici bir breadcrumb gösterebilsin. `/cube` (chip düzenlemesi) HER
    # ZAMAN bir devam olduğundan varsayılan False doğru kalır (o uç bunu hiç set etmez).
    # §B DÜZELTMESİ (1 Ağustos 2026): bu alan İLK sürümde YANLIŞLIKLA frontend'in thread
    # sınırı (yeni panel mi açılsın) kararına da karıştırılmıştı — kullanıcı bunu reddetti
    # ("thread mantığı yanlış... küp ya da bağlamdan bağımsız bir yapı olmalıydı"). Artık
    # SADECE bilgilendirici bir kart-başı etikettir, hiçbir frontend thread-mantığına
    # KARIŞMAZ (thread sınırları artık YALNIZCA kullanıcının hangi komposer'ı kullandığına
    # bağlı — bkz. frontend page.tsx AskMutationVars).
    is_new_topic: bool = False
    # §B (1 Ağustos 2026) — bkz. AskRequest.thread_id: `body.thread_id`'nin AYNEN echo'su
    # (_finish()'te set edilir). is_followup/is_new_topic mantığına HİÇ KARIŞMAZ — frontend
    # bunu görüp KENDİ thread modelini (hangi cevabın hangi thread'e ait olduğunu, sıra-dışı
    # geri-dönüşlerde bile doğru gruplamak için) kurar.
    thread_id: str | None = None
    # §B düzeltmesi (1 Ağustos 2026) — bkz. AskRequest.reply_to_label: body'nin AYNEN
    # echo'su (_finish()'te set edilir). Doluysa ReportCard normal "◆ yeni konu"/"↳ önceki
    # raporun devamı" breadcrumb'ının YERİNE öncelikli olarak bunu gösterir. None ise
    # (genel devam / yeni-thread mesajı) eski breadcrumb değişmeden kalır.
    reply_to_label: str | None = None
    # VİZ ÖNERİSİ (ADR-0024) — grafik/tablo/pivot KARARI backend'de deterministik üretilir
    # (app/viz.py; Show Me + Cleveland-McGill + çok-birim politikası). VizSpec: {kind, measures,
    # dims, time_col, primary_dim, heat, heat_any, facet, facet_measure, scatter, pivot, series_dim,
    # units, unit_count, dual_axis, stackable, partition, alternatives, table_mode}. FE `data.viz`
    # gelince yerel analyze() yerine bunu render eder; view_hint + kullanıcı toggle üstüne biner.
    # Sonuç yoksa None (FE kendi analyze()'ine düşer). İleride: report={blocks:[...]} çok-grafik.
    viz: dict[str, Any] | None = None
    # KONUŞMA CEVABININ İÇERİĞİ (Faz G1/H). "bu neden böyle?" gibi bir takip sorusuna
    # verilen cevabın GÖVDESİ budur — `next_steps` DEĞİL.
    #
    # Neden ayrı bir alan: bulgular `next_steps` üzerinden taşındığında UI onları
    # "SONRAKİ ADIM" başlığıyla gösteriyordu (ölçüldü) — yani CEVABIN KENDİSİ bir
    # "sonraki adım" gibi etiketleniyor, Δ tutarları / % paylar / kırpma uyarısı ise
    # tamamen kayboluyordu. Alan aynı zamanda israfı da önler: backend katkıyı zaten
    # hesapladı; frontend'in aynı ayrıştırmayı ikinci kez istemesi gerekmez.
    #
    # Yeni bir PANEL değil bir ALAN (MIMARI §14.2): cevap kendini tanımlar ve mevcut
    # `ContributionLayer` bileşeni onu render eder — TEK render edici, iki veri kaynağı
    # (buton yolu kendi çeker, konuşma yolu hazır alır). İki render edici zamanla
    # ayrışırdı; bu depoda o desen beş kez ölçüldü.
    contribution: dict[str, Any] | None = None
    # REÇETE (Faz G3) — "ne yapmalıyız?" cevabının YAPILI gövdesi. Düz metne
    # çevrilseydi backend'de hesaplanan üç şey kaybolurdu: segment başına YÖN
    # (`lower_is_better` beyanından: kötüleşti/iyileşti), YOĞUNLAŞMA oranı ve etki/pay
    # sayıları. Chip yalnız etiket taşır; yön bir renk kararıdır ve metinden okunmaz.
    #
    # Yeni bir PANEL değil bir ALAN (MIMARI §14.2): cevabın kendi kartında açılır.
    prescription: dict[str, Any] | None = None
    # DÜZ-DİL HESAPLAMA AÇIKLAMASI (Madde 12, 1 Ağustos 2026): `drill.py::formula_explanation`
    # KPI-olmayan cube raporları İÇİN de (yalnız `/ask/drill`e değil, normal `/ask`e) çağrılır.
    # DİKKAT — `explain` (yukarıda) ile KARIŞTIRILMAMALI: `explain` provenance/güven metadata'sı
    # (kaynak yolu + confidence), bu alan ise ÖLÇÜNÜN NASIL HESAPLANDIĞININ düz-dil anlatımıdır
    # (KPI'ların `kpi.explain`iyle AYNI amaç, sıradan cube raporları İÇİN). cube_query yoksa
    # (LLM/Discovery) None kalır — deterministik formül-açıklama üretilemez, dürüstçe boş bırakılır.
    calculation_explanation: str | None = None
    # Query Contract (ADR-0010): raporun kanıt kaydı — GET /contracts/{id}/replay ile
    # yeniden oynatılıp "veri mi değişti, tanım mı?" teşhisi yapılabilir.
    contract_id: str | None = None
    # Cross-cube KPI kartı (CCC/nakit döngüsü…): tek skaler + bileşenleri (DSO/DIO/DPO).
    # Cube raporu değil bileşke — client bunu KPI kartı olarak render eder.
    kpi: dict[str, Any] | None = None
    # EVRENSEL ÇIKTI YORUMU (feature flag: cikti_yorumlama) — her grafik/tablo/rapor/KPI için
    # DETERMİNİSTİK data-güdümlü yorum {facts:[...], summary:"Türkçe"}. Bayrak kapalıysa None
    # (admin panelden kim görür kararlaştırılır). Ham veri LLM'e gitmez (KVKK).
    # FAZ 4 (K3) — AJAN KOŞUM MAKBUZU. Planlayıcı bir cevabı NASIL ürettiğini söyleyemezse
    # "LLM garson oldu" bir BEYAN olarak kalır. `Kosum.makbuza()` bunu YAPISAL kılar:
    # hangi araçlar · hangi sırayla · kaç ms · hangi adım hata verdi · bütçe kısıldı mı.
    # Yalnız planlayıcıdan geçen cevaplarda dolu; diğerlerinde None (uydurulmaz).
    agent_run: dict[str, Any] | None = None
    interpretation: dict[str, Any] | None = None
    # K2 (rehberli analitik) — rapordan DETERMİNİSTİK sonraki adım chip'leri: kullanılmayan
    # boyut (kırılım) / ölçü (ölçek) / zaman granülerliği. Her biri TAM cube_query taşır →
    # FE /cube ile LLM'siz koşar. Katalogdan türetilir (LLM yok). Rapor yoksa boş.
    next_steps: list[NextStep] = Field(default_factory=list)
    # K4 (karar motoru) — K3 sinyallerinden türetilen aksiyon önerileri: "neye bakmalısın"
    # + opsiyonel tıklanır drill (sürükleyeni bul). Sinyal yoksa boş. Deterministik.
    recommendations: list[Recommendation] = Field(default_factory=list)
    # Faz 3 (31 Temmuz 2026) — birleşik açıklama nesnesi: `trace[]`/`source` Faz 1.5'te az
    # önce kapsamlıca düzeltildiğinden BÜYÜK bir göç riskli olurdu; bunun yerine EKLEYİCİ
    # (trace/source SİLİNMEDİ, ikisi paralel durur — mevcut SourceBadge/trace render'ı
    # kırılmaz) tek bir `explain` alanı. Frontend YENİ alanı kullanmaya başlayabilir,
    # kademeli geçiş.
    explain: Explain | None = None
    # Faz 4.1 (31 Temmuz 2026) — yalnız `ask_async_discovery` bayrağı açıkken dolar: Discovery
    # arka-plan işine kuyruklandığında (result/source HENÜZ yok) client bunu görüp
    # GET /ask/jobs/{job_id} ile poll eder. Bayrak kapalıyken (varsayılan) HER ZAMAN None —
    # mevcut senkron akış BİREBİR korunur.
    job_id: str | None = None
    # FAZ H — ONAYLI YAZMA. Ajan yazma aracını ÇALIŞTIRMAZ; bir ÖNERİ üretir ve
    # kullanıcı onaylar. Alan doluyken `sql`/`result` BOŞTUR: eylem ifadesi bir veri
    # sorusu değildir, merdivene hiç girilmez (0 LLM · 0 SQL).
    #
    # Şekil: {eylem, ozet, izin, geri_alinabilir, argumanlar}. `izin` UI'ın düğmeyi
    # gösterip göstermeyeceğini `/auth/me` permissions listesinden okumasını sağlar —
    # rol matrisi frontend'e KOPYALANMAZ (CLAUDE.md). `argumanlar` onay ucuna aynen
    # gider ama ORADA YENİDEN doğrulanır: öneri güvenilir bir girdi DEĞİLDİR.
    eylem_onerisi: dict[str, Any] | None = None


class EylemOnayRequest(BaseModel):
    """POST /ask/eylem — bir eylem önerisinin ONAYI.

    Öneriyi geri göndermek bir yetki taşımaz: uç, eylemi kayıttan çözer (kayıtta
    olmayan ad → 400), `authorize()`'ı YENİDEN çağırır (öneri anındaki yetkiye
    güvenmek TOCTOU olurdu) ve argümanları VAR OLAN handler'a verir — doğrulama
    ikinci kez YAZILMAZ.
    """

    eylem: str
    argumanlar: dict[str, Any] = Field(default_factory=dict)
    #: `pano.ekle` için hedef pano; boşsa kullanıcının ilk panosu kullanılır
    #: (hiç yoksa oluşturulur — öneri özeti bunu SÖYLER).
    dashboard_id: str | None = None


class EylemOnayResponse(BaseModel):
    ok: bool
    eylem: str
    #: oluşan kaydın kimliği (widget id / schedule id) — UI derin bağlantı kurar
    id: str | None = None
    note: str


class AskJobStatus(BaseModel):
    """Faz 4.1 — GET /ask/jobs/{id} yanıtı. `response` yalnız status='completed' olunca
    dolar (tam AskResponse — client bunu normal /ask cevabı gibi işler). `trace` (Faz 4.12,
    dış yol haritası 2.9 "canlı düşünme adımları") iş HENÜZ tamamlanmadan da BİRİKEREK
    dolar — client bunu poll ederken göstererek "ne yapıyor" hissi verir."""

    id: str
    status: str  # pending | running | completed | failed
    question: str | None = None
    response: AskResponse | None = None
    error: str | None = None
    trace: list[str] = Field(default_factory=list)


class TenantConnectionCreate(BaseModel):
    """Faz 4.5 (31 Temmuz 2026) — tenant-kendi-hizmeti DB bağlama sihirbazı. `admin_app.
    schemas.ConnectionCreate`'ten FARKI: `tenant_id` request'te YOKTUR — tenant HER ZAMAN
    principal'dan türetilir (CLAUDE.md kuralı: "Tenant DAİMA token'dan türetilir, request
    girdisinden asla"). Bu sürümde yalnız Postgres desteklenir (app/db_introspect.py)."""

    datasource: str = "postgres"
    host: str = Field(min_length=1)
    port: int = Field(default=5432, ge=1, le=65535)
    database: str = Field(min_length=1)
    user: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TenantConnectionOut(BaseModel):
    id: str
    datasource: str
    host: str
    port: int
    database: str
    user: str
    has_secret: bool


class ConnectionTestResult(BaseModel):
    ok: bool
    detail: str | None = None


class DraftCube(BaseModel):
    """Bir introspect edilmiş tablonun cube ADAYI — kullanıcı onay ekranında `include`'u
    kapatabilir ya da ölçü/boyut listesini düzenleyebilir (yanlış sınıflandırılan bir
    kolonu taşıyabilir) — `POST /connections/{id}/confirm`'e AYNEN geri gönderilir."""

    name: str
    include: bool = True
    measures: list[str] = Field(default_factory=list)
    dimensions: list[str] = Field(default_factory=list)
    time_dimensions: list[str] = Field(default_factory=list)
    primary_key: str | None = None


class DraftRelationship(BaseModel):
    name: str
    join_type: str = "MANY_TO_ONE"
    models: list[str]
    condition: str


class ConnectionDraft(BaseModel):
    cubes: list[DraftCube]
    relationships: list[DraftRelationship]


class ConnectionConfirmResult(BaseModel):
    written_cubes: list[str]
    written_relationships: int


class DrillRequest(BaseModel):
    """Faz 4.10 (1 Ağustos 2026) — dış yol haritası 2.5+2.15 "dallı kök-neden analizi".
    GENİŞLETİLMİŞ TASARIM (kullanıcı düzeltmesi): bu uç artık GERÇEK sorgu ÇALIŞTIRIR
    (`action` alanına göre) — "tüm veri ağacına ulaşabilmeli" gereksinimi salt yorumlama
    ile karşılanamaz. Her `action` KENDİ Query Contract kaydını üretir (dry_plan+execute
    /cube ile AYNI ilke).

    action:
      - "explain": SORGU ÇALIŞTIRMAZ — yalnız ZATEN elde olan `result`i yorumlar (formül
        açıklaması + dallanma adayları + anomaliler). İLK tıklama burdan başlar.
      - "expand": `dimension` cube_query.dimensions'a EKLENİR, GERÇEK sorgu çalıştırılır.
      - "select": `dimension`'daki `filter_value` kategorisi bir FİLTREYE çevrilir
        (dimensions'tan çıkar), GERÇEK sorgu çalıştırılır — breadcrumb'ın her adımı.
      - "raw": YAPRAK seviyesi — mevcut filtrelerle cube'un base_object'inden HAM satırlar.
      - "related": `target_cube`'a GEÇİLİR (mevcut filtrelerden PAYLAŞILAN olanlar taşınır)
        — kök-neden için İLİŞKİLİ bir cube'un verisine bakma (ör. OEE düşükken duruş
        nedenlerine geçmek, kullanıcı senaryosu 1 Ağustos 2026)."""

    cube_query: dict[str, Any] | None = None
    result: QueryResult | None = None
    kpi: dict[str, Any] | None = None
    session_id: str | None = None
    action: str = "explain"  # explain | expand | select | raw | related
    dimension: str | None = None       # expand: eklenecek boyut; select: filtreye çevrilecek boyut
    filter_value: str | None = None    # select: seçilen kategori değeri
    target_cube: str | None = None     # related: geçilecek cube adı
    limit: int = 50                    # raw: kaç satır getirilsin


class ContributionRequest(BaseModel):
    """Faz 5.1/5.2 — *"neden değişti?"*. Bir `cube_query` alır, kullanılmayan boyutlar
    üzerinde dönemsel değişimin nereden geldiğini arar. `mode` `yoy` (geçen yıl) ya da `mom`.

    `kind`:
      - `segment` (varsayılan) — değişimi SEGMENTLERE dağıtır (Faz 5.2).
      - `pvm` — değişimi FİYAT / MİKTAR / BİRLEŞİK etkiye ayrıştırır (Faz 5.1). Yalnız
        cube'un `pvm:` beyanı varsa çalışır; eşleştirme tahmin EDİLMEZ.
    """

    cube_query: dict[str, Any]
    mode: str = "yoy"
    kind: str = "segment"
    session_id: str | None = None
    max_dimensions: int | None = None


class PvmFinding(BaseModel):
    """Bir segmentin fiyat/miktar ayrışması. `cube_query` onu yalnız başına gösterir."""

    label: str
    kind: str = "dimension"
    deger: Any = None
    delta: float = 0.0
    fiyat_etkisi: float = 0.0
    miktar_etkisi: float = 0.0
    birlesik_etki: float = 0.0
    baskin_etken: str = "miktar"
    fiyat_simdi: float | None = None
    fiyat_onceki: float | None = None
    miktar_simdi: float = 0.0
    miktar_onceki: float = 0.0
    deger_simdi: float = 0.0
    deger_onceki: float = 0.0
    cube_query: dict[str, Any]


class PvmReport(BaseModel):
    """Toplam ayrışma ARTIKSIZDIR: fiyat + miktar + birleşik = net_degisim (birebir)."""

    dimension: str
    dimension_label: str
    value_measure: str
    volume_measure: str
    price_label: str
    net_degisim: float
    fiyat_etkisi: float
    miktar_etkisi: float
    birlesik_etki: float
    bulgular: list[PvmFinding] = Field(default_factory=list)
    kirpilan_segment: int = 0
    kirpilan_esik_yuzde: float = 0.0
    # ŞELALE GRAFİĞİ (Faz I2) — PVM'nin ARTIKSIZ ayrışması şelalenin seçim kuralını tam
    # olarak karşılar (fiyat+miktar+birleşik = net, birebir). Karar BACKEND'de alınır
    # (ADR-0024: grafik kararı LLM'e VERİLMEZ, frontend'e de bırakılmaz) ve toplam
    # tutmuyorsa `None` gelir — o zaman frontend tabloya düşer.
    viz: dict[str, Any] | None = None


class ContributionFinding(BaseModel):
    """Tek bir segmentin katkısı. `cube_query` ONU YALNIZ BAŞINA gösteren sorgudur —
    tıklanınca `/cube` ile LLM'siz koşar ve kendi Query Contract'ını üretir. Rakiplerden
    ayrıştığı nokta budur: skor bir metin değil, doğrulanabilir bir sorgunun etiketi."""

    label: str
    kind: str = "dimension"
    deger: Any = None
    simdi: float = 0.0
    onceki: float = 0.0
    delta: float = 0.0
    net_pay: float | None = None    # net değişime oranı (net ~0 ise None — uydurulmaz)
    brut_pay: float | None = None   # mutlak hareketlerin toplamına oranı
    cube_query: dict[str, Any]


class ContributionReport(BaseModel):
    """Tek bir boyut için ayrıştırma. `kirpilan_segment` sessiz kesme OLMADIĞININ kaydıdır."""

    dimension: str
    dimension_label: str
    net_degisim: float
    brut_hareket: float
    bulgular: list[ContributionFinding] = Field(default_factory=list)
    kirpilan_segment: int = 0
    kirpilan_esik_yuzde: float = 0.0


class ContributionResponse(BaseModel):
    """`note` ayrıştırma YAPILAMADIĞINDA nedenini taşır (toplanamayan ölçü, dönem yok).
    `taranmayan_boyut` üst sınır yüzünden bakılmayan boyut sayısıdır — kapsam sessizce
    daraltılmaz. `taranmayan_adlar` onları ADIYLA taşır: bir SAYI ("3 boyut taranmadı")
    kullanıcıya hangi soruyu sorabileceğini söylemez, ad söyler ("peki renk bazında?")."""

    measure: str | None = None
    mode: str = "yoy"
    kind: str = "segment"
    raporlar: list[ContributionReport] = Field(default_factory=list)
    pvm_raporlar: list[PvmReport] = Field(default_factory=list)
    note: str | None = None
    taranmayan_boyut: int = 0
    taranmayan_adlar: list[str] = Field(default_factory=list)
    contract_ids: list[str] = Field(default_factory=list)


class DrillDimension(BaseModel):
    name: str
    label: str


class DrillAnomaly(BaseModel):
    value: str
    amount: float
    direction: str  # above | below
    z_score: float


class DrillRelatedCube(BaseModel):
    cube: str
    label: str
    shared_dimensions: list[str]


class RawRow(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int


class DrillKpiComponent(BaseModel):
    name: str | None = None
    label: str
    value: float | None = None
    unit: str | None = None


class DrillResponse(BaseModel):
    """`cube_query` (Faz 4.10 GENİŞLETİLMİŞ): bu adımın SONUCUNDA oluşan yapısal durum —
    frontend bunu breadcrumb'a ekler VE bir sonraki /ask/drill çağrısına GERİ gönderir
    (her adım bir öncekinin üstüne inşa edilir). `result` bu adımda GERÇEKTEN çalıştırılan
    sorgunun (varsa) verisidir — "explain" hariç HER action için doludur."""

    cube_query: dict[str, Any] | None = None
    formula_explanation: str
    available_dimensions: list[DrillDimension] = Field(default_factory=list)
    related_cubes: list[DrillRelatedCube] = Field(default_factory=list)
    anomalies: list[DrillAnomaly] = Field(default_factory=list)
    result: QueryResult | None = None
    raw_rows: RawRow | None = None
    kpi_components: list[DrillKpiComponent] | None = None
    contract_id: str | None = None
    note: str | None = None
    # Faz 4.10 doğrulama düzeltmesi (1 Ağustos 2026) — dış yol haritası UC-2.18/2.19 "kanıt
    # paneli": formül açıklamasının YANINDA bu adımı üreten GERÇEK SQL + çalışma süresi de
    # dönmeli ki kullanıcı SQL'i kopyalayıp DB'de çalıştırabilsin (aynı sonucu görsün).
    # `_run()` zaten bu SQL'i Query Contract için üretiyordu — burada ayrıca ATILMADAN taşınır.
    sql: str | None = None
    duration_ms: float | None = None
