# DIMA METABASE — CANONICAL REPOSITORY CLEANUP INVENTORY

**Date:** 2026-09-26  
**Starting SHA:** f229da9f1c67be94ad23bc2e50740b5353e88403  
**Core A certified candidate:** 81a36a6984e273676119e86fc69534e967713912  
**Engine:** cbe313af9ac2d5960f662068e433d328d896fb06 / 0.63.18-dima.6  
**Status:** **REPOSITORY CANONICALIZATION = SEALED**

## 1. Canonical architecture

~~~text
DIMA CORE
+
METABASE / METABOT
=
CANONICAL PRODUCTION CORE

WREN BAKE-OFF = CANCELLED
WREN SOURCE TREE = NOT CANONICAL
UI IMPLEMENTATION = NOT AUTHORIZED
~~~

Git history remains the archive.

## 2. Machine-counted legacy surfaces

| path | entries | files | blob bytes | classification |
|---|---:|---:|---:|---|
| WrenAI-main/ | 821 | 662 | 14,661,706 | DELETE_AFTER_REFERENCE_FIX |
| belgeler/ | 62 | 52 | 16,103,953 | DELETE_AFTER_REFERENCE_FIX |
| dima-frontend-demo-master/ | 110 | 97 | 1,262,264 | DELETE_AFTER_REFERENCE_FIX |
| backend/admin-dev/ | 2 | 1 | 852 | DELETE_AFTER_REFERENCE_FIX |
| backend/admin_app/ | 27 | 24 | 121,695 | DELETE_AFTER_REFERENCE_FIX |
| backend/backend/lab/ | 2 | 1 | 0 | DELETE_SAFE |
| backend/demo/ | 863 | 432 | 45,832,870 | DELETE_AFTER_REFERENCE_FIX |
| backend/docs/ | 33 | 31 | 65,435 | DELETE_AFTER_REFERENCE_FIX |
| lab/curl/ | 7 | 6 | 9,947 | DELETE_SAFE |
| backend/app/v2/ | 47 | 46 | 671,032 | SPLIT: compatibility types KEEP; runtime DELETE |

Workflow inventory at start:

~~~text
.github/workflows total = 77
legacy v2-* = 28
historical Metabase P3-P13 = 28
sealed P14-P21 family = 11
Core A = 2
~~~

## 3. Canonical Python dependency findings

Sealed P14-P21/Core A does not import the vendored WrenAI-main tree.

Sealed Research retains exact type dependencies on:

~~~text
app.v2.models
app.v2.manager_models
~~~

Therefore:

~~~text
backend/app/v2/__init__.py       = KEEP_CANONICAL compatibility package
backend/app/v2/models.py         = KEEP_CANONICAL sealed contract dependency
backend/app/v2/manager_models.py = KEEP_CANONICAL sealed contract dependency

all other app/v2 interpreter/resolver/manager/execution files
= DELETE_AFTER_REFERENCE_FIX
~~~

No retained type dependency grants authority to the old Ask-v2 runtime.

## 4. Wren dependency findings

Current legacy runtime still references Wren through:

~~~text
backend/app/main.py
backend/app/wren_service.py
backend/app/v3/substrate/wren.py
legacy Ask/query/cube/runtime modules
backend/Dockerfile
backend/pyproject.toml
README / backend README / .env defaults
historical workflows/tests
~~~

Canonical P14 analytical path is:

~~~text
Metabot / Metabase
→ app.v3.substrate.metabase.native_engine
→ P14 Research
→ Evidence / Claim / P19 / Report / Decision
~~~

The canonical P14 path does not require WrenAI-main, wrenai, or wren-core-py.

## 5. backend/demo findings

No sealed v3/Core A owner imports backend/demo resources.

Current dependencies on backend/demo are legacy shell concerns:

~~~text
old Wren startup
old company/project/data config defaults
Docker bundled demo COPY
README/demo instructions
legacy tests/workflows
~~~

Therefore backend/demo is DELETE_AFTER_REFERENCE_FIX. If a retained consumer is discovered during
focused validation, migrate only that exact resource to backend/resources/ or backend/fixtures/.

## 6. Frontend/admin findings

~~~text
dima-frontend-demo-master = old UI; DELETE_AFTER_REFERENCE_FIX
backend/admin-dev         = old admin dev shell; DELETE_AFTER_REFERENCE_FIX
backend/admin_app         = old separate admin HTTP service; DELETE_AFTER_REFERENCE_FIX
~~~

Control-plane/auth/security packages remain canonical. Deleting old UI does not authorize new UI.

## 7. Documentation findings

~~~text
backend/belgeler/metabase/ = KEEP_CANONICAL active authority tree
belgeler/                  = legacy Ask-v2/history; DELETE_AFTER_REFERENCE_FIX
backend/docs/              = legacy ADR/history tree; DELETE_AFTER_REFERENCE_FIX
~~~

Unique still-binding architecture content must be represented in the canonical Metabase authority
tree before removal. Git history is the archive.

## 8. Lab findings

Keep only certification/eval assets required for P14/P17/P19 and Core B/final certification.
Delete historical Ask-v2/Wren/UI/curl experiments. Root lab/curl is DELETE_SAFE after stale links
are removed.

## 9. Workflow findings

~~~text
CANONICAL ACTIVE
- governance
- Core A final closure
- cleanup closure
- later Core B/final certification

SEALED REGRESSION
- P14-P21 workflows still useful until final consolidation
- bounded P14/P17/P19 live canaries where still needed

PRODUCTIZATION_DEBT
- Resend provider-free seam only

RETIRE
- M1 Wren parity
- M2 historical lab gate after hygiene replacement
- P3-P13 historical milestone workflows
- v2/day* Ask-v2 workflows
- Resend live-canary workflow
~~~

## 10. Manifest/runtime reference fixes required before deletion

~~~text
README.md
backend/README.md
backend/pyproject.toml
backend/.env.example
backend/Dockerfile
docker-compose.yml
backend/package.json
backend/app/main.py
backend/app/config.py
workflow path filters / grep guards
current roadmap/living docs
~~~

## 11. Initially unresolved items

~~~text
qdrant in root docker-compose
legacy app modules outside app/v2
remaining test-only demo resources
remaining backend/lab assets
~~~

These require explicit audit; naming alone is not deletion authority.

## 12. Cleanup invariants

~~~text
Core A stays SEALED
P14-P21 stay SEALED
Human Adoption stays SEALED
ActionAuthorization stays SEALED
engine gitlink stays cbe313af9ac2d5960f662068e433d328d896fb06
DEFAULT_ACTION_CAPABILITY_REGISTRY stays EMPTY
external side effects = 0
UI implementation = 0
~~~

## 13. Proof strategy

~~~text
inventory
→ reference fixes / canonical runtime shell
→ coherent deletions
→ resource/test/workflow pruning
→ import + FastAPI + Alembic smoke
→ one final Core A + P14-P21 canonical regression
→ governance + hygiene
→ cleanup seal
→ Core B
~~~


---

## 14. Final canonicalization closure

~~~text
starting cleanup authority SHA         = af544a64f80e6e92553f28a9181d06530d0ddc85
final cleanup behavior SHA             = 2a8534990757d6b84634aac1e70fdf78f99798f0
cleanup-focused                        = 36237748801 SUCCESS
governance                             = 36237748789 SUCCESS
Core A final regression                = 36237748799 SUCCESS
Alembic head                           = fb4e6d2a1074
engine gitlink                         = cbe313af9ac2d5960f662068e433d328d896fb06
external side effects                  = 0
UI implementation                     = 0
~~~

Final removal added 48 files to the earlier cleanup:
25 legacy `backend/belgeler/plan/**` files, 19 historical ticket files and four unreferenced
root/backend helper documents/scripts.

Final canonical root contains only the current status pointer, canonical README, backend, engine,
compose metadata and repository metadata. Active architecture authority lives under
`backend/belgeler/metabase/`.

The inventory is closed. Forward authority is Core Closure B.
