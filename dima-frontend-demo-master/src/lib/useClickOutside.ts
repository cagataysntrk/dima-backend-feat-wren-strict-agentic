import { useEffect, useRef } from "react";

/**
 * Dışarı-tıklama ile kapatma: `active` iken, `ref`li elemanın DIŞINA mousedown/touchstart
 * gelince `onClose` çağrılır. Boş sayfaya ya da BAŞKA bir komponentin dropdown'ına tıklamak
 * bu dropdown'ı kapatır (her dropdown'lı komponent bu hook'u kullanır → tek-açık davranışı).
 * Not: aynı komponentteki başka bir tetikleyici ref İÇİNDE olduğu için kapanmaz — o kendi
 * state'iyle geçiş yapar (ör. InterpretationBar'ın tek `openFilter`'ı).
 */
export function useClickOutside<T extends HTMLElement>(active: boolean, onClose: () => void) {
  const ref = useRef<T>(null);
  useEffect(() => {
    if (!active) return;
    const handler = (e: MouseEvent | TouchEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) onClose();
    };
    document.addEventListener("mousedown", handler);
    document.addEventListener("touchstart", handler);
    return () => {
      document.removeEventListener("mousedown", handler);
      document.removeEventListener("touchstart", handler);
    };
  }, [active, onClose]);
  return ref;
}
