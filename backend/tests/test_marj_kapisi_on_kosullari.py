r"""🔴 `FAZ 2` — **MARJ KAPISININ ÖN KOŞULLARI** *(ve `2.1`/`2.2`'nin gerekçeli ⊘'si)*.

`FAZ 2` *«marj eşiği bir bayrak olsun, `cube_router:1190` onu okusun»* istiyordu.
Ölçüldü (13 Ağustos 2026) ve **`2.1` ile `2.2` ertelendi** ㊸ — üç engelin üçü de
kodda ölçüldü, hiçbiri fikir değil:

**① Bayrak kaydı SAYI taşımıyor.** `features.resolve_for` imzası `dict[str, str]`;
değerler **aşamadır** (`off|alpha|beta|prod`). `marj_esigi: ∞` bir **sayıdır** ve bu
şekle oturmaz ⑤. Sayısal ayarların evi `app/config.Settings`'tir (`consistency_k` ·
`intent_azami_saniye` deseni). İkisini birden kullanmak **tek bir düğme için iki
mekanizma** demektir — `KAT-1`'in tam tersi.

**② `cube_router` bilerek SAF.** `:1375` bunu bir disiplin olarak yazmış: *«Bayrak
parametrede, `get_settings()` çağrısında DEĞİL… Bayrağı çağıran çözer»* — gerekçesi
`lab/` araçlarının A/B koşabilmesi. `_match_cube`'un **beş** genel çağıranı var
(`cube_only_match` · `chip_kullanisli_mi` · `cube_tie_candidates` · `partial_unknowns`
· `typo_correct`), beşi de `(q, schema)`.

**③ 🔴 BELİRLEYİCİ OLAN BU: ayar TEK KAYNAĞI BÖLERDİ.** Beraberliği **kıran** kural
(`_match_cube:1194/1200`) ile beraberliği **tanımlayan** kural
(`cube_tie_candidates:2547`) **aynı ölçüyü** okur — `_longest_syn_hit`, ve o
fonksiyonun kendi docstring'i bunu şöyle gerekçelendirir: *«ikisi ayrışırsa chip,
route'un çözebildiği bir soruya sorulur.»* Yalnız `_match_cube`'u ayarlanabilir
yapmak o ayrışmayı **elle üretmek** olurdu.

⊙ Ve motivasyon tarafı: `FAZ 2`'yi doğuran **ölçülmüş bir kusur yok**. Planın kendi
zarar kontrolü *«varsayılan `∞` → hiçbir davranış değişmez; faz **etkisiz** teslim
edilir»* diyor. Ölçülmemiş bir ihtiyaç için, sistemin **en çok sınanan** yolunda beş
imza açmak `§101.1`'in tersidir.

## Bu kapı ne yapar

⊘ bir sonuçtur ama **kapısız bir ⊘ bir niyettir**. Bu dosya, ertelemenin dayandığı üç
olguyu **kilitler**: biri değişirse ⊘ yeniden değerlendirilmelidir — ve kapı bunu
kırmızıyla söyler 🅗.

## ⚠ `2.4` ZATEN VAR — ㊷ on üçüncü kez

Plan *«`_meta.karar` makbuza girsin»* istiyordu. `typo_correct` **zaten** her
düzeltmeyi `{"kind": "auto"|"suggest"}` diye yazıyor — bu tam olarak
`Karar.OTO_ICRA` / `Karar.GOSTER`'dir, dört üretim noktasında. Yeni bir alan
açmak ㊲ *aynı işin iki satırı* olurdu.
"""

from __future__ import annotations

import ast
import inspect
import pathlib

_APP = pathlib.Path(__file__).resolve().parents[1] / "app"


# ── ① BAYRAK KAYDI AŞAMA TAŞIR, SAYI DEĞİL ───────────────────────────────────

def test_bayrak_cozumleyicisi_ASAMA_dondurur_sayi_DEGIL():
    """🔴 `2.1`'in ⊘ gerekçesi. Bu imza `dict[str, float]` olursa erteleme düşer.

    ⚠ İmza **çalışma zamanında** okunur (`inspect`), metinde aranmaz — bir yorum
    satırındaki `dict[str, str]` kapıyı yanıltmamalı 🅞.
    """
    from app.features import resolve_for

    donus = inspect.signature(resolve_for).return_annotation
    assert "str]" in str(donus), (
        f"🔴 `resolve_for` artık {donus} döndürüyor — bayrak kaydı SAYI taşıyabiliyorsa "
        "`FAZ 2.1`'in ⊘ gerekçesi düşmüştür, yeniden değerlendirilmeli.")


def test_sayisal_ayarlarin_evi_SETTINGS():
    """Sayısal düğmelerin **tek** evi. `marj_esigi` bir gün gelirse **buraya** gelir;
    `features.yml`'e değil (iki mekanizma = `KAT-1` ihlali)."""
    from app.config import Settings

    alanlar = getattr(Settings, "model_fields", {})
    sayisal = [a for a, f in alanlar.items()
               if getattr(f, "annotation", None) in (int, float)]
    assert len(sayisal) >= 5, (
        "🔴 `Settings` sayısal ayar taşımıyor görünüyor — ölçüm aracı bozulmuş olabilir "
        "㉒; `consistency_k`/`intent_azami_saniye` orada olmalıydı.")


# ── ② `cube_router` SAF KALIR ────────────────────────────────────────────────

def test_cube_router_AYAR_OKUMAZ():
    """🔴 `:1375`'in disiplini: *«Bayrağı çağıran çözer.»*

    Bu yüklem `lab/` araçlarının A/B koşabilmesini korur — modül içinde bir ayar
    okuması olursa, aynı süreçte iki farklı yapılandırma **koşulamaz** hâle gelir.

    ⚠ ② `ast` ile: yorumdaki `get_settings()` sözü kapıyı kırmamalı.
    """
    agac = ast.parse((_APP / "cube_router.py").read_text(encoding="utf-8"))
    yasak = {"get_settings", "resolve_for"}
    bulunan = [d.func.id for d in ast.walk(agac)
               if isinstance(d, ast.Call) and isinstance(d.func, ast.Name)
               and d.func.id in yasak]
    assert not bulunan, (
        f"🔴 `cube_router` artık ayar okuyor: {sorted(set(bulunan))} — `:1375`'in "
        "saflık disiplini kırıldı, `lab/` A/B koşamaz.")


# ── ③ 🔴 TEK KAYNAK: beraberliği TANIMLAYAN ile onu KIRAN aynı ölçüyü okur ───

def test_beraberlik_olcusu_TEK_KAYNAK():
    """🔴🔴 **`FAZ 2.2`'nin ⊘'sünün BELİRLEYİCİ gerekçesi.**

    `_match_cube` (kıran) ile `cube_tie_candidates` (tanımlayan) **aynı**
    `_longest_syn_hit`'i çağırmalı. Ayrışırlarsa chip, route'un **çözebildiği** bir
    soruya sorulur — `_longest_syn_hit` docstring'inin kendi uyarısı.

    🅑 Mutasyon: iki çağrıdan biri başka bir ölçüye (`_match_measure` gibi)
    çevrilirse bu yüklem kırılır.
    """
    agac = ast.parse((_APP / "cube_router.py").read_text(encoding="utf-8"))
    sahipler: dict[str, int] = {}
    for d in ast.walk(agac):
        if not isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        n = sum(1 for c in ast.walk(d)
                if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                and c.func.id == "_longest_syn_hit")
        if n:
            sahipler[d.name] = n

    for ad in ("_match_cube", "cube_tie_candidates"):
        assert ad in sahipler, (
            f"🔴 `{ad}` artık `_longest_syn_hit` okumuyor — beraberlik ölçüsü İKİYE "
            "AYRILDI. Chip ile route ayrı şeyler ölçüyorsa, sistem cevaplayabildiği "
            "bir soruyu sorar (KAT-1).")


# ── ④ `2.4` ZATEN VAR: karar makbuzda ────────────────────────────────────────

def test_karar_MAKBUZDA_zaten_var():
    """㊷ Plan *«`_meta.karar` ekle»* istiyordu; `kind` **zaten** o kararı taşıyor.

    `auto` ≡ `Karar.OTO_ICRA` · `suggest` ≡ `Karar.GOSTER`. Yeni bir alan açmak ㊲
    *aynı işin iki satırı* olurdu — ve iki satır bir gün ayrışır.
    """
    from app.emin_miyim import Karar

    kaynak = (_APP / "cube_router.py").read_text(encoding="utf-8")
    assert kaynak.count('"kind": "auto"') >= 2 and kaynak.count('"kind": "suggest"') >= 2, (
        "🔴 makbuzdaki karar alanı kayboldu — `FAZ 2.4`'ün «zaten var» gerekçesi düştü.")
    # ⚠ Ve eşleme **yazılı** olmalı, varsayımda kalmamalı 🅐
    assert Karar.OTO_ICRA.value == "oto_icra" and Karar.GOSTER.value == "goster"
