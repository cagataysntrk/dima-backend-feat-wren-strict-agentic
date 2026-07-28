/**
 * dima-backend'e giden TEK HTTP yüzeyi (saka-standards: dağınık `fetch` yok).
 *
 * KALAN WEB VARSAYIMI — bilinçli, çözülmedi:
 * Refresh token HTTP-only bir cookie'de ve `withCredentials` ile taşınıyor.
 * Bu, tarayıcıda doğru olan tasarım: JS token'a erişemez, XSS çalamaz.
 * Masaüstünde (Tauri/Electron) same-origin bir sunucu olmadığı için cookie
 * kurulamaz; refresh token'ın işletim sistemi anahtarlığında (Keychain /
 * Credential Manager) tutulup istek gövdesinde gönderilmesi gerekecek.
 *
 * O adımı ŞİMDİ yazmıyorum: test edilemez ve güvenlik modelini değiştirir.
 * Değişecek yer burası — `doRefresh()` ve `withCredentials`. Erişim token'ı
 * her platformda bellekte kalır, localStorage'a ASLA yazılmaz.
 */
export * from "./api-client";
