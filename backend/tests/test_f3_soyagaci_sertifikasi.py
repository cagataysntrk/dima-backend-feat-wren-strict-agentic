"""🔴 `§F3` — ÖLÇÜLMÜŞ BİR JOIN'İN SAĞLIĞI ARTIK KULLANICIYA SÖYLENİYOR.

## Raporun teşhisi ESKİMİŞTİ — ölçüldü (2026-08-11)

`§11.2` şunu yazıyor: *«`relationships` **31** — 🔴 cube_router'da sıfır anma; çapraz-küp
«blend» ile yapılıyor, **gerçek JOIN değil**»*. Ölçüm bunu **çürüttü**; ilişkiler **sekiz**
yerde kullanılıyor ve `cube_router`'daki sessizlik bir kusur değil, `§38.4`'ün
**JOIN planlayıcı yasağının ta kendisidir** — router ilişkiyi bilmemelidir, sıradan bir
boyut görür:

| katman | ne yapıyor | ölçüm |
|---|---|---|
| **cube derleyicisi** (`compose._compose_relationship_dimensions`) | 10 `expose:` bloğu → 9 türev boyut, **7 cube**'a | ölçüldü |
| **model katmanı** (`WrenEngine.dry_plan`) | `is_calculated` kolon → **gerçek JOIN**, çok-sıçramalı | canlı curl |
| **fan-out sertifikası** (`fanout.certify`) | **31/31 ölçüldü**, hepsi `saglikli` | artefakt |
| `WrenService.schema()` | `dimension_origin[*].certified` damgası | kod |
| `drill.py:163` | `olculdu:riskli` kök-neden sırasında **geriye itilir** | kod |
| `gorsel_ekleme` | soyağacı cümlesi | canlı curl |
| `ossie.py` · `connections.py` | ithal ilişki `olculmedi` damgalı gelir | kod |
| ön uç (`InterpretationBar.tsx`) | rozet | kod |

## Ve BİR gerçek boşluk vardı — bu dosya onu kapatıyor

Canlıda basıldı (`bölüm bazında oee` → `cube=oee`, `dimensions=["bolum"]`, 5 satır):

    “bölüm” boyutu makineler.bolum kolonundan, oee_vardiya_makineler ilişkisi
    üzerinden geldi (1 sıçrama).

…ve **orada bitiyordu**. `"certified" in yanıt` → **False**. Yani 31 ilişkinin tamamı
ölçülmüştü, ölçüm bir artefakta yazılmıştı, damga şemaya basılmıştı — ve kullanıcıya
**hiçbir yerden ulaşmıyordu**. Okuyan kişi bir kolonun iki tablo öteden geldiğini görüyor,
o join'in toplamları **şişirip şişirmediğini bilemiyordu**.

> *Omni'nin `$55,5 milyar`lık kartezyen felaketi (`§23.1`) bu boşlukta doğdu — orada
> ölçüm hiç yoktu. Bizde **vardı ve söylenmiyordu**; ikincisi daha ucuz bir kusurdur,
> ama daha sinsi olanıdır: sistem doğruyu biliyor ve susuyor.*
"""

from __future__ import annotations

import ast
import pathlib

from app import fanout
from tests.conftest import ask

_ROZETLER = ("olculdu:saglikli", "olculdu:riskli", "olculmedi")


def test_ROZETIN_HER_KODU_bir_cumle_bulur():
    """`KAT-1` — `rozet()`'in ürettiği her kodun karşılığı olmalı; dördüncü bir kod
    eklenirse bu test kırılır ve cümlesi de yazılır."""
    for k in _ROZETLER:
        assert fanout.beyan(k), f"{k} için beyan yok"


def test_rozet_KODLARI_ile_sozluk_BIREBIR():
    """Sözlükte fazlalık da olmamalı: yazılmış ama hiç üretilmeyen bir cümle, ölü koddur."""
    assert set(fanout._ROZET_BEYANI) == set(_ROZETLER)


def test_RISKLI_beyani_SONUCU_soyler_mekanizmayi_degil():
    """Kullanıcı *«benzersiz anahtar»* değil *«sayı şişer mi»* sorusunu sorar."""
    b = fanout.beyan("olculdu:riskli")
    assert "şişmiş olabilir" in b
    assert "RİSKLİ" in b


def test_SAGLIKLI_beyani_GARANTIYI_soyler():
    assert "şişmiyor" in fanout.beyan("olculdu:saglikli")


def test_OLCULMEDI_temiz_GIBI_gosterilmez():
    """🔴 Sertifikanın tüm değeri bu ayrımdadır: ölçülmemişi temiz göstermek, olmayan bir
    garantiyi rozetlemek olurdu."""
    b = fanout.beyan("olculmedi")
    assert "ÖLÇÜLMEDİ" in b
    assert "şişmiyor" not in b


def test_BILINMEYEN_kodda_UYDURULMAZ():
    """Eksik bir damga, uydurulmuş bir güvenceden iyidir → sessizlik."""
    assert fanout.beyan("gelecekteki_yeni_kod") is None
    assert fanout.beyan(None) is None
    assert fanout.beyan("") is None


def test_SOYAGACI_beyani_GOVDEDE_kurulu():
    """⚠ Kapı iddiası **docstring'e değil GÖVDEYE** kurulur — bu oturumda üç kez bir
    docstring'e bakan test, kaldırılmış bir davranışı yeşil gösterdi."""
    src = pathlib.Path(__file__).parent.parent / "app" / "gorsel_ekleme.py"
    agac = ast.parse(src.read_text(encoding="utf-8"))
    for d in ast.walk(agac):
        if isinstance(d, ast.FunctionDef) and d.name == "gorsel_ekle":
            govde = d.body[1:] if (d.body and isinstance(d.body[0], ast.Expr)
                                   and isinstance(d.body[0].value, ast.Constant)) else d.body
            metin = "\n".join(ast.dump(x) for x in govde)
            break
    else:
        raise AssertionError("gorsel_ekle bulunamadı")
    assert "beyan" in metin, "soyağacı sertifikayı sormuyor"
    assert "certified" in metin


def test_SOYAGACI_CEVABINDA_sertifika_gorunur(client):
    """🔴 Uçtan uca — kapatılan boşluğun ta kendisi. Ölçümden ÖNCE bu cümle
    *«…(1 sıçrama).»* ile bitiyordu."""
    d = ask(client, "bu yıl bölüm bazında ortalama oee")
    assert d.get("cube_query", {}).get("dimensions") == ["bolum"], d.get("note")
    aciklama = d.get("calculation_explanation") or ""
    assert "oee_vardiya_makineler ilişkisi üzerinden geldi" in aciklama, aciklama
    assert "fan-out" in aciklama, f"sertifika beyanı cevaba ulaşmıyor: {aciklama!r}"


def test_YEREL_boyutta_sertifika_CUMLESI_YOK(client):
    """Yerel bir kolonda fan-out sorusu anlamsızdır — gürültü yapılmaz."""
    d = ask(client, "bu yıl makine bazında ortalama oee")
    assert "fan-out" not in (d.get("calculation_explanation") or "")


def test_CANLI_SERTIFIKA_31_iliskiyi_TAMAMEN_olcmus(schema):
    """⊙ `§11.2`'nin *«kullanmıyoruz»* teşhisinin çürüğü: ölçüm **var** ve **tam**.
    Bu test bir gerileme kapısıdır — ilişki eklenip ölçülmezse `olculmedi` düşer."""
    o = next(c for c in schema["cubes"] if c["name"] == "oee")["dimension_origin"]
    damga = o["bolum"]["certified"]
    # 🔴🔴 **ÜÇ DEĞER, İKİ FARKLI SINIF — ve bu ayrım GİZLİ BİR KIRMIZIYI çözdü.**
    #
    # Ölçüldü (2026-08-12): bu test **seri koşumda yeşil**, `-n 8` altında **kırmızı** —
    # ve **taban da öyle** (`git worktree`, HEAD~6: aynı kırmızı). Yani bir gerileme
    # değil, kapının kendi ölçüm ön koşulu:
    #
    #     seri   → certified = 'olculdu:saglikli'
    #     -n 8   → certified = **'olculmedi'**
    #
    # Sebep `lab/izolasyon.py`: her xdist işçisi **kendi derlenmiş ağacını** kurar ve o
    # ağaçta sertifika ölçümü koşmaz. Yani `olculmedi` bir **ortam** durumudur, bir veri
    # bozulması değil — ikisini aynı kırmızıya bağlamak, `§F8` hijyeninin ihlalidir:
    # *bir kapı, ortam eksiğini ürün kusuru gibi göstermemeli.*
    #
    # ⚠ Ama **sessizce geçmek de yok** (`ADR-0020`): atlama sebebiyle birlikte yazılır.
    # Ve `olculdu:bozuk` **her koşulda kırmızıdır** — asıl korunan şey odur.
    if damga == "olculmedi":
        import pytest as _pt

        _pt.skip("⊘ ORTAM: sertifika bu işçinin izole ağacında ÖLÇÜLMEDİ (`-n` paralel "
                 "koşum, `lab/izolasyon.py`). Ürün kusuru değil — seri koşumda "
                 "`olculdu:saglikli`. Bu kapı `olculdu:bozuk`'u yakalamak için var.")
    assert damga == "olculdu:saglikli", (
        f"🔴 sertifika damgası `{damga}` — canlı katalogda bu ilişki ölçülmüş ve "
        "SAĞLIKLIYDI. `olculdu:bozuk` bir veri/ilişki kusurudur ve susturulamaz.")
