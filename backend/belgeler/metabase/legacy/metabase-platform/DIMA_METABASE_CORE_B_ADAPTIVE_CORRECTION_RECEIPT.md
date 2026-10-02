# DIMA METABASE — CORE-B ADAPTIVE ROOT CORRECTION RECEIPT

**Date:** 2026-09-27  
**Branch:** `feat/dima-metabase-platform`  
**Adaptive root-fix SHA:** `773caa54540e495f52a53d44cf9dabe67acda8c4`  
**Final frozen sentinel SHA:** `e962a76900f0eae5e19c62fe35a89afc1a2301bb`

## Authority result

~~~text
ADAPTIVE DEPENDENCY ROOT CORRECTION = CLOSED / GREEN
FINAL FROZEN SENTINEL              = RED / DIFFERENT FAILURE FAMILY
CORE CLOSURE B                     = NOT SEALED
PLATFORM COMPARISON-READY          = NO
CURRENT ACTION                     = SUPERVISOR STOP
~~~

## Root correction

The removed defect was the heuristic:

~~~text
some VERIFIED Evidence exists
+ another analytical goal is not VERIFIED
→ invoke P17 for the unrelated goal
~~~

The accepted replacement is:

~~~text
ProductInvestigationRequirement
kind = FOLLOW_VERIFIED_MATERIAL
source_goal_id = exact accepted analytical goal
→ persisted product-routing intent
→ P17 invoked on source_goal_id
→ P17 scope validators remain final
~~~

No benchmark manifest authority and no raw-text routing is used.

## Core owner immutability

~~~text
research_manager.py
before = d9a2a83e3f5e678870a2ecbaf330ccb81edb73d7
after  = d9a2a83e3f5e678870a2ecbaf330ccb81edb73d7

research.py                      unchanged
research_product.py              unchanged
report_document.py               unchanged
business_relationship_policy.py  unchanged
hypothesis_root_cause.py         unchanged
~~~

## Provider-free closure

~~~text
Core-B provider-free seal = 36279494493 SUCCESS
governance                = 36279494473 SUCCESS

P14 = 15 PASS
P17 = 108 PASS
P18 = 24 PASS
P19 = 42 PASS
P20 = 19 PASS
P21 = 25 PASS
control-plane security = 6 PASS
~~~

## Focused adaptive live

~~~text
run                              = 36279322283 SUCCESS
dispatch SHA                     = fcbd96c5dbfe7824e157e6ebc82b7ba080c5e182
case                             = adaptive_tr
terminal                         = REPORT
research session                 = rs_05b86069e9b3076d7409956e
source/target analytical goal    = g_702db766de9285afa8b5
inspected Evidence obligations   = [g_702db766de9285afa8b5]
investigation requirement        = pir_db53a5d0d18ccc126b49
fulfilled investigation req      = pir_db53a5d0d18ccc126b49
evidence count                   = 1
artifact count                   = 4
observable model boundary units  = 3
Metabase analytical calls        = 1
P17 manager calls                = 1
total latency                    = 20642 ms
silent wrong                     = 0
security violations              = 0
causal overclaim                 = false
~~~

## One final frozen sentinel

~~~text
run                              = 36279494474 FAILURE
candidate SHA                    = e962a76900f0eae5e19c62fe35a89afc1a2301bb
case count                       = 6
passed                           = 4
failed                           = 2
failed case IDs                 = relationship_explicit_tr
                                  root_cause_tr
observable model boundary units  = 24 / ceiling 30
Metabase analytical calls        = 10
silent wrong                     = 0
security violations              = 0
engine SHA                       = cbe313af9ac2d5960f662068e433d328d896fb06
engine runtime                   = v0.63.18-dima.6
~~~

### relationship_explicit_tr

~~~text
terminal                         = REPORT
evidence count                   = 2
P17 refs                         = 3
P18 policy refs                  = 0
limitation                       = PRODUCT_RELATIONSHIP_LINEAGE_INCOMPLETE
failure                          = P18_RELATIONSHIP_AUTHORITY_NOT_COMPOSED
lineage valid                    = true
security valid                   = true
causal overclaim                 = false
~~~

### root_cause_tr

~~~text
terminal                         = REPORT
evidence count                   = 1
P17 target                       = g_8a68aad2becd7c108ddc
P17 inspected Evidence obligation= g_8a68aad2becd7c108ddc
P17 refs                         = 4
P19 assessment refs              = 0
limitation                       = PRODUCT_P19_COMPETING_HYPOTHESES_INCOMPLETE
failure                          = P19_EPISTEMIC_AUTHORITY_NOT_COMPOSED
lineage valid                    = true
security valid                   = true
causal overclaim                 = false
~~~

## Permanent statements

~~~text
P17 DOMAIN VALIDATION NOT WEAKENED
METABASE ENGINE UNCHANGED
FROZEN SENTINEL UNCHANGED
DEV80 NOT RUN
Validation50 NOT RUN
Hidden50 NOT RUN
UI IMPLEMENTATION NOT STARTED
EXTERNAL SIDE EFFECTS = 0
~~~

The final sentinel RED is a different failure family from the authorized adaptive correction.
Relationship/root-cause paths are sealed. Do not patch them under this directive.
