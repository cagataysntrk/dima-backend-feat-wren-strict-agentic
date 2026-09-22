import { Suspense } from "react";
import type { Metadata } from "next";
import { chatConfigured } from "@/server/chat/openrouter";
import { canAnalyze, shellContext } from "@/server/session";
import { ChatView } from "./ChatView";

export const metadata: Metadata = { title: "Sohbet" };

export default async function ChatPage() {
  const ctx = await shellContext();
  const org = ctx.orgs.find((o) => o.id === ctx.activeOrgId);
  return (
    <Suspense>
      <ChatView
        company={org?.name ?? ""}
        orgId={org?.id ?? ""}
        slug={org?.slug ?? ""}
        configured={chatConfigured()}
        canSave={canAnalyze(ctx.role)}
      />
    </Suspense>
  );
}
