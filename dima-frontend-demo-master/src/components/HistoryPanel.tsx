"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deleteConversation, listConversations, restoreConversation } from "@/lib/api-client";
import { useState } from "react";
import { HataSeridi } from "@/components/HataSeridi";
import { hataMetni } from "@/lib/mutasyonHatasi";
import { GeriAlSeridi } from "@/components/GeriAlSeridi";

// Sohbet geçmişi (per-user, backend kalıcı). Liste → tıkla=resume, × = soft-delete.
// Minimal: demo sağ sheet içinde render edilir (SettingsDrawer). dima-frontend'in
// elaborate AppSidebar'ı KOPYALANMADI — demo sade tutulur.
// 🔴🔴 `§K12` — Ölçüldü (canlı, Playwright kampanyası): aynı başlıkla açılan 4 thread
// yalnız DAKİKA çözünürlüklü bu damgayla ayrışamıyordu — hızlı ardışık (saniyeler
// arayla) sohbetler aynı "gg.aa ss:dd" değerini üretiyordu. Saniye eklendi; asıl
// ayrım sinyali `last_question` (aşağıda) ama bu da bağımsız bir kök-düzeltme.
function fmtDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString("tr-TR", {
      day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit",
    });
  } catch {
    return "";
  }
}

export function HistoryPanel({
  onResume,
  onNewChat,
  activeSessionId,
}: {
  onResume: (id: string) => void;
  onNewChat: () => void;
  activeSessionId?: string | null;
}) {
  // 🔴 Denetim F3: mutasyonlar hata yüzeyi taşımıyordu — başarısız bir işlem
  // ekranda hiçbir iz bırakmıyordu. *Sessizce başarısız olan bir eylem,
  // kullanıcıya ürünün bozuk olduğunu değil KENDİSİNİN yanlış yaptığını düşündürür.*
  const [hata, setHata] = useState<string | null>(null);
  // 🔴 Denetim F2: sunucu **silmiyor damgalıyordu** ama geri getiren hiçbir yol yoktu —
  // kullanıcı açısından soft-delete ile hard-delete **birebir aynı deneyimdi**.
  // ⚠ Ad da tutuluyor: *"silindi"* tek başına NEYİN silindiğini söylemez ve kullanıcı
  // geri alıp almayacağına karar veremez.
  const [silinen, setSilinen] = useState<{ id: string; title: string } | null>(null);
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["conversations"],
    queryFn: listConversations,
  });
  const geriAl = useMutation({
    onError: (e) => setHata(hataMetni(e, "Geri alma")),
    mutationFn: (id: string) => restoreConversation(id),
    onSuccess: () => {
      setSilinen(null);
      qc.invalidateQueries({ queryKey: ["conversations"] });
    },
  });
  const del = useMutation({
    onError: (e) => {
      // 🔴 Silme başarısızsa geri-al şeridi **gösterilmemeli**: olmayan bir silmeyi
      // geri almayı teklif etmek, kullanıcıya yanlış bir dünya tarif eder.
      setSilinen(null);
      setHata(hataMetni(e, "Sohbet silme"));
    },
    mutationFn: (id: string) => deleteConversation(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["conversations"] }),
  });

  return (
    <div className="space-y-3">
      <HataSeridi metin={hata} onKapat={() => setHata(null)} />
      <GeriAlSeridi
        etiket={silinen?.title ?? null}
        onGeriAl={async () => {
          await geriAl.mutateAsync(silinen!.id);
        }}
      />
      <button
        onClick={onNewChat}
        className="w-full border border-hairline px-3 py-1.5 text-left font-mono text-[12px] text-neutral-600 transition-colors hover:border-accent/50 hover:text-foreground dark:text-neutral-300"
      >
        + yeni sohbet
      </button>

      {isLoading ? (
        <p className="font-mono text-[11px] text-neutral-400">yükleniyor…</p>
      ) : !data || data.length === 0 ? (
        <p className="font-mono text-[11px] text-neutral-400">henüz kayıtlı sohbet yok</p>
      ) : (
        <ul className="space-y-0.5">
          {data.map((c) => {
            const isActive = c.session_id === activeSessionId;
            return (
              <li
                key={c.id}
                className={`group flex items-center gap-1 border-l-2 pl-2 transition-colors ${
                  isActive ? "border-accent bg-accent/[0.06]" : "border-transparent hover:bg-neutral-500/[0.04]"
                }`}
              >
                <button onClick={() => onResume(c.id)} className="min-w-0 flex-1 py-1.5 text-left">
                  <div className="truncate text-[13px] text-foreground">
                    {c.title || "(başlıksız)"}
                  </div>
                  {/* `§K12` — SON TUR ÖNİZLEMESİ: aynı başlıkla açılan sohbetleri ayırt
                      eden asıl sinyal (başlık aynı kalsa bile son soru neredeyse hiç
                      aynı olmaz) — bkz. `ConversationOut.last_question` (backend). */}
                  {c.last_question && (
                    <div className="truncate text-[11px] text-neutral-500">
                      {c.last_question}
                    </div>
                  )}
                  <div className="font-mono text-[10px] text-neutral-400">
                    {c.message_count} mesaj · {fmtDate(c.updated_at)}
                  </div>
                </button>
                <button
                  // ⚠ Ad silmeden ÖNCE yakalanır: silindikten sonra liste tazelenir ve
                  // satır kaybolur — o an adı sormanın yeri kalmaz.
                  onClick={() => {
                    setSilinen({ id: c.id, title: c.title || "Sohbet" });
                    del.mutate(c.id);
                  }}
                  disabled={del.isPending}
                  title="Sohbeti sil"
                  className="px-1.5 font-mono text-sm text-neutral-400 opacity-0 transition-opacity hover:text-red-500 group-hover:opacity-100"
                >
                  ×
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
