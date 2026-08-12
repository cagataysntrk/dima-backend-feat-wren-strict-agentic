"""⊘ `§A15` — *«Wren'in `evals/` koşumuna desen olarak bak»* — ÖLÇÜLDÜ, YAPILMIYOR.

## Kartın iddiası

> **`evals/`** | §11.3 | 🆕 **A15** — *Wren'in kendi eval koşumu; `A1`'e desen olarak
> bakılmalı*

## Ölçüm (2026-08-12)

| | ölçülen |
|---|---|
| kurulu `wren` paketi | **28 alt modül** — `ask` · `cli` · `context` · `mdl` · `osi` · `policy` · `skills_cli` … |
| `evals` var mı | 🔴 **YOK.** `import wren.evals` → `ModuleNotFoundError` (`wren.eval`, `wren.benchmark` de yok) |
| bizim eval takımımız | ✅ `eval/run.py` **392 satır** + `cases.yaml` + `baseline.json` + **iki ground-truth** dosyası + `report.json` + tarihli mutabakat belgesi |
| koşuyor mu | ✅ `lab/kapi.py --hepsi` içinde; `test_eval_gate` bir **taban ratchet'i** tutuyor |

⊙ Yani `evals/` **depoda** var, **pakette** yok: desen olarak bakmak için `WrenAI`
deposunu klonlamak gerekir — bu bir **araştırma** işidir, bir kablolama değil.

## 🔴 KARAR: YAPILMIYOR — üç gerekçe, üçü de ölçülü

1. **Desen alınacak yer boş değil.** Kendi koşumumuz var, koşuyor ve bir **taban
   ratchet'i** tutuyor. Raporun kendi cümlesi (`§13.5`): *«`eval/run.py`'miz zaten
   selective prediction uyguluyor… listedeki çoğu araçtan **olgun**.»*
2. **Hedefi `A1` ve `A1` PARK.** `A15` açıkça *«`A1`'e desen»* diye yazılmış; `A1`
   kullanıcının bağlayıcı kuralıyla park edildi: *«ölçüm/altyapı tesisatı ürün
   değildir»*. Park edilmiş bir işe desen aramak, parkı **dolambaçlı yoldan** bozar.
3. **Bedeli ölçülmemiş.** `evals/` pakette olmadığı için maliyeti bir klon + inceleme
   turudur ve karşılığında **ne kazanacağımız yazılı değil**.

⊙ Ölçüye dayanan **on beşinci** *«yapma»*. ⚠ Ve raporun `§13.5`'te zaten adlandırdığı
**gerçek** eksikler ayrı duruyor: snapshot katmanı · kategori kırılımı · **standart
hata** (*«20 senaryoluk paydada %85 ile %90 arasındaki fark gürültü mü?»*). Onlar
`evals/`'ı kopyalamakla değil, **kendi koşumumuza eklenerek** gelir.

*Bir deseni, deseni uygulayacağı iş park edilmişken aramak; hazırlığı işin yerine
koymaktır.*
"""

from __future__ import annotations

import pathlib

_EVAL = pathlib.Path(__file__).parent.parent / "eval"


def test_MOTORDA_evals_YOK():
    """Kararın birinci dayanağı: desen **pakette** değil (depoda). Bir gün paketlenirse
    bu test kırılır ve karar **yeniden okunur**."""
    import pkgutil

    import wren
    mods = {n for _, n, _ in pkgutil.iter_modules(wren.__path__)}
    assert mods, "wren paketi okunamadı"
    assert "evals" not in mods, (
        "🔴 `wren.evals` artık PAKETTE — `§A15` kararı ölçüme dayanıyordu ve ölçüm "
        "değişti. Deseni incele: snapshot katmanı · kategori kırılımı · standart hata "
        "(§13.5'in adlandırdığı üç gerçek eksik) bizim koşumumuza eklenebilir mi?")


def test_KENDI_EVAL_KOSUMUMUZ_var_ve_TAM():
    """İkinci dayanak: desen alınacak yer **boş değil**."""
    assert (_EVAL / "run.py").is_file()
    assert (_EVAL / "cases.yaml").is_file(), "vaka kümesi yok"
    assert (_EVAL / "baseline.json").is_file(), "taban yok — ratchet dayanaksız kalır"
    gt = list(_EVAL.glob("ground_truth*"))
    assert gt, "ground-truth dosyası yok"


def test_EVAL_KAPIDA_kosuyor():
    """Üçüncü dayanak: koşum **bağlı**. Yazılıp koşulmayan bir eval, olmayan bir evaldir."""
    kapi = (pathlib.Path(__file__).parent.parent / "lab" / "kapi.py").read_text(
        encoding="utf-8")
    assert "eval" in kapi, "eval koşumu kapıdan düşmüş"
