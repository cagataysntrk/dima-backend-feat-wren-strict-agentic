"""FAZ 0.14 — BEŞ ENTEGRASYON KAPISININ ORTAK İSKELETİ. **Tek sahip.**

## Neden tek dosya

`0.14`'ün `NASIL`'ı: *"`_fe_metni()` yardımcısı **yeniden kullanılır**, ikinci tarayıcı
**yazılmaz**. K3/K4/K5 yeni dosya ama **yeni desen değil** — üçü de aynı «iki tarafı
karşılaştır» iskeletini paylaşır."*

Beş kapı da aynı iki soruyu sorar: *"bir taraf ne beyan ediyor?"* ve *"öbür taraf onu
gerçekten kullanıyor mu?"* Tarayıcıyı her dosyaya kopyalamak, bu deponun **1 numaralı
kusurunu** (aynı kuralın iki sahibi) kapının **içine** koymak olurdu.

## 🔴 Yorumlar neden ayıklanır

Bu operasyonda kapılar **altı kez** metni ölçtü, davranışı değil. Sonuncusu tam burada
yakalandı: `test_uc_yetim_degil` `GET /contracts` ucunu **yeşil** sayıyordu, çünkü
`/contracts` dizesi bir **yorum satırında** geçiyordu:

    // oynatılamazdı; backend uçları (/contracts, /contracts/{cid}, /cont…

Bir yorum bir tüketici değildir. Kapı **koda** bakar.
"""

from __future__ import annotations

import pathlib
import re

import pytest

KOK = pathlib.Path(__file__).resolve().parents[1]


def frontend_dir() -> pathlib.Path:
    """Frontend kaynak kökü. Mount edilmemişse çağıran `skip` eder."""
    for aday in (KOK.parent / "dima-frontend-demo-master" / "src",
                 pathlib.Path("/dima-frontend-demo-master") / "src"):
        if aday.exists():
            return aday
    pytest.skip("frontend kaynağı mount edilmemiş (CI reçetesinde -v ... :ro gerekir)")
    raise AssertionError                                        # pragma: no cover


def yorumsuz(kaynak: str) -> str:
    """`//` ve `/* … */` yorumlarını atar — **kapı KODU ölçer, ANLATIMI değil.**

    Çok satırlı blokların **devam satırları** da atılır: yarım bir ayıklayıcı, tam
    olmayan bir kapıdır (denetimde ölçüldü — 8 satır sızıyordu).
    """
    out: list[str] = []
    blokta = False
    for s in kaynak.splitlines():
        d = s.strip()
        if blokta:
            if "*/" in d:
                blokta = False
                kalan = d.split("*/", 1)[1]
                if kalan.strip():
                    out.append(kalan)
            continue
        if d.startswith("//"):
            continue
        if "/*" in d and "*/" not in d.split("/*", 1)[1]:
            blokta = True
            bas = d.split("/*", 1)[0]
            if bas.strip():
                out.append(bas)
            continue
        # satır-içi `//` yorumu: dize değişmezlerini bozmamak için yalnız satır
        # BAŞINDA ya da boşluk sonrası gelen `//` atılır ve `://` (URL) korunur.
        s = re.sub(r"(?<![:'\"`])//(?![/*]).*$", "", s)
        out.append(s)
    return "\n".join(out)


def fe_kaynak(*, yorumlar_dahil: bool = False) -> str:
    """Tüm `.ts`/`.tsx` kaynağı tek metin. Varsayılan: **yorumsuz**."""
    kok = frontend_dir()
    ham = "\n".join(
        f.read_text(encoding="utf-8", errors="ignore")
        for f in sorted(kok.rglob("*"))
        if f.is_file() and f.suffix in (".ts", ".tsx"))
    return ham if yorumlar_dahil else yorumsuz(ham)


def fe_dosyalari(*, haric: set[str] | None = None) -> dict[str, str]:
    """`göreli yol → yorumsuz kaynak`. `haric`: dosya ADI kümesi."""
    kok = frontend_dir()
    disi = haric or set()
    return {str(f.relative_to(kok)): yorumsuz(f.read_text(encoding="utf-8", errors="ignore"))
            for f in sorted(kok.rglob("*"))
            if f.is_file() and f.suffix in (".ts", ".tsx") and f.name not in disi}


def tuketiliyor(ad: str, metin: str) -> bool:
    """Ad **kullanılıyor** mu — `import` satırları sayılmaz.

    🔴 **ÇAĞRI DEĞİL, KULLANIM.** İlk sürüm `ad\\s*\\(` arıyordu ve
    `queryFn: listConversations` gibi **fonksiyon referanslarını** göremedi → dört canlı
    sarmalayıcıyı *"ölü"* ilan etti. Kullanılmayan bir import zaten eslint'e takılır;
    kapının işi o değil.
    """
    desen = re.compile(rf"\b{re.escape(ad)}\b")
    for satir in metin.splitlines():
        if re.match(r"\s*(import|export)\b", satir) or 'from "@/lib/' in satir:
            continue
        if desen.search(satir):
            return True
    return False


def tam_yol_deseni(yol: str) -> re.Pattern[str]:
    """`/measures/{cid}/preview` → tam-yol eşleştiren desen.

    🔴 **SINIR ŞART.** Alt-dize araması `GET /contracts`'ı `` `/contracts/${cid}` ``
    içinde bulup kapıyı **yanlış-pozitif yeşil** yapıyordu ([KANIT §0.1-5]).
    Eşleşmeden sonra yeni bir yol parçası ya da kelime karakteri **gelemez**.
    """
    kacisli = re.escape(yol).replace(r"\{", "{").replace(r"\}", "}")
    govde = re.sub(r"\{[^}]+\}", lambda _m: r"[^\"'`\s]+", kacisli)
    return re.compile(govde + r"(?![\w/-])")
