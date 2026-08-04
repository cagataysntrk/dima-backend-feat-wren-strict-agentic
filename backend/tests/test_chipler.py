"""FAZ 5.4 kapısı — **eksik chip'ler: `mom` · `dün` · Top-N.** [bayraksız: ucuz kazanç]

## Ölçülen boşluk — üçü de "motor var, chip yok"

| yetenek | motoru | chip'i |
|---|---|---|
| `compare: "mom"` | ✅ `_ACIK_KIYAS = ("yoy", "mom")`, `compare_mode()` çözüyor | ❌ yalnız `yoy` |
| `order`/`limit` (Top-N) | ✅ NL'den çözülüyor (*"en çok satan 5 müşteri"*) | ❌ hiç |

🔴 **Sıfır motor işi.** Bu faz yeni bir yetenek açmaz; **var olanı erişilebilir** kılar.

## 🔴 Bu fazın ölçülmüş tuzağı: chip'i eklemek onu GÖRÜNÜR kılmıyor

İlk denemede iki chip eklendi ve **ikisi de hiç görünmedi**: tavan (`_MAX_NEXT_STEPS=6`)
düz birleştirmede her zaman **son kategorileri** kesiyordu. *Görünmeyen bir chip, olmayan
bir chiptir.* Çözüm tavanı yükseltmek (ölçülmemiş bir UI kararı) değil, kategorileri
**sırayla** temsil etmek oldu.
"""

from __future__ import annotations

import pytest

from app import cube_router as cr


@pytest.fixture(scope="module")
def _idx(schema):
    return {c["name"]: c for c in schema.get("cubes") or []}


def _cq(gran: str | None = None, dims=("makine",), order=None):
    q = {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": list(dims)}
    if gran:
        q["timeDimensions"] = [{"dimension": "tarih", "granularity": gran}]
    if order:
        q["order"] = order
    return q


def test_MOM_chipi_AYLIK_raporda_uretilir(_idx):
    """🔴 `mom` motoru vardı, chip'i yoktu — *çalışan bir yetenek keşfedilemezdi*."""
    chipler = cr.suggest_next_steps(_cq("month"), _idx)
    kiyas = [c for c in chipler if (c["cube_query"] or {}).get("compare")]
    assert kiyas, "kıyas chip'i hiç üretilmedi"
    assert kiyas[0]["cube_query"]["compare"] == "mom", (
        "🔴 Aylık bir raporda doğal kıyas **geçen aydır**. `yoy` basmak, kullanıcıya "
        "bağlamına uymayan bir öneri vermektir.")


def test_YOY_chipi_GRANULERSIZ_raporda_uretilir(_idx):
    """⚠ İkisini yan yana basmak çözüm değildi: tavan yüzünden ikincisi **hiç görünmüyordu**."""
    chipler = cr.suggest_next_steps(_cq(None), _idx)
    kiyas = [c for c in chipler if (c["cube_query"] or {}).get("compare")]
    assert kiyas and kiyas[0]["cube_query"]["compare"] == "yoy"


def test_TOPN_chipi_uretilir_ve_GORUNUR(_idx):
    """🔴 NL'i tam, chip'i yoktu. Ve eklemek yetmiyordu — **görünmesi** gerekiyordu."""
    chipler = cr.suggest_next_steps(_cq("month"), _idx)
    topn = [c for c in chipler if c["kind"] == "order"]
    assert topn, (
        "🔴 Top-N chip'i üretilmedi YA DA tavana takılıp kesildi. *Görünmeyen bir chip, "
        "olmayan bir chiptir* — bu fazın ölçülmüş tuzağı tam olarak buydu.")
    cq = topn[0]["cube_query"]
    assert cq["limit"] == 5
    assert cq["order"][0]["id"] == "toplam_fire_kg" and cq["order"][0]["desc"] is True


def test_TOPN_SIRALI_raporda_TEKRAR_onerilmez(_idx):
    """*Kullanıcının zaten yaptığı şeyi tekrar teklif etmek, bir öneri değildir.*"""
    chipler = cr.suggest_next_steps(
        _cq("month", order=[{"id": "toplam_fire_kg", "desc": True}]), _idx)
    assert not [c for c in chipler if c["kind"] == "order"]


def test_TOPN_KIRILIMSIZ_raporda_onerilmez(_idx):
    """Kırılım yoksa tek satır döner — **sıralanacak bir şey yoktur**."""
    chipler = cr.suggest_next_steps(_cq("month", dims=()), _idx)
    assert not [c for c in chipler if c["kind"] == "order"]


def test_BES_KATEGORI_de_TEMSIL_edilir(_idx):
    """🔴 *Bir chip listesi bir KEŞİF mekanizmasıdır; keşfedilmesi gerekeni göstermelidir.*

    Düz birleştirme, kullanıcının **zaten bildiğini** (kırılım) tekrar teklif edip
    **bilmediğini** (sıralama, kıyas) hiç göstermiyordu.
    """
    kindler = {c["kind"] for c in cr.suggest_next_steps(_cq("month"), _idx)}
    assert {"dimension", "measure", "time", "order"} <= kindler, (
        f"🔴 Kategoriler temsil edilmiyor: {sorted(kindler)}. Round-robin bozulmuş "
        f"olabilir ve son kategoriler yine tavana kurban gidiyordur.")


def test_TAVAN_YUKSELTILMEDI():
    """⚠ Sorun chip **sayısı** değil **çeşitliliğiydi**; tavanı yükseltmek ölçülmemiş
    bir UI kararı olurdu."""
    assert cr._MAX_NEXT_STEPS == 6


def test_HER_CHIP_tam_bir_cube_query_tasir(_idx):
    """Chip tıklanınca `/cube` ile **0 LLM** koşar — eksik bir sorgu bunu kırardı."""
    for c in cr.suggest_next_steps(_cq("month"), _idx):
        cq = c["cube_query"]
        assert cq.get("cube") and cq.get("measures"), f"eksik cube_query: {c['label']}"
        assert "_ad" not in c, "iç alan sızdı"
