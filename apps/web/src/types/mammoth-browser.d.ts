// mammoth'un tarayıcı derlemesi (`mammoth/mammoth.browser`) tip taşımıyor;
// paketin kendi .d.ts'i yalnız Node girişini kapsıyor. Kullandığımız tek
// yüzeyi burada daraltarak bildiriyoruz — `any` sızdırmıyoruz.
declare module "mammoth/mammoth.browser" {
  interface ConvertResult {
    value: string;
    messages: { type: string; message: string }[];
  }
  const mammoth: {
    convertToHtml(input: { arrayBuffer: ArrayBuffer }): Promise<ConvertResult>;
    extractRawText(input: { arrayBuffer: ArrayBuffer }): Promise<ConvertResult>;
  };
  export default mammoth;
}
