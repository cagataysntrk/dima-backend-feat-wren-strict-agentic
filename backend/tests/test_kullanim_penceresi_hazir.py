"""FAZ 8.1 kapısı — **gerçek kullanım penceresi AÇILMAYA HAZIR MI.**
[bayraksız: KOD DEĞİL]

## 🔴 Bu kapı 8.1'i "geçemez" — ve geçtiğini iddia etmiyor

8.1'in kendisi bir **kullanım** maddesidir: *1-2 gerçek kullanıcı, 2-4 hafta, gerçek
sorular, ≥300 tur.* Hiçbir test onu yeşile çeviremez. *Bir bekleme süresini bir testle
kısaltmak mümkün olsaydı, ölçmeye gerek kalmazdı.*

Kapının ölçtüğü şey **hazırlık**: pencere açıldığında veri **gerçekten birikecek mi**.
Ve bu ayrım önemli çünkü tersi ölçülmüştü: *"~130 madde hiçbir gerçek kullanıcı görmeden
inşa ediliyordu"* (D5) — enstrümantasyonu **pencereden sonra** kurmak, ilk haftaların
verisini **geri getirilemez** biçimde kaybetmek olurdu.

## Kontrol listesi (yol haritasının kendi dört maddesi)

| # | Madde | Bu kapı ne ölçüyor |
|---|---|---|
| 1 | enstrümantasyon | `interaction_log` **varsayılan açık** · `reject_reason` **ayrı kolon** · `route-distribution` ucu **var** |
| 2 | KVKK/rıza | bildirim **kullanıcıya görünüyor** · `InteractionLog` **ham sonuç satırı tutmuyor** |
| 3 | *"gerçek soru"* ölçütü | ⊘ **kod değil** — ekip dışı, iş amaçlı |
| 4 | hedef hacim ≥300 | ⊘ **bir SAYAÇ, bir kapı değil** |

## ⚠ Bilinen ve beyan edilen kırmızı

`GET /sadmin/interactions/route-distribution` **var ama UI tüketicisi yok** — tüketicisi
FAZ **7.7**'nin *"Dima kendini nasıl geliştiriyor"* sekmesi ve o sekme **yazılmadı**.
Yani pencere açıldığında veri **birikir** ama *"LLM-free oranı aylık trendi"* ekranda
**görünmez**; rakam `admin_app`'ten okunur. Bu, kapının **beyan edilmiş kırmızısıdır**.
"""

from __future__ import annotations

from pathlib import Path

from tests.kapi_ortak import fe_dosyalari, fe_kaynak

_KOK = Path(__file__).resolve().parents[1]


# --- Madde 1: enstrümantasyon ----------------------------------------------------------

def test_INTERACTION_LOG_varsayilan_ACIK():
    """🔴 Varsayılan `False` olsaydı pencere açılır, veri **birikmezdi** — ve bunu ancak
    haftalar sonra fark ederdik. *Bir ölçümün varsayılanı, ölçümün kendisi kadar önemlidir.*
    """
    from app.config import Settings

    assert Settings.model_fields["interaction_log"].default is True


def test_REJECT_REASON_AYRI_KOLON():
    """🔴 `note`'a sıkıştırılsaydı **gruplanamazdı** — ve FAZ 0'ın çıktısı (*"en sık 20
    red gerekçesi"*) tam olarak gruplama gerektiriyor.

    ⚠ Ayrıca `note` serbest **metindir** ve `synonyms.py::mine_candidates` onu zaten
    başarısızlık açıklaması olarak okuyor: aynı alanı iki amaçla kullanmak, ikisini de
    güvenilmez yapardı.
    """
    from control_plane.models import InteractionLog

    assert "reject_reason" in InteractionLog.model_fields


def test_ROUTE_DISTRIBUTION_ucu_VAR():
    """Yol dağılımı, *"LLM-free oranı"*nın tek kaynağıdır."""
    src = (_KOK / "admin_app/routers/interactions.py").read_text(encoding="utf-8")
    assert '@router.get("/route-distribution")' in src


def test_ROUTE_DISTRIBUTION_UI_TUKETICISI_YOK_ve_bu_BEYAN_EDILIYOR():
    """🔴 **Beyan edilmiş kırmızı.** Tüketicisi FAZ 7.7'nin paneli ve o **yazılmadı**.

    ⚠ Bu testin yönü bilinçli olarak **ters**: bugün tüketici yok ve kapı bunu
    **doğruluyor**. Panel yazıldığı gün bu test kırmızı olur — ve o kırmızı, *"beyanı
    güncelle"* demektir. *Bayat bir muafiyet, muafiyeti olmayan bir uçtan tehlikelidir,
    çünkü sessizce doğru görünür.*
    """
    assert "route-distribution" not in fe_kaynak(), (
        "🔴 Frontend artık `route-distribution` tüketiyor — FAZ 7.7 paneli inmiş demektir. "
        "Bu testi ve `OPERASYON-DURUM.md`'deki 'beyan edilmiş kırmızı' satırını GÜNCELLE.")


# --- Madde 2: KVKK / bildirim ----------------------------------------------------------

def test_KAYIT_BILDIRIMI_KULLANICIYA_gorunuyor():
    """🔴 *Bir veriyi toplamaya başladığın an, toplandığını söylemen gereken andır —
    sonra değil.* Ölçüldü: bildirim **hiçbir yerde yoktu** ve `interaction_log`
    **varsayılan açıktı**."""
    src = fe_dosyalari()["components/KayitBildirimi.tsx"]
    assert "kaydediliyor" in src
    assert "<KayitBildirimi />" in fe_dosyalari()["components/Landing.tsx"], (
        "🔴 Bildirim boş durumda gösterilmiyor — kullanıcı ilk sorusunu **bilmeden** sorar.")


def test_BILDIRIM_NE_KAYDEDILMEDIGINI_de_soyluyor():
    """🔴 Yalnız *"kayıt tutuluyor"* demek, kullanıcıya **en kötüyü varsaydırır**:
    *"demek ki verilerim de saklanıyor."* Oysa `InteractionLog` ham sonuç satırı tutmaz."""
    src = fe_dosyalari()["components/KayitBildirimi.tsx"]
    assert "Sonuç satırlarınız kaydedilmez" in src


def test_INTERACTION_LOG_HAM_SONUC_tutmuyor():
    """⚠ Bildirimin doğru olması, **şemanın** onu doğrulamasına bağlıdır. *Bir gizlilik
    beyanı, kodla desteklenmiyorsa bir taahhüt değil bir risktir.*"""
    from control_plane.models import InteractionLog

    # 🔴 Yasak **ada değil, TAŞIDIĞI ŞEYE** konur — ve bu ayrım ölçümle öğrenildi: ilk
    # sürüm `"rows"` adını yasakladı ve `rows: int | None`u yakaladı. O bir **sayaçtır**,
    # satırların kendisi değil. *Bir kuralı ada bağlamak, onu türden bağımsız yapar ve
    # doğru bir şemayı kırmızıya boğar.*
    #
    # Ölçüt: sonuç **yükü** ancak `str`/`bytes`/`list`/`dict` bir alanda taşınabilir.
    # Bir tam sayı, ne kadar çok satır döndüğünü söyler; **hangi satırlar** olduğunu değil.
    supheli = {"rows", "result", "result_rows", "data", "sonuc", "satirlar", "sample_rows",
               "sample_rows_json", "result_json"}
    catisan = []
    for ad in supheli & set(InteractionLog.model_fields):
        ann = InteractionLog.model_fields[ad].annotation
        if ann in (int, type(None)) or "int" in str(ann):
            continue  # sayaç — yük değil
        catisan.append(f"{ad}: {ann}")
    assert not catisan, (
        f"🔴 `InteractionLog` sonuç YÜKÜ taşıyan alan(lar) kazanmış: {catisan}. "
        f"Kullanıcıya verilen 'sonuç satırlarınız kaydedilmez' sözü ARTIK YANLIŞ.")


def test_BILDIRIM_KAPATILSA_da_METIN_kaliyor():
    """⚠ *Bir bildirimi kapatmak, onu geri alınamaz biçimde silmek olmamalı.*"""
    assert "Sorularınız ürünü geliştirmek için kaydediliyor" in \
        fe_dosyalari()["components/HelpPanel.tsx"]


def test_BILDIRIM_RIZA_gibi_DAVRANMIYOR():
    """🔴 Bir onay kutusu koymak, arkasında **gerçekten kaydı durduran** bir yol olmadan
    **yanlış beyandır**. Bildirim kapatmanın kaydı durdurmadığını **söylüyor**."""
    src = fe_dosyalari()["components/KayitBildirimi.tsx"]
    assert "kaydı durdurmaz" in src
    assert "DIMA_INTERACTION_LOG=false" in src, (
        "🔴 Kaydı durdurma yolu söylenmiyor — bir sınırı söylemeden koymak, onu bir "
        "sırra çevirir.")


def test_BILDIRIM_HYDRATION_tuzagina_dusmuyor():
    """⚠ `useState(() => localStorage…)` sunucuda `window` olmadığı için ilk render'ı
    istemciden **ayrıştırır**. Okuma effect'te yapılmalı."""
    src = fe_dosyalari()["components/KayitBildirimi.tsx"]
    assert "useEffect(() => {" in src
    assert "useState(false)" in src


# --- Madde 3 ve 4: kod DEĞİL -----------------------------------------------------------

def test_HEDEF_HACIM_bir_SAYAC_bir_KAPI_DEGIL():
    """⊘ *Bir bekleme süresini bir testle kısaltmak mümkün olsaydı, ölçmeye gerek
    kalmazdı.* ≥300 tur bir **sayaçtır**; bu dosya onu yeşile çeviremez ve çevirdiğini
    iddia etmez."""
    doc = __doc__ or ""
    assert "bir SAYAÇ, bir kapı değil" in doc
    assert "geçemez" in doc
