r"""🔴🔴 `§G` — **YETİM MODÜL KAPISI**: *«geliştirdik ama bağlanmadı, ve fark edilmedi»*.

## Neden bu kapı var

Kullanıcının `§G` teşhisi: *«ne nereye bağlanmış karışıyor; bazen geliştirip
bağlanmıyor, bu da fark edilmiyor.»* Bu deponun **ölçülmüş** kusur sınıfı — bu oturumda
**beş kez** aynı desen çıktı:

| ne | nasıl görünmüştü |
|---|---|
| `§E2` sürpriz alanları | üretiliyordu, **şemada yoktu** → Pydantic sınırında siliniyordu |
| `§F7` chip üreteci | yazılmıştı, **düzyazı ondan beslenmiyordu** |
| `§F13` `tercih.kaydet` | onay yolu tamdı, **aracı yoktu** |
| `§38.3 D13` `llm.*` | **yayımlanıyordu**, çağrılamıyordu |
| `§A.5` `sinonim_onerici` | hat kuruluydu, **kolu çeviren yoktu** |

> 🆌 *Bir motoru doğru kurmak onu çalıştırmaz.*

## Ölçüm (2026-08-12, kendi koşumum)

```
app/ altında modül                     : 138
ÜRETİMDEN (app·admin_app·control_plane) hiç import edilmeyen : 4
```

⊙ **Ve dördü, deponun `2026-08-05_V1-SON-KONTROL.md:212`'de ilan ettiği dörtle BİREBİR
aynı.** Yani sınıflandırma doğru ve **kararlı**; eksik olan onu **kapıya bağlamaktı** —
bugüne kadar bu liste bir **belge cümlesiydi**, bir **değişmez** değil.

⚠ **Ölçüt neden «üretimden import»**: bir modülü yalnız kendi testi import ediyorsa o
modül **çalışmıyor**, yalnız **sınanıyor**. *Bir testin bir modülü çağırması, ürünün onu
çağırdığı anlamına gelmez.*
"""

from __future__ import annotations

import ast
import pathlib

_KOK = pathlib.Path(__file__).resolve().parents[1]

#: Ayrıştırma önbelleği — kapı O(n²) olmasın (ölçüldü: önbeleksiz **2 dk+**).
_INDEKS: dict[str, set[str]] | None = None

#: Üretim ağaçları — bir modülün *«bağlı»* sayılması için buralardan import edilmeli.
#: ⚠ `tests`/`lab`/`eval` **bilerek yok**: onlar ürünü **sınar**, **koşturmaz**.
_URETIM = ("app", "admin_app", "control_plane")

#: 🔴 **MEŞRU YETİMLER — ve her birinin GEREKÇESİ.** Bu sözlük bir muafiyet listesi
#: değil, bir **beyan**dır: buraya bir ad girecekse **neden** de girer.
#: ⊙ Kaynak: `belgeler/denetim/2026-08-05_V1-SON-KONTROL.md:212` — ve bu turda kendi
#: ölçümümle **birebir** doğrulandı (138 modülün 4'ü).
YETIM_MESRU: dict[str, str] = {
    "embed_kapsam": "P0-bloke: gömme sağlayıcısı kararı verilmeden bağlanamaz",
    "kanal_kimlik": "adaptör bekliyor: teslim kanalı sözleşmesi henüz tek sağlayıcılı",
    "bayrak_profilleri": "test yardımcısı: bayrak kombinasyonlarını kurar, ürün yolu yok",
    # ⏭ `sinonim_onerici` — `§A.6/3` ile bir **çevrimdışı koşucu** kazanınca buradan
    #    ÇIKACAK. Bugün hâlâ yetim ve gerekçesi *«tasarım: offline»*.
    #    ⚠ Ama `§A.5`'in dersi: *«offline» bir ÇALIŞMA KİPİDİR, bir ÇALIŞMAMA GEREKÇESİ
    #    DEĞİL* — bu satır bir **borç kaydıdır**, bir aklama değil.
    "sinonim_onerici": "⏭ BORÇ: tasarım offline, ama koşucusu yok — `§A.6/3` ile kapanacak",
}


def _modul_adlari() -> set[str]:
    return {p.stem for p in (_KOK / "app").rglob("*.py")
            if p.stem not in {"__init__", "main"}}


def _ithal_indeksi() -> dict[str, set[str]]:
    """`dosya kökü → o dosyanın import ettiği app.* adları`. **Bir kez** ayrıştırılır.

    ⚠ İlk yazımım her modül için **tüm ağacı yeniden** ayrıştırıyordu (138 × tam tarama)
    ve kapı **2 dakikada bitmedi**. *Bir kapı, koştuğundan pahalıysa atlanan bir kapıya
    dönüşür* — `CLAUDE.md`'nin kendi dersi.
    """
    global _INDEKS
    if _INDEKS is not None:
        return _INDEKS
    idx: dict[str, set[str]] = {}
    for kd in _URETIM:
        d = _KOK / kd
        if not d.is_dir():
            continue
        for f in d.rglob("*.py"):
            try:
                agac = ast.parse(f.read_text(encoding="utf-8"))
            except SyntaxError:                        # pragma: no cover
                continue
            adlar: set[str] = set()
            for n in ast.walk(agac):
                if isinstance(n, ast.ImportFrom) and n.module and \
                        n.module.split(".")[0] == "app":
                    adlar.add(n.module.split(".")[-1])
                    adlar |= {a.name for a in n.names}
                elif isinstance(n, ast.Import):
                    adlar |= {a.name.split(".")[-1] for a in n.names
                              if a.name.startswith("app.")}
            idx.setdefault(f.stem, set()).update(adlar)
    _INDEKS = idx
    return idx


def _yetimler() -> set[str]:
    """Üretimden — **kendisi hariç** — hiç import edilmeyen modüller."""
    idx = _ithal_indeksi()
    yetim = set()
    for m in _modul_adlari():
        if not any(m in adlar for kok, adlar in idx.items() if kok != m):
            yetim.add(m)
    return yetim


def test_OLCUM_TABANI_MODUL_SAYISI_ANLAMLI():
    """⊘ **Boş yeşil avı.** Modül taraması çökerse aşağıdaki yüklem hiçbir şey ölçmez."""
    n = len(_modul_adlari())
    assert n >= 100, f"⊘ ölçüm tabanı çöktü: `app/` altında {n} modül (beklenen ≥100)"


def test_HER_MODULUN_YA_CAGIRANI_YA_GEREKCESI_VAR():
    """🔴🔴 **ASIL KAPI.** Yeni bir modül yazılıp **bağlanmazsa** burada görünür.

    ⊙ Bugün **4/138**; hepsi `YETIM_MESRU`'da **gerekçesiyle** kayıtlı. Beşincisi
    doğduğu gün bu kapı kırmızı olur ve yazan kişi **iki şeyden birini** yapmak zorunda
    kalır: ya modülü **bağlar**, ya **neden bağlanmadığını yazar**.

    *Bir modülü yazıp bağlamamak bir hata değildir; bağlamadığını söylememektir.*
    """
    beyansiz = sorted(_yetimler() - set(YETIM_MESRU))
    assert not beyansiz, (
        f"🔴 BEYANSIZ YETİM MODÜL: {beyansiz}\n"
        "Bu modüller `app/` altında duruyor ama üretim kodundan (app·admin_app·"
        "control_plane) **hiç import edilmiyor** — yani yazıldılar, bağlanmadılar.\n"
        "→ Ya bağla, ya `YETIM_MESRU`'ya **gerekçesiyle** yaz.")


def test_MESRU_LISTE_BAYATLAMIYOR():
    """⚠ Ters yön: bir modül **bağlandığı hâlde** listede kalırsa, liste bir **aklama
    kağıdına** dönüşür ve bir sonraki gerçek yetimi de örter.

    *Bir muafiyet listesi, kendini temizlemiyorsa bir muafiyet değil bir perdedir.*
    """
    yetim = _yetimler()
    bayat = sorted(set(YETIM_MESRU) - yetim)
    assert not bayat, (
        f"🔴 `YETIM_MESRU` BAYATLADI: {bayat} artık üretimden çağrılıyor — listeden "
        "çıkarılmalı. Aksi hâlde liste, gerçek yetimleri gizleyen bir perde olur.")


def test_HER_GEREKCE_DOLU():
    """⚠ Boş bir gerekçe, gerekçesizlikten kötüdür: okuyan onu **okunmuş** sanır."""
    for ad, sebep in YETIM_MESRU.items():
        assert len(str(sebep).strip()) >= 20, (
            f"🔴 `{ad}` için gerekçe yok ya da anlamsız kısa: {sebep!r}")


def test_YETIM_SAYISI_ARTMIYOR():
    """🔴 **BORÇ TAVANI.** Bugün **4**. Sayı artarsa borç büyümüş demektir — `YETIM_MESRU`'ya
    ad eklemek kapıyı yeşil yapar ama **bu yüklem** onu görünür tutar.

    ⊙ `§A.6/3` `sinonim_onerici`'yi bağlayınca beklenen sayı **3**'e düşer; azalma
    serbesttir, kapı yalnız **artışı** yasaklar.
    """
    n = len(_yetimler())
    assert n <= 4, (
        f"🔴 yetim modül sayısı {n} (tavan 4) — yeni bir modül yazılıp bağlanmamış.")
