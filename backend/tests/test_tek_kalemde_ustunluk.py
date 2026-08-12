"""🔴🔴 TEK KALEMDE **ÜSTÜNLÜK YAZILMAZ** — bir sıralama en az iki şey ister.

## Ölçülen kusur (canlı curl ×3, 2026-08-12)

    «pompa arızası kaç kere oldu»
      cq: filters = [ariza_tipi eq "pompa arızası", …]
          dimensions = ["ariza_tipi"]          ← üç koşumun İKİSİNDE
      özet: «**En yüksek arıza tipi: pompa arızası** (26 adet).»

Üçüncü koşumda `dimensions` gelmedi ve özet şu oldu: *«Arıza sayısı 26 adet.»*

⊙ **Aynı soru · aynı sayı (26) · iki farklı cümle** — biri doğru, biri **yapılmamış bir
kıyası ima ediyor**. Kullanıcı zaten tek bir tipe süzmüştü; sıralanacak ikinci bir tip
hiç yoktu.

## ⚠ Ve bu kural zaten VARDI — yalnız yarısına uygulanmıştı

`_rank_facts` içindeki `pay` satırı aynı şeyi **payda** çözüyor ve gerekçesi canlı bir
kullanıcı şikâyeti:

> *«toplamın %100.0'i»* → kullanıcı: *«boş laf — tek yıl tabii ki %100»*

Kural payda uygulanmış, **başlıkta** uygulanmamıştı.

> *Bir üstünlük iddiası, kıyaslayacak ikinci bir şey yoksa bir iddia değil bir süstür —
> ve süs, hesaplanmışla doldurulmuşu ayırt edilemez kılar.*

## Rapor iddiası da ölçüldü — ve bayat çıktı

`§` *«pompa arızası self-consistency %33, `bilinmeyen=pompa`»*: canlıda **üç koşumun
üçünde de** `cube=bakim` · `measures=['ariza_sayisi']` · `ariza_tipi eq "pompa arızası"`
· **26 adet**. Terim çözülüyor; ayrışan tek şey **kırılımın varlığı**, yani sayı değil
**cümle**. Bu dosya o kalan farkı kapatır.
"""

from __future__ import annotations

from app import anlatici
from app.interpret import _rank_facts, interpret


def test_TEK_GRUPTA_USTUNLUK_YOK_TEK_DEGER_VAR():
    """🔴 Kusurun ta kendisi."""
    f = _rank_facts([{"ariza_tipi": "pompa arızası", "ariza_sayisi": 26}],
                    "ariza_tipi", "ariza_sayisi", "adet")
    assert [x["type"] for x in f] == ["single"], (
        f"🔴 tek grupta hâlâ sıralama yazılıyor: {[x['type'] for x in f]} — "
        "*bir üstünlük iddiası, kıyaslayacak ikinci bir şey yoksa bir süstür.*")
    assert "En yüksek" not in f[0]["text"], f"yapılmamış kıyas ima ediliyor: {f[0]['text']}"
    assert "26" in f[0]["text"], "sayı kayboldu — susturma değil DÜZELTME isteniyordu"


def test_IKI_GRUPTA_SIRALAMA_AYNEN_KALIR():
    """⊘ Ön koşul: düzeltme kapsamı yutmadı (`KURAL B`)."""
    f = _rank_facts([{"m": "RAM-2", "v": 70.0}, {"m": "RAM-3", "v": 40.0}], "m", "v", None)
    tipler = [x["type"] for x in f]
    assert tipler == ["top", "bottom"], tipler
    assert "En yüksek" in f[0]["text"] and "En düşük" in f[1]["text"]


def test_UC_GRUPTA_PAY_da_KALIR():
    """Pay yalnız çok kalemde yazılır — o kural zaten vardı, bozulmadı."""
    f = _rank_facts([{"m": "a", "v": 50.0}, {"m": "b", "v": 30.0}, {"m": "c", "v": 20.0}],
                    "m", "v", None)
    assert "toplamın" in f[0]["text"], "çok kalemde pay yazılmalı"


def test_TEK_GRUP_TIPI_TANINIYOR():
    """🔴 `single` `anlatici.TANINAN` içinde olmalı — değilse düzeltme, cevabı sessizce
    LLM'e gönderirdi (bu oturumun `§D11-b` dersi: *bir yinelenme/tip, sayan her kuralı
    yanıltır*)."""
    assert "single" in anlatici.TANINAN
    assert "single" in anlatici._ONCELIK


def test_UCTAN_UCA_TEK_GRUP_SABLONDA_KALIR():
    """Uçtan uca: süzülmüş tek tipli bir kırılım şablonla anlatılabilmeli (0 LLM)."""
    res = {"columns": ["ariza_tipi", "ariza_sayisi"],
           "rows": [{"ariza_tipi": "pompa arızası", "ariza_sayisi": 26}], "row_count": 1}
    cq = {"cube": "bakim", "measures": ["ariza_sayisi"], "dimensions": ["ariza_tipi"],
          "filters": [{"dimension": "ariza_tipi", "operator": "eq",
                       "value": "pompa arızası"}]}
    y = interpret(res, cq) or {}
    metin = (y.get("summary") or "") + " ".join(f.get("text", "") for f in y.get("facts") or [])
    assert "En yüksek" not in metin, f"🔴 uçtan uca hâlâ uydurma kıyas: {metin!r}"
    assert "26" in metin
    assert anlatici.basit_mi(y) is True, (
        "🔴 tek gruplu cevap şablona düşmüyor — gereksiz bir LLM çağrısı doğar.")
