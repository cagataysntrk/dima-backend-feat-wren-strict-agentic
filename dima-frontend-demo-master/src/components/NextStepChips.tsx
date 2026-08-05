"use client";

import type { CubeQuery, NextStep } from "@/lib/types";

// ⚠️ TEK SAHİP (KAT-1). Bu blok `ReportCard` ile `ReportPanel`'in saf-not dalında
// **İKİ KEZ** yazılıydı: 22 satırın 19'u birebir aynıydı (başlık · title · className'ler ·
// ikon üçlemesi). Denetim ölçtü ve *"tek sahip"* diye kutlanan turun kendisinin ikinci bir
// sahip doğurduğunu gösterdi. İkonların (`⌗ ◷ ∑`) iki dosyada olması ayrıca şu riski
// taşıyordu: backend `NextStep.kind` alanını **kısıtlamıyor**; dördüncü bir tür sessizce
// `∑` olurdu — **iki yerde birden**, ve ayrışmayı ölçen hiçbir kapı yoktu.
// ⚠️ **VE O RİSK GERÇEKLEŞTİ (FAZ 5.4).** Yukarıdaki yorum *"dördüncü bir tür sessizce
// `∑` olurdu"* diye uyarıyordu; `order` (Top-N) türü tam olarak öyle doğdu. Tek sahip
// olduğu için düzeltmesi **tek satır** — ikinci sahip yaşasaydı iki yerde birden
// unutulabilirdi. *Bir uyarının değeri, gerçekleştiğinde ne kadar ucuza kapandığıdır.*
const IKON: Record<string, string> = { dimension: "⌗", time: "◷", measure: "∑",
                                       order: "↓" };

export function NextStepChips({
  steps,
  onCubeEdit,
  baslik = "sonraki adım",
}: {
  steps: NextStep[] | undefined;
  onCubeEdit: (edit: { cq: CubeQuery; label: string }) => void;
  // Başlık ÇAĞIRANA aittir: netleştirme cevabında ("Hangi ölçüyü istiyorsun?") bu liste
  // bir SORUNUN ŞIKLARIDIR, "sonraki adım" değil. `ReportCard`'ın kendi yorumu aynı
  // başlığı yanlış bağlamda kullanmayı zaten yasaklıyor — o yasak burada da geçerli.
  baslik?: string;
}) {
  if (!steps?.length) return null;
  return (
    <div className="mt-3">
      <div className="mb-1.5 font-mono text-[var(--text-etiket)] uppercase tracking-wider text-neutral-400">
        {baslik}
      </div>
      <div className="flex flex-wrap gap-1.5">
        {steps.map((step, i) => (
          <button
            key={`${step.kind}-${i}`}
            onClick={() => onCubeEdit({ cq: step.cube_query, label: step.label })}
            title="Deterministik koşar — LLM yok"
            className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-500 transition-colors hover:border-foreground/30 hover:text-foreground"
          >
            <span className="mr-1 text-neutral-400">{IKON[step.kind] ?? "∑"}</span>
            {step.label}
          </button>
        ))}
      </div>
    </div>
  );
}
