r"""🔴 **DOCSTRING AYIKLAYICI — iki kapının ORTAK ölçütü** (`KAT-1`).

## Neden var

`E-8` yasağı (*«çevrimdışı hasat zinciri üretim yoluna giremez»*) **iki** kapı
tarafından tutuluyor:

* `test_sinonim_onerici.py::test_HICBIR_ASK_YOLUNDAN_cagrilmiyor`
* `test_a_sozluk_hasadi.py::test_E8_KORUNUYOR_sicak_yol_bu_modulu_cagirmiyor`

İkisi de `app/` ağacında **metin** arıyordu — ve ikisi de aynı gün, aynı sebeple
kırmızı verdi: `app/hasat.py` yasaklı modülün adını **açıklamasında** anmıştı (*«yazan
`sinonim_onerici.kuyruga_koy`'dur, ikinci hat kurulmadı»*), oysa dosyada **hiçbir
çağrı yok** 🅞.

⚠ **Ayıklayıcı iki kapıya KOPYALANMADI** ㊲: kopyalansaydı biri bir gün düzeltilir,
öteki eski hâliyle kalırdı — ve iki kapı aynı yasağı **iki farklı** biçimde ölçerdi.

## Neden salt `ast` yetmiyor ②

Metin araması bir **dinamik** sızıntıyı da yakalıyor: `importlib.import_module(
"sinonim_onerici")` gibi bir **dize sabiti** `ast`'te bir import değildir. Bu yüzden
yalnız **docstring'ler** düşürülür; dize sabitleri **kalır** ve aranmaya devam eder.

*Bir yasağı ölçen kapı, yasağın kendisinden fazlasını yasaklıyorsa, bir gün onu doğru
dürüst yazan kişiyi durdurur.*
"""

from __future__ import annotations

import ast

__all__ = ["kodu_ayikla"]


def kodu_ayikla(kaynak: str) -> str:
    """Docstring'leri düşürür, kalan kodu geri verir (yorumlar `unparse` ile gider).

    Ayrıştırılamayan kaynak **olduğu gibi** döner: bir sözdizimi hatası yüzünden bir
    güvenlik kapısını kör etmek, hatanın kendisinden pahalıdır 🅐.
    """
    try:
        agac = ast.parse(kaynak)
    except SyntaxError:                                        # pragma: no cover
        return kaynak
    for d in ast.walk(agac):
        govde = getattr(d, "body", None)
        if not isinstance(govde, list) or not govde:
            continue
        ilk = govde[0]
        if (isinstance(d, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                           ast.ClassDef))
                and isinstance(ilk, ast.Expr)
                and isinstance(ilk.value, ast.Constant)
                and isinstance(ilk.value.value, str)):
            govde.pop(0)
            if not govde:
                govde.append(ast.Pass())
    return ast.unparse(ast.fix_missing_locations(agac))
