"use client";

import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import type { AskResponse, CubeQuery, QueryResult } from "@dima/contracts";
import { cn } from "@dima/ui/utils";
import {
  contrastRatio,
  gradeContrast,
  resolveCssColor,
  srgbToHex,
  type ContrastGrade,
} from "@/lib/color";
import { BrandMark, PILLARS } from "@dima/ui/brand/BrandMark";
import { ResultView } from "@/components/ResultView";
import { ChatPanel } from "@/components/ChatPanel";
import { InterpretationBar } from "@/components/InterpretationBar";
import { ChainOfThought, Reasoning } from "@/components/ai/thinking";
import { ErdView } from "@/components/schema/ErdView";
import { ThemeToggle } from "@/components/shell/ThemeToggle";
import { LocaleSwitcher } from "@/components/shell/LocaleSwitcher";
import { Button } from "@dima/ui/primitives/button";
import { Badge } from "@dima/ui/primitives/badge";
import { Input } from "@dima/ui/primitives/input";
import { Textarea } from "@dima/ui/primitives/textarea";
import { Label } from "@dima/ui/primitives/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@dima/ui/primitives/card";
import { Separator } from "@dima/ui/primitives/separator";
import { Skeleton } from "@dima/ui/primitives/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@dima/ui/primitives/tabs";
import { ToggleGroup, ToggleGroupItem } from "@dima/ui/primitives/toggle-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@dima/ui/primitives/select";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@dima/ui/primitives/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@dima/ui/primitives/dropdown-menu";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@dima/ui/primitives/popover";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@dima/ui/primitives/dialog";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@dima/ui/primitives/sheet";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@dima/ui/primitives/tooltip";
import { ArrowUpRight, Layers3, ShieldCheck } from "lucide-react";

/**
 * YAŞAYAN STİL KILAVUZU — tasarım sisteminin birincil QA yüzeyi.
 *
 * KAYDIRMA: `(product)/app/layout.tsx` çocuklarını `h-dvh overflow-hidden`
 * içine alır (kabuk kendi kaydırmasını yönetsin diye). Bu sayfa ise düz uzun
 * bir doküman, dolayısıyla KENDİ kaydırma kabını açmak ZORUNDA — aksi halde
 * ilk ekrandan sonrası sessizce kırpılır. `#doc` o kap; yapışkan başlık ve sol
 * içindekiler ona göre konumlanır.
 */

// ── Örnek veri (hepsi uydurma; hiçbir çağrı ağa çıkmaz) ─────────────────────

const ERD_MODELS = [
  {
    name: "partiler",
    columns: [
      { name: "parti_no", type: "text", values: null },
      { name: "makine", type: "text", values: null },
      { name: "renk", type: "text", values: null },
      { name: "fire_kg", type: "number", values: null },
      { name: "ciro", type: "number", values: null },
      { name: "siparis_no", type: "text", values: null },
    ],
  },
  {
    name: "makineler",
    columns: [
      { name: "makine", type: "text", values: null },
      { name: "tip", type: "text", values: null },
    ],
  },
  {
    name: "musteriler",
    columns: [
      { name: "musteri", type: "text", values: null },
      { name: "sehir", type: "text", values: null },
    ],
  },
  {
    name: "siparisler",
    columns: [
      { name: "siparis_no", type: "text", values: null },
      { name: "musteri", type: "text", values: null },
      { name: "miktar", type: "number", values: null },
    ],
  },
];
const ERD_RELS = [
  {
    name: "r1",
    models: ["partiler", "makineler"],
    join_type: "many_to_one",
    condition: "partiler.makine = makineler.makine",
  },
  {
    name: "r2",
    models: ["partiler", "siparisler"],
    join_type: "many_to_one",
    condition: "partiler.siparis_no = siparisler.siparis_no",
  },
  {
    name: "r3",
    models: ["siparisler", "musteriler"],
    join_type: "many_to_one",
    condition: "siparisler.musteri = musteriler.musteri",
  },
];

const qr = (columns: string[], rows: (string | number)[][]): QueryResult => ({
  columns,
  rows: rows.map((r) => Object.fromEntries(columns.map((c, i) => [c, r[i]]))),
  row_count: rows.length,
});

const SAMPLE_BAR = qr(
  ["makine", "oee"],
  [
    ["M-01", 0.82],
    ["M-02", 0.76],
    ["M-03", 0.91],
    ["M-04", 0.68],
    ["M-05", 0.84],
  ],
);
const SAMPLE_LINE = qr(
  ["tarih__month", "ciro"],
  [
    ["2026-02-01", 1840000],
    ["2026-03-01", 2010000],
    ["2026-04-01", 1930000],
    ["2026-05-01", 2260000],
    ["2026-06-01", 2110000],
    ["2026-07-01", 2480000],
  ],
);
const SAMPLE_GROUPED = qr(
  ["hafta_gunu", "cinsiyet", "fire_kg"],
  [
    ["Pzt", "Kadın", 120],
    ["Pzt", "Erkek", 98],
    ["Sal", "Kadın", 140],
    ["Sal", "Erkek", 110],
    ["Çar", "Kadın", 90],
    ["Çar", "Erkek", 130],
    ["Per", "Kadın", 160],
    ["Per", "Erkek", 105],
    ["Cum", "Kadın", 100],
    ["Cum", "Erkek", 120],
  ],
);
const SAMPLE_KPI = qr(["ciro", "fire_kg", "oee"], [[2480000, 1240, 0.83]]);
// Çapraz karşılaştırma: fire_kg ve agirlik_kg AYNI birimde (sol eksen, sütun),
// fire_orani farklı birimde (sağ eksen, çizgi). Tek eksende oran düz çizgi olurdu.
const SAMPLE_COMBO = qr(
  ["tarih__month", "fire_kg", "agirlik_kg", "fire_orani"],
  [
    ["2026-02-01", 820, 51000, 1.6],
    ["2026-03-01", 910, 48000, 1.9],
    ["2026-04-01", 1180, 52500, 2.2],
    ["2026-05-01", 1040, 55200, 1.9],
    ["2026-06-01", 1310, 53100, 2.5],
    ["2026-07-01", 980, 56400, 1.7],
  ],
);
// 3 kırılım (zaman × kumaş × vardiya) → panelli görünüm, ortak y-skala.
const SAMPLE_FACET = qr(
  ["tarih__month", "kumas_cinsi", "vardiya", "uretim_kg"],
  [
    ["2026-05-01", "Pamuk", "A", 4100],
    ["2026-05-01", "Pamuk", "B", 3800],
    ["2026-06-01", "Pamuk", "A", 4600],
    ["2026-06-01", "Pamuk", "B", 3200],
    ["2026-07-01", "Pamuk", "A", 4900],
    ["2026-07-01", "Pamuk", "B", 4400],
    ["2026-05-01", "Polyester", "A", 6200],
    ["2026-05-01", "Polyester", "B", 5900],
    ["2026-06-01", "Polyester", "A", 6800],
    ["2026-06-01", "Polyester", "B", 6100],
    ["2026-07-01", "Polyester", "A", 7300],
    ["2026-07-01", "Polyester", "B", 6600],
    ["2026-05-01", "Viskon", "A", 2400],
    ["2026-05-01", "Viskon", "B", 2900],
    ["2026-06-01", "Viskon", "A", 3100],
    ["2026-06-01", "Viskon", "B", 2600],
    ["2026-07-01", "Viskon", "A", 2800],
    ["2026-07-01", "Viskon", "B", 3300],
  ],
);
// Vardiya × haftanın günü matrisi — kenar ortalamalarıyla (marj) birlikte.
const SAMPLE_HEATMAP = qr(
  ["vardiya", "hafta_gunu", "oee"],
  [
    ["A", "Pzt", 0.78],
    ["A", "Sal", 0.84],
    ["A", "Çar", 0.91],
    ["A", "Per", 0.86],
    ["A", "Cum", 0.74],
    ["B", "Pzt", 0.65],
    ["B", "Sal", 0.71],
    ["B", "Çar", 0.83],
    ["B", "Per", 0.79],
    ["B", "Cum", 0.68],
    ["C", "Pzt", 0.58],
    ["C", "Sal", 0.62],
    ["C", "Çar", 0.75],
    ["C", "Per", 0.7],
    ["C", "Cum", 0.61],
  ],
);

const CHAT_ITEMS: AskResponse[] = [
  {
    question: "Örnek: fiyat listesi 2027",
    sql: "",
    planned_sql: null,
    result: null,
    source: null,
    cube_query: null,
    note: "Bu alanı modelde bulamadım. Şunları deneyebilirsin:",
    trace: [],
    suggestions: [
      { label: "Bu ay toplam üretim", query: "bu ay toplam üretim" },
      { label: "Makine bazında OEE", query: "makine bazında OEE" },
    ],
    view_hint: null,
    contract_id: null,
  },
  {
    question: "Makine bazında OEE",
    sql: "SELECT makine, AVG(oee) FROM vardiya GROUP BY makine",
    planned_sql: null,
    result: SAMPLE_BAR,
    source: "cube",
    cube_query: {
      cube: "vardiya",
      measures: ["oee"],
      dimensions: ["makine"],
    } as unknown as CubeQuery,
    note: null,
    trace: [],
    suggestions: [],
    view_hint: null,
    contract_id: "qc_a1b2c3",
  },
];

// ── Jeton (token) tablosu ───────────────────────────────────────────────────
// `on` = o zeminin ÜSTÜNDE duran metnin jetonu. Eşleşmeyi göstermek kontrastı
// göz kararı bırakmamak demek: swatch'ın içindeki "Aa" gerçek eşleşmedir.

interface TokenSpec {
  name: string;
  bg: string;
  /** Bu zeminin ÜSTÜNDE duran metnin sınıfı + jetonu (kontrast bu ikiliden). */
  on?: string;
  onToken?: string;
  ring?: boolean;
}

const TOKENS: TokenSpec[] = [
  {
    name: "background",
    bg: "bg-background",
    on: "text-foreground",
    onToken: "foreground",
    ring: true,
  },
  {
    name: "card",
    bg: "bg-card",
    on: "text-card-foreground",
    onToken: "card-foreground",
    ring: true,
  },
  {
    name: "muted",
    bg: "bg-muted",
    on: "text-muted-foreground",
    onToken: "muted-foreground",
    ring: true,
  },
  {
    name: "accent",
    bg: "bg-accent",
    on: "text-accent-foreground",
    onToken: "accent-foreground",
    ring: true,
  },
  {
    name: "secondary",
    bg: "bg-secondary",
    on: "text-secondary-foreground",
    onToken: "secondary-foreground",
    ring: true,
  },
  {
    name: "primary",
    bg: "bg-primary",
    on: "text-primary-foreground",
    onToken: "primary-foreground",
  },
  {
    name: "brand",
    bg: "bg-brand",
    on: "text-brand-foreground",
    onToken: "brand-foreground",
  },
  {
    name: "destructive",
    bg: "bg-destructive",
    on: "text-destructive-foreground",
    onToken: "destructive-foreground",
  },
  {
    name: "foreground",
    bg: "bg-foreground",
    on: "text-background",
    onToken: "background",
  },
  { name: "border", bg: "bg-border", ring: true },
];

/**
 * Çalışma anında okunacak jeton adları — GÖSTERİLEN her jeton burada olmalı.
 * Listeden düşen bir jeton hata vermez, sessizce "—" gösterir; o yüzden liste
 * gösterim tablolarından TÜRETİLİR, elle yazılmaz.
 */
// Sınıf adları TAM yazılır: Tailwind kaynağı statik tarar, `bg-${x}` derlenmez.
const CHART_TOKENS: { name: string; bg: string }[] = [
  { name: "chart-1", bg: "bg-chart-1" },
  { name: "chart-2", bg: "bg-chart-2" },
  { name: "chart-3", bg: "bg-chart-3" },
  { name: "chart-4", bg: "bg-chart-4" },
  { name: "chart-5", bg: "bg-chart-5" },
];

const READ_TOKENS = [
  ...TOKENS.map((t) => t.name),
  ...TOKENS.flatMap((t) => (t.onToken ? [t.onToken] : [])),
  ...CHART_TOKENS.map((c) => c.name),
];

const RADII: { name: string; className: string; note: string }[] = [
  { name: "sm", className: "rounded-sm", note: "rozet, chip" },
  { name: "md", className: "rounded-md", note: "düğme, girdi" },
  { name: "lg", className: "rounded-lg", note: "kart, panel" },
  { name: "xl", className: "rounded-xl", note: "diyalog, sayfa bloğu" },
];

// ── Gezinme ─────────────────────────────────────────────────────────────────
// Tek kaynak: hem sol içindekiler hem de içerikteki grup başlıkları buradan.

const NAV: { group: string; items: { id: string; label: string }[] }[] = [
  {
    group: "Temel",
    items: [
      { id: "renk", label: "Renk" },
      { id: "tipografi", label: "Tipografi" },
      { id: "form-dili", label: "Köşe & kenar" },
    ],
  },
  {
    group: "Bileşenler",
    items: [
      { id: "dugmeler", label: "Düğmeler" },
      { id: "rozetler", label: "Rozetler" },
      { id: "form", label: "Form" },
      { id: "kartlar", label: "Kartlar" },
      { id: "katmanlar", label: "Katmanlar" },
      { id: "sekme-tablo", label: "Sekme & tablo" },
    ],
  },
  {
    group: "Veri",
    items: [
      { id: "grafikler", label: "Grafikler" },
      { id: "yorum-cubugu", label: "Yorum çubuğu" },
      { id: "erd", label: "ERD" },
    ],
  },
  {
    group: "Desenler",
    items: [
      { id: "sohbet", label: "Sohbet" },
      { id: "dusunme", label: "Düşünme" },
    ],
  },
];

const ALL_IDS = NAV.flatMap((g) => g.items.map((i) => i.id));

/** Editoryal numaralandırma — sıra NAV'dan gelir, elle sayılmaz. */
const SECTION_NO: Record<string, string> = Object.fromEntries(
  ALL_IDS.map((id, i) => [id, String(i + 1).padStart(2, "0")]),
);

/** Görünür bölümü izler — sol içindekiler nerede olduğunu göstersin diye. */
function useActiveSection(ids: string[]): string {
  const [active, setActive] = useState(ids[0] ?? "");

  useEffect(() => {
    const nodes = ids
      .map((id) => document.getElementById(id))
      .filter((n): n is HTMLElement => n !== null);

    if (process.env.NODE_ENV !== "production" && nodes.length !== ids.length) {
      // İçindekiler ile bölümler ayrı yazılıyor; kayma sessiz olmasın.
      console.warn("[style] içindekiler ↔ bölüm eşleşmiyor", {
        beklenen: ids.length,
        bulunan: nodes.length,
      });
    }

    // Görünür bölümlerin KÜMESİ tutulur, tek tek olaylar değil: bir bölüm banttan
    // çıkarken gelen olay yalnız "artık görünmüyorum" der, o anki geçerli bölümü
    // söylemez. Sadece olaylara bakınca işaret önceki bölümde takılı kalıyordu.
    const visible = new Set<string>();

    const observer = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) visible.add(e.target.id);
          else visible.delete(e.target.id);
        }
        // Bant birden çok bölüme değebilir → belge sırasında en üstteki kazanır.
        const top = ids.find((id) => visible.has(id));
        if (top) setActive(top);
      },
      // Üst bandı başlık yüksekliği kadar kırp: "aktif" olan, başlığın hemen
      // altındaki bölüm olsun.
      { rootMargin: "-72px 0px -65% 0px", threshold: 0 },
    );

    nodes.forEach((n) => observer.observe(n));
    return () => observer.disconnect();
  }, [ids]);

  return active;
}

/**
 * Jetonların ÇALIŞMA ANINDAKİ değerlerini okur (`--brand` → "oklch(...)").
 *
 * Kaynak globals.css; burada kopyası tutulmaz — kopya tutmak, paletin sayfada
 * gösterilen halinin gerçekten uygulanan halden sessizce ayrılması demekti.
 * Tema sınıfı değişince yeniden okunur, dolayısıyla koyu tema kendi sayılarını
 * gösterir. SSR'de boş: sunucuda hesaplanmış stil yok.
 */
function useTokenValues(names: string[]): Record<string, string> {
  const [values, setValues] = useState<Record<string, string>>({});

  useEffect(() => {
    const read = () => {
      const cs = getComputedStyle(document.documentElement);
      setValues(
        Object.fromEntries(
          names.map((n) => [n, cs.getPropertyValue(`--${n}`).trim()]),
        ),
      );
    };
    read();
    // next-themes kökteki `class`ı değiştirir → jetonlar yeniden okunmalı.
    const mo = new MutationObserver(read);
    mo.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class", "style"],
    });
    return () => mo.disconnect();
  }, [names]);

  return values;
}

const GRADE_STYLE: Record<ContrastGrade, string> = {
  AAA: "border-transparent bg-muted text-foreground",
  AA: "border-transparent bg-muted text-foreground",
  "AA-large": "border-border text-muted-foreground",
  fail: "border-destructive/40 bg-destructive/10 text-destructive",
};

const GRADE_LABEL: Record<ContrastGrade, string> = {
  AAA: "AAA",
  AA: "AA",
  "AA-large": "AA iri",
  fail: "kalır",
};

/** Tek jeton kartı: örnek + gerçek değer + ölçülmüş kontrast. */
function TokenCard({
  spec,
  values,
}: {
  spec: TokenSpec;
  values: Record<string, string>;
}) {
  const parsed = resolveCssColor(values[spec.name] ?? "");
  const onParsed = spec.onToken
    ? resolveCssColor(values[spec.onToken] ?? "")
    : null;
  const ratio = parsed && onParsed ? contrastRatio(parsed, onParsed) : null;

  const copy = useCallback(() => {
    void navigator.clipboard
      ?.writeText(`var(--${spec.name})`)
      .then(() => toast(`var(--${spec.name}) kopyalandı`));
  }, [spec.name]);

  return (
    // DİKKAT — kart bir <button> DEĞİL, bilerek. Safari düğme içeriğini kendi
    // anonim kutusuna sarar; içindeki sabit yükseklikli kutu (h-20) oraya
    // uymayıp içerik boyuna çöküyordu. Tıklanabilir olan sadece jeton adı —
    // erişilebilir ad da böylece kartın tüm metni değil, jetonun kendisi olur.
    <div className="space-y-2">
      <div
        className={cn(
          "flex h-20 min-h-20 items-end rounded-lg p-2.5",
          spec.bg,
          spec.ring && "ring-1 ring-border ring-inset",
        )}
      >
        {spec.on && (
          <span className={cn("font-mono text-[11px]", spec.on)}>Aa</span>
        )}
      </div>
      <div className="space-y-1">
        <div className="flex items-baseline justify-between gap-2">
          <button
            type="button"
            onClick={copy}
            title={`var(--${spec.name}) kopyala`}
            className="font-mono text-[11px] transition-colors hover:text-brand"
          >
            {spec.name}
          </button>
          <span className="font-mono text-[10px] text-muted-foreground tabular-nums">
            {parsed ? srgbToHex(parsed) : "—"}
          </span>
        </div>
        {ratio !== null && (
          <div className="flex items-center gap-1.5">
            <span className="font-mono text-[10px] text-muted-foreground tabular-nums">
              {ratio.toFixed(2)}:1
            </span>
            <span
              className={cn(
                "rounded-sm border px-1 font-mono text-[9px] tracking-wide uppercase",
                GRADE_STYLE[gradeContrast(ratio)],
              )}
            >
              {GRADE_LABEL[gradeContrast(ratio)]}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Düzen parçaları ─────────────────────────────────────────────────────────

function GroupRule({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-4 pt-6">
      <span className="font-mono text-[10px] tracking-[0.22em] text-muted-foreground uppercase">
        {label}
      </span>
      <span className="h-px flex-1 bg-border" />
    </div>
  );
}

function Section({
  id,
  title,
  description,
  children,
}: {
  id: string;
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-28 space-y-6">
      <div className="max-w-2xl space-y-2">
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-micro text-brand tabular-nums">
            {SECTION_NO[id]}
          </span>
          <h2 className="text-2xl font-semibold tracking-tight text-balance">{title}</h2>
        </div>
        {description && (
          <p className="pl-[calc(1.5rem+1ch)] text-sm leading-relaxed text-muted-foreground">
            {description}
          </p>
        )}
      </div>
      <div className="space-y-4">{children}</div>
    </section>
  );
}

/** Örneklerin ortak çerçevesi: ince kenar + isteğe bağlı üst etiket. */
function Specimen({
  label,
  className,
  children,
}: {
  label?: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="overflow-hidden rounded-xl border border-border bg-card shadow-xs">
      {label && (
        <div className="flex items-center gap-2 border-b border-border bg-muted/35 px-4 py-2">
          <span className="size-1.5 rounded-full bg-brand" aria-hidden="true" />
          <span className="font-mono text-micro tracking-[0.16em] text-muted-foreground uppercase">
          {label}
          </span>
        </div>
      )}
      <div className={cn("p-4 sm:p-5", className)}>{children}</div>
    </div>
  );
}

export default function StyleGuide() {
  const active = useActiveSection(ALL_IDS);
  const tokenValues = useTokenValues(READ_TOKENS);

  return (
    // Kendi kaydırma kabı — layout `overflow-hidden` olduğu için ŞART.
    <div id="doc" className="h-dvh overflow-y-auto bg-background motion-safe:scroll-smooth">
      {/* Yapışkan üst bar */}
      {/* Zemin SAYDAM DEĞİL: iç içe kaydırma kabında Safari'nin backdrop-filter'ı
          güvenilmez, ve altından geçen içerik başlığın üstüne biniyor gibi
          görünüyordu. Doküman başlığı için düz zemin zaten daha okunur. */}
      <header className="sticky top-0 z-30 border-b border-border/80 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/85">
        <div className="mx-auto flex h-14 max-w-7xl items-center gap-3 px-4 sm:px-6">
          <BrandMark size="sm" />
          <span className="text-sm text-muted-foreground">/</span>
          <span className="text-sm text-muted-foreground">sistem rehberi</span>
          <span className="hidden rounded-sm border border-border px-1.5 py-0.5 font-mono text-micro text-muted-foreground sm:inline">
            v1.0
          </span>
          <div className="ml-auto flex items-center gap-1">
            <LocaleSwitcher />
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Dar ekranda içindekiler — sol ray lg altında gizleniyor ve 14 bölümlük
          bir doküman gezinmesiz kalıyordu. Izgaranın DIŞINDA duruyor: tek
          sütunlu ızgarada öğenin alanı kendi boyu kadar olur ve sticky hiç
          tutmaz; burada kapsayıcı blok #doc olduğu için başlığın altına yapışır. */}
      <nav
        aria-label="Bölümler"
        className="sticky top-14 z-20 border-b border-border bg-background/95 backdrop-blur lg:hidden"
      >
        <ul className="mx-auto flex max-w-7xl gap-1 overflow-x-auto px-4 py-2 sm:px-6 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {NAV.flatMap((g) => g.items).map((item) => (
            <li key={item.id}>
              <a
                href={`#${item.id}`}
                aria-current={active === item.id ? "true" : undefined}
                className={cn(
                  "block rounded-md px-2.5 py-1 text-[13px] whitespace-nowrap transition-colors",
                  active === item.id
                    ? "bg-muted font-medium text-foreground"
                    : "text-muted-foreground",
                )}
              >
                {item.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-x-14 px-4 sm:px-6 lg:grid-cols-[190px_minmax(0,1fr)]">
        {/* Sol içindekiler — yalnız geniş ekranda; okuma sütununu daraltmaz */}
        {/* Yapışkanlık ızgara ÖĞESİNİN KENDİSİNDE değil, içindeki nav'da: Safari
            grid item üzerindeki position:sticky'yi güvenilir uygulamıyor —
            içindekiler başlığın altına yapışmayıp sayfayla birlikte kayıyordu. */}
        <div className="hidden lg:block">
          <nav
            aria-label="Bölümler"
            className="sticky top-14 max-h-[calc(100dvh-3.5rem)] overflow-y-auto py-10"
          >
            <ul className="space-y-6">
              {NAV.map((g) => (
                <li key={g.group}>
                  <div className="mb-2 font-mono text-[10px] tracking-[0.18em] text-muted-foreground uppercase">
                    {g.group}
                  </div>
                  <ul className="space-y-0.5 border-l border-border">
                    {g.items.map((item) => {
                      const on = active === item.id;
                      return (
                        <li key={item.id}>
                          <a
                            href={`#${item.id}`}
                            aria-current={on ? "true" : undefined}
                            className={cn(
                              "-ml-px block border-l py-1 pl-3 text-[13px] transition-colors",
                              on
                                ? "border-brand font-medium text-foreground"
                                : "border-transparent text-muted-foreground hover:border-border hover:text-foreground",
                            )}
                          >
                            {item.label}
                          </a>
                        </li>
                      );
                    })}
                  </ul>
                </li>
              ))}
            </ul>
          </nav>
        </div>

        <main className="min-w-0 space-y-16 py-8 pb-16 sm:py-12">
          {/* Manşet */}
          <div className="overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
            <div className="grid gap-8 p-6 sm:p-8 lg:grid-cols-[minmax(0,1fr)_17rem] lg:items-end lg:p-10">
              <div className="space-y-6">
                <div className="flex items-center gap-2 font-mono text-micro tracking-[0.16em] text-muted-foreground uppercase">
                  <span className="size-1.5 rounded-full bg-brand" aria-hidden="true" />
                  dima sistem rehberi
                </div>
                <div className="space-y-3">
                  <BrandMark size="xl" animate />
                  <h1 className="max-w-2xl text-4xl font-semibold tracking-tight text-balance sm:text-5xl">
                    Güven veren analitik için sakin bir arayüz dili.
                  </h1>
                  <p className="max-w-xl text-[15px] leading-relaxed text-muted-foreground">
                    Bu sayfa, dima&apos;nın bileşenlerini yalnız sergilemez; kararların
                    nasıl görünmesi gerektiğini açıklar. Her örnek gerçek ürün
                    primitifleriyle çalışır ve iki temada da denetlenir.
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm">
                  <span className="inline-flex items-center gap-1.5 text-muted-foreground">
                    <ShieldCheck className="size-4 text-brand" />
                    gerçek jetonlar
                  </span>
                  <span className="inline-flex items-center gap-1.5 text-muted-foreground">
                    <Layers3 className="size-4 text-brand" />
                    yaşayan bileşenler
                  </span>
                  <a href="#renk" className="inline-flex items-center gap-1 text-foreground underline-offset-4 hover:text-brand hover:underline">
                    Temelleri incele <ArrowUpRight className="size-3.5" />
                  </a>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-border bg-border">
                {PILLARS.map((pillar, index) => (
                  <div key={pillar.letter} className="min-h-30 bg-card p-4 sm:p-5">
                    <div className="flex items-start justify-between">
                      <span className="font-sans text-3xl leading-none tracking-tight text-brand">
                        {pillar.letter === "i" ? (
                          <span className="relative inline-block">
                            ı
                            <span className="absolute left-1/2 top-[0.14em] size-[0.13em] -translate-x-1/2 rounded-full bg-brand" />
                          </span>
                        ) : (
                          pillar.letter
                        )}
                      </span>
                      <span className="font-mono text-micro text-muted-foreground tabular-nums">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                    </div>
                    <p lang="en" className="mt-5 font-mono text-micro tracking-[0.08em] text-foreground uppercase">
                      {pillar.word}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid border-t border-border sm:grid-cols-3">
              {[
                ["Arayüz", "Plus Jakarta Sans"],
                ["Veri dili", "JetBrains Mono · Recharts"],
                ["Güvence", "Açık ve koyu tema"],
              ].map(([label, value]) => (
                <div key={label} className="border-border px-6 py-4 sm:border-r sm:last:border-r-0">
                  <p className="font-mono text-micro tracking-[0.14em] text-muted-foreground uppercase">{label}</p>
                  <p className="mt-1 text-sm font-medium text-foreground">{value}</p>
                </div>
              ))}
            </div>
          </div>

          <GroupRule label="Temel" />

          <Section
            id="renk"
            title="Renk"
            description="Tek kaynak: CSS jetonları — ham renk sınıfı (neutral-500 gibi) kullanılmaz. Değerler ve kontrast oranları bu sayfada ÇALIŞMA ANINDA okunup hesaplanıyor; yani aşağıdaki sayılar paletin kopyası değil, kendisi. Temayı değiştir, hepsi yeniden ölçülür. Jeton adına tıklayınca var(--…) kopyalanır."
          >
            <div className="grid grid-cols-2 gap-x-3 gap-y-5 sm:grid-cols-3 lg:grid-cols-5">
              {TOKENS.map((t) => (
                <TokenCard key={t.name} spec={t} values={tokenValues} />
              ))}
            </div>

            <div className="space-y-2 pt-4">
              <p className="font-mono text-[10px] tracking-wider text-muted-foreground uppercase">
                grafik dizisi — sırayla atanır, döngüye girmez
              </p>
              <div className="flex gap-1.5">
                {CHART_TOKENS.map((c, i) => {
                  const parsed = resolveCssColor(tokenValues[c.name] ?? "");
                  return (
                    <div key={c.name} className="flex-1 space-y-1.5">
                      <div className={cn("h-12 rounded-md", c.bg)} />
                      <div className="font-mono text-[10px] text-muted-foreground tabular-nums">
                        {i + 1} · {parsed ? srgbToHex(parsed) : "—"}
                      </div>
                    </div>
                  );
                })}
              </div>
              <p className="max-w-2xl text-xs leading-relaxed text-muted-foreground">
                Sıra bir güvenlik mekanizmasıdır: mavi → turuncu → aqua → sarı →
                magenta, renk körlüğünde ayrışacak şekilde seçildi. Marka moru
                kasıtla bu rampanın dışında — arayüz vurgusu bir seri kimliğini
                taklit etmemeli.
              </p>
            </div>
          </Section>

          <Section
            id="tipografi"
            title="Tipografi"
            description="İki yazı tipi taşıyor: Jakarta arayüzü, JetBrains Mono sayıyı ve SQL'i. Playfair yalnız marketing sayfalarına ayrıldı — uygulamada kullanılmaz."
          >
            <Specimen>
              <div className="space-y-4">
                <p className="text-4xl font-semibold tracking-tight">
                  Veriyle konuş.
                </p>
                <p className="text-lg">
                  Plus Jakarta Sans — arayüzün sesi. Doğal dille sor, güvenilir
                  SQL ve rapor al.
                </p>
                <p className="text-sm text-muted-foreground">
                  İkincil gövde — açıklama, üstveri, alt not.
                </p>
                <p className="font-mono text-sm tabular-nums">
                  JetBrains Mono — SELECT SUM(ciro) FROM partiler WHERE ay =
                  &apos;2026-07&apos;
                </p>
                <Separator />
                <p className="font-display text-3xl">
                  Playfair Display — yalnız marketing
                </p>
              </div>
            </Specimen>
          </Section>

          <Section
            id="form-dili"
            title="Köşe & kenar"
            description="Gölge yerine saç teli kenar. Yükseklik hissini kenarın kendisi taşır; yalnız üste binen katmanlar (diyalog, popover) gölge alır."
          >
            <div className="grid gap-4 sm:grid-cols-2">
              <Specimen label="yarıçap ölçeği">
                <div className="flex items-end gap-4">
                  {RADII.map((r) => (
                    <div key={r.name} className="space-y-2 text-center">
                      <div
                        className={cn(
                          "size-14 border border-border bg-muted",
                          r.className,
                        )}
                      />
                      <div className="font-mono text-[10px] text-muted-foreground">
                        {r.name}
                      </div>
                      <div className="text-[10px] text-muted-foreground">
                        {r.note}
                      </div>
                    </div>
                  ))}
                </div>
              </Specimen>
              <Specimen label="yüzey">
                <div className="space-y-3">
                  <div className="rounded-lg border border-border p-3 text-sm">
                    Kenar — kart, panel, satır
                  </div>
                  <div className="rounded-lg bg-muted p-3 text-sm">
                    Sessiz zemin — gruplama
                  </div>
                  <div className="rounded-lg border border-border bg-popover p-3 text-sm shadow-md">
                    Yüzen katman — yalnız burada gölge
                  </div>
                </div>
              </Specimen>
            </div>
          </Section>

          <GroupRule label="Bileşenler" />

          <Section
            id="dugmeler"
            title="Düğmeler"
            description="Basınca %97'ye iner — arayüzün duyduğunu anında bildiren geri bildirim."
          >
            <Specimen label="varyant">
              <div className="flex flex-wrap items-center gap-3">
                <Button>Birincil</Button>
                <Button variant="brand">Marka</Button>
                <Button variant="secondary">İkincil</Button>
                <Button variant="outline">Çerçeveli</Button>
                <Button variant="ghost">Sessiz</Button>
                <Button variant="destructive">Sil</Button>
                <Button variant="link">Metin bağlantısı</Button>
              </div>
            </Specimen>
            <Specimen label="boyut & durum">
              <div className="flex flex-wrap items-center gap-3">
                <Button size="sm">Küçük</Button>
                <Button size="default">Varsayılan</Button>
                <Button size="lg">Büyük</Button>
                <Button disabled>Devre dışı</Button>
                <Button
                  onClick={() =>
                    toast("Rapor hazır", { description: "3 satır döndü." })
                  }
                >
                  Toast
                </Button>
              </div>
            </Specimen>
          </Section>

          <Section
            id="rozetler"
            title="Rozetler & köken"
            description="SQL'i kimin ürettiği renkle değil ETİKETLE söylenir; renk yalnız pekiştirir. CUBE deterministik yoldur — marka rengini yalnız o hak eder."
          >
            <Specimen>
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="brand">◆ CUBE</Badge>
                <Badge variant="brand-subtle">◆ CUBE·LLM</Badge>
                <Badge variant="secondary">▚ LLM·anthropic</Badge>
                <Badge variant="outline">⚙ KURAL</Badge>
                <Badge>default</Badge>
                <Badge variant="destructive">alert</Badge>
              </div>
            </Specimen>
          </Section>

          <Section id="form" title="Form">
            <Specimen>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="q">Soru</Label>
                  <Input id="q" placeholder="Verine bir soru sor…" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cube">Küp</Label>
                  <Select>
                    <SelectTrigger id="cube">
                      <SelectValue placeholder="Bir küp seç" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="partiler">partiler</SelectItem>
                      <SelectItem value="siparisler">siparişler</SelectItem>
                      <SelectItem value="vardiya">vardiya_kayitlari</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2 sm:col-span-2">
                  <Label htmlFor="note">Not</Label>
                  <Textarea id="note" placeholder="Açıklama…" />
                </div>
                <div className="sm:col-span-2">
                  <ToggleGroup
                    type="single"
                    defaultValue="chart"
                    variant="outline"
                  >
                    <ToggleGroupItem value="chart">Grafik</ToggleGroupItem>
                    <ToggleGroupItem value="table">Tablo</ToggleGroupItem>
                  </ToggleGroup>
                </div>
              </div>
            </Specimen>
          </Section>

          <Section id="kartlar" title="Kartlar">
            <div className="grid gap-4 sm:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Toplam ciro</CardTitle>
                  <CardDescription>Bu ay · CUBE</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="font-mono text-3xl tabular-nums">₺2.48M</p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Geçen aya göre +12%
                  </p>
                </CardContent>
                <CardFooter>
                  <Badge variant="brand-subtle">◆ CUBE</Badge>
                </CardFooter>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Yükleniyor</CardTitle>
                  <CardDescription>İskelet durumu</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                  <Skeleton className="h-24 w-full" />
                </CardContent>
              </Card>
            </div>
          </Section>

          <Section
            id="katmanlar"
            title="Katmanlar"
            description="Popover ve menü tetikleyicisinden büyür (transform-origin tetikleyicide); diyalog merkezde kalır — bir düğmeye bağlı değildir."
          >
            <Specimen>
              <div className="flex flex-wrap items-center gap-3">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="outline">Tooltip</Button>
                  </TooltipTrigger>
                  <TooltipContent>Nasıl çözüldü?</TooltipContent>
                </Tooltip>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline">Dropdown</Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuLabel>Zamanla</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem>Her sabah 08:00</DropdownMenuItem>
                    <DropdownMenuItem>Her saat</DropdownMenuItem>
                    <DropdownMenuItem>Her pazartesi</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>

                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline">Popover</Button>
                  </PopoverTrigger>
                  <PopoverContent>
                    <p className="text-sm">Bildirim yok.</p>
                  </PopoverContent>
                </Popover>

                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="outline">Dialog</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Ayarlar</DialogTitle>
                      <DialogDescription>
                        Örnek bir diyalog penceresi.
                      </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                      <Button variant="ghost">İptal</Button>
                      <Button>Kaydet</Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>

                <Sheet>
                  <SheetTrigger asChild>
                    <Button variant="outline">Sheet</Button>
                  </SheetTrigger>
                  <SheetContent>
                    <SheetHeader>
                      <SheetTitle>Veri modeli</SheetTitle>
                      <SheetDescription>
                        Şema tarayıcısı burada açılır.
                      </SheetDescription>
                    </SheetHeader>
                  </SheetContent>
                </Sheet>
              </div>
            </Specimen>
          </Section>

          <Section id="sekme-tablo" title="Sekme & tablo">
            <Tabs defaultValue="table">
              <TabsList>
                <TabsTrigger value="table">Tablo</TabsTrigger>
                <TabsTrigger value="about">Hakkında</TabsTrigger>
              </TabsList>
              <TabsContent value="table">
                <div className="overflow-x-auto rounded-lg border border-border">
                  <Table>
                    <TableCaption>Örnek rapor · 3 satır</TableCaption>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Makine</TableHead>
                        <TableHead className="text-right">OEE</TableHead>
                        <TableHead className="text-right">Fire (kg)</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {[
                        ["M-01", "%82", "124"],
                        ["M-02", "%76", "201"],
                        ["M-03", "%91", "88"],
                      ].map((r) => (
                        <TableRow key={r[0]}>
                          <TableCell className="font-mono">{r[0]}</TableCell>
                          <TableCell className="text-right font-mono tabular-nums">
                            {r[1]}
                          </TableCell>
                          <TableCell className="text-right font-mono tabular-nums">
                            {r[2]}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </TabsContent>
              <TabsContent value="about">
                <p className="text-sm text-muted-foreground">
                  Sayılar hep tek genişlikte (tabular-nums) ve sağa dayalı — göz
                  basamakları sütun gibi okusun diye.
                </p>
              </TabsContent>
            </Tabs>
          </Section>

          <GroupRule label="Veri" />

          <Section
            id="grafikler"
            title="Grafikler"
            description="Tek cephe: <Chart>. Türü veri şekli seçer (analyze), renkler jetonlardan gelir — dolayısıyla koyu tema kendiliğinden doğru. Lejant tıklanabilir; bir seriyi kapatıp açabilirsin."
          >
            <div className="grid gap-4 md:grid-cols-2">
              <div className="md:col-span-2">
                <Specimen label="çizgi · zaman serisi (ciro)">
                  <ResultView result={SAMPLE_LINE} />
                </Specimen>
              </div>
              <Specimen label="sütun · tek ölçü (OEE)">
                <ResultView result={SAMPLE_BAR} />
              </Specimen>
              <Specimen label="gruplu sütun · 2 kırılım">
                <ResultView result={SAMPLE_GROUPED} />
              </Specimen>
              <Specimen label="kpi · tek satır">
                <ResultView result={SAMPLE_KPI} />
              </Specimen>
              <Specimen label="sütun + çizgi · çapraz karşılaştırma">
                <ResultView result={SAMPLE_COMBO} viewHint="combo" />
              </Specimen>
              <Specimen label="ısı haritası · marj ortalamalı">
                <ResultView result={SAMPLE_HEATMAP} viewHint="heatmap" />
              </Specimen>
              <div className="md:col-span-2">
                <Specimen label="panelli · 3 kırılım (ortak y-skala)">
                  <ResultView result={SAMPLE_FACET} viewHint="facet" />
                </Specimen>
              </div>
            </div>
          </Section>

          <Section
            id="yorum-cubugu"
            title="Yorum çubuğu"
            description="Raporun yapısal durumu, oynanabilir chip'ler olarak. Chip düzenlemesi LLM'e gitmez — deterministik /cube yolundan koşar."
          >
            <Specimen>
              <InterpretationBar
                cq={
                  {
                    cube: "partiler",
                    measures: ["ciro", "fire_kg"],
                    dimensions: ["kumas_cinsi"],
                    timeDimensions: [
                      { dimension: "tarih", granularity: "month" },
                    ],
                    filters: [
                      {
                        dimension: "tarih",
                        operator: "gte",
                        value: "2026-07-01",
                      },
                    ],
                  } as unknown as CubeQuery
                }
                onEdit={() => {}}
              />
            </Specimen>
          </Section>

          <Section
            id="erd"
            title="ERD"
            description="Veri modeli tarayıcısı — küpler ve aralarındaki ilişkiler."
          >
            <ErdView models={ERD_MODELS} relationships={ERD_RELS} />
          </Section>

          <GroupRule label="Desenler" />

          <Section
            id="sohbet"
            title="Sohbet"
            description="Mesaj primitifleri gerçek akışın kendisi: cevap bulunamadığında dürüst not + öneri chip'leri, bulunduğunda köken rozetiyle rapor."
          >
            <div className="h-[540px] overflow-hidden rounded-lg border border-border">
              <ChatPanel
                items={CHAT_ITEMS}
                active={CHAT_ITEMS[0] ?? null}
                pending={false}
                onSelect={() => {}}
                onSubmit={() => {}}
              />
            </div>
          </Section>

          <Section
            id="dusunme"
            title="Düşünme"
            description="Bekleme boşluğu doldurulmaz, anlatılır: canlı zincir yanıt beklerken akar; cevap gelince kapalı bir bloğa çekilir."
          >
            <div className="grid gap-4 sm:grid-cols-2">
              <Specimen label="canlı — yanıt beklenirken">
                <ChainOfThought />
              </Specimen>
              <Specimen label="yerleşik — açılıp kapanır">
                <Reasoning durationMs={4200} />
              </Specimen>
            </div>
          </Section>

          <footer className="border-t border-border pt-6 pb-4">
            <p className="text-xs text-muted-foreground">
              Bu sayfa yalnız oturum açmış kullanıcıya görünür (proxy.ts) ve
              indekslenmez. Bir bileşen burada yoksa tasarım sisteminde de yok
              sayılır.
            </p>
          </footer>
        </main>
      </div>
    </div>
  );
}
