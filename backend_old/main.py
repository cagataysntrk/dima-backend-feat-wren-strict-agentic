from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import hashlib
import json
from openai import OpenAI
import os
from mdl_manager import DIMASemanticManager
from typing import Optional

app = FastAPI(title="DİMA Enterprise AI OS Engine", version="2.0")

# CORS Konfigürasyonu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WREN_ENGINE_URL = os.getenv("WREN_ENGINE_URL", "http://localhost:8080")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", os.getenv("DIMA_OPENROUTER_API_KEY", ""))
BASE_URL = "https://openrouter.ai/api/v1" if os.getenv("DIMA_OPENROUTER_API_KEY") else None
LLM_MODEL = os.getenv("DIMA_OPENROUTER_MODEL", "gpt-4o")

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=BASE_URL
)

semantic_manager = DIMASemanticManager(WREN_ENGINE_URL)
boyahane_schema = semantic_manager.generate_boyahane_mdl()

class QueryRequest(BaseModel):
    user_id: str
    question: str
    mdl_schema: Optional[dict] = None

class DIMAQueryContract:
    @staticmethod
    def generate_badge(sql: str, raw_data: list, mdl_version: str) -> str:
        """SHA-256 Kriptografik Kanıt Mührü (GOLD_TRUST_BADGE)"""
        payload = f"{sql}_{json.dumps(raw_data, sort_keys=True)}_{mdl_version}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def call_llm_for_wren_sql(system_prompt: str, user_question: str) -> str:
    """LLM Çağrı Katmanı - Saf Wren SQL üretir"""
    completion = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        temperature=0.0
    )
    raw_sql = completion.choices[0].message.content
    return raw_sql.replace("```sql", "").replace("```", "").strip()

@app.post("/api/v1/cortex/query")
async def execute_cortex_query(req: QueryRequest):
    """
    DİMA Bilişsel Sorgu Hattı:
    - MDL Semantik Kontrolü
    - Text-to-Wren-SQL Dönüşümü
    - Dry-Run Doğrulama & Otomatik Düzeltme (Self-Healing)
    - Veritabanı İcraatı
    - QueryContract SHA-256 Mühürleme
    - Grafik ve Takip Sorusu Üretimi
    """
    schema_to_use = req.mdl_schema if req.mdl_schema else boyahane_schema

    system_prompt = f"""
    Sen DİMA Semantik SQL Ajanısın.
    Aşağıdaki MDL Şemasını incele ve kullanıcının Türkçe sorusuna karşılık gelen geçerli bir Wren SQL yaz.

    KURALLAR:
    - SADECE MDL içindeki tanımlı model, metrik ve kolon isimlerini kullan.
    - Veritabanında olmayan tablo veya kolon uydurma.
    - Yanıt olarak SADECE saf Wren SQL kodu döndür, açıklama veya yorum ekleme.

    MDL ŞEMASI:
    {json.dumps(schema_to_use)}
    """

    try:
        # 1. ADIM: LLM'den Wren SQL İste
        wren_sql = call_llm_for_wren_sql(system_prompt, req.question)

        # 2. ADIM: Dry-Run Doğrulama (Wren Engine)
        validate_res = requests.post(f"{WREN_ENGINE_URL}/v1/query/validate", json={
            "mdl": schema_to_use,
            "query": wren_sql
        }, timeout=5)

        # SELF-HEALING LOOP: SQL Hatalıysa 1 Kez Otomatik Düzeltme Dene
        if validate_res.status_code != 200:
            error_msg = validate_res.json().get("error", "Sözdizimi hatası")
            correction_prompt = f"""
            Ürettiğin Wren SQL hatalı çıktı!
            HATA MESAJI: {error_msg}
            HATALI SQL: {wren_sql}

            Lütfen MDL şemasına tam uyacak şekilde düzeltilmiş saf Wren SQL kodunu tekrar yaz:
            """
            wren_sql = call_llm_for_wren_sql(system_prompt, correction_prompt)

        # 3. ADIM: Fiziksel Veritabanında İcraat
        exec_res = requests.post(f"{WREN_ENGINE_URL}/v1/query/execute", json={
            "mdl": schema_to_use,
            "query": wren_sql
        }, timeout=10)

        if exec_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Sorgu icraat hatası. Şema ile veri uyumsuz.")

        data = exec_res.json().get("data", [])

        # 4. ADIM: QueryContract (SHA-256) Mührü Oluştur
        proof_hash = DIMAQueryContract.generate_badge(wren_sql, data, "v1.0-boyahane")

        # 5. ADIM: Otomatik Görselleştirme ve Takip Sorusu Mantığı
        chart_type = "METRIC_CARD"
        if len(data) > 1:
            chart_type = "BAR" if any("tarih" in k.lower() or "makine" in k.lower() for k in data[0].keys()) else "TABLE"

        follow_ups = [
            "Bu kayıpların hangi makinelerde yoğunlaştığını detaylandır.",
            "Son 30 günlük trend grafiğini çıkar.",
            "Su sertliği 12'nin üstünde olan partileri filtrele."
        ]

        # 6. ADIM: Standart DİMA Yanıt Paketi
        return {
            "badge": "GOLD_TRUST_BADGE",
            "question": req.question,
            "summary": f"İşlem tamamlandı. {len(data)} adet kayıt başarıyla hesaplandı.",
            "data": data,
            "visualization": {
                "recommended_chart": chart_type,
                "data_length": len(data)
            },
            "proof": {
                "executed_wren_sql": wren_sql,
                "query_contract_hash": proof_hash,
                "engine_status": "DETERMINISTIC_SUCCESS"
            },
            "suggested_follow_up_questions": follow_ups
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
