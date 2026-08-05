"use client";

/** FAZ 7.7 · **KİM OLARAK GİRİLDİ** — `/auth/me`'nin görünür yüzü.
 *
 * ## Ölçülen kusur
 *
 * `getMe()` depoda **tek bir yerde** çağrılıyordu (`usePermission`) ve orada yalnız
 * `permissions` okunuyordu. **E-posta, rol, tenant: hiçbiri render edilmiyordu.**
 *
 * 🔴 Ve bu, bir "eksik özellik"ten daha ciddiydi: `AuthUser` tipi `email`i **zorunlu**
 * ilan ediyordu ama `/auth/me` onu **hiç göndermiyordu**. TypeScript `me.email`in var
 * olduğuna inanıyor, çalışma zamanında `undefined` geliyordu — *bir tür sistemi tam da
 * engellemesi gereken şeyi onaylıyordu.* İkisi de bu turda düzeltildi.
 *
 * ## Neden bu bir güvenlik yüzeyidir, bir süs değil
 *
 * Çok kiracılı bir üründe **hangi şirketin verisine baktığını bilmemek**, yanlış şirket
 * hakkında karar vermenin ta kendisidir. Ve süperadmin bir tenant'a **girebiliyorsa**,
 * o hâlin ekranda **sabit** durması gerekir: *geçici bir yetkiyi görünmez yapmak, onu
 * kalıcı bir yetkiye çevirir.*
 *
 * ⚠ Rol **backend'den okunur, türetilmez**: `authorize()` matrisi UI'a KOPYALANMAZ
 * (CLAUDE.md). Burada yalnız `roles` dizisi **gösterilir**; ondan bir yetki **çıkarılmaz**.
 *
 * ## K5 — yeni panel değil
 *
 * Bu bir **şerit**tir, bir panel değil (`export function …Panel` DEĞİL): panel tavanı
 * 13/13 dolu ve *bir yetenek bir panel doğurmaz*.
 */

import { useQuery } from "@tanstack/react-query";
import { usePathname } from "next/navigation";

import { getMe } from "@/lib/api-client";

export function KimlikSeridi() {
  const pathname = usePathname();
  // ⚠ `/login`'de kimlik **yoktur** ve sormak 401 üretirdi — bir hata gibi görünen bir
  // gürültü. `ConnectionBadge`/`LogoutButton` ile aynı desen.
  const girisSayfasi = pathname === "/login";
  const { data: ben, isError } = useQuery({
    queryKey: ["me"],
    queryFn: getMe,
    enabled: !girisSayfasi,
    // ⚠ Kimlik her odak değişiminde yeniden çekilmez: değişmesi bir **giriş** gerektirir
    // ve gereksiz istek, kimlik ucunu bir gürültü kaynağına çevirir.
    staleTime: 5 * 60_000,
    retry: false,
  });

  // ⚠ Hata **gizlenmiyor** ama alarma da çevrilmiyor: kimlik okunamıyorsa kullanıcı
  // bunu bilmeli, çünkü ekrandaki verinin **kime ait** olduğu da belirsizdir.
  if (girisSayfasi) return null;
  if (isError) {
    return (
      <span
        data-no-print
        className="fixed right-14 top-3 z-40 font-mono text-[10px] text-neutral-400 max-md:right-3"
        title="/auth/me okunamadı"
      >
        kimlik okunamadı
      </span>
    );
  }
  if (!ben) return null;

  const rol = ben.roles?.[0] ?? null;

  return (
    <span
      data-no-print
      className="fixed right-14 top-3 z-40 flex max-w-[min(22rem,55vw)] min-w-0 items-center gap-1.5 font-mono text-[10px] text-neutral-400 max-md:right-3"
    >
      {/* 🔴 E-posta `null` olabilir ve o hâl **yazılır**, boş bırakılmaz: boş bir alan
          "yüklenmedi" gibi okunur, oysa burada bilgi **yok**. */}
      <span className="truncate text-foreground" title={ben.email ?? undefined}>
        {ben.email ?? "e-posta kayıtlı değil"}
      </span>
      {rol && (
        <>
          <span aria-hidden>·</span>
          {/* ⚠ Rol GÖSTERİLİR, ondan yetki ÇIKARILMAZ — matris backend'dedir. */}
          <span title="Rol backend'in authorize() matrisinden gelir; arayüz onu kopyalamaz.">
            {rol}
          </span>
        </>
      )}
      {ben.is_superadmin && (
        <>
          <span aria-hidden>·</span>
          {/* 🔴 Sabit ve dikkat çekici: *geçici bir yetkiyi görünmez yapmak, onu kalıcı
              bir yetkiye çevirir.* */}
          <span
            className="border border-amber-600/60 px-1 text-amber-600"
            title="Süperadmin oturumu — bu ekrandaki veriler kendi şirketiniz DIŞINDAN olabilir."
          >
            süperadmin
          </span>
        </>
      )}
    </span>
  );
}
