"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { apiErrorMessage, ask } from "@/lib/api-client";
import { ChatPanel } from "@/components/ChatPanel";
import { FloatingControls } from "@/components/FloatingControls";
import { HelpPanel } from "@/components/HelpPanel";
import { Landing } from "@/components/Landing";
import { ReportPanel } from "@/components/ReportPanel";
import { SchemaPanel } from "@/components/SchemaPanel";
import { SettingsDrawer } from "@/components/SettingsDrawer";
import { useHistory } from "@/stores/history";
import type { AskResponse } from "@/lib/types";

type Drawer = "settings" | "help" | null;

export default function Home() {
  const [active, setActive] = useState<AskResponse | null>(null);
  const [drawer, setDrawer] = useState<Drawer>(null);
  const items = useHistory((s) => s.items);
  const addHistory = useHistory((s) => s.add);

  const mutation = useMutation<AskResponse, unknown, string>({
    mutationFn: (q: string) => ask({ question: q }),
    onSuccess: (data) => {
      addHistory(data);
      setActive(data);
    },
  });

  const submit = (q: string) => {
    setDrawer(null);
    mutation.mutate(q);
  };

  const started = items.length > 0 || mutation.isPending;
  const pendingQuestion = mutation.isPending ? mutation.variables : undefined;

  return (
    <div className="h-full">
      {!started ? (
        <Landing onSubmit={submit} />
      ) : (
        <div className="flex h-full min-h-0">
          <section className="flex w-[38%] min-w-[320px] max-w-[440px] shrink-0 flex-col border-r border-hairline">
            <ChatPanel
              items={items}
              active={active}
              pending={mutation.isPending}
              pendingQuestion={pendingQuestion}
              onSelect={setActive}
              onSubmit={submit}
            />
          </section>
          <section className="min-w-0 flex-1 overflow-auto">
            <ReportPanel
              data={active}
              pending={mutation.isPending}
              error={mutation.isError ? apiErrorMessage(mutation.error) : null}
            />
          </section>
        </div>
      )}

      <FloatingControls onHelp={() => setDrawer("help")} onSettings={() => setDrawer("settings")} />

      <SettingsDrawer
        open={drawer !== null}
        onClose={() => setDrawer(null)}
        title={drawer === "help" ? "dima · yardım" : "Ayarlar · Veri Modeli"}
      >
        {drawer === "help" ? <HelpPanel onPick={submit} /> : <SchemaPanel />}
      </SettingsDrawer>
    </div>
  );
}
