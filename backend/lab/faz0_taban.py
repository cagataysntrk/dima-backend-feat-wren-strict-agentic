#!/usr/bin/env python3
"""FAZ 0.1 — YENİDEN ÖLÇÜM TURU: §C'nin ölçütleri **güncel HEAD'de**.

## Neden bu araç var

Yol haritasının §C tablosu *"bugün"* sütununu taşıyor ve o sütun **bir commit'e aitti**.
Sayı bayatladığında plan sessizce yanlış bir tabana dayanır — bu deponun `D2` kuralı tam
bunun için var: **her sayı `<sayı> @<sha> · <komut>` taşır.** Bu araç o üçlüyü **üretir**;
elle yazılan bir sayı bir daha kabul edilmez.

## Üç durum, iki değil

Bir ölçüt ya **ölçülür**, ya **ölçülemez** (`⊘`) — *"yeşile yuvarlamak"* yok. `⊘` bir
başarısızlık değil, bir **ön koşul eksikliğidir** ve öyle raporlanır (ör. korpus artefaktı
yoksa: kapı koşulmamıştır, sayı uydurulmaz).

## Ölçüm aracının kendisi de bir bağımlılıktır

Bu dosya **hiçbir sayıyı sabit tutmaz**; hepsini kaynaktan/artefakttan üretir. Damga
zorunludur: `--sha` verilmezse ve `git` okunamazsa araç **koşmaz** (fail-closed) — damgasız
bir ölçüm, D2 açısından ölçüm değildir.

    python lab/faz0_taban.py                 # host'ta (git bulunur)
    python lab/faz0_taban.py --sha 0619bfd   # konteynerde (.git mount edilmez)
"""

from __future__ import annotations

import argparse
import ast
import collections
import pathlib
import re
import subprocess
import sys

BE = pathlib.Path(__file__).resolve().parents[1]          # backend/
KOK = BE.parent                                            # repo kökü
FE = KOK / "dima-frontend-demo-master"
RAPOR = BE / "lab" / "reports" / "faz0_taban.md"

OLCULEMEDI = "⊘ ÖLÇÜLEMEDİ"


class Olcum:
    """Tek bir ölçüt: değer + komut + (varsa) ölçülememe gerekçesi."""

    def __init__(self, deger: str, komut: str, not_: str = ""):
        self.deger, self.komut, self.not_ = deger, komut, not_

    @classmethod
    def yok(cls, komut: str, neden: str) -> Olcum:
        return cls(OLCULEMEDI, komut, neden)


# ── yardımcılar ────────────────────────────────────────────────────────────────

def _oku(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""


def _grep_say(kok: pathlib.Path, desen: str, uzanti: str = "*.py") -> int:
    """`grep -r <desen>` isabet SAYISI (satır değil, isabet) — kabuk bağımsız."""
    n = 0
    for f in kok.rglob(uzanti):
        n += len(re.findall(desen, _oku(f)))
    return n


def _grep_dosya(kok: pathlib.Path, desen: str, uzanti: str = "*.py") -> int:
    """`grep -rl` — desenin geçtiği DOSYA sayısı."""
    return sum(1 for f in kok.rglob(uzanti) if re.search(desen, _oku(f)))


# ── §C ölçütleri ───────────────────────────────────────────────────────────────

def olcut_1_2_3() -> dict[str, Olcum]:
    """Korpus üçlüsü — `lab/reports/nl_corpus.md` ARTEFAKTINDAN okunur.

    ⚠ Korpusu burada yeniden koşmuyoruz: kapı (`lab/kapi.py --tam`) zaten koşuyor ve
    **iki test konteyneri asla paralel koşmaz**. Artefakt yoksa `⊘` — sayı uydurulmaz.

    🔴 **§C'nin 1. ölçütünde bir TANIM BULANIKLIĞI ölçüldü:** satır *"yanlış-cube
    493/7213"* diyor, ama korpus raporunda `yanlış cube` toplamı **458**tir; aradaki
    **35** *"Discovery'ye düştü"*tür. Yani 493 = *"doğru cube ÜRETİLEMEDİ"*, `yanlış-cube`
    ise onun **alt kümesi**. İkisi ayrı ayrı raporlanır — hedef *"azalır"* olduğu için
    hangi sayının azalacağı belirsiz kalamaz.
    """
    metin = _oku(BE / "lab" / "reports" / "nl_corpus.md")
    komut = "python lab/nl_corpus.py --kapi  (artefakt: lab/reports/nl_corpus.md)"
    if not metin:
        neden = "korpus artefaktı yok — kapı bu HEAD'de koşulmamış"
        return {k: Olcum.yok(komut, neden) for k in ("1a", "1b", "1c", "2", "3")}

    dogru = yanlis = discovery = payda_cube = 0
    for m in re.finditer(r"DOĞRU CUBE: (\d+)/(\d+).*?yanlış cube: (\d+).*?"
                         r"Discovery'ye düştü: (\d+)", metin):
        dogru += int(m.group(1)); payda_cube += int(m.group(2))
        yanlis += int(m.group(3)); discovery += int(m.group(4))

    say: collections.Counter[str] = collections.Counter()
    for m in re.finditer(r"- (tekil|süreç)::([A-ZÇĞİÖŞÜa-zçğıöşü:\-()ğ ]+): (\d+)", metin):
        say[m.group(2).strip()] += int(m.group(3))
    tur = sum(int(m.group(1)) for m in re.finditer(r"toplam tur: (\d+)", metin))

    def oran(pay: int, payda: int) -> str:
        return f"{pay}/{payda} = %{100 * pay / payda:.1f}".replace(".", ",") if payda else OLCULEMEDI

    ok = say.get("OK", 0)
    clarify_donem = say.get("CLARIFY:dönem", 0)
    yanlis_ok = say.get("YANLIS-OK(gürültüye SQL)", 0)
    return {
        "1a": Olcum(oran(yanlis, payda_cube), komut, "YALNIZ yanlış cube (Discovery hariç)"),
        "1b": Olcum(oran(yanlis + discovery, payda_cube), komut,
                    f"doğru cube ÜRETİLEMEDİ (yanlış {yanlis} + Discovery {discovery})"),
        "1c": Olcum(str(yanlis_ok), komut, "YANLIS-OK: gürültüye SQL üretildi — artmamalı"),
        "2": Olcum(oran(ok, tur), komut, "doğrudan cevap (ERİŞİM)"),
        "3": Olcum(oran(clarify_donem, tur), komut, "±0,5 puan dışına çıkarsa ADR-0007/K3 delinmiş"),
    }


def olcut_4_rls() -> Olcum:
    n = _grep_say(BE / "app", r"rowLevelAccessControl")
    return Olcum(str(n), "grep -rc rowLevelAccessControl backend/app/",
                 "motor-seviyesi RLS; hedef: `on` + gölge modda 7 gün · sapma 0")


def _araclar() -> list[dict]:
    agac = ast.parse(_oku(BE / "app" / "tools.py"))
    out = []
    for n in ast.walk(agac):
        if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "Arac":
            out.append({k.arg: getattr(k.value, "value", None) for k in n.keywords})
    return out


def olcut_5_yetki() -> Olcum:
    a = _araclar()
    izin = collections.Counter(x.get("izin") for x in a)
    en_cok, adet = (izin.most_common(1) or [(None, 0)])[0]
    return Olcum(f"{len(a)} araç · {adet}/{len(a)} `{en_cok}`",
                 "ast: tools.py::Arac(izin=…) dağılımı",
                 "granülerlik EFEKTİF YOK demek: tek izin tüm araçları açar")


def olcut_6_yazma() -> Olcum:
    a = _araclar()
    yazar = sum(1 for x in a if x.get("yan_etki") == "yazar")
    onay = (BE / "app" / "onay_akisi.py").exists()
    return Olcum(f"yazma aracı {yazar} · onay akışı {'VAR' if onay else 'YOK'}",
                 "ast: tools.py::Arac(yan_etki='yazar') + app/onay_akisi.py",
                 "bugün yazma İMKÂNSIZ çünkü araç yok — hedef: mümkün ama ONAYLI")


def olcut_7_yetim() -> Olcum:
    """Kapılar **kör**: bu satır kapıların söylediğini değil, §C'nin envanterini izler."""
    return Olcum.yok("test_uc_yetim_degil · test_cevap_alani_yetim_degil",
                     "kapılar YEŞİL ama §C'nin 9'u kapının GÖREMEDİĞİ sınıftan — "
                     "envanter FAZ 0.14'te (K1-K5 kör noktaları) yeniden sayılır")


def olcut_8_ci() -> Olcum:
    wf = KOK / ".github" / "workflows"
    dosyalar = sorted(p.name for p in wf.glob("*.yml")) if wf.exists() else []
    kapili = [n for n in dosyalar
              if re.search(r"kapi\.py|nl_corpus|eval\.run", _oku(wf / n))]
    return Olcum(f"{len(dosyalar)} workflow · ölçüm kapısı taşıyan: {len(kapili)}",
                 "ls .github/workflows/ + içerik taraması",
                 f"dosyalar: {', '.join(dosyalar) or '—'}; hedef: 4 kapı GECELİK")


def olcut_9_turler() -> Olcum:
    adlar = re.findall(r"^(TUR_[A-Z_]+) = ", _oku(BE / "app" / "followup.py"), re.M)
    return Olcum(f"{len(adlar)}", 'grep -cE "^TUR_[A-Z_]+ = " backend/app/followup.py',
                 f"{' · '.join(adlar)} — v1 hedefi **7** (+takip +paylaş; 8.'si v3)")


def olcut_10_bayrak() -> Olcum:
    kayit = re.findall(r'^\s{4}"([a-z0-9_]+)":', _oku(BE / "app" / "features.py"), re.M)
    yaml = re.findall(r"^\s{2}([a-z0-9_]+):", _oku(BE / "demo" / "packs" / "features.yml"), re.M)
    eksik = sorted(set(kayit) - set(yaml))
    return Olcum(f"FLAG_REGISTRY {len(kayit)} ↔ features.yml {len(yaml)}",
                 "regex: features.py::FLAG_REGISTRY ↔ demo/packs/features.yml",
                 f"kayıtta var YAML'de yok: {', '.join(eksik) or '—'}")


def olcut_11_panel() -> Olcum:
    if not FE.exists():
        return Olcum.yok("grep -rE 'export (default )?function [A-Za-z]+Panel' src/",
                         "frontend kaynağı yok")
    src = FE / "src"
    export = _grep_say(src, r"export (?:default )?function [A-Za-z]+Panel", "*.tsx")
    dosya = len(list((src / "components").glob("*Panel.tsx")))
    return Olcum(f"export {export} · dosya {dosya}",
                 "grep -rE 'export (default )?function [A-Za-z]+Panel' src/ | wc -l",
                 "🔴 TANIMA BAĞLI — tavan **13 export** (ölçüt 11 tanım kutusu)")


def olcut_12_tazelik() -> Olcum:
    n = _grep_dosya(BE / "app", r"freshness")
    return Olcum(str(n), "grep -rl freshness backend/app/ | wc -l",
                 "hedef: her cevapta taze|uyarı|hata|bilinmiyor; hata/bilinmiyor → SAYI YOK")


def olcut_test_sayisi() -> Olcum:
    """Süit büyüklüğü — `pytest` yoksa `⊘` (kaba `def test_` sayımı KABUL EDİLMEZ:
    parametrize edilmiş testler farklı sayı verir, ve bu araç sayı UYDURMAZ)."""
    komut = "python -m pytest -q --collect-only"
    try:
        c = subprocess.run([sys.executable, "-m", "pytest", "-q", "--collect-only"],
                           cwd=BE, capture_output=True, text=True, timeout=600)
    except Exception as exc:                                   # noqa: BLE001
        return Olcum.yok(komut, f"pytest koşamadı: {exc}")

    # 🔴 TOPLAMA HATASI VARSA SAYI YAZILMAZ. Bu satır bir kusurdan doğdu: araç host'ta
    # koşulduğunda bazı test modülleri import edilemiyor ve `pytest` **daha az** test
    # toplayıp yine de "collected" yazıyordu → **1806** (konteynerde **2056**). D2 damgalı
    # bir tabloya sessizce YANLIŞ bir sayı girecekti. Ölçüm aracının kendisi de bir
    # bağımlılıktır: eksik ortamda doğru cevap "ölçemedim"dir, küçük bir sayı değil.
    hata = re.search(r"(\d+) errors?", c.stdout) or re.search(r"errors? during collection", c.stdout)
    if hata:
        return Olcum.yok(komut, "toplama HATASI var (eksik bağımlılık?) — sayı eksik "
                                "çıkardı; kanonik koşum KONTEYNERDEDİR")
    m = re.search(r"(\d+) tests? collected", c.stdout)
    if m:
        return Olcum(m.group(1), komut)
    return Olcum.yok(komut, "toplama çıktısı ayrıştırılamadı")



# ── [KANIT §0.1]'in 12 kusuru — güncel HEAD'de yeniden ────────────────────────
#
# 0.1'in `NE`'si: *"12 kusur + §C'nin tüm sayıları güncel HEAD'de yeniden ölçülür;
# yalnız HÂLÂ AÇIK olanlar iş listesine girer."* Kapananlar da yazılır (kütük).

def _fe(pat: str = "*.ts*") -> str:
    return "\n".join(_oku(f) for f in (FE / "src").rglob(pat)) if FE.exists() else ""


def _fe_tuketici(ad: str) -> int:
    """Bir alanın FE'deki **TÜKETİCİ** sayısı — `lib/types.ts` HARİÇ.

    🔴 Bu ayrım bir ölçüm hatasından doğdu: `receipt`/`supersedes` için ilk sayım **1**
    dedi ve *"tüketiliyor"* diye okundu; o tek isabet `lib/types.ts`'teki **tip beyanıydı**.
    **Bir tip beyanı tüketici değildir** — tam olarak bu deponun avladığı *"beyan var,
    tüketicisi yok"* sınıfı. Sayaç bunu bilmiyorsa kapı yanlış-pozitif yeşil verir.
    """
    if not FE.exists():
        return -1
    n = 0
    for f in (FE / "src").rglob("*.ts*"):
        if f.name == "types.ts":
            continue
        n += len(re.findall(re.escape(ad), _oku(f)))
    return n


def kusurlar() -> list[tuple[str, str, str, str]]:
    """(no, kusur, durum, kanıt) — durum: `✅ KAPANDI` · `🔴 AÇIK` · `◐ KISMEN` · `⊘`."""
    pln = _oku(BE / "app" / "planner.py")
    ask = _oku(BE / "app" / "routers" / "ask.py")
    ac = _oku(FE / "src" / "components" / "AnalysisCanvas.tsx")
    oi = _oku(FE / "src" / "components" / "OutputInsight.tsx")
    yml = _oku(BE / "demo" / "packs" / "features.yml")
    fe = _fe()
    out: list[tuple[str, str, str, str]] = []

    kapali = 'kapisiz=True, dis_maliyet="sifir"' in pln
    out.append(("1", "`sec()` uydurma araç → makbuz düşüyor · bütçe kapısı atlanıyor",
                "✅ KAPANDI" if kapali else "🔴 AÇIK",
                "`planner.py` reddi `kapisiz=True, dis_maliyet=\"sifir\"` ile kaydeder "
                "(FAZ 0.2, bu turda) + `sorgu_sayisi` fail-safe"))

    rozet = ac.count("SourceBadge")
    out.append(("2", "`AnalysisCanvas` `SourceBadge`/`explain` render **etmiyor**",
                "✅ KAPANDI" if rozet else "🔴 AÇIK",
                f"`AnalysisCanvas.tsx`: SourceBadge **{rozet}** · explain **{ac.count('explain')}** "
                "→ **FAZ 0.3**"))

    mek = '"netlestirme_onceligi" in resolve_for' in ask
    m = re.search(r"netlestirme_onceligi:\s*\"?(\w+)", yml)
    out.append(("3", "Ölçü-belirsizliği chip'i Intent-JSON'dan SONRA",
                "◐ KISMEN" if mek else "🔴 AÇIK",
                f"mekanizma **{'VAR' if mek else 'YOK'}** · bayrak **{m.group(1) if m else '?'}** "
                "→ kalan iş bir **ÖLÇÜM KARARI** (FAZ 0.4)"))

    capa = ask.count("capalar=")
    out.append(("4", "`Baglam` çapa kuralları üretimde **hiç ateşlenmiyor**",
                "✅ KAPANDI" if capa else "🔴 AÇIK",
                f"`ask.py` `capalar=` geçişi **{capa}** · `SureklilikOlcumu` çağrısı "
                f"**{ask.count('SureklilikOlcumu')}** · FE `reply_to_cube_query` "
                f"**{fe.count('reply_to_cube_query')}** → **FAZ 0.5**"))

    liste = bool(re.search(r"(listContracts|get\([\'\"`]/contracts[\'\"`])", fe))
    out.append(("5", "`GET /contracts` (liste) **tüketicisiz**; kapı yanlış-pozitif yeşil",
                "✅ KAPANDI" if liste else "🔴 AÇIK",
                f"FE'de liste çağrısı **{'VAR' if liste else 'YOK'}** "
                f"(`/contracts` alt-dize isabeti {fe.count('/contracts')} — kapıyı kandıran şey bu)"))

    rq = _fe_tuketici("runQuery")
    out.append(("6", "`POST /query` + `runQuery()` **ölü** (sarmalayıcı var, çağıranı yok)",
                "✅ KAPANDI" if rq > 1 else "🔴 AÇIK",
                f"`runQuery` tüketici isabeti **{rq}** (tanım dâhil; >1 olmalı)"))

    yetim = {a: _fe_tuketici(a) for a in
             ("receipt", "explain.path", "kpi_components", "supersedes", "execute:", "limit:")}
    acik = [a for a, n in yetim.items() if n == 0]
    out.append(("7", "Alan yetimleri (`receipt` · `explain.path` · `kpi_components` · "
                     "`supersedes` · `AskRequest.execute`/`limit`)",
                "✅ KAPANDI" if not acik else ("◐ KISMEN" if len(acik) < len(yetim) else "🔴 AÇIK"),
                "TÜKETİCİ sayısı (`lib/types.ts` HARİÇ): "
                + " · ".join(f"`{a}` **{n}**" for a, n in yetim.items())
                + f" → hâlâ yetim: **{', '.join(acik) or '—'}**"))

    top_var = '"top"' in _oku(BE / "app" / "interpret.py")
    top_ui = "top:" in oi or '"top"' in oi
    out.append(("8", "`interpret`'in `\"top\"` fact türü UI sözlüğünde yok → **sessizce düşüyor**",
                "✅ KAPANDI" if (not top_var or top_ui) else "🔴 AÇIK",
                f"`interpret.py` üretiyor: **{'evet' if top_var else 'hayır'}** · "
                f"`OutputInsight.tsx` tanıyor: **{'evet' if top_ui else 'HAYIR'}**"))

    ciplak = bool(re.search(r"for h in _META_HINTS[\s\S]{0,200}?h in q_norm", ask))
    out.append(("9", "`_META_HINTS` **çıplak alt-dize** eşleştiriyor",
                "🔴 AÇIK" if ciplak else "✅ KAPANDI",
                "kelime sınırı disiplinine geçmiş (çıplak `h in q_norm` kalıbı bulunamadı)"))

    sabit = bool(re.search(r"sinifla\([^)]*baglam_var=True", ask))
    out.append(("10", "`sinifla(baglam_var=True)` **sabit kodlu** → `baglam-yok` kuralı ölü",
                "🔴 AÇIK" if sabit else "✅ KAPANDI",
                f"`ask.py` içinde sabit `baglam_var=True` çağrısı: **{'VAR' if sabit else 'yok'}**"))

    try:
        import json as _json
        b = _json.loads(_oku(BE / "eval" / "baseline.json") or "{}")
        r = _json.loads(_oku(BE / "eval" / "report.json") or "{}")
        uyum = b.get("n") == r.get("n") and b.get("n") is not None
        kanit = f"`baseline.n` **{b.get('n')}** ↔ `report.n` **{r.get('n')}**"
    except Exception:                                          # noqa: BLE001
        uyum, kanit = False, "baseline/report okunamadı"
    kati = "lambda self, models" in _oku(BE / "lab" / "nl_accuracy.py")
    out.append(("11", "`eval/baseline.json` bayat · `nl_accuracy` katı monkeypatch imzası",
                "✅ KAPANDI" if (uyum and not kati) else "◐ KISMEN",
                f"{kanit} · katı imza: **{'VAR' if kati else 'yok'}**"))

    mim = "Kapsam dışı: sosyal" in _oku(BE / "MIMARI.md")
    bayrak = "sosyal_sinif" in _oku(BE / "app" / "features.py")
    test = (BE / "tests" / "test_sosyal_sinif.py").exists()
    out.append(("12", "Faz D1 teslim borcu (test ↔ assertion · MIMARI:811 · **bayrak yok**)",
                "✅ KAPANDI" if (not mim and bayrak and test) else "◐ KISMEN",
                f"test **{'VAR' if test else 'YOK'}** · MIMARI'de *\"kapsam dışı\"* "
                f"**{'hâlâ var' if mim else 'düzeltildi'}** · bayrak **{'VAR' if bayrak else 'YOK'}**"))
    return out

BASLIKLAR: list[tuple[str, str]] = [
    ("1a", "Sessiz-yanlış — **yanlış cube**"),
    ("1b", "Sessiz-yanlış — doğru cube üretilemedi *(yanlış + Discovery)*"),
    ("1c", "`YANLIS-OK` (gürültüye SQL)"),
    ("2", "Doğrudan cevap (OK)"),
    ("3", "`CLARIFY:dönem`"),
    ("4", "Motor-seviyesi RLS"),
    ("5", "Yetki granülerliği"),
    ("6", "Onaysız yazma"),
    ("7", "Yetim uç / alan"),
    ("8", "Ölçüm kapıları CI'da"),
    ("9", "Konuşma türleri"),
    ("10", "Ölü bayrak"),
    ("11", "Panel sayısı"),
    ("12", "Tazelik"),
    ("T", "Test süiti"),
]


def olc() -> dict[str, Olcum]:
    out = dict(olcut_1_2_3())
    out |= {
        "4": olcut_4_rls(), "5": olcut_5_yetki(), "6": olcut_6_yazma(),
        "7": olcut_7_yetim(), "8": olcut_8_ci(), "9": olcut_9_turler(),
        "10": olcut_10_bayrak(), "11": olcut_11_panel(), "12": olcut_12_tazelik(),
        "T": olcut_test_sayisi(),
    }
    return out


def _sha(arg: str | None) -> str:
    if arg:
        return arg
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=KOK,
                              capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:                                          # noqa: BLE001
        return ""


def main() -> int:
    ap = argparse.ArgumentParser(description="FAZ 0.1 — §C ölçütlerini güncel HEAD'de ölç")
    ap.add_argument("--sha", default=None,
                    help="ölçüm damgası; konteynerde .git mount edilmediği için gerekir")
    a = ap.parse_args()

    sha = _sha(a.sha)
    if not sha:
        print("🔴 DAMGA YOK: `git rev-parse` okunamadı ve `--sha` verilmedi.\n"
              "   Damgasız ölçüm D2 açısından ÖLÇÜM DEĞİLDİR — araç koşmaz (fail-closed).",
              file=sys.stderr)
        return 2

    olcumler = olc()
    sat = [f"# FAZ 0.1 — §C taban ölçümü  ·  @`{sha}`", "",
           "> Her satır **`<sayı> @<sha> · <komut>`** taşır (kural **D2**). Bu tablo",
           "> **elle yazılmaz** — `python lab/faz0_taban.py` üretir.",
           ">", "> `⊘ ÖLÇÜLEMEDİ` ne geçti ne kaldı demektir: ölçümün **ön koşulu**",
           "> sağlanmadı. Yeşile yuvarlamak *\"risk yok\"* yalanı üretirdi.", "",
           "| # | Ölçüt | Değer @`" + sha + "` | Komut | Not |",
           "|---|---|---|---|---|"]
    for anahtar, baslik in BASLIKLAR:
        o = olcumler.get(anahtar)
        if o is None:
            continue
        # `|` hücre ayracıdır: komut/not içindeki boru işaretleri KAÇIŞLANIR, yoksa
        # tablo sessizce bozulur (ve okuyan kişi sayıyı yanlış sütunda görür).
        kaçış = lambda s: s.replace("|", "\\|")              # noqa: E731
        sat.append(f"| {anahtar} | {baslik} | **{kaçış(o.deger)}** | "
                   f"`{kaçış(o.komut)}` | {kaçış(o.not_)} |")

    olculemedi = [k for k, o in olcumler.items() if o.deger == OLCULEMEDI]
    sat += ["", f"**Ölçülemeyen:** {len(olculemedi)}/{len(olcumler)} "
                f"({', '.join(olculemedi) or '—'})", ""]

    ks = kusurlar()
    sat += ["---", "", f"## [KANIT §0.1] — 12 kusur, @`{sha}`'de yeniden", "",
            "> Kapananlar da yazılır (**kütük**); yalnız `🔴 AÇIK` ve `◐ KISMEN` olanlar",
            "> iş listesine girer.", "",
            "| # | Kusur | Durum | Kanıt @`" + sha + "` |", "|---|---|---|---|"]
    for no, kusur, durum, kanit in ks:
        sat.append(f"| {no} | {kusur} | **{durum}** | {kanit} |")
    dagilim = collections.Counter(d.split()[0] for _, _, d, _ in ks)
    sat += ["", "**Dağılım:** " + " · ".join(f"{k} {v}" for k, v in sorted(dagilim.items())), ""]

    print("\n".join(sat))
    try:
        RAPOR.parent.mkdir(parents=True, exist_ok=True)
        RAPOR.write_text("\n".join(sat) + "\n", encoding="utf-8")
        print(f"\n→ {RAPOR}")
    except OSError as exc:
        # `lab/reports/` konteyner tarafından (root) yazılır; host'tan koşulduğunda
        # yazma izni olmayabilir. Tablo YİNE DE basılır — ama artefaktın yazılmadığı
        # SÖYLENİR: sessizce atlamak, raporun güncel sanılmasına yol açardı.
        print(f"\n⚠ ARTEFAKT YAZILAMADI ({exc.__class__.__name__}): {RAPOR}\n"
              "  Tablo yukarıda basıldı ama dosya GÜNCELLENMEDİ — kanonik koşum "
              "konteynerdedir: `docker run … dima-test python lab/faz0_taban.py --sha <sha>`",
              file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
