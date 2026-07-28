"use client";

import { useState } from "react";
import {
  AlertTriangle,
  Check,
  ChevronLeft,
  ChevronRight,
  Database,
  Loader2,
  Plug,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

/**
 * Entegrasyon sihirbazı — 4 adım: kaynak → bağlan+test → kapsam → doğrula.
 *
 * GÜVENLİK: kimlik bilgileri istemcide TUTULMAZ. Form alanları yalnız bileşen
 * state'inde yaşar, "kaydet" onları doğrudan backend'e postalar; backend şifreler
 * ve saklar. UI yalnız "bağlı / bağlı değil" durumunu görür — access token
 * kuralıyla aynı mantık (bkz. CLAUDE.md).
 *
 * DURUM: backend sözleşmesinde HENÜZ entegrasyon ucu yok (/ask /cube /verify
 * /query /schedules /notifications /contracts). Bu yüzden "bağlantıyı test et"
 * ve "kaydet" gerçek bir çağrı YAPMAZ; uç eklenene kadar devre dışı ve bunu
 * kullanıcıya açıkça söylüyoruz. Sahte bir "bağlandı" göstermek, kurulmamış bir
 * entegrasyonu kurulmuş sanmaya yol açardı.
 */

const SOURCES = [
  { id: "postgres", label: "PostgreSQL", port: "5432" },
  { id: "mysql", label: "MySQL", port: "3306" },
  { id: "mssql", label: "SQL Server", port: "1433" },
  { id: "bigquery", label: "BigQuery", port: "" },
  { id: "snowflake", label: "Snowflake", port: "" },
] as const;

type SourceId = (typeof SOURCES)[number]["id"];

const STEPS = ["Kaynak", "Bağlantı", "Kapsam", "Doğrula"] as const;

export function IntegrationWizard({ onCancel }: { onCancel: () => void }) {
  const [step, setStep] = useState(0);
  const [source, setSource] = useState<SourceId | null>(null);
  const [form, setForm] = useState({ host: "", port: "", database: "", user: "", password: "" });
  const [schemas, setSchemas] = useState("");

  const chosen = SOURCES.find((s) => s.id === source);
  // Adım 2'den ileri gitmek bağlantı testine bağlı olmalı; test ucu olmadığı
  // için ilerlemeyi burada kapatıyoruz (sahte "başarılı" göstermek yerine).
  const canAdvance = step === 0 ? source !== null : false;

  const pick = (id: SourceId) => {
    setSource(id);
    const port = SOURCES.find((s) => s.id === id)?.port ?? "";
    setForm((f) => ({ ...f, port }));
    setStep(1);
  };

  return (
    <div className="space-y-6">
      {/* adım göstergesi */}
      <ol className="flex items-center gap-2">
        {STEPS.map((label, i) => {
          const done = i < step;
          const active = i === step;
          return (
            <li key={label} className="flex items-center gap-2">
              <span
                className={cn(
                  "flex size-6 items-center justify-center rounded-full border text-[11px] tabular-nums",
                  done && "border-brand bg-brand text-brand-foreground",
                  active && !done && "border-brand text-brand",
                  !done && !active && "border-border text-muted-foreground",
                )}
              >
                {done ? <Check className="size-3" /> : i + 1}
              </span>
              <span
                className={cn(
                  "text-xs",
                  active ? "font-medium text-foreground" : "text-muted-foreground",
                )}
              >
                {label}
              </span>
              {i < STEPS.length - 1 && (
                <ChevronRight className="size-3 text-muted-foreground/50" />
              )}
            </li>
          );
        })}
      </ol>

      <div className="flex items-start gap-2 rounded-lg border border-amber-500/30 bg-amber-500/5 px-3 py-2">
        <AlertTriangle className="mt-0.5 size-4 shrink-0 text-amber-600 dark:text-amber-400" />
        <p className="text-xs leading-relaxed text-muted-foreground">
          Backend&apos;de entegrasyon ucu henüz yok. Formu doldurabilirsin ama{" "}
          <strong className="font-medium text-foreground">
            bağlantı testi ve kaydetme çalışmıyor
          </strong>{" "}
          — uç eklendiğinde bu uyarı kalkacak ve adımlar açılacak.
        </p>
      </div>

      {step === 0 && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {SOURCES.map((s) => (
            <Card
              key={s.id}
              onClick={() => pick(s.id)}
              className={cn(
                "cursor-pointer gap-2 p-4 transition-colors hover:border-brand/40",
                source === s.id && "border-brand/60",
              )}
            >
              <Database className="size-5 text-muted-foreground" />
              <span className="text-sm font-medium">{s.label}</span>
            </Card>
          ))}
        </div>
      )}

      {step === 1 && chosen && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Badge variant="brand-subtle">{chosen.label}</Badge>
            <button
              type="button"
              onClick={() => setStep(0)}
              className="text-xs text-muted-foreground underline-offset-2 hover:underline"
            >
              değiştir
            </button>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Field id="host" label="Sunucu" value={form.host} onChange={(v) => setForm((f) => ({ ...f, host: v }))} placeholder="db.sirket.com" />
            <Field id="port" label="Port" value={form.port} onChange={(v) => setForm((f) => ({ ...f, port: v }))} placeholder={chosen.port || "—"} />
            <Field id="database" label="Veritabanı" value={form.database} onChange={(v) => setForm((f) => ({ ...f, database: v }))} placeholder="uretim" />
            <Field id="user" label="Kullanıcı" value={form.user} onChange={(v) => setForm((f) => ({ ...f, user: v }))} placeholder="dima_readonly" />
            <div className="sm:col-span-2">
              <Field id="password" label="Parola" type="password" value={form.password} onChange={(v) => setForm((f) => ({ ...f, password: v }))} placeholder="••••••••" />
            </div>
          </div>

          <p className="text-xs leading-relaxed text-muted-foreground">
            Yalnız <strong className="font-medium text-foreground">okuma yetkisi</strong> olan
            bir kullanıcı ver. Parola tarayıcıda saklanmaz; kaydettiğinde doğrudan
            sunucuya gider ve orada şifrelenir.
          </p>

          <Button variant="outline" disabled className="gap-2">
            <Loader2 className="size-4" />
            Bağlantıyı test et
          </Button>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-3">
          <Label htmlFor="schemas">Okunacak şemalar</Label>
          <Input
            id="schemas"
            value={schemas}
            onChange={(e) => setSchemas(e.target.value)}
            placeholder="public, uretim"
          />
          <p className="text-xs text-muted-foreground">
            Virgülle ayır. Boş bırakırsan erişilebilen tüm şemalar taranır.
          </p>
        </div>
      )}

      <div className="flex items-center justify-between border-t border-border pt-4">
        <Button variant="ghost" onClick={onCancel}>
          Vazgeç
        </Button>
        <div className="flex items-center gap-2">
          {step > 0 && (
            <Button variant="outline" onClick={() => setStep((s) => s - 1)} className="gap-1.5">
              <ChevronLeft className="size-4" />
              Geri
            </Button>
          )}
          <Button
            variant="brand"
            disabled={!canAdvance}
            onClick={() => setStep((s) => s + 1)}
            className="gap-1.5"
          >
            {step === STEPS.length - 1 ? "Kaydet" : "İleri"}
            {step < STEPS.length - 1 && <ChevronRight className="size-4" />}
          </Button>
        </div>
      </div>
    </div>
  );
}

function Field({
  id,
  label,
  value,
  onChange,
  placeholder,
  type = "text",
}: {
  id: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
}) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        type={type}
        value={value}
        placeholder={placeholder}
        autoComplete="off"
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

/** Boş durum — henüz entegrasyon yokken gösterilen kart. */
export function NoIntegrations({ onAdd }: { onAdd: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-border py-12 text-center">
      <Plug className="size-6 text-muted-foreground" />
      <div>
        <p className="text-sm font-medium">Bağlı veri kaynağı yok</p>
        <p className="mt-1 max-w-sm text-xs text-muted-foreground">
          dima şu an ortam değişkeniyle tanımlı kaynağa bağlanıyor. Buradan
          yönetilen entegrasyonlar backend ucu eklendiğinde açılacak.
        </p>
      </div>
      <Button variant="outline" onClick={onAdd} className="gap-1.5">
        <Plug className="size-4" />
        Kaynak ekle
      </Button>
    </div>
  );
}
