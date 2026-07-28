"use client";

import { useMemo, useSyncExternalStore } from "react";
import { useTheme } from "next-themes";
import {
  Background,
  BackgroundVariant,
  Controls,
  Handle,
  Position,
  ReactFlow,
  ReactFlowProvider,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import type { ColumnMeta, ModelMeta, RelationshipMeta } from "@dima/contracts";

// mounted flag without setState-in-effect: server snapshot false, client true.
const subscribeNoop = () => () => {};

type TableData = { name: string; columns: ColumnMeta[] };

// Tablo düğümü: başlık + kolon listesi. Kenarlar sol/sağ handle'lara bağlanır.
function TableNode({ data }: NodeProps<Node<TableData>>) {
  return (
    <div className="min-w-[180px] overflow-hidden rounded-lg border border-border bg-card shadow-sm">
      <Handle type="target" position={Position.Left} className="!size-2 !border-brand !bg-brand" />
      <div className="flex items-center gap-1.5 border-b border-border bg-muted/40 px-3 py-1.5 font-mono text-[12px] font-medium text-foreground">
        <span className="text-brand">◆</span>
        {data.name}
      </div>
      <ul className="max-h-44 overflow-auto py-1">
        {data.columns.map((c) => (
          <li
            key={c.name}
            className="flex items-center justify-between gap-4 px-3 py-0.5 font-mono text-[10px]"
          >
            <span className="truncate text-foreground">{c.name}</span>
            <span className="shrink-0 text-muted-foreground">{c.type}</span>
          </li>
        ))}
      </ul>
      <Handle type="source" position={Position.Right} className="!size-2 !border-brand !bg-brand" />
    </div>
  );
}

const nodeTypes = { table: TableNode };

function ErdInner({
  models,
  relationships,
}: {
  models: ModelMeta[];
  relationships: RelationshipMeta[];
}) {
  // next-themes'in çözdüğü tema yalnız client'ta bilinir; sunucu her zaman "light"
  // render eder. İlk client render'ında da "light" diyip temayı mount SONRASI
  // uygulamıyoruz → React Flow'un kök class'ında hydration uyuşmazlığı olmuyor.
  const { resolvedTheme } = useTheme();
  const mounted = useSyncExternalStore(subscribeNoop, () => true, () => false);
  const colorMode = mounted && resolvedTheme === "dark" ? "dark" : "light";

  // Katmanlı yerleşim: ilişki grafiğinde BFS ile derinlik hesapla, her derinliği
  // bir SÜTUN yap. Kenarlar hep sağdan-sola aktığı için bu, kesişmelerin büyük
  // kısmını kaynağında yok eder (naif kare ızgara tam tersini yapıyordu).
  const layout = useMemo(() => {
    const names = models.map((m) => m.name);
    const adj = new Map<string, Set<string>>(names.map((n) => [n, new Set<string>()]));
    for (const r of relationships) {
      const [a, b] = r.models;
      if (adj.has(a) && adj.has(b)) {
        adj.get(a)!.add(b);
        adj.get(b)!.add(a);
      }
    }
    const depth = new Map<string, number>();
    // en çok bağlantılı düğümden başla — merkez tablo (fact) solda kalsın
    const order = [...names].sort((x, y) => (adj.get(y)?.size ?? 0) - (adj.get(x)?.size ?? 0));
    for (const seed of order) {
      if (depth.has(seed)) continue;
      depth.set(seed, 0);
      const queue = [seed];
      while (queue.length) {
        const cur = queue.shift()!;
        for (const nb of adj.get(cur) ?? []) {
          if (!depth.has(nb)) {
            depth.set(nb, (depth.get(cur) ?? 0) + 1);
            queue.push(nb);
          }
        }
      }
    }
    const perColumn = new Map<number, number>();
    const pos = new Map<string, { x: number; y: number }>();
    for (const n of names) {
      const d = depth.get(n) ?? 0;
      const row = perColumn.get(d) ?? 0;
      perColumn.set(d, row + 1);
      pos.set(n, { x: d * 340, y: row * 260 });
    }
    return pos;
  }, [models, relationships]);

  const nodes = useMemo<Node<TableData>[]>(() => {
    return models.map((m) => ({
      id: m.name,
      type: "table",
      position: layout.get(m.name) ?? { x: 0, y: 0 },
      data: { name: m.name, columns: m.columns },
    }));
  }, [models, layout]);

  const edges = useMemo<Edge[]>(() => {
    const ids = new Set(models.map((m) => m.name));
    const depthOf = (n: string) => layout.get(n)?.x ?? 0;
    return relationships
      .filter((r) => r.models.length >= 2 && ids.has(r.models[0]) && ids.has(r.models[1]))
      .map((r, i) => {
        // Kenar HER ZAMAN soldaki düğümden sağdakine aksın; ters yönde çizilirse
        // handle'ların etrafından dolaşıp spagetti yapıyordu.
        const [a, b] = r.models;
        const [source, target] = depthOf(a) <= depthOf(b) ? [a, b] : [b, a];
        return {
          id: `e-${r.name ?? i}`,
          source,
          target,
          type: "smoothstep",
          pathOptions: { borderRadius: 14, offset: 18 },
          label: r.join_type || undefined,
          labelShowBg: true,
          labelStyle: { fontSize: 10, fontFamily: "var(--font-mono)", fill: "var(--muted-foreground)" },
          labelBgStyle: { fill: "var(--card)" },
          labelBgPadding: [4, 2] as [number, number],
          labelBgBorderRadius: 4,
          style: { stroke: "var(--border)", strokeWidth: 1.5 },
        };
      });
  }, [models, relationships, layout]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      colorMode={colorMode}
      fitView
      minZoom={0.3}
      proOptions={{ hideAttribution: true }}
    >
      <Background variant={BackgroundVariant.Dots} gap={20} size={1} className="!bg-transparent" />
      <Controls showInteractive={false} />
    </ReactFlow>
  );
}

/** ERD graph of the cube catalog — tables as nodes, relationships as edges. */
export function ErdView({
  models,
  relationships,
  className,
}: {
  models: ModelMeta[];
  relationships: RelationshipMeta[];
  className?: string;
}) {
  return (
    <div className={className ?? "h-[480px] w-full overflow-hidden rounded-lg border border-border"}>
      <ReactFlowProvider>
        <ErdInner models={models} relationships={relationships} />
      </ReactFlowProvider>
    </div>
  );
}
