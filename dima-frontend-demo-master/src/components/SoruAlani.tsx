"use client";

/** **SORU ALANI** — sohbetin tek giriş yüzeyi ve dört ayarının **tek sahibi**.
 *
 * ## 🔴 Kapatılan asimetri
 *
 * Bir envanter denetimi ölçtü: `kapsam` · `yol sınırı` · `hızlı/derin` · `📎 yükleme`
 * **yalnız sol komposerde** vardı. Sağdaki *"devam et"* komposerinde hiçbiri yoktu —
 * yani kullanıcı **ilk soruda** bu ayarları verebiliyor, **takip sorusunda
 * veremiyordu**.
 *
 * > ⚠ *Bir ayarın yalnız bazı sorulara uygulanabilmesi, kullanıcıya o ayarın ne
 * > zaman geçerli olduğunu **tahmin ettirir**.* Ve tahmin ettiren bir ayar,
 * > güvenilmeyen bir ayardır.
 *
 * ## Neden ortak bileşen, iki kopya değil
 *
 * Aynı dört kontrolü iki komposere ayrı ayrı yazmak, bu deponun defterindeki
 * **"aynı kuralın iki sahibi"** sınıfını doğururdu: biri güncellenir, öteki kalır ve
 * kullanıcı aynı anahtarın iki yerde **farklı davrandığını** görür.
 *
 * *Bir asimetri, ikinci bir kopya eklenerek değil, tek sahip kurularak kapatılır.*
 */

import { useRef } from "react";

import { CaretInput } from "@/components/CaretInput";

/** ⚠ `Kapsam` **null İÇERMEZ**: kapsam düğmeleri her zaman bir değer gönderir
 *  (`genel` varsayılandır, *"seçilmemiş"* diye bir hâl yoktur). Değerin kendisi
 *  `null` olabilir (henüz okunmamış), ama **ayarlayıcı** asla `null` almaz.
 *  *Bir tipin gereğinden geniş olması, çağıranı olmayan bir hâli ele almaya zorlar.* */
export type Kapsam = "departman" | "genel" | "portfoy";
export type YolSiniri = "deterministik" | "llm" | null;
export type Mod = "hizli" | "derin" | null;

export function SoruAlani({
  deger,
  onDeger,
  onGonder,
  pending,
  ipucu,
  kapsam = null,
  onKapsam,
  superadmin,
  yolSiniri = null,
  onYolSiniri,
  mod = null,
  onMod,
  onUpload,
  uploading,
}: {
  deger: string;
  onDeger: (v: string) => void;
  onGonder: () => void;
  pending?: boolean;
  /** Komposerin üstünde gösterilecek bağlam ipucu (ör. *"her zaman yeni thread"*). */
  ipucu?: React.ReactNode;
  kapsam?: Kapsam | null;
  /** `undefined` → anahtar **hiç çizilmez** (bayrak kapalı). */
  onKapsam?: (k: Kapsam) => void;
  /** ⚠ Bilinen borç: `page.tsx` bu prop'u hiç göndermiyor → *"portföy"* seçeneği
   *  bugün **hiç görünmüyor**. Envanter bunu taşımadan ÖNCE kırık diye ölçtü;
   *  burada iletim yolu **korunuyor** ki düzeltme tek satır olsun. */
  superadmin?: boolean;
  yolSiniri?: YolSiniri;
  onYolSiniri?: (y: YolSiniri) => void;
  mod?: Mod;
  onMod?: (m: Mod) => void;
  onUpload?: (f: File) => void;
  uploading?: boolean;
}) {
  const fileRef = useRef<HTMLInputElement>(null);

  const cip = (secili: boolean) =>
    `rounded-[var(--radius-chip)] border px-1.5 py-0.5 font-mono text-[var(--text-etiket)] transition-colors ${
      secili
        ? "border-accent/50 text-accent"
        : "border-[var(--surface-kenar)] text-neutral-500 hover:text-foreground"
    }`;

  return (
    <div className="shrink-0 border-t border-[var(--surface-kenar)] px-4 py-3">
      {ipucu}

      {/* KAPSAM — 🔴 bir GÖRÜNÜRLÜK aracıdır, güvenlik sınırı DEĞİL: `genel`e dönmek
          hiçbir yetki AÇMAZ; sınırı backend (`authorize()` + RLS) koyar. `portfoy`
          yalnız superadmin'e görünür — görünürlük bir sınır değil, kullanıcıya
          yapamayacağı bir şeyi teklif etmeme nezaketidir. */}
      {onKapsam && (
        <div className="mb-2 flex items-center gap-1.5">
          <span className="select-none font-mono text-[var(--text-etiket)] uppercase tracking-wider text-neutral-400">
            kapsam
          </span>
          {([
            ["genel", "genel", "Bugünkü tam katalog (varsayılan)"],
            ["departman", "departmanım", "Yalnız departmanıma atanmış metrikler — atanmamışlar da görünür"],
            ...(superadmin
              ? [["portfoy", "portföy", "Çok-tenant birleşik görünüm (yalnız superadmin)"] as const]
              : []),
          ] as const).map(([d, etiket, ipucuMetni]) => (
            <button
              key={etiket}
              type="button"
              onClick={() => onKapsam(d)}
              title={ipucuMetni}
              className={cip((kapsam ?? "genel") === d)}
            >
              {etiket}
            </button>
          ))}
        </div>
      )}

      {/* YOL SINIRI — üç konumlu **uzman** ayarı; oturum boyu kalıcı. */}
      {onYolSiniri && (
        <div className="mb-2 flex items-center gap-1.5">
          <span className="select-none font-mono text-[var(--text-etiket)] uppercase tracking-wider text-neutral-400">
            yol
          </span>
          {([
            [null, "hepsi", "Küp → LLM seçimi → keşif (varsayılan)"],
            ["llm", "küp + llm", "Ham SQL YOK — yalnız katalogdan seçim"],
            ["deterministik", "yalnız küp", "LLM'e HİÇ gidilmez — yalnız kanıtlanmış yol"],
          ] as const).map(([d, etiket, ipucuMetni]) => (
            <button
              key={etiket}
              type="button"
              onClick={() => onYolSiniri(d)}
              title={ipucuMetni}
              className={cip(yolSiniri === d)}
            >
              {etiket}
            </button>
          ))}
        </div>
      )}

      {/* HIZLI ↔ DERİN — ⚠ `yol_siniri` üç konumlu bir UZMAN ayarıdır; bu ise günlük
          kullanım için **tek soruluk** bir karardır ve her mesajda sıfırlanır.
          İkisi aynı sunucu kapısından geçer — aynı davranışa iki AD, iki uygulama değil. */}
      {onMod && (
        <div className="mb-1.5 inline-flex overflow-hidden rounded-[var(--radius-chip)] border border-[var(--surface-kenar)]">
          {([
            ["hizli", "hızlı", "Yalnız kanıtlanmış küp yolu — LLM'e HİÇ gidilmez"],
            ["derin", "derin", "Tam merdiven: küp → LLM seçimi → keşif"],
          ] as const).map(([d, etiket, ipucuMetni], i) => (
            <button
              key={d}
              type="button"
              title={ipucuMetni}
              onClick={() => onMod(mod === d ? null : d)}
              className={`${i ? "border-l border-[var(--surface-kenar)] " : ""}px-2 py-0.5 font-mono text-[var(--text-etiket)] transition-colors ${
                mod === d ? "bg-accent/10 text-accent" : "text-neutral-500 hover:text-foreground"
              }`}
            >
              {etiket}
            </button>
          ))}
        </div>
      )}

      <div className="flex items-center gap-2">
        {onUpload && (
          <>
            <input
              ref={fileRef}
              type="file"
              accept=".csv,.xlsx,.xls,.txt,.tsv"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) onUpload(f);
                e.target.value = "";
              }}
            />
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              disabled={uploading}
              title="Excel/CSV yükle — bu sohbete özel veri kaynağı (geçici)"
              aria-label="Excel veya CSV yükle"
              className="select-none font-mono text-sm text-neutral-500 transition-colors hover:text-accent disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
            >
              {uploading ? "⋯" : "📎"}
            </button>
          </>
        )}
        <span className="select-none font-mono text-sm text-accent" aria-hidden>›</span>
        <div className="flex-1">
          <CaretInput
            value={deger}
            onChange={onDeger}
            onSubmit={onGonder}
            busy={pending}
            size="inline"
          />
        </div>
      </div>
    </div>
  );
}
