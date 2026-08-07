"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useClickOutside } from "@/lib/useClickOutside";
import { getSchema } from "@/lib/api-client";
import type { CubeQuery } from "@/lib/types";

// Yorum çubuğu: sistemin sorudan çıkardığı YORUM (ölçü/kırılım/filtre/dönem) chip'ler
// olarak görünür ve OYNANABİLİR — UpcyBrain IntentRouter deseninin CubeQuery-natif hali.
// Her düzenleme deterministik /cube ucuna gider (LLM yok).

interface Filter {
  dimension: string;
  operator: string;
  value: string | string[];  // in-filtre: liste
}

type Edit = { cq: CubeQuery; label: string };

const chip =
  "inline-flex items-center gap-1 border border-hairline px-1.5 py-0.5 font-mono text-[11px] text-neutral-600 dark:text-neutral-300";
const xBtn =
  "ml-0.5 text-neutral-400 transition-colors hover:text-accent";

export function InterpretationBar({
  cq,
  onEdit,
}: {
  cq: CubeQuery;
  onEdit: (edit: Edit) => void;
}) {
  const { data: schema } = useQuery({ queryKey: ["schema"], queryFn: () => getSchema() });
  const [openFilter, setOpenFilter] = useState<string | null>(null);
  const [cStart, setCStart] = useState("");  // özel tarih aralığı (gte)
  const [cEnd, setCEnd] = useState("");      // özel tarih aralığı (lte)
  // Açık dropdown, çubuğun DIŞINA (boş sayfa ya da başka komponentin dropdown'ı) tıklanınca kapanır.
  const barRef = useClickOutside<HTMLDivElement>(openFilter != null, () => setOpenFilter(null));

  const measures = (cq.measures as string[]) ?? [];
  // CROSS-CUBE BLEND: başka cube'lardan katılan ölçüler (cq.blend). "kâr da ekle" tek
  // raporda ticaret + karlilik ölçüsünü birleştirir; burada cube etiketiyle gösterilir.
  const blend = (cq.blend as { cube: string; measures: string[] }[]) ?? [];
  const dims = (cq.dimensions as string[]) ?? [];
  const filters = (cq.filters as Filter[]) ?? [];
  const tds = (cq.timeDimensions as { dimension: string; granularity: string }[]) ?? [];

  const catFilters = filters.filter((f) => f.dimension !== "tarih");
  const dateFilters = filters.filter((f) => f.dimension === "tarih");

  // FAZ H5 — KÖKEN ROZETİ. Bir kırılımın NEREDEN geldiği bugüne kadar API'de vardı
  // (`dimension_origin`, Faz 1.1) ama UI'da hiç görünmüyordu; Faz D2'den beri yanında
  // **fan-out sertifikası** da geliyor. Kullanıcının "bu bölüm bilgisi makineler
  // tablosundan, 1 sıçrama, ölçülmüş" diyebilmesi güvenin GÖRÜNÜR halidir — ve fan-out
  // riski tam olarak burada yaşar: beyan yanlışsa sonuç hatasız, uyarısız ve "cube"
  // rozetiyle ŞİŞMİŞ gelir.
  const kokenFor = (dim: string) => {
    const cubeAdi = cq.cube as string | undefined;
    const c = (schema?.cubes ?? []).find((x) => x.name === cubeAdi);
    const o = c?.dimension_origin?.[dim];
    if (!o) return null;  // yerel boyut — köken sorusu anlamsız, rozet YOK
    const sert =
      o.certified === "olculdu:saglikli"
        ? { im: "✓", renk: "text-emerald-600", not: "fan-out ölçüldü: hedef anahtar benzersiz, NULL yok, öksüz satır yok" }
        : o.certified === "olculdu:riskli"
          ? { im: "⚠", renk: "text-amber-600", not: "fan-out ÖLÇÜLDÜ ve RİSKLİ — bu kırılımda toplamlar şişmiş olabilir" }
          : { im: "?", renk: "text-neutral-500", not: "bu join HENÜZ ÖLÇÜLMEDİ (sertifika üretilmemiş) — temiz olduğu iddia EDİLMİYOR" };
    return {
      ...sert,
      baslik: `${dim} — ${o.model}.${o.column} tablosundan, ${o.hops} sıçrama (${o.relationship}). ${sert.not}`,
    };
  };

  const KokenRozeti = ({ dim }: { dim: string }) => {
    const k = kokenFor(dim);
    if (!k) return null;
    return (
      <span className={`ml-1 cursor-help ${k.renk}`} title={k.baslik}>
        ⇱{k.im}
      </span>
    );
  };

  // Boyutun kategorik değerleri (şemadan) — filtre chip'i düzenlenirken seçenek olur.
  const valuesFor = (dim: string): string[] => {
    for (const m of schema?.models ?? []) {
      for (const c of m.columns) {
        if (c.name === dim && c.values) return c.values;
      }
    }
    return [];
  };

  const clone = (): CubeQuery => JSON.parse(JSON.stringify(cq));

  // Ölçü kaldırma (canlı 2026-07-25: kırılım/filtre/kova/dönem chip'lerinde × vardı ama
  // ÖLÇÜde yoktu → kullanıcı çok-ölçülü rapordan ölçü düşüremiyordu). Son ölçü korunur
  // (raporun en az bir ölçüsü olmalı); sıralama o ölçüye bağlıysa düşer. Deterministik /cube.
  const removeMeasure = (m: string) => {
    const next = clone();
    next.measures = measures.filter((x) => x !== m);
    const ord = next.order as { measure?: string } | undefined;
    if (ord?.measure === m) delete next.order;
    onEdit({ cq: next, label: `chip: ölçü − ${m}` });
  };

  // Blend ölçüsü kaldırma: cq.blend'den düşür; o cube'un ölçüsü kalmazsa entry'i at,
  // hiç blend kalmazsa alanı sil (tek-cube rapora döner). Deterministik /cube.
  const removeBlendMeasure = (cubeName: string, m: string) => {
    const next = clone();
    const nb = ((next.blend as { cube: string; measures: string[] }[]) ?? [])
      .map((b) => (b.cube === cubeName ? { ...b, measures: b.measures.filter((x) => x !== m) } : b))
      .filter((b) => b.measures.length > 0);
    if (nb.length) next.blend = nb;
    else delete next.blend;
    onEdit({ cq: next, label: `chip: ölçü − ${m}` });
  };

  const removeDim = (d: string) => {
    const next = clone();
    next.dimensions = dims.filter((x) => x !== d);
    if (!(next.dimensions as string[]).length) delete next.dimensions;
    // seçim kırılıma AİTTİR: kırılım kalkınca gizli in/eq filtresi arkada kalmasın
    next.filters = filters.filter((f) => f.dimension !== d);
    if (!(next.filters as Filter[]).length) delete next.filters;
    onEdit({ cq: next, label: `chip: kırılım − ${d}` });
  };

  const setGran = (g: string) => {
    const next = clone();
    next.timeDimensions = [{ dimension: "tarih", granularity: g }];
    onEdit({ cq: next, label: `chip: kova → ${g}` });
  };

  const removeGran = () => {
    const next = clone();
    delete next.timeDimensions;
    onEdit({ cq: next, label: "chip: zaman kovası kaldırıldı" });
  };

  const removeDateFilters = () => {
    const next = clone();
    next.filters = filters.filter((f) => f.dimension !== "tarih");
    if (!(next.filters as Filter[]).length) delete next.filters;
    delete next.ayrik_aylar;   // dönem kalkıyorsa ayrık-ay daraltması da kalkar (bkz. setPeriod)
    onEdit({ cq: next, label: "chip: dönem → tüm zamanlar" });
  };

  const setFilterValue = (dim: string, value: string) => {
    const next = clone();
    next.filters = [
      ...filters.filter((f) => f.dimension !== dim),
      { dimension: dim, operator: "eq", value },
    ];
    onEdit({ cq: next, label: `chip: ${dim} = ${value}` });
  };

  const filterToDim = (dim: string) => {
    const next = clone();
    next.filters = filters.filter((f) => f.dimension !== dim);
    if (!(next.filters as Filter[]).length) delete next.filters;
    next.dimensions = [...dims, dim];
    onEdit({ cq: next, label: `chip: ${dim} → kırılım (hepsi ayrı)` });
  };

  const removeFilter = (dim: string) => {
    const next = clone();
    next.filters = filters.filter((f) => f.dimension !== dim);
    if (!(next.filters as Filter[]).length) delete next.filters;
    onEdit({ cq: next, label: `chip: ${dim} filtresi kaldırıldı` });
  };

  // KIRILIM ALTINDA ÇOKLU DEĞER SEÇİMİ: kırılım kalır, kapsam in-filtresiyle daralır
  // ("sadece beyaz ve siyah"). Tümü seçili = filtre yok; tek seçili = eq.
  const setDimSelection = (dim: string, selected: string[], all: string[]) => {
    const next = clone();
    const others = filters.filter((f) => f.dimension !== dim);
    if (selected.length === 0 || selected.length === all.length) {
      next.filters = others; // hepsi = filtresiz
    } else if (selected.length === 1) {
      next.filters = [...others, { dimension: dim, operator: "eq", value: selected[0] }];
    } else {
      next.filters = [...others, { dimension: dim, operator: "in", value: selected }];
    }
    if (!(next.filters as Filter[]).length) delete next.filters;
    onEdit({
      cq: next,
      label: `chip: ${dim} seçimi → ${selected.length && selected.length < all.length ? selected.join(", ") : "hepsi"}`,
    });
  };

  // Kırılımdan tek değere GERİ dönüş: boyutu kaldır, o değere filtrele
  // (ör. cinsiyet kırılımı → yalnız Kadın).
  const dimToFilter = (dim: string, value: string) => {
    const next = clone();
    next.dimensions = dims.filter((x) => x !== dim);
    if (!(next.dimensions as string[]).length) delete next.dimensions;
    next.filters = [
      ...filters.filter((f) => f.dimension !== dim),
      { dimension: dim, operator: "eq", value },
    ];
    onEdit({ cq: next, label: `chip: kırılım → ${dim} = ${value}` });
  };

  // Chip YORUMU gösterir, ham tarihi değil: preset ("Bu yıl"), ay ("Temmuz 2026") ya da
  // okunur aralık ("1 Oca – 31 Mar 2026"). Ham değerler tooltip'te şeffaf kalır.
  const MONTHS_TR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                     "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"];
  const parseIso = (s: string) => {
    const [y, m, d] = s.split("-").map(Number);
    return { y, m, d };
  };
  const fmtShort = (s: string) => {
    const { y, m, d } = parseIso(s);
    return `${d} ${MONTHS_TR[m - 1].slice(0, 3)} ${y}`;
  };
  const periodLabel = (): string => {
    // AYRIK AYLAR ÖNCE OKUNUR. Backend "ocak ve mart" için KAPSAYAN aralık filtresi
    // (1 Oca – 31 Mar) + `ayrik_aylar` işareti üretir; sonucu o iki aya daraltan sarma
    // işaretten gelir. Yalnız filtrelere bakan bir etiket burada "1 Oca – 31 Mar" yazar
    // ve KULLANICIYA YALAN SÖYLER — Şubat cevaba dahil değildir. Etiket, sonucun
    // gerçekten neyi içerdiğini söylemek zorundadır.
    const ayrik = (cq.ayrik_aylar as { aylar?: string[] } | undefined)?.aylar;
    if (ayrik?.length) {
      const yillar = new Set(ayrik.map((a) => parseIso(a).y));
      const adlar = ayrik.map((a) => {
        const { y, m } = parseIso(a);
        return yillar.size === 1 ? MONTHS_TR[m - 1] : `${MONTHS_TR[m - 1]} ${y}`;
      });
      return yillar.size === 1
        ? `${adlar.join(" · ")} ${[...yillar][0]}`
        : adlar.join(" · ");
    }
    // tarih filtreleri her zaman TEK değerdir (liste yalnız kategorik in-filtrede)
    const gte = dateFilters.find((f) => f.operator === "gte")?.value as string | undefined;
    const lte = dateFilters.find((f) => f.operator === "lte")?.value as string | undefined;
    if (!gte && !lte) return "tümü";
    if (gte && !lte) {
      const preset = periodPresets().find((p) => p.start === gte);
      if (preset) return preset.label;
      return `${fmtShort(gte)}'den beri`;
    }
    if (gte && lte) {
      const g = parseIso(gte);
      const l = parseIso(lte);
      const lastDay = new Date(l.y, l.m, 0).getDate();
      if (g.d === 1 && g.m === l.m && g.y === l.y && l.d === lastDay) {
        return `${MONTHS_TR[g.m - 1]} ${g.y}`; // tam ay: "Temmuz 2026"
      }
      return `${fmtShort(gte)} – ${fmtShort(lte)}`;
    }
    return `≤ ${fmtShort(lte!)}`;
  };

  // Dönem hazır seçenekleri — client tarafında deterministik tarih (backend chip'leriyle aynı).
  // DİKKAT: toISOString() UTC'ye çevirir (TR'de 1 Ocak 00:00 → 31 Aralık!) — YEREL formatla.
  const iso = (d: Date) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const periodPresets = (): { label: string; start: string | null; end?: string }[] => {
    const t = new Date();
    const monday = new Date(t);
    monday.setDate(t.getDate() - ((t.getDay() + 6) % 7));
    const monthsAgo = (n: number) => { const d = new Date(t); d.setMonth(t.getMonth() - n); return iso(d); };
    const py = t.getFullYear() - 1;
    return [
      { label: "Bugün", start: iso(t) },
      { label: "Bu hafta", start: iso(monday) },
      { label: "Bu ay", start: iso(new Date(t.getFullYear(), t.getMonth(), 1)) },
      { label: "Son 3 ay", start: monthsAgo(3) },   // göreli kayan pencere
      { label: "Bu yıl", start: iso(new Date(t.getFullYear(), 0, 1)) },
      { label: "Son 12 ay", start: monthsAgo(12) }, // trailing 12 ay (T12M)
      { label: "Geçen yıl", start: iso(new Date(py, 0, 1)), end: iso(new Date(py, 11, 31)) }, // önceki takvim yılı
      { label: "Tümü", start: null },
    ];
  };

  const setPeriod = (label: string, start: string | null, end?: string) => {
    const next = clone();
    const rest = filters.filter((f) => f.dimension !== "tarih");
    const df: Filter[] = [];
    if (start) df.push({ dimension: "tarih", operator: "gte", value: start });
    if (end) df.push({ dimension: "tarih", operator: "lte", value: end });
    next.filters = [...rest, ...df];
    if (!(next.filters as Filter[]).length) delete next.filters;
    // AYRIK AY DARALTMASI DÖNEMLE BİRLİKTE DÜŞER. `ayrik_aylar` backend'de sonucu
    // kullanıcının SAYDIĞI aylara daraltan bir sarma üretir (bkz. wren_service._ayrik_ay_sar).
    // Kullanıcı burada YENİ bir dönem seçtiyse eski daraltma artık onun istediğini
    // anlatmıyor: taşınırsa yeni dönemle SESSİZCE kesişir ve çoğu zaman BOŞ sonuç verir.
    delete next.ayrik_aylar;
    onEdit({ cq: next, label: `chip: dönem → ${label}` });
  };

  return (
    <div ref={barRef} className="mb-4 flex flex-wrap items-center gap-1.5">
      <span className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
        yorum
      </span>

      {measures.map((m) => (
        <span key={m} className={chip} title="Ölçü">
          <span className="text-accent">◆</span> {m}
          {(measures.length > 1 || blend.length > 0) && (
            <button onClick={() => removeMeasure(m)} className={xBtn} aria-label={`${m} ölçüsünü kaldır`}>×</button>
          )}
        </span>
      ))}

      {/* CROSS-CUBE BLEND ölçüleri — cube etiketiyle ("◆ brut_kar ·karlilik"): tek raporda
          birden çok cube. "kâr da ekle" bunları katar; × ile kaldırılır. */}
      {blend.flatMap((b) =>
        b.measures.map((m) => (
          <span key={`${b.cube}:${m}`} className={chip} title={`Ölçü · ${b.cube}`}>
            <span className="text-accent">◆</span> {m}
            <span className="text-[9px] text-neutral-400">·{b.cube}</span>
            <button onClick={() => removeBlendMeasure(b.cube, m)} className={xBtn} aria-label={`${m} ölçüsünü kaldır`}>×</button>
          </span>
        )),
      )}

      {tds.map((t) => {
        const GRAN_TR: Record<string, string> = { day: "gün", week: "hafta", month: "ay", quarter: "çeyrek", year: "yıl" };
        const open = openFilter === "kova";
        return (
          <span key={t.dimension} className={`relative ${chip}`} title="Zaman kovası — tıkla: değiştir">
            <button
              onClick={() => setOpenFilter(open ? null : "kova")}
              className="inline-flex items-center gap-1 hover:text-foreground"
            >
              kova: <span className="text-accent">{GRAN_TR[t.granularity] ?? t.granularity}</span> ▾
            </button>
            <button onClick={removeGran} className={xBtn} aria-label="Zaman kovasını kaldır">×</button>
            {open && (
              <span className="absolute left-0 top-full z-30 mt-1 flex min-w-full flex-col border border-hairline bg-background shadow-lg">
                {(Object.entries(GRAN_TR) as [string, string][]).map(([g, label]) => (
                  <button
                    key={g}
                    onClick={() => { setOpenFilter(null); if (g !== t.granularity) setGran(g); }}
                    className={`px-2 py-1 text-left font-mono text-[11px] hover:bg-neutral-500/[0.06] ${g === t.granularity ? "text-accent" : ""}`}
                  >
                    {label}
                  </button>
                ))}
              </span>
            )}
          </span>
        );
      })}

      {dims.map((d) => {
        const opts = valuesFor(d);
        const open = openFilter === `dim:${d}`;
        if (!opts.length) {
          return (
            <span key={d} className={chip} title="Kırılım">
              kırılım: {d}
              <KokenRozeti dim={d} />
              <button onClick={() => removeDim(d)} className={xBtn} aria-label={`${d} kırılımını kaldır`}>×</button>
            </span>
          );
        }
        // Kategorik kırılım — ÇOKLU SEÇİM: değerleri işaretle/kaldır ("sadece beyaz
        // ve siyah"), kırılım kalır, sorguya in-filtre yansır. Tek değere indirmek
        // için "sadece X" davranışı: son kalan işaretli değer eq olur.
        const dimFilter = catFilters.find((f) => f.dimension === d);
        const selected = dimFilter
          ? (Array.isArray(dimFilter.value) ? dimFilter.value : [dimFilter.value])
          : opts;
        const label =
          dimFilter && selected.length < opts.length
            ? `kırılım: ${d} · ${selected.length}/${opts.length}`
            : `kırılım: ${d}`;
        return (
          <span key={d} className={`relative ${chip}`} title="Kırılım — tıkla: değerleri seç">
            <button
              onClick={() => setOpenFilter(open ? null : `dim:${d}`)}
              className="inline-flex items-center gap-1 hover:text-foreground"
            >
              {label} ▾
            </button>
            <KokenRozeti dim={d} />
            <button onClick={() => removeDim(d)} className={xBtn} aria-label={`${d} kırılımını kaldır`}>×</button>
            {open && (
              <span className="absolute left-0 top-full z-30 mt-1 flex min-w-full flex-col border border-hairline bg-background shadow-lg">
                {opts.map((v) => {
                  const on = selected.includes(v);
                  return (
                    <button
                      key={v}
                      onClick={() => {
                        // TÜMÜ seçiliyken tıklama = "sadece bu" (beklenen davranış);
                        // kısmi seçimde normal aç/kapa. En az bir değer kalmalı.
                        const allOn = selected.length === opts.length;
                        const nextSel = allOn
                          ? [v]
                          : on
                            ? selected.filter((x) => x !== v)
                            : [...selected, v];
                        if (!nextSel.length) return;
                        setDimSelection(d, nextSel, opts);
                      }}
                      className={`px-2 py-1 text-left font-mono text-[11px] hover:bg-neutral-500/[0.06] ${on ? "text-accent" : "text-neutral-400"}`}
                    >
                      {on ? "☑" : "☐"} {v}
                    </button>
                  );
                })}
                <button
                  onClick={() => setDimSelection(d, opts, opts)}
                  className="border-t border-hairline px-2 py-1 text-left font-mono text-[11px] text-neutral-500 hover:bg-neutral-500/[0.06]"
                >
                  hepsi
                </button>
              </span>
            )}
          </span>
        );
      })}

      {catFilters.filter((f) => !dims.includes(f.dimension)).map((f) => {
        const opts = valuesFor(f.dimension);
        const open = openFilter === f.dimension;
        return (
          <span key={f.dimension} className={`relative ${chip}`} title="Filtre — tıkla: değiştir">
            <button
              onClick={() => setOpenFilter(open ? null : f.dimension)}
              className="inline-flex items-center gap-1 hover:text-foreground"
            >
              {f.dimension} {Array.isArray(f.value) ? "∈" : "="}{" "}
              <span className="text-accent">
                {Array.isArray(f.value) ? f.value.join(", ") : f.value}
              </span>{" "}
              ▾
            </button>
            <button onClick={() => removeFilter(f.dimension)} className={xBtn} aria-label="Filtreyi kaldır">×</button>
            {open && (
              <span className="absolute left-0 top-full z-30 mt-1 flex min-w-full flex-col border border-hairline bg-background shadow-lg">
                {opts.map((v) => (
                  <button
                    key={v}
                    onClick={() => { setOpenFilter(null); if (v !== f.value) setFilterValue(f.dimension, v); }}
                    className={`px-2 py-1 text-left font-mono text-[11px] hover:bg-neutral-500/[0.06] ${v === f.value ? "text-accent" : ""}`}
                  >
                    {v}
                  </button>
                ))}
                <button
                  onClick={() => { setOpenFilter(null); filterToDim(f.dimension); }}
                  className="border-t border-hairline px-2 py-1 text-left font-mono text-[11px] text-neutral-500 hover:bg-neutral-500/[0.06]"
                >
                  ◫ hepsi ayrı (kırılım)
                </button>
              </span>
            )}
          </span>
        );
      })}

      {(() => {
        const open = openFilter === "tarih";
        const raw = dateFilters.map((f) => `${f.operator} ${f.value}`).join(" · ");
        return (
          <span className={`relative ${chip}`} title={raw ? `Dönem (${raw}) — tıkla: değiştir` : "Dönem — tıkla: değiştir"}>
            <button
              onClick={() => setOpenFilter(open ? null : "tarih")}
              className="inline-flex items-center gap-1 hover:text-foreground"
            >
              dönem:{" "}
              {dateFilters.length > 0 ? (
                <span className="text-accent">{periodLabel()}</span>
              ) : (
                "tümü"
              )}{" "}
              ▾
            </button>
            {dateFilters.length > 0 && (
              <button onClick={removeDateFilters} className={xBtn} aria-label="Dönem filtresini kaldır">×</button>
            )}
            {open && (
              <span className="absolute left-0 top-full z-30 mt-1 flex min-w-full flex-col border border-hairline bg-background shadow-lg">
                {periodPresets().map((p) => (
                  <button
                    key={p.label}
                    onClick={() => { setOpenFilter(null); setPeriod(p.label, p.start, p.end); }}
                    className="whitespace-nowrap px-2 py-1 text-left font-mono text-[11px] hover:bg-neutral-500/[0.06]"
                  >
                    {p.label}
                  </button>
                ))}
                {/* ÖZEL ARALIK — iki tarih seçici (gte/lte). En az biri dolu → uygula. */}
                <div className="border-t border-hairline px-2 py-1.5">
                  <div className="mb-1 text-[9px] uppercase tracking-wider text-neutral-400">özel aralık</div>
                  <div className="flex items-center gap-1">
                    <input
                      type="date" value={cStart} onChange={(e) => setCStart(e.target.value)}
                      className="border border-hairline bg-background px-1 py-0.5 font-mono text-[10px]"
                    />
                    <span className="text-neutral-400">–</span>
                    <input
                      type="date" value={cEnd} onChange={(e) => setCEnd(e.target.value)}
                      className="border border-hairline bg-background px-1 py-0.5 font-mono text-[10px]"
                    />
                    <button
                      disabled={!cStart && !cEnd}
                      onClick={() => {
                        setOpenFilter(null);
                        const lbl = cStart && cEnd ? `${cStart} – ${cEnd}` : cStart ? `${cStart}'den beri` : `≤ ${cEnd}`;
                        setPeriod(lbl, cStart || null, cEnd || undefined);
                      }}
                      className="ml-auto border border-hairline px-1.5 py-0.5 font-mono text-[10px] text-accent hover:bg-neutral-500/[0.06] disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
                    >
                      uygula
                    </button>
                  </div>
                </div>
              </span>
            )}
          </span>
        );
      })()}

      {/* DÖNEMSEL KIYAS — kova/dönem yanında. Aç: compare ekler (/cube period-shift →
          cari + geçen dönem + %). Aktifken × ile kaldırılır (diğer chip'ler gibi).
          🔴 `DA-9` — **KİPE DUYARLI.** Eskiden `=== "yoy"` sabit kodluydu; `G6`'nın
          `kiyas_cebiri`'si `mom` de üretiyor (*"mart'ı şubat ile kıyasla"* → `mom`).
          Sonuç iki kat kusurluydu: `mom` aktifken chip **"kapalı"** gösteriyordu ve
          tıklayınca kullanıcının kıyasını **sessizce `yoy`'a çeviriyordu** — yani bir
          gösterge, kapatmaya çalıştığı şeyi DEĞİŞTİRİYORDU.
          *Bir anahtarın yalnız bir değeri tanıması, öteki değeri yok saymak değil
          BOZMAKTIR.* */}
      {(() => {
        const mod = cq.compare as string | undefined;
        const active = mod === "yoy" || mod === "mom";
        const etiket = mod === "mom" ? "geçen aya göre" : "geçen yıla göre";
        const setCompare = (on: boolean) => {
          const next = clone() as Record<string, unknown>;
          // ⚠ Açarken varsayılan `yoy` (bugünkü davranış); KAPATIRKEN hangi kip olursa
          // olsun **silinir** — `mom`'u `yoy`'a çevirmek bir kaldırma değil bir düzenlemedir.
          if (on) next.compare = "yoy";
          else delete next.compare;
          onEdit({ cq: next as CubeQuery, label: on ? "chip: geçen yıla göre kıyasla" : "chip: kıyas kaldırıldı" });
        };
        return (
          <button
            onClick={() => setCompare(!active)}
            role="switch"
            aria-checked={active}
            title={active ? `${etiket} kıyaslanıyor — kaldırmak için tıkla`
                          : "Geçen yıla göre kıyasla (YoY) — aç/kapa"}
            className={`${chip} inline-flex items-center gap-1.5 hover:text-foreground ${active ? "border-accent text-accent" : ""}`}
          >
            <span className={active ? "text-accent" : "text-neutral-400"}>◷</span> {etiket}
            {/* on/off göstergesi: yeşil=açık, gri=kapalı */}
            <span className={`inline-block h-2.5 w-2.5 rounded-full ${active ? "bg-accent" : "bg-neutral-400/40"}`} />
            <span className={active ? "text-accent" : "text-neutral-400"}>{active ? "açık" : "kapalı"}</span>
          </button>
        );
      })()}
    </div>
  );
}
