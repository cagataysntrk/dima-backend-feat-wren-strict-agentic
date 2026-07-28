#!/usr/bin/env python3
"""dima-backend'in Pydantic modellerinden OpenAPI 3.1 bileşen şeması çıkarır.

NEDEN TÜM APP IMPORT EDİLMİYOR:
`from app.main import app` yolu FastAPI'nin tam OpenAPI belgesini verirdi ama
uygulama sqlmodel/DB katmanını da çekiyor — yani şema üretmek için veritabanı
bağımlılıklarının kurulu olması gerekirdi. `app/schemas.py` yalnız pydantic'e
bağlı; sözleşme yüzeyi zaten orada. Bu yol hem daha az kırılgan hem CI'da
kurulum gerektirmiyor.

Backend çalışıyorsa alternatif her zaman var: GET /openapi.json.

Kullanım:
    python3 extract-schema.py <backend-repo-yolu> > openapi.json
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import sys
from pathlib import Path


def load_schemas_module(backend_root: Path):
    """schemas.py'yi TEK BAŞINA yükler — app paketini import etmeden.

    `app/__init__.py` üzerinden gitmek zincirleme importları tetikler; dosyayı
    doğrudan yüklemek onu izole eder.
    """
    schemas_path = backend_root / "app" / "schemas.py"
    if not schemas_path.is_file():
        raise SystemExit(f"schemas.py bulunamadı: {schemas_path}")

    spec = importlib.util.spec_from_file_location("dima_schemas", schemas_path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"yüklenemedi: {schemas_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["dima_schemas"] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)

    backend_root = Path(sys.argv[1]).expanduser().resolve()
    module = load_schemas_module(backend_root)

    try:
        from pydantic import BaseModel
    except ImportError:  # pragma: no cover
        raise SystemExit("pydantic gerekli: pip install pydantic")

    schemas: dict[str, object] = {}
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if not issubclass(obj, BaseModel) or obj is BaseModel:
            continue
        if obj.__module__ != module.__name__:
            continue  # pydantic'in kendi sınıfları

        # Pydantic v2 JSON Schema draft 2020-12 üretir; OpenAPI 3.1 bununla
        # uyumludur. $defs referanslarını OpenAPI'nin beklediği yere taşıyoruz.
        model_schema = obj.model_json_schema(ref_template="#/components/schemas/{model}")
        defs = model_schema.pop("$defs", {})
        schemas.update(defs)
        schemas[name] = model_schema

    document = {
        "openapi": "3.1.0",
        "info": {
            "title": "dima-backend contracts",
            "version": "0",
            "description": (
                "app/schemas.py'den ÜRETİLMİŞTİR. Elle düzenleme. "
                "Yenilemek için: bun run --filter @dima/contracts codegen"
            ),
        },
        "paths": {},
        "components": {"schemas": dict(sorted(schemas.items()))},
    }

    json.dump(document, sys.stdout, indent=2, ensure_ascii=False, sort_keys=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
