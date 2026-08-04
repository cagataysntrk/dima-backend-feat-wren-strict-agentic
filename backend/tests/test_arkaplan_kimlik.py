"""FAZ 1.1b — **ARKA PLAN İŞİ KİMLİKSİZ KOŞMAZ** kapısı.

`1.1` yalnız **istek yolunu** kapattı. Zamanlayıcı yolu açıktı: `run_schedule` `principal`
olmadan çağrılıyordu → `authorize()` **hiç çalışmıyordu** ve zamanlanmış bir rapor,
sahibinin yetkisi **alındıktan sonra da** koşuyordu.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from app import arkaplan_kimlik as ak

KOK = pathlib.Path(__file__).resolve().parents[1]


class _SahteOturum:
    def __init__(self, kullanici=None):
        self._k = kullanici

    def get(self, _model, _kid):
        return self._k

    def exec(self, _sorgu):
        return []


# ── 1 · SAHİPLİK ZİNCİRİ ─────────────────────────────────────────────────────

def test_RUN_AS_VARSA_O_KAZANIR():
    assert ak.sahip_kimligi({"run_as_user_id": "u1", "created_by": "u2"}) == "u1"


def test_RUN_AS_YOKSA_CREATED_BY_A_DUSULUYOR():
    """🔴 **Kesinti üretmeden fail-closed'ın anahtarı.** Yol haritası *"`principal=None`
    reddedilir"* diyor; harfi harfine uygulanırsa **her zamanlanmış rapor durur**.

    Ölçüldü: kayıt `created_by`'ı **zaten taşıyor** — yani *"bu iş kimin adına koşuyor"*
    sorusunun cevabı kayıtta **duruyordu**, hiç **sorulmuyordu**. Bir zamanlamanın
    varsayılan sahibi onu **kuran** kişidir; bu bir gevşetme değil, **geriye doldurmadır**.
    """
    assert ak.sahip_kimligi({"created_by": "u2"}) == "u2"


def test_IKISI_DE_YOKSA_NONE():
    assert ak.sahip_kimligi({}) is None
    assert ak.sahip_kimligi({"created_by": "", "run_as_user_id": None}) is None


# ── 2 · ÜÇ FAIL-CLOSED KAPISI ────────────────────────────────────────────────

def test_SAHIPSIZ_IS_REDDEDILIYOR():
    """🔴 Kimliksiz bir arka plan işi `authorize()`'ı **hiç çağırmaz**. Kapatılan delik
    tam olarak budur."""
    with pytest.raises(ak.KimliksizArkaPlanIsi) as ex:
        ak.yetkilendir({"id": "s1", "label": "haftalık ciro"}, _SahteOturum())
    assert "SAHİBİ YOK" in str(ex.value) and "s1" in str(ex.value), str(ex.value)


def test_SILINMIS_KULLANICI_REDDEDILIYOR():
    """Silinmiş/pasif bir kullanıcının zamanlanmış raporu koşmaya devam etmemelidir —
    `_tenant_active` kapısının **arka plan yolundaki** karşılığı."""
    with pytest.raises(ak.KimliksizArkaPlanIsi) as ex:
        ak.yetkilendir({"id": "s2", "created_by": "silinmis"}, _SahteOturum(None))
    assert "ÇÖZÜLEMEDİ" in str(ex.value)


def test_PASIF_KULLANICI_COZULMUYOR():
    class _K:
        id, tenant_id, is_superadmin, status = "u", None, False, "suspended"

    assert ak.kimlik_coz("u", None, _SahteOturum(_K())) is None


def test_YETKISI_ALINAN_SAHIP_REDDEDILIYOR():
    """🔴 **Yetki, verildiği an değil KULLANILDIĞI AN geçerli olmalıdır.**

    Kullanıcı `viewer`'a düşürülürse zamanlanmış raporu da durmalı — aksi hâlde zamanlama,
    yetki iptalini **atlatan** kalıcı bir kanal olur.
    """
    class _K:
        id, tenant_id, is_superadmin, status = "u", None, False, "active"

    class _O(_SahteOturum):
        pass

    # tenant_id None → `tenant_scope` fail-closed → AuthzError → KimliksizArkaPlanIsi
    with pytest.raises(ak.KimliksizArkaPlanIsi):
        ak.yetkilendir({"id": "s3", "created_by": "u"}, _O(_K()))


# ── 3 · ÇAĞRI YOLU GERÇEKTEN BAĞLI ───────────────────────────────────────────

def test_RUN_SCHEDULE_KIMLIK_ISTIYOR():
    """Bir kapıyı yazmak yetmez; **çağrıldığı yerde** vardır. `run_schedule` gövdesinde
    `yetkilendir` çağrısı olmalı ve `principal is None` dalında koşmalı."""
    agac = ast.parse((KOK / "app" / "schedules.py").read_text(encoding="utf-8"))
    fn = next((n for n in ast.walk(agac)
               if isinstance(n, ast.FunctionDef) and n.name == "run_schedule"), None)
    assert fn is not None, "`run_schedule` YOK"
    assert "principal" in {a.arg for a in fn.args.kwonlyargs}, \
        "`run_schedule` `principal` almıyor — elle koşum kimliğini geçemez"
    assert any(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "yetkilendir"
               for n in ast.walk(fn)), "kimlik kapısı ÇAĞRILMIYOR — modül ölü"


def test_ZAMANLAYICI_REDDI_SESSIZCE_YUTMUYOR():
    """🔴 **Sahipsiz iş bir "eski veri" değil, bir BULGUDUR.** Genel `except`e düşürmek
    onu *"tek zamanlama hatası"* diye meşrulaştırır ve delik **sessizce** açık kalırdı."""
    kaynak = (KOK / "app" / "schedules.py").read_text(encoding="utf-8")
    i = kaynak.index("def run_due")if "def run_due" in kaynak else kaynak.index("try_claim")
    blok = kaynak[i:i + 1800]
    assert "except KimliksizArkaPlanIsi" in blok, \
        "kimlik reddi genel `except`e düşüyor — bulgu kayboluyor"
    assert blok.index("except KimliksizArkaPlanIsi") < blok.index("except Exception"), \
        "özel yakalayıcı genel olandan SONRA — hiç ateşlenmez"


# ── 4 · SÖZLEŞME + FRONTEND (K2: alan yetim kalamaz) ─────────────────────────

def test_SOZLESME_RUN_AS_DONDURUYOR():
    kaynak = (KOK / "app" / "routers" / "schedules.py").read_text(encoding="utf-8")
    assert '"run_as": sahip_kimligi(s)' in kaynak, "liste ucu sahibi döndürmüyor"


def test_FRONTEND_RUN_AS_I_TUKETIYOR():
    """🔴 **K2:** yeni bir sözleşme alanı **frontend tüketicisi olmadan** eklenemez.
    Ve burada özel bir sebep var: sahipsiz kayıt **koşmuyor**; bunu göstermemek,
    kullanıcıyı **sessizce durmuş** bir raporu beklemeye bırakırdı."""
    fe = KOK.parent / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    tip = (fe / "lib" / "api-client.ts").read_text(encoding="utf-8")
    panel = (fe / "components" / "SchedulesPanel.tsx").read_text(encoding="utf-8")
    assert "run_as?" in tip, "sözleşme tipi `run_as` taşımıyor"
    assert "s.run_as" in panel, "panel `run_as`'i OKUMUYOR — alan yetim"
    assert "sahipsiz" in panel, "sahipsiz hâl kullanıcıya GÖSTERİLMİYOR"
