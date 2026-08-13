r"""🔴🔴 `§B1`+`§B2` — GARSONA GİDEN HER YOL **BUDANMIŞ KATALOG** ve **ÖRNEK** görmeli.

## Ölçülen boşluk (2026-08-12, denetim ajanı + kendi ölçümüm)

`§B1` (şema daraltma) ve `§B2` (VQR few-shot) `§0.6` karnesinde **koşulsuz ✅** yazıyordu.
Ölçüldü — ikisi de garsonun **üç yolundan yalnız birine** bağlıydı:

    metin_ve_indeks çağrı yerleri: 5 · `soru=` geçen: **1**
      ask.py:4003  soru=✅  ← TAZE garson
      ask.py:359   soru=🔴  ← `llm.select_cube` (PLAN İÇİ garson)
      ask.py:5017  soru=🔴  ← `refine_cube`     (TAKİP garsonu)
      ask.py:270   —        ⊙ planlayıcı kurulumu (garson değil)
      plan_tuketici.py:411 — ⊙ orkestratör (garson değil)

    _vqr_ornek çağrı yeri: **1** (yalnız taze yol)

⊙ Yani bir kullanıcı ilk soruyu sorduğunda garson **budanmış** katalog + örnek görüyor;
**takip** sorusunda ve **plan içi** çağrıda **23.729 karakterin tamamını** ve **sıfır
örnek** görüyordu. Karne satırları bunu söylemiyordu.

## Neden bu kapı — ve neden ALLOW-LIST

`soru=` **isteğe bağlı bir anahtar kelime**dir; unutulması **sessizdir**. Ve
`metin_ve_indeks`'in kendi docstring'i bu dosyanın gerekçesini zaten yazmış:
*«bir bayrağı N yerde okumak, N−1 yerde okumaya giden yoldur.»*

⚠ Yüklem *«hangi çağrı garson yolunda»* diye **tahmin etmiyor** — garson-olmayan iki
çağrı **adıyla ve gerekçesiyle** muaf tutulmuş bir listede. Yeni bir çağrı eklenirse
kapı kırmızı verir ve yazan kişi ya `soru=` geçer ya muafiyeti **gerekçesiyle** yazar.
*Bir kapsamı daraltmak meşrudur; daraltmayı yazmamak değildir.*
"""

from __future__ import annotations

import ast
import pathlib

_APP = pathlib.Path(__file__).parent.parent / "app"

#: 🔴 `metin_ve_indeks`'i **garson istemi kurmadan** çağıran yerler — `soru=` gerekmez.
#: Kapalı liste: her kalem tek tek okunup yargılandı.
#: 🔴🔴 **MUAFİYET FONKSİYONA BAĞLI, DOSYAYA DEĞİL — ve bunun bir sebebi var.**
#: İlk yazımım `("routers/ask.py", …)` diyordu ve **o dosyadaki ÜÇ GARSON ÇAĞRISINI DA**
#: muaf tutuyordu: mutasyonla sınandı, `soru=` silindiği hâlde kapı **yeşil kaldı**.
#: Yani kapı, koruduğunu iddia ettiği şeyi hiç ölçmüyordu — bu oturumda avladığım
#: kusurun kendi elimden çıkmış hâli. *Bir muafiyeti dosyaya vermek, o dosyadaki her
#: şeyi affetmektir.*
MUAF = {
    ("_prompt_enhance_dene", "istem zenginleştirici: katalog **sözcük havuzu** için, bir "
                             "garson istemi için değil"),
    ("cevap", "orkestratör plan tüketicisi (`plan_tuketici`): hazır planı koşar, küp SEÇMEZ"),
    # 🔴 `§7②` makro ucu — `cevap` ile **aynı sınıf ve aynı gerekçe**: plan bir
    # **reçeteden** hazır gelir, küp seçilmez, garsona hiçbir istem kurulmaz (uç LLM'e
    # değmez; `test_MAKRO_UCU_ORKESTRATORUN_LLM_KAPISINDAN_GECMEZ` bunu tutuyor).
    #
    # ⚠ Ve `soru=` geçmek burada **zararlı** olurdu, sadece gereksiz değil: `soru`
    # verildiğinde `katalog_metni` `daraltma_adaylari` ile budama yapabiliyor ve budama
    # **indeksi de** daraltıyor. Makro planı o indeksle koşuyor — daraltılmış bir indeks,
    # planın küpünü **görünmez** kılar ve reçete kendi kataloğunda düşerdi 🆐.
    # *Bir budamayı ihtiyacı olmayan yola uygulamak, tasarruf değil kör nokta üretir.*
    ("oneri_makro", "`§7②` makro ucu: plan reçeteden hazır gelir, küp SEÇMEZ; `soru=` "
                    "indeksi de budayacağı için ZARARLI olurdu"),
}
_MUAF_FN = {f for f, _ in MUAF}


def _cagrilar(ad: str) -> list[tuple[str, int, str, set[str]]]:
    """→ `[(dosya, satır, KAPSAYAN FONKSİYON, anahtar-kelimeler)]` — `ast` ile.

    ⚠ Kapsayan fonksiyon **zorunlu**: muafiyet ona bağlanıyor (yukarıdaki gerekçe).
    """
    out = []
    for f in _APP.rglob("*.py"):
        try:
            agac = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):            # noqa: PERF203
            continue
        ust = {}
        for n in ast.walk(agac):
            for c in ast.iter_child_nodes(n):
                ust[c] = n
        for n in ast.walk(agac):
            if not isinstance(n, ast.Call):
                continue
            cagri = (n.func.attr if isinstance(n.func, ast.Attribute)
                     else getattr(n.func, "id", None))
            if cagri != ad:
                continue
            ebeveyn, fn = ust.get(n), "<modül>"
            while ebeveyn is not None:
                if isinstance(ebeveyn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    fn = ebeveyn.name
                    break
                ebeveyn = ust.get(ebeveyn)
            out.append((str(f.relative_to(_APP)), n.lineno, fn,
                        {k.arg for k in n.keywords if k.arg}))
    return out


def test_OLCUM_TABANI_AYAKTA():
    """⊘ **Boş yeşil avı** — sıfır çağrı bulan bir kapı her ihmali doğrular."""
    c = _cagrilar("metin_ve_indeks")
    assert len(c) >= 4, f"⊘ ölçüm tabanı çöktü: yalnız {len(c)} çağrı bulundu: {c}"


def test_GARSON_YOLUNDAKI_HER_CAGRI_SORU_TASIYOR():
    """🔴🔴 **ASIL KAPI.** Muaf olmayan her `metin_ve_indeks` çağrısı `soru=` geçmeli.

    Kırmızı verirse ya yeni bir garson yolu **budanmamış** katalog alıyordur (kullanıcı
    takip turunda tam kataloğa döner), ya da yeni bir garson-olmayan çağrı eklenmiştir
    ve `MUAF`'a **gerekçesiyle** yazılmalıdır.
    """
    kacak = [f"{d}:{ln} ({fn})" for d, ln, fn, kw in _cagrilar("metin_ve_indeks")
             if "soru" not in kw and fn not in _MUAF_FN]
    assert not kacak, (
        f"🔴 `soru=` GEÇMEYEN garson çağrısı: {kacak}\n"
        "Bu yol garsona **budanmamış** kataloğu (23.729 kr) veriyor. `soru=` ekleyin, "
        "ya da çağrı bir garson istemi kurmuyorsa `MUAF`'a **gerekçesiyle** yazın.\n"
        "*Bir bayrağı N yerde okumak, N−1 yerde okumaya giden yoldur.*")


def test_MUAFIYET_LISTESI_BAYATLAMIYOR():
    """⚠ Ters yön: muaf tutulan bir dosya artık `metin_ve_indeks` çağırmıyorsa liste
    bayatlamıştır — ve bayat bir muafiyet, bir gün gerçek bir kaçağı örter."""
    fonksiyonlar = {fn for _d, _ln, fn, _k in _cagrilar("metin_ve_indeks")}
    hayalet = _MUAF_FN - fonksiyonlar
    assert not hayalet, (
        f"🔴 `MUAF` listesi BAYAT: {sorted(hayalet)} artık `metin_ve_indeks` çağıran bir fonksiyon değil. "
        "*Bayat bir muafiyet, bir gün gerçek bir kaçağı örter.*")


def test_UC_GARSON_YOLU_da_FEW_SHOT_GORUYOR():
    """🔴 `§B2` — few-shot da **üç garson yolunun üçünde** olmalı.

    Ölçüm (08-12): `_vqr_ornek` **tek** çağrı yerindeydi; plan içi garson ve takip
    garsonu **sıfır örnek** görüyordu. Few-shot katalog metnine **eklenerek** veriliyor
    (imza değişmiyor), yani her üç yolda da aynı desenle bağlanabilir.

    ⚠ `KURAL B` korunur: bayrak (`vqr_few_shot`) kapalıyken blok **boş** döner ve metin
    bayt bayt eskisiyle aynı kalır.
    """
    c = _cagrilar("_vqr_ornek")
    assert len(c) >= 3, (
        f"🔴 `_vqr_ornek` yalnız {len(c)} yerde çağrılıyor: {c}\n"
        "Garsonun ÜÇ yolu var (taze · plan içi `llm.select_cube` · takip `refine_cube`) "
        "ve üçü de örnek görmeli. *Bir yolda öğrenen, ötekinde unutan bir garson, "
        "kullanıcı için TEK bir garsondur.*")
