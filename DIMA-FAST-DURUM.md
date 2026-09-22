# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

CURRENT_GATE: F0 — Governance / isolated bootstrap
CURRENT_HEAD: governance bootstrap commit oluşturuluyor
PARENT_SNAPSHOT: 352205f112fe735d8f80065c7d255d78905398b9
LAST_GREEN: parent snapshot baseline
OPEN_RED: none
OPEN_DEBT: F0A pinned Metabase capability preflight henüz Fast Track branch'inde tekrar mühürlenmedi

## COMPLETED

- Yeni Fast Track branch exact SHA'dan oluşturuldu.
- Source branches read-only ilan edildi.
- Moving HEAD inheritance yasaklandı.
- Branch-local governance dosyaları oluşturuluyor.
- Fast Track runtime namespace yalnız skeleton olarak hazırlanıyor.
- Functional analytics henüz başlatılmadı.

## CURRENT_INVARIANTS

- Writes yalnız Fast Track branch.
- Wren/V2/V3 semantic hot-path dependency = 0.
- Silent fallback = 0.
- Native SQL default = OFF.
- Functional analytics F0A'dan önce yok.
- External pilot F9 security gate'ten önce yok.

## NEXT_EXACT_ACTION

1. Governance bootstrap commit'ini mühürle.
2. Branch head ve dosyaları doğrula.
3. FT-002/F0A pre-development review aç.
4. Pinned Metabase v0.63.18 capability probe'u Fast Track receipt'i olarak tekrar çalıştır.
5. F0A green olmadan Ask/Analyst/Root-Cause kodu yazma.

## FILES_NEXT_ALLOWED

- backend/belgeler/fast/**
- backend/app/fast/**
- Fast Track test files
- minimal config/lab files only after predev review

## FILES_NEXT_FORBIDDEN

- app.wren_*
- backend/app/v2/**
- backend/app/v3 semantic/compiler owners
- source branches
- legacy ask behavior
