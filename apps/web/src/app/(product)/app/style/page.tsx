"use client";

import { toast } from "sonner";
import type { AskResponse, CubeQuery, QueryResult } from "@dima/contracts";
import { ResultView } from "@/components/ResultView";
import { ChatPanel } from "@/components/ChatPanel";
import { InterpretationBar } from "@/components/InterpretationBar";
import { ChainOfThought, Reasoning } from "@/components/ai/thinking";
import { ErdView } from "@/components/schema/ErdView";

const ERD_MODELS = [
  { name: "partiler", columns: [
    { name: "parti_no", type: "text", values: null }, { name: "makine", type: "text", values: null },
    { name: "renk", type: "text", values: null }, { name: "fire_kg", type: "number", values: null },
    { name: "ciro", type: "number", values: null }, { name: "siparis_no", type: "text", values: null },
  ] },
  { name: "makineler", columns: [{ name: "makine", type: "text", values: null }, { name: "tip", type: "text", values: null }] },
  { name: "musteriler", columns: [{ name: "musteri", type: "text", values: null }, { name: "sehir", type: "text", values: null }] },
  { name: "siparisler", columns: [
    { name: "siparis_no", type: "text", values: null }, { name: "musteri", type: "text", values: null },
    { name: "miktar", type: "number", values: null },
  ] },
];
const ERD_RELS = [
  { name: "r1", models: ["partiler", "makineler"], join_type: "many_to_one", condition: "partiler.makine = makineler.makine" },
  { name: "r2", models: ["partiler", "siparisler"], join_type: "many_to_one", condition: "partiler.siparis_no = siparisler.siparis_no" },
  { name: "r3", models: ["siparisler", "musteriler"], join_type: "many_to_one", condition: "siparisler.musteri = musteriler.musteri" },
];
import { ThemeToggle } from "@/components/shell/ThemeToggle";
import { LocaleSwitcher } from "@/components/shell/LocaleSwitcher";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const qr = (columns: string[], rows: (string | number)[][]): QueryResult => ({
  columns,
  rows: rows.map((r) => Object.fromEntries(columns.map((c, i) => [c, r[i]]))),
  row_count: rows.length,
});

const SAMPLE_BAR = qr(
  ["makine", "oee"],
  [["M-01", 0.82], ["M-02", 0.76], ["M-03", 0.91], ["M-04", 0.68], ["M-05", 0.84]],
);
const SAMPLE_LINE = qr(
  ["tarih__month", "ciro"],
  [
    ["2026-02-01", 1840000], ["2026-03-01", 2010000], ["2026-04-01", 1930000],
    ["2026-05-01", 2260000], ["2026-06-01", 2110000], ["2026-07-01", 2480000],
  ],
);
const SAMPLE_GROUPED = qr(
  ["hafta_gunu", "cinsiyet", "fire_kg"],
  [
    ["Pzt", "Kadın", 120], ["Pzt", "Erkek", 98], ["Sal", "Kadın", 140], ["Sal", "Erkek", 110],
    ["Çar", "Kadın", 90], ["Çar", "Erkek", 130], ["Per", "Kadın", 160], ["Per", "Erkek", 105],
    ["Cum", "Kadın", 100], ["Cum", "Erkek", 120],
  ],
);
const SAMPLE_KPI = qr(["ciro", "fire_kg", "oee"], [[2480000, 1240, 0.83]]);

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
    cube_query: { cube: "vardiya", measures: ["oee"], dimensions: ["makine"] } as unknown as CubeQuery,
    note: null,
    trace: [],
    suggestions: [],
    view_hint: null,
    contract_id: "qc_a1b2c3",
  },
];

const TOKENS: { name: string; className: string; border?: boolean }[] = [
  { name: "background", className: "bg-background", border: true },
  { name: "foreground", className: "bg-foreground" },
  { name: "card", className: "bg-card", border: true },
  { name: "primary", className: "bg-primary" },
  { name: "secondary", className: "bg-secondary", border: true },
  { name: "muted", className: "bg-muted", border: true },
  { name: "accent", className: "bg-accent", border: true },
  { name: "brand", className: "bg-brand" },
  { name: "destructive", className: "bg-destructive" },
  { name: "border", className: "bg-border" },
  { name: "chart-1", className: "bg-chart-1" },
  { name: "chart-2", className: "bg-chart-2" },
  { name: "chart-3", className: "bg-chart-3" },
  { name: "chart-4", className: "bg-chart-4" },
  { name: "chart-5", className: "bg-chart-5" },
];

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
      <div className="space-y-4">{children}</div>
    </section>
  );
}

export default function StyleGuide() {
  return (
    <main className="mx-auto max-w-5xl space-y-14 px-6 py-12">
      {/* Header */}
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-border pb-6">
        <div>
          <h1 className="text-4xl font-semibold tracking-tight">
            dima design system
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Deterministic · Intelligent · Modeled · Agentic — premium editorial,
            light &amp; dark.
          </p>
        </div>
        <div className="flex items-center gap-1">
          <LocaleSwitcher />
          <ThemeToggle />
        </div>
      </header>

      {/* Color tokens */}
      <Section title="Color">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5">
          {TOKENS.map((t) => (
            <div key={t.name} className="space-y-1.5">
              <div
                className={`h-16 w-full rounded-lg ${t.className} ${
                  t.border ? "border border-border" : ""
                }`}
              />
              <div className="font-mono text-xs text-muted-foreground">
                {t.name}
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* Typography */}
      <Section title="Typography">
        <div className="space-y-3">
          <p className="text-5xl font-semibold tracking-tight">Veriyle konuş.</p>
          <p className="text-xs text-muted-foreground">
            Plus Jakarta Sans — uygulama başlıkları da artık bu. Playfair yalnız
            (henüz olmayan) marketing sayfaları için ayrıldı:
          </p>
          <p className="font-display text-3xl">Playfair Display — yalnız marketing</p>
          <Separator />
          <p className="text-lg">
            Plus Jakarta Sans — the interface voice. Doğal dille sor, güvenilir
            SQL ve rapor al.
          </p>
          <p className="text-sm text-muted-foreground">
            Muted body — secondary information, captions, metadata.
          </p>
          <p className="font-mono text-sm">
            JetBrains Mono — SELECT SUM(ciro) FROM partiler WHERE ay = &apos;2026-07&apos;
          </p>
        </div>
      </Section>

      {/* Buttons */}
      <Section title="Buttons">
        <div className="flex flex-wrap items-center gap-3">
          <Button>Primary</Button>
          <Button variant="brand">Brand</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="destructive">Destructive</Button>
          <Button variant="link">Link</Button>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Button size="sm">Small</Button>
          <Button size="default">Default</Button>
          <Button size="lg">Large</Button>
          <Button disabled>Disabled</Button>
          <Button onClick={() => toast("Rapor hazır", { description: "3 satır döndü." })}>
            Toast
          </Button>
        </div>
      </Section>

      {/* Badges — provenance language */}
      <Section title="Badges &amp; provenance">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="brand">◆ CUBE</Badge>
          <Badge variant="brand-subtle">◆ CUBE·LLM</Badge>
          <Badge variant="secondary">▚ LLM·anthropic</Badge>
          <Badge variant="outline">⚙ KURAL</Badge>
          <Badge>default</Badge>
          <Badge variant="destructive">alert</Badge>
        </div>
      </Section>

      {/* Chat — AI message primitives (MessageScroller / Message / Bubble) */}
      <Section title="Sohbet">
        <div className="h-[540px] overflow-hidden rounded-lg border border-border">
          <ChatPanel
            items={CHAT_ITEMS}
            active={CHAT_ITEMS[1]}
            pending={false}
            onSelect={() => {}}
            onSubmit={() => {}}
          />
        </div>
      </Section>

      {/* Düşünme — canlı zincir (bekleme) ve cevabın yanında kalan kapalı blok */}
      <Section title="Düşünme">
        <div className="grid gap-6 sm:grid-cols-2">
          <div className="rounded-lg border border-border p-4">
            <p className="mb-3 font-mono text-[11px] uppercase tracking-wide text-muted-foreground">
              canlı — yanıt beklenirken
            </p>
            <ChainOfThought />
          </div>
          <div className="rounded-lg border border-border p-4">
            <p className="mb-3 font-mono text-[11px] uppercase tracking-wide text-muted-foreground">
              yerleşik — açılıp kapanır
            </p>
            <Reasoning durationMs={4200} />
          </div>
        </div>
      </Section>

      {/* ERD — React Flow schema diagram */}
      <Section title="ERD">
        <ErdView models={ERD_MODELS} relationships={ERD_RELS} />
      </Section>

      {/* Interpretation bar — playable CubeQuery chips */}
      <Section title="Yorum çubuğu">
        <Card className="p-4">
          <InterpretationBar
            cq={
              {
                cube: "partiler",
                measures: ["ciro", "fire_kg"],
                dimensions: ["kumas_cinsi"],
                timeDimensions: [{ dimension: "tarih", granularity: "month" }],
                filters: [{ dimension: "tarih", operator: "gte", value: "2026-07-01" }],
              } as unknown as CubeQuery
            }
            onEdit={() => {}}
          />
        </Card>
      </Section>

      {/* Charts — the <Chart> façade (Recharts + tokens) */}
      <Section title="Charts">
        <div className="grid gap-4 md:grid-cols-2">
          <Card className="p-4">
            <p className="mb-2 text-sm font-medium">Sütun · tek ölçü (OEE)</p>
            <ResultView result={SAMPLE_BAR} />
          </Card>
          <Card className="p-4">
            <p className="mb-2 text-sm font-medium">Çizgi · zaman serisi (ciro)</p>
            <ResultView result={SAMPLE_LINE} />
          </Card>
          <Card className="p-4">
            <p className="mb-2 text-sm font-medium">Gruplu sütun · 2 kırılım</p>
            <ResultView result={SAMPLE_GROUPED} />
          </Card>
          <Card className="p-4">
            <p className="mb-2 text-sm font-medium">KPI · tek satır</p>
            <ResultView result={SAMPLE_KPI} />
          </Card>
        </div>
      </Section>

      {/* Form controls */}
      <Section title="Form controls">
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
        </div>
        <div className="flex flex-wrap items-center gap-4">
          <ToggleGroup type="single" defaultValue="chart" variant="outline">
            <ToggleGroupItem value="chart">Grafik</ToggleGroupItem>
            <ToggleGroupItem value="table">Tablo</ToggleGroupItem>
          </ToggleGroup>
        </div>
      </Section>

      {/* Cards */}
      <Section title="Cards">
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
              <CardTitle>Loading state</CardTitle>
              <CardDescription>Skeletons</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
              <Skeleton className="h-24 w-full" />
            </CardContent>
          </Card>
        </div>
      </Section>

      {/* Overlays */}
      <Section title="Overlays">
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
                <SheetDescription>Şema tarayıcısı burada açılır.</SheetDescription>
              </SheetHeader>
            </SheetContent>
          </Sheet>
        </div>
      </Section>

      {/* Tabs + Table */}
      <Section title="Tabs &amp; table">
        <Tabs defaultValue="table">
          <TabsList>
            <TabsTrigger value="table">Tablo</TabsTrigger>
            <TabsTrigger value="about">Hakkında</TabsTrigger>
          </TabsList>
          <TabsContent value="table">
            <div className="overflow-x-auto">
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
              Recharts + shadcn chart kit, token renkleriyle. Isı haritası ve
              panel görünümleri şimdilik tabloya düşer (visx ileride).
            </p>
          </TabsContent>
        </Tabs>
      </Section>
    </main>
  );
}
