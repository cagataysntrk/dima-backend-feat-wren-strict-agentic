"""FAZ 0.21 — **MODÜL BÜYÜME KAPISI.** Borç büyümesini durdurur; küçültmeyi zorlamaz.

## Neden

`ask()` **tek fonksiyon** ve gövdesi **2.052 ham satır / 19 iç fonksiyon**. FAZ 0/2/5/6'nın
neredeyse her maddesi oraya dokunuyor ve depo **paylaşılan bir dizinde** — yani bu fonksiyon
aynı zamanda bir **çakışma jeneratörü**. Ve `K3`'ün kusuru tam bu boyuttan doğuyor: iki bin
satırlık bir gövdede bir çağrının **yanlış `if`in içinde** olduğu **görünmüyor**.

⚠ **Bilinçle *"şimdi refactor et"* DENMİYOR.** Büyük refactor'ün kazancı **ölçülmedi**;
kapı refactor'ü **zorlamadan** borcun büyümesini durdurur. Maliyeti **bir test dosyası**.

🔴 **Bu bir TAVAN, bir HEDEF değil.** Küçültmek serbesttir ve ayrı bir maddedir; bu dosya
yalnız *"buradan yukarı çıkma"* der.

## 🔴 BİRİM KARARI — ve onu belirleyen ölçüm

Kapı **ham satır saymaz, KOD satırı sayar** (yorum ve docstring hariç). Sebep tahmin değil,
ölçüm (`c3fcfe7` → `a41f981`):

| | ham satır | **kod satırı** |
|---|---|---|
| `ask.py` | 3991 → 4035 (**+44**) | 2394 → 2406 (**+12**) |
| `cube_router.py` | 3565 → 3592 (**+27**) | 1723 → 1736 (**+13**) |

Yani FAZ 0'ın `ask.py`'ye kattığı ham satırın **%73'ü belgelemedir**. Ham satır sayan bir
kapı, bu depoda **ölçülmüş kusurların kaydedildiği mekanizmayı** vergilendirirdi — ve
geliştiriciyi *"yorumu silersem kapı yeşile döner"* diye ödüllendirirdi. Bu belge kültürünü
kapıyla cezalandırmak, kapının korumaya çalıştığı bilgiyi yok etmek olurdu.
*(`cube_router.py` bugün **%52 belge**; ham sayıya bakan bir okuyucu modülü iki kat büyük sanır.)*

## Neden `ask()` FONKSİYONU, `ask.py` DOSYASI değil

Zarar dosyada değil **fonksiyonda**: 19 iç fonksiyon **aynı kapsamı paylaşıyor**. Kodu
`ask()`'ten çıkarıp aynı dosyada modül düzeyine almak **istenen** yöndür — dosya kapısı
onu **cezalandırırdı**. Yine de dosya bütünü **kod satırı** üzerinden sınırlı: yoksa
`ask()` küçülürken dosyanın geri kalanı sessizce şişerdi.

## FAZ 0 MUAFİYETLERİ — madde madde, gerekçeli

Tavan **FAZ 0 ÖNCESİ** ölçümden (`c3fcfe7`) alınır; FAZ 0'ın eklediği her satır **ayrı bir
muafiyet satırı** olarak yazılır. Bugünkü sayıyı doğrudan tavan yapmak, **şişmiş bir tavanı
kilitlemek** olurdu ve kapı hiç iş görmezdi (yol haritasının §A.5/4 ihlali).
"""

from __future__ import annotations

import ast
import pathlib

import pytest

APP = pathlib.Path(__file__).resolve().parents[1] / "app"

# ── TAVAN: FAZ 0 ÖNCESİ ölçüm (@`c3fcfe7`) ───────────────────────────────────
TABAN_ASK_KOD = 1135          # ask() gövdesi, yorum/docstring hariç
TABAN_ASK_IC_FN = 19          # iç fonksiyon (closure) sayısı
#: 🔴 **1723 → 1703 (2026-08-05): TAVAN İNDİ, ve inmesi bir KURAL GEREĞİDİR.**
#:
#: `cube_query_json_schema` `app/intent_semasi.py`'ye taşındığında modül 1749'dan 1703'e
#: düştü ve tavanda **38 satır boşluk** kaldı. Meta-kapı (`test_TAVAN_KAPISI_GERCEKTEN
#: _KIRMIZI_VERIYOR`) bunu **kırmızı** verdi ve haklıydı: *boşluklu bir tavan büyümeyi
#: durdurmaz — bir kod satırı eklenir, kapı yine yeşil der.*
#:
#: ⚠ Taban **ölçülen değere** indirildi, muafiyetler **korundu**: muafiyetler geçmiş
#: kararların kaydıdır ve bir taşıma onları geçersiz kılmaz. *Bir tavanı indirmek bir
#: iyileşmedir; muafiyet listesini silmek bir hafıza kaybıdır.*
#: ⚠ **VE TABAN, MUAFİYETLERİN DÜŞÜLDÜĞÜ HÂLDİR — ilk düzeltmem yanlıştı.**
#: `TAVAN = TABAN + Σmuafiyet` olduğu için tabanı ölçülen değere (1703) koymak, tavanı
#: 1721'e çıkarıp **18 satır boşluk** bıraktı; meta-kapı yine kırmızı verdi. Muafiyetler
#: ölçülen değerin **İÇİNDE** zaten var — onları bir kez daha eklemek **çifte sayımdır**.
#: Doğru taban: `ölçülen (1703) − Σmuafiyet (18) = 1685`, ve tavan yine tam 1703.
#: *Bir formülü düzeltmeden bir sayıyı düzeltmek, sayıyı ikinci kez yanlış yapar.*
TABAN_CUBE_ROUTER_KOD = 1685  # 1703 ölçüldü − 18 muafiyet = taban; tavan tam 1703

#: `(sha, Δ, gerekçe)` — her satır **bir maddeye** aittir ve nedeni yazılıdır.
#: 🔴 Toplamları aşağıda **kapıyla** doğrulanır: kimse listeye bakmadan tavanı büyütemez.
MUAFIYET_ASK_KOD = [
    ("9a138a9", 11, "0.5 · çapa zinciri — `coz(..., capalar=…)` bağlandı; "
                    "bayrak `capa_zinciri`, varsayılan `off`"),
    ("98a5071", 1, "0.12/0.13/0.6 · gerçek kill-switch + kanıt geçmişi"),
    ("faz-2.2b/borc11", 1, "grain-farkında çapraz-cube geçişi — kullanıcıya gösterilen "
                          "notun içine tanelik uyarısı giriyor (`grain_uyarisi`). Uyarıyı "
                          "cevaba TAŞIYAN satır `ask()` içinde olmak zorunda: notu üreten "
                          "yer orası. Karar ve metin `app/cekirdek.py`'de"),
    ("faz-5.16", 1, "NETLEŞTİRME DÜZEYİ bağlandı — `_olcu_belirsizligi_netlestir`'in "
                    "ilk satırı `netlestirme.sorar_mi()`'ye sorar. 🔴 Bu satır TAŞINAMAZ: "
                    "karar noktası `ask()`in kendi dalıdır ve kararı bir modüle çıkarmak "
                    "dalın kendisini de çıkarmak demektir (o da 33 satır ve `ask()`in "
                    "yerellerine bağlı). Kapının ölçüsü **eklenen kod**, ve eklenen kod "
                    "TEK satır: `sorar_mi()` çağrısı. Eşik ve düzey çözümü modüle ve "
                    "modül-düzeyi yardımcıya ait — `ask()`e giren yalnız SORU"),
    ("KÖK-4/donem_capasi", 3,
     "🔴 TAKİP TURUNDA DÖNEM ÇAPASI (denetim raporu KN-1) — sondanın EN BÜYÜK tek "
     "kümesi: 43 netleştirmenin 34'ü dönem, 26'sı TAKİP turunda ve 26/26'sında önceki "
     "turda dönem VARDI. Ölçü değişince `deterministic_refine` dönemi düşürüyor ve "
     "`_period_gate` «Hangi dönem için?» diye soruyor — oysa cevap bir tur önce "
     "verilmişti. "
     "🔴 Bu altı satır TAŞINAMAZ ve sebebi konum: `_period_gate` takip zincirinin DÖRT "
     "dalının da (refine · cross_cube_add · cross_cube_dim_switch · taze route) geçtiği "
     "TEK karar noktasıdır. Dört yere ayrı ayrı yazmak 'aynı kuralın iki sahibi' "
     "sınıfını DÖRDE katlardı. Taşınabilir olan her şey `app/donem_capasi.py`'de: üç "
     "şart, zaman-boyutu yeniden adlandırma, not metni, TAŞIYICI temizliği. "
     "⊙ Büyüme kapısı bunu İKİ KEZ ölçtü ve iki kez de tasarımı düzeltti: "
     "10 satır → 3 (yerinde taşıma + notu_al modüle gitti). "
     "⚠ Ve `return None` KALDIRILMADI (anti-çözüm A4): o dal bilinçli — farklı metrik "
     "gerçekten yeni bir sorudur. Dönem soruya değil OTURUMA bağlandı"),
    ("KÖK-2+3/uyum", 8,
     "🔴 UYUM KAPISI + BEYANLI KISMİ CEVAP (denetim raporu KÖK-2·KÖK-3). Ölçülen: "
     "`route()` bir CubeQuery üretiyor ama sorudaki NİYET İŞARETİNİN sorguda karşılığı "
     "olduğu hiçbir yerde denetlenmiyordu — `ocak ve haziran ciro karşılaştır` → "
     "Ocak-Haziran TOPLAMI, üstelik `source=cube` rozetiyle. "
     "🔴 Bu sekiz satır TAŞINAMAZ ve sebebi konum: denetim, sorgunun ÇALIŞTIĞI ve "
     "sonucun BİLİNDİĞİ noktada yapılmalı (`_answer_from_cube_query`); daha erken "
     "yapılsa `order`/`limit` henüz yok, daha geç yapılsa cevap çoktan gitmiş olur. "
     "Taşınabilir olan HER ŞEY `app/uyum.py`'de: yedi değişmez, dedektörler, "
     "kısmi-cevap metni. `ask()`e giren yalnız ÇAĞRI, cube_meta çözümü ve İKİ ATAMA. "
     "⊙ Ölçüldü: 525 meşru soruda 0 yanlış-pozitif, 5/5 hedef yakalandı; ölçüt üç kez "
     "düzeltildi ve her düzeltme bir yanlış-pozitif ölçümünden geldi"),
    ("KÖK-6/yetenek", 2, "🔴 YETENEK KAPISI (denetim raporu KN-3) — *"
                         "«forecast v1'de yok» gibi ÜRÜN-DÜZEYİ bir sınır Discovery'ye "
                         "düşüp bir SAYIYA dönüşüyordu (`adhoc.toplam_toplam_ciro`). "
                         "🔴 Bu iki satır TAŞINAMAZ ve sebebi kod değil KONUM: kapının "
                         "tek güvencesi *«route() ve Intent-JSON'ın İKİSİ de pes ettikten "
                         "SONRA»* çalışmasıdır. Daha erken bir yere konsa cevaplanabilir "
                         "soruları keserdi; daha geç konsa Discovery zaten devralmış "
                         "olurdu. Taşınabilir olan HER ŞEY `app/yetenek.py`'de: üç "
                         "dedektör, üç kutu, mesajlar ve yanıt alanları. `ask()`'e giren "
                         "yalnız ÇAĞRI ve DÖNÜŞ. ⊙ Ölçüldü: 968 meşru soruda "
                         "**0 yanlış-pozitif**, 3/3 hedef yakalandı"),
    ("faz-1.3b/2", 3, "Katman B'nin Discovery çağrı yolu — TAŞINABİLİR OLAN HER ŞEY "
                      "`app/katman_b.py`'ye taşındı (zorlama · allowlist okuma · ret notu "
                      "· sarmal sınıf). `ask()`'te kalan üç satır taşınamaz: motoru bir kez "
                      "saran bağlama (1) + yetki reddini onarım yoluna DÜŞÜRMEYEN `except` "
                      "(2). Reddi onarıma bırakmak 2 satır kazandırırdı ama bir yetki "
                      "sınırını 'güvenilir bir sorgu üretemedim' diye raporlardı — tavan, "
                      "dürüst olmayan bir mesajı SATIN ALMAZ"),
]
MUAFIYET_CUBE_ROUTER_KOD = [
    ("KÖK-7e/ay-cekimi", 7,
     "🔴 AY ÇEKİMİ TEK SAHİPTEN (denetim raporu KÖK-7e). Ölçüldü: `_AY_ADI_RE` ay "
     "adından SONRA `\\b` istiyordu ve Türkçenin en doğal söyleyişlerini GÖRMÜYORDU — "
     "60 çekimin 11'i (%18) geçiyordu (`ocakta`·`martta`·`subattan` hepsi kaçıyordu). "
     "🔴 Ve asıl kusur kalıpta değil İKİ SAHİPTE: tarih ÇÖZÜCÜSÜ `ocakta`yı doğru "
     "çözüyordu ([2026-01-01, 2026-01-31]) ama KAPSAM KAPISI kendi ay kalıbını taşıyor "
     "ve görmüyordu → soru R10 ile reddediliyordu. Sistem tarihi biliyor ama bildiğini "
     "bilmiyordu. "
     "Bu yedi satır TAŞINAMAZ: kalıbın kendisi (2) ve İKİ tüketicideki çekim denetimi "
     "(5). Denetimin kararı zaten `_ek_gecerli`de — çekimin TEK sahibi; buraya giren "
     "yalnız ÇAĞRI. Yeni ek listesi YAZILMADI (ADR-0008). "
     "⊙ Sonuç: %18 → **%100 (60/60)**, üç yanlış-pozitif kapısı temiz "
     "(`mart ayakkabi` · `kargo` · `ekim ekipmani`)"),
    ("faz-2.2b/borc11", 5, "grain-farkında çapraz-cube geçişi — ölçü eşlemesi ADLA değil "
                           "KAVRAMLA yapılıyor. 🔴 Taşınabilir olan HER ŞEY taşındı: "
                           "`olcu_eslemesi` + `grain_uyarisi` `app/cekirdek.py`'ye "
                           "(varyant bilgisi ÇEKİRDEK KATMANIN sorusudur, router'ın "
                           "değil); burada kalan yalnız çağrı ve döngünün yeni şekli"),
    ("9164806", 13, "0.18 · metrik kaydı = hakem — `_match_cube`'un İLK satırı "
                    "`schema['metrik_kaydi']`'na bakar; kayıt yoksa davranış birebir bugünkü"),
]
#: 🔴 **AYRI LİSTE — ve bu bir ÖLÇÜM ARACI DÜZELTMESİDİR.** İlk tasarımda dosya tavanı
#: `TAVAN_ASK_KOD + 1259` idi; yani **modül düzeyine** eklenen bir satır için `MUAFIYET_
#: ASK_KOD`'a yazmak gerekirdi ve o liste **aynı anda `ask()` gövdesinin tavanını da**
#: yükseltirdi. `ask()` bugün tam tavanında (1147/1147) duruyor — modül düzeyindeki bir
#: uç kaydı ona **bedava pay** açardı. *Bir tavanı yanlışlıkla yükselten muafiyet, muafiyet
#: değil sessiz bir tavan artışıdır* (bu dosyanın kendi cümlesi). Dosya muafiyeti bu yüzden
#: **ayrı** sayılır ve `ask()` tavanına **dokunmaz**.
MUAFIYET_ASK_DOSYA = [
    ("faz-5.16", 17, "`_netlestirme_duzeyi()` modül-düzeyi yardımcısı: tenant ayarını "
                     "okur ve `netlestirme.duzey()`e verir. 🔴 `ask()`in İÇİNE "
                     "yazılsaydı gövde tavanını 17 satır aşardı; dışarı alınması hem "
                     "tavanı korur hem doğru yerdir — bir AYAR okuması bir cevaplama "
                     "adımı değildir. ⚠ Okunamazsa `normal` döner: varsayılan BUGÜNKÜ "
                     "davranıştır ve bir ayar okunamadığında davranışı değiştirmek "
                     "sessiz bir kapsam kaybı olurdu"),
    ("faz-1.12", 9, "AI Act Md.14 durdurma ucu — karar+yazma `app/ask_jobs.py`'de; `ask.py`'de "
                "kalan yalnız UÇ KAYDI (dekoratör 2 + imza 1 + delege 1 + `ask_jobs` "
                "importu 1), `_bg`'nin iki dalındaki iptal kontrolü (2) ve akışın `iptal` "
                "olayı (3 — durdurma `hata` değildir ve dalsız akış 6 dk açık kalırdı). "
                "Bir HTTP uç kaydı router modülünden çıkarılamaz; çıkarmak `/ask/jobs` "
                "kaynağını iki dosyaya bölerdi"),
]
#: 🔴 `0619bfd` (0.22 · `migration_trace` `UnboundLocalError`) ham satırda **+8** getirdi
#: ama **kod satırında 0**: bildirim `if` bloğundan gövde başına **TAŞINDI**. Bir taşıma
#: borç değildir ve muafiyet listesinde yeri yoktur — burada yazılı olması, *"neden bu
#: madde listede yok?"* sorusunun cevabının kaybolmaması içindir.

TAVAN_ASK_KOD = TABAN_ASK_KOD + sum(d for _s, d, _g in MUAFIYET_ASK_KOD)
TAVAN_CUBE_ROUTER_KOD = (TABAN_CUBE_ROUTER_KOD
                         + sum(d for _s, d, _g in MUAFIYET_CUBE_ROUTER_KOD))
#: Dosya tavanı: FAZ 0 ÖNCESİ dosya kodu (2394) − o günkü `ask()` kodu (1135) = 1259 taşınabilir
#: pay, artı `ask()` muafiyetleri (taşınabilir), artı **modül düzeyi** muafiyetleri (ayrı liste).
#:
#: 🔴 **1259 → 1217 (2026-08-05): PAY İNDİ, çünkü BOŞLUK BÜYÜMEYİ DURDURMAZ.**
#: `_attach_viz` → `app/gorsel_ekleme.py` ve `_queue_discovery_job` →
#: `app/discovery_kuyrugu.py` taşındıktan sonra dosya 2498'den **2377**'ye düştü ve
#: tavanda **42 satır boşluk** kaldı. `cube_router`'da meta-kapı aynı boşluğu kırmızı
#: vermişti; burada meta-kapı yok ama **kural aynı**: *bir tavanı bir taşımadan sonra
#: indirmemek, kazanılan payı sessizce yeni büyümeye açar.*
#:
#: ⚠ `ask()` tavanı **1151'de bırakıldı** (bugün 1150, boşluk **1**): gövde payı zaten
#: sıkı ve onu 1150'ye çekmek, bir sonraki tek satırlık düzeltmeyi bir muafiyet
#: tartışmasına çevirirdi. *Bir tavan sıfır boşlukla değil, ANLAMLI bir boşlukla sıkıdır.*
#: 🔴 **TEK KOPYA.** Bu sayı iki yerde yazılıydı — burada ve `test_MUAFIYETLER_GEREKCELI
#: _ve_TOPLAMI_TUTUYOR`'un içinde — ve indirdiğimde **ikincisi bayatladı**: kapı
#: `2410 + 9 == 2377` diye kırmızı verdi. *Tanımsız bir sayının iki kopyası, iki ayrı
#: bayatlama yüzeyidir* (bu dosyanın kendi cümlesi, bu kez kendi üstünde ölçüldü).
TASINABILIR_PAY = 1217
TAVAN_ASK_DOSYA = TAVAN_ASK_KOD + TASINABILIR_PAY + sum(d for _s, d, _g in MUAFIYET_ASK_DOSYA)


# ── ÖLÇÜM ARACI ──────────────────────────────────────────────────────────────

def _belge_satirlari(agac: ast.AST) -> set[int]:
    """Docstring gövdelerinin kapladığı satır numaraları."""
    out: set[int] = set()
    for n in ast.walk(agac):
        if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            ilk = n.body[0] if n.body else None
            if (isinstance(ilk, ast.Expr) and isinstance(ilk.value, ast.Constant)
                    and isinstance(ilk.value.value, str)):
                out.update(range(ilk.lineno, ilk.end_lineno + 1))
    return out


def kod_satiri(kaynak: str, bas: int | None = None, son: int | None = None) -> int:
    """Yorum · docstring · boş satır **hariç** satır sayısı.

    ⚠ **Ölçüm aracının kendisi de bir bağımlılıktır** (MIMARI §6.4). Bu fonksiyon sessizce
    değişirse tavan da sessizce değişir — bu yüzden `test_OLCUM_ARACI_KENDINI_OLCUYOR`
    onu sabit bir girdiyle kilitler.
    """
    agac = ast.parse(kaynak)
    belge = _belge_satirlari(agac)
    satirlar = kaynak.splitlines()
    bas, son = bas or 1, son or len(satirlar)
    return sum(1 for i in range(bas, son + 1)
               if satirlar[i - 1].strip()
               and not satirlar[i - 1].strip().startswith("#")
               and i not in belge)


def _ask_dugumu() -> tuple[str, ast.AST]:
    kaynak = (APP / "routers" / "ask.py").read_text(encoding="utf-8")
    for n in ast.walk(ast.parse(kaynak)):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "ask":
            return kaynak, n
    pytest.fail("`ask()` fonksiyonu bulunamadı — taşınmışsa kapı GÜNCELLENMELİ, silinmemeli")


# ── KAPILAR ──────────────────────────────────────────────────────────────────

def test_OLCUM_ARACI_KENDINI_OLCUYOR():
    """Tavan, `kod_satiri`'nin doğruluğuna dayanır. Araç kayarsa kapı **sessizce** kayar."""
    ornek = (
        '"""Modül belgesi\nikinci satır."""\n'      # 2 satır belge → sayılmaz
        "# yorum\n"                                  # sayılmaz
        "\n"                                          # sayılmaz
        "import os\n"                                # 1
        "def f():\n"                                 # 2
        '    """tek satır belge."""\n'               # sayılmaz
        "    return os\n"                            # 3
    )
    assert kod_satiri(ornek) == 3, kod_satiri(ornek)


def test_ASK_FONKSIYONU_TAVANI_ASMIYOR():
    """`ask()` gövdesi **kod satırı** olarak tavanı aşamaz."""
    kaynak, n = _ask_dugumu()
    kod = kod_satiri(kaynak, n.lineno, n.end_lineno)
    assert kod <= TAVAN_ASK_KOD, (
        f"🔴 `ask()` {kod} kod satırı — tavan {TAVAN_ASK_KOD} "
        f"(FAZ 0 ÖNCESİ {TABAN_ASK_KOD} + {len(MUAFIYET_ASK_KOD)} muafiyet).\n"
        "YAPILACAK: yeni davranışı **modüle çıkar**, tavanı yükseltme. Tavanı yükseltmek "
        "kapıyı kapının kendisiyle çürütür — bu madde tam olarak onu engellemek için var.\n"
        "Gerçekten muaf bir iş ise MUAFIYET_ASK_KOD'a **sha + Δ + GEREKÇE** ile yazılır; "
        "gerekçesiz bir sayı muafiyet değil, sessiz bir tavan artışıdır.")


def test_ASK_IC_FONKSIYON_SAYISI_ARTMIYOR():
    """🔴 Asıl zarar **paylaşılan kapsamdır**: 19 iç fonksiyon aynı yerel değişkenleri
    görüyor ve bir çağrının **yanlış `if`in içinde** olduğu görünmüyor (`K3`'ün kusuru
    buradan doğdu). Yirminci closure, o körlüğü büyütür.

    ⚠ FAZ 0'ın **hiçbir maddesi** bu sayıyı artırmadı — muafiyet listesi bu ölçüt için
    **boştur** ve boş kalması bir başarıdır.
    """
    _kaynak, n = _ask_dugumu()
    ic = sum(1 for c in ast.walk(n)
             if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)) and c is not n)
    assert ic <= TABAN_ASK_IC_FN, (
        f"🔴 `ask()` içinde {ic} iç fonksiyon — tavan {TABAN_ASK_IC_FN}.\n"
        "Yeni bir yardımcı gerekiyorsa **modül düzeyine** al: saf bir fonksiyon test "
        "edilebilir, closure edilemez. `ask()`'in kapsamına eklemek borcu büyütür.")


def test_CUBE_ROUTER_TAVANI_ASMIYOR():
    """`cube_router.py` modül bütünü — **kod satırı**."""
    kaynak = (APP / "cube_router.py").read_text(encoding="utf-8")
    kod = kod_satiri(kaynak)
    assert kod <= TAVAN_CUBE_ROUTER_KOD, (
        f"🔴 `cube_router.py` {kod} kod satırı — tavan {TAVAN_CUBE_ROUTER_KOD} "
        f"(FAZ 0 ÖNCESİ {TABAN_CUBE_ROUTER_KOD} + "
        f"{len(MUAFIYET_CUBE_ROUTER_KOD)} muafiyet).\n"
        "Yeni eşleştirme kuralı bir **modüle** çıkar; bu dosya zaten deterministik "
        "yolun tamamını taşıyor.")


def test_ASK_PY_DOSYASI_ASK_DISINDA_SESSIZCE_SISMIYOR():
    """`ask()` küçülürken dosyanın **geri kalanı** şişerse borç yer değiştirmiş olur.

    ⚠ Bu ölçüt `ask()` dışını sayar; `ask()`'ten modül düzeyine **taşınan** kod bu sayıyı
    artırır ve bu **istenen** yöndür — o yüzden tavan, taşınabilecek payı da kapsayacak
    şekilde `ask.py`'nin **bütünü** üzerinden kurulur (aşağıdaki toplam kapısı).
    """
    kaynak, n = _ask_dugumu()
    toplam, icinde = kod_satiri(kaynak), kod_satiri(kaynak, n.lineno, n.end_lineno)
    disinda = toplam - icinde
    assert toplam <= TAVAN_ASK_DOSYA, (
        f"🔴 `ask.py` toplam {toplam} kod satırı (`ask()` {icinde} · dışı {disinda}) — "
        f"tavan {TAVAN_ASK_DOSYA}.\n"
        "`ask()`'ten modül düzeyine TAŞIMAK bu sayıyı artırmaz (yer değiştirir); "
        "artıyorsa gerçekten YENİ kod eklenmiş demektir → ayrı bir modüle çıkar.")


def test_KAPI_SAHTE_DEGIL_bir_satir_eklenince_KIRMIZI():
    """🔴 **Bir kapı, kırmızı olabildiğini kanıtlayana kadar kapı değildir.**

    Bu operasyonda bir kapı **üç kez** yanlış yazıldı ve *"yeşil"* kaldığı için kusuru
    **taşıyarak** geçti. Burada mutasyon **bellekte** yapılır: gerçek kaynağa **tek bir
    kod satırı** enjekte edilir ve tavanın aşıldığı gösterilir. Depoya hiçbir şey yazılmaz.

    Ayrıca **ikinci bir şey** kanıtlanır: enjekte edilen satır bir **yorum** olsaydı kapı
    yeşil kalırdı — birim kararının (*"kod satırı, ham satır değil"*) davranıştaki
    karşılığı budur, bir niyet beyanı değil.
    """
    kaynak = (APP / "cube_router.py").read_text(encoding="utf-8")
    temiz = kod_satiri(kaynak)
    assert temiz <= TAVAN_CUBE_ROUTER_KOD, "ön koşul: dosya bugün tavanın altında olmalı"

    # (a) KOD satırı → tavan aşılır
    kodlu = kaynak + "\n_FAZ_0_21_MUTASYON = 1\n"
    assert kod_satiri(kodlu) == temiz + 1
    assert not (kod_satiri(kodlu) <= TAVAN_CUBE_ROUTER_KOD), (
        "🔴 KAPI SAHTE: bir kod satırı eklendi ve tavan hâlâ aşılmadı. Tavanda boşluk "
        f"var demektir ({TAVAN_CUBE_ROUTER_KOD - temiz}) — kapı büyümeyi DURDURMUYOR.")

    # (b) YORUM satırı → kapı sessiz kalır (belgeleme vergilendirilmez)
    yorumlu = kaynak + "\n# ölçülmüş bir kusurun kaydı buraya yazılabilmeli\n"
    assert kod_satiri(yorumlu) == temiz, "yorum kod sayılıyor — belge vergilendirilir"
    assert kod_satiri(yorumlu) <= TAVAN_CUBE_ROUTER_KOD


def test_MUAFIYETLER_GEREKCELI_ve_TOPLAMI_TUTUYOR():
    """🔴 **Gerekçesiz bir sayı muafiyet değil, sessiz bir tavan artışıdır.**

    Kapı burada kendi listesini denetler: her muafiyet bir **kaynak** (sha — ya da henüz
    commit'lenmemiş bir madde için `faz-N.M` kimliği), bir **Δ** ve bir **gerekçe**
    taşımalı; toplamları da ilan edilen tavanla birebir tutmalı. Aksi hâlde biri listeye
    bakmadan `TAVAN_*` sabitini büyütür ve kapı, kendi kendini çürütür.
    """
    for ad, liste, taban, tavan in (
            ("ASK", MUAFIYET_ASK_KOD, TABAN_ASK_KOD, TAVAN_ASK_KOD),
            ("CUBE_ROUTER", MUAFIYET_CUBE_ROUTER_KOD,
             TABAN_CUBE_ROUTER_KOD, TAVAN_CUBE_ROUTER_KOD),
            ("ASK_DOSYA", MUAFIYET_ASK_DOSYA, TAVAN_ASK_KOD + TASINABILIR_PAY,
             TAVAN_ASK_DOSYA)):
        for sha, delta, gerekce in liste:
            assert len(sha) >= 7 and delta > 0 and len(gerekce) > 25, \
                f"{ad}: muafiyet eksik/gerekçesiz: {(sha, delta, gerekce)}"
        assert taban + sum(d for _s, d, _g in liste) == tavan, \
            f"{ad}: muafiyet toplamı ilan edilen tavanla TUTMUYOR"


def test_DOSYA_MUAFIYETI_ASK_TAVANINI_YUKSELTMIYOR():
    """🔴 **Ölçüm aracının kendi kusuru — ve düzeltmesi.**

    `ask()` bugün tam tavanında (1147/1147). Modül düzeyine eklenen bir uç kaydı için
    `MUAFIYET_ASK_KOD`'a yazmak, **aynı anda** `ask()` gövdesine de o kadar pay açardı —
    yani *"fonksiyonu büyütme"* kuralı, dosyaya eklenen her satırla **sessizce** gevşerdi.
    *Bir tavanı yanlışlıkla yükselten muafiyet, muafiyet değil sessiz bir tavan artışıdır.*
    """
    assert TAVAN_ASK_KOD == TABAN_ASK_KOD + sum(d for _s, d, _g in MUAFIYET_ASK_KOD), \
        "dosya muafiyeti `ask()` tavanına sızmış"
    # ⚠ Karşılaştırma bilinçli olarak **sabit adı taşımıyor**: `test_KAPI_BIR_TAVAN_BIR_
    # HEDEF_DEGIL` tavan sabitiyle yapılan her karşılaştırmanın `<=` olmasını arar ve bu
    # satır `>` olduğu için onu **yanlışlıkla** kırmızı yapardı (kapının kapıyı yakalaması).
    assert sum(d for _s, d, _g in MUAFIYET_ASK_DOSYA) > 0, "dosya muafiyeti hiç uygulanmamış"


def test_KAPI_BIR_TAVAN_BIR_HEDEF_DEGIL():
    """Küçültme **serbesttir** ve ayrı bir maddedir. Kapı `<=` kullanır, `==` değil.

    `==` kullanmak, iyileştirmeyi **kırmızı** gösterirdi — bir kapının yapabileceği en
    ters şey, doğru işi cezalandırmaktır. Bu test o niyeti **kodla** kilitler.

    🔴 **İLK SÜRÜM METİN ARADI VE KENDİ İDDİASINI YAKALADI.** `"== TAVAN_ASK_KOD" not in
    kaynak` yazıyordu; o dizi **testin kendi assert satırında** geçiyordu → kapı, doğru
    yazılmış bir dosyayı *"eşitlikle kilitlenmiş"* ilan etti. Bu deponun tam olarak
    kaydettiği sınıf: *"testler METNİ ölçtü, davranışı değil"* (`⟳` sayacı da aynı yere
    düşmüştü: kendi paragrafını sayıp 14 ↔ 13 vermişti).

    Doğru ölçüm **yapısaldır**: tavan sabitleriyle yapılan karşılaştırmaların **operatörü**
    AST'ten okunur. Bir dizi değil, bir **düğüm**.
    """
    agac = ast.parse(pathlib.Path(__file__).read_text(encoding="utf-8"))
    tavanlar = {"TAVAN_ASK_KOD", "TAVAN_ASK_DOSYA", "TAVAN_CUBE_ROUTER_KOD",
                "TABAN_ASK_IC_FN"}
    bulunan = 0
    for n in ast.walk(agac):
        if not isinstance(n, ast.Compare):
            continue
        # Sağ tarafta bir tavan sabiti geçiyor mu (yalın ya da toplamın parçası olarak)?
        adlar = {a.id for k in n.comparators for a in ast.walk(k)
                 if isinstance(a, ast.Name)}
        if not (adlar & tavanlar):
            continue
        bulunan += 1
        assert all(isinstance(o, ast.LtE) for o in n.ops), (
            f"tavan karşılaştırması `<=` değil ({[type(o).__name__ for o in n.ops]}) — "
            "küçültme kırmızı verirdi; kapı bir TAVAN, bir hedef değil")
    assert bulunan >= 3, f"tavan karşılaştırması bulunamadı ({bulunan}) — kapı boş mu?"


def test_YOL_HARITASININ_ILAN_ETTIGI_SAYIYLA_FARK_YAZILI():
    """⚠ Yol haritası `0.21`'i *"~1.930 satır / **20 closure** @`c4b14d1`"* diye ilan etti;
    bu kapının ölçtüğü ise `c3fcfe7`'de **2008 ham / 1135 kod / 19 iç fonksiyon**.

    İkisi **çelişmiyor**, farklı şey sayıyorlar: farklı sha, ve *"closure"* ile *"iç
    fonksiyon"* aynı birim değil. Sessizce kendi sayımı benimsemek, bu deponun altı kez
    kaydettiği *"ölçüm birimi tanımlanmadan yapılan kıyas"* kusuru olurdu — fark **yazılı**.
    """
    kaynak = pathlib.Path(__file__).read_text(encoding="utf-8")
    assert "c4b14d1" in kaynak and "c3fcfe7" in kaynak, \
        "iki ölçüm noktası da belgede anılmalı"
