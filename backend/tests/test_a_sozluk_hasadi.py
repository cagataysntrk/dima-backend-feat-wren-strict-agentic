r"""🔴 `§A.6/3` — **MADENCİNİN KOLU**: hasat hattı kuruluydu, çeviren yoktu.

`§A.5` ölçümü: `sinonim_onerici` → `kuyruga_koy` → admin onayı → `compose` zinciri
**eksiksiz**, ama modülün **hiçbir çağıranı yoktu**. Depo bunu *«meşru — tasarım:
offline»* diye kaydetmişti; sınıflandırma doğru, **sonuç eksik**:

> 🆌 *«Offline» bir ÇALIŞMA KİPİDİR, bir ÇALIŞMAMA GEREKÇESİ değil.*

✅ Kol: `lab/sozluk_hasadi.py`. **Kuru mod varsayılan** — sağlayıcı olmadan da koşar ve
*«kaç alan hasat edilebilirdi»*yi **sayar**. *Bir borç, ödenemediği gün bile ölçülebilir
olmalıdır.*

⚠ **Ve modül üretimden çağrılMAmalı**: `E-8` (*sıcak yola seri ikinci LLM turu
eklenemez*) bunu **şart** koşuyor. Bu yüzden `YETIM_MESRU`'da **kalıyor** — ama artık
gerekçesi *«koşucusu yok»* değil, *«kolu şurada»*.

## Ölçülen borç (2026-08-12, gerçek katalog)

```
23 küp · sinonimi olmayan («çıplak») alan: 1   →  maliyet.toplam_uretim_kg
```

⊙ Yani `§A`'nın *«iş sözlüğü çürümüş»* öncülü **üçüncü kez** ölçümle daraldı: 136
ölçünün **135'i** zaten 3+ ada sahip ve çıplak alan **bir tane**. Sözlük çürük değil;
**büyümesi otomatik değil**di — ve asıl eksik oydu.
"""

from __future__ import annotations

import ast
import inspect
import pathlib

_KOK = pathlib.Path(__file__).resolve().parents[1]


def test_KOSUCU_VAR():
    """🔴 **ASIL KAPI.** Kol yoksa hat çalışmaz."""
    f = _KOK / "lab" / "sozluk_hasadi.py"
    assert f.is_file(), (
        "🔴 `lab/sozluk_hasadi.py` YOK — hasat hattının kolu kaldırılmış. "
        "`sinonim_onerici` yeniden çalıştırılmayan bir motora döner.")


def test_KOSUCU_MADENCIYI_GERCEKTEN_CAGIRIYOR():
    """⚠ Dosyanın var olması yetmez: *«bir aracı yayımlamak onu çağrılabilir yapmaz»*.
    Yüklem **yapısal** (`ast`) — yorumda geçen bir ad kapıyı yeşil yapmasın."""
    kaynak = (_KOK / "lab" / "sozluk_hasadi.py").read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    # ⚠ **İLK YÜKLEMİM KENDİ KUSURUYLA KIRMIZI VERDİ** (ders ③): `from app import
    # sinonim_onerici as _so` biçiminde ad **alias**'tadır, `module`'de değil — yüklem
    # yalnız `module`'e bakınca *«import etmiyor»* dedi. *Bir kapının kırmızısı önce
    # kapının kendi kapsamıyla sınanmalı.*
    adlar: set[str] = set()
    for n in ast.walk(agac):
        if isinstance(n, ast.ImportFrom):
            if n.module:
                adlar.add(n.module.split(".")[-1])
            adlar |= {a.name.split(".")[-1] for a in n.names}
        elif isinstance(n, ast.Import):
            adlar |= {a.name.split(".")[-1] for a in n.names}
    assert "sinonim_onerici" in adlar, (
        "🔴 koşucu `sinonim_onerici`'yi import ETMİYOR — kol boşa dönüyor.")
    cagrilar = {n.func.attr for n in ast.walk(agac)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert {"ciplak_cube_icin", "kuyruga_koy"} <= cagrilar, (
        f"🔴 koşucu madencinin iki ucunu da çağırmıyor: {sorted(cagrilar)[:8]}")


def test_KURU_MOD_VARSAYILAN_ve_YAZMIYOR():
    """🔴🔴 **GÜVENLİK YÜKLEMİ.** Varsayılan koşum **hiçbir şey yazmamalı** ve **hiçbir
    LLM çağırmamalı** — yoksa bir CI koşumu sessizce kuyruğa gürültü doldurur."""
    from lab import sozluk_hasadi

    imza = inspect.signature(sozluk_hasadi.kos)
    assert imza.parameters["yaz"].default is False, (
        "🔴 `kos(yaz=...)` varsayılanı `True` — kuru mod varsayılan olmalı.")
    govde = inspect.getsource(sozluk_hasadi.kos)
    kuru_dal = govde.split("if not yaz:")[1].split("return rapor")[0]
    assert "kuyruga_koy" not in kuru_dal and "build_generator" not in kuru_dal, (
        "🔴 kuru dalda yazma/LLM izi var — kuru mod adını hak etmiyor.")


def test_E8_KORUNUYOR_sicak_yol_bu_modulu_cagirmiyor():
    """🔴🔴 `E-8` — *sıcak yola seri ikinci LLM turu eklenemez, ölçümle bile açılmaz.*

    Koşucu **`lab/`** altında ve `app/` **hiçbir yerden** import etmiyor. Bu bir tercih
    değil bir **şart**: üretim importu doğduğu gün `E-8` ihlal edilmiş olur.
    """
    kacak = []
    for kd in ("app", "admin_app", "control_plane"):
        d = _KOK / kd
        if not d.is_dir():
            continue
        for f in d.rglob("*.py"):
            from tests._kod_ayikla import kodu_ayikla

            # 🅞 **Sözü değil KULLANIMI ara.** Açıklamada geçen bir modül adı bir
            # çağrı değildir; ayıklayıcı ortak (`tests/_kod_ayikla.py`) ㊲.
            m = kodu_ayikla(f.read_text(encoding="utf-8"))
            if "sozluk_hasadi" in m or "sinonim_onerici" in m:
                kacak.append(str(f.relative_to(_KOK)))
    assert not kacak, (
        f"🔴 `E-8` İHLALİ: üretim kodu hasat modülünü import ediyor → {kacak}. "
        "Bu zincir çevrimdışıdır; sıcak yola bağlanamaz.")


def test_CIPLAK_ALAN_SAYISI_ARTMIYOR():
    """🔴 **BORÇ TAVANI.** Bugün **1** çıplak alan (`maliyet.toplam_uretim_kg`).
    Katalog büyürken sinonimsiz alan sayısı artarsa, sözlük **geride kalıyor** demektir.

    ⊙ Yüklem koşucunun **kendi ölçüm fonksiyonunu** çağırır — ikinci bir *«çıplak»*
    tanımı yazılmaz (`KAT-1`).
    """
    from lab.sozluk_hasadi import _ciplak_alanlar

    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    w = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                    connection_info=s.connection_dict())
    try:
        sema = w.schema()
    finally:
        try:
            w.close()
        except Exception:                              # noqa: BLE001
            pass
    ciplak = _ciplak_alanlar(sema)
    assert len(sema.get("cubes") or []) >= 20, "⊘ ölçüm tabanı çöktü: katalog küçük"
    assert len(ciplak) <= 3, (
        f"🔴 sinonimi olmayan alan {len(ciplak)} (tavan 3): "
        f"{[f'{c}.{a}' for c, _t, a in ciplak[:6]]} — sözlük katalogun gerisinde kaldı. "
        "`python lab/sozluk_hasadi.py --kuru` ile bak, `--yaz` ile aday üret.")


def test_KURU_MOD_GERCEKTEN_KOSUYOR():
    r"""🔴🔴 **ÇALIŞTIRAN YÜKLEM** — ve neden var olduğu ölçülmüş bir kusurdur.

    ⊙ `FAZ 8.6` (`7d4638f`) `_tiklama_adaylari()`'yi dosyanın **sonuna** ekledi ve o yer
    `if __name__ == "__main__"` guard'ının **altındaydı**. Modül import edilince
    guard **çalışmaz**, dolayısıyla fonksiyon **tanımlanmaz**; ama `kos()` onu çağırıyor:

        NameError: name '_tiklama_adaylari' is not defined

    Aracın belgelediği tek kullanım (`python lab/sozluk_hasadi.py`) **tamamen kırıktı**
    ve bu dosyadaki **hiçbir** kapı görmedi — çünkü hepsi modülü **import ediyor**,
    `kos()`'u **koşturmuyordu** 🆎. *Bir testin çağırması, ürünün çağırdığı anlamına
    gelmez; bir modülün import edilmesi de çalıştığı anlamına gelmez.*

    ⚠ Kuru mod seçildi bilerek: yazma yok, LLM yok, DB yok — yani bu yüklem **ucuz**
    ve yine de gövdeyi **gerçekten** koşturur.

    ⚠🅑 **Ama bu yüklem tek başına o kusuru YAKALAYAMAZ ve bu ölçüldü:** guard'ın
    altına konan bir `def` **import sırasında yine çalışır**; çökme yalnız `__main__`
    kipinde olur, çünkü guard gövdesi o `def`'ten **önce** koşar. Mutasyon bu yüklemin
    altında **hayatta kaldı**. Asıl değişmezi bir sonraki yüklem tutuyor.
    """
    from lab import sozluk_hasadi

    rapor = sozluk_hasadi.kos(yaz=False)
    assert rapor["kuru"] is True
    for alan in ("cube", "ciplak", "aday", "yazilan", "tiklama_aday"):
        assert alan in rapor, f"🔴 rapor alanı kayboldu: {alan!r} 🅬"
    assert rapor["yazilan"] == 0, "🔴 kuru mod YAZDI — adını hak etmiyor."


def test_MAIN_GUARDI_SON_IFADE():
    r"""🔴🔴 **KUSURUN GERÇEK DEĞİŞMEZİ** — ve doğru araç bu ②.

    `if __name__ == "__main__":` bloğu **modülün son üst-düzey ifadesi** olmalıdır.
    Altına konan her `def`/atama, **import**ta çalışır ama **`__main__` kipinde geç
    kalır**: guard gövdesi onlardan **önce** koşar ve `NameError` fırlar.

    ⊙ Ölçülmüş vaka (`7d4638f`): `_tiklama_adaylari` guard'ın altına düştü,
    `python lab/sozluk_hasadi.py` **çöktü**, ve import eden hiçbir kapı görmedi 🆎.

    ⚠ Bir önceki yüklem (`kos()`'u koşturan) bu mutasyonu **yakalayamadı** — çünkü
    import kipinde ad **tanımlıdır**. *Doğru soruyu yanlış kiple sormak, cevabı
    değiştirir.*
    """
    import ast
    import inspect
    import pathlib as _p

    from lab import sozluk_hasadi

    agac = ast.parse(_p.Path(inspect.getfile(sozluk_hasadi)).read_text(encoding="utf-8"))
    guard_yeri = [i for i, d in enumerate(agac.body)
                  if isinstance(d, ast.If) and "__main__" in ast.unparse(d.test)]
    assert guard_yeri, "🔴 `__main__` guard'ı bulunamadı — çapa kaymış."
    sonra = agac.body[guard_yeri[0] + 1:]
    assert not sonra, (
        "🔴 `__main__` guard'ından SONRA üst-düzey ifade(ler) var: "
        f"{[type(d).__name__ for d in sonra]}. Bunlar import'ta çalışır ama betik "
        "kipinde GEÇ KALIR — guard gövdesi onlardan önce koşar ve `NameError` fırlar "
        "(ölçülmüş vaka: `7d4638f`).")
