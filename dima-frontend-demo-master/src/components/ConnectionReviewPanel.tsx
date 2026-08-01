"use client";

// DB bağlama sihirbazı (Faz 4.5, 31 Temmuz 2026) — tenant-kendi-hizmeti: gerçek bir
// Postgres veritabanına bağlan → test et → gerçek şema introspection'ından üretilen
// TASLAK MDL'i (ölçü/boyut sınıflandırması + FK ilişkileri) İNCELE → onayla. Excel/CSV
// akışının (composer'daki 📎, ephemeral/tek-tablo) AKSİNE bu yol KALICI/çok-tablolu —
// ikisi ayrı ihtiyaçlara hizmet eder, biri diğerinin yerini almaz (bkz. backend/CLAUDE.md
// Faz 4 plan notu).

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  confirmConnectionDraft,
  createTenantConnection,
  deleteTenantConnection,
  getConnectionDraft,
  listTenantConnections,
  testTenantConnection,
} from "@/lib/api-client";
import { usePermission } from "@/lib/usePermission";
import type { ConnectionDraft, DraftCube } from "@/lib/types";

type Step = "form" | "review" | "done";

const inputCls =
  "w-full rounded-md border border-hairline bg-transparent px-3 py-2 text-sm text-foreground outline-none focus:border-accent";
const labelCls = "mb-1 block font-mono text-[0.7rem] uppercase tracking-wide text-muted";

function FormField({
  label,
  ...props
}: { label: string } & React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <div className="mb-3">
      <label className={labelCls}>{label}</label>
      <input className={inputCls} {...props} />
    </div>
  );
}

export function ConnectionReviewPanel() {
  const qc = useQueryClient();
  // Doğrulama turu düzeltmesi (1 Ağustos 2026): bu panel HİÇ izin kontrolü YAPMIYORDU —
  // `connection:write` yetkisi olmayan (analyst/viewer) bir kullanıcı sihirbazın TAMAMINI
  // görüyor, submit ettiğinde backend'in doğru şekilde engellediği bir 403 alıyordu
  // (backend zaten `Depends(require("connection:write"))` ile ZORLUYOR — bu GÜVENLİK
  // açığı değildi, yalnız kafa karıştırıcı bir UX'ti). Diğer izin-duyarlı bileşenlerle
  // (ReportPanel/SettingsDrawer) AYNI paylaşılan `usePermission` hook'u kullanılır.
  const canWrite = usePermission("connection:write");
  const [step, setStep] = useState<Step>("form");
  const [form, setForm] = useState({
    host: "", port: "5432", database: "", user: "", password: "",
  });
  const [activeConnId, setActiveConnId] = useState<string | null>(null);
  const [draft, setDraft] = useState<ConnectionDraft | null>(null);
  const [testMsg, setTestMsg] = useState<string | null>(null);

  const connectionsQ = useQuery({
    queryKey: ["tenant-connections"],
    queryFn: listTenantConnections,
  });

  const body = () => ({
    datasource: "postgres",
    host: form.host,
    port: Number(form.port) || 5432,
    database: form.database,
    user: form.user,
    password: form.password,
  });

  const testMut = useMutation({
    mutationFn: () => testTenantConnection(body()),
    onSuccess: (r) => setTestMsg(r.ok ? "✓ Bağlantı başarılı." : `✗ ${r.detail ?? "Bağlantı kurulamadı."}`),
    onError: () => setTestMsg("✗ Bağlantı kurulamadı."),
  });

  const createMut = useMutation({
    mutationFn: () => createTenantConnection(body()),
    onSuccess: async (conn) => {
      setActiveConnId(conn.id);
      qc.invalidateQueries({ queryKey: ["tenant-connections"] });
      const d = await getConnectionDraft(conn.id);
      setDraft(d);
      setStep("review");
    },
  });

  const draftForMut = useMutation({
    mutationFn: (id: string) => getConnectionDraft(id),
    onSuccess: (d, id) => {
      setActiveConnId(id);
      setDraft(d);
      setStep("review");
    },
  });

  const confirmMut = useMutation({
    mutationFn: () => {
      if (!activeConnId || !draft) throw new Error("taslak yok");
      return confirmConnectionDraft(activeConnId, draft);
    },
    onSuccess: () => setStep("done"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => deleteTenantConnection(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tenant-connections"] }),
  });

  const toggleInclude = (name: string) => {
    if (!draft) return;
    setDraft({
      ...draft,
      cubes: draft.cubes.map((c) => (c.name === name ? { ...c, include: !c.include } : c)),
    });
  };

  const includedNames = new Set((draft?.cubes ?? []).filter((c) => c.include).map((c) => c.name));

  if (!canWrite) {
    return (
      <p className="text-sm text-muted">
        Veri kaynağı bağlama sihirbazı yalnız yönetici yetkisiyle kullanılabilir. Erişim
        gerekiyorsa yöneticinizle iletişime geçin.
      </p>
    );
  }

  return (
    <div className="text-sm">
      <p className="mb-4 text-xs text-muted">
        Gerçek bir veritabanına bağlanıp tablolarını kalıcı olarak analiz edilebilir hale
        getir. Excel/CSV yüklemesinden farkı: burada ilişkiler tahmin edilmez, gerçek
        şemadan (yabancı anahtarlardan) okunur.
      </p>

      {step === "form" && (
        <div>
          <FormField label="Sunucu (host)" value={form.host}
                    onChange={(e) => setForm({ ...form, host: e.target.value })} />
          <FormField label="Port" value={form.port} inputMode="numeric"
                    onChange={(e) => setForm({ ...form, port: e.target.value })} />
          <FormField label="Veritabanı adı" value={form.database}
                    onChange={(e) => setForm({ ...form, database: e.target.value })} />
          <FormField label="Kullanıcı" value={form.user}
                    onChange={(e) => setForm({ ...form, user: e.target.value })} />
          <FormField label="Parola" type="password" value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })} />

          {testMsg && <p className="mb-3 text-xs text-muted">{testMsg}</p>}

          <div className="flex gap-2">
            <button
              type="button"
              disabled={testMut.isPending || !form.host || !form.database}
              onClick={() => testMut.mutate()}
              className="flex-1 rounded-md border border-hairline py-2 text-sm disabled:opacity-50"
            >
              {testMut.isPending ? "…" : "Bağlantıyı test et"}
            </button>
            <button
              type="button"
              disabled={createMut.isPending || !form.host || !form.database}
              onClick={() => createMut.mutate()}
              className="flex-1 rounded-md bg-accent py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {createMut.isPending ? "…" : "Bağla ve şemayı incele"}
            </button>
          </div>
          {createMut.isError && (
            <p className="mt-2 text-xs" style={{ color: "var(--danger, #b42318)" }}>
              Bağlantı kaydedilemedi (dry-run başarısız olmuş olabilir).
            </p>
          )}

          {connectionsQ.data && connectionsQ.data.length > 0 && (
            <div className="mt-6 border-t border-hairline pt-4">
              <p className={labelCls}>mevcut bağlantılar</p>
              {connectionsQ.data.map((c) => (
                <div key={c.id} className="flex items-center justify-between py-1 text-xs">
                  <span className="text-muted">
                    {c.datasource} · {c.host}:{c.port}/{c.database}
                  </span>
                  <div className="flex gap-2">
                    <button
                      className="text-accent hover:underline"
                      onClick={() => draftForMut.mutate(c.id)}
                    >
                      incele
                    </button>
                    <button
                      className="text-muted hover:text-foreground"
                      onClick={() => deleteMut.mutate(c.id)}
                    >
                      sil
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {step === "review" && draft && (
        <div>
          <p className="mb-3 text-xs text-muted">
            {draft.cubes.length} tablo bulundu. Analiz edilecekleri seç, gerekirse hariç
            bırak — onayladığında yalnız işaretli olanlar kalıcı hale gelir.
          </p>
          <div className="max-h-[50vh] space-y-2 overflow-auto">
            {draft.cubes.map((c) => (
              <DraftCubeRow key={c.name} cube={c} onToggle={() => toggleInclude(c.name)} />
            ))}
          </div>
          {draft.relationships.length > 0 && (
            <div className="mt-4 border-t border-hairline pt-3">
              <p className={labelCls}>tespit edilen ilişkiler</p>
              {draft.relationships.map((r) => (
                <p key={r.name} className="text-xs text-muted">
                  {r.models[0]} → {r.models[1]}{" "}
                  <span className="opacity-60">({r.condition})</span>
                  {!(includedNames.has(r.models[0]) && includedNames.has(r.models[1])) && (
                    <span className="ml-1 text-[10px] opacity-50">(hariç tutulan tablo içeriyor)</span>
                  )}
                </p>
              ))}
            </div>
          )}
          <div className="mt-4 flex gap-2">
            <button
              type="button"
              onClick={() => setStep("form")}
              className="flex-1 rounded-md border border-hairline py-2 text-sm"
            >
              geri
            </button>
            <button
              type="button"
              disabled={confirmMut.isPending || includedNames.size === 0}
              onClick={() => confirmMut.mutate()}
              className="flex-1 rounded-md bg-accent py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {confirmMut.isPending ? "…" : `Onayla (${includedNames.size} tablo)`}
            </button>
          </div>
        </div>
      )}

      {step === "done" && confirmMut.data && (
        <div className="text-center">
          <p className="mb-2 text-2xl">✓</p>
          <p className="mb-1">
            {confirmMut.data.written_cubes.length} yeni tablo eklendi
            {confirmMut.data.written_relationships > 0 &&
              ` (${confirmMut.data.written_relationships} ilişki dahil)`}
            .
          </p>
          <p className="text-xs text-muted">
            {confirmMut.data.written_cubes.join(", ") || "(hepsi zaten mevcuttu)"}
          </p>
          <button
            type="button"
            onClick={() => {
              setStep("form");
              setDraft(null);
              setActiveConnId(null);
              setForm({ host: "", port: "5432", database: "", user: "", password: "" });
            }}
            className="mt-4 rounded-md border border-hairline px-4 py-2 text-sm"
          >
            yeni bağlantı
          </button>
        </div>
      )}
    </div>
  );
}

function DraftCubeRow({ cube, onToggle }: { cube: DraftCube; onToggle: () => void }) {
  return (
    <label className="flex cursor-pointer items-start gap-2 rounded-md border border-hairline p-2">
      <input type="checkbox" checked={cube.include} onChange={onToggle} className="mt-1" />
      <div className="min-w-0 flex-1">
        <p className="font-mono text-xs">{cube.name}</p>
        <p className="truncate text-[11px] text-muted">
          {cube.measures.length > 0 && `ölçü: ${cube.measures.join(", ")}`}
          {cube.dimensions.length > 0 && ` · boyut: ${cube.dimensions.join(", ")}`}
          {cube.time_dimensions.length > 0 && ` · zaman: ${cube.time_dimensions.join(", ")}`}
        </p>
      </div>
    </label>
  );
}
