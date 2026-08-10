"""FAZ 1.0 — `parti` cube'u VIEW yerine MODEL tabanlı: mekanizma + fan-out kilidi.

`parti`, `parti_zengin` adlı elle yazılmış bir SQL view'ına bağlıydı (partiler ⟕ personel ⟕
personel_ozluk). Gerekçesi view'ın kendi başlığında yazılıydı: *"calc field'lar
cube_query_to_sql'de JOIN'lenmiyor → demografiyi VIEW'da denormalize ederiz."*

O inancın İLK YARISI doğru, çıkarılan SONUÇ yanlıştı (bkz. backend/MIMARI.md §3.2):
cube derleyicisi gerçekten JOIN üretmez, ama MODEL KATMANI (`WrenEngine.dry_plan`) ilişki
handle'ı + `is_calculated` kolon üzerinden JOIN'i OTOMATİK ve ÇOK-SIÇRAMALI enjekte eder.
`models_enrich.yml` gerekli calc kolonlarını (operator_cinsiyet/departman/egitim/
dogum_tarihi) ZATEN üretiyordu — hiçbir cube onları okumuyordu, öksüz duruyorlardı.

Bu dosya iki şeyi kalıcı kılar:
  (a) geçişin geri alınmadığını (base_object bir MODEL olmalı),
  (b) asıl DEĞİŞMEZİ: ilişki üzerinden gelen bir boyutla kırılım yapmak toplamı
      DEĞİŞTİRMEZ. Fan-out olsaydı sayılar şişerdi ve cevap `source="cube"` rozetiyle
      gelirdi — sistemin üretebileceği en kötü hata sınıfı.

(b) kasıtlı olarak view'a atıf yapmadan yazıldı: view kaldırıldığında (Faz 2) da geçerli
kalır. Geçişin kendisi ayrıca 26 noktada view sürümüyle birebir karşılaştırılarak
doğrulandı (10 ölçü kırılımsız · 14 boyut × 2 ölçü · demografi × ay · yaş × departman).
"""

from __future__ import annotations

import pytest

DEMOGRAFI = ["cinsiyet", "departman", "egitim", "yas_grubu"]


@pytest.fixture(scope="module")
def parti(schema):
    cube = next((c for c in schema["cubes"] if c["name"] == "parti"), None)
    assert cube, "parti cube'u katalogda yok"
    return cube


def test_base_object_MODEL_olmali_view_degil(parti, schema):
    """Geçiş geri alınırsa burada görünür."""
    base = parti["base_object"]
    assert base == "partiler", f"base_object geri alınmış: {base!r}"
    model_adlari = {m["name"] for m in schema.get("models", [])}
    assert base in model_adlari, f"{base!r} bir MODEL değil (view'a geri dönülmüş olabilir)"


def test_demografi_boyutlari_hala_yayinlaniyor(parti):
    eksik = [d for d in DEMOGRAFI if d not in parti["dimensions"]]
    assert not eksik, f"demografi boyutları kayboldu: {eksik}"


@pytest.mark.parametrize("dim", DEMOGRAFI)
def test_iliski_uzerinden_kirilim_TOPLAMI_DEGISTIRMEZ(client, dim):
    """ASIL DEĞİŞMEZ — fan-out kilidi.

    `partiler → personel` join'i `operator = ad_soyad` üzerinden kuruluyor; `ad_soyad`
    bir PRIMARY KEY DEĞİL. Bugün benzersiz (ölçüldü) ama bu bir VERİ özelliğidir, şema
    garantisi değil: aynı adı taşıyan ikinci bir personel eklenirse join çoğaltır ve
    SUM'lar şişer — hatasız, uyarısız, `source="cube"` rozetiyle.

    Kırılımlı toplam = kırılımsız toplam olmalı.
    """
    from tests.conftest import ask

    # ⟳🔴 **SORU TEKNİK ADLA SORULUYORDU — ve KAZARA çalışıyordu.**
    #
    # ⊙ Ölçüldü (`§EB`, 2026-08-10): `yas_grubu` sorusu yalnız `grubu` token'ı üzerinden
    # eşleşiyordu; o token **iki boyutun etiketinden** türemiş bir belirsizlikti
    # (`ham_grup` ∩ `yas_grubu`) ve *«renk grubuna göre fire»* sorusuna **personel yaş
    # grubunu** sokuyordu. Belirsizlik kaldırılınca bu kapı kırmızıya döndü — yani
    # yıllardır bir **kusur sayesinde** geçiyormuş.
    #
    # ⚠ Ve teknik adı sinonim yapmak **ölçülüp reddedildi**: gerçek-dünya korpusunda
    # `sessiz_yanlis` **12 → 18** (`§EB/A`, `§99.1`'in tekrarı). Teknik ad kullanıcının
    # konuşmadığı bir kelimedir.
    #
    # 🔴 Doğru soru **kullanıcının yazacağı** biçimdir: boyutun **etiketi**. Kapının
    # sözleşmesi değişmedi (*kırılımlı toplam = kırılımsız toplam*); yalnız o sözleşmeyi
    # **gerçek bir yoldan** sınıyor. *Bir kapıyı teknik adla sürmek, ürünün konuşmadığı
    # bir dilde test etmektir.*
    _etiket = {"yas_grubu": "yaş grubu", "cinsiyet": "cinsiyet",
               "departman": "departman", "egitim": "eğitim"}.get(dim, dim)
    duz = ask(client, "bu yıl işlenen kg")
    kirilimli = ask(client, f"bu yıl {_etiket} bazında işlenen kg")

    assert duz.get("result"), f"kırılımsız sorgu cevap vermedi: {duz.get('note')}"
    assert kirilimli.get("result"), f"{dim} kırılımı cevap vermedi: {kirilimli.get('note')}"
    assert kirilimli["cube_query"]["cube"] == "parti"
    assert dim in (kirilimli["cube_query"].get("dimensions") or []), (
        f"{dim} boyutu cube_query'ye girmedi: {kirilimli['cube_query']}"
    )

    def _toplam(d):
        # `WrenService.query` satırları SÖZLÜK döndürür (Arrow `to_pylist()`), liste değil.
        return round(sum(r["toplam_agirlik_kg"] for r in d["result"]["rows"]
                         if r.get("toplam_agirlik_kg") is not None), 2)

    assert _toplam(kirilimli) == _toplam(duz), (
        f"FAN-OUT: {dim} kırılımı toplamı değiştirdi "
        f"({_toplam(kirilimli)} != {_toplam(duz)}) — join çoğaltıyor"
    )


def test_join_YALNIZCA_iliski_boyutu_istendiginde_uretilir(schema):
    """Join pruning: ilişki boyutu istenmeyen sorgu JOIN üretmemeli.

    Bu, Faz 1'in maliyet varsayımının temeli — manifesti ilişki-türevi kolonlarla
    zenginleştirmek, o kolonlar İSTENMEDİKÇE sorgu maliyeti doğurmaz.
    """
    from app.config import get_settings
    from app.wren_service import WrenService

    svc = WrenService(get_settings().resolved_project_dir(), datasource="duckdb",
                      connection_info=get_settings().connection_dict())

    yerel = svc.dry_plan(svc.cube_sql(
        {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["makine"]}))
    iliskili = svc.dry_plan(svc.cube_sql(
        {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["cinsiyet"]}))

    assert yerel.upper().count(" JOIN ") == 0, "yerel boyut gereksiz JOIN üretti"
    assert iliskili.upper().count(" JOIN ") >= 1, "ilişki boyutu JOIN üretmedi"


def test_iki_sicramali_boyut_calisir(client):
    """`yas_grubu` 2 sıçrama gerektirir: partiler → personel → personel_ozluk
    (doğum tarihi özlükte). Çok-sıçramalı çözümün canlı kanıtı."""
    from tests.conftest import ask

    d = ask(client, "bu yıl yaş grubu bazında işlenen kg")
    assert d.get("result"), f"2-sıçramalı boyut cevap vermedi: {d.get('note')}"
    gruplar = {r["yas_grubu"] for r in d["result"]["rows"]}
    assert gruplar & {"<30", "30-39", "40-49", "50+"}, f"beklenmeyen yaş grupları: {gruplar}"
