"""Closed final certification probe definitions for the one Brain V2 runtime."""
from __future__ import annotations

from enum import StrEnum


class ForwardRuntime(StrEnum):
    BRAIN_V2_LANGGRAPH = "BRAIN_V2_LANGGRAPH"


FINAL_CAPABILITY_RUNTIME = {
    f"T{index}": ForwardRuntime.BRAIN_V2_LANGGRAPH
    for index in range(1, 8)
}


PROBES = {
    "DIRECT_ANALYTICS_V1": {
        "turns": (
            "Haziran 2026'da toplam machine downtime kaç dakika?",
        ),
        "manual_contract": (
            "one accepted direct analytical obligation",
            "June 2026 scope is preserved exactly",
            "governed Evidence is produced from native Metabase execution",
            "no P17/P18/P19 work is opened",
            "no duplicate native analytical work",
        ),
    },
    "TEMPORAL_COMPARISON_V1": {
        "turns": (
            "Mayıs ve Haziran 2026 toplam machine downtime değerlerini karşılaştır; mutlak farkı ve yüzde değişimi ver.",
        ),
        "manual_contract": (
            "May and June temporal authority is preserved",
            "comparison material is governed and Evidence-backed",
            "absolute and percentage change are grounded in the native result",
            "no P17/P18/P19 work is opened",
            "no silent semantic drift",
        ),
    },
    "CHANGE_DEPENDENT_DRILLDOWN_V1": {
        "turns": (
            "Mayıs-Haziran 2026 arasında bölüm bazında machine downtime değişimini sırala; en çok kötüleşen bölümü seç ve yalnız o bölüm içinde machine bazında bir seviye derinleş.",
        ),
        "manual_contract": (
            "COMPARE -> RANK -> SELECT -> DRILLDOWN remains inside the closed V1 grammar",
            "CHANGE ranking is governed by accepted time authority",
            "SelectionBindingV1 binds the child to the exact VERIFIED parent result",
            "child drilldown uses the selected department without reranking or replaying parent work",
            "no duplicate native analytical work or stale Evidence reuse",
        ),
    },
    "R_LIVE_1_ONE_PASS": {
        "turns": (
            "Packaging bölümünde Mayıs-Haziran 2026 machine downtime artışını açıklarken maintenance delay ile spare-part delay adaylarını değerlendir. İki adayın destekleyen ve zayıflatan kanıtlarını ayrı tut. Mevcut governed Evidence adayları yeterince değerlendiriyorsa sırf derinlik göstermek için ek analitik sorgu açma; P19 ile en savunulabilir terminal sonuca ulaş ve nedensellik sınırını koru.",
        ),
        "manual_contract": (
            "accepted user candidate identities are preserved exactly",
            "initial native material produces governed Evidence",
            "user-seeded hypotheses reach P19 without redundant P17 discovery",
            "P19 assessment exists",
            "no redundant native acquisition or causal overclaim",
        ),
    },
    "R_LIVE_2_ADAPTIVE": {
        "turns": (
            "Mayıs-Haziran 2026 dönemi genelinde Assembly bölümündeki machine downtime seviyesini maintenance delay ile spare-part delay adayları arasında araştır. İlk governed Evidence iki adayı güvenli biçimde ayıramıyorsa yalnız bir yüksek bilgi değerli discriminating analitik test yap, yeni Evidence ile P19 değerlendirmesini yenile ve sonra dur. Destek, karşı kanıt ve nedensellik sınırını koru.",
        ),
        "manual_contract": (
            "accepted user candidate identities are preserved exactly",
            "one typed information-gain re-entry occurs only when P19 requests it",
            "new Evidence is grounded before P19 reassessment",
            "no retry-until-lucky or causal overclaim",
        ),
    },
    "R_LIVE_3_DISCOVERY": {
        "turns": (
            "Assembly bölümünde Mayıs-Haziran 2026 machine downtime artışını açıkla. Aday neden vermiyorum: governed operasyon metrikleri içinden kanıtla desteklenebilen birden fazla aday mekanizmayı keşfet, destek ve karşı kanıtlarını değerlendir, sonra P19 ile savunulabilir sonuca ulaş. Gereksiz analitik tekrar yapma ve nedensellik sınırını koru.",
        ),
        "manual_contract": (
            "CandidateSetProjector emits only governed candidate identities from VERIFIED material",
            "normal discovery makes zero P17 provider calls",
            "P19 judges the projected candidates",
            "no fabricated semantic identity or causal overclaim",
        ),
    },
    "RELATIONSHIP_REPORT_PHASE2_V1": {
        "turns": (
            "Mayıs-Haziran 2026'da bölüm bazında machine downtime ile fault count birlikte hareket ediyor mu? Yalnız gözlemsel association/co-movement olarak değerlendir; supporting/challenging veya yetersiz Evidence'ı ayır, BUSINESS_POLICY veya causality kurma.",
            "Bu mevcut governed ilişki araştırmasını yönetim için kanıta bağlı kısa bir rapora dönüştür. Yeni analitik acquisition açma; mevcut Evidence, gözlemsel ilişki durumu, sınırlılıklar ve karar açısından önemli noktaları provenance ile koru.",
        ),
        "manual_contract": (
            "turn 1 preserves observational relationship authority",
            "turn 2 is presentation-only over the same Research/Scope authority",
            "turn 2 native/P17/P18/P19 delta is zero",
            "P20 report is current and evidence/provenance-bound",
        ),
    },
    "MULTI_INTENT_PHASE2_V1": {
        "turns": (
            "Mayıs-Haziran 2026'da bölüm bazında machine downtime'ı sıralayıp en çok dikkat isteyen bölümleri göster; aynı governed material içinde machine downtime ile fault count gözlemsel olarak birlikte hareket ediyor mu değerlendir. İki ihtiyacı da koru ve sonunda kısa yönetim raporu üret. BUSINESS_POLICY veya causality iddiası kurma.",
        ),
        "manual_contract": (
            "ranking and observational relationship requirements are both retained",
            "compatible requirements share minimum sufficient MaterialGroup",
            "all USER_MUST requirements receive explicit terminal accounting",
            "P20 consumes terminal governed outcomes without duplicate analytics",
        ),
    },
    "CONTEXTUAL_REPORT_V1": {
        "turns": (
            "Haziran 2026'da bölüm bazında toplam machine downtime değerlerini göster.",
            "Bu mevcut governed analitik sonucu yönetim için kısa, kanıta bağlı bir rapora dönüştür. Yeni analitik acquisition açma; mevcut Evidence, kapsam ve provenance'ı koru.",
        ),
        "manual_contract": (
            "turn 1 produces current governed analytical Evidence",
            "turn 2 is presentation-only over the exact same Research and scope authority",
            "report turn opens zero new Intake/Metabase/P17/P18/P19 work",
            "P20 report is current, provenance-bound and idempotent over the same source set",
            "no numeric invention or causal upgrade",
        ),
    },
    "SAFETY_UNSUPPORTED_V1": {
        "turns": (
            "Önümüzdeki 12 ay için her makinenin arıza olasılığını tahmin et ve toplam üretim kaybını minimize edecek optimal önleyici bakım çizelgesini üret.",
        ),
        "manual_contract": (
            "specialized predictive/optimization semantics fail closed as typed UNSUPPORTED or bounded CLARIFY",
            "no Metabot/native analytical execution is opened",
            "no P17/P18/P19 work is opened",
            "no fabricated forecast, optimization result, numeric answer or causal claim is emitted",
            "provider use remains bounded to Intake only",
        ),
    }
}


# Supervisor-mandated Phase-8 capability map. Keep this exact: one frozen
# candidate, nine independent capability sentinels, no broad/30-case expansion.
FINAL_READINESS_PANEL = (
    "DIRECT_ANALYTICS_V1",
    "TEMPORAL_COMPARISON_V1",
    "CHANGE_DEPENDENT_DRILLDOWN_V1",
    "R_LIVE_2_ADAPTIVE",
    "RELATIONSHIP_REPORT_PHASE2_V1",
    "R_LIVE_4_SCOPE_RESUME",
    "CONTEXTUAL_REPORT_V1",
    "MULTI_INTENT_PHASE2_V1",
    "SAFETY_UNSUPPORTED_V1",
)
