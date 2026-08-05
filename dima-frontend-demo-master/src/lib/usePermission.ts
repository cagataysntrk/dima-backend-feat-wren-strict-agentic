"use client";

// İzinler (/auth/me permissions) — kaynak backend authorize matrisi; rol semantiği
// UI'a KOPYALANMAZ, rol açmak yalnız backend değişikliğidir. Liste yüklenene kadar
// izinli varsayılır (regresyon olmasın); backend her eylemi kendi tarafında da zorlar.
// ReportPanel'in yerel `usePermission`'ıyla AYNI desen (useFeature.ts'in izin karşılığı) —
// page/rail gibi ortak tüketiciler için.

import { useEffect, useState } from "react";
import { getMe } from "@/lib/api-client";

let _perms: string[] | null = null;
let _super: boolean | null = null;

/** 🔴 TEK UÇUŞ: iki kanca da **aynı** `/auth/me` çağrısını paylaşır.
 *
 * ⚠ İkinci bir `getMe()` mekanizması açmak, aynı yanıtı iki kez istemek ve iki ayrı
 * önbellek tutmak olurdu — bu deponun defterindeki *"aynı kuralın iki sahibi"*
 * sınıfının ağ hâli. Söz veren `Promise` paylaşılır; ikinci çağıran onu **bekler**. */
let _uçuş: Promise<void> | null = null;

function _yukle(): Promise<void> {
  if (_uçuş) return _uçuş;
  _uçuş = getMe()
    .then((me) => {
      _perms = me.permissions ?? [];
      _super = !!me.is_superadmin;
    })
    .catch(() => {
      // ⚠ Yutmak DEĞİL, geri çekilmek: `/auth/me` okunamadıysa yetkiyi VARSAYMAYIZ
      // ama izinleri de kilitlemeyiz (regresyon olmasın; sınırı backend zaten zorlar).
      _uçuş = null;
    });
  return _uçuş;
}

/** ⚠ Her iki kanca da **her zaman** `_yukle()` üzerinden geçer, "zaten yüklüyse
 *  senkron ata" kısayolu kullanmaz. İki sebep:
 *  1. `setState`i doğrudan bir effect gövdesinde çağırmak React'ın uyardığı desendir
 *     (`react-hooks/set-state-in-effect`) — ve uyarı haklı: fazladan bir render turu.
 *  2. Yüklü olsa bile `_yukle()` **çözülmüş** promise'i döndürür; `.then` bir
 *     mikro-görevde koşar, yani atama effect'in dışına düşer. *Bir kısayol, tek bir
 *     mikro-görev kazandırıp bir sınıf hata açıyorsa kısayol değildir.* */
export function usePermission(action: string): boolean {
  const [ok, setOk] = useState<boolean>(() => (_perms ? _perms.includes(action) : true));
  useEffect(() => {
    let iptal = false;
    _yukle().then(() => { if (!iptal) setOk((_perms ?? []).includes(action)); });
    return () => { iptal = true; };
  }, [action]);
  return ok;
}

/** Süperadmin mi — *"portföy"* kapsamının **görünürlük** kararı için.
 *
 * 🔴 Bu bir güvenlik sınırı DEĞİLDİR: sınırı `authorize()` + RLS koyar ve backend her
 * eylemi kendi tarafında da zorlar. Burada verilen karar yalnız **kullanıcıya
 * yapamayacağı bir şeyi teklif etmeme nezaketidir**.
 *
 * ⚠ Varsayılan `false` (izinlerin tersine): bilinmeyen bir kullanıcıya süperadmin
 * seçeneği **göstermek**, ona çalışmayacak bir düğme vaat etmektir. *Bir yetkiyi
 * varsaymak ile bir izni varsaymak aynı şey değildir.* */
export function useSuperadmin(): boolean {
  const [ok, setOk] = useState<boolean>(() => _super ?? false);
  useEffect(() => {
    let iptal = false;
    _yukle().then(() => { if (!iptal) setOk(_super ?? false); });
    return () => { iptal = true; };
  }, []);
  return ok;
}
