import json
import requests
from typing import Dict, Any

class DIMASemanticManager:
    """
    WrenAI MDL (Model Definition Language) Yönetim Katmanı.
    Veritabanı tablolarını, ilişkileri ve Altın Yol Metriklerini saklar.
    """
    def __init__(self, wren_engine_url: str):
        self.wren_engine_url = wren_engine_url

    def generate_boyahane_mdl(self) -> Dict[str, Any]:
        """
        DİMA + Boyahane Paketi v1.0 Semantik Şeması.
        Deterministik RFT ve Rework hesaplama kurallarını içerir.
        """
        return {
            "catalog": "dima_production_db",
            "schema": "public",
            "models": [
                {
                    "name": "PartiKayitlari",
                    "tableReference": {"table": "boyahane_parti_logs"},
                    "columns": [
                        {"name": "parti_id", "type": "INTEGER", "isCalculated": False},
                        {"name": "recete_kodu", "type": "VARCHAR", "isCalculated": False},
                        {"name": "makine_id", "type": "INTEGER", "isCalculated": False},
                        {"name": "is_rework", "type": "BOOLEAN", "isCalculated": False},
                        {"name": "maliyet_tl", "type": "DOUBLE", "isCalculated": False},
                        {"name": "su_sertligi", "type": "DOUBLE", "isCalculated": False},
                        {"name": "islem_tarihi", "type": "DATE", "isCalculated": False}
                    ],
                    "primaryKey": "parti_id"
                },
                {
                    "name": "MakineKapasite",
                    "tableReference": {"table": "makine_tanimlari"},
                    "columns": [
                        {"name": "makine_id", "type": "INTEGER", "isCalculated": False},
                        {"name": "makine_adi", "type": "VARCHAR", "isCalculated": False},
                        {"name": "saatlik_maliyet_eur", "type": "DOUBLE", "isCalculated": False}
                    ],
                    "primaryKey": "makine_id"
                }
            ],
            "relationships": [
                {
                    "name": "PartiMakineIliskisi",
                    "models": ["PartiKayitlari", "MakineKapasite"],
                    "joinType": "MANY_TO_ONE",
                    "condition": "PartiKayitlari.makine_id = MakineKapasite.makine_id"
                }
            ],
            "metrics": [
                {
                    "name": "ToplamReworkKaybi",
                    "baseModel": "PartiKayitlari",
                    "dimension": ["islem_tarihi", "makine_id"],
                    "measures": [
                        {
                            "name": "toplam_kayip_tl",
                            "expression": "SUM(CASE WHEN is_rework = TRUE THEN maliyet_tl ELSE 0 END)"
                        },
                        {
                            "name": "toplam_parti_sayisi",
                            "expression": "COUNT(parti_id)"
                        },
                        {
                            "name": "rework_parti_sayisi",
                            "expression": "SUM(CASE WHEN is_rework = TRUE THEN 1 ELSE 0 END)"
                        }
                    ]
                }
            ]
        }

    def deploy_mdl_to_engine(self, mdl_schema: Dict[str, Any]) -> bool:
        """MDL şemasını Wren Engine üzerine yükler ve doğrular."""
        endpoint = f"{self.wren_engine_url}/v1/mdl/deploy"
        try:
            res = requests.post(endpoint, json=mdl_schema, timeout=10)
            return res.status_code == 200
        except Exception as e:
            print(f"[MDL Deploy Error]: {e}")
            return False

if __name__ == "__main__":
    manager = DIMASemanticManager("http://localhost:8080")
    schema = manager.generate_boyahane_mdl()
    print("Deploying MDL schema...")
    success = manager.deploy_mdl_to_engine(schema)
    print(f"Deploy status: {'Success' if success else 'Failed'}")
