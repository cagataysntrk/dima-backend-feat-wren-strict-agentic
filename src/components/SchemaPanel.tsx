"use client";

import { useQuery } from "@tanstack/react-query";
import { Database, GitBranch, Network } from "lucide-react";
import { getSchema } from "@/lib/api-client";
import { ErdView } from "@/components/schema/ErdView";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

// Veri modeli (şema) — cube kataloğu: tablolar/kolonlar + ilişkiler. Artifact panelinde açılır.
export function SchemaPanel() {
  const { data, isLoading, isError } = useQuery({ queryKey: ["schema"], queryFn: getSchema });

  if (isLoading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-9 w-full" />
        <Skeleton className="h-9 w-full" />
        <Skeleton className="h-9 w-full" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <p className="rounded-lg border border-destructive/40 bg-destructive/5 px-3 py-2 text-sm text-destructive">
        Backend&apos;e ulaşılamadı. dima-backend çalışıyor mu?
      </p>
    );
  }

  const rels = data.relationships ?? [];

  return (
    <Tabs defaultValue="tables" className="gap-4">
      <TabsList>
        <TabsTrigger value="tables" className="gap-1.5">
          <Database className="size-3.5" /> Tablolar
          <Badge variant="secondary" className="ml-1 h-4 px-1 text-[10px]">
            {data.models.length}
          </Badge>
        </TabsTrigger>
        <TabsTrigger value="relationships" className="gap-1.5">
          <GitBranch className="size-3.5" /> İlişkiler
          <Badge variant="secondary" className="ml-1 h-4 px-1 text-[10px]">
            {rels.length}
          </Badge>
        </TabsTrigger>
        <TabsTrigger value="diagram" className="gap-1.5">
          <Network className="size-3.5" /> Diyagram
        </TabsTrigger>
      </TabsList>

      <TabsContent value="tables">
        <Accordion type="multiple" className="w-full">
          {data.models.map((model) => (
            <AccordionItem key={model.name} value={model.name}>
              <AccordionTrigger className="gap-2 py-2.5 font-mono text-sm hover:no-underline">
                <span className="flex items-center gap-2">
                  <span className="text-brand">◆</span>
                  {model.name}
                  <span className="text-xs font-normal text-muted-foreground">
                    {model.columns.length} kolon
                  </span>
                </span>
              </AccordionTrigger>
              <AccordionContent>
                <ul className="divide-y divide-border rounded-md border border-border">
                  {model.columns.map((col) => (
                    <li
                      key={col.name}
                      className="flex items-center justify-between gap-3 px-3 py-1.5 font-mono text-xs"
                    >
                      <span className="truncate text-foreground">{col.name}</span>
                      <span className="shrink-0 text-muted-foreground">{col.type}</span>
                    </li>
                  ))}
                </ul>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </TabsContent>

      <TabsContent value="relationships">
        {rels.length === 0 ? (
          <p className="px-1 py-4 text-sm text-muted-foreground">Tanımlı ilişki yok.</p>
        ) : (
          <ul className="space-y-2">
            {rels.map((rel) => (
              <li key={rel.name} className="rounded-lg border border-border p-3">
                <div className="flex items-center gap-2 font-mono text-xs text-foreground">
                  {rel.models.join(" → ")}
                  {rel.join_type && (
                    <Badge variant="outline" className="text-[10px]">
                      {rel.join_type}
                    </Badge>
                  )}
                </div>
                <div className="mt-1 font-mono text-[11px] text-muted-foreground">{rel.condition}</div>
              </li>
            ))}
          </ul>
        )}
      </TabsContent>

      <TabsContent value="diagram">
        <ErdView models={data.models} relationships={rels} />
      </TabsContent>
    </Tabs>
  );
}
