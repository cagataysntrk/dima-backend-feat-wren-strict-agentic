"""PII maskeleme (Faz 4.14, 1 Ağustos 2026 — dış yol haritası 2.19). KVKK'ya doğrudan
bağlı: TCKN/e-posta/telefon/IBAN çıktıya (tablo hücreleri + deterministik yorum metni)
ULAŞMADAN HEMEN ÖNCE regex-tabanlı taranır ve maskelenir — `/ask`, `/cube`, `/query`'nin
HER BİRİNİN kendi tek çıkış noktasında (Plane Enforcer'ın — 4.6, ertelendi — aynı "tek
çıkış" ilkesi, burada YALNIZ PII'ye uygulanır).

Kanıt: `demo/companies/*/…`'daki GERÇEK şemada `personel_ozluk.tc_kimlik` zaten var —
bugün hiçbir cube bunu SEÇMİYOR (Faz 2 öncesi `parti_zengin` view'ı bilerek dışarıda
bırakıyordu; view'lar silindikten sonra aynı işi `relationships.yml`'in `expose:` blokları
görüyor — `personel_ozluk`tan yalnız demografi kolonları yayımlanıyor) ama
`/query` (ham SQL, `sql:run` yetkisi) VE Discovery (gerçek bir LLM sağlayıcıyla, ham SQL
üretimi ANY kolonu seçebilir) bu sütuna DOĞRUDAN erişebilir — bu modül olmadan maskesiz
döner. Rol-duyarlı istisna: `pii:view` yetkisi olan (admin+) rol maskesiz görür (bkz.
control_plane/authorize.py, app/routers/ask.py — bu erişim audit'e düşer)."""

from __future__ import annotations

import re

from app.logging_setup import get_logger

_log = get_logger("pii")

# TCKN: 11 hane, ilk hane 0 olamaz — checksum algoritması ile GERÇEK bir TCKN'i rastgele
# 11 haneli bir sayıdan (ör. sipariş no) ayırt eder (false-positive'i büyük ölçüde önler).
_TCKN_RE = re.compile(r"\b[1-9]\d{10}\b")
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
# TR telefon: opsiyonel +90/0 + 10 hane (05XX XXX XX XX gibi ayraçlı/ayraçsız).
_PHONE_RE = re.compile(r"\b(?:\+90|0)?[\s.-]?5\d{2}[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}\b")
_IBAN_RE = re.compile(r"\bTR\d{2}[\s]?(?:\d[\s]?){22}\b", re.IGNORECASE)


def _tckn_checksum_valid(digits: str) -> bool:
    """Resmi TCKN algoritması (Nüfus ve Vatandaşlık İşleri): d10/d11 kontrol haneleri."""
    d = [int(c) for c in digits]
    if len(d) != 11 or d[0] == 0:
        return False
    d10 = ((sum(d[0:9:2]) * 7) - sum(d[1:8:2])) % 10
    if d10 != d[9]:
        return False
    d11 = sum(d[:10]) % 10
    return d11 == d[10]


def _mask_middle(s: str, keep_start: int, keep_end: int, ch: str = "*") -> str:
    if len(s) <= keep_start + keep_end:
        return ch * len(s)
    return s[:keep_start] + ch * (len(s) - keep_start - keep_end) + s[-keep_end:]


def mask_tckn(text: str) -> str:
    def _repl(m: re.Match) -> str:
        val = m.group(0)
        return _mask_middle(val, 3, 2) if _tckn_checksum_valid(val) else val
    return _TCKN_RE.sub(_repl, text)


def mask_email(text: str) -> str:
    def _repl(m: re.Match) -> str:
        local, _, domain = m.group(0).partition("@")
        masked_local = local[0] + "*" * max(1, len(local) - 1)
        return f"{masked_local}@{domain}"
    return _EMAIL_RE.sub(_repl, text)


def mask_phone(text: str) -> str:
    def _repl(m: re.Match) -> str:
        digits = re.sub(r"\D", "", m.group(0))
        return _mask_middle(digits, 3, 2)
    return _PHONE_RE.sub(_repl, text)


def mask_iban(text: str) -> str:
    def _repl(m: re.Match) -> str:
        compact = re.sub(r"\s", "", m.group(0)).upper()
        return _mask_middle(compact, 4, 4)
    return _IBAN_RE.sub(_repl, text)


def mask_text(value: str) -> str:
    """Tek bir metin değerine TÜM PII filtrelerini sırayla uygular."""
    return mask_iban(mask_phone(mask_email(mask_tckn(value))))


def _mask_scalar(v):
    if isinstance(v, str):
        return mask_text(v)
    return v


def mask_query_result(result: dict, principal=None) -> tuple[dict, bool]:
    """`/query`'nin maskeleme deseninin PAYLAŞILAN hâli — `result` (columns/rows/row_count
    sözlüğü) alır, (yeni_result, unmasked_pii_shown) döner. Doğrulama turunda (1 Ağustos
    2026) bulunan gerçek boşluk: Faz 4.14 yalnız `/ask`/`/cube`/`/query`'yi kapsıyordu —
    `app/report.py`, `app/routers/dashboards.py::dashboard_data`, `app/schedules.py::
    run_schedule` de `svc.query(...)` çağırıyor ama HİÇBİRİ maskelemiyordu (üçü de aynı
    ham satırları ya panoya, ya rapora, ya da BİR E-POSTAYA taşıyordu). Bu fonksiyon o
    dört çağrı yerinin (bu üçü + `/query`) TEK ortak uygulamasıdır — tekrarı önler.

    `principal=None` (ör. zamanlanmış rapor TESLİMİ gibi canlı bir kullanıcı OLMAYAN,
    otomatik/arka-plan bağlamlar) HER ZAMAN maskeler — bypass edecek bir yetkili
    GÖRÜNTÜLEYİCİ o anda YOK (e-postanın kime gideceği önceden bilinemez), bu yüzden
    fail-closed varsayılan uygulanır. Bu fonksiyon `audit.record` ÇAĞIRMAZ — hangi ek
    alanların (session_id, generated_sql, dashboard/schedule id vb.) loglanacağı çağırana
    göre değiştiği için audit satırını ÇAĞIRAN kendi bağlamıyla yazar."""
    if not result.get("rows"):
        return result, False
    from control_plane.authorize import can

    has_pii_view = principal is not None and can(principal, "pii:view")
    masked_rows, found = mask_rows(result["rows"])
    if not found:
        return result, False
    if has_pii_view:
        return result, True
    return {**result, "rows": masked_rows}, False


#: 🔴 **MASKELENMEYECEK ALANLAR — ve her biri GEREKÇELİ.**
#:
#: `KAT-5`'in kuralı: *"SAYMA — KAPAT."* Maskelenecek alanları saymak, yeni bir alan
#: eklendiğinde onu **sessizce dışarıda** bırakır; bu depoda o desen defalarca ölçüldü
#: (`ReportPanel`'in `SAF_NOT_ALANLARI` tümleyeni aynı sebeple yazıldı). Varsayılan
#: **maskelemektir**; muaf tutmak **açık bir karar** ister ve karar burada durur.
#:
#: ⚠ Ölçüldü (2026-08-04): `apply_to_ask_response` yalnız `result.rows` · `facts[].text` ·
#: `summary` maskeliyordu. `AskResponse`'un o gün **29**, bugün **31** alanı var (FAZ 1.12
#: `ai_generated_prose` + `kanit_sinifi`, FAZ 2.6 `mali_donem`, FAZ 2.5 `hedef`
#: ekledi) — ve bu **tümleyenin işe yaradığının kanıtıdır**: DÖRT yeni alan için hiçbir şey
#: yazılmadı, yine de kapsandılar. Kapı her seferinde bayat notu yakaladı.
#: Sayılan bir liste olsaydı ikisi de sessizce dışarıda kalırdı. Geri kalanı — `narration`
#: (LLM metni, olgulardan üretilir) · `contribution` (**cevabın gövdesi**, bkz. `0.23`) ·
#: `next_steps` · `suggestions` · `prescription` — **hiç maskelenmiyordu**.
MUAF_ALANLAR: dict[str, str] = {
    "result": "AYRI ele alınıyor (`mask_rows`) — derin gezinti onu ikinci kez tarayıp "
              "büyük sonuçlarda gereksiz maliyet üretirdi",
    "sql": "SQL maskelemek onu ÇALIŞTIRILAMAZ kılar ve makbuzun yeniden üretilebilirliğini "
           "bozar; erişim zaten `sql:run` (analyst+) ile sınırlı",
    "planned_sql": "aynı gerekçe — motorun ürettiği plan, maskelenirse kanıt olmaktan çıkar",
    "cube_query": "YAPISAL alan; `POST /cube` onu birebir yeniden koşar. Maskelemek "
                  "checkpoint'i (D4) kırardı — bir kanıt, değiştirilirse kanıt değildir",
    "question": "kullanıcının KENDİ yazdığı metin; kendisine geri gösterilmesi bir sızıntı "
                "değildir (bilgi zaten onda) ve maskelemek soruyu tanınmaz kılardı",
    "thread_id": "kimlik", "contract_id": "kimlik", "job_id": "kimlik",
    "source": "sabit küme (enum)", "view_hint": "sabit küme (enum)",
    "is_new_topic": "bool", "reply_to_label": "istemcinin kendi etiketi",
    "viz": "yalnız KOLON ADLARI ve yapı taşır — ölçüldü, veri değeri içermez",
}


def muhurle_derin(deger, _derinlik: int = 0):
    """Yuvalanmış yapıdaki **tüm** metinleri maskeler. Saf fonksiyon.

    Sözlük/liste/metin dışındaki her şey (sayı, bool, None) **dokunulmadan** döner —
    `mask_rows`'un aynı kararı: bir ölçü değerini maskelemek veriyi bozar.

    ⚠ Derinlik sınırı **yok** ve bu bilinçli: sınır koymak, sınırın ötesindeki bir alanı
    **sessizce** muaf tutardı. Yanıt gövdeleri sonlu ve küçüktür (satırlar hariç, onlar
    muaf).

    🔴 **PYDANTİC MODELLERİ DE GEZİLİR.** `suggestions` bir `list[Suggestion]`'dır —
    sözlük değil. Yalnız `str`/`dict`/`list` gezen bir maskeleyici onu **sessizce**
    atlardı ve chip etiketleri maskesiz kalırdı. Model **yerinde** güncellenir; yeniden
    kurmak, doğrulama kurallarına takılıp isteği düşürebilirdi.
    """
    if isinstance(deger, str):
        return mask_text(deger)
    if isinstance(deger, dict):
        return {k: muhurle_derin(v, _derinlik + 1) for k, v in deger.items()}
    if isinstance(deger, (list, tuple)):
        tur = type(deger)
        return tur(muhurle_derin(v, _derinlik + 1) for v in deger)
    alanlar = getattr(type(deger), "model_fields", None)
    if alanlar:                                   # pydantic modeli — YERİNDE güncelle
        for ad in alanlar:
            ic = getattr(deger, ad, None)
            if ic is None or isinstance(ic, (int, float, bool)):
                continue
            yeni_ic = muhurle_derin(ic, _derinlik + 1)
            if yeni_ic != ic:
                try:
                    setattr(deger, ad, yeni_ic)
                except Exception:                 # noqa: BLE001
                    _log.warning("PII: iç alan maskelenemedi: %s.%s",
                                 type(deger).__name__, ad)
        return deger
    return deger


def apply_to_ask_response(resp, principal) -> bool:
    """`resp`'i YERİNDE (in-place) maskeler — `result.rows` + `interpretation` metni.
    `pii:view` yetkisi olan principal (admin+, control_plane/authorize.py) İÇİN dokunulmaz.
    `_persist_message`/`_log_interaction`'dan ÖNCE çağrılmalı (aksi halde ham PII kalıcı
    sohbet geçmişine de düşer). Döner: PII bulunup principal'a MASKESİZ gösterildi mi
    (çağıran bunu `audit.record`'a "pii_view" olarak düşürür — KVKK erişim izi)."""
    from control_plane.authorize import can

    has_pii_view = principal is not None and can(principal, "pii:view")
    unmasked_pii_shown = False
    if resp.result is not None and resp.result.rows:
        masked_rows, found = mask_rows(resp.result.rows)
        if found:
            if has_pii_view:
                unmasked_pii_shown = True
            else:
                resp.result.rows = masked_rows
    # ⟳ **FAZ 1.2c — SAYMA, KAPAT.** Eskiden burada yalnız `facts[].text` ve `summary`
    # maskeleniyordu; `AskResponse`'un (o gün 29, bugün 37) alanının geri kalanı — `narration` (LLM metni,
    # olgulardan üretilir) · `contribution` (**cevabın gövdesi**) · `next_steps` ·
    # `suggestions` · `prescription` — **hiç** maskelenmiyordu. Sayılan bir liste, yeni
    # alanı sessizce dışarıda bırakır; tümleyen bırakmaz.
    if not has_pii_view:
        for alan in type(resp).model_fields:
            if alan in MUAF_ALANLAR:
                continue
            eski = getattr(resp, alan, None)
            if eski is None or isinstance(eski, (int, float, bool)):
                continue
            yeni = muhurle_derin(eski)
            if yeni != eski:
                try:
                    setattr(resp, alan, yeni)
                except Exception:  # noqa: BLE001 — pydantic doğrulaması reddederse
                    # Sessizce geçme: maskelenemeyen bir alan bir BULGUDUR. Ama isteği de
                    # düşürme — maskelenmemiş hâli zaten bugünkü davranış.
                    _log.warning("PII: `%s` alanı maskelenemedi (tip kısıtı)", alan)
    return unmasked_pii_shown


def mask_rows(rows: list[dict]) -> tuple[list[dict], bool]:
    """Tablo satırlarını (sonuç hücreleri) maskeler. Döner: (maskelenmiş satırlar, en az
    bir PII bulundu mu). Sayısal/bool/None değerlere DOKUNULMAZ (yalnız string hücreler
    taranır — TCKN gibi metin-olarak-saklanan sayısal görünümlü değerler DAHİL, ama
    gerçek ölçü/miktar sütunları etkilenmez)."""
    found = False
    out: list[dict] = []
    for row in rows:
        new_row = {}
        for k, v in row.items():
            masked = _mask_scalar(v)
            if masked != v:
                found = True
            new_row[k] = masked
        out.append(new_row)
    return out, found


def muhurle(resp, request, principal, *, ad: str) -> None:
    """`/ask` DIŞINDAKİ veri döndüren uçlar için gizlilik + iz mührü — YERİNDE uygular.

    ## Neden ayrı bir fonksiyon

    `answer.py::seal()` `AskResponse`'a özeldir (chip · aksiyon · köken · yorum zinciri
    ona bağlı). Ama `seal`'in **üç garantisi** cevabın TÜRÜNE değil, **veri döndürüyor
    olmasına** bağlıdır: PII maskesi · erişim audit'i · etkileşim logu.

    ## Ne kapatıyor — DENETİMDE ÖLÇÜLDÜ (Faz 9.1)

    `answer.py`'nin modül değişmezi *"**her** yanıt buradan geçer"* diyordu; iki uçta
    **geçerli değildi**:

    | uç | dönüş noktası | audit | PII maskesi |
    |---|---|---|---|
    | `POST /ask/drill` | **8** | yalnız `raw` dalında | **hiçbirinde** |
    | `POST /ask/contribution` | 2 | yok | yok |

    Ve taşıdıkları veri hassas: `DrillResponse.result` **satır**, `.anomalies` ve
    `ContributionResponse.raporlar` **boyut değerleri** — bu katalogda `musteri` ·
    `operator` · `calisan` gerçek boyutlardır. Yani `/ask` maskeliyor, bu iki uç
    **maskelemiyordu**. Kodun kendi yorumu `raw` dalı için bunun *"önceden hiç
    çalışmadığını"* kaydetmişti; **kardeş dallar açık kalmıştı** (deponun kendi
    "kimlik asimetrisi" sınıfı, MIMARI §6.1h).

    ## Sözleşme

    Bilinen taşıyıcı alanlar (`result.rows` · `raw_rows.rows` · `anomalies` ·
    `raporlar`/`pvm_raporlar` içindeki segment etiketleri) maskelenir; `pii:view` yetkisi
    olan **maskesiz görür** ve bu AYRI bir audit satırıdır (KVKK: hangi PII'yi kim gördü).
    Maskeleme **best-effort DEĞİL**: bir alan tanınmıyorsa sessizce geçilir ama tanınan
    her alan mutlaka geçer — ve audit `try/except`'siz atılır (*"başarı audit'siz
    raporlanamaz"*).
    """
    from control_plane import audit
    from control_plane.authorize import can

    goruldu = False

    def _satirlari_maskele(satirlar):
        nonlocal goruldu
        if not satirlar:
            return satirlar
        maskeli, bulundu = mask_rows(satirlar)
        if not bulundu:
            return satirlar
        if can(principal, "pii:view") if principal is not None else False:
            goruldu = True
            return satirlar
        return maskeli

    for alan in ("result", "raw_rows"):
        tasiyici = getattr(resp, alan, None)
        if tasiyici is not None and getattr(tasiyici, "rows", None):
            tasiyici.rows = _satirlari_maskele(tasiyici.rows)

    # BOYUT DEĞERİ TAŞIYAN ETİKETLER de maskelenir. `musteri`/`operator` kırılımında
    # bunlar **doğrudan kişi adıdır**. Satır maskelenip etiket maskelenmeseydi kapı yarım
    # kalırdı ve tam da en GÖRÜNÜR yerden sızardı (anomali listesi, katkı bulgusu).
    #
    # Alan adları ŞEMADAN doğrulandı, tahmin edilmedi: `DrillAnomaly.value` ·
    # `ContributionFinding.label`/`deger` — ilk sürümde uydurduğum `segment` alanı
    # `ContributionReport`'ta YOKTU ve test onu yakaladı.
    def _etiket_maskele(oge, anahtarlar):
        nonlocal goruldu
        for k in anahtarlar:
            v = getattr(oge, k, None)
            if not isinstance(v, str) or not v:
                continue
            yeni = mask_text(v)
            if yeni == v:
                continue
            if principal is not None and can(principal, "pii:view"):
                goruldu = True
            else:
                setattr(oge, k, yeni)

    for oge in (getattr(resp, "anomalies", None) or []):
        _etiket_maskele(oge, ("value",))
    for alan in ("raporlar", "pvm_raporlar"):
        for rapor in (getattr(resp, alan, None) or []):
            for bulgu in (getattr(rapor, "bulgular", None) or []):
                _etiket_maskele(bulgu, ("label", "deger"))

    if goruldu:
        audit.record(principal, "pii_view", nl_question=ad,
                     ip=request.client.host if request.client else None)
    audit.record(principal, "query", nl_question=ad,
                 rows_returned=getattr(getattr(resp, "result", None), "row_count", None),
                 contract_id=getattr(resp, "contract_id", None),
                 ip=request.client.host if request.client else None)
