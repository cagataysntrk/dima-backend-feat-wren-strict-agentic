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


class CubeRequest(BaseModel):
    """Yorum çubuğu (chip) düzenlemesi: client CubeQuery'yi doğrudan düzenler,
    motor deterministik çalıştırır (LLM yok). label: transkriptte görünen açıklama."""
    cube_query: dict[str, Any]
    label: str | None = None
    limit: int | None = Field(default=None, ge=1)
    session_id: str | None = None
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
    # VİZ ÖNERİSİ (ADR-0024) — grafik/tablo/pivot KARARI backend'de deterministik üretilir
    # (app/viz.py; Show Me + Cleveland-McGill + çok-birim politikası). VizSpec: {kind, measures,
    # dims, time_col, primary_dim, heat, heat_any, facet, facet_measure, scatter, pivot, series_dim,
    # units, unit_count, dual_axis, stackable, partition, alternatives, table_mode}. FE `data.viz`
    # gelince yerel analyze() yerine bunu render eder; view_hint + kullanıcı toggle üstüne biner.
    # Sonuç yoksa None (FE kendi analyze()'ine düşer). İleride: report={blocks:[...]} çok-grafik.
    viz: dict[str, Any] | None = None
    # Query Contract (ADR-0010): raporun kanıt kaydı — GET /contracts/{id}/replay ile
    # yeniden oynatılıp "veri mi değişti, tanım mı?" teşhisi yapılabilir.
    contract_id: str | None = None
    # Cross-cube KPI kartı (CCC/nakit döngüsü…): tek skaler + bileşenleri (DSO/DIO/DPO).
    # Cube raporu değil bileşke — client bunu KPI kartı olarak render eder.
    kpi: dict[str, Any] | None = None
    # EVRENSEL ÇIKTI YORUMU (feature flag: cikti_yorumlama) — her grafik/tablo/rapor/KPI için
    # DETERMİNİSTİK data-güdümlü yorum {facts:[...], summary:"Türkçe"}. Bayrak kapalıysa None
    # (admin panelden kim görür kararlaştırılır). Ham veri LLM'e gitmez (KVKK).
    interpretation: dict[str, Any] | None = None
    # K2 (rehberli analitik) — rapordan DETERMİNİSTİK sonraki adım chip'leri: kullanılmayan
    # boyut (kırılım) / ölçü (ölçek) / zaman granülerliği. Her biri TAM cube_query taşır →
    # FE /cube ile LLM'siz koşar. Katalogdan türetilir (LLM yok). Rapor yoksa boş.
    next_steps: list[NextStep] = Field(default_factory=list)
    # K4 (karar motoru) — K3 sinyallerinden türetilen aksiyon önerileri: "neye bakmalısın"
    # + opsiyonel tıklanır drill (sürükleyeni bul). Sinyal yoksa boş. Deterministik.
    recommendations: list[Recommendation] = Field(default_factory=list)
