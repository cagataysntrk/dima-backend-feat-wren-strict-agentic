# OPERASYON — ARKA PLAN DENETİMİ · ajan görev tanımları

> Her faz commit'inden **sonra** üç ajan **paralel** koşar. Görev metinleri burada
> **sabittir** — her seferinde yeniden yazılmaz, yalnız `<FAZ>` / `<MADDE>` / `<SHA>`
> doldurulur. Raporları **bir sonraki fazın girdisidir**.
>
> 🔴 **Denetim bir tören değildir.** Bu oturumda ajanlar belgede **15 kusur** buldu ve
> geliştiricinin kendi ölçüm aracı **12+ kez** yanlış ölçtü. Denetim, *"ben doğru
> yaptım"* duygusunun panzehridir.

---

## Ortak kurallar — üç ajan için de

* **Türkçe** rapor.
* **Testleri KOŞMA** (yavaş, ve kapı konteyneriyle çakışır) — kaynağı oku, `grep` yap.
  *İstisna:* **C ajanı** canlı tur koşar ve **tek konteyner** kullanır.
* **İddia etme, göster:** her bulguya `dosya:satır` ya da komut çıktısı.
* Emin olmadığına **`[DOĞRULANMADI]`** yaz — gizleme.
* **Yoğun yaz, dolgu yapma.** Sonuç yargısı en sonda, tek paragraf.

---

## A · PLAN DENETÇİSİ — *"madde TAM uygulandı mı?"*

```
Türkçe cevap ver. Bir geliştirme turunun yol haritasına UYUMUNU denetle.

BELGE : ~/.claude/plans/DIMA-V1-YOL-HARITASI.md   (madde: <MADDE>)
KURAL : <repo>/OPERASYON.md                        (§2 döngü · §5 D1-D5 · §6 değişmezler)
REPO  : /home/cagataysntrk/İndirilenler/dima-backend-feat-wren-strict-agentic
TUR   : <SHA> — `git show --stat <SHA>` ile başla

SOR ve KANITLA:
1. NE'nin ÜÇ PARÇASI da indi mi? (D1) — backend · sözleşme(alan/uç+tip) · frontend
   (bileşen+etkileşim). Frontend yoksa madde `api-only` beyanı taşıyor mu?
2. KAPI gerçekten kuruldu mu? Maddedeki test dosyası/adı VAR mı, o testi
   ÇALIŞTIRMADAN oku: doğru şeyi mi ölçüyor? (Bu depoda testler 6 kez METNİ ölçtü,
   davranışı değil.)
3. GERİ AL: bayraklı madde mi? Bayrak `FLAG_REGISTRY` VE `features.yml`'de mi?
   Bayrak kapalıyken davranışın BİREBİR aynı olduğu testle kilitli mi?
4. SONUÇ: maddenin ilan ettiği ölçülebilir değişim GERÇEKLEŞTİ mi? Commit mesajındaki
   sayı, kodda doğrulanabiliyor mu?
5. MIMARI.md AYNI commit'te güncellendi mi? `⟳` → `✅` dönüşümü ölçümlü mü?
6. ATLANAN var mı? Maddenin metnini satır satır tara; uygulanmamış her cümleyi listele.

ÇIKTI: (a) EKSİK KALEM listesi — her biri madde/satır atfıyla · (b) YANLIŞ UYGULANAN
listesi · (c) tek paragraf yargı: "madde inmiş sayılır mı?"
```

---

## B · BÜTÜNLÜK DENETÇİSİ — *"yeni kusur doğdu mu?"*

```
Türkçe cevap ver. Bir geliştirme turunun YAN ETKİLERİNİ denetle.

KURAL : <repo>/OPERASYON.md  (§4 KAT-1..KAT-5 · §6 on değişmez)
REPO  : /home/cagataysntrk/İndirilenler/dima-backend-feat-wren-strict-agentic
TUR   : <SHA> — `git show <SHA>` ile diff'i oku

SOR ve KANITLA:
1. YETİM doğdu mu? Yeni sözleşme alanı → frontend tüketicisi var mı? Yeni uç → çağıranı
   var mı? (Kapılar KÖR: `test_uc_yetim_degil` `re.search` kullanıyor, `test_cevap_alani_
   yetim_degil` yalnız 1. seviye AskResponse tarıyor — bunlara GÜVENME, kendin bak.)
2. KAT-1: yeni bir mekanizma İKİ İŞ birden mi yapıyor?
3. KAT-2: `source=None` dönen yeni bir dal merdiveni KESİYOR mu?
4. KAT-5 🔴: yeni bir SAYILAN KÜME doğdu mu? (`in ("a","b")` · dict anahtar süzgeci ·
   `Literal[...]` · sabit sözlük). Kullanıcıya dönük bir anlam ekseniyse İHLAL.
5. İKİNCİ SAHİP: aynı kural/gövde ikinci kez yazıldı mı? (Bu deponun 1 numaralı kusuru.)
6. BEYAN ↔ KOD: yeni yazılan yorum/docstring, kodun yaptığından FAZLASINI mı söylüyor?
7. SAYI BAYATLIĞI: commit'te/MIMARI'de yazılan sayılar HEAD'de hâlâ doğru mu? (D2)
8. GÜVENLİK: yetki/RLS/maskeleme yüzeyi genişledi mi? Onaysız yazma açıldı mı?

ÇIKTI: (a) İHLAL listesi — kanıtla (dosya:satır) · (b) RİSK listesi (henüz ihlal değil) ·
(c) tek paragraf yargı: "bu tur bir kusur sınıfı açtı mı?"
```

---

## C · CANLI KULLANICI — *"gerçek bir insan gibi kullan"*

```
Türkçe cevap ver. Sen bir DENETÇİ DEĞİLSİN — sen bir KULLANICISIN.
Türk bir üretim/finans yöneticisisin, veriyle çalışıyorsun, teknik bilmiyorsun.

REPO  : /home/cagataysntrk/İndirilenler/dima-backend-feat-wren-strict-agentic
ARAÇ  : backend/lab/vk_taban.py deseniyle KENDİ turunu kur (TestClient + --live)
KOTA  : ⚠ tur arası 5 SN — ölçülen sınır 10 istek/10 sn, bir Intent turu 3 çağrı

🔴 BAĞLAYICI KURALLAR:
· TOPLU KOŞUM YAPMA. Tek soru sor → cevabı OKU → ona göre bir sonrakini yaz.
  İnsan böyle çalışır; senaryo listesi koşturan bir betik DEĞİLSİN.
· En fazla 12-15 tur. Az ve derin, çok ve yüzeysel değil.
· Bu turda inen maddeyi (<MADDE>) KULLANMAYA ÇALIŞ — ama onu aramıyormuş gibi,
  doğal bir iş akışı içinde.
· Yazım hatası yap, eksik cümle kur, konuşma dili kullan. Gerçek kullanıcı düzgün yazmaz.
· Bir şey anlaşılmazsa DÜZELTMEYE ÇALIŞ (insan öyle yapar) — ve bunu rapor et.
· TEK konteyner kullan (`--name` ver); ikinci test konteyneri AÇMA.

HER TUR İÇİN KAYDET: ne yazdım · ne aldım (source · not · satır) · NE HİSSETTİM
(anladı mı? güvendim mi? devam edebildim mi?) · takıldıysam NEREDE.

ÇIKTI:
(a) TUR TUR anlatı (kısa, dürüst, birinci ağızdan)
(b) 🔴 KIRILMA ANLARI — "burada bıraktım/şaşırdım/güvenmedim" dediğin her nokta
(c) NE İYİ ÇALIŞTI (bunu da yaz — yalnız kusur raporu yanıltıcıdır)
(d) tek paragraf: "bugün bu ürünle işimi yapabilir miydim?"
```

---

## Denetim çıktısının işlenmesi

1. Üç rapor okunur, bulgular **birleştirilir** (aynı kusuru üçü de bulduysa **sınıfsaldır**).
2. **Kritik bulgu** (yetim · `KAT` ihlali · güvenlik · sessiz-yanlış) → **sıradaki maddeden
   ÖNCE** işlenir.
3. Kalanlar `OPERASYON-DURUM.md`'nin **açık borçlar** tablosuna yazılır — *kaybolmaz*.
4. Denetim turunun kendisi `OPERASYON-DURUM.md`'ye tarih+SHA ile kaydedilir.

> ⚠ **Ajan raporu bir OTORİTE DEĞİLDİR.** Bu oturumda ajanlar iki kez düşük saydı
> (14 ↔ gerçek 17 · "1/47" ↔ gerçek 13). Kritik bir sayı **kendin ölçülmeden** belgeye
> yazılmaz — `OPERASYON.md` §6/5.
