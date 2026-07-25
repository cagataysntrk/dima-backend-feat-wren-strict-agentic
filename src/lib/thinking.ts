// Bir cevabın "düşünme" süresi — sunucu sözleşmesine ait DEĞİL, tamamen istemci
// tarafı bir ölçüm (mutation başlangıcı → yanıt). AskResponse tipini kirletmemek
// için yanıt nesnesinin kimliğine bağlı bir WeakMap'te tutulur; konuşma
// store'undan item düşünce kayıt da kendiliğinden düşer.

const durations = new WeakMap<object, number>();

export function markThinking(item: object, ms: number): void {
  durations.set(item, ms);
}

export function thinkingMs(item: object): number | undefined {
  return durations.get(item);
}
