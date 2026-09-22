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
import type { SchemaColumn, SchemaEdge, SchemaTable } from "@/lib/gateway";

// mounted flag without setState-in-effect: server snapshot false, client true.
const subscribeNoop = () => () => {};

type TableData = { name: string; columns: SchemaColumn[]; linked: Set<string> };

/** Table node: header + column list. Edges attach to the left/right handles. */
function TableNode({ data }: NodeProps<Node<TableData>>) {
  return (
    <div className="min-w-[190px] overflow-hidden rounded-lg border border-border bg-card shadow-sm">
      <Handle type="target" position={Position.Left} className="!size-2 !border-brand !bg-brand" />
      <div className="flex items-center gap-1.5 border-b border-border bg-muted/40 px-3 py-1.5 font-mono text-[12px] font-medium">
        <span className="text-brand">◆</span>
        {data.name}
      </div>
      <ul className="max-h-44 overflow-auto py-1">
        {data.columns.map((c) => (
          <li key={c.name} className="flex items-center justify-between gap-4 px-3 py-0.5 font-mono text-[10px]">
            <span className="truncate">
              {/* A column that carries a relationship is worth spotting in the list. */}
              {data.linked.has(c.name) && <span className="mr-1 text-brand">↗</span>}
              {c.name}
            </span>
            <span className="shrink-0 text-muted-foreground">{c.type}</span>
          </li>
        ))}
      </ul>
      <Handle type="source" position={Position.Right} className="!size-2 !border-brand !bg-brand" />
    </div>
  );
}

const nodeTypes = { table: TableNode };

function ErdInner({ tables, edges: rels }: { tables: SchemaTable[]; edges: SchemaEdge[] }) {
  // next-themes only resolves on the client; the server always renders "light".
  // Applying the theme after mount keeps React Flow's root class hydration-safe.
  const { resolvedTheme } = useTheme();
  const mounted = useSyncExternalStore(subscribeNoop, () => true, () => false);
  const colorMode = mounted && resolvedTheme === "dark" ? "dark" : "light";

  // Layered layout: BFS depth over the relationship graph, one COLUMN per depth.
  // Edges then always flow left to right, which removes most crossings at the
  // source (a naive grid produces the opposite).
  const layout = useMemo(() => {
    const names = tables.map((t) => t.name);
    const adj = new Map<string, Set<string>>(names.map((n) => [n, new Set<string>()]));
    for (const r of rels) {
      if (adj.has(r.from) && adj.has(r.to)) {
        adj.get(r.from)!.add(r.to);
        adj.get(r.to)!.add(r.from);
      }
    }
    const depth = new Map<string, number>();
    // Start from the most connected table so the fact table sits on the left.
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
  }, [tables, rels]);

  const nodes = useMemo<Node<TableData>[]>(() => {
    const linked = new Map<string, Set<string>>();
    for (const r of rels) {
      (linked.get(r.from) ?? linked.set(r.from, new Set()).get(r.from)!).add(r.fromColumn);
      (linked.get(r.to) ?? linked.set(r.to, new Set()).get(r.to)!).add(r.toColumn);
    }
    return tables.map((t) => ({
      id: t.name,
      type: "table",
      position: layout.get(t.name) ?? { x: 0, y: 0 },
      data: { name: t.name, columns: t.columns, linked: linked.get(t.name) ?? new Set<string>() },
    }));
  }, [tables, rels, layout]);

  const edges = useMemo<Edge[]>(() => {
    const depthOf = (n: string) => layout.get(n)?.x ?? 0;
    return rels.map((r) => {
      // Always draw from the left-hand node: reversed, the edge loops around
      // the handles and turns into spaghetti.
      const [source, target] = depthOf(r.from) <= depthOf(r.to) ? [r.from, r.to] : [r.to, r.from];
      return {
        id: r.id,
        source,
        target,
        type: "smoothstep",
        pathOptions: { borderRadius: 14, offset: 18 },
        label: `${r.fromColumn} → ${r.toColumn}`,
        labelShowBg: true,
        labelStyle: { fontSize: 10, fontFamily: "var(--font-mono)", fill: "var(--muted-foreground)" },
        labelBgStyle: { fill: "var(--card)" },
        labelBgPadding: [4, 2] as [number, number],
        labelBgBorderRadius: 4,
        style: { stroke: "var(--border)", strokeWidth: 1.5 },
      };
    });
  }, [rels, layout]);

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

/** Schema diagram — tables as nodes, declared relationships as edges. */
export function ErdView({
  tables,
  edges,
  className,
}: {
  tables: SchemaTable[];
  edges: SchemaEdge[];
  className?: string;
}) {
  return (
    <div className={className ?? "h-[520px] w-full overflow-hidden rounded-xl border border-border"}>
      <ReactFlowProvider>
        <ErdInner tables={tables} edges={edges} />
      </ReactFlowProvider>
    </div>
  );
}
