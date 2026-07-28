"use client";

// Dikte — tarayıcının yerleşik Web Speech API'si (SpeechRecognition). Ses hiçbir
// yere GÖNDERİLMEZ: tanıma tarayıcıda/işletim sisteminde olur, biz yalnız metni
// alırız. Desteklemeyen tarayıcılarda `supported` false döner ve buton kapanır.

import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from "react";

interface SpeechAlternative {
  transcript: string;
}
interface SpeechResult {
  0: SpeechAlternative;
  isFinal: boolean;
}
interface SpeechEvent {
  resultIndex: number;
  results: { length: number; [i: number]: SpeechResult };
}
interface SpeechRecognizer {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start(): void;
  stop(): void;
  onresult: ((e: SpeechEvent) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
}
type RecognizerCtor = new () => SpeechRecognizer;

function getCtor(): RecognizerCtor | null {
  if (typeof window === "undefined") return null;
  const w = window as unknown as {
    SpeechRecognition?: RecognizerCtor;
    webkitSpeechRecognition?: RecognizerCtor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

export function useSpeech(locale: string, onText: (text: string) => void) {
  const [listening, setListening] = useState(false);
  const ref = useRef<SpeechRecognizer | null>(null);
  const onTextRef = useRef(onText);
  // callback'i render sırasında değil, commit'ten sonra tazele
  useEffect(() => {
    onTextRef.current = onText;
  }, [onText]);

  // sunucuda false, istemcide gerçek yetenek — setState-in-effect olmadan
  const supported = useSyncExternalStore(
    () => () => {},
    () => getCtor() !== null,
    () => false,
  );

  const stop = useCallback(() => {
    ref.current?.stop();
    ref.current = null;
    setListening(false);
  }, []);

  const start = useCallback(() => {
    const Ctor = getCtor();
    if (!Ctor) return;
    const rec = new Ctor();
    rec.lang = locale === "en" ? "en-US" : "tr-TR";
    rec.continuous = true;
    rec.interimResults = false;
    rec.onresult = (e) => {
      let text = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) text += e.results[i][0].transcript;
      }
      if (text.trim()) onTextRef.current(text.trim());
    };
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);
    ref.current = rec;
    rec.start();
    setListening(true);
  }, [locale]);

  // sayfadan ayrılırken mikrofonu bırak
  useEffect(() => () => ref.current?.stop(), []);

  return { listening, supported, toggle: () => (listening ? stop() : start()) };
}
