"use client";

/** FAZ 7.11 · **DCM MODU** — *Deterministik Cevap Modu.* [bayrak: `ui_dcm_modu`]
 *
 * ## Neden var
 *
 * Banka/kamu alıcısı için **tam görünürlük** modu: sohbet **serbest metin kabul etmez**,
 * cevap üç tıkla ve **LLM'e hiç gidilmeden** üretilir. Sürüm 1'de yalnız EK D'de
 * *"DCM 3 tık"* **sayısı** vardı ve madde yoktu — *bir sayı bir işi tarif etmez.*
 *
 * ## 🔴 Metin kutusunu gizlemek bir GARANTİ DEĞİLDİR
 *
 * Bu maddenin en kolay yanlış uygulaması, `<textarea>`'yı `hidden` yapıp işi bitmiş
 * saymaktır. O bir **görünüm kararıdır**; kullanıcı (ya da bir betik) uca doğrudan
 * serbest metin gönderebilir ve akış LLM'e düşer. **Garantiyi sunucu verir:** akış
 * `POST /cube` kullanır — bir `cube_query`'yi **LLM'siz** koşan uç. Serbest metin diye
 * bir şey **hiç oluşmaz**, gizlenmez.
 *
 * ## ⚠ "Altın rozet" maddesi — bilinçli olarak UYGULANMADI, ve sebebi yazılı
 *
 * Yol haritası *"tüm sonuçlar **altın rozet**"* diyor. FAZ 7.8/K2 tam da bunu
 * **kaldırdı**: `🥇` + `Yüksek güven (100%)` kalibre edilmemiş bir yol etiketiydi ve
 * MIMARI §9'un *"o sayı bir güven değil bir SÜStür"* yasağının canlı ihlaliydi.
 *
 * 🔴 **İki madde çatışıyorsa mimari kural kazanır** — ve çatışma **gizlenmez**. DCM'in
 * vaat ettiği şey zaten `◆ CUBE` rozetinde **ölçülmüş** olarak duruyor: bu modda her
 * cevap `route()`/`/cube` yolundan gelir, yani rozet bir süs değil bir **olgudur**.
 * *Bir garantiyi ikinci kez, kalibre edilmemiş bir sayıyla söylemek onu güçlendirmez —
 * zayıflatır.*
 *
 * ## Üç tık — ve neden dördüncü bir "çalıştır" düğmesi yok
 *
 * `ölçü` → `analiz tipi` → `dönem`. Üçüncü seçim **doğrudan koşar**. Ayrı bir "çalıştır"
 * düğmesi kapıyı **dört tığa** çıkarırdı ve hiçbir bilgi eklemezdi: üçüncü seçimden
 * sonra sorunun tanımı **tamamlanmıştır**.
 */

import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { askCube, getSchema } from "@/lib/api-client";
import type { AskResponse, CubeQuery } from "@/lib/types";

/** Analiz tipleri — **kapalı** bir liste. ⚠ Serbest metin kabul etmeyen bir modda
 *  seçenek kümesi de kapalı olmalı: "diğer…" diye bir madde, serbest metni arka kapıdan
 *  geri getirirdi. */
const ANALIZ = [
  { id: "toplam", ad: "toplam", aciklama: "tek sayı" },
  { id: "kirilim", ad: "kırılım", aciklama: "boyuta göre dağılım" },
  { id: "trend", ad: "trend", aciklama: "zaman içinde" },
] as const;

type AnalizId = (typeof ANALIZ)[number]["id"];

/** Dönem seçenekleri — `timeDimensions.granularity` değerleri. ⚠ *"Bu yıl"* gibi
 *  **göreli** bir ifade burada yok: göreli dönemin çözümü bir tarih hesabıdır ve onun
 *  sahibi backend'dir (`cube_router`). İki sahip, iki farklı "bu yıl" demektir. */
const DONEM = [
  { id: "month", ad: "aylık" },
  { id: "quarter", ad: "çeyreklik" },
  { id: "year", ad: "yıllık" },
] as const;

type DonemId = (typeof DONEM)[number]["id"];

export function DcmAkisi({
  sessionId,
  onSonuc,
}: {
  sessionId?: string;
  onSonuc: (r: AskResponse) => void;
}) {
  const [olcu, setOlcu] = useState<{ cube: string; measure: string } | null>(null);
  const [analiz, setAnaliz] = useState<AnalizId | null>(null);

  const sema = useQuery({ queryKey: ["schema"], queryFn: () => getSchema() });
  const kos = useMutation({
    mutationFn: (cq: CubeQuery) => askCube({ cube_query: cq, session_id: sessionId }),
    onSuccess: onSonuc,
  });

  const cubelar = sema.data?.cubes ?? [];

  /** 🔴 `cube_query` **burada** kurulur ve backend'e olduğu gibi gider: hiçbir yerde bir
   *  cümle oluşmaz, dolayısıyla çözülecek bir cümle de yoktur. */
  const calistir = (donem: DonemId) => {
    if (!olcu || !analiz) return;
    const meta = cubelar.find((c) => c.name === olcu.cube);
    const zaman = meta?.time_dimensions?.[0];
    const cq: CubeQuery = { cube: olcu.cube, measures: [olcu.measure] };
    if (analiz === "kirilim") {
      const boyut = meta?.dimensions?.[0];
      // ⚠ Boyutu olmayan bir cube'da "kırılım" **sessizce toplama düşmez**: seçenek
      // zaten sunulmaz (aşağıda `disabled`). Burada da savunma var — iki kapı, çünkü
      // sessiz bir dejenerasyon kullanıcıya "kırılım budur" der.
      if (boyut) (cq as Record<string, unknown>).dimensions = [boyut];
    }
    if (analiz === "trend" && zaman) {
      (cq as Record<string, unknown>).timeDimensions = [
        { dimension: zaman, granularity: donem },
      ];
    }
    kos.mutate(cq);
  };

  const secilenMeta = olcu ? cubelar.find((c) => c.name === olcu.cube) : null;
  const kirilimMumkun = Boolean(secilenMeta?.dimensions?.length);
  const trendMumkun = Boolean(secilenMeta?.time_dimensions?.length);

  return (
    <div className="flex flex-col gap-4 p-4" data-dcm>
      {/* 🔴 Sabit rozet — HER ekranda. Bir mod, ancak açık olduğu **görülüyorsa** bir
          moddur; sessiz bir kısıtlama, kullanıcıya ürünü bozuk gösterir. */}
      <div className="flex items-center gap-2">
        <span
          className="border border-accent/50 px-2 py-0.5 font-mono text-[var(--text-etiket)] uppercase tracking-wider text-accent"
          title="Deterministik Cevap Modu: serbest metin kabul edilmez, her cevap LLM'siz cube yolundan üretilir."
        >
          DCM Aktif
        </span>
        <span className="font-mono text-[11px] text-neutral-400">
          serbest metin yok · her cevap LLM&apos;siz cube yolundan
        </span>
      </div>

      {/* 1. TIK — ölçü */}
      <Adim no={1} baslik="ölçü" secili={olcu ? `${olcu.cube} · ${olcu.measure}` : null}>
        <div className="flex flex-wrap gap-1.5">
          {cubelar.flatMap((c) =>
            (c.measures ?? []).map((m) => (
              <Secenek
                key={`${c.name}.${m}`}
                secili={olcu?.cube === c.name && olcu?.measure === m}
                onClick={() => {
                  setOlcu({ cube: c.name, measure: m });
                  setAnaliz(null);
                }}
              >
                {m}
              </Secenek>
            )),
          )}
        </div>
      </Adim>

      {/* 2. TIK — analiz tipi */}
      {olcu && (
        <Adim no={2} baslik="analiz" secili={analiz}>
          <div className="flex flex-wrap gap-1.5">
            {ANALIZ.map((a) => {
              const kapali =
                (a.id === "kirilim" && !kirilimMumkun) || (a.id === "trend" && !trendMumkun);
              return (
                <Secenek
                  key={a.id}
                  secili={analiz === a.id}
                  kapali={kapali}
                  baslik={
                    kapali
                      ? a.id === "kirilim"
                        ? "Bu ölçünün cube'unda kırılabilecek bir boyut yok"
                        : "Bu ölçünün cube'unda zaman boyutu yok"
                      : a.aciklama
                  }
                  onClick={() => setAnaliz(a.id)}
                >
                  {a.ad}
                </Secenek>
              );
            })}
          </div>
        </Adim>
      )}

      {/* 3. TIK — dönem; seçim DOĞRUDAN koşar (dördüncü tık yok) */}
      {olcu && analiz && (
        <Adim no={3} baslik="dönem" secili={null}>
          <div className="flex flex-wrap gap-1.5">
            {DONEM.map((d) => (
              <Secenek key={d.id} kapali={kos.isPending} onClick={() => calistir(d.id)}>
                {d.ad}
              </Secenek>
            ))}
          </div>
        </Adim>
      )}

      {kos.isPending && (
        <p className="font-mono text-[11px] text-neutral-400">çalışıyor…</p>
      )}
      {/* ⚠ Hata **gizlenmez**: DCM'in vaadi görünürlüktür; sessizce boş dönen bir akış
          o vaadi tam da en çok gerektiği anda bozar. */}
      {kos.isError && (
        <p className="font-mono text-[11px] text-[var(--negative)]">
          Sorgu çalıştırılamadı. Seçimi değiştirip tekrar deneyin.
        </p>
      )}
    </div>
  );
}

function Adim({
  no,
  baslik,
  secili,
  children,
}: {
  no: number;
  baslik: string;
  secili: string | null;
  children: React.ReactNode;
}) {
  return (
    <section className="border border-hairline p-3">
      <h3 className="mb-2 font-mono text-[var(--text-etiket)] uppercase tracking-wider text-neutral-400">
        {no}. {baslik}
        {secili && <span className="ml-2 text-accent">{secili}</span>}
      </h3>
      {children}
    </section>
  );
}

function Secenek({
  children,
  secili = false,
  kapali = false,
  baslik,
  onClick,
}: {
  children: React.ReactNode;
  secili?: boolean;
  kapali?: boolean;
  baslik?: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      disabled={kapali}
      title={baslik}
      aria-pressed={secili}
      className={`border px-2 py-1 font-mono text-[11px] transition-colors disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)] ${
        secili
          ? "border-accent text-accent"
          : "border-hairline text-neutral-500 hover:border-accent/50 hover:text-foreground"
      }`}
    >
      {children}
    </button>
  );
}
