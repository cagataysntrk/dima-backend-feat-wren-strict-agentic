# DIMA DAY 6.5 — M0E CAPABILITY EXHAUSTION RECEIPT

**Status:** M0E-v1 VALID BASELINE / FINAL EXHAUSTION SUPERSEDED BY M0E-DEEP-DELTA  
**Date:** 2026-09-22  
**Canonical upstream:** `metabase/metabase`  
**Pinned source SHA:** `74216b30981d8310c4cf724d63ca282e2e63529d`  
**Current upstream master checked:** `fff70175e0b5f82dc0eb267593c717c4a6130206`  
**Relevant source drift:** NONE — one locale-only commit  
**Source copy/port/vendor:** NONE  
**Production Metabase dependency:** OFF

This receipt preserves the **M0E-v1 capability classification baseline**. It no longer claims FINAL exhaustion.
A deeper upstream source audit identified additional Dima-relevant mechanisms; final exhaustion is reopened in
`DIMA_DAY6_5_M0E_DEEP_DELTA_CONTRACT.md`. Existing v1 rows remain valid evidence and are not deleted.

## M0E-01 — Generic agent loop / terminal mechanics

- mechanism: bounded agent loop, terminal/no-progress/retry process mechanics
- exact upstream source evidence: `src/metabase/metabot/agent/core.clj::loop-step`;
  `src/metabase/metabot/agent/profiles.clj`
- problem solved: generic bounded agent execution lifecycle
- maturity / why it exists: shared Metabot orchestration with profile-owned tools/terminals
- Dima equivalent: `BoundedAgentRuntimeKernel`
- Wren equivalent: none
- current gap: no material pre-X0 gap
- disposition: **PATTERN_ONLY**
- WHY: Dima already owns stricter authority/progress semantics; runtime dependency adds no core value
- native implementation cost: LOW, already implemented
- Metabase runtime dependency if reused: none
- authority/security impact: kernel must remain authority-blind
- semantic duplication risk: none
- operational dependency: none
- license/API implication: source studied only; no copy
- required behavioral proof: existing Day6.5 agent-runtime/provider-free family tests
- timing: PRE-X0 / already adopted

## M0E-02 — Agent profiles / capability-scoped tool surfaces

- mechanism: profile-specific tool/capability registry
- source: `src/metabase/metabot/agent/profiles.clj`; `src/metabase/mcp/v2` tool registry
- problem: prevent one generic agent from receiving every capability
- maturity: shared profile/tool boundary used by Metabot/MCP
- Dima equivalent: Standard vs Research profiles + governed tool contracts
- Wren equivalent: none
- gap: no material core gap
- disposition: **PATTERN_ONLY**
- WHY: profile separation is already Dima-native
- native cost: LOW / implemented
- runtime dependency: none
- authority/security: preserve least-capability profile
- semantic duplication: none
- operational: none
- license/API: pattern study only
- proof: capability-algebra + preacceptance/provider-free tests
- timing: PRE-X0 / already adopted

## M0E-03 — Agent API construct-query boundary

- mechanism: external structured query → validated/resolved live query
- source: `src/metabase/agent_api/api.clj::evaluate-external-query-to-live-query`;
  Agent API `POST /v2/construct-query`
- problem: turn a portable structured query into an executable query artifact
- maturity: supported/versioned Agent API path
- Dima equivalent: `StandardProjection → planner/Wren`
- Wren equivalent: Wren compiler/dry-plan
- gap: potential generic query-lifecycle reuse
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: mature generic infrastructure; high cost to reproduce without differentiated Dima semantics
- native cost: HIGH
- runtime dependency: Metabase service + app DB
- authority/security: input must already be accepted Dima semantics
- semantic duplication: HIGH if adapter redefines metrics/relationships; target 0 manual duplication
- operational: service/network/JVM/app DB
- license/API: supported API preferred; no source port
- proof: X0 construct success + provenance + semantic-duplication receipt
- timing: X0

## M0E-04 — Agent API / MCP structured execution

- mechanism: resolved structured query execution
- source: `src/metabase/mcp/v2/queries.clj::execute-representations-query`;
  Agent API query endpoint; `src/metabase/query_processor/execute.clj`
- problem: execute governed queries through mature processing/driver stack
- maturity: central query execution path
- Dima equivalent: official execution boundary → Wren query
- Wren equivalent: Wren dry-plan/query
- gap: candidate execution/query-lifecycle alternative
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: core X0 residual-value question
- native cost: HIGH
- runtime dependency: Metabase
- authority/security: Dima authority/evidence remains external and mandatory
- semantic duplication: must be 0/manual-minimal
- operational: service + DB drivers
- license/API: API integration only
- proof: same StandardProjection meaning, same principal, same DB, actual result/receipt
- timing: X0

## M0E-05 — Portable representation boundary / closed stage keys

- mechanism: canonical portable MBQL representation and unknown-key rejection
- source: `src/metabase/agent_lib/representations.clj::assert-known-stage-keys!`,
  `validate-query`
- problem: reject typo/shape laundering before query processing
- maturity: dedicated agent-facing portable-query boundary
- Dima equivalent: typed `StandardProjection` + schema validation
- Wren equivalent: CubeQuery/MDL compiler shape
- gap: runtime can add mature structured-query validation
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: useful through runtime; do not transliterate schema/repair code
- native cost: MEDIUM-HIGH
- runtime dependency: Metabase Agent API
- authority/security: unknown/native payload must fail closed
- semantic duplication: low if generated from sealed projection
- operational: adapter schema translation
- license/API: supported API only
- proof: malformed/unknown-stage attack fails closed
- timing: X0

## M0E-06 — LLM-authored query repair pipeline

- mechanism: idempotent structural query repair
- source: `src/metabase/agent_lib/representations/repair.clj::repair` family
- problem: repair common structured-query shape errors before resolution/execution
- maturity: dedicated multi-pass repair with idempotency invariant/property tests
- Dima equivalent: bounded StandardBuilder repairs; no equivalent full BI query repair engine
- Wren equivalent: compiler/dry-plan validation, not same repair breadth
- gap: material generic implementation burden if rebuilt
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: canonical build-vs-buy example; use mature runtime if it proves safe/value-generating
- native cost: HIGH
- runtime dependency: Metabase
- authority/security: repair may fix shape only; cannot create Dima semantic authority
- semantic duplication: medium if repair infers joins from Metabase metadata; X0 must measure
- operational: service dependency
- license/API: consume behavior via Agent API, no code copy
- proof: repair success, idempotent outcome behavior, no semantic drift, no native SQL
- timing: X0 / FULL-X

## M0E-07 — FK/entity resolution and export

- mechanism: portable FK → numeric-ID resolve, normalized MBQL, permission-aware export
- source: `src/metabase/agent_lib/representations/resolve.clj::resolve-query`,
  `export-query`, `try-export-query`
- problem: bind portable query references to current Metabase metadata
- maturity: central representations resolver
- Dima equivalent: semantic handles + planner/Wren resolution
- Wren equivalent: MDL semantic compilation
- gap: execution-runtime translation only
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: may be necessary inside Metabase arm, but is not Dima semantic truth
- native cost: HIGH
- runtime dependency: Metabase metadata/app DB
- authority/security: agent-facing caller must use permission-aware store
- semantic duplication: HIGH if used to redefine business semantics; X0 veto
- operational: metadata sync dependency
- license/API: service boundary
- proof: unreadable entity cannot be exported/resolved; same accepted meaning preserved
- timing: X0

## M0E-08 — Query preprocess pipeline

- mechanism: validate/prefetch/resolve cards/metrics/fields/joins/parameters/temporal/persistence
- source: `src/metabase/query_processor/preprocess.clj::preprocess`
- problem: normalize and validate rich BI query before compilation
- maturity: long-lived central middleware pipeline
- Dima equivalent: planner + validator + dry-plan sequence
- Wren equivalent: semantic compiler/dry-plan
- gap: generic BI query lifecycle breadth
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: expensive generic infrastructure; test rather than rebuild
- native cost: HIGH
- runtime dependency: Metabase
- authority/security: permission and sandbox middleware must remain active
- semantic duplication: medium/high if Metabase owns semantic joins
- operational: JVM/runtime metadata
- license/API: indirect through supported API
- proof: malformed/missing refs fail; permissioned preprocessing; same projection semantics
- timing: X0 / FULL-X

## M0E-09 — Query execution middleware / driver boundary

- mechanism: compiled query execution with permission middleware
- source: `src/metabase/query_processor/execute.clj::execute`
- problem: central execution stack over heterogeneous drivers
- maturity: core Metabase execution path
- Dima equivalent: WrenService query
- Wren equivalent: current incumbent execution
- gap: potential driver/processing leverage
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: core execution challenger
- native cost: HIGH
- runtime dependency: Metabase + driver
- authority/security: `check-query-permissions` must not be bypassed
- semantic duplication: low if query is faithful translation
- operational: runtime/connection pools
- license/API: service API
- proof: same principal permissions; denied query stays denied
- timing: X0

## M0E-10 — Shared Lib query validation / bad-reference detection

- mechanism: typed query manipulation and missing/bad ref validation
- source: `src/metabase/lib/validate.cljc::find-bad-refs`,
  `find-bad-refs-with-source`; `src/metabase/lib/query.cljc`
- problem: catch stale/missing field/table/card refs
- maturity: shared backend/frontend query library
- Dima equivalent: planner/result validation + context-version gates
- Wren equivalent: semantic compile/dry-plan
- gap: runtime-specific validation breadth
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: valuable inside Metabase arm; direct port would duplicate mature library
- native cost: HIGH
- runtime dependency: Metabase
- authority/security: validation is not semantic authority
- semantic duplication: medium
- operational: none beyond runtime
- license/API: do not embed AGPL library in Dima
- proof: stale/missing reference typed failure
- timing: X0

## M0E-11 — Backend metadata provider/cache

- mechanism: application DB models → normalized metadata provider/cache
- source: `src/metabase/lib_be/metadata/jvm.clj::instance->metadata`;
  `src/metabase/lib_be/query.clj::bulk-load-query-metadata!`
- problem: efficient metadata normalization/cache for query processing
- maturity: shared Lib backend infrastructure
- Dima equivalent: ContextProvider/Wren schema snapshots
- Wren equivalent: MDL/catalog
- gap: only relevant to Metabase runtime internals
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: let service own its internals; do not reproduce
- native cost: HIGH
- runtime dependency: Metabase app DB
- authority/security: metadata visibility must obey permissions on external surfaces
- semantic duplication: medium if treated as business semantic source
- operational: app DB/cache
- license/API: indirect service use
- proof: X0 metadata translation does not become Dima authority
- timing: X0

## M0E-12 — Metabase metric definition / dimension semantic layer

- mechanism: metric definitions, stable dimension IDs/mappings, curated metric dimensions
- source: `src/metabase/lib_metric/core.cljc`;
  `src/metabase/metrics/core.clj::compute-dimensions`, `sync-dimensions!`
- problem: reusable metric semantics and dimension exploration
- maturity: dedicated metric semantic subsystem
- Dima equivalent: Dima handles/trust consuming Wren semantics
- Wren equivalent: **MDL/models/relationships/cubes/knowledge**
- gap: no gap that justifies a second semantic truth
- disposition: **WREN_OWNS**
- WHY: duplicating metric/dimension semantics is exactly the semantic-drift risk X0 must avoid
- native cost: N/A
- runtime dependency if reused: would require dual semantics
- authority/security: Metabase metric IDs cannot mint Dima semantic handles
- semantic duplication: VERY HIGH
- operational: sync/curation burden
- license/API: optional resource later only
- proof: X0 manual dual semantic definitions = 0
- timing: PRE-X0 ownership decision; workspace use POST-MVP

## M0E-13 — Query permission calculation / replay authorization

- mechanism: compute required permissions from resolved query sources; check execution permission
- source: `src/metabase/query_permissions/impl.clj::query->resolved-source-ids`,
  `required-perms-for-query`, `check-data-perms`
- problem: permission verdict over nested cards/tables/native paths
- maturity: central query permission subsystem
- Dima equivalent: explicit Principal + tenant execution gates
- Wren equivalent: principal-aware RLS/CLS/execution
- gap: Metabase arm needs equivalent runtime permission proof
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: mature permission engine is part of runtime value, but Dima remains outer trust owner
- native cost: HIGH
- runtime dependency: Metabase
- authority/security: P0; current-user permission must be revalidated at execute/replay
- semantic duplication: none
- operational: user/group configuration mapping
- license/API: supported runtime
- proof: permission revoke → replay/handle execution denied; cross-user handle denied
- timing: X0

## M0E-14 — Object read/write/query permissions

- mechanism: model-level `can-read?`, `can-write?`, `can-query?`, user permission sets
- source: `src/metabase/models/interface.clj`; `src/metabase/permissions/user.clj`
- problem: distinguish metadata visibility, object write, and query execution
- maturity: cross-product permission framework
- Dima equivalent: Dima authorization + principal/tenant scope
- Wren equivalent: execution security
- gap: identity equivalence across runtimes
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: X0 must prove same principal sees/runs the same resources
- native cost: HIGH
- runtime dependency: Metabase user/group model
- authority/security: P0
- semantic duplication: none
- operational: identity/group provisioning
- license/API: runtime auth boundary
- proof: same principal allow/deny matrix; existence oracle suppression where applicable
- timing: X0

## M0E-15 — API scopes

- mechanism: named/hierarchical API capability scopes
- source: `src/metabase/api_scope/core.clj::defscope`, `scope-matches?`
- problem: limit API caller capabilities independently of data permissions
- maturity: generic API authorization registry
- Dima equivalent: governed tool/profile permissions
- Wren equivalent: none
- gap: Metabase transport needs least scopes
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: use runtime scopes in X0; Dima still authorizes the operation separately
- native cost: LOW if reimplemented, but unnecessary
- runtime dependency: Metabase API auth
- authority/security: defense-in-depth, not Dima authority replacement
- semantic duplication: none
- operational: token/scope configuration
- license/API: supported API
- proof: missing scope rejects operation; wildcard not over-broad
- timing: X0

## M0E-16 — API-key user as Dima principal

- mechanism: API-key-backed user identity
- source: `src/metabase/api_keys/core.clj`,
  `metabase.api-keys.models.api-key::create-api-key-with-new-user!`
- problem: service authentication
- maturity: supported API-key mechanism
- Dima equivalent: authenticated Dima Principal
- Wren equivalent: explicit principal
- gap: API-key group identity is not enough to prove end-user equivalence
- disposition: **REJECT**
- WHY: may authenticate transport, but cannot silently substitute for per-user Dima principal
- native cost: N/A
- runtime dependency: optional API key
- authority/security: high risk if used as shared super-principal
- semantic duplication: none
- operational: key rotation
- license/API: API auth
- proof: X0 must use representative user/session/JWT mapping; shared key cannot widen permissions
- timing: PRE-X0

## M0E-17 — Permission-filtered search/discovery

- mechanism: searchable entity index with collection/table permission filters
- source: `src/metabase/search/core.clj`; `src/metabase/search/permissions.clj`
- problem: scalable discovery of BI resources without leaking inaccessible entities
- maturity: indexed search subsystem
- Dima equivalent: SemanticCatalogRetriever / future workspace search
- Wren equivalent: semantic catalog context
- gap: no pre-X0 execution gap
- disposition: **PATTERN_ONLY**
- WHY: X0 consumes accepted StandardProjection; search must not become semantic truth
- native cost: MEDIUM
- runtime dependency: none pre-X0
- authority/security: discovery score != semantic truth; permission filter is valuable invariant
- semantic duplication: medium if used for business semantics
- operational: index lifecycle if later reused
- license/API: ordinary search OSS; semantic search differs
- proof: inaccessible resource not discoverable if later used
- timing: PRE-X0 pattern; product search POST-MVP

## M0E-18 — Metabase semantic search engine

- mechanism: embedding/semantic search engine
- source: `src/metabase/search/semantic/core.clj`
- problem: semantic retrieval
- maturity: implemented behind enterprise feature boundary
- Dima equivalent: semantic catalog retrieval/cognition
- Wren equivalent: semantic context
- gap: not needed for X0 execution
- disposition: **DEFER_PRODUCT**
- WHY: OSS path explicitly throws premium-feature error; no reason to add commercial dependency now
- native cost: MEDIUM-HIGH
- runtime dependency: Metabase Enterprise/semantic index
- authority/security: retrieval never authority
- semantic duplication: high if treated as truth
- operational: separate search index
- license/API: **Enterprise/premium requirement**
- proof: later product evaluation only
- timing: POST-MVP

## M0E-19 — Generic Toucan application-model persistence framework

- mechanism: generic app model transforms/hydration/CRUD dispatch
- source: `src/metabase/models/interface.clj`; `models/resolution.clj`
- problem: Metabase application persistence
- maturity: core internal ORM/model framework
- Dima equivalent: own persistence stack
- Wren equivalent: none
- gap: none; not a supported reusable product boundary
- disposition: **NOT_APPLICABLE**
- WHY: internal implementation detail, not residual Agent API value
- native cost: N/A
- runtime dependency: internal Metabase app DB
- authority/security: no Dima ownership
- semantic duplication: none
- operational: internal
- license/API: no direct reuse
- proof: none
- timing: none

## M0E-20 — Model persistence/materialization

- mechanism: persist model/query results into source DB tables with refresh lifecycle
- source: `src/metabase/model_persistence/models/persisted_info.clj`;
  settings/refresh task
- problem: accelerate expensive model queries
- maturity: lifecycle/state/refresh/invalidation subsystem
- Dima equivalent: none required for MVP
- Wren equivalent: execution/materialization may be solved elsewhere
- gap: performance optimization, not correctness
- disposition: **DEFER_PRODUCT**
- WHY: adds write/materialization semantics and operational complexity outside X0
- native cost: HIGH
- runtime dependency: Metabase + source DB writes
- authority/security: write permission/data freshness implications
- semantic duplication: medium
- operational: refresh jobs/tables
- license/API: some controls enterprise-sensitive
- proof: only if performance roadmap later demands it
- timing: POST-MVP / FULL-X later

## M0E-21 — Query result cache

- mechanism: query cache TTL/size/early refresh
- source: `src/metabase/cache/core.clj`; `cache/settings.clj`
- problem: reduce repeated query latency/load
- maturity: configurable cache subsystem
- Dima equivalent: no required Day6.5 cache
- Wren equivalent: not semantic ownership
- gap: optimization only
- disposition: **DEFER_PRODUCT**
- WHY: do not let cache behavior influence substrate correctness decision
- native cost: MEDIUM-HIGH
- runtime dependency: Metabase/app DB/cache
- authority/security: cache hits must preserve permission/freshness rules
- semantic duplication: none
- operational: eviction/refresh/storage
- license/API: runtime feature
- proof: later permission/freshness tests if adopted
- timing: FULL-X / POST-MVP

## M0E-22 — Database metadata sync / FK discovery

- mechanism: sync database/tables/fields/FKs/index metadata via drivers
- source: `src/metabase/sync/core.clj`; `sync/fetch_metadata.clj::db-metadata`,
  `fields-metadata`, `fk-metadata`
- problem: onboard heterogeneous DB schemas and keep technical metadata current
- maturity: mature connector-driven sync subsystem
- Dima equivalent: Wren MDL onboarding + Dima context building
- Wren equivalent: Wren semantic model must still be authored/retained
- gap: potential large generic onboarding/metadata-discovery value
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: can reduce generic connector/sync engineering without owning business semantics
- native cost: HIGH
- runtime dependency: Metabase + drivers
- authority/security: technical metadata discovery must not override Wren semantic definitions
- semantic duplication: medium; must separate physical metadata from semantic truth
- operational: sync jobs / metadata app DB
- license/API: runtime service
- proof: X0/full-X onboarding burden + no semantic ownership transfer
- timing: X0 metric / FULL-X

## M0E-23 — Driver registry / connector ecosystem

- mechanism: driver registration/loading/inheritance/plugin architecture
- source: `src/metabase/driver/impl.clj::register!`, `load-driver-namespace-if-needed!`
- problem: support many databases through one query runtime
- maturity: long-lived connector abstraction
- Dima equivalent: customer DB connectors
- Wren equivalent: Wren/data source support
- gap: possible substantial connector engineering avoided
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: high residual value candidate; must measure against extra service cost
- native cost: HIGH
- runtime dependency: Metabase drivers/plugins
- authority/security: connector reach must be scoped to intended DB/principal
- semantic duplication: none by itself
- operational: driver versions/plugins
- license/API: runtime/plugin ecosystem review
- proof: X0/full-X driver leverage/onboarding metric
- timing: X0 metric / FULL-X

## M0E-24 — JDBC execution / pooling / read-only defaults

- mechanism: connection pooling, session timezone, read-only defaults, query execution
- source: `src/metabase/driver/sql_jdbc/execute.clj::do-with-connection-with-options`,
  `execute-prepared-statement!`
- problem: robust SQL DB execution mechanics
- maturity: mature driver runtime
- Dima equivalent: direct/Wren data connection stack
- Wren equivalent: current incumbent execution stack
- gap: operational/runtime candidate
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: generic infra potentially avoided, not worth reimplementation solely for ownership
- native cost: HIGH
- runtime dependency: JVM/JDBC/pools
- authority/security: read-only path and permissions must be observed
- semantic duplication: none
- operational: pool sizing, memory, failures
- license/API: internal runtime via API
- proof: X0 latency/RAM/network/failure-blast/connection behavior
- timing: X0 / FULL-X

## M0E-25 — Dashboard persistence/write lifecycle

- mechanism: permission-checked dashboard create/update/layout/parameter mappings
- source: `src/metabase/dashboards/write.clj::create-dashboard!`,
  `update-dashboard!`
- problem: mature BI dashboard product/workspace
- maturity: transaction/event/permission-aware product subsystem
- Dima equivalent: future dashboards/workspace
- Wren equivalent: none
- gap: product capability, not execution correctness
- disposition: **DEFER_PRODUCT**
- WHY: UI/workspace attractiveness must not choose X0 substrate
- native cost: HIGH
- runtime dependency: Metabase product/app DB
- authority/security: dashboard refs have read/write/data permission checks
- semantic duplication: possible if dashboard-owned metrics become truth
- operational: app DB/UI
- license/API: later product/API review
- proof: later product track
- timing: DAY11-15 / POST-MVP

## M0E-26 — Collections/workspace organization

- mechanism: collection create/update/archive/sync dependency semantics
- source: `src/metabase/collections/core.clj`
- problem: saved-content workspace hierarchy/permissions
- maturity: core Metabase product feature
- Dima equivalent: future saved analyses/workspaces
- Wren equivalent: none
- gap: not pre-X0
- disposition: **DEFER_PRODUCT**
- WHY: product/workspace track independent of execution substrate
- native cost: MEDIUM-HIGH
- runtime dependency: Metabase app DB
- authority/security: collection permissions remain runtime-local
- semantic duplication: none
- operational: persistence
- license/API: later
- proof: later product acceptance
- timing: POST-MVP

## M0E-27 — Activity feed / recent views

- mechanism: per-user recent resource tracking
- source: `src/metabase/activity_feed/models/recent_views.clj`
- problem: workspace navigation/recency UX
- maturity: bounded/pruned permission-aware recent-view model
- Dima equivalent: none required now
- Wren equivalent: none
- gap: UX only
- disposition: **DEFER_PRODUCT**
- WHY: no Day6.5/X0 relevance
- native cost: LOW-MEDIUM
- runtime dependency: app DB
- authority/security: returned items permission-filtered
- semantic duplication: none
- operational: small app state
- license/API: product feature
- proof: later UX
- timing: POST-MVP

## M0E-28 — Audit application/logging

- mechanism: user/app action audit log
- source: `src/metabase/audit_app/models/audit_log.clj::record-event!`
- problem: operational/product activity audit
- maturity: structured event/model audit subsystem
- Dima equivalent: Dima audit + QueryContract/Evidence/DecisionRecord direction
- Wren equivalent: none
- gap: Dima trust audit is already differentiated core
- disposition: **PATTERN_ONLY**
- WHY: Dima must own trust/evidence audit; Metabase log may later complement its own runtime ops
- native cost: LOW-MEDIUM for existing Dima direction
- runtime dependency: none for Dima core
- authority/security: Dima evidence/audit cannot be delegated to Metabase
- semantic duplication: none
- operational: Metabase audit may be useful observability later
- license/API: audit app features may vary by edition; no source reuse
- proof: existing Dima contract/evidence/audit provider-free tests
- timing: PRE-X0 pattern / POST-MVP runtime ops

## M0E-29 — Static embedding JWT security

- mechanism: signed embed JWT validation, reject `alg=none`, feature enable gate
- source: `src/metabase/embedding/jwt.clj::unsign`; `embedding/validation.clj::check-embedding-enabled`
- problem: securely expose embedded Metabase product surfaces
- maturity: explicit signed-token product boundary
- Dima equivalent: Dima auth/session/embed surfaces
- Wren equivalent: none
- gap: not required for headless X0 Agent API
- disposition: **DEFER_PRODUCT**
- WHY: product embedding is separate from execution/query-lifecycle necessity
- native cost: MEDIUM
- runtime dependency: Metabase UI/embed runtime
- authority/security: JWT pattern is useful; must not bypass Dima auth
- semantic duplication: none
- operational: secret rotation/embed config
- license/API: later product/licensing review
- proof: later embedding threat model
- timing: POST-MVP

## M0E-30 — Query handle / continuation identity and reauthorization

- mechanism: opaque query identity/replay/pagination token with permission revalidation
- source: `src/metabase/mcp/v2/queries.clj::resolve-query-handle!`,
  `resolve-query-handle-for-save!`; Agent API continuation permission checks
- problem: stable execution identity without trusting model context
- maturity: explicit handle/replay mechanisms
- Dima equivalent: QueryContract/Evidence refs
- Wren equivalent: execution/query identities
- gap: potential useful runtime provenance
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: valuable if bound as provenance only and reauthorized every replay
- native cost: MEDIUM-HIGH
- runtime dependency: Metabase app state
- authority/security: **handle != authorization**; Dima authority not conferred
- semantic duplication: none
- operational: state retention
- license/API: runtime API
- proof: acquire handle → revoke permission → replay DENIED; cross-user handle DENIED
- timing: X0

## M0E-31 — Native SQL guard / structured-query isolation

- mechanism: distinguish structured MBQL path from native SQL; scope/kill-switch guards
- source: `src/metabase/agent_api/query_guards.clj`; MCP query tools
- problem: stop agent/query-builder path from smuggling native SQL
- maturity: explicit security boundary
- Dima equivalent: Manager raw-SQL prohibition + governed execution tools
- Wren equivalent: Dima/Wren official execution boundary
- gap: X0 must prove adapter cannot bypass either side
- disposition: **METABASE_RUNTIME_CANDIDATE**
- WHY: runtime must enforce it; Dima also retains outer invariant
- native cost: LOW for Dima invariant, HIGH for full query runtime
- runtime dependency: Metabase for inner guard
- authority/security: P0
- semantic duplication: none
- operational: scope/config
- license/API: supported API boundary
- proof: nested/native marker → fail closed; no raw SQL escape
- timing: X0

## M0E-32 — Dima cognition / accepted authority / evidence

- mechanism: user-intent cognition, exactly-one accepted authority, evidence/completion truth
- source reference contrast: Metabase agent loop/audit mechanisms above
- problem: Dima's differentiating decision/trust semantics
- maturity: existing Dima Day6.5 architecture
- Dima equivalent: Manager/Standard cognition, `AcceptedAuthorityRegistry`,
  SemanticBindingGate, Evidence/Completion gates
- Wren equivalent: none
- gap: none delegated
- disposition: **DIMA_CORE_NATIVE**
- WHY: this is what makes Dima Dima
- native cost: already accepted core
- runtime dependency: none on Metabase
- authority/security: ultimate Dima owner
- semantic duplication: external ownership forbidden
- operational: Dima service
- license/API: none
- required behavioral proof:
  `test_v2_day6_5_manager_authority.py`,
  `test_v2_day6_5_standard_authority.py`,
  `test_v2_day6_5_real_trust_plane.py`
- timing: PRE-X0 / already implemented

# Family coverage

Required M0E families and their material rows:

```text
metabot              M0E-01,02
agent_api            M0E-03,04,15,30,31
mcp                  M0E-02,04,30,31
agent_lib            M0E-05,06,07
query_processor      M0E-08,09
lib                  M0E-10
lib_be               M0E-11
lib_metric            M0E-12
query_permissions    M0E-13
permissions          M0E-14
api_scope            M0E-15
api_keys             M0E-16
search               M0E-17,18
metrics              M0E-12
models               M0E-19
model_persistence    M0E-20
cache                M0E-21
sync                 M0E-22
driver               M0E-23,24
dashboards           M0E-25
collections          M0E-26
activity_feed        M0E-27
audit_app            M0E-28
embedding            M0E-29
```

# PRE-X0 Dima-native behavioral owners

```text
exactly-one authority / cross-family XOR
→ app/v2/standard_authority.py
→ tests/test_v2_day6_5_standard_authority.py

foreign-tenant handle/authority rejection
→ SemanticHandleRegistry + acceptance/standard authority
→ tests/test_v2_day6_5_manager_authority.py
→ tests/test_v2_day6_5_standard_authority.py

evidence presence != verification
→ Dima evidence/completion plane
→ tests/test_v2_day6_5_manager_authority.py

real principal-aware Wren → QueryContract → verified Evidence
→ governed manager/core execution
→ tests/test_v2_day6_5_real_trust_plane.py

closed governed Manager tools / no raw SQL tool
→ manager_tools closed registry + execution boundary
→ provider-free Day6.5 manager tests
```

Runtime-candidate permission/handle/native-SQL behavior remains intentionally an **X0 proof**,
not a pre-X0 Metabase reimplementation.

# M0E exit gate

```text
Dima-relevant Metabase mechanisms UNCLASSIFIED                 = 0
PRE-X0 authority/security mechanisms without disposition       = 0
PATTERN_ONLY / DIMA_CORE_NATIVE PRE-X0 items without owner     = 0
WREN_OWNS items with duplicate Metabase semantic ownership     = 0
METABASE_RUNTIME_CANDIDATE items without X0/FULL-X proof       = 0
```

**M0E-v1 RESULT = VALID BASELINE. FINAL EXHAUSTION = REOPENED / NOT YET GREEN.**

Deferred items are intentionally not implemented.

# Binding conclusions for D65-SI/X0

1. Dima cognition/trust/evidence stays native.
2. Wren semantic backbone stays retained by default.
3. Metabase's strongest current residual-value candidates are:
   - construct/validate/repair/resolve query lifecycle;
   - permission-aware execute/replay;
   - query handles/provenance;
   - technical metadata sync;
   - driver/connector/JDBC runtime leverage.
4. Metabase metric semantic ownership is NOT adopted; it would duplicate Wren.
5. Cache/materialization/dashboard/workspace/activity/embedding are deferred and cannot select X0.
6. X0 may now be designed around runtime necessity, but may not execute until D65-SI + real
   Standard Wren sentinel are GREEN.


# Final-exhaustion supersession

The v1 claim `Dima-relevant UNCLASSIFIED = 0` is historical for the v1 map only.

Current final-exhaustion authority:
`DIMA_DAY6_5_M0E_DEEP_DELTA_CONTRACT.md`.

Do not erase or rewrite the v1 mechanism rows.
