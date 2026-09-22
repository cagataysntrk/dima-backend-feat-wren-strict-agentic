import type { QueryResult } from "@/lib/types";
import { FastResultCard } from "./FastResultCard";

type Provenance = {
  source: string;
  gateway_tested_commit: string;
  metabase_runtime: string;
  metabase_image_digest: string;
  data_class: string;
  note: string;
};

export function FastAnalystPoc({
  result,
  provenance,
}: {
  result: QueryResult;
  provenance: Provenance;
}) {
  return (
    <main
      data-fast-poc="true"
      data-fast-shell
      className="h-full overflow-y-auto bg-background text-foreground"
    >
      <div className="mx-auto w-full max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
        <header className="border-b border-hairline pb-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-accent">
                DIMA · Fast Track
              </p>
              <h1 className="mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">
                Analyst rendering POC
              </h1>
            </div>
            <span className="border border-hairline px-2 py-1 font-mono text-[10px] uppercase text-neutral-500">
              FT-UI-002
            </span>
          </div>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-neutral-500">
            Dima kullanıcı ürünüdür; Metabase görünmeyen analitik motordur. Bu izole ekran yalnız
            gerçek Metabase sonuç şeklinin Dima-native analist akışında tablo ve grafik olarak
            sunulabildiğini kanıtlar.
          </p>
        </header>

        <section className="py-6" aria-labelledby="poc-intent">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-neutral-500">
            POC intent
          </p>
          <h2 id="poc-intent" className="mt-2 text-lg font-medium">
            “Gerçek analitik sonucu Dima içinde en sade biçimde gösterebilir miyiz?”
          </h2>
          <p className="mt-2 text-sm text-neutral-500">
            Bu bir kullanıcı cevabı değildir. Soru yalnız rendering/composition gate’ini sınar.
          </p>
        </section>

        <FastResultCard result={result} />

        <section className="mt-5 grid gap-4 md:grid-cols-[1.4fr_1fr]">
          <div className="border border-hairline p-4">
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-neutral-500">
              Kanıt / provenance
            </p>
            <dl className="mt-3 grid gap-2 text-sm">
              <div className="flex flex-wrap justify-between gap-2 border-b border-hairline pb-2">
                <dt className="text-neutral-500">Kaynak</dt>
                <dd className="font-mono text-[11px]">{provenance.source}</dd>
              </div>
              <div className="flex flex-wrap justify-between gap-2 border-b border-hairline pb-2">
                <dt className="text-neutral-500">Metabase</dt>
                <dd className="font-mono text-[11px]">{provenance.metabase_runtime}</dd>
              </div>
              <div className="flex flex-wrap justify-between gap-2 border-b border-hairline pb-2">
                <dt className="text-neutral-500">Veri sınıfı</dt>
                <dd className="font-mono text-[11px]">{provenance.data_class}</dd>
              </div>
              <div className="flex flex-wrap justify-between gap-2">
                <dt className="text-neutral-500">Gateway proof</dt>
                <dd className="max-w-full break-all font-mono text-[10px]">
                  {provenance.gateway_tested_commit}
                </dd>
              </div>
            </dl>
          </div>

          <div className="border border-hairline p-4">
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-neutral-500">
              Sonraki ürün eylemleri
            </p>
            <p className="mt-3 text-sm leading-6 text-neutral-500">
              Bu butonlar POC’ta bilinçli olarak pasif. Gerçek davranış FT-003 ve sonraki
              ürün ticket’larında kanıtlanacak.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {["Derinleştir", "Karar Kaydet", "Raporla"].map((label) => (
                <button
                  key={label}
                  type="button"
                  disabled
                  className="cursor-not-allowed border border-hairline px-3 py-2 text-xs opacity-[var(--opacity-disabled)]"
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </section>

        <p className="mt-5 font-mono text-[10px] leading-5 text-neutral-500">
          {provenance.note}
        </p>
      </div>
    </main>
  );
}
