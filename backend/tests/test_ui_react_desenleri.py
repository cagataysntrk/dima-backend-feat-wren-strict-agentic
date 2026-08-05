"""⚛ FAZ 6 — **React desen kapıları.** `eslint`in yerel karşılığı.

## Neden bu dosya var

FAZ 6'da ölçüldü: `pnpm lint` **7 hatayla düşüyordu** ve kimse bilmiyordu, çünkü
frontend'in **hiç CI'ı yoktu**. Hatalar eklendi, `frontend-ci.yml` yazıldı — ama CI
uzaktadır ve bu deponun ritmi *"her düzenlemeden sonra hedefli test"*tir.

⚠ Bu kapı `eslint`in **yerini almaz**; onun yalnız en pahalı üç kuralını yerelde,
`node` olmadan, saniyeler içinde tekrar eder. *Bir kuralı iki yerde zorlamak, onu
hiç zorlamamaktan iyidir — yeter ki hangisinin otorite olduğu yazılı olsun:*
**otorite `eslint`tir**, bu kapı erken uyarıdır.

## Ölçülen üç desen — ve neden "stil" değiller

| desen | gerçek sonucu |
|---|---|
| effect gövdesinde senkron `setState` | basamaklı render; ve dördü de aslında **türetilebilir** değerdi |
| render sırasında ref yazımı | eşzamanlı render'da **iptal edilmiş** bir render'ın kapatıcısı kalıcılaşabilir |
| ölü kod | ikinci sahip adayı — *canlanana kadar bakımsız kalır, canlandığında yanlış olur* |
"""

from __future__ import annotations

import re

from tests.kapi_ortak import frontend_dir, yorumsuz

_SET = re.compile(r"\bset[A-ZİÖÜĞŞÇ][A-Za-z0-9]*\(")

#: 🔴 `set…(` deseni durum ayarlayıcılara **benzeyen platform API'lerini** de yakalar.
#: ⚠ Bunu ölçmeden bilemezdim: kapı ilk yazımında `setTimeout(() => …)` çağrısını
#: *"senkron setState"* sandı — yani **yeni ve doğru** kodu kırmızı verecekti.
#: *Bir kalıp, yakaladıklarıyla değil YANLIŞ yakaladıklarıyla sınanır.*
_PLATFORM = {"setTimeout", "setInterval", "setAttribute", "setItem", "setProperty",
             "setDate", "setHours", "setMinutes", "setSeconds", "setMonth",
             "setFullYear", "setCustomValidity", "setSelectionRange",
             "setRequestHeader", "setPointerCapture", "setData"}


def _effect_govdeleri(kaynak: str):
    """`useEffect(() => { … })` gövdeleri — süslü ayraç eşleyerek.

    ⚠ Düzenli ifadeyle *"effect'in ilk satırı"*na bakmak **yetmez**: ölçülen dört
    kusurun **üçünde** `setState` ilk satır değildi (`const c = cerezOku();` ·
    `temaBaslat();` · `if (!etiket) return;` önce geliyordu). *Kapıyı yazarken
    yakalayacağı örnekleri değil, KAÇIRACAĞI örnekleri düşünmek gerekir.*"""
    for m in re.finditer(r"useEffect\(\s*\(\)\s*=>\s*\{", kaynak):
        i = m.end() - 1
        derinlik, j = 0, i
        while j < len(kaynak):
            if kaynak[j] == "{":
                derinlik += 1
            elif kaynak[j] == "}":
                derinlik -= 1
                if derinlik == 0:
                    break
            j += 1
        yield kaynak[:m.start()].count("\n") + 1, kaynak[i + 1:j]


def _senkron_setstateler(govde: str) -> list[str]:
    """Bir **geri çağrının içinde olmayan** `setX(` çağrıları.

    Geri çağrı içindeki `setState` **meşrudur** ve yakalanmamalı: olay dinleyicisi,
    `.then(…)`, `setTimeout(…)` — hepsi commit'ten sonra koşar."""
    out: list[str] = []
    yigin: list[str] = []
    k = 0
    while k < len(govde):
        c = govde[k]
        if c == "{":
            onceki = govde[max(0, k - 80):k]
            yigin.append("cb" if re.search(r"(=>|function\s*\([^)]*\))\s*$", onceki) else "blok")
            k += 1
            continue
        if c == "}":
            if yigin:
                yigin.pop()
            k += 1
            continue
        m = _SET.match(govde, k)
        if m:
            ad = m.group(0)[:-1]
            # ⚠ `c.setOption(…)` bir NESNE METODUDUR (echarts), durum ayarlayıcı değil.
            # *Bir ad kalıbı, bağlamı okunmadan bir tür beyanı sayılamaz.*
            if k and govde[k - 1] == ".":
                k = m.end()
                continue
            satir_bas = govde.rfind("\n", 0, k) + 1
            tek_satir_ok = "=>" in govde[satir_bas:k]   # `() => setX(…)`
            if ad not in _PLATFORM and "cb" not in yigin and not tek_satir_ok:
                out.append(f"{ad}() @+{govde[:k].count(chr(10)) + 1}")
            k = m.end()
            continue
        k += 1
    return out


def _tsx() -> dict[str, str]:
    kok = frontend_dir()
    return {str(p.relative_to(kok)): yorumsuz(p.read_text(encoding="utf-8"))
            for p in kok.rglob("*.ts*") if p.is_file()}


def test_EFFECT_GOVDESINDE_SENKRON_SETSTATE_YOK():
    """🔴 Ölçüldü: **dört** bileşende (`YanCubuk` ×2, `FloatingControls`,
    `KayitBildirimi`, `GeriAlSeridi`) bu desen vardı ve hepsinin niyeti **doğruydu**:
    `localStorage`/`document.cookie`/`window.innerWidth` sunucuda okunamaz, bu yüzden
    okuma mount sonrasına bırakılmıştı.

    ⚠ Ama React'ın bu iş için **tam olarak** bir aracı var: `useSyncExternalStore` —
    ve üçüncü parametresi sorunun kendisini adlandırıyor (*"sunucuda ne göstereyim?"*).
    Ortak kanca `lib/istemci.ts`'te; tema ise **gerçek** bir depo olduğu için kendi
    abonesini kurdu (`lib/tema.ts::temaAbone`) ve bir bonus kusur da kapandı: iki tema
    anahtarı ayrı `useState` tuttuğu için **birbirinden habersizdi**.

    *Bir değerin iki görüntüleyicisi varsa, o artık bileşen durumu değil bir depodur.*
    """
    kotu = []
    for ad, kaynak in _tsx().items():
        for satir, govde in _effect_govdeleri(kaynak):
            for bulgu in _senkron_setstateler(govde):
                kotu.append(f"{ad}:{satir} → {bulgu}")
    assert not kotu, (
        "🔴 effect gövdesinde senkron setState:\n  " + "\n  ".join(kotu) +
        "\n\nYAPILACAK: değer türetilebiliyorsa **türet** (durum tutma); istemciye özel "
        "bir okuma ise `useIstemciDegeri` (lib/istemci.ts) kullan.")


def test_RENDER_SIRASINDA_REF_YAZIMI_YOK():
    """🔴 `xRef.current = y` bir **render gövdesinde** çalışırsa React açıkça yasaklar
    (*"Cannot access refs during render"*): eşzamanlı/yeniden-oynatılan render'da
    **iptal edilmiş** bir render'ın değeri kalıcılaşabilir.

    ⚠ Doğru yer bağımlılıksız bir effect'tir — her commit'ten sonra tazelenir ve
    dinleyici olayı zaten commit'ten **sonra** okur. *Doğru zaman, en erken zaman
    değildir.*"""
    kotu = []
    for ad, kaynak in _tsx().items():
        satirlar = kaynak.split("\n")
        for i, s in enumerate(satirlar):
            if not re.match(r"^  [A-Za-z_][A-Za-z0-9_]*Ref\.current = ", s):
                continue
            # Bir effect/geri-çağrı İÇİNDE olsaydı girinti 2'den derin olurdu.
            kotu.append(f"{ad}:{i + 1}")
    assert not kotu, (
        "🔴 render sırasında ref yazımı:\n  " + "\n  ".join(kotu) +
        "\n\nYAPILACAK: `useEffect(() => { ref.current = x; })` — bağımlılık dizisi YOK.")


def test_ISTEMCI_KANCASI_TEK_SAHIP():
    """⚠ `useIstemciDegeri` **paylaşılan** olmalı: dört kopya tam da bu yüzden
    doğmuştu (*"her bileşen kendi küçük çözümünü yazdı"*)."""
    kok = frontend_dir()
    assert (kok / "lib/istemci.ts").exists(), "🔴 ortak istemci kancası yok"
    src = yorumsuz((kok / "lib/istemci.ts").read_text(encoding="utf-8"))
    assert "useSyncExternalStore" in src, \
        "🔴 kanca `useSyncExternalStore` kullanmıyor — hidrasyon garantisi kayboldu"


def test_TEMA_TEK_DEPODAN_OKUNUYOR():
    """🔴 Ölçülen kusur: tema anahtarı **iki yerde** çiziliyor (`FloatingControls`,
    `YanCubuk`) ve her biri kendi `useState`ini tutuyordu → birinden değiştirilince
    öteki **eski değeri gösteriyordu**. İkisi de doğruydu; ikisi birden doğru değildi."""
    kok = frontend_dir()
    tema = yorumsuz((kok / "lib/tema.ts").read_text(encoding="utf-8"))
    assert "temaAbone" in tema, "🔴 tema bir depo değil — abone yok"
    for ad in ("components/FloatingControls.tsx", "components/YanCubuk.tsx"):
        src = yorumsuz((kok / ad).read_text(encoding="utf-8"))
        assert "useSyncExternalStore(temaAbone" in src, \
            f"🔴 {ad}: tema yine yerel duruma kopyalanmış"


def test_FRONTEND_CI_VAR():
    """🔴 **Kapının kendi ön koşulu.** Bu dosya `eslint`in *erken uyarısıdır*; otorite
    CI'daki `pnpm lint`tir. O yoksa buradaki üç kural, `eslint`in kırktan fazla
    kuralının yerine geçiyormuş gibi **yanlış bir güven** üretir.

    ⊘ Depo kökü konteynerde görünmüyorsa ölçülemez — sessizce geçilmez, atlanır."""
    import pathlib

    import pytest

    wf = pathlib.Path(frontend_dir()).parent.parent / ".github/workflows/frontend-ci.yml"
    if not wf.parent.exists():
        pytest.skip("⊘ ÖLÇÜLEMEDİ — depo kökü bu ortamda görünmüyor (yalnız `backend/` "
                    "ve frontend bağlı). Depo kökünden koşulmalı.")
    assert wf.exists(), (
        "🔴 `frontend-ci.yml` YOK — frontend'in CI'ı geri alınmış. FAZ 6'da ölçüldü: "
        "CI olmadığında `pnpm lint` 7 hatayla düşüyordu ve kimse bilmiyordu.")
    metin = wf.read_text(encoding="utf-8")
    assert "--max-warnings 0" in metin, \
        "🔴 uyarılar kırmızı vermiyor — bu depoda uyarı biriktirmenin sonucu ÖLÇÜLDÜ"
    assert "tsc --noEmit" in metin, "🔴 strict tip denetimi CI'da yok"
