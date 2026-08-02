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
    if resp.interpretation and not has_pii_view:
        facts = resp.interpretation.get("facts") or []
        for f in facts:
            if isinstance(f, dict) and isinstance(f.get("text"), str):
                f["text"] = mask_text(f["text"])
        if isinstance(resp.interpretation.get("summary"), str):
            resp.interpretation["summary"] = mask_text(resp.interpretation["summary"])
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
