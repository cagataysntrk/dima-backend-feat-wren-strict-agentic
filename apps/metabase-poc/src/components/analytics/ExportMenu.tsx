"use client";

import { Download } from "lucide-react";
import { gateway, type DrillScope } from "@/lib/gateway";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

/** CSV / Excel download of a card, with the dashboard filters applied when scoped. */
export function ExportMenu({ cardId, scope }: { cardId: number; scope?: DrillScope }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon-sm" aria-label="Dışa aktar">
          <Download className="size-4" aria-hidden />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem asChild>
          <a href={gateway.exportUrl(cardId, "xlsx", scope)} download>
            Excel (.xlsx)
          </a>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <a href={gateway.exportUrl(cardId, "csv", scope)} download>
            CSV (.csv)
          </a>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
