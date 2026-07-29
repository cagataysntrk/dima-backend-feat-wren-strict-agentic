// Yüklenen veri kümesi — sunucu sözleşmesine ait DEĞİL, bir SOHBET OLAYI.
//
// `/ask/upload` bir `UploadResponse` döner (dataset adı, satır sayısı, çıkarılan
// kolonlar, örnek sorular). Bunu sohbet akışında göstermek için AskResponse
// tipini kirletmiyoruz; yanıt nesnesinin kimliğine bağlı bir WeakMap'te
// tutuyoruz — thinking.ts ve attachments.ts ile aynı desen. Konuşma store'undan
// item düşerse kayıt da kendiliğinden düşer.

import type { UploadResponse } from "@dima/contracts";

const datasets = new WeakMap<object, UploadResponse>();

export function markDataset(item: object, res: UploadResponse): void {
  datasets.set(item, res);
}

export function datasetOf(item: object): UploadResponse | undefined {
  return datasets.get(item);
}

/** Tabloya dönüşebilecek dosya mı — .xlsx/.xls/.csv dışındakiler yüklenmez. */
export function isDatasetFile(file: File): boolean {
  return /\.(xlsx|xls|csv)$/i.test(file.name);
}
