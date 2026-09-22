"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, MessagesSquare, Search } from "lucide-react";
import { useConversations } from "@/stores/conversations";
import { Button } from "@dima/ui/primitives/button";
import { Input } from "@dima/ui/primitives/input";
import { Card } from "@dima/ui/primitives/card";
import { Badge } from "@dima/ui/primitives/badge";
import { cn } from "@dima/ui/utils";

/** Tüm sohbetler — sidebar listesinin tam sayfa, aranabilir hâli. */
export default function ChatsPage() {
  const router = useRouter();
  const conversations = useConversations((s) => s.conversations);
  const activeId = useConversations((s) => s.activeId);
  const select = useConversations((s) => s.select);
  const [q, setQ] = useState("");

  const shown = useMemo(() => {
    const needle = q.trim().toLocaleLowerCase("tr-TR");
    if (!needle) return conversations;
    return conversations.filter((c) =>
      (c.title || "").toLocaleLowerCase("tr-TR").includes(needle),
    );
  }, [conversations, q]);

  const open = (id: string) => {
    select(id);
    router.push("/app");
  };

  const fmt = (ts: number) =>
    new Intl.DateTimeFormat("tr-TR", { dateStyle: "medium", timeStyle: "short" }).format(ts);

  return (
    <main className="dima-page-in mx-auto max-w-3xl space-y-6 px-6 py-10">
      <header className="space-y-3">
        <Button variant="ghost" size="sm" asChild className="-ml-2 gap-1.5">
          <Link href="/app">
            <ArrowLeft className="size-4" />
            Sohbete dön
          </Link>
        </Button>
        <h1 className="text-2xl font-semibold tracking-tight">Tüm sohbetler</h1>
      </header>

      <div className="relative">
        <Search className="absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Sohbetlerde ara…"
          aria-label="Sohbetlerde ara"
          className="pl-9"
        />
      </div>

      {shown.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-border py-14 text-center">
          <MessagesSquare className="size-5 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            {conversations.length === 0 ? "Henüz sohbet yok." : "Eşleşen sohbet yok."}
          </p>
        </div>
      ) : (
        <ul className="space-y-2">
          {shown.map((c) => (
            <li key={c.id}>
              <Card
                onClick={() => open(c.id)}
                className={cn(
                  "cursor-pointer gap-1 p-3 transition-colors hover:border-brand/40",
                  c.id === activeId && "border-brand/60",
                )}
              >
                <div className="flex items-center gap-2">
                  <MessagesSquare className="size-3.5 shrink-0 text-muted-foreground" />
                  <span className="min-w-0 flex-1 truncate text-sm text-foreground">
                    {c.title || "Yeni sohbet"}
                  </span>
                  {c.id === activeId && (
                    <Badge variant="brand-subtle" className="text-[10px]">
                      açık
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-2 pl-5.5 text-xs text-muted-foreground">
                  <span>{c.items.length} mesaj</span>
                  <span aria-hidden>·</span>
                  <time dateTime={new Date(c.createdAt).toISOString()}>{fmt(c.createdAt)}</time>
                </div>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
