"""Özellik bayrakları (feature flags) — katmanlı çözümleme (ADR-0009).

Değerler: "off" | "alpha" | "beta" | "prod".

İKİ katman:
1. FABRİKA AYARI (kod/YAML): sektör pack.yml → şirket company.yml (şirket kazanır).
   Yeni sektör paketi varsayılanlarını böyle getirir.
2. İŞLETME GERÇEĞİ (DB, admin panelden): FeatureOverride satırları — çözüm kuralı
   EN SPESİFİK KAZANIR: user > role > tenant > sector > global > fabrika ayarı.
   Tanımsız kapsam bir üstünü MİRAS alır; spesifik "off" = kill switch.

NOT: Bayrak = rollout/görünürlük. YETKİ değildir — aksiyon güvenliği her zaman
authorize() matrisinden geçer (permissions); bayrak onu gevşetemez.
"""

from __future__ import annotations

from pathlib import Path

import yaml

STAGES = ("off", "alpha", "beta", "prod")
SCOPE_TYPES = ("global", "sector", "tenant", "role", "user")
# Spesifiklik sırası (soldan sağa artar) — sağdaki tanım soldakini ezer.
_SCOPE_ORDER = ("global", "sector", "tenant", "role", "user")

# ── KANONİK KAYIT (registry) ─────────────────────────────────────────────────
# Platform bayraklarının TEK metadata kaynağı: insan-okur etiket + açıklama +
# kategori. VARSAYILAN AŞAMA burada DEĞİL — o YAML'da (demo/packs/features.yml)
# durur; böylece ops aşamayı git'ten yönetir, kod değişmez. Admin panel bu
# metadata'yı okunabilir etiket/açıklama olarak gösterir (ham snake_case yerine).
#
# YENİ HAM ÖZELLİĞİ FLAG ARKASINA ALMA REÇETESİ (ADR-0009):
#   1) Buraya bir satır ekle (etiket/açıklama/kategori).
#   2) demo/packs/features.yml'e varsayılan aşamayı yaz (genelde `beta` — böylece
#      herkese kapalı, admin panelden seçili müşteriye açılır).
#   3) Tüketen yüzeyi `useFeature("<key>")` ile geçitle (frontend).
#   4) Gerekiyorsa admin panelden tenant/rol/kullanıcı override'ı ile aç.
FLAG_REGISTRY: dict[str, dict[str, str]] = {
    "sosyal_sinif": {
        "label": "Sosyal sınıf (veri-niyeti kapısı)",
        "description": "Veri niyeti taşımayan ifadeler (selam/teşekkür) LLM'e ve SQL'e "
                       "HİÇ gitmez. Kapalıyken `sosyal_ayikla` `route()` girişine "
                       "müdahale etmez ve davranış birebir bugünküdür (FAZ 0.13). "
                       "MIMARI §6.13z/9.11: bir kill-switch yalnız KOD'da varsa YARIMDIR.",
        "category": "Konuşma",
    },
    "capa_zinciri": {
        "label": "Çapa zinciri (karta yanıt)",
        "description": "Bir karta yanıt verirken çapa KİMLİĞİYLE taşınır: tek kart → o "
                       "karta yanıt, çok kart → kesişim, farklı cube'lar → SOR. Kapalıyken "
                       "çapa listesi boş kalır ve davranış birebir bugünküdür (FAZ 0.5).",
        "category": "Konuşma",
    },
    "metrik_sertifikasi": {
        "label": "Metrik sertifikası",
        "description": "Bir metriğin tanımını KİM onayladı ve o onaydan beri tanım ya da "
                       "üst-akış kolon kümesi DEĞİŞTİ Mİ (FAZ 1.5, B8). Çürüyen sertifika "
                       "SİLİNMEZ: seviyesi korunur, üstüne `yeniden_dogrulama_gerekli` "
                       "bayrağı düşer — \"hiç sertifikalanmamış\" ile \"sertifikalanmış "
                       "ama tanım değişmiş\" farklı şeylerdir. TTL 90 gün.",
        "category": "Kanıt",
    },
    "lineage": {
        "label": "Kolon kökeni",
        "description": "\"Bu sayı hangi tablonun hangi kolonundan, hangi DÖNÜŞÜMLE "
                       "geldi?\" — LLM'siz şablon cümleler (FAZ 1.6). Teknik köken GRAFİĞİ "
                       "gösterilmez (KD-13): kullanıcının cevabı bir cümledir, graf bir "
                       "geliştirici artefaktıdır. Discovery ham SQL'inde `bilinmiyor` "
                       "yazılır — `None` ile aynı şey DEĞİL: `None` \"hiç sorulmadı\", "
                       "`bilinmiyor` \"soruldu, cevap yok\". Kapalıyken makbuz birebir "
                       "bugünkü (GERİ AL).",
        "category": "Kanıt",
    },
    "metrik_kaydi": {
        "label": "Metrik kaydı (hakem)",
        "description": "Bir iş terimini birden fazla cube sahipleniyorsa HAKEM kaydı "
                       "karar verir (FAZ 0.18). Kapalıyken kayıt şemaya hiç yazılmaz "
                       "ve davranış birebir bugünküdür — GERİ AL mekanizması budur.",
        "category": "Semantik",
    },
    "cikti_yorumlama": {
        "label": "Çıktı yorumu",
        "description": "Her tablo/grafik/rapor/KPI için deterministik doğal-dil "
                       "yorumu (OutputInsight, ADR-0022).",
        "category": "Analiz",
    },
    "sql_display": {
        "label": "SQL'i göster",
        "description": "Üretilen SQL sorgusunu kullanıcıya açar (rapor altında "
                       "'+ sql göster').",
        "category": "Şeffaflık",
    },
    "verify_button": {
        "label": "Doğrula (✓/✗)",
        "description": "Raporu doğru/yanlış işaretleme — VQR öğrenmesini besler "
                       "(aynı soru sonra LLM'siz cevaplanır).",
        "category": "Öğrenme",
    },
    "scheduled_reports": {
        "label": "Zamanlanmış raporlar",
        "description": "Raporu belirli aralıkla otomatik koşup bildirim üretir "
                       "(🔔 zamanla, ADR-0011).",
        "category": "Otomasyon",
    },
    "dashboards": {
        "label": "Panolar (dashboard)",
        "description": "Chat'te üretilen grafik/tabloyu panoya ekleyip canlı izleme "
                       "(kullanıcı başı ≤10 pano, §9).",
        "category": "Otomasyon",
    },
    "next_steps": {
        "label": "Sonraki adım önerileri",
        "description": "Rapordan deterministik kırılım/ölçek/zaman chip'leri — tıklayınca "
                       "LLM'siz koşar (rehberli analitik K2).",
        "category": "Rehber",
    },
    "ask_intent_first": {
        "label": "Intent-first yönlendirme (/ask)",
        "description": "/ask'te route() boş dönerse LLM'e ham SQL yerine bir Intent-JSON "
                       "(ölçü/boyut/filtre seçimi) doldurttur; deterministik derleyici SQL'i "
                       "üretir (Faz 1). route()'un kendisi bu bayraktan BAĞIMSIZ her zaman "
                       "dener (sıfır risk) — bu bayrak yalnız LLM-destekli Intent-JSON adımını "
                       "kademeli açar (davranış değişikliği taşıyan tek adım).",
        "category": "Yönlendirme",
    },
    "ask_async_discovery": {
        "label": "Discovery arka-plan işi",
        "description": "/ask'in Discovery (ham-SQL LLM) yolu senkron HTTP yerine arka-plan "
                       "işi (AskJob) olarak çalışır; istemci GET /ask/jobs/{id} ile poll eder "
                       "(Faz 4.1 — uzun LLM çağrılarında arayüz donmasın). BİLEREK "
                       "demo/packs/features.yml'e eklenmedi (varsayılan KAPALI) — mevcut "
                       "senkron davranış hiçbir tenant'ta değişmeden kalır; yalnız açıkça "
                       "override edilince devreye girer.",
        "category": "Yönlendirme",
    },
    "threaded_chat": {
        "label": "Konu/thread modeli (sohbet+rapor paneli)",
        "description": "Sohbet panelinde konular (thread) iç-içe gösterilir, rapor paneli "
                       "aynı konunun cevaplarını alta doğru biriktirir (§B, 1 Ağustos 2026). "
                       "BİLEREK demo/packs/features.yml'e eklenmedi (ask_async_discovery ile "
                       "AYNI ilke) — bu, sohbet/rapor panelinin TEMEL render mantığını "
                       "değiştiren büyük bir UX değişikliği; mevcut tek-rapor davranışı "
                       "hiçbir tenant'ta değişmeden kalır, yalnız açıkça override edilince "
                       "devreye girer.",
        "category": "Analiz",
    },
    # ── FAZ 9.11 — bu oturumun ALTI FAZI yönetim yüzeyinde ADSIZDI ────────────────
    # Denetimde ölçüldü: `demo/packs/features.yml`'de 13 bayrak, kayıtta 9. Eksik altısı
    # admin panelde açıklamasız `snake_case` ve kategori *"Diğer"* olarak görünüyordu —
    # yani bayrağı açacak/kapatacak kişi ne yaptığını okuyamıyordu. Bir kill-switch
    # (KURAL B) yalnız KOD'da varsa yarım bir kill-switch'tir.
    "adhoc_cube": {
        "label": "Ad-hoc cube (Discovery cevabına yapı)",
        "description": "LLM'in yazdığı SQL'in SONUCUNDAN oturum-scoped geçici bir cube "
                       "türetir; chip/kırılım/tarih/grafik Discovery cevabında da açılır "
                       "(FAZ 1/K1). Rozet DÜRÜST kalır: source hâlâ llm:*, confidence "
                       "hâlâ None — yapı ≠ güven.",
        "category": "Analiz",
    },
    "liste_niyeti": {
        "label": "Liste/döküm niyeti",
        "description": "'listele'/'dökümü' gibi sorular boyut kırılımına çevrilir (R2 "
                       "yerine cevap). YALNIZ gerçek bir kırılım eşleşirse onurlandırılır "
                       "— aksi hâlde döküm isteyene dejenere tek toplam dönerdi.",
        "category": "Analiz",
    },
    "llm_sema_kisitli": {
        "label": "Şema-kısıtlı LLM çıktısı",
        "description": "Intent-JSON seçimi sağlayıcının native tool-use'una taşınır; "
                       "cube/ölçü/boyut adları o anki kataloğun ENUM'u olur → model var "
                       "olmayan bir adı ÜRETEMEZ. 'hiçbiri' (cube:null) dalı korunur.",
        "category": "Doğruluk",
    },
    "prompt_enhancer": {
        "label": "Soru iyileştirici (LLM)",
        "description": "route() boş dönerse ucuz model soruyu kanonik Türkçeye çevirir ve "
                       "AYNI deterministik yol tekrar denenir. YAPI SEÇMEZ, yalnız metni "
                       "düzeltir; planlayıcının dört kapısından geçer.",
        "category": "Anlama",
    },
    "agent_plan_secimi": {
        "label": "Ajan plan seçimi",
        "description": "LLM hangi aracın hangi sırayla çalışacağını ÖNERİR; her adım yine "
                       "dört kapıdan (kayıt·yetki·deterministik-önce·bütçe) geçer. "
                       "Seçim ≠ çalıştırma: seçicinin yanılması yeni bir risk açmaz.",
        "category": "Ajan",
    },
    "netlestirme_onceligi": {
        "label": "Netleştirme, LLM tahminini önceler",
        "description": "Katalogda ≥2 cube'un sahiplendiği bir ölçüde (ör. 'bakiye' → "
                       "cari|mizan) netleştirme chip'i Intent-JSON'dan ÖNCE gelir. "
                       "Gerçekten belirsiz bir kelimede doğru cevap yoktur; olasılıksal "
                       "bir seçimi 0.85 rozetiyle sunmak onu daha kötü yapar. "
                       "AÇILMADAN ÖNCE kapsam kaybı ölçülmeli.",
        "category": "Doğruluk",
    },
    "t2_anlatici": {
        "label": "T2 anlatıcı (guarded LLM)",
        "description": "Deterministik olguların ÜSTÜNE akıcı Türkçe anlatı ekler; sayıyı "
                       "SİSTEM koyar. narration_guard fail-closed: eşleşmeyen sayı taşıyan "
                       "cümle DÜŞER. Varsayılan KAPALI — sıcak yola LLM ekler.",
        "category": "Anlatım",
    },
}




def _load_yaml(p: Path) -> dict:
    try:
        return yaml.safe_load(p.read_text()) or {}
    except Exception:
        return {}


def company_sectors(settings) -> list[str]:
    """Aktif şirketin sektör pack anahtarları. İki biçim desteklenir:
    ``sektor: x`` (tekil, elle yazılmış) ve ``sektorler: [x, y]`` (materializer/
    çoklu — compose ile AYNI kural: listede önce gelen kazanır)."""
    base = settings.resolved_project_dir().parent
    cfg = _load_yaml(base / "companies" / settings.company / "company.yml")
    return cfg.get("sektorler") or ([cfg["sektor"]] if cfg.get("sektor") else [])


def factory_defaults(settings) -> dict[str, str]:
    """Fabrika ayarı: GLOBAL platform ⊕ sektör paketleri ⊕ şirket YAML'ı (sağdaki kazanır;
    sektörler arasında listede ÖNCE gelen kazanır). 'off' dahil DÖNER — panel bilinen
    bayrak listesini buradan keşfeder.

    Öncelik (en düşük → yüksek): packs/features.yml (GLOBAL platform, sektörden bağımsız) <
    sektör pack.yml < şirket company.yml. Böylece platform yetenekleri TEK yerde durur ve
    her şirketçe miras alınır; sektör pack'leri yalnız sektöre-özel bayrak taşır (ADR-0009)."""
    base = settings.resolved_project_dir().parent
    company_yml = _load_yaml(base / "companies" / settings.company / "company.yml")
    flags: dict[str, str] = {}
    # 1) GLOBAL platform varsayılanları (en düşük öncelik) — sektör/şirketten bağımsız.
    global_yml = _load_yaml(base / "packs" / "features.yml")
    flags.update({k: str(v) for k, v in (global_yml.get("features") or {}).items()})
    # 2) Sektör paketleri — ters sırayla uygula: sonda yazılan ezer → listede önce gelen kazanır.
    for sektor in reversed(company_sectors(settings)):
        pack = _load_yaml(base / "packs" / "sektor" / str(sektor) / "pack.yml")
        flags.update({k: str(v) for k, v in (pack.get("features") or {}).items()})
    # 3) Şirket YAML'ı (en yüksek fabrika önceliği).
    flags.update({k: str(v) for k, v in (company_yml.get("features") or {}).items()})
    return flags


def _db_overrides() -> list:
    """Tüm FeatureOverride satırları. Control-plane erişilemezse boş (bayraklar
    fabrika ayarına düşer — demo kırılmaz)."""
    try:
        from sqlmodel import Session, select

        from control_plane.db import engine
        from control_plane.models import FeatureOverride

        with Session(engine) as s:
            return list(s.exec(select(FeatureOverride)).all())
    except Exception:
        return []


def resolve_for(settings, principal=None) -> dict[str, str]:
    """Principal'a özel etkin bayrak seti ('off' olanlar elenir).

    Kapsam eşlemesi: sector = aktif şirketin pack anahtarı; tenant = principal
    tenant_id; role = principal rol anahtarları; user = principal user_id.
    """
    flags = dict(factory_defaults(settings))

    sectors = set(company_sectors(settings))
    tenant_id = getattr(principal, "tenant_id", None)
    roles = set(getattr(principal, "roles", None) or [])
    user_id = getattr(principal, "user_id", None)

    def _matches(o) -> bool:
        if o.scope_type == "global":
            return True
        if o.scope_type == "sector":
            return o.scope_id in sectors
        if o.scope_type == "tenant":
            return tenant_id is not None and o.scope_id == tenant_id
        if o.scope_type == "role":
            return o.scope_id in roles
        if o.scope_type == "user":
            return user_id is not None and o.scope_id == user_id
        return False

    # Spesifiklik sırasıyla uygula: sonra yazılan (daha spesifik) kazanır.
    overrides = _db_overrides()
    for scope in _SCOPE_ORDER:
        for o in overrides:
            if o.scope_type == scope and _matches(o) and o.stage in STAGES:
                flags[o.feature_key] = o.stage

    return {k: v for k, v in flags.items() if v != "off"}


def resolve(settings) -> dict[str, str]:
    """Geriye-uyum: principal'sız çözüm (fabrika ayarı + yalnız global/sector
    override'ları — kimliksiz bağlamlar için)."""
    return resolve_for(settings, principal=None)
