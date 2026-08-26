"""FAZ C4 — `app/yoy.py`: 93 satır, **sıfır doğrudan test**, dört üretim tüketicisi.

`app/report.py`, `app/routers/dashboards.py`, `/ask` (iki yerde) ve dolaylı olarak
`app/contribution.py` (çıktı şekline bağımlı) bu modüle güveniyordu ve hiçbiri onu izole
sınamıyordu. Denetimde (2 Ağustos 2026) *"sessiz-yanlış üretmeye en müsait modül"* diye
işaretlenmişti; şüphenin gerekçesi tek satırdı:

    shift = 1 if mode == "yoy" else 1   # iki dal AYNI

## Kanıtlanan kusur

`_merge`, önceki dönem satırlarını cari döneme hizalamak için anahtarın **yılını** kaydırır.
YoY'da doğru (2025-03 → +1 yıl → 2026-03). **MoM'da imkânsız**: önceki ay 2026-02'dir ve
yılı kaydırmak onu 2027-02 yapar — cari 2026-03 ile hiçbir zaman eşleşmez.

Ölçüldü (düzeltme öncesi):

| Mod | Zaman kolonu | `_gecen` |
|---|---|---|
| yoy | var | `100` ✓ |
| **mom** | **var** | **`None`** ✗ |
| mom | yok (boyut kırılımı) | `200` ✓ |

Yani *"geçen aya göre aylık ciro"* sorusu **sessizce boş bir kıyas kolonu** döndürüyordu —
hata yok, uyarı yok, yalnız veri yok. Boyut kırılımında çalıştığı için kusur gözden
kaçmıştı.
"""

from __future__ import annotations

import datetime as dt

import pytest

from app.yoy import _merge, time_dim_of

# --- hizalama: asıl kusur --------------------------------------------------------

CUR = [{"tarih": "2026-03-01", "ciro": 300}]


@pytest.mark.parametrize("mod,prev,beklenen", [
    ("yoy", [{"tarih": "2025-03-01", "ciro": 100}], 100),
    ("mom", [{"tarih": "2026-02-01", "ciro": 200}], 200),
])
def test_zaman_serisinde_HIZALAMA(mod, prev, beklenen):
    """ASIL KAPI. MoM'da `_gecen` hep `None` geliyordu."""
    rows, _cols = _merge(CUR, prev, ["ciro"], [], mod)
    assert rows[0]["ciro_gecen"] == beklenen, (
        f"{mod}: önceki dönem hizalanamadı — kıyas sessizce boş döner")


def test_mom_YIL_SINIRINI_asar():
    """Ocak'ın önceki ayı bir ÖNCEKİ YILIN Aralık'ıdır. Ay kaydırması yıl devrini
    yönetmezse yılbaşı kıyasları sessizce boşalır."""
    rows, _ = _merge([{"tarih": "2026-01-01", "ciro": 300}],
                     [{"tarih": "2025-12-01", "ciro": 200}], ["ciro"], [], "mom")
    assert rows[0]["ciro_gecen"] == 200


def test_yoy_ARTIK_YIL_29_subat():
    """29 Şubat'ın bir önceki yıl karşılığı yoktur; eşleşmemeli ama PATLAMAMALI."""
    rows, _ = _merge([{"tarih": "2024-02-29", "ciro": 300}],
                     [{"tarih": "2023-02-28", "ciro": 200}], ["ciro"], [], "yoy")
    assert rows[0]["ciro_gecen"] is None


def test_gunluk_seride_mom():
    """Günlük seri + MoM: 15 Şubat ↔ 15 Mart (ayın günü korunur)."""
    rows, _ = _merge([{"tarih": "2026-03-15", "ciro": 300}],
                     [{"tarih": "2026-02-15", "ciro": 200}], ["ciro"], [], "mom")
    assert rows[0]["ciro_gecen"] == 200


def test_date_NESNESI_de_hizalanir():
    """`WrenService.query` Arrow `to_pylist()` döndürür → gerçek `date` nesneleri gelir."""
    rows, _ = _merge([{"tarih": dt.date(2026, 3, 1), "ciro": 300}],
                     [{"tarih": dt.date(2025, 3, 1), "ciro": 100}], ["ciro"], [], "yoy")
    assert rows[0]["ciro_gecen"] == 100


# --- boyut kırılımı (zaman kolonu yok) — bozulmamalı -----------------------------

@pytest.mark.parametrize("mod", ["yoy", "mom"])
def test_boyut_kiriliminda_BOZULMADI(mod):
    """Zaman kolonu yokken anahtar yalnız boyutlardır; düzeltme burayı etkilememeli
    (kusur zaten burada YOKTU ve bu yüzden gözden kaçmıştı)."""
    rows, _ = _merge([{"makine": "A", "ciro": 300}], [{"makine": "A", "ciro": 200}],
                     ["ciro"], ["makine"], mod)
    assert rows[0]["ciro_gecen"] == 200


def test_eslesmeyen_satir_NONE_birakir():
    """Geçen dönemde karşılığı olmayan satır (yeni makine) `None` almalı — 0 DEĞİL.
    0 yazmak "geçen dönem sıfırdı" demektir ve %değişimi sonsuz/yanıltıcı yapar."""
    rows, _ = _merge([{"makine": "YENİ", "ciro": 300}], [{"makine": "A", "ciro": 200}],
                     ["ciro"], ["makine"], "yoy")
    assert rows[0]["ciro_gecen"] is None and rows[0]["ciro_degisim_yuzde"] is None


def test_yuzde_degisim_ve_SIFIRA_BOLME():
    rows, _ = _merge([{"m": "A", "v": 150}], [{"m": "A", "v": 100}], ["v"], ["m"], "yoy")
    assert rows[0]["v_degisim_yuzde"] == 50.0
    rows, _ = _merge([{"m": "A", "v": 150}], [{"m": "A", "v": 0}], ["v"], ["m"], "yoy")
    assert rows[0]["v_degisim_yuzde"] is None, "sıfıra bölme sızdı"


def test_KAYAN_NOKTA_ARTIGI_ANLAMSIZ_YUZDE_URETMEZ():
    """🔴 `§K2` **ASIL DEĞİŞMEZ.** Dengelenmesi beklenen (borç−alacak≈0) bir ölçü
    tam `0` değil, kayan-nokta artığı (`4.65e-10`) döndürebilir — `p == 0`
    koruması bunu YAKALAMAZ (Python'da `4.65e-10` truthy'dir). Ölçüldü (canlı,
    `mizan.bakiye`): iki gürültü-seviyesi sayı arasında *"%100 arttı"* gibi
    anlamsız bir yüzde üretiyordu. ⚠ Ölçü adı bilinçli olarak `mizan`/`bakiye`
    DEĞİL — bu eşik domain-agnostik olmalı, herhangi bir ölçüde geçerli."""
    rows, _ = _merge([{"m": "A", "net_etki": 9.313225746154785e-10}],
                     [{"m": "A", "net_etki": -4.656612873077393e-10}],
                     ["net_etki"], ["m"], "yoy")
    assert rows[0]["net_etki_degisim_yuzde"] is None, (
        "🔴 kayan-nokta artığı gerçek bir taban değeriymiş gibi kullanıldı")


def test_ZIT_OLCUT_NORMAL_BUYUKLUKTE_DEGER_HALA_HESAPLANIR():
    """🆃 Kapının kurbanı: eşiği çok büyük tutup HER küçük-ama-gerçek değeri de
    `None`'a çevirmek de yeşil kalırdı. `0,01` gibi küçük ama **gerçek** bir
    taban değer hâlâ normal şekilde hesaplanmalı — yalnız gürültü elenir."""
    rows, _ = _merge([{"m": "A", "v": 0.02}], [{"m": "A", "v": 0.01}], ["v"], ["m"], "yoy")
    assert rows[0]["v_degisim_yuzde"] == 100.0, "🔴 gerçek küçük değer de elendi"


def test_kolon_duzeni():
    """`contribution.py` `<measure>_gecen` adına BAĞIMLI — ad sözleşmesi kilitlenir."""
    _rows, cols = _merge([{"m": "A", "v": 1}], [{"m": "A", "v": 1}], ["v"], ["m"], "yoy")
    assert "v_gecen" in cols and "v_degisim_yuzde" in cols


def test_bos_seriler_PATLAMAZ():
    assert _merge([], [], ["v"], ["m"], "yoy")[0] == []
    rows, _ = _merge([{"m": "A", "v": 1}], [], ["v"], ["m"], "yoy")
    assert rows[0]["v_gecen"] is None


# --- time_dim_of -----------------------------------------------------------------

def test_time_dim_of_cubeden_okur(schema):
    """`kpi.py` bu fonksiyonu kullanmıyordu ve zaman kolonunu `"tarih"` diye SABİT
    kodluyordu (Faz C3) — `donem_tarih` kullanan cube'larda yanlış pencere kuruyordu."""
    assert time_dim_of(schema, "parti") == "tarih"
    assert time_dim_of(schema, "ik") == "donem_tarih"
    assert time_dim_of(schema, "bilinmeyen_cube") == "tarih", "yedek 'tarih' olmalı"


# --- FAZ C3: kpi.py'nin sabit zaman kolonu ---------------------------------------

def test_kpi_serisi_ZAMAN_KOLONUNU_beyan_edebilir():
    """`resolve_kpi_series` zaman kolonunu ÜÇ yerde `"tarih"` diye sabit kodluyordu.
    KPI'ın dayandığı view farklı bir zaman kolonu taşıyorsa (`donem_tarih`) sorgu ya
    patlar ya da — ad tesadüfen varsa — SESSİZCE YANLIŞ PENCERE kurar.

    ⚠️ **Uçtan uca gösterilemiyor:** demo-boyahane'de KPI tanımı YOK (ölçüldü: 0) ve
    `resolve_kpi_series`'in üretimde çağıranı da yok (`_try_kpi` "bu turda MİNİMAL:
    yalnız SKALER kart" diye açıkça erteliyor). Bu yüzden sahte bir servisle SQL'in
    kendisi denetlenir — iddia edilen değil üretilen sorgu.
    """
    from app.kpi import resolve_kpi_series

    sorgular: list[str] = []

    class _SahteSvc:
        def query(self, sql, limit=None):
            sorgular.append(" ".join(sql.split()))
            if "MIN(" in sql:                      # aralık sorgusu
                return {"rows": [{"mn": "2026-01-01", "mx": "2026-03-01"}]}
            return {"rows": [{"value": 1}]}        # bileşen sorgusu

    spec = {"name": "t", "requires_views": ["mizan_src"], "time_column": "donem_tarih",
            "formula": "a", "components": {"a": {"sql": "SELECT 1 AS value FROM x {where}"}}}
    resolve_kpi_series(_SahteSvc(), spec, "month")
    assert sorgular, "hiç sorgu üretilmedi"
    assert any("MIN(donem_tarih)" in q for q in sorgular), \
        f"zaman kolonu beyanı yok sayıldı: {sorgular[0][:120]}"
    assert not any("MIN(tarih)" in q for q in sorgular), "sabit `tarih` hâlâ üretiliyor"


def test_kpi_serisi_beyan_YOKSA_tarih_kullanir():
    """Geriye uyum: beyan edilmemiş KPI'lar bugünkü davranışı korumalı."""
    from app.kpi import resolve_kpi_series

    sorgular: list[str] = []

    class _SahteSvc:
        def query(self, sql, limit=None):
            sorgular.append(" ".join(sql.split()))
            if "MIN(" in sql:
                return {"rows": [{"mn": "2026-01-01", "mx": "2026-02-01"}]}
            return {"rows": [{"value": 1}]}

    resolve_kpi_series(_SahteSvc(), {"name": "t", "requires_views": ["v"], "formula": "a",
                                     "components": {"a": {"sql": "SELECT 1 AS value FROM x {where}"}}},
                       "month")
    assert any("MIN(tarih)" in q for q in sorgular)
