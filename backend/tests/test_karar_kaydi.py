"""FAZ E-4 — KARAR KAYDI: Query Contract'ın bir üstü.

Query Contract *"bu sayı nasıl hesaplandı"* sorusunu cevaplar. Karar Kaydı **bir üst
soruyu** cevaplar:

> *"Bu sayıya bakarak NE KARAR VERDİK, hangi seçenekler arasından, hangi gerekçeyle,
> kim ve ne zaman?"*

BI ürünlerinde eksik olan halka budur: **rapor kalır, kararın kendisi kaybolur.** Altı ay
sonra *"bunu neden yapmıştık"* sorusunun cevabı kimsede olmaz.

## Kilitlenen üç karar

1. **Değerlendirilen TÜM seçenekler saklanır**, yalnız seçilen değil — *"neden bu?"*
   ancak *"hangilerine karşı?"* bilinirse cevaplanabilir.
2. **`content_hash` bir İMZA değil KURCALAMA TESPİTİDİR.** Anahtarlı imza, anahtar
   yönetimi demektir ve **ölçülmüş bir tehdide** dayanmadan o karmaşıklığı almak
   *"ölçülmemiş ihtiyaç için altyapı kurma"* kuralının ihlali olurdu.
3. **Append-only** — karar silinmez; revizyon `supersedes` ile yeni kayıt yazar.
"""

from __future__ import annotations

import pytest
from sqlmodel import Session, select

from app import decision
from control_plane.db import engine
from control_plane.models import DecisionRecord


@pytest.fixture(autouse=True)
def _sema():
    """Şemayı kur. `client` fixture'ı uygulama açılışında `init_db()` çağırır; DB'ye
    doğrudan dokunan BİRİM testleri o yoldan geçmez ve tablo bulamaz. Bunu `client`
    isteyerek çözmek her birim testine bir HTTP uygulaması kurdururdu."""
    from control_plane.db import init_db

    init_db()

ICERIK = {
    "question": "fire neden arttı?",
    "chosen": {"segment": "Örme Kumaş", "impact": 271490.3, "direction": "kotulesti"},
    "options": [{"segment": "Örme Kumaş", "impact": 271490.3},
                {"segment": "Dokuma", "impact": 12000.0}],
    "rationale": "Değişim yoğunlaşmış (en büyük segment brüt hareketin %100'i).",
    "note": "Örme hattında iplik değişimi denenecek.",
    "contract_ids": ["c-abc123", "c-def456"],
}


# --- HASH: kanoniklik ve kurcalama ----------------------------------------------

def test_ayni_icerik_AYNI_hash():
    """`sort_keys` + sabit ayraç: alan sırası değişse de hash aynı kalmalı — aksi halde
    her okuma "kurcalanmış" derdi ve doğrulama gürültüye dönerdi."""
    a = dict(ICERIK)
    b = {k: ICERIK[k] for k in reversed(list(ICERIK))}
    assert decision.hash_of(a) == decision.hash_of(b)


@pytest.mark.parametrize("alan,yeni", [
    ("question", "başka soru"),
    ("rationale", "başka gerekçe"),
    ("note", "başka not"),
])
def test_DEGISEN_alan_hashi_bozar(alan, yeni):
    """ASIL KAPI. Kayıt sonradan değiştirilirse hash TUTMAZ."""
    bozuk = {**ICERIK, alan: yeni}
    assert decision.hash_of(bozuk) != decision.hash_of(ICERIK)


def test_SECENEK_listesi_de_hashe_girer():
    """Değerlendirilen seçenekleri sessizce değiştirmek, kararın GEREKÇESİNİ değiştirir —
    seçilen aynı kalsa bile. Hash bunu yakalamalı."""
    bozuk = {**ICERIK, "options": [ICERIK["options"][0]]}
    assert decision.hash_of(bozuk) != decision.hash_of(ICERIK)


def test_KANIT_listesi_de_hashe_girer():
    bozuk = {**ICERIK, "contract_ids": ["c-abc123"]}
    assert decision.hash_of(bozuk) != decision.hash_of(ICERIK)


def test_hash_SURUMLU():
    """Alan listesi genişletilirse eski kayıtlar doğrulanamaz hale gelir; sürüm etiketi
    o günü ayırt edilebilir kılar."""
    assert decision.HASH_SURUMU in decision.kanonik(ICERIK)


def test_seri_edilemez_deger_PATLAMAZ():
    """`default=str` bilinçli: patlamak, kararın KAYDEDİLMEMESİ demektir ve kanıt kaybı
    kurcalama riskinden daha somut bir zarardır."""
    import datetime as dt

    assert decision.hash_of({**ICERIK, "note": dt.date(2026, 8, 2)})


# --- YAZMA ve OKUMA -------------------------------------------------------------

def _kaydet(**ek):
    return decision.kaydet(tenant_id="t1", user_id="u1", session_id="s1",
                           **{**ICERIK, **ek})


def test_kaydet_ve_DOGRULA():
    kayit = _kaydet()
    assert kayit["id"].startswith("d-") and kayit["content_hash"].startswith("sha256:")
    with Session(engine) as s:
        satir = s.exec(select(DecisionRecord)
                       .where(DecisionRecord.id == kayit["id"])).first()
    assert decision.oku_satir(satir)["verified"] is True


def test_KURCALANMIS_kayit_yakalanir():
    """ASIL KAPI. Makbuzun değeri onu KONTROL EDEBİLMEKTE; DB'de elle değiştirilen bir
    karar kaydı `verified=False` ile dönmeli."""
    kayit = _kaydet()
    with Session(engine) as s:
        satir = s.exec(select(DecisionRecord)
                       .where(DecisionRecord.id == kayit["id"])).first()
        satir.rationale = "sonradan değiştirilmiş gerekçe"
        s.add(satir)
        s.commit()
        s.refresh(satir)
    assert decision.oku_satir(satir)["verified"] is False


def test_HASHSIZ_kayit_NONE_doner():
    """`None` ile `False` FARKLI: `None` = "doğrulanamadı" (eski/bozuk satır),
    `False` = "KURCALANMIŞ". İkisini birleştirmek suçsuzu suçlu göstermek olurdu."""
    kayit = _kaydet()
    with Session(engine) as s:
        satir = s.exec(select(DecisionRecord)
                       .where(DecisionRecord.id == kayit["id"])).first()
        satir.content_hash = None
        s.add(satir)
        s.commit()
        s.refresh(satir)
    assert decision.oku_satir(satir)["verified"] is None


def test_KANIT_sayisi_okumada_gorunur():
    """"Kanıtsız" ile "kanıtlı" aynı şey değildir ve bu ayrım okumada görünmeli."""
    assert _kaydet()["evidence_count"] == 2
    assert _kaydet(contract_ids=[])["evidence_count"] == 0


def test_SUPERSEDES_zinciri():
    """Append-only: karar silinmez, revizyon yeni kayıt yazar ve eskisini gösterir."""
    ilk = _kaydet()
    yeni = _kaydet(note="revize edildi", supersedes=ilk["id"])
    assert yeni["supersedes"] == ilk["id"] and yeni["id"] != ilk["id"]


# --- UÇLAR: ikisinin de tüketicisi var (MIMARI §14.1) --------------------------

def test_UC_yaz_ve_oku(client):
    r = client.post("/decisions", json={
        "question": ICERIK["question"], "chosen": ICERIK["chosen"],
        "options": ICERIK["options"], "rationale": ICERIK["rationale"],
        "note": ICERIK["note"], "contract_ids": ICERIK["contract_ids"],
        "session_id": "e2e"})
    assert r.status_code == 200, r.text
    kayit = r.json()
    assert kayit["verified"] is True and kayit["evidence_count"] == 2

    g = client.get(f"/decisions/{kayit['id']}")
    assert g.status_code == 200
    okunan = g.json()
    assert okunan["id"] == kayit["id"] and okunan["verified"] is True
    assert okunan["options"] == ICERIK["options"], "değerlendirilen seçenekler kaybolmuş"


def test_UC_BILINMEYEN_kimlik_404(client):
    assert client.get("/decisions/d-yoktur").status_code == 404


def test_UC_BASKA_TENANT_404_doner(client):
    """403 DEĞİL 404: "yetkin yok" cevabı, kaydın VAR OLDUĞUNU sızdırır."""
    kayit = decision.kaydet(tenant_id="baska-tenant", user_id="x", session_id=None,
                            **ICERIK)
    assert client.get(f"/decisions/{kayit['id']}").status_code == 404


def test_UC_MINIMAL_govde_kabul_eder(client):
    """Kullanıcı serbest metinle de karar yazabilmeli — kanıt zorunlu DEĞİL ama
    yokluğu okumada görünür."""
    r = client.post("/decisions", json={"note": "Hattı durduruyoruz."})
    assert r.status_code == 200 and r.json()["evidence_count"] == 0
