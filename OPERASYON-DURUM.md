# OPERASYON DURUMU — *nerede kaldık*

> 🔴 **BAĞLAM SIFIRLANDIYSA BURADAN BAŞLA.** Sırayla oku:
> 1. **`OPERASYON.md`** — kural seti (nasıl çalışılır)
> 2. **bu dosya** — nerede kaldık
> 3. **`~/.claude/plans/DIMA-V1-YOL-HARITASI.md`** — ne yapılacak *(§10'daki sıra)*
> 4. `backend/MIMARI.md` — mimari değişmezler
>
> Bu dört dosya operasyonun **tam durumunu** taşır. Sohbet geçmişine ihtiyaç YOKTUR.

**Son güncelleme:** 2026-08-04 · HEAD `8f87e40`

---

## 🔵 ŞU AN

| | |
|---|---|
| **Aktif faz** | **FAZ −1** — `MIMARI.md` ön hazırlığı *(kod yok)* |
| **Sıradaki madde** | `−1.1` Kutu A · `−1.2` Kutu B · `−1.3` Kutu C |
| **Ondan sonra** | **FAZ 0 · adım 1:** `0.22` + `0.2` + `0.23` *(~1 oturum, ucuz + bloklayıcı üçlü)* |
| **v1 bitiş ölçütü** | §C'nin **16 ölçütü** yeşil |

---

## ✅ BİTEN

### FAZ −2 · Belge onarımı *(kod yok — 2026-08-04)*
Yol haritası **4881 → 5213 satır**. Yedek: `~/.claude/plans/.yedek/` *(md5 doğrulandı)*.

| # | Ne | Nerede |
|---|---|---|
| **#5** | **`§G.6f`** — `N`=3 (simetri şartıyla) · hakem protokolü (2 hakem · 10 vaka · ayrışma→`⊘`) · 🔴 **`⊘ KOŞULAMADI` ≠ «kaybetti»** · kısmi benimseme | §G.6f |
| **#1** | v2 giriş **döngüsel kilidi** kırıldı: *"teyitli"* → **"kararı bağlanmış"**; v3'e ait 2 madde kapıdan çıkarıldı | §B · Bölüm II girişi · II-0 |
| **#4** | FAZ 0'ın **dört `KAT-3` ihlali** + **bağlayıcı koşum sırası**; `0.23`'ün *"bağımlı değil"* çelişkisi kapatıldı | FAZ 0 girişi · 0.23 |
| **#3** | **`6.0` YENİ MADDE** — *"D9 ters uygulanmış · yapılanı geri al"*; `6.1`'in çelişkili `KAPI` bloğu kaldırıldı | 6.0 · 6.1 |
| **#2** | Bölüm II şablon borcu: **18 bayraklı maddenin 17'sinde `GERİ AL` yok** + kök neden (denetim regex'i `II-X.N` başlıklarını kapsamıyordu) kapıya çevrildi | Bölüm II girişi |
| **+** | **VK-5 üç kalıntısı** düzeltildi *(aşağıdaki ölçümle)* | §G.6e |

### Taban ölçümü · `lab/vk_taban.py` *(commit `8f87e40`)*
VK-1…VK-6 **yapısal ve canlı** (gemini) ölçüldü. `§G.6e`'nin *"Bugün"* sütunu artık
**yeniden üretilebilir**. Üç satır düzeltilmesi gerekti (VK-4 · VK-5 · VK-6).

> 🔴 **OPERASYONUN EN ÖNEMLİ SAYISI:** **13 turun DÖRDÜNDE** yazım-benzerliği kısa devresi
> öldürüyor → **`AJ0` §G'nin tek en yüksek kaldıraçlı maddesi**; VK-1 · VK-5 · VK-6'yı
> **ilk kapıda** kesiyor, `AJ2`/`AJ5b` sıraya bile gelmiyor.

> ✅ **Çürütülen iddia:** *"`verimlilik` katalogda YOK"* **yanlıştı** — `verim` + geçerli ek
> zinciriyle kapsanıyor (`oee.ort_oee`). Asıl eksik **ÜRÜN BOYUTU** (`R9`), ve o
> **tenant-özel** (`stok_adi` gitas'ta VAR).

---

## 📋 AÇIK BORÇLAR — unutulmayacak

| # | Borç | Nerede kapanır |
|---|---|---|
| 1 | `0.23` **kapısız iner** (düzeltmesi bağımsız, `KAPI`'sı `K2/(c)`) | **FAZ 0.14** — geriye dönük |
| 2 | Bölüm II'nin **17 maddesinde `GERİ AL` yok** | Madde **sıraya alındığında** (kapı: 0.14'ün `test_yol_haritasi_butunlugu.py`) |
| 3 | Belgede **10 kusur** kaldı: sayı çelişkileri (v2 kapsamı · §G aralığı · `KAT-1…4` başlığı · EK K 24↔29 · `−1.1` 6↔13) · **4 ölü bayrak** · `II-D.1b` tanımsız · **iki biçim hatası** (`GERİ AL` blokları yanlış faz başlığı altında) · FAZ 7 kapsamı (Plan 2 dalı) | İlgili faza gelindiğinde — **ayrı tur AÇILMAZ** |
| 4 | `is_period_only` hâlâ **0 çağıran** | 0.14/K2 |
| 5 | Deneyim süitinin **bilerek açık kırmızısı**: *"o ayı makine bazında aç"* | II-D *(satır çapası)* |

---

## 🤖 ARKA PLAN DENETİMİ

Her faz commit'inden sonra **üç ajan paralel** koşar *(`OPERASYON.md` §7)*:
**A** plan denetçisi · **B** bütünlük denetçisi · **C** canlı kullanıcı *(tek tek, insan gibi)*.
Raporları **bir sonraki fazın girdisidir**; kritik bulgu sıradaki maddeden **önce** işlenir.

**Son denetim turu:** *(henüz koşulmadı — ilk tur FAZ −1 sonunda)*

---

## 📌 ÖLÇÜM TABANI *(D2: sayı + damga + komut)*

| Ölçüt | Değer | Damga | Komut |
|---|---|---|---|
| Test | **2018** | `8f87e40` | `pytest -q --collect-only` |
| eval | `+0,0 / +0,0 / +0,0` | `88bde2a` | `python -m eval.run` |
| Korpus doğru-cube | **%93,2** | `88bde2a` | `python lab/nl_corpus.py --kapi` |
| Deneyim süiti (canlı) | **41 ✅ · 1 ❌ · 63 ⊘** | `88bde2a` | `python lab/deneyim.py --live` |
| VK taban | **§G.6e kutusu** | `8f87e40` | `python lab/vk_taban.py --live` |
| Motor-RLS | **0** | `8f87e40` | `grep -rc rowLevelAccessControl backend/app/` |
| Bayrak | `FLAG_REGISTRY` **16** ↔ `features.yml` **14** | `8f87e40` | — |
| Panel export | **13** *(tavan DOLU)* | `88bde2a` | `grep -rE "export (default )?function [A-Za-z]+Panel" src/ \| wc -l` |
| Konuşma türü | **5** *(v1 hedefi 7)* | `8f87e40` | `grep -cE "^TUR_[A-Z_]+ = " backend/app/followup.py` |
