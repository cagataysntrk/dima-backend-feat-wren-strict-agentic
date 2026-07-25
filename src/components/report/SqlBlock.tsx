"use client";

import { useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { Check, ChevronRight, Copy } from "lucide-react";
import { formatSql, tokenizeSql, type SqlTokenType } from "@/lib/sql-format";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

// Renkler grafik token'larından gelir → tema değişince otomatik doğru.
const TOKEN_CLASS: Record<SqlTokenType, string> = {
  keyword: "text-brand font-medium",
  function: "text-[var(--chart-5)]",
  string: "text-[var(--chart-2)]",
  number: "text-[var(--chart-3)]",
  comment: "text-muted-foreground italic",
  punct: "text-muted-foreground",
  ident: "text-foreground",
  space: "",
};

/**
 * The query behind the answer — collapsed by default, inside the result card
 * under the chart/table. Expanded it reads like a code editor: reflowed onto
 * clause lines, gutter line numbers, token colouring from the chart palette.
 */
export function SqlBlock({ sql, className }: { sql: string; className?: string }) {
  const t = useTranslations();
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const lines = useMemo(() => {
    const pretty = formatSql(sql);
    return pretty.split("\n").map((line) => tokenizeSql(line));
  }, [sql]);

  const copy = () => {
    void navigator.clipboard?.writeText(formatSql(sql)).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };

  return (
    <Collapsible open={open} onOpenChange={setOpen} className={cn("min-w-0", className)}>
      <div className="flex items-center gap-1">
        <CollapsibleTrigger className="group flex items-center gap-1 text-xs text-muted-foreground transition-colors hover:text-foreground">
          <ChevronRight className="size-3.5 transition-transform duration-200 group-data-[state=open]:rotate-90" />
          {t("common.sql")}
        </CollapsibleTrigger>
        {open && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label={t("common.sql")}
                onClick={copy}
                className="size-6 text-muted-foreground hover:text-foreground"
              >
                {copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="top">SQL&apos;i panoya kopyala</TooltipContent>
          </Tooltip>
        )}
      </div>

      <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down">
        <div className="mt-2 overflow-x-auto rounded-lg border border-border bg-muted/40">
          <pre className="min-w-full py-2 font-mono text-[12px] leading-relaxed">
            <code>
              {lines.map((tokens, ln) => (
                <div key={ln} className="flex px-0">
                  <span
                    aria-hidden="true"
                    className="sticky left-0 w-9 shrink-0 select-none bg-muted/40 pr-3 text-right text-muted-foreground/60 tabular-nums"
                  >
                    {ln + 1}
                  </span>
                  <span className="min-w-0 flex-1 pr-4 whitespace-pre">
                    {tokens.map((tok, i) => (
                      <span key={i} className={TOKEN_CLASS[tok.type]}>
                        {tok.text}
                      </span>
                    ))}
                  </span>
                </div>
              ))}
            </code>
          </pre>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
