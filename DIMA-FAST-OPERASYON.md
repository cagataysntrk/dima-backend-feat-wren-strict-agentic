# DIMA FAST TRACK — OPERASYON

Status: NORMATIVE
Branch: `feat/dima-metabase-product-fast-track`

## 1. Mutlak branch izolasyonu

Bu geliştirme yalnız bu branch'te yapılır.

READ/WRITE:
- feat/dima-metabase-product-fast-track

READ-ONLY REFERENCES:
- feat/dima-metabase-platform@352205f112fe735d8f80065c7d255d78905398b9
- feat/ask-v2-mvp@6d65600842731112f2362261a30660217cbde05d

YASAK:
- source branch'e commit
- source branch'e update_ref / force push
- source branch'e merge / rebase / cherry-pick
- moving source HEAD'i Fast Track'e otomatik almak
- source branch'ten receipt olmadan kod kopyalamak

Kaynak branch'te yararlı bir fikir görülürse yalnız:
1. read-only incele,
2. Fast Track abstraction'ında yeniden türet,
3. gerekirse PORT RECEIPT yaz,
4. Fast Track'te yeniden test et.

## 2. Normatif okuma sırası

Yeni geliştirici önce:
1. backend/belgeler/fast/DIMA_FAST_TRACK_ROADMAP.md
2. backend/belgeler/fast/DIMA_FAST_SOURCE_LOCK.md
3. DIMA-FAST-DURUM.md
4. DIMA-FAST-OPERASYON.md
5. DIMA-FAST-DENETIM.md
6. aktif PRE-DEVELOPMENT REVIEW
7. açık failure / decision receipts
8. ancak gerekirse read-only source branch

okur.

## 3. Ticket protokolü

Her ticket implementation'dan önce:
`backend/belgeler/fast/predev/<TICKET>_PREDEVELOPMENT_REVIEW.md`

Minimum alanlar:
- CURRENT_HEAD
- USER_SCENARIO
- CURRENT_OWNER
- TARGET_OWNER
- FILES_TO_TOUCH
- FILES_NOT_TO_TOUCH
- INVARIANTS
- BASELINE
- FAILURE_MODES
- FOCUSED_TESTS
- LIVE_SENTINEL
- EXIT_GATE
- ROLLBACK

Predev review commit edilmeden product implementation commit'i açılmaz.

## 4. Failure protokolü

RED sonrası phrase-specific patch yok.

Önce receipt:
- FAILURE_ID
- OBSERVED_SHA
- TEST/RUN
- FAILURE_CLASS
- SINGLE_OWNER
- ROOT_CAUSE_EVIDENCE
- FORBIDDEN_PATCHES
- ALLOWED_FILES
- FOCUSED_PROOF
- FAMILY_PROOF

Failure classes:
- MODEL_COGNITION
- RESOURCE_RESOLUTION
- TEMPORAL_BINDING
- QUERY_CONSTRUCTION
- QUERY_EXECUTION
- AUTH_PERMISSION
- CONVERSATION_STATE
- EVIDENCE_PROVENANCE
- ROOT_CAUSE_LOGIC
- ASSET_PERSISTENCE
- TRANSPORT_RUNTIME
- EVAL_ORACLE

## 5. Commit disiplini

Tercih:
- one ticket
- one owner
- one coherent change

Aynı commit'te prompt + backend + UI + unrelated refactor + dependency upgrade yapılmaz.

## 6. Runtime sınırları

Fast hot path:
`backend/app/fast/**`

Runtime import YASAK:
- app.wren_*
- app.v2.semantic_*
- app.v2.manager_*
- app.v3.semantic_spec
- app.v3.substrate.metabase.compiler

Metabase transport pattern'i read-only reference'tan öğrenilebilir; Fast Track owner'ı yine `app.fast` olmalıdır.

## 7. Silent fallback yasağı

Metabase failure:
- Wren'e düşmez.
- V2'ye düşmez.
- V3 semantic owner'a düşmez.

Typed failure döner.

## 8. Native SQL

Default:
`DIMA_FAST_ALLOW_NATIVE_SQL=0`

Native SQL bir gizli repair/fallback yolu olamaz.

## 9. Oturum sonu handoff

DIMA-FAST-DURUM.md mutlaka güncellenir:
- CURRENT_HEAD
- CURRENT_GATE
- LAST_GREEN
- OPEN_RED
- OPEN_DEBT
- NEXT_EXACT_ACTION
- FILES_NEXT_ALLOWED
- FILES_NEXT_FORBIDDEN
