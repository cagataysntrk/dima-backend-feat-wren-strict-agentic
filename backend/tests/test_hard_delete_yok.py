"""**HARD-DELETE YASAĞI — beyandan KAPIYA.** [bayraksız: değişmez]

## 🔴 Kural yazılıydı, kod onu bir yerde tanımıyordu

`app/routers/conversations.py:121` kuralı birebir yazıyor:

> *"SOFT DELETE (**proje kuralı: hard-delete YOK**): kayıt+mesajlar kalır
> (audit/kurtarma); liste/getir onları süzer."*

Ölçüldü: `app/routers/connections.py::delete_connection` `s.delete(conn)` yapıyordu —
**bir hard-delete**, ve deponun **en pahalı** nesnesinde: `db_connection` satırı
**AES-256-GCM ile şifrelenmiş kimlik bilgisi** (`secret_ciphertext`) taşıyor.

| ne kaybolurdu | neden ciddi |
|---|---|
| şifreli kimlik bilgisi | kullanıcı bağlantıyı **sıfırdan** kurar; kurtarma yok |
| denetim izinin **konusu** | `audit.record(…, "connection_delete", nl_question=cid)` var olmayan bir kimliğe işaret eder |

> 🔴 *Bir silme kaydı, sildiği şeye artık ulaşamıyorsa, bir kayıt değil bir dipnottur.*

## Neden yalnız düzeltmek yetmez

Kural üç yerde **yazılıydı** (`conversations` · `VerifiedQuery` · ADR-0019) ve dördüncü
yerde **uygulanmıyordu**. *Üç kez yazılıp bir kez uygulanmayan bir kural, bir kural değil
bir alışkanlıktır.* Bu kapı onu **kaynak taramasıyla** bağlayıcı yapar.

⚠ Muafiyet listesi **açık ve gerekçeli**: bazı silmeler gerçekten kalıcıdır (geçici
oturum verisi, sır rotasyonunda eski anahtar). Muafiyet **yazılmadan** eklenemez —
*gerekçesiz bir muafiyet, muafiyet değil sessiz bir istisnadır.*
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_KOK = Path(__file__).resolve().parents[1]

#: `(dosya, fonksiyon, gerekçe)` — kalıcı silmesi **meşru** olan yerler.
#: 🔴 Bugün **boş**: ölçüldüğünde meşru bir hard-delete bulunamadı. Boş kalması bir
#: tesadüf değil bir **iddiadır**; bir gün dolarsa gerekçesi burada okunur.
MUAF: list[tuple[str, str, str]] = []


def _silme_cagrilari() -> list[str]:
    """`session.delete(...)` / `s.delete(...)` çağrıları — **yorumsuz**, AST ile.

    ⚠ Metin taraması **yetmez**: bu operasyonda taramalar **on kez** kendi belgesini
    ölçtü. Bu dosyanın kendi docstring'i `s.delete(conn)` yazıyor ve bir `grep` onu
    ihlal sanardı.
    """
    bulgular: list[str] = []
    muaf = {(d, f) for d, f, _ in MUAF}
    for p in sorted((_KOK / "app").rglob("*.py")) + sorted((_KOK / "control_plane").rglob("*.py")):
        try:
            agac = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError:                                   # pragma: no cover
            continue
        yol = p.relative_to(_KOK).as_posix()
        for fn in (n for n in ast.walk(agac)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
            if (yol, fn.name) in muaf:
                continue
            for n in ast.walk(fn):
                if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                        and n.func.attr == "delete"
                        and isinstance(n.func.value, ast.Name)
                        and n.func.value.id in ("s", "session", "oturum", "db")):
                    bulgular.append(f"{yol}::{fn.name} (satır {n.lineno})")
    return bulgular


def test_HARD_DELETE_YOK():
    """🔴 *Üç kez yazılıp bir kez uygulanmayan bir kural, bir kural değil bir
    alışkanlıktır.*"""
    bulgular = _silme_cagrilari()
    assert not bulgular, (
        "🔴 KALICI SİLME bulundu:\n  " + "\n  ".join(bulgular)
        + "\n\nProje kuralı: hard-delete YOK (soft-delete = `deleted_at` damgası). "
          "Gerçekten meşru bir kalıcı silme ise `MUAF` listesine **gerekçesiyle** yazılır; "
          "gerekçesiz bir muafiyet, muafiyet değil sessiz bir istisnadır.")


def test_MUAFIYETLER_GEREKCELI():
    """⚠ Liste bugün boş; dolduğu gün her satır bir gerekçe taşımalı."""
    for dosya, fn, gerekce in MUAF:
        assert dosya and fn and len(gerekce) > 25, f"gerekçesiz muafiyet: {(dosya, fn)}"


# --- Bağlantı silmesi: soft, ve okuma yolları SÜZÜYOR ---------------------------------

def test_BAGLANTI_SOFT_DELETE():
    """Ölçülen ihlalin kapanışı."""
    from control_plane.models import DbConnection

    assert "deleted_at" in DbConnection.model_fields
    src = (_KOK / "app/routers/connections.py").read_text(encoding="utf-8")
    assert "conn.deleted_at = datetime.utcnow()" in src


def test_SIFRELI_SIR_SILINMIYOR():
    """🔴 *Erişimi kapatmak ile veriyi yok etmek aynı şey değildir.* Kurtarma, şifreli
    sır olmadan **imkânsız** olurdu."""
    src = (_KOK / "app/routers/connections.py").read_text(encoding="utf-8")
    agac = ast.parse(src)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "delete_connection")
    govde = ast.unparse(fn)
    assert "secret_ciphertext" not in govde, (
        "🔴 Silme yolu şifreli sırra dokunuyor — kurtarma imkânsız olur.")


def test_SAHIPLIK_KAPISI_silinmisi_SUZUYOR():
    """⚠ Süzgeç **tek kapıda**: üç çağrı yerinde üç kez unutulma riski sıfırlanır.
    🔴 Ve **404** döner, 410 değil: varlığını söylemek, silinmiş bir kaydın var olduğunu
    sızdırırdı — oysa `_get_own`'un tüm amacı o sızıntıyı kapatmak."""
    src = (_KOK / "app/routers/connections.py").read_text(encoding="utf-8")
    agac = ast.parse(src)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "_get_own")
    govde = ast.unparse(fn)
    assert "deleted_at is not None" in govde
    assert "404" in govde


def test_LISTE_de_SUZUYOR():
    """⚠ Sahiplik kapısı tekil okuma içindir; **liste** ondan geçmez ve ayrıca süzmeli —
    aksi hâlde silinmiş bir bağlantı listede görünür, açılınca 404 verirdi."""
    src = (_KOK / "app/routers/connections.py").read_text(encoding="utf-8")
    agac = ast.parse(src)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "list_connections")
    assert "deleted_at.is_(None)" in ast.unparse(fn)


def test_GOC_NULLABLE_ve_INDEKSLI():
    """⚠ `nullable=True` **zorunlu**: mevcut satırlara silme damgası uydurmak, geçmişi
    yeniden yazmak olurdu. İndeks de zorunlu: her okuma yolu bu kolonu süzüyor."""
    goc = (_KOK / "migrations/versions/f1a7c92d4b60_baglanti_soft_delete.py").read_text(
        encoding="utf-8")
    assert 'sa.Column("deleted_at", sa.DateTime(), nullable=True)' in goc
    assert "create_index" in goc


def test_GOC_GERI_ALMANIN_BEDELI_yazili():
    """🔴 *Sessiz bir geri alma, veri kaybından daha kötüdür* — kimse kaybettiğini bilmez."""
    goc = (_KOK / "migrations/versions/f1a7c92d4b60_baglanti_soft_delete.py").read_text(
        encoding="utf-8")
    assert "veri kaybeder" in goc


@pytest.mark.parametrize("yol,fn", [("app/routers/conversations.py", "delete_conversation")])
def test_SOFT_DELETE_DESENI_KORUNDU(yol, fn):
    """Kuralı **yazan** yer de kapıya bağlanır: kural oradan silinirse bu kırmızı olur."""
    src = (_KOK / yol).read_text(encoding="utf-8")
    assert "hard-delete YOK" in src
