import { Badge } from "../primitives/badge";

/**
 * SQL provenance badge (deterministic-first trust language):
 * ◆ CUBE / ◆ CUBE·LLM (brand) · ▚ LLM·<provider> (secondary) · ⚙ KURAL (outline).
 */
export function SourceBadge({ source }: { source: string | null }) {
  if (!source) return null;

  let label: string;
  let variant: "brand" | "brand-subtle" | "secondary" | "outline";
  if (source === "cube") {
    label = "◆ CUBE";
    variant = "brand";
  } else if (source === "kpi") {
    // çapraz-cube KPI kartı (CCC, likidite oranları) — cube kadar deterministik
    label = "◆ KPI";
    variant = "brand";
  } else if (source === "cube+llm") {
    label = "◆ CUBE·LLM";
    variant = "brand-subtle";
  } else if (source.startsWith("llm:")) {
    label = `▚ LLM·${source.slice(4)}`;
    variant = "secondary";
  } else {
    label = "⚙ KURAL";
    variant = "outline";
  }

  return (
    <Badge
      variant={variant}
      title="SQL bu yolla üretildi (deterministik-önce)"
      className="rounded-md text-[10px] font-medium tracking-wide"
    >
      {label}
    </Badge>
  );
}
