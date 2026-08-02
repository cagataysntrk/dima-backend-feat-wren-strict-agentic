"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { askContribution } from "@/lib/api-client";
import { fmtValue } from "@/lib/format";
import type {
  ContributionFinding,
  ContributionResponse,
  CubeQuery,
  PvmFinding,
  WaterfallSpec,
} from "@/lib/types";

// FAZ H2 — "NEDEN DEĞİŞTİ?" cevabın İÇİNDE bir KATMAN, ayrı bir panel DEĞİL.
//
// Backend'de `POST /ask/contribution` Faz 5.1/5.2'de yazıldı (katkı ayrıştırması + PVM),
// testleri vardı, çalışıyordu — ve HİÇBİR frontend tüketicisi yoktu. Denetimde yakalandı
// (`tests/test_uc_yetim_degil.py` artık bunu CI'da tutuyor).
//
// Neden panel değil katman: her yetenek için bir `*Panel` açmak bugünkü desendi
// (DrillDownPanel, DashboardsPanel, SchedulesPanel, ReportPanel, SchemaPanel, HistoryPanel,
// ContractDetailPanel, ConnectionReviewPanel, ReviewPanel, HelpPanel…). Şartnamedeki
// özelliklerin onda biri eklense arayüz kullanılamaz hale gelir. Kural: **tek cevap yüzeyi
// + kademeli açılım** — kök neden, katkı, PVM, köken, makbuz hepsi cevabın KENDİ kartında
// açılır/kapanır.
//
// Ürünün tezi burada görünür hale gelir: her bulgu bir METİN DEĞİL, kendi `cube_query`'sini
// taşıyan tıklanabilir bir SORGUDUR. Tıklanınca `/cube` ile LLM'siz koşar ve kendi Query
// Contract'ını üretir. Snowflake TOP_INSIGHTS / Power BI Key Influencers / Tableau Pulse —
// hepsi semantic layer'ın DIŞINDA çalışır, dolayısıyla bulguları yeniden çalıştırılabilir
// değildir.

function Yuzde({ v }: { v: number | null }) {
  // `null` = "net değişim ~0, pay TANIMSIZ". Backend bunu bilerek uydurmuyor; UI de
  // uydurmamalı — "%0" yazmak "katkısı yok" demektir ve bu YANLIŞ olur.
  if (v === null) return <span className="text-neutral-500">—</span>;
  const p = v * 100;
  return (
    <span className={p >= 0 ? "text-emerald-600" : "text-red-500"}>
      {p >= 0 ? "+" : ""}
      {p.toFixed(1)}%
    </span>
  );
}

function Delta({ v, col }: { v: number; col: string }) {
  return (
    <span className={v >= 0 ? "text-emerald-600" : "text-red-500"}>
      {v >= 0 ? "+" : ""}
      {fmtValue(v, col)}
    </span>
  );
}

function BulguSatiri({
  etiket,
  sag,
  detay,
  cq,
  onCubeEdit,
}: {
  etiket: string;
  sag: React.ReactNode;
  detay?: React.ReactNode;
  cq: CubeQuery;
  onCubeEdit?: (e: { cq: CubeQuery; label: string }) => void;
}) {
  const tiklanir = Boolean(onCubeEdit);
  return (
    <button
      type="button"
      disabled={!tiklanir}
      onClick={() => onCubeEdit?.({ cq, label: etiket })}
      title={tiklanir ? "Bu bulguyu tek başına aç — LLM'siz koşar, kendi makbuzunu üretir" : undefined}
      className={`flex w-full items-baseline justify-between gap-3 border-b border-hairline/40 px-1 py-1 text-left font-mono text-[11px] last:border-0 ${
        tiklanir ? "transition-colors hover:bg-foreground/[0.04]" : "cursor-default"
      }`}
    >
      <span className="min-w-0 flex-1 truncate text-neutral-300">
        {tiklanir && <span className="mr-1 text-neutral-500">↗</span>}
        {etiket}
      </span>
      {detay && <span className="shrink-0 text-neutral-500">{detay}</span>}
      <span className="shrink-0 tabular-nums">{sag}</span>
    </button>
  );
}

function SegmentRapor({
  r,
  measure,
  onCubeEdit,
}: {
  r: ContributionResponse["raporlar"][number];
  measure: string;
  onCubeEdit?: (e: { cq: CubeQuery; label: string }) => void;
}) {
  return (
    <div className="space-y-1">
      <div className="flex items-baseline justify-between font-mono text-[10px] uppercase text-neutral-400">
        <span>{r.dimension_label || r.dimension}</span>
        <span className="normal-case tabular-nums">
          net <Delta v={r.net_degisim} col={measure} />
        </span>
      </div>
      <div className="border border-hairline">
        {r.bulgular.map((b: ContributionFinding, i: number) => (
          <BulguSatiri
            key={`${b.label}-${i}`}
            etiket={b.label}
            detay={
              <>
                {fmtValue(b.onceki, measure)} → {fmtValue(b.simdi, measure)}
              </>
            }
            sag={
              <>
                <Delta v={b.delta} col={measure} />{" "}
                <span className="text-neutral-500">(</span>
                <Yuzde v={b.net_pay} />
                <span className="text-neutral-500">)</span>
              </>
            }
            cq={b.cube_query}
            onCubeEdit={onCubeEdit}
          />
        ))}
      </div>
      {r.kirpilan_segment > 0 && (
        // KIRPMA SESSİZ OLMAZ. "Veri yok" ile "kırpıldı" ayrı şeylerdir; ikincisini
        // göstermemek kapsamı sessizce daraltmaktır.
        <p className="font-mono text-[10px] text-neutral-500">
          {r.kirpilan_segment} segment eşiğin altında kaldı (|pay| &lt; %
          {(r.kirpilan_esik_yuzde * 100).toFixed(1)}) — gösterilmedi, yok sayılmadı.
        </p>
      )}
    </div>
  );
}

function Selale({ spec, col }: { spec: WaterfallSpec; col: string }) {
  // ŞELALE — "bu çubukları üst üste koyarsan sondaki değere varırsın." Backend bu
  // iddiayı ARTIKSIZLIK kapısıyla garanti eder (viz.waterfall_spec); tutmazsa `viz`
  // null gelir ve bu bileşen hiç render edilmez.
  //
  // Kütüphane KULLANILMADI: üç-dört adımlık bir şelale saf CSS ile çizilir ve
  // ECharts'ın waterfall'ı yığılmış-bar + görünmez taban numarasıdır (aynı sayıyı iki
  // seriye bölmek gerekir). Burada sayı BÖLÜNMEZ — okunan değer gösterilen değerdir.
  // Kümülatif taban: her çubuk bir öncekinin bittiği yerden başlar. `reduce` ile SAF
  // birikim — dışarıdan bir sayacı `map` içinde mutasyona uğratmak react-compiler'ın
  // değişmezlik kuralını ihlal ediyordu (eslint yakaladı) ve render sırası değişirse
  // sessizce yanlış tabanlar üretirdi.
  const kutular = spec.steps.reduce<
    { label: string; value: number; taban: number; tepe: number }[]
  >((acc, a) => {
    const taban = acc.length ? acc[acc.length - 1].tepe : spec.start.value;
    return [...acc, { ...a, taban, tepe: taban + a.value }];
  }, []);
  const tumDegerler = [spec.start.value, spec.end.value, ...kutular.flatMap((k) => [k.taban, k.tepe])];
  const enAz = Math.min(...tumDegerler, 0);
  const enCok = Math.max(...tumDegerler, 0);
  const aralik = enCok - enAz || 1;
  const yuzde = (v: number) => ((v - enAz) / aralik) * 100;

  return (
    <div className="space-y-1">
      <div className="flex h-28 items-end gap-1 border-b border-hairline">
        {kutular.map((k, i) => {
          const alt = Math.min(k.taban, k.tepe);
          const ust = Math.max(k.taban, k.tepe);
          return (
            <div key={`${k.label}-${i}`} className="relative flex flex-1 flex-col justify-end"
                 style={{ height: "100%" }}
                 title={`${k.label}: ${fmtValue(k.value, col)}`}>
              <div
                className={k.value >= 0 ? "bg-emerald-600/70" : "bg-red-500/70"}
                style={{
                  position: "absolute",
                  bottom: `${yuzde(alt)}%`,
                  height: `${Math.max(1, yuzde(ust) - yuzde(alt))}%`,
                  left: 0, right: 0,
                }}
              />
            </div>
          );
        })}
        {/* SONUÇ çubuğu — sıfırdan nete kadar tam yükseklik: "vardığımız yer burası". */}
        <div className="relative flex flex-1 flex-col justify-end" style={{ height: "100%" }}
             title={`${spec.end.label}: ${fmtValue(spec.end.value, col)}`}>
          <div
            className="bg-foreground/60"
            style={{
              position: "absolute",
              bottom: `${yuzde(Math.min(0, spec.end.value))}%`,
              height: `${Math.max(1, yuzde(Math.max(0, spec.end.value)) - yuzde(Math.min(0, spec.end.value)))}%`,
              left: 0, right: 0,
            }}
          />
        </div>
      </div>
      <div className="flex gap-1 font-mono text-[10px] text-neutral-400">
        {kutular.map((k, i) => (
          <div key={`${k.label}-lbl-${i}`} className="flex-1 truncate text-center">
            {k.label}
            <div className={k.value >= 0 ? "text-emerald-600" : "text-red-500"}>
              {k.value >= 0 ? "+" : ""}
              {fmtValue(k.value, col)}
            </div>
          </div>
        ))}
        <div className="flex-1 truncate text-center text-foreground">
          = {spec.end.label}
          <div className="tabular-nums">{fmtValue(spec.end.value, col)}</div>
        </div>
      </div>
    </div>
  );
}

function PvmRapor({
  r,
  onCubeEdit,
}: {
  r: ContributionResponse["pvm_raporlar"][number];
  onCubeEdit?: (e: { cq: CubeQuery; label: string }) => void;
}) {
  const m = r.value_measure;
  return (
    <div className="space-y-1">
      <div className="font-mono text-[10px] uppercase text-neutral-400">
        {r.dimension_label || r.dimension} · {r.price_label}
      </div>
      {/* ŞELALE (Faz I2) — PVM'nin matematiği Faz 5.1'de yazılmıştı, GÖRSELİ YOKTU.
          Backend artıksızlık kapısını geçirdiyse `viz` dolu gelir; geçmediyse null
          gelir ve aşağıdaki ızgara TEK BAŞINA kalır (grafik susar, tablo konuşur). */}
      {r.viz && <Selale spec={r.viz} col={m} />}
      {/* ARTIKSIZ AYRIŞMA: fiyat + miktar + birleşik = net (birebir). Şelale yolu
          gösterir, ızgara SAYIYI verir — ikisi birbirinin yerine değil tamamlayıcısıdır
          (grafikten okunan değer her zaman yaklaşıktır; kesin sayı burada durur). */}
      <div className="grid grid-cols-4 gap-px border border-hairline bg-hairline/40 font-mono text-[11px]">
        {[
          ["fiyat", r.fiyat_etkisi],
          ["miktar", r.miktar_etkisi],
          ["birleşik", r.birlesik_etki],
          ["= net", r.net_degisim],
        ].map(([ad, v]) => (
          <div key={ad as string} className="bg-background px-2 py-1">
            <div className="text-[9px] uppercase text-neutral-400">{ad as string}</div>
            <div className="tabular-nums">
              <Delta v={v as number} col={m} />
            </div>
          </div>
        ))}
      </div>
      <div className="border border-hairline">
        {r.bulgular.map((b: PvmFinding, i: number) => (
          <BulguSatiri
            key={`${b.label}-${i}`}
            etiket={b.label}
            detay={
              <>
                {b.baskin_etken === "fiyat" ? "fiyat ▲" : "miktar ▲"} · f{" "}
                {fmtValue(b.fiyat_etkisi, m)} · m {fmtValue(b.miktar_etkisi, m)}
              </>
            }
            sag={<Delta v={b.delta} col={m} />}
            cq={b.cube_query}
            onCubeEdit={onCubeEdit}
          />
        ))}
      </div>
      {r.kirpilan_segment > 0 && (
        <p className="font-mono text-[10px] text-neutral-500">
          {r.kirpilan_segment} segment eşiğin altında kaldı — gösterilmedi, yok sayılmadı.
        </p>
      )}
    </div>
  );
}

export function ContributionLayer({
  cubeQuery,
  sessionId,
  onCubeEdit,
  hazir,
}: {
  cubeQuery: CubeQuery;
  sessionId?: string;
  onCubeEdit?: (e: { cq: CubeQuery; label: string }) => void;
  // HAZIR VERİ (Faz G1): kullanıcı "bu neden böyle?" diye SORDUĞUNDA backend ayrıştırmayı
  // zaten yapmıştır ve cevabın gövdesi olarak döner. O durumda bu bileşen fetch ETMEZ,
  // yalnız RENDER eder.
  //
  // Neden aynı bileşen: iki render edici (biri buton yolu, biri konuşma yolu) zamanla
  // AYRIŞIR — bu depoda o desen beş kez ölçüldü (fmt/stats/result_shape/fanout/_syn_hit).
  // Δ tutarı, % pay, kırpma uyarısı ve "pay tanımsız → —" kuralı tek yerde yaşamalı.
  hazir?: ContributionResponse | null;
}) {
  const [acik, setAcik] = useState(false);
  const [mode, setMode] = useState<"yoy" | "mom">("yoy");
  const [kind, setKind] = useState<"segment" | "pvm">("segment");

  // Parametreler mutation'a DEĞİŞKEN olarak geçer, kapanıştan okunmaz: `setMode` asenkron
  // olduğu için "geçen ay"a tıklandığında kapanış hâlâ ESKİ modu görür ve kullanıcı
  // sessizce yanlış dönemin ayrışmasını okurdu.
  const sor = useMutation({
    mutationFn: (v: { mode: "yoy" | "mom"; kind: "segment" | "pvm" }) =>
      askContribution({ cube_query: cubeQuery, ...v, session_id: sessionId }),
  });

  // Hazır veri varsa O otoritedir: kullanıcı zaten sordu, cevabı geldi.
  const d = hazir ?? sor.data;
  const measure = d?.measure ?? "";
  const konusmaCevabi = Boolean(hazir);

  const calistir = (m: "yoy" | "mom", k: "segment" | "pvm") => {
    setMode(m);
    setKind(k);
    setAcik(true);
    sor.mutate({ mode: m, kind: k });
  };

  const gorunur = konusmaCevabi || acik;

  return (
    <div className="mt-2">
      {/* Konuşma cevabında "neden değişti?" butonu GÖSTERİLMEZ: kullanıcı zaten sordu ve
          cevap açık duruyor. Butonu da göstermek aynı yeteneğe iki giriş noktası koyar
          ve kullanıcı "tıklasam ne olur?" diye düşünür — üst üste binme tam olarak budur. */}
      <div className={`flex flex-wrap items-center gap-1.5 ${konusmaCevabi ? "hidden" : ""}`}>
        <button
          onClick={() => (acik ? setAcik(false) : calistir(mode, kind))}
          title="Geçen döneme göre NE DEĞİŞTİ ve kim sürükledi? (DEĞİŞİM analizi — mevcut seviyenin kırılımı için «⤵ kırılıma in»)"
          className={`border px-2 py-[3px] font-mono text-[11px] transition-colors ${
            acik
              ? "border-accent/40 text-accent"
              : "border-hairline text-neutral-400 hover:border-accent hover:text-accent"
          }`}
        >
          {sor.isPending ? "hesaplanıyor…" : "𝚫 neden değişti?"}
        </button>
        {acik && (
          <>
            {(["yoy", "mom"] as const).map((m) => (
              <button
                key={m}
                onClick={() => calistir(m, kind)}
                className={`border px-2 py-[3px] font-mono text-[11px] transition-colors ${
                  mode === m
                    ? "border-accent/40 text-accent"
                    : "border-hairline text-neutral-500 hover:text-foreground"
                }`}
              >
                {m === "yoy" ? "geçen yıl" : "geçen ay"}
              </button>
            ))}
            {(["segment", "pvm"] as const).map((k) => (
              <button
                key={k}
                onClick={() => calistir(mode, k)}
                title={
                  k === "pvm"
                    ? "Fiyat / miktar / birleşik etki — yalnız cube'un pvm beyanı varsa"
                    : "Değişimi segmentlere dağıt"
                }
                className={`border px-2 py-[3px] font-mono text-[11px] transition-colors ${
                  kind === k
                    ? "border-accent/40 text-accent"
                    : "border-hairline text-neutral-500 hover:text-foreground"
                }`}
              >
                {k === "pvm" ? "fiyat/miktar" : "segment"}
              </button>
            ))}
          </>
        )}
      </div>

      {gorunur && (
        <div className="mt-2 space-y-3 border border-hairline p-2">
          {sor.isError && (
            <p className="font-mono text-[11px] text-red-500">
              Ayrıştırma çalıştırılamadı.
            </p>
          )}
          {/* DÜRÜST RED birinci sınıf: "toplanamayan ölçü" ya da "dönem yok" bir hata
              ekranı değil, bir AÇIKLAMADIR. Katkı payı yalnız TOPLANABİLİR ölçülerde
              tanımlıdır; AVG/oran/COUNT(DISTINCT) için "bu segment değişimin %40'ını
              açıklıyor" cümlesi matematiksel olarak YANLIŞ olur. */}
          {d?.note && (
            <p className="font-mono text-[11px] text-amber-600">{d.note}</p>
          )}
          {/* Hangi ayrışmanın gösterileceği CEVABIN kendi `kind`'ından okunur, yerel
              state'ten değil: ikisi bir an için ayrışabilir (istek uçarken kullanıcı sekme
              değiştirebilir) ve o anda ekranda "fiyat/miktar" yazarken segment tablosu
              durur. Ekrandaki etiket ile gösterilen veri asla çelişmemeli. */}
          {d?.kind === "segment" &&
            d.raporlar.map((r) => (
              <SegmentRapor key={r.dimension} r={r} measure={measure} onCubeEdit={onCubeEdit} />
            ))}
          {d?.kind === "pvm" &&
            d.pvm_raporlar.map((r) => (
              <PvmRapor key={r.dimension} r={r} onCubeEdit={onCubeEdit} />
            ))}
          {d && !d.note && d.raporlar.length === 0 && d.pvm_raporlar.length === 0 && (
            <p className="font-mono text-[11px] text-neutral-400">
              Anlamlı bir ayrışma bulunamadı — değişim tek bir segmentte yoğunlaşmıyor.
            </p>
          )}
          {d && d.taranmayan_boyut > 0 && (
            // Kapsam sessizce daraltılmaz (üst sınır bir performans kararıdır, bir cevap değil).
            <p className="font-mono text-[10px] text-neutral-500">
              {d.taranmayan_boyut} boyut üst sınır nedeniyle taranmadı.
            </p>
          )}
          {d && d.contract_ids.length > 0 && (
            <p className="font-mono text-[10px] text-neutral-500">
              {d.contract_ids.length} makbuz üretildi — her bulgu ayrı ayrı kanıtlanabilir.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
