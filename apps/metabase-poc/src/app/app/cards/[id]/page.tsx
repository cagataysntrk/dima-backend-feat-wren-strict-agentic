import { canAnalyze, shellContext } from "@/server/session";
import { CardView } from "./CardView";

export default async function CardPage({ params }: { params: Promise<{ id: string }> }) {
  const [{ id }, ctx] = await Promise.all([params, shellContext()]);
  return <CardView id={Number(id)} canEdit={canAnalyze(ctx.role)} />;
}
