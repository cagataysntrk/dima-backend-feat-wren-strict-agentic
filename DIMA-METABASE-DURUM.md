# Dima Metabase Platform — Current Status

Canonical current authority lives under `backend/belgeler/metabase/`.

Read:
1. `DIMA_METABASE_CORE_CLOSURE_FINAL_ROADMAP.md`
2. `DIMA_METABASE_CURRENT_PRODUCT_PLAN.md`
3. `DIMA_METABASE_DECISION_RECEIPTS.md`
4. `DIMA_METABASE_CURRENT_HANDOFF.md`

Current state: **Repository canonicalization SEALED → Core A SEALED → Core B FINAL LIVE STOP (P17 provider boundary)**.

Final target: **SEALED NEUTRAL-COMPARISON CANDIDATE**.

~~~text
DEV80 = NOT RUN / NOT AUTHORIZED
VALIDATION50 = NOT RUN / NOT AUTHORIZED
HIDDEN50 = NOT RUN / NOT AUTHORIZED
NEUTRAL COMPARISON = NOT PERFORMED HERE
UI IMPLEMENTATION = NOT STARTED
EXTERNAL EXECUTION = DEFERRED
~~~


## Current Core-B stop — 2026-09-26

~~~text
owner-scoped USER_MUST candidate      = 58fb2d049d9b99b4db10bd71fa4782c12d0ac10a
provider-free seal                    = 36250936119 SUCCESS
governance                            = 36250936065 SUCCESS
final live dispatch SHA               = 2b3b4779f97ecae088a7f2ae73e4f94661ad525a
final real sentinel                   = 36251231885 FAILURE

first wrong transition                = P17 manager provider boundary
trace                                 = research_manager.py
                                      -> research_manager_provider.py
                                      -> structured_transport.py
failure                               = COGNITION_PROVIDER_REJECTED / HTTP 400
failing frozen case                   = root_cause_tr

P14/P20 lifecycle amendment           = PROVIDER-FREE GREEN
P17 semantics changed                 = NO
engine changed                        = NO
manifest / prompt / fixture changed   = NO
final sentinel receipt                = NOT WRITTEN (fail-fast exception)
artifact                              = NONE
observed completed Metabot streams    = 6
observed completed dataset executions = 6

CORE CLOSURE B                        = NOT SEALED
PLATFORM COMPARISON-READY             = NO
STOP                                  = REQUIRED BEFORE SEALED P17 CHANGE
~~~

Do not rerun the final sentinel blindly. Do not modify P17/P18/P19 under the owner-scoped
P14/P20 amendment. A new supervisor decision is required before changing the sealed P17 provider
boundary.
