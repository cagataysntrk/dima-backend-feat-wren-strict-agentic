"""FAZ 7.3(k) kapısı — **B8 ZİNCİRİ BAĞLANDI.** [bayrak: `metrik_sertifikasi`]

## 🔴 Ölçüm yol haritasını düzeltti

7.3(k) *"sarı drift bandı — **B8'in TEK kullanıcı-görünür yüzeyi**; arkası kurulu, önü
yoktu"* diyordu. Ölçüldü: **arkası da kurulu değildi.** Beş halka vardı ve **hiçbiri
diğerine dokunmuyordu**:

| halka | vardı | bağlıydı |
|---|---|---|
| `metrik_sertifikasi` tablosu | ✅ | 🔴 **hiçbir okuyucu yok** |
| `app/certification.py` (12 test) | ✅ | 🔴 **hiçbir çağıran yok** |
| `Explain.sertifika` (`schemas.py`) | ✅ | 🔴 **hiçbir dolduran yok** |
| `Explain.sertifika` (TypeScript) | 🔴 **tipte bile yoktu** | — |
| `sertifikaRozeti()` (`ChatPanel`) | ✅ | 🔴 **hiçbir çağıran yok** |

> 🔴 *Bir zincirin her halkasını ayrı ayrı test etmek, zinciri test etmek değildir.*

⚠ **Ve bu sınıf yalnız B8'de değil:** aynı gün koşan denetim `app/`'in 86 modülünden
**12'sinin** üretim kodunda hiç import edilmediğini ölçtü (~1.470 satır). Bu kapı
o sınıfın **birinci** kapanışını kilitliyor.

## Bu kapı NEYİ ölçüyor — ve neyi ölçemediğini söylüyor

Ölçtüğü: **her halkanın bir sonrakine dokunduğu**. Ölçemediği: gerçek bir tenant'ta
gerçek bir sertifika satırıyla uçtan uca akış — o, canlı bir DB ve bir onay ister.
**⊘ ÖLÇÜLEMEDİ** ve gizlenmiyor.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.kapi_ortak import fe_dosyalari, fe_kaynak

_KOK = Path(__file__).resolve().parents[1]


# --- Halka 1-2: tablo → certification -------------------------------------------------

def test_HALKA_1_TABLOYU_okuyan_VAR():
    """🔴 `MetrikSertifikasi`'nin **hiçbir okuyucusu yoktu** — tablo bir beyandı."""
    from app import sertifika_okuma

    kaynak = (_KOK / "app/sertifika_okuma.py").read_text(encoding="utf-8")
    assert "MetrikSertifikasi" in kaynak
    assert hasattr(sertifika_okuma, "kayittan_oku")


def test_HALKA_1_TENANT_ZORUNLU():
    """🔴 `tenant_id` olmadan bir sertifika okuması, **başka bir şirketin onayını** bu
    şirkete gösterirdi."""
    from app import sertifika_okuma

    assert sertifika_okuma.kayittan_oku(None, None, "parti.toplam_ciro") is None
    assert sertifika_okuma.kayittan_oku(None, "t1", "") is None


def test_HALKA_2_CERTIFICATION_cagriliyor():
    """🔴 `certification.py` 12 testli ve **çağıranı yoktu**."""
    kaynak = (_KOK / "app/sertifika_okuma.py").read_text(encoding="utf-8")
    assert "certification.durum(" in kaynak
    assert "certification.rozet_kademesi(" in kaynak


def test_KADEME_BACKENDDE_hesaplaniyor():
    """⚠ Rozet kademesi bir **karardır**; iki sahibi olursa ayrışır. Arayüz yalnız
    gösterir."""
    from app import sertifika_okuma

    blok = sertifika_okuma.blok({"seviye": "sertifikali"})
    assert blok is not None and "kademe" in blok


def test_METRIK_REF_UYDURULMUYOR():
    """⚠ Uydurma bir referans, olmayan bir sertifikayı *"bulunamadı"* diye gösterirdi —
    ve o, *"hiç sertifikalanmamış"*tan farklı okunurdu."""
    from app import sertifika_okuma

    assert sertifika_okuma.metrik_ref(None) is None
    assert sertifika_okuma.metrik_ref({"cube": "parti"}) is None
    assert sertifika_okuma.metrik_ref({"measures": ["x"]}) is None
    assert sertifika_okuma.metrik_ref({"cube": "parti", "measures": ["x"]}) == "parti.x"


# --- Halka 3: Explain.sertifika dolduruluyor -----------------------------------------

def test_HALKA_3_SEAL_sertifikayi_DOLDURUYOR():
    """🔴 Alan `schemas.py`'de FAZ 1.5'ten beri vardı ve **dolduranı yoktu**.

    ⚠ Yeri `seal()`: sertifika bir **mühürleme** kararıdır ve `ask()` tavanı 1150/1151 —
    oraya bir çağrı eklemek tavanı aşardı.
    """
    kaynak = (_KOK / "app/answer.py").read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    seal = next(n for n in agac.body
                if isinstance(n, ast.FunctionDef) and n.name == "seal")
    govde = ast.unparse(seal)
    assert "resp.explain.sertifika" in govde, "🔴 `seal()` sertifikayı doldurmuyor"
    assert "metrik_sertifikasi" in govde, "🔴 bayrağa bağlı değil (KURAL B)"


def test_HALKA_3_ASKRESPONSE_DEGIL_EXPLAIN():
    """🔴 İlk yazımda `resp.sertifika` yazdım ve Pydantic **çalışma zamanında**
    `ValueError: "AskResponse" object has no field "sertifika"` dedi.

    *Bir alanın hangi modele ait olduğunu "yakınında duruyor" diye varsaymak*, bu
    zincirin **beşinci** kopukluğuydu.
    """
    from app.schemas import AskResponse, Explain

    assert "sertifika" in Explain.model_fields
    assert "sertifika" not in AskResponse.model_fields


def test_KURAL_B_bayrak_kapaliyken_DOKUNULMUYOR():
    """Kapalıyken `explain.sertifika` **hiç üretilmez** → yanıt bugünküyle birebir."""
    kaynak = (_KOK / "app/answer.py").read_text(encoding="utf-8")
    i = kaynak.index('"metrik_sertifikasi" in resolve_for')
    assert "resolve_for" in kaynak[i - 400:i + 400]


def test_SERTIFIKA_CEVABI_DUSURMUYOR():
    """⚠ Bir rozet, cevabın kendisini riske atamaz."""
    kaynak = (_KOK / "app/answer.py").read_text(encoding="utf-8")
    i = kaynak.index("resp.explain.sertifika")
    assert "except Exception:" in kaynak[i:i + 800]


def test_PARMAK_IZLERI_BUGUNKU_semadan():
    """🔴 Kayıttaki hash'i yeniden kullanmak, kıyası **kendisiyle** yapmak olurdu ve
    hiçbir çürüme asla görünmezdi."""
    kaynak = (_KOK / "app/answer.py").read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    fn = next(n for n in agac.body
              if isinstance(n, ast.FunctionDef) and n.name == "_sertifika_blogu")
    govde = ast.unparse(fn)
    assert "certification.tanim_hash(" in govde and "certification.koken_hash(" in govde


# --- Halka 4-5: TypeScript tipi + arayüz ---------------------------------------------

def test_HALKA_4_TIPTE_var():
    """🔴 `Explain.sertifika` TypeScript'te **hiç yoktu** — arayüz onu göremezdi."""
    src = fe_dosyalari()["lib/types.ts"]
    i = src.index("export interface Explain")
    blok = src[i:i + 1400]
    assert "sertifika?" in blok, "🔴 `Explain` tipinde `sertifika` yok"
    assert "yeniden_dogrulama_gerekli" in blok


def test_HALKA_5_ROZET_cagriliyor():
    """🔴 `sertifikaRozeti()` **export edilmiş ama hiç çağrılmamıştı**."""
    assert fe_kaynak().count("sertifikaRozeti") >= 2, (
        "🔴 `sertifikaRozeti` hâlâ yalnız TANIMLI — çağıranı yok.")


@pytest.mark.parametrize("dosya", ["components/ReportCard.tsx", "components/ChatPanel.tsx",
                                   "components/AnalysisCanvas.tsx"])
def test_UC_ROZET_TUKETICISININ_hepsi_sertifikayi_GECIRIYOR(dosya):
    """*Bir yüzeyi iki yerde bağlayıp üçüncüsünü bırakmak, kullanıcıya aynı cevabın iki
    farklı güvencesini gösterir.*"""
    assert "sertifika={" in fe_dosyalari()[dosya]


# --- Bant: uyarı ile etiket AYRI ------------------------------------------------------

def test_BANT_YALNIZ_UYARI_kademesinde():
    """⚠ Sağlam bir sertifika için bant açmak, uyarıyı **sıradanlaştırırdı** — ve
    sıradanlaşan bir uyarı okunmaz."""
    src = fe_dosyalari()["components/SertifikaBandi.tsx"]
    assert "if (!s?.yeniden_dogrulama_gerekli) return null;" in src


def test_ROZET_UYARIYI_gostermiyor():
    """🔴 *Bir uyarıyı bir etiketin içine sıkıştırmak, onu bir etikete indirger.*"""
    src = fe_dosyalari()["components/ChatPanel.tsx"]
    assert 'sertifika.kademe !== "uyari"' in src


def test_BANT_ONAYIN_SILINMEDIGINI_soyluyor():
    """🔴 *"Hiç onaylanmamış"* ile *"onaylanmış ama tanım değişmiş"* farklı şeylerdir —
    ve ikincisi **daha bilgilendiricidir**."""
    assert "Onay silinmedi" in fe_dosyalari()["components/SertifikaBandi.tsx"]


def test_BANT_COZEMEYECEGI_EYLEMI_vaat_etmiyor():
    """🔴 Yol haritası *"«yeniden doğrula» düğmesi"* diyordu; **düğme konmadı** ve gerekçe
    kodda yazılı: yeniden doğrulama bir **yetki kararıdır** ve sahibi metrik sahibidir,
    cevabı okuyan kişi değil. Buraya bir düğme koymak **onaysız bir onay** üretirdi.

    ⚠ Bir maddeyi uygulamamak bir **karardır** ve kararın yeri koddur.
    """
    from tests.kapi_ortak import frontend_dir

    ham = (frontend_dir() / "components/SertifikaBandi.tsx").read_text(encoding="utf-8")
    assert "onaysız bir onay" in ham, "🔴 uygulanmayan maddenin gerekçesi yazılı değil"
    assert "<button" not in fe_dosyalari()["components/SertifikaBandi.tsx"], (
        "🔴 bantta düğme var — onaysız bir onay yüzeyi")


def test_BILINMEYEN_NEDEN_gizlenmiyor():
    """⚠ *Bir uyarının anlaşılmaz yarısını atmak, uyarının tamamını eksik yapar.*"""
    assert "NEDEN_METNI[n] ?? n" in fe_dosyalari()["components/SertifikaBandi.tsx"]


def test_BACKEND_SINIRI_ekrana_TASINIYOR():
    """⚠ Çok ölçülü cevapta sertifika **ilk** ölçüden okunur. Kullanıcı hangi ölçü
    hakkında uyarıldığını bilmeden karar veremez."""
    assert "KISIT_COK_OLCU" in (_KOK / "app/sertifika_okuma.py").read_text(encoding="utf-8")
    assert "s.kisit" in fe_dosyalari()["components/SertifikaBandi.tsx"]


def test_BANT_yeni_PANEL_acmadi():
    """K5 13/13."""
    from tests.test_panel_sayisi import DESEN

    assert not DESEN.findall(fe_dosyalari()["components/SertifikaBandi.tsx"])


def test_OLCULEMEYEN_kisim_YAZILI():
    """⊘ Gerçek tenant + gerçek sertifika satırıyla uçtan uca akış canlı DB ister."""
    assert "⊘ ÖLÇÜLEMEDİ" in (__doc__ or "")
