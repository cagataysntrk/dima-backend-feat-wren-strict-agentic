"""FAZ 0.6 — VQR ham-SQL replay'inde şema-sürüm kapısı.

`always_filter` (LookML `sql_always_where` karşılığı) cube düzeyinde tanımlanır ve
`WrenService.cube_sql()` onu ÜRETİLEN HER SQL'e enjekte eder — `CANCELLED = 0` gibi bir
iş kuralının ölçü ifadelerinde tekrarlanmasını önler ve iptal kayıtlarının toplama
sızmasını YAPISAL olarak engeller. Enjeksiyon `_inject_always_filter` içinde FAIL-CLOSED'dır.

Ama `_inject_always_filter` yalnız `cube_sql()` ve `blend_sql()` yolundadır. HAM SQL
çalıştıran yollar ondan geçmez. Bunlardan biri VQR replay'idir ve en sinsisidir:

    1. Bir soru Discovery'den ham SQL ile cevaplanır ve VQR'a "doğrulanmış" olarak yazılır.
    2. Sonra o cube'a `always_filter` eklenir (ya da bir ölçü tanımı değişir).
    3. Aynı soru tekrar sorulur → VQR birebir eşleşir → ESKİ ham SQL aynen oynatılır.
       Yapısal yol filtreyi uygular, VQR yolu UYGULAMAZ: aynı soru, iki farklı sayı.
       Ve yanlış olanı `source="vqr"` rozetiyle, "doğrulanmış" güveniyle sunulur.

`dry_plan` bunu YAKALAYAMAZ — SQL sözdizimsel olarak hâlâ geçerlidir; değişen şey
anlamdır. Tek güvenilir sinyal MDL sürümüdür (ADR-0010'un sözleşme damgasıyla aynı).

Kapı: ham-SQL kayıtları yazılırken `mdl_version` damgalanır; replay'de damga güncel
sürümle eşleşmiyorsa (ya da HİÇ YOKSA) kısayol atlanır ve soru normal merdivenden
cevaplanır. Kayıp yalnız bir önbellek isabetidir; kazanç, kanıtlayamadığımız bir cevabı
"doğrulanmış" diye sunmamaktır. Kayıt bir sonraki başarılı cevapta damgalı olarak
yeniden öğrenilir — kendi kendini onarır.
"""

from __future__ import annotations

import pytest

from tests.conftest import ask

Q = "vqr surum kapisi icin ozel soru"
SQL = "SELECT 1 AS x"


@pytest.fixture()
def vqr_store(client):
    """Aktif tenant'ın VQR deposu (conftest izole geçici dosyaya yönlendirir)."""
    from app.main import create_app  # noqa: F401 - uygulama zaten ayakta

    return client.app.state.vqr


def _mdl_version(client) -> str:
    return client.app.state.wren.mdl_version


def test_ham_sql_kaydi_mdl_version_ile_damgalanir(client, vqr_store):
    """Discovery/verify yolundan yazılan her ham-SQL kaydı sürüm damgası taşımalı."""
    vqr_store.store(Q, {"wren_sql": SQL, "mdl_version": _mdl_version(client)},
                    source="auto")
    hit = vqr_store.near_exact(Q)
    assert hit, "kayıt bulunamadı"
    assert hit["cube_query"].get("mdl_version") == _mdl_version(client)


def test_guncel_damgali_kayit_replay_EDILIR(client, vqr_store):
    vqr_store.store(Q, {"wren_sql": SQL, "mdl_version": _mdl_version(client)},
                    source="auto")
    d = ask(client, Q)
    assert d["source"] == "vqr", f"güncel kayıt oynatılmadı: {d.get('source')}"
    assert d["sql"] == SQL


def test_bayat_damgali_kayit_replay_EDILMEZ(client, vqr_store):
    """MDL değişmişse eski ham SQL 'doğrulanmış' sayılamaz — kısayol atlanır."""
    vqr_store.store(Q, {"wren_sql": SQL, "mdl_version": "bayat000000"}, source="auto")
    d = ask(client, Q)
    assert d.get("source") != "vqr", (
        "bayat VQR kaydı oynatıldı — always_filter/ölçü değişimi sessizce atlanabilir"
    )


def test_damgasiz_ESKI_kayit_replay_EDILMEZ(client, vqr_store):
    """Damgası olmayan kayıtların geçerliliği KANITLANAMAZ; bayat sayılırlar.

    Bu, kapının eklenmesinden önce yazılmış tüm kayıtları bir kez geçersiz kılar —
    bilinçli tercih: kanıtlanamayan bir cevabı 'doğrulanmış' diye sunmaktansa yeniden
    hesaplamak yeğdir. Kayıtlar sonraki başarılı cevapta damgalı olarak geri gelir.
    """
    vqr_store.store(Q, {"wren_sql": SQL}, source="auto")
    d = ask(client, Q)
    assert d.get("source") != "vqr"


def test_cube_query_kayitlari_ETKILENMEZ(client, vqr_store):
    """Kapı YALNIZ ham-SQL kayıtları içindir.

    CubeQuery kayıtları her replay'de `cube_sql()`'den yeniden derlenir, dolayısıyla
    güncel `always_filter`'ı ve lehçeyi ZATEN alırlar — onları sürüm damgasıyla
    geçersiz kılmak gereksiz bir önbellek kaybı olurdu.
    """
    # NOT: `store()` CubeQuery kayıtlarından tarih filtrelerini DÜŞÜRÜR (sorgu ŞEKLİ
    # öğrenilir, dönem her mesajdan yeniden çözülür) — bu yüzden soru metninin kendisi
    # bir dönem taşımalı, yoksa `_period_gate` netleştirme chip'i döndürür.
    q = "vqr surum kapisi icin ozel cube sorusu bu yil"
    cq = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}
    vqr_store.store(q, cq, source="chip_approved")
    d = ask(client, q)
    assert d["source"] == "vqr", f"CubeQuery kaydı gereksiz yere atlandı: {d.get('source')}"
    assert (d.get("cube_query") or {}).get("cube") == "oee"
