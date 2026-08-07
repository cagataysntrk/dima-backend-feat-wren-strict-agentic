"""NL→SQL sağlayıcıları.

Uygulamalar:
- `AnthropicSqlGenerator`        — Claude (API key gerekir).
- `OpenAICompatibleSqlGenerator` — OpenAI-uyumlu /chat/completions; **Groq** (ücretsiz key)
                                   ve **Ollama** (tam yerel, anahtarsız) bunu kullanır.
- `RuleBasedSqlGenerator`        — LLM'siz, anahtarsız; boyahane demo şeması (partiler +
                                   oee_vardiya/OEE) üzerinde Türkçe soruları kurallarla
                                   SQL'e çevirir; doğru tabloya yönlendirir.

Üretilen SQL her durumda motorun dry_plan doğrulamasından + SELECT-only guard'dan geçer.
`build_generator(settings)` sağlayıcıyı seçer (bkz. fabrika).
"""

from __future__ import annotations

import contextvars
import re
import time
from typing import Protocol

from app.llm_guard import safe_call
from app.logging_setup import get_logger

# Kapsamlı istek/hata logu (1 Ağustos 2026, kullanıcı talebi: "llm mi patladı api mi
# docker mı front mu net şekilde görelim"). ÖNCEDEN bu modülde HİÇ log YOKTU —
# `FailoverSqlGenerator` bir sağlayıcı hata verip SONRAKİ başarılı olduğunda ARA hatayı
# SESSİZCE yutuyordu (yalnız `errs` listesine ekleniyor, hiçbir yere yazılmıyordu) — bu
# yüzden ör. Anthropic anahtarı geçersizken Gemini'ye sessizce düşülüyor, kullanıcı
# HİÇBİR ZAMAN Anthropic'in patladığını GÖREMİYORDU. Log-and-rethrow deseni: davranış
# (hangi exception'ın fırlatıldığı/yutulduğu) HİÇ DEĞİŞMEZ, yalnız her deneme GÖRÜNÜR olur.
_log = get_logger("llm")

_FENCE = re.compile(r"^```[a-zA-Z]*\n?|\n?```$")


class SaglayiciYaniti(RuntimeError):
    """Sağlayıcı **HTTP 200 döndürdü ama cevap kullanılabilir değil.**"""


def _icerik_cikar(data: dict, saglayici: str, model: str) -> str:
    """OpenAI-uyumlu yanıttan metni çıkar — **teşhisli**.

    ## Ölçülen kusur (2026-08-07, `G0` ön uçuşu)

    Eski hâli tek satırdı: `data["choices"][0]["message"]["content"]`. OpenRouter'ın
    ücretsiz katmanı kısıtlandığında **HTTP 200** ile `{"error": {...}}` döndürüyor;
    `raise_for_status()` bunu geçiriyor ve satır **`KeyError: 'choices'`** ile patlıyordu.
    Yukarıdaki ön uçuş o hatayı görünce *"kota tükenmiş **ya da** anahtar geçersiz
    olabilir"* diye **tahmin** yazdı — teşhis değil, tahmin. ADR-0020'nin *"sessiz yutma
    yok"* kuralı opak hatayı da kapsar: **bir hata, ne olduğunu söylemiyorsa yutulmuştur.**

    ## Üç ayrı durum, üç ayrı mesaj

    | Yanıt | Anlamı |
    |---|---|
    | `{"error": ...}` | sağlayıcı **reddetti** (kota · kısıtlama · geçersiz istek) |
    | `choices` yok | yanıt **beklenen biçimde değil** (sağlayıcı/sürüm uyumsuzluğu) |
    | `content` boş + `finish_reason=length` | 🔴 **AKIL YÜRÜTEN MODEL**: bütçe `reasoning`'e gitti |

    Üçüncüsü bu turda ölçüldü: `nemotron-3-ultra` *"yalnız TAMAM yaz"* isteğine 16
    token'ın tamamını `reasoning`'e harcayıp `content="T"` döndürdü. Bunu *"boş cevap"*
    diye raporlamak, kusurun **modelde** değil **istekte** olduğunu gizlerdi.
    """
    hata = data.get("error")
    if hata:
        mesaj = hata.get("message") if isinstance(hata, dict) else str(hata)
        raise SaglayiciYaniti(
            f"{saglayici} REDDETTİ (model={model}, HTTP 200 gövdesinde error): {mesaj}")
    secenekler = data.get("choices")
    if not secenekler:
        raise SaglayiciYaniti(
            f"{saglayici} yanıtında `choices` YOK (model={model}). "
            f"Gelen anahtarlar: {sorted(data)}")
    ileti = (secenekler[0] or {}).get("message") or {}
    icerik = (ileti.get("content") or "").strip()
    if not icerik:
        bitis = (secenekler[0] or {}).get("finish_reason")
        akil = bool(ileti.get("reasoning") or ileti.get("reasoning_details"))
        if akil or bitis == "length":
            raise SaglayiciYaniti(
                f"{saglayici} BOŞ içerik döndürdü (model={model}, finish_reason={bitis}). "
                "Model AKIL YÜRÜTÜYOR ve token bütçesi `reasoning`'e gitti — "
                "bu model sıcak yola uygun değil ya da `max_tokens` yükseltilmeli.")
        raise SaglayiciYaniti(
            f"{saglayici} BOŞ içerik döndürdü (model={model}, finish_reason={bitis}).")
    return _FENCE.sub("", icerik).strip()
# Diakritik düzleştirme + KESME İŞARETLERİ silinir: "mart'tan"→"marttan", "2026'da"→"2026da"
# (çekim ekleri kesmeyle ayrılınca desen eşleşmeleri kaçıyordu — canlı log kanıtı).
_TR = str.maketrans("ışğüöçİâîû", "isguociaiu", "'’`")

# --- LLM kullanım telemetrisi (model/token/latency) --------------------------
# Generator'lar SINGLETON (servis başına) → eşzamanlı isteklerde instance-attribute
# yarış yaratır. Bu yüzden usage istek-BAZLI bir ContextVar'da toplanır (FastAPI sync
# endpoint'i kendi kopya-context'inde koştuğundan istekler izole). İstek başında
# ``reset_llm_usage()``, çağrılarda ``record_llm_usage()``, sonunda ``get_llm_usage()``.
_llm_usage_var: contextvars.ContextVar = contextvars.ContextVar("dima_llm_usage", default=None)


def reset_llm_usage() -> None:
    """İstek başında: bu isteğin LLM çağrılarını taze bir kovada toplamaya başla."""
    _llm_usage_var.set([])


def record_llm_usage(model: str | None, input_tokens, output_tokens, latency_ms: int) -> None:
    """Bir LLM API çağrısının kullanımını (varsa) mevcut isteğin kovasına ekler."""
    bucket = _llm_usage_var.get()
    if bucket is None:
        return  # istek başında reset edilmedi (eval/test/deterministik yol) → sessizce atla
    bucket.append({
        "model": model, "input_tokens": input_tokens,
        "output_tokens": output_tokens, "latency_ms": latency_ms,
    })


def get_llm_usage() -> dict | None:
    """İstek boyunca biriken LLM kullanımını özetler (çoklu çağrı toplanır). Yoksa None."""
    bucket = _llm_usage_var.get()
    if not bucket:
        return None
    return {
        "model": bucket[-1].get("model"),  # son kullanılan model
        "input_tokens": sum((u.get("input_tokens") or 0) for u in bucket),
        "output_tokens": sum((u.get("output_tokens") or 0) for u in bucket),
        "latency_ms": sum((u.get("latency_ms") or 0) for u in bucket),
        "calls": len(bucket),
    }


def _norm(text: str) -> str:
    # Türkçe büyük İ tuzağı: Python'da "İ".lower() → "i" + U+0307 (combining dot above),
    # _TR'nin İ→i eşlemesi .lower()'dan SONRA hiç tetiklenmez → "DİMA"≠"dima", "NEDİR"≠
    # "nedir" (canlı 2026-07-25: büyük-harf sorguda meta/değer/sinonim eşleşmesi kırılırdı).
    # Combining dot'u sil → tüm büyük-harf İ girişleri doğru normalize olur.
    return text.lower().replace("̇", "").translate(_TR)


class SqlGenerator(Protocol):
    def generate_sql(self, question: str, schema: dict) -> str: ...


# --- ortak prompt -----------------------------------------------------------

_SYSTEM = """Sen bir SQL üreticisisin. Wren semantik katmanı üzerinde çalışan
tek bir okuma-amaçlı (read-only) SQL SELECT sorgusu üretirsin.

Kurallar:
- SADECE verilen tabloları ve kolonları kullan.
- SADECE SELECT / WITH üret. Asla INSERT/UPDATE/DELETE/DROP/DDL üretme.
- Cevabında AÇIKLAMA veya markdown olmasın; yalnızca çalıştırılabilir SQL döndür.
- Kullanıcı Türkçe sorabilir; kolon/tablo adları şemadaki gibi kalır.
- Örnek sorgular DESEN göstermek içindir: onlardaki tablo/kolon adlarını KOPYALAMA;
  yalnız sorunun konusuna uygun tabloları kullan. Sorulmayan filtre/dönem EKLEME.
- Birden fazla satır dönebilecek her sorguya AÇIK bir ORDER BY ekle (sıralama ölçütü
  sorudan belli değilse birincil ölçüye veya ilk boyuta göre sırala). ORDER BY'sız çok
  satırlı bir sorgu + LIMIT kombinasyonu motor/veritabanına göre HANGİ satırların
  döneceğini belirsiz bırakır — aynı soru farklı zamanlarda farklı veri döndürebilir.
"""


def _schema_prompt(schema: dict) -> str:
    from app.sensitivity import prompt_safe_values

    lines = ["Kullanılabilir tablolar:"]
    enum_lines: list[str] = []
    for m in schema.get("models", []):
        cols = ", ".join(f'{c["name"]} {c.get("type", "")}'.strip() for c in m["columns"])
        lines.append(f'- {m["name"]}({cols})')
        for c in m["columns"]:
            # HASSAS KOLON DEĞERLERİ PROMPT'A GİRMEZ (Faz A1) — ölçüldü: bu blok 1391 gerçek
            # değer gönderiyordu, içinde tam ad-soyad, SGK no ve IBAN. Süzgeç TEK yerde
            # (`app/sensitivity.py`) ki `cube_router.build_catalog` ile aynı politikayı
            # uygulasın; eskiden ikisi FARKLI davranıyordu.
            if vals_ok := prompt_safe_values(c):
                vals = ", ".join(str(v) for v in vals_ok)
                enum_lines.append(f'  - {m["name"]}.{c["name"]} ∈ {{{vals}}}')
    if enum_lines:
        lines.append("")
        lines.append("Kategorik kolon değerleri (WHERE filtresi için birebir kullan):")
        lines.extend(enum_lines)
    rels = schema.get("relationships") or []
    if rels:
        lines.append("")
        lines.append("Tablolar arası ilişkiler (JOIN için kullan):")
        for r in rels:
            lines.append(f'- {r["name"]} ({r.get("join_type", "")}): {r.get("condition", "")}')
        lines.append(
            "Çapraz-tablo sorularında bu koşullarla açık JOIN yaz "
            "(ör. partiler ile oee_vardiya makineler üzerinden birleşir)."
        )
    return "\n".join(lines)


def _dialect_hint(dialect: str) -> str:
    """Hedef veritabanı lehçesine göre SQL yazım rehberi (fonksiyon uyumu)."""
    d = (dialect or "").lower()
    if d.startswith("duck"):
        return (
            "Hedef veritabanı: **DuckDB**. SQL'i DuckDB lehçesinde yaz:\n"
            "- Haftanın günü: isodow(tarih) (1=Pzt..7=Paz) ya da dayname(tarih). "
            "ASLA EXTRACT(DAY_OF_WEEK/DOW ...) veya DAYOFWEEK() kullanma.\n"
            "- Ay/hafta/gün kovası: date_trunc('month'|'week'|'day', tarih).\n"
            "- Tarih aralığı: tarih >= CURRENT_DATE - INTERVAL '3 months'.\n"
            "- Sıfıra bölmeyi NULLIF ile engelle."
        )
    if d in ("mssql", "sqlserver"):
        return "Hedef veritabanı: SQL Server (T-SQL). Haftanın günü DATEPART(WEEKDAY, ...); TOP N kullan."
    if d == "oracle":
        return "Hedef veritabanı: Oracle. Haftanın günü TO_CHAR(tarih,'D'); satır limiti FETCH FIRST N ROWS ONLY."
    if d:
        return f"Hedef veritabanı lehçesi: {dialect}. Fonksiyonları bu lehçeye uygun yaz."
    return ""


def _build_system(schema: dict, dialect: str) -> str:
    parts = [_SYSTEM]
    hint = _dialect_hint(dialect)
    if hint:
        parts.append(hint)
    parts.append(_schema_prompt(schema))
    rules = (schema.get("business_rules") or "").strip()
    if rules:
        # ADR-0005 context: sektör/konu bilgisi (metrik semantiği, dönemsel karşılaştırma).
        parts.append("İş kuralları (SQL üretirken KESİNLİKLE uy):\n\n" + rules)
    golden = (schema.get("golden_sql") or "").strip()
    if golden:
        # ADR-0005 context: doğrulanmış örnek sorgular — benzer soruda deseni izle.
        parts.append(golden)
    return "\n\n".join(parts)


def _followup_user(prev_question: str, prev_sql: str, history: list[str], message: str) -> str:
    """Takip mesajı prompt'u (WrenAI'nin followup_sql_generation deseninin Dima-yerlisi —
    ADR: strict-agentic /ask bağlam eksikliği düzeltmesi). WrenAI ham sohbet metnini
    yığmaz: her turu (soru, SQL) çiftine sıkıştırıp SIRADAKİ soruyla birlikte LLM'e verir,
    SQL'i sıfırdan değil önceki SQL'i ÇAPA alarak yeniden ürettirir. Burada da aynı desen:
    önceki soru+SQL güçlü bağlam, geri kalan geçmiş (varsa) yalnız referans içindir."""
    parts: list[str] = []
    older = [h for h in (history or []) if h and h != prev_question][-4:]
    if older:
        parts.append("Daha eski sorular (eski→yeni, yalnız bağlam):\n"
                     + "\n".join(f"- {h}" for h in older))
    parts.append(f"Bir önceki soru: {prev_question}\nBir önceki SQL:\n{prev_sql}")
    parts.append(
        f"Yeni mesaj: {message}\n\n"
        "Yeni mesaj önceki sorunun DEVAMI/DÜZENLEMESİ olabilir (kırılım ekleme/değiştirme, "
        "filtre ekleme/çıkarma, ölçü değiştirme, dönem değiştirme, \"aylara göre\" gibi bir "
        "detaylandırma isteği vb.) — bu durumda BİR ÖNCEKİ SQL'i bu isteğe göre DÜZENLEYEREK "
        "yeni SQL'i yaz (sıfırdan yazma; mevcut yapıyı koru, yalnız istenen değişikliği uygula). "
        "Eğer yeni mesaj öncekiyle TAMAMEN ilgisiz, bağımsız bir konuysa önceki SQL'i YOK SAY "
        "ve sıfırdan yaz. Yalnızca nihai SQL'i döndür, hangi yolu seçtiğini açıklama."
    )
    return "\n\n".join(parts)


def _repair_prompt(question: str, bad_sql: str, error: str) -> str:
    return (
        "Aşağıdaki SQL çalıştırılınca/doğrulanınca HATA verdi. Aynı soruyu, hedef "
        "veritabanı lehçesinde ÇALIŞACAK şekilde yeniden yaz. Sadece SQL döndür.\n\n"
        f"Soru: {question}\nHatalı SQL:\n{bad_sql}\nHata: {error}"
    )


def _anlati_system() -> str:
    """T2 ANLATICI (§4.4) — **LLM ÜSLUBU yazar, SAYIYI sistem koyar.**

    Bu prompt bilerek DAR: girdi olarak yalnız ZATEN HESAPLANMIŞ ve DOĞRULANMIŞ gerçekler
    verilir (`interpret()` çıktısı). Model SQL yazmaz, sayı hesaplamaz, cube seçmez —
    yalnız verilen cümleleri akıcı Türkçeye çevirir. Çıktı `narration_guard`'ın
    FAIL-CLOSED kapısından geçer: eşleşmeyen sayı taşıyan cümle YAYIMLANMAZ.
    """
    return (
        "Sana bir veri raporunun DOĞRULANMIŞ bulguları veriliyor. Görevin bunları akıcı, "
        "kısa ve profesyonel Türkçeyle ANLATMAK.\n\n"
        "MUTLAK KURALLAR:\n"
        "- HİÇBİR YENİ SAYI ÜRETME. Yalnız verilen sayıları, verildiği gibi kullan. "
        "Hesap yapma, yuvarlama, tahmin etme, oran türetme.\n"
        "- Verilmeyen bir olgu EKLEME (sebep, öngörü, sektör kıyası, tavsiye YOK).\n"
        "- 2-4 cümle. Madde işareti yok, başlık yok, emoji yok.\n"
        "- Belirsizlik varsa sus; uydurma."
    )


def _anlati_user(soru: str, gercekler: list[str]) -> str:
    return ("Soru: " + (soru or "—") + "\n\nDoğrulanmış bulgular:\n"
            + "\n".join(f"- {g}" for g in gercekler))


def _enhance_system(catalog: str) -> str:
    """PROMPT-ENHANCER (§4.3) — T1'in DÖRDÜNCÜ, AYRI LLM rolü.

    Intent-JSON alan **SEÇER**; enhancer **yapı seçmez**, yalnız **METNİ** iyileştirir ve
    aynı deterministik `route()`'a geri verir. *"Hangi ölçü/boyut"* kararı hâlâ küptedir —
    bu ayrım fazın varlık sebebidir: LLM'in gücü burada "ifadeyi düzeltmek"le sınırlı kalır.
    """
    return (
        "Kullanıcının veri sorusunu, aşağıdaki katalogda GEÇEN terimlerle YENİDEN YAZ.\n\n"
        "Katalog:\n" + catalog + "\n\n"
        "KURALLAR:\n"
        "- SADECE yeniden yazılmış soruyu döndür. Açıklama, SQL, JSON, tırnak YOK.\n"
        "- ANLAMI DEĞİŞTİRME. Yeni ölçü/boyut/filtre/dönem EKLEME, var olanı ÇIKARMA.\n"
        "- Kullanıcının kelimesinin katalogdaki KARŞILIĞI varsa onu kullan "
        "(ör. 'hasılat' → 'ciro'); yoksa kelimeyi AYNEN bırak.\n"
        "- Katalogda karşılığı OLMAYAN bir şey isteniyorsa soruyu OLDUĞU GİBİ döndür — "
        "uydurma bir terime çevirmek, cevapsız kalmaktan KÖTÜDÜR.\n"
        "- Tek satır, en fazla 15 kelime."
    )


def _plan_sec_system(araclar_json: str, ipucu: str) -> str:
    """ORKESTRATÖR (FAZ 4 / K3) — *"LLM garson olur, işi küpler yapar."*

    Model **iş yapmaz**, yalnız hangi aracın hangi sırayla çağrılacağını **önerir**.
    Öneri `Planlayici.calistir()`'in dört kapısından geçer; uydurulmuş bir araç adı
    KAYIT kapısında ölür. Bu yüzden prompt "doğru seç" demez, "**listeden** seç" der.
    """
    return (
        "Bir veri sorusunu, ELİNDEKİ ARAÇLARLA çözülecek ADIMLARA ayırırsın.\n\n"
        "Araçlar (JSON):\n" + araclar_json + "\n\n"
        + (f"Bağlam: {ipucu}\n\n" if ipucu else "")
        + "KURALLAR:\n"
        "- SADECE yukarıdaki listede ADI GEÇEN araçları seç. Araç UYDURMA.\n"
        '- Çıktı SADECE JSON dizisi: [{"arac":"<ad>","neden":"<kısa Türkçe>"}]\n'
        "- Deterministik araç varsa LLM aracından ÖNCE gelir (`route` her zaman ilk).\n"
        "- En fazla 4 adım. Gereksiz adım EKLEME — her adım bütçe harcar.\n"
        "- Soru tek adımda çözülüyorsa TEK adım döndür."
    )


def _sinonim_system() -> str:
    """OFFLINE SİNONİM ÖNERİCİSİ (FAZ 6 / §4.5) — **çalışma-anı sorgu yoluna ASLA girmez.**

    `mdl_writer.write_cube_yaml` bilinçli olarak *"sinonim ÜRETİLMEZ"* diyor ve bu doğru:
    tahmini bir sinonim, `route()`'un doğrudan davranışını değiştirir. Ama sonuç, tablo
    adından başka etiketi olmayan **çıplak** bir cube — `route()` onu neredeyse hiç
    eşleştiremez. §2.1'in ölçtüğü darboğaz tam burada: *mekanizma üretiliyor, sözlük
    üretilmiyor.*

    Bu rol o boşluğu **insan onayıyla** doldurur: LLM bir TASLAK üretir, çıktı doğrudan
    yazılmaz, `SynonymOverride(approved=False)` kuyruğuna **aday** olarak düşer. Yani
    LLM'in meşru olduğu tek yer: **offline, insan-onaylı öneri.**
    """
    return (
        "Bir veri tablosunun/kolonunun teknik adını, Türkçe konuşan bir iş kullanıcısının "
        "kullanacağı EŞANLAMLILARA çevirirsin.\n\n"
        "KURALLAR:\n"
        "- SADECE JSON dizisi döndür: [\"eşanlam1\", \"eşanlam2\", …]. Açıklama YOK.\n"
        "- En fazla 6 öneri. Emin olmadığını YAZMA — boş dizi döndürmek yanlış öneriden İYİDİR.\n"
        "- Teknik ad ANLAMSIZSA (kod/kısaltma) boş dizi döndür; UYDURMA.\n"
        "- Yalnız küçük harf, Türkçe. Tekil/çoğul varyant üretme (sistem eki kendi çözer)."
    )


def _cube_select_system(catalog: str) -> str:
    """Soruyu SQL değil, tanımlı bir cube SEÇİMİNE eşleten prompt (kısıtlı → halüsinasyon yok)."""
    return (
        "Bir soruyu YÖNETİLEN semantik katmandaki yapısal bir cube sorgusuna eşlersin.\n"
        "Yalnızca aşağıdaki cube'lar, ölçüler ve boyutlar VARDIR:\n\n" + catalog + "\n\n"
        "Kurallar:\n"
        "- SADECE JSON döndür (SQL YOK, açıklama YOK).\n"
        '- Biçim: {"cube":"<ad>","measures":["<ölçü>"],"dimensions":["<boyut>"],'
        '"timeDimensions":[{"dimension":"<zaman>","granularity":"year|quarter|month|week|day"}],'
        '"filters":[{"dimension":"<boyut>","operator":"eq","value":"<değer>"}]}\n'
        "- SADECE yukarıda listelenen ölçü/boyut adlarını kullan.\n"
        # 🔴 `AJ3.4` — **KARŞI AĞIRLIK.** Ölçüldü: bu prompt modele reddetmeyi ÜÇ kez
        # söylüyordu (metinde *"KESİNLİKLE null"*, şemada red **ilk** dal, araç
        # açıklamasında bir kez daha) ve yorumlamayı **bir kez bile** söylemiyordu.
        # Canlı sonuç: **9/9 `{"cube":null}`** — model yanlış anlamadı, hiç anlamaya
        # ÇALIŞMADI. *Bir modele üç kez hayır demeyi öğretip bir kez evet demeyi
        # öğretmemek, onu susturmaktır.*
        "- 🔴 ASIL İŞİN: günlük Türkçeyi bu kataloğun diline ÇEVİRMEK. Kullanıcı ölçü "
        "adı bilmez — *«işler nasıl»*, *«ne kadar kaybettik»*, *«iyi miyiz»* der. "
        "Katalogda makul bir karşılık VARSA onu seç; kelimesi kelimesine eşleşme arama.\n"
        '- {"cube":null} bir KAÇIŞ değil, bir KARARDIR: soru gerçekten tek bir cube ile '
        "yanıtlanamıyorsa (birden çok konunun ölçüsü, tanımsız bir kavram, katalogda "
        "karşılığı olmayan bir istek) onu seç. Emin olamadığın için değil, "
        "**yanıtlanamadığı için**.\n"
        "- FİLTRE UYDURMA: filters'ı yalnız kullanıcı bir değeri AÇIKÇA yazdıysa kullan — "
        "katalogdaki değer listeleri seçenek dökümüdür, varsayılan filtre değildir.\n"
        # 🔴 `AJ3.3` — **İFADE BOŞLUĞU.** *"Tarih yazma"* doğru bir kuraldı ama yarımdı:
        # dönemi yazacak bir ALAN yoktu. Model *"geçen çeyrek"*i hiçbir yere koyamıyordu,
        # tutarlı tek davranışı onu düşürmek ya da tüm soruyu reddetmekti. Takip yolunda
        # (`_cube_refine_user`) bu **çözülmüş** bir problemdi — tasarım oradan alındı.
        "- TARİH HESAPLAMA (sistem yapar) — ama dönemi SÖYLE: sorudaki dönem ifadesini "
        'AYNEN `period_expr` alanına kopyala (*«geçen çeyrek»*, *«yılbaşından bugüne»*). '
        "Yoksa null bırak. `filters` içine tarih YAZMA.\n"
        "- timeDimensions'ı yalnız kullanıcı zaman KOVASI istediyse ekle "
        "(aylık/haftalık/günlük/trend) — bir dönem ifadesi kova demek değildir.\n"
        "- Sıralama/limit ekleme; yalnız ölçü + boyut + zaman + filtre seç.\n"
        # 🔴 `AJ3.5` — ÖRNEKLER. Ölçüldü: dar düzenleme yapan `refine_cube` prompt'unda
        # **4 örnek** vardı, doğal dili yorumlayan bu prompt'ta **0**. Zor işi yapana
        # örnek verilmemişti.
        "\nÖrnekler (biçim için — cube/ölçü adları YUKARIDAKİ katalogdan gelir):\n"
        '- «geçen çeyrek nasıl gidiyoruz» → ilgili özet ölçü + '
        '"period_expr":"geçen çeyrek"\n'
        '- «hat bazında verimlilik» → verim ölçüsü + "dimensions":["hat"]\n'
        '- «aylık ciro trendi» → ciro ölçüsü + timeDimensions granularity="month"\n'
        '- «hem cironun hem personel maliyetinin ilişkisi» → {"cube":null} '
        "(iki ayrı konu + ilişki hesabı)"
    )


def _cube_refine_user(prev_cq_json: str, message: str) -> str:
    """Konuşmasal daraltma — YAPISAL karar protokolü (ADR-0008 K1/K3).

    LLM SQL yazmaz, TARİH HESAPLAMAZ: yalnız katalog-kısıtlı CubeQuery düzenler; dönem
    ifadesini `period_expr`e AYNEN kopyalar (Python çözer; çözemezse sistem sorar)."""
    return (
        "Kullanıcı mevcut bir raporu değiştiriyor.\n"
        f"Mevcut CubeQuery:\n{prev_cq_json}\n\n"
        f"Mesaj: {message}\n\n"
        "Yukarıdaki cube kataloğuna göre TEK bir karar JSON'u döndür (yalnız JSON):\n"
        '{"action": "edit" | "new" | "unavailable",\n'
        ' "cube_query": <edit ise güncellenmiş TAM CubeQuery>,\n'
        ' "period_expr": "<mesajdaki dönem/tarih ifadesi AYNEN; yoksa null>",\n'
        ' "view": "chart|table|line|bar|pie|heatmap|facet" | null,\n'
        ' "reason": "<unavailable ise kısa Türkçe neden>"}\n'
        "KURALLAR:\n"
        "- TARİH HESAPLAMA ve tarih filtresi YAZMA (filters'a tarih dimension'ı EKLEME). "
        'Dönem ifadesi görürsen ("son 6 ay", "1 ocak 31 mart arası", "geçen bayram") '
        "period_expr'e AYNEN kopyala — hesabı sistem yapar.\n"
        "- cube_query yalnız katalogdaki ölçü/boyut adlarını kullanır. Sıralama: "
        '"order":{"measure":"<ölçü>","direction":"asc|desc"}; limit: "limit":N '
        '("en düşük"→asc, "ilk 5"→limit 5).\n'
        "- Mesaj mevcut raporla ilgisiz YENİ bir konuysa action=new.\n"
        "- İstenen alan katalogda YOKSA action=unavailable + reason. UYDURMA.\n"
        '- Görünüm isteği ("grafik/tablo/panelli...") view alanına; görünüm TEK başınaysa '
        "cube_query'yi mevcut haliyle aynen döndür (action=edit).\n"
        'Örnekler: "aylara göre"→timeDimensions month; "vardiyalara göre de"→dimensions\'a '
        'vardiya ekle; "sadece erkek"→filters cinsiyet=Erkek; "X hariç"→operator=neq.'
    )


# --- Anthropic --------------------------------------------------------------


class AnthropicSqlGenerator:
    def __init__(self, api_key: str, model: str, dialect: str = "", select_model: str | None = None):
        from anthropic import Anthropic

        self._client = Anthropic(api_key=api_key)
        self._model = model
        # Faz 4.2 — Intent-JSON seçimi (select_cube/refine_cube) generate_sql/repair'dan
        # (Discovery, ham-SQL) DAHA UCUZ/HIZLI bir modelle yanıtlanabilir; boş → AYNI model
        # (davranış değişmez).
        self._select_model = select_model or model
        self._dialect = dialect

    def _ask(self, system: str, user: str, model: str | None = None) -> str:
        use_model = model or self._model
        _t0 = time.monotonic()
        try:
            # FAZ 1.2b — SAĞLAYICIYA GİDEN TEK KAPI. Çağrı bir closure olarak geçilir:
            # üç sağlayıcının imzaları farklı ve ortak bir imza uydurmak, onların
            # DÖRDÜNCÜ bir temsilini yaratırdı.
            message = safe_call(
                lambda: self._client.messages.create(
                    model=use_model,
                    max_tokens=1024,
                    temperature=0,  # OpenAICompatibleSqlGenerator zaten 0 kullanıyor;
                                    # burada eksikti — Anthropic varsayılanı (1.0) aynı
                                    # soruya farklı SQL üretebiliyordu (canlı 2026-07-31).
                    system=system,
                    messages=[{"role": "user", "content": user}],
                ),
                yuk=f"{system}\n{user}", ad="anthropic._ask")
        except Exception as exc:
            # Log-and-rethrow: davranış (exception'ın FailoverSqlGenerator'a kadar aynen
            # ULAŞMASI) HİÇ değişmez — yalnız BURADA, kaybolmadan ÖNCE, GÖRÜNÜR olur.
            _log.warning("Anthropic API çağrısı başarısız (model=%s, %dms): %s",
                        use_model, int((time.monotonic() - _t0) * 1000), exc, exc_info=True)
            raise
        elapsed_ms = int((time.monotonic() - _t0) * 1000)
        try:  # telemetri — asla yanıtı bozmaz
            _u = getattr(message, "usage", None)
            record_llm_usage(use_model, getattr(_u, "input_tokens", None),
                             getattr(_u, "output_tokens", None), elapsed_ms)
        except Exception:
            pass
        _log.info("Anthropic API başarılı (model=%s, %dms)", use_model, elapsed_ms)
        text = "".join(b.text for b in message.content if b.type == "text")
        return _FENCE.sub("", text.strip()).strip()

    def generate_sql(self, question: str, schema: dict) -> str:
        return self._ask(_build_system(schema, self._dialect), question)

    def generate_followup_sql(self, question: str, schema: dict, prev_question: str,
                              prev_sql: str, history: list[str]) -> str:
        return self._ask(_build_system(schema, self._dialect),
                         _followup_user(prev_question, prev_sql, history, question))

    def repair(self, question: str, schema: dict, bad_sql: str, error: str) -> str:
        return self._ask(_build_system(schema, self._dialect), _repair_prompt(question, bad_sql, error))

    def sinonim_oner(self, teknik_ad: str, baglam: str = "") -> str:
        """OFFLINE sinonim TASLAĞI (FAZ 6). Çıktı doğrudan YAZILMAZ — insan onay kuyruğuna
        aday olarak düşer. Çalışma-anı sorgu yoluna ASLA girmez."""
        return self._ask(_sinonim_system(),
                         f"Teknik ad: {teknik_ad}" + (f"\nBağlam: {baglam}" if baglam else ""),
                         model=self._select_model)

    def plan_sec(self, soru: str, araclar_json: str, ipucu: str = "") -> str:
        """ORKESTRATÖR (FAZ 4). Dönüş bir ÖNERİDİR (JSON) — çalıştırmayı `Planlayici` yapar."""
        return self._ask(_plan_sec_system(araclar_json, ipucu), soru, model=self._select_model)

    def prompt_enhance(self, soru: str, catalog: str) -> str:
        """PROMPT-ENHANCER (FAZ 3b). Dönüş bir METİNDİR — yapı DEĞİL. Çağıran onu aynı
        deterministik `route()`'a verir; karar hâlâ küpündür."""
        return self._ask(_enhance_system(catalog), soru, model=self._select_model)

    def anlat(self, soru: str, gercekler: list[str]) -> str:
        """T2 anlatıcı (FAZ 5). Çıktı ÇAĞIRAN tarafından `narration_guard`'tan GEÇİRİLİR —
        bu metodun dönüşü HAM'dır ve doğrudan yayımlanamaz.

        ⚠ Zaman bütçesi çağıranda (`answer._anlati_ekle`), burada değil: bütçe bir **ürün
        kararıdır** (*"süs ne kadar bekletebilir"*), sağlayıcı ayrıntısı değil.
        """
        return self._ask(_anlati_system(), _anlati_user(soru, gercekler),
                         model=self._select_model)

    #: 🔴 **YETENEK BEYANI — `B5`.** Bu sağlayıcı native tool-use ile şema kısıtını
    #: **gerçekten uyguluyor**; şema üretmeye değer.
    sema_kullanir = True

    def select_cube(self, question: str, catalog: str, sema: dict | None = None) -> str:
        """FAZ 3a — `sema` verilirse sağlayıcının NATIVE tool-use'u kullanılır: cube/ölçü/
        boyut adları o anki kataloğun **enum**'u olarak şemaya gömülür ve model şemanın
        dışına çıkmadan geçersiz bir ad üretemez. Şema yoksa ya da tool-use yolu herhangi
        bir nedenle başarısız olursa **bugünkü serbest-JSON yoluna düşülür** — ikisi de
        aynı `parse_cube_query`'ye varır, yani yedek yol zaten doğrulanmış."""
        if sema is None:
            return self._ask(_cube_select_system(catalog), question, model=self._select_model)
        try:
            return self._arac_ile(_cube_select_system(catalog), question, sema)
        except Exception:
            _log.warning("şema-kısıtlı select_cube başarısız → serbest-JSON yedeği",
                         exc_info=True)
            return self._ask(_cube_select_system(catalog), question, model=self._select_model)

    def _arac_ile(self, system: str, user: str, sema: dict) -> str:
        """Anthropic tool-use ile ŞEMA-KISITLI CubeQuery. Dönüş bugünküyle AYNI sözleşme
        (JSON metni) — çağıran taraf değişmez, yalnız o metnin ÜRETİLİŞ biçimi değişir."""
        import json as _json

        _t0 = time.monotonic()
        message = safe_call(
            lambda: self._client.messages.create(
                model=self._select_model or self._model,
                max_tokens=1024, temperature=0, system=system,
                messages=[{"role": "user", "content": user}],
                tools=[{"name": "cube_query", "input_schema": sema,
                        "description": "Soruyu yapısal bir CubeQuery'ye eşle. Soru TEK bir "
                                       "cube ile yanıtlanamıyorsa cube=null dalını seç."}],
                tool_choice={"type": "tool", "name": "cube_query"},
            ),
            yuk=f"{system}\n{user}", ad="anthropic._arac_ile")
        elapsed_ms = int((time.monotonic() - _t0) * 1000)
        try:
            _u = getattr(message, "usage", None)
            record_llm_usage(self._select_model or self._model,
                             getattr(_u, "input_tokens", None),
                             getattr(_u, "output_tokens", None), elapsed_ms)
        except Exception:
            pass
        for b in message.content:
            if getattr(b, "type", None) == "tool_use":
                return _json.dumps(b.input, ensure_ascii=False)
        raise RuntimeError("tool_use bloğu dönmedi")

    def refine_cube(self, prev_cq_json: str, message: str, catalog: str) -> str:
        return self._ask(_cube_select_system(catalog), _cube_refine_user(prev_cq_json, message),
                         model=self._select_model)


# --- OpenAI-uyumlu (Groq / Ollama) ------------------------------------------


class OpenAICompatibleSqlGenerator:
    """OpenAI /chat/completions sözleşmesini konuşan her sağlayıcı için ortak istemci.
    Groq: base_url=https://api.groq.com/openai/v1 (Bearer key).
    Ollama: base_url=http://localhost:11434/v1 (key gerekmez)."""

    def __init__(self, base_url: str, api_key: str, model: str, provider: str = "openai", dialect: str = "",
                 select_model: str | None = None):
        self._url = base_url.rstrip("/") + "/chat/completions"
        # 🔴 **ANAHTAR ZİNCİRİ.** `api_key` virgüllü bir liste olabilir; ilk eleman
        # bugünkü tek anahtarla **birebir aynı** davranır. Kota dolunca (`402`/`429`)
        # sıradakine geçilir ve tur başa döndüğünde ilki tazelenmiş olur.
        #
        # ⚠ Rotasyon **çağrı başına değil, HATA başına**: her istekte anahtar değiştirmek
        # sağlayıcının kota muhasebesini okunamaz kılar ve hangi anahtarın dolduğunu
        # **hiç** öğrenemezdik. *Bir yedek, ancak öncekinin neden düştüğü bilinirse
        # yedektir.*
        self._keys = [k.strip() for k in str(api_key or "").split(",") if k.strip()]
        self._key_ix = 0
        self._model = model
        # Faz 4.2 — bkz. AnthropicSqlGenerator._select_model docstring'i (aynı ilke).
        self._select_model = select_model or model
        self._provider = provider
        self._dialect = dialect

    def _chat(self, system: str, user: str, model: str | None = None) -> str:
        import requests  # wrenai zaten requests'e bağımlı

        use_model = model or self._model
        headers = {"Content-Type": "application/json"}
        if self._keys:
            headers["Authorization"] = f"Bearer {self._keys[self._key_ix]}"
        payload = {
            "model": use_model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        _t0 = time.monotonic()
        try:
            resp = safe_call(
                lambda: requests.post(self._url, json=payload, headers=headers,
                                      timeout=30),
                yuk=f"{system}\n{user}", ad=f"{self._provider}._chat")
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            # 🔴 **KOTA DOLDU → SIRADAKİ ANAHTAR.** Yalnız `402`/`429` (ödeme/hız sınırı)
            # rotasyona sebep olur: bir şema hatası ya da 500, anahtar değiştirmekle
            # düzelmez ve zinciri boşuna tüketirdi.
            # ⚠ Rotasyon **yeniden denemez** — çağrı bu tur düşer, sonraki tur yeni
            # anahtarla açılır. Aynı istek içinde denemek, bir hatayı gizleyip süreyi
            # ikiye katlardı. *Bir yedeğe geçmek, hatayı silmek değil bir sonrakini
            # kurtarmaktır.*
            _m = str(exc)
            if len(self._keys) > 1 and ("402" in _m or "429" in _m):
                self._key_ix = (self._key_ix + 1) % len(self._keys)
                _log.warning("%s: kota/ödeme hatası → anahtar %d/%d'e geçildi",
                             self._provider, self._key_ix + 1, len(self._keys))
            # Log-and-rethrow — bkz. AnthropicSqlGenerator._ask (aynı desen). Groq/Ollama/
            # Gemini/xAI HEPSİ bu sınıftan geçer; `provider` alanı hangisi olduğunu netleştirir.
            _log.warning("%s API çağrısı başarısız (model=%s, %dms): %s",
                        self._provider, use_model, int((time.monotonic() - _t0) * 1000), exc, exc_info=True)
            raise
        elapsed_ms = int((time.monotonic() - _t0) * 1000)
        try:  # telemetri — asla yanıtı bozmaz
            _u = data.get("usage") or {}
            record_llm_usage(use_model, _u.get("prompt_tokens"), _u.get("completion_tokens"), elapsed_ms)
        except Exception:
            pass
        _log.info("%s API başarılı (model=%s, %dms)", self._provider, use_model, elapsed_ms)
        return _icerik_cikar(data, self._provider, use_model)

    def generate_sql(self, question: str, schema: dict) -> str:
        return self._chat(_build_system(schema, self._dialect), question)

    def generate_followup_sql(self, question: str, schema: dict, prev_question: str,
                              prev_sql: str, history: list[str]) -> str:
        return self._chat(_build_system(schema, self._dialect),
                          _followup_user(prev_question, prev_sql, history, question))

    def repair(self, question: str, schema: dict, bad_sql: str, error: str) -> str:
        return self._chat(_build_system(schema, self._dialect), _repair_prompt(question, bad_sql, error))

    def sinonim_oner(self, teknik_ad: str, baglam: str = "") -> str:
        """OFFLINE sinonim taslağı (FAZ 6) — bkz. `AnthropicSqlGenerator.sinonim_oner`."""
        return self._chat(_sinonim_system(),
                          f"Teknik ad: {teknik_ad}" + (f"\nBağlam: {baglam}" if baglam else ""),
                          model=self._select_model)

    def plan_sec(self, soru: str, araclar_json: str, ipucu: str = "") -> str:
        """ORKESTRATÖR (FAZ 4) — bkz. `AnthropicSqlGenerator.plan_sec`."""
        return self._chat(_plan_sec_system(araclar_json, ipucu), soru,
                          model=self._select_model)

    def prompt_enhance(self, soru: str, catalog: str) -> str:
        """PROMPT-ENHANCER (FAZ 3b) — bkz. `AnthropicSqlGenerator.prompt_enhance`."""
        return self._chat(_enhance_system(catalog), soru, model=self._select_model)

    def anlat(self, soru: str, gercekler: list[str]) -> str:
        """T2 anlatıcı (FAZ 5) — bkz. `AnthropicSqlGenerator.anlat`."""
        return self._chat(_anlati_system(), _anlati_user(soru, gercekler),
                          model=self._select_model)

    #: 🔴 **YETENEK BEYANI — `B5`.** Bu sağlayıcı `oneOf` desteklemiyor, yani `sema`
    #: argümanını **hiç okumuyor**. Ama çağıran bunu bilmiyordu ve şemayı **her istekte
    #: üretiyordu**: ölçüldü, 23 cube'luk demoda **~10.000 token**lık bir yapı kuruluyor
    #: ve **atılıyor**.
    #:
    #: ⚠ Çözüm çağıranda bir `isinstance` DEĞİL: *aynı kuralın iki sahibi olmaz.* Bir
    #: sağlayıcının şema kullanıp kullanmadığını **kendisi** bilir; çağıran sorar.
    #: *Bir yeteneği dışarıdan tahmin etmek, onu iki yerde tanımlamaktır.*
    sema_kullanir = False

    def select_cube(self, question: str, catalog: str, sema: dict | None = None) -> str:
        """FAZ 3a — `sema` KABUL EDİLİR ama BU SAĞLAYICIDA KULLANILMAZ (bilinçli).
        OpenAI-uyumlu uçların `strict` fonksiyon şeması `oneOf`'u desteklemiyor; kısıtı
        yarım uygulamak, uygulamamaktan **kötüdür** (model geçerli ama yanlış bir dala
        zorlanabilirdi). Bugünkü serbest-JSON yolu korunur ve `parse_cube_query` zaten
        doğruluyor. İmza uyumlu kalır ki `FailoverSqlGenerator` ayrım yapmasın."""
        return self._chat(_cube_select_system(catalog), question, model=self._select_model)

    def refine_cube(self, prev_cq_json: str, message: str, catalog: str) -> str:
        return self._chat(_cube_select_system(catalog), _cube_refine_user(prev_cq_json, message),
                          model=self._select_model)


# --- Kural-tabanlı (anahtarsız) — boyahane demo şeması ----------------------

# OEE / vardiya tablosuna yönlendiren anahtar kelimeler.
_OEE_HINTS = (
    "oee",
    "verim",  # kök: verim, verime, verimli, verimlilik, verimsiz
    "vardiya",
    "varidya",  # yaygın harf devriği
    "personel",
    "operator",
    "durus",
    "kullanilabilirlik",
    "performans",
    "availability",
    "downtime",
    "ariza",
)


#: Sayma dalının meşruiyet şartı — bkz. `RuleBasedSqlGenerator._partiler_sql`'in
#: koşulsuz `else` dalının kapatılma gerekçesi.
_SAYMA_NIYETI = ("kac ", " kac", "sayisi", "adet", "kacar")


#: Satır DÖKÜMÜ niyeti — `_partiler_sql`in aşağıdaki liste dalıyla **aynı kelimeler**.
#: ⚠ Tek sahip: iki yerde iki liste tutmak, bu deponun ölçülmüş kusur sınıfıdır.
_LISTE_KELIMELERI = ("listele", "liste", "goster", "hangileri", "hangi", "detay", "dokum")


def _liste_niyeti(q: str) -> bool:
    """Soru bir **satır dökümü** mü istiyor — tek bir sayı değil?

    🔴 Bu, sayma dalının meşru istisnasıdır: döküm **uydurmaz**, veriyi olduğu gibi
    gösterir. Uydurma riski tek bir sayı vermekte; kullanıcı bir tabloya bakarken ne
    aldığını görür.
    """
    return any(w in q for w in _LISTE_KELIMELERI)


def _sayma_dayanagi(q: str, cols: set) -> bool:
    """Soruda sayma dalını haklı çıkaran bir dayanak var mı — **iki şart BİRDEN**.

    1. **Açık sayma niyeti** — `kaç` · `sayısı` · `adet`.
    2. **Tanınan bir varlık** — şemanın bir kolon adının kökü soruda geçiyor.

    ## 🔴 Neden "VEYA" değil "VE" — ölçümle düzeltildi

    İlk yazımda "biri yeterli" denmişti ve gerekçesi şuydu: *"sayma niyeti açıkça
    yazılmışsa kullanıcı bir SAYI istemiştir."* **Ölçüm o gerekçeyi çürüttü:**

        flarnak bizde kac  →  SELECT COUNT(*) FROM partiler  →  **37 878**

    `flarnak` hiçbir yerde tanınmıyor; kullanıcı *"kaç flarnak"* diye sordu, sistem
    *"37 878 parti"* dedi ve **notsuz** gönderdi. Sayma niyeti *sayının istendiğini*
    söyler, **neyin sayılacağını** söylemez.

    ⚠ Kapsam bedeli bilerek ödendi: `kaç kayıt var` gibi varlıksız sorular da düşer.
    Bu **dar ama dürüsttür** ve kural motoru zaten anahtarsız yedektir — üst basamak
    (Discovery) o soruları hâlâ deneyebilir.

    ⊙ `kaç parti` KORUNUR: `parti_no` kolonunun kökü (`parti`) soruda geçer.

    *Bir sınırı çizerken, çizginin hangi tarafında yanlış cevap, hangi tarafında eksik
    cevap kaldığını bilmek gerekir; bu kural yanlışı keser, eksiği bırakır.*
    """
    if not any(w in q for w in _SAYMA_NIYETI):
        return False
    return any(len(c) >= 4 and c.split("_")[0] in q for c in cols)


class RuleBasedSqlGenerator:
    """LLM'siz sezgisel NL→SQL. İki tabloyu yönlendirir:
    - `oee_vardiya` (OEE): makine/vardiya bazlı verimlilik (47-tablo rebind, eski adı
      `vardiya_kayitlari` — bkz. app/llm.py Faz 2b notu, kolon adları da değişti).
    - `partiler` (boya partileri): fire, su/enerji, maliyet, renk sapması, ağırlık, ciro."""

    def generate_followup_sql(self, question: str, schema: dict, prev_question: str,  # noqa: ARG002
                              prev_sql: str, history: list[str]) -> str:  # noqa: ARG002
        # Kural motoru bağlam düzenleyemez (kalıp eşleştirici, LLM değil) — takip mesajını
        # bağımsız bir soru gibi ele alır. Onurlu sınır: sessiz yanlış üretmek yerine
        # en azından anahtar-kelime kalıbına uyan bir SQL döner ya da dürüstçe reddeder.
        return self.generate_sql(question, schema)

    def generate_sql(self, question: str, schema: dict) -> str:
        models = schema.get("models") or []
        if not models:
            raise ValueError("Şemada model yok.")
        q = _norm(question)
        names = {m["name"]: m for m in models}

        # Sevkiyat / termin soruları (sipariş + sevkiyat + müşteri).
        if any(w in q for w in ["sevkiyat", "sevk", "termin", "teslim", "gecik"]) and "sevkiyatlar" in names:
            return self._sevkiyat_sql(q)

        # Reçete-kimyasal (BOM) — "reçete" ya da "kimyasal" (ama parti "kimyasal maliyet"i değil).
        if ("recete" in q or ("kimyasal" in q and "maliyet" not in q)) and "recete_kimyasal" in names:
            return self._recete_sql(q)

        # Çapraz-tablo: verim (oee_vardiya) VE fire (partiler) birlikte,
        # makineler hub'ı üzerinden birleştirilir.
        oee_hit = any(h in q for h in _OEE_HINTS)
        fire_hit = "fire" in q
        both_tables = {"oee_vardiya", "partiler", "makineler"} <= set(names)
        if oee_hit and fire_hit and both_tables:
            return self._cross_makine_sql(q)

        use_oee = oee_hit and "oee_vardiya" in names
        if use_oee:
            return self._oee_sql(q, names["oee_vardiya"])
        # ŞEMA-GUARD (panel K8, 4 ajan): _partiler_sql boyahane şemasına ÖZGÜdür
        # (fire_kg/agirlik_kg). partiler yoksa `models[0]`'a bu şablonu uygulamak
        # mikro/logo/netsis tenant'ında sessiz-yanlış/çökme üretir → dürüst ret.
        if "partiler" not in names:
            raise ValueError(
                "Kural-tabanlı jeneratör bu şemayı desteklemiyor (boyahane-özel şablon); "
                "gerçek LLM sağlayıcı gerekli."
            )
        return self._partiler_sql(q, question, names["partiler"])

    # -- top-N ayrıştırma ("ilk 3", "en çok 5 makine", "3 makine") --------
    @staticmethod
    def _top_n(q: str) -> int | None:
        m = re.search(r"\b(?:ilk|top|en\s+\w+)\s+(\d+)", q) or re.search(
            r"\b(\d+)\s+(?:makin|musteri|parti|vardiya|renk|kumas|recete|kimyasal|personel|siparis)",
            q,
        )
        return int(m.group(1)) if m else None

    def _limit(self, q: str, has_top: bool, dim_present: bool) -> str:
        n = self._top_n(q)
        if n and dim_present:
            return f" LIMIT {n}"
        if has_top and dim_present:
            return " LIMIT 1"
        return ""

    # -- sevkiyat / termin ------------------------------------------------
    def _sevkiyat_sql(self, q: str) -> str:
        _, direction = self._direction(q)
        # Geciken siparişler: termini geçmiş ve tamamlanmamış.
        if "gecik" in q:
            return (
                "SELECT s.siparis_no, m.musteri_adi, s.kumas_cinsi, s.renk, s.miktar_kg, "
                "s.termin, s.durum FROM siparisler s "
                "JOIN musteriler m ON s.musteri_kodu = m.musteri_kodu "
                "WHERE s.termin < CURRENT_DATE AND s.durum <> 'tamamlandi' "
                "ORDER BY s.termin ASC"
            )
        if "sevkiyat" in q or "sevk" in q:
            if "fire" in q and "oran" in q:
                measure, alias = "ROUND(SUM(fire_kg)*100.0/NULLIF(SUM(brut_sevk_kg),0),2)", "sevk_fire_orani"
            elif "fire" in q:
                measure, alias = "SUM(fire_kg)", "toplam_sevk_fire_kg"
            elif "net" in q:
                measure, alias = "SUM(net_sevk_kg)", "toplam_net_sevk_kg"
            else:
                measure, alias = "SUM(brut_sevk_kg)", "toplam_brut_sevk_kg"
            if "musteri" in q:
                return (
                    f"SELECT m.musteri_adi, {measure} AS {alias} "
                    "FROM sevkiyatlar sv JOIN siparisler s ON sv.siparis_no = s.siparis_no "
                    "JOIN musteriler m ON s.musteri_kodu = m.musteri_kodu "
                    f"GROUP BY m.musteri_adi ORDER BY {alias} {direction}"
                )
            return f"SELECT {measure} AS {alias} FROM sevkiyatlar"
        # termin listesi (yaklaşan siparişler)
        return (
            "SELECT s.siparis_no, m.musteri_adi, s.kumas_cinsi, s.miktar_kg, s.termin, s.durum "
            "FROM siparisler s JOIN musteriler m ON s.musteri_kodu = m.musteri_kodu "
            "ORDER BY s.termin ASC"
        )

    # -- reçete-kimyasal (BOM) -------------------------------------------
    def _recete_sql(self, q: str) -> str:
        has_top, direction = self._direction(q)
        limit = self._limit(q, has_top, True)
        cost = "maliyet" in q or "pahali" in q
        # Kimyasal bazında (reçete kelimesi yoksa): kaç reçetede / toplam maliyet katkısı.
        if "kimyasal" in q and "recete" not in q:
            measure, alias = ("SUM(rk.maliyet_katki)", "toplam_maliyet_katki") if cost else ("COUNT(*)", "recete_sayisi")
            return (
                f"SELECT k.kimyasal_adi, k.tur, ROUND({measure},3) AS {alias} "
                "FROM recete_kimyasal rk JOIN kimyasallar k ON rk.kimyasal_kodu = k.kimyasal_kodu "
                f"GROUP BY k.kimyasal_adi, k.tur ORDER BY {alias} {direction}{limit}"
            )
        # Reçete bazında toplam kimyasal maliyet katkısı ve kimyasal sayısı.
        return (
            "SELECT r.recete_no, r.renk_adi, r.boya_turu, "
            "ROUND(SUM(rk.maliyet_katki),3) AS maliyet_katki, COUNT(*) AS kimyasal_sayisi "
            "FROM recete_kimyasal rk JOIN receteler r ON rk.recete_no = r.recete_no "
            f"GROUP BY r.recete_no, r.renk_adi, r.boya_turu ORDER BY maliyet_katki {direction}{limit}"
        )

    # -- çapraz-tablo: makine bazında verim + fire (makineler hub) --------
    def _cross_makine_sql(self, q: str) -> str:
        _, direction = self._direction(q)
        # Sıralama ölçütü: "verim/oee" mi "fire" mı öne çıkıyor?
        order_col = "ort_oee" if ("verim" in q or "oee" in q) else "fire_orani_yuzde"
        return (
            "WITH oee AS ("
            "SELECT makine, AVG(OEE) AS ort_oee FROM oee_vardiya GROUP BY makine"
            "), fire AS ("
            "SELECT makine, ROUND(SUM(fire_kg)*100.0/NULLIF(SUM(agirlik_kg),0),2) "
            "AS fire_orani_yuzde FROM partiler GROUP BY makine"
            ") SELECT m.makine, m.tip, m.kapasite_kg AS kapasite, "
            "oee.ort_oee, fire.fire_orani_yuzde "
            "FROM makineler m "
            "LEFT JOIN oee ON oee.makine = m.makine "
            "LEFT JOIN fire ON fire.makine = m.makine "
            f"ORDER BY {order_col} {direction}"
        )

    # -- ortak: sıralama yönü ve top --------------------------------------
    @staticmethod
    def _direction(q: str) -> tuple[bool, str]:
        asc = any(w in q for w in ["en dusuk", "en az", "en kotu", "en verimsiz"])
        desc = any(w in q for w in ["en cok", "en yuksek", "en fazla", "en verimli", "en iyi", "en buyuk", "hangisi"])
        return (asc or desc), ("ASC" if asc else "DESC")

    # -- OEE / vardiya ----------------------------------------------------
    # NOT (Faz 2b, 31 Temmuz 2026): bu metod 47-tablo rebind'inden (eski
    # `vardiya_kayitlari` → `oee_vardiya`) SONRA hiç güncellenmemişti — `use_oee`
    # kapısı (`"vardiya_kayitlari" in names`) artık HİÇBİR ZAMAN doğru olmadığından bu
    # metot fiilen ÖLÜ KODdu; oee-ipucu taşıyan sorular sessizce `_partiler_sql`'e
    # (ilgisiz cube) düşüyordu (gerçek bulgu: "duruş nedenlerine göre..." → alakasız
    # parti_sayisi cevabı). Tablo/kolon adları GERÇEK `oee_vardiya` şemasına göre
    # düzeltildi (bkz. demo/companies/demo-boyahane/models/oee_vardiya/metadata.yml).
    # `personel_kodu` artık BU tabloda YOK (operatör verimliliği `parti` cube'una taşındı,
    # bkz. oee cube metadata'sının kendi yorumu) — personel-boyutu dalı bilerek kaldırıldı.
    def _oee_sql(self, q: str, model: dict) -> str:
        cols = {c["name"] for c in model["columns"]}

        if "kullanilabilirlik" in q or "availability" in q:
            measure, alias = "AVG(kullanilabilirlik_EV)", "ort_kullanilabilirlik"
        elif "performans" in q:
            measure, alias = "AVG(performans_PV)", "ort_performans"
        elif "durus" in q or "ariza" in q or "downtime" in q:
            measure, alias = "SUM(planli_durus_dk + plansiz_durus_dk)", "toplam_durus_dakika"
        elif "calisma" in q:
            measure, alias = "SUM(calisma_suresi_dk)", "toplam_calisma_dakika"
        elif ("uretim" in q or "miktar" in q) and "uretim_kg" in cols:
            measure, alias = "SUM(uretim_kg)", "toplam_uretim_kg"
        elif "fire" in q and "hatali_kg" in cols:
            measure, alias = "SUM(hatali_kg)", "toplam_fire_kg"
        elif "kalite" in q and "kalite_KS" in cols:
            measure, alias = "AVG(kalite_KS)", "ort_kalite"
        else:
            measure, alias = "AVG(OEE)", "ort_oee"

        # İki boyutlu matris: vardiya × gün → heatmap. "vardiya" + gün/hafta/tarih.
        if "vardiya" in q and (re.search(r"\bgun(luk|ler|lere|u)?\b", q) or "hafta" in q or "tarih" in q):
            # Zaman penceresi (opsiyonel): "geçen hafta", "son N gün/ay/hafta".
            win = ""
            mwin = re.search(r"son\s+(\d+)\s*(gun|ay|hafta)", q)
            if "gecen hafta" in q:
                win = " WHERE tarih >= CURRENT_DATE - INTERVAL '7 days'"
            elif mwin:
                unit = {"gun": "days", "ay": "months", "hafta": "weeks"}[mwin.group(2)]
                win = f" WHERE tarih >= CURRENT_DATE - INTERVAL '{int(mwin.group(1))} {unit}'"

            # "haftanın günü" → Pzt..Paz matrisi (tekrarlayan desen); değilse gün bazlı.
            if "haftanin" in q or "gunu" in q or "gun adi" in q:
                gun_expr = (
                    "CASE isodow(tarih) WHEN 1 THEN 'Pzt' WHEN 2 THEN 'Sal' WHEN 3 THEN 'Çar' "
                    "WHEN 4 THEN 'Per' WHEN 5 THEN 'Cum' WHEN 6 THEN 'Cmt' ELSE 'Paz' END"
                )
                return (
                    f"SELECT vardiya, {gun_expr} AS gun, {measure} AS {alias} "
                    f"FROM oee_vardiya{win} GROUP BY vardiya, gun, isodow(tarih) "
                    "ORDER BY isodow(tarih), vardiya"
                )
            # Gün-adı değilse: pencere belirtilmemişse VARSAYILAN son 7 gün (anlık görüntü).
            if not win:
                win = " WHERE tarih >= CURRENT_DATE - INTERVAL '7 days'"
            return (
                f"SELECT vardiya, CAST(tarih AS DATE) AS gun, {measure} AS {alias} "
                f"FROM oee_vardiya{win} GROUP BY vardiya, gun ORDER BY gun, vardiya"
            )

        dim = None
        if "makin" in q:  # makine/makina/makinesi/makineler
            dim = "makine"
        elif "vardiya" in q or "varidya" in q:
            dim = "vardiya"

        where = ""
        # vardiya artık TAM SAYI (1/2/3), eski şemadaki gibi metin adı DEĞİL — bkz.
        # cube katmanındaki CASE eşlemesi (1=Gündüz/08-16, 2=Akşam/16-24, 3=Gece/00-08).
        for token, val in (("gunduz", 1), ("aksam", 2), ("gece", 3)):
            if token in q:
                where = f" WHERE vardiya = {val}"
                break

        has_top, direction = self._direction(q)
        select_dim = f"{dim}, " if dim else ""
        group = f" GROUP BY {dim}" if dim else ""
        order = f" ORDER BY {alias} {direction}" if dim else ""
        limit = self._limit(q, has_top, dim is not None)
        return f"SELECT {select_dim}{measure} AS {alias} FROM oee_vardiya{where}{group}{order}{limit}"

    # -- partiler / boya süreç -------------------------------------------
    def _partiler_sql(self, q: str, raw: str, model: dict) -> str:
        cols = {c["name"] for c in model["columns"]}

        def has(word: str) -> bool:
            return re.search(rf"\b{word}\b", q) is not None

        if "fire" in q and "oran" in q and {"fire_kg", "agirlik_kg"} <= cols:
            measure, alias = "ROUND(SUM(fire_kg)*100.0/NULLIF(SUM(agirlik_kg),0),2)", "fire_orani_yuzde"
        elif "fire" in q and "fire_kg" in cols:
            measure, alias = "SUM(fire_kg)", "toplam_fire_kg"
        elif (has("su") or "su tuket" in q) and "su_tuketim_lt" in cols:
            measure, alias = "SUM(su_tuketim_lt)", "toplam_su_lt"
        elif "enerji" in q and "enerji_kwh" in cols:
            measure, alias = "SUM(enerji_kwh)", "toplam_enerji_kwh"
        elif ("maliyet" in q or "kimyasal" in q) and "kimyasal_maliyet" in cols:
            measure, alias = "SUM(kimyasal_maliyet)", "toplam_maliyet"
        elif ("sapma" in q or "kalite" in q or "delta" in q) and "renk_sapmasi" in cols:
            measure, alias = "AVG(renk_sapmasi)", "ort_renk_sapmasi"
        elif ("karli" in q or "kazanc" in q or has("kar")) and {"tutar", "kimyasal_maliyet"} <= cols:
            # kâr ≈ ciro − kimyasal maliyet (brüt marj yaklaşığı)
            measure, alias = "SUM(tutar - kimyasal_maliyet)", "kar"
        elif ("ciro" in q or "gelir" in q or "tutar" in q) and "tutar" in cols:
            measure, alias = "SUM(tutar)", "toplam_ciro"
        elif (any(w in q for w in ["kilo", "agirli", "islenen", "tonaj"]) or has("kg")) and "agirlik_kg" in cols:
            measure, alias = "SUM(agirlik_kg)", "toplam_kg"
        else:
            # 🔴 **KOŞULSUZ SAYMA DALI KAPATILDI** (2026-08-06, canlı ölçüm).
            #
            # Ölçülen kusur — bu sınıfın KENDİ belgesinin ihlali (*"sessiz yanlış üretmek
            # yerine ... dürüstçe reddeder"*):
            #
            #     zombixyz ne kadar          →  SELECT COUNT(*) FROM partiler  →  37 878
            #     flarnak bizde kac          →  aynı SQL, AYNI SAYI
            #     qwertyuiop ne durumda      →  aynı SQL, AYNI SAYI
            #     zombixyz ve flarnak kiyasla→  aynı SQL, AYNI SAYI
            #
            # Dördü de `source=rule` rozetiyle, **notsuz**, tek bir sayı olarak döndü.
            # Bu, deponun adını koyduğu en kötü hata sınıfıdır: *anlaşılmamış bir soruya
            # kendinden emin bir sayı.* ADR-0008'in birinci yasağı tam olarak budur.
            #
            # ⚠ Ve `route()` bunu ZATEN BİLİYORDU: `partial_unknowns` `['zombixyz']`
            # döndürüyor, kapsam kapısı kelimeyi tanımıyor. Bilgi vardı; bu dala
            # ulaşmıyordu. *Merdivenin alt basamağı, üst basamağın bildiğini bilmiyordu.*
            #
            # Kural: sayma dalı yalnız soruda **tanınan bir dayanak** varken meşrudur —
            # ya açık bir sayma niyeti (`kaç`/`sayısı`/`adet`) ya bir kolon/varlık adı.
            # Hiçbiri yoksa **dürüst ret**; üst basamaklar (Discovery) yine denenebilir.
            # ⚠ LİSTE/DÖKÜM NİYETİ İSTİSNA — ve bu, kapının kendi ölçümüyle bulundu:
            # ilk yazımda bu dal koşulsuz `raise` ediyordu ve **satır dökümü yolu da
            # onun arkasındaydı** (`alias == "parti_sayisi"` şartıyla aşağıda). Yani
            # *"partileri listele"* gibi HİÇBİR SAYI UYDURMAYAN meşru bir istek de
            # kesildi ve iki kapı (`test_ask_async_discovery` ·
            # `test_discovery_execution_failure`) kırmızıya döndü.
            # 🔴 Ayrım net: uydurma riski **tek bir sayı** vermekte; satır dökümü
            # veriyi olduğu gibi gösterir ve kullanıcı ne aldığını görür.
            # *Bir kapıyı kapatırken, arkasından geçen başka bir yolu da kapatmamak
            # gerekir — ve bunu ancak koşarak öğrenirsin.*
            if not (_liste_niyeti(q) or _sayma_dayanagi(q, cols)):
                raise ValueError(
                    "Kural-tabanlı jeneratör soruda tanıdığı bir ölçü/varlık bulamadı — "
                    "sayı uydurmak yerine dürüstçe reddediyor."
                )
            measure, alias = "COUNT(*)", "parti_sayisi"

        if "ortalama" in q and measure.startswith("SUM(") and measure[4:-1].isidentifier():
            inner = measure[4:-1]
            measure, alias = f"AVG({inner})", f"ort_{inner}"

        dim = None
        if "makin" in q and "makine" in cols:  # makine/makina/makinesi
            dim = "makine"
        elif ("kumas" in q or "kumaş" in raw.lower()) and "kumas_cinsi" in cols:
            dim = "kumas_cinsi"
        elif "musteri" in q and "musteri" in cols:
            dim = "musteri"
        elif (
            any(w in q for w in ["asama", "boyama", "yikama", "apre", "kurutma"])
            and "asama" in cols
        ):
            dim = "asama"
        elif "durum" in q and "durum" in cols:
            dim = "durum"
        elif "renk" in q and "sapma" not in q and "renk" in cols:
            dim = "renk"
        elif "renk" in q and any(w in q for w in ["bazinda", "gore", "her"]) and "renk" in cols:
            dim = "renk"

        conds: list[str] = []
        if "durum" in cols:
            if "reddedil" in q or has("red"):
                conds.append("durum = 'red'")
            elif "tamamlan" in q:
                conds.append("durum = 'tamamlandi'")
            elif "tekrar" in q:
                conds.append("durum = 'tekrar'")
            elif "islemde" in q or "devam" in q or "suren" in q:
                conds.append("durum = 'islemde'")

        # Kategorik değer filtreleri: soruda geçen müşteri/renk/kumaş/... adı → WHERE.
        filtered: set[str] = set()
        for c in model["columns"]:
            vals = c.get("values")
            if not vals or c["name"] == "durum":
                continue
            for v in vals:
                nv = _norm(str(v))
                if nv and nv in q:
                    conds.append(f"{c['name']} = '{str(v).replace(chr(39), chr(39) * 2)}'")
                    filtered.add(c["name"])
                    break

        # Belirli bir değer eşleştiyse o kolonu BOYUT değil FİLTRE olarak kullan
        # (ör. "süprem kumaşın su tüketimi" → WHERE kumas_cinsi='Süprem', GROUP BY yok).
        if dim in filtered:
            dim = None

        where = (" WHERE " + " AND ".join(conds)) if conds else ""

        # "Listele / liste / göster" → toplulaştırma değil, satır DÖKÜMÜ.
        # Yalnızca ölçü de boyut da istenmediğinde (yoksa COUNT(*)'a düşecekti).
        list_intent = any(
            w in q for w in ["listele", "liste", "goster", "hangileri", "hangi", "detay", "dokum"]
        )
        count_intent = "kac" in q or "sayisi" in q or "adet" in q
        if alias == "parti_sayisi" and dim is None and list_intent and not count_intent:
            prefer = [
                "parti_no", "musteri", "kumas_cinsi", "renk", "makine", "asama",
                "agirlik_kg", "fire_kg", "renk_sapmasi", "durum", "tarih",
            ]
            sel = [c for c in prefer if c in cols] or ["*"]
            order_by = " ORDER BY tarih DESC" if "tarih" in cols else ""
            return f"SELECT {', '.join(sel)} FROM partiler{where}{order_by}"

        has_top, direction = self._direction(q)

        # Zaman birimi (aylık/haftalık/günlük) — varsa boyutla birleşir.
        time_unit = None
        if "tarih" in cols:
            if any(w in q for w in ["haftalik", "haftalar", "haftaya", "hafta bazinda"]):
                time_unit = "week"
            elif any(w in q for w in ["gunluk", "gunler", "gunlere", "gune gore", "gun bazinda"]):
                time_unit = "day"
            elif any(w in q for w in ["aylik", "aylar", "aya gore", "ay bazinda", "trend", "zaman"]):
                time_unit = "month"
        if time_unit:
            sel = [f"date_trunc('{time_unit}', tarih) AS donem"]
            grp = ["donem"]
            order_by = "donem"
            if dim:
                sel.append(dim)
                grp.append(dim)
                order_by = f"donem, {alias} {direction}"
            sel.append(f"{measure} AS {alias}")
            return (
                f"SELECT {', '.join(sel)} FROM partiler{where} "
                f"GROUP BY {', '.join(grp)} ORDER BY {order_by}"
            )

        select_dim = f"{dim}, " if dim else ""
        group = f" GROUP BY {dim}" if dim else ""
        order = f" ORDER BY {alias} {direction}" if dim else ""
        limit = self._limit(q, has_top, dim is not None)
        return f"SELECT {select_dim}{measure} AS {alias} FROM partiler{where}{group}{order}{limit}"


# --- fabrika ----------------------------------------------------------------


def _reachable(base_url: str) -> bool:
    try:
        import requests

        requests.get(base_url.rstrip("/") + "/models", timeout=0.6)
        return True
    except Exception:
        return False


class FailoverSqlGenerator:
    """LLM sağlayıcılarını sırayla dener; biri hata verirse (429/ağ/timeout) sonrakine
    geçer. Böylece bir sağlayıcının kotası dolsa da LLM kalitesi korunur."""

    def __init__(self, generators: list):
        self._gens = list(generators)
        self._last = None  # son başarılı sağlayıcı (repair önce onu dener)

    def _dususu_kaydet(self, gen, sira: int) -> None:
        """FAZ 1.11 — bir SEVİYE düşüşünü `AuditLog`'a yazar.

        ⚠ Sağlayıcı geçişi değil **seviye** değişimi kaydedilir: gemini→groq kullanıcı
        için bir olay DEĞİLDİR (ikisi de seviye 2) ve her denemeyi audit'e yazmak kaydı
        **gürültüye** boğardı — gürültüyle dolan bir kanıt defteri okunmaz olur.

        🔴 Audit yazımı başarısız olursa **cevap düşürülmez**: kademeli düşüş bir
        DAYANIKLILIK mekanizmasıdır; onu kayıt yüzünden kırmak, amacının tam tersi olurdu.
        """
        try:
            from app.kademeli_dusus import dusus_kaydi

            # Taban her zaman seviye 1: "normal" durum birincil LLM'dir. Önceki
            # ÜRETİCİYİ geçmek, "önceki her zaman listenin başıdır" gizli varsayımını
            # taşırdı (bkz. `dusus_kaydi` belgesi).
            olay = dusus_kaydi(gen, yeni_sira=sira, onceki_seviye=1)
            if not olay:
                return
            from control_plane import audit

            audit.record(None, "llm_kademeli_dusus", generated_sql=olay["ozet"])
        except Exception:  # noqa: BLE001 — kayıt, dayanıklılığı KIRAMAZ
            _log.warning("kademeli düşüş audit'e yazılamadı", exc_info=True)

    def generate_sql(self, question: str, schema: dict) -> str:
        errs = []
        for sira, g in enumerate(self._gens):
            try:
                sql = g.generate_sql(question, schema)
                if sira:
                    self._dususu_kaydet(g, sira)
                self._last = g
                return sql
            except Exception as e:
                errs.append(f"{getattr(g, '_provider', type(g).__name__)}: {e}")
        # Alt-seviye logs (_ask/_chat) her TEK denemeyi zaten logladı; burası tüm
        # zincirin TÜKENDİĞİNİ tek bakışta gösteren ÖZET (ERROR seviyesi — "llm mi
        # patladı" sorusuna kesin cevap).
        _log.error("FailoverSqlGenerator.generate_sql: TÜM sağlayıcılar başarısız: %s", " | ".join(errs))
        raise RuntimeError("Tüm LLM sağlayıcıları başarısız: " + " | ".join(errs))

    def generate_followup_sql(self, question: str, schema: dict, prev_question: str,
                              prev_sql: str, history: list[str]) -> str:
        errs = []
        for g in self._gens:
            try:
                fn = getattr(g, "generate_followup_sql", None)
                sql = (fn(question, schema, prev_question, prev_sql, history) if fn
                      else g.generate_sql(question, schema))
                self._last = g
                return sql
            except Exception as e:
                errs.append(f"{getattr(g, '_provider', type(g).__name__)}: {e}")
        _log.error("FailoverSqlGenerator.generate_followup_sql: TÜM sağlayıcılar başarısız: %s", " | ".join(errs))
        raise RuntimeError("Tüm LLM sağlayıcıları başarısız (followup): " + " | ".join(errs))

    def repair(self, question: str, schema: dict, bad_sql: str, error: str) -> str:
        order = ([self._last] if self._last else []) + [g for g in self._gens if g is not self._last]
        for g in order:
            if not hasattr(g, "repair"):
                continue
            try:
                return g.repair(question, schema, bad_sql, error)
            except Exception:
                continue
        _log.error("FailoverSqlGenerator.repair: TÜM sağlayıcılar başarısız")
        raise RuntimeError("repair: tüm sağlayıcılar başarısız")

    def sinonim_oner(self, teknik_ad: str, baglam: str = "") -> str:
        for g in self._gens:
            if not hasattr(g, "sinonim_oner"):
                continue
            try:
                out = g.sinonim_oner(teknik_ad, baglam)
                self._last = g
                return out
            except Exception:
                continue
        raise RuntimeError("sinonim_oner: tüm sağlayıcılar başarısız")

    def plan_sec(self, soru: str, araclar_json: str, ipucu: str = "") -> str:
        for g in self._gens:
            if not hasattr(g, "plan_sec"):
                continue
            try:
                out = g.plan_sec(soru, araclar_json, ipucu)
                self._last = g
                return out
            except Exception:
                continue
        raise RuntimeError("plan_sec: tüm sağlayıcılar başarısız")

    def prompt_enhance(self, soru: str, catalog: str) -> str:
        for g in self._gens:
            if not hasattr(g, "prompt_enhance"):
                continue          # kural-tabanlı sağlayıcıda YOK — yol kapalı, hata değil
            try:
                out = g.prompt_enhance(soru, catalog)
                self._last = g
                return out
            except Exception:
                continue
        raise RuntimeError("prompt_enhance: tüm sağlayıcılar başarısız")

    def anlat(self, soru: str, gercekler: list[str]) -> str:
        for g in self._gens:
            if not hasattr(g, "anlat"):
                continue          # kural-tabanlı sağlayıcıda YOK — yol kapalı, hata değil
            try:
                out = g.anlat(soru, gercekler)
                self._last = g
                return out
            except Exception:
                continue
        raise RuntimeError("anlat: tüm sağlayıcılar başarısız")

    def select_cube(self, question: str, catalog: str, sema: dict | None = None) -> str:
        for g in self._gens:
            if not hasattr(g, "select_cube"):
                continue
            try:
                # FAZ 3a: şemayı KABUL EDEN sağlayıcıya geçir; etmeyene (eski/üçüncü-parti
                # üreteç) bugünkü iki-argümanlı çağrıyla git — ikisi de aynı sözleşmeye
                # (JSON metni) varır, yani karışım güvenlidir.
                try:
                    out = g.select_cube(question, catalog, sema)
                except TypeError:
                    out = g.select_cube(question, catalog)
                self._last = g
                return out
            except Exception:
                continue
        _log.error("FailoverSqlGenerator.select_cube: TÜM sağlayıcılar başarısız")
        raise RuntimeError("select_cube: tüm sağlayıcılar başarısız")

    def refine_cube(self, prev_cq_json: str, message: str, catalog: str) -> str:
        for g in self._gens:
            if not hasattr(g, "refine_cube"):
                continue
            try:
                out = g.refine_cube(prev_cq_json, message, catalog)
                self._last = g
                return out
            except Exception:
                continue
        _log.error("FailoverSqlGenerator.refine_cube: TÜM sağlayıcılar başarısız")
        raise RuntimeError("refine_cube: tüm sağlayıcılar başarısız")


def _make(provider: str, settings, dialect: str):
    """Tek bir sağlayıcı için üretici döndürür (anahtar/erişim yoksa None)."""
    if provider == "anthropic" and settings.anthropic_api_key:
        return AnthropicSqlGenerator(settings.anthropic_api_key, settings.llm_model, dialect,
                                     select_model=settings.anthropic_select_model)
    if provider == "xai" and settings.xai_api_key:
        return OpenAICompatibleSqlGenerator(
            settings.xai_base_url, settings.xai_api_key, settings.xai_model, "xai", dialect,
            select_model=settings.xai_select_model,
        )
    if provider == "gemini" and settings.gemini_api_key:
        return OpenAICompatibleSqlGenerator(
            settings.gemini_base_url, settings.gemini_api_key, settings.gemini_model, "gemini", dialect,
            select_model=settings.gemini_select_model,
        )
    if provider == "groq" and settings.groq_api_key:
        return OpenAICompatibleSqlGenerator(
            settings.groq_base_url, settings.groq_api_key, settings.groq_model, "groq", dialect,
            select_model=settings.groq_select_model,
        )
    if provider == "openrouter" and settings.openrouter_api_key:
        return OpenAICompatibleSqlGenerator(
            settings.openrouter_base_url,
            # Zincir varsa o, yoksa tek anahtar — varsayılan davranış birebir bugünkü.
            settings.openrouter_api_keys or settings.openrouter_api_key,
            settings.openrouter_model, "openrouter", dialect,
            select_model=settings.openrouter_select_model,
        )
    if provider == "ollama" and _reachable(settings.ollama_base_url):
        return OpenAICompatibleSqlGenerator(
            settings.ollama_base_url, "", settings.ollama_model, "ollama", dialect,
            select_model=settings.ollama_select_model,
        )
    return None


class NoLlmGenerator:
    """A#5: rule_fallback KAPALI + hiç sağlayıcı yok → tahmin YOK. generate_sql hata
    fırlatır; routers/ask.py bunu dürüst redde çevirir (sessiz-yanlış SQL yerine)."""

    def generate_sql(self, question: str, schema: dict) -> str:  # noqa: ARG002
        raise RuntimeError("LLM sağlayıcısı yok ve kural yedeği kapalı (DIMA_RULE_FALLBACK)")

    def generate_followup_sql(self, question: str, schema: dict, prev_question: str,  # noqa: ARG002
                              prev_sql: str, history: list[str]) -> str:  # noqa: ARG002
        raise RuntimeError("LLM sağlayıcısı yok ve kural yedeği kapalı (DIMA_RULE_FALLBACK)")


def build_generator(settings) -> SqlGenerator:
    """Sağlayıcı seçimi.

    auto: mevcut TÜM LLM sağlayıcılarını öncelik sırasıyla zincirler (failover) —
    çalışan ücretsizler (gemini, groq) önce, sonra xai/ollama; hepsi başarısızsa
    istek anında kural-tabanlıya düşülür (bkz. routers/ask.py — rule_fallback açıksa).
    Hiç sağlayıcı yoksa: demo'da kural-tabanlı, üretimde (rule_fallback=False) dürüst
    ret üreticisi. Açık değerler: anthropic | xai | gemini | groq | openrouter | ollama | rule.
    """
    p = (settings.llm_provider or "auto").lower()
    dialect = getattr(settings, "datasource", "") or ""
    # A#5: örtük kural-tabanlı düşüş yalnız demo'da; açık `rule` seçimi (testler) hariç.
    fallback = (
        RuleBasedSqlGenerator()
        if getattr(settings, "rule_fallback", True)
        else NoLlmGenerator()
    )

    if p == "rule":
        return RuleBasedSqlGenerator()
    if p != "auto":
        return _make(p, settings, dialect) or fallback
    # auto: çalışan ücretsizler (gemini, groq) önce; xai kredi bekliyor → sonra.
    # `openrouter` xai'den SONRA: ölçüm turları için eklendi (Gemini ücretsiz katmanı
    # 429'a çarpıyor), ama üretimin varsayılan sağlayıcısını DEĞİŞTİRMEMELİ.
    order = ["anthropic", "gemini", "groq", "xai", "openrouter", "ollama"]
    gens = [g for g in (_make(name, settings, dialect) for name in order) if g]
    if not gens:
        return fallback
    return gens[0] if len(gens) == 1 else FailoverSqlGenerator(gens)
