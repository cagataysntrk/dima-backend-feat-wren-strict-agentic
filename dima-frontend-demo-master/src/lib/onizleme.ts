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
  /** 🔴 `§66` — **onaylanan plan**. Doluysa istek `/oneri/makro`'ya değil
   *  `POST /plan/kos`'a gider: merdiven yolunda (`/ask`) önizlenen plan bir **reçete adı**
   *  taşımaz, planın kendisini taşır. ⚠ Üç alan da aynı istekte durur çünkü hepsi **aynı
   *  koşumun** tarifidir; ayrı üç mutasyon, aynı yerleştirme gövdesinin üç kopyası olurdu. */
  plan?: Record<string, unknown>;
}

/** Ekranın çizdiği **birleşik** plan. ⚠ Tel biçimi düzdür (`AskResponse.adimlar` +
 *  `gecerli`); burada bir araya gelir çünkü kart üç ayrı bayrağı değil **bir** nesneyi
 *  okumalı (`KAT-1`). `soru` sunucudan gelmez: kullanıcının **kendi** cümlesidir ve
 *  `[düzenle]` onu besteciye geri yazar — makronun adını (`neden`) değil. */
export interface PlanOnizlemesi {
  makro: string;
  /** 🔴 `§68`/`§28.1` — teklifin **pill satırı**; yalnız tek adımlı teklifte dolar 🆂. */
  piller?: import("@/lib/types").PillYaniti["piller"] | null;
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
      if (cevap.source !== "onizleme") {
        setDurum(null);
        return false;
      }
      // 🔴 `§66` — **İKİ YOL, TEK ÖNİZLEME.** Makro yolunda tarif bir **reçete adıdır**
      // (`istek.makro`), merdiven yolunda (`/ask`) **planın kendisidir**
      // (`cevap.plan_taslagi`). İkisi için ayrı bir gösterim/durum kurmak, kullanıcıya
      // aynı kararı iki farklı yüzle sormak olurdu ㊲.
      const _plan = cevap.plan_taslagi ?? undefined;
      if (!istek.makro && !_plan) { setDurum(null); return false; }
      setDurum({
        plan: {
          makro: istek.makro?.ad ?? "plan",
          adimlar: cevap.adimlar ?? [],
          // ⚠ `!== false`: alan hiç gelmediyse plan geçerli sayılır — sunucu geçersizliği
          // **söyler**, sessizliği bir ret değildir (ADR-0020 ruhu).
          gecerli: cevap.gecerli !== false,
          note: cevap.note ?? "",
          piller: cevap.piller ?? null,
          soru: istek.makro?.soru ?? istek.label,
        },
        istek: { ...istek, plan: _plan },
      });
      return true;
    },

    /** Onaylanmış istek — `null` ise ortada bekleyen bir plan yoktur. */
    onayla(): MakroIstegi | null {
      const i = durum?.istek;
      if (!i || (!i.makro && !i.plan)) return null;
      setDurum(null);
      // ⚠ Plan varsa **o** koşulur (`/plan/kos`); yoksa makro `kos: true` ile onaylanır.
      return i.plan ? i : { ...i, makro: { ...i.makro!, kos: true } };
    },

    iptal(): void {
      setDurum(null);
    },
  };
}
