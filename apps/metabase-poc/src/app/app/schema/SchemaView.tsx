"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { Share2 } from "lucide-react";
import { gateway } from "@/lib/gateway";
import { EmptyState } from "@/components/shell/EmptyState";
import { ErdView } from "@/components/schema/ErdView";
import { Skeleton } from "@dima/ui/primitives/skeleton";

export function SchemaView() {
  const t = useTranslations("schema");
  const graph = useQuery({ queryKey: ["schema-graph"], queryFn: gateway.schemaGraph });

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6 p-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">{t("title")}</h1>
        <p className="text-sm text-muted-foreground">{t("subtitle")}</p>
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
              title={t("emptyTitle")}
              hint={t("emptyHint")}
            />
          </div>
        ) : (
          <>
            <ErdView tables={graph.data.tables} edges={graph.data.edges} />
            {graph.data.edges.length === 0 && (
              <p className="text-sm text-muted-foreground">
                {t("noEdges")}{" "}
                <Link href="/app/model" className="font-medium text-brand hover:underline">
                  {t("noEdgesLink")}
                </Link>{" "}
                {t("noEdgesTail")}
              </p>
            )}
          </>
        ))}
    </div>
  );
}
