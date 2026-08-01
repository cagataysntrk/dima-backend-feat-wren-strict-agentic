// §B (1 Ağustos 2026) — Konu/Thread modeli: bir "thread", aynı konuyu paylaşan bir kök
// soru + üstüne gelen takiplerin tümüdür. Kullanıcı bir thread'i derinlemesine işleyip
// başka bir konuya geçip GERİ DÖNEBİLİR — bu yüzden gruplama KRONOLOJİK POZİSYONA değil,
// KİMLİĞE (thread_id) dayanır (bkz. plan: SAF is_new_topic-sınırlı ardışık gruplama bu
// senaryoda YANLIŞ sonuç verir — geri dönülen thread'e eklenen mesaj, kronolojik olarak
// ARADA başlayan başka bir thread'e yanlışlıkla karışırdı).
//
// ChatPanel VE ReportPanel AYNI groupIntoThreads() çıktısını kullanır (page.tsx'te TEK
// yerde hesaplanır) — iki panelin thread sınırları konusunda ASLA anlaşmazlığa düşmemesi
// garanti edilir.

import type { AskResponse } from "./types";

export interface Thread {
  id: string;
  items: AskResponse[]; // eski→yeni, yalnız EKLENİR (asla yeniden sıralanmaz/silinmez)
}

// Yeni bir thread kimliği üret — page.tsx'teki makeSessionId() ile AYNI dayanıklı desen
// (güvenli bağlamda crypto.randomUUID, aksi halde zaman+rastgelelik fallback'i).
export function mintThreadId(): string {
  try {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
      return crypto.randomUUID();
    }
  } catch {
    /* güvenli bağlam değil */
  }
  return `t-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

// `items` KRONOLOJİK (eski→yeni) sırada beklenir — çağıran (page.tsx) `useHistory`'nin
// yeni→eski store sırasını `[...items].reverse()` ile çevirir (ChatPanel'in bugün zaten
// yaptığı AYNI çevirme).
//
// Algoritma: `thread_id` VARSA (bu özellik şu andan itibaren HER yeni mesaja client
// tarafından yazılır) ona göre grupla — bir thread_id'nin İLK görülüşü yeni bir grup
// AÇAR, SONRAKİ görülüşleri (ARDIŞIK OLMASA BİLE, ör. araya başka thread'ler girmiş
// olsa da) O GRUBA eklenir. `thread_id` YOKSA (bu özellikten ÖNCE kaydedilmiş, resume
// edilen ESKİ konuşmalar) `is_new_topic` sınırlı ARDIŞIK gruplamaya düşülür — yalnız
// eski veri için kabul edilebilir bir yaklaşıklık (yeni veri için asla devreye girmez).
export function groupIntoThreads(items: AskResponse[]): Thread[] {
  const threads: Thread[] = [];
  const byThreadId = new Map<string, Thread>();
  let legacyCurrent: Thread | null = null;

  items.forEach((item, i) => {
    const tid = item.thread_id;
    if (tid) {
      legacyCurrent = null; // etiketli bir mesaj görülünce eski-tip zincir sıfırlanır
      let t = byThreadId.get(tid);
      if (!t) {
        t = { id: tid, items: [] };
        byThreadId.set(tid, t);
        threads.push(t);
      }
      t.items.push(item);
      return;
    }
    const startsNewLegacyThread = legacyCurrent === null || item.is_new_topic === true || i === 0;
    if (startsNewLegacyThread) {
      legacyCurrent = { id: `legacy-${i}`, items: [] };
      threads.push(legacyCurrent);
    }
    legacyCurrent!.items.push(item);
  });

  return threads;
}

// Verilen item'ın AİT OLDUĞU thread'i bulur (ChatPanel'de tıklama çözümü, "yeniden girme"
// için) — referans eşitliğiyle arar (AskResponse nesneleri store'da yeniden yaratılmaz).
export function threadContaining(threads: Thread[], item: AskResponse): Thread | null {
  return threads.find((t) => t.items.includes(item)) ?? null;
}

// §B düzeltmesi (1 Ağustos 2026) — "bu karta yanıt ver": backend'e gönderilen/kart
// üstünde gösterilecek kısa, insan-okur çapa etiketi. Sunucu bunu aynen echo eder
// (AskResponse.reply_to_label); ReportCard breadcrumb'ta gösterir.
export function replyAnchorLabel(question: string): string {
  const q = question.trim();
  return q.length > 48 ? `${q.slice(0, 45)}…` : q;
}
