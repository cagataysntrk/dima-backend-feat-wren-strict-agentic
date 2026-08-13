"use client";

// 🔴🔴 `§63`/`§64` — **ÖNİZLEMENİN DURUMU VE ONAYI.**
//
// Belgenin başlığı işin kendisi: *«route ve garson, KARAR VERİCİ olmaktan çıkıp TAHMİNCİ
// oluyor … **kullanıcı KARARI VERİR (bir tık)**»* (`§3.1`). Bu dosya o tıkın mekaniğidir:
// bir cevap **önizleme mi**, onaylanırsa **hangi istek** yeniden gönderilir, iptal edilirse
// ne kalır.
//
// ══ NEDEN `page.tsx`'TE DEĞİL ══
//
// `page.tsx` bir **tavana** dayanmış durumda ve kapının kendi öğüdü açık: *«yeni davranışı
// bir bileşene çıkar, tavanı yükseltme»*. Ama asıl sebep tavan değil **sahiplik**: burada
// duran şey bir ekran değil bir **karar makinesidir** (üç durum: yok · bekliyor · onaylandı)
// ve `page.tsx`'in işi thread/bağlam yaşam döngüsüdür. İkisini aynı gövdeye koymak, bir
// cevabın geçmişe yazılıp yazılmayacağı kararını üç ayrı `useState`'e dağıtmak olurdu.
//
// ⚠ **İSTEK, PLANLA BİRLİKTE DURUR.** `[koş]` yeni bir istek **kurmaz**, aynısını
// `kos: true` ile **onaylar**. Ayrı iki durum olsaydı bir gün biri güncellenir öteki
// unutulurdu ㊲ — bu depoda o desen (`contextRapor` · `diyalog_durumu`) iki kez ölçüldü.

import { useState } from "react";

import type { AskResponse, CubeQuery } from "@/lib/types";

/** Makro/`/cube` koşumunun **tek** istek biçimi — mutasyon da, onay da bunu taşır. */
export interface MakroIstegi {
  cq: CubeQuery;
  label: string;
  makro?: { ad: string; soru: string; boyut: string; kos?: boolean };
}

/** Ekranın çizdiği **birleşik** plan. ⚠ Tel biçimi düzdür (`AskResponse.adimlar` +
 *  `gecerli`); burada bir araya gelir çünkü kart üç ayrı bayrağı değil **bir** nesneyi
 *  okumalı (`KAT-1`). `soru` sunucudan gelmez: kullanıcının **kendi** cümlesidir ve
 *  `[düzenle]` onu besteciye geri yazar — makronun adını (`neden`) değil. */
export interface PlanOnizlemesi {
  makro: string;
  adimlar: { sira: number; fiil: string; metin: string }[];
  gecerli: boolean;
  note: string;
  soru: string;
}

/** Bestecinin aldığı **kumanda**: ne çizilecek ve iki düğme ne yapacak. Tek prop olarak
 *  geçer — üç ayrı prop, üç ayrı yerde unutulabilecek üç ayrı bağ demekti 🆘. */
export interface OnizlemeKumandasi {
  plan: PlanOnizlemesi | null;
  kos: () => void;
  iptal: () => void;
}

export function useOnizleme() {
  const [durum, setDurum] = useState<{ plan: PlanOnizlemesi; istek: MakroIstegi } | null>(null);

  return {
    plan: durum?.plan ?? null,

    /** 🔴 **ÖNİZLEME BİR CEVAP DEĞİLDİR.** `true` dönerse çağıran onu **kaydetmez**:
     *  hiçbir sorgu koşmadı, geçmişe yazmak/tuvale eklemek/bağlamı güncellemek olmamış
     *  bir cevabı olmuş gibi kaydetmek olurdu — ve bir sonraki takip sorusu o hayalî
     *  bağlam üzerinden sorulurdu. */
    yakala(cevap: AskResponse, istek: MakroIstegi): boolean {
      if (cevap.source !== "onizleme" || !istek.makro) {
        setDurum(null);
        return false;
      }
      setDurum({
        plan: {
          makro: istek.makro.ad,
          adimlar: cevap.adimlar ?? [],
          // ⚠ `!== false`: alan hiç gelmediyse plan geçerli sayılır — sunucu geçersizliği
          // **söyler**, sessizliği bir ret değildir (ADR-0020 ruhu).
          gecerli: cevap.gecerli !== false,
          note: cevap.note ?? "",
          soru: istek.makro.soru,
        },
        istek,
      });
      return true;
    },

    /** Onaylanmış istek — `null` ise ortada bekleyen bir plan yoktur. */
    onayla(): MakroIstegi | null {
      if (!durum?.istek.makro) return null;
      setDurum(null);
      return { ...durum.istek, makro: { ...durum.istek.makro, kos: true } };
    },

    iptal(): void {
      setDurum(null);
    },
  };
}
