// Bir mesajla birlikte gönderilen dosyalar — sunucu sözleşmesine ait DEĞİL.
// Backend /ask şu an metin-only; ekler tamamen istemci tarafında yaşar ve yalnız
// sohbette "ne eklemiştim" görünürlüğü için tutulur.
//
// AskResponse tipini kirletmemek için yanıt nesnesinin kimliğine bağlı bir
// WeakMap'te durur (thinking.ts ile aynı desen): konuşma store'undan item
// düşünce kayıt da kendiliğinden düşer.

const files = new WeakMap<object, File[]>();

export function markAttachments(item: object, list: File[]): void {
  if (list.length) files.set(item, list);
}

export function attachmentsOf(item: object): File[] | undefined {
  return files.get(item);
}
