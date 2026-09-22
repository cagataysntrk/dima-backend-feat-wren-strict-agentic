"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Share2 } from "lucide-react";
import { gateway } from "@/lib/gateway";
import { EmptyState } from "@/components/shell/EmptyState";
import { ErdView } from "@/components/schema/ErdView";
import { Skeleton } from "@dima/ui/primitives/skeleton";

export function SchemaView() {
  const graph = useQuery({ queryKey: ["schema-graph"], queryFn: gateway.schemaGraph });

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6 p-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">Şema</h1>
        <p className="text-sm text-muted-foreground">
          Tablolarınız ve aralarındaki ilişkiler. İlişkiler veri modelinde tanımlanır.
        </p>
      </header>

      {graph.isPending && <Skeleton className="h-[520px] w-full rounded-xl" />}
      {graph.isError && (
        <p role="alert" className="text-sm text-destructive">
          {graph.error.message}
        </p>
      )}
      {graph.data &&
        (graph.data.tables.length === 0 ? (
          <div className="surface">
            <EmptyState
              icon={Share2}
              title="Gösterilecek tablo yok."
              hint="Veri yükleyin ya da yöneticinizden bir veri kaynağı tanımlamasını isteyin."
            />
          </div>
        ) : (
          <>
            <ErdView tables={graph.data.tables} edges={graph.data.edges} />
            {graph.data.edges.length === 0 && (
              <p className="text-sm text-muted-foreground">
                Henüz tanımlı ilişki yok — tablolar ayrı duruyor.{" "}
                <Link href="/app/model" className="font-medium text-brand hover:underline">
                  Veri modelinde
                </Link>{" "}
                bir sütunu başka bir tablonun sütununa bağlayın.
              </p>
            )}
          </>
        ))}
    </div>
  );
}
