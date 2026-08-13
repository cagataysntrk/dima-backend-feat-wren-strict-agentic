"use client";

// ══════════════════════════════════════════════════════════════════════════════
// 🔴🔴 BESTECİ — ÜRÜNÜN **TEK** GİRDİ KUTUSU, ARTIK TEK BİR YERDE YAZILI
// ══════════════════════════════════════════════════════════════════════════════
//
// ⊙ **ÖLÇÜLMÜŞ GERİLEME (2026-08-13).** «Tek chat» kararı uygulandığında sol besteci
// kaldırıldı (`ChatPanel` → `+ yeni sohbet`) ve tek besteci `ReportPanel`'in altına
// yerleşti. Ama `🗂 tuval` modunda `AnalysisCanvas` `ReportPanel`'in **YERİNE**
// çiziliyordu → o modda ekranda **hiçbir girdi kutusu kalmadı.** Bir kapsam kararı
// değil, taşımanın yan hasarıydı: eskiden soldaki kutu vardı, artık yoktu.
//
// 🔴 **BU DOSYA ÜÇÜNCÜ BİR BESTECİ DEĞİLDİR — TEK BESTECİDİR.** `ReportPanel` içinde
// aynı `OneriSeridi`+`CaretInput` sarmalaması **iki kez** yazılıydı (çoklu-seçim ve
// «devam et»); tuval için bir üçüncüsünü yazmak, aynı özelliği üçüncü kez bakmak
// olurdu — ve «tek chat» kararının gerekçesi tam olarak buydu:
// *«çift chat'e her özelliği girmek elim bir hata ve risk»*.
//
// ⚠ ÇIKARIM SIRASINDA DAVRANIŞ **BİREBİR** KORUNDU:
//   · `OneriSeridi` sarmalaması (çapa üstte · şerit altta · `↓↑ Enter Esc` yalnız
//     odaktaki kutuda — `onKeyDownCapture`, küresel dinleyici YOK);
//   · `secili` başlangıcı **-1** (`§3.3`: *menü değil tamamlama* — `Enter` kullanıcının
//     KENDİ cümlesini gönderir; şeride girmek için önce `↓`). Bu karar `OneriSeridi`'nin
//     içindedir ve buradan **görünmez bile**; bu dosya onu ne bilir ne bozabilir;
//   · `öneri: açık/kapalı` tuşu · 📌 çapa çubuğu · `✕ bağlamı bırak` · `busy` tarama
//     çizgisi · `size="inline"` · `ipucu`.
//
// ⊘ **NE ALMADI:** 📎 yükleme ve kapsam/yol/mod anahtarları `ChatPanel`'de KALDI.
// `ChatPanel`'in kendi taşıma tablosu bunu yazıyor: *«bir sohbet-kapsamlı veri kaynağı
// bir cümle değildir»* ve o anahtarlar **soru başına değil oturum başına** ayarlardır
// (`test_kapsam_mercegi` de onları o dosyada arar). Buraya taşımak, bir kapıyı
// kırmak ve bir ayarı yanlış ömre bağlamak olurdu.

import { CaretInput } from "@/components/CaretInput";
import { OneriSeridi, type OneriCapasi } from "@/components/OneriSeridi";
import { PillSatiri } from "@/components/PillSatiri";
import type { ReactNode } from "react";

export function Besteci({
  deger,
  onDeger,
  onGonder,
  busy = false,
  ipucu,
  capa = null,
  onCapaBirak,
  onMakro,
  sonBakilanlar = [],
  ustBilgi,
  vurgulu = false,
}: {
  /** Kutunun metni. ⚠ Durum **çağıranda** durur: `ReportPanel` iki farklı kutuyu iki
   *  farklı state ile besliyor (`continueValue` · `multiValue`) ve bir seçim
   *  gönderildiğinde ikisi FARKLI şeyler temizliyor. Durumu buraya çekmek, o farkı
   *  gizler ve bir gün yalnız birini temizlerdik. */
  deger: string;
  onDeger: (v: string) => void;
  /** 🔴 **TRIM + BOŞ KORUMASI BURADA, TEK YERDE.** Çıkarımdan önce iki kutu bunu iki
   *  ayrı yerde yapıyordu (biri `CaretInput.onSubmit` içinde, öteki `submitReplyMulti`
   *  gövdesinde). Aynı kuralın iki sahibi, bu deponun 1 numaralı kusur sınıfı.
   *  Çağıran **kırpılmış, boş olmayan** metni alır; temizlik/kapanış onun işidir. */
  onGonder: (metin: string) => void;
  busy?: boolean;
  ipucu?: string;
  /** `§5.1` — 📌 görünür çapa. `null` → çubuk hiç çizilmez. */
  capa?: OneriCapasi | null;
  /** `✕ bağlamı bırak` — **açık kullanıcı eylemi**; verilmezse düğme çizilmez. */
  onCapaBirak?: () => void;
  /** 🔴 `§7 ②` — ADLANDIRILMIŞ MAKRO. Şeritteki *«… neden bu seviyede?»* satırı bir
   *  `cube_query` **taşımaz**; tıklanınca metni tamamlamak yerine `POST /oneri/makro`'ya
   *  gider ve **LLM'siz** çok adımlı bir plan koşar.
   *  ⚠ Bu prop **buradan geçer ama burada karşılanmaz**: çapayı (`capa.cq`) ve cevabın
   *  hangi thread'e düşeceğini bu dosya bilmez. Bilen `ReportPanel`/`page.tsx`'tir ve
   *  makro cevabı `/cube` ile **aynı** yerleştirme yolundan geçer — yeni bir gösterim
   *  icat edilmedi. Verilmezse şerit bugünkü davranışını sürdürür (`KURAL B`). */
  onMakro?: (ad: string, soru: string) => void;
  sonBakilanlar?: string[];
  /** Kutunun üstünde tek satırlık durum (bugün: *«N kart birleştirilerek soruluyor»*).
   *  ⚠ Bu satır varken çapa **verilmez**: bağlamı seçili kartlar kurar ve bunu zaten
   *  bu satır söyler — ikinci bir çapa, hangisinin geçerli olduğunu belirsiz bırakırdı. */
  ustBilgi?: ReactNode;
  /** Çoklu-seçim kipinin hafif vurgusu (`bg-accent/[0.03]`). */
  vurgulu?: boolean;
}) {
  return (
    <div
      className={
        "shrink-0 border-t border-hairline px-4 py-3" +
        (vurgulu ? " bg-accent/[0.03]" : "")
      }
    >
      {ustBilgi && (
        <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
          {ustBilgi}
        </div>
      )}
      <div className="flex items-center gap-2">
        <span className="select-none font-mono text-sm text-accent">›</span>
        <div className="flex-1">
          {/* 🔴 `§5.1` — `OneriSeridi` besteciyi **sarmalar**: 📌 çapa üstte, öneri
              şeridi altta, tuşlar yalnız odaktaki kutuda. Sıra bağlayıcıdır. */}
          <OneriSeridi
            metin={deger}
            onSec={onDeger}
            sonBakilanlar={sonBakilanlar}
            capa={capa}
            onCapaBirak={onCapaBirak}
            onMakro={onMakro}
          >
            <CaretInput
              value={deger}
              onChange={onDeger}
              onSubmit={() => {
                const t = deger.trim();
                if (!t) return;
                onGonder(t);
              }}
              busy={busy}
              size="inline"
              ipucu={ipucu}
            />
          </OneriSeridi>
          {/* 🔴 `§5.2`/`§5.3` — PILL SATIRI, bestecinin **altında**. ⚠ `OneriSeridi`'nin
              İÇİNE değil ALTINA konuldu ve bu bir yerleşim tercihi değil bir sahiplik
              kararı: şerit *«ne sorabilirsin»* der (aday listesi), pill satırı *«ne
              anladım ve bu soru koşabilir mi»* der (`Niyet` + doğrulama). İkisini tek
              bileşene koymak, iki farklı soruyu tek sahibe vermek olurdu.
              ⊘ Kendi bayrağını/debounce'unu kendi taşır; buradan geçen tek şey metindir. */}
          <PillSatiri metin={deger} />
        </div>
      </div>
    </div>
  );
}
