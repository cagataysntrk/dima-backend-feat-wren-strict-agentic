// Belgeler — kullanıcının YÜKLEDİĞİ ve uygulamanın ÜRETTİĞİ dosyalar tek listede.
//
// İkisi aynı şeydir: bir sohbetin ürettiği tablo da, kullanıcının sürüklediği
// Excel de "bu hesapta duran bir dosya". Ayrı sayfalar tutmak kullanıcıyı aynı
// soruyu iki yerde sormaya zorlardı ("o rapor neredeydi?"). Ayrım tek bir
// alanda taşınır — `origin` — ve arayüzde bir rozete dönüşür.
//
// KALICILIK: şu an bellekte. Backend'de henüz dosya ucu YOK (ne yükleme ne
// dışa aktarma — dima-backend HEAD'de doğrulandı), bu yüzden belgeler oturum
// boyunca yaşar. Şekil, kalıcılık geldiğinde değişmeyecek: aynı alanlar bir
// `/documents` yanıtından da doldurulabilir.

import { create } from "zustand";

export type DocumentOrigin = "uploaded" | "generated";

export interface DocumentEntry {
  id: string;
  name: string;
  /** YÜKLENEN mi ÜRETİLEN mi — listedeki rozetin kaynağı. */
  origin: DocumentOrigin;
  /** MIME ya da kaba tür etiketi (csv, xlsx, pdf…). */
  kind: string;
  size: number;
  createdAt: number;
  /** Hangi sohbetten doğdu — sohbet kapsamlı görünüm bunu süzer. */
  conversationId?: string | null;
  /** Belgeyi doğuran soru (üretilenlerde başlık olarak okunur). */
  question?: string | null;
  /** Kanıt kaydı — varsa üretilen belgenin sorgu sözleşmesi. */
  contractId?: string | null;
  /** İçerik. Yüklenende kullanıcının dosyası, üretilende bizim ürettiğimiz blob. */
  blob: Blob;
}

interface DocumentsState {
  documents: DocumentEntry[];
  add: (doc: Omit<DocumentEntry, "id" | "createdAt">) => string;
  remove: (id: string) => void;
  /** Oturum değişiminde temizlik (çapraz kullanıcı sızıntısı olmasın). */
  reset: () => void;
}

function makeId(): string {
  try {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
      return `d-${crypto.randomUUID()}`;
    }
  } catch {
    /* güvenli bağlam değil */
  }
  return `d-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

export const useDocuments = create<DocumentsState>((set) => ({
  documents: [],
  add: (doc) => {
    const id = makeId();
    set((s) => ({ documents: [{ ...doc, id, createdAt: Date.now() }, ...s.documents] }));
    return id;
  },
  remove: (id) => set((s) => ({ documents: s.documents.filter((d) => d.id !== id) })),
  reset: () => set({ documents: [] }),
}));

/** Bir belgeyi indir — object URL açılır, indirilir ve hemen geri verilir. */
export function downloadDocument(doc: DocumentEntry): void {
  const url = URL.createObjectURL(doc.blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = doc.name;
  a.click();
  // revoke'u bir sonraki tick'e bırak: bazı tarayıcılar indirme başlamadan
  // URL'i geçersiz kılarsak dosyayı boş indiriyor.
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
