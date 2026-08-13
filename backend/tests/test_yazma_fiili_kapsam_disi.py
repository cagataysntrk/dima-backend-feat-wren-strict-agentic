"""🔴 `§28.3` **satır 4** — *«yazma fiili → senkron onay»*: bugün **konusu yok**, ve bu
bir eksik değil **ölçülmüş bir sınırdır** ㊸. Bu kapı o sınırı **zincire bağlar** ㉕.

## Ölçüm (2026-08-13)

| ne | değer |
|---|---|
| kapalı fiil kümesi | **15** fiil |
| yazan fiil | **0** — `PANO` bile *«hiçbir şey kaydetmez, yalnız taslak»* |
| koşucuda `INSERT`/`UPDATE`/`commit` | **0** |
| SQL guard | `SELECT`/`WITH` dışını **reddeder** (`UnsafeSqlError`) |

Yani `§28.3`'ün dördüncü satırı bugün **uygulanamaz**, çünkü uygulanacağı bir fiil yok.
Bunu *«yapıldı»* diye işaretlemek yalan, *«yapılmadı»* diye bırakmak eksik olurdu 🆂.

> ㉖ *«Kapı yok» ≠ «boşluk var».* Doğrusu üçüncü seçenek: **kapsamı ilan et ve o kapsam
> değiştiği an haber veren bir tel ger.**

## Bu kapının üç yüklemi

| # | savunulan |
|---|---|
| 1 | fiil kümesi **kayıtlı olanla aynı** — yeni fiil `§28.3.4`'ü yeniden açar |
| 2 | koşucu **yazmıyor** (salt-okunur ve idempotent) |
| 3 | 🆃 ölçüt **gerçekten** yazma arıyor — sahte bir yeşil değil |

⚠ Birincisi bilerek **katıdır**: bir fiil eklemek meşru bir iştir, ama bu kapıyı kırar ve
kıran kişi *«bu fiil yazıyor mu? yazıyorsa senkron onay nerede?»* sorusunu **cevaplamadan**
geçemez. *Bir kararı belgeye yazmak onu hatırlatmaz; bir kapıya yazmak hatırlatır.*
"""

from __future__ import annotations

import pathlib

from app import plan_kosucu
from app.plan_semasi import FIILLER

#: Ölçülen küme (`§69`, 2026-08-13). ⚠ **Bir liste değil bir FOTOĞRAF**: değiştiği an
#: `§28.3` satır 4 yeniden sorulur.
KAYITLI = {
    "SORGU", "KIYASLA", "AYRISTIR", "BAGLA", "HESAPLA", "TREND", "ANLAT",
    "KIR", "SUZ", "BOYUTSEC", "MATRIS", "SIRALA", "RAPOR", "GORSEL", "PANO",
}


def test_FIIL_KUMESI_DEGISMEDI():
    """🔴 **ASIL DEĞİŞMEZ** ㉕ — küme büyürse `§28.3.4` kararı **yeniden** verilmeli."""
    assert set(FIILLER) == KAYITLI, (
        f"🔴 kapalı fiil kümesi değişti: eklenen={set(FIILLER) - KAYITLI} · "
        f"çıkan={KAYITLI - set(FIILLER)}\n"
        "YAPILACAK: yeni fiil **yazıyor mu**? Yazıyorsa `§28.3` satır 4 (*«yazma fiili → "
        "senkron onay»*) uygulanmadan yayına çıkamaz; yazmıyorsa bu kapının fotoğrafını "
        "güncelle ve `ONGORU-DURUM.md`'ye **neden** yazmadığını yaz 🅖.")


def test_KOSUCU_YAZMIYOR():
    """Çalıştırıcı **salt-okunur ve idempotent**: ilk yan etkili fiil bu değişmezi kırar."""
    kaynak = pathlib.Path(plan_kosucu.__file__).read_text(encoding="utf-8")
    govde = "\n".join(l for l in kaynak.split("\n") if not l.lstrip().startswith("#"))
    for yasak in ("INSERT ", "UPDATE ", "DELETE ", ".commit()"):
        assert yasak not in govde, (
            f"🔴 koşucuda yazma izi: {yasak!r} — `§28.3` satır 4 artık **zorunlu**")


def test_ZIT_OLCUT_OLCUT_GERCEKTEN_YAZMA_ARIYOR():
    """🆃 Kapının kurbanı: hiçbir şey aramayan bir ölçüt de yeşil kalırdı."""
    sahte = "def kaydet():\n    oturum.commit()\n"
    govde = "\n".join(l for l in sahte.split("\n") if not l.lstrip().startswith("#"))
    assert ".commit()" in govde, "🔴 ölçüt yazma izini göremiyor — kapı sahte"
