/** **MUTASYON HATASI** — bir yazma isteği başarısız olduğunda kullanıcı ne görür.
 *
 * ## 🔴 Ölçülen kusur (denetim F3)
 *
 * `DashboardsPanel` (4 mutasyon) · `TercihlerPanel` (4) · `HistoryPanel` (2) —
 * **onError: 0, isError: 0**. 403 dönen bir *"Panoyu sil"* ekranda **hiçbir iz
 * bırakmıyordu**: düğmeye basılır, hiçbir şey olmaz, kullanıcı tekrar basar.
 *
 * Ve bu, F1/F2 ile bir **zincir** oluşturuyordu:
 * *onay yok → başarısızlık bildirimi yok → geri alma yok.*
 *
 * > 🔴 *Sessizce başarısız olan bir eylem, kullanıcıya ürünün bozuk olduğunu değil,
 * > **kendisinin yanlış yaptığını** düşündürür.*
 *
 * ## Neden tek yerde
 *
 * On mutasyona on ayrı `onError` yazmak **on sahip** demekti; dokuzu bir gün 403 ile
 * 500'ü aynı cümleyle anlatırdı. Eşleme burada **bir kez** yapılır.
 *
 * ## ⚠ Neden genel bir cümle DEĞİL
 *
 * *"Bir şeyler ters gitti"* bir bilgi değil bir **süstür**: kullanıcı ne yapacağını
 * bilemez. Her durum **ne olduğunu ve ne yapılacağını** söyler — ve ayrımın en önemlisi
 * **403 ile 500 arasındadır**: birinde tekrar denemek işe yaramaz, diğerinde yarar.
 */

/** HTTP durumu → düz Türkçe, **eylem önerisiyle**.
 *
 * ⚠ Bilinmeyen bir durum **gizlenmez**: kodu yazılır. *Anlaşılmayan bir hatayı
 * "bilinmeyen hata" diye yutmak, destek isteyen kullanıcıdan tek ipucunu alır.*
 */
export function hataMetni(e: unknown, ne: string): string {
  const yanit = (e as { response?: { status?: number; data?: { detail?: string } } })
    ?.response;
  const durum = yanit?.status;
  const detay = typeof yanit?.data?.detail === "string" ? yanit.data.detail : "";

  // 🔴 Sunucunun kendi cümlesi **öncelikli**: `detail` zaten kullanıcıya yazılmış bir
  // gerekçedir (ör. "Onay süresi doldu (30 dk)…") ve onu genel bir metinle ezmek,
  // sunucunun bildiği şeyi kullanıcıdan saklamaktır.
  if (detay && durum && durum < 500) return detay;

  switch (durum) {
    case 400:
      return `${ne} yapılamadı: istek geçersiz. Alanları kontrol edip tekrar deneyin.`;
    case 401:
      return "Oturumunuz sona ermiş. Sayfayı yenileyip tekrar giriş yapın.";
    case 403:
      // ⚠ *"Tekrar deneyin"* DEMİYOR: yetki eksikse tekrar denemek işe yaramaz ve
      // kullanıcıyı aynı duvara ikinci kez çarptırır.
      return `${ne} için yetkiniz yok. Bir yöneticiden isteyebilirsiniz.`;
    case 404:
      return `${ne} bulunamadı — başka biri silmiş olabilir. Listeyi yenileyin.`;
    case 409:
      return `${ne} çakıştı: kayıt bu arada değişmiş. Listeyi yenileyip tekrar deneyin.`;
    case 429:
      return `Çok fazla istek gönderildi. Birkaç saniye sonra tekrar deneyin.`;
    default:
      break;
  }
  if (durum && durum >= 500) {
    return `${ne} sunucu hatası nedeniyle tamamlanamadı (${durum}). Tekrar deneyebilirsiniz.`;
  }
  // ⚠ Ağ hatası ile sunucu hatası **ayrı**: birinde bağlantı, diğerinde ürün suçlu ve
  // kullanıcının yapacağı şey farklı.
  return `${ne} tamamlanamadı — bağlantı kurulamadı. İnternet bağlantınızı kontrol edin.`;
}
