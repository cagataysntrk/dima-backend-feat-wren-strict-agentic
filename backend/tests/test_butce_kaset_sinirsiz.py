"""🔴 SONSUZ BİR BÜTÇE, SONSUZ BİR `timeout` DEĞİLDİR — ölçülmüş bir ürün kusuru.

`butce.kos` kaset modunda (`DIMA_KASET=kayit|oynat`) bütçeyi bilerek `inf` yapıyor
(*«bir ölçümün aleti, ölçtüğü şeyi kısaltmamalıdır»* — karar doğru). Ama `inf` bir
`timeout` **sayısı** olarak `Future.result()`'a geçince `threading`'in
`waiter.acquire(True, inf)`'ine düşüyor:

    OverflowError: timestamp out of range for platform time_t

⊙ **Ölçülen sonuç aletin kendi amacını yiyordu:** kaset altında her bütçeli paralel
koşum patlıyor, çağıranın `except`'i yutuyor ve kütükte yalnız *«LLM Intent-JSON
seçimi başarısız (best-effort)»* kalıyordu — yani **garsonun `k=3` oylaması kaset
altında hiç koşmuyordu**, kasetli garson korpusunun ölçmek için var olduğu tam o
basamak. Kayıt turunda **16 kez** sayıldı (2026-08-11).
"""

import os

from app.butce import ASIM, kos


def test_kaset_modunda_sonsuz_butce_PATLAMAZ(monkeypatch):
    """🔴 Kusurun ta kendisi: eskiden `OverflowError` fırlatıyordu."""
    monkeypatch.setenv("DIMA_KASET", "oynat")
    assert kos([lambda: "a", lambda: "b"], saniye=0.001, ad="t") == ["a", "b"]


def test_kayit_modunda_da_PATLAMAZ(monkeypatch):
    monkeypatch.setenv("DIMA_KASET", "kayit")
    assert kos([lambda: 1], saniye=0.0, ad="t") == [1]


def test_kaset_DISINDA_butce_HALA_KESER(monkeypatch):
    """⚠ Düzeltme bir gevşetme DEĞİL: kaset dışında duvar-saati koruması yerinde.

    Bütçe, kullanıcı beklemesin diye vardır; yalnız **ölçüm** turunda bekleyen bir
    kullanıcı yoktur.
    """
    monkeypatch.delenv("DIMA_KASET", raising=False)
    import time

    out = kos([lambda: time.sleep(5) or "geç"], saniye=0.05, ad="t")
    assert out == [ASIM], "kaset dışında bütçe kesmeliydi"


def test_kaset_bayragi_okunmayan_deger_ise_normal_butce(monkeypatch):
    """Kapalı küme: yalnız `kayit`/`oynat` sınırsızdır — başka değer bütçeyi açmaz."""
    monkeypatch.setenv("DIMA_KASET", "belkide")
    import time

    assert kos([lambda: time.sleep(5) or "geç"], saniye=0.05, ad="t") == [ASIM]


def test_govde_inf_i_timeout_olarak_GECIRMEZ():
    """Kapı: `inf` bir daha `timeout` olarak geçirilmesin (regresyon kilidi)."""
    import inspect

    import app.butce as b

    kaynak = inspect.getsource(b.kos)
    assert "timeout=None if _sinirsiz" in kaynak, (
        "sonsuz bütçe `timeout=None` ile ifade edilmeli — `inf` OverflowError verir")
    assert os.environ.get("DIMA_KASET") in (None, "", "kayit", "oynat", "belkide")
