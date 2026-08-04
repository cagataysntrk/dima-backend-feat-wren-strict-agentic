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
  apiErrorMessage,
  confirmConnectionDraft,
  createTenantConnection,
  deleteTenantConnection,
  getConnectionDraft,
  exportSemantic,
  importSemantic,
  listTenantConnections,
  testTenantConnection,
} from "@/lib/api-client";
import { useFeature } from "@/lib/useFeature";
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

/** FAZ 3.4 — Ossie semantik model ithali (önizleme). Yeni PANEL değil: bağlantı
 *  sihirbazının `review` adımının bir bölümü (K5 tavanı 13/13). */
function OssieIthal({ id }: { id: string }) {
  const [metin, setMetin] = useState("");
  const ithal = useMutation({
    mutationFn: () => importSemantic(id, JSON.parse(metin || "{}")),
  });
  return (
    <details className="mb-3 border border-hairline px-2.5 py-2">
      <summary className="cursor-pointer font-mono text-[11px] text-neutral-500">
        ⇪ mevcut semantik modelini içe aktar (Apache Ossie)
      </summary>
      <p className="mt-2 font-mono text-[10px] leading-snug text-neutral-400">
        Ossie YAML/JSON belgeni yapıştır. Bu adım <span className="text-foreground">yalnız
        önizleme</span> üretir — kalıcı hale gelmesi için aşağıdaki onay adımından geçer.
      </p>
      <textarea
        value={metin}
        onChange={(e) => setMetin(e.target.value)}
        rows={4}
        placeholder='{"version": "0.1.1", "datasets": [...]}'
        className="mt-2 w-full border border-hairline bg-transparent p-2 font-mono text-[11px]"
      />
      <button
        type="button"
        disabled={!metin.trim() || ithal.isPending}
        onClick={() => ithal.mutate()}
        className="mt-1 border border-hairline px-2 py-[3px] font-mono text-[11px] text-neutral-500 transition-colors hover:border-accent hover:text-accent disabled:opacity-50"
      >
        {ithal.isPending ? "…" : "önizle"}
      </button>
      {ithal.isError && (
        <p className="mt-2 font-mono text-[11px] text-red-500">
          {apiErrorMessage(ithal.error)}
        </p>
      )}
      {ithal.data && (
        <div className="mt-2 space-y-1 font-mono text-[11px]">
          <p className="text-foreground">
            {ithal.data.cubes.length} cube · {ithal.data.relationships.length} ilişki
          </p>
          {ithal.data.uyarilar.map((u) => (
            <p key={u} className="text-amber-600">⚠ {u}</p>
          ))}
          {ithal.data.relationships.some((r) => r.certified === "olculmedi") && (
            <p className="text-amber-600">
              ⚠ İthal ilişkiler <span className="text-foreground">ÖLÇÜLMEDİ</span> damgasıyla
              gelir — sessiz &quot;sağlıklı&quot; değildir. Fan-out sertifikası onay adımında ölçülür.
            </p>
          )}
        </div>
      )}
    </details>
  );
}

/** FAZ 4.4 — Ossie **ihracı**. Aynı `details` bölümünün ikinci yarısı; yeni PANEL değil
 *  (K5 tavanı 13/13 — bir yetenek bir panel doğurmaz).
 *
 *  🔴 Farkımız `x-dima` içinde gider ve kullanıcıya **söylenir**: sessiz-yanlışı önleyen
 *  dört alan (fan-out sertifikası · `always_filter` · `additive:` · `dimension_origin`)
 *  Ossie'nin kendi şemasında yoktur. Kullanıcı belgeyi başka bir araca taşırken bunu
 *  bilmelidir — *aksi hâlde "standart bir dosya" sanıp farkı sessizce kaybeder.*
 *
 *  ⚠ 404 bir **hata değil, bir yokluktur**: bayrak kapalıysa özellik bu kurulumda yok. */
function OssieIhrac({ id }: { id: string }) {
  const ihrac = useMutation({ mutationFn: () => exportSemantic(id) });
  const kapali = (ihrac.error as { response?: { status?: number } } | null)
    ?.response?.status === 404;
  return (
    <div className="mt-3 border-t border-hairline pt-2">
      <button
        type="button"
        disabled={ihrac.isPending}
        onClick={() => ihrac.mutate()}
        className="border border-hairline px-2 py-[3px] font-mono text-[11px] text-neutral-500 transition-colors hover:border-accent hover:text-accent disabled:opacity-50"
      >
        {ihrac.isPending ? "…" : "⇫ semantik modeli dışa aktar (Ossie)"}
      </button>
      {kapali && (
        <p className="mt-2 font-mono text-[11px] text-neutral-500">
          Bu kurulumda kapalı.
        </p>
      )}
      {ihrac.isError && !kapali && (
        <p className="mt-2 font-mono text-[11px] text-red-500">
          {apiErrorMessage(ihrac.error)}
        </p>
      )}
      {ihrac.data && (
        <div className="mt-2 space-y-1 font-mono text-[11px]">
          <p className="text-amber-600">
            ⚠ Farkımız <span className="text-foreground">x-dima</span> uzantısında:
            fan-out sertifikası · always_filter · additive · dimension_origin. Ossie
            şemasında karşılıkları <span className="text-foreground">yok</span> — başka
            bir araca taşırken bu alanlar okunmayabilir.
          </p>
          <button
            type="button"
            onClick={() => {
              const bag = new Blob([JSON.stringify(ihrac.data, null, 2)],
                                   { type: "application/json" });
              const url = URL.createObjectURL(bag);
              const a = document.createElement("a");
              a.href = url;
              a.download = `ossie-${id}.json`;
              a.click();
              URL.revokeObjectURL(url);
            }}
            className="border border-hairline px-2 py-[3px] text-neutral-500 transition-colors hover:border-accent hover:text-accent"
          >
            ↓ indir
          </button>
          <pre className="max-h-40 overflow-auto border border-hairline p-2 text-[10px] text-neutral-400">
            {JSON.stringify(ihrac.data, null, 2).slice(0, 1200)}
          </pre>
        </div>
      )}
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
  const ossieAcik = useFeature("ossie_ithal") !== "off";
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
          {/* FAZ 3.4 — MEVCUT SEMANTİK MODELİ İÇE AKTAR (Apache Ossie).
              🔴 Bu adım YAZMAZ, ÖNİZLEME üretir: yarım ithal edilmiş bir model, ithal
              edilmemiş bir modelden kötüdür — katalogda görünür ama sayılarını kimse
              denetlememiştir. Yazma yine `confirm` adımının işi.
              ⚠ İthal ilişkiler `olculmedi` damgasıyla gelir ve bu EKRANDA söylenir:
              bir başkasının modelinin doğru olduğunu VARSAYMAK, sessiz-yanlışın ithal
              edilmiş hâli olurdu. */}
          {ossieAcik && activeConnId && (
            <>
              <OssieIthal id={activeConnId} />
              <OssieIhrac id={activeConnId} />
            </>
          )}
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
